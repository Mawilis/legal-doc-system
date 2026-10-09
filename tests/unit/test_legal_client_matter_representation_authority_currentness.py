"""Direct certificate for L9C11-P21A client-authority currentness.

TITLE: WILSY OS Legal Client Representation Authority Currentness Certificate
VERSION: v1.1.0-L9C11-P21A-CLIENT-REPRESENTATION-AUTHORITY-CURRENTNESS-CERT
AUTHORITY: Wilsy OS Core Governance / Python EOS Legal Operations
EPITOME: Certify the pure representative-specific P1-history projection for
         explicit time, strict hydration, duplicate normalization, ambiguity,
         corruption, deterministic integrity and authority-boundary exclusions.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tests/unit/test_legal_client_matter_representation_authority_currentness.py
COLLABORATION / OWNERSHIP: P1 immutable authority and P7 history remain
                            read-only precedents. This certificate exercises
                            only the P21A pure domain; it performs no Mongo,
                            IAM, firm decision, Representation, Court or
                            financial work.
CERTIFICATION / UPDATE DATE: 2026-09-28
TRANSACTION BOUNDARY: Pure in-memory synthetic P1 values; no network or
                      persistence.
FAIL-CLOSED DECLARATION: Invalid, cross-lineage, contradictory or corrupt
                         evidence never becomes positive currentness.
"""
from __future__ import annotations

import ast
from dataclasses import FrozenInstanceError
from datetime import datetime, timedelta, timezone
from itertools import permutations
from pathlib import Path
from typing import Any, cast

import pytest

from tools.eos.legal_operations.domain.legal_client_matter_representation_authority import (
    LegalClientMatterRepresentationAuthority,
    LegalClientMatterRepresentationAuthorityDecision,
)
from tools.eos.legal_operations.domain.legal_client_matter_representation_authority_currentness import (
    SCHEMA,
    VERSION,
    LegalClientMatterRepresentationAuthorityCurrentness,
    LegalClientMatterRepresentationAuthorityCurrentnessError,
    LegalClientMatterRepresentationAuthorityCurrentnessState,
    project_legal_client_matter_representation_authority_currentness,
)


BASE = datetime(2026, 9, 28, 10, 0, 0, 123456, tzinfo=timezone.utc)
TENANT = "tenant-l9c11-p21a"
MATTER = "matter-l9c11-p21a"
PARTY = "party-l9c11-p21a"
SUBJECT = "b" * 128
MATTER_FP = "a" * 128


def authority(
    *,
    authority_id: str = "authority-l9c11-p21a-1",
    decision: str = "APPOINTED",
    effective_from: datetime = BASE,
    effective_until: datetime | None = None,
    tenant_id: str = TENANT,
    representative_principal_id: str = "principal-l9c11-p21a",
    representative_role: str = "LEGAL_PRACTITIONER",
    representation_scope_capabilities: tuple[str, ...] = ("ADVISORY",),
) -> LegalClientMatterRepresentationAuthority:
    """Build one valid immutable P1 snapshot without persistence or IAM."""
    suffix = authority_id
    return LegalClientMatterRepresentationAuthority(
        authority_id=authority_id,
        tenant_id=tenant_id,
        case_matter_id=MATTER,
        matter_fingerprint=MATTER_FP,
        client_party_id=PARTY,
        subject_reference="client:subject-l9c11-p21a",
        subject_identity_fingerprint=SUBJECT,
        engagement_id="engagement-l9c11-p21a",
        engagement_fingerprint="c" * 128,
        mandate_id="mandate-l9c11-p21a",
        mandate_fingerprint="d" * 128,
        mandate_scope_reference="scope:l9c11:p21a",
        mandate_scope_fingerprint="e" * 128,
        mandate_capabilities=("ADVISORY", "NEGOTIATION"),
        acting_capacity_id="capacity-l9c11-p21a",
        acting_capacity_fingerprint="f" * 128,
        representative_principal_id=representative_principal_id,
        representative_role=representative_role,
        representation_scope_capabilities=representation_scope_capabilities,
        decision=decision,
        appointing_principal_id="principal-client-l9c11-p21a",
        source_evidence_reference=f"source:{suffix}",
        source_evidence_fingerprint="1" * 128,
        authorization_evidence_reference=f"authorization:{suffix}",
        authorization_evidence_fingerprint="2" * 128,
        occurred_at=effective_from,
        effective_from=effective_from,
        effective_until=effective_until or effective_from + timedelta(days=30),
        idempotency_key=f"idempotency:{suffix}",
    )


