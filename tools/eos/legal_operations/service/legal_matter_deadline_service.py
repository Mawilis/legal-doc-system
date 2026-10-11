"""Wilsy OS legal-matter deadline service orchestration.

TITLE: Wilsy OS Legal Matter Deadline Service
VERSION: v1.0.0-LEGAL-OPS-COMPLETION-D3A-DEADLINE-SERVICE
AUTHORITY: Wilsy OS Core Governance / Python EOS Legal Operations
EPITOME: Correlate one explicit deadline command to exact current tenant matter
         truth, construct certified D1 evidence, and persist through D2.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system-legal-deadline-engine/tools/eos/legal_operations/service/legal_matter_deadline_service.py
COLLABORATION / OWNERSHIP: Lifecycle registry/current projection own matter truth;
                            D1 owns deadline semantics; D2 owns persistence;
                            D3A owns only their fail-closed composition.
CERTIFICATION / UPDATE DATE: 2026-10-11
CHANGELOG: 2026-10-11 v1.0.0-LEGAL-OPS-COMPLETION-D3A-DEADLINE-SERVICE establishes current-matter correlation, exact session propagation, stable error translation, D1 construction, D2 replay, bounded reads and pure temporal observation.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2; ISO 27001.
SECURITY / PRIVACY POSTURE: Opaque identifiers and evidence only; foreign matter is bounded absence.
TENANT BOUNDARY: Matter and deadline operations use one exact caller tenant predicate.
AUTHORITY BOUNDARY: Orchestration only; no IAM, legal-period, filing, service,
                    court, representation, notification, calendar, or AI authority.
TRANSACTION BOUNDARY: Caller owns active session/transaction, commit, abort,
                      retry and unknown-commit handling; same session reaches all dependencies.
FINANCIAL AUTHORITY BOUNDARY: None; Kennel EOS remains exclusive.
FAIL-CLOSED DECLARATION: Missing/corrupt matter, invalid deadline, transaction,
                         conflict, corruption or persistence failure rejects.
"""
from __future__ import annotations

from datetime import datetime
from typing import Any, NoReturn

from tools.eos.legal_operations.domain.legal_matter_deadline import LegalMatterDeadline, LegalMatterDeadlineError, LegalMatterDeadlineTemporalPosture
from tools.eos.legal_operations.domain.legal_operations_current_projection import LegalOperationsCurrentProjectionError, resolve_current_lifecycle_snapshot
from tools.eos.legal_operations.domain.legal_operations_lifecycle import CaseMatter, CaseMatterState
from tools.eos.legal_operations.registry.legal_operations_lifecycle_registry import LegalOperationsLifecycleRegistry, LegalOperationsLifecycleRegistryError
from tools.eos.legal_operations.registry.legal_matter_deadline_registry import LegalMatterDeadlineRegistry, LegalMatterDeadlineRegistryConflictError, LegalMatterDeadlineRegistryNotFoundError, LegalMatterDeadlineRegistryPersistedRecordInvalidError, LegalMatterDeadlineRegistryPersistenceUnavailableError, LegalMatterDeadlineRegistryRetryRequiredError, LegalMatterDeadlineRegistryTransactionRequiredError

VERSION = "v1.0.0-LEGAL-OPS-COMPLETION-D3A-DEADLINE-SERVICE"


class LegalMatterDeadlineServiceError(RuntimeError):
    """Stable service error without tenant, evidence, or persistence leakage."""
    def __init__(self, code: str) -> None:
        self.code = code
        super().__init__(code)


def _fail(code: str, cause: BaseException | None = None) -> NoReturn:
    error = LegalMatterDeadlineServiceError(code)
    if cause is None: raise error
    raise error from cause


def _transaction(session: Any) -> Any:
    marker = getattr(session, "in_transaction", None) if session is not None else None
    try: active = marker() if callable(marker) else marker
    except (AttributeError, TypeError): active = False
    if active is not True: _fail("DEADLINE_TRANSACTION_REQUIRED")
    return session


def _matter(tenant_id: str, case_matter_id: str, collection: Any, session: Any) -> CaseMatter:
    try:
        history = LegalOperationsLifecycleRegistry.get_entity_history(tenant_id, "CaseMatter", case_matter_id, collection, session=session)
    except LegalOperationsLifecycleRegistryError as error:
        _fail("DEADLINE_MATTER_PERSISTENCE_FAILURE", error)
    if not history: _fail("DEADLINE_MATTER_NOT_AVAILABLE")
    try: current = resolve_current_lifecycle_snapshot(history, expected_type=CaseMatter)
    except LegalOperationsCurrentProjectionError as error:
        _fail("DEADLINE_MATTER_CORRUPT", error)
    if type(current) is not CaseMatter or current.state is not CaseMatterState.OPEN: _fail("DEADLINE_MATTER_NOT_AVAILABLE")
    if current.tenant_id != tenant_id or current.case_matter_id != case_matter_id: _fail("DEADLINE_MATTER_NOT_AVAILABLE")
    return current


