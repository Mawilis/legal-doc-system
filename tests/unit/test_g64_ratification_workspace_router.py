"""Authenticated G64 workspace command transport tests."""
import hashlib
from datetime import datetime, timezone
from types import SimpleNamespace

from fastapi import FastAPI
from fastapi.testclient import TestClient

from tools.eos.api import g64_ratification_workspace_router as workspace_router
from tools.eos.api.tenant_authorization_http import TenantAuthorizationContext

NOW = datetime(2026, 10, 27, tzinfo=timezone.utc)


class Session:
    in_transaction = True

    def __enter__(self):
        return self

    def __exit__(self, *_args):
        return False

    def start_transaction(self):
        return self


class Cursor:
    def __init__(self, rows):
        self.rows = list(rows)

    def sort(self, *_args):
        return self

    def limit(self, count):
        self.rows = self.rows[:count]
        return self

    def __iter__(self):
        return iter(self.rows)


class Collection:
    def __init__(self):
        self.rows = {}

    def with_options(self, **_kwargs):
        return self

    def find_one(self, query, session=None):
        assert session is not None
        return self.rows.get(
            (query["tenant_id"], query["institution_id"], query["record_id"])
        )

    def insert_one(self, document, session=None):
        assert session is not None
        key = (
            document["tenant_id"],
            document["institution_id"],
            document["record_id"],
        )
        if key in self.rows:
            raise RuntimeError("duplicate record")
        self.rows[key] = document

    def find(self, query, session=None):
        assert session is not None
        return Cursor([
            value for (tenant, institution, _), value in self.rows.items()
            if tenant == query["tenant_id"] and institution == query["institution_id"]
        ])


class Client:
    def start_session(self):
        return Session()


class Database:
    def __init__(self):
        self.collection = Collection()

    def __getitem__(self, _name):
        return self.collection


def request_body():
    evidence = {
        "locator": "evidence:governance-source-001",
        "sha3_512_fingerprint": "b" * 128,
    }
    return {
        "institution_id": "institution-label-pending-verification",
        "decisions": [
            {
                "decision_id": f"D{index:02}",
                "disposition": "DEFER",
                "rationale": "Explicitly defer pending independent institutional verification.",
                "scope": ["institution:pending", f"decision:D{index:02}"],
                "accountable_source_owner": "owner-pending-verification",
                "evidence": [evidence],
                "effective_from": "2026-10-27T00:00:00Z",
                "expires_or_review_at": "2026-11-27T00:00:00Z",
                "revocation_rule": "No access while deferred; re-review before any change.",
            }
            for index in range(1, 11)
        ],
        "supporting_evidence": [evidence],
    }


def make_client(monkeypatch):
    app = FastAPI()
    app.include_router(workspace_router.router, prefix="/api")
    context = TenantAuthorizationContext(
        identity=SimpleNamespace(identity_id="principal-authenticated-001"),
        tenant_id="tenant-001",
        decision=None,
    )
    app.dependency_overrides[workspace_router._WRITE_AUTHORITY] = lambda: context
    app.dependency_overrides[workspace_router._READ_AUTHORITY] = lambda: context
    database = Database()
    monkeypatch.setattr(workspace_router, "_storage", lambda: (Client(), database))
    monkeypatch.setattr(
        workspace_router,
        "publish_repository_evidence",
        lambda **_kwargs: {
            "status": "PUBLISHED",
            "repository": "Mawilis/legal-doc-system",
            "branch": "g64-evidence/test",
            "path": "encryption-evidence/g64-ratification-workspaces/test.json",
            "commit_sha": "c" * 40,
        },
    )
    return TestClient(app), database


