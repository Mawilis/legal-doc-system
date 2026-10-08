"""WILSY OS — Business Identity Registry direct certificate.

TITLE: Business Identity Registry Direct Certificate
VERSION: v1.0.0-BUSINESS-IDENTITY-REGISTRY-TEST
AUTHORITY: Wilsy OS Core Governance

PURPOSE:
    Certify the prospective immutable Business Identity persistence boundary
    before production implementation exists.

BOUNDARY:
- Insert-only immutable Business Identity revision history.
- Caller-owned active transaction required before tenant dependency reads.
- Tenant dependency is read-only canonical identity validation only.
- No unversioned subject read and no latest/current authority.
- No invented N-1 supersession rule.
- No classification, taxonomy, subscription, entitlement, permission,
  authorization, activation, regulatory-status, tax-validity, AI-execution,
  or financial authority.
"""

from __future__ import annotations

from copy import deepcopy
from datetime import datetime, timezone
import inspect
from types import SimpleNamespace
from typing import Any, cast

import pytest
from pymongo.errors import DuplicateKeyError

from tools.eos.saas.domain.business_identity import (
    BusinessIdentity,
)

from tools.eos.saas.business_identity_registry import (
    COLLECTION_NAME,
    VERSION,
    BusinessIdentityRegistry,
    BusinessIdentityRegistryError,
)


NOW = datetime(
    2026,
    10,
    8,
    8,
    0,
    tzinfo=timezone.utc,
)


def identity(
    *,
    business_identity_id: str = "BUSINESS-001",
    tenant_id: str = "tenant-a",
    revision: int = 1,
    organization_name: str = "Acme Holdings",
    legal_name: str = "Acme Holdings (Pty) Ltd",
    supersedes_revision: int | None = None,
) -> BusinessIdentity:
    """Build one immutable Business Identity revision."""
    return BusinessIdentity(
        business_identity_id=business_identity_id,
        tenant_id=tenant_id,
        revision=revision,
        organization_name=organization_name,
        legal_name=legal_name,
        created_at=NOW,
        effective_from=NOW,
        supersedes_revision=supersedes_revision,
    )


class Session:
    """Minimal caller-owned transaction fixture."""

    def __init__(
        self,
        *,
        in_transaction: bool = True,
    ) -> None:
        self.in_transaction = in_transaction


class Cursor:
    """Minimal Mongo-shaped deterministic cursor."""

    def __init__(
        self,
        rows: list[dict[str, Any]],
    ) -> None:
        self._rows = [
            deepcopy(row)
            for row in rows
        ]

    def sort(
        self,
        keys: Any,
        direction: int | None = None,
    ) -> Cursor:
        if isinstance(
            keys,
            str,
        ):
            assert direction is not None

            normalized = [
                (
                    keys,
                    direction,
                )
            ]
        else:
            normalized = list(
                keys
            )

        for key, order in reversed(
            normalized
        ):
            reverse = order < 0

            def sort_key(
                row: dict[str, Any],
                *,
                field_name: str = key,
            ) -> tuple[int, str]:
                value = row[
                    field_name
                ]

                if isinstance(
                    value,
                    int,
                ) and not isinstance(
                    value,
                    bool,
                ):
                    return (
                        value,
                        "",
                    )

                assert isinstance(
                    value,
                    str,
                )

                return (
                    0,
                    value,
                )

            self._rows.sort(
                key=sort_key,
                reverse=reverse,
            )

        return self

    def __iter__(self):
        return iter(
            deepcopy(
                self._rows
            )
        )


