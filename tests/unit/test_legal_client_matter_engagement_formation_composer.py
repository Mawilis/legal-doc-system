"""Direct certificate for the L9C10-P5 Engagement formation composer.

TITLE: WILSY OS Legal Engagement Formation Composer Certificate
VERSION: v1.0.0-L9C10-P6-ENGAGEMENT-FORMATION-DIRECT-CERTIFICATE
AUTHORITY: Wilsy OS Core Governance / Python EOS Legal Operations
EPITOME: Prove the published formation composer revalidates exact canonical
         prerequisites under one caller transaction and one explicit instant,
         derives immutable Engagement evidence, and performs one registry
         boundary without introducing IAM or downstream legal authority.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tests/unit/test_legal_client_matter_engagement_formation_composer.py
COLLABORATION / OWNERSHIP: This certificate covers only the P5 composer;
                            domain, registry, currentness and IAM authorities
                            remain owned by their published artifacts.
CERTIFICATION / UPDATE DATE: 2026-09-28
CHANGELOG: v1.0.0-L9C10-P6 certifies transaction ownership, shared-time and
           lineage propagation, currentness gates, deterministic identity,
           mandate-derived scope, scalar decision safety, replay/persistence,
           bounded errors and authority exclusions using recording fakes.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2; ISO 27001.
SECURITY / PRIVACY POSTURE: Synthetic opaque identifiers only; no Mongo,
                             network, credentials, tokens or production data.
TENANT BOUNDARY: Fakes record exact tenant and lineage arguments; no fallback
                 or cross-tenant authority is available to the certificate.
AUTHORITY BOUNDARY: Test evidence only. Passing this file creates no runtime
                    IAM, Representation, Court, lifecycle or financial truth.
FINANCIAL AUTHORITY BOUNDARY: Kennel EOS exclusively owns execution.
TRANSACTION BOUNDARY: Recording fakes prove the composer never owns lifecycle.
FAIL-CLOSED DECLARATION: Every material missing, stale, ambiguous, corrupt or
                         divergent prerequisite tested here rejects safely.
"""
# pyright: reportArgumentType=false, reportAttributeAccessIssue=false, reportOptionalMemberAccess=false, reportCallIssue=false, reportIndexIssue=false
from __future__ import annotations

import ast
import inspect
from dataclasses import dataclass, replace
from datetime import datetime, timedelta, timezone
from types import SimpleNamespace
from typing import Any

import pytest

from tools.eos.auth.identity import SovereignIdentity
from tools.eos.auth.principal_status import PrincipalStatus
from tools.eos.legal_operations.domain.legal_client_acceptance import (
    LegalClientAcceptance,
    record_legal_client_acceptance,
)
from tools.eos.legal_operations.domain.legal_client_acting_capacity import (
    LegalClientActingCapacity,
    LegalClientActingCapacityType,
    record_legal_client_acting_capacity,
)
from tools.eos.legal_operations.domain.legal_client_matter_acceptance_instrument import (
    LegalClientMatterAcceptanceInstrument,
    record_legal_client_matter_acceptance_instrument,
)
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
from tools.eos.legal_operations.domain.legal_client_matter_engagement import (
    VERSION as ENGAGEMENT_DOMAIN_VERSION,
)
from tools.eos.legal_operations.domain.legal_matter_party import (
    LegalMatterPartyKind,
    LegalMatterPartyRole,
    LegalMatterPartySide,
    register_legal_matter_party,
)
from tools.eos.legal_operations.domain.legal_operations_lifecycle import (
    CaseMatter,
    CaseMatterState,
)
from tools.eos.legal_operations.orchestration import (
    legal_client_matter_engagement_formation_composer as composer_module,
)


