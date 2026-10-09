"""Real-Mongo certificate for the D21B4B tenant branding profile registry.

TITLE: Tenant Branding Profile Registry Real-Mongo Certificate
VERSION: v1.0.0-D21B4B-TENANT-BRANDING-PROFILE-REGISTRY-REAL-MONGO-CERT
AUTHORITY: Wilsy OS Core Governance
EPITOME: Physically certify D21B4B profile/selection persistence and explicit
         tenant current-pointer semantics against a disposable Mongo replica-set
         database with caller-owned transactions, strict hydration, CAS and
         concurrency evidence.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tests/integration/test_tenant_branding_profile_registry_real_mongo.py
COLLABORATION / OWNERSHIP: Host-backed D21B4B certificate only. D21B3 owns
                            approved profile evidence; D21B4A owns immutable
                            historical selection facts; D21B4B owns durable
                            profile/selection/currentness persistence. This test
                            caller owns every Mongo session/transaction boundary.
CERTIFICATION / UPDATE DATE: 2026-09-25
CHANGELOG: v1.0.0-D21B4B-TENANT-BRANDING-PROFILE-REGISTRY-REAL-MONGO-CERT
           establishes physical evidence for exact indexes, committed create and
           replay, rollback atomicity, tenant isolation, current-pointer creation
           and CAS advancement, stale replay rejection, corruption rejection,
           duplicate-current enforcement, caller transaction ownership and a
           genuine competing revision race.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2; ISO 27001.
SECURITY / PRIVACY POSTURE: UUID-isolated synthetic tenants and disposable local
                             database only; no credentials, external calls,
                             asset bytes, raw URLs, filesystem paths or browser
                             state.
TENANT BOUNDARY: Every registry operation and every physical uniqueness
                 primitive remains tenant-scoped. Cross-tenant evidence is
                 observed only as absence.
AUTHORITY BOUNDARY: Durable D21B4B persistence/currentness evidence only.
                    Current selection does not prove D21B2 remains ACTIVE and
                    creates no asset-resolution, browser, IAM or legal authority.
FINANCIAL AUTHORITY BOUNDARY: No price, bank, tax, invoice, charge, payment,
                               execution or settlement truth. Kennel EOS remains
                               the exclusive financial execution authority.
TRANSACTION BOUNDARY: The certificate starts/commits/aborts transactions; the
                      registry must only require and propagate the supplied
                      session. Whole-transaction retry remains caller-owned.
FAIL-CLOSED DECLARATION: Wrong/unavailable replica set may skip only before the
                         fixture yields. Once yielded, index, transaction,
                         hydration, replay, CAS, corruption or concurrency
                         failures are certification failures.
"""
from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor
from copy import deepcopy
from datetime import datetime, timezone
import os
from threading import Barrier
from typing import Any, Iterator
import uuid

import pytest
from pymongo import MongoClient
from pymongo.errors import DuplicateKeyError, PyMongoError
from pymongo.read_concern import ReadConcern
from pymongo.write_concern import WriteConcern

from tools.eos.saas.billing import tenant_branding_profile_registry as registry
from tools.eos.saas.billing.tenant_branding_vas_policy import TenantBrandingTier
from tools.eos.saas.domain.tenant_branding_entitlement import (
    TenantBrandingEntitlement,
    TenantBrandingEntitlementState,
    create_tenant_branding_entitlement,
)
from tools.eos.saas.domain.tenant_branding_profile import (
    TenantBrandingProfile,
    approve_tenant_branding_profile,
)
from tools.eos.saas.domain.tenant_branding_profile_selection import (
    TenantBrandingProfileSelection,
    select_tenant_branding_profile,
)


VERSION = "v1.0.0-D21B4B-TENANT-BRANDING-PROFILE-REGISTRY-REAL-MONGO-CERT"
MONGO_URI = os.getenv(
    "TEST_VENDOR_MONGO_URI",
    "mongodb://127.0.0.1:27027/?replicaSet=wilsyVendorCertRS",
)
EXPECTED_REPLICA_SET = "wilsyVendorCertRS"
NOW = datetime(2026, 9, 25, 14, 0, tzinfo=timezone.utc)
FP = "a" * 128
ASSET_FP = "b" * 128


