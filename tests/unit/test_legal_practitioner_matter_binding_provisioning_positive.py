"""P4-R4-R2D canonical grant/revoke and fail-closed service tests.

Actual immutable domain factory and in-memory registry are exercised.
External lifecycle, policy lookup and conflict provenance are isolated
and must be certified separately.
"""
from __future__ import annotations
from tools.eos.legal_operations.service.legal_practitioner_matter_access_codec import encode_practitioner_matter_access as _p47_encode_evidence

from datetime import timedelta
from pathlib import Path
import runpy
from types import SimpleNamespace
from typing import Any
from unittest.mock import Mock

import pytest

from tools.eos.auth.tenant_authorization import (
    TenantAuthorizationDecision, TenantAuthorizationReason,
)
from tools.eos.auth.principal_status import PrincipalStatus
from tools.eos.auth.tenant_membership import TenantMembershipStatus
from tools.eos.auth.tenant_business_role import TenantBusinessRoleStatus
from tools.eos.auth.role_assignment import RoleAssignmentStatus
from tools.eos.auth.role_assignment_repository import (
    RoleAssignmentNotFoundError,
)
from tools.eos.legal_operations.domain.legal_practitioner_matter_access import (
    LegalPractitionerMatterAccessDecision,
    LegalPractitionerMatterAccessEvidence,
)
from tools.eos.legal_operations.domain.legal_practitioner_matter_binding import (
    LegalPractitionerMatterBinding,
    PractitionerMatterBindingStatus,
)
from tools.eos.legal_operations.registry import (
    legal_practitioner_matter_binding_registry as registry,
)
from tools.eos.legal_operations.service import (
    legal_practitioner_matter_binding_provisioning_service as service,
)

ROOT = Path(__file__).resolve().parents[2]
BINDING_FIXTURE = runpy.run_path(
    str(ROOT / "tests/unit/test_legal_practitioner_matter_binding.py")
)
EVIDENCE_FIXTURE = runpy.run_path(
    str(ROOT / "tests/unit/test_legal_practitioner_matter_access.py")
)
REGISTRY_FIXTURE = runpy.run_path(
    str(ROOT / "tests/unit/test_legal_practitioner_matter_binding_registry.py")
)
AT = BINDING_FIXTURE["AT"]
COLLECTION = REGISTRY_FIXTURE["Collection"]


class Session:
    in_transaction = True


class Principals:
    def __init__(self, *, active=True):
        self.active = active
        self.calls: list[Any] = []

    def resolve(self, principal_id, *, session=None):
        self.calls.append((principal_id, session))
        return SimpleNamespace(
            status=PrincipalStatus.ACTIVE if self.active else None
        )


class Memberships:
    def __init__(self, *, active=True):
        self.active = active
        self.calls: list[Any] = []

    def resolve(self, principal_id, tenant_id, *, session=None):
        self.calls.append((principal_id, tenant_id, session))
        return SimpleNamespace(
            status=TenantMembershipStatus.ACTIVE if self.active else None
        )


class BusinessRoles:
    def __init__(self, *, roles=("tenant_legal_attorney",)):
        self.roles = roles
        self.calls: list[Any] = []

    def resolve(self, principal_id, tenant_id, role_id, *, session=None):
        self.calls.append((principal_id, tenant_id, role_id, session))
        if role_id not in self.roles:
            raise RoleAssignmentNotFoundError("ABSENT")
        return SimpleNamespace(status=TenantBusinessRoleStatus.ACTIVE)


class AuthorizationRoles:
    def __init__(self, *, active=True):
        self.active = active
        self.calls: list[Any] = []

    def resolve(self, principal_id, tenant_id, role_id, *, session=None):
        self.calls.append((principal_id, tenant_id, role_id, session))
        return SimpleNamespace(
            status=RoleAssignmentStatus.ACTIVE if self.active else None
        )


