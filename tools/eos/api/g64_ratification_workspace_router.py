"""Authenticated, tenant-scoped G64 ratification evidence command transport.

TITLE: G64 Ratification Workspace Router
VERSION: v1.0.0-G64-AUTHENTICATED-WORKSPACE-COMMANDS
AUTHORITY: Evidence capture only; no institutional ratification or access authority.
TENANT BOUNDARY: Tenant scope is server-derived from canonical tenant IAM.
INSTITUTION BOUNDARY: Submitted institution ID remains UNVERIFIED draft evidence.
FAIL-CLOSED: Unknown permissions, unavailable IAM/database, malformed evidence,
             corrupt persistence, and conflicting idempotency keys deny.
"""
from __future__ import annotations

import hashlib
import json
import re
from datetime import datetime, timezone
from typing import Final

from fastapi import APIRouter, Depends, Header, HTTPException, Query, status
from pydantic import BaseModel, ConfigDict, Field
from pymongo.errors import PyMongoError

from tools.eos.api.tenant_authorization_http import (
    RequireTenantAuthorization,
    TenantAuthorizationContext,
)
from tools.eos.kernel.db import get_client, get_database
from tools.eos.legal_operations.domain.g64_ratification_workspace_evidence import (
    G64ClickAttestation,
    G64DecisionEntry,
    G64Disposition,
    G64EvidenceReference,
    G64RatificationWorkspaceRecord,
    G64RecordState,
    G64WorkspaceEvidenceError,
)
from tools.eos.legal_operations.domain.g64_ratification_workspace_export import (
    build_repository_export_bytes,
)
from tools.eos.legal_operations.registry.g64_ratification_workspace_registry import (
    COLLECTION,
    G64RegistryConflictError,
    G64RegistryError,
    G64RegistryInputError,
    G64RegistryUnavailableError,
    append_record,
    ensure_indexes,
    list_history,
    read_record,
)

router = APIRouter(
    prefix="/legal-operations/g64/ratification-workspace",
    tags=["legal-operations", "g64-ratification-workspace"],
)
VERSION: Final[str] = "v1.0.0-G64-AUTHENTICATED-WORKSPACE-COMMANDS"
_WRITE_PERMISSION: Final[str] = "legal_operations:g64_ratification_workspace:write"
_READ_PERMISSION: Final[str] = "legal_operations:g64_ratification_workspace:read"
_WRITE_AUTHORITY = RequireTenantAuthorization(
    _WRITE_PERMISSION, "legal_operations:g64_ratification_workspace:write"
)
_READ_AUTHORITY = RequireTenantAuthorization(
    _READ_PERMISSION, "legal_operations:g64_ratification_workspace:read"
)
_IDEMPOTENCY_KEY: Final[re.Pattern[str]] = re.compile(
    r"[A-Za-z0-9][A-Za-z0-9._:/-]{0,255}\Z"
)


class EvidenceReferenceInput(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)
    locator: str
    sha3_512_fingerprint: str


class DecisionInput(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)
    decision_id: str
    disposition: G64Disposition
    rationale: str
    scope: list[str] = Field(min_length=1)
    accountable_source_owner: str
    evidence: list[EvidenceReferenceInput] = Field(min_length=1)
    effective_from: datetime
    expires_or_review_at: datetime
    revocation_rule: str


class WorkspaceAttestationInput(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)
    institution_id: str
    contract_version: str
    contract_sha3_512_fingerprint: str
    decisions: list[DecisionInput] = Field(min_length=10, max_length=10)
    supporting_evidence: list[EvidenceReferenceInput] = Field(default_factory=list)


def _reference(item: EvidenceReferenceInput) -> G64EvidenceReference:
    return G64EvidenceReference(
        locator=item.locator,
        sha3_512_fingerprint=item.sha3_512_fingerprint,
    )


def _decision(item: DecisionInput) -> G64DecisionEntry:
    return G64DecisionEntry(
        decision_id=item.decision_id,
        disposition=item.disposition,
        rationale=item.rationale,
        scope=tuple(item.scope),
        accountable_source_owner=item.accountable_source_owner,
        evidence=tuple(_reference(value) for value in item.evidence),
        effective_from=item.effective_from,
        expires_or_review_at=item.expires_or_review_at,
        revocation_rule=item.revocation_rule,
    )


def _raise_registry_http(error: G64RegistryError) -> None:
    if isinstance(error, G64RegistryInputError):
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=error.code)
    if isinstance(error, G64RegistryConflictError):
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=error.code)
    if error.code == "G64_REGISTRY_RECORD_NOT_FOUND":
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=error.code)
    raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=error.code)


def _storage() -> tuple[object, object]:
    client = get_client()
    database = get_database()
    if client is None or database is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="G64_WORKSPACE_PERSISTENCE_UNAVAILABLE",
        )
    return client, database


