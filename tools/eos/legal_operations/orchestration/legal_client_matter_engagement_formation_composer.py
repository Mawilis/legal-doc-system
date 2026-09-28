"""WILSY OS internal Engagement-formation orchestration boundary.

TITLE: WILSY OS Legal Client Matter Engagement Formation Composer
VERSION: v1.0.0-L9C10-P5-ENGAGEMENT-FORMATION-COMPOSER
AUTHORITY: Wilsy OS Core Governance / Python EOS Legal Operations
EPITOME: Re-read exact canonical matter, party, acceptance, instrument,
         conflict, mandate and firm-decision evidence at one caller-supplied
         instant, then construct and persist one immutable Engagement.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tools/eos/legal_operations/orchestration/legal_client_matter_engagement_formation_composer.py
COLLABORATION / OWNERSHIP: Domain objects own semantic validation; lifecycle,
                            currentness and evidence registries own durable
                            truth; the Engagement registry owns append-only
                            persistence. This module owns orchestration only.
CERTIFICATION / UPDATE DATE: 2026-09-28
CHANGELOG: v1.0.0-L9C10-P5 establishes exact tenant/principal binding,
           caller-owned transaction/session propagation, one explicit shared
           evaluation instant, exact prerequisite lineage, deterministic
           Engagement identity, and one registry write/replay boundary. It
           creates no new IAM, HTTP, UI, lifecycle/currentness or finance.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2; ISO 27001.
SECURITY / PRIVACY POSTURE: Inputs are bounded opaque identifiers and an
                             active identity. Errors expose stable codes only;
                             no raw BSON, PII, credentials or authorization
                             internals are returned.
TENANT BOUNDARY: Tenant derives only from active SovereignIdentity. Every
                 read and the final write is exact-tenant and uses the same
                 caller session; no cross-tenant fallback exists.
AUTHORITY BOUNDARY: Formation evidence orchestration only. No permission
                    decision, role grant, IAM evidence, representation,
                    Court, lifecycle/currentness persistence or delivery.
FINANCIAL AUTHORITY BOUNDARY: No billing, payment, settlement or execution;
                              Kennel EOS remains exclusive.
TRANSACTION BOUNDARY: Caller supplies and owns an active transaction. This
                      module never starts, commits, aborts or retries it.
FAIL-CLOSED DECLARATION: Missing, corrupt, stale, ambiguous or divergent
                         prerequisites reject without arbitrary selection,
                         clock reads, fallback or partial persistence.
"""
from __future__ import annotations

from datetime import datetime, timezone
import hashlib
import json
import re
from typing import Any, Final, NoReturn

