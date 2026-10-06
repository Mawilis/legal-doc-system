"""Deterministic Legal Operations entity read models.

TITLE: WILSY OS Legal Operations Current and History Read Model
VERSION: v1.0.0-L8-5-LEGAL-OPERATIONS-ENTITY-READ-MODEL
AUTHORITY: Wilsy OS Legal Operations deterministic read-model composition.
EPITOME: Compose exact tenant-scoped P2 immutable snapshots with L8-0 current
         projection to expose deterministic current-plus-history read models
         for one entity or one complete tenant/entity class without creating
         queue, search, lifecycle, service, billing, or financial truth.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tools/eos/legal_operations/domain/legal_operations_read_model.py
COLLABORATION / OWNERSHIP: P1 owns lifecycle/evidence values; P2 owns durable
                            snapshot enumeration and strict hydration; L8-0
                            owns deterministic current-state selection; L8-5
                            owns read-model composition only. HTTP/IAM, queues,
                            search, client policy, and Intelligence projections
                            remain separate bounded gates.
CERTIFICATION / UPDATE DATE: 2026-09-23
CHANGELOG: 2026-09-23 v1.0.0-L8-5-LEGAL-OPERATIONS-ENTITY-READ-MODEL
           establishes deterministic exact-entity and tenant/entity-class
           current-plus-history models using only canonical P2 enumeration and
           L8-0 projection, with exact tenant/type/identity validation,
           deterministic identity ordering, bounded absence, and fail-closed
           corruption/divergence translation.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2; ISO 27001.
SECURITY / PRIVACY POSTURE: Read-only composition over canonical opaque P1
                             evidence. It accepts no credentials, JWT claims,
                             browser authority, raw provider payloads, or new
                             customer/person identity fields.
TENANT BOUNDARY: Every P2 read binds one explicit P1-valid tenant. Returned
                 snapshots must match the requested tenant, entity type, and
                 canonical identity; foreign evidence is never queried.
AUTHORITY BOUNDARY: Projection only. This module cannot register, accept,
                    receive, allocate, attempt, serve, generate a return, bill,
                    invoice, pay, execute, settle, authorize, or persist truth.
FINANCIAL AUTHORITY BOUNDARY: Kennel EOS exclusively owns financial execution
                              and settlement; these read models never infer
                              invoice, paid, execution, or settlement state.
TRANSACTION BOUNDARY: Caller-owned sessions are forwarded unchanged to P2.
                      This module never starts, commits, aborts, retries, or
                      stores a database client/session.
FAIL-CLOSED DECLARATION: Unsupported type, absence, tenant/type/identity drift,
                         malformed P2 evidence, static divergence, immutable
                         divergence, history forks, and ambiguous current state
                         reject without fallback or arbitrary row selection.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Final, NoReturn, cast

from tools.eos.legal_operations.domain.legal_operations_current_projection import (
    LegalOperationsCurrentProjectionError,
    LifecycleValue,
    resolve_current_lifecycle_snapshot,
)
from tools.eos.legal_operations.domain.legal_operations_lifecycle import (
    CaseMatter,
    Deputy,
    District,
    DocumentCustodyEvent,
    LegalInstruction,
    ProcessDocument,
    ReturnOfService,
    ServiceAttempt,
    ServiceExecution,
    SheriffOffice,
)
from tools.eos.legal_operations.registry.legal_operations_lifecycle_registry import (
    LegalOperationsLifecycleRegistry,
    LegalOperationsLifecycleRegistryError,
)


VERSION: Final[str] = "v1.0.0-L8-5-LEGAL-OPERATIONS-ENTITY-READ-MODEL"

_ENTITY_TYPES: Final[dict[str, type[LifecycleValue]]] = {
    "LegalInstruction": LegalInstruction,
    "CaseMatter": CaseMatter,
    "ProcessDocument": ProcessDocument,
    "District": District,
    "SheriffOffice": SheriffOffice,
    "Deputy": Deputy,
    "DocumentCustodyEvent": DocumentCustodyEvent,
    "ServiceAttempt": ServiceAttempt,
    "ServiceExecution": ServiceExecution,
    "ReturnOfService": ReturnOfService,
}

_ENTITY_ID_FIELDS: Final[dict[str, str]] = {
    "LegalInstruction": "instruction_id",
    "CaseMatter": "case_matter_id",
    "ProcessDocument": "document_id",
    "District": "district_id",
    "SheriffOffice": "sheriff_office_id",
    "Deputy": "deputy_id",
    "DocumentCustodyEvent": "custody_event_id",
    "ServiceAttempt": "attempt_id",
    "ServiceExecution": "service_execution_id",
    "ReturnOfService": "return_id",
}


class LegalOperationsReadModelError(RuntimeError):
    """Stable read-model failure with no mutation or authorization authority."""

    def __init__(self, code: str) -> None:
        self.code = code
        super().__init__(code)


def _fail(
    code: str,
    cause: BaseException | None = None,
) -> NoReturn:
    """Raise one stable L8-5 read-model failure while retaining root cause."""
    error = LegalOperationsReadModelError(code)
    if cause is None:
        raise error
    raise error from cause


def _expected_type(entity_type: str) -> type[LifecycleValue]:
    """Return one canonical P1 entity type or reject unsupported vocabulary."""
    expected = _ENTITY_TYPES.get(entity_type)
    if expected is None:
        _fail("L8_5_ENTITY_TYPE_UNSUPPORTED")
    return expected


def _identity(value: LifecycleValue, entity_type: str) -> str:
    """Return and validate one supported canonical P1 identity."""
    field = _ENTITY_ID_FIELDS.get(entity_type)
    if field is None:
        _fail("L8_5_ENTITY_TYPE_UNSUPPORTED")
    identity = getattr(value, field, None)
    if not isinstance(identity, str) or not identity:
        _fail("L8_5_ENTITY_IDENTITY_INVALID")
    return identity


def _validate_history_scope(
    *,
    tenant_id: str,
    entity_type: str,
    entity_identity: str,
    history: tuple[LifecycleValue, ...],
) -> None:
    """Require every snapshot to remain inside one exact requested scope."""
    expected = _expected_type(entity_type)
    for value in history:
        if type(value) is not expected:
            _fail("L8_5_HISTORY_TYPE_MISMATCH")
        if value.tenant_id != tenant_id:
            _fail("L8_5_HISTORY_TENANT_MISMATCH")
        if _identity(value, entity_type) != entity_identity:
            _fail("L8_5_HISTORY_IDENTITY_MISMATCH")


@dataclass(frozen=True, slots=True)
class LegalOperationsEntityReadModel:
    """One deterministic current-plus-history Legal Operations projection.

    The model is an immutable read projection only. Its current value is
    selected solely by L8-0 over the complete P2-hydrated history for one
    exact tenant/type/identity. It grants no IAM, mutation, service, billing,
    payment, execution, or settlement authority.
    """

    tenant_id: str
    entity_type: str
    entity_identity: str
    current: LifecycleValue
    history: tuple[LifecycleValue, ...]

    def __post_init__(self) -> None:
        if not self.history:
            _fail("L8_5_HISTORY_REQUIRED")
        _validate_history_scope(
            tenant_id=self.tenant_id,
            entity_type=self.entity_type,
            entity_identity=self.entity_identity,
            history=self.history,
        )
        if type(self.current) is not _expected_type(self.entity_type):
            _fail("L8_5_CURRENT_TYPE_MISMATCH")
        if self.current.tenant_id != self.tenant_id:
            _fail("L8_5_CURRENT_TENANT_MISMATCH")
        if _identity(self.current, self.entity_type) != self.entity_identity:
            _fail("L8_5_CURRENT_IDENTITY_MISMATCH")
        if not any(
            value.fingerprint == self.current.fingerprint
            for value in self.history
        ):
            _fail("L8_5_CURRENT_NOT_IN_HISTORY")

    def to_dict(self) -> dict[str, object]:
        """Serialize the bounded projection without persistence internals."""
        return {
            "tenant_id": self.tenant_id,
            "entity_type": self.entity_type,
            "entity_identity": self.entity_identity,
            "current": self.current.to_dict(),
            "history": [value.to_dict() for value in self.history],
        }


def _compose(
    *,
    tenant_id: str,
    entity_type: str,
    entity_identity: str,
    history: tuple[LifecycleValue, ...],
) -> LegalOperationsEntityReadModel:
    """Compose one exact entity model from complete already-hydrated history."""
    expected = _expected_type(entity_type)
    if not history:
        _fail("L8_5_ENTITY_NOT_FOUND")
    _validate_history_scope(
        tenant_id=tenant_id,
        entity_type=entity_type,
        entity_identity=entity_identity,
        history=history,
    )
    try:
        current = resolve_current_lifecycle_snapshot(
            history,
            expected_type=expected,
        )
    except LegalOperationsCurrentProjectionError as error:
        _fail("L8_5_CURRENT_PROJECTION_INVALID", error)
    return LegalOperationsEntityReadModel(
        tenant_id=tenant_id,
        entity_type=entity_type,
        entity_identity=entity_identity,
        current=current,
        history=history,
    )


def get_entity_read_model(
    *,
    tenant_id: str,
    entity_type: str,
    entity_identity: str,
    lifecycle_collection: Any,
    session: Any = None,
) -> LegalOperationsEntityReadModel:
    """Return one deterministic exact-entity current-plus-history projection.

    P2 performs the exact tenant/type/identity read and strict hydration. Empty
    exact scope becomes L8_5_ENTITY_NOT_FOUND. Corruption/outage becomes
    L8_5_EVIDENCE_UNAVAILABLE and L8-0 divergence becomes
    L8_5_CURRENT_PROJECTION_INVALID. Caller session ownership is preserved.
    """
    _expected_type(entity_type)
    try:
        history = LegalOperationsLifecycleRegistry.get_entity_history(
            tenant_id,
            entity_type,
            entity_identity,
            lifecycle_collection,
            session=session,
        )
    except LegalOperationsLifecycleRegistryError as error:
        _fail("L8_5_EVIDENCE_UNAVAILABLE", error)

    return _compose(
        tenant_id=tenant_id,
        entity_type=entity_type,
        entity_identity=entity_identity,
        history=cast(tuple[LifecycleValue, ...], history),
    )


def list_entity_read_models(
    *,
    tenant_id: str,
    entity_type: str,
    lifecycle_collection: Any,
    session: Any = None,
) -> tuple[LegalOperationsEntityReadModel, ...]:
    """Return deterministic current-plus-history models for one tenant/type.

    P2 enumerates every immutable snapshot for the exact tenant/entity class.
    This function groups only by the canonical P1 identity field, then delegates
    each complete history to L8-0 for current selection. Result order is the
    canonical entity identity. Empty scope returns an empty tuple.

    No queue membership, free-text search, authorization, lifecycle mutation,
    billing readiness, financial execution, or settlement truth is inferred.
    """
    expected = _expected_type(entity_type)
    try:
        snapshots = LegalOperationsLifecycleRegistry.get_tenant_entity_snapshots(
            tenant_id,
            entity_type,
            lifecycle_collection,
            session=session,
        )
    except LegalOperationsLifecycleRegistryError as error:
        _fail("L8_5_EVIDENCE_UNAVAILABLE", error)

    grouped: dict[str, list[LifecycleValue]] = {}
    for raw_value in snapshots:
        value = cast(LifecycleValue, raw_value)
        if value.tenant_id != tenant_id:
            _fail("L8_5_HISTORY_TENANT_MISMATCH")
        if type(value) is not expected:
            _fail("L8_5_HISTORY_TYPE_MISMATCH")
        identity = _identity(value, entity_type)
        grouped.setdefault(identity, []).append(value)

    return tuple(
        _compose(
            tenant_id=tenant_id,
            entity_type=entity_type,
            entity_identity=identity,
            history=tuple(grouped[identity]),
        )
        for identity in sorted(grouped)
    )


__all__ = [
    "VERSION",
    "LegalOperationsEntityReadModel",
    "LegalOperationsReadModelError",
    "get_entity_read_model",
    "list_entity_read_models",
]


# ARTIFACT: legal_operations_read_model.py
# VERSION: v1.0.0-L8-5-LEGAL-OPERATIONS-ENTITY-READ-MODEL
# AUTHORITY BOUNDARY: deterministic current-plus-history read-model composition only
# TENANT POSTURE: exact tenant/type/identity P2 histories; foreign evidence is never queried
# FAIL-CLOSED POSTURE: unsupported/absent/corrupt/divergent/ambiguous histories reject without fallback
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively
# END OF WILSY OS SOVEREIGN ARTIFACT
