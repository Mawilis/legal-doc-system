"""Direct certificate for the governed authorization-role revocation command.

TITLE: Governed Authorization Role Revocation Command Direct Certificate
VERSION: v1.0.0-P1-R3C-G1-GOVERNED-AUTHORIZATION-ROLE-REVOCATION-COMMAND-CERT
AUTHORITY: Wilsy OS Core Governance / Sovereign IAM Design
EPITOME: Prove replay-first admission, current authority, pre-write validation,
         ordered evidence/CAS writes, failure propagation, and hard boundaries.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tests/unit/test_authorization_role_revocation_command.py
COLLABORATION / OWNERSHIP: Certifies only authorization_role_revocation_command.py.
CERTIFICATION / UPDATE DATE: 2026-10-13
CHANGELOG: v1.0.0-P1-R3C-G1 establishes deterministic direct command proof with
           no Mongo, HTTP, Legal Operations, session lifecycle, or finance.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2; ISO 27001.
SECURITY / PRIVACY POSTURE: Synthetic opaque identifiers and in-memory spies only.
TENANT BOUNDARY: Exact actor, target, role, revision, and tenant flow certified.
AUTHORITY BOUNDARY: Direct IAM orchestration verification only; no authority grant.
FINANCIAL AUTHORITY BOUNDARY: None; Kennel EOS remains exclusive.
"""
from __future__ import annotations

import ast
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import pytest

from tools.eos.auth.authorization_role_revocation_command import (
    OPERATION,
    PERMISSION,
    AuthorizationRoleRevocationCommand,
    AuthorizationRoleRevocationCommandAuthorizationDeniedError,
    AuthorizationRoleRevocationCommandPolicyDeniedError,
    AuthorizationRoleRevocationCommandReplayConflictError,
    AuthorizationRoleRevocationCommandTargetInvalidError,
    AuthorizationRoleRevocationCommandTransactionRequiredError,
    AuthorizationRoleRevocationResultState,
)
from tools.eos.auth.authorization_role_revocation_evidence import AuthorizationRoleRevocationEvidence
from tools.eos.auth.authorization_role_revocation_policy import (
    AuthorizationRoleRevocationDecision,
    AuthorizationRoleRevocationDenialCode,
    evaluate_authorization_role_revocation,
)
from tools.eos.auth.role_assignment import RoleAssignmentAuthority, RoleAssignmentStatus
from tools.eos.auth.role_assignment_repository import RoleAssignmentRevisionConflictError
from tools.eos.auth.tenant_authorization import TenantAuthorizationDecision, TenantAuthorizationReason
from tools.eos.auth.tenant_authorization_decision_evidence import TenantAuthorizationDecisionEvidence


VERSION = "v1.0.0-P1-R3C-G1-GOVERNED-AUTHORIZATION-ROLE-REVOCATION-COMMAND-CERT"
PRODUCTION = Path("tools/eos/auth/authorization_role_revocation_command.py")
NOW = datetime(2026, 10, 13, 12, 0, tzinfo=timezone.utc)


class Session:
    """Caller-owned active-transaction marker without lifecycle APIs."""

    def __init__(self, active: bool = True) -> None:
        self.in_transaction = active


def revocation_evidence(**changes: object) -> AuthorizationRoleRevocationEvidence:
    """Build deterministic historic revocation evidence."""
    values: dict[str, object] = {
        "revocation_id": "revocation-001",
        "tenant_id": "tenant-a",
        "actor_principal_id": "actor-a",
        "target_principal_id": "target-a",
        "target_role_id": "AUDITOR",
        "target_assignment_prior_revision": 4,
        "target_assignment_result_revision": 5,
        "operation": "role_revoke",
        "reason_reference": "case:001",
        "authorization_evidence_reference": "tenant-authorization-decision:auth-001",
        "authorization_evidence_fingerprint": "a" * 128,
        "idempotency_key": "idem-001",
        "revoked_at": NOW,
    }
    values.update(changes)
    return AuthorizationRoleRevocationEvidence(**values)  # type: ignore[arg-type]


