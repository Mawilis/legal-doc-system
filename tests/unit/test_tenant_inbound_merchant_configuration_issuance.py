"""Wilsy OS certificate for authorized tenant merchant-configuration registration.

TITLE: Tenant Inbound Merchant Configuration Issuance Certificate
VERSION: v1.1.0-M11-R8-R3B-P8-P3B-I2-I1-R2-R1-AUTHORIZED-MERCHANT-CONFIGURATION-LIFECYCLE-CERT
AUTHORITY: Wilsy OS Core Governance; direct unit evidence for the SaaS registration owner.
EPITOME: Prove replay-first, provenance-bound, current-authority registration without Mongo.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tests/unit/test_tenant_inbound_merchant_configuration_issuance.py
COLLABORATION / OWNERSHIP: Test owner certifies the paired issuance owner; frozen P8-P2/P8-P3A owners remain untouched.
CERTIFICATION / UPDATE DATE: 2026-09-09
CHANGELOG: v1.1.0-M11-R8-R3B-P8-P3B-I2-I1-R2-R1-AUTHORIZED-MERCHANT-CONFIGURATION-LIFECYCLE-CERT replaces static transaction-ownership checks with runtime caller-session sentinels for cases 65-69; the complete 78-case matrix remains certified.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2.
SECURITY / PRIVACY POSTURE: Synthetic opaque identifiers only; no secrets, network, Mongo, or provider adapter.
TENANT BOUNDARY: Every synthetic lookup and persisted evidence row is explicitly tenant scoped.
AUTHORITY BOUNDARY: Tests composition only; they never create generic authority or lifecycle authority.
FINANCIAL AUTHORITY BOUNDARY: No payment, invoice, receivable, execution, or settlement behavior.
FAIL-CLOSED DECLARATION: Any replay, provenance, currentness, schema, transaction, or input divergence is rejected.
"""
from __future__ import annotations

from copy import deepcopy
from dataclasses import dataclass, replace
from datetime import datetime, timezone
import ast
import inspect
from pathlib import Path
from types import SimpleNamespace
from typing import Any, cast

import pytest
from pymongo.errors import DuplicateKeyError

from tools.eos.auth import permission_namespace, roles, tenant_authorization, tenant_authority_policy
from tools.eos.auth.principal_authority import PrincipalAuthority
from tools.eos.auth.principal_status import PrincipalStatus
from tools.eos.auth.role_assignment import RoleAssignmentStatus
from tools.eos.auth.role_assignment_repository import RoleAssignmentNotFoundError
from tools.eos.auth.tenant_authorization_decision_evidence import TenantAuthorizationDecisionEvidence
from tools.eos.auth.tenant_authorization_decision_evidence_registry import TenantAuthorizationDecisionEvidenceRegistry
from tools.eos.auth.tenant_business_role import TenantBusinessRoleStatus
from tools.eos.auth.tenant_membership import TenantMembershipAuthority, TenantMembershipStatus
from tools.eos.saas.billing.tenant_inbound_merchant_configuration_issuance import (
    REGISTER_AUTHORIZATION_ROLE,
    REGISTER_BUSINESS_ROLE,
    REGISTER_OPERATION,
    REGISTER_PERMISSION,
    REGISTER_INTENT_FIELDS,
    TenantInboundMerchantConfigurationIssuanceError,
    VERSION,
    canonical_registration_intent_fingerprint,
    register_tenant_inbound_merchant_configuration,
    transition_tenant_inbound_merchant_configuration,
    compromise_tenant_inbound_merchant_configuration,
    remediate_tenant_inbound_merchant_configuration,
    LIFECYCLE_OPERATION, LIFECYCLE_PERMISSION, LIFECYCLE_AUTHORIZATION_ROLE, LIFECYCLE_BUSINESS_ROLE,
    COMPROMISE_OPERATION, COMPROMISE_PERMISSION, COMPROMISE_AUTHORIZATION_ROLE, COMPROMISE_BUSINESS_ROLE,
    REMEDIATION_OPERATION, REMEDIATION_PERMISSION, REMEDIATION_AUTHORIZATION_ROLE, REMEDIATION_BUSINESS_ROLE,
    registration_subject_reference,
    _lifecycle_payload,
    _lifecycle_fingerprint,
    _lifecycle_subject,
)
from tools.eos.saas.billing.tenant_inbound_merchant_configuration_registry import TenantInboundMerchantConfigurationRegistry
from tools.eos.saas.domain.tenant_inbound_merchant_configuration import InboundMerchantProviderId
from tools.eos.saas.billing.tenant_inbound_merchant_configuration_registry import EnablementState
import tools.eos.saas.billing.tenant_inbound_merchant_configuration_issuance as issuance_module


class Session:
    """Minimal caller-owned active transaction marker."""

    in_transaction = True


class TransactionSessionSpy:
    """Caller-owned transaction sentinel; issuer-owned transaction calls fail immediately."""

    def __init__(self, *, active: bool = True) -> None:
        self.in_transaction = active
        self.start_calls = 0
        self.commit_calls = 0
        self.abort_calls = 0

    def start_transaction(self, *args: object, **kwargs: object) -> None:
        self.start_calls += 1
        raise AssertionError("issuer attempted to start caller transaction")

    def commit_transaction(self, *args: object, **kwargs: object) -> None:
        self.commit_calls += 1
        raise AssertionError("issuer attempted to commit caller transaction")

    def abort_transaction(self, *args: object, **kwargs: object) -> None:
        self.abort_calls += 1
        raise AssertionError("issuer attempted to abort caller transaction")


class FakeCollection:
    """Session-recording collection double with exact dotted-key matching."""

    def __init__(self) -> None:
        self.rows: list[dict[str, object]] = []
        self.calls: list[tuple[str, object, object]] = []

    @staticmethod
    def _value(row: dict[str, object], dotted: str) -> object:
        def walk(value: object, parts: list[str]) -> object:
            if not parts:
                return value
            if isinstance(value, list):
                return [walk(item, parts) for item in value]
            if not isinstance(value, dict):
                return None
            return walk(value.get(parts[0]), parts[1:])
        return walk(row, dotted.split("."))

    def find_one(self, query: dict[str, object], *, session: object = None) -> dict[str, object] | None:
        self.calls.append(("find_one", deepcopy(query), session))
        for row in self.rows:
            def contains(value: object, expected: object) -> bool:
                if value == expected:
                    return True
                return isinstance(value, list) and any(contains(item, expected) for item in value)
            if all(contains(self._value(row, key), expected) for key, expected in query.items()):
                return deepcopy(row)
        return None

    def insert_one(self, document: dict[str, object], *, session: object = None) -> object:
        self.calls.append(("insert_one", deepcopy(document), session))
        self.rows.append(deepcopy(document))
        return object()

    def update_one(self, query: dict[str, object], update: dict[str, object], *, session: object = None) -> object:
        self.calls.append(("update_one", deepcopy(query), session))
        for row in self.rows:
            if all(self._value(row, key) == expected or (isinstance(self._value(row, key), list) and any(item == expected for item in cast(list[object], self._value(row, key)))) for key, expected in query.items()):
                for key, value in cast(dict[str, object], update.get("$set", {})).items():
                    target = row
                    parts = key.split(".")
                    for part in parts[:-1]:
                        target = cast(dict[str, object], target[part])
                    target[parts[-1]] = deepcopy(value)
                pushed = update.get("$push", {})
                for key, value in cast(dict[str, object], pushed).items():
                    cast(list[object], row[key]).append(deepcopy(value))
                return type("Result", (), {"matched_count": 1})()
        return type("Result", (), {"matched_count": 0})()


@dataclass(frozen=True)
class _CurrentPrincipal:
    principal_id: str
    status: PrincipalStatus = PrincipalStatus.ACTIVE
    revision: int = 1


@dataclass(frozen=True)
class _CurrentMembership:
    principal_id: str
    tenant_id: str
    status: TenantMembershipStatus = TenantMembershipStatus.ACTIVE
    revision: int = 1


@dataclass(frozen=True)
class _AuthAssignment:
    status: RoleAssignmentStatus = RoleAssignmentStatus.ACTIVE
    revision: int = 1


@dataclass(frozen=True)
class _BusinessAssignment:
    status: TenantBusinessRoleStatus = TenantBusinessRoleStatus.ACTIVE
    revision: int = 1


