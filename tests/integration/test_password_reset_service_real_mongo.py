"""Real-Mongo certificate for the WILSY OS password-reset transaction.

TITLE: WILSY OS Password Reset Service Real-Mongo Transaction Certificate
VERSION: v1.0.0-R10D3-PASSWORD-RESET-SERVICE-REAL-MONGO-CERT
AUTHORITY: Wilsy OS Core Governance
EPITOME: Certifies the already-frozen password-reset orchestration against a
         writable local MongoDB replica set using only disposable databases.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tests/integration/test_password_reset_service_real_mongo.py
COLLABORATION / OWNERSHIP: Tests only; R10D1 production orchestration and
                           R10D2 direct certificate remain read-only.
CERTIFICATION / UPDATE DATE: 2026-09-22
CHANGELOG: v1.0.0-R10D3 proves real commit, rollback after each participant,
           replay rejection, exact scope, shared sessions, and one-winner
           concurrent capability consumption.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2; ISO 27001.
SECURITY / PRIVACY POSTURE: Loopback-only synthetic identities and bearer
                            values are used. No secret or credential material
                            is printed or included in assertion messages.
TENANT BOUNDARY: Every fixture and assertion uses exact durable tenant and
                 principal predicates; cross-tenant state is control evidence.
AUTHORITY BOUNDARY: Real-Mongo reset transaction evidence only. No HTTP, JWT,
                    UI, TokenService, Node, delivery, MFA, or financial
                    authority is created.
FINANCIAL AUTHORITY BOUNDARY: None; Kennel EOS remains exclusive.
TRANSACTION BOUNDARY: The real PasswordResetService owns with_transaction;
                      child registries and AuthRegistry only participate.
FAIL-CLOSED POSTURE: Infrastructure failure fails the suite; no skip or xfail
                     converts unavailable Mongo into certification.
"""
from __future__ import annotations

import bcrypt
import hashlib
import os
import threading
import uuid
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from typing import Any, Iterator
from urllib.parse import urlparse

import pytest
from pymongo import MongoClient
from pymongo.read_concern import ReadConcern
from pymongo.write_concern import WriteConcern

from tools.eos.saas.auth import auth_registry as auth_registry_module
from tools.eos.saas.auth import password_recovery_registry as recovery_module
from tools.eos.saas.auth.auth_registry import AuthRegistry
from tools.eos.saas.auth.migrations.refresh_token_indexes import (
    IndexMode,
    reconcile_refresh_token_indexes,
)
from tools.eos.saas.auth.password_recovery import (
    PasswordRecoveryCapability,
    PasswordRecoveryCapabilityStatus,
)
from tools.eos.saas.auth.password_recovery_registry import (
    PasswordRecoveryCapabilityRegistry,
)
from tools.eos.saas.auth.password_reset_service import (
    PasswordResetResult,
    PasswordResetService,
    PasswordResetServiceError,
)
from tools.eos.saas.tenancy import tenant_registry as tenant_registry_module


VERSION = "v1.0.0-R10D3-PASSWORD-RESET-SERVICE-REAL-MONGO-CERT"
URI_ENV = "R10D3_PASSWORD_RESET_MONGO_URI"
FALLBACK_URI_ENV = "TEST_VENDOR_MONGO_URI"
DEFAULT_URI = "mongodb://127.0.0.1:27027/?replicaSet=wilsyVendorCertRS"
REPLICA_SET = "wilsyVendorCertRS"
DATABASE_PREFIX = "wilsy_r10d3_password_reset_"
BASE_TIME = datetime(2026, 9, 22, 12, 0, tzinfo=timezone.utc)
EXPIRY = BASE_TIME + timedelta(hours=1)
TENANT = "tenant-r10d3-primary"
OTHER_TENANT = "tenant-r10d3-other"
PRINCIPAL = "principal-r10d3-primary"
OTHER_PRINCIPAL = "principal-r10d3-other"
STARTING_REVISION = 7
OLD_PASSWORD = "old-password-r10d3-synthetic"
NEW_PASSWORD = "new-password-r10d3-synthetic"
RECOVERY_TOKEN = "recovery-token-r10d3-synthetic"


