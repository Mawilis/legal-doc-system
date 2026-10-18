"""
WILSY P4-P2 authenticated Temporal Operations real-Mongo HTTP certificate.

Reuses the durable Productive Work IAM HTTP harness without overriding
the RequireTenantAuthorization Productive Work permission.

No new IAM, visibility authority, persistence model or legal execution.
"""
from __future__ import annotations

import importlib.util
import os
import uuid
from datetime import timedelta
from pathlib import Path
from typing import Any

import pytest

from fastapi.testclient import TestClient
from pymongo import MongoClient

import tools.eos.api.legal_operations_router as legal_router
from tools.eos.legal_operations.domain.legal_matter_deadline import (
    LegalMatterDeadline,
)
from tools.eos.legal_operations.registry import (
    legal_matter_deadline_registry as deadline_registry,
)

URI = os.environ["WILSY_P4_TEMPORAL_MONGO_URI"]

# The existing certified harness uses its own environment variable.
os.environ["WILSY_PW_HTTP_REAL_MONGO_URI"] = URI

HARNESS_PATH = Path(__file__).with_name(
    "test_legal_productive_work_http_real_mongo.py"
)

spec = importlib.util.spec_from_file_location(
    "_wilsy_temporal_productive_http_harness",
    HARNESS_PATH,
)
assert spec is not None and spec.loader is not None
harness = importlib.util.module_from_spec(spec)
spec.loader.exec_module(harness)

NOW = harness.NOW
PATH = "/api/legal-operations/temporal-operations"


def _deadline(
    identity: str,
    matter: str,
    tenant: str,
    days: int,
) -> LegalMatterDeadline:
    return LegalMatterDeadline(
        tenant_id=tenant,
        case_matter_id=matter,
        deadline_id=identity,
        deadline_kind="FILING",
        title=identity,
        due_at=NOW + timedelta(days=days),
        source_type="COURT_ORDER",
        source_reference=f"evidence:{identity}",
        source_evidence_fingerprint="b" * 128,
        jurisdiction_reference="jurisdiction:za-high-court",
        created_at=NOW,
    )


def test_real_iam_temporal_http_visibility_and_provenance(
    monkeypatch: Any,
) -> None:
    client: MongoClient[Any] = MongoClient(
        URI,
        serverSelectionTimeoutMS=5000,
        uuidRepresentation="standard",
    )
    database = client[
        "wilsy_p4_temporal_http_" + uuid.uuid4().hex
    ]
    tenant = "tenant-p4-http-" + uuid.uuid4().hex
    principal = "principal-p4-http-" + uuid.uuid4().hex

    try:
        hello = client.admin.command("hello")
        assert hello.get("isWritablePrimary") is True
        assert hello.get("logicalSessionTimeoutMinutes") is not None

        values = harness._collections(database)
        harness._ensure_indexes(values)

        collection = database[
            deadline_registry.COLLECTION
        ]
        deadline_registry.ensure_indexes(collection)

        harness._seed_iam(values, principal, tenant)
        harness._seed_work(client, values, principal, tenant)

        with client.start_session() as session:
            with session.start_transaction():
                for item in (
                    _deadline(
                        "deadline-visible",
                        "matter-http-1",
                        tenant,
                        2,
                    ),
                    _deadline(
                        "deadline-hidden",
                        "matter-hidden",
                        tenant,
                        1,
                    ),
                    _deadline(
                        "deadline-foreign",
                        "matter-http-1",
                        "tenant-foreign-" + uuid.uuid4().hex,
                        0,
                    ),
                ):
                    deadline_registry.persist_deadline(
                        item,
                        collection,
                        session=session,
                    )

        # The real RequireTenantAuthorization dependency is retained.
        # Only the test identity/repository wiring is controlled.
        app = harness._app(
            client, database, values, principal, tenant
        )
        monkeypatch.setattr(
            legal_router,
            "_db_handles",
            lambda: (client, database),
        )

        with TestClient(app) as api:
            response = api.get(
                PATH,
                headers={"X-Tenant-ID": tenant},
                params={
                    "tenant_id": "foreign-tenant",
                    "principal_id": "foreign-principal",
                    "case_matter_id": "matter-hidden",
                },
            )

        assert response.status_code == 200, response.text
        body = response.json()

        assert body["tenant_id"] == tenant
        assert body["principal_id"] == principal
        assert body["visible_matter_ids"] == ["matter-http-1"]
        assert [
            row["deadline_id"] for row in body["rows"]
        ] == ["deadline-visible"]

        row = body["rows"][0]
        assert row["case_matter_id"] == "matter-http-1"
        assert row["source_type"] == "COURT_ORDER"
        assert row["source_reference"] == "evidence:deadline-visible"
        assert row["source_evidence_fingerprint"] == "b" * 128
        assert row["due_at"] == (
            NOW + timedelta(days=2)
        ).isoformat()

        serialized = response.text.casefold()
        assert "deadline-hidden" not in serialized
        assert "deadline-foreign" not in serialized
        assert "foreign-principal" not in serialized
        assert "matter-hidden" not in serialized
        assert "payment" not in serialized
        assert "settlement" not in serialized

        assert values["work"].count_documents({}) == 1
        assert values["assignment"].count_documents({}) == 1
        assert values["supervision"].count_documents({}) == 0
        assert collection.count_documents({}) == 3

    finally:
        client.drop_database(database.name)
        client.close()


