"""TITLE: Platform Billing Execution Truth Bridge
VERSION: v2.0.0-M11-P5-R2D-R1
AUTHORITY: Wilsy OS Core Governance / Kennel EOS
EPITOME: Project a durable neutral execution fact through a canonical Platform generic command.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tools/eos/kennel/orchestration/platform_billing_execution_truth_bridge.py
COLLABORATION / OWNERSHIP: Kennel EOS Platform Billing execution-evidence bridge owner.
CERTIFICATION / UPDATE DATE: 2026-09-08.
CHANGELOG: v2.0.0-M11-P5-R2D-R1 removes legacy Platform-command reconstruction and bridges only neutral facts plus generic commands.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2.
SECURITY / PRIVACY POSTURE: Opaque references only; no credentials, provider payloads, or caller-selected providers.
TENANT BOUNDARY: Fact, command, and projected truth reads are exact tenant-scoped lookups.
AUTHORITY BOUNDARY: Consumes canonical generic command and neutral execution fact; no command issuance.
FINANCIAL AUTHORITY BOUNDARY: No provider call, attempt mutation, settlement, paid state, or receivable projection.
TRANSACTION BOUNDARY: Caller-owned active session is forwarded to every read and write.
FAIL-CLOSED DECLARATION: Missing, non-executed, mixed-family, divergent, and legacy authority rejects.
"""
from __future__ import annotations

from pymongo.client_session import ClientSession
from pymongo.collection import Collection

from ..domain.financial_execution import FinancialExecutionFact, FinancialExecutionStatus
from ..domain.financial_execution_command import FinancialExecutionCommand, FinancialExecutionCommandFamily, PlatformBillingCommandSource
from ..domain.platform_billing_financial_execution_truth import PlatformBillingFinancialExecutionTruth
from ..registry.financial_execution_registry import FinancialExecutionFactRegistry
from ..registry.financial_execution_command_registry import FinancialExecutionCommandRegistry
from ..registry.platform_billing_financial_execution_truth_registry import PlatformBillingFinancialExecutionTruthRegistry

VERSION = "v2.0.0-M11-P5-R2D-R1"


class PlatformBillingExecutionTruthBridgeError(RuntimeError):
    """Fail-closed platform correlation error."""


def bridge_financial_execution_fact_to_platform(
    tenant_id: str,
    execution_fact_id: str,
    *,
    fact_collection: Collection,
    command_collection: Collection,
    platform_truth_collection: Collection,
    session: ClientSession,
) -> PlatformBillingFinancialExecutionTruth:
    """Persist Platform truth from one neutral fact and one generic Platform command."""
    if session is None or getattr(session, "in_transaction", False) is not True:
        raise PlatformBillingExecutionTruthBridgeError("M11E2D3_ACTIVE_SESSION_REQUIRED")
    fact = FinancialExecutionFactRegistry.get(tenant_id, execution_fact_id, fact_collection, session=session)
    if not isinstance(fact, FinancialExecutionFact) or fact.execution_status is not FinancialExecutionStatus.EXECUTED:
        raise PlatformBillingExecutionTruthBridgeError("EXECUTION_FACT_NOT_EXECUTED")
    command = FinancialExecutionCommandRegistry.get(tenant_id, fact.execution_command_id, command_collection, session=session)
    if not isinstance(command, FinancialExecutionCommand) or command.source_authority_kind is not FinancialExecutionCommandFamily.PLATFORM_BILLING or type(command.source_authority) is not PlatformBillingCommandSource:
        raise PlatformBillingExecutionTruthBridgeError("PLATFORM_COMMAND_REQUIRED")
    if fact.tenant_id != tenant_id or fact.execution_command_id != command.execution_command_id or fact.execution_command_fingerprint != command.fingerprint or fact.provider != command.provider_name or fact.executed_amount_minor != command.amount_minor or fact.currency != command.currency or fact.payment_destination_reference != command.payment_destination_reference:
        raise PlatformBillingExecutionTruthBridgeError("FACT_COMMAND_CORRELATION_MISMATCH")
    try:
        truth = PlatformBillingFinancialExecutionTruth.from_execution_fact(fact, command)
        return PlatformBillingFinancialExecutionTruthRegistry.create(truth, platform_truth_collection, session=session)
    except PlatformBillingExecutionTruthBridgeError:
        raise
    except Exception as error:
        raise PlatformBillingExecutionTruthBridgeError("PLATFORM_EXECUTION_TRUTH_PERSISTENCE_FAILED") from error


# ARTIFACT: platform_billing_execution_truth_bridge.py
# VERSION: v2.0.0-M11-P5-R2D-R1
# AUTHORITY BOUNDARY: neutral-fact to Platform-evidence projection only; no execution or settlement.
# TENANT POSTURE: all source reads and persistence are tenant-scoped.
# FAIL-CLOSED POSTURE: legacy command adaptation and provider selection are absent.
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively.
# END OF WILSY OS SOVEREIGN ARTIFACT