class AllowChecker:
    """Offline deterministic password intelligence capability."""

    def is_blocked(self, candidate: str) -> bool:
        """Allow only the synthetic certificate candidate."""

        return False


class DelegatingRecoveryRegistry:
    """Record session forwarding while delegating every operation to Mongo."""

    def __init__(self, delegate: PasswordRecoveryCapabilityRegistry) -> None:
        self.delegate = delegate
        self.transactional_session_ids: list[int] = []
        self.transition_before_transactional_read = False
        self.transition_done = False
        self.fail_after_consume = False

    def get_by_token_digest(
        self, *, tenant_id: str, token_digest: str, session: Any | None = None
    ) -> PasswordRecoveryCapability | None:
        """Delegate exact digest lookup and record only opaque session identity."""

        if session is not None:
            self.transactional_session_ids.append(id(session))
        result = self.delegate.get_by_token_digest(
            tenant_id=tenant_id, token_digest=token_digest, session=session
        )
        if session is None and self.transition_before_transactional_read and not self.transition_done:
            assert result is not None
            self.delegate.revoke(result, BASE_TIME)
            self.transition_done = True
        return result

    def consume(
        self,
        capability: PasswordRecoveryCapability,
        consumed_at: datetime,
        *,
        session: Any | None = None,
    ) -> PasswordRecoveryCapability:
        """Delegate the real lifecycle CAS, optionally fail after it."""

        assert session is not None
        self.transactional_session_ids.append(id(session))
        result = self.delegate.consume(capability, consumed_at, session=session)
        if self.fail_after_consume:
            raise RuntimeError("synthetic post-consume failure")
        return result


class DelegatingAuthRegistry:
    """Record transaction sessions while delegating credential persistence."""

    def __init__(self, delegate: AuthRegistry) -> None:
        self.delegate = delegate
        self.transactional_session_ids: list[int] = []
        self.fail_after_cas = False
        self.fail_after_sessions = False
        self.fail_after_refresh = False

    def hash_password(self, password: str) -> str:
        """Use the canonical bcrypt authority without retaining the value."""

        return self.delegate.hash_password(password)

    def get_credential_revision(self, tenant_id: str, user_id: str, *, session: Any = None) -> int:
        """Delegate exact revision read and record the caller session."""

        assert session is not None
        self.transactional_session_ids.append(id(session))
        return self.delegate.get_credential_revision(tenant_id, user_id, session=session)

    def compare_and_swap_password_hash(
        self,
        tenant_id: str,
        user_id: str,
        expected_credential_revision: int,
        new_password_hash: str,
        *,
        session: Any = None,
    ) -> int:
        """Delegate the real atomic CAS, optionally fail after the write."""

        assert session is not None
        self.transactional_session_ids.append(id(session))
        result = self.delegate.compare_and_swap_password_hash(
            tenant_id,
            user_id,
            expected_credential_revision,
            new_password_hash,
            session=session,
        )
        if self.fail_after_cas:
            raise RuntimeError("synthetic post-CAS failure")
        return result

    def revoke_sessions(self, tenant_id: str, user_id: str, *, session: Any = None) -> int:
        """Delegate real exact session deletion, optionally fail afterward."""

        assert session is not None
        self.transactional_session_ids.append(id(session))
        result = self.delegate.revoke_sessions(tenant_id, user_id, session=session)
        if self.fail_after_sessions:
            raise RuntimeError("synthetic post-session failure")
        return result

    def revoke_refresh_tokens(self, tenant_id: str, user_id: str, *, session: Any = None) -> int:
        """Delegate real exact refresh deletion, optionally fail afterward."""

        assert session is not None
        self.transactional_session_ids.append(id(session))
        result = self.delegate.revoke_refresh_tokens(tenant_id, user_id, session=session)
        if self.fail_after_refresh:
            raise RuntimeError("synthetic post-refresh failure")
        return result


