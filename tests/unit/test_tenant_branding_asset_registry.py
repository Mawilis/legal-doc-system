"""Direct certificate for the D21B5B tenant branding asset registry.

TITLE: Tenant Branding Asset Registry Direct Certificate
VERSION: v1.0.0-D21B5B-TENANT-BRANDING-ASSET-REGISTRY-CERT
AUTHORITY: Wilsy OS Core Governance
EPITOME: Prove immutable bounded byte persistence, exact replay, strict content
         re-hash, tenant/reference isolation, expected profile-evidence
         correlation and caller-owned transaction semantics.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tests/unit/test_tenant_branding_asset_registry.py
COLLABORATION / OWNERSHIP: Direct collection-double evidence for D21B5B only;
                            real-Mongo remains a separate gate.
CERTIFICATION / UPDATE DATE: 2026-09-25
CHANGELOG: v1.0.0-D21B5B-TENANT-BRANDING-ASSET-REGISTRY-CERT establishes
           adversarial evidence for indexes, exact create/replay, divergent
           conflict, tenant silence, byte corruption rejection, expected
           fingerprint/kind checks, duplicate races and transient retry labels.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2; ISO 27001.
SECURITY / PRIVACY POSTURE: Synthetic bounded image bytes only; no URL/storage
                             credentials/browser state.
TENANT BOUNDARY: Every direct registry operation binds exact tenant/reference.
AUTHORITY BOUNDARY: Asset byte persistence/resolution only; no profile/current
                    branding/entitlement/IAM/browser authority.
FINANCIAL AUTHORITY BOUNDARY: None; Kennel EOS remains exclusive.
"""
from __future__ import annotations

from copy import deepcopy
from datetime import datetime, timezone
from typing import Any

import pytest
from pymongo.errors import DuplicateKeyError, PyMongoError

from tools.eos.saas.billing import tenant_branding_asset_registry as registry
from tools.eos.saas.domain.tenant_branding_asset import (
    TenantBrandingAsset,
    TenantBrandingAssetKind,
    register_tenant_branding_asset,
)


NOW = datetime(2026, 9, 25, 18, 0, tzinfo=timezone.utc)
FP = "a" * 128
PNG = b"\x89PNG\r\n\x1a\n" + b"tenant-logo"


class Session:
    """Minimal active caller transaction marker."""

    def __init__(self, active: bool = True) -> None:
        self.in_transaction = active


class Cursor:
    """Bounded deterministic cursor double."""

    def __init__(self, rows: list[dict[str, Any]]) -> None:
        self.rows = rows
        self.limit_value: int | None = None

    def limit(self, value: int) -> "Cursor":
        self.limit_value = value
        return self

    def __iter__(self) -> Any:
        rows = self.rows
        if self.limit_value is not None:
            rows = rows[: self.limit_value]
        return iter(deepcopy(rows))


class TransientMongoError(PyMongoError):
    """Synthetic Mongo transient-transaction failure."""

    def has_error_label(self, label: str) -> bool:
        return label == "TransientTransactionError"


class Collection:
    """Mongo-like collection double with exact unique-index enforcement."""

    def __init__(self) -> None:
        self.rows: list[dict[str, Any]] = []
        self.indexes: list[dict[str, Any]] = []
        self.calls: list[tuple[str, object, dict[str, Any]]] = []
        self.force_duplicate = False
        self.transient_find = False
        self.transient_insert = False

    def with_options(self, **_: Any) -> "Collection":
        return self

    def create_index(self, keys: Any, **kwargs: Any) -> str:
        self.indexes.append({"key": list(keys), **kwargs})
        return str(kwargs["name"])

    @staticmethod
    def _match(row: dict[str, Any], query: dict[str, Any]) -> bool:
        return all(row.get(key) == value for key, value in query.items())

    def find(
        self,
        query: dict[str, Any],
        *,
        session: object,
    ) -> Cursor:
        assert session is not None
        self.calls.append(("find", session, deepcopy(query)))
        if self.transient_find:
            self.transient_find = False
            raise TransientMongoError("transient find")
        return Cursor([row for row in self.rows if self._match(row, query)])

    def find_one(
        self,
        query: dict[str, Any],
        *,
        session: object,
    ) -> dict[str, Any] | None:
        assert session is not None
        self.calls.append(("find_one", session, deepcopy(query)))
        if self.transient_find:
            self.transient_find = False
            raise TransientMongoError("transient find-one")
        row = next((row for row in self.rows if self._match(row, query)), None)
        return None if row is None else deepcopy(row)

    def _violates_unique(self, document: dict[str, Any]) -> bool:
        for index in self.indexes:
            if not index.get("unique"):
                continue
            keys = [name for name, _ in index["key"]]
            expected = tuple(document.get(name) for name in keys)
            if any(
                tuple(row.get(name) for name in keys) == expected
                for row in self.rows
            ):
                return True
        return False

    def insert_one(
        self,
        document: dict[str, Any],
        *,
        session: object,
    ) -> object:
        assert session is not None
        self.calls.append(("insert_one", session, deepcopy(document)))
        if self.transient_insert:
            self.transient_insert = False
            raise TransientMongoError("transient insert")
        if self.force_duplicate:
            self.force_duplicate = False
            raise DuplicateKeyError("forced duplicate")
        if self._violates_unique(document):
            raise DuplicateKeyError("unique index")
        self.rows.append(deepcopy(document))
        return object()


