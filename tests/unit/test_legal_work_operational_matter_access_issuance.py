"""WILSY P47-R95-G22 — Operational matter-access issuance admission.

CONTRACT: Only independently verified, current, transaction-bound
issuer and recipient evidence may precede an immutable grant.
Practitioner binding and documentary ALLOW are never sufficient.
"""

from datetime import datetime, timezone

import pytest

from tools.eos.legal_operations.service.legal_work_operational_matter_access_issuance import (
    LegalWorkOperationalMatterAccessIssuanceDenied,
    issue_operational_matter_access,
)

NOW = datetime(2026, 10, 21, 9, 0, tzinfo=timezone.utc)


class Session:
    def __init__(self, active):
        self.in_transaction = active


class ForbiddenDependency:
    def __getattr__(self, name):
        raise AssertionError("DEPENDENCY_MUST_NOT_BE_USED:" + name)


def request(session):
    return {
        "authenticated_principal_id": "partner-001",
        "tenant_id": "tenant-001",
        "case_matter_id": "matter-001",
        "practitioner_principal_id": "practitioner-001",
        "event_id": "operational-grant-001",
        "occurred_at": NOW,
        "issuer_authorization_evidence_reference": "issuer-evidence-001",
        "reason_reference": "matter-team-appointment-001",
        "principal_repository": ForbiddenDependency(),
        "membership_repository": ForbiddenDependency(),
        "business_role_repository": ForbiddenDependency(),
        "role_assignment_repository": ForbiddenDependency(),
        "lifecycle_collection": ForbiddenDependency(),
        "access_evidence_collection": ForbiddenDependency(),
        "conflict_disposition_collection": ForbiddenDependency(),
        "registry_collection": ForbiddenDependency(),
        "session": session,
    }


@pytest.mark.parametrize("session", [
    None, Session(False), Session(None),
])
def test_issuance_denies_without_active_transaction(session):
    with pytest.raises(LegalWorkOperationalMatterAccessIssuanceDenied):
        issue_operational_matter_access(**request(session))


def test_issuance_never_trusts_unavailable_iam_repositories():
    with pytest.raises(LegalWorkOperationalMatterAccessIssuanceDenied):
        issue_operational_matter_access(**request(Session(True)))


def test_issuance_does_not_accept_caller_supplied_allow_flag():
    args = request(Session(True))
    args["matter_access_allowed"] = True
    with pytest.raises(
        (TypeError, LegalWorkOperationalMatterAccessIssuanceDenied)
    ):
        issue_operational_matter_access(**args)


def test_issuance_does_not_accept_caller_supplied_clearance_flag():
    args = request(Session(True))
    args["ethical_wall_cleared"] = True
    with pytest.raises(
        (TypeError, LegalWorkOperationalMatterAccessIssuanceDenied)
    ):
        issue_operational_matter_access(**args)


def test_issuance_does_not_accept_binding_as_authority():
    args = request(Session(True))
    args["practitioner_binding_authorizes_access"] = True
    with pytest.raises(
        (TypeError, LegalWorkOperationalMatterAccessIssuanceDenied)
    ):
        issue_operational_matter_access(**args)


@pytest.mark.parametrize("bad", [
    "", "default", "*", "tenant foreign", None,
])
def test_tenant_scope_must_not_be_widened(bad):
    args = request(Session(True))
    args["tenant_id"] = bad
    with pytest.raises(LegalWorkOperationalMatterAccessIssuanceDenied):
        issue_operational_matter_access(**args)


def test_issuer_rejection_stops_before_matter_lookup(monkeypatch):
    from tools.eos.legal_operations.service import (
        legal_work_operational_matter_access_issuance as admission,
    )

    calls = []

    def reject_issuer(**kwargs):
        calls.append("issuer")
        raise admission.LegalWorkOperationalMatterAccessIssuanceDenied(
            "TEST_ISSUER_DENIED"
        )

    def forbidden_matter(**kwargs):
        raise AssertionError("MATTER_READ_AFTER_ISSUER_DENIAL")

    monkeypatch.setattr(admission, "_issuer", reject_issuer)
    monkeypatch.setattr(admission, "_case_matter", forbidden_matter)

    with pytest.raises(
        admission.LegalWorkOperationalMatterAccessIssuanceDenied,
        match="TEST_ISSUER_DENIED",
    ):
        issue_operational_matter_access(**request(Session(True)))

    assert calls == ["issuer"]


def test_closed_matter_stops_before_recipient(monkeypatch):
    from types import SimpleNamespace
    from tools.eos.legal_operations.service import (
        legal_work_operational_matter_access_issuance as admission,
    )

    calls = []

    def valid_issuer(**kwargs):
        calls.append("issuer")

    def closed_matter(**kwargs):
        calls.append("matter")
        return SimpleNamespace(
            tenant_id="tenant-001",
            case_matter_id="matter-001",
            state=SimpleNamespace(value="CLOSED"),
        )

    def forbidden_recipient(**kwargs):
        raise AssertionError("RECIPIENT_READ_AFTER_CLOSED_MATTER")

    monkeypatch.setattr(admission, "_issuer", valid_issuer)
    monkeypatch.setattr(admission, "_case_matter", closed_matter)
    monkeypatch.setattr(admission, "_recipient", forbidden_recipient)

    with pytest.raises(
        admission.LegalWorkOperationalMatterAccessIssuanceDenied,
        match="P47_R95_ISSUER_MATTER_NOT_OPEN",
    ):
        issue_operational_matter_access(**request(Session(True)))

    assert calls == ["issuer", "matter"]


