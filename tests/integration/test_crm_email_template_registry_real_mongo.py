"""
TITLE: WILSY OS CRM Email Template Registry Real-Mongo Certificate
VERSION: v1.1.0-P0-CRM-EMAIL-TEMPLATE-REGISTRY-REAL-MONGO

AUTHORITY:
    Real MongoDB certification of tenant-bound CRM email-template metadata
    persistence and immutable published-revision history.

EPITOME:
    Certifies actual Mongo indexes, caller-owned transactions, exact replay,
    strict revision sequencing, tenant isolation, corruption rejection,
    concurrent-writer convergence and absence of destructive/send authority.

ABSOLUTE CANONICAL PATH:
    /Users/wilsonkhanyezi/legal-doc-system/tests/integration/test_crm_email_template_registry_real_mongo.py

RUNTIME BINDING:
    TEST_VENDOR_MONGO_URI when explicitly supplied, otherwise the canonical
    loopback certification fallback:
    mongodb://127.0.0.1:27027/?replicaSet=wilsyVendorCertRS

DATABASE POSTURE:
    Every test uses a UUID-isolated disposable database.

TRANSACTION POSTURE:
    Production writes occur only inside caller-owned Mongo transactions.
    Public reads may receive the caller-owned session so the service layer
    can preserve real-Mongo transaction visibility without manufacturing
    or owning transaction lifecycle.

CONCURRENCY POSTURE:
    Mongo unique indexes are the final race arbiter. Concurrent callers may
    converge through exact replay or one caller may receive a governed Mongo /
    registry conflict, but only one durable identity may remain.

RETENTION BOUNDARY:
    No TTL index, deletion, purge or destructive registry authority.

SEND BOUNDARY:
    No mailbox, send, consent, sequence, AI-send or financial-execution state
    may be persisted by this registry.
"""

from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timedelta, timezone
import os
from typing import Any, Iterator
from urllib.parse import urlparse
from uuid import uuid4

import pytest
from pymongo import MongoClient
from pymongo.errors import PyMongoError

from tools.eos.crm.domain.crm_email_template import (
    CrmEmailTemplate,
    CrmEmailTemplateLifecycle,
    CrmEmailTemplateOrigin,
    CrmEmailTemplateRevision,
    CrmEmailTemplateScope,
)

from tools.eos.crm.persistence.crm_email_template_registry import (
    CRM_EMAIL_TEMPLATE_METADATA_COLLECTION,
    CRM_EMAIL_TEMPLATE_REVISION_COLLECTION,
    CrmEmailTemplateRegistry,
    CrmEmailTemplateRegistryConflictError,
    CrmEmailTemplateRegistryCorruptionError,
    CrmEmailTemplateRegistryError,
    CrmEmailTemplateRegistryTransactionError,
)


DEFAULT_MONGO_URI = (
    "mongodb://127.0.0.1:27027/"
    "?replicaSet=wilsyVendorCertRS"
)

MONGO_URI = os.environ.get(
    "TEST_VENDOR_MONGO_URI",
    DEFAULT_MONGO_URI,
).strip()

if not MONGO_URI:
    MONGO_URI = DEFAULT_MONGO_URI

TENANT = "WILSYTENANT-CRM-EMAIL-MONGO-001"
OTHER_TENANT = "WILSYTENANT-CRM-EMAIL-MONGO-002"
TEMPLATE_ID = "WILSYCRM-EMAIL-TEMPLATE-MONGO-001"
OWNER = "principal-sales-mongo-001"

NOW = datetime(
    2026,
    10,
    7,
    1,
    30,
    tzinfo=timezone.utc,
)

SOURCE_FP = "a" * 128


@pytest.fixture
def mongo_context() -> Iterator[
    tuple[Any, Any, Any, Any]
]:
    client: Any = MongoClient(
        MONGO_URI,
        serverSelectionTimeoutMS=3000,
        connectTimeoutMS=3000,
        socketTimeoutMS=5000,
    )

    hello = client.admin.command(
        "hello"
    )

    assert hello.get("ok") == 1
    assert (
        hello.get("setName")
        == "wilsyVendorCertRS"
    )
    assert hello.get("isWritablePrimary") is True

    parsed = urlparse(
        MONGO_URI
    )

    assert parsed.hostname in {
        "127.0.0.1",
        "localhost",
    }

    db_name = (
        "wilsy_crm_email_template_cert_"
        + uuid4().hex
    )

    database = client[db_name]

    metadata = database[
        CRM_EMAIL_TEMPLATE_METADATA_COLLECTION
    ]

    revisions = database[
        CRM_EMAIL_TEMPLATE_REVISION_COLLECTION
    ]

    CrmEmailTemplateRegistry.ensure_indexes(
        metadata,
        revisions,
    )

    try:
        yield (
            client,
            database,
            metadata,
            revisions,
        )

    finally:
        client.drop_database(
            db_name
        )
        client.close()


