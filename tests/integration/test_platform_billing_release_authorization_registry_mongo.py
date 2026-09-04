"""WILSY OS governed real-Mongo R3C2 certificate.
TITLE: Platform Billing Release Authorization Registry Mongo Certificate
VERSION: v1.1.0-PLATFORM-BILLING-RELEASE-AUTHORIZATION-REGISTRY-MONGO-CERT
AUTHORITY: Wilsy OS Core Governance
EPITOME: Certify durable tenant-scoped immutable release evidence on actual MongoDB.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tests/integration/test_platform_billing_release_authorization_registry_mongo.py
COLLABORATION / OWNERSHIP: Python EOS Core Engineering
CERTIFICATION / UPDATE DATE: 2026-09-04
CHANGELOG: v1.1.0 expands replay, conflict, corruption, index, and session coverage.
COMPLIANCE: POPIA §19 | GDPR Article 32 | SOC2 CC7.2
SECURITY / PRIVACY: UUID-isolated disposable database; no provider or payment data.
TENANT BOUNDARY: Every lookup and idempotency identity is tenant-scoped.
AUTHORITY BOUNDARY: Persistence evidence only; no execution, settlement, or approval grant.
FINANCIAL AUTHORITY BOUNDARY: Kennel EOS exclusively owns financial execution and settlement.
"""
from __future__ import annotations

import os
from datetime import datetime, timezone
from typing import Any
from uuid import uuid4

import pytest
from pymongo import MongoClient
from pymongo.client_session import ClientSession

from tools.eos.saas.billing.platform_billing_release_authorization_registry import (
    PlatformBillingReleaseAuthorizationIdempotencyConflictError,
    PlatformBillingReleaseAuthorizationIdentityConflictError,
    PlatformBillingReleaseAuthorizationNotFoundError,
    PlatformBillingReleaseAuthorizationPersistedRecordInvalidError,
    PlatformBillingReleaseAuthorizationRegistry,
)
from tools.eos.saas.domain.platform_billing_release_authorization import PlatformBillingReleaseAuthorization

MONGO_URI = os.getenv("TEST_VENDOR_MONGO_URI", "mongodb://127.0.0.1:27027/?replicaSet=wilsyVendorCertRS")

def _authorization(tenant: str = "tenant-a", *, key: str = "idem-a", release_id: str = "release-a", destination: str = "DEST-A") -> PlatformBillingReleaseAuthorization:
    return PlatformBillingReleaseAuthorization(tenant_id=tenant, release_authorization_id=release_id, platform_invoice_id="invoice-a", platform_invoice_evidence_fingerprint="a" * 128, authorization_evidence_reference="evidence-a", authorization_evidence_fingerprint="b" * 128, authorized_amount_minor=100, currency="ZAR", payment_destination_reference=destination, idempotency_key=key, authorized_by_principal_id="principal-a", authorization_basis_reference="basis-a", authorized_at=datetime(2026, 1, 1, tzinfo=timezone.utc), created_at=datetime(2026, 1, 1, tzinfo=timezone.utc))

def _semantic(document: dict[str, Any]) -> dict[str, Any]:
    return {key: value for key, value in document.items() if key != "_id"}

def _stored(collection: Any, query: dict[str, str], session: ClientSession) -> dict[str, Any]:
    document = collection.find_one(query, session=session)
    assert isinstance(document, dict)
    return document

def _session(client: MongoClient[Any]) -> ClientSession:
    return client.start_session()

