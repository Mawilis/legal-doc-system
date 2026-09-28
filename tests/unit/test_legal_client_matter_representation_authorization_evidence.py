"""Direct certificate for the L9C11-P17 authorization-evidence domain.

TITLE: WILSY OS L9C11-P17 Client Representation Authorization Evidence Certificate
VERSION: v1.0.0-L9C11-P17-CLIENT-REPRESENTATION-AUTHORIZATION-EVIDENCE-CERT
AUTHORITY: Wilsy OS Core Governance / Python EOS Legal Operations
EPITOME: Prove one immutable positive client self-appointment evidence snapshot
         without live authority reads, persistence, IAM, currentness, P1
         construction, Representation formation, Court or financial authority.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tests/unit/test_legal_client_matter_representation_authorization_evidence.py
COLLABORATION / OWNERSHIP: Certificate for the L9C11-P17 pure domain only.
CERTIFICATION / UPDATE DATE: 2026-09-28
CHANGELOG: v1.0.0 covers positive-only vocabulary, exact lineage, SELF-only
           capacity, closed internal roles, source revisions, bounded scope,
           deterministic identity/fingerprint, strict hydration and authority
           exclusions.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2.
SECURITY / PRIVACY POSTURE: Synthetic opaque identifiers and fingerprints only.
TENANT BOUNDARY: Every fixture is explicitly tenant-scoped.
AUTHORITY BOUNDARY: Evidence shape only; no live authorization or persistence.
FINANCIAL AUTHORITY BOUNDARY: No financial execution or settlement authority.
"""
from __future__ import annotations

from dataclasses import FrozenInstanceError
from datetime import datetime, timedelta, timezone
import inspect
from pathlib import Path
from typing import Any, cast

import pytest

from tools.eos.auth.principal_status import PrincipalStatus
from tools.eos.auth.tenant_membership import TenantMembershipStatus
from tools.eos.legal_operations.domain.legal_client_acting_capacity import (
    LegalClientActingCapacityType,
)
from tools.eos.legal_operations.domain.legal_client_matter_representation_authorization_evidence import (
    ELIGIBLE_REPRESENTATIVE_ROLES,
    REPRESENTATION_AUTHORIZATION_EVIDENCE_FIELDS,
    SCHEMA,
    VERSION,
    LegalClientMatterRepresentationAuthorizationDecision,
    LegalClientMatterRepresentationAuthorizationEvidence,
    LegalClientMatterRepresentationAuthorizationEvidenceError,
)


HEX_A = "a" * 128
HEX_B = "b" * 128
WHEN = datetime(2026, 9, 28, 8, 0, tzinfo=timezone.utc)


def _evidence(**overrides: object) -> LegalClientMatterRepresentationAuthorizationEvidence:
    values: dict[str, object] = {
        "tenant_id": "tenant-a",
        "case_matter_id": "matter-1",
        "matter_fingerprint": HEX_A,
        "client_party_id": "party-1",
        "subject_reference": "client:subject-1",
        "subject_identity_fingerprint": HEX_A,
        "client_subject_principal_id": "principal-client-1",
        "appointing_principal_id": "principal-client-1",
        "appointing_principal_status": PrincipalStatus.ACTIVE,
        "appointing_membership_status": TenantMembershipStatus.ACTIVE,
        "appointing_membership_revision": 4,
        "appointing_role": "LEGAL_CLIENT",
        "appointing_role_assignment_revision": 7,
        "client_visibility_reference": "visibility:binding-1",
        "client_visibility_fingerprint": HEX_A,
        "client_visibility_status": "ACTIVE",
        "acting_capacity_id": "capacity-1",
        "acting_capacity_fingerprint": HEX_A,
        "acting_capacity_type": LegalClientActingCapacityType.SELF,
        "engagement_id": "engagement-1",
        "engagement_fingerprint": HEX_A,
        "mandate_id": "mandate-1",
        "mandate_fingerprint": HEX_A,
        "mandate_scope_reference": "scope:limited",
        "mandate_scope_fingerprint": HEX_A,
        "mandate_capabilities": ["ADVISORY", "NEGOTIATION"],
        "representative_principal_id": "principal-attorney-1",
        "representative_principal_status": PrincipalStatus.ACTIVE,
        "representative_membership_status": TenantMembershipStatus.ACTIVE,
        "representative_membership_revision": 3,
        "representative_role_assignment_revision": 8,
        "representative_role": "LEGAL_ATTORNEY",
        "representative_eligibility_policy_version": "roles:v1.29.0",
        "representation_scope_capabilities": ["ADVISORY"],
        "decision": LegalClientMatterRepresentationAuthorizationDecision.AUTHORIZED,
        "source_evidence_reference": "evidence:client-appointment-1",
        "source_evidence_fingerprint": HEX_A,
        "occurred_at": WHEN,
        "effective_from": WHEN + timedelta(minutes=1),
        "idempotency_key": "idempotency:client-appointment-1",
    }
    values.update(overrides)
    return LegalClientMatterRepresentationAuthorizationEvidence(**cast(Any, values))


