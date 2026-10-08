"""
TITLE: WILSY OS CRM Email Template Registry
VERSION: v1.1.0-CRM-EMAIL-TEMPLATE-REGISTRY

AUTHORITY:
    Tenant-bound persistence and exact replay for immutable CRM email-template
    identity and published content-revision history.

EPITOME:
    Persists template metadata once, appends immutable revisions in strict
    sequence, rejects divergent replay and corruption, and preserves caller-
    owned transaction and tenant-isolation boundaries.

ABSOLUTE CANONICAL PATH:
    /Users/wilsonkhanyezi/legal-doc-system/tools/eos/crm/persistence/crm_email_template_registry.py

RESEARCH BASIS:
    - Canonical WILSY CRM Lead registry identity/idempotency precedent.
    - WILSY caller-owned active Mongo transaction precedent.
    - WILSY HR immutable-history exact-replay precedent.
    - Apollo template ownership/link/copy semantics.
    - lemlist copy/workspace-isolation semantics.

COLLECTION MODEL:
    crm_email_templates
        Immutable v1 template metadata identity plus registry-owned creation
        idempotency evidence.

    crm_email_template_revisions
        Append-only immutable published template content history.

TENANT BOUNDARY:
    Every durable identity, replay predicate, revision lookup and write is
    tenant-bound. Cross-tenant inference is forbidden.

CREATE REPLAY:
    The tenant/create-idempotency coordinate is checked first.
    An identical durable domain payload is returned as exact replay.
    Divergent reuse fails closed.
    Reuse of the same tenant/template identity under another create key also
    fails closed.

REVISION REPLAY:
    The exact tenant/template/revision identity is checked first.
    Identical content is returned as replay.
    Divergent content fails closed.

REVISION SEQUENCE:
    The first revision is exactly 1.
    Every fresh later revision is exactly latest + 1.
    No gaps or rewinds are accepted.

CONCURRENCY:
    Deterministic pre-write classification provides clear local semantics.
    Mongo unique indexes remain the final concurrency arbiter.
    After DuplicateKeyError, the exact durable identity is re-read and only an
    identical durable replay is accepted.

TRANSACTION POSTURE:
    Every write requires a caller-provided active Mongo transaction before any
    read or write is performed. This registry never starts, commits or aborts
    a transaction. Public reads accept an optional caller-owned session
    and forward that exact session to the underlying MongoDB operation.

HYDRATION:
    The canonical CrmEmailTemplate / CrmEmailTemplateRevision from_dict()
    methods remain the strict domain corruption boundary.

METADATA MUTATION BOUNDARY:
    Explicit domain-derived metadata compare-and-swap is supported.
    Each mutation requires expected revision and fingerprint coordinates.
    No implicit mutation, delete or authority escalation is permitted.

RETENTION BOUNDARY:
    No delete, purge or TTL authority.

MAILBOX / SEND BOUNDARY:
    Persistence grants no mailbox credential access and no email-send authority.

CONSENT / AI BOUNDARY:
    No consent decision, suppression decision, AI-send authority or sequence
    execution authority exists here.

FINANCIAL AUTHORITY BOUNDARY:
    None. Kennel EOS remains exclusive financial execution authority.

CHANGELOG:
    2026-10-07 v1.0.0 establishes tenant-bound metadata create/replay and
    immutable monotonically revisioned template history.
    2026-10-07 v1.1.0 introduces optional caller-owned session forwarding
    across all five public metadata and revision read methods.
"""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any, Final, cast

from pymongo.errors import DuplicateKeyError, PyMongoError

from tools.eos.crm.domain.crm_email_template import (
    CrmEmailTemplate,
    CrmEmailTemplateError,
    CrmEmailTemplateRevision,
)


CRM_EMAIL_TEMPLATE_REGISTRY_VERSION: Final[str] = (
    "v1.1.0-CRM-EMAIL-TEMPLATE-REGISTRY"
)

CRM_EMAIL_TEMPLATE_METADATA_COLLECTION: Final[str] = (
    "crm_email_templates"
)

CRM_EMAIL_TEMPLATE_REVISION_COLLECTION: Final[str] = (
    "crm_email_template_revisions"
)


_METADATA_REGISTRY_FIELDS: Final[frozenset[str]] = frozenset({
    "create_idempotency_key",
})

_MONGO_OWNED_FIELDS: Final[frozenset[str]] = frozenset({
    "_id",
})

