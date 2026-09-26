"""Direct certificate for the L9A4-P1B matter-review instrument domain.

TITLE: WILSY OS Legal Client Matter Acceptance Instrument Certificate
VERSION: v1.0.0-L9A4-P1B-CLIENT-MATTER-ACCEPTANCE-INSTRUMENT-CERT
AUTHORITY: Direct adversarial certification of immutable reviewable material.
EPITOME: Prove exact CaseMatter binding, version/content/provenance identity,
         UTC chronology, supersession integrity, strict hydration and the
         absence of acceptance, engagement, visibility or financial authority.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tests/unit/test_legal_client_matter_acceptance_instrument.py
COLLABORATION / OWNERSHIP: The L9A4-P1B domain is the only production subject;
                            this certificate uses synthetic opaque evidence and
                            does not create a registry, acceptance or IAM path.
CERTIFICATION / UPDATE DATE: 2026-09-26
CHANGELOG: v1.0.0-L9A4-P1B-CLIENT-MATTER-ACCEPTANCE-INSTRUMENT-CERT proves
           construction, immutability, exact matter binding, content and
           approval provenance, chronology, supersession, fingerprints,
           corruption rejection and authority exclusions.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2; ISO 27001.
SECURITY / PRIVACY POSTURE: Synthetic opaque values only; no live database,
                             network, credentials, tokens or raw client PII.
TENANT BOUNDARY: Fixtures derive tenant/matter only from one exact CaseMatter.
AUTHORITY BOUNDARY: Pure reviewable instrument metadata only; no acceptance,
                    engagement, representation, Court, visibility or finance.
FINANCIAL AUTHORITY BOUNDARY: None; Kennel EOS remains exclusive.
"""
from __future__ import annotations

from dataclasses import fields
from datetime import datetime, timezone
import hashlib
import inspect
from typing import Any, cast

import pytest

from tools.eos.legal_operations.domain.legal_client_matter_acceptance_instrument import (
    INSTRUMENT_FIELDS,
    SCHEMA,
    VERSION,
    LegalClientMatterAcceptanceInstrument,
    LegalClientMatterAcceptanceInstrumentError,
    record_legal_client_matter_acceptance_instrument,
)
from tools.eos.legal_operations.domain.legal_operations_lifecycle import CaseMatter


UTC = timezone.utc
MOMENT = datetime(2026, 9, 26, 8, 7, 6, 123456, tzinfo=UTC)
MATTER = CaseMatter(
    tenant_id="tenant-review",
    case_matter_id="matter-001",
    matter_reference="matter-reference-001",
    opened_at=MOMENT,
    evidence_reference="evidence:matter-open-001",
)
CONTENT = hashlib.sha3_512(b"synthetic-review-content-v1").hexdigest()
APPROVAL = hashlib.sha3_512(b"synthetic-approval-evidence-v1").hexdigest()


def _instrument(**changes: object) -> LegalClientMatterAcceptanceInstrument:
    values: dict[str, Any] = {
        "case_matter": MATTER,
        "instrument_id": "matter-instrument-001",
        "version": "1.0.0",
        "instrument_kind": "MATTER_REVIEW",
        "title": "Matter Information Review",
        "review_scope": "Review the bounded matter material before any later decision.",
        "content_reference": "artifact:matter-001/instrument-001/v1",
        "content_fingerprint": CONTENT,
        "created_at": MOMENT,
        "effective_from": MOMENT,
        "approval_evidence_reference": "approval:matter-001/instrument-001/v1",
        "approval_evidence_fingerprint": APPROVAL,
    }
    values.update(changes)
    return record_legal_client_matter_acceptance_instrument(**values)


def _direct(**changes: object) -> LegalClientMatterAcceptanceInstrument:
    value = _instrument(**changes)
    return LegalClientMatterAcceptanceInstrument(**cast(Any, value.to_dict()))


def _reject(**changes: object) -> None:
    with pytest.raises(LegalClientMatterAcceptanceInstrumentError):
        _instrument(**changes)


def test_valid_instrument_binds_exact_matter_and_all_reviewable_fields() -> None:
    value = _instrument()
    assert value.tenant_id == MATTER.tenant_id
    assert value.case_matter_id == MATTER.case_matter_id
    assert value.matter_fingerprint == MATTER.fingerprint
    assert value.instrument_id == "matter-instrument-001"
    assert value.version == "1.0.0"
    assert value.version_id == "matter-instrument-001:1.0.0"
    assert value.instrument_kind == "MATTER_REVIEW"
    assert value.title == "Matter Information Review"
    assert value.review_scope.startswith("Review the bounded")
    assert value.content_reference.startswith("artifact:")
    assert value.content_fingerprint == CONTENT
    assert value.approval_evidence_reference.startswith("approval:")
    assert value.approval_evidence_fingerprint == APPROVAL


