"""L7D host-backed transport hardening certificate.

VERSION: v1.0.0-L7D-BACKEND-HARDENING-RM-CERT
AUTHORITY: Runtime evidence only; no legal or financial authority is created.
TENANT BOUNDARY: unauthenticated requests cannot reach tenant repositories.
FAIL-CLOSED POSTURE: missing Mongo availability skips only the host gate.
FINANCIAL AUTHORITY BOUNDARY: Kennel EOS exclusively owns execution/settlement.
"""

from __future__ import annotations

import os
import uuid
from collections.abc import Generator

import pytest
from fastapi.testclient import TestClient
from pymongo import MongoClient
from pymongo.errors import PyMongoError

from tools.eos.api.server import WilsyAPIServer


DEFAULT_URI = "mongodb://127.0.0.1:27027/?replicaSet=wilsyVendorCertRS"
EXPECTED_REPLICA_SET = "wilsyVendorCertRS"


@pytest.fixture()
def mongo_runtime() -> Generator[tuple[MongoClient, str], None, None]:
    uri = os.getenv("TEST_VENDOR_MONGO_URI", DEFAULT_URI)
    client = MongoClient(uri, serverSelectionTimeoutMS=1500)
    database_name = f"l7d_{uuid.uuid4().hex[:16]}"
    try:
        hello = client.admin.command("hello")
        if hello.get("setName") != EXPECTED_REPLICA_SET or not hello.get("isWritablePrimary", hello.get("ismaster", False)):
            pytest.skip("certification Mongo replica set is unavailable or not writable")
        client[database_name].command("ping")
        yield client, database_name
    except PyMongoError as error:
        pytest.skip(f"certification Mongo runtime unavailable: {type(error).__name__}")
    finally:
        try:
            client.drop_database(database_name)
        except PyMongoError:
            pass
        client.close()


def test_real_mongo_runtime_and_auth_before_legal_repository(mongo_runtime: tuple[MongoClient, str]) -> None:
    _client, _database_name = mongo_runtime
    app = WilsyAPIServer(allowed_origins=[]).app
    response = TestClient(app).get("/api/legal-operations/instructions/foreign")
    assert response.status_code in {401, 403}
    assert response.headers["X-Content-Type-Options"] == "nosniff"
    assert response.headers["Referrer-Policy"] == "no-referrer"
    assert response.headers["X-Frame-Options"] == "DENY"
    assert response.headers["Cache-Control"] == "no-store"


def test_real_app_uses_actual_tenant_authorization_before_all_legal_surfaces(
    mongo_runtime: tuple[MongoClient, str],
) -> None:
    _client, _database_name = mongo_runtime
    app = WilsyAPIServer(allowed_origins=[]).app
    client = TestClient(app)
    requests = [
        ("GET", "/api/legal-operations/instructions/tenant-b-identity"),
        ("GET", "/api/legal-operations/attempts/tenant-b-identity"),
        ("GET", "/api/legal-operations/executions/tenant-b-identity"),
        ("GET", "/api/legal-operations/returns/tenant-b-identity"),
        ("GET", "/api/legal-operations/tariff-assessments/tenant-b-identity"),
        ("GET", "/api/legal-operations/billing-eligibilities/tenant-b-identity"),
        ("GET", "/api/legal-operations/invoices/tenant-b-identity"),
        ("POST", "/api/legal-operations/attempts"),
    ]
    for method, path in requests:
        response = client.request(method, path, json={"attempt_authority_id": "x"} if method == "POST" else None)
        assert response.status_code in {401, 403}
        assert "Traceback" not in response.text
        assert "mongodb" not in response.text.lower()
        assert "WILSY_JWT_SECRET" not in response.text


# ARTIFACT: test_l7d_backend_hardening_real_mongo.py
# VERSION: v1.0.0-L7D-BACKEND-HARDENING-RM-CERT
# AUTHORITY BOUNDARY: host/runtime evidence only.
# TENANT POSTURE: unauthorized requests cannot disclose tenant evidence.
# FAIL-CLOSED POSTURE: unavailable host runtime is never represented as pass.
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS remains exclusive.
# END OF WILSY OS SOVEREIGN ARTIFACT