def asset(
    *,
    tenant_id: str = "tenant-a",
    reference: str = "asset:tenant-a:logo:primary",
    kind: TenantBrandingAssetKind = TenantBrandingAssetKind.LOGO,
    content: bytes = PNG,
) -> TenantBrandingAsset:
    """Return one exact D21B5A asset evidence value."""
    return register_tenant_branding_asset(
        tenant_id=tenant_id,
        asset_reference=reference,
        asset_kind=kind,
        media_type="image/png",
        content=content,
        source_evidence_reference="upload-1",
        source_evidence_fingerprint=FP,
        registered_at=NOW,
    )


def collection() -> Collection:
    """Return one indexed collection double."""
    value = Collection()
    registry.ensure_indexes(value)
    return value


def test_index_contract_has_one_identity_unique_and_nonunique_content_lookup() -> None:
    """Identity is unique; identical content may serve multiple references."""
    values = collection()
    assert values.indexes == [
        {
            "key": [("tenant_id", 1), ("asset_reference", 1)],
            "unique": True,
            "name": registry.IDENTITY_INDEX_NAME,
        },
        {
            "key": [("tenant_id", 1), ("content_fingerprint", 1)],
            "unique": False,
            "name": registry.CONTENT_INDEX_NAME,
        },
    ]
    assert not any("expireAfterSeconds" in item for item in values.indexes)


def test_operational_paths_require_active_caller_transaction() -> None:
    """Registry cannot create or resolve outside an active caller transaction."""
    values = collection()
    value = asset()
    for bad in (None, Session(False)):
        with pytest.raises(
            registry.TenantBrandingAssetRegistryTransactionRequiredError
        ):
            registry.create_or_replay(value, PNG, values, session=bad)
        with pytest.raises(
            registry.TenantBrandingAssetRegistryTransactionRequiredError
        ):
            registry.resolve(
                value.tenant_id,
                value.asset_reference,
                expected_content_fingerprint=value.content_fingerprint,
                expected_kind=value.asset_kind,
                collection=values,
                session=bad,
            )
    assert not any(
        name in dir(registry.TenantBrandingAssetRegistry)
        for name in (
            "start_transaction",
            "commit_transaction",
            "abort_transaction",
            "with_transaction",
        )
    )


def test_create_exact_replay_and_session_propagation() -> None:
    """Immutable bytes persist once and exact replay hydrates same evidence."""
    values = collection()
    session = Session()
    value = asset()
    first = registry.create_or_replay(value, PNG, values, session=session)
    replay = registry.create_or_replay(value, PNG, values, session=session)
    assert first == replay
    assert first.asset == value
    assert first.content == PNG
    assert len(values.rows) == 1
    assert all(call[1] is session for call in values.calls)


def test_same_reference_divergent_bytes_or_metadata_conflicts() -> None:
    """An existing tenant/reference cannot be rebound to new immutable evidence."""
    values = collection()
    session = Session()
    original = asset()
    registry.create_or_replay(original, PNG, values, session=session)

    new_bytes = PNG + b"x"
    divergent = asset(content=new_bytes)
    with pytest.raises(registry.TenantBrandingAssetRegistryConflictError):
        registry.create_or_replay(divergent, new_bytes, values, session=session)


def test_create_rejects_content_that_does_not_match_asset_evidence() -> None:
    """Caller bytes must exactly satisfy D21B5A length and SHA3 identity."""
    values = collection()
    session = Session()
    value = asset()
    with pytest.raises(
        registry.TenantBrandingAssetRegistryInputError,
        match="D21B5B_CONTENT_EVIDENCE_MISMATCH",
    ):
        registry.create_or_replay(value, PNG + b"x", values, session=session)


def test_resolve_requires_exact_expected_fingerprint_and_kind() -> None:
    """Profile-supplied content identity and purpose must correlate exactly."""
    values = collection()
    session = Session()
    value = asset()
    registry.create_or_replay(value, PNG, values, session=session)

    resolved = registry.resolve(
        value.tenant_id,
        value.asset_reference,
        expected_content_fingerprint=value.content_fingerprint,
        expected_kind=TenantBrandingAssetKind.LOGO,
        collection=values,
        session=session,
    )
    assert resolved.asset == value
    assert resolved.content == PNG

    with pytest.raises(registry.TenantBrandingAssetRegistryConflictError):
        registry.resolve(
            value.tenant_id,
            value.asset_reference,
            expected_content_fingerprint="f" * 128,
            expected_kind=TenantBrandingAssetKind.LOGO,
            collection=values,
            session=session,
        )
    with pytest.raises(registry.TenantBrandingAssetRegistryConflictError):
        registry.resolve(
            value.tenant_id,
            value.asset_reference,
            expected_content_fingerprint=value.content_fingerprint,
            expected_kind=TenantBrandingAssetKind.FAVICON,
            collection=values,
            session=session,
        )


