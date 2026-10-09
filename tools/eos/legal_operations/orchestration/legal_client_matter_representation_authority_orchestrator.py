"""WILSY OS client-side Representation-authority orchestrator.

TITLE: WILSY OS Legal Client Matter Representation Authority Orchestrator
VERSION: v1.0.0-L9C11-P20-CLIENT-REPRESENTATION-AUTHORITY-ORCHESTRATOR
AUTHORITY: Wilsy OS Core Governance / Python EOS Legal Operations
EPITOME: Issue one tenant-scoped client self-appointment by re-reading every
         authenticated, matter, visibility, acting-capacity, Engagement,
         Mandate, representative and role prerequisite in one caller-owned
         transaction, then persisting P17 evidence and P1 authority atomically.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tools/eos/legal_operations/orchestration/legal_client_matter_representation_authority_orchestrator.py
COLLABORATION / OWNERSHIP: P1 owns immutable client appointment authority;
                            P7 owns its durability; P17/P18 own authorization
                            evidence and durability; IAM owns principal,
                            membership and role facts; currentness composers
                            own Engagement/Mandate projections. P20 composes
                            these authorities and creates no Representation,
                            firm decision, Court or financial authority.
CERTIFICATION / UPDATE DATE: 2026-09-28
CHANGELOG: v1.0.0-L9C11-P20 establishes caller-owned transaction orchestration,
           authenticated LEGAL_CLIENT self appointment, exact OPEN matter and
           client-party binding, ACTIVE visibility and SELF capacity checks,
           certified Engagement/Mandate currentness consumption, deterministic
           internal attorney/partner selection, P17 then P1 persistence, exact
           replay and divergent-idempotency fail-closed behavior. No new IAM
           permission, delegation, assignment, professional-admission, Court,
           Representation-formation or financial authority is introduced.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2; ISO 27001.
SECURITY / PRIVACY POSTURE: Tenant and principal identity come only from the
                             authenticated SovereignIdentity and canonical
                             repositories. Caller claims never supply role,
                             status, fingerprints, currentness or visibility.
TENANT BOUNDARY: Every read and write is bound to request tenant and the exact
                 caller session; representatives must be internal ACTIVE
                 members of that same tenant.
AUTHORITY BOUNDARY: Client-side appointment prerequisite only. This module
                    does not accept delegated actors, create firm acceptance,
                    assert professional admission, form Representation, grant
                    Court authority or authorize financial execution.
FINANCIAL AUTHORITY BOUNDARY: None; Kennel EOS remains exclusive for financial
                              execution and settlement.
TRANSACTION BOUNDARY: The caller supplies and owns an already-active Mongo
                      transaction. P20 never starts, commits, aborts or retries
                      a transaction and forwards the identical session to every
                      source read and both registry writes.
FAIL-CLOSED DECLARATION: Missing/inactive/ambiguous/divergent/stale source
                         evidence, scope widening, wrong tenant, unsupported
                         role, inactive visibility/capacity, non-current
                         prerequisites and persistence uncertainty reject.
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any, Final, NoReturn, Protocol, cast

from tools.eos.auth.identity import SovereignIdentity
from tools.eos.auth.principal_authority import PrincipalAuthority
from tools.eos.auth.principal_status import PrincipalStatus
from tools.eos.auth.role_assignment import RoleAssignmentAuthority
from tools.eos.auth.role_assignment import RoleAssignmentStatus
from tools.eos.auth.roles import VERSION as ROLE_POLICY_VERSION
from tools.eos.auth.tenant_authorization import (
    TenantAuthorizationReason,
    authorize_tenant_operation,
)
from tools.eos.auth.tenant_membership import TenantMembershipStatus
from tools.eos.auth.tenant_membership import TenantMembershipAuthority
from tools.eos.legal_operations.domain.legal_client_acting_capacity import (
    LegalClientActingCapacity,
    LegalClientActingCapacityType,
)
from tools.eos.legal_operations.domain.legal_client_matter_engagement import LegalClientMatterEngagement
from tools.eos.legal_operations.domain.legal_client_matter_mandate import LegalClientMatterMandate
from tools.eos.legal_operations.domain.legal_client_matter_representation_authority import (
    LegalClientMatterRepresentationAuthority,
    LegalClientMatterRepresentationAuthorityDecision,
)
from tools.eos.legal_operations.domain.legal_client_matter_representation_authorization_evidence import (
    ELIGIBLE_REPRESENTATIVE_ROLES,
    LegalClientMatterRepresentationAuthorizationDecision,
    LegalClientMatterRepresentationAuthorizationEvidence,
)
from tools.eos.legal_operations.domain.legal_matter_party import (
    LegalMatterParty,
    LegalMatterPartyRole,
    LegalMatterPartySide,
)
from tools.eos.legal_operations.domain.legal_operations_current_projection import (
    resolve_current_lifecycle_snapshot,
)
from tools.eos.legal_operations.domain.legal_operations_lifecycle import (
    CaseMatter,
    CaseMatterState,
)
from tools.eos.legal_operations.orchestration.legal_client_matter_engagement_currentness_composer import (
    LegalClientMatterEngagementCurrentnessComposer,
)
from tools.eos.legal_operations.orchestration.legal_client_matter_mandate_currentness_composer import (
    LegalClientMatterMandateCurrentnessComposer,
)
from tools.eos.legal_operations.registry import (
    legal_client_acting_capacity_registry as capacity_registry,
    legal_client_matter_engagement_registry as engagement_registry,
    legal_client_matter_representation_authority_registry as authority_registry,
    legal_client_matter_representation_authorization_evidence_registry as evidence_registry,
    legal_client_matter_visibility_registry as visibility_registry,
    legal_client_matter_mandate_registry as mandate_registry,
    legal_matter_party_registry as party_registry,
    legal_operations_lifecycle_registry as matter_registry,
)
from tools.eos.legal_operations.domain.legal_client_matter_visibility_binding import LegalClientMatterVisibilityBinding


VERSION: Final[str] = "v1.0.0-L9C11-P20-CLIENT-REPRESENTATION-AUTHORITY-ORCHESTRATOR"
PERMISSION: Final[str] = "legal_operations:client_matter:read"
OPERATION: Final[str] = "legal_client_matter_read"
ELIGIBILITY_POLICY_VERSION: Final[str] = f"roles:{ROLE_POLICY_VERSION}"
UTC = timezone.utc


class LegalClientMatterRepresentationAuthorityOrchestrationError(RuntimeError):
    """Stable non-sensitive P20 failure; no supplied values are echoed."""

    def __init__(self, code: str) -> None:
        self.code = code
        super().__init__(code)


class LegalClientMatterRepresentationAuthorityOrchestrationRetryRequiredError(
    LegalClientMatterRepresentationAuthorityOrchestrationError
):
    """A caller transaction must be restarted after a registry race."""


class _EvidenceRegistry(Protocol):
    def persist_authorization_evidence(self, value: object, collection: Any, *, session: Any) -> object: ...


class _AuthorityRegistry(Protocol):
    def persist_representation_authority(self, value: object, collection: Any, *, session: Any) -> object: ...


def _fail(code: str, cause: BaseException | None = None) -> NoReturn:
    error = LegalClientMatterRepresentationAuthorityOrchestrationError(code)
    if cause is None:
        raise error
    raise error from cause


def _retry(code: str, cause: BaseException) -> NoReturn:
    raise LegalClientMatterRepresentationAuthorityOrchestrationRetryRequiredError(code) from cause


def _text(name: str, value: object) -> str:
    if not isinstance(value, str) or not value or value != value.strip():
        _fail(f"L9C11_P20_{name.upper()}_INVALID")
    return value


def _timestamp(name: str, value: object) -> datetime:
    parsed = value
    if isinstance(parsed, str):
        try:
            parsed = datetime.fromisoformat(parsed.replace("Z", "+00:00"))
        except ValueError as error:
            _fail(f"L9C11_P20_{name.upper()}_INVALID", error)
    if not isinstance(parsed, datetime) or parsed.tzinfo is None or parsed.utcoffset() is None:
        _fail(f"L9C11_P20_{name.upper()}_INVALID")
    return parsed.astimezone(UTC)


def _scope(value: object) -> tuple[str, ...]:
    if isinstance(value, str) or not isinstance(value, (tuple, list, set, frozenset)):
        _fail("L9C11_P20_SCOPE_INVALID")
    labels: set[str] = set()
    for item in value:
        label = getattr(item, "value", item)
        if not isinstance(label, str) or not label or label != label.strip():
            _fail("L9C11_P20_SCOPE_INVALID")
        labels.add(label.upper())
    if not labels:
        _fail("L9C11_P20_SCOPE_REQUIRED")
    return tuple(sorted(labels))


def _revision(name: str, value: object) -> int:
    if isinstance(value, bool) or not isinstance(value, int) or value < 0:
        _fail(f"L9C11_P20_{name.upper()}_INVALID")
    return value


def _active_transaction(session: Any) -> Any:
    if session is None:
        _fail("L9C11_P20_ACTIVE_TRANSACTION_REQUIRED")
    marker = getattr(session, "in_transaction", None)
    try:
        active = marker() if callable(marker) else marker
    except Exception as error:
        _fail("L9C11_P20_ACTIVE_TRANSACTION_REQUIRED", error)
    if active is not True:
        _fail("L9C11_P20_ACTIVE_TRANSACTION_REQUIRED")
    return session


def _identity(identity: SovereignIdentity) -> tuple[str, str]:
    if not isinstance(identity, SovereignIdentity):
        _fail("L9C11_P20_AUTHENTICATED_IDENTITY_REQUIRED")
    if identity.status is not PrincipalStatus.ACTIVE:
        _fail("L9C11_P20_APPOINTING_PRINCIPAL_INACTIVE")
    return _text("tenant_id", identity.tenant_id), _text("principal_id", identity.identity_id)


def _current(value: object, name: str) -> None:
    state = getattr(value, "state", None)
    if getattr(value, "is_current", False) is not True and getattr(state, "value", state) != "CURRENT":
        _fail(f"L9C11_P20_{name.upper()}_CURRENT_REQUIRED")


@dataclass(frozen=True, slots=True)
class LegalClientMatterRepresentationAuthorityRequest:
    """Immutable scalar command; authoritative fields are never caller claims."""

    tenant_id: str
    case_matter_id: str
    client_party_id: str
    identity: SovereignIdentity
    representative_principal_id: str
    mandate_id: str
    representation_scope_capabilities: tuple[str, ...] | list[str]
    occurred_at: datetime
    effective_from: datetime
    idempotency_key: str
    source_evidence_reference: str
    source_evidence_fingerprint: str
    subject_reference: str | None = None
    effective_until: datetime | None = None

    def __post_init__(self) -> None:
        """Validate only command shape; all authority snapshots are re-read."""
        for name, value in (
            ("tenant_id", self.tenant_id),
            ("case_matter_id", self.case_matter_id),
            ("client_party_id", self.client_party_id),
            ("representative_principal_id", self.representative_principal_id),
            ("mandate_id", self.mandate_id),
            ("idempotency_key", self.idempotency_key),
            ("source_evidence_reference", self.source_evidence_reference),
            ("source_evidence_fingerprint", self.source_evidence_fingerprint),
        ):
            _text(name, value)
        if not isinstance(self.identity, SovereignIdentity):
            _fail("L9C11_P20_AUTHENTICATED_IDENTITY_REQUIRED")
        object.__setattr__(self, "representation_scope_capabilities", _scope(self.representation_scope_capabilities))
        object.__setattr__(self, "occurred_at", _timestamp("occurred_at", self.occurred_at))
        object.__setattr__(self, "effective_from", _timestamp("effective_from", self.effective_from))
        if self.effective_until is not None:
            object.__setattr__(self, "effective_until", _timestamp("effective_until", self.effective_until))
        if self.effective_from < self.occurred_at:
            _fail("L9C11_P20_EFFECTIVE_FROM_BEFORE_OCCURRED")
        if self.effective_until is not None and self.effective_until <= self.effective_from:
            _fail("L9C11_P20_EFFECTIVE_UNTIL_INVALID")


class LegalClientMatterRepresentationAuthorityOrchestrator:
    """Compose and persist one client self-appointment in caller transaction."""

    def __init__(
        self,
        *,
        matter_lifecycle_collection: Any,
        visibility_collection: Any,
        party_collection: Any,
        capacity_collection: Any,
        engagement_collection: Any,
        mandate_collection: Any,
        grant_collection: Any,
        grant_lifecycle_collection: Any,
        acknowledgment_collection: Any,
        evidence_collection: Any,
        authority_collection: Any,
        principal_repository: Any,
        membership_repository: Any,
        business_role_repository: Any,
        role_assignment_repository: Any,
        engagement_currentness_composer: Any | None = None,
        mandate_currentness_composer: Any | None = None,
        evidence_persistence: Any = evidence_registry,
        authority_persistence: Any = authority_registry,
    ) -> None:
        """Bind canonical collections and repositories without resolving them."""
        values = (
            matter_lifecycle_collection, visibility_collection, party_collection,
            capacity_collection, engagement_collection, mandate_collection,
            grant_collection, grant_lifecycle_collection, acknowledgment_collection,
            evidence_collection, authority_collection, principal_repository,
            membership_repository, business_role_repository, role_assignment_repository,
        )
        if any(value is None for value in values):
            _fail("L9C11_P20_COLLECTION_OR_REPOSITORY_REQUIRED")
        self._matter_collection = matter_lifecycle_collection
        self._visibility_collection = visibility_collection
        self._party_collection = party_collection
        self._capacity_collection = capacity_collection
        self._engagement_collection = engagement_collection
        self._mandate_collection = mandate_collection
        self._evidence_collection = evidence_collection
        self._authority_collection = authority_collection
        self._principal_repository = principal_repository
        self._membership_repository = membership_repository
        self._business_role_repository = business_role_repository
        self._role_assignment_repository = role_assignment_repository
        self._evidence_persistence = evidence_persistence
        self._authority_persistence = authority_persistence
        self._engagement_currentness = engagement_currentness_composer or LegalClientMatterEngagementCurrentnessComposer(
            engagement_collection=engagement_collection
        )
        self._mandate_currentness = mandate_currentness_composer or LegalClientMatterMandateCurrentnessComposer(
            mandate_collection=mandate_collection,
            grant_collection=grant_collection,
            grant_lifecycle_collection=grant_lifecycle_collection,
            matter_lifecycle_collection=matter_lifecycle_collection,
            acknowledgment_collection=acknowledgment_collection,
        )

    @staticmethod
    def _resolve(repository: Any, *args: object, session: Any) -> object:
        """Resolve one canonical repository fact with the exact caller session."""
        try:
            return repository.resolve(*args, session=session)
        except Exception as error:
            _fail("L9C11_P20_IAM_SOURCE_UNAVAILABLE", error)

    def _authorize_client(self, tenant: str, principal: str, session: Any) -> tuple[PrincipalAuthority, TenantMembershipAuthority, RoleAssignmentAuthority]:
        """Require active principal, membership and canonical LEGAL_CLIENT role."""
        try:
            decision = authorize_tenant_operation(
                principal_id=principal,
                tenant_id=tenant,
                permission_id=PERMISSION,
                operation=OPERATION,
                principal_repository=self._principal_repository,
                membership_repository=self._membership_repository,
                business_role_repository=self._business_role_repository,
                role_assignment_repository=self._role_assignment_repository,
                session=session,
            )
        except Exception as error:
            _fail("L9C11_P20_CLIENT_AUTHORIZATION_UNAVAILABLE", error)
        if (
            decision.authorized is not True
            or decision.reason is not TenantAuthorizationReason.AUTHORIZED
            or decision.business_role != "tenant_legal_client"
            or decision.authorization_role != "LEGAL_CLIENT"
        ):
            _fail("L9C11_P20_LEGAL_CLIENT_CONTEXT_REQUIRED")
        principal_value = cast(PrincipalAuthority, self._resolve(self._principal_repository, principal, session=session))
        membership = cast(TenantMembershipAuthority, self._resolve(self._membership_repository, principal, tenant, session=session))
        role = cast(RoleAssignmentAuthority, self._resolve(self._role_assignment_repository, principal, tenant, "LEGAL_CLIENT", session=session))
        if getattr(principal_value, "status", None) is not PrincipalStatus.ACTIVE:
            _fail("L9C11_P20_APPOINTING_PRINCIPAL_INACTIVE")
        if getattr(membership, "status", None) is not TenantMembershipStatus.ACTIVE:
            _fail("L9C11_P20_APPOINTING_MEMBERSHIP_INACTIVE")
        if (
            getattr(role, "status", None) is not RoleAssignmentStatus.ACTIVE
            or getattr(role, "role_id", None) != "LEGAL_CLIENT"
        ):
            _fail("L9C11_P20_LEGAL_CLIENT_ROLE_REQUIRED")
        return principal_value, membership, role

    def _matter(self, tenant: str, matter_id: str, session: Any) -> CaseMatter:
        try:
            history = matter_registry.LegalOperationsLifecycleRegistry.get_entity_history(
                tenant, "CaseMatter", matter_id, self._matter_collection, session=session
            )
            matter = resolve_current_lifecycle_snapshot(history, expected_type=CaseMatter)
        except Exception as error:
            _fail("L9C11_P20_MATTER_UNAVAILABLE", error)
        if type(matter) is not CaseMatter or matter.state is not CaseMatterState.OPEN:
            _fail("L9C11_P20_OPEN_MATTER_REQUIRED")
        if matter.tenant_id != tenant or matter.case_matter_id != matter_id:
            _fail("L9C11_P20_MATTER_SCOPE_MISMATCH")
        return matter

    def _party(self, request: LegalClientMatterRepresentationAuthorityRequest, matter: CaseMatter, session: Any) -> LegalMatterParty:
        try:
            parties = party_registry.list_matter_parties(
                request.tenant_id, matter.case_matter_id, self._party_collection, session=session
            )
        except Exception as error:
            _fail("L9C11_P20_CLIENT_PARTY_UNAVAILABLE", error)
        matches = tuple(value for value in parties if getattr(value, "party_id", None) == request.client_party_id)
        if len(matches) != 1:
            _fail("L9C11_P20_CLIENT_PARTY_REQUIRED")
        party = matches[0]
        if (
            getattr(party, "tenant_id", None) != request.tenant_id
            or getattr(party, "case_matter_id", None) != matter.case_matter_id
            or getattr(party, "matter_fingerprint", None) != matter.fingerprint
            or getattr(getattr(party, "matter_role", None), "value", getattr(party, "matter_role", None)) != LegalMatterPartyRole.CLIENT.value
            or getattr(getattr(party, "party_side", None), "value", getattr(party, "party_side", None)) != LegalMatterPartySide.CLIENT_SIDE.value
        ):
            _fail("L9C11_P20_CLIENT_PARTY_SCOPE_MISMATCH")
        if request.subject_reference is not None and party.subject_reference != request.subject_reference:
            _fail("L9C11_P20_SUBJECT_SCOPE_MISMATCH")
        return party

    def _capacity(self, tenant: str, principal: str, matter: CaseMatter, party: LegalMatterParty, at: datetime, session: Any) -> LegalClientActingCapacity:
        try:
            values = capacity_registry.list_valid_capacities_at(
                tenant, matter.case_matter_id, at, self._capacity_collection, session=session
            )
        except Exception as error:
            _fail("L9C11_P20_ACTING_CAPACITY_UNAVAILABLE", error)
        matches = tuple(
            value for value in values
            if getattr(value, "principal_id", None) == principal
            and getattr(value, "party_id", None) == getattr(party, "party_id", None)
            and getattr(value, "tenant_id", None) == tenant
            and getattr(value, "case_matter_id", None) == matter.case_matter_id
            and getattr(value, "matter_fingerprint", None) == matter.fingerprint
            and getattr(value, "subject_reference", None) == getattr(party, "subject_reference", None)
            and getattr(value, "subject_identity_fingerprint", None) == getattr(party, "subject_identity_fingerprint", None)
            and getattr(getattr(value, "capacity_type", None), "value", getattr(value, "capacity_type", None)) == LegalClientActingCapacityType.SELF.value
        )
        if len(matches) != 1:
            _fail("L9C11_P20_SELF_ACTING_CAPACITY_REQUIRED")
        return matches[0]

    def _current_lineage(self, request: LegalClientMatterRepresentationAuthorityRequest, matter: CaseMatter, party: LegalMatterParty, session: Any) -> tuple[LegalClientMatterEngagement, LegalClientMatterMandate, object]:
        try:
            engagement_currentness = self._engagement_currentness.compose_currentness(
                request.tenant_id, matter.case_matter_id, matter.fingerprint,
                request.client_party_id, party.subject_identity_fingerprint,
                request.effective_from, session,
            )
        except Exception as error:
            _fail("L9C11_P20_ENGAGEMENT_CURRENTNESS_UNAVAILABLE", error)
        _current(engagement_currentness, "engagement")
        engagement_id = getattr(engagement_currentness, "decisive_engagement_id", None)
        engagement_fp = getattr(engagement_currentness, "decisive_engagement_fingerprint", None)
        if not isinstance(engagement_id, str) or not isinstance(engagement_fp, str):
            _fail("L9C11_P20_ENGAGEMENT_CURRENTNESS_INVALID")
        try:
            engagement = cast(LegalClientMatterEngagement, engagement_registry.get_engagement(
                request.tenant_id, engagement_id, self._engagement_collection, session=session
            ))
        except Exception as error:
            _fail("L9C11_P20_ENGAGEMENT_UNAVAILABLE", error)
        try:
            mandate_currentness = self._mandate_currentness.compose_currentness(
                request.tenant_id, request.mandate_id, request.effective_from, session
            )
        except Exception as error:
            _fail("L9C11_P20_MANDATE_CURRENTNESS_UNAVAILABLE", error)
        _current(mandate_currentness, "mandate")
        mandate_id = getattr(mandate_currentness, "mandate_id", None)
        mandate_fp = getattr(mandate_currentness, "mandate_fingerprint", None)
        if mandate_id != request.mandate_id or not isinstance(mandate_fp, str):
            _fail("L9C11_P20_MANDATE_CURRENTNESS_INVALID")
        try:
            mandate = cast(LegalClientMatterMandate, mandate_registry.get_mandate(
                request.tenant_id, request.mandate_id, self._mandate_collection, session=session
            ))
        except Exception as error:
            _fail("L9C11_P20_MANDATE_UNAVAILABLE", error)
        if (
            engagement.tenant_id != request.tenant_id
            or engagement.case_matter_id != matter.case_matter_id
            or engagement.client_party_id != party.party_id
            or engagement.subject_identity_fingerprint != party.subject_identity_fingerprint
            or engagement.mandate_id != mandate.mandate_id
            or engagement.mandate_fingerprint != mandate.fingerprint
            or mandate.fingerprint != mandate_fp
        ):
            _fail("L9C11_P20_LINEAGE_SCOPE_MISMATCH")
        return engagement, mandate, engagement_currentness

    def _representative(self, tenant: str, principal_id: str, session: Any) -> tuple[PrincipalAuthority, TenantMembershipAuthority, str, RoleAssignmentAuthority]:
        principal = cast(PrincipalAuthority, self._resolve(self._principal_repository, principal_id, session=session))
        membership = cast(TenantMembershipAuthority, self._resolve(self._membership_repository, principal_id, tenant, session=session))
        if getattr(principal, "status", None) is not PrincipalStatus.ACTIVE:
            _fail("L9C11_P20_REPRESENTATIVE_INACTIVE")
        if (
            getattr(membership, "status", None) is not TenantMembershipStatus.ACTIVE
            or getattr(membership, "tenant_id", None) != tenant
        ):
            _fail("L9C11_P20_REPRESENTATIVE_MEMBERSHIP_INACTIVE")
        try:
            assignments = self._role_assignment_repository.list_assignments(
                principal_id, tenant, session=session
            )
        except Exception as error:
            _fail("L9C11_P20_REPRESENTATIVE_ROLES_UNAVAILABLE", error)
        eligible = sorted(
            {
                getattr(value, "role_id", None): value
                for value in assignments
                if getattr(value, "tenant_id", None) == tenant
                and getattr(value, "principal_id", None) == principal_id
                and getattr(value, "status", None) is RoleAssignmentStatus.ACTIVE
                and getattr(value, "role_id", None) in ELIGIBLE_REPRESENTATIVE_ROLES
            }.items(),
            key=lambda item: cast(str, item[0]),
        )
        if not eligible:
            _fail("L9C11_P20_ELIGIBLE_REPRESENTATIVE_ROLE_REQUIRED")
        role_id, assignment = eligible[0]
        return principal, membership, cast(str, role_id), cast(RoleAssignmentAuthority, assignment)

    def issue(self, request: LegalClientMatterRepresentationAuthorityRequest, *, session: Any) -> LegalClientMatterRepresentationAuthority:
        """Issue or exactly replay P17 evidence and P1 authority."""
        tx = _active_transaction(session)
        if not isinstance(request, LegalClientMatterRepresentationAuthorityRequest):
            _fail("L9C11_P20_REQUEST_REQUIRED")
        identity_tenant, appointing = _identity(request.identity)
        if identity_tenant != request.tenant_id:
            _fail("L9C11_P20_TENANT_IDENTITY_MISMATCH")
        if appointing != request.identity.identity_id:
            _fail("L9C11_P20_APPOINTING_PRINCIPAL_INVALID")
        actor_principal, actor_membership, actor_role = self._authorize_client(identity_tenant, appointing, tx)
        matter = self._matter(identity_tenant, request.case_matter_id, tx)
        party = self._party(request, matter, tx)
        if appointing != request.identity.identity_id:
            _fail("L9C11_P20_SELF_ACTOR_REQUIRED")
        visibility = self._require_visibility(identity_tenant, appointing, matter.case_matter_id, matter.fingerprint, tx)
        capacity = self._capacity(identity_tenant, appointing, matter, party, request.effective_from, tx)
        engagement, mandate, _ = self._current_lineage(request, matter, party, tx)
        representative, representative_membership, representative_role, representative_assignment = self._representative(
            identity_tenant, request.representative_principal_id, tx
        )
        try:
            evidence = LegalClientMatterRepresentationAuthorizationEvidence(
                tenant_id=identity_tenant,
                case_matter_id=matter.case_matter_id,
                matter_fingerprint=matter.fingerprint,
                client_party_id=party.party_id,
                subject_reference=party.subject_reference,
                subject_identity_fingerprint=party.subject_identity_fingerprint,
                client_subject_principal_id=appointing,
                appointing_principal_id=appointing,
                appointing_principal_status=actor_principal.status,
                appointing_membership_status=actor_membership.status,
                appointing_membership_revision=actor_membership.revision,
                appointing_role="LEGAL_CLIENT",
                appointing_role_assignment_revision=_revision("appointing_role_assignment_revision", actor_role.revision),
                client_visibility_reference=visibility.binding_identity,
                client_visibility_fingerprint=visibility.fingerprint,
                client_visibility_status=visibility.status.value,
                acting_capacity_id=capacity.capacity_id,
                acting_capacity_fingerprint=capacity.fingerprint,
                acting_capacity_type=capacity.capacity_type,
                engagement_id=engagement.engagement_id,
                engagement_fingerprint=engagement.fingerprint,
                mandate_id=mandate.mandate_id,
                mandate_fingerprint=mandate.fingerprint,
                mandate_scope_reference=mandate.scope_reference,
                mandate_scope_fingerprint=mandate.scope_fingerprint,
                mandate_capabilities=mandate.capabilities,
                representative_principal_id=representative.principal_id,
                representative_principal_status=representative.status,
                representative_membership_status=representative_membership.status,
                representative_membership_revision=representative_membership.revision,
                representative_role_assignment_revision=_revision("representative_role_assignment_revision", representative_assignment.revision),
                representative_role=representative_role,
                representative_eligibility_policy_version=ELIGIBILITY_POLICY_VERSION,
                representation_scope_capabilities=request.representation_scope_capabilities,
                decision=LegalClientMatterRepresentationAuthorizationDecision.AUTHORIZED,
                source_evidence_reference=request.source_evidence_reference,
                source_evidence_fingerprint=request.source_evidence_fingerprint,
                occurred_at=request.occurred_at,
                effective_from=request.effective_from,
                idempotency_key=request.idempotency_key,
            )
        except Exception as error:
            _fail("L9C11_P20_EVIDENCE_CONSTRUCTION_FAILED", error)
        try:
            persisted_evidence = self._evidence_persistence.persist_authorization_evidence(
                evidence, self._evidence_collection, session=tx
            )
        except evidence_registry.LegalClientMatterRepresentationAuthorizationEvidenceRegistryRetryRequiredError as error:
            _retry("L9C11_P20_EVIDENCE_RETRY_REQUIRED", error)
        except evidence_registry.LegalClientMatterRepresentationAuthorizationEvidenceRegistryError as error:
            _fail("L9C11_P20_EVIDENCE_PERSISTENCE_FAILED", error)
        if not isinstance(persisted_evidence, LegalClientMatterRepresentationAuthorizationEvidence) or persisted_evidence.to_dict() != evidence.to_dict():
            _fail("L9C11_P20_EVIDENCE_REPLAY_CORRELATION_INVALID")
        authority_id = f"representation-authority:{evidence.fingerprint}"
        try:
            authority = LegalClientMatterRepresentationAuthority.from_canonical(
                authority_id=authority_id,
                engagement=engagement,
                mandate=mandate,
                acting_capacity=capacity,
                representative_principal_id=representative.principal_id,
                representative_role=representative_role,
                representation_scope_capabilities=request.representation_scope_capabilities,
                decision=LegalClientMatterRepresentationAuthorityDecision.APPOINTED,
                appointing_principal_id=appointing,
                source_evidence_reference=request.source_evidence_reference,
                source_evidence_fingerprint=request.source_evidence_fingerprint,
                authorization_evidence_reference=evidence.evidence_id,
                authorization_evidence_fingerprint=evidence.fingerprint,
                occurred_at=request.occurred_at,
                effective_from=request.effective_from,
                effective_until=request.effective_until,
                idempotency_key=request.idempotency_key,
            )
        except Exception as error:
            _fail("L9C11_P20_AUTHORITY_CONSTRUCTION_FAILED", error)
        try:
            persisted_authority = self._authority_persistence.persist_representation_authority(
                authority, self._authority_collection, session=tx
            )
        except authority_registry.LegalClientMatterRepresentationAuthorityRegistryRetryRequiredError as error:
            _retry("L9C11_P20_AUTHORITY_RETRY_REQUIRED", error)
        except authority_registry.LegalClientMatterRepresentationAuthorityRegistryError as error:
            _fail("L9C11_P20_AUTHORITY_PERSISTENCE_FAILED", error)
        if not isinstance(persisted_authority, LegalClientMatterRepresentationAuthority) or persisted_authority.to_dict() != authority.to_dict():
            _fail("L9C11_P20_AUTHORITY_REPLAY_CORRELATION_INVALID")
        return persisted_authority

    orchestrate = issue

    def _require_visibility(self, tenant: str, principal: str, matter_id: str, matter_fp: str, session: Any) -> LegalClientMatterVisibilityBinding:
        try:
            value = cast(LegalClientMatterVisibilityBinding, visibility_registry.LegalClientMatterVisibilityRegistry.resolve_current_active(
                tenant, principal, matter_id, self._visibility_collection, session=session
            ))
        except Exception as error:
            _fail("L9C11_P20_ACTIVE_VISIBILITY_REQUIRED", error)
        if (
            value.tenant_id != tenant
            or value.client_principal_id != principal
            or value.case_matter_id != matter_id
            or value.source_case_matter_fingerprint != matter_fp
            or getattr(value.status, "value", value.status) != "ACTIVE"
        ):
            _fail("L9C11_P20_VISIBILITY_SCOPE_MISMATCH")
        return value


def issue_client_representation_authority(
    *,
    orchestrator: LegalClientMatterRepresentationAuthorityOrchestrator,
    request: LegalClientMatterRepresentationAuthorityRequest,
    session: Any,
) -> LegalClientMatterRepresentationAuthority:
    """Functional boundary equivalent; transaction lifecycle remains caller-owned."""
    return orchestrator.issue(request, session=session)


__all__ = [
    "ELIGIBILITY_POLICY_VERSION",
    "OPERATION",
    "PERMISSION",
    "VERSION",
    "LegalClientMatterRepresentationAuthorityOrchestrationError",
    "LegalClientMatterRepresentationAuthorityOrchestrationRetryRequiredError",
    "LegalClientMatterRepresentationAuthorityOrchestrator",
    "LegalClientMatterRepresentationAuthorityRequest",
    "issue_client_representation_authority",
]


# ARTIFACT: legal_client_matter_representation_authority_orchestrator.py
# VERSION: v1.0.0-L9C11-P20-CLIENT-REPRESENTATION-AUTHORITY-ORCHESTRATOR
# AUTHORITY BOUNDARY: client self-appointment orchestration only
# TENANT POSTURE: exact authenticated tenant, matter, client party, visibility and internal representative membership
# FAIL-CLOSED POSTURE: no active transaction, stale/currentness, role, scope, replay or persistence uncertainty succeeds
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively
# END OF WILSY OS SOVEREIGN ARTIFACT