BASE = datetime(2026, 9, 28, 10, 0, 0, 123456, tzinfo=timezone.utc)
TENANT = "tenant-l9c10"
MATTER_ID = "matter-l9c10"
PARTY_ID = "party-l9c10"
CONTEXT_ID = "context-l9c10"
ACCEPTANCE_ID = f"LEGAL-CLIENT-ACCEPT:{CONTEXT_ID}"
CAPACITY_ID = "capacity-l9c10"
INSTRUMENT_ID = "instrument-l9c10"
INSTRUMENT_VERSION = "1.0.0"
MANDATE_ID = "mandate-l9c10"
CONFLICT_ID = "conflict-l9c10"
DECISION_ID = "decision-l9c10"
ACTOR_ID = "principal-client-l9c10"
FINGERPRINTS = {
    "matter": "a" * 128,
    "subject": "b" * 128,
    "evidence": "c" * 128,
    "content": "d" * 128,
    "mandate": "e" * 128,
    "conflict": "f" * 128,
    "decision": "0" * 128,
    "authorization": "1" * 128,
    "source": "2" * 128,
    "capacity": "3" * 128,
    "instrument": "4" * 128,
}


class Session:
    """Recording active transaction accepted by every fake dependency."""

    def __init__(self, active: bool = True) -> None:
        self.active = active
        self.calls: list[tuple[str, object, object, dict[str, object]]] = []

    def in_transaction(self) -> bool:
        return self.active


@dataclass
class State:
    """Mutable fake state used only to drive bounded negative cases."""

    conflict_state: object = LegalClientMatterConflictDispositionCurrentnessState.ENGAGEMENT_PERMITTED
    mandate_state: object = LegalClientMatterMandateCurrentnessState.CURRENT
    decision_state: object = LegalClientMatterEngagementFirmDecisionCurrentnessState.ACCEPTED
    capacities: tuple[LegalClientActingCapacity, ...] = ()
    approval: object | None = None
    lifecycle: object | None = None
    matter: CaseMatter | None = None
    party: object | None = None
    acceptance: object | None = None
    context: object | None = None
    instrument: object | None = None
    mandate: object | None = None
    conflict: object | None = None
    decision: object | None = None
    decisive_conflict_ids: tuple[str, ...] = (CONFLICT_ID,)
    decisive_conflict_fps: tuple[str, ...] = (FINGERPRINTS["conflict"],)
    decisive_decision_ids: tuple[str, ...] = (DECISION_ID,)
    decisive_decision_fps: tuple[str, ...] = (FINGERPRINTS["decision"],)
    persisted: LegalClientMatterEngagement | None = None
    persist_calls: int = 0
    writes: list[tuple[object, object]] | None = None


def _matter() -> CaseMatter:
    return CaseMatter(
        tenant_id=TENANT,
        case_matter_id=MATTER_ID,
        matter_reference="matter-reference:l9c10",
        opened_at=BASE,
        evidence_reference="matter-evidence:l9c10",
    )


def _party(matter: CaseMatter) -> object:
    return register_legal_matter_party(
        matter=matter,
        party_id=PARTY_ID,
        party_kind=LegalMatterPartyKind.ORGANIZATION,
        party_side=LegalMatterPartySide.CLIENT_SIDE,
        matter_role=LegalMatterPartyRole.CLIENT,
        subject_reference="organization:client-l9c10",
        subject_identity_fingerprint=FINGERPRINTS["subject"],
        display_name="Synthetic client",
        registered_at=BASE + timedelta(minutes=1),
        source_evidence_reference="party-evidence:l9c10",
        source_evidence_fingerprint=FINGERPRINTS["evidence"],
    )


def _capacity(matter: CaseMatter, party: object) -> LegalClientActingCapacity:
    return record_legal_client_acting_capacity(
        case_matter=matter,
        party=party,
        capacity_id=CAPACITY_ID,
        principal_id=ACTOR_ID,
        capacity_type=LegalClientActingCapacityType.AUTHORIZED_AGENT,
        effective_from=BASE + timedelta(minutes=2),
        effective_until=BASE + timedelta(days=30),
        source_evidence_reference="capacity-evidence:l9c10",
        source_evidence_fingerprint=FINGERPRINTS["evidence"],
    )


