"""Regression tests for canonical telemetry ingestion policy and durable-write contract."""
from __future__ import annotations
import pytest
from pymongo.errors import DuplicateKeyError
from tools.eos.api.telemetry_ingestion_router import TelemetryEventRequest, _persist_telemetry_event, router
from tools.eos.auth.permission_namespace import permission_metadata
from tools.eos.auth.roles import ROLE_PERMISSIONS_MAP
from tools.eos.auth.tenant_authority_policy import DENY, ELIGIBLE, tenant_role_operation_eligibility

def test_route_is_registered_once() -> None:
    assert [r.path for r in router.routes if getattr(r, "path", None) == "/telemetry/event"] == ["/telemetry/event"]

def test_telemetry_permission_is_canonical_and_narrowly_granted() -> None:
    metadata = permission_metadata("telemetry:event:write")
    assert metadata.tenant_membership_required is True
    assert "telemetry:event:write" in ROLE_PERMISSIONS_MAP["ENTERPRISE_ADMIN"]
    assert "telemetry:event:write" not in ROLE_PERMISSIONS_MAP["AUDITOR"]
    for role in ("tenant_owner", "tenant_admin", "tenant_manager"):
        assert tenant_role_operation_eligibility(role, "telemetry_event_write") == ELIGIBLE
    assert tenant_role_operation_eligibility("tenant_auditor", "telemetry_event_write") == DENY

def test_event_rejects_unknown_fields_forged_tenant_and_malformed_trace() -> None:
    for payload in (
        {"eventType": "SYSTEM_EVENT", "tenantId": "forged"},
        {"eventType": "SYSTEM_EVENT", "traceId": "bad trace"},
        {"eventType": "lowercase", "metadata": {}},
    ):
        with pytest.raises(ValueError):
            TelemetryEventRequest.validate_event(payload)

def test_event_rejects_oversized_metadata() -> None:
    with pytest.raises(ValueError):
        TelemetryEventRequest.validate_event({"eventType": "SYSTEM_EVENT", "metadata": {"body": "x" * 17000}})

def test_success_follows_insert_and_uses_server_trace() -> None:
    class Collection:
        def __init__(self): self.indexes, self.records = [], []
        def create_index(self, key, **kwargs): self.indexes.append((key, kwargs))
        def insert_one(self, record): self.records.append(record)
    class Database:
        def __init__(self): self.collection = Collection()
        def __getitem__(self, name):
            assert name == "wilsy_sovereign_telemetry"
            return self.collection
    db = Database()
    event = TelemetryEventRequest.validate_event({"eventType": "SYSTEM_EVENT", "metadata": {"source": "test"}})
    result = _persist_telemetry_event(tenant_id="tenant-1", principal_id="principal-1", event=event, trace_id="trace-test", database=db)
    assert result["accepted"] is True
    assert db.collection.records[0]["trace_id"] == "trace-test"
    assert db.collection.indexes[0][1]["unique"] is True

def test_duplicate_trace_is_not_acknowledged() -> None:
    class Collection:
        def create_index(self, key, **kwargs): assert kwargs["unique"] is True
        def insert_one(self, record): raise DuplicateKeyError("duplicate")
    class Database:
        def __getitem__(self, name): return Collection()
    event = TelemetryEventRequest.validate_event({"eventType": "SYSTEM_EVENT"})
    with pytest.raises(DuplicateKeyError):
        _persist_telemetry_event(tenant_id="tenant-1", principal_id="principal-1", event=event, trace_id="duplicate", database=Database())

def test_database_unavailable_fails_before_acceptance() -> None:
    event = TelemetryEventRequest.validate_event({"eventType": "SYSTEM_EVENT"})
    with pytest.raises(RuntimeError, match="TELEMETRY_DATABASE_UNAVAILABLE"):
        _persist_telemetry_event(tenant_id="tenant-1", principal_id="principal-1", event=event, database=None)


def _client(monkeypatch, database):
    import tools.eos.api.telemetry_ingestion_router as module
    app = FastAPI()
    app.include_router(router)
    app.state.telemetry_indexes_ready = True
    app.dependency_overrides[module._authorize_telemetry_write] = lambda: SimpleNamespace(
        tenant_id="tenant-authorized", identity=SimpleNamespace(identity_id="principal-authenticated")
    )
    monkeypatch.setattr(module, "get_database", lambda: database)
    return TestClient(app)


def test_http_success_persists_under_authorized_tenant_with_server_trace(monkeypatch):
    class Collection:
        def __init__(self):
            self.records = []
        def insert_one(self, record):
            self.records.append(record)
    class Database:
        def __init__(self):
            self.collection = Collection()
        def __getitem__(self, name):
            assert name == "wilsy_sovereign_telemetry"
            return self.collection
    db = Database()
    client = _client(monkeypatch, db)
    response = client.post("/telemetry/event", json={
        "eventType": "SYSTEM_EVENT", "traceId": "TRC-client-123", "metadata": {"ok": True}
    })
    assert response.status_code == 201
    assert response.json()["trace_id"] != "TRC-client-123"
    assert db.collection.records[0]["tenant_id"] == "tenant-authorized"
    assert db.collection.records[0]["client_trace_id"] == "TRC-client-123"


def test_http_rejects_forged_tenant_and_oversized_raw_body(monkeypatch):
    client = _client(monkeypatch, object())
    forged = client.post("/telemetry/event", json={"eventType": "SYSTEM_EVENT", "tenantId": "attacker"})
    oversized = client.post("/telemetry/event", json={"eventType": "SYSTEM_EVENT", "metadata": {"blob": "x" * 17000}})
    assert forged.status_code == 422
    assert oversized.status_code == 413


def test_http_reports_database_unavailable_and_duplicate_trace(monkeypatch):
    client = _client(monkeypatch, None)
    unavailable = client.post("/telemetry/event", json={"eventType": "SYSTEM_EVENT"})
    assert unavailable.status_code == 503

    class Collection:
        def insert_one(self, record):
            raise DuplicateKeyError("duplicate")
    class Database:
        def __getitem__(self, name):
            return Collection()
    client = _client(monkeypatch, Database())
    conflict = client.post("/telemetry/event", json={"eventType": "SYSTEM_EVENT"})
    assert conflict.status_code == 409
