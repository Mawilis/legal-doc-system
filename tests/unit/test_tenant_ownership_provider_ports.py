"""Contract tests for provider-neutral Issue #300 integration ports.

These tests validate shape and minimization only. They do not certify a provider,
legal authority, key custody system, or positive ownership verification path.
"""
from __future__ import annotations

from dataclasses import FrozenInstanceError, fields
from datetime import datetime, timezone

import pytest

from tools.eos.auth.tenant_ownership_provider_ports import (
    RegistrySnapshot,
    SigningReceipt,
    SigningRequest,
    SubjectProofingReceipt,
)


def test_registry_snapshot_is_immutable_and_provenance_bearing() -> None:
    """Registry snapshots retain filing lineage and source freshness."""
    now = datetime(2026, 11, 2, tzinfo=timezone.utc)
    snapshot = RegistrySnapshot(
        source_id="cipc",
        record_reference="record-1",
        filing_reference="filing-2",
        filing_revision="2",
        jurisdiction="ZA",
        entity_type="company",
        record_status="ACTIVE",
        retrieved_at=now,
        effective_at=now,
        source_fingerprint="sha256:source",
        attributes_fingerprint="sha256:attributes",
        supersedes_filing_reference="filing-1",
    )

    assert snapshot.supersedes_filing_reference == "filing-1"
    assert snapshot.retrieved_at == now
    with pytest.raises(FrozenInstanceError):
        snapshot.filing_revision = "3"  # type: ignore[misc]


def test_signing_contract_is_digest_scoped_and_contains_no_private_key() -> None:
    """The provider receives a digest and returns a receipt, never key bytes."""
    request_fields = {field.name for field in fields(SigningRequest)}
    receipt_fields = {field.name for field in fields(SigningReceipt)}

    assert "payload_digest" in request_fields
    assert "purpose" in request_fields
    assert "key_reference" in request_fields
    assert not any("private_key" in name or "secret" in name for name in request_fields)
    assert "signature" in receipt_fields
    assert "audit_reference" in receipt_fields
    assert not any("private_key" in name or "secret" in name for name in receipt_fields)


def test_identity_receipt_is_opaque_and_not_a_wilsy_principal_grant() -> None:
    """Identity proofing receipts contain subject references, not IAM decisions."""
    receipt_fields = {field.name for field in fields(SubjectProofingReceipt)}

    assert {
        "provider_id",
        "verifier_id",
        "assurance_profile",
        "subject_reference",
        "evidence_fingerprint",
        "revocation_reference",
    }.issubset(receipt_fields)
    assert "principal_id" not in receipt_fields
    assert "authorized" not in receipt_fields
