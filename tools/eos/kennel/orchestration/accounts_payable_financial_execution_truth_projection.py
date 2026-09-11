"""TITLE: Accounts Payable Financial Execution Truth Projection.
VERSION: v1.0.0-M11-P5-R2E-R1-R2.
AUTHORITY: Wilsy OS Core Governance / Kennel EOS.
EPITOME: Project certified neutral execution facts through canonical AP command provenance into immutable AP execution truth.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tools/eos/kennel/orchestration/accounts_payable_financial_execution_truth_projection.py
COLLABORATION / OWNERSHIP: Kennel EOS AP execution-evidence projection owner.
CERTIFICATION / UPDATE DATE: 2026-09-08.
CHANGELOG: v1.0.0-M11-P5-R2E-R1-R2 establishes neutral-fact-to-AP-truth projection without observation reread, terminalization rerun, provider transport, or settlement authority.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2.
SECURITY / PRIVACY POSTURE: Opaque tenant-scoped references only; no credentials/provider payloads.
TENANT BOUNDARY: Fact and command reads, correlation, and AP persistence are exact tenant scoped.
AUTHORITY BOUNDARY: Neutral fact supplies execution evidence; typed AP command source supplies payable/release authority.
FINANCIAL AUTHORITY BOUNDARY: No provider, settlement, paid state, receivable, or ClientInvoice authority.
TRANSACTION BOUNDARY: Caller-owned active session is required and forwarded unchanged.
FAIL-CLOSED DECLARATION: Missing, cross-family, wrong-source, divergent, or mismatched evidence rejects before AP truth construction.
"""
from __future__ import annotations

from datetime import timezone
from typing import NoReturn, Optional, cast

from pymongo.client_session import ClientSession
from pymongo.collection import Collection

from ..domain.financial_execution import (
    FinancialExecutionFact,
    FinancialExecutionStatus,
    FinancialExecutionTruth,
)
from ..domain.financial_execution_command import (
    AccountsPayableCommandSource,
    FinancialExecutionCommandFamily,
)
from ..registry.financial_execution_command_registry import FinancialExecutionCommandRegistry
from ..registry.financial_execution_registry import (
    FinancialExecutionFactRegistry,
    FinancialExecutionTruthRegistry,
)

VERSION = "v1.0.0-M11-P5-R2E-R1-R2"


class AccountsPayableFinancialExecutionTruthProjectionError(RuntimeError):
    """Fail-closed error for an invalid AP fact-to-truth projection."""

    def __init__(self, code: str) -> None:
        self.code = code
        super().__init__(code)


def _reject(code: str) -> NoReturn:
    """Raise one stable projection error without manufacturing financial truth."""
    raise AccountsPayableFinancialExecutionTruthProjectionError(code)


def _active_session(session: Optional[ClientSession]) -> ClientSession:
    """Require a caller-owned active transaction before any authority read."""
    if session is None or not bool(getattr(session, "in_transaction", False)):
        _reject("ACTIVE_TRANSACTION_REQUIRED")
    return session


def _correlate(
    tenant_id: str,
    fact: FinancialExecutionFact,
    command: object,
) -> AccountsPayableCommandSource:
    """Correlate every neutral fact field with the exact durable AP command."""
    from ..domain.financial_execution_command import FinancialExecutionCommand

    if not isinstance(command, FinancialExecutionCommand):
        _reject("FINANCIAL_EXECUTION_COMMAND_REQUIRED")
    if command.tenant_id != tenant_id or fact.tenant_id != tenant_id:
        _reject("TENANT_CORRELATION_MISMATCH")
    if command.source_authority_kind is not FinancialExecutionCommandFamily.ACCOUNTS_PAYABLE:
        _reject("AP_COMMAND_FAMILY_REQUIRED")
    if type(command.source_authority) is not AccountsPayableCommandSource:
        _reject("AP_COMMAND_SOURCE_REQUIRED")
    source = cast(AccountsPayableCommandSource, command.source_authority)
    if fact.execution_command_id != command.execution_command_id:
        _reject("COMMAND_ID_CORRELATION_MISMATCH")
    if fact.execution_command_fingerprint != command.fingerprint:
        _reject("COMMAND_FINGERPRINT_CORRELATION_MISMATCH")
    if fact.provider != command.provider_name:
        _reject("PROVIDER_CORRELATION_MISMATCH")
    if fact.executed_amount_minor != command.amount_minor:
        _reject("AMOUNT_CORRELATION_MISMATCH")
    if fact.currency != command.currency:
        _reject("CURRENCY_CORRELATION_MISMATCH")
    if fact.payment_destination_reference != command.payment_destination_reference:
        _reject("DESTINATION_CORRELATION_MISMATCH")
    return source


