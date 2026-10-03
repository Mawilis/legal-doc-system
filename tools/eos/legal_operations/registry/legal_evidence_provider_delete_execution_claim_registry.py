"""WILSY OS Legal Evidence provider-delete execution-claim registry.

TITLE: Legal Evidence Provider Delete Execution Claim Registry
VERSION: v1.0.1-L10A2R-A3-P4-P6D3-PROVIDER-DELETE-EXECUTION-CLAIM-REGISTRY-GOVERNANCE
AUTHORITY: Wilsy OS Core Governance / Python EOS Legal Operations
EPITOME:
    Immutable tenant-scoped Mongo persistence for pre-provider execution claims,
    with exact replay, corruption rejection and caller-owned transaction scope.
ABSOLUTE CANONICAL PATH:
    /Users/wilsonkhanyezi/legal-doc-system/tools/eos/legal_operations/registry/legal_evidence_provider_delete_execution_claim_registry.py
COLLABORATION / OWNERSHIP:
    Python EOS Legal Operations owns registry persistence semantics. The claim
    domain owns durable document schema, version validation and fingerprint
    integrity. Callers own transaction lifecycle and whole-transaction retry.
CERTIFICATION OR UPDATE DATE: 2026-10-03
CHANGELOG:
    v1.0.1-L10A2R-A3-P4-P6D3-PROVIDER-DELETE-EXECUTION-CLAIM-REGISTRY-GOVERNANCE repairs sovereign source governance metadata and the
    mandatory end seal only. Executable module VERSION remains
    v1.0.0-L10A2R-A3-P4-P6D3-PROVIDER-DELETE-EXECUTION-CLAIM-REGISTRY; collection identity, indexes, reads, writes, replay,
    transaction boundaries, exception behavior and domain hydration are unchanged.
    v1.0.0-L10A2R-A3-P4-P6D3-PROVIDER-DELETE-EXECUTION-CLAIM-REGISTRY establishes the immutable execution-claim registry.
COMPLIANCE:
    WILSY OS sovereign Legal Operations governance; caller-owned active Mongo
    transactions; exact tenant isolation; immutable replay; no TTL deletion.
SECURITY / PRIVACY POSTURE:
    Tenant-scoped durable claim evidence only. Persisted bytes are validated by
    the claim domain on hydration; corrupt evidence fails closed.
TENANT BOUNDARY:
    Every lookup and durable identity key includes exact tenant scope. Cross-
    tenant reads remain absent and disclose no foreign tenant claim.
AUTHORITY BOUNDARY:
    Persistence authority for execution claims only. No provider execution,
    cleanup authorization, claim release, provider retry, reconciliation,
    physical-absence, IAM, billing, payment or settlement authority.
FINANCIAL AUTHORITY BOUNDARY:
    None. Provider-delete claim persistence is not financial execution or
    settlement; Kennel EOS remains the exclusive financial execution authority.

EXECUTABLE MODULE VERSION:
    v1.0.0-L10A2R-A3-P4-P6D3-PROVIDER-DELETE-EXECUTION-CLAIM-REGISTRY

TRANSACTION BOUNDARY:
    Caller supplies one active Mongo transaction. Duplicate-key or transient
    transaction failure requires caller abort and a fresh whole-transaction
    restart; database retry never authorizes a provider retry.

DURABLE DOCUMENT AUTHORITY:
    LegalEvidenceProviderDeleteExecutionClaim owns serialization, durable VERSION,
    schema validation and cryptographic fingerprint integrity.
"""

from __future__ import annotations

from copy import deepcopy
from typing import Any, Final

from pymongo import ASCENDING
from pymongo.errors import DuplicateKeyError, PyMongoError

from tools.eos.legal_operations.domain.legal_evidence_provider_delete_execution_claim import (
    LegalEvidenceProviderDeleteExecutionClaim,
    LegalEvidenceProviderDeleteExecutionClaimError,
)


