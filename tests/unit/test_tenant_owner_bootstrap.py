"""WILSY OS tenant-owner bootstrap behavioral certificate.

TITLE: Tenant-owner bootstrap unit certificate
VERSION: v1.1.1-WILSY-TENANT-OWNER-BOOTSTRAP-CERT
AUTHORITY: Wilsy OS Core Governance
PURPOSE: Executably certify the bounded four-write genesis contract.
EPITOME: In-memory verification of authority, conflicts, transaction and retry semantics.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tests/unit/test_tenant_owner_bootstrap.py
COLLABORATION / OWNERSHIP: Auth orchestration certificate; production and integration remain read-only.
SECURITY / PRIVACY POSTURE: Synthetic identities only; no network, database, or secret material.
TENANT BOUNDARY: Explicit target tenant and authenticated principal are preserved.
AUTHORITY BOUNDARY: Certificate only; no authority grant or execution capability.
FINANCIAL AUTHORITY BOUNDARY: No financial or Kennel authority.
TRANSACTION BOUNDARY: Fake caller-owned session; all reads and writes capture its identity.
CERTIFICATION / UPDATE DATE: 2026-09-05
CHANGELOG: v1.1.1 aligns certificate metadata with the create-command adapter.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2.
"""
from __future__ import annotations
from contextlib import contextmanager
from copy import deepcopy
from dataclasses import FrozenInstanceError
from types import SimpleNamespace
from typing import Any
import inspect
import pytest
import tools.eos.auth.tenant_owner_bootstrap as mod
from tools.eos.auth.identity import SovereignIdentity
from tools.eos.auth.principal_authority import PrincipalAuthority
from tools.eos.auth.principal_status import PrincipalStatus
from tools.eos.auth.tenant_membership_repository import TenantMembershipNotFoundError
from tools.eos.auth.role_assignment_repository import RoleAssignmentNotFoundError
from tools.eos.auth.tenant_business_role_repository import TenantBusinessRoleNotFoundError
from tools.eos.auth.pretenant_bootstrap_authority import PretenantBootstrapAuthorityError, PretenantBootstrapAuthorityDenialCode
from tools.eos.saas.domain.tenant import OrganizationProfile, SubscriptionPlan, TenantEntity

class FakeSession:
    def __init__(self, owner: "FakeClient") -> None: self.owner = owner
    def with_transaction(self, callback: Any) -> None:
        self.owner.trace.extend(["transaction.with_transaction.enter", "transaction.callback.enter"]); self.owner.callbacks += 1; callback(self); self.owner.trace.extend(["transaction.callback.exit", "transaction.with_transaction.return"])
        if self.owner.replay: callback(self)

class FakeClient:
    def __init__(self) -> None:
        self.session = FakeSession(self); self.callbacks = 0; self.replay = False; self.trace: list[str] = []
    @contextmanager
    def start_session(self) -> Any: self.trace.extend(["client.start_session", "session.enter"]); yield self.session; self.trace.append("session.exit")

