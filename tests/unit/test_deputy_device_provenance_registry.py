"""Focused L8-6H registry certificate: transaction scope, persistence and replay."""
from __future__ import annotations

from copy import deepcopy
from datetime import datetime, timedelta, timezone
from types import SimpleNamespace
from typing import Any

import pytest
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.primitives.asymmetric.utils import decode_dss_signature
from pymongo.errors import DuplicateKeyError

from tools.eos.legal_operations.domain.deputy_device_provenance_authority import (
    DeputyDeviceProvenanceChallenge,
)
from tools.eos.legal_operations.domain.deputy_principal_binding import (
    DeputyPrincipalBinding,
)
from tools.eos.legal_operations.domain.legal_operations_lifecycle import Deputy
from tools.eos.legal_operations.registry.deputy_device_provenance_registry import (
    DeputyDeviceProvenanceRegistry,
    DeputyDeviceProvenanceRegistryConflictError,
    DeputyDeviceProvenanceRegistryTransactionRequiredError,
)

NOW = datetime(2026, 10, 30, 12, 0, tzinfo=timezone.utc)
TENANT, PRINCIPAL, DEPUTY_ID, OFFICE, SESSION_REF = (
    "tenant-a", "principal-1", "deputy-1", "office-1", "session-1"
)


class FakeSession:
    def __init__(self, active: bool = True) -> None:
        self.in_transaction = active


class FakeCollection:
    """Exact-query fake; update_one models a single-document atomic CAS."""
    def __init__(self) -> None:
        self.docs: list[dict[str, Any]] = []
        self.calls: list[tuple[str, object, object]] = []
        self.indexes: list[dict[str, Any]] = []
        self.force_cas_miss = False

    @staticmethod
    def _matches(doc: dict[str, Any], query: dict[str, Any]) -> bool:
        return all(doc.get(key) == value for key, value in query.items())

    def find_one(self, query: dict[str, Any], *, session: object = None):
        self.calls.append(("find_one", session, deepcopy(query)))
        return next(
            (deepcopy(doc) for doc in self.docs if self._matches(doc, query)),
            None,
        )

    def insert_one(self, document: dict[str, Any], *, session: object = None):
        self.calls.append(("insert_one", session, deepcopy(document)))
        if any(self._matches(doc, {
            "tenant_id": document["tenant_id"],
            "challenge_id": document["challenge_id"],
        }) for doc in self.docs):
            raise DuplicateKeyError("duplicate challenge")
        self.docs.append(deepcopy(document))
        return SimpleNamespace(inserted_id=len(self.docs))

    def update_one(
        self, query: dict[str, Any], update: dict[str, Any],
        *, upsert: bool = False, session: object = None,
    ):
        self.calls.append(("update_one", session, deepcopy(query)))
        if self.force_cas_miss:
            return SimpleNamespace(matched_count=0, modified_count=0)
        for doc in self.docs:
            if self._matches(doc, query):
                before = deepcopy(doc)
                doc.update(deepcopy(update["$set"]))
                return SimpleNamespace(
                    matched_count=1, modified_count=int(doc != before)
                )
        return SimpleNamespace(matched_count=0, modified_count=0)

    def create_index(self, keys, **kwargs):
        self.indexes.append({"keys": keys, **kwargs})
        return kwargs.get("name")


class FakeAuthRegistry:
    def __init__(self) -> None:
        self.current = True
        self.calls: list[tuple[Any, ...]] = []

    def is_session_current(
        self, tenant_id, user_id, session_reference, *, at=None, session=None
    ):
        self.calls.append((tenant_id, user_id, session_reference, at, session))
        return self.current


