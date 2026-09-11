"""WILSY OS host-backed tenant inbound merchant-configuration certificate.

TITLE: Tenant Inbound Merchant Configuration Lifecycle — Real Mongo Certificate
VERSION: v1.2.2-M11-R8-R3B-P8-P2-P0-R1
AUTHORITY: Wilsy OS Core Governance; host-backed persistence evidence only.
EPITOME: Certify durable registration, ordinary lifecycle, compromise,
         remediation, replay, tenant isolation, CAS, strict hydration, and
         caller-visible commit uncertainty.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tests/integration/test_tenant_inbound_merchant_configuration_lifecycle_real_mongo.py
COLLABORATION / OWNERSHIP: SaaS lifecycle certificate owner; production issuer,
                            domain, registry, and generic authorization remain
                            separate canonical owners. M2 extends this M1 owner
                            for real-driver commit-uncertainty evidence.
CERTIFICATION / UPDATE DATE: 2026-09-09
CHANGELOG: v1.2.2-M11-R8-R3B-P8-P2-P0-R1 certifies the same-document
           lifecycle idempotency projection and migration-safe tenant-wide
           uniqueness while preserving the existing host-backed lifecycle.
v1.1.0-M11-R8-R3B-P8-P3B-I2-M2 extends the host-backed lifecycle
           certificate with a bounded real-driver commit-uncertainty replay:
           the server commit is issued first, the caller observes an
           UnknownTransactionCommitResult boundary, and a fresh transaction
           exact-replays the same tenant/key/authorization intent.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2.
SECURITY / PRIVACY POSTURE: Synthetic opaque identifiers only; no raw secret,
                             provider credential, KMS, PayFast, or PayShap call.
TENANT BOUNDARY: Every configuration, evidence, replay, and CAS assertion is
                 bound to an explicit tenant; cross-tenant keys are isolated.
AUTHORITY BOUNDARY: This file certifies existing owners; it creates no policy,
                    provider binding, checkout, payment, or remediation truth.
FINANCIAL AUTHORITY BOUNDARY: No execution, settlement, invoice, receivable, or
                              ClientInvoice authority; Kennel EOS remains exclusive.
TRANSACTION BOUNDARY: Tests start, commit, abort, and dispose every session;
                      production issuers never own transaction lifecycle.
FAIL-CLOSED DECLARATION: Host absence, wrong replica set, stale CAS, divergent
                          replay, corruption, or transaction drift fails tests.
"""
from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass
from datetime import datetime, timezone
from threading import Barrier
from typing import Any, Callable, NoReturn
from uuid import uuid4
import os

import pytest
from pymongo import MongoClient
from pymongo.client_session import ClientSession
from pymongo.collection import Collection
from pymongo.errors import ConnectionFailure, PyMongoError

from tools.eos.auth.permission_namespace import VERSION as PERMISSION_NAMESPACE_VERSION
from tools.eos.auth.principal_authority import PrincipalAuthority
from tools.eos.auth.principal_status import PrincipalStatus
from tools.eos.auth.role_assignment import RoleAssignmentAuthority, RoleAssignmentStatus
from tools.eos.auth.role_assignment_repository import RoleAssignmentNotFoundError
from tools.eos.auth.tenant_authorization import VERSION as AUTHORIZATION_VERSION
from tools.eos.auth.tenant_authorization_decision_evidence import TenantAuthorizationDecisionEvidence
from tools.eos.auth.tenant_authorization_decision_evidence_registry import TenantAuthorizationDecisionEvidenceRegistry
from tools.eos.auth.tenant_authority_policy import VERSION as TENANT_AUTHORITY_POLICY_VERSION
from tools.eos.auth.roles import VERSION as ROLES_VERSION
from tools.eos.auth.tenant_membership import TenantMembershipAuthority, TenantMembershipStatus
from tools.eos.saas.billing.tenant_inbound_merchant_configuration_issuance import (
    COMPROMISE_BUSINESS_ROLE,
    COMPROMISE_OPERATION,
    COMPROMISE_PERMISSION,
    LIFECYCLE_BUSINESS_ROLE,
    LIFECYCLE_OPERATION,
    LIFECYCLE_PERMISSION,
    REGISTER_BUSINESS_ROLE,
    REGISTER_OPERATION,
    REGISTER_PERMISSION,
    REMEDIATION_BUSINESS_ROLE,
    REMEDIATION_OPERATION,
    REMEDIATION_PERMISSION,
    TenantInboundMerchantConfigurationIssuanceError,
    _lifecycle_fingerprint,
    _lifecycle_payload,
    _lifecycle_subject,
    canonical_registration_intent_fingerprint,
    register_tenant_inbound_merchant_configuration,
    registration_subject_reference,
    transition_tenant_inbound_merchant_configuration,
    compromise_tenant_inbound_merchant_configuration,
    remediate_tenant_inbound_merchant_configuration,
)
from tools.eos.saas.billing.tenant_inbound_merchant_configuration_registry import (
    EnablementState,
    TenantInboundMerchantConfigurationRegistryError,
    TenantInboundMerchantConfigurationRegistry,
    TenantInboundMerchantConfigurationPersistedRecordInvalidError,
    TenantInboundMerchantConfigurationReplayConflictError,
    TenantInboundMerchantConfigurationTransitionConflictError,
)
from tools.eos.saas.billing.migrations.tenant_inbound_merchant_configuration_lifecycle_idempotency_projection import (
    LifecycleIdempotencyProjectionMigrationError,
    migrate as migrate_lifecycle_idempotency_projection,
)
from tools.eos.saas.domain.tenant_inbound_merchant_configuration import (
    InboundMerchantProviderId,
    TenantInboundMerchantConfiguration,
)


URI = "mongodb://127.0.0.1:27027/?replicaSet=wilsyVendorCertRS"
FIXED_AT = datetime(2026, 9, 9, 10, 0, tzinfo=timezone.utc)
CONFIGURATION_COLLECTION = "tenant_inbound_merchant_configurations"
EVIDENCE_COLLECTION = "tenant_authorization_decision_evidence"
PRINCIPAL_ID = "principal-real-mongo-cert"
TENANT_A = "tenant-real-mongo-a"
TENANT_B = "tenant-real-mongo-b"


