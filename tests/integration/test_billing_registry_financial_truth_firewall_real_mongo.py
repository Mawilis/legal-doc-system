"""WILSY OS — BillingRegistry financial-truth firewall real-Mongo certificate.

TITLE:
    WAI-VAS23R3B1 BillingRegistry Financial-Truth Firewall Certificate

VERSION:
    v1.0.0-BILLING-FINANCIAL-TRUTH-FIREWALL-REAL-MONGO-CERT

AUTHORITY:
    Wilsy OS Core Governance

EPITOME:
    Certifies that BillingRegistry may create only pending collection evidence
    while direct payment execution truth, refund execution, paid state, and
    settlement mutation fail closed behind Kennel EOS authority.

ABSOLUTE CANONICAL PATH:
    /Users/wilsonkhanyezi/legal-doc-system/tests/integration/test_billing_registry_financial_truth_firewall_real_mongo.py

COLLABORATION / OWNERSHIP:
    Wilson Khanyezi / Wilsy OS Core Engineering

CERTIFICATION / UPDATE DATE:
    2026-09-04

CHANGELOG:
    v1.0.0 establishes the R3B1 governed real-Mongo authority certificate.

COMPLIANCE:
    POPIA section 19; GDPR Article 32; SOC 2 CC7.2; ISO 27001-aligned
    tenant separation and financial-authority containment.

SECURITY / PRIVACY POSTURE:
    Synthetic tenant, invoice, payment, and opaque identifiers only.

TENANT BOUNDARY:
    Every persisted test record is tenant-scoped and no cross-tenant inference
    is permitted.

AUTHORITY BOUNDARY:
    Certification only. This file owns no commercial, authorization, provider,
    financial execution, or settlement authority.

FINANCIAL AUTHORITY BOUNDARY:
    Kennel EOS remains the exclusive financial execution authority.

REAL-WORLD CERTIFICATION:
    Uses only the governed wilsyVendorCertRS replica set on 127.0.0.1:27027.
"""

from __future__ import annotations

import importlib
import os
from pathlib import Path
import sys
import types
from typing import Any, Iterator
import uuid

from pymongo import MongoClient
import pytest


TEST_VERSION = (
    "v1.0.0-BILLING-FINANCIAL-TRUTH-FIREWALL-REAL-MONGO-CERT"
)
EXPECTED_PRODUCTION_VERSION = (
    "v1.1.0-FINANCIAL-TRUTH-FIREWALL"
)
EXPECTED_URI = (
    "mongodb://127.0.0.1:27027/?replicaSet=wilsyVendorCertRS"
)

PRODUCTION_PATH = Path(
    "tools/eos/saas/billing/billing_registry.py"
)


@pytest.fixture(scope="module")
def billing_context() -> Iterator[tuple[Any, Any, Any]]:
    """Load BillingRegistry against one isolated governed real-Mongo database."""
    uri = os.environ.get("TEST_VENDOR_MONGO_URI")

    assert uri == EXPECTED_URI

    client: Any = MongoClient(
        uri,
        tz_aware=True,
        serverSelectionTimeoutMS=5000,
        connectTimeoutMS=5000,
    )

    client.admin.command("ping")

    database = client[
        f"wilsy_r3b1_billing_firewall_{uuid.uuid4().hex}"
    ]

    kernel_name = "tools.eos.kernel.db"
    registry_name = "tools.eos.saas.billing.billing_registry"

    previous_kernel = sys.modules.get(kernel_name)
    previous_registry = sys.modules.pop(
        registry_name,
        None,
    )

    kernel_stub = types.ModuleType(kernel_name)

    setattr(
        kernel_stub,
        "get_database",
        lambda: database,
    )
    setattr(
        kernel_stub,
        "get_client",
        lambda: client,
    )
    setattr(
        kernel_stub,
        "is_db_ready",
        lambda: True,
    )
    setattr(
        kernel_stub,
        "connect_db",
        lambda *args, **kwargs: (
            True,
            "governed real-Mongo certificate",
        ),
    )

    sys.modules[kernel_name] = kernel_stub

    try:
        billing: Any = importlib.import_module(
            registry_name
        )

        yield billing, database, client

    finally:
        sys.modules.pop(
            registry_name,
            None,
        )

        if previous_registry is not None:
            sys.modules[
                registry_name
            ] = previous_registry

        if previous_kernel is None:
            sys.modules.pop(
                kernel_name,
                None,
            )
        else:
            sys.modules[
                kernel_name
            ] = previous_kernel

        client.drop_database(database.name)
        client.close()


def test_version_and_structural_authority_contract() -> None:
    """Production runtime/header/seal must advertise the firewall exactly."""
    source = PRODUCTION_PATH.read_text(
        encoding="utf-8"
    )

    assert TEST_VERSION == (
        "v1.0.0-BILLING-FINANCIAL-TRUTH-FIREWALL-REAL-MONGO-CERT"
    )

    assert (
        f'VERSION = "{EXPECTED_PRODUCTION_VERSION}"'
        in source
    )

    assert (
        f"# VERSION: {EXPECTED_PRODUCTION_VERSION}"
        in source
    )

    for token in (
        "ABSOLUTE CANONICAL PATH:",
        "TENANT BOUNDARY:",
        "AUTHORITY BOUNDARY:",
        "FINANCIAL AUTHORITY BOUNDARY:",
        "BILLING_EXECUTION_TRUTH_REQUIRES_KENNEL",
        "BILLING_REFUND_REQUIRES_KENNEL_EXECUTION",
        "BILLING_SETTLEMENT_TRUTH_REQUIRES_KENNEL",
        "BILLING_PAID_STATE_REQUIRES_KENNEL_SETTLEMENT_EVIDENCE",
        "# END OF WILSY OS SOVEREIGN ARTIFACT",
    ):
        assert token in source

    upper = source.upper()

    assert "TODO" not in upper
    assert "FIXME" not in upper


