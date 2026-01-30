from cryptography.fernet import Fernet
from base64 import urlsafe_b64encode
import hashlib
import os

from app.core.config import settings


class EncryptionService:
    """Service for encrypting and decrypting sensitive data like database passwords."""

    def __init__(self):
        self._fernet = None

    def _get_fernet(self) -> Fernet:
        """Get or create Fernet instance using SECRET_KEY."""
        if self._fernet is None:
            # Derive a 32-byte key from SECRET_KEY using SHA256
            key = hashlib.sha256(settings.SECRET_KEY.encode()).digest()
            fernet_key = urlsafe_b64encode(key)
            self._fernet = Fernet(fernet_key)
        return self._fernet

    def encrypt(self, plaintext: str) -> str:
        """Encrypt a plaintext string and return base64-encoded ciphertext."""
        if not plaintext:
            return ""
        fernet = self._get_fernet()
        encrypted = fernet.encrypt(plaintext.encode())
        return encrypted.decode()

    def decrypt(self, ciphertext: str) -> str:
        """Decrypt a base64-encoded ciphertext and return plaintext."""
        if not ciphertext:
            return ""
        fernet = self._get_fernet()
        decrypted = fernet.decrypt(ciphertext.encode())
        return decrypted.decode()


# Singleton instance
encryption_service = EncryptionService()
