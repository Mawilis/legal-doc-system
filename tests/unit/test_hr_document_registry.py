"""TITLE: WILSY OS HR Document Registry Direct Certification.
VERSION: v1.0.0-P0-C12F4B-HR-DOCUMENT-REGISTRY-CERT
AUTHORITY: Direct certificate for immutable HR document-version metadata persistence.
EPITOME: Proves exact tenant/employee/document/version scope, caller-owned
active transactions, immutable replay, corruption rejection, scoped reads,
index contract and absence of update/delete/TTL authority.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tests/unit/test_hr_document_registry.py
CERTIFICATION/UPDATE DATE: 2026-10-04.
CHANGELOG:
2026-10-04 v1.0.0-P0-C12F4B-HR-DOCUMENT-REGISTRY-CERT
establishes the direct HR document registry certificate.
AUTHORITY BOUNDARY: metadata persistence only; no binary storage execution,
IAM, HTTP, retention enforcement, deletion execution or financial authority.
"""

from __future__ import annotations

from copy import deepcopy
from datetime import datetime, timedelta, timezone
import hashlib
import pathlib
from typing import Any

import pytest
from pymongo.errors import DuplicateKeyError

from tools.eos.saas.domain.hr_document import (
    HrDocument,
    HrDocumentClass,
)
from tools.eos.saas.hr import hr_document_registry as registry
from tools.eos.saas.hr.hr_document_storage import (
    HrDocumentBinaryObjectEvidence,
    HrDocumentBinaryWriteIntent,
)


TENANT = "tenant-hr-doc"
OTHER_TENANT = "tenant-hr-other"
EMPLOYEE = "employee-001"
OTHER_EMPLOYEE = "employee-999"

CREATED = datetime(
    2026,
    10,
    4,
    8,
    0,
    0,
    123456,
    tzinfo=timezone.utc,
)

PAYLOAD = b"%PDF-1.7\nreal-hr-document\x00\x01"


class FakeSession:
    def __init__(
        self,
        active: bool = True,
    ) -> None:
        self.in_transaction = active
        self.start_calls = 0
        self.commit_calls = 0
        self.abort_calls = 0

    def start_transaction(self) -> None:
        self.start_calls += 1

    def commit_transaction(self) -> None:
        self.commit_calls += 1

    def abort_transaction(self) -> None:
        self.abort_calls += 1


class FakeCursor:
    def __init__(
        self,
        rows: list[dict[str, Any]],
    ) -> None:
        self.rows = rows

    def sort(
        self,
        spec: list[tuple[str, int]],
    ) -> "FakeCursor":
        for key, direction in reversed(spec):
            self.rows.sort(
                key=lambda row: row.get(key) or "",
                reverse=direction < 0,
            )
        return self

    def limit(
        self,
        value: int,
    ) -> "FakeCursor":
        self.rows = self.rows[:value]
        return self

    def __iter__(self):
        return iter(self.rows)


class FakeCollection:
    def __init__(self) -> None:
        self.rows: list[dict[str, Any]] = []
        self.indexes: list[
            tuple[
                list[tuple[str, int]],
                dict[str, Any],
            ]
        ] = []
        self.raise_duplicate = False

    def with_options(
        self,
        **_: Any,
    ) -> "FakeCollection":
        return self

    def create_index(
        self,
        spec: list[tuple[str, int]],
        **kwargs: Any,
    ) -> str:
        self.indexes.append(
            (
                spec,
                kwargs,
            )
        )
        return str(
            kwargs.get(
                "name",
                "",
            )
        )

    def find(
        self,
        query: dict[str, object],
        *,
        session: Any,
    ) -> FakeCursor:
        del session

        rows = [
            deepcopy(row)
            for row in self.rows
            if all(
                row.get(key) == value
                for key, value in query.items()
            )
        ]

        return FakeCursor(
            rows
        )

    def insert_one(
        self,
        document: dict[str, object],
        *,
        session: Any,
    ) -> object:
        del session

        if self.raise_duplicate:
            self.raise_duplicate = False
            raise DuplicateKeyError(
                "duplicate"
            )

        self.rows.append(
            deepcopy(document)
        )

        return object()


