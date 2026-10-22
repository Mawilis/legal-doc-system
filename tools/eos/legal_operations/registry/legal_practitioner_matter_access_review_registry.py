"""TITLE: WILSY OS Institutional Matter-Access Review Registry.
VERSION: v1.0.0-R65-INSTITUTIONAL-ACCESS-REVIEW-REGISTRY
AUTHORITY: Append-only pending/denied request persistence and exact replay.
EPITOME: Persist R65 non-authorizing review outcomes within caller-owned
    transactions while rejecting divergent identity, idempotency and corruption.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tools/eos/legal_operations/registry/legal_practitioner_matter_access_review_registry.py
COLLABORATION / OWNERSHIP: R65 domain owns shape and integrity; API owns
    transaction lifecycle; MongoDB owns durable uniqueness.
CERTIFICATION / UPDATE DATE: 2026-10-22
CHANGELOG: 2026-10-22 v1.0.0-R65-INSTITUTIONAL-ACCESS-REVIEW-REGISTRY
    introduces exact-tenant append, replay, read and deterministic indexes.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2.
SECURITY / PRIVACY POSTURE: No logs or raw evidence; bounded error codes only.
TENANT BOUNDARY: Every identity, idempotency and read predicate begins tenant.
AUTHORITY BOUNDARY: Persistence does not approve, grant, assign or verify.
TRANSACTION BOUNDARY: Active caller-owned Mongo transaction is mandatory.
FINANCIAL AUTHORITY BOUNDARY: None; Kennel EOS exclusively.
"""

from __future__ import annotations

from datetime import datetime
from typing import Any, Final, NoReturn

from pymongo import ASCENDING
from pymongo.errors import DuplicateKeyError, PyMongoError

from tools.eos.legal_operations.registry.legal_practitioner_matter_access_review_codec import (
    hydrate as codec_hydrate,
    serialize,
    verify_integrity,
)

from tools.eos.legal_operations.domain.legal_practitioner_matter_access_review import (
    LegalPractitionerMatterAccessReview as Review,
)


VERSION: Final[str] = "v1.0.0-R65-INSTITUTIONAL-ACCESS-REVIEW-REGISTRY"
COLLECTION_NAME: Final[str] = "legal_practitioner_matter_access_review_requests"
IDENTITY_INDEX: Final[str] = "r65_access_review_identity_unique"
IDEMPOTENCY_INDEX: Final[str] = "r65_access_review_idempotency_unique"
SCOPE_INDEX: Final[str] = "r65_access_review_scope"


class MatterAccessReviewRegistryError(RuntimeError):
    """Base content-free R65 persistence error."""


class MatterAccessReviewTransactionRequired(MatterAccessReviewRegistryError):
    """The caller did not supply an active transaction."""


class MatterAccessReviewConflict(MatterAccessReviewRegistryError):
    """Durable identity or idempotency evidence diverged."""


class MatterAccessReviewPersistedInvalid(MatterAccessReviewRegistryError):
    """Durable evidence failed canonical hydration or integrity."""


class MatterAccessReviewRetryTransaction(MatterAccessReviewRegistryError):
    """The caller must restart the whole transaction from fresh state."""


class MatterAccessReviewPersistenceUnavailable(MatterAccessReviewRegistryError):
    """MongoDB did not establish a safe durable outcome."""


def _fail(error: type[MatterAccessReviewRegistryError], code: str) -> NoReturn:
    raise error(code)


def _tx(session: object) -> object:
    marker = getattr(session, "in_transaction", False) if session is not None else False
    if marker is not True:
        _fail(MatterAccessReviewTransactionRequired, "R65_ACTIVE_TRANSACTION_REQUIRED")
    return session


def _retryable(error: BaseException) -> bool:
    if not isinstance(error, PyMongoError):
        return False
    return any(
        bool(error.has_error_label(label))
        for label in ("TransientTransactionError", "UnknownTransactionCommitResult")
    )


def _hydrate(document: object) -> Review:
    """Decode and independently verify exact persisted review evidence."""
    try:
        if not isinstance(document, dict):
            raise ValueError("R65_PERSISTED_SHAPE_INVALID")
        return codec_hydrate(document)
    except (ValueError, TypeError, AttributeError) as error:
        raise MatterAccessReviewPersistedInvalid(
            "R65_PERSISTED_VALUE_INVALID"
        ) from error



