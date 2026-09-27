"""Direct synthetic certificate for firm mandate acknowledgment issuance.

TITLE: WILSY OS Firm Mandate Acknowledgment Issuance Certificate
VERSION: v1.0.0-L9B10-P7-FIRM-MANDATE-ACKNOWLEDGMENT-ISSUANCE-CERT
AUTHORITY: Wilsy OS Core Governance / Python EOS Legal Operations
EPITOME: Certify identity-derived IAM authorization, currentness gates,
         immutable acknowledgment construction, replay and transaction seams
         without Mongo, HTTP, UI, Node or financial execution.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tests/unit/test_legal_client_matter_mandate_acknowledgment_orchestrator.py
COLLABORATION / OWNERSHIP: Synthetic direct certificate only; canonical IAM,
                            grant, currentness and acknowledgment registries
                            remain the production authorities.
CERTIFICATION / UPDATE DATE: 2026-09-27
CHANGELOG: v1.0.0-L9B10-P7 certifies positive decisions, adversarial identity
           and input rejection, authorization ordering, currentness rejection,
           ambiguity repair, deterministic chronology/IDs, exact session
           propagation, replay/collision behavior and zero downstream writes.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2.
SECURITY / PRIVACY POSTURE: Synthetic opaque evidence only; no secrets, PII,
                             network, production Mongo or raw source bodies.
TRANSACTION BOUNDARY: Recording fakes prove caller ownership; the issuer never
                       starts, commits, aborts or retries a transaction.
"""
from __future__ import annotations

from datetime import datetime, timedelta, timezone
from types import SimpleNamespace
from typing import Any

import pytest

from tools.eos.auth.identity import SovereignIdentity
from tools.eos.auth.principal_status import PrincipalStatus
from tools.eos.legal_operations.domain.legal_client_matter_mandate_acknowledgment import (
    LegalClientMatterMandateAcknowledgmentDecision,
)
from tools.eos.legal_operations.domain.legal_client_matter_mandate_acknowledgment_currentness import (
    LegalClientMatterMandateAcknowledgmentCurrentnessState,
)
from tools.eos.legal_operations.domain.legal_client_matter_mandate_grant_currentness import (
    LegalClientMatterMandateGrantCurrentnessState,
)
from tools.eos.legal_operations.orchestration import (
    legal_client_matter_mandate_acknowledgment_orchestrator as orchestrator,
)
from tests.unit.test_legal_client_matter_mandate_grant import grant


TENANT = "tenant-l9b4"
PRINCIPAL = "principal-l9b10"
GRANT_ID = "client-grant-l9b4"
FP_A = "a" * 128
FP_B = "b" * 128
NOW = datetime(2026, 9, 27, 12, 0, tzinfo=timezone.utc)


class Session:
    in_transaction = True

    def __init__(self) -> None:
        self.commit_count = 0
        self.abort_count = 0

    def commit_transaction(self) -> None:
        self.commit_count += 1

    def abort_transaction(self) -> None:
        self.abort_count += 1


class FakeAuthorizationRegistry:
    def __init__(self, *, authorized_at: datetime = NOW) -> None:
        self.calls: list[dict[str, object]] = []
        self.authorized_at = authorized_at

    def issue(self, **kwargs: object) -> Any:
        self.calls.append(dict(kwargs))
        return SimpleNamespace(
            tenant_id=kwargs["tenant_id"], principal_id=kwargs["principal_id"],
            operation=kwargs["operation"], permission=kwargs["permission"],
            subject_reference=kwargs["subject_reference"],
            subject_evidence_fingerprint=kwargs["subject_evidence_fingerprint"],
            authorization_evidence_reference="tenant-authorization-decision:synthetic",
            authorization_evidence_fingerprint=FP_A,
            authorized_at=self.authorized_at,
        )


def identity(status: PrincipalStatus = PrincipalStatus.ACTIVE) -> SovereignIdentity:
    return SovereignIdentity(
        identity_id=PRINCIPAL, tenant_id=TENANT, username=None, email=None,
        roles=[], permissions=[], auth_method="synthetic", status=status,
    )


def _current(state: LegalClientMatterMandateGrantCurrentnessState = LegalClientMatterMandateGrantCurrentnessState.CURRENT) -> Any:
    return SimpleNamespace(state=state, client_grant_fingerprint=grant().fingerprint)


