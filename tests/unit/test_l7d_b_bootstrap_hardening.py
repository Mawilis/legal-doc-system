"""L7D-B direct certificate for import-inert, explicit database bootstrap.

TITLE: WILSY OS L7D-B Bootstrap Hardening Certificate
VERSION: v1.0.0-L7D-B-BOOTSTRAP-HARDENING-CERT
AUTHORITY: Wilsy OS Core Governance
EPITOME: Proves kernel/billing imports are inert and explicit persistence is
         resolved only after a caller-owned bootstrap succeeds.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tests/unit/test_l7d_b_bootstrap_hardening.py
TENANT BOUNDARY: Billing operations retain explicit tenant predicates.
AUTHORITY BOUNDARY: Certificate covers lifecycle wiring, not domain authority.
FINANCIAL AUTHORITY BOUNDARY: Kennel EOS exclusively owns execution/settlement.
FAIL-CLOSED DECLARATION: Missing persistence raises an explicit unavailable error.
"""

from __future__ import annotations

import subprocess
import sys
from types import SimpleNamespace
from typing import Any

import pytest

import tools.eos.api.billing_router as billing_router
import tools.eos.kernel.db as kernel_db
import tools.eos.saas.billing.billing_registry as billing_registry


def test_kernel_billing_and_router_imports_are_inert() -> None:
    code = r'''
import pymongo, threading
calls = []
class FakeDatabase:
    name = "import-only"
    def __getitem__(self, name):
        return object()
    def get_collection(self, name, **kwargs):
        return object()
class ForbiddenClient:
    def __init__(self, *args, **kwargs):
        calls.append(("MongoClient", kwargs.get("connect")))
    def get_default_database(self, *args, **kwargs):
        return FakeDatabase()
class ForbiddenThread:
    def __init__(self, *args, **kwargs):
        calls.append("Thread")
        raise AssertionError("import attempted thread")
pymongo.MongoClient = ForbiddenClient
threading.Thread = ForbiddenThread
import tools.eos.kernel.db as db
import tools.eos.saas.billing.billing_registry as registry
import tools.eos.api.billing_router as router
assert db.get_client() is None
assert db.get_database() is None
assert db.get_db_status()["retry_thread_alive"] is False
assert registry.db is None and registry.client is None
assert router.db is None and router.mongo_client is None
assert all(kind == "MongoClient" and connect is False for kind, connect in calls)
print("IMPORT_INERT=PASS")
'''
    result = subprocess.run([sys.executable, "-c", code], check=True, capture_output=True, text=True)
    assert "IMPORT_INERT=PASS" in result.stdout


def test_explicit_connect_disconnect_and_reconnect(monkeypatch: pytest.MonkeyPatch) -> None:
    class FakeDatabase:
        name = "l7d_b"

    class FakeAdmin:
        def command(self, name: str) -> dict[str, int]:
            assert name == "ping"
            return {"ok": 1}

    class FakeClient:
        def __init__(self, *_args: Any, **_kwargs: Any) -> None:
            self.admin = FakeAdmin()
            self.closed = False

        def get_database(self) -> FakeDatabase:
            return FakeDatabase()

        def close(self) -> None:
            self.closed = True

    monkeypatch.setenv("MONGODB_URI", "mongodb://explicit/l7d_b")
    monkeypatch.setattr(kernel_db, "MongoClient", FakeClient)
    kernel_db.disconnect_db()
    assert kernel_db.connect_db() == (True, "Connected successfully")
    assert kernel_db.is_db_ready() is True
    assert kernel_db.get_database() is not None
    kernel_db.disconnect_db()
    assert kernel_db.is_db_ready() is False
    assert kernel_db.get_database() is None
    assert kernel_db.connect_db() == (True, "Connected successfully")
    kernel_db.disconnect_db()


def test_billing_fails_closed_without_active_database(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(billing_registry, "get_database", lambda: None)
    monkeypatch.setattr(billing_registry, "platform_invoices_coll", None)
    with pytest.raises(RuntimeError, match="BILLING_DATABASE_UNAVAILABLE"):
        billing_registry.BillingRegistry().create_platform_invoice(
            "tenant-l7d-b",
            line_items=[{"description": "service", "quantity": 1, "unit_price": 10}],
        )


def test_billing_resolves_live_database_after_explicit_connect(monkeypatch: pytest.MonkeyPatch) -> None:
    inserted: list[dict[str, Any]] = []

    class Collection:
        def find_one(self, *_args: Any, **_kwargs: Any) -> None:
            return None

        def insert_one(self, doc: dict[str, Any], **_kwargs: Any) -> SimpleNamespace:
            inserted.append(doc)
            return SimpleNamespace(inserted_id="invoice")

    collection = Collection()

    class Database:
        def __getitem__(self, name: str) -> Collection:
            assert name == "platform_invoices"
            return collection

    monkeypatch.setattr(billing_registry, "get_database", lambda: Database())
    monkeypatch.setattr(billing_registry, "platform_invoices_coll", None)
    invoice = billing_registry.BillingRegistry().create_platform_invoice(
        "tenant-l7d-b",
        line_items=[{"description": "service", "quantity": 1, "unit_price": 10}],
        idempotency_key="l7d-b-explicit",
    )
    assert inserted and inserted[0]["tenant_id"] == "tenant-l7d-b"
    assert invoice.tenant_id == "tenant-l7d-b"


def test_router_resolves_live_kernel_handles(monkeypatch: pytest.MonkeyPatch) -> None:
    database = object()
    client = object()
    monkeypatch.setattr(billing_router, "db", None)
    monkeypatch.setattr(billing_router, "mongo_client", None)
    monkeypatch.setattr(billing_router, "get_kernel_database", lambda: database)
    monkeypatch.setattr(billing_router, "get_kernel_client", lambda: client)
    assert billing_router._require_db() is database
    assert billing_router._require_mongo_client() is client


# ARTIFACT: test_l7d_b_bootstrap_hardening.py
# VERSION: v1.0.0-L7D-B-BOOTSTRAP-HARDENING-CERT
# AUTHORITY BOUNDARY: Direct lifecycle certificate only.
# TENANT POSTURE: Existing tenant-scoped billing predicates remain authoritative.
# FAIL-CLOSED POSTURE: Import, persistence, and bootstrap failures are explicit.
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively.
# END OF WILSY OS SOVEREIGN ARTIFACT
