"""Host-backed real-Mongo certificate for the L8-8N screening read route.

TITLE: WILSY OS Legal Conflict Screening Read Router Real-Mongo Certificate
VERSION: v1.0.0-L8-8N-CONFLICT-SCREENING-READ-ROUTER-RM-CERT
AUTHORITY: Host-backed authenticated read-projection certificate only.
EPITOME: Prove physically that immutable tenant-scoped screening rows are
         discoverable through the authenticated bounded HTTP queue without
         cross-tenant leakage or any review/evidence/screening mutation.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tests/integration/test_legal_conflict_screening_read_router_real_mongo.py
COLLABORATION / OWNERSHIP: L8-8E owns screening persistence; this certificate
                            owns only the L8-8N HTTP/read boundary.
CERTIFICATION / UPDATE DATE: 2026-09-25
CHANGELOG: 2026-09-25 v1.0.0-L8-8N-CONFLICT-SCREENING-READ-ROUTER-RM-CERT
           establishes real replica-set tenant isolation, deterministic queue
           ordering, empty state and zero-side-effect evidence.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2; ISO 27001.
SECURITY / PRIVACY POSTURE: UUID-isolated database and synthetic opaque values;
                             no production data, secrets or provider calls.
TENANT BOUNDARY: Registry query and response use one exact authorized tenant.
AUTHORITY BOUNDARY: Read-only certificate; no screening/review/authorization
                    mutation or conflict clearance is created.
FINANCIAL AUTHORITY BOUNDARY: Kennel EOS exclusively owns financial execution.
FAIL-CLOSED DECLARATION: Mongo/auth/session/ordering/leakage/side-effect drift
                         fails this certificate.
"""
from __future__ import annotations

from datetime import datetime, timezone
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
from tools.eos.api.errors import register_error_handlers
from tools.eos.api.tenant_authorization_http import TenantAuthorizationContext
from tools.eos.auth.identity import SovereignIdentity
from tools.eos.auth.principal_status import PrincipalStatus
from tools.eos.auth.tenant_authorization import (
    TenantAuthorizationDecision,
    TenantAuthorizationReason,
)
from tools.eos.legal_operations.domain.legal_conflict_screening import (
    LegalConflictScreeningResult,
    build_legal_conflict_screening,
)
from tools.eos.legal_operations.domain.legal_matter_party import (
    LegalMatterPartyKind,
    LegalMatterPartyRole,
    LegalMatterPartySide,
    register_legal_matter_party,
)
from tools.eos.legal_operations.domain.legal_operations_lifecycle import CaseMatter
from tools.eos.legal_operations.registry import legal_conflict_screening_registry as registry


VERSION = "v1.0.0-L8-8N-CONFLICT-SCREENING-READ-ROUTER-RM-CERT"
MONGO_URI = os.getenv(
    "TEST_VENDOR_MONGO_URI",
    "mongodb://127.0.0.1:27027/?replicaSet=wilsyVendorCertRS",
)
EXPECTED_REPLICA_SET = "wilsyVendorCertRS"
NOW = datetime(2026, 9, 25, 4, 0, tzinfo=timezone.utc)
FINGERPRINT = "a" * 128


