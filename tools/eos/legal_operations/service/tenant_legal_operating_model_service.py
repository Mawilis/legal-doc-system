"""WILSY OS Tenant Legal Operating Model command service.

TITLE: Tenant Legal Operating Model Command Service
VERSION: v1.0.0-CX26-R3-CURRENT-OPERATING-MODEL-COMMAND
AUTHORITY: Wilsy OS Core Governance / Python EOS Legal Operations
EPITOME: Authorize and compose one immutable current tenant Legal operating-model revision.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tools/eos/legal_operations/service/tenant_legal_operating_model_service.py
COLLABORATION / OWNERSHIP: CX26-R2 registry owns persistence; G7B owns model semantics; CX26-R3 owns command admission and optimistic revision composition.
CERTIFICATION / UPDATE DATE: 2026-10-13
CHANGELOG: v1.0.0-CX26-R3 establishes transaction-bound authorization, currentness comparison, deterministic idempotent replay, and server-owned revision construction.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2; ISO 27001.
SECURITY / PRIVACY POSTURE: Exact own-tenant authorization precedes every domain read or write; no request authority fields are trusted.
TENANT BOUNDARY: Authenticated tenant and requested tenant must correlate exactly; every persistence operation is tenant-first.
AUTHORITY BOUNDARY: Configuration admission only; activation never grants a principal role, permission, entitlement, workflow, or legal execution authority.
FINANCIAL AUTHORITY BOUNDARY: None; Kennel EOS exclusively owns financial execution and settlement.
TRANSACTION BOUNDARY: The caller supplies and owns one active transaction spanning authorization, currentness, and persistence.
FAIL-CLOSED DECLARATION: Denial, unavailable authority, stale revision, divergent replay, corrupt history, and persistence failure reject without mutation.
"""
from __future__ import annotations

from datetime import datetime, timezone
from hashlib import sha3_512
import hmac
from typing import Any, Final, NoReturn

from tools.eos.auth.tenant_authorization import (
    TenantAuthorizationReason,
    authorize_tenant_operation,
)
from tools.eos.legal_operations.domain.tenant_legal_operating_model import (
    TenantLegalOperatingModel,
    TenantLegalOperatingModelError,
)
from tools.eos.legal_operations.registry.tenant_legal_operating_model_registry import (
    TenantLegalOperatingModelRegistry,
    TenantLegalOperatingModelRegistryNotFoundError,
)

VERSION: Final[str] = "v1.0.0-CX26-R3-CURRENT-OPERATING-MODEL-COMMAND"
PERMISSION: Final[str] = "legal_operations:operating_model:manage"
OPERATION: Final[str] = "legal_operating_model_manage"


class TenantLegalOperatingModelServiceError(RuntimeError):
    """Base command-service failure exposing one stable non-secret code."""

    def __init__(self, code: str) -> None:
        self.code = code
        super().__init__(code)


class TenantLegalOperatingModelAuthorizationDeniedError(TenantLegalOperatingModelServiceError):
    """Current authority denied the exact own-tenant operation."""


class TenantLegalOperatingModelAuthorityUnavailableError(TenantLegalOperatingModelServiceError):
    """A required current authorization authority could not be resolved."""


class TenantLegalOperatingModelRevisionConflictError(TenantLegalOperatingModelServiceError):
    """The caller's expected revision or idempotent command conflicts."""


def _fail(error_type: type[TenantLegalOperatingModelServiceError], code: str) -> NoReturn:
    """Raise one typed service error without disclosing authority internals."""
    raise error_type(code)


def _active_transaction(session: Any) -> Any:
    """Require the caller-owned transaction used by authorization and registry."""
    marker = getattr(session, "in_transaction", None)
    active = marker() if callable(marker) else marker
    if active is not True:
        _fail(TenantLegalOperatingModelAuthorityUnavailableError, "CX26_R3_ACTIVE_TRANSACTION_REQUIRED")
    return session


def _idempotent_model_id(tenant_id: str, idempotency_key: str) -> str:
    """Derive a non-reversible stable model identity from tenant and command key."""
    material = f"WILSY-CX26-R3\x00{tenant_id}\x00{idempotency_key}".encode("utf-8")
    return f"tlom-{sha3_512(material).hexdigest()}"


def _authorize(
    *,
    tenant_id: str,
    principal_id: str,
    principal_repository: Any,
    membership_repository: Any,
    business_role_repository: Any,
    role_assignment_repository: Any,
    session: Any,
) -> None:
    """Require exact current IAM inside the mutation/read transaction."""
    decision = authorize_tenant_operation(
        principal_id=principal_id,
        tenant_id=tenant_id,
        permission_id=PERMISSION,
        operation=OPERATION,
        principal_repository=principal_repository,
        membership_repository=membership_repository,
        business_role_repository=business_role_repository,
        role_assignment_repository=role_assignment_repository,
        session=session,
    )
    if decision.authorized and decision.reason is TenantAuthorizationReason.AUTHORIZED:
        return
    unavailable = {
        TenantAuthorizationReason.PRINCIPAL_AUTHORITY_UNAVAILABLE,
        TenantAuthorizationReason.MEMBERSHIP_AUTHORITY_UNAVAILABLE,
        TenantAuthorizationReason.TENANT_BUSINESS_ROLE_AUTHORITY_UNAVAILABLE,
        TenantAuthorizationReason.ROLE_ASSIGNMENT_AUTHORITY_UNAVAILABLE,
        TenantAuthorizationReason.WORKFORCE_AUTHORITY_UNAVAILABLE,
    }
    if decision.reason in unavailable:
        _fail(TenantLegalOperatingModelAuthorityUnavailableError, "CX26_R3_AUTHORITY_UNAVAILABLE")
    _fail(TenantLegalOperatingModelAuthorizationDeniedError, "CX26_R3_AUTHORIZATION_DENIED")


