"""Authenticated Real-Mongo HTTP certificate for L8-8H6 recipient administration.

TITLE: Legal Notification Recipient Binding Command API Real-Mongo Certificate
VERSION: v1.0.0-L8-8H6-NOTIFICATION-RECIPIENT-BINDING-COMMAND-REAL-MONGO-CERT
AUTHORITY: Wilsy OS Core Governance / Python EOS Legal Operations
EPITOME: Certifies authenticated Partner/Attorney recipient-binding create,
         replay, revoke and supersede command admission against a writable
         Mongo replica set using production tenant authorization and registries.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tests/integration/test_legal_notification_recipient_binding_command_router_real_mongo.py
COLLABORATION / OWNERSHIP: L8-8H owns binding/lifecycle truth; generic tenant IAM
                            owns actor authority; command API owns only HTTP and
                            transaction composition.
CERTIFICATION / UPDATE DATE: 2026-10-12
CHANGELOG: v1.0.0 establishes authenticated live-IAM HTTP create/replay,
           divergent conflict, forbidden-role and cross-tenant zero-write,
           immutable revoke/supersede, rollback, non-TTL and no-contact proofs.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2.
SECURITY / PRIVACY POSTURE: UUID-isolated synthetic database; opaque IDs only.
TENANT BOUNDARY: X-Tenant-ID, principal, membership, business role, final role,
                 matter and durable writes are exact tenant scoped.
AUTHORITY BOUNDARY: Recipient administration != contact authority != transport
                    authority != delivery evidence != representation authority.
TRANSACTION BOUNDARY: Production command API owns request transactions; harness
                      transactions seed only canonical fixture truth.
FINANCIAL AUTHORITY BOUNDARY: None; Kennel EOS remains exclusive.
FAIL-CLOSED DECLARATION: Denial, foreign tenant, replay divergence, persistence
                         failure or partial supersession cannot fabricate success.
"""
from __future__ import annotations

from datetime import datetime, timedelta, timezone
import os
from typing import Any, Iterator
from uuid import uuid4

from fastapi import FastAPI
from fastapi.testclient import TestClient
import pytest
from pymongo import MongoClient
from pymongo.errors import PyMongoError
from pymongo.read_concern import ReadConcern
from pymongo.write_concern import WriteConcern

from tools.eos.api.errors import register_error_handlers
import tools.eos.api.legal_operations_command_router as command_api
import tools.eos.api.tenant_authorization_http as authorization_http
from tools.eos.auth import authentication, tenant_access
from tools.eos.auth.identity import SovereignIdentity
from tools.eos.auth.principal_authority import PrincipalAuthority
from tools.eos.auth.principal_authority_repository import (
    COLLECTION as PRINCIPAL_COLLECTION,
    PrincipalAuthorityRepository,
)
from tools.eos.auth.principal_status import PrincipalStatus
from tools.eos.auth.role_assignment import (
    RoleAssignmentAuthority,
    RoleAssignmentStatus,
)
from tools.eos.auth.role_assignment_repository import (
    COLLECTION as ROLE_COLLECTION,
    RoleAssignmentNotFoundError,
    RoleAssignmentRepository,
    RoleAssignmentRepositoryError,
)
from tools.eos.auth.tenant_authority_policy import TENANT_ROLES
from tools.eos.auth.tenant_authorization_decision_evidence_registry import (
    COLLECTION as AUTH_EVIDENCE_COLLECTION,
    TenantAuthorizationDecisionEvidenceRegistry,
)
from tools.eos.auth.tenant_business_role import (
    TenantBusinessRoleAuthority,
    TenantBusinessRoleStatus,
)
from tools.eos.auth.tenant_business_role_repository import (
    COLLECTION as BUSINESS_ROLE_COLLECTION,
    TenantBusinessRoleNotFoundError,
    TenantBusinessRoleRepository,
    TenantBusinessRoleRepositoryError,
)
from tools.eos.auth.tenant_membership import (
    TenantMembershipAuthority,
    TenantMembershipStatus,
)
from tools.eos.auth.tenant_membership_repository import (
    COLLECTION as MEMBERSHIP_COLLECTION,
    TenantMembershipRepository,
)
from tools.eos.legal_operations.domain.legal_notification_recipient_binding import (
    LegalNotificationEvent,
)
from tools.eos.legal_operations.domain.legal_operations_lifecycle import (
    CaseMatter,
)
from tools.eos.legal_operations.registry.legal_notification_recipient_binding_registry import (
    COLLECTION as BINDING_COLLECTION,
    LegalNotificationRecipientBindingRegistry,
)
from tools.eos.legal_operations.registry.legal_notification_recipient_binding_lifecycle_registry import (
    COLLECTION as BINDING_LIFECYCLE_COLLECTION,
    LegalNotificationRecipientBindingLifecycleRegistry,
    LegalNotificationRecipientBindingLifecycleRegistryError,
)
from tools.eos.legal_operations.registry.legal_operations_lifecycle_registry import (
    LegalOperationsLifecycleRegistry,
)


