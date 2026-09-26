"""TITLE: WILSY OS Matter Acceptance Instrument Approval Issuance Orchestrator.
VERSION: v1.0.0-L9A4-P2B3-MATTER-ACCEPTANCE-INSTRUMENT-APPROVAL-ISSUANCE
AUTHORITY: Wilsy OS Core Governance / Python EOS Legal Operations.
EPITOME: Compose one immutable firm-side approval decision only after an
         authenticated partner/attorney is authorized and the exact OPEN
         CaseMatter, effective instrument version, and ACTIVE lifecycle are
         re-read in the same caller-owned transaction.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tools/eos/legal_operations/orchestration/legal_client_matter_acceptance_instrument_approval_orchestrator.py
COLLABORATION / OWNERSHIP: CaseMatter, instrument and lifecycle registries
                            own source truth; TenantAuthorizationDecisionEvidence
                            owns durable IAM evidence; the approval domain and
                            registry own immutable decision evidence. This
                            module composes those authorities only.
CERTIFICATION / UPDATE DATE: 2026-09-26.
CHANGELOG: v1.0.0-L9A4-P2B3 establishes exact authenticated firm-side
           matter-acceptance-instrument approval issuance for APPROVED and
           REJECTED decisions, latest-effective ACTIVE-version gating,
           subject-bound authorization evidence, exact replay and divergent
           collision rejection. It creates no client acceptance, engagement,
           representation, Court, financial or settlement authority.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2; ISO 27001.
SECURITY / PRIVACY POSTURE: Only opaque identifiers, bounded evidence
                             references and SHA3-512 fingerprints are admitted;
                             no raw document body, PII, credentials or tokens.
TENANT BOUNDARY: Tenant and principal are derived from one active
                 SovereignIdentity; every source, authorization and approval
                 operation is exact tenant/matter/instrument scoped.
AUTHORITY BOUNDARY: Authorized immutable approval evidence only. Approval is
                    not currentness, visibility, client acceptance, engagement,
                    representation, Court authority or legal sufficiency.
FINANCIAL AUTHORITY BOUNDARY: None; Kennel EOS remains exclusive.
TRANSACTION BOUNDARY: Caller supplies and owns the active session, commit,
                      abort, retry and unknown-commit lifecycle. This module
                      never starts, commits, aborts or retries a transaction.
FAIL-CLOSED DECLARATION: Missing transaction, inactive identity, stale or
                         terminal lifecycle, non-latest instrument, denied or
                         divergent authorization, replay collision and any
                         persistence uncertainty reject without fallback.
"""
from __future__ import annotations

import hashlib
import json
from typing import Any, Final, NoReturn

from tools.eos.auth.identity import SovereignIdentity
from tools.eos.auth.principal_status import PrincipalStatus
from tools.eos.auth.tenant_authorization_decision_evidence_registry import (
    TenantAuthorizationDecisionEvidenceAuthorizationDeniedError,
    TenantAuthorizationDecisionEvidenceConflictError,
    TenantAuthorizationDecisionEvidencePersistenceError,
    TenantAuthorizationDecisionEvidenceRegistry,
    TenantAuthorizationDecisionEvidenceRegistryError,
    TenantAuthorizationDecisionEvidenceTransactionRequiredError,
)
from tools.eos.legal_operations.domain.legal_client_matter_acceptance_instrument_approval import (
    LegalClientMatterAcceptanceInstrumentApproval,
    LegalClientMatterAcceptanceInstrumentApprovalError,
    LegalClientMatterAcceptanceInstrumentApprovalDecision,
    record_legal_client_matter_acceptance_instrument_approval,
)
from tools.eos.legal_operations.domain.legal_client_matter_acceptance_instrument_lifecycle import (
    LegalClientMatterAcceptanceInstrumentLifecycleStatus,
)
from tools.eos.legal_operations.registry import (
    legal_client_matter_acceptance_instrument_approval_registry as approval_registry,
    legal_client_matter_acceptance_instrument_lifecycle_registry as lifecycle_registry,
    legal_client_matter_acceptance_instrument_registry as instrument_registry,
    legal_operations_lifecycle_registry as matter_registry,
)
from tools.eos.legal_operations.domain.legal_operations_current_projection import (
    resolve_current_lifecycle_snapshot,
)
from tools.eos.legal_operations.domain.legal_operations_lifecycle import (
    CaseMatter,
    CaseMatterState,
)


