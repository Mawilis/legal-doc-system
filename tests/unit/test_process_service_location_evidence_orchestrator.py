"""Orchestrator certificates for short-lived location permission and GPS evidence."""
from __future__ import annotations

from datetime import datetime, timedelta, timezone
from types import SimpleNamespace
from typing import Any

import pytest
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.primitives.asymmetric.utils import decode_dss_signature

from tools.eos.legal_operations.domain.deputy_device_provenance_authority import (
    DeputyDeviceProvenance,
    DeputyDeviceProvenanceChallenge,
)
from tools.eos.legal_operations.domain.deputy_principal_binding import DeputyPrincipalBinding
from tools.eos.legal_operations.domain.legal_operations_lifecycle import (
    Deputy,
    ServiceAttempt,
    ServiceAttemptState,
)
from tools.eos.legal_operations.orchestration.process_service_location_evidence_orchestrator import (
    location_observation_signed_payload,
    MAX_PERMISSION_WINDOW,
    ProcessServiceLocationEvidenceOrchestrationError,
    issue_process_service_location_permission_grant,
    record_process_service_location_observation,
    revoke_process_service_location_permission_grant,
)
from tools.eos.legal_operations.registry.process_service_allocation_registry import (
    ProcessServiceAllocationCurrent,
    ProcessServiceAllocationReceipt,
)
from tools.eos.legal_operations.registry.process_service_location_evidence_registry import (
    ProcessServiceLocationEvidenceRegistry as Registry,
    ProcessServiceLocationEvidenceRegistryConflictError,
)

HASH = "a" * 128
TENANT, PRINCIPAL, DEPUTY_ID, OFFICE = "tenant-p5l-orch", "principal-p5l", "deputy-p5l", "office-p5l"


class Session:
    in_transaction = True


class Collection:
    def __init__(self) -> None:
        self.docs: list[dict[str, Any]] = []
        self.indexes: list[Any] = []

    def find_one(self, query: dict[str, Any], *, session: object = None):
        return next((dict(row) for row in self.docs if all(row.get(k) == v for k, v in query.items())), None)

    def insert_one(self, value: dict[str, Any], *, session: object = None):
        self.docs.append(dict(value))
        return SimpleNamespace(inserted_id=len(self.docs))

    def create_index(self, keys, **kwargs):
        self.indexes.append((keys, kwargs))


def sources():
    now = datetime.now(timezone.utc)
    attempt = ServiceAttempt(
        tenant_id=TENANT, attempt_id="attempt-p5l",
        instruction_id="instruction-p5l", document_id="document-p5l",
        deputy_id=DEPUTY_ID, allocated_at=now - timedelta(minutes=2),
        allocation_evidence_reference="allocation-p5l",
    ).transition_to(
        ServiceAttemptState.ATTEMPTED, evidence_reference="attempt-evidence",
        evidence_fingerprint=HASH, occurred_at=now - timedelta(minutes=1),
    )
    receipt = ProcessServiceAllocationReceipt(
        tenant_id=TENANT, allocation_command_id="allocation-command-p5l",
        idempotency_key="allocation-key-p5l", instruction_id="instruction-p5l",
        case_matter_id="matter-p5l", document_id="document-p5l", district_id="district-p5l",
        sheriff_office_id=OFFICE, deputy_id=DEPUTY_ID,
        assignment_decision_id="assignment-p5l", assignment_decision_fingerprint=HASH,
        source_instruction_fingerprint=HASH, source_document_fingerprint=HASH,
        source_district_fingerprint=HASH, source_sheriff_office_fingerprint=HASH,
        source_deputy_fingerprint=HASH, prior_custody_chain_fingerprint=HASH,
        prior_custody_head_event_id="head-p5l", prior_custody_head_fingerprint=HASH,
        prior_custody_head_sequence_number=1, from_holder_reference=OFFICE,
        to_holder_reference=DEPUTY_ID, allocation_custody_event_id="allocation-event-p5l",
        allocation_evidence_reference="allocation-p5l", allocated_at=now - timedelta(minutes=2),
        allocated_document_fingerprint=HASH, allocation_custody_event_fingerprint=HASH,
        result_custody_chain_fingerprint=HASH,
    )
    current = ProcessServiceAllocationCurrent(
        tenant_id=TENANT, document_id="document-p5l",
        process_document_fingerprint=HASH, custody_chain_fingerprint=HASH,
        custody_head_event_id="allocation-event-p5l", custody_head_fingerprint=HASH,
        custody_head_sequence_number=2, current_holder_reference=DEPUTY_ID,
        authority_evidence_reference="allocation-command-p5l",
        authority_evidence_fingerprint=receipt.fingerprint,
    )
    return attempt, receipt, current, now