def authorization_evidence() -> TenantAuthorizationDecisionEvidence:
    """Build current-attempt authorization evidence returned by the issuer spy."""
    return TenantAuthorizationDecisionEvidence(
        tenant_id="tenant-a",
        authorization_decision_id="auth-001",
        principal_id="actor-a",
        operation=OPERATION,
        permission=PERMISSION,
        business_role="tenant_admin",
        authorization_role="ENTERPRISE_ADMIN",
        membership_revision=2,
        role_assignment_revision=3,
        subject_reference="role-assignment:tenant-a:target-a:AUDITOR:revision:4",
        subject_evidence_fingerprint="b" * 128,
        permission_namespace_version="permission-v1",
        authorization_role_policy_version="roles-v1",
        tenant_business_role_policy_version="business-v1",
        tenant_authorization_composition_version="authorization-v1",
        idempotency_key="role-revocation-authorization:idem-001",
        authorized_at=NOW,
    )


class ReplayRegistry:
    """Revocation registry spy preserving ordered reads and writes."""

    def __init__(self, calls: list[tuple[Any, ...]], historic: AuthorizationRoleRevocationEvidence | None = None) -> None:
        self.calls = calls
        self.historic = historic
        self.failure: BaseException | None = None

    def get_by_tenant_idempotency(self, **kwargs: object) -> AuthorizationRoleRevocationEvidence | None:
        self.calls.append(("historic_read", kwargs))
        return self.historic

    def create_or_replay(self, evidence: AuthorizationRoleRevocationEvidence, *, session: object) -> AuthorizationRoleRevocationEvidence:
        self.calls.append(("revocation_write", evidence, session))
        if self.failure is not None:
            raise self.failure
        return evidence


class AssignmentRepository:
    """Exact target resolution and CAS spy."""

    def __init__(self, calls: list[tuple[Any, ...]], target: RoleAssignmentAuthority | None = None) -> None:
        self.calls = calls
        self.target = target or RoleAssignmentAuthority("target-a", "tenant-a", "AUDITOR", RoleAssignmentStatus.ACTIVE, 4)
        self.resolve_failure: BaseException | None = None
        self.cas_failure: BaseException | None = None

    def resolve(self, *args: object, **kwargs: object) -> RoleAssignmentAuthority:
        self.calls.append(("target_read", args, kwargs))
        if self.resolve_failure is not None:
            raise self.resolve_failure
        return self.target

    def compare_and_swap(self, *args: object, **kwargs: object) -> RoleAssignmentAuthority:
        self.calls.append(("cas_write", args, kwargs))
        if self.cas_failure is not None:
            raise self.cas_failure
        return args[0]  # type: ignore[return-value]


class AuthorizationEvidenceRegistry:
    """Authorization-decision evidence issuance spy."""

    def __init__(self, calls: list[tuple[Any, ...]]) -> None:
        self.calls = calls

    def issue(self, **kwargs: object) -> TenantAuthorizationDecisionEvidence:
        self.calls.append(("authorization_write", kwargs))
        return authorization_evidence()


class Factory:
    """Count deterministic clock and identifier generation."""

    def __init__(self, value: object) -> None:
        self.value = value
        self.calls = 0

    def __call__(self) -> Any:
        self.calls += 1
        return self.value


