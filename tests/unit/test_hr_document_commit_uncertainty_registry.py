"""WILSY OS HR Commit-Uncertainty Registry Direct Certificate.

TITLE: HR Document Commit-Uncertainty Registry Direct Certificate
VERSION: v1.0.0-P0-C12F6D-HR-COMMIT-UNCERTAINTY-REGISTRY-CERT
AUTHORITY: Wilsy OS Core Governance / Python EOS
PURPOSE: Certify append-once, tenant-scoped durable persistence for
frozen HR document commit-uncertainty evidence.
ABSOLUTE CANONICAL PATH:
/Users/wilsonkhanyezi/legal-doc-system/tests/unit/test_hr_document_commit_uncertainty_registry.py
CERTIFICATION / UPDATE DATE: 2026-10-05
AUTHORITY BOUNDARY:
Persistence only. No provider IO, reconciliation, deletion, retention
decision, IAM, HTTP, payroll, billing, payment, settlement or financial
execution authority.
"""

from __future__ import annotations

from copy import deepcopy
from datetime import datetime, timedelta, timezone
import hashlib
import importlib
import importlib.util
from typing import Any

import pytest
from pymongo import ASCENDING, DESCENDING

from tools.eos.saas.domain.hr_document import (
    HrDocumentClass,
)
from tools.eos.saas.domain.hr_document_commit_uncertainty import (
    HrDocumentCommitUncertainty,
    open_hr_document_commit_uncertainty,
)
from tools.eos.saas.hr.hr_document_storage import (
    HrDocumentBinaryObjectEvidence,
    HrDocumentBinaryWriteIntent,
)


MODULE = (
    "tools.eos.saas.hr."
    "hr_document_commit_uncertainty_registry"
)

EXPECTED_VERSION = (
    "v1.0.0-P0-C12F6D-"
    "HR-COMMIT-UNCERTAINTY-REGISTRY"
)

EXPECTED_COLLECTION = (
    "hr_document_commit_uncertainties"
)

EXPECTED_FIELDS = {
    "uncertainty_id",
    "tenant_id",
    "employee_id",
    "document_id",
    "document_version_id",
    "ingestion_reference",
    "media_type",
    "original_filename",
    "admitted_max_content_length",
    "document_class",
    "created_at",
    "created_by_principal_id",
    "retention_until",
    "legal_hold",
    "supersedes_version_id",
    "provider_name",
    "storage_reference",
    "object_version_reference",
    "provider_integrity_reference",
    "write_intent_fingerprint",
    "content_length",
    "content_fingerprint",
    "detected_at",
    "schema",
    "uncertainty_version",
    "fingerprint",
}


class FakeSession:
    def __init__(
        self,
        *,
        in_transaction: bool,
    ) -> None:
        self.in_transaction = in_transaction


class FakeCursor:
    def __init__(
        self,
        rows: list[dict[str, Any]],
    ) -> None:
        self.rows = rows

    def limit(
        self,
        count: int,
    ) -> "FakeCursor":
        self.rows = self.rows[
            :count
        ]
        return self

    def __iter__(
        self,
    ):
        return iter(
            self.rows
        )


class FakeCollection:
    def __init__(
        self,
    ) -> None:
        self.rows: list[
            dict[str, Any]
        ] = []
        self.indexes: list[
            tuple[
                list[tuple[str, int]],
                bool,
                str,
            ]
        ] = []

    def with_options(
        self,
        **_: Any,
    ) -> "FakeCollection":
        return self

    def create_index(
        self,
        keys: list[
            tuple[str, int]
        ],
        *,
        unique: bool,
        name: str,
    ) -> str:
        self.indexes.append(
            (
                keys,
                unique,
                name,
            )
        )
        return name

    def find_one(
        self,
        query: dict[
            str,
            Any,
        ],
        *,
        session: Any,
    ):
        del session

        for row in self.rows:
            if all(
                row.get(
                    key
                )
                == value
                for key, value
                in query.items()
            ):
                return deepcopy(
                    row
                )

        return None

    def find(
        self,
        query: dict[
            str,
            Any,
        ],
        *,
        session: Any,
    ) -> FakeCursor:
        del session

        return FakeCursor(
            [
                deepcopy(
                    row
                )
                for row in self.rows
                if all(
                    row.get(
                        key
                    )
                    == value
                    for key, value
                    in query.items()
                )
            ]
        )

    def insert_one(
        self,
        document: dict[
            str,
            Any,
        ],
        *,
        session: Any,
    ) -> object:
        del session

        # Preserve production input immutability.
        self.rows.append(
            deepcopy(
                document
            )
        )

        return object()


def _module():
    return importlib.import_module(
        MODULE
    )