def context(monkeypatch, *, target_roles=("tenant_legal_attorney",),
            target_active=True, member_active=True,
            authorization_active=True, evidence_changes=None):
    matter = BINDING_FIXTURE["matter"]()
    changes = evidence_changes or {}
    evidence = EVIDENCE_FIXTURE["_make"](**changes)
    session = Session()
    binding_col = COLLECTION()
    principals = Principals(active=target_active)
    memberships = Memberships(active=member_active)
    business = BusinessRoles(roles=target_roles)
    authorization = AuthorizationRoles(active=authorization_active)

    actor_decision = Mock(return_value=TenantAuthorizationDecision(
        True, TenantAuthorizationReason.AUTHORIZED,
        "tenant_legal_partner", "LEGAL_PARTNER"
    ))
    lifecycle = Mock(return_value=matter)
    evidence_reader = Mock(return_value=evidence)
    history_reader = Mock(return_value=(evidence,))
    provenance = Mock()

    monkeypatch.setattr(service, "authorize_tenant_operation", actor_decision)
    monkeypatch.setattr(service, "_case_matter", lifecycle)
    monkeypatch.setattr(service, "get_by_id", evidence_reader)
    monkeypatch.setattr(
        service, "read_practitioner_matter_access_history",
        history_reader, raising=False,
    )
    monkeypatch.setattr(
        service, "verify_current_conflict_provenance", provenance
    )

    kw: dict[str, Any] = dict(
        authenticated_principal_id="partner-1",
        tenant_id=matter.tenant_id,
        case_matter_id=matter.case_matter_id,
        practitioner_principal_id=evidence.practitioner_principal_id,
        binding_id="binding-service-1",
        access_evidence_id=evidence.access_evidence_id,
        expected_access_evidence_fingerprint=evidence.fingerprint,
        granted_at=AT,
        client_party_id="client-1",
        subject_identity_fingerprint="b" * 128,
        principal_repository=principals,
        membership_repository=memberships,
        business_role_repository=business,
        role_assignment_repository=authorization,
        lifecycle_collection=object(),
        access_evidence_collection=object(),
        disposition_collection=object(),
        binding_collection=binding_col,
        session=session,
    )
    return kw, {
        "matter": matter,
        "evidence": evidence,
        "binding_collection": binding_col,
        "session": session,
        "actor": actor_decision,
        "lifecycle": lifecycle,
        "evidence_reader": evidence_reader,
        "history_reader": history_reader,
        "provenance": provenance,
        "principals": principals,
        "memberships": memberships,
        "business": business,
        "authorization": authorization,
    }


def revoke_kwargs(kw: dict[str, Any]) -> dict[str, Any]:
    return dict(
        authenticated_principal_id=kw["authenticated_principal_id"],
        tenant_id=kw["tenant_id"],
        binding_id=kw["binding_id"],
        evidence_reference="revocation-evidence-1",
        revoked_at=AT + timedelta(hours=1),
        principal_repository=kw["principal_repository"],
        membership_repository=kw["membership_repository"],
        business_role_repository=kw["business_role_repository"],
        role_assignment_repository=kw["role_assignment_repository"],
        binding_collection=kw["binding_collection"],
        session=kw["session"],
    )


def test_canonical_grant_persists_real_domain_snapshot(monkeypatch):
    kw, evidence = context(monkeypatch)
    value = service.grant_binding(**kw)
    assert type(value) is LegalPractitionerMatterBinding
    assert value.status is PractitionerMatterBindingStatus.ACTIVE
    assert value.binding_id == kw["binding_id"]
    assert value.tenant_id == kw["tenant_id"]
    assert value.case_matter_id == kw["case_matter_id"]
    assert value.practitioner_principal_id == kw["practitioner_principal_id"]
    assert value.source_case_matter_fingerprint == evidence["matter"].fingerprint
    assert value.grant_evidence_reference == kw["access_evidence_id"]
    assert registry.read_binding_history(
        tenant_id=value.tenant_id, binding_id=value.binding_id,
        collection=kw["binding_collection"], session=kw["session"],
    ) == (value,)
    assert evidence["provenance"].call_args.kwargs["session"] is kw["session"]
    assert evidence["provenance"].call_args.kwargs["evidence"] == evidence["evidence"]
    assert evidence["evidence_reader"].call_args.kwargs["session"] is kw["session"]
    assert evidence["lifecycle"].call_args.kwargs["session"] is kw["session"]
    assert all(s is kw["session"] for s in kw["binding_collection"].sessions)
    assert evidence["actor"].call_args.kwargs["permission_id"] == service.PERMISSION
    assert evidence["actor"].call_args.kwargs["operation"] == service.OPERATION


