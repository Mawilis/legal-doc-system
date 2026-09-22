"""Real-Mongo certificate for the WILSY OS password-recovery engine.

TITLE: WILSY OS Password Recovery Engine Real-Mongo Certificate
VERSION: v1.0.1-R10E46-PASSWORD-RECOVERY-ENGINE-REAL-MONGO-TYPE-CLOSURE
AUTHORITY: Wilsy OS Core Governance
EPITOME: Certifies verified recovery-contact persistence, email-control
         verification lifecycle, atomic contact enrollment, replay rejection,
         tenant isolation, and namespaced request throttling against a writable
         disposable MongoDB replica set.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tests/integration/test_password_recovery_engine_real_mongo.py
COLLABORATION / OWNERSHIP: Exercises R10E1/R10E15 domains, R10E16/R10E19
                           registries, R10E18 rate gate, R10E21 completion
                           transaction, and canonical AuthRegistry reads only.
CERTIFICATION / UPDATE DATE: 2026-09-22
CHANGELOG: v1.0.1-R10E46-PASSWORD-RECOVERY-ENGINE-REAL-MONGO-TYPE-CLOSURE introduces
           loopback-only replica-set evidence for real indexes, digest-only
           durability, single-ACTIVE contact authority, exact tenant isolation,
           transaction-scoped verification completion, changed-contact
           replacement, email-drift rollback, replay rejection, real namespaced
           rate counters, and disposable-database cleanup.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2; ISO 27001.
SECURITY / PRIVACY POSTURE: Synthetic addresses/tokens only; durable assertions
                            prove raw email and raw capability absence from R10E
                            contact/verification/rate collections.
TENANT BOUNDARY: Every registry and completion operation uses exact synthetic
                 tenant/principal bindings; cross-tenant reads return absence.
AUTHORITY BOUNDARY: Disposable real-Mongo recovery evidence only; no SMTP,
                    HTTP, browser, password reset, session, JWT, MFA, Node, or
                    financial authority is created.
FINANCIAL AUTHORITY BOUNDARY: None; Kennel EOS remains exclusive.
TRANSACTION BOUNDARY: R10E21 owns with_transaction; child registries receive
                      only the caller-owned real ClientSession.
FAIL-CLOSED POSTURE: Unavailable/non-loopback/non-primary Mongo fails the suite;
                     no skip/xfail converts missing infrastructure into PASS.
"""

from __future__ import annotations

import hashlib
import os
import uuid
from datetime import datetime, timedelta, timezone
from typing import Any, Iterator
from urllib.parse import urlparse

import pytest
from pymongo import MongoClient
from pymongo.read_concern import ReadConcern
from pymongo.write_concern import WriteConcern

from tools.eos.saas.auth import auth_registry as auth_registry_module
from tools.eos.saas.auth.auth_registry import AuthRegistry
from tools.eos.saas.auth.password_recovery_contact import (
    VerifiedRecoveryContact,
    VerifiedRecoveryContactChannel,
    VerifiedRecoveryContactStatus,
)
from tools.eos.saas.auth.password_recovery_contact_registry import (
    COLLECTION as CONTACT_COLLECTION,
    VerifiedRecoveryContactRegistry,
)
from tools.eos.saas.auth.password_recovery_contact_verification import (
    RecoveryContactVerification,
    RecoveryContactVerificationStatus,
)
from tools.eos.saas.auth.password_recovery_contact_verification_registry import (
    COLLECTION as VERIFICATION_COLLECTION,
    RecoveryContactVerificationRegistry,
)
from tools.eos.saas.auth.password_recovery_contact_verification_service import (
    RecoveryContactVerificationCode,
    RecoveryContactVerificationService,
    RecoveryContactVerificationServiceError,
)
from tools.eos.saas.auth.password_recovery_rate_limit import (
    COLLECTION as RATE_COLLECTION,
    PasswordRecoveryRateLimit,
)
from tools.eos.saas.auth.password_recovery_request_service import (
    PasswordRecoveryRequestRateLimitedError,
    recovery_address_digest,
)
from tools.eos.saas.tenancy import tenant_registry as tenant_registry_module

VERSION = "v1.0.1-R10E46-PASSWORD-RECOVERY-ENGINE-REAL-MONGO-TYPE-CLOSURE"
URI_ENV = "R10E35_PASSWORD_RECOVERY_MONGO_URI"
FALLBACK_URI_ENV = "TEST_VENDOR_MONGO_URI"
DEFAULT_URI = "mongodb://127.0.0.1:27027/?replicaSet=wilsyVendorCertRS"
REPLICA_SET = "wilsyVendorCertRS"
DATABASE_PREFIX = "wilsy_r10e35_recovery_"

