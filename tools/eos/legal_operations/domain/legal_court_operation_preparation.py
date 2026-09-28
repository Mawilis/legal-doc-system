"""WILSY OS immutable internal Court Operation Preparation truth.

TITLE: WILSY OS Legal Court Operation Preparation
VERSION: v1.0.0-L9C12-P1-COURT-OPERATION-PREPARATION
AUTHORITY: Wilsy OS Core Governance / Python EOS Legal Operations
EPITOME: Preserve one immutable, tenant-scoped preparation snapshot for a
         bounded Court filing-preparation intent. This artifact records only
         WILSY preparation and handoff readiness; it never asserts a judicial
         act or external Court result.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tools/eos/legal_operations/domain/legal_court_operation_preparation.py
COLLABORATION / OWNERSHIP: P24 final Representation supplies immutable
                            lineage; a future Court orchestrator owns fresh
                            P21A/P22/Engagement/Mandate and IAM revalidation.
                            This module owns pure immutable preparation truth.
CERTIFICATION / UPDATE DATE: 2026-09-28
CHANGELOG: v1.0.0 establishes preparation-only operation identity, canonical
           document/evidence lineage, deterministic SHA3-512 identity and
           fingerprint, aware-UTC chronology, and no judicial state.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2; ISO 27001.
SECURITY / PRIVACY POSTURE: Opaque references and fingerprints only; no raw
                             documents, Court payloads, credentials, or PII.
TENANT BOUNDARY: Every preparation is bound to one explicit tenant and matter.
AUTHORITY BOUNDARY: Internal preparation and external-handoff readiness only;
                    no filing, acceptance, issuance, service, hearing, order,
                    admission, attorney-of-record, IAM, or financial authority.
TRANSACTION BOUNDARY: Pure immutable construction; no clock, database, network,
                      or transaction lifecycle behavior.
FAIL-CLOSED DECLARATION: Invalid identity, scope, chronology, lineage, schema,
                         or deterministic integrity is rejected.
"""
from __future__ import annotations

import hashlib
import hmac
import json
import re
import unicodedata
from dataclasses import dataclass
from datetime import datetime, timezone
from enum import StrEnum
from typing import Any, Final, Mapping, NoReturn, cast


VERSION: Final[str] = "v1.0.0-L9C12-P1-COURT-OPERATION-PREPARATION"
SCHEMA: Final[str] = "WILSY-LEGAL-COURT-OPERATION-PREPARATION/V1"
_IDENTITY: Final[re.Pattern[str]] = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._:-]{0,159}$")
_HEX: Final[re.Pattern[str]] = re.compile(r"^[0-9a-f]{128}$")
_FORBIDDEN_TENANTS: Final[frozenset[str]] = frozenset({"default", "global", "global_root", "root", "master", "*"})
_PREPARATION_SCOPE: Final[str] = "COURT_FILING_PREPARATION"


class LegalCourtOperationPreparationError(ValueError):
    """Stable, non-sensitive fail-closed preparation-domain error."""

    def __init__(self, code: str) -> None:
        self.code = code
        super().__init__(code)


class LegalCourtOperationType(StrEnum):
    """Initial preparation-only Court operation vocabulary."""

    COURT_FILING_PREPARATION = "COURT_FILING_PREPARATION"


class LegalCourtOperationPreparationState(StrEnum):
    """Internal preparation snapshots; none is a judicial result."""

    PREPARATION_REQUIRED = "PREPARATION_REQUIRED"
    READY_FOR_EXTERNAL_HANDOFF = "READY_FOR_EXTERNAL_HANDOFF"
    HANDED_OFF_EXTERNALLY = "HANDED_OFF_EXTERNALLY"
    EXTERNAL_EVIDENCE_PENDING = "EXTERNAL_EVIDENCE_PENDING"
    EXTERNAL_EVIDENCE_RECORDED = "EXTERNAL_EVIDENCE_RECORDED"
    BLOCKED = "BLOCKED"


_FIELDS: Final[tuple[str, ...]] = (
    "schema",
    "preparation_version",
    "operation_preparation_id",
    "tenant_id",
    "case_matter_id",
    "matter_fingerprint",
    "final_representation_id",
    "final_representation_fingerprint",
    "operation_type",
    "target_court_reference",
    "target_jurisdiction_reference",
    "document_evidence_lineage",
    "requested_scope_capabilities",
    "preparation_state",
    "source_evidence_reference",
    "source_evidence_fingerprint",
    "provenance_reference",
    "prepared_at",
    "occurred_at",
    "idempotency_key",
    "fingerprint",
)
COURT_OPERATION_PREPARATION_FIELDS: Final[frozenset[str]] = frozenset(_FIELDS)


