"""Direct certificate for recovery-contact verification persistence.

TITLE: WILSY OS Recovery Contact Verification Registry Certificate
VERSION: v1.0.0-R10E13-RECOVERY-CONTACT-VERIFICATION-REGISTRY-CERT
AUTHORITY: Wilsy OS Core Governance
EPITOME: Certifies digest-only challenge persistence and lifecycle CAS.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tests/unit/test_recovery_contact_verification_registry.py
COLLABORATION / OWNERSHIP: Deterministic in-memory PyMongo-shaped evidence only.
CERTIFICATION / UPDATE DATE: 2026-09-22
CHANGELOG:
  v1.0.0-R10E13-RECOVERY-CONTACT-VERIFICATION-REGISTRY-CERT — Certifies indexes,
    insert-only creation, tenant/digest lookup, active contact scope, session
    forwarding, consume/expire/revoke CAS, corruption detection, and raw-token exclusion.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2; ISO 27001.
SECURITY / PRIVACY POSTURE: Synthetic digest/address only.
TENANT BOUNDARY: Exact tenant/principal/contact scope.
AUTHORITY BOUNDARY: Persistence evidence only.
FINANCIAL AUTHORITY BOUNDARY: None; Kennel EOS remains exclusively financial.
"""

from __future__ import annotations

import hashlib
from copy import deepcopy
from datetime import datetime, timedelta, timezone
from typing import Any

import pytest
from pymongo.errors import DuplicateKeyError, PyMongoError

from tools.eos.saas.auth.recovery_contact_verification import (
    RecoveryContactVerificationChallenge,
    RecoveryContactVerificationStatus,
)
from tools.eos.saas.auth.recovery_contact_verification_registry import (
    COLLECTION,
    INDEX_DEFINITIONS,
    RecoveryContactVerificationAlreadyExistsError,
    RecoveryContactVerificationLifecycleConflictError,
    RecoveryContactVerificationPersistedRecordInvalidError,
    RecoveryContactVerificationPersistenceError,
    RecoveryContactVerificationRegistry,
)


NOW = datetime(2026, 9, 22, 19, 30, 0, tzinfo=timezone.utc)


class _Collection:
    def __init__(self) -> None:
        self.rows: list[dict[str, Any]] = []
        self.calls: list[dict[str, Any]] = []
        self.index_calls: list[tuple[list[tuple[str, int]], dict[str, Any]]] = []
        self.force_miss = False
        self.fail_reads = False

    @staticmethod
    def _matches(row: dict[str, Any], query: dict[str, Any]) -> bool:
        return all(row.get(key) == value for key, value in query.items())

    def create_index(self, keys: list[tuple[str, int]], **options: Any) -> str:
        self.index_calls.append((list(keys), dict(options)))
        return str(options["name"])

    def insert_one(self, document: dict[str, Any], **options: Any) -> object:
        self.calls.append({"method": "insert_one", "document": deepcopy(document), "options": options})
        if any(row["challenge_id"] == document["challenge_id"] for row in self.rows):
            raise DuplicateKeyError("id")
        if any(row["token_digest"] == document["token_digest"] for row in self.rows):
            raise DuplicateKeyError("digest")
        self.rows.append(deepcopy(document))
        return object()

    def find_one(self, query: dict[str, Any], **options: Any) -> dict[str, Any] | None:
        self.calls.append({"method": "find_one", "query": deepcopy(query), "options": options})
        if self.fail_reads:
            raise PyMongoError("read")
        for row in self.rows:
            if self._matches(row, query):
                return deepcopy(row)
        return None

    def find(self, query: dict[str, Any], **options: Any):
        self.calls.append({"method": "find", "query": deepcopy(query), "options": options})
        if self.fail_reads:
            raise PyMongoError("read")
        return [deepcopy(row) for row in self.rows if self._matches(row, query)]

    def find_one_and_replace(
        self, query: dict[str, Any], replacement: dict[str, Any], **options: Any
    ) -> dict[str, Any] | None:
        self.calls.append({"method": "find_one_and_replace", "query": deepcopy(query), "replacement": deepcopy(replacement), "options": options})
        if self.force_miss:
            return None
        for index, row in enumerate(self.rows):
            if self._matches(row, query):
                self.rows[index] = deepcopy(replacement)
                return deepcopy(replacement)
        return None


def _challenge(challenge_id: str = "challenge-a", seed: str = "seed") -> RecoveryContactVerificationChallenge:
    return RecoveryContactVerificationChallenge.issue(
        challenge_id=challenge_id,
        tenant_id="tenant-a",
        principal_id="principal-a",
        contact_id="contact-a",
        address="person@example.com",
        token_digest=hashlib.sha3_512(seed.encode()).hexdigest(),
        issued_at=NOW,
        expires_at=NOW + timedelta(minutes=15),
    )


def _registry() -> tuple[RecoveryContactVerificationRegistry, _Collection, object]:
    collection = _Collection()
    return RecoveryContactVerificationRegistry(collection), collection, object()