class Collection:
    """Deterministic persistence seam."""

    def __init__(self) -> None:
        self.documents: list[
            dict[str, Any]
        ] = []

        self.index_calls: list[
            tuple[
                tuple[Any, ...],
                dict[str, Any],
            ]
        ] = []

        self.find_one_calls: list[
            tuple[
                dict[str, Any],
                Any,
            ]
        ] = []

        self.find_calls: list[
            tuple[
                dict[str, Any],
                Any,
            ]
        ] = []

        self.insert_calls: list[
            tuple[
                dict[str, Any],
                Any,
            ]
        ] = []

        self.raise_duplicate_on_insert = False

    def create_index(
        self,
        *args: Any,
        **kwargs: Any,
    ) -> str:
        self.index_calls.append(
            (
                args,
                kwargs,
            )
        )

        return str(
            kwargs.get(
                "name",
                "index",
            )
        )

    def find_one(
        self,
        query: dict[str, Any],
        *,
        session: Any = None,
    ) -> dict[str, Any] | None:
        self.find_one_calls.append(
            (
                deepcopy(
                    query
                ),
                session,
            )
        )

        for document in self.documents:
            if all(
                document.get(key)
                == value
                for key, value
                in query.items()
            ):
                return deepcopy(
                    document
                )

        return None

    def find(
        self,
        query: dict[str, Any],
        *,
        session: Any = None,
    ) -> Cursor:
        self.find_calls.append(
            (
                deepcopy(
                    query
                ),
                session,
            )
        )

        return Cursor(
            [
                document
                for document
                in self.documents
                if all(
                    document.get(key)
                    == value
                    for key, value
                    in query.items()
                )
            ]
        )

    def insert_one(
        self,
        document: dict[str, Any],
        *,
        session: Any = None,
    ) -> Any:
        self.insert_calls.append(
            (
                deepcopy(
                    document
                ),
                session,
            )
        )

        if self.raise_duplicate_on_insert:
            raise DuplicateKeyError(
                "synthetic competing insert"
            )

        self.documents.append(
            deepcopy(
                document
            )
        )

        return SimpleNamespace(
            inserted_id=None,
        )


class TenantDependency:
    """Read-only canonical tenant dependency seam."""

    def __init__(
        self,
        *,
        existing: set[str] | None = None,
    ) -> None:
        self.existing = (
            set(existing)
            if existing is not None
            else {
                "tenant-a",
                "tenant-b",
            }
        )

        self.calls: list[
            tuple[
                str,
                Any,
                bool,
            ]
        ] = []

        self.create_calls = 0
        self.update_calls = 0
        self.archive_calls = 0

    def resolve_canonical_tenant(
        self,
        tenant_reference: str,
        *,
        session: Any = None,
        allow_alias: bool = False,
    ) -> Any:
        self.calls.append(
            (
                tenant_reference,
                session,
                allow_alias,
            )
        )

        if (
            tenant_reference
            not in self.existing
        ):
            raise RuntimeError(
                "TENANT_REGISTRY_CANONICAL_NOT_FOUND"
            )

        return SimpleNamespace(
            tenant_id=tenant_reference,
            status="ACTIVE",
        )

    def create(
        self,
        *_args: Any,
        **_kwargs: Any,
    ) -> None:
        self.create_calls += 1

        raise AssertionError(
            "TENANT_DEPENDENCY_WRITE_FORBIDDEN"
        )

    def update(
        self,
        *_args: Any,
        **_kwargs: Any,
    ) -> None:
        self.update_calls += 1

        raise AssertionError(
            "TENANT_DEPENDENCY_WRITE_FORBIDDEN"
        )

    def archive(
        self,
        *_args: Any,
        **_kwargs: Any,
    ) -> None:
        self.archive_calls += 1

        raise AssertionError(
            "TENANT_DEPENDENCY_WRITE_FORBIDDEN"
        )


def registry(
    *,
    collection: Collection | None = None,
    tenants: set[str] | None = None,
) -> tuple[
    BusinessIdentityRegistry,
    Collection,
    TenantDependency,
]:
    """Build prospective registry dependency shape."""
    store = (
        collection
        if collection is not None
        else Collection()
    )

    tenant_dependency = (
        TenantDependency(
            existing=tenants
        )
    )

    value = BusinessIdentityRegistry(
        store,
        tenant_registry=tenant_dependency,
    )

    return (
        value,
        store,
        tenant_dependency,
    )


def persist_direct(
    store: Collection,
    value: BusinessIdentity,
) -> None:
    """Seed durable identity truth without registry create authority."""
    store.documents.append(
        deepcopy(
            value.to_dict()
        )
    )


def test_version_and_collection_exact() -> None:
    assert (
        VERSION
        == "v1.0.0-WILSY-BUSINESS-IDENTITY-REGISTRY"
    )

    assert (
        COLLECTION_NAME
        == "business_identities"
    )


def test_public_surface_exact() -> None:
    public = {
        name
        for name, member
        in inspect.getmembers(
            BusinessIdentityRegistry
        )
        if (
            callable(
                member
            )
            and not name.startswith("_")
        )
    }

    assert public == {
        "ensure_indexes",
        "create",
        "get_revision",
        "get_by_fingerprint",
        "get_history",
        "get_by_tenant",
    }


