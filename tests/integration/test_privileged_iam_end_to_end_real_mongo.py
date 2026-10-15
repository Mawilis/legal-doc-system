"""
WILSY OS SOVEREIGN IAM — P8 END-TO-END REAL-MONGO CERTIFICATE

VERSION:
    v1.0.0-P8-PRIVILEGED-IAM-END-TO-END-REAL-MONGO

AUTHORITY:
    Certification only. This artifact creates no production authority.

PURPOSE:
    Prove that the independently sealed D12/P2/P3/P4/P5/P6/P7 IAM components
    compose into coherent executable privileged-access lifecycles against a
    real writable MongoDB replica set.

CERTIFIED FLOWS:
    1. D12 assignment -> P4 issuance -> P5 use -> P6 revoke -> P5 denial.
    2. D12 break-glass assignment -> P7 dual-control issuance ->
       P6 revoke -> terminal non-resurrection.
    3. D12 permission revocation -> current-possession loss ->
       downstream privileged command denial.

TRANSACTION POSTURE:
    Every command owns no transaction. The caller creates and controls the
    active Mongo session/transaction for each command boundary.

AUTHORITY BOUNDARY:
    No new permission, role, assignment policy, break-glass authority,
    HTTP route, autonomous override, token/session issuance, or financial
    execution authority is created by this certificate.

FINANCIAL EXECUTION AUTHORITY:
    Kennel EOS exclusively.
"""

from __future__ import annotations

from datetime import timedelta
from typing import Any, Final

import pytest

from tools.eos.auth.current_system_permission_possession import (
    CurrentSystemPermissionPossessionResolver,
)
from tools.eos.auth.system_permission_command_policy import (
    PRIVILEGED_ACTIVATION_BREAK_GLASS_PERMISSION,
    PRIVILEGED_ACTIVATION_ISSUE_PERMISSION,
)

PRIVILEGED_ACTIVATION_REVOKE_PERMISSION: Final[str] = (
    "privileged_activation:revoke"
)
from tools.eos.auth.privileged_activation import (
    PrivilegedTargetClass,
)
from tools.eos.auth.privileged_activation_revocation_command_evidence import (
    PrivilegedActivationRevocationCommandEvidence,
)
from tools.eos.auth.privileged_activation_revocation_command_evidence_registry import (
    PrivilegedActivationRevocationCommandEvidenceRegistry,
)
from tools.eos.auth.privileged_activation_revocation_command_service import (
    PrivilegedActivationRevocationCommandService,
)
from tools.eos.auth.privileged_activation_issuance_service import (
    PrivilegedActivationIssuanceError,
)
from tools.eos.auth.privileged_activation_use_authority import (
    PrivilegedActivationUseError,
)
from tools.eos.auth.privileged_break_glass_command_evidence_registry import (
    PrivilegedBreakGlassCommandEvidenceRegistry,
)
from tools.eos.auth.privileged_break_glass_service import (
    PrivilegedBreakGlassService,
    PrivilegedBreakGlassServiceError,
)
from tools.eos.auth.system_permission_assignment import (
    SystemPermissionAssignment,
)
from tools.eos.auth.system_permission_assignment_command_service import (
    SystemPermissionAssignmentCommandService,
)
from tools.eos.auth.system_permission_revocation_command_service import (
    SystemPermissionRevocationCommandService,
)
from tools.eos.auth.system_permission_command_evidence import (
    SystemPermissionCommandEvidence,
    SystemPermissionCommandOperation,
)
from tools.eos.auth.system_permission_bootstrap_authority_registry import (
    SystemPermissionBootstrapAuthorityRegistry,
)
from tools.eos.auth.current_system_permission_bootstrap_authority import (
    CurrentSystemPermissionBootstrapAuthorityResolver,
)
from tools.eos.auth.system_permission_bootstrap_authority import (
    SystemPermissionBootstrapAuthority,
)
from tools.eos.auth.system_permission_bootstrap_seed_service import (
    SystemPermissionBootstrapSeedService,
)
from tools.eos.auth.system_permission_command_policy import (
    ASSIGN_BOOTSTRAP_PURPOSE,
    ASSIGN_COMMAND_PERMISSION,
    REVOKE_BOOTSTRAP_PURPOSE,
    REVOKE_COMMAND_PERMISSION,
)

