"""G79-R20: invalid lineage is a bounded non-disclosing HTTP 503."""

import asyncio
from typing import cast

import pytest
from fastapi import HTTPException

from tools.eos.api import legal_operations_router as router
from tools.eos.api.tenant_authorization_http import TenantAuthorizationContext
from tools.eos.legal_operations.service.legal_practice_workspace_matter_lineage import (
    MatterLineageError,
)

EXPECTED = "LEGAL_OPERATIONS_WORKSPACE_PARENT_LINEAGE_INVALID"

@pytest.mark.parametrize(
    "secret",
    (
        "restricted-matter-123",
        "confidential-client-name",
        "opaque-snapshot-locator",
    ),
)
def test_parent_corruption_returns_specific_non_disclosing_503(
    monkeypatch, secret
):
    monkeypatch.setattr(
        router, "_workspace_context",
        lambda *contexts: object(),
    )

    def failed_snapshot(callback):
        raise MatterLineageError(secret)

    monkeypatch.setattr(
        router, "_workspace_projection_transaction",
        failed_snapshot,
    )

    with pytest.raises(HTTPException) as exc:
        asyncio.run(
            router.get_legal_practice_workspace_projection(
                cast(TenantAuthorizationContext, object()), cast(TenantAuthorizationContext, object()), cast(TenantAuthorizationContext, object()), cast(TenantAuthorizationContext, object())
            )
        )
    assert exc.value.status_code == 503
    assert exc.value.detail == EXPECTED
    assert secret not in str(exc.value.detail)

def test_lineage_error_is_not_positive_authorization():
    assert not hasattr(router, "issue_workspace_wall_clearance")
    assert not hasattr(router, "grant_workspace_matter_access")
