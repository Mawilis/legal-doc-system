from __future__ import annotations

from types import SimpleNamespace

import pytest

from tools.eos.legal_operations.service import legal_evidence_provider_readonly_reconciliation_audit_provisioner as provisioner


class _Client:
    def __init__(self, database):
        self.database = database
        self.closed = False
        self.admin = SimpleNamespace(command=lambda command: {"ok": 1})

    def get_database(self):
        return self.database

    def close(self):
        self.closed = True


class _Database:
    def __init__(self, name, client):
        self.name = name
        self.client = client


class _Provisioner:
    def __init__(self, *, audit_database, audit_client):
        self.database_name = audit_database.name
        self.audit_client = audit_client
        self.provisioned = False

    def provision(self):
        self.provisioned = True

    def verify(self):
        return self.provisioned


def test_provisioner_uses_explicit_separate_target_and_closes_client(monkeypatch, capsys) -> None:
    business_uri = "mongodb://business.example:27017/business"
    audit_uri = "mongodb://audit.example:27017/audit"
    client = _Client(None)
    database = _Database("audit", client)
    client.database = database
    captured = {}

    def create_client(uri, **kwargs):
        captured["uri"] = uri
        return client

    class RecordingProvisioner(_Provisioner):
        def __init__(self, **kwargs):
            super().__init__(**kwargs)
            captured["provisioner"] = self

    monkeypatch.setenv("MONGODB_URI", business_uri)
    monkeypatch.setenv(provisioner.AUDIT_URI_ENV, audit_uri)
    monkeypatch.setattr(provisioner, "MongoClient", create_client)
    monkeypatch.setattr(
        provisioner,
        "PlatformAuthorizationDecisionEvidenceIndexProvisioner",
        RecordingProvisioner,
    )
    assert provisioner.main() == 0
    output = capsys.readouterr().out
    assert "RECONCILIATION_AUDIT_INDEXES_PROVISIONED_AND_VERIFIED" in output
    assert audit_uri not in output
    assert business_uri not in output
    assert captured["uri"] == audit_uri
    assert captured["provisioner"].provisioned is True
    assert client.closed is True


def test_provisioner_rejects_same_business_and_audit_target_before_connecting(monkeypatch) -> None:
    uri = "mongodb://localhost:27017/wilsy"
    monkeypatch.setenv("MONGODB_URI", uri)
    monkeypatch.setenv(provisioner.AUDIT_URI_ENV, uri)
    monkeypatch.setattr(
        provisioner,
        "MongoClient",
        lambda *args, **kwargs: pytest.fail("client must not be created for shared target"),
    )
    with pytest.raises(SystemExit, match="AUDIT_AND_BUSINESS_TARGET_MUST_DIFFER"):
        provisioner.main()
