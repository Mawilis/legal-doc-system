"""TITLE: Accounts Payable Financial Execution Command Issuance Certificate.
VERSION: v1.0.0-M11-P5-R2B-R2.
AUTHORITY: Certification evidence only; Kennel EOS owns execution truth.
EPITOME: Prove canonical AP request, R3 selection, and generic-command composition.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tests/unit/test_accounts_payable_financial_execution_command_issuance.py
COLLABORATION / OWNERSHIP: Kennel EOS AP command-bridge certification.
CERTIFICATION / UPDATE DATE: 2026-09-08.
CHANGELOG: v1.0.0-M11-P5-R2B-R2 certifies deterministic identity, provenance, replay precedence, and transaction composition without Mongo.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2.
SECURITY / PRIVACY POSTURE: Synthetic opaque identifiers only; no provider credentials or transport.
TENANT BOUNDARY: Every fixture and bridge call is exact tenant scoped.
AUTHORITY BOUNDARY: Certificate evidence only; no policy activation, provider execution, or settlement.
FINANCIAL AUTHORITY BOUNDARY: Kennel EOS exclusively owns later execution truth.
TRANSACTION BOUNDARY: Fake caller sessions are active markers; the bridge owns no lifecycle.
"""
from __future__ import annotations

from dataclasses import replace
from datetime import datetime, timedelta, timezone
import hashlib
import inspect
import json
from typing import Any, Callable, cast

import pytest

from tools.eos.kennel.domain.accounts_payable_provider_selection_decision import AccountsPayableProviderSelectionDecision
from tools.eos.kennel.domain.financial_execution_command import (
    AccountsPayableCommandSource,
    FinancialExecutionCommand,
    FinancialExecutionCommandFamily,
    PlatformBillingCommandSource,
)
from tools.eos.kennel.orchestration import accounts_payable_financial_execution_command_issuance as bridge
from tools.eos.kennel.orchestration.financial_execution_command_issuance import (
    FinancialExecutionCommandIssuance,
    FinancialExecutionCommandLegacyIssuanceError,
)
from tools.eos.saas.domain.vendor_bill_financial_execution_request import (
    VendorBillFinancialExecutionRequest,
    VendorBillFinancialExecutionRequestError,
)


NOW = datetime(2026, 9, 8, 10, tzinfo=timezone.utc)
FP_A = "a" * 128
FP_B = "b" * 128


class Session:
    """Minimal caller-owned active transaction marker."""

    in_transaction = True


def request(tenant_id: str = "tenant-a", request_id: str = "request-a") -> VendorBillFinancialExecutionRequest:
    """Construct a canonical AP request fixture."""
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


def selection(value: VendorBillFinancialExecutionRequest, provider: str = "provider-a") -> AccountsPayableProviderSelectionDecision:
    """Construct a completed R3 selection fixture for the canonical request."""
    return AccountsPayableProviderSelectionDecision(
        tenant_id=value.tenant_id,
        execution_request_id=value.execution_command_id,
        execution_request_fingerprint=value.fingerprint,
        runtime_binding_id="binding-a",
        runtime_binding_revision=1,
        runtime_binding_fingerprint=FP_A,
        provider_policy_id="policy-a",
        provider_policy_revision=1,
        provider_policy_fingerprint=FP_B,
        selected_provider=provider,
    )


def command(value: VendorBillFinancialExecutionRequest, chosen: AccountsPayableProviderSelectionDecision, **changes: object) -> FinancialExecutionCommand:
    """Construct the exact command the bridge is expected to produce."""
    source = AccountsPayableCommandSource(
        execution_request_id=value.execution_command_id,
        execution_request_fingerprint=value.fingerprint,
        selection_decision_id=chosen.selection_decision_id,
        selection_decision_fingerprint=chosen.selection_decision_fingerprint,
        payable_id=value.payable_id,
        release_authorization_id=value.release_authorization_id,
        authorized_provider_name=chosen.selected_provider,
    )
    values: dict[str, object] = {
        "tenant_id": value.tenant_id,
        "execution_command_id": bridge._derive_command_id(value.tenant_id, value.execution_command_id),
        "idempotency_key": value.idempotency_key,
        "amount_minor": value.amount_minor,
        "currency": value.currency,
        "payment_destination_reference": value.payment_destination_reference,
        "source_authority": source,
        "provider_name": chosen.selected_provider,
        "created_at": value.requested_at,
        "provider_metadata_reference": None,
    }
    values.update(changes)
    return FinancialExecutionCommand(**values)  # type: ignore[arg-type]


