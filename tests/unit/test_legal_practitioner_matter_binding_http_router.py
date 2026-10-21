"""P12C practitioner binding authenticated HTTP contract certificate.

Authority: transport structure and fail-closed request admission only.
No content grants, ethical-wall waivers, financial execution or database writes.
"""
from __future__ import annotations

import importlib

import pytest
from fastapi.routing import APIRoute
from pydantic import ValidationError


MODULE = (
    "tools.eos.api."
    "legal_practitioner_matter_binding_router"
)


@pytest.fixture
def boundary():
    """Load the dedicated sovereign HTTP boundary."""
    return importlib.import_module(MODULE)


def test_exact_two_command_routes(boundary):
    """Expose only grant and revoke command methods."""
    routes = sorted(
        (method, route.path)
        for route in boundary.router.routes
        if isinstance(route, APIRoute)
        for method in (route.methods or ())
    )
    assert routes == [
        ("POST", "/legal-operations/practitioner-bindings"),
        ("POST", "/legal-operations/practitioner-bindings/revocations"),
    ]


def test_exact_partner_permission_pair(boundary):
    """Reuse the certified partner provisioning permission."""
    from tools.eos.legal_operations.service import (
        legal_practitioner_matter_binding_provisioning_service
        as service,
    )

    assert boundary.PERMISSION == service.PERMISSION
    assert boundary.OPERATION == service.OPERATION


@pytest.mark.parametrize(
    "forbidden",
    [
        "tenant_id",
        "authenticated_principal_id",
        "granted_at",
        "client_party_id",
        "subject_identity_fingerprint",
        "matter_fingerprint",
        "authorization_decision",
        "ethical_wall_clearance",
    ],
)
def test_grant_cannot_accept_caller_authority(boundary, forbidden):
    """Reject all browser-asserted authority and chronology."""
    payload = {
        "case_matter_id": "matter-1",
        "practitioner_principal_id": "lawyer-1",
        "binding_id": "binding-1",
        "access_evidence_id": "evidence-1",
        "expected_access_evidence_fingerprint": "a" * 128,
    }
    payload[forbidden] = "forged"
    with pytest.raises(ValidationError):
        boundary.GrantPractitionerBindingCommand.model_validate(
            payload
        )


@pytest.mark.parametrize(
    "forbidden",
    [
        "tenant_id",
        "authenticated_principal_id",
        "revoked_at",
        "authorization_decision",
        "ethical_wall_clearance",
    ],
)
def test_revoke_cannot_accept_caller_authority(
    boundary, forbidden
):
    """Revocation cannot accept browser IAM or timestamps."""
    payload = {
        "binding_id": "binding-1",
        "evidence_reference": "revocation-1",
    }
    payload[forbidden] = "forged"
    with pytest.raises(ValidationError):
        boundary.RevokePractitionerBindingCommand.model_validate(
            payload
        )


def test_service_functions_remain_canonical(boundary):
    """The router must import, not recreate, binding authority."""
    from tools.eos.legal_operations.service import (
        legal_practitioner_matter_binding_provisioning_service
        as service,
    )

    assert boundary.grant_binding is service.grant_binding
    assert boundary.revoke_binding is service.revoke_binding


# ARTIFACT: test_legal_practitioner_matter_binding_http_router.py
# VERSION: v1.0.0-P12C-R4A-HTTP-CONTRACT-RED
# AUTHORITY BOUNDARY: test certificate only
# TENANT POSTURE: forbids caller-asserted tenant authority
# FAIL-CLOSED POSTURE: forbidden fields reject
# FINANCIAL EXECUTION AUTHORITY: none
# END OF WILSY OS SOVEREIGN ARTIFACT
