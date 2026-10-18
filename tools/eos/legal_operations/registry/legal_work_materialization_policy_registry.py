"""
WILSY OS — Legal Work-Materialization Policy Registry

TITLE: Legal Work-Materialization Policy Registry
VERSION: v1.0.0-P14-P9-WORK-MATERIALIZATION-POLICY-REGISTRY
AUTHORITY: Wilsy OS Core Governance / Python EOS Legal Operations

EPITOME:
    Immutable tenant-first durability for versioned
    LegalWorkMaterializationPolicy truth.

    The registry stores exact policy revisions, validates predecessor lineage,
    supports deterministic exact replay, strictly hydrates persisted truth and
    derives latest state from immutable history. It stores no mutable current
    pointer.

COMPETITIVE POSTURE:
    Persists stage-triggered multi-work policy, dependency-template policy and
    relative operational due-rule history while preserving deterministic
    historical replay and authority separation.

TENANT BOUNDARY:
    Every identity and query begins with exact tenant scope.

TRANSACTION BOUNDARY:
    Caller owns the active Mongo transaction and whole-transaction retry.

AUTHORITY BOUNDARY:
    Persistence and read projection only. This registry does not create work
    items, assign principals, supervise principals, grant IAM or professional
    authority, calculate legal deadlines, deliver notifications, invoke AI, or
    execute financial transactions.

DURABILITY:
    Immutable insert-only revision history. No TTL, update, replace, delete,
    upsert or mutable current pointer.

FINANCIAL AUTHORITY BOUNDARY:
    None. Kennel EOS remains exclusive for financial execution.

FAIL-CLOSED DECLARATION:
    Inactive transaction, divergent replay, revision gap, predecessor drift,
    malformed persisted truth or cross-tenant lookup rejects.
"""

from __future__ import annotations

from typing import Any, Final, Mapping, NoReturn

from pymongo.errors import DuplicateKeyError

from tools.eos.legal_operations.domain.legal_work_materialization_policy import (
    LegalWorkMaterializationPolicy,
    LegalWorkMaterializationPolicyError,
)


VERSION: Final[str] = (
    "v1.0.0-P14-P9-WORK-MATERIALIZATION-POLICY-REGISTRY"
)

COLLECTION_NAME: Final[str] = (
    "legal_work_materialization_policies"
)


class LegalWorkMaterializationPolicyRegistryError(RuntimeError):
    """Base durable materialization-policy registry error."""


class LegalWorkMaterializationPolicyRegistryInputError(
    LegalWorkMaterializationPolicyRegistryError
):
    """Caller supplied invalid registry input."""


class LegalWorkMaterializationPolicyRegistryTransactionRequiredError(
    LegalWorkMaterializationPolicyRegistryError
):
    """Caller did not supply an active transaction."""


class LegalWorkMaterializationPolicyRegistryConflictError(
    LegalWorkMaterializationPolicyRegistryError
):
    """Immutable replay or revision-lineage conflict."""


class LegalWorkMaterializationPolicyRegistryNotFoundError(
    LegalWorkMaterializationPolicyRegistryError
):
    """Exact requested durable policy revision was not found."""


class LegalWorkMaterializationPolicyRegistryPersistedRecordInvalidError(
    LegalWorkMaterializationPolicyRegistryError
):
    """Persisted row failed strict domain hydration."""


class LegalWorkMaterializationPolicyRegistryRetryTransactionError(
    LegalWorkMaterializationPolicyRegistryError
):
    """Caller must retry the complete transaction."""


class LegalWorkMaterializationPolicyRegistryPersistenceError(
    LegalWorkMaterializationPolicyRegistryError
):
    """Unexpected persistence-layer failure."""


def _raise(
    error_type: type[LegalWorkMaterializationPolicyRegistryError],
    code: str,
    cause: BaseException | None = None,
) -> NoReturn:
    error = error_type(code)

    if cause is None:
        raise error

    raise error from cause


def _transaction(
    session: object,
) -> object:
    active = getattr(
        session,
        "in_transaction",
        False,
    )

    if active is not True:
        _raise(
            LegalWorkMaterializationPolicyRegistryTransactionRequiredError,
            "P14_P9_ACTIVE_TRANSACTION_REQUIRED",
        )

    return session


def _text(
    name: str,
    value: object,
) -> str:
    if (
        not isinstance(value, str)
        or not value
        or value != value.strip()
    ):
        _raise(
            LegalWorkMaterializationPolicyRegistryInputError,
            f"P14_P9_{name.upper()}_INVALID",
        )

    return value


