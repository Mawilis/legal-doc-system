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
        key = (query["tenant_id"], query["institution_id"], query["record_id"])
        if "event_id" in query:
            key = (*key, query["event_id"])
        return self.rows.get(key)

    def insert_one(self, document, session=None):
        assert session is not None
        key = (
            document["tenant_id"],
            document["institution_id"],
            document["record_id"],
        )
        if "event_id" in document:
            key = (*key, document["event_id"])
        if key in self.rows:
            raise RuntimeError("duplicate record")
        self.rows[key] = document

    def find(self, query, session=None):
        assert session is not None
        return Cursor([
            value for key, value in self.rows.items()
            if key[0] == query["tenant_id"] and key[1] == query["institution_id"]
            and key[2] == query.get("record_id", key[2])
        ])


class Client:
    def start_session(self):
        return Session()


class Database:
    def __init__(self):
        self.collection = Collection()
        self.collections = {}

    def __getitem__(self, name):
        if name == workspace_router.COLLECTION:
            return self.collection
        return self.collections.setdefault(name, Collection())


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
    verifier_context = TenantAuthorizationContext(
        identity=SimpleNamespace(identity_id="principal-independent-verifier"),
        tenant_id="tenant-001", decision=None,
    )
    approver_context = TenantAuthorizationContext(
        identity=SimpleNamespace(identity_id="principal-independent-second-approver"),
        tenant_id="tenant-001", decision=None,
    )
    app.dependency_overrides[workspace_router._VERIFY_AUTHORITY] = lambda: verifier_context
    app.dependency_overrides[workspace_router._SECOND_APPROVAL_AUTHORITY] = lambda: approver_context
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


def test_g64_router_and_registry_index_are_wired_into_python_eos_startup():
    from pathlib import Path

    root = Path(__file__).resolve().parents[2]
    server_source = (root / "tools/eos/api/server.py").read_text(encoding="utf-8")
    assert server_source.count(
        'app.include_router(g64_ratification_workspace_router, prefix="/api")'
    ) == 1
    assert "ensure_g64_workspace_evidence_indexes(" in server_source
    assert "database[G64_WORKSPACE_EVIDENCE_COLLECTION]" in server_source


def test_interactive_workspace_route_is_protected_and_all_choices_start_blank():
    from pathlib import Path

    root = Path(__file__).resolve().parents[2]
    app_source = (root / "client/src/App.jsx").read_text(encoding="utf-8")
    ui_source = (
        root / "client/src/components/legal/G64RatificationWorkspace.jsx"
    ).read_text(encoding="utf-8")
    assert 'path="/g64-ratification-workspace"' in app_source
    assert "LegalAcceptanceBoundary runtime={<G64RatificationWorkspace />}" in app_source
    assert "disposition: ''" in ui_source
    assert "Choose disposition" in ui_source
    assert "institution_binding_status" in ui_source
    assert "cryptographic signature" in ui_source


def test_independent_verification_and_second_approval_are_durable_and_non_authorizing(monkeypatch):
    client, database = make_client(monkeypatch)
    created = client.post(
        "/api/legal-operations/g64/ratification-workspace/records",
        headers={"Idempotency-Key": "click-for-review-001"},
        json=request_body(),
    )
    assert created.status_code == 201
    record = created.json()["record"]
    evidence = {
        "locator": "evidence:independent-review-001",
        "sha3_512_fingerprint": "d" * 128,
    }
    verification = client.post(
        f"/api/legal-operations/g64/ratification-workspace/records/{record['record_id']}/independent-verification",
        headers={"Idempotency-Key": "verification-event-001"},
        json={
            "institution_id": record["institution_id"],
            "record_id": record["record_id"],
            "record_sha3_512_fingerprint": record["evidence_sha3_512"],
            "outcome": "PASS",
            "institution_binding_verified": True,
            "ratifier_authority_verified": True,
            "evidence_integrity_verified": True,
            "rationale": "Independent review checked source provenance and authority evidence.",
            "evidence": [evidence],
        },
    )
    assert verification.status_code == 201, verification.text
    verifier_event = verification.json()["review_event"]
    assert verifier_event["reviewer_principal_id"] != record["ratifier_principal_id"]
    assert verifier_event["permits_operational_access"] is False

    approval = client.post(
        f"/api/legal-operations/g64/ratification-workspace/records/{record['record_id']}/second-approval",
        headers={"Idempotency-Key": "second-approval-event-001"},
        json={
            "institution_id": record["institution_id"],
            "record_id": record["record_id"],
            "record_sha3_512_fingerprint": record["evidence_sha3_512"],
            "verification_event_id": verifier_event["event_id"],
            "outcome": "APPROVE",
            "rationale": "Independent second approver reviewed the verifier evidence and scope.",
            "evidence": [evidence],
        },
    )
    assert approval.status_code == 201, approval.text
    approval_event = approval.json()["review_event"]
    assert approval_event["approver_principal_id"] not in {
        record["ratifier_principal_id"], verifier_event["reviewer_principal_id"]
    }
    assert approval.json()["ratification_complete"] is False
    assert approval.json()["permits_operational_access"] is False
    assert len(database.collections[workspace_router.REVIEW_COLLECTION].rows) == 2


def test_independent_verification_cannot_be_submitted_by_original_attester(monkeypatch):
    client, _database = make_client(monkeypatch)
    created = client.post(
        "/api/legal-operations/g64/ratification-workspace/records",
        headers={"Idempotency-Key": "click-for-review-002"},
        json=request_body(),
    )
    record = created.json()["record"]
    evidence = {
        "locator": "evidence:independent-review-002",
        "sha3_512_fingerprint": "e" * 128,
    }
    response = client.post(
        f"/api/legal-operations/g64/ratification-workspace/records/{record['record_id']}/independent-verification",
        headers={"Idempotency-Key": "verification-event-002"},
        json={
            "institution_id": record["institution_id"],
            "record_id": record["record_id"],
            "record_sha3_512_fingerprint": record["evidence_sha3_512"],
            "outcome": "FAIL",
            "institution_binding_verified": False,
            "ratifier_authority_verified": False,
            "evidence_integrity_verified": True,
            "rationale": "The current authenticated principal is the original attester.",
            "evidence": [evidence],
        },
    )
    assert response.status_code == 403
    assert response.json()["detail"] == "G64_VERIFIER_MUST_BE_INDEPENDENT"
