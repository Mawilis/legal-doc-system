"""WILSY P9-R105-P3R2 authenticated issuer test-first certificate."""
from pathlib import Path
import runpy
from unittest.mock import Mock

import pytest

from tools.eos.auth.tenant_authorization import (
    TenantAuthorizationDecision,
    TenantAuthorizationReason,
)
from tools.eos.legal_operations.service import (
    legal_practitioner_matter_access_issuer_service as issuer,
)

ROOT = Path(__file__).resolve().parents[2]
MAKE = runpy.run_path(
    str(ROOT / "tests/unit/test_legal_practitioner_matter_access.py")
)["_make"]


class Session:
    in_transaction = True


def decision(
    allowed=True,
    reason=TenantAuthorizationReason.AUTHORIZED,
    business_role="tenant_legal_partner",
    role="LEGAL_PARTNER",
):
    return TenantAuthorizationDecision(allowed, reason, business_role, role)


def call(item=None, **changes):
    valid = MAKE()
    values = dict(
        authenticated_principal_id=valid.issued_by_principal_id,
        tenant_id=valid.tenant_id,
        evidence=valid if item is None else item,
        principal_repository=object(),
        membership_repository=object(),
        role_assignment_repository=object(),
        business_role_repository=object(),
        collection=object(),
        session=Session(),
        matter_fingerprint="a" * 128,
        client_party_id="client-1",
        subject_identity_fingerprint="b" * 128,
        evaluation_time=valid.effective_from,
        disposition_collection=object(),
    )
    values.update(changes)
    return issuer.issue_first_revision_evidence(**values)


@pytest.fixture(autouse=True)
def _isolate_provenance_for_actor_unit_tests(monkeypatch):
    monkeypatch.setattr(
        issuer, "verify_current_conflict_provenance",
        lambda **kwargs: None,
    )


def test_partner_issues_documentary_first_revision(monkeypatch):
    auth = Mock(return_value=decision())
    append = Mock(side_effect=lambda **kw: kw["evidence"])
    monkeypatch.setattr(issuer, "authorize_tenant_operation", auth)
    monkeypatch.setattr(issuer, "append_evidence", append)
    item = MAKE()
    assert call(item) == item
    assert append.call_count == 1
    assert append.call_args.kwargs["evidence"] == item
    assert append.call_args.kwargs["session"].in_transaction is True


def test_actor_tenant_and_canonical_iam_are_exact(monkeypatch):
    auth = Mock(return_value=decision())
    monkeypatch.setattr(issuer, "authorize_tenant_operation", auth)
    monkeypatch.setattr(issuer, "append_evidence", lambda **kw: kw["evidence"])
    item = MAKE()
    call(item)
    args = auth.call_args.kwargs
    assert args["principal_id"] == item.issued_by_principal_id
    assert args["tenant_id"] == item.tenant_id
    assert args["permission_id"] == issuer.PERMISSION
    assert args["operation"] == issuer.OPERATION
    assert args["session"].in_transaction is True


@pytest.mark.parametrize("auth_result", [
    decision(False),
    decision(False, TenantAuthorizationReason.BUSINESS_ROLE_INELIGIBLE),
    decision(True, TenantAuthorizationReason.BUSINESS_ROLE_INELIGIBLE),
    decision(True, business_role="tenant_legal_attorney"),
    decision(True, role="LEGAL_ATTORNEY"),
])
def test_denied_or_forged_decision_cannot_append(monkeypatch, auth_result):
    monkeypatch.setattr(
        issuer, "authorize_tenant_operation", lambda **kw: auth_result
    )
    monkeypatch.setattr(
        issuer, "append_evidence",
        lambda **kw: pytest.fail("DENIED_ACTOR_PERSISTED_EVIDENCE"),
    )
    with pytest.raises(issuer.PractitionerMatterAccessIssuerDenied):
        call()


