"""Real-Mongo certificate for Legal Storefront public-intent rate limiting.

TITLE: Legal Storefront Public Intent Rate Limit Real-Mongo Certificate
VERSION: v1.0.0-L8-9C0-LEGAL-STOREFRONT-PUBLIC-INTENT-RATE-LIMIT-REAL-MONGO-CERT
AUTHORITY: Wilsy OS Core Governance / Python EOS Legal Operations
EPITOME: Certify physical lookup/TTL indexes, atomic fixed-window counting,
         durable throttling, new-window separation, BSON UTC round-trip,
         pre-tenant privacy posture and corruption rejection against a writable
         MongoDB replica set.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tests/integration/test_legal_storefront_public_intent_rate_limit_real_mongo.py
COLLABORATION / OWNERSHIP: Certificate only. L8-9C0 owns request-density
                            capability; L8-9A owns public-intent semantics;
                            L8-9B owns durable public-intent persistence.
CERTIFICATION / UPDATE DATE: 2026-10-12
CHANGELOG: 2026-10-12 v1.0.0-L8-9C0-LEGAL-STOREFRONT-PUBLIC-INTENT-RATE-LIMIT-REAL-MONGO-CERT
           establishes physical Mongo index metadata, same-window atomic count,
           durable rate rejection, new-window bucket separation, UTC hydration,
           authority-field exclusion and persisted-state corruption rejection.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2; ISO 27001.
SECURITY / PRIVACY POSTURE: UUID-isolated database and synthetic SHA3-512
                             subject digests only; no live contact or IP data.
TENANT BOUNDARY: Pre-tenant. tenant_id is neither indexed nor persisted.
AUTHORITY BOUNDARY: Rate-density certificate only; allowance is not public
                    intent admission, identity, tenant genesis, Legal lifecycle,
                    subscription, entitlement or financial authority.
TRANSACTION BOUNDARY: Gate uses one atomic find_one_and_update per request and
                      owns no caller transaction.
RETENTION BOUNDARY: TTL applies only to ephemeral rate-limit buckets.
FINANCIAL AUTHORITY BOUNDARY: Kennel EOS remains exclusive.
FAIL-CLOSED DECLARATION: Mongo/runtime, physical-index, throttling, UTC,
                         persisted-state or privacy-boundary failure fails the
                         certificate; unavailable infrastructure is not PASS.
"""

from __future__ import annotations

from datetime import datetime, timedelta, timezone
import hashlib
import os
from typing import Any, Iterator
from uuid import uuid4

import pytest
from pymongo import MongoClient
from pymongo.read_concern import ReadConcern
from pymongo.write_concern import WriteConcern

from tools.eos.legal_operations.service.legal_storefront_public_intent_rate_limit import (
    COLLECTION,
    DEFAULT_NAMESPACE,
    DEFAULT_WINDOW,
    INDEX_LOOKUP,
    INDEX_TTL,
    LegalStorefrontPublicIntentRateLimit,
    LegalStorefrontPublicIntentRateLimitDependencyError,
    LegalStorefrontPublicIntentRateLimitedError,
    ensure_indexes,
)


VERSION = (
    "v1.0.0-L8-9C0-LEGAL-STOREFRONT-PUBLIC-INTENT-RATE-LIMIT-REAL-MONGO-CERT"
)

MONGO_URI = os.environ.get(
    "TEST_VENDOR_MONGO_URI",
    "mongodb://127.0.0.1:27027/?replicaSet=wilsyVendorCertRS",
)

BASE = datetime(2026, 10, 12, 12, 0, 0, tzinfo=timezone.utc)
DIGEST = hashlib.sha3_512(b"l8-9c0-real-subject").hexdigest()


