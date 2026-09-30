"""WILSY OS immutable Legal Evidence commit-uncertainty evidence.

TITLE: Legal Evidence Commit Uncertainty
VERSION: v1.0.0-L10A2R-C4A-COMMIT-UNCERTAINTY
AUTHORITY: WILSY OS Core Governance / Python EOS Legal Operations

PURPOSE:
    Represent one exact Legal Evidence ingestion for which WILSY has verified
    durable provider-object evidence but does not yet possess caller-observed
    proof that the corresponding C3 Mongo control-plane transaction became
    durable.

EPITOME:
    ACTIVE CAPACITY RESERVATION
    + SEALED WRITE INTENT
    + VERIFIED PROVIDER OBJECT EVIDENCE
    + EXACT WILSY STREAM LENGTH / SHA3-512
    + C3 COMMIT OUTCOME NOT PROVEN
    -> COMMIT UNCERTAINTY EVIDENCE

    COMMIT UNCERTAINTY
    != ORPHAN PROVEN
    != MONGO COMMIT FAILED
    != METADATA ABSENT
    != RESERVATION RELEASED
    != OBJECT DELETION AUTHORIZED
    != AUTHORIZED AVAILABILITY

COLLABORATION / OWNERSHIP:
    L10A2Q-P5A owns immutable capacity-reservation evidence.
    L10A2R-A owns provider-neutral binary-write intent/object evidence.
    L10A2R-C3 owns exact two-plane commit composition.
    C4B will own durable uncertainty persistence.
    Later C4 reconciliation artifacts will determine actual control-plane state.
    Retention/legal-hold/deletion authority remains separately certified.

SECURITY / TENANT POSTURE:
    The reservation, write intent and provider object must bind to exactly one
    tenant/document/ingestion intent. Cross-scope evidence rejects before any
    uncertainty value is created.

AUTHORITY BOUNDARY:
    Pure immutable uncertainty evidence only. This artifact performs no Mongo
    read/write, provider IO, capacity mutation, reservation transition, usage
    mutation, reconciliation, deletion, retention/legal-hold decision,
    availability publication, IAM, billing, payment, execution or settlement.

FAIL-CLOSED DECLARATION:
    Wrong types, malformed identities, invalid SHA3-512 evidence, reservation
    scope or dimensions, write-intent scope, provider-object binding, observed
    stream divergence, impossible timestamps, schema drift and fingerprint
    corruption reject.

CERTIFICATION / UPDATE DATE: 2026-09-30
"""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from datetime import datetime, timezone
import hashlib
import hmac
import json
import re
from typing import Any, Final, cast

from tools.eos.legal_operations.domain.legal_evidence_capacity_reservation import (
    LegalEvidenceCapacityReservation,
    LegalEvidenceCapacityReservationStatus,
)
from tools.eos.legal_operations.service.legal_evidence_binary_storage_port import (
    LegalEvidenceBinaryObjectEvidence,
    LegalEvidenceBinaryStoragePortError,
    LegalEvidenceBinaryWriteIntent,
    validate_object_evidence_for_intent,
)


VERSION: Final[str] = (
    "v1.0.0-L10A2R-C4A-COMMIT-UNCERTAINTY"
)

SCHEMA: Final[str] = (
    "WILSY-LEGAL-EVIDENCE-COMMIT-UNCERTAINTY/V1"
)

_UNCERTAINTY_PREFIX: Final[str] = (
    "legal-evidence-commit-uncertainty:"
)

_IDENTITY_RE: Final[re.Pattern[str]] = re.compile(
    r"^[A-Za-z0-9][A-Za-z0-9._:@/-]{0,511}$"
)

_SHA3_RE: Final[re.Pattern[str]] = re.compile(
    r"^[0-9a-f]{128}$"
)

_FORBIDDEN_TENANTS: Final[frozenset[str]] = frozenset(
    {
        "default",
        "global",
        "global_root",
        "root",
        "master",
        "*",
    }
)

