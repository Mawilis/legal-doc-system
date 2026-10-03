from copy import deepcopy
from datetime import datetime, timedelta, timezone

import pytest
from pymongo.errors import DuplicateKeyError

from tools.eos.legal_operations.domain.legal_evidence_provider_delete_execution_claim import (
    LegalEvidenceProviderDeleteExecutionClaim,
)
from tools.eos.legal_operations.registry.legal_evidence_provider_delete_execution_claim_registry import (
    COLLECTION,
    INDEX_TENANT_CLAIM_ID,
    INDEX_TENANT_CLEANUP_AUTHORIZATION,
    INDEX_TENANT_COMMAND,
    INDEX_TENANT_FINGERPRINT,
    INDEX_TENANT_PROVIDER_OBJECT,
    VERSION,
    LegalEvidenceProviderDeleteExecutionClaimRegistry,
    LegalEvidenceProviderDeleteExecutionClaimRegistryIntegrityError,
    LegalEvidenceProviderDeleteExecutionClaimRegistryRetryRequiredError,
    LegalEvidenceProviderDeleteExecutionClaimRegistryTransactionError,
)


AT = datetime(2026, 10, 2, 16, 0, tzinfo=timezone.utc)


class Session:
    def __init__(self, *, active: bool = True) -> None:
        self.in_transaction = active


class CallableSession:
    def __init__(self, *, active: bool = True) -> None:
        self._active = active

    def in_transaction(self) -> bool:
        return self._active


class Collection:
    def __init__(self) -> None:
        self.rows: list[dict[str, object]] = []
        self.indexes: list[
            tuple[list[tuple[str, int]], dict[str, object]]
        ] = []
        self.sessions: list[object] = []
        self.insert_failure: Exception | None = None

    def create_index(
        self,
        keys: list[tuple[str, int]],
        **kwargs: object,
    ) -> str | None:
        self.indexes.append((list(keys), dict(kwargs)))
        name = kwargs.get("name")
        return name if isinstance(name, str) else None

    def find_one(
        self,
        query: dict[str, object],
        *,
        session: object,
    ) -> dict[str, object] | None:
        self.sessions.append(session)
        for row in self.rows:
            if all(row.get(key) == value for key, value in query.items()):
                return deepcopy(row)
        return None

    def insert_one(
        self,
        document: dict[str, object],
        *,
        session: object,
    ) -> object:
        self.sessions.append(session)
        if self.insert_failure is not None:
            raise self.insert_failure
        self.rows.append(deepcopy(document))
        return object()


def _claim(**changes):
    values = {
        "claim_id": "claim-1",
        "tenant_id": "tenant-1",
        "command_id": "command-1",
        "cleanup_authorization_id": "authorization-1",
        "provider_name": "aws_s3",
        "storage_reference": "opaque-storage-key",
        "object_version_reference": "version-1",
        "command_fingerprint": "a" * 128,
        "cleanup_authorization_fingerprint": "b" * 128,
        "claimed_at": AT,
    }
    values.update(changes)
    return LegalEvidenceProviderDeleteExecutionClaim(**values)


def _registry():
    collection = Collection()
    return (
        collection,
        LegalEvidenceProviderDeleteExecutionClaimRegistry(
            collection
        ),
    )


def test_identity_collection_indexes_and_no_ttl():
    assert VERSION == (
        "v1.0.0-L10A2R-A3-P4-P6D3-"
        "PROVIDER-DELETE-EXECUTION-CLAIM-REGISTRY"
    )
    assert COLLECTION == (
        "legal_evidence_provider_delete_execution_claims"
    )

    collection, registry = _registry()
    registry.ensure_indexes()

    assert len(collection.indexes) == 5
    assert {item[1]["name"] for item in collection.indexes} == {
        INDEX_TENANT_CLAIM_ID,
        INDEX_TENANT_FINGERPRINT,
        INDEX_TENANT_COMMAND,
        INDEX_TENANT_CLEANUP_AUTHORIZATION,
        INDEX_TENANT_PROVIDER_OBJECT,
    }
    assert all(item[1]["unique"] is True for item in collection.indexes)
    assert all(
        "expireAfterSeconds" not in item[1]
        for item in collection.indexes
    )


def test_create_once_exact_replay_and_session_propagation():
    collection, registry = _registry()
    session = Session()
    value = _claim()

    assert registry.create_or_replay(value, session=session) == value
    assert registry.create_or_replay(value, session=session) == value

    assert len(collection.rows) == 1
    assert collection.sessions
    assert all(item is session for item in collection.sessions)