# Reuse the already certified P4 real-Mongo environment rather than inventing
# another authority/fixture topology.
from tests.integration.test_system_permission_command_plane_real_mongo import (
    NOW as D12_NOW,
    _assignment_evidence as _d12_assignment_evidence,
    _seed_evidence as _d12_seed_evidence,
)
from tests.integration.test_privileged_activation_issuance_service_real_mongo import (
    ASSIGNMENT_ID,
    ELIGIBILITY_ID,
    NOW,
    PRINCIPAL,
    PROOF_REFERENCE,
    PROOF_TENANT,
    SOVEREIGN_ARCHITECT,
    context,
    _seed,
)

# Reuse the already certified P7 environment extension for approver/supervisor
# setup and current security proof.
import tests.integration.test_privileged_break_glass_p6_lifecycle_real_mongo as p7_fixture

APPROVER = p7_fixture.APPROVER
SUPERVISOR = p7_fixture.SUPERVISOR


pytestmark = pytest.mark.integration


def _possession(
    context: dict[str, Any],
) -> CurrentSystemPermissionPossessionResolver:
    return CurrentSystemPermissionPossessionResolver(
        principal_collection=context["principals"],
        assignment_registry=context["assignment_registry"],
    )


def _d12_services(
    context: dict[str, Any],
) -> tuple[
    SystemPermissionBootstrapSeedService,
    SystemPermissionAssignmentCommandService,
    SystemPermissionRevocationCommandService,
]:
    """
    Compose the exact sealed D12 command graph over this certificate database.

    No alternate bootstrap service, inferred constructor, role authority, or
    direct ongoing permission persistence is permitted.
    """

    database = context["database"]

    bootstrap_registry = SystemPermissionBootstrapAuthorityRegistry(
        database["system_permission_bootstrap_authorities"]
    )
    bootstrap_registry.ensure_indexes()

    bootstrap_resolver = (
        CurrentSystemPermissionBootstrapAuthorityResolver(
            principal_collection=context["principals"],
            bootstrap_registry=bootstrap_registry,
        )
    )

    possession = _possession(context)

    seed = SystemPermissionBootstrapSeedService(
        principal_collection=context["principals"],
        bootstrap_resolver=bootstrap_resolver,
        assignment_registry=context["assignment_registry"],
    )

    assign = SystemPermissionAssignmentCommandService(
        principal_collection=context["principals"],
        possession_resolver=possession,
        assignment_registry=context["assignment_registry"],
    )

    revoke = SystemPermissionRevocationCommandService(
        principal_collection=context["principals"],
        possession_resolver=possession,
        assignment_registry=context["assignment_registry"],
    )

    return seed, assign, revoke


def _bootstrap_d12_actor(
    context: dict[str, Any],
) -> tuple[
    SystemPermissionBootstrapSeedService,
    SystemPermissionAssignmentCommandService,
    SystemPermissionRevocationCommandService,
]:
    seed, assign, revoke = _d12_services(
        context
    )

    bootstrap_registry = (
        SystemPermissionBootstrapAuthorityRegistry(
            context["database"][
                "system_permission_bootstrap_authorities"
            ]
        )
    )
    bootstrap_registry.ensure_indexes()

    # D12 command-plane actor is an explicit current principal.
    if context["principals"].find_one(
        {
            "principal_id": "actor-a",
        }
    ) is None:
        context["principals"].insert_one(
            {
                "principal_id": "actor-a",
                "status": "ACTIVE",
                "revision": 1,
            }
        )

    with context["client"].start_session() as session:
        with session.start_transaction():
            for purpose, suffix in (
                (
                    ASSIGN_BOOTSTRAP_PURPOSE,
                    "assign",
                ),
                (
                    REVOKE_BOOTSTRAP_PURPOSE,
                    "revoke",
                ),
            ):
                bootstrap_registry.create_or_replay(
                    SystemPermissionBootstrapAuthority.issue(
                        bootstrap_id=
                            "bootstrap-" + suffix,
                        actor_principal_id=
                            "actor-a",
                        purpose=purpose,
                        evidence_reference=
                            "installation-" + suffix,
                        issued_at=
                            D12_NOW
                            - timedelta(minutes=1),
                    ),
                    idempotency_key=
                        "bootstrap-idem-" + suffix,
                    session=session,
                )

    with context["client"].start_session() as session:
        with session.start_transaction():
            seed.seed(
                _d12_seed_evidence(
                    ASSIGN_BOOTSTRAP_PURPOSE,
                    ASSIGN_COMMAND_PERMISSION,
                    "assign",
                ),
                session=session,
            )

            seed.seed(
                _d12_seed_evidence(
                    REVOKE_BOOTSTRAP_PURPOSE,
                    REVOKE_COMMAND_PERMISSION,
                    "revoke",
                ),
                session=session,
            )

    possession = _possession(
        context
    )

    assert possession.resolve(
        principal_id="actor-a",
        permission_id=ASSIGN_COMMAND_PERMISSION,
    ) is not None

    assert possession.resolve(
        principal_id="actor-a",
        permission_id=REVOKE_COMMAND_PERMISSION,
    ) is not None

    return seed, assign, revoke


