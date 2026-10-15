"""
TITLE: WILSY OS Legal Principal Operating Role Binding Registry Real-Mongo Certificate
VERSION: v1.0.1-CX27-R5B-R4-LEGAL-PRINCIPAL-OPERATING-ROLE-BINDING-REAL-MONGO
AUTHORITY: Wilsy OS Core Governance / Python EOS Legal Operations.
CLASSIFICATION: SOVEREIGN REAL-MONGO CERTIFICATE
EPITOME: Physical immutable-registry durability certification.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tests/integration/test_legal_principal_operating_role_binding_registry_real_mongo.py
COLLABORATION / OWNERSHIP: CX27-D physical persistence and effective-window certificate only.
CERTIFICATION / UPDATE DATE: 2026-10-15
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2; ISO 27001.
SECURITY / PRIVACY POSTURE: UUID-isolated synthetic data; no production data, PII, or credentials.
TENANT BOUNDARY: Certifies exact tenant-scoped persistence and non-disclosure.
AUTHORITY BOUNDARY: Durability and window evidence only; no authentication, IAM, access, workforce, matter, workflow, or financial authority.
FINANCIAL AUTHORITY BOUNDARY: None; Kennel EOS exclusively executes or settles.
MONGO SCOPE: UUID-isolated disposable database only.
PRODUCTION DATABASE WRITE AUTHORITY: NONE.
CHANGELOG: v1.0.1 completes sovereign certificate metadata without changing test behavior.
"""


from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timedelta, timezone
import os
import uuid
from typing import Any, Iterator

import pytest
from pymongo import MongoClient
from pymongo.errors import PyMongoError

MONGO_URI = os.getenv(
    "TEST_VENDOR_MONGO_URI",
    "mongodb://127.0.0.1:27027/?replicaSet=wilsyVendorCertRS",
)

EXPECTED_REPLICA_SET = "wilsyVendorCertRS"

NOW = datetime(
    2026, 10, 13, 12, 0, 0, 123456,
    tzinfo=timezone.utc,
)

FORBIDDEN_AUTHORITY_KEYS = {
    "permission",
    "permissions",
    "operation",
    "operations",
    "iam",
    "authorization_role",
    "business_role",
    "matter_authority",
    "assignment",
    "work_assignment",
    "supervision",
    "billing_authority",
    "financial_authority",
    "financial_execution_authority",
}

def _client() -> MongoClient[Any]:
    client: MongoClient[Any] = MongoClient(
        MONGO_URI,
        serverSelectionTimeoutMS=5000,
        retryWrites=True,
        tz_aware=True,
    )
    hello = client.admin.command("hello")
    assert hello.get("setName") == EXPECTED_REPLICA_SET
    assert bool(
        hello.get(
            "isWritablePrimary",
            hello.get("ismaster", False),
        )
    )
    return client

def _commit(
    client: MongoClient[Any],
    registry: Any,
    value: Any,
) -> Any:
    with client.start_session() as session:
        session.start_transaction()
        result = registry.persist_revision(
            value,
            session=session,
        )
        session.commit_transaction()
        return result

def _read_revision(
    client: MongoClient[Any],
    registry: Any,
    tenant: str,
    identity: str,
    revision: int,
) -> Any:
    with client.start_session() as session:
        session.start_transaction()
        value = registry.get_revision(
            tenant,
            identity,
            revision,
            session=session,
        )
        session.abort_transaction()
        return value

def _index_map(collection: Any) -> dict[str, dict[str, Any]]:
    return {
        str(item["name"]): dict(item)
        for item in collection.list_indexes()
    }


from tools.eos.legal_operations.domain.legal_principal_operating_role_binding import (
    LegalPrincipalOperatingRoleBinding,
)
from tools.eos.legal_operations.registry.legal_principal_operating_role_binding_registry import (
    LegalPrincipalOperatingRoleBindingRegistry,
    RegistryConflictError,
    RegistryPersistedRecordInvalidError,
    RegistryTransactionRequiredError,
)


COLLECTION_NAME = "legal_principal_operating_role_bindings"


SOURCE_FP = "a" * 128