class Harness:
    def __init__(self) -> None:
        self.client = FakeClient(); self.trace = self.client.trace; self.events: list[tuple[str, Any, Any]] = []; self.existing: dict[str, Any] = {}; self.fail: str | None = None; self.pre_calls = 0
        self.principal = PrincipalAuthority("principal-1", PrincipalStatus.ACTIVE, 0); self.principal_sequence: list[Any] | None = None; h = self
        class PR:
            @staticmethod
            def get(pid: str, *, session: Any = None) -> PrincipalAuthority:
                h.events.append(("principal_get", pid, session)); h.trace.append("principal.get.tx" if session is not None else "principal.get.pre")
                if h.principal_sequence is not None:
                    value = h.principal_sequence.pop(0)
                    if value is None: raise mod.PrincipalAuthorityNotFoundError(pid)
                    return value
                if h.existing.get("principal_missing"): raise mod.PrincipalAuthorityNotFoundError(pid)
                return h.principal
            @staticmethod
            def create(*args: Any, **kwargs: Any) -> None: raise AssertionError("principal create forbidden")
        class TR:
            @staticmethod
            def get(tid: str, *, session: Any = None) -> Any: h.events.append(("tenant_get", tid, session)); h.trace.append("tenant.get"); return h.existing.get("tenant")
            @staticmethod
            def create(value: Any, *, session: Any = None) -> dict[str, Any]:
                h.events.append(("tenant_create", value, session)); h.trace.append("tenant.create")
                if h.fail == "tenant": raise RuntimeError("db secret")
                return {"success": True}
        class MR:
            @staticmethod
            def resolve(*args: Any, session: Any = None, **kwargs: Any) -> Any:
                h.events.append(("membership_resolve", args, session)); h.trace.append("membership.resolve")
                if h.fail == "membership_resolve": raise RuntimeError("db secret")
                if h.existing.get("membership"): return object()
                raise TenantMembershipNotFoundError("missing")
            @staticmethod
            def insert(value: Any, *, session: Any = None) -> None:
                h.events.append(("membership_insert", value, session)); h.trace.append("membership.insert")
                if h.fail == "membership": raise RuntimeError("db secret")
        class RR:
            @staticmethod
            def resolve(*args: Any, session: Any = None, **kwargs: Any) -> Any:
                h.events.append(("role_resolve", args, session)); h.trace.append("auth_role.resolve")
                if h.fail == "role_resolve": raise RuntimeError("db secret")
                if h.existing.get("role"): return object()
                raise RoleAssignmentNotFoundError("missing")
            @staticmethod
            def insert(value: Any, *, session: Any = None) -> None:
                h.events.append(("role_insert", value, session)); h.trace.append("auth_role.insert")
                if h.fail == "role": raise RuntimeError("db secret")
        class BR:
            @staticmethod
            def resolve(*args: Any, session: Any = None, **kwargs: Any) -> Any:
                h.events.append(("business_resolve", args, session)); h.trace.append("business_role.resolve")
                if h.fail == "business_resolve": raise RuntimeError("db secret")
                if h.existing.get("business"): return object()
                raise TenantBusinessRoleNotFoundError("missing")
            @staticmethod
            def insert(value: Any, *, session: Any = None) -> None:
                h.events.append(("business_insert", value, session)); h.trace.append("business_role.insert")
                if h.fail == "business": raise RuntimeError("db secret")
        self.patch = SimpleNamespace(PR=PR, TR=TR, MR=MR, RR=RR, BR=BR)

def identity() -> SovereignIdentity:
    return SovereignIdentity(identity_id="principal-1", tenant_id="bootstrap", username=None, email=None, auth_method="test", status=PrincipalStatus.ACTIVE)
def tenant(name: str = "T1") -> TenantEntity:
    return TenantEntity(organization=OrganizationProfile(name, "legal", SubscriptionPlan.COMMUNITY), tenant_id=name)

@pytest.fixture
def harness(monkeypatch: pytest.MonkeyPatch) -> Harness:
    h = Harness(); monkeypatch.setattr(mod, "PrincipalAuthorityRepository", h.patch.PR); monkeypatch.setattr(mod, "TenantRegistry", h.patch.TR); monkeypatch.setattr(mod, "TenantMembershipRepository", h.patch.MR); monkeypatch.setattr(mod, "RoleAssignmentRepository", h.patch.RR); monkeypatch.setattr(mod, "TenantBusinessRoleRepository", h.patch.BR); monkeypatch.setattr(mod, "get_client", lambda: h.client); monkeypatch.setattr(mod, "verify_pretenant_bootstrap_authority", lambda _i: (h.trace.append("pretenant.verify"), setattr(h, "pre_calls", h.pre_calls + 1))); return h

def test_success_fixed_genesis_and_same_session(harness: Harness) -> None:
    result = mod.bootstrap_tenant_owner(identity=identity(), tenant=tenant())
    assert isinstance(result, mod.TenantOwnerBootstrapResult) and result.tenant.tenant_id == "T1"
    assert result.membership.principal_id == "principal-1" and result.membership.status.value == "ACTIVE" and result.membership.revision == 0
    assert result.authorization_role.role_id == "ENTERPRISE_ADMIN" and result.business_role.business_role == "tenant_owner"
    assert result.business_role.status.value == "ACTIVE" and result.business_role.revision == 0
    assert harness.pre_calls == 1 and harness.client.callbacks == 1
    assert all(event[2] is harness.client.session for event in harness.events if event[2] is not None)
    with pytest.raises(FrozenInstanceError): setattr(result, "tenant", tenant("x"))