def _uncertainty(
    *,
    tenant_id: str = "tenant-f6d",
    ingestion_reference: str = "ingestion-f6d-001",
    object_version_reference: str = "provider-version-f6d-001",
) -> HrDocumentCommitUncertainty:
    payload = (
        b"WILSY-HR-F6D-"
        b"COMMIT-UNCERTAINTY"
    )

    intent = HrDocumentBinaryWriteIntent(
        tenant_id=tenant_id,
        employee_id="employee-f6d",
        document_id="document-f6d",
        document_version_id=(
            "document-version-f6d"
        ),
        ingestion_reference=(
            ingestion_reference
        ),
        media_type="application/pdf",
        original_filename=(
            "employment-contract.pdf"
        ),
        admitted_max_content_length=4096,
    )

    evidence = (
        HrDocumentBinaryObjectEvidence(
            provider_name="aws_s3",
            storage_reference=(
                "hr-documents/v1/"
                "opaque-f6d-object"
            ),
            object_version_reference=(
                object_version_reference
            ),
            provider_integrity_reference=(
                "provider-integrity-f6d"
            ),
            write_intent_fingerprint=(
                intent.fingerprint
            ),
            content_length=len(
                payload
            ),
            content_fingerprint=(
                hashlib.sha3_512(
                    payload
                ).hexdigest()
            ),
        )
    )

    created = datetime(
        2026,
        10,
        5,
        10,
        11,
        12,
        123456,
        tzinfo=timezone.utc,
    )

    return open_hr_document_commit_uncertainty(
        intent=intent,
        object_evidence=evidence,
        document_class=(
            HrDocumentClass.EMPLOYMENT_CONTRACT
        ),
        created_at=created,
        created_by_principal_id=(
            "principal-f6d"
        ),
        retention_until=(
            created
            + timedelta(
                days=365
            )
        ),
        legal_hold=False,
        supersedes_version_id=None,
        detected_at=(
            created
            + timedelta(
                seconds=3,
                microseconds=222,
            )
        ),
    )


def _active() -> FakeSession:
    return FakeSession(
        in_transaction=True
    )


def test_registry_module_exists_before_behavior() -> None:
    assert (
        importlib.util.find_spec(
            MODULE
        )
        is not None
    ), (
        "P0_C12F6D_EXPECTED_REGISTRY_MODULE_MISSING"
    )


def test_version_collection_and_index_contract() -> None:
    module = _module()

    assert (
        module.VERSION
        == EXPECTED_VERSION
    )

    assert (
        module.COLLECTION
        == EXPECTED_COLLECTION
    )

    collection = FakeCollection()

    module.ensure_indexes(
        collection
    )

    indexes = {
        name: (
            keys,
            unique,
        )
        for keys, unique, name
        in collection.indexes
    }

    assert indexes[
        module.UNCERTAINTY_INDEX_NAME
    ] == (
        [
            (
                "tenant_id",
                ASCENDING,
            ),
            (
                "uncertainty_id",
                ASCENDING,
            ),
        ],
        True,
    )

    assert indexes[
        module.INGESTION_INDEX_NAME
    ] == (
        [
            (
                "tenant_id",
                ASCENDING,
            ),
            (
                "ingestion_reference",
                ASCENDING,
            ),
        ],
        True,
    )

    assert indexes[
        module.PROVIDER_OBJECT_INDEX_NAME
    ] == (
        [
            (
                "tenant_id",
                ASCENDING,
            ),
            (
                "provider_name",
                ASCENDING,
            ),
            (
                "storage_reference",
                ASCENDING,
            ),
            (
                "object_version_reference",
                ASCENDING,
            ),
        ],
        True,
    )

    assert indexes[
        module.DETECTED_INDEX_NAME
    ] == (
        [
            (
                "tenant_id",
                ASCENDING,
            ),
            (
                "detected_at",
                DESCENDING,
            ),
            (
                "uncertainty_id",
                ASCENDING,
            ),
        ],
        False,
    )

    # No wall-clock deletion index.
    assert all(
        "expireAfterSeconds"
        not in str(
            item
        )
        for item in collection.indexes
    )


def test_active_transaction_required_before_read_or_write() -> None:
    module = _module()

    registry = (
        module.HrDocumentCommitUncertaintyRegistry(
            FakeCollection()
        )
    )

    value = _uncertainty()

    for session in (
        None,
        FakeSession(
            in_transaction=False
        ),
    ):
        with pytest.raises(
            module.HrDocumentCommitUncertaintyRegistryTransactionRequiredError
        ):
            registry.create_or_replay(
                value,
                session=session,
            )

        with pytest.raises(
            module.HrDocumentCommitUncertaintyRegistryTransactionRequiredError
        ):
            registry.get(
                tenant_id=value.tenant_id,
                uncertainty_id=(
                    value.uncertainty_id
                ),
                session=session,
            )


