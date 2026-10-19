"""WILSY Legal Operations practitioner matter-access evidence registry.

VERSION: v1.0.0-P9-R105-P1-PRACTITIONER-ACCESS-EVIDENCE-REGISTRY
ABSOLUTE CANONICAL PATH:
    tools/eos/legal_operations/registry/legal_practitioner_matter_access_registry.py
AUTHORITY: Immutable, own-tenant documentary ALLOW/DENY evidence persistence.
CERTIFICATION / UPDATE DATE: 2026-10-19
CHANGELOG:
    2026-10-19 P9-R105-P1 transaction-bound append, replay and corruption gates.

No IAM authorization, matter-access grants, policy issuance orchestration,
reassignment execution, financial authority, or mutable current pointers.
"""

from __future__ import annotations

from typing import Any, Final, Mapping

from pymongo import ASCENDING
from pymongo.errors import DuplicateKeyError

from tools.eos.legal_operations.domain.legal_practitioner_matter_access import (
    LegalPractitionerMatterAccessEvidence,
)

VERSION: Final[str] = (
    "v1.0.0-P9-R105-P1-PRACTITIONER-ACCESS-EVIDENCE-REGISTRY"
)

IDENTITY_INDEX: Final[str] = "p9_access_evidence_tenant_identity_unique"
REVISION_INDEX: Final[str] = "p9_access_evidence_tenant_scope_revision_unique"
FINGERPRINT_INDEX: Final[str] = "p9_access_evidence_tenant_fingerprint_unique"


class PractitionerMatterAccessRegistryError(RuntimeError):
    """Fail-closed evidence-registry error."""


class PractitionerMatterAccessTransactionRequired(
    PractitionerMatterAccessRegistryError
):
    pass


class PractitionerMatterAccessConflict(
    PractitionerMatterAccessRegistryError
):
    pass


class PractitionerMatterAccessPersistedInvalid(
    PractitionerMatterAccessRegistryError
):
    pass


class PractitionerMatterAccessPersistenceUnavailable(
    PractitionerMatterAccessRegistryError
):
    pass


def _transaction(session: Any) -> None:
    if session is None or getattr(session, "in_transaction", False) is not True:
        raise PractitionerMatterAccessTransactionRequired(
            "P9_R105_ACTIVE_TRANSACTION_REQUIRED"
        )


def _evidence(value: object) -> LegalPractitionerMatterAccessEvidence:
    if not isinstance(value, LegalPractitionerMatterAccessEvidence):
        raise PractitionerMatterAccessRegistryError(
            "P9_R105_EVIDENCE_TYPE_INVALID"
        )
    return value


def _hydrate(
    record: Mapping[str, object],
) -> LegalPractitionerMatterAccessEvidence:
    if not isinstance(record, Mapping):
        raise PractitionerMatterAccessPersistedInvalid(
            "P9_R105_PERSISTED_SHAPE_INVALID"
        )
    raw = dict(record)
    raw.pop("_id", None)
    try:
        hydrated = LegalPractitionerMatterAccessEvidence.from_dict(raw)
    except (ValueError, TypeError, KeyError) as exc:
        raise PractitionerMatterAccessPersistedInvalid(
            "P9_R105_PERSISTED_EVIDENCE_INVALID"
        ) from exc
    if hydrated.to_dict() != raw:
        raise PractitionerMatterAccessPersistedInvalid(
            "P9_R105_PERSISTED_EVIDENCE_DIVERGENT"
        )
    return hydrated


def ensure_indexes(collection: Any) -> None:
    """Create only deterministic unique indexes; never TTL/current pointers."""
    collection.create_index(
        [("tenant_id", ASCENDING), ("access_evidence_id", ASCENDING)],
        unique=True,
        name=IDENTITY_INDEX,
    )
    collection.create_index(
        [
            ("tenant_id", ASCENDING),
            ("case_matter_id", ASCENDING),
            ("practitioner_principal_id", ASCENDING),
            ("revision", ASCENDING),
        ],
        unique=True,
        name=REVISION_INDEX,
    )
    collection.create_index(
        [("tenant_id", ASCENDING), ("fingerprint", ASCENDING)],
        unique=True,
        name=FINGERPRINT_INDEX,
    )


