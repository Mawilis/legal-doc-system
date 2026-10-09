"""WILSY OS firm-side Representation-decision orchestration.

TITLE: WILSY OS Legal Client Matter Representation Firm Decision Orchestrator
VERSION: v1.0.0-L9C11-P21B-FIRM-REPRESENTATION-DECISION-ORCHESTRATOR
AUTHORITY: Wilsy OS Core Governance / Python EOS Legal Operations
EPITOME: Authorize one firm actor, consume certified P1/Engagement/Mandate
         currentness and append one immutable P2 decision in a caller-owned
         transaction.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tools/eos/legal_operations/orchestration/legal_client_matter_representation_firm_decision_orchestrator.py
COLLABORATION / OWNERSHIP: P21A owns Representation-authority currentness;
                            P2 owns immutable firm decision semantics; P9 owns
                            P2 durability; IAM owns actor and representative
                            identity facts. This adapter composes only those
                            certified authorities.
CERTIFICATION / UPDATE DATE: 2026-09-28
CHANGELOG: v1.0.0-L9C11-P21B establishes exact firm IAM, OPEN matter and
           client-party revalidation, P21A/Engagement/Mandate currentness
           consumption, representative eligibility, subject-bound authorization
           evidence, atomic P2 persistence, and exact replay semantics. It
           creates no client authority, currentness write, final Representation,
           Court, professional or financial authority.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2; ISO 27001.
SECURITY / PRIVACY POSTURE: Only bounded opaque identifiers, references and
                             SHA3-512 fingerprints cross this boundary.
TENANT BOUNDARY: Tenant derives from active SovereignIdentity; every read,
                 evidence issue and P2 write is exact-tenant and same-session.
AUTHORITY BOUNDARY: Firm-decision evidence only. ACCEPTED is not a formed
                    Representation and no Court or professional authority is
                    inferred.
FINANCIAL AUTHORITY BOUNDARY: No billing, payment, settlement or execution;
                              Kennel EOS remains exclusive.
TRANSACTION BOUNDARY: Caller supplies and owns an active transaction. This
                      module never starts, commits, aborts, retries or
                      reconciles a transaction.
FAIL-CLOSED DECLARATION: Missing, stale, ambiguous, corrupt, foreign,
                         divergent or unavailable evidence rejects.
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
import hashlib
import json
import re
from typing import Any, Final, NoReturn, cast

from tools.eos.auth.identity import SovereignIdentity
from tools.eos.auth.principal_authority import PrincipalAuthority
from tools.eos.auth.principal_status import PrincipalStatus
from tools.eos.auth.role_assignment import RoleAssignmentAuthority, RoleAssignmentStatus
from tools.eos.auth.tenant_authorization_decision_evidence_registry import (
    TenantAuthorizationDecisionEvidenceAuthorizationDeniedError,
    TenantAuthorizationDecisionEvidenceConflictError,
    TenantAuthorizationDecisionEvidencePersistenceError,
    TenantAuthorizationDecisionEvidenceRegistry,
    TenantAuthorizationDecisionEvidenceRegistryError,
    TenantAuthorizationDecisionEvidenceTransactionRequiredError,
)
from tools.eos.auth.tenant_membership import TenantMembershipAuthority, TenantMembershipStatus
from tools.eos.legal_operations.domain.legal_client_matter_engagement import LegalClientMatterEngagement
from tools.eos.legal_operations.domain.legal_client_matter_mandate import LegalClientMatterMandate
from tools.eos.legal_operations.domain.legal_client_matter_representation_authority import (
    LegalClientMatterRepresentationAuthority,
)
from tools.eos.legal_operations.domain.legal_client_matter_representation_authority_currentness import (
    LegalClientMatterRepresentationAuthorityCurrentness,
)
from tools.eos.legal_operations.domain.legal_client_matter_representation_firm_decision import (
    LegalClientMatterRepresentationFirmDecision,
    LegalClientMatterRepresentationFirmDecisionError,
    LegalClientMatterRepresentationFirmDecisionType,
)
from tools.eos.legal_operations.domain.legal_matter_party import (
    LegalMatterParty,
    LegalMatterPartyRole,
    LegalMatterPartySide,
)
from tools.eos.legal_operations.domain.legal_operations_current_projection import resolve_current_lifecycle_snapshot
from tools.eos.legal_operations.domain.legal_operations_lifecycle import CaseMatter, CaseMatterState
from tools.eos.legal_operations.orchestration.legal_client_matter_engagement_currentness_composer import (
    LegalClientMatterEngagementCurrentnessComposer,
)
from tools.eos.legal_operations.orchestration.legal_client_matter_mandate_currentness_composer import (
    LegalClientMatterMandateCurrentnessComposer,
)
from tools.eos.legal_operations.orchestration.legal_client_matter_representation_authority_currentness_composer import (
    LegalClientMatterRepresentationAuthorityCurrentnessComposer,
)
from tools.eos.legal_operations.registry import (
    legal_client_matter_engagement_registry as engagement_registry,
    legal_client_matter_mandate_registry as mandate_registry,
    legal_client_matter_representation_authority_registry as authority_registry,
    legal_client_matter_representation_firm_decision_registry as decision_registry,
    legal_matter_party_registry as party_registry,
    legal_operations_lifecycle_registry as matter_registry,
)


VERSION: Final[str] = "v1.0.0-L9C11-P21B-FIRM-REPRESENTATION-DECISION-ORCHESTRATOR"
OPERATION: Final[str] = "legal_matter_representation_firm_decision_write"
PERMISSION: Final[str] = "legal_operations:matter_representation_firm_decision:write"
SUBJECT_PREFIX: Final[str] = "legal-representation-firm-decision"
ELIGIBLE_REPRESENTATIVE_ROLES: Final[frozenset[str]] = frozenset({"LEGAL_PARTNER", "LEGAL_ATTORNEY"})
_IDENTITY = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._:-]{0,159}$")
_FINGERPRINT = re.compile(r"^[0-9a-f]{128}$")
_MAX_REFERENCE: Final[int] = 512
_MAX_IDEMPOTENCY: Final[int] = 240
UTC: Final[timezone] = timezone.utc


class LegalClientMatterRepresentationFirmDecisionOrchestrationError(RuntimeError):
    """Stable non-sensitive failure at the P21B boundary."""

    def __init__(self, code: str) -> None:
        self.code = code
        super().__init__(code)


class LegalClientMatterRepresentationFirmDecisionOrchestrationRetryRequiredError(
    LegalClientMatterRepresentationFirmDecisionOrchestrationError
):
    """The caller must restart the whole transaction after a race."""


def _fail(code: str, cause: BaseException | None = None) -> NoReturn:
    error = LegalClientMatterRepresentationFirmDecisionOrchestrationError(code)
    if cause is None:
        raise error
    raise error from cause


def _retry(code: str, cause: BaseException) -> NoReturn:
    raise LegalClientMatterRepresentationFirmDecisionOrchestrationRetryRequiredError(code) from cause


def _active_transaction(session: Any) -> Any:
    if session is None:
        _fail("L9C11_P21B_ACTIVE_TRANSACTION_REQUIRED")
    marker = getattr(session, "in_transaction", None)
    try:
        active = marker() if callable(marker) else marker
    except Exception as error:
        _fail("L9C11_P21B_ACTIVE_TRANSACTION_REQUIRED", error)
    if active is not True:
        _fail("L9C11_P21B_ACTIVE_TRANSACTION_REQUIRED")
    return session


def _text(name: str, value: object, *, limit: int = _MAX_REFERENCE) -> str:
    if (
        not isinstance(value, str)
        or not value
        or value != value.strip()
        or len(value) > limit
        or any(ord(character) < 32 or 0x7F <= ord(character) <= 0x9F for character in value)
    ):
        _fail(f"L9C11_P21B_{name.upper()}_INVALID")
    return value


def _identity_text(name: str, value: object) -> str:
    value = _text(name, value, limit=160)
    if _IDENTITY.fullmatch(value) is None:
        _fail(f"L9C11_P21B_{name.upper()}_INVALID")
    return value


def _fingerprint(name: str, value: object) -> str:
    if not isinstance(value, str) or _FINGERPRINT.fullmatch(value) is None:
        _fail(f"L9C11_P21B_{name.upper()}_INVALID")
    return value


def _timestamp(name: str, value: object) -> datetime:
    parsed = value
    if isinstance(parsed, str):
        try:
            parsed = datetime.fromisoformat(parsed.replace("Z", "+00:00"))
        except ValueError as error:
            _fail(f"L9C11_P21B_{name.upper()}_INVALID", error)
    if not isinstance(parsed, datetime) or parsed.tzinfo is None or parsed.utcoffset() is None:
        _fail(f"L9C11_P21B_{name.upper()}_INVALID")
    return parsed.astimezone(UTC)


def _scope(value: object) -> tuple[str, ...]:
    if isinstance(value, str) or not isinstance(value, (tuple, list, set, frozenset)):
        _fail("L9C11_P21B_SCOPE_INVALID")
    labels: list[str] = []
    for item in value:
        label = item.value if hasattr(item, "value") else item
        if not isinstance(label, str):
            _fail("L9C11_P21B_SCOPE_INVALID")
        labels.append(label.upper())
    result = tuple(sorted(set(labels)))
    if not result or any(not _IDENTITY.fullmatch(item) for item in result):
        _fail("L9C11_P21B_SCOPE_INVALID")
    if any(item in {"COURT", "COURT_AUTHORITY", "PAYMENT", "SETTLEMENT", "FINANCIAL_EXECUTION"} for item in result):
        _fail("L9C11_P21B_SCOPE_PROHIBITED")
    return result


def _identity_scope(identity: object) -> tuple[str, str]:
    if not isinstance(identity, SovereignIdentity):
        _fail("L9C11_P21B_AUTHENTICATED_IDENTITY_REQUIRED")
    if identity.status is not PrincipalStatus.ACTIVE:
        _fail("L9C11_P21B_ACTOR_INACTIVE")
    return _identity_text("tenant_id", identity.tenant_id), _identity_text("principal_id", identity.identity_id)


def _canonical_digest(payload: dict[str, object]) -> str:
    return hashlib.sha3_512(json.dumps(payload, ensure_ascii=False, allow_nan=False, sort_keys=True, separators=(",", ":")).encode("utf-8")).hexdigest()


def _require_current(value: object, name: str) -> None:
    state = getattr(value, "state", None)
    if getattr(value, "is_current", False) is not True and getattr(state, "value", state) != "CURRENT":
        _fail(f"L9C11_P21B_{name.upper()}_CURRENT_REQUIRED")


@dataclass(frozen=True, slots=True)
class LegalClientMatterRepresentationFirmDecisionRequest:
    """Immutable scalar command; all authoritative facts are re-read."""

    tenant_id: str
    case_matter_id: str
    client_party_id: str
    representative_principal_id: str
    decision: LegalClientMatterRepresentationFirmDecisionType | str
    representation_scope_capabilities: tuple[str, ...] | list[str]
    evaluated_at: datetime
    idempotency_key: str
    source_evidence_reference: str
    source_evidence_fingerprint: str
    identity: SovereignIdentity

    def __post_init__(self) -> None:
        for name, value in (("tenant_id", self.tenant_id), ("case_matter_id", self.case_matter_id), ("client_party_id", self.client_party_id), ("representative_principal_id", self.representative_principal_id), ("idempotency_key", self.idempotency_key), ("source_evidence_reference", self.source_evidence_reference)):
            _identity_text(name, value) if name != "source_evidence_reference" else _text(name, value)
        _fingerprint("source_evidence_fingerprint", self.source_evidence_fingerprint)
        _timestamp("evaluated_at", self.evaluated_at)
        _scope(self.representation_scope_capabilities)
        if not isinstance(self.identity, SovereignIdentity):
            _fail("L9C11_P21B_AUTHENTICATED_IDENTITY_REQUIRED")


class LegalClientMatterRepresentationFirmDecisionOrchestrator:
    """Issue or exactly replay one P2 firm Representation decision."""

    def __init__(
        self,
        *,
        matter_lifecycle_collection: Any,
        party_collection: Any,
        authority_collection: Any,
        engagement_collection: Any,
        mandate_collection: Any,
        grant_collection: Any,
        grant_lifecycle_collection: Any,
        acknowledgment_collection: Any,
        decision_collection: Any,
        principal_repository: Any,
        membership_repository: Any,
        role_assignment_repository: Any,
        business_role_repository: Any,
        authorization_evidence_registry: TenantAuthorizationDecisionEvidenceRegistry,
        authority_currentness_composer: Any | None = None,
        engagement_currentness_composer: Any | None = None,
        mandate_currentness_composer: Any | None = None,
        decision_persistence: Any = decision_registry,
    ) -> None:
        values = (matter_lifecycle_collection, party_collection, authority_collection, engagement_collection, mandate_collection, grant_collection, grant_lifecycle_collection, acknowledgment_collection, decision_collection, principal_repository, membership_repository, role_assignment_repository, business_role_repository, authorization_evidence_registry)
        if any(value is None for value in values):
            _fail("L9C11_P21B_COLLECTION_OR_REPOSITORY_REQUIRED")
        self._matter_collection = matter_lifecycle_collection
        self._party_collection = party_collection
        self._authority_collection = authority_collection
        self._engagement_collection = engagement_collection
        self._mandate_collection = mandate_collection
        self._decision_collection = decision_collection
        self._principal_repository = principal_repository
        self._membership_repository = membership_repository
        self._role_assignment_repository = role_assignment_repository
        self._business_role_repository = business_role_repository
        self._authorization_evidence_registry = authorization_evidence_registry
        self._decision_persistence = decision_persistence
        self._authority_currentness = authority_currentness_composer or LegalClientMatterRepresentationAuthorityCurrentnessComposer(authority_collection=authority_collection)
        self._engagement_currentness = engagement_currentness_composer or LegalClientMatterEngagementCurrentnessComposer(engagement_collection=engagement_collection)
        self._mandate_currentness = mandate_currentness_composer or LegalClientMatterMandateCurrentnessComposer(mandate_collection=mandate_collection, grant_collection=grant_collection, grant_lifecycle_collection=grant_lifecycle_collection, matter_lifecycle_collection=matter_lifecycle_collection, acknowledgment_collection=acknowledgment_collection)

    def _matter(self, tenant: str, matter_id: str, session: Any) -> CaseMatter:
        try:
            history = matter_registry.LegalOperationsLifecycleRegistry.get_entity_history(tenant, "CaseMatter", matter_id, self._matter_collection, session=session)
            value = resolve_current_lifecycle_snapshot(history, expected_type=CaseMatter)
        except Exception as error:
            _fail("L9C11_P21B_MATTER_UNAVAILABLE", error)
        if type(value) is not CaseMatter or value.tenant_id != tenant or value.case_matter_id != matter_id:
            _fail("L9C11_P21B_MATTER_SCOPE_MISMATCH")
        if value.state is not CaseMatterState.OPEN:
            _fail("L9C11_P21B_OPEN_MATTER_REQUIRED")
        return value

    def _party(self, tenant: str, matter: CaseMatter, party_id: str, session: Any) -> LegalMatterParty:
        try:
            value = party_registry.get_party(tenant, party_id, self._party_collection, session=session)
        except Exception as error:
            _fail("L9C11_P21B_CLIENT_PARTY_UNAVAILABLE", error)
        if type(value) is not LegalMatterParty or value.tenant_id != tenant or value.case_matter_id != matter.case_matter_id or value.matter_fingerprint != matter.fingerprint or value.party_side is not LegalMatterPartySide.CLIENT_SIDE or value.matter_role is not LegalMatterPartyRole.CLIENT:
            _fail("L9C11_P21B_CLIENT_PARTY_SCOPE_MISMATCH")
        return value

    def _representative(self, tenant: str, principal_id: str, expected_role: str, session: Any) -> RoleAssignmentAuthority:
        try:
            principal = self._principal_repository.resolve(principal_id, session=session)
            membership = self._membership_repository.resolve(principal_id, tenant, session=session)
            assignments = self._role_assignment_repository.list_assignments(principal_id, tenant, session=session)
        except Exception as error:
            _fail("L9C11_P21B_REPRESENTATIVE_AUTHORITY_UNAVAILABLE", error)
        if type(principal) is not PrincipalAuthority or principal.status is not PrincipalStatus.ACTIVE:
            _fail("L9C11_P21B_REPRESENTATIVE_INACTIVE")
        if type(membership) is not TenantMembershipAuthority or membership.status is not TenantMembershipStatus.ACTIVE or membership.tenant_id != tenant:
            _fail("L9C11_P21B_REPRESENTATIVE_MEMBERSHIP_REQUIRED")
        if expected_role not in ELIGIBLE_REPRESENTATIVE_ROLES:
            _fail("L9C11_P21B_REPRESENTATIVE_ROLE_INVALID")
        eligible = tuple(value for value in assignments if type(value) is RoleAssignmentAuthority and value.principal_id == principal_id and value.tenant_id == tenant and value.status is RoleAssignmentStatus.ACTIVE and value.role_id in ELIGIBLE_REPRESENTATIVE_ROLES)
        matching = tuple(value for value in eligible if value.role_id == expected_role)
        if len(matching) != 1 or len(eligible) != 1:
            _fail("L9C11_P21B_REPRESENTATIVE_ROLE_REQUIRED")
        return matching[0]

    def issue(self, request: LegalClientMatterRepresentationFirmDecisionRequest, *, session: Any) -> LegalClientMatterRepresentationFirmDecision:
        tx = _active_transaction(session)
        if not isinstance(request, LegalClientMatterRepresentationFirmDecisionRequest):
            _fail("L9C11_P21B_REQUEST_REQUIRED")
        tenant, actor = _identity_scope(request.identity)
        if tenant != request.tenant_id or actor != request.identity.identity_id:
            _fail("L9C11_P21B_IDENTITY_SCOPE_MISMATCH")
        matter_id = _identity_text("case_matter_id", request.case_matter_id)
        party_id = _identity_text("client_party_id", request.client_party_id)
        representative_id = _identity_text("representative_principal_id", request.representative_principal_id)
        evaluated_at = _timestamp("evaluated_at", request.evaluated_at)
        scope = _scope(request.representation_scope_capabilities)
        source_reference = _text("source_evidence_reference", request.source_evidence_reference)
        source_fingerprint = _fingerprint("source_evidence_fingerprint", request.source_evidence_fingerprint)
        idempotency = _text("idempotency_key", request.idempotency_key, limit=_MAX_IDEMPOTENCY)
        try:
            decision = LegalClientMatterRepresentationFirmDecisionType(request.decision)
        except (TypeError, ValueError) as error:
            _fail("L9C11_P21B_DECISION_INVALID", error)
        matter = self._matter(tenant, matter_id, tx)
        party = self._party(tenant, matter, party_id, tx)
        try:
            p1_currentness = self._authority_currentness.compose_currentness(tenant, matter.case_matter_id, matter.fingerprint, party.party_id, party.subject_identity_fingerprint, representative_id, evaluated_at, tx)
        except Exception as error:
            _fail("L9C11_P21B_P1_CURRENTNESS_UNAVAILABLE", error)
        if not isinstance(p1_currentness, LegalClientMatterRepresentationAuthorityCurrentness) or not p1_currentness.is_currently_appointed:
            _fail("L9C11_P21B_P1_APPOINTED_REQUIRED")
        authority_id = p1_currentness.decisive_authority_id
        authority_fingerprint = p1_currentness.decisive_authority_fingerprint
        if not isinstance(authority_id, str) or not isinstance(authority_fingerprint, str):
            _fail("L9C11_P21B_P1_IDENTITY_INVALID")
        try:
            authority = authority_registry.get_representation_authority(tenant, authority_id, self._authority_collection, session=tx)
        except Exception as error:
            _fail("L9C11_P21B_P1_AUTHORITY_UNAVAILABLE", error)
        if type(authority) is not LegalClientMatterRepresentationAuthority or authority.fingerprint != authority_fingerprint or authority.tenant_id != tenant or authority.case_matter_id != matter.case_matter_id or authority.matter_fingerprint != matter.fingerprint or authority.client_party_id != party.party_id or authority.subject_reference != party.subject_reference or authority.subject_identity_fingerprint != party.subject_identity_fingerprint or authority.representative_principal_id != representative_id or authority.is_appointing is not True:
            _fail("L9C11_P21B_P1_LINEAGE_MISMATCH")
        self._representative(tenant, representative_id, authority.representative_role, tx)
        try:
            engagement_currentness = self._engagement_currentness.compose_currentness(tenant, matter.case_matter_id, matter.fingerprint, party.party_id, party.subject_identity_fingerprint, evaluated_at, tx)
        except Exception as error:
            _fail("L9C11_P21B_ENGAGEMENT_CURRENTNESS_UNAVAILABLE", error)
        _require_current(engagement_currentness, "engagement")
        engagement_id = getattr(engagement_currentness, "decisive_engagement_id", None)
        engagement_fingerprint = getattr(engagement_currentness, "decisive_engagement_fingerprint", None)
        if not isinstance(engagement_id, str) or not isinstance(engagement_fingerprint, str) or engagement_id != authority.engagement_id or engagement_fingerprint != authority.engagement_fingerprint:
            _fail("L9C11_P21B_ENGAGEMENT_LINEAGE_MISMATCH")
        try:
            engagement = engagement_registry.get_engagement(tenant, engagement_id, self._engagement_collection, session=tx)
        except Exception as error:
            _fail("L9C11_P21B_ENGAGEMENT_UNAVAILABLE", error)
        if (
            type(engagement) is not LegalClientMatterEngagement
            or engagement.fingerprint != engagement_fingerprint
            or engagement.tenant_id != tenant
            or engagement.case_matter_id != matter.case_matter_id
            or engagement.matter_fingerprint != matter.fingerprint
            or engagement.client_party_id != party.party_id
            or engagement.subject_reference != party.subject_reference
            or engagement.subject_identity_fingerprint != party.subject_identity_fingerprint
            or engagement.mandate_id != authority.mandate_id
            or engagement.mandate_fingerprint != authority.mandate_fingerprint
        ):
            _fail("L9C11_P21B_ENGAGEMENT_INVALID")
        try:
            mandate_currentness = self._mandate_currentness.compose_currentness(tenant, authority.mandate_id, evaluated_at, tx)
        except Exception as error:
            _fail("L9C11_P21B_MANDATE_CURRENTNESS_UNAVAILABLE", error)
        _require_current(mandate_currentness, "mandate")
        if getattr(mandate_currentness, "mandate_id", None) != authority.mandate_id or getattr(mandate_currentness, "mandate_fingerprint", None) != authority.mandate_fingerprint:
            _fail("L9C11_P21B_MANDATE_LINEAGE_MISMATCH")
        try:
            mandate = mandate_registry.get_mandate(tenant, authority.mandate_id, self._mandate_collection, session=tx)
        except Exception as error:
            _fail("L9C11_P21B_MANDATE_UNAVAILABLE", error)
        if (
            type(mandate) is not LegalClientMatterMandate
            or mandate.fingerprint != authority.mandate_fingerprint
            or mandate.tenant_id != tenant
            or mandate.case_matter_id != matter.case_matter_id
            or mandate.matter_fingerprint != matter.fingerprint
            or mandate.client_party_id != party.party_id
            or mandate.subject_identity_fingerprint != party.subject_identity_fingerprint
            or set(authority.mandate_capabilities) - set(mandate.capabilities)
        ):
            _fail("L9C11_P21B_MANDATE_LINEAGE_MISMATCH")
        subject = f"{SUBJECT_PREFIX}:{tenant}:{matter.case_matter_id}:{party.party_id}"
        subject_fingerprint = _canonical_digest({"tenant_id": tenant, "case_matter_id": matter.case_matter_id, "matter_fingerprint": matter.fingerprint, "client_party_id": party.party_id, "subject_reference": party.subject_reference, "subject_identity_fingerprint": party.subject_identity_fingerprint, "representation_authority_id": authority.authority_id, "representation_authority_fingerprint": authority.fingerprint, "representative_principal_id": authority.representative_principal_id, "representative_role": authority.representative_role, "decision": decision.value, "representation_scope_capabilities": list(scope), "idempotency_key": idempotency})
        authorization_idempotency = f"{SUBJECT_PREFIX}:iam:{_canonical_digest({'tenant_id': tenant, 'idempotency_key': idempotency})}"
        try:
            authorization = self._authorization_evidence_registry.issue(tenant_id=tenant, principal_id=actor, operation=OPERATION, permission=PERMISSION, subject_reference=subject, subject_evidence_fingerprint=subject_fingerprint, idempotency_key=authorization_idempotency, session=tx)
        except TenantAuthorizationDecisionEvidenceAuthorizationDeniedError as error:
            _fail("L9C11_P21B_ACTOR_AUTHORIZATION_REQUIRED", error)
        except TenantAuthorizationDecisionEvidenceTransactionRequiredError as error:
            _fail("L9C11_P21B_ACTIVE_TRANSACTION_REQUIRED", error)
        except TenantAuthorizationDecisionEvidenceConflictError as error:
            _fail("L9C11_P21B_IDEMPOTENCY_CONFLICT", error)
        except (TenantAuthorizationDecisionEvidencePersistenceError, TenantAuthorizationDecisionEvidenceRegistryError) as error:
            _fail("L9C11_P21B_AUTHORIZATION_EVIDENCE_UNAVAILABLE", error)
        if (
            authorization.tenant_id != tenant
            or authorization.principal_id != actor
            or authorization.operation != OPERATION
            or authorization.permission != PERMISSION
            or authorization.subject_reference != subject
            or authorization.subject_evidence_fingerprint != subject_fingerprint
            or authorization.authorization_role not in {"LEGAL_PARTNER", "LEGAL_ATTORNEY"}
        ):
            _fail("L9C11_P21B_AUTHORIZATION_EVIDENCE_CORRELATION_INVALID")
        try:
            value = LegalClientMatterRepresentationFirmDecision.from_client_authority(client_authority=authority, decision=decision, representation_scope_capabilities=scope, decision_actor_principal_id=actor, authorization_evidence_reference=authorization.authorization_evidence_reference, authorization_evidence_fingerprint=authorization.authorization_evidence_fingerprint, source_evidence_reference=source_reference, source_evidence_fingerprint=source_fingerprint, occurred_at=authorization.authorized_at, effective_from=authorization.authorized_at, idempotency_key=idempotency)
        except LegalClientMatterRepresentationFirmDecisionError as error:
            _fail("L9C11_P21B_P2_CONSTRUCTION_FAILED", error)
        try:
            persisted = self._decision_persistence.persist_firm_decision(value, self._decision_collection, session=tx)
        except decision_registry.LegalClientMatterRepresentationFirmDecisionRegistryRetryRequiredError as error:
            _retry("L9C11_P21B_WHOLE_TRANSACTION_RETRY_REQUIRED", error)
        except decision_registry.LegalClientMatterRepresentationFirmDecisionRegistryConflictError as error:
            _fail("L9C11_P21B_IDEMPOTENCY_CONFLICT", error)
        except decision_registry.LegalClientMatterRepresentationFirmDecisionRegistryError as error:
            _fail("L9C11_P21B_P2_PERSISTENCE_FAILED", error)
        if type(persisted) is not LegalClientMatterRepresentationFirmDecision or persisted.to_dict() != value.to_dict():
            _fail("L9C11_P21B_P2_REPLAY_CORRELATION_INVALID")
        return persisted

    orchestrate = issue


def issue_client_matter_representation_firm_decision(*, orchestrator: LegalClientMatterRepresentationFirmDecisionOrchestrator, request: LegalClientMatterRepresentationFirmDecisionRequest, session: Any) -> LegalClientMatterRepresentationFirmDecision:
    """Functional boundary equivalent; transaction lifecycle remains external."""
    return orchestrator.issue(request, session=session)


__all__ = [
    "ELIGIBLE_REPRESENTATIVE_ROLES", "OPERATION", "PERMISSION", "SUBJECT_PREFIX", "VERSION",
    "LegalClientMatterRepresentationFirmDecisionOrchestrationError",
    "LegalClientMatterRepresentationFirmDecisionOrchestrationRetryRequiredError",
    "LegalClientMatterRepresentationFirmDecisionRequest",
    "LegalClientMatterRepresentationFirmDecisionOrchestrator",
    "issue_client_matter_representation_firm_decision",
]


# ARTIFACT: legal_client_matter_representation_firm_decision_orchestrator.py
# VERSION: v1.0.0-L9C11-P21B-FIRM-REPRESENTATION-DECISION-ORCHESTRATOR
# AUTHORITY BOUNDARY: firm Representation decision evidence only
# TENANT POSTURE: exact authenticated tenant and caller transaction throughout
# FAIL-CLOSED POSTURE: stale, ambiguous, divergent or unavailable authority rejects
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively
# END OF WILSY OS SOVEREIGN ARTIFACT
