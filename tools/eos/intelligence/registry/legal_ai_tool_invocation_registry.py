"""Durable tenant-scoped registry for WILSY AI legal-tool invocation evidence.

TITLE: WILSY AI Legal Tool Invocation Evidence Registry
VERSION: v1.1.0-L7B-WILSY-AI-LEGAL-TOOL-INVOCATION-REGISTRY
AUTHORITY: Append-only invocation-evidence persistence and strict hydration.
EPITOME: Converts Mongo transport documents into the canonical invocation
         evidence domain without transferring transaction or legal authority.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tools/eos/intelligence/registry/legal_ai_tool_invocation_registry.py
COLLABORATION / OWNERSHIP: Gateway supplies immutable evidence; caller owns
                            session, transaction, commit, abort, and retry.
CERTIFICATION / UPDATE DATE: 2026-09-16
CHANGELOG: v1.1.0 strips only Mongo transport metadata ``_id`` before strict
           canonical hydration, preserving unknown-field and fingerprint gates.
           v1.0.0 established tenant-scoped append-only evidence persistence.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2.
SECURITY / PRIVACY POSTURE: No prompts, secrets, or provider payloads are
                             introduced; malformed evidence fails closed.
TENANT BOUNDARY: Every lookup and write includes exact tenant_id.
AUTHORITY BOUNDARY: Persistence adapter only; no IAM, legal lifecycle, billing,
                    invoice, payment, or settlement authority.
FINANCIAL AUTHORITY BOUNDARY: Kennel EOS exclusively owns execution and settlement.
FAIL-CLOSED DECLARATION: Corruption, duplicate divergence, unknown fields,
                         fingerprint mismatch, and persistence errors reject.
"""
from __future__ import annotations

from collections.abc import Mapping
from typing import Any, Final
from pymongo.errors import DuplicateKeyError, PyMongoError
from pymongo.read_concern import ReadConcern
from pymongo.write_concern import WriteConcern
from tools.eos.intelligence.domain.legal_ai_gateway import LegalAIToolGatewayError, LegalAIToolInvocationEvidence

VERSION: Final[str] = "v1.1.0-L7B-WILSY-AI-LEGAL-TOOL-INVOCATION-REGISTRY"
COLLECTION: Final[str] = "wilsy_ai_legal_tool_invocations"
WRITE_CONCERN = WriteConcern(w="majority", j=True)
READ_CONCERN = ReadConcern("majority")


class LegalAIToolInvocationRegistryError(ValueError):
    """Base persistence error."""


class LegalAIToolInvocationConflictError(LegalAIToolInvocationRegistryError):
    """Existing invocation evidence is divergent."""


def _canonical_domain_document(document: Mapping[str, object]) -> dict[str, object]:
    """Remove only Mongo's transport ``_id`` before strict domain hydration."""
    if not isinstance(document, Mapping):
        raise TypeError("persisted invocation document must be a mapping")
    return {key: value for key, value in document.items() if key != "_id"}


def ensure_indexes(collection: Any) -> None:
    """Create deterministic tenant-scoped uniqueness indexes."""
    target = collection.with_options(write_concern=WRITE_CONCERN, read_concern=READ_CONCERN) if hasattr(collection, "with_options") else collection
    target.create_index([("tenant_id", 1), ("invocation_id", 1)], unique=True, name="wilsy_ai_legal_tool_invocation_unique")
    target.create_index([("tenant_id", 1), ("fingerprint", 1)], unique=True, name="wilsy_ai_legal_tool_evidence_unique")


class LegalAIToolInvocationRegistry:
    """Caller-session append-only evidence registry with exact replay."""

    __slots__ = ("_collection",)

    def __init__(self, collection: Any) -> None:
        if collection is None: raise LegalAIToolInvocationRegistryError("L7B_COLLECTION_REQUIRED")
        self._collection = collection.with_options(write_concern=WRITE_CONCERN, read_concern=READ_CONCERN) if hasattr(collection, "with_options") else collection

    def create_or_replay(self, evidence: LegalAIToolInvocationEvidence, *, session: Any) -> LegalAIToolInvocationEvidence:
        """Insert evidence once or return byte-equivalent replay; never owns transaction."""
        if not isinstance(evidence, LegalAIToolInvocationEvidence) or session is None:
            raise LegalAIToolInvocationRegistryError("L7B_INPUT_INVALID")
        query = {"tenant_id": evidence.tenant_id, "invocation_id": evidence.invocation_id}
        try: existing = self._collection.find_one(query, session=session)
        except PyMongoError as error: raise LegalAIToolInvocationRegistryError("L7B_PERSISTENCE_UNAVAILABLE") from error
        if existing is not None:
            try: hydrated = LegalAIToolInvocationEvidence.from_dict(_canonical_domain_document(existing))
            except (LegalAIToolGatewayError, TypeError, KeyError) as error: raise LegalAIToolInvocationRegistryError("L7B_CORRUPT_EVIDENCE") from error
            if hydrated.to_dict() != evidence.to_dict(): raise LegalAIToolInvocationConflictError("L7B_DIVERGENT_REPLAY")
            return hydrated
        try: self._collection.insert_one(evidence.to_dict(), session=session)
        except DuplicateKeyError as error: raise LegalAIToolInvocationConflictError("L7B_DUPLICATE_RACE") from error
        except PyMongoError as error: raise LegalAIToolInvocationRegistryError("L7B_PERSISTENCE_UNAVAILABLE") from error
        return evidence

    def get(self, *, tenant_id: str, invocation_id: str, session: Any) -> LegalAIToolInvocationEvidence:
        """Hydrate exact tenant evidence; absence is non-disclosing."""
        if not isinstance(tenant_id, str) or not tenant_id.strip() or not isinstance(invocation_id, str) or not invocation_id.strip() or session is None:
            raise LegalAIToolInvocationRegistryError("L7B_INPUT_INVALID")
        try: row = self._collection.find_one({"tenant_id": tenant_id, "invocation_id": invocation_id}, session=session)
        except PyMongoError as error: raise LegalAIToolInvocationRegistryError("L7B_PERSISTENCE_UNAVAILABLE") from error
        if not isinstance(row, Mapping): raise LegalAIToolInvocationRegistryError("L7B_NOT_FOUND")
        try: return LegalAIToolInvocationEvidence.from_dict(_canonical_domain_document(row))
        except (LegalAIToolGatewayError, TypeError, KeyError) as error: raise LegalAIToolInvocationRegistryError("L7B_CORRUPT_EVIDENCE") from error


__all__ = ["VERSION", "COLLECTION", "WRITE_CONCERN", "READ_CONCERN", "ensure_indexes", "LegalAIToolInvocationRegistry", "LegalAIToolInvocationRegistryError", "LegalAIToolInvocationConflictError"]
# ARTIFACT: legal_ai_tool_invocation_registry.py
# VERSION: v1.1.0-L7B-WILSY-AI-LEGAL-TOOL-INVOCATION-REGISTRY
# AUTHORITY BOUNDARY: append-only invocation evidence persistence only
# TENANT POSTURE: exact tenant predicates; foreign absence is bounded
# FAIL-CLOSED POSTURE: corruption and divergence reject
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively
# END OF WILSY OS SOVEREIGN ARTIFACT