def _validate_command(expected_revision: object, activated_item_ids: object, idempotency_key: object) -> tuple[int | None, tuple[str, ...], str]:
    """Validate the narrow command envelope before opening domain semantics."""
    if expected_revision is not None and (
        isinstance(expected_revision, bool)
        or not isinstance(expected_revision, int)
        or expected_revision < 1
    ):
        _fail(TenantLegalOperatingModelRevisionConflictError, "CX26_R3_EXPECTED_REVISION_INVALID")
    if not isinstance(activated_item_ids, (list, tuple)):
        raise TenantLegalOperatingModelError("G7B_ACTIVATED_ITEMS_INVALID")
    if not isinstance(idempotency_key, str) or not idempotency_key or idempotency_key != idempotency_key.strip() or len(idempotency_key) > 200:
        _fail(TenantLegalOperatingModelRevisionConflictError, "CX26_R3_IDEMPOTENCY_KEY_INVALID")
    return expected_revision, tuple(activated_item_ids), idempotency_key


def get_current_tenant_legal_operating_model(
    *,
    tenant_id: str,
    principal_id: str,
    registry: TenantLegalOperatingModelRegistry,
    principal_repository: Any,
    membership_repository: Any,
    business_role_repository: Any,
    role_assignment_repository: Any,
    session: Any,
    observed_at: datetime | None = None,
) -> TenantLegalOperatingModel:
    """Return current exact-tenant configuration after transaction-bound authorization.

    This read neither mutates configuration nor grants any downstream capability.
    """
    tx = _active_transaction(session)
    _authorize(
        tenant_id=tenant_id,
        principal_id=principal_id,
        principal_repository=principal_repository,
        membership_repository=membership_repository,
        business_role_repository=business_role_repository,
        role_assignment_repository=role_assignment_repository,
        session=tx,
    )
    moment = observed_at or datetime.now(timezone.utc)
    return registry.resolve_current(tenant_id, moment, session=tx)


def configure_tenant_legal_operating_model(
    *,
    tenant_id: str,
    principal_id: str,
    expected_revision: int | None,
    activated_item_ids: list[str] | tuple[str, ...],
    idempotency_key: str,
    registry: TenantLegalOperatingModelRegistry,
    principal_repository: Any,
    membership_repository: Any,
    business_role_repository: Any,
    role_assignment_repository: Any,
    session: Any,
    effective_from: datetime | None = None,
) -> TenantLegalOperatingModel:
    """Authorize and persist the next immutable current configuration revision.

    Same tenant plus idempotency key and semantically identical command returns
    the original durable revision. Reuse with different content fails closed.
    The caller owns commit, abort, and whole-transaction retry.
    """
    expected, requested_items, key = _validate_command(expected_revision, activated_item_ids, idempotency_key)
    tx = _active_transaction(session)
    _authorize(
        tenant_id=tenant_id,
        principal_id=principal_id,
        principal_repository=principal_repository,
        membership_repository=membership_repository,
        business_role_repository=business_role_repository,
        role_assignment_repository=role_assignment_repository,
        session=tx,
    )
    model_id = _idempotent_model_id(tenant_id, key)
    try:
        replay = registry.get_by_id(tenant_id, model_id, session=tx)
    except TenantLegalOperatingModelRegistryNotFoundError:
        replay = None
    if replay is not None:
        replay_expected = replay.revision - 1 if replay.revision > 1 else None
        if replay_expected == expected and replay.activated_item_ids == tuple(sorted(requested_items)):
            return replay
        _fail(TenantLegalOperatingModelRevisionConflictError, "CX26_R3_DIVERGENT_IDEMPOTENCY_REPLAY")

    now = effective_from or datetime.now(timezone.utc)
    try:
        current = registry.resolve_current(tenant_id, now, session=tx)
    except TenantLegalOperatingModelRegistryNotFoundError:
        current = None
    actual_revision = current.revision if current is not None else None
    if actual_revision != expected:
        _fail(TenantLegalOperatingModelRevisionConflictError, "CX26_R3_EXPECTED_REVISION_CONFLICT")

    candidate = TenantLegalOperatingModel(
        tenant_id=tenant_id,
        operating_model_id=model_id,
        revision=1 if current is None else current.revision + 1,
        activated_item_ids=requested_items,
        effective_from=now,
        supersedes_operating_model_id=None if current is None else current.operating_model_id,
    )
    persisted = registry.create_or_replay(candidate, session=tx)
    if not hmac.compare_digest(persisted.fingerprint, candidate.fingerprint):
        _fail(TenantLegalOperatingModelRevisionConflictError, "CX26_R3_PERSISTED_REPLAY_MISMATCH")
    return persisted


__all__ = [
    "VERSION", "PERMISSION", "OPERATION",
    "TenantLegalOperatingModelServiceError",
    "TenantLegalOperatingModelAuthorizationDeniedError",
    "TenantLegalOperatingModelAuthorityUnavailableError",
    "TenantLegalOperatingModelRevisionConflictError",
    "get_current_tenant_legal_operating_model",
    "configure_tenant_legal_operating_model",
]

# ARTIFACT: tenant_legal_operating_model_service.py
# VERSION: v1.0.0-CX26-R3-CURRENT-OPERATING-MODEL-COMMAND
# AUTHORITY BOUNDARY: exact-IAM tenant configuration admission only; no downstream capability grant
# TENANT POSTURE: authorization precedes every exact-tenant domain read and mutation
# FAIL-CLOSED POSTURE: denial, outage, stale revision, replay divergence, corruption, and persistence failure reject
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively
# END OF WILSY OS SOVEREIGN ARTIFACT
