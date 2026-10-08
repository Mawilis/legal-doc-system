"""
TITLE: WILSY OS CRM Email Template Registry Direct Certificate
VERSION: v1.0.0-P0-CRM-EMAIL-TEMPLATE-REGISTRY-CERT

AUTHORITY:
    Test-first persistence contract for tenant-bound CRM email-template
    metadata creation and immutable published-revision history.

EPITOME:
    Freezes durable template identity, exact replay, strict hydration,
    monotonic revision history, caller-owned transaction boundaries and
    tenant-isolated reads without inventing send or mailbox authority.

ABSOLUTE CANONICAL PATH:
    /Users/wilsonkhanyezi/legal-doc-system/tests/unit/test_crm_email_template_registry.py

RESEARCH BASIS:
    - Apollo template ownership, folders/tags, permissions, link/copy behavior.
    - lemlist copy/workspace-isolation behavior.
    - WILSY CRM Lead registry.
    - WILSY HR immutable document registry.
    - WILSY caller-owned transaction and CAS precedents.

V1 MUTATION BOUNDARY:
    This registry may:
        - create immutable template metadata identity;
        - exactly replay that create through a registry-owned idempotency key;
        - append immutable content revisions;
        - read/list tenant-bound metadata/revisions.

    This registry may NOT yet mutate existing template metadata.

WHY:
    CrmEmailTemplate v1 does not yet expose a metadata revision/fingerprint
    suitable for lossless current-state CAS. Folder/tag/scope/owner/team/archive
    mutations therefore require a separately researched metadata-CAS contract.

REVISION DOCTRINE:
    First published content revision is 1.
    Every fresh later revision must equal current latest revision + 1.
    Gaps, rewinds and divergent duplicate revision identities fail closed.

ARCHIVE DOCTRINE:
    ARCHIVED exists in the pure domain but the registry does not perform the
    transition in v1. No blind replacement of current metadata is permitted.

DELETE DOCTRINE:
    No delete, purge or TTL authority.

TRANSACTION DOCTRINE:
    Every write requires a caller-provided active Mongo transaction.

SEND BOUNDARY:
    Persistence never grants permission or email-send authority.

FINANCIAL AUTHORITY BOUNDARY:
    None. Kennel EOS remains exclusive financial execution authority.
"""

from __future__ import annotations

import inspect
from datetime import datetime, timedelta, timezone
from typing import Any

import pytest

from tools.eos.crm.domain.crm_email_template import (
    CrmEmailTemplate,
    CrmEmailTemplateError,
    CrmEmailTemplateLifecycle,
    CrmEmailTemplateOrigin,
    CrmEmailTemplateRevision,
    CrmEmailTemplateScope,
)

from tools.eos.crm.persistence.crm_email_template_registry import (
    CRM_EMAIL_TEMPLATE_METADATA_COLLECTION,
    CRM_EMAIL_TEMPLATE_REGISTRY_VERSION,
    CRM_EMAIL_TEMPLATE_REVISION_COLLECTION,
    CrmEmailTemplateRegistry,
    CrmEmailTemplateRegistryConflictError,
    CrmEmailTemplateRegistryCorruptionError,
    CrmEmailTemplateRegistryError,
    CrmEmailTemplateRegistryTransactionError,
)


TENANT = "WILSYTENANT-CRM-EMAIL-REG-001"
OTHER_TENANT = "WILSYTENANT-CRM-EMAIL-REG-002"
TEMPLATE_ID = "WILSYCRM-EMAIL-TEMPLATE-001"
OWNER = "principal-sales-001"
NOW = datetime(
    2026,
    10,
    7,
    1,
    0,
    tzinfo=timezone.utc,
)

EXPECTED_VERSION = (
    "v1.1.0-CRM-EMAIL-TEMPLATE-REGISTRY"
)

SOURCE_FP = "a" * 128


class FakeReplaceResult:
    def __init__(
        self,
        matched_count: int,
        modified_count: int,
    ):
        self.matched_count = matched_count
        self.modified_count = modified_count


class FakeInsertResult:
    def __init__(self, inserted_id: object):
        self.inserted_id = inserted_id


class FakeCursor:
    """Minimal Mongo-style cursor without overriding list.sort."""

    def __init__(
        self,
        rows: list[dict[str, object]],
    ) -> None:
        self._rows = rows

    def __iter__(self):
        return iter(self._rows)

    def sort(
        self,
        key: str,
        direction: int,
    ) -> "FakeCursor":
        reverse = direction < 0

        def sortable(
            row: dict[str, object],
        ) -> tuple[int, str]:
            value = row.get(key)

            if value is None:
                return (0, "")

            return (1, str(value))

        self._rows.sort(
            key=sortable,
            reverse=reverse,
        )

        return self


