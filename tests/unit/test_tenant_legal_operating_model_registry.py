"""Direct certificate for the durable Tenant Legal Operating Model registry.

TITLE: Tenant Legal Operating Model Registry Direct Certificate
VERSION: v1.0.0-CX26-R2-DURABLE-REGISTRY-CERT
AUTHORITY: Direct proof of immutable tenant-scoped persistence/currentness semantics.
EPITOME: Certify transaction ownership, indexes, replay, corruption rejection,
         tenant isolation, deterministic history, and lineage-derived currentness.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tests/unit/test_tenant_legal_operating_model_registry.py
COLLABORATION / OWNERSHIP: Exercises only G7B domain and CX26 R2 registry contracts.
CERTIFICATION / UPDATE DATE: 2026-10-13
CHANGELOG: v1.0.0-CX26-R2 establishes the direct fake-transport certificate.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2.
TENANT BOUNDARY: Synthetic exact-tenant values only; no customer data.
AUTHORITY BOUNDARY: Configuration persistence proof only; no IAM or command authority.
FINANCIAL AUTHORITY BOUNDARY: None; Kennel EOS remains exclusive.
FAIL-CLOSED DECLARATION: Invalid transaction, replay, collision, corruption,
                         ambiguity, and supersession inconsistency must reject.
"""
from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Any, Mapping, cast

import pytest
from pymongo.errors import DuplicateKeyError, OperationFailure

from tools.eos.legal_operations.domain.legal_operating_catalogue import CATALOGUE_FINGERPRINT
from tools.eos.legal_operations.domain.tenant_legal_operating_model import TenantLegalOperatingModel
from tools.eos.legal_operations.registry.tenant_legal_operating_model_registry import (
    COLLECTION_NAME,
    CURRENTNESS_INDEX_NAME,
    FINGERPRINT_INDEX_NAME,
    IDENTITY_INDEX_NAME,
    SUPERSESSION_INDEX_NAME,
    TENANT_HISTORY_INDEX_NAME,
    VERSION,
    TenantLegalOperatingModelRegistry,
    TenantLegalOperatingModelRegistryConflictError,
    TenantLegalOperatingModelRegistryNotFoundError,
    TenantLegalOperatingModelRegistryPersistedRecordInvalidError,
    TenantLegalOperatingModelRegistryPersistenceError,
    TenantLegalOperatingModelRegistryTransactionRequiredError,
)

BASE = datetime(2026, 10, 13, 8, 30, 0, 654321, tzinfo=timezone.utc)
TENANT = "tenant-cx26-r2"


def model(
    identity: str = "operating-model-1",
    *,
    tenant: str = TENANT,
    revision: int = 1,
    effective_from: datetime = BASE,
    supersedes: str | None = None,
    items: tuple[str, ...] = ("PERSONA_PARTNER", "PRACTICE_DISPUTES"),
) -> TenantLegalOperatingModel:
    """Build one strict canonical synthetic model."""
    return TenantLegalOperatingModel(
        tenant_id=tenant,
        operating_model_id=identity,
        revision=revision,
        activated_item_ids=items,
        effective_from=effective_from,
        supersedes_operating_model_id=supersedes,
    )


class Session:
    """Minimal caller-owned transaction signal for direct tests."""

    def __init__(self, active: bool = True) -> None:
        self.in_transaction = active


class Cursor:
    """Deterministic fake cursor supporting PyMongo-style compound sort."""

    def __init__(self, rows: Any) -> None:
        self._rows = list(rows)

    def sort(self, keys: list[tuple[str, int]]) -> "Cursor":
        for key, direction in reversed(keys):
            self._rows.sort(key=lambda row: (row.get(key) is None, row.get(key)), reverse=direction < 0)
        return self

    def __iter__(self) -> Any:
        return iter(self._rows)


class Collection:
    """In-memory transport preserving production method/session shapes."""

    def __init__(self) -> None:
        self.rows: list[dict[str, object]] = []
        self.indexes: list[tuple[list[tuple[str, int]], dict[str, object]]] = []
        self.inserts = 0
        self.sessions: list[object] = []

    def create_index(self, keys: list[tuple[str, int]], **kwargs: object) -> str:
        self.indexes.append((keys, dict(kwargs)))
        return str(kwargs["name"])

    def find_one(self, query: Mapping[str, object], *, session: object) -> dict[str, object] | None:
        self.sessions.append(session)
        for row in self.rows:
            if all(row.get(key) == value for key, value in query.items()):
                return dict(row)
        return None

    def find(self, query: Mapping[str, object], *, session: object) -> Cursor:
        self.sessions.append(session)
        return Cursor(dict(row) for row in self.rows if all(row.get(key) == value for key, value in query.items()))

    def insert_one(self, document: Mapping[str, object], *, session: object) -> object:
        self.sessions.append(session)
        for row in self.rows:
            same_identity = row.get("tenant_id") == document.get("tenant_id") and row.get("operating_model_id") == document.get("operating_model_id")
            same_fingerprint = row.get("tenant_id") == document.get("tenant_id") and row.get("fingerprint") == document.get("fingerprint")
            if same_identity or same_fingerprint:
                raise DuplicateKeyError("duplicate")
        self.inserts += 1
        self.rows.append({"_id": f"mongo-{self.inserts}", **dict(document)})
        return object()