def test_conflicts_and_fail_closed(harness: Harness) -> None:
    for key, code in [("tenant", "TENANT_ALREADY_EXISTS"), ("membership", "MEMBERSHIP_ALREADY_EXISTS"), ("role", "AUTHORIZATION_ROLE_ALREADY_EXISTS"), ("business", "BUSINESS_ROLE_ALREADY_EXISTS")]:
        harness.existing[key] = object()
        with pytest.raises(mod.TenantOwnerBootstrapError, match=code): mod.bootstrap_tenant_owner(identity=identity(), tenant=tenant())
        harness.existing.clear()
    harness.principal = PrincipalAuthority("principal-1", PrincipalStatus.SUSPENDED, 0)
    with pytest.raises(mod.TenantOwnerBootstrapError, match="PRINCIPAL_NOT_ACTIVE"): mod.bootstrap_tenant_owner(identity=identity(), tenant=tenant())

def test_pretenant_passthrough_and_public_signature(harness: Harness, monkeypatch: pytest.MonkeyPatch) -> None:
    def deny(_identity: SovereignIdentity) -> None: raise PretenantBootstrapAuthorityError(PretenantBootstrapAuthorityDenialCode.MALFORMED_IDENTITY)
    monkeypatch.setattr(mod, "verify_pretenant_bootstrap_authority", deny)
    with pytest.raises(PretenantBootstrapAuthorityError): mod.bootstrap_tenant_owner(identity=identity(), tenant=tenant())
    assert harness.client.callbacks == 0 and list(inspect.signature(mod.bootstrap_tenant_owner).parameters) == ["identity", "tenant"]

@pytest.mark.parametrize("failure", ["tenant", "membership", "role", "business", "membership_resolve", "role_resolve", "business_resolve"])
def test_failures_are_bounded(harness: Harness, failure: str) -> None:
    harness.fail = failure
    with pytest.raises(mod.TenantOwnerBootstrapError) as exc: mod.bootstrap_tenant_owner(identity=identity(), tenant=tenant())
    assert "db secret" not in str(exc.value)
    assert exc.value.code is mod.TenantOwnerBootstrapDenialCode.PERSISTENCE_FAILURE

@pytest.mark.parametrize("failure,blocked", [("tenant", ["membership_insert", "role_insert", "business_insert"]), ("membership", ["role_insert", "business_insert"]), ("role", ["business_insert"]), ("business", [])])
def test_write_failure_order_is_fail_closed(harness: Harness, failure: str, blocked: list[str]) -> None:
    harness.fail = failure
    with pytest.raises(mod.TenantOwnerBootstrapError): mod.bootstrap_tenant_owner(identity=identity(), tenant=tenant())
    for kind in blocked: assert not any(event[0] == kind for event in harness.events)

def test_multi_tenant_and_vocab() -> None:
    assert {c.value for c in mod.TenantOwnerBootstrapDenialCode} == {"PRINCIPAL_NOT_FOUND", "PRINCIPAL_NOT_ACTIVE", "TENANT_ALREADY_EXISTS", "MEMBERSHIP_ALREADY_EXISTS", "AUTHORIZATION_ROLE_ALREADY_EXISTS", "BUSINESS_ROLE_ALREADY_EXISTS", "PERSISTENCE_FAILURE", "INTERNAL_INVARIANT_FRACTURE"}
    source = open(mod.__file__, encoding="utf-8").read()
    for forbidden in ("authorize_tenant_operation", "evaluate_business_role_mutation", "FastAPI", "tools.eos.saas.billing"): assert forbidden not in source

def test_retry_reuses_frozen_values(harness: Harness) -> None:
    harness.client.replay = True
    mod.bootstrap_tenant_owner(identity=identity(), tenant=tenant())
    for kind in ("membership_insert", "role_insert", "business_insert"):
        values = [event[1] for event in harness.events if event[0] == kind]
        assert len(values) == 2 and values[0] == values[1]