def test_replay_is_exact_and_does_not_insert_second_snapshot(monkeypatch):
    kw, _ = context(monkeypatch)
    first = service.grant_binding(**kw)
    assert service.grant_binding(**kw) == first
    assert len(kw["binding_collection"].rows) == 1


def test_revocation_appends_immutable_successor(monkeypatch):
    kw, _ = context(monkeypatch)
    initial = service.grant_binding(**kw)
    revoked = service.revoke_binding(**revoke_kwargs(kw))
    assert revoked.status is PractitionerMatterBindingStatus.REVOKED
    assert revoked.binding_id == initial.binding_id
    assert revoked.fingerprint != initial.fingerprint
    assert revoked.revoked_by_principal_id == kw["authenticated_principal_id"]
    assert registry.read_binding_history(
        tenant_id=initial.tenant_id, binding_id=initial.binding_id,
        collection=kw["binding_collection"], session=kw["session"],
    ) == (initial, revoked)
    assert registry.resolve_current_binding(
        tenant_id=initial.tenant_id, binding_id=initial.binding_id,
        collection=kw["binding_collection"], session=kw["session"],
    ) is None
    assert len(kw["binding_collection"].rows) == 2


def test_duplicate_revocation_denied_without_third_snapshot(monkeypatch):
    kw, _ = context(monkeypatch)
    service.grant_binding(**kw)
    service.revoke_binding(**revoke_kwargs(kw))
    with pytest.raises(service.PractitionerBindingProvisioningDenied):
        service.revoke_binding(**revoke_kwargs(kw))
    assert len(kw["binding_collection"].rows) == 2


@pytest.mark.parametrize("roles", [
    (), ("tenant_legal_partner", "tenant_legal_attorney"),
])
def test_no_or_ambiguous_target_business_role_denies_before_matter(
    monkeypatch, roles,
):
    kw, evidence = context(monkeypatch, target_roles=roles)
    with pytest.raises(service.PractitionerBindingProvisioningDenied):
        service.grant_binding(**kw)
    evidence["lifecycle"].assert_not_called()
    assert kw["binding_collection"].rows == []


@pytest.mark.parametrize("kind", ["principal", "membership", "auth"])
def test_inactive_target_denied_before_matter(monkeypatch, kind):
    kw, evidence = context(
        monkeypatch,
        target_active=kind != "principal",
        member_active=kind != "membership",
        authorization_active=kind != "auth",
    )
    with pytest.raises(service.PractitionerBindingProvisioningDenied):
        service.grant_binding(**kw)
    evidence["lifecycle"].assert_not_called()
    assert kw["binding_collection"].rows == []


def test_deny_documentary_evidence_cannot_create_binding(monkeypatch):
    kw, evidence = context(
        monkeypatch,
        evidence_changes={
            "decision": LegalPractitionerMatterAccessDecision.DENY
        },
    )
    with pytest.raises(service.PractitionerBindingProvisioningDenied):
        service.grant_binding(**kw)
    evidence["provenance"].assert_not_called()
    assert kw["binding_collection"].rows == []


def test_unavailable_conflict_provenance_denies_before_write(monkeypatch):
    kw, evidence = context(monkeypatch)
    evidence["provenance"].side_effect = RuntimeError("UNAVAILABLE")
    with pytest.raises(service.PractitionerBindingProvisioningDenied):
        service.grant_binding(**kw)
    assert kw["binding_collection"].rows == []


def test_foreign_tenant_policy_evidence_denied(monkeypatch):
    kw, evidence = context(monkeypatch)
    foreign = EVIDENCE_FIXTURE["_make"](tenant_id="foreign-tenant")
    evidence["evidence_reader"].return_value = foreign
    with pytest.raises(service.PractitionerBindingProvisioningDenied):
        service.grant_binding(**kw)
    assert kw["binding_collection"].rows == []


def test_no_regrant_after_revocation(monkeypatch):
    kw, _ = context(monkeypatch)
    service.grant_binding(**kw)
    service.revoke_binding(**revoke_kwargs(kw))
    kw["binding_id"] = "another-binding-id"
    with pytest.raises(service.PractitionerBindingProvisioningDenied):
        service.grant_binding(**kw)
    assert len(kw["binding_collection"].rows) == 2



