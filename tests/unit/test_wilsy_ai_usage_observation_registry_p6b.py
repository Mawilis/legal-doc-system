"""Direct certificate for M13-P6B bounded P5B retrieval.

TITLE: WILSY AI Usage Observation P6B Retrieval Direct Certificate
VERSION: v1.1.0-M13-P6B
AUTHORITY: Wilsy OS Core Governance
EPITOME: Prove exhaustive caller-snapshot retrieval for P6A without moving
         aggregation, quota, commercial, or financial authority into P5B.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tests/unit/test_wilsy_ai_usage_observation_registry_p6b.py
COLLABORATION / OWNERSHIP: Direct certificate for the P6B registry seam;
                            P6A remains the sole capacity derivation owner.
CERTIFICATION / UPDATE DATE: 2026-09-13
CHANGELOG: v1.0.0-M13-P6B certifies bounded inclusion/exclusion, strict
           hydration, binding, ordering, outage handling, and transaction
           ownership.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2.
"""
from datetime import datetime, timezone
from typing import Any

import pytest
from pymongo.errors import PyMongoError

import tools.eos.saas.billing.wilsy_ai_usage_observation_registry as registry_module
from tools.eos.saas.billing.wilsy_ai_usage_capacity import derive_wilsy_ai_usage_capacity
from tools.eos.saas.billing.wilsy_ai_commercial_policy import WilsyAITier, get_wilsy_ai_commercial_policy
from tools.eos.saas.billing.wilsy_ai_usage_observation_registry import (
    WilsyAIUsageObservationRegistry,
    WilsyAIUsageObservationRegistryError,
    ensure_indexes,
)
from tools.eos.saas.domain.wilsy_ai_usage_window import WilsyAIUsageWindowEvidence
from tools.eos.saas.domain.wilsy_ai_entitlement import WilsyAIEntitlement, WilsyAIEntitlementState
from tools.eos.saas.domain.wilsy_ai_usage_observation import WilsyAIUsageObservation


FP = "a" * 128
AS_OF = datetime(2026, 9, 12, 12, tzinfo=timezone.utc)


class Session:
    def __init__(self, active: bool = True) -> None:
        self.in_transaction = active
        self.commits = 0
        self.aborts = 0

    def commit_transaction(self) -> None:
        self.commits += 1

    def abort_transaction(self) -> None:
        self.aborts += 1


class Cursor:
    def __init__(self, rows: list[dict[str, object]], failure: bool = False) -> None:
        self.rows = rows
        self.failure = failure

    def __iter__(self) -> "Cursor":
        if self.failure:
            raise PyMongoError("cursor iteration offline")
        return self

    def __next__(self) -> dict[str, object]:
        if not self.rows:
            raise StopIteration
        return self.rows.pop(0)


class Collection:
    def __init__(self) -> None:
        self.rows: list[dict[str, object]] = []
        self.indexes: list[tuple[Any, dict[str, object]]] = []
        self.find_failure = False
        self.cursor_failure = False

    def with_options(self, **_: object) -> "Collection":
        return self

    def create_index(self, keys: Any, **kwargs: object) -> str:
        self.indexes.append((keys, kwargs))
        return str(kwargs["name"])

    def find(self, query: dict[str, object], *, session: Session) -> Cursor:
        assert session.in_transaction is True
        if self.find_failure:
            raise PyMongoError("find offline")
        rows = [row.copy() for row in self.rows if all(row.get(key) == value for key, value in query.items())]
        return Cursor(rows, self.cursor_failure)


def entitlement() -> WilsyAIEntitlement:
    policy = get_wilsy_ai_commercial_policy(WilsyAITier.STARTER)
    pending = WilsyAIEntitlement(
        tenant_id="tenant-a", entitlement_id="ent-a", module_id="module-a", module_name="Inbox",
        tier=WilsyAITier.STARTER, policy_fingerprint=policy.policy_fingerprint,
        lifecycle_state=WilsyAIEntitlementState.PENDING_SOURCE, source_requirements=("records",),
        capability_grants=("ai.summary",), source_readiness_evidence_reference="ready",
        source_readiness_evidence_fingerprint=FP,
    )
    return pending.transition(WilsyAIEntitlementState.ACTIVE, expected_revision=0,
                              evidence_reference="active", evidence_fingerprint=FP,
                              occurred_at=datetime(2026, 9, 1, tzinfo=timezone.utc))


def observation(ent: WilsyAIEntitlement, *, ident: str, when: datetime, tenant: str | None = None,
                module: str | None = None, revision: int | None = None,
                entitlement_fp: str | None = None) -> WilsyAIUsageObservation:
    return WilsyAIUsageObservation(
        tenant or ent.tenant_id, ident, ent.entitlement_id, ent.lifecycle_revision if revision is None else revision,
        ent.fingerprint if entitlement_fp is None else entitlement_fp, module or ent.module_id,
        1, 10, 20, 1, when, f"src-{ident}", FP,
    )


