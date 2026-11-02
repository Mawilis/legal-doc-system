"""Adversarial registry tests for immutable purpose-bound GPS evidence."""
from __future__ import annotations

from base64 import b64encode
from copy import deepcopy
from datetime import datetime, timedelta, timezone
import hashlib
from types import SimpleNamespace
from typing import Any

import pytest
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.primitives.asymmetric.utils import decode_dss_signature
from pymongo.errors import DuplicateKeyError

from tools.eos.legal_operations.domain.legal_operations_lifecycle import (
    ServiceAttempt,
    ServiceAttemptState,
)
from tools.eos.legal_operations.orchestration.process_service_location_evidence_orchestrator import location_observation_signed_payload
from tools.eos.legal_operations.domain.process_service_location_evidence_authority import (
    LOCATION_PURPOSE,
    create_location_permission_grant,
    create_process_service_location_observation,
)
from tools.eos.legal_operations.registry.process_service_allocation_registry import (
    ProcessServiceAllocationCurrent,
    ProcessServiceAllocationReceipt,
)
from tools.eos.legal_operations.registry.process_service_location_evidence_registry import (
    ACCESS_AUDIT_COLLECTION,
    OBSERVATION_COLLECTION,
    PERMISSION_COLLECTION,
    REVOCATION_COLLECTION,
    ProcessServiceLocationEvidenceRegistry as Registry,
    ProcessServiceLocationEvidenceRegistryConflictError,
    ProcessServiceLocationEvidenceRegistryRecordInvalidError,
    ProcessServiceLocationEvidenceRegistryTransactionRequiredError,
)

BASE = datetime(2026, 10, 30, 8, 0, tzinfo=timezone.utc)
HASH = "a" * 128
TENANT = "tenant-location-registry"


class Session:
    in_transaction = True


class Cursor:
    def __init__(self, rows: list[dict[str, Any]]) -> None:
        self.rows = rows

    def sort(self, _keys):
        self.rows.sort(key=lambda row: (row["payload"]["captured_at"], row["observation_id"]))
        return self

    def __iter__(self):
        return iter(deepcopy(self.rows))


class Collection:
    def __init__(self) -> None:
        self.docs: list[dict[str, Any]] = []
        self.indexes: list[dict[str, Any]] = []
        self.calls: list[tuple[str, object, object]] = []

    @staticmethod
    def matches(doc: dict[str, Any], query: dict[str, Any]) -> bool:
        return all(doc.get(key) == value for key, value in query.items())

    def find_one(self, query: dict[str, Any], *, session: object = None):
        self.calls.append(("find_one", session, deepcopy(query)))
        return deepcopy(next((d for d in self.docs if self.matches(d, query)), None))

    def insert_one(self, document: dict[str, Any], *, session: object = None):
        self.calls.append(("insert_one", session, deepcopy(document)))
        identity = {key: document[key] for key in ("tenant_id", "grant_id") if key in document}
        if "observation_id" in document:
            identity = {"tenant_id": document["tenant_id"], "observation_id": document["observation_id"]}
        if "event_id" in document:
            identity = {"tenant_id": document["tenant_id"], "event_id": document["event_id"]}
        if "revocation_id" in document:
            identity = {"tenant_id": document["tenant_id"], "grant_id": document["grant_id"]}
        if any(self.matches(row, identity) for row in self.docs):
            raise DuplicateKeyError("duplicate")
        self.docs.append(deepcopy(document))
        return SimpleNamespace(inserted_id=len(self.docs))

    def create_index(self, keys, **kwargs):
        self.indexes.append({"keys": keys, **kwargs})
        return kwargs.get("name")

    def find(self, query: dict[str, Any], *, session: object = None):
        self.calls.append(("find", session, deepcopy(query)))
        return Cursor([deepcopy(row) for row in self.docs if self.matches(row, query)])