class CurrentRepositories:
    """Canonical-shaped currentness repositories that retain every session."""

    def __init__(self, *, membership_revision: int = 1, assignment_status: RoleAssignmentStatus = RoleAssignmentStatus.ACTIVE, business_role: str = REGISTER_BUSINESS_ROLE) -> None:
        self.principal_calls: list[object] = []
        self.membership_calls: list[object] = []
        self.assignment_calls: list[object] = []
        self.assignment_role_ids: list[str] = []
        self.business_calls: list[object] = []
        self.membership_revision = membership_revision
        self.assignment_status = assignment_status
        self.business_role = business_role

    def principal(self, principal_id: str, *, session: object = None) -> _CurrentPrincipal:
        self.principal_calls.append(session)
        return _CurrentPrincipal(principal_id)

    def membership(self, principal_id: str, tenant_id: str, *, session: object = None) -> _CurrentMembership:
        self.membership_calls.append(session)
        return _CurrentMembership(principal_id, tenant_id, revision=self.membership_revision)

    def assignment(self, principal_id: str, tenant_id: str, role_id: str, *, session: object = None) -> object:
        self.assignment_calls.append(session)
        self.assignment_role_ids.append(role_id)
        if role_id in {REGISTER_AUTHORIZATION_ROLE, LIFECYCLE_AUTHORIZATION_ROLE, COMPROMISE_AUTHORIZATION_ROLE, REMEDIATION_AUTHORIZATION_ROLE}:
            return _AuthAssignment(self.assignment_status, 1)
        if role_id == self.business_role:
            self.business_calls.append(session)
            return _BusinessAssignment()
        raise RoleAssignmentNotFoundError("ABSENT_ROLE")


class PrincipalRepository:
    def __init__(self, current: CurrentRepositories) -> None:
        self.current = current

    def resolve(self, principal_id: str, *, session: object = None) -> object:
        return self.current.principal(principal_id, session=session)


class MembershipRepository:
    def __init__(self, current: CurrentRepositories) -> None:
        self.current = current

    def resolve(self, principal_id: str, tenant_id: str, *, session: object = None) -> object:
        return self.current.membership(principal_id, tenant_id, session=session)


class AssignmentRepository:
    def __init__(self, current: CurrentRepositories) -> None:
        self.current = current

    def resolve(self, principal_id: str, tenant_id: str, role_id: str, *, session: object = None) -> object:
        return self.current.assignment(principal_id, tenant_id, role_id, session=session)


class CountingClock:
    def __init__(self, value: datetime) -> None:
        self.value = value
        self.calls = 0

    def __call__(self) -> datetime:
        self.calls += 1
        return self.value


def _intent(*, account: str = "merchant-account-1", options: dict[str, str] | None = None) -> dict[str, Any]:
    return {
        "tenant_id": "tenant-a",
        "provider_id": InboundMerchantProviderId.PAYFAST,
        "merchant_account_id": account,
        "merchant_configuration_id": "merchant-config-1",
        "merchant_configuration_version": 1,
        "non_secret_provider_options": {"currency": "ZAR"} if options is None else options,
        "credential_secret_reference": "vault://tenant-a/payfast/current",
        "register_idempotency_key": "register-1",
    }


def _evidence(intent: dict[str, Any], *, decision_id: str = "decision-1", operation: str = REGISTER_OPERATION, permission: str = REGISTER_PERMISSION, subject_reference: str | None = None, subject_fingerprint: str | None = None) -> TenantAuthorizationDecisionEvidence:
    fingerprint = canonical_registration_intent_fingerprint(**intent)
    return TenantAuthorizationDecisionEvidence(
        tenant_id="tenant-a",
        authorization_decision_id=decision_id,
        principal_id="principal-1",
        operation=operation,
        permission=permission,
        business_role=REGISTER_BUSINESS_ROLE,
        authorization_role=REGISTER_AUTHORIZATION_ROLE,
        membership_revision=1,
        role_assignment_revision=1,
        subject_reference=registration_subject_reference(fingerprint) if subject_reference is None else subject_reference,
        subject_evidence_fingerprint=fingerprint if subject_fingerprint is None else subject_fingerprint,
        permission_namespace_version=permission_namespace.VERSION,
        authorization_role_policy_version=roles.VERSION,
        tenant_business_role_policy_version=tenant_authority_policy.VERSION,
        tenant_authorization_composition_version=tenant_authorization.VERSION,
        idempotency_key="auth-idem-1",
        authorized_at=datetime(2026, 9, 9, 8, 0, tzinfo=timezone.utc),
    )


def _setup(*, evidence: TenantAuthorizationDecisionEvidence | None = None, current: CurrentRepositories | None = None) -> dict[str, Any]:
    intent = _intent()
    current = CurrentRepositories() if current is None else current
    session = Session()
    config_collection = FakeCollection()
    evidence_collection = FakeCollection()
    evidence = _evidence(intent) if evidence is None else evidence
    evidence_collection.rows.append(evidence.to_persisted())
    principal = PrincipalRepository(current)
    membership = MembershipRepository(current)
    assignment = AssignmentRepository(current)
    return {
        "intent": intent,
        "session": session,
        "configuration_collection": config_collection,
        "authorization_evidence_collection": evidence_collection,
        "authorization_evidence_registry": TenantAuthorizationDecisionEvidenceRegistry(cast(Any, evidence_collection), principal_repository=principal, membership_repository=membership, role_assignment_repository=assignment, business_role_repository=assignment),
        "principal_repository": principal,
        "membership_repository": membership,
        "role_assignment_repository": assignment,
        "business_role_repository": assignment,
        "current": current,
        "config_collection": config_collection,
        "evidence_collection": evidence_collection,
    }


def _register(setup: dict[str, Any], *, clock: CountingClock | None = None, **changes: Any) -> Any:
    intent = dict(setup["intent"])
    decision_id = changes.pop("authorization_decision_id", "decision-1")
    intent.update(changes)
    kwargs = dict(intent)
    kwargs.update(
        authorization_decision_id=decision_id,
        session=setup["session"],
        configuration_collection=setup["configuration_collection"],
        authorization_evidence_collection=setup["authorization_evidence_collection"],
        authorization_evidence_registry=setup["authorization_evidence_registry"],
        principal_repository=setup["principal_repository"],
        membership_repository=setup["membership_repository"],
        role_assignment_repository=setup["role_assignment_repository"],
        business_role_repository=setup["business_role_repository"],
        configuration_registry=changes.pop("configuration_registry", TenantInboundMerchantConfigurationRegistry),
        clock=clock,
    )
    return register_tenant_inbound_merchant_configuration(**kwargs)


def _lifecycle_evidence(setup: dict[str, Any], record: Any, *, operation: str, permission: str, business_role: str, authorization_role: str, prior: EnablementState, target: EnablementState, key: str, decision_id: str) -> TenantAuthorizationDecisionEvidence:
    payload = _lifecycle_payload(tenant_id="tenant-a", merchant_configuration_id="merchant-config-1", merchant_configuration_version=1, configuration_fingerprint=record.configuration.fingerprint, expected_prior_lifecycle_revision=record.revision, expected_prior_state=prior, target_state=target, reason_reference="security-review", lifecycle_idempotency_key=key)
    fingerprint = _lifecycle_fingerprint(payload)
    return TenantAuthorizationDecisionEvidence(tenant_id="tenant-a", authorization_decision_id=decision_id, principal_id="principal-1", operation=operation, permission=permission, business_role=business_role, authorization_role=authorization_role, membership_revision=1, role_assignment_revision=1, subject_reference=_lifecycle_subject("lifecycle-transition" if operation == LIFECYCLE_OPERATION else "compromise" if operation == COMPROMISE_OPERATION else "remediate", fingerprint), subject_evidence_fingerprint=fingerprint, permission_namespace_version=permission_namespace.VERSION, authorization_role_policy_version=roles.VERSION, tenant_business_role_policy_version=tenant_authority_policy.VERSION, tenant_authorization_composition_version=tenant_authorization.VERSION, idempotency_key=f"auth-{key}", authorized_at=datetime(2026, 9, 9, 8, 0, tzinfo=timezone.utc))


