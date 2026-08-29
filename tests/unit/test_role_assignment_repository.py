"""TITLE: WILSY OS Role Assignment Repository Unit Contract Tests.
VERSION: v1.0.0-WILSY-ROLE-ASSIGNMENT-UNIT-CONTRACT
AUTHORITY: Deterministic unit-level contract verification for role-assignment repository mechanics only.
EPITOME: Supplements real-Mongo certification with fast deterministic proofs of repository round-trip, revision CAS, absence, and stale-write behavior.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tests/unit/test_role_assignment_repository.py
COLLABORATION / OWNERSHIP: Wilson Khanyezi / Wilsy Core Engineering.
CERTIFICATION/UPDATE DATE: 2026-08-29.
CHANGELOG: v1.0.0-WILSY-ROLE-ASSIGNMENT-UNIT-CONTRACT — sovereign hardening of deterministic repository unit-contract coverage; runtime authority semantics unchanged.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2; ISO 27001.
SECURITY/PRIVACY POSTURE: Deterministic synthetic opaque identifiers only; no credentials, profile data, production tenants, or production persistence.
TENANT BOUNDARY: Unit fixtures use explicit tenant identifiers and never infer or default tenant context.
AUTHORITY BOUNDARY: Unit-contract support only; not operational certification and no ownership of role definitions, permissions, authentication, authorization, principal lifecycle, tenant membership, or financial execution.
FINANCIAL AUTHORITY BOUNDARY: None. Kennel EOS exclusively owns financial execution.
"""
from __future__ import annotations
from typing import cast
from pymongo.collection import Collection
from tools.eos.auth.role_assignment import RoleAssignmentAuthority, RoleAssignmentStatus
from tools.eos.auth.role_assignment_repository import *

VERSION = "v1.0.0-WILSY-ROLE-ASSIGNMENT-UNIT-CONTRACT"

class Result:
    """Minimal deterministic result carrying Mongo matched-count semantics."""
    matched_count = 1

class Fake:
    """In-memory collection double modeling repository mechanics only."""
    def __init__(self): self.rows=[]; self.calls=[]
    def create_index(self,*a,**k): self.calls.append((a,k))
    def insert_one(self,d,**k):
        if any(all(r[x]==d[x] for x in ('principal_id','tenant_id','role_id')) for r in self.rows): raise Exception
        self.rows.append(d)
    def find_one(self,q,**k): return next((r for r in self.rows if all(r[x]==v for x,v in q.items())),None)
    def replace_one(self,q,d,**k):
        for i,r in enumerate(self.rows):
            if all(r[x]==v for x,v in q.items()): self.rows[i]=d; return Result()
        return type('R',(),{'matched_count':0})()

def value(rev=0,status=RoleAssignmentStatus.ACTIVE):
    """Build an explicit synthetic tenant-scoped assignment value."""
    return RoleAssignmentAuthority('p','t','r',status,rev)

def test_roundtrip_and_cas():
    """Prove deterministic round-trip and exact revision CAS mechanics."""
    c=cast(Collection,Fake()); RoleAssignmentRepository.ensure_indexes(c); RoleAssignmentRepository.insert(value(),c); assert RoleAssignmentRepository.resolve('p','t','r',c)==value(); RoleAssignmentRepository.compare_and_swap(value(1,RoleAssignmentStatus.REVOKED),0,c); assert RoleAssignmentRepository.resolve('p','t','r',c).status is RoleAssignmentStatus.REVOKED

def test_absence_and_stale():
    """Prove absence and stale revisions fail closed without synthetic authority."""
    c=cast(Collection,Fake())
    try: RoleAssignmentRepository.resolve('p','t','r',c); assert False
    except RoleAssignmentNotFoundError: pass
    RoleAssignmentRepository.insert(value(),c)
    try: RoleAssignmentRepository.compare_and_swap(value(2),0,c); assert False
    except RoleAssignmentRevisionConflictError: pass

# ARTIFACT: test_role_assignment_repository.py
# VERSION: v1.0.0-WILSY-ROLE-ASSIGNMENT-UNIT-CONTRACT
# AUTHORITY BOUNDARY: deterministic unit-level repository contract support only; not operational certification
# TENANT POSTURE: explicit synthetic tenant identifiers only; no tenant inference or defaulting
# FAIL-CLOSED POSTURE: absence and stale revision never become successful authority
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS remains exclusive
# END OF WILSY OS SOVEREIGN ARTIFACT
