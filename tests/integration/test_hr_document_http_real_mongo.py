"""WILSY OS — HR document HTTP real-Mongo integration certificate.

TITLE:
    HR Document HTTP Real-Mongo Integration Certificate

VERSION:
    v1.0.0-P0-C12F7C-D1-R3-R5-REAL-MONGO-HTTP

AUTHORITY:
    Wilsy OS Core Governance

PURPOSE:
    Certify F7C HTTP tenant/document read behavior against a real MongoDB
    replica-set persistence surface while preserving canonical F6F upload
    ownership.

EPITOME:
    HTTP projection consumes sovereign persisted HR document truth; it does
    not invent storage, authorization, reconciliation, or financial truth.

ABSOLUTE CANONICAL PATH:
    tests/integration/test_hr_document_http_real_mongo.py

CERTIFICATION DATE:
    2026-10-05

CHANGELOG:
    v1.0.0-P0-C12F7C-D1-R3-R5-REAL-MONGO-HTTP
    - Initial real-Mongo HTTP read certificate.
    - Uses canonical HrDocument constructor directly.
    - Uses canonical persist_document registry mutation.
    - Preserves F6F as POST persistence owner.
    - Excludes real AWS provider execution.

SECURITY / PRIVACY POSTURE:
    Tenant scoped. Cross-tenant and cross-employee exact reads remain
    non-disclosing.

TENANT BOUNDARY:
    Every real persistence lookup remains explicitly tenant scoped.

AUTHORITY BOUNDARY:
    HTTP derives read authority from persisted document sensitivity.
    POST durability remains owned by F6F ingestion orchestration.

FINANCIAL AUTHORITY BOUNDARY:
    No billing, payment, settlement, or financial execution authority.
    Kennel EOS remains exclusive financial execution authority.

NO EVIDENCE = NO FACT.
"""

from __future__ import annotations

import hashlib
import inspect
import os
from collections.abc import Iterator
from datetime import datetime, timezone
from typing import Any
from uuid import uuid4

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from pymongo import MongoClient

import tools.eos.api.hr_document_router as http
from tools.eos.saas.domain.hr_document import (
    HrDocument,
    HrDocumentClass,
    sensitivity_for_document_class,
)
from tools.eos.saas.hr.hr_document_registry import (
    ensure_indexes,
    persist_document,
)


MONGO_URI = os.environ.get(
    "TEST_VENDOR_MONGO_URI",
    "mongodb://127.0.0.1:27027/?replicaSet=wilsyVendorCertRS",
)


def _digest(seed: str) -> str:
    return hashlib.sha3_512(
        seed.encode("utf-8")
    ).hexdigest()


def _document(
    *,
    tenant_id: str,
    employee_id: str,
    document_id: str,
    document_version_id: str,
) -> HrDocument:
    document_class = HrDocumentClass.EMPLOYMENT_CONTRACT
    sensitivity = sensitivity_for_document_class(document_class)

    return HrDocument(
        tenant_id=tenant_id,
        employee_id=employee_id,
        document_id=document_id,
        document_version_id=document_version_id,
        document_class=document_class,
        sensitivity=sensitivity,
        original_filename=f"{document_version_id}.pdf",
        media_type="application/pdf",
        byte_length=32,
        content_digest_sha3_512=_digest(
            f"content:{document_version_id}"
        ),
        storage_provider_id="s3",
        storage_object_reference=(
            f"hr/{tenant_id}/{document_version_id}"
        ),
        object_version_reference=(
            f"object-version-{document_version_id}"
        ),
        provider_integrity_reference=(
            f"integrity-{document_version_id}"
        ),
        created_at=datetime(
            2026,
            10,
            5,
            12,
            0,
            0,
            tzinfo=timezone.utc,
        ),
        created_by_principal_id="principal-http-real-mongo",
        retention_until=None,
        legal_hold=False,
        supersedes_version_id=None,
    )


def _persist(
    *,
    client: MongoClient[Any],
    collection: Any,
    document: HrDocument,
) -> HrDocument:
    with client.start_session() as session:
        with session.start_transaction():
            return persist_document(
                document,
                collection,
                session=session,
            )