def row(item: WilsyAIUsageObservation, key: str) -> dict[str, object]:
    document = item.to_dict()
    document.update(idempotency_key=key, command_fingerprint=registry_module._command_fingerprint(item, key))
    return document


def test_bounded_inclusion_exclusion_order_and_p6a_composition() -> None:
    ent = entitlement(); collection = Collection(); ensure_indexes(collection)
    collection.rows.extend([
        row(observation(ent, ident="late", when=datetime(2026, 9, 12, 11, tzinfo=timezone.utc)), "late"),
        row(observation(ent, ident="early", when=datetime(2026, 9, 1, tzinfo=timezone.utc)), "early"),
        row(observation(ent, ident="prior", when=datetime(2026, 8, 31, 23, tzinfo=timezone.utc)), "prior"),
        row(observation(ent, ident="future", when=datetime(2026, 9, 12, 13, tzinfo=timezone.utc)), "future"),
        row(observation(ent, ident="other-tenant", when=datetime(2026, 9, 5, tzinfo=timezone.utc), tenant="tenant-b"), "other-tenant"),
        row(observation(ent, ident="other-module", when=datetime(2026, 9, 5, tzinfo=timezone.utc), module="module-b"), "other-module"),
    ])
    registry = WilsyAIUsageObservationRegistry(collection); session = Session()
    bounded = registry.get_bounded_for_p6a(tenant_id=ent.tenant_id, entitlement_id=ent.entitlement_id,
        module_id=ent.module_id, expected_entitlement_revision=ent.lifecycle_revision,
        expected_entitlement_fingerprint=ent.fingerprint, as_of=AS_OF, session=session)
    assert [item.usage_observation_id for item in bounded] == ["early", "late"]
    complete = WilsyAIUsageWindowEvidence(
        tenant_id=ent.tenant_id, entitlement_id=ent.entitlement_id, module_id=ent.module_id,
        entitlement_revision=ent.lifecycle_revision, entitlement_fingerprint=ent.fingerprint,
        as_of=AS_OF, window_start=datetime(2026, 9, 1, tzinfo=timezone.utc), window_end=AS_OF,
        observation_count=len(bounded), observation_fingerprints=tuple(item.fingerprint for item in bounded),
        observations=bounded,
    )
    capacity = derive_wilsy_ai_usage_capacity(entitlement=ent, usage_window=complete, as_of=AS_OF)
    assert capacity.daily_consumed_request_units == 1 and capacity.monthly_consumed_automation_actions == 2
    assert session.commits == 0 and session.aborts == 0 and session.in_transaction is True
    assert len(collection.indexes) == 4 and any("entitlement_id" in dict(keys) and "module_id" in dict(keys) for keys, _ in collection.indexes)


def test_empty_window_returns_empty_tuple_not_zero_claim() -> None:
    ent = entitlement(); collection = Collection()
    collection.rows.append(row(observation(ent, ident="prior", when=datetime(2026, 8, 31, tzinfo=timezone.utc)), "prior"))
    result = WilsyAIUsageObservationRegistry(collection).get_bounded_for_p6a(
        tenant_id=ent.tenant_id, entitlement_id=ent.entitlement_id, module_id=ent.module_id,
        expected_entitlement_revision=ent.lifecycle_revision, expected_entitlement_fingerprint=ent.fingerprint,
        as_of=AS_OF, session=Session())
    assert result == ()


def test_complete_window_empty_result_is_authoritative_zero_window() -> None:
    ent = entitlement(); collection = Collection(); registry = WilsyAIUsageObservationRegistry(collection); session = Session()
    value = registry.get_complete_window_for_p6a(
        tenant_id=ent.tenant_id, entitlement_id=ent.entitlement_id, module_id=ent.module_id,
        expected_entitlement_revision=ent.lifecycle_revision,
        expected_entitlement_fingerprint=ent.fingerprint, as_of=AS_OF, session=session,
    )
    assert isinstance(value, WilsyAIUsageWindowEvidence)
    assert value.observation_count == 0 and value.observations == () and value.observation_fingerprints == ()
    assert session.in_transaction is True and session.commits == 0 and session.aborts == 0


def test_complete_window_contains_exact_sorted_observations() -> None:
    ent = entitlement(); collection = Collection(); registry = WilsyAIUsageObservationRegistry(collection)
    early = observation(ent, ident="early", when=datetime(2026, 9, 1, tzinfo=timezone.utc)); late = observation(ent, ident="late", when=AS_OF)
    collection.rows.extend([row(late, "late"), row(early, "early")])
    value = registry.get_complete_window_for_p6a(
        tenant_id=ent.tenant_id, entitlement_id=ent.entitlement_id, module_id=ent.module_id,
        expected_entitlement_revision=ent.lifecycle_revision,
        expected_entitlement_fingerprint=ent.fingerprint, as_of=AS_OF, session=Session(),
    )
    assert [item.usage_observation_id for item in value.observations] == ["early", "late"]
    assert value.observation_fingerprints == tuple(item.fingerprint for item in value.observations)


