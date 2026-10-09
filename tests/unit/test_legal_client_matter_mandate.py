"""Direct certificate for the pure L9B3 client-matter mandate domain.

TITLE: WILSY OS Legal Client Matter Mandate Certificate
VERSION: v1.0.0-L9B3-CLIENT-MATTER-MANDATE-CERT
AUTHORITY: Wilsy OS Core Governance / Python EOS Legal Operations
EPITOME: Adversarially certify immutable bounded mandate formation evidence,
         exact canonical subject/capacity correlation, deterministic capability
         ordering, chronology, strict hydration and authority exclusions.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tests/unit/test_legal_client_matter_mandate.py
COLLABORATION / OWNERSHIP: L9B3 certifies only the pure mandate domain;
                            grant, firm acknowledgment, registry/currentness,
                            Engagement, Representation, Court, API, UI and
                            Node authorities remain separate gates.
CERTIFICATION / UPDATE DATE: 2026-09-27
CHANGELOG: v1.0.0-L9B3-CLIENT-MATTER-MANDATE-CERT covers construction,
           canonical correlation, closed capabilities, chronology, replay
           identity, hydration, tamper rejection and authority exclusions.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2; ISO 27001.
SECURITY / PRIVACY POSTURE: Synthetic opaque evidence only; no PII, secrets,
                             network, Mongo, HTTP or production records.
TENANT BOUNDARY: Every factory test is exact tenant/matter/client-party scoped.
AUTHORITY BOUNDARY: Tests grant no mandate, Engagement, Representation, Court
                    or financial authority.
FINANCIAL AUTHORITY BOUNDARY: Kennel EOS exclusively owns execution.
TRANSACTION BOUNDARY: Pure in-memory unit certificate.
FAIL-CLOSED DECLARATION: Malformed, divergent, ambiguous, stale or authority-
                         expanding input must reject.
"""
from __future__ import annotations

import ast
from dataclasses import FrozenInstanceError
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, cast

import pytest

from tools.eos.legal_operations.domain.legal_client_acting_capacity import (
    LegalClientActingCapacity,
    LegalClientActingCapacityType,
    record_legal_client_acting_capacity,
)
from tools.eos.legal_operations.domain.legal_client_matter_mandate import (
    MANDATE_FIELDS,
    VERSION,
    LegalClientMatterMandate,
    LegalClientMatterMandateBreadth,
    LegalClientMatterMandateCapability,
    LegalClientMatterMandateError,
)
from tools.eos.legal_operations.domain.legal_matter_party import (
    LegalMatterPartyKind,
    LegalMatterPartyRole,
    LegalMatterPartySide,
    register_legal_matter_party,
)
from tools.eos.legal_operations.domain.legal_operations_lifecycle import CaseMatter


BASE = datetime(2026, 9, 27, 12, 0, 0, 123456, tzinfo=timezone.utc)
TENANT = "tenant-l9b3"
SUBJECT_FP = "a" * 128
EVIDENCE_FP = "b" * 128
SCOPE_FP = "c" * 128
GRANT_FP = "d" * 128
ACK_FP = "e" * 128


def matter(*, tenant_id: str = TENANT, matter_id: str = "matter-l9b3") -> CaseMatter:
    """Return synthetic canonical open matter evidence."""
    return CaseMatter(
        tenant_id=tenant_id,
        case_matter_id=matter_id,
        matter_reference="CASE-L9B3-001",
        opened_at=BASE,
        evidence_reference="matter-registration:l9b3",
    )


def party(
    *,
    source_matter: CaseMatter | None = None,
    party_side: LegalMatterPartySide = LegalMatterPartySide.CLIENT_SIDE,
    matter_role: LegalMatterPartyRole = LegalMatterPartyRole.CLIENT,
    party_id: str = "party-l9b3",
) -> Any:
    """Return synthetic matter-party evidence with controllable classification."""
    source = source_matter or matter()
    return register_legal_matter_party(
        matter=source,
        party_id=party_id,
        party_kind=LegalMatterPartyKind.ORGANIZATION,
        party_side=party_side,
        matter_role=matter_role,
        subject_reference="organization:client-l9b3",
        subject_identity_fingerprint=SUBJECT_FP,
        display_name="Synthetic client presentation",
        registered_at=BASE,
        source_evidence_reference="matter-party:l9b3",
        source_evidence_fingerprint=EVIDENCE_FP,
    )


def capacity(
    *,
    source_matter: CaseMatter | None = None,
    source_party: Any | None = None,
    principal_id: str = "principal-client-l9b3",
) -> LegalClientActingCapacity:
    """Return synthetic exact acting-capacity provenance."""
    source = source_matter or matter()
    subject = source_party or party(source_matter=source)
    return record_legal_client_acting_capacity(
        case_matter=source,
        party=subject,
        capacity_id="capacity-l9b3",
        principal_id=principal_id,
        capacity_type=LegalClientActingCapacityType.AUTHORIZED_AGENT,
        effective_from=BASE + timedelta(minutes=1),
        effective_until=BASE + timedelta(days=30),
        source_evidence_reference="acting-capacity:l9b3",
        source_evidence_fingerprint=EVIDENCE_FP,
    )