def proof(now: datetime) -> tuple[DeputyDeviceProvenance, Any]:
    deputy = Deputy(
        tenant_id=TENANT, deputy_id=DEPUTY_ID, sheriff_office_id=OFFICE,
        display_name="Synthetic Deputy", badge_reference="badge-p5l",
        evidence_reference="deputy-evidence-p5l",
    )
    binding = DeputyPrincipalBinding.from_deputy(
        principal_id=PRINCIPAL, deputy=deputy,
        bound_at=now - timedelta(days=1), evidence_reference="binding-p5l",
    )
    private_key = ec.generate_private_key(ec.SECP256R1())
    public_der = private_key.public_key().public_bytes(
        serialization.Encoding.DER, serialization.PublicFormat.SubjectPublicKeyInfo
    )
    challenge = DeputyDeviceProvenanceChallenge.issue(
        binding=binding, session_reference="WILSYSESSION-p5l",
        challenge_id="challenge-p5l", public_key_spki_der=public_der,
        nonce=b"N" * 32, issued_at=now - timedelta(seconds=5),
        expires_at=now + timedelta(minutes=2),
    )
    der = private_key.sign(challenge.signed_payload(), ec.ECDSA(hashes.SHA256()))
    r, s = decode_dss_signature(der)
    signature = r.to_bytes(32, "big") + s.to_bytes(32, "big")
    return DeputyDeviceProvenance.verify(
        challenge=challenge, signature_p1363=signature, verified_at=now
    ), private_key


def create_grant(attempt, receipt, current, device_proof, now, collection):
    return issue_process_service_location_permission_grant(
        attempt=attempt, allocation_receipt=receipt, allocation_current=current,
        device_provenance=device_proof, principal_id=PRINCIPAL, grant_id="grant-p5l",
        permission_granted=True, permission_notice_version="location-notice-v1",
        granted_at=now, permission_collection=collection, session=Session(),
    )


def test_short_lived_grant_is_bound_to_verified_device_and_server_acknowledgement():
    attempt, receipt, current, now = sources()
    proof_value, _private_key = proof(now)
    grants = Collection()
    grant = create_grant(attempt, receipt, current, proof_value, now, grants)
    assert grant.device_id == proof_value.device_id
    assert grant.expires_at - grant.granted_at == MAX_PERMISSION_WINDOW
    assert grant.permission_evidence_reference == "location-permission:grant-p5l"
    assert len(grants.docs) == 1


def test_permission_denial_and_wrong_principal_do_not_persist():
    attempt, receipt, current, now = sources()
    proof_value, _private_key = proof(now)
    grants = Collection()
    with pytest.raises(ProcessServiceLocationEvidenceOrchestrationError):
        issue_process_service_location_permission_grant(
            attempt=attempt, allocation_receipt=receipt, allocation_current=current,
            device_provenance=proof_value, principal_id=PRINCIPAL, grant_id="grant-denied",
            permission_granted=False, permission_notice_version="location-notice-v1",
            granted_at=now, permission_collection=grants, session=Session(),
        )
    with pytest.raises(ProcessServiceLocationEvidenceOrchestrationError):
        issue_process_service_location_permission_grant(
            attempt=attempt, allocation_receipt=receipt, allocation_current=current,
            device_provenance=proof_value, principal_id="foreign-principal", grant_id="grant-foreign",
            permission_granted=True, permission_notice_version="location-notice-v1",
            granted_at=now, permission_collection=grants, session=Session(),
        )
    assert grants.docs == []