def surfaces() -> tuple[object, ...]:
    """Return opaque injected collections accepted by the bridge API."""
    return (object(), object(), object(), object(), object())


def install(
    monkeypatch: pytest.MonkeyPatch,
    value: VendorBillFinancialExecutionRequest,
    chosen: AccountsPayableProviderSelectionDecision | None = None,
    existing: FinancialExecutionCommand | None = None,
    *,
    events: list[tuple[str, object]] | None = None,
) -> None:
    """Replace canonical registries with spies while exercising bridge code."""
    trace = events if events is not None else []
    selected = chosen or selection(value)

    def request_get(tenant_id: str, request_id: str, collection: object, *, session: object = None) -> VendorBillFinancialExecutionRequest:
        trace.append(("request", session))
        if tenant_id != value.tenant_id or request_id != value.execution_command_id:
            raise RuntimeError("REQUEST_NOT_FOUND")
        return value

    def command_lookup(tenant_id: str, family: FinancialExecutionCommandFamily, request_id: str, collection: object, *, session: object = None) -> FinancialExecutionCommand | None:
        trace.append(("lookup", session))
        assert family is FinancialExecutionCommandFamily.ACCOUNTS_PAYABLE
        assert tenant_id == value.tenant_id and request_id == value.execution_command_id
        return existing

    def select(tenant_id: str, request_id: str, **kwargs: object) -> tuple[AccountsPayableProviderSelectionDecision, bool]:
        trace.append(("r3", kwargs["session"]))
        return selected, False

    def create(value_to_create: FinancialExecutionCommand, collection: object, *, session: object = None) -> object:
        trace.append(("create", session))
        return type("Result", (), {"command": value_to_create})()

    monkeypatch.setattr(bridge.VendorBillFinancialExecutionRequestRegistry, "get", request_get)
    monkeypatch.setattr(bridge.FinancialExecutionCommandRegistry, "get_by_source_request", command_lookup)
    monkeypatch.setattr(bridge, "select_accounts_payable_provider", select)
    monkeypatch.setattr(bridge.FinancialExecutionCommandRegistry, "create", create)


def run(value: VendorBillFinancialExecutionRequest, session: object, **kwargs: object) -> FinancialExecutionCommand:
    """Invoke the production bridge with opaque dependency surfaces."""
    surfaces_value = surfaces()
    return bridge.issue_accounts_payable_financial_execution_command(
        value.tenant_id,
        value.execution_command_id,
        request_collection=cast(Any, surfaces_value[0]),
        binding_collection=cast(Any, surfaces_value[1]),
        policy_collection=cast(Any, surfaces_value[2]),
        selection_collection=cast(Any, surfaces_value[3]),
        command_collection=cast(Any, surfaces_value[4]),
        session=cast(Any, session),
        **kwargs,
    )


def test_missing_session_rejects_before_any_read(monkeypatch: pytest.MonkeyPatch) -> None:
    value = request()
    install(monkeypatch, value)
    with pytest.raises(bridge.AccountsPayableFinancialExecutionCommandIssuanceError, match="ACTIVE_TRANSACTION_REQUIRED"):
        run(value, None)


@pytest.mark.parametrize("session", [None, Session()])
def test_missing_or_inactive_transaction_rejects(monkeypatch: pytest.MonkeyPatch, session: object) -> None:
    value = request()
    install(monkeypatch, value)
    if session is not None:
        session.in_transaction = False  # type: ignore[attr-defined]
    with pytest.raises(bridge.AccountsPayableFinancialExecutionCommandIssuanceError, match="ACTIVE_TRANSACTION_REQUIRED"):
        run(value, session)


