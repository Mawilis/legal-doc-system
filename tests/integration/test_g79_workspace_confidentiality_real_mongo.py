"""G79-R18: canonical lifecycle workspace denial on real MongoDB.

Existing D15 fixture injects an authorized context. This verifies
tenant/product/workspace behavior, not a live authentication flow.
"""
import uuid

from test_legal_operations_practice_workspace_real_mongo import (
    mongo_context,
    _register_intake,
    _persist_product,
    _workspace,
)


def test_populated_canonical_workspace_denied_without_clearance(
    mongo_context, monkeypatch
):
    tenant = "tenant-g79-" + uuid.uuid4().hex
    _register_intake(
        tenant_id=tenant,
        client=mongo_context["client"],
        lifecycle=mongo_context["lifecycle"],
        suffix="g79-restricted",
    )
    _persist_product(
        tenant_id=tenant,
        mongo_context=mongo_context,
        activate=True,
    )

    response = _workspace(
        tenant_id=tenant,
        mongo_context=mongo_context,
        monkeypatch=monkeypatch,
    )

    assert response.status_code == 503
    assert response.json() == {
        "detail": "LEGAL_OPERATIONS_WORKSPACE_MATTER_CLEARANCE_UNAVAILABLE"
    }
    for secret in (
        "matter-g79-restricted",
        "CASE-g79-restricted",
        "instruction-g79-restricted",
        "document-g79-restricted",
        "evidence_identity",
    ):
        assert secret not in response.text


def test_foreign_tenant_and_own_restricted_matter_never_leak(
    mongo_context, monkeypatch
):
    tenant = "tenant-own-" + uuid.uuid4().hex
    foreign = "tenant-other-" + uuid.uuid4().hex
    _register_intake(
        tenant_id=tenant,
        client=mongo_context["client"],
        lifecycle=mongo_context["lifecycle"],
        suffix="g79-own",
    )
    _register_intake(
        tenant_id=foreign,
        client=mongo_context["client"],
        lifecycle=mongo_context["lifecycle"],
        suffix="g79-foreign",
    )
    _persist_product(
        tenant_id=tenant,
        mongo_context=mongo_context,
        activate=True,
    )
    response = _workspace(
        tenant_id=tenant,
        mongo_context=mongo_context,
        monkeypatch=monkeypatch,
    )
    assert response.status_code == 503
    assert response.json()["detail"] == (
        "LEGAL_OPERATIONS_WORKSPACE_MATTER_CLEARANCE_UNAVAILABLE"
    )
    for forbidden in (
        "matter-g79-own", "matter-g79-foreign",
        "CASE-g79-own", "CASE-g79-foreign",
        foreign, "evidence_identity",
    ):
        assert forbidden not in response.text


def test_empty_active_workspace_is_valid_zero_disclosure(
    mongo_context, monkeypatch
):
    tenant = "tenant-empty-" + uuid.uuid4().hex
    _persist_product(
        tenant_id=tenant,
        mongo_context=mongo_context,
        activate=True,
    )
    response = _workspace(
        tenant_id=tenant,
        mongo_context=mongo_context,
        monkeypatch=monkeypatch,
    )
    assert response.status_code == 200
    body = response.json()
    for group in (
        "matters", "instructions", "documents",
        "attempts", "executions", "returns",
    ):
        assert body[group] == []
        assert body["summary"][group + "_total"] == 0


def test_unavailable_product_precedes_matter_disclosure(
    mongo_context, monkeypatch
):
    tenant = "tenant-pending-" + uuid.uuid4().hex
    _register_intake(
        tenant_id=tenant,
        client=mongo_context["client"],
        lifecycle=mongo_context["lifecycle"],
        suffix="g79-pending",
    )
    response = _workspace(
        tenant_id=tenant,
        mongo_context=mongo_context,
        monkeypatch=monkeypatch,
    )
    assert response.status_code == 403
    assert response.json() == {
        "detail": "LEGAL_OPERATIONS_PRODUCT_UNAVAILABLE"
    }
    assert "matter-g79-pending" not in response.text