def _fail(code: str, cause: BaseException | None = None) -> NoReturn:
    error = LegalCourtOperationPreparationError(code)
    if cause is None:
        raise error
    raise error from cause


def _identity(name: str, value: object) -> str:
    if not isinstance(value, str) or _IDENTITY.fullmatch(value) is None:
        _fail(f"L9C12_P1_{name.upper()}_INVALID")
    return value


def _tenant(value: object) -> str:
    tenant = _identity("tenant_id", value)
    if tenant.casefold() in _FORBIDDEN_TENANTS:
        _fail("L9C12_P1_TENANT_REQUIRED")
    return tenant


def _fingerprint(name: str, value: object) -> str:
    if not isinstance(value, str) or _HEX.fullmatch(value) is None:
        _fail(f"L9C12_P1_{name.upper()}_INVALID")
    return value


def _reference(name: str, value: object, *, limit: int = 512) -> str:
    if not isinstance(value, str) or not value or value != value.strip() or len(value) > limit:
        _fail(f"L9C12_P1_{name.upper()}_INVALID")
    if any(ord(ch) < 32 or 0x7F <= ord(ch) <= 0x9F or 0xD800 <= ord(ch) <= 0xDFFF for ch in value):
        _fail(f"L9C12_P1_{name.upper()}_INVALID")
    normalized = unicodedata.normalize("NFC", value)
    if not normalized or len(normalized) > limit:
        _fail(f"L9C12_P1_{name.upper()}_INVALID")
    return normalized


def _references(name: str, value: object, *, limit: int = 128) -> tuple[str, ...]:
    if isinstance(value, str) or not isinstance(value, (tuple, list, set, frozenset)) or not value:
        _fail(f"L9C12_P1_{name.upper()}_INVALID")
    values = tuple(_reference(name, item) for item in value)
    if len(values) != len(set(values)) or len(values) > limit:
        _fail(f"L9C12_P1_{name.upper()}_INVALID")
    return tuple(sorted(values))


def _scope(value: object) -> tuple[str, ...]:
    scope = _references("requested_scope_capabilities", value)
    if scope != (_PREPARATION_SCOPE,):
        _fail("L9C12_P1_SCOPE_FORBIDDEN")
    return scope


def _timestamp(name: str, value: object) -> datetime:
    parsed = value
    if isinstance(parsed, str):
        try:
            parsed = datetime.fromisoformat(parsed.replace("Z", "+00:00"))
        except ValueError as error:
            _fail(f"L9C12_P1_{name.upper()}_INVALID", error)
    if not isinstance(parsed, datetime) or parsed.tzinfo is None or parsed.utcoffset() is None:
        _fail(f"L9C12_P1_{name.upper()}_INVALID")
    return parsed.astimezone(timezone.utc)


def _json_value(value: object) -> object:
    if isinstance(value, datetime):
        return value.astimezone(timezone.utc).isoformat(timespec="microseconds").replace("+00:00", "Z")
    return value


def _digest_payload(instance: "LegalCourtOperationPreparation", fields: tuple[str, ...]) -> bytes:
    payload = {field: _json_value(getattr(instance, field)) for field in fields}
    return json.dumps(payload, ensure_ascii=False, allow_nan=False, sort_keys=False, separators=(",", ":")).encode("utf-8")


def _operation_preparation_id(instance: "LegalCourtOperationPreparation") -> str:
    digest = hashlib.sha3_512(_digest_payload(instance, tuple(field for field in _FIELDS if field not in {"operation_preparation_id", "fingerprint"}))).hexdigest()
    return f"court-operation-preparation:{digest[:48]}"


def _fingerprint_for(instance: "LegalCourtOperationPreparation") -> str:
    return hashlib.sha3_512(_digest_payload(instance, _FIELDS[:-1])).hexdigest()


