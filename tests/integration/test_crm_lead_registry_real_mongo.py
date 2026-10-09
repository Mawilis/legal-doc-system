"""Real-Mongo certificate for WILSY OS CRM Lead durable registry.

TITLE: WILSY OS CRM Lead Real Mongo Certificate
VERSION: v1.0.0-CRM-P8C-LEAD-REAL-MONGO-CERT
AUTHORITY: Wilsy OS Core Governance
PURPOSE:
    Certify physical Mongo indexes, exact replay, strict hydration, tenant
    isolation, caller transaction ownership, corruption rejection, restart
    durability and competing creation against an actual replica-set MongoDB.

TEST DATA:
    UUID-isolated synthetic database and tenant identities only.

TRANSACTION BOUNDARY:
    The caller owns every ClientSession and transaction lifecycle.

FINANCIAL AUTHORITY BOUNDARY:
    None. Kennel EOS remains exclusive financial execution authority.
"""

from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor
from collections.abc import Iterator
from dataclasses import dataclass
from datetime import UTC, datetime
import os
import uuid

import pytest
from pymongo import MongoClient
from pymongo.collection import Collection

from tools.eos.crm.domain.crm_lead import (
    CrmLead,
    CrmLeadConsentBasis,
    CrmLeadPriority,
    CrmLeadSourceChannel,
    CrmLeadStatus,
)
from tools.eos.crm.persistence.crm_lead_registry import (
    COLLECTION,
    CrmLeadRegistry,
    CrmLeadRegistryError,
    CrmLeadRegistryNotFoundError,
    ensure_indexes,
)


@dataclass
class MongoContext:
    client: MongoClient
    database_name: str
    collection: Collection[dict[str, object]]
    registry: CrmLeadRegistry


def _lead(
    *,
    tenant_id: str,
    owner_id: str = "principal-owner-1",
    status: CrmLeadStatus = CrmLeadStatus.NEW,
    score: int = 73,
) -> CrmLead:
    return CrmLead.create(
        tenant_id=tenant_id,
        full_name="Ada Ndlovu",
        company_name="Sovereign Logistics",
        email="ada@example.test",
        phone="+27821234567",
        mobile="+27821234567",
        status=status,
        owner_id=owner_id,
        source_channel=CrmLeadSourceChannel.REFERRAL,
        priority=CrmLeadPriority.HIGH,
        consent_basis=CrmLeadConsentBasis.CONSENT,
        score=score,
        industry="Logistics",
        due_at=None,
        notes="real mongo certificate",
        created_at=datetime(2026, 10, 6, 14, 0, tzinfo=UTC),
    )


@pytest.fixture
def mongo_context() -> Iterator[MongoContext]:
    uri = os.environ["WILSY_CRM_REAL_MONGO_URI"]

    client = MongoClient(
        uri,
        serverSelectionTimeoutMS=5000,
        connectTimeoutMS=5000,
    )

    hello = client.admin.command("hello")
    assert hello.get("setName"), "REAL_MONGO_REPLICA_SET_REQUIRED"

    database_name = f"wilsy_crm_p8c_{uuid.uuid4().hex}"
    database = client[database_name]
    collection = database[COLLECTION]

    ensure_indexes(collection)

    context = MongoContext(
        client=client,
        database_name=database_name,
        collection=collection,
        registry=CrmLeadRegistry(collection),
    )

    yield context

    client.drop_database(database_name)
    client.close()


def test_real_physical_indexes_exact_and_no_ttl(
    mongo_context: MongoContext,
) -> None:
    indexes = {
        item["name"]: item
        for item in mongo_context.collection.list_indexes()
    }

    assert indexes["crm_lead_tenant_identity_unique"]["key"] == {
        "tenant_id": 1,
        "lead_id": 1,
    }
    assert indexes["crm_lead_tenant_identity_unique"]["unique"] is True

    assert indexes["crm_lead_tenant_idempotency_unique"]["key"] == {
        "tenant_id": 1,
        "idempotency_key": 1,
    }
    assert indexes["crm_lead_tenant_idempotency_unique"]["unique"] is True

    assert indexes["crm_lead_tenant_status_updated_at"]["key"] == {
        "tenant_id": 1,
        "status": 1,
        "updated_at": -1,
    }

    assert indexes["crm_lead_tenant_owner_updated_at"]["key"] == {
        "tenant_id": 1,
        "owner_id": 1,
        "updated_at": -1,
    }

    for index in indexes.values():
        assert "expireAfterSeconds" not in index


def test_real_create_exact_replay_and_restart_hydration(
    mongo_context: MongoContext,
) -> None:
    tenant = f"tenant-{uuid.uuid4().hex}"
    lead = _lead(tenant_id=tenant)

    with mongo_context.client.start_session() as session:
        first = mongo_context.registry.create_or_replay(
            lead,
            idempotency_key="create-1",
            session=session,
        )
        second = mongo_context.registry.create_or_replay(
            lead,
            idempotency_key="create-1",
            session=session,
        )

    assert first == lead
    assert second == lead
    assert second.lead_id == lead.lead_id

    assert mongo_context.collection.count_documents(
        {
            "tenant_id": tenant,
            "idempotency_key": "create-1",
        }
    ) == 1

    restarted = CrmLeadRegistry(mongo_context.collection)

    with mongo_context.client.start_session() as session:
        hydrated = restarted.get(
            tenant_id=tenant,
            lead_id=lead.lead_id,
            session=session,
        )

    assert hydrated == lead
    assert hydrated.lead_id == lead.lead_id


