"""Deterministic current-snapshot projection for Legal Operations history.

TITLE: Wilsy OS Legal Operations Current Snapshot Projection
VERSION: v1.0.0-L8-0-LEGAL-OPERATIONS-CURRENT-PROJECTION
AUTHORITY: Wilsy OS Core Governance
EPITOME: Resolve one deterministic current Legal Operations snapshot from
         immutable P1 history while rejecting type, tenant, identity, static
         payload, lineage, and immutable-fact divergence.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tools/eos/legal_operations/domain/legal_operations_current_projection.py
COLLABORATION / OWNERSHIP: P1 remains lifecycle authority and P2 remains
                            persistence/hydration authority. This module owns
                            current-history projection semantics only; callers
                            provide already-hydrated P1 snapshots.
CERTIFICATION / UPDATE DATE: 2026-09-23
CHANGELOG: 2026-09-23 v1.0.0-L8-0-LEGAL-OPERATIONS-CURRENT-PROJECTION
           establishes deterministic full-lineage current selection for
           stateful P1 entities and exact-single-truth resolution for immutable
           P1 entities without introducing a persistence current pointer.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2.
SECURITY / PRIVACY POSTURE: Pure in-memory projection over canonical P1 values;
                             no network, database, provider, credential, secret,
                             browser, device, or PII expansion.
TENANT BOUNDARY: Every candidate snapshot must share one explicit non-global
                 tenant already validated by P1; cross-tenant input rejects.
AUTHORITY BOUNDARY: Projection only. This module cannot create, mutate,
                    authorize, persist, accept, receive, allocate, attempt,
                    serve, return, bill, invoice, pay, execute, or settle.
FINANCIAL AUTHORITY BOUNDARY: Kennel EOS exclusively owns financial execution
                              and settlement; projection never creates
                              financial truth.
TRANSACTION BOUNDARY: None. The function performs no persistence and owns no
                      session, transaction, retry, commit, or abort lifecycle.
FAIL-CLOSED DECLARATION: Empty input, unsupported type, type/scope/identity
                         mismatch, static divergence, forked history, and
                         divergent immutable facts reject through stable codes.
"""
from __future__ import annotations

from collections.abc import Iterable
from typing import Any, Final, NoReturn, TypeAlias, cast

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


VERSION: Final[str] = "v1.0.0-L8-0-LEGAL-OPERATIONS-CURRENT-PROJECTION"

LifecycleValue: TypeAlias = (
    LegalInstruction
    | CaseMatter
    | ProcessDocument
    | District
    | SheriffOffice
    | Deputy
    | DocumentCustodyEvent
    | ServiceAttempt
    | ServiceExecution
    | ReturnOfService
)

_SUPPORTED_TYPES: Final[tuple[type[Any], ...]] = (
    LegalInstruction,
    CaseMatter,
    ProcessDocument,
    District,
    SheriffOffice,
    Deputy,
    DocumentCustodyEvent,
    ServiceAttempt,
    ServiceExecution,
    ReturnOfService,
)

_STATEFUL_TYPES: Final[tuple[type[Any], ...]] = (
    LegalInstruction,
    CaseMatter,
    ProcessDocument,
    ServiceAttempt,
)

_ENTITY_ID_FIELDS: Final[dict[type[Any], str]] = {
    LegalInstruction: "instruction_id",
    CaseMatter: "case_matter_id",
    ProcessDocument: "document_id",
    District: "district_id",
    SheriffOffice: "sheriff_office_id",
    Deputy: "deputy_id",
    DocumentCustodyEvent: "custody_event_id",
    ServiceAttempt: "attempt_id",
    ServiceExecution: "service_execution_id",
    ReturnOfService: "return_id",
}


class LegalOperationsCurrentProjectionError(RuntimeError):
    """Stable fail-closed current-projection error.

    The code describes projection ambiguity only. The exception carries no
    lifecycle mutation, persistence, authorization, billing, invoice, payment,
    execution, settlement, session, or transaction authority.
    """

    def __init__(self, code: str) -> None:
        self.code = code
        super().__init__(code)


def _fail(code: str) -> NoReturn:
    """Raise one stable projection failure without inventing a fallback."""
    raise LegalOperationsCurrentProjectionError(code)


def _entity_identity(value: LifecycleValue) -> str:
    """Return the canonical P1 entity identity for one supported snapshot."""
    field = _ENTITY_ID_FIELDS.get(type(value))
    if field is None:
        _fail("L8_0_ENTITY_TYPE_UNSUPPORTED")
    identity = getattr(value, field, None)
    if not isinstance(identity, str) or not identity:
        _fail("L8_0_ENTITY_IDENTITY_INVALID")
    return identity