BASE_TIME = datetime(2026, 9, 22, 18, 0, tzinfo=timezone.utc)
TENANT = "tenant-r10e35-primary"
OTHER_TENANT = "tenant-r10e35-other"
PRINCIPAL = "principal-r10e35-primary"
OTHER_PRINCIPAL = "principal-r10e35-other"
EMAIL = "verified.r10e35@example.com"
OTHER_EMAIL = "other.r10e35@example.com"
RAW_VERIFICATION_TOKEN = "r10e35-verification-token-synthetic"
TOKEN_DIGEST = hashlib.sha3_512(RAW_VERIFICATION_TOKEN.encode("utf-8")).hexdigest()
ADDRESS_DIGEST = recovery_address_digest(EMAIL)


class MongoContext:
    """Own one UUID-scoped disposable database and R10E collections."""

    def __init__(self, client: MongoClient[Any], database_name: str) -> None:
        self.client = client
        self.database_name = database_name
        self.database = client.get_database(
            database_name,
            read_concern=ReadConcern("majority"),
            write_concern=WriteConcern(w="majority", j=True),
        )
        self.tenants = self.database["tenants"]
        self.users = self.database["users"]
        self.contacts = self.database[CONTACT_COLLECTION]
        self.verifications = self.database[VERIFICATION_COLLECTION]
        self.rate_limits = self.database[RATE_COLLECTION]


def _runtime_uri() -> str:
    """Resolve only a loopback disposable certification URI."""

    value = os.environ.get(URI_ENV) or os.environ.get(FALLBACK_URI_ENV) or DEFAULT_URI
    parsed = urlparse(value)
    if parsed.scheme != "mongodb":
        raise RuntimeError("R10E35 requires mongodb:// URI")
    if parsed.hostname not in {"127.0.0.1", "localhost", "::1"}:
        raise RuntimeError("R10E35 requires loopback Mongo")
    if "mongodb.net" in value.lower() or "atlas" in value.lower():
        raise RuntimeError("R10E35 rejects hosted Mongo")
    if parsed.path.strip("/") == "wilsy":
        raise RuntimeError("R10E35 rejects canonical database")
    return value


def _open_runtime() -> MongoClient[Any]:
    """Require a writable MongoDB 7.x replica-set primary."""

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
        if hello.get("setName") != REPLICA_SET:
            raise RuntimeError("R10E35 replica-set identity mismatch")
        if hello.get("isWritablePrimary") is not True:
            raise RuntimeError("R10E35 requires writable primary")
        address = client.address
        if address is None or address[0] not in {"127.0.0.1", "localhost"}:
            raise RuntimeError("R10E35 runtime is not loopback")
        if not str(client.server_info().get("version", "")).startswith("7."):
            raise RuntimeError("R10E35 requires MongoDB 7.x")
        return client
    except BaseException:
        client.close()
        raise


@pytest.fixture(scope="module")
def mongo_client() -> Iterator[MongoClient[Any]]:
    client = _open_runtime()
    try:
        yield client
    finally:
        client.close()


@pytest.fixture()
def context(mongo_client: MongoClient[Any]) -> Iterator[MongoContext]:
    database_name = DATABASE_PREFIX + uuid.uuid4().hex
    if database_name == "wilsy":
        raise RuntimeError("R10E35 disposable database guard failed")
    ctx = MongoContext(mongo_client, database_name)
    try:
        yield ctx
    finally:
        mongo_client.drop_database(database_name)
        assert database_name not in mongo_client.list_database_names()


@pytest.fixture()
def bound_context(monkeypatch: pytest.MonkeyPatch, context: MongoContext) -> MongoContext:
    """Bind canonical AuthRegistry/TenantRegistry reads to the disposable DB."""

    monkeypatch.setattr(auth_registry_module.kernel_db, "get_database", lambda: context.database)
    monkeypatch.setattr(tenant_registry_module.kernel_db, "get_database", lambda: context.database)
    monkeypatch.setattr(tenant_registry_module, "tenants_collection", context.tenants)
    return context


def _tenant_document(tenant_id: str) -> dict[str, Any]:
    return {
        "tenant_id": tenant_id,
        "name": f"Synthetic {tenant_id}",
        "industry": "Certification",
        "subscription": {"plan": "BASIC"},
        "status": "ACTIVE",
        "created_at": BASE_TIME.isoformat(),
    }