@pytest.fixture()
def mongo_context() -> Iterator[
    tuple[MongoClient[Any], Any, Any]
]:
    """Yield one UUID-isolated database on the certified replica set."""

    client: MongoClient[Any] = MongoClient(
        MONGO_URI,
        serverSelectionTimeoutMS=5000,
    )

    hello = client.admin.command("hello")

    assert hello.get("ok") == 1
    assert hello.get("setName") == "wilsyVendorCertRS"
    assert bool(hello.get("isWritablePrimary"))

    database_name = (
        "wilsy_p0_c12f7c_d1_http_"
        + uuid4().hex
    )

    database = client[database_name]
    collection = database.get_collection("hr_documents")

    try:
        ensure_indexes(collection)
        yield client, database, collection

    finally:
        client.drop_database(database_name)
        client.close()


@pytest.fixture()
def app() -> FastAPI:
    """Expose only the canonical production HR document router."""

    application = FastAPI()
    application.include_router(http.router)

    application.dependency_overrides[
        http.get_current_identity
    ] = lambda: object()

    return application


@pytest.fixture()
def client(app: FastAPI) -> Iterator[TestClient]:
    """Yield the synchronous ASGI certificate client."""

    with TestClient(app) as value:
        yield value


def _bind_real_mongo(
    monkeypatch: pytest.MonkeyPatch,
    mongo_context: tuple[MongoClient[Any], Any, Any],
) -> tuple[MongoClient[Any], Any, Any]:
    client, database, collection = mongo_context

    monkeypatch.setattr(
        http,
        "_runtime_database",
        lambda: (
            client,
            collection,
            database,
        ),
    )

    return client, database, collection


