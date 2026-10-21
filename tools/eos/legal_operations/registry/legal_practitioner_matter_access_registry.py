"""TITLE: WILSY OS Practitioner Matter Access Evidence Registry.
VERSION: v1.2.0-P47-R33-PRACTITIONER-ACCESS-REGISTRY-CODEC
AUTHORITY: Immutable exact-tenant documentary ALLOW/DENY persistence only.
EPITOME: Appends canonical codec-verified evidence with deterministic indexes,
    exact replay and a fail-closed first-revision lineage gate.
ABSOLUTE CANONICAL PATH:
    /Users/wilsonkhanyezi/legal-doc-system/tools/eos/legal_operations/registry/legal_practitioner_matter_access_registry.py
COLLABORATION / OWNERSHIP: Wilsy OS Core Engineering; callers own transaction
    lifecycle and the service codec owns serialization and hydration.
CERTIFICATION / UPDATE DATE: 2026-10-20
CHANGELOG:
    2026-10-20 v1.2.0-P47-R33-PRACTITIONER-ACCESS-REGISTRY-CODEC
    Replace domain serialization/hydration with the canonical service codec.
    2026-10-19 v1.1.0-P9-R105-P4B-FIRST-REVISION-LINEAGE-GATE
    Added transaction-bound append, replay, corruption and root-lineage gates.
COMPLIANCE: LAW EK-006; POPIA section 19; GDPR Article 32; SOC 2 CC7.2.
SECURITY / PRIVACY POSTURE: Stable bounded errors; no evidence values logged.
TENANT BOUNDARY: Every read, identity, scope and fingerprint index is tenant
    scoped; cross-tenant absence discloses no foreign record.
AUTHORITY BOUNDARY: Persistence only; no IAM, access grant, policy issuance,
    ethical-wall override, professional eligibility or reassignment authority.
TRANSACTION BOUNDARY: Caller-owned active transaction mandatory for reads and
    writes; this registry never starts, commits, aborts or retries a session.
FINANCIAL AUTHORITY BOUNDARY: None; Kennel EOS exclusively.
"""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any, Final

from pymongo import ASCENDING
from pymongo.errors import DuplicateKeyError

from tools.eos.legal_operations.domain.legal_practitioner_matter_access import (
    LegalPractitionerMatterAccessEvidence,
)
from tools.eos.legal_operations.service.legal_practitioner_matter_access_codec import (
    decode_practitioner_matter_access,
    encode_practitioner_matter_access,
    verify_practitioner_matter_access,
)


VERSION: Final[str] = "v1.2.0-P47-R33-PRACTITIONER-ACCESS-REGISTRY-CODEC"
IDENTITY_INDEX: Final[str] = "p9_access_evidence_tenant_identity_unique"
REVISION_INDEX: Final[str] = "p9_access_evidence_tenant_scope_revision_unique"
FINGERPRINT_INDEX: Final[str] = "p9_access_evidence_tenant_fingerprint_unique"


class PractitionerMatterAccessRegistryError(RuntimeError):
    """Base fail-closed registry failure with no sensitive payload details."""


class PractitionerMatterAccessTransactionRequired(
    PractitionerMatterAccessRegistryError
):
    """Signal absence of the mandatory caller-owned active transaction."""


class PractitionerMatterAccessConflict(PractitionerMatterAccessRegistryError):
    """Signal divergent identity, lineage, scope or unique-index evidence."""


class PractitionerMatterAccessPersistedInvalid(
    PractitionerMatterAccessRegistryError
):
    """Signal corrupt, noncanonical or scope-divergent persisted evidence."""


class PractitionerMatterAccessPersistenceUnavailable(
    PractitionerMatterAccessRegistryError
):
    """Signal database unavailability without leaking persistence details."""


def _transaction(session: Any) -> None:
    if session is None or getattr(session, "in_transaction", False) is not True:
        raise PractitionerMatterAccessTransactionRequired(
            "P9_R105_ACTIVE_TRANSACTION_REQUIRED"
        )


def _evidence(value: object) -> LegalPractitionerMatterAccessEvidence:
    if type(value) is not LegalPractitionerMatterAccessEvidence:
        raise PractitionerMatterAccessRegistryError(
            "P9_R105_EVIDENCE_TYPE_INVALID"
        )
    try:
        return verify_practitioner_matter_access(value)
    except Exception as error:
        raise PractitionerMatterAccessRegistryError(
            "P9_R105_CANONICAL_EVIDENCE_MISMATCH"
        ) from error


