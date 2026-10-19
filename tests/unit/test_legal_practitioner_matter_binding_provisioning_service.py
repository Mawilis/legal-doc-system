"""P4-R4-R2C service security and transaction boundary tests."""
from datetime import datetime,timezone
from typing import Any
from unittest.mock import Mock
import pytest
from tools.eos.legal_operations.service import (
    legal_practitioner_matter_binding_provisioning_service as service,
)
from tools.eos.auth.tenant_authorization import (
    TenantAuthorizationDecision,TenantAuthorizationReason,
)

class Session:
    in_transaction=True

def config() -> dict[str, Any]:
    return dict(
        authenticated_principal_id="partner-1",tenant_id="tenant-1",
        case_matter_id="matter-1",practitioner_principal_id="lawyer-1",
        binding_id="binding-1",access_evidence_id="access-1",
        expected_access_evidence_fingerprint="a"*128,
        granted_at=datetime(2026,10,19,tzinfo=timezone.utc),
        client_party_id="client-1",subject_identity_fingerprint="b"*128,
        principal_repository=object(),membership_repository=object(),
        business_role_repository=object(),role_assignment_repository=object(),
        lifecycle_collection=object(),access_evidence_collection=object(),
        disposition_collection=object(),binding_collection=object(),
        session=Session(),
    )

@pytest.mark.parametrize("change",[
    {"session":None},{"session":type("S",(),{"in_transaction":False})()},
    {"tenant_id":" "},{"binding_id":""},
    {"authenticated_principal_id":"wrong\nactor"},
])
def test_invalid_input_or_transaction_denied_before_auth(monkeypatch,change):
    auth=Mock(side_effect=AssertionError("AUTH_CALLED"))
    monkeypatch.setattr(service,"authorize_tenant_operation",auth)
    kw=config()
    kw.update(change)
    with pytest.raises(service.PractitionerBindingProvisioningDenied):
        service.grant_binding(**kw)
    auth.assert_not_called()

@pytest.mark.parametrize("allowed,role,business",[
    (False,"LEGAL_PARTNER","tenant_legal_partner"),
    (True,"LEGAL_ATTORNEY","tenant_legal_partner"),
    (True,"LEGAL_PARTNER","tenant_legal_attorney"),
])
def test_forged_or_denied_partner_decision_never_reaches_target(
        monkeypatch,allowed,role,business):
    monkeypatch.setattr(service,"authorize_tenant_operation",
        Mock(return_value=TenantAuthorizationDecision(
            allowed,TenantAuthorizationReason.AUTHORIZED,business,role)))
    target=Mock(side_effect=AssertionError("TARGET_CALLED"))
    monkeypatch.setattr(service,"_practitioner",target)
    with pytest.raises(service.PractitionerBindingProvisioningDenied):
        service.grant_binding(**config())
    target.assert_not_called()

def test_canonical_permission_and_session_passed_to_composer(monkeypatch):
    auth=Mock(return_value=TenantAuthorizationDecision(
        True,TenantAuthorizationReason.AUTHORIZED,
        "tenant_legal_partner","LEGAL_PARTNER"))
    monkeypatch.setattr(service,"authorize_tenant_operation",auth)
    monkeypatch.setattr(service,"_practitioner",
        Mock(side_effect=service.PractitionerBindingProvisioningDenied("STOP")))
    kw=config()
    with pytest.raises(service.PractitionerBindingProvisioningDenied):
        service.grant_binding(**kw)
    assert auth.call_args.kwargs["permission_id"]==service.PERMISSION
    assert auth.call_args.kwargs["operation"]==service.OPERATION
    assert auth.call_args.kwargs["session"] is kw["session"]

def test_revoke_transaction_required_before_authority(monkeypatch):
    auth=Mock(side_effect=AssertionError("AUTH_CALLED"))
    monkeypatch.setattr(service,"authorize_tenant_operation",auth)
    kw=config()
    with pytest.raises(service.PractitionerBindingProvisioningDenied):
        service.revoke_binding(
            authenticated_principal_id=kw["authenticated_principal_id"],
            tenant_id=kw["tenant_id"],binding_id=kw["binding_id"],
            evidence_reference="revocation-1",revoked_at=kw["granted_at"],
            principal_repository=kw["principal_repository"],
            membership_repository=kw["membership_repository"],
            business_role_repository=kw["business_role_repository"],
            role_assignment_repository=kw["role_assignment_repository"],
            binding_collection=kw["binding_collection"],session=None,
        )
    auth.assert_not_called()

def test_no_content_or_wall_waiver_api():
    for symbol in ("grant_content_access","waive_ethical_wall",
                   "read_matter_documents","read_deadline"):
        assert not hasattr(service,symbol)

# WILSY OS SOVEREIGN ARTIFACT SEAL
# VERSION: v1.0.0-P9-R105-P4G-P6-R7B-P4-R4-R2C
# END OF WILSY OS SOVEREIGN ARTIFACT
