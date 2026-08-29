# -*- coding: utf-8 -*-
"""Bounded certification for the forward-canonical lifecycle policy.

VERSION: v1.0.0-WILSY-PRINCIPAL-LIFECYCLE-POLICY-CERT
CHANGELOG: v1.0.0 certifies transition admissibility and authority boundaries only.
"""
import inspect
from typing import cast

import pytest

from tools.eos.auth.principal_lifecycle_policy import (
    PrincipalLifecycleTransitionError,
    can_transition,
    require_transition,
)
from tools.eos.auth.principal_status import PrincipalStatus


@pytest.mark.parametrize(
    ("current", "target"),
    [
        (PrincipalStatus.ACTIVE, PrincipalStatus.SUSPENDED),
        (PrincipalStatus.ACTIVE, PrincipalStatus.REVOKED),
        (PrincipalStatus.SUSPENDED, PrincipalStatus.ACTIVE),
        (PrincipalStatus.SUSPENDED, PrincipalStatus.REVOKED),
    ],
)
def test_allowed_transitions(current: PrincipalStatus, target: PrincipalStatus) -> None:
    assert can_transition(current, target)
    assert require_transition(current, target) is None


@pytest.mark.parametrize(
    ("current", "target"),
    [
        (PrincipalStatus.ACTIVE, PrincipalStatus.ACTIVE),
        (PrincipalStatus.SUSPENDED, PrincipalStatus.SUSPENDED),
        (PrincipalStatus.REVOKED, PrincipalStatus.REVOKED),
        (PrincipalStatus.REVOKED, PrincipalStatus.ACTIVE),
        (PrincipalStatus.REVOKED, PrincipalStatus.SUSPENDED),
    ],
)
def test_forbidden_and_self_transitions_fail_closed(
    current: PrincipalStatus, target: PrincipalStatus
) -> None:
    assert not can_transition(current, target)
    with pytest.raises(PrincipalLifecycleTransitionError):
        require_transition(current, target)


def test_policy_is_deterministic_and_stateless() -> None:
    pair = (PrincipalStatus.ACTIVE, PrincipalStatus.REVOKED)
    assert can_transition(*pair) is can_transition(*pair)
    assert "current" in inspect.signature(can_transition).parameters
    assert "target" in inspect.signature(require_transition).parameters


def test_typed_boundary_rejects_unknown_strings() -> None:
    assert not can_transition(cast(PrincipalStatus, "ACTIVE"), PrincipalStatus.SUSPENDED)
    with pytest.raises(PrincipalLifecycleTransitionError):
        require_transition(cast(PrincipalStatus, "ACTIVE"), PrincipalStatus.SUSPENDED)


def test_policy_has_no_external_authority_or_status_mutation() -> None:
    assert set(PrincipalStatus) == {
        PrincipalStatus.ACTIVE,
        PrincipalStatus.SUSPENDED,
        PrincipalStatus.REVOKED,
    }
    assert not any(name in inspect.signature(can_transition).parameters for name in ("tenant_id", "role", "permission", "credential"))
    assert not hasattr(can_transition, "__self__")


# ARTIFACT: test_principal_lifecycle_policy.py
# VERSION: v1.0.0-WILSY-PRINCIPAL-LIFECYCLE-POLICY-CERT
# END OF WILSY OS SOVEREIGN ARTIFACT
