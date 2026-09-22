"""Direct unit certificate for the WILSY OS password-recovery registry.

TITLE: WILSY OS Password Recovery Registry Direct Certificate
VERSION: v1.0.0-R10B3-PASSWORD-RECOVERY-REGISTRY-CERT
AUTHORITY: Wilsy OS Core Governance
EPITOME: Certifies the exact R10B2 registry API against deterministic,
         in-memory PyMongo-shaped spies without contacting Mongo or changing
         production behavior.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tests/unit/test_password_recovery_registry.py
COLLABORATION / OWNERSHIP: Tests
                            `tools/eos/saas/auth/password_recovery_registry.py`
                            and its certified R10B1 domain dependency only;
                            no service, router, client, or database runtime is
                            exercised here.
CERTIFICATION / UPDATE DATE: 2026-09-22
CHANGELOG: v1.0.0-R10B3-PASSWORD-RECOVERY-REGISTRY-CERT certifies collection identity, deterministic indexes,
           insert-only creation, tenant-scoped reads, domain hydration,
           lifecycle CAS predicates, replay classification, session
           forwarding, and forbidden-authority boundaries.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2; ISO 27001.
SECURITY / PRIVACY POSTURE: Only synthetic digests and opaque identifiers are
                            used. The fake rejects and records no raw token,
                            password, JWT, session bearer, refresh token, or
                            MFA secret.
TENANT BOUNDARY: Tests require exact tenant predicates for identity and digest
                 reads and ensure another tenant remains scoped absence.
AUTHORITY BOUNDARY: Unit evidence for registry behavior only; no real Mongo,
                    password mutation, token delivery, HTTP, MFA, JWT, or
                    session-revocation authority is certified.
DATABASE BOUNDARY: Deterministic in-memory spy only; canonical and disposable
                   Mongo are intentionally not contacted.
FINANCIAL AUTHORITY BOUNDARY: None; Kennel EOS remains the exclusive financial
                              execution and settlement authority.
FAIL-CLOSED POSTURE: Production errors, corruption, duplicate races, and
                     lifecycle conflicts must remain explicit failures.
"""
from __future__ import annotations

import ast
import hashlib
from copy import deepcopy
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any

import pytest
from pymongo.errors import DuplicateKeyError, PyMongoError

from tools.eos.saas.auth.password_recovery import (
    PasswordRecoveryCapability,
    PasswordRecoveryCapabilityStatus,
)
from tools.eos.saas.auth.password_recovery_registry import (
    COLLECTION,
    INDEX_DEFINITIONS,
    PasswordRecoveryCapabilityAlreadyExistsError,
    PasswordRecoveryCapabilityLifecycleConflictError,
    PasswordRecoveryCapabilityNotFoundError,
    PasswordRecoveryCapabilityPersistedRecordInvalidError,
    PasswordRecoveryCapabilityPersistenceError,
    PasswordRecoveryCapabilityRegistry,
    PasswordRecoveryCapabilityRegistryError,
)


BASE_TIME = datetime(2026, 9, 22, 10, 0, 0, 123456, tzinfo=timezone.utc)
EXPIRY_TIME = BASE_TIME + timedelta(hours=1)
_REGISTRY_PATH = Path(__file__).resolve().parents[2] / "tools/eos/saas/auth/password_recovery_registry.py"


class RecordingCollection:
    """Deterministic collection spy implementing only the registry boundary."""

    def __init__(self) -> None:
        self.rows: list[dict[str, Any]] = []
        self.index_calls: list[tuple[tuple[tuple[str, int], ...], dict[str, Any]]] = []
        self.calls: list[dict[str, Any]] = []
        self.force_cas_miss = False
        self.fail_transition = False
        self.fail_reads = False
        self.upsert_seen = False

    @staticmethod
    def _matches(row: dict[str, Any], query: dict[str, Any]) -> bool:
        for key, expected in query.items():
            actual = row.get(key)
            if isinstance(expected, dict):
                if "$gt" in expected and not (actual > expected["$gt"]):
                    return False
                if "$lte" in expected and not (actual <= expected["$lte"]):
                    return False
            elif actual != expected:
                return False
        return True

    def create_index(self, keys: list[tuple[str, int]], **options: Any) -> str:
        self.index_calls.append((tuple(keys), dict(options)))
        return str(options["name"])

    def insert_one(self, document: dict[str, Any], **options: Any) -> object:
        self.calls.append({"method": "insert_one", "document": deepcopy(document), "options": options})
        self.upsert_seen = self.upsert_seen or bool(options.get("upsert", False))
        if any(row["capability_id"] == document["capability_id"] for row in self.rows):
            raise DuplicateKeyError("synthetic capability identity collision")
        if any(row["token_digest"] == document["token_digest"] for row in self.rows):
            raise DuplicateKeyError("synthetic digest collision")
        self.rows.append(deepcopy(document))
        return object()

    def find_one(self, query: dict[str, Any], **options: Any) -> dict[str, Any] | None:
        self.calls.append({"method": "find_one", "query": deepcopy(query), "options": options})
        if self.fail_reads:
            raise PyMongoError("synthetic read failure")
        for row in self.rows:
            if self._matches(row, query):
                return deepcopy(row)
        return None

    def find_one_and_update(
        self,
        query: dict[str, Any],
        update: dict[str, Any],
        **options: Any,
    ) -> dict[str, Any] | None:
        self.calls.append(
            {
                "method": "find_one_and_update",
                "query": deepcopy(query),
                "update": deepcopy(update),
                "options": options,
            }
        )
        if self.fail_transition:
            raise PyMongoError("synthetic transition failure")
        if self.force_cas_miss:
            return None
        for index, row in enumerate(self.rows):
            if self._matches(row, query):
                next_row = deepcopy(row)
                next_row.update(update["$set"])
                self.rows[index] = next_row
                return deepcopy(next_row)
        return None