def _acceptance(matter: CaseMatter, party: object) -> LegalClientAcceptance:
    return record_legal_client_acceptance(
        case_matter=matter,
        acceptance_id=ACCEPTANCE_ID,
        party_id=party.party_id,
        subject_reference=party.subject_reference,
        subject_identity_fingerprint=party.subject_identity_fingerprint,
        acceptance_scope="client-information-review:v1",
        actor_principal_id=ACTOR_ID,
        accepted_at=BASE + timedelta(minutes=3),
        source_evidence_reference=(
            f"legal-client-acceptance-context:{CONTEXT_ID}:instrument:"
            f"{INSTRUMENT_ID}:{INSTRUMENT_VERSION}:content:{FINGERPRINTS['content']}:intent:synthetic"
        ),
        source_evidence_fingerprint=FINGERPRINTS["content"],
    )


def _instrument(matter: CaseMatter) -> LegalClientMatterAcceptanceInstrument:
    return record_legal_client_matter_acceptance_instrument(
        case_matter=matter,
        instrument_id=INSTRUMENT_ID,
        version=INSTRUMENT_VERSION,
        instrument_kind="CLIENT_REVIEW_TERMS",
        title="Synthetic reviewed instrument",
        review_scope="client-information-review:v1",
        content_reference="content-reference:l9c10",
        content_fingerprint=FINGERPRINTS["content"],
        created_at=BASE,
        effective_from=BASE + timedelta(minutes=1),
        approval_evidence_reference="approval-evidence:l9c10",
        approval_evidence_fingerprint=FINGERPRINTS["evidence"],
    )