def test_real_iam_rejects_unknown_principal(
    monkeypatch: Any,
) -> None:
    client: MongoClient[Any] = MongoClient(
        URI,
        serverSelectionTimeoutMS=5000,
        uuidRepresentation="standard",
    )
    database = client[
        "wilsy_p4_temporal_denied_" + uuid.uuid4().hex
    ]
    tenant = "tenant-p4-denied-" + uuid.uuid4().hex
    principal = "principal-not-authorized-" + uuid.uuid4().hex

    try:
        values = harness._collections(database)
        harness._ensure_indexes(values)

        # No principal authority, membership or role is seeded.
        app = harness._app(
            client, database, values, principal, tenant
        )
        monkeypatch.setattr(
            legal_router,
            "_db_handles",
            lambda: (client, database),
        )

        with TestClient(app) as api:
            response = api.get(
                PATH,
                headers={"X-Tenant-ID": tenant},
            )

        assert response.status_code in (401, 403), response.text
        assert "rows" not in response.text
        assert "visible_matter_ids" not in response.text

    finally:
        client.drop_database(database.name)
        client.close()


def _assert_temporal_tenant_scope_denied(
    monkeypatch: Any,
    *,
    foreign_tenant: bool,
) -> None:
    """Exercise real IAM repositories; do not override final authorization."""
    client: MongoClient[Any] = MongoClient(
        URI,
        serverSelectionTimeoutMS=5000,
        uuidRepresentation="standard",
    )
    database = client[
        "wilsy_p4_temporal_scope_denied_" + uuid.uuid4().hex
    ]
    tenant = "tenant-p4-scope-" + uuid.uuid4().hex
    principal = "principal-p4-scope-" + uuid.uuid4().hex

    try:
        values = harness._collections(database)
        harness._ensure_indexes(values)
        harness._seed_iam(values, principal, tenant)

        deadline_collection = database[
            deadline_registry.COLLECTION
        ]
        deadline_registry.ensure_indexes(deadline_collection)

        before = {
            name: collection.count_documents({})
            for name, collection in values.items()
        }
        before["deadlines"] = deadline_collection.count_documents({})

        app = harness._app(
            client, database, values, principal, tenant
        )
        monkeypatch.setattr(
            legal_router,
            "_db_handles",
            lambda: (client, database),
        )

        headers = (
            {"X-Tenant-ID": "tenant-foreign-" + uuid.uuid4().hex}
            if foreign_tenant
            else {}
        )

        with TestClient(app) as api:
            response = api.get(
                PATH,
                headers=headers,
                params={
                    "tenant_id": tenant,
                    "principal_id": principal,
                    "case_matter_id": "matter-arbitrary",
                },
            )

        assert response.status_code == 403, response.text
        body = response.text.casefold()
        assert "visible_matter_ids" not in body
        assert "deadline_id" not in body
        assert "source_evidence_fingerprint" not in body
        assert "matter-arbitrary" not in body

        after = {
            name: collection.count_documents({})
            for name, collection in values.items()
        }
        after["deadlines"] = deadline_collection.count_documents({})
        assert after == before

    finally:
        client.drop_database(database.name)
        client.close()


def test_real_iam_temporal_missing_tenant_header_denied(
    monkeypatch: Any,
) -> None:
    _assert_temporal_tenant_scope_denied(
        monkeypatch,
        foreign_tenant=False,
    )


def test_real_iam_temporal_foreign_tenant_header_denied(
    monkeypatch: Any,
) -> None:
    _assert_temporal_tenant_scope_denied(
        monkeypatch,
        foreign_tenant=True,
    )