@dataclass(frozen=True)
class Fixture:
    """Opaque identifiers and durable fixture metadata for one test database."""

    tenant_id: str
    other_tenant_id: str
    principal_id: str
    other_principal_id: str
    token: str
    token_digest: str
    capability_id: str
    old_password_hash: str
    starting_revision: int


class MongoContext:
    """Own one isolated database and its real persistence collections."""

    def __init__(self, client: MongoClient[Any], database_name: str) -> None:
        self.client = client
        self.database_name = database_name
        self.database = client.get_database(
            database_name,
            read_concern=ReadConcern("majority"),
            write_concern=WriteConcern(w="majority", j=True),
        )
        self.users = self.database["users"]
        self.tenants = self.database["tenants"]
        self.sessions = self.database["sessions"]
        self.refresh_tokens = self.database["refresh_tokens"]
        self.capabilities = self.database[recovery_module.COLLECTION]


def _runtime_uri() -> str:
    """Resolve only a loopback disposable URI and reject canonical databases."""

    value = os.environ.get(URI_ENV) or os.environ.get(FALLBACK_URI_ENV) or DEFAULT_URI
    parsed = urlparse(value)
    if parsed.scheme != "mongodb" or parsed.hostname not in {"127.0.0.1", "localhost", "::1"}:
        raise RuntimeError("R10D3 requires a loopback mongodb URI")
    if parsed.path.strip("/") in {"wilsy", "wilsy/"} or "mongodb.net" in value.lower():
        raise RuntimeError("R10D3 rejects canonical or hosted Mongo")
    return value


def _open_runtime() -> MongoClient[Any]:
    """Connect to and verify the established writable Mongo replica set."""

    client: MongoClient[Any] = MongoClient(
        _runtime_uri(),
        replicaSet=REPLICA_SET,
        serverSelectionTimeoutMS=5000,
        connectTimeoutMS=5000,
        socketTimeoutMS=10000,
        retryWrites=True,
    )
    try:
        hello = client.admin.command("hello")
        if hello.get("setName") != REPLICA_SET or hello.get("isWritablePrimary") is not True:
            raise RuntimeError("R10D3 requires a writable replica-set primary")
        if hello.get("primary") != "127.0.0.1:27027":
            raise RuntimeError("R10D3 primary identity is not established")
        if client.address != ("127.0.0.1", 27027):
            raise RuntimeError("R10D3 connected address is not loopback port 27027")
        if not str(client.server_info().get("version", "")).startswith("7."):
            raise RuntimeError("R10D3 requires MongoDB 7.x")
        return client
    except BaseException:
        client.close()
        raise


@pytest.fixture(scope="module")
def mongo_client() -> Iterator[MongoClient[Any]]:
    """Use the established mongod without starting or stopping it."""

    client = _open_runtime()
    try:
        yield client
    finally:
        client.close()


@pytest.fixture()
def mongo_context(mongo_client: MongoClient[Any]) -> Iterator[MongoContext]:
    """Create and drop exactly one UUID-scoped disposable database."""

    context = MongoContext(mongo_client, DATABASE_PREFIX + uuid.uuid4().hex)
    assert context.database_name != "wilsy"
    try:
        yield context
    finally:
        mongo_client.drop_database(context.database_name)
        assert context.database_name not in mongo_client.list_database_names()


@pytest.fixture()
def bound_database(monkeypatch: pytest.MonkeyPatch, mongo_context: MongoContext) -> MongoContext:
    """Bind canonical Python collection resolution to this disposable database."""

    monkeypatch.setattr(auth_registry_module.kernel_db, "get_database", lambda: mongo_context.database)
    monkeypatch.setattr(tenant_registry_module.kernel_db, "get_database", lambda: mongo_context.database)
    monkeypatch.setattr(tenant_registry_module, "tenants_collection", mongo_context.tenants)
    return mongo_context


