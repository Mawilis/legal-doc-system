"""Real-Mongo certificate for the Legal Storefront public-intent registry.

TITLE: Legal Storefront Public Intent Registry Real-Mongo Certificate
VERSION: v1.0.0-L8-9B-LEGAL-STOREFRONT-PUBLIC-INTENT-REGISTRY-REAL-MONGO-CERT
AUTHORITY: Wilsy OS Core Governance / Python EOS Legal Operations
EPITOME: Prove physical unique indexes, no-TTL metadata, transactional
         durability, exact replay, rollback, strict corruption rejection,
         physical uniqueness and downstream-authority exclusion for immutable
         pre-tenant Storefront intent evidence on a writable Mongo replica set.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tests/integration/test_legal_storefront_public_intent_registry_real_mongo.py
COLLABORATION / OWNERSHIP: Certificate only. L8-9A owns immutable intent
                            semantics; L8-9B owns append-only persistence.
                            Identity verification, tenant genesis, retention,
                            deletion, HTTP admission and downstream workflows
                            remain separate owners.
CERTIFICATION / UPDATE DATE: 2026-10-12
CHANGELOG: 2026-10-12 v1.0.0-L8-9B-LEGAL-STOREFRONT-PUBLIC-INTENT-REGISTRY-REAL-MONGO-CERT
           establishes physical index/no-TTL proof, commit/replay/read,
           rollback atomicity, uniqueness, persisted corruption rejection and
           durable-row authority exclusion against real MongoDB.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2; ISO 27001.
SECURITY / PRIVACY POSTURE: UUID-isolated database and synthetic Storefront
                             metadata only; no live credentials or customers.
TENANT BOUNDARY: Pre-tenant by definition. The certificate proves tenant_id is
                 neither indexed nor stored and persistence creates no tenant.
AUTHORITY BOUNDARY: Persistence evidence only; no identity, tenant genesis,
                    role, subscription, entitlement, Legal lifecycle, billing,
                    payment, settlement, deletion or retention authority.
TRANSACTION BOUNDARY: Certificate owns start/commit/abort. Registry receives
                      one already-active caller transaction only.
RETENTION BOUNDARY: Physical Mongo metadata must contain no TTL index.
FINANCIAL AUTHORITY BOUNDARY: Kennel EOS remains exclusive.
FAIL-CLOSED DECLARATION: Mongo/runtime, index drift, rollback, uniqueness,
                         replay, persisted corruption or authority leakage fails
                         this certificate; unavailable infrastructure is not PASS.
"""

from __future__ import annotations

from copy import deepcopy
from datetime import datetime, timezone
import os
from typing import Any, Iterator
from uuid import uuid4

import pytest
from pymongo import MongoClient
from pymongo.errors import DuplicateKeyError
from pymongo.read_concern import ReadConcern
from pymongo.write_concern import WriteConcern

from tools.eos.legal_operations.domain.legal_storefront_public_intent import (
    create_legal_storefront_public_intent,
)
from tools.eos.legal_operations.registry.legal_storefront_public_intent_registry import (
    COLLECTION,
    INDEX_FINGERPRINT,
    INDEX_INTENT_ID,
    LegalStorefrontPublicIntentRegistry,
    LegalStorefrontPublicIntentRegistryError,
    ensure_indexes,
)


VERSION = (
    "v1.0.0-L8-9B-LEGAL-STOREFRONT-PUBLIC-INTENT-REGISTRY-REAL-MONGO-CERT"
)

MONGO_URI = os.environ.get(
    "TEST_VENDOR_MONGO_URI",
    "mongodb://127.0.0.1:27027/?replicaSet=wilsyVendorCertRS",
)

BASE = datetime(2026, 10, 12, 9, 30, 0, 123456, tzinfo=timezone.utc)


@pytest.fixture()
def mongo_context() -> Iterator[tuple[MongoClient[Any], Any, Any]]:
    """Yield one UUID-isolated majority/journal Storefront-intent collection."""
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

    database = client[f"wilsy_l8_9b_storefront_{uuid4().hex}"]
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