def test_authenticated_click_persists_non_authorizing_record_and_export(monkeypatch):
    client, database = make_client(monkeypatch)
    response = client.post(
        "/api/legal-operations/g64/ratification-workspace/records",
        headers={"Idempotency-Key": "click-event-001"},
        json=request_body(),
    )
    assert response.status_code == 201
    body = response.json()
    assert len(database.collection.rows) == 1
    assert body["record"]["state"] == "ATTESTED_PENDING_VERIFICATION"
    assert body["record"]["attestation"]["signature_kind"] == (
        "AUTHENTICATED_CLICK_TO_ATTEST_NOT_CRYPTOGRAPHIC_SIGNATURE"
    )
    assert body["institution_binding_status"] == (
        "UNVERIFIED_PENDING_INDEPENDENT_VERIFICATION"
    )
    assert body["ratification_complete"] is False
    assert body["permits_operational_access"] is False
    assert body["repository_evidence_export"]["constitutes_ratification"] is False
    assert body["repository_evidence_export"]["export_status"] == (
        "INDEPENDENT_VERIFICATION_PENDING"
    )
    assert body["repository_persistence_status"] == "PUBLISHED"
    assert body["repository_commit"]["commit_sha"] == "c" * 40


def test_idempotent_retry_replays_same_record_without_duplicate(monkeypatch):
    client, database = make_client(monkeypatch)
    headers = {"Idempotency-Key": "click-event-002"}
    first = client.post(
        "/api/legal-operations/g64/ratification-workspace/records",
        headers=headers,
        json=request_body(),
    )
    replay = client.post(
        "/api/legal-operations/g64/ratification-workspace/records",
        headers=headers,
        json=request_body(),
    )
    assert first.status_code == 201
    assert replay.status_code == 201
    assert len(database.collection.rows) == 1
    assert replay.json()["record"]["record_id"] == first.json()["record"]["record_id"]


def test_idempotency_key_cannot_replay_different_decisions(monkeypatch):
    client, database = make_client(monkeypatch)
    headers = {"Idempotency-Key": "click-event-003"}
    first_body = request_body()
    first = client.post(
        "/api/legal-operations/g64/ratification-workspace/records",
        headers=headers,
        json=first_body,
    )
    changed_body = request_body()
    changed_body["decisions"][0]["rationale"] = "Changed payload under same idempotency key."
    conflict = client.post(
        "/api/legal-operations/g64/ratification-workspace/records",
        headers=headers,
        json=changed_body,
    )
    assert first.status_code == 201
    assert conflict.status_code == 409
    assert len(database.collection.rows) == 1


def test_history_is_tenant_scoped_and_returns_unverified_evidence(monkeypatch):
    client, _database = make_client(monkeypatch)
    created = client.post(
        "/api/legal-operations/g64/ratification-workspace/records",
        headers={"Idempotency-Key": "click-event-004"},
        json=request_body(),
    )
    history = client.get(
        "/api/legal-operations/g64/ratification-workspace/records",
        params={"institution_id": "institution-label-pending-verification"},
    )
    assert created.status_code == 201
    assert history.status_code == 200
    assert len(history.json()["records"]) == 1
    assert history.json()["records"][0]["institution_binding_status"] == (
        "UNVERIFIED_PENDING_INDEPENDENT_VERIFICATION"
    )


def test_contract_endpoint_uses_canonical_repository_source(monkeypatch):
    client, _database = make_client(monkeypatch)
    response = client.get(
        "/api/legal-operations/g64/ratification-workspace/contract"
    )
    assert response.status_code == 200
    body = response.json()
    assert body["contract_version"] == "v1.0.0-P47-R95-G62-DRAFT"
    assert body["contract_sha3_512_fingerprint"] == hashlib.sha3_512(
        body["contract_text"].encode("utf-8")
    ).hexdigest()
    assert body["contract_status"] == "PROPOSED_NOT_INSTITUTIONALLY_APPROVED"
    assert body["ratification_complete"] is False


def test_repository_publisher_unavailable_returns_pending_after_app_persistence(monkeypatch):
    client, database = make_client(monkeypatch)

    def unavailable(**_kwargs):
        raise workspace_router.G64RepositoryPublishError(
            "G64_REPOSITORY_PUBLISHER_NOT_CONFIGURED"
        )

    monkeypatch.setattr(workspace_router, "publish_repository_evidence", unavailable)
    response = client.post(
        "/api/legal-operations/g64/ratification-workspace/records",
        headers={"Idempotency-Key": "click-event-pending-repository"},
        json=request_body(),
    )
    assert response.status_code == 202
    assert len(database.collection.rows) == 1
    body = response.json()
    assert body["application_persistence_status"] == "PERSISTED"
    assert body["repository_persistence_status"] == "PENDING_CONFIGURATION"
    assert body["ratification_complete"] is False
