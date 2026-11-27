"""TITLE: WILSY OS Canonical Founder HR Activation Operator
VERSION: v1.1.0-OPTIONAL-FOUNDER-HR-DIRECTOR-BOOTSTRAP
AUTHORITY: Owner-password/TOTP authenticated local Python EOS orchestration.
EPITOME: Issue canonical R0 HR entitlement and an independently delegated HR
         Manager role plus active business capacity using source-owned commands.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tools/eos/ops/founder_hr_activation.py
COLLABORATION / OWNERSHIP: AuthRegistry authenticates; D22B3 issues entitlement;
                            invitation authorities issue/consume roles; multi
                            business-role repository owns capacity history.
CERTIFICATION / UPDATE DATE: 2026-11-27
CHANGELOG: v1.1.0-OPTIONAL-FOUNDER-HR-DIRECTOR-BOOTSTRAP adds a separate, explicitly requested Founder HR Director invitation and multi-capacity issuance with fresh Owner/MFA verification; independent decisions and employee admission remain separate.
           v1.0.1-STABLE-HR-OPERATOR-DENIAL-CODES preserves safe typed issuer and local-auth denial codes instead of collapsing every failure into an opaque generic error.
           v1.0.0-BOUNDED-FOUNDER-HR-ACTIVATION composes owner-authenticated,
           development-only HR entitlement, invitation-based HR_MANAGER role
           and separately versioned tenant_hr_manager capacity issuance.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2.
SECURITY / PRIVACY POSTURE: Password/TOTP entered locally and never printed.
                           No principal identifiers, token or personnel data on stdout.
TENANT BOUNDARY: WILSYTENANT-4CD2FZ4O only; no fallback aliases.
AUTHORITY BOUNDARY: No Founder-title bypass, HR_DIRECTOR, employee admission,
                    payroll execution, independent approval or wildcard grants.
TRANSACTION BOUNDARY: Existing issuer and repositories own participant writes;
                      caller owns whole entitlement/capacity Mongo transactions.
FINANCIAL AUTHORITY BOUNDARY: Kennel EOS exclusively.
FAIL-CLOSED POSTURE: Identity, Founder state, owner role, membership, source
                     subscription and role mismatches reject before protected writes.
"""
from __future__ import annotations

import argparse
from datetime import datetime, timedelta, timezone
import json
import os
from typing import Any, Final, Sequence

from tools.eos.auth.identity import SovereignIdentity
from tools.eos.auth.invitation_creation import create_invitation
from tools.eos.auth.invited_member_admission import admit_invited_member
from tools.eos.auth.principal_authority_repository import PrincipalAuthorityRepository
from tools.eos.auth.principal_status import PrincipalStatus
from tools.eos.auth.role_assignment import RoleAssignmentStatus
from tools.eos.auth.role_assignment_repository import (
    RoleAssignmentNotFoundError,
    RoleAssignmentRepository,
)
from tools.eos.auth.tenant_authorization_decision_evidence_registry import (
    TenantAuthorizationDecisionEvidenceRegistry,
)
from tools.eos.auth.tenant_business_role import (
    TenantBusinessRoleAuthority,
    TenantBusinessRoleStatus,
)
from tools.eos.auth.tenant_business_role_repository import TenantBusinessRoleRepository
from tools.eos.auth.tenant_membership import TenantMembershipStatus
from tools.eos.auth.tenant_membership_repository import TenantMembershipRepository
from tools.eos.auth.workspace_bootstrap_projection import WILSY_COMPANY_TENANT_ID
from tools.eos.saas.auth.auth_registry import AuthRegistry
from tools.eos.saas.entitlement.product_catalogue import TenantProductId
from tools.eos.saas.entitlement.tenant_product_entitlement_composer import (
    derive_tenant_product_entitlement_id,
)
from tools.eos.saas.entitlement.tenant_product_entitlement_issuance_orchestrator import (
    issue_tenant_product_entitlement,
)
from tools.eos.saas.entitlement.tenant_product_entitlement_registry import (
    CURRENT_COLLECTION,
    HISTORY_COLLECTION,
    ensure_indexes as ensure_entitlement_indexes,
    get_current,
)
from tools.eos.saas.domain.tenant_product_entitlement import TenantProductEntitlementState
from tools.eos.ops.founder_hr_iam_preflight import inspect_founder_hr_prerequisites