def fixture():
    deputy = Deputy(
        tenant_id=TENANT, deputy_id=DEPUTY_ID,
        sheriff_office_id=OFFICE, display_name="Synthetic Deputy",
        badge_reference="badge-1", evidence_reference="deputy-evidence",
    )
    binding = DeputyPrincipalBinding.from_deputy(
        principal_id=PRINCIPAL, deputy=deputy,
        bound_at=NOW - timedelta(days=1), evidence_reference="binding-evidence",
    )
    binding_store = FakeCollection()
    binding_store.docs.append(binding.to_dict())
    challenge_store = FakeCollection()
    auth = FakeAuthRegistry()
    registry = DeputyDeviceProvenanceRegistry(
        challenge_store, auth_registry=auth, binding_collection=binding_store
    )
    private_key = ec.generate_private_key(ec.SECP256R1())
    public_der = private_key.public_key().public_bytes(
        serialization.Encoding.DER,
        serialization.PublicFormat.SubjectPublicKeyInfo,
    )
    challenge = DeputyDeviceProvenanceChallenge.issue(
        binding=binding, session_reference=SESSION_REF,
        challenge_id="challenge-1", public_key_spki_der=public_der,
        nonce=b"N" * 32, issued_at=NOW,
        expires_at=NOW + timedelta(minutes=2),
    )
    return registry, challenge_store, binding_store, auth, private_key, challenge, FakeSession()


def signature(private_key, challenge) -> bytes:
    der = private_key.sign(challenge.signed_payload(), ec.ECDSA(hashes.SHA256()))
    r, s = decode_dss_signature(der)
    return r.to_bytes(32, "big") + s.to_bytes(32, "big")


def test_create_persists_exact_challenge_and_propagates_one_session():
    registry, store, binding_store, auth, _, challenge, session = fixture()
    assert registry.create(challenge, session=session).to_dict() == challenge.to_dict()
    assert len(store.docs) == 1
    assert store.docs[0]["consumed_at"] is None
    assert auth.calls == [(TENANT, PRINCIPAL, SESSION_REF, NOW, session)]
    assert all(call[1] is session for call in store.calls + binding_store.calls)


def test_exact_create_replay_is_idempotent_and_divergent_replay_conflicts():
    registry, store, _, _, _, challenge, session = fixture()
    registry.create(challenge, session=session)
    assert registry.create(challenge, session=session).to_dict() == challenge.to_dict()
    other_key = ec.generate_private_key(ec.SECP256R1())
    other_der = other_key.public_key().public_bytes(
        serialization.Encoding.DER, serialization.PublicFormat.SubjectPublicKeyInfo
    )
    other = DeputyDeviceProvenanceChallenge.issue(
        binding=DeputyPrincipalBinding.from_deputy(
            principal_id=PRINCIPAL,
            deputy=Deputy(
                tenant_id=TENANT, deputy_id=DEPUTY_ID,
                sheriff_office_id=OFFICE, display_name="Synthetic Deputy",
                badge_reference="badge-1", evidence_reference="deputy-evidence",
            ),
            bound_at=NOW - timedelta(days=1), evidence_reference="binding-evidence",
        ),
        session_reference=SESSION_REF, challenge_id="challenge-1",
        public_key_spki_der=other_der, nonce=b"Z" * 32, issued_at=NOW,
        expires_at=NOW + timedelta(minutes=2),
    )
    with pytest.raises(DeputyDeviceProvenanceRegistryConflictError):
        registry.create(other, session=session)
    assert len(store.docs) == 1


def test_inactive_transaction_rejects_before_any_storage_or_session_read():
    registry, store, binding_store, auth, _, challenge, _ = fixture()
    with pytest.raises(DeputyDeviceProvenanceRegistryTransactionRequiredError):
        registry.create(challenge, session=FakeSession(False))
    assert store.calls == binding_store.calls == auth.calls == []


