"""WILSY OS Legal Evidence provider-delete execution-evidence registry.

TITLE: Legal Evidence Provider Delete Execution Evidence Registry
VERSION: v1.0.1-L10A2R-A3-P4-P5B-PROVIDER-DELETE-EXECUTION-EVIDENCE-REGISTRY-GOVERNANCE
AUTHORITY: Wilsy OS Core Governance / Python EOS Legal Operations
EPITOME:
    Immutable tenant-scoped Mongo persistence for provider-delete execution
    evidence with exact replay, corruption rejection and caller-owned
    transaction scope.
ABSOLUTE CANONICAL PATH:
    /Users/wilsonkhanyezi/legal-doc-system/tools/eos/legal_operations/registry/legal_evidence_provider_delete_execution_evidence_registry.py
COLLABORATION / OWNERSHIP:
    Python EOS Legal Operations owns registry persistence semantics. The
    execution-evidence domain owns serialized document schema and fingerprint
    integrity. Callers own transaction lifecycle and whole-transaction retry.
CERTIFICATION OR UPDATE DATE: 2026-10-03
CHANGELOG:
    v1.0.1-L10A2R-A3-P4-P5B-PROVIDER-DELETE-EXECUTION-EVIDENCE-REGISTRY-GOVERNANCE repairs sovereign source governance metadata and the
    mandatory end seal only. Executable module VERSION remains
    v1.0.0-L10A2R-A3-P4-P5B-PROVIDER-DELETE-EXECUTION-EVIDENCE-REGISTRY; collection identity, indexes, reads, writes, replay,
    transaction boundaries, exception behavior and domain hydration are unchanged.
    v1.0.0-L10A2R-A3-P4-P5B-PROVIDER-DELETE-EXECUTION-EVIDENCE-REGISTRY establishes the immutable execution-evidence registry.
COMPLIANCE:
    WILSY OS sovereign Legal Operations governance; caller-owned active Mongo
    transactions; exact tenant isolation; immutable replay; no TTL deletion.
SECURITY / PRIVACY POSTURE:
    Tenant-scoped durable execution evidence only. Persisted bytes are validated
    by the execution-evidence domain on hydration; corrupt evidence fails closed.
TENANT BOUNDARY:
    Every lookup and durable identity key includes exact tenant scope. Cross-
    tenant reads remain absent and disclose no foreign execution evidence.
AUTHORITY BOUNDARY:
    Persistence authority for provider-delete execution evidence only. No
    provider execution, cleanup authorization, provider retry, reconciliation,
    physical-absence, IAM, billing, payment or settlement authority.
FINANCIAL AUTHORITY BOUNDARY:
    None. Provider-delete execution-evidence persistence is not financial
    execution or settlement; Kennel EOS remains the exclusive financial
    execution authority.

EXECUTABLE MODULE VERSION:
    v1.0.0-L10A2R-A3-P4-P5B-PROVIDER-DELETE-EXECUTION-EVIDENCE-REGISTRY

TRANSACTION BOUNDARY:
    Caller supplies one active Mongo transaction. Duplicate-key or transient
    transaction failure requires caller abort and a fresh whole-transaction
    restart; database retry never authorizes a provider retry.

DURABLE DOCUMENT AUTHORITY:
    LegalEvidenceProviderDeleteExecutionEvidence owns serialization, SCHEMA
    validation and cryptographic fingerprint integrity. Its executable VERSION
    is source identity metadata and is not persisted in durable evidence.
"""

from __future__ import annotations

from copy import deepcopy
from typing import Any, Final

from pymongo import ASCENDING
from pymongo.errors import DuplicateKeyError, PyMongoError

from tools.eos.legal_operations.domain.legal_evidence_provider_delete_execution_evidence import (
    LegalEvidenceProviderDeleteExecutionEvidence,
    LegalEvidenceProviderDeleteExecutionEvidenceError,
)


VERSION: Final[str] = (
    "v1.0.0-L10A2R-A3-P4-P5B-"
    "PROVIDER-DELETE-EXECUTION-EVIDENCE-REGISTRY"
)
COLLECTION: Final[str] = (
    "legal_evidence_provider_delete_execution_evidence"
)

INDEX_TENANT_EXECUTION_EVIDENCE_ID: Final[str] = (
    "legal_evidence_provider_delete_execution_evidence_tenant_id_unique"
)
INDEX_TENANT_FINGERPRINT: Final[str] = (
    "legal_evidence_provider_delete_execution_evidence_tenant_fingerprint_unique"
)
INDEX_TENANT_COMMAND: Final[str] = (
    "legal_evidence_provider_delete_execution_evidence_tenant_command_unique"
)
INDEX_TENANT_PROVIDER_OBJECT: Final[str] = (
    "legal_evidence_provider_delete_execution_evidence_tenant_provider_object_unique"
)


class LegalEvidenceProviderDeleteExecutionEvidenceRegistryError(RuntimeError):
    """Base stable registry failure."""


class LegalEvidenceProviderDeleteExecutionEvidenceRegistryTransactionError(
    LegalEvidenceProviderDeleteExecutionEvidenceRegistryError
):
    """Caller did not supply one active Mongo transaction."""