VERSION: Final[str] = (
    "v1.0.0-L9A4-P2B3-MATTER-ACCEPTANCE-INSTRUMENT-APPROVAL-ISSUANCE"
)
PERMISSION: Final[str] = "legal_operations:matter_acceptance_instrument_approval:write"
OPERATION: Final[str] = "legal_matter_acceptance_instrument_approval_write"
SUBJECT_PREFIX: Final[str] = "legal-matter-acceptance-instrument-approval"


class LegalClientMatterAcceptanceInstrumentApprovalOrchestrationError(RuntimeError):
    """Stable fail-closed orchestration error without supplied-value leakage."""

    def __init__(self, code: str) -> None:
        self.code = code
        super().__init__(code)


class LegalClientMatterAcceptanceInstrumentApprovalOrchestrationRetryRequiredError(
    LegalClientMatterAcceptanceInstrumentApprovalOrchestrationError
):
    """Caller must abort and restart the complete transaction from fresh state."""


def _fail(code: str, cause: BaseException | None = None) -> NoReturn:
    """Raise one bounded code while retaining technical cause internally."""
    error = LegalClientMatterAcceptanceInstrumentApprovalOrchestrationError(code)
    if cause is None:
        raise error
    raise error from cause


def _retry(code: str, cause: BaseException) -> NoReturn:
    """Require whole-transaction retry for a persistence race."""
    raise LegalClientMatterAcceptanceInstrumentApprovalOrchestrationRetryRequiredError(code) from cause


def _text(name: str, value: object) -> str:
    """Require bounded opaque text without trimming or coercion."""
    if not isinstance(value, str) or not value or value != value.strip():
        _fail(f"L9A4_P2B3_{name.upper()}_INVALID")
    return value


def _active_session(session: Any) -> Any:
    """Require one already-active caller-owned transaction session."""
    if session is None:
        _fail("L9A4_P2B3_ACTIVE_TRANSACTION_REQUIRED")
    marker = getattr(session, "in_transaction", None)
    try:
        active = marker() if callable(marker) else marker
    except (AttributeError, TypeError):
        active = False
    if active is not True:
        _fail("L9A4_P2B3_ACTIVE_TRANSACTION_REQUIRED")
    return session


def _identity(identity: SovereignIdentity) -> tuple[str, str]:
    """Derive exact tenant and principal only from active authentication."""
    if not isinstance(identity, SovereignIdentity):
        _fail("L9A4_P2B3_IDENTITY_REQUIRED")
    if identity.status is not PrincipalStatus.ACTIVE:
        _fail("L9A4_P2B3_PRINCIPAL_INACTIVE")
    return _text("tenant_id", identity.tenant_id), _text("principal_id", identity.identity_id)


def _subject_reference(tenant: str, matter: str, instrument: str, version: str) -> str:
    """Derive an opaque, tenant-scoped authorization subject reference."""
    return f"{SUBJECT_PREFIX}:{tenant}:{matter}:{instrument}:{version}"


def _authorization_idempotency_key(approval_id: str, idempotency_key: str) -> str:
    """Namespace authorization replay independently from approval identity."""
    return f"{SUBJECT_PREFIX}:{approval_id}:{idempotency_key}"