from tools.eos.auth.identity import SovereignIdentity
from tools.eos.auth.principal_status import PrincipalStatus
from tools.eos.legal_operations.domain.legal_client_matter_acceptance_instrument_approval import (
    LegalClientMatterAcceptanceInstrumentApprovalDecision,
)
from tools.eos.legal_operations.domain.legal_client_matter_acceptance_instrument_lifecycle import (
    LegalClientMatterAcceptanceInstrumentLifecycleStatus,
)
from tools.eos.legal_operations.domain.legal_client_matter_conflict_disposition import (
    LegalClientMatterConflictDispositionType,
)
from tools.eos.legal_operations.domain.legal_client_matter_conflict_disposition_currentness import (
    LegalClientMatterConflictDispositionCurrentnessState,
)
from tools.eos.legal_operations.domain.legal_client_matter_engagement import (
    LegalClientMatterEngagement,
)
from tools.eos.legal_operations.domain.legal_client_matter_engagement_firm_decision import (
    LegalClientMatterEngagementFirmDecisionType,
)
from tools.eos.legal_operations.domain.legal_client_matter_engagement_firm_decision_currentness import (
    LegalClientMatterEngagementFirmDecisionCurrentnessState,
)
from tools.eos.legal_operations.domain.legal_client_matter_mandate_currentness import (
    LegalClientMatterMandateCurrentnessState,
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
from tools.eos.legal_operations.orchestration.legal_client_matter_conflict_disposition_currentness_composer import (
    LegalClientMatterConflictDispositionCurrentnessComposer,
    LegalClientMatterConflictDispositionCurrentnessComposerError,
)
from tools.eos.legal_operations.orchestration.legal_client_matter_engagement_firm_decision_currentness_composer import (
    LegalClientMatterEngagementFirmDecisionCurrentnessComposer,
    LegalClientMatterEngagementFirmDecisionCurrentnessComposerError,
)
from tools.eos.legal_operations.orchestration.legal_client_matter_mandate_currentness_composer import (
    LegalClientMatterMandateCurrentnessComposer,
    LegalClientMatterMandateCurrentnessComposerError,
)
from tools.eos.legal_operations.registry import (
    legal_client_acceptance_context_registry as context_registry,
    legal_client_acceptance_registry as acceptance_registry,
    legal_client_acting_capacity_registry as capacity_registry,
    legal_client_matter_acceptance_instrument_approval_registry as approval_registry,
    legal_client_matter_acceptance_instrument_lifecycle_registry as instrument_lifecycle_registry,
    legal_client_matter_acceptance_instrument_registry as instrument_registry,
    legal_client_matter_conflict_disposition_registry as disposition_registry,
    legal_client_matter_engagement_registry as engagement_registry,
    legal_client_matter_engagement_firm_decision_registry as decision_registry,
    legal_client_matter_mandate_registry as mandate_registry,
    legal_matter_party_registry as party_registry,
    legal_operations_lifecycle_registry as matter_registry,
)


VERSION: Final[str] = "v1.0.0-L9C10-P5-ENGAGEMENT-FORMATION-COMPOSER"
ENGAGEMENT_ID_PREFIX: Final[str] = "legal-client-matter-engagement"
ACCEPTANCE_ID_PREFIX: Final[str] = "LEGAL-CLIENT-ACCEPT:"
_IDENTITY: Final[re.Pattern[str]] = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._:-]{0,159}$")
_FINGERPRINT: Final[re.Pattern[str]] = re.compile(r"^[0-9a-f]{128}$")
_MAX_IDEMPOTENCY: Final[int] = 240


class LegalClientMatterEngagementFormationComposerError(RuntimeError):
    """Stable, non-sensitive fail-closed formation error."""

    def __init__(self, code: str) -> None:
        """Expose only a bounded machine-readable error code."""
        self.code = code
        super().__init__(code)


def _fail(code: str, cause: BaseException | None = None) -> NoReturn:
    """Raise one bounded error while retaining an internal technical cause."""
    error = LegalClientMatterEngagementFormationComposerError(code)
    if cause is None:
        raise error
    raise error from cause


def _active_transaction(session: Any) -> Any:
    """Require an already-active caller transaction without owning it."""
    if session is None:
        _fail("L9C10_P5_ACTIVE_TRANSACTION_REQUIRED")
    marker = getattr(session, "in_transaction", None)
    try:
        active = marker() if callable(marker) else marker
    except (AttributeError, TypeError) as error:
        _fail("L9C10_P5_ACTIVE_TRANSACTION_REQUIRED", error)
    if active is not True:
        _fail("L9C10_P5_ACTIVE_TRANSACTION_REQUIRED")
    return session


def _text(name: str, value: object, *, limit: int = 512) -> str:
    """Require bounded single-line text without coercion or trimming."""
    if (
        not isinstance(value, str)
        or not value
        or value != value.strip()
        or len(value) > limit
        or any(
            ord(character) < 32
            or 0x7F <= ord(character) <= 0x9F
            or 0xD800 <= ord(character) <= 0xDFFF
            for character in value
        )
    ):
        _fail(f"L9C10_P5_{name.upper()}_INVALID")
    return value


def _identity(name: str, value: object) -> str:
    """Require the repository's bounded opaque identity vocabulary."""
    text = _text(name, value, limit=160)
    if _IDENTITY.fullmatch(text) is None:
        _fail(f"L9C10_P5_{name.upper()}_INVALID")
    return text


def _fingerprint(name: str, value: object) -> str:
    """Require a lowercase SHA3-512 fingerprint."""
    if not isinstance(value, str) or _FINGERPRINT.fullmatch(value) is None:
        _fail(f"L9C10_P5_{name.upper()}_INVALID")
    return value


