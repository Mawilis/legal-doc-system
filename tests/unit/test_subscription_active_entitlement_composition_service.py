"""D22B3 P42 subscription-active entitlement service direct certificate.

TITLE: Subscription Active Entitlement Composition Service Direct Certificate
VERSION: v1.0.0-D22B3-P42-SUBSCRIPTION-ACTIVE-ENTITLEMENT-COMPOSITION-SERVICE-CERT
AUTHORITY: Wilsy OS Core Governance
EPITOME: Directly certify exact Legal-only product authority, canonical runtime
         bindings, shared transaction ordering, deterministic lifecycle replay
         coordinates, bounded whole-transaction retry and commit uncertainty.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tests/unit/test_subscription_active_entitlement_composition_service.py
COLLABORATION / OWNERSHIP: Deterministic doubles certify the P42 service while
                            SubscriptionRegistry and D22B3 P25 retain their own
                            sealed direct certificates.
CERTIFICATION / UPDATE DATE: 2026-10-09
CHANGELOG: v1.0.0-D22B3-P42-SUBSCRIPTION-ACTIVE-ENTITLEMENT-COMPOSITION-SERVICE-CERT
           establishes the bounded 34-point direct unit certificate.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2.
SECURITY / PRIVACY POSTURE: Synthetic opaque identities only; no credentials.
TENANT BOUNDARY: Tests prove exact identity-derived tenant/principal propagation.
AUTHORITY BOUNDARY: Certificate only; no runtime, IAM, commercial or financial
                    authority is created.
FINANCIAL AUTHORITY BOUNDARY: Kennel EOS exclusively.
"""
from __future__ import annotations

import ast
from collections.abc import Sequence
from dataclasses import FrozenInstanceError
from datetime import datetime, timezone
import inspect
from pathlib import Path
from typing import Any, cast

import pytest
from pymongo.errors import PyMongoError

from tools.eos.auth.identity import SovereignIdentity
from tools.eos.auth.principal_status import PrincipalStatus
from tools.eos.saas.billing import (
    subscription_active_entitlement_composition_service as service,
)
from tools.eos.saas.domain.subscription import (
    AuditAction,
    AuditEntry,
    BillingFrequency,
    PlanTiers,
    SubscriptionEntity,
    SubscriptionStatus,
)
from tools.eos.saas.entitlement.product_catalogue import TenantProductId
from tools.eos.saas.entitlement.tenant_product_entitlement_issuance_orchestrator import (
    TenantProductEntitlementIssuanceCompositionError,
)


NOW = datetime(2026, 10, 9, 12, 0, tzinfo=timezone.utc)


def identity() -> SovereignIdentity:
    """Return one active canonical synthetic identity."""
    return SovereignIdentity(
        identity_id="principal-p42",
        tenant_id="tenant-p42",
        username=None,
        email=None,
        roles=[],
        permissions=[],
        auth_method="synthetic",
        status=PrincipalStatus.ACTIVE,
    )


def entity(
    operation: str = "create",
    *,
    status: SubscriptionStatus = SubscriptionStatus.ACTIVE,
    features: tuple[str, ...] = ("legal.core",),
    proof: str = "a" * 128,
    timestamp: datetime = NOW,
) -> SubscriptionEntity:
    """Build canonical resulting subscription truth with immutable audit proof."""
    action = AuditAction(operation)
    audit = AuditEntry(
        action=action,
        timestamp=timestamp,
        previous_status=(
            SubscriptionStatus.PAUSED
            if action is AuditAction.RESUME
            else SubscriptionStatus.CANCELLED
            if action is AuditAction.REACTIVATE
            else None
        ),
        new_status=status,
        proof_hash=proof,
    )
    return SubscriptionEntity(
        tenant_id="tenant-p42",
        plan_id="plan-p42",
        plan=PlanTiers.PROFESSIONAL,
        amount=100.0,
        currency="ZAR",
        billing_frequency=BillingFrequency.MONTHLY,
        start_date=NOW,
        current_period_start=NOW,
        current_period_end=datetime(2026, 11, 9, 12, 0, tzinfo=timezone.utc),
        idempotency_key="commercial-create-key",
        subscription_id="subscription-p42",
        plan_features=features,
        status=status,
        proof_hash=proof,
        audit_trail=[audit],
    )