@pytest.fixture
def mongo_context() -> Iterator[tuple[MongoClient[Any], Any, Any, Any, Any]]:
    """Yield one UUID-isolated writable replica-set database.

    Only pre-yield host availability/topology mismatches may skip. Once this
    fixture yields, all physical persistence failures propagate as failures.
    """
    client: MongoClient[Any] = MongoClient(
        MONGO_URI,
        serverSelectionTimeoutMS=3000,
        connectTimeoutMS=3000,
        retryWrites=True,
        tz_aware=True,
    )
    database: Any = None
    try:
        try:
            hello = client.admin.command("hello")
        except PyMongoError as error:
            pytest.skip(
                f"host Mongo unavailable during hello: {type(error).__name__}: {error}"
            )
        if hello.get("setName") != EXPECTED_REPLICA_SET:
            pytest.skip(f"wrong replica set: {hello.get('setName')!r}")
        if hello.get("isWritablePrimary", hello.get("ismaster")) is not True:
            pytest.skip("replica set has no writable primary")
        if hello.get("logicalSessionTimeoutMinutes") is None:
            pytest.skip("replica set has no logical-session capability")

        database = client[f"wilsy_d21b4b_branding_{uuid.uuid4().hex}"]
        profiles = database.get_collection(
            registry.PROFILE_COLLECTION,
            write_concern=WriteConcern(w="majority", j=True),
            read_concern=ReadConcern("majority"),
        )
        selections = database.get_collection(
            registry.SELECTION_COLLECTION,
            write_concern=WriteConcern(w="majority", j=True),
            read_concern=ReadConcern("majority"),
        )
        current = database.get_collection(
            registry.CURRENT_COLLECTION,
            write_concern=WriteConcern(w="majority", j=True),
            read_concern=ReadConcern("majority"),
        )
        registry.ensure_indexes(profiles, selections, current)
        yield client, database, profiles, selections, current
    finally:
        if database is not None:
            client.drop_database(database.name)
        client.close()


def _active_entitlement(
    tenant_id: str,
    *,
    entitlement_id: str = "branding-entitlement-1",
) -> TenantBrandingEntitlement:
    """Build one exact ACTIVE D21B2 entitlement snapshot."""
    pending = create_tenant_branding_entitlement(
        tenant_id=tenant_id,
        entitlement_id=entitlement_id,
        branding_tier=TenantBrandingTier.PROFESSIONAL,
        source_evidence_reference="composition-1",
        source_evidence_fingerprint=FP,
    )
    return pending.transition(
        TenantBrandingEntitlementState.ACTIVE,
        expected_revision=0,
        evidence_reference="activation-1",
        evidence_fingerprint=FP,
        occurred_at=NOW,
    )


def _profile(
    entitlement: TenantBrandingEntitlement,
    *,
    profile_id: str,
    profile_label: str,
) -> TenantBrandingProfile:
    """Build one valid approved D21B3 profile with opaque asset evidence."""
    return approve_tenant_branding_profile(
        entitlement=entitlement,
        profile_id=profile_id,
        profile_label=profile_label,
        source_evidence_reference=f"submission:{profile_id}",
        source_evidence_fingerprint=FP,
        approved_at=NOW,
        approval_evidence_reference=f"approval:{profile_id}",
        approval_evidence_fingerprint=FP,
        logo_asset_reference=f"asset:{entitlement.tenant_id}:logo:{profile_id}",
        logo_asset_fingerprint=ASSET_FP,
        primary_color="#112233",
        secondary_color="#445566",
        accent_color="#AABBCC",
        email_display_name="Acme Legal",
    )


