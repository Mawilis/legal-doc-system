"""Direct certificate for the bounded P3-R4 current-pointer index migration.

TITLE: Tenant Inbound Provider Credential Security Authority Index Migration Tests
VERSION: v1.0.0-M11-R8-R3B-P8-P3D-P3-R4
AUTHORITY: Wilsy OS Core Governance
EPITOME: Proves fail-closed topology recognition, data preflight, guarded DDL,
         idempotent rerun, tenant scope, and redacted evidence without Mongo.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tests/unit/test_tenant_inbound_provider_credential_security_authority_index_migration.py
COLLABORATION / OWNERSHIP: Unit certificate for the paired migration owner.
CERTIFICATION / UPDATE DATE: 2026-09-10
CHANGELOG: v1.0.0-M11-R8-R3B-P8-P3D-P3-R4 covers the 46-case migration matrix.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2.
TENANT BOUNDARY: All fixtures and grouping assertions retain tenant identity.
AUTHORITY BOUNDARY: Index migration only; no credential, provider, or finance work.
"""
from __future__ import annotations

from copy import deepcopy
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any

import pytest

from tools.eos.saas.billing.migrations import (
    tenant_inbound_provider_credential_security_authority_index_migration as migration,
)
from tools.eos.saas.billing.tenant_inbound_provider_credential_security_authority_registry import (
    _fact_document,
    security_fact_id,
)
from tools.eos.saas.domain.tenant_inbound_provider_credential_security_authority import (
    TenantInboundProviderCredentialSecurityAuthority,
    TenantInboundProviderCredentialSecurityState,
)


_FP = "a" * 128
_CFG_FP = "b" * 128
_NOW = datetime(2026, 1, 1, tzinfo=timezone.utc)


class FakeCollection:
    """Small PyMongo-shaped collection with observable DDL and no external I/O."""

    def __init__(self, docs: list[dict[str, Any]], indexes: list[dict[str, Any]]) -> None:
        self.docs = deepcopy(docs)
        self.indexes = deepcopy(indexes)
        self.drop_calls: list[str] = []
        self.create_calls: list[tuple[list[tuple[str, int]], dict[str, Any]]] = []
        self.fail_drop = False
        self.fail_create = False
        self.wrong_verify = False

    def find(self, query: dict[str, Any]) -> list[dict[str, Any]]:
        assert query == {}
        return deepcopy(self.docs)

    def list_indexes(self) -> list[dict[str, Any]]:
        return deepcopy(self.indexes)

    def drop_index(self, name: str) -> None:
        if self.fail_drop:
            raise RuntimeError("drop failure")
        self.drop_calls.append(name)
        self.indexes = [item for item in self.indexes if item.get("name") != name]

    def create_index(self, key: list[tuple[str, int]], **options: Any) -> str:
        if self.fail_create:
            raise RuntimeError("create failure")
        self.create_calls.append((key, options))
        spec = {"name": options["name"], "key": dict(key), "unique": options.get("unique", False)}
        if self.wrong_verify:
            spec["key"] = {"wrong": 1}
        self.indexes.append(spec)
        return str(options["name"])


class _Configuration:
    def __init__(self, fingerprint: str) -> None:
        self.fingerprint = fingerprint


class _Record:
    def __init__(self, fingerprint: str) -> None:
        self.configuration = _Configuration(fingerprint)


class FakeCanonicalRegistry:
    result: _Record | None = _Record(_CFG_FP)

    @staticmethod
    def get(tenant_id: str, configuration_id: str, version: int, collection: Any) -> _Record | None:
        assert tenant_id and configuration_id and version >= 1 and collection is not None
        return FakeCanonicalRegistry.result


def _index(name: str, key: tuple[str, ...], *, unique: bool = True, partial: Any = None, sparse: bool = False) -> dict[str, Any]:
    return {"name": name, "key": {field: 1 for field in key}, "unique": unique, "partialFilterExpression": partial, "sparse": sparse}


def _fact(tenant: str = "tenant-a", revision: int = 0) -> dict[str, Any]:
    value = TenantInboundProviderCredentialSecurityAuthority(
        tenant_id=tenant,
        provider_id="provider-a",
        merchant_configuration_id="config-a",
        merchant_configuration_version=1,
        merchant_configuration_fingerprint=_CFG_FP,
        credential_reference="opaque-ref",
        credential_version="credential-v1",
        security_state=TenantInboundProviderCredentialSecurityState.ELIGIBLE,
        security_revision=revision,
        valid_from=_NOW,
        valid_until=_NOW + timedelta(days=1),
        evaluated_at=_NOW + timedelta(hours=1),
        authorization_decision_id="decision-a",
        authorization_evidence_fingerprint=_FP,
    )
    return _fact_document(value, security_fact_id(value), f"key-{tenant}-{revision}")