def project_financial_execution_fact_to_accounts_payable(
    tenant_id: str,
    execution_fact_id: str,
    *,
    fact_collection: Collection,
    command_collection: Collection,
    truth_collection: Collection,
    session: ClientSession,
) -> FinancialExecutionTruth:
    """Project one already-terminalized fact into immutable AP execution truth.

    The caller owns the active Mongo transaction.  This function reads the
    exact tenant/fact identity, follows only the fact's command ID, verifies a
    typed AP source and exact semantic correlations, then delegates persistence
    and replay adjudication to ``FinancialExecutionTruthRegistry.create``.
    It does not reread provider observations, rerun terminalization, derive a
    second fact, invoke or select a provider, or create settlement/receivable
    or ClientInvoice state.
    """
    tx = _active_session(session)
    try:
        fact = FinancialExecutionFactRegistry.get(
            tenant_id, execution_fact_id, fact_collection, session=tx
        )
    except Exception as error:
        raise AccountsPayableFinancialExecutionTruthProjectionError(
            "FINANCIAL_EXECUTION_FACT_READ_FAILED"
        ) from error
    if fact is None or not isinstance(fact, FinancialExecutionFact):
        _reject("FINANCIAL_EXECUTION_FACT_REQUIRED")
    if fact.execution_fact_id != execution_fact_id:
        _reject("FACT_ID_CORRELATION_MISMATCH")
    if fact.execution_status not in (
        FinancialExecutionStatus.EXECUTED,
        FinancialExecutionStatus.FAILED,
    ):
        _reject("TERMINAL_EXECUTION_FACT_REQUIRED")
    try:
        command = FinancialExecutionCommandRegistry.get(
            tenant_id, fact.execution_command_id, command_collection, session=tx
        )
    except Exception as error:
        raise AccountsPayableFinancialExecutionTruthProjectionError(
            "FINANCIAL_EXECUTION_COMMAND_READ_FAILED"
        ) from error
    source = _correlate(tenant_id, fact, command)
    from ..domain.financial_execution_command import FinancialExecutionCommand

    canonical_command = cast(FinancialExecutionCommand, command)
    try:
        truth = FinancialExecutionTruth(
            execution_truth_id=canonical_command.execution_command_id,
            tenant_id=canonical_command.tenant_id,
            payable_id=source.payable_id,
            release_authorization_id=source.release_authorization_id,
            provider=fact.provider,
            provider_execution_reference=fact.provider_execution_reference,
            execution_status=fact.execution_status,
            executed_amount_minor=canonical_command.amount_minor,
            currency=canonical_command.currency,
            executed_at=fact.executed_at,
            payment_destination_reference=canonical_command.payment_destination_reference,
            provider_evidence_reference=fact.provider_evidence_reference,
            execution_command_fingerprint=canonical_command.fingerprint,
            execution_evidence_fingerprint=fact.execution_evidence_fingerprint,
            created_at=canonical_command.created_at.astimezone(timezone.utc),
        )
    except Exception as error:
        raise AccountsPayableFinancialExecutionTruthProjectionError(
            "FINANCIAL_EXECUTION_TRUTH_CONSTRUCTION_FAILED"
        ) from error
    try:
        result = FinancialExecutionTruthRegistry.create(
            truth,
            canonical_command.idempotency_key,
            truth_collection,
            session=tx,
        )
    except Exception as error:
        raise AccountsPayableFinancialExecutionTruthProjectionError(
            "FINANCIAL_EXECUTION_TRUTH_PERSISTENCE_FAILED"
        ) from error
    return result.execution_truth


# ARTIFACT: accounts_payable_financial_execution_truth_projection.py
# VERSION: v1.0.0-M11-P5-R2E-R1-R2
# AUTHORITY BOUNDARY: neutral execution fact plus typed AP command provenance projected into historical AP truth only.
# TENANT POSTURE: exact tenant-scoped fact and command reads; caller-owned transaction forwarded unchanged.
# FAIL-CLOSED POSTURE: missing, nonterminal, cross-family, mismatched, and divergent evidence rejects; registry owns replay.
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively; execution truth is not settlement or receivable closure.
# END OF WILSY OS SOVEREIGN ARTIFACT