class _LifecycleRegistry:
    """Deterministic registry spy exposing lookup, CAS, and append counts."""

    def __init__(self, *, state: EnablementState = EnablementState.DISABLED, revision: int = 0) -> None:
        self.record = SimpleNamespace(configuration=SimpleNamespace(tenant_id="tenant-a", merchant_configuration_id="merchant-config-1", merchant_configuration_version=1, fingerprint="f" * 128), lifecycle_state=state, lifecycle_revision=revision, state=state, revision=revision)
        self.events: dict[str, tuple[Any, Any]] = {}
        self.transition_calls: list[tuple[Any, ...]] = []
        self.transition_sessions: list[object] = []
        self.lookup_sessions: list[object] = []
        self.lookup_calls = 0
        self.failure: Exception | None = None

    def get_lifecycle_event_by_idempotency_key(self, tenant_id: str, key: str, collection: object, *, session: object = None) -> tuple[Any, Any] | None:
        self.lookup_calls += 1
        self.lookup_sessions.append(session)
        event = self.events.get(key)
        if event is None or getattr(event[1], "tenant_id", None) != tenant_id:
            return None
        return event

    def get(self, tenant_id: str, configuration_id: str, version: int, collection: object, *, session: object = None) -> Any:
        self.lookup_sessions.append(session)
        if tenant_id != self.record.configuration.tenant_id or configuration_id != self.record.configuration.merchant_configuration_id or version != self.record.configuration.merchant_configuration_version:
            return None
        return self.record

    def transition_enablement(self, *args: Any, **kwargs: Any) -> Any:
        self.transition_calls.append(args)
        self.transition_sessions.append(kwargs.get("session"))
        if self.failure is not None:
            raise self.failure
        self.record.lifecycle_state = args[5]
        self.record.state = args[5]
        self.record.lifecycle_revision = args[3] + 1
        self.record.revision = args[3] + 1
        event = SimpleNamespace(tenant_id="tenant-a", merchant_configuration_id="merchant-config-1", merchant_configuration_version=1, configuration_fingerprint=self.record.configuration.fingerprint, prior_revision=args[3], prior_state=args[4], new_state=args[5], reason_reference=args[8], authorization_reference=args[9], authorization_evidence_fingerprint=args[10], lifecycle_idempotency_key=args[11])
        self.events[args[11]] = (self.record, event)
        return self.record


class _EvidenceReader:
    def __init__(self, evidence: Any) -> None:
        self.evidence = evidence
        self.calls = 0
        self.sessions: list[object] = []

    def get(self, *, tenant_id: str, authorization_decision_id: str, session: object = None) -> Any:
        self.calls += 1
        self.sessions.append(session)
        return self.evidence


def _synthetic_setup(*, state: EnablementState = EnablementState.DISABLED, revision: int = 0, operation: str = LIFECYCLE_OPERATION, permission: str = LIFECYCLE_PERMISSION, business_role: str = LIFECYCLE_BUSINESS_ROLE, authorization_role: str = LIFECYCLE_AUTHORIZATION_ROLE, target: EnablementState = EnablementState.ENABLED, key: str = "key-1", decision: str = "decision-1", current: CurrentRepositories | None = None) -> dict[str, Any]:
    setup = _setup(current=current)
    registry = _LifecycleRegistry(state=state, revision=revision)
    evidence = _lifecycle_evidence(setup, registry.record, operation=operation, permission=permission, business_role=business_role, authorization_role=authorization_role, prior=state, target=target, key=key, decision_id=decision)
    setup["current"].business_role = business_role
    setup["authorization_evidence_registry"] = _EvidenceReader(evidence)
    setup["registry"] = registry
    setup["decision"] = decision
    setup["key"] = key
    setup["evidence"] = evidence
    return setup


def _transition_kwargs(setup: dict[str, Any], *, prior: EnablementState, target: EnablementState, key: str | None = None, decision: str | None = None, operation: str = LIFECYCLE_OPERATION, permission: str = LIFECYCLE_PERMISSION) -> dict[str, Any]:
    record = setup["registry"].record
    return {"tenant_id": "tenant-a", "merchant_configuration_id": "merchant-config-1", "merchant_configuration_version": 1, "expected_configuration_fingerprint": record.configuration.fingerprint, "expected_lifecycle_revision": record.revision, "expected_prior_state": prior, "target_state": target, "reason_reference": "security-review", "lifecycle_idempotency_key": setup["key"] if key is None else key, "authorization_decision_id": setup["decision"] if decision is None else decision, "session": setup["session"], "configuration_collection": setup["configuration_collection"], "authorization_evidence_collection": setup["authorization_evidence_collection"], "authorization_evidence_registry": setup["authorization_evidence_registry"], "principal_repository": setup["principal_repository"], "membership_repository": setup["membership_repository"], "role_assignment_repository": setup["role_assignment_repository"], "business_role_repository": setup["business_role_repository"], "configuration_registry": setup["registry"], "operation": operation, "permission": permission}


def test_fresh_registration_is_disabled_and_forwards_one_session() -> None:
    setup = _setup()
    clock = CountingClock(datetime(2026, 9, 9, 9, 0, tzinfo=timezone.utc))
    result = _register(setup, clock=clock)
    assert result.state is EnablementState.DISABLED
    assert result.revision == 0
    assert result.configuration.created_at == clock.value
    assert clock.calls == 1
    assert len(setup["config_collection"].rows) == 1
    assert all(call[2] is setup["session"] for call in setup["config_collection"].calls)
    current = setup["current"]
    assert current.principal_calls == [setup["session"]]
    assert current.membership_calls == [setup["session"]]
    assert current.business_calls
    assert all(value is setup["session"] for value in current.assignment_calls)


def test_exact_replay_reads_evidence_but_skips_currentness_clock_and_create() -> None:
    setup = _setup()
    first = _register(setup, clock=CountingClock(datetime(2026, 9, 9, 9, 0, tzinfo=timezone.utc)))
    current = setup["current"]
    current.principal = lambda *_args, **_kwargs: (_ for _ in ()).throw(AssertionError("reauthorized"))
    replay_clock = CountingClock(datetime(2027, 1, 1, tzinfo=timezone.utc))
    second = _register(setup, clock=replay_clock)
    assert second == first
    assert replay_clock.calls == 0
    assert len(setup["config_collection"].rows) == 1
    assert setup["config_collection"].calls[0][0] == "find_one"


def test_replay_preserves_existing_lifecycle_state_and_revision() -> None:
    setup = _setup()
    first = _register(setup, clock=CountingClock(datetime(2026, 9, 9, 9, 0, tzinfo=timezone.utc)))
    row = setup["config_collection"].rows[0]
    row["lifecycle"]["state"] = "ENABLED"  # type: ignore[index]
    row["lifecycle"]["revision"] = 3  # type: ignore[index]
    row["lifecycle_history"] = row["lifecycle_history"] + [row["lifecycle_history"][0]]  # type: ignore[index]
    # Deliberately leave strict history invalid: replay must not reset or repair durable state.
    with pytest.raises(Exception):
        _register(setup, clock=CountingClock(datetime(2027, 1, 1, tzinfo=timezone.utc)))
    assert first.revision == 0


def test_divergent_intent_and_decision_fail_closed_before_fresh_work() -> None:
    setup = _setup()
    _register(setup, clock=CountingClock(datetime(2026, 9, 9, 9, 0, tzinfo=timezone.utc)))
    with pytest.raises(TenantInboundMerchantConfigurationIssuanceError):
        _register(setup, merchant_account_id="other-account", clock=CountingClock(datetime(2027, 1, 1, tzinfo=timezone.utc)))
    with pytest.raises(TenantInboundMerchantConfigurationIssuanceError):
        _register(setup, authorization_decision_id="decision-2", clock=CountingClock(datetime(2027, 1, 1, tzinfo=timezone.utc)))


def test_legacy_null_provenance_replay_fails_closed_without_backfill() -> None:
    setup = _setup()
    _register(setup, clock=CountingClock(datetime(2026, 9, 9, 9, 0, tzinfo=timezone.utc)))
    row = setup["config_collection"].rows[0]
    del row["create_authorization_reference"]
    del row["create_authorization_evidence_fingerprint"]
    with pytest.raises(Exception):
        _register(setup, clock=CountingClock(datetime(2027, 1, 1, tzinfo=timezone.utc)))
    assert "create_authorization_reference" not in row


