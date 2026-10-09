"""Direct P2C3 certificate for authenticated acceptance-context composition.

Synthetic source objects and recording seams are used here. No canonical Mongo,
HTTP, ClientAcceptance, Engagement, Representation, Court, or finance path is
exercised.
"""
from __future__ import annotations

from datetime import datetime, timedelta, timezone
from types import SimpleNamespace
from typing import Any, cast

import pytest

from tools.eos.auth.identity import SovereignIdentity
from tools.eos.auth.principal_status import PrincipalStatus
from tools.eos.auth.tenant_authorization import (
    TenantAuthorizationDecision,
    TenantAuthorizationReason,
)
from tools.eos.legal_operations.domain.legal_client_matter_acceptance_instrument_approval import (
    LegalClientMatterAcceptanceInstrumentApprovalDecision,
)
from tools.eos.legal_operations.domain.legal_client_matter_acceptance_instrument_lifecycle import (
    LegalClientMatterAcceptanceInstrumentLifecycleStatus,
)
from tools.eos.legal_operations.domain.legal_operations_lifecycle import CaseMatter, CaseMatterState
from tools.eos.legal_operations.orchestration import (
    legal_client_acceptance_context_orchestrator as orchestrator,
)

TENANT = "tenant-p2c3"
PRINCIPAL = "principal-client"
MATTER_ID = "matter-1"
PARTY_ID = "party-1"
INSTRUMENT_ID = "instrument-1"
CONTEXT_ID = "context-1"
REPLAY_KEY = "replay-1"
NOW = datetime(2026, 9, 26, 12, 0, 0, 123456, tzinfo=timezone.utc)
FP_A = "a" * 128
FP_B = "b" * 128


class Session:
    """Already-active caller-owned transaction marker."""

    in_transaction = True


class FakeRepository:
    """IAM repository seam recording exact session propagation."""

    def __init__(self) -> None:
        self.calls: list[tuple[tuple[object, ...], dict[str, object]]] = []

    def resolve(self, *args: object, **kwargs: object) -> object:
        self.calls.append((args, kwargs))
        return SimpleNamespace(status="ACTIVE", revision=1)


class FakeIssuer:
    """Authorization-evidence issuer with exact request recording."""

    def __init__(self) -> None:
        self.calls: list[dict[str, object]] = []

    def issue(self, **kwargs: object) -> object:
        self.calls.append(dict(kwargs))
        return SimpleNamespace(
            tenant_id=TENANT,
            principal_id=PRINCIPAL,
            operation=orchestrator.OPERATION,
            permission=orchestrator.PERMISSION,
            authorization_evidence_reference="authorization-evidence:1",
            authorization_evidence_fingerprint=FP_A,
        )


class FakeContext:
    def __init__(self, *, context_id: str = CONTEXT_ID, replay: str = REPLAY_KEY) -> None:
        self.acceptance_context_id = context_id
        self.replay_key = replay
        self.case_matter_id = MATTER_ID
        self.instrument_id = INSTRUMENT_ID
        self.tenant_id = TENANT
        self.actor_principal_id = PRINCIPAL
        self.issued_at = NOW
        self.expires_at = NOW + orchestrator.CONTEXT_LIFETIME

    def to_dict(self) -> dict[str, object]:
        return {
            "acceptance_context_id": self.acceptance_context_id,
            "replay_key": self.replay_key,
            "case_matter_id": self.case_matter_id,
            "instrument_id": self.instrument_id,
            "tenant_id": self.tenant_id,
            "actor_principal_id": self.actor_principal_id,
        }


def _identity(status: PrincipalStatus = PrincipalStatus.ACTIVE) -> SovereignIdentity:
    return SovereignIdentity(
        identity_id=PRINCIPAL,
        tenant_id=TENANT,
        username=None,
        email=None,
        roles=[],
        permissions=[],
        auth_method="synthetic",
        status=status,
    )