def _template(
    *,
    tenant_id: str = TENANT,
    template_id: str = TEMPLATE_ID,
    name: str = "Initial Outreach",
) -> CrmEmailTemplate:
    return CrmEmailTemplate.create(
        tenant_id=tenant_id,
        template_id=template_id,
        name=name,
        scope=CrmEmailTemplateScope.USER_PRIVATE,
        origin=CrmEmailTemplateOrigin.TENANT_CREATED,
        lifecycle=CrmEmailTemplateLifecycle.ACTIVE,
        owner_principal_id=OWNER,
        team_id=None,
        folder="Outbound",
        tags=(
            "prospecting",
            "initial",
        ),
        created_at=NOW,
    )


def _revision(
    revision: int,
    *,
    tenant_id: str = TENANT,
    template_id: str = TEMPLATE_ID,
    subject: str | None = None,
) -> CrmEmailTemplateRevision:
    actual_subject = (
        subject
        if subject is not None
        else (
            f"Revision {revision} "
            "{{lead.first_name}}"
        )
    )

    return CrmEmailTemplateRevision.publish(
        tenant_id=tenant_id,
        template_id=template_id,
        revision=revision,
        subject=actual_subject,
        text_body="Hello {{lead.first_name}}",
        html_body="<p>Hello {{lead.first_name}}</p>",
        variable_keys=(
            "lead.first_name",
        ),
        attachment_references=(),
        signature_reference="sender.default_signature",
        source_reference=(
            f"real-mongo-author:{OWNER}:"
            f"revision:{revision}"
        ),
        source_fingerprint=SOURCE_FP,
        published_at=NOW,
    )


def _create_committed(
    client: Any,
    metadata: Any,
    value: CrmEmailTemplate,
    *,
    key: str,
) -> CrmEmailTemplate:
    with client.start_session() as session:
        with session.start_transaction():
            result = (
                CrmEmailTemplateRegistry
                .create_template(
                    value,
                    idempotency_key=key,
                    metadata_collection=metadata,
                    session=session,
                )
            )

    return result


def _append_committed(
    client: Any,
    metadata: Any,
    revisions: Any,
    value: CrmEmailTemplateRevision,
) -> CrmEmailTemplateRevision:
    with client.start_session() as session:
        with session.start_transaction():
            result = (
                CrmEmailTemplateRegistry
                .append_revision(
                    value,
                    metadata_collection=metadata,
                    revision_collection=revisions,
                    session=session,
                )
            )

    return result


def _index_map(
    collection: Any,
) -> dict[str, dict[str, Any]]:
    result: dict[
        str,
        dict[str, Any],
    ] = {}

    for raw in collection.list_indexes():
        row = dict(raw)
        result[str(row["name"])] = row

    return result


def _keys(
    index: dict[str, Any],
) -> tuple[tuple[str, int], ...]:
    return tuple(
        (
            str(key),
            int(direction),
        )
        for key, direction
        in index["key"].items()
    )


def test_real_index_metadata_and_no_ttl(
    mongo_context: tuple[Any, Any, Any, Any],
) -> None:
    _, _, metadata, revisions = mongo_context

    meta = _index_map(
        metadata
    )

    rev = _index_map(
        revisions
    )

    assert _keys(
        meta[
            "crm_email_template_"
            "tenant_identity_unique"
        ]
    ) == (
        ("tenant_id", 1),
        ("template_id", 1),
    )

    assert (
        meta[
            "crm_email_template_"
            "tenant_identity_unique"
        ].get("unique")
        is True
    )

    assert _keys(
        meta[
            "crm_email_template_"
            "tenant_create_idempotency_unique"
        ]
    ) == (
        ("tenant_id", 1),
        ("create_idempotency_key", 1),
    )

    assert (
        meta[
            "crm_email_template_"
            "tenant_create_idempotency_unique"
        ].get("unique")
        is True
    )

    assert _keys(
        rev[
            "crm_email_template_"
            "revision_identity_unique"
        ]
    ) == (
        ("tenant_id", 1),
        ("template_id", 1),
        ("revision", 1),
    )

    assert (
        rev[
            "crm_email_template_"
            "revision_identity_unique"
        ].get("unique")
        is True
    )

    assert _keys(
        rev[
            "crm_email_template_"
            "revision_fingerprint_unique"
        ]
    ) == (
        ("tenant_id", 1),
        ("template_id", 1),
        ("fingerprint", 1),
    )

    assert (
        rev[
            "crm_email_template_"
            "revision_fingerprint_unique"
        ].get("unique")
        is True
    )

    assert _keys(
        rev[
            "crm_email_template_"
            "revision_read"
        ]
    ) == (
        ("tenant_id", 1),
        ("template_id", 1),
        ("revision", -1),
    )

    for collection_indexes in (
        meta,
        rev,
    ):
        for index in collection_indexes.values():
            assert (
                "expireAfterSeconds"
                not in index
            )