def registry() -> tuple[TenantLegalOperatingModelRegistry, Collection, Session]:
    """Create one isolated direct registry fixture."""
    collection = Collection()
    session = Session()
    return TenantLegalOperatingModelRegistry(collection), collection, session


def test_exact_version_collection_and_indexes_have_no_ttl() -> None:
    assert VERSION == "v1.0.0-CX26-R2-DURABLE-TENANT-LEGAL-OPERATING-MODEL-REGISTRY"
    assert COLLECTION_NAME == "legal_tenant_operating_models"
    target, collection, _session = registry()
    target.ensure_indexes()
    by_name = {cast(str, options["name"]): (keys, options) for keys, options in collection.indexes}
    assert set(by_name) == {IDENTITY_INDEX_NAME, FINGERPRINT_INDEX_NAME, TENANT_HISTORY_INDEX_NAME, CURRENTNESS_INDEX_NAME, SUPERSESSION_INDEX_NAME}
    assert by_name[IDENTITY_INDEX_NAME][1]["unique"] is True
    assert by_name[FINGERPRINT_INDEX_NAME][1]["unique"] is True
    assert by_name[TENANT_HISTORY_INDEX_NAME][1]["unique"] is False
    assert by_name[CURRENTNESS_INDEX_NAME][1]["unique"] is False
    assert all(keys[0] == ("tenant_id", 1) for keys, _options in by_name.values())
    assert all("expireAfterSeconds" not in options for _keys, options in by_name.values())


@pytest.mark.parametrize("session", [None, Session(False)])
def test_active_transaction_is_required_for_write(session: object) -> None:
    target, _collection, _active = registry()
    with pytest.raises(TenantLegalOperatingModelRegistryTransactionRequiredError):
        target.create_or_replay(model(), session=session)


def test_insert_and_exact_replay_produce_one_immutable_row() -> None:
    target, collection, session = registry()
    value = model()
    assert target.create_or_replay(value, session=session) == value
    assert target.create_or_replay(value, session=session) == value
    assert collection.inserts == 1 and len(collection.rows) == 1


def test_divergent_same_identity_replay_rejects() -> None:
    target, _collection, session = registry()
    target.create_or_replay(model(), session=session)
    with pytest.raises(TenantLegalOperatingModelRegistryConflictError, match="DIVERGENT_REPLAY"):
        target.create_or_replay(model(items=("RISK_CONFLICTS",)), session=session)


def test_exact_tenant_isolation_and_cross_tenant_same_identity() -> None:
    target, collection, session = registry()
    own = model()
    foreign = model(tenant="tenant-cx26-foreign")
    target.create_or_replay(own, session=session)
    target.create_or_replay(foreign, session=session)
    assert len(collection.rows) == 2
    assert target.get_by_id(TENANT, own.operating_model_id, session=session) == own
    with pytest.raises(TenantLegalOperatingModelRegistryNotFoundError):
        target.get_by_id("tenant-absent", own.operating_model_id, session=session)


def test_fingerprint_collision_for_different_identity_rejects() -> None:
    target, collection, session = registry()
    value = model()
    collision = value.to_dict()
    collision["operating_model_id"] = "collision-id"
    collection.rows.append({"_id": "collision", **collision})
    with pytest.raises(TenantLegalOperatingModelRegistryConflictError, match="FINGERPRINT_COLLISION"):
        target.create_or_replay(value, session=session)


@pytest.mark.parametrize("mutation", ["extra", "fingerprint", "catalogue"])
def test_strict_hydration_rejects_unknown_and_corrupt_rows(mutation: str) -> None:
    target, collection, session = registry()
    row = model().to_dict()
    if mutation == "extra":
        row["unexpected"] = True
    elif mutation == "fingerprint":
        row["fingerprint"] = "f" * 128
    else:
        row["catalogue_fingerprint"] = "a" * 128 if CATALOGUE_FINGERPRINT != "a" * 128 else "b" * 128
    collection.rows.append({"_id": "corrupt", **row})
    with pytest.raises(TenantLegalOperatingModelRegistryPersistedRecordInvalidError):
        target.get_by_id(TENANT, "operating-model-1", session=session)


