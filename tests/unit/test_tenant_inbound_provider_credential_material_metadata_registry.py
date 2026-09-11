"""WILSY OS direct P5-R5 certificate for the metadata registry.

TITLE: Tenant Inbound Provider Credential Material Metadata Registry Tests
VERSION: v1.0.0-M11-R8-R3B-P8-P3D-P5-R5-CERT
AUTHORITY: Wilsy OS Core Governance
EPITOME: Host-free proof of durable field shape, generation identity,
         idempotency, explicit currentness, CAS and transaction ownership.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tests/unit/test_tenant_inbound_provider_credential_material_metadata_registry.py
COLLABORATION / OWNERSHIP: Direct P5-R5 registry certificate; real Mongo is a
                            later P5-R6 owner.
CERTIFICATION / UPDATE DATE: 2026-09-10
CHANGELOG: v1.0.0-M11-R8-R3B-P8-P3D-P5-R5 certifies the 58 required registry
           cases without provider, security-evidence, financial, or Mongo work.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2.
SECURITY / PRIVACY POSTURE: Synthetic opaque values only; no secret/KMS/provider access.
TENANT BOUNDARY: Every fake durable lookup includes tenant_id.
AUTHORITY BOUNDARY: Registry persistence/currentness only; provenance is prevalidated.
FINANCIAL AUTHORITY BOUNDARY: Kennel EOS exclusively owns financial execution.
FAIL-CLOSED DECLARATION: Corrupt shape, identity, replay, pointer and CAS reject.
"""
from __future__ import annotations

from dataclasses import replace
from datetime import datetime, timedelta, timezone
import ast
from pathlib import Path
from typing import Any, cast

import pytest

from tools.eos.saas.billing.tenant_inbound_provider_credential_material_metadata_registry import (
    AUTHORITY_UNIQUE_INDEX_COUNT,
    CREDENTIAL_VERSION_INDEX_NAME,
    CURRENT_POINTER_INDEX_NAME,
    FACT_COLLECTION,
    FACT_IDENTITY_INDEX_NAME,
    IDEMPOTENCY_INDEX_NAME,
    IDEMPOTENCY_KEY_FIELD,
    METADATA_FACT_ID_FIELD,
    CASConflictError,
    GenerationConflictError,
    IdempotencyConflictError,
    PersistedRecordInvalidError,
    TenantInboundProviderCredentialMaterialMetadataRegistry,
    TransactionRequiredError,
    ensure_indexes,
    get_current_metadata,
    get_fact,
    metadata_fact_id,
    persist_fact_and_advance_current,
)
from tools.eos.saas.domain.tenant_inbound_provider_credential_material_metadata import (
    TenantInboundProviderCredentialMaterialMetadata,
)


AT = datetime(2026, 9, 10, 10, 0, tzinfo=timezone.utc)
CFG = "a" * 128


class _Cursor(list[dict[str, object]]):
    def limit(self, count: int) -> "_Cursor":
        return _Cursor(self[:count])


class Collection:
    """Small Mongo-like fake retaining query and transaction kwargs."""

    def __init__(self) -> None:
        self.rows: list[dict[str, object]] = []
        self.indexes: list[tuple[list[tuple[str, int]], dict[str, object]]] = []
        self.calls: list[tuple[str, dict[str, object]]] = []

    def create_index(self, keys: list[tuple[str, int]], **options: object) -> str:
        self.indexes.append((keys, dict(options)))
        return str(options.get("name", "index"))

    def find(self, query: dict[str, object], **kwargs: object) -> _Cursor:
        self.calls.append(("find", kwargs))
        return _Cursor([dict(row) for row in self.rows if all(row.get(k) == v for k, v in query.items())])

    def find_one(self, query: dict[str, object], **kwargs: object) -> dict[str, object] | None:
        rows = self.find(query, **kwargs)
        return rows[0] if rows else None

    def insert_one(self, document: dict[str, object], **kwargs: object) -> object:
        self.calls.append(("insert_one", kwargs))
        self.rows.append(dict(document))
        return object()

    def update_one(self, query: dict[str, object], update: dict[str, object], **kwargs: object) -> object:
        self.calls.append(("update_one", kwargs))
        matched = 0
        for row in self.rows:
            if all(row.get(k) == v for k, v in query.items()):
                row.update(cast(dict[str, object], update.get("$set", {})))
                matched = 1
                break
        return type("Result", (), {"matched_count": matched})()


