"""Unit certificate for the Issue #300 owner-genesis fail-closed boundary.

TITLE: Tenant-owner bootstrap ownership-evidence block certificate
VERSION: v1.3.0-ISSUE-300-OWNERSHIP-EVIDENCE-BLOCK-CERT
AUTHORITY: Verify that no deployment provisioner can receive tenant ownership
           without independent legal-entity ownership evidence.
EPITOME: Prove stable denial precedes all database, principal, tenant, IAM,
         membership and business-role activity.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tests/unit/test_tenant_owner_bootstrap.py
COLLABORATION / OWNERSHIP: Certificate for tools/eos/auth/tenant_owner_bootstrap.py
                            v1.0.3-ISSUE-300-OWNERSHIP-EVIDENCE-BLOCK.
CERTIFICATION / UPDATE DATE: 2026-11-02
CHANGELOG: 2026-11-02 v1.3.0-ISSUE-300-OWNERSHIP-EVIDENCE-BLOCK exercises the real deployment pretenant allowlist parser and proves a non-allowlisted identity is rejected before the ownership-authority denial.
CHANGELOG: 2026-11-02 v1.2.0-ISSUE-300-OWNERSHIP-EVIDENCE-BLOCK certifies stable denial after pretenant verification and zero downstream persistence or repository access.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2.
SECURITY / PRIVACY POSTURE: Synthetic identity and tenant values only.
TENANT BOUNDARY: The requested tenant value is never persisted or disclosed.
AUTHORITY BOUNDARY: Deployment request authority is not ownership evidence.
FINANCIAL AUTHORITY BOUNDARY: No financial or Kennel execution authority.
"""
from __future__ import annotations

import inspect
from typing import Any

import pytest

from tools.eos.auth.identity import SovereignIdentity
from tools.eos.auth.pretenant_bootstrap_authority import (
    PretenantBootstrapAuthorityError,
    PretenantBootstrapAuthorityDenialCode,
)
from tools.eos.auth.principal_status import PrincipalStatus
from tools.eos.auth.tenant_owner_bootstrap import (
    TENANT_OWNER_BOOTSTRAP_VERSION,
    TenantOwnerBootstrapDenialCode,
    TenantOwnerBootstrapError,
    bootstrap_tenant_owner,
)
from tools.eos.saas.domain.tenant import (
    OrganizationProfile,
    SubscriptionPlan,
    TenantEntity,
)


VERSION = "v1.3.0-ISSUE-300-OWNERSHIP-EVIDENCE-BLOCK-CERT"


def _identity(**overrides: Any) -> SovereignIdentity:
    """Build one synthetic principal whose claims cannot establish ownership."""
    values: dict[str, Any] = {
        "identity_id": "principal-synthetic",
        "tenant_id": "caller-selected-tenant",
        "username": "owner@example.invalid",
        "email": "owner@example.invalid",
        "roles": ["OWNER", "ENTERPRISE_ADMIN"],
        "permissions": ["*"],
        "auth_method": "token",
        "status": PrincipalStatus.ACTIVE,
    }
    values.update(overrides)
    return SovereignIdentity(**values)


def _tenant() -> TenantEntity:
    """Build one synthetic tenant with caller-supplied identity attributes."""
    return TenantEntity(
        organization=OrganizationProfile(
            "Synthetic Legal Entity",
            "legal",
            SubscriptionPlan.ENTERPRISE,
            "Synthetic Legal Entity Ltd",
            "REG-123",
            "owner@example.invalid",
            ["ZA"],
        ),
        tenant_id="tenant-synthetic",
        verified=True,
    )


