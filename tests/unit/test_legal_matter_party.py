"""Direct certificate for immutable L8-8A legal matter-party authority.

VERSION: v1.0.0-L8-8A-LEGAL-MATTER-PARTY-CERT
AUTHORITY: Wilsy OS Core Governance
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tests/unit/test_legal_matter_party.py
AUTHORITY BOUNDARY: Pure matter-party association evidence only.
FINANCIAL AUTHORITY BOUNDARY: Kennel EOS exclusively owns execution.
"""
from dataclasses import FrozenInstanceError, replace
from datetime import datetime, timezone

import pytest

from tools.eos.legal_operations.domain.legal_matter_party import (
    PARTY_FIELDS,
    LegalMatterParty,
    LegalMatterPartyError,
    LegalMatterPartyKind,
    LegalMatterPartyRole,
    LegalMatterPartySide,
    register_legal_matter_party,
)
from tools.eos.legal_operations.domain.legal_operations_lifecycle import (
    CaseMatter,
    CaseMatterState,
)


NOW = datetime(2026, 9, 25, 12, 0, tzinfo=timezone.utc)
FP_A = "a" * 128
FP_B = "b" * 128


def matter() -> CaseMatter:
    return CaseMatter(
        tenant_id="tenant-law",
        case_matter_id="matter-1",
        matter_reference="MAT-2026-001",
        opened_at=NOW,
        evidence_reference="intake:1",
    )


def party(**overrides: object) -> LegalMatterParty:
    values = {
        "matter": matter(),
        "party_id": "party-1",
        "party_kind": LegalMatterPartyKind.ORGANIZATION,
        "party_side": LegalMatterPartySide.CLIENT_SIDE,
        "matter_role": LegalMatterPartyRole.CLIENT,
        "subject_reference": "organization:acme-legal",
        "subject_identity_fingerprint": FP_A,
        "display_name": "Acme Legal (Pty) Ltd",
        "registered_at": NOW,
        "source_evidence_reference": "intake-party:1",
        "source_evidence_fingerprint": FP_B,
    }
    values.update(overrides)
    return register_legal_matter_party(**values)


def test_valid_party_is_bound_to_exact_open_case_matter() -> None:
    source = matter()
    value = party(matter=source)
    assert value.tenant_id == source.tenant_id
    assert value.case_matter_id == source.case_matter_id
    assert value.matter_fingerprint == source.fingerprint
    assert value.party_side is LegalMatterPartySide.CLIENT_SIDE
    assert value.matter_role is LegalMatterPartyRole.CLIENT
    assert len(value.fingerprint) == 128


def test_round_trip_and_fingerprint_are_deterministic() -> None:
    value = party()
    payload = value.to_dict()
    assert set(payload) == set(PARTY_FIELDS)
    assert LegalMatterParty.from_dict(payload) == value
    assert LegalMatterParty.from_dict(payload).fingerprint == value.fingerprint


def test_closed_matter_cannot_admit_new_party() -> None:
    closed = matter().transition_to(
        CaseMatterState.CLOSED,
        evidence_reference="closure:1",
        occurred_at=datetime(2026, 9, 25, 13, 0, tzinfo=timezone.utc),
    )
    with pytest.raises(LegalMatterPartyError) as raised:
        party(matter=closed)
    assert raised.value.code == "L8_8A_OPEN_CASE_MATTER_REQUIRED"


@pytest.mark.parametrize(
    "reference",
    [
        "1234567890123",
        "person@example.com",
        "https://example.test/person/1",
        "/clients/secret.json",
        " subject:abc",
        "subject:",
    ],
)
def test_subject_reference_must_be_opaque_authority_reference(reference: str) -> None:
    with pytest.raises(LegalMatterPartyError) as raised:
        party(subject_reference=reference)
    assert raised.value.code == "L8_8A_SUBJECT_REFERENCE_INVALID"


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("party_kind", "ALIEN"),
        ("party_side", "CONFLICTED"),
        ("matter_role", "JUDGE_AND_JURY"),
    ],
)
def test_party_classifications_are_closed(field: str, value: str) -> None:
    with pytest.raises(LegalMatterPartyError) as raised:
        party(**{field: value})
    assert raised.value.code == "L8_8A_PARTY_CLASSIFICATION_INVALID"


def test_subject_identity_requires_exact_lowercase_sha3_512_shape() -> None:
    for invalid in ("a" * 127, "A" * 128, "g" * 128):
        with pytest.raises(LegalMatterPartyError) as raised:
            party(subject_identity_fingerprint=invalid)
        assert raised.value.code == "L8_8A_SUBJECT_IDENTITY_FINGERPRINT_INVALID"


def test_registered_at_requires_timezone_awareness() -> None:
    with pytest.raises(LegalMatterPartyError) as raised:
        party(registered_at=datetime(2026, 9, 25, 12, 0))
    assert raised.value.code == "L8_8A_REGISTERED_AT_INVALID"


def test_stored_fingerprint_tampering_rejects() -> None:
    payload = party().to_dict()
    payload["display_name"] = "Tampered"
    with pytest.raises(LegalMatterPartyError) as raised:
        LegalMatterParty.from_dict(payload)
    assert raised.value.code == "L8_8A_FINGERPRINT_MISMATCH"


def test_schema_is_exact_and_raw_pii_fields_do_not_exist() -> None:
    payload = party().to_dict()
    forbidden = {
        "id_number", "identity_number", "passport_number", "tax_number",
        "email", "phone", "address", "bank_account", "account_number",
        "biometric", "password", "secret", "token",
    }
    assert forbidden.isdisjoint(payload)
    with pytest.raises(LegalMatterPartyError) as raised:
        LegalMatterParty.from_dict({**payload, "email": "secret@example.test"})
    assert raised.value.code == "L8_8A_SCHEMA_INVALID"


def test_value_is_frozen_and_divergence_changes_fingerprint() -> None:
    value = party()
    with pytest.raises(FrozenInstanceError):
        value.display_name = "Mutated"  # type: ignore[misc]
    divergent = replace(value, display_name="Another Law Firm", fingerprint="")
    assert divergent.fingerprint != value.fingerprint


def test_direct_constructor_rejects_pseudo_tenant_scope() -> None:
    source = party()
    with pytest.raises(LegalMatterPartyError) as raised:
        replace(source, tenant_id="GLOBAL_ROOT", fingerprint="")
    assert raised.value.code == "L8_8A_TENANT_REQUIRED"


# ARTIFACT: test_legal_matter_party.py
# VERSION: v1.0.0-L8-8A-LEGAL-MATTER-PARTY-CERT
# AUTHORITY BOUNDARY: pure immutable party-association evidence only
# TENANT POSTURE: exact P1 CaseMatter-derived tenant and matter identity
# FAIL-CLOSED POSTURE: closed/malformed/raw-identity-shaped/drifted evidence rejects
# FINANCIAL EXECUTION AUTHORITY: none; Kennel EOS exclusively
# END OF WILSY OS SOVEREIGN ARTIFACT