@pytest.mark.parametrize("change", [
    {"authenticated_principal_id": "foreign-issuer"},
    {"authenticated_principal_id": " "},
    {"tenant_id": "foreign-tenant"},
    {"tenant_id": ""},
    {"session": None},
    {"session": type("Inactive", (), {"in_transaction": False})()},
])
def test_invalid_scope_or_transaction_denied_before_auth(monkeypatch, change):
    monkeypatch.setattr(
        issuer, "authorize_tenant_operation",
        lambda **kw: pytest.fail("UNAUTHORIZED_IAM_LOOKUP"),
    )
    with pytest.raises(issuer.PractitionerMatterAccessIssuerDenied):
        call(**change)


def test_noncanonical_evidence_denied_before_auth(monkeypatch):
    monkeypatch.setattr(
        issuer, "authorize_tenant_operation",
        lambda **kw: pytest.fail("UNAUTHORIZED_IAM_LOOKUP"),
    )
    with pytest.raises(issuer.PractitionerMatterAccessIssuerDenied):
        call(item=object())


def test_no_operational_access_or_reassignment():
    for symbol in (
        "grant_access", "reassign", "authorize_matter_access",
        "execute_policy", "grant_matter_visibility",
    ):
        assert not hasattr(issuer, symbol)


# WILSY OS SOVEREIGN ARTIFACT SEAL
# ARTIFACT: test_legal_practitioner_matter_access_issuer_service.py
# VERSION: v1.0.0-P9-R105-P3R2-ISSUER-TESTS
# END OF WILSY OS SOVEREIGN ARTIFACT


def test_missing_provenance_context_denies_persistence(monkeypatch):
    monkeypatch.setattr(
        issuer, "authorize_tenant_operation",
        lambda **kw: decision(),
    )
    monkeypatch.setattr(
        issuer, "append_evidence",
        lambda **kw: pytest.fail("MISSING_PROVENANCE_PERSISTED"),
    )
    with pytest.raises(issuer.PractitionerMatterAccessIssuerDenied):
        call(disposition_collection=None)


def test_denied_provenance_never_persists(monkeypatch):
    from tools.eos.legal_operations.service.legal_practitioner_matter_access_conflict_provenance import (
        PractitionerMatterAccessConflictProvenanceDenied,
    )
    monkeypatch.setattr(
        issuer, "authorize_tenant_operation",
        lambda **kw: decision(),
    )
    def reject(**kw):
        raise PractitionerMatterAccessConflictProvenanceDenied(
            "P9_TEST_NO_CLEARANCE"
        )
    monkeypatch.setattr(
        issuer, "verify_current_conflict_provenance", reject
    )
    monkeypatch.setattr(
        issuer, "append_evidence",
        lambda **kw: pytest.fail("DENIED_PROVENANCE_PERSISTED"),
    )
    with pytest.raises(issuer.PractitionerMatterAccessIssuerDenied):
        call()


def test_positive_issuer_passes_exact_evidence_scope_and_session(
    monkeypatch,
):
    verify = Mock(return_value=None)
    append = Mock(side_effect=lambda **kw: kw["evidence"])
    monkeypatch.setattr(
        issuer, "authorize_tenant_operation",
        lambda **kw: decision(),
    )
    monkeypatch.setattr(
        issuer, "verify_current_conflict_provenance", verify
    )
    monkeypatch.setattr(issuer, "append_evidence", append)
    item=MAKE()
    assert call(item)==item
    assert verify.call_count==1
    assert append.call_count==1
    assert verify.call_args.kwargs["evidence"]==item
    assert verify.call_args.kwargs["session"] is append.call_args.kwargs["session"]


def test_no_legacy_issuer_bypass_without_provenance(monkeypatch):
    monkeypatch.setattr(
        issuer, "authorize_tenant_operation",
        lambda **kw: decision(),
    )
    monkeypatch.setattr(
        issuer, "append_evidence",
        lambda **kw: pytest.fail("LEGACY_BYPASS"),
    )
    with pytest.raises(issuer.PractitionerMatterAccessIssuerDenied):
        call(
            matter_fingerprint=None,
            client_party_id=None,
            subject_identity_fingerprint=None,
            evaluation_time=None,
            disposition_collection=None,
        )