class FakeCollection:
    """Small deterministic PyMongo-like test double."""

    def __init__(self) -> None:
        self.docs: list[dict[str, object]] = []
        self.indexes: list[
            tuple[
                tuple[tuple[str, int], ...],
                dict[str, object],
            ]
        ] = []
        self.read_calls = 0
        self.write_calls = 0

    def create_index(
        self,
        keys: list[tuple[str, int]],
        **kwargs: object,
    ) -> str:
        self.indexes.append(
            (
                tuple(keys),
                dict(kwargs),
            )
        )

        return str(
            kwargs.get("name", "unnamed")
        )

    @staticmethod
    def _matches(
        row: dict[str, object],
        query: dict[str, object],
    ) -> bool:
        return all(
            row.get(key) == value
            for key, value in query.items()
        )

    def find_one(
        self,
        query: dict[str, object],
        **kwargs: object,
    ) -> dict[str, object] | None:
        del kwargs
        self.read_calls += 1

        for row in self.docs:
            if self._matches(row, query):
                return dict(row)

        return None

    def find(
        self,
        query: dict[str, object],
        **kwargs: object,
    ) -> FakeCursor:
        del kwargs
        self.read_calls += 1

        return FakeCursor(
            [
                dict(row)
                for row in self.docs
                if self._matches(row, query)
            ]
        )

    def insert_one(
        self,
        document: dict[str, object],
        **kwargs: object,
    ) -> FakeInsertResult:
        del kwargs
        self.write_calls += 1
        self.docs.append(
            dict(document)
        )

        return FakeInsertResult(
            len(self.docs)
        )

    def replace_one(
        self,
        query: dict[str, object],
        document: dict[str, object],
        *,
        upsert: bool = False,
        **kwargs: object,
    ) -> FakeReplaceResult:
        del kwargs

        if upsert is not False:
            raise AssertionError(
                "TEST_DOUBLE_FORBIDS_UPSERT"
            )

        self.write_calls += 1

        for index, row in enumerate(
            self.docs
        ):
            if self._matches(
                row,
                query,
            ):
                self.docs[index] = dict(
                    document
                )

                return FakeReplaceResult(
                    matched_count=1,
                    modified_count=1,
                )

        return FakeReplaceResult(
            matched_count=0,
            modified_count=0,
        )


class ActiveSession:
    in_transaction = True


class InactiveSession:
    in_transaction = False


def _template(
    *,
    tenant_id: str = TENANT,
    template_id: str = TEMPLATE_ID,
    scope: CrmEmailTemplateScope = (
        CrmEmailTemplateScope.USER_PRIVATE
    ),
    origin: CrmEmailTemplateOrigin = (
        CrmEmailTemplateOrigin.TENANT_CREATED
    ),
    lifecycle: CrmEmailTemplateLifecycle = (
        CrmEmailTemplateLifecycle.ACTIVE
    ),
    owner_principal_id: str | None = OWNER,
    team_id: str | None = None,
) -> CrmEmailTemplate:
    return CrmEmailTemplate.create(
        tenant_id=tenant_id,
        template_id=template_id,
        name="Initial Outreach",
        scope=scope,
        origin=origin,
        lifecycle=lifecycle,
        owner_principal_id=owner_principal_id,
        team_id=team_id,
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
        else f"Revision {revision} for {{{{lead.first_name}}}}"
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
            f"template-author:{OWNER}:revision:{revision}"
        ),
        source_fingerprint=SOURCE_FP,
        published_at=NOW,
    )


def _collections():
    return (
        FakeCollection(),
        FakeCollection(),
    )


def _revise_template_metadata(
    *args: Any,
    **kwargs: Any,
) -> Any:
    """Invoke the intentionally absent production CAS method dynamically."""

    method = getattr(
        CrmEmailTemplateRegistry,
        "revise_template_metadata",
    )

    return method(
        *args,
        **kwargs,
    )


def test_registry_identity_is_exact() -> None:
    assert (
        CRM_EMAIL_TEMPLATE_REGISTRY_VERSION
        == EXPECTED_VERSION
    )

    assert (
        CRM_EMAIL_TEMPLATE_METADATA_COLLECTION
        == "crm_email_templates"
    )

    assert (
        CRM_EMAIL_TEMPLATE_REVISION_COLLECTION
        == "crm_email_template_revisions"
    )


def test_registry_public_surface_is_closed() -> None:
    expected = {
        "append_revision",
        "create_template",
        "ensure_indexes",
        "get_latest_revision",
        "get_revision",
        "get_template",
        "list_revisions",
        "list_templates",
        "revise_template_metadata",
    }

    public = {
        name
        for name, member in inspect.getmembers(
            CrmEmailTemplateRegistry
        )
        if (
            not name.startswith("_")
            and callable(member)
        )
    }

    assert public == expected