def test_instrument_is_frozen_and_semantic_mutation_changes_fingerprint() -> None:
    value = _instrument()
    with pytest.raises((AttributeError, TypeError)):
        value.title = "changed"  # type: ignore[misc]
    changed = _instrument(review_scope="A materially different bounded review scope.")
    assert changed.fingerprint != value.fingerprint


def test_tenant_and_case_matter_are_derived_from_exact_open_case_matter() -> None:
    other = CaseMatter(
        tenant_id="tenant-other",
        case_matter_id="matter-other",
        matter_reference="matter-reference-other",
        opened_at=MOMENT,
        evidence_reference="evidence:matter-open-other",
    )
    value = record_legal_client_matter_acceptance_instrument(
        case_matter=other,
        instrument_id="matter-instrument-001",
        version="1.0.0",
        instrument_kind="MATTER_REVIEW",
        title="Matter Information Review",
        review_scope="Review the bounded matter material before any later decision.",
        content_reference="artifact:matter-other/instrument-001/v1",
        content_fingerprint=CONTENT,
        created_at=MOMENT,
        effective_from=MOMENT,
        approval_evidence_reference="approval:matter-other/instrument-001/v1",
        approval_evidence_fingerprint=APPROVAL,
    )
    assert value.tenant_id == "tenant-other"
    assert value.case_matter_id == "matter-other"
    assert value.matter_fingerprint == other.fingerprint


def test_closed_matter_cannot_create_new_instrument() -> None:
    closed = MATTER.transition_to(
        type(MATTER.state).CLOSED,
        evidence_reference="evidence:matter-closed-001",
        occurred_at=datetime(2026, 9, 27, tzinfo=UTC),
    )
    with pytest.raises(LegalClientMatterAcceptanceInstrumentError):
        record_legal_client_matter_acceptance_instrument(
            case_matter=closed,
            instrument_id="matter-instrument-001",
            version="1.0.0",
            instrument_kind="MATTER_REVIEW",
            title="Matter Information Review",
            review_scope="Review the bounded matter material before any later decision.",
            content_reference="artifact:matter-001/instrument-001/v1",
            content_fingerprint=CONTENT,
            created_at=MOMENT,
            effective_from=MOMENT,
            approval_evidence_reference="approval:matter-001/instrument-001/v1",
            approval_evidence_fingerprint=APPROVAL,
        )


def test_first_version_without_supersession_and_later_supersession_bind_exact_id() -> None:
    first = _instrument()
    second = _instrument(
        version="2.0.0",
        content_reference="artifact:matter-001/instrument-001/v2",
        content_fingerprint=hashlib.sha3_512(b"synthetic-review-content-v2").hexdigest(),
        approval_evidence_reference="approval:matter-001/instrument-001/v2",
        approval_evidence_fingerprint=hashlib.sha3_512(b"synthetic-approval-evidence-v2").hexdigest(),
        supersedes_version_id=first.version_id,
    )
    assert first.supersedes_version_id is None
    assert second.supersedes_version_id == first.version_id
    assert second.version_id != first.version_id


def test_self_supersession_is_rejected() -> None:
    _reject(supersedes_version_id="matter-instrument-001:1.0.0")


def test_utc_chronology_preserves_microseconds_and_naive_is_rejected() -> None:
    value = _instrument()
    assert value.created_at == MOMENT
    assert value.effective_from.microsecond == 123456
    assert value.to_dict()["created_at"] == "2026-09-26T08:07:06.123456Z"
    _reject(created_at=datetime(2026, 9, 26, 8, 7, 6))
    _reject(effective_from=datetime(2026, 9, 26, 8, 7, 6))


def test_fingerprint_is_deterministic_and_exact_round_trip_hydrates() -> None:
    value = _instrument()
    same = _instrument()
    assert value.fingerprint == same.fingerprint
    hydrated = LegalClientMatterAcceptanceInstrument.from_dict(value.to_dict())
    assert hydrated == value
    assert hydrated.to_dict() == value.to_dict()


@pytest.mark.parametrize(
    "field,value",
    [
        ("tenant_id", "default"),
        ("tenant_id", ""),
        ("case_matter_id", "bad matter"),
        ("matter_fingerprint", "g" * 128),
        ("instrument_id", " instrument"),
        ("version", ""),
        ("instrument_kind", "kind\ninvalid"),
        ("title", ""),
        ("title", "x" * 201),
        ("review_scope", "x" * 1001),
        ("content_reference", "artifact:\ninvalid"),
        ("content_fingerprint", "A" * 128),
        ("approval_evidence_reference", "approval:\x00invalid"),
        ("approval_evidence_fingerprint", "z" * 128),
    ],
)
def test_malformed_metadata_rejects(field: str, value: object) -> None:
    if field in {"tenant_id", "case_matter_id", "matter_fingerprint"}:
        payload = _instrument().to_dict()
        payload[field] = value
        with pytest.raises(LegalClientMatterAcceptanceInstrumentError):
            LegalClientMatterAcceptanceInstrument.from_dict(payload)
    else:
        _reject(**{field: value})


