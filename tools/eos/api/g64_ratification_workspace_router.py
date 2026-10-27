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
from pathlib import Path
from typing import Final

from fastapi import APIRouter, Depends, Header, HTTPException, Query, Response, status
from pydantic import BaseModel, ConfigDict, Field
from pymongo.errors import PyMongoError

from tools.eos.api.tenant_authorization_http import (
    RequireTenantAuthorization,
    TenantAuthorizationContext,
)
from tools.eos.kernel.db import get_client, get_database
from tools.eos.legal_operations.domain.g64_ratification_workspace_verification import (
    G64IndependentVerification,
    G64SecondApprovalPolicyDecision,
    G64VerificationCheck,
    G64VerificationFinding,
    G64VerificationOutcome,
)
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
from tools.eos.legal_operations.service.g64_repository_evidence_publisher import (
    G64RepositoryPublishError,
    publish_repository_evidence,
)
from tools.eos.legal_operations.registry.g64_ratification_review_registry import (
    COLLECTION as REVIEW_COLLECTION, G64ReviewRegistryError,
    append_review_event, list_review_events,
)
from tools.eos.legal_operations.registry.g64_ratification_workspace_registry import (
    COLLECTION,
    G64RegistryConflictError,
    G64RegistryError,
    G64RegistryInputError,
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
_VERIFY_AUTHORITY = RequireTenantAuthorization(
    "legal_operations:g64_ratification_workspace:verify", "legal_operations:g64_ratification_workspace:verify"
)
_SECOND_APPROVAL_AUTHORITY = RequireTenantAuthorization(
    "legal_operations:g64_ratification_workspace:second_approve", "legal_operations:g64_ratification_workspace:second_approve"
)
_POLICY_AUTHORITY = RequireTenantAuthorization(
    "legal_operations:g64_ratification_workspace:policy", "legal_operations:g64_ratification_workspace:policy"
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
    decisions: list[DecisionInput] = Field(min_length=10, max_length=10)
    supporting_evidence: list[EvidenceReferenceInput] = Field(default_factory=list)

class VerificationFindingInput(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)
    check: G64VerificationCheck
    passed: bool
    rationale: str = Field(min_length=20, max_length=2000)
    evidence: list[EvidenceReferenceInput] = Field(min_length=1, max_length=20)


class IndependentVerificationInput(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)
    institution_id: str
    record_id: str
    record_sha3_512_fingerprint: str
    outcome: G64VerificationOutcome
    rationale: str = Field(min_length=20, max_length=4000)
    findings: list[VerificationFindingInput] = Field(min_length=8, max_length=8)


class SecondApprovalPolicyInput(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)
    institution_id: str
    record_id: str
    record_sha3_512_fingerprint: str
    verification_event_id: str
    second_approval_required: bool
    rationale: str = Field(min_length=20, max_length=4000)
    policy_source: EvidenceReferenceInput
    independent_verification_evidence: EvidenceReferenceInput


class SecondApprovalInput(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)
    institution_id: str
    record_id: str
    record_sha3_512_fingerprint: str
    verification_event_id: str
    policy_decision_event_id: str
    outcome: str
    rationale: str = Field(min_length=20, max_length=4000)
    evidence: list[EvidenceReferenceInput] = Field(min_length=1, max_length=20)



def _canonical_contract() -> tuple[str, str, str]:
    """Read and fingerprint the canonical repository contract, never caller input."""
    path = Path(__file__).resolve().parents[3] / (
        "docs/architecture/wilsy-practitioner-confidentiality-institutional-authority-contract.md"
    )
    try:
        raw = path.read_bytes()
        source = raw.decode("utf-8")
    except (OSError, UnicodeDecodeError) as error:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="G64_CANONICAL_CONTRACT_UNAVAILABLE",
        ) from error
    match = re.search(r"^VERSION:\s*(\S+)\s*$", source, re.MULTILINE)
    if match is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="G64_CANONICAL_CONTRACT_VERSION_UNAVAILABLE",
        )
    return match.group(1), hashlib.sha3_512(raw).hexdigest(), source


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
    try:
        export_bytes = build_repository_export_bytes(
            tenant_id=tenant_id,
            record=_hydrate_record_for_export(record_document),
        )
    except (KeyError, TypeError, ValueError) as error:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="G64_PERSISTED_RECORD_INVALID",
        ) from error
    return {
        "version": VERSION,
        "record": record_document,
        "repository_evidence_export": json.loads(export_bytes),
        "institution_binding_status": "UNVERIFIED_PENDING_INDEPENDENT_VERIFICATION",
        "ratifier_authority_status": "UNVERIFIED_PENDING_INDEPENDENT_VERIFICATION",
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


@router.get("/contract")
def read_canonical_contract(
    context: TenantAuthorizationContext = Depends(_READ_AUTHORITY),
) -> dict[str, object]:
    """Return the repository-owned contract version, fingerprint and text."""
    del context
    version, fingerprint, source = _canonical_contract()
    return {
        "version": VERSION,
        "contract_version": version,
        "contract_sha3_512_fingerprint": fingerprint,
        "contract_status": "PROPOSED_NOT_INSTITUTIONALLY_APPROVED",
        "contract_text": source,
        "ratification_complete": False,
        "permits_operational_access": False,
    }


@router.post("/records", status_code=status.HTTP_201_CREATED)
def submit_attested_record(
    body: WorkspaceAttestationInput,
    response: Response,
    context: TenantAuthorizationContext = Depends(_WRITE_AUTHORITY),
    idempotency_key: str = Header(alias="Idempotency-Key"),
) -> dict[str, object]:
    """Persist an authenticated click-to-attest record and publish its evidence export."""
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
        contract_version, contract_fingerprint, _contract_text = _canonical_contract()
        supporting = tuple(_reference(item) for item in body.supporting_evidence)
        client, database = _storage()
        collection = database[COLLECTION]
        record_document: dict[str, object]
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
                    draft = G64RatificationWorkspaceRecord(
                        record_id=record_id,
                        institution_id=body.institution_id,
                        ratifier_principal_id=context.identity.identity_id,
                        contract_version=contract_version,
                        contract_sha3_512_fingerprint=contract_fingerprint,
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
                        contract_version=contract_version,
                        contract_sha3_512_fingerprint=contract_fingerprint,
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
                    record_document = record.to_document()
                else:
                    payload = existing["payload"]
                    requested_decisions = [item.to_document() for item in decisions]
                    if (
                        payload.get("ratifier_principal_id") != context.identity.identity_id
                        or payload.get("contract_version") != contract_version
                        or payload.get("contract_sha3_512_fingerprint") != contract_fingerprint
                        or payload.get("decisions") != requested_decisions
                        or payload.get("supporting_evidence") != [item.to_document() for item in supporting]
                    ):
                        raise HTTPException(
                            status_code=status.HTTP_409_CONFLICT,
                            detail="G64_IDEMPOTENCY_KEY_PAYLOAD_CONFLICT",
                        )
                    record_document = payload

        result = _response(record_document, tenant_id)
        manifest = result["repository_evidence_export"]
        manifest_bytes = json.dumps(
            manifest, sort_keys=True, separators=(",", ":"),
            ensure_ascii=True, allow_nan=False,
        ).encode("ascii")
        try:
            published = publish_repository_evidence(
                record_id=record_id,
                manifest_bytes=manifest_bytes,
            )
        except G64RepositoryPublishError as error:
            result["application_persistence_status"] = "PERSISTED"
            result["repository_persistence_status"] = (
                "PENDING_CONFIGURATION"
                if error.code == "G64_REPOSITORY_PUBLISHER_NOT_CONFIGURED"
                else "PENDING_RETRY"
            )
            result["repository_persistence_error_code"] = error.code
            response.status_code = status.HTTP_202_ACCEPTED
        else:
            result["application_persistence_status"] = "PERSISTED"
            result["repository_persistence_status"] = published["status"]
            result["repository_commit"] = published
        return result
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
        records = [_response(row["payload"], context.tenant_id) for row in rows]
        return {
            "version": VERSION,
            "records": records,
            "institution_binding_status": "UNVERIFIED_PENDING_INDEPENDENT_VERIFICATION",
            "ratification_complete": False,
            "permits_operational_access": False,
            "constitutes_ratification": False,
            "ratifier_authority_status": "UNVERIFIED_PENDING_INDEPENDENT_VERIFICATION",
        }
    except G64RegistryError as error:
        _raise_registry_http(error)
    except PyMongoError as error:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="G64_WORKSPACE_PERSISTENCE_UNAVAILABLE",
        ) from error


# END OF WILSY OS SOVEREIGN ARTIFACT

def _review_target(*, tenant_id: str, institution_id: str, record_id: str, session: object, collection: object) -> dict[str, object]:
    stored = read_record(tenant_id=tenant_id, institution_id=institution_id, record_id=record_id, collection=collection, session=session)
    payload = stored.get("payload")
    if not isinstance(payload, dict):
        raise HTTPException(status_code=503, detail="G64_PERSISTED_RECORD_INVALID")
    try:
        record = _hydrate_record_for_export(payload)
    except (KeyError, TypeError, ValueError) as error:
        raise HTTPException(status_code=503, detail="G64_PERSISTED_RECORD_INVALID") from error
    if record.evidence_fingerprint() != payload.get("evidence_sha3_512"):
        raise HTTPException(status_code=503, detail="G64_PERSISTED_RECORD_INTEGRITY_FAILURE")
    return payload


def _review_event_id(kind: str, tenant_id: str, record_id: str, key: str) -> str:
    digest = hashlib.sha3_512(f"{kind}|{tenant_id}|{record_id}|{key}".encode()).hexdigest()
    return f"{kind.lower()}-{digest[:40]}"


def _review_event(*, kind: str, event_id: str, tenant_id: str, institution_id: str, record_id: str, fingerprint: str, actor_field: str, actor: str, outcome: str, rationale: str, evidence: list[EvidenceReferenceInput], now: datetime, extra: dict[str, object] | None = None) -> dict[str, object]:
    return {
        "event_id": event_id, "event_type": kind, "tenant_id": tenant_id,
        "institution_id": institution_id, "record_id": record_id,
        "record_sha3_512_fingerprint": fingerprint, actor_field: actor,
        "outcome": outcome, "rationale": rationale,
        "evidence": [_reference(item).to_document() for item in evidence],
        "created_at": now.isoformat(), "authority_effect": "NONE",
        "ratification_complete": False, "permits_operational_access": False,
        **(extra or {}),
    }


@router.post("/records/{record_id}/independent-verification", status_code=status.HTTP_201_CREATED)
def record_independent_verification(record_id: str, body: IndependentVerificationInput, idempotency_key: str = Header(alias="Idempotency-Key"), context: TenantAuthorizationContext = Depends(_VERIFY_AUTHORITY)) -> dict[str, object]:
    if body.record_id != record_id or _IDEMPOTENCY_KEY.fullmatch(idempotency_key) is None:
        raise HTTPException(status_code=422, detail="G64_REVIEW_REQUEST_IDENTITY_INVALID")
    client, database = _storage()
    event_id = _review_event_id("VERIFICATION", context.tenant_id, record_id, idempotency_key)
    now = datetime.now(timezone.utc).replace(microsecond=0)
    try:
        with client.start_session() as session:
            with session.start_transaction():
                target = _review_target(tenant_id=context.tenant_id, institution_id=body.institution_id, record_id=record_id, session=session, collection=database[COLLECTION])
                if target.get("ratifier_principal_id") == context.identity.identity_id:
                    raise HTTPException(status_code=403, detail="G64_VERIFIER_MUST_BE_INDEPENDENT")
                if target.get("evidence_sha3_512") != body.record_sha3_512_fingerprint:
                    raise HTTPException(status_code=409, detail="G64_REVIEW_RECORD_FINGERPRINT_MISMATCH")
                findings = tuple(
                    G64VerificationFinding(
                        check=item.check,
                        passed=item.passed,
                        rationale=item.rationale,
                        evidence=tuple(_reference(ref) for ref in item.evidence),
                    )
                    for item in body.findings
                )
                verification = G64IndependentVerification(
                    verification_id=event_id,
                    tenant_id=context.tenant_id,
                    institution_id=body.institution_id,
                    record_id=record_id,
                    record_sha3_512_fingerprint=body.record_sha3_512_fingerprint,
                    ratifier_principal_id=str(target.get("ratifier_principal_id")),
                    verifier_principal_id=context.identity.identity_id,
                    verified_at=now,
                    outcome=body.outcome,
                    findings=findings,
                )
                event = {
                    **verification.to_document(),
                    "event_id": event_id,
                    "event_type": "INDEPENDENT_VERIFICATION",
                    "rationale": body.rationale,
                    "created_at": now.isoformat(),
                    "authority_effect": "NONE",
                    "ratification_complete": False,
                }
                saved = append_review_event(tenant_id=context.tenant_id, institution_id=body.institution_id, record_id=record_id, event_id=event_id, payload=event, collection=database[REVIEW_COLLECTION], session=session)
    except G64RegistryError as error:
        _raise_registry_http(error)
    except G64ReviewRegistryError as error:
        raise HTTPException(status_code=503, detail=error.code) from error
    except G64WorkspaceEvidenceError as error:
        raise HTTPException(status_code=422, detail=str(error)) from error
    return {"review_event": saved["payload"], "second_approval_required": True, "authority_effect": "NONE", "ratification_complete": False, "permits_operational_access": False}


@router.post("/records/{record_id}/second-approval-policy", status_code=status.HTTP_201_CREATED)
def record_second_approval_policy(record_id: str, body: SecondApprovalPolicyInput, idempotency_key: str = Header(alias="Idempotency-Key"), context: TenantAuthorizationContext = Depends(_POLICY_AUTHORITY)) -> dict[str, object]:
    """Persist an evidence-backed second-approval policy determination, never infer policy."""
    if body.record_id != record_id or _IDEMPOTENCY_KEY.fullmatch(idempotency_key) is None:
        raise HTTPException(status_code=422, detail="G64_REVIEW_REQUEST_IDENTITY_INVALID")
    client, database = _storage()
    event_id = _review_event_id("SECOND-APPROVAL-POLICY", context.tenant_id, record_id, idempotency_key)
    now = datetime.now(timezone.utc).replace(microsecond=0)
    try:
        with client.start_session() as session:
            with session.start_transaction():
                target = _review_target(tenant_id=context.tenant_id, institution_id=body.institution_id, record_id=record_id, session=session, collection=database[COLLECTION])
                if target.get("ratifier_principal_id") == context.identity.identity_id:
                    raise HTTPException(status_code=403, detail="G64_POLICY_DECIDER_MUST_BE_INDEPENDENT")
                if target.get("evidence_sha3_512") != body.record_sha3_512_fingerprint:
                    raise HTTPException(status_code=409, detail="G64_REVIEW_RECORD_FINGERPRINT_MISMATCH")
                events = list_review_events(tenant_id=context.tenant_id, institution_id=body.institution_id, record_id=record_id, collection=database[REVIEW_COLLECTION], session=session, limit=100)
                existing_policy = next((row for row in events if row.get("payload", {}).get("event_type") == "SECOND_APPROVAL_POLICY"), None)
                if existing_policy is not None and existing_policy.get("event_id") != event_id:
                    raise HTTPException(status_code=409, detail="G64_SECOND_APPROVAL_POLICY_ALREADY_RECORDED")
                verifier = next((row.get("payload", {}) for row in events if row.get("event_id") == body.verification_event_id), None)
                if not isinstance(verifier, dict) or verifier.get("event_type") != "INDEPENDENT_VERIFICATION" or verifier.get("outcome") != "PASS":
                    raise HTTPException(status_code=409, detail="G64_INDEPENDENT_VERIFICATION_PASS_REQUIRED")
                verifier_id = verifier.get("verifier_principal_id")
                if verifier_id in {target.get("ratifier_principal_id"), context.identity.identity_id}:
                    raise HTTPException(status_code=403, detail="G64_POLICY_VERIFIER_MUST_BE_INDEPENDENT")
                source = _reference(body.policy_source)
                verification_evidence = _reference(body.independent_verification_evidence)
                if source == verification_evidence:
                    raise HTTPException(status_code=422, detail="G64_POLICY_EVIDENCE_MUST_BE_DISTINCT")
                decision = G64SecondApprovalPolicyDecision(
                    policy_decision_id=event_id,
                    tenant_id=context.tenant_id,
                    institution_id=body.institution_id,
                    record_id=record_id,
                    record_sha3_512_fingerprint=body.record_sha3_512_fingerprint,
                    determined_by_principal_id=context.identity.identity_id,
                    independently_verified_by_principal_id=verifier_id,
                    determined_at=now,
                    second_approval_required=body.second_approval_required,
                    policy_source=source,
                    independent_verification_evidence=verification_evidence,
                )
                event = {
                    **decision.to_document(),
                    "event_id": event_id,
                    "event_type": "SECOND_APPROVAL_POLICY",
                    "rationale": body.rationale,
                    "verification_event_id": body.verification_event_id,
                    "created_at": now.isoformat(),
                    "authority_effect": "NONE",
                    "ratification_complete": False,
                }
                saved = append_review_event(tenant_id=context.tenant_id, institution_id=body.institution_id, record_id=record_id, event_id=event_id, payload=event, collection=database[REVIEW_COLLECTION], session=session)
    except G64RegistryError as error:
        _raise_registry_http(error)
    except G64ReviewRegistryError as error:
        raise HTTPException(status_code=503, detail=error.code) from error
    except G64WorkspaceEvidenceError as error:
        raise HTTPException(status_code=422, detail=str(error)) from error
    return {"review_event": saved["payload"], "second_approval_required": body.second_approval_required, "ratification_complete": False, "permits_operational_access": False}


@router.post("/records/{record_id}/second-approval", status_code=status.HTTP_201_CREATED)
def record_second_approval(record_id: str, body: SecondApprovalInput, idempotency_key: str = Header(alias="Idempotency-Key"), context: TenantAuthorizationContext = Depends(_SECOND_APPROVAL_AUTHORITY)) -> dict[str, object]:
    if body.record_id != record_id or _IDEMPOTENCY_KEY.fullmatch(idempotency_key) is None:
        raise HTTPException(status_code=422, detail="G64_REVIEW_REQUEST_IDENTITY_INVALID")
    if body.outcome not in {"APPROVE", "REJECT"}:
        raise HTTPException(status_code=422, detail="G64_SECOND_APPROVAL_OUTCOME_INVALID")
    client, database = _storage()
    event_id = _review_event_id("SECOND-APPROVAL", context.tenant_id, record_id, idempotency_key)
    now = datetime.now(timezone.utc).replace(microsecond=0)
    try:
        with client.start_session() as session:
            with session.start_transaction():
                target = _review_target(tenant_id=context.tenant_id, institution_id=body.institution_id, record_id=record_id, session=session, collection=database[COLLECTION])
                if target.get("ratifier_principal_id") == context.identity.identity_id:
                    raise HTTPException(status_code=403, detail="G64_SECOND_APPROVER_MUST_BE_INDEPENDENT")
                if target.get("evidence_sha3_512") != body.record_sha3_512_fingerprint:
                    raise HTTPException(status_code=409, detail="G64_REVIEW_RECORD_FINGERPRINT_MISMATCH")
                events = list_review_events(tenant_id=context.tenant_id, institution_id=body.institution_id, record_id=record_id, collection=database[REVIEW_COLLECTION], session=session, limit=100)
                existing_approval = next((row for row in events if row.get("payload", {}).get("event_type") == "SECOND_APPROVAL"), None)
                if existing_approval is not None and existing_approval.get("event_id") != event_id:
                    raise HTTPException(status_code=409, detail="G64_SECOND_APPROVAL_ALREADY_RECORDED")
                verifier = next((row.get("payload", {}) for row in events if row.get("event_id") == body.verification_event_id), None)
                if not isinstance(verifier, dict) or verifier.get("event_type") != "INDEPENDENT_VERIFICATION" or verifier.get("outcome") != "PASS":
                    raise HTTPException(status_code=409, detail="G64_INDEPENDENT_VERIFICATION_PASS_REQUIRED")
                if verifier.get("record_sha3_512_fingerprint") != body.record_sha3_512_fingerprint:
                    raise HTTPException(status_code=409, detail="G64_REVIEW_RECORD_FINGERPRINT_MISMATCH")
                verifier_id = verifier.get("verifier_principal_id")
                if verifier_id in {target.get("ratifier_principal_id"), context.identity.identity_id}:
                    raise HTTPException(status_code=403, detail="G64_SEPARATION_OF_DUTIES_VIOLATION")
                policy = next(
                    (row.get("payload", {}) for row in events
                     if row.get("event_id") == body.policy_decision_event_id),
                    None,
                )
                if (
                    not isinstance(policy, dict)
                    or policy.get("event_type") != "SECOND_APPROVAL_POLICY"
                    or policy.get("verification_event_id") != body.verification_event_id
                    or policy.get("record_sha3_512_fingerprint") != body.record_sha3_512_fingerprint
                ):
                    raise HTTPException(status_code=409, detail="G64_SECOND_APPROVAL_POLICY_REQUIRED")
                if policy.get("second_approval_required") is not True:
                    raise HTTPException(status_code=409, detail="G64_SECOND_APPROVAL_NOT_REQUIRED_BY_POLICY")
                if context.identity.identity_id == policy.get("determined_by_principal_id"):
                    raise HTTPException(status_code=403, detail="G64_POLICY_DECIDER_CANNOT_SECOND_APPROVE")
                event = _review_event(kind="SECOND_APPROVAL", event_id=event_id, tenant_id=context.tenant_id, institution_id=body.institution_id, record_id=record_id, fingerprint=body.record_sha3_512_fingerprint, actor_field="approver_principal_id", actor=context.identity.identity_id, outcome=body.outcome, rationale=body.rationale, evidence=body.evidence, now=now, extra={"verification_event_id": body.verification_event_id, "policy_decision_event_id": body.policy_decision_event_id})
                saved = append_review_event(tenant_id=context.tenant_id, institution_id=body.institution_id, record_id=record_id, event_id=event_id, payload=event, collection=database[REVIEW_COLLECTION], session=session)
    except G64RegistryError as error:
        _raise_registry_http(error)
    except G64ReviewRegistryError as error:
        raise HTTPException(status_code=503, detail=error.code) from error
    except G64WorkspaceEvidenceError as error:
        raise HTTPException(status_code=422, detail=str(error)) from error
    return {"review_event": saved["payload"], "second_approval_status": "RECORDED_NON_AUTHORIZING", "ratification_complete": False, "permits_operational_access": False}


@router.get("/records/{record_id}/review-events")
def read_review_events(record_id: str, institution_id: str = Query(min_length=1, max_length=256), limit: int = Query(default=50, ge=1, le=100), context: TenantAuthorizationContext = Depends(_READ_AUTHORITY)) -> dict[str, object]:
    client, database = _storage()
    try:
        with client.start_session() as session:
            with session.start_transaction():
                _review_target(tenant_id=context.tenant_id, institution_id=institution_id, record_id=record_id, session=session, collection=database[COLLECTION])
                events = list_review_events(tenant_id=context.tenant_id, institution_id=institution_id, record_id=record_id, collection=database[REVIEW_COLLECTION], session=session, limit=limit)
    except G64RegistryError as error:
        _raise_registry_http(error)
    except G64ReviewRegistryError as error:
        raise HTTPException(status_code=503, detail=error.code) from error
    return {"review_events": [item["payload"] for item in events], "ratification_complete": False, "permits_operational_access": False}
