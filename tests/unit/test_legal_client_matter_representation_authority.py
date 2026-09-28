"""Direct certificate for the L9C11-P1 client Representation authority domain.

TITLE: WILSY OS L9C11-P1 Representation Authority Certificate
VERSION: v1.0.0-L9C11-P1-CLIENT-REPRESENTATION-AUTHORITY-CERT
AUTHORITY: Wilsy OS Core Governance / Python EOS Legal Operations
EPITOME: Prove the immutable client appointment prerequisite without creating
         Representation, currentness, IAM, persistence, Court or finance.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tests/unit/test_legal_client_matter_representation_authority.py
COLLABORATION / OWNERSHIP: Certificate for the L9C11-P1 pure domain only.
CERTIFICATION / UPDATE DATE: 2026-09-28
CHANGELOG: v1.0.0-L9C11-P1 certificate covers vocabulary, exact lineage fields,
           mandate-bounded non-Court scope, chronology, immutability, strict
           hydration, deterministic fingerprint and authority exclusions.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2.
SECURITY / PRIVACY POSTURE: Synthetic opaque identifiers and fingerprints only.
TENANT BOUNDARY: Tests use one explicit synthetic tenant and no persistence.
AUTHORITY BOUNDARY: Client appointment evidence only; no formed Representation.
FINANCIAL AUTHORITY BOUNDARY: No financial execution or settlement authority.
"""
from __future__ import annotations

from dataclasses import FrozenInstanceError
from datetime import datetime, timedelta, timezone
import inspect
from pathlib import Path
from typing import Any, cast

import pytest

