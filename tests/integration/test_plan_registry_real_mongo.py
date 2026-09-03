# -*- coding: utf-8 -*-
"""
TITLE:
    WILSY OS — PlanRegistry Real-Mongo Certification

VERSION:
    v1.1.2-PLAN-REGISTRY-SELF-VERSION-ALIGNMENT-CERT

AUTHORITY:
    Wilsy OS Core Governance

PURPOSE:
    Certify that the canonical PlanRegistry persists and rehydrates PlanEntity
    commercial evidence through actual MongoDB without in-memory authority.

EPITOME:
    Catalogue durability is real only when canonical PlanEntity evidence survives
    independent-process hydration and persistence failure cannot masquerade as
    absence.

ABSOLUTE CANONICAL PATH:
    /Users/wilsonkhanyezi/legal-doc-system/tests/integration/test_plan_registry_real_mongo.py

OWNERSHIP:
    Python EOS SaaS / Billing certification.

COLLABORATION:
    PlanEntity remains sovereign commercial-state validator.
    PlanRegistry remains catalogue persistence/lifecycle owner.
    Plan HTTP authorization remains outside this certificate.

CLASSIFICATION:
    Integration Certification Artifact

CERTIFICATION DATE:
    2026-09-03

CHANGELOG:
    2026-09-03 v1.1.2-PLAN-REGISTRY-SELF-VERSION-ALIGNMENT-CERT
        - Aligns the topology certificate's TEST_VERSION assertion with its governed runtime identity.
        - PlanRegistry production bytes and exact-tenant semantics remain unchanged.
    2026-09-03 v1.1.1-PLAN-REGISTRY-VERSION-ALIGNMENT-CERT
        - Aligns the topology/version certificate with PlanRegistry v1.2.0 exact-tenant scope.
        - No production bytes or catalogue semantics change.
    2026-09-03 v1.1.0-PLAN-REGISTRY-EXACT-TENANT-CERT
        - Certifies default global compatibility plus exact-tenant opt-in.
        - Certifies exact filtering before total/pages/pagination.
        - Certifies global Plans cannot be updated/archived in exact mode.
    2026-09-03 v1.0.4-PLAN-REGISTRY-CONSUMER-CONVERGENCE-CERT
        - Certifies that /billing/plans delegates catalogue truth to
          PlanRegistry and contains no direct plans-collection reader.
        - Certifies removal of PlanEntity/minimal fallback hydration and
          explicit HTTP 503 failure on catalogue persistence errors.
        - Preserves all v1.0.3 Real-Mongo storage/CAS certificates.
    2026-09-03 v1.0.3-PLAN-REGISTRY-STORAGE-CAS-CERT
        - Corrects the certificate's own topology/version assertion to the
          current certificate version after the v1.0.2 transport-fixture
          alignment.
        - No production Registry, Plan Domain, Billing Router or domain
          certificate bytes are changed.
        - Test count and behavioral coverage remain unchanged.
    2026-09-03 v1.0.2-PLAN-REGISTRY-STORAGE-CAS-CERT
        - Aligns the synthetic unversioned/legacy Mongo fixture with the required
          Registry transport envelope by supplying _registry_revision=1.
        - Preserves the distinct certificate that missing transport revision
          fails closed as PLAN_REGISTRY_REVISION_INVALID.
        - Proves that a valid Registry envelope cannot bless unversioned Plan
          commercial material; PlanEntity still requires explicit legacy
          migration.
        - Production PlanRegistry bytes remain unchanged.
    2026-09-03 v1.0.1-PLAN-REGISTRY-STORAGE-CAS-CERT
        - Certifies explicit _id plus monotonic _registry_revision transport
          evidence without promoting those fields into PlanEntity state.
        - Reproduces the P2R1 ABA defect by advancing only the storage revision
          while the former CAS commercial fields remain unchanged.
        - Certifies immutable Mongo identity binding and undeclared persisted
          field rejection.
        - Certifies successful lifecycle logging is debug-gated.
    2026-09-03 v1.0.0-PLAN-REGISTRY-REAL-MONGO-CERT
        - Certifies actual Mongo topology, majority durability and deterministic
          catalogue indexes.
        - Certifies canonical PlanEntity.to_dict()/from_dict() persistence.
        - Certifies global plan-id/idempotency uniqueness.
        - Certifies global-plan plus tenant-scope catalogue compatibility.
        - Certifies update/archive/reactivate evidence durability and optimistic
          compare-and-swap protection.
        - Certifies invalid persisted truth and Mongo outages fail closed.
        - Certifies independent-process read-back durability.
        - Migrates the former Plan Domain certificate's Registry-specific
          user-context, price-passthrough and health assertions here.

COMPLIANCE:
    POPIA §19 | GDPR §32 | SOC2 CC7.2 | ISO 27001

SECURITY / PRIVACY:
    Synthetic certification data only. No production or Atlas connection is
    permitted. Environment outage is a certification failure, never a skip.

TENANT / AUTHORITY BOUNDARY:
    tenant_id is catalogue scope evidence only. These tests do not certify
    membership, roles, permissions, subscription entitlement or HTTP authority.

FINANCIAL AUTHORITY:
    NONE. Kennel EOS remains the exclusive financial execution authority.

REAL-WORLD POSTURE:
    Actual MongoDB only. No mongomock, fake collection or in-memory registry is
    accepted as persistence evidence.

WILSY OS — ALL OR NOTHING.
"""

from __future__ import annotations

from collections.abc import Iterator
from decimal import Decimal
from pathlib import Path
from typing import Any
import ast
import os
import subprocess
import sys
import uuid

import pytest
from pymongo import MongoClient
from pymongo.collection import Collection
from pymongo.errors import PyMongoError
from pymongo.read_concern import ReadConcern
from pymongo.write_concern import WriteConcern

