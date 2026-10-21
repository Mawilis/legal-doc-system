"""TITLE: WILSY P9 Practitioner Matter Access Evidence Evaluation Service.
VERSION: v1.0.0-P9-R101-ACCESS-EVALUATION-SERVICE-GREEN
AUTHORITY: Python/EOS Legal Operations read-only documentary evaluation.
EPITOME: Compose transaction-bound immutable evidence history with
    deterministic explicit-deny currentness; never authorize matter access.
ABSOLUTE CANONICAL PATH:
    tools/eos/legal_operations/service/legal_practitioner_matter_access_evaluation_service.py
COLLABORATION / OWNERSHIP: WILSY OS Core Engineering.
CERTIFICATION / UPDATE DATE: 2026-10-19
CHANGELOG:
    2026-10-19 v1.0.0-P9-R101-ACCESS-EVALUATION-SERVICE-GREEN
    Compose independently certified reader and projector without writes.
TENANT BOUNDARY: Exact tenant/matter/practitioner.
AUTHORITY BOUNDARY: Documentary finding only; caller must separately
    certify IAM, issuer authority, conflict clearance and eligibility.
TRANSACTION BOUNDARY: Caller owns already-active Mongo transaction.
FINANCIAL EXECUTION AUTHORITY: None; Kennel EOS exclusively.
"""

from __future__ import annotations

from datetime import datetime
from typing import Any, Final

from tools.eos.legal_operations.domain.legal_practitioner_matter_access_currentness import (
    LegalPractitionerMatterAccessCurrentness,
    project_legal_practitioner_matter_access_currentness,
)
from tools.eos.legal_operations.registry.legal_practitioner_matter_access_history_reader import (
    read_practitioner_matter_access_history,
)

VERSION: Final[str] = "v1.0.0-P9-R101-ACCESS-EVALUATION-SERVICE-GREEN"


def evaluate_practitioner_matter_access_evidence(
    *,
    tenant_id: str,
    case_matter_id: str,
    practitioner_principal_id: str,
    evaluation_time: datetime,
    collection: Any,
    session: Any,
) -> LegalPractitionerMatterAccessCurrentness:
    """Read and project exact documentary history; grant no access.

    Read failures, unavailable active transactions and malformed
    persistence propagate fail-closed exceptions. Never convert an
    unavailable read into an empty or apparently permitted history.
    """
    history = read_practitioner_matter_access_history(
        tenant_id=tenant_id,
        case_matter_id=case_matter_id,
        practitioner_principal_id=practitioner_principal_id,
        collection=collection,
        session=session,
    )
    return project_legal_practitioner_matter_access_currentness(
        tenant_id=tenant_id,
        case_matter_id=case_matter_id,
        practitioner_principal_id=practitioner_principal_id,
        evaluation_time=evaluation_time,
        evidence=history,
    )


__all__ = [
    "VERSION",
    "evaluate_practitioner_matter_access_evidence",
]

# WILSY OS SOVEREIGN ARTIFACT SEAL
# ARTIFACT: legal_practitioner_matter_access_evaluation_service.py
# VERSION: v1.0.0-P9-R101-ACCESS-EVALUATION-SERVICE-GREEN
# AUTHORITY: NO IAM OR MATTER ACCESS GRANT
# REASSIGNMENT AND FINANCIAL EXECUTION AUTHORITY: NONE
# END OF WILSY OS SOVEREIGN ARTIFACT