@dataclass(frozen=True)
class _AuthorityContext:
    principal: PrincipalAuthority
    membership: TenantMembershipAuthority
    roles: dict[str, RoleAssignmentAuthority]

    def principal_repository(self) -> Any:
        return _PrincipalRepository(self.principal)

    def membership_repository(self) -> Any:
        return _MembershipRepository(self.membership)

    def role_repository(self) -> Any:
        return _RoleRepository(self.roles)


class _PrincipalRepository:
    def __init__(self, value: PrincipalAuthority) -> None:
        self._value = value

    def resolve(self, principal_id: str, *, session: Any = None) -> PrincipalAuthority:
        if principal_id != self._value.principal_id:
            from tools.eos.auth.principal_authority_repository import PrincipalAuthorityNotFoundError

            raise PrincipalAuthorityNotFoundError("PRINCIPAL_AUTHORITY_NOT_FOUND")
        return self._value


class _MembershipRepository:
    def __init__(self, value: TenantMembershipAuthority) -> None:
        self._value = value

    def resolve(self, principal_id: str, tenant_id: str, *, session: Any = None) -> TenantMembershipAuthority:
        if (principal_id, tenant_id) != (self._value.principal_id, self._value.tenant_id):
            from tools.eos.auth.tenant_membership_repository import TenantMembershipNotFoundError

            raise TenantMembershipNotFoundError("TENANT_MEMBERSHIP_NOT_FOUND")
        return self._value


class _RoleRepository:
    def __init__(self, values: dict[str, RoleAssignmentAuthority]) -> None:
        self._values = values

    def resolve(self, principal_id: str, tenant_id: str, role_id: str, *, session: Any = None) -> RoleAssignmentAuthority:
        value = self._values.get(role_id)
        if value is None or (value.principal_id, value.tenant_id) != (principal_id, tenant_id):
            raise RoleAssignmentNotFoundError("ROLE_ASSIGNMENT_NOT_FOUND")
        return value


class _DurableEvidenceReader:
    """Strictly hydrate evidence from the real collection on the caller session."""

    def __init__(self, collection: Collection) -> None:
        self._collection = collection

    def get(self, *, tenant_id: str, authorization_decision_id: str, session: ClientSession) -> TenantAuthorizationDecisionEvidence:
        row = self._collection.find_one(
            {"tenant_id": tenant_id, "authorization_decision_id": authorization_decision_id},
            session=session,
        )
        assert row is not None
        body = dict(row)
        body.pop("_id", None)
        return TenantAuthorizationDecisionEvidence.from_persisted(body)


class _UnknownCommitResult(ConnectionFailure):
    """Caller-visible uncertainty raised after a real server commit is issued."""

    def has_error_label(self, label: str) -> bool:
        """Expose MongoDB's canonical unknown-commit label to the harness."""
        return label == "UnknownTransactionCommitResult"


def _context(tenant_id: str, business_role: str, authorization_role: str) -> _AuthorityContext:
    return _AuthorityContext(
        principal=PrincipalAuthority(PRINCIPAL_ID, PrincipalStatus.ACTIVE, 0),
        membership=TenantMembershipAuthority(PRINCIPAL_ID, tenant_id, TenantMembershipStatus.ACTIVE, 0),
        roles={
            business_role: RoleAssignmentAuthority(PRINCIPAL_ID, tenant_id, business_role, RoleAssignmentStatus.ACTIVE, 0),
            authorization_role: RoleAssignmentAuthority(PRINCIPAL_ID, tenant_id, authorization_role, RoleAssignmentStatus.ACTIVE, 0),
        },
    )


def _evidence(
    *, collection: Collection, tenant_id: str, decision_id: str, operation: str,
    permission: str, business_role: str, authorization_role: str,
    subject_reference: str, subject_fingerprint: str, idempotency_key: str,
) -> TenantAuthorizationDecisionEvidence:
    evidence = TenantAuthorizationDecisionEvidence(
        tenant_id=tenant_id,
        authorization_decision_id=decision_id,
        principal_id=PRINCIPAL_ID,
        operation=operation,
        permission=permission,
        business_role=business_role,
        authorization_role=authorization_role,
        membership_revision=0,
        role_assignment_revision=0,
        subject_reference=subject_reference,
        subject_evidence_fingerprint=subject_fingerprint,
        permission_namespace_version=PERMISSION_NAMESPACE_VERSION,
        authorization_role_policy_version=ROLES_VERSION,
        tenant_business_role_policy_version=TENANT_AUTHORITY_POLICY_VERSION,
        tenant_authorization_composition_version=AUTHORIZATION_VERSION,
        idempotency_key=idempotency_key,
        authorized_at=FIXED_AT,
    )
    collection.insert_one(evidence.to_persisted())
    return evidence


def _transaction(client: MongoClient, operation: Callable[[ClientSession], Any]) -> Any:
    """Run one caller-owned transaction and abort on every operation failure."""
    with client.start_session() as session:
        session.start_transaction()
        try:
            result = operation(session)
            session.commit_transaction()
            return result
        except BaseException:
            if session.in_transaction:
                session.abort_transaction()
            raise


def _commit_then_report_unknown(session: ClientSession) -> NoReturn:
    """Issue a real commit, then model the caller's ambiguous network outcome."""
    session.commit_transaction()
    raise _UnknownCommitResult("commit outcome is unknown to the caller")


@pytest.fixture()
def mongo_db() -> Any:
    """Require the approved host replica set and yield a UUID-isolated database."""
    configured = os.environ.get("TEST_VENDOR_MONGO_URI")
    assert configured, "TEST_VENDOR_MONGO_URI is required for host certification"
    client = MongoClient(configured, serverSelectionTimeoutMS=5000, retryWrites=True)
    hello = client.admin.command("hello")
    assert hello.get("setName") == "wilsyVendorCertRS"
    assert hello.get("isWritablePrimary") is True
    database = client[f"wilsy_inbound_lifecycle_cert_{uuid4().hex}"]
    configurations = database[CONFIGURATION_COLLECTION]
    evidence = database[EVIDENCE_COLLECTION]
    TenantInboundMerchantConfigurationRegistry.ensure_indexes(configurations)
    TenantAuthorizationDecisionEvidenceRegistry(evidence, principal_repository=_PrincipalRepository(PrincipalAuthority(PRINCIPAL_ID, PrincipalStatus.ACTIVE, 0))).ensure_indexes()
    try:
        yield client, database, configurations, evidence
    finally:
        client.drop_database(database.name)
        client.close()