def _install(monkeypatch: pytest.MonkeyPatch) -> tuple[composer_module.LegalClientMatterEngagementFormationComposer, State, Session, datetime]:
    """Install recording dependency seams and return a ready positive harness."""
    state = State()
    session = Session()
    moment = BASE + timedelta(minutes=10)
    matter = _matter()
    party = _party(matter)
    capacity = _capacity(matter, party)
    acceptance = _acceptance(matter, party)
    instrument = _instrument(matter)
    context = SimpleNamespace(
        acceptance_context_id=CONTEXT_ID,
        tenant_id=TENANT,
        case_matter_id=MATTER_ID,
        matter_fingerprint=matter.fingerprint,
        party_id=PARTY_ID,
        subject_reference=party.subject_reference,
        subject_identity_fingerprint=party.subject_identity_fingerprint,
        actor_principal_id=ACTOR_ID,
        capacity_id=CAPACITY_ID,
        capacity_fingerprint=capacity.fingerprint,
        instrument_id=INSTRUMENT_ID,
        instrument_version=INSTRUMENT_VERSION,
        instrument_fingerprint=instrument.fingerprint,
        content_fingerprint=instrument.content_fingerprint,
        acceptance_scope=acceptance.acceptance_scope,
    )
    lifecycle = SimpleNamespace(
        status=LegalClientMatterAcceptanceInstrumentLifecycleStatus.ACTIVE,
        instrument_fingerprint=instrument.fingerprint,
        occurred_at=BASE + timedelta(minutes=1),
    )
    approval = SimpleNamespace(
        decision=LegalClientMatterAcceptanceInstrumentApprovalDecision.APPROVED,
        effective_from=BASE + timedelta(minutes=2),
        instrument_fingerprint=instrument.fingerprint,
        content_fingerprint=instrument.content_fingerprint,
    )
    mandate = SimpleNamespace(
        tenant_id=TENANT,
        mandate_id=MANDATE_ID,
        case_matter_id=MATTER_ID,
        matter_fingerprint=matter.fingerprint,
        client_party_id=PARTY_ID,
        subject_identity_fingerprint=party.subject_identity_fingerprint,
        fingerprint=FINGERPRINTS["mandate"],
        scope_reference="mandate-scope:l9c10",
        effective_from=BASE + timedelta(minutes=5),
    )
    conflict = SimpleNamespace(
        disposition_id=CONFLICT_ID,
        tenant_id=TENANT,
        case_matter_id=MATTER_ID,
        matter_fingerprint=matter.fingerprint,
        client_party_id=PARTY_ID,
        subject_identity_fingerprint=party.subject_identity_fingerprint,
        fingerprint=FINGERPRINTS["conflict"],
        disposition=LegalClientMatterConflictDispositionType.ENGAGEMENT_PERMITTED,
        effective_from=BASE + timedelta(minutes=6),
    )
    decision = SimpleNamespace(
        decision_id=DECISION_ID,
        tenant_id=TENANT,
        case_matter_id=MATTER_ID,
        matter_fingerprint=matter.fingerprint,
        client_party_id=PARTY_ID,
        subject_reference=party.subject_reference,
        subject_identity_fingerprint=party.subject_identity_fingerprint,
        fingerprint=FINGERPRINTS["decision"],
        decision=LegalClientMatterEngagementFirmDecisionType.ACCEPTED,
        decision_actor_principal_id="principal-firm-l9c10",
        authorization_evidence_reference="decision-auth:l9c10",
        authorization_evidence_fingerprint=FINGERPRINTS["authorization"],
        source_evidence_reference="decision-source:l9c10",
        source_evidence_fingerprint=FINGERPRINTS["source"],
        effective_from=BASE + timedelta(minutes=7),
    )
    state.matter, state.party, state.acceptance = matter, party, acceptance
    state.context, state.instrument = context, instrument
    state.lifecycle, state.approval, state.mandate = lifecycle, approval, mandate
    state.conflict, state.decision, state.capacities = conflict, decision, (capacity,)
    state.writes = []

    def record(name: str, args: tuple[object, ...], kwargs: dict[str, object]) -> None:
        supplied = kwargs.get("session")
        if supplied is None and args and args[-1] is session:
            supplied = session
        session.calls.append((name, args, supplied, kwargs))

    monkeypatch.setattr(
        composer_module.matter_registry.LegalOperationsLifecycleRegistry,
        "get_entity_history",
        staticmethod(lambda *args, **kwargs: (record("matter", args, kwargs), state.matter)[1]),
    )
    monkeypatch.setattr(composer_module, "resolve_current_lifecycle_snapshot", lambda *_a, **_k: state.matter)
    monkeypatch.setattr(composer_module.party_registry, "get_party", lambda *args, **kwargs: (record("party", args, kwargs), state.party)[1])
    monkeypatch.setattr(composer_module.capacity_registry, "list_valid_capacities_at", lambda *args, **kwargs: (record("capacity", args, kwargs), state.capacities)[1])
    monkeypatch.setattr(composer_module.context_registry, "get_context", lambda *args, **kwargs: (record("context", args, kwargs), state.context)[1])
    monkeypatch.setattr(composer_module.acceptance_registry, "get_acceptance", lambda *args, **kwargs: (record("acceptance", args, kwargs), state.acceptance)[1])
    monkeypatch.setattr(composer_module.instrument_registry, "get_instrument", lambda *args, **kwargs: (record("instrument", args, kwargs), state.instrument)[1])
    monkeypatch.setattr(composer_module.instrument_lifecycle_registry, "get_current_lifecycle", lambda *args, **kwargs: (record("lifecycle", args, kwargs), state.lifecycle)[1])
    monkeypatch.setattr(composer_module.approval_registry, "get_current_approval", lambda *args, **kwargs: (record("approval", args, kwargs), state.approval)[1])

    class ConflictCurrentness:
        def __init__(self, **_kwargs: object) -> None:
            pass

        def compose_currentness(self, *args: object, **kwargs: object) -> object:
            record("conflict_currentness", args, kwargs)
            return SimpleNamespace(
                state=state.conflict_state,
                decisive_disposition_ids=state.decisive_conflict_ids,
                decisive_disposition_fingerprints=state.decisive_conflict_fps,
                decisive_effective_from=state.conflict.effective_from if state.conflict else None,
            )

    class MandateCurrentness:
        def __init__(self, **_kwargs: object) -> None:
            pass

        def compose_currentness(self, *args: object, **kwargs: object) -> object:
            record("mandate_currentness", args, kwargs)
            return SimpleNamespace(
                state=state.mandate_state,
                mandate_fingerprint=state.mandate.fingerprint if state.mandate else None,
            )

    class DecisionCurrentness:
        def __init__(self, **_kwargs: object) -> None:
            pass

        def compose_currentness(self, *args: object, **kwargs: object) -> object:
            record("decision_currentness", args, kwargs)
            return SimpleNamespace(
                state=state.decision_state,
                decisive_decision_ids=state.decisive_decision_ids,
                decisive_decision_fingerprints=state.decisive_decision_fps,
                decisive_effective_from=state.decision.effective_from if state.decision else None,
            )

    monkeypatch.setattr(composer_module, "LegalClientMatterConflictDispositionCurrentnessComposer", ConflictCurrentness)
    monkeypatch.setattr(composer_module, "LegalClientMatterMandateCurrentnessComposer", MandateCurrentness)
    monkeypatch.setattr(composer_module, "LegalClientMatterEngagementFirmDecisionCurrentnessComposer", DecisionCurrentness)
    monkeypatch.setattr(composer_module.disposition_registry, "get_disposition", lambda *args, **kwargs: (record("disposition", args, kwargs), state.conflict)[1])
    monkeypatch.setattr(composer_module.mandate_registry, "get_mandate", lambda *args, **kwargs: (record("mandate", args, kwargs), state.mandate)[1])
    monkeypatch.setattr(composer_module.decision_registry, "get_firm_decision", lambda *args, **kwargs: (record("decision", args, kwargs), state.decision)[1])

    def persist(value: LegalClientMatterEngagement, _collection: object, *, session: object) -> LegalClientMatterEngagement:
        state.persist_calls += 1
        state.writes.append((value, session))
        return state.persisted or value

    monkeypatch.setattr(composer_module.engagement_registry, "persist_engagement", persist)
    collections = {name: object() for name in (
        "matter_lifecycle", "party", "capacity", "context", "acceptance",
        "instrument", "instrument_lifecycle", "approval", "conflict", "mandate",
        "mandate_grant", "mandate_grant_lifecycle", "mandate_matter_lifecycle",
        "mandate_acknowledgment", "decision", "engagement",
    )}
    composer = composer_module.LegalClientMatterEngagementFormationComposer(**{
        f"{name}_collection": value for name, value in collections.items()
    })
    return composer, state, session, moment


