"""TITLE: Financial Execution Runtime Orchestrator.
VERSION: v1.0.0-M11-P5-R2E-R2.
AUTHORITY: Wilsy OS Core Governance / Kennel EOS.
EPITOME: Compose one certified neutral execution fact with the closed family-specific truth projection.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tools/eos/kennel/orchestration/financial_execution_runtime_orchestrator.py
COLLABORATION / OWNERSHIP: Kennel EOS post-terminalization orchestration owner.
CERTIFICATION / UPDATE DATE: 2026-09-08.
CHANGELOG: v1.0.0-M11-P5-R2E-R2 establishes unmounted, caller-transaction-bound AP/Platform family dispatch without duplicating financial authority.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2.
SECURITY / PRIVACY POSTURE: Tenant-scoped opaque identifiers only; no credentials, provider transport, or payment payloads.
TENANT BOUNDARY: Neutral derivation and command recovery are exact tenant-scoped operations.
AUTHORITY BOUNDARY: Composition only; certified derivation and family projection owners retain business authority.
FINANCIAL AUTHORITY BOUNDARY: No command issuance, provider selection, settlement, paid state, receivable closure, or ClientInvoice authority.
TRANSACTION BOUNDARY: Caller-owned active session spans derivation, command recovery, and family projection; lifecycle is never owned here.
FAIL-CLOSED DECLARATION: Missing, malformed, uncorrelated, unsupported, and unknown family material rejects without partial success.
"""
from __future__ import annotations

from typing import NoReturn

from pymongo.client_session import ClientSession
from pymongo.collection import Collection

from ..domain.financial_execution import FinancialExecutionFact, FinancialExecutionTruth
from ..domain.financial_execution_command import (
    FinancialExecutionCommand,
    FinancialExecutionCommandFamily,
)
from ..domain.financial_execution_execution_time_evidence import FinancialExecutionTimeEvidence
from ..domain.platform_billing_financial_execution_truth import PlatformBillingFinancialExecutionTruth
from ..registry.financial_execution_command_registry import FinancialExecutionCommandRegistry
from ..registry.financial_execution_registry import (
    FinancialExecutionFactCreateResult,
)
from .accounts_payable_financial_execution_truth_projection import (
    project_financial_execution_fact_to_accounts_payable,
)
from .financial_execution_truth_derivation import derive_financial_execution_fact
from .platform_billing_execution_truth_bridge import bridge_financial_execution_fact_to_platform

VERSION = "v1.0.0-M11-P5-R2E-R2"


class FinancialExecutionRuntimeOrchestratorError(RuntimeError):
    """Fail-closed composition error before family truth is returned."""

    def __init__(self, code: str) -> None:
        self.code = code
        super().__init__(code)


def _reject(code: str) -> NoReturn:
    """Reject malformed composition state without converting it to success."""
    raise FinancialExecutionRuntimeOrchestratorError(code)


def _active_session(session: ClientSession) -> ClientSession:
    """Require the caller-owned active transaction before any child operation."""
    if session is None or not bool(getattr(session, "in_transaction", False)):
        _reject("ACTIVE_TRANSACTION_REQUIRED")
    return session


def _recover_fact(result: object) -> FinancialExecutionFact:
    """Recover only the canonical fact object returned by certified derivation."""
    if not isinstance(result, FinancialExecutionFactCreateResult):
        _reject("NEUTRAL_FACT_DERIVATION_RESULT_REQUIRED")
    fact = result.execution_fact
    if not isinstance(fact, FinancialExecutionFact):
        _reject("NEUTRAL_FACT_REQUIRED")
    return fact