def test_valid_proof_is_atomically_consumed_once_and_replay_is_rejected():
    registry, store, _, auth, key, challenge, session = fixture()
    registry.create(challenge, session=session)
    verified_at = NOW + timedelta(seconds=1)
    proof = registry.verify_and_consume(
        tenant_id=TENANT, challenge_id="challenge-1",
        signature_p1363=signature(key, challenge),
        verified_at=verified_at, session=session,
    )
    row = store.docs[0]
    assert row["consumed_at"] == verified_at.isoformat(timespec="microseconds")
    assert row["provenance"]["challenge_id"] == "challenge-1"
    assert row["provenance_fingerprint"] == proof.fingerprint
    writes = [call for call in store.calls if call[0] == "update_one"]
    assert len(writes) == 1 and writes[0][1] is session
    assert auth.calls[-1] == (TENANT, PRINCIPAL, SESSION_REF, verified_at, session)
    with pytest.raises(DeputyDeviceProvenanceRegistryConflictError):
        registry.verify_and_consume(
            tenant_id=TENANT, challenge_id="challenge-1",
            signature_p1363=signature(key, challenge),
            verified_at=NOW + timedelta(seconds=2), session=session,
        )
    assert len([call for call in store.calls if call[0] == "update_one"]) == 1



def test_consumed_device_provenance_can_be_reloaded_for_delayed_signed_sync():
    registry, store, binding_store, auth, key, challenge, session = fixture()
    registry.create(challenge, session=session)
    signature = _signature(key, challenge)
    proof = registry.verify_and_consume(
        tenant_id=TENANT,
        challenge_id=challenge.challenge_id,
        signature_p1363=signature,
        verified_at=NOW + timedelta(seconds=1),
        session=session,
    )
    restored = registry.get_consumed_provenance(
        tenant_id=TENANT,
        challenge_id=challenge.challenge_id,
        principal_id=PRINCIPAL,
        session_reference=SESSION_REF,
        at=NOW + timedelta(seconds=2),
        session=session,
    )
    assert restored.fingerprint == proof.fingerprint
    assert restored.public_key_spki == proof.public_key_spki
    assert restored.challenge_id == challenge.challenge_id
    auth.current = False
    with pytest.raises(DeputyDeviceProvenanceRegistryConflictError):
        registry.get_consumed_provenance(
            tenant_id=TENANT,
            challenge_id=challenge.challenge_id,
            principal_id=PRINCIPAL,
            session_reference=SESSION_REF,
            at=NOW + timedelta(seconds=3),
            session=session,
        )



def test_stale_session_bad_signature_and_cas_miss_do_not_consume():
    registry, store, _, auth, key, challenge, session = fixture()
    registry.create(challenge, session=session)
    auth.current = False
    with pytest.raises(DeputyDeviceProvenanceRegistryConflictError):
        registry.verify_and_consume(
            tenant_id=TENANT, challenge_id="challenge-1",
            signature_p1363=signature(key, challenge),
            verified_at=NOW + timedelta(seconds=1), session=session,
        )
    auth.current = True
    with pytest.raises(DeputyDeviceProvenanceRegistryConflictError):
        registry.verify_and_consume(
            tenant_id=TENANT, challenge_id="challenge-1",
            signature_p1363=b"\x00" * 64,
            verified_at=NOW + timedelta(seconds=1), session=session,
        )
    store.force_cas_miss = True
    with pytest.raises(DeputyDeviceProvenanceRegistryConflictError):
        registry.verify_and_consume(
            tenant_id=TENANT, challenge_id="challenge-1",
            signature_p1363=signature(key, challenge),
            verified_at=NOW + timedelta(seconds=1), session=session,
        )
    assert store.docs[0]["consumed_at"] is None
    assert store.docs[0]["provenance"] is None


def test_indexes_are_tenant_scoped_and_not_ttl():
    registry, store, _, _, _, _, _ = fixture()
    registry.ensure_indexes()
    assert len(store.indexes) == 2
    assert store.indexes[0]["keys"] == [("tenant_id", 1), ("challenge_id", 1)]
    assert store.indexes[0]["unique"] is True
    assert all("expireAfterSeconds" not in item for item in store.indexes)


# ARTIFACT: tests/unit/test_deputy_device_provenance_registry.py
# AUTHORITY: Synthetic collection and key only; no production data or Mongo state.
# REPLAY: Exact create replay, divergent replay and single-use proof consumption.
# TRANSACTION: One caller-owned active session propagated to every registry operation.
# END OF WILSY OS SOVEREIGN ARTIFACT
