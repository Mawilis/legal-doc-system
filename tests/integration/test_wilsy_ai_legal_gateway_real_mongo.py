"""WILSY AI Legal Tool Gateway official real-Mongo certificate.

TITLE: WILSY AI Legal Tool Gateway Runtime Certificate
VERSION: v1.3.1-L7B-WILSY-AI-LEGAL-TOOL-REAL-MONGO-CERT
AUTHORITY: Host-backed evidence that the production gateway composes its
           canonical IAM, entitlement, capacity, legal-read and invocation
           evidence authorities.
EPITOME: Exercise the mounted FastAPI gateway against an isolated writable
         Mongo replica set without replacing any production decision function.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tests/integration/test_wilsy_ai_legal_gateway_real_mongo.py
COLLABORATION / OWNERSHIP: The gateway router composes L7A/L7C reads, P4/P6B/
                            P6C commercial capacity and the L7B evidence
                            registry; Kennel EOS remains financial authority.
CERTIFICATION / UPDATE DATE: 2026-09-23
CHANGELOG: v1.3.1 aligns real-Mongo IAM seeding with the canonical dedicated
           tenant_business_roles store used by tenant_authorization_http v1.1.0,
           preserving separate business-role eligibility and uppercase granting
           role authority while keeping the production gateway unchanged.
           v1.3.0 reconciled positive visibility with all seven canonical
           registry tools and proved capacity binds entitlement identity.
           v1.1.0 replaces direct synthetic registry writes with production
           router HTTP composition, real canonical auth/entitlement/lifecycle
           seed data, exact replay, tenant isolation and corruption evidence.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2.
SECURITY / PRIVACY POSTURE: UUID-isolated synthetic tenants only; no provider,
                             credential, prompt, secret or customer payload.
TENANT BOUNDARY: Every canonical repository query is exact-tenant scoped;
                 foreign resource existence is returned only as bounded absence.
AUTHORITY BOUNDARY: Read-tool allowlist and immutable invocation evidence only;
                    no legal lifecycle, billing, invoice, payment or settlement mutation.
FINANCIAL AUTHORITY BOUNDARY: Kennel EOS exclusively owns financial execution
                              and settlement.
TRANSACTION BOUNDARY: The production router owns its request transaction;
                      canonical repositories receive that session and the
                      test never supplies a replacement transaction policy.
FAIL-CLOSED DECLARATION: Only hello connectivity, replica-set mismatch, or
                         missing writable primary may skip; all product,
                         persistence, hydration, IAM and projection failures fail.
"""
from __future__ import annotations

import os
from datetime import datetime, timezone
from typing import Any, Iterator, Mapping, cast
from uuid import uuid4

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from pymongo import MongoClient
from pymongo.errors import AutoReconnect, ConnectionFailure, ServerSelectionTimeoutError

from tools.eos.auth.authentication import get_current_identity
from tools.eos.auth.identity import SovereignIdentity
from tools.eos.auth.principal_authority import PrincipalAuthority
from tools.eos.auth.principal_authority_repository import PrincipalAuthorityRepository
from tools.eos.auth.principal_status import PrincipalStatus
from tools.eos.auth.role_assignment import RoleAssignmentAuthority, RoleAssignmentStatus
from tools.eos.auth.role_assignment_repository import RoleAssignmentRepository
from tools.eos.auth.tenant_business_role import (
    TenantBusinessRoleAuthority,
    TenantBusinessRoleStatus,
)
from tools.eos.auth.tenant_business_role_repository import TenantBusinessRoleRepository
from tools.eos.auth.tenant_membership import TenantMembershipAuthority, TenantMembershipStatus
from tools.eos.auth.tenant_membership_repository import TenantMembershipRepository
from tools.eos.intelligence.domain.legal_ai_gateway import (
    CAPABILITIES,
    LegalAIToolInvocationEvidence,
)
from tools.eos.intelligence.registry.legal_ai_tool_invocation_registry import (
    COLLECTION as INVOCATION_COLLECTION,
    LegalAIToolInvocationConflictError,
    LegalAIToolInvocationRegistry,
    LegalAIToolInvocationRegistryError,
    ensure_indexes as ensure_invocation_indexes,
)
from tools.eos.legal_operations.domain.legal_operations_lifecycle import LegalInstruction
from tools.eos.legal_operations.registry.legal_operations_lifecycle_registry import (
    COLLECTION as LIFECYCLE_COLLECTION,
    LegalOperationsLifecycleRegistry,
)
from tools.eos.saas.billing.wilsy_ai_commercial_policy import (
    WilsyAITier,
    get_wilsy_ai_commercial_policy,
)
from tools.eos.saas.billing.wilsy_ai_entitlement_registry import (
    COLLECTION as ENTITLEMENT_COLLECTION,
    WilsyAIEntitlementNotFoundError,
    WilsyAIEntitlementRegistry,
    WilsyAIEntitlementRegistryError,
    ensure_indexes as ensure_entitlement_indexes,
)
from tools.eos.saas.billing.wilsy_ai_usage_observation_registry import (
    COLLECTION as OBSERVATION_COLLECTION,
    WilsyAIUsageObservationRegistry,
    ensure_indexes as ensure_observation_indexes,
)
from tools.eos.saas.billing.wilsy_ai_usage_capacity_orchestrator import (
    WilsyAIUsageCapacityOrchestrator,
)
from tools.eos.saas.domain.wilsy_ai_entitlement import (
    WilsyAIEntitlement,
    WilsyAIEntitlementState,
)
from tools.eos.saas.domain.wilsy_ai_usage_observation import WilsyAIUsageObservation