VERSION: Final[str] = "v1.1.0-OPTIONAL-FOUNDER-HR-DIRECTOR-BOOTSTRAP"
_IDEMPOTENCY_KEY: Final[str] = "founder-hr-r0-activation-v1"
_ALLOWED_ENV: Final[frozenset[str]] = frozenset({"development", "dev", "local", "test", "testing"})
_ENABLE_ENV: Final[str] = "WILSY_FOUNDER_HR_ACTIVATION"
_TRUE: Final[frozenset[str]] = frozenset({"1", "true", "yes"})


class FounderHRActivationError(RuntimeError):
    """Secret-free denial; no partial stage can assert verified browser access."""


def _require_active_owner(identity: SovereignIdentity, db: Any, *,
                          session: Any) -> None:
    """Recheck authenticated owner and source Founder evidence in transaction."""
    if (identity.tenant_id != WILSY_COMPANY_TENANT_ID
            or identity.status is not PrincipalStatus.ACTIVE):
        raise FounderHRActivationError("FOUNDER_HR_OWNER_IDENTITY_DENIED")
    principal = PrincipalAuthorityRepository.resolve(
        identity.identity_id, db["principal_authorities"], session=session,
    )
    membership = TenantMembershipRepository.resolve(
        identity.identity_id, identity.tenant_id,
        db["tenant_memberships"], session=session,
    )
    owner = TenantBusinessRoleRepository.resolve(
        identity.identity_id, identity.tenant_id,
        db["tenant_business_roles"], session=session,
    )
    admin = RoleAssignmentRepository.resolve(
        identity.identity_id, identity.tenant_id, "ENTERPRISE_ADMIN",
        db["role_assignments"], session=session,
    )
    if (principal.status is not PrincipalStatus.ACTIVE
            or membership.status is not TenantMembershipStatus.ACTIVE
            or owner.status is not TenantBusinessRoleStatus.ACTIVE
            or owner.business_role != "tenant_owner"
            or admin.status is not RoleAssignmentStatus.ACTIVE):
        raise FounderHRActivationError("FOUNDER_HR_DURABLE_OWNER_AUTHORITY_DENIED")
    founders = list(db["institutional_principal_designations"].find(
        {"tenant_id": identity.tenant_id, "designation": "Founder"},
        {"_id": 0, "principal_id": 1, "state": 1, "business_role": 1,
         "grants_permissions": 1},
        session=session,
    ).limit(2))
    if (len(founders) != 1 or founders[0].get("principal_id") != identity.identity_id
            or founders[0].get("state") != "ACTIVE"
            or founders[0].get("business_role") != "tenant_owner"
            or founders[0].get("grants_permissions") is not False):
        raise FounderHRActivationError("FOUNDER_HR_DESIGNATION_DENIED")


def _issue_hr_entitlement(identity: SovereignIdentity, client: Any, db: Any) -> None:
    """Issue or replay one D22B3 entitlement with same-session audit evidence."""
    evidence = TenantAuthorizationDecisionEvidenceRegistry(
        db["tenant_authorization_decision_evidence"],
        principal_repository=PrincipalAuthorityRepository,
    )
    evidence.ensure_indexes()
    ensure_entitlement_indexes(db[HISTORY_COLLECTION], db[CURRENT_COLLECTION])
    entitlement_id = derive_tenant_product_entitlement_id(identity.tenant_id, TenantProductId.HR)
    with client.start_session() as session:
        def callback(tx: Any) -> None:
            _require_active_owner(identity, db, session=tx)
            issue_tenant_product_entitlement(
                identity=identity,
                product_id=TenantProductId.HR,
                idempotency_key=_IDEMPOTENCY_KEY,
                occurred_at=datetime.now(timezone.utc),
                subscription_collection=db["subscriptions"],
                entitlement_history_collection=db[HISTORY_COLLECTION],
                entitlement_current_collection=db[CURRENT_COLLECTION],
                authorization_evidence_registry=evidence,
                session=tx,
            )
            current = get_current(
                identity.tenant_id, entitlement_id,
                db[HISTORY_COLLECTION], db[CURRENT_COLLECTION], session=tx,
            )
            if (current.product_id is not TenantProductId.HR
                    or current.lifecycle_state is not TenantProductEntitlementState.ACTIVE):
                raise FounderHRActivationError("FOUNDER_HR_ENTITLEMENT_NOT_ACTIVE")
        session.with_transaction(callback)


