"""Explicit credential-security current-pointer index migration.

TITLE: Tenant Inbound Provider Credential Security Authority Index Migration
VERSION: v1.0.0-M11-R8-R3B-P8-P3D-P3-R4
AUTHORITY: Wilsy OS Core Governance
EPITOME: Fail-closed upgrade of the legacy fingerprint-scoped current and
         revision indexes to the repaired four-field stream identity.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tools/eos/saas/billing/migrations/tenant_inbound_provider_credential_security_authority_index_migration.py
COLLABORATION / OWNERSHIP: Explicit SaaS billing deployment migration owner;
                            caller supplies collections and quiescence proof.
CERTIFICATION / UPDATE DATE: 2026-09-10
CHANGELOG: v1.0.0-M11-R8-R3B-P8-P3D-P3-R4 implements strict index introspection,
           preflight divergence/provenance scans, guarded DDL, and idempotent
           re-execution without document mutation.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2.
SECURITY / PRIVACY POSTURE: No secret resolution, KMS, provider, network, or
                             credential-reference output; only opaque digests are
                             compared for migration safety.
TENANT BOUNDARY: Every stream, revision, pointer/fact, and canonical configuration
                 lookup includes tenant_id.
AUTHORITY BOUNDARY: Index topology migration only; no credential-security
                    issuance, evaluation, binding, checkout, or lifecycle writes.
FINANCIAL AUTHORITY BOUNDARY: Kennel EOS exclusively owns financial execution.
TRANSACTION BOUNDARY: Deployment caller supplies explicit collections and quiescence;
                      index DDL is not coupled to a Mongo transaction.
FAIL-CLOSED DECLARATION: Unknown topology, divergent rows, malformed documents,
                          provenance drift, and every DDL failure stop migration.
"""
from __future__ import annotations

from dataclasses import dataclass
import json
from typing import Any, ClassVar, Mapping, NoReturn, Sequence, cast

from tools.eos.saas.billing.tenant_inbound_merchant_configuration_registry import (
    TenantInboundMerchantConfigurationRegistry,
    TenantInboundMerchantConfigurationRegistryError,
)
from tools.eos.saas.billing.tenant_inbound_provider_credential_security_authority_registry import (
    CURRENT_POINTER_INDEX_NAME,
    FACT_COLLECTION,
    REVISION_INDEX_NAME,
    TenantInboundProviderCredentialSecurityAuthorityRegistryPersistenceCorruptionError,
    TenantInboundProviderCredentialSecurityAuthorityRegistryRecordInvalidError,
    _hydrate_fact,
    _hydrate_pointer,
    security_fact_id,
)


VERSION = "v1.0.0-M11-R8-R3B-P8-P3D-P3-R4"
CAMPAIGN_IDENTITY = "M11-R8-R3B-P8-P3D-P3-R4"
CURRENT_POINTER_COLLECTION = "tenant_inbound_provider_credential_security_current"
FACT_COLLECTION_NAME = FACT_COLLECTION
CURRENT_POINTER_LEGACY_KEY = (
    "tenant_id",
    "provider_id",
    "merchant_configuration_id",
    "merchant_configuration_version",
    "merchant_configuration_fingerprint",
)
CURRENT_POINTER_REPAIRED_KEY = CURRENT_POINTER_LEGACY_KEY[:-1]
REVISION_LEGACY_KEY = CURRENT_POINTER_LEGACY_KEY + ("security_revision",)
REVISION_REPAIRED_KEY = CURRENT_POINTER_REPAIRED_KEY + ("security_revision",)
_AFFECTED_NAMES = frozenset({CURRENT_POINTER_INDEX_NAME, REVISION_INDEX_NAME})


class TenantInboundProviderCredentialSecurityAuthorityIndexMigrationError(RuntimeError):
    """Every migration refusal is explicit and fail-closed."""