def _d12_assign(
    context: dict[str, Any],
    *,
    target_principal_id: str,
    permission_id: str,
    evidence_reference: str,
    idempotency_key: str,
) -> SystemPermissionAssignment:
    _, assign, _ = _bootstrap_d12_actor(context)

    command = _d12_assignment_evidence(
        actor="actor-a",
        target=target_principal_id,
        permission=permission_id,
        evidence=evidence_reference,
        idempotency=idempotency_key,
    )

    with context["client"].start_session() as session:
        with session.start_transaction():
            assigned = assign.assign(
                command,
                session=session,
            )

    return assigned


def _d12_revoke(
    context: dict[str, Any],
    *,
    assignment: SystemPermissionAssignment,
    target_principal_id: str,
    permission_id: str,
    evidence_reference: str,
    idempotency_key: str,
) -> SystemPermissionAssignment:
    _, _, revoke = _d12_services(context)

    command = SystemPermissionCommandEvidence(
        SystemPermissionCommandOperation.REVOKE,
        "actor-a",
        target_principal_id,
        permission_id,
        evidence_reference,
        NOW + timedelta(minutes=2),
        idempotency_key,
        assignment_id=assignment.assignment_id,
    )

    with context["client"].start_session() as session:
        with session.start_transaction():
            revoked = revoke.revoke(
                command,
                session=session,
            )

    return revoked


def _revocation_service(
    context: dict[str, Any],
) -> PrivilegedActivationRevocationCommandService:
    evidence_registry = (
        PrivilegedActivationRevocationCommandEvidenceRegistry(
            context["database"][
                "privileged_activation_revocation_command_evidence"
            ]
        )
    )
    evidence_registry.ensure_indexes()

    return PrivilegedActivationRevocationCommandService(
        possession_resolver=_possession(context),
        activation_registry=context["activation_registry"],
        evidence_registry=evidence_registry,
    )