def _assert_temporal_lifecycle_denied(
    monkeypatch: Any,
    *,
    authority: str,
    status_name: str,
) -> None:
    """A durable lifecycle CAS must immediately remove HTTP access."""
    from tools.eos.auth.principal_authority import PrincipalAuthority
    from tools.eos.auth.principal_authority_repository import (
        PrincipalAuthorityRepository,
    )
    from tools.eos.auth.principal_status import PrincipalStatus
    from tools.eos.auth.tenant_membership import (
        TenantMembershipAuthority,
        TenantMembershipStatus,
    )
    from tools.eos.auth.tenant_membership_repository import (
        TenantMembershipRepository,
    )

    assert authority in ("membership", "principal")
    assert status_name in ("SUSPENDED", "REVOKED")

    client: MongoClient[Any] = MongoClient(
        URI,
        serverSelectionTimeoutMS=5000,
        uuidRepresentation="standard",
    )
    database = client[
        "wilsy_p4_temporal_lifecycle_" + uuid.uuid4().hex
    ]
    tenant = "tenant-p4-lifecycle-" + uuid.uuid4().hex
    principal = "principal-p4-lifecycle-" + uuid.uuid4().hex

    try:
        values = harness._collections(database)
        harness._ensure_indexes(values)
        harness._seed_iam(values, principal, tenant)

        deadline_collection = database[
            deadline_registry.COLLECTION
        ]
        deadline_registry.ensure_indexes(deadline_collection)

        desired: TenantMembershipAuthority | None = None
        desired_principal: PrincipalAuthority | None = None

        if authority == "membership":
            desired = TenantMembershipAuthority(
                principal,
                tenant,
                TenantMembershipStatus(status_name),
                1,
            )
            assert TenantMembershipRepository.compare_and_swap(
                desired,
                0,
                values["membership"],
            ) == desired
            assert TenantMembershipRepository.resolve(
                principal,
                tenant,
                values["membership"],
            ) == desired
        else:
            desired_principal = PrincipalAuthority(
                principal,
                PrincipalStatus(status_name),
                1,
            )
            assert PrincipalAuthorityRepository.compare_and_swap(
                desired_principal,
                0,
                values["principal"],
            ) == desired_principal
            assert PrincipalAuthorityRepository.get(
                principal,
                values["principal"],
            ) == desired_principal

        before = {
            name: collection.count_documents({})
            for name, collection in values.items()
        }
        before["deadlines"] = deadline_collection.count_documents({})

        app = harness._app(
            client,
            database,
            values,
            principal,
            tenant,
        )
        monkeypatch.setattr(
            legal_router,
            "_db_handles",
            lambda: (client, database),
        )

        with TestClient(app) as api:
            response = api.get(
                PATH,
                headers={"X-Tenant-ID": tenant},
            )

        assert response.status_code == 403, response.text
        serialized = response.text.casefold()
        for forbidden in (
            "visible_matter_ids",
            "deadline_id",
            "source_reference",
            "source_evidence_fingerprint",
        ):
            assert forbidden not in serialized

        after = {
            name: collection.count_documents({})
            for name, collection in values.items()
        }
        after["deadlines"] = deadline_collection.count_documents({})
        assert after == before

        if authority == "membership":
            assert desired is not None
            assert TenantMembershipRepository.resolve(
                principal,
                tenant,
                values["membership"],
            ) == desired
        else:
            assert desired_principal is not None
            assert PrincipalAuthorityRepository.get(
                principal,
                values["principal"],
            ) == desired_principal

    finally:
        client.drop_database(database.name)
        client.close()


def test_real_iam_temporal_membership_suspended_denied(
    monkeypatch: Any,
) -> None:
    _assert_temporal_lifecycle_denied(
        monkeypatch,
        authority="membership",
        status_name="SUSPENDED",
    )


def test_real_iam_temporal_membership_revoked_denied(
    monkeypatch: Any,
) -> None:
    _assert_temporal_lifecycle_denied(
        monkeypatch,
        authority="membership",
        status_name="REVOKED",
    )


def test_real_iam_temporal_principal_suspended_denied(
    monkeypatch: Any,
) -> None:
    _assert_temporal_lifecycle_denied(
        monkeypatch,
        authority="principal",
        status_name="SUSPENDED",
    )


def test_real_iam_temporal_principal_revoked_denied(
    monkeypatch: Any,
) -> None:
    _assert_temporal_lifecycle_denied(
        monkeypatch,
        authority="principal",
        status_name="REVOKED",
    )