def test_transaction_required_and_input_validation() -> None:
    ent = entitlement(); registry = WilsyAIUsageObservationRegistry(Collection())
    with pytest.raises(WilsyAIUsageObservationRegistryError, match="M13P6B_TRANSACTION_REQUIRED"):
        registry.get_bounded_for_p6a(tenant_id=ent.tenant_id, entitlement_id=ent.entitlement_id, module_id=ent.module_id,
            expected_entitlement_revision=1, expected_entitlement_fingerprint=ent.fingerprint, as_of=AS_OF, session=Session(False))
    with pytest.raises(WilsyAIUsageObservationRegistryError, match="M13P6B_INPUT_INVALID"):
        registry.get_bounded_for_p6a(tenant_id=ent.tenant_id, entitlement_id=ent.entitlement_id, module_id=ent.module_id,
            expected_entitlement_revision=1, expected_entitlement_fingerprint="B" * 128, as_of=AS_OF, session=Session())


def test_binding_conflict_corruption_timestamp_and_duplicates_fail_closed() -> None:
    ent = entitlement(); registry = WilsyAIUsageObservationRegistry(Collection())
    conflict = Collection(); conflict.rows.append(row(observation(ent, ident="conflict", when=AS_OF, revision=2, entitlement_fp="b" * 128), "conflict"))
    with pytest.raises(WilsyAIUsageObservationRegistryError, match="M13P6B_BINDING_CONFLICT"):
        WilsyAIUsageObservationRegistry(conflict).get_bounded_for_p6a(tenant_id=ent.tenant_id, entitlement_id=ent.entitlement_id, module_id=ent.module_id, expected_entitlement_revision=1, expected_entitlement_fingerprint=ent.fingerprint, as_of=AS_OF, session=Session())
    corrupt = Collection(); corrupt.rows.append(row(observation(ent, ident="corrupt", when=AS_OF), "corrupt")); corrupt.rows[0]["source_evidence_reference"] = "changed"
    with pytest.raises(WilsyAIUsageObservationRegistryError, match="M13P5B_CORRUPT_OBSERVATION"):
        WilsyAIUsageObservationRegistry(corrupt).get_bounded_for_p6a(tenant_id=ent.tenant_id, entitlement_id=ent.entitlement_id, module_id=ent.module_id, expected_entitlement_revision=1, expected_entitlement_fingerprint=ent.fingerprint, as_of=AS_OF, session=Session())
    malformed = Collection(); malformed.rows.append(row(observation(ent, ident="time", when=AS_OF), "time")); malformed.rows[0]["occurred_at"] = "not-a-timestamp"
    with pytest.raises(WilsyAIUsageObservationRegistryError, match="M13P5B_CORRUPT_OBSERVATION"):
        WilsyAIUsageObservationRegistry(malformed).get_bounded_for_p6a(tenant_id=ent.tenant_id, entitlement_id=ent.entitlement_id, module_id=ent.module_id, expected_entitlement_revision=1, expected_entitlement_fingerprint=ent.fingerprint, as_of=AS_OF, session=Session())
    duplicates = Collection(); duplicate = row(observation(ent, ident="dup", when=AS_OF), "dup"); duplicates.rows.extend([duplicate, duplicate.copy()])
    with pytest.raises(WilsyAIUsageObservationRegistryError, match="M13P6B_DUPLICATE_EVIDENCE"):
        WilsyAIUsageObservationRegistry(duplicates).get_bounded_for_p6a(tenant_id=ent.tenant_id, entitlement_id=ent.entitlement_id, module_id=ent.module_id, expected_entitlement_revision=1, expected_entitlement_fingerprint=ent.fingerprint, as_of=AS_OF, session=Session())


@pytest.mark.parametrize("failure", ["find", "cursor"])
def test_find_and_cursor_iteration_failures_are_governed(failure: str) -> None:
    ent = entitlement(); collection = Collection(); collection.rows.append(row(observation(ent, ident="one", when=AS_OF), "one"))
    if failure == "find": collection.find_failure = True
    else: collection.cursor_failure = True
    with pytest.raises(WilsyAIUsageObservationRegistryError, match="M13P6B_PERSISTENCE_UNAVAILABLE"):
        WilsyAIUsageObservationRegistry(collection).get_bounded_for_p6a(tenant_id=ent.tenant_id, entitlement_id=ent.entitlement_id, module_id=ent.module_id, expected_entitlement_revision=1, expected_entitlement_fingerprint=ent.fingerprint, as_of=AS_OF, session=Session())


def test_no_quota_or_financial_authority_surface() -> None:
    names = set(dir(WilsyAIUsageObservationRegistry))
    assert not names.intersection({"aggregate", "sum_usage", "calculate_quota", "invoice", "payment", "execute", "settle"})


# ARTIFACT: test_wilsy_ai_usage_observation_registry_p6b.py
# VERSION: v1.1.0-M13-P6B
# AUTHORITY BOUNDARY: bounded raw observation retrieval only
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively
# END OF WILSY OS SOVEREIGN ARTIFACT