@dataclass(frozen=True, slots=True)
class LegalCourtOperationPreparation:
    """Immutable internal preparation snapshot with no judicial state."""

    tenant_id: str
    case_matter_id: str
    matter_fingerprint: str
    final_representation_id: str
    final_representation_fingerprint: str
    operation_type: LegalCourtOperationType | str
    target_court_reference: str
    target_jurisdiction_reference: str
    document_evidence_lineage: tuple[str, ...] | list[str]
    requested_scope_capabilities: tuple[str, ...] | list[str]
    preparation_state: LegalCourtOperationPreparationState | str
    source_evidence_reference: str
    source_evidence_fingerprint: str
    provenance_reference: str
    prepared_at: datetime
    occurred_at: datetime
    idempotency_key: str
    operation_preparation_id: str = ""
    schema: str = SCHEMA
    preparation_version: str = VERSION
    fingerprint: str = ""

    def __post_init__(self) -> None:
        """Normalize, validate, and derive deterministic immutable identities."""
        if self.schema != SCHEMA or self.preparation_version != VERSION:
            _fail("L9C12_P1_IDENTITY_INVALID")
        operation = self.operation_type.value if isinstance(self.operation_type, StrEnum) else self.operation_type
        state = self.preparation_state.value if isinstance(self.preparation_state, StrEnum) else self.preparation_state
        if operation != LegalCourtOperationType.COURT_FILING_PREPARATION.value:
            _fail("L9C12_P1_OPERATION_TYPE_FORBIDDEN")
        try:
            state_value = LegalCourtOperationPreparationState(state)
        except (TypeError, ValueError) as error:
            _fail("L9C12_P1_PREPARATION_STATE_INVALID", error)
        normalized: dict[str, object] = {
            "tenant_id": _tenant(self.tenant_id),
            "case_matter_id": _identity("case_matter_id", self.case_matter_id),
            "matter_fingerprint": _fingerprint("matter_fingerprint", self.matter_fingerprint),
            "final_representation_id": _identity("final_representation_id", self.final_representation_id),
            "final_representation_fingerprint": _fingerprint("final_representation_fingerprint", self.final_representation_fingerprint),
            "operation_type": LegalCourtOperationType.COURT_FILING_PREPARATION,
            "target_court_reference": _reference("target_court_reference", self.target_court_reference),
            "target_jurisdiction_reference": _reference("target_jurisdiction_reference", self.target_jurisdiction_reference),
            "document_evidence_lineage": _references("document_evidence_lineage", self.document_evidence_lineage),
            "requested_scope_capabilities": _scope(self.requested_scope_capabilities),
            "preparation_state": state_value,
            "source_evidence_reference": _reference("source_evidence_reference", self.source_evidence_reference),
            "source_evidence_fingerprint": _fingerprint("source_evidence_fingerprint", self.source_evidence_fingerprint),
            "provenance_reference": _reference("provenance_reference", self.provenance_reference),
            "prepared_at": _timestamp("prepared_at", self.prepared_at),
            "occurred_at": _timestamp("occurred_at", self.occurred_at),
            "idempotency_key": _reference("idempotency_key", self.idempotency_key, limit=240),
        }
        if cast(datetime, normalized["occurred_at"]) < cast(datetime, normalized["prepared_at"]):
            _fail("L9C12_P1_OCCURRED_BEFORE_PREPARED")
        for name, value in normalized.items():
            object.__setattr__(self, name, value)
        derived_id = _operation_preparation_id(self)
        if self.operation_preparation_id and self.operation_preparation_id != derived_id:
            _fail("L9C12_P1_OPERATION_PREPARATION_ID_MISMATCH")
        object.__setattr__(self, "operation_preparation_id", derived_id)
        digest = _fingerprint_for(self)
        if self.fingerprint and (not isinstance(self.fingerprint, str) or not hmac.compare_digest(self.fingerprint, digest)):
            _fail("L9C12_P1_FINGERPRINT_MISMATCH")
        object.__setattr__(self, "fingerprint", digest)

    def to_dict(self) -> dict[str, object]:
        """Serialize exact preparation truth without external Court claims."""
        return {field: _json_value(getattr(self, field)) for field in _FIELDS}

    @classmethod
    def from_dict(cls, payload: Mapping[str, object]) -> "LegalCourtOperationPreparation":
        """Hydrate exactly the P1 schema and verify deterministic integrity."""
        if not isinstance(payload, Mapping) or set(payload) != set(COURT_OPERATION_PREPARATION_FIELDS):
            _fail("L9C12_P1_SCHEMA_INVALID")
        values = dict(payload)
        stored = values.pop("fingerprint")
        result = cls(**cast(Any, values))
        if not isinstance(stored, str) or not hmac.compare_digest(stored, result.fingerprint):
            _fail("L9C12_P1_FINGERPRINT_MISMATCH")
        return result


__all__ = [
    "COURT_OPERATION_PREPARATION_FIELDS",
    "LegalCourtOperationPreparation",
    "LegalCourtOperationPreparationError",
    "LegalCourtOperationPreparationState",
    "LegalCourtOperationType",
    "SCHEMA",
    "VERSION",
]


# ARTIFACT: legal_court_operation_preparation.py
# VERSION: v1.0.0-L9C12-P1-COURT-OPERATION-PREPARATION
# AUTHORITY BOUNDARY: immutable internal Court preparation only
# TENANT POSTURE: explicit tenant and matter binding; no cross-tenant inference
# FAIL-CLOSED POSTURE: invalid lineage, scope, chronology, schema and integrity reject
# FINANCIAL EXECUTION AUTHORITY: none; judicial acts remain external evidence
# END OF WILSY OS SOVEREIGN ARTIFACT
