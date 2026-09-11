"""WILSY OS real-Mongo provider-policy activation certificate.

TITLE: Tenant Inbound Provider Policy Activation — Real Mongo Certificate
VERSION: v1.0.0-M11-R8-R3B-P8-P3C-P8-R2D
AUTHORITY: Wilsy OS Core Governance; host-backed persistence evidence only.
EPITOME: Certify P7 activation orchestration over the frozen P5/P6 stack using
         a real replica-set transaction, durable indexes, replay, CAS and
         strict hydration.  No provider execution or credential authority is
         created here.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tests/integration/test_tenant_inbound_provider_policy_activation_real_mongo.py
COLLABORATION / OWNERSHIP: Real-Mongo certificate owner for P8 provider-policy
                            activation; P1/P2/P4/P5/P6/P7 remain separate.
CERTIFICATION / UPDATE DATE: 2026-09-10
CHANGELOG: v1.0.0-M11-R8-R3B-P8-P3C-P8-R2D corrects the tenant-scoped event-ledger
           assertion to match the seven durable events produced by the certificate.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2.
SECURITY / PRIVACY POSTURE: Synthetic identifiers only; no raw secret, KMS,
                             provider transport, PayFast or PayShap call.
TENANT BOUNDARY: Every event, policy, configuration, evidence and lookup is
                 explicitly tenant and scope bound.
AUTHORITY BOUNDARY: Tests existing policy activation authority only; no policy
                    binding, checkout, payment, settlement or invoice truth.
TRANSACTION BOUNDARY: The harness owns sessions, transactions, commit and abort.
FAIL-CLOSED DECLARATION: Wrong topology, corruption, replay divergence, stale
                          CAS and duplicate durable identity fail the certificate.
"""
from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass
from datetime import datetime, timezone
from threading import Barrier
from typing import Any, cast
from uuid import uuid4
import os

import pytest
from pymongo import MongoClient
from pymongo.errors import DuplicateKeyError, PyMongoError

from tools.eos.auth.permission_namespace import VERSION as PERMISSION_NAMESPACE_VERSION
from tools.eos.auth.principal_authority import PrincipalAuthority
from tools.eos.auth.principal_status import PrincipalStatus
from tools.eos.auth.role_assignment import RoleAssignmentAuthority, RoleAssignmentStatus
from tools.eos.auth.role_assignment_repository import RoleAssignmentNotFoundError
from tools.eos.auth.roles import VERSION as ROLES_VERSION
from tools.eos.auth.tenant_authorization import VERSION as AUTHORIZATION_VERSION
from tools.eos.auth.tenant_authorization_decision_evidence import TenantAuthorizationDecisionEvidence
from tools.eos.auth.tenant_authority_policy import VERSION as TENANT_AUTHORITY_POLICY_VERSION
from tools.eos.auth.tenant_membership import TenantMembershipAuthority, TenantMembershipStatus
from tools.eos.saas.domain.tenant_inbound_merchant_configuration import (
    InboundMerchantProviderId,
    TenantInboundMerchantConfiguration,
)
from tools.eos.saas.domain.tenant_inbound_provider_policy import (
    TenantInboundProviderPolicy,
    TenantInboundProviderPolicyScope,
)
from tools.eos.saas.domain.tenant_inbound_provider_policy_activation import (
    TenantInboundProviderPolicyActivationEventKind,
    TenantInboundProviderPolicyReference,
)
from tools.eos.saas.billing.tenant_inbound_merchant_configuration_registry import (
    EnablementState,
    TenantInboundMerchantConfigurationRegistry,
)
from tools.eos.saas.billing.tenant_inbound_provider_policy_activation_issuance import (
    ACTIVATE_OPERATION,
    ACTIVATE_PERMISSION,
    ACTIVATE_AUTH_ROLE,
    ACTIVATE_BUSINESS_ROLE,
    DEACTIVATE_OPERATION,
    DEACTIVATE_PERMISSION,
    DEACTIVATE_AUTH_ROLE,
    DEACTIVATE_BUSINESS_ROLE,
    EMERGENCY_DISABLE_OPERATION,
    EMERGENCY_DISABLE_PERMISSION,
    EMERGENCY_DISABLE_AUTH_ROLE,
    EMERGENCY_DISABLE_BUSINESS_ROLE,
    TenantInboundProviderPolicyActivationIssuanceError,
    _intent_payload,
    _subject,
    activate_tenant_inbound_provider_policy,
    supersede_tenant_inbound_provider_policy,
    deactivate_tenant_inbound_provider_policy,
    emergency_disable_tenant_inbound_provider_policy,
)
from tools.eos.saas.billing.tenant_inbound_provider_policy_activation_registry import (
    ActivationRegistry,
    EVENT_IDENTITY_INDEX_NAME,
    IDEMPOTENCY_INDEX_NAME,
    REVISION_INDEX_NAME,
    ACTIVE_SLOT_INDEX_NAME,
    TenantInboundProviderPolicyActivationRegistryRecordInvalidError,
    TenantInboundProviderPolicyActivationRegistryCASConflictError,
)
from tools.eos.saas.billing.tenant_inbound_provider_policy_registry import TenantInboundProviderPolicyRegistry


