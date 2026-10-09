"""Direct certificate for the pure L9C1 Engagement firm-decision domain.

TITLE: WILSY OS Legal Client Matter Engagement Firm Decision Certificate
VERSION: v1.0.0-L9C1-ENGAGEMENT-FIRM-DECISION-CERT
AUTHORITY: Wilsy OS Core Governance / Python EOS Legal Operations
EPITOME: Prove the bounded immutable firm-decision contract without wiring
         Engagement formation, IAM, persistence, conflict currentness or finance.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tests/unit/test_legal_client_matter_engagement_firm_decision.py
COLLABORATION / OWNERSHIP: This certificate owns only direct pure-domain
                            evidence; published Engagement, acceptance,
                            mandate, conflict and IAM artifacts remain read-only.
CERTIFICATION / UPDATE DATE: 2026-09-27
CHANGELOG: v1.0.0-L9C1-ENGAGEMENT-FIRM-DECISION-CERT proves vocabulary,
           exact canonical binding, chronology, authorization provenance,
           strict hydration, deterministic integrity and authority exclusions.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2; ISO 27001.
SECURITY / PRIVACY POSTURE: Synthetic opaque identifiers and fingerprints only;
                             no credentials, tokens, PII or network access.
TENANT BOUNDARY: Exact canonical OPEN matter and client party correlation.
AUTHORITY BOUNDARY: Certificate evidence only; no Engagement or IAM authority.
FINANCIAL AUTHORITY BOUNDARY: None; Kennel EOS exclusively owns execution.
TRANSACTION BOUNDARY: Pure in-memory tests; no database or transaction.
FAIL-CLOSED DECLARATION: Malformed, unknown, cross-scope, naive, tampered or
                         authority-expanding inputs must reject.
"""
from __future__ import annotations

import ast
from dataclasses import FrozenInstanceError, replace
from datetime import datetime, timedelta, timezone
import inspect
from pathlib import Path
from typing import Any, cast

import pytest