def test_additional_active_unrelated_business_role_denied(monkeypatch):
    # This is the critical gap: scanning only the three approved
    # practitioner roles would miss a fourth concurrently active role.
    from tools.eos.auth.tenant_authority_policy import TENANT_ROLES
    extra = "tenant_legal_secretary"
    assert extra in TENANT_ROLES
    kw, ctx = context(
        monkeypatch,
        target_roles=("tenant_legal_attorney", extra),
    )
    with pytest.raises(service.PractitionerBindingProvisioningDenied):
        service.grant_binding(**kw)
    ctx["lifecycle"].assert_not_called()
    assert kw["binding_collection"].rows == []


def test_only_unrelated_active_business_role_denied(monkeypatch):
    from tools.eos.auth.tenant_authority_policy import TENANT_ROLES
    extra = "tenant_legal_secretary"
    assert extra in TENANT_ROLES
    kw, ctx = context(monkeypatch, target_roles=(extra,))
    with pytest.raises(service.PractitionerBindingProvisioningDenied):
        service.grant_binding(**kw)
    ctx["lifecycle"].assert_not_called()
    assert kw["binding_collection"].rows == []


def test_full_scope_business_role_authority_outage_denied(monkeypatch):
    kw, ctx = context(monkeypatch)
    reader = kw["business_role_repository"]
    reader.resolve = Mock(side_effect=RuntimeError("UNAVAILABLE"))
    with pytest.raises(service.PractitionerBindingProvisioningDenied):
        service.grant_binding(**kw)
    ctx["lifecycle"].assert_not_called()
    assert kw["binding_collection"].rows == []



def test_independent_persisted_deny_blocks_grant(monkeypatch):
    kw, ctx = context(monkeypatch)
    deny = EVIDENCE_FIXTURE["_make"](
        access_evidence_id="independent-deny-1",
        decision=LegalPractitionerMatterAccessDecision.DENY,
    )
    ctx["history_reader"].return_value = (ctx["evidence"], deny)
    with pytest.raises(service.PractitionerBindingProvisioningDenied):
        service.grant_binding(**kw)
    ctx["provenance"].assert_not_called()
    assert kw["binding_collection"].rows == []


def test_ambiguous_equal_time_allows_block_grant(monkeypatch):
    kw, ctx = context(monkeypatch)
    other = EVIDENCE_FIXTURE["_make"](
        access_evidence_id="independent-allow-2",
    )
    ctx["history_reader"].return_value = (ctx["evidence"], other)
    with pytest.raises(service.PractitionerBindingProvisioningDenied):
        service.grant_binding(**kw)
    ctx["provenance"].assert_not_called()
    assert kw["binding_collection"].rows == []


def test_missing_or_unavailable_history_blocks_grant(monkeypatch):
    kw, ctx = context(monkeypatch)
    ctx["history_reader"].return_value = ()
    with pytest.raises(service.PractitionerBindingProvisioningDenied):
        service.grant_binding(**kw)
    ctx["provenance"].assert_not_called()
    assert kw["binding_collection"].rows == []


def test_history_storage_exception_blocks_grant(monkeypatch):
    kw, ctx = context(monkeypatch)
    ctx["history_reader"].side_effect = RuntimeError("HISTORY_UNAVAILABLE")
    with pytest.raises(service.PractitionerBindingProvisioningDenied):
        service.grant_binding(**kw)
    ctx["provenance"].assert_not_called()
    assert kw["binding_collection"].rows == []


def test_newer_decisive_allow_cannot_be_substituted(monkeypatch):
    kw, ctx = context(monkeypatch)
    newer = EVIDENCE_FIXTURE["_make"](
        access_evidence_id="newer-independent-allow",
        effective_from=AT - timedelta(minutes=1),
    )
    ctx["history_reader"].return_value = (ctx["evidence"], newer)
    with pytest.raises(service.PractitionerBindingProvisioningDenied):
        service.grant_binding(**kw)
    ctx["provenance"].assert_not_called()
    assert kw["binding_collection"].rows == []