def _register_seed(client: MongoClient, configurations: Collection, evidence: Collection, tenant_id: str = TENANT_A, suffix: str = "a") -> TenantInboundMerchantConfiguration:
    configuration_id = f"merchant-config-{suffix}"
    register_key = f"register-key-{suffix}"
    options = {"mode": "live", "merchant_name": f"Merchant {suffix}", "currency": "ZAR"}
    fingerprint = canonical_registration_intent_fingerprint(
        tenant_id=tenant_id, provider_id=InboundMerchantProviderId.PAYFAST,
        merchant_account_id=f"merchant-account-{suffix}", merchant_configuration_id=configuration_id,
        merchant_configuration_version=1, non_secret_provider_options=options,
        credential_secret_reference=f"secret-ref-{suffix}", register_idempotency_key=register_key,
    )
    _evidence(
        collection=evidence, tenant_id=tenant_id, decision_id=f"decision-register-{suffix}",
        operation=REGISTER_OPERATION, permission=REGISTER_PERMISSION,
        business_role=REGISTER_BUSINESS_ROLE, authorization_role="INBOUND_MERCHANT_CONFIGURATION_ADMIN",
        subject_reference=registration_subject_reference(fingerprint), subject_fingerprint=fingerprint,
        idempotency_key=f"evidence-register-{suffix}",
    )
    context = _context(tenant_id, REGISTER_BUSINESS_ROLE, "INBOUND_MERCHANT_CONFIGURATION_ADMIN")
    return _transaction(client, lambda session: register_tenant_inbound_merchant_configuration(
        tenant_id=tenant_id, provider_id=InboundMerchantProviderId.PAYFAST,
        merchant_account_id=f"merchant-account-{suffix}", merchant_configuration_id=configuration_id,
        merchant_configuration_version=1, non_secret_provider_options=options,
        credential_secret_reference=f"secret-ref-{suffix}", register_idempotency_key=register_key,
        authorization_decision_id=f"decision-register-{suffix}", session=session,
        configuration_collection=configurations, authorization_evidence_collection=evidence,
        principal_repository=context.principal_repository(), membership_repository=context.membership_repository(),
        role_assignment_repository=context.role_repository(), business_role_repository=context.role_repository(),
        authorization_evidence_registry=_DurableEvidenceReader(evidence), clock=lambda: FIXED_AT,
    )).configuration


def _lifecycle_evidence(collection: Collection, configuration: TenantInboundMerchantConfiguration, *, decision_id: str, key: str, operation: str, permission: str, business_role: str, authorization_role: str, prior_revision: int, prior_state: EnablementState, target_state: EnablementState, reason: str) -> None:
    payload = _lifecycle_payload(
        tenant_id=configuration.tenant_id, merchant_configuration_id=configuration.merchant_configuration_id,
        merchant_configuration_version=configuration.merchant_configuration_version,
        configuration_fingerprint=configuration.fingerprint, expected_prior_lifecycle_revision=prior_revision,
        expected_prior_state=prior_state, target_state=target_state, reason_reference=reason,
        lifecycle_idempotency_key=key,
    )
    fingerprint = _lifecycle_fingerprint(payload)
    prefix = {LIFECYCLE_OPERATION: "lifecycle-transition", COMPROMISE_OPERATION: "compromise", REMEDIATION_OPERATION: "remediate"}[operation]
    _evidence(
        collection=collection, tenant_id=configuration.tenant_id, decision_id=decision_id,
        operation=operation, permission=permission, business_role=business_role,
        authorization_role=authorization_role, subject_reference=_lifecycle_subject(prefix, fingerprint),
        subject_fingerprint=fingerprint, idempotency_key=f"evidence-{key}",
    )


def _transition_kwargs(configuration: TenantInboundMerchantConfiguration, session: ClientSession, configurations: Collection, evidence: Collection, context: _AuthorityContext, decision_id: str, key: str, prior_revision: int, prior_state: EnablementState, target_state: EnablementState, reason: str, operation: str) -> dict[str, Any]:
    common = dict(
        tenant_id=configuration.tenant_id, merchant_configuration_id=configuration.merchant_configuration_id,
        merchant_configuration_version=configuration.merchant_configuration_version,
        expected_configuration_fingerprint=configuration.fingerprint, expected_lifecycle_revision=prior_revision,
        expected_prior_state=prior_state, reason_reference=reason,
        authorization_decision_id=decision_id, session=session, configuration_collection=configurations,
        authorization_evidence_collection=evidence, principal_repository=context.principal_repository(),
        membership_repository=context.membership_repository(), role_assignment_repository=context.role_repository(),
        business_role_repository=context.role_repository(), authorization_evidence_registry=_DurableEvidenceReader(evidence),
        clock=lambda: FIXED_AT,
    )
    if operation == LIFECYCLE_OPERATION:
        common.update(target_state=target_state, lifecycle_idempotency_key=key)
    elif operation == COMPROMISE_OPERATION:
        common.update(security_event_idempotency_key=key)
    else:
        common.update(lifecycle_idempotency_key=key)
    return common


