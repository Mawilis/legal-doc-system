"""TITLE: WILSY P9 Practitioner Matter Access Evidence History Reader.
VERSION: v1.0.0-P9-R99-PRACTITIONER-ACCESS-HISTORY-READER
AUTHORITY: Read-only, transaction-bound documentary evidence retrieval.
EPITOME: Exact-scope bounded history, strict integrity hydration, fail closed.
ABSOLUTE CANONICAL PATH:
    tools/eos/legal_operations/registry/legal_practitioner_matter_access_history_reader.py
COLLABORATION / OWNERSHIP: WILSY OS Core Engineering.
CERTIFICATION / UPDATE DATE: 2026-10-19
CHANGELOG:
    2026-10-19 v1.0.0-P9-R99-PRACTITIONER-ACCESS-HISTORY-READER
    Add bounded read-only evidence retrieval with mandatory transaction.
TENANT BOUNDARY: Exact tenant/matter/practitioner predicates.
AUTHORITY BOUNDARY: No IAM admission, access granting, policy issuance,
    ethical-wall override, professional eligibility or reassignment.
TRANSACTION BOUNDARY: Caller-owned active transaction mandatory; no lifecycle.
FINANCIAL EXECUTION AUTHORITY: None; Kennel EOS exclusively.
"""

from __future__ import annotations

from collections.abc import Mapping
from itertools import islice
from typing import Any, Final

from tools.eos.legal_operations.domain.legal_practitioner_matter_access import (
    LegalPractitionerMatterAccessEvidence,
)

VERSION: Final[str] = "v1.0.0-P9-R99-PRACTITIONER-ACCESS-HISTORY-READER"
MAX_HISTORY: Final[int] = 128


class PractitionerMatterAccessHistoryReadError(ValueError):
    """Public bounded failure; no untrusted record content in messages."""


def _identity(name: str, value: object, *, tenant: bool = False) -> str:
    if (
        type(value) is not str
        or not value
        or value != value.strip()
        or len(value) > (160 if tenant else 200)
        or any(ord(ch) < 33 or ord(ch) == 127 for ch in value)
    ):
        raise PractitionerMatterAccessHistoryReadError(
            "P9_R99_" + name.upper() + "_INVALID"
        )
    if tenant and value.casefold() in {"default", "global", "root", "*"}:
        raise PractitionerMatterAccessHistoryReadError(
            "P9_R99_TENANT_ID_INVALID"
        )
    return value


def read_practitioner_matter_access_history(
    *,
    tenant_id: str,
    case_matter_id: str,
    practitioner_principal_id: str,
    collection: Any,
    session: Any,
) -> tuple[LegalPractitionerMatterAccessEvidence, ...]:
    """Read documentary evidence, never infer or issue access authority.

    An authorized caller must establish current IAM permission separately.
    Empty history proves no grant. An overlong history is not truncated;
    it fails closed because truncation could discard a decisive DENY.
    """
    tenant = _identity("tenant_id", tenant_id, tenant=True)
    matter = _identity("case_matter_id", case_matter_id)
    practitioner = _identity(
        "practitioner_principal_id", practitioner_principal_id
    )

    try:
        active = getattr(session, "in_transaction", False) is True
    except Exception:
        active = False
    if not active:
        raise PractitionerMatterAccessHistoryReadError(
            "P9_R99_ACTIVE_TRANSACTION_REQUIRED"
        )

    predicate = {
        "tenant_id": tenant,
        "case_matter_id": matter,
        "practitioner_principal_id": practitioner,
    }
    try:
        cursor = collection.find(predicate, session=session)
        documents = tuple(islice(iter(cursor), MAX_HISTORY + 1))
    except Exception as error:
        raise PractitionerMatterAccessHistoryReadError(
            "P9_R99_HISTORY_READ_UNAVAILABLE"
        ) from error

    if len(documents) > MAX_HISTORY:
        raise PractitionerMatterAccessHistoryReadError(
            "P9_R99_HISTORY_LIMIT_EXCEEDED"
        )

    by_fingerprint: dict[str, LegalPractitionerMatterAccessEvidence] = {}
    try:
        for raw in documents:
            if not isinstance(raw, Mapping):
                raise ValueError("INVALID_DOCUMENT")
            document = dict(raw)
            document.pop("_id", None)
            value = LegalPractitionerMatterAccessEvidence.from_dict(document)
            if (
                value.tenant_id != tenant
                or value.case_matter_id != matter
                or value.practitioner_principal_id != practitioner
            ):
                raise ValueError("SCOPE_MISMATCH")
            previous = by_fingerprint.get(value.fingerprint)
            if previous is not None and previous.to_dict() != value.to_dict():
                raise ValueError("DIVERGENT_REPLAY")
            by_fingerprint[value.fingerprint] = value
    except Exception as error:
        raise PractitionerMatterAccessHistoryReadError(
            "P9_R99_PERSISTED_HISTORY_INVALID"
        ) from error

    return tuple(by_fingerprint[key] for key in sorted(by_fingerprint))


__all__ = [
    "VERSION",
    "MAX_HISTORY",
    "PractitionerMatterAccessHistoryReadError",
    "read_practitioner_matter_access_history",
]

# WILSY OS SOVEREIGN ARTIFACT SEAL
# ARTIFACT: legal_practitioner_matter_access_history_reader.py
# VERSION: v1.0.0-P9-R99-PRACTITIONER-ACCESS-HISTORY-READER
# AUTHORITY: READ ONLY; NO ISSUANCE OR ACCESS GRANT
# FINANCIAL EXECUTION AUTHORITY: NONE
# END OF WILSY OS SOVEREIGN ARTIFACT