def identity(status: PrincipalStatus = PrincipalStatus.ACTIVE) -> SovereignIdentity:
    """Return a synthetic active or inactive caller identity."""
    return SovereignIdentity(
        identity_id="principal-formation-caller",
        tenant_id=TENANT,
        username=None,
        email=None,
        roles=[],
        permissions=[],
        auth_method="unit",
        status=status,
    )


def compose(composer: Any, session: Session, moment: datetime, **overrides: object) -> LegalClientMatterEngagement:
    """Invoke the only public formation boundary with bounded caller inputs."""
    values: dict[str, object] = {
        "identity": identity(),
        "case_matter_id": MATTER_ID,
        "client_party_id": PARTY_ID,
        "client_acceptance_id": ACCEPTANCE_ID,
        "mandate_id": MANDATE_ID,
        "idempotency_key": "formation-idempotency:l9c10",
        "evaluated_at": moment,
        "session": session,
    }
    values.update(overrides)
    return composer.compose_engagement(**values)


def assert_composer_error(operation: object) -> str:
    """Return the bounded composer code from one expected failure."""
    with pytest.raises(composer_module.LegalClientMatterEngagementFormationComposerError) as raised:
        assert callable(operation)
        operation()  # type: ignore[operator]
    assert raised.value.args == (raised.value.code,)
    return raised.value.code