import tools.eos.saas.billing.plan_registry as registry
from tools.eos.saas.billing.plan_registry import (
    PLAN_REGISTRY_VERSION,
    PlanRegistry,
)
from tools.eos.saas.domain.plan import (
    AuditAction,
    PlanEntity,
    PlanTiers,
)

TEST_VERSION = (
    "v1.1.2-PLAN-REGISTRY-SELF-VERSION-ALIGNMENT-CERT"
)

CERT_URI_ENV = (
    "TEST_VENDOR_MONGO_URI"
)

DEFAULT_CERT_URI = (
    "mongodb://127.0.0.1:27027/"
    "?replicaSet=wilsyVendorCertRS"
)

EXPECTED_REPLICA_SET = (
    "wilsyVendorCertRS"
)

TEST_MONGO_URI = os.getenv(
    CERT_URI_ENV,
    DEFAULT_CERT_URI,
)

_ROOT = (
    Path(__file__)
    .resolve()
    .parents[2]
)

_EXPECTED_INDEXES = {
    "plan_id_unique",
    "idempotency_key_unique",
    "tenant_active",
    "tenant_plan_type",
    "catalogue_order",
}


class _MongoContext:
    """Hold one UUID-isolated actual-Mongo certification database."""

    def __init__(
        self,
        *,
        client: MongoClient[Any],
        collection: Collection[
            dict[
                str,
                Any,
            ]
        ],
        database_name: str,
        database_uri: str,
    ) -> None:
        self.client = client
        self.collection = collection
        self.database_name = database_name
        self.database_uri = database_uri


def _database_uri(
    uri: str,
    database_name: str,
) -> str:
    base, separator, query = (
        uri.partition(
            "?"
        )
    )

    prefix = base.rsplit(
        "/",
        1,
    )[0]

    resolved = (
        f"{prefix}/{database_name}"
    )

    if separator:
        resolved += (
            f"?{query}"
        )

    return resolved


def _payload(
    *,
    name: str = "Professional",
    price: Any = 499.0,
    plan_type: str = "PROFESSIONAL",
    idempotency_key: str,
    tenant_id: str | None = None,
    plan_id: str | None = None,
    active: bool = True,
    user: str = "PLAN-MONGO-CERT",
) -> dict[
    str,
    Any,
]:
    payload: dict[
        str,
        Any,
    ] = {
        "name":
            name,
        "price":
            price,
        "currency":
            "ZAR",
        "billingFrequency":
            "monthly",
        "planType":
            plan_type,
        "idempotencyKey":
            idempotency_key,
        "active":
            active,
        "features": [
            "crm.core",
            "legal.documents",
        ],
        "metadata": {
            "certificate":
                True
        },
        "tags": [
            "plan-registry-cert"
        ],
        "user":
            user,
    }

    if tenant_id is not None:
        payload[
            "tenantId"
        ] = tenant_id

    if plan_id is not None:
        payload[
            "plan_id"
        ] = plan_id

    return payload


def _stored_payload(
    collection: Collection[
        dict[
            str,
            Any,
        ]
    ],
    plan_id: str,
) -> dict[
    str,
    Any,
]:
    document = (
        collection.find_one(
            {
                "plan_id":
                    plan_id
            }
        )
    )

    if document is None:
        raise AssertionError(
            "persisted plan missing"
        )

    payload = dict(
        document
    )

    payload.pop(
        "_id",
        None,
    )

    payload.pop(
        "_registry_revision",
        None,
    )

    return payload


@pytest.fixture(
    scope="module"
)
def mongo_context() -> Iterator[
    _MongoContext
]:
    """Bind PlanRegistry to one isolated actual-Mongo certification database."""

    client: MongoClient[
        Any
    ] = MongoClient(
        TEST_MONGO_URI,
        serverSelectionTimeoutMS=5000,
    )

    client.admin.command(
        "ping"
    )

    hello = (
        client.admin.command(
            "hello"
        )
    )

    if (
        hello.get(
            "setName"
        )
        != EXPECTED_REPLICA_SET
    ):
        raise RuntimeError(
            "PLAN_CERT_WRONG_MONGO_TOPOLOGY"
        )

    if (
        hello.get(
            "isWritablePrimary"
        )
        is not True
    ):
        raise RuntimeError(
            "PLAN_CERT_MONGO_NOT_PRIMARY"
        )

    database_name = (
        "wilsy_plan_cert_"
        + uuid.uuid4().hex
    )

    database = client[
        database_name
    ]

    collection: Collection[
        dict[
            str,
            Any,
        ]
    ] = (
        database.get_collection(
            "plans",
            write_concern=
                WriteConcern(
                    w="majority",
                    j=True,
                ),
            read_concern=
                ReadConcern(
                    "majority"
                ),
        )
    )

    original_collection = (
        registry.plans_collection
    )

    registry.plans_collection = (
        collection
    )

    PlanRegistry._ensure_indexes()

    collection.delete_many(
        {}
    )

    context = _MongoContext(
        client=client,
        collection=collection,
        database_name=
            database_name,
        database_uri=
            _database_uri(
                TEST_MONGO_URI,
                database_name,
            ),
    )

    try:
        yield context

    finally:
        registry.plans_collection = (
            original_collection
        )

        client.drop_database(
            database_name
        )

        assert (
            database_name
            not in client.list_database_names()
        )

        client.close()


@pytest.fixture(
    autouse=True
)
def clean_collection(
    mongo_context: _MongoContext,
) -> Iterator[
    None
]:
    """Ensure every certificate starts and ends with empty Mongo truth."""

    mongo_context.collection.delete_many(
        {}
    )

    yield

    mongo_context.collection.delete_many(
        {}
    )


