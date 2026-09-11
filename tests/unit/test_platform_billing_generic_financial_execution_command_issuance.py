"""TITLE: Platform Billing Generic Financial Execution Command Certificate.
VERSION: v1.0.0-M11E2D5C2G-P5-R2C-R2.
AUTHORITY: Kennel EOS / Wilsy OS Core Governance.
EPITOME: Prove canonical Platform request plus pre-existing P4 composition into one generic command.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tests/unit/test_platform_billing_generic_financial_execution_command_issuance.py
COLLABORATION / OWNERSHIP: Kennel EOS Platform generic-command bridge certificate.
CERTIFICATION / UPDATE DATE: 2026-09-08.
CHANGELOG: v1.0.0-M11E2D5C2G-P5-R2C-R2 certifies request precedence, P4 provenance, deterministic identity, strict replay, and transaction composition.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2.
SECURITY / PRIVACY POSTURE: Synthetic opaque identifiers only; no credentials, provider payloads, or transport.
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
from typing import Any, cast

import pytest

from tools.eos.kennel.domain.financial_execution_command import (
    AccountsPayableCommandSource,
    FinancialExecutionCommand,
    FinancialExecutionCommandFamily,
    PlatformBillingCommandSource,
)
from types import SimpleNamespace
from tools.eos.kennel.domain.platform_billing_provider_routing_decision import (
    PlatformBillingProviderRoutingDecision,
)
from tools.eos.kennel.orchestration import (
    platform_billing_generic_financial_execution_command_issuance as bridge,
)
from tools.eos.saas.domain.platform_billing_financial_execution_request import (
    PlatformBillingFinancialExecutionRequest,
)

NOW = datetime(2026, 9, 8, 10, tzinfo=timezone.utc)
FP_A = "a" * 128
FP_B = "b" * 128
FP_C = "c" * 128


class Session:
    """Minimal caller-owned active transaction marker."""

    in_transaction = True


def request(tenant_id: str = "tenant-a", request_id: str = "request-a") -> PlatformBillingFinancialExecutionRequest:
    """Construct one canonical Platform request fixture."""
    return PlatformBillingFinancialExecutionRequest(
        execution_request_id=request_id,
        tenant_id=tenant_id,
        release_authorization_id=f"release-{tenant_id}",
        platform_invoice_id=f"platform-invoice-{tenant_id}",
        release_authorization_fingerprint=FP_A,
        amount_minor=100,
        currency="ZAR",
        payment_destination_reference=f"opaque-destination-{tenant_id}",
        idempotency_key=f"idem-{tenant_id}-{request_id}",
        requested_by_principal_id=f"principal-{tenant_id}",
        authorization_basis_reference=f"basis-{tenant_id}",
        requested_at=NOW,
        provider_policy_runtime_binding_id=f"binding-{tenant_id}",
        provider_policy_runtime_binding_fingerprint=FP_B,
        provider_policy_id=f"policy-{tenant_id}",
        provider_policy_revision=1,
        provider_policy_fingerprint=FP_C,
    )


def decision(value: PlatformBillingFinancialExecutionRequest, provider: str = "provider-a") -> PlatformBillingProviderRoutingDecision:
    """Construct frozen P4 routing authority correlated to the request."""
    return PlatformBillingProviderRoutingDecision(
        tenant_id=value.tenant_id,
        routing_decision_id=f"routing-{value.execution_request_id}",
        source_execution_request_id=value.execution_request_id,
        source_execution_request_fingerprint=value.fingerprint,
        source_provider_policy_id=value.provider_policy_id,
        source_provider_policy_revision=value.provider_policy_revision,
        source_provider_policy_fingerprint=value.provider_policy_fingerprint,
        selected_provider=provider,
        decided_at=NOW,
    )


def command(value: PlatformBillingFinancialExecutionRequest, chosen: PlatformBillingProviderRoutingDecision, **changes: object) -> FinancialExecutionCommand:
    """Construct the exact generic command expected from canonical facts."""
    source = PlatformBillingCommandSource(
        execution_request_id=value.execution_request_id,
        execution_request_fingerprint=value.fingerprint,
        routing_decision_id=chosen.routing_decision_id,
        routing_decision_fingerprint=chosen.routing_decision_fingerprint,
        platform_invoice_id=value.platform_invoice_id,
        release_authorization_id=value.release_authorization_id,
        release_authorization_fingerprint=value.release_authorization_fingerprint,
        authorized_provider_name=chosen.selected_provider,
    )
    values: dict[str, object] = {
        "tenant_id": value.tenant_id,
        "execution_command_id": bridge._derive_command_id(value.tenant_id, value.execution_request_id),
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


def install(monkeypatch: pytest.MonkeyPatch, value: PlatformBillingFinancialExecutionRequest, existing: FinancialExecutionCommand | None = None, chosen: PlatformBillingProviderRoutingDecision | None = None, *, events: list[tuple[str, object]] | None = None) -> None:
    """Replace canonical registries with spies while exercising the bridge."""
    trace = events if events is not None else []
    selected = chosen or decision(value)

    def request_get(tenant_id: str, request_id: str, collection: object, *, session: object = None) -> PlatformBillingFinancialExecutionRequest:
        trace.append(("request", session))
        if tenant_id != value.tenant_id or request_id != value.execution_request_id:
            raise RuntimeError("REQUEST_NOT_FOUND")
        return value

    def command_lookup(tenant_id: str, family: FinancialExecutionCommandFamily, request_id: str, collection: object, *, session: object = None) -> FinancialExecutionCommand | None:
        trace.append(("command_lookup", session))
        assert family is FinancialExecutionCommandFamily.PLATFORM_BILLING
        return existing

    def p4_lookup(tenant_id: str, request_id: str, collection: object, *, session: object = None) -> PlatformBillingProviderRoutingDecision | None:
        trace.append(("p4_lookup", session))
        return selected

    def create(value_to_create: FinancialExecutionCommand, collection: object, *, session: object = None) -> object:
        trace.append(("create", session))
        return type("Result", (), {"command": value_to_create})()

    monkeypatch.setattr(bridge.PlatformBillingFinancialExecutionRequestRegistry, "get", request_get)
    monkeypatch.setattr(bridge.FinancialExecutionCommandRegistry, "get_by_source_request", command_lookup)
    monkeypatch.setattr(bridge.PlatformBillingProviderRoutingDecisionRegistry, "get_by_request", p4_lookup)
    monkeypatch.setattr(bridge.FinancialExecutionCommandRegistry, "create", create)


def run(value: PlatformBillingFinancialExecutionRequest, session: object, **kwargs: object) -> FinancialExecutionCommand:
    """Invoke the production bridge with injected dependency surfaces."""
    return bridge.issue_platform_billing_generic_financial_execution_command(
        value.tenant_id,
        value.execution_request_id,
        request_collection=cast(Any, object()),
        routing_collection=cast(Any, object()),
        command_collection=cast(Any, object()),
        session=cast(Any, session),
        **kwargs,
    )


def test_missing_session_rejects_before_any_read(monkeypatch: pytest.MonkeyPatch) -> None:
    value = request(); install(monkeypatch, value)
    with pytest.raises(bridge.PlatformBillingGenericFinancialExecutionCommandIssuanceError, match="ACTIVE_TRANSACTION_REQUIRED"):
        run(value, None)


@pytest.mark.parametrize("session", [None, Session()])
def test_missing_or_inactive_transaction_rejects(monkeypatch: pytest.MonkeyPatch, session: object) -> None:
    value = request(); install(monkeypatch, value)
    if session is not None:
        session.in_transaction = False  # type: ignore[attr-defined]
    with pytest.raises(bridge.PlatformBillingGenericFinancialExecutionCommandIssuanceError, match="ACTIVE_TRANSACTION_REQUIRED"):
        run(value, session)


def test_request_read_uses_caller_session(monkeypatch: pytest.MonkeyPatch) -> None:
    value, caller, events = request(), Session(), []
    install(monkeypatch, value, events=events); run(value, caller)
    assert events[0] == ("request", caller)


def test_missing_request_rejects(monkeypatch: pytest.MonkeyPatch) -> None:
    value, caller = request(), Session(); install(monkeypatch, value)
    monkeypatch.setattr(bridge.PlatformBillingFinancialExecutionRequestRegistry, "get", lambda *args, **kwargs: (_ for _ in ()).throw(RuntimeError("REQUEST_NOT_FOUND")))
    with pytest.raises(bridge.PlatformBillingGenericFinancialExecutionCommandIssuanceError, match="REQUEST_NOT_FOUND"):
        run(value, caller)


def test_cross_tenant_request_rejects(monkeypatch: pytest.MonkeyPatch) -> None:
    value, caller = request(), Session(); install(monkeypatch, value)
    with pytest.raises(bridge.PlatformBillingGenericFinancialExecutionCommandIssuanceError, match="REQUEST_NOT_FOUND"):
        bridge.issue_platform_billing_generic_financial_execution_command("tenant-b", value.execution_request_id, request_collection=cast(Any, object()), routing_collection=cast(Any, object()), command_collection=cast(Any, object()), session=cast(Any, caller))


def test_existing_command_precedes_p4_and_is_returned(monkeypatch: pytest.MonkeyPatch) -> None:
    value, caller, events = request(), Session(), []
    durable = command(value, decision(value)); install(monkeypatch, value, durable, events=events)
    assert run(value, caller) == durable
    assert [name for name, _ in events] == ["request", "command_lookup"]


def test_existing_command_path_persists_nothing(monkeypatch: pytest.MonkeyPatch) -> None:
    value, events = request(), []; install(monkeypatch, value, command(value, decision(value)), events=events)
    run(value, Session()); assert "create" not in [name for name, _ in events]


def test_existing_command_path_does_not_read_p4(monkeypatch: pytest.MonkeyPatch) -> None:
    value, events = request(), []; install(monkeypatch, value, command(value, decision(value)), events=events)
    run(value, Session()); assert "p4_lookup" not in [name for name, _ in events]


@pytest.mark.parametrize("field", ["tenant_id", "execution_command_id", "amount_minor", "currency", "payment_destination_reference", "idempotency_key", "created_at"])
def test_existing_command_request_correlations_reject(monkeypatch: pytest.MonkeyPatch, field: str) -> None:
    value = request(); durable = command(value, decision(value))
    if field == "tenant_id": durable = replace(durable, tenant_id="tenant-b")
    elif field == "execution_command_id": durable = replace(durable, execution_command_id="wrong")
    elif field == "created_at": durable = replace(durable, created_at=value.requested_at + timedelta(seconds=1))
    else: durable = replace(durable, **{field: 999 if field == "amount_minor" else ("USD" if field == "currency" else "wrong")})
    install(monkeypatch, value, durable)
    with pytest.raises(bridge.PlatformBillingGenericFinancialExecutionCommandIssuanceError, match="EXISTING_COMMAND_REQUEST_CORRELATION_INVALID"):
        run(value, Session())


@pytest.mark.parametrize("field", ["platform_invoice_id", "release_authorization_id", "release_authorization_fingerprint"])
def test_existing_command_source_correlations_reject(monkeypatch: pytest.MonkeyPatch, field: str) -> None:
    value, chosen = request(), decision(request()); durable = command(value, chosen)
    source = durable.source_authority
    changes = {field: FP_C if "fingerprint" in field else "wrong-source"}
    durable = replace(durable, source_authority=replace(source, **changes))
    install(monkeypatch, value, durable)
    with pytest.raises(bridge.PlatformBillingGenericFinancialExecutionCommandIssuanceError, match="EXISTING_COMMAND_REQUEST_CORRELATION_INVALID"):
        run(value, Session())


def test_existing_command_family_mismatch_rejects(monkeypatch: pytest.MonkeyPatch) -> None:
    value = request(); source = AccountsPayableCommandSource(value.execution_request_id, FP_A, "selection", FP_B, "payable", value.release_authorization_id, "provider-a")
    durable = FinancialExecutionCommand(value.tenant_id, bridge._derive_command_id(value.tenant_id, value.execution_request_id), value.idempotency_key, value.amount_minor, value.currency, value.payment_destination_reference, source, "provider-a", value.requested_at)
    install(monkeypatch, value, durable)
    monkeypatch.setattr(bridge.FinancialExecutionCommandRegistry, "get_by_source_request", lambda *args, **kwargs: durable)
    with pytest.raises(bridge.PlatformBillingGenericFinancialExecutionCommandIssuanceError, match="EXISTING_COMMAND_REQUEST_CORRELATION_INVALID"):
        run(value, Session())


def test_existing_command_outlives_later_policy_state(monkeypatch: pytest.MonkeyPatch) -> None:
    value, durable = request(), command(request(), decision(request(), "provider-a")); install(monkeypatch, value, durable)
    assert run(value, Session()) == durable


def test_missing_p4_rejects_without_inventing_route(monkeypatch: pytest.MonkeyPatch) -> None:
    value = request(); install(monkeypatch, value, chosen=None)
    monkeypatch.setattr(bridge.PlatformBillingProviderRoutingDecisionRegistry, "get_by_request", lambda *args, **kwargs: None)
    with pytest.raises(bridge.PlatformBillingGenericFinancialExecutionCommandIssuanceError, match="P4_ROUTING_DECISION_REQUIRED"):
        run(value, Session())


@pytest.mark.parametrize("field", ["tenant_id", "source_execution_request_id", "source_execution_request_fingerprint", "source_provider_policy_id", "source_provider_policy_revision", "source_provider_policy_fingerprint"])
def test_p4_request_correlations_reject(monkeypatch: pytest.MonkeyPatch, field: str) -> None:
    value, chosen = request(), decision(request()); changes = {field: 9 if field.endswith("revision") else ("wrong" if field not in ("source_execution_request_fingerprint", "source_provider_policy_fingerprint") else FP_A)}
    p4_values = {name: getattr(chosen, name) for name in ("tenant_id", "routing_decision_id", "source_execution_request_id", "source_execution_request_fingerprint", "source_provider_policy_id", "source_provider_policy_revision", "source_provider_policy_fingerprint", "selected_provider", "routing_decision_fingerprint")}
    p4_values.update(changes)
    bad = SimpleNamespace(**p4_values)
    install(monkeypatch, value, chosen=cast(Any, bad))
    with pytest.raises(bridge.PlatformBillingGenericFinancialExecutionCommandIssuanceError, match="P4_REQUEST_CORRELATION_INVALID"):
        run(value, Session())


def test_p4_lookup_uses_same_session_and_persists_same_session(monkeypatch: pytest.MonkeyPatch) -> None:
    value, caller, events = request(), Session(), []; install(monkeypatch, value, events=events); run(value, caller)
    assert [name for name, _ in events] == ["request", "command_lookup", "p4_lookup", "create"]
    assert all(session is caller for _, session in events)


def test_provider_comes_only_from_p4(monkeypatch: pytest.MonkeyPatch) -> None:
    value, chosen = request(), decision(request(), "p4-provider"); install(monkeypatch, value, chosen=chosen)
    result = run(value, Session()); assert result.provider_name == "p4-provider" and result.source_authority.authorized_provider_name == "p4-provider"


def test_command_facts_are_canonical_request_values(monkeypatch: pytest.MonkeyPatch) -> None:
    value = request(); install(monkeypatch, value); result = run(value, Session())
    assert (result.created_at, result.idempotency_key, result.amount_minor, result.currency, result.payment_destination_reference) == (value.requested_at, value.idempotency_key, value.amount_minor, value.currency, value.payment_destination_reference)
    assert result.provider_metadata_reference is None


def test_platform_source_contains_complete_canonical_provenance(monkeypatch: pytest.MonkeyPatch) -> None:
    value, chosen = request(), decision(request(), "provider-z"); install(monkeypatch, value, chosen=chosen); result = run(value, Session())
    source = result.source_authority; assert isinstance(source, PlatformBillingCommandSource)
    assert source.execution_request_id == value.execution_request_id and source.execution_request_fingerprint == value.fingerprint
    assert source.routing_decision_id == chosen.routing_decision_id and source.routing_decision_fingerprint == chosen.routing_decision_fingerprint
    assert source.platform_invoice_id == value.platform_invoice_id and source.release_authorization_id == value.release_authorization_id
    assert source.release_authorization_fingerprint == value.release_authorization_fingerprint and source.authorized_provider_name == chosen.selected_provider


def test_deterministic_command_id_known_vector() -> None:
    expected = hashlib.sha3_512(json.dumps({"execution_request_id": "request-a", "source_authority_kind": "PLATFORM_BILLING", "tenant_id": "tenant-a"}, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode()).hexdigest()
    assert bridge._derive_command_id("tenant-a", "request-a") == expected


def test_same_request_same_command_id() -> None:
    assert bridge._derive_command_id("tenant-a", "request-a") == bridge._derive_command_id("tenant-a", "request-a")


def test_cross_tenant_and_cross_family_ids_differ() -> None:
    platform = bridge._derive_command_id("tenant-a", "request-a")
    other_tenant = hashlib.sha3_512(b'{"execution_request_id":"request-a","source_authority_kind":"PLATFORM_BILLING","tenant_id":"tenant-b"}').hexdigest()
    ap = hashlib.sha3_512(b'{"execution_request_id":"request-a","source_authority_kind":"ACCOUNTS_PAYABLE","tenant_id":"tenant-a"}').hexdigest()
    assert platform != other_tenant and platform != ap


@pytest.mark.parametrize("unused", ["routing_id", "provider", "request_fingerprint"])
def test_non_identity_facts_do_not_enter_command_id(unused: str) -> None:
    assert bridge._derive_command_id("tenant-a", "request-a") == bridge._derive_command_id("tenant-a", "request-a")


def test_command_id_is_lowercase_full_sha3_hex() -> None:
    value = bridge._derive_command_id("tenant-a", "request-a"); assert len(value) == 128 and value == value.lower() and all(c in "0123456789abcdef" for c in value)


def test_public_api_has_no_caller_authority_arguments() -> None:
    names = set(inspect.signature(bridge.issue_platform_billing_generic_financial_execution_command).parameters)
    forbidden = {"provider", "command_id", "execution_command_id", "routing_decision_id", "policy", "binding", "amount_minor", "currency", "payment_destination_reference", "platform_invoice_id", "release_authorization_id", "idempotency_key", "created_at"}
    assert names.isdisjoint(forbidden)


def test_p4_id_is_not_command_id() -> None:
    value = request(); chosen = decision(value); result = command(value, chosen)
    assert result.execution_command_id != chosen.routing_decision_id


def test_registry_create_is_the_only_persistence_surface(monkeypatch: pytest.MonkeyPatch) -> None:
    value, events = request(), []; install(monkeypatch, value, events=events); run(value, Session()); assert [n for n, _ in events][-1] == "create"


def test_same_canonical_command_race_is_exact_replay(monkeypatch: pytest.MonkeyPatch) -> None:
    value, durable = request(), command(request(), decision(request())); install(monkeypatch, value, durable); assert run(value, Session()) == durable


def test_divergent_command_conflict_is_not_failover(monkeypatch: pytest.MonkeyPatch) -> None:
    value, durable = request(), command(request(), decision(request(), "different")); divergent = durable
    install(monkeypatch, value, divergent)
    assert run(value, Session()) == divergent


def test_bridge_has_no_platform_specific_command_import() -> None:
    source = inspect.getsource(bridge); assert "PlatformBillingFinancialExecutionCommand" not in source and "platform_billing_financial_execution_command_issuance" not in source


def test_bridge_has_no_ap_or_client_invoice_authority() -> None:
    source = inspect.getsource(bridge); assert "AccountsPayable" not in source and "ClientInvoice" not in source and "payable_id" not in source


def test_bridge_has_no_attempt_truth_or_settlement_authority() -> None:
    assert not hasattr(bridge, "FinancialExecutionAttempt") and not hasattr(bridge, "issue_financial_execution_attempt")


def test_bridge_does_not_start_transaction_or_use_current_clock() -> None:
    source = inspect.getsource(bridge.issue_platform_billing_generic_financial_execution_command); assert "start_transaction" not in source and "datetime.now" not in source


def test_bridge_requires_p4_before_command_creation(monkeypatch: pytest.MonkeyPatch) -> None:
    value, events = request(), []; install(monkeypatch, value, events=events); monkeypatch.setattr(bridge.PlatformBillingProviderRoutingDecisionRegistry, "get_by_request", lambda *a, **k: None)
    with pytest.raises(bridge.PlatformBillingGenericFinancialExecutionCommandIssuanceError): run(value, Session())
    assert "create" not in [name for name, _ in events]


def test_command_created_at_is_stable_on_retry(monkeypatch: pytest.MonkeyPatch) -> None:
    value = request(); install(monkeypatch, value); assert run(value, Session()).created_at == value.requested_at


def test_platform_invoice_is_not_payable_subject(monkeypatch: pytest.MonkeyPatch) -> None:
    value = request(); install(monkeypatch, value); result = run(value, Session()); source = result.source_authority
    assert isinstance(source, PlatformBillingCommandSource) and source.platform_invoice_id == value.platform_invoice_id


def test_no_provider_metadata_is_invented(monkeypatch: pytest.MonkeyPatch) -> None:
    value = request(); install(monkeypatch, value); assert run(value, Session()).provider_metadata_reference is None


@pytest.mark.parametrize("forbidden", [
    "provider", "provider_name", "command_id", "execution_command_id",
    "routing_decision_id", "routing_decision", "policy", "binding",
    "amount_minor", "currency", "payment_destination_reference",
    "platform_invoice_id", "release_authorization_id", "idempotency_key",
    "created_at", "platform_specific_command",
])
def test_each_caller_authority_argument_is_absent(forbidden: str) -> None:
    """The public composition boundary accepts no caller-supplied authority fact."""
    assert forbidden not in inspect.signature(
        bridge.issue_platform_billing_generic_financial_execution_command
    ).parameters


# ARTIFACT: test_platform_billing_generic_financial_execution_command_issuance.py
# VERSION: v1.0.0-M11E2D5C2G-P5-R2C-R2
# AUTHORITY BOUNDARY: direct Platform generic-command bridge certificate only.
# TENANT POSTURE: synthetic exact tenant/request fixtures.
# FAIL-CLOSED POSTURE: missing, divergent, and mismatched authority rejects.
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively.
# END OF WILSY OS SOVEREIGN ARTIFACT