def _tenant_and_principal(identity: object) -> tuple[str, str]:
    """Derive tenant and principal only from an active authenticated projection."""
    if not isinstance(identity, SovereignIdentity):
        _fail("L9C10_P5_IDENTITY_REQUIRED")
    if identity.status is not PrincipalStatus.ACTIVE:
        _fail("L9C10_P5_PRINCIPAL_INACTIVE")
    return (
        _identity("tenant_id", identity.tenant_id),
        _identity("principal_id", identity.identity_id),
    )


def _evaluated_at(value: object) -> datetime:
    """Require one explicit aware instant and normalize it once to UTC."""
    if not isinstance(value, datetime) or value.tzinfo is None or value.utcoffset() is None:
        _fail("L9C10_P5_EVALUATED_AT_INVALID")
    return value.astimezone(timezone.utc)


def _idempotency(value: object) -> str:
    """Require a bounded, stable idempotency key."""
    return _text("idempotency_key", value, limit=_MAX_IDEMPOTENCY)


def _state(value: object) -> str:
    """Render enum state without exposing arbitrary object representations."""
    label = getattr(value, "value", value)
    return label if isinstance(label, str) else "INVALID"


def _formation_id(
    *,
    tenant_id: str,
    case_matter_id: str,
    client_party_id: str,
    client_acceptance_fingerprint: str,
    mandate_fingerprint: str,
    conflict_disposition_fingerprint: str,
    firm_decision_fingerprint: str,
    idempotency_key: str,
) -> str:
    """Derive deterministic identity from the complete material intent."""
    payload = {
        "tenant_id": tenant_id,
        "case_matter_id": case_matter_id,
        "client_party_id": client_party_id,
        "client_acceptance_fingerprint": client_acceptance_fingerprint,
        "mandate_fingerprint": mandate_fingerprint,
        "conflict_disposition_fingerprint": conflict_disposition_fingerprint,
        "firm_decision_fingerprint": firm_decision_fingerprint,
        "idempotency_key": idempotency_key,
    }
    digest = hashlib.sha3_512(
        json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")
    ).hexdigest()[:48]
    return f"{ENGAGEMENT_ID_PREFIX}:{digest}"


def _case_matter(*, tenant: str, matter_id: str, collection: Any, session: Any) -> CaseMatter:
    """Resolve the exact current OPEN CaseMatter snapshot."""
    if collection is None:
        _fail("L9C10_P5_CASE_MATTER_COLLECTION_REQUIRED")
    try:
        history = matter_registry.LegalOperationsLifecycleRegistry.get_entity_history(
            tenant, "CaseMatter", matter_id, collection, session=session
        )
        value = resolve_current_lifecycle_snapshot(history, expected_type=CaseMatter)
    except Exception as error:
        _fail("L9C10_P5_CASE_MATTER_UNAVAILABLE", error)
    if type(value) is not CaseMatter:
        _fail("L9C10_P5_CASE_MATTER_INVALID")
    if value.tenant_id != tenant or value.case_matter_id != matter_id:
        _fail("L9C10_P5_CASE_MATTER_SCOPE_MISMATCH")
    if value.state is not CaseMatterState.OPEN:
        _fail("L9C10_P5_CASE_MATTER_NOT_OPEN")
    return value


def _context_id(acceptance_id: str) -> str:
    """Derive the immutable acceptance-context identity from acceptance ID."""
    if not acceptance_id.startswith(ACCEPTANCE_ID_PREFIX):
        _fail("L9C10_P5_ACCEPTANCE_CONTEXT_LINEAGE_INVALID")
    return _identity("acceptance_context_id", acceptance_id[len(ACCEPTANCE_ID_PREFIX) :])


def _require_collection(name: str, value: Any) -> Any:
    """Reject missing explicit dependency handles before any reads."""
    if value is None:
        _fail(f"L9C10_P5_{name.upper()}_COLLECTION_REQUIRED")
    return value


