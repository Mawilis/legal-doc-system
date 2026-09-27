"""Direct certificate for the pure L9B5 firm mandate acknowledgment domain.

TITLE: WILSY OS Legal Client Matter Mandate Acknowledgment Certificate
VERSION: v1.0.0-L9B5-FIRM-MANDATE-ACKNOWLEDGMENT-CERT
AUTHORITY: Wilsy OS Core Governance / Python EOS Legal Operations
EPITOME: Certify exact client-grant binding, closed firm decisions,
         chronology, deterministic integrity, strict hydration and authority
         exclusions for immutable acknowledgment evidence.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tests/unit/test_legal_client_matter_mandate_acknowledgment.py
COLLABORATION / OWNERSHIP: This certificate covers only the pure domain;
                            IAM, registry/currentness, mandate formation,
                            Engagement, Representation, Court, finance, API,
                            UI and Node authorities remain separate.
CERTIFICATION / UPDATE DATE: 2026-09-27
CHANGELOG: v1.0.0-L9B5-FIRM-MANDATE-ACKNOWLEDGMENT-CERT covers construction,
           exact grant lineage, all decisions, chronology, replay identity,
           strict hydration, tamper rejection and authority exclusions.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2; ISO 27001.
SECURITY / PRIVACY POSTURE: Synthetic opaque evidence only; no PII, secrets,
                             network, Mongo, HTTP or production records.
TENANT BOUNDARY: Every factory construction derives one exact tenant and
                 matter from one canonical client grant.
AUTHORITY BOUNDARY: Tests establish no currentness, Engagement,
                    Representation, Court or financial authority.
FINANCIAL AUTHORITY BOUNDARY: Kennel EOS exclusively owns financial execution.
TRANSACTION BOUNDARY: Pure in-memory unit certificate.
FAIL-CLOSED DECLARATION: Divergent, malformed, ambiguous or authority-
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
    LegalClientMatterMandateBreadth,
    LegalClientMatterMandateCapability,
)
from tools.eos.legal_operations.domain.legal_client_matter_mandate_acknowledgment import (
    ACKNOWLEDGMENT_FIELDS,
    SCHEMA,
    VERSION,
    LegalClientMatterMandateAcknowledgment,
    LegalClientMatterMandateAcknowledgmentDecision,
    LegalClientMatterMandateAcknowledgmentError,
)
from tools.eos.legal_operations.domain.legal_client_matter_mandate_grant import (
    LegalClientMatterMandateGrant,
)
from tools.eos.legal_operations.domain.legal_matter_party import (
    LegalMatterPartyKind,
    LegalMatterPartyRole,
    LegalMatterPartySide,
    register_legal_matter_party,
)
from tools.eos.legal_operations.domain.legal_operations_lifecycle import CaseMatter


BASE = datetime(2026, 9, 27, 12, 0, 0, 123456, tzinfo=timezone.utc)
TENANT = "tenant-l9b5"
SUBJECT_FP = "a" * 128
EVIDENCE_FP = "b" * 128
AUTH_FP = "c" * 128


def matter(*, tenant_id: str = TENANT, matter_id: str = "matter-l9b5") -> CaseMatter:
    """Return synthetic canonical open matter evidence."""
    return CaseMatter(
        tenant_id=tenant_id,
        case_matter_id=matter_id,
        matter_reference="CASE-L9B5-001",
        opened_at=BASE,
        evidence_reference="matter-registration:l9b5",
    )


def party(
    *,
    source_matter: CaseMatter | None = None,
    party_side: LegalMatterPartySide = LegalMatterPartySide.CLIENT_SIDE,
    matter_role: LegalMatterPartyRole = LegalMatterPartyRole.CLIENT,
) -> Any:
    """Return synthetic exact client-side matter-party evidence."""
    source = source_matter or matter()
    return register_legal_matter_party(
        matter=source,
        party_id="party-l9b5",
        party_kind=LegalMatterPartyKind.ORGANIZATION,
        party_side=party_side,
        matter_role=matter_role,
        subject_reference="organization:client-l9b5",
        subject_identity_fingerprint=SUBJECT_FP,
        display_name="Synthetic client presentation",
        registered_at=BASE,
        source_evidence_reference="matter-party:l9b5",
        source_evidence_fingerprint=EVIDENCE_FP,
    )


def capacity(*, source_matter: CaseMatter | None = None, source_party: Any | None = None) -> LegalClientActingCapacity:
    """Return synthetic client acting-capacity provenance."""
    source = source_matter or matter()
    subject = source_party or party(source_matter=source)
    return record_legal_client_acting_capacity(
        case_matter=source,
        party=subject,
        capacity_id="capacity-l9b5",
        principal_id="principal-client-l9b5",
        capacity_type=LegalClientActingCapacityType.AUTHORIZED_AGENT,
        effective_from=BASE + timedelta(minutes=1),
        effective_until=BASE + timedelta(days=30),
        source_evidence_reference="acting-capacity:l9b5",
        source_evidence_fingerprint=EVIDENCE_FP,
    )


def grant() -> LegalClientMatterMandateGrant:
    """Return one valid canonical published client-grant value."""
    source = matter()
    subject = party(source_matter=source)
    return LegalClientMatterMandateGrant.from_canonical(
        client_grant_id="client-grant-l9b5",
        case_matter=source,
        party=subject,
        acting_capacity=capacity(source_matter=source, source_party=subject),
        breadth=LegalClientMatterMandateBreadth.LIMITED,
        scope_reference="scope-reference:l9b5",
        scope_fingerprint="d" * 128,
        capabilities=(
            LegalClientMatterMandateCapability.ADVISORY,
            LegalClientMatterMandateCapability.SETTLEMENT_NEGOTIATION,
        ),
        source_evidence_reference="client-confirmation:l9b5",
        source_evidence_fingerprint=EVIDENCE_FP,
        authorization_evidence_reference="iam-authorization:l9b5",
        authorization_evidence_fingerprint=AUTH_FP,
        occurred_at=BASE + timedelta(hours=1),
        effective_from=BASE + timedelta(hours=2),
        effective_until=BASE + timedelta(days=30),
        idempotency_key="client-grant-idempotency:l9b5",
    )


def acknowledgment(**overrides: object) -> LegalClientMatterMandateAcknowledgment:
    """Return one valid exact-grant-derived acknowledgment."""
    values: dict[str, object] = {
        "client_grant": grant(),
        "acknowledgment_id": "acknowledgment-l9b5",
        "decision": LegalClientMatterMandateAcknowledgmentDecision.ACKNOWLEDGED,
        "decision_actor_principal_id": "principal-firm-l9b5",
        "authorization_evidence_reference": "firm-iam:l9b5",
        "authorization_evidence_fingerprint": "e" * 128,
        "source_evidence_reference": "firm-review:l9b5",
        "source_evidence_fingerprint": "f" * 128,
        "occurred_at": BASE + timedelta(hours=3),
        "effective_from": BASE + timedelta(hours=4),
        "idempotency_key": "firm-ack-idempotency:l9b5",
    }
    values.update(overrides)
    return LegalClientMatterMandateAcknowledgment.from_client_grant(**cast(Any, values))


def assert_code(expected: str, operation: object) -> None:
    """Assert one stable non-sensitive error code."""
    with pytest.raises(LegalClientMatterMandateAcknowledgmentError) as raised:
        assert callable(operation)
        operation()  # type: ignore[operator]
    assert raised.value.code == expected


def test_all_decisions_and_mandate_forming_value() -> None:
    acknowledged = acknowledgment()
    declined = acknowledgment(decision="DECLINED")
    review = acknowledgment(decision="REQUIRES_REVIEW")
    assert acknowledged.decision is LegalClientMatterMandateAcknowledgmentDecision.ACKNOWLEDGED
    assert declined.decision is LegalClientMatterMandateAcknowledgmentDecision.DECLINED
    assert review.decision is LegalClientMatterMandateAcknowledgmentDecision.REQUIRES_REVIEW
    assert acknowledged.is_mandate_forming is True
    assert declined.is_mandate_forming is False
    assert review.is_mandate_forming is False


def test_exact_grant_lineage_and_canonical_bindings_are_derived() -> None:
    source = grant()
    value = acknowledgment(client_grant=source)
    assert value.acknowledgment_id == "acknowledgment-l9b5"
    assert value.acknowledgment_version == VERSION
    assert value.schema == SCHEMA
    assert value.tenant_id == source.tenant_id
    assert value.case_matter_id == source.case_matter_id
    assert value.matter_fingerprint == source.matter_fingerprint
    assert value.client_party_id == source.client_party_id
    assert value.subject_identity_fingerprint == source.subject_identity_fingerprint
    assert value.client_grant_id == source.client_grant_id
    assert value.client_grant_fingerprint == source.fingerprint
    assert not hasattr(value, "capabilities")
    assert not hasattr(value, "scope_reference")


def test_actor_evidence_chronology_and_idempotency_are_bound() -> None:
    value = acknowledgment()
    assert value.decision_actor_principal_id == "principal-firm-l9b5"
    assert value.authorization_evidence_reference == "firm-iam:l9b5"
    assert value.source_evidence_reference == "firm-review:l9b5"
    assert value.occurred_at.tzinfo is timezone.utc
    assert value.occurred_at.microsecond == 123456
    assert value.effective_from > value.occurred_at
    assert value.idempotency_key == "firm-ack-idempotency:l9b5"


def test_value_is_immutable() -> None:
    with pytest.raises(FrozenInstanceError):
        acknowledgment().decision = "DECLINED"  # type: ignore[misc]


def test_fingerprint_is_deterministic_and_semantic_changes_diverge() -> None:
    first = acknowledgment()
    second = acknowledgment()
    assert first.fingerprint == second.fingerprint
    assert first.to_dict() == second.to_dict()
    assert acknowledgment(decision="DECLINED").fingerprint != first.fingerprint


def test_strict_hydration_round_trips_and_rejects_schema_or_fingerprint_tamper() -> None:
    value = acknowledgment()
    restored = LegalClientMatterMandateAcknowledgment.from_dict(value.to_dict())
    assert restored == value
    payload = value.to_dict()
    payload["unexpected"] = "value"
    assert_code("L9B5_SCHEMA_INVALID", lambda: LegalClientMatterMandateAcknowledgment.from_dict(payload))
    payload = value.to_dict()
    payload["fingerprint"] = "0" * 128
    assert_code("L9B5_FINGERPRINT_MISMATCH", lambda: LegalClientMatterMandateAcknowledgment.from_dict(payload))


def test_unknown_decision_and_malformed_evidence_reject() -> None:
    assert_code("L9B5_DECISION_INVALID", lambda: acknowledgment(decision="APPROVED"))
    assert_code("L9B5_AUTHORIZATION_EVIDENCE_FINGERPRINT_INVALID", lambda: acknowledgment(authorization_evidence_fingerprint="bad"))
    assert_code("L9B5_SOURCE_EVIDENCE_FINGERPRINT_INVALID", lambda: acknowledgment(source_evidence_fingerprint="bad"))


def test_malformed_grant_fingerprint_rejects_before_acknowledgment() -> None:
    source = grant()
    object.__setattr__(source, "fingerprint", "0" * 128)
    assert_code("L9B5_CLIENT_GRANT_INVALID", lambda: acknowledgment(client_grant=source))


def test_chronology_rejects_naive_and_reversed_values() -> None:
    assert_code("L9B5_OCCURRED_AT_INVALID", lambda: acknowledgment(occurred_at=BASE.replace(tzinfo=None)))
    assert_code(
        "L9B5_EFFECTIVE_FROM_BEFORE_OCCURRED",
        lambda: acknowledgment(effective_from=BASE + timedelta(hours=2)),
    )


def test_factory_requires_exact_grant_and_cannot_accept_scope_substitution() -> None:
    assert_code("L9B5_CLIENT_GRANT_REQUIRED", lambda: acknowledgment(client_grant=object()))
    substituted: dict[str, Any] = {
        "client_grant": grant(),
        "acknowledgment_id": "acknowledgment-l9b5",
        "decision": "ACKNOWLEDGED",
        "decision_actor_principal_id": "principal-firm-l9b5",
        "authorization_evidence_reference": "firm-iam:l9b5",
        "authorization_evidence_fingerprint": "e" * 128,
        "source_evidence_reference": "firm-review:l9b5",
        "source_evidence_fingerprint": "f" * 128,
        "occurred_at": BASE + timedelta(hours=3),
        "effective_from": BASE + timedelta(hours=4),
        "idempotency_key": "firm-ack-idempotency:l9b5",
        "scope_reference": "substituted-scope",
    }
    with pytest.raises(TypeError):
        LegalClientMatterMandateAcknowledgment.from_client_grant(**substituted)


def test_no_currentness_or_downstream_authority_fields_exist() -> None:
    fields = set(acknowledgment().to_dict())
    assert fields == set(ACKNOWLEDGMENT_FIELDS)
    assert not fields.intersection(
        {
            "status",
            "current",
            "revoked_at",
            "superseded_by",
            "engagement_id",
            "representation_id",
            "court_authority",
            "responsible_attorney_id",
            "invoice_id",
            "payment_authority",
        }
    )


def test_no_instrument_or_conflict_substitution_and_no_pii_requirement() -> None:
    value = acknowledgment()
    assert "instrument_id" not in value.to_dict()
    assert "conflict_disposition_id" not in value.to_dict()
    assert "email" not in value.to_dict()
    assert "display_name" not in value.to_dict()


def test_firm_acknowledgment_domain_has_no_forbidden_authority_imports() -> None:
    source = Path(__file__).parents[2] / "tools/eos/legal_operations/domain/legal_client_matter_mandate_acknowledgment.py"
    tree = ast.parse(source.read_text(encoding="utf-8"))
    imported = {
        node.module or ""
        for node in ast.walk(tree)
        if isinstance(node, ast.ImportFrom)
    }
    assert not any(
        any(term in module for term in ("registry", "mongo", "jwt", "http", "engagement"))
        for module in imported
    )


def test_mandate_reference_mapping_is_exact_and_no_other_authority_is_created() -> None:
    value = acknowledgment()
    mandate_projection = {
        "firm_acknowledgment_reference": value.acknowledgment_id,
        "firm_acknowledgment_fingerprint": value.fingerprint,
    }
    assert mandate_projection == {
        "firm_acknowledgment_reference": "acknowledgment-l9b5",
        "firm_acknowledgment_fingerprint": value.fingerprint,
    }
    assert value.is_mandate_forming is True


def test_public_domain_has_complete_sovereign_artifact_markers() -> None:
    source = Path(__file__).parents[2] / "tools/eos/legal_operations/domain/legal_client_matter_mandate_acknowledgment.py"
    text = source.read_text(encoding="utf-8")
    assert text.startswith('"""WILSY OS immutable firm-side mandate acknowledgment evidence domain.')
    assert "VERSION: v1.0.0-L9B5-FIRM-MANDATE-ACKNOWLEDGMENT" in text
    assert "# END OF WILSY OS SOVEREIGN ARTIFACT" in text
    for marker in ("TO" + "DO", "FIX" + "ME"):
        assert marker not in text


# ARTIFACT: test_legal_client_matter_mandate_acknowledgment.py
# VERSION: v1.0.0-L9B5-FIRM-MANDATE-ACKNOWLEDGMENT-CERT
# AUTHORITY BOUNDARY: pure acknowledgment-domain certificate only
# TENANT POSTURE: synthetic exact grant binding; no persistence
# FAIL-CLOSED POSTURE: adversarial decision, chronology, schema and fingerprint checks
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively
# END OF WILSY OS SOVEREIGN ARTIFACT
