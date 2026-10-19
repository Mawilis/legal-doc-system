"""TITLE: WILSY OS P9 Reassignment Recipient Currentness Composer.
VERSION: v1.0.0-P9-R77-RECIPIENT-CURRENTNESS-GREEN
ARTIFACT: legal_work_reassignment_recipient_currentness_composer.py
AUTHORITY: Transaction-bound composition of canonical identity reads only.
EPITOME: Resolve exact principal and tenant-membership snapshots inside one
    already-active caller-owned transaction, then reuse the pure recipient
    identity validator without granting recipient admission or reassignment.
ABSOLUTE CANONICAL PATH:
    /Users/wilsonkhanyezi/legal-doc-system/tools/eos/legal_operations/
    orchestration/legal_work_reassignment_recipient_currentness_composer.py
COLLABORATION / OWNERSHIP: Wilsy OS Core Engineering; composes canonical IAM
    read repositories with Legal Operations snapshot-consistency validation.
CERTIFICATION / UPDATE DATE: 2026-10-19
CHANGELOG:
    2026-10-19 v1.0.0-P9-R77-RECIPIENT-CURRENTNESS-GREEN
    Establishes principal-first, exact-session canonical currentness reads.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2 technical controls.
SECURITY / PRIVACY POSTURE: Stable non-sensitive errors; no identifier logging,
    global collection fallback, persistence, telemetry, or authority leakage.
TENANT BOUNDARY: Exact non-pseudo tenant and recipient principal pair only.
AUTHORITY BOUNDARY: Current identity composition is not IAM authorization,
    professional eligibility, matter access, confidentiality or ethical-wall
    clearance, supervisor approval, recipient admission, or reassignment.
FINANCIAL AUTHORITY BOUNDARY: None; Kennel EOS remains exclusive.
"""

from __future__ import annotations

from collections.abc import Callable
from typing import Final, NoReturn, cast

from tools.eos.auth.principal_authority import PrincipalAuthority
from tools.eos.auth.tenant_membership import TenantMembershipAuthority
from tools.eos.legal_operations.service.legal_work_reassignment_recipient_identity import (
    LegalWorkReassignmentRecipientIdentityError,
    validate_legal_work_reassignment_recipient_identity,
)

VERSION: Final[str] = "v1.0.0-P9-R77-RECIPIENT-CURRENTNESS-GREEN"

_FORBIDDEN_TENANTS: Final[frozenset[str]] = frozenset(
    {"default", "global", "root", "*"}
)


class LegalWorkReassignmentRecipientCurrentnessError(RuntimeError):
    """Bounded failure to compose exact current recipient identity.

    The error discloses no tenant, principal, repository, or persisted snapshot
    material. It grants no retry, transaction, admission, or execution authority.
    """

    def __init__(self, code: str) -> None:
        super().__init__(code)
        self.code = code


def _fail(code: str) -> NoReturn:
    raise LegalWorkReassignmentRecipientCurrentnessError(code)


def _validated_identifier(name: str, value: object, *, tenant: bool = False) -> str:
    """Return one exact bounded identifier or fail before repository access."""
    if (
        type(value) is not str
        or not value
        or value != value.strip()
        or len(value) > 512
        or "*" in value
        or (tenant and value.casefold() in _FORBIDDEN_TENANTS)
    ):
        _fail(f"P9_R77_{name}_INVALID")
    return value


def _active_transaction(session: object) -> object:
    """Require, but never own, the caller's already-active transaction."""
    if session is None:
        _fail("P9_R77_ACTIVE_TRANSACTION_REQUIRED")
    try:
        marker = getattr(session, "in_transaction", None)
        active = marker() if callable(marker) else marker
    except Exception as error:
        raise LegalWorkReassignmentRecipientCurrentnessError(
            "P9_R77_ACTIVE_TRANSACTION_REQUIRED"
        ) from error
    if active is not True:
        _fail("P9_R77_ACTIVE_TRANSACTION_REQUIRED")
    return session