def _matter(state: CaseMatterState = CaseMatterState.OPEN) -> CaseMatter:
    return CaseMatter(
        tenant_id=TENANT,
        case_matter_id=MATTER_ID,
        matter_reference="matter-reference",
        opened_at=NOW,
        evidence_reference="matter-source:1",
        state=state,
    )


def _sources() -> dict[str, object]:
    matter = _matter()
    party = SimpleNamespace(
        tenant_id=TENANT,
        case_matter_id=MATTER_ID,
        matter_fingerprint=matter.fingerprint,
        party_id=PARTY_ID,
        subject_reference="client:subject-1",
        subject_identity_fingerprint=FP_A,
        fingerprint=FP_B,
    )
    capacity = SimpleNamespace(
        tenant_id=TENANT,
        case_matter_id=MATTER_ID,
        matter_fingerprint=matter.fingerprint,
        capacity_id="capacity-1",
        principal_id=PRINCIPAL,
        party_id=PARTY_ID,
        subject_reference="client:subject-1",
        subject_identity_fingerprint=FP_A,
        fingerprint=FP_A,
    )
    instrument = SimpleNamespace(
        tenant_id=TENANT,
        case_matter_id=MATTER_ID,
        matter_fingerprint=matter.fingerprint,
        instrument_id=INSTRUMENT_ID,
        version="1.0.0",
        fingerprint=FP_A,
        content_fingerprint=FP_B,
        effective_from=NOW - timedelta(days=1),
    )
    lifecycle = SimpleNamespace(
        tenant_id=TENANT,
        case_matter_id=MATTER_ID,
        matter_fingerprint=matter.fingerprint,
        instrument_fingerprint=FP_A,
        status=LegalClientMatterAcceptanceInstrumentLifecycleStatus.ACTIVE,
        fingerprint=FP_B,
    )
    approval = SimpleNamespace(
        tenant_id=TENANT,
        case_matter_id=MATTER_ID,
        instrument_id=INSTRUMENT_ID,
        version="1.0.0",
        instrument_fingerprint=FP_A,
        content_fingerprint=FP_B,
        approval_id="approval-1",
        fingerprint=FP_A,
        decision=LegalClientMatterAcceptanceInstrumentApprovalDecision.APPROVED,
        effective_from=NOW - timedelta(days=1),
    )
    return {"matter": matter, "party": party, "capacity": capacity, "instrument": instrument, "lifecycle": lifecycle, "approval": approval}


@pytest.fixture
def harness(monkeypatch: pytest.MonkeyPatch) -> dict[str, object]:
    sources = _sources()
    issuer = FakeIssuer()
    repos = {name: FakeRepository() for name in ("principal", "membership", "business", "role")}

    def authorize(**kwargs: object) -> TenantAuthorizationDecision:
        session = kwargs["session"]
        for repository in repos.values():
            assert isinstance(repository, FakeRepository)
            repository.resolve(kwargs["principal_id"], kwargs["tenant_id"], session=session)
        return TenantAuthorizationDecision(
            True, TenantAuthorizationReason.AUTHORIZED, "tenant_legal_client", "LEGAL_CLIENT"
        )

    monkeypatch.setattr(
        orchestrator,
        "authorize_tenant_operation",
        authorize,
    )
    monkeypatch.setattr(
        orchestrator.matter_registry.LegalOperationsLifecycleRegistry,
        "get_entity_history",
        staticmethod(lambda *_args, **_kwargs: (sources["matter"],)),
    )
    monkeypatch.setattr(
        orchestrator.visibility_registry.LegalClientMatterVisibilityRegistry,
        "resolve_current_active",
        staticmethod(lambda *_args, **_kwargs: SimpleNamespace(tenant_id=TENANT, client_principal_id=PRINCIPAL, case_matter_id=MATTER_ID)),
    )
    monkeypatch.setattr(orchestrator.party_registry, "list_matter_parties", lambda *_args, **_kwargs: (sources["party"],))
    monkeypatch.setattr(orchestrator.capacity_registry, "list_valid_capacities_at", lambda *_args, **_kwargs: (sources["capacity"],))
    monkeypatch.setattr(orchestrator.instrument_registry, "get_latest_effective_version", lambda *_args, **_kwargs: sources["instrument"])
    monkeypatch.setattr(orchestrator.lifecycle_registry, "get_current_lifecycle", lambda *_args, **_kwargs: sources["lifecycle"])
    monkeypatch.setattr(orchestrator.approval_registry, "get_current_approval", lambda *_args, **_kwargs: sources["approval"])
    monkeypatch.setattr(orchestrator.context_registry, "list_contexts_for_actor", lambda *_args, **_kwargs: ())
    persisted: list[FakeContext] = []
    monkeypatch.setattr(orchestrator.LegalClientAcceptanceContext, "from_canonical", classmethod(lambda cls, **_kwargs: FakeContext()))
    monkeypatch.setattr(orchestrator.context_registry, "persist_context", lambda value, _collection, *, session: (persisted.append(value) or value))
    return {"issuer": issuer, "repos": repos, "sources": sources, "persisted": persisted}