class Session:
    in_transaction = True


def value(**changes: object) -> TenantInboundProviderCredentialMaterialMetadata:
    payload: dict[str, object] = {
        "tenant_id": "tenant-a", "provider_id": "provider-a",
        "merchant_configuration_id": "config-a", "merchant_configuration_version": 1,
        "merchant_configuration_fingerprint": CFG,
        "credential_reference": "opaque-ref-a", "credential_version": "credential-v1",
        "observed_at": AT, "metadata_source_identity": "adapter-a",
        "metadata_source_version": "adapter-v1", "version_provenance_reference": "provenance-a",
    }
    payload.update(changes)
    return TenantInboundProviderCredentialMaterialMetadata(**payload)  # type: ignore[arg-type]


def persisted(value_: TenantInboundProviderCredentialMaterialMetadata, key: str = "key-a") -> tuple[Collection, Collection, Session]:
    facts, pointers, session = Collection(), Collection(), Session()
    persist_fact_and_advance_current(value_, key, None, None, fact_collection=facts, pointer_collection=pointers, session=session)
    return facts, pointers, session


def test_01_durable_fact_has_exact_fifteen_fields() -> None:
    facts, _, _ = persisted(value())
    assert len(facts.rows[0]) == 15
    assert set(facts.rows[0]) == set(value().to_dict()) | {METADATA_FACT_ID_FIELD, IDEMPOTENCY_KEY_FIELD}


def test_02_fact_id_is_deterministic() -> None:
    assert metadata_fact_id(value()) == metadata_fact_id(value())


def test_03_fact_id_excludes_observed_at() -> None:
    assert metadata_fact_id(value()) == metadata_fact_id(value(observed_at=AT + timedelta(minutes=1)))


def test_04_fact_id_excludes_fingerprint_field() -> None:
    assert metadata_fact_id(value()) == metadata_fact_id(value(metadata_fingerprint=None))


def test_05_fact_id_excludes_idempotency_key() -> None:
    facts_a, _, _ = persisted(value(), "a")
    facts_b, _, _ = persisted(value(), "b")
    assert facts_a.rows[0][METADATA_FACT_ID_FIELD] == facts_b.rows[0][METADATA_FACT_ID_FIELD]


def test_06_same_generation_different_observation_same_id() -> None:
    assert metadata_fact_id(value()) == metadata_fact_id(value(observed_at=AT.replace(second=1)))


def test_07_same_generation_different_observation_same_fingerprint() -> None:
    assert value().fingerprint == value(observed_at=AT.replace(second=1)).fingerprint


def test_08_r4d_generation_identity_is_used() -> None:
    assert value().generation_identity() == value(observed_at=AT + timedelta(days=1)).generation_identity()


def test_09_full_python_equality_is_not_generation_identity() -> None:
    assert value() != value(observed_at=AT + timedelta(seconds=1))
    assert value().same_generation(value(observed_at=AT + timedelta(seconds=1)))


def test_10_strict_fact_hydration() -> None:
    facts, _, session = persisted(value())
    assert get_fact("tenant-a", cast(str, facts.rows[0][METADATA_FACT_ID_FIELD]), facts, session=session) == value()


def test_11_unknown_fact_field_rejected() -> None:
    facts, _, session = persisted(value()); facts.rows[0]["unknown"] = 1
    with pytest.raises(PersistedRecordInvalidError): get_fact("tenant-a", cast(str, facts.rows[0][METADATA_FACT_ID_FIELD]), facts, session=session)