def test_real_mongo_version_topology_health_and_index_contract(
    mongo_context: _MongoContext,
) -> None:
    assert (
        PLAN_REGISTRY_VERSION
        == "v1.2.0-EXACT-TENANT-SCOPE"
    )

    assert (
        TEST_VERSION
        == "v1.1.2-PLAN-REGISTRY-SELF-VERSION-ALIGNMENT-CERT"
    )

    hello = (
        mongo_context.client
        .admin
        .command(
            "hello"
        )
    )

    assert (
        hello.get(
            "setName"
        )
        == EXPECTED_REPLICA_SET
    )

    assert (
        hello.get(
            "isWritablePrimary"
        )
        is True
    )

    health = (
        PlanRegistry
        .health_check()
    )

    assert (
        health[
            "status"
        ]
        == "OPERATIONAL"
    )

    assert (
        health[
            "version"
        ]
        == PLAN_REGISTRY_VERSION
    )

    assert (
        health[
            "store_type"
        ]
        == "mongo"
    )

    assert (
        health[
            "plan_count"
        ]
        == 0
    )

    assert set(
        health[
            "required_indexes"
        ]
    ) == _EXPECTED_INDEXES

    assert set(
        health[
            "observed_indexes"
        ]
    ) == _EXPECTED_INDEXES

    assert (
        health[
            "write_concern"
        ]
        == "majority+journal"
    )

    assert (
        health[
            "read_concern"
        ]
        == "majority"
    )

    information = (
        mongo_context.collection
        .index_information()
    )

    assert (
        information[
            "plan_id_unique"
        ][
            "unique"
        ]
        is True
    )

    assert (
        information[
            "idempotency_key_unique"
        ][
            "unique"
        ]
        is True
    )


def test_real_mongo_create_persists_exact_canonical_plan_evidence(
    mongo_context: _MongoContext,
) -> None:
    result = (
        PlanRegistry.create(
            _payload(
                idempotency_key=
                    "PLAN-CREATE-001",
                tenant_id=
                    "TENANT-A",
                plan_id=
                    "WILSYPLAN-A1A1A1A1",
            )
        )
    )

    assert (
        result[
            "success"
        ]
        is True
    )

    plan = result[
        "plan"
    ]

    assert isinstance(
        plan,
        PlanEntity,
    )

    persisted = _stored_payload(
        mongo_context.collection,
        plan.plan_id,
    )

    assert (
        persisted
        == plan.to_dict()
    )

    hydrated = (
        PlanEntity.from_dict(
            persisted
        )
    )

    assert (
        hydrated
        == plan
    )

    assert (
        plan.audit_trail[
            -1
        ].action
        == AuditAction.CREATE
    )

    assert (
        plan.audit_trail[
            -1
        ].user
        == "PLAN-MONGO-CERT"
    )

    assert (
        len(
            plan.state_history
        )
        == 1
    )


def test_real_mongo_idempotency_is_globally_unique_across_tenants(
    mongo_context: _MongoContext,
) -> None:
    first = (
        PlanRegistry.create(
            _payload(
                idempotency_key=
                    "GLOBAL-IDEMP-001",
                tenant_id=
                    "TENANT-A",
                plan_id=
                    "WILSYPLAN-B1B1B1B1",
            )
        )
    )

    second = (
        PlanRegistry.create(
            _payload(
                idempotency_key=
                    "GLOBAL-IDEMP-001",
                tenant_id=
                    "TENANT-B",
                plan_id=
                    "WILSYPLAN-B2B2B2B2",
            )
        )
    )

    assert (
        first[
            "success"
        ]
        is True
    )

    assert (
        second[
            "success"
        ]
        is False
    )

    assert (
        "already exists"
        in second[
            "error"
        ]
    )

    assert (
        mongo_context.collection
        .count_documents(
            {}
        )
        == 1
    )


def test_real_mongo_plan_id_is_globally_unique(
    mongo_context: _MongoContext,
) -> None:
    first = (
        PlanRegistry.create(
            _payload(
                idempotency_key=
                    "PLAN-ID-001",
                plan_id=
                    "WILSYPLAN-C1C1C1C1",
            )
        )
    )

    second = (
        PlanRegistry.create(
            _payload(
                idempotency_key=
                    "PLAN-ID-002",
                plan_id=
                    "WILSYPLAN-C1C1C1C1",
            )
        )
    )

    assert (
        first[
            "success"
        ]
        is True
    )

    assert (
        second[
            "success"
        ]
        is False
    )

    assert (
        "Plan ID"
        in second[
            "error"
        ]
        or "Duplicate"
        in second[
            "error"
        ]
    )

    assert (
        mongo_context.collection
        .count_documents(
            {}
        )
        == 1
    )


def test_real_mongo_get_preserves_global_and_tenant_scope_semantics() -> None:
    global_result = (
        PlanRegistry.create(
            _payload(
                idempotency_key=
                    "SCOPE-GLOBAL",
                plan_id=
                    "WILSYPLAN-D1D1D1D1",
            )
        )
    )

    tenant_result = (
        PlanRegistry.create(
            _payload(
                idempotency_key=
                    "SCOPE-A",
                tenant_id=
                    "TENANT-A",
                plan_id=
                    "WILSYPLAN-D2D2D2D2",
            )
        )
    )

    assert (
        global_result[
            "success"
        ]
        is True
    )

    assert (
        tenant_result[
            "success"
        ]
        is True
    )

    global_id = (
        global_result[
            "plan"
        ].plan_id
    )

    tenant_plan_id = (
        tenant_result[
            "plan"
        ].plan_id
    )

    assert (
        PlanRegistry.get(
            global_id,
            tenant_id=
                "TENANT-B",
        )
        is not None
    )

    assert (
        PlanRegistry.get(
            tenant_plan_id,
            tenant_id=
                "TENANT-A",
        )
        is not None
    )

    assert (
        PlanRegistry.get(
            tenant_plan_id,
            tenant_id=
                "TENANT-B",
        )
        is None
    )

    assert (
        PlanRegistry.get(
            tenant_plan_id
        )
        is not None
    )

    assert (
        PlanRegistry.get(
            "WILSYPLAN-FFFFFFFF"
        )
        is None
    )


