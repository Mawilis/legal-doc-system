"""TITLE: WILSY OS Governed Business Activity Context
VERSION: v1.0.0-M03-HR03-GOVERNED-BUSINESS-CONTEXT
AUTHORITY: WILSY OS Core Governance
EPITOME: Independently approved, exact-tenant business-activity profiles for department suggestions, separate from external legal-entity evidence.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tools/eos/api/hr_organization_business_context_router.py
COLLABORATION / OWNERSHIP: WILSY OS HR Organization / Python EOS engineering
CERTIFICATION / UPDATE DATE: 2026-11-28
CHANGELOG: v1.0.0-M03-HR03-GOVERNED-BUSINESS-CONTEXT adds governed source, consumer and evidence contracts without expanding IAM grants.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2 technical controls.
SECURITY / PRIVACY POSTURE: Bounded readback and event labels; no personnel/financial secrets, no fabricated external entity verification.
TENANT BOUNDARY: Exact authenticated EOS tenant; no root or Owner fallback.
AUTHORITY BOUNDARY: EOS source grants are separately required; maker and checker cannot be the same principal.
FINANCIAL AUTHORITY BOUNDARY: No financial execution; Kennel EOS exclusively.
"""

from __future__ import annotations

from typing import Any, Literal
from datetime import datetime, timezone
from uuid import uuid4

from fastapi import APIRouter, Depends, Header, HTTPException
from pydantic import BaseModel, ConfigDict, Field
from pymongo import ReturnDocument
from pymongo.errors import DuplicateKeyError
from pymongo.read_concern import ReadConcern
from pymongo.read_preferences import ReadPreference
from pymongo.write_concern import WriteConcern

from . import hr_workforce_directory_router as org
from .tenant_authorization_http import TenantAuthorizationContext
from tools.eos.kernel.db import get_client, get_database

router = APIRouter(prefix="/api/hr/workforce/structure/context", tags=["hr-business-context"])
_PROPOSALS = "hr_business_activity_proposals"
_CURRENT = "hr_business_activity_current"
_EVENTS = "hr_business_activity_events"
_ALLOWED = frozenset({
    "general", "legal", "medical", "dental", "veterinary",
    "import_export", "auto_parts", "mechanical", "dealership", "agriculture",
    "manufacturing", "construction", "retail", "hospitality", "education",
    "technology", "professional", "financial", "logistics", "property",
    "energy", "nonprofit", "public",
})


class ActivityContextDraft(BaseModel):
    """Strictly bounded tenant-declared business activity proposal; not external classification evidence."""
    model_config = ConfigDict(extra="forbid")
    activity_ids: list[str] = Field(min_length=1, max_length=8)
    reason: str = Field(min_length=5, max_length=1000)


class ContextRevision(BaseModel):
    """Required revision precondition for maker submission."""
    model_config = ConfigDict(extra="forbid")
    expected_revision: int = Field(ge=1, strict=True)


class ContextDecision(ContextRevision):
    """Reasoned decision requiring independent EOS organization checker authority."""
    decision: Literal["APPROVE", "REJECT"]
    reason: str = Field(min_length=5, max_length=2000)


def _col(db: Any, name: str):
    """Return majority-consistent collection; caller must enforce exact tenant scope."""
    return db.get_collection(
        name, read_concern=ReadConcern("majority"),
        write_concern=WriteConcern(w="majority", j=True),
    )


def _now():
    """Return ISO UTC audit time; no entity or business authority inferred."""
    return datetime.now(timezone.utc).isoformat()


def _pub(row: dict, *, actor: str | None = None):
    """Project proposal without exposing other principal identities."""
    data = {key: row.get(key) for key in (
        "proposal_id", "status", "activity_ids", "reason",
        "decision_reason", "revision", "base_revision",
    )}
    if actor is not None:
        data["current_principal_is_maker"] = actor in (
            row.get("created_by"), row.get("submitted_by"),
        )
    return data


def _transact(callback):
    """Own majority transaction with proposal, current profile and command evidence."""
    client, db = get_client(), get_database()
    if client is None or db is None:
        raise HTTPException(503, "BUSINESS_CONTEXT_DATABASE_UNAVAILABLE")
    try:
        proposal, current, event = (_col(db, collection) for collection in (
            _PROPOSALS, _CURRENT, _EVENTS,
        ))
        proposal.create_index([("tenant_id", 1), ("proposal_id", 1)], unique=True)
        current.create_index([("tenant_id", 1)], unique=True)
        event.create_index([("tenant_id", 1), ("actor_id", 1), ("key", 1)], unique=True)
        with client.start_session() as session:
            return session.with_transaction(
                lambda tx: callback(proposal, current, event, tx),
                read_concern=ReadConcern("snapshot"),
                write_concern=WriteConcern(w="majority", j=True),
                read_preference=ReadPreference.PRIMARY,
            )
    except HTTPException:
        raise
    except DuplicateKeyError as error:
        raise HTTPException(409, "BUSINESS_CONTEXT_CONCURRENT_CONFLICT") from error
    except Exception as error:
        raise HTTPException(503, "BUSINESS_CONTEXT_TRANSACTION_UNAVAILABLE") from error


