"""Real-Mongo HTTP certificate for Legal Storefront public-intent admission.

TITLE: Legal Storefront Public Intent HTTP Real-Mongo Certificate
VERSION: v1.0.0-L8-9C-LEGAL-STOREFRONT-PUBLIC-INTENT-HTTP-REAL-MONGO-CERT
AUTHORITY: Wilsy OS Core Governance / Python EOS Legal Operations
EPITOME: Exercise the real L8-9C anonymous HTTP router against a writable Mongo
         replica set and certify durable public-intent persistence, opaque
         request-density evidence, bounded authority rejection, durable blocked
         attempts and absence of tenant, AI and financial authority.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tests/integration/test_legal_storefront_public_intent_http_real_mongo.py
COLLABORATION / OWNERSHIP: L8-9A owns immutable intent semantics; L8-9B owns
                            durable intent persistence; L8-9C0 owns atomic
                            pre-tenant throttling; L8-9C owns HTTP composition.
                            This artifact owns only disposable host evidence.
CERTIFICATION / UPDATE DATE: 2026-10-12
CHANGELOG: 2026-10-12 v1.0.0-L8-9C-LEGAL-STOREFRONT-PUBLIC-INTENT-HTTP-REAL-MONGO-CERT
           establishes host-backed 202 persistence, exact privacy boundaries,
           authority-bearing input rejection, deterministic rate limiting,
           durable blocked counting and header-independent rate identity.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2; ISO 27001.
SECURITY / PRIVACY POSTURE: UUID-isolated disposable database; synthetic
                             acquisition metadata only. Rate rows persist only
                             opaque SHA3-512 subject identity, never raw email.
TENANT BOUNDARY: Explicitly pre-tenant; no tenant_id may be accepted, inferred,
                 indexed, persisted or returned.
AUTHORITY BOUNDARY: Runtime evidence only; successful admission establishes
                    public intent evidence, not identity, tenant, Legal
                    lifecycle, AI, subscription or entitlement authority.
AI AUTHORITY BOUNDARY: No WILSY AI gateway, model, entitlement or inference is
                       invoked by this certificate.
TRANSACTION BOUNDARY: L8-9C0 performs its certified atomic counter write;
                      L8-9B persistence executes in the HTTP-owned transaction.
FINANCIAL AUTHORITY BOUNDARY: None. Kennel EOS remains exclusive.
"""

from __future__ import annotations

from datetime import datetime, timezone
import hashlib
import os
import uuid
from typing import Any, Iterator

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from pymongo import MongoClient
from pymongo.collection import Collection
from pymongo.database import Database

import tools.eos.api.legal_storefront_public_intent_router as subject
from tools.eos.legal_operations.registry.legal_storefront_public_intent_registry import (
    COLLECTION as INTENT_COLLECTION,
    LegalStorefrontPublicIntentRegistry,
)
from tools.eos.legal_operations.service.legal_storefront_public_intent_rate_limit import (
    COLLECTION as RATE_COLLECTION,
    DEFAULT_MAX_REQUESTS,
    LegalStorefrontPublicIntentRateLimit,
)


MONGO_URI = os.getenv(
    "TEST_VENDOR_MONGO_URI",
    "mongodb://127.0.0.1:27027/?replicaSet=wilsyVendorCertRS",
)

FIXED_NOW = datetime(
    2026,
    10,
    12,
    14,
    45,
    0,
    tzinfo=timezone.utc,
)

BASE_PAYLOAD = {
    "organization_name": "Wilsy Legal Practice",
    "contact_email": "PUBLIC@EXAMPLE.COM",
    "industry": "Legal Services",
    "region": "ZA_GP",
}


