"""Direct certificate for WILSY OS CRM Lead durable Mongo registry.

TITLE: WILSY OS CRM Lead Durable Registry Direct Certificate
VERSION: v1.0.0-CRM-P8A-LEAD-REGISTRY-CERT
AUTHORITY: Wilsy OS Core Governance
PURPOSE:
    Freeze the durable persistence contract for canonical CRM Lead truth before
    implementation exists.

CERTIFICATION SCOPE:
    - deterministic Mongo collection and indexes;
    - exact tenant-scoped Lead identity;
    - exact tenant-local idempotent replay;
    - divergent replay rejection;
    - caller-owned Mongo session requirement;
    - exact durable hydration through CrmLead.from_dict;
    - corruption rejection;
    - cross-tenant absence;
    - no TTL deletion;
    - no role, permission, entitlement, AI, deal, invoice or financial authority.

TRANSACTION BOUNDARY:
    The caller owns ClientSession and transaction lifecycle. The registry must
    never start, commit or abort a transaction.

FINANCIAL AUTHORITY BOUNDARY:
    None. Kennel EOS remains exclusive financial execution authority.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime
from typing import Any

import pytest

from tools.eos.crm.domain.crm_lead import (
    CrmLead,
    CrmLeadConsentBasis,
    CrmLeadPriority,
    CrmLeadSourceChannel,
    CrmLeadStatus,
)
from tools.eos.crm.persistence.crm_lead_registry import (
    COLLECTION,
    CRM_LEAD_REGISTRY_VERSION,
    CrmLeadRegistry,
    CrmLeadRegistryConflictError,
    CrmLeadRegistryError,
    CrmLeadRegistryNotFoundError,
    ensure_indexes,
)


EXPECTED_VERSION = "v1.0.0-CRM-LEAD-REGISTRY"
EXPECTED_COLLECTION = "crm_leads"


def _lead(
    *,
    tenant_id: str = "tenant-alpha",
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
        notes="qualified discovery candidate",
        created_at=datetime(2026, 10, 6, 14, 0, tzinfo=UTC),
    )


@dataclass
class _InsertResult:
    inserted_id: str = "mongo-row-1"


class _Collection:
    def __init__(self) -> None:
        self.documents: list[dict[str, object]] = []
        self.index_calls: list[
            tuple[list[tuple[str, int]], bool, str]
        ] = []
        self.find_calls: list[
            tuple[dict[str, object], object]
        ] = []
        self.insert_sessions: list[object] = []

    def with_options(self, **_: object) -> "_Collection":
        return self

    def create_index(
        self,
        keys: list[tuple[str, int]],
        *,
        unique: bool = False,
        name: str,
    ) -> str:
        self.index_calls.append((keys, unique, name))
        return name

    def find_one(
        self,
        query: dict[str, object],
        *,
        session: object,
    ) -> dict[str, object] | None:
        self.find_calls.append((dict(query), session))

        for document in self.documents:
            if all(document.get(key) == value for key, value in query.items()):
                return dict(document)

        return None

    def insert_one(
        self,
        document: dict[str, object],
        *,
        session: object,
    ) -> _InsertResult:
        self.documents.append(dict(document))
        self.insert_sessions.append(session)
        return _InsertResult()


def test_registry_version_and_collection_are_frozen() -> None:
    assert CRM_LEAD_REGISTRY_VERSION == EXPECTED_VERSION
    assert COLLECTION == EXPECTED_COLLECTION


def test_indexes_are_deterministic_tenant_scoped_and_have_no_ttl() -> None:
    collection = _Collection()

    ensure_indexes(collection)

    assert collection.index_calls == [
        (
            [("tenant_id", 1), ("lead_id", 1)],
            True,
            "crm_lead_tenant_identity_unique",
        ),
        (
            [("tenant_id", 1), ("idempotency_key", 1)],
            True,
            "crm_lead_tenant_idempotency_unique",
        ),
        (
            [("tenant_id", 1), ("status", 1), ("updated_at", -1)],
            False,
            "crm_lead_tenant_status_updated_at",
        ),
        (
            [("tenant_id", 1), ("owner_id", 1), ("updated_at", -1)],
            False,
            "crm_lead_tenant_owner_updated_at",
        ),
    ]

    assert all("expire" not in name.lower() for _, _, name in collection.index_calls)
    assert all("ttl" not in name.lower() for _, _, name in collection.index_calls)


def test_registry_requires_collection() -> None:
    with pytest.raises(
        CrmLeadRegistryError,
        match="CRM_LEAD_REGISTRY_COLLECTION_REQUIRED",
    ):
        CrmLeadRegistry(None)


@pytest.mark.parametrize("key", ["", " ", " replay-key", "replay-key "])
def test_create_or_replay_requires_exact_idempotency_key(key: str) -> None:
    registry = CrmLeadRegistry(_Collection())

    with pytest.raises(
        CrmLeadRegistryError,
        match="CRM_LEAD_REGISTRY_IDEMPOTENCY_KEY_INVALID",
    ):
        registry.create_or_replay(
            _lead(),
            idempotency_key=key,
            session=object(),
        )


def test_create_requires_caller_owned_session() -> None:
    registry = CrmLeadRegistry(_Collection())

    with pytest.raises(
        CrmLeadRegistryError,
        match="CRM_LEAD_REGISTRY_SESSION_REQUIRED",
    ):
        registry.create_or_replay(
            _lead(),
            idempotency_key="create-1",
            session=None,
        )


def test_get_requires_caller_owned_session() -> None:
    lead = _lead()
    registry = CrmLeadRegistry(_Collection())

    with pytest.raises(
        CrmLeadRegistryError,
        match="CRM_LEAD_REGISTRY_SESSION_REQUIRED",
    ):
        registry.get(
            tenant_id=lead.tenant_id,
            lead_id=lead.lead_id,
            session=None,
        )


def test_create_persists_exact_lead_truth_and_registry_evidence() -> None:
    collection = _Collection()
    registry = CrmLeadRegistry(collection)
    lead = _lead()
    session = object()

    created = registry.create_or_replay(
        lead,
        idempotency_key="create-1",
        session=session,
    )

    assert created == lead
    assert len(collection.documents) == 1

    durable = collection.documents[0]

    for key, value in lead.to_dict().items():
        assert durable[key] == value

    assert durable["tenant_id"] == lead.tenant_id
    assert durable["lead_id"] == lead.lead_id
    assert durable["idempotency_key"] == "create-1"
    assert isinstance(durable["command_fingerprint"], str)
    assert len(durable["command_fingerprint"]) == 128
    assert collection.insert_sessions == [session]

    forbidden = {
        "deal_id",
        "opportunity_id",
        "quote_id",
        "invoice_id",
        "payment_status",
        "settlement_status",
        "revenue",
    }

    assert forbidden.isdisjoint(durable)


def test_exact_replay_returns_original_durable_identity_without_second_write() -> None:
    collection = _Collection()
    registry = CrmLeadRegistry(collection)
    lead = _lead()
    session = object()

    first = registry.create_or_replay(
        lead,
        idempotency_key="replay-1",
        session=session,
    )
    second = registry.create_or_replay(
        lead,
        idempotency_key="replay-1",
        session=session,
    )

    assert first == lead
    assert second == lead
    assert second.lead_id == first.lead_id
    assert len(collection.documents) == 1


def test_same_tenant_and_key_with_divergent_command_rejects() -> None:
    collection = _Collection()
    registry = CrmLeadRegistry(collection)
    session = object()

    first = _lead(score=25)
    second = _lead(score=91)

    registry.create_or_replay(
        first,
        idempotency_key="conflict-1",
        session=session,
    )

    with pytest.raises(
        CrmLeadRegistryConflictError,
        match="CRM_LEAD_REGISTRY_DIVERGENT_IDEMPOTENCY",
    ):
        registry.create_or_replay(
            second,
            idempotency_key="conflict-1",
            session=session,
        )

    assert len(collection.documents) == 1


def test_same_idempotency_key_is_independent_between_tenants() -> None:
    collection = _Collection()
    registry = CrmLeadRegistry(collection)
    session = object()

    tenant_a = _lead(tenant_id="tenant-alpha")
    tenant_b = _lead(tenant_id="tenant-beta")

    registry.create_or_replay(
        tenant_a,
        idempotency_key="shared-key",
        session=session,
    )
    registry.create_or_replay(
        tenant_b,
        idempotency_key="shared-key",
        session=session,
    )

    assert len(collection.documents) == 2
    assert {item["tenant_id"] for item in collection.documents} == {
        "tenant-alpha",
        "tenant-beta",
    }


def test_get_is_exactly_tenant_scoped_and_cross_tenant_is_absent() -> None:
    collection = _Collection()
    registry = CrmLeadRegistry(collection)
    session = object()
    lead = _lead(tenant_id="tenant-alpha")

    registry.create_or_replay(
        lead,
        idempotency_key="read-1",
        session=session,
    )

    observed = registry.get(
        tenant_id="tenant-alpha",
        lead_id=lead.lead_id,
        session=session,
    )

    assert observed == lead

    with pytest.raises(
        CrmLeadRegistryNotFoundError,
        match="CRM_LEAD_REGISTRY_NOT_FOUND",
    ):
        registry.get(
            tenant_id="tenant-beta",
            lead_id=lead.lead_id,
            session=session,
        )


@pytest.mark.parametrize(
    "tenant_id",
    [
        "",
        " ",
        " tenant-alpha",
        "tenant-alpha ",
        "MASTER",
        "GLOBAL_ROOT",
        "SOVEREIGN_ROOT",
        "wilsy-sovereign-root",
    ],
)
def test_get_rejects_invalid_or_global_tenant_scope(tenant_id: str) -> None:
    registry = CrmLeadRegistry(_Collection())

    with pytest.raises(
        CrmLeadRegistryError,
        match="CRM_LEAD_REGISTRY_TENANT_ID_INVALID",
    ):
        registry.get(
            tenant_id=tenant_id,
            lead_id=_lead().lead_id,
            session=object(),
        )


def test_get_rejects_corrupt_durable_lead() -> None:
    collection = _Collection()
    registry = CrmLeadRegistry(collection)
    session = object()
    lead = _lead()

    registry.create_or_replay(
        lead,
        idempotency_key="corrupt-1",
        session=session,
    )

    collection.documents[0]["status"] = "CORRUPT"

    with pytest.raises(
        CrmLeadRegistryError,
        match="CRM_LEAD_REGISTRY_CORRUPT_DOCUMENT",
    ):
        registry.get(
            tenant_id=lead.tenant_id,
            lead_id=lead.lead_id,
            session=session,
        )


def test_registry_exposes_no_transaction_or_financial_execution_methods() -> None:
    forbidden = {
        "start_transaction",
        "commit_transaction",
        "abort_transaction",
        "charge",
        "settle",
        "pay",
        "invoice",
        "create_deal",
    }

    assert forbidden.isdisjoint(dir(CrmLeadRegistry))


# =============================================================================
# WILSY OS SOVEREIGN TEST ARTIFACT SEAL
# ARTIFACT: test_crm_lead_registry.py
# VERSION: v1.0.0-CRM-P8A-LEAD-REGISTRY-CERT
# AUTHORITY BOUNDARY: direct durable CRM Lead registry contract only
# TENANT POSTURE: exact tenant scope; no MASTER/global/root/default fallback
# TRANSACTION POSTURE: caller owns session and transaction lifecycle
# FINANCIAL EXECUTION AUTHORITY: none; Kennel EOS exclusively
# END OF WILSY OS SOVEREIGN TEST ARTIFACT
# =============================================================================
