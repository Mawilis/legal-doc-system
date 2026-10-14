from __future__ import annotations

from datetime import datetime, timedelta, timezone
from uuid import uuid4

import pytest
from pymongo import MongoClient
from pymongo.client_session import ClientSession
from pymongo.collection import Collection
from pymongo.database import Database

from tools.eos.auth.current_platform_privileged_eligibility_prerequisite import (
    CurrentPlatformPrivilegedEligibilityPrerequisiteResolver,
)
from tools.eos.auth.platform_privileged_eligibility_prerequisite import (
    PRIVILEGE_CLASS,
    SCOPE,
    PlatformPrerequisiteStatus,
    PlatformPrivilegedEligibilityPrerequisite,
)
from tools.eos.auth.platform_privileged_eligibility_prerequisite_registry import (
    PlatformPrerequisiteRegistryError,
    PlatformPrivilegedEligibilityPrerequisiteRegistry,
)
from tools.eos.auth.principal_authority import (
    PrincipalAuthority,
)
from tools.eos.auth.principal_authority_repository import (
    PrincipalAuthorityRepository,
)
from tools.eos.auth.principal_status import (
    PrincipalStatus,
)


MONGO_URI = (
    "mongodb://127.0.0.1:27027/"
    "?replicaSet=wilsyVendorCertRS"
)

PRINCIPAL = "principal-platform-p2-real"
PREREQUISITE_ID = "platform-prerequisite-p2-real"

NOW = datetime(
    2026,
    10,
    14,
    18,
    0,
    tzinfo=timezone.utc,
)


@pytest.fixture()
def mongo():
    client = MongoClient(
        MONGO_URI,
        serverSelectionTimeoutMS=5000,
    )

    hello = client.admin.command("hello")

    assert hello.get("setName") == "wilsyVendorCertRS"
    assert hello.get("logicalSessionTimeoutMinutes") is not None

    canonical_before = set(
        client["wilsy"].list_collection_names()
    )

    db_name = (
        "wilsy_p2_platform_prerequisite_"
        + uuid4().hex
    )

    db = client[db_name]

    principal: Collection = db["principal_authorities"]
    prerequisite: Collection = db[
        "platform_privileged_eligibility_prerequisites"
    ]

    PrincipalAuthorityRepository.ensure_indexes(
        principal
    )

    registry = (
        PlatformPrivilegedEligibilityPrerequisiteRegistry(
            prerequisite
        )
    )

    registry.ensure_indexes()

    yield {
        "client": client,
        "db": db,
        "db_name": db_name,
        "principal": principal,
        "prerequisite": prerequisite,
        "registry": registry,
        "canonical_before": canonical_before,
    }

    canonical_after = set(
        client["wilsy"].list_collection_names()
    )

    assert canonical_after == canonical_before

    client.drop_database(db_name)
    client.close()


def designation(
    *,
    evidence: str = "core-governance:real-a",
    effective_from: datetime = NOW,
    effective_until: datetime | None = (
        NOW + timedelta(hours=1)
    ),
) -> PlatformPrivilegedEligibilityPrerequisite:
    return (
        PlatformPrivilegedEligibilityPrerequisite
        .designate(
            platform_prerequisite_id=
                PREREQUISITE_ID,
            principal_id=
                PRINCIPAL,
            effective_from=
                effective_from,
            effective_until=
                effective_until,
            source_evidence_reference=
                evidence,
        )
    )


def create_principal(
    collection: Collection,
    *,
    status: PrincipalStatus = PrincipalStatus.ACTIVE,
    session: ClientSession | None = None,
) -> None:
    PrincipalAuthorityRepository.create(
        PrincipalAuthority(
            PRINCIPAL,
            status,
            1,
        ),
        collection=collection,
        session=session,
    )


def test_real_indexes_no_ttl_and_exact_replay(mongo) -> None:
    registry = mongo["registry"]
    collection = mongo["prerequisite"]

    indexes = {
        item["name"]: item
        for item in collection.list_indexes()
    }

    assert (
        "platform_prerequisite_revision_unique"
        in indexes
    )

    assert indexes[
        "platform_prerequisite_revision_unique"
    ].get("unique") is True

    assert (
        "platform_prerequisite_current_lookup"
        in indexes
    )

    for item in indexes.values():
        assert "expireAfterSeconds" not in item

    value = designation()

    with mongo["client"].start_session() as session:
        with session.start_transaction():
            first = registry.append(
                value,
                session=session,
            )

            second = registry.append(
                value,
                session=session,
            )

            assert first == second == value

    assert (
        collection.count_documents(
            {
                "platform_prerequisite_id":
                    PREREQUISITE_ID
            }
        )
        == 1
    )

    divergent = designation(
        evidence="core-governance:real-divergent"
    )

    with mongo["client"].start_session() as session:
        with pytest.raises(
            PlatformPrerequisiteRegistryError,
            match="DIVERGENT_REPLAY",
        ):
            with session.start_transaction():
                registry.append(
                    divergent,
                    session=session,
                )