_FIELDS: Final[tuple[str, ...]] = (
    "uncertainty_id",
    "tenant_id",
    "case_matter_id",
    "document_id",
    "ingestion_intent_id",
    "reservation_id",
    "provider_name",
    "storage_reference",
    "object_version_reference",
    "provider_integrity_reference",
    "write_intent_fingerprint",
    "content_length",
    "content_fingerprint",
    "source_evidence_reference",
    "source_evidence_fingerprint",
    "detected_at",
    "schema",
    "uncertainty_version",
    "fingerprint",
)


class LegalEvidenceCommitUncertaintyError(ValueError):
    """Raised when immutable commit-uncertainty evidence is invalid."""


def _identity(
    name: str,
    value: object,
) -> str:
    if (
        not isinstance(value, str)
        or value != value.strip()
        or _IDENTITY_RE.fullmatch(value) is None
    ):
        raise LegalEvidenceCommitUncertaintyError(
            f"L10A2R_C4A_{name.upper()}_INVALID"
        )

    return value


def _tenant(
    value: object,
) -> str:
    tenant = _identity(
        "tenant_id",
        value,
    )

    if tenant.casefold() in _FORBIDDEN_TENANTS:
        raise LegalEvidenceCommitUncertaintyError(
            "L10A2R_C4A_TENANT_REQUIRED"
        )

    return tenant


def _text(
    name: str,
    value: object,
    *,
    limit: int = 2048,
) -> str:
    if (
        not isinstance(value, str)
        or not value
        or value != value.strip()
        or len(value) > limit
        or any(
            ord(character) < 32
            for character in value
        )
    ):
        raise LegalEvidenceCommitUncertaintyError(
            f"L10A2R_C4A_{name.upper()}_INVALID"
        )

    return value


def _sha3(
    name: str,
    value: object,
) -> str:
    if (
        not isinstance(value, str)
        or _SHA3_RE.fullmatch(value) is None
    ):
        raise LegalEvidenceCommitUncertaintyError(
            f"L10A2R_C4A_{name.upper()}_INVALID"
        )

    return value


def _positive_int(
    name: str,
    value: object,
) -> int:
    if (
        isinstance(value, bool)
        or not isinstance(value, int)
        or value <= 0
    ):
        raise LegalEvidenceCommitUncertaintyError(
            f"L10A2R_C4A_{name.upper()}_INVALID"
        )

    return value


def _utc(
    name: str,
    value: object,
) -> datetime:
    if isinstance(value, str):
        try:
            value = datetime.fromisoformat(
                value.replace(
                    "Z",
                    "+00:00",
                )
            )
        except ValueError as error:
            raise LegalEvidenceCommitUncertaintyError(
                f"L10A2R_C4A_{name.upper()}_INVALID"
            ) from error

    if (
        not isinstance(value, datetime)
        or value.tzinfo is None
        or value.utcoffset() is None
    ):
        raise LegalEvidenceCommitUncertaintyError(
            f"L10A2R_C4A_{name.upper()}_INVALID"
        )

    return value.astimezone(
        timezone.utc
    )


def _timestamp_text(
    value: datetime,
) -> str:
    return (
        value.astimezone(timezone.utc)
        .isoformat()
        .replace(
            "+00:00",
            "Z",
        )
    )


def _serialize_value(
    value: object,
) -> object:
    if isinstance(
        value,
        datetime,
    ):
        return _timestamp_text(
            value
        )

    return value


def _uncertainty_identity(
    *,
    tenant_id: str,
    case_matter_id: str,
    document_id: str,
    ingestion_intent_id: str,
    reservation_id: str,
    provider_name: str,
    storage_reference: str,
    object_version_reference: str,
    write_intent_fingerprint: str,
    content_length: int,
    content_fingerprint: str,
) -> str:
    payload = {
        "tenant_id": tenant_id,
        "case_matter_id": case_matter_id,
        "document_id": document_id,
        "ingestion_intent_id": ingestion_intent_id,
        "reservation_id": reservation_id,
        "provider_name": provider_name,
        "storage_reference": storage_reference,
        "object_version_reference": object_version_reference,
        "write_intent_fingerprint": write_intent_fingerprint,
        "content_length": content_length,
        "content_fingerprint": content_fingerprint,
    }

    raw = json.dumps(
        payload,
        ensure_ascii=False,
        allow_nan=False,
        sort_keys=True,
        separators=(
            ",",
            ":",
        ),
    ).encode(
        "utf-8"
    )

    return (
        _UNCERTAINTY_PREFIX
        + hashlib.sha3_512(
            raw
        ).hexdigest()
    )