def sources():
    attempt = ServiceAttempt(
        tenant_id=TENANT, attempt_id="attempt-1",
        instruction_id="instruction-1", document_id="document-1",
        deputy_id="deputy-1", allocated_at=BASE,
        allocation_evidence_reference="allocation",
    ).transition_to(
        ServiceAttemptState.ATTEMPTED, evidence_reference="attempt-proof",
        evidence_fingerprint=HASH, occurred_at=BASE + timedelta(minutes=1),
    )
    receipt = ProcessServiceAllocationReceipt(
        tenant_id=TENANT, allocation_command_id="allocation-command",
        idempotency_key="allocation-key", instruction_id="instruction-1",
        case_matter_id="matter-1", document_id="document-1", district_id="district-1",
        sheriff_office_id="office-1", deputy_id="deputy-1",
        assignment_decision_id="assignment-1", assignment_decision_fingerprint=HASH,
        source_instruction_fingerprint=HASH, source_document_fingerprint=HASH,
        source_district_fingerprint=HASH, source_sheriff_office_fingerprint=HASH,
        source_deputy_fingerprint=HASH, prior_custody_chain_fingerprint=HASH,
        prior_custody_head_event_id="head-1", prior_custody_head_fingerprint=HASH,
        prior_custody_head_sequence_number=1, from_holder_reference="office-1",
        to_holder_reference="deputy-1", allocation_custody_event_id="allocation-event",
        allocation_evidence_reference="allocation", allocated_at=BASE,
        allocated_document_fingerprint=HASH, allocation_custody_event_fingerprint=HASH,
        result_custody_chain_fingerprint=HASH,
    )
    current = ProcessServiceAllocationCurrent(
        tenant_id=TENANT, document_id="document-1",
        process_document_fingerprint=HASH, custody_chain_fingerprint=HASH,
        custody_head_event_id="allocation-event", custody_head_fingerprint=HASH,
        custody_head_sequence_number=2, current_holder_reference="deputy-1",
        authority_evidence_reference="allocation-command",
        authority_evidence_fingerprint=receipt.fingerprint,
    )
    return attempt, receipt, current


def grant(*, grant_id: str = "grant-1", device_id: str = "device-1"):
    attempt, receipt, current = sources()
    return create_location_permission_grant(
        attempt=attempt, allocation_receipt=receipt, allocation_current=current,
        grant_id=grant_id, device_id=device_id, permission_granted=True,
        purpose=LOCATION_PURPOSE, permission_evidence_reference="permission-event",
        permission_evidence_fingerprint=HASH, granted_at=BASE + timedelta(minutes=2),
        expires_at=BASE + timedelta(minutes=20),
    )


def observation():
    attempt, receipt, current = sources()
    private_key = ec.generate_private_key(ec.SECP256R1())
    public_der = private_key.public_key().public_bytes(
        serialization.Encoding.DER, serialization.PublicFormat.SubjectPublicKeyInfo
    )
    device_id = f"deputy-device:{hashlib.sha3_512(public_der).hexdigest()}"
    value = create_process_service_location_observation(
        attempt=attempt, allocation_receipt=receipt, allocation_current=current,
        permission_grant=grant(device_id=device_id), observation_id="observation-1", device_id=device_id,
        latitude=-26.2041, longitude=28.0473, horizontal_accuracy_m=12.5,
        captured_at=BASE + timedelta(minutes=3),
        device_provenance_reference="challenge-proof-1",
        device_provenance_fingerprint=HASH, evidence_reference="gps-event-1",
    )
    signed = location_observation_signed_payload(
        tenant_id=TENANT, attempt_id="attempt-1",
        current_evidence_identity="p2-current-identity-1", deputy_id="deputy-1",
        device_id=device_id, challenge_id="challenge-proof-1", grant_id="grant-1",
        observation_id="observation-1", latitude=-26.2041, longitude=28.0473,
        horizontal_accuracy_m=12.5, captured_at=BASE + timedelta(minutes=3),
    )
    der = private_key.sign(signed, ec.ECDSA(hashes.SHA256()))
    r_value, s_value = decode_dss_signature(der)
    signature = r_value.to_bytes(32, "big") + s_value.to_bytes(32, "big")
    return value, signature, b64encode(public_der).decode("ascii"), hashlib.sha3_512(signed).hexdigest(), "p2-current-identity-1"


def test_grant_persistence_exact_replay_and_source_hydration():
    collection = Collection()
    value = grant()
    assert Registry.persist_permission_grant(value, collection, session=Session()) == value
    assert Registry.persist_permission_grant(value, collection, session=Session()) == value
    attempt, receipt, current = sources()
    hydrated = Registry.get_permission_grant(
        TENANT, "grant-1", collection, attempt=attempt,
        allocation_receipt=receipt, allocation_current=current, session=Session(),
    )
    assert hydrated.to_dict() == value.to_dict()
    assert len(collection.docs) == 1


def test_divergent_grant_replay_and_foreign_tenant_are_rejected():
    collection = Collection()
    Registry.persist_permission_grant(grant(), collection, session=Session())
    with pytest.raises(ProcessServiceLocationEvidenceRegistryConflictError):
        Registry.persist_permission_grant(
            grant(device_id="other-device"), collection, session=Session()
        )
    with pytest.raises(ProcessServiceLocationEvidenceRegistryConflictError):
        Registry.get_permission_grant(
            "foreign-tenant", "grant-1", collection,
            attempt=sources()[0], allocation_receipt=sources()[1],
            allocation_current=sources()[2], session=Session(),
        )
    assert len(collection.docs) == 1