def test_missing_and_inactive_transactions_reject_before_write(
    mongo_context: tuple[Any, Any, Any, Any],
) -> None:
    client, _, metadata, revisions = mongo_context

    value = _template()

    with pytest.raises(
        CrmEmailTemplateRegistryTransactionError
    ):
        CrmEmailTemplateRegistry.create_template(
            value,
            idempotency_key="missing-session",
            metadata_collection=metadata,
            session=None,
        )

    assert metadata.count_documents({}) == 0

    with client.start_session() as inactive:
        assert inactive.in_transaction is False

        with pytest.raises(
            CrmEmailTemplateRegistryTransactionError
        ):
            CrmEmailTemplateRegistry.create_template(
                value,
                idempotency_key="inactive-session",
                metadata_collection=metadata,
                session=inactive,
            )

        with pytest.raises(
            CrmEmailTemplateRegistryTransactionError
        ):
            CrmEmailTemplateRegistry.append_revision(
                _revision(1),
                metadata_collection=metadata,
                revision_collection=revisions,
                session=inactive,
            )

    assert metadata.count_documents({}) == 0
    assert revisions.count_documents({}) == 0


def test_real_create_commit_read_and_exact_replay(
    mongo_context: tuple[Any, Any, Any, Any],
) -> None:
    client, _, metadata, _ = mongo_context

    value = _template()

    first = _create_committed(
        client,
        metadata,
        value,
        key="create-001",
    )

    assert first == value

    persisted = (
        CrmEmailTemplateRegistry.get_template(
            TENANT,
            TEMPLATE_ID,
            metadata,
        )
    )

    assert persisted == value
    assert metadata.count_documents({}) == 1

    second = _create_committed(
        client,
        metadata,
        value,
        key="create-001",
    )

    assert second == first
    assert metadata.count_documents({}) == 1


def test_real_create_divergent_replay_and_identity_conflict(
    mongo_context: tuple[Any, Any, Any, Any],
) -> None:
    client, _, metadata, _ = mongo_context

    baseline = _template()

    _create_committed(
        client,
        metadata,
        baseline,
        key="create-001",
    )

    divergent_key_payload = _template(
        template_id=(
            "WILSYCRM-EMAIL-TEMPLATE-MONGO-002"
        ),
        name="Different Template",
    )

    with pytest.raises(
        CrmEmailTemplateRegistryConflictError
    ):
        _create_committed(
            client,
            metadata,
            divergent_key_payload,
            key="create-001",
        )

    with pytest.raises(
        CrmEmailTemplateRegistryConflictError
    ):
        _create_committed(
            client,
            metadata,
            baseline,
            key="create-002",
        )

    assert metadata.count_documents({}) == 1


def test_real_revision_sequence_replay_divergence_and_history(
    mongo_context: tuple[Any, Any, Any, Any],
) -> None:
    client, _, metadata, revisions = mongo_context

    _create_committed(
        client,
        metadata,
        _template(),
        key="create-001",
    )

    one = _revision(1)
    two = _revision(2)

    assert _append_committed(
        client,
        metadata,
        revisions,
        one,
    ) == one

    raw_one_before = revisions.find_one(
        {
            "tenant_id": TENANT,
            "template_id": TEMPLATE_ID,
            "revision": 1,
        }
    )

    assert raw_one_before is not None

    assert _append_committed(
        client,
        metadata,
        revisions,
        two,
    ) == two

    with pytest.raises(
        CrmEmailTemplateRegistryConflictError
    ):
        _append_committed(
            client,
            metadata,
            revisions,
            _revision(4),
        )

    replay = _append_committed(
        client,
        metadata,
        revisions,
        two,
    )

    assert replay == two

    divergent = _revision(
        2,
        subject="Divergent second revision",
    )

    with pytest.raises(
        CrmEmailTemplateRegistryConflictError
    ):
        _append_committed(
            client,
            metadata,
            revisions,
            divergent,
        )

    assert revisions.count_documents({}) == 2

    raw_one_after = revisions.find_one(
        {
            "tenant_id": TENANT,
            "template_id": TEMPLATE_ID,
            "revision": 1,
        }
    )

    assert raw_one_after == raw_one_before

    latest = (
        CrmEmailTemplateRegistry
        .get_latest_revision(
            TENANT,
            TEMPLATE_ID,
            revisions,
        )
    )

    assert latest == two

    assert [
        item.revision
        for item in (
            CrmEmailTemplateRegistry
            .list_revisions(
                TENANT,
                TEMPLATE_ID,
                revisions,
            )
        )
    ] == [
        2,
        1,
    ]