def test_principal_missing_is_fail_closed(harness: Harness) -> None:
    harness.existing["principal_missing"] = True
    with pytest.raises(mod.TenantOwnerBootstrapError, match="PRINCIPAL_NOT_FOUND"): mod.bootstrap_tenant_owner(identity=identity(), tenant=tenant())
    assert harness.client.callbacks == 0

def test_partial_state_is_not_repaired(harness: Harness) -> None:
    harness.existing["membership"] = object()
    with pytest.raises(mod.TenantOwnerBootstrapError, match="MEMBERSHIP_ALREADY_EXISTS"):
        mod.bootstrap_tenant_owner(identity=identity(), tenant=tenant())
    assert not any(event[0] in {"tenant_create", "membership_insert", "role_insert", "business_insert"} for event in harness.events)

def test_same_principal_bootstraps_distinct_tenants(harness: Harness) -> None:
    first = mod.bootstrap_tenant_owner(identity=identity(), tenant=tenant("T1"))
    second = mod.bootstrap_tenant_owner(identity=identity(), tenant=tenant("T2"))
    assert first.tenant.tenant_id != second.tenant.tenant_id
    assert first.membership.principal_id == second.membership.principal_id == "principal-1"
    assert not any(event[0] == "principal_create" for event in harness.events)

def test_same_target_repeat_conflicts(harness: Harness) -> None:
    mod.bootstrap_tenant_owner(identity=identity(), tenant=tenant("T1"))
    harness.existing["tenant"] = object()
    before = len(harness.events)
    with pytest.raises(mod.TenantOwnerBootstrapError, match="TENANT_ALREADY_EXISTS"):
        mod.bootstrap_tenant_owner(identity=identity(), tenant=tenant("T1"))
    later = [event[0] for event in harness.events[before:]]
    assert "membership_insert" not in later and "role_insert" not in later and "business_insert" not in later

@pytest.mark.parametrize("second,expected", [(None, "PRINCIPAL_NOT_FOUND"), (PrincipalAuthority("principal-1", PrincipalStatus.SUSPENDED, 1), "PRINCIPAL_NOT_ACTIVE")])
def test_callback_principal_revalidation(harness: Harness, second: Any, expected: str) -> None:
    harness.principal_sequence = [PrincipalAuthority("principal-1", PrincipalStatus.ACTIVE, 0), second]
    with pytest.raises(mod.TenantOwnerBootstrapError, match=expected): mod.bootstrap_tenant_owner(identity=identity(), tenant=tenant())
    principal_reads = [event for event in harness.events if event[0] == "principal_get"]
    assert len(principal_reads) == 2 and principal_reads[0][2] is None and principal_reads[1][2] is harness.client.session
    assert not any(event[0].endswith("_insert") or event[0] == "tenant_create" for event in harness.events)

def test_ordered_read_write_trace(harness: Harness) -> None:
    mod.bootstrap_tenant_owner(identity=identity(), tenant=tenant())
    names = [event[0] for event in harness.events]
    positions = {name: names.index(name) for name in ("principal_get", "tenant_get", "membership_resolve", "role_resolve", "business_resolve", "tenant_create", "membership_insert", "role_insert", "business_insert")}
    assert positions["principal_get"] < positions["tenant_get"] < positions["tenant_create"] < positions["membership_insert"] < positions["role_insert"] < positions["business_insert"]
    assert positions["business_resolve"] < positions["tenant_create"]

def test_full_lifecycle_trace(harness: Harness) -> None:
    mod.bootstrap_tenant_owner(identity=identity(), tenant=tenant()); harness.trace.append("bootstrap.return")
    required = ["pretenant.verify", "principal.get.pre", "client.start_session", "session.enter", "transaction.with_transaction.enter", "transaction.callback.enter", "principal.get.tx", "tenant.get", "membership.resolve", "auth_role.resolve", "business_role.resolve", "tenant.create", "membership.insert", "auth_role.insert", "business_role.insert", "transaction.callback.exit", "transaction.with_transaction.return", "session.exit", "bootstrap.return"]
    assert all(harness.trace.index(required[i]) < harness.trace.index(required[i + 1]) for i in range(len(required) - 1))