VERSION: Final[str] = (
    "v1.0.0-L10A2R-A3-P4-P6D3-"
    "PROVIDER-DELETE-EXECUTION-CLAIM-REGISTRY"
)
COLLECTION: Final[str] = (
    "legal_evidence_provider_delete_execution_claims"
)

INDEX_TENANT_CLAIM_ID: Final[str] = (
    "legal_evidence_provider_delete_claim_tenant_claim_id_unique"
)
INDEX_TENANT_FINGERPRINT: Final[str] = (
    "legal_evidence_provider_delete_claim_tenant_fingerprint_unique"
)
INDEX_TENANT_COMMAND: Final[str] = (
    "legal_evidence_provider_delete_claim_tenant_command_unique"
)
INDEX_TENANT_CLEANUP_AUTHORIZATION: Final[str] = (
    "legal_evidence_provider_delete_claim_tenant_cleanup_authorization_unique"
)
INDEX_TENANT_PROVIDER_OBJECT: Final[str] = (
    "legal_evidence_provider_delete_claim_tenant_provider_object_unique"
)


class LegalEvidenceProviderDeleteExecutionClaimRegistryError(RuntimeError):
    """Base stable execution-claim registry failure."""


class LegalEvidenceProviderDeleteExecutionClaimRegistryTransactionError(
    LegalEvidenceProviderDeleteExecutionClaimRegistryError
):
    """Caller did not provide one active Mongo transaction."""


class LegalEvidenceProviderDeleteExecutionClaimRegistryIntegrityError(
    LegalEvidenceProviderDeleteExecutionClaimRegistryError
):
    """Durable claim is corrupt or conflicts with immutable identity."""


class LegalEvidenceProviderDeleteExecutionClaimRegistryRetryRequiredError(
    LegalEvidenceProviderDeleteExecutionClaimRegistryError
):
    """Caller must abort and restart persistence in a fresh transaction."""


class LegalEvidenceProviderDeleteExecutionClaimRegistryPersistenceError(
    LegalEvidenceProviderDeleteExecutionClaimRegistryError
):
    """Unexpected durable persistence failure."""


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
        raise LegalEvidenceProviderDeleteExecutionClaimRegistryTransactionError(
            "L10A2R_A3_P4_P6D3_ACTIVE_TRANSACTION_REQUIRED"
        )
    return session


def _hydrate(
    document: dict[str, object] | None,
) -> LegalEvidenceProviderDeleteExecutionClaim | None:
    if document is None:
        return None

    payload = deepcopy(document)
    payload.pop("_id", None)

    try:
        return LegalEvidenceProviderDeleteExecutionClaim.from_document(
            payload
        )
    except LegalEvidenceProviderDeleteExecutionClaimError as error:
        raise LegalEvidenceProviderDeleteExecutionClaimRegistryIntegrityError(
            "L10A2R_A3_P4_P6D3_PERSISTED_DOCUMENT_CORRUPT"
        ) from error


def _same(
    left: LegalEvidenceProviderDeleteExecutionClaim,
    right: LegalEvidenceProviderDeleteExecutionClaim,
) -> bool:
    return left == right and left.fingerprint == right.fingerprint


