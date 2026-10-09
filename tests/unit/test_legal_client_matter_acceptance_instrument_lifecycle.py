"""Direct certificate for the pure L9A4-P2A lifecycle evidence domain.

TITLE: WILSY OS Legal Client Matter Acceptance Instrument Lifecycle Certificate
VERSION: v1.0.0-L9A4-P2A-MATTER-ACCEPTANCE-INSTRUMENT-LIFECYCLE-CERT
AUTHORITY: Wilsy OS Core Governance
EPITOME: Certify immutable exact-scope lifecycle facts, terminal transitions,
         successor linkage, chronology, provenance, strict hydration and
         SHA3-512 integrity without persistence or authority expansion.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tests/unit/test_legal_client_matter_acceptance_instrument_lifecycle.py
COLLABORATION / OWNERSHIP: Synthetic in-memory fixtures only; no Mongo or HTTP.
CERTIFICATION / UPDATE DATE: 2026-09-26
CHANGELOG: v1.0.0-L9A4-P2A-MATTER-ACCEPTANCE-INSTRUMENT-LIFECYCLE-CERT
           certifies the one-file pure domain gate.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2; ISO 27001.
SECURITY / PRIVACY POSTURE: No PII, secrets, tokens, network or persistence.
TENANT BOUNDARY: Synthetic exact tenant/matter assertions.
AUTHORITY BOUNDARY: Lifecycle evidence only; no approval or acceptance.
FINANCIAL AUTHORITY BOUNDARY: Kennel EOS exclusively owns execution.
"""
from __future__ import annotations

from copy import deepcopy
from datetime import datetime, timedelta, timezone
import hashlib
import inspect

import pytest

from tools.eos.legal_operations.domain import (
    legal_client_matter_acceptance_instrument_lifecycle as lifecycle,
)


UTC = timezone.utc
NOW = datetime(2026, 9, 26, 12, 0, 0, 123456, tzinfo=UTC)
HEX_A = hashlib.sha3_512(b"instrument-a").hexdigest()
HEX_B = hashlib.sha3_512(b"instrument-b").hexdigest()
MATTER_FP = hashlib.sha3_512(b"matter").hexdigest()
EVIDENCE_FP = hashlib.sha3_512(b"evidence").hexdigest()
SUCCESSOR_FP = hashlib.sha3_512(b"successor").hexdigest()


def make(
    *,
    status: lifecycle.LegalClientMatterAcceptanceInstrumentLifecycleStatus = (
        lifecycle.LegalClientMatterAcceptanceInstrumentLifecycleStatus.ACTIVE
    ),
    prior_status: lifecycle.LegalClientMatterAcceptanceInstrumentLifecycleStatus | None = None,
    occurred_at: datetime = NOW,
    **changes: object,
) -> lifecycle.LegalClientMatterAcceptanceInstrumentLifecycle:
    """Build one synthetic exact-scope lifecycle fact."""
    values: dict[str, object] = {
        "tenant_id": "tenant-law",
        "case_matter_id": "matter-1",
        "matter_fingerprint": MATTER_FP,
        "instrument_id": "instrument-1",
        "version": "1.0.0",
        "instrument_fingerprint": HEX_A,
        "status": status,
        "prior_status": prior_status,
        "occurred_at": occurred_at,
        "lifecycle_evidence_reference": "evidence:lifecycle-1",
        "lifecycle_evidence_fingerprint": EVIDENCE_FP,
        "superseding_version_id": None,
        "superseding_instrument_fingerprint": None,
    }
    values.update(changes)
    return lifecycle.LegalClientMatterAcceptanceInstrumentLifecycle(**values)


def test_all_lifecycle_states_and_terminal_semantics() -> None:
    """ACTIVE is explicit; each terminal state has distinct semantics."""
    active = make()
    superseded = make(
        status=lifecycle.LegalClientMatterAcceptanceInstrumentLifecycleStatus.SUPERSEDED,
        prior_status=lifecycle.LegalClientMatterAcceptanceInstrumentLifecycleStatus.ACTIVE,
        superseding_version_id="instrument-1:2.0.0",
        superseding_instrument_fingerprint=SUCCESSOR_FP,
    )
    retired = make(
        status=lifecycle.LegalClientMatterAcceptanceInstrumentLifecycleStatus.RETIRED,
        prior_status=lifecycle.LegalClientMatterAcceptanceInstrumentLifecycleStatus.ACTIVE,
    )
    withdrawn = make(
        status=lifecycle.LegalClientMatterAcceptanceInstrumentLifecycleStatus.WITHDRAWN,
        prior_status=lifecycle.LegalClientMatterAcceptanceInstrumentLifecycleStatus.ACTIVE,
    )
    assert active.status.value == "ACTIVE"
    assert superseded.is_terminal and retired.is_terminal and withdrawn.is_terminal
    assert len({active.fingerprint, superseded.fingerprint, retired.fingerprint, withdrawn.fingerprint}) == 4


