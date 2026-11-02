"""D15 host-backed real-Mongo certificate for first-class Legal Practice matters.

TITLE: WILSY OS First-Class Legal Matter Workspace Real-Mongo Certificate
VERSION: v1.4.0-ISSUE-300-COMBINED-ROUTER-RM-CERT
AUTHORITY: Host-backed certificate for durable CaseMatter projection through the
           authenticated Legal Practice workspace read boundary.
EPITOME: Prove that one real L8-2 intake transaction durably creates CaseMatter,
         LegalInstruction, ProcessDocument and REGISTERED custody evidence and
         that the real D15 /workspace snapshot transaction returns CaseMatter as
         first-class exact-tenant truth with its persisted opaque SHA3-512
         evidence locator only when real D22B5 Legal product availability is
         ACTIVE. Also prove product isolation, zero writes, bounded denial,
         foreign-tenant exclusion and corruption rejection without fallback.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tests/integration/test_legal_operations_practice_workspace_real_mongo.py
COLLABORATION / OWNERSHIP: L8-2 owns intake composition; P1 owns lifecycle value
                            semantics; P2 owns immutable persistence/hydration and
                            exact snapshot evidence locators; D15 owns read-only
                            workspace composition; tenant authorization remains
                            the access authority outside this persistence-focused
                            certificate.
CERTIFICATION / UPDATE DATE: 2026-11-02
CHANGELOG: 2026-11-02 v1.4.0-ISSUE-300-COMBINED-ROUTER-RM-CERT updates the pinned production router version after the semantic merge, provisions required Plan indexes only in the UUID-isolated disposable database, and preserves explicit allowlisted loopback Mongo URI and transaction certification.
CHANGELOG: 2026-11-02 v1.3.0-ISSUE-300-EXPLICIT-MONGO-URI-RM-CERT requires an explicit allowlisted loopback replica-set URI, rejects unsafe endpoints before client construction, and preserves real transaction certification.
CHANGELOG: 2026-11-02 v1.2.0-ISSUE-300-D22B5-SUBSCRIPTION-RM-CERT proves the D22B5 plus active-subscription conjunction under a caller-owned real-Mongo snapshot transaction; endpoint collection/session propagation is covered by the HTTP certificate.
CHANGELOG: 2026-10-10 v1.1.0-D22B5-R21-LEGAL-PRODUCT-CONJUNCTION-RM-CERT adds real ACTIVE success, absence/PENDING denial, product tenant isolation, corruption-as-authority-failure and zero-write projection proof inside the existing workspace snapshot transaction.
           2026-09-24 v1.0.0-L8-7D15-FIRST-CLASS-MATTER-WORKSPACE-RM-CERT
           establishes durable intake-to-workspace matter discoverability,
           exact locator binding, tenant isolation, summary consistency and
           corrupted-CaseMatter fail-closed behavior on the Wilsy replica set.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2; ISO 27001.
SECURITY / PRIVACY POSTURE: UUID-isolated databases and synthetic identifiers
                            only; no customer data, credentials, provider calls,
                            payment data, or external network capability.
TENANT BOUNDARY: Every durable row and workspace read remains exact-tenant
                 scoped. Foreign CaseMatter evidence must not appear.
AUTHORITY BOUNDARY: Certificate only. Authorized practice contexts are injected
                    at the FastAPI dependency seam solely to isolate D15 durable
                    projection behavior; no IAM authority is created by this file.
FINANCIAL AUTHORITY BOUNDARY: None; Kennel EOS remains the exclusive financial
                              execution and settlement authority.
TRANSACTION BOUNDARY: L8-2 registration runs inside one caller-owned Mongo
                      transaction. D15 then opens its own read-only snapshot
                      transaction through the production workspace code.
FAIL-CLOSED DECLARATION: Unavailable/wrong Mongo runtime, projection mismatch,
                         tenant leakage, locator mismatch, durable corruption or
                         transaction failure fails this certificate.
"""
from __future__ import annotations