def test_all_exact_tenant_scoped_lookups():
    _, registry = _registry()
    session = Session()
    value = _claim()

    registry.create_or_replay(value, session=session)

    assert registry.get_by_claim_id(
        tenant_id=value.tenant_id,
        claim_id=value.claim_id,
        session=session,
    ) == value

    assert registry.get_by_fingerprint(
        tenant_id=value.tenant_id,
        fingerprint=value.fingerprint,
        session=session,
    ) == value

    assert registry.get_by_command_id(
        tenant_id=value.tenant_id,
        command_id=value.command_id,
        session=session,
    ) == value

    assert registry.get_by_cleanup_authorization_id(
        tenant_id=value.tenant_id,
        cleanup_authorization_id=value.cleanup_authorization_id,
        session=session,
    ) == value

    assert registry.get_by_provider_object(
        tenant_id=value.tenant_id,
        provider_name=value.provider_name,
        storage_reference=value.storage_reference,
        object_version_reference=value.object_version_reference,
        session=session,
    ) == value


def test_cross_tenant_reads_are_absent():
    _, registry = _registry()
    session = Session()
    value = _claim()

    registry.create_or_replay(value, session=session)

    assert registry.get_by_claim_id(
        tenant_id="tenant-other",
        claim_id=value.claim_id,
        session=session,
    ) is None

    assert registry.get_by_command_id(
        tenant_id="tenant-other",
        command_id=value.command_id,
        session=session,
    ) is None

    assert registry.get_by_cleanup_authorization_id(
        tenant_id="tenant-other",
        cleanup_authorization_id=value.cleanup_authorization_id,
        session=session,
    ) is None

    assert registry.get_by_provider_object(
        tenant_id="tenant-other",
        provider_name=value.provider_name,
        storage_reference=value.storage_reference,
        object_version_reference=value.object_version_reference,
        session=session,
    ) is None


@pytest.mark.parametrize(
    "session",
    [
        None,
        Session(active=False),
        CallableSession(active=False),
    ],
)
def test_missing_or_inactive_transaction_rejects(session):
    _, registry = _registry()

    with pytest.raises(
        LegalEvidenceProviderDeleteExecutionClaimRegistryTransactionError
    ):
        registry.get_by_command_id(
            tenant_id="tenant-1",
            command_id="command-1",
            session=session,  # type: ignore[arg-type]
        )


def test_wrong_domain_type_rejects():
    _, registry = _registry()

    with pytest.raises(
        LegalEvidenceProviderDeleteExecutionClaimRegistryIntegrityError,
        match="CLAIM_REQUIRED",
    ):
        registry.create_or_replay(
            object(),  # type: ignore[arg-type]
            session=Session(),
        )


def test_persisted_corruption_rejects():
    collection, registry = _registry()
    session = Session()
    value = _claim()

    document = value.to_document()
    document["command_id"] = "corrupt-command"
    collection.rows.append(document)

    with pytest.raises(
        LegalEvidenceProviderDeleteExecutionClaimRegistryIntegrityError,
        match="PERSISTED_DOCUMENT_CORRUPT",
    ):
        registry.get_by_claim_id(
            tenant_id=value.tenant_id,
            claim_id=value.claim_id,
            session=session,
        )


def test_divergent_command_claim_rejects():
    _, registry = _registry()
    session = Session()

    first = _claim()

    second = _claim(
        claim_id="claim-2",
        command_id=first.command_id,
        cleanup_authorization_id="authorization-2",
        storage_reference="other-key",
        object_version_reference="version-2",
        command_fingerprint="c" * 128,
        cleanup_authorization_fingerprint="d" * 128,
        claimed_at=AT + timedelta(seconds=1),
    )

    registry.create_or_replay(first, session=session)

    with pytest.raises(
        LegalEvidenceProviderDeleteExecutionClaimRegistryIntegrityError,
        match="REPLAY_CONFLICT",
    ):
        registry.create_or_replay(second, session=session)


def test_divergent_provider_object_claim_rejects():
    _, registry = _registry()
    session = Session()

    first = _claim()

    second = _claim(
        claim_id="claim-2",
        command_id="command-2",
        cleanup_authorization_id="authorization-2",
        command_fingerprint="c" * 128,
        cleanup_authorization_fingerprint="d" * 128,
        claimed_at=AT + timedelta(seconds=1),
    )

    registry.create_or_replay(first, session=session)

    with pytest.raises(
        LegalEvidenceProviderDeleteExecutionClaimRegistryIntegrityError,
        match="REPLAY_CONFLICT",
    ):
        registry.create_or_replay(second, session=session)


def test_duplicate_key_requires_whole_transaction_retry():
    collection, registry = _registry()
    collection.insert_failure = DuplicateKeyError("duplicate")

    with pytest.raises(
        LegalEvidenceProviderDeleteExecutionClaimRegistryRetryRequiredError,
        match="WHOLE_TRANSACTION_RETRY_REQUIRED",
    ):
        registry.create_or_replay(
            _claim(),
            session=Session(),
        )


def test_registry_has_no_provider_execution_retry_reconciliation_or_release_surface():
    forbidden = {
        "execute_delete",
        "delete_object",
        "retry_delete",
        "authorize_retry",
        "reconcile",
        "release",
        "delete_claim",
        "expire",
    }

    public = {
        name
        for name in dir(
            LegalEvidenceProviderDeleteExecutionClaimRegistry
        )
        if not name.startswith("_")
    }

    assert forbidden.isdisjoint(public)
