"""G64 repository publisher fails closed without scoped credentials and branch policy."""
from datetime import datetime, timezone

import pytest

from tools.eos.legal_operations.domain.g64_ratification_workspace_evidence import (
    G64RatificationWorkspaceRecord,
    G64RecordState,
    new_pending_decisions,
)
from tools.eos.legal_operations.domain.g64_ratification_workspace_export import (
    build_repository_export_bytes,
)
from tools.eos.legal_operations.service.g64_repository_evidence_publisher import (
    G64RepositoryPublishError,
    _configuration,
    publish_repository_evidence,
)

NOW = datetime(2026, 10, 27, tzinfo=timezone.utc)
RECORD_ID = "g64-" + "a" * 40


def manifest():
    record = G64RatificationWorkspaceRecord(
        record_id=RECORD_ID,
        institution_id="institution-001",
        ratifier_principal_id="principal-unverified",
        contract_version="v1.0.0-P47-R95-G62-DRAFT",
        contract_sha3_512_fingerprint="b" * 128,
        created_at=NOW,
        state=G64RecordState.DRAFT,
        decisions=new_pending_decisions(),
    )
    return build_repository_export_bytes(tenant_id="tenant-001", record=record)


def test_publisher_requires_explicit_repository_credentials(monkeypatch):
    for name in (
        "G64_REPOSITORY_EXPORT_TOKEN",
        "G64_REPOSITORY_EXPORT_REPOSITORY",
        "G64_REPOSITORY_EXPORT_BASE_BRANCH",
        "G64_REPOSITORY_EXPORT_BRANCH",
    ):
        monkeypatch.delenv(name, raising=False)
    with pytest.raises(G64RepositoryPublishError) as captured:
        publish_repository_evidence(record_id=RECORD_ID, manifest_bytes=manifest())
    assert captured.value.code == "G64_REPOSITORY_PUBLISHER_NOT_CONFIGURED"


def test_export_branch_must_be_dedicated_and_not_the_base(monkeypatch):
    monkeypatch.setenv("G64_REPOSITORY_EXPORT_TOKEN", "test-token-not-used")
    monkeypatch.setenv("G64_REPOSITORY_EXPORT_REPOSITORY", "Mawilis/legal-doc-system")
    monkeypatch.setenv("G64_REPOSITORY_EXPORT_BASE_BRANCH", "main")
    monkeypatch.setenv("G64_REPOSITORY_EXPORT_BRANCH", "main")
    with pytest.raises(G64RepositoryPublishError) as captured:
        _configuration()
    assert captured.value.code == "G64_REPOSITORY_BRANCH_POLICY_INVALID"


def test_publisher_rejects_invalid_record_id_before_network(monkeypatch):
    with pytest.raises(G64RepositoryPublishError) as captured:
        publish_repository_evidence(record_id="../main", manifest_bytes=manifest())
    assert captured.value.code == "G64_REPOSITORY_RECORD_ID_INVALID"


class Response:
    def __init__(self, status, body=None):
        import json

        self.status = status
        self.body = b"" if body is None else json.dumps(body).encode("utf-8")

    def __enter__(self):
        return self

    def __exit__(self, *_args):
        return False

    def read(self):
        return self.body


def test_publisher_creates_dedicated_branch_and_immutable_manifest(monkeypatch):
    import base64
    import json

    calls = []

    def fake_urlopen(request, timeout):
        calls.append((request.get_method(), request.full_url, request.data, timeout))
        method, url = request.get_method(), request.full_url
        if method == "GET" and url.endswith("/git/ref/heads/g64-evidence/test"):
            return Response(404, {"message": "not found"})
        if method == "GET" and url.endswith("/git/ref/heads/main"):
            return Response(200, {"object": {"sha": "a" * 40}})
        if method == "POST" and url.endswith("/git/refs"):
            body = json.loads(request.data)
            assert body["ref"] == "refs/heads/g64-evidence/test"
            return Response(201, {"ref": body["ref"]})
        if method == "GET" and "/contents/encryption-evidence/g64-ratification-workspaces/" in url:
            return Response(404, {"message": "not found"})
        if method == "PUT" and "/contents/encryption-evidence/g64-ratification-workspaces/" in url:
            body = json.loads(request.data)
            assert body["branch"] == "g64-evidence/test"
            return Response(201, {"commit": {"sha": "c" * 40}})
        raise AssertionError(f"Unexpected publisher request: {method} {url}")

    monkeypatch.setenv("G64_REPOSITORY_EXPORT_TOKEN", "test-token")
    monkeypatch.setenv("G64_REPOSITORY_EXPORT_REPOSITORY", "Mawilis/legal-doc-system")
    monkeypatch.setenv("G64_REPOSITORY_EXPORT_BASE_BRANCH", "main")
    monkeypatch.setenv("G64_REPOSITORY_EXPORT_BRANCH", "g64-evidence/test")
    monkeypatch.setattr(
        "tools.eos.legal_operations.service.g64_repository_evidence_publisher.urlopen",
        fake_urlopen,
    )
    result = publish_repository_evidence(record_id=RECORD_ID, manifest_bytes=manifest())
    assert result["status"] == "PUBLISHED"
    assert result["branch"] == "g64-evidence/test"
    assert result["commit_sha"] == "c" * 40
    assert not any("/git/refs/heads/main" in url for _method, url, _body, _timeout in calls)
    assert calls[-1][0] == "PUT"


def test_publisher_rejects_tampered_manifest_fingerprint_before_network(monkeypatch):
    import json

    raw = json.loads(manifest())
    raw["manifest_sha3_512"] = "0" * 128
    monkeypatch.setenv("G64_REPOSITORY_EXPORT_TOKEN", "test-token")
    monkeypatch.setenv("G64_REPOSITORY_EXPORT_REPOSITORY", "Mawilis/legal-doc-system")
    monkeypatch.setenv("G64_REPOSITORY_EXPORT_BASE_BRANCH", "main")
    monkeypatch.setenv("G64_REPOSITORY_EXPORT_BRANCH", "g64-evidence/test")
    monkeypatch.setattr(
        "tools.eos.legal_operations.service.g64_repository_evidence_publisher.urlopen",
        lambda *_args, **_kwargs: (_ for _ in ()).throw(AssertionError("network must not be called")),
    )
    with pytest.raises(G64RepositoryPublishError, match="G64_REPOSITORY_MANIFEST_FINGERPRINT_INVALID"):
        publish_repository_evidence(
            record_id=RECORD_ID,
            manifest_bytes=json.dumps(raw, sort_keys=True, separators=(",", ":")).encode("ascii"),
        )
