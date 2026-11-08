from unittest.mock import MagicMock

import pytest

from tools.eos.runtime.core_worker_registry import (
    CLIENT_COLLECTION,
    COMPLIANCE_FINDINGS_COLLECTION,
    NOTIFICATION_OUTBOX_COLLECTION,
    build_core_worker_registry,
    provision_core_worker_indexes,
)


def test_core_registry_registers_only_implemented_compliance_handler():
    client = object()
    database = MagicMock()
    database.client = client
    registry = build_core_worker_registry(database=database, mongo_client=client)
    assert registry.engine_names == ("COMPLIANCE_SCAN",)
    assert database[CLIENT_COLLECTION] is not None
    assert database[COMPLIANCE_FINDINGS_COLLECTION] is not None
    assert database[NOTIFICATION_OUTBOX_COLLECTION] is not None


def test_core_registry_rejects_mixed_database_authority():
    database = MagicMock()
    database.client = object()
    with pytest.raises(RuntimeError, match="EOS_WORKER_DATABASE_CLIENT_MISMATCH"):
        build_core_worker_registry(database=database, mongo_client=object())


def test_core_registry_fails_closed_without_kernel_database():
    with pytest.raises(RuntimeError, match="EOS_KERNEL_DATABASE_NOT_READY"):
        build_core_worker_registry(database=None, mongo_client=None)


def test_core_index_provisioning_targets_compliance_collections_explicitly():
    database = MagicMock()
    collections = {
        CLIENT_COLLECTION: MagicMock(),
        COMPLIANCE_FINDINGS_COLLECTION: MagicMock(),
        NOTIFICATION_OUTBOX_COLLECTION: MagicMock(),
    }
    database.__getitem__.side_effect = collections.__getitem__
    provision_core_worker_indexes(database=database)
    assert collections[CLIENT_COLLECTION].create_index.call_count == 1
    assert collections[COMPLIANCE_FINDINGS_COLLECTION].create_index.call_count == 1
    assert collections[NOTIFICATION_OUTBOX_COLLECTION].create_index.call_count == 2
