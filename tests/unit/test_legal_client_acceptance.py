"""Direct certificate for the immutable L9A client-acceptance domain.

VERSION: v1.0.0-L9A-CLIENT-ACCEPTANCE-CERT
AUTHORITY: Wilsy OS Core Governance
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tests/unit/test_legal_client_acceptance.py
AUTHORITY BOUNDARY: Pure matter-scoped client-acceptance evidence only.
FINANCIAL AUTHORITY BOUNDARY: Kennel EOS exclusively owns execution.
"""
from dataclasses import FrozenInstanceError, replace
from datetime import datetime, timezone

import pytest

from tools.eos.legal_operations.domain.legal_client_acceptance import (
    ACCEPTANCE_FIELDS,
    LegalClientAcceptance,
    LegalClientAcceptanceError,
    record_legal_client_acceptance,
)
from tools.eos.legal_operations.domain.legal_operations_lifecycle import (
    CaseMatter,
    CaseMatterState,
)


NOW = datetime(2026, 9, 26, 12, 0, 0, 123456, tzinfo=timezone.utc)
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


def acceptance(**overrides: object) -> LegalClientAcceptance:
    values = {
        "case_matter": matter(),
        "acceptance_id": "acceptance-1",
        "party_id": "party-1",
        "subject_reference": "client:acme-1",
        "subject_identity_fingerprint": FP_A,
        "acceptance_scope": "client-information-review:v1",
        "actor_principal_id": "principal-client-1",
        "accepted_at": NOW,
        "source_evidence_reference": "client-evidence:1",
        "source_evidence_fingerprint": FP_B,
    }
    values.update(overrides)
    return record_legal_client_acceptance(**values)


def test_valid_acceptance_binds_exact_matter_subject_actor_scope_and_evidence() -> None:
    source = matter()
    value = acceptance(case_matter=source)
    assert value.tenant_id == source.tenant_id
    assert value.case_matter_id == source.case_matter_id
    assert value.matter_fingerprint == source.fingerprint
    assert value.party_id == "party-1"
    assert value.subject_reference == "client:acme-1"
    assert value.subject_identity_fingerprint == FP_A
    assert value.acceptance_scope == "client-information-review:v1"
    assert value.actor_principal_id == "principal-client-1"
    assert value.source_evidence_reference == "client-evidence:1"
    assert value.source_evidence_fingerprint == FP_B
    assert value.accepted_at == NOW
    assert len(value.fingerprint) == 128


def test_round_trip_and_fingerprint_are_deterministic() -> None:
    value = acceptance()
    payload = value.to_dict()
    assert set(payload) == set(ACCEPTANCE_FIELDS)
    assert LegalClientAcceptance.from_dict(payload) == value
    assert LegalClientAcceptance.from_dict(payload).fingerprint == value.fingerprint


def test_value_is_frozen_and_semantic_mutation_changes_fingerprint() -> None:
    value = acceptance()
    with pytest.raises(FrozenInstanceError):
        value.acceptance_scope = "other-scope"  # type: ignore[misc]
    divergent = replace(value, acceptance_scope="client-information-review:v2", fingerprint="")
    assert divergent.fingerprint != value.fingerprint


def test_aware_iso_timestamp_is_normalized_to_utc_and_naive_is_rejected() -> None:
    value = acceptance(accepted_at="2026-09-26T14:00:00.123456+02:00")
    assert value.accepted_at == NOW
    with pytest.raises(LegalClientAcceptanceError) as raised:
        acceptance(accepted_at=datetime(2026, 9, 26, 12, 0))
    assert raised.value.code == "L9A_ACCEPTED_AT_INVALID"


def test_closed_matter_cannot_create_acceptance() -> None:
    closed = matter().transition_to(
        CaseMatterState.CLOSED,
        evidence_reference="closure:1",
        occurred_at=datetime(2026, 9, 26, 13, 0, tzinfo=timezone.utc),
    )
    with pytest.raises(LegalClientAcceptanceError) as raised:
        acceptance(case_matter=closed)
    assert raised.value.code == "L9A_OPEN_CASE_MATTER_REQUIRED"