@pytest.fixture
def mongo_context() -> Iterator[dict[str, Any]]:
    """Yield one verified writable UUID-isolated database, then drop it."""
    client = MongoClient(
        MONGO_URI,
        serverSelectionTimeoutMS=3000,
        retryWrites=True,
        tz_aware=True,
    )
    database: Any = None
    try:
        try:
            hello = client.admin.command("hello")
        except PyMongoError as error:
            pytest.fail(f"L8_8N_MONGO_RUNTIME_UNAVAILABLE:{type(error).__name__}")
        if hello.get("setName") != EXPECTED_REPLICA_SET:
            pytest.fail("L8_8N_MONGO_REPLICA_SET_MISMATCH")
        if hello.get("isWritablePrimary", hello.get("ismaster")) is not True:
            pytest.fail("L8_8N_MONGO_WRITABLE_PRIMARY_UNAVAILABLE")
        if hello.get("logicalSessionTimeoutMinutes") is None:
            pytest.fail("L8_8N_MONGO_SESSIONS_UNAVAILABLE")
        database = client[f"legal_conflict_screening_read_{uuid.uuid4().hex}"]
        collection = database.get_collection(
            registry.COLLECTION,
            write_concern=WriteConcern(w="majority", j=True),
            read_concern=ReadConcern("majority"),
        )
        registry.ensure_indexes(collection)
        yield {"client": client, "database": database, "collection": collection}
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
    """Build one already-authorized exact-tenant practice context."""
    return TenantAuthorizationContext(
        identity=SovereignIdentity(
            identity_id="principal-law",
            tenant_id=tenant_id,
            username="operator",
            email="operator@example.test",
            auth_method="TEST",
            status=PrincipalStatus.ACTIVE,
        ),
        tenant_id=tenant_id,
        decision=TenantAuthorizationDecision(
            authorized=True,
            reason=TenantAuthorizationReason.AUTHORIZED,
            business_role="tenant_legal_partner",
            authorization_role="LEGAL_PARTNER",
        ),
    )


def _app(
    *,
    tenant_id: str,
    client: MongoClient[Any],
    database: Any,
    monkeypatch: pytest.MonkeyPatch,
) -> FastAPI:
    """Mount the production route with only auth and DB locator seams bound."""
    app = FastAPI()
    app.dependency_overrides[legal_router._INSTRUCTION_READ] = (
        lambda: _context(tenant_id)
    )
    monkeypatch.setattr(legal_router, "_db_handles", lambda: (client, database))
    app.include_router(legal_router.router, prefix="/api")
    return app


def _screening(
    tenant: str,
    *,
    screening_id: str,
    matter_id: str,
    screened_at: datetime,
) -> LegalConflictScreeningResult:
    """Build one canonical REVIEW_REQUIRED result from synthetic party facts."""
    matter = CaseMatter(
        tenant_id=tenant,
        case_matter_id=matter_id,
        matter_reference=f"REF-{matter_id}",
        opened_at=screened_at,
        evidence_reference=f"matter:{matter_id}",
    )
    source = register_legal_matter_party(
        matter=matter,
        party_id=f"party-{screening_id}",
        party_kind=LegalMatterPartyKind.ORGANIZATION,
        party_side=LegalMatterPartySide.CLIENT_SIDE,
        matter_role=LegalMatterPartyRole.CLIENT,
        subject_reference="organization:synthetic",
        subject_identity_fingerprint=FINGERPRINT,
        display_name="Synthetic Legal Party",
        registered_at=screened_at,
        source_evidence_reference=f"party:{screening_id}",
        source_evidence_fingerprint=FINGERPRINT,
    )
    match = register_legal_matter_party(
        matter=CaseMatter(
            tenant_id=tenant,
            case_matter_id=f"{matter_id}-match",
            matter_reference=f"REF-{matter_id}-MATCH",
            opened_at=screened_at,
            evidence_reference=f"matter:{matter_id}-match",
        ),
        party_id=f"party-{screening_id}-match",
        party_kind=LegalMatterPartyKind.ORGANIZATION,
        party_side=LegalMatterPartySide.ADVERSE_SIDE,
        matter_role=LegalMatterPartyRole.RESPONDENT,
        subject_reference="organization:synthetic",
        subject_identity_fingerprint=FINGERPRINT,
        display_name="Synthetic Legal Party",
        registered_at=screened_at,
        source_evidence_reference=f"party:{screening_id}-match",
        source_evidence_fingerprint=FINGERPRINT,
    )
    return build_legal_conflict_screening(
        source_party=source,
        occurrences=(source, match),
        screening_id=screening_id,
        screened_at=screened_at,
        source_evidence_reference=f"screening:{screening_id}",
        source_evidence_fingerprint=FINGERPRINT,
    )