def _selection(
    profile: TenantBrandingProfile,
    entitlement: TenantBrandingEntitlement,
    *,
    selection_id: str,
    revision: int,
    prior: TenantBrandingProfileSelection | None = None,
) -> TenantBrandingProfileSelection:
    """Build one valid immutable D21B4A selection fact."""
    return select_tenant_branding_profile(
        profile=profile,
        current_entitlement=entitlement,
        selection_id=selection_id,
        selection_revision=revision,
        selected_at=NOW,
        selection_evidence_reference=f"selection-evidence:{selection_id}",
        selection_evidence_fingerprint=FP,
        prior_selection=prior,
    )


def _commit_profile(
    client: MongoClient[Any],
    profile: TenantBrandingProfile,
    profiles: Any,
) -> TenantBrandingProfile:
    """Persist one profile under a caller-owned committed transaction."""
    with client.start_session() as session:
        with session.start_transaction():
            return registry.persist_profile(profile, profiles, session=session)


def _commit_selection(
    client: MongoClient[Any],
    selection: TenantBrandingProfileSelection,
    profiles: Any,
    selections: Any,
    current: Any,
) -> registry.TenantBrandingSelectionPersistenceResult:
    """Persist one selection/current advancement under caller ownership."""
    with client.start_session() as session:
        with session.start_transaction():
            return registry.persist_selection_and_advance_current(
                selection,
                profiles,
                selections,
                current,
                session=session,
            )


def _raw_without_id(collection: Any, query: dict[str, object]) -> dict[str, Any]:
    """Return one raw physical Mongo row without the transport-only _id."""
    row = collection.find_one(query)
    assert isinstance(row, dict)
    payload = dict(row)
    payload.pop("_id", None)
    return payload


def test_real_index_topology_is_exact_unique_and_has_no_ttl(
    mongo_context: tuple[MongoClient[Any], Any, Any, Any, Any],
) -> None:
    """Physically prove the five D21B4B uniqueness primitives and no TTL."""
    _, _, profiles, selections, current = mongo_context
    profile_indexes = {
        item["name"]: item
        for item in profiles.list_indexes()
        if item["name"] != "_id_"
    }
    selection_indexes = {
        item["name"]: item
        for item in selections.list_indexes()
        if item["name"] != "_id_"
    }
    current_indexes = {
        item["name"]: item
        for item in current.list_indexes()
        if item["name"] != "_id_"
    }

    assert set(profile_indexes) == {
        registry.PROFILE_ID_INDEX_NAME,
        registry.PROFILE_FINGERPRINT_INDEX_NAME,
    }
    assert dict(profile_indexes[registry.PROFILE_ID_INDEX_NAME]["key"]) == {
        "tenant_id": 1,
        "profile_id": 1,
    }
    assert dict(
        profile_indexes[registry.PROFILE_FINGERPRINT_INDEX_NAME]["key"]
    ) == {
        "tenant_id": 1,
        "profile_fingerprint": 1,
    }
    assert set(selection_indexes) == {
        registry.SELECTION_ID_INDEX_NAME,
        registry.SELECTION_REVISION_INDEX_NAME,
    }
    assert dict(selection_indexes[registry.SELECTION_ID_INDEX_NAME]["key"]) == {
        "tenant_id": 1,
        "selection_id": 1,
    }
    assert dict(
        selection_indexes[registry.SELECTION_REVISION_INDEX_NAME]["key"]
    ) == {
        "tenant_id": 1,
        "selection_revision": 1,
    }
    assert set(current_indexes) == {registry.CURRENT_TENANT_INDEX_NAME}
    assert dict(current_indexes[registry.CURRENT_TENANT_INDEX_NAME]["key"]) == {
        "tenant_id": 1
    }

    all_indexes = [
        *profile_indexes.values(),
        *selection_indexes.values(),
        *current_indexes.values(),
    ]
    assert all(item.get("unique") is True for item in all_indexes)
    assert all("expireAfterSeconds" not in item for item in all_indexes)