VERSION = (
    "v1.0.0-L8-8H6-NOTIFICATION-RECIPIENT-BINDING-COMMAND-REAL-MONGO-CERT"
)
DEFAULT_URI = (
    "mongodb://127.0.0.1:27027/?replicaSet=wilsyVendorCertRS"
)
EXPECTED_REPLICA_SET = "wilsyVendorCertRS"
BASE = datetime(2026, 10, 12, 8, 0, tzinfo=timezone.utc)
EFFECTIVE = BASE + timedelta(days=1)


class _PrincipalReader:
    """Read canonical principal authority from the fixture collection."""

    def __init__(self, collection: Any) -> None:
        self._collection = collection

    def resolve(
        self,
        principal_id: str,
        *,
        session: Any = None,
    ) -> Any:
        return PrincipalAuthorityRepository.get(
            principal_id,
            self._collection,
            session=session,
        )


class _MembershipReader:
    """Read canonical own-tenant membership."""

    def __init__(self, collection: Any) -> None:
        self._collection = collection

    def resolve(
        self,
        principal_id: str,
        tenant_id: str,
        *,
        session: Any = None,
    ) -> Any:
        return TenantMembershipRepository.resolve(
            principal_id,
            tenant_id,
            self._collection,
            session=session,
        )


class _RoleReader:
    """Resolve business and final authorization roles from canonical stores."""

    def __init__(
        self,
        authorization_collection: Any,
        business_collection: Any,
    ) -> None:
        self._authorization_collection = authorization_collection
        self._business_collection = business_collection

    def resolve(
        self,
        principal_id: str,
        tenant_id: str,
        role_id: str,
        *,
        session: Any = None,
    ) -> Any:
        if role_id in TENANT_ROLES:
            try:
                value = TenantBusinessRoleRepository.resolve(
                    principal_id,
                    tenant_id,
                    self._business_collection,
                    session=session,
                )
            except TenantBusinessRoleNotFoundError as error:
                raise RoleAssignmentNotFoundError(
                    "TENANT_BUSINESS_ROLE_NOT_FOUND"
                ) from error
            except TenantBusinessRoleRepositoryError as error:
                raise RoleAssignmentRepositoryError(
                    "TENANT_BUSINESS_ROLE_AUTHORITY_UNAVAILABLE"
                ) from error

            if value.business_role != role_id:
                raise RoleAssignmentNotFoundError(
                    "TENANT_BUSINESS_ROLE_NOT_FOUND"
                )
            return value

        return RoleAssignmentRepository.resolve(
            principal_id,
            tenant_id,
            role_id,
            self._authorization_collection,
            session=session,
        )