def test_create_and_exact_replay_are_append_once() -> None:
    module = _module()

    collection = FakeCollection()

    registry = (
        module.HrDocumentCommitUncertaintyRegistry(
            collection
        )
    )

    value = _uncertainty()

    first = registry.create_or_replay(
        value,
        session=_active(),
    )

    second = registry.create_or_replay(
        value,
        session=_active(),
    )

    assert first == value
    assert second == value

    assert len(
        collection.rows
    ) == 1


def test_persisted_schema_is_exact_and_contains_no_raw_bytes() -> None:
    module = _module()

    collection = FakeCollection()

    registry = (
        module.HrDocumentCommitUncertaintyRegistry(
            collection
        )
    )

    value = _uncertainty()

    registry.create_or_replay(
        value,
        session=_active(),
    )

    assert len(
        collection.rows
    ) == 1

    row = collection.rows[0]

    assert set(
        row
    ) == EXPECTED_FIELDS

    assert all(
        not isinstance(
            item,
            (
                bytes,
                bytearray,
                memoryview,
            ),
        )
        for item in row.values()
    )

    # Registry storage must preserve exact timestamp identity.
    assert row[
        "created_at"
    ] == value.created_at.isoformat()

    assert row[
        "retention_until"
    ] == (
        value.retention_until.isoformat()
        if value.retention_until
        is not None
        else None
    )

    assert row[
        "detected_at"
    ] == value.detected_at.isoformat()


def test_get_is_exactly_tenant_scoped() -> None:
    module = _module()

    collection = FakeCollection()

    registry = (
        module.HrDocumentCommitUncertaintyRegistry(
            collection
        )
    )

    first = _uncertainty(
        tenant_id="tenant-f6d-a"
    )

    second = _uncertainty(
        tenant_id="tenant-f6d-b"
    )

    registry.create_or_replay(
        first,
        session=_active(),
    )

    registry.create_or_replay(
        second,
        session=_active(),
    )

    assert (
        registry.get(
            tenant_id=first.tenant_id,
            uncertainty_id=(
                first.uncertainty_id
            ),
            session=_active(),
        )
        == first
    )

    with pytest.raises(
        module.HrDocumentCommitUncertaintyRegistryNotFoundError
    ):
        registry.get(
            tenant_id=second.tenant_id,
            uncertainty_id=(
                first.uncertainty_id
            ),
            session=_active(),
        )


def test_list_is_tenant_scoped_and_deterministic() -> None:
    module = _module()

    collection = FakeCollection()

    registry = (
        module.HrDocumentCommitUncertaintyRegistry(
            collection
        )
    )

    first = _uncertainty(
        tenant_id="tenant-f6d-a",
        ingestion_reference=(
            "ingestion-f6d-001"
        ),
        object_version_reference=(
            "provider-version-f6d-001"
        ),
    )

    second = _uncertainty(
        tenant_id="tenant-f6d-a",
        ingestion_reference=(
            "ingestion-f6d-002"
        ),
        object_version_reference=(
            "provider-version-f6d-002"
        ),
    )

    other = _uncertainty(
        tenant_id="tenant-f6d-b",
        ingestion_reference=(
            "ingestion-f6d-003"
        ),
        object_version_reference=(
            "provider-version-f6d-003"
        ),
    )

    for item in (
        first,
        second,
        other,
    ):
        registry.create_or_replay(
            item,
            session=_active(),
        )

    listed = (
        registry.list_tenant_uncertainties(
            tenant_id="tenant-f6d-a",
            session=_active(),
        )
    )

    assert set(
        listed
    ) == {
        first,
        second,
    }

    assert listed == tuple(
        sorted(
            listed,
            key=lambda item: (
                item.detected_at,
                item.uncertainty_id,
            ),
            reverse=True,
        )
    )


def test_corrupt_or_extra_persisted_field_fails_closed() -> None:
    module = _module()

    collection = FakeCollection()

    registry = (
        module.HrDocumentCommitUncertaintyRegistry(
            collection
        )
    )

    value = _uncertainty()

    registry.create_or_replay(
        value,
        session=_active(),
    )

    collection.rows[0][
        "unexpected"
    ] = "corruption"

    with pytest.raises(
        module.HrDocumentCommitUncertaintyRegistryPersistedRecordInvalidError
    ):
        registry.get(
            tenant_id=value.tenant_id,
            uncertainty_id=(
                value.uncertainty_id
            ),
            session=_active(),
        )


