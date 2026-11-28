"""TITLE: WILSY OS Atlas Company Publication Index Admission Certificate.
VERSION: v1.0.0-EXPLICIT-ATLAS-COMPANY-INDEX-UNIT-CERT
AUTHORITY: WILSY OS Core Governance / AGENTS.md.
EPITOME: Isolated no-network proof of safe publication index migration.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tests/unit/test_provision_atlas_company_document_indexes.py
COLLABORATION / OWNERSHIP: Company document registry and guarded Atlas index tool.
CERTIFICATION / UPDATE DATE: 2026-11-23
CHANGELOG: v1.0.0-EXPLICIT-ATLAS-COMPANY-INDEX-UNIT-CERT validates inert
default, required explicit database confirmation, Atlas-only source gate,
no-DDL metadata preflight, existing-source refusal and post-DDL verification.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC2 CC7.2.
SECURITY / PRIVACY POSTURE: Synthetic URI and database only; no real network.
TENANT BOUNDARY: Exact canonical test database, no tenant document writes.
AUTHORITY BOUNDARY: Never simulates or bypasses independent publisher IAM.
FINANCIAL AUTHORITY BOUNDARY: Kennel EOS exclusively.
"""
from __future__ import annotations

from types import SimpleNamespace

import pytest

from tools.eos.ops import provision_atlas_company_document_indexes as operator


class Database:
    """Synthetic source metadata representing document/command collections."""

    def __init__(self, *, populated: bool = False) -> None:
        """Initialize independent fake index and row states."""
        self.populated = populated
        self.ready = False
        self.ddl_count = 0

    def list_collection_names(self):
        """Expose current logical source names without adding them."""
        return list(operator._COLLECTIONS)

    def __getitem__(self, _name):
        """Return the fake collection for bounded source inspection."""
        return self

    def count_documents(self, _query, *, limit):
        """Return presence, never bodies or principal identities."""
        assert limit == 1
        return int(self.populated)


class Client:
    """Fake replica set without any socket or connection string."""

    def __init__(self, database: Database) -> None:
        """Hold the test database."""
        self.database = database
        self.admin = SimpleNamespace(command=lambda _operation: {"setName": "synthetic-rs"})

    def __enter__(self):
        """Acquire no real connection."""
        return self

    def __exit__(self, *_exc):
        """Release fake transport."""
        return None

    def get_database(self, name):
        """Prevent test writes to any noncanonical database."""
        assert name == "wilsy"
        return self.database


def _configure(monkeypatch, database: Database) -> None:
    """Install synthetic Atlas, DB and source index implementation."""
    monkeypatch.setattr(operator, "resolve_mongo_uri", lambda: "mongodb+srv://synthetic.invalid/wilsy")
    monkeypatch.setattr(operator, "_assert_atlas_source", lambda _uri: None)
    monkeypatch.setattr(operator, "MongoClient", lambda *_a, **_k: Client(database))
    def require(_registry):
        if not database.ready:
            raise operator.CompanyDocumentError("COMPANY_DOCUMENT_INDEX_PROVISIONING_REQUIRED")
    def provision(_registry):
        database.ddl_count += 1
        database.ready = True
    monkeypatch.setattr(operator.CompanyOperatingDocumentRegistry, "require_command_indexes", require)
    monkeypatch.setattr(operator.CompanyOperatingDocumentRegistry, "provision_indexes", provision)


def test_default_and_missing_confirmation_cannot_connect(monkeypatch, capsys):
    """Nothing without an explicit action and exact target confirmation."""
    monkeypatch.setattr(operator, "MongoClient",
                        lambda *_a, **_k: pytest.fail("UNAPPROVED_DATABASE_CONNECTION"))
    assert operator.main([]) == 0
    assert "DRY_RUN_NOT_EXECUTED" in capsys.readouterr().out
    assert operator.main(["--apply"]) == 2
    assert "CONFIRMATION_REQUIRED" in capsys.readouterr().out


@pytest.mark.parametrize("uri", ["", "mongodb://127.0.0.1:27017/wilsy"])
def test_standard_or_empty_uri_cannot_run_atlas_migration(monkeypatch, capsys, uri):
    """No fallback to local or unset shell database."""
    monkeypatch.setattr(operator, "resolve_mongo_uri", lambda: uri)
    monkeypatch.setattr(operator, "MongoClient",
                        lambda *_a, **_k: pytest.fail("UNVERIFIED_DATABASE_CONNECTION"))
    assert operator.main(["--check"]) == 1
    assert "COMPANY_DOC_ATLAS_SRV_REQUIRED" in capsys.readouterr().err


def test_read_only_preflight_and_exact_index_readback(monkeypatch, capsys):
    """Only explicit confirmed operator apply may create the required indexes."""
    database = Database()
    _configure(monkeypatch, database)
    assert operator.main(["--check"]) == 0
    assert "MISSING_INDEXES" in capsys.readouterr().out
    assert database.ddl_count == 0
    assert operator.main(["--apply", "--confirm-database", "wilsy"]) == 0
    assert "REQUIRED_UNIQUE_INDEXES=3" in capsys.readouterr().out
    assert database.ddl_count == 1
    assert operator.main(["--check"]) == 0
    assert "VERIFIED_EXISTING" in capsys.readouterr().out


def test_preexisting_records_stop_admission(monkeypatch, capsys):
    """Do not alter or migrate even one preexisting company revision/receipt."""
    database = Database(populated=True)
    _configure(monkeypatch, database)
    assert operator.main(["--apply", "--confirm-database", "wilsy"]) == 1
    assert "COMPANY_DOC_SOURCE_RECONCILIATION_REQUIRED" in capsys.readouterr().err
    assert database.ddl_count == 0


# ARTIFACT: test_provision_atlas_company_document_indexes.py
# VERSION: v1.0.0-EXPLICIT-ATLAS-COMPANY-INDEX-UNIT-CERT
# AUTHORITY BOUNDARY: Synthetic operator-only DDL certificate.
# TENANT POSTURE: No application principal or publication state manufactured.
# FAIL-CLOSED POSTURE: Unsafe state aborts index creation.
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively.
# END OF WILSY OS SOVEREIGN ARTIFACT