class LegalClientMatterEngagementFormationComposer:
    """Form one immutable Engagement from exact canonical prerequisites.

    ``compose_engagement`` accepts no caller assertions for tenant, subject,
    fingerprints, conflict state, mandate scope, decision provenance or
    effective time. It requires an active identity and transaction, performs
    all reads with that exact session, invokes published currentness
    authorities at one explicit instant, and calls the Engagement registry
    once. Transaction lifecycle, retry and final commit remain caller-owned.
    """

    def __init__(
        self,
        *,
        matter_lifecycle_collection: Any,
        party_collection: Any,
        capacity_collection: Any,
        context_collection: Any,
        acceptance_collection: Any,
        instrument_collection: Any,
        instrument_lifecycle_collection: Any,
        approval_collection: Any,
        conflict_collection: Any,
        mandate_collection: Any,
        mandate_grant_collection: Any,
        mandate_grant_lifecycle_collection: Any,
        mandate_matter_lifecycle_collection: Any,
        mandate_acknowledgment_collection: Any,
        decision_collection: Any,
        engagement_collection: Any,
    ) -> None:
        """Bind explicit canonical collection handles; never resolve a DB."""
        names = (
            ("matter_lifecycle", matter_lifecycle_collection),
            ("party", party_collection),
            ("capacity", capacity_collection),
            ("context", context_collection),
            ("acceptance", acceptance_collection),
            ("instrument", instrument_collection),
            ("instrument_lifecycle", instrument_lifecycle_collection),
            ("approval", approval_collection),
            ("conflict", conflict_collection),
            ("mandate", mandate_collection),
            ("mandate_grant", mandate_grant_collection),
            ("mandate_grant_lifecycle", mandate_grant_lifecycle_collection),
            ("mandate_matter_lifecycle", mandate_matter_lifecycle_collection),
            ("mandate_acknowledgment", mandate_acknowledgment_collection),
            ("decision", decision_collection),
            ("engagement", engagement_collection),
        )
        for name, value in names:
            _require_collection(name, value)
        self._matter_lifecycle_collection = matter_lifecycle_collection
        self._party_collection = party_collection
        self._capacity_collection = capacity_collection
        self._context_collection = context_collection
        self._acceptance_collection = acceptance_collection
        self._instrument_collection = instrument_collection
        self._instrument_lifecycle_collection = instrument_lifecycle_collection
        self._approval_collection = approval_collection
        self._conflict_collection = conflict_collection
        self._mandate_collection = mandate_collection
        self._mandate_grant_collection = mandate_grant_collection
        self._mandate_grant_lifecycle_collection = mandate_grant_lifecycle_collection
        self._mandate_matter_lifecycle_collection = mandate_matter_lifecycle_collection
        self._mandate_acknowledgment_collection = mandate_acknowledgment_collection
        self._decision_collection = decision_collection
        self._engagement_collection = engagement_collection

    def compose_engagement(
        self,
        *,
        identity: SovereignIdentity,
        case_matter_id: str,
        client_party_id: str,
        client_acceptance_id: str,
        mandate_id: str,
        idempotency_key: str,
        evaluated_at: datetime,
        session: Any,
    ) -> LegalClientMatterEngagement:
        """Construct or replay one exact Engagement formation artifact.

        The caller owns commit, abort and whole-transaction retry. All
        dependency reads and the single append/replay write receive ``session``
        unchanged. A replay is returned by the registry only when every
        canonical payload and tenant-scoped identity agrees.
        """
        tx = _active_transaction(session)
        tenant, _caller_principal = _tenant_and_principal(identity)
        matter_id = _identity("case_matter_id", case_matter_id)
        party_id = _identity("client_party_id", client_party_id)
        acceptance_id = _identity("client_acceptance_id", client_acceptance_id)
        requested_mandate_id = _identity("mandate_id", mandate_id)
        replay_key = _idempotency(idempotency_key)
        at = _evaluated_at(evaluated_at)

        matter = _case_matter(
            tenant=tenant,
            matter_id=matter_id,
            collection=self._matter_lifecycle_collection,
            session=tx,
        )
        try:
            party = party_registry.get_party(tenant, party_id, self._party_collection, session=tx)
        except Exception as error:
            _fail("L9C10_P5_PARTY_UNAVAILABLE", error)
        if type(party) is not LegalMatterParty:
            _fail("L9C10_P5_PARTY_INVALID")
        if (
            party.tenant_id != tenant
            or party.case_matter_id != matter.case_matter_id
            or party.matter_fingerprint != matter.fingerprint
            or party.party_side is not LegalMatterPartySide.CLIENT_SIDE
            or party.matter_role is not LegalMatterPartyRole.CLIENT
        ):
            _fail("L9C10_P5_PARTY_LINEAGE_INVALID")

        context_id = _context_id(acceptance_id)
        try:
            context = context_registry.get_context(tenant, context_id, self._context_collection, session=tx)
        except Exception as error:
            _fail("L9C10_P5_ACCEPTANCE_CONTEXT_UNAVAILABLE", error)
        try:
            acceptance = acceptance_registry.get_acceptance(
                tenant, acceptance_id, self._acceptance_collection, session=tx
            )
        except Exception as error:
            _fail("L9C10_P5_ACCEPTANCE_UNAVAILABLE", error)
        if (
            context.tenant_id != tenant
            or context.case_matter_id != matter.case_matter_id
            or context.matter_fingerprint != matter.fingerprint
            or context.party_id != party.party_id
            or context.subject_reference != party.subject_reference
            or context.subject_identity_fingerprint != party.subject_identity_fingerprint
            or acceptance.tenant_id != tenant
            or acceptance.case_matter_id != matter.case_matter_id
            or acceptance.matter_fingerprint != matter.fingerprint
            or acceptance.acceptance_id != acceptance_id
            or acceptance.party_id != party.party_id
            or acceptance.subject_reference != party.subject_reference
            or acceptance.subject_identity_fingerprint != party.subject_identity_fingerprint
            or acceptance.actor_principal_id != context.actor_principal_id
            or acceptance.acceptance_scope != context.acceptance_scope
            or acceptance.source_evidence_fingerprint != context.content_fingerprint
            or not acceptance.source_evidence_reference.startswith(
                f"legal-client-acceptance-context:{context.acceptance_context_id}:instrument:"
            )
        ):
            _fail("L9C10_P5_ACCEPTANCE_LINEAGE_INVALID")

        try:
            capacities = capacity_registry.list_valid_capacities_at(
                tenant,
                matter.case_matter_id,
                at,
                self._capacity_collection,
                session=tx,
            )
        except Exception as error:
            _fail("L9C10_P5_CAPACITY_UNAVAILABLE", error)
        matching_capacities = tuple(
            value
            for value in capacities
            if (
                value.tenant_id == tenant
                and value.case_matter_id == matter.case_matter_id
                and value.matter_fingerprint == matter.fingerprint
                and value.party_id == party.party_id
                and value.subject_reference == party.subject_reference
                and value.subject_identity_fingerprint == party.subject_identity_fingerprint
                and value.principal_id == context.actor_principal_id
                and value.capacity_id == context.capacity_id
                and value.fingerprint == context.capacity_fingerprint
            )
        )
        if len(matching_capacities) != 1:
            _fail("L9C10_P5_CAPACITY_NOT_EXACTLY_ONE")
        capacity = matching_capacities[0]

        try:
            instrument = instrument_registry.get_instrument(
                tenant,
                matter.case_matter_id,
                context.instrument_id,
                context.instrument_version,
                self._instrument_collection,
                session=tx,
            )
            lifecycle = instrument_lifecycle_registry.get_current_lifecycle(
                tenant,
                matter.case_matter_id,
                context.instrument_id,
                context.instrument_version,
                self._instrument_lifecycle_collection,
                session=tx,
            )
        except Exception as error:
            _fail("L9C10_P5_INSTRUMENT_UNAVAILABLE", error)
        if (
            instrument.tenant_id != tenant
            or instrument.case_matter_id != matter.case_matter_id
            or instrument.matter_fingerprint != matter.fingerprint
            or instrument.instrument_id != context.instrument_id
            or instrument.version != context.instrument_version
            or instrument.fingerprint != context.instrument_fingerprint
            or instrument.content_fingerprint != context.content_fingerprint
            or instrument.effective_from > at
            or lifecycle is None
            or lifecycle.status is not LegalClientMatterAcceptanceInstrumentLifecycleStatus.ACTIVE
            or lifecycle.instrument_fingerprint != instrument.fingerprint
            or lifecycle.occurred_at > at
        ):
            _fail("L9C10_P5_INSTRUMENT_LINEAGE_INVALID")
        try:
            approval = approval_registry.get_current_approval(
                tenant,
                matter.case_matter_id,
                instrument.instrument_id,
                instrument.version,
                instrument.fingerprint,
                instrument.content_fingerprint,
                self._approval_collection,
                at=at,
                session=tx,
            )
        except Exception as error:
            _fail("L9C10_P5_APPROVAL_UNAVAILABLE", error)
        if (
            approval is None
            or approval.decision is not LegalClientMatterAcceptanceInstrumentApprovalDecision.APPROVED
            or approval.effective_from > at
            or approval.instrument_fingerprint != instrument.fingerprint
            or approval.content_fingerprint != instrument.content_fingerprint
        ):
            _fail("L9C10_P5_APPROVAL_NOT_CURRENT")

        try:
            conflict_currentness = LegalClientMatterConflictDispositionCurrentnessComposer(
                disposition_collection=self._conflict_collection
            ).compose_currentness(
                tenant,
                matter.case_matter_id,
                matter.fingerprint,
                party.party_id,
                party.subject_identity_fingerprint,
                at,
                tx,
            )
        except LegalClientMatterConflictDispositionCurrentnessComposerError as error:
            _fail("L9C10_P5_CONFLICT_CURRENTNESS_FAILED", error)
        if conflict_currentness.state is not LegalClientMatterConflictDispositionCurrentnessState.ENGAGEMENT_PERMITTED:
            _fail(f"L9C10_P5_CONFLICT_NOT_PERMITTED_{_state(conflict_currentness.state)}")
        if len(conflict_currentness.decisive_disposition_ids) != 1 or len(conflict_currentness.decisive_disposition_fingerprints) != 1:
            _fail("L9C10_P5_CONFLICT_DECISION_AMBIGUOUS")
        conflict_id = conflict_currentness.decisive_disposition_ids[0]
        conflict_fp = conflict_currentness.decisive_disposition_fingerprints[0]
        try:
            conflict = disposition_registry.get_disposition(tenant, conflict_id, self._conflict_collection, session=tx)
        except Exception as error:
            _fail("L9C10_P5_CONFLICT_UNAVAILABLE", error)
        if (
            conflict.fingerprint != conflict_fp
            or conflict.tenant_id != tenant
            or conflict.case_matter_id != matter.case_matter_id
            or conflict.matter_fingerprint != matter.fingerprint
            or conflict.client_party_id != party.party_id
            or conflict.subject_identity_fingerprint != party.subject_identity_fingerprint
            or conflict.disposition is not LegalClientMatterConflictDispositionType.ENGAGEMENT_PERMITTED
            or conflict.effective_from > at
        ):
            _fail("L9C10_P5_CONFLICT_LINEAGE_INVALID")

        try:
            mandate_currentness = LegalClientMatterMandateCurrentnessComposer(
                mandate_collection=self._mandate_collection,
                grant_collection=self._mandate_grant_collection,
                grant_lifecycle_collection=self._mandate_grant_lifecycle_collection,
                matter_lifecycle_collection=self._mandate_matter_lifecycle_collection,
                acknowledgment_collection=self._mandate_acknowledgment_collection,
            ).compose_currentness(tenant, requested_mandate_id, at, tx)
        except LegalClientMatterMandateCurrentnessComposerError as error:
            _fail("L9C10_P5_MANDATE_CURRENTNESS_FAILED", error)
        if mandate_currentness.state is not LegalClientMatterMandateCurrentnessState.CURRENT:
            _fail(f"L9C10_P5_MANDATE_NOT_CURRENT_{_state(mandate_currentness.state)}")
        try:
            mandate = mandate_registry.get_mandate(
                tenant, requested_mandate_id, self._mandate_collection, session=tx
            )
        except Exception as error:
            _fail("L9C10_P5_MANDATE_UNAVAILABLE", error)
        if (
            mandate.tenant_id != tenant
            or mandate.mandate_id != requested_mandate_id
            or mandate.case_matter_id != matter.case_matter_id
            or mandate.matter_fingerprint != matter.fingerprint
            or mandate.client_party_id != party.party_id
            or mandate.subject_identity_fingerprint != party.subject_identity_fingerprint
            or mandate.fingerprint != mandate_currentness.mandate_fingerprint
            or mandate.effective_from > at
        ):
            _fail("L9C10_P5_MANDATE_LINEAGE_INVALID")

        try:
            decision_currentness = LegalClientMatterEngagementFirmDecisionCurrentnessComposer(
                decision_collection=self._decision_collection
            ).compose_currentness(
                tenant,
                matter.case_matter_id,
                matter.fingerprint,
                party.party_id,
                party.subject_identity_fingerprint,
                at,
                tx,
            )
        except LegalClientMatterEngagementFirmDecisionCurrentnessComposerError as error:
            _fail("L9C10_P5_FIRM_DECISION_CURRENTNESS_FAILED", error)
        if decision_currentness.state is not LegalClientMatterEngagementFirmDecisionCurrentnessState.ACCEPTED:
            _fail(f"L9C10_P5_FIRM_DECISION_NOT_ACCEPTED_{_state(decision_currentness.state)}")
        if len(decision_currentness.decisive_decision_ids) != 1 or len(decision_currentness.decisive_decision_fingerprints) != 1:
            _fail("L9C10_P5_FIRM_DECISION_NOT_SCALAR")
        decision_id = decision_currentness.decisive_decision_ids[0]
        decision_fp = decision_currentness.decisive_decision_fingerprints[0]
        try:
            decision = decision_registry.get_firm_decision(tenant, decision_id, self._decision_collection, session=tx)
        except Exception as error:
            _fail("L9C10_P5_FIRM_DECISION_UNAVAILABLE", error)
        if (
            decision.fingerprint != decision_fp
            or decision.tenant_id != tenant
            or decision.case_matter_id != matter.case_matter_id
            or decision.matter_fingerprint != matter.fingerprint
            or decision.client_party_id != party.party_id
            or decision.subject_reference != party.subject_reference
            or decision.subject_identity_fingerprint != party.subject_identity_fingerprint
            or decision.decision is not LegalClientMatterEngagementFirmDecisionType.ACCEPTED
            or decision.effective_from > at
        ):
            _fail("L9C10_P5_FIRM_DECISION_LINEAGE_INVALID")

        decisive_times = (
            matter.opened_at,
            party.registered_at,
            capacity.effective_from,
            acceptance.accepted_at,
            instrument.effective_from,
            lifecycle.occurred_at,
            approval.effective_from,
            conflict.effective_from,
            mandate.effective_from,
            decision.effective_from,
        )
        effective_from = max(decisive_times)
        if effective_from > at:
            _fail("L9C10_P5_EFFECTIVE_FROM_FUTURE")
        engagement_id = _formation_id(
            tenant_id=tenant,
            case_matter_id=matter.case_matter_id,
            client_party_id=party.party_id,
            client_acceptance_fingerprint=acceptance.fingerprint,
            mandate_fingerprint=mandate.fingerprint,
            conflict_disposition_fingerprint=conflict.fingerprint,
            firm_decision_fingerprint=decision.fingerprint,
            idempotency_key=replay_key,
        )
        try:
            value = LegalClientMatterEngagement.from_canonical(
                engagement_id=engagement_id,
                case_matter=matter,
                party=party,
                acting_capacity=capacity,
                client_acceptance=acceptance,
                instrument=instrument,
                mandate_id=mandate.mandate_id,
                mandate_scope=mandate.scope_reference,
                mandate_fingerprint=mandate.fingerprint,
                conflict_disposition_id=conflict.disposition_id,
                conflict_disposition_fingerprint=conflict.fingerprint,
                firm_decision_id=decision.decision_id,
                decision_actor_principal_id=decision.decision_actor_principal_id,
                firm_decision_fingerprint=decision.fingerprint,
                authorization_evidence_reference=decision.authorization_evidence_reference,
                authorization_evidence_fingerprint=decision.authorization_evidence_fingerprint,
                source_evidence_reference=decision.source_evidence_reference,
                source_evidence_fingerprint=decision.source_evidence_fingerprint,
                effective_from=effective_from,
                idempotency_key=replay_key,
            )
        except Exception as error:
            _fail("L9C10_P5_ENGAGEMENT_CONSTRUCTION_FAILED", error)
        try:
            persisted = engagement_registry.persist_engagement(
                value, self._engagement_collection, session=tx
            )
        except engagement_registry.LegalClientMatterEngagementRegistryConflictError as error:
            _fail("L9C10_P5_DIVERGENT_REPLAY", error)
        except engagement_registry.LegalClientMatterEngagementRegistryRetryRequiredError as error:
            _fail("L9C10_P5_WHOLE_TRANSACTION_RETRY_REQUIRED", error)
        except engagement_registry.LegalClientMatterEngagementRegistryError as error:
            _fail("L9C10_P5_ENGAGEMENT_PERSISTENCE_FAILED", error)
        if type(persisted) is not LegalClientMatterEngagement or persisted.to_dict() != value.to_dict():
            _fail("L9C10_P5_POST_WRITE_CORRELATION_INVALID")
        return persisted