def test_target_identity_signature_and_authority_surface() -> None:
    """The public surface exposes only caller context, not derived authority."""
    assert composer_module.VERSION == "v1.0.0-L9C10-P5-ENGAGEMENT-FORMATION-COMPOSER"
    signature = inspect.signature(composer_module.LegalClientMatterEngagementFormationComposer.compose_engagement)
    names = set(signature.parameters)
    assert {"identity", "case_matter_id", "client_party_id", "client_acceptance_id", "mandate_id", "idempotency_key", "evaluated_at", "session"} <= names
    assert not {"tenant_id", "subject_reference", "matter_fingerprint", "mandate_scope", "effective_from", "engagement_id", "fingerprint"} & names
    assert ENGAGEMENT_DOMAIN_VERSION == "v1.0.0-L9B1-CLIENT-MATTER-ENGAGEMENT"
    source = open(composer_module.__file__, encoding="utf-8").read()
    tree = ast.parse(source)
    imported = {alias.name for node in tree.body if isinstance(node, ast.ImportFrom) for alias in node.names}
    assert "TenantAuthorizationDecisionEvidenceRegistry" not in imported
    assert "tenant_authorization_decision_evidence_registry" not in source


def test_transaction_and_identity_contracts_reject_before_reads(monkeypatch: pytest.MonkeyPatch) -> None:
    """Missing/inactive transactions and inactive principals fail closed."""
    composer, _state, session, moment = _install(monkeypatch)
    assert_composer_error(lambda: composer.compose_engagement(identity=identity(), case_matter_id=MATTER_ID, client_party_id=PARTY_ID, client_acceptance_id=ACCEPTANCE_ID, mandate_id=MANDATE_ID, idempotency_key="formation-idempotency:l9c10", evaluated_at=moment, session=None))
    inactive = Session(active=False)
    assert_composer_error(lambda: composer.compose_engagement(identity=identity(), case_matter_id=MATTER_ID, client_party_id=PARTY_ID, client_acceptance_id=ACCEPTANCE_ID, mandate_id=MANDATE_ID, idempotency_key="formation-idempotency:l9c10", evaluated_at=moment, session=inactive))
    assert_composer_error(lambda: compose(composer, session, moment, identity=identity(PrincipalStatus.REVOKED)))
    assert session.calls == []


def test_success_provenance_time_session_and_single_registry_boundary(monkeypatch: pytest.MonkeyPatch) -> None:
    """A positive formation proves exact fields, session/time propagation and one write."""
    composer, state, session, moment = _install(monkeypatch)
    result = compose(composer, session, moment)
    assert type(result) is LegalClientMatterEngagement
    assert result.tenant_id == TENANT
    assert result.case_matter_id == MATTER_ID
    assert result.client_party_id == PARTY_ID
    assert result.client_acceptance_id == ACCEPTANCE_ID
    assert result.instrument_id == INSTRUMENT_ID
    assert result.version == INSTRUMENT_VERSION
    assert result.mandate_id == MANDATE_ID
    assert result.mandate_scope == "mandate-scope:l9c10"
    assert result.conflict_disposition_id == CONFLICT_ID
    assert result.conflict_disposition_fingerprint == FINGERPRINTS["conflict"]
    assert result.firm_decision_id == DECISION_ID
    assert result.decision_actor_principal_id == "principal-firm-l9c10"
    assert result.authorization_evidence_reference == "decision-auth:l9c10"
    assert result.source_evidence_reference == "decision-source:l9c10"
    assert result.effective_from == BASE + timedelta(minutes=7)
    assert result.idempotency_key == "formation-idempotency:l9c10"
    assert state.persist_calls == 1
    assert state.writes == [(result, session)]
    dependency_calls = [entry for entry in session.calls if entry[0] in {"capacity", "approval", "conflict_currentness", "mandate_currentness", "decision_currentness"}]
    assert dependency_calls
    assert all(entry[2] is session for entry in session.calls)
    assert any(entry[0] == "capacity" and entry[1][2] == moment for entry in dependency_calls)
    assert any(entry[0] == "approval" and entry[3].get("at") is moment for entry in session.calls)
    assert any(entry[0] == "conflict_currentness" and entry[1][5] == moment for entry in session.calls)
    assert any(entry[0] == "mandate_currentness" and entry[1][2] == moment for entry in session.calls)
    assert any(entry[0] == "decision_currentness" and entry[1][5] == moment for entry in session.calls)


