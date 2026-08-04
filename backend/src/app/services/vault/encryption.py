"""
Vault Encryption Service - AES-256 encryption for API keys
"""
import os
import base64
import hashlib
from typing import Optional
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from src.app.config import settings

class VaultEncryption:
    """
    Handles encryption/decryption of sensitive API keys using AES-256.
    Uses Fernet (symmetric encryption) with a master key derived from environment variable.
    """
    
    def __init__(self):
        self._master_key = self._get_or_generate_master_key()
        self._fernet = Fernet(self._master_key)
    
    def _get_or_generate_master_key(self) -> bytes:
        """
        Get master key from environment or generate new one.
        In production, VAULT_MASTER_KEY must be set in environment.
        """
        master_key_env = os.getenv("VAULT_MASTER_KEY")
        
        if master_key_env:
            # Use provided key (must be 32 bytes base64-encoded)
            return master_key_env.encode() if isinstance(master_key_env, str) else master_key_env
        
        # Development fallback: derive key from SECRET_KEY
        # In production, always use VAULT_MASTER_KEY env var
        if settings.SECRET_KEY and settings.SECRET_KEY != "supersecretdevelopmentkeychangeinprod":
            salt = b"auto_apply_ai_vault_salt"  # Fixed salt for dev
            kdf = PBKDF2HMAC(
                algorithm=hashes.SHA256(),
                length=32,
                salt=salt,
                iterations=100000,
            )
            key = base64.urlsafe_b64encode(kdf.derive(settings.SECRET_KEY.encode()))
            return key
        
        # Generate new key for development (insecure, for dev only)
        print("⚠️  WARNING: Generating new vault master key. Set VAULT_MASTER_KEY env var in production!")
        key = Fernet.generate_key()
        print(f"Generated key: {key.decode()}")
        print("Save this as VAULT_MASTER_KEY in your .env file")
        return key
    
    def encrypt(self, plaintext: str) -> str:
        """
        Encrypt a string value.
        
        Args:
            plaintext: The value to encrypt
            
        Returns:
            Encrypted string (base64 encoded)
        """
        if not plaintext:
            return ""
        
        try:
            encrypted_bytes = self._fernet.encrypt(plaintext.encode())
            return encrypted_bytes.decode()
        except Exception as e:
            raise ValueError(f"Encryption failed: {e}")
    
    def decrypt(self, ciphertext: str) -> str:
        """
        Decrypt an encrypted string value.
        
        Args:
            ciphertext: The encrypted value (base64 encoded)
            
        Returns:
            Decrypted string
        """
        if not ciphertext:
            return ""
        
        try:
            decrypted_bytes = self._fernet.decrypt(ciphertext.encode())
            return decrypted_bytes.decode()
        except Exception as e:
            raise ValueError(f"Decryption failed: {e}")
    
    def encrypt_dict(self, data: dict) -> dict:
        """
        Encrypt all string values in a dictionary.
        
        Args:
            data: Dictionary with string values to encrypt
            
        Returns:
            Dictionary with encrypted values
        """
        encrypted = {}
        for key, value in data.items():
            if isinstance(value, str) and value:
                encrypted[key] = self.encrypt(value)
            elif isinstance(value, dict):
                encrypted[key] = self.encrypt_dict(value)
            else:
                encrypted[key] = value
        return encrypted
    
    def decrypt_dict(self, data: dict) -> dict:
        """
        Decrypt all encrypted string values in a dictionary.
        
        Args:
            data: Dictionary with encrypted string values
            
        Returns:
            Dictionary with decrypted values
        """
        decrypted = {}
        for key, value in data.items():
            if isinstance(value, str) and value:
                try:
                    decrypted[key] = self.decrypt(value)
                except ValueError:
                    # If decryption fails, assume it's not encrypted
                    decrypted[key] = value
            elif isinstance(value, dict):
                decrypted[key] = self.decrypt_dict(value)
            else:
                decrypted[key] = value
        return decrypted


# Global encryption instance
vault_encryption = VaultEncryption()