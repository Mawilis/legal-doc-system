"""Direct certificate for the L9C11-P2 firm Representation decision domain.

TITLE: WILSY OS L9C11-P2 Firm Representation Decision Certificate
VERSION: v1.0.0-L9C11-P2-FIRM-REPRESENTATION-DECISION-CERT
AUTHORITY: Wilsy OS Core Governance / Python EOS Legal Operations
EPITOME: Prove immutable firm acceptance evidence bound to one exact client
         Representation authority, without forming Representation or granting
         currentness, IAM, Court or financial authority.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tests/unit/test_legal_client_matter_representation_firm_decision.py
COLLABORATION / OWNERSHIP: Certificate for the L9C11-P2 pure domain only.
CERTIFICATION / UPDATE DATE: 2026-09-28
CHANGELOG: v1.0.0-L9C11-P2 certificate covers exact P1 binding, vocabulary,
           bounded scope, chronology, immutable deterministic evidence,
           strict hydration and authority exclusions.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2.
SECURITY / PRIVACY POSTURE: Synthetic opaque identifiers and fingerprints only.
TENANT BOUNDARY: Exact synthetic tenant and upstream lineage are asserted.
AUTHORITY BOUNDARY: Historical firm decision evidence only; no formation.
FINANCIAL AUTHORITY BOUNDARY: No payment, settlement or execution authority.
"""
from __future__ import annotations

from dataclasses import FrozenInstanceError
from datetime import datetime, timedelta, timezone
import inspect
from pathlib import Path
from typing import Any, cast

import pytest

from tools.eos.legal_operations.domain.legal_client_matter_representation_authority import (
    LegalClientMatterRepresentationAuthority,
    LegalClientMatterRepresentationAuthorityDecision,
)
from tools.eos.legal_operations.domain.legal_client_matter_representation_firm_decision import (
    REPRESENTATION_FIRM_DECISION_FIELDS,
    SCHEMA,
    VERSION,
    LegalClientMatterRepresentationFirmDecision,
    LegalClientMatterRepresentationFirmDecisionError,
    LegalClientMatterRepresentationFirmDecisionType,
)


HEX = "a" * 128
WHEN = datetime(2026, 9, 28, 8, 0, tzinfo=timezone.utc)


def _authority(**overrides: object) -> LegalClientMatterRepresentationAuthority:
    values: dict[str, object] = {
        "authority_id": "representation-authority-1",
        "tenant_id": "tenant-a",
        "case_matter_id": "matter-1",
        "matter_fingerprint": HEX,
        "client_party_id": "party-1",
        "subject_reference": "client:subject-1",
        "subject_identity_fingerprint": HEX,
        "engagement_id": "engagement-1",
        "engagement_fingerprint": HEX,
        "mandate_id": "mandate-1",
        "mandate_fingerprint": HEX,
        "mandate_scope_reference": "scope:limited",
        "mandate_scope_fingerprint": HEX,
        "mandate_capabilities": ["ADVISORY", "NEGOTIATION"],
        "acting_capacity_id": "capacity-1",
        "acting_capacity_fingerprint": HEX,
        "representative_principal_id": "principal-attorney-1",
        "representative_role": "LEGAL_PRACTITIONER",
        "representation_scope_capabilities": ["ADVISORY"],
        "decision": LegalClientMatterRepresentationAuthorityDecision.APPOINTED,
        "appointing_principal_id": "principal-client-1",
        "source_evidence_reference": "evidence:appointment-1",
        "source_evidence_fingerprint": HEX,
        "authorization_evidence_reference": "evidence:authorization-1",
        "authorization_evidence_fingerprint": HEX,
        "occurred_at": WHEN,
        "effective_from": WHEN + timedelta(minutes=1),
        "effective_until": WHEN + timedelta(days=30),
        "idempotency_key": "idempotency:appointment-1",
    }
    values.update(overrides)
    return LegalClientMatterRepresentationAuthority(**cast(Any, values))


def _decision(
    authority: LegalClientMatterRepresentationAuthority | None = None,
    **overrides: object,
) -> LegalClientMatterRepresentationFirmDecision:
    authority = authority or _authority()
    values: dict[str, object] = {
        "client_authority": authority,
        "decision": LegalClientMatterRepresentationFirmDecisionType.ACCEPTED,
        "decision_actor_principal_id": "principal-firm-1",
        "authorization_evidence_reference": "evidence:firm-authorization-1",
        "authorization_evidence_fingerprint": HEX,
        "source_evidence_reference": "evidence:firm-decision-1",
        "source_evidence_fingerprint": HEX,
        "occurred_at": WHEN + timedelta(minutes=2),
        "effective_from": WHEN + timedelta(minutes=3),
        "idempotency_key": "idempotency:firm-decision-1",
    }
    values.update(overrides)
    return LegalClientMatterRepresentationFirmDecision.from_client_authority(
        **cast(Any, values)
    )