def test_host_preconditions_indexes_and_durable_registration(mongo_db: Any) -> None:
    client, _, configurations, evidence = mongo_db
    indexes = {item["name"]: item for item in configurations.list_indexes()}
    assert "tenant_lifecycle_idempotency_projection_unique" in indexes
    assert indexes["tenant_lifecycle_idempotency_projection_unique"]["key"] == {"configuration.tenant_id": 1, "lifecycle_idempotency_keys": 1}
    assert indexes["tenant_lifecycle_idempotency_projection_unique"]["unique"] is True
    assert indexes["tenant_lifecycle_idempotency_projection_unique"]["partialFilterExpression"] == {"lifecycle_idempotency_keys.0": {"$exists": True}}
    assert "configuration.merchant_configuration_id" not in indexes["tenant_lifecycle_idempotency_projection_unique"]["key"]
    assert "tenant_lifecycle_idempotency_unique" not in indexes
    configuration = _register_seed(client, configurations, evidence)
    row = configurations.find_one({"configuration.tenant_id": TENANT_A, "configuration.merchant_configuration_id": configuration.merchant_configuration_id})
    assert row is not None
    record = TenantInboundMerchantConfigurationRegistry.get(TENANT_A, configuration.merchant_configuration_id, 1, configurations)
    assert record is not None
    assert record.state is EnablementState.DISABLED
    assert record.revision == 0
    assert len(record.history) == 1
    assert record.history[0].authorization_reference == "tenant-authorization-decision:decision-register-a"
    assert len(record.history[0].authorization_evidence_fingerprint or "") == 128
    assert evidence.count_documents({"tenant_id": TENANT_A}) == 1


def test_real_mongo_projection_tracks_history_and_migration_backfills_old_shape(mongo_db: Any) -> None:
    client, database, configurations, evidence = mongo_db
    configuration = _register_seed(client, configurations, evidence)
    row = configurations.find_one({"configuration.tenant_id": TENANT_A, "configuration.merchant_configuration_id": configuration.merchant_configuration_id})
    assert row is not None
    assert row["lifecycle_idempotency_keys"] == []
    ordinary_context = _context(TENANT_A, LIFECYCLE_BUSINESS_ROLE, "INBOUND_MERCHANT_CONFIGURATION_ADMIN")
    _lifecycle_evidence(evidence, configuration, decision_id="decision-projection", key="projection-key", operation=LIFECYCLE_OPERATION, permission=LIFECYCLE_PERMISSION, business_role=LIFECYCLE_BUSINESS_ROLE, authorization_role="INBOUND_MERCHANT_CONFIGURATION_ADMIN", prior_revision=0, prior_state=EnablementState.DISABLED, target_state=EnablementState.ENABLED, reason="projection")
    enabled = _transaction(client, lambda session: transition_tenant_inbound_merchant_configuration(**_transition_kwargs(configuration, session, configurations, evidence, ordinary_context, "decision-projection", "projection-key", 0, EnablementState.DISABLED, EnablementState.ENABLED, "projection", LIFECYCLE_OPERATION)))
    assert enabled.history[-1].lifecycle_idempotency_key == "projection-key"
    stored = configurations.find_one({"configuration.tenant_id": TENANT_A, "configuration.merchant_configuration_id": configuration.merchant_configuration_id})
    assert stored is not None and stored["lifecycle_idempotency_keys"] == ["projection-key"]
    assert stored["lifecycle_history"][0].get("lifecycle_idempotency_key") is None

    legacy = database["tenant_inbound_merchant_configurations_legacy_projection"]
    legacy.drop()
    legacy.create_index([("configuration.tenant_id", 1), ("lifecycle_history.lifecycle_idempotency_key", 1)], unique=True, name="tenant_lifecycle_idempotency_unique", partialFilterExpression={"lifecycle_history.lifecycle_idempotency_key": {"$type": "string"}})
    legacy_doc = dict(stored)
    legacy_doc.pop("lifecycle_idempotency_keys", None)
    legacy.insert_one(legacy_doc)
    report = migrate_lifecycle_idempotency_projection(legacy)
    assert report["rows_backfilled"] == 1
    migrated = legacy.find_one({"_id": legacy_doc["_id"]})
    assert migrated is not None and migrated["lifecycle_idempotency_keys"] == ["projection-key"]
    migrated_indexes = {item["name"]: item for item in legacy.list_indexes()}
    assert "tenant_lifecycle_idempotency_projection_unique" in migrated_indexes
    assert "tenant_lifecycle_idempotency_unique" not in migrated_indexes
    assert migrate_lifecycle_idempotency_projection(legacy)["rows_backfilled"] == 1


def test_real_mongo_migration_duplicate_preflight_fails_before_any_mutation(mongo_db: Any) -> None:
    _, database, _, _ = mongo_db
    legacy = database["tenant_inbound_merchant_configurations_duplicate_preflight"]
    legacy.drop()
    first = {"configuration": {"tenant_id": TENANT_A, "merchant_configuration_id": "legacy-a", "merchant_configuration_version": 1}, "lifecycle_history": [{"lifecycle_idempotency_key": "duplicate-key"}]}
    second = {"configuration": {"tenant_id": TENANT_A, "merchant_configuration_id": "legacy-b", "merchant_configuration_version": 1}, "lifecycle_history": [{"lifecycle_idempotency_key": "duplicate-key"}]}
    legacy.insert_many([first, second])
    before_indexes = list(legacy.list_indexes())
    before = list(legacy.find({}, {"_id": 0}))
    with pytest.raises(LifecycleIdempotencyProjectionMigrationError, match="CROSS_DOCUMENT_LIFECYCLE_IDEMPOTENCY_CONFLICT"):
        migrate_lifecycle_idempotency_projection(legacy)
    assert list(legacy.list_indexes()) == before_indexes
    assert list(legacy.find({}, {"_id": 0})) == before
    assert not any(item.get("name") == "tenant_lifecycle_idempotency_projection_unique" for item in legacy.list_indexes())