def _invoke(harness: dict[str, object], **overrides: object) -> Any:
    repos = harness["repos"]
    assert isinstance(repos, dict)
    kwargs: dict[str, object] = {
        "identity": _identity(),
        "case_matter_id": MATTER_ID,
        "acceptance_context_id": CONTEXT_ID,
        "replay_key": REPLAY_KEY,
        "instrument_id": INSTRUMENT_ID,
        "matter_lifecycle_collection": object(),
        "visibility_collection": object(),
        "party_collection": object(),
        "capacity_collection": object(),
        "instrument_collection": object(),
        "instrument_lifecycle_collection": object(),
        "approval_collection": object(),
        "context_collection": object(),
        "authorization_evidence_registry": harness["issuer"],
        "principal_repository": repos["principal"],
        "membership_repository": repos["membership"],
        "business_role_repository": repos["business"],
        "role_assignment_repository": repos["role"],
        "session": Session(),
        "clock": lambda: NOW,
    }
    kwargs.update(overrides)
    return orchestrator.compose_legal_client_acceptance_context(**cast(dict[str, Any], kwargs))


def test_authenticated_client_composes_server_bound_context_and_issuer(harness: dict[str, object]) -> None:
    result = _invoke(harness)
    assert result.tenant_id == TENANT
    assert result.actor_principal_id == PRINCIPAL
    persisted = cast(list[FakeContext], harness["persisted"])
    assert len(persisted) == 1
    issuer = harness["issuer"]
    assert isinstance(issuer, FakeIssuer) and len(issuer.calls) == 1
    assert cast(Session, issuer.calls[0]["session"]).in_transaction is True
    assert issuer.calls[0]["permission"] == orchestrator.PERMISSION
    assert result.expires_at - result.issued_at == orchestrator.CONTEXT_LIFETIME


