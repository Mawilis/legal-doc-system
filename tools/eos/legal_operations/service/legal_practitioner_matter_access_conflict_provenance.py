"""WILSY Legal Operations conflict-disposition provenance boundary.

VERSION: v1.0.0-P9-R105-P4C-R2B-CONFLICT-PROVENANCE
AUTHORITY: Read-only current conflict-disposition verification.
CERTIFICATION / UPDATE DATE: 2026-10-19
CHANGELOG: Exact-scoped transaction-bound history and pure currentness.

A positive conflict disposition is necessary evidence, not practitioner
approval, ethical-wall clearance, access admission or financial authority.
"""
from __future__ import annotations

from datetime import datetime
from typing import Any, Final

from tools.eos.legal_operations.domain.legal_practitioner_matter_access import (
    LegalPractitionerMatterAccessEvidence,
)
from tools.eos.legal_operations.domain.legal_client_matter_conflict_disposition import (
    LegalClientMatterConflictDisposition,
)
from tools.eos.legal_operations.domain.legal_client_matter_conflict_disposition_currentness import (
    LegalClientMatterConflictDispositionCurrentnessState,
    project_legal_client_matter_conflict_disposition_currentness,
)
from tools.eos.legal_operations.registry.legal_client_matter_conflict_disposition_registry import (
    list_dispositions_for_context,
)

VERSION: Final[str] = "v1.0.0-P9-R105-P4C-R2B-CONFLICT-PROVENANCE"


class PractitionerMatterAccessConflictProvenanceDenied(PermissionError):
    """Fail-closed conflict provenance denial."""


def verify_current_conflict_provenance(
    *,
    evidence: LegalPractitionerMatterAccessEvidence,
    matter_fingerprint: str,
    client_party_id: str,
    subject_identity_fingerprint: str,
    evaluation_time: datetime,
    disposition_collection: Any,
    session: Any,
) -> None:
    """Require current source disposition under exact externally supplied scope.

    This checks conflict provenance only, never practitioner authority.
    """
    if type(evidence) is not LegalPractitionerMatterAccessEvidence:
        raise PractitionerMatterAccessConflictProvenanceDenied(
            "P9_PROVENANCE_EVIDENCE_INVALID"
        )
    if session is None or getattr(session, "in_transaction", False) is not True:
        raise PractitionerMatterAccessConflictProvenanceDenied(
            "P9_PROVENANCE_ACTIVE_TRANSACTION_REQUIRED"
        )
    if (
        type(matter_fingerprint) is not str
        or type(client_party_id) is not str
        or type(subject_identity_fingerprint) is not str
        or not matter_fingerprint
        or not client_party_id
        or not subject_identity_fingerprint
    ):
        raise PractitionerMatterAccessConflictProvenanceDenied(
            "P9_PROVENANCE_CONTEXT_INVALID"
        )

    try:
        history = list_dispositions_for_context(
            tenant_id=evidence.tenant_id,
            case_matter_id=evidence.case_matter_id,
            matter_fingerprint=matter_fingerprint,
            client_party_id=client_party_id,
            subject_identity_fingerprint=subject_identity_fingerprint,
            disposition_collection=disposition_collection,
            session=session,
        )
        if not history:
            raise PractitionerMatterAccessConflictProvenanceDenied(
                "P9_PROVENANCE_HISTORY_ABSENT"
            )

        projection = project_legal_client_matter_conflict_disposition_currentness(
            tenant_id=evidence.tenant_id,
            case_matter_id=evidence.case_matter_id,
            matter_fingerprint=matter_fingerprint,
            client_party_id=client_party_id,
            subject_identity_fingerprint=subject_identity_fingerprint,
            evaluation_time=evaluation_time,
            dispositions=history,
        )
    except PractitionerMatterAccessConflictProvenanceDenied:
        raise
    except Exception as exc:
        raise PractitionerMatterAccessConflictProvenanceDenied(
            "P9_PROVENANCE_AUTHORITY_UNAVAILABLE"
        ) from exc

    if (
        projection.state
        is not LegalClientMatterConflictDispositionCurrentnessState.ENGAGEMENT_PERMITTED
        or projection.tenant_id != evidence.tenant_id
        or projection.case_matter_id != evidence.case_matter_id
        or projection.matter_fingerprint != matter_fingerprint
        or projection.client_party_id != client_party_id
        or projection.subject_identity_fingerprint != subject_identity_fingerprint
        or projection.evaluation_time != evaluation_time
        or projection.corruption_evidence_fingerprints
        or projection.decisive_disposition_fingerprints
        != (evidence.source_evidence_fingerprint,)
    ):
        raise PractitionerMatterAccessConflictProvenanceDenied(
            "P9_PROVENANCE_CURRENT_AUTHORITY_MISMATCH"
        )

    # Confirm the referenced fingerprint is an actual exact-scope
    # canonical disposition, not merely an arbitrary projector string.
    if not any(
        type(item) is LegalClientMatterConflictDisposition
        and item.fingerprint == evidence.source_evidence_fingerprint
        and item.tenant_id == evidence.tenant_id
        and item.case_matter_id == evidence.case_matter_id
        for item in history
    ):
        raise PractitionerMatterAccessConflictProvenanceDenied(
            "P9_PROVENANCE_SOURCE_NOT_PRESENT"
        )


__all__ = (
    "VERSION",
    "PractitionerMatterAccessConflictProvenanceDenied",
    "verify_current_conflict_provenance",
)

# WILSY OS SOVEREIGN ARTIFACT SEAL
# ARTIFACT: legal_practitioner_matter_access_conflict_provenance.py
# VERSION: v1.0.0-P9-R105-P4C-R2B-CONFLICT-PROVENANCE
# ACCESS GRANT / ETHICAL WALL / ISSUER / FINANCIAL AUTHORITY: NONE
# END OF WILSY OS SOVEREIGN ARTIFACT
