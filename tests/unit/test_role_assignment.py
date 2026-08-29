"""Unit certification for role assignment authority boundaries."""
from dataclasses import fields
from inspect import signature
from typing import cast
import pytest
from tools.eos.auth.role_assignment import RoleAssignmentAuthority, RoleAssignmentStatus

def assignment(**changes):
    v=dict(principal_id="p",tenant_id="t",role_id="role-a",status=RoleAssignmentStatus.ACTIVE,revision=0); v.update(changes)
    return RoleAssignmentAuthority(cast(str,v["principal_id"]),cast(str,v["tenant_id"]),cast(str,v["role_id"]),cast(RoleAssignmentStatus,v["status"]),cast(int,v["revision"]))

def test_states_and_exact_values():
    assert [s.value for s in RoleAssignmentStatus]==["ACTIVE","REVOKED"] and assignment().role_id=="role-a"

@pytest.mark.parametrize("field",["principal_id","tenant_id","role_id"])
@pytest.mark.parametrize("value",[""," "," value","value "])
def test_identifiers_reject_invalid(field,value):
    with pytest.raises(ValueError): assignment(**{field:value})

def test_status_revision_and_immutability():
    with pytest.raises(TypeError): assignment(status="ACTIVE")
    with pytest.raises(ValueError): assignment(revision=-1)
    with pytest.raises(ValueError): assignment(revision=True)
    with pytest.raises((AttributeError,TypeError)): setattr(assignment(),"status",RoleAssignmentStatus.REVOKED)

def test_deterministic_hashable_and_multi_tenant_roles():
    assert assignment()==assignment() and hash(assignment())==hash(assignment())
    assert assignment(role_id="role-b")!=assignment() and assignment(tenant_id="other")!=assignment()

def test_exact_surface_and_no_default_status():
    assert {f.name for f in fields(RoleAssignmentAuthority)}=={"principal_id","tenant_id","role_id","status","revision"}
    assert not {"permissions","membership_status","owner","credential_id","profile","subscription","financial","kernel","kind"}.intersection(RoleAssignmentAuthority.__dataclass_fields__)
    assert signature(RoleAssignmentAuthority).parameters["status"].default is signature(RoleAssignmentAuthority).empty