def test_missing_or_inactive_membership_is_denied(harness: dict[str, object], monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(orchestrator, "authorize_tenant_operation", lambda **_kwargs: TenantAuthorizationDecision(False, TenantAuthorizationReason.MEMBERSHIP_INACTIVE))
    with pytest.raises(orchestrator.LegalClientAcceptanceContextOrchestrationError) as error:
        _invoke(harness)
    assert error.value.code == "L9A4_P2C3_LEGAL_CLIENT_AUTHORIZATION_REQUIRED"


def test_wrong_role_is_denied(harness: dict[str, object], monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(orchestrator, "authorize_tenant_operation", lambda **_kwargs: TenantAuthorizationDecision(True, TenantAuthorizationReason.AUTHORIZED, "tenant_legal_partner", "LEGAL_PARTNER"))
    with pytest.raises(orchestrator.LegalClientAcceptanceContextOrchestrationError):
        _invoke(harness)


def test_tenant_and_principal_are_server_derived(harness: dict[str, object]) -> None:
    result = _invoke(harness)
    assert result.tenant_id == TENANT and result.actor_principal_id == PRINCIPAL
    source = open(orchestrator.__file__, encoding="utf-8").read()
    signature = source.split("def compose_legal_client_acceptance_context", 1)[1].split(") ->", 1)[0]
    assert "tenant_id: str" not in signature and "principal_id: str" not in signature


def test_missing_transaction_rejects_before_reads(harness: dict[str, object]) -> None:
    with pytest.raises(orchestrator.LegalClientAcceptanceContextOrchestrationError) as error:
        _invoke(harness, session=None)
    assert error.value.code == "L9A4_P2C3_ACTIVE_TRANSACTION_REQUIRED"


def test_inactive_identity_rejects(harness: dict[str, object]) -> None:
    with pytest.raises(orchestrator.LegalClientAcceptanceContextOrchestrationError) as error:
        _invoke(harness, identity=_identity(PrincipalStatus.SUSPENDED))
    assert error.value.code == "L9A4_P2C3_PRINCIPAL_INACTIVE"


def test_missing_visibility_rejects(harness: dict[str, object], monkeypatch: pytest.MonkeyPatch) -> None:
    def absent(*_args: object, **_kwargs: object) -> object:
        raise orchestrator.visibility_registry.LegalClientMatterVisibilityNotFoundError("NOT_FOUND")
    monkeypatch.setattr(orchestrator.visibility_registry.LegalClientMatterVisibilityRegistry, "resolve_current_active", staticmethod(absent))
    with pytest.raises(orchestrator.LegalClientAcceptanceContextOrchestrationError) as error:
        _invoke(harness)
    assert error.value.code == "L9A4_P2C3_ACTIVE_VISIBILITY_REQUIRED"


def test_closed_matter_rejects(harness: dict[str, object], monkeypatch: pytest.MonkeyPatch) -> None:
    closed = _matter().transition_to(
        CaseMatterState.CLOSED,
        evidence_reference="matter-close:1",
        occurred_at=NOW + timedelta(seconds=1),
    )
    monkeypatch.setattr(orchestrator.matter_registry.LegalOperationsLifecycleRegistry, "get_entity_history", staticmethod(lambda *_args, **_kwargs: (closed,)))
    with pytest.raises(orchestrator.LegalClientAcceptanceContextOrchestrationError) as error:
        _invoke(harness)
    assert error.value.code == "L9A4_P2C3_CASE_MATTER_NOT_OPEN"


@pytest.mark.parametrize("count", [0, 2])
def test_zero_or_ambiguous_party_capacity_rejects(harness: dict[str, object], monkeypatch: pytest.MonkeyPatch, count: int) -> None:
    source = harness["sources"]
    assert isinstance(source, dict)
    capacities = tuple(source["capacity"] for _ in range(count))
    monkeypatch.setattr(orchestrator.capacity_registry, "list_valid_capacities_at", lambda *_args, **_kwargs: capacities)
    with pytest.raises(orchestrator.LegalClientAcceptanceContextOrchestrationError):
        _invoke(harness)


def test_stale_instrument_cannot_be_selected(harness: dict[str, object], monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(orchestrator.instrument_registry, "get_latest_effective_version", lambda *_args, **_kwargs: None)
    with pytest.raises(orchestrator.LegalClientAcceptanceContextOrchestrationError) as error:
        _invoke(harness)
    assert error.value.code == "L9A4_P2C3_LATEST_INSTRUMENT_REQUIRED"


@pytest.mark.parametrize(
    "status",
    [
        LegalClientMatterAcceptanceInstrumentLifecycleStatus.SUPERSEDED,
        LegalClientMatterAcceptanceInstrumentLifecycleStatus.RETIRED,
        LegalClientMatterAcceptanceInstrumentLifecycleStatus.WITHDRAWN,
    ],
)
def test_terminal_lifecycle_rejects(
    harness: dict[str, object], status: LegalClientMatterAcceptanceInstrumentLifecycleStatus
) -> None:
    source = harness["sources"]
    assert isinstance(source, dict)
    lifecycle = source["lifecycle"]
    assert isinstance(lifecycle, SimpleNamespace)
    lifecycle.status = status
    with pytest.raises(orchestrator.LegalClientAcceptanceContextOrchestrationError):
        _invoke(harness)


def test_missing_approval_rejects(harness: dict[str, object], monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(orchestrator.approval_registry, "get_current_approval", lambda *_args, **_kwargs: None)
    with pytest.raises(orchestrator.LegalClientAcceptanceContextOrchestrationError) as error:
        _invoke(harness)
    assert error.value.code == "L9A4_P2C3_CURRENT_APPROVAL_REQUIRED"


def test_exact_replay_preserves_original_chronology(harness: dict[str, object], monkeypatch: pytest.MonkeyPatch) -> None:
    first = _invoke(harness)
    existing = FakeContext()
    monkeypatch.setattr(orchestrator.context_registry, "list_contexts_for_actor", lambda *_args, **_kwargs: (existing,))
    replay = _invoke(harness)
    assert replay.to_dict() == first.to_dict()


def test_divergent_replay_rejects(harness: dict[str, object], monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(orchestrator.context_registry, "list_contexts_for_actor", lambda *_args, **_kwargs: (FakeContext(context_id="other-context"),))
    with pytest.raises(orchestrator.LegalClientAcceptanceContextOrchestrationError) as error:
        _invoke(harness)
    assert error.value.code == "L9A4_P2C3_CONTEXT_REPLAY_CONFLICT"


def test_same_session_is_forwarded_to_iam_and_issuer(harness: dict[str, object]) -> None:
    session = Session()
    _invoke(harness, session=session)
    repos = harness["repos"]
    assert isinstance(repos, dict)
    assert all(call[1]["session"] is session for repo in repos.values() for call in repo.calls)
    issuer = harness["issuer"]
    assert isinstance(issuer, FakeIssuer) and issuer.calls[0]["session"] is session


def test_no_downstream_authorities_are_imported_or_called() -> None:
    import ast

    source = open(orchestrator.__file__, encoding="utf-8").read()
    tree = ast.parse(source)
    imported = {
        alias.name
        for node in ast.walk(tree)
        if isinstance(node, ast.Import)
        for alias in node.names
    }
    imported.update(
        alias.name
        for node in ast.walk(tree)
        if isinstance(node, ast.ImportFrom)
        for alias in node.names
    )
    assert "LegalClientAcceptanceRegistry" not in imported
    assert "requests" not in imported and "httpx" not in imported
    called = {
        node.func.attr
        for node in ast.walk(tree)
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute)
    }
    assert not {"start_transaction", "commit_transaction", "abort_transaction"} & called


def test_public_authority_constants_are_narrow() -> None:
    assert orchestrator.PERMISSION == "legal_operations:client_matter:read"
    assert orchestrator.OPERATION == "legal_client_matter_read"
    assert orchestrator.CONTEXT_LIFETIME == timedelta(minutes=10)


# ARTIFACT: test_legal_client_acceptance_context_orchestrator.py
# VERSION: v1.0.0-L9A4-P2C3-CLIENT-ACCEPTANCE-CONTEXT-COMPOSER-CERT
# AUTHORITY BOUNDARY: direct composition certificate only
# TENANT POSTURE: authenticated exact tenant/principal and current visibility/source scope
# FAIL-CLOSED POSTURE: inactive, denied, stale, terminal, ambiguous and divergent paths reject
# FINANCIAL EXECUTION AUTHORITY: none; Kennel EOS exclusively
# END OF WILSY OS SOVEREIGN ARTIFACT