URI = "mongodb://127.0.0.1:27027/?replicaSet=wilsyVendorCertRS"
SCOPE = TenantInboundProviderPolicyScope.INBOUND_COLLECTION
AT = datetime(2026, 9, 10, 10, 0, tzinfo=timezone.utc)
PRINCIPAL = "principal-provider-policy-real-mongo"
TENANT_A = "tenant-provider-policy-a"
TENANT_B = "tenant-provider-policy-b"
AUTH_FP = "a" * 128


class _PrincipalRepo:
    def __init__(self, value: PrincipalAuthority) -> None:
        self.value = value

    def resolve(self, principal_id: str, *, session: Any = None) -> PrincipalAuthority:
        if principal_id != self.value.principal_id:
            from tools.eos.auth.principal_authority_repository import PrincipalAuthorityNotFoundError
            raise PrincipalAuthorityNotFoundError("PRINCIPAL_NOT_FOUND")
        return self.value


class _MembershipRepo:
    def __init__(self, value: TenantMembershipAuthority) -> None:
        self.value = value

    def resolve(self, principal_id: str, tenant_id: str, *, session: Any = None) -> TenantMembershipAuthority:
        if (principal_id, tenant_id) != (self.value.principal_id, self.value.tenant_id):
            from tools.eos.auth.tenant_membership_repository import TenantMembershipNotFoundError
            raise TenantMembershipNotFoundError("MEMBERSHIP_NOT_FOUND")
        return self.value


class _RoleRepo:
    def __init__(self, tenant_id: str, business_role: str, auth_roles: tuple[str, ...]) -> None:
        self.tenant_id = tenant_id
        self.business_role = business_role
        self.values = {
            role: RoleAssignmentAuthority(PRINCIPAL, tenant_id, role, RoleAssignmentStatus.ACTIVE, 0)
            for role in auth_roles
        }
        self.values[business_role] = RoleAssignmentAuthority(PRINCIPAL, tenant_id, business_role, RoleAssignmentStatus.ACTIVE, 0)

    def resolve(self, principal_id: str, tenant_id: str, role_id: str, *, session: Any = None) -> RoleAssignmentAuthority:
        value = self.values.get(role_id)
        if value is None or (principal_id, tenant_id) != (PRINCIPAL, self.tenant_id):
            raise RoleAssignmentNotFoundError("ROLE_NOT_FOUND")
        return value


class _EvidenceReader:
    def __init__(self, collection: Any) -> None:
        self.collection = collection

    def get(self, *, tenant_id: str, authorization_decision_id: str, session: Any = None) -> TenantAuthorizationDecisionEvidence:
        row = self.collection.find_one({"tenant_id": tenant_id, "authorization_decision_id": authorization_decision_id}, session=session)
        if row is None:
            raise ValueError("EVIDENCE_NOT_FOUND")
        body = dict(row)
        body.pop("_id", None)
        return TenantAuthorizationDecisionEvidence.from_persisted(body)