def test_real_mongo_list_preserves_scope_filters_and_pagination() -> None:
    commands = (
        _payload(
            name="Global Pro",
            idempotency_key=
                "LIST-GLOBAL",
            plan_type=
                "PROFESSIONAL",
            plan_id=
                "WILSYPLAN-E1E1E1E1",
        ),
        _payload(
            name="Tenant A Enterprise",
            idempotency_key=
                "LIST-A-ENTERPRISE",
            tenant_id=
                "TENANT-A",
            plan_type=
                "ENTERPRISE",
            plan_id=
                "WILSYPLAN-E2E2E2E2",
        ),
        _payload(
            name="Tenant A Inactive",
            idempotency_key=
                "LIST-A-INACTIVE",
            tenant_id=
                "TENANT-A",
            plan_type=
                "PROFESSIONAL",
            active=False,
            plan_id=
                "WILSYPLAN-E3E3E3E3",
        ),
        _payload(
            name="Tenant B Pro",
            idempotency_key=
                "LIST-B",
            tenant_id=
                "TENANT-B",
            plan_type=
                "PROFESSIONAL",
            plan_id=
                "WILSYPLAN-E4E4E4E4",
        ),
    )

    for command in commands:
        result = (
            PlanRegistry.create(
                command
            )
        )

        assert (
            result[
                "success"
            ]
            is True
        )

    tenant_a = (
        PlanRegistry.list(
            tenant_id=
                "TENANT-A"
        )
    )

    assert (
        tenant_a[
            "total"
        ]
        == 3
    )

    active = (
        PlanRegistry.list(
            tenant_id=
                "TENANT-A",
            active=True,
        )
    )

    assert (
        active[
            "total"
        ]
        == 2
    )

    professional = (
        PlanRegistry.list(
            tenant_id=
                "TENANT-A",
            plan_type=
                PlanTiers.PROFESSIONAL,
        )
    )

    assert (
        professional[
            "total"
        ]
        == 2
    )

    page = (
        PlanRegistry.list(
            tenant_id=
                "TENANT-A",
            page=2,
            limit=1,
        )
    )

    assert (
        len(
            page[
                "items"
            ]
        )
        == 1
    )

    assert (
        page[
            "total"
        ]
        == 3
    )

    assert (
        page[
            "pages"
        ]
        == 3
    )


def test_real_mongo_update_persists_version_history_and_operator_audit(
    mongo_context: _MongoContext,
) -> None:
    created = (
        PlanRegistry.create(
            _payload(
                idempotency_key=
                    "UPDATE-001",
                tenant_id=
                    "TENANT-A",
                plan_id=
                    "WILSYPLAN-F1F1F1F1",
            )
        )
    )

    assert (
        created[
            "success"
        ]
        is True
    )

    before = created[
        "plan"
    ]

    updated = (
        PlanRegistry.update(
            before.plan_id,
            {
                "price":
                    799,
                "features": [
                    "crm.core",
                    "legal.documents",
                    "ai.wilsy",
                ],
                "user":
                    "OPERATOR",
            },
            tenant_id=
                "TENANT-A",
        )
    )

    assert (
        updated[
            "success"
        ]
        is True
    )

    plan = updated[
        "plan"
    ]

    assert (
        plan.price
        == 799.0
    )

    assert (
        plan.catalogue_version
        == 2
    )

    assert (
        len(
            plan.state_history
        )
        == 2
    )

    assert (
        len(
            plan.state_proof_lineage
        )
        == 2
    )

    assert (
        plan.audit_trail[
            -1
        ].user
        == "OPERATOR"
    )

    assert (
        "user"
        not in plan.to_dict()
    )

    persisted = _stored_payload(
        mongo_context.collection,
        plan.plan_id,
    )

    assert (
        persisted
        == plan.to_dict()
    )

    reloaded = (
        PlanRegistry.get(
            plan.plan_id,
            tenant_id=
                "TENANT-A",
        )
    )

    assert (
        reloaded
        == plan
    )


def test_real_mongo_stale_compare_and_swap_fails_closed(
    mongo_context: _MongoContext,
) -> None:
    created = (
        PlanRegistry.create(
            _payload(
                idempotency_key=
                    "CAS-001",
                plan_id=
                    "WILSYPLAN-A2A2A2A2",
            )
        )
    )

    assert (
        created[
            "success"
        ]
        is True
    )

    stale = (
        PlanRegistry._get_record(
            created[
                "plan"
            ].plan_id
        )
    )

    assert stale is not None

    before = (
        mongo_context.collection
        .find_one(
            {
                "_id":
                    stale.mongo_id
            }
        )
    )

    assert before is not None

    assert (
        before[
            "_registry_revision"
        ]
        == 1
        == stale.registry_revision
    )

    # Exact P2R1 Codex reproduction:
    # advance only storage generation; leave former four CAS values untouched.
    changed = (
        mongo_context.collection
        .update_one(
            {
                "_id":
                    stale.mongo_id
            },
            {
                "$inc": {
                    "_registry_revision":
                        1
                }
            },
        )
    )

    assert (
        changed.matched_count
        == 1
    )

    stale_update = (
        stale.plan
        .update(
            {
                "price":
                    900
            }
        )
        .add_audit_entry(
            AuditAction.UPDATE,
            user="STALE",
            reason=
                "stale storage generation",
        )
    )

    with pytest.raises(
        RuntimeError,
        match=
            "PLAN_REGISTRY_CONCURRENT_MUTATION",
    ):
        PlanRegistry._replace_current(
            stale,
            stale_update,
        )

    persisted = (
        mongo_context.collection
        .find_one(
            {
                "_id":
                    stale.mongo_id
            }
        )
    )

    assert persisted is not None

    assert (
        persisted[
            "_registry_revision"
        ]
        == 2
    )

    canonical = dict(
        persisted
    )

    canonical.pop(
        "_id"
    )

    canonical.pop(
        "_registry_revision"
    )

    assert (
        canonical
        == stale.plan.to_dict()
    )