@pytest.fixture
def mongo_context(
    monkeypatch: pytest.MonkeyPatch,
) -> Iterator[
    tuple[
        MongoClient[Any],
        Database[Any],
        Collection[Any],
        Collection[Any],
        TestClient,
    ]
]:
    """Provide one writable replica-set database and real standalone HTTP app."""
    client: MongoClient[Any] = MongoClient(
        MONGO_URI,
        serverSelectionTimeoutMS=5000,
        connectTimeoutMS=5000,
        socketTimeoutMS=5000,
    )

    hello = client.admin.command("hello")
    assert hello.get("setName") == "wilsyVendorCertRS"
    assert hello.get("isWritablePrimary") is True

    database_name = (
        "wilsy_l8_9c_http_"
        + uuid.uuid4().hex
    )
    database = client[database_name]

    intent_collection = database[INTENT_COLLECTION]
    rate_collection = database[RATE_COLLECTION]

    LegalStorefrontPublicIntentRegistry.ensure_indexes(
        intent_collection
    )
    LegalStorefrontPublicIntentRateLimit.ensure_indexes(
        rate_collection
    )

    monkeypatch.setattr(
        subject,
        "_handles",
        lambda: (client, database),
    )
    monkeypatch.setattr(
        subject,
        "_now",
        lambda: FIXED_NOW,
    )

    app = FastAPI()
    app.include_router(subject.router)
    http = TestClient(app)

    try:
        yield (
            client,
            database,
            intent_collection,
            rate_collection,
            http,
        )
    finally:
        client.drop_database(database_name)
        client.close()


def _forbidden_authority_fields() -> set[str]:
    return {
        "tenant_id",
        "tenantId",
        "principal_id",
        "principalId",
        "role",
        "permissions",
        "plan",
        "subscription_id",
        "subscriptionId",
        "entitlement_id",
        "entitlementId",
        "case_matter_id",
        "caseMatterId",
        "instruction_id",
        "instructionId",
        "invoice_id",
        "invoiceId",
        "payment_id",
        "paymentId",
        "settlement_id",
        "settlementId",
        "ai_prompt",
        "aiPrompt",
        "ai_result",
        "aiResult",
    }


def test_real_http_202_persists_intent_and_opaque_rate_evidence(
    mongo_context: tuple[
        MongoClient[Any],
        Database[Any],
        Collection[Any],
        Collection[Any],
        TestClient,
    ],
) -> None:
    """Prove one anonymous request durably creates bounded evidence only."""
    _, _, intents, rates, http = mongo_context

    response = http.post(
        "/legal-storefront/public-intents",
        json=BASE_PAYLOAD,
    )

    assert response.status_code == 202
    body = response.json()
    assert set(body) == {"status", "intentId"}
    assert body["status"] == "ACCEPTED"

    assert intents.count_documents({}) == 1
    assert rates.count_documents({}) == 1

    intent = intents.find_one({})
    rate = rates.find_one({})

    assert intent is not None
    assert rate is not None

    assert intent["intent_id"] == body["intentId"]
    assert intent["contact_email"] == "public@example.com"
    assert intent["organization_name"] == "Wilsy Legal Practice"
    assert intent["industry"] == "Legal Services"
    assert intent["region"] == "ZA_GP"

    expected_digest = hashlib.sha3_512(
        b"public@example.com"
    ).hexdigest()

    assert rate["subject_digest"] == expected_digest
    assert rate["count"] == 1

    serialized_rate = repr(rate).lower()
    assert "public@example.com" not in serialized_rate
    assert "PUBLIC@EXAMPLE.COM" not in repr(rate)

    forbidden = _forbidden_authority_fields()
    assert forbidden.isdisjoint(intent.keys())
    assert forbidden.isdisjoint(rate.keys())
    assert forbidden.isdisjoint(body.keys())


def test_real_authority_bearing_input_is_422_and_writes_nothing(
    mongo_context: tuple[
        MongoClient[Any],
        Database[Any],
        Collection[Any],
        Collection[Any],
        TestClient,
    ],
) -> None:
    """Prove pre-tenant HTTP validation rejects attempted tenant authority."""
    _, _, intents, rates, http = mongo_context

    response = http.post(
        "/legal-storefront/public-intents",
        json={
            **BASE_PAYLOAD,
            "tenant_id": "tenant-forbidden",
        },
    )

    assert response.status_code == 422
    assert intents.count_documents({}) == 0
    assert rates.count_documents({}) == 0


def test_real_rate_limit_blocks_after_exact_allowance_and_counts_block(
    mongo_context: tuple[
        MongoClient[Any],
        Database[Any],
        Collection[Any],
        Collection[Any],
        TestClient,
    ],
) -> None:
    """Prove blocked attempts remain durably counted and are not admitted."""
    _, _, intents, rates, http = mongo_context

    statuses: list[int] = []

    for sequence in range(DEFAULT_MAX_REQUESTS + 1):
        response = http.post(
            "/legal-storefront/public-intents",
            json={
                **BASE_PAYLOAD,
                "organization_name": (
                    f"Wilsy Legal Practice {sequence}"
                ),
            },
        )
        statuses.append(response.status_code)

    assert statuses[:-1] == [
        202
        for _ in range(DEFAULT_MAX_REQUESTS)
    ]
    assert statuses[-1] == 429

    assert intents.count_documents({}) == DEFAULT_MAX_REQUESTS
    assert rates.count_documents({}) == 1

    rate = rates.find_one({})
    assert rate is not None
    assert rate["count"] == DEFAULT_MAX_REQUESTS + 1


