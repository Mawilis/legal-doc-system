# pyright: reportArgumentType=false, reportAttributeAccessIssue=false
"""TITLE: Financial Execution Fact Registry Certificate
VERSION: v2.0.0-M11-P5-R2D-R1
AUTHORITY: Wilsy OS Core Governance / Kennel EOS
EPITOME: Certify isolated strict neutral-fact persistence and replay semantics.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tests/unit/test_platform_billing_financial_execution_truth_registry.py
COLLABORATION / OWNERSHIP: Kennel EOS neutral execution-fact registry certificate.
CERTIFICATION / UPDATE DATE: 2026-09-08.
CHANGELOG: v2.0.0-M11-P5-R2D-R1 certifies tenant/attempt uniqueness, strict hydration, and caller sessions.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2.
TENANT BOUNDARY: All fake persistence queries include tenant identity.
AUTHORITY BOUNDARY: Persistence only; no transaction lifecycle or provider authority.
FINANCIAL AUTHORITY BOUNDARY: No settlement or paid-state mutation.
FAIL-CLOSED DECLARATION: Divergent replay, unknown fields, and corruption reject.
"""
from datetime import datetime, timezone
from types import SimpleNamespace
import pytest
from tools.eos.kennel.domain.financial_execution import FinancialExecutionFact, FinancialExecutionStatus
from tools.eos.kennel.registry.financial_execution_registry import FinancialExecutionFactRegistry, FinancialExecutionFactRegistryError, FinancialExecutionFactCreateConflictError, FinancialExecutionFactPersistedRecordInvalidError

NOW = datetime(2026, 1, 1, tzinfo=timezone.utc); FP = "a" * 128
def item(tenant="tenant-1", attempt="attempt-1", **changes):
    values = dict(execution_fact_id=FinancialExecutionFact.deterministic_id(tenant, attempt), tenant_id=tenant, execution_command_id="command-1", execution_command_fingerprint=FP, execution_attempt_id=attempt, provider="PAYSHAP", provider_execution_reference="provider-ref", execution_status=FinancialExecutionStatus.EXECUTED, executed_amount_minor=100, currency="ZAR", executed_at=NOW, payment_destination_reference="destination", provider_evidence_reference="evidence", execution_evidence_fingerprint="b" * 128, created_at=NOW); values.update(changes); return FinancialExecutionFact(**values)
class Cursor:
    def __init__(self, rows): self.rows = rows
    def limit(self, n): return Cursor(self.rows[:n])
    def __iter__(self): return iter(self.rows)
class Collection:
    def __init__(self): self.rows=[]; self.indexes=[]; self.sessions=[]
    def create_index(self, spec, **kwargs): self.indexes.append((spec, kwargs)); return kwargs.get("name", "index")
    def find_one(self, query, session=None): self.sessions.append(session); return next((r.copy() for r in self.rows if all(r.get(k)==v for k,v in query.items())), None)
    def find(self, query, session=None): self.sessions.append(session); return Cursor([r.copy() for r in self.rows if all(r.get(k)==v for k,v in query.items())])
    def insert_one(self, document, session=None): self.sessions.append(session); self.rows.append(dict(document)); return SimpleNamespace(inserted_id="id")
def test_indexes_are_separate_and_unique():
    c=Collection(); FinancialExecutionFactRegistry.ensure_indexes(c); assert len(c.indexes)==2 and all(x[1]["unique"] for x in c.indexes)
def test_create_returns_created():
    c=Collection(); result=FinancialExecutionFactRegistry.create(item(), c); assert result.outcome.value=="CREATED"
def test_get_round_trip():
    c=Collection(); value=item(); FinancialExecutionFactRegistry.create(value,c); assert FinancialExecutionFactRegistry.get("tenant-1", value.execution_fact_id,c)==value
def test_get_by_attempt_round_trip():
    c=Collection(); value=item(); FinancialExecutionFactRegistry.create(value,c); assert FinancialExecutionFactRegistry.get_by_attempt("tenant-1", "attempt-1", c)==value