def _intent(
    *,
    intent_id: str = "legal-storefront-intent:real-1",
    organization_name: str = "Khanyezi Legal",
):
    return create_legal_storefront_public_intent(
        intent_id=intent_id,
        organization_name=organization_name,
        contact_email="intake@example.org",
        industry="Legal Services",
        region="ZA",
        submitted_at=BASE,
    )


def test_real_indexes_are_exact_unique_pretenant_and_have_no_ttl(
    mongo_context: tuple[MongoClient[Any], Any, Any],
) -> None:
    _, _, collection = mongo_context

    indexes = {
        entry["name"]: entry
        for entry in collection.list_indexes()
    }

    by_intent = indexes[INDEX_INTENT_ID]
    by_fingerprint = indexes[INDEX_FINGERPRINT]

    assert dict(by_intent["key"]) == {"intent_id": 1}
    assert by_intent["unique"] is True

    assert dict(by_fingerprint["key"]) == {"fingerprint": 1}
    assert by_fingerprint["unique"] is True

    assert all(
        "expireAfterSeconds" not in entry
        for entry in indexes.values()
    )

    indexed_fields = {
        field
        for entry in indexes.values()
        for field in dict(entry["key"])
    }
    assert "tenant_id" not in indexed_fields
    assert "contact_email" not in indexed_fields
    assert "organization_name" not in indexed_fields


def test_real_transaction_create_replay_and_exact_read(
    mongo_context: tuple[MongoClient[Any], Any, Any],
) -> None:
    client, _, collection = mongo_context
    registry = LegalStorefrontPublicIntentRegistry(collection)
    value = _intent()

    with client.start_session() as session:
        session.start_transaction(
            read_concern=ReadConcern("snapshot"),
            write_concern=WriteConcern("majority"),
        )

        first = registry.create_or_replay(value, session=session)
        replay = registry.create_or_replay(value, session=session)
        exact = registry.get_by_intent_id(
            intent_id=value.intent_id,
            session=session,
        )

        session.commit_transaction()

    assert first == value
    assert replay == value
    assert exact == value
    assert collection.count_documents(
        {"intent_id": value.intent_id}
    ) == 1


def test_real_missing_intent_is_canonical_absence(
    mongo_context: tuple[MongoClient[Any], Any, Any],
) -> None:
    client, _, collection = mongo_context
    registry = LegalStorefrontPublicIntentRegistry(collection)

    with client.start_session() as session:
        session.start_transaction(
            read_concern=ReadConcern("snapshot"),
            write_concern=WriteConcern("majority"),
        )

        result = registry.get_by_intent_id(
            intent_id="legal-storefront-intent:missing",
            session=session,
        )

        session.commit_transaction()

    assert result is None


def test_real_abort_leaves_zero_durable_intents(
    mongo_context: tuple[MongoClient[Any], Any, Any],
) -> None:
    client, _, collection = mongo_context
    registry = LegalStorefrontPublicIntentRegistry(collection)
    value = _intent()

    with client.start_session() as session:
        session.start_transaction(
            read_concern=ReadConcern("snapshot"),
            write_concern=WriteConcern("majority"),
        )

        registry.create_or_replay(value, session=session)

        assert collection.count_documents(
            {"intent_id": value.intent_id},
            session=session,
        ) == 1

        session.abort_transaction()

    assert collection.count_documents({}) == 0


def test_real_physical_intent_identity_uniqueness(
    mongo_context: tuple[MongoClient[Any], Any, Any],
) -> None:
    _, _, collection = mongo_context

    first = _intent()
    second = _intent(
        intent_id="legal-storefront-intent:real-2",
        organization_name="Other Legal",
    )

    collection.insert_one(first.to_dict())

    duplicate = second.to_dict()
    duplicate["intent_id"] = first.intent_id

    with pytest.raises(DuplicateKeyError):
        collection.insert_one(duplicate)

    assert collection.count_documents(
        {"intent_id": first.intent_id}
    ) == 1


