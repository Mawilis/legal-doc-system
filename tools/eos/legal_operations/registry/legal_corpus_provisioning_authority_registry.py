"""Append-only registry for legal-corpus provisioning authority evidence.

TITLE: WILSY OS Legal Corpus Provisioning Authority Evidence Registry
VERSION: v1.1.0-R9B-P7-A2-R1-LEGAL-CORPUS-PROVISIONING-AUTHORITY-REGISTRY
AUTHORITY: Wilsy OS Core Governance
EPITOME: Durably admits and replays immutable PLATFORM draft-admission
         authority evidence without issuing authority or persisting a document.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tools/eos/legal_operations/registry/legal_corpus_provisioning_authority_registry.py
COLLABORATION / OWNERSHIP: The future governed provisioning service supplies
                            already-issued R8D evidence; callers own sessions,
                            transactions, commit/abort, and whole-transaction
                            retry boundaries.
CERTIFICATION / UPDATE DATE: 2026-09-17
CHANGELOG: v1.1.0-R9B-P7-A2-R1 reconciles the reusable R8F candidate into the
           tracked multi-document provisioning path without changing its
           immutable persistence or caller-owned transaction semantics.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2.
SECURITY / PRIVACY POSTURE: Only bounded authority metadata is persisted; no
                            secrets, request context, or caller dictionaries
                            are accepted as authority evidence.
TENANT BOUNDARY: This registry is PLATFORM-scoped institutional evidence;
                 tenant/principal acceptance remains a separate authority
                 plane and is never inferred here.
AUTHORITY BOUNDARY: Persists evidence that was already issued elsewhere; it
                    does not authenticate actors, admit documents, review,
                    approve, accept, sign, or promote legal status.
FINANCIAL AUTHORITY BOUNDARY: None; Kennel EOS remains exclusive for financial
                              execution and settlement truth.
TRANSACTION BOUNDARY: Every read/write forwards the caller session. This
                      registry never creates clients/sessions, starts or ends
                      transactions, retries, or interprets commit outcomes.
FAIL-CLOSED POSTURE: Corrupt persistence, duplicate ambiguity, and semantic
                     divergence are bounded errors, never successful replay.
"""
from __future__ import annotations

from copy import deepcopy
from datetime import datetime, timezone
from typing import Any, Final

from pymongo.errors import DuplicateKeyError, PyMongoError

from tools.eos.kernel import db as kernel_db
from tools.eos.legal_operations.domain.legal_corpus_provisioning_authority import (
    AUTHORITY_SCOPE,
    AUTHORIZED_OPERATION,
    LegalCorpusProvisioningAuthorityError,
    LegalCorpusProvisioningAuthorityEvidence,
    LegalCorpusProvisioningAuthorityScope,
    LegalCorpusProvisioningAuthoritySource,
    LegalCorpusProvisioningOperation,
)
from tools.eos.legal_operations.domain.legal_acceptance import (
    LegalAgreementType,
    LegalDocumentStatus,
)


VERSION: Final[str] = "v1.1.0-R9B-P7-A2-R1-LEGAL-CORPUS-PROVISIONING-AUTHORITY-REGISTRY"
COLLECTION: Final[str] = "legal_corpus_provisioning_authority_evidence"

_PERSISTED_FIELDS: Final[frozenset[str]] = frozenset(
    {
        "authority_evidence_id",
        "scope",
        "operation",
        "source_document_id",
        "source_agreement_type",
        "source_version",
        "source_status",
        "source_content_reference",
        "source_sha3_512",
        "authority_source_id",
        "authority_source_version",
        "actor_representation",
        "authorized_at",
        "idempotency_key",
        "evidence_fingerprint",
    }
)


class LegalCorpusProvisioningAuthorityRegistryError(RuntimeError):
    """Stable, non-sensitive failure for registry input or persistence."""

    def __init__(self, code: str) -> None:
        self.code = code
        super().__init__(code)


def _target(collection: Any = None) -> Any:
    """Resolve an explicit collection or the canonical Kernel DB collection."""
    if collection is not None:
        return collection
    database = kernel_db.get_database()
    if database is None:
        raise LegalCorpusProvisioningAuthorityRegistryError(
            "LEGAL_CORPUS_PROVISIONING_AUTHORITY_DATABASE_UNAVAILABLE"
        )
    return database[COLLECTION]


