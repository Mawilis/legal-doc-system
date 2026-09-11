"""WILSY OS host-backed P5-R7 credential-material metadata certificate.

TITLE: Tenant Inbound Provider Credential Material Metadata Registry — Real Mongo
VERSION: v1.0.0-M11-R8-R3B-P8-P3D-P5-R7
AUTHORITY: Wilsy OS Core Governance; bounded host integration evidence only.
EPITOME: Physically certify the frozen P5-R5 registry against a dedicated
         MongoDB replica set without modifying production or security authority.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tests/integration/test_tenant_inbound_provider_credential_material_metadata_registry_real_mongo.py
COLLABORATION / OWNERSHIP: Distinct P5-R7 Real-Mongo certificate owner;
                            domain, registry, adapters, security evidence,
                            provider binding, checkout, and finance remain frozen.
CERTIFICATION / UPDATE DATE: 2026-09-10
CHANGELOG: v1.0.0-M11-R8-R3B-P8-P3D-P5-R7 certifies physical indexes,
           transaction ownership/rollback, replay, re-observation, CAS race,
           strict hydration, tenant/configuration isolation, and cleanup.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2.
SECURITY / PRIVACY POSTURE: Synthetic opaque references only; no raw secret,
                             KMS, provider contact, security evidence, or auth.
TENANT BOUNDARY: Every fact, pointer, idempotency key, and unique constraint is
                 tenant-scoped; the database is unique and ephemeral per run.
AUTHORITY BOUNDARY: Host certificate proves registry persistence semantics only.
TRANSACTION BOUNDARY: Harness owns session, transaction, commit, abort, retry.
FINANCIAL AUTHORITY BOUNDARY: Kennel EOS exclusively owns financial execution.
FAIL-CLOSED DECLARATION: Wrong topology, failed durability, uniqueness, replay,
                          hydration, CAS, isolation, or cleanup fails the gate.
"""
from __future__ import annotations

from copy import deepcopy
from contextlib import contextmanager
from datetime import datetime, timedelta, timezone
import hashlib
import json
import os
from concurrent.futures import ThreadPoolExecutor
from threading import Barrier
from typing import Any, Mapping, cast
from uuid import uuid4

import pytest
from pymongo import MongoClient
from pymongo.errors import DuplicateKeyError, PyMongoError

from tools.eos.saas.billing.tenant_inbound_provider_credential_material_metadata_registry import (
    CREDENTIAL_VERSION_INDEX_NAME,
    CURRENT_POINTER_INDEX_NAME,
    FACT_IDENTITY_INDEX_NAME,
    IDEMPOTENCY_INDEX_NAME,
    IDEMPOTENCY_KEY_FIELD,
    METADATA_FACT_ID_FIELD,
    TenantInboundProviderCredentialMaterialMetadataRegistryCASConflictError,
    TenantInboundProviderCredentialMaterialMetadataRegistryIdempotencyConflictError,
    TenantInboundProviderCredentialMaterialMetadataRegistryPersistedRecordInvalidError,
    ensure_indexes,
    get_current_metadata,
    get_fact,
    persist_fact_and_advance_current,
)
from tools.eos.saas.domain.tenant_inbound_provider_credential_material_metadata import (
    TenantInboundProviderCredentialMaterialMetadata,
)
from tools.eos.saas.billing.tenant_inbound_provider_credential_material_metadata_registry import (
    metadata_fact_id,
)


EXPECTED_REPLICA_SET = "wilsyVendorCertRS"
EXPECTED_MONGO_VERSION = "7.0.37"
VERSION = "v1.0.0-M11-R8-R3B-P8-P3D-P5-R7"
CAMPAIGN_IDENTITY = "M11-R8-R3B-P8-P3D-P5-R7"
AT = datetime(2026, 9, 10, 10, 0, tzinfo=timezone.utc)
CONFIGURATION_FINGERPRINT = "a" * 128
TENANT_A = "p5-r7-tenant-a"
TENANT_B = "p5-r7-tenant-b"
PROVIDER = "synthetic-provider"
CONFIGURATION = "synthetic-configuration"


