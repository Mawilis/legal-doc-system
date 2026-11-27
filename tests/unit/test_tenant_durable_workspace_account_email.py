"""TITLE: WILSY OS Tenant Durable Workspace Account Email Certificate.
VERSION: v1.0.0-TENANT-EMAIL-SOURCE-CERT
AUTHORITY: Python EOS authenticated workspace source boundary.
EPITOME: Certifies tenant-session email is read from exact durable identity,
    never from bearer metadata or a login-email compatibility fallback.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tests/unit/test_tenant_durable_workspace_account_email.py
COLLABORATION / OWNERSHIP: Authentication router, canonical AuthRegistry and workspace bootstrap.
CERTIFICATION / UPDATE DATE: 2026-11-27
CHANGELOG: v1.0.0-TENANT-EMAIL-SOURCE-CERT proves current principal/tenant identity binding,
    missing identity, malformed email and unavailable canonical identity fail closed.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2; ISO 27001.
SECURITY / PRIVACY POSTURE: Synthetic values only; no live emails, credentials or tokens.
TENANT BOUNDARY: Exact principal and tenant match required before account email disclosure.
AUTHORITY BOUNDARY: Read-only projection certificate; creates no grants or sessions.
FINANCIAL AUTHORITY BOUNDARY: No financial execution; Kennel EOS remains exclusive.
"""

from types import SimpleNamespace

import pytest

from tools.eos.api import auth_router
from tools.eos.auth.workspace_bootstrap_projection import (
    WorkspaceBootstrapProjectionError,
)


def _identity():
    """Return one synthetic legacy session with misleading JWT email metadata."""
    return SimpleNamespace(
        principal_scope="TENANT", email="untrusted-display@example.invalid",
    )


def _projection():
    """Return the independently validated exact principal/tenant projection."""
    return SimpleNamespace(principal_id="synthetic-principal", tenant_id="synthetic-tenant", email=None)


def _install_registry(monkeypatch, *, user=None, error=None):
    """Bind a synthetic exact-source registry; never touch persistence."""
    def read(principal_id):
        assert principal_id == "synthetic-principal"
        if error is not None:
            raise error
        return user

    monkeypatch.setattr(
        auth_router, "get_auth_registry",
        lambda _scope: SimpleNamespace(get_user_by_id=read),
    )


def test_legacy_workspace_email_uses_durable_exact_principal_and_tenant(monkeypatch):
    """Only durable user email may appear as the account email."""
    _install_registry(monkeypatch, user=SimpleNamespace(
        id="synthetic-principal", tenantId="synthetic-tenant",
        email="canonical@example.invalid",
    ))
    assert auth_router._workspace_durable_account_email(
        _identity(), _projection(),
    ) == "canonical@example.invalid"


@pytest.mark.parametrize("user", [
    None,
    SimpleNamespace(id="other-principal", tenantId="synthetic-tenant", email="other@example.invalid"),
    SimpleNamespace(id="synthetic-principal", tenantId="other-tenant", email="other@example.invalid"),
    SimpleNamespace(id="synthetic-principal", tenantId="synthetic-tenant", email=None),
    SimpleNamespace(id="synthetic-principal", tenantId="synthetic-tenant", email=" "),
])
def test_legacy_workspace_email_rejects_missing_mismatched_or_invalid_identity(monkeypatch, user):
    """Source ambiguity never permits fallback to JWT sign-in email."""
    _install_registry(monkeypatch, user=user)
    with pytest.raises(
        WorkspaceBootstrapProjectionError,
        match="WORKSPACE_BOOTSTRAP_PRINCIPAL_EMAIL_INVALID",
    ):
        auth_router._workspace_durable_account_email(_identity(), _projection())


def test_legacy_workspace_email_reports_source_outage_without_fallback(monkeypatch):
    """Transport/source failure cannot turn sign-in metadata into account authority."""
    _install_registry(monkeypatch, error=RuntimeError("synthetic source outage"))
    with pytest.raises(
        WorkspaceBootstrapProjectionError,
        match="WORKSPACE_BOOTSTRAP_PRINCIPAL_EMAIL_UNAVAILABLE",
    ):
        auth_router._workspace_durable_account_email(_identity(), _projection())


# ARTIFACT: tests/unit/test_tenant_durable_workspace_account_email.py
# VERSION: v1.0.0-TENANT-EMAIL-SOURCE-CERT
# AUTHORITY BOUNDARY: Source-bound read-only certification; no IAM or authentication writes.
# TENANT POSTURE: Exact synthetic principal/tenant alignment or denial.
# FAIL-CLOSED POSTURE: No JWT, login email or other tenant fallback.
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively owns financial execution.
# END OF WILSY OS SOVEREIGN ARTIFACT
