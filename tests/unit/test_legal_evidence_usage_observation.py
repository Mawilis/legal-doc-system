"""Direct certificate for immutable Legal Evidence usage observations.

TITLE: Legal Evidence Usage Observation Direct Certificate
VERSION: v1.0.0-L10A2Q-P3A-LEGAL-EVIDENCE-USAGE-OBSERVATION-CERT
AUTHORITY: WILSY OS Core Governance
PURPOSE:
    Prove that one usage observation is derived only from one canonical
    LegalEvidenceContent value after Legal Evidence content truth exists.

EPITOME:
    PROVIDER OBJECT COMPLETE
    != LEGAL EVIDENCE COMMITTED
    != USAGE OBSERVED
    != REMAINING CAPACITY
    != CAPACITY RESERVED
    != STORAGE ADMISSION

CERTIFICATION / UPDATE DATE: 2026-09-29

TENANT POSTURE:
    Usage preserves the exact canonical LegalEvidenceContent tenant, matter,
    document and content identity. No caller-selected tenant override exists.

AUTHORITY BOUNDARY:
    Immutable observed consumption only. No capacity derivation, reservation,
    admission, entitlement mutation, billing, payment, settlement or execution.

FAIL-CLOSED POSTURE:
    Invalid canonical content, malformed identity/time, schema drift and
    fingerprint divergence reject.
"""

from __future__ import annotations

from dataclasses import FrozenInstanceError
from datetime import datetime, timezone
import inspect

import pytest

from tools.eos.legal_operations.domain.legal_evidence_content import (
    LegalEvidenceContent,
    register_legal_evidence_content,
)
from tools.eos.legal_operations.domain.legal_evidence_usage_observation import (
    LegalEvidenceUsageObservation,
    LegalEvidenceUsageObservationError,
    observe_legal_evidence_usage,
)


STAMP = datetime(2026, 9, 29, 20, 30, tzinfo=timezone.utc)
CONTENT = b"WILSY legal evidence usage observation certificate"
SOURCE_FP = "a" * 128


def _content() -> LegalEvidenceContent:
    return register_legal_evidence_content(
        tenant_id="tenant-l10a2q-p3a",
        case_matter_id="matter-l10a2q-p3a",
        document_id="document-l10a2q-p3a",
        media_type="application/pdf",
        original_filename="usage-certificate.pdf",
        content=CONTENT,
        source_evidence_reference="source:l10a2q-p3a",
        source_evidence_fingerprint=SOURCE_FP,
        registered_at=STAMP,
    )


def test_canonical_content_derives_exact_usage_observation() -> None:
    content = _content()

    observed = observe_legal_evidence_usage(content=content)

    assert isinstance(observed, LegalEvidenceUsageObservation)
    assert observed.tenant_id == content.tenant_id
    assert observed.case_matter_id == content.case_matter_id
    assert observed.document_id == content.document_id
    assert observed.content_reference == content.content_reference
    assert observed.content_fingerprint == content.content_fingerprint
    assert observed.content_evidence_fingerprint == content.fingerprint

    assert observed.storage_bytes_added == content.content_length
    assert observed.monthly_ingress_bytes == content.content_length
    assert observed.document_versions_added == 1

    assert observed.occurred_at == content.registered_at
    assert len(observed.fingerprint) == 128
    int(observed.fingerprint, 16)


def test_identical_canonical_content_derives_identical_observation() -> None:
    first = observe_legal_evidence_usage(content=_content())
    second = observe_legal_evidence_usage(content=_content())

    assert first == second
    assert first.usage_observation_id == second.usage_observation_id
    assert first.fingerprint == second.fingerprint


def test_observation_is_immutable() -> None:
    observed = observe_legal_evidence_usage(content=_content())

    with pytest.raises(FrozenInstanceError):
        observed.storage_bytes_added = 0  # type: ignore[misc]


def test_observation_round_trip_preserves_exact_fingerprint() -> None:
    observed = observe_legal_evidence_usage(content=_content())

    hydrated = LegalEvidenceUsageObservation.from_dict(observed.to_dict())

    assert hydrated == observed
    assert hydrated.fingerprint == observed.fingerprint


def test_fingerprint_corruption_rejects() -> None:
    observed = observe_legal_evidence_usage(content=_content())
    payload = observed.to_dict()
    payload["fingerprint"] = "f" * 128

    with pytest.raises(
        LegalEvidenceUsageObservationError,
        match="L10A2Q_P3A_FINGERPRINT_MISMATCH",
    ):
        LegalEvidenceUsageObservation.from_dict(payload)


def test_pseudo_tenant_rejects_on_hydration() -> None:
    observed = observe_legal_evidence_usage(content=_content())
    payload = observed.to_dict()
    payload["tenant_id"] = "global"
    payload["fingerprint"] = ""

    with pytest.raises(
        LegalEvidenceUsageObservationError,
        match="L10A2Q_P3A_TENANT_REQUIRED",
    ):
        LegalEvidenceUsageObservation.from_dict(payload)


def test_usage_dimensions_are_not_caller_authority() -> None:
    signature = inspect.signature(observe_legal_evidence_usage)

    assert tuple(signature.parameters) == ("content",)

    forbidden = {
        "tenant_id",
        "case_matter_id",
        "document_id",
        "content_reference",
        "content_length",
        "storage_bytes_added",
        "monthly_ingress_bytes",
        "document_versions_added",
        "price",
        "amount",
        "quota",
        "remaining_capacity",
        "reservation_id",
    }

    assert forbidden.isdisjoint(signature.parameters)


def test_serialized_surface_contains_no_capacity_or_financial_authority() -> None:
    keys = set(observe_legal_evidence_usage(content=_content()).to_dict())

    assert "remaining_storage_bytes" not in keys
    assert "remaining_ingress_bytes" not in keys
    assert "capacity_limit_bytes" not in keys
    assert "reservation_id" not in keys
    assert "admitted" not in keys
    assert "price" not in keys
    assert "amount" not in keys
    assert "currency" not in keys
    assert "invoice" not in keys
    assert "payment" not in keys
    assert "settlement" not in keys
    assert "execution" not in keys


# ARTIFACT: test_legal_evidence_usage_observation.py
# VERSION: v1.0.0-L10A2Q-P3A-LEGAL-EVIDENCE-USAGE-OBSERVATION-CERT
# AUTHORITY BOUNDARY: immutable observed Legal Evidence consumption only
# TENANT POSTURE: all usage coordinates derive from canonical LegalEvidenceContent
# FAIL-CLOSED POSTURE: malformed/corrupt/noncanonical observation evidence rejects
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively
# END OF WILSY OS SOVEREIGN ARTIFACT