def record_legal_matter_deadline(*, tenant_id: str, case_matter_id: str, deadline_id: str, deadline_kind: object, title: str, due_at: datetime, source_type: object, source_reference: str, source_evidence_fingerprint: str, jurisdiction_reference: str, created_at: datetime, matter_collection: Any, deadline_collection: Any, session: Any, supersedes_deadline_id: str | None = None, status: object = "ACTIVE") -> LegalMatterDeadline:
    """Record one explicitly evidenced deadline after exact current-matter proof.

    Every due date and provenance value is supplied explicitly; this service
    performs no legal-period, business-day, holiday, cutoff, AI, filing, service,
    payment or settlement inference. Supersession never mutates prior truth.
    """
    tx = _transaction(session)
    _matter(tenant_id, case_matter_id, matter_collection, tx)
    try:
        value = LegalMatterDeadline(tenant_id=tenant_id, case_matter_id=case_matter_id, deadline_id=deadline_id, deadline_kind=deadline_kind, title=title, due_at=due_at, source_type=source_type, source_reference=source_reference, source_evidence_fingerprint=source_evidence_fingerprint, jurisdiction_reference=jurisdiction_reference, created_at=created_at, supersedes_deadline_id=supersedes_deadline_id, status=status)  # type: ignore[arg-type]
    except LegalMatterDeadlineError as error:
        _fail("DEADLINE_INVALID", error)
    try: return LegalMatterDeadlineRegistry.persist_deadline(value, deadline_collection, session=tx)
    except LegalMatterDeadlineRegistryConflictError as error: _fail("DEADLINE_CONFLICT", error)
    except LegalMatterDeadlineRegistryPersistedRecordInvalidError as error: _fail("DEADLINE_CORRUPT", error)
    except LegalMatterDeadlineRegistryTransactionRequiredError as error: _fail("DEADLINE_TRANSACTION_REQUIRED", error)
    except (LegalMatterDeadlineRegistryPersistenceUnavailableError, LegalMatterDeadlineRegistryRetryRequiredError) as error: _fail("DEADLINE_PERSISTENCE_FAILURE", error)


def get_legal_matter_deadline(*, tenant_id: str, deadline_id: str, deadline_collection: Any, session: Any) -> LegalMatterDeadline:
    """Read one exact tenant deadline with bounded absence and stable errors."""
    tx = _transaction(session)
    try: return LegalMatterDeadlineRegistry.get_deadline(tenant_id, deadline_id, deadline_collection, session=tx)
    except LegalMatterDeadlineRegistryNotFoundError as error: _fail("DEADLINE_NOT_AVAILABLE", error)
    except LegalMatterDeadlineRegistryPersistedRecordInvalidError as error: _fail("DEADLINE_CORRUPT", error)
    except (LegalMatterDeadlineRegistryPersistenceUnavailableError, LegalMatterDeadlineRegistryRetryRequiredError) as error: _fail("DEADLINE_PERSISTENCE_FAILURE", error)


def list_legal_matter_deadlines(*, tenant_id: str, case_matter_id: str, deadline_collection: Any, session: Any) -> tuple[LegalMatterDeadline, ...]:
    """List exact tenant/matter deadlines without selecting current authority."""
    tx = _transaction(session)
    try: return LegalMatterDeadlineRegistry.list_matter_deadlines(tenant_id, case_matter_id, deadline_collection, session=tx)
    except LegalMatterDeadlineRegistryPersistedRecordInvalidError as error: _fail("DEADLINE_CORRUPT", error)
    except (LegalMatterDeadlineRegistryPersistenceUnavailableError, LegalMatterDeadlineRegistryRetryRequiredError) as error: _fail("DEADLINE_PERSISTENCE_FAILURE", error)


def observe_legal_matter_deadline(deadline: LegalMatterDeadline, *, at: datetime) -> LegalMatterDeadlineTemporalPosture:
    """Delegate pure explicit-time posture observation exclusively to D1."""
    if type(deadline) is not LegalMatterDeadline: _fail("DEADLINE_INVALID")
    try: return deadline.temporal_posture(at)
    except LegalMatterDeadlineError as error: _fail("DEADLINE_INVALID", error)


__all__ = ["VERSION", "LegalMatterDeadlineServiceError", "get_legal_matter_deadline", "list_legal_matter_deadlines", "observe_legal_matter_deadline", "record_legal_matter_deadline"]

# ARTIFACT: legal_matter_deadline_service.py
# VERSION: v1.0.0-LEGAL-OPS-COMPLETION-D3A-DEADLINE-SERVICE
# AUTHORITY BOUNDARY: current-matter correlation plus D1/D2 composition only; no IAM, legal-rule, overdue, AI, filing, service, court or financial authority
# TENANT POSTURE: exact tenant matter correlation and tenant-scoped deadline operations
# FAIL-CLOSED POSTURE: transaction, matter, validation, conflict, corruption and persistence failures reject
# FINANCIAL EXECUTION AUTHORITY: none; Kennel EOS remains exclusive
# END OF WILSY OS SOVEREIGN ARTIFACT