def test_real_rate_identity_ignores_untrusted_forwarding_headers(
    mongo_context: tuple[
        MongoClient[Any],
        Database[Any],
        Collection[Any],
        Collection[Any],
        TestClient,
    ],
) -> None:
    """Prove untrusted forwarding headers do not become rate authority."""
    _, _, intents, rates, http = mongo_context

    first = http.post(
        "/legal-storefront/public-intents",
        json=BASE_PAYLOAD,
        headers={
            "x-forwarded-for": "198.51.100.1",
            "forwarded": "for=198.51.100.1",
        },
    )
    second = http.post(
        "/legal-storefront/public-intents",
        json={
            **BASE_PAYLOAD,
            "organization_name": "Wilsy Legal Practice Two",
        },
        headers={
            "x-forwarded-for": "203.0.113.99",
            "forwarded": "for=203.0.113.99",
        },
    )

    assert first.status_code == 202
    assert second.status_code == 202

    assert intents.count_documents({}) == 2
    assert rates.count_documents({}) == 1

    rate = rates.find_one({})
    assert rate is not None
    assert rate["count"] == 2
    assert rate["subject_digest"] == hashlib.sha3_512(
        b"public@example.com"
    ).hexdigest()


def test_real_distinct_normalized_contacts_have_independent_buckets(
    mongo_context: tuple[
        MongoClient[Any],
        Database[Any],
        Collection[Any],
        Collection[Any],
        TestClient,
    ],
) -> None:
    """Prove separate normalized contact subjects receive separate buckets."""
    _, _, intents, rates, http = mongo_context

    first = http.post(
        "/legal-storefront/public-intents",
        json=BASE_PAYLOAD,
    )
    second = http.post(
        "/legal-storefront/public-intents",
        json={
            **BASE_PAYLOAD,
            "contact_email": "other@example.com",
        },
    )

    assert first.status_code == 202
    assert second.status_code == 202

    assert intents.count_documents({}) == 2
    assert rates.count_documents({}) == 2

    digests = {
        row["subject_digest"]
        for row in rates.find({})
    }

    assert digests == {
        hashlib.sha3_512(
            b"public@example.com"
        ).hexdigest(),
        hashlib.sha3_512(
            b"other@example.com"
        ).hexdigest(),
    }


def test_real_indexes_preserve_durable_intent_and_ephemeral_rate_contract(
    mongo_context: tuple[
        MongoClient[Any],
        Database[Any],
        Collection[Any],
        Collection[Any],
        TestClient,
    ],
) -> None:
    """Prove TTL exists only on ephemeral rate evidence, never public intent."""
    _, _, intents, rates, _ = mongo_context

    intent_indexes = {
        entry["name"]: entry
        for entry in intents.list_indexes()
    }
    rate_indexes = {
        entry["name"]: entry
        for entry in rates.list_indexes()
    }

    assert not any(
        "expireAfterSeconds" in entry
        for entry in intent_indexes.values()
    )

    ttl = [
        entry
        for entry in rate_indexes.values()
        if entry.get("expireAfterSeconds") == 0
    ]
    assert len(ttl) == 1


# ARTIFACT: test_legal_storefront_public_intent_http_real_mongo.py
# VERSION: v1.0.0-L8-9C-LEGAL-STOREFRONT-PUBLIC-INTENT-HTTP-REAL-MONGO-CERT
# AUTHORITY BOUNDARY: disposable host-backed HTTP evidence only
# TENANT POSTURE: explicitly pre-tenant and UUID-database isolated
# TRANSACTION POSTURE: HTTP-owned L8-9B transaction plus atomic L8-9C0 rate write
# PRIVACY POSTURE: rate storage contains only opaque SHA3-512 contact subject
# AI POSTURE: no WILSY AI invocation, inference, entitlement or authority
# FAIL-CLOSED POSTURE: malformed/authority-bearing/rate-blocked requests never fabricate admission
# FINANCIAL EXECUTION AUTHORITY: none; Kennel EOS remains exclusive
# END OF WILSY OS SOVEREIGN ARTIFACT