def test_cross_tenant_resolution_is_indistinguishable_from_absence() -> None:
    """Foreign tenant cannot discover another tenant's asset reference."""
    values = collection()
    session = Session()
    value = asset()
    registry.create_or_replay(value, PNG, values, session=session)
    with pytest.raises(registry.TenantBrandingAssetRegistryNotFoundError):
        registry.resolve(
            "tenant-b",
            value.asset_reference,
            expected_content_fingerprint=value.content_fingerprint,
            expected_kind=value.asset_kind,
            collection=values,
            session=session,
        )


def test_persisted_byte_or_metadata_corruption_rejects() -> None:
    """Durable bytes and metadata are revalidated on every hydration."""
    values = collection()
    session = Session()
    value = asset()
    registry.create_or_replay(value, PNG, values, session=session)

    original = deepcopy(values.rows[0])
    values.rows[0]["content_bytes"] = PNG + b"tampered"
    with pytest.raises(
        registry.TenantBrandingAssetRegistryPersistedRecordInvalidError
    ):
        registry.resolve(
            value.tenant_id,
            value.asset_reference,
            expected_content_fingerprint=value.content_fingerprint,
            expected_kind=value.asset_kind,
            collection=values,
            session=session,
        )
    values.rows[0] = deepcopy(original)

    values.rows[0]["asset_payload"]["fingerprint"] = "e" * 128
    with pytest.raises(
        registry.TenantBrandingAssetRegistryPersistedRecordInvalidError
    ):
        registry.resolve(
            value.tenant_id,
            value.asset_reference,
            expected_content_fingerprint=value.content_fingerprint,
            expected_kind=value.asset_kind,
            collection=values,
            session=session,
        )


def test_duplicate_insert_and_transient_errors_signal_whole_transaction_retry() -> None:
    """Duplicate/transient races require caller to restart the whole transaction."""
    session = Session()
    value = asset()

    duplicate = collection()
    duplicate.force_duplicate = True
    with pytest.raises(registry.TenantBrandingAssetRegistryRetryRequiredError):
        registry.create_or_replay(value, PNG, duplicate, session=session)

    transient_read = collection()
    transient_read.transient_find = True
    with pytest.raises(registry.TenantBrandingAssetRegistryRetryRequiredError):
        registry.create_or_replay(value, PNG, transient_read, session=session)

    transient_insert = collection()
    transient_insert.transient_insert = True
    with pytest.raises(registry.TenantBrandingAssetRegistryRetryRequiredError):
        registry.create_or_replay(value, PNG, transient_insert, session=session)


def test_same_content_may_have_distinct_same_tenant_references() -> None:
    """Content lookup is deliberately nonunique; reference remains authority key."""
    values = collection()
    session = Session()
    first = asset()
    second = asset(reference="asset:tenant-a:logo:secondary")
    registry.create_or_replay(first, PNG, values, session=session)
    registry.create_or_replay(second, PNG, values, session=session)
    assert len(values.rows) == 2
    assert values.rows[0]["content_fingerprint"] == values.rows[1]["content_fingerprint"]


def test_registry_has_no_url_path_provider_browser_or_financial_surface() -> None:
    """Durable resolution remains bytes/evidence only."""
    value = asset()
    values = collection()
    session = Session()
    resolved = registry.create_or_replay(value, PNG, values, session=session)
    serialized = resolved.asset.to_dict()
    forbidden = {
        "url",
        "path",
        "bucket",
        "storage_key",
        "signed_url",
        "profile_id",
        "current",
        "principal_id",
        "role",
        "permission",
        "price",
        "amount",
        "invoice",
        "payment",
        "execution",
        "settlement",
    }
    assert forbidden.isdisjoint(serialized)


# ARTIFACT: test_tenant_branding_asset_registry.py
# VERSION: v1.0.0-D21B5B-TENANT-BRANDING-ASSET-REGISTRY-CERT
# AUTHORITY BOUNDARY: direct immutable byte persistence/resolution evidence only; no profile/current/entitlement/browser/IAM/financial authority
# TENANT POSTURE: exact tenant/reference persistence and foreign-absence behavior
# FAIL-CLOSED POSTURE: transaction absence, divergent evidence, byte/metadata corruption and races reject
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively
# END OF WILSY OS SOVEREIGN ARTIFACT