@pytest.fixture
def mongo_context() -> Iterator[dict[str, Any]]:
    """Yield one majority-backed disposable recipient-command database."""

    client: MongoClient[Any] = MongoClient(
        os.getenv("TEST_VENDOR_MONGO_URI", DEFAULT_URI),
        serverSelectionTimeoutMS=5000,
        connectTimeoutMS=5000,
        socketTimeoutMS=10000,
        retryWrites=True,
        tz_aware=True,
    )
    database: Any = None

    try:
        try:
            hello = client.admin.command("hello")
        except PyMongoError as error:
            pytest.skip(
                "host Mongo unavailable during hello: "
                f"{type(error).__name__}: {error}"
            )

        if hello.get("setName") != EXPECTED_REPLICA_SET:
            pytest.skip(
                f"wrong replica set: {hello.get('setName')!r}"
            )
        if hello.get(
            "isWritablePrimary",
            hello.get("ismaster"),
        ) is not True:
            pytest.skip("replica set has no writable primary")
        if hello.get("logicalSessionTimeoutMinutes") is None:
            pytest.skip("replica set has no logical-session capability")

        database = client.get_database(
            f"wilsy_l8_8h6_recipient_command_{uuid4().hex}",
            read_concern=ReadConcern("majority"),
            write_concern=WriteConcern(w="majority", j=True),
        )

        collections = {
            "principal": database.get_collection(PRINCIPAL_COLLECTION),
            "membership": database.get_collection(MEMBERSHIP_COLLECTION),
            "roles": database.get_collection(ROLE_COLLECTION),
            "business": database.get_collection(BUSINESS_ROLE_COLLECTION),
            "authorization": database.get_collection(AUTH_EVIDENCE_COLLECTION),
            "lifecycle": database.get_collection(
                command_api.LIFECYCLE_COLLECTION
            ),
            "bindings": database.get_collection(BINDING_COLLECTION),
            "binding_lifecycle": database.get_collection(
                BINDING_LIFECYCLE_COLLECTION
            ),
        }

        PrincipalAuthorityRepository.ensure_indexes(
            collections["principal"]
        )
        TenantMembershipRepository.ensure_indexes(
            collections["membership"]
        )
        RoleAssignmentRepository.ensure_indexes(collections["roles"])
        TenantBusinessRoleRepository.ensure_indexes(
            collections["business"]
        )
        TenantAuthorizationDecisionEvidenceRegistry(
            collections["authorization"],
            principal_repository=object(),
        ).ensure_indexes()
        LegalOperationsLifecycleRegistry.ensure_indexes(
            collections["lifecycle"]
        )
        LegalNotificationRecipientBindingRegistry(
            collections["bindings"]
        ).ensure_indexes()
        LegalNotificationRecipientBindingLifecycleRegistry(
            collections["binding_lifecycle"]
        ).ensure_indexes()

        yield {
            "client": client,
            "database": database,
            "collections": collections,
        }
    finally:
        if database is not None:
            client.drop_database(database.name)
        client.close()


def _seed(
    context: dict[str, Any],
    *,
    business_role: str = "tenant_legal_partner",
    grant_role: str = "LEGAL_PARTNER",
    suffix: str | None = None,
) -> dict[str, str]:
    """Seed one matter, administrator IAM chain and active recipient IAM."""

    suffix = suffix or uuid4().hex
    tenant = f"tenant-recipient-{suffix}"
    actor = f"actor-{suffix}"
    recipient = f"recipient-{suffix}"
    matter_id = f"matter-{suffix}"
    collections = context["collections"]

    matter = CaseMatter(
        tenant_id=tenant,
        case_matter_id=matter_id,
        matter_reference=f"MAT-{suffix}",
        opened_at=BASE,
        evidence_reference=f"matter-source:{suffix}",
    )

    with context["client"].start_session() as session:
        session.start_transaction(
            read_concern=ReadConcern("snapshot"),
            write_concern=WriteConcern(w="majority", j=True),
        )

        LegalOperationsLifecycleRegistry.create(
            matter,
            collections["lifecycle"],
            session=session,
        )

        for principal in (actor, recipient):
            PrincipalAuthorityRepository.create(
                PrincipalAuthority(
                    principal,
                    PrincipalStatus.ACTIVE,
                    0,
                ),
                collections["principal"],
                session=session,
            )
            TenantMembershipRepository.insert(
                TenantMembershipAuthority(
                    principal,
                    tenant,
                    TenantMembershipStatus.ACTIVE,
                    0,
                ),
                collections["membership"],
                session=session,
            )

        TenantBusinessRoleRepository.insert(
            TenantBusinessRoleAuthority(
                actor,
                tenant,
                business_role,
                TenantBusinessRoleStatus.ACTIVE,
                0,
                BASE,
                None,
            ),
            collections["business"],
            session=session,
        )

        RoleAssignmentRepository.insert(
            RoleAssignmentAuthority(
                actor,
                tenant,
                grant_role,
                RoleAssignmentStatus.ACTIVE,
                0,
            ),
            collections["roles"],
            session=session,
        )

        session.commit_transaction()

    return {
        "tenant": tenant,
        "actor": actor,
        "recipient": recipient,
        "matter": matter_id,
    }