def _activate_manager_assignment(identity: SovereignIdentity, db: Any) -> None:
    """Use existing invitation issuance and acceptance, never raw role writes."""
    try:
        existing = RoleAssignmentRepository.resolve(
            identity.identity_id, identity.tenant_id,
            "HR_MANAGER", db["role_assignments"],
        )
    except RoleAssignmentNotFoundError:
        existing = None
    if existing is not None:
        if existing.status is not RoleAssignmentStatus.ACTIVE:
            raise FounderHRActivationError("FOUNDER_HR_ROLE_CONFLICT")
        return
    invitation = create_invitation(
        identity=identity,
        tenant_id=identity.tenant_id,
        recipient_principal_id=identity.identity_id,
        authorization_role_id="HR_MANAGER",
        expires_at=datetime.now(timezone.utc) + timedelta(minutes=10),
    )
    # The one-time capability remains in memory; the source stores its digest.
    admit_invited_member(
        identity=identity,
        invitation_id=invitation.invitation.invitation_id,
        capability=invitation.capability,
    )
    granted = RoleAssignmentRepository.resolve(
        identity.identity_id, identity.tenant_id,
        "HR_MANAGER", db["role_assignments"],
    )
    if granted.status is not RoleAssignmentStatus.ACTIVE:
        raise FounderHRActivationError("FOUNDER_HR_ROLE_READBACK_FAILED")


def _activate_manager_capacity(identity: SovereignIdentity, client: Any, db: Any) -> None:
    """Append capacity history + current projection under active Owner/HR role."""
    TenantBusinessRoleRepository.ensure_multi_capacity_indexes(db)
    with client.start_session() as session:
        def callback(tx: Any) -> None:
            _require_active_owner(identity, db, session=tx)
            assigned = RoleAssignmentRepository.resolve(
                identity.identity_id, identity.tenant_id,
                "HR_MANAGER", db["role_assignments"], session=tx,
            )
            if assigned.status is not RoleAssignmentStatus.ACTIVE:
                raise FounderHRActivationError("FOUNDER_HR_ROLE_REQUIRED")
            current = db["tenant_business_role_assignments"].find_one(
                {"principal_id": identity.identity_id, "tenant_id": identity.tenant_id,
                 "business_role": "tenant_hr_manager"},
                {"_id": 0, "status": 1},
                session=tx,
            )
            if current is not None:
                if current.get("status") != "ACTIVE":
                    raise FounderHRActivationError("FOUNDER_HR_CAPACITY_CONFLICT")
                return
            capacity = TenantBusinessRoleAuthority(
                principal_id=identity.identity_id,
                tenant_id=identity.tenant_id,
                business_role="tenant_hr_manager",
                status=TenantBusinessRoleStatus.ACTIVE,
                revision=0,
                effective_at=datetime.now(timezone.utc),
                revoked_at=None,
            )
            TenantBusinessRoleRepository.record_capacity_revision(
                capacity, None, db, session=tx,
            )
        session.with_transaction(callback)


def _activate_director_assignment(identity: SovereignIdentity, db: Any) -> None:
    """Admit only a self-bound Founder HR Director invitation under existing IAM."""
    _activate_role_assignment(identity, db, "HR_DIRECTOR")