def test_location_observation_requires_active_grant_and_same_device():
    attempt, receipt, current, now = sources()
    proof_value, private_key = proof(now)
    grants, observations, revocations = Collection(), Collection(), Collection()
    grant = create_grant(attempt, receipt, current, proof_value, now, grants)
    current_identity = "p2-current-identity-p5l"
    captured_at = now + timedelta(seconds=1)
    signed_payload = location_observation_signed_payload(
        tenant_id=TENANT, attempt_id=attempt.attempt_id,
        current_evidence_identity=current_identity, deputy_id=DEPUTY_ID,
        device_id=proof_value.device_id, challenge_id=proof_value.challenge_id,
        grant_id=grant.grant_id, observation_id="observation-p5l",
        latitude=-26.2041, longitude=28.0473, horizontal_accuracy_m=10.0,
        captured_at=captured_at,
    )
    der = private_key.sign(signed_payload, ec.ECDSA(hashes.SHA256()))
    r_value, s_value = decode_dss_signature(der)
    location_signature = r_value.to_bytes(32, "big") + s_value.to_bytes(32, "big")
    value = record_process_service_location_observation(
        attempt=attempt, allocation_receipt=receipt, allocation_current=current,
        device_provenance=proof_value, principal_id=PRINCIPAL, grant_id=grant.grant_id,
        observation_id="observation-p5l", current_evidence_identity=current_identity,
        location_signature_p1363=location_signature, latitude=-26.2041, longitude=28.0473,
        horizontal_accuracy_m=10.0, captured_at=captured_at,
        permission_collection=grants, observation_collection=observations,
        revocation_collection=revocations, session=Session(),
    )
    assert value.device_provenance_reference == proof_value.challenge_id
    assert value.device_provenance_fingerprint == proof_value.fingerprint
    assert len(observations.docs) == 1
    Registry.assert_permission_grant_active(TENANT, grant.grant_id, revocations, session=Session())


def test_revoked_grant_blocks_observation_but_preserves_existing_grant():
    attempt, receipt, current, now = sources()
    proof_value, private_key = proof(now)
    grants, observations, revocations = Collection(), Collection(), Collection()
    grant = create_grant(attempt, receipt, current, proof_value, now, grants)
    revoke_process_service_location_permission_grant(
        tenant_id=TENANT, grant_id=grant.grant_id, revocation_id="revoke-p5l",
        revoked_by_principal_id=PRINCIPAL, revoked_at=now + timedelta(seconds=2),
        reason_reference="user-withdrew-permission", grant_collection=grants,
        revocation_collection=revocations, session=Session(),
    )
    captured_at = now + timedelta(seconds=3)
    signed_payload = location_observation_signed_payload(
        tenant_id=TENANT, attempt_id=attempt.attempt_id,
        current_evidence_identity="p2-current-identity-p5l", deputy_id=DEPUTY_ID,
        device_id=proof_value.device_id, challenge_id=proof_value.challenge_id,
        grant_id=grant.grant_id, observation_id="observation-after-revoke",
        latitude=-26.2, longitude=28.0, horizontal_accuracy_m=10.0,
        captured_at=captured_at,
    )
    der = private_key.sign(signed_payload, ec.ECDSA(hashes.SHA256()))
    r_value, s_value = decode_dss_signature(der)
    location_signature = r_value.to_bytes(32, "big") + s_value.to_bytes(32, "big")
    with pytest.raises(ProcessServiceLocationEvidenceOrchestrationError) as error:
        record_process_service_location_observation(
            attempt=attempt, allocation_receipt=receipt, allocation_current=current,
            device_provenance=proof_value, principal_id=PRINCIPAL, grant_id=grant.grant_id,
            observation_id="observation-after-revoke", current_evidence_identity="p2-current-identity-p5l",
            location_signature_p1363=location_signature, latitude=-26.2, longitude=28.0,
            horizontal_accuracy_m=10.0, captured_at=captured_at,
            permission_collection=grants, observation_collection=observations,
            revocation_collection=revocations, session=Session(),
        )
    assert error.value.code == "P5L_LOCATION_OBSERVATION_PERSISTENCE_REJECTED"
    assert len(grants.docs) == 1 and len(revocations.docs) == 1 and observations.docs == []




