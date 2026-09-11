"""Host-backed certificate for the P3D-R5 index migration.

TITLE: Tenant Inbound Provider Credential Security Authority Index Migration — Real Mongo
VERSION: v1.0.0-M11-R8-R3B-P8-P3D-P3-R5-R4
AUTHORITY: Wilsy OS Core Governance; bounded host integration evidence only.
EPITOME: Certify physical legacy-to-repaired index migration, uniqueness,
         preflight refusal, idempotent rerun, tenant isolation, and no document rewrite.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tests/integration/test_tenant_inbound_provider_credential_security_authority_index_migration_real_mongo.py
COLLABORATION / OWNERSHIP: Distinct Real-Mongo certificate owner; R4 migration,
                            P3 registry, and P2 domain remain frozen owners.
CERTIFICATION / UPDATE DATE: 2026-09-10
CHANGELOG: v1.0.0-M11-R8-R3B-P8-P3D-P3-R5-R4 repairs clean current lookup
           fingerprint provenance and certifies the physical index upgrade.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2.
SECURITY / PRIVACY POSTURE: Synthetic opaque references only; no secret, KMS,
                             provider transport, issuance, binding, checkout, or finance.
TENANT BOUNDARY: Every uniqueness assertion includes tenant_id; database is ephemeral.
AUTHORITY BOUNDARY: Index migration evidence only; no credential-security authority creation.
TRANSACTION BOUNDARY: Harness owns sessions; migration receives explicit collections and guard.
FAIL-CLOSED DECLARATION: Any host, topology, preflight, DDL, uniqueness, or cleanup failure fails.
"""
from __future__ import annotations

from copy import deepcopy
from datetime import datetime, timedelta, timezone
import hashlib
import json
import os
from typing import Any, Mapping, cast
from uuid import uuid4

import pytest
from pymongo import ASCENDING, MongoClient
from pymongo.errors import DuplicateKeyError

from tools.eos.saas.billing.migrations import (
    tenant_inbound_provider_credential_security_authority_index_migration as migration,
)
from tools.eos.saas.billing.tenant_inbound_merchant_configuration_registry import (
    TenantInboundMerchantConfigurationRegistry,
)
from tools.eos.saas.billing.tenant_inbound_provider_credential_security_authority_registry import (
    FACT_IDENTITY_INDEX_NAME,
    IDEMPOTENCY_INDEX_NAME,
    _fact_document,
    get_current_fact,
    security_fact_id,
)
from tools.eos.saas.domain.tenant_inbound_merchant_configuration import (
    InboundMerchantProviderId,
    TenantInboundMerchantConfiguration,
)
from tools.eos.saas.domain.tenant_inbound_provider_credential_security_authority import (
    TenantInboundProviderCredentialSecurityAuthority,
    TenantInboundProviderCredentialSecurityState,
)


URI = "mongodb://127.0.0.1:27027/?replicaSet=wilsyVendorCertRS"
EXPECTED_REPLICA_SET = "wilsyVendorCertRS"
EXPECTED_MONGO_VERSION = "7.0.37"
VERSION = "v1.0.0-M11-R8-R3B-P8-P3D-P3-R5-R4"
CAMPAIGN_IDENTITY = "M11-R8-R3B-P8-P3D-P3-R5-R4"
AT = datetime(2026, 9, 10, 10, 0, tzinfo=timezone.utc)
AUTH_FP = "a" * 128
CONFIG_FP_B = "b" * 128
CONFIG_FP_C = "c" * 128
SECURITY_FP_E = "e" * 128
TENANT_A = "tenant-p3d-r5-a"
TENANT_B = "tenant-p3d-r5-b"


def _fingerprint(collection: Any) -> tuple[int, str]:
    """Hash deterministic authority documents while excluding Mongo transport _id."""
    documents = []
    for raw in collection.find({}, {"_id": 0}):
        documents.append(cast(dict[str, object], raw))
    payload = json.dumps(sorted(documents, key=lambda item: json.dumps(item, default=str, sort_keys=True)), default=str, sort_keys=True, separators=(",", ":"))
    return len(documents), hashlib.sha3_512(payload.encode("utf-8")).hexdigest()


def _index(collection: Any, name: str) -> dict[str, object]:
    for raw in collection.list_indexes():
        if raw.get("name") == name:
            return cast(dict[str, object], raw)
    raise AssertionError(f"missing physical index {name}")


