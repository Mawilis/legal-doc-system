"""TITLE: WILSY OS Practitioner Binding History Disclosure Denial Certificate.
VERSION: v1.0.0-P12C-R4N-P4C10-R3-NEGATIVE-DISCLOSURE-CERT
AUTHORITY: Test-only certification of existing denial boundaries.
EPITOME: Preserve distinct read/provision permissions, missing read-operation
    admission, and documentary guard non-authority until separately certified
    actor-to-matter disclosure admission exists.
ABSOLUTE CANONICAL PATH: tests/unit/test_legal_practitioner_binding_history_disclosure_denials.py
COLLABORATION / OWNERSHIP: WILSY OS Core Engineering.
CERTIFICATION / UPDATE DATE: 2026-10-20
CHANGELOG:
    2026-10-20 v1.0.0-P12C-R4N-P4C10-R3-NEGATIVE-DISCLOSURE-CERT
    Adds negative-only contract tests. No authorization, policy, role grant,
    persistence, ethical-wall clearance, transport, content or finance authority.
SECURITY / PRIVACY POSTURE: Synthetic policy state only; no customer records.
TENANT BOUNDARY: No tenant or actor claims establish access.
AUTHORITY BOUNDARY: Denial regression certificate, not operational admission.
FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively.
"""

from __future__ import annotations

import pytest

from tools.eos.auth.roles import get_roles_granting_permission
from tools.eos.auth.tenant_authority_policy import (
    DENY,
    OPERATIONS,
    TENANT_ROLES,
    permission_for_business_role_operation,
    tenant_role_operation_eligibility,
)
from tools.eos.auth.tenant_authorization import _BINDINGS
from tools.eos.api.legal_practitioner_matter_binding_router import router
from tools.eos.legal_operations.service.legal_practitioner_ethical_wall_read_barrier import (
    EthicalWallReadBarrierResult,
    EthicalWallReadBarrierState,
)
from tools.eos.legal_operations.service.legal_practitioner_conjunctive_read_guard import (
    ConjunctiveReadGuardResult,
    ConjunctiveReadGuardState,
)

VERSION = "v1.0.0-P12C-R4N-P4C10-R3-NEGATIVE-DISCLOSURE-CERT"

READ_OPERATION = "legal_practitioner_matter_binding_read"
READ_PERMISSION = "legal_operations:practitioner_matter_binding:read"
PROVISION_OPERATION = "legal_practitioner_matter_binding_provision"
PROVISION_PERMISSION = (
    "legal_operations:practitioner_matter_binding:provision"
)


def test_binding_history_read_operation_remains_unregistered() -> None:
    assert READ_OPERATION not in OPERATIONS
    assert _BINDINGS.get(READ_OPERATION) is None
    assert permission_for_business_role_operation(READ_OPERATION) is None


@pytest.mark.parametrize("role", sorted(TENANT_ROLES))
def test_read_operation_denies_all_current_business_roles(role: str) -> None:
    assert tenant_role_operation_eligibility(role, READ_OPERATION) == DENY


def test_read_permission_has_no_static_role_grants() -> None:
    assert get_roles_granting_permission(READ_PERMISSION) == ()


def test_provisioning_does_not_inherit_read_permission() -> None:
    assert _BINDINGS.get(PROVISION_OPERATION) == PROVISION_PERMISSION
    assert get_roles_granting_permission(PROVISION_PERMISSION) == (
        "LEGAL_PARTNER",
    )
    assert READ_PERMISSION != PROVISION_PERMISSION
    assert get_roles_granting_permission(READ_PERMISSION) == ()


@pytest.mark.parametrize(
    "state",
    tuple(EthicalWallReadBarrierState),
)
def test_ethical_wall_evidence_never_grants_disclosure(
    state: EthicalWallReadBarrierState,
) -> None:
    finding = EthicalWallReadBarrierResult(state, None)
    assert finding.authorized is False
    assert finding.permits_content is False


@pytest.mark.parametrize(
    "state",
    tuple(ConjunctiveReadGuardState),
)
def test_documentary_conjunctive_guard_never_grants_disclosure(
    state: ConjunctiveReadGuardState,
) -> None:
    finding = ConjunctiveReadGuardResult(state)
    assert finding.authorized is False
    assert finding.permits_content is False


def test_binding_router_contains_no_read_endpoint() -> None:
    for route in router.routes:
        assert "GET" not in getattr(route, "methods", set())


# ARTIFACT: test_legal_practitioner_binding_history_disclosure_denials.py
# VERSION: v1.0.0-P12C-R4N-P4C10-R3-NEGATIVE-DISCLOSURE-CERT
# AUTHORITY BOUNDARY: regression evidence only; no positive admission
# TENANT POSTURE: exact tenant and matter remain separately governed
# FAIL-CLOSED POSTURE: no operation, role, or documentary evidence grants access
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively
# END OF WILSY OS SOVEREIGN ARTIFACT