def test_schema_version_and_exact_lineage_are_preserved() -> None:
    value = _decision()
    assert set(value.to_dict()) == set(REPRESENTATION_FIRM_DECISION_FIELDS)
    assert value.schema == SCHEMA
    assert value.decision_version == VERSION
    assert value.tenant_id == "tenant-a"
    assert value.case_matter_id == "matter-1"
    assert value.client_party_id == "party-1"
    assert value.subject_identity_fingerprint == HEX
    assert value.engagement_id == "engagement-1"
    assert value.mandate_id == "mandate-1"
    assert value.acting_capacity_id == "capacity-1"
    assert value.representation_authority_id == "representation-authority-1"
    assert value.client_authority_scope_capabilities == ("ADVISORY",)


def test_only_accepted_and_appointed_is_representation_forming() -> None:
    assert {item.value for item in LegalClientMatterRepresentationFirmDecisionType} == {
        "ACCEPTED", "DECLINED", "REQUIRES_REVIEW"
    }
    assert _decision().is_representation_forming is True
    assert _decision(decision="DECLINED").is_representation_forming is False
    assert _decision(decision="REQUIRES_REVIEW").is_representation_forming is False
    assert _decision(authority=_authority(decision="DECLINED"), decision="DECLINED").is_representation_forming is False
    assert _decision(authority=_authority(decision="REQUIRES_REVIEW"), decision="REQUIRES_REVIEW").is_representation_forming is False


def test_exact_client_authority_binding_carries_principal_role_scope_and_fingerprint() -> None:
    authority = _authority()
    value = _decision(authority)
    assert value.representation_authority_fingerprint == authority.fingerprint
    assert value.representative_principal_id == authority.representative_principal_id
    assert value.representative_role == authority.representative_role
    assert value.mandate_capabilities == authority.mandate_capabilities
    assert value.representation_scope_capabilities == authority.representation_scope_capabilities


@pytest.mark.parametrize("client_state", ["DECLINED", "REQUIRES_REVIEW"])
def test_accepted_rejects_non_appointed_client_authority(client_state: str) -> None:
    with pytest.raises(LegalClientMatterRepresentationFirmDecisionError) as error:
        _decision(authority=_authority(decision=client_state))
    assert error.value.code == "L9C11_P2_CLIENT_AUTHORITY_NOT_APPOINTED"


def test_non_accepting_decision_can_preserve_a_non_appointed_client_state() -> None:
    value = _decision(authority=_authority(decision="DECLINED"), decision="DECLINED")
    assert value.client_authority_decision is LegalClientMatterRepresentationAuthorityDecision.DECLINED
    assert value.is_representation_forming is False


def test_scope_is_subset_of_mandate_and_court_scope_is_forbidden() -> None:
    authority = _authority(
        mandate_capabilities=["ADVISORY", "NEGOTIATION"],
        representation_scope_capabilities=["ADVISORY"],
    )
    valid = _decision(authority)
    assert set(valid.representation_scope_capabilities) <= set(valid.mandate_capabilities)
    values = valid.to_dict()
    values["representation_scope_capabilities"] = ["NEGOTIATION"]
    values["fingerprint"] = valid.fingerprint
    with pytest.raises(LegalClientMatterRepresentationFirmDecisionError):
        LegalClientMatterRepresentationFirmDecision.from_dict(values)
    values = valid.to_dict()
    values["mandate_capabilities"] = ["COURT_FILING_PREPARATION"]
    values["representation_scope_capabilities"] = ["COURT_FILING_PREPARATION"]
    with pytest.raises(LegalClientMatterRepresentationFirmDecisionError) as error:
        LegalClientMatterRepresentationFirmDecision.from_dict(values)
    assert error.value.code == "L9C11_P2_COURT_SCOPE_FORBIDDEN"


def test_firm_scope_may_be_narrower_but_not_wider_than_client_scope() -> None:
    authority = _authority(
        mandate_capabilities=["ADVISORY", "NEGOTIATION"],
        representation_scope_capabilities=["ADVISORY", "NEGOTIATION"],
    )
    value = _decision(authority, representation_scope_capabilities=["ADVISORY"])
    assert value.client_authority_scope_capabilities == ("ADVISORY", "NEGOTIATION")
    assert value.representation_scope_capabilities == ("ADVISORY",)
    with pytest.raises(LegalClientMatterRepresentationFirmDecisionError) as error:
        _decision(
            _authority(
                mandate_capabilities=["ADVISORY", "NEGOTIATION"],
                representation_scope_capabilities=["ADVISORY"],
            ),
            representation_scope_capabilities=["NEGOTIATION"],
        )
    assert error.value.code == "L9C11_P2_SCOPE_EXCEEDS_CLIENT_AUTHORITY"


def test_aware_utc_chronology_and_effective_lower_bound_are_required() -> None:
    value = _decision(occurred_at="2026-09-28T08:02:00Z", effective_from="2026-09-28T08:03:00+00:00")
    assert value.occurred_at.tzinfo == timezone.utc
    assert value.effective_from >= value.client_authority_effective_from
    with pytest.raises(LegalClientMatterRepresentationFirmDecisionError):
        _decision(occurred_at=datetime(2026, 9, 28, 8, 2))
    with pytest.raises(LegalClientMatterRepresentationFirmDecisionError) as error:
        _decision(effective_from=WHEN + timedelta(seconds=30))
    assert error.value.code == "L9C11_P2_EFFECTIVE_FROM_BEFORE_CLIENT_AUTHORITY"
    with pytest.raises(LegalClientMatterRepresentationFirmDecisionError) as error:
        _decision(occurred_at=WHEN + timedelta(minutes=4), effective_from=WHEN + timedelta(minutes=3))
    assert error.value.code == "L9C11_P2_EFFECTIVE_FROM_BEFORE_OCCURRED"