def test_real_normal_privileged_lifecycle_d12_p4_p5_p6(
    context: dict[str, Any],
) -> None:
    """Certify assignment -> issuance -> use -> revoke -> denied use."""

    _seed(
        context,
        include_permission=False,
    )

    issue_assignment = _d12_assign(
        context,
        target_principal_id=PRINCIPAL,
        permission_id=PRIVILEGED_ACTIVATION_ISSUE_PERMISSION,
        evidence_reference="p8-d12-issue",
        idempotency_key="p8-d12-issue",
    )

    supervisor_assignment = SystemPermissionAssignment.assign(
        assignment_id="p8-assignment-revoke",
        principal_id=SUPERVISOR,
        permission_id=PRIVILEGED_ACTIVATION_REVOKE_PERMISSION,
        assigned_by_principal_id="p8-governance",
        assigned_at=NOW - timedelta(minutes=1),
        assignment_evidence_reference="p8-evidence-revoke",
    )

    with context["client"].start_session() as session:
        with session.start_transaction():

            # P6 supervisor principal may already exist in a reused topology;
            # only create if absent.
            if context["principals"].find_one(
                {"principal_id": SUPERVISOR},
                session=session,
            ) is None:
                from tools.eos.auth.principal_authority import (
                    PrincipalAuthority,
                )
                from tools.eos.auth.principal_authority_repository import (
                    PrincipalAuthorityRepository,
                )
                from tools.eos.auth.principal_status import (
                    PrincipalStatus,
                )

                PrincipalAuthorityRepository.create(
                    PrincipalAuthority(
                        SUPERVISOR,
                        PrincipalStatus.ACTIVE,
                        1,
                    ),
                    context["principals"],
                    session=session,
                )

            context["assignment_registry"].create_or_replay(
                supervisor_assignment,
                idempotency_key="p8-create-revoke",
                session=session,
            )

    possession = _possession(context)

    assert possession.resolve(
        principal_id=PRINCIPAL,
        permission_id=PRIVILEGED_ACTIVATION_ISSUE_PERMISSION,
    ) is not None

    with context["client"].start_session() as session:
        with session.start_transaction():
            activation = context["issuance_service"].issue_interactive(
                tenant_id=None,
                eligibility_evidence_id=ELIGIBILITY_ID,
                proof_tenant_id=PROOF_TENANT,
                proof_reference=PROOF_REFERENCE,
                issuance_idempotency_key="p8-normal-issuance",
                session=session,
            )

    assert activation.is_current(
        at=NOW,
        tenant_id=None,
        principal_id=PRINCIPAL,
        privileged_role_id=SOVEREIGN_ARCHITECT,
        target_class=PrivilegedTargetClass.PLATFORM_SYSTEM_ROOT,
    )

    use_authority = context.get("use_authority")
    if use_authority is None:
        from tools.eos.auth.privileged_activation_use_authority import (
            PrivilegedActivationUseAuthority,
        )

        use_authority = PrivilegedActivationUseAuthority(
            activation_registry=context["activation_registry"],
            eligibility_resolver=getattr(
                context["issuance_service"],
                "_eligibility_resolver",
            ),
            interactive_assurance_service=getattr(
                context["issuance_service"],
                "_interactive_assurance_service",
            ),
            noninteractive_assurance_service=getattr(
                context["issuance_service"],
                "_noninteractive_assurance_service",
                None,
            ),
        )

    with context["client"].start_session() as session:
        with session.start_transaction():
            use_result = use_authority.authorize_interactive(
                activation_tenant_id=None,
                proof_tenant_id=PROOF_TENANT,
                principal_id=PRINCIPAL,
                privileged_role_id=SOVEREIGN_ARCHITECT,
                target_class=PrivilegedTargetClass.PLATFORM_SYSTEM_ROOT,
                at=NOW + timedelta(seconds=15),
                proof_reference=PROOF_REFERENCE,
                idempotency_key="p8-normal-use",
                session=session,
            )

    assert use_result is not None

    command = PrivilegedActivationRevocationCommandEvidence.compose(
        actor_principal_id=SUPERVISOR,
        actor_permission_id=PRIVILEGED_ACTIVATION_REVOKE_PERMISSION,
        actor_permission_assignment_id=supervisor_assignment.assignment_id,
        actor_permission_assignment_revision=supervisor_assignment.revision,
        actor_permission_assignment_fingerprint=(
            supervisor_assignment.assignment_fingerprint
        ),
        target_activation_id=activation.activation_id,
        target_principal_id=PRINCIPAL,
        target_class=PrivilegedTargetClass.PLATFORM_SYSTEM_ROOT.value,
        target_tenant_id=None,
        revocation_reason_reference="p8-normal-terminal",
        authorized_at=NOW + timedelta(seconds=30),
        idempotency_key="p8-normal-revoke",
    )

    with context["client"].start_session() as session:
        with session.start_transaction():
            revoked = _revocation_service(context).revoke(
                command,
                session=session,
            )

    assert revoked.activation.status.value == "REVOKED"

    with context["client"].start_session() as session:
        session.start_transaction()

        with pytest.raises(PrivilegedActivationUseError):
            use_authority.authorize_interactive(
                activation_tenant_id=None,
                proof_tenant_id=PROOF_TENANT,
                principal_id=PRINCIPAL,
                privileged_role_id=SOVEREIGN_ARCHITECT,
                target_class=PrivilegedTargetClass.PLATFORM_SYSTEM_ROOT,
                at=NOW + timedelta(minutes=1),
                proof_reference=PROOF_REFERENCE,
                idempotency_key="p8-normal-use-after-revoke",
                session=session,
            )

        session.abort_transaction()