def _uri() -> str:
    """Require the explicitly supplied, repository-certified Mongo URI."""
    uri = os.environ.get("TEST_VENDOR_MONGO_URI", "").strip()
    if not uri:
        pytest.fail("TEST_VENDOR_MONGO_URI is required for the P5-R7 certificate")
    if "mongodb.net" in uri.lower() or "atlas" in uri.lower():
        pytest.fail("Atlas or production Mongo endpoints are prohibited")
    return uri


def _metadata(
    tenant_id: str = TENANT_A,
    *,
    configuration: str = CONFIGURATION,
    configuration_version: int = 1,
    configuration_fingerprint: str = CONFIGURATION_FINGERPRINT,
    credential_version: str = "credential-v1",
    observed_at: datetime = AT,
    provenance: str | None = None,
    credential_reference: str = "opaque-synthetic-reference",
) -> TenantInboundProviderCredentialMaterialMetadata:
    """Build valid R4D metadata with synthetic, non-secret provenance."""
    return TenantInboundProviderCredentialMaterialMetadata(
        tenant_id=tenant_id,
        provider_id=PROVIDER,
        merchant_configuration_id=configuration,
        merchant_configuration_version=configuration_version,
        merchant_configuration_fingerprint=configuration_fingerprint,
        credential_reference=credential_reference,
        credential_version=credential_version,
        observed_at=observed_at,
        metadata_source_identity="synthetic-test-source",
        metadata_source_version="synthetic-contract-v1",
        version_provenance_reference=provenance or f"synthetic-provenance-{credential_version}",
    )


def _document(value: TenantInboundProviderCredentialMaterialMetadata, key: str) -> dict[str, object]:
    """Serialize one exact fifteen-field registry document for raw index cases."""
    payload = value.to_dict()
    payload[METADATA_FACT_ID_FIELD] = metadata_fact_id(value)
    payload[IDEMPOTENCY_KEY_FIELD] = key
    return payload


def _pair(database: Any, suffix: str) -> tuple[Any, Any]:
    """Create one bounded fact/pointer pair and explicitly install four indexes."""
    facts = database[f"tenant_inbound_provider_credential_material_metadata_facts_{suffix}"]
    pointers = database[f"tenant_inbound_provider_credential_material_metadata_current_{suffix}"]
    ensure_indexes(facts, pointers)
    return facts, pointers


def _persist(
    value: TenantInboundProviderCredentialMaterialMetadata,
    key: str,
    facts: Any,
    pointers: Any,
    client: MongoClient[Any],
    *,
    prior_fact_id: str | None = None,
    prior_metadata_fingerprint: str | None = None,
    prior_configuration_fingerprint: str | None = None,
) -> TenantInboundProviderCredentialMaterialMetadata:
    """Run one registry operation in a caller-owned transaction and commit."""
    with client.start_session() as session:
        session.start_transaction()
        result = persist_fact_and_advance_current(
            value,
            key,
            prior_fact_id,
            prior_metadata_fingerprint,
            expected_prior_configuration_fingerprint=prior_configuration_fingerprint,
            fact_collection=facts,
            pointer_collection=pointers,
            session=session,
        )
        session.commit_transaction()
        return result


def _snapshot(collection: Any, query: Mapping[str, object]) -> tuple[int, str]:
    """Hash deterministic canonical JSON documents while excluding Mongo _id."""
    docs = [
        {key: value for key, value in cast(dict[str, object], row).items() if key != "_id"}
        for row in collection.find(dict(query))
    ]
    canonical = json.dumps(
        sorted(docs, key=lambda item: json.dumps(item, sort_keys=True, default=str)),
        sort_keys=True,
        separators=(",", ":"),
        default=str,
    ).encode("utf-8")
    return len(docs), hashlib.sha3_512(canonical).hexdigest()


