"""WILSY OS M10B1 registry certificate.
TITLE: Financial Movement Execution Registry Unit Certificate
VERSION: v1.0.0-M10B1
AUTHORITY: Wilsy OS Core Governance
EPITOME: Certify durable tenant/direction-scoped replay.
ABSOLUTE CANONICAL PATH: tests/unit/test_financial_movement_execution_registry.py
COLLABORATION / OWNERSHIP: Kennel EOS registry certification owner.
CERTIFICATION / UPDATE DATE: 2026-09-06
CHANGELOG: v1.0.0-M10B1 certifies explicit collection/session persistence.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2.
SECURITY / PRIVACY POSTURE: Deterministic in-memory persistence double.
TENANT BOUNDARY: Every lookup includes tenant and authority subject.
AUTHORITY BOUNDARY: Persistence evidence only.
FINANCIAL AUTHORITY BOUNDARY: No settlement or paid state.
TRANSACTION BOUNDARY: Caller session forwarded; registry starts none.
FAIL-CLOSED DECLARATION: Corruption and divergent replay reject.
"""
import pytest
from dataclasses import replace
from tools.eos.kennel.domain.financial_execution import FinancialExecutionStatus
from tools.eos.kennel.domain.financial_movement_execution import FinancialMovementDirection
from tools.eos.kennel.registry.financial_movement_execution_registry import FinancialMovementExecutionRegistry, FinancialMovementExecutionRegistryError
from tools.eos.kennel.domain.financial_movement_execution import FinancialMovementExecutionTruth
from datetime import datetime, timezone

class Collection:
    def __init__(self): self.rows=[]; self.inserts=0; self.sessions=[]; self.indexes=[]
    def create_index(self, spec, unique=False): self.indexes.append((spec, unique))
    def find_one(self, query, session=None):
        self.sessions.append(session)
        return next((r.copy() for r in self.rows if all(r.get(k)==v for k,v in query.items())), None)
    def insert_one(self, row, session=None): self.sessions.append(session); self.rows.append(row.copy()); self.inserts += 1
class Session: pass

def truth(direction=FinancialMovementDirection.COLLECTION, tenant="t"):
    n=datetime.now(timezone.utc)
    return FinancialMovementExecutionTruth("id-"+direction.value,tenant,"auth","invoice","inv",direction,"p","ref",FinancialExecutionStatus.EXECUTED,1,"ZAR",n,"instrument","ev","a"*128,"b"*128,n)

def test_r01_indexes_and_r02_r03_create_hydrate():
    c=Collection(); FinancialMovementExecutionRegistry.ensure_indexes(c); assert len(c.indexes)==2
    t=truth(); assert FinancialMovementExecutionRegistry.create(t,"k",c) == t
    assert FinancialMovementExecutionRegistry.get_by_idempotency_key("t","invoice","inv",t.direction,"k",c) == t

def test_r04_to_r10_isolation_replay_and_conflict():
    c=Collection(); t=truth(); first=FinancialMovementExecutionRegistry.create(t,"k",c)
    assert FinancialMovementExecutionRegistry.get_by_idempotency_key("other","invoice","inv",t.direction,"k",c) is None
    assert FinancialMovementExecutionRegistry.get_by_idempotency_key("t","other","inv",t.direction,"k",c) is None
    assert FinancialMovementExecutionRegistry.get_by_idempotency_key("t","invoice","inv",FinancialMovementDirection.DISBURSEMENT,"k",c) is None
    assert FinancialMovementExecutionRegistry.create(t,"k",c) == first and c.inserts == 1
    divergent=replace(t, execution_truth_id="different")
    with pytest.raises(FinancialMovementExecutionRegistryError): FinancialMovementExecutionRegistry.create(divergent,"k",c)

def test_r11_corruption_fails_closed_and_r12_r18_session_is_forwarded():
    c=Collection(); t=truth(); FinancialMovementExecutionRegistry.create(t,"k",c); c.rows[0]["execution_status"]="CORRUPT"
    with pytest.raises(Exception): FinancialMovementExecutionRegistry.get_by_idempotency_key("t","invoice","inv",t.direction,"k",c)
    c=Collection(); s=Session(); FinancialMovementExecutionRegistry.create(t,"k",c,session=s); assert c.sessions and all(x is s for x in c.sessions)

def test_r11_truth_corruption_rejection():
    c=Collection(); t=truth(); FinancialMovementExecutionRegistry.create(t,"k",c); c.rows[0]["executed_amount_minor"]=0
    with pytest.raises(Exception): FinancialMovementExecutionRegistry.get_by_idempotency_key("t","invoice","inv",t.direction,"k",c)

def test_r19_mongo_id_is_transport_metadata_only():
    c=Collection(); original=truth(); FinancialMovementExecutionRegistry.create(original,"k",c)
    c.rows[0]["_id"]="mongo-id"
    hydrated=FinancialMovementExecutionRegistry.get_by_idempotency_key("t","invoice","inv",original.direction,"k",c)
    assert hydrated is not None
    assert hydrated == original
    assert hydrated.to_dict() == original.to_dict()
    assert "_id" not in hydrated.to_dict()
    assert c.rows[0]["_id"] == "mongo-id"

def test_r20_unknown_persisted_field_fails_closed():
    c=Collection(); original=truth(); FinancialMovementExecutionRegistry.create(original,"k",c)
    c.rows[0]["unknown"]="reject"
    with pytest.raises(Exception):
        FinancialMovementExecutionRegistry.get_by_idempotency_key("t","invoice","inv",original.direction,"k",c)

# ARTIFACT: test_financial_movement_execution_registry.py
# VERSION: v1.1.0-M10B1
# AUTHORITY BOUNDARY: Unit persistence evidence only.
# TENANT POSTURE: Synthetic tenant isolation.
# FAIL-CLOSED POSTURE: Replay and corruption are rejected.
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively.
# END OF WILSY OS SOVEREIGN ARTIFACT