def test_fingerprint_corruption_fails_closed() -> None:
    module = _module()

    collection = FakeCollection()

    registry = (
        module.HrDocumentCommitUncertaintyRegistry(
            collection
        )
    )

    value = _uncertainty()

    registry.create_or_replay(
        value,
        session=_active(),
    )

    collection.rows[0][
        "fingerprint"
    ] = "0" * 128

    with pytest.raises(
        module.HrDocumentCommitUncertaintyRegistryPersistedRecordInvalidError
    ):
        registry.get(
            tenant_id=value.tenant_id,
            uncertainty_id=(
                value.uncertainty_id
            ),
            session=_active(),
        )


def test_divergent_same_ingestion_identity_fails_closed() -> None:
    module = _module()

    collection = FakeCollection()

    registry = (
        module.HrDocumentCommitUncertaintyRegistry(
            collection
        )
    )

    first = _uncertainty(
        ingestion_reference=(
            "ingestion-f6d-same"
        ),
        object_version_reference=(
            "provider-version-f6d-001"
        ),
    )

    second = _uncertainty(
        ingestion_reference=(
            "ingestion-f6d-same"
        ),
        object_version_reference=(
            "provider-version-f6d-002"
        ),
    )

    registry.create_or_replay(
        first,
        session=_active(),
    )

    with pytest.raises(
        module.HrDocumentCommitUncertaintyRegistryConflictError
    ):
        registry.create_or_replay(
            second,
            session=_active(),
        )


def test_provider_object_identity_cannot_bind_two_uncertainties() -> None:
    module = _module()

    collection = FakeCollection()

    registry = (
        module.HrDocumentCommitUncertaintyRegistry(
            collection
        )
    )

    first = _uncertainty(
        ingestion_reference=(
            "ingestion-f6d-001"
        ),
    )

    # Build a second frozen value by preserving the exact provider-object
    # identity but changing ingestion identity through a separately valid
    # write intent and evidence. The registry must reject that collision.
    payload = (
        b"WILSY-HR-F6D-"
        b"COMMIT-UNCERTAINTY"
    )

    intent = HrDocumentBinaryWriteIntent(
        tenant_id=first.tenant_id,
        employee_id=first.employee_id,
        document_id=first.document_id,
        document_version_id=(
            first.document_version_id
        ),
        ingestion_reference=(
            "ingestion-f6d-002"
        ),
        media_type=first.media_type,
        original_filename=(
            first.original_filename
        ),
        admitted_max_content_length=(
            first.admitted_max_content_length
        ),
    )

    evidence = (
        HrDocumentBinaryObjectEvidence(
            provider_name=first.provider_name,
            storage_reference=(
                first.storage_reference
            ),
            object_version_reference=(
                first.object_version_reference
            ),
            provider_integrity_reference=(
                first.provider_integrity_reference
            ),
            write_intent_fingerprint=(
                intent.fingerprint
            ),
            content_length=len(
                payload
            ),
            content_fingerprint=(
                hashlib.sha3_512(
                    payload
                ).hexdigest()
            ),
        )
    )

    second = open_hr_document_commit_uncertainty(
        intent=intent,
        object_evidence=evidence,
        document_class=(
            first.document_class
        ),
        created_at=first.created_at,
        created_by_principal_id=(
            first.created_by_principal_id
        ),
        retention_until=(
            first.retention_until
        ),
        legal_hold=first.legal_hold,
        supersedes_version_id=(
            first.supersedes_version_id
        ),
        detected_at=first.detected_at,
    )

    registry.create_or_replay(
        first,
        session=_active(),
    )

    with pytest.raises(
        module.HrDocumentCommitUncertaintyRegistryConflictError
    ):
        registry.create_or_replay(
            second,
            session=_active(),
        )


def test_registry_surface_exposes_no_update_delete_or_provider_methods() -> None:
    module = _module()

    forbidden = {
        "update",
        "delete",
        "remove",
        "purge",
        "dispose",
        "write_provider",
        "delete_provider",
        "reconcile",
    }

    names = {
        name
        for name in dir(
            module.HrDocumentCommitUncertaintyRegistry
        )
        if not name.startswith(
            "_"
        )
    }

    assert not (
        names
        & forbidden
    )


# ARTIFACT: tests/unit/test_hr_document_commit_uncertainty_registry.py
# VERSION: v1.0.0-P0-C12F6D-HR-COMMIT-UNCERTAINTY-REGISTRY-CERT
# CERTIFICATE: append-once durable HR commit-uncertainty persistence
# TTL AUTHORITY: none
# UPDATE AUTHORITY: none
# DELETE AUTHORITY: none
# PROVIDER IO AUTHORITY: none
# RECONCILIATION AUTHORITY: none
# IAM / HTTP AUTHORITY: none
# FINANCIAL EXECUTION AUTHORITY: none; Kennel EOS exclusively
# END OF WILSY OS SOVEREIGN ARTIFACT
