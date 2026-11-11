"""WILSY OS Institutional Signer Router Certification.

TITLE: Institutional Signer Router Readiness and Provenance Certificate
VERSION: v1.0.1-P12C-INSTITUTIONAL-SIGNER-PROVENANCE-CERT
AUTHORITY: Deterministic HTTP readiness and provenance evidence only.
EPITOME: Proves enrollment provenance requires current, exact identity-proofing
         and signatory-mandate records bound to tenant, principal, certificate,
         and the caller-supplied evidence references.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tests/unit/test_institutional_signer_router.py
COLLABORATION / OWNERSHIP: Exercises the canonical institutional signer router
                           and enrollment registry contracts.
CERTIFICATION / UPDATE DATE: 2026-11-11
CHANGELOG: v1.0.1-P12C-INSTITUTIONAL-SIGNER-PROVENANCE-CERT makes provenance
           fixtures current at the evaluation instant and supplies exact
           identity and mandate evidence references to the required API.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2.
SECURITY / PRIVACY POSTURE: Synthetic evidence references and fingerprints only.
TENANT BOUNDARY: Exact tenant, subject principal, and certificate bindings are asserted.
AUTHORITY BOUNDARY: Evidence provenance does not grant enrollment or signing authority.
FINANCIAL AUTHORITY BOUNDARY: Kennel EOS exclusively owns financial execution.
"""
from __future__ import annotations

from datetime import datetime, timedelta, timezone
from types import SimpleNamespace

import pytest
from fastapi import HTTPException

from tools.eos.api import institutional_signer_router as router
from tools.eos.security.institutional_signer_enrollment_registry import (
    InstitutionalSignerEnrollmentRegistry,
    InstitutionalSignerRegistryError,
)


class _Session:
    def __enter__(self):
        return self

    def __exit__(self, *_args):
        return False

    def with_transaction(self, callback, **_kwargs):
        return callback(self)


class _Client:
    def start_session(self):
        return _Session()


class _Database:
    def __getitem__(self, _name):
        return object()


def test_signer_transaction_does_not_create_indexes_on_request_path(monkeypatch):
    monkeypatch.setattr(router, "get_client", lambda: _Client())
    monkeypatch.setattr(router, "get_database", lambda: _Database())

    def forbidden_ddl(*_args, **_kwargs):
        raise AssertionError("request path must not execute index DDL")

    monkeypatch.setattr(InstitutionalSignerEnrollmentRegistry, "ensure_indexes", forbidden_ddl)

    result = router._transaction(
        lambda registry, _session: isinstance(registry, InstitutionalSignerEnrollmentRegistry)
    )
    assert result is True


def test_signer_routes_fail_closed_until_canonical_startup_registry_indexes_are_ready():
    request = SimpleNamespace(app=SimpleNamespace(
        state=SimpleNamespace(institutional_signer_registry_ready=False)
    ))
    with pytest.raises(HTTPException) as error:
        router._require_registry_ready(request)
    assert error.value.status_code == 503
    assert error.value.detail == "INSTITUTIONAL_SIGNER_REGISTRY_NOT_READY"


def test_signer_registry_readiness_is_independent_of_pki_verifier_readiness():
    request = SimpleNamespace(app=SimpleNamespace(
        state=SimpleNamespace(
            institutional_signer_registry_ready=True,
            institutional_pki_ready=False,
            institutional_pki_verifier=None,
        )
    ))
    router._require_registry_ready(request)
    with pytest.raises(HTTPException) as error:
        router._verifier(request)
    assert error.value.status_code == 503
    assert error.value.detail == "INSTITUTIONAL_PKI_NOT_READY"