class LegalEvidenceProviderDeleteExecutionEvidenceRegistryIntegrityError(
    LegalEvidenceProviderDeleteExecutionEvidenceRegistryError
):
    """Durable evidence is corrupt or conflicts with immutable identity."""


class LegalEvidenceProviderDeleteExecutionEvidenceRegistryRetryRequiredError(
    LegalEvidenceProviderDeleteExecutionEvidenceRegistryError
):
    """Concurrent duplicate requires caller abort and fresh transaction retry."""


class LegalEvidenceProviderDeleteExecutionEvidenceRegistryPersistenceError(
    LegalEvidenceProviderDeleteExecutionEvidenceRegistryError
):
    """Unexpected persistence failure."""


def _active_transaction(session: object | None) -> bool:
    if session is None:
        return False
    marker = getattr(session, "in_transaction", False)
    if callable(marker):
        try:
            return bool(marker())
        except Exception:
            return False
    return bool(marker)


def _require_transaction(session: object | None) -> object:
    if not _active_transaction(session):
        raise LegalEvidenceProviderDeleteExecutionEvidenceRegistryTransactionError(
            "L10A2R_A3_P4_P5B_ACTIVE_TRANSACTION_REQUIRED"
        )
    return session


def _hydrate(
    document: dict[str, object] | None,
) -> LegalEvidenceProviderDeleteExecutionEvidence | None:
    if document is None:
        return None

    payload = deepcopy(document)
    payload.pop("_id", None)

    try:
        return LegalEvidenceProviderDeleteExecutionEvidence.from_document(
            payload
        )
    except LegalEvidenceProviderDeleteExecutionEvidenceError as error:
        raise LegalEvidenceProviderDeleteExecutionEvidenceRegistryIntegrityError(
            "L10A2R_A3_P4_P5B_PERSISTED_DOCUMENT_CORRUPT"
        ) from error


def _same(
    left: LegalEvidenceProviderDeleteExecutionEvidence,
    right: LegalEvidenceProviderDeleteExecutionEvidence,
) -> bool:
    return left == right and left.fingerprint == right.fingerprint


