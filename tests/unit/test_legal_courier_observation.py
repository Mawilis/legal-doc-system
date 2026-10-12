"""Direct adversarial certificate for Legal Operations courier observation evidence.

TITLE: Legal Operations Courier Observation Evidence Direct Certificate
VERSION: v1.0.0-L8-8A-COURIER-OBSERVATION-EVIDENCE-CERT
AUTHORITY: Wilsy OS Core Governance / Python EOS Legal Operations
EPITOME: Prove immutable courier-provider observations derive exact tenant,
         matter and process-document scope from canonical P1 evidence, preserve
         deterministic SHA3-512 integrity, reject malformed/cross-scope input,
         and never become service, return, custody, notification, Court,
         billing, payment, execution or settlement authority.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tests/unit/test_legal_courier_observation.py
COLLABORATION / OWNERSHIP: Certificate only. P1 owns CaseMatter and
                            ProcessDocument truth; L8-8A owns provider-neutral
                            courier observation normalization only.
CERTIFICATION / UPDATE DATE: 2026-10-12
CHANGELOG: 2026-10-12 v1.0.0-L8-8A-COURIER-OBSERVATION-EVIDENCE-CERT
           establishes positive scope derivation/round-trip proof plus
           cross-scope, chronology, provider-metadata, schema/fingerprint and
           downstream-authority adversarial coverage.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2; ISO 27001.
SECURITY / PRIVACY POSTURE: Synthetic opaque identifiers and hashes only.
TENANT BOUNDARY: Tenant/matter/document identities must derive from exact
                 canonical source objects; provider fields cannot widen scope.
AUTHORITY BOUNDARY: Observation evidence only; no lifecycle mutation or
                    downstream execution authority is certified here.
FINANCIAL AUTHORITY BOUNDARY: Kennel EOS remains exclusive.
FAIL-CLOSED DECLARATION: Malformed or divergent evidence must raise rather than
                         normalize, repair, infer authority or manufacture truth.
"""
from __future__ import annotations

from copy import deepcopy
from datetime import datetime, timedelta, timezone
import inspect

import pytest

import tools.eos.legal_operations.domain.legal_courier_observation as courier
from tools.eos.legal_operations.domain.legal_courier_observation import (
    LEGAL_COURIER_OBSERVATION_FIELDS,
    LegalCourierObservation,
    LegalCourierObservationError,
    LegalCourierObservationKind,
    create_legal_courier_observation,
)
from tools.eos.legal_operations.domain.legal_operations_lifecycle import (
    CaseMatter,
    ProcessDocument,
)


BASE = datetime(2026, 10, 12, 5, 0, tzinfo=timezone.utc)
FP = "a" * 128


def case_matter(
    *,
    tenant_id: str = "tenant-a",
    case_matter_id: str = "matter-1",
) -> CaseMatter:
    """Build one canonical synthetic open CaseMatter."""
    return CaseMatter(
        tenant_id=tenant_id,
        case_matter_id=case_matter_id,
        matter_reference="MAT-001",
        opened_at=BASE,
        evidence_reference="matter-registration-1",
    )


def process_document(
    *,
    tenant_id: str = "tenant-a",
    case_matter_id: str = "matter-1",
) -> ProcessDocument:
    """Build one canonical synthetic registered ProcessDocument."""
    return ProcessDocument(
        tenant_id=tenant_id,
        document_id="document-1",
        case_matter_id=case_matter_id,
        document_type="SUMMONS",
        registered_at=BASE + timedelta(minutes=1),
        registration_evidence_reference="document-registration-1",
    )


def observation(
    *,
    matter: CaseMatter | None = None,
    document: ProcessDocument | None = None,
    kind: LegalCourierObservationKind = LegalCourierObservationKind.IN_TRANSIT,
    observed_at: datetime | None = None,
) -> LegalCourierObservation:
    """Create one valid provider-neutral courier observation."""
    return create_legal_courier_observation(
        case_matter=matter or case_matter(),
        process_document=document or process_document(),
        observation_id="courier-observation-1",
        provider_key="provider-alpha",
        tracking_reference="tracking-123",
        provider_event_reference="provider-event-123",
        event_kind=kind,
        provider_status="IN_TRANSIT",
        observed_at=observed_at or BASE + timedelta(minutes=2),
        source_evidence_reference="provider-webhook:provider-event-123",
        source_evidence_fingerprint=FP,
    )


def test_derives_exact_canonical_scope_and_round_trips() -> None:
    """Provider input cannot supply tenant/matter/document truth."""
    matter = case_matter()
    document = process_document()

    value = observation(matter=matter, document=document)

    assert value.tenant_id == matter.tenant_id
    assert value.case_matter_id == matter.case_matter_id
    assert value.matter_fingerprint == matter.fingerprint
    assert value.document_id == document.document_id
    assert value.document_fingerprint == document.fingerprint
    assert value.event_kind is LegalCourierObservationKind.IN_TRANSIT
    assert len(value.fingerprint) == 128
    assert set(value.to_dict()) == set(LEGAL_COURIER_OBSERVATION_FIELDS)
    assert LegalCourierObservation.from_dict(value.to_dict()) == value


@pytest.mark.parametrize("kind", list(LegalCourierObservationKind))
def test_all_event_kinds_remain_observation_only(
    kind: LegalCourierObservationKind,
) -> None:
    """Every normalized provider status remains evidence rather than Legal truth."""
    value = observation(kind=kind)
    assert value.event_kind is kind
    assert value.tenant_id == "tenant-a"
    assert value.document_id == "document-1"