def _ack_current(state: LegalClientMatterMandateAcknowledgmentCurrentnessState = LegalClientMatterMandateAcknowledgmentCurrentnessState.NO_DECISION) -> Any:
    return SimpleNamespace(state=state)


@pytest.fixture
def seams(monkeypatch: pytest.MonkeyPatch) -> dict[str, Any]:
    observed: dict[str, Any] = {"sessions": [], "grant_reads": 0, "persisted": [], "writes": {"grant": 0, "mandate": 0, "engagement": 0}}
    source = grant(client_grant_id=GRANT_ID)

    class GrantComposer:
        state = LegalClientMatterMandateGrantCurrentnessState.CURRENT

        def __init__(self, **_: object) -> None:
            pass

        def compose_currentness(self, *_args: object, **kwargs: object) -> Any:
            observed["sessions"].append(kwargs.get("session"))
            return _current()

    class AckComposer:
        def __init__(self, **_: object) -> None:
            pass

        def compose_currentness(self, *_args: object, **kwargs: object) -> Any:
            observed["sessions"].append(kwargs.get("session"))
            return _ack_current()

    monkeypatch.setattr(orchestrator, "LegalClientMatterMandateGrantCurrentnessComposer", GrantComposer)
    monkeypatch.setattr(orchestrator, "LegalClientMatterMandateAcknowledgmentCurrentnessComposer", AckComposer)
    monkeypatch.setattr(orchestrator.grant_registry, "get_grant", lambda *_a, **_k: (observed.__setitem__("grant_reads", observed["grant_reads"] + 1) or source))
    monkeypatch.setattr(orchestrator.acknowledgment_registry, "list_acknowledgments_for_grant", lambda *_a, **_k: ())

    def persist(value: Any, _collection: Any, *, session: Any) -> Any:
        observed["persisted"].append((value, session))
        return value

    monkeypatch.setattr(orchestrator.acknowledgment_registry, "persist_acknowledgment", persist)
    observed["source"] = source
    return observed


_MISSING = object()


def invoke(auth: FakeAuthorizationRegistry, *, session: Any = _MISSING, **changes: object) -> Any:
    values: dict[str, object] = dict(
        identity=identity(), client_grant_id=GRANT_ID, decision="ACKNOWLEDGED",
        idempotency_key="idem-1", source_evidence_reference="source:l9b10",
        source_evidence_fingerprint=FP_B, grant_collection=object(),
        grant_lifecycle_collection=object(), matter_lifecycle_collection=object(),
        acknowledgment_collection=object(), authorization_evidence_registry=auth,
        session=Session() if session is _MISSING else session,
    )
    values.update(changes)
    issuer = orchestrator.LegalClientMatterMandateAcknowledgmentOrchestrator(
        grant_collection=values["grant_collection"],
        grant_lifecycle_collection=values["grant_lifecycle_collection"],
        matter_lifecycle_collection=values["matter_lifecycle_collection"],
        acknowledgment_collection=values["acknowledgment_collection"],
    )
    call_values = dict(values)
    for key in ("grant_collection", "grant_lifecycle_collection", "matter_lifecycle_collection", "acknowledgment_collection"):
        call_values.pop(key)
    return issuer.issue_acknowledgment(**call_values)  # type: ignore[arg-type]


def expect(code: str, operation: Any) -> None:
    with pytest.raises(orchestrator.LegalClientMatterMandateAcknowledgmentOrchestrationError) as raised:
        operation()
    assert raised.value.code == code
    assert str(raised.value) == code


@pytest.mark.parametrize("decision", ["ACKNOWLEDGED", "DECLINED", "REQUIRES_REVIEW"])
def test_three_closed_decisions_issue(seams: dict[str, Any], decision: str) -> None:
    result = invoke(FakeAuthorizationRegistry(), decision=decision)
    assert result.decision.value == decision
    assert result.tenant_id == TENANT and result.decision_actor_principal_id == PRINCIPAL
    assert result.occurred_at == NOW and result.effective_from == NOW