@dataclass(frozen=True)
class _Context:
    principal: _PrincipalRepo
    membership: _MembershipRepo
    roles: _RoleRepo


def _context(tenant: str, business_role: str, auth_role: str) -> _Context:
    return _Context(
        _PrincipalRepo(PrincipalAuthority(PRINCIPAL, PrincipalStatus.ACTIVE, 0)),
        _MembershipRepo(TenantMembershipAuthority(PRINCIPAL, tenant, TenantMembershipStatus.ACTIVE, 0)),
        _RoleRepo(tenant, business_role, (auth_role,)),
    )


def _tx(client: MongoClient, callback: Any) -> Any:
    with client.start_session() as session:
        session.start_transaction()
        try:
            result = callback(session)
            session.commit_transaction()
            return result
        except BaseException:
            if session.in_transaction:
                session.abort_transaction()
            raise


def _configuration(tenant: str, identifier: str) -> TenantInboundMerchantConfiguration:
    return TenantInboundMerchantConfiguration(
        merchant_configuration_id=identifier,
        tenant_id=tenant,
        provider_id=InboundMerchantProviderId.PAYFAST,
        merchant_account_id=f"account-{identifier}",
        merchant_configuration_version=1,
        non_secret_provider_options={"mode": "sandbox", "merchant_name": identifier, "currency": "ZAR"},
        credential_secret_reference=f"secret-ref-{identifier}",
        created_at=AT,
    )


def _seed_configuration(collection: Any, tenant: str, identifier: str, enabled: bool = True) -> TenantInboundMerchantConfiguration:
    value = _configuration(tenant, identifier)
    record = TenantInboundMerchantConfigurationRegistry.create(
        value, collection, idempotency_key=f"create-{identifier}",
        authorization_reference=f"tenant-authorization-decision:create-{identifier}",
        authorization_evidence_fingerprint=AUTH_FP,
    )
    if enabled:
        TenantInboundMerchantConfigurationRegistry.transition_enablement(
            tenant, identifier, 1, 0, EnablementState.DISABLED, EnablementState.ENABLED,
            AT, AT, f"enable-{identifier}", f"tenant-authorization-decision:enable-{identifier}",
            AUTH_FP, f"enable-key-{identifier}", collection,
        )
    assert record.configuration == value
    return value


def _policy(tenant: str, policy_id: str, config: TenantInboundMerchantConfiguration, version: int = 1) -> TenantInboundProviderPolicy:
    return TenantInboundProviderPolicy(
        tenant_id=tenant,
        provider_policy_id=policy_id,
        policy_version=version,
        policy_scope=SCOPE,
        provider_id=InboundMerchantProviderId.PAYFAST,
        merchant_configuration_id=config.merchant_configuration_id,
        merchant_configuration_version=config.merchant_configuration_version,
        merchant_configuration_fingerprint=config.fingerprint,
        authoring_authorization_reference=f"tenant-authorization-decision:author-{policy_id}",
        authoring_authorization_evidence_fingerprint=AUTH_FP,
        created_at=AT,
    )


def _reference(policy: TenantInboundProviderPolicy) -> TenantInboundProviderPolicyReference:
    return TenantInboundProviderPolicyReference(
        provider_policy_id=policy.provider_policy_id,
        policy_version=policy.policy_version,
        policy_fingerprint=policy.fingerprint,
        provider_id=policy.provider_id,
        merchant_configuration_id=policy.merchant_configuration_id,
        merchant_configuration_version=policy.merchant_configuration_version,
        merchant_configuration_fingerprint=policy.merchant_configuration_fingerprint,
    )