def _seed_recipient(
    context: dict[str, Any],
    *,
    tenant: str,
    recipient: str,
) -> None:
    """Persist one additional active same-tenant recipient."""

    c = context["collections"]
    with context["client"].start_session() as session:
        session.start_transaction(
            read_concern=ReadConcern("snapshot"),
            write_concern=WriteConcern(w="majority", j=True),
        )
        PrincipalAuthorityRepository.create(
            PrincipalAuthority(
                recipient,
                PrincipalStatus.ACTIVE,
                0,
            ),
            c["principal"],
            session=session,
        )
        TenantMembershipRepository.insert(
            TenantMembershipAuthority(
                recipient,
                tenant,
                TenantMembershipStatus.ACTIVE,
                0,
            ),
            c["membership"],
            session=session,
        )
        session.commit_transaction()


def _identity(
    principal: str,
    tenant: str,
) -> SovereignIdentity:
    """Inject authentication identity only; durable authorization remains live."""

    return SovereignIdentity(
        identity_id=principal,
        tenant_id=tenant,
        username="recipient-admin",
        email="recipient-admin@example.test",
        auth_method="TEST",
        status=PrincipalStatus.ACTIVE,
    )


def _client(
    context: dict[str, Any],
    monkeypatch: pytest.MonkeyPatch,
    fixture: dict[str, str],
) -> TestClient:
    """Compose production tenant authorization over real durable stores."""

    c = context["collections"]
    principal_reader = _PrincipalReader(c["principal"])
    membership_reader = _MembershipReader(c["membership"])
    role_reader = _RoleReader(c["roles"], c["business"])

    app = FastAPI()
    register_error_handlers(app, debug=False)

    app.dependency_overrides[
        authorization_http.get_current_identity
    ] = lambda: _identity(
        fixture["actor"],
        fixture["tenant"],
    )

    app.dependency_overrides[
        authentication.get_principal_authority_repository
    ] = lambda: principal_reader

    app.dependency_overrides[
        tenant_access.get_tenant_membership_repository
    ] = lambda: membership_reader

    app.dependency_overrides[
        authorization_http.get_role_assignment_repository
    ] = lambda: role_reader

    app.include_router(command_api.router, prefix="/api")

    monkeypatch.setattr(
        command_api,
        "_db_handles",
        lambda: (
            context["client"],
            context["database"],
        ),
    )

    return TestClient(app)


def _create_payload(
    fixture: dict[str, str],
    *,
    binding_id: str = "binding-1",
    recipient: str | None = None,
    effective_from: datetime = EFFECTIVE,
) -> dict[str, str | None]:
    return {
        "binding_id": binding_id,
        "case_matter_id": fixture["matter"],
        "recipient_principal_id": recipient or fixture["recipient"],
        "effective_from": effective_from.isoformat(),
        "effective_until": None,
    }