def test_version_schema_and_exact_fields() -> None:
    value = _evidence()
    assert set(value.to_dict()) == set(REPRESENTATION_AUTHORIZATION_EVIDENCE_FIELDS)
    assert value.schema == SCHEMA
    assert value.authorization_version == VERSION
    assert value.decision is LegalClientMatterRepresentationAuthorizationDecision.AUTHORIZED
    assert value.is_authorized is True
    assert ELIGIBLE_REPRESENTATIVE_ROLES == frozenset({"LEGAL_ATTORNEY", "LEGAL_PARTNER"})


def test_immutable_and_input_collections_are_not_retained_mutably() -> None:
    mandate = ["ADVISORY", "NEGOTIATION"]
    scope = ["ADVISORY"]
    value = _evidence(mandate_capabilities=mandate, representation_scope_capabilities=scope)
    mandate.append("TRANSACTIONAL")
    scope.append("NEGOTIATION")
    assert value.mandate_capabilities == ("ADVISORY", "NEGOTIATION")
    assert value.representation_scope_capabilities == ("ADVISORY",)
    with pytest.raises(FrozenInstanceError):
        value.decision = "AUTHORIZED"  # type: ignore[misc]


def test_only_authorized_is_a_positive_decision() -> None:
    assert {item.value for item in LegalClientMatterRepresentationAuthorizationDecision} == {"AUTHORIZED"}
    for decision in ("DENIED", "REVIEW", "UNKNOWN"):
        with pytest.raises(LegalClientMatterRepresentationAuthorizationEvidenceError):
            _evidence(decision=decision)


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("tenant_id", "tenant-b"),
        ("case_matter_id", "matter-2"),
        ("client_party_id", "party-2"),
        ("client_subject_principal_id", "principal-client-2"),
        ("appointing_principal_id", "principal-client-2"),
        ("matter_fingerprint", HEX_B),
        ("subject_identity_fingerprint", HEX_B),
    ],
)
def test_exact_tenant_matter_client_and_subject_bindings_are_immutable(field: str, value: object) -> None:
    original = _evidence()
    overrides: dict[str, object] = {field: value}
    if field == "client_subject_principal_id":
        overrides["appointing_principal_id"] = value
    elif field == "appointing_principal_id":
        overrides["client_subject_principal_id"] = value
    changed = _evidence(**overrides)
    assert changed.fingerprint != original.fingerprint
    assert changed.evidence_id != original.evidence_id


def test_appointing_principal_must_equal_client_subject() -> None:
    with pytest.raises(LegalClientMatterRepresentationAuthorizationEvidenceError) as error:
        _evidence(appointing_principal_id="principal-other")
    assert error.value.code == "L9C11_P17_APPOINTING_PRINCIPAL_CLIENT_SUBJECT_MISMATCH"