def _capability(
    capability_id: str,
    seed: str,
    *,
    tenant_id: str = "tenant-a",
    principal_id: str = "principal-a",
) -> PasswordRecoveryCapability:
    """Build deterministic synthetic R10B1 state without raw-token material."""

    return PasswordRecoveryCapability.issue(
        capability_id=capability_id,
        tenant_id=tenant_id,
        principal_id=principal_id,
        token_digest=hashlib.sha3_512(seed.encode("utf-8")).hexdigest(),
        issued_at=BASE_TIME,
        expires_at=EXPIRY_TIME,
    )


def _registry() -> tuple[PasswordRecoveryCapabilityRegistry, RecordingCollection, object]:
    collection = RecordingCollection()
    return PasswordRecoveryCapabilityRegistry(collection), collection, object()


def _last_call(collection: RecordingCollection, method: str) -> dict[str, Any]:
    return next(call for call in reversed(collection.calls) if call["method"] == method)


def _cas_call(collection: RecordingCollection) -> dict[str, Any]:
    return _last_call(collection, "find_one_and_update")


def test_collection_and_index_contract() -> None:
    registry, collection, _ = _registry()

    registry.ensure_indexes()

    assert COLLECTION == "password_recovery_capabilities"
    assert [options["name"] for _, options in collection.index_calls] == [
        "password_recovery_capability_identity_unique",
        "password_recovery_token_digest_unique",
        "password_recovery_tenant_principal_status_expiry",
    ]
    assert len(INDEX_DEFINITIONS) == 3
    assert collection.index_calls[0][1]["unique"] is True
    assert collection.index_calls[1][1]["unique"] is True
    assert collection.index_calls[2][1].get("unique", False) is False
    assert all("expireAfterSeconds" not in options for _, options in collection.index_calls)
    assert all("password_reset" not in str(keys).lower() for keys, _ in collection.index_calls)


def test_insert_only_creation_uses_domain_document_and_session() -> None:
    registry, collection, session = _registry()
    capability = _capability("cap-create", "synthetic-create")

    assert registry.create(capability, session=session) == capability

    inserted = _last_call(collection, "insert_one")
    document = inserted["document"]
    assert document["capability_id"] == capability.capability_id
    assert document["tenant_id"] == capability.tenant_id
    assert document["principal_id"] == capability.principal_id
    assert document["token_digest"] == capability.token_digest
    assert "raw_token" not in document and "token" not in document
    assert "password" not in document and "passwordHash" not in document
    assert inserted["options"]["session"] is session
    assert "upsert" not in inserted["options"]
    assert collection.upsert_seen is False


def test_terminal_creation_and_duplicate_identity_or_digest_fail_closed() -> None:
    registry, collection, session = _registry()
    first = _capability("cap-duplicate", "synthetic-duplicate")
    registry.create(first, session=session)

    with pytest.raises(PasswordRecoveryCapabilityAlreadyExistsError) as identity_error:
        registry.create(first, session=session)
    assert identity_error.value.code == "RECOVERY_CAPABILITY_ID_DUPLICATE"

    digest_collision = _capability("cap-other-id", "synthetic-duplicate")
    with pytest.raises(PasswordRecoveryCapabilityAlreadyExistsError) as digest_error:
        registry.create(digest_collision, session=session)
    assert digest_error.value.code == "RECOVERY_TOKEN_DIGEST_DUPLICATE"

    consumed = first.consume(BASE_TIME + timedelta(minutes=1))
    with pytest.raises(PasswordRecoveryCapabilityRegistryError) as terminal_error:
        registry.create(consumed, session=session)
    assert terminal_error.value.code == "RECOVERY_CREATE_REQUIRES_ACTIVE"
    assert len(collection.rows) == 1