def _static_payload(value: LifecycleValue) -> dict[str, object]:
    """Return fields that must remain invariant across one stateful lineage."""
    payload = value.to_dict()
    if not isinstance(payload, dict):
        _fail("L8_0_PAYLOAD_INVALID")
    result = dict(payload)
    result.pop("state", None)
    result.pop("transition_history", None)
    return cast(dict[str, object], result)


def _history(value: LifecycleValue) -> tuple[Any, ...]:
    """Return the complete validated P1 transition history for a stateful value."""
    history = getattr(value, "transition_history", None)
    if not isinstance(history, tuple):
        _fail("L8_0_HISTORY_INVALID")
    return history


def _deduplicate_exact(values: tuple[LifecycleValue, ...]) -> tuple[LifecycleValue, ...]:
    """Collapse exact repeated inputs without collapsing divergent evidence."""
    seen: set[str] = set()
    result: list[LifecycleValue] = []
    for value in values:
        fingerprint = getattr(value, "fingerprint", None)
        if not isinstance(fingerprint, str) or len(fingerprint) != 128:
            _fail("L8_0_FINGERPRINT_INVALID")
        if fingerprint in seen:
            continue
        seen.add(fingerprint)
        result.append(value)
    return tuple(result)


def resolve_current_lifecycle_snapshot(
    values: Iterable[LifecycleValue],
    *,
    expected_type: type[Any] | None = None,
) -> LifecycleValue:
    """Resolve one deterministic current snapshot from complete immutable history.

    Stateful entities are accepted only when every candidate has the same
    static payload and every shorter transition history is an exact prefix of
    one unique longest lineage. A fork at any depth fails closed.

    Immutable entities have no transition lineage; more than one distinct
    fingerprint for the same tenant/type/entity identity is therefore
    ambiguous and rejects.

    The caller is responsible for hydrating all durable snapshots belonging to
    the exact tenant/type/entity identity. This function performs no database
    access, persistence, authorization, or transaction lifecycle operation.
    """

    snapshots = tuple(values)
    if not snapshots:
        _fail("L8_0_HISTORY_REQUIRED")

    for value in snapshots:
        if type(value) not in _SUPPORTED_TYPES:
            _fail("L8_0_ENTITY_TYPE_UNSUPPORTED")

    snapshots = _deduplicate_exact(cast(tuple[LifecycleValue, ...], snapshots))
    first = snapshots[0]
    concrete_type = type(first)

    if expected_type is not None and concrete_type is not expected_type:
        _fail("L8_0_EXPECTED_TYPE_MISMATCH")

    tenant_id = first.tenant_id
    entity_identity = _entity_identity(first)

    for value in snapshots:
        if type(value) is not concrete_type:
            _fail("L8_0_ENTITY_TYPE_MISMATCH")
        if value.tenant_id != tenant_id:
            _fail("L8_0_TENANT_MISMATCH")
        if _entity_identity(value) != entity_identity:
            _fail("L8_0_ENTITY_IDENTITY_MISMATCH")

    if concrete_type not in _STATEFUL_TYPES:
        if len(snapshots) != 1:
            _fail("L8_0_IMMUTABLE_FACT_DIVERGENCE")
        return first

    canonical_static = _static_payload(first)
    histories: list[tuple[LifecycleValue, tuple[Any, ...]]] = []
    for value in snapshots:
        if _static_payload(value) != canonical_static:
            _fail("L8_0_STATIC_PAYLOAD_DIVERGENCE")
        histories.append((value, _history(value)))

    maximum_depth = max(len(history) for _, history in histories)
    heads = tuple(value for value, history in histories if len(history) == maximum_depth)

    if len(heads) != 1:
        _fail("L8_0_CURRENT_SNAPSHOT_AMBIGUOUS")

    current = heads[0]
    current_history = _history(current)

    for value, history in histories:
        if current_history[: len(history)] != history:
            _fail("L8_0_HISTORY_DIVERGENCE")

    return current


__all__ = [
    "VERSION",
    "LifecycleValue",
    "LegalOperationsCurrentProjectionError",
    "resolve_current_lifecycle_snapshot",
]


# ARTIFACT: legal_operations_current_projection.py
# VERSION: v1.0.0-L8-0-LEGAL-OPERATIONS-CURRENT-PROJECTION
# AUTHORITY BOUNDARY: deterministic current-history projection only; no mutation
# TENANT POSTURE: every candidate must share one exact P1-validated tenant
# FAIL-CLOSED POSTURE: ambiguous, forked, mismatched, or divergent evidence rejects
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively
# END OF WILSY OS SOVEREIGN ARTIFACT