from datetime import datetime, timedelta, timezone
import os
import sys
from typing import Any, Iterator
from urllib.parse import parse_qs, urlsplit
import uuid

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from pymongo import MongoClient
from pymongo.errors import PyMongoError
from pymongo.read_concern import ReadConcern
from pymongo.write_concern import WriteConcern

import tools.eos.api.legal_operations_router as legal_router
import tools.eos.saas.billing.subscription_registry as subscription_registry_module
import tools.eos.saas.billing.plan_registry as plan_registry_module
from tools.eos.api.tenant_authorization_http import TenantAuthorizationContext
from tools.eos.auth.identity import SovereignIdentity
from tools.eos.auth.principal_status import PrincipalStatus
from tools.eos.auth.tenant_authorization import (
    TenantAuthorizationDecision,
    TenantAuthorizationReason,
)
from tools.eos.legal_operations.domain.legal_operations_lifecycle import CaseMatter
from tools.eos.legal_operations.orchestration.process_service_intake_registration_orchestrator import (
    ProcessServiceIntakeRegistrationDisposition,
    register_process_service_intake,
)
from tools.eos.legal_operations.registry.legal_operations_lifecycle_registry import (
    COLLECTION,
    LegalOperationsLifecycleRegistry,
)
from tools.eos.saas.domain.tenant_product_entitlement import (
    TenantProductEntitlementState,
    create_tenant_product_entitlement,
)
from tools.eos.saas.billing.plan_registry import PlanRegistry
from tools.eos.saas.billing.subscription_registry import SubscriptionRegistry
from tools.eos.saas.entitlement import tenant_product_entitlement_registry as entitlement_registry
from tools.eos.saas.entitlement.legal_commercial_context_projection import (
    LegalCommercialContextProjectionError,
    resolve_legal_commercial_context,
)
from tools.eos.saas.entitlement.product_catalogue import TenantProductId
from tools.eos.saas.entitlement.tenant_product_entitlement_composer import (
    derive_tenant_product_entitlement_id,
)


VERSION = "v1.4.0-ISSUE-300-COMBINED-ROUTER-RM-CERT"
EXPECTED_REPLICA_SET = "wilsyVendorCertRS"
_ALLOWED_LOOPBACK_HOSTS = frozenset({"127.0.0.1", "localhost", "::1"})
_ALLOWED_DISPOSABLE_PORTS = frozenset({27017, 27028})


def _validate_mongo_uri(uri_value: str | None) -> str:
    """Require explicit disposable loopback replica-set configuration.

    Authority: test configuration only; this function cannot establish
    production or hosted-service database authority.

    Tenant and mutation scope: none. It validates transport target before any
    MongoClient is constructed and therefore before networking or persistence.

    Failure semantics: missing, malformed, non-loopback, non-allowlisted,
    credential-bearing, or wrong-replica-set values fail closed.
    """
    if not isinstance(uri_value, str) or not uri_value.strip():
        raise RuntimeError("TEST_VENDOR_MONGO_URI_REQUIRED")
    candidate = uri_value.strip()
    try:
        parsed = urlsplit(candidate)
        port = parsed.port
        query = parse_qs(parsed.query, keep_blank_values=True)
    except ValueError as error:
        raise RuntimeError("TEST_VENDOR_MONGO_URI_INVALID") from error
    if (
        parsed.scheme != "mongodb"
        or parsed.hostname not in _ALLOWED_LOOPBACK_HOSTS
        or port is None
        or port not in _ALLOWED_DISPOSABLE_PORTS
        or port == 27027
        or parsed.username is not None
        or parsed.password is not None
        or query.get("replicaSet") != [EXPECTED_REPLICA_SET]
    ):
        raise RuntimeError("TEST_VENDOR_MONGO_URI_NOT_PERMITTED")
    return candidate