def test_real_mongo_archive_and_reactivate_are_durable_lifecycle_events() -> None:
    created = (
        PlanRegistry.create(
            _payload(
                idempotency_key=
                    "LIFECYCLE-001",
                tenant_id=
                    "TENANT-A",
                plan_id=
                    "WILSYPLAN-B2B2B2B2",
            )
        )
    )

    assert (
        created[
            "success"
        ]
        is True
    )

    plan_id = (
        created[
            "plan"
        ].plan_id
    )

    assert (
        PlanRegistry.archive(
            plan_id,
            tenant_id=
                "TENANT-A",
        )
        is True
    )

    archived = (
        PlanRegistry.get(
            plan_id,
            tenant_id=
                "TENANT-A",
        )
    )

    assert (
        archived
        is not None
    )

    assert (
        archived.active
        is False
    )

    assert (
        archived.catalogue_version
        == 2
    )

    assert (
        archived.audit_trail[
            -1
        ].action
        == AuditAction.ARCHIVE
    )

    assert (
        PlanRegistry.reactivate(
            plan_id,
            tenant_id=
                "TENANT-A",
        )
        is True
    )

    active = (
        PlanRegistry.get(
            plan_id,
            tenant_id=
                "TENANT-A",
        )
    )

    assert (
        active
        is not None
    )

    assert (
        active.active
        is True
    )

    assert (
        active.catalogue_version
        == 3
    )

    assert (
        active.audit_trail[
            -1
        ].action
        == AuditAction.REACTIVATE
    )

    proof_before_noop = (
        active.integrity_root
    )

    assert (
        PlanRegistry.reactivate(
            plan_id,
            tenant_id=
                "TENANT-A",
        )
        is True
    )

    after_noop = (
        PlanRegistry.get(
            plan_id,
            tenant_id=
                "TENANT-A",
        )
    )

    assert (
        after_noop
        is not None
    )

    assert (
        after_noop.integrity_root
        == proof_before_noop
    )


def test_real_mongo_genuine_absence_is_distinct_from_failure() -> None:
    missing = (
        "WILSYPLAN-C2C2C2C2"
    )

    assert (
        PlanRegistry.get(
            missing
        )
        is None
    )

    assert (
        PlanRegistry.archive(
            missing
        )
        is False
    )

    assert (
        PlanRegistry.reactivate(
            missing
        )
        is False
    )


def test_real_mongo_invalid_persisted_truth_fails_get_closed(
    mongo_context: _MongoContext,
) -> None:
    created = (
        PlanRegistry.create(
            _payload(
                idempotency_key=
                    "CORRUPT-GET",
                plan_id=
                    "WILSYPLAN-D2D2D2D2",
            )
        )
    )

    assert (
        created[
            "success"
        ]
        is True
    )

    plan_id = (
        created[
            "plan"
        ].plan_id
    )

    mongo_context.collection.update_one(
        {
            "plan_id":
                plan_id
        },
        {
            "$set": {
                "proof_hash":
                    "A" * 128
            }
        },
    )

    with pytest.raises(
        ValueError
    ):
        PlanRegistry.get(
            plan_id
        )


def test_real_mongo_invalid_persisted_truth_cannot_masquerade_as_empty_list(
    mongo_context: _MongoContext,
) -> None:
    created = (
        PlanRegistry.create(
            _payload(
                idempotency_key=
                    "CORRUPT-LIST",
                plan_id=
                    "WILSYPLAN-E2E2E2E2",
            )
        )
    )

    assert (
        created[
            "success"
        ]
        is True
    )

    mongo_context.collection.update_one(
        {
            "plan_id":
                created[
                    "plan"
                ].plan_id
        },
        {
            "$unset": {
                "state_history":
                    ""
            }
        },
    )

    with pytest.raises(
        ValueError,
        match=
            "state history",
    ):
        PlanRegistry.list()


def test_real_mongo_legacy_or_unversioned_material_blocks_current_catalogue_authority(
    mongo_context: _MongoContext,
) -> None:
    mongo_context.collection.insert_one(
        {
            "plan_id":
                "WILSYPLAN-F2F2F2F2",
            "name":
                "Legacy Plan",
            "price":
                100,
            "currency":
                "ZAR",
            "billing_frequency":
                "monthly",
            "plan_type":
                "PROFESSIONAL",
            "idempotency_key":
                "LEGACY-PERSISTED-001",
            "_registry_revision":
                1,
            "created_at":
                "2026-01-01T00:00:00+00:00",
            "updated_at":
                "2026-01-01T00:00:00+00:00",
        }
    )

    with pytest.raises(
        ValueError,
        match=
            "explicit legacy migration",
    ):
        PlanRegistry.list()

    create_attempt = (
        PlanRegistry.create(
            _payload(
                idempotency_key=
                    "AFTER-LEGACY",
                plan_id=
                    "WILSYPLAN-A3A3A3A3",
            )
        )
    )

    assert (
        create_attempt[
            "success"
        ]
        is False
    )

    assert (
        "explicit legacy migration"
        in create_attempt[
            "error"
        ]
    )


