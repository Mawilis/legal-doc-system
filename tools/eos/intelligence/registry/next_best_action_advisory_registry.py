"""WILSY OS C1D caller-session registry for advisory evidence.

TITLE: Next-Best-Action Advisory Registry
VERSION: v1.0.0-C1D-R1
AUTHORITY: Wilsy OS Core Governance; append-only advisory persistence boundary
EPITOME: Persists immutable tenant-scoped C1D envelopes with exact replay,
         strict corruption handling, and derived supersession status.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tools/eos/intelligence/registry/next_best_action_advisory_registry.py
COLLABORATION / OWNERSHIP: C1D domain supplies validated envelopes; callers own
                            Mongo sessions, transactions, commit, abort, and retry.
CERTIFICATION / UPDATE DATE: 2026-09-17
CHANGELOG: v1.0.0-C1D-R1 establishes majority+journal persistence, deterministic
           tenant indexes, immutable replay, and forward-only supersession lineage.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2.
SECURITY / PRIVACY POSTURE: Only bounded advisory identities and evidence refs persist.
TENANT BOUNDARY: Every query includes exact tenant_id; foreign rows appear absent.
AUTHORITY BOUNDARY: Persistence adapter only; no recommendation, IAM, legal,
                    billing, payment, or settlement authority is granted.
FINANCIAL AUTHORITY BOUNDARY: Kennel EOS exclusively owns financial execution.
"""
from __future__ import annotations

from collections.abc import Mapping
from typing import Any, Final

from pymongo.errors import DuplicateKeyError, PyMongoError
from pymongo.read_concern import ReadConcern
from pymongo.write_concern import WriteConcern

from tools.eos.intelligence.domain.next_best_action_advisory import (
    AdvisoryStatusProjection,
    NextBestActionAdvisory,
    NextBestActionAdvisoryError,
)

VERSION: Final[str] = "v1.0.0-C1D-R1"
COLLECTION: Final[str] = "wilsy_ai_next_best_action_advisories"
WRITE_CONCERN = WriteConcern(w="majority", j=True)
READ_CONCERN = ReadConcern("majority")


class NextBestActionAdvisoryRegistryError(ValueError):
    """Stable fail-closed registry error."""


class NextBestActionAdvisoryConflictError(NextBestActionAdvisoryRegistryError):
    """Divergent replay or supersession conflict."""


def ensure_indexes(collection: Any) -> None:
    """Create deterministic tenant-scoped uniqueness indexes."""
    target = collection.with_options(write_concern=WRITE_CONCERN, read_concern=READ_CONCERN) if hasattr(collection, "with_options") else collection
    target.create_index([("tenant_id", 1), ("advisory_id", 1)], unique=True, name="c1d_advisory_identity_unique")
    target.create_index([("tenant_id", 1), ("fingerprint", 1)], unique=True, name="c1d_advisory_fingerprint_unique")
    target.create_index([("tenant_id", 1), ("scope_ref", 1), ("source_snapshot_fingerprint", 1), ("policy_id", 1), ("policy_version", 1)], unique=True, name="c1d_advisory_snapshot_unique")
    target.create_index([("tenant_id", 1), ("supersedes_advisory_id", 1)], unique=True, partialFilterExpression={"supersedes_advisory_id": {"$type": "string"}}, name="c1d_advisory_successor_unique")


def _domain_document(row: Mapping[str, object]) -> dict[str, object]:
    if not isinstance(row, Mapping):
        raise NextBestActionAdvisoryRegistryError("C1D_CORRUPT_ADVISORY")
    return {key: value for key, value in row.items() if key != "_id"}


def _hydrate(row: Mapping[str, object]) -> NextBestActionAdvisory:
    try:
        return NextBestActionAdvisory.from_dict(_domain_document(row))
    except (NextBestActionAdvisoryError, NextBestActionAdvisoryRegistryError, TypeError, ValueError) as error:
        raise NextBestActionAdvisoryRegistryError("C1D_CORRUPT_ADVISORY") from error