def _mongo_client_for_uri(uri_value: str | None) -> MongoClient[Any]:
    """Construct a client only after strict disposable-target validation."""
    return MongoClient(
        _validate_mongo_uri(uri_value),
        serverSelectionTimeoutMS=3000,
        retryWrites=True,
    )
BASE = datetime(2026, 9, 24, 6, 0, tzinfo=timezone.utc)
ENTITLEMENT_EVIDENCE_FINGERPRINT = "a" * 128


@pytest.fixture
def mongo_context(monkeypatch: pytest.MonkeyPatch) -> Iterator[dict[str, Any]]:
    """Yield a verified writable UUID-isolated database; host failure fails."""
    client = _mongo_client_for_uri(os.environ.get("TEST_VENDOR_MONGO_URI"))
    database: Any = None
    try:
        try:
            hello = client.admin.command("hello")
        except PyMongoError as error:
            pytest.fail(
                f"D15B_MONGO_RUNTIME_UNAVAILABLE:{type(error).__name__}:{error}"
            )
        if hello.get("setName") != EXPECTED_REPLICA_SET:
            pytest.fail(
                f"D15B_MONGO_REPLICA_SET_MISMATCH:{hello.get('setName')!r}"
            )
        if hello.get("isWritablePrimary", hello.get("ismaster")) is not True:
            pytest.fail("D15B_MONGO_WRITABLE_PRIMARY_UNAVAILABLE")
        if hello.get("logicalSessionTimeoutMinutes") is None:
            pytest.fail("D15B_MONGO_TRANSACTIONS_UNAVAILABLE")

        database = client[f"legal_ops_d15b_workspace_{uuid.uuid4().hex}"]
        plans = database.get_collection(
            "plans",
            write_concern=WriteConcern(w="majority", j=True),
            read_concern=ReadConcern("majority"),
        )
        subscriptions = database.get_collection(
            "subscriptions",
            write_concern=WriteConcern(w="majority", j=True),
            read_concern=ReadConcern("majority"),
        )
        monkeypatch.setattr(plan_registry_module, "plans_collection", plans)
        monkeypatch.setattr(
            subscription_registry_module,
            "subscriptions_collection",
            subscriptions,
        )
        PlanRegistry.provision_indexes()
        subscription_registry_module._ensure_indexes(subscriptions)
        lifecycle = database.get_collection(
            COLLECTION,
            write_concern=WriteConcern(w="majority", j=True),
            read_concern=ReadConcern("majority"),
        )
        LegalOperationsLifecycleRegistry.ensure_indexes(lifecycle)
        entitlement_history = database.get_collection(
            entitlement_registry.HISTORY_COLLECTION,
            write_concern=WriteConcern(w="majority", j=True),
            read_concern=ReadConcern("majority"),
        )
        entitlement_current = database.get_collection(
            entitlement_registry.CURRENT_COLLECTION,
            write_concern=WriteConcern(w="majority", j=True),
            read_concern=ReadConcern("majority"),
        )
        entitlement_registry.ensure_indexes(
            entitlement_history,
            entitlement_current,
        )
        yield {
            "client": client,
            "database": database,
            "lifecycle": lifecycle,
            "entitlement_history": entitlement_history,
            "entitlement_current": entitlement_current,
            "subscriptions": subscriptions,
        }
    finally:
        active_error = sys.exc_info()[0] is not None
        try:
            if database is not None:
                try:
                    client.drop_database(database.name)
                except PyMongoError:
                    if not active_error:
                        raise
        finally:
            client.close()


