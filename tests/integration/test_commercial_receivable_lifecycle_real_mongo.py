"""WILSY OS — M11E2 commercial receivable lifecycle real-Mongo certificate.

TITLE: M11E2 Commercial Receivable Lifecycle Real-Mongo Certificate
VERSION: v1.0.0-M11E2-RM-AR
AUTHORITY: Wilsy OS Core Governance
EPITOME: Certifies durable receivables, lawful Kennel settlement consumption,
         reconciliation, and PLATFORM closure without test-owned financial truth.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tests/integration/test_commercial_receivable_lifecycle_real_mongo.py
COLLABORATION / OWNERSHIP: M11 AR / reconciliation certification owner.
CERTIFICATION / UPDATE DATE: 2026-09-12
CHANGELOG: v1.0.0 establishes RM-AR01 through RM-AR06.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2.
SECURITY / PRIVACY POSTURE: Synthetic UUID identities only; no credentials or raw provider payloads.
TENANT BOUNDARY: Every durable identity and projection is tenant-scoped.
AUTHORITY BOUNDARY: Python EOS owns commercial truth; Kennel EOS exclusively owns execution and settlement evidence.
FINANCIAL AUTHORITY BOUNDARY: Test fixtures supply external capability evidence only; they never construct execution truth, settlement evidence, R3F, or AR1P truth.
TRANSACTION BOUNDARY: Production Kennel and projection functions retain their caller-owned transaction contracts.
FAIL-CLOSED DECLARATION: Replay divergence, corruption, missing R3F evidence, and cross-tenant closure reject.
"""

from __future__ import annotations

from dataclasses import replace
from pathlib import Path
import os
import runpy
from typing import Any
import uuid

import pytest
from pymongo import MongoClient

from tools.eos.saas.billing.commercial_receivable_adaptation import (
    client_invoice_to_receivable,
    platform_invoice_to_receivable,
)
from tools.eos.saas.billing.commercial_receivable_registry import (
    CommercialReceivableRegistry,
    CommercialReceivableRegistryError,
)
from tools.eos.saas.billing.platform_billing_commercial_receivable_closure_projection import (
    project_platform_billing_commercial_receivable_closure,
)
from tools.eos.saas.billing.platform_billing_commercial_receivable_closure_projection_registry import (
    PlatformBillingCommercialReceivableClosureProjectionRegistry,
)
from tools.eos.saas.billing.platform_billing_commercial_settlement_projection_registry import (
    PlatformBillingCommercialSettlementProjectionNotFoundError,
)
from tools.eos.saas.domain.billing import (
    ClientInvoice,
    InvoiceStatus,
    PlatformInvoice,
)
from tools.eos.saas.domain.commercial_receivable import (
    ReceivableFamily,
    ReceivableStatus,
)
from tools.eos.saas.domain.commercial_receivable_reconciliation import (
    CommercialReceivableReconciliation,
)


URI = os.getenv("TEST_VENDOR_MONGO_URI", "")

# Reuse the already-certified R3F-C harness only as deterministic external
# capability fixture infrastructure. Its production calls remain the authority.
_FIXTURE_PATH = Path(__file__).with_name(
    "test_platform_billing_commercial_settlement_projection_real_mongo.py"
)
_FIXTURE = runpy.run_path(str(_FIXTURE_PATH))
_r3f_graph: Any = _FIXTURE["graph"]
_r3f_project: Any = _FIXTURE["project"]


def _mongo(prefix: str) -> tuple[Any, Any]:
    if not URI:
        raise RuntimeError("TEST_VENDOR_MONGO_URI is required")
    client = MongoClient(
        URI,
        serverSelectionTimeoutMS=2000,
        retryWrites=True,
    )
    client.admin.command("ping")
    database = client[f"{prefix}_{uuid.uuid4().hex}"]
    return client, database


def _platform_invoice(tenant_id: str, invoice_id: str) -> PlatformInvoice:
    return PlatformInvoice(
        tenant_id,
        invoice_id,
        status=InvoiceStatus.OPEN,
        total=100.0,
        amount=100.0,
        outstanding_amount=100.0,
        currency="ZAR",
    )


def _client_invoice(tenant_id: str, invoice_id: str) -> ClientInvoice:
    return ClientInvoice(
        tenant_id,
        invoice_id,
        status=InvoiceStatus.OPEN,
        total=200.0,
        amount=200.0,
        outstanding_amount=200.0,
        currency="ZAR",
    )