def _tenant_document(tenant_id: str) -> dict[str, Any]:
    """Build the minimum valid active tenant projection."""

    return {
        "tenant_id": tenant_id,
        "name": "Synthetic certification tenant",
        "industry": "Certification",
        "subscription": {"plan": "BASIC"},
        "status": "ACTIVE",
        "created_at": BASE_TIME.isoformat(),
    }


def _user_document(
    *, tenant_id: str, user_id: str, password_hash: str, revision: int
) -> dict[str, Any]:
    """Build one durable user with non-password authority controls."""

    return {
        "user_id": user_id,
        "email": f"{user_id}@example.com",
        "firstName": "Synthetic",
        "lastName": "Principal",
        "role": "USER",
        "permissions": ["legal:read"],
        "tenantId": tenant_id,
        "passwordHash": password_hash,
        "credential_revision": revision,
        "mfaRegistered": True,
        "hasSignedCovenant": True,
        "createdAt": BASE_TIME,
        "updatedAt": BASE_TIME,
    }


def _seed(context: MongoContext, suffix: str) -> Fixture:
    """Seed principal/control rows and one active real capability."""

    auth = AuthRegistry()
    old_hash = auth.hash_password(OLD_PASSWORD)
    context.tenants.insert_many([_tenant_document(TENANT), _tenant_document(OTHER_TENANT)])
    context.users.insert_many(
        [
            _user_document(
                tenant_id=TENANT,
                user_id=PRINCIPAL,
                password_hash=old_hash,
                revision=STARTING_REVISION,
            ),
            _user_document(
                tenant_id=OTHER_TENANT,
                user_id=OTHER_PRINCIPAL,
                password_hash=auth.hash_password("other-password-r10d3-synthetic"),
                revision=3,
            ),
        ]
    )
    context.sessions.insert_many(
        [
            {"user_id": PRINCIPAL, "tenant_id": TENANT, "token": f"session-a-{suffix}", "expires_at": EXPIRY},
            {"user_id": PRINCIPAL, "tenant_id": TENANT, "token": f"session-b-{suffix}", "expires_at": EXPIRY},
            {"user_id": OTHER_PRINCIPAL, "tenant_id": OTHER_TENANT, "token": f"session-other-{suffix}", "expires_at": EXPIRY},
        ]
    )
    context.refresh_tokens.insert_many(
        [
            {"user_id": PRINCIPAL, "tenant_id": TENANT, "token": f"refresh-a-{suffix}", "expires": EXPIRY},
            {"user_id": PRINCIPAL, "tenant_id": TENANT, "token": f"refresh-b-{suffix}", "expires": EXPIRY},
            {"user_id": OTHER_PRINCIPAL, "tenant_id": OTHER_TENANT, "token": f"refresh-other-{suffix}", "expires": EXPIRY},
        ]
    )
    recovery = PasswordRecoveryCapabilityRegistry(context.capabilities)
    capability_id = f"capability-r10d3-{suffix}"
    token = f"recovery-r10d3-{suffix}"
    token_digest = hashlib.sha3_512(token.encode("utf-8")).hexdigest()
    capability = PasswordRecoveryCapability.issue(
        capability_id=capability_id,
        tenant_id=TENANT,
        principal_id=PRINCIPAL,
        token_digest=token_digest,
        issued_at=BASE_TIME - timedelta(minutes=5),
        expires_at=EXPIRY,
    )
    recovery.create(capability)
    return Fixture(
        tenant_id=TENANT,
        other_tenant_id=OTHER_TENANT,
        principal_id=PRINCIPAL,
        other_principal_id=OTHER_PRINCIPAL,
        token=token,
        token_digest=token_digest,
        capability_id=capability_id,
        old_password_hash=old_hash,
        starting_revision=STARTING_REVISION,
    )


