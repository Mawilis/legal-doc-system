"""TITLE: WILSY OS Authenticated Telemetry Ingestion
VERSION: v1.0.0-TELEMETRY-EVENT-IAM-DURABLE-WRITE
AUTHORITY: Canonical tenant authorization plus durable telemetry persistence only.
TENANT POSTURE: Tenant scope comes exclusively from TenantAuthorizationContext.
FAIL-CLOSED POSTURE: No success response before the unique-indexed insert completes.
"""
from __future__ import annotations
import json
import re
from datetime import datetime, timezone
from typing import Any
from uuid import uuid4
from fastapi import APIRouter, Depends, HTTPException, Request, status
from pydantic import BaseModel, ConfigDict, Field, StrictStr, ValidationError
from pymongo.errors import DuplicateKeyError, PyMongoError
from tools.eos.api.tenant_authorization_http import RequireTenantAuthorization, TenantAuthorizationContext
from tools.eos.kernel.db import get_database

router = APIRouter(prefix="/telemetry", tags=["Telemetry Ingestion"])
_authorize_telemetry_write = RequireTenantAuthorization("telemetry:event:write", "telemetry_event_write")
_COLLECTION = "wilsy_sovereign_telemetry"
_MAX_PAYLOAD_BYTES = 16_384
_EVENT_TYPE = re.compile(r"^[A-Z][A-Z0-9_]{0,63}$")
_CLIENT_TRACE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._:-]{0,127}$")

class TelemetryEventRequest(BaseModel):
    """Strict browser-compatible event envelope; caller tenant and authority are forbidden."""
    model_config = ConfigDict(extra="forbid", populate_by_name=True)
    event_type: StrictStr = Field(alias="eventType", min_length=1, max_length=64)
    metadata: dict[str, Any] = Field(default_factory=dict)
    client_trace_id: StrictStr | None = Field(default=None, alias="traceId", max_length=128)
    timestamp: StrictStr | None = Field(default=None, max_length=64)
    nonce: StrictStr | None = Field(default=None, max_length=128)
    forensic_seal: StrictStr | None = Field(default=None, alias="forensicSeal", max_length=256)
    seal_algorithm: StrictStr | None = Field(default=None, alias="sealAlgorithm", max_length=32)
    status_value: StrictStr | None = Field(default=None, alias="status", max_length=32)
    event_id: StrictStr | None = Field(default=None, alias="id", max_length=128)

    @classmethod
    def validate_event(cls, value: object) -> "TelemetryEventRequest":
        event = cls.model_validate(value)
        if not _EVENT_TYPE.fullmatch(event.event_type):
            raise ValueError("eventType must be a canonical uppercase event token")
        if event.client_trace_id is not None and not _CLIENT_TRACE.fullmatch(event.client_trace_id):
            raise ValueError("traceId is malformed")
        encoded = json.dumps(event.metadata, separators=(",", ":"), ensure_ascii=False, allow_nan=False).encode("utf-8")
        if len(encoded) > _MAX_PAYLOAD_BYTES:
            raise ValueError("metadata exceeds the 16384-byte limit")
        return event

def _persist_telemetry_event(*, tenant_id: str, principal_id: str, event: TelemetryEventRequest, trace_id: str | None = None, database: Any = None) -> dict[str, Any]:
    """Persist one bounded event with a server-generated, storage-unique trace."""
    db = database if database is not None else get_database()
    if db is None:
        raise RuntimeError("TELEMETRY_DATABASE_UNAVAILABLE")
    collection = db[_COLLECTION]
    server_trace_id = trace_id or str(uuid4())
    collection.insert_one({
        "trace_id": server_trace_id,
        "tenant_id": tenant_id,
        "principal_id": principal_id,
        "event_type": event.event_type,
        "metadata": event.metadata,
        "client_trace_id": event.client_trace_id,
        "received_at": datetime.now(timezone.utc),
        "schema_version": 1,
    })
    return {"accepted": True, "trace_id": server_trace_id, "event_type": event.event_type}

@router.post("/event", status_code=status.HTTP_201_CREATED)
async def ingest_telemetry_event(request: Request, context: TenantAuthorizationContext = Depends(_authorize_telemetry_write)) -> dict[str, Any]:
    """Bound raw input, authorize, validate, and durably append one tenant-scoped event."""
    if not getattr(request.app.state, "telemetry_indexes_ready", False):
        raise HTTPException(status_code=503, detail="TELEMETRY_PERSISTENCE_UNAVAILABLE")
    raw_body = await request.body()
    if len(raw_body) > _MAX_PAYLOAD_BYTES:
        raise HTTPException(status_code=413, detail="TELEMETRY_BODY_TOO_LARGE")
    try:
        payload = json.loads(raw_body)
        if not isinstance(payload, dict):
            raise ValueError("event envelope must be an object")
        event = TelemetryEventRequest.validate_event(payload)
    except (json.JSONDecodeError, ValidationError, ValueError, TypeError) as exc:
        raise HTTPException(status_code=422, detail="INVALID_TELEMETRY_EVENT") from exc
    try:
        return _persist_telemetry_event(tenant_id=context.tenant_id, principal_id=context.identity.identity_id, event=event)
    except DuplicateKeyError as exc:
        raise HTTPException(status_code=409, detail="TELEMETRY_TRACE_CONFLICT") from exc
    except (PyMongoError, RuntimeError, OSError) as exc:
        raise HTTPException(status_code=503, detail="TELEMETRY_PERSISTENCE_UNAVAILABLE") from exc

__all__ = ["router", "TelemetryEventRequest", "_persist_telemetry_event"]
# END OF WILSY OS SOVEREIGN ARTIFACT
