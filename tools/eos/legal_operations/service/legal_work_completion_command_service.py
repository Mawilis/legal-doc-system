"""
WILSY OS Legal Work Completion Event Preparation.

R20R18 now consumes one already-composed R20R22
LegalWorkCompletionAuthorityEvidence value.

Authority evaluation, historical assignment resolution and canonical IAM
evidence issuance occur before this service. This module only correlates the
authority artifact to the exact work item and constructs the immutable
LegalWorkCompletionEvent candidate.

Persistence and transaction lifecycle remain outside this module.
"""

from __future__ import annotations

from typing import Final, NoReturn

from tools.eos.legal_operations.domain.legal_work_completion_authority_evidence import (
    LegalWorkCompletionAuthorityEvidence,
)
from tools.eos.legal_operations.domain.legal_work_completion_event import (
    LegalWorkCompletionEvent,
)
from tools.eos.legal_operations.domain.legal_work_item import (
    LegalWorkItem,
)


VERSION: Final[str] = (
    "v2.0.0-P14-R20R24-"
    "PURE-R20R22-WORK-COMPLETION-EVENT-COMPOSER"
)


class LegalWorkCompletionCommandError(
    ValueError
):
    """Fail-closed completion-event preparation error."""


def _fail(
    code: str,
) -> NoReturn:
    raise LegalWorkCompletionCommandError(
        code
    )


def _require_exact_work_scope(
    *,
    work_item: LegalWorkItem,
    completion_authority_evidence:
        LegalWorkCompletionAuthorityEvidence,
) -> None:
    if type(work_item) is not LegalWorkItem:
        _fail(
            "P14_R20R24_WORK_ITEM_INVALID"
        )

    if (
        type(completion_authority_evidence)
        is not LegalWorkCompletionAuthorityEvidence
    ):
        _fail(
            "P14_R20R24_COMPLETION_AUTHORITY_EVIDENCE_INVALID"
        )

    if (
        completion_authority_evidence.tenant_id
        != work_item.tenant_id
    ):
        _fail(
            "P14_R20R24_AUTHORITY_TENANT_MISMATCH"
        )

    if (
        completion_authority_evidence.case_matter_id
        != work_item.case_matter_id
    ):
        _fail(
            "P14_R20R24_AUTHORITY_MATTER_MISMATCH"
        )

    if (
        completion_authority_evidence.work_item_id
        != work_item.work_item_id
    ):
        _fail(
            "P14_R20R24_AUTHORITY_WORK_ITEM_MISMATCH"
        )

    if (
        completion_authority_evidence.work_item_fingerprint
        != work_item.fingerprint
    ):
        _fail(
            "P14_R20R24_AUTHORITY_WORK_FINGERPRINT_MISMATCH"
        )


def prepare_legal_work_completion_event(
    *,
    work_item: LegalWorkItem,
    completion_authority_evidence:
        LegalWorkCompletionAuthorityEvidence,
    completion_evidence_reference: str,
    completion_evidence_fingerprint: str,
) -> LegalWorkCompletionEvent:
    """
    Construct one immutable completion-event candidate.

    The R20R22 authority artifact is the sole authorization provenance input.
    """

    _require_exact_work_scope(
        work_item=work_item,
        completion_authority_evidence=(
            completion_authority_evidence
        ),
    )

    return LegalWorkCompletionEvent(
        tenant_id=work_item.tenant_id,
        case_matter_id=work_item.case_matter_id,
        work_item_id=work_item.work_item_id,
        work_item_fingerprint=work_item.fingerprint,
        completion_evidence_reference=(
            completion_evidence_reference
        ),
        completion_evidence_fingerprint=(
            completion_evidence_fingerprint
        ),
        completed_at=(
            completion_authority_evidence.evaluated_at
        ),
        actor_principal_id=(
            completion_authority_evidence.principal_id
        ),
        authorization_evidence_reference=(
            completion_authority_evidence
            .completion_authority_evidence_reference
        ),
        authorization_evidence_fingerprint=(
            completion_authority_evidence.fingerprint
        ),
    )


__all__ = [
    "VERSION",
    "LegalWorkCompletionCommandError",
    "prepare_legal_work_completion_event",
]


# =============================================================================
# WILSY OS SOVEREIGN ARTIFACT SEAL
# =============================================================================
# ARTIFACT: legal_work_completion_command_service.py
# AUTHORITY INPUT: one precomposed R20R22 authority evidence value
# AUTHORITY EVALUATION: NONE
# IAM REPOSITORIES: NONE
# ASSIGNMENT RESOLUTION: NONE
# SECOND EVALUATION INSTANT: NONE
# SYNTHETIC AUTHORIZATION PROVENANCE: NONE
# EVENT CONSTRUCTION: YES
# PERSISTENCE: NONE
# TRANSACTION LIFECYCLE: NONE
# WORKFLOW TRANSITION: NONE
# DEPENDENCY RELEASE: NONE
# =============================================================================