def test_real_mongo_outage_cannot_masquerade_as_absence_or_empty_truth(
    mongo_context: _MongoContext,
) -> None:
    dead_client: MongoClient[
        Any
    ] = MongoClient(
        "mongodb://127.0.0.1:1/"
        "?directConnection=true",
        serverSelectionTimeoutMS=100,
        connectTimeoutMS=100,
        socketTimeoutMS=100,
    )

    dead_collection: Collection[
        dict[
            str,
            Any,
        ]
    ] = (
        dead_client[
            "wilsy_plan_dead"
        ].get_collection(
            "plans",
            write_concern=
                WriteConcern(
                    w="majority",
                    j=True,
                ),
            read_concern=
                ReadConcern(
                    "majority"
                ),
        )
    )

    original = (
        registry.plans_collection
    )

    registry.plans_collection = (
        dead_collection
    )

    try:
        with pytest.raises(
            PyMongoError
        ):
            PlanRegistry.get(
                "WILSYPLAN-B3B3B3B3"
            )

        with pytest.raises(
            PyMongoError
        ):
            PlanRegistry.list()

        with pytest.raises(
            PyMongoError
        ):
            PlanRegistry.archive(
                "WILSYPLAN-B3B3B3B3"
            )

        with pytest.raises(
            PyMongoError
        ):
            PlanRegistry.reactivate(
                "WILSYPLAN-B3B3B3B3"
            )

        create_result = (
            PlanRegistry.create(
                _payload(
                    idempotency_key=
                        "OUTAGE-CREATE",
                    plan_id=
                        "WILSYPLAN-B3B3B3B3",
                )
            )
        )

        assert (
            create_result[
                "success"
            ]
            is False
        )

        update_result = (
            PlanRegistry.update(
                "WILSYPLAN-B3B3B3B3",
                {
                    "price":
                        999
                },
            )
        )

        assert (
            update_result[
                "success"
            ]
            is False
        )

        health = (
            PlanRegistry.health_check()
        )

        assert (
            health[
                "status"
            ]
            == "UNAVAILABLE"
        )

    finally:
        registry.plans_collection = (
            original
        )

        dead_client.close()

    assert (
        mongo_context.collection
        .count_documents(
            {}
        )
        == 0
    )


def test_real_mongo_independent_process_restart_durability(
    mongo_context: _MongoContext,
) -> None:
    created = (
        PlanRegistry.create(
            _payload(
                idempotency_key=
                    "PROCESS-RESTART",
                tenant_id=
                    "TENANT-A",
                plan_id=
                    "WILSYPLAN-C3C3C3C3",
            )
        )
    )

    assert (
        created[
            "success"
        ]
        is True
    )

    plan = created[
        "plan"
    ]

    code = (
        "from tools.eos.saas.billing.plan_registry "
        "import PlanRegistry; "
        f"p=PlanRegistry.get('{plan.plan_id}', "
        "tenant_id='TENANT-A'); "
        "assert p is not None; "
        f"assert p.proof_hash=='{plan.proof_hash}'; "
        f"assert p.integrity_root=='{plan.integrity_root}'; "
        "assert p.catalogue_version==1; "
        "print('INDEPENDENT_PROCESS_PLAN_READ=PASS')"
    )

    environment = dict(
        os.environ
    )

    environment[
        "WILSY_PLAN_MONGO_URI"
    ] = (
        mongo_context.database_uri
    )

    environment.pop(
        "WILSY_PLAN_MONGO_DATABASE",
        None,
    )

    environment[
        "PYTHONDONTWRITEBYTECODE"
    ] = "1"

    completed = (
        subprocess.run(
            [
                sys.executable,
                "-B",
                "-c",
                code,
            ],
            cwd=_ROOT,
            env=environment,
            text=True,
            stdout=
                subprocess.PIPE,
            stderr=
                subprocess.PIPE,
            check=False,
        )
    )

    if (
        completed.returncode
        != 0
    ):
        raise AssertionError(
            "independent process failed:\n"
            + completed.stdout
            + "\n"
            + completed.stderr
        )

    assert (
        "INDEPENDENT_PROCESS_PLAN_READ=PASS"
        in completed.stdout
    )


def test_real_mongo_registry_price_passthrough_and_user_context_compatibility(
    mongo_context: _MongoContext,
) -> None:
    lossy = (
        PlanRegistry.create(
            _payload(
                price=
                    Decimal(
                        "1.0000000000000001"
                    ),
                idempotency_key=
                    "PRECISION-REJECT",
                plan_id=
                    "WILSYPLAN-D3D3D3D3",
            )
        )
    )

    assert (
        lossy[
            "success"
        ]
        is False
    )

    assert (
        mongo_context.collection
        .count_documents(
            {}
        )
        == 0
    )

    created = (
        PlanRegistry.create(
            _payload(
                price=100,
                idempotency_key=
                    "USER-CONTEXT",
                plan_id=
                    "WILSYPLAN-D3D3D3D3",
            )
        )
    )

    assert (
        created[
            "success"
        ]
        is True
    )

    updated = (
        PlanRegistry.update(
            created[
                "plan"
            ].plan_id,
            {
                "price":
                    200,
                "user":
                    "OPERATOR",
            },
        )
    )

    assert (
        updated[
            "success"
        ]
        is True
    )

    plan = updated[
        "plan"
    ]

    assert (
        plan.price
        == 200.0
    )

    assert (
        plan.catalogue_version
        == 2
    )

    assert (
        plan.audit_trail[
            -1
        ].user
        == "OPERATOR"
    )

    assert (
        "user"
        not in plan.to_dict()
    )


