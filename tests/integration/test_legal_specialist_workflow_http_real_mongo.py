"""
TITLE: WILSY OS Legal Specialist Workflow HTTP Real-Mongo Certificate
VERSION: v1.0.0-P2-LEGAL-SPECIALIST-WORKFLOW-HTTP-REAL-MONGO
AUTHORITY: Evidence-only certification of the authenticated read runtime.
EPITOME: Prove the mounted HTTP projection composes the actual registry graph
         inside one caller-owned snapshot transaction without creating truth.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tests/integration/test_legal_specialist_workflow_http_real_mongo.py
COLLABORATION / OWNERSHIP: Python EOS API and canonical Legal registries.
CERTIFICATION / UPDATE DATE: 2026-10-18
CHANGELOG: v1.0.0 establishes exact-tenant authenticated empty-projection proof
           against a disposable writable Mongo replica set.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2.
TENANT BOUNDARY: Authenticated context is the sole tenant/principal source.
AUTHORITY BOUNDARY: Read-only projection; no work, workflow or IAM mutation.
FINANCIAL AUTHORITY BOUNDARY: Kennel EOS exclusively owns execution.
"""

from __future__ import annotations

import os
import uuid
from types import SimpleNamespace
from typing import Any, Iterator

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from pymongo import MongoClient

import tools.eos.api.legal_operations_router as legal_router


MONGO_URI = os.environ["TEST_LEGAL_SPECIALIST_HTTP_MONGO_URI"]
EXPECTED_REPLICA_SET = os.environ[
    "TEST_LEGAL_SPECIALIST_HTTP_MONGO_REPLICA_SET"
]


@pytest.fixture
def mongo_runtime(monkeypatch: Any) -> Iterator[tuple[MongoClient[Any], Any]]:
    client: MongoClient[Any] = MongoClient(
        MONGO_URI,
        serverSelectionTimeoutMS=3000,
        connectTimeoutMS=3000,
        tz_aware=True,
    )
    hello = client.admin.command("hello")
    assert hello.get("setName") == EXPECTED_REPLICA_SET
    assert hello.get("isWritablePrimary") is True

    database = client[
        "wilsy_p2_specialist_http_" + uuid.uuid4().hex
    ]
    monkeypatch.setattr(
        legal_router,
        "_db_handles",
        lambda: (client, database),
    )
    try:
        yield client, database
    finally:
        client.drop_database(database.name)
        client.close()


def _context() -> Any:
    return SimpleNamespace(
        tenant_id="tenant-certified",
        identity=SimpleNamespace(identity_id="principal-certified"),
    )


def test_authenticated_actual_registry_graph_returns_truthful_empty_projection(
    mongo_runtime: tuple[MongoClient[Any], Any],
) -> None:
    _, database = mongo_runtime
    app = FastAPI()
    app.dependency_overrides[legal_router._PRODUCTIVE_WORK_READ] = _context
    app.include_router(legal_router.router, prefix="/api")

    before = set(database.list_collection_names())
    with TestClient(app) as http:
        response = http.get(
            "/api/legal-operations/specialist-workflow"
            "?tenant_id=foreign&principal_id=foreign"
        )
    after = set(database.list_collection_names())

    assert response.status_code == 200
    body = response.json()
    assert body["tenant_id"] == "tenant-certified"
    assert body["principal_id"] == "principal-certified"
    assert body["rows"] == []
    assert body["http_version"] == (
        "v1.0.0-P2-LEGAL-SPECIALIST-WORKFLOW-HTTP"
    )
    assert "foreign" not in response.text
    assert after == before


# ==============================================================================
# WILSY OS SOVEREIGN ARTIFACT SEAL
# ==============================================================================
# ARTIFACT: test_legal_specialist_workflow_http_real_mongo.py
# VERSION: v1.0.0-P2-LEGAL-SPECIALIST-WORKFLOW-HTTP-REAL-MONGO
# AUTHORITY BOUNDARY: Authenticated read runtime evidence only
# TENANT POSTURE: Exact context-derived tenant and principal only
# FAIL-CLOSED POSTURE: Missing topology or transaction prevents certification
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively
# END OF WILSY OS SOVEREIGN ARTIFACT
