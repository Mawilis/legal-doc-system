"""Read-only HTTP certification for the controlled Issue #300 readiness surface."""
from __future__ import annotations

import asyncio
from types import SimpleNamespace

import pytest
from fastapi import HTTPException

from tools.eos.api.tenant_router import get_tenant_ownership_readiness


def test_readiness_reports_explicit_deny_without_database_or_write_authority() -> None:
    response = asyncio.run(
        get_tenant_ownership_readiness(
            tenant_id="tenant-qa-001",
            request=object(),  # type: ignore[arg-type]
            authorization=SimpleNamespace(tenant_id="tenant-qa-001"),  # type: ignore[arg-type]
        )
    )
    assert response.model_dump() == {
        "tenant_id": "tenant-qa-001",
        "status": "DENY",
        "reason": "OWNERSHIP_EVIDENCE_AUTHORITY_UNAVAILABLE",
        "positive_operations_enabled": False,
    }


def test_readiness_rejects_cross_tenant_authorization_scope() -> None:
    with pytest.raises(HTTPException) as raised:
        asyncio.run(
            get_tenant_ownership_readiness(
                tenant_id="tenant-target",
                request=object(),  # type: ignore[arg-type]
                authorization=SimpleNamespace(tenant_id="tenant-other"),  # type: ignore[arg-type]
            )
        )
    assert raised.value.status_code == 403
    assert raised.value.detail == "TENANT_SCOPE_PATH_MISMATCH"