def _response(record_document: dict[str, object], tenant_id: str) -> dict[str, object]:
    export_bytes = build_repository_export_bytes(
        tenant_id=tenant_id,
        record=_hydrate_record_for_export(record_document),
    )
    return {
        "version": VERSION,
        "record": record_document,
        "repository_evidence_export": json.loads(export_bytes),
        "institution_binding_status": "UNVERIFIED_PENDING_INDEPENDENT_VERIFICATION",
        "ratification_complete": False,
        "permits_operational_access": False,
        "constitutes_ratification": False,
    }


def _hydrate_record_for_export(
    document: dict[str, object],
) -> G64RatificationWorkspaceRecord:
    """Strictly hydrate the exact stored record before creating an export."""
    from datetime import datetime

    def moment(value: object) -> datetime:
        if not isinstance(value, str):
            raise G64WorkspaceEvidenceError("PERSISTED_TIMESTAMP_INVALID")
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
        if parsed.microsecond:
            raise G64WorkspaceEvidenceError("PERSISTED_TIMESTAMP_NONCANONICAL")
        return parsed

    decisions_raw = document.get("decisions")
    if not isinstance(decisions_raw, list) or len(decisions_raw) != 10:
        raise G64WorkspaceEvidenceError("PERSISTED_DECISIONS_INVALID")
    decisions: list[G64DecisionEntry] = []
    for item in decisions_raw:
        if not isinstance(item, dict):
            raise G64WorkspaceEvidenceError("PERSISTED_DECISION_INVALID")
        disposition_value = item.get("disposition")
        evidence_raw = item.get("evidence")
        scope_raw = item.get("scope")
        if not isinstance(evidence_raw, list) or not isinstance(scope_raw, list):
            raise G64WorkspaceEvidenceError("PERSISTED_DECISION_FIELDS_INVALID")
        decisions.append(
            G64DecisionEntry(
                decision_id=item.get("decision_id"),
                disposition=G64Disposition(disposition_value),
                rationale=item.get("rationale"),
                scope=tuple(scope_raw),
                accountable_source_owner=item.get("accountable_source_owner"),
                evidence=tuple(
                    G64EvidenceReference(
                        locator=value["locator"],
                        sha3_512_fingerprint=value["sha3_512_fingerprint"],
                    )
                    for value in evidence_raw
                ),
                effective_from=moment(item.get("effective_from")),
                expires_or_review_at=moment(item.get("expires_or_review_at")),
                revocation_rule=item.get("revocation_rule"),
            )
        )
    supporting_raw = document.get("supporting_evidence")
    if not isinstance(supporting_raw, list):
        raise G64WorkspaceEvidenceError("PERSISTED_SUPPORTING_EVIDENCE_INVALID")
    attestation_raw = document.get("attestation")
    attestation = None
    if attestation_raw is not None:
        if not isinstance(attestation_raw, dict):
            raise G64WorkspaceEvidenceError("PERSISTED_ATTESTATION_INVALID")
        attestation = G64ClickAttestation(
            event_id=attestation_raw.get("event_id"),
            authenticated_principal_id=attestation_raw.get("authenticated_principal_id"),
            authenticated_request_reference=attestation_raw.get("authenticated_request_reference"),
            attested_at=moment(attestation_raw.get("attested_at")),
            record_sha3_512_fingerprint=attestation_raw.get("record_sha3_512_fingerprint"),
            attestation_text_version=attestation_raw.get("attestation_text_version"),
        )
    return G64RatificationWorkspaceRecord(
        record_id=document.get("record_id"),
        institution_id=document.get("institution_id"),
        ratifier_principal_id=document.get("ratifier_principal_id"),
        contract_version=document.get("contract_version"),
        contract_sha3_512_fingerprint=document.get("contract_sha3_512_fingerprint"),
        created_at=moment(document.get("created_at")),
        state=G64RecordState(document.get("state")),
        decisions=tuple(decisions),
        supporting_evidence=tuple(
            G64EvidenceReference(
                locator=value["locator"],
                sha3_512_fingerprint=value["sha3_512_fingerprint"],
            )
            for value in supporting_raw
        ),
        attestation=attestation,
    )