def ensure_indexes(collection: Any) -> None:
    """Install deterministic R65 indexes outside request transactions."""
    collection.create_index(
        [("tenant_id", ASCENDING), ("review_request_id", ASCENDING)],
        unique=True,
        name=IDENTITY_INDEX,
    )
    collection.create_index(
        [("tenant_id", ASCENDING), ("idempotency_key", ASCENDING)],
        unique=True,
        name=IDEMPOTENCY_INDEX,
    )
    collection.create_index(
        [
            ("tenant_id", ASCENDING), ("case_matter_id", ASCENDING),
            ("practitioner_principal_id", ASCENDING), ("recorded_at", ASCENDING),
        ],
        name=SCOPE_INDEX,
    )


def append_review(*, review: Review, collection: Any, session: Any) -> Review:
    """Append or exactly replay one non-authorizing R65 review outcome."""
    tx = _tx(session)
    if type(review) is not Review or not verify_integrity(review):
        _fail(MatterAccessReviewConflict, "R65_REVIEW_VALUE_INVALID")
    identity = {"tenant_id": review.tenant_id, "review_request_id": review.review_request_id}
    replay = {"tenant_id": review.tenant_id, "idempotency_key": review.idempotency_key}
    try:
        existing = collection.find_one({"$or": [identity, replay]}, session=tx)
        if existing is not None:
            current = _hydrate(existing)
            if current == review and serialize(current) == serialize(review):
                return current
            _fail(MatterAccessReviewConflict, "R65_DIVERGENT_REPLAY")
        collection.insert_one(serialize(review), session=tx)
        persisted = collection.find_one(identity, session=tx)
    except MatterAccessReviewRegistryError:
        raise
    except DuplicateKeyError as error:
        raise MatterAccessReviewRetryTransaction("R65_WHOLE_TRANSACTION_RETRY_REQUIRED") from error
    except PyMongoError as error:
        if _retryable(error):
            raise MatterAccessReviewRetryTransaction("R65_WHOLE_TRANSACTION_RETRY_REQUIRED") from error
        raise MatterAccessReviewPersistenceUnavailable("R65_PERSISTENCE_UNAVAILABLE") from error
    if persisted is None:
        _fail(MatterAccessReviewPersistenceUnavailable, "R65_POST_WRITE_READ_MISSING")
    result = _hydrate(persisted)
    if result != review:
        _fail(MatterAccessReviewPersistedInvalid, "R65_POST_WRITE_CORRELATION_INVALID")
    return result


def get_review(
    *, tenant_id: str, review_request_id: str, collection: Any, session: Any,
) -> Review | None:
    """Read one exact-tenant request without probing foreign-tenant existence."""
    tx = _tx(session)
    if type(tenant_id) is not str or not tenant_id or type(review_request_id) is not str or not review_request_id:
        _fail(MatterAccessReviewRegistryError, "R65_REVIEW_IDENTITY_INVALID")
    try:
        document = collection.find_one(
            {"tenant_id": tenant_id, "review_request_id": review_request_id},
            session=tx,
        )
    except PyMongoError as error:
        raise MatterAccessReviewPersistenceUnavailable("R65_READ_UNAVAILABLE") from error
    return None if document is None else _hydrate(document)


__all__ = [
    "VERSION", "COLLECTION_NAME", "MatterAccessReviewRegistryError",
    "MatterAccessReviewTransactionRequired", "MatterAccessReviewConflict",
    "MatterAccessReviewPersistedInvalid", "MatterAccessReviewRetryTransaction",
    "MatterAccessReviewPersistenceUnavailable", "ensure_indexes", "append_review",
    "get_review",
]


# WILSY OS SOVEREIGN ARTIFACT SEAL
# ARTIFACT: legal_practitioner_matter_access_review_registry.py
# VERSION: v1.0.0-R65-INSTITUTIONAL-ACCESS-REVIEW-REGISTRY
# AUTHORITY BOUNDARY: APPEND-ONLY PENDING OR DENIED EVIDENCE PERSISTENCE
# TENANT POSTURE: EXACT TENANT-SCOPED IDENTITIES AND IDEMPOTENCY
# FAIL-CLOSED POSTURE: DIVERGENCE, CORRUPTION AND UNCERTAINTY REJECT
# FINANCIAL EXECUTION AUTHORITY: NONE; KENNEL EOS EXCLUSIVELY
# END OF WILSY OS SOVEREIGN ARTIFACT