from tools.eos.legal_operations.domain.legal_client_matter_engagement_firm_decision import (
    FIRM_DECISION_FIELDS,
    SCHEMA,
    VERSION,
    LegalClientMatterEngagementFirmDecision,
    LegalClientMatterEngagementFirmDecisionError,
    LegalClientMatterEngagementFirmDecisionType,
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
TENANT = "tenant-l9c1"
MATTER_FP = "a" * 128
SUBJECT_FP = "b" * 128
AUTH_FP = "c" * 128
SOURCE_FP = "d" * 128


def matter(*, tenant_id: str = TENANT, matter_id: str = "matter-l9c1") -> CaseMatter:
    """Return one synthetic canonical OPEN CaseMatter."""
    return CaseMatter(
        tenant_id=tenant_id,
        case_matter_id=matter_id,
        matter_reference="CASE-L9C1-001",
        opened_at=BASE,
        evidence_reference="matter:l9c1",
    )


def party(
    *,
    source_matter: CaseMatter | None = None,
    side: LegalMatterPartySide = LegalMatterPartySide.CLIENT_SIDE,
    role: LegalMatterPartyRole = LegalMatterPartyRole.CLIENT,
    party_id: str = "party-l9c1",
) -> Any:
    """Return one synthetic matter party with controllable classification."""
    source = source_matter or matter()
    return register_legal_matter_party(
        matter=source,
        party_id=party_id,
        party_kind=LegalMatterPartyKind.ORGANIZATION,
        party_side=side,
        matter_role=role,
        subject_reference="organization:client-l9c1",
        subject_identity_fingerprint=SUBJECT_FP,
        display_name="Synthetic client presentation",
        registered_at=BASE + timedelta(minutes=1),
        source_evidence_reference="party:l9c1",
        source_evidence_fingerprint=SOURCE_FP,
    )


def decision(**overrides: object) -> LegalClientMatterEngagementFirmDecision:
    """Return one valid canonical firm decision."""
    source = cast(CaseMatter, overrides.pop("case_matter", matter()))
    dependency_source = (
        source
        if isinstance(source, CaseMatter) and source.state is CaseMatterState.OPEN
        else matter()
    )
    subject = overrides.pop("party", party(source_matter=dependency_source))
    values: dict[str, object] = {
        "decision_id": "decision-l9c1",
        "case_matter": source,
        "party": subject,
        "decision": LegalClientMatterEngagementFirmDecisionType.ACCEPTED,
        "decision_actor_principal_id": "principal-firm-l9c1",
        "authorization_evidence_reference": "iam-decision:l9c1",
        "authorization_evidence_fingerprint": AUTH_FP,
        "source_evidence_reference": "firm-decision:l9c1",
        "source_evidence_fingerprint": SOURCE_FP,
        "occurred_at": BASE + timedelta(minutes=2),
        "effective_from": BASE + timedelta(minutes=3),
        "idempotency_key": "decision-idempotency:l9c1",
    }
    values.update(overrides)
    return LegalClientMatterEngagementFirmDecision.from_canonical(
        **cast(Any, values)
    )


def assert_code(expected: str, operation: object) -> None:
    """Assert one stable non-sensitive failure code."""
    with pytest.raises(LegalClientMatterEngagementFirmDecisionError) as raised:
        assert callable(operation)
        operation()  # type: ignore[operator]
    assert raised.value.code == expected


def test_version_schema_and_exact_vocabulary() -> None:
    assert VERSION == "v1.0.0-L9C1-ENGAGEMENT-FIRM-DECISION"
    assert SCHEMA == "WILSY-LEGAL-CLIENT-MATTER-ENGAGEMENT-FIRM-DECISION/V1"
    assert {item.value for item in LegalClientMatterEngagementFirmDecisionType} == {
        "ACCEPTED",
        "DECLINED",
        "REQUIRES_REVIEW",
    }
    assert decision().decision is LegalClientMatterEngagementFirmDecisionType.ACCEPTED


@pytest.mark.parametrize(
    ("value", "forming"),
    [
        (LegalClientMatterEngagementFirmDecisionType.ACCEPTED, True),
        (LegalClientMatterEngagementFirmDecisionType.DECLINED, False),
        (LegalClientMatterEngagementFirmDecisionType.REQUIRES_REVIEW, False),
    ],
)
def test_only_accepted_is_positive(value: object, forming: bool) -> None:
    result = decision(decision=value)
    assert result.is_engagement_forming is forming
    assert result.decision is value


def test_exact_binding_and_authorization_provenance() -> None:
    source = matter()
    subject = party(source_matter=source)
    result = decision(case_matter=source, party=subject)
    assert result.tenant_id == TENANT
    assert result.case_matter_id == source.case_matter_id
    assert result.matter_fingerprint == source.fingerprint
    assert result.client_party_id == subject.party_id
    assert result.subject_reference == subject.subject_reference
    assert result.subject_identity_fingerprint == SUBJECT_FP
    assert result.decision_actor_principal_id == "principal-firm-l9c1"
    assert result.authorization_evidence_reference == "iam-decision:l9c1"
    assert result.authorization_evidence_fingerprint == AUTH_FP


def test_immutable_and_repeated_fingerprint_is_deterministic() -> None:
    first = decision()
    second = decision()
    assert first == second
    assert first.fingerprint == second.fingerprint
    assert len(first.fingerprint) == 128
    assert first.fingerprint == first.fingerprint.lower()
    with pytest.raises(FrozenInstanceError):
        first.decision_id = "other"  # type: ignore[misc]
    assert replace(first, decision_id="other", fingerprint="").fingerprint != first.fingerprint


def test_exact_round_trip_and_strict_schema() -> None:
    value = decision()
    payload = value.to_dict()
    assert set(payload) == set(FIRM_DECISION_FIELDS)
    assert LegalClientMatterEngagementFirmDecision.from_dict(payload) == value
    assert_code("L9C1_SCHEMA_INVALID", lambda: LegalClientMatterEngagementFirmDecision.from_dict({**payload, "extra": "x"}))
    assert_code("L9C1_SCHEMA_INVALID", lambda: LegalClientMatterEngagementFirmDecision.from_dict({key: item for key, item in payload.items() if key != "decision"}))
    assert_code("L9C1_FINGERPRINT_MISMATCH", lambda: LegalClientMatterEngagementFirmDecision.from_dict({**payload, "fingerprint": "f" * 128}))


@pytest.mark.parametrize(
    ("field", "value", "code"),
    [
        ("tenant_id", "", "L9C1_TENANT_ID_INVALID"),
        ("case_matter_id", " matter", "L9C1_CASE_MATTER_ID_INVALID"),
        ("matter_fingerprint", "A" * 128, "L9C1_MATTER_FINGERPRINT_INVALID"),
        ("client_party_id", "", "L9C1_CLIENT_PARTY_ID_INVALID"),
        ("subject_reference", "raw-subject", "L9C1_SUBJECT_REFERENCE_INVALID"),
        ("subject_identity_fingerprint", "G" * 128, "L9C1_SUBJECT_IDENTITY_FINGERPRINT_INVALID"),
        ("decision_actor_principal_id", " actor", "L9C1_DECISION_ACTOR_PRINCIPAL_ID_INVALID"),
        ("authorization_evidence_reference", "", "L9C1_AUTHORIZATION_EVIDENCE_REFERENCE_INVALID"),
        ("authorization_evidence_fingerprint", "G" * 128, "L9C1_AUTHORIZATION_EVIDENCE_FINGERPRINT_INVALID"),
        ("source_evidence_reference", "", "L9C1_SOURCE_EVIDENCE_REFERENCE_INVALID"),
        ("source_evidence_fingerprint", "G" * 128, "L9C1_SOURCE_EVIDENCE_FINGERPRINT_INVALID"),
        ("idempotency_key", "", "L9C1_IDEMPOTENCY_KEY_INVALID"),
    ],
)
def test_malformed_fields_fail_closed(field: str, value: object, code: str) -> None:
    assert_code(code, lambda: replace(decision(), **{field: value}, fingerprint=""))


def test_unknown_decision_and_identity_version_fail_closed() -> None:
    assert_code("L9C1_DECISION_INVALID", lambda: replace(decision(), decision="MAYBE", fingerprint=""))
    assert_code("L9C1_IDENTITY_INVALID", lambda: replace(decision(), decision_version="other", fingerprint=""))
    assert_code("L9C1_IDENTITY_INVALID", lambda: replace(decision(), schema="other", fingerprint=""))


def test_aware_utc_chronology_and_no_expiry() -> None:
    value = decision(effective_from="2026-09-27T14:03:00.123456+02:00")
    assert value.effective_from == BASE + timedelta(minutes=3)
    assert value.effective_from.microsecond == 123456
    assert value.to_dict()["effective_from"] == "2026-09-27T12:03:00.123456Z"
    assert_code("L9C1_OCCURRED_AT_INVALID", lambda: replace(decision(), occurred_at=BASE.replace(tzinfo=None), fingerprint=""))
    assert_code("L9C1_EFFECTIVE_FROM_INVALID", lambda: replace(decision(), effective_from="not-time", fingerprint=""))
    assert_code("L9C1_EFFECTIVE_FROM_BEFORE_OCCURRED", lambda: decision(effective_from=BASE + timedelta(minutes=1)))


def test_canonical_requires_open_client_matter_party() -> None:
    closed = matter().transition_to(
        CaseMatterState.CLOSED,
        evidence_reference="matter-close:l9c1",
        occurred_at=BASE + timedelta(hours=1),
    )
    assert_code("L9C1_OPEN_CASE_MATTER_REQUIRED", lambda: decision(case_matter=closed))
    assert_code("L9C1_CLIENT_PARTY_REQUIRED", lambda: decision(party=party(side=LegalMatterPartySide.ADVERSE_SIDE)))
    assert_code("L9C1_CLIENT_PARTY_ROLE_REQUIRED", lambda: decision(party=party(role=LegalMatterPartyRole.WITNESS)))
    assert_code("L9C1_PARTY_REQUIRED", lambda: decision(party=object()))
    assert_code("L9C1_CASE_MATTER_REQUIRED", lambda: decision(case_matter=object()))


def test_cross_scope_matter_party_and_subject_bindings_fail_closed() -> None:
    assert_code(
        "L9C1_PARTY_MATTER_MISMATCH",
        lambda: decision(party=party(source_matter=matter(tenant_id="tenant-other"))),
    )
    assert_code(
        "L9C1_PARTY_MATTER_MISMATCH",
        lambda: decision(party=party(source_matter=matter(matter_id="matter-other"))),
    )
    foreign_subject = party()
    assert_code(
        "L9C1_SUBJECT_REFERENCE_INVALID",
        lambda: replace(decision(), subject_reference="other:subject", fingerprint=""),
    )
    assert foreign_subject.subject_reference == "organization:client-l9c1"


def test_authorization_provenance_is_carried_not_evaluated() -> None:
    value = decision()
    assert value.authorization_evidence_reference
    assert value.authorization_evidence_fingerprint == AUTH_FP
    assert not hasattr(value, "authorized")
    assert not hasattr(value, "role")
    assert value.is_engagement_forming is True


def test_decision_alone_does_not_form_engagement() -> None:
    source = Path("tools/eos/legal_operations/domain/legal_client_matter_engagement_firm_decision.py").read_text()
    assert "LegalClientMatterEngagement" not in source.replace("LegalClientMatterEngagementFirmDecision", "")
    assert "from tools.eos.legal_operations.registry" not in source
    assert "def form_engagement" not in source
    assert "def transition" not in source


def test_authority_exclusions_and_no_wall_clock() -> None:
    source = Path("tools/eos/legal_operations/domain/legal_client_matter_engagement_firm_decision.py").read_text()
    tree = ast.parse(source)
    imported = {
        node.module
        for node in ast.walk(tree)
        if isinstance(node, ast.ImportFrom) and node.module
    }
    forbidden = ("pymongo", "fastapi", "jwt", "requests", "registry", "iam", "engagement", "representation", "court", "billing", "payment")
    assert not any(any(token in module.lower() for token in forbidden) for module in imported)
    assert "datetime.now" not in source
    assert "utcnow" not in source
    assert "time.time" not in source
    assert "TODO" not in source
    assert "FIXME" not in source


def test_published_engagement_domain_accepts_decision_provenance_shape() -> None:
    value = decision()
    from tools.eos.legal_operations.domain.legal_client_matter_engagement import (
        LegalClientMatterEngagement,
    )

    parameters = inspect.signature(LegalClientMatterEngagement.from_canonical).parameters
    assert {"firm_decision_id", "decision_actor_principal_id", "firm_decision_fingerprint"} <= set(parameters)
    assert value.decision_id
    assert value.decision_actor_principal_id
    assert len(value.fingerprint) == 128


def test_version_identity_and_public_surface_are_complete() -> None:
    source = Path("tools/eos/legal_operations/domain/legal_client_matter_engagement_firm_decision.py").read_text()
    assert source.count(VERSION) >= 3
    assert "END OF WILSY OS SOVEREIGN ARTIFACT" in source
    assert "__all__" in source
    assert FIRM_DECISION_FIELDS.isdisjoint({"password", "token", "email", "representation_id", "court_authority"})


# ARTIFACT: test_legal_client_matter_engagement_firm_decision.py
# VERSION: v1.0.0-L9C1-ENGAGEMENT-FIRM-DECISION-CERT
# AUTHORITY BOUNDARY: pure immutable Engagement decision certificate only
# TENANT POSTURE: exact canonical matter/client-party correlation
# FAIL-CLOSED POSTURE: malformed, drifted, cross-scope or authority-expanding input rejects
# FINANCIAL EXECUTION AUTHORITY: none; Kennel EOS exclusively
# END OF WILSY OS SOVEREIGN ARTIFACT