@pytest.mark.parametrize("field,value", [("operation", "wrong_operation"), ("permission", "wrong:permission"), ("subject_reference", "wrong-subject"), ("subject_fingerprint", "0" * 128)])
def test_fresh_evidence_correlation_is_exact(field: str, value: str) -> None:
    intent = _intent()
    evidence = _evidence(intent, **{field: value})
    setup = _setup(evidence=evidence)
    with pytest.raises(TenantInboundMerchantConfigurationIssuanceError):
        _register(setup, clock=CountingClock(datetime(2026, 9, 9, 9, 0, tzinfo=timezone.utc)))
    assert setup["config_collection"].rows == []


def test_stale_membership_and_revoked_role_fail_before_clock_or_create() -> None:
    stale = _setup(current=CurrentRepositories(membership_revision=2))
    stale_clock = CountingClock(datetime(2026, 9, 9, 9, 0, tzinfo=timezone.utc))
    with pytest.raises(TenantInboundMerchantConfigurationIssuanceError):
        _register(stale, clock=stale_clock)
    assert stale_clock.calls == 0
    revoked = _setup(current=CurrentRepositories(assignment_status=RoleAssignmentStatus.REVOKED))
    with pytest.raises(TenantInboundMerchantConfigurationIssuanceError):
        _register(revoked, clock=CountingClock(datetime(2026, 9, 9, 9, 0, tzinfo=timezone.utc)))
    assert revoked["config_collection"].rows == []


def test_no_active_transaction_is_rejected_before_lookup() -> None:
    setup = _setup()
    setup["session"].in_transaction = False
    with pytest.raises(TenantInboundMerchantConfigurationIssuanceError):
        _register(setup)
    assert setup["config_collection"].calls == []


def test_duplicate_key_propagates_without_same_transaction_recovery() -> None:
    setup = _setup()

    class DuplicateRegistry:
        def __init__(self) -> None:
            self.create_calls = 0

        def get_by_idempotency_key(self, *_args: object, **_kwargs: object) -> None:
            return None

        def create(self, *_args: object, **_kwargs: object) -> None:
            self.create_calls += 1
            raise DuplicateKeyError("RACE")

    registry = DuplicateRegistry()
    with pytest.raises(DuplicateKeyError):
        _register(setup, configuration_registry=registry)
    assert registry.create_calls == 1


def test_input_boundary_and_intent_hash_are_closed() -> None:
    signature = inspect.signature(register_tenant_inbound_merchant_configuration)
    names = set(signature.parameters)
    assert {"created_at", "configuration_fingerprint", "initial_enablement_state", "authorization_evidence", "authorization_evidence_fingerprint", "principal_id", "raw_secret", "secret_version"}.isdisjoint(names)
    assert REGISTER_INTENT_FIELDS == ("tenant_id", "provider_id", "merchant_account_id", "merchant_configuration_id", "merchant_configuration_version", "non_secret_provider_options", "credential_secret_reference", "register_idempotency_key")
    intent = _intent(options={"currency": "ZAR", "mode": "live"})
    fingerprint = canonical_registration_intent_fingerprint(**intent)
    assert len(fingerprint) == 128 and fingerprint == fingerprint.lower()
    assert "created_at" not in intent and "lifecycle_state" not in intent
    assert registration_subject_reference(fingerprint).startswith("tenant-inbound-merchant-configuration:register:sha3-512:")


def test_provider_secret_and_transaction_boundaries_are_explicit() -> None:
    setup = _setup()
    with pytest.raises(TenantInboundMerchantConfigurationIssuanceError):
        _register(setup, provider_id="PAYSHAP")
    with pytest.raises(TenantInboundMerchantConfigurationIssuanceError):
        _register(setup, non_secret_provider_options={"api_key": "raw"})
    source = Path("tools/eos/saas/billing/tenant_inbound_merchant_configuration_issuance.py").read_text()
    tree = ast.parse(source)
    imported = " ".join(
        node.module or ""
        for node in ast.walk(tree)
        if isinstance(node, ast.ImportFrom)
    ).lower()
    for forbidden in ("billing_registry", "connect_db", "payfast", "payshap", "clientinvoice", "commercial_receivable", "kms", "checkout"):
        assert forbidden not in imported
    assert "tenant_inbound_merchant_configuration_registry" in imported


def test_lifecycle_compromise_and_remediation_are_separate_authorities() -> None:
    setup = _setup()
    record = _register(setup, clock=CountingClock(datetime(2026, 9, 9, 9, 0, tzinfo=timezone.utc)))
    ordinary_key = "life-1"
    ordinary_decision = "decision-life"
    setup["current"].business_role = LIFECYCLE_BUSINESS_ROLE
    setup["evidence_collection"].rows.append(_lifecycle_evidence(setup, record, operation=LIFECYCLE_OPERATION, permission=LIFECYCLE_PERMISSION, business_role=LIFECYCLE_BUSINESS_ROLE, authorization_role=LIFECYCLE_AUTHORIZATION_ROLE, prior=EnablementState.DISABLED, target=EnablementState.ENABLED, key=ordinary_key, decision_id=ordinary_decision).to_persisted())
    record = transition_tenant_inbound_merchant_configuration("tenant-a", "merchant-config-1", 1, record.configuration.fingerprint, 0, EnablementState.DISABLED, EnablementState.ENABLED, "security-review", ordinary_key, ordinary_decision, session=setup["session"], configuration_collection=setup["configuration_collection"], authorization_evidence_collection=setup["authorization_evidence_collection"], authorization_evidence_registry=setup["authorization_evidence_registry"], principal_repository=setup["principal_repository"], membership_repository=setup["membership_repository"], role_assignment_repository=setup["role_assignment_repository"], business_role_repository=setup["business_role_repository"], clock=CountingClock(datetime(2026, 9, 9, 9, 1, tzinfo=timezone.utc)))
    compromise_key = "compromise-1"
    compromise_decision = "decision-compromise"
    setup["current"].business_role = COMPROMISE_BUSINESS_ROLE
    setup["evidence_collection"].rows.append(_lifecycle_evidence(setup, record, operation=COMPROMISE_OPERATION, permission=COMPROMISE_PERMISSION, business_role=COMPROMISE_BUSINESS_ROLE, authorization_role=COMPROMISE_AUTHORIZATION_ROLE, prior=EnablementState.ENABLED, target=EnablementState.COMPROMISED, key=compromise_key, decision_id=compromise_decision).to_persisted())
    record = compromise_tenant_inbound_merchant_configuration("tenant-a", "merchant-config-1", 1, record.configuration.fingerprint, 1, EnablementState.ENABLED, "security-review", compromise_key, compromise_decision, session=setup["session"], configuration_collection=setup["configuration_collection"], authorization_evidence_collection=setup["authorization_evidence_collection"], authorization_evidence_registry=setup["authorization_evidence_registry"], principal_repository=setup["principal_repository"], membership_repository=setup["membership_repository"], role_assignment_repository=setup["role_assignment_repository"], business_role_repository=setup["business_role_repository"], clock=CountingClock(datetime(2026, 9, 9, 9, 2, tzinfo=timezone.utc)))
    remediation_key = "remediation-1"
    remediation_decision = "decision-remediation"
    setup["current"].business_role = REMEDIATION_BUSINESS_ROLE
    setup["evidence_collection"].rows.append(_lifecycle_evidence(setup, record, operation=REMEDIATION_OPERATION, permission=REMEDIATION_PERMISSION, business_role=REMEDIATION_BUSINESS_ROLE, authorization_role=REMEDIATION_AUTHORIZATION_ROLE, prior=EnablementState.COMPROMISED, target=EnablementState.DISABLED, key=remediation_key, decision_id=remediation_decision).to_persisted())
    record = remediate_tenant_inbound_merchant_configuration("tenant-a", "merchant-config-1", 1, record.configuration.fingerprint, 2, EnablementState.COMPROMISED, "security-review", remediation_key, remediation_decision, session=setup["session"], configuration_collection=setup["configuration_collection"], authorization_evidence_collection=setup["authorization_evidence_collection"], authorization_evidence_registry=setup["authorization_evidence_registry"], principal_repository=setup["principal_repository"], membership_repository=setup["membership_repository"], role_assignment_repository=setup["role_assignment_repository"], business_role_repository=setup["business_role_repository"], clock=CountingClock(datetime(2026, 9, 9, 9, 3, tzinfo=timezone.utc)))
    assert record.state is EnablementState.DISABLED and record.revision == 3


