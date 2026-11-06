"""Tenant-neutral global principal credential snapshot.

Credential verification material is deliberately separated from tenant membership,
business capacity, authorization, workspace selection and financial authority.
"""
from __future__ import annotations

from dataclasses import dataclass, field

MAX_CREDENTIAL_REVISION = (1 << 63) - 1


@dataclass(frozen=True, slots=True)
class PrincipalCredential:
    """Global credential identity keyed by principal and normalized email."""

    principal_id: str
    normalized_email: str
    password_hash: str = field(repr=False)
    credential_revision: int
    mfa_enabled: bool

    def __post_init__(self) -> None:
        if not isinstance(self.principal_id, str) or not self.principal_id or self.principal_id != self.principal_id.strip():
            raise ValueError("principal_id must be a non-empty trimmed string")
        if not isinstance(self.normalized_email, str) or not self.normalized_email or self.normalized_email != self.normalized_email.strip() or self.normalized_email != self.normalized_email.lower():
            raise ValueError("normalized_email must be lowercase and trimmed")
        validate_password_hash(self.password_hash)
        if not isinstance(self.mfa_enabled, bool):
            raise TypeError("mfa_enabled must be an explicit boolean")
        if isinstance(self.credential_revision, bool) or not isinstance(self.credential_revision, int) or not 0 <= self.credential_revision <= MAX_CREDENTIAL_REVISION:
            raise ValueError("credential_revision must be a bounded non-negative integer")


def normalize_principal_email(value: object) -> str:
    """Normalize the email key exactly as the existing authentication boundary."""
    if not isinstance(value, str):
        raise ValueError("principal email is invalid")
    normalized = value.strip().lower()
    if not normalized or "@" not in normalized or any(character.isspace() for character in normalized):
        raise ValueError("principal email is invalid")
    return normalized


def validate_password_hash(value: object) -> str:
    """Validate bcrypt verifier shape without exposing or transforming it."""
    if not isinstance(value, str) or not value.startswith(("$2a$", "$2b$", "$2y$")) or len(value) != 60:
        raise ValueError("password_hash must be a supported bcrypt verifier")
    return value


__all__ = ["MAX_CREDENTIAL_REVISION", "PrincipalCredential", "normalize_principal_email", "validate_password_hash"]