def _parse_timestamp(value: Any) -> datetime:
    """Parse an aware persisted timestamp and normalize it to UTC."""
    if not isinstance(value, str):
        raise LegalCorpusProvisioningAuthorityRegistryError(
            "LEGAL_CORPUS_PROVISIONING_AUTHORITY_PERSISTED_INVALID"
        )
    try:
        parsed = datetime.fromisoformat(value)
    except ValueError as error:
        raise LegalCorpusProvisioningAuthorityRegistryError(
            "LEGAL_CORPUS_PROVISIONING_AUTHORITY_PERSISTED_INVALID"
        ) from error
    if parsed.tzinfo is None or parsed.utcoffset() is None:
        raise LegalCorpusProvisioningAuthorityRegistryError(
            "LEGAL_CORPUS_PROVISIONING_AUTHORITY_PERSISTED_INVALID"
        )
    return parsed.astimezone(timezone.utc)


def _hydrate(row: Any) -> LegalCorpusProvisioningAuthorityEvidence:
    """Reconstruct and revalidate one complete canonical evidence value."""
    if not isinstance(row, dict) or set(row) - _PERSISTED_FIELDS - {"_id"}:
        raise LegalCorpusProvisioningAuthorityRegistryError(
            "LEGAL_CORPUS_PROVISIONING_AUTHORITY_PERSISTED_INVALID"
        )
    try:
        return LegalCorpusProvisioningAuthorityEvidence(
            authority_evidence_id=row["authority_evidence_id"],
            scope=LegalCorpusProvisioningAuthorityScope(row["scope"]),
            operation=LegalCorpusProvisioningOperation(row["operation"]),
            source_document_id=row["source_document_id"],
            source_agreement_type=LegalAgreementType(row["source_agreement_type"]),
            source_version=row["source_version"],
            source_status=LegalDocumentStatus(row["source_status"]),
            source_content_reference=row["source_content_reference"],
            source_sha3_512=row["source_sha3_512"],
            authority_source_id=LegalCorpusProvisioningAuthoritySource(
                row["authority_source_id"]
            ),
            authority_source_version=row["authority_source_version"],
            actor_representation=row["actor_representation"],
            authorized_at=_parse_timestamp(row["authorized_at"]),
            idempotency_key=row["idempotency_key"],
            evidence_fingerprint=row["evidence_fingerprint"],
        )
    except (
        KeyError,
        TypeError,
        ValueError,
        LegalCorpusProvisioningAuthorityError,
        OverflowError,
    ) as error:
        raise LegalCorpusProvisioningAuthorityRegistryError(
            "LEGAL_CORPUS_PROVISIONING_AUTHORITY_PERSISTED_INVALID"
        ) from error


def _canonical_row(row: Any) -> dict[str, str]:
    """Return the validated semantic payload, excluding Mongo ``_id`` metadata."""
    return _hydrate(row).to_document()


def _read_one(source: Any, query: dict[str, Any], session: Any) -> Any:
    """Read one row with caller session forwarding and bounded errors."""
    try:
        return source.find_one(query, session=session)
    except PyMongoError as error:
        raise LegalCorpusProvisioningAuthorityRegistryError(
            "LEGAL_CORPUS_PROVISIONING_AUTHORITY_READ_FAILED"
        ) from error


