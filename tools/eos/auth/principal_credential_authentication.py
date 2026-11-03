"""Global-principal credential verification without tenant selection or session issuance."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import bcrypt

from tools.eos.auth.principal_status import PrincipalStatus
from tools.eos.auth.principal_authority_repository import (
    PrincipalAuthorityNotFoundError,
    PrincipalAuthorityRepository,
    PrincipalAuthorityRepositoryError,
)
from tools.eos.auth.principal_credential import normalize_principal_email
from tools.eos.auth.principal_credential_repository import (
    PrincipalCredentialNotFoundError,
    PrincipalCredentialRepository,
    PrincipalCredentialRepositoryError,
)

VERSION = "v1.0.0-GLOBAL-PRINCIPAL-CREDENTIAL-AUTHENTICATION"


class GlobalPrincipalAuthenticationUnavailable(RuntimeError):
    """A required credential or principal authority could not be read."""


@dataclass(frozen=True, slots=True)
class AuthenticatedGlobalPrincipal:
    """Password-verified global identity; deliberately contains no tenant scope."""

    principal_id: str
    normalized_email: str
    credential_revision: int
    mfa_enabled: bool


def authenticate_global_principal(
    *,
    email: str,
    password: str,
    credential_repository: Any = None,
    principal_repository: Any = None,
    session: Any = None,
) -> AuthenticatedGlobalPrincipal | None:
    """Verify global credentials and ACTIVE principal status only.

    This function does not enumerate or select tenants, expose memberships,
    select a business capacity, issue a challenge/session/token, or authorize
    any tenant operation. Callers must apply rate limiting and generic failure
    responses at the HTTP boundary, then perform explicit membership selection.
    """
    try:
        normalized_email = normalize_principal_email(email)
    except ValueError:
        return None
    if not isinstance(password, str) or not password:
        return None

    credentials = credential_repository or PrincipalCredentialRepository()
    principals = principal_repository or PrincipalAuthorityRepository()
    try:
        credential = credentials.get_by_email(normalized_email, session=session)
    except PrincipalCredentialNotFoundError:
        # Consume bcrypt-equivalent work for unknown emails so the public
        # boundary does not expose a cheap account-existence timing oracle.
        try:
            bcrypt.hashpw(
                password.encode("utf-8"),
                bcrypt.gensalt(rounds=12),
            )
        except (TypeError, ValueError):
            pass
        return None
    except PrincipalCredentialRepositoryError as error:
        raise GlobalPrincipalAuthenticationUnavailable(
            "GLOBAL_PRINCIPAL_CREDENTIAL_UNAVAILABLE"
        ) from error

    try:
        password_matches = bcrypt.checkpw(
            password.encode("utf-8"),
            credential.password_hash.encode("utf-8"),
        )
    except (TypeError, ValueError):
        return None
    if not password_matches:
        return None

    try:
        principal = principals.get(credential.principal_id, session=session)
    except PrincipalAuthorityNotFoundError:
        return None
    except PrincipalAuthorityRepositoryError as error:
        raise GlobalPrincipalAuthenticationUnavailable(
            "GLOBAL_PRINCIPAL_AUTHORITY_UNAVAILABLE"
        ) from error

    if (
        getattr(principal, "principal_id", None) != credential.principal_id
        or getattr(principal, "status", None) is not PrincipalStatus.ACTIVE
    ):
        return None

    return AuthenticatedGlobalPrincipal(
        principal_id=credential.principal_id,
        normalized_email=credential.normalized_email,
        credential_revision=credential.credential_revision,
        mfa_enabled=credential.mfa_enabled,
    )


__all__ = [
    "VERSION",
    "GlobalPrincipalAuthenticationUnavailable",
    "AuthenticatedGlobalPrincipal",
    "authenticate_global_principal",
]