def test_real_mongo_ordinary_compromise_remediation_and_exact_replay(mongo_db: Any) -> None:
    client, _, configurations, evidence = mongo_db
    configuration = _register_seed(client, configurations, evidence)
    initial = TenantInboundMerchantConfigurationRegistry.get(TENANT_A, configuration.merchant_configuration_id, 1, configurations)
    assert initial is not None and initial.state is EnablementState.DISABLED and initial.revision == 0
    ordinary_context = _context(TENANT_A, LIFECYCLE_BUSINESS_ROLE, "INBOUND_MERCHANT_CONFIGURATION_ADMIN")
    _lifecycle_evidence(evidence, configuration, decision_id="decision-enable", key="enable-key", operation=LIFECYCLE_OPERATION, permission=LIFECYCLE_PERMISSION, business_role=LIFECYCLE_BUSINESS_ROLE, authorization_role="INBOUND_MERCHANT_CONFIGURATION_ADMIN", prior_revision=0, prior_state=EnablementState.DISABLED, target_state=EnablementState.ENABLED, reason="enable-approved")
    enabled = _transaction(client, lambda session: transition_tenant_inbound_merchant_configuration(**_transition_kwargs(configuration, session, configurations, evidence, ordinary_context, "decision-enable", "enable-key", 0, EnablementState.DISABLED, EnablementState.ENABLED, "enable-approved", LIFECYCLE_OPERATION)))
    assert (enabled.state, enabled.revision, len(enabled.history)) == (EnablementState.ENABLED, 1, 2)
    assert enabled.history[0] == initial.history[0]
    assert enabled.history[-1].authorization_reference == "tenant-authorization-decision:decision-enable"
    assert len(enabled.history[-1].authorization_evidence_fingerprint or "") == 128
    assert enabled.history[-1].lifecycle_idempotency_key == "enable-key"
    replay = _transaction(client, lambda session: transition_tenant_inbound_merchant_configuration(**_transition_kwargs(configuration, session, configurations, evidence, ordinary_context, "decision-enable", "enable-key", 0, EnablementState.DISABLED, EnablementState.ENABLED, "enable-approved", LIFECYCLE_OPERATION)))
    assert replay.state is EnablementState.ENABLED and replay.revision == 1 and len(replay.history) == 2
    assert replay.history == enabled.history
    security_context = _context(TENANT_A, COMPROMISE_BUSINESS_ROLE, "INBOUND_PROVIDER_SECURITY_ADMIN")
    _lifecycle_evidence(evidence, configuration, decision_id="decision-compromise", key="compromise-key", operation=COMPROMISE_OPERATION, permission=COMPROMISE_PERMISSION, business_role=COMPROMISE_BUSINESS_ROLE, authorization_role="INBOUND_PROVIDER_SECURITY_ADMIN", prior_revision=1, prior_state=EnablementState.ENABLED, target_state=EnablementState.COMPROMISED, reason="security-event")
    compromised = _transaction(client, lambda session: compromise_tenant_inbound_merchant_configuration(**_transition_kwargs(configuration, session, configurations, evidence, security_context, "decision-compromise", "compromise-key", 1, EnablementState.ENABLED, EnablementState.COMPROMISED, "security-event", COMPROMISE_OPERATION)))
    assert (compromised.state, compromised.revision, len(compromised.history)) == (EnablementState.COMPROMISED, 2, 3)
    assert compromised.history[-1].authorization_reference == "tenant-authorization-decision:decision-compromise"
    assert len(compromised.history[-1].authorization_evidence_fingerprint or "") == 128
    assert compromised.history[-1].reason_reference == "security-event"
    assert compromised.history[-1].lifecycle_idempotency_key == "compromise-key"
    _lifecycle_evidence(evidence, configuration, decision_id="decision-remediate", key="remediate-key", operation=REMEDIATION_OPERATION, permission=REMEDIATION_PERMISSION, business_role=REMEDIATION_BUSINESS_ROLE, authorization_role="INBOUND_PROVIDER_SECURITY_ADMIN", prior_revision=2, prior_state=EnablementState.COMPROMISED, target_state=EnablementState.DISABLED, reason="remediated")
    remediated = _transaction(client, lambda session: remediate_tenant_inbound_merchant_configuration(**_transition_kwargs(configuration, session, configurations, evidence, security_context, "decision-remediate", "remediate-key", 2, EnablementState.COMPROMISED, EnablementState.DISABLED, "remediated", REMEDIATION_OPERATION)))
    assert (remediated.state, remediated.revision, len(remediated.history)) == (EnablementState.DISABLED, 3, 4)
    assert remediated.history[-1].authorization_reference == "tenant-authorization-decision:decision-remediate"
    assert len(remediated.history[-1].authorization_evidence_fingerprint or "") == 128
    assert remediated.history[-1].reason_reference == "remediated"
    assert remediated.history[-1].lifecycle_idempotency_key == "remediate-key"
    compromise_replay = _transaction(client, lambda session: compromise_tenant_inbound_merchant_configuration(**_transition_kwargs(configuration, session, configurations, evidence, security_context, "decision-compromise", "compromise-key", 1, EnablementState.ENABLED, EnablementState.COMPROMISED, "security-event", COMPROMISE_OPERATION)))
    assert compromise_replay.state is EnablementState.DISABLED and compromise_replay.revision == 3 and len(compromise_replay.history) == 4
    assert compromise_replay.history == remediated.history
    remediation_replay = _transaction(client, lambda session: remediate_tenant_inbound_merchant_configuration(**_transition_kwargs(configuration, session, configurations, evidence, security_context, "decision-remediate", "remediate-key", 2, EnablementState.COMPROMISED, EnablementState.DISABLED, "remediated", REMEDIATION_OPERATION)))
    assert remediation_replay.state is EnablementState.DISABLED and remediation_replay.revision == 3 and len(remediation_replay.history) == 4
    assert remediation_replay.history == remediated.history