def test_real_break_glass_lifecycle_d12_p7_p6(
    context: dict[str, Any],
) -> None:
    """Certify dual-control P7 issuance -> P6 terminal revocation."""

    # Seed requester P2/P3 state without installing P4 issue authority.
    # P8 must prove break-glass permission arrival through D12 itself.
    _seed(
        context,
        include_permission=False,
    )

    with context["client"].start_session() as session:
        with session.start_transaction():
            p7_fixture.PrincipalAuthorityRepository.create(
                p7_fixture.PrincipalAuthority(
                    APPROVER,
                    p7_fixture.PrincipalStatus.ACTIVE,
                    1,
                ),
                context["principals"],
                session=session,
            )

            p7_fixture.PrincipalAuthorityRepository.create(
                p7_fixture.PrincipalAuthority(
                    SUPERVISOR,
                    p7_fixture.PrincipalStatus.ACTIVE,
                    1,
                ),
                context["principals"],
                session=session,
            )

            context["database"]["users"].insert_one(
                {
                    "user_id": APPROVER,
                    "email": "p7-approver@example.com",
                    "firstName": "P7",
                    "lastName": "Approver",
                    "role": "USER",
                    "permissions": [],
                    "tenantId": PROOF_TENANT,
                    "passwordHash": "synthetic",
                    "credential_revision": 9,
                    "mfaRegistered": True,
                    "hasSignedCovenant": True,
                    "createdAt": NOW.replace(
                        tzinfo=None
                    ),
                    "updatedAt": NOW.replace(
                        tzinfo=None
                    ),
                },
                session=session,
            )

            context["database"]["sessions"].insert_one(
                {
                    "tenant_id": PROOF_TENANT,
                    "user_id": APPROVER,
                    "session_reference": "session-p7-approver",
                    "expires_at":
                        NOW + timedelta(hours=1),
                },
                session=session,
            )

            context["factor_registry"].create_or_replay(
                p7_fixture.InteractiveFactorVerificationEvent(
                    "factor-p7-approver",
                    APPROVER,
                    "session-p7-approver",
                    9,
                    NOW,
                    p7_fixture.FactorVerificationStatus.VERIFIED,
                ),
                recorded_at=NOW,
                session=session,
            )

            context["proof_registry"].create_or_replay(
                p7_fixture.PrivilegedInteractiveSecurityProof(
                    "proof-p7-approver",
                    APPROVER,
                    "factor-p7-approver",
                    NOW,
                    9,
                    "session-p7-approver",
                    p7_fixture.PrivilegedInteractiveProofStatus.VERIFIED,
                    "proof-ref-p7-approver",
                ),
                status_changed_at=NOW,
                idempotency_key=
                    "proof-idem-p7-approver",
                session=session,
            )

    requester = _d12_assign(
        context,
        target_principal_id=PRINCIPAL,
        permission_id=
            PRIVILEGED_ACTIVATION_BREAK_GLASS_PERMISSION,
        evidence_reference=
            "p8-d12-break-glass-requester",
        idempotency_key=
            "p8-d12-break-glass-requester",
    )

    approver = _d12_assign(
        context,
        target_principal_id=APPROVER,
        permission_id=
            PRIVILEGED_ACTIVATION_BREAK_GLASS_PERMISSION,
        evidence_reference=
            "p8-d12-break-glass-approver",
        idempotency_key=
            "p8-d12-break-glass-approver",
    )

    # D12 policy intentionally does not delegate
    # privileged_activation:revoke. P6's supervisor authority remains an
    # independently provisioned exact current assignment, matching the
    # sealed P6/P7 lifecycle certificate.
    supervisor = SystemPermissionAssignment.assign(
        assignment_id=
            "assignment-p8-p7-supervisor-revoke",
        principal_id=SUPERVISOR,
        permission_id=
            PRIVILEGED_ACTIVATION_REVOKE_PERMISSION,
        assigned_by_principal_id=
            "p8-supervisory-governance",
        assigned_at=
            NOW - timedelta(minutes=1),
        assignment_evidence_reference=
            "p8-supervisor-revoke-evidence",
    )

    with context["client"].start_session() as session:
        with session.start_transaction():
            context["assignment_registry"].create_or_replay(
                supervisor,
                idempotency_key=
                    "p8-supervisor-revoke-create",
                session=session,
            )

    possession = _possession(context)

    assert possession.resolve(
        principal_id=PRINCIPAL,
        permission_id=
            PRIVILEGED_ACTIVATION_BREAK_GLASS_PERMISSION,
    ) == requester

    assert possession.resolve(
        principal_id=APPROVER,
        permission_id=
            PRIVILEGED_ACTIVATION_BREAK_GLASS_PERMISSION,
    ) == approver

    assert possession.resolve(
        principal_id=SUPERVISOR,
        permission_id=
            PRIVILEGED_ACTIVATION_REVOKE_PERMISSION,
    ) == supervisor

    evidence_registry = PrivilegedBreakGlassCommandEvidenceRegistry(
        context["database"]["privileged_break_glass_command_evidence"]
    )
    evidence_registry.ensure_indexes()

    service = PrivilegedBreakGlassService(
        possession_resolver=possession,
        eligibility_resolver=getattr(
            context["issuance_service"],
            "_eligibility_resolver",
        ),
        interactive_assurance_service=getattr(
            context["issuance_service"],
            "_interactive_assurance_service",
        ),
        activation_registry=context["activation_registry"],
        evidence_registry=evidence_registry,
        clock=lambda: NOW,
        assurance_attempt_id_factory=iter(
            (
                "p8-bg-requester-1",
                "p8-bg-approver-1",
                "p8-bg-requester-2",
                "p8-bg-approver-2",
            )
        ).__next__,
    )

    with context["client"].start_session() as session:
        with session.start_transaction():
            issued = service.issue_interactive(
                requester_principal_id=PRINCIPAL,
                approver_principal_id=APPROVER,
                tenant_id=None,
                requester_proof_tenant_id=PROOF_TENANT,
                requester_proof_reference=PROOF_REFERENCE,
                approver_proof_tenant_id=PROOF_TENANT,
                approver_proof_reference="proof-ref-p7-approver",
                eligibility_evidence_id=ELIGIBILITY_ID,
                reason_reference="p8-break-glass-opaque",
                effective_until=NOW + timedelta(minutes=10),
                idempotency_key="p8-break-glass",
                session=session,
            )

    assert issued.activation.is_current(
        at=NOW,
        tenant_id=None,
        principal_id=PRINCIPAL,
        privileged_role_id=SOVEREIGN_ARCHITECT,
        target_class=PrivilegedTargetClass.PLATFORM_SYSTEM_ROOT,
    )

    command = PrivilegedActivationRevocationCommandEvidence.compose(
        actor_principal_id=SUPERVISOR,
        actor_permission_id=PRIVILEGED_ACTIVATION_REVOKE_PERMISSION,
        actor_permission_assignment_id=supervisor.assignment_id,
        actor_permission_assignment_revision=supervisor.revision,
        actor_permission_assignment_fingerprint=(
            supervisor.assignment_fingerprint
        ),
        target_activation_id=issued.activation.activation_id,
        target_principal_id=PRINCIPAL,
        target_class=PrivilegedTargetClass.PLATFORM_SYSTEM_ROOT.value,
        target_tenant_id=None,
        revocation_reason_reference="p8-break-glass-contained",
        authorized_at=NOW + timedelta(minutes=1),
        idempotency_key="p8-break-glass-revoke",
    )

    with context["client"].start_session() as session:
        with session.start_transaction():
            revoked = _revocation_service(context).revoke(
                command,
                session=session,
            )

    assert revoked.activation.status.value == "REVOKED"

    with context["client"].start_session() as session:
        session.start_transaction()

        with pytest.raises(
            PrivilegedBreakGlassServiceError,
            match="TERMINAL_ACTIVATION_REPLAY_FORBIDDEN",
        ):
            service.issue_interactive(
                requester_principal_id=PRINCIPAL,
                approver_principal_id=APPROVER,
                tenant_id=None,
                requester_proof_tenant_id=PROOF_TENANT,
                requester_proof_reference=PROOF_REFERENCE,
                approver_proof_tenant_id=PROOF_TENANT,
                approver_proof_reference="proof-ref-p7-approver",
                eligibility_evidence_id=ELIGIBILITY_ID,
                reason_reference="p8-break-glass-opaque",
                effective_until=NOW + timedelta(minutes=10),
                idempotency_key="p8-break-glass",
                session=session,
            )

        session.abort_transaction()

    assert (
        context["database"][
            "privileged_break_glass_command_evidence"
        ].count_documents({})
        == 1
    )