def test_indexes_exact_and_no_ttl() -> None:
    _registry, store, _tenants = registry()

    BusinessIdentityRegistry.ensure_indexes(
        store
    )

    observed = {
        kwargs["name"]: (
            args,
            kwargs,
        )
        for args, kwargs
        in store.index_calls
    }

    assert set(
        observed
    ) == {
        "business_identity_subject_revision_unique",
        "business_identity_fingerprint_unique",
        "business_identity_tenant_subject_revision",
        "business_identity_tenant_effective_from",
        "business_identity_subject_supersedes_revision",
    }

    assert (
        observed[
            "business_identity_subject_revision_unique"
        ][1]["unique"]
        is True
    )

    assert (
        observed[
            "business_identity_fingerprint_unique"
        ][1]["unique"]
        is True
    )

    assert all(
        "expireAfterSeconds"
        not in kwargs
        for _args, kwargs
        in store.index_calls
    )


def test_missing_session_rejected_before_tenant_read() -> None:
    value, store, tenants = registry()

    with pytest.raises(
        BusinessIdentityRegistryError,
        match="ACTIVE_TRANSACTION_REQUIRED",
    ):
        value.create(
            identity(),
            session=None,
        )

    assert tenants.calls == []
    assert store.find_one_calls == []
    assert store.insert_calls == []


def test_inactive_transaction_rejected_before_tenant_read() -> None:
    value, store, tenants = registry()

    with pytest.raises(
        BusinessIdentityRegistryError,
        match="ACTIVE_TRANSACTION_REQUIRED",
    ):
        value.create(
            identity(),
            session=Session(
                in_transaction=False
            ),
        )

    assert tenants.calls == []
    assert store.find_one_calls == []
    assert store.insert_calls == []


def test_create_accepts_only_business_identity_domain() -> None:
    value, store, tenants = registry()

    with pytest.raises(
        BusinessIdentityRegistryError
    ):
        value.create(
            cast(
                Any,
                object(),
            ),
            session=Session(),
        )

    assert tenants.calls == []
    assert store.insert_calls == []