def test_surrogate_and_control_metadata_reject() -> None:
    _reject(title="valid\ud800title")
    _reject(review_scope="valid\x01scope")


def test_approval_evidence_is_referenced_not_created_or_verified_here() -> None:
    value = _instrument(
        approval_evidence_reference="external:approved-artifact",
        approval_evidence_fingerprint=hashlib.sha3_512(b"external").hexdigest(),
    )
    assert value.approval_evidence_reference == "external:approved-artifact"


def test_schema_and_fingerprint_tampering_rejects() -> None:
    value = _instrument()
    payload = value.to_dict()
    payload["schema"] = SCHEMA + "/tampered"
    with pytest.raises(LegalClientMatterAcceptanceInstrumentError):
        LegalClientMatterAcceptanceInstrument.from_dict(payload)
    payload = value.to_dict()
    payload["fingerprint"] = "0" * 128
    with pytest.raises(LegalClientMatterAcceptanceInstrumentError):
        LegalClientMatterAcceptanceInstrument.from_dict(payload)


def test_extra_or_missing_fields_reject() -> None:
    value = _instrument().to_dict()
    extra = dict(value)
    extra["party_id"] = "party-should-be-later"
    with pytest.raises(LegalClientMatterAcceptanceInstrumentError):
        LegalClientMatterAcceptanceInstrument.from_dict(extra)
    missing = dict(value)
    del missing["review_scope"]
    with pytest.raises(LegalClientMatterAcceptanceInstrumentError):
        LegalClientMatterAcceptanceInstrument.from_dict(missing)
    assert set(value) == INSTRUMENT_FIELDS


def test_content_and_version_identity_are_immutable_semantics() -> None:
    value = _instrument()
    altered_content = _instrument(
        content_fingerprint=hashlib.sha3_512(b"different-content").hexdigest(),
    )
    altered_version = _instrument(version="1.0.1")
    assert altered_content.fingerprint != value.fingerprint
    assert altered_version.version_id != value.version_id
    assert altered_version.fingerprint != value.fingerprint


def test_domain_has_no_party_acceptance_engagement_visibility_court_or_finance_state() -> None:
    names = {field.name for field in fields(LegalClientMatterAcceptanceInstrument)}
    forbidden = {
        "party_id", "subject_reference", "actor_principal_id", "accepted_at",
        "acceptance_id", "engagement_id", "retainer_id", "mandate_id",
        "representation_id", "court_proceeding_id", "visibility_grant_id",
        "fee", "invoice_id", "payment_id", "settlement_id",
    }
    assert not names & forbidden
    assert "review_scope" in names
    assert "approval_evidence_reference" in names


def test_domain_is_pure_and_requires_no_raw_pii_or_runtime_authority() -> None:
    source = inspect.getsource(__import__(
        "tools.eos.legal_operations.domain.legal_client_matter_acceptance_instrument",
        fromlist=["*"],
    ))
    forbidden_imports = (
        "pymongo", "kernel.db", "requests", "httpx", "jwt", "LegalClientAcceptance",
        "LegalClientActingCapacityRegistry", "Engagement", "Representation",
    )
    assert not any(token in source for token in forbidden_imports)
    assert "client_name" not in source
    assert "email" not in source
    assert "identity_number" not in source


def test_public_contract_and_version_are_exact() -> None:
    assert VERSION == "v1.0.0-L9A4-P1B-CLIENT-MATTER-ACCEPTANCE-INSTRUMENT"
    assert SCHEMA == "WILSY-LEGAL-CLIENT-MATTER-ACCEPTANCE-INSTRUMENT/V1"
    assert "case_matter" in inspect.signature(
        record_legal_client_matter_acceptance_instrument
    ).parameters


# ARTIFACT: test_legal_client_matter_acceptance_instrument.py
# VERSION: v1.0.0-L9A4-P1B-CLIENT-MATTER-ACCEPTANCE-INSTRUMENT-CERT
# AUTHORITY BOUNDARY: pure matter-review instrument evidence certificate only
# TENANT POSTURE: every fixture derives tenant/matter from exact CaseMatter
# FAIL-CLOSED POSTURE: malformed, tampered, extra, naive and authority-bearing state rejects
# FINANCIAL EXECUTION AUTHORITY: none; Kennel EOS exclusively
# END OF WILSY OS SOVEREIGN ARTIFACT
