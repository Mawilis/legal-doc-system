"""WILSY OS strict persistence authority for family-discriminated commands.

TITLE: Financial Execution Command Registry
VERSION: v2.1.0-M11-P5-R2B-R1
AUTHORITY: Wilsy OS Core Governance / Kennel EOS
EPITOME: Persist and replay complete AP or Platform Billing command authority without reconstruction.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tools/eos/kennel/registry/financial_execution_command_registry.py
COLLABORATION / OWNERSHIP: Kennel EOS generic command persistence owner.
CERTIFICATION / UPDATE DATE: 2026-09-08
CHANGELOG: v2.1.0-M11-P5-R2B-R1 adds tenant/family/source-request uniqueness, exact source lookup, and fail-closed duplicate-key race adjudication while preserving command-ID replay law.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2.
SECURITY / PRIVACY POSTURE: Opaque references only; no provider credentials or payloads.
TENANT BOUNDARY: Every identity and source-request filter includes tenant_id.
AUTHORITY BOUNDARY: Persistence and strict hydration only; registry grants no provider or execution authority.
FINANCIAL AUTHORITY BOUNDARY: No attempt, provider execution, truth, settlement, paid state, or receivable mutation.
TRANSACTION BOUNDARY: Caller-owned sessions; registry never starts, commits, aborts, or retries transactions.
FAIL-CLOSED DECLARATION: Unknown fields, missing provenance, family mismatch, corruption, divergent replay, and source-request conflicts reject.
"""
from __future__ import annotations

from typing import Any, Optional

from pymongo import ASCENDING
from pymongo.client_session import ClientSession
from pymongo.collection import Collection
from pymongo.errors import DuplicateKeyError, PyMongoError

from ..domain.financial_execution_command import (
    FinancialExecutionCommand,
    FinancialExecutionCommandError,
    FinancialExecutionCommandFamily,
)

VERSION = "v2.1.0-M11-P5-R2B-R1"
COLLECTION = "kennel_financial_execution_commands"


class FinancialExecutionCommandRegistryError(RuntimeError):
    """Base fail-closed command persistence error."""


class FinancialExecutionCommandNotFoundError(FinancialExecutionCommandRegistryError):
    """Tenant-scoped command absence."""


class FinancialExecutionCommandPersistedRecordInvalidError(FinancialExecutionCommandRegistryError):
    """Persisted command corruption or incomplete authority detected."""


class FinancialExecutionCommandCreateConflictError(FinancialExecutionCommandRegistryError):
    """Divergent immutable material for an existing command identity."""


class FinancialExecutionCommandCreateOutcome(str):
    """Stable create classifications."""

    CREATED = "CREATED"
    IDEMPOTENT_REPLAY = "IDEMPOTENT_REPLAY"


def _target(collection: Optional[Collection]) -> Collection:
    """Resolve an injected collection without taking transaction ownership."""
    if collection is not None:
        return collection
    from ...kernel.db import get_database

    database = get_database()
    if database is None:
        raise FinancialExecutionCommandRegistryError("FINANCIAL_EXECUTION_COMMAND_PERSISTENCE_UNAVAILABLE")
    return database[COLLECTION]


def _hydrate(document: Any) -> FinancialExecutionCommand:
    """Hydrate only the exact current schema; never infer family or provenance."""
    try:
        return FinancialExecutionCommand.from_persisted(document)
    except (TypeError, ValueError, KeyError, FinancialExecutionCommandError) as error:
        raise FinancialExecutionCommandPersistedRecordInvalidError("FINANCIAL_EXECUTION_COMMAND_PERSISTED_RECORD_INVALID") from error


def _require_family(source_family: FinancialExecutionCommandFamily) -> FinancialExecutionCommandFamily:
    """Require the closed enum rather than accepting a free-form family string."""
    if not isinstance(source_family, FinancialExecutionCommandFamily):
        raise FinancialExecutionCommandRegistryError("SOURCE_REQUEST_FAMILY_INVALID")
    return source_family


def _source_request_query(
    tenant_id: str,
    source_family: FinancialExecutionCommandFamily,
    execution_request_id: str,
) -> dict[str, object]:
    """Build the exact persisted source-request query without normalization."""
    family = _require_family(source_family)
    return {
        "tenant_id": tenant_id,
        "source_authority_kind": family.value,
        "source_authority.execution_request_id": execution_request_id,
    }