URI = os.getenv(
    "TEST_VENDOR_MONGO_URI",
    "mongodb://127.0.0.1:27027/?replicaSet=wilsyVendorCertRS",
)
EXPECTED_SET_NAME = "wilsyVendorCertRS"
TENANT_A = "tenant-b4-real-a"
TENANT_B = "tenant-b4-real-b"
TENANT_C = "tenant-b4-real-c"
MODULE_ID = "WILSY_AI_LEGAL_TOOL_GATEWAY"
BASE_TIME = datetime(2026, 9, 15, 12, 0, tzinfo=timezone.utc)
READINESS_FP = "a" * 128
ACTIVATION_FP = "b" * 128


class _FrozenDateTime(datetime):
    """Keep two identical requests byte-identical for the gateway replay proof."""

    @classmethod
    def now(cls, tz: Any = None) -> datetime:
        if tz is None:
            return BASE_TIME.replace(tzinfo=None)
        return BASE_TIME.astimezone(tz)


def _identity(tenant_id: str) -> SovereignIdentity:
    """Build an authenticated identity projection whose authority is seeded below."""
    return SovereignIdentity(
        identity_id=f"principal-{tenant_id}",
        tenant_id=tenant_id,
        username=f"cert-{tenant_id}",
        email=None,
        roles=[],
        permissions=[],
        auth_method="CERTIFICATE",
        status=PrincipalStatus.ACTIVE,
    )


def _seed_auth(
    database: Any,
    tenant_id: str,
    *,
    business_role_id: str,
    authorization_role_id: str,
) -> None:
    """Persist separate business-role and granting authorization-role evidence."""
    principal_collection = database["principal_authorities"]
    membership_collection = database["tenant_memberships"]
    role_collection = database["role_assignments"]
    business_role_collection = database["tenant_business_roles"]
    PrincipalAuthorityRepository.ensure_indexes(principal_collection)
    TenantMembershipRepository.ensure_indexes(membership_collection)
    RoleAssignmentRepository.ensure_indexes(role_collection)
    TenantBusinessRoleRepository.ensure_indexes(business_role_collection)
    principal_id = f"principal-{tenant_id}"
    with database.client.start_session() as session:
        session.start_transaction()
        PrincipalAuthorityRepository.create(
            PrincipalAuthority(principal_id, PrincipalStatus.ACTIVE, 0),
            principal_collection,
            session=session,
        )
        TenantMembershipRepository.insert(
            TenantMembershipAuthority(
                principal_id, tenant_id, TenantMembershipStatus.ACTIVE, 0
            ),
            membership_collection,
            session=session,
        )
        TenantBusinessRoleRepository.insert(
            TenantBusinessRoleAuthority(
                principal_id,
                tenant_id,
                business_role_id,
                TenantBusinessRoleStatus.ACTIVE,
                0,
                BASE_TIME,
                None,
            ),
            business_role_collection,
            session=session,
        )
        RoleAssignmentRepository.insert(
            RoleAssignmentAuthority(
                principal_id,
                tenant_id,
                authorization_role_id,
                RoleAssignmentStatus.ACTIVE,
                0,
            ),
            role_collection,
            session=session,
        )
        session.commit_transaction()