_FORBIDDEN_TENANTS: Final[frozenset[str]] = frozenset({
    "default",
    "global",
    "root",
    "*",
    "master",
    "global_root",
    "sovereign_root",
    "wilsy-sovereign-root",
})


class CrmEmailTemplateRegistryError(RuntimeError):
    """Base registry failure."""


class CrmEmailTemplateRegistryConflictError(
    CrmEmailTemplateRegistryError
):
    """Durable identity, replay or monotonicity conflict."""


class CrmEmailTemplateRegistryCorruptionError(
    CrmEmailTemplateRegistryError
):
    """Persisted document failed canonical domain hydration."""


class CrmEmailTemplateRegistryTransactionError(
    CrmEmailTemplateRegistryError
):
    """Caller did not supply an active transaction for a write."""


def _tenant(value: object) -> str:
    """Require one exact non-pseudo tenant identifier."""

    if (
        not isinstance(value, str)
        or not value
        or value != value.strip()
        or value.casefold() in _FORBIDDEN_TENANTS
    ):
        raise CrmEmailTemplateRegistryError(
            "CRM_EMAIL_TEMPLATE_REGISTRY_TENANT_INVALID"
        )

    return value


def _identifier(
    name: str,
    value: object,
) -> str:
    """Require one exact nonblank identifier."""

    if (
        not isinstance(value, str)
        or not value
        or value != value.strip()
    ):
        raise CrmEmailTemplateRegistryError(
            f"CRM_EMAIL_TEMPLATE_REGISTRY_{name.upper()}_INVALID"
        )

    return value


def _revision_number(value: object) -> int:
    """Require one positive revision identity."""

    if (
        isinstance(value, bool)
        or not isinstance(value, int)
        or value < 1
    ):
        raise CrmEmailTemplateRegistryError(
            "CRM_EMAIL_TEMPLATE_REGISTRY_REVISION_INVALID"
        )

    return value


def _active_transaction(session: object) -> object:
    """Require a caller-provided active Mongo transaction before any I/O."""

    if session is None:
        raise CrmEmailTemplateRegistryTransactionError(
            "CRM_EMAIL_TEMPLATE_REGISTRY_TRANSACTION_REQUIRED"
        )

    if getattr(session, "in_transaction", False) is not True:
        raise CrmEmailTemplateRegistryTransactionError(
            "CRM_EMAIL_TEMPLATE_REGISTRY_TRANSACTION_REQUIRED"
        )

    return session


def _collection(value: object, name: str) -> Any:
    """Require a minimal PyMongo-like collection surface."""

    if value is None:
        raise CrmEmailTemplateRegistryError(
            f"CRM_EMAIL_TEMPLATE_REGISTRY_{name.upper()}_COLLECTION_REQUIRED"
        )

    return value


def _metadata_payload(
    template: CrmEmailTemplate,
    *,
    idempotency_key: str,
) -> dict[str, object]:
    """Build the exact durable metadata document."""

    payload = template.to_dict()
    payload["create_idempotency_key"] = idempotency_key

    return payload


def _hydrate_metadata(
    raw: Mapping[str, object],
) -> CrmEmailTemplate:
    """Hydrate metadata after removing registry-owned replay evidence."""

    try:
        domain_payload = {
            key: value
            for key, value in raw.items()
            if (
                key not in _METADATA_REGISTRY_FIELDS
                and key not in _MONGO_OWNED_FIELDS
            )
        }

        return CrmEmailTemplate.from_dict(
            domain_payload
        )

    except (
        CrmEmailTemplateError,
        KeyError,
        TypeError,
        ValueError,
    ) as error:
        raise CrmEmailTemplateRegistryCorruptionError(
            "CRM_EMAIL_TEMPLATE_REGISTRY_METADATA_CORRUPT"
        ) from error


def _hydrate_revision(
    raw: Mapping[str, object],
) -> CrmEmailTemplateRevision:
    """Hydrate one strict immutable revision."""

    try:
        domain_payload = {
            key: value
            for key, value in raw.items()
            if key not in _MONGO_OWNED_FIELDS
        }

        return CrmEmailTemplateRevision.from_dict(
            domain_payload
        )

    except (
        CrmEmailTemplateError,
        KeyError,
        TypeError,
        ValueError,
    ) as error:
        raise CrmEmailTemplateRegistryCorruptionError(
            "CRM_EMAIL_TEMPLATE_REGISTRY_REVISION_CORRUPT"
        ) from error