def setup(
    *,
    historic: AuthorizationRoleRevocationEvidence | None = None,
    target: RoleAssignmentAuthority | None = None,
    authorized: bool = True,
    policy_allowed: bool = True,
) -> dict[str, Any]:
    """Build one fully injected command harness."""
    calls: list[tuple[Any, ...]] = []
    replay = ReplayRegistry(calls, historic)
    assignments = AssignmentRepository(calls, target)
    authorization_registry = AuthorizationEvidenceRegistry(calls)
    clock = Factory(NOW)
    identity = Factory("revocation-001")

    def authorize(**kwargs: object) -> TenantAuthorizationDecision:
        calls.append(("authorize", kwargs))
        return TenantAuthorizationDecision(
            authorized,
            TenantAuthorizationReason.AUTHORIZED if authorized else TenantAuthorizationReason.PERMISSION_NOT_GRANTED,
            "tenant_admin" if authorized else None,
            "ENTERPRISE_ADMIN" if authorized else None,
        )

    def policy(**kwargs: object) -> AuthorizationRoleRevocationDecision:
        calls.append(("policy", kwargs))
        return AuthorizationRoleRevocationDecision(
            allowed=policy_allowed,
            denial_code=None if policy_allowed else AuthorizationRoleRevocationDenialCode.TARGET_ROLE_NOT_REVOCABLE,
            operation=kwargs["operation"],
            actor_principal_id=kwargs["actor_principal_id"],
            actor_tenant_id=kwargs["actor_tenant_id"],
            actor_authorization_role=kwargs["actor_authorization_role"],
            target_principal_id=kwargs["target_principal_id"],
            target_tenant_id=kwargs["target_tenant_id"],
            target_authorization_role=kwargs["target_authorization_role"],
            target_assignment_status=kwargs["target_assignment_status"],
        )

    command = AuthorizationRoleRevocationCommand(
        principal_repository=object(),
        membership_repository=object(),
        role_assignment_repository=assignments,
        business_role_repository=object(),
        role_assignment_collection=object(),
        authorization_evidence_registry=authorization_registry,
        revocation_evidence_registry=replay,
        clock=clock,
        revocation_id_factory=identity,
        authorization=authorize,
        revocation_policy=policy,
    )
    return {
        "command": command,
        "calls": calls,
        "replay": replay,
        "assignments": assignments,
        "clock": clock,
        "identity": identity,
    }


def execute(harness: dict[str, Any], **changes: object) -> Any:
    """Invoke the command with one canonical request."""
    values: dict[str, object] = {
        "actor_principal_id": "actor-a",
        "tenant_id": "tenant-a",
        "target_principal_id": "target-a",
        "target_role_id": "AUDITOR",
        "expected_target_assignment_revision": 4,
        "reason_reference": "case:001",
        "idempotency_key": "idem-001",
        "session": Session(),
    }
    values.update(changes)
    return harness["command"].execute(**values)


@pytest.mark.parametrize("session", [None, Session(False)])
def test_transaction_admission_rejects_before_first_persistence_read(session: object) -> None:
    """Missing and inactive caller transactions reject before replay lookup."""
    harness = setup()
    with pytest.raises(AuthorizationRoleRevocationCommandTransactionRequiredError):
        execute(harness, session=session)
    assert harness["calls"] == []


def test_exact_replay_is_first_and_zero_write_without_authority_or_factories() -> None:
    """Exact history returns before current authority, target state, writes, clock, or ID."""
    historic = revocation_evidence()
    harness = setup(historic=historic, target=RoleAssignmentAuthority("target-a", "tenant-a", "AUDITOR", RoleAssignmentStatus.REVOKED, 5), authorized=False)
    result = execute(harness)
    assert result.state is AuthorizationRoleRevocationResultState.EXACT_REPLAY
    assert result.revocation_evidence is historic
    assert result.resulting_role_assignment == RoleAssignmentAuthority("target-a", "tenant-a", "AUDITOR", RoleAssignmentStatus.REVOKED, 5)
    assert [call[0] for call in harness["calls"]] == ["historic_read"]
    assert harness["clock"].calls == harness["identity"].calls == 0


@pytest.mark.parametrize(
    ("field", "value"),
    (
        ("actor_principal_id", "actor-b"),
        ("tenant_id", "tenant-b"),
        ("target_principal_id", "target-b"),
        ("target_role_id", "SERVICE_WORKER"),
        ("expected_target_assignment_revision", 3),
        ("reason_reference", "case:other"),
        ("idempotency_key", "idem-other"),
    ),
)
def test_historic_divergence_rejects_zero_write_even_if_currently_authorized(field: str, value: object) -> None:
    """Every caller-controlled replay dimension diverges before current authority."""
    harness = setup(historic=revocation_evidence(), authorized=True)
    with pytest.raises(AuthorizationRoleRevocationCommandReplayConflictError):
        execute(harness, **{field: value})
    assert [call[0] for call in harness["calls"]] == ["historic_read"]
    assert harness["clock"].calls == harness["identity"].calls == 0


