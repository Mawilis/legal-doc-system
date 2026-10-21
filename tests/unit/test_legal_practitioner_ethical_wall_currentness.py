"""P9-R105-P4G-P4-R2A ethical-wall currentness adversarial certificate."""
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any
import runpy

import pytest

from tools.eos.legal_operations.domain.legal_practitioner_ethical_wall_currentness import (
    LegalPractitionerEthicalWallCurrentnessState as State,
    LegalPractitionerEthicalWallCurrentnessError as Invalid,
    project_legal_practitioner_ethical_wall_currentness as project,
)

ROOT = Path(__file__).resolve().parents[2]
MAKE = runpy.run_path(
    str(ROOT / "tests/unit/test_legal_practitioner_ethical_wall_restriction.py")
)["make"]
AT = datetime(2026, 10, 19, 12, tzinfo=timezone.utc)


def evaluate(*items: Any, **changes: Any) -> Any:
    # Explicit Any prevents heterogeneous fixture values from being
    # incorrectly widened into every keyword parameter by Pyright.
    values: dict[str, Any] = dict(
        tenant_id="tenant-1",
        case_matter_id="matter-1",
        restricted_practitioner_principal_id="practitioner-1",
        evaluation_time=AT,
        restrictions=items,
    )
    values.update(changes)
    return project(**values)


def test_single_restriction_blocks():
    item = MAKE()
    value = evaluate(item)
    assert value.state is State.RESTRICTED
    assert value.blocks_access
    assert not value.grants_access
    assert value.decisive_restriction_fingerprints == (item.fingerprint,)


def test_empty_history_is_not_clearance():
    value = evaluate()
    assert value.state is State.NO_RECORDED_RESTRICTION
    assert value.decisive_restriction_fingerprints == ()
    assert not value.grants_access


def test_future_only_history_does_not_backdate_restriction():
    item = MAKE(effective_from=AT + timedelta(seconds=1))
    earlier = evaluate(item)
    later = evaluate(item, evaluation_time=AT + timedelta(seconds=1))
    assert earlier.state is State.NO_RECORDED_RESTRICTION
    assert earlier.observed_restriction_fingerprints == (item.fingerprint,)
    assert later.state is State.RESTRICTED


def test_restriction_does_not_expire_without_authorized_lifecycle():
    item = MAKE()
    assert evaluate(
        item, evaluation_time=AT + timedelta(days=36500)
    ).state is State.RESTRICTED


def test_duplicate_replay_does_not_change_projection():
    item = MAKE()
    assert evaluate(item, item) == evaluate(item)


def test_independent_restrictions_are_cumulative():
    a = MAKE()
    b = MAKE(
        restriction_id="restriction-2",
        reason_code="CLIENT_CONFIDENTIALITY",
    )
    assert evaluate(a, b) == evaluate(b, a)
    assert evaluate(a, b).state is State.RESTRICTED
    assert len(evaluate(a, b).decisive_restriction_fingerprints) == 2


@pytest.mark.parametrize("change", [
    {"tenant_id": "other-tenant"},
    {"case_matter_id": "other-matter"},
    {"restricted_practitioner_principal_id": "other-practitioner"},
])
def test_foreign_scope_corrupt_blocks(change):
    result = evaluate(MAKE(**change))
    assert result.state is State.CORRUPT_BLOCKED
    assert result.blocks_access
    assert not result.grants_access


def test_divergent_same_identity_corrupt_blocks():
    a = MAKE()
    b = MAKE(reason_code="CLIENT_CONFIDENTIALITY")
    assert evaluate(a, b).state is State.CORRUPT_BLOCKED


def test_invalid_history_member_corrupt_blocks():
    assert evaluate(MAKE(), object()).state is State.CORRUPT_BLOCKED


def test_unavailable_history_iterator_corrupt_blocks():
    class Broken:
        def __iter__(self):
            raise RuntimeError("READ_FAILED")

    result = project(
        tenant_id="tenant-1",
        case_matter_id="matter-1",
        restricted_practitioner_principal_id="practitioner-1",
        evaluation_time=AT,
        restrictions=Broken(),
    )
    assert result.state is State.CORRUPT_BLOCKED


@pytest.mark.parametrize("change", [
    {"tenant_id": ""},
    {"tenant_id": " other"},
    {"case_matter_id": ""},
    {"restricted_practitioner_principal_id": ""},
    {"evaluation_time": datetime(2026, 10, 19)},
])
def test_invalid_request_scope_rejected(change):
    with pytest.raises(Invalid):
        evaluate(**change)


def test_never_grants_operational_access():
    import tools.eos.legal_operations.domain.legal_practitioner_ethical_wall_currentness as module
    for name in ("grant_access", "waive", "lift",
                 "authorize", "reassign", "execute"):
        assert not hasattr(module, name)
    for result in (evaluate(), evaluate(MAKE())):
        assert result.grants_access is False


# WILSY OS SOVEREIGN ARTIFACT SEAL
# VERSION: v1.0.0-P9-R105-P4G-P4-R2A
# END OF WILSY OS SOVEREIGN ARTIFACT