def _revision(
    value: object,
) -> int:
    if (
        isinstance(value, bool)
        or not isinstance(value, int)
        or value <= 0
    ):
        _raise(
            LegalWorkMaterializationPolicyRegistryInputError,
            "P14_P9_POLICY_REVISION_INVALID",
        )

    return value


class LegalWorkMaterializationPolicyRegistry:
    """
    Persist immutable work-materialization policy revisions.

    Latest truth is derived from ordered history. No current pointer exists.
    """

    def __init__(
        self,
        collection: Any,
    ) -> None:
        self._collection = collection

    def ensure_indexes(
        self,
    ) -> None:
        """Create tenant-first non-TTL access and uniqueness indexes."""
        self._collection.create_index(
            [
                ("tenant_id", 1),
                ("policy_id", 1),
                ("policy_revision", 1),
            ],
            unique=True,
            name=(
                "legal_work_materialization_policy_"
                "identity_unique"
            ),
        )

        self._collection.create_index(
            [
                ("tenant_id", 1),
                ("fingerprint", 1),
            ],
            unique=True,
            name=(
                "legal_work_materialization_policy_"
                "fingerprint_unique"
            ),
        )

        self._collection.create_index(
            [
                ("tenant_id", 1),
                ("workflow_definition_id", 1),
                ("target_stage_definition_id", 1),
            ],
            name=(
                "legal_work_materialization_policy_"
                "workflow_stage"
            ),
        )

    @staticmethod
    def _hydrate(
        raw: Mapping[str, object],
    ) -> LegalWorkMaterializationPolicy:
        document = dict(raw)
        document.pop("_id", None)

        try:
            return LegalWorkMaterializationPolicy.from_dict(
                document
            )
        except (
            LegalWorkMaterializationPolicyError,
            TypeError,
            ValueError,
        ) as error:
            _raise(
                LegalWorkMaterializationPolicyRegistryPersistedRecordInvalidError,
                "P14_P9_PERSISTED_RECORD_INVALID",
                error,
            )

    @staticmethod
    def _equal(
        left: LegalWorkMaterializationPolicy,
        right: LegalWorkMaterializationPolicy,
    ) -> bool:
        return (
            left.fingerprint == right.fingerprint
            and left == right
        )

    def create_or_replay(
        self,
        value: LegalWorkMaterializationPolicy,
        *,
        session: object,
    ) -> LegalWorkMaterializationPolicy:
        """
        Insert one immutable revision or return an exact replay.

        Revision N>1 must directly supersede revision N-1 by fingerprint.
        """
        tx = _transaction(
            session
        )

        if type(value) is not LegalWorkMaterializationPolicy:
            _raise(
                LegalWorkMaterializationPolicyRegistryInputError,
                "P14_P9_POLICY_REQUIRED",
            )

        identity_query = {
            "tenant_id":
                value.tenant_id,
            "policy_id":
                value.policy_id,
            "policy_revision":
                value.policy_revision,
        }

        existing_raw = self._collection.find_one(
            identity_query,
            session=tx,
        )

        if existing_raw is not None:
            existing = self._hydrate(
                existing_raw
            )

            if self._equal(
                existing,
                value,
            ):
                return existing

            _raise(
                LegalWorkMaterializationPolicyRegistryConflictError,
                "P14_P9_DIVERGENT_REPLAY",
            )

        if value.policy_revision == 1:
            if value.supersedes_fingerprint is not None:
                _raise(
                    LegalWorkMaterializationPolicyRegistryConflictError,
                    "P14_P9_FIRST_REVISION_SUPERSEDES_FORBIDDEN",
                )
        else:
            previous_raw = self._collection.find_one(
                {
                    "tenant_id":
                        value.tenant_id,
                    "policy_id":
                        value.policy_id,
                    "policy_revision":
                        value.policy_revision - 1,
                },
                session=tx,
            )

            if previous_raw is None:
                _raise(
                    LegalWorkMaterializationPolicyRegistryConflictError,
                    "P14_P9_REVISION_GAP",
                )

            previous = self._hydrate(
                previous_raw
            )

            if value.supersedes_fingerprint is None:
                _raise(
                    LegalWorkMaterializationPolicyRegistryConflictError,
                    "P14_P9_SUPERSEDES_REQUIRED",
                )

            if (
                value.supersedes_fingerprint
                != previous.fingerprint
            ):
                _raise(
                    LegalWorkMaterializationPolicyRegistryConflictError,
                    "P14_P9_SUPERSEDES_FINGERPRINT_MISMATCH",
                )

        try:
            self._collection.insert_one(
                value.to_dict(),
                session=tx,
            )
        except DuplicateKeyError as error:
            raced_raw = self._collection.find_one(
                identity_query,
                session=tx,
            )

            if raced_raw is not None:
                raced = self._hydrate(
                    raced_raw
                )

                if self._equal(
                    raced,
                    value,
                ):
                    return raced

            _raise(
                LegalWorkMaterializationPolicyRegistryRetryTransactionError,
                "P14_P9_DUPLICATE_RACE_RETRY_TRANSACTION",
                error,
            )
        except Exception as error:
            _raise(
                LegalWorkMaterializationPolicyRegistryPersistenceError,
                "P14_P9_PERSISTENCE_ERROR",
                error,
            )

        return self.get_revision(
            value.tenant_id,
            value.policy_id,
            value.policy_revision,
            session=tx,
        )

    def get_revision(
        self,
        tenant_id: str,
        policy_id: str,
        policy_revision: int,
        *,
        session: object,
    ) -> LegalWorkMaterializationPolicy:
        """Return one exact tenant-scoped immutable policy revision."""
        tx = _transaction(
            session
        )

        tenant = _text(
            "tenant_id",
            tenant_id,
        )
        identity = _text(
            "policy_id",
            policy_id,
        )
        revision = _revision(
            policy_revision
        )

        raw = self._collection.find_one(
            {
                "tenant_id":
                    tenant,
                "policy_id":
                    identity,
                "policy_revision":
                    revision,
            },
            session=tx,
        )

        if raw is None:
            _raise(
                LegalWorkMaterializationPolicyRegistryNotFoundError,
                "P14_P9_POLICY_REVISION_NOT_FOUND",
            )

        value = self._hydrate(
            raw
        )

        if (
            value.tenant_id != tenant
            or value.policy_id != identity
            or value.policy_revision != revision
        ):
            _raise(
                LegalWorkMaterializationPolicyRegistryPersistedRecordInvalidError,
                "P14_P9_PERSISTED_SCOPE_MISMATCH",
            )

        return value

    def get_history(
        self,
        tenant_id: str,
        policy_id: str,
        *,
        session: object,
    ) -> tuple[
        LegalWorkMaterializationPolicy,
        ...,
    ]:
        """Return complete immutable policy history in ascending revision order."""
        tx = _transaction(
            session
        )

        tenant = _text(
            "tenant_id",
            tenant_id,
        )
        identity = _text(
            "policy_id",
            policy_id,
        )

        raws = tuple(
            self._collection.find(
                {
                    "tenant_id":
                        tenant,
                    "policy_id":
                        identity,
                },
                session=tx,
            )
        )

        values = tuple(
            sorted(
                (
                    self._hydrate(raw)
                    for raw in raws
                ),
                key=lambda item:
                    item.policy_revision,
            )
        )

        for expected_revision, value in enumerate(
            values,
            start=1,
        ):
            if (
                value.tenant_id != tenant
                or value.policy_id != identity
                or value.policy_revision
                != expected_revision
            ):
                _raise(
                    LegalWorkMaterializationPolicyRegistryPersistedRecordInvalidError,
                    "P14_P9_HISTORY_REVISION_INVALID",
                )

            if expected_revision == 1:
                if value.supersedes_fingerprint is not None:
                    _raise(
                        LegalWorkMaterializationPolicyRegistryPersistedRecordInvalidError,
                        "P14_P9_HISTORY_FIRST_REVISION_SUPERSEDES",
                    )
                continue

            previous = values[
                expected_revision - 2
            ]

            if (
                value.supersedes_fingerprint
                != previous.fingerprint
            ):
                _raise(
                    LegalWorkMaterializationPolicyRegistryPersistedRecordInvalidError,
                    "P14_P9_HISTORY_SUPERSESSION_INVALID",
                )

        return values

    def get_latest(
        self,
        tenant_id: str,
        policy_id: str,
        *,
        session: object,
    ) -> LegalWorkMaterializationPolicy:
        """Derive latest durable policy truth from immutable history."""
        history = self.get_history(
            tenant_id,
            policy_id,
            session=session,
        )

        if not history:
            _raise(
                LegalWorkMaterializationPolicyRegistryNotFoundError,
                "P14_P9_POLICY_HISTORY_NOT_FOUND",
            )

        return history[-1]

    def list_workflow(
        self,
        tenant_id: str,
        workflow_definition_id: str,
        *,
        session: object,
    ) -> tuple[
        LegalWorkMaterializationPolicy,
        ...,
    ]:
        """List tenant-scoped policy revisions for one workflow definition."""
        tx = _transaction(
            session
        )

        tenant = _text(
            "tenant_id",
            tenant_id,
        )
        workflow = _text(
            "workflow_definition_id",
            workflow_definition_id,
        )

        raws = tuple(
            self._collection.find(
                {
                    "tenant_id":
                        tenant,
                    "workflow_definition_id":
                        workflow,
                },
                session=tx,
            )
        )

        values = tuple(
            sorted(
                (
                    self._hydrate(raw)
                    for raw in raws
                ),
                key=lambda item: (
                    item.policy_id,
                    item.policy_revision,
                ),
            )
        )

        for value in values:
            if (
                value.tenant_id != tenant
                or value.workflow_definition_id
                != workflow
            ):
                _raise(
                    LegalWorkMaterializationPolicyRegistryPersistedRecordInvalidError,
                    "P14_P9_WORKFLOW_SCOPE_MISMATCH",
                )

        return values

    def list_workflow_stage(
        self,
        tenant_id: str,
        workflow_definition_id: str,
        target_stage_definition_id: str,
        *,
        session: object,
    ) -> tuple[
        LegalWorkMaterializationPolicy,
        ...,
    ]:
        """List tenant/workflow/stage-scoped immutable policy revisions."""
        tx = _transaction(
            session
        )

        tenant = _text(
            "tenant_id",
            tenant_id,
        )
        workflow = _text(
            "workflow_definition_id",
            workflow_definition_id,
        )
        stage = _text(
            "target_stage_definition_id",
            target_stage_definition_id,
        )

        raws = tuple(
            self._collection.find(
                {
                    "tenant_id":
                        tenant,
                    "workflow_definition_id":
                        workflow,
                    "target_stage_definition_id":
                        stage,
                },
                session=tx,
            )
        )

        values = tuple(
            sorted(
                (
                    self._hydrate(raw)
                    for raw in raws
                ),
                key=lambda item: (
                    item.policy_id,
                    item.policy_revision,
                ),
            )
        )

        for value in values:
            if (
                value.tenant_id != tenant
                or value.workflow_definition_id
                != workflow
                or value.target_stage_definition_id
                != stage
            ):
                _raise(
                    LegalWorkMaterializationPolicyRegistryPersistedRecordInvalidError,
                    "P14_P9_WORKFLOW_STAGE_SCOPE_MISMATCH",
                )

        return values