@dataclass(frozen=True, slots=True)
class TenantInboundProviderCredentialSecurityAuthorityIndexMigrationResult:
    """Redacted deterministic deployment evidence returned after successful migration."""

    state: str
    indexes_dropped: tuple[str, ...]
    indexes_created: tuple[str, ...]
    document_mutation_count: int
    pointer_rows_scanned: int
    fact_rows_scanned: int

    _STATES: ClassVar[frozenset[str]] = frozenset({"already_repaired", "migrated"})

    def __post_init__(self) -> None:
        if self.state not in self._STATES or self.document_mutation_count != 0:
            raise TenantInboundProviderCredentialSecurityAuthorityIndexMigrationError(
                "M11P3D_INVALID_MIGRATION_RESULT"
            )
        if self.pointer_rows_scanned < 0 or self.fact_rows_scanned < 0:
            raise TenantInboundProviderCredentialSecurityAuthorityIndexMigrationError(
                "M11P3D_INVALID_MIGRATION_COUNTS"
            )

    def to_dict(self) -> dict[str, object]:
        """Return bounded evidence without raw documents or credential references."""
        return {
            "state": self.state,
            "indexes_dropped": list(self.indexes_dropped),
            "indexes_created": list(self.indexes_created),
            "document_mutation_count": self.document_mutation_count,
            "pointer_rows_scanned": self.pointer_rows_scanned,
            "fact_rows_scanned": self.fact_rows_scanned,
        }


def _fail(code: str, cause: BaseException | None = None) -> NoReturn:
    """Raise one stable migration error and never continue after a failed phase."""
    error = TenantInboundProviderCredentialSecurityAuthorityIndexMigrationError(code)
    if cause is None:
        raise error
    raise error from cause


def _rows(collection: Any) -> list[Mapping[str, object]]:
    """Read all rows from an explicitly supplied collection without mutation."""
    if collection is None or not hasattr(collection, "find"):
        _fail("M11P3D_COLLECTION_FIND_REQUIRED")
    rows = cast(Any, collection).find({})
    return [row for row in rows]


def _key_tuple(raw_key: object) -> tuple[tuple[str, int], ...]:
    """Normalize ordered Mongo key specifications without discarding order."""
    if isinstance(raw_key, Mapping):
        return tuple((str(name), int(direction)) for name, direction in raw_key.items())
    if isinstance(raw_key, Sequence) and not isinstance(raw_key, (str, bytes, bytearray)):
        result: list[tuple[str, int]] = []
        for item in raw_key:
            if not isinstance(item, Sequence) or len(item) != 2:
                _fail("M11P3D_INVALID_INDEX_KEY")
            result.append((str(item[0]), int(cast(Any, item[1]))))
        return tuple(result)
    _fail("M11P3D_INVALID_INDEX_KEY")


def _canonical_option(value: object) -> str:
    """Compare index options deterministically, including absent-vs-present values."""
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def _normalized_index(raw: Mapping[str, object]) -> dict[str, object]:
    """Normalize name, ordered keys, and safety options from list_indexes()."""
    name = raw.get("name")
    if not isinstance(name, str) or not name:
        _fail("M11P3D_INVALID_INDEX_NAME")
    return {
        "name": name,
        "key": _key_tuple(raw.get("key")),
        "unique": raw.get("unique") is True,
        "partialFilterExpression": raw.get("partialFilterExpression"),
        "sparse": raw.get("sparse", False) is True,
    }


def _expected_index(name: str, key: tuple[str, ...]) -> dict[str, object]:
    """Build one exact affected-index definition."""
    return {
        "name": name,
        "key": tuple((field, 1) for field in key),
        "unique": True,
        "partialFilterExpression": None,
        "sparse": False,
    }


def _definition_matches(actual: Mapping[str, object], expected: Mapping[str, object]) -> bool:
    """Require exact ordered keys and relevant Mongo options."""
    return all(
        _canonical_option(actual.get(field)) == _canonical_option(expected.get(field))
        for field in ("name", "key", "unique", "partialFilterExpression", "sparse")
    )


