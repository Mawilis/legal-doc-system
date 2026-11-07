from datetime import datetime, timezone

import pytest

from tools.eos.security.institutional_signer_enrollment_registry import (
    InstitutionalSignerEnrollmentRegistry,
    InstitutionalSignerRegistryConflict,
    InstitutionalSignerRegistryError,
)


class Result:
    def __init__(self, modified_count):
        self.modified_count = modified_count


class MemoryCollection:
    def __init__(self):
        self.rows = []
        self.next_id = 1

    def create_index(self, *args, **kwargs):
        return kwargs.get("name")

    def find_one(self, query, session=None):
        assert session is not None
        for row in self.rows:
            if all(row.get(key) == value for key, value in query.items()):
                return dict(row)
        return None

    def insert_one(self, value, session=None):
        assert session is not None
        row = dict(value)
        row["_id"] = self.next_id
        self.next_id += 1
        self.rows.append(row)

    def update_one(self, query, update, session=None):
        assert session is not None
        for row in self.rows:
            if all(row.get(key) == value for key, value in query.items()):
                row.update(update["$set"])
                return Result(1)
        return Result(0)


def setup_registry():
    records, events = MemoryCollection(), MemoryCollection()
    registry = InstitutionalSignerEnrollmentRegistry(records, events)
    registry.ensure_indexes(records, events)
    return registry, records, events


def request(registry, session, **overrides):
    values = {
        "tenant_id": "WILSYTENANT-4CD2FZ4O",
        "certificate_fingerprint_sha256": "a" * 64,
        "certificate_serial_number_hex": "abc123",
        "subject_common_name": "Approved Wilsy Signatory",
        "issuer_common_name": "WILSY Intermediate CA",
        "issuer_subject_sha256": "c" * 64,
        "trust_root_sha256": "b" * 64,
        "identity_proofing_evidence_reference": "proofing://case/verified-001",
        "signatory_mandate_evidence_reference": "mandate://board-resolution/001",
        "requested_by_principal_id": "owner-requester",
        "requested_at": datetime(2026, 11, 7, 12, tzinfo=timezone.utc),
        "idempotency_key": "signer-request-001",
        "session": session,
    }
    values.update(overrides)
    return registry.request_enrollment(**values)


def test_signer_enrollment_requires_distinct_owner_approval_and_revocation_is_immediate():
    registry, records, events = setup_registry()
    tx = object()
    pending = request(registry, tx)
    assert pending["status"] == "PENDING_APPROVAL"
    assert request(registry, tx) == pending
    assert len(events.rows) == 1

    with pytest.raises(InstitutionalSignerRegistryConflict, match="MAKER_CHECKER_REQUIRED"):
        registry.approve_enrollment(
            tenant_id="WILSYTENANT-4CD2FZ4O",
            certificate_fingerprint_sha256="a" * 64,
            approver_principal_id="owner-requester",
            approval_attestation_reference="attestation://independent-review/self",
            approved_at=datetime(2026, 11, 7, 13, tzinfo=timezone.utc),
            idempotency_key="approve-self",
            session=tx,
        )

    active = registry.approve_enrollment(
        tenant_id="WILSYTENANT-4CD2FZ4O",
        certificate_fingerprint_sha256="a" * 64,
        approver_principal_id="owner-approver",
        approval_attestation_reference="attestation://independent-review/001",
        approved_at=datetime(2026, 11, 7, 13, tzinfo=timezone.utc),
        idempotency_key="approve-independent",
        session=tx,
    )
    assert active["status"] == "ACTIVE"
    assert active["requested_by_principal_id"] != active["approved_by_principal_id"]
    assert registry.approve_enrollment(
        tenant_id="WILSYTENANT-4CD2FZ4O",
        certificate_fingerprint_sha256="a" * 64,
        approver_principal_id="owner-approver",
        approval_attestation_reference="attestation://independent-review/001",
        approved_at=datetime(2026, 11, 7, 13, tzinfo=timezone.utc),
        idempotency_key="approve-independent",
        session=tx,
    ) == active
    assert registry.require_active(
        tenant_id="WILSYTENANT-4CD2FZ4O",
        certificate_fingerprint_sha256="a" * 64,
        certificate_serial_number_hex="abc123",
        trust_root_sha256="b" * 64,
        session=tx,
    )["status"] == "ACTIVE"

    revoked = registry.revoke(
        tenant_id="WILSYTENANT-4CD2FZ4O",
        certificate_fingerprint_sha256="a" * 64,
        revoked_by_principal_id="owner-revoker",
        revoked_at=datetime(2026, 11, 7, 14, tzinfo=timezone.utc),
        reason="Signatory mandate withdrawn",
        idempotency_key="revoke-001",
        session=tx,
    )
    assert revoked["status"] == "REVOKED"
    assert revoked["crl_revocation_publication_status"] == "PENDING"
    assert registry.revoke(
        tenant_id="WILSYTENANT-4CD2FZ4O",
        certificate_fingerprint_sha256="a" * 64,
        revoked_by_principal_id="owner-revoker",
        revoked_at=datetime(2026, 11, 7, 14, tzinfo=timezone.utc),
        reason="Signatory mandate withdrawn",
        idempotency_key="revoke-001",
        session=tx,
    ) == revoked
    with pytest.raises(InstitutionalSignerRegistryConflict, match="ACTIVE_ENROLLMENT_REQUIRED"):
        registry.require_active(
            tenant_id="WILSYTENANT-4CD2FZ4O",
            certificate_fingerprint_sha256="a" * 64,
            certificate_serial_number_hex="abc123",
            issuer_subject_sha256="c" * 64,
            trust_root_sha256="b" * 64,
            session=tx,
        )
    assert [event["action"] for event in events.rows] == [
        "SIGNER_ENROLLMENT_REQUESTED",
        "SIGNER_ENROLLMENT_APPROVED",
        "SIGNER_ENROLLMENT_REVOKED",
    ]


def test_signer_enrollment_requires_transaction_and_proofing_and_mandate_evidence():
    registry, records, events = setup_registry()
    with pytest.raises(InstitutionalSignerRegistryError, match="CALLER_TRANSACTION_REQUIRED"):
        request(registry, None)
    with pytest.raises(InstitutionalSignerRegistryError, match="PROOFING_EVIDENCE_REQUIRED"):
        request(registry, object(), identity_proofing_evidence_reference="")
    with pytest.raises(InstitutionalSignerRegistryError, match="MANDATE_EVIDENCE_REQUIRED"):
        request(registry, object(), signatory_mandate_evidence_reference="")
    assert not records.rows and not events.rows



def test_wilsy_institutional_signer_registry_rejects_other_tenant_scopes():
    registry, records, events = setup_registry()
    with pytest.raises(InstitutionalSignerRegistryConflict, match="TENANT_SCOPE_INVALID"):
        request(registry, object(), tenant_id="CUSTOMER-TENANT-001")
    assert not records.rows and not events.rows