def project(
    values: tuple[LegalClientMatterRepresentationAuthority, ...],
    *,
    at: datetime = BASE + timedelta(hours=1),
    **context: object,
) -> LegalClientMatterRepresentationAuthorityCurrentness:
    """Project synthetic values through the public P21A function."""
    return project_legal_client_matter_representation_authority_currentness(
        tenant_id=cast(str, context.get("tenant_id", TENANT)),
        case_matter_id=cast(str, context.get("case_matter_id", MATTER)),
        matter_fingerprint=cast(str, context.get("matter_fingerprint", MATTER_FP)),
        client_party_id=cast(str, context.get("client_party_id", PARTY)),
        subject_identity_fingerprint=cast(str, context.get("subject_identity_fingerprint", SUBJECT)),
        representative_principal_id=cast(
            str, context.get("representative_principal_id", "principal-l9c11-p21a")
        ),
        evaluated_at=at,
        authorities=values,
    )


def test_version_schema_states_immutability_and_positive_predicate() -> None:
    result = project(())
    assert VERSION == "v1.1.0-L9C11-P21A-CLIENT-REPRESENTATION-AUTHORITY-CURRENTNESS"
    assert SCHEMA == "WILSY-LEGAL-CLIENT-MATTER-REPRESENTATION-AUTHORITY-CURRENTNESS/V2"
    assert [state.value for state in LegalClientMatterRepresentationAuthorityCurrentnessState] == [
        "NO_AUTHORITY", "APPOINTED", "DECLINED", "REQUIRES_REVIEW", "AMBIGUOUS", "CORRUPT_BLOCKED"
    ]
    assert result.state is LegalClientMatterRepresentationAuthorityCurrentnessState.NO_AUTHORITY
    assert result.representative_role is None
    assert result.representation_scope_capabilities == ()
    assert result.is_currently_appointed is False
    assert result.is_usable is False
    with pytest.raises(FrozenInstanceError):
        setattr(result, "state", "APPOINTED")


def test_explicit_aware_time_and_zero_clock_reads() -> None:
    with pytest.raises(LegalClientMatterRepresentationAuthorityCurrentnessError):
        project((), at=datetime(2026, 9, 28, 10, 0))
    source = Path("tools/eos/legal_operations/domain/legal_client_matter_representation_authority_currentness.py").read_text()
    assert "datetime.now" not in source
    assert "datetime.utcnow" not in source


def test_empty_history_is_no_authority() -> None:
    result = project(())
    assert result.state is LegalClientMatterRepresentationAuthorityCurrentnessState.NO_AUTHORITY
    assert result.candidate_authority_ids == ()
    assert result.normalized_authority_count == 0


@pytest.mark.parametrize("state", ["APPOINTED", "DECLINED", "REQUIRES_REVIEW"])
def test_single_state_and_only_appointed_is_positive(state: str) -> None:
    result = project((authority(decision=state),))
    assert str(getattr(result.state, "value", result.state)) == state
    assert result.is_currently_appointed is (state == "APPOINTED")
    assert result.is_usable is (state == "APPOINTED")
    if state == "APPOINTED":
        assert result.representative_role == "LEGAL_PRACTITIONER"
        assert result.representation_scope_capabilities == ("ADVISORY",)
    else:
        assert result.representative_role is None
        assert result.representation_scope_capabilities == ()


@pytest.mark.parametrize("state", ["APPOINTED", "DECLINED", "REQUIRES_REVIEW"])
def test_future_rows_are_excluded_without_clock_reads(state: str) -> None:
    result = project((authority(decision=state, effective_from=BASE + timedelta(days=1)),), at=BASE)
    assert result.state is LegalClientMatterRepresentationAuthorityCurrentnessState.NO_AUTHORITY
    assert result.candidate_authority_ids == ()
    assert result.normalized_authority_count == 1
    assert result.representative_role is None
    assert result.representation_scope_capabilities == ()


