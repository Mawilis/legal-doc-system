"""WILSY Legal Operations authenticated documentary evidence issuer.

VERSION: v1.0.0-P9-R105-P3R2-FIRST-REVISION-ISSUER
ABSOLUTE CANONICAL PATH:
    tools/eos/legal_operations/service/legal_practitioner_matter_access_issuer_service.py
AUTHORITY: Exact authenticated partner admission, documentary first revision.
CERTIFICATION / UPDATE DATE: 2026-10-19
CHANGELOG: P9-R105-P3R2 canonical authorization decision contract.
No matter-access grant, reassignment, financial or transport authority.
"""
from __future__ import annotations

from dataclasses import fields
from datetime import datetime
from typing import Any, Final

from tools.eos.auth.tenant_authorization import (
    TenantAuthorizationDecision,
    TenantAuthorizationReason,
    authorize_tenant_operation,
)
from tools.eos.legal_operations.domain.legal_practitioner_matter_access import (
    LegalPractitionerMatterAccessEvidence,
)
from tools.eos.legal_operations.registry.legal_practitioner_matter_access_registry import (
    append_evidence,
)

from tools.eos.legal_operations.service.legal_practitioner_matter_access_conflict_provenance import (
    PractitionerMatterAccessConflictProvenanceDenied,
    verify_current_conflict_provenance,
)

VERSION: Final[str] = "v1.1.0-P9-R105-P4D-PROVENANCE-GATED-ISSUER"
PERMISSION: Final[str] = "legal_operations:practitioner_matter_access_policy:issue"
OPERATION: Final[str] = "legal_practitioner_matter_access_policy_issue"


class PractitionerMatterAccessIssuerDenied(PermissionError):
    """Fail-closed evidence issuance denial."""


def _partner_admitted(decision: object) -> bool:
    """Check all four canonical composer result slots, without a fabricated name."""
    if not isinstance(decision, TenantAuthorizationDecision):
        return False
    names = tuple(field.name for field in fields(TenantAuthorizationDecision))
    if len(names) != 4 or names[:3] != (
        "authorized", "reason", "business_role"
    ):
        return False
    return (
        decision.authorized is True
        and decision.reason is TenantAuthorizationReason.AUTHORIZED
        and decision.business_role == "tenant_legal_partner"
        and getattr(decision, names[3]) == "LEGAL_PARTNER"
    )


def issue_first_revision_evidence(
    *,
    authenticated_principal_id: str,
    tenant_id: str,
    evidence: LegalPractitionerMatterAccessEvidence,
    principal_repository: Any,
    membership_repository: Any,
    role_assignment_repository: Any,
    business_role_repository: Any,
    collection: Any,
    session: Any,
    matter_fingerprint: str | None = None,
    client_party_id: str | None = None,
    subject_identity_fingerprint: str | None = None,
    evaluation_time: datetime | None = None,
    disposition_collection: Any = None,
) -> LegalPractitionerMatterAccessEvidence:
    """Issue first-revision documentary evidence in the caller's transaction."""
    if (
        not isinstance(authenticated_principal_id, str)
        or not authenticated_principal_id
        or authenticated_principal_id != authenticated_principal_id.strip()
        or not isinstance(tenant_id, str)
        or not tenant_id
        or tenant_id != tenant_id.strip()
        or not isinstance(evidence, LegalPractitionerMatterAccessEvidence)
    ):
        raise PractitionerMatterAccessIssuerDenied("P9_ISSUER_INPUT_INVALID")

    if (
        evidence.tenant_id != tenant_id
        or evidence.issued_by_principal_id != authenticated_principal_id
    ):
        raise PractitionerMatterAccessIssuerDenied("P9_ISSUER_SCOPE_MISMATCH")

    if evidence.revision != 1 or evidence.supersedes_fingerprint is not None:
        raise PractitionerMatterAccessIssuerDenied(
            "P9_ISSUER_SUCCESSOR_NOT_CERTIFIED"
        )

    if session is None or getattr(session, "in_transaction", False) is not True:
        raise PractitionerMatterAccessIssuerDenied(
            "P9_ISSUER_ACTIVE_TRANSACTION_REQUIRED"
        )

    decision = authorize_tenant_operation(
        principal_id=authenticated_principal_id,
        tenant_id=tenant_id,
        permission_id=PERMISSION,
        operation=OPERATION,
        principal_repository=principal_repository,
        membership_repository=membership_repository,
        role_assignment_repository=role_assignment_repository,
        business_role_repository=business_role_repository,
        session=session,
    )
    if not _partner_admitted(decision):
        raise PractitionerMatterAccessIssuerDenied(
            "P9_ISSUER_CURRENT_AUTHORITY_DENIED"
        )

    # An authorized partner without current canonical conflict provenance
    # cannot append a practitioner access policy document.
    if (
        not isinstance(matter_fingerprint, str)
        or not matter_fingerprint
        or not isinstance(client_party_id, str)
        or not client_party_id
        or not isinstance(subject_identity_fingerprint, str)
        or not subject_identity_fingerprint
        or not isinstance(evaluation_time, datetime)
        or disposition_collection is None
    ):
        raise PractitionerMatterAccessIssuerDenied(
            "P9_ISSUER_PROVENANCE_INPUT_REQUIRED"
        )

    try:
        verify_current_conflict_provenance(
            evidence=evidence,
            matter_fingerprint=matter_fingerprint,
            client_party_id=client_party_id,
            subject_identity_fingerprint=subject_identity_fingerprint,
            evaluation_time=evaluation_time,
            disposition_collection=disposition_collection,
            session=session,
        )
    except PractitionerMatterAccessConflictProvenanceDenied as exc:
        raise PractitionerMatterAccessIssuerDenied(
            "P9_ISSUER_CONFLICT_PROVENANCE_DENIED"
        ) from exc

    return append_evidence(
        evidence=evidence, collection=collection, session=session
    )


__all__ = (
    "VERSION", "PERMISSION", "OPERATION",
    "PractitionerMatterAccessIssuerDenied",
    "issue_first_revision_evidence",
)

# WILSY OS SOVEREIGN ARTIFACT SEAL
# ARTIFACT: legal_practitioner_matter_access_issuer_service.py
# VERSION: v1.0.0-P9-R105-P3R2-FIRST-REVISION-ISSUER
# AUTHORITY: FIRST-REVISION DOCUMENTARY EVIDENCE ONLY
# OPERATIONAL ACCESS / REASSIGNMENT / FINANCIAL AUTHORITY: NONE
# END OF WILSY OS SOVEREIGN ARTIFACT