def _context(tenant_id: str) -> TenantAuthorizationContext:
    """Return one already-authorized exact-tenant legal-practice context."""
    identity = SovereignIdentity(
        identity_id="principal-d15b",
        tenant_id=tenant_id,
        username="partner",
        email="partner@example.test",
        auth_method="TEST",
        status=PrincipalStatus.ACTIVE,
    )
    decision = TenantAuthorizationDecision(
        authorized=True,
        reason=TenantAuthorizationReason.AUTHORIZED,
        business_role="tenant_legal_partner",
        authorization_role="LEGAL_PARTNER",
    )
    return TenantAuthorizationContext(
        identity=identity,
        tenant_id=tenant_id,
        decision=decision,
    )


def _app(
    *,
    context: TenantAuthorizationContext,
    client: MongoClient[Any],
    database: Any,
    monkeypatch: pytest.MonkeyPatch,
) -> FastAPI:
    """Mount the real D15 router with only authorization and DB locator seams."""
    app = FastAPI()
    for dependency in (
        legal_router._INSTRUCTION_READ,
        legal_router._ALLOCATION_READ,
        legal_router._ATTEMPT_READ,
        legal_router._RETURN_READ,
    ):
        app.dependency_overrides[dependency] = lambda context=context: context
    monkeypatch.setattr(
        legal_router,
        "_db_handles",
        lambda: (client, database),
    )
    app.include_router(legal_router.router, prefix="/api")
    return app


def _register_intake(
    *,
    tenant_id: str,
    client: MongoClient[Any],
    lifecycle: Any,
    suffix: str,
    opened_at: datetime = BASE,
) -> Any:
    """Persist one exact L8-2 registration under a real Mongo transaction."""
    instruction_at = opened_at + timedelta(minutes=1)
    document_at = opened_at + timedelta(minutes=2)
    with client.start_session() as session:
        session.start_transaction(
            read_concern=ReadConcern("snapshot"),
            write_concern=WriteConcern(w="majority", j=True),
        )
        try:
            result = register_process_service_intake(
                tenant_id=tenant_id,
                case_matter_id=f"matter-{suffix}",
                matter_reference=f"CASE-{suffix}",
                case_opened_at=opened_at,
                matter_evidence_reference=f"matter-proof-{suffix}",
                instruction_id=f"instruction-{suffix}",
                instruction_registered_at=instruction_at,
                instruction_evidence_reference=f"instruction-proof-{suffix}",
                document_id=f"document-{suffix}",
                document_type="summons",
                document_registered_at=document_at,
                document_registration_evidence_reference=f"document-proof-{suffix}",
                registration_custody_event_id=f"custody-{suffix}",
                lifecycle_collection=lifecycle,
                session=session,
            )
            session.commit_transaction()
        except Exception:
            if bool(getattr(session, "in_transaction", False)):
                session.abort_transaction()
            raise
    assert result.disposition is ProcessServiceIntakeRegistrationDisposition.CREATED
    return result


def _entitlement_id(tenant_id: str) -> str:
    """Return the server-derived canonical Legal product lineage identity."""
    return derive_tenant_product_entitlement_id(
        tenant_id,
        TenantProductId.LEGAL_OPERATIONS,
    )


def _persist_product(
    *,
    tenant_id: str,
    mongo_context: dict[str, Any],
    activate: bool,
) -> None:
    """Persist canonical PENDING or ACTIVE D22 entitlement in one transaction."""
    client = mongo_context["client"]
    history = mongo_context["entitlement_history"]
    current = mongo_context["entitlement_current"]
    pending = create_tenant_product_entitlement(
        tenant_id=tenant_id,
        entitlement_id=_entitlement_id(tenant_id),
        product_id=TenantProductId.LEGAL_OPERATIONS,
        source_evidence_reference=f"r21-source:{tenant_id}",
        source_evidence_fingerprint=ENTITLEMENT_EVIDENCE_FINGERPRINT,
    )
    with client.start_session() as session:
        with session.start_transaction():
            entitlement_registry.create_or_replay(
                pending,
                history,
                current,
                session=session,
            )
            if activate:
                entitlement_registry.transition(
                    tenant_id=tenant_id,
                    entitlement_id=pending.entitlement_id,
                    target_state=TenantProductEntitlementState.ACTIVE,
                    expected_revision=0,
                    evidence_reference=f"r21-activation:{tenant_id}",
                    evidence_fingerprint=ENTITLEMENT_EVIDENCE_FINGERPRINT,
                    occurred_at=BASE,
                    history_collection=history,
                    current_collection=current,
                    session=session,
                )