@pytest.mark.parametrize("state", ["APPOINTED", "DECLINED", "REQUIRES_REVIEW"])
def test_exact_duplicates_are_one_semantic_authority(state: str) -> None:
    value = authority(decision=state)
    result = project((value, value, value))
    assert str(getattr(result.state, "value", result.state)) == state
    assert result.normalized_authority_count == 1
    assert result.eligible_authority_count == 1


@pytest.mark.parametrize(
    "left,right",
    [("APPOINTED", "APPOINTED"), ("APPOINTED", "DECLINED"), ("APPOINTED", "REQUIRES_REVIEW"),
     ("DECLINED", "REQUIRES_REVIEW"), ("DECLINED", "DECLINED")],
)
def test_distinct_eligible_rows_are_ambiguous_without_latest_wins(left: str, right: str) -> None:
    result = project((authority(authority_id="authority-left", decision=left), authority(authority_id="authority-right", decision=right)))
    assert result.state is LegalClientMatterRepresentationAuthorityCurrentnessState.AMBIGUOUS
    assert result.is_currently_appointed is False
    assert result.decisive_authority_id is None
    assert result.eligible_authority_count == 2
    assert result.representative_role is None
    assert result.representation_scope_capabilities == ()


def test_later_effective_row_does_not_supersede_earlier() -> None:
    result = project((
        authority(authority_id="authority-early", decision="APPOINTED", effective_from=BASE - timedelta(minutes=2)),
        authority(authority_id="authority-late", decision="DECLINED", effective_from=BASE),
    ))
    assert result.state is LegalClientMatterRepresentationAuthorityCurrentnessState.AMBIGUOUS
    assert result.candidate_authority_ids == ("authority-early", "authority-late")


def test_same_effective_distinct_rows_are_ambiguous() -> None:
    result = project((authority(authority_id="authority-a"), authority(authority_id="authority-b")))
    assert result.state is LegalClientMatterRepresentationAuthorityCurrentnessState.AMBIGUOUS


def test_scope_and_identity_fingerprint_differences_are_distinct() -> None:
    scoped = authority(authority_id="authority-scoped", representation_scope_capabilities=("NEGOTIATION",))
    different_id = authority(authority_id="authority-different-id")
    result = project((scoped, different_id))
    assert result.state is LegalClientMatterRepresentationAuthorityCurrentnessState.AMBIGUOUS
    assert len(set(result.candidate_authority_fingerprints)) == 2


def test_positive_projection_binds_role_scope_and_fingerprint_changes() -> None:
    baseline = project((authority(),))
    changed_role = project((authority(representative_role="LEGAL_ATTORNEY"),))
    changed_scope = project((authority(representation_scope_capabilities=("NEGOTIATION", "ADVISORY")),))
    assert baseline.representative_role == "LEGAL_PRACTITIONER"
    assert baseline.representation_scope_capabilities == ("ADVISORY",)
    assert changed_role.representative_role == "LEGAL_ATTORNEY"
    assert changed_scope.representation_scope_capabilities == ("ADVISORY", "NEGOTIATION")
    assert changed_role.fingerprint != baseline.fingerprint
    assert changed_scope.fingerprint != baseline.fingerprint


def test_representative_dimension_is_exact_p7_lineage() -> None:
    wrong_representative = authority(
        authority_id="authority-other-representative",
        representative_principal_id="principal-other",
    )
    result = project((wrong_representative,))
    assert result.state is LegalClientMatterRepresentationAuthorityCurrentnessState.CORRUPT_BLOCKED
    assert result.corruption_evidence_fingerprints


def test_mixed_valid_and_corrupt_fails_closed() -> None:
    valid = authority()
    corrupt = cast(Any, authority(authority_id="authority-corrupt"))
    object.__setattr__(corrupt, "fingerprint", "not-a-fingerprint")
    result = project((valid, corrupt))
    assert result.state is LegalClientMatterRepresentationAuthorityCurrentnessState.CORRUPT_BLOCKED
    assert result.is_currently_appointed is False
    assert result.representative_role is None
    assert result.representation_scope_capabilities == ()