def test_real_cross_tenant_same_template_identity_is_isolated(
    mongo_context: tuple[Any, Any, Any, Any],
) -> None:
    client, _, metadata, revisions = mongo_context

    left = _template(
        tenant_id=TENANT,
    )

    right = _template(
        tenant_id=OTHER_TENANT,
    )

    _create_committed(
        client,
        metadata,
        left,
        key="left-create",
    )

    _create_committed(
        client,
        metadata,
        right,
        key="right-create",
    )

    _append_committed(
        client,
        metadata,
        revisions,
        _revision(
            1,
            tenant_id=TENANT,
        ),
    )

    _append_committed(
        client,
        metadata,
        revisions,
        _revision(
            1,
            tenant_id=OTHER_TENANT,
        ),
    )

    assert metadata.count_documents({}) == 2
    assert revisions.count_documents({}) == 2

    assert (
        CrmEmailTemplateRegistry.get_template(
            TENANT,
            TEMPLATE_ID,
            metadata,
        )
        == left
    )

    assert (
        CrmEmailTemplateRegistry.get_template(
            OTHER_TENANT,
            TEMPLATE_ID,
            metadata,
        )
        == right
    )

    left_revisions = (
        CrmEmailTemplateRegistry.list_revisions(
            TENANT,
            TEMPLATE_ID,
            revisions,
        )
    )

    right_revisions = (
        CrmEmailTemplateRegistry.list_revisions(
            OTHER_TENANT,
            TEMPLATE_ID,
            revisions,
        )
    )

    assert len(left_revisions) == 1
    assert len(right_revisions) == 1

    assert (
        left_revisions[0].tenant_id
        == TENANT
    )

    assert (
        right_revisions[0].tenant_id
        == OTHER_TENANT
    )


def test_real_raw_metadata_and_revision_corruption_reject(
    mongo_context: tuple[Any, Any, Any, Any],
) -> None:
    client, _, metadata, revisions = mongo_context

    _create_committed(
        client,
        metadata,
        _template(),
        key="create-001",
    )

    _append_committed(
        client,
        metadata,
        revisions,
        _revision(1),
    )

    metadata.update_one(
        {
            "tenant_id": TENANT,
            "template_id": TEMPLATE_ID,
        },
        {
            "$set": {
                "scope": "INVALID",
            },
        },
    )

    with pytest.raises(
        CrmEmailTemplateRegistryCorruptionError
    ):
        CrmEmailTemplateRegistry.get_template(
            TENANT,
            TEMPLATE_ID,
            metadata,
        )

    revisions.update_one(
        {
            "tenant_id": TENANT,
            "template_id": TEMPLATE_ID,
            "revision": 1,
        },
        {
            "$set": {
                "fingerprint": "b" * 128,
            },
        },
    )

    with pytest.raises(
        CrmEmailTemplateRegistryCorruptionError
    ):
        CrmEmailTemplateRegistry.get_revision(
            TENANT,
            TEMPLATE_ID,
            1,
            revisions,
        )


def test_real_competing_create_writers_converge_to_one_durable_identity(
    mongo_context: tuple[Any, Any, Any, Any],
) -> None:
    client, _, metadata, _ = mongo_context

    value = _template(
        template_id=(
            "WILSYCRM-EMAIL-TEMPLATE-RACE-001"
        ),
        name="Concurrent Outreach",
    )

    key = "race-create-001"

    def worker() -> tuple[str, object]:
        try:
            with client.start_session() as session:
                with session.start_transaction():
                    result = (
                        CrmEmailTemplateRegistry
                        .create_template(
                            value,
                            idempotency_key=key,
                            metadata_collection=metadata,
                            session=session,
                        )
                    )

            return (
                "SUCCESS",
                result.to_dict(),
            )

        except (
            CrmEmailTemplateRegistryError,
            PyMongoError,
        ) as error:
            return (
                "GOVERNED_CONFLICT",
                error.__class__.__name__,
            )

    with ThreadPoolExecutor(
        max_workers=2
    ) as pool:
        futures = [
            pool.submit(worker)
            for _ in range(2)
        ]

        results = [
            future.result(
                timeout=15
            )
            for future in futures
        ]

    durable = list(
        metadata.find(
            {
                "tenant_id": TENANT,
                "template_id":
                    value.template_id,
            }
        )
    )

    assert len(durable) == 1

    successes = [
        payload
        for state, payload in results
        if state == "SUCCESS"
    ]

    assert successes

    for payload in successes:
        assert payload == value.to_dict()

    assert all(
        state in {
            "SUCCESS",
            "GOVERNED_CONFLICT",
        }
        for state, _ in results
    )