def make_document(
    *,
    tenant_id: str = TENANT,
    employee_id: str = EMPLOYEE,
    document_id: str = "hrdoc-001",
    document_version_id: str = "hrdocver-001",
    document_class: HrDocumentClass = (
        HrDocumentClass.APPOINTMENT_LETTER
    ),
    created_at: datetime = CREATED,
    supersedes_version_id: str | None = None,
) -> HrDocument:

    current_intent = HrDocumentBinaryWriteIntent(
        tenant_id=tenant_id,
        employee_id=employee_id,
        document_id=document_id,
        document_version_id=document_version_id,
        ingestion_reference=(
            "ingest-"
            + document_version_id
        ),
        media_type="application/pdf",
        original_filename="appointment-letter.pdf",
        admitted_max_content_length=2_000_000,
    )

    current_evidence = HrDocumentBinaryObjectEvidence(
        provider_name="hr-provider",
        storage_reference=(
            "opaque/"
            + document_version_id
        ),
        object_version_reference=(
            "provider-"
            + document_version_id
        ),
        provider_integrity_reference=(
            "integrity-"
            + document_version_id
        ),
        write_intent_fingerprint=current_intent.fingerprint,
        content_length=len(PAYLOAD),
        content_fingerprint=hashlib.sha3_512(
            PAYLOAD
        ).hexdigest(),
    )

    return HrDocument.from_binary_evidence(
        intent=current_intent,
        evidence=current_evidence,
        document_class=document_class,
        created_at=created_at,
        created_by_principal_id="principal-hr",
        retention_until=(
            created_at
            + timedelta(
                days=365,
            )
        ),
        supersedes_version_id=supersedes_version_id,
    )


def test_collection_and_index_contract_is_exact() -> None:
    collection = FakeCollection()

    registry.ensure_indexes(
        collection
    )

    assert registry.COLLECTION == "hr_documents"

    assert collection.indexes == [
        (
            [
                ("tenant_id", 1),
                ("document_version_id", 1),
            ],
            {
                "unique": True,
                "name": registry.DOCUMENT_VERSION_INDEX_NAME,
            },
        ),
        (
            [
                ("tenant_id", 1),
                ("fingerprint", 1),
            ],
            {
                "unique": True,
                "name": registry.FINGERPRINT_INDEX_NAME,
            },
        ),
        (
            [
                ("tenant_id", 1),
                ("employee_id", 1),
                ("created_at", -1),
            ],
            {
                "unique": False,
                "name": registry.EMPLOYEE_CREATED_INDEX_NAME,
            },
        ),
        (
            [
                ("tenant_id", 1),
                ("employee_id", 1),
                ("document_id", 1),
                ("created_at", -1),
            ],
            {
                "unique": False,
                "name": registry.DOCUMENT_HISTORY_INDEX_NAME,
            },
        ),
        (
            [
                ("tenant_id", 1),
                ("employee_id", 1),
                ("document_class", 1),
                ("created_at", -1),
            ],
            {
                "unique": False,
                "name": registry.EMPLOYEE_CLASS_INDEX_NAME,
            },
        ),
        (
            [
                ("tenant_id", 1),
                ("employee_id", 1),
                ("sensitivity", 1),
                ("created_at", -1),
            ],
            {
                "unique": False,
                "name": registry.EMPLOYEE_SENSITIVITY_INDEX_NAME,
            },
        ),
    ]


def test_active_transaction_required_before_read_or_write() -> None:
    collection = FakeCollection()
    value = make_document()

    with pytest.raises(
        registry.HrDocumentRegistryTransactionRequiredError
    ):
        registry.persist_document(
            value,
            collection,
            session=None,
        )

    with pytest.raises(
        registry.HrDocumentRegistryTransactionRequiredError
    ):
        registry.get_document_version(
            TENANT,
            value.document_version_id,
            collection,
            session=FakeSession(
                active=False
            ),
        )


def test_exact_replay_is_idempotent_and_single_row() -> None:
    collection = FakeCollection()
    session = FakeSession()
    value = make_document()

    first = registry.persist_document(
        value,
        collection,
        session=session,
    )

    second = registry.persist_document(
        value,
        collection,
        session=session,
    )

    assert first == value
    assert second == value
    assert len(collection.rows) == 1


def test_same_version_divergence_rejects_without_mutation() -> None:
    collection = FakeCollection()
    session = FakeSession()

    original = make_document()

    registry.persist_document(
        original,
        collection,
        session=session,
    )

    before = deepcopy(
        collection.rows
    )

    divergent = make_document(
        document_class=HrDocumentClass.WARNING
    )

    with pytest.raises(
        registry.HrDocumentRegistryConflictError
    ):
        registry.persist_document(
            divergent,
            collection,
            session=session,
        )

    assert collection.rows == before