class LegalEvidenceProviderDeleteExecutionClaimRegistry:
    """Immutable tenant-scoped provider-delete execution-claim persistence."""

    def __init__(self, collection: Any) -> None:
        self._collection = collection

    def ensure_indexes(self) -> None:
        self._collection.create_index(
            [
                ("tenant_id", ASCENDING),
                ("claim_id", ASCENDING),
            ],
            name=INDEX_TENANT_CLAIM_ID,
            unique=True,
        )
        self._collection.create_index(
            [
                ("tenant_id", ASCENDING),
                ("fingerprint", ASCENDING),
            ],
            name=INDEX_TENANT_FINGERPRINT,
            unique=True,
        )
        self._collection.create_index(
            [
                ("tenant_id", ASCENDING),
                ("command_id", ASCENDING),
            ],
            name=INDEX_TENANT_COMMAND,
            unique=True,
        )
        self._collection.create_index(
            [
                ("tenant_id", ASCENDING),
                ("cleanup_authorization_id", ASCENDING),
            ],
            name=INDEX_TENANT_CLEANUP_AUTHORIZATION,
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

    def get_by_claim_id(
        self,
        *,
        tenant_id: str,
        claim_id: str,
        session: object,
    ) -> LegalEvidenceProviderDeleteExecutionClaim | None:
        _require_transaction(session)
        try:
            return _hydrate(
                self._collection.find_one(
                    {
                        "tenant_id": tenant_id,
                        "claim_id": claim_id,
                    },
                    session=session,
                )
            )
        except LegalEvidenceProviderDeleteExecutionClaimRegistryError:
            raise
        except PyMongoError as error:
            raise LegalEvidenceProviderDeleteExecutionClaimRegistryPersistenceError(
                "L10A2R_A3_P4_P6D3_READ_FAILED"
            ) from error

    def get_by_fingerprint(
        self,
        *,
        tenant_id: str,
        fingerprint: str,
        session: object,
    ) -> LegalEvidenceProviderDeleteExecutionClaim | None:
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
        except LegalEvidenceProviderDeleteExecutionClaimRegistryError:
            raise
        except PyMongoError as error:
            raise LegalEvidenceProviderDeleteExecutionClaimRegistryPersistenceError(
                "L10A2R_A3_P4_P6D3_READ_FAILED"
            ) from error

    def get_by_command_id(
        self,
        *,
        tenant_id: str,
        command_id: str,
        session: object,
    ) -> LegalEvidenceProviderDeleteExecutionClaim | None:
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
        except LegalEvidenceProviderDeleteExecutionClaimRegistryError:
            raise
        except PyMongoError as error:
            raise LegalEvidenceProviderDeleteExecutionClaimRegistryPersistenceError(
                "L10A2R_A3_P4_P6D3_READ_FAILED"
            ) from error

    def get_by_cleanup_authorization_id(
        self,
        *,
        tenant_id: str,
        cleanup_authorization_id: str,
        session: object,
    ) -> LegalEvidenceProviderDeleteExecutionClaim | None:
        _require_transaction(session)
        try:
            return _hydrate(
                self._collection.find_one(
                    {
                        "tenant_id": tenant_id,
                        "cleanup_authorization_id":
                            cleanup_authorization_id,
                    },
                    session=session,
                )
            )
        except LegalEvidenceProviderDeleteExecutionClaimRegistryError:
            raise
        except PyMongoError as error:
            raise LegalEvidenceProviderDeleteExecutionClaimRegistryPersistenceError(
                "L10A2R_A3_P4_P6D3_READ_FAILED"
            ) from error

    def get_by_provider_object(
        self,
        *,
        tenant_id: str,
        provider_name: str,
        storage_reference: str,
        object_version_reference: str,
        session: object,
    ) -> LegalEvidenceProviderDeleteExecutionClaim | None:
        _require_transaction(session)
        try:
            return _hydrate(
                self._collection.find_one(
                    {
                        "tenant_id": tenant_id,
                        "provider_name": provider_name,
                        "storage_reference": storage_reference,
                        "object_version_reference":
                            object_version_reference,
                    },
                    session=session,
                )
            )
        except LegalEvidenceProviderDeleteExecutionClaimRegistryError:
            raise
        except PyMongoError as error:
            raise LegalEvidenceProviderDeleteExecutionClaimRegistryPersistenceError(
                "L10A2R_A3_P4_P6D3_READ_FAILED"
            ) from error

    def create_or_replay(
        self,
        value: LegalEvidenceProviderDeleteExecutionClaim,
        *,
        session: object,
    ) -> LegalEvidenceProviderDeleteExecutionClaim:
        _require_transaction(session)

        if type(value) is not LegalEvidenceProviderDeleteExecutionClaim:
            raise LegalEvidenceProviderDeleteExecutionClaimRegistryIntegrityError(
                "L10A2R_A3_P4_P6D3_CLAIM_REQUIRED"
            )

        lookups = (
            self.get_by_claim_id(
                tenant_id=value.tenant_id,
                claim_id=value.claim_id,
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
            self.get_by_cleanup_authorization_id(
                tenant_id=value.tenant_id,
                cleanup_authorization_id=
                    value.cleanup_authorization_id,
                session=session,
            ),
            self.get_by_provider_object(
                tenant_id=value.tenant_id,
                provider_name=value.provider_name,
                storage_reference=value.storage_reference,
                object_version_reference=
                    value.object_version_reference,
                session=session,
            ),
        )

        present = [item for item in lookups if item is not None]

        if present:
            if not all(_same(item, value) for item in present):
                raise LegalEvidenceProviderDeleteExecutionClaimRegistryIntegrityError(
                    "L10A2R_A3_P4_P6D3_REPLAY_CONFLICT"
                )
            if len(present) != len(lookups):
                raise LegalEvidenceProviderDeleteExecutionClaimRegistryIntegrityError(
                    "L10A2R_A3_P4_P6D3_DURABLE_IDENTITY_CONFLICT"
                )
            return value

        try:
            self._collection.insert_one(
                value.to_document(),
                session=session,
            )
            return value
        except DuplicateKeyError as error:
            raise LegalEvidenceProviderDeleteExecutionClaimRegistryRetryRequiredError(
                "L10A2R_A3_P4_P6D3_WHOLE_TRANSACTION_RETRY_REQUIRED"
            ) from error
        except PyMongoError as error:
            if getattr(error, "has_error_label", lambda _x: False)(
                "TransientTransactionError"
            ):
                raise LegalEvidenceProviderDeleteExecutionClaimRegistryRetryRequiredError(
                    "L10A2R_A3_P4_P6D3_WHOLE_TRANSACTION_RETRY_REQUIRED"
                ) from error
            raise LegalEvidenceProviderDeleteExecutionClaimRegistryPersistenceError(
                "L10A2R_A3_P4_P6D3_WRITE_FAILED"
            ) from error


__all__ = [
    "COLLECTION",
    "INDEX_TENANT_CLAIM_ID",
    "INDEX_TENANT_CLEANUP_AUTHORIZATION",
    "INDEX_TENANT_COMMAND",
    "INDEX_TENANT_FINGERPRINT",
    "INDEX_TENANT_PROVIDER_OBJECT",
    "VERSION",
    "LegalEvidenceProviderDeleteExecutionClaimRegistry",
    "LegalEvidenceProviderDeleteExecutionClaimRegistryError",
    "LegalEvidenceProviderDeleteExecutionClaimRegistryIntegrityError",
    "LegalEvidenceProviderDeleteExecutionClaimRegistryPersistenceError",
    "LegalEvidenceProviderDeleteExecutionClaimRegistryRetryRequiredError",
    "LegalEvidenceProviderDeleteExecutionClaimRegistryTransactionError",
]

# =============================================================================
# WILSY OS SOVEREIGN ARTIFACT SEAL
# =============================================================================
# ARTIFACT: legal_evidence_provider_delete_execution_claim_registry.py
# VERSION: v1.0.1-L10A2R-A3-P4-P6D3-PROVIDER-DELETE-EXECUTION-CLAIM-REGISTRY-GOVERNANCE
# AUTHORITY BOUNDARY: tenant-scoped durable execution-claim persistence only; no provider execution, release, provider retry, reconciliation, physical-absence, IAM, billing, payment or settlement authority
# TENANT POSTURE: every durable identity and lookup remains exact-tenant scoped; cross-tenant reads are absent
# FAIL-CLOSED POSTURE: inactive transaction, malformed domain value, corrupt persisted bytes, divergent replay and persistence failure reject
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively
# EXECUTABLE MODULE VERSION: v1.0.0-L10A2R-A3-P4-P6D3-PROVIDER-DELETE-EXECUTION-CLAIM-REGISTRY
# DURABLE DOCUMENT AUTHORITY: LegalEvidenceProviderDeleteExecutionClaim
# END OF WILSY OS SOVEREIGN ARTIFACT