def test_absent_replay_reproves_exact_current_authorization_before_target() -> None:
    """Canonical operation, permission, tenant, repositories, and session precede target read."""
    harness = setup()
    execute(harness)
    assert [call[0] for call in harness["calls"][:3]] == ["historic_read", "authorize", "target_read"]
    kwargs = harness["calls"][1][1]
    assert kwargs["operation"] == "role_revoke"
    assert kwargs["permission_id"] == "tenant:role_assignment:write"
    assert kwargs["principal_id"] == "actor-a" and kwargs["tenant_id"] == "tenant-a"
    assert kwargs["session"] is harness["calls"][0][1]["session"]


def test_authorization_denial_has_zero_write_and_no_target_resolution() -> None:
    """Current denial stops before target, policy, evidence, CAS, or factories."""
    harness = setup(authorized=False)
    with pytest.raises(AuthorizationRoleRevocationCommandAuthorizationDeniedError):
        execute(harness)
    assert [call[0] for call in harness["calls"]] == ["historic_read", "authorize"]
    assert harness["clock"].calls == harness["identity"].calls == 0


@pytest.mark.parametrize(
    "target",
    (
        RoleAssignmentAuthority("target-a", "tenant-b", "AUDITOR", RoleAssignmentStatus.ACTIVE, 4),
        RoleAssignmentAuthority("target-a", "tenant-a", "AUDITOR", RoleAssignmentStatus.REVOKED, 4),
        RoleAssignmentAuthority("target-a", "tenant-a", "AUDITOR", RoleAssignmentStatus.ACTIVE, 3),
    ),
)
def test_target_scope_status_and_revision_fail_before_write(target: RoleAssignmentAuthority) -> None:
    """Wrong tenant, inactive status, and stale revision reject after authorization."""
    harness = setup(target=target)
    with pytest.raises(AuthorizationRoleRevocationCommandTargetInvalidError):
        execute(harness)
    assert [call[0] for call in harness["calls"]] == ["historic_read", "authorize", "target_read"]


def test_target_not_found_fails_before_write() -> None:
    """Repository absence remains a bounded target failure with zero writes."""
    harness = setup()
    harness["assignments"].resolve_failure = RuntimeError("absent")
    with pytest.raises(AuthorizationRoleRevocationCommandTargetInvalidError):
        execute(harness)
    assert [call[0] for call in harness["calls"]] == ["historic_read", "authorize", "target_read"]


@pytest.mark.parametrize("role", ["ENTERPRISE_ADMIN", "SOVEREIGN_ARCHITECT"])
def test_certified_policy_denies_privileged_targets_before_write(role: str) -> None:
    """Ordinary command cannot cross enterprise-root or system-root boundaries."""
    target = RoleAssignmentAuthority("target-a", "tenant-a", role, RoleAssignmentStatus.ACTIVE, 4)
    harness = setup(target=target)
    harness["command"]._revocation_policy = evaluate_authorization_role_revocation
    with pytest.raises(AuthorizationRoleRevocationCommandPolicyDeniedError):
        execute(harness, target_role_id=role)
    assert [call[0] for call in harness["calls"]] == ["historic_read", "authorize", "target_read"]


def test_policy_denial_has_zero_write() -> None:
    """Any pure-policy denial stops before authorization evidence issuance."""
    harness = setup(policy_allowed=False)
    with pytest.raises(AuthorizationRoleRevocationCommandPolicyDeniedError):
        execute(harness)
    assert [call[0] for call in harness["calls"]] == ["historic_read", "authorize", "target_read", "policy"]