def test_registry_exposes_no_delete_or_metadata_mutation_surface() -> None:
    forbidden = {
        "delete",
        "delete_template",
        "purge",
        "archive",
        "restore",
        "update_template",
        "replace_template",
        "set_scope",
        "set_owner",
        "set_team",
        "set_folder",
        "set_tags",
    }

    assert forbidden.isdisjoint(
        set(dir(CrmEmailTemplateRegistry))
    )


def test_indexes_are_exact_and_tenant_bound() -> None:
    metadata, revisions = _collections()

    CrmEmailTemplateRegistry.ensure_indexes(
        metadata,
        revisions,
    )

    metadata_indexes = {
        str(options["name"]):
            (keys, options)
        for keys, options in metadata.indexes
    }

    revision_indexes = {
        str(options["name"]):
            (keys, options)
        for keys, options in revisions.indexes
    }

    assert (
        metadata_indexes[
            "crm_email_template_tenant_identity_unique"
        ][0]
        == (
            ("tenant_id", 1),
            ("template_id", 1),
        )
    )

    assert (
        metadata_indexes[
            "crm_email_template_tenant_identity_unique"
        ][1]["unique"]
        is True
    )

    assert (
        metadata_indexes[
            "crm_email_template_tenant_create_idempotency_unique"
        ][0]
        == (
            ("tenant_id", 1),
            ("create_idempotency_key", 1),
        )
    )

    assert (
        metadata_indexes[
            "crm_email_template_tenant_create_idempotency_unique"
        ][1]["unique"]
        is True
    )

    assert (
        revision_indexes[
            "crm_email_template_revision_identity_unique"
        ][0]
        == (
            ("tenant_id", 1),
            ("template_id", 1),
            ("revision", 1),
        )
    )

    assert (
        revision_indexes[
            "crm_email_template_revision_identity_unique"
        ][1]["unique"]
        is True
    )

    assert (
        revision_indexes[
            "crm_email_template_revision_fingerprint_unique"
        ][0]
        == (
            ("tenant_id", 1),
            ("template_id", 1),
            ("fingerprint", 1),
        )
    )

    assert (
        revision_indexes[
            "crm_email_template_revision_fingerprint_unique"
        ][1]["unique"]
        is True
    )

    assert (
        revision_indexes[
            "crm_email_template_revision_read"
        ][0]
        == (
            ("tenant_id", 1),
            ("template_id", 1),
            ("revision", -1),
        )
    )


def test_metadata_read_indexes_cover_operational_filters() -> None:
    metadata, revisions = _collections()

    CrmEmailTemplateRegistry.ensure_indexes(
        metadata,
        revisions,
    )

    keys = {
        tuple(spec)
        for spec, options in metadata.indexes
        if options.get("unique") is not True
    }

    assert (
        ("tenant_id", 1),
        ("scope", 1),
        ("lifecycle", 1),
    ) in keys

    assert (
        ("tenant_id", 1),
        ("owner_principal_id", 1),
        ("lifecycle", 1),
    ) in keys

    assert (
        ("tenant_id", 1),
        ("team_id", 1),
        ("lifecycle", 1),
    ) in keys

    assert (
        ("tenant_id", 1),
        ("folder", 1),
        ("lifecycle", 1),
    ) in keys


@pytest.mark.parametrize(
    "session",
    (
        None,
        InactiveSession(),
    ),
)
def test_create_requires_active_caller_transaction_before_io(
    session: object,
) -> None:
    metadata, revisions = _collections()
    del revisions

    with pytest.raises(
        CrmEmailTemplateRegistryTransactionError
    ):
        CrmEmailTemplateRegistry.create_template(
            _template(),
            idempotency_key="template-create-001",
            metadata_collection=metadata,
            session=session,
        )

    assert metadata.read_calls == 0
    assert metadata.write_calls == 0


@pytest.mark.parametrize(
    "session",
    (
        None,
        InactiveSession(),
    ),
)
def test_revision_append_requires_active_transaction_before_io(
    session: object,
) -> None:
    metadata, revisions = _collections()

    with pytest.raises(
        CrmEmailTemplateRegistryTransactionError
    ):
        CrmEmailTemplateRegistry.append_revision(
            _revision(1),
            metadata_collection=metadata,
            revision_collection=revisions,
            session=session,
        )

    assert metadata.read_calls == 0
    assert metadata.write_calls == 0
    assert revisions.read_calls == 0
    assert revisions.write_calls == 0