def get_by_id(
    *,
    tenant_id: str,
    access_evidence_id: str,
    collection: Any,
    session: Any,
) -> LegalPractitionerMatterAccessEvidence | None:
    _transaction(session)
    if (
        not isinstance(tenant_id, str)
        or not tenant_id
        or tenant_id != tenant_id.strip()
        or not isinstance(access_evidence_id, str)
        or not access_evidence_id
        or access_evidence_id != access_evidence_id.strip()
    ):
        raise PractitionerMatterAccessRegistryError(
            "P9_R105_IDENTITY_INVALID"
        )
    query = {
        "tenant_id": tenant_id,
        "access_evidence_id": access_evidence_id,
    }
    try:
        record = collection.find_one(query, session=session)
    except Exception as exc:
        raise PractitionerMatterAccessPersistenceUnavailable(
            "P9_R105_READ_UNAVAILABLE"
        ) from exc
    if record is None:
        return None
    result = _hydrate(record)
    if (
        result.tenant_id != tenant_id
        or result.access_evidence_id != access_evidence_id
    ):
        raise PractitionerMatterAccessPersistedInvalid(
            "P9_R105_PERSISTED_IDENTITY_MISMATCH"
        )
    return result


def append_evidence(
    *,
    evidence: LegalPractitionerMatterAccessEvidence,
    collection: Any,
    session: Any,
) -> LegalPractitionerMatterAccessEvidence:
    """Caller-owned transaction; exact replay only; no mutation of prior rows."""
    _transaction(session)
    item = _evidence(evidence)
    canonical = item.to_dict()
    authoritative = LegalPractitionerMatterAccessEvidence.from_dict(
        canonical
    )
    if authoritative != item:
        raise PractitionerMatterAccessRegistryError(
            "P9_R105_CANONICAL_EVIDENCE_MISMATCH"
        )

    existing = get_by_id(
        tenant_id=item.tenant_id,
        access_evidence_id=item.access_evidence_id,
        collection=collection,
        session=session,
    )
    if existing is not None:
        if existing == item and existing.to_dict() == canonical:
            return existing
        raise PractitionerMatterAccessConflict(
            "P9_R105_DIVERGENT_IDENTITY"
        )

    try:
        collection.insert_one(dict(canonical), session=session)
    except DuplicateKeyError as exc:
        # A duplicate revision/fingerprint or competing identity is never
        # silently reinterpreted as authorization.
        raise PractitionerMatterAccessConflict(
            "P9_R105_UNIQUE_COLLISION_RETRY_REQUIRED"
        ) from exc
    except Exception as exc:
        raise PractitionerMatterAccessPersistenceUnavailable(
            "P9_R105_INSERT_UNAVAILABLE"
        ) from exc
    return item


__all__ = [
    "VERSION",
    "IDENTITY_INDEX",
    "REVISION_INDEX",
    "FINGERPRINT_INDEX",
    "PractitionerMatterAccessRegistryError",
    "PractitionerMatterAccessTransactionRequired",
    "PractitionerMatterAccessConflict",
    "PractitionerMatterAccessPersistedInvalid",
    "PractitionerMatterAccessPersistenceUnavailable",
    "ensure_indexes",
    "get_by_id",
    "append_evidence",
]

# WILSY OS SOVEREIGN ARTIFACT SEAL
# ARTIFACT: legal_practitioner_matter_access_registry.py
# VERSION: v1.0.0-P9-R105-P1-PRACTITIONER-ACCESS-EVIDENCE-REGISTRY
# AUTHORITY: APPEND-ONLY DOCUMENTARY EVIDENCE
# ACCESS GRANT / POLICY ISSUER / REASSIGNMENT AUTHORITY: NONE
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively
# END OF WILSY OS SOVEREIGN ARTIFACT
