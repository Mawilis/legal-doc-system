"""Append-only durable legal-acceptance evidence registry.

TITLE: WILSY OS Legal Acceptance Evidence Registry
VERSION: v1.0.0-R1D-B0F-B4-PRODUCTION-LEGAL-ACCEPTANCE
AUTHORITY: Wilsy OS Core Governance
EPITOME: Stores immutable, tenant/principal-scoped acceptance evidence and
         performs deterministic replay/divergence adjudication.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tools/eos/legal_operations/registry/legal_acceptance_registry.py
COLLABORATION / OWNERSHIP: LegalAcceptanceService supplies authenticated
                            context; callers own Mongo transactions and retries.
CERTIFICATION / UPDATE DATE: 2026-09-17
CHANGELOG: v1.0.0 establishes append-only acceptance persistence, unique
           identity indexes, and idempotent replay with fail-closed divergence.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2.
SECURITY / PRIVACY POSTURE: Caller tenant/principal are verified context, not
                            body authority; evidence never stores secrets.
TENANT BOUNDARY: Every predicate includes tenant_id and principal_id.
AUTHORITY BOUNDARY: Acceptance evidence only; no organisation-binding authority.
FINANCIAL AUTHORITY BOUNDARY: None; Kennel EOS remains exclusive.
"""
from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Final

from pymongo.errors import DuplicateKeyError, PyMongoError

from tools.eos.kernel import db as kernel_db
from tools.eos.legal_operations.domain.legal_acceptance import (
    AcceptanceMethod,
    LegalAcceptanceEvidence,
    LegalAcceptanceError,
    LegalAgreementType,
)


VERSION: Final[str] = "v1.0.0-R1D-B0F-B4-PRODUCTION-LEGAL-ACCEPTANCE"
COLLECTION: Final[str] = "legal_acceptance_evidence"


class LegalAcceptanceRegistryError(RuntimeError):
    """Bounded acceptance persistence, replay, or hydration failure."""


def _target(collection: Any = None) -> Any:
    if collection is not None:
        return collection
    database = kernel_db.get_database()
    if database is None:
        raise LegalAcceptanceRegistryError("LEGAL_ACCEPTANCE_DATABASE_UNAVAILABLE")
    return database[COLLECTION]


def _parse(value: Any) -> datetime:
    if not isinstance(value, str):
        raise LegalAcceptanceRegistryError("LEGAL_ACCEPTANCE_PERSISTED_INVALID")
    try:
        result = datetime.fromisoformat(value)
    except ValueError as error:
        raise LegalAcceptanceRegistryError("LEGAL_ACCEPTANCE_PERSISTED_INVALID") from error
    if result.tzinfo is None or result.utcoffset() is None:
        raise LegalAcceptanceRegistryError("LEGAL_ACCEPTANCE_PERSISTED_INVALID")
    return result.astimezone(timezone.utc)


def _hydrate(row: Any) -> LegalAcceptanceEvidence:
    if not isinstance(row, dict):
        raise LegalAcceptanceRegistryError("LEGAL_ACCEPTANCE_PERSISTED_INVALID")
    try:
        return LegalAcceptanceEvidence(
            acceptance_id=row["acceptance_id"], tenant_id=row["tenant_id"],
            principal_id=row["principal_id"], agreement_type=LegalAgreementType(row["agreement_type"]),
            document_id=row["document_id"], document_version=row["document_version"],
            document_sha3_512=row["document_sha3_512"], accepted_at=_parse(row["accepted_at"]),
            acceptance_method=AcceptanceMethod(row["acceptance_method"]),
            actor_role_at_acceptance=row["actor_role_at_acceptance"],
            session_id=row["session_id"], locale=row["locale"],
            authority_representation=row["authority_representation"],
            evidence_fingerprint=row["evidence_fingerprint"],
            supersedes_acceptance_id=row.get("supersedes_acceptance_id"),
            idempotency_key=row.get("idempotency_key"),
        )
    except (KeyError, TypeError, ValueError, LegalAcceptanceError) as error:
        raise LegalAcceptanceRegistryError("LEGAL_ACCEPTANCE_PERSISTED_INVALID") from error


