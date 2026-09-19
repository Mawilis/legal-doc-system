"""Append-only registry for approved legal-document versions.

TITLE: WILSY OS Legal Document Version Registry
VERSION: v1.0.1-R1D-B0F-B4-PRODUCTION-LEGAL-ACCEPTANCE
AUTHORITY: Wilsy OS Core Governance
EPITOME: Owns immutable server-selected document/version truth; it never
         confers acceptance, signatory, commercial, or financial authority.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tools/eos/legal_operations/registry/legal_document_registry.py
COLLABORATION / OWNERSHIP: Acceptance policy reads this registry; callers own
                            Mongo sessions, transactions, and retry boundaries.
CERTIFICATION / UPDATE DATE: 2026-09-17
CHANGELOG: v1.0.1 isolates mutable Mongo insert metadata from canonical replay
           comparison while retaining strict immutable version arbitration.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2.
SECURITY / PRIVACY POSTURE: No client-supplied approval status is trusted.
TENANT BOUNDARY: Documents are platform legal artifacts; acceptance is tenant
                 scoped in the separate evidence registry.
AUTHORITY BOUNDARY: Document truth only; approval is metadata, not acceptance.
FINANCIAL AUTHORITY BOUNDARY: None; Kennel EOS remains exclusive.
"""
from __future__ import annotations

from copy import deepcopy
from datetime import datetime, timezone
from typing import Any, Final

from pymongo.errors import DuplicateKeyError, PyMongoError

from tools.eos.kernel import db as kernel_db
from tools.eos.legal_operations.domain.legal_acceptance import (
    LegalAcceptanceError,
    LegalAgreementType,
    LegalDocumentStatus,
    LegalDocumentVersion,
)


VERSION: Final[str] = "v1.0.1-R1D-B0F-B4-PRODUCTION-LEGAL-ACCEPTANCE"
COLLECTION: Final[str] = "legal_document_versions"


class LegalDocumentRegistryError(RuntimeError):
    """Bounded document persistence, immutability, or hydration failure."""


def _target(collection: Any = None) -> Any:
    if collection is not None:
        return collection
    database = kernel_db.get_database()
    if database is None:
        raise LegalDocumentRegistryError("LEGAL_DOCUMENT_DATABASE_UNAVAILABLE")
    return database[COLLECTION]


def _parse(value: Any) -> datetime:
    if not isinstance(value, str):
        raise LegalDocumentRegistryError("LEGAL_DOCUMENT_PERSISTED_INVALID")
    try:
        result = datetime.fromisoformat(value)
    except ValueError as error:
        raise LegalDocumentRegistryError("LEGAL_DOCUMENT_PERSISTED_INVALID") from error
    if result.tzinfo is None or result.utcoffset() is None:
        raise LegalDocumentRegistryError("LEGAL_DOCUMENT_PERSISTED_INVALID")
    return result.astimezone(timezone.utc)


def _hydrate(row: Any) -> LegalDocumentVersion:
    if not isinstance(row, dict):
        raise LegalDocumentRegistryError("LEGAL_DOCUMENT_PERSISTED_INVALID")
    try:
        return LegalDocumentVersion(
            document_id=row["document_id"],
            agreement_type=LegalAgreementType(row["agreement_type"]),
            version=row["version"], title=row["title"],
            jurisdiction=row["jurisdiction"], locale=row["locale"],
            effective_from=_parse(row["effective_from"]),
            status=LegalDocumentStatus(row["status"]),
            content_reference=row["content_reference"], content=row["content"],
            sha3_512=row["sha3_512"], created_at=_parse(row["created_at"]),
            supersedes_document_id=row.get("supersedes_document_id"),
        )
    except (KeyError, ValueError, TypeError, LegalAcceptanceError) as error:
        if isinstance(error, LegalAcceptanceError):
            raise LegalDocumentRegistryError(str(error)) from error
        raise LegalDocumentRegistryError("LEGAL_DOCUMENT_PERSISTED_INVALID") from error


