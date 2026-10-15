"""TITLE: WILSY OS Legal Matter Workflow Transition Registry Unit Certificate.

VERSION: v1.0.0-G7G-P0B-TRANSITION-REGISTRY-UNIT-CERT
AUTHORITY: Wilsy OS Core Governance / Python EOS Legal Operations
EPITOME: Certify immutable tenant-first persistence, strict hydration, replay,
         transaction ownership, lineage/currentness, and authority exclusions.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tests/unit/test_legal_matter_workflow_transition_registry.py
COLLABORATION / OWNERSHIP: Direct certificate for the corresponding P0 registry.
CERTIFICATION / UPDATE DATE: 2026-10-15
CHANGELOG: v1.0.0-G7G-P0B-TRANSITION-REGISTRY-UNIT-CERT establishes the first bounded unit certificate.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2.
TENANT BOUNDARY: Exact tenant isolation and foreign-tenant non-disclosure tested.
AUTHORITY BOUNDARY: Tests grant no IAM, assignment, supervision, or execution power.
FINANCIAL AUTHORITY BOUNDARY: Kennel EOS exclusively.
"""
from types import SimpleNamespace
import pytest
from pymongo.errors import DuplicateKeyError
from tests.unit.test_legal_matter_workflow_transition import context, transition
from tools.eos.legal_operations.domain.legal_matter_workflow_transition import LegalMatterWorkflowTransition
from tools.eos.legal_operations.registry.legal_matter_workflow_transition_registry import (
    LegalMatterWorkflowTransitionRegistry,
    LegalMatterWorkflowTransitionRegistryConflictError,
    LegalMatterWorkflowTransitionRegistryPersistedRecordInvalidError,
    LegalMatterWorkflowTransitionRegistryRetryTransactionError,
    LegalMatterWorkflowTransitionRegistryTransactionRequiredError,
)

class Cursor:
    def __init__(self, values):
        self._values = list(values)

    def __iter__(self):
        return iter(self._values)

    def __len__(self):
        return len(self._values)

    def __getitem__(self, index):
        return self._values[index]

    def sort(self, keys):
        values = list(self._values)
        for key, direction in reversed(keys):
            values.sort(
                key=lambda row: row[key],
                reverse=direction < 0,
            )
        return Cursor(values)
class Collection:
    def __init__(self): self.rows=[]; self.indexes=[]; self.duplicate=False
    def create_index(self,keys,**options): self.indexes.append((tuple(keys),options))
    def find_one(self,query,*,session): return next((dict(r) for r in self.rows if all(r.get(k)==v for k,v in query.items())),None)
    def find(self,query,*,session): return Cursor([dict(r) for r in self.rows if all(r.get(k)==v for k,v in query.items())])
    def insert_one(self,doc,*,session):
        if self.duplicate: raise DuplicateKeyError("race")
        self.rows.append(dict(doc)); return SimpleNamespace(inserted_id="id")
ACTIVE=SimpleNamespace(in_transaction=True)

def second(first):
    data=first.to_dict()
    data.update({
        "transition_id":"transition-2",
        "sequence_number":2,
        "previous_transition_fingerprint":first.fingerprint,
        "source_stage_definition_id":first.target_stage_definition_id,
        "source_stage_fingerprint":first.target_stage_fingerprint,
        "target_stage_definition_id":"stage-3",
        "target_stage_fingerprint":"d"*128,
        "transitioned_at":first.transitioned_at.replace(minute=first.transitioned_at.minute+1).isoformat(),
        "fingerprint":"",
    })
    return LegalMatterWorkflowTransition.from_dict(data)

def setup():
    c=Collection(); return LegalMatterWorkflowTransitionRegistry(c),c

def test_indexes_are_tenant_first_unique_and_non_ttl():
    r,c=setup(); r.ensure_indexes()
    assert len(c.indexes)==4
    assert all(keys[0]==("tenant_id",1) for keys,_ in c.indexes)
    assert all("expireAfterSeconds" not in options for _,options in c.indexes)

def test_active_transaction_required():
    r,_=setup()
    with pytest.raises(LegalMatterWorkflowTransitionRegistryTransactionRequiredError):
        r.create_or_replay(transition(),session=None)

def test_create_replay_and_complete_history():
    r,_=setup(); first=transition(); follow=second(first)
    assert r.create_or_replay(first,session=ACTIVE)==first
    assert r.create_or_replay(first,session=ACTIVE)==first
    assert r.create_or_replay(follow,session=ACTIVE)==follow
    assert r.list_history(first.tenant_id,first.workflow_instance_id,session=ACTIVE)==(first,follow)

def test_gap_or_wrong_predecessor_rejects():
    r,_=setup(); first=transition(); r.create_or_replay(first,session=ACTIVE)
    data=second(first).to_dict(); data.update({"sequence_number":3,"fingerprint":""})
    with pytest.raises(LegalMatterWorkflowTransitionRegistryConflictError):
        r.create_or_replay(LegalMatterWorkflowTransition.from_dict(data),session=ACTIVE)

def test_divergent_replay_rejects():
    r,_=setup(); first=transition(); r.create_or_replay(first,session=ACTIVE)
    data=first.to_dict(); data.update({"transition_authorization_evidence_reference":"other","fingerprint":""})
    with pytest.raises(LegalMatterWorkflowTransitionRegistryConflictError):
        r.create_or_replay(LegalMatterWorkflowTransition.from_dict(data),session=ACTIVE)

def test_currentness_is_derived_from_instance_and_complete_history():
    r,c=setup(); first=transition(); follow=second(first); c.rows.extend([first.to_dict(),follow.to_dict()])
    instance,*_=context()
    current=r.derive_currentness("current-1",instance,session=ACTIVE)
    assert current.transition_count==2
    assert current.current_stage_definition_id=="stage-3"
    assert current.head_transition_id=="transition-2"

def test_persisted_corruption_rejects():
    r,c=setup(); first=transition(); c.rows.append({**first.to_dict(),"fingerprint":"0"*128})
    with pytest.raises(LegalMatterWorkflowTransitionRegistryPersistedRecordInvalidError):
        r.list_history(first.tenant_id,first.workflow_instance_id,session=ACTIVE)

def test_duplicate_race_requires_whole_transaction_retry():
    r,c=setup(); c.duplicate=True
    with pytest.raises(LegalMatterWorkflowTransitionRegistryRetryTransactionError):
        r.create_or_replay(transition(),session=ACTIVE)
# ARTIFACT: test_legal_matter_workflow_transition_registry.py
# VERSION: v1.0.0-G7G-P0B-TRANSITION-REGISTRY-UNIT-CERT
# AUTHORITY BOUNDARY: verification only; no runtime authority
# TENANT POSTURE: exact tenant-isolation assertions
# FAIL-CLOSED POSTURE: negative and corruption cases required
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively
# END OF WILSY OS SOVEREIGN ARTIFACT