def test_create_persists_exact_domain_payload_and_registry_replay_key() -> None:
    metadata, revisions = _collections()
    del revisions

    expected = _template()

    actual = CrmEmailTemplateRegistry.create_template(
        expected,
        idempotency_key="template-create-001",
        metadata_collection=metadata,
        session=ActiveSession(),
    )

    assert actual == expected
    assert len(metadata.docs) == 1

    row = metadata.docs[0]

    assert row["tenant_id"] == TENANT
    assert row["template_id"] == TEMPLATE_ID
    assert (
        row["create_idempotency_key"]
        == "template-create-001"
    )

    domain_payload = {
        key: value
        for key, value in row.items()
        if key != "create_idempotency_key"
    }

    assert domain_payload == expected.to_dict()


def test_create_exact_idempotency_replay_returns_existing_without_write() -> None:
    metadata, revisions = _collections()
    del revisions

    value = _template()

    first = CrmEmailTemplateRegistry.create_template(
        value,
        idempotency_key="template-create-001",
        metadata_collection=metadata,
        session=ActiveSession(),
    )

    writes = metadata.write_calls

    second = CrmEmailTemplateRegistry.create_template(
        value,
        idempotency_key="template-create-001",
        metadata_collection=metadata,
        session=ActiveSession(),
    )

    assert second == first
    assert metadata.write_calls == writes


def test_create_divergent_idempotency_replay_fails_closed() -> None:
    metadata, revisions = _collections()
    del revisions

    CrmEmailTemplateRegistry.create_template(
        _template(),
        idempotency_key="template-create-001",
        metadata_collection=metadata,
        session=ActiveSession(),
    )

    divergent = CrmEmailTemplate.create(
        tenant_id=TENANT,
        template_id="WILSYCRM-EMAIL-TEMPLATE-002",
        name="Different",
        scope=CrmEmailTemplateScope.USER_PRIVATE,
        origin=CrmEmailTemplateOrigin.TENANT_CREATED,
        lifecycle=CrmEmailTemplateLifecycle.ACTIVE,
        owner_principal_id=OWNER,
        team_id=None,
        folder="Outbound",
        tags=(),
        created_at=NOW,
    )

    with pytest.raises(
        CrmEmailTemplateRegistryConflictError
    ):
        CrmEmailTemplateRegistry.create_template(
            divergent,
            idempotency_key="template-create-001",
            metadata_collection=metadata,
            session=ActiveSession(),
        )


def test_create_same_template_identity_with_different_create_key_conflicts() -> None:
    metadata, revisions = _collections()
    del revisions

    value = _template()

    CrmEmailTemplateRegistry.create_template(
        value,
        idempotency_key="template-create-001",
        metadata_collection=metadata,
        session=ActiveSession(),
    )

    with pytest.raises(
        CrmEmailTemplateRegistryConflictError
    ):
        CrmEmailTemplateRegistry.create_template(
            value,
            idempotency_key="template-create-002",
            metadata_collection=metadata,
            session=ActiveSession(),
        )


def test_get_template_is_exactly_tenant_bound() -> None:
    metadata, revisions = _collections()
    del revisions

    CrmEmailTemplateRegistry.create_template(
        _template(),
        idempotency_key="template-create-001",
        metadata_collection=metadata,
        session=ActiveSession(),
    )

    assert (
        CrmEmailTemplateRegistry.get_template(
            TENANT,
            TEMPLATE_ID,
            metadata,
        )
        == _template()
    )

    assert (
        CrmEmailTemplateRegistry.get_template(
            OTHER_TENANT,
            TEMPLATE_ID,
            metadata,
        )
        is None
    )


def test_list_templates_never_crosses_tenants() -> None:
    metadata, revisions = _collections()
    del revisions

    for tenant, template_id, key in (
        (
            TENANT,
            "WILSYCRM-EMAIL-TEMPLATE-001",
            "create-a",
        ),
        (
            TENANT,
            "WILSYCRM-EMAIL-TEMPLATE-002",
            "create-b",
        ),
        (
            OTHER_TENANT,
            "WILSYCRM-EMAIL-TEMPLATE-003",
            "create-c",
        ),
    ):
        CrmEmailTemplateRegistry.create_template(
            _template(
                tenant_id=tenant,
                template_id=template_id,
            ),
            idempotency_key=key,
            metadata_collection=metadata,
            session=ActiveSession(),
        )

    rows = CrmEmailTemplateRegistry.list_templates(
        TENANT,
        metadata,
    )

    assert {
        item.template_id
        for item in rows
    } == {
        "WILSYCRM-EMAIL-TEMPLATE-001",
        "WILSYCRM-EMAIL-TEMPLATE-002",
    }


def test_first_revision_requires_existing_same_tenant_template() -> None:
    metadata, revisions = _collections()

    with pytest.raises(
        CrmEmailTemplateRegistryConflictError
    ):
        CrmEmailTemplateRegistry.append_revision(
            _revision(1),
            metadata_collection=metadata,
            revision_collection=revisions,
            session=ActiveSession(),
        )

    assert revisions.write_calls == 0