def test_same_fingerprint_under_different_version_rejects() -> None:
    collection = FakeCollection()
    session = FakeSession()

    original = make_document()

    registry.persist_document(
        original,
        collection,
        session=session,
    )

    forged = deepcopy(
        collection.rows[0]
    )

    forged["document_version_id"] = "hrdocver-forged"

    collection.rows.append(
        forged
    )

    with pytest.raises(
        registry.HrDocumentRegistryPersistedRecordInvalidError
    ):
        registry.get_document_by_fingerprint(
            TENANT,
            original.fingerprint,
            collection,
            session=session,
        )


def test_get_exact_version_is_tenant_scoped() -> None:
    collection = FakeCollection()
    session = FakeSession()
    value = make_document()

    registry.persist_document(
        value,
        collection,
        session=session,
    )

    assert (
        registry.get_document_version(
            TENANT,
            value.document_version_id,
            collection,
            session=session,
        )
        == value
    )

    with pytest.raises(
        registry.HrDocumentRegistryNotFoundError
    ):
        registry.get_document_version(
            OTHER_TENANT,
            value.document_version_id,
            collection,
            session=session,
        )


def test_employee_document_list_is_exact_and_newest_first() -> None:
    collection = FakeCollection()
    session = FakeSession()

    older = make_document(
        document_id="hrdoc-old",
        document_version_id="hrdocver-old",
        created_at=CREATED,
    )

    newer = make_document(
        document_id="hrdoc-new",
        document_version_id="hrdocver-new",
        created_at=(
            CREATED
            + timedelta(
                days=1
            )
        ),
    )

    foreign_employee = make_document(
        employee_id=OTHER_EMPLOYEE,
        document_id="hrdoc-foreign",
        document_version_id="hrdocver-foreign",
        created_at=(
            CREATED
            + timedelta(
                days=2
            )
        ),
    )

    for value in (
        older,
        newer,
        foreign_employee,
    ):
        registry.persist_document(
            value,
            collection,
            session=session,
        )

    values = registry.list_employee_documents(
        TENANT,
        EMPLOYEE,
        collection,
        session=session,
    )

    assert [
        item.document_version_id
        for item in values
    ] == [
        "hrdocver-new",
        "hrdocver-old",
    ]


def test_document_version_history_is_exact_scope() -> None:
    collection = FakeCollection()
    session = FakeSession()

    first = make_document()

    second = make_document(
        document_version_id="hrdocver-002",
        created_at=(
            CREATED
            + timedelta(
                hours=1
            )
        ),
        supersedes_version_id="hrdocver-001",
    )

    foreign_document = make_document(
        document_id="hrdoc-other",
        document_version_id="hrdocver-other",
    )

    for value in (
        first,
        second,
        foreign_document,
    ):
        registry.persist_document(
            value,
            collection,
            session=session,
        )

    values = registry.list_document_versions(
        TENANT,
        EMPLOYEE,
        "hrdoc-001",
        collection,
        session=session,
    )

    assert [
        item.document_version_id
        for item in values
    ] == [
        "hrdocver-002",
        "hrdocver-001",
    ]


def test_class_scoped_read_excludes_other_classes() -> None:
    collection = FakeCollection()
    session = FakeSession()

    appointment = make_document()

    warning = make_document(
        document_id="hrdoc-warning",
        document_version_id="hrdocver-warning",
        document_class=HrDocumentClass.WARNING,
    )

    registry.persist_document(
        appointment,
        collection,
        session=session,
    )

    registry.persist_document(
        warning,
        collection,
        session=session,
    )

    values = registry.list_employee_documents_by_class(
        TENANT,
        EMPLOYEE,
        HrDocumentClass.WARNING,
        collection,
        session=session,
    )

    assert values == (
        warning,
    )


def test_strict_hydration_preserves_microseconds_and_domain_truth() -> None:
    collection = FakeCollection()
    session = FakeSession()
    value = make_document()

    registry.persist_document(
        value,
        collection,
        session=session,
    )

    hydrated = registry.get_document_version(
        TENANT,
        value.document_version_id,
        collection,
        session=session,
    )

    assert hydrated == value

    assert (
        hydrated.created_at.microsecond
        == 123456
    )


def test_strict_hydration_rejects_extra_field() -> None:
    collection = FakeCollection()
    session = FakeSession()
    value = make_document()

    registry.persist_document(
        value,
        collection,
        session=session,
    )

    collection.rows[0]["unexpected"] = "authority"

    with pytest.raises(
        registry.HrDocumentRegistryPersistedRecordInvalidError
    ):
        registry.get_document_version(
            TENANT,
            value.document_version_id,
            collection,
            session=session,
        )