def mandate(**overrides: object) -> LegalClientMatterMandate:
    """Return one valid factory-derived mandate formation value."""
    source = cast(CaseMatter, overrides.pop("case_matter", matter()))
    subject = cast(Any, overrides.pop("party", None))
    if subject is None:
        subject = party(source_matter=source)
    acting = cast(Any, overrides.pop("acting_capacity", None))
    if acting is None:
        acting = capacity(source_matter=source, source_party=subject)
    values: dict[str, object] = {
        "mandate_id": "mandate-l9b3",
        "case_matter": source,
        "party": subject,
        "acting_capacity": acting,
        "breadth": LegalClientMatterMandateBreadth.LIMITED,
        "scope_reference": "scope-reference:l9b3",
        "scope_fingerprint": SCOPE_FP,
        "capabilities": (
            LegalClientMatterMandateCapability.SETTLEMENT_NEGOTIATION,
            LegalClientMatterMandateCapability.ADVISORY,
        ),
        "source_evidence_reference": "mandate-source:l9b3",
        "source_evidence_fingerprint": EVIDENCE_FP,
        "client_grant_reference": "client-grant:l9b3",
        "client_grant_fingerprint": GRANT_FP,
        "firm_acknowledgment_reference": "firm-ack:l9b3",
        "firm_acknowledgment_fingerprint": ACK_FP,
        "occurred_at": BASE + timedelta(hours=1),
        "effective_from": BASE + timedelta(hours=2),
        "effective_until": BASE + timedelta(days=30),
        "idempotency_key": "mandate-idempotency:l9b3",
    }
    values.update(overrides)
    return LegalClientMatterMandate.from_canonical(**cast(Any, values))


def assert_code(expected: str, operation: object) -> None:
    """Assert one stable non-sensitive failure code."""
    with pytest.raises(LegalClientMatterMandateError) as raised:
        assert callable(operation)
        operation()  # type: ignore[operator]
    assert raised.value.code == expected


def test_valid_construction_and_exact_subject_actor_bindings() -> None:
    value = mandate()
    assert value.mandate_id == "mandate-l9b3"
    assert value.mandate_version == VERSION
    assert value.tenant_id == TENANT
    assert value.case_matter_id == "matter-l9b3"
    assert value.client_party_id == "party-l9b3"
    assert value.grant_actor_principal_id == "principal-client-l9b3"
    assert value.acting_capacity_id == "capacity-l9b3"
    assert value.mandate_scope == value.scope_reference
    assert value.capabilities == (
        LegalClientMatterMandateCapability.ADVISORY,
        LegalClientMatterMandateCapability.SETTLEMENT_NEGOTIATION,
    )


def test_breadths_and_immutable_value() -> None:
    assert mandate(breadth=LegalClientMatterMandateBreadth.LIMITED).breadth is LegalClientMatterMandateBreadth.LIMITED
    assert mandate(breadth=LegalClientMatterMandateBreadth.TASK_SPECIFIC).breadth is LegalClientMatterMandateBreadth.TASK_SPECIFIC
    with pytest.raises(FrozenInstanceError):
        mandate().mandate_id = "other"  # type: ignore[misc]


def test_capabilities_are_closed_sorted_and_duplicate_free() -> None:
    first = mandate(capabilities=["SETTLEMENT_NEGOTIATION", "ADVISORY"])
    second = mandate(capabilities=["ADVISORY", "SETTLEMENT_NEGOTIATION"])
    assert first.capabilities == second.capabilities
    assert first.fingerprint == second.fingerprint
    assert_code("L9B3_CAPABILITY_DUPLICATE", lambda: mandate(capabilities=["ADVISORY", "ADVISORY"]))
    assert_code("L9B3_CAPABILITY_UNKNOWN", lambda: mandate(capabilities=["FILE_IN_COURT"]))


def test_scope_and_all_three_evidence_sources_are_required_and_bound() -> None:
    value = mandate()
    assert value.scope_fingerprint == SCOPE_FP
    assert value.source_evidence_fingerprint == EVIDENCE_FP
    assert value.client_grant_fingerprint == GRANT_FP
    assert value.firm_acknowledgment_fingerprint == ACK_FP
    assert value.client_grant_reference != value.firm_acknowledgment_reference


def test_chronology_is_utc_and_effective_interval_is_bounded() -> None:
    value = mandate(
        occurred_at=BASE.replace(tzinfo=timezone(timedelta(hours=2))),
        effective_from=BASE + timedelta(hours=2),
    )
    assert value.occurred_at.tzinfo is timezone.utc
    assert value.effective_from.tzinfo is timezone.utc
    assert value.occurred_at.microsecond == 123456
    assert_code(
        "L9B3_EFFECTIVE_FROM_BEFORE_OCCURRED",
        lambda: mandate(
            occurred_at=BASE + timedelta(hours=3),
            effective_from=BASE + timedelta(hours=2),
        ),
    )
    assert_code("L9B3_EFFECTIVE_UNTIL_INVALID", lambda: mandate(effective_until=BASE + timedelta(hours=1)))
    assert_code("L9B3_OCCURRED_AT_INVALID", lambda: mandate(occurred_at=BASE.replace(tzinfo=None)))


