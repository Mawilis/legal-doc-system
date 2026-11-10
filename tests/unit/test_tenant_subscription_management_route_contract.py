"""Certify the protected tenant subscription-management browser entry.

The browser role projection is presentation-only. Python EOS retains final
subscription, IAM, entitlement and tenant-scope authority.
"""

from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def test_billing_route_is_protected_by_canonical_tenant_business_roles():
    source = (ROOT / "client/src/App.jsx").read_text()
    start = source.index("const ProtectedBillingRoute")
    end = source.index("const SovereignRouter", start)
    guard = source[start:end]

    for role in ("TENANT_OWNER", "TENANT_ADMIN", "TENANT_MANAGER"):
        assert role in guard

    assert "return <Navigate to=\"/\" replace />" in guard
    assert "Python-EOS" in guard
    assert 'path="/billing"' in source
    assert "<BillingHUD user={user} />" in source


def test_subscription_tab_is_visible_to_tenant_subscription_admin_roles_only():
    source = (ROOT / "client/src/utils/billingCapabilities.js").read_text()

    assert (
        "const isTenantSubscriptionAdmin = "
        "['TENANT_OWNER', 'TENANT_ADMIN', 'TENANT_MANAGER'].includes(role);"
    ) in source
    assert (
        "viewSubscriptions: isFinance || isSovereign || isTenantSubscriptionAdmin,"
    ) in source
    assert "viewPayables: isFinance || isSovereign," in source
    assert "managePlans: isSovereign," in source


def test_specialized_legal_partner_role_does_not_gain_subscription_management():
    source = (ROOT / "client/src/utils/billingCapabilities.js").read_text()
    assert "'TENANT_LEGAL_PARTNER'" not in source
    assert "'LEGAL_PARTNER'" not in source

    authority = (ROOT / "tools/eos/auth/tenant_authority_policy.py").read_text()
    assert '"subscription_upgrade": ELIGIBLE' in authority
    assert '"tenant_legal_partner"' not in authority.split('"tenant_owner":', 1)[1].split('}),', 1)[0]