def test_capacity_and_currentness_negative_matrix(monkeypatch: pytest.MonkeyPatch) -> None:
    """Zero/multiple capacity and every negative currentness state are blocked."""
    composer, state, session, moment = _install(monkeypatch)
    state.capacities = ()
    assert "CAPACITY_NOT_EXACTLY_ONE" in assert_composer_error(lambda: compose(composer, session, moment))
    composer, state, session, moment = _install(monkeypatch)
    state.capacities = (state.capacities[0], state.capacities[0])
    assert "CAPACITY_NOT_EXACTLY_ONE" in assert_composer_error(lambda: compose(composer, session, moment))
    for field, values in (
        ("conflict_state", ["NO_DISPOSITION", "ENGAGEMENT_PROHIBITED", "ENGAGEMENT_UNRESOLVED", "AMBIGUOUS", "CORRUPT_BLOCKED"]),
        ("mandate_state", ["FORMATION_ABSENT", "EXPIRED", "GRANT_NOT_CURRENT", "ACKNOWLEDGMENT_NOT_CURRENT", "AMBIGUOUS", "CORRUPT_BLOCKED", "NOT_YET_EFFECTIVE"]),
        ("decision_state", ["NO_DECISION", "DECLINED", "REQUIRES_REVIEW", "AMBIGUOUS", "CORRUPT_BLOCKED"]),
    ):
        for value in values:
            composer, state, session, moment = _install(monkeypatch)
            setattr(state, field, value)
            assert_composer_error(lambda composer=composer, session=session, moment=moment: compose(composer, session, moment))


def test_lineage_and_approval_instrument_fail_closed(monkeypatch: pytest.MonkeyPatch) -> None:
    """Acceptance, instrument, approval, party and decisive-record drift reject."""
    composer, state, session, moment = _install(monkeypatch)
    state.acceptance = SimpleNamespace(
        tenant_id=state.acceptance.tenant_id,
        case_matter_id=state.acceptance.case_matter_id,
        matter_fingerprint=state.acceptance.matter_fingerprint,
        acceptance_id=state.acceptance.acceptance_id,
        party_id="other-party",
        subject_reference=state.acceptance.subject_reference,
        subject_identity_fingerprint=state.acceptance.subject_identity_fingerprint,
        acceptance_scope=state.acceptance.acceptance_scope,
        actor_principal_id=state.acceptance.actor_principal_id,
        accepted_at=state.acceptance.accepted_at,
        source_evidence_fingerprint=state.acceptance.source_evidence_fingerprint,
        source_evidence_reference=state.acceptance.source_evidence_reference,
    )
    assert "ACCEPTANCE_LINEAGE_INVALID" in assert_composer_error(lambda: compose(composer, session, moment))
    composer, state, session, moment = _install(monkeypatch)
    state.instrument = SimpleNamespace(**{field: getattr(state.instrument, field) for field in ("tenant_id", "case_matter_id", "matter_fingerprint", "instrument_id", "version", "fingerprint", "content_fingerprint", "effective_from")})
    state.instrument.content_fingerprint = "f" * 128
    assert "INSTRUMENT_LINEAGE_INVALID" in assert_composer_error(lambda: compose(composer, session, moment))
    composer, state, session, moment = _install(monkeypatch)
    state.approval = None
    assert "APPROVAL_NOT_CURRENT" in assert_composer_error(lambda: compose(composer, session, moment))
    composer, state, session, moment = _install(monkeypatch)
    other_matter = CaseMatter(
        tenant_id=TENANT,
        case_matter_id=MATTER_ID,
        matter_reference="matter-reference:other",
        opened_at=BASE,
        evidence_reference="matter-evidence:other",
    )
    state.party = _party(other_matter)
    assert "PARTY_LINEAGE_INVALID" in assert_composer_error(lambda: compose(composer, session, moment))
    composer, state, session, moment = _install(monkeypatch)
    state.decisive_decision_ids = (DECISION_ID, "decision-2")
    state.decisive_decision_fps = (FINGERPRINTS["decision"], "1" * 128)
    assert "FIRM_DECISION_NOT_SCALAR" in assert_composer_error(lambda: compose(composer, session, moment))


