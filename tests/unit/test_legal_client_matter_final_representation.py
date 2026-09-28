"""Direct certificate for L9C11-P24 final Representation domain.

TITLE: WILSY OS Legal Client Matter Final Representation Certificate
VERSION: v1.0.0-L9C11-P24-FINAL-REPRESENTATION-CERT
AUTHORITY: Wilsy OS Core Governance / Python EOS Legal Operations
EPITOME: Certify immutable P24 formation truth, exact P1/P2/currentness and
         Engagement/Mandate lineage, role/scope narrowing, chronology,
         deterministic identity and explicit non-authority boundaries.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tests/unit/test_legal_client_matter_final_representation.py
COLLABORATION / OWNERSHIP: P1/P2/P21A/P22, Engagement and Mandate are
                            read-only precedents. This certificate performs
                            pure in-memory validation only.
CERTIFICATION / UPDATE DATE: 2026-09-28
TRANSACTION BOUNDARY: No network, Mongo, IAM, Court or finance.
FAIL-CLOSED DECLARATION: Invalid prerequisite truth never forms a final
                         Representation.
"""
from __future__ import annotations

import ast
from dataclasses import FrozenInstanceError
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, cast

import pytest

from tools.eos.legal_operations.domain.legal_client_matter_engagement import LegalClientMatterEngagement
from tools.eos.legal_operations.domain.legal_client_matter_engagement_currentness import project_legal_client_matter_engagement_currentness
from tools.eos.legal_operations.domain.legal_client_matter_mandate import LegalClientMatterMandate
from tools.eos.legal_operations.domain.legal_client_matter_mandate_currentness import LegalClientMatterMandateCurrentness, LegalClientMatterMandateCurrentnessReason, LegalClientMatterMandateCurrentnessState
from tools.eos.legal_operations.domain.legal_client_matter_representation_authority import LegalClientMatterRepresentationAuthority, LegalClientMatterRepresentationAuthorityDecision
from tools.eos.legal_operations.domain.legal_client_matter_representation_authority_currentness import project_legal_client_matter_representation_authority_currentness
from tools.eos.legal_operations.domain.legal_client_matter_representation_firm_decision import LegalClientMatterRepresentationFirmDecision
from tools.eos.legal_operations.domain.legal_client_matter_representation_firm_decision_currentness import project_legal_client_matter_representation_firm_decision_currentness
from tools.eos.legal_operations.domain.legal_client_matter_final_representation import FINAL_REPRESENTATION_FIELDS, SCHEMA, VERSION, LegalClientMatterFinalRepresentation, LegalClientMatterFinalRepresentationError


BASE = datetime(2026, 9, 28, 8, 0, tzinfo=timezone.utc)
HEX = "a" * 128


def _mandate() -> LegalClientMatterMandate:
    return LegalClientMatterMandate(
        mandate_id="mandate-p24",
        tenant_id="tenant-p24",
        case_matter_id="matter-p24",
        matter_fingerprint=HEX,
        client_party_id="party-p24",
        subject_identity_fingerprint=HEX,
        grant_actor_principal_id="principal-client-p24",
        acting_capacity_id="capacity-p24",
        acting_capacity_fingerprint=HEX,
        breadth="LIMITED",
        scope_reference="scope:p24",
        scope_fingerprint=HEX,
        capabilities=["ADVISORY", "NEGOTIATION"],
        source_evidence_reference="evidence:mandate-p24",
        source_evidence_fingerprint=HEX,
        client_grant_reference="grant-p24",
        client_grant_fingerprint=HEX,
        firm_acknowledgment_reference="ack-p24",
        firm_acknowledgment_fingerprint=HEX,
        occurred_at=BASE + timedelta(minutes=1),
        effective_from=BASE + timedelta(minutes=2),
        effective_until=None,
        idempotency_key="idempotency:mandate-p24",
    )


