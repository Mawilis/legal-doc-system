"""WILSY OS Legal Operations return-ready notification issuance orchestrator.

TITLE: Legal Operations Return-Ready Notification Issuance Orchestrator
VERSION: v1.0.0-L8-8G-RETURN-READY-NOTIFICATION-ISSUANCE
AUTHORITY: Wilsy OS Core Governance / Python EOS Legal Operations
EPITOME: Rehydrate one exact canonical P2 ReturnOfService snapshot, derive one
         immutable L8-8E RETURN_READY intent and persist/replay it through L8-8F
         inside one caller-owned active transaction.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tools/eos/legal_operations/orchestration/legal_return_ready_notification_issuance_orchestrator.py
COLLABORATION / OWNERSHIP: P1/P2 own ReturnOfService truth and durable lifecycle
                            snapshots. L8-8E owns notification intent semantics.
                            L8-8F owns append-only notification persistence.
                            This module composes those authorities only.
CERTIFICATION / UPDATE DATE: 2026-10-12
CHANGELOG: 2026-10-12 v1.0.0-L8-8G-RETURN-READY-NOTIFICATION-ISSUANCE
           establishes exact tenant/evidence-identity resolution of canonical
           ReturnOfService, active caller-transaction enforcement, L8-8E intent
           derivation and L8-8F replay-safe persistence without recipient,
           transport, lifecycle, Court, billing or financial authority.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2; ISO 27001.
SECURITY / PRIVACY POSTURE: Accepts only tenant id, P2 evidence identity and one
                             opaque notification id. No recipient/contact data,
                             message body, provider credential or transport secret.
TENANT BOUNDARY: The requested tenant must exactly match the tenant of the
                 rehydrated canonical ReturnOfService; foreign evidence remains
                 unavailable and cannot be rebound.
AUTHORITY BOUNDARY: Notification issuance composition only. It cannot create,
                    alter or certify service, return, custody, pickup, Court,
                    invoice, payment, execution or settlement truth.
TRANSACTION BOUNDARY: Caller owns one already-active transaction spanning P2
                      return read and L8-8F append/replay. This module never
                      starts, commits, aborts, retries or reconciles transactions.
FINANCIAL AUTHORITY BOUNDARY: None. Kennel EOS remains the exclusive financial
                              execution authority; settlement remains separate.
FAIL-CLOSED DECLARATION: Missing transaction, malformed tenant/evidence identity,
                         absent/corrupt/wrong-type/foreign return truth, invalid
                         notification derivation or persistence failure reject.
"""
from __future__ import annotations

import re
from typing import Any, Final, NoReturn

from tools.eos.legal_operations.domain.legal_operations_lifecycle import (
    ReturnOfService,
)
from tools.eos.legal_operations.domain.legal_return_ready_notification import (
    LegalReturnReadyNotification,
    LegalReturnReadyNotificationError,
    create_return_ready_notification,
)
from tools.eos.legal_operations.registry.legal_operations_lifecycle_registry import (
    LegalOperationsLifecycleRegistry,
    LegalOperationsLifecycleRegistryError,
)
from tools.eos.legal_operations.registry.legal_return_ready_notification_registry import (
    LegalReturnReadyNotificationRegistry,
    LegalReturnReadyNotificationRegistryError,
)


VERSION: Final[str] = "v1.0.0-L8-8G-RETURN-READY-NOTIFICATION-ISSUANCE"

_IDENTITY: Final[re.Pattern[str]] = re.compile(
    r"^[A-Za-z0-9][A-Za-z0-9._:-]{0,159}$"
)
_SHA3: Final[re.Pattern[str]] = re.compile(r"^[0-9a-f]{128}$")
_FORBIDDEN_TENANTS: Final[frozenset[str]] = frozenset(
    {"default", "global", "global_root", "root", "master", "*"}
)


class LegalReturnReadyNotificationIssuanceError(RuntimeError):
    """Stable fail-closed failure for L8-8G issuance composition."""

    def __init__(self, code: str) -> None:
        self.code = code
        super().__init__(code)


def _fail(code: str) -> NoReturn:
    raise LegalReturnReadyNotificationIssuanceError(code)


