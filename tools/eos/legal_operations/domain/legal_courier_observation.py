"""WILSY OS immutable Legal Operations courier observation evidence.

TITLE: Legal Operations Courier Observation Evidence Domain
VERSION: v1.0.0-L8-8A-COURIER-OBSERVATION-EVIDENCE
AUTHORITY: Wilsy OS Core Governance / Python EOS Legal Operations
EPITOME: Normalize one external courier event into immutable tenant-, matter-,
         and process-document-bound observation evidence without allowing a
         provider status to become Legal lifecycle, service, return, billing,
         payment, execution, settlement, Court, custody, or IAM truth.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tools/eos/legal_operations/domain/legal_courier_observation.py
COLLABORATION / OWNERSHIP: P1 Legal Operations lifecycle owns CaseMatter and
                            ProcessDocument truth. External courier providers
                            own only their transport observations. This pure
                            domain owns bounded normalization and integrity
                            evidence only. Later registries/HTTP/provider
                            adapters remain separate certified gates.
CERTIFICATION / UPDATE DATE: 2026-10-12
CHANGELOG: 2026-10-12 v1.0.0-L8-8A-COURIER-OBSERVATION-EVIDENCE establishes
           provider-neutral courier observation kinds, canonical P1-derived
           tenant/matter/document scope, bounded provider/tracking/status
           metadata, UTC chronology, deterministic SHA3-512 integrity,
           strict hydration, and explicit downstream-authority firewalls.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2; ISO 27001.
SECURITY / PRIVACY POSTURE: Opaque identifiers and bounded provider status only.
                             No address, GPS, signature image, raw provider
                             payload, credential, secret, token, personal
                             contact data, document bytes, payment data, or AI
                             payload is accepted or emitted.
TENANT BOUNDARY: Tenant, case_matter_id and document_id are derived only from
                 validated canonical CaseMatter and ProcessDocument evidence.
                 Provider input cannot establish or widen tenant/matter scope.
AUTHORITY BOUNDARY: Courier observation evidence only. DISPATCH_ACCEPTED,
                    IN_TRANSIT, DELIVERY_ATTEMPTED and DELIVERY_REPORTED are
                    external observations, not ProcessDocument transitions,
                    custody facts, ServiceAttempt outcomes, ServiceExecution,
                    ReturnOfService, Court filing, invoice, payment, execution,
                    settlement, notification-delivery or client-acceptance truth.
TRANSACTION BOUNDARY: Pure immutable in-memory composition and hydration only;
                      no MongoDB, session, transaction, filesystem, HTTP,
                      provider call, queue dispatch, retry or clock ownership.
FINANCIAL AUTHORITY BOUNDARY: None. Kennel EOS remains the exclusive financial
                              execution authority; settlement remains separate.
FAIL-CLOSED DECLARATION: Invalid canonical sources, cross-scope correlation,
                         malformed provider metadata, chronology, schema,
                         event vocabulary or fingerprint divergence rejects
                         without coercion, repair, fallback or authority expansion.
"""
from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from datetime import datetime, timezone
from enum import StrEnum
import hashlib
import hmac
import json
import re
import unicodedata
from typing import Any, Final, NoReturn, cast

from tools.eos.legal_operations.domain.legal_operations_lifecycle import (
    CaseMatter,
    ProcessDocument,
)


VERSION: Final[str] = "v1.0.0-L8-8A-COURIER-OBSERVATION-EVIDENCE"
SCHEMA: Final[str] = "WILSY-LEGAL-COURIER-OBSERVATION/V1"

_IDENTITY: Final[re.Pattern[str]] = re.compile(
    r"^[A-Za-z0-9][A-Za-z0-9._:-]{0,159}$"
)
_PROVIDER_KEY: Final[re.Pattern[str]] = re.compile(
    r"^[A-Za-z0-9][A-Za-z0-9._:-]{0,63}$"
)
_HEX: Final[re.Pattern[str]] = re.compile(r"^[0-9a-f]{128}$")
_FORBIDDEN_TENANTS: Final[frozenset[str]] = frozenset(
    {"default", "global", "global_root", "root", "master", "*"}
)