def _activate_role_assignment(identity: SovereignIdentity, db: Any, role_id: str) -> None:
    """Use institutional invitation issue/accept with exact active-role replay."""
    if role_id not in ("HR_MANAGER", "HR_DIRECTOR"):
        raise FounderHRActivationError("FOUNDER_HR_ROLE_NOT_SUPPORTED")
    try:
        existing = RoleAssignmentRepository.resolve(
            identity.identity_id, identity.tenant_id, role_id, db["role_assignments"],
        )
    except RoleAssignmentNotFoundError:
        existing = None
    if existing is not None:
        if existing.status is not RoleAssignmentStatus.ACTIVE:
            raise FounderHRActivationError("FOUNDER_HR_ROLE_CONFLICT")
        return
    invitation = create_invitation(
        identity=identity, tenant_id=identity.tenant_id,
        recipient_principal_id=identity.identity_id, authorization_role_id=role_id,
        expires_at=datetime.now(timezone.utc) + timedelta(minutes=10),
    )
    admit_invited_member(
        identity=identity, invitation_id=invitation.invitation.invitation_id,
        capability=invitation.capability,
    )
    granted = RoleAssignmentRepository.resolve(
        identity.identity_id, identity.tenant_id, role_id, db["role_assignments"],
    )
    if granted.status is not RoleAssignmentStatus.ACTIVE:
        raise FounderHRActivationError("FOUNDER_HR_ROLE_READBACK_FAILED")


def _activate_director_capacity(identity: SovereignIdentity, client: Any, db: Any) -> None:
    """Write separate HR Director capacity history only after exact authority."""
    TenantBusinessRoleRepository.ensure_multi_capacity_indexes(db)
    with client.start_session() as session:
        def callback(tx: Any) -> None:
            _require_active_owner(identity, db, session=tx)
            assigned = RoleAssignmentRepository.resolve(
                identity.identity_id, identity.tenant_id,
                "HR_DIRECTOR", db["role_assignments"], session=tx,
            )
            if assigned.status is not RoleAssignmentStatus.ACTIVE:
                raise FounderHRActivationError("FOUNDER_HR_DIRECTOR_ROLE_REQUIRED")
            current = db["tenant_business_role_assignments"].find_one(
                {"principal_id": identity.identity_id, "tenant_id": identity.tenant_id,
                 "business_role": "tenant_hr_director"},
                {"_id": 0, "status": 1}, session=tx,
            )
            if current is not None:
                if current.get("status") != "ACTIVE":
                    raise FounderHRActivationError("FOUNDER_HR_DIRECTOR_CAPACITY_CONFLICT")
                return
            capacity = TenantBusinessRoleAuthority(
                principal_id=identity.identity_id,
                tenant_id=identity.tenant_id,
                business_role="tenant_hr_director",
                status=TenantBusinessRoleStatus.ACTIVE,
                revision=0,
                effective_at=datetime.now(timezone.utc),
                revoked_at=None,
            )
            TenantBusinessRoleRepository.record_capacity_revision(
                capacity, None, db, session=tx,
            )
        session.with_transaction(callback)


def activate_founder_hr(
    identity: SovereignIdentity, client: Any, db: Any, *,
    activate_director: bool = False,
) -> dict[str, object]:
    """Perform governed stages and return no PII or false browser attestation.

    Partial durable stages can safely be resumed: entitlement uses source
    idempotency, invitation is skipped for an existing active assignment, and
    capacity history is inserted exactly once.
    """
    if identity.tenant_id != WILSY_COMPANY_TENANT_ID:
        raise FounderHRActivationError("FOUNDER_HR_TENANT_DENIED")
    _issue_hr_entitlement(identity, client, db)
    _activate_manager_assignment(identity, db)
    _activate_manager_capacity(identity, client, db)
    if activate_director:
        # Separate delegation and role: Director is not automatically inferred
        # from the Founder designation or the HR Manager activation.
        _activate_director_assignment(identity, db)
        _activate_director_capacity(identity, client, db)
    current = inspect_founder_hr_prerequisites(db, identity.tenant_id)
    if not current.get("hr_manager_capacity_active") or not current.get(
        "hr_manager_authorization_role_active"
    ):
        raise FounderHRActivationError("FOUNDER_HR_IAM_READBACK_FAILED")
    if activate_director and (
        not current.get("hr_director_capacity_active")
        or not current.get("hr_director_authorization_role_active")
    ):
        raise FounderHRActivationError("FOUNDER_HR_DIRECTOR_IAM_READBACK_FAILED")
    return {
        "schema": "WILSY-FOUNDER-HR-ACTIVATION/V1",
        "tenant": "CANONICAL_WILSY_EMPLOYER",
        "entitlement": "ACTIVE_TRANSACTIONAL_READBACK",
        "hr_manager_role": "ACTIVE_DURABLE_READBACK",
        "hr_manager_capacity": "ACTIVE_DURABLE_READBACK",
        "founder_owner_preserved": bool(current.get("tenant_owner_capacity_active")),
        "employee_admission": "NOT_ISSUED",
        "hr_director": "ACTIVE_DURABLE_READBACK" if activate_director else "NOT_ISSUED",
        "independent_self_approval": "NOT_AUTHORIZED",
        "next": "REAUTHENTICATE_AND_VERIFY_FOUR_HR_ROUTES",
        "authenticated_http_verified": False,
    }