def test_real_profile_create_exact_replay_divergence_and_tenant_isolation(
    mongo_context: tuple[MongoClient[Any], Any, Any, Any, Any],
) -> None:
    """Certify immutable profile replay/conflict and cross-tenant silence."""
    client, _, profiles, _, _ = mongo_context
    tenant_a = f"tenant-a-{uuid.uuid4().hex}"
    tenant_b = f"tenant-b-{uuid.uuid4().hex}"
    entitlement_a = _active_entitlement(tenant_a)
    entitlement_b = _active_entitlement(tenant_b)
    profile_a = _profile(
        entitlement_a,
        profile_id="profile-primary",
        profile_label="Tenant A primary",
    )
    profile_b = _profile(
        entitlement_b,
        profile_id="profile-primary",
        profile_label="Tenant B primary",
    )

    assert _commit_profile(client, profile_a, profiles) == profile_a
    assert _commit_profile(client, profile_a, profiles) == profile_a
    assert _commit_profile(client, profile_b, profiles) == profile_b
    assert profiles.count_documents({"profile_id": "profile-primary"}) == 2

    divergent = _profile(
        entitlement_a,
        profile_id="profile-primary",
        profile_label="Divergent approved profile",
    )
    with client.start_session() as session:
        session.start_transaction()
        with pytest.raises(registry.TenantBrandingProfileRegistryProfileConflictError):
            registry.persist_profile(divergent, profiles, session=session)
        session.abort_transaction()

    with client.start_session() as session:
        with session.start_transaction():
            with pytest.raises(
                registry.TenantBrandingProfileRegistryProfileNotFoundError
            ):
                registry.get_profile(
                    tenant_b,
                    "profile-does-not-exist",
                    profiles,
                    session=session,
                )


def test_real_caller_transaction_required_and_abort_is_atomic(
    mongo_context: tuple[MongoClient[Any], Any, Any, Any, Any],
) -> None:
    """Prove registry owns no transaction lifecycle and caller abort rolls back."""
    client, _, profiles, selections, current = mongo_context
    tenant = f"tenant-abort-{uuid.uuid4().hex}"
    entitlement = _active_entitlement(tenant)
    approved = _profile(
        entitlement,
        profile_id="profile-abort",
        profile_label="Abort profile",
    )
    selected = _selection(
        approved,
        entitlement,
        selection_id="selection-abort",
        revision=1,
    )

    with pytest.raises(
        registry.TenantBrandingProfileRegistryTransactionRequiredError
    ):
        registry.persist_profile(approved, profiles, session=None)

    with client.start_session() as inactive_session:
        assert inactive_session.in_transaction is False
        with pytest.raises(
            registry.TenantBrandingProfileRegistryTransactionRequiredError
        ):
            registry.persist_profile(
                approved,
                profiles,
                session=inactive_session,
            )

    with client.start_session() as session:
        session.start_transaction()
        registry.persist_profile(approved, profiles, session=session)
        registry.persist_selection_and_advance_current(
            selected,
            profiles,
            selections,
            current,
            session=session,
        )
        assert profiles.count_documents({"tenant_id": tenant}, session=session) == 1
        assert (
            selections.count_documents({"tenant_id": tenant}, session=session) == 1
        )
        assert current.count_documents({"tenant_id": tenant}, session=session) == 1
        session.abort_transaction()

    assert profiles.count_documents({"tenant_id": tenant}) == 0
    assert selections.count_documents({"tenant_id": tenant}) == 0
    assert current.count_documents({"tenant_id": tenant}) == 0


