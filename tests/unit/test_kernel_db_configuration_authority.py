"""Direct certificate for the canonical Kernel database configuration authority.

TITLE: WILSY OS Kernel Database Configuration Authority Certificate
VERSION: v1.0.0-R1D-B0F-B3B-R0-CANONICAL-URI
AUTHORITY: Wilsy OS Core Governance
EPITOME: Proves that MONGODB_URI is the sole production database authority,
         production never receives repository-dotenv rescue, non-production
         dotenv remains controlled, and diagnostics do not expose credentials.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tests/unit/test_kernel_db_configuration_authority.py
COLLABORATION / OWNERSHIP: Certificate for tools.eos.kernel.db.
CERTIFICATION / UPDATE DATE: 2026-09-17
CHANGELOG: v1.0.0-R1D-B0F-B3B-R0-CANONICAL-URI - Covers authority conflicts,
           fail-closed production bootstrap, dotenv posture, and safe status.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2.
TENANT BOUNDARY: Database selection is configuration-owned, never request-owned.
AUTHORITY BOUNDARY: Kernel connection lifecycle only; no tenant or auth grant.
"""
from __future__ import annotations

import inspect
import os
from types import SimpleNamespace
from typing import Any

import pytest

import tools.eos.kernel.db as kernel_db


def _disable_dotenv(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(kernel_db, "load_dotenv", lambda *_args, **_kwargs: False)


def test_process_mongodb_uri_is_canonical_even_when_legacy_aliases_differ(monkeypatch: pytest.MonkeyPatch) -> None:
    _disable_dotenv(monkeypatch)
    monkeypatch.setenv("ENV", "development")
    monkeypatch.setenv("MONGODB_URI", "mongodb://canonical/wilsy")
    monkeypatch.setenv("MONGO_URI", "mongodb://legacy/other")
    monkeypatch.setenv("DATABASE_URL", "mongodb://database-url/other")
    monkeypatch.setenv("WILSY_MONGO_URI", "mongodb://wilsy-alias/other")
    assert kernel_db.resolve_mongo_uri() == "mongodb://canonical/wilsy"


@pytest.mark.parametrize("legacy_name", ["MONGO_URI", "DATABASE_URL", "WILSY_MONGO_URI"])
def test_missing_canonical_uri_never_falls_back_to_legacy_alias(monkeypatch: pytest.MonkeyPatch, legacy_name: str) -> None:
    _disable_dotenv(monkeypatch)
    monkeypatch.setenv("ENV", "test")
    monkeypatch.delenv("MONGODB_URI", raising=False)
    monkeypatch.setenv(legacy_name, "mongodb://legacy/other")
    assert kernel_db.resolve_mongo_uri() == ""


def test_production_missing_authority_fails_before_mongo_client_creation(monkeypatch: pytest.MonkeyPatch) -> None:
    _disable_dotenv(monkeypatch)
    monkeypatch.setenv("ENV", "production")
    monkeypatch.delenv("MONGODB_URI", raising=False)
    monkeypatch.setenv("MONGO_URI", "mongodb://legacy/other")
    created: list[bool] = []

    class ForbiddenClient:
        def __init__(self, *_args: Any, **_kwargs: Any) -> None:
            created.append(True)

    monkeypatch.setattr(kernel_db, "MongoClient", ForbiddenClient)
    kernel_db.disconnect_db()
    connected, detail = kernel_db.connect_db()
    assert connected is False
    assert "missing" in detail.lower()
    assert created == []


def test_production_deployment_uri_is_not_overridden_or_dotenv_loaded(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("ENV", "production")
    monkeypatch.setenv("MONGODB_URI", "mongodb://deployment/wilsy")
    monkeypatch.setenv("MONGO_URI", "mongodb://legacy/other")

    def forbidden_dotenv(*_args: Any, **_kwargs: Any) -> None:
        raise AssertionError("repository dotenv is forbidden in production")

    monkeypatch.setattr(kernel_db, "load_dotenv", forbidden_dotenv)
    assert kernel_db.resolve_mongo_uri() == "mongodb://deployment/wilsy"


def test_nonproduction_dotenv_can_supply_only_missing_canonical_uri(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("ENV", "development")
    monkeypatch.delenv("MONGODB_URI", raising=False)

    def controlled_dotenv(*_args: Any, **_kwargs: Any) -> None:
        os.environ.setdefault("MONGODB_URI", "mongodb://dotenv/wilsy")

    monkeypatch.setattr(kernel_db, "load_dotenv", controlled_dotenv)
    assert kernel_db.resolve_mongo_uri() == "mongodb://dotenv/wilsy"


def test_safe_status_contains_database_name_but_no_uri_or_credentials(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(kernel_db, "_db", SimpleNamespace(name="wilsy-os-dev"))
    monkeypatch.setattr(kernel_db, "_client", object())
    monkeypatch.setattr(kernel_db, "_last_error", None)
    status = kernel_db.get_db_status()
    assert status == {
        "ready": False,
        "client_created": True,
        "database_name": "wilsy-os-dev",
        "last_error": None,
        "retry_thread_alive": False,
    }
    rendered = repr(status)
    assert "mongodb://" not in rendered
    assert "password" not in rendered.lower()


def test_resolver_source_has_no_legacy_fallback_authorities() -> None:
    source = inspect.getsource(kernel_db.resolve_mongo_uri)
    assert "MONGO_URI" not in source
    assert "DATABASE_URL" not in source
    assert "WILSY_MONGO_URI" not in source
    assert "localhost" not in source


# ARTIFACT: test_kernel_db_configuration_authority.py
# VERSION: v1.0.0-R1D-B0F-B3B-R0-CANONICAL-URI
# AUTHORITY BOUNDARY: Kernel configuration certificate only.
# TENANT POSTURE: Database identity is not selected by tenant aliases or requests.
# FAIL-CLOSED POSTURE: Missing production MONGODB_URI prevents MongoClient creation.
# FINANCIAL EXECUTION AUTHORITY: none; Kennel EOS remains exclusive.
# END OF WILSY OS SOVEREIGN ARTIFACT