def _workspace(
    *,
    tenant_id: str,
    mongo_context: dict[str, Any],
    monkeypatch: pytest.MonkeyPatch,
) -> Any:
    """Issue one real D15 workspace request against the isolated database."""
    app = _app(
        context=_context(tenant_id),
        client=mongo_context["client"],
        database=mongo_context["database"],
        monkeypatch=monkeypatch,
    )
    with TestClient(app) as http:
        return http.get("/api/legal-operations/workspace")


def _active_subscription(
    *,
    tenant_id: str,
    mongo_context: dict[str, Any],
) -> None:
    """Persist one canonical ACTIVE Legal subscription in isolated Mongo."""
    plan = PlanRegistry.create(
        {
            "name": f"Legal Workspace {tenant_id}",
            "price": 14400.0,
            "currency": "ZAR",
            "billingFrequency": "annual",
            "planType": "PROFESSIONAL",
            "idempotencyKey": f"workspace-plan-{tenant_id}",
            "active": True,
            "features": ["legal.core"],
            "metadata": {"certificate": "D22B5-WORKSPACE-REAL-MONGO"},
            "tags": ["legal-workspace"],
            "user": "D22B5-WORKSPACE-CERT",
        },
        tenant_id=tenant_id,
    )
    assert plan["success"] is True
    created = SubscriptionRegistry.create(
        {
            "tenantId": tenant_id,
            "planId": plan["plan"].plan_id,
            "startDate": BASE.isoformat(),
            "idempotencyKey": f"workspace-subscription-{tenant_id}",
        },
        tenant_id_header=tenant_id,
    )
    assert created["success"] is True


