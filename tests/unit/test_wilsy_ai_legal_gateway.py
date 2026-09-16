"""Direct certificate for the Phase B WILSY AI Legal Tool Gateway.

TITLE: WILSY AI Legal Tool Gateway Direct Certificate
VERSION: v1.2.0-L7B-WILSY-AI-LEGAL-TOOL-GATEWAY-CERT
CERTIFICATION DATE: 2026-09-15
AUTHORITY: Direct unit proof of bounded read-only gateway contracts.
TENANT BOUNDARY: Exact own-tenant contexts only; pseudo/global tenants reject.
AUTHORITY BOUNDARY: IAM, entitlement, capacity and legal evidence remain canonical.
FAIL-CLOSED: Unknown tools, commands, malformed input and exhausted capacity reject.
FINANCIAL AUTHORITY: Kennel EOS exclusively owns execution and settlement.
CHANGELOG: v1.2.0 adds direct Mongo transport hydration, replay, divergence,
           unknown-field, corruption, and caller-session regression proofs.
           v1.1.0 established the gateway direct certificate.
"""
from __future__ import annotations

from datetime import datetime, timezone
from dataclasses import replace
from types import SimpleNamespace
import asyncio
from typing import Any, cast

import pytest
from pydantic import ValidationError

from tools.eos.api.tenant_authorization_http import TenantAuthorizationContext
from tools.eos.api.wilsy_ai_legal_gateway_router import LegalToolInvokeRequest, router
from tools.eos.auth.identity import SovereignIdentity
from tools.eos.auth.principal_status import PrincipalStatus
from tools.eos.auth.roles import ROLE_PERMISSIONS_MAP, get_roles_granting_permission
from tools.eos.auth.tenant_authority_policy import tenant_role_operation_eligibility, ELIGIBLE
from tools.eos.auth.tenant_authorization import TenantAuthorizationDecision, TenantAuthorizationReason
from tools.eos.intelligence.domain.legal_ai_gateway import (
    CAPABILITIES, GATEWAY_PERMISSION, TOOL_CONTRACTS, TOOL_IDENTITIES,
    LegalAIToolContract, LegalAIToolGatewayError, authorize_legal_ai_tool,
)
from tools.eos.intelligence.domain import legal_ai_read_adapter as read_adapter_module
from tools.eos.intelligence.domain.legal_ai_read_adapter import LegalAIReadAdapter
from tools.eos.intelligence.registry.legal_ai_tool_invocation_registry import LegalAIToolInvocationConflictError, LegalAIToolInvocationRegistry, LegalAIToolInvocationRegistryError


def _context(tenant: str = "tenant-a", allowed: bool = True) -> TenantAuthorizationContext:
    identity = SovereignIdentity(identity_id="principal-1", tenant_id=tenant, username="tester", email="tester@example.com", auth_method="test", status=PrincipalStatus.ACTIVE)
    decision = TenantAuthorizationDecision(allowed, TenantAuthorizationReason.AUTHORIZED if allowed else TenantAuthorizationReason.PERMISSION_NOT_GRANTED, "tenant_legal_attorney", "LEGAL_ATTORNEY")
    return TenantAuthorizationContext(identity=identity, tenant_id=tenant, decision=decision)


def _facts(tenant: str = "tenant-a", remaining: int = 10) -> tuple[Any, Any]:
    entitlement = SimpleNamespace(tenant_id=tenant, entitlement_id="ent-1", lifecycle_state="ACTIVE", policy_fingerprint="a" * 128, capability_grants=("legal.read.instruction",), lifecycle_revision=1, fingerprint="e" * 128, tier=SimpleNamespace(value="WILSY_AI_STARTER"))
    capacity = SimpleNamespace(tenant_id=tenant, entitlement_fingerprint=entitlement.fingerprint, daily_remaining_request_units=remaining, monthly_remaining_automation_actions=remaining, daily_exhausted=remaining <= 0, monthly_exhausted=remaining <= 0, fingerprint="c" * 128)
    return entitlement, capacity


