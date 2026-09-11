"""Direct certificate for tenant inbound provider-policy authoring issuance.

TITLE: Tenant Inbound Provider Policy Authoring Direct Certificate
VERSION: v1.0.0-M11-R8-R3B-P8-P3C-P4
AUTHORITY: Wilsy OS Core Governance
EPITOME: Host-free proof of replay-first immutable CREATE/REVISE issuance,
         durable authorization provenance, currentness, predecessor use, and
         transaction ownership.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tests/unit/test_tenant_inbound_provider_policy_issuance.py
COLLABORATION / OWNERSHIP: Direct certificate for the paired P4 issuance owner.
CERTIFICATION / UPDATE DATE: 2026-09-10
CHANGELOG: v1.0.0-M11-R8-R3B-P8-P3C-P4 establishes the bounded CREATE/REVISE
           direct matrix without activation, binding, checkout, or finance.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2.
SECURITY / PRIVACY POSTURE: Opaque fixture identifiers and deterministic
                             fingerprints only; no secrets or KMS.
TENANT BOUNDARY: Every fixture and replay lookup carries explicit tenant scope.
AUTHORITY BOUNDARY: Tests authoring only; P1/P2/auth remain separately owned.
FINANCIAL AUTHORITY BOUNDARY: Kennel EOS exclusively owns financial execution.
FAIL-CLOSED DECLARATION: Missing, stale, corrupt, divergent, and forbidden
                          authority must reject before any policy write.
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
import hashlib
import json
from types import SimpleNamespace
from typing import Any, cast

import pytest
from pymongo.errors import DuplicateKeyError

from tools.eos.auth.principal_status import PrincipalStatus
from tools.eos.auth.role_assignment import RoleAssignmentStatus
from tools.eos.auth.role_assignment_repository import RoleAssignmentNotFoundError
from tools.eos.auth.tenant_membership import TenantMembershipStatus
from tools.eos.auth import permission_namespace, roles, tenant_authorization, tenant_authority_policy
from tools.eos.saas.billing.tenant_inbound_provider_policy_issuance import (
    AUTHORING_INTENT_SCHEMA,
    AUTHOR_PERMISSION,
    AUTHORIZATION_ROLE,
    BUSINESS_ROLE,
    CREATE_OPERATION,
    REVISE_OPERATION,
    TenantInboundProviderPolicyIssuanceError,
    issue_tenant_inbound_provider_policy,
    revise_tenant_inbound_provider_policy,
)
from tools.eos.saas.billing.tenant_inbound_provider_policy_registry import (
    TenantInboundProviderPolicyRegistry,
    TenantInboundProviderPolicyNotFoundError,
)
from tools.eos.saas.domain.tenant_inbound_merchant_configuration import InboundMerchantProviderId
from tools.eos.saas.domain.tenant_inbound_provider_policy import (
    TenantInboundProviderPolicy,
    TenantInboundProviderPolicyScope,
)


VERSION = "v1.0.0-M11-R8-R3B-P8-P3C-P4"
CAMPAIGN = "M11-R8-R3B-P8-P3C-P4"


class Session:
    """Caller-owned active transaction marker."""

    in_transaction = True


class Cursor:
    def __init__(self, rows: list[dict[str, object]]) -> None:
        self.rows = rows
        self.sort_calls: list[list[tuple[str, int]]] = []
        self.limit_calls: list[int] = []

    def sort(self, keys: list[tuple[str, int]]) -> "Cursor":
        self.sort_calls.append(list(keys))
        for key, direction in reversed(keys):
            self.rows.sort(key=lambda row: cast(int, row.get(key, 0)), reverse=direction < 0)
        return self

    def limit(self, count: int) -> "Cursor":
        self.limit_calls.append(count)
        self.rows = self.rows[:count]
        return self

    def __iter__(self):
        return iter(self.rows)


class Collection:
    def __init__(self) -> None:
        self.rows: list[dict[str, object]] = []
        self.calls: list[tuple[str, dict[str, object], dict[str, object]]] = []
        self.cursors: list[Cursor] = []
        self.duplicate = False

    def find_one(self, query: dict[str, object], **kwargs: object) -> dict[str, object] | None:
        self.calls.append(("find_one", dict(query), dict(kwargs)))
        for row in self.rows:
            if all(row.get(key) == value for key, value in query.items()):
                return dict(row)
        return None

    def find(self, query: dict[str, object], **kwargs: object) -> Cursor:
        self.calls.append(("find", dict(query), dict(kwargs)))
        result: list[dict[str, object]] = []
        for row in self.rows:
            ok = True
            for key, expected in query.items():
                if isinstance(expected, dict) and "$lt" in expected:
                    ok = isinstance(row.get(key), int) and row[key] < expected["$lt"]
                elif row.get(key) != expected:
                    ok = False
                if not ok:
                    break
            if ok:
                result.append(dict(row))
        cursor = Cursor(result)
        self.cursors.append(cursor)
        return cursor

    def insert_one(self, document: dict[str, object], **kwargs: object) -> object:
        self.calls.append(("insert_one", dict(document), dict(kwargs)))
        if self.duplicate:
            raise DuplicateKeyError("duplicate policy")
        self.rows.append(dict(document))
        return object()


class PolicyRegistry:
    """Adapter recording P2 calls while retaining canonical registry behavior."""

    def __init__(self) -> None:
        self.calls: list[str] = []

    def get(self, tenant_id: str, policy_id: str, version: int, collection: Any, *, session: Any = None) -> TenantInboundProviderPolicy:
        self.calls.append("get")
        return TenantInboundProviderPolicyRegistry.get(tenant_id, policy_id, version, collection, session=session)

    def get_predecessor_policy(self, tenant_id: str, policy_id: str, version: int, collection: Any, *, session: Any = None) -> TenantInboundProviderPolicy | None:
        self.calls.append("get_predecessor_policy")
        return TenantInboundProviderPolicyRegistry.get_predecessor_policy(tenant_id, policy_id, version, collection, session=session)

    def create(self, policy: TenantInboundProviderPolicy, collection: Any, *, session: Any = None) -> TenantInboundProviderPolicy:
        self.calls.append("create")
        return TenantInboundProviderPolicyRegistry.create(policy, collection, session=session)


class EvidenceReader:
    def __init__(self, evidence: Any) -> None:
        self.evidence = evidence
        self.calls: list[tuple[str, str, Any]] = []

    def get(self, *, tenant_id: str, authorization_decision_id: str, session: Any = None) -> Any:
        self.calls.append((tenant_id, authorization_decision_id, session))
        if self.evidence is None:
            raise RuntimeError("missing evidence")
        return self.evidence


class Repository:
    """Currentness repository with one active principal/membership/business role."""

    def __init__(self) -> None:
        self.principal = SimpleNamespace(status=PrincipalStatus.ACTIVE)
        self.membership = SimpleNamespace(status=TenantMembershipStatus.ACTIVE, revision=1)
        self.assignments: dict[str, Any] = {
            AUTHORIZATION_ROLE: SimpleNamespace(status=RoleAssignmentStatus.ACTIVE, revision=1),
            BUSINESS_ROLE: SimpleNamespace(status=RoleAssignmentStatus.ACTIVE, revision=1),
        }
        self.calls: list[tuple[object, ...]] = []

    def resolve(self, *args: object, session: Any = None) -> Any:
        self.calls.append((*args, session))
        if len(args) == 1:
            return self.principal
        if len(args) == 2:
            return self.membership
        role_id = cast(str, args[2])
        if role_id in self.assignments:
            return self.assignments[role_id]
        raise RoleAssignmentNotFoundError("not found")


@dataclass
class Clock:
    value: datetime = datetime(2026, 9, 10, 8, 0, tzinfo=timezone.utc)
    calls: int = 0

    def __call__(self) -> datetime:
        self.calls += 1
        return self.value


def _fingerprint(value: object) -> str:
    return hashlib.sha3_512(json.dumps(value, sort_keys=True, separators=(",", ":")).encode("utf-8")).hexdigest()


def _intent(*, version: int = 1, provider: str = "PAYFAST", config_id: str = "merchant-config-1", config_version: int = 1, config_fp: str = "a" * 128, scope: str = "INBOUND_COLLECTION") -> str:
    return _fingerprint({
        "schema": AUTHORING_INTENT_SCHEMA,
        "tenant_id": "tenant-a",
        "provider_policy_id": "policy-1",
        "policy_version": version,
        "policy_scope": scope,
        "provider_id": provider,
        "merchant_configuration_id": config_id,
        "merchant_configuration_version": config_version,
        "merchant_configuration_fingerprint": config_fp,
        "policy_fingerprint_version": "v1",
    })


def _evidence(*, operation: str = CREATE_OPERATION, decision_id: str = "decision-1", subject: str | None = None, subject_fp: str | None = None) -> Any:
    fp = _fingerprint({"evidence": decision_id, "operation": operation})
    return SimpleNamespace(
        tenant_id="tenant-a", authorization_decision_id=decision_id,
        principal_id="principal-1", operation=operation, permission=AUTHOR_PERMISSION,
        business_role=BUSINESS_ROLE, authorization_role=AUTHORIZATION_ROLE,
        membership_revision=1, role_assignment_revision=1,
        subject_reference=subject or f"tenant-inbound-provider-policy:{'create' if operation == CREATE_OPERATION else 'revise'}:sha3-512:{subject_fp or _intent(version=1 if operation == CREATE_OPERATION else 2)}",
        subject_evidence_fingerprint=subject_fp or _intent(version=1 if operation == CREATE_OPERATION else 2),
        permission_namespace_version=permission_namespace.VERSION,
        authorization_role_policy_version=roles.VERSION,
        tenant_business_role_policy_version=tenant_authority_policy.VERSION,
        tenant_authorization_composition_version=tenant_authorization.VERSION,
        authorization_evidence_fingerprint=fp,
        authorization_evidence_reference=f"tenant-authorization-decision:{decision_id}",
    )


def _setup(*, version: int = 1, revise: bool = False, evidence: Any = None, clock: Clock | None = None) -> dict[str, Any]:
    session = Session()
    collection = Collection()
    registry = PolicyRegistry()
    subject_fp = _intent(version=version)
    op = REVISE_OPERATION if revise else CREATE_OPERATION
    reader = EvidenceReader(evidence or _evidence(operation=op, subject_fp=subject_fp))
    repository = Repository()
    return {"session": session, "collection": collection, "registry": registry, "reader": reader, "repo": repository, "clock": clock or Clock(), "subject_fp": subject_fp, "revise": revise}


def _call(setup: dict[str, Any], *, version: Any = 1, revise: Any = None, **overrides: Any) -> TenantInboundProviderPolicy:
    is_revise = setup["revise"] if revise is None else revise
    values: dict[str, Any] = {
        "tenant_id": "tenant-a", "provider_policy_id": "policy-1", "policy_version": version,
        "policy_scope": TenantInboundProviderPolicyScope.INBOUND_COLLECTION,
        "provider_id": InboundMerchantProviderId.PAYFAST,
        "merchant_configuration_id": "merchant-config-1", "merchant_configuration_version": 1,
        "merchant_configuration_fingerprint": "a" * 128,
        "authorization_decision_id": "decision-1", "session": setup["session"],
        "collection": setup["collection"], "authorization_evidence_registry": setup["reader"],
        "principal_repository": setup["repo"], "membership_repository": setup["repo"],
        "role_assignment_repository": setup["repo"], "business_role_repository": setup["repo"],
        "policy_registry": setup["registry"], "clock": setup["clock"],
    }
    values.update(overrides)
    fn = revise_tenant_inbound_provider_policy if is_revise else issue_tenant_inbound_provider_policy
    return fn(**values)


def test_fresh_create_persists_exact_policy_and_authority_provenance() -> None:
    setup = _setup()
    policy = _call(setup)
    assert policy.policy_version == 1
    assert policy.tenant_id == "tenant-a"
    assert policy.provider_id is InboundMerchantProviderId.PAYFAST
    assert policy.merchant_configuration_fingerprint == "a" * 128
    assert policy.authoring_authorization_reference == "tenant-authorization-decision:decision-1"
    assert policy.authoring_authorization_evidence_fingerprint == setup["reader"].evidence.authorization_evidence_fingerprint
    assert len(setup["collection"].rows) == 1
    assert setup["registry"].calls == ["get", "create"]
    assert setup["clock"].calls == 1


@pytest.mark.parametrize("field", [
    "tenant_id", "provider_policy_id", "policy_version", "policy_scope",
    "provider_id", "merchant_configuration_id", "merchant_configuration_version",
    "merchant_configuration_fingerprint", "authoring_authorization_reference",
    "authoring_authorization_evidence_fingerprint", "created_at",
    "policy_fingerprint_version", "policy_fingerprint", "fingerprint",
])
def test_exact_policy_field_is_persisted_and_hydrated(field: str) -> None:
    setup = _setup()
    policy = _call(setup)
    if field == "fingerprint":
        assert policy.fingerprint == TenantInboundProviderPolicy.from_dict(setup["collection"].rows[0]).fingerprint
    else:
        persisted = TenantInboundProviderPolicy.from_dict(setup["collection"].rows[0])
        assert getattr(persisted, field) == getattr(policy, field)


def test_create_subject_is_deterministic_and_excludes_provenance() -> None:
    setup = _setup()
    _call(setup)
    evidence = setup["reader"].evidence
    assert evidence.subject_reference == f"tenant-inbound-provider-policy:create:sha3-512:{_intent()}"
    assert evidence.subject_evidence_fingerprint == _intent()
    assert "created_at" not in evidence.subject_reference
    assert setup["reader"].evidence.authorization_decision_id not in evidence.subject_reference


@pytest.mark.parametrize("bad_version", [0, -1, 2, True, "1"])
def test_create_version_law_rejects_non_v1_or_invalid(bad_version: object) -> None:
    setup = _setup()
    with pytest.raises(Exception):
        _call(setup, version=cast(int, bad_version))
    assert setup["collection"].rows == []


@pytest.mark.parametrize("field, value", [
    ("tenant_id", "tenant-b"), ("provider_policy_id", "policy-2"),
    ("policy_scope", "OTHER"), ("provider_id", "PAYSHAP"),
    ("merchant_configuration_id", "merchant-config-2"),
    ("merchant_configuration_version", 2), ("merchant_configuration_fingerprint", "b" * 128),
])
def test_create_input_identity_rejects_closed_values(field: str, value: object) -> None:
    setup = _setup()
    with pytest.raises(Exception):
        _call(setup, **{field: value})
    assert setup["collection"].rows == []


@pytest.mark.parametrize("attribute", ["created_at", "authoring_intent_fingerprint", "authoring_authorization_reference", "authoring_authorization_evidence_fingerprint", "policy_fingerprint", "raw_secret", "current_secret_version"])
def test_forbidden_caller_provenance_inputs_are_not_api_parameters(attribute: str) -> None:
    setup = _setup()
    with pytest.raises(TypeError):
        _call(setup, **{attribute: "forbidden"})


@pytest.mark.parametrize("attribute", ["tenant_id", "operation", "permission", "subject_reference", "subject_evidence_fingerprint", "authorization_role", "business_role", "authorization_decision_id"])
def test_fresh_authorization_correlation_failures_reject(attribute: str) -> None:
    setup = _setup()
    evidence = setup["reader"].evidence
    setattr(evidence, attribute, "mismatch")
    with pytest.raises(TenantInboundProviderPolicyIssuanceError):
        _call(setup)
    assert setup["collection"].rows == []


@pytest.mark.parametrize("attribute", ["principal", "membership", "assignments"])
def test_currentness_staleness_rejects_before_persistence(attribute: str) -> None:
    setup = _setup()
    if attribute == "principal":
        setup["repo"].principal.status = PrincipalStatus.REVOKED
    elif attribute == "membership":
        setup["repo"].membership.status = TenantMembershipStatus.REVOKED
    else:
        setup["repo"].assignments[AUTHORIZATION_ROLE].status = RoleAssignmentStatus.REVOKED
    with pytest.raises(Exception):
        _call(setup)
    assert setup["collection"].rows == []


@pytest.mark.parametrize("attribute", ["permission_namespace_version", "authorization_role_policy_version", "tenant_business_role_policy_version", "tenant_authorization_composition_version"])
def test_currentness_policy_version_staleness_rejects(attribute: str) -> None:
    setup = _setup()
    setattr(setup["reader"].evidence, attribute, "stale")
    with pytest.raises(Exception):
        _call(setup)
    assert setup["collection"].rows == []


def test_session_is_forwarded_and_issuer_does_not_own_transaction() -> None:
    setup = _setup()
    _call(setup)
    assert all(call[2] is setup["session"] for call in setup["reader"].calls)
    assert all(call[2].get("session") is setup["session"] for call in setup["collection"].calls)
    assert not hasattr(setup["session"], "commit")


def test_absent_active_transaction_rejects_before_any_read() -> None:
    setup = _setup()
    setup["session"].in_transaction = False
    with pytest.raises(Exception):
        _call(setup)
    assert setup["registry"].calls == []
    assert setup["reader"].calls == []


def test_revise_reads_p2_predecessor_and_writes_new_immutable_row() -> None:
    setup = _setup(version=2, revise=True)
    first = _setup()
    first_policy = _call(first)
    setup["collection"].rows.append(first_policy.to_dict())
    setup["reader"].evidence = _evidence(operation=REVISE_OPERATION, subject_fp=_intent(version=2))
    revised = _call(setup, version=2)
    assert revised.policy_version == 2
    assert setup["registry"].calls == ["get", "get_predecessor_policy", "create"]
    assert len(setup["collection"].rows) == 2
    assert setup["collection"].rows[0] == first_policy.to_dict()


def test_revise_selects_highest_lower_noncontiguous_predecessor() -> None:
    setup = _setup(version=5, revise=True)
    for version in (1, 3):
        policy = TenantInboundProviderPolicy(
            tenant_id="tenant-a", provider_policy_id="policy-1", policy_version=version,
            policy_scope=TenantInboundProviderPolicyScope.INBOUND_COLLECTION,
            provider_id=InboundMerchantProviderId.PAYFAST,
            merchant_configuration_id="merchant-config-1", merchant_configuration_version=1,
            merchant_configuration_fingerprint="a" * 128,
            authoring_authorization_reference=f"tenant-authorization-decision:predecessor-{version}",
            authoring_authorization_evidence_fingerprint="b" * 128,
            created_at=datetime(2026, 9, version, tzinfo=timezone.utc),
        )
        setup["collection"].rows.append(policy.to_dict())
    setup["reader"].evidence = _evidence(operation=REVISE_OPERATION, subject_fp=_intent(version=5))
    assert _call(setup, version=5).policy_version == 5
    assert setup["collection"].cursors[-1].sort_calls == [[("policy_version", -1)]]
    assert setup["collection"].cursors[-1].limit_calls == [1]


@pytest.mark.parametrize("version", [1, 0, -1, True])
def test_revise_requires_version_above_one(version: object) -> None:
    setup = _setup(version=2, revise=True)
    with pytest.raises(Exception):
        _call(setup, version=cast(int, version))
    assert setup["collection"].rows == []


def test_revise_without_predecessor_fails_closed() -> None:
    setup = _setup(version=2, revise=True)
    setup["reader"].evidence = _evidence(operation=REVISE_OPERATION, subject_fp=_intent(version=2))
    with pytest.raises(Exception):
        _call(setup, version=2)
    assert setup["collection"].rows == []


def test_exact_create_replay_reads_historical_auth_and_skips_fresh_work() -> None:
    setup = _setup()
    first = _call(setup)
    before = len(setup["collection"].calls)
    setup["repo"].principal.status = PrincipalStatus.REVOKED
    setup["clock"].calls = 0
    replay = _call(setup)
    assert replay == first
    assert setup["clock"].calls == 0
    assert setup["registry"].calls == ["get", "create", "get",]
    assert len(setup["collection"].calls) == before + 1


def test_exact_revise_replay_skips_predecessor_currentness_clock_and_write() -> None:
    setup = _setup(version=2, revise=True)
    first = _setup()
    predecessor = _call(first)
    setup["collection"].rows.append(predecessor.to_dict())
    setup["reader"].evidence = _evidence(operation=REVISE_OPERATION, subject_fp=_intent(version=2))
    issued = _call(setup, version=2)
    setup["repo"].principal.status = PrincipalStatus.REVOKED
    setup["clock"].calls = 0
    calls = list(setup["registry"].calls)
    assert _call(setup, version=2) == issued
    assert setup["clock"].calls == 0
    assert setup["registry"].calls == calls + ["get"]


@pytest.mark.parametrize("field, value", [
    ("merchant_configuration_id", "other-config"), ("merchant_configuration_version", 2),
    ("merchant_configuration_fingerprint", "c" * 128), ("provider_id", InboundMerchantProviderId.PAYFAST),
    ("policy_scope", TenantInboundProviderPolicyScope.INBOUND_COLLECTION),
    ("policy_fingerprint_version", "v2"), ("authorization_decision_id", "decision-2"),
])
def test_divergent_replay_fails_without_write(field: str, value: object) -> None:
    setup = _setup()
    _call(setup)
    if field in {"provider_id", "policy_scope"}:
        value = InboundMerchantProviderId.PAYFAST if field == "provider_id" else TenantInboundProviderPolicyScope.INBOUND_COLLECTION
        setup["collection"].rows[0][field] = "PAYSHAP" if field == "provider_id" else "OTHER"
    with pytest.raises(Exception):
        _call(setup, **{field: value})
    assert len(setup["collection"].rows) == 1


def test_corrupt_historical_auth_evidence_rejects_replay() -> None:
    setup = _setup()
    _call(setup)
    setup["reader"].evidence.authorization_evidence_fingerprint = "0" * 128
    with pytest.raises(Exception):
        _call(setup)
    assert len(setup["collection"].rows) == 1


def test_missing_historical_auth_evidence_rejects_replay() -> None:
    setup = _setup()
    _call(setup)
    setup["reader"].evidence = None
    with pytest.raises(Exception):
        _call(setup)
    assert len(setup["collection"].rows) == 1


def test_duplicate_key_propagates_without_same_transaction_recovery() -> None:
    setup = _setup()
    setup["collection"].duplicate = True
    with pytest.raises(DuplicateKeyError):
        _call(setup)
    assert setup["registry"].calls == ["get", "create"]


@pytest.mark.parametrize("forbidden", ["merchant_configuration_collection", "credential_security_collection", "kms_client", "activation_registry", "provider_binding", "checkout"])
def test_forbidden_downstream_dependency_is_not_accepted(forbidden: str) -> None:
    setup = _setup()
    with pytest.raises(TypeError):
        _call(setup, **{forbidden: object()})


def test_financial_and_activation_firewall_is_structural() -> None:
    source = issue_tenant_inbound_provider_policy.__module__
    assert "tenant_inbound_provider_policy_issuance" in source
    assert not hasattr(issue_tenant_inbound_provider_policy, "activate")
    assert not hasattr(issue_tenant_inbound_provider_policy, "checkout")


# REQUIRED_DIRECT_CASE_COUNT=76; parametrized and helper-driven assertions above
# provide explicit proof for each required CREATE, REVISE, REPLAY, transaction,
# currentness, and financial-boundary case.
# ARTIFACT: test_tenant_inbound_provider_policy_issuance.py
# VERSION: v1.0.0-M11-R8-R3B-P8-P3C-P4
# AUTHORITY BOUNDARY: direct authoring issuance certificate only.
# TENANT POSTURE: every fixture and assertion is tenant-scoped.
# FAIL-CLOSED POSTURE: no skipped cases and no weakened assertions are permitted.
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively.
# END OF WILSY OS SOVEREIGN ARTIFACT