@pytest.mark.parametrize("failure", [False, True])
def test_real_mongo_temporal_http_transaction_commands(
    monkeypatch: Any,
    failure: bool,
) -> None:
    """Prove actual Mongo lsid/txnNumber across both reads and commit/abort."""
    from pymongo import monitoring
    from tools.eos.legal_operations.service import (
        legal_temporal_operations_read_service as temporal_service,
    )

    class Listener(monitoring.CommandListener):
        def __init__(self) -> None:
            self.events: list[tuple[str, str, object, object]] = []

        def started(self, event: Any) -> None:
            command = event.command
            name = event.command_name
            if name == "find":
                collection_name = command.get("find", "")
                if collection_name not in (
                    "legal_work_items",
                    deadline_registry.COLLECTION,
                ):
                    return
                self.events.append((
                    name, str(collection_name),
                    command.get("lsid"), command.get("txnNumber"),
                ))
            elif name in ("commitTransaction", "abortTransaction"):
                self.events.append((
                    name, "",
                    command.get("lsid"), command.get("txnNumber"),
                ))

        def succeeded(self, event: Any) -> None:
            pass

        def failed(self, event: Any) -> None:
            pass

    listener = Listener()
    client: MongoClient[Any] = MongoClient(
        URI,
        serverSelectionTimeoutMS=5000,
        uuidRepresentation="standard",
        event_listeners=[listener],
    )
    database = client[
        "wilsy_p4_monitor_" + uuid.uuid4().hex
    ]
    tenant = "tenant-p4-monitor-" + uuid.uuid4().hex
    principal = "principal-p4-monitor-" + uuid.uuid4().hex

    try:
        hello = client.admin.command("hello")
        assert hello.get("isWritablePrimary") is True
        assert hello.get("logicalSessionTimeoutMinutes") is not None

        values = harness._collections(database)
        harness._ensure_indexes(values)
        deadlines = database[deadline_registry.COLLECTION]
        deadline_registry.ensure_indexes(deadlines)
        harness._seed_iam(values, principal, tenant)
        harness._seed_work(client, values, principal, tenant)

        with client.start_session() as session:
            with session.start_transaction():
                deadline_registry.persist_deadline(
                    _deadline(
                        "deadline-monitored",
                        "matter-http-1",
                        tenant,
                        2,
                    ),
                    deadlines,
                    session=session,
                )

        app = harness._app(
            client, database, values, principal, tenant
        )
        monkeypatch.setattr(
            legal_router,
            "_db_handles",
            lambda: (client, database),
        )

        if failure:
            original_reader = (
                temporal_service._CanonicalDeadlineReader.list_matter_deadlines
            )

            def fail_after_canonical_read(
                self: Any, **kwargs: Any
            ) -> Any:
                original_reader(self, **kwargs)
                raise RuntimeError("INJECTED_AFTER_CANONICAL_READ")

            monkeypatch.setattr(
                temporal_service._CanonicalDeadlineReader,
                "list_matter_deadlines",
                fail_after_canonical_read,
            )

        # Ignore setup and seed transactions. Only observe the HTTP call.
        listener.events.clear()

        with TestClient(app) as api:
            response = api.get(
                PATH, headers={"X-Tenant-ID": tenant}
            )

        events = listener.events

        work_reads = [
            event for event in events
            if event[0] == "find"
            and event[1] == "legal_work_items"
        ]
        deadline_reads = [
            event for event in events
            if event[0] == "find"
            and event[1] == deadline_registry.COLLECTION
        ]

        assert work_reads, f"PRODUCTIVE_WORK_FIND_MISSING={events}"
        assert deadline_reads, f"CANONICAL_DEADLINE_FIND_MISSING={events}"

        work_session = work_reads[0][2:]
        deadline_session = deadline_reads[0][2:]
        assert work_session[0] is not None
        assert work_session[1] is not None
        assert work_session == deadline_session

        endings = [
            event for event in events
            if event[0] in ("commitTransaction", "abortTransaction")
            and event[2:] == work_session
        ]

        if failure:
            assert response.status_code == 503, response.text
            assert response.json() == {
                "detail": "LEGAL_OPERATIONS_TEMPORAL_EVIDENCE_UNAVAILABLE"
            }
            assert [event[0] for event in endings] == [
                "abortTransaction"
            ]
            assert "deadline-monitored" not in response.text
        else:
            assert response.status_code == 200, response.text
            assert [
                row["deadline_id"]
                for row in response.json()["rows"]
            ] == ["deadline-monitored"]
            assert [event[0] for event in endings] == [
                "commitTransaction"
            ]

        assert values["work"].count_documents({}) == 1
        assert values["assignment"].count_documents({}) == 1
        assert deadlines.count_documents({}) == 1

    finally:
        client.drop_database(database.name)
        client.close()
