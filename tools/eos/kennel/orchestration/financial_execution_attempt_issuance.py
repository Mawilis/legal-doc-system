"""TITLE: Financial Execution Attempt Issuance
VERSION: v1.1.0-M11-P5-R2D-R0-R1
AUTHORITY: Wilsy OS Core Governance / Kennel EOS.
EPITOME: Canonical command readback and exact lineage before PREPARED attempt construction.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tools/eos/kennel/orchestration/financial_execution_attempt_issuance.py
COLLABORATION / OWNERSHIP: Kennel EOS execution-attempt orchestration owner.
CERTIFICATION / UPDATE DATE: 2026-09-08.
CHANGELOG: v1.1.0-M11-P5-R2D-R0-R1 removes caller-command authority, requires tenant-scoped canonical command readback, and projects attempts from the exact durable command fact.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2.
SECURITY / PRIVACY POSTURE: Opaque tenant-scoped references only; no provider payloads or credentials.
TENANT BOUNDARY: Canonical command lookup and all projected attempt identities remain tenant-scoped.
AUTHORITY BOUNDARY: Durable FinancialExecutionCommand is the sole command authority; issuance is preparation only.
FINANCIAL AUTHORITY BOUNDARY: No provider transport, execution truth, settlement, paid state, or receivable mutation.
TRANSACTION BOUNDARY: Caller supplies the session; this owner never starts, commits, aborts, or retries a transaction.
FAIL-CLOSED DECLARATION: Missing, cross-tenant, divergent, or mismatched command authority rejects before attempt construction.
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime

from pymongo.client_session import ClientSession
from pymongo.collection import Collection

from tools.eos.kennel.domain.financial_execution_command import FinancialExecutionCommand
from tools.eos.kennel.domain.financial_execution_lifecycle import (
    FinancialExecutionAttempt,
    FinancialExecutionAttemptState,
)
from tools.eos.kennel.registry.financial_execution_command_registry import (
    FinancialExecutionCommandRegistry,
    FinancialExecutionCommandRegistryError,
)

VERSION = "v1.1.0-M11-P5-R2D-R0-R1"


class FinancialExecutionAttemptIssuanceError(RuntimeError):
    """Fail-closed error for canonical command admission or projection."""


@dataclass(frozen=True)
class FinancialExecutionAttemptIssuance:
    """Explicit attempt-only authority; command material is never duplicated."""

    execution_attempt_id: str
    provider_name: str
    created_at: datetime
    destination_fingerprint: str | None = None
    request_evidence_reference: str | None = None


def _require_active_session(session: ClientSession | None) -> ClientSession:
    """Require a caller-owned active transaction for the canonical read."""
    if session is None or getattr(session, "in_transaction", False) is not True:
        raise FinancialExecutionAttemptIssuanceError("ACTIVE_TRANSACTION_REQUIRED")
    return session


def _canonical_command(
    command: FinancialExecutionCommand,
    command_collection: Collection,
    session: ClientSession,
) -> FinancialExecutionCommand:
    """Read and strictly hydrate the command identified by the caller proposal."""
    try:
        canonical = FinancialExecutionCommandRegistry.get(
            command.tenant_id,
            command.execution_command_id,
            command_collection,
            session=session,
        )
    except FinancialExecutionCommandRegistryError as error:
        raise FinancialExecutionAttemptIssuanceError(
            "CANONICAL_COMMAND_REQUIRED"
        ) from error
    if not isinstance(canonical, FinancialExecutionCommand):
        raise FinancialExecutionAttemptIssuanceError("CANONICAL_COMMAND_REQUIRED")
    if (
        command.tenant_id != canonical.tenant_id
        or command.execution_command_id != canonical.execution_command_id
        or command.fingerprint != canonical.fingerprint
    ):
        raise FinancialExecutionAttemptIssuanceError(
            "CALLER_COMMAND_CANONICAL_MISMATCH"
        )
    return canonical


def issue_financial_execution_attempt(
    command: FinancialExecutionCommand,
    issuance: FinancialExecutionAttemptIssuance,
    *,
    command_collection: Collection,
    session: ClientSession,
) -> FinancialExecutionAttempt:
    """Construct one PREPARED attempt from the exact durable command fact.

    The supplied command is an identifier/equality proposal only. It must
    strictly match the tenant-scoped durable command before any attempt is
    constructed. The canonical command, not the caller copy, supplies every
    command-projected attempt field. ``issuance.provider_name`` remains a
    correlation assertion and cannot select or override a provider.
    """
    if not isinstance(command, FinancialExecutionCommand):
        raise TypeError("command must be FinancialExecutionCommand")
    if not isinstance(issuance, FinancialExecutionAttemptIssuance):
        raise TypeError("issuance must be FinancialExecutionAttemptIssuance")
    tx = _require_active_session(session)
    canonical = _canonical_command(command, command_collection, tx)
    if issuance.provider_name != canonical.provider_name:
        raise ValueError("attempt provider differs from canonical command provider")
    return FinancialExecutionAttempt(
        execution_attempt_id=issuance.execution_attempt_id,
        tenant_id=canonical.tenant_id,
        execution_command_id=canonical.execution_command_id,
        provider_name=canonical.provider_name,
        state=FinancialExecutionAttemptState.PREPARED,
        payment_destination_reference=canonical.payment_destination_reference,
        request_fingerprint=canonical.fingerprint,
        destination_fingerprint=issuance.destination_fingerprint,
        request_evidence_reference=issuance.request_evidence_reference,
        created_at=issuance.created_at,
    )


# ARTIFACT: financial_execution_attempt_issuance.py
# VERSION: v1.1.0-M11-P5-R2D-R0-R1
# AUTHORITY BOUNDARY: canonical command admission and PREPARED attempt construction only; no provider, truth, or settlement authority.
# TENANT POSTURE: exact tenant-scoped command readback and immutable attempt projection.
# FAIL-CLOSED POSTURE: missing or divergent command material rejects before construction.
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively owns later execution truth.
# END OF WILSY OS SOVEREIGN ARTIFACT