@router.post("/records", status_code=status.HTTP_201_CREATED)
def submit_attested_record(
    body: WorkspaceAttestationInput,
    context: TenantAuthorizationContext = Depends(_WRITE_AUTHORITY),
    idempotency_key: str = Header(alias="Idempotency-Key"),
) -> dict[str, object]:
    """Persist one authenticated click-to-attest record; this is not ratification."""
    if _IDEMPOTENCY_KEY.fullmatch(idempotency_key) is None:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="G64_IDEMPOTENCY_KEY_INVALID",
        )
    try:
        decisions = tuple(_decision(item) for item in body.decisions)
        if any(item.disposition is None for item in decisions):
            raise G64WorkspaceEvidenceError("ALL_D01_D10_CHOICES_REQUIRED_FOR_ATTESTATION")
        now = datetime.now(timezone.utc).replace(microsecond=0)
        tenant_id = context.tenant_id
        record_id = "g64-" + hashlib.sha3_512(
            f"{tenant_id}|{body.institution_id}|{idempotency_key}".encode("utf-8")
        ).hexdigest()[:40]
        supporting = tuple(_reference(item) for item in body.supporting_evidence)
        client, database = _storage()
        collection = database[COLLECTION]
        with client.start_session() as session:
            with session.start_transaction():
                try:
                    existing = read_record(
                        tenant_id=tenant_id,
                        institution_id=body.institution_id,
                        record_id=record_id,
                        collection=collection,
                        session=session,
                    )
                except G64RegistryError as error:
                    if error.code != "G64_REGISTRY_RECORD_NOT_FOUND":
                        _raise_registry_http(error)
                else:
                    payload = existing["payload"]
                    requested_decisions = [item.to_document() for item in decisions]
                    if (
                        payload.get("ratifier_principal_id") != context.identity.identity_id
                        or payload.get("contract_version") != body.contract_version
                        or payload.get("contract_sha3_512_fingerprint") != body.contract_sha3_512_fingerprint
                        or payload.get("decisions") != requested_decisions
                        or payload.get("supporting_evidence") != [item.to_document() for item in supporting]
                    ):
                        raise HTTPException(
                            status_code=status.HTTP_409_CONFLICT,
                            detail="G64_IDEMPOTENCY_KEY_PAYLOAD_CONFLICT",
                        )
                    return _response(payload, tenant_id)
                draft = G64RatificationWorkspaceRecord(
                    record_id=record_id,
                    institution_id=body.institution_id,
                    ratifier_principal_id=context.identity.identity_id,
                    contract_version=body.contract_version,
                    contract_sha3_512_fingerprint=body.contract_sha3_512_fingerprint,
                    created_at=now,
                    state=G64RecordState.DRAFT,
                    decisions=decisions,
                    supporting_evidence=supporting,
                )
                attestation = G64ClickAttestation(
                    event_id=f"attestation-{record_id}",
                    authenticated_principal_id=context.identity.identity_id,
                    authenticated_request_reference=hashlib.sha3_512(
                        f"{tenant_id}|{record_id}|{idempotency_key}".encode("utf-8")
                    ).hexdigest(),
                    attested_at=now,
                    record_sha3_512_fingerprint=draft.evidence_fingerprint(),
                    attestation_text_version="g64-attestation-copy-v1",
                )
                record = G64RatificationWorkspaceRecord(
                    record_id=record_id,
                    institution_id=body.institution_id,
                    ratifier_principal_id=context.identity.identity_id,
                    contract_version=body.contract_version,
                    contract_sha3_512_fingerprint=body.contract_sha3_512_fingerprint,
                    created_at=now,
                    state=G64RecordState.ATTESTED_PENDING_VERIFICATION,
                    decisions=decisions,
                    supporting_evidence=supporting,
                    attestation=attestation,
                )
                append_record(
                    tenant_id=tenant_id,
                    record=record,
                    collection=collection,
                    session=session,
                )
        return _response(record.to_document(), tenant_id)
    except G64WorkspaceEvidenceError as error:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(error),
        ) from error
    except G64RegistryError as error:
        _raise_registry_http(error)
    except PyMongoError as error:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="G64_WORKSPACE_PERSISTENCE_UNAVAILABLE",
        ) from error


@router.get("/records")
def read_workspace_history(
    institution_id: str = Query(min_length=1, max_length=256),
    limit: int = Query(default=100, ge=1, le=500),
    context: TenantAuthorizationContext = Depends(_READ_AUTHORITY),
) -> dict[str, object]:
    """Read verified-integrity workspace history within server-derived tenant scope."""
    try:
        client, database = _storage()
        with client.start_session() as session:
            with session.start_transaction():
                rows = list_history(
                    tenant_id=context.tenant_id,
                    institution_id=institution_id,
                    collection=database[COLLECTION],
                    session=session,
                    limit=limit,
                )
        records = [row["payload"] for row in rows]
        return {
            "version": VERSION,
            "records": records,
            "institution_binding_status": "UNVERIFIED_PENDING_INDEPENDENT_VERIFICATION",
            "ratification_complete": False,
            "permits_operational_access": False,
            "constitutes_ratification": False,
        }
    except G64RegistryError as error:
        _raise_registry_http(error)
    except PyMongoError as error:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="G64_WORKSPACE_PERSISTENCE_UNAVAILABLE",
        ) from error


# END OF WILSY OS SOVEREIGN ARTIFACT