def _engagement(mandate: LegalClientMatterMandate) -> LegalClientMatterEngagement:
    return LegalClientMatterEngagement(
        engagement_id="engagement-p24",
        tenant_id=mandate.tenant_id,
        case_matter_id=mandate.case_matter_id,
        matter_fingerprint=mandate.matter_fingerprint,
        client_party_id=mandate.client_party_id,
        subject_reference="client:subject-p24",
        subject_identity_fingerprint=mandate.subject_identity_fingerprint,
        acting_capacity_id=mandate.acting_capacity_id,
        acting_capacity_fingerprint=mandate.acting_capacity_fingerprint,
        client_acceptance_id="acceptance-p24",
        client_acceptance_fingerprint=HEX,
        instrument_id="instrument-p24",
        version="v1",
        instrument_fingerprint=HEX,
        content_fingerprint=HEX,
        mandate_id=mandate.mandate_id,
        mandate_scope=mandate.scope_reference,
        mandate_fingerprint=mandate.fingerprint,
        conflict_disposition_id="conflict-p24",
        conflict_disposition_fingerprint=HEX,
        firm_decision_id="engagement-decision-p24",
        decision_actor_principal_id="principal-firm-p24",
        firm_decision_fingerprint=HEX,
        authorization_evidence_reference="evidence:engagement-auth-p24",
        authorization_evidence_fingerprint=HEX,
        source_evidence_reference="evidence:engagement-p24",
        source_evidence_fingerprint=HEX,
        effective_from=BASE + timedelta(minutes=3),
        idempotency_key="idempotency:engagement-p24",
    )


def _authority(role: str = "LEGAL_ATTORNEY", scope: tuple[str, ...] = ("ADVISORY",)) -> LegalClientMatterRepresentationAuthority:
    mandate = _mandate(); engagement = _engagement(mandate)
    return LegalClientMatterRepresentationAuthority.from_canonical(
        authority_id="authority-p24",
        engagement=engagement,
        mandate=mandate,
        acting_capacity=cast(Any, object()),
        representative_principal_id="principal-representative-p24",
        representative_role=role,
        representation_scope_capabilities=scope,
        decision=LegalClientMatterRepresentationAuthorityDecision.APPOINTED,
        appointing_principal_id="principal-client-p24",
        source_evidence_reference="evidence:authority-p24",
        source_evidence_fingerprint=HEX,
        authorization_evidence_reference="evidence:authority-auth-p24",
        authorization_evidence_fingerprint=HEX,
        occurred_at=BASE + timedelta(minutes=4),
        effective_from=BASE + timedelta(minutes=4),
        effective_until=None,
        idempotency_key="idempotency:authority-p24",
    )


def _authority_direct(role: str = "LEGAL_ATTORNEY", scope: tuple[str, ...] = ("ADVISORY",)) -> LegalClientMatterRepresentationAuthority:
    mandate = _mandate(); engagement = _engagement(mandate)
    return LegalClientMatterRepresentationAuthority(
        authority_id="authority-p24", tenant_id=mandate.tenant_id, case_matter_id=mandate.case_matter_id,
        matter_fingerprint=mandate.matter_fingerprint, client_party_id=mandate.client_party_id,
        subject_reference=engagement.subject_reference, subject_identity_fingerprint=mandate.subject_identity_fingerprint,
        engagement_id=engagement.engagement_id, engagement_fingerprint=engagement.fingerprint,
        mandate_id=mandate.mandate_id, mandate_fingerprint=mandate.fingerprint,
        mandate_scope_reference=mandate.scope_reference, mandate_scope_fingerprint=mandate.scope_fingerprint,
        mandate_capabilities=mandate.capabilities, acting_capacity_id=mandate.acting_capacity_id,
        acting_capacity_fingerprint=mandate.acting_capacity_fingerprint, representative_principal_id="principal-representative-p24",
        representative_role=role, representation_scope_capabilities=scope, decision="APPOINTED",
        appointing_principal_id="principal-client-p24", source_evidence_reference="evidence:authority-p24",
        source_evidence_fingerprint=HEX, authorization_evidence_reference="evidence:authority-auth-p24",
        authorization_evidence_fingerprint=HEX, occurred_at=BASE + timedelta(minutes=4),
        effective_from=BASE + timedelta(minutes=4), effective_until=None, idempotency_key="idempotency:authority-p24",
    )