def test_real_initial_selection_and_revision_two_cas_correlate_exactly(
    mongo_context: tuple[MongoClient[Any], Any, Any, Any, Any],
) -> None:
    """Certify explicit pointer creation and exact revision-two CAS advancement."""
    client, _, profiles, selections, current = mongo_context
    tenant = f"tenant-cas-{uuid.uuid4().hex}"
    entitlement = _active_entitlement(tenant)
    first_profile = _profile(
        entitlement,
        profile_id="profile-1",
        profile_label="Profile one",
    )
    second_profile = _profile(
        entitlement,
        profile_id="profile-2",
        profile_label="Profile two",
    )
    first = _selection(
        first_profile,
        entitlement,
        selection_id="selection-1",
        revision=1,
    )
    second = _selection(
        second_profile,
        entitlement,
        selection_id="selection-2",
        revision=2,
        prior=first,
    )

    _commit_profile(client, first_profile, profiles)
    _commit_profile(client, second_profile, profiles)
    created = _commit_selection(client, first, profiles, selections, current)
    advanced = _commit_selection(client, second, profiles, selections, current)

    assert (
        created.outcome
        is registry.TenantBrandingProfilePersistenceOutcome.CREATED
    )
    assert (
        advanced.outcome
        is registry.TenantBrandingProfilePersistenceOutcome.CREATED
    )
    assert advanced.current.selection == second
    assert advanced.current.profile == second_profile
    assert advanced.current.pointer.selection_revision == 2
    assert selections.count_documents({"tenant_id": tenant}) == 2
    assert current.count_documents({"tenant_id": tenant}) == 1

    with client.start_session() as session:
        with session.start_transaction():
            hydrated = registry.get_current(
                tenant,
                profiles,
                selections,
                current,
                session=session,
            )
            assert hydrated == advanced.current


def test_real_current_replay_is_idempotent_and_historical_replay_cannot_rewind(
    mongo_context: tuple[MongoClient[Any], Any, Any, Any, Any],
) -> None:
    """Certify exact-current replay and stale historical replay rejection."""
    client, _, profiles, selections, current = mongo_context
    tenant = f"tenant-replay-{uuid.uuid4().hex}"
    entitlement = _active_entitlement(tenant)
    profile_1 = _profile(entitlement, profile_id="profile-1", profile_label="One")
    profile_2 = _profile(entitlement, profile_id="profile-2", profile_label="Two")
    first = _selection(
        profile_1,
        entitlement,
        selection_id="selection-1",
        revision=1,
    )
    second = _selection(
        profile_2,
        entitlement,
        selection_id="selection-2",
        revision=2,
        prior=first,
    )
    _commit_profile(client, profile_1, profiles)
    _commit_profile(client, profile_2, profiles)
    _commit_selection(client, first, profiles, selections, current)

    replay = _commit_selection(client, first, profiles, selections, current)
    assert (
        replay.outcome
        is registry.TenantBrandingProfilePersistenceOutcome.IDEMPOTENT_REPLAY
    )
    assert replay.current.selection == first

    _commit_selection(client, second, profiles, selections, current)
    with client.start_session() as session:
        session.start_transaction()
        with pytest.raises(
            registry.TenantBrandingProfileRegistryCurrentPointerConflictError
        ) as raised:
            registry.persist_selection_and_advance_current(
                first,
                profiles,
                selections,
                current,
                session=session,
            )
        assert raised.value.code == "D21B4B_STALE_SELECTION_REPLAY"
        session.abort_transaction()

    raw_current = _raw_without_id(current, {"tenant_id": tenant})
    assert raw_current["selection_id"] == second.selection_id
    assert raw_current["selection_revision"] == 2


