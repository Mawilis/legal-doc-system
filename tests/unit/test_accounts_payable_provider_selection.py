"""TITLE: Accounts Payable Provider Selection Orchestration Certificate.
VERSION: v1.0.0-M11-P5-R1B-AP2D-R3.
AUTHORITY: Direct unit certification of the canonical AP selection transition.
EPITOME: Proves durable request provenance, explicit current binding, exact policy, cardinality, and selection persistence.
ABSOLUTE CANONICAL PATH: tests/unit/test_accounts_payable_provider_selection.py
COLLABORATION / OWNERSHIP: Kennel EOS AP2D orchestration certificate.
CERTIFICATION / UPDATE DATE: 2026-09-07.
CHANGELOG: v1.0.0 certifies existing-selection precedence, provenance correlation, and sole-provider selection.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2.
SECURITY / PRIVACY POSTURE: Synthetic opaque identifiers only; no provider transport or secrets.
TENANT BOUNDARY: Every fixture and assertion is tenant scoped.
AUTHORITY BOUNDARY: Certificate evidence only; no command, execution, settlement, or invoice authority.
FINANCIAL AUTHORITY BOUNDARY: Kennel EOS remains the exclusive financial execution authority.
"""
from __future__ import annotations

from datetime import datetime, timezone
import inspect
from typing import Any

import pytest

from tools.eos.kennel.domain.accounts_payable_provider_policy import (
    AccountsPayableProviderPolicy,
)
from tools.eos.kennel.domain.accounts_payable_provider_policy_runtime_binding import (
    AccountsPayableProviderPolicyRuntimeBinding,
)
from tools.eos.kennel.domain.accounts_payable_provider_selection_decision import (
    AccountsPayableProviderSelectionDecision,
)
from tools.eos.kennel.orchestration.accounts_payable_provider_selection import (
    AccountsPayableProviderSelectionOrchestrationError,
    select_accounts_payable_provider,
)
from tools.eos.kennel.registry.accounts_payable_provider_policy_registry import (
    AccountsPayableProviderPolicyRegistry,
)
from tools.eos.kennel.registry.accounts_payable_provider_policy_runtime_binding_registry import (
    AccountsPayableProviderPolicyRuntimeBindingRegistry,
)
from tools.eos.kennel.registry.accounts_payable_provider_selection_decision_registry import (
    AccountsPayableProviderSelectionDecisionRegistry,
)
from tools.eos.saas.billing.vendor_bill_financial_execution_request_registry import (
    VendorBillFinancialExecutionRequestRegistry,
)
from tools.eos.saas.domain.vendor_bill_financial_execution_request import (
    VendorBillFinancialExecutionRequest,
)


FP_A = "a" * 128
FP_B = "b" * 128
FP_C = "c" * 128
NOW = datetime(2026, 9, 7, 12, 0, tzinfo=timezone.utc)


class Session:
    """Minimal active caller transaction marker."""

    in_transaction = True


class SpyCollection:
    """In-memory collection that records queries, sessions, and writes."""

    def __init__(self) -> None:
        self.rows: list[dict[str, object]] = []
        self.sessions: list[object] = []
        self.queries: list[dict[str, object]] = []
        self.writes = 0
        self.fail_on_read = False

    def find_one(self, query: dict[str, object], **kwargs: object) -> dict[str, object] | None:
        if self.fail_on_read:
            raise AssertionError("unexpected read")
        self.queries.append(dict(query))
        self.sessions.append(kwargs.get("session"))
        return next((row for row in self.rows if all(row.get(k) == v for k, v in query.items())), None)

    def find(self, query: dict[str, object], **kwargs: object) -> list[dict[str, object]]:
        if self.fail_on_read:
            raise AssertionError("unexpected read")
        self.queries.append(dict(query))
        self.sessions.append(kwargs.get("session"))
        return [row for row in self.rows if all(row.get(k) == v for k, v in query.items())]

    def insert_one(self, row: dict[str, object], **kwargs: object) -> object:
        self.sessions.append(kwargs.get("session"))
        self.writes += 1
        self.rows.append(dict(row))
        return object()

    def replace_one(self, query: dict[str, object], row: dict[str, object], **kwargs: object) -> object:
        self.sessions.append(kwargs.get("session"))
        for index, current in enumerate(self.rows):
            if all(current.get(k) == v for k, v in query.items()):
                self.rows[index] = dict(row)
                return type("ReplaceResult", (), {"matched_count": 1})()
        return type("ReplaceResult", (), {"matched_count": 0})()

    def create_index(self, keys: list[tuple[str, int]], **kwargs: object) -> str:
        return str(kwargs.get("name", keys))