def test_observation_append_only_replay_and_integrity_checked_listing():
    collection = Collection()
    value, signature, public_key, payload_fingerprint, current_identity = observation()
    kwargs = {
        "current_evidence_identity": current_identity,
        "location_signature_p1363": signature,
        "device_public_key_spki": public_key,
        "signed_payload_fingerprint": payload_fingerprint,
    }
    Registry.persist_observation(value, collection, session=Session(), **kwargs)
    Registry.persist_observation(value, collection, session=Session(), **kwargs)
    rows = Registry.list_observations_for_attempt(
        TENANT, "attempt-1", collection, session=Session()
    )
    assert len(rows) == 1
    assert rows[0]["latitude"] == -26.2041
    assert rows[0]["observation_id"] == "observation-1"
    collection.docs[0]["payload"]["latitude"] = -25.0
    with pytest.raises(ProcessServiceLocationEvidenceRegistryRecordInvalidError):
        Registry.list_observations_for_attempt(
            TENANT, "attempt-1", collection, session=Session()
        )


def test_revocation_is_append_only_and_blocks_future_grant_use():
    grants, revocations = Collection(), Collection()
    Registry.persist_permission_grant(grant(), grants, session=Session())
    event = Registry.revoke_permission_grant(
        tenant_id=TENANT, grant_id="grant-1", revocation_id="revoke-1",
        revoked_by_principal_id="deputy-principal",
        revoked_at=BASE + timedelta(minutes=4), reason_reference="user-withdrew-permission",
        evidence_reference="permission-revocation-event",
        grant_collection=grants, revocation_collection=revocations, session=Session(),
    )
    assert event["entity_type"] == "ProcessServiceLocationPermissionRevocation"
    with pytest.raises(ProcessServiceLocationEvidenceRegistryConflictError) as error:
        Registry.assert_permission_grant_active(
            TENANT, "grant-1", revocations, session=Session()
        )
    assert error.value.code == "P5L_PERMISSION_GRANT_REVOKED"
    with pytest.raises(ProcessServiceLocationEvidenceRegistryConflictError):
        Registry.revoke_permission_grant(
            tenant_id=TENANT, grant_id="grant-1", revocation_id="revoke-2",
            revoked_by_principal_id="deputy-principal",
            revoked_at=BASE + timedelta(minutes=5), reason_reference="different-reason",
            evidence_reference="different-event",
            grant_collection=grants, revocation_collection=revocations, session=Session(),
        )
    assert len(grants.docs) == 1 and len(revocations.docs) == 1



def test_revocation_binding_can_be_checked_after_attempt_terminal_transition():
    grants = Collection()
    Registry.persist_permission_grant(grant(), grants, session=Session())
    payload = Registry.assert_permission_grant_attempt_binding(
        TENANT, "grant-1", "attempt-1", "deputy-1", grants, session=Session()
    )
    assert payload["attempt_id"] == "attempt-1"
    assert payload["deputy_id"] == "deputy-1"
    with pytest.raises(ProcessServiceLocationEvidenceRegistryConflictError):
        Registry.assert_permission_grant_attempt_binding(
            TENANT, "grant-1", "attempt-foreign", "deputy-1", grants, session=Session()
        )

def test_access_audit_is_metadata_only_and_tenant_scoped():
    collection = Collection()
    event = Registry.record_access(
        tenant_id=TENANT, event_id="access-1", attempt_id="attempt-1",
        grant_id="grant-1", actor_principal_id="sheriff-principal",
        actor_scope="SHERIFF_OFFICE", accessed_at=BASE + timedelta(minutes=5),
        record_count=1, purpose="review-location-evidence",
        collection=collection, session=Session(),
    )
    assert event["record_count"] == 1
    assert "latitude" not in event and "longitude" not in event
    assert event["actor_principal_id"] == "sheriff-principal"


def test_indexes_are_unique_and_never_create_ttl_retention():
    collections = [Collection() for _ in range(4)]
    Registry.ensure_indexes(*collections)
    all_indexes = [index for collection in collections for index in collection.indexes]
    assert len(all_indexes) == 7
    assert all("expireAfterSeconds" not in index for index in all_indexes)
    assert collections[0].indexes[0]["unique"] is True


def test_transaction_is_required_before_any_registry_io():
    collection = Collection()
    with pytest.raises(ProcessServiceLocationEvidenceRegistryTransactionRequiredError):
        Registry.persist_permission_grant(grant(), collection, session=None)
    assert collection.calls == []


# ARTIFACT: test_process_service_location_evidence_registry.py
# AUTHORITY: Synthetic collection only; no production data or Mongo state.
# REPLAY: Exact immutable grant/observation replay; divergent replay rejects.
# REVOCATION: Append-only event blocks subsequent use; original grant remains immutable.
# RETENTION: No TTL; policy-specific lifecycle must be approved before enforcement.
# END OF WILSY OS SOVEREIGN ARTIFACT