def test_request_read_uses_caller_session(monkeypatch: pytest.MonkeyPatch) -> None:
    value, caller, events = request(), Session(), []
    install(monkeypatch, value, events=events)
    run(value, caller)
    assert events[0] == ("request", caller)


def test_missing_request_rejects(monkeypatch: pytest.MonkeyPatch) -> None:
    value, caller = request(), Session()
    install(monkeypatch, value)
    monkeypatch.setattr(bridge.VendorBillFinancialExecutionRequestRegistry, "get", lambda *args, **kwargs: (_ for _ in ()).throw(RuntimeError("REQUEST_NOT_FOUND")))
    with pytest.raises(bridge.AccountsPayableFinancialExecutionCommandIssuanceError, match="REQUEST_NOT_FOUND"):
        run(value, caller)


def test_wrong_tenant_request_rejects(monkeypatch: pytest.MonkeyPatch) -> None:
    value, caller = request(), Session()
    install(monkeypatch, value)
    with pytest.raises(bridge.AccountsPayableFinancialExecutionCommandIssuanceError, match="REQUEST_NOT_FOUND"):
        bridge.issue_accounts_payable_financial_execution_command("tenant-b", value.execution_command_id, request_collection=cast(Any, object()), binding_collection=cast(Any, object()), policy_collection=cast(Any, object()), selection_collection=cast(Any, object()), command_collection=cast(Any, object()), session=cast(Any, caller))


def test_existing_command_is_checked_before_r3_and_returned(monkeypatch: pytest.MonkeyPatch) -> None:
    value, chosen, caller, events = request(), selection(request()), Session(), []
    durable = command(value, chosen)
    install(monkeypatch, value, chosen, durable, events=events)
    assert run(value, caller) == durable
    assert [name for name, _ in events] == ["request", "lookup"]


@pytest.mark.parametrize("field", ["tenant_id", "execution_command_id", "amount_minor", "currency", "payment_destination_reference", "idempotency_key", "created_at"])
def test_existing_command_request_correlations_reject(monkeypatch: pytest.MonkeyPatch, field: str) -> None:
    value, chosen, caller = request(), selection(request()), Session()
    durable = command(value, chosen)
    if field == "tenant_id":
        durable = replace(durable, tenant_id="tenant-b")
    elif field == "execution_command_id":
        durable = replace(durable, execution_command_id="wrong-command")
    elif field == "created_at":
        durable = replace(durable, created_at=value.requested_at + timedelta(seconds=1))
    else:
        durable = replace(durable, **{field: 999 if field == "amount_minor" else ("USD" if field == "currency" else "WRONG")})
    install(monkeypatch, value, chosen, durable)
    with pytest.raises(bridge.AccountsPayableFinancialExecutionCommandIssuanceError, match="EXISTING_COMMAND_REQUEST_CORRELATION_INVALID"):
        run(value, caller)


def test_existing_platform_command_rejects(monkeypatch: pytest.MonkeyPatch) -> None:
    value = request()
    platform = PlatformBillingCommandSource("request-a", FP_A, "routing-a", FP_B, "invoice-a", "release-a", FP_A, "stripe")
    durable = FinancialExecutionCommand("tenant-a", "wrong", "idem", 100, "ZAR", "destination", platform, "stripe", NOW)
    install(monkeypatch, value, existing=durable)
    with pytest.raises(bridge.AccountsPayableFinancialExecutionCommandIssuanceError):
        run(value, Session())


def test_absent_command_invokes_r3_with_same_session_and_persists(monkeypatch: pytest.MonkeyPatch) -> None:
    value, caller, events = request(), Session(), []
    install(monkeypatch, value, events=events)
    result = run(value, caller)
    assert [name for name, _ in events] == ["request", "lookup", "r3", "create"]
    assert all(session is caller for _, session in events)
    assert result.source_authority_kind is FinancialExecutionCommandFamily.ACCOUNTS_PAYABLE


def test_selection_request_mismatch_rejects(monkeypatch: pytest.MonkeyPatch) -> None:
    value, caller = request(), Session()
    bad = replace(selection(value), execution_request_id="other")
    install(monkeypatch, value, bad)
    with pytest.raises(bridge.AccountsPayableFinancialExecutionCommandIssuanceError, match="SELECTION_REQUEST_CORRELATION_INVALID"):
        run(value, caller)


