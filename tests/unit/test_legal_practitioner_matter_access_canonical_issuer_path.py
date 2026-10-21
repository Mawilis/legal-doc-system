"""WILSY P9-R105-P4E canonical documentary issuer composition certificate.

Genuine conflict-disposition domain evidence, real currentness projector,
real issuer provenance integration and real fake-collection registry append.
Only the separate IAM decision and database history transport are substituted.
No operational matter access or ethical-wall clearance is established.
"""
from datetime import timedelta
from pathlib import Path
import runpy

import pytest

from tools.eos.auth.tenant_authorization import (
    TenantAuthorizationDecision,
    TenantAuthorizationReason,
)
from tools.eos.legal_operations.domain.legal_client_matter_conflict_disposition import (
    LegalClientMatterConflictDispositionType,
)
from tools.eos.legal_operations.service import (
    legal_practitioner_matter_access_issuer_service as issuer,
)
from tools.eos.legal_operations.service import (
    legal_practitioner_matter_access_conflict_provenance as provenance,
)

ROOT = Path(__file__).resolve().parents[2]
MAKE = runpy.run_path(
    str(ROOT / "tests/unit/test_legal_practitioner_matter_access.py")
)["_make"]
BUNDLE = runpy.run_path(
    str(ROOT / "tests/unit/test_legal_client_matter_conflict_disposition.py")
)["bundle"]
REGISTRY = runpy.run_path(
    str(ROOT / "tests/unit/test_legal_practitioner_matter_access_registry.py")
)
Collection = REGISTRY["Collection"]
Session = REGISTRY["Session"]


def prepare(monkeypatch, *, disposition=None, permitted=True):
    if disposition is None:
        historical = BUNDLE()[0]
    else:
        historical = BUNDLE(disposition=disposition)[0]

    evidence = MAKE(
        tenant_id=historical.tenant_id,
        case_matter_id=historical.case_matter_id,
        source_evidence_fingerprint=historical.fingerprint,
    )
    collection = Collection()
    session = Session()
    calls = []

    def read_history(**kwargs):
        calls.append(kwargs)
        return (historical,)

    monkeypatch.setattr(
        provenance, "list_dispositions_for_context", read_history
    )

    decision = TenantAuthorizationDecision(
        permitted,
        (
            TenantAuthorizationReason.AUTHORIZED
            if permitted
            else TenantAuthorizationReason.PERMISSION_NOT_GRANTED
        ),
        "tenant_legal_partner",
        "LEGAL_PARTNER",
    )
    auth_calls = []

    def authorize(**kwargs):
        auth_calls.append(kwargs)
        return decision

    monkeypatch.setattr(issuer, "authorize_tenant_operation", authorize)

    arguments = dict(
        authenticated_principal_id=evidence.issued_by_principal_id,
        tenant_id=evidence.tenant_id,
        evidence=evidence,
        principal_repository=object(),
        membership_repository=object(),
        role_assignment_repository=object(),
        business_role_repository=object(),
        collection=collection,
        session=session,
        matter_fingerprint=historical.matter_fingerprint,
        client_party_id=historical.client_party_id,
        subject_identity_fingerprint=historical.subject_identity_fingerprint,
        evaluation_time=historical.effective_from,
        disposition_collection=object(),
    )
    return historical, evidence, collection, arguments, calls, auth_calls


def test_real_permitted_history_issues_one_exact_document(monkeypatch):
    historical, evidence, collection, args, reads, auths = prepare(monkeypatch)

    assert historical.disposition.value == "ENGAGEMENT_PERMITTED"
    assert historical.review_outcome.value == "NO_CONFLICT_IDENTIFIED"

    first = issuer.issue_first_revision_evidence(**args)
    replay = issuer.issue_first_revision_evidence(**args)

    assert first == evidence
    assert replay == evidence
    assert len(collection.rows) == 1
    assert collection.rows[0]["fingerprint"] == evidence.fingerprint
    assert collection.rows[0]["source_evidence_fingerprint"] == (
        historical.fingerprint
    )
    assert len(reads) == 2
    assert len(auths) == 2
    assert all(item["session"] is args["session"] for item in reads)
    assert all(item["session"] is args["session"] for item in auths)
    assert all(
        item["permission_id"] == issuer.PERMISSION
        and item["operation"] == issuer.OPERATION
        for item in auths
    )


def test_wrong_source_fingerprint_cannot_append(monkeypatch):
    historical, _, collection, args, _, _ = prepare(monkeypatch)
    bad = "f" * 128
    if historical.fingerprint == bad:
        bad = "e" * 128

    args["evidence"] = MAKE(
        tenant_id=historical.tenant_id,
        case_matter_id=historical.case_matter_id,
        source_evidence_fingerprint=bad,
    )

    with pytest.raises(issuer.PractitionerMatterAccessIssuerDenied):
        issuer.issue_first_revision_evidence(**args)
    assert collection.rows == []


def test_future_only_disposition_cannot_append(monkeypatch):
    _, _, collection, args, _, _ = prepare(monkeypatch)
    args["evaluation_time"] -= timedelta(microseconds=1)

    with pytest.raises(issuer.PractitionerMatterAccessIssuerDenied):
        issuer.issue_first_revision_evidence(**args)
    assert collection.rows == []


def test_prohibited_disposition_cannot_append(monkeypatch):
    _, _, collection, args, _, _ = prepare(
        monkeypatch,
        disposition=LegalClientMatterConflictDispositionType.ENGAGEMENT_PROHIBITED,
    )
    with pytest.raises(issuer.PractitionerMatterAccessIssuerDenied):
        issuer.issue_first_revision_evidence(**args)
    assert collection.rows == []


def test_denied_actor_cannot_read_provenance_or_append(monkeypatch):
    _, _, collection, args, reads, auths = prepare(
        monkeypatch, permitted=False
    )
    with pytest.raises(issuer.PractitionerMatterAccessIssuerDenied):
        issuer.issue_first_revision_evidence(**args)
    assert len(auths) == 1
    assert reads == []
    assert collection.rows == []


def test_cross_tenant_issuer_scope_cannot_append(monkeypatch):
    _, _, collection, args, reads, auths = prepare(monkeypatch)
    args["tenant_id"] = "foreign-tenant"
    with pytest.raises(issuer.PractitionerMatterAccessIssuerDenied):
        issuer.issue_first_revision_evidence(**args)
    assert auths == []
    assert reads == []
    assert collection.rows == []


def test_first_revision_only_and_no_operational_grant():
    assert not hasattr(issuer, "grant_access")
    assert not hasattr(issuer, "reassign")
    assert not hasattr(provenance, "grant_access")


# WILSY OS SOVEREIGN ARTIFACT SEAL
# ARTIFACT: test_legal_practitioner_matter_access_canonical_issuer_path.py
# VERSION: v1.0.0-P9-R105-P4E
# OPERATIONAL MATTER ACCESS / ETHICAL WALL / FINANCIAL AUTHORITY: NONE
# END OF WILSY OS SOVEREIGN ARTIFACT
