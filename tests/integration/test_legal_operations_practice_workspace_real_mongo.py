"""D15 host-backed real-Mongo certificate for first-class Legal Practice matters.

TITLE: WILSY OS First-Class Legal Matter Workspace Real-Mongo Certificate
VERSION: v1.0.0-L8-7D15-FIRST-CLASS-MATTER-WORKSPACE-RM-CERT
AUTHORITY: Host-backed certificate for durable CaseMatter projection through the
           authenticated Legal Practice workspace read boundary.
EPITOME: Prove that one real L8-2 intake transaction durably creates CaseMatter,
         LegalInstruction, ProcessDocument and REGISTERED custody evidence and
         that the real D15 /workspace snapshot transaction returns CaseMatter as
         first-class exact-tenant truth with its persisted opaque SHA3-512
         evidence locator. Also prove foreign-tenant exclusion and corruption
         rejection without browser/client reconstruction or fallback.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tests/integration/test_legal_operations_practice_workspace_real_mongo.py
COLLABORATION / OWNERSHIP: L8-2 owns intake composition; P1 owns lifecycle value
                            semantics; P2 owns immutable persistence/hydration and
                            exact snapshot evidence locators; D15 owns read-only
                            workspace composition; tenant authorization remains
                            the access authority outside this persistence-focused
                            certificate.
CERTIFICATION / UPDATE DATE: 2026-09-24
CHANGELOG: 2026-09-24 v1.0.0-L8-7D15-FIRST-CLASS-MATTER-WORKSPACE-RM-CERT
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
import uuid

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from pymongo import MongoClient
from pymongo.errors import PyMongoError
from pymongo.read_concern import ReadConcern
from pymongo.write_concern import WriteConcern

import tools.eos.api.legal_operations_router as legal_router
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


VERSION = "v1.0.0-L8-7D15-FIRST-CLASS-MATTER-WORKSPACE-RM-CERT"
MONGO_URI = os.getenv(
    "TEST_VENDOR_MONGO_URI",
    "mongodb://127.0.0.1:27027/?replicaSet=wilsyVendorCertRS",
)
EXPECTED_REPLICA_SET = "wilsyVendorCertRS"
BASE = datetime(2026, 9, 24, 6, 0, tzinfo=timezone.utc)


@pytest.fixture
def mongo_context() -> Iterator[dict[str, Any]]:
    """Yield a verified writable UUID-isolated database; host failure fails."""
    client = MongoClient(
        MONGO_URI,
        serverSelectionTimeoutMS=3000,
        retryWrites=True,
    )
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

        database = client[f"legal_ops_d15b_workspace_{uuid.uuid4().hex}"]
        lifecycle = database.get_collection(
            COLLECTION,
            write_concern=WriteConcern(w="majority", j=True),
            read_concern=ReadConcern("majority"),
        )
        LegalOperationsLifecycleRegistry.ensure_indexes(lifecycle)
        yield {
            "client": client,
            "database": database,
            "lifecycle": lifecycle,
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


def test_real_mongo_intake_case_matter_is_first_class_workspace_truth(
    mongo_context: dict[str, Any],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Durable L8-2 intake is directly discoverable as one D15 matter row."""
    tenant = f"tenant-{uuid.uuid4().hex}"
    result = _register_intake(
        tenant_id=tenant,
        client=mongo_context["client"],
        lifecycle=mongo_context["lifecycle"],
        suffix="d15b-001",
    )
    locator = LegalOperationsLifecycleRegistry.get_snapshot_evidence_identity(
        result.case_matter,
        mongo_context["lifecycle"],
    )

    response = _workspace(
        tenant_id=tenant,
        mongo_context=mongo_context,
        monkeypatch=monkeypatch,
    )

    assert response.status_code == 200
    body = response.json()
    assert body["schema"] == "WILSY-LEGAL-OPERATIONS-PRACTICE-WORKSPACE/V2"
    assert body["version"] == "v1.8.0-L8-7D15-FIRST-CLASS-MATTER-WORKSPACE-API"
    assert body["tenant_id"] == tenant
    assert body["visibility"] == "LEGAL_PRACTICE_WORKSPACE"
    assert body["summary"]["matters_total"] == 1
    assert body["summary"]["matters_open"] == 1
    assert body["summary"]["matters_closed"] == 0
    assert body["summary"]["instructions_total"] == 1
    assert body["summary"]["documents_total"] == 1
    assert body["summary"]["attempts_total"] == 0
    assert body["summary"]["executions_total"] == 0
    assert body["summary"]["returns_total"] == 0
    assert body["matters"] == [
        {
            "case_matter_id": "matter-d15b-001",
            "matter_reference": "CASE-d15b-001",
            "opened_at": BASE.isoformat(),
            "state": "OPEN",
            "evidence_identity": locator,
        }
    ]
    assert body["instructions"][0]["case_matter_id"] == "matter-d15b-001"
    assert body["documents"][0]["case_matter_id"] == "matter-d15b-001"
    assert len(locator) == 128
    assert set(locator) <= set("0123456789abcdef")

    serialized = str(body).lower()
    for forbidden in (
        "matter-proof-d15b-001",
        "instruction-proof-d15b-001",
        "document-proof-d15b-001",
        "evidence_reference",
        "transition_history",
        "payment",
        "settlement",
        "paid_state",
    ):
        assert forbidden not in serialized


def test_real_mongo_workspace_excludes_foreign_case_matter(
    mongo_context: dict[str, Any],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """One tenant workspace never includes another tenant's durable matter."""
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

    response = _workspace(
        tenant_id=tenant,
        mongo_context=mongo_context,
        monkeypatch=monkeypatch,
    )

    assert response.status_code == 200
    body = response.json()
    assert body["summary"]["matters_total"] == 1
    assert [item["case_matter_id"] for item in body["matters"]] == ["matter-own"]
    assert "matter-foreign" not in str(body)
    assert foreign not in str(body)


def test_real_mongo_corrupt_case_matter_rejects_workspace_without_fallback(
    mongo_context: dict[str, Any],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Corrupted durable matter evidence makes D15 fail closed, never disappear."""
    tenant = f"tenant-{uuid.uuid4().hex}"
    _register_intake(
        tenant_id=tenant,
        client=mongo_context["client"],
        lifecycle=mongo_context["lifecycle"],
        suffix="corrupt",
    )

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
    assert response.json()["detail"] == "LEGAL_OPERATIONS_WORKSPACE_EVIDENCE_UNAVAILABLE"


def test_d15b_certificate_surface_is_frozen() -> None:
    """Certificate remains bound to the intended production D15 contract."""
    assert VERSION == "v1.0.0-L8-7D15-FIRST-CLASS-MATTER-WORKSPACE-RM-CERT"
    assert legal_router.VERSION == "v1.8.0-L8-7D15-FIRST-CLASS-MATTER-WORKSPACE-API"
    assert not hasattr(legal_router, "insert_one")
    assert not hasattr(legal_router, "update_one")
    assert not hasattr(legal_router, "delete_one")


# ARTIFACT: test_legal_operations_practice_workspace_real_mongo.py
# VERSION: v1.0.0-L8-7D15-FIRST-CLASS-MATTER-WORKSPACE-RM-CERT
# AUTHORITY BOUNDARY: D15 first-class matter workspace real-Mongo certificate only
# TENANT POSTURE: exact-tenant durable intake and workspace projection; foreign matter excluded
# FAIL-CLOSED POSTURE: host/transaction/projection/locator/corruption/tenant drift fails
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively
# END OF WILSY OS SOVEREIGN ARTIFACT