@pytest.mark.parametrize("capacity", ["AUTHORIZED_AGENT", "REPRESENTATIVE", "UNKNOWN"])
def test_non_self_capacity_is_rejected(capacity: str) -> None:
    with pytest.raises(LegalClientMatterRepresentationAuthorizationEvidenceError) as error:
        _evidence(acting_capacity_type=capacity)
    assert error.value.code in {
        "L9C11_P17_SELF_CAPACITY_REQUIRED",
        "L9C11_P17_ACTING_CAPACITY_TYPE_INVALID",
    }


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("appointing_principal_status", "SUSPENDED"),
        ("appointing_membership_status", "REVOKED"),
        ("appointing_role", "LEGAL_PARTNER"),
        ("client_visibility_status", "REVOKED"),
        ("representative_principal_status", "REVOKED"),
        ("representative_membership_status", "SUSPENDED"),
    ],
)
def test_actor_and_representative_active_evidence_is_required(field: str, value: object) -> None:
    with pytest.raises(LegalClientMatterRepresentationAuthorizationEvidenceError):
        _evidence(**{field: value})


def test_engagement_mandate_and_capacity_lineage_is_bound() -> None:
    value = _evidence()
    assert value.engagement_id == "engagement-1"
    assert value.engagement_fingerprint == HEX_A
    assert value.mandate_id == "mandate-1"
    assert value.mandate_fingerprint == HEX_A
    assert value.acting_capacity_id == "capacity-1"
    assert value.acting_capacity_fingerprint == HEX_A


def test_canonical_capability_normalization_and_duplicate_deduplication() -> None:
    value = _evidence(
        mandate_capabilities=["NEGOTIATION", "ADVISORY", "ADVISORY"],
        representation_scope_capabilities=["ADVISORY", "ADVISORY"],
    )
    assert value.mandate_capabilities == ("ADVISORY", "NEGOTIATION")
    assert value.representation_scope_capabilities == ("ADVISORY",)


def test_scope_must_be_a_subset_of_mandate() -> None:
    with pytest.raises(LegalClientMatterRepresentationAuthorizationEvidenceError) as error:
        _evidence(representation_scope_capabilities=["TRANSACTIONAL"])
    assert error.value.code == "L9C11_P17_SCOPE_EXCEEDS_MANDATE"


@pytest.mark.parametrize("capability", ["COURT_FILING_PREPARATION", "COURT_APPEARANCE_PREPARATION"])
def test_court_capabilities_are_rejected(capability: str) -> None:
    with pytest.raises(LegalClientMatterRepresentationAuthorizationEvidenceError) as error:
        _evidence(representation_scope_capabilities=[capability])
    assert error.value.code == "L9C11_P17_COURT_SCOPE_FORBIDDEN"


@pytest.mark.parametrize("capability", ["PAYMENT_EXECUTION", "SETTLEMENT", "UNKNOWN"])
def test_financial_or_unknown_capabilities_are_rejected(capability: str) -> None:
    with pytest.raises(LegalClientMatterRepresentationAuthorizationEvidenceError):
        _evidence(representation_scope_capabilities=[capability])


@pytest.mark.parametrize("role", ["LEGAL_ATTORNEY", "LEGAL_PARTNER"])
def test_partner_and_attorney_are_accepted(role: str) -> None:
    assert _evidence(representative_role=role).representative_role == role


@pytest.mark.parametrize(
    "role",
    ["LEGAL_PARALEGAL", "LEGAL_CLIENT", "LEGAL_SECRETARY", "LEGAL_FINANCE", "UNKNOWN"],
)
def test_roles_outside_closed_eligible_set_are_rejected(role: str) -> None:
    with pytest.raises(LegalClientMatterRepresentationAuthorizationEvidenceError) as error:
        _evidence(representative_role=role)
    assert error.value.code == "L9C11_P17_REPRESENTATIVE_ROLE_INELIGIBLE"


def test_status_membership_and_role_revisions_are_bound() -> None:
    value = _evidence(
        appointing_membership_revision=11,
        appointing_role_assignment_revision=12,
        representative_membership_revision=13,
        representative_role_assignment_revision=14,
    )
    assert value.appointing_membership_revision == 11
    assert value.appointing_role_assignment_revision == 12
    assert value.representative_membership_revision == 13
    assert value.representative_role_assignment_revision == 14