def test_signer_evidence_verifier_is_unavailable_by_default_and_denies_enrollment():
    from tools.eos.security.institutional_signer_evidence_verifier import (
        UnavailableInstitutionalSignerEvidenceVerifier,
    )
    request = SimpleNamespace(app=SimpleNamespace(state=SimpleNamespace(
        institutional_signer_evidence_verifier=UnavailableInstitutionalSignerEvidenceVerifier()
    )))
    verifier = router._evidence_verifier(request)
    with pytest.raises(HTTPException) as error:
        router._verify_enrollment_evidence(
            verifier,
            tenant_id="WILSYTENANT-4CD2FZ4O",
            certificate_fingerprint_sha256="a" * 64,
            subject_principal_id="PRINCIPAL-1",
            identity_proofing_reference="evidence://identity/123",
            signatory_mandate_reference="evidence://mandate/456",
            evaluated_at=datetime.now(timezone.utc),
            session=object(),
        )
    assert error.value.status_code == 503
    assert error.value.detail == "INSTITUTIONAL_SIGNER_EVIDENCE_AUTHORITY_UNAVAILABLE"


def _evidence_record(**overrides):
    now = datetime.now(timezone.utc)
    values = {
        "source_system_id": "dha-npr-verification",
        "source_record_id": "record-001",
        "source_revision": "revision-7",
        "evidence_reference": "evidence://source/record-001",
        "status": "ACTIVE",
        "evidence_fingerprint_sha256": "e" * 64,
        "valid_from": now - timedelta(days=365),
        "valid_until": None,
        "revoked": False,
        "verified_at": now - timedelta(seconds=1),
        "tenant_id": "WILSYTENANT-4CD2FZ4O",
        "subject_principal_id": "PRINCIPAL-1",
        "certificate_fingerprint_sha256": "a" * 64,
        "identity_assurance_level": "SUBSTANTIAL",
        "legal_entity_reference": "WILSY-PTY-LTD",
        "mandate_scope": "INSTITUTIONAL_SIGNER",
        "approval_scope": "INSTITUTIONAL_SIGNER_ENROLLMENT",
    }
    values.update(overrides)
    return SimpleNamespace(**values)


def test_signer_route_builds_complete_identity_and_mandate_provenance():
    now = datetime.now(timezone.utc)
    result = SimpleNamespace(
        identity_proofing=_evidence_record(),
        signatory_mandate=_evidence_record(
            source_system_id="wilsy-company-secretarial-register",
            source_record_id="board-resolution-009",
            evidence_reference="evidence://source/mandate-009",
            evidence_kind="SIGNATORY_MANDATE",
            legal_entity_reference="WILSY-PTY-LTD",
            mandate_scope="INSTITUTIONAL_SIGNER",
        ),
    )
    result.identity_proofing.evidence_kind = "IDENTITY_PROOFING"
    snapshot, digest = router._enrollment_provenance(
        result, tenant_id="WILSYTENANT-4CD2FZ4O",
        certificate_fingerprint_sha256="a" * 64,
        subject_principal_id="PRINCIPAL-1",
        identity_proofing_reference="evidence://source/record-001",
        signatory_mandate_reference="evidence://source/mandate-009",
        evaluated_at=now,
    )
    assert snapshot["identity_proofing"]["source_system_id"] == "dha-npr-verification"
    assert snapshot["signatory_mandate"]["source_record_id"] == "board-resolution-009"
    assert len(digest) == 64


def test_signer_route_rejects_expired_or_revoked_evidence_provenance():
    now = datetime.now(timezone.utc)
    expired = _evidence_record(valid_until=now.replace(year=now.year - 1))
    with pytest.raises(HTTPException) as error:
        router._record_provenance_snapshot(expired, evaluated_at=now, expected_bindings={})
    assert error.value.detail == "INSTITUTIONAL_SIGNER_EVIDENCE_NOT_CURRENT"
    revoked = _evidence_record(revoked=True)
    with pytest.raises(HTTPException) as error:
        router._record_provenance_snapshot(revoked, evaluated_at=now, expected_bindings={})
    assert error.value.detail == "INSTITUTIONAL_SIGNER_EVIDENCE_NOT_CURRENT"



