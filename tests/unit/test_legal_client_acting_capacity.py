"""Direct certificate for immutable L9A4-P1A acting-capacity evidence.

TITLE: WILSY OS Legal Client Acting Capacity Certificate
VERSION: v1.0.0-L9A4-P1A-CLIENT-ACTING-CAPACITY-CERT
AUTHORITY: Direct adversarial certification of pure acting-capacity evidence.
EPITOME: Prove exact CaseMatter/LegalMatterParty correlation, bounded capacity
         vocabulary, UTC chronology, immutable deterministic SHA3-512 integrity,
         strict hydration and the absence of acceptance, engagement,
         representation, Court, IAM, persistence or financial authority.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tests/unit/test_legal_client_acting_capacity.py
COLLABORATION / OWNERSHIP: The L9A4-P1A production domain is the sole subject
                            under test. P1 CaseMatter and L8-8A LegalMatterParty
                            provide synthetic canonical evidence. Registry,
                            orchestrator, IAM, HTTP, UI and persistence remain
                            later gates.
CERTIFICATION / UPDATE DATE: 2026-09-26
CHANGELOG: v1.0.0-L9A4-P1A-CLIENT-ACTING-CAPACITY-CERT establishes direct
           proof for valid construction, provenance correlation, immutability,
           chronology, strict schema/fingerprint hydration and explicit
           authority exclusions.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2; ISO 27001.
SECURITY / PRIVACY POSTURE: Synthetic opaque identifiers and SHA3-512 values
                             only; no credentials, tokens, raw PII, network or
                             production records.
TENANT BOUNDARY: Assertions require exact matter and party provenance; no
                 browser, role or visibility inference is permitted.
AUTHORITY BOUNDARY: Certificate evidence only; passing tests grant no runtime
                    client authority or legal sufficiency.
FINANCIAL AUTHORITY BOUNDARY: Kennel EOS exclusively owns execution.
TRANSACTION BOUNDARY: Pure in-memory unit tests; no database, HTTP, IAM,
                      transaction, filesystem or network mutation.
FAIL-CLOSED DECLARATION: Every malformed or authority-expanding input must
                         reject rather than become capacity truth.
"""
from __future__ import annotations

import ast
from dataclasses import FrozenInstanceError, replace
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, cast

import pytest

from tools.eos.legal_operations.domain.legal_client_acting_capacity import (
    ACTING_CAPACITY_FIELDS,
    VERSION,
    LegalClientActingCapacity,
    LegalClientActingCapacityError,
    LegalClientActingCapacityType,
    record_legal_client_acting_capacity,
)
from tools.eos.legal_operations.domain.legal_matter_party import (
    LegalMatterPartyKind,
    LegalMatterPartyRole,
    LegalMatterPartySide,
    register_legal_matter_party,
)
from tools.eos.legal_operations.domain.legal_operations_lifecycle import (
    CaseMatter,
    CaseMatterState,
)


BASE = datetime(2026, 9, 26, 12, 0, 0, 123456, tzinfo=timezone.utc)
TENANT = "tenant-l9a4-p1a"
PRINCIPAL = "principal-client-l9a4-p1a"
CAPACITY_ID = "capacity-l9a4-p1a-1"
SUBJECT_FP = "a" * 128
SOURCE_FP = "b" * 128


def matter(*, tenant_id: str = TENANT) -> CaseMatter:
    """Return one synthetic canonical OPEN CaseMatter."""
    return CaseMatter(
        tenant_id=tenant_id,
        case_matter_id="matter-l9a4-p1a-1",
        matter_reference="CASE-L9A4-P1A-001",
        opened_at=BASE,
        evidence_reference="matter-registration:l9a4-p1a",
    )


def party(*, source_matter: CaseMatter | None = None):
    """Return one synthetic LegalMatterParty from the exact supplied matter."""
    return register_legal_matter_party(
        matter=source_matter or matter(),
        party_id="party-l9a4-p1a-1",
        party_kind=LegalMatterPartyKind.ORGANIZATION,
        party_side=LegalMatterPartySide.CLIENT_SIDE,
        matter_role=LegalMatterPartyRole.CLIENT,
        subject_reference="organization:client-l9a4-p1a",
        subject_identity_fingerprint=SUBJECT_FP,
        display_name="Synthetic subject presentation",
        registered_at=BASE,
        source_evidence_reference="matter-party-registration:l9a4-p1a",
        source_evidence_fingerprint=SOURCE_FP,
    )


def capacity(**overrides: object) -> LegalClientActingCapacity:
    """Return one valid factory-derived acting-capacity value."""
    values: dict[str, object] = {
        "case_matter": matter(),
        "party": party(),
        "capacity_id": CAPACITY_ID,
        "principal_id": PRINCIPAL,
        "capacity_type": LegalClientActingCapacityType.AUTHORIZED_AGENT,
        "effective_from": BASE + timedelta(minutes=1),
        "effective_until": BASE + timedelta(days=30),
        "source_evidence_reference": "acting-capacity-source:l9a4-p1a",
        "source_evidence_fingerprint": "c" * 128,
    }
    values.update(overrides)
    return record_legal_client_acting_capacity(**cast(Any, values))