_FIELDS: Final[tuple[str, ...]] = (
    "schema",
    "courier_observation_version",
    "tenant_id",
    "case_matter_id",
    "matter_fingerprint",
    "document_id",
    "document_fingerprint",
    "observation_id",
    "provider_key",
    "tracking_reference",
    "provider_event_reference",
    "event_kind",
    "provider_status",
    "observed_at",
    "source_evidence_reference",
    "source_evidence_fingerprint",
    "fingerprint",
)
LEGAL_COURIER_OBSERVATION_FIELDS: Final[tuple[str, ...]] = _FIELDS


class LegalCourierObservationKind(StrEnum):
    """Bounded provider-neutral courier observation vocabulary.

    These values describe only what an external courier channel reported.
    No value is a Legal Operations lifecycle transition or proof of service.
    """

    DISPATCH_ACCEPTED = "DISPATCH_ACCEPTED"
    IN_TRANSIT = "IN_TRANSIT"
    DELIVERY_ATTEMPTED = "DELIVERY_ATTEMPTED"
    DELIVERY_REPORTED = "DELIVERY_REPORTED"
    FAILED = "FAILED"
    CANCELLED = "CANCELLED"


class LegalCourierObservationError(ValueError):
    """Stable fail-closed error for invalid courier observation evidence."""

    def __init__(self, code: str) -> None:
        """Expose one bounded machine code without echoing supplied values."""
        self.code = code
        super().__init__(code)


def _fail(code: str) -> NoReturn:
    """Raise one bounded courier-observation validation failure."""
    raise LegalCourierObservationError(code)


def _text(name: str, value: object, *, limit: int) -> str:
    """Return exact bounded NFC text without controls or surrounding whitespace."""
    if not isinstance(value, str) or not value or value != value.strip():
        _fail(f"L8_8A_{name.upper()}_INVALID")
    normalized = unicodedata.normalize("NFC", value)
    if (
        not normalized
        or len(normalized) > limit
        or any(ord(character) < 32 or ord(character) == 127 for character in normalized)
    ):
        _fail(f"L8_8A_{name.upper()}_INVALID")
    return normalized


def _identity(name: str, value: object) -> str:
    """Require one canonical opaque WILSY identity."""
    identity = _text(name, value, limit=160)
    if _IDENTITY.fullmatch(identity) is None:
        _fail(f"L8_8A_{name.upper()}_INVALID")
    return identity


def _tenant(value: object) -> str:
    """Require one explicit non-pseudo tenant identity."""
    tenant_id = _identity("tenant_id", value)
    if tenant_id.casefold() in _FORBIDDEN_TENANTS:
        _fail("L8_8A_TENANT_REQUIRED")
    return tenant_id


def _provider_key(value: object) -> str:
    """Require one bounded opaque provider-family key, never a credential."""
    provider = _text("provider_key", value, limit=64)
    if _PROVIDER_KEY.fullmatch(provider) is None:
        _fail("L8_8A_PROVIDER_KEY_INVALID")
    return provider


def _fingerprint(name: str, value: object) -> str:
    """Require canonical lowercase SHA3-512 hexadecimal evidence."""
    if not isinstance(value, str) or _HEX.fullmatch(value) is None:
        _fail(f"L8_8A_{name.upper()}_INVALID")
    return value


def _when(name: str, value: object) -> datetime:
    """Normalize one timezone-aware timestamp to canonical UTC."""
    parsed = value
    if isinstance(parsed, str):
        try:
            parsed = datetime.fromisoformat(parsed.replace("Z", "+00:00"))
        except ValueError as error:
            raise LegalCourierObservationError(
                f"L8_8A_{name.upper()}_INVALID"
            ) from error
    if (
        not isinstance(parsed, datetime)
        or parsed.tzinfo is None
        or parsed.utcoffset() is None
    ):
        _fail(f"L8_8A_{name.upper()}_INVALID")
    return parsed.astimezone(timezone.utc)


def _json_value(value: object) -> object:
    """Project exact domain values into deterministic JSON-compatible form."""
    if isinstance(value, datetime):
        return value.astimezone(timezone.utc).isoformat().replace("+00:00", "Z")
    if isinstance(value, StrEnum):
        return value.value
    return value


