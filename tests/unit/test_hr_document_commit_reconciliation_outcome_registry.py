"""WILSY OS HR Commit-Reconciliation Outcome Registry Direct Certificate.

TITLE: HR Document Commit-Reconciliation Outcome Registry Direct Certificate
VERSION: v1.0.0-P0-C12F6E2-HR-COMMIT-RECONCILIATION-OUTCOME-REGISTRY-CERT
AUTHORITY: Wilsy OS Core Governance / Python EOS

PURPOSE:
Certify append-once durable persistence for frozen F6E1 HR document
commit-reconciliation outcomes.

AUTHORITY BOUNDARY:
Persistence only. No reconciliation decision authority, provider IO,
provider deletion, orphan determination, uncertainty mutation, IAM,
HTTP, retention/disposal, billing, payment, settlement or financial
execution authority.

TERMINAL OUTCOME RULE:
Exactly one durable reconciliation outcome may bind one tenant-scoped
uncertainty. Exact replay is allowed; any divergent replay conflicts.

ABSOLUTE CANONICAL PATH:
/Users/wilsonkhanyezi/legal-doc-system/tests/unit/test_hr_document_commit_reconciliation_outcome_registry.py

CERTIFICATION / UPDATE DATE: 2026-10-05
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
from tools.eos.saas.domain.hr_document_commit_reconciliation_outcome import (
    HrDocumentCommitReconciliationOutcome,
    HrDocumentCommitReconciliationOutcomeEvidence,
    record_hr_document_commit_reconciliation_outcome,
)
from tools.eos.saas.domain.hr_document_commit_uncertainty import (
    open_hr_document_commit_uncertainty,
)
from tools.eos.saas.hr.hr_document_storage import (
    HrDocumentBinaryObjectEvidence,
    HrDocumentBinaryWriteIntent,
)


MODULE = (
    "tools.eos.saas.hr."
    "hr_document_commit_reconciliation_outcome_registry"
)

EXPECTED_VERSION = (
    "v1.0.0-P0-C12F6E2-"
    "HR-COMMIT-RECONCILIATION-OUTCOME-REGISTRY"
)

EXPECTED_COLLECTION = (
    "hr_document_commit_reconciliation_outcomes"
)

EXPECTED_FIELDS = {
    "outcome_id",
    "tenant_id",
    "uncertainty_id",
    "uncertainty_fingerprint",
    "document_version_id",
    "document_fingerprint",
    "outcome",
    "reconciled_at",
    "schema",
    "outcome_version",
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
    tenant_id: str = "tenant-f6e2",
):
    payload = (
        b"WILSY-HR-F6E2-"
        b"OUTCOME-REGISTRY"
    )

    intent = HrDocumentBinaryWriteIntent(
        tenant_id=tenant_id,
        employee_id="employee-f6e2",
        document_id="document-f6e2",
        document_version_id=(
            "document-version-f6e2"
        ),
        ingestion_reference=(
            "ingestion-f6e2"
        ),
        media_type="application/pdf",
        original_filename=(
            "employment-contract.pdf"
        ),
        admitted_max_content_length=4096,
    )

    evidence = HrDocumentBinaryObjectEvidence(
        provider_name="aws_s3",
        storage_reference=(
            "hr/v1/opaque-f6e2-object"
        ),
        object_version_reference=(
            "provider-version-f6e2"
        ),
        provider_integrity_reference=(
            "provider-integrity-f6e2"
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

    created = datetime(
        2026,
        10,
        5,
        13,
        0,
        0,
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
            "principal-f6e2"
        ),
        retention_until=None,
        legal_hold=False,
        supersedes_version_id=None,
        detected_at=created,
    )


def _outcome(
    *,
    tenant_id: str = "tenant-f6e2",
    result: HrDocumentCommitReconciliationOutcome = (
        HrDocumentCommitReconciliationOutcome
        .COMMITTED_CONFIRMED
    ),
    seconds_after: int = 60,
) -> HrDocumentCommitReconciliationOutcomeEvidence:
    uncertainty = _uncertainty(
        tenant_id=tenant_id
    )

    document = uncertainty.to_hr_document()

    return record_hr_document_commit_reconciliation_outcome(
        uncertainty=uncertainty,
        document=document,
        outcome=result,
        reconciled_at=(
            uncertainty.detected_at
            + timedelta(
                seconds=seconds_after
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
        "P0_C12F6E2_EXPECTED_OUTCOME_REGISTRY_MODULE_MISSING"
    )


def test_version_collection_and_exact_index_contract() -> None:
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
        module.OUTCOME_ID_INDEX_NAME
    ] == (
        [
            (
                "tenant_id",
                ASCENDING,
            ),
            (
                "outcome_id",
                ASCENDING,
            ),
        ],
        True,
    )

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
        module.RECONCILED_INDEX_NAME
    ] == (
        [
            (
                "tenant_id",
                ASCENDING,
            ),
            (
                "reconciled_at",
                DESCENDING,
            ),
            (
                "outcome_id",
                ASCENDING,
            ),
        ],
        False,
    )

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
        module.HrDocumentCommitReconciliationOutcomeRegistry(
            FakeCollection()
        )
    )

    value = _outcome()

    for session in (
        None,
        FakeSession(
            in_transaction=False
        ),
    ):
        with pytest.raises(
            module.HrDocumentCommitReconciliationOutcomeRegistryTransactionRequiredError
        ):
            registry.create_or_replay(
                value,
                session=session,
            )

        with pytest.raises(
            module.HrDocumentCommitReconciliationOutcomeRegistryTransactionRequiredError
        ):
            registry.get_by_uncertainty(
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
        module.HrDocumentCommitReconciliationOutcomeRegistry(
            collection
        )
    )

    value = _outcome()

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


def test_same_uncertainty_cannot_acquire_different_terminal_outcome() -> None:
    module = _module()

    collection = FakeCollection()

    registry = (
        module.HrDocumentCommitReconciliationOutcomeRegistry(
            collection
        )
    )

    first = _outcome(
        result=(
            HrDocumentCommitReconciliationOutcome
            .COMMITTED_CONFIRMED
        )
    )

    divergent = _outcome(
        result=(
            HrDocumentCommitReconciliationOutcome
            .COMMIT_RECOVERED
        )
    )

    assert (
        first.uncertainty_id
        == divergent.uncertainty_id
    )

    assert (
        first.outcome_id
        != divergent.outcome_id
    )

    registry.create_or_replay(
        first,
        session=_active(),
    )

    with pytest.raises(
        module.HrDocumentCommitReconciliationOutcomeRegistryConflictError
    ):
        registry.create_or_replay(
            divergent,
            session=_active(),
        )

    assert len(
        collection.rows
    ) == 1


def test_same_uncertainty_cannot_acquire_different_reconciliation_time() -> None:
    module = _module()

    collection = FakeCollection()

    registry = (
        module.HrDocumentCommitReconciliationOutcomeRegistry(
            collection
        )
    )

    first = _outcome(
        seconds_after=60
    )

    divergent = _outcome(
        seconds_after=61
    )

    assert (
        first.uncertainty_id
        == divergent.uncertainty_id
    )

    assert (
        first.outcome_id
        != divergent.outcome_id
    )

    registry.create_or_replay(
        first,
        session=_active(),
    )

    with pytest.raises(
        module.HrDocumentCommitReconciliationOutcomeRegistryConflictError
    ):
        registry.create_or_replay(
            divergent,
            session=_active(),
        )

    assert len(
        collection.rows
    ) == 1


def test_persisted_schema_is_exact_and_contains_no_raw_bytes() -> None:
    module = _module()

    collection = FakeCollection()

    registry = (
        module.HrDocumentCommitReconciliationOutcomeRegistry(
            collection
        )
    )

    value = _outcome()

    registry.create_or_replay(
        value,
        session=_active(),
    )

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

    assert row[
        "reconciled_at"
    ] == value.reconciled_at.isoformat()


def test_get_by_uncertainty_is_exactly_tenant_scoped() -> None:
    module = _module()

    collection = FakeCollection()

    registry = (
        module.HrDocumentCommitReconciliationOutcomeRegistry(
            collection
        )
    )

    first = _outcome(
        tenant_id="tenant-f6e2-a"
    )

    second = _outcome(
        tenant_id="tenant-f6e2-b"
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
        registry.get_by_uncertainty(
            tenant_id=first.tenant_id,
            uncertainty_id=(
                first.uncertainty_id
            ),
            session=_active(),
        )
        == first
    )

    with pytest.raises(
        module.HrDocumentCommitReconciliationOutcomeRegistryNotFoundError
    ):
        registry.get_by_uncertainty(
            tenant_id=second.tenant_id,
            uncertainty_id=(
                first.uncertainty_id
            ),
            session=_active(),
        )


def test_get_by_outcome_id_is_exactly_tenant_scoped() -> None:
    module = _module()

    collection = FakeCollection()

    registry = (
        module.HrDocumentCommitReconciliationOutcomeRegistry(
            collection
        )
    )

    value = _outcome()

    registry.create_or_replay(
        value,
        session=_active(),
    )

    assert (
        registry.get_by_outcome_id(
            tenant_id=value.tenant_id,
            outcome_id=value.outcome_id,
            session=_active(),
        )
        == value
    )

    with pytest.raises(
        module.HrDocumentCommitReconciliationOutcomeRegistryNotFoundError
    ):
        registry.get_by_outcome_id(
            tenant_id="tenant-neighbor",
            outcome_id=value.outcome_id,
            session=_active(),
        )


def test_list_is_tenant_scoped_and_deterministic() -> None:
    module = _module()

    collection = FakeCollection()

    registry = (
        module.HrDocumentCommitReconciliationOutcomeRegistry(
            collection
        )
    )

    first = _outcome(
        tenant_id="tenant-f6e2-a"
    )

    other_tenant = _outcome(
        tenant_id="tenant-f6e2-b"
    )

    registry.create_or_replay(
        first,
        session=_active(),
    )

    registry.create_or_replay(
        other_tenant,
        session=_active(),
    )

    listed = registry.list_tenant_outcomes(
        tenant_id="tenant-f6e2-a",
        session=_active(),
    )

    assert listed == (
        first,
    )


def test_corrupt_fingerprint_or_extra_field_fails_closed() -> None:
    module = _module()

    for corruption in (
        "fingerprint",
        "extra",
    ):
        collection = FakeCollection()

        registry = (
            module.HrDocumentCommitReconciliationOutcomeRegistry(
                collection
            )
        )

        value = _outcome()

        registry.create_or_replay(
            value,
            session=_active(),
        )

        if corruption == "fingerprint":
            collection.rows[0][
                "fingerprint"
            ] = "0" * 128
        else:
            collection.rows[0][
                "unexpected"
            ] = "authority"

        with pytest.raises(
            module.HrDocumentCommitReconciliationOutcomeRegistryPersistedRecordInvalidError
        ):
            registry.get_by_uncertainty(
                tenant_id=value.tenant_id,
                uncertainty_id=(
                    value.uncertainty_id
                ),
                session=_active(),
            )


def test_registry_surface_exposes_no_update_delete_or_reconciliation_methods() -> None:
    module = _module()

    forbidden = {
        "update",
        "delete",
        "remove",
        "purge",
        "dispose",
        "reconcile",
        "resolve",
        "write_provider",
        "delete_provider",
    }

    names = {
        name
        for name in dir(
            module.HrDocumentCommitReconciliationOutcomeRegistry
        )
        if not name.startswith(
            "_"
        )
    }

    assert not (
        names
        & forbidden
    )


# ARTIFACT: tests/unit/test_hr_document_commit_reconciliation_outcome_registry.py
# VERSION: v1.0.0-P0-C12F6E2-HR-COMMIT-RECONCILIATION-OUTCOME-REGISTRY-CERT
# CERTIFICATE: append-once durable terminal reconciliation-outcome persistence
# ONE OUTCOME PER UNCERTAINTY: mandatory
# EXACT REPLAY: allowed
# DIVERGENT REPLAY: rejected
# TTL AUTHORITY: none
# UPDATE/DELETE AUTHORITY: none
# RECONCILIATION DECISION AUTHORITY: none
# PROVIDER IO AUTHORITY: none
# ORPHAN PROOF AUTHORITY: none
# IAM / HTTP AUTHORITY: none
# FINANCIAL EXECUTION AUTHORITY: none; Kennel EOS exclusively
# END OF WILSY OS SOVEREIGN ARTIFACT