def inspect_index_topology(fact_collection: Any, pointer_collection: Any) -> dict[str, str]:
    """Recognize only complete legacy or complete repaired affected topology."""
    if fact_collection is None or pointer_collection is None:
        _fail("M11P3D_EXPLICIT_COLLECTIONS_REQUIRED")
    expected = {
        REVISION_INDEX_NAME: (
            _expected_index(REVISION_INDEX_NAME, REVISION_LEGACY_KEY),
            _expected_index(REVISION_INDEX_NAME, REVISION_REPAIRED_KEY),
        ),
        CURRENT_POINTER_INDEX_NAME: (
            _expected_index(CURRENT_POINTER_INDEX_NAME, CURRENT_POINTER_LEGACY_KEY),
            _expected_index(CURRENT_POINTER_INDEX_NAME, CURRENT_POINTER_REPAIRED_KEY),
        ),
    }
    actual_by_name: dict[str, dict[str, object]] = {}
    placement = {
        REVISION_INDEX_NAME: fact_collection,
        CURRENT_POINTER_INDEX_NAME: pointer_collection,
    }
    wrong_placement_names: set[str] = set()
    for collection in (fact_collection, pointer_collection):
        if not hasattr(collection, "list_indexes"):
            _fail("M11P3D_INDEX_INTROSPECTION_REQUIRED")
        for raw in cast(Any, collection).list_indexes():
            normalized = _normalized_index(raw)
            name = str(normalized["name"])
            if name in _AFFECTED_NAMES:
                if placement[name] is not collection:
                    wrong_placement_names.add(name)
                    continue
                if name in actual_by_name:
                    _fail("M11P3D_DUPLICATE_AFFECTED_INDEX_NAME")
                actual_by_name[name] = normalized
    if wrong_placement_names:
        _fail("M11P3D_AFFECTED_INDEX_WRONG_COLLECTION")
    states: dict[str, str] = {}
    for name, (legacy, repaired) in expected.items():
        actual = actual_by_name.get(name)
        if actual is None:
            _fail("M11P3D_AFFECTED_INDEX_MISSING")
        if _definition_matches(actual, repaired):
            states[name] = "repaired"
        elif _definition_matches(actual, legacy):
            states[name] = "legacy"
        else:
            _fail("M11P3D_UNKNOWN_AFFECTED_INDEX_DEFINITION")
    if len(set(states.values())) != 1:
        _fail("M11P3D_UNKNOWN_MIXED_INDEX_TOPOLOGY")
    return states


def scan_divergent_pointer_streams(pointer_collection: Any) -> list[dict[str, object]]:
    """Group pointer rows by the repaired four-field stream identity."""
    groups: dict[tuple[object, ...], dict[str, object]] = {}
    for row in _rows(pointer_collection):
        key = tuple(row.get(field) for field in CURRENT_POINTER_REPAIRED_KEY)
        group = groups.setdefault(
            key,
            {
                "stream": key,
                "pointer_row_count": 0,
                "configuration_fingerprints": set(),
                "security_fact_ids": set(),
                "security_revisions": set(),
                "credential_versions": set(),
                "security_fingerprints": set(),
            },
        )
        group["pointer_row_count"] = int(cast(Any, group["pointer_row_count"])) + 1
        for output, field in (
            ("configuration_fingerprints", "merchant_configuration_fingerprint"),
            ("security_fact_ids", "security_fact_id"),
            ("security_revisions", "security_revision"),
            ("credential_versions", "credential_version"),
            ("security_fingerprints", "security_fingerprint"),
        ):
            cast_set = group[output]
            if isinstance(cast_set, set):
                cast_set.add(row.get(field))
    divergent: list[dict[str, object]] = []
    for group in groups.values():
        if int(cast(Any, group["pointer_row_count"])) > 1:
            divergent.append(
                {
                    key: sorted(value, key=str)
                    if isinstance(value, set)
                    else value
                    for key, value in group.items()
                }
            )
    return divergent


def scan_revision_collisions(fact_collection: Any) -> list[dict[str, object]]:
    """Group immutable facts by repaired stream plus security revision."""
    groups: dict[tuple[object, ...], dict[str, object]] = {}
    fields = REVISION_REPAIRED_KEY
    for row in _rows(fact_collection):
        key = tuple(row.get(field) for field in fields)
        group = groups.setdefault(key, {"stream_revision": key, "fact_row_count": 0, "configuration_fingerprints": set()})
        group["fact_row_count"] = int(cast(Any, group["fact_row_count"])) + 1
        fingerprints = group["configuration_fingerprints"]
        if isinstance(fingerprints, set):
            fingerprints.add(row.get("merchant_configuration_fingerprint"))
    return [
        {key: sorted(value, key=str) if isinstance(value, set) else value for key, value in group.items()}
        for group in groups.values()
        if int(cast(Any, group["fact_row_count"])) > 1
    ]


