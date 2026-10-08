"""WILSY OS — Business Classification Projection Registry direct certificate.

TITLE: Business Classification Projection Registry Direct Certificate
VERSION: v1.0.1-BUSINESS-CLASSIFICATION-PROJECTION-REGISTRY-TEST
AUTHORITY: Wilsy OS Core Governance
PURPOSE:
    Certify the immutable tenant-scoped persistence boundary for
    BusinessClassificationProjection before production implementation exists.

CERTIFICATION BOUNDARY:
- Test-first clean RED.
- Production registry must be absent for the R20-R3 clean-RED gate.
- Snapshot authority is read-only and resolves immutable snapshot ID + digest.
- Classification code is captured classification truth, not hierarchy/category
  authority.
- No hierarchy, correspondence, subscription, entitlement, authorization,
  service-pack, workflow, AI-execution, regulatory-status, or financial authority.
- Insert-only immutable projection history.
- No latest/current authority.
- No invented revision N-1 supersession rule.
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

from tools.eos.saas.domain.business_classification_projection import (
    BusinessActivity,
    BusinessActivityConfirmation,
    BusinessActivityRole,
    BusinessClassificationEvidence,
    BusinessClassificationProjection,
    BusinessClassificationReference,
    BusinessClassificationSourceKind,
)

from tools.eos.saas.business_classification_projection_registry import (
    COLLECTION_NAME,
    VERSION,
    BusinessClassificationProjectionRegistry,
    BusinessClassificationProjectionRegistryError,
)


NOW = datetime(
    2026,
    10,
    8,
    8,
    0,
    tzinfo=timezone.utc,
)

DIGEST_A = hashlib.sha3_512(
    b"business-classification-evidence-a"
).hexdigest()

DIGEST_B = hashlib.sha3_512(
    b"business-classification-evidence-b"
).hexdigest()

TAXONOMY_DIGEST_A = hashlib.sha3_512(
    b"official-taxonomy-snapshot-a"
).hexdigest()

TAXONOMY_DIGEST_B = hashlib.sha3_512(
    b"official-taxonomy-snapshot-b"
).hexdigest()

PROFILE_DIGEST = hashlib.sha3_512(
    b"tenant-profile-source-snapshot"
).hexdigest()

PROFILE_DIGEST_B = hashlib.sha3_512(
    b"tenant-profile-source-snapshot-b"
).hexdigest()


def evidence(
    evidence_id: str = "EVIDENCE-1",
    *,
    source_kind: BusinessClassificationSourceKind
        = BusinessClassificationSourceKind.TENANT_DECLARATION,
    source_reference: str = "tenant-profile:industry",
    source_digest: str = DIGEST_A,
) -> BusinessClassificationEvidence:
    """Build one immutable evidence fixture with no authority side effect."""
    return BusinessClassificationEvidence(
        evidence_id=evidence_id,
        source_kind=source_kind,
        source_reference=source_reference,
        observed_at=NOW,
        source_digest=source_digest,
    )


def classification(
    *,
    scheme_id: str = "ISIC",
    scheme_version: str = "REV5",
    code: str = "TEST-CODE-A",
    title: str = "Synthetic certificate activity",
    jurisdiction: str = "GLOBAL",
    taxonomy_snapshot_id: str = "TAXONOMY-SNAPSHOT-A",
    taxonomy_snapshot_digest: str = TAXONOMY_DIGEST_A,
) -> BusinessClassificationReference:
    """Build one snapshot-bound external-classification reference."""
    return BusinessClassificationReference(
        scheme_id=scheme_id,
        scheme_version=scheme_version,
        code=code,
        title=title,
        jurisdiction=jurisdiction,
        taxonomy_snapshot_id=taxonomy_snapshot_id,
        taxonomy_snapshot_digest=taxonomy_snapshot_digest,
    )


def activity(
    activity_id: str = "ACTIVITY-1",
    *,
    role: BusinessActivityRole = BusinessActivityRole.PRIMARY,
    confirmation:
        BusinessActivityConfirmation
        = BusinessActivityConfirmation.CONFIRMED,
    confidence_basis_points: int = 9500,
    evidence_refs: tuple[str, ...] = ("EVIDENCE-1",),
    classifications: tuple[
        BusinessClassificationReference,
        ...,
    ] | None = None,
) -> BusinessActivity:
    """Build one activity fixture without service-pack or entitlement grants."""
    return BusinessActivity(
        activity_id=activity_id,
        role=role,
        description="Synthetic business activity",
        confirmation=confirmation,
        confidence_basis_points=confidence_basis_points,
        evidence_refs=evidence_refs,
        classifications=(
            classifications
            if classifications is not None
            else (classification(),)
        ),
    )


def projection(
    *,
    tenant_id: str = "tenant-a",
    projection_id: str = "WILSYBUSCLASS-TEST-1",
    revision: int = 1,
    source_profile_digest: str = PROFILE_DIGEST,
    activities: tuple[BusinessActivity, ...] | None = None,
    evidences: tuple[
        BusinessClassificationEvidence,
        ...,
    ] | None = None,
    supersedes_projection_id: str | None = None,
) -> BusinessClassificationProjection:
    """Build one immutable tenant-bound projection fixture."""
    return BusinessClassificationProjection(
        projection_id=projection_id,
        tenant_id=tenant_id,
        revision=revision,
        source_profile_digest=source_profile_digest,
        evidences=(
            evidences
            if evidences is not None
            else (evidence(),)
        ),
        activities=(
            activities
            if activities is not None
            else (activity(),)
        ),
        effective_from=NOW,
        created_at=NOW,
        supersedes_projection_id=supersedes_projection_id,
    )


def snapshot(
    *,
    snapshot_id: str = "TAXONOMY-SNAPSHOT-A",
    snapshot_digest: str = TAXONOMY_DIGEST_A,
    scheme_id: str = "ISIC",
    scheme_version: str = "REV5",
    jurisdiction: str = "GLOBAL",
) -> Any:
    """Build authoritative snapshot read truth required by this registry only."""
    return SimpleNamespace(
        snapshot_id=snapshot_id,
        snapshot_digest=snapshot_digest,
        scheme_id=scheme_id,
        scheme_version=scheme_version,
        jurisdiction=jurisdiction,
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
    """Minimal Mongo-like cursor for read-only history tests."""

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
        key: str,
        direction: int,
    ) -> Cursor:
        assert key == "revision"

        reverse = direction < 0

        def revision_key(
            value: dict[str, Any],
        ) -> int:
            observed = value[
                "revision"
            ]

            assert isinstance(
                observed,
                int,
            )

            assert not isinstance(
                observed,
                bool,
            )

            return observed

        self._values.sort(
            key=revision_key,
            reverse=reverse,
        )

        return self

    def __iter__(self):
        return iter(
            deepcopy(
                self._values
            )
        )


class Collection:
    """Deterministic in-memory persistence seam with Mongo-shaped calls."""

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


class SnapshotRegistry:
    """Read-only snapshot authority seam."""

    def __init__(
        self,
        snapshots: tuple[Any, ...] = (),
    ) -> None:
        self.by_id = {
            value.snapshot_id: value
            for value in snapshots
        }

        self.by_digest = {
            value.snapshot_digest: value
            for value in snapshots
        }

        self.get_calls: list[
            tuple[str, Any]
        ] = []

        self.get_digest_calls: list[
            tuple[str, Any]
        ] = []

        self.create_calls = 0
        self.update_calls = 0
        self.delete_calls = 0

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

        return self.by_id.get(
            snapshot_id
        )

    def get_by_digest(
        self,
        snapshot_digest: str,
        *,
        session: Any = None,
    ) -> Any:
        self.get_digest_calls.append(
            (
                snapshot_digest,
                session,
            )
        )

        return self.by_digest.get(
            snapshot_digest
        )

    def create(
        self,
        *_args: Any,
        **_kwargs: Any,
    ) -> None:
        self.create_calls += 1

        raise AssertionError(
            "SNAPSHOT_DEPENDENCY_WRITE_FORBIDDEN"
        )

    def update(
        self,
        *_args: Any,
        **_kwargs: Any,
    ) -> None:
        self.update_calls += 1

        raise AssertionError(
            "SNAPSHOT_DEPENDENCY_WRITE_FORBIDDEN"
        )

    def delete(
        self,
        *_args: Any,
        **_kwargs: Any,
    ) -> None:
        self.delete_calls += 1

        raise AssertionError(
            "SNAPSHOT_DEPENDENCY_WRITE_FORBIDDEN"
        )


def registry(
    *,
    collection: Collection | None = None,
    snapshots: tuple[Any, ...] | None = None,
) -> tuple[
    BusinessClassificationProjectionRegistry,
    Collection,
    SnapshotRegistry,
]:
    """Build exact prospective registry dependencies."""
    store = (
        collection
        if collection is not None
        else Collection()
    )

    snapshot_values = (
        snapshots
        if snapshots is not None
        else (
            snapshot(),
        )
    )

    snapshot_registry = SnapshotRegistry(
        snapshot_values
    )

    value = BusinessClassificationProjectionRegistry(
        store,
        snapshot_registry=snapshot_registry,
    )

    return (
        value,
        store,
        snapshot_registry,
    )


def persist_direct(
    store: Collection,
    value: BusinessClassificationProjection,
) -> None:
    """Seed durable truth without exercising create authority."""
    store.documents.append(
        deepcopy(
            value.to_dict()
        )
    )


def test_version_and_collection_name_exact() -> None:
    assert (
        VERSION
        == "v1.0.0-WILSY-BUSINESS-CLASSIFICATION-PROJECTION-REGISTRY"
    )

    assert (
        COLLECTION_NAME
        == "business_classification_projections"
    )


def test_public_surface_is_exact() -> None:
    public = {
        name
        for name, member
        in inspect.getmembers(
            BusinessClassificationProjectionRegistry
        )
        if (
            callable(member)
            and not name.startswith("_")
        )
    }

    assert public == {
        "ensure_indexes",
        "create",
        "get",
        "get_by_fingerprint",
        "get_by_tenant_revision",
        "get_by_tenant",
    }


def test_ensure_indexes_exact_and_no_ttl() -> None:
    _value, store, _snapshots = registry()

    BusinessClassificationProjectionRegistry.ensure_indexes(
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

    assert set(observed) == {
        "business_classification_projection_id_unique",
        "business_classification_projection_fingerprint_unique",
        "business_classification_tenant_revision_unique",
        "business_classification_tenant_effective_from",
        "business_classification_tenant_supersedes",
    }

    for name in (
        "business_classification_projection_id_unique",
        "business_classification_projection_fingerprint_unique",
        "business_classification_tenant_revision_unique",
    ):
        assert (
            observed[name][1]["unique"]
            is True
        )

    assert all(
        "expireAfterSeconds"
        not in kwargs
        for _args, kwargs
        in store.index_calls
    )


def test_missing_session_rejected_before_snapshot_or_supersession_read() -> None:
    value, store, snapshots = registry()

    with pytest.raises(
        BusinessClassificationProjectionRegistryError,
        match="ACTIVE_TRANSACTION_REQUIRED",
    ):
        value.create(
            projection(),
            session=None,
        )

    assert snapshots.get_calls == []
    assert snapshots.get_digest_calls == []
    assert store.find_one_calls == []
    assert store.insert_calls == []


def test_inactive_transaction_rejected_before_snapshot_or_supersession_read() -> None:
    value, store, snapshots = registry()

    with pytest.raises(
        BusinessClassificationProjectionRegistryError,
        match="ACTIVE_TRANSACTION_REQUIRED",
    ):
        value.create(
            projection(),
            session=Session(
                in_transaction=False
            ),
        )

    assert snapshots.get_calls == []
    assert snapshots.get_digest_calls == []
    assert store.find_one_calls == []
    assert store.insert_calls == []


def test_create_accepts_only_projection_domain() -> None:
    value, store, snapshots = registry()

    with pytest.raises(
        BusinessClassificationProjectionRegistryError
    ):
        value.create(
            cast(
                Any,
                object(),
            ),
            session=Session(),
        )

    assert snapshots.get_calls == []
    assert snapshots.get_digest_calls == []
    assert store.insert_calls == []


def test_candidate_strict_rehydration_required(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    value, store, _snapshots = registry()

    called = {"count": 0}

    original = (
        BusinessClassificationProjection.from_dict
    )

    def strict(
        cls: type[
            BusinessClassificationProjection
        ],
        payload: Any,
    ) -> BusinessClassificationProjection:
        called["count"] += 1
        return original(payload)

    monkeypatch.setattr(
        BusinessClassificationProjection,
        "from_dict",
        classmethod(strict),
    )

    candidate = projection()

    assert (
        value.create(
            candidate,
            session=Session(),
        )
        == candidate
    )

    assert called["count"] >= 1
    assert len(store.insert_calls) == 1


def test_each_distinct_snapshot_binding_resolved_by_id_and_digest() -> None:
    second_snapshot = snapshot(
        snapshot_id="TAXONOMY-SNAPSHOT-B",
        snapshot_digest=TAXONOMY_DIGEST_B,
        scheme_id="NAICS",
        scheme_version="2022",
        jurisdiction="US",
    )

    second_classification = classification(
        scheme_id="NAICS",
        scheme_version="2022",
        code="541110",
        title="Offices of Lawyers",
        jurisdiction="US",
        taxonomy_snapshot_id="TAXONOMY-SNAPSHOT-B",
        taxonomy_snapshot_digest=TAXONOMY_DIGEST_B,
    )

    candidate = projection(
        activities=(
            activity(
                classifications=(
                    classification(),
                    second_classification,
                ),
            ),
        ),
    )

    value, _store, snapshots = registry(
        snapshots=(
            snapshot(),
            second_snapshot,
        )
    )

    value.create(
        candidate,
        session=Session(),
    )

    assert {
        call[0]
        for call
        in snapshots.get_calls
    } == {
        "TAXONOMY-SNAPSHOT-A",
        "TAXONOMY-SNAPSHOT-B",
    }

    assert {
        call[0]
        for call
        in snapshots.get_digest_calls
    } == {
        TAXONOMY_DIGEST_A,
        TAXONOMY_DIGEST_B,
    }


def test_repeated_snapshot_binding_deduplicates_dependency_reads() -> None:
    candidate = projection(
        activities=(
            activity(
                classifications=(
                    classification(
                        code="A"
                    ),
                    classification(
                        code="B",
                        title="Second code",
                    ),
                ),
            ),
        ),
    )

    value, _store, snapshots = registry()

    value.create(
        candidate,
        session=Session(),
    )

    assert [
        call[0]
        for call
        in snapshots.get_calls
    ] == [
        "TAXONOMY-SNAPSHOT-A"
    ]

    assert [
        call[0]
        for call
        in snapshots.get_digest_calls
    ] == [
        TAXONOMY_DIGEST_A
    ]


def test_missing_snapshot_binding_rejected_before_insert() -> None:
    value, store, _snapshots = registry(
        snapshots=()
    )

    with pytest.raises(
        BusinessClassificationProjectionRegistryError
    ):
        value.create(
            projection(),
            session=Session(),
        )

    assert store.insert_calls == []


def test_snapshot_id_digest_mismatch_rejected_before_insert() -> None:
    by_id = snapshot()

    wrong_digest_target = snapshot(
        snapshot_id="OTHER-SNAPSHOT",
        snapshot_digest=TAXONOMY_DIGEST_A,
    )

    value, store, snapshots = registry(
        snapshots=(
            by_id,
            wrong_digest_target,
        )
    )

    snapshots.by_digest[
        TAXONOMY_DIGEST_A
    ] = wrong_digest_target

    with pytest.raises(
        BusinessClassificationProjectionRegistryError
    ):
        value.create(
            projection(),
            session=Session(),
        )

    assert store.insert_calls == []


def test_snapshot_scheme_mismatch_rejected_before_insert() -> None:
    value, store, _snapshots = registry(
        snapshots=(
            snapshot(
                scheme_id="NAICS"
            ),
        )
    )

    with pytest.raises(
        BusinessClassificationProjectionRegistryError
    ):
        value.create(
            projection(),
            session=Session(),
        )

    assert store.insert_calls == []


def test_snapshot_version_mismatch_rejected_before_insert() -> None:
    value, store, _snapshots = registry(
        snapshots=(
            snapshot(
                scheme_version="REV4"
            ),
        )
    )

    with pytest.raises(
        BusinessClassificationProjectionRegistryError
    ):
        value.create(
            projection(),
            session=Session(),
        )

    assert store.insert_calls == []


def test_snapshot_jurisdiction_mismatch_rejected_before_insert() -> None:
    value, store, _snapshots = registry(
        snapshots=(
            snapshot(
                jurisdiction="ZA"
            ),
        )
    )

    with pytest.raises(
        BusinessClassificationProjectionRegistryError
    ):
        value.create(
            projection(),
            session=Session(),
        )

    assert store.insert_calls == []


def test_registry_does_not_validate_code_through_hierarchy() -> None:
    candidate = projection(
        activities=(
            activity(
                classifications=(
                    classification(
                        code="CAPTURED-CODE-NOT-HIERARCHY-AUTHORITY",
                    ),
                ),
            ),
        ),
    )

    value, store, _snapshots = registry()

    assert (
        value.create(
            candidate,
            session=Session(),
        )
        == candidate
    )

    assert len(store.insert_calls) == 1


def test_revision_one_requires_no_supersession_lookup() -> None:
    value, store, _snapshots = registry()

    candidate = projection()

    value.create(
        candidate,
        session=Session(),
    )

    assert candidate.supersedes_projection_id is None

    assert not any(
        (
            query.get(
                "projection_id"
            )
            not in (
                None,
                candidate.projection_id,
            )
        )
        for query, _session
        in store.find_one_calls
    )


def test_later_revision_requires_existing_superseded_projection() -> None:
    prior = projection(
        projection_id="PROJECTION-PRIOR",
        revision=1,
    )

    candidate = projection(
        projection_id="PROJECTION-NEXT",
        revision=2,
        supersedes_projection_id=prior.projection_id,
    )

    value, store, _snapshots = registry()

    persist_direct(
        store,
        prior,
    )

    assert (
        value.create(
            candidate,
            session=Session(),
        )
        == candidate
    )


def test_cross_tenant_supersession_rejected() -> None:
    prior = projection(
        tenant_id="tenant-b",
        projection_id="PROJECTION-OTHER-TENANT",
        revision=1,
    )

    candidate = projection(
        tenant_id="tenant-a",
        projection_id="PROJECTION-NEXT",
        revision=2,
        supersedes_projection_id=prior.projection_id,
    )

    value, store, _snapshots = registry()

    persist_direct(
        store,
        prior,
    )

    with pytest.raises(
        BusinessClassificationProjectionRegistryError
    ):
        value.create(
            candidate,
            session=Session(),
        )

    assert store.insert_calls == []


def test_corrupt_superseded_projection_rejected() -> None:
    prior = projection(
        projection_id="PROJECTION-PRIOR",
        revision=1,
    ).to_dict()

    prior["fingerprint"] = "0" * 128

    candidate = projection(
        projection_id="PROJECTION-NEXT",
        revision=2,
        supersedes_projection_id="PROJECTION-PRIOR",
    )

    value, store, _snapshots = registry()

    store.documents.append(
        deepcopy(prior)
    )

    with pytest.raises(
        BusinessClassificationProjectionRegistryError
    ):
        value.create(
            candidate,
            session=Session(),
        )

    assert store.insert_calls == []


def test_registry_does_not_invent_n_minus_one_rule() -> None:
    prior = projection(
        projection_id="PROJECTION-REVISION-2",
        revision=2,
        supersedes_projection_id="PROJECTION-REVISION-1",
    )

    candidate = projection(
        projection_id="PROJECTION-REVISION-7",
        revision=7,
        supersedes_projection_id=prior.projection_id,
    )

    value, store, _snapshots = registry()

    persist_direct(
        store,
        prior,
    )

    assert (
        value.create(
            candidate,
            session=Session(),
        )
        == candidate
    )


def test_create_persists_exact_domain_serialization() -> None:
    value, store, _snapshots = registry()

    candidate = projection()

    value.create(
        candidate,
        session=Session(),
    )

    assert store.documents == [
        candidate.to_dict()
    ]


def test_exact_replay_returns_identical_durable_projection() -> None:
    value, store, _snapshots = registry()

    candidate = projection()

    persist_direct(
        store,
        candidate,
    )

    before = len(store.documents)

    observed = value.create(
        candidate,
        session=Session(),
    )

    assert observed == candidate
    assert len(store.documents) == before
    assert store.insert_calls == []


def test_projection_id_conflict_rejected_before_insert() -> None:
    durable = projection()

    conflicting = projection(
        source_profile_digest=PROFILE_DIGEST_B,
    )

    value, store, _snapshots = registry()

    persist_direct(
        store,
        durable,
    )

    with pytest.raises(
        BusinessClassificationProjectionRegistryError
    ):
        value.create(
            conflicting,
            session=Session(),
        )

    assert store.insert_calls == []


def test_fingerprint_conflict_rejected_before_insert() -> None:
    candidate = projection(
        projection_id="PROJECTION-CANDIDATE"
    )

    collision = projection(
        projection_id="PROJECTION-DURABLE",
        source_profile_digest=PROFILE_DIGEST_B,
    ).to_dict()

    collision["fingerprint"] = candidate.fingerprint

    value, store, _snapshots = registry()

    store.documents.append(
        collision
    )

    with pytest.raises(
        BusinessClassificationProjectionRegistryError
    ):
        value.create(
            candidate,
            session=Session(),
        )

    assert store.insert_calls == []


def test_tenant_revision_conflict_rejected_before_insert() -> None:
    durable = projection(
        projection_id="PROJECTION-A",
    )

    candidate = projection(
        projection_id="PROJECTION-B",
        source_profile_digest=PROFILE_DIGEST_B,
    )

    value, store, _snapshots = registry()

    persist_direct(
        store,
        durable,
    )

    with pytest.raises(
        BusinessClassificationProjectionRegistryError
    ):
        value.create(
            candidate,
            session=Session(),
        )

    assert store.insert_calls == []


def test_duplicate_race_fails_closed_without_post_error_read() -> None:
    value, store, _snapshots = registry()

    store.raise_duplicate_on_insert = True

    candidate = projection()

    with pytest.raises(
        BusinessClassificationProjectionRegistryError
    ):
        value.create(
            candidate,
            session=Session(),
        )

    assert len(store.insert_calls) == 1


def test_get_strictly_hydrates_projection() -> None:
    value, store, _snapshots = registry()

    candidate = projection()

    persist_direct(
        store,
        candidate,
    )

    assert (
        value.get(
            candidate.projection_id
        )
        == candidate
    )


def test_get_by_fingerprint_strictly_hydrates_projection() -> None:
    value, store, _snapshots = registry()

    candidate = projection()

    persist_direct(
        store,
        candidate,
    )

    assert (
        value.get_by_fingerprint(
            candidate.fingerprint
        )
        == candidate
    )


def test_get_by_tenant_revision_returns_exact_projection() -> None:
    candidate = projection(
        revision=4,
        projection_id="PROJECTION-4",
        supersedes_projection_id="PROJECTION-1",
    )

    value, store, _snapshots = registry()

    persist_direct(
        store,
        candidate,
    )

    assert (
        value.get_by_tenant_revision(
            "tenant-a",
            4,
        )
        == candidate
    )


def test_get_by_tenant_returns_revision_ordered_history() -> None:
    first = projection(
        projection_id="PROJECTION-1",
        revision=1,
    )

    second = projection(
        projection_id="PROJECTION-2",
        revision=2,
        supersedes_projection_id=first.projection_id,
    )

    third = projection(
        projection_id="PROJECTION-5",
        revision=5,
        supersedes_projection_id=second.projection_id,
    )

    value, store, _snapshots = registry()

    for candidate in (
        third,
        first,
        second,
    ):
        persist_direct(
            store,
            candidate,
        )

    assert value.get_by_tenant(
        "tenant-a"
    ) == (
        first,
        second,
        third,
    )


def test_corrupt_persisted_projection_rejected() -> None:
    value, store, _snapshots = registry()

    document = projection().to_dict()

    document["fingerprint"] = "f" * 128

    store.documents.append(
        document
    )

    with pytest.raises(
        BusinessClassificationProjectionRegistryError
    ):
        value.get(
            "WILSYBUSCLASS-TEST-1"
        )


def test_registry_is_insert_only() -> None:
    source = inspect.getsource(
        BusinessClassificationProjectionRegistry
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
            BusinessClassificationProjectionRegistry,
            forbidden,
        )


def test_snapshot_dependency_is_read_only() -> None:
    value, _store, snapshots = registry()

    value.create(
        projection(),
        session=Session(),
    )

    assert snapshots.create_calls == 0
    assert snapshots.update_calls == 0
    assert snapshots.delete_calls == 0


def test_registry_contains_no_commercial_authorization_activation_or_financial_authority() -> None:
    public = {
        name
        for name, member
        in inspect.getmembers(
            BusinessClassificationProjectionRegistry
        )
        if (
            callable(member)
            and not name.startswith("_")
        )
    }

    assert not (
        public
        & {
            "subscribe",
            "grant_entitlement",
            "authorize",
            "assign_role",
            "activate",
            "activate_service_pack",
            "execute_payment",
            "settle",
            "invoice",
            "classify",
        }
    )


# ARTIFACT: test_business_classification_projection_registry.py
