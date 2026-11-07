"""Institutional signer HTTP runtime readiness and request-path DDL boundaries."""
from __future__ import annotations

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
            evaluated_at=__import__("datetime").datetime.now(__import__("datetime").timezone.utc),
            session=object(),
        )
    assert error.value.status_code == 503
    assert error.value.detail == "INSTITUTIONAL_SIGNER_EVIDENCE_AUTHORITY_UNAVAILABLE"


def test_signer_evidence_verifier_requires_a_canonical_provenance_fingerprint():
    with pytest.raises(HTTPException) as error:
        router._provenance_fingerprint(SimpleNamespace(provenance_fingerprint_sha256="unverified"))
    assert error.value.status_code == 503
    assert error.value.detail == "INSTITUTIONAL_SIGNER_EVIDENCE_PROVENANCE_INVALID"