def test_real_persisted_documents_contain_no_send_or_financial_authority(
    mongo_context: tuple[Any, Any, Any, Any],
) -> None:
    client, _, metadata, revisions = mongo_context

    _create_committed(
        client,
        metadata,
        _template(),
        key="create-001",
    )

    _append_committed(
        client,
        metadata,
        revisions,
        _revision(1),
    )

    metadata_row = metadata.find_one(
        {
            "tenant_id": TENANT,
            "template_id": TEMPLATE_ID,
        }
    )

    revision_row = revisions.find_one(
        {
            "tenant_id": TENANT,
            "template_id": TEMPLATE_ID,
            "revision": 1,
        }
    )

    assert metadata_row is not None
    assert revision_row is not None

    forbidden = {
        "smtp_password",
        "smtp_secret",
        "oauth_token",
        "refresh_token",
        "access_token",
        "provider_credential",
        "mailbox_password",
        "can_send",
        "send_authority",
        "permission",
        "permissions",
        "authorization_role",
        "entitlement",
        "consent",
        "lawful_basis",
        "suppressed",
        "unsubscribe_status",
        "provider_message_id",
        "sent_at",
        "delivered_at",
        "bounced_at",
        "payment_authority",
        "settlement_authority",
        "financial_execution",
    }

    assert forbidden.isdisjoint(
        set(metadata_row)
    )

    assert forbidden.isdisjoint(
        set(revision_row)
    )


def test_real_metadata_cas_commit_advances_once_and_preserves_registry_identity(
    mongo_context: tuple[Any, Any, Any, Any],
) -> None:
    client, _, metadata, revisions = mongo_context

    value = _template(
        template_id="WILSYCRM-EMAIL-TEMPLATE-CAS-001",
        name="CAS Baseline",
    )

    created = _create_committed(
        client,
        metadata,
        value,
        key="cas-create-001",
    )

    _append_committed(
        client,
        metadata,
        revisions,
        _revision(
            1,
            template_id=value.template_id,
        ),
    )

    revision_history_before = list(
        revisions.find(
            {
                "tenant_id": TENANT,
                "template_id": value.template_id,
            }
        )
    )

    raw_before = metadata.find_one(
        {
            "tenant_id": TENANT,
            "template_id": value.template_id,
        }
    )

    assert raw_before is not None

    create_key_before = raw_before[
        "create_idempotency_key"
    ]

    with client.start_session() as session:
        with session.start_transaction():
            revised = (
                CrmEmailTemplateRegistry
                .revise_template_metadata(
                    TENANT,
                    value.template_id,
                    created.metadata_revision,
                    created.metadata_fingerprint,
                    NOW + timedelta(minutes=1),
                    metadata,
                    session,
                    name="CAS Revised",
                    folder="Renewal",
                    tags=(
                        "cas",
                        "revised",
                    ),
                )
            )

    assert (
        revised.metadata_revision
        == created.metadata_revision + 1
    )

    assert (
        revised.metadata_fingerprint
        != created.metadata_fingerprint
    )

    assert revised.name == "CAS Revised"
    assert revised.folder == "Renewal"
    assert revised.tags == (
        "cas",
        "revised",
    )

    durable = (
        CrmEmailTemplateRegistry
        .get_template(
            TENANT,
            value.template_id,
            metadata,
        )
    )

    assert durable == revised

    raw_after = metadata.find_one(
        {
            "tenant_id": TENANT,
            "template_id": value.template_id,
        }
    )

    assert raw_after is not None

    assert (
        raw_after["create_idempotency_key"]
        == create_key_before
        == "cas-create-001"
    )

    assert (
        raw_after["metadata_revision"]
        == created.metadata_revision + 1
    )

    assert (
        raw_after["metadata_fingerprint"]
        == revised.metadata_fingerprint
    )

    revision_history_after = list(
        revisions.find(
            {
                "tenant_id": TENANT,
                "template_id": value.template_id,
            }
        )
    )

    assert (
        revision_history_after
        == revision_history_before
    )