@pytest.fixture()
def mongo_context() -> Iterator[tuple[MongoClient[Any], Any, Any]]:
    """Yield one UUID-isolated majority/journal rate-limit collection."""
    client: MongoClient[Any] = MongoClient(
        MONGO_URI,
        serverSelectionTimeoutMS=5000,
        connectTimeoutMS=5000,
        socketTimeoutMS=10000,
        retryWrites=True,
    )

    client.admin.command("ping")
    hello = client.admin.command("hello")
    assert hello.get("setName") == "wilsyVendorCertRS"
    assert hello.get("isWritablePrimary", hello.get("ismaster")) is True

    database = client[f"wilsy_l8_9c0_rate_{uuid4().hex}"]
    collection = database.get_collection(
        COLLECTION,
        write_concern=WriteConcern(w="majority", j=True),
        read_concern=ReadConcern("majority"),
    )
    ensure_indexes(collection)

    try:
        yield client, database, collection
    finally:
        client.drop_database(database.name)
        client.close()


def test_real_indexes_are_exact_pretenant_and_ttl_scoped(
    mongo_context: tuple[MongoClient[Any], Any, Any],
) -> None:
    _, _, collection = mongo_context

    indexes = {
        entry["name"]: entry
        for entry in collection.list_indexes()
    }

    lookup = indexes[INDEX_LOOKUP]
    ttl = indexes[INDEX_TTL]

    assert dict(lookup["key"]) == {
        "namespace": 1,
        "subject_digest": 1,
        "bucket_start": 1,
    }
    assert lookup.get("unique") is not True

    assert dict(ttl["key"]) == {"expires_at": 1}
    assert ttl["expireAfterSeconds"] == 0

    indexed_fields = {
        field
        for entry in indexes.values()
        for field in dict(entry["key"])
    }

    assert "tenant_id" not in indexed_fields
    assert "email" not in indexed_fields
    assert "contact_email" not in indexed_fields
    assert "ip" not in indexed_fields
    assert "ip_address" not in indexed_fields


def test_real_same_window_count_is_atomic_and_durable(
    mongo_context: tuple[MongoClient[Any], Any, Any],
) -> None:
    _, _, collection = mongo_context
    gate = LegalStorefrontPublicIntentRateLimit(
        collection,
        max_requests=5,
    )

    for second in range(5):
        gate.require_allowed(
            subject_digest=DIGEST,
            observed_at=BASE + timedelta(seconds=second),
        )

    row = collection.find_one(
        {
            "namespace": DEFAULT_NAMESPACE,
            "subject_digest": DIGEST,
        }
    )
    assert row is not None
    assert row["count"] == 5
    assert row["subject_digest"] == DIGEST
    assert row["bucket_start"].replace(
        tzinfo=timezone.utc
    ) == BASE
    assert row["expires_at"].replace(
        tzinfo=timezone.utc
    ) == BASE + DEFAULT_WINDOW + timedelta(minutes=1)


def test_real_request_beyond_limit_is_rejected_and_counted(
    mongo_context: tuple[MongoClient[Any], Any, Any],
) -> None:
    _, _, collection = mongo_context
    gate = LegalStorefrontPublicIntentRateLimit(
        collection,
        max_requests=2,
    )

    gate.require_allowed(
        subject_digest=DIGEST,
        observed_at=BASE,
    )
    gate.require_allowed(
        subject_digest=DIGEST,
        observed_at=BASE + timedelta(seconds=1),
    )

    with pytest.raises(
        LegalStorefrontPublicIntentRateLimitedError,
        match="L8_9C0_RATE_LIMITED",
    ):
        gate.require_allowed(
            subject_digest=DIGEST,
            observed_at=BASE + timedelta(seconds=2),
        )

    row = collection.find_one(
        {"subject_digest": DIGEST}
    )
    assert row is not None
    assert row["count"] == 3


def test_real_new_fixed_window_creates_independent_bucket(
    mongo_context: tuple[MongoClient[Any], Any, Any],
) -> None:
    _, _, collection = mongo_context
    gate = LegalStorefrontPublicIntentRateLimit(collection)

    gate.require_allowed(
        subject_digest=DIGEST,
        observed_at=BASE,
    )
    gate.require_allowed(
        subject_digest=DIGEST,
        observed_at=BASE + DEFAULT_WINDOW,
    )

    rows = list(
        collection.find(
            {"subject_digest": DIGEST}
        ).sort("bucket_start", 1)
    )

    assert len(rows) == 2
    assert [row["count"] for row in rows] == [1, 1]