@pytest.mark.parametrize(
    ("business_role", "grant_role"),
    [
        ("tenant_legal_partner", "LEGAL_PARTNER"),
        ("tenant_legal_attorney", "LEGAL_ATTORNEY"),
    ],
)
def test_real_http_partner_and_attorney_create_exact_replay(
    mongo_context: dict[str, Any],
    monkeypatch: pytest.MonkeyPatch,
    business_role: str,
    grant_role: str,
) -> None:
    """Partner and Attorney create/replay exactly once with server chronology."""

    fixture = _seed(
        mongo_context,
        business_role=business_role,
        grant_role=grant_role,
    )
    c = mongo_context["collections"]
    client = _client(mongo_context, monkeypatch, fixture)
    headers = {"X-Tenant-ID": fixture["tenant"]}
    payload = _create_payload(fixture)

    first = client.post(
        "/api/legal-operations/notification-recipient-bindings",
        json=payload,
        headers=headers,
    )
    second = client.post(
        "/api/legal-operations/notification-recipient-bindings",
        json=payload,
        headers=headers,
    )

    assert first.status_code == 200, first.text
    assert second.status_code == 200, second.text
    assert second.json() == first.json()

    data = first.json()["data"]
    assert data["tenant_id"] == fixture["tenant"]
    assert data["binding_id"] == "binding-1"
    assert data["case_matter_id"] == fixture["matter"]
    assert data["event"] == LegalNotificationEvent.RETURN_READY.value
    assert data["recipient_principal_id"] == fixture["recipient"]
    assert data["created_by_principal_id"] == fixture["actor"]
    assert "created_at" in data
    assert data["created_at"] != payload["effective_from"]
    assert len(data["fingerprint"]) == 128

    assert c["bindings"].count_documents(
        {"tenant_id": fixture["tenant"]}
    ) == 1
    assert c["authorization"].count_documents(
        {
            "tenant_id": fixture["tenant"],
            "operation": (
                "legal_notification_recipient_binding_write"
            ),
            "permission": (
                "legal_operations:"
                "notification_recipient_binding:write"
            ),
        }
    ) == 1

    auth = c["authorization"].find_one(
        {"tenant_id": fixture["tenant"]}
    )
    binding = c["bindings"].find_one(
        {"tenant_id": fixture["tenant"]}
    )
    assert auth is not None
    assert binding is not None
    auth_time = datetime.fromisoformat(auth["authorized_at"])
    durable_auth_time = auth_time.astimezone(timezone.utc).replace(
        microsecond=(auth_time.microsecond // 1000) * 1000
    )
    assert binding["created_at"] == durable_auth_time

    forbidden = {
        "email",
        "phone",
        "address",
        "channel",
        "provider",
        "message",
        "transport",
        "delivery",
    }
    assert not (forbidden & set(binding))

    indexes = c["bindings"].index_information()
    assert all(
        "expireAfterSeconds" not in metadata
        for metadata in indexes.values()
    )


def test_real_http_forbidden_role_and_cross_tenant_are_zero_write(
    mongo_context: dict[str, Any],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Paralegal and foreign tenant scope fail before recipient authority writes."""

    fixture = _seed(
        mongo_context,
        business_role="tenant_legal_paralegal",
        grant_role="LEGAL_PARALEGAL",
    )
    c = mongo_context["collections"]
    client = _client(mongo_context, monkeypatch, fixture)

    denied = client.post(
        "/api/legal-operations/notification-recipient-bindings",
        json=_create_payload(fixture),
        headers={"X-Tenant-ID": fixture["tenant"]},
    )
    assert denied.status_code == 403, denied.text
    assert c["bindings"].count_documents({}) == 0
    assert c["authorization"].count_documents({}) == 0

    partner = _seed(mongo_context)
    partner_client = _client(
        mongo_context,
        monkeypatch,
        partner,
    )
    foreign = partner_client.post(
        "/api/legal-operations/notification-recipient-bindings",
        json=_create_payload(partner),
        headers={"X-Tenant-ID": f"foreign-{uuid4().hex}"},
    )
    assert foreign.status_code == 403, foreign.text
    assert c["bindings"].count_documents(
        {"tenant_id": partner["tenant"]}
    ) == 0
    assert c["authorization"].count_documents(
        {"tenant_id": partner["tenant"]}
    ) == 0


def test_real_http_divergent_same_binding_conflicts_and_preserves_first(
    mongo_context: dict[str, Any],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Same binding identity cannot be replayed with a substituted recipient."""

    fixture = _seed(mongo_context)
    second_recipient = f"recipient-second-{uuid4().hex}"
    _seed_recipient(
        mongo_context,
        tenant=fixture["tenant"],
        recipient=second_recipient,
    )
    c = mongo_context["collections"]
    client = _client(mongo_context, monkeypatch, fixture)
    headers = {"X-Tenant-ID": fixture["tenant"]}

    first = client.post(
        "/api/legal-operations/notification-recipient-bindings",
        json=_create_payload(fixture),
        headers=headers,
    )
    divergent = client.post(
        "/api/legal-operations/notification-recipient-bindings",
        json=_create_payload(
            fixture,
            recipient=second_recipient,
        ),
        headers=headers,
    )

    assert first.status_code == 200, first.text
    assert divergent.status_code == 409, divergent.text
    assert divergent.json() == {
        "detail": (
            "LEGAL_NOTIFICATION_RECIPIENT_BINDING_CONFLICT"
        )
    }

    assert c["bindings"].count_documents(
        {"tenant_id": fixture["tenant"]}
    ) == 1
    row = c["bindings"].find_one(
        {"tenant_id": fixture["tenant"]}
    )
    assert row is not None
    assert row["recipient_principal_id"] == fixture["recipient"]


def test_real_http_revocation_and_supersession_are_append_only(
    mongo_context: dict[str, Any],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Revocation and supersession append lifecycle evidence; target stays immutable."""

    # Revocation scenario.
    fixture = _seed(mongo_context)
    c = mongo_context["collections"]
    client = _client(mongo_context, monkeypatch, fixture)
    headers = {"X-Tenant-ID": fixture["tenant"]}

    created = client.post(
        "/api/legal-operations/notification-recipient-bindings",
        json=_create_payload(fixture),
        headers=headers,
    )
    assert created.status_code == 200, created.text
    original = dict(
        c["bindings"].find_one(
            {"tenant_id": fixture["tenant"]}
        )
        or {}
    )

    revoked = client.post(
        (
            "/api/legal-operations/"
            "notification-recipient-bindings/revocations"
        ),
        json={
            "lifecycle_event_id": "revoke-1",
            "case_matter_id": fixture["matter"],
            "target_binding_id": "binding-1",
            "effective_at": (
                EFFECTIVE + timedelta(hours=1)
            ).isoformat(),
        },
        headers=headers,
    )
    assert revoked.status_code == 200, revoked.text
    after_revoke = c["bindings"].find_one(
        {"tenant_id": fixture["tenant"]}
    )
    assert after_revoke == original
    assert c["binding_lifecycle"].count_documents(
        {"tenant_id": fixture["tenant"]}
    ) == 1

    # Independent supersession scenario.
    second = _seed(
        mongo_context,
        suffix=f"super-{uuid4().hex}",
    )
    successor_principal = f"successor-{uuid4().hex}"
    _seed_recipient(
        mongo_context,
        tenant=second["tenant"],
        recipient=successor_principal,
    )
    second_client = _client(
        mongo_context,
        monkeypatch,
        second,
    )
    second_headers = {"X-Tenant-ID": second["tenant"]}

    target = second_client.post(
        "/api/legal-operations/notification-recipient-bindings",
        json=_create_payload(second),
        headers=second_headers,
    )
    assert target.status_code == 200, target.text

    superseded = second_client.post(
        (
            "/api/legal-operations/"
            "notification-recipient-bindings/supersessions"
        ),
        json={
            "binding_id": "binding-successor",
            "case_matter_id": second["matter"],
            "recipient_principal_id": successor_principal,
            "effective_from": (
                EFFECTIVE + timedelta(hours=2)
            ).isoformat(),
            "effective_until": None,
            "lifecycle_event_id": "supersede-1",
            "target_binding_id": "binding-1",
        },
        headers=second_headers,
    )
    assert superseded.status_code == 200, superseded.text
    body = superseded.json()
    assert body["data"]["binding_id"] == "binding-successor"
    assert body["lifecycle"]["target_binding_id"] == "binding-1"
    assert (
        body["lifecycle"]["successor_binding_id"]
        == "binding-successor"
    )

    assert c["bindings"].count_documents(
        {"tenant_id": second["tenant"]}
    ) == 2
    assert c["binding_lifecycle"].count_documents(
        {"tenant_id": second["tenant"]}
    ) == 1


def test_real_http_supersession_second_write_failure_rolls_back_successor(
    mongo_context: dict[str, Any],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Failure after successor insertion aborts the whole API transaction."""

    fixture = _seed(mongo_context)
    successor_principal = f"rollback-successor-{uuid4().hex}"
    _seed_recipient(
        mongo_context,
        tenant=fixture["tenant"],
        recipient=successor_principal,
    )
    c = mongo_context["collections"]
    client = _client(mongo_context, monkeypatch, fixture)
    headers = {"X-Tenant-ID": fixture["tenant"]}

    initial = client.post(
        "/api/legal-operations/notification-recipient-bindings",
        json=_create_payload(fixture),
        headers=headers,
    )
    assert initial.status_code == 200, initial.text
    before_bindings = c["bindings"].count_documents(
        {"tenant_id": fixture["tenant"]}
    )
    before_lifecycle = c["binding_lifecycle"].count_documents(
        {"tenant_id": fixture["tenant"]}
    )

    original = (
        command_api
        .LegalNotificationRecipientBindingLifecycleRegistry
        .create_or_replay
    )

    def fail_second_write(
        self: Any,
        value: Any,
        *,
        session: Any,
    ) -> Any:
        raise LegalNotificationRecipientBindingLifecycleRegistryError(
            "L8_8H_LIFECYCLE_REGISTRY_PERSISTENCE_UNAVAILABLE"
        )

    monkeypatch.setattr(
        command_api
        .LegalNotificationRecipientBindingLifecycleRegistry,
        "create_or_replay",
        fail_second_write,
    )

    failed = client.post(
        (
            "/api/legal-operations/"
            "notification-recipient-bindings/supersessions"
        ),
        json={
            "binding_id": "binding-rollback-successor",
            "case_matter_id": fixture["matter"],
            "recipient_principal_id": successor_principal,
            "effective_from": (
                EFFECTIVE + timedelta(hours=3)
            ).isoformat(),
            "effective_until": None,
            "lifecycle_event_id": "supersede-rollback-1",
            "target_binding_id": "binding-1",
        },
        headers=headers,
    )

    monkeypatch.setattr(
        command_api
        .LegalNotificationRecipientBindingLifecycleRegistry,
        "create_or_replay",
        original,
    )

    assert failed.status_code == 503, failed.text
    assert failed.json() == {
        "detail": "LEGAL_OPERATIONS_UNAVAILABLE"
    }

    assert c["bindings"].count_documents(
        {"tenant_id": fixture["tenant"]}
    ) == before_bindings
    assert c["bindings"].count_documents(
        {
            "tenant_id": fixture["tenant"],
            "binding_id": "binding-rollback-successor",
        }
    ) == 0
    assert c["binding_lifecycle"].count_documents(
        {"tenant_id": fixture["tenant"]}
    ) == before_lifecycle


# ARTIFACT: test_legal_notification_recipient_binding_command_router_real_mongo.py
# VERSION: v1.0.0-L8-8H6-NOTIFICATION-RECIPIENT-BINDING-COMMAND-REAL-MONGO-CERT
# AUTHORITY BOUNDARY: authenticated recipient-administration HTTP certificate only
# TENANT POSTURE: UUID database; actor, recipient, matter and writes are exact scoped
# FAIL-CLOSED POSTURE: denial/divergence/outage/partial-write paths cannot fabricate success
# FINANCIAL EXECUTION AUTHORITY: none; Kennel EOS exclusively
# END OF WILSY OS SOVEREIGN ARTIFACT