def test_capability_and_digest_reads_are_exactly_tenant_scoped() -> None:
    registry, collection, session = _registry()
    capability = _capability("cap-tenant", "synthetic-tenant")
    registry.create(capability, session=session)
    collection.calls.clear()

    assert registry.get_by_capability_id(tenant_id="tenant-b", capability_id=capability.capability_id, session=session) is None
    capability_read = _last_call(collection, "find_one")
    assert capability_read["query"] == {"tenant_id": "tenant-b", "capability_id": capability.capability_id}
    assert capability_read["options"]["session"] is session

    assert registry.get_by_token_digest(tenant_id="tenant-b", token_digest=capability.token_digest, session=session) is None
    digest_read = _last_call(collection, "find_one")
    assert digest_read["query"] == {"tenant_id": "tenant-b", "token_digest": capability.token_digest}
    assert digest_read["options"]["session"] is session

    assert registry.get_by_capability_id(tenant_id="tenant-a", capability_id=capability.capability_id, session=session) == capability
    assert registry.get_by_token_digest(tenant_id="tenant-a", token_digest=capability.token_digest, session=session) == capability


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("token_digest", "malformed"),
        ("status", "UNSUPPORTED"),
        ("consumed_at", BASE_TIME.isoformat()),
        ("_expires_at_epoch_us", 1),
    ],
)
def test_corrupt_durable_state_is_not_repaired(field: str, value: Any) -> None:
    registry, collection, session = _registry()
    capability = _capability("cap-corrupt-" + field.replace("_", "-"), "synthetic-corrupt-" + field)
    registry.create(capability, session=session)
    collection.rows[0][field] = value

    with pytest.raises(PasswordRecoveryCapabilityPersistedRecordInvalidError) as error:
        registry.get_by_capability_id(tenant_id=capability.tenant_id, capability_id=capability.capability_id, session=session)
    assert error.value.code == "RECOVERY_PERSISTED_RECORD_INVALID"


def test_consume_cas_binds_identity_digest_active_state_and_expiry() -> None:
    registry, collection, session = _registry()
    capability = _capability("cap-consume", "synthetic-consume")
    registry.create(capability, session=session)
    collection.calls.clear()

    consumed_at = BASE_TIME + timedelta(minutes=5)
    result = registry.consume(capability, consumed_at, session=session)
    assert result.status is PasswordRecoveryCapabilityStatus.CONSUMED
    call = _cas_call(collection)
    query = call["query"]
    assert query["tenant_id"] == capability.tenant_id
    assert query["capability_id"] == capability.capability_id
    assert query["principal_id"] == capability.principal_id
    assert query["token_digest"] == capability.token_digest
    assert query["issued_at"] == capability.issued_at.isoformat()
    assert query["expires_at"] == capability.expires_at.isoformat()
    assert query["status"] == "ACTIVE"
    assert query["consumed_at"] is None and query["expired_at"] is None and query["revoked_at"] is None
    assert "$gt" in query["_expires_at_epoch_us"]
    assert call["update"] == {"$set": {"status": "CONSUMED", "consumed_at": consumed_at.isoformat()}}
    assert call["options"]["session"] is session
    assert "upsert" not in call["options"]

    with pytest.raises(PasswordRecoveryCapabilityLifecycleConflictError) as replay:
        registry.consume(capability, consumed_at + timedelta(minutes=1), session=session)
    assert replay.value.code == "RECOVERY_CAPABILITY_CONSUMED"


def test_revoke_cas_is_pre_expiry_and_terminal_state_safe() -> None:
    registry, collection, session = _registry()
    capability = _capability("cap-revoke", "synthetic-revoke")
    registry.create(capability, session=session)
    collection.calls.clear()
    revoked_at = BASE_TIME + timedelta(minutes=6)

    result = registry.revoke(capability, revoked_at, session=session)
    assert result.status is PasswordRecoveryCapabilityStatus.REVOKED
    call = _cas_call(collection)
    assert call["query"]["tenant_id"] == capability.tenant_id
    assert call["query"]["principal_id"] == capability.principal_id
    assert call["query"]["token_digest"] == capability.token_digest
    assert call["query"]["status"] == "ACTIVE"
    assert "$gt" in call["query"]["_expires_at_epoch_us"]
    assert call["update"] == {"$set": {"status": "REVOKED", "revoked_at": revoked_at.isoformat()}}
    assert call["options"]["session"] is session
    assert "upsert" not in call["options"]

    with pytest.raises(PasswordRecoveryCapabilityLifecycleConflictError) as replay:
        registry.revoke(capability, revoked_at + timedelta(minutes=1), session=session)
    assert replay.value.code == "RECOVERY_CAPABILITY_REVOKED"