def main(argv: Sequence[str] | None = None) -> int:
    """Run only in explicitly enabled non-production with local owner+TOTP."""
    parser = argparse.ArgumentParser(description="Governed canonical Founder HR activation")
    parser.add_argument("--tenant-id", required=True)
    parser.add_argument("--apply", action="store_true")
    parser.add_argument("--activate-director", action="store_true", help="Separately request transitional Founder HR Director IAM authority")
    args = parser.parse_args(argv)
    if args.tenant_id != WILSY_COMPANY_TENANT_ID:
        parser.error("Canonical Wilsy employer only")
    from tools.eos.kernel.db import connect_db, disconnect_db, get_client, get_database
    if args.activate_director and not args.apply:
        parser.error("--activate-director requires --apply and authenticated local Owner")
    if not args.apply:
        from tools.eos.ops.founder_hr_iam_preflight import main as preflight_main
        return preflight_main(["--tenant-id", args.tenant_id])
    if (os.getenv("ENV", "").strip().lower() not in _ALLOWED_ENV
            or os.getenv(_ENABLE_ENV, "").strip().lower() not in _TRUE):
        print(json.dumps({"status": "FOUNDER_HR_OPERATOR_ENVIRONMENT_DENIED"}))
        return 3
    connected = False
    try:
        success, _ = connect_db()
        if not success:
            raise FounderHRActivationError("FOUNDER_HR_DATABASE_UNAVAILABLE")
        connected = True
        db, client = get_database(), get_client()
        if db is None or client is None:
            raise FounderHRActivationError("FOUNDER_HR_DATABASE_UNAVAILABLE")
        from tools.eos.cli.developer_persona import _authenticate_owner
        identity = _authenticate_owner(
            registry=AuthRegistry(), tenant_id=args.tenant_id,
        )
        # A preflight is not itself the source of authorization.
        report = activate_founder_hr(identity, client, db, activate_director=args.activate_director)
        print(json.dumps(report, sort_keys=True))
        return 0
    except Exception as error:
        # Only typed, bounded institutional codes may escape to stdout.
        bounded = getattr(error, "code", None)
        if isinstance(error, FounderHRActivationError):
            code = str(error)
        elif isinstance(bounded, str) and bounded.isascii() and bounded.replace("_", "").isalnum():
            code = bounded
        else:
            code = "FOUNDER_HR_ACTIVATION_DENIED_OR_UNAVAILABLE"
        print(json.dumps({"status": code, "authenticated_http_verified": False}))
        return 2
    finally:
        if connected:
            disconnect_db()


if __name__ == "__main__":
    raise SystemExit(main())

# ARTIFACT: tools/eos/ops/founder_hr_activation.py
# VERSION: v1.1.0-OPTIONAL-FOUNDER-HR-DIRECTOR-BOOTSTRAP
# AUTHORITY BOUNDARY: Local owner-authenticated orchestration of existing governed sources only.
# TENANT POSTURE: Canonical Wilsy employer; no customer, global root or alias fallback.
# FAIL-CLOSED POSTURE: No unverified stage is reported as authenticated EOS HR access.
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively.
# END OF WILSY OS SOVEREIGN ARTIFACT