def test_entitlement_fingerprint_is_canonical_capacity_identity() -> None:
    entitlement, capacity = _facts()
    assert entitlement.fingerprint != entitlement.policy_fingerprint
    assert capacity.entitlement_fingerprint == entitlement.fingerprint
    evidence = authorize_legal_ai_tool(
        gateway_context=_context(), underlying_context=_context(), entitlement=entitlement,
        capacity=capacity, tool_identity=TOOL_IDENTITIES[0],
        input_payload={"resource_identity": "r", "entitlement_id": "ent-1", "correlation_id": "fp-ok"},
        occurred_at=datetime.now(timezone.utc),
    )
    assert evidence.entitlement_fingerprint == entitlement.fingerprint
    assert evidence.policy_fingerprint == entitlement.policy_fingerprint


def test_entitlement_fingerprint_mismatch_and_policy_substitution_fail_closed() -> None:
    entitlement, capacity = _facts()
    capacity.entitlement_fingerprint = "f" * 128
    with pytest.raises(LegalAIToolGatewayError, match="L7B_ENTITLEMENT_DENIED"):
        authorize_legal_ai_tool(
            gateway_context=_context(), underlying_context=_context(), entitlement=entitlement,
            capacity=capacity, tool_identity=TOOL_IDENTITIES[0],
            input_payload={"resource_identity": "r", "entitlement_id": "ent-1", "correlation_id": "fp-bad"},
            occurred_at=datetime.now(timezone.utc),
        )
    capacity.entitlement_fingerprint = entitlement.policy_fingerprint
    with pytest.raises(LegalAIToolGatewayError, match="L7B_ENTITLEMENT_DENIED"):
        authorize_legal_ai_tool(
            gateway_context=_context(), underlying_context=_context(), entitlement=entitlement,
            capacity=capacity, tool_identity=TOOL_IDENTITIES[0],
            input_payload={"resource_identity": "r", "entitlement_id": "ent-1", "correlation_id": "fp-policy"},
            occurred_at=datetime.now(timezone.utc),
        )


def test_exactly_seven_read_tools_and_no_commands() -> None:
    assert TOOL_IDENTITIES == tuple(TOOL_CONTRACTS)
    assert len(TOOL_IDENTITIES) == 7
    assert all("read" in identity and "command" not in identity for identity in TOOL_IDENTITIES)
    assert len(CAPABILITIES) == 7


def test_contract_rejects_unknown_identity() -> None:
    with pytest.raises(LegalAIToolGatewayError):
        LegalAIToolContract("legal.command.write.v1", "v1", "legal_operations:instruction:read", CAPABILITIES[0], "X", "NONE", ("x",))


def test_request_forbids_tenant_and_extra_fields() -> None:
    with pytest.raises(ValidationError):
        LegalToolInvokeRequest.model_validate({"resource_identity":"x", "entitlement_id":"e", "correlation_id":"c", "tenant_id":"tenant-a"})


def test_gateway_permission_is_dedicated() -> None:
    assert GATEWAY_PERMISSION == "wilsy_ai:legal_tool:read"
    assert tenant_role_operation_eligibility("tenant_legal_attorney", "wilsy_ai_legal_tool_read") == ELIGIBLE
    assert tenant_role_operation_eligibility("tenant_legal_client", "wilsy_ai_legal_tool_read") != ELIGIBLE
    assert "LEGAL_ATTORNEY" in get_roles_granting_permission(GATEWAY_PERMISSION)
    assert "LEGAL_CLIENT" not in get_roles_granting_permission(GATEWAY_PERMISSION)


def test_role_least_privilege_is_preserved_for_gateway_tools() -> None:
    assert GATEWAY_PERMISSION not in ROLE_PERMISSIONS_MAP["LEGAL_CLIENT"]
    assert "legal_operations:instruction:read" not in ROLE_PERMISSIONS_MAP["LEGAL_FINANCE"]
    assert "legal_operations:invoice:read" not in ROLE_PERMISSIONS_MAP["SHERIFF"]
    assert "legal_operations:billing:read" not in ROLE_PERMISSIONS_MAP["DEPUTY"]


def test_unknown_tool_fails_closed() -> None:
    entitlement, capacity = _facts()
    with pytest.raises(LegalAIToolGatewayError, match="L7B_TOOL_UNKNOWN"):
        authorize_legal_ai_tool(gateway_context=_context(), underlying_context=_context(), entitlement=entitlement, capacity=capacity, tool_identity="legal.command.v1", input_payload={"resource_identity": "r", "entitlement_id": "ent-1", "correlation_id": "c"}, occurred_at=datetime.now(timezone.utc))