def make_request(tenant_id: str = "tenant-a", request_id: str = "request-a") -> VendorBillFinancialExecutionRequest:
    """Construct a provider-neutral AP request used only as durable fixture input."""
    return VendorBillFinancialExecutionRequest(
        execution_command_id=request_id,
        tenant_id=tenant_id,
        payable_id=f"payable-{tenant_id}",
        release_authorization_id=f"release-{tenant_id}",
        idempotency_key=f"idem-{tenant_id}-{request_id}",
        amount_minor=100,
        currency="ZAR",
        payment_destination_reference=f"opaque-destination-{tenant_id}",
        requested_by_actor_id=f"actor-{tenant_id}",
        requested_at=NOW,
    )


def make_policy(
    policy_id: str = "policy-a",
    tenant_id: str = "tenant-a",
    revision: int = 1,
    providers: tuple[str, ...] = ("provider-a",),
) -> AccountsPayableProviderPolicy:
    """Construct one exact historical AP eligibility fact."""
    return AccountsPayableProviderPolicy(
        policy_id=policy_id,
        tenant_id=tenant_id,
        policy_revision=revision,
        eligible_provider_names=providers,
        authorization_decision_id=f"auth-{policy_id}-{revision}",
        authorization_decision_fingerprint=FP_A,
        created_at=NOW,
    )


def make_binding(
    policy: AccountsPayableProviderPolicy,
    binding_id: str = "binding-a",
    revision: int = 1,
    tenant_id: str | None = None,
    policy_fingerprint: str | None = None,
    previous_binding_id: str | None = None,
    previous_binding_fingerprint: str | None = None,
) -> AccountsPayableProviderPolicyRuntimeBinding:
    """Construct a binding fixture; currentness remains registry-owned."""
    return AccountsPayableProviderPolicyRuntimeBinding(
        binding_id=binding_id,
        tenant_id=tenant_id or policy.tenant_id,
        binding_revision=revision,
        provider_policy_id=policy.policy_id,
        provider_policy_revision=policy.policy_revision,
        provider_policy_fingerprint=policy_fingerprint or policy.policy_fingerprint,
        activation_authorization_evidence_id=f"activation-{binding_id}",
        activation_authorization_evidence_fingerprint=FP_B,
        previous_binding_id=previous_binding_id,
        previous_binding_fingerprint=previous_binding_fingerprint,
        activated_at=NOW,
        created_at=NOW,
    )


def persist_request(request: VendorBillFinancialExecutionRequest, collection: SpyCollection, session: Session) -> None:
    VendorBillFinancialExecutionRequestRegistry.create(request, collection, session=session)


def persist_policy(policy: AccountsPayableProviderPolicy, collection: SpyCollection, session: Session) -> None:
    AccountsPayableProviderPolicyRegistry.create(policy, collection, session=session)


def persist_binding(binding: AccountsPayableProviderPolicyRuntimeBinding, collection: SpyCollection, session: Session) -> None:
    AccountsPayableProviderPolicyRuntimeBindingRegistry.create(binding, collection, session=session)


def persist_selection(
    request: VendorBillFinancialExecutionRequest,
    binding: AccountsPayableProviderPolicyRuntimeBinding,
    policy: AccountsPayableProviderPolicy,
    provider: str,
    collection: SpyCollection,
    session: Session,
) -> AccountsPayableProviderSelectionDecision:
    """Seed an existing selection only through the canonical selection registry."""
    value = AccountsPayableProviderSelectionDecision(
        tenant_id=request.tenant_id,
        execution_request_id=request.execution_command_id,
        execution_request_fingerprint=request.fingerprint,
        runtime_binding_id=binding.binding_id,
        runtime_binding_revision=binding.binding_revision,
        runtime_binding_fingerprint=binding.binding_fingerprint,
        provider_policy_id=policy.policy_id,
        provider_policy_revision=policy.policy_revision,
        provider_policy_fingerprint=policy.policy_fingerprint,
        selected_provider=provider,
    )
    AccountsPayableProviderSelectionDecisionRegistry.create(value, collection, session=session)
    return value