class LabeledError(PyMongoError):
    """Minimal PyMongo-style labeled error used for retry classification."""

    def __init__(self, *labels: str, code: int | None = None) -> None:
        super().__init__("synthetic")
        self.labels = set(labels)
        self.code = code

    def has_error_label(self, label: str) -> bool:
        """Return exact synthetic error-label membership."""
        return label in self.labels


class Session:
    """Record exact transaction lifecycle and configurable failures."""

    def __init__(
        self,
        events: list[str],
        *,
        commit_error: BaseException | None = None,
    ) -> None:
        self.events = events
        self.commit_error = commit_error
        self.in_transaction = False

    def __enter__(self) -> "Session":
        return self

    def __exit__(self, *_args: object) -> None:
        return None

    def start_transaction(self) -> None:
        self.events.append("start")
        self.in_transaction = True

    def commit_transaction(self) -> None:
        self.events.append("commit")
        if self.commit_error is not None:
            raise self.commit_error
        self.in_transaction = False

    def abort_transaction(self) -> None:
        self.events.append("abort")
        self.in_transaction = False


class Client:
    """Create one fresh deterministic session per whole-transaction attempt."""

    def __init__(self, sessions: list[Session]) -> None:
        self.sessions = sessions
        self.calls = 0

    def start_session(self) -> Session:
        value = self.sessions[self.calls]
        self.calls += 1
        return value


class Database:
    """Record exact canonical collection resolution."""

    def __init__(self) -> None:
        self.collections: dict[str, object] = {}
        self.lookups: list[str] = []

    def __getitem__(self, name: str) -> object:
        self.lookups.append(name)
        return self.collections.setdefault(name, object())


class Registry:
    """Configurable commercial participant with no transaction ownership."""

    operation = "create"
    values: list[object] = []
    calls: list[tuple[str, tuple[object, ...], dict[str, object]]] = []

    @classmethod
    def reset(cls, operation: str, *values: object) -> None:
        cls.operation = operation
        cls.values = list(values)
        cls.calls = []

    @classmethod
    def _call(cls, name: str, args: tuple[object, ...], kwargs: dict[str, object]) -> object:
        cls.calls.append((name, args, kwargs))
        value = cls.values.pop(0)
        if isinstance(value, BaseException):
            raise value
        return value

    @classmethod
    def create(cls, *args: object, **kwargs: object) -> object:
        return cls._call("create", args, kwargs)

    @classmethod
    def resume(cls, *args: object, **kwargs: object) -> object:
        return cls._call("resume", args, kwargs)

    @classmethod
    def reactivate(cls, *args: object, **kwargs: object) -> object:
        return cls._call("reactivate", args, kwargs)


def commercial(value: SubscriptionEntity) -> dict[str, object]:
    """Return one successful canonical registry result."""
    return {"success": True, "subscription": value, "replayed": False}


def install(
    monkeypatch: pytest.MonkeyPatch,
    registry_values: list[object],
    *,
    operation: str = "create",
    sessions: list[Session] | None = None,
    issue_values: Sequence[object] | None = None,
) -> tuple[Database, Client, list[dict[str, object]], list[tuple[object, dict[str, object]]]]:
    """Install canonical deterministic dependency doubles for one invocation."""
    events: list[str] = []
    configured_sessions = sessions or [Session(events)]
    client = Client(configured_sessions)
    database = Database()
    Registry.reset(operation, *registry_values)
    issue_calls: list[dict[str, object]] = []
    constructed: list[tuple[object, dict[str, object]]] = []
    values = list(issue_values or [object()] * len(registry_values))

    def issue(**kwargs: object) -> object:
        issue_calls.append(kwargs)
        configured_sessions[client.calls - 1].events.append("issue")
        value = values.pop(0)
        if isinstance(value, BaseException):
            raise value
        return value

    def evidence_registry(collection: object, **kwargs: object) -> object:
        constructed.append((collection, kwargs))
        return object()

    monkeypatch.setattr(service, "get_client", lambda: client)
    monkeypatch.setattr(service, "get_database", lambda: database)
    monkeypatch.setattr(service, "SubscriptionRegistry", Registry)
    monkeypatch.setattr(service, "issue_tenant_product_entitlement", issue)
    monkeypatch.setattr(service, "TenantAuthorizationDecisionEvidenceRegistry", evidence_registry)
    return database, client, issue_calls, constructed