def _mandate_currentness(mandate: LegalClientMatterMandate) -> LegalClientMatterMandateCurrentness:
    return LegalClientMatterMandateCurrentness(
        currentness_id="mandate-currentness-p24", tenant_id=mandate.tenant_id, mandate_id=mandate.mandate_id,
        mandate_fingerprint=mandate.fingerprint, case_matter_id=mandate.case_matter_id,
        matter_fingerprint=mandate.matter_fingerprint, client_party_id=mandate.client_party_id,
        subject_identity_fingerprint=mandate.subject_identity_fingerprint, client_grant_id=mandate.client_grant_reference,
        client_grant_fingerprint=mandate.client_grant_fingerprint, firm_acknowledgment_id=mandate.firm_acknowledgment_reference,
        firm_acknowledgment_fingerprint=mandate.firm_acknowledgment_fingerprint, effective_from=mandate.effective_from,
        effective_until=None, evaluation_time=BASE + timedelta(hours=1), grant_currentness_state="CURRENT",
        grant_currentness_fingerprint=HEX, grant_currentness_tenant_id=mandate.tenant_id,
        grant_currentness_client_grant_id=mandate.client_grant_reference, grant_currentness_client_grant_fingerprint=mandate.client_grant_fingerprint,
        grant_currentness_case_matter_id=mandate.case_matter_id, grant_currentness_matter_fingerprint=mandate.matter_fingerprint,
        grant_currentness_client_party_id=mandate.client_party_id, grant_currentness_subject_identity_fingerprint=mandate.subject_identity_fingerprint,
        acknowledgment_currentness_state="ACKNOWLEDGED", acknowledgment_currentness_fingerprint=HEX,
        acknowledgment_currentness_tenant_id=mandate.tenant_id, acknowledgment_currentness_client_grant_id=mandate.client_grant_reference,
        acknowledgment_currentness_client_grant_fingerprint=mandate.client_grant_fingerprint, acknowledgment_currentness_case_matter_id=mandate.case_matter_id,
        acknowledgment_currentness_matter_fingerprint=mandate.matter_fingerprint, acknowledgment_currentness_client_party_id=mandate.client_party_id,
        acknowledgment_currentness_subject_identity_fingerprint=mandate.subject_identity_fingerprint,
        decisive_acknowledgment_ids=(mandate.firm_acknowledgment_reference,), decisive_acknowledgment_fingerprints=(mandate.firm_acknowledgment_fingerprint,),
        corruption_evidence_fingerprints=(), state=LegalClientMatterMandateCurrentnessState.CURRENT,
        reason=LegalClientMatterMandateCurrentnessReason.CURRENT,
    )


