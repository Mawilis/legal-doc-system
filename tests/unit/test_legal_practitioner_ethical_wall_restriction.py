"""P9-R105-P4G-P2R3 ethical-wall restriction domain certificate."""
from dataclasses import FrozenInstanceError
from datetime import datetime, timedelta, timezone
from typing import Any
import pytest

from tools.eos.legal_operations.domain.legal_practitioner_ethical_wall_restriction import (
    FIELDS,
    REASONS,
    LegalPractitionerEthicalWallRestriction as Restriction,
    LegalPractitionerEthicalWallRestrictionError as Invalid,
)

T0 = datetime(2026, 10, 19, 12, 0, tzinfo=timezone.utc)

def make(**changes: Any) -> Restriction:
    # Explicit Any values support adversarial malformed-input cases.
    values: dict[str, Any] = dict(
        restriction_id="restriction-1",
        tenant_id="tenant-1",
        case_matter_id="matter-1",
        restricted_practitioner_principal_id="practitioner-1",
        source_evidence_fingerprint="a" * 128,
        recorded_by_principal_id="actor-1",
        effective_from=T0,
        reason_code="CONFLICT_RESTRICTION",
    )
    values.update(changes)
    return Restriction(**values)

def test_roundtrip_exact_digest_and_determinism():
    item = make()
    assert len(item.fingerprint) == 128
    assert all(c in "0123456789abcdef" for c in item.fingerprint)
    assert set(item.to_dict()) == FIELDS
    assert Restriction.from_dict(item.to_dict()) == item
    assert item == make()

def test_immutable():
    item = make()
    with pytest.raises(FrozenInstanceError):
        setattr(item, "tenant_id", "foreign")

@pytest.mark.parametrize("change", [
    {"tenant_id": "foreign"},
    {"case_matter_id": "other"},
    {"restricted_practitioner_principal_id": "other"},
    {"recorded_by_principal_id": "other"},
    {"source_evidence_fingerprint": "b" * 128},
    {"reason_code": "CLIENT_CONFIDENTIALITY"},
    {"effective_from": T0 + timedelta(seconds=1)},
])
def test_material_change_alters_digest(change):
    assert make(**change).fingerprint != make().fingerprint

@pytest.mark.parametrize("value", [
    "", "a" * 127, "a" * 129, "A" * 128,
    "g" * 128, "a" * 128 + "Z", None, 123,
])
def test_invalid_digest_denied(value):
    with pytest.raises(Invalid):
        make(source_evidence_fingerprint=value)

@pytest.mark.parametrize("change", [
    {"tenant_id": ""},
    {"tenant_id": " tenant-1"},
    {"case_matter_id": "matter-1 "},
    {"restricted_practitioner_principal_id": ""},
    {"reason_code": "APPROVED"},
    {"reason_code": "WAIVER_GRANTED"},
    {"effective_from": datetime(2026, 10, 19)},
])
def test_invalid_authority_inputs_denied(change):
    with pytest.raises(Invalid):
        make(**change)

def test_reasons_only_restrict():
    assert REASONS == frozenset({
        "CONFLICT_RESTRICTION",
        "CLIENT_CONFIDENTIALITY",
        "INFORMATION_BARRIER",
    })

def test_tampering_unknown_missing_and_noncanonical_denied():
    original = make().to_dict()
    for change in (
        {"case_matter_id": "forged"},
        {"extra_authority": True},
        {"effective_from": "2026-10-19T14:00:00+02:00"},
    ):
        changed = dict(original)
        changed.update(change)
        with pytest.raises(Invalid):
            Restriction.from_dict(changed)
    missing = dict(original)
    del missing["reason_code"]
    with pytest.raises(Invalid):
        Restriction.from_dict(missing)

def test_no_operational_authority():
    import tools.eos.legal_operations.domain.legal_practitioner_ethical_wall_restriction as module
    for name in ("waive", "lift", "grant_access", "reassign", "authorize"):
        assert not hasattr(module, name)

# WILSY OS SOVEREIGN ARTIFACT SEAL
# VERSION: v1.0.1-P9-R105-P4G-P2R3
# END OF WILSY OS SOVEREIGN ARTIFACT