@pytest.mark.parametrize(
    ("field", "value", "code"),
    [
        ("case_matter", object(), "L9A_CASE_MATTER_REQUIRED"),
        ("acceptance_id", " acceptance-1", "L9A_ACCEPTANCE_ID_INVALID"),
        ("party_id", "", "L9A_PARTY_ID_INVALID"),
        ("subject_reference", "person@example.com", "L9A_SUBJECT_REFERENCE_INVALID"),
        ("subject_identity_fingerprint", "A" * 128, "L9A_SUBJECT_IDENTITY_FINGERPRINT_INVALID"),
        ("actor_principal_id", " actor", "L9A_ACTOR_PRINCIPAL_ID_INVALID"),
        ("acceptance_scope", "engagement", "L9A_ACCEPTANCE_SCOPE_INVALID"),
        ("source_evidence_reference", "", "L9A_SOURCE_EVIDENCE_REFERENCE_INVALID"),
        ("source_evidence_fingerprint", "g" * 128, "L9A_SOURCE_EVIDENCE_FINGERPRINT_INVALID"),
    ],
)
def test_malformed_authority_fields_fail_closed(
    field: str,
    value: object,
    code: str,
) -> None:
    with pytest.raises(LegalClientAcceptanceError) as raised:
        acceptance(**{field: value})
    assert raised.value.code == code


def test_pseudo_tenant_matter_and_fingerprint_drift_fail_closed() -> None:
    with pytest.raises(LegalClientAcceptanceError) as raised:
        replace(acceptance(), tenant_id="GLOBAL_ROOT", fingerprint="")
    assert raised.value.code == "L9A_TENANT_REQUIRED"
    payload = acceptance().to_dict()
    payload["matter_fingerprint"] = "c" * 128
    with pytest.raises(LegalClientAcceptanceError) as raised:
        LegalClientAcceptance.from_dict(payload)
    assert raised.value.code == "L9A_FINGERPRINT_MISMATCH"


def test_case_matter_identity_and_reserved_scope_fail_closed() -> None:
    with pytest.raises(LegalClientAcceptanceError) as raised:
        replace(acceptance(), case_matter_id=" matter-1", fingerprint="")
    assert raised.value.code == "L9A_CASE_MATTER_ID_INVALID"
    with pytest.raises(LegalClientAcceptanceError) as raised:
        acceptance(acceptance_scope="representation:v1")
    assert raised.value.code == "L9A_ACCEPTANCE_SCOPE_INVALID"


def test_round_trip_tampering_and_schema_expansion_fail_closed() -> None:
    payload = acceptance().to_dict()
    tampered = dict(payload)
    tampered["acceptance_scope"] = "client-information-review:v2"
    with pytest.raises(LegalClientAcceptanceError) as raised:
        LegalClientAcceptance.from_dict(tampered)
    assert raised.value.code == "L9A_FINGERPRINT_MISMATCH"
    with pytest.raises(LegalClientAcceptanceError) as raised:
        LegalClientAcceptance.from_dict({**payload, "email": "secret@example.test"})
    assert raised.value.code == "L9A_SCHEMA_INVALID"


def test_domain_excludes_engagement_representation_financial_court_and_pii_fields() -> None:
    forbidden = {
        "engagement_active", "retainer_accepted", "representation_active",
        "representation_scope", "court_authorized", "conflict_cleared",
        "waiver", "ethical_wall", "billing_authorized", "payment_authorized",
        "tenant_visibility", "portal_access", "email", "phone", "address",
        "name", "password", "token",
    }
    assert forbidden.isdisjoint(ACCEPTANCE_FIELDS)
    assert forbidden.isdisjoint(acceptance().to_dict())


def test_acceptance_has_no_status_or_external_authority_claims() -> None:
    payload = acceptance().to_dict()
    assert "status" not in payload
    assert "engagement_id" not in payload
    assert "representation_id" not in payload
    assert "court_proceeding_id" not in payload
    assert "financial_authority" not in payload


# ARTIFACT: test_legal_client_acceptance.py
# VERSION: v1.0.0-L9A-CLIENT-ACCEPTANCE-CERT
# AUTHORITY BOUNDARY: pure immutable matter-scoped client-acceptance evidence
# TENANT POSTURE: exact CaseMatter-derived tenant and matter identity
# FAIL-CLOSED POSTURE: malformed, drifted, closed, or authority-expanding input rejects
# FINANCIAL EXECUTION AUTHORITY: none; Kennel EOS exclusively
# END OF WILSY OS SOVEREIGN ARTIFACT