def test_real_mongo_tenant_idempotency_cross_tenant_and_stale_cas(mongo_db: Any) -> None:
    client, _, configurations, evidence = mongo_db
    first = _register_seed(client, configurations, evidence, TENANT_A, "a")
    second = _register_seed(client, configurations, evidence, TENANT_B, "b")
    auth_fp = "f" * 128
    with client.start_session() as session:
        session.start_transaction()
        TenantInboundMerchantConfigurationRegistry.transition_enablement(
            TENANT_A, first.merchant_configuration_id, 1, 0, EnablementState.DISABLED,
            EnablementState.ENABLED, FIXED_AT, FIXED_AT, "aborted", "tenant-authorization-decision:fixture",
            auth_fp, "aborted-key", configurations, session=session,
        )
        session.abort_transaction()
    aborted = TenantInboundMerchantConfigurationRegistry.get(TENANT_A, first.merchant_configuration_id, 1, configurations)
    assert aborted is not None and aborted.revision == 0 and len(aborted.history) == 1
    assert configurations.count_documents({"lifecycle_history.lifecycle_idempotency_key": "aborted-key"}) == 0
    transition = lambda tenant, config, state: _transaction(client, lambda session: TenantInboundMerchantConfigurationRegistry.transition_enablement(tenant, config.merchant_configuration_id, 1, 0, EnablementState.DISABLED, state, FIXED_AT, FIXED_AT, "shared-key-reason", "tenant-authorization-decision:fixture", auth_fp, "tenant-wide-key", configurations, session=session))
    transition(TENANT_A, first, EnablementState.ENABLED)
    with pytest.raises(TenantInboundMerchantConfigurationReplayConflictError):
        transition(TENANT_A, second, EnablementState.ENABLED)
    transition(TENANT_B, second, EnablementState.ENABLED)
    with pytest.raises(TenantInboundMerchantConfigurationTransitionConflictError):
        _transaction(client, lambda session: TenantInboundMerchantConfigurationRegistry.transition_enablement(TENANT_A, first.merchant_configuration_id, 1, 0, EnablementState.DISABLED, EnablementState.SUSPENDED, FIXED_AT, FIXED_AT, "stale", "tenant-authorization-decision:fixture", auth_fp, "stale-key", configurations, session=session))
    current_a = TenantInboundMerchantConfigurationRegistry.get(TENANT_A, first.merchant_configuration_id, 1, configurations)
    current_b = TenantInboundMerchantConfigurationRegistry.get(TENANT_B, second.merchant_configuration_id, 1, configurations)
    assert current_a is not None and current_b is not None
    assert current_a.revision == current_b.revision == 1
    assert current_a.state is current_b.state is EnablementState.ENABLED


def test_real_mongo_concurrent_cas_exactly_one_commit(mongo_db: Any) -> None:
    client, _, configurations, evidence = mongo_db
    configuration = _register_seed(client, configurations, evidence)
    barrier = Barrier(2)

    def worker(target: EnablementState) -> tuple[str, str]:
        try:
            with client.start_session() as session:
                session.start_transaction()
                barrier.wait(timeout=5)
                TenantInboundMerchantConfigurationRegistry.transition_enablement(
                    TENANT_A, configuration.merchant_configuration_id, 1, 0, EnablementState.DISABLED,
                    target, FIXED_AT, FIXED_AT, f"race-{target.value}", "tenant-authorization-decision:race",
                    "e" * 128, f"race-key-{target.value}", configurations, session=session,
                )
                session.commit_transaction()
                return "committed", target.value
        except (PyMongoError, TenantInboundMerchantConfigurationRegistryError, TenantInboundMerchantConfigurationTransitionConflictError, TenantInboundMerchantConfigurationReplayConflictError) as error:
            return "rejected", type(error).__name__

    with ThreadPoolExecutor(max_workers=2) as pool:
        outcomes = list(pool.map(worker, (EnablementState.ENABLED, EnablementState.SUSPENDED)))
    assert sum(result == "committed" for result, _ in outcomes) == 1
    current = TenantInboundMerchantConfigurationRegistry.get(TENANT_A, configuration.merchant_configuration_id, 1, configurations)
    assert current is not None and current.revision == 1 and len(current.history) == 2
    assert sum(event.lifecycle_idempotency_key is not None for event in current.history) == 1


def test_real_mongo_concurrent_same_key_has_one_durable_event(mongo_db: Any) -> None:
    client, _, configurations, evidence = mongo_db
    configuration = _register_seed(client, configurations, evidence)
    barrier = Barrier(2)

    def worker() -> str:
        try:
            with client.start_session() as session:
                session.start_transaction()
                barrier.wait(timeout=5)
                TenantInboundMerchantConfigurationRegistry.transition_enablement(
                    TENANT_A, configuration.merchant_configuration_id, 1, 0, EnablementState.DISABLED,
                    EnablementState.ENABLED, FIXED_AT, FIXED_AT, "same-key", "tenant-authorization-decision:same",
                    "a" * 128, "same-idempotency-key", configurations, session=session,
                )
                session.commit_transaction()
                return "committed"
        except (PyMongoError, TenantInboundMerchantConfigurationRegistryError):
            return "rejected"

    with ThreadPoolExecutor(max_workers=2) as pool:
        outcomes = list(pool.map(lambda _: worker(), range(2)))
    if not any(outcome == "committed" for outcome in outcomes):
        _transaction(client, lambda session: TenantInboundMerchantConfigurationRegistry.transition_enablement(
            TENANT_A, configuration.merchant_configuration_id, 1, 0, EnablementState.DISABLED,
            EnablementState.ENABLED, FIXED_AT, FIXED_AT, "same-key", "tenant-authorization-decision:same",
            "a" * 128, "same-idempotency-key", configurations, session=session,
        ))
    current = TenantInboundMerchantConfigurationRegistry.get(TENANT_A, configuration.merchant_configuration_id, 1, configurations)
    assert current is not None and current.revision == 1 and len(current.history) == 2
    assert sum(event.lifecycle_idempotency_key == "same-idempotency-key" for event in current.history) == 1