def test_tenant_history_is_deterministic_and_preserves_microseconds() -> None:
    target, _collection, session = registry()
    third = model("operating-model-3", revision=3, effective_from=BASE + timedelta(days=2), supersedes="operating-model-2")
    first = model()
    second = model("operating-model-2", revision=2, effective_from=BASE + timedelta(days=1), supersedes="operating-model-1")
    for value in (third, first, second):
        target.create_or_replay(value, session=session)
    history = target.list_tenant_history(TENANT, session=session)
    assert history == (first, second, third)
    assert history[0].effective_from.microsecond == 654321


def test_currentness_boundary_and_future_exclusion() -> None:
    target, _collection, session = registry()
    first = model()
    second_time = BASE + timedelta(days=1, microseconds=1)
    second = model("operating-model-2", revision=2, effective_from=second_time, supersedes=first.operating_model_id)
    target.create_or_replay(first, session=session)
    target.create_or_replay(second, session=session)
    with pytest.raises(TenantLegalOperatingModelRegistryNotFoundError):
        target.resolve_current(TENANT, BASE - timedelta(microseconds=1), session=session)
    assert target.resolve_current(TENANT, BASE, session=session) == first
    assert target.resolve_current(TENANT, second_time - timedelta(microseconds=1), session=session) == first
    assert target.resolve_current(TENANT, second_time, session=session) == second
    assert target.resolve_current(TENANT, second_time + timedelta(days=1), session=session) == second


@pytest.mark.parametrize(
    "history",
    [
        (model("operating-model-2", revision=2, supersedes=None),),
        (model(), model("operating-model-2", revision=2, effective_from=BASE + timedelta(days=1), supersedes="wrong")),
        (model(), model("operating-model-2", revision=2, effective_from=BASE, supersedes="operating-model-1")),
    ],
)
def test_supersession_inconsistency_rejects(history: tuple[TenantLegalOperatingModel, ...]) -> None:
    target, _collection, session = registry()
    for value in history:
        target.create_or_replay(value, session=session)
    with pytest.raises(TenantLegalOperatingModelRegistryConflictError):
        target.resolve_current(TENANT, BASE + timedelta(days=3), session=session)


def test_ambiguous_duplicate_revision_rejects() -> None:
    target, collection, session = registry()
    first = model()
    left = model("operating-model-2a", revision=2, effective_from=BASE + timedelta(days=1), supersedes=first.operating_model_id)
    right = model("operating-model-2b", revision=2, effective_from=BASE + timedelta(days=2), supersedes=first.operating_model_id)
    collection.rows.extend([first.to_dict(), left.to_dict(), right.to_dict()])
    with pytest.raises(TenantLegalOperatingModelRegistryConflictError, match="AMBIGUOUS_OR_GAPPED_HISTORY"):
        target.resolve_current(TENANT, BASE + timedelta(days=3), session=session)


def test_registry_exposes_no_mutation_delete_or_authority_surface() -> None:
    forbidden_methods = {"update", "replace", "delete", "set_current", "grant", "authorize", "assign"}
    assert not any(hasattr(TenantLegalOperatingModelRegistry, name) for name in forbidden_methods)
    forbidden_fields = {"principal_id", "role_id", "business_role", "permission", "authorization", "subscription_id", "entitlement_id", "payment", "settlement"}
    assert not forbidden_fields.intersection(model().to_dict())


def test_pymongo_failure_is_translated_fail_closed() -> None:
    class BrokenCollection(Collection):
        def find_one(self, query: Mapping[str, object], *, session: object) -> None:
            raise OperationFailure("synthetic outage")

    target = TenantLegalOperatingModelRegistry(BrokenCollection())
    with pytest.raises(TenantLegalOperatingModelRegistryPersistenceError):
        target.get_by_id(TENANT, "operating-model-1", session=Session())


# ARTIFACT: test_tenant_legal_operating_model_registry.py
# VERSION: v1.0.0-CX26-R2-DURABLE-REGISTRY-CERT
# AUTHORITY BOUNDARY: direct immutable persistence/currentness proof only
# TENANT POSTURE: exact synthetic tenant isolation
# FAIL-CLOSED POSTURE: transaction, corruption, divergence, collision, ambiguity, and outage reject
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively
# END OF WILSY OS SOVEREIGN CERTIFICATE
