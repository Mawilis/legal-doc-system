"""Durable tenant-scoped persistence authority for immutable execution commands.

VERSION: v1.0.2-KENNEL-FINANCIAL-EXECUTION-COMMAND-REGISTRY
TITLE: Financial Execution Command Registry
PURPOSE: Persist authorized command material for process-failure recovery.
AUTHORITY: Immutable command persistence, replay, and corruption detection only.
EPITOME: Tenant-bound `$setOnInsert` storage preserves command identity without overwrites.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tools/eos/kennel/registry/financial_execution_command_registry.py
COLLABORATION / OWNERSHIP: Wilson Khanyezi (Founder); Codex (AI Engineering)
CERTIFICATION DATE: 2026-08-28
CHANGELOG: v1.0.2 preserves caller-owned transaction-control taxonomy by propagating labeled TransientTransactionError and UnknownTransactionCommitResult unchanged; unlabeled PyMongo failures remain registry-wrapped and transaction ownership is unchanged. v1.0.1 corrected provider-name hydration fallback evaluation; v1.0.0 established caller-session command persistence, exact replay, divergent conflict, and corruption-first hydration.
COMPLIANCE: POPIA | GDPR | SOC2
SECURITY / PRIVACY: opaque references only; raw credentials and provider payloads are forbidden.
TENANT BOUNDARY: every identity filter includes tenant_id.
TRANSACTION BOUNDARY: caller-owned sessions; this registry never starts, commits, aborts, or retries transactions.
FINANCIAL AUTHORITY BOUNDARY: no attempt, provider, execution-truth, settlement, ledger, or payable authority.
"""
from __future__ import annotations

import hashlib
from datetime import datetime, timezone
from typing import Any, Mapping, Optional

from pymongo import ASCENDING
from pymongo.client_session import ClientSession
from pymongo.collection import Collection
from pymongo.errors import PyMongoError

from ..domain.financial_execution_command import FinancialExecutionCommand, FinancialExecutionCommandError

VERSION = "v1.0.2-KENNEL-FINANCIAL-EXECUTION-COMMAND-REGISTRY"
COLLECTION = "kennel_financial_execution_commands"


class FinancialExecutionCommandRegistryError(RuntimeError):
    """Base fail-closed command persistence error."""


class FinancialExecutionCommandNotFoundError(FinancialExecutionCommandRegistryError):
    """Tenant-scoped command absence."""


class FinancialExecutionCommandPersistedRecordInvalidError(FinancialExecutionCommandRegistryError):
    """Persisted command corruption detected before replay or return."""


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


def _fingerprint(command: FinancialExecutionCommand) -> str:
    """Return the command's canonical synchronous-compatible fingerprint."""
    return command.fingerprint


def _document(command: FinancialExecutionCommand) -> dict[str, Any]:
    """Build the complete immutable persistence projection."""
    return {
        **command.evidence_payload(),
        "created_at": command.created_at.isoformat(),
        "provider_name": command.provider_name,
        "provider_metadata_reference": command.provider_metadata_reference,
        "command_fingerprint": _fingerprint(command),
    }


def _hydrate(document: Mapping[str, Any]) -> FinancialExecutionCommand:
    """Hydrate and validate canonical command material before any classification."""
    try:
        data = dict(document)
        stored = data.pop("command_fingerprint", None)
        data.pop("_id", None)
        created_at = data.get("created_at")
        if isinstance(created_at, str):
            data["created_at"] = datetime.fromisoformat(created_at)
        elif isinstance(created_at, datetime) and created_at.tzinfo is None:
            data["created_at"] = created_at.replace(tzinfo=timezone.utc)
        has_provider_name = "provider_name" in data
        has_legacy_provider = "requested_provider" in data
        provider_name = data.pop("provider_name") if has_provider_name else data.pop("requested_provider", None)
        if has_provider_name and has_legacy_provider:
            legacy_provider = data.pop("requested_provider")
            if legacy_provider != provider_name:
                raise ValueError("provider-name fields diverge")
        data["provider_name"] = provider_name
        command = FinancialExecutionCommand(**data)
        if not isinstance(stored, str) or stored != _fingerprint(command):
            raise ValueError("command fingerprint mismatch")
        return command
    except (TypeError, ValueError, KeyError, FinancialExecutionCommandError) as error:
        raise FinancialExecutionCommandPersistedRecordInvalidError("FINANCIAL_EXECUTION_COMMAND_PERSISTED_RECORD_INVALID") from error


