"""L7D-B host certificate for explicit Kernel/Billing bootstrap lifecycle.

TITLE: WILSY OS L7D-B Real-Mongo Bootstrap Certificate
VERSION: v1.0.0-L7D-B-BOOTSTRAP-HARDENING-RM-CERT
AUTHORITY: Wilsy OS Core Governance
EPITOME: Certifies explicit connect, durable billing persistence, disconnect,
         fail-closed absence, and deterministic reconnect on the local replica set.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tests/integration/test_l7d_b_bootstrap_hardening_real_mongo.py
TENANT BOUNDARY: Synthetic tenant data is isolated to a UUID database.
AUTHORITY BOUNDARY: Kernel owns connection lifecycle; BillingRegistry owns only
                     commercial persistence and historical projections.
FINANCIAL AUTHORITY BOUNDARY: Kennel EOS exclusively owns execution/settlement.
FAIL-CLOSED DECLARATION: Unavailable persistence is never represented as absence.
"""

from __future__ import annotations

import os
import uuid
from typing import Any, Iterator

import pytest
from pymongo import MongoClient
from pymongo.read_concern import ReadConcern
from pymongo.write_concern import WriteConcern

import tools.eos.kernel.db as kernel_db
from tools.eos.saas.billing.billing_registry import BillingRegistry


URI = os.getenv(
    "TEST_VENDOR_MONGO_URI",
    "mongodb://127.0.0.1:27027/?replicaSet=wilsyVendorCertRS",
)
EXPECTED_REPLICA_SET = "wilsyVendorCertRS"


@pytest.fixture()
def isolated_database(monkeypatch: pytest.MonkeyPatch) -> Iterator[Any]:
    client = MongoClient(URI, serverSelectionTimeoutMS=3000, retryWrites=True)
    database = None
    try:
        hello = client.admin.command("hello")
        assert hello.get("setName") == EXPECTED_REPLICA_SET
        assert hello.get("isWritablePrimary") is True
        database = client.get_database(
            "l7db_" + uuid.uuid4().hex[:20],
            read_concern=ReadConcern("majority"),
            write_concern=WriteConcern(w="majority", j=True),
        )
        monkeypatch.setenv(
            "MONGODB_URI",
            f"mongodb://127.0.0.1:27027/{database.name}?replicaSet={EXPECTED_REPLICA_SET}",
        )
        kernel_db.disconnect_db()
        connected, detail = kernel_db.connect_db()
        assert connected, detail
        yield database
    finally:
        kernel_db.disconnect_db()
        if database is not None:
            client.drop_database(database.name)
        client.close()


def test_explicit_bootstrap_billing_persistence_disconnect_and_reconnect(
    isolated_database: Any,
) -> None:
    registry = BillingRegistry()
    invoice = registry.create_platform_invoice(
        "tenant-l7d-b-real",
        line_items=[{"description": "service", "quantity": 1, "unit_price": 125}],
        idempotency_key="l7d-b-real-key",
    )
    stored = isolated_database["platform_invoices"].find_one(
        {"tenant_id": "tenant-l7d-b-real", "invoice_id": invoice.invoice_id}
    )
    assert stored is not None
    assert stored["tenant_id"] == "tenant-l7d-b-real"

    kernel_db.disconnect_db()
    assert kernel_db.is_db_ready() is False
    with pytest.raises(RuntimeError, match="BILLING_DATABASE_UNAVAILABLE"):
        registry.create_platform_invoice(
            "tenant-l7d-b-real",
            line_items=[{"description": "service", "quantity": 1, "unit_price": 125}],
            idempotency_key="l7d-b-after-disconnect",
        )

    connected, detail = kernel_db.connect_db()
    assert connected, detail
    replay = registry.get_platform_invoice("tenant-l7d-b-real", invoice.invoice_id)
    assert replay is not None
    assert replay.to_dict() == invoice.to_dict()


# ARTIFACT: test_l7d_b_bootstrap_hardening_real_mongo.py
# VERSION: v1.0.0-L7D-B-BOOTSTRAP-HARDENING-RM-CERT
# AUTHORITY BOUNDARY: Host lifecycle certificate only.
# TENANT POSTURE: UUID-isolated synthetic tenant data and explicit tenant queries.
# FAIL-CLOSED POSTURE: Disconnect and unavailable persistence reject operations.
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively.
# END OF WILSY OS SOVEREIGN ARTIFACT