def test_lifecycle_replay_is_exact_and_skips_currentness_and_clock() -> None:
    setup = _setup()
    record = _register(setup, clock=CountingClock(datetime(2026, 9, 9, 9, 0, tzinfo=timezone.utc)))
    key, decision = "life-replay", "decision-replay"
    setup["current"].business_role = LIFECYCLE_BUSINESS_ROLE
    evidence = _lifecycle_evidence(setup, record, operation=LIFECYCLE_OPERATION, permission=LIFECYCLE_PERMISSION, business_role=LIFECYCLE_BUSINESS_ROLE, authorization_role=LIFECYCLE_AUTHORIZATION_ROLE, prior=EnablementState.DISABLED, target=EnablementState.ENABLED, key=key, decision_id=decision)
    setup["evidence_collection"].rows.append(evidence.to_persisted())
    first = transition_tenant_inbound_merchant_configuration("tenant-a", "merchant-config-1", 1, record.configuration.fingerprint, 0, EnablementState.DISABLED, EnablementState.ENABLED, "security-review", key, decision, session=setup["session"], configuration_collection=setup["configuration_collection"], authorization_evidence_collection=setup["authorization_evidence_collection"], authorization_evidence_registry=setup["authorization_evidence_registry"], principal_repository=setup["principal_repository"], membership_repository=setup["membership_repository"], role_assignment_repository=setup["role_assignment_repository"], business_role_repository=setup["business_role_repository"], clock=CountingClock(datetime(2026, 9, 9, 9, 1, tzinfo=timezone.utc)))
    setup["current"].principal = lambda *_args, **_kwargs: (_ for _ in ()).throw(AssertionError("reauthorized"))
    replay_clock = CountingClock(datetime(2027, 1, 1, tzinfo=timezone.utc))
    second = transition_tenant_inbound_merchant_configuration("tenant-a", "merchant-config-1", 1, record.configuration.fingerprint, 0, EnablementState.DISABLED, EnablementState.ENABLED, "security-review", key, decision, session=setup["session"], configuration_collection=setup["configuration_collection"], authorization_evidence_collection=setup["authorization_evidence_collection"], authorization_evidence_registry=setup["authorization_evidence_registry"], principal_repository=setup["principal_repository"], membership_repository=setup["membership_repository"], role_assignment_repository=setup["role_assignment_repository"], business_role_repository=setup["business_role_repository"], clock=replay_clock)
    assert second == first and replay_clock.calls == 0


def test_metadata_and_frozen_owner_anchors_are_present() -> None:
    source = Path("tools/eos/saas/billing/tenant_inbound_merchant_configuration_issuance.py").read_text()
    assert VERSION in source
    assert "END OF WILSY OS SOVEREIGN ARTIFACT" in source
    assert Path("tools/eos/saas/domain/tenant_inbound_merchant_configuration.py").stat().st_size == 14387
    assert Path("tools/eos/saas/billing/tenant_inbound_merchant_configuration_registry.py").stat().st_size == 36982


def _invoke_lifecycle(setup: dict[str, Any], *, api: Any, prior: EnablementState, target: EnablementState, key: str, decision: str, **overrides: Any) -> Any:
    """Invoke one public lifecycle authority with the exact synthetic evidence envelope."""
    values = _transition_kwargs(setup, prior=prior, target=target, key=key, decision=decision)
    values.update(overrides)
    if api is compromise_tenant_inbound_merchant_configuration:
        values["security_event_idempotency_key"] = values.pop("lifecycle_idempotency_key")
        values.pop("target_state", None)
        values.pop("operation", None)
        values.pop("permission", None)
        return api(**values)
    if api is remediate_tenant_inbound_merchant_configuration:
        values.pop("target_state", None)
        values.pop("operation", None)
        values.pop("permission", None)
        return api(**values)
    values.pop("operation", None)
    values.pop("permission", None)
    return api(**values)


def _fresh_lifecycle(*, prior: EnablementState, target: EnablementState, api: Any = transition_tenant_inbound_merchant_configuration, key: str = "matrix-key", decision: str = "matrix-decision") -> tuple[dict[str, Any], Any]:
    """Prepare and execute one fresh transition while retaining the registry spy."""
    authority = {
        transition_tenant_inbound_merchant_configuration: (LIFECYCLE_OPERATION, LIFECYCLE_PERMISSION, LIFECYCLE_BUSINESS_ROLE, LIFECYCLE_AUTHORIZATION_ROLE),
        compromise_tenant_inbound_merchant_configuration: (COMPROMISE_OPERATION, COMPROMISE_PERMISSION, COMPROMISE_BUSINESS_ROLE, COMPROMISE_AUTHORIZATION_ROLE),
        remediate_tenant_inbound_merchant_configuration: (REMEDIATION_OPERATION, REMEDIATION_PERMISSION, REMEDIATION_BUSINESS_ROLE, REMEDIATION_AUTHORIZATION_ROLE),
    }[api]
    setup = _synthetic_setup(state=prior, revision=0, target=target, operation=authority[0], permission=authority[1], business_role=authority[2], authorization_role=authority[3], key=key, decision=decision)
    result = _invoke_lifecycle(setup, api=api, prior=prior, target=target, key=key, decision=decision)
    return setup, result


ORDINARY_CASES = [
    (2, EnablementState.DISABLED, EnablementState.SUSPENDED),
    (3, EnablementState.DISABLED, EnablementState.RETIRED),
    (4, EnablementState.ENABLED, EnablementState.DISABLED),
    (5, EnablementState.ENABLED, EnablementState.SUSPENDED),
    (6, EnablementState.ENABLED, EnablementState.RETIRED),
    (7, EnablementState.SUSPENDED, EnablementState.ENABLED),
    (8, EnablementState.SUSPENDED, EnablementState.DISABLED),
    (9, EnablementState.SUSPENDED, EnablementState.RETIRED),
]


@pytest.mark.parametrize("case,prior,target", ORDINARY_CASES, ids=[f"case-{case}" for case, _, _ in ORDINARY_CASES])
def test_cases_2_to_9_ordinary_edges_are_exact(case: int, prior: EnablementState, target: EnablementState) -> None:
    setup, result = _fresh_lifecycle(prior=prior, target=target, key=f"ordinary-{case}", decision=f"decision-{case}")
    assert result.state is target
    assert len(setup["registry"].transition_calls) == 1
    call = setup["registry"].transition_calls[0]
    assert call[4] is prior and call[5] is target
    assert call[9] == f"tenant-authorization-decision:decision-{case}"
    assert len(call[10]) == 128 and call[11] == f"ordinary-{case}"


@pytest.mark.parametrize("case,prior,target", [
    (10, EnablementState.COMPROMISED, EnablementState.ENABLED),
    (11, EnablementState.RETIRED, EnablementState.ENABLED),
    (12, EnablementState.DISABLED, EnablementState.COMPROMISED),
    (13, EnablementState.DISABLED, EnablementState.DISABLED),
], ids=["case-10", "case-11", "case-12", "case-13"])
def test_cases_10_to_13_forbidden_ordinary_edges_fail_closed(case: int, prior: EnablementState, target: EnablementState) -> None:
    setup = _synthetic_setup(state=prior, target=target, key=f"forbidden-{case}", decision=f"decision-{case}")
    with pytest.raises(TenantInboundMerchantConfigurationIssuanceError):
        _invoke_lifecycle(setup, api=transition_tenant_inbound_merchant_configuration, prior=prior, target=target, key=f"forbidden-{case}", decision=f"decision-{case}")
    assert len(setup["registry"].transition_calls) == 0


@pytest.mark.parametrize("case,prior", [(14, EnablementState.DISABLED), (16, EnablementState.SUSPENDED)], ids=["case-14", "case-16"])
def test_cases_14_and_16_compromise_success_forward_exact_authority(case: int, prior: EnablementState) -> None:
    setup, result = _fresh_lifecycle(prior=prior, target=EnablementState.COMPROMISED, api=compromise_tenant_inbound_merchant_configuration, key=f"compromise-{case}", decision=f"decision-{case}")
    assert result.state is EnablementState.COMPROMISED
    assert len(setup["registry"].transition_calls) == 1
    call = setup["registry"].transition_calls[0]
    assert call[4] is prior and call[5] is EnablementState.COMPROMISED and call[11] == f"compromise-{case}"
    assert call[9] == f"tenant-authorization-decision:decision-{case}" and len(call[10]) == 128