def make_value(
    *,
    revision: int = 1,
    when: datetime = NOW,
    predecessor: str | None = None,
    variant: str = "base",
    until: datetime | None = None,
) -> LegalPrincipalOperatingRoleBinding:
    return LegalPrincipalOperatingRoleBinding(
        tenant_id="tenant-r5b-principal",
        principal_operating_role_binding_id="principal-role-r5b-1",
        binding_revision=revision,
        principal_id="principal-r5b-1",
        operating_role_id="role-r5b-1",
        operating_role_revision=4,
        effective_from=when,
        effective_until=until,
        source_reference=f"r5b:{variant}:{revision}",
        source_evidence_fingerprint=SOURCE_FP,
        supersedes_fingerprint=predecessor,
    )



INDEX_EXPECTATIONS = (
    (
        "legal_principal_operating_role_bindings_identity_unique",
        (
            ("tenant_id", 1),
            ("principal_operating_role_binding_id", 1),
            ("binding_revision", 1),
        ),
        True,
    ),
    (
        "legal_principal_operating_role_bindings_fingerprint_unique",
        (
            ("tenant_id", 1),
            ("fingerprint", 1),
        ),
        True,
    ),
    (
        "legal_principal_operating_role_bindings_history",
        (
            ("tenant_id", 1),
            ("principal_operating_role_binding_id", 1),
            ("binding_revision", 1),
        ),
        False,
    ),
    (
        "legal_principal_operating_role_bindings_currentness",
        (
            ("tenant_id", 1),
            ("principal_operating_role_binding_id", 1),
            ("effective_from", 1),
            ("binding_revision", 1),
        ),
        False,
    ),
    (
        "legal_principal_operating_role_principal_history",
        (
            ("tenant_id", 1),
            ("principal_id", 1),
            ("effective_from", 1),
            ("binding_revision", 1),
        ),
        False,
    ),
    (
        "legal_principal_operating_role_role_history",
        (
            ("tenant_id", 1),
            ("operating_role_id", 1),
            ("operating_role_revision", 1),
            ("principal_id", 1),
            ("binding_revision", 1),
        ),
        False,
    ),
)


@pytest.fixture()
def mongo_context() -> Iterator[
    tuple[
        MongoClient[Any],
        Any,
        Any,
        LegalPrincipalOperatingRoleBindingRegistry,
    ]
]:
    client = _client()

    database_name = (
        "wilsy_cx27_r5b_r4_"
        + uuid.uuid4().hex
    )

    assert database_name != "wilsy"

    database = client[database_name]
    collection = database[COLLECTION_NAME]
    registry = LegalPrincipalOperatingRoleBindingRegistry(collection)

    registry.ensure_indexes()

    try:
        yield client, database, collection, registry
    finally:
        client.drop_database(database_name)
        client.close()


def test_real_topology_database_and_exact_index_metadata(
    mongo_context: tuple[
        MongoClient[Any],
        Any,
        Any,
        LegalPrincipalOperatingRoleBindingRegistry,
    ],
) -> None:
    client, database, collection, registry = mongo_context

    hello = client.admin.command("hello")
    assert hello.get("setName") == EXPECTED_REPLICA_SET
    assert database.name != "wilsy"
    assert database.name.startswith("wilsy_cx27_r5b_r4_")

    registry.ensure_indexes()

    indexes = _index_map(collection)

    expected_names = {
        "_id_",
        *(name for name, _keys, _unique in INDEX_EXPECTATIONS),
    }

    assert set(indexes) == expected_names

    for name, keys, unique in INDEX_EXPECTATIONS:
        assert dict(indexes[name]["key"]) == dict(keys)
        assert bool(indexes[name].get("unique", False)) is unique
        assert "expireAfterSeconds" not in indexes[name]

    assert all(
        "expireAfterSeconds" not in item
        for item in indexes.values()
    )