def _seed_entitlement(database: Any, tenant_id: str) -> WilsyAIEntitlement:
    """Create one active canonical gateway entitlement for a tenant."""
    collection = database[ENTITLEMENT_COLLECTION]
    ensure_entitlement_indexes(collection)
    policy = get_wilsy_ai_commercial_policy(WilsyAITier.STARTER)
    pending = WilsyAIEntitlement(
        tenant_id=tenant_id,
        entitlement_id=f"entitlement-{tenant_id}",
        module_id=MODULE_ID,
        module_name="WILSY AI Legal Tools",
        tier=WilsyAITier.STARTER,
        policy_fingerprint=policy.policy_fingerprint,
        lifecycle_state=WilsyAIEntitlementState.PENDING_SOURCE,
        source_requirements=("records",),
        capability_grants=CAPABILITIES,
        source_readiness_evidence_reference=f"ready-{tenant_id}",
        source_readiness_evidence_fingerprint=READINESS_FP,
    )
    with database.client.start_session() as session:
        session.start_transaction()
        registry = WilsyAIEntitlementRegistry(collection)
        registry.create_or_replay(
            pending,
            idempotency_key=f"idem-{tenant_id}",
            session=session,
        )
        active = registry.transition(
            tenant_id=tenant_id,
            entitlement_id=pending.entitlement_id,
            target_state=WilsyAIEntitlementState.ACTIVE,
            expected_revision=0,
            evidence_reference=f"activate-{tenant_id}",
            evidence_fingerprint=ACTIVATION_FP,
            occurred_at=BASE_TIME,
            session=session,
        )
        session.commit_transaction()
    return active


def _seed_instruction(database: Any) -> LegalInstruction:
    """Persist one canonical P2 LegalInstruction for the adapter's real read."""
    collection = database[LIFECYCLE_COLLECTION]
    LegalOperationsLifecycleRegistry.ensure_indexes(collection)
    instruction = LegalInstruction(
        tenant_id=TENANT_A,
        instruction_id="instruction-b4-real",
        case_matter_id="matter-b4-real",
        document_id="document-b4-real",
        registered_at=BASE_TIME,
        evidence_reference="instruction-registration-b4-real",
    )
    with database.client.start_session() as session:
        session.start_transaction()
        LegalOperationsLifecycleRegistry.create(instruction, collection, session=session)
        session.commit_transaction()
    return instruction


def _seed_observation(
    database: Any, entitlement: WilsyAIEntitlement, usage_id: str, request_units: int
) -> WilsyAIUsageObservation:
    """Persist one canonical P6B observation for real P6C capacity derivation."""
    collection = database[OBSERVATION_COLLECTION]
    observation = WilsyAIUsageObservation(
        tenant_id=entitlement.tenant_id,
        usage_observation_id=usage_id,
        entitlement_id=entitlement.entitlement_id,
        entitlement_revision=entitlement.lifecycle_revision,
        entitlement_fingerprint=entitlement.fingerprint,
        module_id=entitlement.module_id,
        request_units=request_units,
        input_tokens=10,
        output_tokens=20,
        automation_actions=request_units,
        occurred_at=BASE_TIME,
        source_evidence_reference=f"source-{usage_id}",
        source_evidence_fingerprint=READINESS_FP,
    )
    with database.client.start_session() as session:
        session.start_transaction()
        WilsyAIUsageObservationRegistry(collection).create_or_replay(
            observation,
            idempotency_key=f"idem-{usage_id}",
            session=session,
        )
        session.commit_transaction()
    return observation


@pytest.fixture()
def mongo_database() -> Iterator[tuple[MongoClient, Any]]:
    """Yield a UUID-isolated database after the three permitted hello skips."""
    client = MongoClient(URI, serverSelectionTimeoutMS=2000, retryWrites=True)
    try:
        hello = client.admin.command("hello")
    except (ServerSelectionTimeoutError, ConnectionFailure, AutoReconnect) as error:
        client.close()
        pytest.skip(f"B4_R1_MONGO_HELLO_UNAVAILABLE:{type(error).__name__}")
    if hello.get("setName") != EXPECTED_SET_NAME:
        client.close()
        pytest.skip(f"B4_R1_MONGO_WRONG_REPLICA_SET:{hello.get('setName')!r}")
    if hello.get("isWritablePrimary", hello.get("ismaster")) is not True:
        client.close()
        pytest.skip("B4_R1_MONGO_WRITABLE_PRIMARY_UNAVAILABLE")
    database = client[f"w_ai_b4r1_{uuid4().hex}"]
    try:
        yield client, database
    finally:
        client.drop_database(database.name)
        client.close()


