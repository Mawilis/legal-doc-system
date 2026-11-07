"""Replica-set certification for institutional signer lifecycle transactions."""
from __future__ import annotations

import os
import json
from hashlib import sha256
import uuid
from datetime import datetime, timezone

import pytest
from pymongo import MongoClient
from pymongo.read_concern import ReadConcern
from pymongo.read_preferences import ReadPreference
from pymongo.write_concern import WriteConcern

from tools.eos.security.institutional_signer_enrollment_registry import (
    COLLECTION, EVENT_COLLECTION, InstitutionalSignerEnrollmentRegistry,
    InstitutionalSignerRegistryConflict,
)

def _provenance_record(*, kind: str, now: datetime, **scope):
    record = {
        "schema": "wilsy.institutional.signer.evidence_provenance.v1",
        "source_system_id": "governed-test-source",
        "source_record_id": f"record-{kind.lower()}",
        "source_revision": "revision-1",
        "evidence_reference": f"evidence://source/{kind.lower()}",
        "status": "ACTIVE",
        "evidence_fingerprint_sha256": "e" * 64,
        "verified_at": now,
        "valid_from": now.replace(year=now.year - 1),
        "valid_until": None,
        "revoked": False,
        "evaluated_at": now,
        "tenant_id": "WILSYTENANT-4CD2FZ4O",
        "certificate_fingerprint_sha256": "a" * 64,
        "evidence_kind": kind,
        "identity_assurance_level": "SUBSTANTIAL",
        "legal_entity_reference": "WILSY-PTY-LTD",
        "mandate_scope": "INSTITUTIONAL_SIGNER",
        "approval_scope": "INSTITUTIONAL_SIGNER_ENROLLMENT",
    }
    record.update(scope)
    return record


