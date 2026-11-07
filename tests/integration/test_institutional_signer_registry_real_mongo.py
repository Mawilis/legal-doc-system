"""Replica-set certification for institutional signer lifecycle transactions."""
from __future__ import annotations

import os
import uuid
from datetime import datetime, timezone

import pytest
from pymongo import MongoClient

from tools.eos.security.institutional_signer_enrollment_registry import (
    COLLECTION, EVENT_COLLECTION, InstitutionalSignerEnrollmentRegistry,
    InstitutionalSignerRegistryConflict,
)

URI = os.getenv("INSTITUTIONAL_PKI_TEST_MONGODB_URI")
pytestmark = pytest.mark.skipif(not URI, reason="INSTITUTIONAL_PKI_TEST_MONGODB_URI is not configured")


def test_signer_enrollment_approval_and_revocation_are_atomic_on_replica_set():
    client = MongoClient(URI, serverSelectionTimeoutMS=5000)
    db_name = f"institutional_signer_{uuid.uuid4().hex}"
    db = client[db_name]
    try:
        hello = client.admin.command("hello")
        assert hello.get("setName") and hello.get("isWritablePrimary") is True
        records, events = db[COLLECTION], db[EVENT_COLLECTION]
        InstitutionalSignerEnrollmentRegistry.ensure_indexes(records, events)
        registry = InstitutionalSignerEnrollmentRegistry(records, events)
        now = datetime.now(timezone.utc)

        def lifecycle(session):
            pending = registry.request_enrollment(
                tenant_id="WILSYTENANT-4CD2FZ4O",
                certificate_fingerprint_sha256="a" * 64,
                certificate_serial_number_hex="abc123",
                subject_common_name="WILSY Authorised Signatory",
                issuer_common_name="WILSY Intermediate CA",
                trust_root_sha256="b" * 64,
                identity_proofing_evidence_reference="proofing://institutional/case-001",
                signatory_mandate_evidence_reference="mandate://institutional/resolution-001",
                requested_by_principal_id="owner-requester",
                requested_at=now, idempotency_key="request-001", session=session,
            )
            assert pending["status"] == "PENDING_APPROVAL"
            active = registry.approve_enrollment(
                tenant_id="WILSYTENANT-4CD2FZ4O",
                certificate_fingerprint_sha256="a" * 64,
                approver_principal_id="owner-independent-approver",
                approval_attestation_reference="attestation://proofing-and-mandate/review-001",
                approved_at=now, idempotency_key="approve-001", session=session,
            )
            assert active["status"] == "ACTIVE"
            assert registry.require_active(
                tenant_id="WILSYTENANT-4CD2FZ4O",
                certificate_fingerprint_sha256="a" * 64,
                certificate_serial_number_hex="abc123",
                trust_root_sha256="b" * 64,
                session=session,
            )["status"] == "ACTIVE"
            revoked = registry.revoke(
                tenant_id="WILSYTENANT-4CD2FZ4O",
                certificate_fingerprint_sha256="a" * 64,
                revoked_by_principal_id="owner-revoker",
                revoked_at=now, reason="Mandate withdrawn",
                idempotency_key="revoke-001", session=session,
            )
            assert revoked["status"] == "REVOKED"
            assert revoked["crl_revocation_publication_status"] == "PENDING"
            with pytest.raises(InstitutionalSignerRegistryConflict):
                registry.require_active(
                    tenant_id="WILSYTENANT-4CD2FZ4O",
                    certificate_fingerprint_sha256="a" * 64,
                    certificate_serial_number_hex="abc123",
                    trust_root_sha256="b" * 64,
                    session=session,
                )
            return revoked

        with client.start_session() as session:
            final = session.with_transaction(lifecycle)
        assert final["status"] == "REVOKED"
        assert records.count_documents({"tenant_id": "WILSYTENANT-4CD2FZ4O"}) == 1
        assert events.count_documents({"tenant_id": "WILSYTENANT-4CD2FZ4O"}) == 3
        assert [row["action"] for row in events.find({"tenant_id": "WILSYTENANT-4CD2FZ4O"}).sort("revision", 1)] == [
            "SIGNER_ENROLLMENT_REQUESTED",
            "SIGNER_ENROLLMENT_APPROVED",
            "SIGNER_ENROLLMENT_REVOKED",
        ]
    finally:
        client.drop_database(db_name)
        assert db_name not in client.list_database_names()
        client.close()