def test_rm_ar01_platform_invoice_receivable_durability() -> None:
    client, database = _mongo("m11e2_ar01")
    try:
        tenant = f"tenant-{uuid.uuid4().hex}"
        invoice = _platform_invoice(tenant, f"platform-{uuid.uuid4().hex}")
        receivable = platform_invoice_to_receivable(invoice)
        collection = database["commercial_receivables"]
        CommercialReceivableRegistry.ensure_indexes(collection)

        created = CommercialReceivableRegistry.create(receivable, collection)
        hydrated = CommercialReceivableRegistry.get(
            tenant,
            ReceivableFamily.PLATFORM,
            invoice.invoice_id,
            collection,
        )

        assert created == hydrated == receivable
        assert hydrated.receivable_family is ReceivableFamily.PLATFORM
        assert hydrated.source_invoice_id == invoice.invoice_id
        assert hydrated.original_amount_minor == 10_000
        assert hydrated.outstanding_amount_minor == 10_000
        assert collection.count_documents({"tenant_id": tenant}) == 1
    finally:
        client.close()


def test_rm_ar02_client_invoice_receivable_durability() -> None:
    client, database = _mongo("m11e2_ar02")
    try:
        tenant = f"tenant-{uuid.uuid4().hex}"
        invoice = _client_invoice(tenant, f"client-{uuid.uuid4().hex}")
        receivable = client_invoice_to_receivable(invoice)
        collection = database["commercial_receivables"]
        CommercialReceivableRegistry.ensure_indexes(collection)

        CommercialReceivableRegistry.create(receivable, collection)
        hydrated = CommercialReceivableRegistry.get(
            tenant,
            ReceivableFamily.CLIENT,
            invoice.invoice_id,
            collection,
        )

        assert hydrated == receivable
        assert hydrated.receivable_family is ReceivableFamily.CLIENT
        assert hydrated.source_invoice_id == invoice.invoice_id
        assert hydrated.original_amount_minor == 20_000
        assert hydrated.outstanding_amount_minor == 20_000
        assert collection.count_documents({"tenant_id": tenant}) == 1
    finally:
        client.close()


def test_rm_ar03_identical_receivable_replay_is_idempotent() -> None:
    client, database = _mongo("m11e2_ar03")
    try:
        tenant = f"tenant-{uuid.uuid4().hex}"
        invoice = _platform_invoice(tenant, f"platform-{uuid.uuid4().hex}")
        receivable = platform_invoice_to_receivable(invoice)
        collection = database["commercial_receivables"]
        CommercialReceivableRegistry.ensure_indexes(collection)

        first = CommercialReceivableRegistry.create(receivable, collection)
        second = CommercialReceivableRegistry.create(receivable, collection)

        assert first == second == receivable
        assert collection.count_documents(
            {
                "tenant_id": tenant,
                "receivable_family": ReceivableFamily.PLATFORM.value,
                "source_invoice_id": invoice.invoice_id,
            }
        ) == 1
    finally:
        client.close()


def test_rm_ar04_divergence_and_corruption_fail_closed() -> None:
    client, database = _mongo("m11e2_ar04")
    try:
        tenant = f"tenant-{uuid.uuid4().hex}"
        invoice = _platform_invoice(tenant, f"platform-{uuid.uuid4().hex}")
        receivable = platform_invoice_to_receivable(invoice)
        collection = database["commercial_receivables"]
        CommercialReceivableRegistry.ensure_indexes(collection)
        CommercialReceivableRegistry.create(receivable, collection)

        divergent = replace(
            receivable,
            outstanding_amount_minor=receivable.outstanding_amount_minor - 1,
        )
        with pytest.raises(
            CommercialReceivableRegistryError,
            match="M11B_RECEIVABLE_REPLAY_CONFLICT",
        ):
            CommercialReceivableRegistry.create(divergent, collection)

        collection.update_one(
            {
                "tenant_id": tenant,
                "receivable_family": ReceivableFamily.PLATFORM.value,
                "source_invoice_id": invoice.invoice_id,
            },
            {"$set": {"receivable_fingerprint": "0" * 128}},
        )
        with pytest.raises(
            CommercialReceivableRegistryError,
            match="M11B_RECEIVABLE_CORRUPT",
        ):
            CommercialReceivableRegistry.get(
                tenant,
                ReceivableFamily.PLATFORM,
                invoice.invoice_id,
                collection,
            )

        assert collection.count_documents({"tenant_id": tenant}) == 1
    finally:
        client.close()