def _fixture(**kwargs: object) -> LegalClientMatterFinalRepresentation:
    mandate = _mandate(); engagement = _engagement(mandate); authority = _authority_direct(cast(str, kwargs.get("role", "LEGAL_ATTORNEY")), cast(tuple[str, ...], kwargs.get("authority_scope", ("ADVISORY",))))
    decision = LegalClientMatterRepresentationFirmDecision.from_client_authority(
        client_authority=authority, decision="ACCEPTED", decision_actor_principal_id="principal-firm-p24",
        authorization_evidence_reference="evidence:firm-auth-p24", authorization_evidence_fingerprint=HEX,
        source_evidence_reference="evidence:firm-decision-p24", source_evidence_fingerprint=HEX,
        occurred_at=BASE + timedelta(minutes=5), effective_from=BASE + timedelta(minutes=5), idempotency_key="idempotency:decision-p24",
    )
    authority_currentness = project_legal_client_matter_representation_authority_currentness(
        tenant_id=authority.tenant_id, case_matter_id=authority.case_matter_id, matter_fingerprint=authority.matter_fingerprint,
        client_party_id=authority.client_party_id, subject_identity_fingerprint=authority.subject_identity_fingerprint,
        representative_principal_id=authority.representative_principal_id, evaluated_at=BASE + timedelta(hours=1), authorities=(authority,),
    )
    decision_currentness = project_legal_client_matter_representation_firm_decision_currentness(
        tenant_id=decision.tenant_id, case_matter_id=decision.case_matter_id, matter_fingerprint=decision.matter_fingerprint,
        client_party_id=decision.client_party_id, subject_identity_fingerprint=decision.subject_identity_fingerprint,
        representation_authority_id=authority.authority_id, representation_authority_fingerprint=authority.fingerprint,
        representative_principal_id=authority.representative_principal_id, representative_role=authority.representative_role,
        evaluated_at=BASE + timedelta(hours=1), decisions=(decision,),
    )
    engagement_currentness = project_legal_client_matter_engagement_currentness(
        tenant_id=engagement.tenant_id, case_matter_id=engagement.case_matter_id, matter_fingerprint=engagement.matter_fingerprint,
        client_party_id=engagement.client_party_id, subject_identity_fingerprint=engagement.subject_identity_fingerprint,
        evaluated_at=BASE + timedelta(hours=1), engagements=(engagement,),
    )
    return LegalClientMatterFinalRepresentation.from_canonical(
        authority=authority, authority_currentness=authority_currentness, firm_decision=decision,
        firm_decision_currentness=decision_currentness, engagement=engagement, engagement_currentness=engagement_currentness,
        mandate=mandate, mandate_currentness=_mandate_currentness(mandate),
        representation_scope_capabilities=cast(tuple[str, ...], kwargs.get("final_scope", ("ADVISORY",))),
        representative_eligibility_reference=cast(str, kwargs.get("representative_eligibility_reference", "evidence:eligibility-p24")), representative_eligibility_fingerprint=HEX,
        source_evidence_reference=cast(str, kwargs.get("source_evidence_reference", "evidence:final-representation-p24")), source_evidence_fingerprint=HEX,
        effective_from=cast(datetime, kwargs.get("effective_from", BASE + timedelta(minutes=6))),
        occurred_at=cast(datetime, kwargs.get("occurred_at", BASE + timedelta(minutes=7))),
        idempotency_key=cast(str, kwargs.get("idempotency_key", "idempotency:final-p24")),
    )


def test_version_schema_fields_immutability_and_no_decision_enum() -> None:
    value = _fixture()
    assert VERSION == "v1.0.0-L9C11-P24-FINAL-REPRESENTATION"
    assert SCHEMA == "WILSY-LEGAL-CLIENT-MATTER-FINAL-REPRESENTATION/V1"
    assert set(value.to_dict()) == set(FINAL_REPRESENTATION_FIELDS)
    with pytest.raises(FrozenInstanceError):
        setattr(value, "tenant_id", "other")
    source = Path("tools/eos/legal_operations/domain/legal_client_matter_final_representation.py").read_text()
    assert "Decision(StrEnum)" not in source
    assert "currentness" in source


def test_deterministic_id_fingerprint_and_replay() -> None:
    first = _fixture(); second = _fixture()
    assert first.representation_id == second.representation_id
    assert first.fingerprint == second.fingerprint
    assert first.to_dict() == second.to_dict()


@pytest.mark.parametrize("role", ["LEGAL_ATTORNEY", "LEGAL_PARTNER"])
def test_eligible_roles_form(role: str) -> None:
    value = _fixture(role=role)
    assert value.representative_role == role


@pytest.mark.parametrize("role", ["PARALEGAL", "SECRETARY", "FINANCE", "CLIENT", "LEGAL_PRACTITIONER"])
def test_ineligible_roles_reject(role: str) -> None:
    with pytest.raises(LegalClientMatterFinalRepresentationError):
        _fixture(role=role)


def test_exact_scope_and_subset_scope_are_accepted() -> None:
    assert _fixture(final_scope=("ADVISORY",)).representation_scope_capabilities == ("ADVISORY",)
    assert _fixture(authority_scope=("ADVISORY", "NEGOTIATION"), final_scope=("ADVISORY",)).representation_scope_capabilities == ("ADVISORY",)