def test_real_mongo_platform_release_authorization_matrix() -> None:
    client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=2000)
    database = client[f"wilsy_r3c2_{uuid4().hex}"]
    collection = database["platform_billing_release_authorizations"]
    try:
        authorization = _authorization()
        tenant_b = _authorization("tenant-b", key="idem-b", release_id="release-b")
        with _session(client) as session:
            created = PlatformBillingReleaseAuthorizationRegistry.create(authorization, collection, session=session)
            assert created.authorization == authorization and created.replayed is False
            assert collection.count_documents({}, session=session) == 1
            assert PlatformBillingReleaseAuthorizationRegistry.get("tenant-a", "release-a", collection, session=session) == authorization

            replay = PlatformBillingReleaseAuthorizationRegistry.create(authorization, collection, session=session)
            assert replay.authorization == authorization and replay.replayed is True
            assert collection.count_documents({}, session=session) == 1
            original = _semantic(_stored(collection, {"tenant_id": "tenant-a", "release_authorization_id": "release-a"}, session))

            with pytest.raises(PlatformBillingReleaseAuthorizationIdempotencyConflictError):
                PlatformBillingReleaseAuthorizationRegistry.create(_authorization(destination="DEST-DIVERGENT"), collection, session=session)
            assert _semantic(_stored(collection, {"tenant_id": "tenant-a", "release_authorization_id": "release-a"}, session)) == original
            with pytest.raises(PlatformBillingReleaseAuthorizationIdentityConflictError):
                PlatformBillingReleaseAuthorizationRegistry.create(_authorization(key="idem-new", destination="DEST-IDENTITY"), collection, session=session)
            assert collection.count_documents({"tenant_id": "tenant-a"}, session=session) == 1

            assert PlatformBillingReleaseAuthorizationRegistry.create(tenant_b, collection, session=session).authorization == tenant_b
            with pytest.raises(PlatformBillingReleaseAuthorizationNotFoundError):
                PlatformBillingReleaseAuthorizationRegistry.get("tenant-b", "release-a", collection, session=session)

            tamper_filter = {"tenant_id": "tenant-a", "release_authorization_id": "release-a"}
            collection.update_one(tamper_filter, {"$set": {"release_authorization_fingerprint": "c" * 128}}, session=session)
            with pytest.raises(PlatformBillingReleaseAuthorizationPersistedRecordInvalidError):
                PlatformBillingReleaseAuthorizationRegistry.get("tenant-a", "release-a", collection, session=session)
            collection.update_one(tamper_filter, {"$set": {"release_authorization_fingerprint": authorization.release_authorization_fingerprint, "schema": "WRONG"}}, session=session)
            with pytest.raises(PlatformBillingReleaseAuthorizationPersistedRecordInvalidError):
                PlatformBillingReleaseAuthorizationRegistry.get("tenant-a", "release-a", collection, session=session)
            collection.update_one(tamper_filter, {"$set": {"schema": "WILSY-PLATFORM-BILLING-RELEASE-AUTHORIZATION/V2", "authorized_amount_minor": 999}}, session=session)
            with pytest.raises(PlatformBillingReleaseAuthorizationPersistedRecordInvalidError):
                PlatformBillingReleaseAuthorizationRegistry.get("tenant-a", "release-a", collection, session=session)

            indexes = collection.index_information()
            assert indexes["tenant_release_authorization_unique"]["unique"] is True
            assert indexes["tenant_release_authorization_unique"]["key"] == [("tenant_id", 1), ("release_authorization_id", 1)]
            assert indexes["tenant_release_authorization_idempotency_unique"]["unique"] is True
            assert indexes["tenant_release_authorization_idempotency_unique"]["key"] == [("tenant_id", 1), ("idempotency_key", 1)]
    finally:
        database.drop_collection("platform_billing_release_authorizations")
        client.close()

# ARTIFACT: test_platform_billing_release_authorization_registry_mongo.py
# VERSION: v1.1.0-PLATFORM-BILLING-RELEASE-AUTHORIZATION-REGISTRY-MONGO-CERT
# AUTHORITY BOUNDARY: durable evidence only; no execution or settlement
# TENANT POSTURE: tenant-scoped identities and idempotency
# FAIL-CLOSED POSTURE: corruption, conflict, absence, and outage are explicit
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively
# END OF WILSY OS SOVEREIGN ARTIFACT
