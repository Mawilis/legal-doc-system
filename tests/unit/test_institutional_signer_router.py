"""Institutional signer HTTP runtime readiness and request-path DDL boundaries."""
from __future__ import annotations

from datetime import datetime, timezone
from types import SimpleNamespace

import pytest
from fastapi import HTTPException

from tools.eos.api import institutional_signer_router as router
from tools.eos.security.institutional_signer_enrollment_registry import (
    InstitutionalSignerEnrollmentRegistry,
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
        "valid_from": now.replace(year=now.year - 1),
        "valid_until": None,
        "revoked": False,
        "verified_at": now,
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
            evidence_kind="SIGNATORY_MANDATE",
            legal_entity_reference="WILSY-PTY-LTD",
            mandate_scope="INSTITUTIONAL_SIGNER",
        ),
    )
    result.identity_proofing.evidence_kind = "IDENTITY_PROOFING"
    snapshot, digest = router._enrollment_provenance(
        result, tenant_id="WILSYTENANT-4CD2FZ4O",
        certificate_fingerprint_sha256="a" * 64,
        subject_principal_id="PRINCIPAL-1", evaluated_at=now,
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