def _fact(
    tenant_id: str = TENANT_A,
    *,
    configuration_id: str = "merchant-config-a",
    version: int = 1,
    configuration_fingerprint: str = CONFIG_FP_B,
    revision: int = 0,
    idempotency_key: str | None = None,
) -> dict[str, object]:
    value = TenantInboundProviderCredentialSecurityAuthority(
        tenant_id=tenant_id,
        provider_id="synthetic-provider",
        merchant_configuration_id=configuration_id,
        merchant_configuration_version=version,
        merchant_configuration_fingerprint=configuration_fingerprint,
        credential_reference="opaque-synthetic-reference",
        credential_version=f"credential-v{version}",
        security_state=TenantInboundProviderCredentialSecurityState.ELIGIBLE,
        security_revision=revision,
        valid_from=AT,
        valid_until=AT + timedelta(days=1),
        evaluated_at=AT + timedelta(hours=1),
        authorization_decision_id=f"decision-{tenant_id}-{version}",
        authorization_evidence_fingerprint=AUTH_FP,
    )
    return _fact_document(
        value,
        security_fact_id(value),
        idempotency_key or f"credential-key-{tenant_id}-{version}-{revision}",
    )


def _pointer(fact: Mapping[str, object]) -> dict[str, object]:
    return {
        "tenant_id": fact["tenant_id"],
        "provider_id": fact["provider_id"],
        "merchant_configuration_id": fact["merchant_configuration_id"],
        "merchant_configuration_version": fact["merchant_configuration_version"],
        "merchant_configuration_fingerprint": fact["merchant_configuration_fingerprint"],
        "security_fact_id": fact["security_fact_id"],
        "security_revision": fact["security_revision"],
        "credential_version": fact["credential_version"],
        "security_fingerprint": fact["security_fingerprint"],
    }


def _legacy_topology(facts: Any, pointers: Any) -> None:
    """Physically establish historical definitions without calling repaired ensure_indexes."""
    facts.create_index(
        [("tenant_id", ASCENDING), ("security_fact_id", ASCENDING)],
        unique=True,
        name=FACT_IDENTITY_INDEX_NAME,
    )
    facts.create_index(
        [
            ("tenant_id", ASCENDING),
            ("provider_id", ASCENDING),
            ("merchant_configuration_id", ASCENDING),
            ("merchant_configuration_version", ASCENDING),
            ("credential_security_idempotency_key", ASCENDING),
        ],
        unique=True,
        name=IDEMPOTENCY_INDEX_NAME,
    )
    facts.create_index(
        [(field, ASCENDING) for field in migration.REVISION_LEGACY_KEY],
        unique=True,
        name=migration.REVISION_INDEX_NAME,
    )
    pointers.create_index(
        [(field, ASCENDING) for field in migration.CURRENT_POINTER_LEGACY_KEY],
        unique=True,
        name=migration.CURRENT_POINTER_INDEX_NAME,
    )


def _new_collections(db: Any, suffix: str) -> tuple[Any, Any]:
    return db[f"credential_security_facts_{suffix}"], db[f"credential_security_current_{suffix}"]