def _pointer_fact_provenance(
    pointer: Mapping[str, object],
    fact: Mapping[str, object],
) -> bool:
    """Require every pointer field to correlate exactly with its referenced fact."""
    return all(
        pointer.get(field) == fact.get(field)
        for field in (
            "tenant_id",
            "provider_id",
            "merchant_configuration_id",
            "merchant_configuration_version",
            "merchant_configuration_fingerprint",
            "security_revision",
            "credential_version",
            "security_fingerprint",
        )
    ) and pointer.get("security_fact_id") == security_fact_id(_hydrate_fact(fact))


def scan_pointer_fact_provenance(
    pointer_collection: Any,
    fact_collection: Any,
    configuration_collection: Any,
) -> tuple[int, int]:
    """Strictly hydrate every fact/pointer and correlate each to canonical configuration."""
    facts_by_identity: dict[tuple[object, object], Mapping[str, object]] = {}
    fact_rows = _rows(fact_collection)
    for raw in fact_rows:
        try:
            fact = _hydrate_fact(raw)
        except (TenantInboundProviderCredentialSecurityAuthorityRegistryRecordInvalidError, TypeError, ValueError) as error:
            _fail("M11P3D_MALFORMED_FACT_BLOCKS_MIGRATION", error)
        facts_by_identity[(raw.get("tenant_id"), raw.get("security_fact_id"))] = raw
        _ = fact
    pointer_rows = _rows(pointer_collection)
    for raw in pointer_rows:
        try:
            pointer = _hydrate_pointer(raw)
        except (TenantInboundProviderCredentialSecurityAuthorityRegistryRecordInvalidError, TypeError, ValueError) as error:
            _fail("M11P3D_MALFORMED_POINTER_BLOCKS_MIGRATION", error)
        fact = facts_by_identity.get((pointer.tenant_id, pointer.security_fact_id))
        if fact is None:
            _fail("M11P3D_MISSING_REFERENCED_FACT")
        fact = cast(Mapping[str, object], fact)
        try:
            hydrated_fact = _hydrate_fact(fact)
        except (TenantInboundProviderCredentialSecurityAuthorityRegistryRecordInvalidError, TypeError, ValueError) as error:
            _fail("M11P3D_MALFORMED_FACT_BLOCKS_MIGRATION", error)
        if not _pointer_fact_provenance(raw, fact):
            _fail("M11P3D_POINTER_FACT_PROVENANCE_MISMATCH")
        if configuration_collection is None:
            _fail("M11P3D_CANONICAL_CONFIGURATION_COLLECTION_REQUIRED")
        try:
            configuration = TenantInboundMerchantConfigurationRegistry.get(
                hydrated_fact.tenant_id,
                hydrated_fact.merchant_configuration_id,
                hydrated_fact.merchant_configuration_version,
                cast(Any, configuration_collection),
            )
        except TenantInboundMerchantConfigurationRegistryError as error:
            _fail("M11P3D_CANONICAL_CONFIGURATION_LOOKUP_FAILED", error)
        if configuration is None:
            _fail("M11P3D_CANONICAL_CONFIGURATION_MISSING")
        if configuration.configuration.fingerprint != hydrated_fact.merchant_configuration_fingerprint:
            _fail("M11P3D_CANONICAL_CONFIGURATION_FINGERPRINT_MISMATCH")
    return len(pointer_rows), len(fact_rows)


def _postflight(
    pointer_collection: Any,
    fact_collection: Any,
    configuration_collection: Any,
) -> tuple[int, int]:
    """Repeat all data safety scans after DDL without rewriting documents."""
    if scan_divergent_pointer_streams(pointer_collection):
        _fail("M11P3D_POSTFLIGHT_DIVERGENT_POINTERS")
    if scan_revision_collisions(fact_collection):
        _fail("M11P3D_POSTFLIGHT_REVISION_COLLISIONS")
    return scan_pointer_fact_provenance(pointer_collection, fact_collection, configuration_collection)


def _verify_repaired_indexes(fact_collection: Any, pointer_collection: Any) -> None:
    """Verify both affected indexes exactly after creation."""
    states = inspect_index_topology(fact_collection, pointer_collection)
    if set(states.values()) != {"repaired"}:
        _fail("M11P3D_REPAIRED_INDEX_VERIFICATION_FAILED")