def _digest(payload: Mapping[str, object]) -> str:
    """Return deterministic lowercase SHA3-512 over one canonical payload."""
    return hashlib.sha3_512(
        json.dumps(
            payload,
            ensure_ascii=False,
            allow_nan=False,
            sort_keys=False,
            separators=(",", ":"),
        ).encode("utf-8")
    ).hexdigest()


@dataclass(frozen=True, slots=True)
class LegalCourierObservation:
    """Immutable external courier observation bound to canonical Legal scope.

    This value records only a normalized external observation. It cannot advance
    CaseMatter, ProcessDocument, custody, ServiceAttempt, ServiceExecution,
    ReturnOfService, billing, notification, payment, settlement or Court state.
    """

    tenant_id: str
    case_matter_id: str
    matter_fingerprint: str
    document_id: str
    document_fingerprint: str
    observation_id: str
    provider_key: str
    tracking_reference: str
    provider_event_reference: str
    event_kind: LegalCourierObservationKind
    provider_status: str
    observed_at: datetime
    source_evidence_reference: str
    source_evidence_fingerprint: str
    schema: str = SCHEMA
    courier_observation_version: str = VERSION
    fingerprint: str = ""

    def __post_init__(self) -> None:
        """Validate scope, provider metadata and deterministic integrity."""
        tenant_id = _tenant(self.tenant_id)
        case_matter_id = _identity("case_matter_id", self.case_matter_id)
        matter_fingerprint = _fingerprint(
            "matter_fingerprint", self.matter_fingerprint
        )
        document_id = _identity("document_id", self.document_id)
        document_fingerprint = _fingerprint(
            "document_fingerprint", self.document_fingerprint
        )
        observation_id = _identity("observation_id", self.observation_id)
        provider_key = _provider_key(self.provider_key)
        tracking_reference = _text(
            "tracking_reference", self.tracking_reference, limit=256
        )
        provider_event_reference = _text(
            "provider_event_reference",
            self.provider_event_reference,
            limit=256,
        )
        if not isinstance(self.event_kind, LegalCourierObservationKind):
            _fail("L8_8A_EVENT_KIND_INVALID")
        provider_status = _text(
            "provider_status", self.provider_status, limit=128
        )
        observed_at = _when("observed_at", self.observed_at)
        source_reference = _text(
            "source_evidence_reference",
            self.source_evidence_reference,
            limit=512,
        )
        source_fingerprint = _fingerprint(
            "source_evidence_fingerprint",
            self.source_evidence_fingerprint,
        )
        if (
            self.schema != SCHEMA
            or self.courier_observation_version != VERSION
        ):
            _fail("L8_8A_IDENTITY_INVALID")

        object.__setattr__(self, "tenant_id", tenant_id)
        object.__setattr__(self, "case_matter_id", case_matter_id)
        object.__setattr__(self, "matter_fingerprint", matter_fingerprint)
        object.__setattr__(self, "document_id", document_id)
        object.__setattr__(self, "document_fingerprint", document_fingerprint)
        object.__setattr__(self, "observation_id", observation_id)
        object.__setattr__(self, "provider_key", provider_key)
        object.__setattr__(self, "tracking_reference", tracking_reference)
        object.__setattr__(
            self,
            "provider_event_reference",
            provider_event_reference,
        )
        object.__setattr__(self, "provider_status", provider_status)
        object.__setattr__(self, "observed_at", observed_at)
        object.__setattr__(
            self,
            "source_evidence_reference",
            source_reference,
        )
        object.__setattr__(
            self,
            "source_evidence_fingerprint",
            source_fingerprint,
        )

        payload = {
            field: _json_value(getattr(self, field))
            for field in _FIELDS[:-1]
        }
        digest = _digest(payload)
        if self.fingerprint and (
            not isinstance(self.fingerprint, str)
            or not hmac.compare_digest(self.fingerprint, digest)
        ):
            _fail("L8_8A_FINGERPRINT_MISMATCH")
        object.__setattr__(self, "fingerprint", digest)

    def to_dict(self) -> dict[str, object]:
        """Serialize exact immutable observation evidence only."""
        return {
            field: _json_value(getattr(self, field))
            for field in _FIELDS
        }

    @classmethod
    def from_dict(
        cls,
        payload: Mapping[str, object],
    ) -> "LegalCourierObservation":
        """Strictly hydrate persisted observation evidence and reject drift."""
        if not isinstance(payload, Mapping) or set(payload) != set(_FIELDS):
            _fail("L8_8A_SCHEMA_INVALID")
        values = dict(payload)
        stored_fingerprint = values.pop("fingerprint")
        try:
            values["event_kind"] = LegalCourierObservationKind(
                cast(str, values["event_kind"])
            )
            item = cls(**cast(Any, values))
        except LegalCourierObservationError:
            raise
        except Exception as error:
            raise LegalCourierObservationError(
                "L8_8A_PAYLOAD_INVALID"
            ) from error
        if (
            not isinstance(stored_fingerprint, str)
            or not hmac.compare_digest(stored_fingerprint, item.fingerprint)
        ):
            _fail("L8_8A_FINGERPRINT_MISMATCH")
        return item


