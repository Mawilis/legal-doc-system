"""Unit certification for the minimal tenant membership authority contract."""
from dataclasses import fields
from inspect import signature
from typing import cast
import pytest
from tools.eos.auth.tenant_membership import TenantMembershipAuthority, TenantMembershipStatus

def member(**changes):
    value = dict(principal_id="principal-a", tenant_id="tenant-a", status=TenantMembershipStatus.ACTIVE, revision=0)
    value.update(changes)
    return TenantMembershipAuthority(principal_id=cast(str, value["principal_id"]), tenant_id=cast(str, value["tenant_id"]), status=cast(TenantMembershipStatus, value["status"]), revision=cast(int, value["revision"]))

def test_all_states_and_exact_values():
    assert [member(status=s).status for s in TenantMembershipStatus] == list(TenantMembershipStatus)
    assert member().principal_id == "principal-a" and member().tenant_id == "tenant-a" and member().revision == 0

@pytest.mark.parametrize("field", ["principal_id", "tenant_id"])
@pytest.mark.parametrize("value", ["", " ", " principal-a", "principal-a "])
def test_identifiers_reject_empty_whitespace_and_trimming(field, value):
    with pytest.raises(ValueError): member(**{field: value})

def test_revision_and_status_are_typed_and_fail_closed():
    with pytest.raises(ValueError): member(revision=-1)
    with pytest.raises(ValueError): member(revision=True)
    with pytest.raises(TypeError): member(status="ACTIVE")

def test_immutable_hashable_and_deterministic():
    value = member()
    with pytest.raises((AttributeError, TypeError)): setattr(value, "status", TenantMembershipStatus.REVOKED)
    assert value == member() and hash(value) == hash(member())
    assert value != member(principal_id="principal-b") and value != member(tenant_id="tenant-b")

def test_exact_surface_and_authority_boundaries():
    names = {field.name for field in fields(TenantMembershipAuthority)}
    assert names == {"principal_id", "tenant_id", "status", "revision"}
    forbidden = {"role", "roles", "permissions", "founding_owner", "credential_id", "kind", "email", "subscription", "payment", "kernel"}
    assert not names.intersection(forbidden)

def test_multi_tenant_pair_identity_is_allowed():
    assert member(tenant_id="tenant-b") != member()
    assert member(principal_id="principal-b") != member()

def test_no_default_active_membership():
    assert signature(TenantMembershipAuthority).parameters["status"].default is signature(TenantMembershipAuthority).empty