def _evidence(
    collection: Any, *, tenant: str, decision: str, operation: str, permission: str,
    business_role: str, auth_role: str, key: str, kind: TenantInboundProviderPolicyActivationEventKind,
    expected_revision: int | None, prior: TenantInboundProviderPolicyReference | None,
    target: TenantInboundProviderPolicyReference | None, reason: str,
) -> None:
    payload = _intent_payload(
        tenant_id=tenant, scope=SCOPE, kind=kind, expected_revision=expected_revision,
        prior_policy=prior, target_policy=target, reason_reference=reason,
        lifecycle_idempotency_key=key,
    )
    subject, fingerprint = _subject(payload, operation)
    evidence = TenantAuthorizationDecisionEvidence(
        tenant_id=tenant, authorization_decision_id=decision, principal_id=PRINCIPAL,
        operation=operation, permission=permission, business_role=business_role,
        authorization_role=auth_role, membership_revision=0, role_assignment_revision=0,
        subject_reference=subject, subject_evidence_fingerprint=fingerprint,
        permission_namespace_version=PERMISSION_NAMESPACE_VERSION,
        authorization_role_policy_version=ROLES_VERSION,
        tenant_business_role_policy_version=TENANT_AUTHORITY_POLICY_VERSION,
        tenant_authorization_composition_version=AUTHORIZATION_VERSION,
        idempotency_key=f"evidence-{key}", authorized_at=AT,
    )
    collection.insert_one(evidence.to_persisted())


@pytest.fixture()
def mongo_db() -> Any:
    configured = os.environ.get("TEST_VENDOR_MONGO_URI", URI)
    if "mongodb.net" in configured or "atlas" in configured.lower():
        pytest.fail("Atlas/production Mongo is prohibited")
    client = MongoClient(configured, tz_aware=True, serverSelectionTimeoutMS=5000, retryWrites=True)
    hello = client.admin.command("hello")
    assert hello.get("setName") == "wilsyVendorCertRS"
    assert hello.get("isWritablePrimary") is True
    database = client[f"wilsy_p8_activation_{uuid4().hex}"]
    policies, configs, evidence = database["tenant_inbound_provider_policies"], database["tenant_inbound_merchant_configurations"], database["tenant_authorization_decision_evidence"]
    events, slots = database["tenant_inbound_provider_policy_activation_events"], database["tenant_inbound_provider_policy_active_slots"]
    TenantInboundProviderPolicyRegistry.ensure_indexes(cast(Any, policies))
    TenantInboundMerchantConfigurationRegistry.ensure_indexes(configs)
    ActivationRegistry.ensure_indexes(events, slots)
    try:
        yield client, database, policies, configs, evidence, events, slots
    finally:
        client.drop_database(database.name)
        client.close()


def _common_kwargs(ctx: _Context, evidence: Any, policies: Any, configs: Any, events: Any, slots: Any, session: Any, decision: str, key: str, target: TenantInboundProviderPolicy, expected: int | None, prior: TenantInboundProviderPolicyReference | None, reason: str, *, include_target_policy_fingerprint: bool = True) -> dict[str, Any]:
    kwargs = dict(
        tenant_id=target.tenant_id, policy_scope=SCOPE, provider_policy_id=target.provider_policy_id,
        policy_version=target.policy_version,
        expected_prior_activation_revision=expected, expected_prior_active_policy=prior,
        lifecycle_idempotency_key=key, authorization_decision_id=decision, reason_reference=reason,
        session=session, policy_collection=policies, configuration_collection=configs,
        authorization_evidence_collection=evidence, event_collection=events, slot_collection=slots,
        principal_repository=ctx.principal, membership_repository=ctx.membership,
        role_assignment_repository=ctx.roles, business_role_repository=ctx.roles,
        authorization_evidence_registry=_EvidenceReader(evidence), clock=lambda: AT,
    )
    if include_target_policy_fingerprint:
        kwargs["target_policy_fingerprint"] = target.fingerprint
    return kwargs


