"""
Admin API endpoints for managing API vault
"""
import logging
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any
from datetime import datetime

from src.app.database import get_db
from src.app.auth import get_current_admin_user, User
from src.app.models import UserRole
from src.app.services.vault.key_manager import KeyManager, APIKeyInfo
from src.app.services.vault.health_monitor import key_health_monitor
from src.app.services.vault.encryption import vault_encryption

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/admin/vault", tags=["admin-vault"])


def get_admin_key_manager(db: Session = Depends(get_db)) -> KeyManager:
    """Get key manager instance for admin operations"""
    manager = KeyManager(db)
    
    # TODO: Load keys from database/encrypted storage
    # For now, keys are loaded from environment/config
    # In Phase 3, we'll add a database-backed vault
    
    return manager


@router.get("/keys/{service}")
async def get_vault_keys(
    service: str,
    current_user: User = Depends(get_current_admin_user),
    key_manager: KeyManager = Depends(get_admin_key_manager)
):
    """
    Get all API keys for a specific service (admin only).
    Returns decrypted keys - use with caution.
    """
    if current_user.role not in [UserRole.ADMIN, UserRole.SUPER_ADMIN]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    
    status_info = key_manager.get_key_status(service)
    
    # Decrypt keys for admin view (in production, restrict this further)
    decrypted_keys = []
    for key_data in status_info.get("keys", []):
        # Find the actual key info
        for key in key_manager._key_registry.get(service, []):
            if key.key_id == key_data["key_id"]:
                decrypted_keys.append({
                    **key_data,
                    "decrypted_key": key.get_decrypted_key()  # Only admin can see this
                })
                break
    
    return {
        "service": service,
        "total_keys": status_info["total_keys"],
        "available_keys": status_info["available_keys"],
        "keys": decrypted_keys
    }


@router.post("/keys/{service}")
async def add_vault_key(
    service: str,
    api_key: str,
    key_id: Optional[str] = None,
    daily_limit: Optional[int] = None,
    monthly_limit: Optional[int] = None,
    cooldown_minutes: int = 60,
    current_user: User = Depends(get_current_admin_user),
    key_manager: KeyManager = Depends(get_admin_key_manager)
):
    """
    Add a new API key to the vault (admin only).
    Key will be encrypted before storage.
    """
    if current_user.role not in [UserRole.ADMIN, UserRole.SUPER_ADMIN]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    
    try:
        key_info = key_manager.register_key(
            service=service,
            api_key=api_key,
            key_id=key_id,
            daily_limit=daily_limit,
            monthly_limit=monthly_limit,
            cooldown_minutes=cooldown_minutes
        )
        
        # TODO: Save encrypted key to database
        # db.add(VaultKey(...))
        # db.commit()
        
        logger.info(f"Admin {current_user.email} added key {key_info.key_id} for service {service}")
        
        return {
            "message": "API key added successfully",
            "key_id": key_info.key_id,
            "service": service,
            "daily_limit": daily_limit,
            "monthly_limit": monthly_limit
        }
    
    except Exception as e:
        logger.error(f"Failed to add API key: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to add API key: {str(e)}"
        )


@router.delete("/keys/{service}/{key_id}")
async def remove_vault_key(
    service: str,
    key_id: str,
    current_user: User = Depends(get_current_admin_user),
    key_manager: KeyManager = Depends(get_admin_key_manager)
):
    """
    Remove an API key from the vault (admin only).
    """
    if current_user.role not in [UserRole.ADMIN, UserRole.SUPER_ADMIN]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    
    success = key_manager.remove_key(service, key_id)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Key {key_id} not found for service {service}"
        )
    
    # TODO: Remove from database
    # db.query(VaultKey).filter(...).delete()
    # db.commit()
    
    logger.info(f"Admin {current_user.email} removed key {key_id} from service {service}")
    
    return {
        "message": "API key removed successfully",
        "service": service,
        "key_id": key_id
    }


@router.post("/keys/{service}/{key_id}/rotate")
async def rotate_vault_key(
    service: str,
    key_id: str,
    current_user: User = Depends(get_current_admin_user),
    key_manager: KeyManager = Depends(get_admin_key_manager)
):
    """
    Manually rotate an API key (mark as exhausted, force next key to be used).
    """
    if current_user.role not in [UserRole.ADMIN, UserRole.SUPER_ADMIN]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    
    success = key_manager.rotate_key(service, key_id)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Key {key_id} not found for service {service}"
        )
    
    logger.info(f"Admin {current_user.email} rotated key {key_id} for service {service}")
    
    return {
        "message": "Key rotated successfully",
        "service": service,
        "key_id": key_id,
        "action": "rotated"
    }


@router.get("/health")
async def get_vault_health(
    current_user: User = Depends(get_current_admin_user),
    key_manager: KeyManager = Depends(get_admin_key_manager)
):
    """
    Get overall vault health status (admin only).
    """
    if current_user.role not in [UserRole.ADMIN, UserRole.SUPER_ADMIN]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    
    health_report = key_health_monitor.get_service_health(key_manager)
    
    return health_report


@router.get("/health/{service}")
async def get_service_health(
    service: str,
    current_user: User = Depends(get_current_admin_user),
    key_manager: KeyManager = Depends(get_admin_key_manager)
):
    """
    Get health status for a specific service (admin only).
    """
    if current_user.role not in [UserRole.ADMIN, UserRole.SUPER_ADMIN]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    
    keys = key_manager._key_registry.get(service, [])
    
    service_health = {
        "service": service,
        "total_keys": len(keys),
        "available_keys": sum(1 for k in keys if k.is_available()),
        "keys": []
    }
    
    for key in keys:
        health = key_health_monitor.check_key_health(key)
        service_health["keys"].append(health)
    
    return service_health


@router.post("/reset-daily")
async def reset_daily_counters(
    current_user: User = Depends(get_current_admin_user),
    key_manager: KeyManager = Depends(get_admin_key_manager)
):
    """
    Reset daily usage counters for all keys (admin only).
    """
    if current_user.role not in [UserRole.ADMIN, UserRole.SUPER_ADMIN]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    
    key_manager.reset_daily_counters()
    
    logger.info(f"Admin {current_user.email} reset daily counters")
    
    return {
        "message": "Daily counters reset successfully",
        "reset_by": current_user.email
    }


@router.post("/reset-monthly")
async def reset_monthly_counters(
    current_user: User = Depends(get_current_admin_user),
    key_manager: KeyManager = Depends(get_admin_key_manager)
):
    """
    Reset monthly usage counters for all keys (admin only).
    """
    if current_user.role not in [UserRole.ADMIN, UserRole.SUPER_ADMIN]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    
    key_manager.reset_monthly_counters()
    
    logger.info(f"Admin {current_user.email} reset monthly counters")
    
    return {
        "message": "Monthly counters reset successfully",
        "reset_by": current_user.email
    }


@router.get("/status")
async def get_vault_status(
    current_user: User = Depends(get_current_admin_user),
    key_manager: KeyManager = Depends(get_admin_key_manager)
):
    """
    Get overall vault status summary (admin only).
    """
    if current_user.role not in [UserRole.ADMIN, UserRole.SUPER_ADMIN]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    
    status_info = key_manager.get_key_status()
    
    # Add additional metadata
    status_info["vault_encryption"] = "AES-256 (Fernet)"
    status_info["rotation_strategy"] = key_manager._rotation_strategy
    
    return status_info