def _rows(
    collection: Any,
    query: Mapping[str, object],
    *,
    session: object | None = None,
) -> list[dict[str, object]]:
    """Read rows through a PyMongo-compatible cursor."""

    kwargs: dict[str, object] = {}

    if session is not None:
        kwargs["session"] = session

    try:
        cursor = collection.find(
            query,
            **kwargs,
        )

        return [
            cast(
                dict[str, object],
                row,
            )
            for row in cursor
        ]

    except PyMongoError as error:
        raise CrmEmailTemplateRegistryError(
            "CRM_EMAIL_TEMPLATE_REGISTRY_READ_FAILED"
        ) from error


def _find_one(
    collection: Any,
    query: Mapping[str, object],
    *,
    session: object | None = None,
) -> dict[str, object] | None:
    """Read one exact durable row."""

    kwargs: dict[str, object] = {}

    if session is not None:
        kwargs["session"] = session

    try:
        row = collection.find_one(
            query,
            **kwargs,
        )

    except PyMongoError as error:
        raise CrmEmailTemplateRegistryError(
            "CRM_EMAIL_TEMPLATE_REGISTRY_READ_FAILED"
        ) from error

    if row is None:
        return None

    if not isinstance(row, Mapping):
        raise CrmEmailTemplateRegistryCorruptionError(
            "CRM_EMAIL_TEMPLATE_REGISTRY_DOCUMENT_NOT_MAPPING"
        )

    return dict(row)


def _metadata_equal(
    raw: Mapping[str, object],
    value: CrmEmailTemplate,
    *,
    idempotency_key: str,
) -> bool:
    """Compare durable metadata and registry replay coordinate exactly."""

    hydrated = _hydrate_metadata(
        raw
    )

    return (
        hydrated == value
        and raw.get("create_idempotency_key")
        == idempotency_key
    )


def _revision_equal(
    raw: Mapping[str, object],
    value: CrmEmailTemplateRevision,
) -> bool:
    """Compare strict immutable revision truth."""

    return (
        _hydrate_revision(raw)
        == value
    )


def _latest_revision_from_rows(
    rows: list[dict[str, object]],
) -> CrmEmailTemplateRevision | None:
    """Return the highest strict revision or None."""

    if not rows:
        return None

    hydrated = [
        _hydrate_revision(row)
        for row in rows
    ]

    hydrated.sort(
        key=lambda item: item.revision,
        reverse=True,
    )

    return hydrated[0]



_METADATA_MUTATION_UNSET: Final[object] = object()


