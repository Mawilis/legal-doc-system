"""Direct certificate for immutable L9B1 Engagement formation evidence.

TITLE: WILSY OS Legal Client Matter Engagement Certificate
VERSION: v1.0.0-L9B1-CLIENT-MATTER-ENGAGEMENT-CERT
AUTHORITY: Wilsy OS Core Governance / Python EOS Legal Operations
EPITOME: Adversarially certify exact client-party formation bindings,
         prerequisite provenance, UTC chronology, strict hydration and
         deterministic SHA3-512 integrity without creating a registry,
         lifecycle, Representation, Court or financial authority.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tests/unit/test_legal_client_matter_engagement.py
COLLABORATION / OWNERSHIP: L9B1 certifies only the pure Engagement domain;
                            mandate, conflict-disposition, firm IAM,
                            registry, orchestration and all runtime surfaces
                            remain explicitly deferred prerequisite gates.
CERTIFICATION / UPDATE DATE: 2026-09-27
CHANGELOG: v1.0.0-L9B1-CLIENT-MATTER-ENGAGEMENT-CERT proves valid immutable
           formation, exact canonical correlation, opaque prerequisite
           references, chronology, hydration, tamper rejection and authority
           exclusions.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2; ISO 27001.
SECURITY / PRIVACY POSTURE: Synthetic opaque identifiers and fingerprints only;
                             no credentials, tokens, raw PII, network or
                             production records.
TENANT BOUNDARY: Every factory assertion is exact tenant/matter/client-party
                 scoped; no identity or authority is inferred by the test.
AUTHORITY BOUNDARY: Certificate evidence only; passing tests grant no runtime
                    Engagement, Representation, Court or financial authority.
FINANCIAL AUTHORITY BOUNDARY: Kennel EOS exclusively owns execution.
TRANSACTION BOUNDARY: Pure in-memory unit tests; no database, HTTP, IAM,
                      filesystem mutation or network access.
FAIL-CLOSED DECLARATION: Malformed, mismatched, naive, tampered or
                         authority-expanding input must reject.
"""
from __future__ import annotations

import ast
from dataclasses import FrozenInstanceError, replace
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, cast

import pytest

