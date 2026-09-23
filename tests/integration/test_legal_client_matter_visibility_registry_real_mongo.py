"""Host-backed certificate for L8-7B client-matter visibility persistence.

TITLE: WILSY OS Legal Client Matter Visibility Registry Real-Mongo Certificate
VERSION: v1.0.0-L8-7B-LEGAL-CLIENT-MATTER-VISIBILITY-REGISTRY-RM-CERT
AUTHORITY: Host-backed certification of append-only visibility persistence/currentness only.
EPITOME: Prove on the verified Mongo replica set that L8-7B enforces tenant-
         scoped lifecycle/fingerprint indexes, exact grant replay, many-to-many
         visibility, append-only revocation, no stale ACTIVE currentness,
         transaction abort, tenant isolation, and durable corruption rejection.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tests/integration/test_legal_client_matter_visibility_registry_real_mongo.py
COLLABORATION / OWNERSHIP: Host certificate for L8-7B registry plus L8-7A values
                            only. IAM, provisioning, HTTP/client projection,
                            lifecycle mutation and finance remain independent.
CERTIFICATION / UPDATE DATE: 2026-09-23
CHANGELOG: 2026-09-23 v1.0.0-L8-7B-LEGAL-CLIENT-MATTER-VISIBILITY-REGISTRY-RM-CERT
           establishes replica-set index, committed replay/current resolution,
           many-matter/many-client enumeration, append-only revocation, aborted
           write absence, tenant isolation, corruption rejection, and authority-
           surface absence against MongoDB.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2; ISO 27001.
SECURITY / PRIVACY POSTURE: UUID-isolated synthetic tenants/principals/matters only.
TENANT BOUNDARY: Every durable row and read is exact-tenant scoped.
AUTHORITY BOUNDARY: Persistence/currentness certificate only; no client read authorization.
FINANCIAL AUTHORITY BOUNDARY: Kennel EOS remains exclusive.
TRANSACTION BOUNDARY: Tests own Mongo transactions; registry receives active session.
FAIL-CLOSED DECLARATION: Replica-set, index, transaction, corruption or scope
                         failure rejects without visibility fabrication.
"""
from __future__ import annotations

from datetime import datetime, timedelta, timezone
import os
import sys
from typing import Any, Iterator
import uuid

import pytest
from pymongo import MongoClient
from pymongo.errors import PyMongoError
from pymongo.read_concern import ReadConcern
from pymongo.write_concern import WriteConcern

from tools.eos.legal_operations.domain.legal_client_matter_visibility_binding import (
    LegalClientMatterVisibilityBinding,
)
from tools.eos.legal_operations.domain.legal_operations_lifecycle import CaseMatter
from tools.eos.legal_operations.registry.legal_client_matter_visibility_registry import (
    COLLECTION,
    VERSION as PRODUCTION_VERSION,
    LegalClientMatterVisibilityNotFoundError,
    LegalClientMatterVisibilityPersistedRecordInvalidError,
    LegalClientMatterVisibilityRegistry,
)


VERSION = "v1.0.0-L8-7B-LEGAL-CLIENT-MATTER-VISIBILITY-REGISTRY-RM-CERT"
MONGO_URI = os.getenv(
    "TEST_VENDOR_MONGO_URI",
    "mongodb://127.0.0.1:27027/?replicaSet=wilsyVendorCertRS",
)
EXPECTED_REPLICA_SET = "wilsyVendorCertRS"
NOW = datetime(2026, 9, 23, 19, 30, tzinfo=timezone.utc)


@pytest.fixture
def mongo_context() -> Iterator[dict[str, Any]]:
    """Yield one verified writable isolated replica-set database."""
    client = MongoClient(
        MONGO_URI,
        serverSelectionTimeoutMS=3000,
        retryWrites=True,
    )
    database: Any = None
    try:
        try:
            hello = client.admin.command("hello")
        except PyMongoError as error:
            pytest.fail(
                f"L8_7B_MONGO_RUNTIME_UNAVAILABLE:{type(error).__name__}:{error}"
            )
        if hello.get("setName") != EXPECTED_REPLICA_SET:
            pytest.fail(
                f"L8_7B_MONGO_REPLICA_SET_MISMATCH:{hello.get('setName')!r}"
            )
        if hello.get("isWritablePrimary", hello.get("ismaster")) is not True:
            pytest.fail("L8_7B_MONGO_WRITABLE_PRIMARY_UNAVAILABLE")

        database = client[f"legal_ops_l8_7b_visibility_{uuid.uuid4().hex}"]
        collection = database.get_collection(
            COLLECTION,
            write_concern=WriteConcern(w="majority", j=True),
            read_concern=ReadConcern("majority"),
        )
        LegalClientMatterVisibilityRegistry.ensure_indexes(collection)
        yield {
            "client": client,
            "database": database,
            "collection": collection,
        }
    finally:
        active_error = sys.exc_info()[0] is not None
        try:
            if database is not None:
                try:
                    client.drop_database(database.name)
                except PyMongoError:
                    if not active_error:
                        raise
        finally:
            client.close()