def _command(callback, tenant, actor, key, command, payload):
    """Replay actor-scoped identical commands and reject mismatched idempotency fingerprints."""
    fingerprint = org._org_fingerprint(
        tenant=tenant, actor=actor, key=key, command=command, payload=payload,
    )
    def execute(proposals, current, events, tx):
        identity = {"tenant_id": tenant, "actor_id": actor, "key": key}
        past = events.find_one(identity, session=tx)
        if past is not None:
            if past.get("fingerprint") != fingerprint:
                raise HTTPException(409, "BUSINESS_CONTEXT_IDEMPOTENCY_CONFLICT")
            return past["response"]
        result = callback(proposals, current, tx)
        events.insert_one({
            **identity, "fingerprint": fingerprint, "response": result,
            "command": command, "timestamp": _now(),
        }, session=tx)
        return result
    return _transact(execute)


@router.get("")
def read_business_activity_context(
    auth: TenantAuthorizationContext = Depends(org._ORG_READ),
):
    """Read only approved own-tenant activity profile and pending proposal projections; no external entity claims."""
    db = get_database()
    if db is None:
        raise HTTPException(503, "BUSINESS_CONTEXT_DATABASE_UNAVAILABLE")
    try:
        current = _col(db, _CURRENT).find_one({"tenant_id": auth.tenant_id},
                                             {"_id": 0, "activity_ids": 1, "revision": 1})
        rows = list(_col(db, _PROPOSALS).find(
            {"tenant_id": auth.tenant_id},
            {"_id": 0, "proposal_id": 1, "status": 1, "activity_ids": 1,
             "reason": 1, "decision_reason": 1, "revision": 1, "base_revision": 1,
             "created_by": 1, "submitted_by": 1},
        ).sort("revision", -1).limit(101))
    except Exception as error:
        raise HTTPException(503, "BUSINESS_CONTEXT_SOURCE_UNAVAILABLE") from error
    if len(rows) > 100:
        raise HTTPException(503, "BUSINESS_CONTEXT_RESULT_BOUND_EXCEEDED")
    return {
        "schema": "WILSY-HR-BUSINESS-ACTIVITY-CONTEXT/V1",
        "source": "EOS_APPROVED_TENANT_BUSINESS_ACTIVITIES",
        "tenant_id": auth.tenant_id,
        "status": "APPROVED" if current else "UNCONFIGURED",
        "activity_ids": current["activity_ids"] if current else [],
        "revision": current["revision"] if current else 0,
        "proposals": [_pub(row, actor=auth.identity.identity_id) for row in rows],
        "operating_entities": [],
        "entity_status": "ENTITY_SOURCE_NOT_CONNECTED",
        "external_business_classification_verified": False,
    }


@router.post("/proposals", status_code=201)
def draft_business_activity_context(
    body: ActivityContextDraft,
    key: str = Header(min_length=12, max_length=128, alias="Idempotency-Key"),
    auth: TenantAuthorizationContext = Depends(org._ORG_CREATE),
):
    """Create an unapproved activity draft under separate organization-create permission."""
    activities = body.activity_ids
    if (len(set(activities)) != len(activities)
            or any(item not in _ALLOWED for item in activities)):
        raise HTTPException(422, "BUSINESS_CONTEXT_ACTIVITY_INVALID")
    tenant, actor = auth.tenant_id, auth.identity.identity_id
    def apply(proposals, current, tx):
        existing = current.find_one({"tenant_id": tenant}, session=tx)
        row = {
            "tenant_id": tenant, "proposal_id": uuid4().hex,
            "activity_ids": activities, "reason": body.reason,
            "base_revision": existing["revision"] if existing else 0,
            "revision": 1, "status": "DRAFT", "created_by": actor,
            "submitted_by": None, "created_at": _now(),
        }
        proposals.insert_one(row, session=tx)
        return {"schema": "WILSY-HR-BUSINESS-ACTIVITY-COMMAND/V1",
                "tenant_id": tenant, "proposal": _pub(row)}
    return _command(apply, tenant, actor, key, "CONTEXT_CREATE",
                    {"activities": activities, "reason": body.reason})