class LegalAcceptanceRegistry:
    """Own append-only acceptance evidence, never update/delete semantics."""

    @staticmethod
    def ensure_indexes(collection: Any = None) -> None:
        """Create deterministic uniqueness constraints for replay safety."""
        source = _target(collection)
        source.create_index([("tenant_id", 1), ("principal_id", 1), ("agreement_type", 1), ("document_id", 1), ("document_version", 1)], unique=True, name="legal_acceptance_version_unique")
        source.create_index([("tenant_id", 1), ("principal_id", 1), ("idempotency_key", 1)], unique=True, sparse=True, name="legal_acceptance_idempotency_unique")

    @staticmethod
    def create_or_replay(evidence: LegalAcceptanceEvidence, collection: Any = None, *, idempotency_key: str | None = None, session: Any = None) -> LegalAcceptanceEvidence:
        """Append evidence, replaying identical identity and rejecting divergence."""
        if not isinstance(evidence, LegalAcceptanceEvidence):
            raise LegalAcceptanceRegistryError("LEGAL_ACCEPTANCE_CREATE_INVALID")
        key = idempotency_key or evidence.idempotency_key
        if key is not None and (not isinstance(key, str) or not key.strip()):
            raise LegalAcceptanceRegistryError("LEGAL_ACCEPTANCE_IDEMPOTENCY_INVALID")
        source = _target(collection)
        payload = evidence.to_document()
        if key is not None:
            payload["idempotency_key"] = key
        query = {"tenant_id": evidence.tenant_id, "principal_id": evidence.principal_id, "agreement_type": evidence.agreement_type.value, "document_id": evidence.document_id, "document_version": evidence.document_version}
        try:
            source.insert_one(payload, session=session)
            return evidence
        except DuplicateKeyError as error:
            existing = source.find_one(query, session=session)
            if existing is None and key is not None:
                existing = source.find_one({"tenant_id": evidence.tenant_id, "principal_id": evidence.principal_id, "idempotency_key": key}, session=session)
            if existing is None:
                raise LegalAcceptanceRegistryError("LEGAL_ACCEPTANCE_DUPLICATE_UNAVAILABLE") from error
            current = _hydrate(existing)
            if current.evidence_fingerprint != evidence.evidence_fingerprint:
                raise LegalAcceptanceRegistryError("LEGAL_ACCEPTANCE_IDEMPOTENCY_CONFLICT") from error
            return current
        except PyMongoError as error:
            raise LegalAcceptanceRegistryError("LEGAL_ACCEPTANCE_CREATE_FAILED") from error

    @staticmethod
    def list_for_principal(tenant_id: str, principal_id: str, collection: Any = None, *, session: Any = None) -> tuple[LegalAcceptanceEvidence, ...]:
        """Read only the authenticated tenant/principal acceptance stream."""
        if not isinstance(tenant_id, str) or not isinstance(principal_id, str) or not tenant_id.strip() or not principal_id.strip():
            raise LegalAcceptanceRegistryError("LEGAL_ACCEPTANCE_SCOPE_INVALID")
        try:
            rows = _target(collection).find({"tenant_id": tenant_id, "principal_id": principal_id}, session=session)
            return tuple(_hydrate(row) for row in rows)
        except PyMongoError as error:
            raise LegalAcceptanceRegistryError("LEGAL_ACCEPTANCE_READ_FAILED") from error


__all__ = ["COLLECTION", "LegalAcceptanceRegistry", "LegalAcceptanceRegistryError", "VERSION"]

# ARTIFACT: legal_acceptance_registry.py
# VERSION: v1.0.0-R1D-B0F-B4-PRODUCTION-LEGAL-ACCEPTANCE
# AUTHORITY BOUNDARY: append-only acceptance evidence persistence only
# TENANT POSTURE: every read/write is tenant and principal scoped
# FAIL-CLOSED POSTURE: duplicate identical replay succeeds; divergent replay fails
# FINANCIAL EXECUTION AUTHORITY: none; Kennel EOS remains exclusive
# END OF WILSY OS SOVEREIGN ARTIFACT