def test_denied_gateway_fails_closed() -> None:
    entitlement, capacity = _facts()
    with pytest.raises(LegalAIToolGatewayError, match="L7B_PERMISSION_DENIED"):
        authorize_legal_ai_tool(gateway_context=_context(allowed=False), underlying_context=_context(), entitlement=entitlement, capacity=capacity, tool_identity=TOOL_IDENTITIES[0], input_payload={"resource_identity": "r", "entitlement_id": "ent-1", "correlation_id": "c"}, occurred_at=datetime.now(timezone.utc))


def test_foreign_tenant_fails_closed() -> None:
    entitlement, capacity = _facts("tenant-b")
    with pytest.raises(LegalAIToolGatewayError, match="L7B_TENANT_MISMATCH"):
        authorize_legal_ai_tool(gateway_context=_context("tenant-a"), underlying_context=_context("tenant-a"), entitlement=entitlement, capacity=capacity, tool_identity=TOOL_IDENTITIES[0], input_payload={"resource_identity": "r", "entitlement_id": "ent-1", "correlation_id": "c"}, occurred_at=datetime.now(timezone.utc))


def test_exhausted_capacity_fails_closed() -> None:
    entitlement, capacity = _facts(remaining=0)
    with pytest.raises(LegalAIToolGatewayError, match="L7B_CAPACITY_EXHAUSTED"):
        authorize_legal_ai_tool(gateway_context=_context(), underlying_context=_context(), entitlement=entitlement, capacity=capacity, tool_identity=TOOL_IDENTITIES[0], input_payload={"resource_identity": "r", "entitlement_id": "ent-1", "correlation_id": "c"}, occurred_at=datetime.now(timezone.utc))


def test_missing_capability_fails_closed() -> None:
    entitlement, capacity = _facts()
    cast(Any, entitlement).capability_grants = ("legal.read.invoice",)
    with pytest.raises(LegalAIToolGatewayError, match="L7B_ENTITLEMENT_DENIED"):
        authorize_legal_ai_tool(gateway_context=_context(), underlying_context=_context(), entitlement=entitlement, capacity=capacity, tool_identity=TOOL_IDENTITIES[0], input_payload={"resource_identity": "r", "entitlement_id": "ent-1", "correlation_id": "c"}, occurred_at=datetime.now(timezone.utc))


def test_input_tenant_override_and_extra_fields_reject() -> None:
    entitlement, capacity = _facts()
    with pytest.raises(LegalAIToolGatewayError, match="L7B_INPUT_INVALID"):
        authorize_legal_ai_tool(gateway_context=_context(), underlying_context=_context(), entitlement=entitlement, capacity=capacity, tool_identity=TOOL_IDENTITIES[0], input_payload={"resource_identity": "r", "entitlement_id": "ent-1", "correlation_id": "c", "tenant_id": "tenant-a"}, occurred_at=datetime.now(timezone.utc))


def test_evidence_is_bounded_and_deterministic() -> None:
    entitlement, capacity = _facts()
    evidence = authorize_legal_ai_tool(gateway_context=_context(), underlying_context=_context(), entitlement=entitlement, capacity=capacity, tool_identity=TOOL_IDENTITIES[0], input_payload={"resource_identity": "r", "entitlement_id": "ent-1", "correlation_id": "c"}, occurred_at=datetime.now(timezone.utc))
    payload = evidence.to_dict()
    assert "prompt" not in payload and "chain_of_thought" not in payload and "secret" not in payload
    assert evidence.fingerprint == evidence.__class__.from_dict(payload).fingerprint


def test_router_exposes_only_get_and_post_gateway_paths() -> None:
    paths = {getattr(route, "path", "") for route in router.routes}
    assert paths == {"/wilsy-ai/legal-tools", "/wilsy-ai/legal-tools/{tool_identity}/invoke"}


def test_financial_authority_is_not_in_gateway_contracts() -> None:
    assert all("payment" not in contract.underlying_permission and "settlement" not in contract.underlying_permission for contract in TOOL_CONTRACTS.values())


