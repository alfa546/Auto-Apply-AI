"""
API Key Manager - Handles rotation, failover, and usage tracking for API keys
"""
import time
import random
import logging
from typing import Optional, List, Dict, Any
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import func
from src.app.models import APIUsage
from src.app.services.vault.encryption import vault_encryption

logger = logging.getLogger(__name__)


class APIKeyInfo:
    """Information about a single API key"""
    
    def __init__(
        self,
        key_id: str,
        service: str,
        encrypted_key: str,
        is_active: bool = True,
        daily_limit: Optional[int] = None,
        monthly_limit: Optional[int] = None,
        cooldown_minutes: int = 60,
        metadata: Optional[Dict[str, Any]] = None
    ):
        self.key_id = key_id
        self.service = service
        self.encrypted_key = encrypted_key
        self.is_active = is_active
        self.daily_limit = daily_limit
        self.monthly_limit = monthly_limit
        self.cooldown_minutes = cooldown_minutes
        self.metadata = metadata or {}
        
        # Runtime tracking
        self.daily_usage = 0
        self.monthly_usage = 0
        self.last_used = None
        self.error_count = 0
        self.cooldown_until = None
    
    def get_decrypted_key(self) -> str:
        """Get the actual API key (decrypted)"""
        return vault_encryption.decrypt(self.encrypted_key)
    
    def is_available(self) -> bool:
        """Check if key is available for use"""
        if not self.is_active:
            return False
        
        # Check cooldown
        if self.cooldown_until and datetime.utcnow() < self.cooldown_until:
            return False
        
        # Check daily limit
        if self.daily_limit and self.daily_usage >= self.daily_limit:
            return False
        
        # Check monthly limit
        if self.monthly_limit and self.monthly_usage >= self.monthly_limit:
            return False
        
        return True
    
    def mark_used(self, tokens: int = 0, success: bool = True):
        """Mark key as used"""
        self.last_used = datetime.utcnow()
        self.daily_usage += 1
        self.monthly_usage += 1
        
        if not success:
            self.error_count += 1
            # If too many errors, put in cooldown
            if self.error_count >= 3:
                self.cooldown_until = datetime.utcnow() + timedelta(minutes=self.cooldown_minutes)
                logger.warning(f"API key {self.key_id} put in cooldown for {self.cooldown_minutes} minutes")
    
    def reset_daily_usage(self):
        """Reset daily usage counter"""
        self.daily_usage = 0
    
    def reset_monthly_usage(self):
        """Reset monthly usage counter"""
        self.monthly_usage = 0
        self.error_count = 0