def _user_document(
    *,
    tenant_id: str,
    user_id: str,
    email: str,
    revision: int = 3,
) -> dict[str, Any]:
    return {
        "user_id": user_id,
        "email": email,
        "firstName": "Synthetic",
        "lastName": "Recovery",
        "role": "USER",
        "permissions": [],
        "tenantId": tenant_id,
        "passwordHash": "$2b$12$abcdefghijklmnopqrstuv123456789012345678901234567890",
        "credential_revision": revision,
        "mfaRegistered": True,
        "hasSignedCovenant": True,
        "createdAt": BASE_TIME,
        "updatedAt": BASE_TIME,
    }


def _prepare(ctx: MongoContext) -> None:
    VerifiedRecoveryContactRegistry(ctx.contacts).ensure_indexes()
    RecoveryContactVerificationRegistry(ctx.verifications).ensure_indexes()
    PasswordRecoveryRateLimit(ctx.rate_limits).ensure_indexes()


def _seed_authority(ctx: MongoContext) -> None:
    ctx.tenants.insert_many([
        _tenant_document(TENANT),
        _tenant_document(OTHER_TENANT),
    ])
    ctx.users.insert_many([
        _user_document(tenant_id=TENANT, user_id=PRINCIPAL, email=EMAIL),
        _user_document(
            tenant_id=OTHER_TENANT,
            user_id=OTHER_PRINCIPAL,
            email=OTHER_EMAIL,
        ),
    ])


def _verification(
    *,
    verification_id: str = "WILSYVERIFY-R10E35",
    tenant_id: str = TENANT,
    principal_id: str = PRINCIPAL,
    address_digest: str = ADDRESS_DIGEST,
    token_digest: str = TOKEN_DIGEST,
) -> RecoveryContactVerification:
    return RecoveryContactVerification.issue(
        verification_id=verification_id,
        tenant_id=tenant_id,
        principal_id=principal_id,
        address_digest=address_digest,
        token_digest=token_digest,
        issued_at=BASE_TIME - timedelta(minutes=5),
        expires_at=BASE_TIME + timedelta(minutes=25),
    )


def _contact(
    *,
    contact_id: str,
    digest: str = ADDRESS_DIGEST,
    verified_at: datetime = BASE_TIME - timedelta(days=1),
) -> VerifiedRecoveryContact:
    return VerifiedRecoveryContact.issue(
        contact_id=contact_id,
        tenant_id=TENANT,
        principal_id=PRINCIPAL,
        channel=VerifiedRecoveryContactChannel.EMAIL,
        address_digest=digest,
        verified_at=verified_at,
    )


def _service(ctx: MongoContext) -> RecoveryContactVerificationService:
    return RecoveryContactVerificationService(
        client=ctx.client,
        verification_registry=RecoveryContactVerificationRegistry(ctx.verifications),
        contact_registry=VerifiedRecoveryContactRegistry(ctx.contacts),
        auth_registry=AuthRegistry(),
        clock=lambda: BASE_TIME,
    )


def test_real_indexes_and_disposable_database_boundary(bound_context: MongoContext) -> None:
    _prepare(bound_context)

    contact_names = {item["name"] for item in bound_context.contacts.list_indexes()}
    verification_names = {item["name"] for item in bound_context.verifications.list_indexes()}
    rate_names = {item["name"] for item in bound_context.rate_limits.list_indexes()}

    assert {
        "_id_",
        "verified_recovery_contact_identity_unique",
        "verified_recovery_contact_active_address_unique",
        "verified_recovery_contact_active_principal_unique",
        "verified_recovery_contact_tenant_principal_status",
    } <= contact_names
    assert {
        "_id_",
        "recovery_contact_verification_identity_unique",
        "recovery_contact_verification_token_unique",
        "recovery_contact_verification_tenant_principal_status_expiry",
    } <= verification_names
    assert {
        "_id_",
        "password_recovery_rate_lookup",
        "password_recovery_rate_ttl",
    } <= rate_names
    assert bound_context.database_name != "wilsy"


def test_real_contact_persistence_is_digest_only_and_tenant_scoped(
    bound_context: MongoContext,
) -> None:
    _prepare(bound_context)
    registry = VerifiedRecoveryContactRegistry(bound_context.contacts)
    contact = _contact(contact_id="WILSYCONTACT-R10E35-DIGEST")

    registry.create(contact)

    persisted = bound_context.contacts.find_one({"contact_id": contact.contact_id})
    assert persisted is not None
    assert persisted["address_digest"] == ADDRESS_DIGEST
    assert all(key not in persisted for key in ("email", "address", "raw_address"))
    assert registry.get_active_by_principal(
        tenant_id=TENANT,
        principal_id=PRINCIPAL,
    ) == contact
    assert registry.get_active_by_principal(
        tenant_id=OTHER_TENANT,
        principal_id=PRINCIPAL,
    ) is None