@pytest.mark.parametrize(
    "field",
    [
        "appointing_membership_revision",
        "appointing_role_assignment_revision",
        "representative_membership_revision",
        "representative_role_assignment_revision",
    ],
)
def test_revisions_reject_bool_negative_and_string(field: str) -> None:
    for value in (True, -1, "1"):
        with pytest.raises(LegalClientMatterRepresentationAuthorizationEvidenceError):
            _evidence(**{field: value})


def test_policy_and_source_evidence_are_bound() -> None:
    value = _evidence(
        representative_eligibility_policy_version="roles:v1.29.0|tenant-policy:v1.27.0",
        source_evidence_reference="evidence:issuer-evaluation-2",
        source_evidence_fingerprint=HEX_B,
    )
    assert "tenant-policy" in value.representative_eligibility_policy_version
    assert value.source_evidence_fingerprint == HEX_B


def test_explicit_aware_utc_timestamps_and_future_effective_values() -> None:
    value = _evidence(
        occurred_at="2026-09-28T08:00:00Z",
        effective_from="2026-12-01T08:00:00+00:00",
    )
    assert value.occurred_at == WHEN
    assert value.effective_from == datetime(2026, 12, 1, 8, tzinfo=timezone.utc)
    with pytest.raises(LegalClientMatterRepresentationAuthorizationEvidenceError):
        _evidence(occurred_at=datetime(2026, 9, 28, 8, 0))
    with pytest.raises(LegalClientMatterRepresentationAuthorizationEvidenceError):
        _evidence(effective_from=WHEN - timedelta(seconds=1))


def test_domain_does_not_read_a_clock() -> None:
    source = inspect.getsource(LegalClientMatterRepresentationAuthorizationEvidence)
    module_source = Path(inspect.getsourcefile(LegalClientMatterRepresentationAuthorizationEvidence) or "").read_text()
    assert "datetime.now" not in source
    assert "datetime.now" not in module_source
    assert "utcnow" not in module_source


def test_deterministic_evidence_id_and_fingerprint() -> None:
    first = _evidence()
    second = _evidence()
    assert first.evidence_id == second.evidence_id
    assert first.fingerprint == second.fingerprint
    assert first.evidence_id.startswith("client-representation-authorization:")
    assert len(first.fingerprint) == 128
    assert first.fingerprint == first.fingerprint.lower()


@pytest.mark.parametrize(
    "field",
    ["representative_principal_id", "representation_scope_capabilities", "case_matter_id", "client_party_id"],
)
def test_changed_identity_or_scope_changes_evidence_identity_and_fingerprint(field: str) -> None:
    original = _evidence()
    changed_value: object = {
        "representative_principal_id": "principal-partner-1",
        "representation_scope_capabilities": ["NEGOTIATION"],
        "case_matter_id": "matter-2",
        "client_party_id": "party-2",
    }[field]
    changed = _evidence(**{field: changed_value})
    assert changed.evidence_id != original.evidence_id
    assert changed.fingerprint != original.fingerprint


def test_changed_idempotency_key_changes_identity_and_fingerprint() -> None:
    original = _evidence()
    changed = _evidence(idempotency_key="idempotency:client-appointment-2")
    assert changed.evidence_id != original.evidence_id
    assert changed.fingerprint != original.fingerprint


def test_strict_to_dict_and_from_dict_round_trip() -> None:
    value = _evidence()
    payload = value.to_dict()
    assert set(payload) == set(REPRESENTATION_AUTHORIZATION_EVIDENCE_FIELDS)
    assert LegalClientMatterRepresentationAuthorizationEvidence.from_dict(payload) == value
    assert isinstance(payload["mandate_capabilities"], list)
    assert isinstance(payload["representation_scope_capabilities"], list)


