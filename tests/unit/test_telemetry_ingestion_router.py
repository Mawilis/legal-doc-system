"""Regression tests for canonical telemetry ingestion policy and durable-write contract."""
from __future__ import annotations
from pathlib import Path
import pytest
from pymongo.errors import DuplicateKeyError
from tools.eos.api.telemetry_ingestion_router import TelemetryEventRequest, _persist_telemetry_event, router
from tools.eos.auth.permission_namespace import permission_metadata
from tools.eos.auth.roles import ROLE_PERMISSIONS_MAP
from tools.eos.auth.tenant_authority_policy import DENY, ELIGIBLE, tenant_role_operation_eligibility

def test_route_is_registered_once() -> None:
    assert [r.path for r in router.routes if getattr(r, "path", None) == "/telemetry/event"] == ["/telemetry/event"]
    server_source = Path("tools/eos/api/server.py").read_text()
    assert server_source.count("from .telemetry_ingestion_router import router as telemetry_ingestion_router") == 1
    assert server_source.count("app.include_router(telemetry_ingestion_router, prefix=\"/api\")") == 1

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
        {"eventType": "MADE_UP_EVENT", "metadata": {}},
    ):
        with pytest.raises(ValueError):
            TelemetryEventRequest.validate_event(payload)

def test_event_accepts_existing_cover_page_action_payload_contract() -> None:
    event = TelemetryEventRequest.validate_event({"action": "COVER_PAGE_ENTERED", "payload": {"anchorId": "A"}})
    assert event.event_type == "COVER_PAGE_ENTERED"
    assert event.metadata == {"anchorId": "A"}

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
    result = _persist_telemetry_event(tenant_id="tenant-1", principal_id="principal-1", event=event, database=db)
    assert result["accepted"] is True
    assert result["trace_id"]
    assert db.collection.records[0]["trace_id"] == result["trace_id"]
    assert not db.collection.indexes  # Index lifecycle is owned by EOS startup, not each request.

def test_duplicate_trace_is_not_acknowledged() -> None:
    class Collection:
        def insert_one(self, record): raise DuplicateKeyError("duplicate")
    class Database:
        def __getitem__(self, name): return Collection()
    event = TelemetryEventRequest.validate_event({"eventType": "SYSTEM_EVENT"})
    with pytest.raises(DuplicateKeyError):
        _persist_telemetry_event(tenant_id="tenant-1", principal_id="principal-1", event=event, trace_id="duplicate", database=Database())

def test_database_unavailable_fails_before_acceptance(monkeypatch) -> None:
    import tools.eos.api.telemetry_ingestion_router as module
    monkeypatch.setattr(module, "get_database", lambda: None)
    event = TelemetryEventRequest.validate_event({"eventType": "SYSTEM_EVENT"})
    with pytest.raises(RuntimeError, match="TELEMETRY_DATABASE_UNAVAILABLE"):
        _persist_telemetry_event(tenant_id="tenant-1", principal_id="principal-1", event=event, database=None)