def test_real_physical_fingerprint_uniqueness(
    mongo_context: tuple[MongoClient[Any], Any, Any],
) -> None:
    _, _, collection = mongo_context

    first = _intent()
    second = _intent(
        intent_id="legal-storefront-intent:real-2",
        organization_name="Other Legal",
    )

    collection.insert_one(first.to_dict())

    duplicate = second.to_dict()
    duplicate["fingerprint"] = first.fingerprint

    with pytest.raises(DuplicateKeyError):
        collection.insert_one(duplicate)

    assert collection.count_documents(
        {"fingerprint": first.fingerprint}
    ) == 1


def test_real_persisted_corruption_and_authority_injection_reject(
    mongo_context: tuple[MongoClient[Any], Any, Any],
) -> None:
    client, _, collection = mongo_context
    registry = LegalStorefrontPublicIntentRegistry(collection)
    value = _intent()

    with client.start_session() as session:
        session.start_transaction(
            read_concern=ReadConcern("snapshot"),
            write_concern=WriteConcern("majority"),
        )
        registry.create_or_replay(value, session=session)
        session.commit_transaction()

    pristine = collection.find_one(
        {"intent_id": value.intent_id}
    )
    assert pristine is not None

    corrupted = deepcopy(pristine)
    corrupted["tenant_id"] = "forbidden-tenant"
    collection.replace_one(
        {"_id": pristine["_id"]},
        corrupted,
    )

    with client.start_session() as session:
        session.start_transaction(
            read_concern=ReadConcern("snapshot"),
            write_concern=WriteConcern("majority"),
        )

        with pytest.raises(
            LegalStorefrontPublicIntentRegistryError,
            match="L8_9B_CORRUPT_INTENT",
        ):
            registry.get_by_intent_id(
                intent_id=value.intent_id,
                session=session,
            )

        session.abort_transaction()


def test_real_durable_row_contains_no_downstream_authority_fields(
    mongo_context: tuple[MongoClient[Any], Any, Any],
) -> None:
    client, _, collection = mongo_context
    registry = LegalStorefrontPublicIntentRegistry(collection)
    value = _intent()

    with client.start_session() as session:
        session.start_transaction(
            read_concern=ReadConcern("snapshot"),
            write_concern=WriteConcern("majority"),
        )
        registry.create_or_replay(value, session=session)
        session.commit_transaction()

    row = collection.find_one(
        {"intent_id": value.intent_id}
    )
    assert row is not None

    forbidden = {
        "tenant_id",
        "principal_id",
        "identity_id",
        "password",
        "credential",
        "role",
        "role_id",
        "plan",
        "tier",
        "subscription",
        "subscription_id",
        "entitlement",
        "entitlement_id",
        "api_key",
        "instruction_id",
        "case_matter_id",
        "document_id",
        "invoice_id",
        "payment_id",
        "settlement_id",
        "expires_at",
        "deleted_at",
    }

    assert not forbidden.intersection(row)


# ARTIFACT: test_legal_storefront_public_intent_registry_real_mongo.py
# VERSION: v1.0.0-L8-9B-LEGAL-STOREFRONT-PUBLIC-INTENT-REGISTRY-REAL-MONGO-CERT
# AUTHORITY BOUNDARY: real-Mongo append-only pre-tenant public-intent persistence certificate only
# TENANT POSTURE: tenant_id is neither indexed nor persisted; durability creates no tenant scope
# TRANSACTION POSTURE: certificate owns start/commit/abort; registry receives only active caller transactions
# RETENTION POSTURE: physical Mongo metadata certifies no TTL deletion index
# PUBLIC LOOKUP POSTURE: no contact, organization or tenant lookup index is present
# FAIL-CLOSED POSTURE: infrastructure, index, rollback, corruption and uniqueness failures fail certification
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively
# END OF WILSY OS SOVEREIGN ARTIFACT