def _allow_all(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    async def allow(**_: Any) -> None:
        return None

    monkeypatch.setattr(
        http,
        "_authorize",
        allow,
    )


def test_real_mongo_employee_list_is_tenant_and_employee_scoped(
    client: TestClient,
    mongo_context: tuple[MongoClient[Any], Any, Any],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    mongo_client, _, collection = _bind_real_mongo(
        monkeypatch,
        mongo_context,
    )
    _allow_all(monkeypatch)

    wanted = _document(
        tenant_id="tenant-http-real-a",
        employee_id="employee-http-real-a",
        document_id="document-http-real-a",
        document_version_id="version-http-real-a",
    )

    cross_tenant = _document(
        tenant_id="tenant-http-real-b",
        employee_id=wanted.employee_id,
        document_id="document-http-real-b",
        document_version_id="version-http-real-b",
    )

    cross_employee = _document(
        tenant_id=wanted.tenant_id,
        employee_id="employee-http-real-b",
        document_id="document-http-real-c",
        document_version_id="version-http-real-c",
    )

    for value in (
        wanted,
        cross_tenant,
        cross_employee,
    ):
        _persist(
            client=mongo_client,
            collection=collection,
            document=value,
        )

    response = client.get(
        f"/api/hr/documents/employees/{wanted.employee_id}",
        headers={"X-Tenant-ID": wanted.tenant_id},
    )

    assert response.status_code == 200

    payload = response.json()

    assert isinstance(payload, list)
    assert len(payload) == 1
    assert payload[0]["tenant_id"] == wanted.tenant_id
    assert payload[0]["employee_id"] == wanted.employee_id
    assert (
        payload[0]["document_version_id"]
        == wanted.document_version_id
    )

    assert collection.count_documents({}) == 3


def test_real_mongo_document_history_is_exactly_scoped(
    client: TestClient,
    mongo_context: tuple[MongoClient[Any], Any, Any],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    mongo_client, _, collection = _bind_real_mongo(
        monkeypatch,
        mongo_context,
    )
    _allow_all(monkeypatch)

    first = _document(
        tenant_id="tenant-http-history",
        employee_id="employee-http-history",
        document_id="document-http-history",
        document_version_id="version-http-history-1",
    )

    second = _document(
        tenant_id=first.tenant_id,
        employee_id=first.employee_id,
        document_id=first.document_id,
        document_version_id="version-http-history-2",
    )

    unrelated = _document(
        tenant_id=first.tenant_id,
        employee_id=first.employee_id,
        document_id="document-http-history-other",
        document_version_id="version-http-history-other",
    )

    for value in (
        first,
        second,
        unrelated,
    ):
        _persist(
            client=mongo_client,
            collection=collection,
            document=value,
        )

    response = client.get(
        (
            f"/api/hr/documents/employees/{first.employee_id}"
            f"/documents/{first.document_id}/versions"
        ),
        headers={"X-Tenant-ID": first.tenant_id},
    )

    assert response.status_code == 200

    assert {
        row["document_version_id"]
        for row in response.json()
    } == {
        first.document_version_id,
        second.document_version_id,
    }


def test_real_mongo_wrong_employee_exact_read_is_404_before_provider(
    client: TestClient,
    mongo_context: tuple[MongoClient[Any], Any, Any],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    mongo_client, _, collection = _bind_real_mongo(
        monkeypatch,
        mongo_context,
    )
    _allow_all(monkeypatch)

    document = _document(
        tenant_id="tenant-http-download",
        employee_id="employee-http-owner",
        document_id="document-http-download",
        document_version_id="version-http-download",
    )

    _persist(
        client=mongo_client,
        collection=collection,
        document=document,
    )

    provider_called = False

    def forbidden_provider(
        *_: Any,
        **__: Any,
    ) -> bytes:
        nonlocal provider_called
        provider_called = True
        raise AssertionError(
            "Provider executed before employee scope passed."
        )

    monkeypatch.setattr(
        http,
        "_read_document_bytes",
        forbidden_provider,
    )

    response = client.get(
        (
            "/api/hr/documents/employees/"
            "employee-http-attacker/"
            f"versions/{document.document_version_id}/content"
        ),
        headers={"X-Tenant-ID": document.tenant_id},
    )

    assert response.status_code == 404
    assert provider_called is False


def test_real_mongo_cross_tenant_exact_read_is_404(
    client: TestClient,
    mongo_context: tuple[MongoClient[Any], Any, Any],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    mongo_client, _, collection = _bind_real_mongo(
        monkeypatch,
        mongo_context,
    )
    _allow_all(monkeypatch)

    document = _document(
        tenant_id="tenant-http-source",
        employee_id="employee-http-source",
        document_id="document-http-source",
        document_version_id="version-http-source",
    )

    _persist(
        client=mongo_client,
        collection=collection,
        document=document,
    )

    response = client.get(
        (
            f"/api/hr/documents/employees/{document.employee_id}"
            f"/versions/{document.document_version_id}/content"
        ),
        headers={
            "X-Tenant-ID": "tenant-http-attacker",
        },
    )

    assert response.status_code == 404


def test_real_mongo_authorization_uses_persisted_sensitivity(
    client: TestClient,
    mongo_context: tuple[MongoClient[Any], Any, Any],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    mongo_client, _, collection = _bind_real_mongo(
        monkeypatch,
        mongo_context,
    )

    document = _document(
        tenant_id="tenant-http-sensitive",
        employee_id="employee-http-sensitive",
        document_id="document-http-sensitive",
        document_version_id="version-http-sensitive",
    )

    _persist(
        client=mongo_client,
        collection=collection,
        document=document,
    )

    observed: list[dict[str, Any]] = []

    async def authorize(**kwargs: Any) -> None:
        observed.append(kwargs)

    monkeypatch.setattr(
        http,
        "_authorize",
        authorize,
    )

    response = client.get(
        f"/api/hr/documents/employees/{document.employee_id}",
        headers={"X-Tenant-ID": document.tenant_id},
    )

    assert response.status_code == 200
    assert len(response.json()) == 1
    assert len(observed) == 1

    assert observed[0]["tenant_id"] == document.tenant_id
    assert observed[0]["sensitivity"] == document.sensitivity
    assert observed[0]["access"] == "read"


def test_upload_retains_canonical_f6f_boundary() -> None:
    """HTTP POST delegates to F6F rather than duplicating persistence."""

    source = inspect.getsource(http.upload_hr_document)

    assert "_run_ingestion" in source
    assert "HrDocumentS3StorageAdapter" in source

    lowered = source.lower()

    assert "delete" not in lowered
    assert "billing" not in lowered
    assert "settlement" not in lowered


# =============================================================================
# WILSY OS SOVEREIGN ARTIFACT SEAL
# =============================================================================
#
# ARTIFACT:
#   HR Document HTTP Real-Mongo Integration Certificate
#
# VERSION:
#   v1.0.0-P0-C12F7C-D1-R3-R5-REAL-MONGO-HTTP
#
# AUTHORITY BOUNDARY:
#   HTTP presentation and tenant-scoped Mongo read evidence only.
#   F6F remains canonical POST durability owner.
#
# TENANT POSTURE:
#   Tenant-scoped and cross-tenant non-disclosing.
#
# FAIL-CLOSED POSTURE:
#   YES
#
# FINANCIAL EXECUTION AUTHORITY:
#   Kennel EOS exclusively.
#
# END OF WILSY OS SOVEREIGN ARTIFACT
# =============================================================================