def invoke(operation: str) -> Any:
    """Invoke one exact public surface without hidden caller transaction input."""
    if operation == "create":
        return service.SubscriptionActiveEntitlementCompositionService.create(
            {"idempotencyKey": "commercial-create-key"}, identity()
        )
    method = getattr(service.SubscriptionActiveEntitlementCompositionService, operation)
    return method("subscription-p42", {"reason": "certificate"}, identity())


def test_import_version_result_contract_and_immutable_result() -> None:
    """Certify version metadata and immutable typed minimum result contract."""
    assert service.VERSION == (
        "v1.0.0-D22B3-P42-SUBSCRIPTION-ACTIVE-ENTITLEMENT-COMPOSITION-SERVICE"
    )
    value = service.SubscriptionActiveEntitlementCompositionResult(
        commercial_result={},
        subscription=entity(),
        legal_entitlement_applicable=False,
        entitlement_issuance_result=None,
    )
    with pytest.raises(FrozenInstanceError):
        value.legal_entitlement_applicable = True  # type: ignore[misc]


def test_public_api_exposes_no_product_session_transaction_or_runtime_authority() -> None:
    """Certify exact bounded caller surfaces for later router replacement."""
    cls = service.SubscriptionActiveEntitlementCompositionService
    assert list(inspect.signature(cls.create).parameters) == ["payload", "identity"]
    assert list(inspect.signature(cls.resume).parameters) == [
        "subscription_id", "metadata", "identity"
    ]
    assert list(inspect.signature(cls.reactivate).parameters) == [
        "subscription_id", "metadata", "identity"
    ]
    forbidden = {"product_id", "session", "transaction", "database", "client"}
    assert all(
        forbidden.isdisjoint(inspect.signature(method).parameters)
        for method in (cls.create, cls.resume, cls.reactivate)
    )


@pytest.mark.parametrize(
    ("operation", "value"),
    [
        ("create", entity("create")),
        ("resume", entity("resume")),
        ("reactivate", entity("reactivate")),
    ],
)
def test_active_legal_operations_issue_in_exact_shared_transaction(
    monkeypatch: pytest.MonkeyPatch,
    operation: str,
    value: SubscriptionEntity,
) -> None:
    """Certify create, PAUSED resume and CANCELLED reactivate positive flows."""
    events: list[str] = []
    session = Session(events)
    database, client, issue_calls, _ = install(
        monkeypatch, [commercial(value)], operation=operation, sessions=[session]
    )
    result = invoke(operation)
    assert result.subscription is value
    assert result.legal_entitlement_applicable is True
    assert result.entitlement_issuance_result is not None
    assert client.calls == 1 and events == ["start", "issue", "commit"]
    assert len(Registry.calls) == 1 and Registry.calls[0][0] == operation
    call = Registry.calls[0][2]
    assert call["collection"] is database.collections[service.SUBSCRIPTION_COLLECTION]
    assert call["session"] is session
    issued = issue_calls[0]
    assert issued["product_id"] is TenantProductId.LEGAL_OPERATIONS
    assert issued["identity"] == identity()
    assert issued["session"] is session
    assert issued["subscription_registry"] is Registry
    occurred_at = issued["occurred_at"]
    assert isinstance(occurred_at, datetime)
    assert occurred_at.utcoffset() == timezone.utc.utcoffset(occurred_at)


@pytest.mark.parametrize(
    "value",
    [
        entity(features=("legal.core.read",)),
        entity(status=SubscriptionStatus.PAUSED),
    ],
)
def test_exact_feature_and_active_status_trigger_skip_entitlement(
    monkeypatch: pytest.MonkeyPatch,
    value: SubscriptionEntity,
) -> None:
    """ACTIVE without exact legal.core and non-ACTIVE both commit commercial only."""
    events: list[str] = []
    _database, _client, issue_calls, _constructed = install(
        monkeypatch, [commercial(value)], sessions=[Session(events)]
    )
    result = invoke("create")
    assert result.legal_entitlement_applicable is False
    assert result.entitlement_issuance_result is None
    assert issue_calls == [] and events == ["start", "commit"]