def test_real_transaction_required_abort_and_revision_one(
    mongo_context: tuple[
        MongoClient[Any],
        Any,
        Any,
        LegalPrincipalOperatingRoleBindingRegistry,
    ],
) -> None:
    client, _database, collection, registry = mongo_context
    first = make_value()

    with pytest.raises(RegistryTransactionRequiredError):
        registry.persist_revision(first, session=None)

    with client.start_session() as inactive:
        with pytest.raises(RegistryTransactionRequiredError):
            registry.persist_revision(
                first,
                session=inactive,
            )

    with client.start_session() as session:
        session.start_transaction()

        assert registry.persist_revision(
            first,
            session=session,
        ) == first

        assert collection.count_documents(
            {"tenant_id": first.tenant_id},
            session=session,
        ) == 1

        assert collection.count_documents(
            {"tenant_id": first.tenant_id}
        ) == 0

        session.abort_transaction()

    assert collection.count_documents(
        {"tenant_id": first.tenant_id}
    ) == 0

    assert _commit(
        client,
        registry,
        first,
    ) == first


def test_real_exact_replay_divergence_gap_and_bad_predecessor(
    mongo_context: tuple[
        MongoClient[Any],
        Any,
        Any,
        LegalPrincipalOperatingRoleBindingRegistry,
    ],
) -> None:
    client, _database, collection, registry = mongo_context
    first = make_value()

    _commit(client, registry, first)

    assert _commit(client, registry, first) == first

    assert collection.count_documents(
        {"tenant_id": first.tenant_id}
    ) == 1

    with pytest.raises(RegistryConflictError):
        _commit(
            client,
            registry,
            make_value(variant="divergent"),
        )

    with pytest.raises(RegistryConflictError):
        _commit(
            client,
            registry,
            make_value(
                revision=3,
                when=NOW + timedelta(days=3),
                predecessor=first.fingerprint,
            ),
        )

    with pytest.raises(RegistryConflictError):
        _commit(
            client,
            registry,
            make_value(
                revision=2,
                when=NOW + timedelta(days=1),
                predecessor="b" * 128,
            ),
        )


def test_real_contiguous_currentness_future_and_tenant_isolation(
    mongo_context: tuple[
        MongoClient[Any],
        Any,
        Any,
        LegalPrincipalOperatingRoleBindingRegistry,
    ],
) -> None:
    client, _database, _collection, registry = mongo_context
    first = make_value()

    _commit(client, registry, first)

    second = make_value(
        revision=2,
        when=NOW + timedelta(days=2),
        predecessor=first.fingerprint,
        variant="second",
    )

    _commit(client, registry, second)

    with client.start_session() as session:
        session.start_transaction()

        assert registry.resolve_current(
            first.tenant_id,
            getattr(first, "principal_operating_role_binding_id"),
            NOW + timedelta(days=1),
            session=session,
        ) == first

        assert registry.resolve_current(
            first.tenant_id,
            getattr(first, "principal_operating_role_binding_id"),
            NOW + timedelta(days=3),
            session=session,
        ) == second

        assert registry.get_history_if_any(
            "tenant-neighbor",
            getattr(first, "principal_operating_role_binding_id"),
            session=session,
        ) == ()

        session.abort_transaction()


def test_real_corruption_and_no_unrelated_authority_fields(
    mongo_context: tuple[
        MongoClient[Any],
        Any,
        Any,
        LegalPrincipalOperatingRoleBindingRegistry,
    ],
) -> None:
    client, _database, collection, registry = mongo_context
    first = make_value()

    _commit(client, registry, first)

    stored = collection.find_one(
        {"tenant_id": first.tenant_id}
    )

    assert stored is not None
    assert not (set(stored) & FORBIDDEN_AUTHORITY_KEYS)

    result = collection.update_one(
        {
            "tenant_id": first.tenant_id,
            "principal_operating_role_binding_id":
                getattr(first, "principal_operating_role_binding_id"),
            "binding_revision":
                getattr(first, "binding_revision"),
        },
        {
            "$set": {
                "fingerprint": "0" * 128,
            }
        },
    )

    assert result.modified_count == 1

    with client.start_session() as session:
        session.start_transaction()

        with pytest.raises(
            RegistryPersistedRecordInvalidError
        ):
            registry.get_revision(
                first.tenant_id,
                getattr(first, "principal_operating_role_binding_id"),
                getattr(first, "binding_revision"),
                session=session,
            )

        session.abort_transaction()


