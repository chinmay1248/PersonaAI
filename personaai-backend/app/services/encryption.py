from cryptography.fernet import Fernet
from app.config import get_settings

settings = get_settings()
_fernet = Fernet(settings.encryption_key.encode("utf-8"))

class EncryptionService:
    def __init__(self, key: str | bytes | None = None, *, strict: bool = True) -> None:
        raw_key = key or settings.encryption_key
        if isinstance(raw_key, str):
            raw_key = raw_key.encode("utf-8")
        self._fernet = Fernet(raw_key)
        self._strict = strict

    def encrypt(self, value: str | None = None) -> str:
        fernet = self._fernet if isinstance(self, EncryptionService) else _fernet
        if not isinstance(self, EncryptionService):
            value = self
        if not value:
            return value
        return fernet.encrypt(value.encode("utf-8")).decode("utf-8")

    def decrypt(self, value: str | None = None) -> str:
        instance_call = isinstance(self, EncryptionService)
        fernet = self._fernet if instance_call else _fernet
        if not instance_call:
            value = self
        if not value:
            return value
        try:
            return fernet.decrypt(value.encode("utf-8")).decode("utf-8")
        except Exception:
            if instance_call and self._strict:
                raise
            return value