def test_exact_subject_binding_and_version_identity() -> None:
    """Tenant, matter, instrument and version are all fingerprinted fields."""
    value = make()
    assert value.tenant_id == "tenant-law"
    assert value.case_matter_id == "matter-1"
    assert value.matter_fingerprint == MATTER_FP
    assert value.instrument_id == "instrument-1"
    assert value.version == "1.0.0"
    assert value.instrument_fingerprint == HEX_A
    assert value.version_id == "instrument-1:1.0.0"


def test_immutability_and_utc_microseconds() -> None:
    """Frozen values normalize offsets while preserving microseconds."""
    value = make(
        occurred_at=datetime(
            2026, 9, 26, 14, 0, 0, 123456,
            tzinfo=timezone(timedelta(hours=2)),
        )
    )
    assert value.occurred_at == NOW
    assert value.occurred_at.microsecond == 123456
    with pytest.raises((AttributeError, TypeError)):
        value.status = lifecycle.LegalClientMatterAcceptanceInstrumentLifecycleStatus.RETIRED  # type: ignore[misc]


def test_fingerprint_is_deterministic_and_semantic_changes_are_visible() -> None:
    """Exact semantics replay exactly; any semantic change changes the digest."""
    first = make()
    second = make()
    changed = make(instrument_fingerprint=HEX_B)
    assert first.fingerprint == second.fingerprint
    assert first.to_dict() == second.to_dict()
    assert changed.fingerprint != first.fingerprint


def test_hydration_round_trip_is_exact() -> None:
    """Serialized UTC/enums hydrate only through the exact schema."""
    value = make(
        status=lifecycle.LegalClientMatterAcceptanceInstrumentLifecycleStatus.SUPERSEDED,
        prior_status=lifecycle.LegalClientMatterAcceptanceInstrumentLifecycleStatus.ACTIVE,
        superseding_version_id="instrument-1:2.0.0",
        superseding_instrument_fingerprint=SUCCESSOR_FP,
    )
    assert lifecycle.LegalClientMatterAcceptanceInstrumentLifecycle.from_dict(value.to_dict()) == value


@pytest.mark.parametrize(
    ("field", "replacement"),
    [
        ("tenant_id", "global"),
        ("case_matter_id", "bad matter"),
        ("matter_fingerprint", "bad"),
        ("instrument_id", "bad instrument"),
        ("version", "bad version"),
        ("instrument_fingerprint", "bad"),
        ("lifecycle_evidence_reference", "bad\nreference"),
        ("lifecycle_evidence_fingerprint", "bad"),
    ],
)
def test_malformed_subject_or_provenance_rejected(field: str, replacement: object) -> None:
    """Malformed scope and evidence cannot be coerced."""
    with pytest.raises(lifecycle.LegalClientMatterAcceptanceInstrumentLifecycleError):
        make(**{field: replacement})


def test_naive_timestamp_is_rejected() -> None:
    """Browser-style naive timestamps are not lifecycle authority."""
    with pytest.raises(lifecycle.LegalClientMatterAcceptanceInstrumentLifecycleError):
        make(occurred_at=datetime(2026, 9, 26, 12, 0, 0, 123456))


def test_transition_rules_fail_closed() -> None:
    """Only ACTIVE baseline and ACTIVE-to-terminal transitions are valid."""
    status = lifecycle.LegalClientMatterAcceptanceInstrumentLifecycleStatus
    with pytest.raises(lifecycle.LegalClientMatterAcceptanceInstrumentLifecycleError):
        make(status=status.ACTIVE, prior_status=status.ACTIVE)
    with pytest.raises(lifecycle.LegalClientMatterAcceptanceInstrumentLifecycleError):
        make(status=status.RETIRED)
    with pytest.raises(lifecycle.LegalClientMatterAcceptanceInstrumentLifecycleError):
        make(status=status.SUPERSEDED, prior_status=status.ACTIVE)
    with pytest.raises(lifecycle.LegalClientMatterAcceptanceInstrumentLifecycleError):
        make(status=status.RETIRED, prior_status=status.ACTIVE, superseding_version_id="instrument-1:2.0.0")
    with pytest.raises(lifecycle.LegalClientMatterAcceptanceInstrumentLifecycleError):
        make(status=status.WITHDRAWN, prior_status=status.ACTIVE, superseding_instrument_fingerprint=SUCCESSOR_FP)