def test_real_metadata_cas_stale_coordinates_and_wrong_tenant_fail_closed(
    mongo_context: tuple[Any, Any, Any, Any],
) -> None:
    client, _, metadata, _ = mongo_context

    value = _template(
        template_id="WILSYCRM-EMAIL-TEMPLATE-CAS-002",
        name="CAS Guard",
    )

    created = _create_committed(
        client,
        metadata,
        value,
        key="cas-create-002",
    )

    original = metadata.find_one(
        {
            "tenant_id": TENANT,
            "template_id": value.template_id,
        }
    )

    assert original is not None

    with pytest.raises(
        CrmEmailTemplateRegistryConflictError
    ):
        with client.start_session() as session:
            with session.start_transaction():
                (
                    CrmEmailTemplateRegistry
                    .revise_template_metadata(
                        TENANT,
                        value.template_id,
                        created.metadata_revision + 1,
                        created.metadata_fingerprint,
                        NOW + timedelta(minutes=1),
                        metadata,
                        session,
                        name="Stale Revision",
                    )
                )

    with pytest.raises(
        CrmEmailTemplateRegistryConflictError
    ):
        with client.start_session() as session:
            with session.start_transaction():
                (
                    CrmEmailTemplateRegistry
                    .revise_template_metadata(
                        TENANT,
                        value.template_id,
                        created.metadata_revision,
                        "f" * 128,
                        NOW + timedelta(minutes=1),
                        metadata,
                        session,
                        name="Stale Fingerprint",
                    )
                )

    other_tenant = (
        f"{TENANT}-cas-other"
    )

    with pytest.raises(
        CrmEmailTemplateRegistryError
    ):
        with client.start_session() as session:
            with session.start_transaction():
                (
                    CrmEmailTemplateRegistry
                    .revise_template_metadata(
                        other_tenant,
                        value.template_id,
                        created.metadata_revision,
                        created.metadata_fingerprint,
                        NOW + timedelta(minutes=1),
                        metadata,
                        session,
                        name="Cross Tenant",
                    )
                )

    durable = metadata.find_one(
        {
            "tenant_id": TENANT,
            "template_id": value.template_id,
        }
    )

    assert durable == original

    assert (
        metadata.count_documents(
            {
                "tenant_id": other_tenant,
                "template_id": value.template_id,
            }
        )
        == 0
    )


def test_real_metadata_cas_archive_is_state_and_revision_history_is_immutable(
    mongo_context: tuple[Any, Any, Any, Any],
) -> None:
    client, _, metadata, revisions = mongo_context

    value = _template(
        template_id="WILSYCRM-EMAIL-TEMPLATE-CAS-003",
        name="Archive Candidate",
    )

    created = _create_committed(
        client,
        metadata,
        value,
        key="cas-create-003",
    )

    _append_committed(
        client,
        metadata,
        revisions,
        _revision(
            1,
            template_id=value.template_id,
        ),
    )

    history_before = list(
        revisions.find(
            {
                "tenant_id": TENANT,
                "template_id": value.template_id,
            }
        )
    )

    with client.start_session() as session:
        with session.start_transaction():
            archived = (
                CrmEmailTemplateRegistry
                .revise_template_metadata(
                    TENANT,
                    value.template_id,
                    created.metadata_revision,
                    created.metadata_fingerprint,
                    NOW + timedelta(minutes=1),
                    metadata,
                    session,
                    lifecycle=(
                        CrmEmailTemplateLifecycle.ARCHIVED
                    ),
                )
            )

    assert (
        archived.lifecycle
        is CrmEmailTemplateLifecycle.ARCHIVED
    )

    assert (
        archived.metadata_revision
        == created.metadata_revision + 1
    )

    assert (
        metadata.count_documents(
            {
                "tenant_id": TENANT,
                "template_id": value.template_id,
            }
        )
        == 1
    )

    durable = (
        CrmEmailTemplateRegistry
        .get_template(
            TENANT,
            value.template_id,
            metadata,
        )
    )

    assert durable == archived

    history_after = list(
        revisions.find(
            {
                "tenant_id": TENANT,
                "template_id": value.template_id,
            }
        )
    )

    assert history_after == history_before


