"""TITLE: WILSY OS Tenant Branding Management HTTP Real-Mongo Certificate.
VERSION: v1.0.0-L10-P2C6R-D21B-BRANDING-MANAGEMENT-HTTP-REAL-MONGO-CERT
AUTHORITY: Wilsy OS Core Governance
EPITOME: Exercise the mounted P2C6 tenant-branding HTTP boundary against real
         caller-owned Mongo transactions, canonical D21B2B/D21B4B registries,
         and the published tenant authorization composer.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tests/integration/test_tenant_branding_management_http_real_mongo.py
COLLABORATION / OWNERSHIP: P2C6 HTTP composition consumes D21B2B entitlement,
                            D21B3/D21B4B profile authorities, D21B8 tenant IAM,
                            and the canonical API-server mount; this certificate
                            owns disposable Mongo evidence only.
CERTIFICATION / UPDATE DATE: 2026-09-29
CHANGELOG: v1.0.0-L10-P2C6R-D21B-BRANDING-MANAGEMENT-HTTP-REAL-MONGO-CERT
           establishes mounted-route, tenant-derived authorization, atomic
           profile/selection mutation, rollback, currentness, corruption and
           authority-boundary evidence against a UUID-isolated replica set.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2; ISO 27001.
SECURITY / PRIVACY POSTURE: Synthetic tenants and a disposable local database;
                             no credentials, external URLs, asset bytes,
                             payment state or production collections.
TENANT BOUNDARY: Every HTTP request derives tenant scope from SovereignIdentity;
                 caller tenant selectors are rejected and cross-tenant records
                 are indistinguishable from absence.
AUTHORITY BOUNDARY: HTTP composition and persistence certification only. No
                    subscription, plan, asset, IAM, Kennel, Court or UI truth is
                    created by this certificate.
FINANCIAL AUTHORITY BOUNDARY: No payment, release, execution or settlement
                              truth. Kennel EOS remains exclusive.
TRANSACTION BOUNDARY: The fixture owns Mongo sessions/transactions; production
                      registries receive and propagate those sessions.
FAIL-CLOSED DECLARATION: Once topology validation yields, every persistence,
                         authorization, route, rollback and integrity failure
                         is a test failure rather than a skip.
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
import hashlib
import json
import os
from typing import Any, Iterator
import uuid

import pytest
from fastapi.testclient import TestClient
from pymongo import MongoClient
from pymongo.errors import PyMongoError
from pymongo.read_concern import ReadConcern
from pymongo.write_concern import WriteConcern

from tools.eos.api import api_server
from tools.eos.api import tenant_branding_router as http_router
from tools.eos.auth.identity import SovereignIdentity
from tools.eos.auth.principal_authority import PrincipalAuthority
from tools.eos.auth.principal_status import PrincipalStatus
from tools.eos.auth.role_assignment import RoleAssignmentAuthority, RoleAssignmentStatus
from tools.eos.auth.role_assignment_repository import RoleAssignmentNotFoundError
from tools.eos.auth.tenant_membership import TenantMembershipAuthority, TenantMembershipStatus
from tools.eos.auth.tenant_membership_repository import TenantMembershipNotFoundError
from tools.eos.auth.principal_authority_repository import PrincipalAuthorityNotFoundError
from tools.eos.saas.billing import tenant_branding_entitlement_registry as entitlement_registry
from tools.eos.saas.billing import tenant_branding_profile_registry as profile_registry
from tools.eos.saas.billing.tenant_branding_vas_policy import TenantBrandingTier
from tools.eos.saas.domain.tenant_branding_entitlement import (
    TenantBrandingEntitlementState,
    create_tenant_branding_entitlement,
)
from tools.eos.saas.domain.tenant_branding_profile import approve_tenant_branding_profile
from tools.eos.saas.domain.tenant_branding_profile_selection import select_tenant_branding_profile


VERSION = "v1.0.0-L10-P2C6R-D21B-BRANDING-MANAGEMENT-HTTP-REAL-MONGO-CERT"
MONGO_URI = os.getenv(
    "TEST_VENDOR_MONGO_URI",
    "mongodb://127.0.0.1:27027/?replicaSet=wilsyVendorCertRS",
)
EXPECTED_REPLICA_SET = "wilsyVendorCertRS"
NOW = datetime(2026, 9, 29, 18, 0, tzinfo=timezone.utc)
FP = "a" * 128
TENANT_A = "tenant-p2c6r-a"
TENANT_B = "tenant-p2c6r-b"
PID = "principal-p2c6r"


@dataclass(frozen=True)
class MongoContext:
    client: MongoClient[Any]
    database: Any
    entitlement_history: Any
    entitlement_current: Any
    profiles: Any
    selections: Any
    profile_current: Any
    database_name: str


@dataclass
class AuthorityState:
    principal_status: PrincipalStatus = PrincipalStatus.ACTIVE
    membership_status: TenantMembershipStatus = TenantMembershipStatus.ACTIVE
    business_role: str = "tenant_owner"
    granting_role: str = "ENTERPRISE_ADMIN"
    granting_status: RoleAssignmentStatus = RoleAssignmentStatus.ACTIVE


class PrincipalReader:
    def __init__(self, state: AuthorityState) -> None:
        self.state = state

    def resolve(self, principal_id: str, *, session: Any = None) -> PrincipalAuthority:
        if principal_id != PID:
            raise PrincipalAuthorityNotFoundError("PRINCIPAL_NOT_FOUND")
        return PrincipalAuthority(principal_id, self.state.principal_status, 0)


class MembershipReader:
    def __init__(self, state: AuthorityState) -> None:
        self.state = state

    def resolve(self, principal_id: str, tenant_id: str, *, session: Any = None) -> TenantMembershipAuthority:
        if principal_id != PID or tenant_id not in {TENANT_A, TENANT_B}:
            raise TenantMembershipNotFoundError("MEMBERSHIP_NOT_FOUND")
        return TenantMembershipAuthority(principal_id, tenant_id, self.state.membership_status, 0)


class RoleReader:
    def __init__(self, state: AuthorityState) -> None:
        self.state = state

    def resolve(self, principal_id: str, tenant_id: str, role_id: str, *, session: Any = None) -> RoleAssignmentAuthority:
        if principal_id != PID or tenant_id not in {TENANT_A, TENANT_B}:
            raise RoleAssignmentNotFoundError("ROLE_NOT_FOUND")
        if role_id == self.state.business_role:
            return RoleAssignmentAuthority(principal_id, tenant_id, role_id, RoleAssignmentStatus.ACTIVE, 0)
        if role_id == self.state.granting_role:
            return RoleAssignmentAuthority(principal_id, tenant_id, role_id, self.state.granting_status, 0)
        raise RoleAssignmentNotFoundError("ROLE_NOT_FOUND")


@pytest.fixture
def mongo_context() -> Iterator[MongoContext]:
    """Yield one disposable writable replica-set database and drop it afterward."""
    client: MongoClient[Any] = MongoClient(
        MONGO_URI,
        serverSelectionTimeoutMS=3000,
        connectTimeoutMS=3000,
        retryWrites=True,
        tz_aware=True,
    )
    database: Any = None
    try:
        try:
            hello = client.admin.command("hello")
        except PyMongoError as error:
            pytest.skip(f"host Mongo unavailable during hello: {type(error).__name__}: {error}")
        if hello.get("setName") != EXPECTED_REPLICA_SET:
            pytest.skip(f"wrong replica set: {hello.get('setName')!r}")
        if hello.get("isWritablePrimary", hello.get("ismaster")) is not True:
            pytest.skip("replica set has no writable primary")
        if hello.get("logicalSessionTimeoutMinutes") is None:
            pytest.skip("replica set has no logical-session capability")
        database_name = f"wilsy_p2c6r_branding_http_{uuid.uuid4().hex}"
        database = client[database_name]

        def collection(name: str) -> Any:
            return database.get_collection(
                name,
                write_concern=WriteConcern(w="majority", j=True),
                read_concern=ReadConcern("majority"),
            )

        entitlement_history = collection(entitlement_registry.HISTORY_COLLECTION)
        entitlement_current = collection(entitlement_registry.CURRENT_COLLECTION)
        profiles = collection(profile_registry.PROFILE_COLLECTION)
        selections = collection(profile_registry.SELECTION_COLLECTION)
        profile_current = collection(profile_registry.CURRENT_COLLECTION)
        entitlement_registry.ensure_indexes(entitlement_history, entitlement_current)
        profile_registry.ensure_indexes(profiles, selections, profile_current)
        context = MongoContext(client, database, entitlement_history, entitlement_current, profiles, selections, profile_current, database_name)
        _seed_entitlement(context, TENANT_A)
        _seed_entitlement(context, TENANT_B)
        yield context
    finally:
        if database is not None:
            client.drop_database(database.name)
        client.close()


def _seed_entitlement(context: MongoContext, tenant_id: str) -> Any:
    """Persist one ACTIVE D21B2 entitlement; profile/selection remain absent."""
    pending = create_tenant_branding_entitlement(
        tenant_id=tenant_id,
        entitlement_id=f"entitlement-{tenant_id}",
        branding_tier=TenantBrandingTier.PROFESSIONAL,
        source_evidence_reference=f"p2c6r-source:{tenant_id}",
        source_evidence_fingerprint=FP,
    )
    with context.client.start_session() as session:
        with session.start_transaction():
            entitlement_registry.create_or_replay(
                pending,
                context.entitlement_history,
                context.entitlement_current,
                session=session,
            )
            result = entitlement_registry.transition(
                tenant_id=tenant_id,
                entitlement_id=pending.entitlement_id,
                target_state=TenantBrandingEntitlementState.ACTIVE,
                expected_revision=0,
                evidence_reference=f"p2c6r-activation:{tenant_id}",
                evidence_fingerprint=FP,
                occurred_at=NOW,
                history_collection=context.entitlement_history,
                current_collection=context.entitlement_current,
                session=session,
            )
            return result.entitlement


def _authority_app(context: MongoContext, state: AuthorityState, tenant_id: str) -> TestClient:
    """Return the canonical API server with only test-local authority/db seams overridden."""
    http_router.get_client = lambda: context.client  # type: ignore[method-assign]
    http_router.get_database = lambda: context.database  # type: ignore[method-assign]
    identity = SovereignIdentity(
        identity_id=PID,
        tenant_id=tenant_id,
        username="p2c6r",
        email="p2c6r@example.test",
        roles=[],
        permissions=[],
        auth_method="certificate",
        status=state.principal_status,
    )
    principal = PrincipalReader(state)
    membership = MembershipReader(state)
    roles = RoleReader(state)
    app = api_server.app
    app.dependency_overrides[http_router.get_current_identity] = lambda: identity
    app.dependency_overrides[http_router.get_principal_authority_repository] = lambda: principal
    app.dependency_overrides[http_router.get_tenant_membership_repository] = lambda: membership
    app.dependency_overrides[http_router.get_tenant_role_repository] = lambda: roles
    app.dependency_overrides[http_router.get_auth_role_repository] = lambda: roles
    return TestClient(app)


@pytest.fixture
def api_context(mongo_context: MongoContext) -> Iterator[tuple[MongoContext, AuthorityState, TestClient]]:
    """Mount production routes and clean dependency overrides after each test."""
    state = AuthorityState()
    client = _authority_app(mongo_context, state, TENANT_A)
    try:
        with client:
            yield mongo_context, state, client
    finally:
        api_server.app.dependency_overrides.clear()


def _data(response: Any) -> Any:
    assert response.status_code < 500, response.text
    payload = response.json()
    return payload.get("data")


def _create(client: TestClient, label: str = "Primary") -> Any:
    return client.post("/api/tenant-branding/profiles", json={"profile_label": label, "primary_color": "#112233", "email_display_name": "Wilsy Legal"})


def _counts(context: MongoContext, tenant_id: str) -> tuple[int, int, int, int, int]:
    return (
        context.entitlement_history.count_documents({"tenant_id": tenant_id}),
        context.entitlement_current.count_documents({"tenant_id": tenant_id}),
        context.profiles.count_documents({"tenant_id": tenant_id}),
        context.selections.count_documents({"tenant_id": tenant_id}),
        context.profile_current.count_documents({"tenant_id": tenant_id}),
    )


def test_real_topology_and_transactions(mongo_context: MongoContext) -> None:
    hello = mongo_context.client.admin.command("hello")
    assert hello["setName"] == EXPECTED_REPLICA_SET
    with mongo_context.client.start_session() as session:
        with session.start_transaction():
            assert session.in_transaction is True


def test_real_get_without_profile_is_safe(api_context: tuple[MongoContext, AuthorityState, TestClient]) -> None:
    _, _, client = api_context
    response = client.get("/api/tenant-branding")
    data = _data(response)
    assert response.status_code == 200 and data["profile"] is None
    assert data["entitlement"]["lifecycleState"] == "ACTIVE"


def test_real_first_profile_create_is_selected(api_context: tuple[MongoContext, AuthorityState, TestClient]) -> None:
    context, _, client = api_context
    response = _create(client)
    data = _data(response)
    assert response.status_code == 201 and data["selected"] is True
    assert data["profileId"].startswith("brand-profile-")
    assert len(data["profileFingerprint"]) == 128
    assert context.profiles.count_documents({"tenant_id": TENANT_A}) == 1
    assert context.selections.count_documents({"tenant_id": TENANT_A}) == 1


def test_real_second_profile_preserves_current(api_context: tuple[MongoContext, AuthorityState, TestClient]) -> None:
    context, _, client = api_context
    assert _create(client).status_code == 201
    second = _create(client, "Secondary")
    assert second.status_code == 201 and _data(second)["selected"] is False
    assert context.profiles.count_documents({"tenant_id": TENANT_A}) == 2
    assert context.selections.count_documents({"tenant_id": TENANT_A}) == 1


def test_real_explicit_select_advances_revision_and_history(api_context: tuple[MongoContext, AuthorityState, TestClient]) -> None:
    context, _, client = api_context
    assert _create(client).status_code == 201
    second = _data(_create(client, "Secondary"))["profileId"]
    selected = client.post(f"/api/tenant-branding/profiles/{second}/select")
    data = _data(selected)
    assert selected.status_code == 200 and data["selectionRevision"] == 2
    assert context.selections.count_documents({"tenant_id": TENANT_A}) == 2
    assert context.profile_current.find_one({"tenant_id": TENANT_A})["profile_id"] == second


def test_real_get_current_profile_is_browser_safe(api_context: tuple[MongoContext, AuthorityState, TestClient]) -> None:
    _, _, client = api_context
    assert _create(client).status_code == 201
    response = client.get("/api/tenant-branding")
    encoded = json.dumps(response.json(), sort_keys=True)
    assert response.status_code == 200 and "source_evidence" not in encoded and "tenant_id" not in encoded
    assert _data(response)["capabilities"]["trustMarkRequired"] is True


def test_real_server_generates_profile_and_evidence_ids(api_context: tuple[MongoContext, AuthorityState, TestClient]) -> None:
    context, _, client = api_context
    data = _data(_create(client))
    raw = context.profiles.find_one({"tenant_id": TENANT_A, "profile_id": data["profileId"]})
    assert raw is not None
    payload = raw["profile_payload"]
    assert payload["approval_evidence_reference"].startswith("http:tenant-branding-profile:")
    assert len(payload["approval_evidence_fingerprint"]) == 128


def test_real_invalid_profile_input_is_422_and_nonmutating(api_context: tuple[MongoContext, AuthorityState, TestClient]) -> None:
    context, _, client = api_context
    before = _counts(context, TENANT_A)
    response = client.post("/api/tenant-branding/profiles", json={"profile_label": ""})
    assert response.status_code == 422 and _counts(context, TENANT_A) == before


def test_real_forbidden_authority_fields_are_422(api_context: tuple[MongoContext, AuthorityState, TestClient]) -> None:
    context, _, client = api_context
    before = _counts(context, TENANT_A)
    response = client.post("/api/tenant-branding/profiles", json={"profile_label": "x", "tenant_id": TENANT_B, "entitlement_id": "evil"})
    assert response.status_code == 422 and _counts(context, TENANT_A) == before


def test_real_tenant_selector_is_not_accepted(api_context: tuple[MongoContext, AuthorityState, TestClient]) -> None:
    _, _, client = api_context
    response = client.post("/api/tenant-branding/profiles", json={"profile_label": "x", "tenant": TENANT_B})
    assert response.status_code == 422


def test_real_tenant_isolation_a_and_b(api_context: tuple[MongoContext, AuthorityState, TestClient]) -> None:
    context, state, client = api_context
    assert _create(client, "A").status_code == 201
    client_b = _authority_app(context, state, TENANT_B)
    try:
        with client_b:
            data = _data(client_b.get("/api/tenant-branding"))
            assert data["profile"] is None
            assert client_b.post("/api/tenant-branding/profiles/a-profile/select").status_code == 404
    finally:
        api_server.app.dependency_overrides.clear()


def test_real_unknown_profile_select_is_404(api_context: tuple[MongoContext, AuthorityState, TestClient]) -> None:
    _, _, client = api_context
    assert client.post("/api/tenant-branding/profiles/not-present/select").status_code == 404


def test_real_cross_tenant_select_has_no_mutation(api_context: tuple[MongoContext, AuthorityState, TestClient]) -> None:
    context, state, client = api_context
    profile_id = _data(_create(client))["profileId"]
    before = _counts(context, TENANT_B)
    client_b = _authority_app(context, state, TENANT_B)
    try:
        with client_b:
            assert client_b.post(f"/api/tenant-branding/profiles/{profile_id}/select").status_code == 404
    finally:
        api_server.app.dependency_overrides.clear()
    assert _counts(context, TENANT_B) == before


@pytest.mark.parametrize("business_role", ["tenant_manager", "tenant_auditor", "tenant_legal_partner", "tenant_legal_attorney", "tenant_sheriff", "tenant_deputy"])
def test_real_non_management_business_roles_are_denied(api_context: tuple[MongoContext, AuthorityState, TestClient], business_role: str) -> None:
    _, state, client = api_context
    state.business_role = business_role
    assert client.post("/api/tenant-branding/profiles", json={"profile_label": "denied"}).status_code == 403


@pytest.mark.parametrize("business_role", ["tenant_owner", "tenant_admin"])
def test_real_owner_and_admin_can_manage(api_context: tuple[MongoContext, AuthorityState, TestClient], business_role: str) -> None:
    _, state, client = api_context
    state.business_role = business_role
    assert _create(client).status_code == 201


def test_real_inactive_principal_denied_before_write(api_context: tuple[MongoContext, AuthorityState, TestClient]) -> None:
    context, state, client = api_context
    state.principal_status = PrincipalStatus.SUSPENDED
    before = _counts(context, TENANT_A)
    assert client.post("/api/tenant-branding/profiles", json={"profile_label": "denied"}).status_code == 403
    assert _counts(context, TENANT_A) == before


@pytest.mark.parametrize("membership_status", [TenantMembershipStatus.SUSPENDED, TenantMembershipStatus.REVOKED])
def test_real_inactive_membership_denied_before_write(api_context: tuple[MongoContext, AuthorityState, TestClient], membership_status: TenantMembershipStatus) -> None:
    context, state, client = api_context
    state.membership_status = membership_status
    before = _counts(context, TENANT_A)
    assert client.post("/api/tenant-branding/profiles", json={"profile_label": "denied"}).status_code == 403
    assert _counts(context, TENANT_A) == before


def test_real_inactive_granting_role_denied(api_context: tuple[MongoContext, AuthorityState, TestClient]) -> None:
    _, state, client = api_context
    state.granting_status = RoleAssignmentStatus.REVOKED
    assert client.post("/api/tenant-branding/profiles", json={"profile_label": "denied"}).status_code == 403


def test_real_subscription_manage_role_has_no_branding_write(api_context: tuple[MongoContext, AuthorityState, TestClient]) -> None:
    _, state, client = api_context
    state.business_role = "tenant_manager"
    state.granting_role = "ENTERPRISE_ADMIN"
    assert client.post("/api/tenant-branding/profiles", json={"profile_label": "denied"}).status_code == 403


def test_real_first_profile_rollback_leaves_no_partial_rows(api_context: tuple[MongoContext, AuthorityState, TestClient], monkeypatch: pytest.MonkeyPatch) -> None:
    context, _, client = api_context
    original = http_router.profile_registry.persist_selection_and_advance_current
    def fail_after_selection(*args: Any, **kwargs: Any) -> Any:
        original(*args, **kwargs)
        raise RuntimeError("P2C6R_FORCED_ROLLBACK")
    monkeypatch.setattr(http_router.profile_registry, "persist_selection_and_advance_current", fail_after_selection)
    before = _counts(context, TENANT_A)
    assert _create(client).status_code == 503
    assert _counts(context, TENANT_A) == before


def test_real_second_profile_rollback_preserves_first(api_context: tuple[MongoContext, AuthorityState, TestClient], monkeypatch: pytest.MonkeyPatch) -> None:
    context, _, client = api_context
    assert _create(client).status_code == 201
    before = _counts(context, TENANT_A)
    original = http_router.profile_registry.persist_profile
    def fail_after_profile(*args: Any, **kwargs: Any) -> Any:
        original(*args, **kwargs)
        raise RuntimeError("P2C6R_FORCED_ROLLBACK")
    monkeypatch.setattr(http_router.profile_registry, "persist_profile", fail_after_profile)
    assert _create(client, "second").status_code == 503
    assert _counts(context, TENANT_A) == before


def test_real_selection_rollback_preserves_current(api_context: tuple[MongoContext, AuthorityState, TestClient], monkeypatch: pytest.MonkeyPatch) -> None:
    context, _, client = api_context
    assert _create(client).status_code == 201
    second = _data(_create(client, "second"))["profileId"]
    before = _counts(context, TENANT_A)
    original = http_router.profile_registry.persist_selection_and_advance_current
    def fail_select(*args: Any, **kwargs: Any) -> Any:
        original(*args, **kwargs)
        raise RuntimeError("P2C6R_FORCED_ROLLBACK")
    monkeypatch.setattr(http_router.profile_registry, "persist_selection_and_advance_current", fail_select)
    assert client.post(f"/api/tenant-branding/profiles/{second}/select").status_code == 503
    assert _counts(context, TENANT_A) == before


def test_real_read_transaction_is_nonmutating_and_aborts(api_context: tuple[MongoContext, AuthorityState, TestClient]) -> None:
    context, _, client = api_context
    before = _counts(context, TENANT_A)
    assert client.get("/api/tenant-branding").status_code == 200
    assert _counts(context, TENANT_A) == before


def test_real_suspended_entitlement_denies_before_writes(api_context: tuple[MongoContext, AuthorityState, TestClient]) -> None:
    context, _, client = api_context
    with context.client.start_session() as session:
        with session.start_transaction():
            entitlement_registry.transition(tenant_id=TENANT_A, entitlement_id=f"entitlement-{TENANT_A}", target_state=TenantBrandingEntitlementState.SUSPENDED, expected_revision=1, evidence_reference="suspend", evidence_fingerprint=FP, occurred_at=NOW, history_collection=context.entitlement_history, current_collection=context.entitlement_current, session=session)
    before = _counts(context, TENANT_A)
    assert client.post("/api/tenant-branding/profiles", json={"profile_label": "denied"}).status_code == 422
    assert _counts(context, TENANT_A) == before


def test_real_revoked_entitlement_denies_before_writes(api_context: tuple[MongoContext, AuthorityState, TestClient]) -> None:
    context, _, client = api_context
    with context.client.start_session() as session:
        with session.start_transaction():
            entitlement_registry.transition(tenant_id=TENANT_A, entitlement_id=f"entitlement-{TENANT_A}", target_state=TenantBrandingEntitlementState.REVOKED, expected_revision=1, evidence_reference="revoke", evidence_fingerprint=FP, occurred_at=NOW, history_collection=context.entitlement_history, current_collection=context.entitlement_current, session=session)
    before = _counts(context, TENANT_A)
    assert client.get("/api/tenant-branding").status_code == 422
    assert _counts(context, TENANT_A) == before


def test_real_multiple_current_entitlements_fail_closed(api_context: tuple[MongoContext, AuthorityState, TestClient]) -> None:
    context, _, client = api_context
    index = entitlement_registry.CURRENT_IDENTITY_INDEX_NAME
    context.entitlement_current.drop_index(index)
    row = context.entitlement_current.find_one({"tenant_id": TENANT_A})
    assert row is not None
    duplicate = dict(row)
    duplicate.pop("_id", None)
    duplicate["entitlement_id"] = "entitlement-duplicate"
    context.entitlement_current.insert_one(duplicate)
    assert client.get("/api/tenant-branding").status_code == 409


def test_real_corrupt_entitlement_current_fails_closed(api_context: tuple[MongoContext, AuthorityState, TestClient]) -> None:
    context, _, client = api_context
    context.entitlement_current.update_one({"tenant_id": TENANT_A}, {"$set": {"lifecycle_revision": 999}})
    assert client.get("/api/tenant-branding").status_code == 409


def test_real_corrupt_profile_current_fails_closed(api_context: tuple[MongoContext, AuthorityState, TestClient]) -> None:
    context, _, client = api_context
    assert _create(client).status_code == 201
    context.profiles.update_one({"tenant_id": TENANT_A}, {"$set": {"profile_payload.profile_label": "tampered"}})
    assert client.get("/api/tenant-branding").status_code in {422, 503}


def test_real_replay_and_divergent_profile_conflict_are_bounded(api_context: tuple[MongoContext, AuthorityState, TestClient], monkeypatch: pytest.MonkeyPatch) -> None:
    context, _, client = api_context
    first = _create(client, "same")
    second = _create(client, "same")
    assert first.status_code == 201
    assert second.status_code == 201 and _data(second)["selected"] is False
    assert context.profiles.count_documents({"tenant_id": TENANT_A}) == 2

    class FixedUUID:
        hex = "f" * 32
    monkeypatch.setattr(http_router, "uuid4", lambda: FixedUUID())
    fixed = _create(client, "fixed")
    assert fixed.status_code == 201
    divergent = _create(client, "different")
    assert divergent.status_code == 409
    assert context.profiles.count_documents({"tenant_id": TENANT_A}) == 3


def test_real_route_set_and_canonical_mount_are_exact(api_context: tuple[MongoContext, AuthorityState, TestClient]) -> None:
    _, _, client = api_context
    paths: set[str] = set()
    for route in api_server.app.routes:
        original_router = getattr(route, "original_router", None)
        if original_router is None:
            continue
        prefix = getattr(getattr(route, "include_context", None), "prefix", "")
        for nested in getattr(original_router, "routes", ()):
            nested_path = getattr(nested, "path", None)
            if isinstance(prefix, str) and isinstance(nested_path, str):
                path = f"{prefix}{nested_path}"
                if path.startswith("/api/tenant-branding"):
                    paths.add(path)
    assert paths == {"/api/tenant-branding", "/api/tenant-branding/profiles", "/api/tenant-branding/profiles/{profile_id}/select"}
    assert client.get("/api/tenant-branding").status_code == 200


def test_real_profile_history_order_is_deterministic(api_context: tuple[MongoContext, AuthorityState, TestClient]) -> None:
    context, _, client = api_context
    assert _create(client).status_code == 201
    second = _data(_create(client, "second"))["profileId"]
    assert client.post(f"/api/tenant-branding/profiles/{second}/select").status_code == 200
    rows = list(context.selections.find({"tenant_id": TENANT_A}).sort("selection_revision", 1))
    assert [row["selection_revision"] for row in rows] == [1, 2]
    assert rows[1]["selection_payload"]["prior_selection_id"] == rows[0]["selection_id"]


def test_real_deterministic_sha3_evidence_is_not_browser_assertable(api_context: tuple[MongoContext, AuthorityState, TestClient]) -> None:
    context, _, client = api_context
    response = _create(client)
    data = _data(response)
    raw = context.profiles.find_one({"tenant_id": TENANT_A, "profile_id": data["profileId"]})
    assert raw is not None
    payload = raw["profile_payload"]
    canonical = dict(payload)
    fingerprint = canonical.pop("fingerprint")
    expected = hashlib.sha3_512(json.dumps(canonical, ensure_ascii=False, allow_nan=False, sort_keys=False, separators=(",", ":")).encode()).hexdigest()
    assert fingerprint == expected
    assert "fingerprint" not in json.dumps(response.json())


def test_real_no_asset_upload_or_legacy_write_route(api_context: tuple[MongoContext, AuthorityState, TestClient]) -> None:
    _, _, client = api_context
    assert client.post("/api/tenant-branding/assets", json={"raw_bytes": "bad"}).status_code in {404, 405}


def test_real_bounded_not_found_and_method_errors(api_context: tuple[MongoContext, AuthorityState, TestClient]) -> None:
    _, _, client = api_context
    assert client.get("/api/tenant-branding/profiles/nope/select").status_code == 405
    assert client.delete("/api/tenant-branding").status_code == 405


def test_real_profile_and_selection_rows_are_tenant_scoped(api_context: tuple[MongoContext, AuthorityState, TestClient]) -> None:
    context, state, client = api_context
    assert _create(client).status_code == 201
    client_b = _authority_app(context, state, TENANT_B)
    try:
        with client_b:
            assert _data(client_b.get("/api/tenant-branding"))["profile"] is None
    finally:
        api_server.app.dependency_overrides.clear()
    assert context.profiles.count_documents({"tenant_id": TENANT_B}) == 0
    assert context.selections.count_documents({"tenant_id": TENANT_B}) == 0


def test_real_zero_entitlement_profile_or_asset_mutation_by_read(api_context: tuple[MongoContext, AuthorityState, TestClient]) -> None:
    context, _, client = api_context
    before = _counts(context, TENANT_A)
    assert client.get("/api/tenant-branding").status_code == 200
    assert _counts(context, TENANT_A) == before


def test_real_profile_projection_reports_manage_capability_only_for_authorized_role(api_context: tuple[MongoContext, AuthorityState, TestClient]) -> None:
    _, state, client = api_context
    state.business_role = "tenant_auditor"
    response = client.get("/api/tenant-branding")
    assert response.status_code == 200
    capabilities = _data(response)["capabilities"]
    assert capabilities["canRead"] is True and capabilities["canManageProfile"] is False and capabilities["canManageAssets"] is False


def test_real_wrong_granting_permission_is_denied(api_context: tuple[MongoContext, AuthorityState, TestClient]) -> None:
    _, state, client = api_context
    state.granting_role = "AUDITOR"
    assert client.post("/api/tenant-branding/profiles", json={"profile_label": "denied"}).status_code == 403


def test_real_asset_fields_are_not_writable_by_profile_command(api_context: tuple[MongoContext, AuthorityState, TestClient]) -> None:
    _, _, client = api_context
    response = client.post("/api/tenant-branding/profiles", json={"profile_label": "x", "logo_asset_reference": "asset:bad"})
    assert response.status_code == 422


def test_real_commit_produces_one_profile_and_one_selection(api_context: tuple[MongoContext, AuthorityState, TestClient]) -> None:
    context, _, client = api_context
    assert _create(client).status_code == 201
    assert context.profiles.count_documents({"tenant_id": TENANT_A}) == 1
    assert context.selections.count_documents({"tenant_id": TENANT_A}) == 1
    assert context.profile_current.count_documents({"tenant_id": TENANT_A}) == 1


def test_real_entitlement_currentness_is_rechecked_for_profile_create(api_context: tuple[MongoContext, AuthorityState, TestClient]) -> None:
    context, _, client = api_context
    context.entitlement_current.update_one({"tenant_id": TENANT_A}, {"$set": {"entitlement_id": "foreign"}})
    before = _counts(context, TENANT_A)
    assert _create(client).status_code == 409
    assert _counts(context, TENANT_A) == before


# ARTIFACT: test_tenant_branding_management_http_real_mongo.py
# VERSION: v1.0.0-L10-P2C6R-D21B-BRANDING-MANAGEMENT-HTTP-REAL-MONGO-CERT
# AUTHORITY BOUNDARY: mounted P2C6 HTTP composition and durable registry evidence only
# TENANT POSTURE: authenticated identity-derived tenant scope; no caller selector
# FAIL-CLOSED POSTURE: unavailable, corrupt, unauthorized and cross-tenant state denies
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively
# END OF WILSY OS SOVEREIGN ARTIFACT
