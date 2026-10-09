"""WILSY OS — Business Classification Projection V2 Registry certificate.

TITLE: Business Classification Projection V2 Registry Direct Certificate
VERSION: v2.0.0-BUSINESS-CLASSIFICATION-PROJECTION-V2-REGISTRY-TEST
AUTHORITY: Wilsy OS Core Governance

PURPOSE:
    Freeze V2 classification persistence before production registry authoring.

BOUNDARY:
- Separate V2 collection generation.
- Caller-owned active transaction required before dependency reads.
- Exact immutable Business Identity revision + fingerprint validation.
- Official taxonomy snapshots remain read-only authority dependencies.
- No V1 hydration, V1 writes, latest/current inference, entitlement,
  authorization, activation, regulatory-status, or financial authority.
"""

from __future__ import annotations

from copy import deepcopy
from datetime import datetime, timezone
import hashlib
import inspect
from types import SimpleNamespace
from typing import Any, cast

import pytest
from pymongo.errors import DuplicateKeyError

from tools.eos.saas.domain.business_identity import (
    BusinessIdentity,
)

from tools.eos.saas.domain.business_classification_projection import (
    BusinessActivity,
    BusinessActivityConfirmation,
    BusinessActivityRole,
    BusinessClassificationEvidence,
    BusinessClassificationProjection,
    BusinessClassificationReference,
    BusinessClassificationSourceKind,
)

from tools.eos.saas.domain.business_classification_projection_v2 import (
    BusinessClassificationProjectionV2,
)

from tools.eos.saas.business_classification_projection_v2_registry import (
    COLLECTION_NAME,
    VERSION,
    BusinessClassificationProjectionV2Registry,
    BusinessClassificationProjectionV2RegistryError,
)


NOW = datetime(
    2026,
    10,
    8,
    11,
    0,
    tzinfo=timezone.utc,
)

PROFILE_DIGEST = hashlib.sha3_512(
    b"profile-v2"
).hexdigest()

EVIDENCE_DIGEST = hashlib.sha3_512(
    b"evidence-v2"
).hexdigest()

SNAPSHOT_DIGEST = hashlib.sha3_512(
    b"taxonomy-snapshot-v2"
).hexdigest()


class Session:
    """Minimal caller-owned transaction seam."""

    def __init__(
        self,
        *,
        in_transaction: bool = True,
    ) -> None:
        self.in_transaction = in_transaction