def test_valid_prerequisite_sequence_still_denies_clearance(monkeypatch):
    from types import SimpleNamespace
    from tools.eos.legal_operations.service import (
        legal_work_operational_matter_access_issuance as admission,
    )

    calls = []

    def issuer(**kwargs):
        assert kwargs["principal_id"] == "partner-001"
        assert kwargs["tenant_id"] == "tenant-001"
        calls.append("issuer")

    def matter(**kwargs):
        assert kwargs["case_matter_id"] == "matter-001"
        assert kwargs["tenant_id"] == "tenant-001"
        calls.append("matter")
        return SimpleNamespace(
            tenant_id="tenant-001",
            case_matter_id="matter-001",
            state=SimpleNamespace(value="OPEN"),
        )

    def recipient(**kwargs):
        assert kwargs["principal_id"] == "practitioner-001"
        assert kwargs["tenant_id"] == "tenant-001"
        calls.append("recipient")

    monkeypatch.setattr(admission, "_issuer", issuer)
    monkeypatch.setattr(admission, "_case_matter", matter)
    monkeypatch.setattr(admission, "_recipient", recipient)

    args = request(Session(True))
    with pytest.raises(
        admission.LegalWorkOperationalMatterAccessIssuanceDenied,
        match="P47_R95_ISSUER_CONFIDENTIALITY_CLEARANCE_UNAVAILABLE",
    ):
        issue_operational_matter_access(**args)

    assert calls == ["issuer", "matter", "recipient"]
    # Every supplied collection is a ForbiddenDependency; reaching this
    # denial proves no registry write occurred in this controlled path.


def test_resolved_recipient_business_role_is_accepted(monkeypatch):
    """The resolver's result object, not its enum class, is authoritative."""
    from types import SimpleNamespace
    from tools.eos.auth.principal_status import PrincipalStatus
    from tools.eos.auth.tenant_membership import TenantMembershipStatus
    from tools.eos.auth.role_assignment import RoleAssignmentStatus
    from tools.eos.auth.tenant_business_role_authority import (
        BusinessRoleResolution,
    )
    from tools.eos.legal_operations.service import (
        legal_work_operational_matter_access_issuance as admission,
    )

    class Repository:
        def __init__(self, value):
            self.value = value
        def resolve(self, *args, session):
            assert session.in_transaction is True
            return self.value

    def role_resolution(**kwargs):
        assert kwargs["principal_id"] == "practitioner-001"
        assert kwargs["tenant_id"] == "tenant-001"
        return SimpleNamespace(
            role="tenant_legal_attorney",
            resolution=BusinessRoleResolution.RESOLVED,
        )

    monkeypatch.setattr(
        admission, "resolve_current_tenant_business_role",
        role_resolution,
    )

    assert admission._recipient(
        principal_id="practitioner-001",
        tenant_id="tenant-001",
        principal_repository=Repository(SimpleNamespace(
            principal_id="practitioner-001",
            status=PrincipalStatus.ACTIVE,
        )),
        membership_repository=Repository(SimpleNamespace(
            principal_id="practitioner-001",
            tenant_id="tenant-001",
            status=TenantMembershipStatus.ACTIVE,
        )),
        business_role_repository=Repository(None),
        role_assignment_repository=Repository(SimpleNamespace(
            principal_id="practitioner-001",
            tenant_id="tenant-001",
            role_id="LEGAL_ATTORNEY",
            status=RoleAssignmentStatus.ACTIVE,
        )),
        session=Session(True),
    ) is None


def test_ambiguous_recipient_business_role_is_denied(monkeypatch):
    from types import SimpleNamespace
    from tools.eos.auth.principal_status import PrincipalStatus
    from tools.eos.auth.tenant_membership import TenantMembershipStatus
    from tools.eos.auth.tenant_business_role_authority import (
        BusinessRoleResolution,
    )
    from tools.eos.legal_operations.service import (
        legal_work_operational_matter_access_issuance as admission,
    )

    class Repository:
        def __init__(self, value):
            self.value = value
        def resolve(self, *args, session):
            return self.value

    monkeypatch.setattr(
        admission, "resolve_current_tenant_business_role",
        lambda **kwargs: SimpleNamespace(
            role=None,
            resolution=BusinessRoleResolution.MULTIPLE_ACTIVE_TENANT_BUSINESS_ROLES,
        ),
    )
    with pytest.raises(
        admission.LegalWorkOperationalMatterAccessIssuanceDenied
    ):
        admission._recipient(
            principal_id="practitioner-001",
            tenant_id="tenant-001",
            principal_repository=Repository(SimpleNamespace(
                principal_id="practitioner-001",
                status=PrincipalStatus.ACTIVE,
            )),
            membership_repository=Repository(SimpleNamespace(
                principal_id="practitioner-001",
                tenant_id="tenant-001",
                status=TenantMembershipStatus.ACTIVE,
            )),
            business_role_repository=Repository(None),
            role_assignment_repository=ForbiddenDependency(),
            session=Session(True),
        )