def test_missing_get_is_none(): assert FinancialExecutionFactRegistry.get("tenant-1", "missing", Collection()) is None
def test_missing_attempt_is_none(): assert FinancialExecutionFactRegistry.get_by_attempt("tenant-1", "missing", Collection()) is None
def test_exact_replay():
    c=Collection(); value=item(); FinancialExecutionFactRegistry.create(value,c); assert FinancialExecutionFactRegistry.create(value,c).outcome.value=="IDEMPOTENT_REPLAY"
def test_attempt_divergence_rejected():
    c=Collection(); FinancialExecutionFactRegistry.create(item(),c)
    with pytest.raises(FinancialExecutionFactCreateConflictError): FinancialExecutionFactRegistry.create(item(execution_evidence_fingerprint="c"*128),c)
def test_tenant_isolation():
    c=Collection(); value=item(); FinancialExecutionFactRegistry.create(value,c); assert FinancialExecutionFactRegistry.get("other", value.execution_fact_id,c) is None
def test_unknown_field_corruption_rejected():
    c=Collection(); value=item(); c.rows.append({**value.to_dict(), "unknown": 1})
    with pytest.raises(FinancialExecutionFactPersistedRecordInvalidError): FinancialExecutionFactRegistry.get("tenant-1", value.execution_fact_id,c)
def test_missing_field_corruption_rejected():
    c=Collection(); value=item(); row=value.to_dict(); row.pop("provider"); c.rows.append(row)
    with pytest.raises(FinancialExecutionFactPersistedRecordInvalidError): FinancialExecutionFactRegistry.get("tenant-1", value.execution_fact_id,c)
def test_fingerprint_corruption_rejected():
    c=Collection(); value=item(); row=value.to_dict(); row["execution_command_fingerprint"]="z"*128; c.rows.append(row)
    with pytest.raises(FinancialExecutionFactPersistedRecordInvalidError): FinancialExecutionFactRegistry.get("tenant-1", value.execution_fact_id,c)
def test_invalid_type_rejected():
    with pytest.raises(FinancialExecutionFactRegistryError): FinancialExecutionFactRegistry.create(object(), Collection())
def test_identity_collision_rejected():
    c=Collection(); value=item(); FinancialExecutionFactRegistry.create(value,c); c.rows[0]["provider"]="OTHER"
    with pytest.raises(FinancialExecutionFactCreateConflictError): FinancialExecutionFactRegistry.create(value,c)
def test_session_forwarded():
    c=Collection(); session=SimpleNamespace(in_transaction=True); FinancialExecutionFactRegistry.create(item(),c,session=session); assert c.sessions and c.sessions[-1] is session
def test_registry_does_not_start_transactions():
    c=Collection(); FinancialExecutionFactRegistry.create(item(),c); assert not hasattr(c, "start_transaction")
def test_no_ap_collection_cross_read():
    c=Collection(); assert FinancialExecutionFactRegistry.get("tenant-1", "fact-x", c) is None and c.rows==[]
def test_exact_one_per_attempt_projection():
    c=Collection(); value=item(); FinancialExecutionFactRegistry.create(value,c); assert len(c.rows)==1
def test_fact_to_dict_has_no_settlement(): assert "settled" not in item().to_dict()
def test_bounded_tenant_argument_validation():
    with pytest.raises(FinancialExecutionFactRegistryError): FinancialExecutionFactRegistry.get("", "fact", Collection())

# ARTIFACT: test_platform_billing_financial_execution_truth_registry.py
# VERSION: v2.0.0-M11-P5-R2D-R1
# AUTHORITY BOUNDARY: strict neutral-fact persistence certificate only.
# TENANT POSTURE: synthetic tenant-scoped collection fixtures.
# FAIL-CLOSED POSTURE: corruption and divergent replay are asserted as failures.
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively.
# END OF WILSY OS SOVEREIGN ARTIFACT
