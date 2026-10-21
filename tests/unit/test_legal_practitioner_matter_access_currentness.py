"""TITLE: WILSY P9 Pure Practitioner Matter Access Currentness RED.
VERSION: v1.0.0-P9-R93-PRACTITIONER-ACCESS-CURRENTNESS-RED
AUTHORITY: Test-first documentary policy projection only.
EPITOME: Exact-scope, deterministic effective-time and revision history,
    explicit DENY precedence, ambiguity and corruption fail-closed.
ABSOLUTE CANONICAL PATH:
    tests/unit/test_legal_practitioner_matter_access_currentness.py
COLLABORATION / OWNERSHIP: WILSY OS Core Engineering.
CERTIFICATION / UPDATE DATE: 2026-10-19
CHANGELOG:
    2026-10-19 v1.0.0-P9-R93-PRACTITIONER-ACCESS-CURRENTNESS-RED
    Freeze pure projection contract without issuance or access authority.
TENANT BOUNDARY: Exact tenant, case matter and practitioner.
AUTHORITY BOUNDARY: ALLOW_UNVERIFIED is documentary, not permission.
FINANCIAL EXECUTION AUTHORITY: None; Kennel EOS exclusively.
"""

from datetime import datetime, timedelta, timezone
from importlib import import_module

import pytest

from tools.eos.legal_operations.domain.legal_practitioner_matter_access import (
    LegalPractitionerMatterAccessDecision as Decision,
    LegalPractitionerMatterAccessEvidence as Evidence,
)

MODULE = (
    'tools.eos.legal_operations.service.legal_practitioner_matter_access_currentness'
)
AT = datetime(2026, 10, 19, 12, tzinfo=timezone.utc)


def _module():
    return import_module(MODULE)


def _evidence(
    *, evidence_id="policy-1", revision=1,
    decision=Decision.ALLOW, at=None, until=None,
    predecessor=None, tenant="tenant-1", matter="matter-1",
    practitioner="practitioner-1",
):
    return _p47_create(
        access_evidence_id=evidence_id,
        tenant_id=tenant,
        case_matter_id=matter,
        practitioner_principal_id=practitioner,
        revision=revision,
        decision=decision,
        effective_from=AT - timedelta(hours=1) if at is None else at,
        effective_until=until,
        issued_by_principal_id="issuer-1",
        source_evidence_fingerprint="a" * 128,
        supersedes_fingerprint=predecessor,
    )


def _project(items, **changes):
    args = dict(
        tenant_id="tenant-1",
        case_matter_id="matter-1",
        practitioner_principal_id="practitioner-1",
        evaluation_time=AT,
        evidence=items,
    )
    args.update(changes)
    return _module().project_legal_practitioner_matter_access_currentness(**args)


def _state(result):
    return result.state.value


def test_empty_history_is_not_access():
    assert _state(_project(())) == "NO_APPLICABLE_EVIDENCE"


def test_single_allow_is_unverified_not_grant():
    assert _state(_project((_evidence(),))) == "ALLOW_UNVERIFIED"


def test_single_deny_blocks():
    assert _state(_project((_evidence(decision=Decision.DENY),))) == "DENY_BLOCKED"


def test_independent_deny_overrides_independent_allow():
    allow = _evidence(evidence_id="allow-1")
    deny = _evidence(evidence_id="deny-1", decision=Decision.DENY)
    assert _state(_project((allow, deny))) == "DENY_BLOCKED"


def test_future_allow_is_not_applicable():
    value = _evidence(at=AT + timedelta(hours=1))
    assert _state(_project((value,))) == "NO_APPLICABLE_EVIDENCE"


def test_expired_allow_is_not_applicable():
    value = _evidence(until=AT)
    assert _state(_project((value,))) == "NO_APPLICABLE_EVIDENCE"


def test_revision_successor_deny_replaces_allow():
    first = _evidence()
    successor = _evidence(
        revision=2, predecessor=first.fingerprint,
        decision=Decision.DENY, at=AT - timedelta(minutes=30),
    )
    assert _state(_project((first, successor))) == "DENY_BLOCKED"


def test_expired_successor_never_reactivates_predecessor():
    first = _evidence()
    successor = _evidence(
        revision=2, predecessor=first.fingerprint,
        at=AT - timedelta(minutes=30),
        until=AT - timedelta(minutes=5),
    )
    assert _state(_project((first, successor))) == "NO_APPLICABLE_EVIDENCE"


def test_missing_revision_predecessor_is_corrupt():
    successor = _evidence(revision=2, predecessor="b" * 128)
    assert _state(_project((successor,))) == "CORRUPT_BLOCKED"


def test_divergent_same_revision_is_corrupt():
    allow = _evidence()
    deny = _evidence(decision=Decision.DENY)
    assert _state(_project((allow, deny))) == "CORRUPT_BLOCKED"


def test_cross_tenant_evidence_is_corrupt():
    value = _evidence(tenant="tenant-other")
    assert _state(_project((value,))) == "CORRUPT_BLOCKED"


def test_cross_matter_or_practitioner_is_corrupt():
    assert _state(_project((_evidence(matter="matter-other"),))) == "CORRUPT_BLOCKED"
    assert _state(_project((_evidence(practitioner="other"),))) == "CORRUPT_BLOCKED"


def test_exact_duplicate_replay_is_idempotent():
    value = _evidence()
    assert _state(_project((value, value))) == "ALLOW_UNVERIFIED"


def test_input_order_does_not_change_projection():
    allow = _evidence(evidence_id="allow-1")
    deny = _evidence(evidence_id="deny-1", decision=Decision.DENY)
    assert _project((allow, deny)) == _project((deny, allow))


def test_naive_evaluation_time_rejected():
    with pytest.raises(ValueError):
        _project((), evaluation_time=AT.replace(tzinfo=None))


def test_invalid_tenant_rejected():
    with pytest.raises(ValueError):
        _project((), tenant_id="default")


def test_no_execution_or_issuance_interface():
    module = _module()
    for name in (
        "grant_matter_access", "authorize_matter_access",
        "issue_access_permission", "execute_reassignment",
        "approve_access", "override_ethical_wall",
    ):
        assert not hasattr(module, name)


# WILSY OS SOVEREIGN ARTIFACT SEAL
# ARTIFACT: test_legal_practitioner_matter_access_currentness.py
# VERSION: v1.0.0-P9-R93-PRACTITIONER-ACCESS-CURRENTNESS-RED
# AUTHORITY: documentary projection only; no operational access
# FINANCIAL EXECUTION AUTHORITY: NONE
# END OF WILSY OS SOVEREIGN ARTIFACT

from tools.eos.legal_operations.service.legal_practitioner_matter_access_codec import create_practitioner_matter_access as _p47_create