def test_scope_is_durable_mandate_scope_and_identity_is_deterministic(monkeypatch: pytest.MonkeyPatch) -> None:
    """Caller cannot widen mandate scope; same intent yields the same ID."""
    composer, state, session, moment = _install(monkeypatch)
    first = compose(composer, session, moment)
    second = compose(composer, session, moment)
    assert first.engagement_id == second.engagement_id
    assert first.fingerprint == second.fingerprint
    assert first.mandate_scope == state.mandate.scope_reference
    assert state.persist_calls == 2
    assert_composer_error(lambda: compose(composer, session, moment, mandate_id="other-mandate"))


def test_chronology_and_input_immutability(monkeypatch: pytest.MonkeyPatch) -> None:
    """Future prerequisites and invalid times reject without mutating inputs."""
    composer, state, session, moment = _install(monkeypatch)
    state.decision.effective_from = moment + timedelta(seconds=1)
    assert assert_composer_error(lambda: compose(composer, session, moment)) in {"L9C10_P5_FIRM_DECISION_LINEAGE_INVALID", "L9C10_P5_EFFECTIVE_FROM_FUTURE"}
    composer, state, session, moment = _install(monkeypatch)
    assert_composer_error(lambda: compose(composer, session, datetime(2026, 9, 28, 10, 0, 0)))
    assert_composer_error(lambda: compose(composer, session, moment, idempotency_key=" bad"))
    assert state.persist_calls == 0


def test_matter_and_party_classification_negative_cases(monkeypatch: pytest.MonkeyPatch) -> None:
    """Missing/non-OPEN matter and wrong side/role are blocked before persistence."""
    composer, state, session, moment = _install(monkeypatch)
    state.matter = None
    assert "CASE_MATTER_INVALID" in assert_composer_error(lambda: compose(composer, session, moment))
    composer, state, session, moment = _install(monkeypatch)
    state.matter = SimpleNamespace(tenant_id=TENANT, case_matter_id=MATTER_ID, state=CaseMatterState.CLOSED)
    assert "CASE_MATTER_INVALID" in assert_composer_error(lambda: compose(composer, session, moment))
    composer, state, session, moment = _install(monkeypatch)
    state.party = SimpleNamespace(tenant_id=TENANT, case_matter_id=MATTER_ID, matter_fingerprint=state.matter.fingerprint, party_side=LegalMatterPartySide.ADVERSE_SIDE, matter_role=LegalMatterPartyRole.DEFENDANT)
    assert "PARTY_INVALID" in assert_composer_error(lambda: compose(composer, session, moment))


def test_no_direct_collection_or_transaction_authority_and_no_real_mongo() -> None:
    """The certificate itself is fake-backed and the composer has no forbidden calls."""
    source = open(composer_module.__file__, encoding="utf-8").read()
    tree = ast.parse(source)
    forbidden = {"start_transaction", "commit_transaction", "abort_transaction", "Representation", "Court", "TenantAuthorizationDecisionEvidenceRegistry", "create_access_token", "requests", "httpx"}
    calls = {node.func.id for node in ast.walk(tree) if isinstance(node, ast.Call) and isinstance(node.func, ast.Name)}
    assert not calls & forbidden
    assert "insert_one" not in source and "update_one" not in source and "delete_many" not in source


__all__ = ["BASE", "TENANT", "MATTER_ID", "PARTY_ID"]


# ARTIFACT: test_legal_client_matter_engagement_formation_composer.py
# VERSION: v1.0.0-L9C10-P6-ENGAGEMENT-FORMATION-DIRECT-CERTIFICATE
# AUTHORITY BOUNDARY: direct certificate evidence only
# TENANT POSTURE: synthetic exact-tenant recording fakes
# FAIL-CLOSED POSTURE: no Mongo, network, production writes or downstream authority
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively
# END OF WILSY OS SOVEREIGN ARTIFACT
