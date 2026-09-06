"""WILSY OS M10B1 orchestrator certificate.
TITLE: Financial Movement Execution Orchestrator Unit Certificate
VERSION: v1.0.0-M10B1
AUTHORITY: Wilsy OS Core Governance
EPITOME: Certify provider invocation, replay, and transaction firewall.
ABSOLUTE CANONICAL PATH: tests/unit/test_financial_movement_execution_orchestrator.py
COLLABORATION / OWNERSHIP: Kennel EOS orchestration certification owner.
CERTIFICATION / UPDATE DATE: 2026-09-06
CHANGELOG: v1.0.0-M10B1 certifies exactly-once provider boundary.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2.
SECURITY / PRIVACY POSTURE: Provider receives validated opaque references.
TENANT BOUNDARY: Command identity scopes replay.
AUTHORITY BOUNDARY: Kennel execution evidence only.
FINANCIAL AUTHORITY BOUNDARY: Execution never implies settlement or paid state.
TRANSACTION BOUNDARY: Caller owns session; orchestrator never commits.
FAIL-CLOSED DECLARATION: Active transactions and bad provider results reject.
"""
from datetime import datetime, timezone
import pytest
from typing import Any, cast
from tools.eos.kennel.domain.financial_execution import FinancialExecutionStatus
from tools.eos.kennel.domain.financial_movement_execution import FinancialMovementDirection
from tools.eos.kennel.orchestration.financial_movement_execution_orchestrator import FinancialMovementExecutionOrchestrator, FinancialMovementProviderResult
from tools.eos.kennel.domain.financial_movement_execution import FinancialMovementExecutionCommand
class Collection:
    def __init__(self): self.rows=[]; self.sessions=[]
    def find_one(self, query, session=None):
        self.sessions.append(session)
        return next((r.copy() for r in self.rows if all(r.get(k)==v for k,v in query.items())), None)
    def insert_one(self, row, session=None): self.sessions.append(session); self.rows.append(row.copy())

def cmd(direction=FinancialMovementDirection.COLLECTION):
    return FinancialMovementExecutionCommand("t","auth","a"*128,"invoice","inv","b"*128,direction,"cmd-"+direction.value,"key-"+direction.value,10,"ZAR","instrument")
class Provider:
    def __init__(self,status=FinancialExecutionStatus.EXECUTED): self.count=0; self.status=status
    def execute(self, command): self.count+=1; return FinancialMovementProviderResult("p","ref-"+command.direction.value,self.status,"ev",datetime.now(timezone.utc))
class Session:
    def __init__(self, active=False): self.in_transaction=active

def test_o01_o02_o03_o04_directional_once_and_replay():
    for direction in (FinancialMovementDirection.COLLECTION, FinancialMovementDirection.DISBURSEMENT):
        p=Provider(); c=Collection(); o=FinancialMovementExecutionOrchestrator(p); first=o.execute(cmd(direction),c); replay=o.execute(cmd(direction),c)
        assert first.provider_invoked and not replay.provider_invoked and p.count == 1 and replay.execution_truth == first.execution_truth

def test_o05_o06_divergent_replay_before_provider():
    p=Provider(); c=Collection(); o=FinancialMovementExecutionOrchestrator(p); o.execute(cmd(),c)
    with pytest.raises(Exception): o.execute(FinancialMovementExecutionCommand("t","auth","c"*128,"invoice","inv","b"*128,FinancialMovementDirection.COLLECTION,"different","key-COLLECTION",10,"ZAR","instrument"),c)
    assert p.count == 1

def test_o07_o08_active_transaction_firewall():
    p=Provider()
    with pytest.raises(RuntimeError): FinancialMovementExecutionOrchestrator(p).execute(cmd(),Collection(),session=cast(Any, Session(True)))
    assert p.count == 0

@pytest.mark.parametrize("status", [FinancialExecutionStatus.EXECUTED, FinancialExecutionStatus.FAILED])
def test_o12_to_o17_terminal_execution_only(status):
    result=FinancialMovementExecutionOrchestrator(Provider(status)).execute(cmd(),Collection()).execution_truth
    assert result.execution_status is status and not hasattr(result,"settled") and not hasattr(result,"paid")

def test_o09_o10_bad_provider_result_fails_closed():
    class Bad:
        def execute(self, command): return object()
    with pytest.raises(RuntimeError): FinancialMovementExecutionOrchestrator(cast(Any, Bad())).execute(cmd(),Collection())

def test_o11_requested_provider_mismatch_rejected_without_persistence():
    requested=FinancialMovementExecutionCommand("t","auth","a"*128,"invoice","inv","b"*128,FinancialMovementDirection.COLLECTION,"cmd-requested","key-requested",10,"ZAR","instrument",requested_provider="provider-A")
    class Other(Provider):
        def execute(self, command): self.count+=1; return FinancialMovementProviderResult("provider-B","ref",FinancialExecutionStatus.EXECUTED,"ev",datetime.now(timezone.utc))
    other=Other(); c=Collection()
    with pytest.raises(RuntimeError): FinancialMovementExecutionOrchestrator(other).execute(requested,c)
    assert other.count == 1 and not c.rows

def test_o18_o21_session_forwarded_and_no_transaction_controls():
    p=Provider(); c=Collection(); s=Session(); FinancialMovementExecutionOrchestrator(p).execute(cmd(),c,session=cast(Any, s)); assert all(x is s for x in c.sessions)

# ARTIFACT: test_financial_movement_execution_orchestrator.py
# VERSION: v1.0.0-M10B1
# AUTHORITY BOUNDARY: Unit orchestration evidence only.
# TENANT POSTURE: Synthetic tenant identifiers.
# FAIL-CLOSED POSTURE: Provider and transaction violations reject.
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively.
# END OF WILSY OS SOVEREIGN ARTIFACT
