"""
P14-R20R28 authenticated FastAPI + real-Mongo Legal completion certificate.

This test does not replace, monkeypatch or stub R20R20/R20R23/R20R22/R20R18.
Authentication identity is injected only through the existing production
FastAPI dependency-override harness. Durable IAM, work, assignment, IAM
evidence and completion evidence remain real Mongo facts.
"""

from __future__ import annotations

from typing import Any
from uuid import uuid4

import pytest

import test_legal_operations_command_router_real_mongo as http_harness
import test_legal_work_completion_authority_persistence_real_mongo as r20r26

from tools.eos.auth.tenant_authorization_decision_evidence_registry import (
    COLLECTION as IAM_EVIDENCE_COLLECTION,
    TenantAuthorizationDecisionEvidenceRegistry,
)
from tools.eos.legal_operations.registry.legal_work_assignment_registry import (
    COLLECTION_NAME as WORK_ASSIGNMENT_COLLECTION,
    LegalWorkAssignmentRegistry,
)
from tools.eos.legal_operations.registry.legal_work_completion_event_registry import (
    COLLECTION_NAME as COMPLETION_COLLECTION,
    LegalWorkCompletionEventRegistry,
)
from tools.eos.legal_operations.registry.legal_work_item_registry import (
    COLLECTION_NAME as WORK_ITEM_COLLECTION,
    LegalWorkItemRegistry,
)


PERMISSION = "legal_operations:work_item:complete"
OPERATION = "legal_work_item_complete"
HEX_A = "a" * 128


# Re-export only the proven real-Mongo fixture.
mongo_context = http_harness.mongo_context


def _ensure_completion_indexes(
    context: dict[str, Any],
) -> None:
    database = context["database"]
    collections = context["collections"]

    LegalWorkItemRegistry(
        database[WORK_ITEM_COLLECTION]
    ).ensure_indexes()

    LegalWorkAssignmentRegistry(
        database[WORK_ASSIGNMENT_COLLECTION]
    ).ensure_indexes()

    LegalWorkCompletionEventRegistry(
        database[COMPLETION_COLLECTION]
    ).ensure_indexes()

    issuer = TenantAuthorizationDecisionEvidenceRegistry(
        database[IAM_EVIDENCE_COLLECTION],
        principal_repository=http_harness._PrincipalReader(
            collections["principal"]
        ),
        membership_repository=http_harness._MembershipReader(
            collections["membership"]
        ),
        role_assignment_repository=http_harness._RoleReader(
            collections["roles"],
            collections["business_roles"],
        ),
        business_role_repository=http_harness._RoleReader(
            collections["roles"],
            collections["business_roles"],
        ),
    )
    issuer.ensure_indexes()


def _seed_completion_stack(
    context: dict[str, Any],
    *,
    tenant_id: str,
    principal_id: str,
    work_item_id: str,
) -> tuple[Any, Any]:
    client = context["client"]
    database = context["database"]

    _ensure_completion_indexes(
        context
    )

    work = r20r26._work(
        tenant_id=tenant_id,
        work_item_id=work_item_id,
    )

    assignment = r20r26._assignment(
        tenant_id=tenant_id,
        principal_id=principal_id,
        work=work,
    )

    work_registry = LegalWorkItemRegistry(
        database[WORK_ITEM_COLLECTION]
    )

    assignment_registry = LegalWorkAssignmentRegistry(
        database[WORK_ASSIGNMENT_COLLECTION]
    )

    with client.start_session() as session:
        session.start_transaction()

        work_registry.create_or_replay(
            work,
            session=session,
        )

        assignment_registry.persist(
            assignment,
            session=session,
        )

        session.commit_transaction()

    return work, assignment


def _post_completion(
    context: dict[str, Any],
    fixture: Any,
    *,
    principal_id: str,
    work_item_id: str,
    reference: str,
    fingerprint: str = HEX_A,
    tenant: str | None = None,
    extra: dict[str, Any] | None = None,
) -> Any:
    payload: dict[str, Any] = {
        "completion_evidence_reference": reference,
        "completion_evidence_fingerprint": fingerprint,
    }

    if extra:
        payload.update(extra)

    return http_harness._post(
        context,
        fixture,
        (
            "/api/legal-operations/work-items/"
            f"{work_item_id}/completion"
        ),
        payload,
        tenant=tenant,
        principal_id=principal_id,
    )


