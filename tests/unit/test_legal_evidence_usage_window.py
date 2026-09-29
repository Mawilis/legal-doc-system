"""Direct certificate for complete Legal Evidence usage-window evidence.

TITLE: Legal Evidence Usage Window Direct Certificate
VERSION: v1.0.0-L10A2Q-P3C-A-LEGAL-EVIDENCE-USAGE-WINDOW-CERT
AUTHORITY: WILSY OS Core Governance
PURPOSE:
    Prove one immutable tenant/document usage snapshot capable of carrying
    complete P3 usage aggregation into P4 without granting reservation,
    admission or financial authority.

EPITOME:
    USAGE OBSERVATIONS DURABLE
    -> COMPLETE USAGE WINDOW EVIDENCE
    != REMAINING CAPACITY
    != CAPACITY RESERVED
    != STORAGE ADMISSION

METRIC SCOPE:
    tenant_storage_bytes_added is tenant-wide cumulative through as_of.
    monthly_ingress_bytes_added is tenant-wide for the month through as_of.
    document_versions_added is cumulative for exactly one document through as_of.

CERTIFICATION / UPDATE DATE: 2026-09-30
"""

from __future__ import annotations

from dataclasses import FrozenInstanceError
from datetime import datetime, timezone

import pytest

from tools.eos.legal_operations.domain.legal_evidence_usage_window import (
    LegalEvidenceUsageWindow,
    LegalEvidenceUsageWindowError,
)


AS_OF = datetime(2026, 9, 30, 18, 45, tzinfo=timezone.utc)
MONTH_START = datetime(2026, 9, 1, tzinfo=timezone.utc)
SOURCE_DIGEST = "a" * 128


def _window(**overrides: object) -> LegalEvidenceUsageWindow:
    values: dict[str, object] = {
        "tenant_id": "tenant-p3c-a",
        "document_id": "document-p3c-a",
        "as_of": AS_OF,
        "monthly_window_start": MONTH_START,
        "monthly_window_end": AS_OF,
        "tenant_observation_count": 11,
        "monthly_observation_count": 4,
        "document_observation_count": 3,
        "tenant_storage_bytes_added": 8192,
        "monthly_ingress_bytes_added": 3072,
        "document_versions_added": 3,
        "source_observation_set_fingerprint": SOURCE_DIGEST,
    }
    values.update(overrides)
    return LegalEvidenceUsageWindow(**values)  # type: ignore[arg-type]


def test_complete_usage_window_preserves_exact_scoped_metrics() -> None:
    item = _window()

    assert item.tenant_id == "tenant-p3c-a"
    assert item.document_id == "document-p3c-a"
    assert item.as_of == AS_OF
    assert item.monthly_window_start == MONTH_START
    assert item.monthly_window_end == AS_OF

    assert item.tenant_observation_count == 11
    assert item.monthly_observation_count == 4
    assert item.document_observation_count == 3

    assert item.tenant_storage_bytes_added == 8192
    assert item.monthly_ingress_bytes_added == 3072
    assert item.document_versions_added == 3

    assert item.source_observation_set_fingerprint == SOURCE_DIGEST
    assert len(item.fingerprint) == 128
    int(item.fingerprint, 16)


def test_legitimate_empty_window_is_representable_and_deterministic() -> None:
    first = _window(
        tenant_observation_count=0,
        monthly_observation_count=0,
        document_observation_count=0,
        tenant_storage_bytes_added=0,
        monthly_ingress_bytes_added=0,
        document_versions_added=0,
        source_observation_set_fingerprint="0" * 128,
    )
    second = _window(
        tenant_observation_count=0,
        monthly_observation_count=0,
        document_observation_count=0,
        tenant_storage_bytes_added=0,
        monthly_ingress_bytes_added=0,
        document_versions_added=0,
        source_observation_set_fingerprint="0" * 128,
    )

    assert first == second
    assert first.fingerprint == second.fingerprint


def test_window_is_immutable() -> None:
    item = _window()

    with pytest.raises(FrozenInstanceError):
        item.document_versions_added = 4  # type: ignore[misc]


def test_round_trip_preserves_exact_fingerprint() -> None:
    item = _window()

    hydrated = LegalEvidenceUsageWindow.from_dict(item.to_dict())

    assert hydrated == item
    assert hydrated.fingerprint == item.fingerprint


def test_fingerprint_corruption_rejects() -> None:
    payload = _window().to_dict()
    payload["fingerprint"] = "b" * 128

    with pytest.raises(
        LegalEvidenceUsageWindowError,
        match="L10A2Q_P3C_A_FINGERPRINT_MISMATCH",
    ):
        LegalEvidenceUsageWindow.from_dict(payload)


def test_monthly_window_must_begin_at_utc_month_boundary_and_end_at_as_of() -> None:
    with pytest.raises(
        LegalEvidenceUsageWindowError,
        match="L10A2Q_P3C_A_WINDOW_INVALID",
    ):
        _window(
            monthly_window_start=datetime(
                2026,
                9,
                2,
                tzinfo=timezone.utc,
            )
        )

    with pytest.raises(
        LegalEvidenceUsageWindowError,
        match="L10A2Q_P3C_A_WINDOW_INVALID",
    ):
        _window(
            monthly_window_end=datetime(
                2026,
                9,
                29,
                tzinfo=timezone.utc,
            )
        )


def test_scoped_counts_must_be_consistent() -> None:
    with pytest.raises(
        LegalEvidenceUsageWindowError,
        match="L10A2Q_P3C_A_COUNT_INVALID",
    ):
        _window(
            tenant_observation_count=2,
            monthly_observation_count=3,
        )

    with pytest.raises(
        LegalEvidenceUsageWindowError,
        match="L10A2Q_P3C_A_COUNT_INVALID",
    ):
        _window(
            tenant_observation_count=2,
            document_observation_count=3,
        )


def test_pseudo_tenant_and_malformed_source_digest_reject() -> None:
    with pytest.raises(
        LegalEvidenceUsageWindowError,
        match="L10A2Q_P3C_A_TENANT_REQUIRED",
    ):
        _window(tenant_id="global")

    with pytest.raises(
        LegalEvidenceUsageWindowError,
        match="L10A2Q_P3C_A_SOURCE_FINGERPRINT_INVALID",
    ):
        _window(source_observation_set_fingerprint="not-a-digest")


def test_serialized_surface_contains_no_p4_p5_or_financial_authority() -> None:
    keys = set(_window().to_dict())

    forbidden = {
        "remaining_storage_bytes",
        "remaining_ingress_bytes",
        "remaining_document_versions",
        "storage_exhausted",
        "ingress_exhausted",
        "versions_exhausted",
        "reservation_id",
        "reserved_bytes",
        "admitted",
        "price",
        "amount",
        "currency",
        "invoice",
        "payment",
        "settlement",
        "execution",
        "overage",
    }

    assert forbidden.isdisjoint(keys)


# ARTIFACT: test_legal_evidence_usage_window.py
# VERSION: v1.0.0-L10A2Q-P3C-A-LEGAL-EVIDENCE-USAGE-WINDOW-CERT
# AUTHORITY BOUNDARY: complete aggregated usage evidence only
# TENANT POSTURE: exact tenant/document binding
# CAPACITY POSTURE: no remaining-capacity, reservation or admission authority
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively
# END OF WILSY OS SOVEREIGN ARTIFACT