def test_real_mongo_eight_divergent_replay_fields_fail_closed(mongo_db: Any) -> None:
    client, _, configurations, evidence = mongo_db
    configuration = _register_seed(client, configurations, evidence)
    auth_fp = "d" * 128
    _transaction(client, lambda session: TenantInboundMerchantConfigurationRegistry.transition_enablement(
        TENANT_A, configuration.merchant_configuration_id, 1, 0, EnablementState.DISABLED,
        EnablementState.ENABLED, FIXED_AT, FIXED_AT, "divergence-reason", "auth-reference", auth_fp,
        "divergence-key", configurations, session=session,
    ))

    def divergent(**overrides: Any) -> None:
        if "configuration_fingerprint" in overrides:
            alternate_fingerprint = overrides["configuration_fingerprint"]
            payload = _lifecycle_payload(
                tenant_id=TENANT_A, merchant_configuration_id=configuration.merchant_configuration_id,
                merchant_configuration_version=1, configuration_fingerprint=alternate_fingerprint,
                expected_prior_lifecycle_revision=0, expected_prior_state=EnablementState.DISABLED,
                target_state=EnablementState.ENABLED, reason_reference="divergence-reason",
                lifecycle_idempotency_key="divergence-key",
            )
            alternate_intent = _lifecycle_fingerprint(payload)
            _evidence(
                collection=evidence, tenant_id=TENANT_A, decision_id="decision-divergent-fingerprint",
                operation=LIFECYCLE_OPERATION, permission=LIFECYCLE_PERMISSION,
                business_role=LIFECYCLE_BUSINESS_ROLE, authorization_role="INBOUND_MERCHANT_CONFIGURATION_ADMIN",
                subject_reference=_lifecycle_subject("lifecycle-transition", alternate_intent),
                subject_fingerprint=alternate_intent, idempotency_key="evidence-divergent-fingerprint",
            )
            ordinary_context = _context(TENANT_A, LIFECYCLE_BUSINESS_ROLE, "INBOUND_MERCHANT_CONFIGURATION_ADMIN")
            with pytest.raises((TenantInboundMerchantConfigurationIssuanceError, TenantInboundMerchantConfigurationReplayConflictError)):
                _transaction(client, lambda session: transition_tenant_inbound_merchant_configuration(
                    tenant_id=TENANT_A, merchant_configuration_id=configuration.merchant_configuration_id,
                    merchant_configuration_version=1, expected_configuration_fingerprint=alternate_fingerprint,
                    expected_lifecycle_revision=0, expected_prior_state=EnablementState.DISABLED,
                    target_state=EnablementState.ENABLED, reason_reference="divergence-reason",
                    lifecycle_idempotency_key="divergence-key", authorization_decision_id="decision-divergent-fingerprint",
                    session=session, configuration_collection=configurations, authorization_evidence_collection=evidence,
                    principal_repository=ordinary_context.principal_repository(), membership_repository=ordinary_context.membership_repository(),
                    role_assignment_repository=ordinary_context.role_repository(), business_role_repository=ordinary_context.role_repository(),
                    authorization_evidence_registry=_DurableEvidenceReader(evidence), clock=lambda: FIXED_AT,
                ))
            return
        values: dict[str, Any] = {
            "tenant_id": TENANT_A,
            "merchant_configuration_id": configuration.merchant_configuration_id,
            "merchant_configuration_version": 1,
            "expected_revision": 0,
            "expected_prior_state": EnablementState.DISABLED,
            "new_state": EnablementState.ENABLED,
            "reason_reference": "divergence-reason",
            "authorization_reference": "auth-reference",
            "authorization_evidence_fingerprint": auth_fp,
            "lifecycle_idempotency_key": "divergence-key",
        }
        values.update(overrides)
        with pytest.raises(TenantInboundMerchantConfigurationReplayConflictError):
            _transaction(client, lambda session: TenantInboundMerchantConfigurationRegistry.transition_enablement(
                values["tenant_id"], values["merchant_configuration_id"], values["merchant_configuration_version"],
                values["expected_revision"], values["expected_prior_state"], values["new_state"], FIXED_AT,
                FIXED_AT, values["reason_reference"], values["authorization_reference"],
                values["authorization_evidence_fingerprint"], values["lifecycle_idempotency_key"],
                configurations, session=session,
            ))

    divergent(merchant_configuration_id="different-config")
    divergent(merchant_configuration_version=2)
    divergent(configuration_fingerprint="c" * 128)
    divergent(expected_revision=1)
    divergent(expected_prior_state=EnablementState.ENABLED)
    divergent(new_state=EnablementState.SUSPENDED)
    divergent(reason_reference="different-reason")
    divergent(authorization_reference="different-auth-reference")
    current = TenantInboundMerchantConfigurationRegistry.get(TENANT_A, configuration.merchant_configuration_id, 1, configurations)
    assert current is not None and current.revision == 1 and len(current.history) == 2


def test_real_mongo_strict_hydration_rejects_corruption_without_repair(mongo_db: Any) -> None:
    client, _, configurations, evidence = mongo_db
    configuration = _register_seed(client, configurations, evidence)
    configurations.update_one({"configuration.tenant_id": TENANT_A, "configuration.merchant_configuration_id": configuration.merchant_configuration_id}, {"$set": {"forged": True}})
    with pytest.raises(TenantInboundMerchantConfigurationPersistedRecordInvalidError):
        TenantInboundMerchantConfigurationRegistry.get(TENANT_A, configuration.merchant_configuration_id, 1, configurations)
    assert configurations.count_documents({"forged": True}) == 1
    assert evidence.count_documents({"tenant_id": TENANT_A}) == 1


def test_real_mongo_corrupt_historical_authorization_rejects_without_mutation(mongo_db: Any) -> None:
    client, _, configurations, evidence = mongo_db
    configuration = _register_seed(client, configurations, evidence)
    _transaction(client, lambda session: TenantInboundMerchantConfigurationRegistry.transition_enablement(
        TENANT_A, configuration.merchant_configuration_id, 1, 0, EnablementState.DISABLED,
        EnablementState.ENABLED, FIXED_AT, FIXED_AT, "auth-corruption", "auth-reference", "a" * 128,
        "auth-corruption-key", configurations, session=session,
    ))
    query = {"configuration.tenant_id": TENANT_A, "configuration.merchant_configuration_id": configuration.merchant_configuration_id}
    configurations.update_one(query, {"$set": {"lifecycle_history.1.authorization_reference": "forged-reference"}})
    with pytest.raises(TenantInboundMerchantConfigurationPersistedRecordInvalidError):
        TenantInboundMerchantConfigurationRegistry.get(TENANT_A, configuration.merchant_configuration_id, 1, configurations)
    configurations.update_one(query, {"$set": {"lifecycle_history.1.authorization_reference": "auth-reference"}})
    configurations.update_one(query, {"$set": {"lifecycle_history.1.authorization_evidence_fingerprint": "b" * 128}})
    with pytest.raises(TenantInboundMerchantConfigurationPersistedRecordInvalidError):
        TenantInboundMerchantConfigurationRegistry.get(TENANT_A, configuration.merchant_configuration_id, 1, configurations)
    configurations.update_one(query, {"$set": {"lifecycle_history.1.authorization_evidence_fingerprint": "a" * 128}})
    current = TenantInboundMerchantConfigurationRegistry.get(TENANT_A, configuration.merchant_configuration_id, 1, configurations)
    assert current is not None and current.revision == 1 and len(current.history) == 2
    assert evidence.count_documents({"tenant_id": TENANT_A}) == 1


