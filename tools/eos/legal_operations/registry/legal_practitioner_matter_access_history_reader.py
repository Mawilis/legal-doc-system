"""TITLE: WILSY OS Practitioner Matter Access Evidence History Reader.
VERSION: v1.1.0-P47-R33-PRACTITIONER-ACCESS-HISTORY-CODEC
AUTHORITY: Read-only transaction-bound documentary evidence retrieval.
EPITOME: Reads bounded exact-scope history and delegates strict persisted
    integrity hydration to the canonical service-owned evidence codec.
ABSOLUTE CANONICAL PATH:
    /Users/wilsonkhanyezi/legal-doc-system/tools/eos/legal_operations/registry/legal_practitioner_matter_access_history_reader.py
COLLABORATION / OWNERSHIP: Wilsy OS Core Engineering; provisioning supplies
    the caller-owned transaction and currentness consumes verified values.
CERTIFICATION / UPDATE DATE: 2026-10-20
CHANGELOG:
    2026-10-20 v1.1.0-P47-R33-PRACTITIONER-ACCESS-HISTORY-CODEC
    Replace domain parsing/serialization with canonical codec hydration.
    2026-10-19 v1.0.0-P9-R99-PRACTITIONER-ACCESS-HISTORY-READER
    Established bounded transaction-bound exact-scope history retrieval.
COMPLIANCE: LAW EK-006; POPIA section 19; GDPR Article 32; SOC 2 CC7.2.
SECURITY / PRIVACY POSTURE: Bounded error codes; no record content is logged.
TENANT BOUNDARY: Exact tenant, matter and practitioner database predicate and
    post-hydration scope verification; foreign scope fails closed.
AUTHORITY BOUNDARY: Read-only evidence retrieval; no IAM admission, access
    grant, policy issuance, ethical-wall override or professional eligibility.
TRANSACTION BOUNDARY: Caller-owned active transaction mandatory; no lifecycle.
FINANCIAL AUTHORITY BOUNDARY: None; Kennel EOS exclusively.
"""

from __future__ import annotations

from collections.abc import Mapping
from itertools import islice
from typing import Any, Final

from tools.eos.legal_operations.domain.legal_practitioner_matter_access import (
    LegalPractitionerMatterAccessEvidence,
)
from tools.eos.legal_operations.service.legal_practitioner_matter_access_codec import (
    decode_practitioner_matter_access,
    encode_practitioner_matter_access,
)


VERSION: Final[str] = "v1.1.0-P47-R33-PRACTITIONER-ACCESS-HISTORY-CODEC"
MAX_HISTORY: Final[int] = 128


class PractitionerMatterAccessHistoryReadError(ValueError):
    """Expose a bounded read failure without untrusted record content."""

    def __init__(self, code: str) -> None:
        """Record one stable error code without sensitive identifiers."""
        self.code = code
        super().__init__(code)


def _identity(name: str, value: object, *, tenant: bool = False) -> str:
    if (
        type(value) is not str
        or not value
        or value != value.strip()
        or len(value) > (160 if tenant else 200)
        or any(ord(character) < 33 or ord(character) == 127 for character in value)
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
    """Read verified documentary history without inferring access authority.

    The caller must prove current IAM separately and own the active transaction.
    Empty history proves no grant. Overlong history fails rather than truncates,
    because truncation could discard a decisive DENY or corrupt revision.

    Raises:
        PractitionerMatterAccessHistoryReadError: For invalid scope, inactive
            transaction, unavailable persistence, overflow or invalid evidence.
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
            value = decode_practitioner_matter_access(document)
            if (
                value.tenant_id != tenant
                or value.case_matter_id != matter
                or value.practitioner_principal_id != practitioner
            ):
                raise ValueError("SCOPE_MISMATCH")
            previous = by_fingerprint.get(value.fingerprint)
            if previous is not None and (
                encode_practitioner_matter_access(previous)
                != encode_practitioner_matter_access(value)
            ):
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
# VERSION: v1.1.0-P47-R33-PRACTITIONER-ACCESS-HISTORY-CODEC
# AUTHORITY BOUNDARY: READ-ONLY DOCUMENTARY EVIDENCE; NO ACCESS OR ISSUANCE
# TENANT POSTURE: EXACT QUERY AND POST-HYDRATION SCOPE
# FAIL-CLOSED POSTURE: INVALID, OVERLONG OR UNAVAILABLE HISTORY REJECTS
# TRANSACTION POSTURE: CALLER-OWNED ACTIVE TRANSACTION REQUIRED
# FINANCIAL EXECUTION AUTHORITY: NONE; KENNEL EOS EXCLUSIVELY
# END OF WILSY OS SOVEREIGN ARTIFACT