class LegalEvidenceProviderDeleteExecutionEvidenceRegistry:
    """Immutable tenant-scoped provider-delete execution-evidence persistence."""

    def __init__(self, collection: Any) -> None:
        self._collection = collection

    def ensure_indexes(self) -> None:
        self._collection.create_index(
            [("tenant_id", ASCENDING), ("execution_evidence_id", ASCENDING)],
            name=INDEX_TENANT_EXECUTION_EVIDENCE_ID,
            unique=True,
        )
        self._collection.create_index(
            [("tenant_id", ASCENDING), ("fingerprint", ASCENDING)],
            name=INDEX_TENANT_FINGERPRINT,
            unique=True,
        )
        self._collection.create_index(
            [("tenant_id", ASCENDING), ("command_id", ASCENDING)],
            name=INDEX_TENANT_COMMAND,
            unique=True,
        )
        self._collection.create_index(
            [
                ("tenant_id", ASCENDING),
                ("provider_name", ASCENDING),
                ("storage_reference", ASCENDING),
                ("object_version_reference", ASCENDING),
            ],
            name=INDEX_TENANT_PROVIDER_OBJECT,
            unique=True,
        )

    def get_by_execution_evidence_id(
        self,
        *,
        tenant_id: str,
        execution_evidence_id: str,
        session: object,
    ) -> LegalEvidenceProviderDeleteExecutionEvidence | None:
        _require_transaction(session)
        try:
            return _hydrate(
                self._collection.find_one(
                    {
                        "tenant_id": tenant_id,
                        "execution_evidence_id": execution_evidence_id,
                    },
                    session=session,
                )
            )
        except LegalEvidenceProviderDeleteExecutionEvidenceRegistryError:
            raise
        except PyMongoError as error:
            raise LegalEvidenceProviderDeleteExecutionEvidenceRegistryPersistenceError(
                "L10A2R_A3_P4_P5B_READ_FAILED"
            ) from error

    def get_by_fingerprint(
        self,
        *,
        tenant_id: str,
        fingerprint: str,
        session: object,
    ) -> LegalEvidenceProviderDeleteExecutionEvidence | None:
        _require_transaction(session)
        try:
            return _hydrate(
                self._collection.find_one(
                    {
                        "tenant_id": tenant_id,
                        "fingerprint": fingerprint,
                    },
                    session=session,
                )
            )
        except LegalEvidenceProviderDeleteExecutionEvidenceRegistryError:
            raise
        except PyMongoError as error:
            raise LegalEvidenceProviderDeleteExecutionEvidenceRegistryPersistenceError(
                "L10A2R_A3_P4_P5B_READ_FAILED"
            ) from error

    def get_by_command_id(
        self,
        *,
        tenant_id: str,
        command_id: str,
        session: object,
    ) -> LegalEvidenceProviderDeleteExecutionEvidence | None:
        _require_transaction(session)
        try:
            return _hydrate(
                self._collection.find_one(
                    {
                        "tenant_id": tenant_id,
                        "command_id": command_id,
                    },
                    session=session,
                )
            )
        except LegalEvidenceProviderDeleteExecutionEvidenceRegistryError:
            raise
        except PyMongoError as error:
            raise LegalEvidenceProviderDeleteExecutionEvidenceRegistryPersistenceError(
                "L10A2R_A3_P4_P5B_READ_FAILED"
            ) from error

    def get_by_provider_object(
        self,
        *,
        tenant_id: str,
        provider_name: str,
        storage_reference: str,
        object_version_reference: str,
        session: object,
    ) -> LegalEvidenceProviderDeleteExecutionEvidence | None:
        _require_transaction(session)
        try:
            return _hydrate(
                self._collection.find_one(
                    {
                        "tenant_id": tenant_id,
                        "provider_name": provider_name,
                        "storage_reference": storage_reference,
                        "object_version_reference": object_version_reference,
                    },
                    session=session,
                )
            )
        except LegalEvidenceProviderDeleteExecutionEvidenceRegistryError:
            raise
        except PyMongoError as error:
            raise LegalEvidenceProviderDeleteExecutionEvidenceRegistryPersistenceError(
                "L10A2R_A3_P4_P5B_READ_FAILED"
            ) from error

    def create_or_replay(
        self,
        value: LegalEvidenceProviderDeleteExecutionEvidence,
        *,
        session: object,
    ) -> LegalEvidenceProviderDeleteExecutionEvidence:
        _require_transaction(session)

        if type(value) is not LegalEvidenceProviderDeleteExecutionEvidence:
            raise LegalEvidenceProviderDeleteExecutionEvidenceRegistryIntegrityError(
                "L10A2R_A3_P4_P5B_EXECUTION_EVIDENCE_REQUIRED"
            )

        lookups = (
            self.get_by_execution_evidence_id(
                tenant_id=value.tenant_id,
                execution_evidence_id=value.execution_evidence_id,
                session=session,
            ),
            self.get_by_fingerprint(
                tenant_id=value.tenant_id,
                fingerprint=value.fingerprint,
                session=session,
            ),
            self.get_by_command_id(
                tenant_id=value.tenant_id,
                command_id=value.command_id,
                session=session,
            ),
            self.get_by_provider_object(
                tenant_id=value.tenant_id,
                provider_name=value.provider_name,
                storage_reference=value.storage_reference,
                object_version_reference=value.object_version_reference,
                session=session,
            ),
        )

        present = [item for item in lookups if item is not None]

        if present:
            if not all(_same(item, value) for item in present):
                raise LegalEvidenceProviderDeleteExecutionEvidenceRegistryIntegrityError(
                    "L10A2R_A3_P4_P5B_REPLAY_CONFLICT"
                )
            if len(present) != len(lookups):
                raise LegalEvidenceProviderDeleteExecutionEvidenceRegistryIntegrityError(
                    "L10A2R_A3_P4_P5B_DURABLE_IDENTITY_CONFLICT"
                )
            return value

        try:
            self._collection.insert_one(
                value.to_document(),
                session=session,
            )
            return value
        except DuplicateKeyError as error:
            raise LegalEvidenceProviderDeleteExecutionEvidenceRegistryRetryRequiredError(
                "L10A2R_A3_P4_P5B_WHOLE_TRANSACTION_RETRY_REQUIRED"
            ) from error
        except PyMongoError as error:
            if getattr(error, "has_error_label", lambda _x: False)(
                "TransientTransactionError"
            ):
                raise LegalEvidenceProviderDeleteExecutionEvidenceRegistryRetryRequiredError(
                    "L10A2R_A3_P4_P5B_WHOLE_TRANSACTION_RETRY_REQUIRED"
                ) from error
            raise LegalEvidenceProviderDeleteExecutionEvidenceRegistryPersistenceError(
                "L10A2R_A3_P4_P5B_WRITE_FAILED"
            ) from error

# =============================================================================
# WILSY OS SOVEREIGN ARTIFACT SEAL
# =============================================================================
# ARTIFACT: legal_evidence_provider_delete_execution_evidence_registry.py
# VERSION: v1.0.1-L10A2R-A3-P4-P5B-PROVIDER-DELETE-EXECUTION-EVIDENCE-REGISTRY-GOVERNANCE
# AUTHORITY BOUNDARY: tenant-scoped durable execution-evidence persistence only; no provider execution, provider retry, reconciliation, physical-absence, IAM, billing, payment or settlement authority
# TENANT POSTURE: every durable identity and lookup remains exact-tenant scoped; cross-tenant reads are absent
# FAIL-CLOSED POSTURE: inactive transaction, malformed domain value, corrupt persisted bytes, divergent replay and persistence failure reject
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively
# EXECUTABLE MODULE VERSION: v1.0.0-L10A2R-A3-P4-P5B-PROVIDER-DELETE-EXECUTION-EVIDENCE-REGISTRY
# DURABLE DOCUMENT AUTHORITY: LegalEvidenceProviderDeleteExecutionEvidence
# END OF WILSY OS SOVEREIGN ARTIFACT
