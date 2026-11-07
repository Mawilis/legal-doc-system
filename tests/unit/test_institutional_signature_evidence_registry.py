from datetime import datetime, timezone

import pytest

from tools.eos.security.institutional_signature_evidence_registry import (
    InstitutionalSignatureEvidenceConflict,
    InstitutionalSignatureEvidenceError,
    InstitutionalSignatureEvidenceRegistry,
)


class MemoryCollection:
    def __init__(self):
        self.rows = []

    def create_index(self, *args, **kwargs):
        return kwargs.get("name")

    def find_one(self, query, session=None):
        assert session is not None
        return next((dict(row) for row in self.rows if all(row.get(k) == v for k, v in query.items())), None)

    def insert_one(self, row, session=None):
        assert session is not None
        self.rows.append(dict(row))


def _registry():
    records, events = MemoryCollection(), MemoryCollection()
    registry = InstitutionalSignatureEvidenceRegistry(records, events)
    registry.ensure_indexes(records, events)
    return registry, records, events


def _record(registry, *, session=object(), **overrides):
    values = {
        "tenant_id": "WILSYTENANT-4CD2FZ4O",
        "offer_id": "OFFER-001",
        "candidate_id": "CAN-001",
        "evidence_id": "EVD-001",
        "evidence_version_id": "VER-001",
        "evidence_digest_sha3_512": "a" * 128,
        "signed_manifest_digest_sha3_512": "f" * 128,
        "signer_certificate_sha256": "b" * 64,
        "signer_serial_number_hex": "abc123",
        "trust_root_sha256": "c" * 64,
        "signature_sha256": "d" * 64,
        "signature_algorithm": "RSA-PSS-SHA384",
        "pki_verification_fingerprint": "e" * 64,
        "verified_at": datetime(2026, 11, 7, tzinfo=timezone.utc),
        "actor_principal_id": "PRINCIPAL-001",
        "idempotency_key": "offer-accept:WILSYTENANT-4CD2FZ4O:OFFER-001:VER-001",
        "session": session,
    }
    values.update(overrides)
    return registry.record_verified(**values)


def test_verified_signature_receipt_is_append_only_and_idempotent():
    registry, records, events = _registry()
    first = _record(registry)
    replay = _record(registry)
    assert first == replay
    assert len(records.rows) == 1
    assert len(events.rows) == 1
    assert first["schema"] == "wilsy.institutional.document_signature_verification.v2"
    assert first["signer_certificate_sha256"] == "b" * 64


def test_different_verification_for_same_offer_evidence_conflicts():
    registry, records, events = _registry()
    _record(registry)
    with pytest.raises(InstitutionalSignatureEvidenceConflict):
        _record(registry, signature_sha256="f" * 64, pki_verification_fingerprint="1" * 64)
    assert len(records.rows) == 1
    assert len(events.rows) == 1


def test_receipt_requires_caller_owned_transaction_and_strict_digests():
    registry, records, events = _registry()
    with pytest.raises(InstitutionalSignatureEvidenceError, match="CALLER_TRANSACTION_REQUIRED"):
        _record(registry, session=None)
    with pytest.raises(InstitutionalSignatureEvidenceError, match="SIGNATURE_SHA256_INVALID"):
        _record(registry, signature_sha256="not-a-digest")
    assert not records.rows and not events.rows