def test_real_different_subjects_do_not_share_bucket(
    mongo_context: tuple[MongoClient[Any], Any, Any],
) -> None:
    _, _, collection = mongo_context
    gate = LegalStorefrontPublicIntentRateLimit(collection)

    other_digest = hashlib.sha3_512(
        b"l8-9c0-other-real-subject"
    ).hexdigest()

    gate.require_allowed(
        subject_digest=DIGEST,
        observed_at=BASE,
    )
    gate.require_allowed(
        subject_digest=other_digest,
        observed_at=BASE,
    )

    assert collection.count_documents({}) == 2


def test_real_durable_bucket_contains_no_raw_or_downstream_authority_fields(
    mongo_context: tuple[MongoClient[Any], Any, Any],
) -> None:
    _, _, collection = mongo_context
    gate = LegalStorefrontPublicIntentRateLimit(collection)

    gate.require_allowed(
        subject_digest=DIGEST,
        observed_at=BASE,
    )

    row = collection.find_one(
        {"subject_digest": DIGEST}
    )
    assert row is not None

    forbidden = {
        "tenant_id",
        "email",
        "contact_email",
        "ip",
        "ip_address",
        "host",
        "hostname",
        "principal_id",
        "identity_id",
        "intent_id",
        "organization_name",
        "plan",
        "tier",
        "subscription_id",
        "entitlement_id",
        "instruction_id",
        "case_matter_id",
        "document_id",
        "invoice_id",
        "payment_id",
        "settlement_id",
    }

    assert not forbidden.intersection(row)


def test_real_bson_utc_round_trip_remains_valid(
    mongo_context: tuple[MongoClient[Any], Any, Any],
) -> None:
    _, _, collection = mongo_context
    gate = LegalStorefrontPublicIntentRateLimit(collection)

    gate.require_allowed(
        subject_digest=DIGEST,
        observed_at=BASE,
    )

    gate.require_allowed(
        subject_digest=DIGEST,
        observed_at=BASE + timedelta(seconds=1),
    )

    row = collection.find_one(
        {"subject_digest": DIGEST}
    )
    assert row is not None
    assert row["count"] == 2


def test_real_persisted_state_corruption_rejects(
    mongo_context: tuple[MongoClient[Any], Any, Any],
) -> None:
    _, _, collection = mongo_context
    gate = LegalStorefrontPublicIntentRateLimit(collection)

    gate.require_allowed(
        subject_digest=DIGEST,
        observed_at=BASE,
    )

    row = collection.find_one(
        {"subject_digest": DIGEST}
    )
    assert row is not None

    collection.update_one(
        {"_id": row["_id"]},
        {
            "$set": {
                "namespace": "corrupt-namespace",
            }
        },
    )

    with pytest.raises(
        LegalStorefrontPublicIntentRateLimitDependencyError,
        match="L8_9C0_STATE_MISMATCH",
    ):
        gate.require_allowed(
            subject_digest=DIGEST,
            observed_at=BASE + timedelta(seconds=2),
        )


# ARTIFACT: test_legal_storefront_public_intent_rate_limit_real_mongo.py
# VERSION: v1.0.0-L8-9C0-LEGAL-STOREFRONT-PUBLIC-INTENT-RATE-LIMIT-REAL-MONGO-CERT
# AUTHORITY BOUNDARY: real-Mongo request-density certificate only; no Storefront admission, identity, tenant, Legal lifecycle or financial authority
# TENANT POSTURE: tenant_id is neither indexed nor persisted
# TRANSACTION POSTURE: one atomic Mongo find/update per request; no caller transaction
# RETENTION POSTURE: physical TTL index applies only to ephemeral rate buckets
# PRIVACY POSTURE: only opaque SHA3-512 subject digest is durable
# FAIL-CLOSED POSTURE: Mongo/index/throttling/UTC/state-integrity failure fails certification
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively
# END OF WILSY OS SOVEREIGN ARTIFACT