def test_first_revision_must_be_one() -> None:
    metadata, revisions = _collections()

    CrmEmailTemplateRegistry.create_template(
        _template(),
        idempotency_key="template-create-001",
        metadata_collection=metadata,
        session=ActiveSession(),
    )

    with pytest.raises(
        CrmEmailTemplateRegistryConflictError
    ):
        CrmEmailTemplateRegistry.append_revision(
            _revision(2),
            metadata_collection=metadata,
            revision_collection=revisions,
            session=ActiveSession(),
        )

    assert revisions.write_calls == 0


def test_append_revision_persists_exact_immutable_domain_payload() -> None:
    metadata, revisions = _collections()

    CrmEmailTemplateRegistry.create_template(
        _template(),
        idempotency_key="template-create-001",
        metadata_collection=metadata,
        session=ActiveSession(),
    )

    value = _revision(1)

    actual = CrmEmailTemplateRegistry.append_revision(
        value,
        metadata_collection=metadata,
        revision_collection=revisions,
        session=ActiveSession(),
    )

    assert actual == value
    assert revisions.docs == [
        value.to_dict()
    ]


def test_revision_append_is_strictly_monotonic_without_gaps() -> None:
    metadata, revisions = _collections()

    CrmEmailTemplateRegistry.create_template(
        _template(),
        idempotency_key="template-create-001",
        metadata_collection=metadata,
        session=ActiveSession(),
    )

    one = _revision(1)
    two = _revision(2)

    CrmEmailTemplateRegistry.append_revision(
        one,
        metadata_collection=metadata,
        revision_collection=revisions,
        session=ActiveSession(),
    )

    CrmEmailTemplateRegistry.append_revision(
        two,
        metadata_collection=metadata,
        revision_collection=revisions,
        session=ActiveSession(),
    )

    with pytest.raises(
        CrmEmailTemplateRegistryConflictError
    ):
        CrmEmailTemplateRegistry.append_revision(
            _revision(4),
            metadata_collection=metadata,
            revision_collection=revisions,
            session=ActiveSession(),
        )

    assert len(revisions.docs) == 2


def test_exact_revision_replay_returns_existing_without_new_write() -> None:
    metadata, revisions = _collections()

    CrmEmailTemplateRegistry.create_template(
        _template(),
        idempotency_key="template-create-001",
        metadata_collection=metadata,
        session=ActiveSession(),
    )

    value = _revision(1)

    first = CrmEmailTemplateRegistry.append_revision(
        value,
        metadata_collection=metadata,
        revision_collection=revisions,
        session=ActiveSession(),
    )

    writes = revisions.write_calls

    second = CrmEmailTemplateRegistry.append_revision(
        value,
        metadata_collection=metadata,
        revision_collection=revisions,
        session=ActiveSession(),
    )

    assert second == first
    assert revisions.write_calls == writes


def test_divergent_same_revision_identity_fails_closed() -> None:
    metadata, revisions = _collections()

    CrmEmailTemplateRegistry.create_template(
        _template(),
        idempotency_key="template-create-001",
        metadata_collection=metadata,
        session=ActiveSession(),
    )

    CrmEmailTemplateRegistry.append_revision(
        _revision(1),
        metadata_collection=metadata,
        revision_collection=revisions,
        session=ActiveSession(),
    )

    with pytest.raises(
        CrmEmailTemplateRegistryConflictError
    ):
        CrmEmailTemplateRegistry.append_revision(
            _revision(
                1,
                subject="Different revision-one content",
            ),
            metadata_collection=metadata,
            revision_collection=revisions,
            session=ActiveSession(),
        )

    assert len(revisions.docs) == 1


def test_revision_reads_are_tenant_bound_and_latest_is_highest() -> None:
    metadata, revisions = _collections()

    CrmEmailTemplateRegistry.create_template(
        _template(),
        idempotency_key="template-create-001",
        metadata_collection=metadata,
        session=ActiveSession(),
    )

    for number in (1, 2, 3):
        CrmEmailTemplateRegistry.append_revision(
            _revision(number),
            metadata_collection=metadata,
            revision_collection=revisions,
            session=ActiveSession(),
        )

    assert (
        CrmEmailTemplateRegistry.get_revision(
            TENANT,
            TEMPLATE_ID,
            2,
            revisions,
        )
        == _revision(2)
    )

    assert (
        CrmEmailTemplateRegistry.get_revision(
            OTHER_TENANT,
            TEMPLATE_ID,
            2,
            revisions,
        )
        is None
    )

    assert (
        CrmEmailTemplateRegistry.get_latest_revision(
            TENANT,
            TEMPLATE_ID,
            revisions,
        )
        == _revision(3)
    )

    assert [
        item.revision
        for item in CrmEmailTemplateRegistry.list_revisions(
            TENANT,
            TEMPLATE_ID,
            revisions,
        )
    ] == [
        3,
        2,
        1,
    ]


