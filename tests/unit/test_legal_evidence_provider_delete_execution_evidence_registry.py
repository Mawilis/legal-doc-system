from __future__ import annotations

from copy import deepcopy
from datetime import datetime, timezone
from typing import Any

import pytest

from tools.eos.legal_operations.domain.legal_evidence_provider_delete_execution_evidence import (
    LegalEvidenceProviderDeleteExecutionEvidence,
)
from tools.eos.legal_operations.registry.legal_evidence_provider_delete_execution_evidence_registry import (
    COLLECTION,
    INDEX_TENANT_COMMAND,
    INDEX_TENANT_EXECUTION_EVIDENCE_ID,
    INDEX_TENANT_FINGERPRINT,
    INDEX_TENANT_PROVIDER_OBJECT,
    VERSION,
    LegalEvidenceProviderDeleteExecutionEvidenceRegistry,
    LegalEvidenceProviderDeleteExecutionEvidenceRegistryIntegrityError,
    LegalEvidenceProviderDeleteExecutionEvidenceRegistryRetryRequiredError,
    LegalEvidenceProviderDeleteExecutionEvidenceRegistryTransactionError,
)


TENANT = "tenant-p5b"
OTHER_TENANT = "tenant-p5b-other"
AT = datetime(2026, 10, 2, 16, 0, tzinfo=timezone.utc)


class DuplicateKeyError(Exception):
    pass


class Session:
    def __init__(self, *, active: bool = True) -> None:
        self.in_transaction = active


class Collection:
    def __init__(self) -> None:
        self.rows: list[dict[str, object]] = []
        self.indexes: list[
            tuple[list[tuple[str, int]], dict[str, object]]
        ] = []
        self.sessions: list[object] = []
        self.insert_failure: Exception | None = None

    def create_index(self, keys, **kwargs):
        self.indexes.append((list(keys), dict(kwargs)))
        return kwargs.get("name")

    def find_one(self, query, *, session):
        self.sessions.append(session)
        for row in self.rows:
            if all(row.get(k) == v for k, v in query.items()):
                return deepcopy(row)
        return None

    def insert_one(self, document, *, session):
        self.sessions.append(session)
        if self.insert_failure is not None:
            raise self.insert_failure
        self.rows.append(deepcopy(document))
        return object()


def _evidence(**overrides):
    values = {
        "execution_evidence_id": "execution-p5b",
        "tenant_id": TENANT,
        "command_id": "command-p5b",
        "cleanup_authorization_id": "cleanup-auth-p5b",
        "provider_name": "aws_s3",
        "storage_reference": "opaque/storage/p5b",
        "object_version_reference": "version-p5b",
        "command_fingerprint": "c" * 128,
        "cleanup_authorization_fingerprint": "d" * 128,
        "delete_marker": False,
        "delete_marker_version_reference": None,
        "executed_at": AT,
    }
    values.update(overrides)
    return LegalEvidenceProviderDeleteExecutionEvidence(**values)


def _registry():
    collection = Collection()
    return collection, LegalEvidenceProviderDeleteExecutionEvidenceRegistry(
        collection
    )