def test_real_current_permission_revocation_cuts_off_downstream_authority(
    context: dict[str, Any],
) -> None:
    """
    Certify that terminal SYSTEM permission state is immediately authoritative.

    Historic assignment possession must not authorize a later privileged command.
    """

    _seed(
        context,
        include_permission=False,
    )

    assignment = _d12_assign(
        context,
        target_principal_id=PRINCIPAL,
        permission_id=PRIVILEGED_ACTIVATION_ISSUE_PERMISSION,
        evidence_reference="p8-cutoff-assign",
        idempotency_key="p8-cutoff-assign",
    )

    possession = _possession(context)

    assert possession.resolve(
        principal_id=PRINCIPAL,
        permission_id=PRIVILEGED_ACTIVATION_ISSUE_PERMISSION,
    ) is not None

    revoked = _d12_revoke(
        context,
        assignment=assignment,
        target_principal_id=PRINCIPAL,
        permission_id=PRIVILEGED_ACTIVATION_ISSUE_PERMISSION,
        evidence_reference="p8-cutoff-revocation",
        idempotency_key="p8-cutoff-revoke",
    )

    assert revoked.status.value == "REVOKED"

    assert possession.resolve(
        principal_id=PRINCIPAL,
        permission_id=PRIVILEGED_ACTIVATION_ISSUE_PERMISSION,
    ) is None

    with context["client"].start_session() as session:
        session.start_transaction()

        with pytest.raises(
            PrivilegedActivationIssuanceError,
            match="ISSUANCE_PERMISSION_NOT_CURRENT",
        ):
            context["issuance_service"].issue_interactive(
                tenant_id=None,
                eligibility_evidence_id=ELIGIBILITY_ID,
                proof_tenant_id=PROOF_TENANT,
                proof_reference=PROOF_REFERENCE,
                issuance_idempotency_key="p8-cutoff-denied",
                session=session,
            )

        session.abort_transaction()

    assert (
        context["activation_collection"].count_documents(
            {"issuance_idempotency_key": "p8-cutoff-denied"}
        )
        == 0
    )


def test_real_p8_certificate_creates_no_adjacent_authority(
    context: dict[str, Any],
) -> None:
    """Certify P8 is composition evidence only."""

    collections = set(
        context["database"].list_collection_names()
    )

    assert not (
        {
            "payments",
            "refunds",
            "settlements",
            "payouts",
            "subscriptions",
            "break_glass_override",
            "autonomous_override",
        }
        & collections
    )


# =============================================================================
# WILSY OS SOVEREIGN ARTIFACT CERTIFICATION SEAL
# =============================================================================
# ARTIFACT: test_privileged_iam_end_to_end_real_mongo.py
# VERSION: v1.0.0-P8-PRIVILEGED-IAM-END-TO-END-REAL-MONGO
# SCOPE: D12 -> P4 -> P5 -> P6 and D12 -> P7 -> P6 composed real-Mongo proof
# TRANSACTION OWNERSHIP: caller-owned explicit active transaction per command
# NEW PRODUCTION AUTHORITY: NONE
# NEW PERMISSION: NONE
# NEW ROLE: NONE
# HTTP AUTHORITY: NONE
# AUTONOMOUS OVERRIDE AUTHORITY: NONE
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively
# END OF WILSY OS SOVEREIGN ARTIFACT