def test_commercial_failure_aborts_before_issuance(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Commercial rejection aborts and cannot create entitlement evidence."""
    events: list[str] = []
    _database, _client, calls, _constructed = install(
        monkeypatch,
        [{"success": False, "error": "denied"}],
        sessions=[Session(events)],
    )
    with pytest.raises(service.SubscriptionActiveEntitlementCompositionLifecycleError):
        invoke("create")
    assert calls == [] and events == ["start", "abort"]


def test_entitlement_failure_aborts_commercial_transaction(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Sealed issuer failure aborts shared commercial work and never commits."""
    events: list[str] = []
    failure = TenantProductEntitlementIssuanceCompositionError("synthetic")
    install(
        monkeypatch,
        [commercial(entity())],
        sessions=[Session(events)],
        issue_values=[failure],
    )
    with pytest.raises(service.SubscriptionActiveEntitlementCompositionIssuanceError):
        invoke("create")
    assert events == ["start", "issue", "abort"]


def test_transient_error_retries_complete_commercial_and_entitlement_work(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Safe transient issuance failure restarts both participants from scratch."""
    first_events: list[str] = []
    second_events: list[str] = []
    transient = LabeledError("TransientTransactionError")
    _database, client, issue_calls, _constructed = install(
        monkeypatch,
        [commercial(entity()), commercial(entity())],
        sessions=[Session(first_events), Session(second_events)],
        issue_values=[transient, object()],
    )
    result = invoke("create")
    assert result.legal_entitlement_applicable is True
    assert client.calls == 2 and len(Registry.calls) == 2 and len(issue_calls) == 2
    assert first_events == ["start", "issue", "abort"]
    assert second_events == ["start", "issue", "commit"]


def test_retry_exhaustion_fails_closed_after_exact_bound(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Every transient attempt aborts and the bounded ceiling rejects."""
    event_sets = [[] for _ in range(service.MAX_TRANSACTION_ATTEMPTS)]
    sessions = [Session(events) for events in event_sets]
    transient = LabeledError(code=112)
    install(
        monkeypatch,
        [commercial(entity())] * service.MAX_TRANSACTION_ATTEMPTS,
        sessions=sessions,
        issue_values=[transient] * service.MAX_TRANSACTION_ATTEMPTS,
    )
    with pytest.raises(service.SubscriptionActiveEntitlementCompositionRetryExhaustedError):
        invoke("create")
    assert len(Registry.calls) == service.MAX_TRANSACTION_ATTEMPTS
    assert all(events == ["start", "issue", "abort"] for events in event_sets)


def test_unknown_commit_result_never_replays_operation_or_returns_success(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Commit uncertainty raises its typed error after one commercial attempt."""
    events: list[str] = []
    install(
        monkeypatch,
        [commercial(entity())],
        sessions=[Session(events, commit_error=LabeledError("UnknownTransactionCommitResult"))],
    )
    with pytest.raises(service.SubscriptionActiveEntitlementCompositionUnknownCommitError):
        invoke("create")
    assert len(Registry.calls) == 1
    assert events[:3] == ["start", "issue", "commit"]
    assert events.count("commit") == 1


@pytest.mark.parametrize("operation", ["create", "resume", "reactivate"])
def test_deterministic_operation_distinct_idempotency(
    operation: str,
) -> None:
    """Exact canonical lifecycle evidence deterministically names each operation."""
    value = entity(operation)
    first = service._issuance_idempotency(operation, value)
    second = service._issuance_idempotency(operation, value)
    assert first == second
    assert first.startswith(f"{service.IDEMPOTENCY_NAMESPACE}:{operation}:")
    assert len(first) == 64


def test_idempotency_changes_with_authoritative_lifecycle_mutation() -> None:
    """Lifecycle proof changes alter issuance replay identity without random input."""
    first = service._issuance_idempotency("resume", entity("resume", proof="a" * 128))
    second = service._issuance_idempotency("resume", entity("resume", proof="b" * 128))
    assert first != second
    assert service._issuance_idempotency("create", entity("create")) != (
        service._issuance_idempotency("resume", entity("resume"))
    )


def test_exact_replay_reuses_issuance_key_at_service_boundary(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Two exact canonical create replays delegate one stable issuer lineage key."""
    first_events: list[str] = []
    second_events: list[str] = []
    value = entity()
    _database, _client, calls, _constructed = install(
        monkeypatch,
        [commercial(value), commercial(value)],
        sessions=[Session(first_events), Session(second_events)],
        issue_values=[object(), object()],
    )
    invoke("create")
    invoke("create")
    assert calls[0]["idempotency_key"] == calls[1]["idempotency_key"]


def test_exact_collections_and_authorization_repository_construction(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Resolve only canonical persistence names and canonical IAM repositories."""
    database, _client, issue_calls, constructed = install(
        monkeypatch, [commercial(entity())]
    )
    invoke("create")
    assert database.lookups == [
        service.SUBSCRIPTION_COLLECTION,
        service.ENTITLEMENT_HISTORY_COLLECTION,
        service.ENTITLEMENT_CURRENT_COLLECTION,
        service.AUTHORIZATION_EVIDENCE_COLLECTION,
    ]
    collection, kwargs = constructed[0]
    assert collection is database.collections[service.AUTHORIZATION_EVIDENCE_COLLECTION]
    assert kwargs == {
        "principal_repository": service.PrincipalAuthorityRepository,
        "membership_repository": service.TenantMembershipRepository,
        "role_assignment_repository": service.RoleAssignmentRepository,
        "business_role_repository": service.RoleAssignmentRepository,
    }
    assert issue_calls[0]["authorization_evidence_registry"] is not None


def test_runtime_dependency_absence_fails_before_session_or_mutation(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Missing canonical runtime fails closed without fabricated persistence."""
    monkeypatch.setattr(service, "get_client", lambda: None)
    monkeypatch.setattr(service, "get_database", lambda: None)
    with pytest.raises(service.SubscriptionActiveEntitlementCompositionDependencyError):
        invoke("create")


def test_identity_is_only_tenant_and_principal_authority(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Commercial tenant and downstream tenant/principal source are one identity."""
    _database, _client, calls, _constructed = install(
        monkeypatch, [commercial(entity())]
    )
    invoke("create")
    assert Registry.calls[0][1][1] == "tenant-p42"
    issued_identity = cast(SovereignIdentity, calls[0]["identity"])
    assert issued_identity.tenant_id == "tenant-p42"
    assert issued_identity.identity_id == "principal-p42"


def test_static_authority_exclusions_and_participant_transaction_boundaries() -> None:
    """Certify no CRM/Billing/HR inference or financial/participant ownership."""
    path = Path(service.__file__)
    source = path.read_text(encoding="utf-8")
    tree = ast.parse(source)
    imports = {
        alias.name
        for node in ast.walk(tree)
        if isinstance(node, (ast.Import, ast.ImportFrom))
        for alias in node.names
    }
    assert not any("crm" in name.lower() for name in imports)
    assert "TenantProductId.LEGAL_OPERATIONS" in source
    assert "TenantProductId.CRM" not in source
    assert "TenantProductId.BILLING" not in source
    assert "TenantProductId.HR" not in source
    for forbidden in (
        "payment execution", "settlement authority", "financial execution",
    ):
        assert forbidden in source.lower()
    registry_source = Path(inspect.getfile(service.SubscriptionRegistry)).read_text(
        encoding="utf-8"
    )
    issuer_source = Path(inspect.getfile(service.issue_tenant_product_entitlement)).read_text(
        encoding="utf-8"
    )
    for participant in (registry_source, issuer_source):
        for token in ("start_transaction(", "commit_transaction(", "abort_transaction("):
            assert token not in participant


def test_service_source_orders_issuance_before_commit_and_return() -> None:
    """Static ordering proves no committed result exists before commit succeeds."""
    source = inspect.getsource(service._run)
    assert source.index("issue_tenant_product_entitlement(") < source.index(
        "session.commit_transaction()"
    ) < source.index("return SubscriptionActiveEntitlementCompositionResult(")


# WILSY OS SOVEREIGN ARTIFACT SEAL
# ARTIFACT: test_subscription_active_entitlement_composition_service.py
# VERSION: v1.0.0-D22B3-P42-SUBSCRIPTION-ACTIVE-ENTITLEMENT-COMPOSITION-SERVICE-CERT
# AUTHORITY BOUNDARY: deterministic direct unit certification only
# TENANT POSTURE: synthetic exact SovereignIdentity tenant/principal evidence
# FAIL-CLOSED POSTURE: every negative boundary asserts rejection or abort
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively
# END OF WILSY OS SOVEREIGN ARTIFACT
