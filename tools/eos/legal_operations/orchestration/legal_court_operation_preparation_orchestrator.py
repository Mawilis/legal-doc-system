"""WILSY OS Court Operation Preparation orchestration boundary.

TITLE: WILSY OS Legal Court Operation Preparation Orchestrator
VERSION: v1.0.0-L9C12-P2-COURT-OPERATION-PREPARATION-ORCHESTRATOR
AUTHORITY: Wilsy OS Core Governance / Python EOS Legal Operations
EPITOME: Freshly revalidate certified P24 Representation, P21A authority,
         P22 decision, Engagement, Mandate and live representative IAM before
         constructing one immutable internal Court filing-preparation snapshot.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tools/eos/legal_operations/orchestration/legal_court_operation_preparation_orchestrator.py
COLLABORATION / OWNERSHIP: P24, P21A, P22, Engagement and Mandate remain the
                            canonical upstream authorities. IAM repositories
                            remain authoritative for live identity facts. P1
                            registry owns only immutable preparation persistence.
CERTIFICATION / UPDATE DATE: 2026-09-28
CHANGELOG: v1.0.0-L9C12-P2 establishes caller-transaction Court preparation
           composition with exact upstream lineage, live IAM revalidation,
           bounded Court scope derivation and one P1 write. No external Court,
           authorization-evidence, HTTP/UI/Node or financial authority exists.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2; ISO 27001.
SECURITY / PRIVACY POSTURE: Caller claims never supply authoritative
                             fingerprints, role, principal or currentness;
                             those facts are re-read from certified truth.
TENANT BOUNDARY: Every upstream read and the P1 write use exact tenant,
                 matter lineage and the caller's same active session.
AUTHORITY BOUNDARY: Internal preparation only; no filing, acceptance,
                    issuance, service, hearing, judicial order, admission,
                    attorney-of-record, Court Online or financial authority.
TRANSACTION BOUNDARY: Caller owns an active transaction. This orchestrator
                      never starts, commits, aborts or retries one.
FAIL-CLOSED DECLARATION: Missing, stale, future, ambiguous, corrupt,
                         mismatched or widened authority rejects.
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any, Final, NoReturn

from tools.eos.auth.principal_authority import PrincipalAuthority
from tools.eos.auth.principal_status import PrincipalStatus
from tools.eos.auth.role_assignment import RoleAssignmentAuthority, RoleAssignmentStatus
from tools.eos.auth.tenant_membership import TenantMembershipAuthority, TenantMembershipStatus
from tools.eos.legal_operations.domain.legal_client_matter_engagement import LegalClientMatterEngagement
from tools.eos.legal_operations.domain.legal_client_matter_final_representation import LegalClientMatterFinalRepresentation
from tools.eos.legal_operations.domain.legal_client_matter_representation_authority_currentness import (
    LegalClientMatterRepresentationAuthorityCurrentness,
    LegalClientMatterRepresentationAuthorityCurrentnessState,
)
from tools.eos.legal_operations.domain.legal_client_matter_representation_firm_decision_currentness import (
    LegalClientMatterRepresentationFirmDecisionCurrentness,
    LegalClientMatterRepresentationFirmDecisionCurrentnessState,
)
from tools.eos.legal_operations.registry import legal_client_matter_engagement_registry as engagement_registry
from tools.eos.legal_operations.registry import legal_client_matter_final_representation_registry as final_representation_registry
from tools.eos.legal_operations.registry import legal_client_matter_mandate_registry as mandate_registry
from tools.eos.legal_operations.registry import legal_court_operation_preparation_registry as preparation_registry
from tools.eos.legal_operations.domain.legal_court_operation_preparation import (
    LegalCourtOperationPreparation,
    LegalCourtOperationPreparationState,
    LegalCourtOperationType,
)


VERSION: Final[str] = "v1.0.0-L9C12-P2-COURT-OPERATION-PREPARATION-ORCHESTRATOR"
COURT_SCOPE_DERIVATION_MODEL: Final[str] = (
    "COURT_FILING_PREPARATION requires LITIGATION_PREPARATION in P24/P21A/P22 "
    "and COURT_FILING_PREPARATION in Mandate; caller scope may not widen"
)
ELIGIBLE_REPRESENTATIVE_ROLES: Final[frozenset[str]] = frozenset({"LEGAL_ATTORNEY", "LEGAL_PARTNER"})
UTC = timezone.utc


class LegalCourtOperationPreparationOrchestrationError(RuntimeError):
    """Stable, non-sensitive fail-closed P2 orchestration error."""

    def __init__(self, code: str) -> None:
        self.code = code
        super().__init__(code)


def _fail(code: str, cause: BaseException | None = None) -> NoReturn:
    error = LegalCourtOperationPreparationOrchestrationError(code)
    if cause is None:
        raise error
    raise error from cause


def _text(name: str, value: object) -> str:
    if not isinstance(value, str) or not value or value != value.strip():
        _fail(f"L9C12_P2_{name.upper()}_INVALID")
    return value


def _fingerprint(name: str, value: object) -> str:
    value = _text(name, value)
    if len(value) != 128 or any(char not in "0123456789abcdef" for char in value):
        _fail(f"L9C12_P2_{name.upper()}_INVALID")
    return value


def _timestamp(name: str, value: object) -> datetime:
    if not isinstance(value, datetime) or value.tzinfo is None or value.utcoffset() is None:
        _fail(f"L9C12_P2_{name.upper()}_INVALID")
    return value.astimezone(UTC)


def _references(name: str, value: object) -> tuple[str, ...]:
    if isinstance(value, str) or not isinstance(value, (tuple, list, set, frozenset)) or not value:
        _fail(f"L9C12_P2_{name.upper()}_INVALID")
    result = tuple(_text(name, item) for item in value)
    if len(result) != len(set(result)):
        _fail(f"L9C12_P2_{name.upper()}_DUPLICATE")
    return tuple(sorted(result))


def _scope(value: object, name: str) -> tuple[str, ...]:
    return _references(name, value)


def _active_transaction(session: Any) -> Any:
    if session is None:
        _fail("L9C12_P2_ACTIVE_TRANSACTION_REQUIRED")
    marker = getattr(session, "in_transaction", None)
    try:
        active = marker() if callable(marker) else marker
    except Exception as error:
        _fail("L9C12_P2_ACTIVE_TRANSACTION_REQUIRED", error)
    if active is not True:
        _fail("L9C12_P2_ACTIVE_TRANSACTION_REQUIRED")
    return session


def _state(value: object) -> str:
    rendered = getattr(value, "value", value)
    return rendered if isinstance(rendered, str) else "INVALID"


def _resolve(repository: Any, *args: object, collection: Any, session: Any, code: str) -> object:
    try:
        return repository.resolve(*args, collection=collection, session=session)
    except TypeError:
        try:
            return repository.resolve(*args, collection, session=session)
        except Exception as error:
            _fail(code, error)
    except Exception as error:
        _fail(code, error)


@dataclass(frozen=True, slots=True)
class LegalCourtOperationPreparationRequest:
    """Minimal caller intent; authoritative upstream facts are deliberately absent."""

    tenant_id: str
    case_matter_id: str
    matter_fingerprint: str
    final_representation_id: str
    operation_type: LegalCourtOperationType | str
    target_court_reference: str
    target_jurisdiction_reference: str
    document_evidence_lineage: tuple[str, ...] | list[str]
    requested_scope_capabilities: tuple[str, ...] | list[str]
    preparation_state: LegalCourtOperationPreparationState | str
    source_evidence_reference: str
    source_evidence_fingerprint: str
    provenance_reference: str
    prepared_at: datetime
    occurred_at: datetime
    evaluated_at: datetime
    idempotency_key: str

    def __post_init__(self) -> None:
        """Validate bounded intent, chronology and preparation-only scope."""
        _text("tenant_id", self.tenant_id)
        _text("case_matter_id", self.case_matter_id)
        _fingerprint("matter_fingerprint", self.matter_fingerprint)
        _text("final_representation_id", self.final_representation_id)
        operation = getattr(self.operation_type, "value", self.operation_type)
        if operation != LegalCourtOperationType.COURT_FILING_PREPARATION.value:
            _fail("L9C12_P2_OPERATION_TYPE_FORBIDDEN")
        state = getattr(self.preparation_state, "value", self.preparation_state)
        try:
            LegalCourtOperationPreparationState(state)
        except (TypeError, ValueError) as error:
            _fail("L9C12_P2_PREPARATION_STATE_INVALID", error)
        _text("target_court_reference", self.target_court_reference)
        _text("target_jurisdiction_reference", self.target_jurisdiction_reference)
        _references("document_evidence_lineage", self.document_evidence_lineage)
        scope = _scope(self.requested_scope_capabilities, "requested_scope_capabilities")
        if scope != (LegalCourtOperationType.COURT_FILING_PREPARATION.value,):
            _fail("L9C12_P2_SCOPE_FORBIDDEN")
        _text("source_evidence_reference", self.source_evidence_reference)
        _fingerprint("source_evidence_fingerprint", self.source_evidence_fingerprint)
        _text("provenance_reference", self.provenance_reference)
        prepared = _timestamp("prepared_at", self.prepared_at)
        occurred = _timestamp("occurred_at", self.occurred_at)
        evaluated = _timestamp("evaluated_at", self.evaluated_at)
        _text("idempotency_key", self.idempotency_key)
        if occurred < prepared:
            _fail("L9C12_P2_OCCURRED_BEFORE_PREPARED")
        if prepared > evaluated or occurred > evaluated:
            _fail("L9C12_P2_PREPARATION_AFTER_EVALUATION")
        object.__setattr__(self, "operation_type", LegalCourtOperationType.COURT_FILING_PREPARATION)
        object.__setattr__(self, "preparation_state", LegalCourtOperationPreparationState(state))
        object.__setattr__(self, "document_evidence_lineage", _references("document_evidence_lineage", self.document_evidence_lineage))
        object.__setattr__(self, "requested_scope_capabilities", scope)
        object.__setattr__(self, "prepared_at", prepared)
        object.__setattr__(self, "occurred_at", occurred)
        object.__setattr__(self, "evaluated_at", evaluated)


class LegalCourtOperationPreparationOrchestrator:
    """Revalidate certified authority and persist one internal P1 preparation."""

    def __init__(
        self,
        *,
        authority_currentness_composer: Any,
        decision_currentness_composer: Any,
        engagement_currentness_composer: Any,
        mandate_currentness_composer: Any,
        representation_collection: Any,
        authority_collection: Any,
        decision_collection: Any,
        engagement_collection: Any,
        mandate_collection: Any,
        preparation_collection: Any,
        principal_repository: Any,
        membership_repository: Any,
        role_assignment_repository: Any,
        principal_collection: Any = None,
        membership_collection: Any = None,
        role_assignment_collection: Any = None,
        representation_reader: Any = final_representation_registry,
        engagement_reader: Any = engagement_registry,
        mandate_reader: Any = mandate_registry,
        preparation_writer: Any = preparation_registry,
    ) -> None:
        required = (
            authority_currentness_composer, decision_currentness_composer,
            engagement_currentness_composer, mandate_currentness_composer,
            representation_collection, authority_collection, decision_collection,
            engagement_collection, mandate_collection, preparation_collection, principal_repository,
            membership_repository, role_assignment_repository,
        )
        if any(value is None for value in required):
            _fail("L9C12_P2_DEPENDENCY_REQUIRED")
        self._authority_currentness = authority_currentness_composer
        self._decision_currentness = decision_currentness_composer
        self._engagement_currentness = engagement_currentness_composer
        self._mandate_currentness = mandate_currentness_composer
        self._representation_collection = representation_collection
        self._authority_collection = authority_collection
        self._decision_collection = decision_collection
        self._engagement_collection = engagement_collection
        self._mandate_collection = mandate_collection
        self._preparation_collection = preparation_collection
        self._principal_repository = principal_repository
        self._membership_repository = membership_repository
        self._role_assignment_repository = role_assignment_repository
        self._principal_collection = principal_collection
        self._membership_collection = membership_collection
        self._role_assignment_collection = role_assignment_collection
        self._representation_reader = representation_reader
        self._engagement_reader = engagement_reader
        self._mandate_reader = mandate_reader
        self._preparation_writer = preparation_writer

    def prepare(self, request: LegalCourtOperationPreparationRequest, *, session: Any) -> LegalCourtOperationPreparation:
        """Freshly revalidate all certified lanes and persist one P1 snapshot."""
        transaction = _active_transaction(session)
        if type(request) is not LegalCourtOperationPreparationRequest:
            _fail("L9C12_P2_REQUEST_REQUIRED")
        try:
            representation = self._representation_reader.get_final_representation(
                request.tenant_id, request.final_representation_id,
                self._representation_collection, session=transaction,
            )
        except Exception as error:
            _fail("L9C12_P2_P24_LOOKUP_FAILED", error)
        if type(representation) is not LegalClientMatterFinalRepresentation:
            _fail("L9C12_P2_P24_REQUIRED")
        if (representation.tenant_id, representation.case_matter_id, representation.matter_fingerprint) != (
            request.tenant_id, request.case_matter_id, request.matter_fingerprint,
        ):
            _fail("L9C12_P2_P24_LINEAGE_MISMATCH")

        p1 = self._authority_currentness.compose_currentness(
            request.tenant_id, request.case_matter_id, request.matter_fingerprint,
            representation.client_party_id, representation.subject_identity_fingerprint,
            representation.representative_principal_id, request.evaluated_at, transaction,
        )
        if type(p1) is not LegalClientMatterRepresentationAuthorityCurrentness:
            _fail("L9C12_P2_P21A_INVALID")
        if _state(p1.state) != LegalClientMatterRepresentationAuthorityCurrentnessState.APPOINTED.value or p1.is_currently_appointed is not True:
            _fail("L9C12_P2_P21A_APPOINTED_REQUIRED")
        if (
            p1.tenant_id != representation.tenant_id or p1.case_matter_id != representation.case_matter_id
            or p1.matter_fingerprint != representation.matter_fingerprint
            or p1.client_party_id != representation.client_party_id
            or p1.subject_identity_fingerprint != representation.subject_identity_fingerprint
            or p1.representative_principal_id != representation.representative_principal_id
            or p1.representative_role != representation.representative_role
            or p1.decisive_authority_id != representation.representation_authority_id
            or p1.decisive_authority_fingerprint != representation.representation_authority_fingerprint
            or p1.currentness_id != representation.authority_currentness_id
            or p1.fingerprint != representation.authority_currentness_fingerprint
            or tuple(p1.representation_scope_capabilities) != tuple(representation.representation_scope_capabilities)
        ):
            _fail("L9C12_P2_P21A_P24_BINDING_MISMATCH")

        p2 = self._decision_currentness.compose_currentness(
            request.tenant_id, request.case_matter_id, request.matter_fingerprint,
            representation.client_party_id, representation.subject_identity_fingerprint,
            representation.representation_authority_id, representation.representation_authority_fingerprint,
            representation.representative_principal_id, representation.representative_role,
            request.evaluated_at, transaction,
        )
        if type(p2) is not LegalClientMatterRepresentationFirmDecisionCurrentness:
            _fail("L9C12_P2_P22_INVALID")
        if _state(p2.state) != LegalClientMatterRepresentationFirmDecisionCurrentnessState.ACCEPTED.value or p2.is_currently_accepted is not True:
            _fail("L9C12_P2_P22_ACCEPTED_REQUIRED")
        if (
            p2.tenant_id != representation.tenant_id or p2.case_matter_id != representation.case_matter_id
            or p2.matter_fingerprint != representation.matter_fingerprint
            or p2.client_party_id != representation.client_party_id
            or p2.subject_identity_fingerprint != representation.subject_identity_fingerprint
            or p2.representation_authority_id != representation.representation_authority_id
            or p2.representation_authority_fingerprint != representation.representation_authority_fingerprint
            or p2.representative_principal_id != representation.representative_principal_id
            or p2.representative_role != representation.representative_role
            or p2.decisive_decision_id != representation.firm_representation_decision_id
            or p2.decisive_decision_fingerprint != representation.firm_representation_decision_fingerprint
            or p2.currentness_id != representation.firm_decision_currentness_id
            or p2.fingerprint != representation.firm_decision_currentness_fingerprint
            or tuple(p2.decisive_representation_scope_capabilities) != tuple(representation.representation_scope_capabilities)
        ):
            _fail("L9C12_P2_P22_P24_BINDING_MISMATCH")

        engagement_currentness = self._engagement_currentness.compose_currentness(
            request.tenant_id, request.case_matter_id, request.matter_fingerprint,
            representation.client_party_id, representation.subject_identity_fingerprint,
            request.evaluated_at, transaction,
        )
        if getattr(engagement_currentness, "is_current", False) is not True:
            _fail("L9C12_P2_ENGAGEMENT_CURRENT_REQUIRED")
        if (
            engagement_currentness.tenant_id != representation.tenant_id
            or engagement_currentness.case_matter_id != representation.case_matter_id
            or engagement_currentness.matter_fingerprint != representation.matter_fingerprint
            or engagement_currentness.client_party_id != representation.client_party_id
            or engagement_currentness.subject_identity_fingerprint != representation.subject_identity_fingerprint
            or engagement_currentness.decisive_engagement_id != representation.engagement_id
            or engagement_currentness.decisive_engagement_fingerprint != representation.engagement_fingerprint
        ):
            _fail("L9C12_P2_ENGAGEMENT_P24_BINDING_MISMATCH")
        try:
            engagement = self._engagement_reader.get_engagement(
                request.tenant_id, representation.engagement_id,
                self._engagement_collection, session=transaction,
            )
        except Exception as error:
            _fail("L9C12_P2_ENGAGEMENT_LOOKUP_FAILED", error)
        if type(engagement) is not LegalClientMatterEngagement or engagement.fingerprint != representation.engagement_fingerprint:
            _fail("L9C12_P2_ENGAGEMENT_BINDING_MISMATCH")

        mandate_currentness = self._mandate_currentness.compose_currentness(
            request.tenant_id, representation.mandate_id, request.evaluated_at, transaction,
        )
        if getattr(mandate_currentness, "is_current", False) is not True:
            _fail("L9C12_P2_MANDATE_CURRENT_REQUIRED")
        if (
            mandate_currentness.tenant_id != representation.tenant_id
            or mandate_currentness.mandate_id != representation.mandate_id
            or mandate_currentness.mandate_fingerprint != representation.mandate_fingerprint
            or mandate_currentness.case_matter_id != representation.case_matter_id
            or mandate_currentness.matter_fingerprint != representation.matter_fingerprint
            or mandate_currentness.client_party_id != representation.client_party_id
            or mandate_currentness.subject_identity_fingerprint != representation.subject_identity_fingerprint
        ):
            _fail("L9C12_P2_MANDATE_P24_BINDING_MISMATCH")
        try:
            mandate = self._mandate_reader.get_mandate(
                request.tenant_id, representation.mandate_id,
                self._mandate_collection, session=transaction,
            )
        except Exception as error:
            _fail("L9C12_P2_MANDATE_LOOKUP_FAILED", error)
        if getattr(mandate, "fingerprint", None) != representation.mandate_fingerprint:
            _fail("L9C12_P2_MANDATE_BINDING_MISMATCH")

        role = representation.representative_role
        if role not in ELIGIBLE_REPRESENTATIVE_ROLES:
            _fail("L9C12_P2_REPRESENTATIVE_ROLE_INELIGIBLE")
        principal = _resolve(self._principal_repository, representation.representative_principal_id, collection=self._principal_collection, session=transaction, code="L9C12_P2_PRINCIPAL_UNAVAILABLE")
        membership = _resolve(self._membership_repository, representation.representative_principal_id, request.tenant_id, collection=self._membership_collection, session=transaction, code="L9C12_P2_MEMBERSHIP_UNAVAILABLE")
        assignment = _resolve(self._role_assignment_repository, representation.representative_principal_id, request.tenant_id, role, collection=self._role_assignment_collection, session=transaction, code="L9C12_P2_ROLE_ASSIGNMENT_UNAVAILABLE")
        if type(principal) is not PrincipalAuthority or principal.status is not PrincipalStatus.ACTIVE or principal.principal_id != representation.representative_principal_id:
            _fail("L9C12_P2_PRINCIPAL_INACTIVE")
        if type(membership) is not TenantMembershipAuthority or membership.status is not TenantMembershipStatus.ACTIVE or membership.tenant_id != request.tenant_id or membership.principal_id != representation.representative_principal_id:
            _fail("L9C12_P2_MEMBERSHIP_INACTIVE")
        if type(assignment) is not RoleAssignmentAuthority or assignment.status is not RoleAssignmentStatus.ACTIVE or assignment.tenant_id != request.tenant_id or assignment.principal_id != representation.representative_principal_id or assignment.role_id != role:
            _fail("L9C12_P2_ROLE_ASSIGNMENT_INVALID")

        p24_scope = set(representation.representation_scope_capabilities)
        p21_scope = set(p1.representation_scope_capabilities)
        p22_scope = set(p2.decisive_representation_scope_capabilities)
        mandate_scope = set(getattr(mandate, "capabilities", ()))
        if "LITIGATION_PREPARATION" not in p24_scope or "LITIGATION_PREPARATION" not in p21_scope or "LITIGATION_PREPARATION" not in p22_scope or LegalCourtOperationType.COURT_FILING_PREPARATION.value not in mandate_scope:
            _fail("L9C12_P2_COURT_SCOPE_UNAUTHORIZED")
        if set(request.requested_scope_capabilities) != {LegalCourtOperationType.COURT_FILING_PREPARATION.value}:
            _fail("L9C12_P2_SCOPE_WIDENING_FORBIDDEN")

        value = LegalCourtOperationPreparation(
            tenant_id=representation.tenant_id,
            case_matter_id=representation.case_matter_id,
            matter_fingerprint=representation.matter_fingerprint,
            final_representation_id=representation.representation_id,
            final_representation_fingerprint=representation.fingerprint,
            operation_type=request.operation_type,
            target_court_reference=request.target_court_reference,
            target_jurisdiction_reference=request.target_jurisdiction_reference,
            document_evidence_lineage=request.document_evidence_lineage,
            requested_scope_capabilities=request.requested_scope_capabilities,
            preparation_state=request.preparation_state,
            source_evidence_reference=request.source_evidence_reference,
            source_evidence_fingerprint=request.source_evidence_fingerprint,
            provenance_reference=request.provenance_reference,
            prepared_at=request.prepared_at,
            occurred_at=request.occurred_at,
            idempotency_key=request.idempotency_key,
        )
        try:
            return self._preparation_writer.persist_court_operation_preparation(value, self._preparation_collection, session=transaction)
        except Exception as error:
            _fail("L9C12_P2_PREPARATION_PERSIST_FAILED", error)


__all__ = [
    "COURT_SCOPE_DERIVATION_MODEL", "ELIGIBLE_REPRESENTATIVE_ROLES", "VERSION",
    "LegalCourtOperationPreparationOrchestrationError", "LegalCourtOperationPreparationOrchestrator",
    "LegalCourtOperationPreparationRequest",
]


# ARTIFACT: legal_court_operation_preparation_orchestrator.py
# VERSION: v1.0.0-L9C12-P2-COURT-OPERATION-PREPARATION-ORCHESTRATOR
# AUTHORITY BOUNDARY: internal Court preparation composition only
# TENANT POSTURE: exact upstream lineage and caller transaction propagation
# FAIL-CLOSED POSTURE: stale, mismatched, widened and inactive authority rejects
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively
# END OF WILSY OS SOVEREIGN ARTIFACT