@dataclass(
    frozen=True,
    slots=True,
)
class LegalEvidenceCommitUncertainty:
    """Immutable evidence that one C3 durable outcome remains unproven."""

    uncertainty_id: str

    tenant_id: str
    case_matter_id: str
    document_id: str
    ingestion_intent_id: str
    reservation_id: str

    provider_name: str
    storage_reference: str
    object_version_reference: str
    provider_integrity_reference: str
    write_intent_fingerprint: str

    content_length: int
    content_fingerprint: str

    source_evidence_reference: str
    source_evidence_fingerprint: str

    detected_at: datetime

    schema: str = SCHEMA
    uncertainty_version: str = VERSION
    fingerprint: str = ""

    def __post_init__(
        self,
    ) -> None:
        tenant = _tenant(
            self.tenant_id
        )
        matter = _identity(
            "case_matter_id",
            self.case_matter_id,
        )
        document = _identity(
            "document_id",
            self.document_id,
        )
        ingestion = _identity(
            "ingestion_intent_id",
            self.ingestion_intent_id,
        )
        reservation = _identity(
            "reservation_id",
            self.reservation_id,
        )

        provider = _identity(
            "provider_name",
            self.provider_name,
        )
        storage = _text(
            "storage_reference",
            self.storage_reference,
        )
        object_version = _text(
            "object_version_reference",
            self.object_version_reference,
        )
        provider_integrity = _text(
            "provider_integrity_reference",
            self.provider_integrity_reference,
        )
        intent_fingerprint = _sha3(
            "write_intent_fingerprint",
            self.write_intent_fingerprint,
        )

        length = _positive_int(
            "content_length",
            self.content_length,
        )
        content_fingerprint = _sha3(
            "content_fingerprint",
            self.content_fingerprint,
        )

        source_reference = _identity(
            "source_evidence_reference",
            self.source_evidence_reference,
        )
        source_fingerprint = _sha3(
            "source_evidence_fingerprint",
            self.source_evidence_fingerprint,
        )

        detected = _utc(
            "detected_at",
            self.detected_at,
        )

        if (
            self.schema != SCHEMA
            or self.uncertainty_version != VERSION
        ):
            raise LegalEvidenceCommitUncertaintyError(
                "L10A2R_C4A_SCHEMA_INVALID"
            )

        expected_id = _uncertainty_identity(
            tenant_id=tenant,
            case_matter_id=matter,
            document_id=document,
            ingestion_intent_id=ingestion,
            reservation_id=reservation,
            provider_name=provider,
            storage_reference=storage,
            object_version_reference=object_version,
            write_intent_fingerprint=intent_fingerprint,
            content_length=length,
            content_fingerprint=content_fingerprint,
        )

        if (
            not isinstance(
                self.uncertainty_id,
                str,
            )
            or not hmac.compare_digest(
                self.uncertainty_id,
                expected_id,
            )
        ):
            raise LegalEvidenceCommitUncertaintyError(
                "L10A2R_C4A_UNCERTAINTY_ID_MISMATCH"
            )

        object.__setattr__(
            self,
            "tenant_id",
            tenant,
        )
        object.__setattr__(
            self,
            "case_matter_id",
            matter,
        )
        object.__setattr__(
            self,
            "document_id",
            document,
        )
        object.__setattr__(
            self,
            "ingestion_intent_id",
            ingestion,
        )
        object.__setattr__(
            self,
            "reservation_id",
            reservation,
        )
        object.__setattr__(
            self,
            "provider_name",
            provider,
        )
        object.__setattr__(
            self,
            "storage_reference",
            storage,
        )
        object.__setattr__(
            self,
            "object_version_reference",
            object_version,
        )
        object.__setattr__(
            self,
            "provider_integrity_reference",
            provider_integrity,
        )
        object.__setattr__(
            self,
            "write_intent_fingerprint",
            intent_fingerprint,
        )
        object.__setattr__(
            self,
            "content_length",
            length,
        )
        object.__setattr__(
            self,
            "content_fingerprint",
            content_fingerprint,
        )
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
        object.__setattr__(
            self,
            "detected_at",
            detected,
        )

        payload = {
            field: _serialize_value(
                getattr(
                    self,
                    field,
                )
            )
            for field in _FIELDS[:-1]
        }

        digest = hashlib.sha3_512(
            json.dumps(
                payload,
                ensure_ascii=False,
                allow_nan=False,
                sort_keys=False,
                separators=(
                    ",",
                    ":",
                ),
            ).encode(
                "utf-8"
            )
        ).hexdigest()

        if self.fingerprint:
            if (
                not isinstance(
                    self.fingerprint,
                    str,
                )
                or not hmac.compare_digest(
                    self.fingerprint,
                    digest,
                )
            ):
                raise LegalEvidenceCommitUncertaintyError(
                    "L10A2R_C4A_FINGERPRINT_MISMATCH"
                )

        object.__setattr__(
            self,
            "fingerprint",
            digest,
        )

    def to_dict(
        self,
    ) -> dict[str, object]:
        """Serialize exact immutable commit-uncertainty evidence."""
        return {
            field: _serialize_value(
                getattr(
                    self,
                    field,
                )
            )
            for field in _FIELDS
        }

    @classmethod
    def from_dict(
        cls,
        payload: Mapping[str, object],
    ) -> "LegalEvidenceCommitUncertainty":
        """Strictly hydrate exact immutable uncertainty evidence."""
        if (
            not isinstance(
                payload,
                Mapping,
            )
            or set(payload) != set(_FIELDS)
        ):
            raise LegalEvidenceCommitUncertaintyError(
                "L10A2R_C4A_SCHEMA_INVALID"
            )

        values = dict(
            payload
        )

        stored_fingerprint = values.pop(
            "fingerprint"
        )

        values["detected_at"] = _utc(
            "detected_at",
            values["detected_at"],
        )

        item = cls(
            **cast(
                Any,
                values,
            )
        )

        if (
            not isinstance(
                stored_fingerprint,
                str,
            )
            or not hmac.compare_digest(
                stored_fingerprint,
                item.fingerprint,
            )
        ):
            raise LegalEvidenceCommitUncertaintyError(
                "L10A2R_C4A_FINGERPRINT_MISMATCH"
            )

        return item