def test_mongo_owned_id_is_not_domain_metadata() -> None:
    metadata, revisions = _collections()
    del revisions

    value = _template()
    row = value.to_dict()
    row["create_idempotency_key"] = "template-create-001"
    row["_id"] = "mongo-generated-id"

    metadata.docs.append(row)

    assert (
        CrmEmailTemplateRegistry.get_template(
            TENANT,
            TEMPLATE_ID,
            metadata,
        )
        == value
    )


def test_mongo_owned_id_is_not_revision_domain_truth() -> None:
    metadata, revisions = _collections()
    del metadata

    value = _revision(1)
    row = value.to_dict()
    row["_id"] = "mongo-generated-revision-id"

    revisions.docs.append(row)

    assert (
        CrmEmailTemplateRegistry.get_revision(
            TENANT,
            TEMPLATE_ID,
            1,
            revisions,
        )
        == value
    )


def test_unknown_metadata_field_other_than_mongo_id_still_fails_closed() -> None:
    metadata, revisions = _collections()
    del revisions

    row = _template().to_dict()
    row["create_idempotency_key"] = "template-create-001"
    row["unexpected_storage_field"] = "forbidden"

    metadata.docs.append(row)

    with pytest.raises(
        CrmEmailTemplateRegistryCorruptionError
    ):
        CrmEmailTemplateRegistry.get_template(
            TENANT,
            TEMPLATE_ID,
            metadata,
        )


def test_unknown_revision_field_other_than_mongo_id_still_fails_closed() -> None:
    metadata, revisions = _collections()
    del metadata

    row = _revision(1).to_dict()
    row["unexpected_storage_field"] = "forbidden"

    revisions.docs.append(row)

    with pytest.raises(
        CrmEmailTemplateRegistryCorruptionError
    ):
        CrmEmailTemplateRegistry.get_revision(
            TENANT,
            TEMPLATE_ID,
            1,
            revisions,
        )


def test_corrupt_metadata_document_fails_closed() -> None:
    metadata, revisions = _collections()
    del revisions

    row = _template().to_dict()
    row["create_idempotency_key"] = "template-create-001"
    row["scope"] = "INVALID"

    metadata.docs.append(row)

    with pytest.raises(
        CrmEmailTemplateRegistryCorruptionError
    ):
        CrmEmailTemplateRegistry.get_template(
            TENANT,
            TEMPLATE_ID,
            metadata,
        )


def test_corrupt_revision_document_fails_closed() -> None:
    metadata, revisions = _collections()
    del metadata

    row = _revision(1).to_dict()
    row["fingerprint"] = "b" * 128

    revisions.docs.append(row)

    with pytest.raises(
        CrmEmailTemplateRegistryCorruptionError
    ):
        CrmEmailTemplateRegistry.get_revision(
            TENANT,
            TEMPLATE_ID,
            1,
            revisions,
        )


def test_registry_contains_no_send_mailbox_or_financial_execution_methods() -> None:
    forbidden = {
        "send",
        "send_email",
        "deliver",
        "queue",
        "connect_mailbox",
        "set_credentials",
        "authorize_send",
        "execute",
        "charge",
        "settle",
        "pay",
    }

    assert forbidden.isdisjoint(
        set(dir(CrmEmailTemplateRegistry))
    )


# ============================================================
# Metadata current-state CAS persistence contract
# ============================================================


def test_metadata_cas_registry_surface_is_exact() -> None:
    import inspect

    method = getattr(
        CrmEmailTemplateRegistry,
        "revise_template_metadata",
    )

    parameters = inspect.signature(
        method
    ).parameters

    assert tuple(parameters) == (
        "tenant_id",
        "template_id",
        "expected_revision",
        "expected_fingerprint",
        "occurred_at",
        "metadata_collection",
        "session",
        "name",
        "scope",
        "lifecycle",
        "owner_principal_id",
        "team_id",
        "folder",
        "tags",
    )


def test_metadata_cas_requires_active_transaction_before_io() -> None:
    metadata, revisions = _collections()
    del revisions

    baseline = _template()

    metadata.docs.append(
        {
            **baseline.to_dict(),
            "create_idempotency_key":
                "template-create-001",
        }
    )

    before = list(
        metadata.docs
    )

    for invalid_session in (
        None,
        InactiveSession(),
    ):
        with pytest.raises(
            CrmEmailTemplateRegistryTransactionError
        ):
            _revise_template_metadata(
                TENANT,
                TEMPLATE_ID,
                baseline.metadata_revision,
                baseline.metadata_fingerprint,
                NOW,
                metadata,
                invalid_session,
                name="Changed",
            )

        assert metadata.docs == before