class Cursor:
    """Minimal deterministic Mongo-shaped cursor."""

    def __init__(
        self,
        values: list[dict[str, Any]],
    ) -> None:
        self._values = [
            deepcopy(value)
            for value in values
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
            self._values.sort(
                key=lambda value: value[
                    key
                ],
                reverse=order < 0,
            )

        return self

    def __iter__(self):
        return iter(
            deepcopy(
                self._values
            )
        )


class Collection:
    """Deterministic V2 persistence seam."""

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
                deepcopy(query),
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
                deepcopy(query),
                session,
            )
        )

        return Cursor(
            [
                document
                for document in self.documents
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
                deepcopy(document),
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
            inserted_id=document.get(
                "projection_id"
            ),
        )


class BusinessIdentityDependency:
    """Read-only exact Business Identity dependency."""

    def __init__(
        self,
        values: tuple[
            BusinessIdentity,
            ...,
        ],
    ) -> None:
        self.values = values

        self.revision_calls: list[
            tuple[str, int, Any]
        ] = []

        self.fingerprint_calls: list[
            tuple[str, Any]
        ] = []

        self.write_calls = 0

    def get_revision(
        self,
        business_identity_id: str,
        revision: int,
        *,
        session: Any = None,
    ) -> BusinessIdentity | None:
        self.revision_calls.append(
            (
                business_identity_id,
                revision,
                session,
            )
        )

        for value in self.values:
            if (
                value.business_identity_id
                == business_identity_id
                and value.revision
                == revision
            ):
                return value

        return None

    def get_by_fingerprint(
        self,
        identity_fingerprint: str,
        *,
        session: Any = None,
    ) -> BusinessIdentity | None:
        self.fingerprint_calls.append(
            (
                identity_fingerprint,
                session,
            )
        )

        for value in self.values:
            if (
                value.identity_fingerprint
                == identity_fingerprint
            ):
                return value

        return None

    def create(
        self,
        *_args: Any,
        **_kwargs: Any,
    ) -> None:
        self.write_calls += 1
        raise AssertionError(
            "BUSINESS_IDENTITY_WRITE_FORBIDDEN"
        )


class SnapshotDependency:
    """Read-only exact taxonomy snapshot dependency."""

    def __init__(self) -> None:
        self.snapshot = SimpleNamespace(
            snapshot_id="SNAPSHOT-001",
            snapshot_digest=SNAPSHOT_DIGEST,
            scheme_id="ISIC",
            scheme_version="REV5",
            jurisdiction="GLOBAL",
        )

        self.get_calls: list[
            tuple[str, Any]
        ] = []

        self.digest_calls: list[
            tuple[str, Any]
        ] = []

        self.write_calls = 0

    def get(
        self,
        snapshot_id: str,
        *,
        session: Any = None,
    ) -> Any:
        self.get_calls.append(
            (
                snapshot_id,
                session,
            )
        )

        if (
            snapshot_id
            == self.snapshot.snapshot_id
        ):
            return self.snapshot

        return None

    def get_by_digest(
        self,
        snapshot_digest: str,
        *,
        session: Any = None,
    ) -> Any:
        self.digest_calls.append(
            (
                snapshot_digest,
                session,
            )
        )

        if (
            snapshot_digest
            == self.snapshot.snapshot_digest
        ):
            return self.snapshot

        return None

    def create(
        self,
        *_args: Any,
        **_kwargs: Any,
    ) -> None:
        self.write_calls += 1
        raise AssertionError(
            "SNAPSHOT_WRITE_FORBIDDEN"
        )


def business_identity(
    *,
    business_identity_id: str = "BUSINESS-001",
    tenant_id: str = "tenant-a",
    revision: int = 1,
    organization_name: str = "Acme",
    legal_name: str = "Acme (Pty) Ltd",
    supersedes_revision: int | None = None,
) -> BusinessIdentity:
    """Build one certified-shape Business Identity revision."""
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


def classification() -> BusinessClassificationReference:
    """Build one exact snapshot-bound classification reference."""
    return BusinessClassificationReference(
        scheme_id="ISIC",
        scheme_version="REV5",
        code="6201",
        title="Computer programming activities",
        jurisdiction="GLOBAL",
        taxonomy_snapshot_id="SNAPSHOT-001",
        taxonomy_snapshot_digest=SNAPSHOT_DIGEST,
    )


def evidence() -> BusinessClassificationEvidence:
    """Build one immutable evidence fixture."""
    return BusinessClassificationEvidence(
        evidence_id="EVIDENCE-1",
        source_kind=(
            BusinessClassificationSourceKind.TENANT_DECLARATION
        ),
        source_reference="tenant-profile:industry",
        observed_at=NOW,
        source_digest=EVIDENCE_DIGEST,
    )


def activity() -> BusinessActivity:
    """Build one immutable business activity."""
    return BusinessActivity(
        activity_id="ACTIVITY-1",
        role=BusinessActivityRole.PRIMARY,
        description="Synthetic business activity",
        confirmation=(
            BusinessActivityConfirmation.CONFIRMED
        ),
        confidence_basis_points=9500,
        evidence_refs=(
            "EVIDENCE-1",
        ),
        classifications=(
            classification(),
        ),
    )


def projection(
    *,
    business: BusinessIdentity | None = None,
    projection_id: str = "V2-PROJECTION-001",
    revision: int = 1,
    supersedes_projection_id: str | None = None,
) -> BusinessClassificationProjectionV2:
    """Build one explicitly Business Identity-bound V2 projection."""
    identity = (
        business
        if business is not None
        else business_identity()
    )

    return BusinessClassificationProjectionV2(
        projection_id=projection_id,
        tenant_id=identity.tenant_id,
        business_identity_id=(
            identity.business_identity_id
        ),
        business_identity_revision=(
            identity.revision
        ),
        business_identity_fingerprint=(
            identity.identity_fingerprint
        ),
        revision=revision,
        source_profile_digest=PROFILE_DIGEST,
        evidences=(
            evidence(),
        ),
        activities=(
            activity(),
        ),
        effective_from=NOW,
        created_at=NOW,
        supersedes_projection_id=(
            supersedes_projection_id
        ),
    )


def historical_v1() -> BusinessClassificationProjection:
    """Build one historical V1 tenant-scoped projection."""
    return BusinessClassificationProjection(
        projection_id="V1-HISTORICAL-001",
        tenant_id="tenant-a",
        revision=1,
        source_profile_digest=PROFILE_DIGEST,
        evidences=(
            evidence(),
        ),
        activities=(
            activity(),
        ),
        effective_from=NOW,
        created_at=NOW,
        supersedes_projection_id=None,
    )


def registry(
    *,
    identities: tuple[
        BusinessIdentity,
        ...,
    ] | None = None,
) -> tuple[
    BusinessClassificationProjectionV2Registry,
    Collection,
    BusinessIdentityDependency,
    SnapshotDependency,
]:
    """Build exact frozen V2 registry dependencies."""
    values = (
        identities
        if identities is not None
        else (
            business_identity(),
        )
    )

    store = Collection()

    identity_dependency = (
        BusinessIdentityDependency(
            values
        )
    )

    snapshot_dependency = (
        SnapshotDependency()
    )

    value = (
        BusinessClassificationProjectionV2Registry(
            store,
            business_identity_registry=(
                identity_dependency
            ),
            snapshot_registry=(
                snapshot_dependency
            ),
        )
    )

    return (
        value,
        store,
        identity_dependency,
        snapshot_dependency,
    )


def persist_direct(
    store: Collection,
    value: BusinessClassificationProjectionV2,
) -> None:
    """Seed V2 durable truth without registry create authority."""
    store.documents.append(
        deepcopy(
            value.to_dict()
        )
    )


def test_v2_collection_name_exact() -> None:
    assert (
        VERSION
        == "v2.0.0-WILSY-BUSINESS-CLASSIFICATION-PROJECTION-REGISTRY"
    )

    assert (
        COLLECTION_NAME
        == "business_classification_projections_v2"
    )


def test_v2_indexes_exact_and_no_ttl() -> None:
    _value, store, _identity, _snapshot = registry()

    BusinessClassificationProjectionV2Registry.ensure_indexes(
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
        "business_classification_v2_projection_id_unique",
        "business_classification_v2_fingerprint_unique",
        "business_classification_v2_tenant_business_revision_unique",
        "business_classification_v2_tenant_business_effective_from",
        "business_classification_v2_business_identity_binding",
        "business_classification_v2_tenant_supersedes_projection",
    }

    assert (
        observed[
            "business_classification_v2_projection_id_unique"
        ][1]["unique"]
        is True
    )

    assert (
        observed[
            "business_classification_v2_fingerprint_unique"
        ][1]["unique"]
        is True
    )

    assert (
        observed[
            "business_classification_v2_tenant_business_revision_unique"
        ][1]["unique"]
        is True
    )

    assert all(
        "expireAfterSeconds"
        not in kwargs
        for _args, kwargs
        in store.index_calls
    )


def test_missing_session_rejected_before_dependency_reads() -> None:
    value, store, identity_dep, snapshot_dep = registry()

    with pytest.raises(
        BusinessClassificationProjectionV2RegistryError,
        match="ACTIVE_TRANSACTION_REQUIRED",
    ):
        value.create(
            projection(),
            session=None,
        )

    assert identity_dep.revision_calls == []
    assert identity_dep.fingerprint_calls == []
    assert snapshot_dep.get_calls == []
    assert snapshot_dep.digest_calls == []
    assert store.insert_calls == []


def test_inactive_transaction_rejected_before_dependency_reads() -> None:
    value, store, identity_dep, snapshot_dep = registry()

    with pytest.raises(
        BusinessClassificationProjectionV2RegistryError,
        match="ACTIVE_TRANSACTION_REQUIRED",
    ):
        value.create(
            projection(),
            session=Session(
                in_transaction=False
            ),
        )

    assert identity_dep.revision_calls == []
    assert snapshot_dep.get_calls == []
    assert store.insert_calls == []


def test_business_identity_exact_revision_and_fingerprint_both_resolved() -> None:
    identity = business_identity()

    value, _store, identity_dep, _snapshot_dep = registry(
        identities=(
            identity,
        )
    )

    assert (
        value.create(
            projection(
                business=identity
            ),
            session=Session(),
        ).business_identity_fingerprint
        == identity.identity_fingerprint
    )

    assert len(
        identity_dep.revision_calls
    ) == 1

    assert len(
        identity_dep.fingerprint_calls
    ) == 1


def test_business_identity_revision_fingerprint_disagreement_rejected() -> None:
    first = business_identity(
        revision=1,
    )

    second = business_identity(
        revision=2,
        supersedes_revision=1,
    )

    value, store, _identity_dep, _snapshot_dep = registry(
        identities=(
            first,
            second,
        )
    )

    candidate = projection(
        business=first
    )

    payload = candidate.to_dict()
    payload[
        "business_identity_fingerprint"
    ] = second.identity_fingerprint

    # Restore the derived projection fingerprint for the altered binding.
    payload.pop(
        "fingerprint"
    )

    with pytest.raises(
        (
            ValueError,
            BusinessClassificationProjectionV2RegistryError,
        )
    ):
        BusinessClassificationProjectionV2.from_dict(
            payload
        )

    assert store.insert_calls == []


def test_business_identity_tenant_mismatch_rejected() -> None:
    identity = business_identity(
        tenant_id="tenant-a",
    )

    value, store, _identity_dep, _snapshot_dep = registry(
        identities=(
            identity,
        )
    )

    candidate = projection(
        business=identity
    )

    payload = candidate.to_dict()
    payload[
        "tenant_id"
    ] = "tenant-b"

    # Direct constructor yields valid fingerprint for the mismatched tenant,
    # allowing the registry dependency check—not hydration corruption—to decide.
    mismatched = BusinessClassificationProjectionV2(
        projection_id=payload[
            "projection_id"
        ],
        tenant_id="tenant-b",
        business_identity_id=(
            identity.business_identity_id
        ),
        business_identity_revision=(
            identity.revision
        ),
        business_identity_fingerprint=(
            identity.identity_fingerprint
        ),
        revision=1,
        source_profile_digest=PROFILE_DIGEST,
        evidences=(evidence(),),
        activities=(activity(),),
        effective_from=NOW,
        created_at=NOW,
        supersedes_projection_id=None,
    )

    with pytest.raises(
        BusinessClassificationProjectionV2RegistryError
    ):
        value.create(
            mismatched,
            session=Session(),
        )

    assert store.insert_calls == []


def test_business_identity_dependency_is_read_only() -> None:
    value, _store, identity_dep, _snapshot_dep = registry()

    value.create(
        projection(),
        session=Session(),
    )

    assert identity_dep.write_calls == 0


def test_snapshot_dependency_remains_read_only() -> None:
    value, _store, _identity_dep, snapshot_dep = registry()

    value.create(
        projection(),
        session=Session(),
    )

    assert snapshot_dep.write_calls == 0
    assert len(
        snapshot_dep.get_calls
    ) >= 1
    assert len(
        snapshot_dep.digest_calls
    ) >= 1


def test_same_business_classification_revision_stream_isolated() -> None:
    business_a = business_identity(
        business_identity_id="BUSINESS-A",
    )

    business_b = business_identity(
        business_identity_id="BUSINESS-B",
    )

    value, store, _identity_dep, _snapshot_dep = registry(
        identities=(
            business_a,
            business_b,
        )
    )

    value.create(
        projection(
            business=business_a,
            projection_id="PROJ-A-1",
        ),
        session=Session(),
    )

    value.create(
        projection(
            business=business_b,
            projection_id="PROJ-B-1",
        ),
        session=Session(),
    )

    assert len(
        store.documents
    ) == 2


def test_two_businesses_same_tenant_can_each_have_revision_one() -> None:
    first = business_identity(
        business_identity_id="BUSINESS-A",
    )

    second = business_identity(
        business_identity_id="BUSINESS-B",
    )

    value, store, _identity_dep, _snapshot_dep = registry(
        identities=(
            first,
            second,
        )
    )

    for identity_value, projection_id in (
        (
            first,
            "PROJ-A-1",
        ),
        (
            second,
            "PROJ-B-1",
        ),
    ):
        value.create(
            projection(
                business=identity_value,
                projection_id=projection_id,
                revision=1,
            ),
            session=Session(),
        )

    assert len(
        store.documents
    ) == 2


def test_cross_business_projection_supersession_rejected() -> None:
    first = business_identity(
        business_identity_id="BUSINESS-A",
    )

    second = business_identity(
        business_identity_id="BUSINESS-B",
    )

    value, store, _identity_dep, _snapshot_dep = registry(
        identities=(
            first,
            second,
        )
    )

    prior = projection(
        business=first,
        projection_id="PROJ-A-1",
    )

    persist_direct(
        store,
        prior,
    )

    later = projection(
        business=second,
        projection_id="PROJ-B-2",
        revision=2,
        supersedes_projection_id="PROJ-A-1",
    )

    with pytest.raises(
        BusinessClassificationProjectionV2RegistryError
    ):
        value.create(
            later,
            session=Session(),
        )


def test_explicit_business_identity_revision_change_across_projection_history_allowed() -> None:
    first = business_identity(
        revision=1,
    )

    second = business_identity(
        revision=2,
        supersedes_revision=1,
    )

    value, store, _identity_dep, _snapshot_dep = registry(
        identities=(
            first,
            second,
        )
    )

    prior = projection(
        business=first,
        projection_id="PROJ-1",
        revision=1,
    )

    persist_direct(
        store,
        prior,
    )

    later = projection(
        business=second,
        projection_id="PROJ-2",
        revision=2,
        supersedes_projection_id="PROJ-1",
    )

    assert (
        value.create(
            later,
            session=Session(),
        )
        == later
    )


def test_registry_does_not_infer_latest_business_identity() -> None:
    public = {
        name
        for name, member
        in inspect.getmembers(
            BusinessClassificationProjectionV2Registry
        )
        if (
            callable(member)
            and not name.startswith("_")
        )
    }

    assert "get_latest" not in public
    assert "get_current" not in public
    assert "resolve_latest_business_identity" not in public


def test_exact_replay() -> None:
    candidate = projection()

    value, store, _identity_dep, _snapshot_dep = registry()

    persist_direct(
        store,
        candidate,
    )

    assert (
        value.create(
            candidate,
            session=Session(),
        )
        == candidate
    )

    assert len(
        store.documents
    ) == 1


def test_projection_id_conflict() -> None:
    durable = projection()

    identity = business_identity(
        organization_name="Changed",
        legal_name="Changed (Pty) Ltd",
    )

    conflicting = projection(
        business=identity,
        projection_id=durable.projection_id,
    )

    value, store, _identity_dep, _snapshot_dep = registry(
        identities=(
            identity,
        )
    )

    persist_direct(
        store,
        durable,
    )

    with pytest.raises(
        BusinessClassificationProjectionV2RegistryError
    ):
        value.create(
            conflicting,
            session=Session(),
        )


def test_fingerprint_conflict() -> None:
    candidate = projection()

    collision = candidate.to_dict()
    collision[
        "projection_id"
    ] = "OTHER-PROJECTION"

    value, store, _identity_dep, _snapshot_dep = registry()

    store.documents.append(
        collision
    )

    with pytest.raises(
        BusinessClassificationProjectionV2RegistryError
    ):
        value.create(
            candidate,
            session=Session(),
        )


def test_tenant_business_revision_conflict() -> None:
    durable = projection()

    conflicting = BusinessClassificationProjectionV2(
        projection_id="OTHER-PROJECTION",
        tenant_id=durable.tenant_id,
        business_identity_id=(
            durable.business_identity_id
        ),
        business_identity_revision=(
            durable.business_identity_revision
        ),
        business_identity_fingerprint=(
            durable.business_identity_fingerprint
        ),
        revision=durable.revision,
        source_profile_digest=hashlib.sha3_512(
            b"different-source"
        ).hexdigest(),
        evidences=(evidence(),),
        activities=(activity(),),
        effective_from=NOW,
        created_at=NOW,
        supersedes_projection_id=None,
    )

    value, store, _identity_dep, _snapshot_dep = registry()

    persist_direct(
        store,
        durable,
    )

    with pytest.raises(
        BusinessClassificationProjectionV2RegistryError
    ):
        value.create(
            conflicting,
            session=Session(),
        )


def test_registry_is_insert_only() -> None:
    source = inspect.getsource(
        BusinessClassificationProjectionV2Registry
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


def test_v1_collection_not_touched() -> None:
    assert (
        COLLECTION_NAME
        != "business_classification_projections"
    )

    source = inspect.getsource(
        BusinessClassificationProjectionV2Registry
    )

    assert (
        '"business_classification_projections"'
        not in source
    )


def test_v1_payload_not_hydrated_as_v2() -> None:
    payload = historical_v1().to_dict()

    with pytest.raises(
        ValueError
    ):
        BusinessClassificationProjectionV2.from_dict(
            payload
        )


def test_no_latest_current_authority() -> None:
    assert not hasattr(
        BusinessClassificationProjectionV2Registry,
        "get_latest",
    )

    assert not hasattr(
        BusinessClassificationProjectionV2Registry,
        "get_current",
    )


def test_no_commercial_authorization_activation_or_financial_authority() -> None:
    public = {
        name
        for name, member
        in inspect.getmembers(
            BusinessClassificationProjectionV2Registry
        )
        if (
            callable(member)
            and not name.startswith("_")
        )
    }

    assert not (
        public
        & {
            "authorize",
            "grant_permission",
            "grant_entitlement",
            "subscribe",
            "activate",
            "activate_service_pack",
            "invoice",
            "charge",
            "collect",
            "settle",
            "execute_payment",
            "refund",
        }
    )


# ARTIFACT: test_business_classification_projection_v2_registry.py