def _correlate_fact_command(
    tenant_id: str,
    fact: FinancialExecutionFact,
    command: object,
) -> FinancialExecutionCommand:
    """Prove fact/command lineage before consulting family authority."""
    if not isinstance(command, FinancialExecutionCommand):
        _reject("FINANCIAL_EXECUTION_COMMAND_REQUIRED")
    if fact.tenant_id != tenant_id or command.tenant_id != tenant_id:
        _reject("FACT_COMMAND_TENANT_CORRELATION_MISMATCH")
    if fact.execution_command_id != command.execution_command_id:
        _reject("FACT_COMMAND_ID_CORRELATION_MISMATCH")
    if fact.execution_command_fingerprint != command.fingerprint:
        _reject("FACT_COMMAND_FINGERPRINT_CORRELATION_MISMATCH")
    if fact.provider != command.provider_name:
        _reject("FACT_COMMAND_PROVIDER_CORRELATION_MISMATCH")
    if fact.executed_amount_minor != command.amount_minor:
        _reject("FACT_COMMAND_AMOUNT_CORRELATION_MISMATCH")
    if fact.currency != command.currency:
        _reject("FACT_COMMAND_CURRENCY_CORRELATION_MISMATCH")
    if fact.payment_destination_reference != command.payment_destination_reference:
        _reject("FACT_COMMAND_DESTINATION_CORRELATION_MISMATCH")
    return command


def orchestrate_terminal_execution_fact_and_projection(
    tenant_id: str,
    execution_attempt_id: str,
    *,
    command_collection: Collection,
    attempt_collection: Collection,
    observation_collection: Collection,
    fact_collection: Collection,
    ap_truth_collection: Collection,
    platform_truth_collection: Collection,
    execution_time_evidence: FinancialExecutionTimeEvidence,
    session: ClientSession,
) -> FinancialExecutionTruth | PlatformBillingFinancialExecutionTruth:
    """Derive/replay one neutral fact and dispatch its canonical command family.

    The caller supplies an already-active transaction and persistence
    dependencies.  Certified derivation owns observation and terminalization;
    certified AP and Platform owners each own their truth schema and replay
    semantics.  This composer performs no transaction lifecycle, provider
    transport or selection, policy lookup, settlement, invoice, or receivable
    work, and has no production caller mount in this gate.
    """
    tx = _active_session(session)
    derived = derive_financial_execution_fact(
        tenant_id,
        execution_attempt_id,
        command_collection=command_collection,
        attempt_collection=attempt_collection,
        observation_collection=observation_collection,
        fact_collection=fact_collection,
        execution_time_evidence=execution_time_evidence,
        session=tx,
    )
    fact = _recover_fact(derived)
    command = FinancialExecutionCommandRegistry.get(
        tenant_id,
        fact.execution_command_id,
        command_collection,
        session=tx,
    )
    command = _correlate_fact_command(tenant_id, fact, command)
    family = command.source_authority_kind
    if family is FinancialExecutionCommandFamily.ACCOUNTS_PAYABLE:
        return project_financial_execution_fact_to_accounts_payable(
            tenant_id,
            fact.execution_fact_id,
            fact_collection=fact_collection,
            command_collection=command_collection,
            truth_collection=ap_truth_collection,
            session=tx,
        )
    if family is FinancialExecutionCommandFamily.PLATFORM_BILLING:
        return bridge_financial_execution_fact_to_platform(
            tenant_id,
            fact.execution_fact_id,
            fact_collection=fact_collection,
            command_collection=command_collection,
            platform_truth_collection=platform_truth_collection,
            session=tx,
        )
    _reject("UNSUPPORTED_FINANCIAL_EXECUTION_COMMAND_FAMILY")


# ARTIFACT: financial_execution_runtime_orchestrator.py
# VERSION: v1.0.0-M11-P5-R2E-R2
# AUTHORITY BOUNDARY: composition-only dispatch from certified neutral fact and canonical command family.
# TENANT POSTURE: tenant-scoped derivation, command recovery, and child projection with one caller session.
# FAIL-CLOSED POSTURE: uncorrelated, unsupported, and malformed family material rejects; child failures propagate.
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively; no settlement, paid state, or receivable closure.
# END OF WILSY OS SOVEREIGN ARTIFACT