def create_legal_courier_observation(
    *,
    case_matter: CaseMatter,
    process_document: ProcessDocument,
    observation_id: str,
    provider_key: str,
    tracking_reference: str,
    provider_event_reference: str,
    event_kind: LegalCourierObservationKind,
    provider_status: str,
    observed_at: datetime,
    source_evidence_reference: str,
    source_evidence_fingerprint: str,
) -> LegalCourierObservation:
    """Normalize one external courier event against canonical Legal evidence.

    Tenant, matter and document identities plus source lifecycle fingerprints
    derive exclusively from validated CaseMatter and ProcessDocument values.
    Caller-supplied provider/tracking/status fields are provenance only.

    This factory performs no provider request, persistence, custody mutation,
    ProcessDocument transition, service-attempt transition, service execution,
    return generation, notification delivery, invoice issuance, payment,
    settlement, Court filing, IAM decision or AI inference.
    """
    if type(case_matter) is not CaseMatter:
        _fail("L8_8A_CASE_MATTER_REQUIRED")
    if type(process_document) is not ProcessDocument:
        _fail("L8_8A_PROCESS_DOCUMENT_REQUIRED")
    try:
        case_matter.__post_init__()
        process_document.__post_init__()
    except Exception as error:
        raise LegalCourierObservationError(
            "L8_8A_CANONICAL_SOURCE_INVALID"
        ) from error

    if (
        case_matter.tenant_id != process_document.tenant_id
        or case_matter.case_matter_id != process_document.case_matter_id
    ):
        _fail("L8_8A_SCOPE_CORRELATION_INVALID")

    observed = _when("observed_at", observed_at)
    if (
        observed < case_matter.opened_at.astimezone(timezone.utc)
        or observed < process_document.registered_at.astimezone(timezone.utc)
    ):
        _fail("L8_8A_CHRONOLOGY_INVALID")

    return LegalCourierObservation(
        tenant_id=case_matter.tenant_id,
        case_matter_id=case_matter.case_matter_id,
        matter_fingerprint=case_matter.fingerprint,
        document_id=process_document.document_id,
        document_fingerprint=process_document.fingerprint,
        observation_id=observation_id,
        provider_key=provider_key,
        tracking_reference=tracking_reference,
        provider_event_reference=provider_event_reference,
        event_kind=event_kind,
        provider_status=provider_status,
        observed_at=observed,
        source_evidence_reference=source_evidence_reference,
        source_evidence_fingerprint=source_evidence_fingerprint,
    )


__all__ = [
    "LEGAL_COURIER_OBSERVATION_FIELDS",
    "SCHEMA",
    "VERSION",
    "LegalCourierObservation",
    "LegalCourierObservationError",
    "LegalCourierObservationKind",
    "create_legal_courier_observation",
]


# ARTIFACT: legal_courier_observation.py
# VERSION: v1.0.0-L8-8A-COURIER-OBSERVATION-EVIDENCE
# AUTHORITY BOUNDARY: immutable provider-neutral courier observation evidence only; no lifecycle, service, custody, return, notification, Court, IAM, AI, billing or financial authority
# TENANT POSTURE: exact tenant/matter/document scope derives only from validated CaseMatter and ProcessDocument evidence
# FAIL-CLOSED POSTURE: invalid sources, cross-scope correlation, chronology, provider metadata, schema or fingerprint divergence rejects without coercion or authority expansion
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively
# END OF WILSY OS SOVEREIGN ARTIFACT