def test_pending_collection_evidence_is_still_persistable(
    billing_context: tuple[Any, Any, Any],
) -> None:
    """Billing may persist PENDING evidence without claiming execution."""
    billing, database, _client = billing_context

    registry = billing.BillingRegistry()

    payment = registry.create_payment(
        invoice_id="INVOICE-R3B1-001",
        tenant_id="TENANT-R3B1",
        amount=125.50,
        currency="ZAR",
        method="manual",
        external_reference="OPAQUE-COLLECTION-REF-R3B1",
        idempotency_key="R3B1-PENDING-CREATE",
        performed_by="R3B1-CERT",
    )

    assert payment.status is billing.PaymentStatus.PENDING

    persisted = database["payments"].find_one(
        {
            "tenant_id": "TENANT-R3B1",
            "payment_id": payment.payment_id,
        }
    )

    assert persisted is not None
    assert persisted["status"] == "pending"
    assert persisted.get("paid_at") is None
    assert persisted.get("paidAt") is None


@pytest.mark.parametrize(
    "forbidden_status",
    (
        "succeeded",
        "failed",
        "refunded",
        "partially_refunded",
    ),
)
def test_direct_payment_execution_truth_always_fails_closed(
    billing_context: tuple[Any, Any, Any],
    forbidden_status: str,
) -> None:
    """No direct BillingRegistry status mutation may create Kennel truth."""
    billing, database, _client = billing_context

    registry = billing.BillingRegistry()

    payment = registry.create_payment(
        invoice_id=f"INV-{forbidden_status}",
        tenant_id="TENANT-R3B1",
        amount=25.00,
        currency="ZAR",
        idempotency_key=f"R3B1-{forbidden_status}",
        performed_by="R3B1-CERT",
    )

    with pytest.raises(
        billing.BillingFinancialTruthAuthorityError,
        match="^BILLING_EXECUTION_TRUTH_REQUIRES_KENNEL$",
    ):
        registry.update_payment_status(
            "TENANT-R3B1",
            payment.payment_id,
            forbidden_status,
            "R3B1-CERT",
        )

    persisted = database["payments"].find_one(
        {
            "tenant_id": "TENANT-R3B1",
            "payment_id": payment.payment_id,
        }
    )

    assert persisted is not None
    assert persisted["status"] == "pending"
    assert persisted.get("paid_at") is None
    assert persisted.get("paidAt") is None


def test_direct_refund_execution_always_fails_closed(
    billing_context: tuple[Any, Any, Any],
) -> None:
    """Refunds are new financial execution, never local billing state edits."""
    billing, database, _client = billing_context

    registry = billing.BillingRegistry()

    payment = registry.create_payment(
        invoice_id="INV-REFUND-R3B1",
        tenant_id="TENANT-R3B1",
        amount=75.00,
        currency="ZAR",
        idempotency_key="R3B1-REFUND-CREATE",
        performed_by="R3B1-CERT",
    )

    with pytest.raises(
        billing.BillingFinancialTruthAuthorityError,
        match="^BILLING_REFUND_REQUIRES_KENNEL_EXECUTION$",
    ):
        registry.refund_payment(
            "TENANT-R3B1",
            payment.payment_id,
            10.00,
            "R3B1-CERT",
        )

    persisted = database["payments"].find_one(
        {
            "tenant_id": "TENANT-R3B1",
            "payment_id": payment.payment_id,
        }
    )

    assert persisted is not None
    assert persisted["status"] == "pending"
    assert persisted.get("refund_amount", 0) in (
        0,
        0.0,
    )


@pytest.mark.parametrize(
    "updates",
    (
        {"status": "paid"},
        {"paid_at": "2026-09-04T10:00:00+00:00"},
        {"paidAt": "2026-09-04T10:00:00+00:00"},
        {"amount_paid": 10.00},
        {"amountPaid": 10.00},
        {"outstanding_amount": 0.00},
        {"outstandingAmount": 0.00},
    ),
)
@pytest.mark.parametrize(
    "method_name",
    (
        "update_platform_invoice",
        "update_client_invoice",
    ),
)
def test_generic_invoice_updates_cannot_manufacture_settlement(
    billing_context: tuple[Any, Any, Any],
    method_name: str,
    updates: dict[str, Any],
) -> None:
    """Settlement fields fail before lookup, proving a deep registry firewall."""
    billing, _database, _client = billing_context

    registry = billing.BillingRegistry()
    method = getattr(
        registry,
        method_name,
    )

    with pytest.raises(
        billing.BillingFinancialTruthAuthorityError
    ):
        method(
            "TENANT-R3B1",
            "INVOICE-DOES-NOT-NEED-TO-EXIST",
            updates,
            "R3B1-CERT",
        )


# =============================================================================
# WILSY OS SOVEREIGN ARTIFACT SEAL
# =============================================================================
# ARTIFACT: tests/integration/test_billing_registry_financial_truth_firewall_real_mongo.py
# VERSION: v1.0.0-BILLING-FINANCIAL-TRUTH-FIREWALL-REAL-MONGO-CERT
# AUTHORITY BOUNDARY:
#   Certification only; no commercial, release, provider, execution, or
#   settlement authority.
# TENANT POSTURE:
#   Governed isolated real-Mongo tenant fixtures only.
# FAIL-CLOSED POSTURE:
#   Direct execution/refund/settlement mutation must raise without persistence.
# FINANCIAL EXECUTION AUTHORITY:
#   Kennel EOS exclusively.
# END OF WILSY OS SOVEREIGN ARTIFACT