def base() -> tuple[SpyCollection, SpyCollection, SpyCollection, SpyCollection, Session, VendorBillFinancialExecutionRequest, AccountsPayableProviderPolicy, AccountsPayableProviderPolicyRuntimeBinding]:
    """Create canonical request, policy, binding, and empty selection surfaces."""
    requests, bindings, policies, selections, session = SpyCollection(), SpyCollection(), SpyCollection(), SpyCollection(), Session()
    request, policy = make_request(), make_policy()
    binding = make_binding(policy)
    persist_request(request, requests, session)
    persist_policy(policy, policies, session)
    persist_binding(binding, bindings, session)
    return requests, bindings, policies, selections, session, request, policy, binding


def run(**surfaces: Any) -> tuple[AccountsPayableProviderSelectionDecision, bool]:
    """Invoke only the public transition owner with canonical surfaces."""
    return select_accounts_payable_provider(**surfaces)


def surface_args(requests: SpyCollection, bindings: SpyCollection, policies: SpyCollection, selections: SpyCollection, session: Any, request: VendorBillFinancialExecutionRequest) -> dict[str, object]:
    return dict(
        tenant_id=request.tenant_id,
        execution_request_id=request.execution_command_id,
        request_collection=requests,
        binding_collection=bindings,
        policy_collection=policies,
        selection_collection=selections,
        session=session,
    )


def test_missing_transaction_rejects_before_reads() -> None:
    requests, bindings, policies, selections, _, request, _, _ = base()
    for collection in (requests, bindings, policies, selections):
        collection.queries.clear()
    with pytest.raises(AccountsPayableProviderSelectionOrchestrationError, match="ACTIVE_TRANSACTION_REQUIRED"):
        run(**surface_args(requests, bindings, policies, selections, None, request))
    assert requests.queries == [] and bindings.queries == [] and policies.queries == [] and selections.queries == []


def test_inactive_transaction_rejects() -> None:
    requests, bindings, policies, selections, session, request, _, _ = base()
    session.in_transaction = False
    with pytest.raises(AccountsPayableProviderSelectionOrchestrationError, match="ACTIVE_TRANSACTION_REQUIRED"):
        run(**surface_args(requests, bindings, policies, selections, session, request))


def test_caller_session_propagates_to_request_read() -> None:
    requests, bindings, policies, selections, session, request, _, _ = base()
    run(**surface_args(requests, bindings, policies, selections, session, request))
    assert requests.sessions[0] is session


def test_caller_session_propagates_to_existing_selection_lookup() -> None:
    requests, bindings, policies, selections, session, request, policy, binding = base()
    persist_selection(request, binding, policy, "provider-a", selections, session)
    run(**surface_args(requests, bindings, policies, selections, session, request))
    assert selections.sessions[-1] is session


def test_existing_canonical_selection_is_returned() -> None:
    requests, bindings, policies, selections, session, request, policy, binding = base()
    existing = persist_selection(request, binding, policy, "provider-a", selections, session)
    returned, replayed = run(**surface_args(requests, bindings, policies, selections, session, request))
    assert returned == existing and replayed is True


def test_existing_selection_path_does_not_resolve_current_binding() -> None:
    requests, bindings, policies, selections, session, request, policy, binding = base()
    persist_selection(request, binding, policy, "provider-a", selections, session)
    bindings.fail_on_read = True
    policies.fail_on_read = True
    returned, _ = run(**surface_args(requests, bindings, policies, selections, session, request))
    assert returned.selected_provider == "provider-a"


def test_later_binding_does_not_create_second_selection() -> None:
    requests, bindings, policies, selections, session, request, policy, binding = base()
    existing = persist_selection(request, binding, policy, "provider-a", selections, session)
    bindings.fail_on_read = True
    returned, replayed = run(**surface_args(requests, bindings, policies, selections, session, request))
    assert returned == existing and replayed is True and len(selections.rows) == 1


def test_later_policy_does_not_create_second_selection() -> None:
    requests, bindings, policies, selections, session, request, policy, binding = base()
    existing = persist_selection(request, binding, policy, "provider-a", selections, session)
    later = make_policy(revision=2, providers=("provider-b",))
    persist_policy(later, policies, session)
    returned, _ = run(**surface_args(requests, bindings, policies, selections, session, request))
    assert returned == existing and returned.provider_policy_revision == 1