__all__ = [
    "COLLECTION_NAME",
    "VERSION",
    "LegalWorkMaterializationPolicyRegistry",
    "LegalWorkMaterializationPolicyRegistryConflictError",
    "LegalWorkMaterializationPolicyRegistryError",
    "LegalWorkMaterializationPolicyRegistryInputError",
    "LegalWorkMaterializationPolicyRegistryNotFoundError",
    "LegalWorkMaterializationPolicyRegistryPersistedRecordInvalidError",
    "LegalWorkMaterializationPolicyRegistryPersistenceError",
    "LegalWorkMaterializationPolicyRegistryRetryTransactionError",
    "LegalWorkMaterializationPolicyRegistryTransactionRequiredError",
]


# ==============================================================================
# WILSY OS SOVEREIGN ARTIFACT SEAL
# ==============================================================================
# ARTIFACT: legal_work_materialization_policy_registry.py
# VERSION: v1.0.0-P14-P9-WORK-MATERIALIZATION-POLICY-REGISTRY
# AUTHORITY BOUNDARY: immutable persistence and read projection only
# COMPETITIVE POSTURE: durable stage-trigger/dependency/due-policy history
# TENANT POSTURE: exact tenant-first correlation on every durable operation
# IMMUTABLE REVISION HISTORY: YES
# EXACT REPLAY: YES
# CURRENT TRUTH: derived from history; no mutable pointer
# CALLER-OWNED ACTIVE TRANSACTION REQUIRED: YES
# TTL / UPDATE / REPLACE / DELETE / UPSERT: NONE
# WORK-ITEM CREATION AUTHORITY: NONE
# ASSIGNMENT AUTHORITY: NONE
# SUPERVISION AUTHORITY: NONE
# IAM / PROFESSIONAL AUTHORITY: NONE
# LEGAL-DEADLINE AUTHORITY: NONE
# NOTIFICATION-DELIVERY AUTHORITY: NONE
# AI EXECUTION AUTHORITY: NONE
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively
# END OF WILSY OS SOVEREIGN ARTIFACT