def test_deterministic_decision_id_and_sha3_fingerprint() -> None:
    first = _decision()
    second = _decision()
    changed = _decision(decision_actor_principal_id="principal-firm-2")
    assert first.decision_id == second.decision_id
    assert first.fingerprint == second.fingerprint
    assert first.decision_id.startswith("representation-firm-decision:")
    assert len(first.fingerprint) == 128
    assert changed.decision_id != first.decision_id
    assert changed.fingerprint != first.fingerprint


def test_strict_round_trip_and_tamper_rejection() -> None:
    value = _decision()
    assert LegalClientMatterRepresentationFirmDecision.from_dict(value.to_dict()) == value
    tampered = value.to_dict()
    tampered["representative_principal_id"] = "principal-other"
    with pytest.raises(LegalClientMatterRepresentationFirmDecisionError) as error:
        LegalClientMatterRepresentationFirmDecision.from_dict(tampered)
    assert error.value.code == "L9C11_P2_DECISION_ID_MISMATCH"
    with pytest.raises(LegalClientMatterRepresentationFirmDecisionError) as error:
        LegalClientMatterRepresentationFirmDecision.from_dict({"schema": SCHEMA})
    assert error.value.code == "L9C11_P2_SCHEMA_INVALID"


def test_supplied_decision_id_and_fingerprint_are_verified() -> None:
    value = _decision()
    tampered = value.to_dict()
    tampered["decision_id"] = "representation-firm-decision:" + "b" * 48
    with pytest.raises(LegalClientMatterRepresentationFirmDecisionError) as error:
        LegalClientMatterRepresentationFirmDecision.from_dict(tampered)
    assert error.value.code == "L9C11_P2_DECISION_ID_MISMATCH"
    tampered = value.to_dict()
    tampered["fingerprint"] = "b" * 128
    with pytest.raises(LegalClientMatterRepresentationFirmDecisionError) as error:
        LegalClientMatterRepresentationFirmDecision.from_dict(tampered)
    assert error.value.code == "L9C11_P2_FINGERPRINT_MISMATCH"


def test_immutable_and_input_collections_are_not_retained_mutably() -> None:
    authority = _authority()
    value = _decision(authority)
    assert isinstance(value.mandate_capabilities, tuple)
    assert isinstance(value.representation_scope_capabilities, tuple)
    with pytest.raises(FrozenInstanceError):
        value.decision = "DECLINED"  # type: ignore[misc]


def test_identity_and_tenant_are_explicit_and_fail_closed() -> None:
    for field in ("tenant_id", "case_matter_id", "client_party_id", "decision_actor_principal_id"):
        values = _decision().to_dict()
        values[field] = " "
        with pytest.raises(LegalClientMatterRepresentationFirmDecisionError):
            LegalClientMatterRepresentationFirmDecision.from_dict(values)
    values = _decision().to_dict()
    values["tenant_id"] = "global"
    with pytest.raises(LegalClientMatterRepresentationFirmDecisionError) as error:
        LegalClientMatterRepresentationFirmDecision.from_dict(values)
    assert error.value.code == "L9C11_P2_TENANT_REQUIRED"


def test_public_domain_has_no_persistence_iam_currentness_or_finance_authority() -> None:
    source = Path(
        "/Users/wilsonkhanyezi/legal-doc-system/tools/eos/legal_operations/domain/legal_client_matter_representation_firm_decision.py"
    ).read_text(encoding="utf-8")
    forbidden_imports = ("pymongo", "motor", "jwt", "fastapi", "sqlalchemy")
    assert not any(term in source for term in forbidden_imports)
    assert "from_client_authority" in source
    assert "is_representation_forming" in source
    assert "TODO" not in source and "FIXME" not in source
    assert "LegalClientMatterRepresentationAuthority" in inspect.getsource(LegalClientMatterRepresentationFirmDecision)


def test_factory_requires_the_published_client_authority_type() -> None:
    with pytest.raises(LegalClientMatterRepresentationFirmDecisionError) as error:
        LegalClientMatterRepresentationFirmDecision.from_client_authority(
            client_authority=cast(Any, object()),
            decision="DECLINED",
            decision_actor_principal_id="principal-firm-1",
            authorization_evidence_reference="evidence:firm-authorization-1",
            authorization_evidence_fingerprint=HEX,
            source_evidence_reference="evidence:firm-decision-1",
            source_evidence_fingerprint=HEX,
            occurred_at=WHEN,
            effective_from=WHEN,
            idempotency_key="idempotency:firm-decision-1",
        )
    assert error.value.code == "L9C11_P2_CLIENT_AUTHORITY_REQUIRED"