def test_candidate_strict_rehydration_required(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    value, store, _tenants = registry()

    called = {
        "count": 0,
    }

    original = BusinessIdentity.from_dict

    def strict(
        cls: type[
            BusinessIdentity
        ],
        payload: Any,
    ) -> BusinessIdentity:
        called["count"] += 1

        return original(
            payload
        )

    monkeypatch.setattr(
        BusinessIdentity,
        "from_dict",
        classmethod(
            strict
        ),
    )

    candidate = identity()

    assert (
        value.create(
            candidate,
            session=Session(),
        )
        == candidate
    )

    assert called[
        "count"
    ] >= 1

    assert len(
        store.insert_calls
    ) == 1


def test_missing_tenant_rejected_before_insert() -> None:
    value, store, tenants = registry(
        tenants=set()
    )

    with pytest.raises(
        BusinessIdentityRegistryError
    ):
        value.create(
            identity(),
            session=Session(),
        )

    assert len(
        tenants.calls
    ) == 1

    assert store.insert_calls == []


def test_existing_tenant_allows_insert() -> None:
    value, store, tenants = registry()

    candidate = identity()

    assert (
        value.create(
            candidate,
            session=Session(),
        )
        == candidate
    )

    assert tenants.calls[
        0
    ][0] == "tenant-a"

    assert tenants.calls[
        0
    ][2] is False

    assert len(
        store.insert_calls
    ) == 1


def test_tenant_dependency_is_read_only() -> None:
    value, _store, tenants = registry()

    value.create(
        identity(),
        session=Session(),
    )

    assert tenants.create_calls == 0
    assert tenants.update_calls == 0
    assert tenants.archive_calls == 0


def test_revision_one_requires_no_predecessor_lookup() -> None:
    value, store, _tenants = registry()

    candidate = identity(
        revision=1
    )

    value.create(
        candidate,
        session=Session(),
    )

    assert not any(
        query
        == {
            "business_identity_id":
                candidate.business_identity_id,
            "revision":
                0,
        }
        for query, _session
        in store.find_one_calls
    )


def test_later_revision_requires_existing_declared_predecessor() -> None:
    prior = identity(
        revision=1,
    )

    later = identity(
        revision=7,
        supersedes_revision=1,
    )

    value, store, _tenants = registry()

    persist_direct(
        store,
        prior,
    )

    assert (
        value.create(
            later,
            session=Session(),
        )
        == later
    )


def test_predecessor_must_share_business_identity_id() -> None:
    prior = identity(
        business_identity_id="BUSINESS-OTHER",
        revision=1,
    )

    later = identity(
        business_identity_id="BUSINESS-001",
        revision=2,
        supersedes_revision=1,
    )

    value, store, _tenants = registry()

    persist_direct(
        store,
        prior,
    )

    with pytest.raises(
        BusinessIdentityRegistryError
    ):
        value.create(
            later,
            session=Session(),
        )

    assert store.insert_calls == []


def test_predecessor_must_share_tenant_id() -> None:
    prior = identity(
        tenant_id="tenant-b",
        revision=1,
    )

    later = identity(
        tenant_id="tenant-a",
        revision=2,
        supersedes_revision=1,
    )

    value, store, _tenants = registry()

    persist_direct(
        store,
        prior,
    )

    with pytest.raises(
        BusinessIdentityRegistryError
    ):
        value.create(
            later,
            session=Session(),
        )

    assert store.insert_calls == []


def test_corrupt_predecessor_rejected() -> None:
    prior = identity(
        revision=1,
    ).to_dict()

    prior[
        "identity_fingerprint"
    ] = "0" * 128

    later = identity(
        revision=2,
        supersedes_revision=1,
    )

    value, store, _tenants = registry()

    store.documents.append(
        prior
    )

    with pytest.raises(
        BusinessIdentityRegistryError
    ):
        value.create(
            later,
            session=Session(),
        )

    assert store.insert_calls == []


def test_registry_does_not_invent_n_minus_one_rule() -> None:
    prior = identity(
        revision=2,
        supersedes_revision=1,
    )

    later = identity(
        revision=7,
        supersedes_revision=2,
    )

    value, store, _tenants = registry()

    persist_direct(
        store,
        prior,
    )

    assert (
        value.create(
            later,
            session=Session(),
        )
        == later
    )


def test_create_persists_exact_domain_serialization() -> None:
    value, store, _tenants = registry()

    candidate = identity()

    value.create(
        candidate,
        session=Session(),
    )

    assert store.documents == [
        candidate.to_dict()
    ]


def test_exact_replay_returns_identical_durable_revision() -> None:
    value, store, _tenants = registry()

    candidate = identity()

    persist_direct(
        store,
        candidate,
    )

    observed = value.create(
        candidate,
        session=Session(),
    )

    assert observed == candidate
    assert store.insert_calls == []
    assert len(store.documents) == 1


def test_subject_revision_conflict_rejected_before_insert() -> None:
    durable = identity()

    conflicting = identity(
        organization_name="Changed Organization",
    )

    value, store, _tenants = registry()

    persist_direct(
        store,
        durable,
    )

    with pytest.raises(
        BusinessIdentityRegistryError
    ):
        value.create(
            conflicting,
            session=Session(),
        )

    assert store.insert_calls == []


def test_fingerprint_conflict_rejected_before_insert() -> None:
    candidate = identity(
        business_identity_id="BUSINESS-CANDIDATE",
    )

    collision = identity(
        business_identity_id="BUSINESS-OTHER",
    ).to_dict()

    collision[
        "identity_fingerprint"
    ] = candidate.identity_fingerprint

    value, store, _tenants = registry()

    store.documents.append(
        collision
    )

    with pytest.raises(
        BusinessIdentityRegistryError
    ):
        value.create(
            candidate,
            session=Session(),
        )

    assert store.insert_calls == []


def test_duplicate_race_fails_closed_without_post_error_read() -> None:
    value, store, _tenants = registry()

    store.raise_duplicate_on_insert = True

    with pytest.raises(
        BusinessIdentityRegistryError
    ):
        value.create(
            identity(),
            session=Session(),
        )

    assert len(
        store.insert_calls
    ) == 1


def test_get_revision_strictly_hydrates() -> None:
    value, store, _tenants = registry()

    candidate = identity()

    persist_direct(
        store,
        candidate,
    )

    assert (
        value.get_revision(
            candidate.business_identity_id,
            candidate.revision,
        )
        == candidate
    )


def test_get_by_fingerprint_strictly_hydrates() -> None:
    value, store, _tenants = registry()

    candidate = identity()

    persist_direct(
        store,
        candidate,
    )

    assert (
        value.get_by_fingerprint(
            candidate.identity_fingerprint
        )
        == candidate
    )


def test_get_history_revision_ordered() -> None:
    first = identity(
        revision=1,
    )

    second = identity(
        revision=2,
        supersedes_revision=1,
    )

    seventh = identity(
        revision=7,
        supersedes_revision=2,
    )

    value, store, _tenants = registry()

    for candidate in (
        seventh,
        first,
        second,
    ):
        persist_direct(
            store,
            candidate,
        )

    assert value.get_history(
        "BUSINESS-001"
    ) == (
        first,
        second,
        seventh,
    )


def test_get_by_tenant_subject_then_revision_ordered() -> None:
    a1 = identity(
        business_identity_id="BUSINESS-A",
        revision=1,
    )

    a2 = identity(
        business_identity_id="BUSINESS-A",
        revision=2,
        supersedes_revision=1,
    )

    b1 = identity(
        business_identity_id="BUSINESS-B",
        revision=1,
    )

    value, store, _tenants = registry()

    for candidate in (
        b1,
        a2,
        a1,
    ):
        persist_direct(
            store,
            candidate,
        )

    assert value.get_by_tenant(
        "tenant-a"
    ) == (
        a1,
        a2,
        b1,
    )


def test_corrupt_persisted_revision_rejected() -> None:
    value, store, _tenants = registry()

    document = identity().to_dict()

    document[
        "identity_fingerprint"
    ] = "0" * 128

    store.documents.append(
        document
    )

    with pytest.raises(
        BusinessIdentityRegistryError
    ):
        value.get_revision(
            "BUSINESS-001",
            1,
        )


def test_registry_is_insert_only() -> None:
    source = inspect.getsource(
        BusinessIdentityRegistry
    )

    for forbidden in (
        ".update_one(",
        ".update_many(",
        ".replace_one(",
        ".delete_one(",
        ".delete_many(",
        ".find_one_and_update(",
        ".find_one_and_replace(",
        ".find_one_and_delete(",
    ):
        assert forbidden not in source


def test_registry_has_no_latest_or_current_authority() -> None:
    for forbidden in (
        "get_latest",
        "get_current",
        "set_current",
        "activate",
    ):
        assert not hasattr(
            BusinessIdentityRegistry,
            forbidden,
        )


def test_registry_has_no_unversioned_subject_read() -> None:
    public = {
        name
        for name, member
        in inspect.getmembers(
            BusinessIdentityRegistry
        )
        if (
            callable(
                member
            )
            and not name.startswith("_")
        )
    }

    assert "get" not in public
    assert "get_by_business_identity_id" not in public


def test_registry_does_not_enforce_single_business_per_tenant() -> None:
    value, store, _tenants = registry()

    first = identity(
        business_identity_id="BUSINESS-A",
    )

    second = identity(
        business_identity_id="BUSINESS-B",
    )

    value.create(
        first,
        session=Session(),
    )

    value.create(
        second,
        session=Session(),
    )

    assert len(
        store.documents
    ) == 2


def test_registry_contains_no_classification_authority() -> None:
    public = {
        name
        for name, member
        in inspect.getmembers(
            BusinessIdentityRegistry
        )
        if callable(member)
        and not name.startswith("_")
    }

    assert not (
        public
        & {
            "classify",
            "set_industry",
            "set_sector",
            "map_taxonomy",
        }
    )


def test_registry_contains_no_entitlement_or_subscription_authority() -> None:
    public = {
        name
        for name, member
        in inspect.getmembers(
            BusinessIdentityRegistry
        )
        if callable(member)
        and not name.startswith("_")
    }

    assert not (
        public
        & {
            "grant_entitlement",
            "subscribe",
            "set_plan",
            "set_features",
        }
    )


def test_registry_contains_no_authorization_or_activation_authority() -> None:
    public = {
        name
        for name, member
        in inspect.getmembers(
            BusinessIdentityRegistry
        )
        if callable(member)
        and not name.startswith("_")
    }

    assert not (
        public
        & {
            "authorize",
            "grant_permission",
            "assign_role",
            "activate",
            "activate_service_pack",
        }
    )


def test_registry_contains_no_regulatory_or_tax_validity_authority() -> None:
    public = {
        name
        for name, member
        in inspect.getmembers(
            BusinessIdentityRegistry
        )
        if callable(member)
        and not name.startswith("_")
    }

    assert not (
        public
        & {
            "verify_tax_registration",
            "set_regulatory_status",
            "approve_compliance",
        }
    )


def test_registry_contains_no_financial_authority() -> None:
    public = {
        name
        for name, member
        in inspect.getmembers(
            BusinessIdentityRegistry
        )
        if callable(member)
        and not name.startswith("_")
    }

    assert not (
        public
        & {
            "invoice",
            "charge",
            "collect",
            "settle",
            "execute_payment",
            "refund",
        }
    )


# ARTIFACT: test_business_identity_registry.py