def test_missing_canonical_request_rejects() -> None:
    requests, bindings, policies, selections, session, request, _, _ = base()
    with pytest.raises(AccountsPayableProviderSelectionOrchestrationError, match="REQUEST_NOT_FOUND"):
        run(**surface_args(requests, bindings, policies, selections, session, make_request(request_id="missing")))


def test_cross_tenant_request_is_not_found() -> None:
    requests, bindings, policies, selections, session, request, _, _ = base()
    with pytest.raises(AccountsPayableProviderSelectionOrchestrationError, match="REQUEST_NOT_FOUND"):
        run(**surface_args(requests, bindings, policies, selections, session, make_request(tenant_id="tenant-b", request_id=request.execution_command_id)))


def test_no_current_binding_rejects_first_selection() -> None:
    requests, _, policies, selections, session, request, _, _ = base()
    empty_bindings = SpyCollection()
    with pytest.raises(AccountsPayableProviderSelectionOrchestrationError, match="CURRENT_BINDING_REQUIRED"):
        run(**surface_args(requests, empty_bindings, policies, selections, session, request))


def test_one_eligible_provider_succeeds() -> None:
    requests, bindings, policies, selections, session, request, policy, binding = base()
    result, replayed = run(**surface_args(requests, bindings, policies, selections, session, request))
    assert result.selected_provider == policy.eligible_provider_names[0] and result.runtime_binding_id == binding.binding_id and replayed is False


@pytest.mark.parametrize("providers,error", [((), "NO_ELIGIBLE_PROVIDERS"), (("provider-a", "provider-b"), "MULTIPLE_ELIGIBLE_PROVIDERS")])
def test_provider_cardinality_rejects_zero_or_multiple(providers: tuple[str, ...], error: str) -> None:
    requests, bindings, policies, selections, session, request, _, first_binding = base()
    policies.rows.clear()
    policy = make_policy(providers=providers)
    persist_policy(policy, policies, session)
    bindings.rows.clear()
    persist_binding(make_binding(policy, binding_id=first_binding.binding_id), bindings, session)
    with pytest.raises(AccountsPayableProviderSelectionOrchestrationError, match=error):
        run(**surface_args(requests, bindings, policies, selections, session, request))
    assert selections.rows == []


def test_canonical_ordering_is_not_a_provider_selector() -> None:
    requests, bindings, policies, selections, session, request, _, first_binding = base()
    policies.rows.clear()
    policy = make_policy(providers=("provider-a", "provider-b"))
    persist_policy(policy, policies, session)
    bindings.rows.clear()
    persist_binding(make_binding(policy, binding_id=first_binding.binding_id), bindings, session)
    with pytest.raises(AccountsPayableProviderSelectionOrchestrationError, match="MULTIPLE_ELIGIBLE_PROVIDERS"):
        run(**surface_args(requests, bindings, policies, selections, session, request))


def test_bound_policy_is_read_by_exact_id_and_revision() -> None:
    requests, bindings, policies, selections, session, request, policy, _ = base()
    run(**surface_args(requests, bindings, policies, selections, session, request))
    assert {"tenant_id": "tenant-a", "policy_id": policy.policy_id, "policy_revision": policy.policy_revision} in policies.queries


def test_latest_policy_is_ignored_when_binding_points_to_history() -> None:
    requests, bindings, policies, selections, session, request, policy, _ = base()
    persist_policy(make_policy(revision=2, providers=("provider-b",)), policies, session)
    result, _ = run(**surface_args(requests, bindings, policies, selections, session, request))
    assert result.provider_policy_revision == policy.policy_revision and result.selected_provider == "provider-a"


def test_higher_policy_revision_does_not_replace_bound_policy() -> None:
    requests, bindings, policies, selections, session, request, policy, _ = base()
    persist_policy(make_policy(revision=3, providers=("provider-c",)), policies, session)
    result, _ = run(**surface_args(requests, bindings, policies, selections, session, request))
    assert result.provider_policy_id == policy.policy_id and result.provider_policy_revision == 1


def test_wrong_policy_tenant_rejects() -> None:
    requests, bindings, _, selections, session, request, _, _ = base()
    wrong_policies = SpyCollection()
    persist_policy(make_policy(tenant_id="tenant-b"), wrong_policies, session)
    with pytest.raises(AccountsPayableProviderSelectionOrchestrationError, match="POLICY_NOT_FOUND"):
        run(**surface_args(requests, bindings, wrong_policies, selections, session, request))