def test_policy_history_read_has_exact_scope_and_transaction(monkeypatch):
    kw, ctx = context(monkeypatch)
    value = service.grant_binding(**kw)
    assert value.status is PractitionerMatterBindingStatus.ACTIVE
    args = ctx["history_reader"].call_args.kwargs
    assert args["tenant_id"] == kw["tenant_id"]
    assert args["case_matter_id"] == kw["case_matter_id"]
    assert args["practitioner_principal_id"] == kw["practitioner_principal_id"]
    assert args["collection"] is kw["access_evidence_collection"]
    assert args["session"] is kw["session"]


def test_no_documentary_projection_content_access_authority():
    from tools.eos.legal_operations.service.legal_practitioner_matter_access_currentness import (
        LegalPractitionerMatterAccessCurrentness,
        LegalPractitionerMatterAccessCurrentnessState,
    )
    finding = LegalPractitionerMatterAccessCurrentness(
        tenant_id="tenant-1",
        case_matter_id="matter-1",
        practitioner_principal_id="practitioner-1",
        evaluation_time=AT,
        state=LegalPractitionerMatterAccessCurrentnessState.ALLOW_UNVERIFIED,
    )
    assert finding.permits_access is False



class PersistedAccessCollection:
    """Transaction-aware adapter exercising real registry and history code."""
    def __init__(self, records):
        self.rows = [dict(value) for value in records]
        self.calls = []
        self.fail = False

    def find_one(self, query, *, session):
        self.calls.append(("find_one", dict(query), session))
        if self.fail:
            raise RuntimeError("PERSISTENCE_DOWN")
        for row in self.rows:
            if all(row.get(key) == value for key, value in query.items()):
                return dict(row)
        return None

    def find(self, query, *, session):
        self.calls.append(("find", dict(query), session))
        if self.fail:
            raise RuntimeError("PERSISTENCE_DOWN")
        return iter(
            dict(row) for row in self.rows
            if all(row.get(key) == value for key, value in query.items())
        )


def real_access_seam(monkeypatch, kw, ctx, records):
    from tools.eos.legal_operations.registry.legal_practitioner_matter_access_registry import (
        get_by_id,
    )
    from tools.eos.legal_operations.registry.legal_practitioner_matter_access_history_reader import (
        read_practitioner_matter_access_history,
    )
    collection = PersistedAccessCollection(records)
    kw["access_evidence_collection"] = collection
    monkeypatch.setattr(service, "get_by_id", get_by_id)
    monkeypatch.setattr(
        service, "read_practitioner_matter_access_history",
        read_practitioner_matter_access_history,
    )
    return collection


def test_real_policy_registry_history_and_binding_write(monkeypatch):
    kw, ctx = context(monkeypatch)
    access = real_access_seam(
        monkeypatch, kw, ctx, [_p47_encode_evidence(ctx["evidence"])],
    )
    granted = service.grant_binding(**kw)
    assert granted.status is PractitionerMatterBindingStatus.ACTIVE
    assert len(kw["binding_collection"].rows) == 1
    assert [call[0] for call in access.calls] == [
        "find_one", "find",
    ]
    expected_scope = {
        "tenant_id": kw["tenant_id"],
        "case_matter_id": kw["case_matter_id"],
        "practitioner_principal_id": kw["practitioner_principal_id"],
    }
    assert access.calls[0][1] == {
        "tenant_id": kw["tenant_id"],
        "access_evidence_id": kw["access_evidence_id"],
    }
    assert access.calls[1][1] == expected_scope
    assert all(call[2] is kw["session"] for call in access.calls)
    revoked = service.revoke_binding(**revoke_kwargs(kw))
    assert revoked.status is PractitionerMatterBindingStatus.REVOKED
    assert registry.read_binding_history(
        tenant_id=kw["tenant_id"],
        binding_id=kw["binding_id"],
        collection=kw["binding_collection"],
        session=kw["session"],
    ) == (granted, revoked)


def test_real_history_independent_deny_blocks(monkeypatch):
    kw, ctx = context(monkeypatch)
    deny = EVIDENCE_FIXTURE["_make"](
        access_evidence_id="independent-persisted-deny",
        decision=LegalPractitionerMatterAccessDecision.DENY,
    )
    real_access_seam(
        monkeypatch, kw, ctx,
        [_p47_encode_evidence(ctx["evidence"]), _p47_encode_evidence(deny)],
    )
    with pytest.raises(service.PractitionerBindingProvisioningDenied):
        service.grant_binding(**kw)
    ctx["provenance"].assert_not_called()
    assert kw["binding_collection"].rows == []