def migrate(
    fact_collection: Any,
    pointer_collection: Any,
    configuration_collection: Any,
    *,
    quiescence_confirmed: bool,
) -> TenantInboundProviderCredentialSecurityAuthorityIndexMigrationResult:
    """Migrate only affected indexes after explicit guard, scans, and quiescence proof."""
    if quiescence_confirmed is not True:
        _fail("M11P3D_DEPLOYMENT_QUIESCENCE_REQUIRED")
    if fact_collection is None or pointer_collection is None or configuration_collection is None:
        _fail("M11P3D_EXPLICIT_TARGET_COLLECTIONS_REQUIRED")
    fact_collection = cast(Any, fact_collection)
    pointer_collection = cast(Any, pointer_collection)
    configuration_collection = cast(Any, configuration_collection)
    states = inspect_index_topology(fact_collection, pointer_collection)
    if scan_divergent_pointer_streams(pointer_collection):
        _fail("M11P3D_DIVERGENT_POINTERS_BEFORE_DDL")
    if scan_revision_collisions(fact_collection):
        _fail("M11P3D_REVISION_COLLISIONS_BEFORE_DDL")
    pointer_count, fact_count = scan_pointer_fact_provenance(pointer_collection, fact_collection, configuration_collection)
    if set(states.values()) == {"repaired"}:
        _postflight(pointer_collection, fact_collection, configuration_collection)
        _verify_repaired_indexes(fact_collection, pointer_collection)
        return TenantInboundProviderCredentialSecurityAuthorityIndexMigrationResult(
            "already_repaired", (), (), 0, pointer_count, fact_count
        )

    dropped: list[str] = []
    created: list[str] = []
    try:
        # Drop only the two same-name legacy indexes; DDL is never claimed atomic.
        fact_collection.drop_index(REVISION_INDEX_NAME)
        dropped.append(REVISION_INDEX_NAME)
        pointer_collection.drop_index(CURRENT_POINTER_INDEX_NAME)
        dropped.append(CURRENT_POINTER_INDEX_NAME)
        fact_collection.create_index(
            [(field, 1) for field in REVISION_REPAIRED_KEY],
            unique=True,
            name=REVISION_INDEX_NAME,
        )
        created.append(REVISION_INDEX_NAME)
        pointer_collection.create_index(
            [(field, 1) for field in CURRENT_POINTER_REPAIRED_KEY],
            unique=True,
            name=CURRENT_POINTER_INDEX_NAME,
        )
        created.append(CURRENT_POINTER_INDEX_NAME)
        _verify_repaired_indexes(fact_collection, pointer_collection)
    except Exception as error:
        _fail("M11P3D_INDEX_DDL_FAILED", error)
    post_pointer_count, post_fact_count = _postflight(pointer_collection, fact_collection, configuration_collection)
    return TenantInboundProviderCredentialSecurityAuthorityIndexMigrationResult(
        "migrated",
        tuple(dropped),
        tuple(created),
        0,
        post_pointer_count,
        post_fact_count,
    )


__all__ = [
    "CAMPAIGN_IDENTITY",
    "CURRENT_POINTER_COLLECTION",
    "CURRENT_POINTER_INDEX_NAME",
    "CURRENT_POINTER_LEGACY_KEY",
    "CURRENT_POINTER_REPAIRED_KEY",
    "FACT_COLLECTION_NAME",
    "REVISION_INDEX_NAME",
    "REVISION_LEGACY_KEY",
    "REVISION_REPAIRED_KEY",
    "TenantInboundProviderCredentialSecurityAuthorityIndexMigrationError",
    "TenantInboundProviderCredentialSecurityAuthorityIndexMigrationResult",
    "inspect_index_topology",
    "migrate",
    "scan_divergent_pointer_streams",
    "scan_pointer_fact_provenance",
    "scan_revision_collisions",
    "VERSION",
]


# ARTIFACT: tenant_inbound_provider_credential_security_authority_index_migration.py
# VERSION: v1.0.0-M11-R8-R3B-P8-P3D-P3-R4
# AUTHORITY BOUNDARY: explicit index topology migration only; no credential or financial authority.
# TENANT POSTURE: every stream, revision, pointer/fact, and canonical lookup is tenant-scoped.
# FAIL-CLOSED POSTURE: divergence, corruption, unknown topology, and DDL failure stop immediately.
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively.
# END OF WILSY OS SOVEREIGN ARTIFACT