def test_real_verification_persistence_is_digest_only_and_cross_tenant_absent(
    bound_context: MongoContext,
) -> None:
    _prepare(bound_context)
    registry = RecoveryContactVerificationRegistry(bound_context.verifications)
    verification = _verification(verification_id="WILSYVERIFY-R10E35-DIGEST")

    registry.create(verification)

    persisted = bound_context.verifications.find_one(
        {"verification_id": verification.verification_id}
    )
    assert persisted is not None
    assert persisted["address_digest"] == ADDRESS_DIGEST
    assert persisted["token_digest"] == TOKEN_DIGEST
    assert all(
        key not in persisted
        for key in ("email", "raw_email", "raw_token", "verification_token")
    )
    assert registry.get_by_token_digest(
        tenant_id=TENANT,
        token_digest=TOKEN_DIGEST,
    ) == verification
    assert registry.get_by_token_digest(
        tenant_id=OTHER_TENANT,
        token_digest=TOKEN_DIGEST,
    ) is None


def test_real_completion_transaction_creates_contact_and_consumes_verification(
    bound_context: MongoContext,
) -> None:
    _prepare(bound_context)
    _seed_authority(bound_context)
    verification = _verification(verification_id="WILSYVERIFY-R10E35-COMMIT")
    RecoveryContactVerificationRegistry(bound_context.verifications).create(verification)

    result = _service(bound_context).verify_contact(
        tenant_id=TENANT,
        verification_token=RAW_VERIFICATION_TOKEN,
    )

    assert result.status == "RECOVERY_CONTACT_VERIFIED"
    persisted_verification = bound_context.verifications.find_one(
        {"verification_id": verification.verification_id}
    )
    assert persisted_verification is not None
    assert persisted_verification["status"] == RecoveryContactVerificationStatus.CONSUMED.value

    contact = VerifiedRecoveryContactRegistry(bound_context.contacts).get_active_by_principal(
        tenant_id=TENANT,
        principal_id=PRINCIPAL,
    )
    assert contact is not None
    assert contact.address_digest == ADDRESS_DIGEST
    assert contact.status is VerifiedRecoveryContactStatus.ACTIVE


def test_real_completion_replaces_changed_active_contact_atomically(
    bound_context: MongoContext,
) -> None:
    _prepare(bound_context)
    _seed_authority(bound_context)
    contact_registry = VerifiedRecoveryContactRegistry(bound_context.contacts)
    old_digest = recovery_address_digest("old.r10e35@example.com")
    old_contact = _contact(
        contact_id="WILSYCONTACT-R10E35-OLD",
        digest=old_digest,
    )
    contact_registry.create(old_contact)

    verification = _verification(verification_id="WILSYVERIFY-R10E35-REPLACE")
    RecoveryContactVerificationRegistry(bound_context.verifications).create(verification)

    _service(bound_context).verify_contact(
        tenant_id=TENANT,
        verification_token=RAW_VERIFICATION_TOKEN,
    )

    old_row = bound_context.contacts.find_one({"contact_id": old_contact.contact_id})
    assert old_row is not None
    assert old_row["status"] == VerifiedRecoveryContactStatus.REVOKED.value
    active = contact_registry.get_active_by_principal(
        tenant_id=TENANT,
        principal_id=PRINCIPAL,
    )
    assert active is not None
    assert active.address_digest == ADDRESS_DIGEST
    assert bound_context.contacts.count_documents(
        {
            "tenant_id": TENANT,
            "principal_id": PRINCIPAL,
            "channel": "EMAIL",
            "status": "ACTIVE",
        }
    ) == 1


def test_real_email_drift_rolls_back_without_contact_or_verification_mutation(
    bound_context: MongoContext,
) -> None:
    _prepare(bound_context)
    _seed_authority(bound_context)
    verification = _verification(verification_id="WILSYVERIFY-R10E35-DRIFT")
    RecoveryContactVerificationRegistry(bound_context.verifications).create(verification)

    bound_context.users.update_one(
        {"user_id": PRINCIPAL, "tenantId": TENANT},
        {"$set": {"email": "changed.r10e35@example.com"}},
    )

    with pytest.raises(RecoveryContactVerificationServiceError) as captured:
        _service(bound_context).verify_contact(
            tenant_id=TENANT,
            verification_token=RAW_VERIFICATION_TOKEN,
        )

    assert captured.value.code is RecoveryContactVerificationCode.EMAIL_CHANGED
    persisted = bound_context.verifications.find_one(
        {"verification_id": verification.verification_id}
    )
    assert persisted is not None
    assert persisted["status"] == RecoveryContactVerificationStatus.ACTIVE.value
    assert bound_context.contacts.count_documents({}) == 0


