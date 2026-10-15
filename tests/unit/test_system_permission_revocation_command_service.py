"""TITLE: D12 revocation command service direct certificate.
VERSION: v1.0.0-D12-REVOCATION-COMMAND-CERT
AUTHORITY: Current-command, target, lineage, and closed-policy revocation proof.
ABSOLUTE PATH: /Users/wilsonkhanyezi/legal-doc-system/tests/unit/test_system_permission_revocation_command_service.py
CERTIFICATION DATE: 2026-10-14
CHANGELOG: v1.0.0 certifies bounded terminal revocation.
BOUNDARY: No recursive/arbitrary revocation, transaction lifecycle, tenant, or finance.
"""
from datetime import datetime, timedelta, timezone
from types import SimpleNamespace
import pytest
from tools.eos.auth.current_system_permission_possession import CurrentSystemPermissionPossessionResolver
from tools.eos.auth.principal_authority import PrincipalAuthority
from tools.eos.auth.principal_authority_repository import PrincipalAuthorityRepository
from tools.eos.auth.principal_status import PrincipalStatus
from tools.eos.auth.system_permission_assignment import SystemPermissionAssignment
from tools.eos.auth.system_permission_assignment_registry import SystemPermissionAssignmentRegistry
from tools.eos.auth.system_permission_command_evidence import SystemPermissionCommandEvidence, SystemPermissionCommandOperation
from tools.eos.auth.system_permission_command_policy import ASSIGN_COMMAND_PERMISSION, PRIVILEGED_ACTIVATION_ISSUE_PERMISSION, REVOKE_COMMAND_PERMISSION
from tools.eos.auth.system_permission_revocation_command_service import SystemPermissionRevocationCommandError, SystemPermissionRevocationCommandService

NOW = datetime(2026, 10, 14, 14, 0, tzinfo=timezone.utc)
class Session: in_transaction = True


def _original() -> SystemPermissionAssignment:
    return SystemPermissionAssignment.assign(assignment_id="assignment-a", principal_id="target-a", permission_id=PRIVILEGED_ACTIVATION_ISSUE_PERMISSION, assigned_by_principal_id="actor-a", assigned_at=NOW - timedelta(minutes=1), assignment_evidence_reference="evidence-assign")


def _evidence(permission: str = PRIVILEGED_ACTIVATION_ISSUE_PERMISSION) -> SystemPermissionCommandEvidence:
    return SystemPermissionCommandEvidence(SystemPermissionCommandOperation.REVOKE, "actor-a", "target-a", permission, "evidence-revoke", NOW, "idem-revoke", assignment_id="assignment-a")


def _parts() -> tuple[SystemPermissionRevocationCommandService, CurrentSystemPermissionPossessionResolver, SystemPermissionAssignmentRegistry]:
    registry = SystemPermissionAssignmentRegistry(object())
    resolver = CurrentSystemPermissionPossessionResolver(principal_collection=object(), assignment_registry=registry)
    return SystemPermissionRevocationCommandService(principal_collection=object(), possession_resolver=resolver, assignment_registry=registry), resolver, registry


def test_successful_revocation_and_exact_lineage(monkeypatch: pytest.MonkeyPatch) -> None:
    service, resolver, registry = _parts()
    monkeypatch.setattr(type(resolver), "resolve", lambda *args, **kwargs: object())
    monkeypatch.setattr(PrincipalAuthorityRepository, "get", lambda *args, **kwargs: PrincipalAuthority("target-a", PrincipalStatus.ACTIVE, 1))
    monkeypatch.setattr(type(registry), "get_history", lambda *args, **kwargs: (_original(),))
    monkeypatch.setattr(type(registry), "revoke_or_replay", lambda self, value, **kwargs: value)
    value = service.revoke(_evidence(), session=Session())  # type: ignore[arg-type]
    assert value.status.value == "REVOKED" and value.revision == 2
    assert value.principal_id == "target-a" and value.permission_id == PRIVILEGED_ACTIVATION_ISSUE_PERMISSION


@pytest.mark.parametrize("denied", [ASSIGN_COMMAND_PERMISSION, REVOKE_COMMAND_PERMISSION, "kernel:write", "*"])
def test_recursive_and_arbitrary_revocation_denied(denied: str) -> None:
    service, _, _ = _parts()
    with pytest.raises(Exception):
        service.revoke(_evidence(denied), session=Session())  # type: ignore[arg-type]


def test_missing_authority_assignment_inactive_target_and_transaction_denied(monkeypatch: pytest.MonkeyPatch) -> None:
    service, resolver, registry = _parts()
    with pytest.raises(SystemPermissionRevocationCommandError, match="ACTIVE_TRANSACTION_REQUIRED"):
        service.revoke(_evidence(), session=SimpleNamespace(in_transaction=False))  # type: ignore[arg-type]
    monkeypatch.setattr(type(resolver), "resolve", lambda *args, **kwargs: None)
    with pytest.raises(SystemPermissionRevocationCommandError, match="CURRENT_REVOCATION_COMMAND_AUTHORITY_REQUIRED"):
        service.revoke(_evidence(), session=Session())  # type: ignore[arg-type]
    monkeypatch.setattr(type(resolver), "resolve", lambda *args, **kwargs: object())
    monkeypatch.setattr(PrincipalAuthorityRepository, "get", lambda *args, **kwargs: PrincipalAuthority("target-a", PrincipalStatus.SUSPENDED, 1))
    with pytest.raises(SystemPermissionRevocationCommandError, match="TARGET_PRINCIPAL_NOT_CURRENT"):
        service.revoke(_evidence(), session=Session())  # type: ignore[arg-type]
    monkeypatch.setattr(PrincipalAuthorityRepository, "get", lambda *args, **kwargs: PrincipalAuthority("target-a", PrincipalStatus.ACTIVE, 1))
    monkeypatch.setattr(type(registry), "get_history", lambda *args, **kwargs: ())
    with pytest.raises(SystemPermissionRevocationCommandError, match="TARGET_ASSIGNMENT_NOT_FOUND"):
        service.revoke(_evidence(), session=Session())  # type: ignore[arg-type]


def test_no_transaction_or_forbidden_authority_surface() -> None:
    assert not {"start_session", "commit", "abort", "assign", "activate", "execute_payment"} & set(dir(SystemPermissionRevocationCommandService))


# WILSY OS SOVEREIGN ARTIFACT SEAL
# ARTIFACT: test_system_permission_revocation_command_service.py
# VERSION: v1.0.0-D12-REVOCATION-COMMAND-CERT
# AUTHORITY BOUNDARY: PRIVILEGED ACTIVATION ISSUE REVOCATION CERTIFICATE
# END OF WILSY OS SOVEREIGN ARTIFACT