def compose_engagement(
    *,
    identity: SovereignIdentity,
    case_matter_id: str,
    client_party_id: str,
    client_acceptance_id: str,
    mandate_id: str,
    idempotency_key: str,
    evaluated_at: datetime,
    session: Any,
    matter_lifecycle_collection: Any,
    party_collection: Any,
    capacity_collection: Any,
    context_collection: Any,
    acceptance_collection: Any,
    instrument_collection: Any,
    instrument_lifecycle_collection: Any,
    approval_collection: Any,
    conflict_collection: Any,
    mandate_collection: Any,
    mandate_grant_collection: Any,
    mandate_grant_lifecycle_collection: Any,
    mandate_matter_lifecycle_collection: Any,
    mandate_acknowledgment_collection: Any,
    decision_collection: Any,
    engagement_collection: Any,
) -> LegalClientMatterEngagement:
    """Functional one-shot boundary equivalent to the explicit composer."""
    return LegalClientMatterEngagementFormationComposer(
        matter_lifecycle_collection=matter_lifecycle_collection,
        party_collection=party_collection,
        capacity_collection=capacity_collection,
        context_collection=context_collection,
        acceptance_collection=acceptance_collection,
        instrument_collection=instrument_collection,
        instrument_lifecycle_collection=instrument_lifecycle_collection,
        approval_collection=approval_collection,
        conflict_collection=conflict_collection,
        mandate_collection=mandate_collection,
        mandate_grant_collection=mandate_grant_collection,
        mandate_grant_lifecycle_collection=mandate_grant_lifecycle_collection,
        mandate_matter_lifecycle_collection=mandate_matter_lifecycle_collection,
        mandate_acknowledgment_collection=mandate_acknowledgment_collection,
        decision_collection=decision_collection,
        engagement_collection=engagement_collection,
    ).compose_engagement(
        identity=identity,
        case_matter_id=case_matter_id,
        client_party_id=client_party_id,
        client_acceptance_id=client_acceptance_id,
        mandate_id=mandate_id,
        idempotency_key=idempotency_key,
        evaluated_at=evaluated_at,
        session=session,
    )


__all__ = [
    "VERSION",
    "LegalClientMatterEngagementFormationComposer",
    "LegalClientMatterEngagementFormationComposerError",
    "compose_engagement",
]


# ARTIFACT: legal_client_matter_engagement_formation_composer.py
# VERSION: v1.0.0-L9C10-P5-ENGAGEMENT-FORMATION-COMPOSER
# AUTHORITY BOUNDARY: immutable Engagement formation orchestration only
# TENANT POSTURE: exact identity-derived tenant and shared caller session
# FAIL-CLOSED POSTURE: no degraded currentness, chronology, replay or lineage
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively
# END OF WILSY OS SOVEREIGN ARTIFACT
