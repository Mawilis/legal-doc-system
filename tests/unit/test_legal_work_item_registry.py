"""TITLE: WILSY OS Legal Work Item Registry Unit Certificate.

VERSION: v1.0.0-G7G-P0D-WORK-ITEM-REGISTRY-UNIT-CERT
AUTHORITY: Wilsy OS Core Governance / Python EOS Legal Operations
EPITOME: Certify immutable tenant-first persistence, strict hydration, replay,
         transaction ownership, lineage/currentness, and authority exclusions.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tests/unit/test_legal_work_item_registry.py
COLLABORATION / OWNERSHIP: Direct certificate for the corresponding P0 registry.
CERTIFICATION / UPDATE DATE: 2026-10-15
CHANGELOG: v1.0.0-G7G-P0D-WORK-ITEM-REGISTRY-UNIT-CERT establishes the first bounded unit certificate.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2.
TENANT BOUNDARY: Exact tenant isolation and foreign-tenant non-disclosure tested.
AUTHORITY BOUNDARY: Tests grant no IAM, assignment, supervision, or execution power.
FINANCIAL AUTHORITY BOUNDARY: Kennel EOS exclusively.
"""
from types import SimpleNamespace
import pytest
from pymongo.errors import DuplicateKeyError

from tests.unit.test_legal_work_item import item
from tools.eos.legal_operations.registry.legal_work_item_registry import (
    LegalWorkItemRegistry,
    LegalWorkItemRegistryConflictError,
    LegalWorkItemRegistryNotFoundError,
    LegalWorkItemRegistryPersistedRecordInvalidError,
    LegalWorkItemRegistryRetryTransactionError,
    LegalWorkItemRegistryTransactionRequiredError,
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
                key=lambda row: (
                    row.get(key) is None,
                    row.get(key),
                ),
                reverse=direction < 0,
            )
        return Cursor(values)

class Collection:
    def __init__(self):
        self.rows=[]; self.indexes=[]; self.duplicate=False
    def create_index(self, keys, **options):
        self.indexes.append((tuple(keys),options))
    def find_one(self, query, *, session):
        return next((dict(row) for row in self.rows if all(row.get(k)==v for k,v in query.items())),None)
    def find(self, query, *, session):
        return Cursor([dict(row) for row in self.rows if all(row.get(k)==v for k,v in query.items())])
    def insert_one(self, document, *, session):
        if self.duplicate: raise DuplicateKeyError("race")
        self.rows.append(dict(document)); return SimpleNamespace(inserted_id="id")

ACTIVE=SimpleNamespace(in_transaction=True)

def setup():
    collection=Collection()
    return LegalWorkItemRegistry(collection),collection

def test_indexes_are_tenant_first_and_have_no_ttl():
    registry,collection=setup(); registry.ensure_indexes()
    assert len(collection.indexes)==5
    assert all(keys[0]==("tenant_id",1) for keys,_ in collection.indexes)
    assert all("expireAfterSeconds" not in options for _,options in collection.indexes)

def test_active_transaction_required():
    registry,_=setup()
    with pytest.raises(LegalWorkItemRegistryTransactionRequiredError):
        registry.create_or_replay(item(),session=None)

def test_create_and_exact_replay():
    registry,collection=setup(); value=item()
    assert registry.create_or_replay(value,session=ACTIVE)==value
    assert registry.create_or_replay(value,session=ACTIVE)==value
    assert len(collection.rows)==1

def test_divergent_replay_rejects():
    registry,_=setup(); registry.create_or_replay(item(),session=ACTIVE)
    with pytest.raises(LegalWorkItemRegistryConflictError):
        registry.create_or_replay(item(title="Different"),session=ACTIVE)

def test_exact_tenant_matter_and_status_queries():
    registry,collection=setup()
    a=item(); b=item(work_item_id="work-2",case_matter_id="matter-2")
    foreign=item(work_item_id="work-3",tenant_id="tenant-2")
    collection.rows.extend([a.to_dict(),b.to_dict(),foreign.to_dict()])
    assert registry.list_matter("tenant-1","matter-1",session=ACTIVE)==(a,)
    assert registry.list_status("tenant-1","OPEN",session=ACTIVE)==(a,b)

def test_foreign_tenant_is_absent():
    registry,collection=setup(); collection.rows.append(item(tenant_id="tenant-2").to_dict())
    with pytest.raises(LegalWorkItemRegistryNotFoundError):
        registry.get_by_id("tenant-1","work-1",session=ACTIVE)

def test_persisted_corruption_rejects():
    registry,collection=setup(); collection.rows.append({**item().to_dict(),"fingerprint":"0"*128})
    with pytest.raises(LegalWorkItemRegistryPersistedRecordInvalidError):
        registry.get_by_id("tenant-1","work-1",session=ACTIVE)

def test_duplicate_race_requires_whole_transaction_retry():
    registry,collection=setup(); collection.duplicate=True
    with pytest.raises(LegalWorkItemRegistryRetryTransactionError):
        registry.create_or_replay(item(),session=ACTIVE)
# ARTIFACT: test_legal_work_item_registry.py
# VERSION: v1.0.0-G7G-P0D-WORK-ITEM-REGISTRY-UNIT-CERT
# AUTHORITY BOUNDARY: verification only; no runtime authority
# TENANT POSTURE: exact tenant-isolation assertions
# FAIL-CLOSED POSTURE: negative and corruption cases required
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively
# END OF WILSY OS SOVEREIGN ARTIFACT
