from cryptography.fernet import Fernet
from app.config import get_settings

settings = get_settings()
_fernet = Fernet(settings.encryption_key.encode("utf-8"))

class EncryptionService:
    @staticmethod
    def encrypt(value: str) -> str:
        if not value:
            return value
        return _fernet.encrypt(value.encode("utf-8")).decode("utf-8")

    @staticmethod
    def decrypt(value: str) -> str:
        if not value:
            return value
        try:
            return _fernet.decrypt(value.encode("utf-8")).decode("utf-8")
        except Exception:
            return value