def test_read_adapter_delegates_all_allowlisted_projections(monkeypatch: pytest.MonkeyPatch) -> None:
    """Every public tool delegates to the existing L7A/L7C callable map."""
    calls: list[str] = []

    async def fake_projection(*args: Any, **kwargs: Any) -> dict[str, object]:
        calls.append(str(kwargs.get("collection") or kwargs.get("invoice_collection") or "projection"))
        return {"data": {"tenant_id": "tenant-a", "instruction_id": "i-1", "document_id": "d-1", "attempt_id": "a-1", "execution_id": "x-1", "return_id": "r-1", "tariff_assessment_id": "ta-1", "billing_eligibility_id": "be-1", "invoice_id": "inv-1", "deputy_id": "dep-1", "state": "ALLOCATED", "evidence_identity": "ev-1", "executed_at": "2026-09-15T00:00:00Z", "assessed_total_minor_units": 100, "eligible_minor_units": 100, "total_minor": 100, "currency": "ZAR", "issued_at": "2026-09-15T00:00:00Z"}}

    for name in ("get_instruction", "get_attempt", "get_execution", "get_return_of_service"):
        monkeypatch.setattr(read_adapter_module.l7a, name, fake_projection)
    for name in ("get_tariff_assessment", "get_billing_eligibility", "get_invoice"):
        monkeypatch.setattr(read_adapter_module.l7c, name, fake_projection)

    context = _context()
    collections = {"lifecycle": object(), "tariff": object(), "eligibility": object(), "invoice": object(), "issuance": object()}

    async def exercise() -> list[dict[str, object]]:
        adapter = LegalAIReadAdapter()
        return [await adapter.read(contract=contract, resource_identity="resource-1", context=context, collections=collections) for contract in TOOL_CONTRACTS.values()]

    results = asyncio.run(exercise())
    assert len(results) == 7
    assert len(calls) == 7
    assert all(result.get("tenant_id") == "tenant-a" for result in results)
    assert all(set(result).issubset(set(contract.allowed_fields)) for result, contract in zip(results, TOOL_CONTRACTS.values()))


def test_invoke_composes_entitlement_capacity_iam_read_and_evidence(monkeypatch: pytest.MonkeyPatch) -> None:
    """The API composition path commits only after canonical read and evidence persistence."""
    entitlement, capacity = _facts(remaining=10)
    cast(Any, entitlement).capability_grants = CAPABILITIES
    commits: list[str] = []

    class Session:
        def start_transaction(self) -> None: pass
        def commit_transaction(self) -> None: commits.append("commit")
        def abort_transaction(self) -> None: commits.append("abort")
        def end_session(self) -> None: commits.append("end")

    class Entitlements:
        def __init__(self, collection: Any) -> None: pass
        def get_by_module(self, **kwargs: Any) -> Any: return entitlement

    class Capacity:
        @classmethod
        def from_collections(cls, **kwargs: Any) -> "Capacity": return cls()
        def derive_capacity(self, **kwargs: Any) -> Any: return capacity

    class Adapter:
        async def read(self, **kwargs: Any) -> dict[str, object]: return {"tenant_id": "tenant-a", "resource_identity": kwargs["resource_identity"]}

    class Invocations:
        def __init__(self, collection: Any) -> None: pass
        def create_or_replay(self, evidence: Any, **kwargs: Any) -> Any: return evidence

    monkeypatch.setattr("tools.eos.api.wilsy_ai_legal_gateway_router._begin_transaction", lambda: (object(), Session()))
    monkeypatch.setattr("tools.eos.api.wilsy_ai_legal_gateway_router._collections", lambda: {"entitlement": object(), "observation": object(), "lifecycle": object(), "tariff": object(), "eligibility": object(), "invoice": object(), "issuance": object(), "invocation": object()})
    monkeypatch.setattr("tools.eos.api.wilsy_ai_legal_gateway_router.WilsyAIEntitlementRegistry", Entitlements)
    monkeypatch.setattr("tools.eos.api.wilsy_ai_legal_gateway_router.WilsyAIUsageCapacityOrchestrator", Capacity)
    monkeypatch.setattr("tools.eos.api.wilsy_ai_legal_gateway_router._canonical_underlying_context", lambda context, contract, session, principal_repository, membership_repository, role_assignment_repository: context)
    monkeypatch.setattr("tools.eos.api.wilsy_ai_legal_gateway_router.LegalAIReadAdapter", Adapter)
    monkeypatch.setattr("tools.eos.api.wilsy_ai_legal_gateway_router.LegalAIToolInvocationRegistry", Invocations)

    context = _context()

    async def exercise() -> list[dict[str, object]]:
        values: list[dict[str, object]] = []
        for identity in TOOL_IDENTITIES:
            values.append(await router_module.invoke_legal_tool(identity, LegalToolInvokeRequest(resource_identity="resource-1", entitlement_id="ent-1", correlation_id=f"corr-{identity}"), context=context, principal_repository=object(), membership_repository=object(), role_assignment_repository=object()))
        return values

    import tools.eos.api.wilsy_ai_legal_gateway_router as router_module
    results = asyncio.run(exercise())
    assert len(results) == 7
    assert all(result["tool"] in TOOL_IDENTITIES for result in results)
    assert commits.count("commit") == 7
    assert commits.count("abort") == 0