class LegalCorpusProvisioningAuthorityRegistry:
    """Persist immutable PLATFORM draft-admission evidence only.

    The class deliberately has no update, delete, replace, transaction, or
    authority-issuing method. A caller supplies an R8D evidence value and
    owns the surrounding Mongo transaction lifecycle.
    """

    @staticmethod
    def ensure_indexes(collection: Any = None) -> None:
        """Create deterministic uniqueness constraints for the evidence stream."""
        source = _target(collection)
        source.create_index(
            [("authority_evidence_id", 1)],
            unique=True,
            name="legal_corpus_provisioning_authority_evidence_id_unique",
        )
        source.create_index(
            [
                ("scope", 1),
                ("operation", 1),
                ("source_document_id", 1),
                ("source_version", 1),
            ],
            unique=True,
            name="legal_corpus_provisioning_authority_source_version_unique",
        )
        source.create_index(
            [("scope", 1), ("operation", 1), ("idempotency_key", 1)],
            unique=True,
            name="legal_corpus_provisioning_authority_idempotency_unique",
        )

    @staticmethod
    def create_or_replay(
        evidence: LegalCorpusProvisioningAuthorityEvidence,
        collection: Any = None,
        *,
        session: Any = None,
    ) -> LegalCorpusProvisioningAuthorityEvidence:
        """Insert evidence once or replay the exact immutable row.

        The input must be the canonical R8D value, never a raw mapping. Any
        uniqueness collision is adjudicated across evidence identity, source
        identity, and idempotency identity; semantic divergence fails closed.
        Mongo ``_id`` is excluded from comparison because it is driver metadata,
        not authority evidence.
        """
        if not isinstance(evidence, LegalCorpusProvisioningAuthorityEvidence):
            raise LegalCorpusProvisioningAuthorityRegistryError(
                "LEGAL_CORPUS_PROVISIONING_AUTHORITY_CREATE_INVALID"
            )
        source = _target(collection)
        canonical_payload = evidence.to_document()
        insert_payload = deepcopy(canonical_payload)
        try:
            source.insert_one(insert_payload, session=session)
            return evidence
        except DuplicateKeyError as error:
            queries = (
                {"authority_evidence_id": evidence.authority_evidence_id},
                {
                    "scope": AUTHORITY_SCOPE,
                    "operation": AUTHORIZED_OPERATION,
                    "source_document_id": evidence.source_document_id,
                    "source_version": evidence.source_version,
                },
                {
                    "scope": AUTHORITY_SCOPE,
                    "operation": AUTHORIZED_OPERATION,
                    "idempotency_key": evidence.idempotency_key,
                },
            )
            existing = None
            for query in queries:
                existing = _read_one(source, query, session)
                if existing is not None:
                    break
            if existing is None:
                raise LegalCorpusProvisioningAuthorityRegistryError(
                    "LEGAL_CORPUS_PROVISIONING_AUTHORITY_DUPLICATE_UNAVAILABLE"
                ) from error
            try:
                persisted_payload = _canonical_row(existing)
            except LegalCorpusProvisioningAuthorityRegistryError as hydration_error:
                raise hydration_error from error
            if persisted_payload != canonical_payload:
                raise LegalCorpusProvisioningAuthorityRegistryError(
                    "LEGAL_CORPUS_PROVISIONING_AUTHORITY_IMMUTABILITY_CONFLICT"
                ) from error
            return _hydrate(existing)
        except PyMongoError as error:
            raise LegalCorpusProvisioningAuthorityRegistryError(
                "LEGAL_CORPUS_PROVISIONING_AUTHORITY_CREATE_FAILED"
            ) from error

    @staticmethod
    def get(
        authority_evidence_id: str,
        collection: Any = None,
        *,
        session: Any = None,
    ) -> LegalCorpusProvisioningAuthorityEvidence | None:
        """Read one evidence value by its immutable authority evidence ID."""
        if not isinstance(authority_evidence_id, str) or not authority_evidence_id.strip():
            raise LegalCorpusProvisioningAuthorityRegistryError(
                "LEGAL_CORPUS_PROVISIONING_AUTHORITY_REFERENCE_INVALID"
            )
        row = _read_one(
            _target(collection),
            {"authority_evidence_id": authority_evidence_id.strip()},
            session,
        )
        return _hydrate(row) if row is not None else None

    @staticmethod
    def get_by_source(
        source_document_id: str,
        source_version: str,
        collection: Any = None,
        *,
        session: Any = None,
    ) -> LegalCorpusProvisioningAuthorityEvidence | None:
        """Read one PLATFORM draft-admission event by canonical source identity."""
        if (
            not isinstance(source_document_id, str)
            or not source_document_id.strip()
            or not isinstance(source_version, str)
            or not source_version.strip()
        ):
            raise LegalCorpusProvisioningAuthorityRegistryError(
                "LEGAL_CORPUS_PROVISIONING_AUTHORITY_SOURCE_REFERENCE_INVALID"
            )
        row = _read_one(
            _target(collection),
            {
                "scope": AUTHORITY_SCOPE,
                "operation": AUTHORIZED_OPERATION,
                "source_document_id": source_document_id.strip(),
                "source_version": source_version.strip(),
            },
            session,
        )
        return _hydrate(row) if row is not None else None


__all__ = [
    "COLLECTION",
    "LegalCorpusProvisioningAuthorityRegistry",
    "LegalCorpusProvisioningAuthorityRegistryError",
    "VERSION",
]


# ARTIFACT: legal_corpus_provisioning_authority_registry.py
# VERSION: v1.1.0-R9B-P7-A2-R1-LEGAL-CORPUS-PROVISIONING-AUTHORITY-REGISTRY
# AUTHORITY BOUNDARY: append-only PLATFORM authority-evidence persistence only
# TENANT POSTURE: platform-scoped corpus evidence; tenant acceptance is separate
# FAIL-CLOSED POSTURE: corrupt rows and divergent collisions are rejected
# FINANCIAL EXECUTION AUTHORITY: none; Kennel EOS remains exclusive
# END OF WILSY OS SOVEREIGN ARTIFACT