def test_real_metadata_cas_competing_writers_converge_to_one_successor(
    mongo_context: tuple[Any, Any, Any, Any],
) -> None:
    client, _, metadata, _ = mongo_context

    value = _template(
        template_id="WILSYCRM-EMAIL-TEMPLATE-CAS-RACE-001",
        name="CAS Race Baseline",
    )

    created = _create_committed(
        client,
        metadata,
        value,
        key="cas-race-create-001",
    )

    def worker(
        name: str,
    ) -> tuple[str, object]:
        try:
            with client.start_session() as session:
                with session.start_transaction():
                    revised = (
                        CrmEmailTemplateRegistry
                        .revise_template_metadata(
                            TENANT,
                            value.template_id,
                            created.metadata_revision,
                            created.metadata_fingerprint,
                            NOW + timedelta(minutes=1),
                            metadata,
                            session,
                            name=name,
                        )
                    )

            return (
                "SUCCESS",
                revised.to_dict(),
            )

        except CrmEmailTemplateRegistryConflictError as error:
            return (
                "CONFLICT",
                error.__class__.__name__,
            )

        except PyMongoError as error:
            return (
                "MONGO_CONFLICT",
                error.__class__.__name__,
            )

    with ThreadPoolExecutor(
        max_workers=2
    ) as pool:
        futures = [
            pool.submit(
                worker,
                name,
            )
            for name in (
                "CAS Writer A",
                "CAS Writer B",
            )
        ]

        results = [
            future.result(
                timeout=15
            )
            for future in futures
        ]

    successes = [
        payload
        for state, payload in results
        if state == "SUCCESS"
    ]

    losers = [
        state
        for state, _ in results
        if state in {
            "CONFLICT",
            "MONGO_CONFLICT",
        }
    ]

    assert len(successes) == 1
    assert len(losers) == 1

    durable_rows = list(
        metadata.find(
            {
                "tenant_id": TENANT,
                "template_id": value.template_id,
            }
        )
    )

    assert len(durable_rows) == 1

    durable = (
        CrmEmailTemplateRegistry
        .get_template(
            TENANT,
            value.template_id,
            metadata,
        )
    )

    assert durable is not None

    assert (
        durable.metadata_revision
        == created.metadata_revision + 1
    )

    assert (
        durable.metadata_fingerprint
        != created.metadata_fingerprint
    )

    assert durable.name in {
        "CAS Writer A",
        "CAS Writer B",
    }

    assert (
        durable_rows[0][
            "create_idempotency_key"
        ]
        == "cas-race-create-001"
    )