def _grant(
    tenant: str,
    principal: str,
    matter_id: str,
) -> LegalClientMatterVisibilityBinding:
    source = CaseMatter(
        tenant_id=tenant,
        case_matter_id=matter_id,
        matter_reference=f"CASE-{matter_id}",
        opened_at=NOW,
        evidence_reference=f"matter-{matter_id}",
    )
    return LegalClientMatterVisibilityBinding.grant(
        client_principal_id=principal,
        case_matter=source,
        granted_by_principal_id="partner-provisioner",
        granted_at=NOW + timedelta(minutes=1),
        evidence_reference=f"grant-{principal}-{matter_id}",
    )


def _revoke(
    active: LegalClientMatterVisibilityBinding,
) -> LegalClientMatterVisibilityBinding:
    return active.revoke(
        revoked_by_principal_id="attorney-provisioner",
        revoked_at=NOW + timedelta(minutes=2),
        evidence_reference="revocation-evidence",
    )


def test_real_indexes_and_many_to_many_current_visibility(
    mongo_context: dict[str, Any],
) -> None:
    """Certify index shape, replay, current resolution and many-to-many support."""
    collection = mongo_context["collection"]
    indexes = {entry["name"]: entry for entry in collection.list_indexes()}
    lifecycle = indexes[
        "legal_operations_client_matter_visibility_lifecycle_unique"
    ]
    fingerprint = indexes[
        "legal_operations_client_matter_visibility_fingerprint_unique"
    ]
    assert lifecycle["unique"] is True
    assert lifecycle["key"] == {
        "tenant_id": 1,
        "binding_identity": 1,
        "status": 1,
    }
    assert fingerprint["unique"] is True
    assert fingerprint["key"] == {"tenant_id": 1, "fingerprint": 1}

    tenant = f"tenant-{uuid.uuid4().hex}"
    client_one = f"client-{uuid.uuid4().hex}"
    client_two = f"client-{uuid.uuid4().hex}"
    first = _grant(tenant, client_one, "matter-b")
    second = _grant(tenant, client_one, "matter-a")
    third = _grant(tenant, client_two, "matter-a")

    with mongo_context["client"].start_session() as session:
        session.start_transaction(
            read_concern=ReadConcern("snapshot"),
            write_concern=WriteConcern(w="majority", j=True),
        )
        created = LegalClientMatterVisibilityRegistry.grant(
            first,
            collection,
            session=session,
        )
        replay = LegalClientMatterVisibilityRegistry.grant(
            first,
            collection,
            session=session,
        )
        LegalClientMatterVisibilityRegistry.grant(
            second,
            collection,
            session=session,
        )
        LegalClientMatterVisibilityRegistry.grant(
            third,
            collection,
            session=session,
        )
        current = LegalClientMatterVisibilityRegistry.resolve_current_active(
            tenant,
            client_one,
            "matter-b",
            collection,
            session=session,
        )
        session.commit_transaction()

    assert created == replay == current == first
    assert [value.case_matter_id for value in (
        LegalClientMatterVisibilityRegistry.list_active_for_principal(
            tenant,
            client_one,
            collection,
        )
    )] == ["matter-a", "matter-b"]
    assert [value.case_matter_id for value in (
        LegalClientMatterVisibilityRegistry.list_active_for_principal(
            tenant,
            client_two,
            collection,
        )
    )] == ["matter-a"]
    assert collection.count_documents({"tenant_id": tenant}) == 3


