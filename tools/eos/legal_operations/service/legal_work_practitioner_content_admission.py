"""TITLE: WILSY OS Practitioner Matter Content Admission Boundary.
VERSION: v1.0.0-P47-R95-G72
AUTHORITY: Fail-closed prerequisite boundary only; no content access.
CHANGELOG: 2026-10-21 G72 creates exact scoped transaction-bound denial.
SECURITY: No caller approval, storage reader, role grant or wall override.
"""
from typing import Any, Final

VERSION: Final[str] = "v1.0.0-P47-R95-G72"

class PractitionerContentAdmissionDenied(PermissionError):
    """Stable, content-free practitioner admission denial."""

def _identity(name: str, value: object) -> str:
    if (
        type(value) is not str
        or not value
        or value.strip() != value
        or len(value) > 256
        or value.casefold() in {
            "unknown", "none", "null", "system", "default"
        }
        or any(ord(c) < 33 or ord(c) > 126 for c in value)
    ):
        raise PractitionerContentAdmissionDenied(
            "P47_R95_CONTENT_SCOPE_INVALID"
        )
    return value

def _transaction(session: Any) -> None:
    try:
        active = session.in_transaction
    except Exception:
        active = None
    if active is not True:
        raise PractitionerContentAdmissionDenied(
            "P47_R95_CONTENT_ACTIVE_TRANSACTION_REQUIRED"
        )

def require_practitioner_content_admission(
    *,
    tenant_id: str,
    case_matter_id: str,
    practitioner_principal_id: str,
    content_reference: str,
    session: Any,
) -> None:
    """Never return authority without independently certified source verification.

    No reader, collection, policy flag or reviewer reference is accepted.
    This function must not be interpreted as a functioning content service.
    """
    _transaction(session)
    _identity("tenant_id", tenant_id)
    _identity("case_matter_id", case_matter_id)
    _identity("practitioner_principal_id", practitioner_principal_id)
    _identity("content_reference", content_reference)
    raise PractitionerContentAdmissionDenied(
        "P47_R95_CONTENT_SOURCE_VERIFICATION_UNAVAILABLE"
    )

# END OF WILSY OS SOVEREIGN ARTIFACT