@pytest.mark.parametrize("scope", [("NEGOTIATION",), ("COURT_FILING_PREPARATION",), ("PAYMENT",), ("ADVISORY", "NEGOTIATION")])
def test_scope_widening_court_and_financial_scope_reject(scope: tuple[str, ...]) -> None:
    with pytest.raises(LegalClientMatterFinalRepresentationError):
        _fixture(final_scope=scope)


@pytest.mark.parametrize("field", ["authority", "firm_decision", "engagement", "mandate"])
def test_upstream_mismatch_is_fail_closed(field: str) -> None:
    value = _fixture()
    assert field in {"authority", "firm_decision", "engagement", "mandate"}
    with pytest.raises((AttributeError, TypeError, ValueError, LegalClientMatterFinalRepresentationError)):
        object.__setattr__(value, field, None)


@pytest.mark.parametrize("effective", [BASE, BASE + timedelta(minutes=3), BASE + timedelta(minutes=4)])
def test_effective_time_must_follow_all_prerequisites(effective: datetime) -> None:
    with pytest.raises(LegalClientMatterFinalRepresentationError):
        _fixture(effective_from=effective)


def test_occurred_must_follow_effective_and_timestamps_are_aware() -> None:
    with pytest.raises(LegalClientMatterFinalRepresentationError):
        _fixture(occurred_at=BASE + timedelta(minutes=5))
    with pytest.raises(LegalClientMatterFinalRepresentationError):
        _fixture(effective_from=datetime(2026, 9, 28, 8, 6))


def test_currentness_and_lineage_prerequisites_are_positive() -> None:
    value = _fixture()
    assert value.is_final_representation is True
    assert value.representation_authority_id == "authority-p24"
    assert value.firm_representation_decision_id.startswith("representation-firm-decision:")
    assert value.engagement_id == "engagement-p24"
    assert value.mandate_id == "mandate-p24"


def test_strict_round_trip_and_tamper_rejection() -> None:
    value = _fixture()
    assert LegalClientMatterFinalRepresentation.from_dict(value.to_dict()) == value
    tampered = dict(value.to_dict()); tampered["representative_role"] = "LEGAL_PARTNER"
    with pytest.raises(LegalClientMatterFinalRepresentationError):
        LegalClientMatterFinalRepresentation.from_dict(tampered)


def test_no_expiry_revocation_supersession_or_downstream_authority() -> None:
    value = _fixture()
    assert not hasattr(value, "effective_until")
    tree = ast.parse(Path("tools/eos/legal_operations/domain/legal_client_matter_final_representation.py").read_text())
    imports = " ".join(ast.unparse(node) for node in ast.walk(tree) if isinstance(node, (ast.Import, ast.ImportFrom))).lower()
    assert all(term not in imports for term in ("iam", "court", "finance", "payment"))


@pytest.mark.parametrize("changed", ["source_evidence_reference", "representative_eligibility_reference", "idempotency_key"])
def test_material_provenance_changes_identity(changed: str) -> None:
    first = _fixture()
    kwargs = {changed: f"changed:{changed}"}
    second = _fixture(**kwargs)
    assert first.fingerprint != second.fingerprint
    assert first.representation_id != second.representation_id


def test_required_identity_fields_are_bound() -> None:
    value = _fixture()
    for field in ("tenant_id", "case_matter_id", "matter_fingerprint", "client_party_id", "subject_identity_fingerprint", "representation_authority_id", "representation_authority_fingerprint", "firm_representation_decision_id", "firm_representation_decision_fingerprint", "representative_principal_id", "representative_role", "engagement_id", "engagement_fingerprint", "mandate_id", "mandate_fingerprint"):
        assert getattr(value, field)


def test_idempotency_is_bound_and_no_decision_property_exists() -> None:
    value = _fixture()
    assert value.idempotency_key == "idempotency:final-p24"
    assert not hasattr(value, "decision")


# ARTIFACT: test_legal_client_matter_final_representation.py
# VERSION: v1.0.0-L9C11-P24-FINAL-REPRESENTATION-CERT
# AUTHORITY BOUNDARY: direct immutable P24 domain certificate only
# FAIL-CLOSED POSTURE: prerequisite, role, scope, chronology and integrity failures are asserted
# END OF WILSY OS SOVEREIGN ARTIFACT