def test_device_signature_cannot_be_replayed_for_changed_gps_coordinates():
    attempt, receipt, current, now = sources()
    proof_value, private_key = proof(now)
    grants, observations, revocations = Collection(), Collection(), Collection()
    grant = create_grant(attempt, receipt, current, proof_value, now, grants)
    current_identity = "p2-current-identity-p5l"
    captured_at = now + timedelta(seconds=1)
    signed_payload = location_observation_signed_payload(
        tenant_id=TENANT, attempt_id=attempt.attempt_id,
        current_evidence_identity=current_identity, deputy_id=DEPUTY_ID,
        device_id=proof_value.device_id, challenge_id=proof_value.challenge_id,
        grant_id=grant.grant_id, observation_id="observation-tampered",
        latitude=-26.2041, longitude=28.0473, horizontal_accuracy_m=10.0,
        captured_at=captured_at,
    )
    der = private_key.sign(signed_payload, ec.ECDSA(hashes.SHA256()))
    r_value, s_value = decode_dss_signature(der)
    location_signature = r_value.to_bytes(32, "big") + s_value.to_bytes(32, "big")
    with pytest.raises(ProcessServiceLocationEvidenceOrchestrationError) as error:
        record_process_service_location_observation(
            attempt=attempt, allocation_receipt=receipt, allocation_current=current,
            device_provenance=proof_value, principal_id=PRINCIPAL, grant_id=grant.grant_id,
            observation_id="observation-tampered", current_evidence_identity=current_identity,
            location_signature_p1363=location_signature, latitude=-26.2, longitude=28.0473,
            horizontal_accuracy_m=10.0, captured_at=captured_at,
            permission_collection=grants, observation_collection=observations,
            revocation_collection=revocations, session=Session(),
        )
    assert error.value.code == "P5L_LOCATION_SIGNATURE_VERIFICATION_FAILED"
    assert observations.docs == []


def test_offline_capture_before_withdrawal_can_sync_after_revocation():
    attempt, receipt, current, now = sources()
    proof_value, private_key = proof(now)
    grants, observations, revocations = Collection(), Collection(), Collection()
    grant = create_grant(attempt, receipt, current, proof_value, now, grants)
    captured_at = now + timedelta(seconds=1)
    current_identity = "p2-current-identity-p5l"
    signed_payload = location_observation_signed_payload(
        tenant_id=TENANT, attempt_id=attempt.attempt_id,
        current_evidence_identity=current_identity, deputy_id=DEPUTY_ID,
        device_id=proof_value.device_id, challenge_id=proof_value.challenge_id,
        grant_id=grant.grant_id, observation_id="observation-before-revoke",
        latitude=-26.2041, longitude=28.0473, horizontal_accuracy_m=10.0,
        captured_at=captured_at,
    )
    der = private_key.sign(signed_payload, ec.ECDSA(hashes.SHA256()))
    r_value, s_value = decode_dss_signature(der)
    location_signature = r_value.to_bytes(32, "big") + s_value.to_bytes(32, "big")
    revoke_process_service_location_permission_grant(
        tenant_id=TENANT, grant_id=grant.grant_id, revocation_id="revoke-after-capture",
        revoked_by_principal_id=PRINCIPAL, revoked_at=now + timedelta(seconds=2),
        reason_reference="user-withdrew-after-capture", grant_collection=grants,
        revocation_collection=revocations, session=Session(),
    )
    value = record_process_service_location_observation(
        attempt=attempt, allocation_receipt=receipt, allocation_current=current,
        device_provenance=proof_value, principal_id=PRINCIPAL, grant_id=grant.grant_id,
        observation_id="observation-before-revoke", current_evidence_identity=current_identity,
        location_signature_p1363=location_signature, latitude=-26.2041, longitude=28.0473,
        horizontal_accuracy_m=10.0, captured_at=captured_at,
        permission_collection=grants, observation_collection=observations,
        revocation_collection=revocations, session=Session(),
    )
    assert value.observation_id == "observation-before-revoke"
    assert len(observations.docs) == 1



def test_location_orchestration_requires_caller_transaction():
    attempt, receipt, current, now = sources()
    with pytest.raises(ProcessServiceLocationEvidenceOrchestrationError):
        issue_process_service_location_permission_grant(
            attempt=attempt, allocation_receipt=receipt, allocation_current=current,
            device_provenance=proof(now)[0], principal_id=PRINCIPAL, grant_id="grant-no-tx",
            permission_granted=True, permission_notice_version="location-notice-v1",
            granted_at=now, permission_collection=Collection(), session=None,
        )


# ARTIFACT: test_process_service_location_evidence_orchestrator.py
# AUTHORITY: Synthetic cryptographic key, identity and collection only.
# PRIVACY: Explicit grant, 15-minute expiry, revocation and one-shot GPS observation.
# END OF WILSY OS SOVEREIGN ARTIFACT
