"""P7 authenticated read-after-write daily-work acceptance.

Production IAM, read and completion routers remain unmodified.
All legal and authorization evidence is durable in one disposable Mongo DB.
"""

from uuid import uuid4

import pytest
from fastapi.testclient import TestClient

import test_legal_operations_command_router_real_mongo as host
import test_legal_work_completion_http_real_mongo as completion

import tools.eos.api.legal_operations_command_router as command_router
import tools.eos.api.legal_operations_router as read_router

from tools.eos.legal_operations.registry.legal_work_item_registry import (
    COLLECTION_NAME as WORK_COLLECTION,
)
from tools.eos.legal_operations.registry.legal_work_completion_event_registry import (
    COLLECTION_NAME as COMPLETION_COLLECTION,
)
from tools.eos.auth.tenant_authorization_decision_evidence_registry import (
    COLLECTION as IAM_COLLECTION,
)


mongo_context = host.mongo_context


def test_authenticated_assigned_work_completion_read_after_write(
    mongo_context,
    monkeypatch: pytest.MonkeyPatch,
):
    database = mongo_context["database"]
    client = mongo_context["client"]

    # Override only the owned database handles, never sovereign IAM
    # verdicts, completion authority or currentness evaluation.
    monkeypatch.setattr(
        command_router,
        "_db_handles",
        lambda: (client, database),
    )
    monkeypatch.setattr(
        read_router,
        "_db_handles",
        lambda: (client, database),
    )

    fixture = host._seed_fixture(
        mongo_context["collections"],
        business_role="tenant_legal_partner",
        grant_role="LEGAL_PARTNER",
    )

    tenant = fixture.tenant
    principal = fixture.principal_id
    work_id = "p7-closed-loop-" + uuid4().hex

    work, assignment = completion._seed_completion_stack(
        mongo_context,
        tenant_id=tenant,
        principal_id=principal,
        work_item_id=work_id,
    )

    before_record = database[WORK_COLLECTION].find_one({
        "tenant_id": tenant,
        "work_item_id": work_id,
    })
    assert before_record is not None

    app = host._app(mongo_context, fixture)
    app.include_router(read_router.router, prefix="/api")

    headers = {"X-Tenant-ID": tenant}
    read_path = "/api/legal-operations/productive-work"
    completion_path = (
        "/api/legal-operations/work-items/"
        f"{work_id}/completion"
    )

    with TestClient(app) as api:
        before = api.get(read_path, headers=headers)
        assert before.status_code == 200, before.text

        before_body = before.json()
        assert before_body["tenant_id"] == tenant
        assert before_body["principal_id"] == principal
        assert work_id in {
            value["work_item_id"]
            for value in before_body["assigned_work_items"]
        }, "WORK_NOT_VISIBLE_BEFORE_COMPLETION"

        completed = api.post(
            completion_path,
            headers=headers,
            json={
                "completion_evidence_reference":
                    "evidence:p7-closed-loop:" + work_id,
                "completion_evidence_fingerprint": "a" * 128,
            },
        )
        assert completed.status_code == 200, completed.text
        assert completed.json()["data"]["work_item_id"] == work_id

        after = api.get(read_path, headers=headers)
        assert after.status_code == 200, after.text

        after_body = after.json()
        assert after_body["tenant_id"] == tenant
        assert after_body["principal_id"] == principal
        assert work_id not in {
            value["work_item_id"]
            for value in after_body["assigned_work_items"]
        }, "COMPLETED_WORK_STILL_ACTIVE"

        assert work_id not in {
            value["work_item_id"]
            for value in after_body["overdue_work_items"]
        }
        assert work_id not in {
            value["work_item_id"]
            for value in after_body["due_soon_work_items"]
        }

        # Existing canonical tenant isolation must remain intact.
        foreign = api.get(
            read_path,
            headers={"X-Tenant-ID": "foreign-" + uuid4().hex},
        )
        assert foreign.status_code != 200
        assert work_id not in foreign.text

    after_record = database[WORK_COLLECTION].find_one({
        "tenant_id": tenant,
        "work_item_id": work_id,
    })

    assert after_record == before_record, (
        "IMMUTABLE_WORK_ITEM_WAS_MUTATED"
    )

    assert database[COMPLETION_COLLECTION].count_documents({
        "tenant_id": tenant,
        "work_item_id": work_id,
    }) == 1

    assert database[IAM_COLLECTION].count_documents({
        "tenant_id": tenant,
        "principal_id": principal,
        "operation": completion.OPERATION,
        "permission": completion.PERMISSION,
    }) == 1

    assert assignment.work_item_id == work.work_item_id