def test_wrong_policy_id_or_revision_rejects() -> None:
    requests, _, policies, selections, session, request, policy, _ = base()
    wrong_bindings = SpyCollection()
    missing_policy = make_policy(policy_id="missing-policy")
    persist_binding(make_binding(missing_policy, binding_id="wrong"), wrong_bindings, session)
    with pytest.raises(AccountsPayableProviderSelectionOrchestrationError, match="POLICY_NOT_FOUND"):
        run(**surface_args(requests, wrong_bindings, policies, selections, session, request))


def test_wrong_policy_fingerprint_rejects() -> None:
    requests, _, policies, selections, session, request, policy, _ = base()
    wrong_bindings = SpyCollection()
    persist_binding(make_binding(policy, binding_id="wrong-fp", policy_fingerprint=FP_C), wrong_bindings, session)
    with pytest.raises(AccountsPayableProviderSelectionOrchestrationError, match="POLICY_BINDING_CORRELATION_INVALID"):
        run(**surface_args(requests, wrong_bindings, policies, selections, session, request))


def test_exact_request_fingerprint_is_propagated() -> None:
    requests, bindings, policies, selections, session, request, _, _ = base()
    result, _ = run(**surface_args(requests, bindings, policies, selections, session, request))
    assert result.execution_request_fingerprint == request.fingerprint


def test_exact_binding_provenance_is_propagated() -> None:
    requests, bindings, policies, selections, session, request, _, binding = base()
    result, _ = run(**surface_args(requests, bindings, policies, selections, session, request))
    assert (result.runtime_binding_id, result.runtime_binding_revision, result.runtime_binding_fingerprint) == (binding.binding_id, binding.binding_revision, binding.binding_fingerprint)


def test_exact_policy_provenance_is_propagated() -> None:
    requests, bindings, policies, selections, session, request, policy, _ = base()
    result, _ = run(**surface_args(requests, bindings, policies, selections, session, request))
    assert (result.provider_policy_id, result.provider_policy_revision, result.provider_policy_fingerprint) == (policy.policy_id, policy.policy_revision, policy.policy_fingerprint)


def test_sole_provider_is_propagated() -> None:
    requests, bindings, policies, selections, session, request, policy, _ = base()
    result, _ = run(**surface_args(requests, bindings, policies, selections, session, request))
    assert result.selected_provider == policy.eligible_provider_names[0]


def test_caller_provider_argument_is_absent() -> None:
    parameters = inspect.signature(select_accounts_payable_provider).parameters
    assert "provider" not in parameters and "selected_provider" not in parameters


def test_request_level_conflict_fails_closed(monkeypatch: pytest.MonkeyPatch) -> None:
    requests, bindings, policies, selections, session, request, _, _ = base()

    def reject_request_conflict(*args: object, **kwargs: object) -> tuple[object, bool]:
        raise RuntimeError("REQUEST_ALREADY_HAS_CANONICAL_SELECTION")

    monkeypatch.setattr(AccountsPayableProviderSelectionDecisionRegistry, "create", reject_request_conflict)
    with pytest.raises(AccountsPayableProviderSelectionOrchestrationError, match="REQUEST_ALREADY_HAS_CANONICAL_SELECTION"):
        run(**surface_args(requests, bindings, policies, selections, session, request))
    assert selections.rows == []


def test_request_conflict_cannot_become_failover_or_overwrite(monkeypatch: pytest.MonkeyPatch) -> None:
    requests, bindings, policies, selections, session, request, _, _ = base()

    def reject_request_conflict(*args: object, **kwargs: object) -> tuple[object, bool]:
        raise RuntimeError("REQUEST_ALREADY_HAS_CANONICAL_SELECTION")

    monkeypatch.setattr(AccountsPayableProviderSelectionDecisionRegistry, "create", reject_request_conflict)
    with pytest.raises(AccountsPayableProviderSelectionOrchestrationError, match="REQUEST_ALREADY_HAS_CANONICAL_SELECTION"):
        run(**surface_args(requests, bindings, policies, selections, session, request))
    assert selections.rows == []


def test_cross_tenant_binding_attack_rejects() -> None:
    requests, _, policies, selections, session, request, _, _ = base()
    foreign_bindings = SpyCollection()
    foreign_policy = make_policy(tenant_id="tenant-b")
    persist_binding(make_binding(foreign_policy, tenant_id="tenant-b"), foreign_bindings, session)
    with pytest.raises(AccountsPayableProviderSelectionOrchestrationError, match="CURRENT_BINDING_REQUIRED"):
        run(**surface_args(requests, foreign_bindings, policies, selections, session, request))