def _commit(
    context: dict[str, Any],
    value: LegalConflictScreeningResult,
) -> None:
    """Persist one synthetic screening through the canonical registry only."""
    with context["client"].start_session() as session:
        with session.start_transaction():
            registry.persist_screening(
                value,
                context["collection"],
                session=session,
            )


def test_real_mongo_route_is_tenant_scoped_ordered_bounded_and_read_only(
    mongo_context: dict[str, Any],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """The authenticated route exposes only exact tenant review-queue rows."""
    tenant = f"tenant-a-{uuid.uuid4().hex}"
    foreign = f"tenant-b-{uuid.uuid4().hex}"
    values = (
        _screening(
            tenant,
            screening_id="screening-old",
            matter_id="matter-old",
            screened_at=NOW,
        ),
        _screening(
            tenant,
            screening_id="screening-new",
            matter_id="matter-new",
            screened_at=NOW.replace(day=26),
        ),
        _screening(
            foreign,
            screening_id="screening-foreign",
            matter_id="matter-foreign",
            screened_at=NOW.replace(day=27),
        ),
    )
    for value in values:
        _commit(mongo_context, value)
    before = mongo_context["collection"].count_documents({})

    with TestClient(
        _app(
            tenant_id=tenant,
            client=mongo_context["client"],
            database=mongo_context["database"],
            monkeypatch=monkeypatch,
        )
    ) as client:
        response = client.get(
            "/api/legal-operations/conflict-screenings?limit=1"
            "&tenant_id=tenant-forged"
        )

    assert response.status_code == 200
    body = response.json()
    assert body["tenant_id"] == tenant
    assert [row["screening_id"] for row in body["screenings"]] == [
        "screening-new"
    ]
    assert set(body["screenings"][0]) == {
        "screening_id",
        "source_case_matter_id",
        "status",
        "screened_at",
    }
    assert mongo_context["collection"].count_documents({}) == before
    assert mongo_context["database"].get_collection("legal_conflict_reviews").count_documents({}) == 0


def test_real_mongo_empty_tenant_is_successful_empty_projection(
    mongo_context: dict[str, Any],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """A tenant without screenings receives the canonical empty queue."""
    tenant = f"tenant-empty-{uuid.uuid4().hex}"
    with TestClient(
        _app(
            tenant_id=tenant,
            client=mongo_context["client"],
            database=mongo_context["database"],
            monkeypatch=monkeypatch,
        )
    ) as client:
        response = client.get("/api/legal-operations/conflict-screenings")
    assert response.status_code == 200
    assert response.json()["screenings"] == []


def test_real_mongo_missing_authentication_is_denied(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """The route does not expose screening rows without canonical auth."""
    app = FastAPI()
    register_error_handlers(app, debug=False)
    app.include_router(legal_router.router, prefix="/api")
    with TestClient(app) as client:
        response = client.get("/api/legal-operations/conflict-screenings")
    assert response.status_code == 401


def test_real_mongo_certificate_surface_is_frozen() -> None:
    """Certificate binds the production route release and remains read-only."""
    assert VERSION == "v1.0.0-L8-8N-CONFLICT-SCREENING-READ-ROUTER-RM-CERT"
    assert legal_router.VERSION == "v1.9.0-L8-8N-CONFLICT-SCREENING-READ-API"


"""
ARTIFACT: test_legal_conflict_screening_read_router_real_mongo.py
VERSION: v1.0.0-L8-8N-CONFLICT-SCREENING-READ-ROUTER-RM-CERT
AUTHORITY BOUNDARY: real-Mongo screening read certificate only
TENANT POSTURE: exact authorized tenant and UUID-isolated database
FAIL-CLOSED POSTURE: host/transaction/projection/leakage/side-effect drift fails
FINANCIAL EXECUTION AUTHORITY: none; Kennel EOS remains exclusive
END OF WILSY OS SOVEREIGN ARTIFACT
"""