from tools.eos.legal_operations.domain.legal_client_matter_representation_authority import (
    REPRESENTATION_AUTHORITY_FIELDS,
    SCHEMA,
    VERSION,
    LegalClientMatterRepresentationAuthority,
    LegalClientMatterRepresentationAuthorityDecision,
    LegalClientMatterRepresentationAuthorityError,
)
from tools.eos.legal_operations.domain.legal_client_acting_capacity import (
    LegalClientActingCapacity,
)
from tools.eos.legal_operations.domain.legal_client_matter_engagement import (
    LegalClientMatterEngagement,
)
from tools.eos.legal_operations.domain.legal_client_matter_mandate import (
    LegalClientMatterMandate,
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


def test_exact_schema_and_lineage_fields() -> None:
    value = _authority()
    assert set(value.to_dict()) == set(REPRESENTATION_AUTHORITY_FIELDS)
    assert value.schema == SCHEMA
    assert value.authority_version == VERSION
    assert value.tenant_id == "tenant-a"
    assert value.engagement_id == "engagement-1"
    assert value.mandate_id == "mandate-1"
    assert value.acting_capacity_id == "capacity-1"
    assert value.representative_principal_id == "principal-attorney-1"


def test_client_vocabulary_has_one_positive_and_two_non_positive_decisions() -> None:
    value = _authority()
    assert value
    assert value.is_appointing is True
    assert _authority(decision="DECLINED").is_appointing is False
    assert _authority(decision="REQUIRES_REVIEW").is_appointing is False
    assert "WITHDRAWN" not in {item.value for item in LegalClientMatterRepresentationAuthorityDecision}
    assert "REVOKED" not in {item.value for item in LegalClientMatterRepresentationAuthorityDecision}


def test_scope_is_a_subset_of_mandate_and_court_scope_is_rejected() -> None:
    assert _authority(
        mandate_capabilities=["ADVISORY", "NEGOTIATION"],
        representation_scope_capabilities=["NEGOTIATION"],
    ).representation_scope_capabilities == ("NEGOTIATION",)
    with pytest.raises(LegalClientMatterRepresentationAuthorityError) as error:
        _authority(representation_scope_capabilities=["TRANSACTIONAL"])
    assert error.value.code == "L9C11_P1_SCOPE_EXCEEDS_MANDATE"
    with pytest.raises(LegalClientMatterRepresentationAuthorityError) as error:
        _authority(
            mandate_capabilities=["COURT_FILING_PREPARATION"],
            representation_scope_capabilities=["COURT_FILING_PREPARATION"],
        )
    assert error.value.code == "L9C11_P1_COURT_SCOPE_FORBIDDEN"


def test_explicit_utc_chronology_and_naive_timestamp_rejection() -> None:
    value = _authority(occurred_at="2026-09-28T08:00:00Z", effective_from="2026-09-28T08:01:00+00:00")
    assert value.occurred_at.tzinfo is not None
    assert value.occurred_at.tzinfo == timezone.utc
    with pytest.raises(LegalClientMatterRepresentationAuthorityError):
        _authority(occurred_at=datetime(2026, 9, 28, 8, 0))
    with pytest.raises(LegalClientMatterRepresentationAuthorityError):
        _authority(effective_from=WHEN - timedelta(seconds=1))
    with pytest.raises(LegalClientMatterRepresentationAuthorityError):
        _authority(effective_until=WHEN)


def test_deterministic_sha3_fingerprint_and_strict_hydration() -> None:
    value = _authority()
    assert len(value.fingerprint) == 128
    assert value.fingerprint == _authority().fingerprint
    assert LegalClientMatterRepresentationAuthority.from_dict(value.to_dict()) == value
    tampered = value.to_dict()
    tampered["representative_role"] = "OTHER_ROLE"
    with pytest.raises(LegalClientMatterRepresentationAuthorityError) as error:
        LegalClientMatterRepresentationAuthority.from_dict(tampered)
    assert error.value.code == "L9C11_P1_FINGERPRINT_MISMATCH"
    with pytest.raises(LegalClientMatterRepresentationAuthorityError) as error:
        LegalClientMatterRepresentationAuthority.from_dict({"schema": SCHEMA})
    assert error.value.code == "L9C11_P1_SCHEMA_INVALID"


def test_immutable_and_input_values_are_not_retained_mutably() -> None:
    mandate_capabilities = ["ADVISORY", "NEGOTIATION"]
    scope_capabilities = ["ADVISORY"]
    value = _authority(
        mandate_capabilities=mandate_capabilities,
        representation_scope_capabilities=scope_capabilities,
    )
    mandate_capabilities.append("TRANSACTIONAL")
    scope_capabilities.append("NEGOTIATION")
    assert value.mandate_capabilities == ("ADVISORY", "NEGOTIATION")
    assert value.representation_scope_capabilities == ("ADVISORY",)
    with pytest.raises(FrozenInstanceError):
        value.decision = "DECLINED"  # type: ignore[misc]


def test_canonical_constructor_binds_exact_upstream_lineage() -> None:
    def bare(cls: type[Any], **fields: object) -> Any:
        instance = object.__new__(cls)
        for name, field_value in fields.items():
            object.__setattr__(instance, name, field_value)
        return instance

    engagement = bare(
        LegalClientMatterEngagement,
        engagement_id="engagement-1",
        tenant_id="tenant-a",
        case_matter_id="matter-1",
        matter_fingerprint=HEX,
        client_party_id="party-1",
        subject_reference="client:subject-1",
        subject_identity_fingerprint=HEX,
        acting_capacity_id="capacity-1",
        acting_capacity_fingerprint=HEX,
        mandate_id="mandate-1",
        mandate_fingerprint=HEX,
        fingerprint=HEX,
    )
    mandate = bare(
        LegalClientMatterMandate,
        mandate_id="mandate-1",
        tenant_id="tenant-a",
        case_matter_id="matter-1",
        matter_fingerprint=HEX,
        client_party_id="party-1",
        subject_identity_fingerprint=HEX,
        acting_capacity_id="capacity-1",
        acting_capacity_fingerprint=HEX,
        scope_reference="scope:limited",
        scope_fingerprint=HEX,
        capabilities=("ADVISORY", "NEGOTIATION"),
        fingerprint=HEX,
    )
    capacity = bare(
        LegalClientActingCapacity,
        capacity_id="capacity-1",
        tenant_id="tenant-a",
        case_matter_id="matter-1",
        matter_fingerprint=HEX,
        party_id="party-1",
        subject_identity_fingerprint=HEX,
        fingerprint=HEX,
    )
    value = LegalClientMatterRepresentationAuthority.from_canonical(
        authority_id="representation-authority-1",
        engagement=engagement,
        mandate=mandate,
        acting_capacity=capacity,
        representative_principal_id="principal-attorney-1",
        representative_role="LEGAL_PRACTITIONER",
        representation_scope_capabilities=["ADVISORY"],
        decision="APPOINTED",
        appointing_principal_id="principal-client-1",
        source_evidence_reference="evidence:appointment-1",
        source_evidence_fingerprint=HEX,
        authorization_evidence_reference="evidence:authorization-1",
        authorization_evidence_fingerprint=HEX,
        occurred_at=WHEN,
        effective_from=WHEN + timedelta(minutes=1),
        effective_until=None,
        idempotency_key="idempotency:appointment-1",
    )
    assert value.engagement_fingerprint == engagement.fingerprint
    assert value.mandate_fingerprint == mandate.fingerprint
    assert value.acting_capacity_fingerprint == capacity.fingerprint
    with pytest.raises(LegalClientMatterRepresentationAuthorityError) as error:
        mismatched = bare(
            LegalClientActingCapacity,
            capacity_id="capacity-1",
            tenant_id="tenant-b",
            case_matter_id="matter-1",
            matter_fingerprint=HEX,
            party_id="party-1",
            subject_identity_fingerprint=HEX,
            fingerprint=HEX,
        )
        LegalClientMatterRepresentationAuthority.from_canonical(
            authority_id="representation-authority-2",
            engagement=engagement,
            mandate=mandate,
            acting_capacity=mismatched,
            representative_principal_id="principal-attorney-1",
            representative_role="LEGAL_PRACTITIONER",
            representation_scope_capabilities=["ADVISORY"],
            decision="APPOINTED",
            appointing_principal_id="principal-client-1",
            source_evidence_reference="evidence:appointment-1",
            source_evidence_fingerprint=HEX,
            authorization_evidence_reference="evidence:authorization-1",
            authorization_evidence_fingerprint=HEX,
            occurred_at=WHEN,
            effective_from=WHEN + timedelta(minutes=1),
            effective_until=None,
            idempotency_key="idempotency:appointment-2",
        )
    assert error.value.code == "L9C11_P1_UPSTREAM_LINEAGE_MISMATCH"


@pytest.mark.parametrize(
    ("field", "bad"),
    [
        ("tenant_id", "global"),
        ("representative_principal_id", ""),
        ("representative_role", "bad role"),
        ("matter_fingerprint", "not-a-fingerprint"),
        ("decision", "AUTHORIZED"),
    ],
)
def test_malformed_authority_inputs_fail_closed(field: str, bad: object) -> None:
    with pytest.raises(LegalClientMatterRepresentationAuthorityError):
        _authority(**{field: bad})


def test_domain_has_no_persistence_iam_formation_or_court_authority() -> None:
    source = Path(
        "tools/eos/legal_operations/domain/legal_client_matter_representation_authority.py"
    ).read_text()
    assert "pymongo" not in source
    assert "tenant_authorization" not in source
    assert "class LegalClientMatterRepresentation:" not in source
    assert "currentness" in source
    assert "Court" in source
    assert "Kennel EOS" in source
    assert "END OF WILSY OS SOVEREIGN ARTIFACT" in source
    assert "TODO" not in source
    assert "FIXME" not in source
    constructor_source = inspect.getsource(
        LegalClientMatterRepresentationAuthority.from_canonical
    )
    assert "from_canonical" in constructor_source
    assert "Engagement currentness" in constructor_source


def test_only_upstream_evidence_constructors_are_imported() -> None:
    module_source = Path(
        "tools/eos/legal_operations/domain/legal_client_matter_representation_authority.py"
    ).read_text()
    assert "legal_client_matter_engagement" in module_source
    assert "legal_client_matter_mandate" in module_source
    assert "legal_client_acting_capacity" in module_source
    assert "/api/" not in module_source


# ARTIFACT: test_legal_client_matter_representation_authority.py
# VERSION: v1.0.0-L9C11-P1-CLIENT-REPRESENTATION-AUTHORITY-CERT
# AUTHORITY BOUNDARY: direct pure-domain certificate only
# TENANT POSTURE: synthetic exact tenant values; no persistence
# FAIL-CLOSED POSTURE: malformed, stale, out-of-scope and tampered evidence rejects
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively
# END OF WILSY OS SOVEREIGN ARTIFACT
