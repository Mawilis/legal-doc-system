"""WILSY OS Legal Evidence provider cleanup classification domain.

TITLE: Legal Evidence Provider Cleanup Classification
VERSION: v1.0.0-L10A2R-C4D3A-PROVIDER-CLEANUP-CLASSIFICATION
AUTHORITY: WILSY OS Core Governance / Python EOS Legal Operations

PURPOSE:
    Classify immutable provider observations against already-certified canonical
    Legal Evidence metadata, commit-uncertainty evidence and C4C reconciliation
    results without granting provider mutation or downstream cleanup authority.

EPITOME:
    PROVIDER OBSERVATION
    + OPTIONAL CANONICAL CONTROL-PLANE EVIDENCE
    -> IMMUTABLE CLASSIFICATION

    INCOMPLETE PROVIDER SESSION
    -> INCOMPLETE_WRITE_SESSION_OBSERVED

    COMPLETED OBJECT + EXACT CANONICAL COMMIT EVIDENCE
    -> CANONICALLY_COMMITTED_OBJECT

    COMPLETED OBJECT + EXACT UNRESOLVED COMMIT EVIDENCE
    -> PROVIDER_OBJECT_UNRESOLVED

    COMPLETED OBJECT + NO SUPPLIED CANONICAL OWNERSHIP/UNCERTAINTY EVIDENCE
    -> CLEANUP_CANDIDATE

    CLEANUP_CANDIDATE
    != ORPHAN PROVEN
    != DELETE AUTHORIZED

AUTHORITY BOUNDARY:
    Pure classification evidence only. No Mongo IO, provider IO, abort,
    deletion, retention/legal-hold decision, availability, IAM, billing,
    payment, settlement, Court or financial execution authority.

COLLABORATION / OWNERSHIP:
    C4D1/C4D2 own provider observation. C2 owns canonical object metadata.
    C4A/C4B own immutable commit uncertainty. C4C owns commit reconciliation.
    Later separately-certified retention, legal-hold and deletion governance
    remains outside this artifact.

SECURITY / PRIVACY POSTURE:
    Exact tenant and provider-object identity binding only. No raw object bytes,
    credentials, secrets or business-authority inference.

FAIL-CLOSED DECLARATION:
    Wrong types, ambiguous evidence combinations, scope divergence, provider
    divergence, object-version divergence, integrity divergence, content-length
    divergence and later-authority claims reject.

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

from tools.eos.legal_operations.domain.legal_evidence_commit_uncertainty import (
    LegalEvidenceCommitUncertainty,
)
from tools.eos.legal_operations.domain.legal_evidence_object_metadata import (
    LegalEvidenceObjectMetadata,
)
from tools.eos.legal_operations.service.legal_evidence_commit_reconciliation_service import (
    LegalEvidenceCommitReconciliationOutcome,
    LegalEvidenceCommitReconciliationResult,
)
from tools.eos.legal_operations.service.legal_evidence_provider_cleanup_discovery_port import (
    LegalEvidenceCompletedObjectObservation,
    LegalEvidenceIncompleteWriteSessionObservation,
)


VERSION: Final[str] = (
    "v1.0.0-L10A2R-C4D3A-PROVIDER-CLEANUP-CLASSIFICATION"
)

_SHA3_RE: Final[re.Pattern[str]] = re.compile(r"^[0-9a-f]{128}$")


class LegalEvidenceProviderCleanupClassification(StrEnum):
    """Closed non-authorizing C4D3A classification vocabulary."""

    INCOMPLETE_WRITE_SESSION_OBSERVED = "INCOMPLETE_WRITE_SESSION_OBSERVED"
    CANONICALLY_COMMITTED_OBJECT = "CANONICALLY_COMMITTED_OBJECT"
    PROVIDER_OBJECT_UNRESOLVED = "PROVIDER_OBJECT_UNRESOLVED"
    CLEANUP_CANDIDATE = "CLEANUP_CANDIDATE"


class LegalEvidenceProviderCleanupClassificationError(ValueError):
    """Stable fail-closed C4D3A classification error."""


def _utc(value: datetime) -> datetime:
    if (
        not isinstance(value, datetime)
        or value.tzinfo is None
        or value.utcoffset() is None
    ):
        raise LegalEvidenceProviderCleanupClassificationError(
            "L10A2R_C4D3A_OBSERVED_AT_INVALID"
        )
    return value.astimezone(timezone.utc)


def _fingerprint(payload: dict[str, object]) -> str:
    encoded = json.dumps(
        payload,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=True,
    ).encode("utf-8")
    return hashlib.sha3_512(encoded).hexdigest()


@dataclass(frozen=True, slots=True)
class LegalEvidenceProviderCleanupClassificationEvidence:
    """Immutable classification evidence; never cleanup execution authority."""

    tenant_id: str
    provider_name: str
    storage_reference: str
    observed_at: datetime
    classification: LegalEvidenceProviderCleanupClassification
    object_version_reference: str | None = None
    provider_integrity_reference: str | None = None
    content_length: int | None = None
    write_session_reference: str | None = None
    initiated_at: datetime | None = None
    last_modified_at: datetime | None = None
    orphan_proven: bool = False
    provider_delete_authorized: bool = False
    abort_authorized: bool = False
    fingerprint: str = ""

    def __post_init__(self) -> None:
        if (
            self.orphan_proven is not False
            or self.provider_delete_authorized is not False
            or self.abort_authorized is not False
        ):
            raise LegalEvidenceProviderCleanupClassificationError(
                "L10A2R_C4D3A_LATER_AUTHORITY_FORBIDDEN"
            )

        observed = _utc(self.observed_at)
        object.__setattr__(self, "observed_at", observed)

        if self.initiated_at is not None:
            object.__setattr__(self, "initiated_at", _utc(self.initiated_at))
        if self.last_modified_at is not None:
            object.__setattr__(
                self,
                "last_modified_at",
                _utc(self.last_modified_at),
            )

        payload: dict[str, object] = {
            "tenant_id": self.tenant_id,
            "provider_name": self.provider_name,
            "storage_reference": self.storage_reference,
            "observed_at": observed.isoformat(),
            "classification": self.classification.value,
            "object_version_reference": self.object_version_reference,
            "provider_integrity_reference": self.provider_integrity_reference,
            "content_length": self.content_length,
            "write_session_reference": self.write_session_reference,
            "initiated_at": (
                self.initiated_at.isoformat()
                if self.initiated_at is not None
                else None
            ),
            "last_modified_at": (
                self.last_modified_at.isoformat()
                if self.last_modified_at is not None
                else None
            ),
            "orphan_proven": False,
            "provider_delete_authorized": False,
            "abort_authorized": False,
            "classification_version": VERSION,
        }
        digest = _fingerprint(payload)

        if self.fingerprint:
            if (
                not isinstance(self.fingerprint, str)
                or _SHA3_RE.fullmatch(self.fingerprint) is None
                or self.fingerprint != digest
            ):
                raise LegalEvidenceProviderCleanupClassificationError(
                    "L10A2R_C4D3A_FINGERPRINT_MISMATCH"
                )

        object.__setattr__(self, "fingerprint", digest)


def _assert_metadata_match(
    observation: LegalEvidenceCompletedObjectObservation,
    metadata: LegalEvidenceObjectMetadata,
) -> None:
    if (
        metadata.tenant_id != observation.tenant_id
        or metadata.provider_name != observation.provider_name
        or metadata.storage_reference != observation.storage_reference
        or metadata.object_version_reference
        != observation.object_version_reference
        or metadata.provider_integrity_reference
        != observation.provider_integrity_reference
        or metadata.content_length != observation.content_length
    ):
        raise LegalEvidenceProviderCleanupClassificationError(
            "L10A2R_C4D3A_METADATA_OBSERVATION_MISMATCH"
        )


def _assert_uncertainty_match(
    observation: LegalEvidenceCompletedObjectObservation,
    uncertainty: LegalEvidenceCommitUncertainty,
) -> None:
    if (
        uncertainty.tenant_id != observation.tenant_id
        or uncertainty.provider_name != observation.provider_name
        or uncertainty.storage_reference != observation.storage_reference
        or uncertainty.object_version_reference
        != observation.object_version_reference
        or uncertainty.provider_integrity_reference
        != observation.provider_integrity_reference
        or uncertainty.content_length != observation.content_length
    ):
        raise LegalEvidenceProviderCleanupClassificationError(
            "L10A2R_C4D3A_UNCERTAINTY_OBSERVATION_MISMATCH"
        )


def _completed_result(
    observation: LegalEvidenceCompletedObjectObservation,
    classification: LegalEvidenceProviderCleanupClassification,
) -> LegalEvidenceProviderCleanupClassificationEvidence:
    return LegalEvidenceProviderCleanupClassificationEvidence(
        tenant_id=observation.tenant_id,
        provider_name=observation.provider_name,
        storage_reference=observation.storage_reference,
        observed_at=observation.observed_at,
        classification=classification,
        object_version_reference=observation.object_version_reference,
        provider_integrity_reference=observation.provider_integrity_reference,
        content_length=observation.content_length,
        last_modified_at=observation.last_modified_at,
    )


def classify_legal_evidence_provider_observation(
    observation: (
        LegalEvidenceIncompleteWriteSessionObservation
        | LegalEvidenceCompletedObjectObservation
    ),
    *,
    metadata: LegalEvidenceObjectMetadata | None = None,
    uncertainty: LegalEvidenceCommitUncertainty | None = None,
    reconciliation: LegalEvidenceCommitReconciliationResult | None = None,
) -> LegalEvidenceProviderCleanupClassificationEvidence:
    """Classify one observation from already-certified immutable evidence."""

    if type(observation) is LegalEvidenceIncompleteWriteSessionObservation:
        if (
            metadata is not None
            or uncertainty is not None
            or reconciliation is not None
        ):
            raise LegalEvidenceProviderCleanupClassificationError(
                "L10A2R_C4D3A_INCOMPLETE_SESSION_EVIDENCE_CONFLICT"
            )

        return LegalEvidenceProviderCleanupClassificationEvidence(
            tenant_id=observation.tenant_id,
            provider_name=observation.provider_name,
            storage_reference=observation.storage_reference,
            observed_at=observation.observed_at,
            classification=(
                LegalEvidenceProviderCleanupClassification
                .INCOMPLETE_WRITE_SESSION_OBSERVED
            ),
            write_session_reference=observation.write_session_reference,
            initiated_at=observation.initiated_at,
        )

    if type(observation) is not LegalEvidenceCompletedObjectObservation:
        raise LegalEvidenceProviderCleanupClassificationError(
            "L10A2R_C4D3A_OBSERVATION_REQUIRED"
        )

    if metadata is not None:
        if type(metadata) is not LegalEvidenceObjectMetadata:
            raise LegalEvidenceProviderCleanupClassificationError(
                "L10A2R_C4D3A_METADATA_INVALID"
            )
        _assert_metadata_match(observation, metadata)

    if uncertainty is not None:
        if type(uncertainty) is not LegalEvidenceCommitUncertainty:
            raise LegalEvidenceProviderCleanupClassificationError(
                "L10A2R_C4D3A_UNCERTAINTY_INVALID"
            )
        _assert_uncertainty_match(observation, uncertainty)

    if reconciliation is not None:
        if type(reconciliation) is not LegalEvidenceCommitReconciliationResult:
            raise LegalEvidenceProviderCleanupClassificationError(
                "L10A2R_C4D3A_RECONCILIATION_INVALID"
            )

        _assert_uncertainty_match(
            observation,
            reconciliation.uncertainty,
        )

        if (
            uncertainty is not None
            and uncertainty != reconciliation.uncertainty
        ):
            raise LegalEvidenceProviderCleanupClassificationError(
                "L10A2R_C4D3A_RECONCILIATION_UNCERTAINTY_CONFLICT"
            )

        if reconciliation.outcome in {
            LegalEvidenceCommitReconciliationOutcome.COMMITTED_CONFIRMED,
            LegalEvidenceCommitReconciliationOutcome.COMMIT_RECOVERED,
        }:
            if reconciliation.metadata is None:
                raise LegalEvidenceProviderCleanupClassificationError(
                    "L10A2R_C4D3A_COMMITTED_METADATA_REQUIRED"
                )

            _assert_metadata_match(
                observation,
                reconciliation.metadata,
            )

            if (
                metadata is not None
                and metadata != reconciliation.metadata
            ):
                raise LegalEvidenceProviderCleanupClassificationError(
                    "L10A2R_C4D3A_COMMITTED_METADATA_CONFLICT"
                )

            return _completed_result(
                observation,
                LegalEvidenceProviderCleanupClassification
                .CANONICALLY_COMMITTED_OBJECT,
            )

        if (
            reconciliation.outcome
            is LegalEvidenceCommitReconciliationOutcome.PROVIDER_OBJECT_UNRESOLVED
        ):
            if metadata is not None:
                raise LegalEvidenceProviderCleanupClassificationError(
                    "L10A2R_C4D3A_UNRESOLVED_METADATA_CONFLICT"
                )

            return _completed_result(
                observation,
                LegalEvidenceProviderCleanupClassification
                .PROVIDER_OBJECT_UNRESOLVED,
            )

        raise LegalEvidenceProviderCleanupClassificationError(
            "L10A2R_C4D3A_RECONCILIATION_OUTCOME_INVALID"
        )

    if metadata is not None:
        return _completed_result(
            observation,
            LegalEvidenceProviderCleanupClassification
            .CANONICALLY_COMMITTED_OBJECT,
        )

    if uncertainty is not None:
        return _completed_result(
            observation,
            LegalEvidenceProviderCleanupClassification
            .PROVIDER_OBJECT_UNRESOLVED,
        )

    return _completed_result(
        observation,
        LegalEvidenceProviderCleanupClassification.CLEANUP_CANDIDATE,
    )


__all__ = [
    "VERSION",
    "LegalEvidenceProviderCleanupClassification",
    "LegalEvidenceProviderCleanupClassificationError",
    "LegalEvidenceProviderCleanupClassificationEvidence",
    "classify_legal_evidence_provider_observation",
]


# ARTIFACT: legal_evidence_provider_cleanup_classification.py
# VERSION: v1.0.0-L10A2R-C4D3A-PROVIDER-CLEANUP-CLASSIFICATION
# AUTHORITY BOUNDARY: immutable provider-observation classification only
# TENANT POSTURE: exact tenant/provider-object evidence binding
# SESSION POSTURE: incomplete observation is not abort authorization
# ORPHAN POSTURE: cleanup candidate and unresolved object are not orphan proof
# DELETION POSTURE: no provider deletion authority
# RETENTION POSTURE: no retention/legal-hold authority
# AVAILABILITY POSTURE: no availability authority
# PROVIDER MUTATION POSTURE: none
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively
# END OF WILSY OS SOVEREIGN ARTIFACT