def test_real_commit_abort_currentness_and_half_open_window(
    mongo,
) -> None:
    registry = mongo["registry"]
    principal = mongo["principal"]
    collection = mongo["prerequisite"]

    create_principal(
        principal
    )

    value = designation()

    with mongo["client"].start_session() as session:
        with session.start_transaction():
            registry.append(
                value,
                session=session,
            )

            current = registry.resolve_current(
                principal_id=
                    PRINCIPAL,
                privilege_class=
                    PRIVILEGE_CLASS,
                scope=
                    SCOPE,
                at=
                    NOW,
                session=session,
            )

            assert current == value

    assert (
        collection.count_documents(
            {
                "platform_prerequisite_id":
                    PREREQUISITE_ID
            }
        )
        == 1
    )

    assert (
        registry.resolve_current(
            principal_id=
                PRINCIPAL,
            privilege_class=
                PRIVILEGE_CLASS,
            scope=
                SCOPE,
            at=
                NOW
                + timedelta(
                    minutes=59
                ),
        )
        == value
    )

    assert (
        registry.resolve_current(
            principal_id=
                PRINCIPAL,
            privilege_class=
                PRIVILEGE_CLASS,
            scope=
                SCOPE,
            at=
                NOW
                + timedelta(
                    hours=1
                ),
        )
        is None
    )

    abort_id = (
        "platform-prerequisite-abort-"
        + uuid4().hex
    )

    abort_value = (
        PlatformPrivilegedEligibilityPrerequisite
        .designate(
            platform_prerequisite_id=
                abort_id,
            principal_id=
                PRINCIPAL,
            effective_from=
                NOW,
            source_evidence_reference=
                "core-governance:abort",
        )
    )

    with mongo["client"].start_session() as session:
        session.start_transaction()

        registry.append(
            abort_value,
            session=session,
        )

        session.abort_transaction()

    assert (
        collection.count_documents(
            {
                "platform_prerequisite_id":
                    abort_id
            }
        )
        == 0
    )


def test_real_retired_revoked_and_wrong_scope_denial(
    mongo,
) -> None:
    registry = mongo["registry"]
    principal = mongo["principal"]

    create_principal(
        principal
    )

    active = designation()

    retired = active.transition(
        status=
            PlatformPrerequisiteStatus.RETIRED,
        effective_from=
            NOW
            + timedelta(
                minutes=10
            ),
        source_evidence_reference=
            "core-governance:retired",
    )

    with mongo["client"].start_session() as session:
        with session.start_transaction():
            registry.append(
                active,
                session=session,
            )
            registry.append(
                retired,
                session=session,
            )

    assert (
        registry.resolve_current(
            principal_id=
                PRINCIPAL,
            privilege_class=
                PRIVILEGE_CLASS,
            scope=
                SCOPE,
            at=
                NOW
                + timedelta(
                    minutes=11
                ),
        )
        is None
    )

    assert (
        registry.resolve_current(
            principal_id=
                PRINCIPAL,
            privilege_class=
                "ENTERPRISE_ADMIN",
            scope=
                SCOPE,
            at=
                NOW,
        )
        is None
    )

    assert (
        registry.resolve_current(
            principal_id=
                PRINCIPAL,
            privilege_class=
                PRIVILEGE_CLASS,
            scope=
                "SYSTEM",
            at=
                NOW,
        )
        is None
    )


def test_real_current_resolver_requires_active_principal(
    mongo,
) -> None:
    registry = mongo["registry"]
    principal = mongo["principal"]

    create_principal(
        principal
    )

    value = designation()

    with mongo["client"].start_session() as session:
        with session.start_transaction():
            registry.append(
                value,
                session=session,
            )

    resolver = (
        CurrentPlatformPrivilegedEligibilityPrerequisiteResolver(
            principal_collection=
                principal,
            prerequisite_registry=
                registry,
        )
    )

    with mongo["client"].start_session() as session:
        current = resolver.resolve(
            principal_id=
                PRINCIPAL,
            privilege_class=
                PRIVILEGE_CLASS,
            scope=
                SCOPE,
            at=
                NOW
                + timedelta(
                    minutes=1
                ),
            session=session,
        )

        assert current == value

    principal.update_one(
        {
            "principal_id":
                PRINCIPAL
        },
        {
            "$set": {
                "status":
                    PrincipalStatus.SUSPENDED.value
            }
        },
    )

    with mongo["client"].start_session() as session:
        assert (
            resolver.resolve(
                principal_id=
                    PRINCIPAL,
                privilege_class=
                    PRIVILEGE_CLASS,
                scope=
                    SCOPE,
                at=
                    NOW
                    + timedelta(
                        minutes=2
                    ),
                session=session,
            )
            is None
        )


def test_real_corruption_fails_closed_and_no_delete_surface(
    mongo,
) -> None:
    registry = mongo["registry"]
    principal = mongo["principal"]
    collection = mongo["prerequisite"]

    create_principal(
        principal
    )

    value = designation()

    with mongo["client"].start_session() as session:
        with session.start_transaction():
            registry.append(
                value,
                session=session,
            )

    original = collection.find_one(
        {
            "platform_prerequisite_id":
                PREREQUISITE_ID,
            "revision":
                1,
        }
    )

    assert original is not None

    for field, bad in (
        (
            "privilege_class",
            "ENTERPRISE_ADMIN",
        ),
        (
            "scope",
            "SYSTEM",
        ),
        (
            "source_authority",
            "OTHER",
        ),
        (
            "prerequisite_fingerprint",
            "0" * 128,
        ),
    ):
        collection.update_one(
            {
                "_id":
                    original["_id"]
            },
            {
                "$set": {
                    field: bad
                }
            },
        )

        with pytest.raises(Exception):
            registry.get(
                platform_prerequisite_id=
                    PREREQUISITE_ID,
                revision=
                    1,
            )

        collection.replace_one(
            {
                "_id":
                    original["_id"]
            },
            original,
        )

    assert not hasattr(
        registry,
        "delete"
    )

    assert not hasattr(
        registry,
        "delete_one"
    )

    assert not hasattr(
        registry,
        "delete_many"
    )