def test_real_mongo_source_has_no_in_memory_or_kernel_db_authority() -> None:
    source = (
        Path(
            registry.__file__
        ).read_text(
            encoding="utf-8"
        )
    )

    assert (
        "kernel.db"
        not in source
    )

    assert (
        "cls._plans"
        not in source
    )

    assert (
        "_plans:"
        not in source
    )

    assert (
        "plans_collection"
        in source
    )

    assert (
        "_REGISTRY_REVISION_FIELD"
        in source
    )

    assert (
        "PLAN_REGISTRY_NONCANONICAL_DOCUMENT"
        in source
    )

    assert (
        source.count(
            "logger.info("
        )
        == 1
    )

    assert (
        "_DEBUG_LOGGING"
        in source
    )

    assert (
        "REAL MONGODB"
        in source
    )

    assert (
        "Kennel EOS remains the exclusive"
        in source
    )


def test_real_mongo_transport_revision_is_required_and_not_domain_state(
    mongo_context: _MongoContext,
) -> None:
    created = (
        PlanRegistry.create(
            _payload(
                idempotency_key=
                    "TRANSPORT-REVISION",
                plan_id=
                    "WILSYPLAN-E3E3E3E3",
            )
        )
    )

    assert (
        created[
            "success"
        ]
        is True
    )

    plan = created[
        "plan"
    ]

    document = (
        mongo_context.collection
        .find_one(
            {
                "plan_id":
                    plan.plan_id
            }
        )
    )

    assert document is not None

    assert (
        "_id"
        in document
    )

    assert (
        document[
            "_registry_revision"
        ]
        == 1
    )

    assert (
        "_id"
        not in plan.to_dict()
    )

    assert (
        "_registry_revision"
        not in plan.to_dict()
    )

    mongo_context.collection.update_one(
        {
            "_id":
                document[
                    "_id"
                ]
        },
        {
            "$unset": {
                "_registry_revision":
                    ""
            }
        },
    )

    with pytest.raises(
        ValueError,
        match=
            "PLAN_REGISTRY_REVISION_INVALID",
    ):
        PlanRegistry.get(
            plan.plan_id
        )


def test_real_mongo_noncanonical_extra_field_fails_closed(
    mongo_context: _MongoContext,
) -> None:
    created = (
        PlanRegistry.create(
            _payload(
                idempotency_key=
                    "NONCANONICAL-FIELD",
                plan_id=
                    "WILSYPLAN-F3F3F3F3",
            )
        )
    )

    assert (
        created[
            "success"
        ]
        is True
    )

    plan_id = (
        created[
            "plan"
        ].plan_id
    )

    mongo_context.collection.update_one(
        {
            "plan_id":
                plan_id
        },
        {
            "$set": {
                "competingAuthority":
                    "MUST-FAIL-CLOSED"
            }
        },
    )

    with pytest.raises(
        ValueError,
        match=
            "PLAN_REGISTRY_NONCANONICAL_DOCUMENT",
    ):
        PlanRegistry.get(
            plan_id
        )

    with pytest.raises(
        ValueError,
        match=
            "PLAN_REGISTRY_NONCANONICAL_DOCUMENT",
    ):
        PlanRegistry.list()

    health = (
        PlanRegistry.health_check()
    )

    assert (
        health[
            "status"
        ]
        == "UNAVAILABLE"
    )


def test_real_mongo_cas_binds_immutable_mongo_identity(
    mongo_context: _MongoContext,
) -> None:
    created = (
        PlanRegistry.create(
            _payload(
                idempotency_key=
                    "CAS-MONGO-ID",
                plan_id=
                    "WILSYPLAN-A4A4A4A4",
            )
        )
    )

    assert (
        created[
            "success"
        ]
        is True
    )

    stale = (
        PlanRegistry._get_record(
            created[
                "plan"
            ].plan_id
        )
    )

    assert stale is not None

    canonical = (
        stale.plan.to_dict()
    )

    deleted = (
        mongo_context.collection
        .delete_one(
            {
                "_id":
                    stale.mongo_id
            }
        )
    )

    assert (
        deleted.deleted_count
        == 1
    )

    replacement = dict(
        canonical
    )

    replacement[
        "_registry_revision"
    ] = (
        stale.registry_revision
    )

    inserted = (
        mongo_context.collection
        .insert_one(
            replacement
        )
    )

    assert (
        inserted.inserted_id
        != stale.mongo_id
    )

    stale_update = (
        stale.plan
        .update(
            {
                "price":
                    901
            }
        )
        .add_audit_entry(
            AuditAction.UPDATE,
            user="STALE-ID",
            reason=
                "stale Mongo identity",
        )
    )

    with pytest.raises(
        RuntimeError,
        match=
            "PLAN_REGISTRY_CONCURRENT_MUTATION",
    ):
        PlanRegistry._replace_current(
            stale,
            stale_update,
        )



def test_billing_plans_consumer_converges_on_plan_registry_fail_closed() -> None:
    billing_path = (
        _ROOT
        / "tools/eos/api/billing_router.py"
    )

    source = billing_path.read_text(
        encoding="utf-8"
    )

    tree = ast.parse(
        source
    )

    matches = [
        node
        for node in ast.walk(
            tree
        )
        if (
            isinstance(
                node,
                ast.AsyncFunctionDef,
            )
            and node.name
            == "get_billing_plans"
        )
    ]

    assert (
        len(
            matches
        )
        == 1
    )

    function_source = (
        ast.get_source_segment(
            source,
            matches[0],
        )
        or ""
    )

    assert (
        "PlanRegistry.list"
        in function_source
    )

    assert (
        "HTTP_503_SERVICE_UNAVAILABLE"
        in function_source
    )

    assert (
        "PLAN_CATALOGUE_CHANGED_DURING_READ"
        in function_source
    )

    for forbidden in (
        "_require_db",
        '["plans"]',
        "['plans']",
        "PlanEntity.from_dict",
        "PLAN_ENTITY_CONVERSION",
        "minimal =",
    ):
        assert (
            forbidden
            not in function_source
        )

    assert (
        "from ..saas.billing.plan_registry import PlanRegistry"
        in source
    )

    assert (
        "from ..saas.domain.plan import PlanEntity"
        not in source
    )