def assert_code(expected: str, operation: object) -> None:
    """Assert one exact stable validation code from a deferred operation."""
    with pytest.raises(LegalClientActingCapacityError) as error:
        assert callable(operation)
        operation()  # type: ignore[operator]
    assert error.value.code == expected


def test_valid_capacity_binds_all_exact_subjects_and_provenance() -> None:
    source_matter = matter()
    source_party = party(source_matter=source_matter)
    value = capacity(case_matter=source_matter, party=source_party)

    assert value.tenant_id == TENANT
    assert value.principal_id == PRINCIPAL
    assert value.case_matter_id == source_matter.case_matter_id
    assert value.matter_fingerprint == source_matter.fingerprint
    assert value.party_id == source_party.party_id
    assert value.subject_reference == source_party.subject_reference
    assert value.subject_identity_fingerprint == source_party.subject_identity_fingerprint
    assert value.capacity_type is LegalClientActingCapacityType.AUTHORIZED_AGENT
    assert value.source_evidence_reference == "acting-capacity-source:l9a4-p1a"
    assert value.source_evidence_fingerprint == "c" * 128
    assert len(value.fingerprint) == 128


def test_capacity_is_frozen_and_semantic_mutations_change_fingerprint() -> None:
    value = capacity()
    with pytest.raises(FrozenInstanceError):
        value.principal_id = "principal-other"  # type: ignore[misc]
    assert replace(value, capacity_type=LegalClientActingCapacityType.SELF, fingerprint="").fingerprint != value.fingerprint
    assert replace(value, effective_until=None, fingerprint="").fingerprint != value.fingerprint


def test_aware_utc_normalization_preserves_microseconds() -> None:
    value = capacity(
        effective_from="2026-09-26T14:00:00.123456+02:00",
        effective_until="2026-10-26T14:00:00.123456+02:00",
    )
    assert value.effective_from == BASE
    assert value.effective_from.microsecond == 123456
    assert value.effective_until == datetime(2026, 10, 26, 12, 0, 0, 123456, tzinfo=timezone.utc)
    assert value.to_dict()["effective_from"] == "2026-09-26T12:00:00.123456Z"


def test_round_trip_schema_and_fingerprint_are_exact() -> None:
    value = capacity()
    payload = value.to_dict()
    assert set(payload) == set(ACTING_CAPACITY_FIELDS)
    assert LegalClientActingCapacity.from_dict(payload) == value
    assert LegalClientActingCapacity.from_dict(payload).fingerprint == value.fingerprint


def test_factory_requires_exact_open_matter_and_matching_party() -> None:
    closed = matter().transition_to(
        CaseMatterState.CLOSED,
        evidence_reference="matter-close:l9a4-p1a",
        occurred_at=BASE + timedelta(hours=1),
    )
    assert_code("L9A4_P1A_OPEN_CASE_MATTER_REQUIRED", lambda: capacity(case_matter=closed))
    foreign_party = party(source_matter=matter(tenant_id="tenant-other"))
    assert_code("L9A4_P1A_PARTY_MATTER_MISMATCH", lambda: capacity(party=foreign_party))
    assert_code("L9A4_P1A_CASE_MATTER_REQUIRED", lambda: capacity(case_matter=object()))
    assert_code("L9A4_P1A_LEGAL_MATTER_PARTY_REQUIRED", lambda: capacity(party=object()))


@pytest.mark.parametrize(
    ("field", "value", "code"),
    [
        ("capacity_id", " capacity-1", "L9A4_P1A_CAPACITY_ID_INVALID"),
        ("principal_id", "", "L9A4_P1A_PRINCIPAL_ID_INVALID"),
        ("capacity_type", "TRUSTEE", "L9A4_P1A_CAPACITY_TYPE_INVALID"),
        ("source_evidence_reference", "", "L9A4_P1A_SOURCE_EVIDENCE_REFERENCE_INVALID"),
        ("source_evidence_fingerprint", "G" * 128, "L9A4_P1A_SOURCE_EVIDENCE_FINGERPRINT_INVALID"),
    ],
)
def test_malformed_capacity_fields_fail_closed(field: str, value: object, code: str) -> None:
    assert_code(code, lambda: capacity(**{field: value}))


def test_malformed_tenant_matter_party_subject_and_fingerprints_fail_closed() -> None:
    assert_code("L9A4_P1A_TENANT_REQUIRED", lambda: replace(capacity(), tenant_id="GLOBAL_ROOT", fingerprint=""))
    assert_code("L9A4_P1A_CASE_MATTER_ID_INVALID", lambda: replace(capacity(), case_matter_id=" matter", fingerprint=""))
    assert_code("L9A4_P1A_PARTY_ID_INVALID", lambda: replace(capacity(), party_id="", fingerprint=""))
    assert_code("L9A4_P1A_SUBJECT_REFERENCE_INVALID", lambda: replace(capacity(), subject_reference="person@example.com", fingerprint=""))
    assert_code("L9A4_P1A_SUBJECT_IDENTITY_FINGERPRINT_INVALID", lambda: replace(capacity(), subject_identity_fingerprint="A" * 128, fingerprint=""))
    assert_code("L9A4_P1A_MATTER_FINGERPRINT_INVALID", lambda: replace(capacity(), matter_fingerprint="g" * 128, fingerprint=""))