def test_real_same_idempotency_key_is_tenant_local(
    mongo_context: MongoContext,
) -> None:
    tenant_a = f"tenant-a-{uuid.uuid4().hex}"
    tenant_b = f"tenant-b-{uuid.uuid4().hex}"

    lead_a = _lead(tenant_id=tenant_a)
    lead_b = _lead(tenant_id=tenant_b)

    with mongo_context.client.start_session() as session:
        mongo_context.registry.create_or_replay(
            lead_a,
            idempotency_key="shared-key",
            session=session,
        )
        mongo_context.registry.create_or_replay(
            lead_b,
            idempotency_key="shared-key",
            session=session,
        )

    assert mongo_context.collection.count_documents(
        {"idempotency_key": "shared-key"}
    ) == 2


def test_real_cross_tenant_read_is_absent(
    mongo_context: MongoContext,
) -> None:
    tenant_a = f"tenant-a-{uuid.uuid4().hex}"
    tenant_b = f"tenant-b-{uuid.uuid4().hex}"
    lead = _lead(tenant_id=tenant_a)

    with mongo_context.client.start_session() as session:
        mongo_context.registry.create_or_replay(
            lead,
            idempotency_key="tenant-read",
            session=session,
        )

        with pytest.raises(
            CrmLeadRegistryNotFoundError,
            match="CRM_LEAD_REGISTRY_NOT_FOUND",
        ):
            mongo_context.registry.get(
                tenant_id=tenant_b,
                lead_id=lead.lead_id,
                session=session,
            )


def test_real_aborted_transaction_is_invisible_and_commit_is_visible(
    mongo_context: MongoContext,
) -> None:
    aborted_tenant = f"tenant-abort-{uuid.uuid4().hex}"
    aborted = _lead(tenant_id=aborted_tenant)

    with mongo_context.client.start_session() as session:
        session.start_transaction()

        mongo_context.registry.create_or_replay(
            aborted,
            idempotency_key="abort-1",
            session=session,
        )

        inside = mongo_context.registry.get(
            tenant_id=aborted_tenant,
            lead_id=aborted.lead_id,
            session=session,
        )
        assert inside == aborted

        session.abort_transaction()

    assert mongo_context.collection.find_one(
        {
            "tenant_id": aborted_tenant,
            "lead_id": aborted.lead_id,
        }
    ) is None

    committed_tenant = f"tenant-commit-{uuid.uuid4().hex}"
    committed = _lead(tenant_id=committed_tenant)

    with mongo_context.client.start_session() as session:
        session.start_transaction()

        mongo_context.registry.create_or_replay(
            committed,
            idempotency_key="commit-1",
            session=session,
        )

        session.commit_transaction()

    assert mongo_context.collection.find_one(
        {
            "tenant_id": committed_tenant,
            "lead_id": committed.lead_id,
        }
    ) is not None


def test_real_corruption_rejected_fail_closed(
    mongo_context: MongoContext,
) -> None:
    tenant = f"tenant-corrupt-{uuid.uuid4().hex}"
    lead = _lead(tenant_id=tenant)

    with mongo_context.client.start_session() as session:
        mongo_context.registry.create_or_replay(
            lead,
            idempotency_key="corrupt-1",
            session=session,
        )

    mongo_context.collection.update_one(
        {
            "tenant_id": tenant,
            "lead_id": lead.lead_id,
        },
        {"$set": {"status": "CORRUPT"}},
    )

    with mongo_context.client.start_session() as session:
        with pytest.raises(
            CrmLeadRegistryError,
            match="CRM_LEAD_REGISTRY_CORRUPT_DOCUMENT",
        ):
            mongo_context.registry.get(
                tenant_id=tenant,
                lead_id=lead.lead_id,
                session=session,
            )


def test_real_competing_exact_creates_converge_to_one_durable_row(
    mongo_context: MongoContext,
) -> None:
    tenant = f"tenant-race-{uuid.uuid4().hex}"
    lead = _lead(tenant_id=tenant)

    def create() -> str:
        with mongo_context.client.start_session() as session:
            result = mongo_context.registry.create_or_replay(
                lead,
                idempotency_key="race-1",
                session=session,
            )
            return result.lead_id

    with ThreadPoolExecutor(max_workers=2) as executor:
        results = list(executor.map(lambda _: create(), range(2)))

    assert results == [lead.lead_id, lead.lead_id]

    assert mongo_context.collection.count_documents(
        {
            "tenant_id": tenant,
            "idempotency_key": "race-1",
        }
    ) == 1


def test_real_collection_contains_no_foreign_authority(
    mongo_context: MongoContext,
) -> None:
    tenant = f"tenant-authority-{uuid.uuid4().hex}"
    lead = _lead(tenant_id=tenant)

    with mongo_context.client.start_session() as session:
        mongo_context.registry.create_or_replay(
            lead,
            idempotency_key="authority-1",
            session=session,
        )

    persisted = mongo_context.collection.find_one(
        {
            "tenant_id": tenant,
            "lead_id": lead.lead_id,
        }
    )

    assert persisted is not None

    forbidden = {
        "deal_id",
        "opportunity_id",
        "quote_id",
        "invoice_id",
        "payment_status",
        "settlement_status",
        "revenue",
    }

    assert forbidden.isdisjoint(persisted)


# =============================================================================
# WILSY OS SOVEREIGN TEST ARTIFACT SEAL
# ARTIFACT: test_crm_lead_registry_real_mongo.py
# VERSION: v1.0.0-CRM-P8C-LEAD-REAL-MONGO-CERT
# AUTHORITY BOUNDARY: actual Mongo durability certificate only
# TENANT POSTURE: exact synthetic tenant scope; cross-tenant absence certified
# TRANSACTION POSTURE: caller owns session and transaction lifecycle
# FINANCIAL EXECUTION AUTHORITY: none; Kennel EOS exclusively
# END OF WILSY OS SOVEREIGN TEST ARTIFACT
# =============================================================================