class FinancialExecutionCommandCreateResult:
    """Immutable-style command create result containing outcome and durable command."""

    __slots__ = ("outcome", "command")

    def __init__(self, outcome: str, command: FinancialExecutionCommand) -> None:
        self.outcome = outcome
        self.command = command


class FinancialExecutionCommandRegistry:
    """Persist immutable command authority with tenant/family source replay."""

    @staticmethod
    def get_by_source_request(
        tenant_id: str,
        source_family: FinancialExecutionCommandFamily,
        execution_request_id: str,
        collection: Optional[Collection] = None,
        *,
        session: Optional[ClientSession] = None,
    ) -> FinancialExecutionCommand | None:
        """Return the sole exact source-request command or fail closed.

        Zero rows is canonical absence; one row is strictly hydrated; multiple
        rows are durable corruption and never trigger first/latest selection.
        """
        target = _target(collection)
        query = _source_request_query(tenant_id, source_family, execution_request_id)
        try:
            cursor = target.find(query, session=session)
            limited = cursor.limit(2) if hasattr(cursor, "limit") else cursor
            rows = list(limited)[:2]
            if len(rows) > 1:
                raise FinancialExecutionCommandRegistryError("MULTIPLE_SOURCE_REQUEST_ROWS")
            if not rows:
                return None
            command = _hydrate(rows[0])
            if (
                command.tenant_id != tenant_id
                or command.source_authority_kind is not source_family
                or command.source_authority.execution_request_id != execution_request_id
            ):
                raise FinancialExecutionCommandPersistedRecordInvalidError(
                    "FINANCIAL_EXECUTION_COMMAND_SOURCE_REQUEST_CORRELATION_INVALID"
                )
            return command
        except FinancialExecutionCommandRegistryError:
            raise
        except PyMongoError as error:
            raise FinancialExecutionCommandRegistryError(
                "FINANCIAL_EXECUTION_COMMAND_SOURCE_REQUEST_LOOKUP_FAILED"
            ) from error
        except Exception as error:
            raise FinancialExecutionCommandRegistryError(
                "FINANCIAL_EXECUTION_COMMAND_SOURCE_REQUEST_LOOKUP_FAILED"
            ) from error

    @staticmethod
    def _same_source_replay_or_conflict(
        candidate: FinancialExecutionCommand,
        existing: FinancialExecutionCommand,
    ) -> FinancialExecutionCommandCreateResult:
        """Classify a source-cardinality match without redefining exact replay."""
        if existing == candidate:
            return FinancialExecutionCommandCreateResult(
                FinancialExecutionCommandCreateOutcome.IDEMPOTENT_REPLAY,
                existing,
            )
        raise FinancialExecutionCommandCreateConflictError(
            "FINANCIAL_EXECUTION_COMMAND_SOURCE_REQUEST_CONFLICT"
        )

    @staticmethod
    def ensure_indexes(collection: Optional[Collection] = None) -> None:
        """Create command-ID and family-scoped source-request uniqueness indexes."""
        target = _target(collection)
        target.create_index(
            [("tenant_id", ASCENDING), ("execution_command_id", ASCENDING)],
            unique=True,
            name="tenant_execution_command_identity_unique",
        )
        target.create_index(
            [
                ("tenant_id", ASCENDING),
                ("source_authority_kind", ASCENDING),
                ("source_authority.execution_request_id", ASCENDING),
            ],
            unique=True,
            name="tenant_family_source_execution_request_unique",
        )
        target.create_index(
            [("tenant_id", ASCENDING), ("source_authority.payable_id", ASCENDING), ("created_at", ASCENDING)],
            name="tenant_payable_commands_timeline",
        )
        target.create_index(
            [("tenant_id", ASCENDING), ("source_authority.release_authorization_id", ASCENDING), ("created_at", ASCENDING)],
            name="tenant_release_authorization_commands_timeline",
        )

    @staticmethod
    def create(
        command: FinancialExecutionCommand,
        collection: Optional[Collection] = None,
        *,
        session: Optional[ClientSession] = None,
    ) -> FinancialExecutionCommandCreateResult:
        """Insert immutable authority, classify exact replay, or reject conflicts.

        Source-request cardinality is adjudicated before command-ID upsert. A
        duplicate-key race is read back through strict source lookup; a
        different command ID, provider, source, or fingerprint cannot overwrite,
        supersede, or become failover authority.
        """
        if not isinstance(command, FinancialExecutionCommand):
            raise FinancialExecutionCommandCreateConflictError("FINANCIAL_EXECUTION_COMMAND_CREATE_INVALID")
        target = _target(collection)
        source = command.source_authority
        existing_source = FinancialExecutionCommandRegistry.get_by_source_request(
            command.tenant_id,
            command.source_authority_kind,
            source.execution_request_id,
            target,
            session=session,
        )
        if existing_source is not None:
            return FinancialExecutionCommandRegistry._same_source_replay_or_conflict(command, existing_source)
        identity = {"tenant_id": command.tenant_id, "execution_command_id": command.execution_command_id}
        try:
            result = target.update_one(identity, {"$setOnInsert": command.to_persisted()}, upsert=True, session=session)
        except DuplicateKeyError:
            winner = FinancialExecutionCommandRegistry.get_by_source_request(
                command.tenant_id,
                command.source_authority_kind,
                source.execution_request_id,
                target,
                session=session,
            )
            if winner is None:
                raise FinancialExecutionCommandRegistryError(
                    "FINANCIAL_EXECUTION_COMMAND_SOURCE_REQUEST_RACE_UNRESOLVED"
                )
            return FinancialExecutionCommandRegistry._same_source_replay_or_conflict(command, winner)
        except PyMongoError as error:
            if error.has_error_label("TransientTransactionError") or error.has_error_label("UnknownTransactionCommitResult"):
                raise
            raise FinancialExecutionCommandRegistryError("FINANCIAL_EXECUTION_COMMAND_CREATE_FAILED") from error
        if result.upserted_id is not None:
            return FinancialExecutionCommandCreateResult(FinancialExecutionCommandCreateOutcome.CREATED, command)
        existing = target.find_one(identity, session=session)
        if existing is None:
            raise FinancialExecutionCommandCreateConflictError("FINANCIAL_EXECUTION_COMMAND_CREATE_CONFLICT")
        durable = _hydrate(existing)
        if durable == command:
            return FinancialExecutionCommandCreateResult(FinancialExecutionCommandCreateOutcome.IDEMPOTENT_REPLAY, durable)
        raise FinancialExecutionCommandCreateConflictError("FINANCIAL_EXECUTION_COMMAND_CREATE_CONFLICT")

    @staticmethod
    def get(
        tenant_id: str,
        execution_command_id: str,
        collection: Optional[Collection] = None,
        *,
        session: Optional[ClientSession] = None,
    ) -> FinancialExecutionCommand:
        """Return one tenant-scoped command after strict corruption-first hydration."""
        row = _target(collection).find_one(
            {"tenant_id": str(tenant_id).strip(), "execution_command_id": str(execution_command_id).strip()},
            session=session,
        )
        if row is None:
            raise FinancialExecutionCommandNotFoundError("FINANCIAL_EXECUTION_COMMAND_NOT_FOUND")
        return _hydrate(row)

    @staticmethod
    def list_for_payable(
        tenant_id: str,
        payable_id: str,
        limit: int = 100,
        collection: Optional[Collection] = None,
        *,
        session: Optional[ClientSession] = None,
    ) -> tuple[FinancialExecutionCommand, ...]:
        """Return bounded AP command history using the typed source subject."""
        if not isinstance(limit, int) or isinstance(limit, bool) or not 1 <= limit <= 250:
            raise FinancialExecutionCommandRegistryError("limit must be between 1 and 250")
        rows = _target(collection).find(
            {"tenant_id": str(tenant_id).strip(), "source_authority.payable_id": str(payable_id).strip()},
            session=session,
        ).sort([("created_at", ASCENDING), ("execution_command_id", ASCENDING)]).limit(limit)
        return tuple(_hydrate(row) for row in rows)


# ARTIFACT: financial_execution_command_registry.py
# VERSION: v2.1.0-M11-P5-R2B-R1
# AUTHORITY BOUNDARY: immutable family-aware command persistence only; no attempt, truth, provider, or settlement authority.
# TENANT POSTURE: all reads and writes are tenant-scoped; source uniqueness includes the closed family.
# FAIL-CLOSED POSTURE: missing, unknown, mixed, corrupt, divergent, and duplicate source material never replays or overwrites.
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively owns later execution truth.
# END OF WILSY OS SOVEREIGN ARTIFACT
