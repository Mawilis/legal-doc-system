"""Direct certificate for provider-neutral Legal Evidence cleanup discovery.

TITLE: Legal Evidence Provider Cleanup Discovery Port Certificate
VERSION: v1.0.0-L10A2R-C4D1-PROVIDER-CLEANUP-DISCOVERY-PORT-CERT
AUTHORITY: WILSY OS Core Governance / Python EOS Legal Operations

PURPOSE:
    Freeze the provider-neutral evidence contract required to discover
    incomplete provider write sessions and completed provider object versions
    under exact tenant scope before any orphan classification or cleanup action.

EPITOME:
    EXACT TENANT DISCOVERY SCOPE
    -> PROVIDER DISCOVERY OBSERVATIONS
    -> IMMUTABLE EVIDENCE

    DISCOVERED SESSION
    != ABORT AUTHORIZED

    DISCOVERED OBJECT
    != ORPHAN PROVEN
    != DELETE AUTHORIZED

    PROVIDER OBSERVATION
    != CANONICAL LEGAL EVIDENCE TRUTH

AUTHORITY BOUNDARY:
    Discovery evidence only. No provider mutation, abort execution, deletion,
    retention/legal-hold decision, availability, IAM, billing, payment or
    settlement authority.

CERTIFICATION / UPDATE DATE: 2026-09-30
"""

from __future__ import annotations

from datetime import datetime, timezone
import hashlib

import pytest

from tools.eos.legal_operations.service.legal_evidence_provider_cleanup_discovery_port import (
    LegalEvidenceCompletedObjectObservation,
    LegalEvidenceIncompleteWriteSessionObservation,
    LegalEvidenceProviderCleanupDiscoveryError,
    LegalEvidenceProviderCleanupDiscoveryPort,
    LegalEvidenceProviderDiscoveryScope,
)


AT = datetime(
    2026,
    9,
    30,
    15,
    30,
    0,
    123456,
    tzinfo=timezone.utc,
)

TENANT_FP = hashlib.sha3_512(
    b"tenant-c4d1"
).hexdigest()

INTENT_FP = hashlib.sha3_512(
    b"intent-c4d1"
).hexdigest()


def test_discovery_scope_is_exact_tenant_bound_and_immutable() -> None:
    scope = LegalEvidenceProviderDiscoveryScope(
        tenant_id="tenant-c4d1",
        tenant_scope_fingerprint=TENANT_FP,
    )

    assert scope.tenant_id == "tenant-c4d1"
    assert scope.tenant_scope_fingerprint == TENANT_FP

    with pytest.raises(
        Exception,
    ):
        scope.tenant_id = "tenant-neighbor"  # type: ignore[misc]


def test_incomplete_session_observation_is_evidence_not_abort_authority() -> None:
    observation = LegalEvidenceIncompleteWriteSessionObservation(
        tenant_id="tenant-c4d1",
        provider_name="aws_s3",
        storage_reference="legal-evidence/v1/opaque/session",
        write_session_reference="upload-c4d1",
        initiated_at=AT,
        observed_at=AT,
    )

    assert observation.tenant_id == "tenant-c4d1"
    assert observation.provider_name == "aws_s3"
    assert observation.write_session_reference == "upload-c4d1"

    public = {
        name.lower()
        for name in dir(observation)
        if not name.startswith("_")
    }

    assert "abort" not in public
    assert "abort_authorized" not in public
    assert "delete" not in public
    assert "delete_authorized" not in public


def test_completed_object_observation_is_not_orphan_or_delete_authority() -> None:
    observation = LegalEvidenceCompletedObjectObservation(
        tenant_id="tenant-c4d1",
        provider_name="aws_s3",
        storage_reference="legal-evidence/v1/opaque/object",
        object_version_reference="version-c4d1",
        provider_integrity_reference='"etag-c4d1"',
        content_length=123,
        last_modified_at=AT,
        observed_at=AT,
    )

    assert observation.content_length == 123

    public = {
        name.lower()
        for name in dir(observation)
        if not name.startswith("_")
    }

    forbidden = {
        "orphan",
        "orphan_proven",
        "delete",
        "delete_authorized",
        "retention_satisfied",
        "legal_hold_cleared",
        "available",
        "authorized_availability",
    }

    assert forbidden.isdisjoint(public)


def test_protocol_exposes_discovery_only() -> None:
    public = {
        name.lower()
        for name in dir(
            LegalEvidenceProviderCleanupDiscoveryPort
        )
        if not name.startswith("_")
    }

    assert {
        "list_incomplete_write_sessions",
        "list_completed_object_versions",
    }.issubset(public)

    forbidden = {
        "begin",
        "write_chunk",
        "complete",
        "abort",
        "delete",
        "delete_object",
        "authorize_availability",
        "make_available",
        "publish",
        "clear_legal_hold",
        "satisfy_retention",
    }

    assert forbidden.isdisjoint(public)


def test_malformed_scope_and_observations_fail_closed() -> None:
    with pytest.raises(
        LegalEvidenceProviderCleanupDiscoveryError,
    ):
        LegalEvidenceProviderDiscoveryScope(
            tenant_id="*",
            tenant_scope_fingerprint=TENANT_FP,
        )

    with pytest.raises(
        LegalEvidenceProviderCleanupDiscoveryError,
    ):
        LegalEvidenceProviderDiscoveryScope(
            tenant_id="tenant-c4d1",
            tenant_scope_fingerprint="A" * 128,
        )

    with pytest.raises(
        LegalEvidenceProviderCleanupDiscoveryError,
    ):
        LegalEvidenceIncompleteWriteSessionObservation(
            tenant_id="tenant-c4d1",
            provider_name="aws_s3",
            storage_reference="",
            write_session_reference="upload-c4d1",
            initiated_at=AT,
            observed_at=AT,
        )

    with pytest.raises(
        LegalEvidenceProviderCleanupDiscoveryError,
    ):
        LegalEvidenceCompletedObjectObservation(
            tenant_id="tenant-c4d1",
            provider_name="aws_s3",
            storage_reference="legal-evidence/v1/object",
            object_version_reference="version-c4d1",
            provider_integrity_reference='"etag-c4d1"',
            content_length=0,
            last_modified_at=AT,
            observed_at=AT,
        )


# ARTIFACT: test_legal_evidence_provider_cleanup_discovery_port.py
# VERSION: v1.0.0-L10A2R-C4D1-PROVIDER-CLEANUP-DISCOVERY-PORT-CERT
# AUTHORITY BOUNDARY: provider cleanup discovery evidence only
# TENANT POSTURE: exact tenant-scoped discovery
# SESSION POSTURE: discovered session is not abort authorization
# OBJECT POSTURE: discovered object is not orphan proof
# DELETION POSTURE: no deletion authority
# RETENTION POSTURE: no retention/legal-hold authority
# AVAILABILITY POSTURE: no availability authority
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively
# END OF WILSY OS SOVEREIGN ARTIFACT