def test_rm_ar05_settlement_reconciliation_and_ar1p_durability() -> None:
    fixture_source = _FIXTURE_PATH.read_text(encoding="utf-8")
    assert "record_platform_billing_financial_execution_truth" not in fixture_source
    assert "record_platform_billing_financial_settlement_evidence" not in fixture_source
    assert "ingest_authenticated_provider_observation" in fixture_source
    assert "ingest_authenticated_settlement_observation" in fixture_source
    assert "bridge_settlement_observation_to_platform_evidence" in fixture_source

    client, database, state = _r3f_graph()
    try:
        tenant = state["tenant"]
        invoice = state["invoice"]

        receivable_collection = database["commercial_receivables"]
        CommercialReceivableRegistry.ensure_indexes(receivable_collection)
        receivable = platform_invoice_to_receivable(invoice)
        CommercialReceivableRegistry.create(
            receivable,
            receivable_collection,
        )

        settlement_projection = _r3f_project(client, database, state)
        reconciliation = CommercialReceivableReconciliation.reconcile(
            receivable,
            adjustments=(),
            settlements=(settlement_projection,),
            effective_at=settlement_projection.settled_at,
        )

        closure_collection = database[
            "platform_billing_commercial_receivable_closure_projections"
        ]
        PlatformBillingCommercialReceivableClosureProjectionRegistry.ensure_indexes(
            closure_collection
        )

        with client.start_session() as session:
            with session.start_transaction():
                closure = (
                    project_platform_billing_commercial_receivable_closure(
                        tenant,
                        settlement_projection.commercial_settlement_projection_id,
                        commercial_settlement_projection_collection=database[
                            "projections"
                        ],
                        platform_invoice_collection=database["invoices"],
                        closure_projection_collection=closure_collection,
                        session=session,
                        projected_at=settlement_projection.projected_at,
                    )
                )

        durable_closure = (
            PlatformBillingCommercialReceivableClosureProjectionRegistry.get(
                tenant,
                closure.commercial_receivable_closure_projection_id,
                closure_collection,
            )
        )
        durable_receivable = CommercialReceivableRegistry.get(
            tenant,
            ReceivableFamily.PLATFORM,
            invoice.invoice_id,
            receivable_collection,
        )

        assert reconciliation.matched_settlement_minor == (
            receivable.original_amount_minor
        )
        assert reconciliation.outstanding_amount_minor == 0
        assert durable_closure.receivable_status == "CLOSED"
        assert durable_closure.remaining_receivable_amount_minor == 0
        assert durable_closure.closed_receivable_amount_minor == (
            receivable.original_amount_minor
        )
        assert durable_closure.settlement_evidence_id == (
            state["settlement"].settlement_evidence_id
        )

        # AR1P is a closure projection; it does not rewrite the canonical
        # receivable into caller-asserted paid/settled truth.
        assert durable_receivable.status is ReceivableStatus.OPEN
        assert durable_receivable.outstanding_amount_minor == (
            receivable.original_amount_minor
        )

        assert database[
            "platform_billing_financial_settlement_evidence"
        ].count_documents({"tenant_id": tenant}) == 1
        assert database["projections"].count_documents(
            {"tenant_id": tenant}
        ) == 1
        assert closure_collection.count_documents(
            {"tenant_id": tenant}
        ) == 1
    finally:
        client.close()


def test_rm_ar06_closure_firewall_requires_r3f_and_exact_tenant() -> None:
    client, database, state = _r3f_graph()
    try:
        tenant = state["tenant"]
        settlement = state["settlement"]
        expected_projection_id = (
            f"platform-commercial-settlement-{settlement.settlement_evidence_id}"
        )
        closure_collection = database[
            "platform_billing_commercial_receivable_closure_projections"
        ]
        PlatformBillingCommercialReceivableClosureProjectionRegistry.ensure_indexes(
            closure_collection
        )

        # Durable Kennel settlement evidence alone is not AR1P closure authority.
        with client.start_session() as session:
            with session.start_transaction():
                with pytest.raises(
                    PlatformBillingCommercialSettlementProjectionNotFoundError,
                    match="R3F_PROJECTION_NOT_FOUND",
                ):
                    project_platform_billing_commercial_receivable_closure(
                        tenant,
                        expected_projection_id,
                        commercial_settlement_projection_collection=database[
                            "projections"
                        ],
                        platform_invoice_collection=database["invoices"],
                        closure_projection_collection=closure_collection,
                        session=session,
                    )

        assert closure_collection.count_documents({}) == 0

        settlement_projection = _r3f_project(client, database, state)

        # Even durable R3F truth cannot cross the tenant boundary.
        with client.start_session() as session:
            with session.start_transaction():
                with pytest.raises(
                    PlatformBillingCommercialSettlementProjectionNotFoundError,
                    match="R3F_PROJECTION_NOT_FOUND",
                ):
                    project_platform_billing_commercial_receivable_closure(
                        f"wrong-{tenant}",
                        settlement_projection.commercial_settlement_projection_id,
                        commercial_settlement_projection_collection=database[
                            "projections"
                        ],
                        platform_invoice_collection=database["invoices"],
                        closure_projection_collection=closure_collection,
                        session=session,
                    )

        assert closure_collection.count_documents({}) == 0
    finally:
        client.close()


# ARTIFACT: test_commercial_receivable_lifecycle_real_mongo.py
# VERSION: v1.0.0-M11E2-RM-AR
# AUTHORITY BOUNDARY: Certification only; no financial authority is created here.
# TENANT POSTURE: Tenant/family/projection boundaries are explicit and fail closed.
# FIXTURE POSTURE: Deterministic external capability evidence only; production Kennel owns execution and settlement truth.
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively.
# END OF WILSY OS SOVEREIGN ARTIFACT