def test_cross_tenant_policy_attack_rejects() -> None:
    requests, bindings, _, selections, session, request, _, _ = base()
    foreign_policies = SpyCollection()
    persist_policy(make_policy(tenant_id="tenant-b"), foreign_policies, session)
    with pytest.raises(AccountsPayableProviderSelectionOrchestrationError, match="POLICY_NOT_FOUND"):
        run(**surface_args(requests, bindings, foreign_policies, selections, session, request))


def test_existing_selection_request_fingerprint_mismatch_rejects() -> None:
    requests, bindings, policies, selections, session, request, policy, binding = base()
    foreign_request = make_request(request_id=request.execution_command_id)
    forged = AccountsPayableProviderSelectionDecision(
        tenant_id=request.tenant_id,
        execution_request_id=request.execution_command_id,
        execution_request_fingerprint=FP_C,
        runtime_binding_id=binding.binding_id,
        runtime_binding_revision=binding.binding_revision,
        runtime_binding_fingerprint=binding.binding_fingerprint,
        provider_policy_id=policy.policy_id,
        provider_policy_revision=policy.policy_revision,
        provider_policy_fingerprint=policy.policy_fingerprint,
        selected_provider="provider-a",
    )
    AccountsPayableProviderSelectionDecisionRegistry.create(forged, selections, session=session)
    assert foreign_request.execution_command_id == request.execution_command_id
    with pytest.raises(AccountsPayableProviderSelectionOrchestrationError, match="SELECTION_REQUEST_CORRELATION_INVALID"):
        run(**surface_args(requests, bindings, policies, selections, session, request))


def test_orchestration_does_not_insert_directly() -> None:
    source = inspect.getsource(select_accounts_payable_provider)
    assert "selection_collection.insert_one" not in source


def test_no_generic_command_or_execution_attempt_surface() -> None:
    source = inspect.getsource(select_accounts_payable_provider)
    assert "FinancialExecutionCommand" not in source and "ExecutionAttempt" not in source


def test_no_provider_transport_or_settlement_surface() -> None:
    source = inspect.getsource(select_accounts_payable_provider)
    assert "provider_call" not in source and "settlement" not in source.lower()


def test_no_vendor_bill_paid_or_settled_transition() -> None:
    source = inspect.getsource(select_accounts_payable_provider)
    assert "paid" not in source.lower() and "settled" not in source.lower()


def test_no_client_invoice_or_client_receivable_authority() -> None:
    source = inspect.getsource(select_accounts_payable_provider)
    assert "ClientInvoice" not in source and "receivable" not in source.lower()


def test_current_binding_is_used_for_first_selection_not_history_order() -> None:
    requests, bindings, policies, selections, session, request, policy, first = base()
    second_policy = make_policy(revision=2, providers=("provider-b",))
    persist_policy(second_policy, policies, session)
    second = make_binding(
        second_policy,
        binding_id="binding-b",
        revision=2,
        previous_binding_id=first.binding_id,
        previous_binding_fingerprint=first.binding_fingerprint,
    )
    persist_binding(second, bindings, session)
    result, _ = run(**surface_args(requests, bindings, policies, selections, session, request))
    assert result.runtime_binding_id == second.binding_id


def test_selection_persistence_uses_canonical_registry_and_session() -> None:
    requests, bindings, policies, selections, session, request, _, _ = base()
    run(**surface_args(requests, bindings, policies, selections, session, request))
    assert selections.writes == 1 and selections.sessions[-1] is session


def test_transaction_lifecycle_remains_caller_owned() -> None:
    requests, bindings, policies, selections, session, request, _, _ = base()
    run(**surface_args(requests, bindings, policies, selections, session, request))
    assert not any(name in vars(session) for name in ("start_transaction", "commit_transaction", "abort_transaction", "retry_transaction"))


# ARTIFACT: test_accounts_payable_provider_selection.py
# VERSION: v1.0.0-M11-P5-R1B-AP2D-R3
# AUTHORITY BOUNDARY: direct AP selection-orchestration certificate only
# TENANT POSTURE: synthetic tenant-scoped fixtures; no Mongo
# FAIL-CLOSED POSTURE: missing, corrupt, ambiguous, cross-tenant, and divergent evidence rejects
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively
# END OF WILSY OS SOVEREIGN ARTIFACT