def test_real_competing_same_next_revision(
    mongo_context: tuple[
        MongoClient[Any],
        Any,
        Any,
        LegalPrincipalOperatingRoleBindingRegistry,
    ],
) -> None:
    client, database, collection, registry = mongo_context
    first = make_value()

    _commit(client, registry, first)

    second = make_value(
        revision=2,
        when=NOW + timedelta(days=1),
        predecessor=first.fingerprint,
        variant="race",
    )

    database_name = database.name

    def contender() -> str:
        local_client = _client()

        try:
            local_collection = (
                local_client[database_name][COLLECTION_NAME]
            )
            local_registry = LegalPrincipalOperatingRoleBindingRegistry(local_collection)

            with local_client.start_session() as session:
                session.start_transaction()

                try:
                    local_registry.persist_revision(
                        second,
                        session=session,
                    )
                    session.commit_transaction()
                    return "SUCCESS"

                except (
                    RegistryConflictError,
                    PyMongoError,
                ) as exc:
                    try:
                        session.abort_transaction()
                    except PyMongoError:
                        pass

                    return (
                        "FAIL_CLOSED:"
                        + type(exc).__name__
                    )
        finally:
            local_client.close()

    with ThreadPoolExecutor(max_workers=2) as pool:
        results = tuple(
            pool.map(
                lambda _: contender(),
                range(2),
            )
        )

    assert "SUCCESS" in results

    assert collection.count_documents(
        {
            "tenant_id": first.tenant_id,
            "principal_operating_role_binding_id":
                getattr(first, "principal_operating_role_binding_id"),
            "binding_revision": 2,
        }
    ) == 1


def test_real_restart_durability(
    mongo_context: tuple[
        MongoClient[Any],
        Any,
        Any,
        LegalPrincipalOperatingRoleBindingRegistry,
    ],
) -> None:
    client, database, _collection, registry = mongo_context
    first = make_value()

    _commit(client, registry, first)

    fresh_client = _client()

    try:
        fresh_registry = LegalPrincipalOperatingRoleBindingRegistry(
            fresh_client[database.name][COLLECTION_NAME]
        )

        assert _read_revision(
            fresh_client,
            fresh_registry,
            first.tenant_id,
            getattr(first, "principal_operating_role_binding_id"),
            getattr(first, "binding_revision"),
        ) == first
    finally:
        fresh_client.close()



def test_real_principal_effective_window(
    mongo_context: tuple[
        MongoClient[Any],
        Any,
        Any,
        LegalPrincipalOperatingRoleBindingRegistry,
    ],
) -> None:
    client, _database, _collection, registry = mongo_context

    first = make_value(
        until=NOW + timedelta(days=1)
    )

    _commit(client, registry, first)

    with client.start_session() as session:
        session.start_transaction()

        assert registry.resolve_current(
            first.tenant_id,
            first.principal_operating_role_binding_id,
            NOW,
            session=session,
        ) == first

        assert registry.resolve_current(
            first.tenant_id,
            first.principal_operating_role_binding_id,
            NOW + timedelta(days=2),
            session=session,
        ) is None

        assert registry.list_current_for_principal(
            first.tenant_id,
            first.principal_id,
            NOW,
            session=session,
        ) == (first,)

        assert registry.list_current_for_principal(
            first.tenant_id,
            first.principal_id,
            NOW + timedelta(days=2),
            session=session,
        ) == ()

        session.abort_transaction()



# ==============================================================================
# WILSY OS SOVEREIGN ARTIFACT SEAL
# ==============================================================================
# ARTIFACT: test_legal_principal_operating_role_binding_registry_real_mongo.py
# VERSION: v1.0.1-CX27-R5B-R4-LEGAL-PRINCIPAL-OPERATING-ROLE-BINDING-REAL-MONGO
# REAL MONGO: wilsyVendorCertRS
# DATABASE SCOPE: UUID-ISOLATED DISPOSABLE ONLY
# PRODUCTION DATABASE AUTHORITY: NONE
# TENANT POSTURE: exact tenant isolation and cross-tenant non-disclosure
# FAIL-CLOSED POSTURE: topology, transaction, conflict, corruption, overlap, race, window, and durability failures reject
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively
# END OF WILSY OS SOVEREIGN ARTIFACT