class NextBestActionAdvisoryRegistry:
    """Caller-session append-only Mongo registry; it never owns transactions."""

    __slots__ = ("_collection",)

    def __init__(self, collection: Any) -> None:
        if collection is None:
            raise NextBestActionAdvisoryRegistryError("C1D_COLLECTION_REQUIRED")
        self._collection = collection.with_options(write_concern=WRITE_CONCERN, read_concern=READ_CONCERN) if hasattr(collection, "with_options") else collection

    @staticmethod
    def _require_session(session: Any) -> None:
        if session is None:
            raise NextBestActionAdvisoryRegistryError("C1D_SESSION_REQUIRED")

    def create_or_replay(self, advisory: NextBestActionAdvisory, *, session: Any) -> NextBestActionAdvisory:
        """Insert an advisory or return exact replay without transaction control."""
        if not isinstance(advisory, NextBestActionAdvisory):
            raise NextBestActionAdvisoryRegistryError("C1D_INPUT_INVALID")
        self._require_session(session)
        query = {"tenant_id": advisory.tenant_id, "advisory_id": advisory.advisory_id}
        try:
            existing = self._collection.find_one(query, session=session)
            if existing is not None:
                prior = _hydrate(existing)
                if prior.to_dict() != advisory.to_dict():
                    raise NextBestActionAdvisoryConflictError("C1D_DIVERGENT_REPLAY")
                return prior
            if advisory.supersedes_advisory_id is not None:
                predecessor = self._collection.find_one({"tenant_id": advisory.tenant_id, "advisory_id": advisory.supersedes_advisory_id}, session=session)
                if predecessor is None:
                    raise NextBestActionAdvisoryConflictError("C1D_PREDECESSOR_NOT_FOUND")
                prior = _hydrate(predecessor)
                if prior.scope_ref != advisory.scope_ref or prior.source_snapshot_fingerprint == advisory.source_snapshot_fingerprint:
                    raise NextBestActionAdvisoryConflictError("C1D_SUPERSESSION_LINEAGE_INVALID")
                if advisory.generated_at <= prior.generated_at:
                    raise NextBestActionAdvisoryConflictError("C1D_SUPERSESSION_TIME_INVALID")
                successor = self._collection.find_one({"tenant_id": advisory.tenant_id, "supersedes_advisory_id": advisory.supersedes_advisory_id}, session=session)
                if successor is not None:
                    raise NextBestActionAdvisoryConflictError("C1D_DUPLICATE_SUCCESSOR")
            self._collection.insert_one(advisory.to_dict(), session=session)
            return advisory
        except (NextBestActionAdvisoryRegistryError, NextBestActionAdvisoryError):
            raise
        except DuplicateKeyError as error:
            raise NextBestActionAdvisoryConflictError("C1D_DUPLICATE_RACE") from error
        except PyMongoError as error:
            raise NextBestActionAdvisoryRegistryError("C1D_PERSISTENCE_UNAVAILABLE") from error

    def get(self, *, tenant_id: str, advisory_id: str, session: Any) -> NextBestActionAdvisory:
        """Hydrate one exact tenant-scoped advisory; foreign rows are undisclosed."""
        if not isinstance(tenant_id, str) or not tenant_id.strip() or not isinstance(advisory_id, str) or not advisory_id.strip():
            raise NextBestActionAdvisoryRegistryError("C1D_INPUT_INVALID")
        self._require_session(session)
        try:
            row = self._collection.find_one({"tenant_id": tenant_id, "advisory_id": advisory_id}, session=session)
            if row is None:
                raise NextBestActionAdvisoryRegistryError("C1D_NOT_FOUND")
            return _hydrate(row)
        except NextBestActionAdvisoryRegistryError:
            raise
        except PyMongoError as error:
            raise NextBestActionAdvisoryRegistryError("C1D_PERSISTENCE_UNAVAILABLE") from error

    def get_status(self, *, tenant_id: str, advisory_id: str, session: Any) -> AdvisoryStatusProjection:
        """Return CURRENT/STALE as a derived reverse-supersession projection."""
        advisory = self.get(tenant_id=tenant_id, advisory_id=advisory_id, session=session)
        try:
            successor = self._collection.find_one({"tenant_id": tenant_id, "supersedes_advisory_id": advisory.advisory_id}, session=session)
            if successor is None:
                return AdvisoryStatusProjection(advisory, "CURRENT", None)
            successor_advisory = _hydrate(successor)
            return AdvisoryStatusProjection(advisory, "STALE", successor_advisory.advisory_id)
        except NextBestActionAdvisoryRegistryError:
            raise
        except PyMongoError as error:
            raise NextBestActionAdvisoryRegistryError("C1D_PERSISTENCE_UNAVAILABLE") from error


__all__ = ["VERSION", "COLLECTION", "WRITE_CONCERN", "READ_CONCERN", "ensure_indexes", "NextBestActionAdvisoryRegistry", "NextBestActionAdvisoryRegistryError", "NextBestActionAdvisoryConflictError"]

# ARTIFACT: next_best_action_advisory_registry.py
# VERSION: v1.0.0-C1D-R1
# AUTHORITY BOUNDARY: append-only advisory evidence persistence only
# TENANT POSTURE: exact tenant predicates; foreign absence is non-disclosing
# FAIL-CLOSED POSTURE: corruption, duplicate, divergence, and lineage conflicts reject
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively
# END OF WILSY OS SOVEREIGN ARTIFACT