@router.post("/proposals/{proposal_id}/submit")
def submit_business_activity_context(
    proposal_id: str, body: ContextRevision,
    key: str = Header(min_length=12, max_length=128, alias="Idempotency-Key"),
    auth: TenantAuthorizationContext = Depends(org._ORG_CREATE),
):
    """Allow maker-only proposal submission with revision compare-and-set."""
    tenant, actor = auth.tenant_id, auth.identity.identity_id
    def apply(proposals, current, tx):
        row = proposals.find_one({"tenant_id": tenant, "proposal_id": proposal_id}, session=tx)
        if row is None:
            raise HTTPException(404, "BUSINESS_CONTEXT_PROPOSAL_NOT_FOUND")
        if row["created_by"] != actor:
            raise HTTPException(403, "BUSINESS_CONTEXT_MAKER_REQUIRED")
        if row["status"] != "DRAFT" or row["revision"] != body.expected_revision:
            raise HTTPException(409, "BUSINESS_CONTEXT_REVISION_CONFLICT")
        updated = proposals.find_one_and_update({
            "tenant_id": tenant, "proposal_id": proposal_id, "status": "DRAFT",
            "revision": body.expected_revision,
        }, {"$set": {"status": "SUBMITTED", "submitted_by": actor, "submitted_at": _now()},
            "$inc": {"revision": 1}}, return_document=ReturnDocument.AFTER, session=tx)
        if updated is None:
            raise HTTPException(409, "BUSINESS_CONTEXT_REVISION_CONFLICT")
        return {"schema": "WILSY-HR-BUSINESS-ACTIVITY-COMMAND/V1",
                "tenant_id": tenant, "proposal": _pub(updated)}
    return _command(apply, tenant, actor, key, "CONTEXT_SUBMIT",
                    {"id": proposal_id, "revision": body.expected_revision})


@router.post("/proposals/{proposal_id}/decision")
def decide_business_activity_context(
    proposal_id: str, body: ContextDecision,
    key: str = Header(min_length=12, max_length=128, alias="Idempotency-Key"),
    auth: TenantAuthorizationContext = Depends(org._ORG_DECIDE),
):
    """Require independent checker; publish approved own-tenant profile atomically."""
    tenant, actor = auth.tenant_id, auth.identity.identity_id
    def apply(proposals, current, tx):
        row = proposals.find_one({"tenant_id": tenant, "proposal_id": proposal_id}, session=tx)
        if row is None:
            raise HTTPException(404, "BUSINESS_CONTEXT_PROPOSAL_NOT_FOUND")
        if actor in (row["created_by"], row.get("submitted_by")):
            raise HTTPException(403, "BUSINESS_CONTEXT_MAKER_CANNOT_APPROVE")
        if row["status"] != "SUBMITTED" or row["revision"] != body.expected_revision:
            raise HTTPException(409, "BUSINESS_CONTEXT_REVISION_CONFLICT")
        latest = current.find_one({"tenant_id": tenant}, session=tx)
        if (latest["revision"] if latest else 0) != row["base_revision"]:
            raise HTTPException(409, "BUSINESS_CONTEXT_SOURCE_CHANGED")
        if body.decision == "APPROVE":
            if latest is None:
                current.insert_one({
                    "tenant_id": tenant, "activity_ids": row["activity_ids"],
                    "revision": 1, "approved_at": _now(),
                }, session=tx)
            else:
                result = current.update_one({
                    "tenant_id": tenant, "revision": row["base_revision"],
                }, {"$set": {"activity_ids": row["activity_ids"], "approved_at": _now()},
                    "$inc": {"revision": 1}}, session=tx)
                if result.matched_count != 1:
                    raise HTTPException(409, "BUSINESS_CONTEXT_SOURCE_CHANGED")
        updated = proposals.find_one_and_update({
            "tenant_id": tenant, "proposal_id": proposal_id,
            "revision": body.expected_revision, "status": "SUBMITTED",
        }, {"$set": {"status": "APPROVED" if body.decision == "APPROVE" else "REJECTED",
                     "decided_by": actor, "decision_reason": body.reason,
                     "decided_at": _now()}, "$inc": {"revision": 1}},
            return_document=ReturnDocument.AFTER, session=tx)
        if updated is None:
            raise HTTPException(409, "BUSINESS_CONTEXT_REVISION_CONFLICT")
        return {"schema": "WILSY-HR-BUSINESS-ACTIVITY-COMMAND/V1",
                "tenant_id": tenant, "proposal": _pub(updated)}
    return _command(apply, tenant, actor, key, "CONTEXT_DECIDE",
                    {"id": proposal_id, **body.model_dump()})

# ARTIFACT: tools/eos/api/hr_organization_business_context_router.py
# VERSION: v1.0.0-M03-HR03-GOVERNED-BUSINESS-CONTEXT
# AUTHORITY BOUNDARY: Exact-tenant EOS authority and regression evidence; no grants or financial execution.
# TENANT POSTURE: Exact authorized tenant only; no cross-tenant records, Owner or root fallback.
# FAIL-CLOSED POSTURE: Missing or contradictory evidence is denied/unavailable, never approved.
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively.
# END OF WILSY OS SOVEREIGN ARTIFACT