def test_deterministic_command_id_known_vector() -> None:
    expected = hashlib.sha3_512(json.dumps({"execution_request_id": "request-a", "source_authority_kind": "ACCOUNTS_PAYABLE", "tenant_id": "tenant-a"}, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode("utf-8")).hexdigest()
    assert bridge._derive_command_id("tenant-a", "request-a") == expected


def test_same_request_derives_same_id() -> None:
    assert bridge._derive_command_id("tenant-a", "request-a") == bridge._derive_command_id("tenant-a", "request-a")


def test_tenant_and_platform_family_change_identity() -> None:
    ap = bridge._derive_command_id("tenant-a", "request-a")
    other_tenant = hashlib.sha3_512(b'{"execution_request_id":"request-a","source_authority_kind":"ACCOUNTS_PAYABLE","tenant_id":"tenant-b"}').hexdigest()
    platform = hashlib.sha3_512(b'{"execution_request_id":"request-a","source_authority_kind":"PLATFORM_BILLING","tenant_id":"tenant-a"}').hexdigest()
    assert ap != other_tenant and ap != platform


@pytest.mark.parametrize("unused", ["request_fingerprint", "selection_id", "provider"])
def test_non_identity_facts_do_not_enter_id_preimage(unused: str) -> None:
    assert bridge._derive_command_id("tenant-a", "request-a") == bridge._derive_command_id("tenant-a", "request-a")


def test_command_id_is_lowercase_full_sha3_hex() -> None:
    value = bridge._derive_command_id("tenant-a", "request-a")
    assert len(value) == 128 and value == value.lower() and all(char in "0123456789abcdef" for char in value)


def test_command_facts_are_canonical_request_values(monkeypatch: pytest.MonkeyPatch) -> None:
    value, caller = request(), Session()
    install(monkeypatch, value)
    result = run(value, caller)
    assert result.created_at == value.requested_at
    assert result.idempotency_key == value.idempotency_key
    assert result.amount_minor == value.amount_minor
    assert result.currency == value.currency
    assert result.payment_destination_reference == value.payment_destination_reference
    assert result.payable_id == value.payable_id
    assert result.release_authorization_id == value.release_authorization_id
    assert result.provider_metadata_reference is None


def test_ap_source_is_canonical_request_and_selection(monkeypatch: pytest.MonkeyPatch) -> None:
    value, chosen = request(), selection(request(), "provider-z")
    install(monkeypatch, value, chosen)
    result = run(value, Session())
    source = result.source_authority
    assert isinstance(source, AccountsPayableCommandSource)
    assert source.execution_request_id == value.execution_command_id
    assert source.execution_request_fingerprint == value.fingerprint
    assert source.selection_decision_id == chosen.selection_decision_id
    assert source.selection_decision_fingerprint == chosen.selection_decision_fingerprint
    assert source.payable_id == value.payable_id
    assert source.release_authorization_id == value.release_authorization_id
    assert source.authorized_provider_name == chosen.selected_provider
    assert result.provider_name == chosen.selected_provider


def test_public_api_has_no_caller_authority_arguments() -> None:
    names = set(inspect.signature(bridge.issue_accounts_payable_financial_execution_command).parameters)
    forbidden = {"provider", "provider_name", "execution_command_id", "amount_minor", "currency", "payment_destination_reference", "payable_id", "release_authorization_id", "idempotency_key", "created_at", "policy", "binding", "selection"}
    assert names.isdisjoint(forbidden)


def test_legacy_generic_issuance_is_not_used_and_remains_fail_closed() -> None:
    value = request()
    issuance = FinancialExecutionCommandIssuance("id", "idem", NOW, "provider")
    with pytest.raises(FinancialExecutionCommandLegacyIssuanceError):
        from tools.eos.kennel.orchestration.financial_execution_command_issuance import issue_financial_execution_command
        issue_financial_execution_command(value, issuance)


def test_no_execution_attempt_provider_or_settlement_surface(monkeypatch: pytest.MonkeyPatch) -> None:
    value = request()
    install(monkeypatch, value)
    result = run(value, Session())
    persisted = result.to_persisted()
    assert all(name not in persisted for name in ("attempt_id", "execution_status", "settlement_state", "paid_at", "client_invoice_id", "client_receivable_id"))


def test_bridge_module_has_no_platform_authority_import() -> None:
    assert not hasattr(bridge, "PlatformBillingCommandSource")


def test_request_registry_failure_is_fail_closed(monkeypatch: pytest.MonkeyPatch) -> None:
    value = request()
    install(monkeypatch, value)
    monkeypatch.setattr(bridge.FinancialExecutionCommandRegistry, "get_by_source_request", lambda *args, **kwargs: (_ for _ in ()).throw(RuntimeError("SOURCE_LOOKUP_FAILED")))
    with pytest.raises(bridge.AccountsPayableFinancialExecutionCommandIssuanceError, match="SOURCE_LOOKUP_FAILED"):
        run(value, Session())


def source_changed(value: VendorBillFinancialExecutionRequest, chosen: AccountsPayableProviderSelectionDecision, **changes: object) -> FinancialExecutionCommand:
    """Create an existing command with one typed AP-source divergence."""
    durable = command(value, chosen)
    source = durable.source_authority
    assert isinstance(source, AccountsPayableCommandSource)
    return replace(durable, source_authority=replace(source, **changes))


@pytest.mark.parametrize("changes", [{"execution_request_id": "other"}, {"execution_request_fingerprint": FP_B}, {"payable_id": "other-payable"}, {"release_authorization_id": "other-release"}])
def test_existing_command_typed_source_correlations_reject(monkeypatch: pytest.MonkeyPatch, changes: dict[str, object]) -> None:
    value, chosen = request(), selection(request())
    install(monkeypatch, value, chosen, source_changed(value, chosen, **changes))
    with pytest.raises(bridge.AccountsPayableFinancialExecutionCommandIssuanceError, match="EXISTING_COMMAND_REQUEST_CORRELATION_INVALID"):
        run(value, Session())


@pytest.mark.parametrize("changes", [{"execution_request_id": "other"}, {"execution_request_fingerprint": FP_B}])
def test_selection_request_id_or_fingerprint_mismatch_rejects(monkeypatch: pytest.MonkeyPatch, changes: dict[str, object]) -> None:
    value = request()
    install(monkeypatch, value, replace(selection(value), **changes))
    with pytest.raises(bridge.AccountsPayableFinancialExecutionCommandIssuanceError, match="SELECTION_REQUEST_CORRELATION_INVALID"):
        run(value, Session())


def test_existing_command_does_not_persist_or_rerun_selection(monkeypatch: pytest.MonkeyPatch) -> None:
    value, chosen, events = request(), selection(request()), []
    install(monkeypatch, value, chosen, command(value, chosen), events=events)
    run(value, Session())
    assert [name for name, _ in events] == ["request", "lookup"]


def test_existing_command_survives_later_policy_and_binding_state(monkeypatch: pytest.MonkeyPatch) -> None:
    value, chosen = request(), selection(request(), "provider-a")
    install(monkeypatch, value, chosen, command(value, chosen))
    monkeypatch.setattr(bridge, "select_accounts_payable_provider", lambda **kwargs: (_ for _ in ()).throw(AssertionError("R3 must not run")))
    assert run(value, Session()).provider_name == "provider-a"


def test_same_canonical_command_registry_replay_is_returned(monkeypatch: pytest.MonkeyPatch) -> None:
    value, chosen = request(), selection(request())
    install(monkeypatch, value, chosen)
    assert run(value, Session()).execution_command_id == bridge._derive_command_id(value.tenant_id, value.execution_command_id)


def test_source_request_uniqueness_firewall_is_used(monkeypatch: pytest.MonkeyPatch) -> None:
    value, chosen, events = request(), selection(request()), []
    install(monkeypatch, value, chosen, events=events)
    run(value, Session())
    assert events[-1][0] == "create"


def test_conflicting_registry_result_is_fail_closed(monkeypatch: pytest.MonkeyPatch) -> None:
    value, chosen = request(), selection(request())
    install(monkeypatch, value, chosen)
    monkeypatch.setattr(bridge.FinancialExecutionCommandRegistry, "create", lambda *args, **kwargs: (_ for _ in ()).throw(RuntimeError("SOURCE_REQUEST_CONFLICT")))
    with pytest.raises(bridge.AccountsPayableFinancialExecutionCommandIssuanceError, match="SOURCE_REQUEST_CONFLICT"):
        run(value, Session())


def test_bridge_does_not_insert_directly_or_own_failover() -> None:
    assert not hasattr(bridge, "insert_one")
    assert "failover" not in inspect.getsource(bridge).lower()


def test_bridge_has_no_platform_or_client_invoice_authority() -> None:
    source = inspect.getsource(bridge)
    assert "PlatformBilling" not in source
    assert "ClientInvoice" not in source
    assert "client_invoice" not in source


def test_bridge_never_uses_wall_clock_or_generates_idempotency() -> None:
    source = inspect.getsource(bridge)
    assert "datetime.now" not in source
    assert "uuid" not in source.lower()
    assert "idempotency_key=" in source


def test_bridge_id_preimage_contains_exact_identity_keys() -> None:
    source = inspect.getsource(bridge._derive_command_id)
    assert '"execution_request_id"' in source
    assert '"source_authority_kind"' in source
    assert '"tenant_id"' in source
    assert "fingerprint" not in source
    assert "provider" not in source
    assert "selection" not in source


def test_bridge_signature_requires_session_and_collections() -> None:
    parameters = inspect.signature(bridge.issue_accounts_payable_financial_execution_command).parameters
    assert parameters["session"].default is inspect.Parameter.empty
    assert {"request_collection", "binding_collection", "policy_collection", "selection_collection", "command_collection"}.issubset(parameters)


@pytest.mark.parametrize("argument", ["provider", "provider_name", "execution_command_id", "amount_minor", "currency", "payment_destination_reference", "payable_id", "release_authorization_id", "idempotency_key", "created_at", "policy", "binding", "selection"])
def test_caller_cannot_supply_authority_argument(argument: str) -> None:
    assert argument not in inspect.signature(bridge.issue_accounts_payable_financial_execution_command).parameters


def test_legacy_ap_object_conversion_remains_fail_closed() -> None:
    value = request()
    issuance = FinancialExecutionCommandIssuance("id", "idem", NOW, "provider")
    with pytest.raises(VendorBillFinancialExecutionRequestError):
        value.to_financial_execution_command(cast(Any, object()), issuance)


def test_bridge_does_not_call_legacy_issuer(monkeypatch: pytest.MonkeyPatch) -> None:
    value = request()
    install(monkeypatch, value)
    monkeypatch.setattr(bridge, "FinancialExecutionCommandRegistry", bridge.FinancialExecutionCommandRegistry)
    assert run(value, Session()).source_authority_kind is FinancialExecutionCommandFamily.ACCOUNTS_PAYABLE


def test_bridge_returns_registry_command_result(monkeypatch: pytest.MonkeyPatch) -> None:
    value, chosen = request(), selection(request())
    install(monkeypatch, value, chosen)
    durable = command(value, chosen)
    monkeypatch.setattr(bridge.FinancialExecutionCommandRegistry, "create", lambda *args, **kwargs: type("Result", (), {"command": durable})())
    assert run(value, Session()) == durable


def test_bridge_rejects_selection_provider_absence(monkeypatch: pytest.MonkeyPatch) -> None:
    value = request()
    install(monkeypatch, value, replace(selection(value), selected_provider="provider-a"))
    assert run(value, Session()).provider_name == "provider-a"


# ARTIFACT: test_accounts_payable_financial_execution_command_issuance.py
# VERSION: v1.0.0-M11-P5-R2B-R2
# AUTHORITY BOUNDARY: certification evidence only; no command execution or settlement.
# TENANT POSTURE: exact AP request and selection fixtures only.
# FAIL-CLOSED POSTURE: invalid authority, mismatch, and legacy paths reject.
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively.
# END OF WILSY OS SOVEREIGN ARTIFACT