def test_real_revocation_is_append_only_and_suppresses_stale_active(
    mongo_context: dict[str, Any],
) -> None:
    """ACTIVE history remains durable but revoked relation is never current."""
    collection = mongo_context["collection"]
    tenant = f"tenant-{uuid.uuid4().hex}"
    principal = f"client-{uuid.uuid4().hex}"
    active = _grant(tenant, principal, "matter-1")
    revoked = _revoke(active)

    with mongo_context["client"].start_session() as session:
        session.start_transaction(
            read_concern=ReadConcern("snapshot"),
            write_concern=WriteConcern(w="majority", j=True),
        )
        LegalClientMatterVisibilityRegistry.grant(
            active,
            collection,
            session=session,
        )
        created = LegalClientMatterVisibilityRegistry.revoke(
            revoked,
            collection,
            session=session,
        )
        replay = LegalClientMatterVisibilityRegistry.revoke(
            revoked,
            collection,
            session=session,
        )
        session.commit_transaction()

    assert created == replay == revoked
    rows = list(
        collection.find(
            {
                "tenant_id": tenant,
                "client_principal_id": principal,
                "case_matter_id": "matter-1",
            }
        )
    )
    assert len(rows) == 2
    assert {row["status"] for row in rows} == {"ACTIVE", "REVOKED"}

    with pytest.raises(LegalClientMatterVisibilityNotFoundError):
        LegalClientMatterVisibilityRegistry.resolve_current_active(
            tenant,
            principal,
            "matter-1",
            collection,
        )
    assert (
        LegalClientMatterVisibilityRegistry.list_active_for_principal(
            tenant,
            principal,
            collection,
        )
        == ()
    )


def test_real_transaction_abort_and_foreign_tenant_are_absence(
    mongo_context: dict[str, Any],
) -> None:
    """Caller abort removes attempted write; foreign scope reveals no row."""
    collection = mongo_context["collection"]
    tenant = f"tenant-{uuid.uuid4().hex}"
    principal = f"client-{uuid.uuid4().hex}"
    active = _grant(tenant, principal, "matter-1")

    with mongo_context["client"].start_session() as session:
        session.start_transaction(
            read_concern=ReadConcern("snapshot"),
            write_concern=WriteConcern(w="majority", j=True),
        )
        LegalClientMatterVisibilityRegistry.grant(
            active,
            collection,
            session=session,
        )
        session.abort_transaction()

    assert collection.count_documents({"tenant_id": tenant}) == 0
    with pytest.raises(LegalClientMatterVisibilityNotFoundError):
        LegalClientMatterVisibilityRegistry.resolve_current_active(
            tenant,
            principal,
            "matter-1",
            collection,
        )

    LegalClientMatterVisibilityRegistry.grant(active, collection)
    foreign = f"tenant-{uuid.uuid4().hex}"
    with pytest.raises(LegalClientMatterVisibilityNotFoundError):
        LegalClientMatterVisibilityRegistry.resolve_current_active(
            foreign,
            principal,
            "matter-1",
            collection,
        )
    assert (
        LegalClientMatterVisibilityRegistry.list_active_for_principal(
            foreign,
            principal,
            collection,
        )
        == ()
    )


def test_real_corruption_rejects_and_registry_contains_no_authority_truth(
    mongo_context: dict[str, Any],
) -> None:
    """Fingerprint corruption fails closed; durable payload grants no IAM/finance."""
    collection = mongo_context["collection"]
    tenant = f"tenant-{uuid.uuid4().hex}"
    principal = f"client-{uuid.uuid4().hex}"
    active = _grant(tenant, principal, "matter-1")
    LegalClientMatterVisibilityRegistry.grant(active, collection)

    row = collection.find_one(
        {
            "tenant_id": tenant,
            "binding_identity": active.binding_identity,
            "status": "ACTIVE",
        }
    )
    assert row is not None
    forbidden = {
        "permission",
        "authorized",
        "role_id",
        "business_role",
        "instruction_id",
        "document_id",
        "attempt_id",
        "service_execution_id",
        "return_id",
        "invoice_id",
        "payment_id",
        "settlement_id",
    }
    assert forbidden.isdisjoint(row)

    result = collection.update_one(
        {"_id": row["_id"]},
        {"$set": {"fingerprint": "f" * 128}},
    )
    assert result.matched_count == 1
    with pytest.raises(LegalClientMatterVisibilityPersistedRecordInvalidError):
        LegalClientMatterVisibilityRegistry.resolve_current_active(
            tenant,
            principal,
            "matter-1",
            collection,
        )

    assert PRODUCTION_VERSION == (
        "v1.0.0-L8-7B-LEGAL-CLIENT-MATTER-VISIBILITY-REGISTRY"
    )


# SOVEREIGN ARTIFACT SEAL
# ARTIFACT: test_legal_client_matter_visibility_registry_real_mongo.py
# VERSION: v1.0.0-L8-7B-LEGAL-CLIENT-MATTER-VISIBILITY-REGISTRY-RM-CERT
# AUTHORITY BOUNDARY: host-backed append-only visibility persistence/currentness certificate only
# TENANT POSTURE: exact tenant/client/matter history, many-to-many scope and foreign absence are certified
# FAIL-CLOSED POSTURE: transaction abort, stale ACTIVE, corruption and foreign scope never become current visibility
# FINANCIAL EXECUTION AUTHORITY: none; Kennel EOS remains exclusive
# END OF WILSY OS SOVEREIGN ARTIFACT