def test_unknown_and_missing_fields_are_rejected() -> None:
    payload = _evidence().to_dict()
    unknown = dict(payload)
    unknown["unexpected"] = True
    with pytest.raises(LegalClientMatterRepresentationAuthorizationEvidenceError) as error:
        LegalClientMatterRepresentationAuthorizationEvidence.from_dict(unknown)
    assert error.value.code == "L9C11_P17_SCHEMA_INVALID"
    missing = dict(payload)
    del missing["source_evidence_fingerprint"]
    with pytest.raises(LegalClientMatterRepresentationAuthorizationEvidenceError) as error:
        LegalClientMatterRepresentationAuthorizationEvidence.from_dict(missing)
    assert error.value.code == "L9C11_P17_SCHEMA_INVALID"


def test_strict_hydration_rejects_duplicate_or_noncanonical_capabilities() -> None:
    duplicate = _evidence().to_dict()
    duplicate["representation_scope_capabilities"] = ["ADVISORY", "ADVISORY"]
    with pytest.raises(LegalClientMatterRepresentationAuthorizationEvidenceError):
        LegalClientMatterRepresentationAuthorizationEvidence.from_dict(duplicate)

    unsorted = _evidence().to_dict()
    unsorted["mandate_capabilities"] = ["NEGOTIATION", "ADVISORY"]
    with pytest.raises(LegalClientMatterRepresentationAuthorizationEvidenceError):
        LegalClientMatterRepresentationAuthorizationEvidence.from_dict(unsorted)

    wrong_container = _evidence().to_dict()
    wrong_container["representation_scope_capabilities"] = ("ADVISORY",)
    with pytest.raises(LegalClientMatterRepresentationAuthorizationEvidenceError):
        LegalClientMatterRepresentationAuthorizationEvidence.from_dict(wrong_container)


def test_fingerprint_corruption_is_rejected() -> None:
    payload = _evidence().to_dict()
    payload["fingerprint"] = HEX_B
    with pytest.raises(LegalClientMatterRepresentationAuthorizationEvidenceError) as error:
        LegalClientMatterRepresentationAuthorizationEvidence.from_dict(payload)
    assert error.value.code == "L9C11_P17_FINGERPRINT_MISMATCH"


def test_evidence_id_corruption_is_rejected() -> None:
    payload = _evidence().to_dict()
    payload["evidence_id"] = "client-representation-authorization:corrupt"
    with pytest.raises(LegalClientMatterRepresentationAuthorizationEvidenceError) as error:
        LegalClientMatterRepresentationAuthorizationEvidence.from_dict(payload)
    assert error.value.code == "L9C11_P17_EVIDENCE_ID_MISMATCH"


def test_no_iam_persistence_registry_or_p1_construction_is_imported() -> None:
    module_source = Path(
        inspect.getsourcefile(LegalClientMatterRepresentationAuthorizationEvidence) or ""
    ).read_text()
    assert "pymongo" not in module_source
    assert "MongoClient" not in module_source
    assert "authorize_tenant_operation" not in module_source
    assert "TenantAuthorization" not in module_source
    assert "LegalClientMatterRepresentationAuthority" not in module_source
    assert "Registry" not in module_source


def test_no_live_queries_or_currentness_composers_are_present() -> None:
    module_source = Path(
        inspect.getsourcefile(LegalClientMatterRepresentationAuthorizationEvidence) or ""
    ).read_text()
    assert ".find(" not in module_source
    assert ".find_one(" not in module_source
    assert "currentness_composer" not in module_source


def test_professional_court_and_financial_boundaries_are_not_fields_or_claims() -> None:
    payload = _evidence().to_dict()
    assert "court_authority" not in payload
    assert "bar_admission" not in payload
    assert "attorney_of_record" not in payload
    assert "financial_execution" not in payload


# ARTIFACT: test_legal_client_matter_representation_authorization_evidence.py
# VERSION: v1.0.0-L9C11-P17-CLIENT-REPRESENTATION-AUTHORIZATION-EVIDENCE-CERT
# AUTHORITY BOUNDARY: direct pure-domain certificate only
# TENANT POSTURE: synthetic exact tenant and lineage fixtures
# FAIL-CLOSED POSTURE: malformed, widened, divergent and unauthorized evidence rejects
# END OF WILSY OS SOVEREIGN ARTIFACT