def test_metadata_cas_missing_template_is_not_found() -> None:
    metadata, revisions = _collections()
    del revisions

    baseline = _template()

    with pytest.raises(
        CrmEmailTemplateRegistryError
    ):
        _revise_template_metadata(
            TENANT,
            TEMPLATE_ID,
            baseline.metadata_revision,
            baseline.metadata_fingerprint,
            NOW + timedelta(minutes=1),
            metadata,
            ActiveSession(),
            name="Changed",
        )


def test_metadata_cas_exact_current_state_advances_once() -> None:
    metadata, revisions = _collections()
    del revisions

    baseline = _template()

    metadata.docs.append(
        {
            **baseline.to_dict(),
            "create_idempotency_key":
                "template-create-001",
        }
    )

    result = _revise_template_metadata(
        TENANT,
        TEMPLATE_ID,
        baseline.metadata_revision,
        baseline.metadata_fingerprint,
        NOW + timedelta(minutes=1),
        metadata,
        ActiveSession(),
        name="Construction Follow-up",
    )

    assert result.metadata_revision == 2
    assert (
        result.metadata_fingerprint
        != baseline.metadata_fingerprint
    )

    assert len(metadata.docs) == 1

    durable = metadata.docs[0]

    assert (
        durable["create_idempotency_key"]
        == "template-create-001"
    )

    assert durable["metadata_revision"] == 2
    assert (
        durable["metadata_fingerprint"]
        == result.metadata_fingerprint
    )


def test_metadata_cas_stale_revision_conflicts_without_write() -> None:
    metadata, revisions = _collections()
    del revisions

    baseline = _template()

    first = baseline.revise_metadata(
        expected_revision=1,
        expected_fingerprint=baseline.metadata_fingerprint,
        occurred_at=NOW + timedelta(minutes=1),
        name="First",
    )

    metadata.docs.append(
        {
            **first.to_dict(),
            "create_idempotency_key":
                "template-create-001",
        }
    )

    before = list(
        metadata.docs
    )

    with pytest.raises(
        CrmEmailTemplateRegistryConflictError
    ):
        _revise_template_metadata(
            TENANT,
            TEMPLATE_ID,
            1,
            baseline.metadata_fingerprint,
            NOW + timedelta(minutes=1),
            metadata,
            ActiveSession(),
            name="Stale",
        )

    assert metadata.docs == before


def test_metadata_cas_stale_fingerprint_conflicts_without_write() -> None:
    metadata, revisions = _collections()
    del revisions

    baseline = _template()

    metadata.docs.append(
        {
            **baseline.to_dict(),
            "create_idempotency_key":
                "template-create-001",
        }
    )

    before = list(
        metadata.docs
    )

    with pytest.raises(
        CrmEmailTemplateRegistryConflictError
    ):
        _revise_template_metadata(
            TENANT,
            TEMPLATE_ID,
            1,
            "b" * 128,
            NOW + timedelta(minutes=1),
            metadata,
            ActiveSession(),
            name="Wrong fingerprint",
        )

    assert metadata.docs == before


def test_metadata_cas_wrong_tenant_cannot_mutate() -> None:
    metadata, revisions = _collections()
    del revisions

    baseline = _template()

    metadata.docs.append(
        {
            **baseline.to_dict(),
            "create_idempotency_key":
                "template-create-001",
        }
    )

    before = list(
        metadata.docs
    )

    with pytest.raises(
        CrmEmailTemplateRegistryError
    ):
        _revise_template_metadata(
            "tenant-b",
            TEMPLATE_ID,
            1,
            baseline.metadata_fingerprint,
            NOW + timedelta(minutes=1),
            metadata,
            ActiveSession(),
            name="Cross tenant",
        )

    assert metadata.docs == before


def test_metadata_cas_domain_invalid_scope_binding_rejects_without_write() -> None:
    metadata, revisions = _collections()
    del revisions

    baseline = _template()

    metadata.docs.append(
        {
            **baseline.to_dict(),
            "create_idempotency_key":
                "template-create-001",
        }
    )

    before = list(
        metadata.docs
    )

    with pytest.raises(
        CrmEmailTemplateError
    ):
        _revise_template_metadata(
            TENANT,
            TEMPLATE_ID,
            1,
            baseline.metadata_fingerprint,
            NOW + timedelta(minutes=1),
            metadata,
            ActiveSession(),
            scope=CrmEmailTemplateScope.TEAM_SHARED,
            owner_principal_id=None,
            team_id=None,
        )

    assert metadata.docs == before