def test_naive_and_invalid_validity_chronology_fail_closed() -> None:
    assert_code("L9A4_P1A_EFFECTIVE_FROM_INVALID", lambda: capacity(effective_from=datetime(2026, 9, 26, 12, 0)))
    assert_code("L9A4_P1A_VALIDITY_INTERVAL_INVALID", lambda: capacity(effective_until=BASE))
    assert_code("L9A4_P1A_VALIDITY_INTERVAL_INVALID", lambda: capacity(effective_until=BASE - timedelta(seconds=1)))


def test_tampered_payload_or_schema_fails_closed() -> None:
    payload = capacity().to_dict()
    tampered = dict(payload)
    tampered["capacity_type"] = LegalClientActingCapacityType.SELF.value
    assert_code("L9A4_P1A_FINGERPRINT_MISMATCH", lambda: LegalClientActingCapacity.from_dict(tampered))
    assert_code("L9A4_P1A_FINGERPRINT_MISMATCH", lambda: LegalClientActingCapacity.from_dict({**payload, "fingerprint": "d" * 128}))
    assert_code("L9A4_P1A_SCHEMA_INVALID", lambda: LegalClientActingCapacity.from_dict({**payload, "email": "secret@example.test"}))
    assert_code("L9A4_P1A_SCHEMA_INVALID", lambda: LegalClientActingCapacity.from_dict({key: value for key, value in payload.items() if key != "party_id"}))


def test_self_still_requires_explicit_source_evidence() -> None:
    value = capacity(capacity_type=LegalClientActingCapacityType.SELF)
    assert value.capacity_type is LegalClientActingCapacityType.SELF
    assert value.source_evidence_reference
    assert value.source_evidence_fingerprint == "c" * 128


def test_capacity_vocabulary_is_closed_and_deliberately_not_legal_taxonomy() -> None:
    assert {item.value for item in LegalClientActingCapacityType} == {
        "SELF", "AUTHORIZED_AGENT", "REPRESENTATIVE"
    }
    assert_code("L9A4_P1A_CAPACITY_TYPE_INVALID", lambda: capacity(capacity_type="GUARDIAN"))


def test_domain_has_no_acceptance_engagement_representation_court_or_finance_fields() -> None:
    forbidden = {
        "acceptance_id", "acceptance_scope", "engagement_id", "engagement_active",
        "retainer_id", "retainer_accepted", "mandate_id", "mandate_accepted",
        "representation_id", "representation_active", "representation_scope",
        "conflict_cleared", "waiver", "ethical_wall", "court_proceeding_id",
        "court_authorized", "billing_authorized", "payment_authorized", "amount",
        "email", "phone", "address", "name", "password", "token",
    }
    assert forbidden.isdisjoint(ACTING_CAPACITY_FIELDS)
    assert forbidden.isdisjoint(capacity().to_dict())


def test_visibility_and_legal_client_role_cannot_create_capacity() -> None:
    signature = str(record_legal_client_acting_capacity)
    assert "visibility" not in signature.casefold()
    assert "role" not in signature.casefold()
    assert "subject_reference" not in signature
    assert "subject_identity_fingerprint" not in signature


def test_production_domain_has_no_io_or_forbidden_authority_imports() -> None:
    path = Path("tools/eos/legal_operations/domain/legal_client_acting_capacity.py")
    tree = ast.parse(path.read_text(encoding="utf-8"))
    imports = {
        alias.name
        for node in ast.walk(tree)
        if isinstance(node, ast.Import)
        for alias in node.names
    }
    imports.update(
        alias.name
        for node in ast.walk(tree)
        if isinstance(node, ast.ImportFrom)
        for alias in node.names
    )
    forbidden = {"pymongo", "requests", "httpx", "jwt", "bcrypt", "socket"}
    assert imports.isdisjoint(forbidden)
    source = path.read_text(encoding="utf-8")
    assert "MongoClient" not in source
    assert "LegalClientAcceptance" not in source
    assert "Engagement" not in source


# ARTIFACT: test_legal_client_acting_capacity.py
# VERSION: v1.0.0-L9A4-P1A-CLIENT-ACTING-CAPACITY-CERT
# AUTHORITY BOUNDARY: direct pure acting-capacity evidence certificate only
# TENANT POSTURE: exact canonical CaseMatter and LegalMatterParty correlation
# FAIL-CLOSED POSTURE: malformed, mismatched, naive, drifted, or tampered input rejects
# FINANCIAL EXECUTION AUTHORITY: none; Kennel EOS exclusively
# END OF WILSY OS SOVEREIGN ARTIFACT