def test_real_authenticated_http_completion_persists_one_iam_and_completion_fact(
    mongo_context: dict[str, Any],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    import tools.eos.api.legal_operations_command_router as command_api

    monkeypatch.setattr(
        command_api,
        "_db_handles",
        lambda: (
            mongo_context["client"],
            mongo_context["database"],
        ),
    )
    fixture = http_harness._seed_fixture(
        mongo_context["collections"],
        business_role="tenant_legal_partner",
        grant_role="LEGAL_PARTNER",
    )
    tenant = fixture.tenant
    principal = fixture.principal_id
    work_id = (
        "work-completion-http-"
        + uuid4().hex
    )

    work, _ = _seed_completion_stack(
        mongo_context,
        tenant_id=tenant,
        principal_id=principal,
        work_item_id=work_id,
    )

    response = _post_completion(
        mongo_context,
        fixture,
        principal_id=principal,
        work_item_id=work_id,
        reference=(
            "completion-http-source:"
            + work_id
        ),
    )

    assert response.status_code == 200, response.text

    data = response.json()["data"]

    assert data["tenant_id"] == tenant
    assert data["work_item_id"] == work_id
    assert (
        data["work_item_fingerprint"]
        == work.fingerprint
    )

    database = mongo_context["database"]

    assert database[
        IAM_EVIDENCE_COLLECTION
    ].count_documents(
        {
            "tenant_id": tenant,
            "principal_id": principal,
            "operation": OPERATION,
            "permission": PERMISSION,
        }
    ) == 1

    assert database[
        COMPLETION_COLLECTION
    ].count_documents(
        {
            "tenant_id": tenant,
            "work_item_id": work_id,
        }
    ) == 1


def test_real_authenticated_http_exact_retry_keeps_one_completion_fact(
    mongo_context: dict[str, Any],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    import tools.eos.api.legal_operations_command_router as command_api

    monkeypatch.setattr(
        command_api,
        "_db_handles",
        lambda: (
            mongo_context["client"],
            mongo_context["database"],
        ),
    )
    fixture = http_harness._seed_fixture(
        mongo_context["collections"],
        business_role="tenant_legal_partner",
        grant_role="LEGAL_PARTNER",
    )
    tenant = fixture.tenant
    principal = fixture.principal_id
    work_id = (
        "work-completion-replay-"
        + uuid4().hex
    )

    _seed_completion_stack(
        mongo_context,
        tenant_id=tenant,
        principal_id=principal,
        work_item_id=work_id,
    )

    reference = (
        "completion-http-replay:"
        + work_id
    )

    first = _post_completion(
        mongo_context,
        fixture,
        principal_id=principal,
        work_item_id=work_id,
        reference=reference,
    )

    assert first.status_code == 200, first.text

    replay = _post_completion(
        mongo_context,
        fixture,
        principal_id=principal,
        work_item_id=work_id,
        reference=reference,
    )

    assert replay.status_code == 200, replay.text
    assert replay.json()["data"] == first.json()["data"]

    database = mongo_context["database"]

    assert database[
        IAM_EVIDENCE_COLLECTION
    ].count_documents(
        {
            "tenant_id": tenant,
            "principal_id": principal,
            "operation": OPERATION,
            "permission": PERMISSION,
        }
    ) == 1

    assert database[
        COMPLETION_COLLECTION
    ].count_documents(
        {
            "tenant_id": tenant,
            "work_item_id": work_id,
        }
    ) == 1


def test_real_http_rejects_client_authority_fields_before_persistence(
    mongo_context: dict[str, Any],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    import tools.eos.api.legal_operations_command_router as command_api

    monkeypatch.setattr(
        command_api,
        "_db_handles",
        lambda: (
            mongo_context["client"],
            mongo_context["database"],
        ),
    )
    fixture = http_harness._seed_fixture(
        mongo_context["collections"],
        business_role="tenant_legal_partner",
        grant_role="LEGAL_PARTNER",
    )
    tenant = fixture.tenant
    principal = fixture.principal_id
    work_id = (
        "work-completion-extra-"
        + uuid4().hex
    )

    _seed_completion_stack(
        mongo_context,
        tenant_id=tenant,
        principal_id=principal,
        work_item_id=work_id,
    )

    response = _post_completion(
        mongo_context,
        fixture,
        principal_id=principal,
        work_item_id=work_id,
        reference=(
            "completion-http-extra:"
            + work_id
        ),
        extra={
            "tenant_id": tenant,
            "principal_id": principal,
            "evaluated_at": (
                "2026-10-17T00:00:00+00:00"
            ),
            "work_item_fingerprint": HEX_A,
        },
    )

    assert response.status_code == 422, response.text

    database = mongo_context["database"]

    assert database[
        COMPLETION_COLLECTION
    ].count_documents(
        {
            "tenant_id": tenant,
            "work_item_id": work_id,
        }
    ) == 0


def test_real_http_unauthorized_principal_cannot_complete_assigned_work(
    mongo_context: dict[str, Any],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    import tools.eos.api.legal_operations_command_router as command_api

    monkeypatch.setattr(
        command_api,
        "_db_handles",
        lambda: (
            mongo_context["client"],
            mongo_context["database"],
        ),
    )
    fixture = http_harness._seed_fixture(
        mongo_context["collections"],
        business_role="tenant_legal_partner",
        grant_role="LEGAL_PARTNER",
    )
    tenant = fixture.tenant
    assigned_principal = fixture.principal_id
    attacker = (
        "principal-completion-attacker-"
        + uuid4().hex
    )
    work_id = (
        "work-completion-denied-"
        + uuid4().hex
    )

    _seed_completion_stack(
        mongo_context,
        tenant_id=tenant,
        principal_id=assigned_principal,
        work_item_id=work_id,
    )

    response = _post_completion(
        mongo_context,
        fixture,
        principal_id=attacker,
        work_item_id=work_id,
        reference=(
            "completion-http-denied:"
            + work_id
        ),
    )

    assert response.status_code in {
        401,
        403,
    }, response.text

    assert mongo_context["database"][
        COMPLETION_COLLECTION
    ].count_documents(
        {
            "tenant_id": tenant,
            "work_item_id": work_id,
        }
    ) == 0


def test_real_http_foreign_tenant_fails_closed_without_completion_fact(
    mongo_context: dict[str, Any],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    import tools.eos.api.legal_operations_command_router as command_api

    monkeypatch.setattr(
        command_api,
        "_db_handles",
        lambda: (
            mongo_context["client"],
            mongo_context["database"],
        ),
    )
    fixture = http_harness._seed_fixture(
        mongo_context["collections"],
        business_role="tenant_legal_partner",
        grant_role="LEGAL_PARTNER",
    )
    tenant = fixture.tenant
    foreign_tenant = (
        "tenant-foreign-"
        + uuid4().hex
    )
    principal = fixture.principal_id
    work_id = (
        "work-completion-tenant-"
        + uuid4().hex
    )

    _seed_completion_stack(
        mongo_context,
        tenant_id=tenant,
        principal_id=principal,
        work_item_id=work_id,
    )

    response = _post_completion(
        mongo_context,
        fixture,
        principal_id=principal,
        work_item_id=work_id,
        reference=(
            "completion-http-foreign:"
            + work_id
        ),
        tenant=foreign_tenant,
    )

    assert response.status_code != 200, response.text

    assert mongo_context["database"][
        COMPLETION_COLLECTION
    ].count_documents(
        {
            "work_item_id": work_id,
        }
    ) == 0


def test_certificate_allows_only_owned_database_handle_binding(
) -> None:
    import ast
    from pathlib import Path

    tree = ast.parse(
        Path(__file__).read_text(
            encoding="utf-8"
        )
    )

    patch_targets: list[str] = []

    for node in ast.walk(tree):
        if not isinstance(
            node,
            ast.Call,
        ):
            continue

        if not (
            isinstance(node.func, ast.Attribute)
            and node.func.attr == "setattr"
        ):
            continue

        if len(node.args) < 3:
            patch_targets.append("MALFORMED")
            continue

        target = ast.unparse(node.args[0])
        attribute = ast.literal_eval(node.args[1])

        patch_targets.append(
            f"{target}.{attribute}"
        )

    assert patch_targets
    assert set(patch_targets) == {
        "command_api._db_handles"
    }

    text = Path(__file__).read_text(
        encoding="utf-8"
    )

    for forbidden in (
        "record_legal_work_completion",
        "compose_legal_work_completion_authority_evidence",
        "prepare_legal_work_completion",
        "LegalWorkCompletionEventRegistry.create_or_replay",
        "TenantAuthorizationDecisionEvidenceRegistry.issue",
    ):
        assert (
            f'monkeypatch.setattr({forbidden}'
            not in text
        )
