"""WILSY OS — billing HTTP financial-truth firewall certificate.

TITLE:
    WAI-VAS23R3B2 Billing HTTP Financial-Truth Firewall Certificate

VERSION:
    v1.0.0-BILLING-HTTP-FINANCIAL-TRUTH-FIREWALL-CERT

AUTHORITY:
    Wilsy OS Core Governance

EPITOME:
    Runtime ASGI certification that caller-controlled Python billing routes
    cannot manufacture payment execution, refund execution, partial settlement,
    paid state, or paid-at settlement truth.

ABSOLUTE CANONICAL PATH:
    /Users/wilsonkhanyezi/legal-doc-system/tests/integration/test_billing_router_financial_truth_firewall_http.py

COLLABORATION / OWNERSHIP:
    Wilson Khanyezi / Wilsy OS Core Engineering

CERTIFICATION / UPDATE DATE:
    2026-09-04

CHANGELOG:
    v1.0.0 establishes the R3B2 HTTP transport-authority firewall certificate.

COMPLIANCE:
    POPIA section 19; GDPR Article 32; SOC 2 CC7.2; ISO 27001-aligned
    fail-closed financial authority containment.

SECURITY / PRIVACY POSTURE:
    Synthetic identifiers only. No external provider, credential, secret, real
    financial destination, or production customer data is used.

TENANT BOUNDARY:
    Synthetic X-Tenant-Id values are transport scope only and never membership
    or financial authorization evidence.

AUTHORITY BOUNDARY:
    Runtime HTTP transport certification only. No financial execution truth is
    created by this file.

FINANCIAL AUTHORITY BOUNDARY:
    Kennel EOS remains the exclusive financial execution authority.

CERTIFICATION CLASSIFICATION:
    HTTP TRANSPORT / AUTHORITY FIREWALL CERTIFICATE.

REAL-WORLD CERTIFICATION BOUNDARY:
    This certifies denial behavior at the Python HTTP surface. R3B1 separately
    certifies the underlying registry firewall against governed real Mongo.
"""

from __future__ import annotations

import importlib
from pathlib import Path
import sys
import types
from typing import Any, Iterator

from fastapi import FastAPI
from fastapi.testclient import TestClient
import pytest


TEST_VERSION = (
    "v1.0.0-BILLING-HTTP-FINANCIAL-TRUTH-FIREWALL-CERT"
)
EXPECTED_ROUTER_VERSION = (
    "v1.8.0-FINANCIAL-TRUTH-HTTP-FIREWALL"
)

ROUTER_PATH = Path(
    "tools/eos/api/billing_router.py"
)


class _ForbiddenRegistryInvocation(AssertionError):
    """Raised if a denied HTTP path reaches any persistence mutation."""


class _ExplodingBillingRegistry:
    """Any attribute access proves the transport firewall was bypassed."""

    def __getattr__(self, name: str) -> Any:
        raise _ForbiddenRegistryInvocation(
            f"denied route reached registry attribute: {name}"
        )


@pytest.fixture()
def client() -> Iterator[TestClient]:
    """Import the router with a side-effect-free BillingRegistry seam."""
    registry_module_name = (
        "tools.eos.saas.billing.billing_registry"
    )
    router_module_name = (
        "tools.eos.api.billing_router"
    )

    previous_registry = sys.modules.get(
        registry_module_name
    )
    previous_router = sys.modules.pop(
        router_module_name,
        None,
    )

    stub = types.ModuleType(
        registry_module_name
    )

    class BillingRegistry:
        pass

    registry = _ExplodingBillingRegistry()

    setattr(
        stub,
        "BillingRegistry",
        BillingRegistry,
    )
    setattr(
        stub,
        "get_billing_registry",
        lambda: registry,
    )
    setattr(
        stub,
        "db",
        {},
    )
    setattr(
        stub,
        "client",
        object(),
    )

    sys.modules[
        registry_module_name
    ] = stub

    try:
        module = importlib.import_module(
            router_module_name
        )

        assert module.VERSION == EXPECTED_ROUTER_VERSION

        app = FastAPI()
        app.include_router(
            module.router
        )

        app.dependency_overrides[
            module.get_tenant_id
        ] = lambda: "TENANT-R3B2"

        app.dependency_overrides[
            module.get_billing_registry
        ] = lambda: registry

        with TestClient(app) as test_client:
            yield test_client

    finally:
        sys.modules.pop(
            router_module_name,
            None,
        )

        if previous_router is not None:
            sys.modules[
                router_module_name
            ] = previous_router

        if previous_registry is None:
            sys.modules.pop(
                registry_module_name,
                None,
            )
        else:
            sys.modules[
                registry_module_name
            ] = previous_registry


def _assert_conflict(
    response: Any,
    code: str,
) -> None:
    assert response.status_code == 409
    assert response.json() == {
        "detail": code,
    }