def _prepare(context: MongoContext) -> None:
    """Establish certified recovery and tenant-bearing refresh indexes."""

    PasswordRecoveryCapabilityRegistry(context.capabilities).ensure_indexes()
    report = reconcile_refresh_token_indexes(
        refresh_tokens=context.refresh_tokens, mode=IndexMode.APPLY
    )
    assert report.state in {"APPLY_VERIFIED", "APPLY_ALREADY_SATISFIED"}


def _service(
    context: MongoContext,
    *,
    recovery: DelegatingRecoveryRegistry | None = None,
    auth: DelegatingAuthRegistry | None = None,
    client: MongoClient[Any] | None = None,
) -> PasswordResetService:
    """Compose the real service with optional delegating failure spies."""

    return PasswordResetService(
        client=client or context.client,
        recovery_registry=recovery or PasswordRecoveryCapabilityRegistry(context.capabilities),
        auth_registry=auth or AuthRegistry(),
        blocklist_checker=AllowChecker(),
        clock=lambda: BASE_TIME,
    )


def _read_user(context: MongoContext, user_id: str, tenant_id: str) -> dict[str, Any]:
    """Read one exact durable identity without exposing it in diagnostics."""

    row = context.users.find_one({"user_id": user_id, "tenantId": tenant_id})
    assert row is not None
    return row


def _assert_rollback(context: MongoContext, fixture: Fixture) -> None:
    """Prove every durable participant returned to the pre-reset state."""

    row = _read_user(context, fixture.principal_id, fixture.tenant_id)
    assert row["credential_revision"] == fixture.starting_revision
    assert bcrypt.checkpw(OLD_PASSWORD.encode(), row["passwordHash"].encode())
    assert context.sessions.count_documents({"tenant_id": fixture.tenant_id, "user_id": fixture.principal_id}) == 2
    assert context.refresh_tokens.count_documents({"tenant_id": fixture.tenant_id, "user_id": fixture.principal_id}) == 2
    capability = context.capabilities.find_one({"capability_id": fixture.capability_id})
    assert capability is not None
    assert capability["status"] == PasswordRecoveryCapabilityStatus.ACTIVE.value


def test_runtime_transaction_smoke_and_certified_indexes(bound_database: MongoContext) -> None:
    """Prove the real runtime and actual index authorities before reset cases."""

    _prepare(bound_database)
    probe = bound_database.database["transaction_probe"]
    with bound_database.client.start_session() as session:
        def callback(tx_session: Any) -> None:
            probe.insert_one({"probe": "opaque"}, session=tx_session)
            assert probe.find_one({"probe": "opaque"}, session=tx_session) is not None

        session.with_transaction(callback)
    assert probe.find_one({"probe": "opaque"}) is not None
    index_names = {item["name"] for item in bound_database.refresh_tokens.list_indexes()}
    assert {"_id_", "refresh_token_token_unique", "refresh_token_tenant_user_lookup"} <= index_names


def test_successful_commit_verifies_password_revision_scope_and_consumption(
    bound_database: MongoContext,
) -> None:
    """Prove one real reset commits every participant atomically."""

    _prepare(bound_database)
    fixture = _seed(bound_database, "commit")
    result = _service(bound_database).reset_password(
        tenant_id=fixture.tenant_id,
        recovery_token=fixture.token,
        new_password=NEW_PASSWORD,
    )
    assert isinstance(result, PasswordResetResult)
    user = _read_user(bound_database, fixture.principal_id, fixture.tenant_id)
    assert user["credential_revision"] == fixture.starting_revision + 1
    assert bcrypt.checkpw(NEW_PASSWORD.encode(), user["passwordHash"].encode())
    assert not bcrypt.checkpw(OLD_PASSWORD.encode(), user["passwordHash"].encode())
    assert bound_database.sessions.count_documents({"tenant_id": fixture.tenant_id, "user_id": fixture.principal_id}) == 0
    assert bound_database.refresh_tokens.count_documents({"tenant_id": fixture.tenant_id, "user_id": fixture.principal_id}) == 0
    capability = bound_database.capabilities.find_one({"capability_id": fixture.capability_id})
    assert capability is not None
    assert capability["status"] == PasswordRecoveryCapabilityStatus.CONSUMED.value


