"""WILSY OS C1C durable orchestration snapshot registry.

TITLE: AI Tool Orchestration Registry
VERSION: v1.0.0-C1C-R1
AUTHORITY: Wilsy OS Core Governance
EPITOME: Caller-session Mongo persistence for bounded orchestration facts,
         exact replay, and fail-closed revision transitions.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tools/eos/intelligence/registry/ai_tool_orchestration_registry.py
COLLABORATION / OWNERSHIP: C1C domain owns state; this adapter owns no
                            transaction lifecycle or provider/legal truth.
CERTIFICATION / UPDATE DATE: 2026-09-16
CHANGELOG: v1.0.0-C1C-R1 establishes tenant-scoped unique identity and CAS
           persistence without raw idempotency keys or transient content.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2.
SECURITY / PRIVACY POSTURE: Only bounded snapshots are persisted.
TENANT BOUNDARY: All reads and writes include tenant_id.
AUTHORITY BOUNDARY: Orchestration evidence persistence only.
FINANCIAL AUTHORITY BOUNDARY: Kennel EOS exclusively owns financial execution.
FAIL-CLOSED DECLARATION: Corruption, duplicate, divergence and CAS races reject.
"""
from __future__ import annotations

from collections.abc import Mapping
from typing import Any, Final, cast
from pymongo.errors import DuplicateKeyError, PyMongoError
from tools.eos.intelligence.domain.ai_tool_orchestration import AIToolOrchestration, AIToolOrchestrationError

VERSION: Final[str] = "v1.0.0-C1C-R1"
COLLECTION: Final[str] = "wilsy_ai_tool_orchestrations"


class AIToolOrchestrationRegistryError(ValueError):
    """Stable persistence failure."""


class AIToolOrchestrationConflictError(AIToolOrchestrationRegistryError):
    """Divergent replay or revision conflict."""


def ensure_indexes(collection: Any) -> None:
    """Create deterministic tenant-scoped indexes."""
    collection.create_index([("tenant_id", 1), ("orchestration_id", 1)], unique=True, name="c1c_orchestration_identity_unique")


def _hydrate(row: Mapping[str, object]) -> AIToolOrchestration:
    try:
        values = dict(row)
        values.pop("_id", None)
        expected = {"orchestration_id", "tenant_id", "principal_id", "correlation_id", "phase", "planner_invocation_id", "tool_invocation_id", "synthesis_invocation_id", "tool_identity", "resource_identity", "evidence_references", "outcome", "revision", "occurred_at", "fingerprint"}
        if set(values) != expected:
            raise AIToolOrchestrationRegistryError("C1C_CORRUPT_ORCHESTRATION")
        from datetime import datetime
        occurred = values.get("occurred_at")
        if isinstance(occurred, str):
            values["occurred_at"] = datetime.fromisoformat(occurred.replace("Z", "+00:00"))
        values["phase"] = str(values["phase"])
        references = values.get("evidence_references", ())
        values["evidence_references"] = tuple(cast(tuple[object, ...], references))
        return AIToolOrchestration(**cast(Any, values))
    except (KeyError, TypeError, ValueError, AIToolOrchestrationError) as error:
        raise AIToolOrchestrationRegistryError("C1C_CORRUPT_ORCHESTRATION") from error


class AIToolOrchestrationRegistry:
    """Caller-transaction registry with exact replay and revision CAS."""

    __slots__ = ("_collection",)

    def __init__(self, collection: Any) -> None:
        if collection is None:
            raise AIToolOrchestrationRegistryError("C1C_COLLECTION_REQUIRED")
        self._collection = collection

    def create_or_replay(self, item: AIToolOrchestration, *, session: Any) -> AIToolOrchestration:
        """Insert one root or return exact tenant-scoped replay."""
        if not isinstance(item, AIToolOrchestration) or session is None:
            raise AIToolOrchestrationRegistryError("C1C_INPUT_INVALID")
        try:
            existing = self._collection.find_one({"tenant_id": item.tenant_id, "orchestration_id": item.orchestration_id}, session=session)
            if existing is not None:
                prior = _hydrate(existing)
                if prior.to_dict() != item.to_dict():
                    raise AIToolOrchestrationConflictError("C1C_DIVERGENT_REPLAY")
                return prior
            self._collection.insert_one(item.to_dict(), session=session)
            return item
        except AIToolOrchestrationRegistryError:
            raise
        except DuplicateKeyError as error:
            raise AIToolOrchestrationConflictError("C1C_DUPLICATE_RACE") from error
        except PyMongoError as error:
            raise AIToolOrchestrationRegistryError("C1C_PERSISTENCE_UNAVAILABLE") from error

    def get(self, *, tenant_id: str, orchestration_id: str, session: Any) -> AIToolOrchestration:
        """Hydrate one exact tenant-scoped root snapshot."""
        try:
            row = self._collection.find_one({"tenant_id": tenant_id, "orchestration_id": orchestration_id}, session=session)
            if row is None:
                raise AIToolOrchestrationRegistryError("C1C_NOT_FOUND")
            return _hydrate(row)
        except AIToolOrchestrationRegistryError:
            raise
        except PyMongoError as error:
            raise AIToolOrchestrationRegistryError("C1C_PERSISTENCE_UNAVAILABLE") from error

    def transition(self, item: AIToolOrchestration, *, expected_revision: int, session: Any) -> AIToolOrchestration:
        """Persist one transition using tenant/id/revision compare-and-set."""
        if item.revision != expected_revision + 1:
            raise AIToolOrchestrationConflictError("C1C_REVISION_INVALID")
        result = self._collection.replace_one({"tenant_id": item.tenant_id, "orchestration_id": item.orchestration_id, "revision": expected_revision}, item.to_dict(), session=session)
        if getattr(result, "modified_count", 1) != 1:
            raise AIToolOrchestrationConflictError("C1C_REVISION_CONFLICT")
        return item


__all__ = ["VERSION", "COLLECTION", "ensure_indexes", "AIToolOrchestrationRegistry", "AIToolOrchestrationRegistryError", "AIToolOrchestrationConflictError"]

# ARTIFACT: ai_tool_orchestration_registry.py
# VERSION: v1.0.0-C1C-R1
# AUTHORITY BOUNDARY: bounded orchestration snapshot persistence
# TENANT POSTURE: exact tenant predicates and CAS revision
# FAIL-CLOSED POSTURE: corruption, duplicate and divergent replay reject
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively
# END OF WILSY OS SOVEREIGN ARTIFACT