def test_runtime_version_and_structure() -> None:
    source = ROUTER_PATH.read_text(
        encoding="utf-8"
    )

    assert TEST_VERSION == (
        "v1.0.0-BILLING-HTTP-FINANCIAL-TRUTH-FIREWALL-CERT"
    )

    assert (
        f'VERSION = "{EXPECTED_ROUTER_VERSION}"'
        in source
    )

    assert (
        f"# VERSION: {EXPECTED_ROUTER_VERSION}"
        in source
    )

    for token in (
        "ABSOLUTE CANONICAL PATH:",
        "TENANT BOUNDARY:",
        "AUTHORITY BOUNDARY:",
        "FINANCIAL AUTHORITY BOUNDARY:",
        "REQUEST != AUTHORIZATION != EXECUTION != SETTLEMENT.",
        "BILLING_EXECUTION_TRUTH_REQUIRES_KENNEL",
        "BILLING_REFUND_REQUIRES_KENNEL_EXECUTION",
        "BILLING_PARTIAL_SETTLEMENT_REQUIRES_KENNEL",
        "BILLING_PAID_STATE_REQUIRES_KENNEL_SETTLEMENT_EVIDENCE",
        "# END OF WILSY OS SOVEREIGN ARTIFACT",
    ):
        assert token in source

    upper = source.upper()

    assert "TODO" not in upper
    assert "FIXME" not in upper


def test_payment_status_route_fails_before_registry(
    client: TestClient,
) -> None:
    response = client.patch(
        "/billing/payments/PAY-R3B2/status",
        json={
            "status": "succeeded",
        },
    )

    _assert_conflict(
        response,
        "BILLING_EXECUTION_TRUTH_REQUIRES_KENNEL",
    )


def test_refund_route_fails_before_registry(
    client: TestClient,
) -> None:
    response = client.post(
        "/billing/payments/PAY-R3B2/refund",
        json={
            "refund_amount": 10.00,
        },
    )

    _assert_conflict(
        response,
        "BILLING_REFUND_REQUIRES_KENNEL_EXECUTION",
    )


@pytest.mark.parametrize(
    "path",
    (
        "/billing/invoices/INV-R3B2/partial-payment",
        "/billing/invoices/INV-R3B2/partialPayment",
        "/billing/invoice/INV-R3B2/partial-payment",
    ),
)
def test_partial_payment_aliases_fail_before_registry(
    client: TestClient,
    path: str,
) -> None:
    response = client.post(
        path,
        json={
            "amount": 10.00,
            "currency": "ZAR",
        },
    )

    _assert_conflict(
        response,
        "BILLING_PARTIAL_SETTLEMENT_REQUIRES_KENNEL",
    )


@pytest.mark.parametrize(
    "path",
    (
        "/billing/platform/invoices/INV-R3B2",
        "/billing/client/invoices/INV-R3B2",
    ),
)
@pytest.mark.parametrize(
    "payload,code",
    (
        (
            {"status": "paid"},
            "BILLING_PAID_STATE_REQUIRES_KENNEL_SETTLEMENT_EVIDENCE",
        ),
        (
            {
                "paid_at":
                    "2026-09-04T10:00:00+00:00"
            },
            "BILLING_SETTLEMENT_TRUTH_REQUIRES_KENNEL",
        ),
    ),
)
def test_generic_invoice_patch_cannot_create_settlement(
    client: TestClient,
    path: str,
    payload: dict[str, Any],
    code: str,
) -> None:
    response = client.patch(
        path,
        json=payload,
    )

    _assert_conflict(
        response,
        code,
    )


@pytest.mark.parametrize(
    "method",
    (
        "patch",
        "put",
        "post",
    ),
)
def test_unified_paid_status_aliases_fail_closed(
    client: TestClient,
    method: str,
) -> None:
    response = getattr(
        client,
        method,
    )(
        "/billing/invoices/INV-R3B2/status",
        json={
            "status": "paid",
        },
    )

    _assert_conflict(
        response,
        "BILLING_PAID_STATE_REQUIRES_KENNEL_SETTLEMENT_EVIDENCE",
    )



@pytest.mark.parametrize(
    "path",
    (
        "/billing/platform/invoices/INV-R3B2-RAW",
        "/billing/client/invoices/INV-R3B2-RAW",
    ),
)
@pytest.mark.parametrize(
    "payload",
    (
        {"paidAt": "caller-authored"},
        {"amount_paid": 10.00},
        {"amountPaid": 10.00},
        {"outstanding_amount": 0.00},
        {"outstandingAmount": 0.00},
    ),
)
def test_raw_settlement_aliases_fail_before_pydantic_projection(
    client: TestClient,
    path: str,
    payload: dict[str, Any],
) -> None:
    """Forbidden aliases must be classified as authority conflicts, not dropped."""
    response = client.patch(
        path,
        json=payload,
    )

    _assert_conflict(
        response,
        "BILLING_SETTLEMENT_TRUTH_REQUIRES_KENNEL",
    )

# =============================================================================
# WILSY OS SOVEREIGN ARTIFACT SEAL
# =============================================================================
# ARTIFACT: tests/integration/test_billing_router_financial_truth_firewall_http.py
# VERSION: v1.0.0-BILLING-HTTP-FINANCIAL-TRUTH-FIREWALL-CERT
# AUTHORITY BOUNDARY:
#   Python HTTP transport certification only.
# TENANT POSTURE:
#   Synthetic tenant scope only; no membership or authority inference.
# FAIL-CLOSED POSTURE:
#   All caller-controlled financial-truth paths return HTTP 409 before registry
#   persistence mutation.
# FINANCIAL EXECUTION AUTHORITY:
#   Kennel EOS exclusively.
# END OF WILSY OS SOVEREIGN ARTIFACT
