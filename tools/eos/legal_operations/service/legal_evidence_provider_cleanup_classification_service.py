"""WILSY OS Legal Evidence provider cleanup classification orchestration.

TITLE: Legal Evidence Provider Cleanup Classification Service
VERSION: v1.1.0-L10A2R-C4D5D3-PROVIDER-WRITE-INTENT-CORRELATION-SERVICE
AUTHORITY: WILSY OS Core Governance / Python EOS Legal Operations

PURPOSE:
    Compose certified provider discovery with canonical C2 metadata and durable
    C4B uncertainty evidence, then delegate pure classification to C4D3A.
    Separately correlate PRESENT provider write-intent metadata with durable
    C4D5C registration and delegate immutable evidence construction to C4D5D2.

EPITOME:
    C4D1/C4D2 PROVIDER DISCOVERY
    + C2 EXACT PROVIDER-OBJECT METADATA LOOKUP
    + C4B DURABLE TENANT UNCERTAINTY EVIDENCE
    -> C4D3A PURE CLASSIFICATION

    NO C2 METADATA + NO C4B UNCERTAINTY
    -> PROVIDER_OBJECT_UNRESOLVED

    PRESENT PROVIDER WRITE-INTENT METADATA
    + C4D5C EXACT TENANT/FINGERPRINT LOOKUP
    -> C4D5D2 IMMUTABLE CORRELATION EVIDENCE

    NOT_OBSERVED / ABSENT
    -> ZERO C4D5C LOOKUPS

    CORRELATION MATCH OR NOT-FOUND
    != CANONICAL COMMIT PROOF
    != ORPHAN PROVEN
    != DELETE AUTHORIZED

IMPORTANT BOUNDARY:
    This service DOES NOT invoke C4C reconciliation. C4C requires the exact
    original LegalEvidenceBinaryWriteIntent. C4D5D3 may read the already-
    certified C4D5C durable registration only for exact PRESENT provider
    fingerprints and must pass that record to C4D5D2 without reconstruction.

TRANSACTION:
    Caller supplies one already-active Mongo transaction. C4D3B validates it
    before provider discovery or control-plane reads. C4D3B never starts,
    commits, aborts or retries transaction lifecycle.

PROVIDER:
    Provider interaction is discovery-only through the certified C4D1 port.
    No provider mutation command exists.

AUTHORITY BOUNDARY:
    Observation classification orchestration only. No abort, deletion, orphan
    proof, retention/legal-hold decision, availability, IAM, billing, payment,
    settlement or financial execution authority.

FAIL CLOSED:
    Missing transaction, malformed dependency results, cross-tenant evidence,
    duplicate provider-object uncertainty identities, metadata divergence,
    malformed C4D5C records and observation/evidence conflicts reject without
    inferred truth. Registry not-found is explicit non-authorizing evidence;
    every other registry failure propagates.

CERTIFICATION / UPDATE DATE: 2026-09-30
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Final

from tools.eos.legal_operations.domain.legal_evidence_commit_uncertainty import (
    LegalEvidenceCommitUncertainty,
)
from tools.eos.legal_operations.domain.legal_evidence_provider_cleanup_classification import (
    LegalEvidenceProviderCleanupClassificationEvidence,
    classify_legal_evidence_provider_observation,
)
from tools.eos.legal_operations.domain.legal_evidence_provider_write_intent_correlation import (
    LegalEvidenceProviderWriteIntentCorrelationEvidence,
    correlate_legal_evidence_provider_write_intent,
)
from tools.eos.legal_operations.registry.legal_evidence_binary_write_intent_registry import (
    LegalEvidenceBinaryWriteIntentNotFoundError,
    LegalEvidenceBinaryWriteIntentRecord,
)
from tools.eos.legal_operations.registry.legal_evidence_object_metadata_registry import (
    LegalEvidenceObjectMetadataRegistryNotFoundError,
)
from tools.eos.legal_operations.service.legal_evidence_provider_cleanup_discovery_port import (
    LegalEvidenceCompletedObjectIntentMetadataState,
    LegalEvidenceCompletedObjectObservation,
    LegalEvidenceIncompleteWriteSessionObservation,
    LegalEvidenceProviderCleanupDiscoveryPort,
    LegalEvidenceProviderDiscoveryScope,
)


VERSION: Final[str] = (
    "v1.1.0-L10A2R-C4D5D3-PROVIDER-WRITE-INTENT-CORRELATION-SERVICE"
)


class LegalEvidenceProviderCleanupClassificationServiceError(RuntimeError):
    """Stable fail-closed C4D3B orchestration error."""


class LegalEvidenceProviderCleanupClassificationTransactionRequiredError(
    LegalEvidenceProviderCleanupClassificationServiceError
):
    """Caller did not provide one already-active transaction."""


def _active_transaction(
    session: Any,
) -> Any:
    if session is None:
        raise LegalEvidenceProviderCleanupClassificationTransactionRequiredError(
            "L10A2R_C4D3B_TRANSACTION_REQUIRED"
        )

    marker = getattr(
        session,
        "in_transaction",
        False,
    )

    try:
        active = (
            marker()
            if callable(marker)
            else marker
        )
    except (
        AttributeError,
        TypeError,
    ):
        active = False

    if active is not True:
        raise LegalEvidenceProviderCleanupClassificationTransactionRequiredError(
            "L10A2R_C4D3B_TRANSACTION_REQUIRED"
        )

    return session


def _utc(
    value: object,
) -> datetime:
    if (
        not isinstance(
            value,
            datetime,
        )
        or value.tzinfo is None
        or value.utcoffset() is None
    ):
        raise LegalEvidenceProviderCleanupClassificationServiceError(
            "L10A2R_C4D3B_OBSERVED_AT_INVALID"
        )

    return value.astimezone(
        timezone.utc
    )


def _provider_key(
    *,
    tenant_id: str,
    provider_name: str,
    storage_reference: str,
    object_version_reference: str,
) -> tuple[str, str, str, str]:
    return (
        tenant_id,
        provider_name,
        storage_reference,
        object_version_reference,
    )


class LegalEvidenceProviderCleanupClassificationService:
    """Read-only orchestration of provider observations into C4D3A evidence."""

    __slots__ = (
        "_discovery",
        "_metadata_registry",
        "_uncertainty_registry",
        "_write_intent_registry",
    )

    def __init__(
        self,
        *,
        discovery: LegalEvidenceProviderCleanupDiscoveryPort,
        metadata_registry: Any,
        uncertainty_registry: Any,
        write_intent_registry: Any | None = None,
    ) -> None:
        if discovery is None:
            raise LegalEvidenceProviderCleanupClassificationServiceError(
                "L10A2R_C4D3B_DISCOVERY_REQUIRED"
            )

        if metadata_registry is None:
            raise LegalEvidenceProviderCleanupClassificationServiceError(
                "L10A2R_C4D3B_METADATA_REGISTRY_REQUIRED"
            )

        if uncertainty_registry is None:
            raise LegalEvidenceProviderCleanupClassificationServiceError(
                "L10A2R_C4D3B_UNCERTAINTY_REGISTRY_REQUIRED"
            )

        self._discovery = discovery
        self._metadata_registry = metadata_registry
        self._uncertainty_registry = uncertainty_registry
        self._write_intent_registry = write_intent_registry

    def classify_tenant_observations(
        self,
        *,
        scope: LegalEvidenceProviderDiscoveryScope,
        observed_at: datetime,
        session: Any,
    ) -> tuple[
        LegalEvidenceProviderCleanupClassificationEvidence,
        ...,
    ]:
        """Discover and classify one exact tenant's provider observations."""
        tx = _active_transaction(
            session
        )

        if type(scope) is not LegalEvidenceProviderDiscoveryScope:
            raise LegalEvidenceProviderCleanupClassificationServiceError(
                "L10A2R_C4D3B_SCOPE_REQUIRED"
            )

        at = _utc(
            observed_at
        )

        uncertainties = (
            self._uncertainty_registry.list_tenant_uncertainties(
                tenant_id=scope.tenant_id,
                session=tx,
            )
        )

        if not isinstance(
            uncertainties,
            tuple,
        ):
            raise LegalEvidenceProviderCleanupClassificationServiceError(
                "L10A2R_C4D3B_UNCERTAINTY_RESULT_INVALID"
            )

        uncertainty_by_provider: dict[
            tuple[str, str, str, str],
            LegalEvidenceCommitUncertainty,
        ] = {}

        for uncertainty in uncertainties:
            if (
                type(uncertainty)
                is not LegalEvidenceCommitUncertainty
                or uncertainty.tenant_id
                != scope.tenant_id
            ):
                raise LegalEvidenceProviderCleanupClassificationServiceError(
                    "L10A2R_C4D3B_UNCERTAINTY_SCOPE_MISMATCH"
                )

            key = _provider_key(
                tenant_id=uncertainty.tenant_id,
                provider_name=uncertainty.provider_name,
                storage_reference=uncertainty.storage_reference,
                object_version_reference=(
                    uncertainty.object_version_reference
                ),
            )

            if key in uncertainty_by_provider:
                raise LegalEvidenceProviderCleanupClassificationServiceError(
                    "L10A2R_C4D3B_PROVIDER_UNCERTAINTY_AMBIGUOUS"
                )

            uncertainty_by_provider[
                key
            ] = uncertainty

        incomplete = (
            self._discovery.list_incomplete_write_sessions(
                scope,
                observed_at=at,
            )
        )

        completed = (
            self._discovery.list_completed_object_versions(
                scope,
                observed_at=at,
            )
        )

        if (
            not isinstance(
                incomplete,
                tuple,
            )
            or not isinstance(
                completed,
                tuple,
            )
        ):
            raise LegalEvidenceProviderCleanupClassificationServiceError(
                "L10A2R_C4D3B_DISCOVERY_RESULT_INVALID"
            )

        classified: list[
            LegalEvidenceProviderCleanupClassificationEvidence
        ] = []

        for observation in incomplete:
            if (
                type(observation)
                is not LegalEvidenceIncompleteWriteSessionObservation
                or observation.tenant_id
                != scope.tenant_id
            ):
                raise LegalEvidenceProviderCleanupClassificationServiceError(
                    "L10A2R_C4D3B_DISCOVERY_SCOPE_MISMATCH"
                )

            classified.append(
                classify_legal_evidence_provider_observation(
                    observation
                )
            )

        for observation in completed:
            if (
                type(observation)
                is not LegalEvidenceCompletedObjectObservation
                or observation.tenant_id
                != scope.tenant_id
            ):
                raise LegalEvidenceProviderCleanupClassificationServiceError(
                    "L10A2R_C4D3B_DISCOVERY_SCOPE_MISMATCH"
                )

            try:
                metadata = (
                    self._metadata_registry.get_provider_object(
                        tenant_id=scope.tenant_id,
                        provider_name=observation.provider_name,
                        storage_reference=observation.storage_reference,
                        object_version_reference=(
                            observation.object_version_reference
                        ),
                        session=tx,
                    )
                )
            except LegalEvidenceObjectMetadataRegistryNotFoundError:
                metadata = None

            key = _provider_key(
                tenant_id=observation.tenant_id,
                provider_name=observation.provider_name,
                storage_reference=observation.storage_reference,
                object_version_reference=(
                    observation.object_version_reference
                ),
            )

            uncertainty = uncertainty_by_provider.get(
                key
            )

            classified.append(
                classify_legal_evidence_provider_observation(
                    observation,
                    metadata=metadata,
                    uncertainty=uncertainty,
                )
            )

        return tuple(
            sorted(
                classified,
                key=lambda item: (
                    item.provider_name,
                    item.storage_reference,
                    item.object_version_reference or "",
                    item.write_session_reference or "",
                    item.fingerprint,
                ),
            )
        )

    def correlate_tenant_completed_write_intents(
        self,
        *,
        scope: LegalEvidenceProviderDiscoveryScope,
        observed_at: datetime,
        session: Any,
    ) -> tuple[
        LegalEvidenceProviderWriteIntentCorrelationEvidence,
        ...,
    ]:
        """Correlate completed-object intent metadata with durable C4D5C rows."""

        tx = _active_transaction(
            session
        )

        if type(scope) is not LegalEvidenceProviderDiscoveryScope:
            raise LegalEvidenceProviderCleanupClassificationServiceError(
                "L10A2R_C4D5D3_SCOPE_REQUIRED"
            )

        at = _utc(
            observed_at
        )

        if self._write_intent_registry is None:
            raise LegalEvidenceProviderCleanupClassificationServiceError(
                "L10A2R_C4D5D3_WRITE_INTENT_REGISTRY_REQUIRED"
            )

        completed = (
            self._discovery.list_completed_object_versions(
                scope,
                observed_at=at,
            )
        )

        if not isinstance(
            completed,
            tuple,
        ):
            raise LegalEvidenceProviderCleanupClassificationServiceError(
                "L10A2R_C4D5D3_DISCOVERY_RESULT_INVALID"
            )

        correlated: list[
            LegalEvidenceProviderWriteIntentCorrelationEvidence
        ] = []

        for observation in completed:
            if (
                type(observation)
                is not LegalEvidenceCompletedObjectObservation
                or observation.tenant_id
                != scope.tenant_id
            ):
                raise LegalEvidenceProviderCleanupClassificationServiceError(
                    "L10A2R_C4D5D3_DISCOVERY_SCOPE_MISMATCH"
                )

            if (
                observation.write_intent_metadata_state
                is not LegalEvidenceCompletedObjectIntentMetadataState.PRESENT
            ):
                correlated.append(
                    correlate_legal_evidence_provider_write_intent(
                        observation=observation,
                        registry_lookup_performed=False,
                    )
                )
                continue

            fingerprint = observation.write_intent_fingerprint

            if fingerprint is None:
                raise LegalEvidenceProviderCleanupClassificationServiceError(
                    "L10A2R_C4D5D3_PRESENT_FINGERPRINT_REQUIRED"
                )

            try:
                record = (
                    self._write_intent_registry.get_by_fingerprint(
                        tenant_id=scope.tenant_id,
                        write_intent_fingerprint=fingerprint,
                        session=tx,
                    )
                )
            except LegalEvidenceBinaryWriteIntentNotFoundError:
                correlated.append(
                    correlate_legal_evidence_provider_write_intent(
                        observation=observation,
                        registry_lookup_performed=True,
                    )
                )
                continue

            if type(record) is not LegalEvidenceBinaryWriteIntentRecord:
                raise LegalEvidenceProviderCleanupClassificationServiceError(
                    "L10A2R_C4D5D3_WRITE_INTENT_RECORD_INVALID"
                )

            correlated.append(
                correlate_legal_evidence_provider_write_intent(
                    observation=observation,
                    registry_lookup_performed=True,
                    registered_intent=record.intent,
                    registration_record_fingerprint=(
                        record.record_fingerprint
                    ),
                    registered_at=record.registered_at,
                )
            )

        return tuple(
            sorted(
                correlated,
                key=lambda item: (
                    item.provider_name,
                    item.storage_reference,
                    item.object_version_reference,
                    item.fingerprint,
                ),
            )
        )


__all__ = [
    "VERSION",
    "LegalEvidenceProviderCleanupClassificationService",
    "LegalEvidenceProviderCleanupClassificationServiceError",
    "LegalEvidenceProviderCleanupClassificationTransactionRequiredError",
]


# ARTIFACT: legal_evidence_provider_cleanup_classification_service.py
# VERSION: v1.1.0-L10A2R-C4D5D3-PROVIDER-WRITE-INTENT-CORRELATION-SERVICE
# AUTHORITY BOUNDARY: read-only cleanup classification orchestration
# C4C POSTURE: no reconciliation invocation and no write-intent reconstruction
# C4D5C POSTURE: exact PRESENT tenant+fingerprint lookup only
# C4D5D2 POSTURE: durable rows pass through without reconstruction
# TENANT POSTURE: exact tenant discovery and control-plane evidence only
# ORPHAN POSTURE: registry match/not-found never proves orphan status
# ABORT POSTURE: no abort authority
# DELETION POSTURE: no provider deletion authority
# RETENTION POSTURE: no retention/legal-hold authority
# AVAILABILITY POSTURE: no availability authority
# PROVIDER MUTATION POSTURE: discovery reads only
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively
# END OF WILSY OS SOVEREIGN ARTIFACT