@pytest.mark.parametrize("keyword", ["owner", "principal_id", "role", "authorization_role", "business_role", "session", "repository", "client", "pretenant_authority", "authority", "config"])
def test_unauthorized_keywords_rejected(keyword: str) -> None:
    with pytest.raises(TypeError): mod.bootstrap_tenant_owner(identity=identity(), tenant=tenant(), **{keyword: object()})

def test_projection_values_do_not_bypass_pretenant(harness: Harness, monkeypatch: pytest.MonkeyPatch) -> None:
    privileged = SovereignIdentity(identity_id="principal-1", tenant_id="other", username="x", email="x", roles=["OWNER"], permissions=["*"], auth_method="token", status=PrincipalStatus.ACTIVE)
    def deny(_identity: SovereignIdentity) -> None: raise PretenantBootstrapAuthorityError(PretenantBootstrapAuthorityDenialCode.MALFORMED_IDENTITY)
    monkeypatch.setattr(mod, "verify_pretenant_bootstrap_authority", deny)
    with pytest.raises(PretenantBootstrapAuthorityError): mod.bootstrap_tenant_owner(identity=privileged, tenant=tenant())
    assert harness.client.callbacks == 0

def test_exact_nondefault_registry_create_command_mapping(harness: Harness, monkeypatch: pytest.MonkeyPatch) -> None:
    source = TenantEntity(organization=OrganizationProfile("Acme Sovereign", "aviation", SubscriptionPlan.ENTERPRISE, "Acme Legal", "TAX-42", "ops@acme.test", ["ZA", "EU"]), tenant_id="tenant-nondefault", status="ACTIVE", alias="acme", region="ZA", compliance_flags={"regulated": True}, verified=True)
    captured: list[dict[str, Any]] = []
    def create(payload: dict[str, Any], *, session: Any = None) -> dict[str, Any]: captured.append(deepcopy(payload)); return {"success": True}
    monkeypatch.setattr(harness.patch.TR, "create", staticmethod(create)); mod.bootstrap_tenant_owner(identity=identity(), tenant=source)
    payload = captured[0]
    assert payload["tenant_id"] == source.tenant_id and payload["name"] == "Acme Sovereign" and payload["organization_name"] == "Acme Sovereign"
    assert payload["industry"] == "aviation" and payload["plan"] == "ENTERPRISE" and payload["legal_name"] == "Acme Legal" and payload["tax_id"] == "TAX-42" and payload["contact_email"] == "ops@acme.test" and payload["regions"] == ["ZA", "EU"]
    assert payload["status"] == "ACTIVE" and payload["alias"] == "acme" and payload["region"] == "ZA" and payload["compliance_flags"] == {"regulated": True} and payload["verified"] is True
    assert not {"role", "roles", "permission", "permissions", "authorization", "principal_authority", "business_role", "payment", "settlement", "financial_execution", "kennel_command"}.intersection(payload)

def test_frozen_create_command_survives_transaction_callback_retry(harness: Harness, monkeypatch: pytest.MonkeyPatch) -> None:
    source = tenant("retry-stable"); captured: list[dict[str, Any]] = []; calls = 0
    def create(payload: dict[str, Any], *, session: Any = None) -> dict[str, Any]:
        nonlocal calls
        calls += 1; captured.append(deepcopy(payload))
        if calls == 1: source.organization.organization_name = "MUTATED_AFTER_FIRST_CALLBACK"
        return {"success": True}
    monkeypatch.setattr(harness.patch.TR, "create", staticmethod(create)); harness.client.replay = True; mod.bootstrap_tenant_owner(identity=identity(), tenant=source)
    assert len(captured) == 2 and captured[0] == captured[1] and captured[0]["name"] == "retry-stable"

# ARTIFACT: test_tenant_owner_bootstrap.py
# VERSION: v1.1.1-WILSY-TENANT-OWNER-BOOTSTRAP-CERT
# AUTHORITY BOUNDARY: Certificate only; no authority grant.
# TENANT POSTURE: Explicit tenant scope; caller-owned transaction evidence.
# FAIL-CLOSED POSTURE: Contract drift and persistence failures deny.
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS remains exclusive.
# END OF WILSY OS SOVEREIGN ARTIFACT