class LegalDocumentRegistry:
    """Persist immutable legal-document versions with caller-owned sessions."""

    @staticmethod
    def ensure_indexes(collection: Any = None) -> None:
        """Create deterministic uniqueness indexes without changing documents."""
        source = _target(collection)
        source.create_index([("document_id", 1), ("version", 1)], unique=True, name="legal_document_version_unique")
        source.create_index([("agreement_type", 1), ("version", 1)], unique=True, name="legal_agreement_version_unique")

    @staticmethod
    def register(document: LegalDocumentVersion, collection: Any = None, *, session: Any = None) -> LegalDocumentVersion:
        """Insert one immutable version or replay the identical existing row."""
        if not isinstance(document, LegalDocumentVersion):
            raise LegalDocumentRegistryError("LEGAL_DOCUMENT_CREATE_INVALID")
        source = _target(collection)
        canonical_payload = document.to_document()
        insert_payload = deepcopy(canonical_payload)
        try:
            source.insert_one(insert_payload, session=session)
            return document
        except DuplicateKeyError as error:
            existing = source.find_one({"document_id": document.document_id, "version": document.version}, session=session)
            if existing is None:
                raise LegalDocumentRegistryError("LEGAL_DOCUMENT_DUPLICATE_UNAVAILABLE") from error
            hydrated = _hydrate(existing)
            persisted_payload = deepcopy(existing)
            persisted_payload.pop("_id", None)
            if persisted_payload != canonical_payload:
                raise LegalDocumentRegistryError("LEGAL_DOCUMENT_VERSION_IMMUTABILITY_CONFLICT") from error
            return hydrated
        except PyMongoError as error:
            raise LegalDocumentRegistryError("LEGAL_DOCUMENT_CREATE_FAILED") from error

    @staticmethod
    def get(document_id: str, version: str | None = None, collection: Any = None, *, session: Any = None) -> LegalDocumentVersion | None:
        """Read one immutable version; absence is distinct from persistence failure."""
        if not isinstance(document_id, str) or not document_id.strip():
            raise LegalDocumentRegistryError("LEGAL_DOCUMENT_REFERENCE_INVALID")
        query: dict[str, Any] = {"document_id": document_id}
        if version is not None:
            query["version"] = version
        try:
            row = _target(collection).find_one(query, session=session)
        except PyMongoError as error:
            raise LegalDocumentRegistryError("LEGAL_DOCUMENT_READ_FAILED") from error
        return _hydrate(row) if row is not None else None

    @staticmethod
    def approved_for(agreement_type: LegalAgreementType, collection: Any = None, *, session: Any = None) -> LegalDocumentVersion | None:
        """Select the latest APPROVED version deterministically, never draft truth."""
        if not isinstance(agreement_type, LegalAgreementType):
            raise LegalDocumentRegistryError("LEGAL_DOCUMENT_AGREEMENT_TYPE_INVALID")
        source = _target(collection)
        try:
            row = source.find_one(
                {"agreement_type": agreement_type.value, "status": LegalDocumentStatus.APPROVED.value},
                sort=[("effective_from", -1), ("version", -1)], session=session,
            )
        except TypeError:
            rows = list(source.find({"agreement_type": agreement_type.value, "status": LegalDocumentStatus.APPROVED.value}, session=session))
            row = sorted(rows, key=lambda item: (item.get("effective_from", ""), item.get("version", "")), reverse=True)[0] if rows else None
        except PyMongoError as error:
            raise LegalDocumentRegistryError("LEGAL_DOCUMENT_READ_FAILED") from error
        return _hydrate(row) if row is not None else None


__all__ = ["COLLECTION", "LegalDocumentRegistry", "LegalDocumentRegistryError", "VERSION"]

# ARTIFACT: legal_document_registry.py
# VERSION: v1.0.1-R1D-B0F-B4-PRODUCTION-LEGAL-ACCEPTANCE
# AUTHORITY BOUNDARY: immutable versioned document persistence only
# TENANT POSTURE: document truth is separate from tenant-scoped acceptance evidence
# FAIL-CLOSED POSTURE: draft/unapproved, corruption, duplicate divergence, and outage reject
# FINANCIAL EXECUTION AUTHORITY: none; Kennel EOS remains exclusive
# END OF WILSY OS SOVEREIGN ARTIFACT