class CrmEmailTemplateRegistry:
    """Tenant-bound CRM email-template durable registry."""

    @staticmethod
    def ensure_indexes(
        metadata_collection: Any,
        revision_collection: Any,
    ) -> None:
        """Install exact tenant-bound identity/read indexes.

        No TTL index is created.
        """

        metadata = _collection(
            metadata_collection,
            "metadata",
        )

        revisions = _collection(
            revision_collection,
            "revision",
        )

        try:
            metadata.create_index(
                [
                    ("tenant_id", 1),
                    ("template_id", 1),
                ],
                unique=True,
                name=(
                    "crm_email_template_"
                    "tenant_identity_unique"
                ),
            )

            metadata.create_index(
                [
                    ("tenant_id", 1),
                    ("create_idempotency_key", 1),
                ],
                unique=True,
                name=(
                    "crm_email_template_"
                    "tenant_create_idempotency_unique"
                ),
            )

            metadata.create_index(
                [
                    ("tenant_id", 1),
                    ("scope", 1),
                    ("lifecycle", 1),
                ],
                name=(
                    "crm_email_template_"
                    "tenant_scope_lifecycle"
                ),
            )

            metadata.create_index(
                [
                    ("tenant_id", 1),
                    ("origin", 1),
                    ("lifecycle", 1),
                ],
                name=(
                    "crm_email_template_"
                    "tenant_origin_lifecycle"
                ),
            )

            metadata.create_index(
                [
                    ("tenant_id", 1),
                    ("owner_principal_id", 1),
                    ("lifecycle", 1),
                ],
                name=(
                    "crm_email_template_"
                    "tenant_owner_lifecycle"
                ),
            )

            metadata.create_index(
                [
                    ("tenant_id", 1),
                    ("team_id", 1),
                    ("lifecycle", 1),
                ],
                name=(
                    "crm_email_template_"
                    "tenant_team_lifecycle"
                ),
            )

            metadata.create_index(
                [
                    ("tenant_id", 1),
                    ("folder", 1),
                    ("lifecycle", 1),
                ],
                name=(
                    "crm_email_template_"
                    "tenant_folder_lifecycle"
                ),
            )

            revisions.create_index(
                [
                    ("tenant_id", 1),
                    ("template_id", 1),
                    ("revision", 1),
                ],
                unique=True,
                name=(
                    "crm_email_template_"
                    "revision_identity_unique"
                ),
            )

            revisions.create_index(
                [
                    ("tenant_id", 1),
                    ("template_id", 1),
                    ("fingerprint", 1),
                ],
                unique=True,
                name=(
                    "crm_email_template_"
                    "revision_fingerprint_unique"
                ),
            )

            revisions.create_index(
                [
                    ("tenant_id", 1),
                    ("template_id", 1),
                    ("revision", -1),
                ],
                name=(
                    "crm_email_template_"
                    "revision_read"
                ),
            )

        except PyMongoError as error:
            raise CrmEmailTemplateRegistryError(
                "CRM_EMAIL_TEMPLATE_REGISTRY_INDEX_FAILED"
            ) from error

    @staticmethod
    def create_template(
        template: CrmEmailTemplate,
        *,
        idempotency_key: str,
        metadata_collection: Any,
        session: Any,
    ) -> CrmEmailTemplate:
        """Persist once or exactly replay one immutable template identity."""

        if not isinstance(
            template,
            CrmEmailTemplate,
        ):
            raise CrmEmailTemplateRegistryError(
                "CRM_EMAIL_TEMPLATE_REGISTRY_TEMPLATE_REQUIRED"
            )

        key = _identifier(
            "idempotency_key",
            idempotency_key,
        )

        tx = _active_transaction(
            session
        )

        collection = _collection(
            metadata_collection,
            "metadata",
        )

        replay_query = {
            "tenant_id":
                template.tenant_id,
            "create_idempotency_key":
                key,
        }

        replay = _find_one(
            collection,
            replay_query,
            session=tx,
        )

        if replay is not None:
            if _metadata_equal(
                replay,
                template,
                idempotency_key=key,
            ):
                return _hydrate_metadata(
                    replay
                )

            raise CrmEmailTemplateRegistryConflictError(
                "CRM_EMAIL_TEMPLATE_CREATE_REPLAY_CONFLICT"
            )

        identity_query = {
            "tenant_id":
                template.tenant_id,
            "template_id":
                template.template_id,
        }

        identity = _find_one(
            collection,
            identity_query,
            session=tx,
        )

        if identity is not None:
            _hydrate_metadata(
                identity
            )

            raise CrmEmailTemplateRegistryConflictError(
                "CRM_EMAIL_TEMPLATE_IDENTITY_CONFLICT"
            )

        document = _metadata_payload(
            template,
            idempotency_key=key,
        )

        try:
            collection.insert_one(
                document,
                session=tx,
            )

        except DuplicateKeyError as error:
            raced_replay = _find_one(
                collection,
                replay_query,
                session=tx,
            )

            if (
                raced_replay is not None
                and _metadata_equal(
                    raced_replay,
                    template,
                    idempotency_key=key,
                )
            ):
                return _hydrate_metadata(
                    raced_replay
                )

            raced_identity = _find_one(
                collection,
                identity_query,
                session=tx,
            )

            if raced_identity is not None:
                _hydrate_metadata(
                    raced_identity
                )

            raise CrmEmailTemplateRegistryConflictError(
                "CRM_EMAIL_TEMPLATE_CREATE_RACE_CONFLICT"
            ) from error

        except PyMongoError as error:
            raise CrmEmailTemplateRegistryError(
                "CRM_EMAIL_TEMPLATE_CREATE_FAILED"
            ) from error

        persisted = _find_one(
            collection,
            identity_query,
            session=tx,
        )

        if persisted is None:
            raise CrmEmailTemplateRegistryCorruptionError(
                "CRM_EMAIL_TEMPLATE_CREATE_NOT_DURABLE"
            )

        if not _metadata_equal(
            persisted,
            template,
            idempotency_key=key,
        ):
            raise CrmEmailTemplateRegistryCorruptionError(
                "CRM_EMAIL_TEMPLATE_CREATE_DURABLE_MISMATCH"
            )

        return _hydrate_metadata(
            persisted
        )

    @staticmethod
    def revise_template_metadata(
        tenant_id: str,
        template_id: str,
        expected_revision: int,
        expected_fingerprint: str,
        occurred_at: Any,
        metadata_collection: Any,
        session: Any,
        name: Any = _METADATA_MUTATION_UNSET,
        scope: Any = _METADATA_MUTATION_UNSET,
        lifecycle: Any = _METADATA_MUTATION_UNSET,
        owner_principal_id: Any = _METADATA_MUTATION_UNSET,
        team_id: Any = _METADATA_MUTATION_UNSET,
        folder: Any = _METADATA_MUTATION_UNSET,
        tags: Any = _METADATA_MUTATION_UNSET,
    ) -> CrmEmailTemplate:
        """Advance template metadata by one atomic compare-and-swap.

        The caller supplies only the expected current CAS coordinates and
        proposed metadata changes. The durable successor is derived solely
        from the currently persisted domain value through revise_metadata().
        This method grants no read, sharing, send, mailbox, consent,
        sequence, AI, billing, payment or financial-execution authority.
        """

        tx = _active_transaction(
            session
        )

        tenant = _tenant(
            tenant_id
        )

        template = _identifier(
            "template_id",
            template_id,
        )

        collection = _collection(
            metadata_collection,
            "metadata",
        )

        row = _find_one(
            collection,
            {
                "tenant_id":
                    tenant,
                "template_id":
                    template,
            },
            session=tx,
        )

        if row is None:
            raise CrmEmailTemplateRegistryError(
                "CRM_EMAIL_TEMPLATE_REGISTRY_TEMPLATE_NOT_FOUND"
            )

        current = _hydrate_metadata(
            row
        )

        create_idempotency_key = row.get(
            "create_idempotency_key"
        )

        if (
            not isinstance(
                create_idempotency_key,
                str,
            )
            or not create_idempotency_key
            or create_idempotency_key
            != create_idempotency_key.strip()
        ):
            raise CrmEmailTemplateRegistryCorruptionError(
                "CRM_EMAIL_TEMPLATE_REGISTRY_METADATA_CORRUPT"
            )

        if (
            current.metadata_revision
            != expected_revision
            or current.metadata_fingerprint
            != expected_fingerprint
        ):
            raise CrmEmailTemplateRegistryConflictError(
                "CRM_EMAIL_TEMPLATE_REGISTRY_METADATA_CAS_CONFLICT"
            )

        changes: dict[str, Any] = {}

        for key, value in (
            ("name", name),
            ("scope", scope),
            ("lifecycle", lifecycle),
            (
                "owner_principal_id",
                owner_principal_id,
            ),
            ("team_id", team_id),
            ("folder", folder),
            ("tags", tags),
        ):
            if value is not _METADATA_MUTATION_UNSET:
                changes[key] = value

        successor = current.revise_metadata(
            expected_revision=expected_revision,
            expected_fingerprint=expected_fingerprint,
            occurred_at=occurred_at,
            **changes,
        )

        replacement = successor.to_dict()

        replacement[
            "create_idempotency_key"
        ] = create_idempotency_key

        try:
            result = collection.replace_one(
                {
                    "tenant_id":
                        tenant,
                    "template_id":
                        template,
                    "metadata_revision":
                        expected_revision,
                    "metadata_fingerprint":
                        expected_fingerprint,
                },
                replacement,
                upsert=False,
                session=tx,
            )
        except PyMongoError as error:
            code = getattr(
                error,
                "code",
                None,
            )

            has_error_label = getattr(
                error,
                "has_error_label",
                None,
            )

            transient_conflict = (
                code == 112
                or (
                    callable(
                        has_error_label
                    )
                    and has_error_label(
                        "TransientTransactionError"
                    )
                )
            )

            if transient_conflict:
                raise CrmEmailTemplateRegistryConflictError(
                    "CRM_EMAIL_TEMPLATE_REGISTRY_METADATA_CAS_CONFLICT"
                ) from error

            raise CrmEmailTemplateRegistryError(
                "CRM_EMAIL_TEMPLATE_REGISTRY_METADATA_UPDATE_FAILED"
            ) from error

        if getattr(
            result,
            "matched_count",
            0,
        ) != 1:
            raise CrmEmailTemplateRegistryConflictError(
                "CRM_EMAIL_TEMPLATE_REGISTRY_METADATA_CAS_CONFLICT"
            )

        return successor


    @staticmethod
    def get_template(
        tenant_id: str,
        template_id: str,
        metadata_collection: Any,
        *,
        session: Any = None,
    ) -> CrmEmailTemplate | None:
        """Return one exact tenant-bound template metadata value."""

        tenant = _tenant(
            tenant_id
        )

        template = _identifier(
            "template_id",
            template_id,
        )

        collection = _collection(
            metadata_collection,
            "metadata",
        )

        row = _find_one(
            collection,
            {
                "tenant_id": tenant,
                "template_id": template,
            },
            session=session,
        )

        if row is None:
            return None

        return _hydrate_metadata(
            row
        )

    @staticmethod
    def list_templates(
        tenant_id: str,
        metadata_collection: Any,
        *,
        session: Any = None,
    ) -> tuple[CrmEmailTemplate, ...]:
        """List template metadata without crossing the requested tenant."""

        tenant = _tenant(
            tenant_id
        )

        collection = _collection(
            metadata_collection,
            "metadata",
        )

        values = [
            _hydrate_metadata(row)
            for row in _rows(
                collection,
                {
                    "tenant_id": tenant,
                },
                session=session,
            )
        ]

        values.sort(
            key=lambda item: item.template_id
        )

        return tuple(values)

    @staticmethod
    def append_revision(
        revision: CrmEmailTemplateRevision,
        *,
        metadata_collection: Any,
        revision_collection: Any,
        session: Any,
    ) -> CrmEmailTemplateRevision:
        """Append one exact next revision or return its exact replay."""

        if not isinstance(
            revision,
            CrmEmailTemplateRevision,
        ):
            raise CrmEmailTemplateRegistryError(
                "CRM_EMAIL_TEMPLATE_REGISTRY_REVISION_REQUIRED"
            )

        tx = _active_transaction(
            session
        )

        metadata = _collection(
            metadata_collection,
            "metadata",
        )

        revisions = _collection(
            revision_collection,
            "revision",
        )

        template_row = _find_one(
            metadata,
            {
                "tenant_id":
                    revision.tenant_id,
                "template_id":
                    revision.template_id,
            },
            session=tx,
        )

        if template_row is None:
            raise CrmEmailTemplateRegistryConflictError(
                "CRM_EMAIL_TEMPLATE_REVISION_TEMPLATE_MISSING"
            )

        template = _hydrate_metadata(
            template_row
        )

        if (
            template.tenant_id
            != revision.tenant_id
            or template.template_id
            != revision.template_id
        ):
            raise CrmEmailTemplateRegistryCorruptionError(
                "CRM_EMAIL_TEMPLATE_REVISION_TEMPLATE_IDENTITY_MISMATCH"
            )

        exact_query = {
            "tenant_id":
                revision.tenant_id,
            "template_id":
                revision.template_id,
            "revision":
                revision.revision,
        }

        exact = _find_one(
            revisions,
            exact_query,
            session=tx,
        )

        if exact is not None:
            if _revision_equal(
                exact,
                revision,
            ):
                return _hydrate_revision(
                    exact
                )

            raise CrmEmailTemplateRegistryConflictError(
                "CRM_EMAIL_TEMPLATE_REVISION_REPLAY_CONFLICT"
            )

        history = _rows(
            revisions,
            {
                "tenant_id":
                    revision.tenant_id,
                "template_id":
                    revision.template_id,
            },
            session=tx,
        )

        latest = _latest_revision_from_rows(
            history
        )

        expected_revision = (
            1
            if latest is None
            else latest.revision + 1
        )

        if revision.revision != expected_revision:
            raise CrmEmailTemplateRegistryConflictError(
                "CRM_EMAIL_TEMPLATE_REVISION_SEQUENCE_CONFLICT"
            )

        document = revision.to_dict()

        try:
            revisions.insert_one(
                document,
                session=tx,
            )

        except DuplicateKeyError as error:
            raced = _find_one(
                revisions,
                exact_query,
                session=tx,
            )

            if (
                raced is not None
                and _revision_equal(
                    raced,
                    revision,
                )
            ):
                return _hydrate_revision(
                    raced
                )

            raise CrmEmailTemplateRegistryConflictError(
                "CRM_EMAIL_TEMPLATE_REVISION_RACE_CONFLICT"
            ) from error

        except PyMongoError as error:
            raise CrmEmailTemplateRegistryError(
                "CRM_EMAIL_TEMPLATE_REVISION_CREATE_FAILED"
            ) from error

        persisted = _find_one(
            revisions,
            exact_query,
            session=tx,
        )

        if persisted is None:
            raise CrmEmailTemplateRegistryCorruptionError(
                "CRM_EMAIL_TEMPLATE_REVISION_NOT_DURABLE"
            )

        if not _revision_equal(
            persisted,
            revision,
        ):
            raise CrmEmailTemplateRegistryCorruptionError(
                "CRM_EMAIL_TEMPLATE_REVISION_DURABLE_MISMATCH"
            )

        return _hydrate_revision(
            persisted
        )

    @staticmethod
    def get_revision(
        tenant_id: str,
        template_id: str,
        revision: int,
        revision_collection: Any,
        *,
        session: Any = None,
    ) -> CrmEmailTemplateRevision | None:
        """Return one exact tenant/template/revision fact."""

        tenant = _tenant(
            tenant_id
        )

        template = _identifier(
            "template_id",
            template_id,
        )

        number = _revision_number(
            revision
        )

        collection = _collection(
            revision_collection,
            "revision",
        )

        row = _find_one(
            collection,
            {
                "tenant_id": tenant,
                "template_id": template,
                "revision": number,
            },
            session=session,
        )

        if row is None:
            return None

        return _hydrate_revision(
            row
        )

    @staticmethod
    def get_latest_revision(
        tenant_id: str,
        template_id: str,
        revision_collection: Any,
        *,
        session: Any = None,
    ) -> CrmEmailTemplateRevision | None:
        """Return the highest strict revision for one tenant/template."""

        tenant = _tenant(
            tenant_id
        )

        template = _identifier(
            "template_id",
            template_id,
        )

        collection = _collection(
            revision_collection,
            "revision",
        )

        return _latest_revision_from_rows(
            _rows(
                collection,
                {
                    "tenant_id": tenant,
                    "template_id": template,
                },
                session=session,
            )
        )

    @staticmethod
    def list_revisions(
        tenant_id: str,
        template_id: str,
        revision_collection: Any,
        *,
        session: Any = None,
    ) -> tuple[CrmEmailTemplateRevision, ...]:
        """List strict immutable revisions newest first."""

        tenant = _tenant(
            tenant_id
        )

        template = _identifier(
            "template_id",
            template_id,
        )

        collection = _collection(
            revision_collection,
            "revision",
        )

        values = [
            _hydrate_revision(row)
            for row in _rows(
                collection,
                {
                    "tenant_id": tenant,
                    "template_id": template,
                },
                session=session,
            )
        ]

        values.sort(
            key=lambda item: item.revision,
            reverse=True,
        )

        return tuple(values)