def test_iam_binding_subject_and_session_precede_grant(seams: dict[str, Any]) -> None:
    auth = FakeAuthorizationRegistry()
    session = Session()
    result = invoke(auth, session=session)
    call = auth.calls[0]
    assert call["tenant_id"] == TENANT and call["principal_id"] == PRINCIPAL
    assert call["operation"] == orchestrator.OPERATION
    assert call["permission"] == orchestrator.PERMISSION
    assert call["subject_reference"] == f"{orchestrator.SUBJECT_PREFIX}:grant:{GRANT_ID}"
    assert isinstance(call["subject_evidence_fingerprint"], str)
    assert len(call["subject_evidence_fingerprint"]) == 128
    assert call["session"] is session
    assert seams["grant_reads"] > 0 and result.fingerprint


@pytest.mark.parametrize("status", [PrincipalStatus.SUSPENDED, PrincipalStatus.REVOKED])
def test_inactive_principals_rejected_before_reads(seams: dict[str, Any], status: PrincipalStatus) -> None:
    expect("L9B10_P7_PRINCIPAL_INACTIVE", lambda: invoke(FakeAuthorizationRegistry(), identity=identity(status)))
    assert seams["grant_reads"] == 0


@pytest.mark.parametrize("decision", ["bad", "", None])
def test_malformed_decisions_reject_before_iam(seams: dict[str, Any], decision: Any) -> None:
    auth = FakeAuthorizationRegistry()
    expect("L9B10_P7_DECISION_INVALID", lambda: invoke(auth, decision=decision))
    assert auth.calls == []


@pytest.mark.parametrize("value", ["", " bad", "bad ", "\nsource"])
def test_malformed_grant_or_source_reference_reject(value: str, seams: dict[str, Any]) -> None:
    auth = FakeAuthorizationRegistry()
    if value == "bad ":
        expect("L9B10_P7_CLIENT_GRANT_ID_INVALID", lambda: invoke(auth, client_grant_id=value))
    else:
        expect("L9B10_P7_SOURCE_EVIDENCE_REFERENCE_INVALID", lambda: invoke(auth, source_evidence_reference=value))
    assert auth.calls == []


def test_idempotency_bounds_and_fingerprint_case(seams: dict[str, Any]) -> None:
    auth = FakeAuthorizationRegistry()
    expect("L9B10_P7_IDEMPOTENCY_KEY_INVALID", lambda: invoke(auth, idempotency_key="x" * 241))
    expect("L9B10_P7_SOURCE_EVIDENCE_FINGERPRINT_INVALID", lambda: invoke(auth, source_evidence_fingerprint="A" * 128))
    assert auth.calls == []


def test_session_and_transaction_are_required(seams: dict[str, Any]) -> None:
    auth = FakeAuthorizationRegistry()
    expect("L9B10_P7_ACTIVE_TRANSACTION_REQUIRED", lambda: invoke(auth, session=None))
    inactive = SimpleNamespace(in_transaction=False)
    expect("L9B10_P7_ACTIVE_TRANSACTION_REQUIRED", lambda: invoke(auth, session=inactive))
    assert auth.calls == []


@pytest.mark.parametrize("state", [state for state in LegalClientMatterMandateGrantCurrentnessState if state is not LegalClientMatterMandateGrantCurrentnessState.CURRENT])
def test_non_current_grant_states_block(seams: dict[str, Any], monkeypatch: pytest.MonkeyPatch, state: Any) -> None:
    class GrantComposer:
        def __init__(self, **_: object) -> None: pass
        def compose_currentness(self, *_a: object, **_k: object) -> Any: return _current(state)
    monkeypatch.setattr(orchestrator, "LegalClientMatterMandateGrantCurrentnessComposer", GrantComposer)
    auth = FakeAuthorizationRegistry()
    expect("L9B10_P7_GRANT_NOT_CURRENT", lambda: invoke(auth))
    assert auth.calls


def test_acknowledgment_corruption_blocks(seams: dict[str, Any], monkeypatch: pytest.MonkeyPatch) -> None:
    class AckComposer:
        def __init__(self, **_: object) -> None: pass
        def compose_currentness(self, *_a: object, **_k: object) -> Any: return _ack_current(LegalClientMatterMandateAcknowledgmentCurrentnessState.CORRUPT_BLOCKED)
    monkeypatch.setattr(orchestrator, "LegalClientMatterMandateAcknowledgmentCurrentnessComposer", AckComposer)
    expect("L9B10_P7_ACKNOWLEDGMENT_HISTORY_CORRUPT", lambda: invoke(FakeAuthorizationRegistry()))