def test_one_real_session_reaches_all_mutations_and_non_password_authority_is_preserved(
    bound_database: MongoContext,
) -> None:
    """Prove session identity forwarding and unchanged durable authority fields."""

    _prepare(bound_database)
    fixture = _seed(bound_database, "session")
    before = _read_user(bound_database, fixture.principal_id, fixture.tenant_id)
    recovery = DelegatingRecoveryRegistry(PasswordRecoveryCapabilityRegistry(bound_database.capabilities))
    auth = DelegatingAuthRegistry(AuthRegistry())
    _service(bound_database, recovery=recovery, auth=auth).reset_password(
        tenant_id=fixture.tenant_id, recovery_token=fixture.token, new_password=NEW_PASSWORD
    )
    session_ids = set(recovery.transactional_session_ids + auth.transactional_session_ids)
    assert len(session_ids) == 1
    after = _read_user(bound_database, fixture.principal_id, fixture.tenant_id)
    for field in ("mfaRegistered", "hasSignedCovenant", "role", "permissions", "tenantId", "user_id"):
        assert after[field] == before[field]
    assert bound_database.sessions.count_documents({"tenant_id": fixture.other_tenant_id}) == 1
    assert bound_database.refresh_tokens.count_documents({"tenant_id": fixture.other_tenant_id}) == 1


def test_committed_replay_cannot_mutate_again(bound_database: MongoContext) -> None:
    """Prove a consumed capability rejects replay without a second transaction."""

    _prepare(bound_database)
    fixture = _seed(bound_database, "replay")
    service = _service(bound_database)
    service.reset_password(tenant_id=fixture.tenant_id, recovery_token=fixture.token, new_password=NEW_PASSWORD)
    before = _read_user(bound_database, fixture.principal_id, fixture.tenant_id)
    with pytest.raises(PasswordResetServiceError):
        service.reset_password(tenant_id=fixture.tenant_id, recovery_token=fixture.token, new_password=NEW_PASSWORD)
    after = _read_user(bound_database, fixture.principal_id, fixture.tenant_id)
    assert after["credential_revision"] == before["credential_revision"] == fixture.starting_revision + 1
    assert bound_database.sessions.count_documents({"tenant_id": fixture.tenant_id, "user_id": fixture.principal_id}) == 0
    assert bound_database.refresh_tokens.count_documents({"tenant_id": fixture.tenant_id, "user_id": fixture.principal_id}) == 0


@pytest.mark.parametrize("failure", ("cas", "sessions", "refresh", "consume"))
def test_each_post_write_failure_rolls_back_all_real_participants(
    bound_database: MongoContext, failure: str
) -> None:
    """Prove abort restores state after each real participant has written."""

    _prepare(bound_database)
    fixture = _seed(bound_database, f"rollback-{failure}")
    recovery = DelegatingRecoveryRegistry(PasswordRecoveryCapabilityRegistry(bound_database.capabilities))
    auth = DelegatingAuthRegistry(AuthRegistry())
    if failure == "cas":
        auth.fail_after_cas = True
    elif failure == "sessions":
        auth.fail_after_sessions = True
    elif failure == "refresh":
        auth.fail_after_refresh = True
    else:
        recovery.fail_after_consume = True
    with pytest.raises(PasswordResetServiceError):
        _service(bound_database, recovery=recovery, auth=auth).reset_password(
            tenant_id=fixture.tenant_id, recovery_token=fixture.token, new_password=NEW_PASSWORD
        )
    _assert_rollback(bound_database, fixture)


