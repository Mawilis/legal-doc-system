"""WILSY OS M10B1 direction-aware provider orchestration.
TITLE: Financial Movement Execution Orchestrator
VERSION: v1.0.0-M10B1
AUTHORITY: Wilsy OS Core Governance
PURPOSE: Execute validated movement commands exactly once through an injected provider.
EPITOME: Kennel-owned provider execution with preflight replay and transaction firewall.
ABSOLUTE CANONICAL PATH: tools/eos/kennel/orchestration/financial_movement_execution_orchestrator.py
COLLABORATION / OWNERSHIP: Kennel EOS orchestration owner.
CERTIFICATION / UPDATE DATE: 2026-09-06
CHANGELOG: v1.0.0-M10B1 establishes directional provider SPI and replay sequencing.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2.
SECURITY / PRIVACY POSTURE: Opaque references; provider injected.
TENANT BOUNDARY: Commands and truths are tenant-scoped.
AUTHORITY BOUNDARY: Kennel owns execution; caller cannot inject truth.
FINANCIAL AUTHORITY BOUNDARY: Execution never implies settlement or paid state.
TRANSACTION BOUNDARY: Caller session is never committed or aborted.
FAIL-CLOSED DECLARATION: Active transactions, replay divergence, and bad provider results reject.
"""
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Protocol
from pymongo.client_session import ClientSession
from ..domain.financial_execution import FinancialExecutionStatus
from ..domain.financial_movement_execution import FinancialMovementExecutionCommand, FinancialMovementExecutionTruth
from ..registry.financial_movement_execution_registry import FinancialMovementExecutionRegistry
@dataclass(frozen=True)
class FinancialMovementProviderResult:
 provider:str; provider_execution_reference:str; execution_status:FinancialExecutionStatus; provider_evidence_reference:str; executed_at:datetime|None
class FinancialMovementProvider(Protocol):
 def execute(self,command:FinancialMovementExecutionCommand)->FinancialMovementProviderResult: ...
@dataclass(frozen=True)
class FinancialMovementResult:
 provider_invoked:bool; execution_truth:FinancialMovementExecutionTruth
class FinancialMovementExecutionOrchestrator:
 def __init__(self,provider:FinancialMovementProvider): self.provider=provider
 def execute(self,command,collection,*,session:ClientSession|None=None):
  existing=FinancialMovementExecutionRegistry.get_by_idempotency_key(command.tenant_id,command.authority_subject_kind,command.authority_subject_id,command.direction,command.idempotency_key,collection,session=session)
  if existing is not None:
   if existing.execution_command_fingerprint != command.fingerprint: raise RuntimeError('M10B_REPLAY_CONFLICT')
   return FinancialMovementResult(False,existing)
  if session is not None and session.in_transaction: raise RuntimeError('M10B_PROVIDER_ACTIVE_TRANSACTION')
  result=self.provider.execute(command)
  if not isinstance(result,FinancialMovementProviderResult) or result.execution_status not in (FinancialExecutionStatus.EXECUTED,FinancialExecutionStatus.FAILED): raise RuntimeError('M10B_PROVIDER_RESULT_INVALID')
  if command.requested_provider is not None and result.provider != command.requested_provider: raise RuntimeError('M10B_PROVIDER_MISMATCH')
  truth=FinancialMovementExecutionTruth(command.execution_command_id,command.tenant_id,command.execution_authorization_id,command.authority_subject_kind,command.authority_subject_id,command.direction,result.provider,result.provider_execution_reference,result.execution_status,command.amount_minor,command.currency,result.executed_at,command.payment_instrument_reference,result.provider_evidence_reference,command.fingerprint,command.fingerprint,datetime.now(timezone.utc))
  return FinancialMovementResult(True,FinancialMovementExecutionRegistry.create(truth,command.idempotency_key,collection,session=session))
# ARTIFACT: financial_movement_execution_orchestrator.py
# VERSION: v1.0.0-M10B1
# AUTHORITY BOUNDARY: Kennel EOS provider execution.
# FAIL-CLOSED POSTURE: Provider and replay failures reject.
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively.
# END OF WILSY OS SOVEREIGN ARTIFACT