def test_real_physical_current_uniqueness_and_no_raw_sensitive_pointer_material(
    mongo_context: tuple[MongoClient[Any], Any, Any, Any, Any],
) -> None:
    """Certify one pointer per tenant and compact non-sensitive currentness."""
    client, _, profiles, selections, current = mongo_context
    tenant = f"tenant-pointer-{uuid.uuid4().hex}"
    entitlement = _active_entitlement(tenant)
    approved = _profile(
        entitlement,
        profile_id="profile-pointer",
        profile_label="Pointer profile",
    )
    selected = _selection(
        approved,
        entitlement,
        selection_id="selection-pointer",
        revision=1,
    )
    _commit_profile(client, approved, profiles)
    _commit_selection(client, selected, profiles, selections, current)

    raw_pointer = _raw_without_id(current, {"tenant_id": tenant})
    forbidden = {
        "logo_asset_reference",
        "logo_asset_fingerprint",
        "primary_color",
        "secondary_color",
        "accent_color",
        "email_display_name",
        "favicon_asset_reference",
        "favicon_asset_fingerprint",
        "bank",
        "bank_account",
        "iban",
        "swift",
        "vat",
        "invoice",
        "payment",
        "settlement",
        "price",
        "amount",
        "url",
        "path",
        "base64",
    }
    assert forbidden.isdisjoint(raw_pointer)

    duplicate = deepcopy(raw_pointer)
    duplicate["selection_id"] = "selection-impossible-duplicate"
    duplicate["selection_fingerprint"] = "c" * 128
    duplicate["fingerprint"] = "d" * 128
    with pytest.raises(DuplicateKeyError):
        current.insert_one(duplicate)
    assert current.count_documents({"tenant_id": tenant}) == 1


def test_real_corrupt_profile_selection_and_pointer_fail_closed(
    mongo_context: tuple[MongoClient[Any], Any, Any, Any, Any],
) -> None:
    """Certify strict physical hydration/correlation across all three layers."""
    client, _, profiles, selections, current = mongo_context
    tenant = f"tenant-corrupt-{uuid.uuid4().hex}"
    entitlement = _active_entitlement(tenant)
    approved = _profile(
        entitlement,
        profile_id="profile-corrupt",
        profile_label="Corrupt profile",
    )
    selected = _selection(
        approved,
        entitlement,
        selection_id="selection-corrupt",
        revision=1,
    )
    _commit_profile(client, approved, profiles)
    _commit_selection(client, selected, profiles, selections, current)

    original_profile = deepcopy(profiles.find_one({"tenant_id": tenant}))
    original_selection = deepcopy(selections.find_one({"tenant_id": tenant}))
    original_current = deepcopy(current.find_one({"tenant_id": tenant}))
    assert isinstance(original_profile, dict)
    assert isinstance(original_selection, dict)
    assert isinstance(original_current, dict)

    profiles.update_one(
        {"tenant_id": tenant},
        {"$set": {"profile_payload.fingerprint": "f" * 128}},
    )
    with client.start_session() as session:
        with session.start_transaction():
            with pytest.raises(
                registry.TenantBrandingProfileRegistryPersistedRecordInvalidError
            ):
                registry.get_current(
                    tenant,
                    profiles,
                    selections,
                    current,
                    session=session,
                )
    profiles.replace_one({"_id": original_profile["_id"]}, original_profile)

    selections.update_one(
        {"tenant_id": tenant},
        {"$set": {"selection_payload.fingerprint": "e" * 128}},
    )
    with client.start_session() as session:
        with session.start_transaction():
            with pytest.raises(
                registry.TenantBrandingProfileRegistryPersistedRecordInvalidError
            ):
                registry.get_current(
                    tenant,
                    profiles,
                    selections,
                    current,
                    session=session,
                )
    selections.replace_one({"_id": original_selection["_id"]}, original_selection)

    current.update_one(
        {"tenant_id": tenant},
        {"$set": {"profile_fingerprint": "d" * 128}},
    )
    with client.start_session() as session:
        with session.start_transaction():
            with pytest.raises(
                registry.TenantBrandingProfileRegistryPersistedRecordInvalidError
            ):
                registry.get_current(
                    tenant,
                    profiles,
                    selections,
                    current,
                    session=session,
                )
    current.replace_one({"_id": original_current["_id"]}, original_current)