@pytest.mark.parametrize("case,prior", [(17, EnablementState.RETIRED), (18, EnablementState.COMPROMISED)], ids=["case-17", "case-18"])
def test_cases_17_and_18_compromise_forbidden_edges_fail_closed(case: int, prior: EnablementState) -> None:
    setup = _synthetic_setup(state=prior, target=EnablementState.COMPROMISED, operation=COMPROMISE_OPERATION, permission=COMPROMISE_PERMISSION, business_role=COMPROMISE_BUSINESS_ROLE, authorization_role=COMPROMISE_AUTHORIZATION_ROLE, key=f"compromise-forbidden-{case}", decision=f"decision-{case}")
    with pytest.raises(TenantInboundMerchantConfigurationIssuanceError):
        _invoke_lifecycle(setup, api=compromise_tenant_inbound_merchant_configuration, prior=prior, target=EnablementState.COMPROMISED, key=f"compromise-forbidden-{case}", decision=f"decision-{case}")
    assert len(setup["registry"].transition_calls) == 0


@pytest.mark.parametrize("case,prior", [(20, EnablementState.DISABLED), (20, EnablementState.ENABLED), (20, EnablementState.SUSPENDED), (20, EnablementState.RETIRED)], ids=["disabled", "enabled", "suspended", "retired"])
def test_case_20_non_compromised_remediation_sources_reject(case: int, prior: EnablementState) -> None:
    setup = _synthetic_setup(state=prior, target=EnablementState.DISABLED, operation=REMEDIATION_OPERATION, permission=REMEDIATION_PERMISSION, business_role=REMEDIATION_BUSINESS_ROLE, authorization_role=REMEDIATION_AUTHORIZATION_ROLE, key=f"remediate-{prior.value}", decision=f"decision-{prior.value}")
    with pytest.raises(TenantInboundMerchantConfigurationIssuanceError):
        _invoke_lifecycle(setup, api=remediate_tenant_inbound_merchant_configuration, prior=prior, target=EnablementState.DISABLED, key=f"remediate-{prior.value}", decision=f"decision-{prior.value}")
    assert len(setup["registry"].transition_calls) == 0


@pytest.mark.parametrize("case,target", [(21, EnablementState.RETIRED), (22, EnablementState.ENABLED)], ids=["retire", "enable"])
def test_cases_21_and_22_remediation_target_is_fixed_disabled(case: int, target: EnablementState) -> None:
    parameters = inspect.signature(remediate_tenant_inbound_merchant_configuration).parameters
    assert "target_state" not in parameters
    assert target is not EnablementState.DISABLED


@pytest.mark.parametrize("case,expected_api,called_api", [
    (23, compromise_tenant_inbound_merchant_configuration, transition_tenant_inbound_merchant_configuration),
    (24, remediate_tenant_inbound_merchant_configuration, transition_tenant_inbound_merchant_configuration),
    (25, transition_tenant_inbound_merchant_configuration, compromise_tenant_inbound_merchant_configuration),
    (26, remediate_tenant_inbound_merchant_configuration, compromise_tenant_inbound_merchant_configuration),
    (27, compromise_tenant_inbound_merchant_configuration, remediate_tenant_inbound_merchant_configuration),
    (28, transition_tenant_inbound_merchant_configuration, remediate_tenant_inbound_merchant_configuration),
    (29, remediate_tenant_inbound_merchant_configuration, transition_tenant_inbound_merchant_configuration),
    (30, transition_tenant_inbound_merchant_configuration, compromise_tenant_inbound_merchant_configuration),
], ids=[f"case-{case}" for case in range(23, 31)])
def test_cases_23_to_30_authority_substitution_fails_before_write(case: int, expected_api: Any, called_api: Any) -> None:
    expected = {
        compromise_tenant_inbound_merchant_configuration: (EnablementState.ENABLED, EnablementState.COMPROMISED, COMPROMISE_OPERATION, COMPROMISE_PERMISSION, COMPROMISE_BUSINESS_ROLE, COMPROMISE_AUTHORIZATION_ROLE),
        remediate_tenant_inbound_merchant_configuration: (EnablementState.COMPROMISED, EnablementState.DISABLED, REMEDIATION_OPERATION, REMEDIATION_PERMISSION, REMEDIATION_BUSINESS_ROLE, REMEDIATION_AUTHORIZATION_ROLE),
        transition_tenant_inbound_merchant_configuration: (EnablementState.DISABLED, EnablementState.ENABLED, LIFECYCLE_OPERATION, LIFECYCLE_PERMISSION, LIFECYCLE_BUSINESS_ROLE, LIFECYCLE_AUTHORIZATION_ROLE),
    }[expected_api]
    prior, target, operation, permission, business_role, authorization_role = expected
    setup = _synthetic_setup(state=prior, target=target, operation=operation, permission=permission, business_role=business_role, authorization_role=authorization_role, key=f"authority-{case}", decision=f"authority-{case}")
    with pytest.raises(TenantInboundMerchantConfigurationIssuanceError):
        _invoke_lifecycle(setup, api=called_api, prior=prior, target=target, key=f"authority-{case}", decision=f"authority-{case}")
    assert len(setup["registry"].transition_calls) == 0


def _establish_event(api: Any, prior: EnablementState, target: EnablementState, key: str, decision: str) -> tuple[dict[str, Any], Any]:
    return _fresh_lifecycle(prior=prior, target=target, api=api, key=key, decision=decision)


@pytest.mark.parametrize("case,api,prior,target", [
    (32, compromise_tenant_inbound_merchant_configuration, EnablementState.ENABLED, EnablementState.COMPROMISED),
    (33, remediate_tenant_inbound_merchant_configuration, EnablementState.COMPROMISED, EnablementState.DISABLED),
], ids=["case-32", "case-33"])
def test_cases_32_and_33_exact_specialized_replay_skips_fresh_authority(case: int, api: Any, prior: EnablementState, target: EnablementState) -> None:
    setup, first = _establish_event(api, prior, target, f"replay-{case}", f"decision-{case}")
    setup["current"].principal = lambda *_args, **_kwargs: (_ for _ in ()).throw(AssertionError("fresh currentness on replay"))
    replay_clock = CountingClock(datetime(2027, 1, 1, tzinfo=timezone.utc))
    second = _invoke_lifecycle(setup, api=api, prior=prior, target=target, key=f"replay-{case}", decision=f"decision-{case}", expected_lifecycle_revision=0, clock=replay_clock)
    assert second == first and replay_clock.calls == 0
    assert len(setup["registry"].transition_calls) == 1


def test_cases_35_to_38_replay_is_event_revision_and_state_immutable() -> None:
    setup, first = _establish_event(transition_tenant_inbound_merchant_configuration, EnablementState.DISABLED, EnablementState.ENABLED, "replay-ordinary", "decision-replay-ordinary")
    first_evidence = setup["evidence"]
    event_count = len(setup["registry"].events)
    revision = setup["registry"].record.revision
    setup["current"].business_role = LIFECYCLE_BUSINESS_ROLE
    later_evidence = _lifecycle_evidence(setup, setup["registry"].record, operation=LIFECYCLE_OPERATION, permission=LIFECYCLE_PERMISSION, business_role=LIFECYCLE_BUSINESS_ROLE, authorization_role=LIFECYCLE_AUTHORIZATION_ROLE, prior=EnablementState.ENABLED, target=EnablementState.SUSPENDED, key="later-event", decision_id="decision-later")
    setup["authorization_evidence_registry"] = _EvidenceReader(later_evidence)
    _invoke_lifecycle(setup, api=transition_tenant_inbound_merchant_configuration, prior=EnablementState.ENABLED, target=EnablementState.SUSPENDED, key="later-event", decision="decision-later")
    later_state = setup["registry"].record.state
    setup["authorization_evidence_registry"] = _EvidenceReader(first_evidence)
    replay_clock = CountingClock(datetime(2027, 1, 1, tzinfo=timezone.utc))
    replay = _invoke_lifecycle(setup, api=transition_tenant_inbound_merchant_configuration, prior=EnablementState.DISABLED, target=EnablementState.ENABLED, key="replay-ordinary", decision="decision-replay-ordinary", expected_lifecycle_revision=0, clock=replay_clock)
    assert len(setup["registry"].events) == event_count + 1
    assert setup["registry"].record.revision == revision + 1
    assert replay == first and setup["registry"].record.state is later_state and replay_clock.calls == 0
    assert len(setup["registry"].transition_calls) == 2