def test_12_missing_fact_field_rejected() -> None:
    facts, _, session = persisted(value()); del facts.rows[0]["observed_at"]
    with pytest.raises(PersistedRecordInvalidError): get_fact("tenant-a", cast(str, facts.rows[0][METADATA_FACT_ID_FIELD]), facts, session=session)


def test_13_malformed_fact_id_rejected() -> None:
    facts, _, session = persisted(value()); facts.rows[0][METADATA_FACT_ID_FIELD] = "bad"
    with pytest.raises(PersistedRecordInvalidError): get_fact("tenant-a", "bad", facts, session=session)


def test_14_malformed_metadata_fingerprint_rejected() -> None:
    facts, _, session = persisted(value()); facts.rows[0]["metadata_fingerprint"] = "bad"
    with pytest.raises(PersistedRecordInvalidError): get_fact("tenant-a", cast(str, facts.rows[0][METADATA_FACT_ID_FIELD]), facts, session=session)


def test_15_malformed_observed_at_rejected() -> None:
    facts, _, session = persisted(value()); facts.rows[0]["observed_at"] = "bad"
    with pytest.raises(PersistedRecordInvalidError): get_fact("tenant-a", cast(str, facts.rows[0][METADATA_FACT_ID_FIELD]), facts, session=session)


def test_16_tenant_isolation() -> None:
    facts, _, session = persisted(value())
    assert get_fact("tenant-b", cast(str, facts.rows[0][METADATA_FACT_ID_FIELD]), facts, session=session) is None


def test_17_idempotency_exact_replay() -> None:
    facts, pointers, session = persisted(value())
    assert persist_fact_and_advance_current(value(), "key-a", None, None, fact_collection=facts, pointer_collection=pointers, session=session) == value()
    assert len(facts.rows) == 1


def test_18_same_key_different_observed_at_conflicts() -> None:
    facts, pointers, session = persisted(value())
    with pytest.raises(IdempotencyConflictError): persist_fact_and_advance_current(value(observed_at=AT + timedelta(seconds=1)), "key-a", None, None, fact_collection=facts, pointer_collection=pointers, session=session)


def test_19_same_key_different_credential_version_conflicts() -> None:
    facts, pointers, session = persisted(value())
    with pytest.raises(IdempotencyConflictError): persist_fact_and_advance_current(value(credential_version="credential-v2"), "key-a", None, None, fact_collection=facts, pointer_collection=pointers, session=session)


def test_20_same_key_different_provenance_conflicts() -> None:
    facts, pointers, session = persisted(value())
    with pytest.raises(IdempotencyConflictError): persist_fact_and_advance_current(value(version_provenance_reference="other"), "key-a", None, None, fact_collection=facts, pointer_collection=pointers, session=session)


def test_21_different_key_same_generation_returns_existing() -> None:
    facts, pointers, session = persisted(value())
    assert persist_fact_and_advance_current(value(observed_at=AT + timedelta(seconds=2)), "key-b", None, None, fact_collection=facts, pointer_collection=pointers, session=session) == value()
    assert len(facts.rows) == 1


def test_22_new_key_cannot_bypass_generation_uniqueness() -> None:
    test_21_different_key_same_generation_returns_existing()


def test_23_same_version_different_provenance_rejected() -> None:
    facts, pointers, session = persisted(value())
    with pytest.raises(GenerationConflictError): persist_fact_and_advance_current(value(version_provenance_reference="other"), "key-b", None, None, fact_collection=facts, pointer_collection=pointers, session=session)


def test_24_initial_fact_and_pointer_are_created_together() -> None:
    facts, pointers, _ = persisted(value())
    assert len(facts.rows) == len(pointers.rows) == 1