class KeyManager:
    """
    Manages multiple API keys with rotation and failover logic.
    Supports 5-6 keys per API service with automatic failover.
    """
    
    def __init__(self, db: Session):
        self.db = db
        self._key_registry: Dict[str, List[APIKeyInfo]] = {}  # service -> list of keys
        self._rotation_strategy = "round_robin"  # round_robin, random, least_used
    
    def register_key(
        self,
        service: str,
        api_key: str,
        key_id: Optional[str] = None,
        daily_limit: Optional[int] = None,
        monthly_limit: Optional[int] = None,
        cooldown_minutes: int = 60,
        metadata: Optional[Dict[str, Any]] = None
    ) -> APIKeyInfo:
        """
        Register a new API key for a service.
        
        Args:
            service: Service name (e.g., "openai", "gemini", "adzuna")
            api_key: The actual API key (will be encrypted)
            key_id: Optional unique identifier for this key
            daily_limit: Max calls per day (None = unlimited)
            monthly_limit: Max calls per month (None = unlimited)
            cooldown_minutes: Minutes to wait after errors before retrying
            metadata: Additional metadata
            
        Returns:
            APIKeyInfo object
        """
        # Encrypt the key
        encrypted_key = vault_encryption.encrypt(api_key)
        
        # Generate key ID if not provided
        if not key_id:
            key_id = f"{service}_{int(time.time())}_{random.randint(1000, 9999)}"
        
        key_info = APIKeyInfo(
            key_id=key_id,
            service=service,
            encrypted_key=encrypted_key,
            daily_limit=daily_limit,
            monthly_limit=monthly_limit,
            cooldown_minutes=cooldown_minutes,
            metadata=metadata
        )
        
        # Add to registry
        if service not in self._key_registry:
            self._key_registry[service] = []
        
        self._key_registry[service].append(key_info)
        logger.info(f"Registered API key {key_id} for service {service}")
        
        return key_info
    
    def get_available_key(self, service: str) -> Optional[APIKeyInfo]:
        """
        Get an available API key for the given service.
        Uses rotation strategy to select key.
        
        Args:
            service: Service name
            
        Returns:
            APIKeyInfo if available, None otherwise
        """
        if service not in self._key_registry:
            logger.warning(f"No keys registered for service: {service}")
            return None
        
        available_keys = [k for k in self._key_registry[service] if k.is_available()]
        
        if not available_keys:
            logger.warning(f"No available keys for service: {service}")
            return None
        
        # Select key based on rotation strategy
        if self._rotation_strategy == "round_robin":
            # Select the least recently used key
            selected = min(available_keys, key=lambda k: k.last_used or datetime.min)
        elif self._rotation_strategy == "random":
            selected = random.choice(available_keys)
        elif self._rotation_strategy == "least_used":
            selected = min(available_keys, key=lambda k: k.daily_usage + k.monthly_usage)
        else:
            selected = available_keys[0]
        
        return selected
    
    def mark_key_used(self, key_info: APIKeyInfo, success: bool, tokens: int = 0):
        """
        Mark a key as used and update usage stats.
        
        Args:
            key_info: The key that was used
            success: Whether the API call succeeded
            tokens: Number of tokens used (for LLM APIs)
        """
        key_info.mark_used(tokens=tokens, success=success)
        
        # Log to database for analytics
        usage_record = APIUsage(
            user_id="system",  # System-level usage
            service=key_info.service,
            tokens_used=tokens,
            success=success
        )
        self.db.add(usage_record)
        
        try:
            self.db.commit()
        except Exception as e:
            logger.error(f"Failed to log API usage: {e}")
            self.db.rollback()
    
    def get_key_status(self, service: Optional[str] = None) -> Dict[str, Any]:
        """
        Get status of all keys or keys for a specific service.
        
        Args:
            service: Optional service name to filter by
            
        Returns:
            Status dictionary
        """
        if service:
            keys = self._key_registry.get(service, [])
            return {
                "service": service,
                "total_keys": len(keys),
                "available_keys": sum(1 for k in keys if k.is_available()),
                "keys": [
                    {
                        "key_id": k.key_id,
                        "is_active": k.is_active,
                        "is_available": k.is_available(),
                        "daily_usage": k.daily_usage,
                        "monthly_usage": k.monthly_usage,
                        "daily_limit": k.daily_limit,
                        "monthly_limit": k.monthly_limit,
                        "error_count": k.error_count,
                        "last_used": k.last_used.isoformat() if k.last_used else None,
                        "cooldown_until": k.cooldown_until.isoformat() if k.cooldown_until else None
                    }
                    for k in keys
                ]
            }
        
        # Return status for all services
        all_status = {}
        for svc, keys in self._key_registry.items():
            all_status[svc] = {
                "total_keys": len(keys),
                "available_keys": sum(1 for k in keys if k.is_available()),
                "keys_count": len(keys)
            }
        
        return {
            "total_services": len(all_status),
            "services": all_status
        }
    
    def rotate_key(self, service: str, key_id: str) -> bool:
        """
        Manually rotate a specific key (mark as exhausted, force next key to be used).
        
        Args:
            service: Service name
            key_id: Key ID to rotate
            
        Returns:
            True if rotation successful
        """
        if service not in self._key_registry:
            return False
        
        for key in self._key_registry[service]:
            if key.key_id == key_id:
                key.cooldown_until = datetime.utcnow() + timedelta(hours=24)
                logger.info(f"Manually rotated key {key_id} for service {service}")
                return True
        
        return False
    
    def reset_daily_counters(self):
        """Reset daily usage counters for all keys"""
        for keys in self._key_registry.values():
            for key in keys:
                key.reset_daily_usage()
        
        logger.info("Reset daily usage counters for all API keys")
    
    def reset_monthly_counters(self):
        """Reset monthly usage counters for all keys"""
        for keys in self._key_registry.values():
            for key in keys:
                key.reset_monthly_usage()
        
        logger.info("Reset monthly usage counters for all API keys")
    
    def remove_key(self, service: str, key_id: str) -> bool:
        """
        Remove a key from the registry.
        
        Args:
            service: Service name
            key_id: Key ID to remove
            
        Returns:
            True if removed successfully
        """
        if service not in self._key_registry:
            return False
        
        original_len = len(self._key_registry[service])
        self._key_registry[service] = [k for k in self._key_registry[service] if k.key_id != key_id]
        
        if len(self._key_registry[service]) < original_len:
            logger.info(f"Removed key {key_id} from service {service}")
            return True
        
        return False


# Global key manager instance (initialized per request with DB session)
_key_manager: Optional[KeyManager] = None


def get_key_manager(db: Session) -> KeyManager:
    """Get or create key manager instance for this request"""
    global _key_manager
    if _key_manager is None:
        _key_manager = KeyManager(db)
    return _key_manager