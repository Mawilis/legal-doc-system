"""Append-only registry for platform privileged-eligibility prerequisites.

TITLE: Platform Privileged Eligibility Prerequisite Registry
VERSION: v1.0.0-P2-R3-PLATFORM-PREREQUISITE-REGISTRY
AUTHORITY: Wilsy OS Sovereign IAM persistence boundary
EPITOME: Persists immutable Core-Governance designation revisions and resolves history.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tools/eos/auth/platform_privileged_eligibility_prerequisite_registry.py
CERTIFICATION / UPDATE DATE: 2026-10-14
CHANGELOG: v1.0.0 establishes append-only exact replay and current resolution.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2.
TENANT BOUNDARY: PLATFORM_SYSTEM only.
AUTHORITY BOUNDARY: Persistence only; no designation or lifecycle permission.
FINANCIAL AUTHORITY BOUNDARY: None.
"""
from __future__ import annotations

from datetime import datetime
from typing import Any, Final, Mapping

from pymongo import ASCENDING, DESCENDING
from pymongo.errors import DuplicateKeyError

from tools.eos.auth.platform_privileged_eligibility_prerequisite import (
    PlatformPrivilegedEligibilityPrerequisite,
    PlatformPrivilegedEligibilityPrerequisiteError,
    PRIVILEGE_CLASS,
    SCOPE,
)

VERSION: Final[str] = "v1.0.0-P2-R3-PLATFORM-PREREQUISITE-REGISTRY"
COLLECTION: Final[str] = "platform_privileged_eligibility_prerequisites"


class PlatformPrerequisiteRegistryError(RuntimeError):
    """Fail-closed registry error with a stable code."""
    def __init__(self, code: str) -> None:
        super().__init__(code)
        self.code = code


def _transaction(session: object) -> None:
    if session is None or getattr(session, "in_transaction", False) is not True:
        raise PlatformPrerequisiteRegistryError("ACTIVE_TRANSACTION_REQUIRED")


def _hydrate(row: object) -> PlatformPrivilegedEligibilityPrerequisite:
    if not isinstance(row, Mapping):
        raise PlatformPrerequisiteRegistryError("PERSISTED_RECORD_INVALID")
    material = dict(row)
    material.pop("_id", None)
    try:
        return PlatformPrivilegedEligibilityPrerequisite.from_persisted(material)
    except PlatformPrivilegedEligibilityPrerequisiteError as error:
        raise PlatformPrerequisiteRegistryError("PERSISTED_RECORD_INVALID") from error


class PlatformPrivilegedEligibilityPrerequisiteRegistry:
    """Append-only revision persistence with caller-owned transactions."""

    def __init__(self, collection: Any) -> None:
        if collection is None:
            raise PlatformPrerequisiteRegistryError("COLLECTION_REQUIRED")
        self._collection = collection

    def ensure_indexes(self) -> None:
        """Create deterministic identity/revision and current-read indexes; no TTL."""
        self._collection.create_index([("platform_prerequisite_id", ASCENDING), ("revision", ASCENDING)], unique=True, name="platform_prerequisite_revision_unique")
        self._collection.create_index([("principal_id", ASCENDING), ("privilege_class", ASCENDING), ("scope", ASCENDING), ("revision", DESCENDING)], name="platform_prerequisite_current_lookup")

    def append(self, value: PlatformPrivilegedEligibilityPrerequisite, *, session: object) -> PlatformPrivilegedEligibilityPrerequisite:
        """Append revision one or its exact next successor; exact replay is idempotent."""
        _transaction(session)
        if not isinstance(value, PlatformPrivilegedEligibilityPrerequisite):
            raise PlatformPrerequisiteRegistryError("PREREQUISITE_INVALID")
        rows = list(self._collection.find({"platform_prerequisite_id": value.platform_prerequisite_id}, session=session).sort("revision", DESCENDING))
        if rows:
            latest = _hydrate(rows[0])
            if latest.revision == value.revision:
                if latest == value:
                    return latest
                raise PlatformPrerequisiteRegistryError("DIVERGENT_REPLAY")
            if value.revision != latest.revision + 1 or latest.status.value != "ACTIVE" or value.principal_id != latest.principal_id:
                raise PlatformPrerequisiteRegistryError("REVISION_CHAIN_INVALID")
        elif value.revision != 1:
            raise PlatformPrerequisiteRegistryError("INITIAL_REVISION_REQUIRED")
        try:
            self._collection.insert_one(value.to_persisted(), session=session)
        except DuplicateKeyError as error:
            raise PlatformPrerequisiteRegistryError("WHOLE_TRANSACTION_RETRY_REQUIRED") from error
        return value

    def get(self, *, platform_prerequisite_id: str, revision: int, session: object = None) -> PlatformPrivilegedEligibilityPrerequisite | None:
        """Read one exact immutable revision."""
        row = self._collection.find_one({"platform_prerequisite_id": platform_prerequisite_id, "revision": revision}, session=session)
        return None if row is None else _hydrate(row)

    def resolve_current(self, *, principal_id: str, privilege_class: str, scope: str,
                        at: datetime, session: object = None) -> PlatformPrivilegedEligibilityPrerequisite | None:
        """Resolve exact latest history and apply lifecycle/effective-window currentness."""
        if privilege_class != PRIVILEGE_CLASS or scope != SCOPE or not isinstance(principal_id, str) or not principal_id or "*" in principal_id:
            return None
        rows = list(self._collection.find({"principal_id": principal_id, "privilege_class": privilege_class, "scope": scope}, session=session).sort("revision", DESCENDING))
        if not rows:
            return None
        values = tuple(_hydrate(row) for row in rows)
        ids = {value.platform_prerequisite_id for value in values}
        if len(ids) != 1 or len({value.revision for value in values}) != len(values):
            raise PlatformPrerequisiteRegistryError("PREREQUISITE_HISTORY_INVALID")
        ordered = sorted(values, key=lambda value: value.revision)
        if [value.revision for value in ordered] != list(range(1, len(ordered) + 1)):
            raise PlatformPrerequisiteRegistryError("PREREQUISITE_HISTORY_INVALID")
        latest = ordered[-1]
        return latest if latest.is_current_at(at) else None


__all__ = ["COLLECTION", "VERSION", "PlatformPrerequisiteRegistryError", "PlatformPrivilegedEligibilityPrerequisiteRegistry"]

# WILSY OS SOVEREIGN ARTIFACT SEAL
# ARTIFACT: platform_privileged_eligibility_prerequisite_registry.py
# VERSION: v1.0.0-P2-R3-PLATFORM-PREREQUISITE-REGISTRY
# MUTATION: append-only, caller-owned active transaction
# TTL / UPDATE / DELETE: FORBIDDEN
# TENANT / FINANCIAL / ACTIVATION AUTHORITY: NONE
# END OF WILSY OS SOVEREIGN ARTIFACT