def test_list_composes_only_currently_usable_tools(monkeypatch: pytest.MonkeyPatch) -> None:
    entitlement, capacity = _facts(remaining=10)
    cast(Any, entitlement).capability_grants = CAPABILITIES

    class Session:
        def start_transaction(self) -> None: pass
        def commit_transaction(self) -> None: self.committed = True
        def abort_transaction(self) -> None: self.aborted = True
        def end_session(self) -> None: pass

    class Entitlements:
        def __init__(self, collection: Any) -> None: pass
        def get_by_module(self, **kwargs: Any) -> Any: return entitlement

    class Capacity:
        @classmethod
        def from_collections(cls, **kwargs: Any) -> "Capacity": return cls()
        def derive_capacity(self, **kwargs: Any) -> Any: return capacity

    session = Session()
    monkeypatch.setattr("tools.eos.api.wilsy_ai_legal_gateway_router._begin_transaction", lambda: (object(), session))
    monkeypatch.setattr("tools.eos.api.wilsy_ai_legal_gateway_router._collections", lambda: {"entitlement": object(), "observation": object()})
    monkeypatch.setattr("tools.eos.api.wilsy_ai_legal_gateway_router.WilsyAIEntitlementRegistry", Entitlements)
    monkeypatch.setattr("tools.eos.api.wilsy_ai_legal_gateway_router.WilsyAIUsageCapacityOrchestrator", Capacity)
    monkeypatch.setattr("tools.eos.api.wilsy_ai_legal_gateway_router._canonical_underlying_context", lambda context, contract, session, principal_repository, membership_repository, role_assignment_repository: context)

    import tools.eos.api.wilsy_ai_legal_gateway_router as router_module
    result = asyncio.run(router_module.list_legal_tools(context=_context(), principal_repository=object(), membership_repository=object(), role_assignment_repository=object()))
    assert result["tenant_id"] == "tenant-a"
    tools = cast(list[dict[str, object]], result["tools"])
    assert {str(item["identity"]) for item in tools} == set(TOOL_IDENTITIES)
    assert getattr(session, "committed", False) is True
    assert not getattr(session, "aborted", False)


def test_invocation_registry_persists_exact_replay_and_rejects_divergence() -> None:
    entitlement, capacity = _facts()
    evidence = authorize_legal_ai_tool(gateway_context=_context(), underlying_context=_context(), entitlement=entitlement, capacity=capacity, tool_identity=TOOL_IDENTITIES[0], input_payload={"resource_identity": "resource-1", "entitlement_id": "ent-1", "correlation_id": "corr-1"}, occurred_at=datetime.now(timezone.utc), result_reference="LegalInstruction:resource-1")

    class Collection:
        def __init__(self) -> None:
            self.rows: dict[tuple[str, str], dict[str, object]] = {}
            self.insert_count = 0
            self.find_sessions: list[object] = []
            self.insert_sessions: list[object] = []
        def find_one(self, query: dict[str, str], **kwargs: Any) -> dict[str, object] | None:
            self.find_sessions.append(kwargs.get("session"))
            row = self.rows.get((query["tenant_id"], query["invocation_id"]))
            return dict(row) if row is not None else None
        def insert_one(self, document: dict[str, object], **kwargs: Any) -> None:
            self.insert_count += 1
            self.insert_sessions.append(kwargs.get("session"))
            self.rows[(str(document["tenant_id"]), str(document["invocation_id"]))] = {"_id": f"mongo-{self.insert_count}", **dict(document)}

    collection = Collection()
    registry = LegalAIToolInvocationRegistry(collection)
    session = object()
    first = registry.create_or_replay(evidence, session=session)
    replay = registry.create_or_replay(evidence, session=session)
    assert first.to_dict() == replay.to_dict()
    assert collection.insert_count == 1
    assert collection.insert_sessions == [session]
    assert collection.find_sessions == [session, session]
    assert first.invocation_id == replay.invocation_id
    assert first.input_fingerprint == replay.input_fingerprint
    assert first.result_fingerprint == replay.result_fingerprint
    assert first.fingerprint == replay.fingerprint
    divergent = replace(evidence, result_reference="LegalInstruction:other", fingerprint="")
    with pytest.raises(LegalAIToolInvocationConflictError, match="L7B_DIVERGENT_REPLAY"):
        registry.create_or_replay(divergent, session=session)