@pytest.mark.parametrize(
    ("matter", "document"),
    [
        (case_matter(tenant_id="tenant-a"), process_document(tenant_id="tenant-b")),
        (case_matter(case_matter_id="matter-a"), process_document(case_matter_id="matter-b")),
    ],
)
def test_cross_scope_sources_fail_closed(
    matter: CaseMatter,
    document: ProcessDocument,
) -> None:
    """Courier observations may not bridge tenants or matters."""
    with pytest.raises(
        LegalCourierObservationError,
        match="L8_8A_SCOPE_CORRELATION_INVALID",
    ):
        observation(matter=matter, document=document)


def test_observation_cannot_predate_canonical_sources() -> None:
    """Provider chronology before canonical registration is rejected."""
    with pytest.raises(
        LegalCourierObservationError,
        match="L8_8A_CHRONOLOGY_INVALID",
    ):
        observation(observed_at=BASE - timedelta(seconds=1))


@pytest.mark.parametrize(
    ("field", "value", "code"),
    [
        ("provider_key", " provider-alpha", "L8_8A_PROVIDER_KEY_INVALID"),
        ("provider_key", "provider alpha", "L8_8A_PROVIDER_KEY_INVALID"),
        ("tracking_reference", "", "L8_8A_TRACKING_REFERENCE_INVALID"),
        (
            "provider_event_reference",
            "event\nnewline",
            "L8_8A_PROVIDER_EVENT_REFERENCE_INVALID",
        ),
        ("provider_status", "", "L8_8A_PROVIDER_STATUS_INVALID"),
        (
            "source_evidence_fingerprint",
            "NOT-A-SHA3-512",
            "L8_8A_SOURCE_EVIDENCE_FINGERPRINT_INVALID",
        ),
    ],
)
def test_provider_metadata_is_bounded_and_fail_closed(
    field: str,
    value: object,
    code: str,
) -> None:
    """Malformed provider/provenance data never becomes normalized truth."""
    kwargs: dict[str, object] = {
        "case_matter": case_matter(),
        "process_document": process_document(),
        "observation_id": "courier-observation-1",
        "provider_key": "provider-alpha",
        "tracking_reference": "tracking-123",
        "provider_event_reference": "provider-event-123",
        "event_kind": LegalCourierObservationKind.IN_TRANSIT,
        "provider_status": "IN_TRANSIT",
        "observed_at": BASE + timedelta(minutes=2),
        "source_evidence_reference": "provider-webhook:provider-event-123",
        "source_evidence_fingerprint": FP,
    }
    kwargs[field] = value
    with pytest.raises(LegalCourierObservationError, match=code):
        create_legal_courier_observation(**kwargs)  # type: ignore[arg-type]


def test_hydration_rejects_schema_and_fingerprint_drift() -> None:
    """Persisted observation corruption is never repaired silently."""
    payload = observation().to_dict()

    extra = deepcopy(payload)
    extra["service_completed"] = True
    with pytest.raises(
        LegalCourierObservationError,
        match="L8_8A_SCHEMA_INVALID",
    ):
        LegalCourierObservation.from_dict(extra)

    corrupted = deepcopy(payload)
    corrupted["provider_status"] = "DELIVERED"
    with pytest.raises(
        LegalCourierObservationError,
        match="L8_8A_FINGERPRINT_MISMATCH",
    ):
        LegalCourierObservation.from_dict(corrupted)


def test_invalid_event_vocabulary_is_rejected_on_hydration() -> None:
    """Unknown provider vocabulary cannot expand the canonical enum."""
    payload = observation().to_dict()
    payload["event_kind"] = "SERVICE_COMPLETED"
    with pytest.raises(
        LegalCourierObservationError,
        match="L8_8A_PAYLOAD_INVALID",
    ):
        LegalCourierObservation.from_dict(payload)


def test_direct_construction_still_requires_valid_canonical_integrity() -> None:
    """Even direct dataclass construction cannot bypass validation."""
    payload = observation().to_dict()
    payload.pop("fingerprint")
    payload["tenant_id"] = "global"
    payload["event_kind"] = LegalCourierObservationKind.IN_TRANSIT
    with pytest.raises(LegalCourierObservationError):
        LegalCourierObservation(**payload)  # type: ignore[arg-type]


def test_source_contains_no_downstream_mutation_authority() -> None:
    """Static authority firewall excludes Legal lifecycle and financial execution."""
    source = inspect.getsource(courier)

    forbidden_calls = (
        ".transition_to(",
        "ServiceExecution.from_attempt(",
        "ReturnOfService.from_service_execution(",
        "insert_one(",
        "update_one(",
        "replace_one(",
        "delete_one(",
        "payment_execute",
        "settlement_execute",
        "invoice_issue",
        "notification_send",
        "court_file",
    )
    for token in forbidden_calls:
        assert token not in source

    assert "DELIVERY_REPORTED" in source
    assert "external observations" in source
    assert "Kennel EOS" in source


# ARTIFACT: test_legal_courier_observation.py
# VERSION: v1.0.0-L8-8A-COURIER-OBSERVATION-EVIDENCE-CERT
# AUTHORITY BOUNDARY: direct certificate only; no runtime, provider, lifecycle or financial authority
# TENANT POSTURE: exact canonical source correlation is adversarially certified
# FAIL-CLOSED POSTURE: malformed, cross-scope and corrupted evidence must reject
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively
# END OF WILSY OS SOVEREIGN ARTIFACT
