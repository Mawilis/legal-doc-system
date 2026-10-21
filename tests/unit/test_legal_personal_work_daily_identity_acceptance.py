"""G79-R8 personal-work identity and route-separation acceptance.

These are endpoint composition tests. They do not certify real
MongoDB persistence or independently authenticate HTTP requests.
"""

import asyncio
from types import SimpleNamespace
from typing import cast

from tools.eos.api.tenant_authorization_http import TenantAuthorizationContext
from unittest.mock import Mock

import pytest

from tools.eos.api import legal_operations_router as router


@pytest.mark.parametrize(
    "principal",
    ("partner-01", "attorney-02", "paralegal-03",
     "secretary-04"),
)
def test_personal_work_projection_uses_authenticated_principal(
    monkeypatch, principal
):
    calls = []
    session = object()
    database = object()
    projection = object()

    class Service:
        def project(self, **kwargs):
            calls.append(kwargs)
            return projection

    monkeypatch.setattr(
        router,
        "_productive_work_projection_transaction",
        lambda callback: callback(session, database),
    )
    monkeypatch.setattr(
        router,
        "_productive_work_service",
        lambda db: Service() if db is database else
        (_ for _ in ()).throw(AssertionError("WRONG_DATABASE")),
    )
    monkeypatch.setattr(
        router, "_productive_work_payload",
        lambda value: {"work_items": []}
        if value is projection else
        (_ for _ in ()).throw(AssertionError("WRONG_PROJECTION")),
    )

    context = SimpleNamespace(
        tenant_id="tenant-certified",
        identity=SimpleNamespace(identity_id=principal),
    )
    result = asyncio.run(
        router.get_legal_productive_work_projection(context=cast(TenantAuthorizationContext, context))
    )

    assert result == {"work_items": []}
    assert len(calls) == 1
    assert calls[0]["tenant_id"] == "tenant-certified"
    assert calls[0]["principal_id"] == principal
    assert calls[0]["session"] is session
    assert "as_of" in calls[0]
    assert "role" not in calls[0]
    assert "authorized_principal_id" not in calls[0]


def test_personal_work_route_is_separate_from_practice_wall_guard(
    monkeypatch,
):
    session = object()
    projection = object()

    class Service:
        def project(self, **kwargs):
            assert kwargs["principal_id"] == "worker-01"
            assert kwargs["session"] is session
            return projection

    def forbidden_guard(**kwargs):
        raise AssertionError("PRACTICE_GUARD_USED_ON_PERSONAL_ROUTE")

    monkeypatch.setattr(
        router, "_require_workspace_disclosure_clearance",
        forbidden_guard,
    )
    monkeypatch.setattr(
        router, "_productive_work_projection_transaction",
        lambda callback: callback(session, object()),
    )
    monkeypatch.setattr(
        router, "_productive_work_service",
        lambda database: Service(),
    )
    monkeypatch.setattr(
        router, "_productive_work_payload",
        lambda value: {"own_work": True},
    )

    context = SimpleNamespace(
        tenant_id="tenant-certified",
        identity=SimpleNamespace(identity_id="worker-01"),
    )

    result = asyncio.run(
        router.get_legal_productive_work_projection(context=cast(TenantAuthorizationContext, context))
    )
    assert result == {"own_work": True}