def test_real_history_ambiguous_allows_block(monkeypatch):
    kw, ctx = context(monkeypatch)
    other = EVIDENCE_FIXTURE["_make"](
        access_evidence_id="independent-persisted-allow",
    )
    real_access_seam(
        monkeypatch, kw, ctx,
        [_p47_encode_evidence(ctx["evidence"]), _p47_encode_evidence(other)],
    )
    with pytest.raises(service.PractitionerBindingProvisioningDenied):
        service.grant_binding(**kw)
    ctx["provenance"].assert_not_called()
    assert kw["binding_collection"].rows == []


def test_real_history_corrupt_extra_record_blocks(monkeypatch):
    kw, ctx = context(monkeypatch)
    corrupt = _p47_encode_evidence(EVIDENCE_FIXTURE["_make"](
        access_evidence_id="corrupt-independent-access",
    ))
    corrupt["fingerprint"] = "0" * 128
    real_access_seam(
        monkeypatch, kw, ctx,
        [_p47_encode_evidence(ctx["evidence"]), corrupt],
    )
    with pytest.raises(service.PractitionerBindingProvisioningDenied):
        service.grant_binding(**kw)
    ctx["provenance"].assert_not_called()
    assert kw["binding_collection"].rows == []


def test_real_history_missing_reference_denied(monkeypatch):
    kw, ctx = context(monkeypatch)
    collection = real_access_seam(monkeypatch, kw, ctx, [])
    with pytest.raises(service.PractitionerBindingProvisioningDenied):
        service.grant_binding(**kw)
    assert collection.calls[0][0] == "find_one"
    ctx["provenance"].assert_not_called()
    assert kw["binding_collection"].rows == []


def test_real_history_storage_outage_denied(monkeypatch):
    kw, ctx = context(monkeypatch)
    collection = real_access_seam(
        monkeypatch, kw, ctx, [_p47_encode_evidence(ctx["evidence"])],
    )
    collection.fail = True
    with pytest.raises(service.PractitionerBindingProvisioningDenied):
        service.grant_binding(**kw)
    ctx["provenance"].assert_not_called()
    assert kw["binding_collection"].rows == []


def test_real_history_read_failure_after_id_lookup_denied(monkeypatch):
    kw, ctx = context(monkeypatch)
    collection = real_access_seam(
        monkeypatch, kw, ctx, [_p47_encode_evidence(ctx["evidence"])],
    )
    def failing_find(query, *, session):
        raise RuntimeError("HISTORY_READ_DOWN")
    collection.find = failing_find
    with pytest.raises(service.PractitionerBindingProvisioningDenied):
        service.grant_binding(**kw)
    ctx["provenance"].assert_not_called()
    assert kw["binding_collection"].rows == []


def test_real_history_cross_scope_records_cannot_substitute(monkeypatch):
    kw, ctx = context(monkeypatch)
    foreign = EVIDENCE_FIXTURE["_make"](
        tenant_id="other-tenant",
        access_evidence_id=ctx["evidence"].access_evidence_id,
    )
    real_access_seam(
        monkeypatch, kw, ctx, [_p47_encode_evidence(foreign)],
    )
    with pytest.raises(service.PractitionerBindingProvisioningDenied):
        service.grant_binding(**kw)
    ctx["provenance"].assert_not_called()
    assert kw["binding_collection"].rows == []

# WILSY OS SOVEREIGN ARTIFACT SEAL
# ARTIFACT: test_legal_practitioner_matter_binding_provisioning_positive.py
# VERSION: v1.0.0-P47-R77-PROVISIONING-POSITIVE-CERTIFICATE
# AUTHORITY BOUNDARY: provisioning behavior tests only; no content access
# TENANT POSTURE: exact own-tenant transactional scope
# FAIL-CLOSED POSTURE: stale, forged, ambiguous and unavailable truth denies
# FINANCIAL EXECUTION AUTHORITY: NONE; Kennel EOS exclusively
# END OF WILSY OS SOVEREIGN ARTIFACT

