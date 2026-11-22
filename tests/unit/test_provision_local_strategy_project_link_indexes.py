"""TITLE: Strategy Pillar-Project Local Index Preflight Unit Certificate.
VERSION: v1.0.0-SAFE-LOCAL-INDEX-DIAGNOSTIC-CERT
AUTHORITY: WILSY OS Core Governance / AGENTS.md.
EPITOME: Certify fail-closed local-only source checks and secret-safe diagnostics.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tests/unit/test_provision_local_strategy_project_link_indexes.py
COLLABORATION / OWNERSHIP: Strategy local index operator; no live Mongo dependency.
CERTIFICATION / UPDATE DATE: 2026-11-22
CHANGELOG: v1.0.0-SAFE-LOCAL-INDEX-DIAGNOSTIC-CERT proves Atlas, missing database,
missing scheme and foreign-host sources fail safely without opening Mongo;
a legitimate local target admits a read-only no-DDL --check, and only --apply
may invoke required source index creation.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2.
SECURITY / PRIVACY POSTURE: No real passwords or external sockets.
TENANT BOUNDARY: Indexes scoped at canonical registry, no tenant record writes.
AUTHORITY BOUNDARY: Operator infrastructure command, not tenant user permission.
FINANCIAL AUTHORITY BOUNDARY: Kennel EOS exclusively.
"""
from __future__ import annotations

from types import SimpleNamespace

import pytest

from tools.eos.ops import provision_local_strategy_project_link_indexes as operator


@pytest.mark.parametrize("uri,code", [
    ("", "LOCAL_MONGODB_STANDARD_URI_REQUIRED"),
    ("mongodb+srv://example.invalid/os", "LOCAL_MONGODB_STANDARD_URI_REQUIRED"),
    ("mongodb://db.example.invalid:27017/wilsy-os-dev", "LOCAL_MONGODB_LOOPBACK_REQUIRED"),
    ("mongodb://127.0.0.1:27017", "LOCAL_MONGODB_DATABASE_NAME_REQUIRED"),
])
def test_unadmitted_mongo_target_fails_without_connection(monkeypatch, capsys, uri, code):
    """A diagnostic code must not include any address or credential material."""
    monkeypatch.setattr(operator, "resolve_mongo_uri", lambda: uri)
    monkeypatch.setattr(operator, "MongoClient",
                        lambda *_args, **_kwargs: pytest.fail("UNADMITTED_DATABASE_CONNECTION"))
    assert operator.main(["--apply"]) == 1
    output = capsys.readouterr().err
    assert "ERROR_CODE=" + code in output
    assert "example.invalid" not in output
    assert uri not in output if uri else True


class _FakeClient:
    """Deterministic local replica set; no backend resource or real DDL."""

    def __init__(self, db):
        """Bind a synthetic database map for no-IO tests."""
        self.db = db
        self.admin = SimpleNamespace(command=lambda command: {"setName": "rs0"})

    def __enter__(self):
        """Open a test-only connection."""
        return self

    def __exit__(self, *_exc):
        """Release the no-IO test fake."""
        return None

    def get_database(self, name):
        """Enforce the URI database identity in the fake."""
        assert name == "wilsy-os-dev"
        return self.db


def test_check_is_read_only_and_apply_is_explicit(monkeypatch, capsys):
    """The operator must never mutate indexes for --check."""
    monkeypatch.setattr(operator, "resolve_mongo_uri",
                        lambda: "mongodb://127.0.0.1:27017/wilsy-os-dev?replicaSet=rs0")
    calls = []
    db = {}
    monkeypatch.setattr(operator, "MongoClient",
                        lambda *_args, **_kwargs: _FakeClient(db))
    monkeypatch.setattr(operator.StrategyProjectRelationshipRegistry, "__init__",
                        lambda self, _db: calls.append("bind"))
    monkeypatch.setattr(operator.StrategyProjectRelationshipRegistry, "require_indexes",
                        lambda self: calls.append("require"))
    monkeypatch.setattr(operator.StrategyProjectRelationshipRegistry, "ensure_indexes",
                        lambda self: calls.append("ensure"))
    assert operator.main(["--check"]) == 0
    assert calls == ["bind", "require"]
    assert "INDEX_MUTATION=NONE" in capsys.readouterr().out
    assert operator.main(["--apply"]) == 0
    assert calls == ["bind", "require", "bind", "ensure", "require"]
    assert "STRATEGY_LINK_INDEX_STATE=VERIFIED" in capsys.readouterr().out


def test_no_action_never_opens_database(monkeypatch, capsys):
    """An invocation without explicit action is inert."""
    monkeypatch.setattr(operator, "MongoClient",
                        lambda *_args, **_kwargs: pytest.fail("UNAUTHORIZED_DATABASE_CONNECTION"))
    assert operator.main([]) == 0
    assert "DRY_RUN_NOT_EXECUTED" in capsys.readouterr().out


# ARTIFACT: test_provision_local_strategy_project_link_indexes.py
# VERSION: v1.0.0-SAFE-LOCAL-INDEX-DIAGNOSTIC-CERT
# AUTHORITY BOUNDARY: Isolated no-IO certificate only.
# TENANT POSTURE: No authority change or tenant state mutation.
# FAIL-CLOSED POSTURE: Unsafe targets cannot reach database transport.
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively.
# END OF WILSY OS SOVEREIGN ARTIFACT
