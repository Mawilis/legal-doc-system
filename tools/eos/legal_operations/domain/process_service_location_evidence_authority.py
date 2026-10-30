"""Attempt-bound, purpose-limited Deputy GPS evidence authority.

TITLE: Wilsy OS Process-Service Location Evidence Authority
VERSION: v1.0.0-PROCESS-SERVICE-LOCATION-EVIDENCE
AUTHORITY: Wilsy OS Core Governance
EPITOME: Admit immutable GPS observations only under explicit permission and
         exact canonical allocation/attempt; never derive service or return truth.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tools/eos/legal_operations/domain/process_service_location_evidence_authority.py
COLLABORATION / OWNERSHIP: P5L location evidence; P1 owns service lifecycle,
                            P2 lifecycle snapshots, P4 allocation/custody,
                            IAM principal/device admission; callers own transactions.
CERTIFICATION / UPDATE DATE: 2026-10-30
CHANGELOG: 2026-10-30 v1.0.0 adds immutable permission grants and GPS observations.
COMPLIANCE: Privacy-by-design controls aligned to POPIA section 19 and GDPR
            Article 32; no legal-compliance finding is made by this module.
SECURITY / PRIVACY POSTURE: Exact purpose, tenant, Deputy, device and attempt
                            binding; explicit permission evidence; bounded
                            coordinates, accuracy and capture time.
TENANT BOUNDARY: Tenant and legal identities derive from canonical P1/P4 records.
AUTHORITY BOUNDARY: Location is evidence only, never proof of presence, service,
                    outcome or Return of Service. No continuous tracking authority.
FINANCIAL AUTHORITY BOUNDARY: Kennel EOS exclusively owns financial execution.
FAIL-CLOSED DECLARATION: Factory-only immutable values, UTC chronology, exact
                         source correlation and SHA3-512 integrity are required.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timedelta
import hashlib
import json
import math
import re
from typing import Final, NoReturn, cast

from tools.eos.legal_operations.domain.legal_operations_lifecycle import ServiceAttempt
from tools.eos.legal_operations.registry.process_service_allocation_registry import (
    ProcessServiceAllocationCurrent,
    ProcessServiceAllocationReceipt,
)

VERSION: Final[str] = "v1.0.0-PROCESS-SERVICE-LOCATION-EVIDENCE"
SCHEMA: Final[str] = "WILSY-PROCESS-SERVICE-LOCATION-EVIDENCE/V1"
LOCATION_PURPOSE: Final[str] = "PROCESS_SERVICE_ATTEMPT_FIELD_EVIDENCE"
_ID = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._:-]{0,127}$")
_SHA3 = re.compile(r"^[0-9a-f]{128}$")
_FORBIDDEN = frozenset({"default", "global", "global_root", "root", "master", "*"})

class ProcessServiceLocationEvidenceAuthorityError(ValueError):
    """Stable fail-closed location-evidence error."""
    def __init__(self, code: str) -> None:
        self.code = code
        super().__init__(code)

def _fail(code: str) -> NoReturn:
    raise ProcessServiceLocationEvidenceAuthorityError(code)

def _id(name: str, value: object) -> str:
    if not isinstance(value, str) or value != value.strip() or _ID.fullmatch(value) is None:
        _fail(f"P5L_{name.upper()}_INVALID")
    return value

def _tenant(value: object) -> str:
    tenant = _id("tenant_id", value)
    if tenant.casefold() in _FORBIDDEN:
        _fail("P5L_TENANT_INVALID")
    return tenant

def _time(name: str, value: object) -> datetime:
    if not isinstance(value, datetime) or value.tzinfo is None or value.utcoffset() != timedelta(0):
        _fail(f"P5L_{name.upper()}_INVALID")
    return value

def _hash(name: str, value: object) -> str:
    if not isinstance(value, str) or _SHA3.fullmatch(value) is None:
        _fail(f"P5L_{name.upper()}_INVALID")
    return value

def _ref(name: str, value: object) -> str:
    if not isinstance(value, str) or value != value.strip() or not value or len(value) > 512:
        _fail(f"P5L_{name.upper()}_INVALID")
    return value

def _digest(value: object) -> str:
    raw = json.dumps(value, ensure_ascii=False, allow_nan=False, sort_keys=True, separators=(",", ":"))
    return hashlib.sha3_512(raw.encode("utf-8")).hexdigest()

def _proof_contract():
    @dataclass(frozen=True, slots=True)
    class Proof:
        digest: str
    def issue(digest: str) -> object:
        return Proof(digest)
    def read(value: object) -> str | None:
        return value.digest if isinstance(value, Proof) else None
    return issue, read

_issue, _read_proof = _proof_contract()

def _allocation(attempt: ServiceAttempt, receipt: ProcessServiceAllocationReceipt,
                current: ProcessServiceAllocationCurrent) -> None:
    if (receipt.tenant_id != attempt.tenant_id or receipt.instruction_id != attempt.instruction_id
        or receipt.document_id != attempt.document_id or receipt.deputy_id != attempt.deputy_id
        or receipt.allocation_evidence_reference != attempt.allocation_evidence_reference
        or current.tenant_id != receipt.tenant_id or current.document_id != receipt.document_id
        or current.process_document_fingerprint != receipt.allocated_document_fingerprint
        or current.custody_chain_fingerprint != receipt.result_custody_chain_fingerprint
        or current.custody_head_event_id != receipt.allocation_custody_event_id
        or current.custody_head_fingerprint != receipt.allocation_custody_event_fingerprint
        or current.custody_head_sequence_number != receipt.prior_custody_head_sequence_number + 1
        or current.current_holder_reference != receipt.deputy_id
        or receipt.to_holder_reference != receipt.deputy_id
        or current.authority_evidence_reference != receipt.allocation_command_id
        or current.authority_evidence_fingerprint != receipt.fingerprint):
        _fail("P5L_ALLOCATION_CORRELATION_INVALID")

def _grant_payload(v: dict[str, object]) -> dict[str, object]:
    return {"schema": SCHEMA, "version": VERSION, "entity_type": "LocationPermissionGrant",
            **v, "granted_at": cast(datetime, v["granted_at"]).isoformat(),
            "expires_at": cast(datetime, v["expires_at"]).isoformat()}

@dataclass(frozen=True, slots=True)
class ProcessServiceLocationPermissionGrant:
    """Verified explicit permission scoped to one tenant, Deputy, attempt and device."""
    tenant_id: str
    grant_id: str
    attempt_id: str
    deputy_id: str
    device_id: str
    purpose: str
    permission_evidence_reference: str
    permission_evidence_fingerprint: str
    granted_at: datetime
    expires_at: datetime
    _proof: object = field(default=None, repr=False, compare=False)

    def to_dict(self) -> dict[str, object]:
        """Return deterministic permission evidence."""
        return _grant_payload({"tenant_id": self.tenant_id, "grant_id": self.grant_id,
            "attempt_id": self.attempt_id, "deputy_id": self.deputy_id, "device_id": self.device_id,
            "purpose": self.purpose, "permission_evidence_reference": self.permission_evidence_reference,
            "permission_evidence_fingerprint": self.permission_evidence_fingerprint,
            "granted_at": self.granted_at, "expires_at": self.expires_at})

    def __post_init__(self) -> None:
        if _read_proof(self._proof) != _digest(self.to_dict()):
            _fail("P5L_PERMISSION_GRANT_FACTORY_REQUIRED")
        _tenant(self.tenant_id)
        for key in ("grant_id", "attempt_id", "deputy_id", "device_id"):
            _id(key, getattr(self, key))
        if self.purpose != LOCATION_PURPOSE:
            _fail("P5L_PERMISSION_PURPOSE_INVALID")
        _ref("permission_evidence_reference", self.permission_evidence_reference)
        _hash("permission_evidence_fingerprint", self.permission_evidence_fingerprint)
        if _time("expires_at", self.expires_at) <= _time("granted_at", self.granted_at):
            _fail("P5L_PERMISSION_WINDOW_INVALID")

    @property
    def fingerprint(self) -> str:
        """Return SHA3-512 of the canonical grant."""
        return _digest(self.to_dict())

def create_location_permission_grant(*, attempt: ServiceAttempt,
    allocation_receipt: ProcessServiceAllocationReceipt,
    allocation_current: ProcessServiceAllocationCurrent, grant_id: str, device_id: str,
    permission_granted: bool, purpose: str, permission_evidence_reference: str,
    permission_evidence_fingerprint: str, granted_at: datetime, expires_at: datetime
) -> ProcessServiceLocationPermissionGrant:
    """Issue a bounded grant only after a trusted permission verifier confirms consent."""
    if permission_granted is not True:
        _fail("P5L_PERMISSION_NOT_GRANTED")
    if type(attempt) is not ServiceAttempt or type(allocation_receipt) is not ProcessServiceAllocationReceipt or type(allocation_current) is not ProcessServiceAllocationCurrent:
        _fail("P5L_SOURCE_CONTEXT_REQUIRED")
    try:
        attempt.__post_init__(); allocation_receipt.__post_init__(); allocation_current.__post_init__()
    except Exception as error:
        raise ProcessServiceLocationEvidenceAuthorityError("P5L_SOURCE_CONTEXT_INVALID") from error
    _allocation(attempt, allocation_receipt, allocation_current)
    start, end = _time("granted_at", granted_at), _time("expires_at", expires_at)
    if start < attempt.allocated_at or end <= start or purpose != LOCATION_PURPOSE:
        _fail("P5L_PERMISSION_WINDOW_OR_PURPOSE_INVALID")
    values: dict[str, object] = {"tenant_id": attempt.tenant_id, "grant_id": _id("grant_id", grant_id),
        "attempt_id": attempt.attempt_id, "deputy_id": attempt.deputy_id,
        "device_id": _id("device_id", device_id), "purpose": purpose,
        "permission_evidence_reference": _ref("permission_evidence_reference", permission_evidence_reference),
        "permission_evidence_fingerprint": _hash("permission_evidence_fingerprint", permission_evidence_fingerprint),
        "granted_at": start, "expires_at": end}
    return ProcessServiceLocationPermissionGrant(**values, _proof=_issue(_digest(_grant_payload(values))))

def _observation_payload(v: dict[str, object]) -> dict[str, object]:
    payload = dict(v)
    payload["captured_at"] = cast(datetime, v["captured_at"]).isoformat()
    return {"schema": SCHEMA, "version": VERSION, "entity_type": "LocationObservation", **payload}

@dataclass(frozen=True, slots=True)
class ProcessServiceLocationObservation:
    """Immutable GPS evidence; never a service outcome or Return of Service."""
    tenant_id: str
    observation_id: str
    grant_id: str
    attempt_id: str
    deputy_id: str
    device_id: str
    district_id: str
    sheriff_office_id: str
    source_attempt_fingerprint: str
    purpose: str
    latitude: float
    longitude: float
    horizontal_accuracy_m: float
    captured_at: datetime
    device_provenance_reference: str
    device_provenance_fingerprint: str
    permission_grant_fingerprint: str
    evidence_reference: str
    _proof: object = field(default=None, repr=False, compare=False)

    def to_dict(self) -> dict[str, object]:
        """Return deterministic canonical GPS evidence."""
        return _observation_payload({"tenant_id": self.tenant_id, "observation_id": self.observation_id,
            "grant_id": self.grant_id, "attempt_id": self.attempt_id, "deputy_id": self.deputy_id,
            "device_id": self.device_id, "district_id": self.district_id,
            "sheriff_office_id": self.sheriff_office_id,
            "source_attempt_fingerprint": self.source_attempt_fingerprint, "purpose": self.purpose,
            "latitude": float(self.latitude), "longitude": float(self.longitude),
            "horizontal_accuracy_m": float(self.horizontal_accuracy_m), "captured_at": self.captured_at,
            "device_provenance_reference": self.device_provenance_reference,
            "device_provenance_fingerprint": self.device_provenance_fingerprint,
            "permission_grant_fingerprint": self.permission_grant_fingerprint,
            "evidence_reference": self.evidence_reference})

    def __post_init__(self) -> None:
        if _read_proof(self._proof) != _digest(self.to_dict()):
            _fail("P5L_OBSERVATION_FACTORY_REQUIRED")
        _tenant(self.tenant_id)
        for key in ("observation_id", "grant_id", "attempt_id", "deputy_id", "device_id", "district_id", "sheriff_office_id"):
            _id(key, getattr(self, key))
        for key in ("source_attempt_fingerprint", "device_provenance_fingerprint", "permission_grant_fingerprint"):
            _hash(key, getattr(self, key))
        for key in ("device_provenance_reference", "evidence_reference"):
            _ref(key, getattr(self, key))
        if self.purpose != LOCATION_PURPOSE:
            _fail("P5L_OBSERVATION_PURPOSE_INVALID")
        for key, value, low, high in (("latitude", self.latitude, -90, 90), ("longitude", self.longitude, -180, 180)):
            if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value) or not low <= value <= high:
                _fail(f"P5L_{key.upper()}_INVALID")
        accuracy = self.horizontal_accuracy_m
        if isinstance(accuracy, bool) or not isinstance(accuracy, (int, float)) or not math.isfinite(accuracy) or not 0 < accuracy <= 10000:
            _fail("P5L_HORIZONTAL_ACCURACY_INVALID")
        _time("captured_at", self.captured_at)

    @property
    def fingerprint(self) -> str:
        """Return SHA3-512 over the immutable observation."""
        return _digest(self.to_dict())

def create_process_service_location_observation(*, attempt: ServiceAttempt,
    allocation_receipt: ProcessServiceAllocationReceipt,
    allocation_current: ProcessServiceAllocationCurrent,
    permission_grant: ProcessServiceLocationPermissionGrant, observation_id: str,
    device_id: str, latitude: float, longitude: float, horizontal_accuracy_m: float,
    captured_at: datetime, device_provenance_reference: str,
    device_provenance_fingerprint: str, evidence_reference: str
) -> ProcessServiceLocationObservation:
    """Admit one GPS observation inside an unexpired exact attempt/device grant."""
    if type(attempt) is not ServiceAttempt or type(permission_grant) is not ProcessServiceLocationPermissionGrant:
        _fail("P5L_SOURCE_AUTHORITY_REQUIRED")
    if type(allocation_receipt) is not ProcessServiceAllocationReceipt or type(allocation_current) is not ProcessServiceAllocationCurrent:
        _fail("P5L_ALLOCATION_CONTEXT_REQUIRED")
    try:
        attempt.__post_init__(); permission_grant.__post_init__()
        allocation_receipt.__post_init__(); allocation_current.__post_init__()
    except Exception as error:
        raise ProcessServiceLocationEvidenceAuthorityError("P5L_SOURCE_CONTEXT_INVALID") from error
    captured = _time("captured_at", captured_at)
    _allocation(attempt, allocation_receipt, allocation_current)
    if (permission_grant.tenant_id != attempt.tenant_id or permission_grant.attempt_id != attempt.attempt_id
        or permission_grant.deputy_id != attempt.deputy_id or permission_grant.device_id != device_id
        or captured < permission_grant.granted_at or captured > permission_grant.expires_at
        or captured < attempt.allocated_at):
        _fail("P5L_PERMISSION_SCOPE_OR_WINDOW_INVALID")
    values: dict[str, object] = {"tenant_id": attempt.tenant_id,
        "observation_id": _id("observation_id", observation_id), "grant_id": permission_grant.grant_id,
        "attempt_id": attempt.attempt_id, "deputy_id": attempt.deputy_id,
        "device_id": _id("device_id", device_id), "district_id": allocation_receipt.district_id,
        "sheriff_office_id": allocation_receipt.sheriff_office_id,
        "source_attempt_fingerprint": attempt.fingerprint, "purpose": LOCATION_PURPOSE,
        "latitude": latitude, "longitude": longitude, "horizontal_accuracy_m": horizontal_accuracy_m,
        "captured_at": captured, "device_provenance_reference": _ref("device_provenance_reference", device_provenance_reference),
        "device_provenance_fingerprint": _hash("device_provenance_fingerprint", device_provenance_fingerprint),
        "permission_grant_fingerprint": permission_grant.fingerprint,
        "evidence_reference": _ref("evidence_reference", evidence_reference)}
    payload = _observation_payload(values)
    return ProcessServiceLocationObservation(**values, _proof=_issue(_digest(payload)))

# ARTIFACT: process_service_location_evidence_authority.py
# VERSION: v1.0.0-PROCESS-SERVICE-LOCATION-EVIDENCE
# AUTHORITY BOUNDARY: purpose-limited GPS evidence only; no service outcome or ReturnOfService.
# TENANT POSTURE: exact canonical tenant, allocation, Deputy, device and attempt.
# FAIL-CLOSED POSTURE: explicit permission, bounded UTC window, source binding and integrity validation.
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively.
# END OF WILSY OS SOVEREIGN ARTIFACT