def test_missing_mongo_uri_is_rejected_before_client_construction(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Missing URI fails before the Mongo client can make a connection."""
    constructed: list[str] = []
    monkeypatch.setattr(
        sys.modules[__name__],
        "MongoClient",
        lambda uri, **kwargs: constructed.append(uri),
    )
    with pytest.raises(RuntimeError, match="TEST_VENDOR_MONGO_URI_REQUIRED"):
        _mongo_client_for_uri(None)
    assert constructed == []


def test_blank_mongo_uri_is_rejected_before_client_construction(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Whitespace-only URI fails before the Mongo client can connect."""
    constructed: list[str] = []
    monkeypatch.setattr(
        sys.modules[__name__],
        "MongoClient",
        lambda uri, **kwargs: constructed.append(uri),
    )
    with pytest.raises(RuntimeError, match="TEST_VENDOR_MONGO_URI_REQUIRED"):
        _mongo_client_for_uri(" \t")
    assert constructed == []


def test_production_certification_port_is_rejected_before_client_construction(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Port 27027 can never be selected by this certificate."""
    constructed: list[str] = []
    monkeypatch.setattr(
        sys.modules[__name__],
        "MongoClient",
        lambda uri, **kwargs: constructed.append(uri),
    )
    with pytest.raises(RuntimeError, match="TEST_VENDOR_MONGO_URI_NOT_PERMITTED"):
        _mongo_client_for_uri(
            "mongodb://127.0.0.1:27027/?replicaSet=wilsyVendorCertRS"
        )
    assert constructed == []


def test_permitted_loopback_replica_set_uri_is_accepted() -> None:
    """Only an explicit approved local replica-set endpoint is accepted."""
    assert _validate_mongo_uri(
        "mongodb://127.0.0.1:27028/?replicaSet=wilsyVendorCertRS"
    ) == "mongodb://127.0.0.1:27028/?replicaSet=wilsyVendorCertRS"


def test_real_mongo_certificate_commits_a_transaction(
    mongo_context: dict[str, Any],
) -> None:
    """The configured writable replica set accepts durable transaction writes."""
    collection = mongo_context["database"]["issue_300_transaction_probe"]
    probe_id = f"transaction-{uuid.uuid4().hex}"
    with mongo_context["client"].start_session() as session:
        session.start_transaction(
            read_concern=ReadConcern("snapshot"),
            write_concern=WriteConcern(w="majority", j=True),
        )
        collection.insert_one({"_id": probe_id, "committed": True}, session=session)
        session.commit_transaction()
    assert collection.find_one({"_id": probe_id}) == {
        "_id": probe_id,
        "committed": True,
    }


def test_real_mongo_populated_workspace_remains_closed_without_clearance(
    mongo_context: dict[str, Any],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Durable first-class matter stays hidden while clearance is unratified."""
    tenant = f"tenant-{uuid.uuid4().hex}"
    result = _register_intake(
        tenant_id=tenant,
        client=mongo_context["client"],
        lifecycle=mongo_context["lifecycle"],
        suffix="d15b-001",
    )
    _persist_product(
        tenant_id=tenant,
        mongo_context=mongo_context,
        activate=True,
    )
    _active_subscription(tenant_id=tenant, mongo_context=mongo_context)
    locator = LegalOperationsLifecycleRegistry.get_snapshot_evidence_identity(
        result.case_matter,
        mongo_context["lifecycle"],
    )
    assert len(locator) == 128
    assert set(locator) <= set("0123456789abcdef")

    response = _workspace(
        tenant_id=tenant,
        mongo_context=mongo_context,
        monkeypatch=monkeypatch,
    )
    assert response.status_code == 503
    assert response.json() == {
        "detail": "LEGAL_OPERATIONS_WORKSPACE_CONFIDENTIALITY_AUTHORITY_UNAVAILABLE"
    }
    for forbidden in (
        tenant, "matter-d15b-001", "CASE-d15b-001",
        "instruction-d15b-001", "document-d15b-001",
        locator, "evidence_identity", "matters_total",
        "instructions_total", "documents_total",
    ):
        assert forbidden not in response.text


def test_real_mongo_foreign_and_local_matters_stay_hidden_without_clearance(
    mongo_context: dict[str, Any],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Neither own nor foreign matter is disclosed before clearance admission."""
    tenant = f"tenant-{uuid.uuid4().hex}"
    foreign = f"tenant-{uuid.uuid4().hex}"
    _register_intake(
        tenant_id=tenant,
        client=mongo_context["client"],
        lifecycle=mongo_context["lifecycle"],
        suffix="own",
    )
    _register_intake(
        tenant_id=foreign,
        client=mongo_context["client"],
        lifecycle=mongo_context["lifecycle"],
        suffix="foreign",
        opened_at=BASE + timedelta(hours=1),
    )
    _persist_product(
        tenant_id=tenant,
        mongo_context=mongo_context,
        activate=True,
    )
    _active_subscription(tenant_id=tenant, mongo_context=mongo_context)
    response = _workspace(
        tenant_id=tenant,
        mongo_context=mongo_context,
        monkeypatch=monkeypatch,
    )
    assert response.status_code == 503
    assert response.json() == {
        "detail": "LEGAL_OPERATIONS_WORKSPACE_CONFIDENTIALITY_AUTHORITY_UNAVAILABLE"
    }
    for forbidden in (
        tenant, foreign, "matter-own", "matter-foreign",
        "CASE-own", "CASE-foreign", "evidence_identity",
        "matters_total", "instructions_total",
    ):
        assert forbidden not in response.text


def test_real_mongo_corrupt_hidden_matter_stays_non_disclosing(
    mongo_context: dict[str, Any],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Confidentiality containment hides corrupted matter before projection."""
    tenant = f"tenant-{uuid.uuid4().hex}"
    _register_intake(
        tenant_id=tenant,
        client=mongo_context["client"],
        lifecycle=mongo_context["lifecycle"],
        suffix="corrupt",
    )
    _persist_product(tenant_id=tenant, mongo_context=mongo_context, activate=True)
    _active_subscription(tenant_id=tenant, mongo_context=mongo_context)

    result = mongo_context["lifecycle"].update_one(
        {
            "tenant_id": tenant,
            "entity_type": "CaseMatter",
            "entity_identity": "matter-corrupt",
        },
        {"$set": {"p1_payload.state": "BROKEN"}},
    )
    assert result.matched_count == 1
    assert result.modified_count == 1

    response = _workspace(
        tenant_id=tenant,
        mongo_context=mongo_context,
        monkeypatch=monkeypatch,
    )

    assert response.status_code == 503
    assert response.json()["detail"] == (
        "LEGAL_OPERATIONS_WORKSPACE_CONFIDENTIALITY_AUTHORITY_UNAVAILABLE"
    )


def test_real_mongo_absent_and_pending_product_deny_without_workspace_disclosure(
    mongo_context: dict[str, Any],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Exact absence and real PENDING state collapse to one bounded product 403."""
    absent_tenant = f"tenant-absent-{uuid.uuid4().hex}"
    pending_tenant = f"tenant-pending-{uuid.uuid4().hex}"
    _register_intake(
        tenant_id=absent_tenant,
        client=mongo_context["client"],
        lifecycle=mongo_context["lifecycle"],
        suffix="absent-product",
    )
    _register_intake(
        tenant_id=pending_tenant,
        client=mongo_context["client"],
        lifecycle=mongo_context["lifecycle"],
        suffix="pending-product",
        opened_at=BASE + timedelta(hours=1),
    )
    _persist_product(
        tenant_id=pending_tenant,
        mongo_context=mongo_context,
        activate=False,
    )

    for tenant in (absent_tenant, pending_tenant):
        response = _workspace(
            tenant_id=tenant,
            mongo_context=mongo_context,
            monkeypatch=monkeypatch,
        )
        assert response.status_code == 403
        assert response.json() == {"detail": "LEGAL_OPERATIONS_PRODUCT_UNAVAILABLE"}
        assert "matter-" not in response.text
        assert "PENDING" not in response.text


def test_real_mongo_active_entitlement_without_subscription_fails_closed(
    mongo_context: dict[str, Any],
) -> None:
    """D22B5 ACTIVE alone cannot form a complete Legal commercial context."""
    tenant = f"tenant-product-no-subscription-{uuid.uuid4().hex}"
    _persist_product(tenant_id=tenant, mongo_context=mongo_context, activate=True)
    with mongo_context["client"].start_session() as session:
        with pytest.raises(LegalCommercialContextProjectionError) as raised:
            session.with_transaction(
                lambda active_session: resolve_legal_commercial_context(
                    tenant,
                    mongo_context["subscriptions"],
                    mongo_context["entitlement_history"],
                    mongo_context["entitlement_current"],
                    session=active_session,
                )
            )
    assert raised.value.code == "LEGAL_COMMERCIAL_ENTITLEMENT_WITHOUT_ACTIVE_SUBSCRIPTION"


def test_real_mongo_foreign_active_product_cannot_admit_tenant(
    mongo_context: dict[str, Any],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Tenant A's ACTIVE product cannot satisfy tenant B's derived lineage."""
    tenant_a = f"tenant-product-a-{uuid.uuid4().hex}"
    tenant_b = f"tenant-product-b-{uuid.uuid4().hex}"
    _persist_product(tenant_id=tenant_a, mongo_context=mongo_context, activate=True)
    _register_intake(
        tenant_id=tenant_b,
        client=mongo_context["client"],
        lifecycle=mongo_context["lifecycle"],
        suffix="tenant-b",
    )
    response = _workspace(
        tenant_id=tenant_b,
        mongo_context=mongo_context,
        monkeypatch=monkeypatch,
    )
    assert response.status_code == 403
    assert response.json() == {"detail": "LEGAL_OPERATIONS_PRODUCT_UNAVAILABLE"}
    assert tenant_a not in response.text
    assert "matter-tenant-b" not in response.text


def test_real_mongo_product_corruption_is_distinct_commercial_authority_failure(
    mongo_context: dict[str, Any],
) -> None:
    """Corrupt D22 currentness fails closed in the canonical conjunction."""
    tenant = f"tenant-product-corrupt-{uuid.uuid4().hex}"
    _persist_product(tenant_id=tenant, mongo_context=mongo_context, activate=True)
    mutation = mongo_context["entitlement_current"].update_one(
        {"tenant_id": tenant, "entitlement_id": _entitlement_id(tenant)},
        {"$set": {"lifecycle_revision": 99}},
    )
    assert mutation.modified_count == 1
    with mongo_context["client"].start_session() as session:
        with pytest.raises(LegalCommercialContextProjectionError) as raised:
            resolve_legal_commercial_context(
                tenant,
                mongo_context["subscriptions"],
                mongo_context["entitlement_history"],
                mongo_context["entitlement_current"],
                session=session,
            )
    assert raised.value.code == "LEGAL_COMMERCIAL_PRODUCT_AUTHORITY_UNAVAILABLE"


def test_real_mongo_active_product_read_performs_zero_writes(
    mongo_context: dict[str, Any],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Commercial admission reads exact D22 state without mutating its stores."""
    tenant = f"tenant-product-read-{uuid.uuid4().hex}"
    _persist_product(tenant_id=tenant, mongo_context=mongo_context, activate=True)
    _active_subscription(tenant_id=tenant, mongo_context=mongo_context)
    history = mongo_context["entitlement_history"]
    current = mongo_context["entitlement_current"]
    history_before = list(history.find({"tenant_id": tenant}))
    current_before = list(current.find({"tenant_id": tenant}))
    with mongo_context["client"].start_session() as session:
        projection = session.with_transaction(
            lambda active_session: resolve_legal_commercial_context(
                tenant,
                mongo_context["subscriptions"],
                history,
                current,
                session=active_session,
            )
        )
    assert projection.product_available is True
    assert projection.subscription_status.value == "active"
    assert list(history.find({"tenant_id": tenant})) == history_before
    assert list(current.find({"tenant_id": tenant})) == current_before


def test_d15b_certificate_surface_is_frozen() -> None:
    """Preserve D15 provenance and prohibit router write-authority expansion."""
    assert VERSION == "v1.4.0-ISSUE-300-COMBINED-ROUTER-RM-CERT"
    assert legal_router.VERSION == "v1.19.0-L8-6E-D22B5-SUBSCRIPTION-ADMISSION"
    assert not hasattr(legal_router, "insert_one")
    assert not hasattr(legal_router, "update_one")
    assert not hasattr(legal_router, "delete_one")
    assert hasattr(legal_router, "_require_workspace_disclosure_clearance")
    assert hasattr(legal_router, "resolve_workspace_canonical_parents")


# ARTIFACT: test_legal_operations_practice_workspace_real_mongo.py
# VERSION: v1.4.0-ISSUE-300-COMBINED-ROUTER-RM-CERT
# AUTHORITY BOUNDARY: D15 IAM plus same-snapshot D22B5 and canonical subscription conjunction; real-Mongo workspace certificate only
# TENANT POSTURE: exact-tenant durable intake and workspace projection; foreign matter excluded
# FAIL-CLOSED POSTURE: explicit loopback URI, replica-set, transaction, product, projection, locator, corruption, and tenant drift fail
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively
# END OF WILSY OS SOVEREIGN ARTIFACT
