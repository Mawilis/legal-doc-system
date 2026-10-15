"""TITLE: D12 bootstrap seed service direct certificate.
VERSION: v1.0.0-D12-BOOTSTRAP-SEED-CERT
AUTHORITY: Purpose-matched self-seed composition proof.
ABSOLUTE PATH: /Users/wilsonkhanyezi/legal-doc-system/tests/unit/test_system_permission_bootstrap_seed_service.py
CERTIFICATION DATE: 2026-10-14
CHANGELOG: v1.0.0 certifies both directions, binding, replay seam, and exclusions.
BOUNDARY: No arbitrary grant, transaction lifecycle, tenant, activation, or finance.
"""
from datetime import datetime, timezone
from types import SimpleNamespace
import pytest
from tools.eos.auth.current_system_permission_bootstrap_authority import CurrentSystemPermissionBootstrapAuthorityResolver
from tools.eos.auth.principal_authority import PrincipalAuthority
from tools.eos.auth.principal_authority_repository import PrincipalAuthorityRepository
from tools.eos.auth.principal_status import PrincipalStatus
from tools.eos.auth.system_permission_assignment_registry import SystemPermissionAssignmentRegistry
from tools.eos.auth.system_permission_bootstrap_authority_registry import SystemPermissionBootstrapAuthorityRegistry
from tools.eos.auth.system_permission_bootstrap_seed_service import SystemPermissionBootstrapSeedError, SystemPermissionBootstrapSeedService
from tools.eos.auth.system_permission_command_evidence import SystemPermissionCommandEvidence, SystemPermissionCommandOperation
from tools.eos.auth.system_permission_command_policy import ASSIGN_BOOTSTRAP_PURPOSE, ASSIGN_COMMAND_PERMISSION, REVOKE_BOOTSTRAP_PURPOSE, REVOKE_COMMAND_PERMISSION

NOW = datetime(2026, 10, 14, 14, 0, tzinfo=timezone.utc)
class Session: in_transaction = True


def _service() -> tuple[SystemPermissionBootstrapSeedService, CurrentSystemPermissionBootstrapAuthorityResolver, SystemPermissionAssignmentRegistry]:
    assignments = SystemPermissionAssignmentRegistry(object())
    bootstrap_registry = SystemPermissionBootstrapAuthorityRegistry(object())
    resolver = CurrentSystemPermissionBootstrapAuthorityResolver(principal_collection=object(), bootstrap_registry=bootstrap_registry)
    return SystemPermissionBootstrapSeedService(principal_collection=object(), bootstrap_resolver=resolver, assignment_registry=assignments), resolver, assignments


def _evidence(purpose: str, permission: str) -> SystemPermissionCommandEvidence:
    return SystemPermissionCommandEvidence(SystemPermissionCommandOperation.BOOTSTRAP_SEED, "principal-a", "principal-a", permission, "evidence-seed", NOW, "idem-seed", bootstrap_id="bootstrap-a", bootstrap_purpose=purpose)


@pytest.mark.parametrize("purpose,permission", [(ASSIGN_BOOTSTRAP_PURPOSE, ASSIGN_COMMAND_PERMISSION), (REVOKE_BOOTSTRAP_PURPOSE, REVOKE_COMMAND_PERMISSION)])
def test_both_exact_seed_directions_and_bindings(monkeypatch: pytest.MonkeyPatch, purpose: str, permission: str) -> None:
    service, resolver, registry = _service()
    seen: dict[str, object] = {}
    monkeypatch.setattr(type(resolver), "resolve", lambda self, **kwargs: SimpleNamespace(bootstrap_id="bootstrap-a", actor_principal_id="principal-a", purpose=purpose))
    monkeypatch.setattr(PrincipalAuthorityRepository, "get", lambda *args, **kwargs: PrincipalAuthority("principal-a", PrincipalStatus.ACTIVE, 1))
    monkeypatch.setattr(type(registry), "create_or_replay", lambda self, value, **kwargs: seen.update(value=value, kwargs=kwargs) or value)
    result = service.seed(_evidence(purpose, permission), session=Session())  # type: ignore[arg-type]
    assert result.principal_id == "principal-a" and result.permission_id == permission
    assert result.assigned_by_principal_id == "principal-a"
    assert seen["kwargs"] == {"idempotency_key": "idem-seed", "session": seen["kwargs"]["session"]}  # type: ignore[index]


def test_seed_rejects_inactive_transaction_target_mismatch_missing_bootstrap_and_arbitrary_permission(monkeypatch: pytest.MonkeyPatch) -> None:
    service, resolver, _ = _service()
    evidence = _evidence(ASSIGN_BOOTSTRAP_PURPOSE, ASSIGN_COMMAND_PERMISSION)
    with pytest.raises(SystemPermissionBootstrapSeedError, match="ACTIVE_TRANSACTION_REQUIRED"):
        service.seed(evidence, session=SimpleNamespace(in_transaction=False))  # type: ignore[arg-type]
    with pytest.raises(SystemPermissionBootstrapSeedError, match="BOOTSTRAP_SELF_SEED_REQUIRED"):
        service.seed(SystemPermissionCommandEvidence(SystemPermissionCommandOperation.BOOTSTRAP_SEED, "a", "b", ASSIGN_COMMAND_PERMISSION, "e", NOW, "i", bootstrap_id="x", bootstrap_purpose=ASSIGN_BOOTSTRAP_PURPOSE), session=Session())  # type: ignore[arg-type]
    monkeypatch.setattr(type(resolver), "resolve", lambda *args, **kwargs: None)
    with pytest.raises(SystemPermissionBootstrapSeedError, match="CURRENT_BOOTSTRAP_REQUIRED"):
        service.seed(evidence, session=Session())  # type: ignore[arg-type]
    with pytest.raises(Exception, match="BOOTSTRAP_SEED_PERMISSION_MISMATCH"):
        service.seed(_evidence(ASSIGN_BOOTSTRAP_PURPOSE, "privileged_activation:issue"), session=Session())  # type: ignore[arg-type]


def test_no_transaction_or_forbidden_authority_surface() -> None:
    assert not {"start_session", "commit", "abort", "activate", "execute_payment"} & set(dir(SystemPermissionBootstrapSeedService))


# WILSY OS SOVEREIGN ARTIFACT SEAL
# ARTIFACT: test_system_permission_bootstrap_seed_service.py
# VERSION: v1.0.0-D12-BOOTSTRAP-SEED-CERT
# AUTHORITY BOUNDARY: EXACT PURPOSE-MATCHED SELF-SEED CERTIFICATE
# END OF WILSY OS SOVEREIGN ARTIFACT