@pytest.mark.parametrize("mutation", ["authorization_evidence_fingerprint", "authorization_reference"], ids=["historical-auth-fingerprint", "historical-auth-reference"])
def test_cases_39_and_40_historical_authority_corruption_rejects(mutation: str) -> None:
    setup, _ = _establish_event(transition_tenant_inbound_merchant_configuration, EnablementState.DISABLED, EnablementState.ENABLED, f"corrupt-{mutation}", f"decision-{mutation}")
    event = setup["registry"].events[f"corrupt-{mutation}"][1]
    setattr(event, mutation, "corrupt" if mutation == "authorization_reference" else "0" * 128)
    with pytest.raises(TenantInboundMerchantConfigurationIssuanceError):
        _invoke_lifecycle(setup, api=transition_tenant_inbound_merchant_configuration, prior=EnablementState.DISABLED, target=EnablementState.ENABLED, key=f"corrupt-{mutation}", decision=f"decision-{mutation}")
    assert len(setup["registry"].transition_calls) == 1


def test_case_41_replay_with_divergent_durable_evidence_fails_closed() -> None:
    setup, _ = _establish_event(transition_tenant_inbound_merchant_configuration, EnablementState.DISABLED, EnablementState.ENABLED, "divergent-replay", "decision-divergent-replay")
    original = _lifecycle_evidence(setup, setup["registry"].record, operation=LIFECYCLE_OPERATION, permission=LIFECYCLE_PERMISSION, business_role=LIFECYCLE_BUSINESS_ROLE, authorization_role=LIFECYCLE_AUTHORIZATION_ROLE, prior=EnablementState.DISABLED, target=EnablementState.ENABLED, key="divergent-replay", decision_id="decision-divergent-replay")
    setup["authorization_evidence_registry"] = _EvidenceReader(replace(original, subject_evidence_fingerprint="0" * 128))
    with pytest.raises(TenantInboundMerchantConfigurationIssuanceError):
        _invoke_lifecycle(setup, api=transition_tenant_inbound_merchant_configuration, prior=EnablementState.DISABLED, target=EnablementState.ENABLED, key="divergent-replay", decision="decision-divergent-replay")
    assert len(setup["registry"].transition_calls) == 1


@pytest.mark.parametrize("case,override", [
    (42, {"merchant_configuration_id": "other-config"}), (43, {"merchant_configuration_version": 2}),
    (44, {"expected_configuration_fingerprint": "0" * 128}), (45, {"expected_lifecycle_revision": 99}),
    (46, {"expected_prior_state": EnablementState.SUSPENDED}), (47, {"target_state": EnablementState.RETIRED}),
    (48, {"reason_reference": "other-reason"}),
], ids=[f"case-{case}" for case in range(42, 49)])
def test_cases_42_to_48_tenant_key_hit_rejects_divergent_intent(case: int, override: dict[str, Any]) -> None:
    setup, _ = _establish_event(transition_tenant_inbound_merchant_configuration, EnablementState.DISABLED, EnablementState.ENABLED, "tenant-wide-key", "tenant-wide-decision")
    calls_before = setup["registry"].lookup_calls
    current_before = len(setup["current"].principal_calls) + len(setup["current"].membership_calls) + len(setup["current"].assignment_calls)
    clock = CountingClock(datetime(2027, 1, 1, tzinfo=timezone.utc))
    with pytest.raises(TenantInboundMerchantConfigurationIssuanceError):
        _invoke_lifecycle(setup, api=transition_tenant_inbound_merchant_configuration, prior=EnablementState.DISABLED, target=EnablementState.ENABLED, key="tenant-wide-key", decision="tenant-wide-decision", clock=clock, **override)
    assert setup["registry"].lookup_calls == calls_before + 1
    assert len(setup["registry"].transition_calls) == 1
    assert len(setup["current"].principal_calls) + len(setup["current"].membership_calls) + len(setup["current"].assignment_calls) == current_before
    assert clock.calls == 0


def test_case_49_same_key_under_other_tenant_isolated() -> None:
    setup, _ = _establish_event(transition_tenant_inbound_merchant_configuration, EnablementState.DISABLED, EnablementState.ENABLED, "isolated-key", "isolated-decision")
    with pytest.raises(TenantInboundMerchantConfigurationIssuanceError):
        _invoke_lifecycle(setup, api=transition_tenant_inbound_merchant_configuration, prior=EnablementState.DISABLED, target=EnablementState.ENABLED, key="isolated-key", decision="isolated-decision", tenant_id="tenant-b")
    assert setup["registry"].lookup_calls == 2 and len(setup["registry"].transition_calls) == 1
    assert setup["registry"].events["isolated-key"][1].tenant_id == "tenant-a"


@pytest.mark.parametrize("case,kind", [(50, "principal"), (51, "membership"), (52, "role"), (53, "business")], ids=["case-50", "case-51", "case-52", "case-53"])
def test_cases_50_to_53_current_identity_and_role_fail_closed(case: int, kind: str) -> None:
    current = CurrentRepositories()
    if kind == "principal":
        current.principal = lambda *_args, **_kwargs: _CurrentPrincipal("principal-1", PrincipalStatus.REVOKED)
    elif kind == "membership":
        current.membership = lambda *_args, **_kwargs: _CurrentMembership("principal-1", "tenant-a", TenantMembershipStatus.REVOKED, 1)
    elif kind == "role":
        current.assignment = lambda principal_id, tenant_id, role_id, *, session=None: _AuthAssignment(RoleAssignmentStatus.REVOKED, 1) if role_id in {LIFECYCLE_AUTHORIZATION_ROLE, COMPROMISE_AUTHORIZATION_ROLE, REMEDIATION_AUTHORIZATION_ROLE} else _BusinessAssignment()
    else:
        current.business_role = "wrong_business_role"
    setup = _synthetic_setup(current=current, operation=LIFECYCLE_OPERATION, permission=LIFECYCLE_PERMISSION, business_role=LIFECYCLE_BUSINESS_ROLE, authorization_role=LIFECYCLE_AUTHORIZATION_ROLE, state=EnablementState.DISABLED, target=EnablementState.ENABLED, key=f"current-{case}", decision=f"current-{case}")
    if kind == "business":
        setup["current"].business_role = "wrong_business_role"
    with pytest.raises(TenantInboundMerchantConfigurationIssuanceError):
        _invoke_lifecycle(setup, api=transition_tenant_inbound_merchant_configuration, prior=EnablementState.DISABLED, target=EnablementState.ENABLED, key=f"current-{case}", decision=f"current-{case}")
    assert len(setup["registry"].transition_calls) == 0


@pytest.mark.parametrize("case,field", [(54, "permission_namespace_version"), (55, "authorization_role_policy_version"), (56, "tenant_business_role_policy_version"), (57, "tenant_authorization_composition_version")], ids=[f"case-{case}" for case in range(54, 58)])
def test_cases_54_to_57_stale_authorization_policy_versions_reject(case: int, field: str) -> None:
    setup = _synthetic_setup(operation=LIFECYCLE_OPERATION, permission=LIFECYCLE_PERMISSION, business_role=LIFECYCLE_BUSINESS_ROLE, authorization_role=LIFECYCLE_AUTHORIZATION_ROLE, state=EnablementState.DISABLED, target=EnablementState.ENABLED, key=f"version-{case}", decision=f"version-{case}")
    setup["evidence"] = replace(setup["evidence"], **{field: "stale-version"})
    setup["authorization_evidence_registry"] = _EvidenceReader(setup["evidence"])
    with pytest.raises(TenantInboundMerchantConfigurationIssuanceError):
        _invoke_lifecycle(setup, api=transition_tenant_inbound_merchant_configuration, prior=EnablementState.DISABLED, target=EnablementState.ENABLED, key=f"version-{case}", decision=f"version-{case}")
    assert len(setup["registry"].transition_calls) == 0