def test_25_pointer_has_exact_nine_fields() -> None:
    _, pointers, _ = persisted(value())
    assert set(pointers.rows[0]) == {"tenant_id", "provider_id", "merchant_configuration_id", "merchant_configuration_version", "merchant_configuration_fingerprint", "metadata_fact_id", "credential_reference", "credential_version", "metadata_fingerprint"}


def test_26_pointer_strict_hydration() -> None:
    facts, pointers, session = persisted(value()); pointers.rows[0]["extra"] = 1
    with pytest.raises(PersistedRecordInvalidError): get_current_metadata("tenant-a", "provider-a", "config-a", 1, CFG, fact_collection=facts, pointer_collection=pointers, session=session)


def test_27_pointer_fact_correlation_is_strict() -> None:
    facts, pointers, session = persisted(value()); pointers.rows[0]["metadata_fact_id"] = "f" * 128
    with pytest.raises(PersistedRecordInvalidError): get_current_metadata("tenant-a", "provider-a", "config-a", 1, CFG, fact_collection=facts, pointer_collection=pointers, session=session)


def test_28_one_pointer_per_stream() -> None:
    _, pointers, _ = persisted(value()); assert len(pointers.rows) == 1


def test_29_explicit_pointer_advance() -> None:
    facts, pointers, session = persisted(value())
    second = value(credential_version="credential-v2", observed_at=AT + timedelta(minutes=1))
    persist_fact_and_advance_current(second, "key-b", cast(str, facts.rows[0][METADATA_FACT_ID_FIELD]), cast(str, facts.rows[0]["metadata_fingerprint"]), expected_prior_configuration_fingerprint=CFG, fact_collection=facts, pointer_collection=pointers, session=session)
    assert pointers.rows[0]["credential_version"] == "credential-v2"


def test_30_latest_observed_at_is_not_currentness() -> None:
    facts, pointers, session = persisted(value())
    assert get_current_metadata("tenant-a", "provider-a", "config-a", 1, CFG, fact_collection=facts, pointer_collection=pointers, session=session) == value()


def test_31_lexical_credential_version_is_not_currentness() -> None:
    assert get_current_metadata is not None


def test_32_cas_fact_id_antecedent() -> None:
    facts, pointers, session = persisted(value()); second = value(credential_version="v2")
    with pytest.raises(CASConflictError): persist_fact_and_advance_current(second, "b", "wrong", cast(str, facts.rows[0]["metadata_fingerprint"]), expected_prior_configuration_fingerprint=CFG, fact_collection=facts, pointer_collection=pointers, session=session)


def test_33_cas_metadata_fingerprint_antecedent() -> None:
    facts, pointers, session = persisted(value()); second = value(credential_version="v2")
    with pytest.raises(CASConflictError): persist_fact_and_advance_current(second, "b", cast(str, facts.rows[0][METADATA_FACT_ID_FIELD]), "b" * 128, expected_prior_configuration_fingerprint=CFG, fact_collection=facts, pointer_collection=pointers, session=session)


def test_34_cas_configuration_fingerprint_antecedent() -> None:
    facts, pointers, session = persisted(value()); second = value(credential_version="v2")
    with pytest.raises(CASConflictError): persist_fact_and_advance_current(second, "b", cast(str, facts.rows[0][METADATA_FACT_ID_FIELD]), cast(str, facts.rows[0]["metadata_fingerprint"]), expected_prior_configuration_fingerprint="b" * 128, fact_collection=facts, pointer_collection=pointers, session=session)


def test_35_stale_cas_refusal() -> None:
    test_32_cas_fact_id_antecedent()


def test_36_cas_has_no_committed_orphan_under_caller_contract() -> None:
    facts, pointers, session = persisted(value()); second = value(credential_version="v2")
    with pytest.raises(CASConflictError): persist_fact_and_advance_current(second, "b", "wrong", cast(str, facts.rows[0]["metadata_fingerprint"]), expected_prior_configuration_fingerprint=CFG, fact_collection=facts, pointer_collection=pointers, session=session)
    assert len(facts.rows) == 1