def test_real_transactional_reads_observe_caller_session_and_preserve_isolation(
    mongo_context: tuple[Any, Any, Any, Any],
) -> None:
    """Certify real-Mongo caller-session visibility and isolation.

    The writer's exact Mongo session must observe its own uncommitted
    metadata and immutable revision. A distinct observer session must
    not observe those uncommitted rows. Abort must leave no durable
    state. A later committed transaction must become durable while
    preserving exact tenant isolation across all public read APIs.

    This certificate grants no permission, entitlement, sharing,
    mailbox, consent, sequence, AI-send or financial authority.
    """
    client, _, metadata, revisions = mongo_context

    template = _template()
    revision = _revision(1)

    # Phase A: uncommitted writer visibility.
    with client.start_session() as writer:
        writer.start_transaction()

        created = CrmEmailTemplateRegistry.create_template(
            template,
            idempotency_key="tx-read-abort-create-001",
            metadata_collection=metadata,
            session=writer,
        )

        appended = CrmEmailTemplateRegistry.append_revision(
            revision,
            metadata_collection=metadata,
            revision_collection=revisions,
            session=writer,
        )

        assert created == template
        assert appended == revision

        # All five public reads must see the transaction's own writes.
        assert (
            CrmEmailTemplateRegistry.get_template(
                TENANT,
                TEMPLATE_ID,
                metadata,
                session=writer,
            )
            == template
        )

        assert (
            CrmEmailTemplateRegistry.list_templates(
                TENANT,
                metadata,
                session=writer,
            )
            == (template,)
        )

        assert (
            CrmEmailTemplateRegistry.get_revision(
                TENANT,
                TEMPLATE_ID,
                1,
                revisions,
                session=writer,
            )
            == revision
        )

        assert (
            CrmEmailTemplateRegistry.get_latest_revision(
                TENANT,
                TEMPLATE_ID,
                revisions,
                session=writer,
            )
            == revision
        )

        assert (
            CrmEmailTemplateRegistry.list_revisions(
                TENANT,
                TEMPLATE_ID,
                revisions,
                session=writer,
            )
            == (revision,)
        )

        # A distinct caller session must not observe uncommitted rows.
        with client.start_session() as observer:
            assert (
                CrmEmailTemplateRegistry.get_template(
                    TENANT,
                    TEMPLATE_ID,
                    metadata,
                    session=observer,
                )
                is None
            )

            assert (
                CrmEmailTemplateRegistry.list_templates(
                    TENANT,
                    metadata,
                    session=observer,
                )
                == ()
            )

            assert (
                CrmEmailTemplateRegistry.get_revision(
                    TENANT,
                    TEMPLATE_ID,
                    1,
                    revisions,
                    session=observer,
                )
                is None
            )

            assert (
                CrmEmailTemplateRegistry.get_latest_revision(
                    TENANT,
                    TEMPLATE_ID,
                    revisions,
                    session=observer,
                )
                is None
            )

            assert (
                CrmEmailTemplateRegistry.list_revisions(
                    TENANT,
                    TEMPLATE_ID,
                    revisions,
                    session=observer,
                )
                == ()
            )

        writer.abort_transaction()

    # Abort must leave no durable metadata or revision history.
    assert metadata.count_documents({}) == 0
    assert revisions.count_documents({}) == 0

    assert (
        CrmEmailTemplateRegistry.get_template(
            TENANT,
            TEMPLATE_ID,
            metadata,
        )
        is None
    )

    assert (
        CrmEmailTemplateRegistry.list_revisions(
            TENANT,
            TEMPLATE_ID,
            revisions,
        )
        == ()
    )

    # Phase B: commit the same logical domain values under a fresh key.
    with client.start_session() as writer:
        writer.start_transaction()

        created = CrmEmailTemplateRegistry.create_template(
            template,
            idempotency_key="tx-read-commit-create-001",
            metadata_collection=metadata,
            session=writer,
        )

        appended = CrmEmailTemplateRegistry.append_revision(
            revision,
            metadata_collection=metadata,
            revision_collection=revisions,
            session=writer,
        )

        assert created == template
        assert appended == revision

        # Same-session read-your-own-write remains true before commit.
        assert (
            CrmEmailTemplateRegistry.get_template(
                TENANT,
                TEMPLATE_ID,
                metadata,
                session=writer,
            )
            == template
        )

        assert (
            CrmEmailTemplateRegistry.get_latest_revision(
                TENANT,
                TEMPLATE_ID,
                revisions,
                session=writer,
            )
            == revision
        )

        writer.commit_transaction()

    # Committed state becomes durable.
    assert metadata.count_documents({}) == 1
    assert revisions.count_documents({}) == 1

    assert (
        CrmEmailTemplateRegistry.get_template(
            TENANT,
            TEMPLATE_ID,
            metadata,
        )
        == template
    )

    assert (
        CrmEmailTemplateRegistry.list_templates(
            TENANT,
            metadata,
        )
        == (template,)
    )

    assert (
        CrmEmailTemplateRegistry.get_revision(
            TENANT,
            TEMPLATE_ID,
            1,
            revisions,
        )
        == revision
    )

    assert (
        CrmEmailTemplateRegistry.get_latest_revision(
            TENANT,
            TEMPLATE_ID,
            revisions,
        )
        == revision
    )

    assert (
        CrmEmailTemplateRegistry.list_revisions(
            TENANT,
            TEMPLATE_ID,
            revisions,
        )
        == (revision,)
    )

    # Identical resource coordinates in another tenant remain invisible.
    assert (
        CrmEmailTemplateRegistry.get_template(
            OTHER_TENANT,
            TEMPLATE_ID,
            metadata,
        )
        is None
    )

    assert (
        CrmEmailTemplateRegistry.list_templates(
            OTHER_TENANT,
            metadata,
        )
        == ()
    )

    assert (
        CrmEmailTemplateRegistry.get_revision(
            OTHER_TENANT,
            TEMPLATE_ID,
            1,
            revisions,
        )
        is None
    )

    assert (
        CrmEmailTemplateRegistry.get_latest_revision(
            OTHER_TENANT,
            TEMPLATE_ID,
            revisions,
        )
        is None
    )

    assert (
        CrmEmailTemplateRegistry.list_revisions(
            OTHER_TENANT,
            TEMPLATE_ID,
            revisions,
        )
        == ()
    )


# ARTIFACT: test_crm_email_template_registry_real_mongo.py
# VERSION: v1.1.0-P0-CRM-EMAIL-TEMPLATE-REGISTRY-REAL-MONGO
# DATABASE: UUID-isolated disposable real Mongo database
# MONGO ENV CONTRACT: TEST_VENDOR_MONGO_URI
# REPLICA SET: wilsyVendorCertRS; canonical local fallback 127.0.0.1:27027
# TRANSACTION POSTURE: caller-owned active Mongo transactions
# TRANSACTIONAL READS: exact caller-session visibility + observer isolation
# REPLAY: exact create/revision replay; divergence fails closed
# HISTORY: append-only monotonic immutable revisions
# TENANT POSTURE: same identity may exist independently across tenants
# CONCURRENCY: one durable identity under competing real writers
# RETENTION: no TTL/delete/purge registry authority
# SEND/MAILBOX/CONSENT/AI AUTHORITY: none
# FINANCIAL EXECUTION AUTHORITY: none; Kennel EOS remains exclusive
# END OF WILSY OS SOVEREIGN CERTIFICATE