def test_index_contract() -> None:
    registry, collection, _ = _registry()
    registry.ensure_indexes()
    assert COLLECTION == "recovery_contact_verification_challenges"
    assert len(INDEX_DEFINITIONS) == 3
    assert [options["name"] for _, options in collection.index_calls] == [
        "recovery_contact_verification_identity_unique",
        "recovery_contact_verification_digest_unique",
        "recovery_contact_verification_active_scope",
    ]


def test_create_persists_digest_only_and_session() -> None:
    registry, collection, session = _registry()
    challenge = _challenge()
    assert registry.create(challenge, session=session) == challenge
    inserted = collection.calls[-1]
    assert inserted["document"]["token_digest"] == challenge.token_digest
    assert "recovery_token" not in inserted["document"]
    assert inserted["options"]["session"] is session


def test_duplicate_identity_and_digest_fail_closed() -> None:
    registry, _collection, session = _registry()
    first = _challenge()
    registry.create(first, session=session)
    with pytest.raises(RecoveryContactVerificationAlreadyExistsError):
        registry.create(first, session=session)
    with pytest.raises(RecoveryContactVerificationAlreadyExistsError):
        registry.create(_challenge("challenge-b", "seed"), session=session)


def test_digest_lookup_is_tenant_scoped() -> None:
    registry, collection, session = _registry()
    challenge = _challenge()
    registry.create(challenge, session=session)
    assert registry.get_by_token_digest(
        tenant_id="tenant-b",
        token_digest=challenge.token_digest,
        session=session,
    ) is None
    call = collection.calls[-1]
    assert call["query"]["tenant_id"] == "tenant-b"
    assert call["options"]["session"] is session


def test_active_contact_scope_returns_only_exact_binding() -> None:
    registry, _collection, session = _registry()
    challenge = _challenge()
    registry.create(challenge, session=session)
    assert registry.list_active_for_contact(
        tenant_id="tenant-a",
        principal_id="principal-a",
        contact_id="contact-a",
        session=session,
    ) == (challenge,)
    assert registry.list_active_for_contact(
        tenant_id="tenant-a",
        principal_id="principal-other",
        contact_id="contact-a",
        session=session,
    ) == ()


def test_consume_cas_preserves_session_and_rejects_replay() -> None:
    registry, collection, session = _registry()
    challenge = _challenge()
    registry.create(challenge, session=session)
    consumed = registry.consume(challenge, NOW + timedelta(minutes=1), session=session)
    assert consumed.status is RecoveryContactVerificationStatus.CONSUMED
    cas = collection.calls[-1]
    assert cas["method"] == "find_one_and_replace"
    assert cas["query"]["status"] == "ACTIVE"
    assert cas["options"]["session"] is session
    with pytest.raises(RecoveryContactVerificationLifecycleConflictError):
        registry.consume(challenge, NOW + timedelta(minutes=2), session=session)


def test_expire_and_revoke_are_exact_terminal_transitions() -> None:
    registry, _collection, session = _registry()
    expiring = _challenge("expire", "expire")
    registry.create(expiring, session=session)
    expired = registry.expire(expiring, NOW + timedelta(minutes=15), session=session)
    assert expired.status is RecoveryContactVerificationStatus.EXPIRED

    revoking = _challenge("revoke", "revoke")
    registry.create(revoking, session=session)
    revoked = registry.revoke(revoking, NOW + timedelta(minutes=2), session=session)
    assert revoked.status is RecoveryContactVerificationStatus.REVOKED


def test_corrupt_metadata_and_read_failure_are_not_absence() -> None:
    registry, collection, session = _registry()
    challenge = _challenge()
    registry.create(challenge, session=session)
    collection.rows[0]["_expires_at_epoch_us"] += 1
    with pytest.raises(RecoveryContactVerificationPersistedRecordInvalidError):
        registry.get_by_token_digest(
            tenant_id="tenant-a",
            token_digest=challenge.token_digest,
            session=session,
        )

    clean_registry, clean_collection, _ = _registry()
    clean_collection.fail_reads = True
    with pytest.raises(RecoveryContactVerificationPersistenceError):
        clean_registry.get_by_token_digest(
            tenant_id="tenant-a",
            token_digest=challenge.token_digest,
        )


# ARTIFACT: tests/unit/test_recovery_contact_verification_registry.py
# VERSION: v1.0.0-R10E13-RECOVERY-CONTACT-VERIFICATION-REGISTRY-CERT
# AUTHORITY BOUNDARY: deterministic digest-only verification persistence evidence
# TENANT POSTURE: exact tenant/principal/contact scope
# FAIL-CLOSED POSTURE: duplicate, corrupt, stale, replayed, and cross-tenant challenge state rejects
# FINANCIAL EXECUTION AUTHORITY: None; Kennel EOS remains exclusively financial
# END OF WILSY OS SOVEREIGN ARTIFACT