def _resolver(name: str, repository: object) -> Callable[..., object]:
    """Require an explicitly injected repository with a callable read seam."""
    resolve = getattr(repository, "resolve", None)
    if not callable(resolve):
        _fail(f"P9_R77_{name}_REPOSITORY_INVALID")
    return cast(Callable[..., object], resolve)


def compose_recipient_currentness(
    *,
    tenant_id: str,
    recipient_principal_id: str,
    session: object,
    principal_repository: object,
    membership_repository: object,
    principal_collection: object,
    membership_collection: object,
) -> tuple[PrincipalAuthority, TenantMembershipAuthority]:
    """Return unchanged current snapshots resolved in one active transaction.

    Principal authority is read first and membership second using the identical
    caller-owned session and explicit injected collections. Any malformed input,
    repository failure, absence, corruption, or identity inconsistency becomes a
    bounded non-sensitive error. This function performs no write, transaction
    lifecycle action, IAM grant, recipient admission, or reassignment execution.

    Raises:
        LegalWorkReassignmentRecipientCurrentnessError: If any prerequisite or
            canonical read/validation boundary fails closed.
    """
    tenant = _validated_identifier("TENANT_ID", tenant_id, tenant=True)
    recipient = _validated_identifier(
        "RECIPIENT_PRINCIPAL_ID", recipient_principal_id
    )
    tx = _active_transaction(session)
    principal_resolve = _resolver("PRINCIPAL", principal_repository)
    membership_resolve = _resolver("MEMBERSHIP", membership_repository)
    if principal_collection is None:
        _fail("P9_R77_PRINCIPAL_COLLECTION_REQUIRED")
    if membership_collection is None:
        _fail("P9_R77_MEMBERSHIP_COLLECTION_REQUIRED")

    try:
        principal = principal_resolve(
            recipient,
            principal_collection,
            session=tx,
        )
    except LegalWorkReassignmentRecipientCurrentnessError:
        raise
    except Exception as error:
        raise LegalWorkReassignmentRecipientCurrentnessError(
            "P9_R77_PRINCIPAL_AUTHORITY_UNAVAILABLE"
        ) from error

    try:
        membership = membership_resolve(
            recipient,
            tenant,
            membership_collection,
            session=tx,
        )
    except LegalWorkReassignmentRecipientCurrentnessError:
        raise
    except Exception as error:
        raise LegalWorkReassignmentRecipientCurrentnessError(
            "P9_R77_MEMBERSHIP_AUTHORITY_UNAVAILABLE"
        ) from error

    try:
        return validate_legal_work_reassignment_recipient_identity(
            tenant_id=tenant,
            recipient_principal_id=recipient,
            principal_authority=principal,
            membership_authority=membership,
        )
    except LegalWorkReassignmentRecipientIdentityError as error:
        raise LegalWorkReassignmentRecipientCurrentnessError(
            "P9_R77_RECIPIENT_IDENTITY_NOT_CURRENT"
        ) from error
    except Exception as error:
        raise LegalWorkReassignmentRecipientCurrentnessError(
            "P9_R77_RECIPIENT_IDENTITY_UNAVAILABLE"
        ) from error


__all__ = [
    "VERSION",
    "LegalWorkReassignmentRecipientCurrentnessError",
    "compose_recipient_currentness",
]


# WILSY OS SOVEREIGN ARTIFACT SEAL
# ARTIFACT: legal_work_reassignment_recipient_currentness_composer.py
# VERSION: v1.0.0-P9-R77-RECIPIENT-CURRENTNESS-GREEN
# AUTHORITY BOUNDARY: transaction-bound current identity reads only
# TENANT POSTURE: exact non-pseudo tenant and recipient pair; fail closed
# CURRENTNESS / IAM / MATTER / APPROVAL AUTHORITY: NOT GRANTED
# REASSIGNMENT EXECUTION / PERSISTENCE: NONE
# FINANCIAL EXECUTION AUTHORITY: NONE; KENNEL EOS EXCLUSIVELY
# END OF WILSY OS SOVEREIGN ARTIFACT