def test_signer_provenance_persists_assurance_and_legal_mandate_scope():
    now = datetime.now(timezone.utc)
    result = SimpleNamespace(
        identity_proofing=_evidence_record(evidence_kind="IDENTITY_PROOFING"),
        signatory_mandate=_evidence_record(
            evidence_reference="evidence://source/mandate-009",
            evidence_kind="SIGNATORY_MANDATE",
            legal_entity_reference="WILSY-PTY-LTD",
            mandate_scope="INSTITUTIONAL_SIGNER",
        ),
    )
    snapshot, _digest = router._enrollment_provenance(
        result, tenant_id="WILSYTENANT-4CD2FZ4O",
        certificate_fingerprint_sha256="a" * 64,
        subject_principal_id="PRINCIPAL-1",
        identity_proofing_reference="evidence://source/record-001",
        signatory_mandate_reference="evidence://source/mandate-009",
        evaluated_at=now,
    )
    assert snapshot["identity_proofing"]["identity_assurance_level"] == "SUBSTANTIAL"
    assert snapshot["signatory_mandate"]["legal_entity_reference"] == "WILSY-PTY-LTD"
    assert snapshot["signatory_mandate"]["mandate_scope"] == "INSTITUTIONAL_SIGNER"


def test_signer_provenance_rejects_adapter_record_for_a_different_lookup_reference():
    now = datetime.now(timezone.utc)
    result = SimpleNamespace(
        identity_proofing=_evidence_record(evidence_kind="IDENTITY_PROOFING"),
        signatory_mandate=_evidence_record(evidence_kind="SIGNATORY_MANDATE"),
    )
    with pytest.raises(HTTPException) as error:
        router._enrollment_provenance(
            result, tenant_id="WILSYTENANT-4CD2FZ4O",
            certificate_fingerprint_sha256="a" * 64,
            subject_principal_id="PRINCIPAL-1",
            identity_proofing_reference="evidence://identity/expected",
            signatory_mandate_reference="evidence://mandate/expected",
            evaluated_at=now,
        )
    assert error.value.detail == "INSTITUTIONAL_SIGNER_EVIDENCE_PROVENANCE_INVALID"


def test_signer_registry_rejects_caller_supplied_provenance_digest_mismatch():
    now = datetime.now(timezone.utc)
    result = SimpleNamespace(
        identity_proofing=_evidence_record(evidence_kind="IDENTITY_PROOFING"),
        signatory_mandate=_evidence_record(evidence_kind="SIGNATORY_MANDATE"),
    )
    snapshot, _digest = router._enrollment_provenance(
        result, tenant_id="WILSYTENANT-4CD2FZ4O",
        certificate_fingerprint_sha256="a" * 64,
        subject_principal_id="PRINCIPAL-1",
        identity_proofing_reference="evidence://source/record-001",
        signatory_mandate_reference="evidence://source/record-001",
        evaluated_at=now,
    )

    class _NeverRead:
        def find_one(self, *_args, **_kwargs):
            raise AssertionError("digest mismatch must fail before any database read")

    registry = InstitutionalSignerEnrollmentRegistry(_NeverRead(), _NeverRead())
    with pytest.raises(InstitutionalSignerRegistryError) as error:
        registry.request_enrollment(
            tenant_id="WILSYTENANT-4CD2FZ4O",
            certificate_fingerprint_sha256="a" * 64,
            certificate_serial_number_hex="abc123",
            subject_common_name="WILSY Authorised Signatory",
            issuer_common_name="WILSY Intermediate CA",
            issuer_subject_sha256="c" * 64,
            trust_root_sha256="b" * 64,
            identity_proofing_evidence_reference="evidence://identity/1",
            signatory_mandate_evidence_reference="evidence://mandate/1",
            requested_by_principal_id="PRINCIPAL-1",
            requested_at=now, idempotency_key="request-digest-mismatch",
            session=object(), evidence_provenance_fingerprint_sha256="0" * 64,
            evidence_provenance_snapshot=snapshot,
        )
    assert error.value.code == "INSTITUTIONAL_SIGNER_EVIDENCE_PROVENANCE_DIGEST_MISMATCH"


# WILSY OS SOVEREIGN ARTIFACT SEAL
# ARTIFACT: test_institutional_signer_router.py
# VERSION: v1.0.1-P12C-INSTITUTIONAL-SIGNER-PROVENANCE-CERT
# AUTHORITY BOUNDARY: direct signer HTTP readiness and provenance tests only
# TENANT POSTURE: exact tenant and evidence subject bindings are required
# FAIL-CLOSED POSTURE: unavailable, stale, mismatched, or incomplete evidence rejects
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively
# END OF WILSY OS SOVEREIGN ARTIFACT