def test_cross_tenant_row_is_corruption_not_absence() -> None:
    result = project((authority(tenant_id="tenant-other"),))
    assert result.state is LegalClientMatterRepresentationAuthorityCurrentnessState.CORRUPT_BLOCKED
    assert result.representative_role is None
    assert result.representation_scope_capabilities == ()


def test_explicit_effective_until_is_not_invented_expiry() -> None:
    value = authority(
        effective_from=BASE - timedelta(days=2),
        effective_until=BASE - timedelta(days=1),
    )
    result = project((value,))
    assert result.state is LegalClientMatterRepresentationAuthorityCurrentnessState.APPOINTED


def test_projection_is_order_independent_and_fingerprint_deterministic() -> None:
    values = (
        authority(authority_id="authority-a", decision="APPOINTED", effective_from=BASE - timedelta(minutes=2)),
        authority(authority_id="authority-b", decision="DECLINED", effective_from=BASE - timedelta(minutes=1)),
        authority(authority_id="authority-future", effective_from=BASE + timedelta(days=1)),
    )
    results = [project(order) for order in permutations(values)]
    assert all(result == results[0] for result in results)
    assert all(result.fingerprint == results[0].fingerprint for result in results)


def test_serialization_hydration_and_strict_schema() -> None:
    result = project((authority(),))
    assert result.to_dict()["representative_role"] == "LEGAL_PRACTITIONER"
    assert result.to_dict()["representation_scope_capabilities"] == ["ADVISORY"]
    assert LegalClientMatterRepresentationAuthorityCurrentness.from_dict(result.to_dict()) == result
    invalid = result.to_dict()
    invalid["unexpected"] = True
    with pytest.raises(LegalClientMatterRepresentationAuthorityCurrentnessError):
        LegalClientMatterRepresentationAuthorityCurrentness.from_dict(invalid)
    tampered = result.to_dict()
    tampered["state"] = "DECLINED"
    with pytest.raises(LegalClientMatterRepresentationAuthorityCurrentnessError):
        LegalClientMatterRepresentationAuthorityCurrentness.from_dict(tampered)


def test_corrupt_type_and_strict_hydration_fail_closed() -> None:
    result = project((cast(Any, object()),))
    assert result.state is LegalClientMatterRepresentationAuthorityCurrentnessState.CORRUPT_BLOCKED
    malformed = cast(Any, authority())
    object.__setattr__(malformed, "decision", "NOT_A_DECISION")
    blocked = project((malformed,))
    assert blocked.state is LegalClientMatterRepresentationAuthorityCurrentnessState.CORRUPT_BLOCKED
    assert blocked.representative_role is None
    assert blocked.representation_scope_capabilities == ()


def test_no_lifecycle_or_downstream_authority_is_created() -> None:
    source = Path("tools/eos/legal_operations/domain/legal_client_matter_representation_authority_currentness.py").read_text()
    tree = ast.parse(source)
    names = {node.id for node in ast.walk(tree) if isinstance(node, ast.Name)}
    assert "datetime" in names
    assert "revocation" in source.lower()
    assert "supersession" in source.lower()
    assert "latest-wins" in source.lower()
    assert "LegalClientMatterRepresentationAuthorityRegistry" not in source
    assert "MongoClient" not in source


# ARTIFACT: test_legal_client_matter_representation_authority_currentness.py
# VERSION: v1.1.0-L9C11-P21A-CLIENT-REPRESENTATION-AUTHORITY-CURRENTNESS-CERT
# AUTHORITY BOUNDARY: direct pure-domain P21A certificate only
# TENANT POSTURE: exact representative-specific lineage
# FAIL-CLOSED POSTURE: corruption and multiplicity never become appointed
# FINANCIAL EXECUTION AUTHORITY: none; Kennel EOS exclusively
# END OF WILSY OS SOVEREIGN ARTIFACT
