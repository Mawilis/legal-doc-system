"""TITLE: WILSY OS Practitioner Binding Provisioning Security Certificate.
VERSION: v1.0.0-P47-R76-PROVISIONING-SECURITY-CERTIFICATE
AUTHORITY: Direct admission, IAM composition and zero-authority tests.
EPITOME: Proves fail-closed inputs, caller-owned transaction admission,
    exact Partner authorization composition and absence of content authority.
ABSOLUTE CANONICAL PATH:
    /Users/wilsonkhanyezi/legal-doc-system/tests/unit/test_legal_practitioner_matter_binding_provisioning_service.py
COLLABORATION / OWNERSHIP: Wilsy OS Core Engineering.
CERTIFICATION / UPDATE DATE: 2026-10-20
CHANGELOG:
    2026-10-20 v1.0.0-P47-R76-PROVISIONING-SECURITY-CERTIFICATE
    Govern the R35 direct security contracts against the R76 service.
COMPLIANCE: LAW EK-006; POPIA section 19; GDPR Article 32; SOC 2 CC7.2.
TENANT BOUNDARY: Exact tenant-scoped admission; no cross-tenant inference.
AUTHORITY BOUNDARY: Tests provisioning admission, not matter-content access.
FINANCIAL AUTHORITY BOUNDARY: None; Kennel EOS exclusively.
"""

from datetime import datetime, timezone
from typing import Any
from unittest.mock import Mock

import pytest

from tools.eos.auth.tenant_authorization import (
    TenantAuthorizationDecision,
    TenantAuthorizationReason,
)
from tools.eos.legal_operations.service import (
    legal_practitioner_matter_binding_provisioning_service as service,
)


class Session:
    """Represent the active caller-owned transaction marker."""

    in_transaction = True


def config() -> dict[str, Any]:
    """Build exact valid admission inputs without persistence authority."""
    return {
        "authenticated_principal_id": "partner-1",
        "tenant_id": "tenant-1",
        "case_matter_id": "matter-1",
        "practitioner_principal_id": "lawyer-1",
        "binding_id": "binding-1",
        "access_evidence_id": "access-1",
        "expected_access_evidence_fingerprint": "a" * 128,
        "granted_at": datetime(2026, 10, 19, tzinfo=timezone.utc),
        "client_party_id": "client-1",
        "subject_identity_fingerprint": "b" * 128,
        "principal_repository": object(),
        "membership_repository": object(),
        "business_role_repository": object(),
        "role_assignment_repository": object(),
        "lifecycle_collection": object(),
        "access_evidence_collection": object(),
        "disposition_collection": object(),
        "binding_collection": object(),
        "session": Session(),
    }


@pytest.mark.parametrize(
    "change",
    [
        {"session": None},
        {"session": type("InactiveSession", (), {"in_transaction": False})()},
        {"tenant_id": " "},
        {"binding_id": ""},
        {"authenticated_principal_id": "wrong\nactor"},
    ],
)
def test_invalid_input_or_transaction_denied_before_auth(
    monkeypatch: pytest.MonkeyPatch,
    change: dict[str, object],
) -> None:
    auth = Mock(side_effect=AssertionError("AUTH_CALLED"))
    monkeypatch.setattr(service, "authorize_tenant_operation", auth)
    kwargs = config()
    kwargs.update(change)
    with pytest.raises(service.PractitionerBindingProvisioningDenied):
        service.grant_binding(**kwargs)
    auth.assert_not_called()


@pytest.mark.parametrize(
    ("allowed", "role", "business"),
    [
        (False, "LEGAL_PARTNER", "tenant_legal_partner"),
        (True, "LEGAL_ATTORNEY", "tenant_legal_partner"),
        (True, "LEGAL_PARTNER", "tenant_legal_attorney"),
    ],
)
def test_forged_or_denied_partner_decision_never_reaches_target(
    monkeypatch: pytest.MonkeyPatch,
    allowed: bool,
    role: str,
    business: str,
) -> None:
    monkeypatch.setattr(
        service,
        "authorize_tenant_operation",
        Mock(
            return_value=TenantAuthorizationDecision(
                allowed,
                TenantAuthorizationReason.AUTHORIZED,
                business,
                role,
            )
        ),
    )
    target = Mock(side_effect=AssertionError("TARGET_CALLED"))
    monkeypatch.setattr(service, "_require_current_practitioner", target)
    with pytest.raises(service.PractitionerBindingProvisioningDenied):
        service.grant_binding(**config())
    target.assert_not_called()


def test_canonical_permission_and_session_passed_to_composer(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    auth = Mock(
        return_value=TenantAuthorizationDecision(
            True,
            TenantAuthorizationReason.AUTHORIZED,
            "tenant_legal_partner",
            "LEGAL_PARTNER",
        )
    )
    monkeypatch.setattr(service, "authorize_tenant_operation", auth)
    monkeypatch.setattr(
        service,
        "_require_current_practitioner",
        Mock(side_effect=service.PractitionerBindingProvisioningDenied("STOP")),
    )
    kwargs = config()
    with pytest.raises(service.PractitionerBindingProvisioningDenied):
        service.grant_binding(**kwargs)
    assert auth.call_args.kwargs["permission_id"] == service.PERMISSION
    assert auth.call_args.kwargs["operation"] == service.OPERATION
    assert auth.call_args.kwargs["session"] is kwargs["session"]


def test_revoke_transaction_required_before_authority(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    auth = Mock(side_effect=AssertionError("AUTH_CALLED"))
    monkeypatch.setattr(service, "authorize_tenant_operation", auth)
    kwargs = config()
    with pytest.raises(service.PractitionerBindingProvisioningDenied):
        service.revoke_binding(
            authenticated_principal_id=kwargs["authenticated_principal_id"],
            tenant_id=kwargs["tenant_id"],
            binding_id=kwargs["binding_id"],
            evidence_reference="revocation-1",
            revoked_at=kwargs["granted_at"],
            principal_repository=kwargs["principal_repository"],
            membership_repository=kwargs["membership_repository"],
            business_role_repository=kwargs["business_role_repository"],
            role_assignment_repository=kwargs["role_assignment_repository"],
            binding_collection=kwargs["binding_collection"],
            session=None,
        )
    auth.assert_not_called()


def test_no_content_or_wall_waiver_api() -> None:
    """Provisioning exports no content, wall-waiver or deadline authority."""
    for symbol in (
        "grant_content_access",
        "waive_ethical_wall",
        "read_matter_documents",
        "read_deadline",
    ):
        assert not hasattr(service, symbol)


# WILSY OS SOVEREIGN ARTIFACT SEAL
# ARTIFACT: test_legal_practitioner_matter_binding_provisioning_service.py
# VERSION: v1.0.0-P47-R76-PROVISIONING-SECURITY-CERTIFICATE
# AUTHORITY BOUNDARY: admission and composition tests only; no access grant
# TENANT POSTURE: exact own-tenant caller-owned transaction required
# FAIL-CLOSED POSTURE: invalid, inactive, mismatched and forged inputs deny
# FINANCIAL EXECUTION AUTHORITY: NONE; Kennel EOS exclusively
# END OF WILSY OS SOVEREIGN ARTIFACT