def test_real_mongo_exact_tenant_opt_in_denies_global_and_neighbor_mutation() -> None:
    """Exact tenant mode excludes global/neighbor Plans without changing defaults."""
    global_result = PlanRegistry.create(
        _payload(
            name="Global Exact Scope",
            idempotency_key=
                "EXACT-GLOBAL",
            plan_id=
                "WILSYPLAN-X1X1X1X1",
        )
    )

    tenant_a_result = PlanRegistry.create(
        _payload(
            name="Tenant A Exact Scope",
            idempotency_key=
                "EXACT-TENANT-A",
            tenant_id=
                "TENANT-A",
            plan_id=
                "WILSYPLAN-X2X2X2X2",
        )
    )

    tenant_b_result = PlanRegistry.create(
        _payload(
            name="Tenant B Exact Scope",
            idempotency_key=
                "EXACT-TENANT-B",
            tenant_id=
                "TENANT-B",
            plan_id=
                "WILSYPLAN-X3X3X3X3",
        )
    )

    assert global_result["success"] is True
    assert tenant_a_result["success"] is True
    assert tenant_b_result["success"] is True

    global_plan = global_result["plan"]
    tenant_a_plan = tenant_a_result["plan"]
    tenant_b_plan = tenant_b_result["plan"]

    # Default compatibility remains unchanged.
    assert (
        PlanRegistry.get(
            global_plan.plan_id,
            tenant_id="TENANT-A",
        )
        is not None
    )

    # Exact scope admits only exact tenant ownership.
    assert (
        PlanRegistry.get(
            global_plan.plan_id,
            tenant_id="TENANT-A",
            exact_tenant=True,
        )
        is None
    )

    assert (
        PlanRegistry.get(
            tenant_a_plan.plan_id,
            tenant_id="TENANT-A",
            exact_tenant=True,
        )
        is not None
    )

    assert (
        PlanRegistry.get(
            tenant_b_plan.plan_id,
            tenant_id="TENANT-A",
            exact_tenant=True,
        )
        is None
    )

    update_global = PlanRegistry.update(
        global_plan.plan_id,
        {
            "price":
                1234.0
        },
        tenant_id="TENANT-A",
        exact_tenant=True,
    )

    assert update_global["success"] is False
    assert update_global["error"] == "Plan not found"

    assert (
        PlanRegistry.archive(
            global_plan.plan_id,
            tenant_id="TENANT-A",
            exact_tenant=True,
        )
        is False
    )

    surviving_global = PlanRegistry.get(
        global_plan.plan_id
    )

    assert surviving_global is not None
    assert surviving_global.active is True


def test_real_mongo_exact_tenant_list_filters_before_pagination() -> None:
    """Exact filtering precedes total/pages/pagination and excludes global Plans."""
    commands = (
        _payload(
            name="Exact Global",
            idempotency_key=
                "EXACT-LIST-GLOBAL",
            plan_id=
                "WILSYPLAN-Y1Y1Y1Y1",
        ),
        _payload(
            name="Exact Tenant A One",
            idempotency_key=
                "EXACT-LIST-A1",
            tenant_id=
                "TENANT-A",
            plan_id=
                "WILSYPLAN-Y2Y2Y2Y2",
        ),
        _payload(
            name="Exact Tenant A Two",
            idempotency_key=
                "EXACT-LIST-A2",
            tenant_id=
                "TENANT-A",
            plan_id=
                "WILSYPLAN-Y3Y3Y3Y3",
        ),
        _payload(
            name="Exact Tenant B",
            idempotency_key=
                "EXACT-LIST-B",
            tenant_id=
                "TENANT-B",
            plan_id=
                "WILSYPLAN-Y4Y4Y4Y4",
        ),
    )

    for command in commands:
        created = PlanRegistry.create(
            command
        )
        assert created["success"] is True

    first = PlanRegistry.list(
        tenant_id="TENANT-A",
        page=1,
        limit=1,
        exact_tenant=True,
    )

    second = PlanRegistry.list(
        tenant_id="TENANT-A",
        page=2,
        limit=1,
        exact_tenant=True,
    )

    assert first["total"] == 2
    assert first["pages"] == 2
    assert len(first["items"]) == 1

    assert second["total"] == 2
    assert second["pages"] == 2
    assert len(second["items"]) == 1

    observed = {
        first["items"][0].tenant_id,
        second["items"][0].tenant_id,
    }

    assert observed == {
        "TENANT-A"
    }


"""
INSTITUTIONAL CERTIFICATION SEAL — WILSY OS PLANREGISTRY REAL-MONGO

Status:
    DIRECT REAL-WORLD CERTIFICATE — ACTUAL MONGODB REQUIRED

Version:
    v1.1.2-PLAN-REGISTRY-SELF-VERSION-ALIGNMENT-CERT

Production owner:
    tools/eos/saas/billing/plan_registry.py

Commercial truth:
    tools/eos/saas/domain/plan.py

Topology:
    Defaults only to local port 27027 / wilsyVendorCertRS.

Persistence:
    UUID-isolated actual MongoDB, majority read/write concern.

Failure semantics:
    Outage and invalid evidence cannot become absence, empty catalogue or false.

Authority:
    Catalogue persistence only. No membership, permission, entitlement,
    HTTP authorization or financial execution authority.

Financial execution:
    NONE — Kennel EOS remains exclusive.

Certification date:
    2026-09-03

WILSY OS — ALL OR NOTHING.
"""