def test_invocation_registry_hydrates_mongo_transport_id_and_preserves_session() -> None:
    """Mongo's transport _id is adapter metadata, not canonical evidence."""
    entitlement, capacity = _facts()
    evidence = authorize_legal_ai_tool(
        gateway_context=_context(), underlying_context=_context(), entitlement=entitlement,
        capacity=capacity, tool_identity=TOOL_IDENTITIES[0],
        input_payload={"resource_identity": "resource-1", "entitlement_id": "ent-1", "correlation_id": "mongo-get"},
        occurred_at=datetime.now(timezone.utc), result_reference="LegalInstruction:resource-1",
    )

    class Collection:
        def __init__(self) -> None:
            self.row = {"_id": "mongo-transport-id", **evidence.to_dict()}
            self.sessions: list[object] = []
        def find_one(self, query: dict[str, str], **kwargs: Any) -> dict[str, object]:
            self.sessions.append(kwargs["session"])
            return dict(self.row)

    collection = Collection()
    registry = LegalAIToolInvocationRegistry(collection)
    session = object()
    hydrated = registry.get(tenant_id="tenant-a", invocation_id="mongo-get", session=session)
    assert hydrated.to_dict() == evidence.to_dict()
    assert collection.sessions == [session]


def test_invocation_registry_rejects_unknown_mongo_row_fields() -> None:
    """Only _id is stripped; unexpected application fields remain forbidden."""
    entitlement, capacity = _facts()
    evidence = authorize_legal_ai_tool(
        gateway_context=_context(), underlying_context=_context(), entitlement=entitlement,
        capacity=capacity, tool_identity=TOOL_IDENTITIES[0],
        input_payload={"resource_identity": "resource-1", "entitlement_id": "ent-1", "correlation_id": "unknown-field"},
        occurred_at=datetime.now(timezone.utc), result_reference="LegalInstruction:resource-1",
    )

    class Collection:
        def find_one(self, query: dict[str, str], **kwargs: Any) -> dict[str, object]:
            return {"_id": "mongo-transport-id", **evidence.to_dict(), "unexpected_domain_field": "reject"}

    with pytest.raises(LegalAIToolInvocationRegistryError, match="L7B_CORRUPT_EVIDENCE"):
        LegalAIToolInvocationRegistry(Collection()).get(tenant_id="tenant-a", invocation_id="unknown-field", session=object())


def test_invocation_registry_rejects_tampered_fingerprint_with_mongo_id() -> None:
    """Transport cleanup does not weaken canonical fingerprint verification."""
    entitlement, capacity = _facts()
    evidence = authorize_legal_ai_tool(
        gateway_context=_context(), underlying_context=_context(), entitlement=entitlement,
        capacity=capacity, tool_identity=TOOL_IDENTITIES[0],
        input_payload={"resource_identity": "resource-1", "entitlement_id": "ent-1", "correlation_id": "tampered"},
        occurred_at=datetime.now(timezone.utc), result_reference="LegalInstruction:resource-1",
    )

    class Collection:
        def find_one(self, query: dict[str, str], **kwargs: Any) -> dict[str, object]:
            return {"_id": "mongo-transport-id", **evidence.to_dict(), "fingerprint": "0" * 128}

    with pytest.raises(LegalAIToolInvocationRegistryError, match="L7B_CORRUPT_EVIDENCE"):
        LegalAIToolInvocationRegistry(Collection()).get(tenant_id="tenant-a", invocation_id="tampered", session=object())


# ARTIFACT: test_wilsy_ai_legal_gateway.py
# VERSION: v1.2.0-L7B-WILSY-AI-LEGAL-TOOL-GATEWAY-CERT
# AUTHORITY BOUNDARY: direct regression proof for canonical read authorization
# TENANT POSTURE: exact own-tenant IAM, entitlement and capacity binding
# FAIL-CLOSED POSTURE: identity, capability, IAM and capacity mismatches reject
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively
# END OF WILSY OS SOVEREIGN CERTIFICATE