def _subject_fingerprint(
    *,
    tenant: str,
    principal: str,
    matter: CaseMatter,
    instrument: Any,
    approval_id: str,
    decision: str,
    capacity: str,
    approval_reference: str,
    approval_fingerprint: str,
    idempotency_key: str,
) -> str:
    """Bind actor, exact source identities and approval intent deterministically."""
    payload = {
        "tenant_id": tenant,
        "principal_id": principal,
        "case_matter_id": matter.case_matter_id,
        "matter_fingerprint": matter.fingerprint,
        "instrument_id": instrument.instrument_id,
        "version": instrument.version,
        "instrument_fingerprint": instrument.fingerprint,
        "content_fingerprint": instrument.content_fingerprint,
        "approval_id": approval_id,
        "decision": decision,
        "approver_capacity_reference": capacity,
        "approval_evidence_reference": approval_reference,
        "approval_evidence_fingerprint": approval_fingerprint,
        "idempotency_key": idempotency_key,
    }
    return hashlib.sha3_512(
        json.dumps(payload, ensure_ascii=False, allow_nan=False, sort_keys=True, separators=(",", ":")).encode("utf-8")
    ).hexdigest()


def _current_case_matter(*, tenant: str, matter_id: str, collection: Any, session: Any) -> CaseMatter:
    """Read the complete exact CaseMatter lifecycle and require OPEN currentness."""
    try:
        history = matter_registry.LegalOperationsLifecycleRegistry.get_entity_history(
            tenant, "CaseMatter", matter_id, collection, session=session
        )
        value = resolve_current_lifecycle_snapshot(history, expected_type=CaseMatter)
    except Exception as error:
        _fail("L9A4_P2B3_CASE_MATTER_UNAVAILABLE", error)
    if not isinstance(value, CaseMatter):
        _fail("L9A4_P2B3_CASE_MATTER_TYPE_INVALID")
    if value.tenant_id != tenant or value.case_matter_id != matter_id:
        _fail("L9A4_P2B3_CASE_MATTER_SCOPE_MISMATCH")
    if value.state is not CaseMatterState.OPEN:
        _fail("L9A4_P2B3_CASE_MATTER_NOT_OPEN")
    return value