def _digest(value):
    canonical = json.dumps(value, sort_keys=True, separators=(",", ":"),
                           default=lambda item: item.isoformat() if isinstance(item, datetime) else item)
    return sha256(canonical.encode("utf-8")).hexdigest()


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
            identity = _provenance_record(kind="IDENTITY_PROOFING", now=now, subject_principal_id="owner-requester")
            mandate = _provenance_record(kind="SIGNATORY_MANDATE", now=now, subject_principal_id="owner-requester")
            enrollment_provenance = {
                "schema": "wilsy.institutional.signer.enrollment_provenance.v1",
                "identity_proofing": identity,
                "signatory_mandate": mandate,
            }

            def abort_after_enrollment(abort_session):
                registry.request_enrollment(
                    tenant_id="WILSYTENANT-4CD2FZ4O",
                    certificate_fingerprint_sha256="a" * 64,
                    certificate_serial_number_hex="abc123",
                    subject_common_name="WILSY Authorised Signatory",
                    issuer_common_name="WILSY Intermediate CA",
                    issuer_subject_sha256="c" * 64,
                    trust_root_sha256="b" * 64,
                    identity_proofing_evidence_reference="proofing://institutional/case-001",
                    signatory_mandate_evidence_reference="mandate://institutional/resolution-001",
                    requested_by_principal_id="owner-requester",
                    requested_at=now, idempotency_key="request-aborted", session=abort_session,
                    evidence_provenance_fingerprint_sha256=_digest(enrollment_provenance),
                    evidence_provenance_snapshot=enrollment_provenance,
                )
                raise RuntimeError("force transaction abort after provenance and event writes")

            with pytest.raises(RuntimeError, match="force transaction abort"):
                with client.start_session() as abort_session:
                    abort_session.with_transaction(
                        abort_after_enrollment,
                        read_concern=ReadConcern("snapshot"),
                        write_concern=WriteConcern("majority", j=True),
                        read_preference=ReadPreference.PRIMARY,
                    )
            assert records.count_documents({"tenant_id": "WILSYTENANT-4CD2FZ4O"}) == 0
            assert events.count_documents({"tenant_id": "WILSYTENANT-4CD2FZ4O"}) == 0

            pending = registry.request_enrollment(
                tenant_id="WILSYTENANT-4CD2FZ4O",
                certificate_fingerprint_sha256="a" * 64,
                certificate_serial_number_hex="abc123",
                subject_common_name="WILSY Authorised Signatory",
                issuer_common_name="WILSY Intermediate CA",
                issuer_subject_sha256="c" * 64,
                trust_root_sha256="b" * 64,
                identity_proofing_evidence_reference="proofing://institutional/case-001",
                signatory_mandate_evidence_reference="mandate://institutional/resolution-001",
                requested_by_principal_id="owner-requester",
                requested_at=now, idempotency_key="request-001", session=session,
                evidence_provenance_fingerprint_sha256=_digest(enrollment_provenance),
                evidence_provenance_snapshot=enrollment_provenance,
            )
            assert pending["status"] == "PENDING_APPROVAL"
            assert pending["evidence_provenance_snapshot"] == enrollment_provenance
            approval_provenance = _provenance_record(
                kind="INDEPENDENT_APPROVAL", now=now,
                enrollment_requester_principal_id="owner-requester",
                reviewer_principal_id="owner-independent-approver",
            )
            active = registry.approve_enrollment(
                tenant_id="WILSYTENANT-4CD2FZ4O",
                certificate_fingerprint_sha256="a" * 64,
                approver_principal_id="owner-independent-approver",
                approval_attestation_reference="attestation://proofing-and-mandate/review-001",
                approved_at=now, idempotency_key="approve-001", session=session,
                evidence_provenance_fingerprint_sha256=_digest(approval_provenance),
                approval_evidence_provenance_snapshot=approval_provenance,
            )
            assert active["status"] == "ACTIVE"
            assert active["approval_evidence_provenance_snapshot"] == approval_provenance
            assert registry.require_active(
                tenant_id="WILSYTENANT-4CD2FZ4O",
                certificate_fingerprint_sha256="a" * 64,
                certificate_serial_number_hex="abc123",
                issuer_subject_sha256="c" * 64,
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
            reconciled = registry.reconcile_crl_publications(
                verified_crls=({
                    "issuer_subject_sha256": "c" * 64,
                    "crl_number": 9,
                    "crl_fingerprint_sha256": "d" * 64,
                    "revoked_serial_numbers_hex": ("abc123",),
                },),
                reconciled_at=now, actor_reference="runtime://institutional-pki",
                session=session,
            )
            assert reconciled == 1
            assert records.find_one({
                "tenant_id": "WILSYTENANT-4CD2FZ4O",
                "certificate_fingerprint_sha256": "a" * 64,
            }, session=session)["crl_revocation_publication_status"] == "PUBLISHED"
            with pytest.raises(InstitutionalSignerRegistryConflict):
                registry.require_active(
                    tenant_id="WILSYTENANT-4CD2FZ4O",
                    certificate_fingerprint_sha256="a" * 64,
                    certificate_serial_number_hex="abc123",
                    issuer_subject_sha256="c" * 64,
                    trust_root_sha256="b" * 64,
                    session=session,
                )
            return revoked

        with client.start_session() as session:
            final = session.with_transaction(
                lifecycle,
                read_concern=ReadConcern("snapshot"),
                write_concern=WriteConcern("majority", j=True),
                read_preference=ReadPreference.PRIMARY,
            )
        assert final["status"] == "REVOKED"
        assert records.count_documents({"tenant_id": "WILSYTENANT-4CD2FZ4O"}) == 1
        assert events.count_documents({"tenant_id": "WILSYTENANT-4CD2FZ4O"}) == 4
        assert [row["action"] for row in events.find({"tenant_id": "WILSYTENANT-4CD2FZ4O"}).sort("revision", 1)] == [
            "SIGNER_ENROLLMENT_REQUESTED",
            "SIGNER_ENROLLMENT_APPROVED",
            "SIGNER_ENROLLMENT_REVOKED",
            "SIGNER_REVOCATION_CRL_PUBLISHED",
        ]
    finally:
        client.drop_database(db_name)
        assert db_name not in client.list_database_names()
        client.close()