def _index(collection: Any, name: str) -> dict[str, object]:
    """Read one physical index specification through list_indexes()."""
    for raw in collection.list_indexes():
        if raw.get("name") == name:
            return cast(dict[str, object], raw)
    raise AssertionError(f"physical index missing: {name}")


def _assert_index(collection: Any, name: str, fields: list[str]) -> None:
    """Verify exact key order and uniqueness/options, not source declarations."""
    spec = _index(collection, name)
    key = cast(Mapping[str, object], spec["key"])
    assert list(key) == fields
    assert spec.get("unique") is True
    assert spec.get("sparse", False) is False
    assert spec.get("partialFilterExpression") is None


@contextmanager
def _read_transaction(client: MongoClient[Any]):
    """Yield a real caller-owned transaction for registry read APIs."""
    with client.start_session() as session:
        session.start_transaction()
        try:
            yield session
        finally:
            if session.in_transaction:
                session.abort_transaction()


def test_real_mongo_credential_material_metadata_registry_certificate() -> None:
    """Execute all 24 frozen P5-R6 physical cases on one bounded database."""
    client: MongoClient[Any] = MongoClient(
        _uri(), serverSelectionTimeoutMS=5000, retryWrites=True, tz_aware=True
    )
    database_name = f"wilsy_p5_r7_metadata_{uuid4().hex}"
    database = client[database_name]
    try:
        # Case 01: host and transaction capability.
        hello = client.admin.command("hello")
        build = client.admin.command("buildInfo")
        assert hello.get("isWritablePrimary") is True
        assert hello.get("setName") == EXPECTED_REPLICA_SET
        assert build.get("version") == EXPECTED_MONGO_VERSION
        assert hello.get("logicalSessionTimeoutMinutes") is not None
        probe = database["bounded_transaction_probe"]
        probe_id = uuid4().hex
        with client.start_session() as session:
            session.start_transaction()
            probe.insert_one({"probe_id": probe_id}, session=session)
            assert probe.find_one({"probe_id": probe_id}, session=session) is not None
            session.abort_transaction()
        assert probe.count_documents({"probe_id": probe_id}) == 0

        # Case 02: exact physical four-index definitions and idempotent setup.
        facts, pointers = _pair(database, "main")
        _assert_index(facts, FACT_IDENTITY_INDEX_NAME, ["tenant_id", METADATA_FACT_ID_FIELD])
        _assert_index(facts, IDEMPOTENCY_INDEX_NAME, ["tenant_id", "provider_id", "merchant_configuration_id", "merchant_configuration_version", IDEMPOTENCY_KEY_FIELD])
        _assert_index(facts, CREDENTIAL_VERSION_INDEX_NAME, ["tenant_id", "provider_id", "merchant_configuration_id", "merchant_configuration_version", "credential_version"])
        _assert_index(pointers, CURRENT_POINTER_INDEX_NAME, ["tenant_id", "provider_id", "merchant_configuration_id", "merchant_configuration_version"])
        before_indexes = list(facts.list_indexes()) + list(pointers.list_indexes())
        ensure_indexes(facts, pointers)
        after_indexes = list(facts.list_indexes()) + list(pointers.list_indexes())
        assert before_indexes == after_indexes

        # Case 03: physical fact-ID uniqueness, bypassing registry precheck.
        fact_id_facts, fact_id_pointers = _pair(database, "fact_id")
        first = _metadata(credential_version="fact-id-v1")
        fact_id_document = _document(first, "fact-id-key-1")
        fact_id_facts.insert_one(fact_id_document)
        duplicate_fact_id = _document(_metadata(credential_version="fact-id-v2"), "fact-id-key-2")
        duplicate_fact_id[METADATA_FACT_ID_FIELD] = fact_id_document[METADATA_FACT_ID_FIELD]
        with pytest.raises(DuplicateKeyError) as fact_id_error:
            fact_id_facts.insert_one(duplicate_fact_id)
        assert type(fact_id_error.value).__name__ == "DuplicateKeyError"

        # Case 04: physical credential-version uniqueness, divergent provenance.
        version_facts, version_pointers = _pair(database, "credential_version")
        version_first = _metadata(credential_version="same-version", provenance="prov-one")
        version_second = _metadata(credential_version="same-version", provenance="prov-two")
        version_facts.insert_one(_document(version_first, "version-key-1"))
        with pytest.raises(DuplicateKeyError) as version_error:
            version_facts.insert_one(_document(version_second, "version-key-2"))
        assert type(version_error.value).__name__ == "DuplicateKeyError"

        # Case 05: physical tenant/provider/config/version/idempotency uniqueness.
        idem_facts, idem_pointers = _pair(database, "idempotency")
        idem_facts.insert_one(_document(_metadata(credential_version="idem-v1"), "same-idempotency"))
        with pytest.raises(DuplicateKeyError) as idem_error:
            idem_facts.insert_one(_document(_metadata(credential_version="idem-v2"), "same-idempotency"))
        assert type(idem_error.value).__name__ == "DuplicateKeyError"

        # Case 06: physical current-pointer uniqueness for the four-field stream.
        pointer_facts, pointer_collection = _pair(database, "pointer")
        pointer_value = _metadata(credential_version="pointer-v1")
        pointer_facts.insert_one(_document(pointer_value, "pointer-key"))
        pointer_document = {
            "tenant_id": pointer_value.tenant_id,
            "provider_id": pointer_value.provider_id,
            "merchant_configuration_id": pointer_value.merchant_configuration_id,
            "merchant_configuration_version": pointer_value.merchant_configuration_version,
            "merchant_configuration_fingerprint": pointer_value.merchant_configuration_fingerprint,
            METADATA_FACT_ID_FIELD: pointer_value.fingerprint,
            "credential_reference": pointer_value.credential_reference,
            "credential_version": pointer_value.credential_version,
            "metadata_fingerprint": pointer_value.fingerprint,
        }
        pointer_collection.insert_one(pointer_document)
        with pytest.raises(DuplicateKeyError) as pointer_error:
            pointer_collection.insert_one({**pointer_document, METADATA_FACT_ID_FIELD: "f" * 128, "credential_version": "pointer-v2"})
        assert type(pointer_error.value).__name__ == "DuplicateKeyError"
        assert pointer_collection.count_documents({}) == 1

        # Case 07: initial fact and pointer commit together under caller ownership.
        initial_value = _metadata(credential_version="initial-v1")
        initial_facts, initial_pointers = _pair(database, "initial")
        _persist(initial_value, "initial-key", initial_facts, initial_pointers, client)
        assert initial_facts.count_documents({}) == 1
        assert initial_pointers.count_documents({}) == 1
        initial_pointer = initial_pointers.find_one({})
        assert initial_pointer and initial_pointer[METADATA_FACT_ID_FIELD] == _document(initial_value, "x")[METADATA_FACT_ID_FIELD]

        # Case 08: real transaction abort removes both fact and pointer.
        abort_facts, abort_pointers = _pair(database, "abort")
        abort_value = _metadata(credential_version="abort-v1")
        with client.start_session() as session:
            session.start_transaction()
            persist_fact_and_advance_current(abort_value, "abort-key", None, None, fact_collection=abort_facts, pointer_collection=abort_pointers, session=session)
            session.abort_transaction()
        assert abort_facts.count_documents({}) == 0
        assert abort_pointers.count_documents({}) == 0

        # Case 09: lawful CAS success advances pointer while V1 remains immutable.
        cas_facts, cas_pointers = _pair(database, "cas")
        cas_v1 = _metadata(credential_version="cas-v1")
        _persist(cas_v1, "cas-key-v1", cas_facts, cas_pointers, client)
        v1_snapshot = _snapshot(cas_facts, {METADATA_FACT_ID_FIELD: _document(cas_v1, "x")[METADATA_FACT_ID_FIELD]})
        v1_row = cas_facts.find_one({"credential_version": "cas-v1"})
        assert v1_row is not None
        cas_v2 = _metadata(credential_version="cas-v2", observed_at=AT + timedelta(minutes=2))
        _persist(cas_v2, "cas-key-v2", cas_facts, cas_pointers, client, prior_fact_id=cast(str, v1_row[METADATA_FACT_ID_FIELD]), prior_metadata_fingerprint=cast(str, v1_row["metadata_fingerprint"]), prior_configuration_fingerprint=CONFIGURATION_FINGERPRINT)
        assert cas_pointers.find_one({})["credential_version"] == "cas-v2"
        assert _snapshot(cas_facts, {METADATA_FACT_ID_FIELD: v1_row[METADATA_FACT_ID_FIELD]}) == v1_snapshot

        # Case 10: stale CAS fails closed and caller abort leaves no orphan.
        stale_value = _metadata(credential_version="cas-stale")
        with client.start_session() as session:
            session.start_transaction()
            with pytest.raises(TenantInboundProviderCredentialMaterialMetadataRegistryCASConflictError):
                persist_fact_and_advance_current(stale_value, "cas-stale-key", "wrong", "b" * 128, expected_prior_configuration_fingerprint=CONFIGURATION_FINGERPRINT, fact_collection=cas_facts, pointer_collection=cas_pointers, session=session)
            session.abort_transaction()
        assert cas_facts.count_documents({"credential_version": "cas-stale"}) == 0
        assert cas_pointers.find_one({})["credential_version"] == "cas-v2"

        # Case 11: two independent transactions race from identical antecedents.
        race_v1 = _metadata(credential_version="race-v1")
        race_facts, race_pointers = _pair(database, "race")
        _persist(race_v1, "race-key-v1", race_facts, race_pointers, client)
        race_row = race_facts.find_one({})
        assert race_row is not None
        race_prior_id = cast(str, race_row[METADATA_FACT_ID_FIELD])
        race_prior_fp = cast(str, race_row["metadata_fingerprint"])
        barrier = Barrier(2)

        def contender(value_: TenantInboundProviderCredentialMaterialMetadata, key_: str) -> str:
            with client.start_session() as session:
                session.start_transaction()
                barrier.wait()
                try:
                    persist_fact_and_advance_current(value_, key_, race_prior_id, race_prior_fp, expected_prior_configuration_fingerprint=CONFIGURATION_FINGERPRINT, fact_collection=race_facts, pointer_collection=race_pointers, session=session)
                    session.commit_transaction()
                    return "committed"
                except Exception as error:
                    if session.in_transaction:
                        session.abort_transaction()
                    return type(error).__name__

        with ThreadPoolExecutor(max_workers=2) as pool:
            outcomes = list(pool.map(contender, [_metadata(credential_version="race-v2a"), _metadata(credential_version="race-v2b")], ["race-key-a", "race-key-b"]))
        assert sum(result == "committed" for result in outcomes) == 1
        assert race_pointers.count_documents({}) == 1
        assert race_facts.count_documents({}) == 2
        assert any(result not in {"committed"} for result in outcomes)

        # Case 12: exact replay writes neither fact nor pointer.
        replay_facts, replay_pointers = _pair(database, "replay")
        replay_value = _metadata(credential_version="replay-v1")
        _persist(replay_value, "replay-key", replay_facts, replay_pointers, client)
        replay_before = (_snapshot(replay_facts, {}), _snapshot(replay_pointers, {}))
        with client.start_session() as session:
            session.start_transaction()
            replay_result = persist_fact_and_advance_current(replay_value, "replay-key", None, None, fact_collection=replay_facts, pointer_collection=replay_pointers, session=session)
            session.commit_transaction()
        assert replay_result == replay_value
        assert (_snapshot(replay_facts, {}), _snapshot(replay_pointers, {})) == replay_before

        # Case 13: re-observation is not replay and does not rewrite observed_at.
        reobs_facts, reobs_pointers = _pair(database, "reobservation")
        reobs_value = _metadata(credential_version="reobs-v1", observed_at=AT)
        _persist(reobs_value, "reobs-key-1", reobs_facts, reobs_pointers, client)
        reobs_before = (_snapshot(reobs_facts, {}), _snapshot(reobs_pointers, {}))
        reobs_later = _metadata(credential_version="reobs-v1", observed_at=AT + timedelta(hours=1))
        with client.start_session() as session:
            session.start_transaction()
            reobs_result = persist_fact_and_advance_current(reobs_later, "reobs-key-2", None, None, fact_collection=reobs_facts, pointer_collection=reobs_pointers, session=session)
            session.commit_transaction()
        assert reobs_result == reobs_value
        assert (_snapshot(reobs_facts, {}), _snapshot(reobs_pointers, {})) == reobs_before
        assert reobs_facts.find_one({})["observed_at"] == AT.isoformat()
        assert reobs_result.fingerprint == reobs_value.fingerprint

        # Case 14: same key with different observed_at is a replay conflict.
        with client.start_session() as session:
            session.start_transaction()
            with pytest.raises(TenantInboundProviderCredentialMaterialMetadataRegistryIdempotencyConflictError):
                persist_fact_and_advance_current(reobs_later, "reobs-key-1", None, None, fact_collection=reobs_facts, pointer_collection=reobs_pointers, session=session)
            session.abort_transaction()
        assert reobs_facts.count_documents({}) == 1

        # Case 15: same stream/version divergent provenance is rejected.
        divergent = _metadata(credential_version="reobs-v1", provenance="divergent-provenance")
        with client.start_session() as session:
            session.start_transaction()
            with pytest.raises(Exception):
                persist_fact_and_advance_current(divergent, "divergent-key", None, None, fact_collection=reobs_facts, pointer_collection=reobs_pointers, session=session)
            session.abort_transaction()
        assert reobs_facts.count_documents({}) == 1

        # Case 16: current lookup resolves only the four-field stream pointer.
        with _read_transaction(client) as read_session:
            current = get_current_metadata(TENANT_A, PROVIDER, CONFIGURATION, 1, CONFIGURATION_FINGERPRINT, fact_collection=reobs_facts, pointer_collection=reobs_pointers, session=read_session)
        assert current is not None and current.credential_version == "reobs-v1"

        # Case 17: corrupt pointer reference fails closed without lookup mutation.
        corrupt_pointer_facts, corrupt_pointer_collection = _pair(database, "corrupt_pointer")
        corrupt_value = _metadata(credential_version="corrupt-pointer-v1")
        _persist(corrupt_value, "corrupt-pointer-key", corrupt_pointer_facts, corrupt_pointer_collection, client)
        corrupt_pointer_collection.update_one({}, {"$set": {METADATA_FACT_ID_FIELD: "f" * 128}})
        pointer_count_before = corrupt_pointer_collection.count_documents({})
        with pytest.raises(TenantInboundProviderCredentialMaterialMetadataRegistryPersistedRecordInvalidError):
            with _read_transaction(client) as read_session:
                get_current_metadata(TENANT_A, PROVIDER, CONFIGURATION, 1, CONFIGURATION_FINGERPRINT, fact_collection=corrupt_pointer_facts, pointer_collection=corrupt_pointer_collection, session=read_session)
        assert corrupt_pointer_collection.count_documents({}) == pointer_count_before

        # Case 18: corrupt fact strict hydration fails closed.
        corrupt_fact_facts, corrupt_fact_pointers = _pair(database, "corrupt_fact")
        corrupt_fact_value = _metadata(credential_version="corrupt-fact-v1")
        _persist(corrupt_fact_value, "corrupt-fact-key", corrupt_fact_facts, corrupt_fact_pointers, client)
        corrupt_fact_id = cast(str, corrupt_fact_facts.find_one({})[METADATA_FACT_ID_FIELD])
        corrupt_fact_facts.update_one({METADATA_FACT_ID_FIELD: corrupt_fact_id}, {"$set": {"metadata_fingerprint": "bad"}})
        with pytest.raises(TenantInboundProviderCredentialMaterialMetadataRegistryPersistedRecordInvalidError):
            with _read_transaction(client) as read_session:
                get_fact(TENANT_A, corrupt_fact_id, corrupt_fact_facts, session=read_session)

        # Case 19: same key/version coexist across tenants and remain isolated.
        tenant_facts, tenant_pointers = _pair(database, "tenant")
        tenant_a = _metadata(TENANT_A, credential_version="tenant-v1")
        tenant_b = _metadata(TENANT_B, credential_version="tenant-v1")
        _persist(tenant_a, "same-tenant-key", tenant_facts, tenant_pointers, client)
        _persist(tenant_b, "same-tenant-key", tenant_facts, tenant_pointers, client)
        assert tenant_facts.count_documents({}) == 2
        with _read_transaction(client) as read_session:
            tenant_current = get_current_metadata(TENANT_A, PROVIDER, CONFIGURATION, 1, CONFIGURATION_FINGERPRINT, fact_collection=tenant_facts, pointer_collection=tenant_pointers, session=read_session)
        assert tenant_current is not None and tenant_current.tenant_id == TENANT_A

        # Case 20: genuine configuration-version streams are independent.
        config_facts, config_pointers = _pair(database, "configuration_version")
        config_v1 = _metadata(TENANT_A, configuration_version=1, credential_version="same-version")
        config_v2 = _metadata(TENANT_A, configuration_version=2, credential_version="same-version")
        _persist(config_v1, "config-v1-key", config_facts, config_pointers, client)
        _persist(config_v2, "config-v2-key", config_facts, config_pointers, client)
        assert config_pointers.count_documents({}) == 2
        assert config_pointers.count_documents({"merchant_configuration_version": 1}) == 1
        assert config_pointers.count_documents({"merchant_configuration_version": 2}) == 1

        # Case 21: wrong configuration fingerprint correlates and fails closed.
        with pytest.raises(Exception):
            with _read_transaction(client) as read_session:
                get_current_metadata(TENANT_A, PROVIDER, CONFIGURATION, 1, "b" * 128, fact_collection=config_facts, pointer_collection=config_pointers, session=read_session)
        assert config_pointers.count_documents({}) == 2

        # Case 22: index setup second run has no duplicate variants.
        ensure_indexes(config_facts, config_pointers)
        assert len(list(config_facts.list_indexes())) == 4
        assert len(list(config_pointers.list_indexes())) == 2

        # Case 23: historical fact snapshots remain unchanged across transitions/replay/re-observation.
        assert _snapshot(config_facts, {"credential_version": "same-version"})[0] == 2
        assert _snapshot(replay_facts, {}) == replay_before[0]
        assert _snapshot(reobs_facts, {}) == reobs_before[0]

        # Case 24: bounded cleanup is guaranteed by this finally block.
        assert database_name.startswith("wilsy_p5_r7_metadata_")
    finally:
        client.drop_database(database_name)
        client.close()
# ARTIFACT: test_tenant_inbound_provider_credential_material_metadata_registry_real_mongo.py
# VERSION: v1.0.0-M11-R8-R3B-P8-P3D-P5-R7
# AUTHORITY BOUNDARY: bounded host-backed registry evidence only.
# TENANT POSTURE: unique ephemeral database; all physical uniqueness is tenant-scoped.
# FAIL-CLOSED POSTURE: any host, transaction, durability, replay, CAS, hydration, or cleanup failure fails.
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively.
# END OF WILSY OS SOVEREIGN ARTIFACT