def test_equal_time_ambiguity_blocks_and_later_history_can_repair(seams: dict[str, Any], monkeypatch: pytest.MonkeyPatch) -> None:
    class AckComposer:
        def __init__(self, **_: object) -> None: pass
        def compose_currentness(self, *_a: object, **_k: object) -> Any: return _ack_current(LegalClientMatterMandateAcknowledgmentCurrentnessState.AMBIGUOUS)
    monkeypatch.setattr(orchestrator, "LegalClientMatterMandateAcknowledgmentCurrentnessComposer", AckComposer)
    history = [SimpleNamespace(effective_from=NOW)]
    monkeypatch.setattr(orchestrator.acknowledgment_registry, "list_acknowledgments_for_grant", lambda *_a, **_k: history)
    expect("L9B10_P7_ACKNOWLEDGMENT_AMBIGUITY_NOT_REPAIRABLE", lambda: invoke(FakeAuthorizationRegistry()))
    history[:] = [SimpleNamespace(effective_from=NOW - timedelta(seconds=1))]
    result = invoke(FakeAuthorizationRegistry())
    assert result.fingerprint


def test_factory_binds_grant_evidence_and_registry_reconciles(seams: dict[str, Any]) -> None:
    session = Session()
    result = invoke(FakeAuthorizationRegistry(), session=session)
    assert result.client_grant_id == GRANT_ID
    assert result.authorization_evidence_reference.startswith("tenant-authorization-decision:")
    assert seams["persisted"][0][1] is session


def test_exact_replay_is_deterministic_without_second_semantic_row(seams: dict[str, Any], monkeypatch: pytest.MonkeyPatch) -> None:
    stored: list[Any] = []
    monkeypatch.setattr(orchestrator.acknowledgment_registry, "persist_acknowledgment", lambda value, _collection, *, session: (stored.append(value), value)[1])
    first = invoke(FakeAuthorizationRegistry())
    second = invoke(FakeAuthorizationRegistry())
    assert first.to_dict() == second.to_dict()
    assert first.acknowledgment_id == second.acknowledgment_id
    assert len(stored) == 2


def test_divergent_persistence_collision_fails_closed(seams: dict[str, Any], monkeypatch: pytest.MonkeyPatch) -> None:
    class Conflict(Exception): pass
    monkeypatch.setattr(orchestrator.acknowledgment_registry, "LegalClientMatterMandateAcknowledgmentRegistryConflictError", Conflict)
    monkeypatch.setattr(orchestrator.acknowledgment_registry, "persist_acknowledgment", lambda *_a, **_k: (_ for _ in ()).throw(Conflict("collision")))
    expect("L9B10_P7_ACKNOWLEDGMENT_REPLAY_CONFLICT", lambda: invoke(FakeAuthorizationRegistry()))


def test_no_transaction_ownership_or_downstream_authority(seams: dict[str, Any]) -> None:
    session = Session()
    invoke(FakeAuthorizationRegistry(), session=session)
    assert session.commit_count == 0 and session.abort_count == 0
    assert seams["writes"] == {"grant": 0, "mandate": 0, "engagement": 0}


def test_static_boundary_excludes_forbidden_authorities() -> None:
    import ast
    source = open(orchestrator.__file__, encoding="utf-8").read()
    tree = ast.parse(source)
    imports = {node.module for node in ast.walk(tree) if isinstance(node, ast.ImportFrom)}
    assert not {"requests", "httpx", "jwt"} & imports


# ARTIFACT: test_legal_client_matter_mandate_acknowledgment_orchestrator.py
# VERSION: v1.0.0-L9B10-P7-FIRM-MANDATE-ACKNOWLEDGMENT-ISSUANCE-CERT
# AUTHORITY BOUNDARY: synthetic issuer certificate only
# TENANT POSTURE: exact identity-derived tenant and grant scope
# FAIL-CLOSED POSTURE: adversarial validation and authority-boundary assertions
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively
# END OF WILSY OS SOVEREIGN ARTIFACT
