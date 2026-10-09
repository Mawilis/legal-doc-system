"""Direct certificate for the pure L9B4 client mandate-grant domain.

TITLE: WILSY OS Legal Client Matter Mandate Grant Certificate
VERSION: v1.0.0-L9B4-CLIENT-MATTER-MANDATE-GRANT-CERT
AUTHORITY: Wilsy OS Core Governance / Python EOS Legal Operations
EPITOME: Adversarially certify immutable client-grant evidence, exact
         canonical subject/capacity correlation, canonical mandate vocabulary,
         chronology, strict hydration, deterministic integrity and authority
         exclusions.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tests/unit/test_legal_client_matter_mandate_grant.py
COLLABORATION / OWNERSHIP: L9B4 certifies only the pure grant domain;
                            IAM, registry/currentness, firm acknowledgment,
                            mandate formation, Engagement, Representation,
                            Court, API, UI, finance and Node authorities remain
                            separate gates.
CERTIFICATION / UPDATE DATE: 2026-09-27
CHANGELOG: v1.0.0-L9B4-CLIENT-MATTER-MANDATE-GRANT-CERT covers construction,
           canonical correlation, closed capabilities, chronology, replay
           identity, hydration, tamper rejection and authority exclusions.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2; ISO 27001.
SECURITY / PRIVACY POSTURE: Synthetic opaque evidence only; no PII, secrets,
                             network, Mongo, HTTP or production records.
TENANT BOUNDARY: Every factory test is exact tenant/matter/client-party scoped.
AUTHORITY BOUNDARY: Tests grant no IAM, currentness, firm acknowledgment,
                    mandate, Engagement, Representation, Court or finance.
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
    VERSION as MANDATE_VERSION,
    LegalClientMatterMandateBreadth,
    LegalClientMatterMandateCapability,
)
from tools.eos.legal_operations.domain.legal_client_matter_mandate_grant import (
    MANDATE_GRANT_FIELDS,
    SCHEMA,
    VERSION,
    LegalClientMatterMandateGrant,
    LegalClientMatterMandateGrantError,
)
from tools.eos.legal_operations.domain.legal_matter_party import (
    LegalMatterPartyKind,
    LegalMatterPartyRole,
    LegalMatterPartySide,
    register_legal_matter_party,
)
from tools.eos.legal_operations.domain.legal_operations_lifecycle import CaseMatter


BASE = datetime(2026, 9, 27, 12, 0, 0, 123456, tzinfo=timezone.utc)
TENANT = "tenant-l9b4"
SUBJECT_FP = "a" * 128
EVIDENCE_FP = "b" * 128
SCOPE_FP = "c" * 128
AUTH_FP = "d" * 128


def matter(*, tenant_id: str = TENANT, matter_id: str = "matter-l9b4") -> CaseMatter:
    """Return synthetic canonical open matter evidence."""
    return CaseMatter(
        tenant_id=tenant_id,
        case_matter_id=matter_id,
        matter_reference="CASE-L9B4-001",
        opened_at=BASE,
        evidence_reference="matter-registration:l9b4",
    )


def party(
    *,
    source_matter: CaseMatter | None = None,
    party_side: LegalMatterPartySide = LegalMatterPartySide.CLIENT_SIDE,
    matter_role: LegalMatterPartyRole = LegalMatterPartyRole.CLIENT,
    party_id: str = "party-l9b4",
) -> Any:
    """Return synthetic matter-party evidence with controllable classification."""
    source = source_matter or matter()
    return register_legal_matter_party(
        matter=source,
        party_id=party_id,
        party_kind=LegalMatterPartyKind.ORGANIZATION,
        party_side=party_side,
        matter_role=matter_role,
        subject_reference="organization:client-l9b4",
        subject_identity_fingerprint=SUBJECT_FP,
        display_name="Synthetic client presentation",
        registered_at=BASE,
        source_evidence_reference="matter-party:l9b4",
        source_evidence_fingerprint=EVIDENCE_FP,
    )


def capacity(
    *,
    source_matter: CaseMatter | None = None,
    source_party: Any | None = None,
    principal_id: str = "principal-client-l9b4",
) -> LegalClientActingCapacity:
    """Return synthetic exact acting-capacity provenance."""
    source = source_matter or matter()
    subject = source_party or party(source_matter=source)
    return record_legal_client_acting_capacity(
        case_matter=source,
        party=subject,
        capacity_id="capacity-l9b4",
        principal_id=principal_id,
        capacity_type=LegalClientActingCapacityType.AUTHORIZED_AGENT,
        effective_from=BASE + timedelta(minutes=1),
        effective_until=BASE + timedelta(days=30),
        source_evidence_reference="acting-capacity:l9b4",
        source_evidence_fingerprint=EVIDENCE_FP,
    )


def grant(**overrides: object) -> LegalClientMatterMandateGrant:
    """Return one valid factory-derived grant evidence value."""
    source = cast(CaseMatter, overrides.pop("case_matter", matter()))
    subject = cast(Any, overrides.pop("party", None))
    if subject is None:
        subject = party(source_matter=source)
    acting = cast(Any, overrides.pop("acting_capacity", None))
    if acting is None:
        acting = capacity(source_matter=source, source_party=subject)
    values: dict[str, object] = {
        "client_grant_id": "client-grant-l9b4",
        "case_matter": source,
        "party": subject,
        "acting_capacity": acting,
        "breadth": LegalClientMatterMandateBreadth.LIMITED,
        "scope_reference": "scope-reference:l9b4",
        "scope_fingerprint": SCOPE_FP,
        "capabilities": (
            LegalClientMatterMandateCapability.SETTLEMENT_NEGOTIATION,
            LegalClientMatterMandateCapability.ADVISORY,
        ),
        "source_evidence_reference": "client-confirmation:l9b4",
        "source_evidence_fingerprint": EVIDENCE_FP,
        "authorization_evidence_reference": "iam-authorization:l9b4",
        "authorization_evidence_fingerprint": AUTH_FP,
        "occurred_at": BASE + timedelta(hours=1),
        "effective_from": BASE + timedelta(hours=2),
        "effective_until": BASE + timedelta(days=30),
        "idempotency_key": "client-grant-idempotency:l9b4",
    }
    values.update(overrides)
    return LegalClientMatterMandateGrant.from_canonical(**cast(Any, values))


def assert_code(expected: str, operation: object) -> None:
    """Assert one stable non-sensitive failure code."""
    with pytest.raises(LegalClientMatterMandateGrantError) as raised:
        assert callable(operation)
        operation()  # type: ignore[operator]
    assert raised.value.code == expected


def test_valid_construction_binds_subject_actor_capacity_and_scope() -> None:
    value = grant()
    assert value.client_grant_id == "client-grant-l9b4"
    assert value.grant_version == VERSION
    assert value.schema == SCHEMA
    assert value.tenant_id == TENANT
    assert value.case_matter_id == "matter-l9b4"
    assert value.client_party_id == "party-l9b4"
    assert value.subject_identity_fingerprint == SUBJECT_FP
    assert value.grant_actor_principal_id == "principal-client-l9b4"
    assert value.acting_capacity_id == "capacity-l9b4"
    assert value.scope_reference == "scope-reference:l9b4"
    assert value.scope_fingerprint == SCOPE_FP
    assert value.source_evidence_fingerprint == EVIDENCE_FP
    assert value.authorization_evidence_fingerprint == AUTH_FP
    assert value.capabilities == (
        LegalClientMatterMandateCapability.ADVISORY,
        LegalClientMatterMandateCapability.SETTLEMENT_NEGOTIATION,
    )


def test_breadths_and_immutable_value() -> None:
    assert grant(breadth=LegalClientMatterMandateBreadth.LIMITED).breadth is LegalClientMatterMandateBreadth.LIMITED
    assert grant(breadth=LegalClientMatterMandateBreadth.TASK_SPECIFIC).breadth is LegalClientMatterMandateBreadth.TASK_SPECIFIC
    with pytest.raises(FrozenInstanceError):
        grant().client_grant_id = "other"  # type: ignore[misc]


def test_canonical_capabilities_are_reused_sorted_non_empty_and_unique() -> None:
    first = grant(capabilities=["SETTLEMENT_NEGOTIATION", "ADVISORY"])
    second = grant(capabilities=["ADVISORY", "SETTLEMENT_NEGOTIATION"])
    assert first.capabilities == second.capabilities
    assert first.fingerprint == second.fingerprint
    assert_code("L9B4_CAPABILITIES_EMPTY", lambda: grant(capabilities=[]))
    assert_code("L9B4_CAPABILITY_DUPLICATE", lambda: grant(capabilities=["ADVISORY", "ADVISORY"]))
    assert_code("L9B4_CAPABILITY_UNKNOWN", lambda: grant(capabilities=["FILE_IN_COURT"]))


def test_chronology_is_utc_microsecond_preserving_and_bounded() -> None:
    value = grant(occurred_at=BASE.replace(tzinfo=timezone(timedelta(hours=2))))
    assert value.occurred_at.tzinfo is timezone.utc
    assert value.occurred_at.microsecond == 123456
    assert_code(
        "L9B4_EFFECTIVE_FROM_BEFORE_OCCURRED",
        lambda: grant(occurred_at=BASE + timedelta(hours=3), effective_from=BASE + timedelta(hours=2)),
    )
    assert_code("L9B4_EFFECTIVE_UNTIL_INVALID", lambda: grant(effective_until=BASE + timedelta(hours=1)))
    assert_code("L9B4_OCCURRED_AT_INVALID", lambda: grant(occurred_at=BASE.replace(tzinfo=None)))


def test_canonical_factory_rejects_cross_scope_wrong_party_and_non_client_party() -> None:
    other = matter(tenant_id="tenant-other", matter_id="matter-other")
    source = matter()
    assert_code(
        "L9B4_PARTY_MATTER_MISMATCH",
        lambda: grant(
            case_matter=source,
            party=party(source_matter=other),
            acting_capacity=capacity(
                source_matter=other,
                source_party=party(source_matter=other),
            ),
        ),
    )
    assert_code(
        "L9B4_CAPACITY_CORRELATION_MISMATCH",
        lambda: grant(case_matter=source, party=party(source_matter=source), acting_capacity=capacity(source_matter=other, source_party=party(source_matter=other))),
    )
    assert_code(
        "L9B4_CLIENT_PARTY_REQUIRED",
        lambda: grant(
            party=party(party_side=LegalMatterPartySide.ADVERSE_SIDE),
            acting_capacity=capacity(
                source_party=party(party_side=LegalMatterPartySide.ADVERSE_SIDE),
            ),
        ),
    )
    assert_code(
        "L9B4_CLIENT_PARTY_ROLE_REQUIRED",
        lambda: grant(
            party=party(matter_role=LegalMatterPartyRole.PLAINTIFF),
            acting_capacity=capacity(
                source_party=party(matter_role=LegalMatterPartyRole.PLAINTIFF),
            ),
        ),
    )


def test_capacity_actor_and_subject_provenance_are_derived_exactly() -> None:
    source = matter()
    subject = party(source_matter=source)
    actor = capacity(source_matter=source, source_party=subject, principal_id="principal-other")
    value = grant(case_matter=source, party=subject, acting_capacity=actor)
    assert value.grant_actor_principal_id == "principal-other"
    assert value.subject_identity_fingerprint == subject.subject_identity_fingerprint
    assert_code(
        "L9B4_CAPACITY_CORRELATION_MISMATCH",
        lambda: grant(acting_capacity=capacity(source_matter=matter(tenant_id="tenant-other", matter_id="matter-other"))),
    )


@pytest.mark.parametrize(
    ("field", "code"),
    [
        ("scope_fingerprint", "L9B4_SCOPE_FINGERPRINT_INVALID"),
        ("source_evidence_fingerprint", "L9B4_SOURCE_EVIDENCE_FINGERPRINT_INVALID"),
        ("authorization_evidence_fingerprint", "L9B4_AUTHORIZATION_EVIDENCE_FINGERPRINT_INVALID"),
    ],
)
def test_evidence_fingerprint_shapes_are_strict(field: str, code: str) -> None:
    assert_code(code, lambda: grant(**{field: "not-a-sha3-512"}))


def test_strict_hydration_and_deterministic_fingerprint() -> None:
    value = grant()
    payload = value.to_dict()
    hydrated = LegalClientMatterMandateGrant.from_dict(payload)
    assert hydrated == value
    assert hydrated.fingerprint == value.fingerprint
    assert_code("L9B4_SCHEMA_INVALID", lambda: LegalClientMatterMandateGrant.from_dict({**payload, "extra": "x"}))
    assert_code("L9B4_FINGERPRINT_MISMATCH", lambda: LegalClientMatterMandateGrant.from_dict({**payload, "client_grant_id": "other"}))
    assert_code("L9B4_SCHEMA_INVALID", lambda: LegalClientMatterMandateGrant.from_dict({key: item for key, item in payload.items() if key != "scope_reference"}))
    assert_code("L9B4_IDENTITY_INVALID", lambda: grant(grant_version=MANDATE_VERSION))


def test_idempotency_and_semantic_changes_are_fingerprinted() -> None:
    first = grant()
    changed = grant(idempotency_key="client-grant-idempotency:other")
    assert first.fingerprint != changed.fingerprint
    assert first.idempotency_key != changed.idempotency_key


def test_authority_exclusions_and_no_firm_acknowledgment_fields() -> None:
    payload = grant().to_dict()
    assert "firm_acknowledgment_reference" not in payload
    assert "firm_acknowledgment_fingerprint" not in payload
    assert "status" not in payload
    assert "current" not in payload
    assert "revoked_at" not in payload
    assert "superseded_by" not in payload
    assert "engagement" not in payload
    assert "representation" not in payload
    assert "court_filing" not in payload
    assert "court_appearance" not in payload
    assert "payment" not in payload
    assert "settlement_execution" not in payload
    assert LegalClientMatterMandateCapability.ADVISORY in grant().capabilities


def test_public_surface_is_pure_and_contains_no_secrets_or_placeholders() -> None:
    source = Path("tools/eos/legal_operations/domain/legal_client_matter_mandate_grant.py").read_text()
    tree = ast.parse(source)
    imported = {
        node.module
        for node in ast.walk(tree)
        if isinstance(node, ast.ImportFrom) and node.module
    }
    assert all(not name.startswith(("pymongo", "fastapi", "requests", "jwt")) for name in imported)
    assert "MongoClient" not in source
    assert "LegalClientMatterEngagement" not in source
    assert "TODO" not in source
    assert "FIXME" not in source
    assert "END OF WILSY OS SOVEREIGN ARTIFACT" in source
    assert MANDATE_GRANT_FIELDS


def test_validation_errors_do_not_echo_pii_or_evidence_body() -> None:
    secret = "private-client@example.invalid"
    with pytest.raises(LegalClientMatterMandateGrantError) as raised:
        grant(scope_reference=secret + "\n")
    assert secret not in str(raised.value)


# ARTIFACT: test_legal_client_matter_mandate_grant.py
# VERSION: v1.0.0-L9B4-CLIENT-MATTER-MANDATE-GRANT-CERT
# STATUS: Direct pure-domain certificate.
# MONGO_READS: 0
# MONGO_WRITES: 0
# END OF WILSY OS SOVEREIGN ARTIFACT