def open_legal_evidence_commit_uncertainty(
    *,
    reservation: LegalEvidenceCapacityReservation,
    intent: LegalEvidenceBinaryWriteIntent,
    object_evidence: LegalEvidenceBinaryObjectEvidence,
    observed_content_length: int,
    observed_content_fingerprint: str,
    source_evidence_reference: str,
    source_evidence_fingerprint: str,
    detected_at: datetime,
) -> LegalEvidenceCommitUncertainty:
    """Create uncertainty only from one exact verified provider completion.

    This function intentionally does not decide whether C3 committed. It records
    the exact evidence needed by later reconciliation to determine that fact.
    """
    if type(reservation) is not LegalEvidenceCapacityReservation:
        raise LegalEvidenceCommitUncertaintyError(
            "L10A2R_C4A_RESERVATION_REQUIRED"
        )

    if type(intent) is not LegalEvidenceBinaryWriteIntent:
        raise LegalEvidenceCommitUncertaintyError(
            "L10A2R_C4A_WRITE_INTENT_REQUIRED"
        )

    if type(object_evidence) is not LegalEvidenceBinaryObjectEvidence:
        raise LegalEvidenceCommitUncertaintyError(
            "L10A2R_C4A_OBJECT_EVIDENCE_REQUIRED"
        )

    if (
        reservation.status
        is not LegalEvidenceCapacityReservationStatus.ACTIVE
    ):
        raise LegalEvidenceCommitUncertaintyError(
            "L10A2R_C4A_ACTIVE_RESERVATION_REQUIRED"
        )

    length = _positive_int(
        "observed_content_length",
        observed_content_length,
    )
    fingerprint = _sha3(
        "observed_content_fingerprint",
        observed_content_fingerprint,
    )
    source_reference = _identity(
        "source_evidence_reference",
        source_evidence_reference,
    )
    source_fingerprint = _sha3(
        "source_evidence_fingerprint",
        source_evidence_fingerprint,
    )
    observed_at = _utc(
        "detected_at",
        detected_at,
    )

    if (
        reservation.tenant_id != intent.tenant_id
        or reservation.document_id != intent.document_id
        or reservation.ingestion_intent_id
        != intent.ingestion_reference
    ):
        raise LegalEvidenceCommitUncertaintyError(
            "L10A2R_C4A_RESERVATION_SCOPE_MISMATCH"
        )

    if (
        reservation.reserved_storage_bytes != length
        or reservation.reserved_ingress_bytes != length
        or reservation.reserved_document_versions != 1
    ):
        raise LegalEvidenceCommitUncertaintyError(
            "L10A2R_C4A_RESERVATION_DIMENSION_MISMATCH"
        )

    if length > intent.admitted_max_content_length:
        raise LegalEvidenceCommitUncertaintyError(
            "L10A2R_C4A_INTENT_CONTENT_LIMIT_EXCEEDED"
        )

    if observed_at < reservation.reserved_at:
        raise LegalEvidenceCommitUncertaintyError(
            "L10A2R_C4A_DETECTED_AT_INVALID"
        )

    try:
        validate_object_evidence_for_intent(
            intent=intent,
            evidence=object_evidence,
        )
    except LegalEvidenceBinaryStoragePortError as error:
        raise LegalEvidenceCommitUncertaintyError(
            "L10A2R_C4A_OBJECT_SCOPE_MISMATCH"
        ) from error

    if not object_evidence.proves_stream(
        observed_length=length,
        observed_fingerprint=fingerprint,
    ):
        raise LegalEvidenceCommitUncertaintyError(
            "L10A2R_C4A_OBJECT_CONTENT_MISMATCH"
        )

    uncertainty_id = _uncertainty_identity(
        tenant_id=intent.tenant_id,
        case_matter_id=intent.case_matter_id,
        document_id=intent.document_id,
        ingestion_intent_id=intent.ingestion_reference,
        reservation_id=reservation.reservation_id,
        provider_name=object_evidence.provider_name,
        storage_reference=object_evidence.storage_reference,
        object_version_reference=object_evidence.object_version_reference,
        write_intent_fingerprint=object_evidence.write_intent_fingerprint,
        content_length=length,
        content_fingerprint=fingerprint,
    )

    return LegalEvidenceCommitUncertainty(
        uncertainty_id=uncertainty_id,
        tenant_id=intent.tenant_id,
        case_matter_id=intent.case_matter_id,
        document_id=intent.document_id,
        ingestion_intent_id=intent.ingestion_reference,
        reservation_id=reservation.reservation_id,
        provider_name=object_evidence.provider_name,
        storage_reference=object_evidence.storage_reference,
        object_version_reference=object_evidence.object_version_reference,
        provider_integrity_reference=(
            object_evidence.provider_integrity_reference
        ),
        write_intent_fingerprint=(
            object_evidence.write_intent_fingerprint
        ),
        content_length=length,
        content_fingerprint=fingerprint,
        source_evidence_reference=source_reference,
        source_evidence_fingerprint=source_fingerprint,
        detected_at=observed_at,
    )


__all__ = [
    "SCHEMA",
    "VERSION",
    "LegalEvidenceCommitUncertainty",
    "LegalEvidenceCommitUncertaintyError",
    "open_legal_evidence_commit_uncertainty",
]


# ARTIFACT: legal_evidence_commit_uncertainty.py
# VERSION: v1.0.0-L10A2R-C4A-COMMIT-UNCERTAINTY
# AUTHORITY BOUNDARY: immutable commit-outcome uncertainty evidence only
# TENANT POSTURE: exact reservation/write-intent/provider-object scope
# PROVIDER POSTURE: verified completion evidence accepted; no provider execution
# MONGO POSTURE: no Mongo IO and no durable commit outcome claimed
# ORPHAN POSTURE: uncertainty is not proof of orphan status
# RECONCILIATION POSTURE: later C4 artifacts determine actual durable state
# DELETION POSTURE: no retention/legal-hold/deletion authority
# AVAILABILITY POSTURE: no availability authority
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively
# END OF WILSY OS SOVEREIGN ARTIFACT