def test_success_has_exact_three_write_order_session_and_binding() -> None:
    """All reads precede authorization evidence, CAS, then revocation evidence."""
    harness = setup()
    result = execute(harness)
    names = [call[0] for call in harness["calls"]]
    assert names == ["historic_read", "authorize", "target_read", "policy", "authorization_write", "cas_write", "revocation_write"]
    assert result.state is AuthorizationRoleRevocationResultState.NEWLY_REVOKED
    assert result.resulting_role_assignment == RoleAssignmentAuthority("target-a", "tenant-a", "AUDITOR", RoleAssignmentStatus.REVOKED, 5)
    evidence = result.revocation_evidence
    assert evidence.revocation_id == "revocation-001"
    assert evidence.target_assignment_prior_revision == 4 and evidence.target_assignment_result_revision == 5
    assert evidence.reason_reference == "case:001" and evidence.idempotency_key == "idem-001"
    auth = authorization_evidence()
    assert evidence.authorization_evidence_reference == auth.authorization_evidence_reference
    assert evidence.authorization_evidence_fingerprint == auth.authorization_evidence_fingerprint
    session = harness["calls"][0][1]["session"]
    assert harness["calls"][4][1]["session"] is session
    assert harness["calls"][5][2]["session"] is session
    assert harness["calls"][6][2] is session
    assert harness["clock"].calls == harness["identity"].calls == 1


def test_cas_conflict_emits_no_revocation_evidence_and_no_factories() -> None:
    """CAS loss propagates without third write, retry, compensation, clock, or ID."""
    harness = setup()
    harness["assignments"].cas_failure = RoleAssignmentRevisionConflictError("ROLE_ASSIGNMENT_REVISION_CONFLICT")
    with pytest.raises(RoleAssignmentRevisionConflictError):
        execute(harness)
    assert [call[0] for call in harness["calls"]][-2:] == ["authorization_write", "cas_write"]
    assert harness["clock"].calls == harness["identity"].calls == 0


def test_revocation_evidence_failure_propagates_without_compensation_or_success() -> None:
    """Third-write failure remains failure and no compensating CAS is attempted."""
    harness = setup()
    harness["replay"].failure = RuntimeError("revocation persistence failed")
    with pytest.raises(RuntimeError, match="revocation persistence failed"):
        execute(harness)
    names = [call[0] for call in harness["calls"]]
    assert names[-3:] == ["authorization_write", "cas_write", "revocation_write"]
    assert names.count("cas_write") == 1


def test_source_owns_no_transaction_retry_transport_or_forbidden_authority() -> None:
    """Certify dependency and lifecycle boundaries structurally."""
    source = PRODUCTION.read_text(encoding="utf-8")
    tree = ast.parse(source)
    imports = {
        alias.name
        for node in ast.walk(tree)
        if isinstance(node, ast.Import)
        for alias in node.names
    } | {
        node.module or ""
        for node in ast.walk(tree)
        if isinstance(node, ast.ImportFrom)
    }
    assert all(not name.startswith(("fastapi", "tools.eos.legal_operations")) for name in imports)
    calls = {
        node.func.attr if isinstance(node.func, ast.Attribute) else node.func.id
        for node in ast.walk(tree)
        if isinstance(node, ast.Call) and isinstance(node.func, (ast.Attribute, ast.Name))
    }
    assert calls.isdisjoint({
        "start_session", "start_transaction", "with_transaction", "commit_transaction",
        "abort_transaction", "end_session", "revoke_session", "revoke_refresh_token",
        "rotate_root", "recover_root", "break_glass", "activate_privilege",
    })
    assert "financial authority boundary: none" in source.casefold()
    assert "kennel eos remains exclusive" in source.casefold()


# ARTIFACT: test_authorization_role_revocation_command.py
# VERSION: v1.0.0-P1-R3C-G1-GOVERNED-AUTHORIZATION-ROLE-REVOCATION-COMMAND-CERT
# AUTHORITY BOUNDARY: direct command verification only; no transport, root, recovery, break-glass, JIT, session lifecycle, Legal Operations, or finance
# TENANT POSTURE: exact actor, target, role, revision, authorization evidence, and revocation evidence scope certified
# FAIL-CLOSED POSTURE: transaction absence, replay divergence, denial, target drift, policy denial, CAS loss, and evidence failure reject
# FINANCIAL EXECUTION AUTHORITY: None; Kennel EOS remains exclusive
# REAL MONGO COMMAND CERTIFICATE: NOT AUTHORIZED OR EXECUTED IN THIS GATE
# END OF WILSY OS SOVEREIGN ARTIFACT
