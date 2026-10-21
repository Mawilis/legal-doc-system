"""P9-R105-P4G-P5-R1 denial-safe ethical-wall read barrier."""
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any
import runpy

import pytest

from tools.eos.legal_operations.service import (
    legal_practitioner_ethical_wall_read_barrier as barrier,
)

ROOT = Path(__file__).resolve().parents[2]
MAKE = runpy.run_path(
    str(ROOT / "tests/unit/test_legal_practitioner_ethical_wall_restriction.py")
)["make"]
REGISTRY = runpy.run_path(
    str(ROOT / "tests/unit/test_legal_practitioner_ethical_wall_restriction_registry.py")
)
Collection = REGISTRY["Collection"]
Session = REGISTRY["Session"]
AT = datetime(2026, 10, 19, 12, tzinfo=timezone.utc)


def inspect(*items: Any, **changes: Any):
    collection = Collection()
    collection.rows.extend(item.to_dict() for item in items)
    values: dict[str, Any] = {
        "tenant_id": "tenant-1",
        "case_matter_id": "matter-1",
        "practitioner_principal_id": "practitioner-1",
        "evaluation_time": AT,
        "restriction_collection": collection,
        "session": Session(),
    }
    values.update(changes)
    return barrier.inspect_practitioner_ethical_wall_read_barrier(**values)


def test_current_restriction_denies_content():
    item = MAKE()
    result = inspect(item)
    assert result.state is barrier.EthicalWallReadBarrierState.DENY_RESTRICTED
    assert result.currentness is not None
    assert result.currentness.decisive_restriction_fingerprints == (
        item.fingerprint,
    )
    assert result.authorized is False
    assert result.permits_content is False


def test_empty_history_is_not_clearance():
    result = inspect()
    assert result.state is barrier.EthicalWallReadBarrierState.DENY_UNVERIFIED
    assert result.authorized is False
    assert result.permits_content is False


def test_future_only_is_not_clearance():
    result = inspect(MAKE(effective_from=AT + timedelta(days=1)))
    assert result.state is barrier.EthicalWallReadBarrierState.DENY_UNVERIFIED
    assert result.permits_content is False


def test_two_independent_restrictions_are_decisive():
    a = MAKE()
    b = MAKE(
        restriction_id="restriction-2",
        reason_code="CLIENT_CONFIDENTIALITY",
    )
    result = inspect(a, b)
    assert result.state is barrier.EthicalWallReadBarrierState.DENY_RESTRICTED
    assert result.currentness is not None
    assert len(result.currentness.decisive_restriction_fingerprints) == 2


@pytest.mark.parametrize("change", [
    {"tenant_id": "foreign-tenant"},
    {"case_matter_id": "foreign-matter"},
    {"practitioner_principal_id": "foreign-practitioner"},
])
def test_cross_scope_query_never_grants(change):
    result = inspect(MAKE(), **change)
    assert result.authorized is False
    assert result.permits_content is False


def test_persisted_tampering_is_fail_closed():
    collection = Collection()
    raw = MAKE().to_dict()
    raw["reason_code"] = "INFORMATION_BARRIER"
    collection.rows.append(raw)
    result = inspect(restriction_collection=collection)
    assert result.state is barrier.EthicalWallReadBarrierState.DENY_UNAVAILABLE
    assert result.permits_content is False


def test_storage_outage_is_fail_closed():
    collection = Collection()
    collection.fail_read = True
    result = inspect(restriction_collection=collection)
    assert result.state is barrier.EthicalWallReadBarrierState.DENY_UNAVAILABLE
    assert result.currentness is None


@pytest.mark.parametrize("session", [
    None,
    object(),
    type("Inactive", (), {"in_transaction": False})(),
])
def test_no_active_transaction_never_reads_or_grants(session):
    collection = Collection()
    result = inspect(
        restriction_collection=collection,
        session=session,
    )
    assert result.state is barrier.EthicalWallReadBarrierState.DENY_UNAVAILABLE
    assert collection.queries == []
    assert result.authorized is False


def test_truncated_history_never_grants():
    collection = Collection()
    registry_limit = runpy.run_path(
        str(ROOT / "tools/eos/legal_operations/registry/"
            "legal_practitioner_ethical_wall_restriction_registry.py")
    )["MAX_HISTORY_READS"]
    collection.rows.extend(
        MAKE(
            restriction_id=f"restriction-{number}",
        ).to_dict()
        for number in range(registry_limit + 1)
    )
    result = inspect(restriction_collection=collection)
    assert result.state is barrier.EthicalWallReadBarrierState.DENY_UNAVAILABLE
    assert result.permits_content is False


def test_no_content_or_authorizing_interface():
    for name in (
        "grant_access", "allow_content", "read_document",
        "fetch_matter", "execute_workflow", "ai_retrieve",
        "waive", "lift", "reassign",
    ):
        assert not hasattr(barrier, name)


# WILSY OS SOVEREIGN ARTIFACT SEAL
# VERSION: v1.0.0-P9-R105-P4G-P5-R1
# END OF WILSY OS SOVEREIGN ARTIFACT
