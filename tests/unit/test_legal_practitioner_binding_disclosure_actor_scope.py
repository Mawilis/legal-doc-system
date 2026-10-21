"""TITLE: WILSY OS Practitioner Binding Disclosure Actor-Scope Denials.
VERSION: v1.0.0-P12C-R4N-P4C10-R3-ACTOR-SCOPE-DENIAL-CERT
AUTHORITY: Test-only denial certificate; not matter access admission.
EPITOME: Forged authority-shaped dependencies and distinct requester or
    subject claims never yield documentary binding disclosure.
ABSOLUTE CANONICAL PATH: tests/unit/test_legal_practitioner_binding_disclosure_actor_scope.py
COLLABORATION / OWNERSHIP: WILSY OS Core Engineering.
CERTIFICATION / UPDATE DATE: 2026-10-20
CHANGELOG:
    2026-10-20 v1.0.0-P12C-R4N-P4C10-R3-ACTOR-SCOPE-DENIAL-CERT
    Proves denial-only service cannot infer grants or access repositories.
SECURITY / PRIVACY POSTURE: Synthetic opaque identifiers only.
TENANT BOUNDARY: Claims and dependency availability are insufficient.
AUTHORITY BOUNDARY: No positive disclosure, IAM or ethical-wall clearance.
FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively.
"""

from __future__ import annotations

import inspect
from types import SimpleNamespace

import pytest

from tools.eos.auth.tenant_authorization import (
    TenantAuthorizationDecision,
    TenantAuthorizationReason,
)
from tools.eos.legal_operations.service.legal_practitioner_binding_history_disclosure_service import (
    PractitionerBindingHistoryDisclosureDenied,
    admit_practitioner_binding_history_read,
)

VERSION = "v1.0.0-P12C-R4N-P4C10-R3-ACTOR-SCOPE-DENIAL-CERT"


class ForbiddenRepository:
    """Any attempted repository access must fail the test."""

    def __getattribute__(self, name: str) -> object:
        raise AssertionError("REPOSITORY_ACCESS_FORBIDDEN")


def _admit(
    actor: str,
    tenant: str,
    binding: str,
    dependency: object,
) -> None:
    admit_practitioner_binding_history_read(
        authenticated_principal_id=actor,
        tenant_id=tenant,
        binding_id=binding,
        principal_repository=dependency,
        membership_repository=dependency,
        business_role_repository=dependency,
        role_assignment_repository=dependency,
        matter_collection=dependency,
        binding_collection=dependency,
        wall_collection=dependency,
        practitioner_access_collection=dependency,
        session=SimpleNamespace(in_transaction=True),
    )


@pytest.mark.parametrize(
    ("actor", "tenant", "binding"),
    (
        ("requester", "tenant-A", "binding-A"),
        ("subject-practitioner", "tenant-A", "binding-A"),
        ("requester", "tenant-B", "binding-A"),
        ("requester", "tenant-A", "binding-B"),
    ),
)
def test_scope_claims_never_grant_disclosure(
    actor: str,
    tenant: str,
    binding: str,
) -> None:
    with pytest.raises(
        PractitionerBindingHistoryDisclosureDenied,
        match="P9_BINDING_DISCLOSURE_NOT_CERTIFIED",
    ):
        _admit(actor, tenant, binding, object())


def test_complete_looking_dependencies_do_not_trigger_repository_access() -> None:
    with pytest.raises(
        PractitionerBindingHistoryDisclosureDenied,
        match="P9_BINDING_DISCLOSURE_NOT_CERTIFIED",
    ):
        _admit(
            "requester",
            "tenant-A",
            "binding-A",
            ForbiddenRepository(),
        )


def test_forged_authorized_iam_value_cannot_be_substituted() -> None:
    fake_decision = TenantAuthorizationDecision(
        authorized=True,
        reason=TenantAuthorizationReason.AUTHORIZED,
        business_role="tenant_legal_partner",
        authorization_role="LEGAL_PARTNER",
    )
    with pytest.raises(
        PractitionerBindingHistoryDisclosureDenied,
        match="P9_BINDING_DISCLOSURE_NOT_CERTIFIED",
    ):
        _admit(
            "requester",
            "tenant-A",
            "binding-A",
            fake_decision,
        )


def test_no_subject_or_preconstructed_authority_input() -> None:
    parameters = inspect.signature(
        admit_practitioner_binding_history_read
    ).parameters
    assert "authenticated_principal_id" in parameters
    assert "subject_practitioner_principal_id" not in parameters
    assert "authorization_decision" not in parameters
    assert "matter_access_decision" not in parameters
    assert "wall_clearance" not in parameters
    assert not any(
        item.kind is inspect.Parameter.VAR_KEYWORD
        for item in parameters.values()
    )


# ARTIFACT: test_legal_practitioner_binding_disclosure_actor_scope.py
# VERSION: v1.0.0-P12C-R4N-P4C10-R3-ACTOR-SCOPE-DENIAL-CERT
# AUTHORITY BOUNDARY: synthetic denial and non-interaction only
# TENANT POSTURE: no cross-tenant authorization inferred
# FAIL-CLOSED POSTURE: all requests denied
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively
# END OF WILSY OS SOVEREIGN ARTIFACT
