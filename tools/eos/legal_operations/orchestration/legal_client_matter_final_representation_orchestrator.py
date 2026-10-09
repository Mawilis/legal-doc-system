"""WILSY OS deterministic final client-matter Representation formation.

TITLE: WILSY OS Legal Client Matter Final Representation Orchestrator
VERSION: v1.0.0-L9C11-P25-FINAL-REPRESENTATION-ORCHESTRATOR
AUTHORITY: Wilsy OS Core Governance / Python EOS Legal Operations
EPITOME: Re-read certified P21A, P22, Engagement and Mandate currentness,
         revalidate the representative's canonical principal, membership and
         role facts, construct one immutable P24 Representation and persist it
         in the caller's active transaction. This is deterministic internal
         business formation, not IAM, Court, professional or financial truth.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tools/eos/legal_operations/orchestration/legal_client_matter_final_representation_orchestrator.py
COLLABORATION / OWNERSHIP: P21A/P22 and Engagement/Mandate composers own
                            currentness projections; P24 owns immutable final
                            Representation semantics; P24 registry owns durable
                            persistence. IAM repositories own principal,
                            membership and role facts. P25 owns composition only.
CERTIFICATION / UPDATE DATE: 2026-09-28
CHANGELOG: v1.0.0-L9C11-P25 establishes explicit-input, caller-transaction
           formation with exact P1/P2 cross-lane binding, live representative
           revalidation, deterministic scope intersection and one P24 write.
           No permission, authorization-evidence row, upstream write,
           currentness, Court, HTTP/UI/Node or finance authority is created.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2; ISO 27001.
SECURITY / PRIVACY POSTURE: Caller claims never supply authoritative role,
                             scope, fingerprints or decisions; all such facts
                             are re-read from certified projections/repositories.
TENANT BOUNDARY: Every composer, IAM repository, upstream registry and final
                 registry call receives the explicit tenant and same session.
AUTHORITY BOUNDARY: Internal final Representation formation only; no attorney-
                    of-record, admission, practising, Court or execution claim.
FINANCIAL AUTHORITY BOUNDARY: None; Kennel EOS remains exclusive.
TRANSACTION BOUNDARY: Caller supplies and owns an active transaction. P25 never
                      starts, commits, aborts or retries a transaction.
FAIL-CLOSED DECLARATION: Missing/inactive/ambiguous/corrupt currentness,
                         lineage mismatch, inactive IAM facts, scope widening,
                         chronology failure and persistence uncertainty reject.
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
from tools.eos.legal_operations.domain.legal_client_matter_engagement_currentness import LegalClientMatterEngagementCurrentness
from tools.eos.legal_operations.domain.legal_client_matter_mandate import LegalClientMatterMandate
from tools.eos.legal_operations.domain.legal_client_matter_mandate_currentness import LegalClientMatterMandateCurrentness
from tools.eos.legal_operations.domain.legal_client_matter_representation_authority import LegalClientMatterRepresentationAuthority
from tools.eos.legal_operations.domain.legal_client_matter_representation_authority_currentness import (
    LegalClientMatterRepresentationAuthorityCurrentness,
    LegalClientMatterRepresentationAuthorityCurrentnessState,
)
from tools.eos.legal_operations.domain.legal_client_matter_representation_firm_decision import LegalClientMatterRepresentationFirmDecision
from tools.eos.legal_operations.domain.legal_client_matter_representation_firm_decision_currentness import (
    LegalClientMatterRepresentationFirmDecisionCurrentness,
    LegalClientMatterRepresentationFirmDecisionCurrentnessState,
)
from tools.eos.legal_operations.domain.legal_client_matter_final_representation import LegalClientMatterFinalRepresentation
from tools.eos.legal_operations.registry import legal_client_matter_engagement_registry as engagement_registry
from tools.eos.legal_operations.registry import legal_client_matter_final_representation_registry as final_registry
from tools.eos.legal_operations.registry import legal_client_matter_mandate_registry as mandate_registry
from tools.eos.legal_operations.registry import legal_client_matter_representation_authority_registry as authority_registry
from tools.eos.legal_operations.registry import legal_client_matter_representation_firm_decision_registry as decision_registry


VERSION: Final[str] = "v1.0.0-L9C11-P25-FINAL-REPRESENTATION-ORCHESTRATOR"
ELIGIBLE_REPRESENTATIVE_ROLES: Final[frozenset[str]] = frozenset({"LEGAL_ATTORNEY", "LEGAL_PARTNER"})
UTC = timezone.utc


class LegalClientMatterFinalRepresentationOrchestrationError(RuntimeError):
    """Stable, non-sensitive P25 fail-closed error."""

    def __init__(self, code: str) -> None:
        self.code = code
        super().__init__(code)


def _fail(code: str, cause: BaseException | None = None) -> NoReturn:
    error = LegalClientMatterFinalRepresentationOrchestrationError(code)
    if cause is None:
        raise error
    raise error from cause


def _text(name: str, value: object, *, limit: int = 512) -> str:
    if not isinstance(value, str) or not value or value != value.strip() or len(value) > limit:
        _fail(f"L9C11_P25_{name.upper()}_INVALID")
    return value


def _timestamp(name: str, value: object) -> datetime:
    if not isinstance(value, datetime) or value.tzinfo is None or value.utcoffset() is None:
        _fail(f"L9C11_P25_{name.upper()}_INVALID")
    return value.astimezone(UTC)


def _active_transaction(session: Any) -> Any:
    if session is None:
        _fail("L9C11_P25_ACTIVE_TRANSACTION_REQUIRED")
    marker = getattr(session, "in_transaction", None)
    try:
        active = marker() if callable(marker) else marker
    except Exception as error:
        _fail("L9C11_P25_ACTIVE_TRANSACTION_REQUIRED", error)
    if active is not True:
        _fail("L9C11_P25_ACTIVE_TRANSACTION_REQUIRED")
    return session


def _state(value: object) -> str:
    rendered = getattr(value, "value", value)
    return rendered if isinstance(rendered, str) else "INVALID"


def _scope(value: object, name: str) -> tuple[str, ...]:
    if isinstance(value, str) or not isinstance(value, (tuple, list, set, frozenset)):
        _fail(f"L9C11_P25_{name.upper()}_INVALID")
    labels = {str(getattr(item, "value", item)).upper() for item in value}
    if not labels or any(not item or item != item.strip() for item in labels):
        _fail(f"L9C11_P25_{name.upper()}_INVALID")
    return tuple(sorted(labels))


def _current(value: object, expected: str, name: str) -> None:
    if _state(getattr(value, "state", None)) != expected:
        _fail(f"L9C11_P25_{name.upper()}_{expected}_REQUIRED")
    predicate = getattr(value, "is_currently_appointed", None) if expected == "APPOINTED" else getattr(value, "is_currently_accepted", None) if expected == "ACCEPTED" else getattr(value, "is_usable", None)
    if predicate is not True:
        _fail(f"L9C11_P25_{name.upper()}_{expected}_REQUIRED")


def _resolve(repository: Any, *args: object, collection: Any, session: Any, code: str) -> object:
    try:
        return repository.resolve(*args, collection, session=session)
    except TypeError:
        try:
            return repository.resolve(*args, session=session)
        except Exception as error:
            _fail(code, error)
    except Exception as error:
        _fail(code, error)


@dataclass(frozen=True, slots=True)
class LegalClientMatterFinalRepresentationFormationRequest:
    """Minimal P25 command; authoritative role/scope/decision fields are absent."""

    tenant_id: str
    case_matter_id: str
    matter_fingerprint: str
    client_party_id: str
    subject_identity_fingerprint: str
    representative_principal_id: str
    evaluated_at: datetime
    effective_from: datetime
    occurred_at: datetime
    idempotency_key: str
    representative_eligibility_reference: str
    representative_eligibility_fingerprint: str
    source_evidence_reference: str
    source_evidence_fingerprint: str
    requested_scope_capabilities: tuple[str, ...] | list[str] | None = None

    def __post_init__(self) -> None:
        for name, value in (
            ("tenant_id", self.tenant_id), ("case_matter_id", self.case_matter_id),
            ("matter_fingerprint", self.matter_fingerprint), ("client_party_id", self.client_party_id),
            ("subject_identity_fingerprint", self.subject_identity_fingerprint),
            ("representative_principal_id", self.representative_principal_id),
            ("idempotency_key", self.idempotency_key),
            ("representative_eligibility_reference", self.representative_eligibility_reference),
            ("representative_eligibility_fingerprint", self.representative_eligibility_fingerprint),
            ("source_evidence_reference", self.source_evidence_reference),
            ("source_evidence_fingerprint", self.source_evidence_fingerprint),
        ):
            _text(name, value)
        object.__setattr__(self, "evaluated_at", _timestamp("evaluated_at", self.evaluated_at))
        object.__setattr__(self, "effective_from", _timestamp("effective_from", self.effective_from))
        object.__setattr__(self, "occurred_at", _timestamp("occurred_at", self.occurred_at))
        if self.occurred_at < self.effective_from:
            _fail("L9C11_P25_OCCURRED_BEFORE_EFFECTIVE")
        if self.requested_scope_capabilities is not None:
            object.__setattr__(self, "requested_scope_capabilities", _scope(self.requested_scope_capabilities, "requested_scope"))


class LegalClientMatterFinalRepresentationOrchestrator:
    """Form and persist one P24 Representation in a caller-owned transaction."""

    def __init__(
        self,
        *,
        authority_currentness_composer: Any,
        decision_currentness_composer: Any,
        engagement_currentness_composer: Any,
        mandate_currentness_composer: Any,
        authority_collection: Any,
        decision_collection: Any,
        engagement_collection: Any,
        mandate_collection: Any,
        final_representation_collection: Any,
        principal_repository: Any,
        membership_repository: Any,
        role_assignment_repository: Any,
        principal_collection: Any = None,
        membership_collection: Any = None,
        role_assignment_collection: Any = None,
        authority_reader: Any = authority_registry,
        decision_reader: Any = decision_registry,
        engagement_reader: Any = engagement_registry,
        mandate_reader: Any = mandate_registry,
        representation_writer: Any = final_registry,
    ) -> None:
        values = (authority_currentness_composer, decision_currentness_composer, engagement_currentness_composer, mandate_currentness_composer, authority_collection, decision_collection, engagement_collection, mandate_collection, final_representation_collection, principal_repository, membership_repository, role_assignment_repository)
        if any(value is None for value in values):
            _fail("L9C11_P25_DEPENDENCY_REQUIRED")
        self._authority_currentness = authority_currentness_composer
        self._decision_currentness = decision_currentness_composer
        self._engagement_currentness = engagement_currentness_composer
        self._mandate_currentness = mandate_currentness_composer
        self._authority_collection = authority_collection
        self._decision_collection = decision_collection
        self._engagement_collection = engagement_collection
        self._mandate_collection = mandate_collection
        self._final_collection = final_representation_collection
        self._principal_repository = principal_repository
        self._membership_repository = membership_repository
        self._role_assignment_repository = role_assignment_repository
        self._principal_collection = principal_collection
        self._membership_collection = membership_collection
        self._role_assignment_collection = role_assignment_collection
        self._authority_reader = authority_reader
        self._decision_reader = decision_reader
        self._engagement_reader = engagement_reader
        self._mandate_reader = mandate_reader
        self._representation_writer = representation_writer

    def form(self, request: LegalClientMatterFinalRepresentationFormationRequest, *, session: Any) -> LegalClientMatterFinalRepresentation:
        """Revalidate certified facts, construct P24 and persist exact replay."""
        transaction = _active_transaction(session)
        if type(request) is not LegalClientMatterFinalRepresentationFormationRequest:
            _fail("L9C11_P25_REQUEST_REQUIRED")
        p1 = self._authority_currentness.compose_currentness(
            request.tenant_id, request.case_matter_id, request.matter_fingerprint,
            request.client_party_id, request.subject_identity_fingerprint,
            request.representative_principal_id, request.evaluated_at, transaction,
        )
        if type(p1) is not LegalClientMatterRepresentationAuthorityCurrentness:
            _fail("L9C11_P25_P1_CURRENTNESS_INVALID")
        _current(p1, "APPOINTED", "P1")
        if (p1.tenant_id, p1.case_matter_id, p1.matter_fingerprint, p1.client_party_id, p1.subject_identity_fingerprint, p1.representative_principal_id) != (request.tenant_id, request.case_matter_id, request.matter_fingerprint, request.client_party_id, request.subject_identity_fingerprint, request.representative_principal_id):
            _fail("L9C11_P25_P1_LINEAGE_MISMATCH")
        if not p1.decisive_authority_id or not p1.decisive_authority_fingerprint or not p1.representative_role:
            _fail("L9C11_P25_P1_BINDING_MISSING")
        role = _text("representative_role", p1.representative_role)
        if role not in ELIGIBLE_REPRESENTATIVE_ROLES:
            _fail("L9C11_P25_REPRESENTATIVE_ROLE_INELIGIBLE")
        authority = self._authority_reader.get_representation_authority(request.tenant_id, p1.decisive_authority_id, self._authority_collection, session=transaction)
        if type(authority) is not LegalClientMatterRepresentationAuthority or authority.fingerprint != p1.decisive_authority_fingerprint:
            _fail("L9C11_P25_P1_BINDING_MISMATCH")
        principal = _resolve(self._principal_repository, request.representative_principal_id, collection=self._principal_collection, session=transaction, code="L9C11_P25_PRINCIPAL_UNAVAILABLE")
        membership = _resolve(self._membership_repository, request.representative_principal_id, request.tenant_id, collection=self._membership_collection, session=transaction, code="L9C11_P25_MEMBERSHIP_UNAVAILABLE")
        assignment = _resolve(self._role_assignment_repository, request.representative_principal_id, request.tenant_id, role, collection=self._role_assignment_collection, session=transaction, code="L9C11_P25_ROLE_ASSIGNMENT_UNAVAILABLE")
        if type(principal) is not PrincipalAuthority or principal.status is not PrincipalStatus.ACTIVE or principal.principal_id != request.representative_principal_id:
            _fail("L9C11_P25_PRINCIPAL_INACTIVE")
        if type(membership) is not TenantMembershipAuthority or membership.status is not TenantMembershipStatus.ACTIVE or membership.principal_id != request.representative_principal_id or membership.tenant_id != request.tenant_id:
            _fail("L9C11_P25_MEMBERSHIP_INACTIVE")
        if type(assignment) is not RoleAssignmentAuthority or assignment.status is not RoleAssignmentStatus.ACTIVE or assignment.principal_id != request.representative_principal_id or assignment.tenant_id != request.tenant_id or assignment.role_id != role:
            _fail("L9C11_P25_ROLE_ASSIGNMENT_INVALID")
        if authority.representative_principal_id != request.representative_principal_id or authority.representative_role != role:
            _fail("L9C11_P25_P1_REPRESENTATIVE_BINDING_MISMATCH")
        p2 = self._decision_currentness.compose_currentness(
            request.tenant_id, request.case_matter_id, request.matter_fingerprint,
            request.client_party_id, request.subject_identity_fingerprint,
            p1.decisive_authority_id, p1.decisive_authority_fingerprint,
            request.representative_principal_id, role, request.evaluated_at, transaction,
        )
        if type(p2) is not LegalClientMatterRepresentationFirmDecisionCurrentness:
            _fail("L9C11_P25_P2_CURRENTNESS_INVALID")
        _current(p2, "ACCEPTED", "P2")
        if (p2.tenant_id, p2.case_matter_id, p2.matter_fingerprint, p2.client_party_id, p2.subject_identity_fingerprint, p2.representation_authority_id, p2.representation_authority_fingerprint, p2.representative_principal_id, p2.representative_role) != (request.tenant_id, request.case_matter_id, request.matter_fingerprint, request.client_party_id, request.subject_identity_fingerprint, authority.authority_id, authority.fingerprint, request.representative_principal_id, role):
            _fail("L9C11_P25_P2_LINEAGE_MISMATCH")
        if not p2.decisive_decision_id or not p2.decisive_decision_fingerprint:
            _fail("L9C11_P25_P2_BINDING_MISSING")
        decision = self._decision_reader.get_firm_decision(request.tenant_id, p2.decisive_decision_id, self._decision_collection, session=transaction)
        if type(decision) is not LegalClientMatterRepresentationFirmDecision or decision.fingerprint != p2.decisive_decision_fingerprint:
            _fail("L9C11_P25_P2_BINDING_MISMATCH")
        engagement_currentness = self._engagement_currentness.compose_currentness(
            request.tenant_id, request.case_matter_id, request.matter_fingerprint,
            request.client_party_id, request.subject_identity_fingerprint, request.evaluated_at, transaction,
        )
        _current(engagement_currentness, "CURRENT", "ENGAGEMENT")
        if not engagement_currentness.decisive_engagement_id or not engagement_currentness.decisive_engagement_fingerprint:
            _fail("L9C11_P25_ENGAGEMENT_BINDING_MISSING")
        engagement = self._engagement_reader.get_engagement(request.tenant_id, engagement_currentness.decisive_engagement_id, self._engagement_collection, session=transaction)
        if type(engagement) is not LegalClientMatterEngagement or engagement.fingerprint != engagement_currentness.decisive_engagement_fingerprint:
            _fail("L9C11_P25_ENGAGEMENT_BINDING_MISMATCH")
        mandate_currentness = self._mandate_currentness.compose_currentness(request.tenant_id, authority.mandate_id, request.evaluated_at, transaction)
        _current(mandate_currentness, "CURRENT", "MANDATE")
        mandate = self._mandate_reader.get_mandate(request.tenant_id, authority.mandate_id, self._mandate_collection, session=transaction)
        if type(mandate) is not LegalClientMatterMandate or mandate.fingerprint != mandate_currentness.mandate_fingerprint:
            _fail("L9C11_P25_MANDATE_BINDING_MISMATCH")
        if not (authority.tenant_id == decision.tenant_id == engagement.tenant_id == mandate.tenant_id == request.tenant_id and authority.case_matter_id == decision.case_matter_id == engagement.case_matter_id == mandate.case_matter_id == request.case_matter_id and authority.matter_fingerprint == decision.matter_fingerprint == engagement.matter_fingerprint == mandate.matter_fingerprint == request.matter_fingerprint and authority.client_party_id == decision.client_party_id == engagement.client_party_id == mandate.client_party_id == request.client_party_id and authority.subject_identity_fingerprint == decision.subject_identity_fingerprint == engagement.subject_identity_fingerprint == mandate.subject_identity_fingerprint):
            _fail("L9C11_P25_CROSS_LANE_LINEAGE_MISMATCH")
        p1_scope = _scope(p1.representation_scope_capabilities, "P1_SCOPE")
        p2_scope = _scope(p2.decisive_representation_scope_capabilities, "P2_SCOPE")
        mandate_scope = _scope(mandate.capabilities, "MANDATE_SCOPE")
        derived_scope = tuple(sorted(set(p1_scope) & set(p2_scope) & set(mandate_scope)))
        if not derived_scope:
            _fail("L9C11_P25_SCOPE_INTERSECTION_EMPTY")
        final_scope = derived_scope
        if request.requested_scope_capabilities is not None:
            requested = _scope(request.requested_scope_capabilities, "REQUESTED_SCOPE")
            if not set(requested).issubset(set(derived_scope)):
                _fail("L9C11_P25_SCOPE_WIDENING_FORBIDDEN")
            final_scope = requested
        value = LegalClientMatterFinalRepresentation.from_canonical(
            authority=authority, authority_currentness=p1, firm_decision=decision,
            firm_decision_currentness=p2, engagement=engagement,
            engagement_currentness=engagement_currentness, mandate=mandate,
            mandate_currentness=mandate_currentness, representation_scope_capabilities=final_scope,
            representative_eligibility_reference=request.representative_eligibility_reference,
            representative_eligibility_fingerprint=request.representative_eligibility_fingerprint,
            source_evidence_reference=request.source_evidence_reference,
            source_evidence_fingerprint=request.source_evidence_fingerprint,
            effective_from=request.effective_from, occurred_at=request.occurred_at,
            idempotency_key=request.idempotency_key,
        )
        return self._representation_writer.persist_final_representation(value, self._final_collection, session=transaction)


__all__ = [
    "ELIGIBLE_REPRESENTATIVE_ROLES",
    "LegalClientMatterFinalRepresentationFormationRequest",
    "LegalClientMatterFinalRepresentationOrchestrationError",
    "LegalClientMatterFinalRepresentationOrchestrator",
    "VERSION",
]


# ARTIFACT: legal_client_matter_final_representation_orchestrator.py
# VERSION: v1.0.0-L9C11-P25-FINAL-REPRESENTATION-ORCHESTRATOR
# AUTHORITY BOUNDARY: deterministic P24 formation only
# TENANT POSTURE: exact tenant and same-session propagation across every read/write
# FAIL-CLOSED POSTURE: non-positive currentness, IAM mismatch, scope widening and persistence failure reject
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively
# END OF WILSY OS SOVEREIGN ARTIFACT
