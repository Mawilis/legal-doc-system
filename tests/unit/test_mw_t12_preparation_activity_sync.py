"""TITLE: MW-T12 governed EOS activity write/readback regression.
VERSION: v1.0.0-INDEPENDENT-ACTIVITY-CERT
AUTHORITY: WILSY OS Core Governance / AGENTS.md.
EPITOME: Certify a single source-owned task-comment checkpoint, replay
         prevention and fail-closed lifecycle/source readback.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tests/unit/test_mw_t12_preparation_activity_sync.py
COLLABORATION / OWNERSHIP: Existing MW-T12 source readback and Projects
         owner comment endpoint; no test writes to live EOS.
CERTIFICATION / UPDATE DATE: 2026-11-25.
CHANGELOG: v1.0.0-INDEPENDENT-ACTIVITY-CERT covers exact target binding,
           comment checksum, absent/duplicate checkpoint, single write,
           independently verified receipt and unchanged task lifecycle.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2; ISO 27001.
SECURITY / PRIVACY POSTURE: Fully synthetic tenant/credential, no real tokens.
TENANT BOUNDARY: No live MongoDB, Atlas or Foundation project mutation.
AUTHORITY BOUNDARY: Mocked network is not authenticated live certification.
FINANCIAL AUTHORITY BOUNDARY: No cloud spending.
"""
from __future__ import annotations

import json
from types import SimpleNamespace

import pytest

from tools.eos.ops import mw_t12_preparation_activity_sync as sync
from tools.eos.ops import mw_t12_foundation_readback as source


PROJECT = "prj-" + "a" * 48
TASK = "ptk-" + "b" * 48


def project_page():
    return [{
        "project_id": PROJECT, "tenant_id": source.CANONICAL_TENANT_ID,
        "name": source.PROJECT_NAME,
    }]


def task_page(status="IN_PROGRESS"):
    return [{
        "task_id": TASK, "project_id": PROJECT,
        "tenant_id": source.CANONICAL_TENANT_ID,
        "title": source.TASK_NAME, "status": status, "revision": 7,
    }]


def comment():
    return {
        "body": sync.BODY, "comment_id": "pcm-" + "c" * 48,
        "tenant_id": source.CANONICAL_TENANT_ID,
        "project_id": PROJECT, "task_id": TASK,
        "fingerprint": "f" * 128,
    }


def test_checkpoint_bound_and_under_comment_limit():
    assert sync.MARKER in sync.BODY
    assert len(sync.BODY) <= 5000
    assert "IN_PROGRESS" in sync.BODY
    assert "rollback" in sync.BODY.lower()
    assert len(sync.KEY) <= 200


def test_locate_original_source(monkeypatch):
    monkeypatch.setattr(source, "_list_all", lambda _c, _b, _t, path, *_a:
                        project_page() if path == "/api/projects"
                        else task_page())
    assert sync._locate(None, "http://127.0.0.1:5173", "synthetic") == (
        PROJECT, TASK, "7"
    )


def test_refuse_completed_original_task(monkeypatch):
    monkeypatch.setattr(source, "_list_all", lambda _c, _b, _t, path, *_a:
                        project_page() if path == "/api/projects"
                        else task_page("DONE"))
    with pytest.raises(source.SourceReadbackDenied,
                       match="MW_T12_TASK_STATUS_OR_BINDING_INVALID"):
        sync._locate(None, "http://127.0.0.1:5173", "synthetic")


def test_comment_duplicate_marker_denied(monkeypatch):
    monkeypatch.setattr(source, "_list_all", lambda *_a: [comment(), comment()])
    with pytest.raises(source.SourceReadbackDenied,
                       match="MW_T12_PREPARATION_COMMENT_DUPLICATE"):
        sync._matching_comment(None, "http://127.0.0.1:5173",
                               "synthetic", PROJECT, TASK)


def test_comment_body_drift_denied(monkeypatch):
    row = {**comment(), "body": sync.BODY + " tampered"}
    monkeypatch.setattr(source, "_list_all", lambda *_a: [row])
    with pytest.raises(source.SourceReadbackDenied,
                       match="MW_T12_PREPARATION_COMMENT_SOURCE_MISMATCH"):
        sync._matching_comment(None, "http://127.0.0.1:5173",
                               "synthetic", PROJECT, TASK)