def test_real_mongo_provider_policy_activation_certificate(mongo_db: Any) -> None:
    client, database, policies, configs, evidence, events, slots = mongo_db
    indexes = {x["name"]: x for x in events.list_indexes()}
    slot_indexes = {x["name"]: x for x in slots.list_indexes()}
    assert indexes[EVENT_IDENTITY_INDEX_NAME]["unique"] is True
    assert indexes[IDEMPOTENCY_INDEX_NAME]["unique"] is True
    assert indexes[REVISION_INDEX_NAME]["unique"] is True
    assert slot_indexes[ACTIVE_SLOT_INDEX_NAME]["unique"] is True
    assert list(indexes[IDEMPOTENCY_INDEX_NAME]["key"]) == ["tenant_id", "policy_scope", "lifecycle_idempotency_key"]

    config_a = _seed_configuration(configs, TENANT_A, "config-a")
    config_b = _seed_configuration(configs, TENANT_A, "config-b")
    config_b_disabled = _seed_configuration(configs, TENANT_A, "config-disabled", enabled=False)
    policy_a, policy_b, policy_c = _policy(TENANT_A, "policy-a", config_a), _policy(TENANT_A, "policy-b", config_b), _policy(TENANT_A, "policy-c", config_b)
    policy_disabled = _policy(TENANT_A, "policy-disabled", config_b_disabled)
    for policy in (policy_a, policy_b, policy_c, policy_disabled):
        TenantInboundProviderPolicyRegistry.create(policy, policies)

    pa = _reference(policy_a)
    ctx_activate = _context(TENANT_A, ACTIVATE_BUSINESS_ROLE, ACTIVATE_AUTH_ROLE)
    _evidence(evidence, tenant=TENANT_A, decision="decision-initial", operation=ACTIVATE_OPERATION, permission=ACTIVATE_PERMISSION, business_role=ACTIVATE_BUSINESS_ROLE, auth_role=ACTIVATE_AUTH_ROLE, key="key-initial", kind=TenantInboundProviderPolicyActivationEventKind.ACTIVATE, expected_revision=None, prior=None, target=pa, reason="initial")
    initial = _tx(client, lambda s: activate_tenant_inbound_provider_policy(**_common_kwargs(ctx_activate, evidence, policies, configs, events, slots, s, "decision-initial", "key-initial", policy_a, None, None, "initial")))
    assert initial.current_activation_revision == 0 and initial.current_active_policy == pa
    assert events.count_documents({"tenant_id": TENANT_A}) == 1 and slots.count_documents({"tenant_id": TENANT_A}) == 1
    assert ActivationRegistry.get_event(TENANT_A, SCOPE, initial.last_activation_event_id, events) is not None
    assert ActivationRegistry.get_current_slot(TENANT_A, SCOPE, slots, events) == initial

    replay = _tx(client, lambda s: activate_tenant_inbound_provider_policy(**_common_kwargs(ctx_activate, evidence, policies, configs, events, slots, s, "decision-initial", "key-initial", policy_a, None, None, "initial")))
    assert replay == initial and events.count_documents({"tenant_id": TENANT_A}) == 1
    _evidence(evidence, tenant=TENANT_A, decision="decision-divergent", operation=ACTIVATE_OPERATION, permission=ACTIVATE_PERMISSION, business_role=ACTIVATE_BUSINESS_ROLE, auth_role=ACTIVATE_AUTH_ROLE, key="key-initial", kind=TenantInboundProviderPolicyActivationEventKind.ACTIVATE, expected_revision=None, prior=None, target=_reference(policy_b), reason="different")
    with pytest.raises(TenantInboundProviderPolicyActivationIssuanceError):
        _tx(client, lambda s: activate_tenant_inbound_provider_policy(**_common_kwargs(ctx_activate, evidence, policies, configs, events, slots, s, "decision-divergent", "key-initial", policy_b, None, None, "different")))
    assert events.count_documents({"tenant_id": TENANT_A}) == 1

    _evidence(evidence, tenant=TENANT_A, decision="decision-supersede", operation=ACTIVATE_OPERATION, permission=ACTIVATE_PERMISSION, business_role=ACTIVATE_BUSINESS_ROLE, auth_role=ACTIVATE_AUTH_ROLE, key="key-supersede", kind=TenantInboundProviderPolicyActivationEventKind.SUPERSEDE, expected_revision=0, prior=pa, target=_reference(policy_b), reason="replace")
    superseded = _tx(client, lambda s: supersede_tenant_inbound_provider_policy(**_common_kwargs(ctx_activate, evidence, policies, configs, events, slots, s, "decision-supersede", "key-supersede", policy_b, 0, pa, "replace")))
    assert superseded.current_activation_revision == 1 and superseded.current_active_policy == _reference(policy_b)
    assert events.count_documents({"tenant_id": TENANT_A}) == 2

    pb = _reference(policy_b)
    _evidence(evidence, tenant=TENANT_A, decision="decision-deactivate", operation=DEACTIVATE_OPERATION, permission=DEACTIVATE_PERMISSION, business_role=DEACTIVATE_BUSINESS_ROLE, auth_role=DEACTIVATE_AUTH_ROLE, key="key-deactivate", kind=TenantInboundProviderPolicyActivationEventKind.DEACTIVATE, expected_revision=1, prior=pb, target=None, reason="clear")
    cleared = _tx(client, lambda s: deactivate_tenant_inbound_provider_policy(**_common_kwargs(ctx_activate, evidence, policies, configs, events, slots, s, "decision-deactivate", "key-deactivate", policy_b, 1, pb, "clear", include_target_policy_fingerprint=False)))
    assert cleared.current_activation_revision == 2 and cleared.current_active_policy is None

    # Re-activation reuses the one slot document and advances exactly once.
    _evidence(evidence, tenant=TENANT_A, decision="decision-reactivate", operation=ACTIVATE_OPERATION, permission=ACTIVATE_PERMISSION, business_role=ACTIVATE_BUSINESS_ROLE, auth_role=ACTIVATE_AUTH_ROLE, key="key-reactivate", kind=TenantInboundProviderPolicyActivationEventKind.ACTIVATE, expected_revision=2, prior=None, target=pa, reason="reactivate")
    reactivated = _tx(client, lambda s: activate_tenant_inbound_provider_policy(**_common_kwargs(ctx_activate, evidence, policies, configs, events, slots, s, "decision-reactivate", "key-reactivate", policy_a, 2, None, "reactivate")))
    assert reactivated.current_activation_revision == 3 and slots.count_documents({"tenant_id": TENANT_A}) == 1

    # Emergency disable is a distinct operation/authority and clears the slot.
    _evidence(evidence, tenant=TENANT_A, decision="decision-emergency", operation=EMERGENCY_DISABLE_OPERATION, permission=EMERGENCY_DISABLE_PERMISSION, business_role=EMERGENCY_DISABLE_BUSINESS_ROLE, auth_role=EMERGENCY_DISABLE_AUTH_ROLE, key="key-emergency", kind=TenantInboundProviderPolicyActivationEventKind.EMERGENCY_DISABLE, expected_revision=3, prior=pa, target=None, reason="incident")
    ctx_security = _context(TENANT_A, EMERGENCY_DISABLE_BUSINESS_ROLE, EMERGENCY_DISABLE_AUTH_ROLE)
    emergency = _tx(client, lambda s: emergency_disable_tenant_inbound_provider_policy(**_common_kwargs(ctx_security, evidence, policies, configs, events, slots, s, "decision-emergency", "key-emergency", policy_a, 3, pa, "incident", include_target_policy_fingerprint=False)))
    assert emergency.current_activation_revision == 4 and emergency.current_active_policy is None
    emergency_slot = ActivationRegistry.get_current_slot(TENANT_A, SCOPE, slots, events)
    assert emergency_slot is not None and emergency_slot.current_active_policy is None

    # Historical replay after later events returns current canonical slot.
    historical = _tx(client, lambda s: activate_tenant_inbound_provider_policy(**_common_kwargs(ctx_activate, evidence, policies, configs, events, slots, s, "decision-initial", "key-initial", policy_a, None, None, "initial")))
    assert historical == emergency and historical.current_activation_revision == 4

    # Tenant-scoped same keys are independent.
    config_other = _seed_configuration(configs, TENANT_B, "config-b-tenant")
    policy_other = _policy(TENANT_B, "policy-a", config_other)
    TenantInboundProviderPolicyRegistry.create(policy_other, policies)
    other_ref = _reference(policy_other)
    ctx_other = _context(TENANT_B, ACTIVATE_BUSINESS_ROLE, ACTIVATE_AUTH_ROLE)
    _evidence(evidence, tenant=TENANT_B, decision="decision-other", operation=ACTIVATE_OPERATION, permission=ACTIVATE_PERMISSION, business_role=ACTIVATE_BUSINESS_ROLE, auth_role=ACTIVATE_AUTH_ROLE, key="key-initial", kind=TenantInboundProviderPolicyActivationEventKind.ACTIVATE, expected_revision=None, prior=None, target=other_ref, reason="initial")
    other = _tx(client, lambda s: activate_tenant_inbound_provider_policy(**_common_kwargs(ctx_other, evidence, policies, configs, events, slots, s, "decision-other", "key-initial", policy_other, None, None, "initial")))
    assert other.tenant_id == TENANT_B and events.count_documents({"lifecycle_idempotency_key": "key-initial"}) == 2
    assert ActivationRegistry.get_event_by_idempotency_key(TENANT_A, SCOPE, "key-initial", events) is not None
    assert ActivationRegistry.get_event_by_idempotency_key(TENANT_B, SCOPE, "key-initial", events) is not None

    # Real unique-index contention rejects duplicate event identity/revision/slot.
    raw_event = events.find_one({"tenant_id": TENANT_A, "lifecycle_idempotency_key": "key-reactivate"})
    assert raw_event is not None
    with pytest.raises(DuplicateKeyError):
        events.insert_one({k: v for k, v in raw_event.items() if k != "_id"})
    raw_slot = slots.find_one({"tenant_id": TENANT_A, "policy_scope": SCOPE.value})
    assert raw_slot is not None
    with pytest.raises(DuplicateKeyError):
        slots.insert_one({k: v for k, v in raw_slot.items() if k != "_id"})

    # Non-enabled configuration is rejected before event/slot mutation.
    disabled_ref = _reference(policy_disabled)
    _evidence(evidence, tenant=TENANT_A, decision="decision-disabled", operation=ACTIVATE_OPERATION, permission=ACTIVATE_PERMISSION, business_role=ACTIVATE_BUSINESS_ROLE, auth_role=ACTIVATE_AUTH_ROLE, key="key-disabled", kind=TenantInboundProviderPolicyActivationEventKind.ACTIVATE, expected_revision=None, prior=None, target=disabled_ref, reason="disabled")
    before = events.count_documents({"tenant_id": TENANT_A})
    with pytest.raises(TenantInboundProviderPolicyActivationIssuanceError):
        _tx(client, lambda s: activate_tenant_inbound_provider_policy(**_common_kwargs(ctx_activate, evidence, policies, configs, events, slots, s, "decision-disabled", "key-disabled", policy_disabled, None, None, "disabled")))
    assert events.count_documents({"tenant_id": TENANT_A}) == before

    # Corrupt event and slot strict hydration fail closed, with no auto-repair.
    event_id = raw_event["activation_event_id"]
    events.update_one({"_id": raw_event["_id"]}, {"$set": {"reason_reference": "corrupt"}})
    with pytest.raises(TenantInboundProviderPolicyActivationRegistryRecordInvalidError):
        ActivationRegistry.get_event(TENANT_A, SCOPE, event_id, events)
    events.replace_one({"_id": raw_event["_id"]}, raw_event)
    slots.update_one({"_id": raw_slot["_id"]}, {"$set": {"last_activation_event_fingerprint": "b" * 128}})
    with pytest.raises(TenantInboundProviderPolicyActivationRegistryRecordInvalidError):
        ActivationRegistry.get_current_slot(TENANT_A, SCOPE, slots, events)
    slots.replace_one({"_id": raw_slot["_id"]}, raw_slot)

    # Two real caller transactions race on the same expected current state.
    race_policy = _policy(TENANT_A, "policy-race", config_a)
    TenantInboundProviderPolicyRegistry.create(race_policy, policies)
    current = ActivationRegistry.get_current_slot(TENANT_A, SCOPE, slots, events)
    assert current is not None
    race_prior = current.current_active_policy
    assert race_prior is None  # emergency-disabled state is the shared baseline
    # Reactivate to establish a shared active prior for the race.
    _evidence(evidence, tenant=TENANT_A, decision="decision-race-base", operation=ACTIVATE_OPERATION, permission=ACTIVATE_PERMISSION, business_role=ACTIVATE_BUSINESS_ROLE, auth_role=ACTIVATE_AUTH_ROLE, key="key-race-base", kind=TenantInboundProviderPolicyActivationEventKind.ACTIVATE, expected_revision=4, prior=None, target=pa, reason="race-base")
    base = _tx(client, lambda s: activate_tenant_inbound_provider_policy(**_common_kwargs(ctx_activate, evidence, policies, configs, events, slots, s, "decision-race-base", "key-race-base", policy_a, 4, None, "race-base")))
    assert base.current_active_policy == pa
    policy_c_ref = _reference(policy_c)
    for decision, key, target in (("decision-race-b", "key-race-b", policy_b), ("decision-race-c", "key-race-c", policy_c)):
        _evidence(evidence, tenant=TENANT_A, decision=decision, operation=ACTIVATE_OPERATION, permission=ACTIVATE_PERMISSION, business_role=ACTIVATE_BUSINESS_ROLE, auth_role=ACTIVATE_AUTH_ROLE, key=key, kind=TenantInboundProviderPolicyActivationEventKind.SUPERSEDE, expected_revision=5, prior=pa, target=_reference(target), reason="race")
    barrier = Barrier(2)
    def race(target: TenantInboundProviderPolicy, decision: str, key: str) -> str:
        try:
            with client.start_session() as session:
                session.start_transaction()
                barrier.wait()
                supersede_tenant_inbound_provider_policy(**_common_kwargs(ctx_activate, evidence, policies, configs, events, slots, session, decision, key, target, 5, pa, "race"))
                session.commit_transaction()
                return "committed"
        except (PyMongoError, TenantInboundProviderPolicyActivationIssuanceError, TenantInboundProviderPolicyActivationRegistryCASConflictError):
            return "rejected"
    with ThreadPoolExecutor(max_workers=2) as pool:
        outcomes = list(pool.map(lambda args: race(*args), ((policy_b, "decision-race-b", "key-race-b"), (policy_c, "decision-race-c", "key-race-c"))))
    assert outcomes.count("committed") == 1 and outcomes.count("rejected") == 1
    final = ActivationRegistry.get_current_slot(TENANT_A, SCOPE, slots, events)
    assert final is not None and final.current_activation_revision == 6
    assert events.count_documents({"tenant_id": TENANT_A}) == 7


# ARTIFACT: test_tenant_inbound_provider_policy_activation_real_mongo.py
# VERSION: v1.0.0-M11-R8-R3B-P8-P3C-P8-R2D
# AUTHORITY BOUNDARY: host-backed evidence only; no provider binding or financial authority.
# TENANT POSTURE: every durable assertion is tenant/scope constrained.
# FAIL-CLOSED POSTURE: topology, index, replay, CAS, rollback, and hydration drift fails.
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively.
# END OF WILSY OS SOVEREIGN ARTIFACT