def test_authorized_provisioner_is_denied_before_any_persistence(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """A deployment allowlist entry is not legal-entity ownership evidence."""
    events: list[str] = []
    monkeypatch.setattr(
        "tools.eos.auth.tenant_owner_bootstrap.verify_pretenant_bootstrap_authority",
        lambda _identity: events.append("pretenant-verified"),
    )

    def forbidden_database_access() -> object:
        events.append("database-access")
        raise AssertionError("ownership denial must precede database access")

    monkeypatch.setattr(
        "tools.eos.auth.tenant_owner_bootstrap.get_client",
        forbidden_database_access,
        raising=False,
    )

    with pytest.raises(TenantOwnerBootstrapError) as raised:
        bootstrap_tenant_owner(identity=_identity(), tenant=_tenant())

    assert raised.value.code is (
        TenantOwnerBootstrapDenialCode.OWNERSHIP_EVIDENCE_AUTHORITY_UNAVAILABLE
    )
    assert str(raised.value) == "OWNERSHIP_EVIDENCE_AUTHORITY_UNAVAILABLE"
    assert events == ["pretenant-verified"]


def test_untrusted_pretenant_request_is_rejected_before_ownership_block(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Existing deployment-rooted request gate remains first and fail-closed."""
    monkeypatch.setattr(
        "tools.eos.auth.tenant_owner_bootstrap.verify_pretenant_bootstrap_authority",
        lambda _identity: (_ for _ in ()).throw(
            PretenantBootstrapAuthorityError(
                PretenantBootstrapAuthorityDenialCode.MALFORMED_IDENTITY
            )
        ),
    )
    with pytest.raises(PretenantBootstrapAuthorityError):
        bootstrap_tenant_owner(identity=_identity(), tenant=_tenant())


def test_actual_pretenant_allowlist_rejects_nonprovisioner(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """The deployed environment allowlist remains the first request gate."""
    monkeypatch.setenv(
        "WILSY_PRETENANT_TENANT_PROVISIONER_PRINCIPAL_IDS",
        '["different-provisioner"]',
    )

    with pytest.raises(PretenantBootstrapAuthorityError) as raised:
        bootstrap_tenant_owner(identity=_identity(), tenant=_tenant())

    assert raised.value.code is (
        PretenantBootstrapAuthorityDenialCode.PRINCIPAL_NOT_PROVISIONER
    )


def test_claims_and_verified_tenant_flag_do_not_bypass_missing_owner_authority(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """JWT-like roles, wildcard permissions and tenant.verified are not proof."""
    monkeypatch.setattr(
        "tools.eos.auth.tenant_owner_bootstrap.verify_pretenant_bootstrap_authority",
        lambda _identity: None,
    )
    privileged_identity = _identity(
        tenant_id="tenant-synthetic",
        roles=["tenant_owner"],
        permissions=["tenant:*"],
    )
    with pytest.raises(TenantOwnerBootstrapError) as raised:
        bootstrap_tenant_owner(identity=privileged_identity, tenant=_tenant())
    assert raised.value.code is (
        TenantOwnerBootstrapDenialCode.OWNERSHIP_EVIDENCE_AUTHORITY_UNAVAILABLE
    )


def test_public_contract_and_version_are_frozen() -> None:
    """Keep a stable command signature and exact public denial vocabulary."""
    assert TENANT_OWNER_BOOTSTRAP_VERSION == (
        "v1.0.3-ISSUE-300-OWNERSHIP-EVIDENCE-BLOCK"
    )
    assert VERSION == "v1.3.0-ISSUE-300-OWNERSHIP-EVIDENCE-BLOCK-CERT"
    assert list(inspect.signature(bootstrap_tenant_owner).parameters) == [
        "identity",
        "tenant",
    ]
    assert (
        TenantOwnerBootstrapDenialCode.OWNERSHIP_EVIDENCE_AUTHORITY_UNAVAILABLE.value
        == "OWNERSHIP_EVIDENCE_AUTHORITY_UNAVAILABLE"
    )


# ARTIFACT: test_tenant_owner_bootstrap.py
# VERSION: v1.3.0-ISSUE-300-OWNERSHIP-EVIDENCE-BLOCK-CERT
# AUTHORITY BOUNDARY: unit evidence only; no tenant ownership authority
# TENANT POSTURE: synthetic identities only; no persistence
# FAIL-CLOSED POSTURE: ownership verifier absence denies before database access
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS remains exclusive
# END OF WILSY OS SOVEREIGN ARTIFACT