def test_post_payload_and_idempotency_are_exact(monkeypatch):
    captured = []

    class Response:
        status = 201

        def __enter__(self):
            return self

        def __exit__(self, *args):
            return False

        def read(self, _size):
            return json.dumps({
                "schema": "WILSY-PROJECT-COMMENT-RESULT/V1",
                "tenant_id": source.CANONICAL_TENANT_ID,
                "project_id": PROJECT, "task_id": TASK, "comment": comment(),
            }).encode()

    class Client:
        def open(self, request, timeout):
            captured.append((request, timeout))
            return Response()

    assert sync._post_once(Client(), "http://127.0.0.1:5173",
                           "synthetic", PROJECT, TASK) == comment()
    request, timeout = captured[0]
    assert request.get_method() == "POST"
    assert request.get_header("Idempotency-key") == sync.KEY
    assert request.get_header("Authorization") == "Bearer synthetic"
    assert json.loads(request.data)["body"] == sync.BODY
    assert timeout == 18


def test_verify_writes_once_and_rereads_exact_receipt(monkeypatch):
    monkeypatch.setattr(source, "_verify_identity", lambda *_: None)
    monkeypatch.setattr(source, "_verify_workspace_scope", lambda *_: None)
    monkeypatch.setattr(source, "_list_all", lambda *_a: [])
    monkeypatch.setattr(sync, "_locate", lambda *_a: (PROJECT, TASK, "7"))
    stored = []
    monkeypatch.setattr(sync, "_matching_comment",
                        lambda *_a: stored[0] if stored else None)

    def post(*_a):
        stored.append(comment())
        return comment()

    monkeypatch.setattr(sync, "_post_once", post)
    assert sync.verify("http://127.0.0.1:5173", "synthetic", True) == (
        "WRITTEN_AND_VERIFIED"
    )
    assert len(stored) == 1
    assert sync.verify("http://127.0.0.1:5173", "synthetic", True) == (
        "EXISTING_VERIFIED"
    )
    assert len(stored) == 1


def test_independent_readback_mismatch_fail_closed(monkeypatch):
    monkeypatch.setattr(source, "_verify_identity", lambda *_: None)
    monkeypatch.setattr(source, "_verify_workspace_scope", lambda *_: None)
    monkeypatch.setattr(sync, "_locate", lambda *_a: (PROJECT, TASK, "7"))
    monkeypatch.setattr(sync, "_matching_comment", lambda *_a: None)
    monkeypatch.setattr(sync, "_post_once", lambda *_a: comment())
    with pytest.raises(source.SourceReadbackDenied,
                       match="MW_T12_PREPARATION_INDEPENDENT_READBACK_MISMATCH"):
        sync.verify("http://127.0.0.1:5173", "synthetic", True)


def test_status_changed_after_comment_denied(monkeypatch):
    monkeypatch.setattr(source, "_verify_identity", lambda *_: None)
    monkeypatch.setattr(source, "_verify_workspace_scope", lambda *_: None)
    targets = [(PROJECT, TASK, "7"), (PROJECT, TASK, "8")]
    monkeypatch.setattr(sync, "_locate", lambda *_a: targets.pop(0))
    monkeypatch.setattr(sync, "_matching_comment", lambda *_a: comment())
    with pytest.raises(source.SourceReadbackDenied,
                       match="MW_T12_TASK_LIFECYCLE_CHANGED"):
        sync.verify("http://127.0.0.1:5173", "synthetic", True)


# ARTIFACT: tests/unit/test_mw_t12_preparation_activity_sync.py
# VERSION: v1.0.0-INDEPENDENT-ACTIVITY-CERT
# AUTHORITY BOUNDARY: Offline simulated HTTP only.
# TENANT POSTURE: Synthetic records, no real data.
# FAIL-CLOSED POSTURE: Missing exact readback never succeeds.
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively.
# END OF WILSY OS SOVEREIGN ARTIFACT