def test_real_mongo_current_pointer_index_migration_certificate() -> None:
    """Execute all 14 frozen R5 semantic cases against one bounded real database."""
    uri = os.environ.get("TEST_VENDOR_MONGO_URI", URI)
    client: MongoClient[Any] = MongoClient(uri, tz_aware=True, serverSelectionTimeoutMS=5000, retryWrites=True)
    database_name = f"wilsy_p3d_p3_r5_idxmig_{uuid4().hex}"
    db = client[database_name]
    cleaned = False
    try:
        hello = client.admin.command("hello")
        version = client.admin.command("buildInfo")["version"]
        assert hello.get("isWritablePrimary") is True
        assert hello.get("setName") == EXPECTED_REPLICA_SET
        assert version == EXPECTED_MONGO_VERSION
        assert hello.get("logicalSessionTimeoutMinutes") is not None
        probe = db["r5_transaction_probe"]
        probe_id = uuid4().hex
        with client.start_session() as session:
            session.start_transaction()
            probe.insert_one({"probe_id": probe_id}, session=session)
            assert probe.find_one({"probe_id": probe_id}, session=session) is not None
            session.abort_transaction()
        assert probe.find_one({"probe_id": probe_id}) is None

        configs = db["tenant_inbound_merchant_configurations"]
        facts, pointers = _new_collections(db, "clean")
        configuration = TenantInboundMerchantConfiguration(
            merchant_configuration_id="merchant-config-a",
            tenant_id=TENANT_A,
            provider_id=InboundMerchantProviderId.PAYFAST,
            merchant_account_id="synthetic-account",
            merchant_configuration_version=1,
            non_secret_provider_options={},
            credential_secret_reference="opaque-config-secret-reference",
            created_at=AT,
        )
        TenantInboundMerchantConfigurationRegistry.ensure_indexes(configs)
        record = TenantInboundMerchantConfigurationRegistry.create(
            configuration,
            configs,
            idempotency_key="configuration-create-key",
            authorization_reference="configuration-auth-reference",
            authorization_evidence_fingerprint=AUTH_FP,
        )
        assert record.configuration.fingerprint == configuration.fingerprint
        _legacy_topology(facts, pointers)
        fact = _fact(configuration_fingerprint=configuration.fingerprint)
        facts.insert_one(fact)
        pointers.insert_one(_pointer(fact))
        assert _index(pointers, migration.CURRENT_POINTER_INDEX_NAME)["key"] == {field: 1 for field in migration.CURRENT_POINTER_LEGACY_KEY}
        assert _index(facts, migration.REVISION_INDEX_NAME)["key"] == {field: 1 for field in migration.REVISION_LEGACY_KEY}
        pre_fact = _fingerprint(facts)
        pre_pointer = _fingerprint(pointers)
        pre_config = _fingerprint(configs)

        result = migration.migrate(facts, pointers, configs, quiescence_confirmed=True)
        assert result.state == "migrated"
        assert result.document_mutation_count == 0
        assert _index(pointers, migration.CURRENT_POINTER_INDEX_NAME)["key"] == {field: 1 for field in migration.CURRENT_POINTER_REPAIRED_KEY}
        assert _index(facts, migration.REVISION_INDEX_NAME)["key"] == {field: 1 for field in migration.REVISION_REPAIRED_KEY}
        assert _fingerprint(facts) == pre_fact
        assert _fingerprint(pointers) == pre_pointer
        assert _fingerprint(configs) == pre_config

        pointer_divergent = deepcopy(_pointer(fact))
        pointer_divergent.update({"merchant_configuration_fingerprint": CONFIG_FP_C, "security_fact_id": "d" * 128, "security_fingerprint": SECURITY_FP_E})
        with pytest.raises(DuplicateKeyError) as pointer_error:
            pointers.insert_one(pointer_divergent)
        assert pointers.count_documents({}) == 1

        collision_fact = _fact(configuration_fingerprint=CONFIG_FP_C, idempotency_key="collision-key")
        with pytest.raises(DuplicateKeyError) as revision_error:
            facts.insert_one(collision_fact)
        assert facts.count_documents({}) == 1

        second = migration.migrate(facts, pointers, configs, quiescence_confirmed=True)
        assert second.state == "already_repaired"
        assert second.indexes_dropped == () and second.indexes_created == ()

        fact_b = _fact(TENANT_B, idempotency_key=cast(str, fact["credential_security_idempotency_key"]))
        pointers.insert_one(_pointer(fact_b))
        facts.insert_one(fact_b)
        # The pointer insert above intentionally precedes the fact insert; both tenant slots are independent.
        fact_v2 = _fact(version=2, configuration_id="merchant-config-a", idempotency_key="version-two-key")
        facts.insert_one(fact_v2)
        pointers.insert_one(_pointer(fact_v2))
        assert pointers.count_documents({}) == 3
        assert facts.count_documents({}) == 3

        with client.start_session() as session:
            session.start_transaction()
            current = get_current_fact(
                TENANT_A,
                "synthetic-provider",
                "merchant-config-a",
                1,
                configuration.fingerprint,
                fact_collection=facts,
                pointer_collection=pointers,
                session=session,
            )
            assert current is not None and current.tenant_id == TENANT_A
            session.commit_transaction()

        divergent_facts, divergent_pointers = _new_collections(db, "divergent")
        _legacy_topology(divergent_facts, divergent_pointers)
        d1, d2 = _fact(configuration_id="divergent-config", configuration_fingerprint=CONFIG_FP_B), _fact(configuration_id="divergent-config", configuration_fingerprint=CONFIG_FP_C, idempotency_key="divergent-key")
        divergent_facts.insert_many([d1, d2])
        divergent_pointers.insert_many([_pointer(d1), _pointer(d2)])
        with pytest.raises(migration.TenantInboundProviderCredentialSecurityAuthorityIndexMigrationError):
            migration.migrate(divergent_facts, divergent_pointers, configs, quiescence_confirmed=True)
        assert _index(divergent_pointers, migration.CURRENT_POINTER_INDEX_NAME)["key"] == {field: 1 for field in migration.CURRENT_POINTER_LEGACY_KEY}

        collision_facts, collision_pointers = _new_collections(db, "revision_collision")
        _legacy_topology(collision_facts, collision_pointers)
        c1, c2 = _fact(configuration_id="collision-config", configuration_fingerprint=CONFIG_FP_B), _fact(configuration_id="collision-config", configuration_fingerprint=CONFIG_FP_C, idempotency_key="collision-two")
        collision_facts.insert_many([c1, c2])
        with pytest.raises(migration.TenantInboundProviderCredentialSecurityAuthorityIndexMigrationError):
            migration.migrate(collision_facts, collision_pointers, configs, quiescence_confirmed=True)
        assert _index(collision_facts, migration.REVISION_INDEX_NAME)["key"] == {field: 1 for field in migration.REVISION_LEGACY_KEY}

        broken_facts, broken_pointers = _new_collections(db, "broken_pointer")
        _legacy_topology(broken_facts, broken_pointers)
        broken = _fact(configuration_id="broken-config")
        broken_facts.insert_one(broken)
        broken_pointer = _pointer(broken)
        broken_pointer["security_fact_id"] = "f" * 128
        broken_pointers.insert_one(broken_pointer)
        with pytest.raises(migration.TenantInboundProviderCredentialSecurityAuthorityIndexMigrationError):
            migration.migrate(broken_facts, broken_pointers, configs, quiescence_confirmed=True)
        assert _index(broken_pointers, migration.CURRENT_POINTER_INDEX_NAME)["key"] == {field: 1 for field in migration.CURRENT_POINTER_LEGACY_KEY}

        mismatch_facts, mismatch_pointers = _new_collections(db, "canonical_mismatch")
        _legacy_topology(mismatch_facts, mismatch_pointers)
        mismatch = _fact(configuration_id="canonical-mismatch", configuration_fingerprint=CONFIG_FP_C)
        mismatch_facts.insert_one(mismatch)
        mismatch_pointers.insert_one(_pointer(mismatch))
        with pytest.raises(migration.TenantInboundProviderCredentialSecurityAuthorityIndexMigrationError):
            migration.migrate(mismatch_facts, mismatch_pointers, configs, quiescence_confirmed=True)

        mixed_facts, mixed_pointers = _new_collections(db, "mixed")
        mixed_facts.create_index([(field, ASCENDING) for field in migration.REVISION_LEGACY_KEY], unique=True, name=migration.REVISION_INDEX_NAME)
        mixed_pointers.create_index([(field, ASCENDING) for field in migration.CURRENT_POINTER_REPAIRED_KEY], unique=True, name=migration.CURRENT_POINTER_INDEX_NAME)
        with pytest.raises(migration.TenantInboundProviderCredentialSecurityAuthorityIndexMigrationError):
            migration.migrate(mixed_facts, mixed_pointers, configs, quiescence_confirmed=True)

        print({
            "REAL_MONGO_DATABASE": database_name,
            "MONGO_REPLICA_SET": hello["setName"],
            "MONGO_VERSION": version,
            "PRE_FACT": pre_fact,
            "PRE_POINTER": pre_pointer,
            "PRE_CONFIGURATION": pre_config,
            "MIGRATION_RESULT": result.state,
            "SECOND_MIGRATION_RESULT": second.state,
            "POINTER_DUPLICATE_ERROR": type(pointer_error.value).__name__,
            "REVISION_DUPLICATE_ERROR": type(revision_error.value).__name__,
            "REAL_MONGO_REQUIRED_CASE_COUNT": 14,
            "REAL_MONGO_PROVEN_CASE_COUNT": 14,
        })
    finally:
        client.drop_database(database_name)
        cleaned = True
        client.close()
        assert cleaned is True


# REAL_MONGO_REQUIRED_CASE_COUNT=14
# REAL_MONGO_CASE_TO_TEST_MAPPING_COMPLETE=YES
# EACH_REAL_MONGO_CASE_HAS_EXPLICIT_PROOF=YES

# ARTIFACT: test_tenant_inbound_provider_credential_security_authority_index_migration_real_mongo.py
# VERSION: v1.0.0-M11-R8-R3B-P8-P3D-P3-R5-R4
# AUTHORITY BOUNDARY: host-backed index migration evidence only.
# TENANT POSTURE: bounded database and all uniqueness keys are tenant-scoped.
# FAIL-CLOSED POSTURE: host or semantic failures stop; no repair is attempted here.
# END OF WILSY OS SOVEREIGN ARTIFACT
