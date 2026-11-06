"""Certificates for source-local optional authorization in unified My Work."""

from __future__ import annotations

import asyncio

import pytest

from tools.eos.api import tenant_authorization_http as boundary
from tools.eos.api.exceptions import ForbiddenOperationException, WilsyAPIException


def _args():
    return (object(), object(), "tenant-a", object(), object(), object())


def test_optional_authorization_omits_only_a_canonical_source_denial(monkeypatch):
    dependency = boundary.OptionalTenantAuthorization("crm:work_item:read", "crm_work_item_read")

    async def denied(*_args):
        raise ForbiddenOperationException("denied")

    monkeypatch.setattr(dependency, "_required", denied)
    assert asyncio.run(dependency(*_args())) is None


def test_optional_authorization_preserves_authorized_source_context(monkeypatch):
    dependency = boundary.OptionalTenantAuthorization("operations:work_item:read", "operations_work_item_read")
    expected = object()

    async def admitted(*_args):
        return expected

    monkeypatch.setattr(dependency, "_required", admitted)
    assert asyncio.run(dependency(*_args())) is expected


@pytest.mark.parametrize(
    "failure",
    [
        WilsyAPIException("authority unavailable", status_code=503),
        RuntimeError("unexpected dependency failure"),
    ],
)
def test_optional_authorization_never_converts_dependency_outage_to_empty_source(monkeypatch, failure):
    dependency = boundary.OptionalTenantAuthorization("intelligence:work_item:read", "intelligence_work_item_read")

    async def unavailable(*_args):
        raise failure

    monkeypatch.setattr(dependency, "_required", unavailable)
    with pytest.raises(type(failure)):
        asyncio.run(dependency(*_args()))


def test_optional_authorization_declares_no_permission_or_persistence_authority():
    dependency = boundary.OptionalTenantAuthorization("legal_operations:productive_work:read", "legal_productive_work_read")
    assert dependency._required.permission_id == "legal_operations:productive_work:read"
    assert dependency._required.operation == "legal_productive_work_read"
