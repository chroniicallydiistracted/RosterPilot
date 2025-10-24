"""Utilities for encrypting and decrypting sensitive secrets."""

from __future__ import annotations

from dataclasses import dataclass

from cryptography.fernet import Fernet, InvalidToken

from app.core.config import Settings


class TokenEncryptionError(RuntimeError):
    """Raised when token encryption or decryption fails."""


@dataclass(slots=True, frozen=True)
class TokenCipher:
    """Wrapper around Fernet symmetric encryption for OAuth tokens."""

    fernet: Fernet

    @classmethod
    def from_settings(cls, settings: Settings) -> "TokenCipher":
        """Instantiate the cipher from application settings."""

        key = settings.token_enc_key
        if not key:
            raise TokenEncryptionError("TOKEN_ENC_KEY is not configured")
        try:
            fernet = Fernet(key.encode("utf-8"))
        except ValueError as exc:  # pragma: no cover - defensive guard
            raise TokenEncryptionError("Invalid TOKEN_ENC_KEY provided") from exc
        return cls(fernet=fernet)

    def encrypt(self, value: str) -> str:
        """Encrypt a sensitive string value."""

        token = value.encode("utf-8")
        return self.fernet.encrypt(token).decode("utf-8")

    def decrypt(self, value: str) -> str:
        """Decrypt a previously encrypted value."""

        try:
            decrypted = self.fernet.decrypt(value.encode("utf-8"))
        except InvalidToken as exc:  # pragma: no cover - indicates corrupted data
            raise TokenEncryptionError("Failed to decrypt token payload") from exc
        return decrypted.decode("utf-8")