def test_metadata_cas_system_seed_rejected_without_write() -> None:
    metadata, revisions = _collections()
    del revisions

    seed = _template(
        scope=CrmEmailTemplateScope.SYSTEM_SEED,
        origin=CrmEmailTemplateOrigin.SYSTEM_SEED,
        owner_principal_id=None,
        team_id=None,
    )

    metadata.docs.append(
        {
            **seed.to_dict(),
            "create_idempotency_key":
                "template-create-seed",
        }
    )

    before = list(
        metadata.docs
    )

    with pytest.raises(
        CrmEmailTemplateError
    ):
        _revise_template_metadata(
            TENANT,
            TEMPLATE_ID,
            1,
            seed.metadata_fingerprint,
            NOW + timedelta(minutes=1),
            metadata,
            ActiveSession(),
            name="Override seed",
        )

    assert metadata.docs == before


def test_metadata_cas_archive_is_current_state_not_delete() -> None:
    metadata, revisions = _collections()

    baseline = _template()

    metadata.docs.append(
        {
            **baseline.to_dict(),
            "create_idempotency_key":
                "template-create-001",
        }
    )

    content = _revision(1)

    revisions.docs.append(
        content.to_dict()
    )

    result = _revise_template_metadata(
        TENANT,
        TEMPLATE_ID,
        1,
        baseline.metadata_fingerprint,
        NOW + timedelta(minutes=1),
        metadata,
        ActiveSession(),
        lifecycle=CrmEmailTemplateLifecycle.ARCHIVED,
    )

    assert (
        result.lifecycle
        is CrmEmailTemplateLifecycle.ARCHIVED
    )

    assert len(metadata.docs) == 1
    assert len(revisions.docs) == 1
    assert (
        revisions.docs[0]
        == content.to_dict()
    )


def test_metadata_cas_archived_template_cannot_mutate_again() -> None:
    metadata, revisions = _collections()
    del revisions

    baseline = _template()

    archived = baseline.revise_metadata(
        expected_revision=1,
        expected_fingerprint=baseline.metadata_fingerprint,
        occurred_at=NOW + timedelta(minutes=1),
        lifecycle=CrmEmailTemplateLifecycle.ARCHIVED,
    )

    metadata.docs.append(
        {
            **archived.to_dict(),
            "create_idempotency_key":
                "template-create-001",
        }
    )

    before = list(
        metadata.docs
    )

    with pytest.raises(
        CrmEmailTemplateError
    ):
        _revise_template_metadata(
            TENANT,
            TEMPLATE_ID,
            archived.metadata_revision,
            archived.metadata_fingerprint,
            NOW + timedelta(minutes=1),
            metadata,
            ActiveSession(),
            name="Forbidden post-archive edit",
        )

    assert metadata.docs == before


def test_metadata_cas_unknown_storage_corruption_fails_closed() -> None:
    metadata, revisions = _collections()
    del revisions

    baseline = _template()

    metadata.docs.append(
        {
            **baseline.to_dict(),
            "create_idempotency_key":
                "template-create-001",
            "unexpected_storage_field":
                "forbidden",
        }
    )

    with pytest.raises(
        CrmEmailTemplateRegistryCorruptionError
    ):
        _revise_template_metadata(
            TENANT,
            TEMPLATE_ID,
            1,
            baseline.metadata_fingerprint,
            NOW + timedelta(minutes=1),
            metadata,
            ActiveSession(),
            name="Should never write",
        )


def test_metadata_cas_does_not_expand_registry_authority() -> None:
    import inspect

    parameters = set(
        inspect.signature(
            getattr(
            CrmEmailTemplateRegistry,
            "revise_template_metadata",
        )
        ).parameters
    )

    forbidden = {
        "send",
        "send_email",
        "mailbox",
        "provider_credentials",
        "consent",
        "suppression",
        "sequence",
        "permission",
        "permissions",
        "authorization",
        "entitlement",
        "ai_execute",
        "financial_execution",
        "payment",
        "settlement",
    }

    assert forbidden.isdisjoint(
        parameters
    )


# ARTIFACT: test_crm_email_template_registry.py
# VERSION: v1.0.0-P0-CRM-EMAIL-TEMPLATE-REGISTRY-CERT
# PERSISTENCE: tenant-bound metadata creation + immutable revision append
# METADATA MUTATION: deferred pending explicit metadata CAS contract
# ARCHIVE MUTATION: deferred pending explicit metadata CAS contract
# DELETE/PURGE/TTL AUTHORITY: none
# MAILBOX/SEND AUTHORITY: none
# FINANCIAL EXECUTION AUTHORITY: none; Kennel EOS remains exclusive
# END OF WILSY OS SOVEREIGN ARTIFACT