def test_real_replay_does_not_create_second_contact(
    bound_context: MongoContext,
) -> None:
    _prepare(bound_context)
    _seed_authority(bound_context)
    verification = _verification(verification_id="WILSYVERIFY-R10E35-REPLAY")
    RecoveryContactVerificationRegistry(bound_context.verifications).create(verification)
    service = _service(bound_context)

    service.verify_contact(
        tenant_id=TENANT,
        verification_token=RAW_VERIFICATION_TOKEN,
    )
    before = bound_context.contacts.count_documents({})

    with pytest.raises(RecoveryContactVerificationServiceError) as replay:
        service.verify_contact(
            tenant_id=TENANT,
            verification_token=RAW_VERIFICATION_TOKEN,
        )

    assert replay.value.code in {
        RecoveryContactVerificationCode.VERIFICATION_INVALID,
        RecoveryContactVerificationCode.VERIFICATION_REPLAYED,
    }
    assert bound_context.contacts.count_documents({}) == before == 1


def test_real_rate_gate_namespaces_and_exact_limit(bound_context: MongoContext) -> None:
    _prepare(bound_context)
    reset_gate = PasswordRecoveryRateLimit(
        bound_context.rate_limits,
        namespace="password-reset",
        max_requests=2,
    )
    verification_gate = PasswordRecoveryRateLimit(
        bound_context.rate_limits,
        namespace="recovery-contact-verification",
        max_requests=1,
    )

    reset_gate.require_allowed(
        tenant_id=TENANT,
        address_digest=ADDRESS_DIGEST,
        observed_at=BASE_TIME,
    )
    reset_gate.require_allowed(
        tenant_id=TENANT,
        address_digest=ADDRESS_DIGEST,
        observed_at=BASE_TIME + timedelta(seconds=10),
    )
    verification_gate.require_allowed(
        tenant_id=TENANT,
        address_digest=ADDRESS_DIGEST,
        observed_at=BASE_TIME,
    )

    with pytest.raises(PasswordRecoveryRequestRateLimitedError):
        reset_gate.require_allowed(
            tenant_id=TENANT,
            address_digest=ADDRESS_DIGEST,
            observed_at=BASE_TIME + timedelta(seconds=20),
        )
    with pytest.raises(PasswordRecoveryRequestRateLimitedError):
        verification_gate.require_allowed(
            tenant_id=TENANT,
            address_digest=ADDRESS_DIGEST,
            observed_at=BASE_TIME + timedelta(seconds=20),
        )

    rows = list(bound_context.rate_limits.find({}))
    assert len(rows) == 2
    assert {row["namespace"] for row in rows} == {
        "password-reset",
        "recovery-contact-verification",
    }
    assert sorted(row["count"] for row in rows) == [2, 3]
    assert all("email" not in row and "raw_token" not in row for row in rows)


def test_real_transaction_smoke(bound_context: MongoContext) -> None:
    probe = bound_context.database["r10e35_transaction_probe"]

    with bound_context.client.start_session() as session:
        def callback(tx_session: Any) -> None:
            probe.insert_one({"probe": "opaque"}, session=tx_session)
            assert probe.find_one({"probe": "opaque"}, session=tx_session) is not None

        session.with_transaction(callback)

    assert probe.count_documents({"probe": "opaque"}) == 1


# =============================================================================
# SOVEREIGN ARTIFACT SEAL
# =============================================================================
# ARTIFACT: test_password_recovery_engine_real_mongo.py
# VERSION: v1.0.1-R10E46-PASSWORD-RECOVERY-ENGINE-REAL-MONGO-TYPE-CLOSURE
# AUTHORITY BOUNDARY: disposable real-Mongo recovery-engine evidence only
# TENANT POSTURE: UUID-isolated loopback DB; exact tenant/principal/digest scope
# FAIL-CLOSED POSTURE: unavailable Mongo, drift, replay, cross-tenant access reject
# FINANCIAL EXECUTION AUTHORITY: none; Kennel EOS remains exclusive
# END OF WILSY OS SOVEREIGN ARTIFACT