def test_expire_cas_marks_state_without_deletion_or_ttl_inference() -> None:
    registry, collection, session = _registry()
    capability = _capability("cap-expire", "synthetic-expire")
    registry.create(capability, session=session)
    collection.calls.clear()

    result = registry.expire(capability, EXPIRY_TIME, session=session)
    assert result.status is PasswordRecoveryCapabilityStatus.EXPIRED
    assert len(collection.rows) == 1
    call = _cas_call(collection)
    assert call["query"]["status"] == "ACTIVE"
    assert "$lte" in call["query"]["_expires_at_epoch_us"]
    assert call["update"] == {"$set": {"status": "EXPIRED", "expired_at": EXPIRY_TIME.isoformat()}}
    assert call["options"]["session"] is session
    assert "upsert" not in call["options"]
    assert not any("expireAfterSeconds" in options for _, options in collection.index_calls)

    with pytest.raises(PasswordRecoveryCapabilityLifecycleConflictError) as replay:
        registry.expire(capability, EXPIRY_TIME + timedelta(minutes=1), session=session)
    assert replay.value.code == "RECOVERY_CAPABILITY_EXPIRED"


def test_cas_miss_classifies_scoped_absence_corruption_and_persistence_failure() -> None:
    registry, collection, session = _registry()
    absent = _capability("cap-absent", "synthetic-absent")
    with pytest.raises(PasswordRecoveryCapabilityNotFoundError) as absent_error:
        registry.consume(absent, BASE_TIME + timedelta(minutes=1), session=session)
    assert absent_error.value.code == "RECOVERY_CAPABILITY_NOT_FOUND"

    tenant_a = _capability("cap-cross-tenant", "synthetic-cross")
    registry.create(tenant_a, session=session)
    tenant_b = _capability("cap-cross-tenant", "synthetic-cross", tenant_id="tenant-b", principal_id="principal-b")
    with pytest.raises(PasswordRecoveryCapabilityNotFoundError):
        registry.consume(tenant_b, BASE_TIME + timedelta(minutes=1), session=session)

    corrupt = _capability("cap-cas-corrupt", "synthetic-cas-corrupt")
    registry.create(corrupt, session=session)
    collection.rows[-1]["status"] = "UNSUPPORTED"
    collection.force_cas_miss = True
    with pytest.raises(PasswordRecoveryCapabilityPersistedRecordInvalidError):
        registry.consume(corrupt, BASE_TIME + timedelta(minutes=2), session=session)

    failed = _capability("cap-persistence-failure", "synthetic-failure")
    collection.fail_transition = True
    with pytest.raises(PasswordRecoveryCapabilityPersistenceError) as persistence_error:
        registry.consume(failed, BASE_TIME + timedelta(minutes=2), session=session)
    assert persistence_error.value.code == "RECOVERY_TRANSITION_FAILED"


def test_registry_does_not_own_transactions_or_forbidden_authority() -> None:
    source = _REGISTRY_PATH.read_text(encoding="utf-8")
    tree = ast.parse(source)
    imported_modules = [node.module or "" for node in tree.body if isinstance(node, ast.ImportFrom)]
    forbidden_import_tokens = ("auth_registry", "jwt", "pyotp", "bcrypt", "smtplib", "twilio")
    assert not any(any(token in module for token in forbidden_import_tokens) for module in imported_modules)
    forbidden_source_tokens = (
        "MongoClient",
        "start_session",
        "commit_transaction",
        "abort_transaction",
        "send_email",
        "send_sms",
        "PasswordResetToken",
        "password_reset_tokens",
        "expireAfterSeconds",
        "datetime.now(",
        "datetime.utcnow(",
    )
    assert not any(token in source for token in forbidden_source_tokens)

    registry, collection, session = _registry()
    capability = _capability("cap-boundary", "synthetic-boundary")
    registry.create(capability, session=session)
    assert all(call["options"].get("session") is session for call in collection.calls)
    assert not any("upsert" in call["options"] for call in collection.calls)


# ARTIFACT: test_password_recovery_registry.py
# VERSION: v1.0.0-R10B3-PASSWORD-RECOVERY-REGISTRY-CERT
# AUTHORITY BOUNDARY: direct unit evidence for recovery-capability registry behavior only
# TENANT POSTURE: exact tenant-scoped fake reads and lifecycle predicates
# FAIL-CLOSED POSTURE: corruption, duplicate, replay, conflict, and persistence failure remain explicit
# FINANCIAL EXECUTION AUTHORITY: none; Kennel EOS remains exclusive
# END OF WILSY OS SOVEREIGN ARTIFACT