__all__ = [
    "CRM_EMAIL_TEMPLATE_METADATA_COLLECTION",
    "CRM_EMAIL_TEMPLATE_REGISTRY_VERSION",
    "CRM_EMAIL_TEMPLATE_REVISION_COLLECTION",
    "CrmEmailTemplateRegistry",
    "CrmEmailTemplateRegistryConflictError",
    "CrmEmailTemplateRegistryCorruptionError",
    "CrmEmailTemplateRegistryError",
    "CrmEmailTemplateRegistryTransactionError",
]

# ARTIFACT: crm_email_template_registry.py
# VERSION: v1.1.0-CRM-EMAIL-TEMPLATE-REGISTRY
# PERSISTENCE: tenant-bound immutable metadata create + revision append
# REPLAY: exact tenant-local replay with post-race durable verification
# CONCURRENCY: Mongo unique indexes remain final race arbiter
# TRANSACTION: active caller-owned transaction required for every write
# READ SESSION: optional exact caller-session forwarding on all public reads
# METADATA UPDATE / ARCHIVE: explicit domain-derived metadata CAS
# DELETE / PURGE / TTL AUTHORITY: none
# MAILBOX / SEND AUTHORITY: none
# CONSENT / AI SEND AUTHORITY: none
# FINANCIAL EXECUTION AUTHORITY: none; Kennel EOS remains exclusive
# END OF WILSY OS SOVEREIGN ARTIFACT
