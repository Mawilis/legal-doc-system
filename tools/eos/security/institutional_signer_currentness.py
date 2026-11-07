"""Two-phase source-currentness recheck orchestration.

Remote source reads occur outside MongoDB transactions. A short read transaction
captures the enrollment revision; a second short transaction persists the
verifier-issued result with a compare-and-set revision guard.
"""
from __future__ import annotations

from datetime import datetime
from typing import Any, Callable

from tools.eos.security.institutional_signer_evidence_verifier import (
    InstitutionalSignerEvidenceVerifier,
)
from tools.eos.security.institutional_signer_enrollment_registry import (
    InstitutionalSignerEnrollmentRegistry,
    InstitutionalSignerRegistryConflict,
    InstitutionalSignerRegistryError,
)


def reconcile_institutional_signer_currentness(
    *,
    registry: InstitutionalSignerEnrollmentRegistry,
    verifier: InstitutionalSignerEvidenceVerifier,
    tenant_id: str,
    certificate_fingerprint_sha256: str,
    evaluated_at: datetime,
    idempotency_key: str,
    actor_reference: str,
    read_transaction: Callable[[Callable[[object], Any]], Any],
    write_transaction: Callable[[Callable[[object], Any]], Any],
) -> dict[str, Any]:
    """Re-read external evidence without holding a DB transaction, then CAS-persist.

    The source verifier must return an opaque, bounded currentness result. A
    concurrent enrollment change between the read and write transactions is
    rejected by the registry revision guard; callers must re-read and retry.
    """
    if not callable(read_transaction) or not callable(write_transaction):
        raise InstitutionalSignerRegistryError(
            "INSTITUTIONAL_SIGNER_CURRENTNESS_TRANSACTION_RUNNER_REQUIRED"
        )
    enrollment = read_transaction(
        lambda session: registry.get_enrollment(
            tenant_id=tenant_id,
            certificate_fingerprint_sha256=certificate_fingerprint_sha256,
            session=session,
        )
    )
    if enrollment.get("status") != "ACTIVE":
        raise InstitutionalSignerRegistryConflict(
            "INSTITUTIONAL_SIGNER_CURRENTNESS_ACTIVE_ENROLLMENT_REQUIRED"
        )
    enrollment_provenance = enrollment.get("evidence_provenance_snapshot")
    approval_provenance = enrollment.get("approval_evidence_provenance_snapshot")
    if not isinstance(enrollment_provenance, dict) or not isinstance(approval_provenance, dict):
        raise InstitutionalSignerRegistryError(
            "INSTITUTIONAL_SIGNER_CURRENTNESS_PROVENANCE_INCOMPLETE"
        )

    # Deliberately outside either MongoDB transaction: remote source latency
    # cannot extend a transaction or be mistaken for atomic DB participation.
    verification = verifier.verify_currentness(
        tenant_id=tenant_id,
        certificate_fingerprint_sha256=certificate_fingerprint_sha256,
        expected_enrollment_revision=enrollment["revision"],
        enrollment_provenance_snapshot=enrollment_provenance,
        approval_provenance_snapshot=approval_provenance,
        evaluated_at=evaluated_at,
    )
    return write_transaction(
        lambda session: registry.record_verified_currentness(
            verification=verification,
            idempotency_key=idempotency_key,
            actor_reference=actor_reference,
            session=session,
        )
    )


__all__ = ["reconcile_institutional_signer_currentness"]