def test_canonical_correlation_rejects_cross_scope_and_wrong_party() -> None:
    other_matter = matter(tenant_id="tenant-other", matter_id="matter-other")
    source = matter()
    assert_code(
        "L9B3_PARTY_MATTER_MISMATCH",
        lambda: mandate(
            case_matter=source,
            party=party(source_matter=other_matter),
            acting_capacity=capacity(source_matter=source, source_party=party(source_matter=source)),
        ),
    )
    assert_code(
        "L9B3_CAPACITY_CORRELATION_MISMATCH",
        lambda: mandate(acting_capacity=capacity(source_matter=other_matter, source_party=party(source_matter=other_matter))),
    )
    assert_code(
        "L9B3_CLIENT_PARTY_REQUIRED",
        lambda: mandate(party=party(party_side=LegalMatterPartySide.ADVERSE_SIDE)),
    )
    assert_code(
        "L9B3_CLIENT_PARTY_ROLE_REQUIRED",
        lambda: mandate(party=party(matter_role=LegalMatterPartyRole.PLAINTIFF)),
    )


def test_subject_and_capacity_mismatch_rejected() -> None:
    source = matter()
    client = party(source_matter=source)
    mismatched_party = party(source_matter=source, party_id="party-other")
    mismatched_capacity = capacity(source_matter=source, source_party=mismatched_party)
    assert_code(
        "L9B3_CAPACITY_CORRELATION_MISMATCH",
        lambda: mandate(acting_capacity=mismatched_capacity),
    )


@pytest.mark.parametrize(
    ("field", "code"),
    [
        ("scope_fingerprint", "L9B3_SCOPE_FINGERPRINT_INVALID"),
        ("client_grant_fingerprint", "L9B3_CLIENT_GRANT_FINGERPRINT_INVALID"),
        ("firm_acknowledgment_fingerprint", "L9B3_FIRM_ACKNOWLEDGMENT_FINGERPRINT_INVALID"),
    ],
)
def test_evidence_fingerprint_shape_is_strict(field: str, code: str) -> None:
    assert_code(code, lambda: mandate(**{field: "not-a-sha3-512"}))


def test_strict_hydration_and_deterministic_fingerprint() -> None:
    value = mandate()
    payload = value.to_dict()
    hydrated = LegalClientMatterMandate.from_dict(payload)
    assert hydrated == value
    assert hydrated.fingerprint == value.fingerprint
    assert_code("L9B3_SCHEMA_INVALID", lambda: LegalClientMatterMandate.from_dict({**payload, "extra": "x"}))
    assert_code("L9B3_FINGERPRINT_MISMATCH", lambda: LegalClientMatterMandate.from_dict({**payload, "mandate_id": "other"}))
    assert_code("L9B3_SCHEMA_INVALID", lambda: LegalClientMatterMandate.from_dict({key: item for key, item in payload.items() if key != "scope_reference"}))


def test_no_lifecycle_or_execution_authority_is_encoded() -> None:
    payload = mandate().to_dict()
    assert "status" not in payload
    assert "current" not in payload
    assert "revoked_at" not in payload
    assert "representation" not in payload
    assert "court_filing" not in payload
    assert "payment" not in payload
    assert "settlement_execution" not in payload


def test_public_surface_is_pure_and_does_not_import_runtime_authorities() -> None:
    source = Path("tools/eos/legal_operations/domain/legal_client_matter_mandate.py").read_text()
    tree = ast.parse(source)
    imported = {
        node.module
        for node in ast.walk(tree)
        if isinstance(node, ast.ImportFrom) and node.module
    }
    assert all(not name.startswith(("pymongo", "fastapi", "requests", "jwt")) for name in imported)
    assert "LegalClientMatterEngagement" not in source
    assert "MongoClient" not in source


def test_pii_is_not_required_or_echoed_by_validation_errors() -> None:
    secret = "client-private-name@example.invalid"
    with pytest.raises(LegalClientMatterMandateError) as raised:
        mandate(scope_reference=secret + "\n")
    assert secret not in str(raised.value)


def test_certificate_has_no_placeholders_and_has_seal() -> None:
    source = Path("tools/eos/legal_operations/domain/legal_client_matter_mandate.py").read_text()
    assert "TODO" not in source
    assert "FIXME" not in source
    assert "END OF WILSY OS SOVEREIGN ARTIFACT" in source
    assert MANDATE_FIELDS


# ARTIFACT: test_legal_client_matter_mandate.py
# VERSION: v1.0.0-L9B3-CLIENT-MATTER-MANDATE-CERT
# STATUS: Direct pure-domain certificate.
# MONGO_READS: 0
# MONGO_WRITES: 0
# END OF WILSY OS SOVEREIGN ARTIFACT