from tools.eos.legal_operations.domain.legal_client_acceptance import (
    LegalClientAcceptance,
    record_legal_client_acceptance,
)
from tools.eos.legal_operations.domain.legal_client_acting_capacity import (
    LegalClientActingCapacity,
    LegalClientActingCapacityType,
    record_legal_client_acting_capacity,
)
from tools.eos.legal_operations.domain.legal_client_matter_acceptance_instrument import (
    LegalClientMatterAcceptanceInstrument,
    record_legal_client_matter_acceptance_instrument,
)
from tools.eos.legal_operations.domain.legal_client_matter_engagement import (
    ENGAGEMENT_FIELDS,
    VERSION,
    LegalClientMatterEngagement,
    LegalClientMatterEngagementError,
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


BASE = datetime(2026, 9, 27, 12, 0, 0, 123456, tzinfo=timezone.utc)
TENANT = "tenant-l9b1"
SUBJECT_FP = "a" * 128
EVIDENCE_FP = "b" * 128
MANDATE_FP = "c" * 128
CONFLICT_FP = "d" * 128
DECISION_FP = "e" * 128
AUTH_FP = "f" * 128
SOURCE_FP = "0" * 128


def matter(*, tenant_id: str = TENANT, matter_id: str = "matter-l9b1") -> CaseMatter:
    """Return synthetic canonical OPEN CaseMatter evidence."""
    return CaseMatter(
        tenant_id=tenant_id,
        case_matter_id=matter_id,
        matter_reference="CASE-L9B1-001",
        opened_at=BASE,
        evidence_reference="matter-registration:l9b1",
    )


def party(
    *,
    source_matter: CaseMatter | None = None,
    party_side: LegalMatterPartySide = LegalMatterPartySide.CLIENT_SIDE,
    matter_role: LegalMatterPartyRole = LegalMatterPartyRole.CLIENT,
    party_id: str = "party-l9b1",
) -> Any:
    """Return synthetic matter-party evidence with controllable classification."""
    source = source_matter or matter()
    return register_legal_matter_party(
        matter=source,
        party_id=party_id,
        party_kind=LegalMatterPartyKind.ORGANIZATION,
        party_side=party_side,
        matter_role=matter_role,
        subject_reference="organization:client-l9b1",
        subject_identity_fingerprint=SUBJECT_FP,
        display_name="Synthetic client presentation",
        registered_at=BASE,
        source_evidence_reference="matter-party:l9b1",
        source_evidence_fingerprint=EVIDENCE_FP,
    )


def acting_capacity(
    *,
    source_matter: CaseMatter | None = None,
    source_party: Any | None = None,
    principal_id: str = "principal-client-l9b1",
) -> LegalClientActingCapacity:
    """Return synthetic exact acting-capacity provenance."""
    source = source_matter or matter()
    subject = source_party or party(source_matter=source)
    return record_legal_client_acting_capacity(
        case_matter=source,
        party=subject,
        capacity_id="capacity-l9b1",
        principal_id=principal_id,
        capacity_type=LegalClientActingCapacityType.AUTHORIZED_AGENT,
        effective_from=BASE + timedelta(minutes=1),
        effective_until=BASE + timedelta(days=30),
        source_evidence_reference="acting-capacity:l9b1",
        source_evidence_fingerprint=EVIDENCE_FP,
    )


def acceptance(
    *,
    source_matter: CaseMatter | None = None,
    source_party: Any | None = None,
    actor_principal_id: str = "principal-client-l9b1",
) -> LegalClientAcceptance:
    """Return synthetic exact client-acceptance provenance."""
    source = source_matter or matter()
    subject = source_party or party(source_matter=source)
    return record_legal_client_acceptance(
        case_matter=source,
        acceptance_id="acceptance-l9b1",
        party_id=subject.party_id,
        subject_reference=subject.subject_reference,
        subject_identity_fingerprint=subject.subject_identity_fingerprint,
        acceptance_scope="client-information-review:v1",
        actor_principal_id=actor_principal_id,
        accepted_at=BASE + timedelta(minutes=2),
        source_evidence_reference="client-acceptance:l9b1",
        source_evidence_fingerprint=EVIDENCE_FP,
    )


def instrument(*, source_matter: CaseMatter | None = None) -> LegalClientMatterAcceptanceInstrument:
    """Return synthetic exact review-instrument provenance."""
    return record_legal_client_matter_acceptance_instrument(
        case_matter=source_matter or matter(),
        instrument_id="instrument-l9b1",
        version="1.0.0",
        instrument_kind="CLIENT_REVIEW_TERMS",
        title="Synthetic reviewed instrument",
        review_scope="client-information-review:v1",
        content_reference="content:l9b1",
        content_fingerprint=EVIDENCE_FP,
        created_at=BASE,
        effective_from=BASE,
        approval_evidence_reference="approval:l9b1",
        approval_evidence_fingerprint=EVIDENCE_FP,
    )


def engagement(**overrides: object) -> LegalClientMatterEngagement:
    """Return one valid factory-derived Engagement formation value."""
    source = cast(CaseMatter, overrides.pop("case_matter", matter()))
    dependency_source = source if source.state is CaseMatterState.OPEN else matter()
    subject = overrides.pop("party", party(source_matter=dependency_source))
    capacity = overrides.pop(
        "acting_capacity",
        acting_capacity(source_matter=dependency_source, source_party=party(source_matter=dependency_source)),
    )
    accepted = overrides.pop(
        "client_acceptance",
        acceptance(source_matter=dependency_source, source_party=party(source_matter=dependency_source)),
    )
    reviewed = overrides.pop("instrument", instrument(source_matter=dependency_source))
    values: dict[str, object] = {
        "engagement_id": "engagement-l9b1",
        "case_matter": source,
        "party": subject,
        "acting_capacity": capacity,
        "client_acceptance": accepted,
        "instrument": reviewed,
        "mandate_id": "mandate-l9b1",
        "mandate_scope": "scope-reference:l9b1",
        "mandate_fingerprint": MANDATE_FP,
        "conflict_disposition_id": "conflict-disposition-l9b1",
        "conflict_disposition_fingerprint": CONFLICT_FP,
        "firm_decision_id": "firm-decision-l9b1",
        "decision_actor_principal_id": "principal-firm-l9b1",
        "firm_decision_fingerprint": DECISION_FP,
        "authorization_evidence_reference": "firm-authorization:l9b1",
        "authorization_evidence_fingerprint": AUTH_FP,
        "source_evidence_reference": "engagement-formation:l9b1",
        "source_evidence_fingerprint": SOURCE_FP,
        "effective_from": BASE + timedelta(minutes=3),
        "idempotency_key": "engagement-idempotency:l9b1",
    }
    values.update(overrides)
    return LegalClientMatterEngagement.from_canonical(**cast(Any, values))


def assert_code(expected: str, operation: object) -> None:
    """Assert one stable non-sensitive failure code."""
    with pytest.raises(LegalClientMatterEngagementError) as raised:
        assert callable(operation)
        operation()  # type: ignore[operator]
    assert raised.value.code == expected


def test_valid_formation_binds_exact_subject_and_all_provenance() -> None:
    source = matter()
    subject = party(source_matter=source)
    value = engagement(case_matter=source, party=subject)
    assert value.engagement_id == "engagement-l9b1"
    assert value.tenant_id == TENANT
    assert value.case_matter_id == source.case_matter_id
    assert value.matter_fingerprint == source.fingerprint
    assert value.client_party_id == subject.party_id
    assert value.subject_reference == subject.subject_reference
    assert value.subject_identity_fingerprint == SUBJECT_FP
    assert value.acting_capacity_id == "capacity-l9b1"
    assert value.client_acceptance_id == "acceptance-l9b1"
    assert value.instrument_id == "instrument-l9b1"
    assert value.version == "1.0.0"
    assert value.mandate_id == "mandate-l9b1"
    assert value.mandate_scope == "scope-reference:l9b1"
    assert value.conflict_disposition_id == "conflict-disposition-l9b1"
    assert value.firm_decision_id == "firm-decision-l9b1"
    assert value.decision_actor_principal_id == "principal-firm-l9b1"
    assert value.authorization_evidence_reference == "firm-authorization:l9b1"
    assert value.source_evidence_reference == "engagement-formation:l9b1"
    assert value.idempotency_key == "engagement-idempotency:l9b1"
    assert len(value.fingerprint) == 128


def test_value_is_frozen_and_semantic_change_changes_fingerprint() -> None:
    value = engagement()
    with pytest.raises(FrozenInstanceError):
        value.mandate_id = "other"  # type: ignore[misc]
    assert replace(value, mandate_scope="other-scope", fingerprint="").fingerprint != value.fingerprint


def test_utc_effectiveness_preserves_microseconds() -> None:
    value = engagement(effective_from="2026-09-27T14:03:00.123456+02:00")
    assert value.effective_from == BASE + timedelta(minutes=3)
    assert value.effective_from.microsecond == 123456
    assert value.to_dict()["effective_from"] == "2026-09-27T12:03:00.123456Z"


def test_exact_round_trip_and_deterministic_fingerprint() -> None:
    value = engagement()
    payload = value.to_dict()
    assert set(payload) == set(ENGAGEMENT_FIELDS)
    assert LegalClientMatterEngagement.from_dict(payload) == value
    assert LegalClientMatterEngagement.from_dict(payload).fingerprint == value.fingerprint


def test_factory_derives_canonical_bindings_instead_of_reasserted_values() -> None:
    source = matter()
    subject = party(source_matter=source)
    value = engagement(case_matter=source, party=subject)
    assert value.tenant_id == source.tenant_id
    assert value.case_matter_id == source.case_matter_id
    assert value.client_party_id == subject.party_id
    assert value.subject_identity_fingerprint == subject.subject_identity_fingerprint
    assert value.instrument_fingerprint == instrument(source_matter=source).fingerprint


def test_effectiveness_requires_all_known_prerequisite_chronology() -> None:
    assert_code("L9B1_EFFECTIVE_FROM_INVALID", lambda: engagement(effective_from=BASE))
    assert_code(
        "L9B1_CAPACITY_NOT_VALID_AT_EFFECTIVE",
        lambda: engagement(effective_from=BASE + timedelta(days=31)),
    )


def test_closed_matter_and_wrong_canonical_types_fail_closed() -> None:
    closed = matter().transition_to(
        CaseMatterState.CLOSED,
        evidence_reference="matter-close:l9b1",
        occurred_at=BASE + timedelta(hours=1),
    )
    assert_code("L9B1_OPEN_CASE_MATTER_REQUIRED", lambda: engagement(case_matter=closed))
    assert_code("L9B1_PARTY_REQUIRED", lambda: engagement(party=object()))
    assert_code("L9B1_INSTRUMENT_REQUIRED", lambda: engagement(instrument=object()))


@pytest.mark.parametrize(
    ("field", "value", "code"),
    [
        ("engagement_id", " engagement", "L9B1_ENGAGEMENT_ID_INVALID"),
        ("mandate_id", "", "L9B1_MANDATE_ID_INVALID"),
        ("mandate_scope", "", "L9B1_MANDATE_SCOPE_INVALID"),
        ("mandate_fingerprint", "A" * 128, "L9B1_MANDATE_FINGERPRINT_INVALID"),
        ("conflict_disposition_id", "", "L9B1_CONFLICT_DISPOSITION_ID_INVALID"),
        ("conflict_disposition_fingerprint", "G" * 128, "L9B1_CONFLICT_DISPOSITION_FINGERPRINT_INVALID"),
        ("firm_decision_id", "", "L9B1_FIRM_DECISION_ID_INVALID"),
        ("decision_actor_principal_id", " actor", "L9B1_DECISION_ACTOR_PRINCIPAL_ID_INVALID"),
        ("firm_decision_fingerprint", "G" * 128, "L9B1_FIRM_DECISION_FINGERPRINT_INVALID"),
        ("authorization_evidence_reference", "", "L9B1_AUTHORIZATION_EVIDENCE_REFERENCE_INVALID"),
        ("authorization_evidence_fingerprint", "G" * 128, "L9B1_AUTHORIZATION_EVIDENCE_FINGERPRINT_INVALID"),
        ("source_evidence_reference", "", "L9B1_SOURCE_EVIDENCE_REFERENCE_INVALID"),
        ("source_evidence_fingerprint", "G" * 128, "L9B1_SOURCE_EVIDENCE_FINGERPRINT_INVALID"),
        ("idempotency_key", "", "L9B1_IDEMPOTENCY_KEY_INVALID"),
    ],
)
def test_malformed_opaque_evidence_fails_closed(field: str, value: object, code: str) -> None:
    assert_code(code, lambda: engagement(**{field: value}))


def test_malformed_subject_fingerprints_and_pseudo_tenant_fail_closed() -> None:
    assert_code("L9B1_TENANT_REQUIRED", lambda: replace(engagement(), tenant_id="GLOBAL", fingerprint=""))
    assert_code("L9B1_SUBJECT_IDENTITY_FINGERPRINT_INVALID", lambda: replace(engagement(), subject_identity_fingerprint="A" * 128, fingerprint=""))
    assert_code("L9B1_MATTER_FINGERPRINT_INVALID", lambda: replace(engagement(), matter_fingerprint="G" * 128, fingerprint=""))


def test_naive_effective_from_is_rejected() -> None:
    assert_code("L9B1_EFFECTIVE_FROM_INVALID", lambda: engagement(effective_from=datetime(2026, 9, 27, 12, 3)))


def test_non_client_side_party_is_rejected() -> None:
    adverse = party(party_side=LegalMatterPartySide.ADVERSE_SIDE)
    assert_code("L9B1_CLIENT_PARTY_REQUIRED", lambda: engagement(party=adverse))


def test_non_client_role_is_rejected() -> None:
    witness = party(matter_role=LegalMatterPartyRole.WITNESS)
    assert_code("L9B1_CLIENT_PARTY_ROLE_REQUIRED", lambda: engagement(party=witness))


def test_cross_tenant_and_cross_matter_are_rejected() -> None:
    foreign_matter = matter(tenant_id="tenant-other")
    assert_code(
        "L9B1_PARTY_MATTER_MISMATCH",
        lambda: engagement(
            party=party(source_matter=foreign_matter),
            acting_capacity=acting_capacity(),
            client_acceptance=acceptance(),
        ),
    )
    foreign_case = matter(matter_id="matter-other")
    assert_code(
        "L9B1_PARTY_MATTER_MISMATCH",
        lambda: engagement(
            party=party(source_matter=foreign_case),
            acting_capacity=acting_capacity(),
            client_acceptance=acceptance(),
        ),
    )


def test_acting_capacity_wrong_party_or_matter_is_rejected() -> None:
    source = matter()
    other_party = party(source_matter=source, party_id="party-other")
    capacity = acting_capacity(source_matter=source, source_party=other_party)
    assert_code("L9B1_CAPACITY_CORRELATION_MISMATCH", lambda: engagement(acting_capacity=capacity))
    foreign_capacity = acting_capacity(source_matter=matter(tenant_id="tenant-other"))
    assert_code("L9B1_CAPACITY_CORRELATION_MISMATCH", lambda: engagement(acting_capacity=foreign_capacity))


def test_acceptance_wrong_party_matter_or_actor_is_rejected() -> None:
    source = matter()
    other_party = party(source_matter=source, party_id="party-other")
    wrong_party_acceptance = acceptance(source_matter=source, source_party=other_party)
    assert_code("L9B1_CLIENT_ACCEPTANCE_CORRELATION_MISMATCH", lambda: engagement(client_acceptance=wrong_party_acceptance))
    foreign_acceptance = acceptance(source_matter=matter(tenant_id="tenant-other"))
    assert_code("L9B1_CLIENT_ACCEPTANCE_CORRELATION_MISMATCH", lambda: engagement(client_acceptance=foreign_acceptance))
    wrong_actor = acceptance(actor_principal_id="principal-other")
    assert_code("L9B1_ACCEPTANCE_ACTOR_CAPACITY_MISMATCH", lambda: engagement(client_acceptance=wrong_actor))


def test_instrument_mismatch_is_rejected() -> None:
    foreign_instrument = instrument(source_matter=matter(tenant_id="tenant-other"))
    assert_code("L9B1_INSTRUMENT_CORRELATION_MISMATCH", lambda: engagement(instrument=foreign_instrument))


def test_content_fingerprint_tampering_is_rejected() -> None:
    payload = engagement().to_dict()
    payload["content_fingerprint"] = "1" * 128
    assert_code("L9B1_FINGERPRINT_MISMATCH", lambda: LegalClientMatterEngagement.from_dict(payload))


def test_firm_decision_and_authorization_are_distinct_opaque_bindings() -> None:
    value = engagement()
    assert value.firm_decision_id != value.authorization_evidence_reference
    assert value.firm_decision_fingerprint != value.authorization_evidence_fingerprint


def test_mandate_and_conflict_are_references_not_embedded_authority() -> None:
    payload = engagement().to_dict()
    assert payload["mandate_scope"] == "scope-reference:l9b1"
    assert "conflict_outcome" not in payload
    assert "conflict_cleared" not in payload
    assert "waiver" not in payload


def test_schema_tampering_and_extra_fields_fail_closed() -> None:
    payload = engagement().to_dict()
    assert_code("L9B1_SCHEMA_INVALID", lambda: LegalClientMatterEngagement.from_dict({**payload, "email": "pii@example.test"}))
    assert_code("L9B1_SCHEMA_INVALID", lambda: LegalClientMatterEngagement.from_dict({key: value for key, value in payload.items() if key != "mandate_id"}))
    assert_code("L9B1_IDENTITY_INVALID", lambda: replace(engagement(), engagement_version="other", fingerprint=""))


def test_fingerprint_tampering_fails_closed() -> None:
    payload = engagement().to_dict()
    assert_code("L9B1_FINGERPRINT_MISMATCH", lambda: LegalClientMatterEngagement.from_dict({**payload, "fingerprint": "1" * 128}))


def test_no_lifecycle_representation_court_or_financial_authority_fields() -> None:
    forbidden = {
        "status", "lifecycle_status", "active", "suspended", "terminated",
        "closed", "withdrawn", "representation_id", "representation_scope",
        "court_proceeding_id", "court_authority", "power_of_attorney",
        "billing_authorized", "payment_authorized", "settlement_authorized",
        "fee", "invoice_id", "email", "phone", "address", "name", "token",
    }
    payload = engagement().to_dict()
    assert forbidden.isdisjoint(ENGAGEMENT_FIELDS)
    assert forbidden.isdisjoint(payload)


def test_no_pii_is_required_and_no_external_authority_is_imported() -> None:
    assert "email" not in ENGAGEMENT_FIELDS
    assert "password" not in ENGAGEMENT_FIELDS
    source = Path("tools/eos/legal_operations/domain/legal_client_matter_engagement.py").read_text()
    tree = ast.parse(source)
    imported = {
        node.module
        for node in ast.walk(tree)
        if isinstance(node, ast.ImportFrom) and node.module
    }
    assert not any(module.startswith(("pymongo", "fastapi", "jwt", "requests")) for module in imported)


def test_version_identity_is_single_and_complete() -> None:
    source = Path("tools/eos/legal_operations/domain/legal_client_matter_engagement.py").read_text()
    assert source.count(VERSION) >= 3
    assert "TODO" not in source
    assert "FIXME" not in source


# ARTIFACT: test_legal_client_matter_engagement.py
# VERSION: v1.0.0-L9B1-CLIENT-MATTER-ENGAGEMENT-CERT
# AUTHORITY BOUNDARY: pure immutable Engagement formation evidence certificate
# TENANT POSTURE: exact canonical matter/client-party prerequisite correlation
# FAIL-CLOSED POSTURE: malformed, drifted, cross-scope or authority-expanding input rejects
# FINANCIAL EXECUTION AUTHORITY: none; Kennel EOS exclusively
# END OF WILSY OS SOVEREIGN ARTIFACT