def issue_legal_client_matter_acceptance_instrument_approval(
    *,
    identity: SovereignIdentity,
    case_matter_id: str,
    instrument_id: str,
    version: str,
    approval_id: str,
    idempotency_key: str,
    decision: LegalClientMatterAcceptanceInstrumentApprovalDecision | str,
    approver_capacity_reference: str,
    approval_evidence_reference: str,
    approval_evidence_fingerprint: str,
    matter_lifecycle_collection: Any,
    instrument_collection: Any,
    instrument_lifecycle_collection: Any,
    approval_collection: Any,
    authorization_evidence_registry: TenantAuthorizationDecisionEvidenceRegistry,
    session: Any,
) -> LegalClientMatterAcceptanceInstrumentApproval:
    """Issue or exactly replay one authorized immutable instrument approval.

    Tenant and principal are server-derived from ``identity``. The caller may
    supply only the bounded subject/approval references and decision; matter,
    instrument, content, lifecycle and authorization fingerprints are derived
    from canonical persisted sources. Authorization evidence and approval use
    the exact active session. The caller owns commit, abort and retry.
    """
    tx = _active_session(session)
    tenant, principal = _identity(identity)
    matter_id = _text("case_matter_id", case_matter_id)
    instrument_identity = _text("instrument_id", instrument_id)
    version_identity = _text("version", version)
    approval_identity = _text("approval_id", approval_id)
    idempotency = _text("idempotency_key", idempotency_key)
    capacity = _text("approver_capacity_reference", approver_capacity_reference)
    evidence_reference = _text("approval_evidence_reference", approval_evidence_reference)
    evidence_fingerprint = _text("approval_evidence_fingerprint", approval_evidence_fingerprint)
    try:
        decision_value = LegalClientMatterAcceptanceInstrumentApprovalDecision(decision).value
    except (TypeError, ValueError) as error:
        _fail("L9A4_P2B3_DECISION_INVALID", error)
    if not isinstance(authorization_evidence_registry, TenantAuthorizationDecisionEvidenceRegistry):
        _fail("L9A4_P2B3_AUTHORIZATION_EVIDENCE_REGISTRY_REQUIRED")
    if any(value is None for value in (matter_lifecycle_collection, instrument_collection, instrument_lifecycle_collection, approval_collection)):
        _fail("L9A4_P2B3_COLLECTION_REQUIRED")

    matter = _current_case_matter(tenant=tenant, matter_id=matter_id, collection=matter_lifecycle_collection, session=tx)
    try:
        instrument = instrument_registry.get_instrument(
            tenant, matter.case_matter_id, instrument_identity, version_identity,
            instrument_collection, session=tx,
        )
    except instrument_registry.LegalClientMatterAcceptanceInstrumentRegistryNotFoundError as error:
        _fail("L9A4_P2B3_INSTRUMENT_NOT_FOUND", error)
    except instrument_registry.LegalClientMatterAcceptanceInstrumentRegistryRetryRequiredError as error:
        _retry("L9A4_P2B3_WHOLE_TRANSACTION_RETRY_REQUIRED", error)
    except instrument_registry.LegalClientMatterAcceptanceInstrumentRegistryError as error:
        _fail("L9A4_P2B3_INSTRUMENT_UNAVAILABLE", error)
    if instrument.tenant_id != tenant or instrument.case_matter_id != matter.case_matter_id:
        _fail("L9A4_P2B3_INSTRUMENT_SCOPE_MISMATCH")

    try:
        lifecycle = lifecycle_registry.get_current_lifecycle(
            tenant, matter.case_matter_id, instrument.instrument_id, instrument.version,
            instrument_lifecycle_collection, session=tx,
        )
    except lifecycle_registry.LegalClientMatterAcceptanceInstrumentLifecycleRegistryError as error:
        _fail("L9A4_P2B3_LIFECYCLE_UNAVAILABLE", error)
    if lifecycle is None or lifecycle.status is not LegalClientMatterAcceptanceInstrumentLifecycleStatus.ACTIVE:
        _fail("L9A4_P2B3_INSTRUMENT_NOT_ACTIVE")
    if lifecycle.instrument_fingerprint != instrument.fingerprint:
        _fail("L9A4_P2B3_LIFECYCLE_INSTRUMENT_MISMATCH")

    subject = _subject_reference(tenant, matter.case_matter_id, instrument.instrument_id, instrument.version)
    subject_fingerprint = _subject_fingerprint(
        tenant=tenant, principal=principal, matter=matter, instrument=instrument,
        approval_id=approval_identity, decision=decision_value, capacity=capacity,
        approval_reference=evidence_reference, approval_fingerprint=evidence_fingerprint,
        idempotency_key=idempotency,
    )
    try:
        authorization = authorization_evidence_registry.issue(
            tenant_id=tenant, principal_id=principal, operation=OPERATION,
            permission=PERMISSION, subject_reference=subject,
            subject_evidence_fingerprint=subject_fingerprint,
            idempotency_key=_authorization_idempotency_key(approval_identity, idempotency),
            session=tx,
        )
    except TenantAuthorizationDecisionEvidenceAuthorizationDeniedError as error:
        _fail("L9A4_P2B3_APPROVER_AUTHORIZATION_REQUIRED", error)
    except TenantAuthorizationDecisionEvidenceTransactionRequiredError as error:
        _fail("L9A4_P2B3_ACTIVE_TRANSACTION_REQUIRED", error)
    except TenantAuthorizationDecisionEvidenceConflictError as error:
        _fail("L9A4_P2B3_AUTHORIZATION_REPLAY_CONFLICT", error)
    except (TenantAuthorizationDecisionEvidencePersistenceError, TenantAuthorizationDecisionEvidenceRegistryError) as error:
        _fail("L9A4_P2B3_AUTHORIZATION_EVIDENCE_UNAVAILABLE", error)
    if (
        authorization.tenant_id != tenant
        or authorization.principal_id != principal
        or authorization.operation != OPERATION
        or authorization.permission != PERMISSION
        or authorization.subject_reference != subject
        or authorization.subject_evidence_fingerprint != subject_fingerprint
    ):
        _fail("L9A4_P2B3_AUTHORIZATION_CORRELATION_INVALID")

    try:
        latest = instrument_registry.get_latest_effective_version(
            tenant, matter.case_matter_id, instrument.instrument_id,
            authorization.authorized_at, instrument_collection, session=tx,
        )
    except instrument_registry.LegalClientMatterAcceptanceInstrumentRegistryError as error:
        _fail("L9A4_P2B3_LATEST_INSTRUMENT_UNAVAILABLE", error)
    if latest is None or latest.fingerprint != instrument.fingerprint or latest.version != instrument.version:
        _fail("L9A4_P2B3_INSTRUMENT_VERSION_NOT_LATEST")

    try:
        approval = record_legal_client_matter_acceptance_instrument_approval(
            case_matter=matter, instrument=instrument, approval_id=approval_identity,
            decision=decision_value, approver_principal_id=principal,
            approver_capacity_reference=capacity,
            authorization_evidence_reference=authorization.authorization_evidence_reference,
            authorization_evidence_fingerprint=authorization.authorization_evidence_fingerprint,
            approval_evidence_reference=evidence_reference,
            approval_evidence_fingerprint=evidence_fingerprint,
            occurred_at=authorization.authorized_at,
            effective_from=authorization.authorized_at,
            idempotency_key=idempotency,
        )
    except LegalClientMatterAcceptanceInstrumentApprovalError as error:
        _fail("L9A4_P2B3_APPROVAL_INVALID", error)
    try:
        persisted = approval_registry.persist_approval(approval, approval_collection, session=tx)
    except approval_registry.LegalClientMatterAcceptanceInstrumentApprovalRegistryRetryRequiredError as error:
        _retry("L9A4_P2B3_WHOLE_TRANSACTION_RETRY_REQUIRED", error)
    except approval_registry.LegalClientMatterAcceptanceInstrumentApprovalRegistryConflictError as error:
        _fail("L9A4_P2B3_APPROVAL_REPLAY_CONFLICT", error)
    except approval_registry.LegalClientMatterAcceptanceInstrumentApprovalRegistryError as error:
        _fail("L9A4_P2B3_APPROVAL_PERSISTENCE_UNAVAILABLE", error)
    if persisted.to_dict() != approval.to_dict() or persisted.approver_principal_id != principal:
        _fail("L9A4_P2B3_POST_WRITE_CORRELATION_INVALID")
    return persisted


__all__ = [
    "OPERATION", "PERMISSION", "SUBJECT_PREFIX", "VERSION",
    "LegalClientMatterAcceptanceInstrumentApprovalOrchestrationError",
    "LegalClientMatterAcceptanceInstrumentApprovalOrchestrationRetryRequiredError",
    "issue_legal_client_matter_acceptance_instrument_approval",
]


# ARTIFACT: legal_client_matter_acceptance_instrument_approval_orchestrator.py
# VERSION: v1.0.0-L9A4-P2B3-MATTER-ACCEPTANCE-INSTRUMENT-APPROVAL-ISSUANCE
# AUTHORITY BOUNDARY: authorized immutable firm-side instrument approval evidence only
# TENANT POSTURE: exact authenticated tenant/matter/instrument/lifecycle scope
# FAIL-CLOSED POSTURE: stale, terminal, denied, divergent and persistence-uncertain requests reject
# FINANCIAL EXECUTION AUTHORITY: none; Kennel EOS remains exclusive
# END OF WILSY OS SOVEREIGN ARTIFACT