def _tenant(value: object) -> str:
    if (
        not isinstance(value, str)
        or value != value.strip()
        or _IDENTITY.fullmatch(value) is None
        or value.casefold() in _FORBIDDEN_TENANTS
    ):
        _fail("L8_8G_TENANT_INVALID")
    return value


def _evidence_identity(value: object) -> str:
    if not isinstance(value, str) or _SHA3.fullmatch(value) is None:
        _fail("L8_8G_RETURN_EVIDENCE_IDENTITY_INVALID")
    return value


def _notification_id(value: object) -> str:
    if (
        not isinstance(value, str)
        or value != value.strip()
        or _IDENTITY.fullmatch(value) is None
    ):
        _fail("L8_8G_NOTIFICATION_ID_INVALID")
    return value


def _active_transaction(session: Any) -> Any:
    if session is None:
        _fail("L8_8G_ACTIVE_TRANSACTION_REQUIRED")
    active = getattr(session, "in_transaction", False)
    if callable(active):
        active = active()
    if active is not True:
        _fail("L8_8G_ACTIVE_TRANSACTION_REQUIRED")
    return session


def issue_return_ready_notification(
    *,
    tenant_id: str,
    return_evidence_identity: str,
    notification_id: str,
    lifecycle_collection: Any,
    notification_collection: Any,
    session: Any,
) -> LegalReturnReadyNotification:
    """Issue one durable RETURN_READY intent from exact canonical return truth.

    The caller provides one tenant-scoped P2 evidence identity, not free-form
    return fields. The exact ReturnOfService is rehydrated through the canonical
    lifecycle registry inside the caller transaction, revalidated by L8-8E,
    then persisted/replayed through L8-8F using the same transaction.

    Recipient resolution and external delivery are intentionally absent.
    """
    tx = _active_transaction(session)
    tenant = _tenant(tenant_id)
    evidence_identity = _evidence_identity(return_evidence_identity)
    notice_id = _notification_id(notification_id)

    try:
        source = LegalOperationsLifecycleRegistry.get(
            tenant,
            evidence_identity,
            lifecycle_collection,
            session=tx,
        )
    except LegalOperationsLifecycleRegistryError as error:
        raise LegalReturnReadyNotificationIssuanceError(
            "L8_8G_RETURN_UNAVAILABLE"
        ) from error

    if type(source) is not ReturnOfService:
        _fail("L8_8G_RETURN_TYPE_INVALID")
    if source.tenant_id != tenant:
        _fail("L8_8G_RETURN_SCOPE_MISMATCH")

    try:
        intent = create_return_ready_notification(
            return_of_service=source,
            notification_id=notice_id,
        )
    except LegalReturnReadyNotificationError as error:
        raise LegalReturnReadyNotificationIssuanceError(
            "L8_8G_NOTIFICATION_INVALID"
        ) from error

    try:
        return LegalReturnReadyNotificationRegistry(
            notification_collection
        ).create_or_replay(
            intent,
            session=tx,
        )
    except LegalReturnReadyNotificationRegistryError as error:
        raise LegalReturnReadyNotificationIssuanceError(
            "L8_8G_PERSISTENCE_FAILED"
        ) from error


__all__ = [
    "VERSION",
    "LegalReturnReadyNotificationIssuanceError",
    "issue_return_ready_notification",
]


# ARTIFACT: legal_return_ready_notification_issuance_orchestrator.py
# VERSION: v1.0.0-L8-8G-RETURN-READY-NOTIFICATION-ISSUANCE
# AUTHORITY BOUNDARY: exact canonical ReturnOfService -> immutable RETURN_READY intent -> append/replay only
# TENANT POSTURE: exact requested tenant must own the P2 return evidence identity
# TRANSACTION POSTURE: caller owns one active transaction spanning P2 read and intent persistence
# DELIVERY POSTURE: no recipient/channel/provider/message/transport/delivery authority
# FAIL-CLOSED POSTURE: invalid/absent/wrong-type/foreign return truth or persistence failure rejects
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively
# END OF WILSY OS SOVEREIGN ARTIFACT
