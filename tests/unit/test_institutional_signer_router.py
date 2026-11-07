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