def test_registry_identity_collection_and_exact_indexes():
    assert VERSION.startswith("v1.0.0-L10A2R-A3-P4-P5B")
    assert COLLECTION == (
        "legal_evidence_provider_delete_execution_evidence"
    )

    collection, registry = _registry()
    registry.ensure_indexes()

    assert len(collection.indexes) == 4
    names = {item[1]["name"] for item in collection.indexes}
    assert names == {
        INDEX_TENANT_EXECUTION_EVIDENCE_ID,
        INDEX_TENANT_FINGERPRINT,
        INDEX_TENANT_COMMAND,
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
    value = _evidence()

    first = registry.create_or_replay(value, session=session)
    second = registry.create_or_replay(value, session=session)

    assert first == value
    assert second == value
    assert len(collection.rows) == 1
    assert collection.rows[0] == value.to_document()
    assert all(seen is session for seen in collection.sessions)


def test_all_exact_tenant_scoped_lookups():
    _, registry = _registry()
    session = Session()
    value = _evidence()

    registry.create_or_replay(value, session=session)

    assert registry.get_by_execution_evidence_id(
        tenant_id=TENANT,
        execution_evidence_id=value.execution_evidence_id,
        session=session,
    ) == value
    assert registry.get_by_fingerprint(
        tenant_id=TENANT,
        fingerprint=value.fingerprint,
        session=session,
    ) == value
    assert registry.get_by_command_id(
        tenant_id=TENANT,
        command_id=value.command_id,
        session=session,
    ) == value
    assert registry.get_by_provider_object(
        tenant_id=TENANT,
        provider_name=value.provider_name,
        storage_reference=value.storage_reference,
        object_version_reference=value.object_version_reference,
        session=session,
    ) == value


def test_cross_tenant_reads_are_absent():
    _, registry = _registry()
    session = Session()
    value = _evidence()

    registry.create_or_replay(value, session=session)

    assert registry.get_by_execution_evidence_id(
        tenant_id=OTHER_TENANT,
        execution_evidence_id=value.execution_evidence_id,
        session=session,
    ) is None
    assert registry.get_by_command_id(
        tenant_id=OTHER_TENANT,
        command_id=value.command_id,
        session=session,
    ) is None


def test_wrong_domain_type_rejects():
    _, registry = _registry()

    with pytest.raises(
        LegalEvidenceProviderDeleteExecutionEvidenceRegistryIntegrityError,
        match="EXECUTION_EVIDENCE_REQUIRED",
    ):
        registry.create_or_replay(
            object(),  # type: ignore[arg-type]
            session=Session(),
        )


@pytest.mark.parametrize(
    "session",
    [None, Session(active=False)],
)
def test_missing_or_inactive_transaction_rejects(session):
    _, registry = _registry()

    with pytest.raises(
        LegalEvidenceProviderDeleteExecutionEvidenceRegistryTransactionError,
        match="ACTIVE_TRANSACTION_REQUIRED",
    ):
        registry.create_or_replay(
            _evidence(),
            session=session,  # type: ignore[arg-type]
        )


def test_persisted_corruption_rejects():
    collection, registry = _registry()
    session = Session()
    value = _evidence()

    corrupt = value.to_document()
    corrupt["storage_reference"] = "different/storage"
    collection.rows.append(corrupt)

    with pytest.raises(
        LegalEvidenceProviderDeleteExecutionEvidenceRegistryIntegrityError,
        match="PERSISTED_DOCUMENT_CORRUPT",
    ):
        registry.get_by_command_id(
            tenant_id=TENANT,
            command_id=value.command_id,
            session=session,
        )


def test_divergent_command_identity_rejects():
    collection, registry = _registry()
    session = Session()
    value = _evidence()
    collection.rows.append(value.to_document())

    divergent = _evidence(
        execution_evidence_id="execution-different",
        storage_reference="different/storage",
        object_version_reference="version-different",
    )

    with pytest.raises(
        LegalEvidenceProviderDeleteExecutionEvidenceRegistryIntegrityError,
        match="REPLAY_CONFLICT",
    ):
        registry.create_or_replay(
            divergent,
            session=session,
        )


def test_duplicate_key_requires_whole_transaction_retry():
    collection, registry = _registry()
    collection.insert_failure = Exception("duplicate")
    session = Session()

    # Test double is converted below to the exact imported exception class
    # expected by the production registry.
    import tools.eos.legal_operations.registry.legal_evidence_provider_delete_execution_evidence_registry as module
    collection.insert_failure = module.DuplicateKeyError("duplicate")

    with pytest.raises(
        LegalEvidenceProviderDeleteExecutionEvidenceRegistryRetryRequiredError,
        match="WHOLE_TRANSACTION_RETRY_REQUIRED",
    ):
        registry.create_or_replay(
            _evidence(),
            session=session,
        )


def test_registry_has_no_provider_execution_or_mutable_reconciliation_surface():
    import inspect

    source = inspect.getsource(
        LegalEvidenceProviderDeleteExecutionEvidenceRegistry
    )

    forbidden = (
        "delete_object",
        "boto3",
        "update_one",
        "replace_one",
        "delete_one",
        "reconcile",
        "mark_completed",
        "mark_failed",
    )

    for token in forbidden:
        assert token not in source
