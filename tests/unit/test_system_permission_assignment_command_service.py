"""TITLE: D12 assignment command service direct certificate.
VERSION: v1.0.0-D12-ASSIGNMENT-COMMAND-CERT
AUTHORITY: Current-command, current-target, closed-policy assignment proof.
ABSOLUTE PATH: /Users/wilsonkhanyezi/legal-doc-system/tests/unit/test_system_permission_assignment_command_service.py
CERTIFICATION DATE: 2026-10-14
CHANGELOG: v1.0.0 certifies bounded ongoing assignment.
BOUNDARY: No recursion, arbitrary grant, transaction lifecycle, tenant, or finance.
"""
from datetime import datetime, timezone
from types import SimpleNamespace
import pytest
from tools.eos.auth.current_system_permission_possession import CurrentSystemPermissionPossessionResolver
from tools.eos.auth.principal_authority import PrincipalAuthority
from tools.eos.auth.principal_authority_repository import PrincipalAuthorityNotFoundError, PrincipalAuthorityRepository
from tools.eos.auth.principal_status import PrincipalStatus
from tools.eos.auth.system_permission_assignment_command_service import SystemPermissionAssignmentCommandError, SystemPermissionAssignmentCommandService
from tools.eos.auth.system_permission_assignment_registry import SystemPermissionAssignmentRegistry
from tools.eos.auth.system_permission_command_evidence import SystemPermissionCommandEvidence, SystemPermissionCommandOperation
from tools.eos.auth.system_permission_command_policy import ASSIGN_COMMAND_PERMISSION, PRIVILEGED_ACTIVATION_ISSUE_PERMISSION, REVOKE_COMMAND_PERMISSION

NOW = datetime(2026, 10, 14, 14, 0, tzinfo=timezone.utc)
class Session: in_transaction = True


def _parts() -> tuple[SystemPermissionAssignmentCommandService, CurrentSystemPermissionPossessionResolver, SystemPermissionAssignmentRegistry]:
    registry = SystemPermissionAssignmentRegistry(object())
    resolver = CurrentSystemPermissionPossessionResolver(principal_collection=object(), assignment_registry=registry)
    return SystemPermissionAssignmentCommandService(principal_collection=object(), possession_resolver=resolver, assignment_registry=registry), resolver, registry


def _evidence(permission: str = PRIVILEGED_ACTIVATION_ISSUE_PERMISSION) -> SystemPermissionCommandEvidence:
    return SystemPermissionCommandEvidence(SystemPermissionCommandOperation.ASSIGN, "actor-a", "target-a", permission, "evidence-assign", NOW, "idem-assign")


def test_current_actor_command_and_target_assign_exact_permission(monkeypatch: pytest.MonkeyPatch) -> None:
    service, resolver, registry = _parts()
    monkeypatch.setattr(type(resolver), "resolve", lambda self, **kwargs: object())
    monkeypatch.setattr(PrincipalAuthorityRepository, "get", lambda *args, **kwargs: PrincipalAuthority("target-a", PrincipalStatus.ACTIVE, 1))
    monkeypatch.setattr(type(registry), "create_or_replay", lambda self, value, **kwargs: value)
    value = service.assign(_evidence(), session=Session())  # type: ignore[arg-type]
    assert value.permission_id == PRIVILEGED_ACTIVATION_ISSUE_PERMISSION
    assert value.principal_id == "target-a" and value.assigned_by_principal_id == "actor-a"


@pytest.mark.parametrize("denied", [ASSIGN_COMMAND_PERMISSION, REVOKE_COMMAND_PERMISSION, "kernel:write", "tenant:profile:write", "*"])
def test_recursive_and_arbitrary_assignment_denied(denied: str) -> None:
    service, _, _ = _parts()
    with pytest.raises(Exception):
        service.assign(_evidence(denied), session=Session())  # type: ignore[arg-type]


def test_missing_command_missing_target_inactive_target_and_transaction_denied(monkeypatch: pytest.MonkeyPatch) -> None:
    service, resolver, _ = _parts()
    with pytest.raises(SystemPermissionAssignmentCommandError, match="ACTIVE_TRANSACTION_REQUIRED"):
        service.assign(_evidence(), session=SimpleNamespace(in_transaction=False))  # type: ignore[arg-type]
    monkeypatch.setattr(type(resolver), "resolve", lambda *args, **kwargs: None)
    with pytest.raises(SystemPermissionAssignmentCommandError, match="CURRENT_ASSIGNMENT_COMMAND_AUTHORITY_REQUIRED"):
        service.assign(_evidence(), session=Session())  # type: ignore[arg-type]
    monkeypatch.setattr(type(resolver), "resolve", lambda *args, **kwargs: object())
    monkeypatch.setattr(PrincipalAuthorityRepository, "get", lambda *args, **kwargs: (_ for _ in ()).throw(PrincipalAuthorityNotFoundError("missing")))
    with pytest.raises(SystemPermissionAssignmentCommandError, match="TARGET_PRINCIPAL_NOT_FOUND"):
        service.assign(_evidence(), session=Session())  # type: ignore[arg-type]
    monkeypatch.setattr(PrincipalAuthorityRepository, "get", lambda *args, **kwargs: PrincipalAuthority("target-a", PrincipalStatus.SUSPENDED, 1))
    with pytest.raises(SystemPermissionAssignmentCommandError, match="TARGET_PRINCIPAL_NOT_CURRENT"):
        service.assign(_evidence(), session=Session())  # type: ignore[arg-type]


def test_no_transaction_or_forbidden_authority_surface() -> None:
    assert not {"start_session", "commit", "abort", "revoke", "activate", "execute_payment"} & set(dir(SystemPermissionAssignmentCommandService))


# WILSY OS SOVEREIGN ARTIFACT SEAL
# ARTIFACT: test_system_permission_assignment_command_service.py
# VERSION: v1.0.0-D12-ASSIGNMENT-COMMAND-CERT
# AUTHORITY BOUNDARY: PRIVILEGED ACTIVATION ISSUE ASSIGNMENT CERTIFICATE
# END OF WILSY OS SOVEREIGN ARTIFACT