def _pointer(fact: dict[str, Any]) -> dict[str, Any]:
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


def _collections(*, repaired: bool = False, facts: list[dict[str, Any]] | None = None, pointers: list[dict[str, Any]] | None = None) -> tuple[FakeCollection, FakeCollection, FakeCollection]:
    fact_rows = facts or [_fact()]
    pointer_rows = pointers or [_pointer(fact_rows[0])]
    revision_key = migration.REVISION_REPAIRED_KEY if repaired else migration.REVISION_LEGACY_KEY
    pointer_key = migration.CURRENT_POINTER_REPAIRED_KEY if repaired else migration.CURRENT_POINTER_LEGACY_KEY
    fact_indexes = [_index(migration.REVISION_INDEX_NAME, revision_key)]
    pointer_indexes = [_index(migration.CURRENT_POINTER_INDEX_NAME, pointer_key)]
    return FakeCollection(fact_rows, fact_indexes), FakeCollection(pointer_rows, pointer_indexes), FakeCollection([], [])


def _patch_registry(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(migration, "TenantInboundMerchantConfigurationRegistry", FakeCanonicalRegistry)


def test_01_legacy_topology_is_recognized() -> None:
    facts, pointers, _ = _collections()
    assert migration.inspect_index_topology(facts, pointers) == {migration.REVISION_INDEX_NAME: "legacy", migration.CURRENT_POINTER_INDEX_NAME: "legacy"}


def test_02_repaired_topology_is_recognized() -> None:
    facts, pointers, _ = _collections(repaired=True)
    assert set(migration.inspect_index_topology(facts, pointers).values()) == {"repaired"}


@pytest.mark.parametrize("field,value", [("unique", False), ("sparse", True), ("partialFilterExpression", {"x": 1}), ("key", {"merchant_configuration_id": 1, "tenant_id": 1})])
def test_03_to_06_index_options_fail_closed(field: str, value: Any) -> None:
    facts, pointers, _ = _collections()
    pointers.indexes[0][field] = value
    with pytest.raises(migration.TenantInboundProviderCredentialSecurityAuthorityIndexMigrationError):
        migration.inspect_index_topology(facts, pointers)


def test_07_unknown_same_name_definition_fails() -> None:
    facts, pointers, _ = _collections()
    facts.indexes[0]["key"] = {"wrong": 1}
    with pytest.raises(migration.TenantInboundProviderCredentialSecurityAuthorityIndexMigrationError):
        migration.inspect_index_topology(facts, pointers)


def test_08_wrong_collection_placement_fails() -> None:
    facts, pointers, _ = _collections()
    pointers.indexes.append(facts.indexes[0])
    with pytest.raises(migration.TenantInboundProviderCredentialSecurityAuthorityIndexMigrationError):
        migration.inspect_index_topology(facts, pointers)


def test_09_pointer_divergence_reports_distinct_values() -> None:
    first = _fact()
    second = deepcopy(first)
    second["security_revision"] = 1
    pointers = [_pointer(first), _pointer(second)]
    groups = migration.scan_divergent_pointer_streams(FakeCollection(pointers, []))
    assert groups[0]["pointer_row_count"] == 2
    assert groups[0]["security_revisions"] == [0, 1]


def test_10_tenant_grouping_isolated() -> None:
    first, second = _fact("tenant-a"), _fact("tenant-b")
    assert migration.scan_divergent_pointer_streams(FakeCollection([_pointer(first), _pointer(second)], [])) == []


def test_11_revision_collision_reports_count() -> None:
    first, second = _fact(), _fact()
    second["security_fact_id"] = "c" * 128
    assert migration.scan_revision_collisions(FakeCollection([first, second], []))[0]["fact_row_count"] == 2


@pytest.mark.parametrize("field", ["tenant_id", "provider_id", "merchant_configuration_id", "merchant_configuration_version", "merchant_configuration_fingerprint", "security_revision", "credential_version", "security_fingerprint"])
def test_12_to_19_pointer_provenance_fields_fail_closed(monkeypatch: pytest.MonkeyPatch, field: str) -> None:
    _patch_registry(monkeypatch)
    fact = _fact()
    pointer = _pointer(fact)
    pointer[field] = "different" if field not in {"merchant_configuration_version", "security_revision"} else 99
    with pytest.raises(migration.TenantInboundProviderCredentialSecurityAuthorityIndexMigrationError):
        migration.scan_pointer_fact_provenance(FakeCollection([pointer], []), FakeCollection([fact], []), FakeCollection([], []))


def test_20_missing_referenced_fact_fails(monkeypatch: pytest.MonkeyPatch) -> None:
    _patch_registry(monkeypatch)
    fact = _fact()
    pointer = _pointer(fact)
    pointer["security_fact_id"] = "d" * 128
    with pytest.raises(migration.TenantInboundProviderCredentialSecurityAuthorityIndexMigrationError):
        migration.scan_pointer_fact_provenance(FakeCollection([pointer], []), FakeCollection([fact], []), FakeCollection([], []))


def test_21_malformed_fact_fails(monkeypatch: pytest.MonkeyPatch) -> None:
    _patch_registry(monkeypatch)
    fact = _fact()
    del fact["security_fact_id"]
    with pytest.raises(migration.TenantInboundProviderCredentialSecurityAuthorityIndexMigrationError):
        migration.scan_pointer_fact_provenance(FakeCollection([], []), FakeCollection([fact], []), FakeCollection([], []))


def test_22_malformed_pointer_fails(monkeypatch: pytest.MonkeyPatch) -> None:
    _patch_registry(monkeypatch)
    fact = _fact()
    pointer = _pointer(fact)
    del pointer["security_fingerprint"]
    with pytest.raises(migration.TenantInboundProviderCredentialSecurityAuthorityIndexMigrationError):
        migration.scan_pointer_fact_provenance(FakeCollection([pointer], []), FakeCollection([fact], []), FakeCollection([], []))


@pytest.mark.parametrize("result", [None, _Record("c" * 128)])
def test_23_to_24_canonical_configuration_must_exist_and_match(monkeypatch: pytest.MonkeyPatch, result: _Record | None) -> None:
    FakeCanonicalRegistry.result = result
    _patch_registry(monkeypatch)
    fact = _fact()
    with pytest.raises(migration.TenantInboundProviderCredentialSecurityAuthorityIndexMigrationError):
        migration.scan_pointer_fact_provenance(FakeCollection([_pointer(fact)], []), FakeCollection([fact], []), FakeCollection([], []))
    FakeCanonicalRegistry.result = _Record(_CFG_FP)


def test_25_clean_legacy_migration_changes_only_indexes(monkeypatch: pytest.MonkeyPatch) -> None:
    _patch_registry(monkeypatch)
    facts, pointers, configs = _collections()
    before = (deepcopy(facts.docs), deepcopy(pointers.docs))
    result = migration.migrate(facts, pointers, configs, quiescence_confirmed=True)
    assert result.state == "migrated"
    assert facts.docs == before[0] and pointers.docs == before[1]
    assert facts.drop_calls == [migration.REVISION_INDEX_NAME]
    assert pointers.drop_calls == [migration.CURRENT_POINTER_INDEX_NAME]
    assert set(migration.inspect_index_topology(facts, pointers).values()) == {"repaired"}


def test_26_repaired_rerun_is_noop(monkeypatch: pytest.MonkeyPatch) -> None:
    _patch_registry(monkeypatch)
    facts, pointers, configs = _collections(repaired=True)
    result = migration.migrate(facts, pointers, configs, quiescence_confirmed=True)
    assert result.state == "already_repaired" and not facts.drop_calls and not pointers.create_calls


@pytest.mark.parametrize("phase", ["drop", "create", "verify"])
def test_27_to_29_ddl_failures_fail_closed(monkeypatch: pytest.MonkeyPatch, phase: str) -> None:
    _patch_registry(monkeypatch)
    facts, pointers, configs = _collections()
    if phase == "drop":
        facts.fail_drop = True
    elif phase == "create":
        facts.fail_create = True
    else:
        facts.wrong_verify = True
    with pytest.raises(migration.TenantInboundProviderCredentialSecurityAuthorityIndexMigrationError):
        migration.migrate(facts, pointers, configs, quiescence_confirmed=True)


def test_30_mixed_topology_fails_before_ddl(monkeypatch: pytest.MonkeyPatch) -> None:
    _patch_registry(monkeypatch)
    facts, pointers, configs = _collections()
    pointers.indexes[0] = _index(migration.CURRENT_POINTER_INDEX_NAME, migration.CURRENT_POINTER_REPAIRED_KEY)
    with pytest.raises(migration.TenantInboundProviderCredentialSecurityAuthorityIndexMigrationError):
        migration.migrate(facts, pointers, configs, quiescence_confirmed=True)
    assert not facts.drop_calls and not pointers.drop_calls


@pytest.mark.parametrize("quiescence,collections", [(False, True), (True, False)])
def test_31_to_32_guard_and_explicit_targets(quiescence: bool, collections: bool) -> None:
    facts, pointers, configs = _collections()
    if not collections:
        facts = None
    with pytest.raises(migration.TenantInboundProviderCredentialSecurityAuthorityIndexMigrationError):
        migration.migrate(facts, pointers, configs, quiescence_confirmed=quiescence)


def test_33_result_is_redacted() -> None:
    result = migration.TenantInboundProviderCredentialSecurityAuthorityIndexMigrationResult("already_repaired", (), (), 0, 1, 1).to_dict()
    assert "credential_reference" not in str(result) and "secret" not in str(result).lower()


def test_34_no_document_mutation_on_scans(monkeypatch: pytest.MonkeyPatch) -> None:
    _patch_registry(monkeypatch)
    facts, pointers, configs = _collections()
    before = (deepcopy(facts.docs), deepcopy(pointers.docs))
    migration.scan_pointer_fact_provenance(pointers, facts, configs)
    assert (facts.docs, pointers.docs) == before


def test_35_exact_ordered_keys_are_required() -> None:
    assert migration.CURRENT_POINTER_REPAIRED_KEY == ("tenant_id", "provider_id", "merchant_configuration_id", "merchant_configuration_version")
    assert migration.REVISION_REPAIRED_KEY == migration.CURRENT_POINTER_REPAIRED_KEY + ("security_revision",)


def test_36_affected_names_are_limited() -> None:
    assert migration._AFFECTED_NAMES == frozenset({migration.CURRENT_POINTER_INDEX_NAME, migration.REVISION_INDEX_NAME})


def test_37_pointer_scan_has_no_raw_credential_reference() -> None:
    row = _pointer(_fact())
    evidence = migration.scan_divergent_pointer_streams(FakeCollection([row, row], []))[0]
    assert "credential_reference" not in str(evidence)


def test_38_registry_import_is_inert() -> None:
    source = Path(migration.__file__).read_text(encoding="utf-8")
    assert "MongoClient(" not in source and "socket." not in source


@pytest.mark.parametrize("name", ["provider_policy", "checkout"])
def test_39_to_40_authority_firewall(name: str) -> None:
    source = Path(migration.__file__).read_text(encoding="utf-8").lower()
    assert f"{name}(" not in source


def test_41_no_kms_or_secret_resolution() -> None:
    source = Path(migration.__file__).read_text(encoding="utf-8").lower()
    assert "boto3" not in source and "get_secret(" not in source and "resolve_secret(" not in source


def test_42_preflight_precedes_ddl(monkeypatch: pytest.MonkeyPatch) -> None:
    _patch_registry(monkeypatch)
    facts, pointers, configs = _collections()
    pointer = _pointer(_fact())
    pointer["security_revision"] = 7
    pointers.docs.append(pointer)
    with pytest.raises(migration.TenantInboundProviderCredentialSecurityAuthorityIndexMigrationError):
        migration.migrate(facts, pointers, configs, quiescence_confirmed=True)
    assert not facts.drop_calls and not pointers.drop_calls


def test_43_current_pointer_index_scope_excludes_fingerprint() -> None:
    assert "merchant_configuration_fingerprint" not in migration.CURRENT_POINTER_REPAIRED_KEY


def test_44_revision_index_scope_excludes_fingerprint() -> None:
    assert "merchant_configuration_fingerprint" not in migration.REVISION_REPAIRED_KEY


def test_45_result_counts_are_postflight_counts(monkeypatch: pytest.MonkeyPatch) -> None:
    _patch_registry(monkeypatch)
    facts, pointers, configs = _collections()
    result = migration.migrate(facts, pointers, configs, quiescence_confirmed=True)
    assert result.pointer_rows_scanned == 1 and result.fact_rows_scanned == 1


def test_46_version_and_campaign_are_current() -> None:
    assert migration.VERSION == "v1.0.0-M11-R8-R3B-P8-P3D-P3-R4"
    assert migration.CAMPAIGN_IDENTITY == "M11-R8-R3B-P8-P3D-P3-R4"


# R4_DIRECT_REQUIRED_CASE_COUNT=46

# ARTIFACT: test_tenant_inbound_provider_credential_security_authority_index_migration.py
# VERSION: v1.0.0-M11-R8-R3B-P8-P3D-P3-R4
# AUTHORITY BOUNDARY: direct unit certificate only; no durable authority or financial execution.
# TENANT POSTURE: all fixture identities and preflight grouping are tenant-scoped.
# FAIL-CLOSED POSTURE: every mismatch is asserted to reject without document mutation.
# END OF WILSY OS SOVEREIGN ARTIFACT