def test_real_mongo_commit_uncertainty_committed_then_exact_replay(mongo_db: Any) -> None:
    """Certify caller retry after a real commit becomes observationally uncertain."""
    client, _, configurations, evidence = mongo_db
    configuration = _register_seed(client, configurations, evidence, TENANT_A, "m2")
    context = _context(TENANT_A, LIFECYCLE_BUSINESS_ROLE, "INBOUND_MERCHANT_CONFIGURATION_ADMIN")
    decision_id = "decision-commit-uncertainty"
    lifecycle_key = "commit-uncertainty-key"
    reason = "commit-outcome-unknown"
    _lifecycle_evidence(
        evidence,
        configuration,
        decision_id=decision_id,
        key=lifecycle_key,
        operation=LIFECYCLE_OPERATION,
        permission=LIFECYCLE_PERMISSION,
        business_role=LIFECYCLE_BUSINESS_ROLE,
        authorization_role="INBOUND_MERCHANT_CONFIGURATION_ADMIN",
        prior_revision=0,
        prior_state=EnablementState.DISABLED,
        target_state=EnablementState.ENABLED,
        reason=reason,
    )
    intent_fingerprint = _lifecycle_fingerprint(_lifecycle_payload(
        tenant_id=TENANT_A,
        merchant_configuration_id=configuration.merchant_configuration_id,
        merchant_configuration_version=configuration.merchant_configuration_version,
        configuration_fingerprint=configuration.fingerprint,
        expected_prior_lifecycle_revision=0,
        expected_prior_state=EnablementState.DISABLED,
        target_state=EnablementState.ENABLED,
        reason_reference=reason,
        lifecycle_idempotency_key=lifecycle_key,
    ))

    first_session: ClientSession | None = None
    first_caller_result = "NOT_EXECUTED"
    try:
        with client.start_session() as session:
            first_session = session
            session.start_transaction()
            transition_tenant_inbound_merchant_configuration(**_transition_kwargs(
                configuration,
                session,
                configurations,
                evidence,
                context,
                decision_id,
                lifecycle_key,
                0,
                EnablementState.DISABLED,
                EnablementState.ENABLED,
                reason,
                LIFECYCLE_OPERATION,
            ))
            try:
                _commit_then_report_unknown(session)
            except _UnknownCommitResult as error:
                assert error.has_error_label("UnknownTransactionCommitResult")
                first_caller_result = "UNKNOWN"
    except BaseException:
        if first_caller_result != "UNKNOWN":
            raise

    assert first_caller_result == "UNKNOWN"
    committed = TenantInboundMerchantConfigurationRegistry.get(
        TENANT_A,
        configuration.merchant_configuration_id,
        1,
        configurations,
    )
    assert committed is not None
    assert committed.revision == 1
    assert committed.state is EnablementState.ENABLED
    assert len(committed.history) == 2
    assert configurations.count_documents({"lifecycle_history.lifecycle_idempotency_key": lifecycle_key}) == 1

    retry_session: ClientSession | None = None
    retry_clock_called = False

    def forbidden_retry_clock() -> datetime:
        nonlocal retry_clock_called
        retry_clock_called = True
        raise AssertionError("exact replay must not obtain a fresh clock authority")

    with client.start_session() as session:
        retry_session = session
        session.start_transaction()
        retry_kwargs = _transition_kwargs(
            configuration,
            session,
            configurations,
            evidence,
            context,
            decision_id,
            lifecycle_key,
            0,
            EnablementState.DISABLED,
            EnablementState.ENABLED,
            reason,
            LIFECYCLE_OPERATION,
        )
        retry_kwargs["clock"] = forbidden_retry_clock
        replay = transition_tenant_inbound_merchant_configuration(**retry_kwargs)
        assert replay == committed
        session.commit_transaction()

    assert first_session is not None and retry_session is not None
    assert first_session is not retry_session
    assert retry_clock_called is False
    final_record = TenantInboundMerchantConfigurationRegistry.get(
        TENANT_A,
        configuration.merchant_configuration_id,
        1,
        configurations,
    )
    assert final_record is not None
    assert final_record.revision == 1
    assert final_record.state is EnablementState.ENABLED
    assert len(final_record.history) == 2
    assert configurations.count_documents({"lifecycle_history.lifecycle_idempotency_key": lifecycle_key}) == 1
    assert evidence.count_documents({"tenant_id": TENANT_A, "authorization_decision_id": decision_id}) == 1
    assert intent_fingerprint == _lifecycle_fingerprint(_lifecycle_payload(
        tenant_id=TENANT_A,
        merchant_configuration_id=configuration.merchant_configuration_id,
        merchant_configuration_version=1,
        configuration_fingerprint=configuration.fingerprint,
        expected_prior_lifecycle_revision=0,
        expected_prior_state=EnablementState.DISABLED,
        target_state=EnablementState.ENABLED,
        reason_reference=reason,
        lifecycle_idempotency_key=lifecycle_key,
    ))


# ARTIFACT: test_tenant_inbound_merchant_configuration_lifecycle_real_mongo.py
# VERSION: v1.2.2-M11-R8-R3B-P8-P2-P0-R1
# AUTHORITY BOUNDARY: host-backed evidence only; no lifecycle authority beyond production owners.
# TENANT POSTURE: UUID database and explicit tenant predicates isolate all durable assertions.
# FAIL-CLOSED POSTURE: host, transaction, CAS, replay, corruption, strict hydration,
# and commit-uncertainty failures reject.
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively; no payment or settlement semantics.
# END OF WILSY OS SOVEREIGN ARTIFACT