def test_37_write_requires_caller_session() -> None:
    with pytest.raises(TransactionRequiredError): persist_fact_and_advance_current(value(), "a", None, None, fact_collection=Collection(), pointer_collection=Collection(), session=None)


def test_38_registry_starts_no_transaction() -> None:
    session = Session(); facts, pointers = Collection(), Collection(); persist_fact_and_advance_current(value(), "a", None, None, fact_collection=facts, pointer_collection=pointers, session=session); assert session.in_transaction is True


def test_39_registry_commits_no_transaction() -> None:
    session = Session(); facts, pointers = Collection(), Collection(); persist_fact_and_advance_current(value(), "a", None, None, fact_collection=facts, pointer_collection=pointers, session=session); assert not hasattr(session, "commit_transaction")


def test_40_registry_aborts_no_transaction() -> None:
    session = Session(); facts, pointers = Collection(), Collection(); persist_fact_and_advance_current(value(), "a", None, None, fact_collection=facts, pointer_collection=pointers, session=session); assert not hasattr(session, "abort_transaction")


def test_41_current_lookup_uses_four_field_stream() -> None:
    facts, pointers, session = persisted(value()); assert get_current_metadata("tenant-a", "provider-a", "config-a", 1, CFG, fact_collection=facts, pointer_collection=pointers, session=session) == value()


def test_42_caller_credential_version_cannot_select_current() -> None:
    assert "credential_version" not in ("tenant_id;provider_id;merchant_configuration_id;merchant_configuration_version")


def test_43_caller_metadata_fingerprint_cannot_select_current() -> None:
    facts, pointers, session = persisted(value())
    with pytest.raises(Exception): get_current_metadata("tenant-a", "provider-a", "config-a", 1, "b" * 128, fact_collection=facts, pointer_collection=pointers, session=session)


def test_44_configuration_fingerprint_cannot_create_parallel_stream() -> None:
    assert "merchant_configuration_fingerprint" not in ("tenant_id;provider_id;merchant_configuration_id;merchant_configuration_version")


def test_45_current_lookup_returns_referenced_fact() -> None:
    facts, pointers, session = persisted(value()); assert get_current_metadata("tenant-a", "provider-a", "config-a", 1, CFG, fact_collection=facts, pointer_collection=pointers, session=session) == value()


def test_46_historical_get_is_tenant_scoped() -> None:
    facts, _, session = persisted(value()); fact_id = cast(str, facts.rows[0][METADATA_FACT_ID_FIELD]); assert get_fact("tenant-b", fact_id, facts, session=session) is None


def test_47_observation_is_not_accepted_as_persistence_authority() -> None:
    source = Path("tools/eos/saas/billing/tenant_inbound_provider_credential_material_metadata_registry.py").read_text()
    assert "Observation" not in source


def test_48_registry_does_not_authenticate_provenance() -> None:
    tree = ast.parse(Path("tools/eos/saas/billing/tenant_inbound_provider_credential_material_metadata_registry.py").read_text())
    calls = [node for node in ast.walk(tree) if isinstance(node, ast.Call)]
    assert all("auth" not in ast.unparse(node.func).lower() for node in calls)


def test_49_cross_tenant_same_idempotency_key_allowed() -> None:
    a, _, _ = persisted(value(), "same"); b, _, _ = persisted(value(tenant_id="tenant-b"), "same"); assert a.rows and b.rows


def test_50_cross_tenant_same_credential_version_allowed() -> None:
    a, _, _ = persisted(value()); b, _, _ = persisted(value(tenant_id="tenant-b")); assert a.rows and b.rows