def test_real_cross_tenant_current_read_is_indistinguishable_from_absence(
    mongo_context: tuple[MongoClient[Any], Any, Any, Any, Any],
) -> None:
    """Certify a foreign tenant cannot discover another tenant's currentness."""
    client, _, profiles, selections, current = mongo_context
    tenant_a = f"tenant-a-current-{uuid.uuid4().hex}"
    tenant_b = f"tenant-b-current-{uuid.uuid4().hex}"
    entitlement = _active_entitlement(tenant_a)
    approved = _profile(
        entitlement,
        profile_id="profile-current",
        profile_label="Current profile",
    )
    selected = _selection(
        approved,
        entitlement,
        selection_id="selection-current",
        revision=1,
    )
    _commit_profile(client, approved, profiles)
    _commit_selection(client, selected, profiles, selections, current)

    with client.start_session() as session:
        with session.start_transaction():
            with pytest.raises(
                registry.TenantBrandingProfileRegistryCurrentPointerMissingError
            ):
                registry.get_current(
                    tenant_b,
                    profiles,
                    selections,
                    current,
                    session=session,
                )


def test_real_competing_revision_two_transactions_have_one_winner_and_retry_loser(
    mongo_context: tuple[MongoClient[Any], Any, Any, Any, Any],
) -> None:
    """Certify a genuine race cannot advance two divergent revision-two facts."""
    client, _, profiles, selections, current = mongo_context
    tenant = f"tenant-race-{uuid.uuid4().hex}"
    entitlement = _active_entitlement(tenant)
    base_profile = _profile(
        entitlement,
        profile_id="profile-base",
        profile_label="Base profile",
    )
    left_profile = _profile(
        entitlement,
        profile_id="profile-left",
        profile_label="Left profile",
    )
    right_profile = _profile(
        entitlement,
        profile_id="profile-right",
        profile_label="Right profile",
    )
    first = _selection(
        base_profile,
        entitlement,
        selection_id="selection-1",
        revision=1,
    )
    left = _selection(
        left_profile,
        entitlement,
        selection_id="selection-left",
        revision=2,
        prior=first,
    )
    right = _selection(
        right_profile,
        entitlement,
        selection_id="selection-right",
        revision=2,
        prior=first,
    )

    for item in (base_profile, left_profile, right_profile):
        _commit_profile(client, item, profiles)
    _commit_selection(client, first, profiles, selections, current)

    barrier = Barrier(2)

    def contender(selection: TenantBrandingProfileSelection) -> str:
        with client.start_session() as session:
            session.start_transaction()
            barrier.wait()
            try:
                registry.persist_selection_and_advance_current(
                    selection,
                    profiles,
                    selections,
                    current,
                    session=session,
                )
                session.commit_transaction()
                return "COMMITTED"
            except registry.TenantBrandingProfileRegistryRetryRequiredError:
                if session.in_transaction:
                    session.abort_transaction()
                return "RETRY_REQUIRED"
            except Exception as error:
                if session.in_transaction:
                    session.abort_transaction()
                return type(error).__name__

    with ThreadPoolExecutor(max_workers=2) as pool:
        outcomes = list(pool.map(contender, (left, right)))

    assert outcomes.count("COMMITTED") == 1
    assert outcomes.count("RETRY_REQUIRED") == 1
    assert selections.count_documents({"tenant_id": tenant}) == 2
    assert selections.count_documents(
        {"tenant_id": tenant, "selection_revision": 2}
    ) == 1
    assert current.count_documents({"tenant_id": tenant}) == 1
    raw_current = _raw_without_id(current, {"tenant_id": tenant})
    assert raw_current["selection_revision"] == 2
    assert raw_current["selection_id"] in {
        left.selection_id,
        right.selection_id,
    }


# ARTIFACT: test_tenant_branding_profile_registry_real_mongo.py
# VERSION: v1.0.0-D21B4B-TENANT-BRANDING-PROFILE-REGISTRY-REAL-MONGO-CERT
# AUTHORITY BOUNDARY: physical D21B4B persistence/currentness evidence only; no entitlement freshness, asset resolution, browser, IAM, legal or financial authority
# TENANT POSTURE: UUID-isolated database and tenant-scoped reads/writes/indexes; foreign currentness is absence
# FAIL-CLOSED POSTURE: post-yield index, transaction, replay, CAS, corruption and concurrency failures fail certification
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively
# END OF WILSY OS SOVEREIGN ARTIFACT
