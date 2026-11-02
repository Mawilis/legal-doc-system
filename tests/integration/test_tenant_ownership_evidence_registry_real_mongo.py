"""Real-replica-set certification for ownership evidence registry boundaries."""
from __future__ import annotations

import os
import uuid
from collections.abc import Iterator
from types import SimpleNamespace
from typing import Any
from urllib.parse import urlparse

import pytest
from pymongo import MongoClient

from tools.eos.auth.tenant_ownership_evidence_registry import (
    TenantOwnershipEvidencePersistenceError,
    TenantOwnershipEvidenceRegistry,
    TenantOwnershipEvidenceTransactionRequiredError,
)

MONGO_URI_ENV = "WILSY_ISSUE_300_REAL_MONGO_URI"
EXPECTED_REPLICA_SET = "wilsyVendorCertRS"


@pytest.fixture
def ownership_registry() -> Iterator[tuple[MongoClient, TenantOwnershipEvidenceRegistry, str]]:
    uri = os.environ.get(MONGO_URI_ENV)
    if not uri:
        pytest.fail(f"{MONGO_URI_ENV}_REQUIRED_FOR_REAL_MONGO_CERTIFICATE")
    parsed = urlparse(uri)
    if parsed.hostname not in {"127.0.0.1", "localhost", "::1"} or parsed.port is None:
        pytest.fail("ISSUE_300_LOOPBACK_MONGO_WITH_EXPLICIT_PORT_REQUIRED")
    client = MongoClient(uri, serverSelectionTimeoutMS=3000)
    database_name = f"issue_300_ownership_registry_{uuid.uuid4().hex}"
    try:
        hello = client.admin.command("hello")
        if hello.get("setName") != EXPECTED_REPLICA_SET or hello.get("isWritablePrimary") is not True:
            pytest.fail("ISSUE_300_APPROVED_DISPOSABLE_REPLICA_SET_REQUIRED")
        database = client[database_name]
        registry = TenantOwnershipEvidenceRegistry(
            database["tenant_ownership_evidence_history"],
            database["tenant_ownership_current"],
        )
        registry.ensure_indexes()
        yield client, registry, database_name
    finally:
        client.drop_database(database_name)
        client.close()


def test_real_mongo_indexes_and_empty_tenant_history_are_exact(
    ownership_registry: tuple[MongoClient, TenantOwnershipEvidenceRegistry, str],
) -> None:
    client, registry, database_name = ownership_registry
    tenant_id = f"tenant-{uuid.uuid4().hex}"
    with client.start_session() as session:
        with session.start_transaction():
            assert registry.current(tenant_id=tenant_id, session=session) is None
            assert registry.history(tenant_id=tenant_id, session=session) == ()
    database = client[database_name]
    history_indexes = database["tenant_ownership_evidence_history"].index_information()
    assert "tenant_ownership_tenant_evidence_unique" in history_indexes
    assert "tenant_ownership_tenant_command_unique" in history_indexes
    assert "tenant_ownership_tenant_revision_unique" in history_indexes
    assert database["tenant_ownership_evidence_history"].count_documents({}) == 0
    assert database["tenant_ownership_current"].count_documents({}) == 0


def test_real_mongo_rejects_unverified_caller_shaped_evidence_without_writes(
    ownership_registry: tuple[MongoClient, TenantOwnershipEvidenceRegistry, str],
) -> None:
    client, registry, database_name = ownership_registry
    tenant_id = f"tenant-{uuid.uuid4().hex}"
    unverified = SimpleNamespace(request=SimpleNamespace(tenant_id=tenant_id))
    with client.start_session() as session:
        with session.start_transaction():
            with pytest.raises(TenantOwnershipEvidencePersistenceError) as raised:
                registry.append(
                    evidence=unverified,  # type: ignore[arg-type]
                    command_id="caller-forged-command",
                    expected_revision=0,
                    session=session,
                )
            assert str(raised.value) == "VERIFIED_OWNERSHIP_EVIDENCE_REQUIRED"
            session.abort_transaction()
    database = client[database_name]
    assert database["tenant_ownership_evidence_history"].count_documents({}) == 0
    assert database["tenant_ownership_current"].count_documents({}) == 0


def test_real_mongo_rejects_reads_without_active_caller_transaction(
    ownership_registry: tuple[MongoClient, TenantOwnershipEvidenceRegistry, str],
) -> None:
    _client, registry, _database_name = ownership_registry
    with pytest.raises(TenantOwnershipEvidenceTransactionRequiredError) as raised:
        registry.current(tenant_id="tenant-no-transaction", session=None)
    assert str(raised.value) == "ACTIVE_TRANSACTION_REQUIRED"