@pytest.fixture()
def production_gateway(monkeypatch: Any) -> Iterator[Any]:
    """Load the unchanged production router and freeze only test clock/auth identity."""
    from tools.eos.api import wilsy_ai_legal_gateway_router as module

    monkeypatch.setattr(module, "datetime", _FrozenDateTime)
    yield module


def test_real_mongo_production_gateway_composition_and_fail_closed_boundaries(
    mongo_database: tuple[MongoClient, Any],
    production_gateway: Any,
    monkeypatch: Any,
) -> None:
    """Prove actual gateway HTTP composition, durable evidence and isolation."""
    client, database = mongo_database
    import tools.eos.kernel.db as kernel_db

    _seed_auth(
        database,
        TENANT_A,
        business_role_id="tenant_legal_attorney",
        authorization_role_id="LEGAL_ATTORNEY",
    )
    _seed_auth(
        database,
        TENANT_B,
        business_role_id="tenant_legal_attorney",
        authorization_role_id="LEGAL_ATTORNEY",
    )
    _seed_auth(
        database,
        TENANT_C,
        business_role_id="tenant_legal_finance",
        authorization_role_id="LEGAL_FINANCE",
    )
    assert "tenant_legal_attorney" != "LEGAL_ATTORNEY"
    assert database["tenant_business_roles"].find_one(
        {
            "tenant_id": TENANT_A,
            "business_role": "tenant_legal_attorney",
        }
    ) is not None
    assert database["role_assignments"].find_one(
        {"tenant_id": TENANT_A, "role_id": "LEGAL_ATTORNEY"}
    ) is not None
    entitlement_a = _seed_entitlement(database, TENANT_A)
    entitlement_b = _seed_entitlement(database, TENANT_B)
    entitlement_c = _seed_entitlement(database, TENANT_C)
    instruction = _seed_instruction(database)
    ensure_observation_indexes(database[OBSERVATION_COLLECTION])
    observation_a = _seed_observation(
        database, entitlement_a, "usage-b4-real-a", request_units=1
    )
    observation_b = _seed_observation(
        database, entitlement_b, "usage-b4-real-b", request_units=35
    )
    _seed_observation(database, entitlement_c, "usage-b4-real-c", request_units=1)
    capacity_orchestrator = WilsyAIUsageCapacityOrchestrator.from_collections(
        entitlement_collection=database[ENTITLEMENT_COLLECTION],
        observation_collection=database[OBSERVATION_COLLECTION],
    )
    with client.start_session() as capacity_session:
        capacity_session.start_transaction()
        capacity_a = capacity_orchestrator.derive_capacity(
            tenant_id=TENANT_A,
            entitlement_id=entitlement_a.entitlement_id,
            as_of=BASE_TIME,
            session=capacity_session,
        )
        capacity_b = capacity_orchestrator.derive_capacity(
            tenant_id=TENANT_B,
            entitlement_id=entitlement_b.entitlement_id,
            as_of=BASE_TIME,
            session=capacity_session,
        )
        assert capacity_a.daily_exhausted is False
        assert capacity_a.daily_remaining_request_units > 0
        assert capacity_a.entitlement_fingerprint == entitlement_a.fingerprint
        assert capacity_a.entitlement_fingerprint != entitlement_a.policy_fingerprint
        assert capacity_b.daily_exhausted is True
        assert capacity_b.daily_remaining_request_units == 0
        capacity_session.abort_transaction()

    entitlement_registry = WilsyAIEntitlementRegistry(
        database[ENTITLEMENT_COLLECTION]
    )
    with client.start_session() as entitlement_session:
        entitlement_session.start_transaction()
        assert entitlement_registry.get_by_module(
            tenant_id=TENANT_A,
            module_id=MODULE_ID,
            session=entitlement_session,
        ).entitlement_id == entitlement_a.entitlement_id
        assert entitlement_registry.get_by_module(
            tenant_id=TENANT_B,
            module_id=MODULE_ID,
            session=entitlement_session,
        ).entitlement_id == entitlement_b.entitlement_id
        with pytest.raises(WilsyAIEntitlementNotFoundError):
            entitlement_registry.get_by_module(
                tenant_id=TENANT_A,
                module_id="unknown-module",
                session=entitlement_session,
            )
        entitlement_session.abort_transaction()

    entitlement_collection = database[ENTITLEMENT_COLLECTION]
    entitlement_collection.update_one(
        {"tenant_id": TENANT_A, "entitlement_id": entitlement_a.entitlement_id},
        {"$set": {"policy_fingerprint": "c" * 128}},
    )
    with client.start_session() as corrupt_entitlement_session:
        corrupt_entitlement_session.start_transaction()
        with pytest.raises(WilsyAIEntitlementRegistryError):
            entitlement_registry.get_by_module(
                tenant_id=TENANT_A,
                module_id=MODULE_ID,
                session=corrupt_entitlement_session,
            )
        corrupt_entitlement_session.abort_transaction()
    entitlement_collection.update_one(
        {"tenant_id": TENANT_A, "entitlement_id": entitlement_a.entitlement_id},
        {"$set": {"policy_fingerprint": entitlement_a.policy_fingerprint}},
    )

    invocation_collection = database[INVOCATION_COLLECTION]
    ensure_invocation_indexes(invocation_collection)
    collections_before_gateway = set(database.list_collection_names())

    monkeypatch.setattr(kernel_db, "get_database", lambda: database)
    monkeypatch.setattr(kernel_db, "get_client", lambda: client)
    current_identity = _identity(TENANT_A)

    def authenticated_identity() -> SovereignIdentity:
        return current_identity

    app = FastAPI()
    app.include_router(production_gateway.router, prefix="/api")
    app.dependency_overrides[get_current_identity] = authenticated_identity
    assert (
        production_gateway.LegalAIReadAdapter.__module__
        == "tools.eos.intelligence.domain.legal_ai_read_adapter"
    )

    path = "/api/wilsy-ai/legal-tools"
    invoke_path = f"{path}/legal.instruction.read.v1/invoke"
    request = {
        "resource_identity": instruction.instruction_id,
        "entitlement_id": entitlement_a.entitlement_id,
        "correlation_id": "correlation-b4-real",
    }

    with TestClient(app) as http:
        listed = http.get(path, headers={"X-Tenant-ID": TENANT_A})
        assert listed.status_code == 200, listed.text
        listed_tools = {item["identity"] for item in listed.json()["tools"]}
        assert listed_tools == {
            "legal.instruction.read.v1",
            "legal.attempt.read.v1",
            "legal.execution.read.v1",
            "legal.return.read.v1",
            "legal.tariff_assessment.read.v1",
            "legal.billing_eligibility.read.v1",
            "legal.invoice.read.v1",
        }

        current_identity = _identity(TENANT_C)
        finance_list = http.get(path, headers={"X-Tenant-ID": TENANT_C})
        assert finance_list.status_code == 200, finance_list.text
        finance_tools = {item["identity"] for item in finance_list.json()["tools"]}
        assert "legal.instruction.read.v1" not in finance_tools
        assert "legal.invoice.read.v1" in finance_tools

        denied_underlying = http.post(
            invoke_path,
            headers={"X-Tenant-ID": TENANT_C},
            json={
                "resource_identity": instruction.instruction_id,
                "entitlement_id": entitlement_c.entitlement_id,
                "correlation_id": "correlation-b4-denied-underlying",
            },
        )
        assert denied_underlying.status_code == 403
        assert instruction.instruction_id not in denied_underlying.text

        current_identity = _identity(TENANT_A)

        first = http.post(invoke_path, headers={"X-Tenant-ID": TENANT_A}, json=request)
        assert first.status_code == 200, first.text
        first_payload = first.json()
        assert first_payload["tool"] == "legal.instruction.read.v1"
        assert first_payload["data"]["instruction_id"] == instruction.instruction_id
        assert first_payload["data"]["tenant_id"] == TENANT_A
        evidence_payload = first_payload["evidence"]
        assert evidence_payload["tenant_id"] == TENANT_A
        assert evidence_payload["entitlement_id"] == entitlement_a.entitlement_id
        assert evidence_payload["result_reference"] == f"LegalInstruction:{instruction.instruction_id}"

        replay = http.post(invoke_path, headers={"X-Tenant-ID": TENANT_A}, json=request)
        assert replay.status_code == 200, replay.text
        assert replay.json() == first_payload
        assert invocation_collection.count_documents({"tenant_id": TENANT_A}) == 1

        unknown = http.post(
            f"{path}/legal.unknown.v1/invoke",
            headers={"X-Tenant-ID": TENANT_A},
            json=request,
        )
        assert unknown.status_code == 404
        assert "entitlement" not in unknown.text.lower()

        current_identity = _identity(TENANT_B)
        foreign_request = {
            "resource_identity": instruction.instruction_id,
            "entitlement_id": entitlement_b.entitlement_id,
            "correlation_id": "correlation-b4-foreign",
        }
        foreign = http.post(
            invoke_path,
            headers={"X-Tenant-ID": TENANT_B},
            json=foreign_request,
        )
        assert foreign.status_code == 404
        assert instruction.instruction_id not in foreign.text
        assert TENANT_A not in foreign.text

    stored = invocation_collection.find_one(
        {"tenant_id": TENANT_A, "invocation_id": request["correlation_id"]}
    )
    assert isinstance(stored, Mapping)
    canonical_evidence = LegalAIToolInvocationEvidence.from_dict(
        cast(Mapping[str, object], {key: stored[key] for key in stored if key != "_id"})
    )
    assert canonical_evidence.to_dict() == evidence_payload

    registry = LegalAIToolInvocationRegistry(invocation_collection)
    assert all(
        not hasattr(LegalAIToolInvocationRegistry, method)
        for method in ("start_transaction", "commit_transaction", "abort_transaction", "commit", "abort")
    )
    assert all(
        not hasattr(WilsyAIEntitlementRegistry, method)
        for method in ("start_transaction", "commit_transaction", "abort_transaction", "commit", "abort")
    )
    with client.start_session() as session:
        session.start_transaction()
        replayed = registry.create_or_replay(canonical_evidence, session=session)
        assert replayed.to_dict() == canonical_evidence.to_dict()
        divergent_values = canonical_evidence.to_dict()
        divergent_values["result_reference"] = "LegalInstruction:divergent"
        divergent_values["fingerprint"] = ""
        divergent_values["occurred_at"] = canonical_evidence.occurred_at
        divergent = LegalAIToolInvocationEvidence(
            **cast(dict[str, Any], divergent_values)
        )
        with pytest.raises(LegalAIToolInvocationConflictError):
            registry.create_or_replay(divergent, session=session)
        session.abort_transaction()

    with client.start_session() as foreign_evidence_session:
        with pytest.raises(LegalAIToolInvocationRegistryError):
            registry.get(
                tenant_id=TENANT_B,
                invocation_id=request["correlation_id"],
                session=foreign_evidence_session,
            )

    original_fingerprint = cast(str, stored["fingerprint"])
    invocation_collection.update_one(
        {"tenant_id": TENANT_A, "invocation_id": request["correlation_id"]},
        {"$set": {"fingerprint": "f" * 128}},
    )
    current_identity = _identity(TENANT_A)
    with TestClient(app) as http:
        corrupt = http.post(invoke_path, headers={"X-Tenant-ID": TENANT_A}, json=request)
    assert corrupt.status_code == 503
    assert "unavailable" in corrupt.text.lower()
    invocation_collection.update_one(
        {"tenant_id": TENANT_A, "invocation_id": request["correlation_id"]},
        {"$set": {"fingerprint": original_fingerprint}},
    )
    with client.start_session() as verify_session:
        assert registry.get(
            tenant_id=TENANT_A,
            invocation_id=request["correlation_id"],
            session=verify_session,
        ).to_dict() == canonical_evidence.to_dict()

    persisted_keys = {str(key).casefold() for key in stored}
    assert not persisted_keys.intersection(
        {"payment", "settlement", "paid_state", "refund", "invoice", "billing_execution"}
    )
    assert len(production_gateway.TOOL_CONTRACTS) == 7
    assert not any("command" in identity for identity in production_gateway.TOOL_CONTRACTS)
    assert not any("write" in identity for identity in production_gateway.TOOL_CONTRACTS)
    assert set(database.list_collection_names()) == collections_before_gateway


# ARTIFACT: test_wilsy_ai_legal_gateway_real_mongo.py
# VERSION: v1.3.1-L7B-WILSY-AI-LEGAL-TOOL-REAL-MONGO-CERT
# AUTHORITY BOUNDARY: production gateway host-composition evidence only
# TENANT POSTURE: UUID-isolated exact-tenant auth, entitlement and projection reads
# FAIL-CLOSED POSTURE: only hello preflight availability may skip; later failures fail
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively
# END OF WILSY OS SOVEREIGN ARTIFACT