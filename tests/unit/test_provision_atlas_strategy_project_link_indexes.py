"""TITLE: WILSY OS Guarded Atlas Strategy Link Index Migration Certificate.
VERSION: v1.0.0-ATLAS-INDEX-PREFLIGHT-UNIT-CERT
AUTHORITY: WILSY OS Core Governance / AGENTS.md.
EPITOME: Prove that Atlas index migration is inert by default, requires exact
wilsy confirmation, rejects existing source data, and verifies index readback.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tests/unit/test_provision_atlas_strategy_project_link_indexes.py
COLLABORATION / OWNERSHIP: Atlas Strategy index migration; synthetic only.
CERTIFICATION / UPDATE DATE: 2026-11-23
CHANGELOG: v1.0.0-ATLAS-INDEX-PREFLIGHT-UNIT-CERT certifies no network without
explicit action, no write during --check, no wrong-db or unapproved DDL,
data-preserving refusal and guarded successful index verification.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC2 CC7.2.
SECURITY / PRIVACY POSTURE: No actual credentials, Atlas hosts, or network IO.
TENANT BOUNDARY: Index contract has tenant_id as the unique key prefix.
AUTHORITY BOUNDARY: Operator guard tests only, no user IAM claim or grants.
FINANCIAL AUTHORITY BOUNDARY: Kennel EOS exclusively.
"""
from __future__ import annotations

from types import SimpleNamespace

import pytest

from tools.eos.ops import provision_atlas_strategy_project_link_indexes as operator


class Database:
    """Fake Atlas collections with read-only preflight and recorded index DDL."""

    def __init__(self, *, populated: bool = False) -> None:
        """Establish fake source documents without production data."""
        self.populated = populated
        self.ddl_count = 0
        self.index_ready = False

    def list_collection_names(self):
        """Return two fake collection names."""
        return list(operator._COLLECTIONS)

    def __getitem__(self, _key):
        """Return source reader for either fake collection."""
        return self

    def count_documents(self, _filter, *, limit):
        """Report existing records only when present."""
        assert limit == 1
        return int(self.populated)


class Client:
    """No-network Atlas replica-set response for test-bound preflight."""

    def __init__(self, database: Database) -> None:
        """Use only synthetic database state."""
        self.database = database
        self.admin = SimpleNamespace(command=lambda _command: {"setName": "test-rs"})

    def __enter__(self):
        """Return client context."""
        return self

    def __exit__(self, *_args):
        """Release fake client."""
        return None

    def get_database(self, name):
        """Verify the explicit canonical database rather than guessing."""
        assert name == "wilsy"
        return self.database


def _mock_source(monkeypatch, database: Database) -> None:
    """Bind a synthetic SRV resolver and fake registry DDL/readback."""
    monkeypatch.setattr(operator, "resolve_mongo_uri",
                        lambda: "mongodb+srv://synthetic-invalid-host/wilsy")
    monkeypatch.setattr(operator, "_verify_target", lambda _uri: "wilsy")
    monkeypatch.setattr(operator, "MongoClient", lambda *_args, **_kw: Client(database))
    def require(_registry):
        if not database.index_ready:
            raise operator.StrategyProjectLinkError("STRATEGY_LINK_INDEX_UNAVAILABLE")
    def ensure(_registry):
        database.ddl_count += 1
        database.index_ready = True
    monkeypatch.setattr(operator.StrategyProjectRelationshipRegistry, "require_indexes", require)
    monkeypatch.setattr(operator.StrategyProjectRelationshipRegistry, "ensure_indexes", ensure)


def test_inert_default_and_confirmation_gate(monkeypatch, capsys):
    """No arguments and missing --apply confirmation cannot reach Mongo."""
    monkeypatch.setattr(operator, "MongoClient",
                        lambda *_args, **_kw: pytest.fail("DATABASE_CONNECTION_NOT_AUTHORIZED"))
    assert operator.main([]) == 0
    assert "DRY_RUN_NOT_EXECUTED" in capsys.readouterr().out
    assert operator.main(["--apply"]) == 2
    assert "EXPLICIT_CONFIRMATION_REQUIRED" in capsys.readouterr().out


@pytest.mark.parametrize("uri,code", [
    ("", "ATLAS_STRATEGY_SRV_REQUIRED"),
    ("mongodb://127.0.0.1:27017/wilsy", "ATLAS_STRATEGY_SRV_REQUIRED"),
])
def test_non_atlas_uri_fails_closed_without_connection(monkeypatch, capsys, uri, code):
    """Atlas-only command never targets local Mongo or a missing URI."""
    monkeypatch.setattr(operator, "resolve_mongo_uri", lambda: uri)
    monkeypatch.setattr(operator, "MongoClient",
                        lambda *_args, **_kw: pytest.fail("DATABASE_CONNECTION_NOT_AUTHORIZED"))
    assert operator.main(["--check"]) == 1
    assert "ERROR_CODE=" + code in capsys.readouterr().err


def test_read_only_check_and_explicit_successful_apply(monkeypatch, capsys):
    """--check cannot create indexes; approved --apply must reread source."""
    database = Database()
    _mock_source(monkeypatch, database)
    assert operator.main(["--check"]) == 0
    check = capsys.readouterr().out
    assert "MISSING_INDEXES" in check
    assert "DATABASE_MUTATIONS=NONE" in check
    assert database.ddl_count == 0
    assert operator.main(["--apply", "--confirm-database", "wilsy"]) == 0
    apply = capsys.readouterr().out
    assert "ATLAS_STRATEGY_INDEX_STATE=VERIFIED" in apply
    assert "REQUIRED_UNIQUE_INDEXES=2" in apply
    assert database.ddl_count == 1
    assert operator.main(["--check"]) == 0
    assert "VERIFIED_EXISTING" in capsys.readouterr().out


def test_existing_source_data_must_not_be_mutated(monkeypatch, capsys):
    """Never backfill or alter preexisting link evidence in an index migration."""
    database = Database(populated=True)
    _mock_source(monkeypatch, database)
    result = operator.main(["--apply", "--confirm-database", "wilsy"])
    assert result == 1
    assert "ATLAS_STRATEGY_EXISTING_RECORDS_REVIEW_REQUIRED" in capsys.readouterr().err
    assert database.ddl_count == 0


# ARTIFACT: test_provision_atlas_strategy_project_link_indexes.py
# VERSION: v1.0.0-ATLAS-INDEX-PREFLIGHT-UNIT-CERT
# AUTHORITY BOUNDARY: Synthetic no-network index migration certificate only.
# TENANT POSTURE: No mutation or foreign tenant access through test calls.
# FAIL-CLOSED POSTURE: Wrong target/confirmation and existing data deny DDL.
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively.
# END OF WILSY OS SOVEREIGN ARTIFACT
