from __future__ import annotations

from types import SimpleNamespace

from fastapi import FastAPI
from fastapi.testclient import TestClient

from tools.eos.api import forensic_merkle_router as module


class _Cursor(list):
    def sort(self, _spec):
        return self

    def limit(self, _value):
        return self


class _Collection:
    def find(self, query, projection):
        self.query = query
        self.projection = projection
        return _Cursor([])


class _Database:
    def __init__(self):
        self.collection = _Collection()

    def __getitem__(self, name):
        assert name == "forensic_ledger"
        return self.collection


def _client(monkeypatch):
    database = _Database()
    context = SimpleNamespace(tenant_id="TENANT-CANONICAL")
    app = FastAPI()
    app.include_router(module.router)
    app.dependency_overrides[module._READ_AUDIT] = lambda: context
    monkeypatch.setattr(module, "get_database", lambda: database)
    return TestClient(app), database


def test_forensic_chain_read_uses_only_authorized_context_tenant(monkeypatch):
    client, database = _client(monkeypatch)
    response = client.get("/forensics/verify-chain?limit=20")
    assert response.status_code == 200
    assert response.json()["tenantId"] == "TENANT-CANONICAL"
    assert response.json()["sourceStatus"] == "SOURCE_SILENT"
    assert response.json()["verified"] is False
    assert database.collection.query == {"tenantId": "TENANT-CANONICAL"}


def test_forensic_status_never_claims_anchor_or_worker_success(monkeypatch):
    client, _database = _client(monkeypatch)
    response = client.get("/forensics/merkle-auditor/status")
    assert response.status_code == 200
    payload = response.json()
    assert payload["anchorMode"] == "NOT_CONFIGURED"
    assert payload["anchorProvider"] == "NONE"
    assert payload["running"] is False
    assert payload["verified"] is False


def test_legacy_rechain_and_seal_commands_fail_closed(monkeypatch):
    client, _database = _client(monkeypatch)
    rechain = client.post("/forensics/merkle-auditor/rechain-receipts")
    seal = client.post("/forensics/merkle-auditor/seal-receipts")
    assert rechain.status_code == 503
    assert rechain.json()["detail"] == "FORENSIC_RECHAIN_COMMAND_NOT_MIGRATED"
    assert seal.status_code == 503
    assert seal.json()["detail"] == "FORENSIC_SEAL_CUSTODY_NOT_CONFIGURED"