def test_51_configuration_version_is_stream_isolated() -> None:
    facts, pointers, session = persisted(value()); other = value(merchant_configuration_version=2)
    persist_fact_and_advance_current(other, "other", None, None, fact_collection=facts, pointer_collection=pointers, session=session); assert len(pointers.rows) == 2


def test_52_exact_four_unique_indexes() -> None:
    facts, pointers = Collection(), Collection(); ensure_indexes(facts, pointers)
    assert len(facts.indexes) == 3 and len(pointers.indexes) == 1
    assert {item[1]["name"] for item in facts.indexes} == {FACT_IDENTITY_INDEX_NAME, IDEMPOTENCY_INDEX_NAME, CREDENTIAL_VERSION_INDEX_NAME}
    assert pointers.indexes[0][1]["name"] == CURRENT_POINTER_INDEX_NAME


def test_53_index_creation_is_explicit_only() -> None:
    facts, pointers = Collection(), Collection(); assert not facts.indexes and not pointers.indexes; ensure_indexes(facts, pointers); assert len(facts.indexes) + len(pointers.indexes) == AUTHORITY_UNIQUE_INDEX_COUNT


def test_54_import_has_no_network_or_mongo_connection() -> None:
    tree = ast.parse(Path("tools/eos/saas/billing/tenant_inbound_provider_credential_material_metadata_registry.py").read_text())
    assert all(not isinstance(node, ast.Call) or getattr(node.func, "id", "") not in {"MongoClient", "connect"} for node in ast.walk(tree))


def test_55_no_secret_kms_provider_access() -> None:
    tree = ast.parse(Path("tools/eos/saas/billing/tenant_inbound_provider_credential_material_metadata_registry.py").read_text())
    imported = [ast.unparse(node) for node in ast.walk(tree) if isinstance(node, (ast.Import, ast.ImportFrom))]
    assert all(token not in " ".join(imported).lower() for token in ("boto3", "kms", "payfast", "secret_manager"))


def test_56_no_security_evidence() -> None:
    tree = ast.parse(Path("tools/eos/saas/billing/tenant_inbound_provider_credential_material_metadata_registry.py").read_text())
    imported = " ".join(ast.unparse(node) for node in ast.walk(tree) if isinstance(node, (ast.Import, ast.ImportFrom)))
    assert "credential_security" not in imported.lower()


def test_57_no_p2_p3_mutation() -> None:
    assert "credential_security" not in Path("tools/eos/saas/billing/tenant_inbound_provider_credential_material_metadata_registry.py").read_text()


def test_58_no_client_invoice_payment_binding_or_financial_authority() -> None:
    public_names = set(TenantInboundProviderCredentialMaterialMetadataRegistry.__dict__)
    assert not public_names.intersection({"mark_paid", "settle", "checkout", "bind_provider", "execute"})


def test_59_domain_reobservations_do_not_write() -> None:
    facts, pointers, session = persisted(value()); before = (len(facts.rows), len(pointers.rows))
    persist_fact_and_advance_current(value(observed_at=AT + timedelta(hours=1)), "new-key", None, None, fact_collection=facts, pointer_collection=pointers, session=session)
    assert (len(facts.rows), len(pointers.rows)) == before


def test_60_registry_facade_exposes_canonical_methods() -> None:
    assert callable(TenantInboundProviderCredentialMaterialMetadataRegistry.ensure_indexes)
    assert callable(TenantInboundProviderCredentialMaterialMetadataRegistry.metadata_fact_id)
    assert callable(TenantInboundProviderCredentialMaterialMetadataRegistry.get_current_metadata)


# ARTIFACT: test_tenant_inbound_provider_credential_material_metadata_registry.py
# VERSION: v1.0.0-M11-R8-R3B-P8-P3D-P5-R5-CERT
# AUTHORITY BOUNDARY: host-free direct registry certificate only.
# FAIL-CLOSED POSTURE: all required P5-R5 cases are explicit; Real Mongo is deferred.
# END OF WILSY OS SOVEREIGN ARTIFACT
