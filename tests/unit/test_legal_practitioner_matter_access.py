"""TITLE: WILSY OS P9 Practitioner Matter Access RED Certificate.
VERSION: v1.0.1-P9-R83R1-PRACTITIONER-MATTER-ACCESS-RED
AUTHORITY: Pure immutable practitioner matter-access evidence tests.
EPITOME: Exact tenant/matter/principal, ALLOW/DENY, UTC time and SHA3-512.
ABSOLUTE CANONICAL PATH:
    tests/unit/test_legal_practitioner_matter_access.py
COLLABORATION / OWNERSHIP: Wilsy OS Core Engineering.
CERTIFICATION / UPDATE DATE: 2026-10-19
CHANGELOG:
    2026-10-19 v1.0.1-P9-R83R1-PRACTITIONER-MATTER-ACCESS-RED
    Repair certification harness; retain original twelve behavioral contracts.
    2026-10-19 v1.0.0-P9-R83-PRACTITIONER-MATTER-ACCESS-RED
    Freeze evidence-only semantics before production implementation.
TENANT BOUNDARY: Exact tenant, case matter, practitioner principal.
AUTHORITY BOUNDARY: Evidence is not authorized policy issuance.
    No affirmative matter access, ethical-wall clearance, professional
    qualification, IAM authorization or reassignment execution.
FINANCIAL EXECUTION AUTHORITY: None; Kennel EOS exclusively.
"""

from __future__ import annotations

from dataclasses import FrozenInstanceError
from datetime import datetime, timedelta, timezone
from importlib import import_module

import pytest

MODULE = (
    "tools.eos.legal_operations.domain."
    "legal_practitioner_matter_access"
)
T0 = datetime(2026, 10, 19, 9, 0, tzinfo=timezone.utc)
FP = "a" * 128


def _module():
    return import_module(MODULE)


def _make(**changes: object):
    module = _module()
    values: dict[str, object] = {
        "access_evidence_id": "access-evidence-1",
        "tenant_id": "tenant-1",
        "case_matter_id": "matter-1",
        "practitioner_principal_id": "practitioner-1",
        "revision": 1,
        "decision": module.LegalPractitionerMatterAccessDecision.ALLOW,
        "effective_from": T0,
        "effective_until": None,
        "issued_by_principal_id": "actor-1",
        "source_evidence_fingerprint": FP,
        "supersedes_fingerprint": None,
    }
    values.update(changes)
    return module.LegalPractitionerMatterAccessEvidence(**values)


def test_exact_allow_evidence_is_constructible_but_not_authorization():
    value = _make()
    assert value.tenant_id == "tenant-1"
    assert value.case_matter_id == "matter-1"
    assert value.practitioner_principal_id == "practitioner-1"
    assert value.revision == 1
    assert value.decision.value == "ALLOW"


def test_explicit_deny_is_distinct_immutable_evidence():
    module = _module()
    value = _make(
        decision=module.LegalPractitionerMatterAccessDecision.DENY
    )
    assert value.decision.value == "DENY"
    assert value.fingerprint != _make().fingerprint


def test_identical_evidence_has_deterministic_sha3_512_fingerprint():
    first = _make()
    second = _make()
    assert first.fingerprint == second.fingerprint
    assert isinstance(first.fingerprint, str)
    assert len(first.fingerprint) == 128
    assert all(ch in "0123456789abcdef" for ch in first.fingerprint)


def test_strict_round_trip_preserves_exact_evidence():
    module = _module()
    value = _make(effective_until=T0 + timedelta(days=2))
    hydrated = module.LegalPractitionerMatterAccessEvidence.from_dict(
        value.to_dict()
    )
    assert hydrated == value
    assert hydrated.fingerprint == value.fingerprint


def test_evidence_is_frozen():
    value = _make()
    with pytest.raises((FrozenInstanceError, AttributeError)):
        value.tenant_id = "another-tenant"


def test_pseudo_tenant_rejected():
    with pytest.raises(ValueError):
        _make(tenant_id="default")


def test_invalid_matter_and_practitioner_rejected():
    with pytest.raises(ValueError):
        _make(case_matter_id=" ")
    with pytest.raises(ValueError):
        _make(practitioner_principal_id=" ")


def test_naive_effective_time_rejected():
    with pytest.raises(ValueError):
        _make(effective_from=datetime(2026, 10, 19, 9, 0))


def test_invalid_effective_interval_rejected():
    with pytest.raises(ValueError):
        _make(effective_until=T0)
    with pytest.raises(ValueError):
        _make(effective_until=T0 - timedelta(seconds=1))


def test_later_revision_requires_explicit_predecessor():
    with pytest.raises(ValueError):
        _make(revision=2, supersedes_fingerprint=None)
    with pytest.raises(ValueError):
        _make(revision=1, supersedes_fingerprint=FP)


def test_fingerprint_and_shape_tampering_rejected():
    module = _module()
    data = _make().to_dict()

    forged = dict(data)
    forged["tenant_id"] = "tenant-foreign"
    with pytest.raises(ValueError):
        module.LegalPractitionerMatterAccessEvidence.from_dict(forged)

    extra = dict(data)
    extra["self_authorized"] = True
    with pytest.raises(ValueError):
        module.LegalPractitionerMatterAccessEvidence.from_dict(extra)

    missing = dict(data)
    missing.pop("case_matter_id")
    with pytest.raises(ValueError):
        module.LegalPractitionerMatterAccessEvidence.from_dict(missing)


def test_no_issuance_access_or_reassignment_execution_interface():
    module = _module()
    for name in (
        "grant_matter_access",
        "authorize_matter_access",
        "issue_access_permission",
        "approve_access",
        "override_ethical_wall",
        "authorize_reassignment",
        "execute_reassignment",
        "persist_reassignment",
    ):
        assert not hasattr(module, name)


# WILSY OS SOVEREIGN ARTIFACT SEAL
# ARTIFACT: test_legal_practitioner_matter_access.py
# VERSION: v1.0.1-P9-R83R1-PRACTITIONER-MATTER-ACCESS-RED
# AUTHORITY BOUNDARY: immutable policy evidence only
# ISSUER AUTHORITY / AFFIRMATIVE ACCESS: NOT GRANTED
# ETHICAL WALL / PROFESSIONAL STATUS / APPROVAL: NOT GRANTED
# REASSIGNMENT EXECUTION / PERSISTENCE: NONE
# FINANCIAL EXECUTION AUTHORITY: NONE
# END OF WILSY OS SOVEREIGN ARTIFACT