@pytest.mark.parametrize("case,override", [(58, {"tenant_id": "tenant-b"}), (59, {"expected_configuration_fingerprint": "0" * 128}), (60, {"expected_lifecycle_revision": 1}), (61, {"expected_prior_state": EnablementState.SUSPENDED})], ids=[f"case-{case}" for case in range(58, 62)])
def test_cases_58_to_61_configuration_currentness_rejects(case: int, override: dict[str, Any]) -> None:
    setup = _synthetic_setup(state=EnablementState.DISABLED, target=EnablementState.ENABLED, key=f"config-{case}", decision=f"config-{case}")
    with pytest.raises(TenantInboundMerchantConfigurationIssuanceError):
        _invoke_lifecycle(setup, api=transition_tenant_inbound_merchant_configuration, prior=EnablementState.DISABLED, target=EnablementState.ENABLED, key=f"config-{case}", decision=f"config-{case}", **override)
    assert len(setup["registry"].transition_calls) == 0


@pytest.mark.parametrize("case,error_type", [(62, RuntimeError), (63, DuplicateKeyError)], ids=["case-62-cas", "case-63-duplicate"])
def test_cases_62_to_64_registry_failures_propagate_without_recovery(case: int, error_type: type[Exception]) -> None:
    setup = _synthetic_setup(state=EnablementState.DISABLED, target=EnablementState.ENABLED, key=f"registry-failure-{case}", decision=f"registry-failure-{case}")
    setup["registry"].failure = error_type("registry failure")
    with pytest.raises(error_type):
        _invoke_lifecycle(setup, api=transition_tenant_inbound_merchant_configuration, prior=EnablementState.DISABLED, target=EnablementState.ENABLED, key=f"registry-failure-{case}", decision=f"registry-failure-{case}")
    assert len(setup["registry"].transition_calls) == 1
    assert setup["registry"].record.revision == 0


@pytest.mark.parametrize("case", [65, 66, 67, 68, 69], ids=[f"case-{case}" for case in range(65, 70)])
def test_cases_65_to_69_transaction_is_caller_owned(case: int, monkeypatch: pytest.MonkeyPatch) -> None:
    setup = _synthetic_setup()
    session = TransactionSessionSpy(active=case != 65)
    setup["session"] = session
    factory_calls = 0

    def forbidden_session_factory(*args: object, **kwargs: object) -> object:
        nonlocal factory_calls
        factory_calls += 1
        raise AssertionError("issuer attempted child-session creation")

    monkeypatch.setattr(issuance_module, "ClientSession", forbidden_session_factory)
    if case == 65:
        with pytest.raises(TenantInboundMerchantConfigurationIssuanceError):
            _invoke_lifecycle(setup, api=transition_tenant_inbound_merchant_configuration, prior=EnablementState.DISABLED, target=EnablementState.ENABLED, key="inactive-tx", decision="inactive-tx")
        assert setup["registry"].lookup_calls == 0
    else:
        result = _invoke_lifecycle(setup, api=transition_tenant_inbound_merchant_configuration, prior=EnablementState.DISABLED, target=EnablementState.ENABLED, key="key-1", decision="decision-1")
        assert result.state is EnablementState.ENABLED
        assert len(setup["registry"].transition_calls) == 1
        assert setup["registry"].transition_sessions == [session]
        assert isinstance(setup["authorization_evidence_registry"], _EvidenceReader)
        assert setup["authorization_evidence_registry"].sessions == [session]  # type: ignore[union-attr]
        assert all(value is session for value in setup["current"].principal_calls + setup["current"].membership_calls + setup["current"].assignment_calls)
        assert all(value is session for value in setup["registry"].lookup_sessions)
    assert factory_calls == 0
    assert session.start_calls == 0
    assert session.commit_calls == 0
    assert session.abort_calls == 0


def test_cases_70_and_71_reenable_after_remediation_has_no_security_fact() -> None:
    setup = _synthetic_setup(state=EnablementState.ENABLED, target=EnablementState.COMPROMISED, operation=COMPROMISE_OPERATION, permission=COMPROMISE_PERMISSION, business_role=COMPROMISE_BUSINESS_ROLE, authorization_role=COMPROMISE_AUTHORIZATION_ROLE, key="security-sequence", decision="security-sequence")
    _invoke_lifecycle(setup, api=compromise_tenant_inbound_merchant_configuration, prior=EnablementState.ENABLED, target=EnablementState.COMPROMISED, key="security-sequence", decision="security-sequence")
    remediation = _lifecycle_evidence(setup, setup["registry"].record, operation=REMEDIATION_OPERATION, permission=REMEDIATION_PERMISSION, business_role=REMEDIATION_BUSINESS_ROLE, authorization_role=REMEDIATION_AUTHORIZATION_ROLE, prior=EnablementState.COMPROMISED, target=EnablementState.DISABLED, key="security-remediation", decision_id="security-remediation")
    setup["current"].business_role = REMEDIATION_BUSINESS_ROLE
    setup["authorization_evidence_registry"] = _EvidenceReader(remediation)
    _invoke_lifecycle(setup, api=remediate_tenant_inbound_merchant_configuration, prior=EnablementState.COMPROMISED, target=EnablementState.DISABLED, key="security-remediation", decision="security-remediation")
    reenable = _lifecycle_evidence(setup, setup["registry"].record, operation=LIFECYCLE_OPERATION, permission=LIFECYCLE_PERMISSION, business_role=LIFECYCLE_BUSINESS_ROLE, authorization_role=LIFECYCLE_AUTHORIZATION_ROLE, prior=EnablementState.DISABLED, target=EnablementState.ENABLED, key="security-reenable", decision_id="security-reenable")
    setup["current"].business_role = LIFECYCLE_BUSINESS_ROLE
    setup["authorization_evidence_registry"] = _EvidenceReader(reenable)
    result = _invoke_lifecycle(setup, api=transition_tenant_inbound_merchant_configuration, prior=EnablementState.DISABLED, target=EnablementState.ENABLED, key="security-reenable", decision="security-reenable")
    assert result.state is EnablementState.ENABLED
    assert [call[5] for call in setup["registry"].transition_calls] == [EnablementState.COMPROMISED, EnablementState.DISABLED, EnablementState.ENABLED]
    assert not any("secret" in role.lower() or "kms" in role.lower() for role in setup["current"].assignment_role_ids)


def test_cases_72_to_77_model_a_and_financial_firewall_is_explicit() -> None:
    apis = [transition_tenant_inbound_merchant_configuration, compromise_tenant_inbound_merchant_configuration, remediate_tenant_inbound_merchant_configuration]
    forbidden_parameters = {"raw_secret", "secret", "secret_value", "secret_bytes", "credential", "credential_value", "current_secret_version", "merchant_secret", "merchant_key", "private_key"}
    assert all(not forbidden_parameters.intersection(inspect.signature(api).parameters) for api in apis)
    source = Path("tools/eos/saas/billing/tenant_inbound_merchant_configuration_issuance.py").read_text().lower()
    tree = ast.parse(source)
    imported = " ".join(node.module or "" for node in ast.walk(tree) if isinstance(node, ast.ImportFrom)).lower()
    names = " ".join(node.id for node in ast.walk(tree) if isinstance(node, ast.Name)).lower()
    for forbidden in ("kms", "payfast", "payshap", "provider_policy", "provider_binding", "checkout", "clientinvoice", "commercialreceivable"):
        assert forbidden not in imported and forbidden not in names


def test_case_78_registration_surface_remains_unchanged() -> None:
    setup = _setup()
    result = _register(setup, clock=CountingClock(datetime(2026, 9, 9, 9, 0, tzinfo=timezone.utc)))
    assert result.state is EnablementState.DISABLED and result.revision == 0
    assert len(setup["config_collection"].rows) == 1


# ARTIFACT: test_tenant_inbound_merchant_configuration_issuance.py
# VERSION: v1.1.0-M11-R8-R3B-P8-P3B-I2-I1-R2-R1-AUTHORIZED-MERCHANT-CONFIGURATION-LIFECYCLE-CERT
# AUTHORITY BOUNDARY: direct unit certificate only; no production authority.
# TENANT POSTURE: synthetic tenant-scoped records and exact session assertions.
# FAIL-CLOSED POSTURE: all divergence, stale currentness, corruption, and forbidden inputs reject.
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively.
# END OF WILSY OS SOVEREIGN ARTIFACT