class FinancialExecutionCommandCreateResult:
    """Immutable-style command create result containing outcome and durable command."""

    __slots__ = ("outcome", "command")

    def __init__(self, outcome: str, command: FinancialExecutionCommand) -> None:
        self.outcome = outcome
        self.command = command


class FinancialExecutionCommandRegistry:
    """Persists immutable command material; never owns attempts, truth, or settlement."""

    @staticmethod
    def ensure_indexes(collection: Optional[Collection] = None) -> None:
        """Create only indexes justified by canonical command retrieval."""
        target = _target(collection)
        target.create_index([('tenant_id', ASCENDING), ('execution_command_id', ASCENDING)], unique=True, name='tenant_execution_command_identity_unique')
        target.create_index([('tenant_id', ASCENDING), ('payable_id', ASCENDING), ('created_at', ASCENDING)], name='tenant_payable_commands_timeline')
        target.create_index([('tenant_id', ASCENDING), ('release_authorization_id', ASCENDING), ('created_at', ASCENDING)], name='tenant_release_authorization_commands_timeline')

    @staticmethod
    def create(command: FinancialExecutionCommand, collection: Optional[Collection] = None, *, session: Optional[ClientSession] = None) -> FinancialExecutionCommandCreateResult:
        """Create immutably or classify exact replay within the caller's session."""
        if not isinstance(command, FinancialExecutionCommand):
            raise FinancialExecutionCommandCreateConflictError("FINANCIAL_EXECUTION_COMMAND_CREATE_INVALID")
        target = _target(collection)
        identity = {'tenant_id': command.tenant_id, 'execution_command_id': command.execution_command_id}
        try:
            result = target.update_one(identity, {'$setOnInsert': _document(command)}, upsert=True, session=session)
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
    def get(tenant_id: str, execution_command_id: str, collection: Optional[Collection] = None, *, session: Optional[ClientSession] = None) -> FinancialExecutionCommand:
        """Return one tenant-scoped command after corruption-first hydration."""
        row = _target(collection).find_one({'tenant_id': str(tenant_id).strip(), 'execution_command_id': str(execution_command_id).strip()}, session=session)
        if row is None:
            raise FinancialExecutionCommandNotFoundError("FINANCIAL_EXECUTION_COMMAND_NOT_FOUND")
        return _hydrate(row)

    @staticmethod
    def list_for_payable(tenant_id: str, payable_id: str, limit: int = 100, collection: Optional[Collection] = None, *, session: Optional[ClientSession] = None) -> tuple[FinancialExecutionCommand, ...]:
        """Return bounded tenant-scoped command history for one payable."""
        if not isinstance(limit, int) or isinstance(limit, bool) or not 1 <= limit <= 250:
            raise FinancialExecutionCommandRegistryError("limit must be between 1 and 250")
        rows = _target(collection).find({'tenant_id': str(tenant_id).strip(), 'payable_id': str(payable_id).strip()}, session=session).sort([('created_at', ASCENDING), ('execution_command_id', ASCENDING)]).limit(limit)
        return tuple(_hydrate(row) for row in rows)


# ARTIFACT: financial_execution_command_registry.py
# VERSION: v1.0.2-KENNEL-FINANCIAL-EXECUTION-COMMAND-REGISTRY
# AUTHORITY BOUNDARY: immutable command persistence only; no attempt, truth, provider, or settlement authority.
# TENANT POSTURE: all reads and writes are tenant-scoped.
# FAIL-CLOSED POSTURE: corruption and divergent identity material never replay or overwrite.
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively owns execution truth; this registry does not create it.
# END OF WILSY OS SOVEREIGN ARTIFACT