def test_transactional_reread_rejects_state_changed_after_preflight(
    bound_database: MongoContext,
) -> None:
    """Prove the real transactional capability reread outranks preflight."""

    _prepare(bound_database)
    fixture = _seed(bound_database, "reread")
    recovery = DelegatingRecoveryRegistry(PasswordRecoveryCapabilityRegistry(bound_database.capabilities))
    recovery.transition_before_transactional_read = True
    with pytest.raises(PasswordResetServiceError):
        _service(bound_database, recovery=recovery).reset_password(
            tenant_id=fixture.tenant_id, recovery_token=fixture.token, new_password=NEW_PASSWORD
        )
    user = _read_user(bound_database, fixture.principal_id, fixture.tenant_id)
    assert user["credential_revision"] == fixture.starting_revision
    assert bound_database.sessions.count_documents({"tenant_id": fixture.tenant_id, "user_id": fixture.principal_id}) == 2
    assert bound_database.refresh_tokens.count_documents({"tenant_id": fixture.tenant_id, "user_id": fixture.principal_id}) == 2
    capability = bound_database.capabilities.find_one({"capability_id": fixture.capability_id})
    assert capability is not None
    assert capability["status"] == PasswordRecoveryCapabilityStatus.REVOKED.value


def test_wrong_tenant_selector_cannot_use_real_capability(bound_database: MongoContext) -> None:
    """Prove recovery authority is exact tenant-bound and cannot be redirected."""

    _prepare(bound_database)
    fixture = _seed(bound_database, "tenant")
    with pytest.raises(PasswordResetServiceError):
        _service(bound_database).reset_password(
            tenant_id=fixture.other_tenant_id, recovery_token=fixture.token, new_password=NEW_PASSWORD
        )
    user = _read_user(bound_database, fixture.principal_id, fixture.tenant_id)
    assert user["credential_revision"] == fixture.starting_revision
    assert bound_database.sessions.count_documents({"tenant_id": fixture.tenant_id, "user_id": fixture.principal_id}) == 2


def test_concurrent_double_use_has_one_durable_winner(bound_database: MongoContext) -> None:
    """Prove two independent real transactions produce one committed reset."""

    _prepare(bound_database)
    fixture = _seed(bound_database, "concurrent")
    barrier = threading.Barrier(2)

    def attempt() -> bool:
        service = _service(bound_database, client=bound_database.client)
        barrier.wait(timeout=10)
        try:
            return isinstance(
                service.reset_password(
                    tenant_id=fixture.tenant_id,
                    recovery_token=fixture.token,
                    new_password=NEW_PASSWORD,
                ),
                PasswordResetResult,
            )
        except PasswordResetServiceError:
            return False

    with ThreadPoolExecutor(max_workers=2) as executor:
        outcomes = list(executor.map(lambda _: attempt(), (1, 2)))
    assert sum(outcomes) == 1
    user = _read_user(bound_database, fixture.principal_id, fixture.tenant_id)
    assert user["credential_revision"] == fixture.starting_revision + 1
    assert bound_database.sessions.count_documents({"tenant_id": fixture.tenant_id, "user_id": fixture.principal_id}) == 0
    assert bound_database.refresh_tokens.count_documents({"tenant_id": fixture.tenant_id, "user_id": fixture.principal_id}) == 0
    capability = bound_database.capabilities.find_one({"capability_id": fixture.capability_id})
    assert capability is not None
    assert capability["status"] == PasswordRecoveryCapabilityStatus.CONSUMED.value


# ARTIFACT: test_password_reset_service_real_mongo.py
# VERSION: v1.0.0-R10D3-PASSWORD-RESET-SERVICE-REAL-MONGO-CERT
# AUTHORITY BOUNDARY: disposable real-Mongo transaction evidence only
# TENANT POSTURE: exact durable tenant/principal scope; cross-tenant controls preserved
# FAIL-CLOSED POSTURE: unavailable Mongo fails; no skip or xfail posture
# FINANCIAL EXECUTION AUTHORITY: none; Kennel EOS remains exclusive
# END OF WILSY OS SOVEREIGN ARTIFACT