def test_supersession_requires_same_chain_and_no_self_reference() -> None:
    """SUPERSEDED structurally binds a different version in the same chain."""
    status = lifecycle.LegalClientMatterAcceptanceInstrumentLifecycleStatus.SUPERSEDED
    with pytest.raises(lifecycle.LegalClientMatterAcceptanceInstrumentLifecycleError):
        make(
            status=status,
            prior_status=lifecycle.LegalClientMatterAcceptanceInstrumentLifecycleStatus.ACTIVE,
            superseding_version_id="other-instrument:2.0.0",
            superseding_instrument_fingerprint=SUCCESSOR_FP,
        )
    with pytest.raises(lifecycle.LegalClientMatterAcceptanceInstrumentLifecycleError):
        make(
            status=status,
            prior_status=lifecycle.LegalClientMatterAcceptanceInstrumentLifecycleStatus.ACTIVE,
            superseding_version_id="instrument-1:1.0.0",
            superseding_instrument_fingerprint=SUCCESSOR_FP,
        )


def test_terminal_states_are_not_reactivatable() -> None:
    """No transition path accepts a terminal prior state or in-place mutation."""
    status = lifecycle.LegalClientMatterAcceptanceInstrumentLifecycleStatus
    for terminal in (status.SUPERSEDED, status.RETIRED, status.WITHDRAWN):
        with pytest.raises(lifecycle.LegalClientMatterAcceptanceInstrumentLifecycleError):
            make(status=status.ACTIVE, prior_status=terminal)


def test_schema_and_fingerprint_tampering_are_rejected() -> None:
    """Strict hydration rejects extra, missing, schema and digest drift."""
    value = make()
    payload = value.to_dict()
    tampered = deepcopy(payload)
    tampered["schema"] = "other"
    with pytest.raises(lifecycle.LegalClientMatterAcceptanceInstrumentLifecycleError):
        lifecycle.LegalClientMatterAcceptanceInstrumentLifecycle.from_dict(tampered)
    tampered = deepcopy(payload)
    tampered["fingerprint"] = "0" * 128
    with pytest.raises(lifecycle.LegalClientMatterAcceptanceInstrumentLifecycleError):
        lifecycle.LegalClientMatterAcceptanceInstrumentLifecycle.from_dict(tampered)
    tampered = deepcopy(payload)
    tampered["unexpected"] = True
    with pytest.raises(lifecycle.LegalClientMatterAcceptanceInstrumentLifecycleError):
        lifecycle.LegalClientMatterAcceptanceInstrumentLifecycle.from_dict(tampered)
    tampered = deepcopy(payload)
    del tampered["status"]
    with pytest.raises(lifecycle.LegalClientMatterAcceptanceInstrumentLifecycleError):
        lifecycle.LegalClientMatterAcceptanceInstrumentLifecycle.from_dict(tampered)


def test_enum_and_state_binding_are_strict() -> None:
    """Unknown lifecycle states cannot enter the domain."""
    with pytest.raises(lifecycle.LegalClientMatterAcceptanceInstrumentLifecycleError):
        make(status="ACTIVE")  # type: ignore[arg-type]


def test_authority_exclusions_and_no_pii_requirement() -> None:
    """The pure domain has no persistence, transport or broader authority."""
    source = inspect.getsource(lifecycle)
    assert "pymongo" not in source
    assert "requests" not in source
    assert "LegalClientAcceptance" not in source
    assert "LegalClientActingCapacity" not in source
    assert not hasattr(lifecycle, "LegalClientAcceptance")
    assert not hasattr(lifecycle, "LegalClientActingCapacity")
    assert not hasattr(lifecycle, "LegalEngagement")
    assert not hasattr(lifecycle, "LegalRepresentation")


def test_public_factory_is_pure_and_does_not_claim_current_approval() -> None:
    """Factory creates only lifecycle evidence and performs no external work."""
    value = lifecycle.record_legal_client_matter_acceptance_instrument_lifecycle(
        tenant_id="tenant-law",
        case_matter_id="matter-1",
        matter_fingerprint=MATTER_FP,
        instrument_id="instrument-1",
        version="1.0.0",
        instrument_fingerprint=HEX_A,
        status=lifecycle.LegalClientMatterAcceptanceInstrumentLifecycleStatus.ACTIVE,
        occurred_at=NOW,
        lifecycle_evidence_reference="evidence:lifecycle-1",
        lifecycle_evidence_fingerprint=EVIDENCE_FP,
    )
    assert value.status is lifecycle.LegalClientMatterAcceptanceInstrumentLifecycleStatus.ACTIVE
    assert value.to_dict()["fingerprint"] == value.fingerprint


# ARTIFACT: test_legal_client_matter_acceptance_instrument_lifecycle.py
# VERSION: v1.0.0-L9A4-P2A-MATTER-ACCEPTANCE-INSTRUMENT-LIFECYCLE-CERT
# AUTHORITY BOUNDARY: pure lifecycle evidence certificate only
# TENANT POSTURE: synthetic exact-scope fixtures
# FAIL-CLOSED POSTURE: malformed, divergent, cross-chain and terminal reactivation cases reject
# FINANCIAL EXECUTION AUTHORITY: none; Kennel EOS remains exclusive
# END OF WILSY OS SOVEREIGN ARTIFACT