def test_strict_hydration_rejects_tampered_fingerprint() -> None:
    collection = FakeCollection()
    session = FakeSession()
    value = make_document()

    registry.persist_document(
        value,
        collection,
        session=session,
    )

    collection.rows[0]["fingerprint"] = "0" * 128

    with pytest.raises(
        registry.HrDocumentRegistryPersistedRecordInvalidError
    ):
        registry.get_document_version(
            TENANT,
            value.document_version_id,
            collection,
            session=session,
        )


def test_strict_hydration_rejects_class_sensitivity_mismatch() -> None:
    collection = FakeCollection()
    session = FakeSession()
    value = make_document()

    registry.persist_document(
        value,
        collection,
        session=session,
    )

    collection.rows[0][
        "sensitivity"
    ] = "HIGHLY_SENSITIVE_HEALTH"

    with pytest.raises(
        registry.HrDocumentRegistryPersistedRecordInvalidError
    ):
        registry.get_document_version(
            TENANT,
            value.document_version_id,
            collection,
            session=session,
        )


def test_duplicate_key_race_exact_replay_is_recovered() -> None:
    collection = FakeCollection()
    session = FakeSession()
    value = make_document()

    collection.rows.append(
        registry.serialize_document(
            value
        )
    )

    collection.raise_duplicate = True

    assert (
        registry.persist_document(
            value,
            collection,
            session=session,
        )
        == value
    )


def test_insert_adapter_mutation_does_not_contaminate_canonical_payload() -> None:
    class MutatingCollection(FakeCollection):
        def insert_one(
            self,
            document: dict[str, object],
            *,
            session: Any,
        ) -> object:
            del session

            document["_id"] = "adapter-injected-id"

            persisted = deepcopy(
                document
            )

            persisted.pop(
                "_id",
                None,
            )

            self.rows.append(
                persisted
            )

            return object()

    collection = MutatingCollection()
    session = FakeSession()
    value = make_document()

    persisted = registry.persist_document(
        value,
        collection,
        session=session,
    )

    assert persisted == value
    assert len(collection.rows) == 1

    assert set(
        collection.rows[0]
    ) == set(
        registry.HR_DOCUMENT_RECORD_FIELDS
    )

    assert "_id" not in collection.rows[0]



def test_registry_does_not_own_transaction_lifecycle() -> None:
    collection = FakeCollection()
    session = FakeSession()

    registry.persist_document(
        make_document(),
        collection,
        session=session,
    )

    assert session.start_calls == 0
    assert session.commit_calls == 0
    assert session.abort_calls == 0


def test_persisted_shape_is_exact_domain_metadata_only() -> None:
    collection = FakeCollection()
    session = FakeSession()
    value = make_document()

    registry.persist_document(
        value,
        collection,
        session=session,
    )

    assert set(
        collection.rows[0]
    ) == set(
        registry.HR_DOCUMENT_RECORD_FIELDS
    )

    forbidden = {
        "content_bytes",
        "binary",
        "raw_file",
        "payment_id",
        "settlement_id",
        "execution_id",
        "billing_authorized",
        "payment_authorized",
        "employee_name",
        "email",
        "phone",
    }

    assert forbidden.isdisjoint(
        collection.rows[0]
    )


def test_registry_source_has_no_update_delete_ttl_or_authority() -> None:
    source = registry.__file__

    assert source is not None

    text = pathlib.Path(
        source
    ).read_text(
        encoding="utf-8",
    )

    forbidden = (
        "expireAfterSeconds",
        "update_one(",
        "update_many(",
        "delete_one(",
        "delete_many(",
        ".delete(",
        "authorize_tenant_operation",
        "ROLE_PERMISSIONS_MAP",
        "payment_execution",
        "settlement_authority",
        "content_bytes",
    )

    assert all(
        token not in text
        for token in forbidden
    )


# ARTIFACT: tests/unit/test_hr_document_registry.py
# VERSION: v1.0.0-P0-C12F4B-HR-DOCUMENT-REGISTRY-CERT
# AUTHORITY BOUNDARY: immutable HR document-version metadata persistence only
# TRANSACTION BOUNDARY: caller-owned active transaction required
# STORAGE BOUNDARY: no binary bytes persisted here
# RETENTION BOUNDARY: no TTL or deletion execution authority
# FINANCIAL EXECUTION AUTHORITY: none; Kennel EOS exclusively
# END OF WILSY OS SOVEREIGN ARTIFACT
