"""
Security utilities: secret encryption/masking helpers and shared settings.
"""
from __future__ import annotations

import os
from functools import lru_cache
from typing import Optional

from cryptography.fernet import Fernet, InvalidToken

SECRET_PREFIX = "enc::"
SENSITIVE_SETTING_KEYS = {
    "openai_api_key",
    "gemini_api_key",
    "anthropic_api_key",
    "shopify_access_token",
    "wordpress_pass",
}


class EncryptionKeyMissing(RuntimeError):
    """Raised when a sensitive value needs encryption but the key is missing."""


@lru_cache(maxsize=1)
def _get_fernet() -> Optional[Fernet]:
    key = os.getenv("APP_ENCRYPTION_KEY")
    if not key:
        return None
    normalized = key.encode() if not isinstance(key, bytes) else key
    return Fernet(normalized)


def is_sensitive_setting(key: str) -> bool:
    return key in SENSITIVE_SETTING_KEYS


def ensure_encryption_key() -> Fernet:
    cipher = _get_fernet()
    if cipher is None:
        raise EncryptionKeyMissing(
            "APP_ENCRYPTION_KEY is not configured. Generate one via "
            "`python -c \"from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())\"` "
            "and set it in the environment before storing sensitive settings."
        )
    return cipher


def encrypt_sensitive_value(key: str, value: Optional[str]) -> Optional[str]:
    if not value or not is_sensitive_setting(key):
        return value
    if value.startswith(SECRET_PREFIX):
        return value
    cipher = ensure_encryption_key()
    token = cipher.encrypt(value.encode("utf-8"))
    return f"{SECRET_PREFIX}{token.decode('utf-8')}"


def decrypt_sensitive_value(key: str, value: Optional[str]) -> Optional[str]:
    if not value:
        return value
    if not (is_sensitive_setting(key) or value.startswith(SECRET_PREFIX)):
        return value
    if not value.startswith(SECRET_PREFIX):
        return value
    cipher = ensure_encryption_key()
    token = value[len(SECRET_PREFIX):]
    try:
        return cipher.decrypt(token.encode("utf-8")).decode("utf-8")
    except InvalidToken as exc:
        raise ValueError("Failed to decrypt stored secret. Key mismatch?") from exc


def mask_sensitive_value(value: Optional[str]) -> str:
    if not value:
        return ""
    return "********"


def prepare_setting_for_response(setting: dict) -> dict:
    """Return a copy of the setting dict with masking metadata applied."""
    result = dict(setting)
    key = result.get("key", "")
    value = result.get("value")
    decrypted_value = decrypt_sensitive_value(key, value)
    result["value"] = decrypted_value
    if is_sensitive_setting(key):
        result["is_masked"] = bool(decrypted_value)
        result["value"] = mask_sensitive_value(decrypted_value)
    else:
        result["is_masked"] = False
    return result
