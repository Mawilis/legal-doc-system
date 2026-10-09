"""WILSY OS Legal Evidence provider/write-intent correlation domain.

TITLE: Legal Evidence Provider Write-Intent Correlation
VERSION: v1.0.0-L10A2R-C4D5D2-PROVIDER-WRITE-INTENT-CORRELATION
AUTHORITY: WILSY OS Core Governance / Python EOS Legal Operations

PURPOSE:
    Express immutable evidence about whether certified provider-side original
    write-intent metadata was observed and, when PRESENT, whether later
    orchestration found an exact durable C4D5C original-intent registration.

EPITOME:
    PROVIDER COMPLETED-OBJECT OBSERVATION
    + OPTIONAL ALREADY-READ DURABLE ORIGINAL WRITE INTENT
    -> IMMUTABLE NON-AUTHORIZING CORRELATION EVIDENCE

    NOT_OBSERVED
    -> METADATA_NOT_OBSERVED

    ABSENT
    -> METADATA_ABSENT

    PRESENT + EXACT TENANT/FINGERPRINT DURABLE REGISTRATION
    -> PRESENT_REGISTRY_MATCH

    PRESENT + COMPLETED REGISTRY LOOKUP + NO REGISTRATION
    -> PRESENT_REGISTRY_NOT_FOUND

    ALL OUTCOMES
    != CANONICAL COMMIT PROOF
    != ORPHAN PROOF
    != DELETE AUTHORITY

AUTHORITY BOUNDARY:
    Pure correlation evidence only. No Mongo IO, provider IO, reconciliation,
    orphan proof, deletion, abort, retention/legal-hold decision, availability,
    IAM, billing, payment, settlement, Court or financial execution authority.

COLLABORATION / OWNERSHIP:
    C4D2R1/C4D2R2 own provider-side write-intent metadata observation.
    C4D5C owns durable original write-intent registration.
    C4D5D2 only validates already-supplied immutable evidence.
    Later service orchestration owns registry lookup and translation.
    Orphan proof and deletion governance remain separately certified domains.

SECURITY / PRIVACY POSTURE:
    Exact tenant and SHA3-512 intent-fingerprint binding only. No provider
    credentials, raw evidence bytes or business-authority inference.

FAIL-CLOSED DECLARATION:
    PRESENT metadata requires proof that registry lookup was performed.
    A supplied durable intent must match the exact observation tenant and exact
    provider write-intent fingerprint. Malformed registration evidence,
    impossible evidence combinations and authority escalation reject.

CERTIFICATION / UPDATE DATE: 2026-09-30
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from enum import StrEnum
import hashlib
import json
import re
from typing import Final

from tools.eos.legal_operations.service.legal_evidence_binary_storage_port import (
    LegalEvidenceBinaryWriteIntent,
)
from tools.eos.legal_operations.service.legal_evidence_provider_cleanup_discovery_port import (
    LegalEvidenceCompletedObjectIntentMetadataState,
    LegalEvidenceCompletedObjectObservation,
)


VERSION: Final[str] = (
    "v1.0.0-L10A2R-C4D5D2-PROVIDER-WRITE-INTENT-CORRELATION"
)

_SHA3_RE: Final[re.Pattern[str]] = re.compile(
    r"^[0-9a-f]{128}$"
)


class LegalEvidenceProviderWriteIntentCorrelationState(StrEnum):
    """Closed, non-authorizing correlation vocabulary."""

    METADATA_NOT_OBSERVED = "METADATA_NOT_OBSERVED"
    METADATA_ABSENT = "METADATA_ABSENT"
    PRESENT_REGISTRY_MATCH = "PRESENT_REGISTRY_MATCH"
    PRESENT_REGISTRY_NOT_FOUND = "PRESENT_REGISTRY_NOT_FOUND"


class LegalEvidenceProviderWriteIntentCorrelationError(
    ValueError
):
    """Stable fail-closed pure-correlation error."""


def _utc(
    name: str,
    value: datetime,
) -> datetime:
    if (
        not isinstance(value, datetime)
        or value.tzinfo is None
        or value.utcoffset() is None
    ):
        raise LegalEvidenceProviderWriteIntentCorrelationError(
            f"L10A2R_C4D5D2_{name.upper()}_INVALID"
        )

    return value.astimezone(
        timezone.utc
    )


def _sha3(
    name: str,
    value: str,
) -> str:
    if (
        not isinstance(value, str)
        or _SHA3_RE.fullmatch(value) is None
    ):
        raise LegalEvidenceProviderWriteIntentCorrelationError(
            f"L10A2R_C4D5D2_{name.upper()}_INVALID"
        )

    return value


def _fingerprint(
    payload: dict[str, object],
) -> str:
    encoded = json.dumps(
        payload,
        ensure_ascii=True,
        allow_nan=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode(
        "utf-8"
    )

    return hashlib.sha3_512(
        encoded
    ).hexdigest()


@dataclass(
    frozen=True,
    slots=True,
)
class LegalEvidenceProviderWriteIntentCorrelationEvidence:
    """Immutable correlation evidence without cleanup/deletion authority."""

    tenant_id: str
    provider_name: str
    storage_reference: str
    object_version_reference: str
    observed_at: datetime
    metadata_state: LegalEvidenceCompletedObjectIntentMetadataState
    correlation_state: LegalEvidenceProviderWriteIntentCorrelationState
    provider_write_intent_fingerprint: str | None = None
    registered_intent_fingerprint: str | None = None
    registration_record_fingerprint: str | None = None
    registered_at: datetime | None = None
    orphan_proven: bool = False
    provider_delete_authorized: bool = False
    fingerprint: str = ""

    def __post_init__(
        self,
    ) -> None:
        if (
            self.orphan_proven is not False
            or self.provider_delete_authorized is not False
        ):
            raise LegalEvidenceProviderWriteIntentCorrelationError(
                "L10A2R_C4D5D2_LATER_AUTHORITY_FORBIDDEN"
            )

        if (
            not isinstance(self.tenant_id, str)
            or not self.tenant_id
            or not isinstance(self.provider_name, str)
            or not self.provider_name
            or not isinstance(self.storage_reference, str)
            or not self.storage_reference
            or not isinstance(self.object_version_reference, str)
            or not self.object_version_reference
        ):
            raise LegalEvidenceProviderWriteIntentCorrelationError(
                "L10A2R_C4D5D2_IDENTITY_INVALID"
            )

        if (
            type(self.metadata_state)
            is not LegalEvidenceCompletedObjectIntentMetadataState
            or type(self.correlation_state)
            is not LegalEvidenceProviderWriteIntentCorrelationState
        ):
            raise LegalEvidenceProviderWriteIntentCorrelationError(
                "L10A2R_C4D5D2_STATE_INVALID"
            )

        observed = _utc(
            "observed_at",
            self.observed_at,
        )
        object.__setattr__(
            self,
            "observed_at",
            observed,
        )

        registered = None

        if self.registered_at is not None:
            registered = _utc(
                "registered_at",
                self.registered_at,
            )
            object.__setattr__(
                self,
                "registered_at",
                registered,
            )

        for name in (
            "provider_write_intent_fingerprint",
            "registered_intent_fingerprint",
            "registration_record_fingerprint",
        ):
            value = getattr(
                self,
                name,
            )
            if value is not None:
                _sha3(
                    name,
                    value,
                )

        payload: dict[str, object] = {
            "tenant_id":
                self.tenant_id,
            "provider_name":
                self.provider_name,
            "storage_reference":
                self.storage_reference,
            "object_version_reference":
                self.object_version_reference,
            "observed_at":
                observed.isoformat(),
            "metadata_state":
                self.metadata_state.value,
            "correlation_state":
                self.correlation_state.value,
            "provider_write_intent_fingerprint":
                self.provider_write_intent_fingerprint,
            "registered_intent_fingerprint":
                self.registered_intent_fingerprint,
            "registration_record_fingerprint":
                self.registration_record_fingerprint,
            "registered_at":
                (
                    registered.isoformat()
                    if registered is not None
                    else None
                ),
            "orphan_proven":
                False,
            "provider_delete_authorized":
                False,
            "correlation_version":
                VERSION,
        }

        digest = _fingerprint(
            payload
        )

        if self.fingerprint:
            if (
                not isinstance(
                    self.fingerprint,
                    str,
                )
                or not _SHA3_RE.fullmatch(
                    self.fingerprint
                )
                or self.fingerprint != digest
            ):
                raise LegalEvidenceProviderWriteIntentCorrelationError(
                    "L10A2R_C4D5D2_FINGERPRINT_MISMATCH"
                )

        object.__setattr__(
            self,
            "fingerprint",
            digest,
        )


def correlate_legal_evidence_provider_write_intent(
    *,
    observation: LegalEvidenceCompletedObjectObservation,
    registry_lookup_performed: bool,
    registered_intent: LegalEvidenceBinaryWriteIntent | None = None,
    registration_record_fingerprint: str | None = None,
    registered_at: datetime | None = None,
) -> LegalEvidenceProviderWriteIntentCorrelationEvidence:
    """Correlate already-observed provider metadata with already-read intent."""

    if type(observation) is not LegalEvidenceCompletedObjectObservation:
        raise LegalEvidenceProviderWriteIntentCorrelationError(
            "L10A2R_C4D5D2_COMPLETED_OBSERVATION_REQUIRED"
        )

    if type(registry_lookup_performed) is not bool:
        raise LegalEvidenceProviderWriteIntentCorrelationError(
            "L10A2R_C4D5D2_REGISTRY_LOOKUP_MARKER_INVALID"
        )

    metadata_state = (
        observation.write_intent_metadata_state
    )
    provider_fingerprint = (
        observation.write_intent_fingerprint
    )

    if metadata_state in {
        LegalEvidenceCompletedObjectIntentMetadataState.NOT_OBSERVED,
        LegalEvidenceCompletedObjectIntentMetadataState.ABSENT,
    }:
        if (
            registry_lookup_performed
            or registered_intent is not None
            or registration_record_fingerprint is not None
            or registered_at is not None
        ):
            raise LegalEvidenceProviderWriteIntentCorrelationError(
                "L10A2R_C4D5D2_NON_PRESENT_REGISTRY_EVIDENCE_FORBIDDEN"
            )

        state = (
            LegalEvidenceProviderWriteIntentCorrelationState
            .METADATA_NOT_OBSERVED
            if metadata_state
            is LegalEvidenceCompletedObjectIntentMetadataState.NOT_OBSERVED
            else
            LegalEvidenceProviderWriteIntentCorrelationState
            .METADATA_ABSENT
        )

        return LegalEvidenceProviderWriteIntentCorrelationEvidence(
            tenant_id=observation.tenant_id,
            provider_name=observation.provider_name,
            storage_reference=observation.storage_reference,
            object_version_reference=(
                observation.object_version_reference
            ),
            observed_at=observation.observed_at,
            metadata_state=metadata_state,
            correlation_state=state,
        )

    if (
        metadata_state
        is not LegalEvidenceCompletedObjectIntentMetadataState.PRESENT
    ):
        raise LegalEvidenceProviderWriteIntentCorrelationError(
            "L10A2R_C4D5D2_METADATA_STATE_INVALID"
        )

    if (
        provider_fingerprint is None
        or not registry_lookup_performed
    ):
        raise LegalEvidenceProviderWriteIntentCorrelationError(
            "L10A2R_C4D5D2_PRESENT_REQUIRES_REGISTRY_LOOKUP"
        )

    if registered_intent is None:
        if (
            registration_record_fingerprint is not None
            or registered_at is not None
        ):
            raise LegalEvidenceProviderWriteIntentCorrelationError(
                "L10A2R_C4D5D2_NOT_FOUND_REGISTRATION_EVIDENCE_FORBIDDEN"
            )

        return LegalEvidenceProviderWriteIntentCorrelationEvidence(
            tenant_id=observation.tenant_id,
            provider_name=observation.provider_name,
            storage_reference=observation.storage_reference,
            object_version_reference=(
                observation.object_version_reference
            ),
            observed_at=observation.observed_at,
            metadata_state=metadata_state,
            correlation_state=(
                LegalEvidenceProviderWriteIntentCorrelationState
                .PRESENT_REGISTRY_NOT_FOUND
            ),
            provider_write_intent_fingerprint=(
                provider_fingerprint
            ),
        )

    if type(registered_intent) is not LegalEvidenceBinaryWriteIntent:
        raise LegalEvidenceProviderWriteIntentCorrelationError(
            "L10A2R_C4D5D2_REGISTERED_INTENT_INVALID"
        )

    if (
        registered_intent.tenant_id
        != observation.tenant_id
        or registered_intent.fingerprint
        != provider_fingerprint
    ):
        raise LegalEvidenceProviderWriteIntentCorrelationError(
            "L10A2R_C4D5D2_REGISTERED_INTENT_MISMATCH"
        )

    if (
        registration_record_fingerprint is None
        or registered_at is None
    ):
        raise LegalEvidenceProviderWriteIntentCorrelationError(
            "L10A2R_C4D5D2_MATCH_REGISTRATION_EVIDENCE_REQUIRED"
        )

    record_fingerprint = _sha3(
        "registration_record_fingerprint",
        registration_record_fingerprint,
    )
    registration_time = _utc(
        "registered_at",
        registered_at,
    )

    return LegalEvidenceProviderWriteIntentCorrelationEvidence(
        tenant_id=observation.tenant_id,
        provider_name=observation.provider_name,
        storage_reference=observation.storage_reference,
        object_version_reference=(
            observation.object_version_reference
        ),
        observed_at=observation.observed_at,
        metadata_state=metadata_state,
        correlation_state=(
            LegalEvidenceProviderWriteIntentCorrelationState
            .PRESENT_REGISTRY_MATCH
        ),
        provider_write_intent_fingerprint=provider_fingerprint,
        registered_intent_fingerprint=(
            registered_intent.fingerprint
        ),
        registration_record_fingerprint=record_fingerprint,
        registered_at=registration_time,
    )


__all__ = [
    "VERSION",
    "LegalEvidenceProviderWriteIntentCorrelationError",
    "LegalEvidenceProviderWriteIntentCorrelationEvidence",
    "LegalEvidenceProviderWriteIntentCorrelationState",
    "correlate_legal_evidence_provider_write_intent",
]


# ARTIFACT: legal_evidence_provider_write_intent_correlation.py
# VERSION: v1.0.0-L10A2R-C4D5D2-PROVIDER-WRITE-INTENT-CORRELATION
# AUTHORITY BOUNDARY: immutable provider/original-intent correlation evidence only
# TENANT POSTURE: exact tenant plus exact write-intent fingerprint binding
# REGISTRY POSTURE: consumes already-read evidence only; performs no registry IO
# COVERAGE POSTURE: registry not-found is unresolved coverage evidence, not orphan proof
# ORPHAN POSTURE: all correlation states have orphan_proven=False
# DELETION POSTURE: all correlation states have provider_delete_authorized=False
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively
# END OF WILSY OS SOVEREIGN ARTIFACT