def _hydrate(record: Mapping[str, object]) -> LegalPractitionerMatterAccessEvidence:
    if not isinstance(record, Mapping):
        raise PractitionerMatterAccessPersistedInvalid(
            "P9_R105_PERSISTED_SHAPE_INVALID"
        )
    raw = dict(record)
    raw.pop("_id", None)
    try:
        hydrated = decode_practitioner_matter_access(raw)
    except (ValueError, TypeError, KeyError) as error:
        raise PractitionerMatterAccessPersistedInvalid(
            "P9_R105_PERSISTED_EVIDENCE_INVALID"
        ) from error
    if encode_practitioner_matter_access(hydrated) != raw:
        raise PractitionerMatterAccessPersistedInvalid(
            "P9_R105_PERSISTED_EVIDENCE_DIVERGENT"
        )
    return hydrated


def ensure_indexes(collection: Any) -> None:
    """Create deterministic unique evidence indexes without current pointers.

    This deployment operation creates no TTL behavior, business authority or
    mutable current state. The caller owns database selection and lifecycle.
    """
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
    """Read one own-tenant evidence identity inside the caller transaction.

    Returns None only for an absent exact-tenant identity. Foreign-tenant
    existence is neither queried nor disclosed.
    """
    _transaction(session)
    if (
        type(tenant_id) is not str
        or not tenant_id
        or tenant_id != tenant_id.strip()
        or type(access_evidence_id) is not str
        or not access_evidence_id
        or access_evidence_id != access_evidence_id.strip()
    ):
        raise PractitionerMatterAccessRegistryError("P9_R105_IDENTITY_INVALID")
    query = {"tenant_id": tenant_id, "access_evidence_id": access_evidence_id}
    try:
        record = collection.find_one(query, session=session)
    except Exception as error:
        raise PractitionerMatterAccessPersistenceUnavailable(
            "P9_R105_READ_UNAVAILABLE"
        ) from error
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
    """Append exact canonical evidence or return an exact durable replay.

    The caller owns the active transaction. Prior rows are immutable. Until a
    separate successor-lineage certificate exists, only revision one roots are
    admitted. No return value is an access grant or proof of issuer authority.
    """
    _transaction(session)
    item = _evidence(evidence)
    canonical = encode_practitioner_matter_access(item)

    existing = get_by_id(
        tenant_id=item.tenant_id,
        access_evidence_id=item.access_evidence_id,
        collection=collection,
        session=session,
    )
    if existing is not None:
        if (
            existing == item
            and encode_practitioner_matter_access(existing) == canonical
        ):
            return existing
        raise PractitionerMatterAccessConflict("P9_R105_DIVERGENT_IDENTITY")

    if item.revision != 1 or item.supersedes_fingerprint is not None:
        raise PractitionerMatterAccessConflict(
            "P9_R105_SUCCESSOR_LINEAGE_NOT_CERTIFIED"
        )

    scope = {
        "tenant_id": item.tenant_id,
        "case_matter_id": item.case_matter_id,
        "practitioner_principal_id": item.practitioner_principal_id,
        "revision": 1,
    }
    try:
        scope_record = collection.find_one(scope, session=session)
    except Exception as error:
        raise PractitionerMatterAccessPersistenceUnavailable(
            "P9_R105_SCOPE_READ_UNAVAILABLE"
        ) from error

    if scope_record is not None:
        prior = _hydrate(scope_record)
        if (
            prior.tenant_id != item.tenant_id
            or prior.case_matter_id != item.case_matter_id
            or prior.practitioner_principal_id != item.practitioner_principal_id
            or prior.revision != 1
        ):
            raise PractitionerMatterAccessPersistedInvalid(
                "P9_R105_SCOPE_RECORD_DIVERGENT"
            )
        raise PractitionerMatterAccessConflict(
            "P9_R105_FIRST_REVISION_ALREADY_EXISTS"
        )

    try:
        collection.insert_one(dict(canonical), session=session)
    except DuplicateKeyError as error:
        raise PractitionerMatterAccessConflict(
            "P9_R105_UNIQUE_COLLISION_RETRY_REQUIRED"
        ) from error
    except Exception as error:
        raise PractitionerMatterAccessPersistenceUnavailable(
            "P9_R105_INSERT_UNAVAILABLE"
        ) from error
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
# VERSION: v1.2.0-P47-R33-PRACTITIONER-ACCESS-REGISTRY-CODEC
# AUTHORITY BOUNDARY: APPEND-ONLY DOCUMENTARY EVIDENCE PERSISTENCE
# TENANT POSTURE: EXACT-TENANT QUERIES AND UNIQUE INDEXES
# FAIL-CLOSED POSTURE: DIVERGENCE, CORRUPTION AND UNCERTIFIED LINEAGE REJECT
# TRANSACTION POSTURE: CALLER-OWNED ACTIVE TRANSACTION ONLY
# ACCESS / ISSUANCE / REASSIGNMENT / FINANCIAL EXECUTION AUTHORITY: NONE
# END OF WILSY OS SOVEREIGN ARTIFACT
