"""TITLE: WILSY OS Tenant Branding Asset Upload HTTP Real-Mongo Certificate.
VERSION: v1.0.0-L10-P2C7R-D21B-GOVERNED-ASSET-UPLOAD-REAL-MONGO-CERT
AUTHORITY: Wilsy OS Core Governance
EPITOME: Exercise the published multipart tenant-branding upload route against
         a real Mongo replica set, then prove immutable bytes, entitlement and
         authorization gates, profile binding, currentness and authenticated
         byte delivery without creating browser, URL, financial or IAM truth.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tests/integration/test_tenant_branding_asset_upload_http_real_mongo.py
COLLABORATION / OWNERSHIP: D21B5A/B asset evidence and registry, D21B2B
                            entitlement, D21B3/D21B4B profile/selection,
                            D21B6/D21B10 workspace delivery and the mounted
                            tenant-branding HTTP router remain canonical; this
                            certificate owns disposable real-Mongo evidence.
CERTIFICATION / UPDATE DATE: 2026-09-29
CHANGELOG: v1.0.0-L10-P2C7R-D21B-GOVERNED-ASSET-UPLOAD-REAL-MONGO-CERT
           certifies mounted multipart upload, exact byte/fingerprint
           persistence, policy and IAM denial, rollback, cross-tenant silence,
           profile binding, currentness and authenticated byte delivery.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2; ISO 27001.
SECURITY / PRIVACY POSTURE: Synthetic tenants and UUID-isolated Mongo only;
                             no canonical data, credentials, public URLs or
                             filesystem paths are used.
TENANT BOUNDARY: Every HTTP identity and registry read is exact-tenant scoped;
                 caller tenant/reference/fingerprint fields never become truth.
AUTHORITY BOUNDARY: Upload/profile/delivery certification only. No IAM,
                    subscription, plan, payment, Kennel, Court or UI authority.
FINANCIAL AUTHORITY BOUNDARY: No financial writes; Kennel EOS remains exclusive.
TRANSACTION BOUNDARY: HTTP upload owns one Mongo transaction; D21B5B receives
                      the active session; delivery owns a fresh read transaction.
FAIL-CLOSED DECLARATION: Once topology yields, every assertion fails rather
                         than being converted into a skip.
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
import hashlib
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
from tools.eos.api import auth_router, tenant_branding_router as http_router
from tools.eos.auth.identity import SovereignIdentity
from tools.eos.auth.principal_authority import PrincipalAuthority
from tools.eos.auth.principal_status import PrincipalStatus
from tools.eos.auth.role_assignment import RoleAssignmentAuthority, RoleAssignmentStatus
from tools.eos.auth.role_assignment_repository import RoleAssignmentNotFoundError
from tools.eos.auth.tenant_membership import TenantMembershipAuthority, TenantMembershipStatus
from tools.eos.auth.tenant_membership_repository import TenantMembershipNotFoundError
from tools.eos.auth.principal_authority_repository import PrincipalAuthorityNotFoundError
from tools.eos.kernel import db as kernel_db
from tools.eos.saas.billing import tenant_branding_asset_registry as asset_registry
from tools.eos.saas.billing import tenant_branding_entitlement_registry as entitlement_registry
from tools.eos.saas.billing import tenant_branding_profile_registry as profile_registry
from tools.eos.saas.billing.tenant_branding_vas_policy import TenantBrandingTier
from tools.eos.saas.domain.tenant_branding_asset import (
    MAX_ASSET_BYTES,
    TenantBrandingAssetKind,
    content_fingerprint,
)
from tools.eos.saas.domain.tenant_branding_entitlement import (
    TenantBrandingEntitlementState,
    create_tenant_branding_entitlement,
)
from tools.eos.auth.tenant_branding_workspace_asset_delivery import (
    resolve_current_tenant_branding_asset,
)


VERSION = "v1.0.0-L10-P2C7R-D21B-GOVERNED-ASSET-UPLOAD-REAL-MONGO-CERT"
MONGO_URI = os.getenv("TEST_VENDOR_MONGO_URI", "mongodb://127.0.0.1:27027/?replicaSet=wilsyVendorCertRS")
EXPECTED_REPLICA_SET = "wilsyVendorCertRS"
NOW = datetime(2026, 9, 29, 19, 0, tzinfo=timezone.utc)
FP = "a" * 128
TENANT_A = "tenant-p2c7r-a"
TENANT_B = "tenant-p2c7r-b"
PID = "principal-p2c7r"
PNG = b"\x89PNG\r\n\x1a\nP2C7R-logo"
JPEG = b"\xff\xd8\xff\xe0P2C7R-jpeg\xff\xd9"
WEBP = b"RIFFP2C7RWEBP"
ICO = b"\x00\x00\x01\x00P2C7R-ico"


@dataclass(frozen=True)
class MongoContext:
    client: MongoClient[Any]
    database: Any
    ent_history: Any
    ent_current: Any
    assets: Any
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


def _collection(database: Any, name: str) -> Any:
    return database.get_collection(name, write_concern=WriteConcern(w="majority", j=True), read_concern=ReadConcern("majority"))


def _seed_entitlement(context: MongoContext, tenant_id: str, tier: TenantBrandingTier = TenantBrandingTier.ENTERPRISE) -> None:
    value = create_tenant_branding_entitlement(
        tenant_id=tenant_id,
        entitlement_id=f"entitlement-{tenant_id}",
        branding_tier=tier,
        source_evidence_reference=f"p2c7r-source:{tenant_id}",
        source_evidence_fingerprint=FP,
    )
    with context.client.start_session() as session:
        with session.start_transaction():
            entitlement_registry.create_or_replay(value, context.ent_history, context.ent_current, session=session)
            entitlement_registry.transition(
                tenant_id=tenant_id,
                entitlement_id=value.entitlement_id,
                target_state=TenantBrandingEntitlementState.ACTIVE,
                expected_revision=0,
                evidence_reference=f"p2c7r-active:{tenant_id}",
                evidence_fingerprint=FP,
                occurred_at=NOW,
                history_collection=context.ent_history,
                current_collection=context.ent_current,
                session=session,
            )


@pytest.fixture
def mongo_context() -> Iterator[MongoContext]:
    """Yield one UUID-isolated writable replica-set database and drop it."""
    client: MongoClient[Any] = MongoClient(MONGO_URI, serverSelectionTimeoutMS=3000, connectTimeoutMS=3000, retryWrites=True, tz_aware=True)
    database: Any = None
    try:
        try:
            hello = client.admin.command("hello")
        except PyMongoError as error:
            pytest.skip(f"host Mongo unavailable during hello: {type(error).__name__}: {error}")
        if hello.get("setName") != EXPECTED_REPLICA_SET or hello.get("isWritablePrimary", hello.get("ismaster")) is not True or hello.get("logicalSessionTimeoutMinutes") is None:
            pytest.skip("sanctioned replica-set topology unavailable")
        database_name = f"wilsy_p2c7r_branding_{uuid.uuid4().hex}"
        database = client[database_name]
        context = MongoContext(
            client,
            database,
            _collection(database, entitlement_registry.HISTORY_COLLECTION),
            _collection(database, entitlement_registry.CURRENT_COLLECTION),
            _collection(database, asset_registry.COLLECTION),
            _collection(database, profile_registry.PROFILE_COLLECTION),
            _collection(database, profile_registry.SELECTION_COLLECTION),
            _collection(database, profile_registry.CURRENT_COLLECTION),
            database_name,
        )
        entitlement_registry.ensure_indexes(context.ent_history, context.ent_current)
        asset_registry.ensure_indexes(context.assets)
        profile_registry.ensure_indexes(context.profiles, context.selections, context.profile_current)
        _seed_entitlement(context, TENANT_A)
        _seed_entitlement(context, TENANT_B)
        yield context
    finally:
        if database is not None:
            client.drop_database(database.name)
        client.close()


def _authority_app(context: MongoContext, state: AuthorityState, tenant_id: str) -> TestClient:
    """Mount the actual app while replacing only test-local identity/database seams."""
    http_router.get_client = lambda: context.client  # type: ignore[method-assign]
    http_router.get_database = lambda: context.database  # type: ignore[method-assign]
    monkey_database = context.database
    kernel_db.get_client = lambda: context.client  # type: ignore[assignment]
    kernel_db.get_database = lambda: monkey_database  # type: ignore[assignment]
    identity = SovereignIdentity(identity_id=PID, tenant_id=tenant_id, username="p2c7r", email="p2c7r@example.test", roles=[], permissions=[], auth_method="certificate", status=state.principal_status)
    principal = PrincipalReader(state)
    membership = MembershipReader(state)
    roles = RoleReader(state)
    app = api_server.app
    for dependency in (http_router.get_current_identity, auth_router.get_current_identity):
        app.dependency_overrides[dependency] = lambda identity=identity: identity
    app.dependency_overrides[http_router.get_principal_authority_repository] = lambda: principal
    app.dependency_overrides[http_router.get_tenant_membership_repository] = lambda: membership
    app.dependency_overrides[http_router.get_tenant_role_repository] = lambda: roles
    app.dependency_overrides[http_router.get_auth_role_repository] = lambda: roles
    return TestClient(app)


@pytest.fixture
def api_context(mongo_context: MongoContext) -> Iterator[tuple[MongoContext, AuthorityState, TestClient]]:
    state = AuthorityState()
    client = _authority_app(mongo_context, state, TENANT_A)
    try:
        with client:
            yield mongo_context, state, client
    finally:
        api_server.app.dependency_overrides.clear()


def _data(response: Any) -> Any:
    payload = response.json()
    return payload.get("data")


def _upload(client: TestClient, kind: str = "logo", content: bytes = PNG, media: str = "image/png", filename: str = "logo.png", extra: dict[str, str] | None = None) -> Any:
    return client.post(f"/api/tenant-branding/assets/{kind}", files={"file": (filename, content, media)}, data=extra or {})


def _profile(client: TestClient, *, label: str = "Legal", logo: Any = None, fingerprint: str | None = None, favicon: Any = None, favicon_fingerprint: str | None = None) -> Any:
    payload: dict[str, Any] = {"profile_label": label}
    if logo is not None:
        payload["logo_asset_reference"] = logo
        payload["logo_asset_fingerprint"] = fingerprint
    if favicon is not None:
        payload["favicon_asset_reference"] = favicon
        payload["favicon_asset_fingerprint"] = favicon_fingerprint
    return client.post("/api/tenant-branding/profiles", json=payload)


def _counts(context: MongoContext, tenant_id: str) -> tuple[int, int, int, int, int]:
    return (
        context.ent_history.count_documents({"tenant_id": tenant_id}),
        context.ent_current.count_documents({"tenant_id": tenant_id}),
        context.assets.count_documents({"tenant_id": tenant_id}),
        context.profiles.count_documents({"tenant_id": tenant_id}),
        context.selections.count_documents({"tenant_id": tenant_id}),
    )


def _reseed_tier(context: MongoContext, tenant_id: str, tier: TenantBrandingTier) -> None:
    context.ent_history.delete_many({"tenant_id": tenant_id})
    context.ent_current.delete_many({"tenant_id": tenant_id})
    _seed_entitlement(context, tenant_id, tier)


def _deliver(context: MongoContext, tenant_id: str, kind: TenantBrandingAssetKind) -> Any:
    with context.client.start_session() as session:
        with session.start_transaction():
            return resolve_current_tenant_branding_asset(
                tenant_id=tenant_id,
                asset_kind=kind,
                entitlement_history_collection=context.ent_history,
                entitlement_current_collection=context.ent_current,
                profile_collection=context.profiles,
                selection_collection=context.selections,
                profile_current_collection=context.profile_current,
                asset_collection=context.assets,
                session=session,
            )


def test_real_topology_and_uuid_database(mongo_context: MongoContext) -> None:
    hello = mongo_context.client.admin.command("hello")
    assert hello["setName"] == EXPECTED_REPLICA_SET
    assert mongo_context.database_name.startswith("wilsy_p2c7r_branding_")
    with mongo_context.client.start_session() as session:
        with session.start_transaction():
            assert session.in_transaction is True


def test_real_asset_indexes_are_exact_and_non_ttl(mongo_context: MongoContext) -> None:
    indexes = {item["name"]: item for item in mongo_context.assets.list_indexes() if item["name"] != "_id_"}
    assert set(indexes) == {asset_registry.IDENTITY_INDEX_NAME, asset_registry.CONTENT_INDEX_NAME}
    assert dict(indexes[asset_registry.IDENTITY_INDEX_NAME]["key"]) == {"tenant_id": 1, "asset_reference": 1}
    assert indexes[asset_registry.IDENTITY_INDEX_NAME].get("unique") is True
    assert dict(indexes[asset_registry.CONTENT_INDEX_NAME]["key"]) == {"tenant_id": 1, "content_fingerprint": 1}
    assert indexes[asset_registry.CONTENT_INDEX_NAME].get("unique") is not True
    assert all("expireAfterSeconds" not in item for item in indexes.values())


def test_real_logo_upload_returns_server_descriptor_and_exact_bytes(api_context: tuple[MongoContext, AuthorityState, TestClient]) -> None:
    context, _, client = api_context
    response = _upload(client)
    descriptor = _data(response)
    assert response.status_code == 201
    assert descriptor["reference"].startswith(f"asset:{TENANT_A}:logo:")
    assert descriptor["kind"] == "LOGO" and descriptor["mediaType"] == "image/png"
    assert descriptor["contentLength"] == len(PNG)
    assert descriptor["contentFingerprint"] == hashlib.sha3_512(PNG).hexdigest()
    assert "content_bytes" not in response.text and "http" not in response.text
    stored = context.assets.find_one({"tenant_id": TENANT_A, "asset_reference": descriptor["reference"]})
    assert stored is not None and stored["content_bytes"] == PNG and stored["content_fingerprint"] == descriptor["contentFingerprint"]


def test_real_favicon_upload_is_kind_scoped(api_context: tuple[MongoContext, AuthorityState, TestClient]) -> None:
    context, _, client = api_context
    response = _upload(client, "favicon", PNG, "image/png", "favicon.ico")
    descriptor = _data(response)
    assert response.status_code == 201 and descriptor["kind"] == "FAVICON"
    assert context.assets.count_documents({"tenant_id": TENANT_A, "asset_payload.asset_kind": "FAVICON"}) == 1
    stored = context.assets.find_one({"tenant_id": TENANT_A, "asset_reference": descriptor["reference"]})
    assert stored is not None
    assert stored["tenant_id"] == TENANT_A
    assert "asset_kind" not in stored
    assert stored["asset_payload"]["asset_kind"] == TenantBrandingAssetKind.FAVICON.value
    with context.client.start_session() as session:
        with session.start_transaction():
            resolved = asset_registry.resolve(
                TENANT_A,
                descriptor["reference"],
                expected_content_fingerprint=descriptor["contentFingerprint"],
                expected_kind=TenantBrandingAssetKind.FAVICON,
                collection=context.assets,
                session=session,
            )
    assert resolved.asset.tenant_id == TENANT_A
    assert resolved.asset.asset_kind is TenantBrandingAssetKind.FAVICON
    assert resolved.content == PNG


@pytest.mark.parametrize(("media", "content", "filename"), [("image/jpeg", JPEG, "logo.jpg"), ("image/webp", WEBP, "logo.webp"), ("image/x-icon", ICO, "logo.ico"), ("image/vnd.microsoft.icon", ICO, "logo.bin")])
def test_real_multiple_safe_media_types_are_admitted(api_context: tuple[MongoContext, AuthorityState, TestClient], media: str, content: bytes, filename: str) -> None:
    _, _, client = api_context
    response = _upload(client, content=content, media=media, filename=filename)
    assert response.status_code == 201 and _data(response)["mediaType"] == media


def test_real_fingerprint_is_independent_sha3_of_uploaded_bytes(api_context: tuple[MongoContext, AuthorityState, TestClient]) -> None:
    context, _, client = api_context
    descriptor = _data(_upload(client))
    raw = context.assets.find_one({"asset_reference": descriptor["reference"]})
    assert raw is not None
    assert descriptor["contentFingerprint"] == content_fingerprint(raw["content_bytes"]) == hashlib.sha3_512(PNG).hexdigest()


@pytest.mark.parametrize("kind", ["script", "unknown", "LOGO..favicon"])
def test_real_invalid_kind_rejected_without_row(api_context: tuple[MongoContext, AuthorityState, TestClient], kind: str) -> None:
    context, _, client = api_context
    before = context.assets.count_documents({"tenant_id": TENANT_A})
    response = _upload(client, kind)
    assert response.status_code == 422
    assert response.json()["detail"] == {"code": "D21B5A_ASSET_KIND_INVALID"}
    assert context.assets.count_documents({"tenant_id": TENANT_A}) == before


@pytest.mark.parametrize(("media", "content", "filename"), [("image/svg+xml", b"<svg/>", "logo.png"), ("text/html", b"<html>", "logo.png"), ("text/css", b"body{}", "logo.png"), ("application/javascript", b"alert(1)", "logo.png"), ("application/pdf", b"%PDF-1.7", "logo.png"), ("application/octet-stream", b"binary", "logo.png")])
def test_real_unsafe_media_rejected_before_commit(api_context: tuple[MongoContext, AuthorityState, TestClient], media: str, content: bytes, filename: str) -> None:
    context, _, client = api_context
    before = context.assets.count_documents({"tenant_id": TENANT_A})
    assert _upload(client, media=media, content=content, filename=filename).status_code == 422
    assert context.assets.count_documents({"tenant_id": TENANT_A}) == before


def test_real_empty_content_rejected(api_context: tuple[MongoContext, AuthorityState, TestClient]) -> None:
    context, _, client = api_context
    before = context.assets.count_documents({"tenant_id": TENANT_A})
    assert _upload(client, content=b"").status_code == 422
    assert context.assets.count_documents({"tenant_id": TENANT_A}) == before


def test_real_oversize_content_rejected_without_orphan(api_context: tuple[MongoContext, AuthorityState, TestClient]) -> None:
    context, _, client = api_context
    before = context.assets.count_documents({"tenant_id": TENANT_A})
    assert _upload(client, content=b"x" * (MAX_ASSET_BYTES + 1)).status_code == 422
    assert context.assets.count_documents({"tenant_id": TENANT_A}) == before


def test_real_exact_max_boundary_is_admitted(api_context: tuple[MongoContext, AuthorityState, TestClient]) -> None:
    _, _, client = api_context
    content = b"x" * MAX_ASSET_BYTES
    response = _upload(client, content=content, filename="boundary.bin")
    assert response.status_code == 201 and _data(response)["contentLength"] == MAX_ASSET_BYTES


def test_real_safe_bytes_named_text_are_allowed_by_current_contract(api_context: tuple[MongoContext, AuthorityState, TestClient]) -> None:
    _, _, client = api_context
    assert _upload(client, content=PNG, media="image/png", filename="file.txt").status_code == 201


def test_real_extra_multipart_authority_fields_do_not_control_identity(api_context: tuple[MongoContext, AuthorityState, TestClient]) -> None:
    _, _, client = api_context
    descriptor = _data(_upload(client, extra={"tenant_id": TENANT_B, "asset_reference": "evil", "content_fingerprint": "f" * 128, "role": "ENTERPRISE_ADMIN"}))
    assert descriptor["reference"].startswith(f"asset:{TENANT_A}:") and descriptor["contentFingerprint"] == hashlib.sha3_512(PNG).hexdigest()


def test_real_repeated_http_uploads_have_distinct_server_references(api_context: tuple[MongoContext, AuthorityState, TestClient]) -> None:
    first = _data(_upload(api_context[2]))
    second = _data(_upload(api_context[2]))
    assert first["reference"] != second["reference"]


def test_real_professional_favicon_is_denied_before_asset_write(api_context: tuple[MongoContext, AuthorityState, TestClient]) -> None:
    context, _, client = api_context
    _reseed_tier(context, TENANT_A, TenantBrandingTier.PROFESSIONAL)
    before = context.assets.count_documents({"tenant_id": TENANT_A})
    assert _upload(client, "favicon").status_code == 422
    assert context.assets.count_documents({"tenant_id": TENANT_A}) == before


def test_real_starter_logo_is_denied_before_asset_write(api_context: tuple[MongoContext, AuthorityState, TestClient]) -> None:
    context, _, client = api_context
    _reseed_tier(context, TENANT_A, TenantBrandingTier.STARTER)
    before = context.assets.count_documents({"tenant_id": TENANT_A})
    assert _upload(client).status_code == 422
    assert context.assets.count_documents({"tenant_id": TENANT_A}) == before


@pytest.mark.parametrize("state", [TenantBrandingEntitlementState.SUSPENDED, TenantBrandingEntitlementState.REVOKED])
def test_real_inactive_entitlement_denies_before_asset_write(api_context: tuple[MongoContext, AuthorityState, TestClient], state: TenantBrandingEntitlementState) -> None:
    context, _, client = api_context
    with context.client.start_session() as session:
        with session.start_transaction():
            entitlement_registry.transition(tenant_id=TENANT_A, entitlement_id=f"entitlement-{TENANT_A}", target_state=state, expected_revision=1, evidence_reference=f"p2c7r-{state.value}", evidence_fingerprint=FP, occurred_at=NOW, history_collection=context.ent_history, current_collection=context.ent_current, session=session)
    before = context.assets.count_documents({"tenant_id": TENANT_A})
    assert _upload(client).status_code == 422
    assert context.assets.count_documents({"tenant_id": TENANT_A}) == before


def test_real_missing_current_entitlement_denies(api_context: tuple[MongoContext, AuthorityState, TestClient]) -> None:
    context, _, client = api_context
    context.ent_current.delete_many({"tenant_id": TENANT_A})
    response = _upload(client)
    assert response.status_code == 409
    assert response.json()["detail"] == {"code": "D21B2B_SINGLE_CURRENT_ENTITLEMENT_REQUIRED"}


def test_real_multiple_current_entitlements_fail_closed(api_context: tuple[MongoContext, AuthorityState, TestClient]) -> None:
    context, _, client = api_context
    context.ent_current.drop_index(entitlement_registry.CURRENT_IDENTITY_INDEX_NAME)
    row = context.ent_current.find_one({"tenant_id": TENANT_A})
    assert row is not None
    duplicate = dict(row)
    duplicate.pop("_id", None)
    duplicate["entitlement_id"] = "entitlement-duplicate"
    context.ent_current.insert_one(duplicate)
    assert _upload(client).status_code == 409


@pytest.mark.parametrize("business_role", ["tenant_owner", "tenant_admin"])
def test_real_owner_and_admin_upload_authorized(api_context: tuple[MongoContext, AuthorityState, TestClient], business_role: str) -> None:
    _, state, client = api_context
    state.business_role = business_role
    assert _upload(client).status_code == 201


@pytest.mark.parametrize("business_role", ["tenant_manager", "tenant_auditor", "tenant_legal_partner", "tenant_legal_attorney", "tenant_legal_client", "tenant_sheriff", "tenant_deputy", "subscription_manage", "ambiguous_role"])
def test_real_non_management_or_ambiguous_roles_denied(api_context: tuple[MongoContext, AuthorityState, TestClient], business_role: str) -> None:
    context, state, client = api_context
    state.business_role = business_role
    before = context.assets.count_documents({"tenant_id": TENANT_A})
    assert _upload(client).status_code == 403
    assert context.assets.count_documents({"tenant_id": TENANT_A}) == before


def test_real_inactive_principal_denied(api_context: tuple[MongoContext, AuthorityState, TestClient]) -> None:
    context, state, client = api_context
    state.principal_status = PrincipalStatus.SUSPENDED
    before = context.assets.count_documents({"tenant_id": TENANT_A})
    assert _upload(client).status_code == 403 and context.assets.count_documents({"tenant_id": TENANT_A}) == before


def test_real_inactive_membership_denied(api_context: tuple[MongoContext, AuthorityState, TestClient]) -> None:
    context, state, client = api_context
    state.membership_status = TenantMembershipStatus.REVOKED
    before = context.assets.count_documents({"tenant_id": TENANT_A})
    assert _upload(client).status_code == 403 and context.assets.count_documents({"tenant_id": TENANT_A}) == before


def test_real_inactive_enterprise_grant_denied(api_context: tuple[MongoContext, AuthorityState, TestClient]) -> None:
    _, state, client = api_context
    state.granting_status = RoleAssignmentStatus.REVOKED
    assert _upload(client).status_code == 403


def test_real_upload_failure_after_registry_write_aborts_transaction(api_context: tuple[MongoContext, AuthorityState, TestClient], monkeypatch: pytest.MonkeyPatch) -> None:
    context, _, client = api_context
    original = http_router.asset_registry.create_or_replay
    def fail_after_write(*args: Any, **kwargs: Any) -> Any:
        result = original(*args, **kwargs)
        raise RuntimeError("P2C7R_FORCED_UPLOAD_ROLLBACK")
    monkeypatch.setattr(http_router.asset_registry, "create_or_replay", fail_after_write)
    assert _upload(client).status_code == 503
    assert context.assets.count_documents({"tenant_id": TENANT_A}) == 0


def test_real_registry_exact_replay_and_divergent_conflict(mongo_context: MongoContext) -> None:
    from tools.eos.saas.domain.tenant_branding_asset import register_tenant_branding_asset
    reference = f"asset:{TENANT_A}:logo:replay"
    asset = register_tenant_branding_asset(tenant_id=TENANT_A, asset_reference=reference, asset_kind=TenantBrandingAssetKind.LOGO, media_type="image/png", content=PNG, source_evidence_reference="p2c7r-replay", source_evidence_fingerprint=FP, registered_at=NOW)
    with mongo_context.client.start_session() as session:
        with session.start_transaction():
            first = asset_registry.create_or_replay(asset, PNG, mongo_context.assets, session=session)
    with mongo_context.client.start_session() as session:
        with session.start_transaction():
            replay = asset_registry.create_or_replay(asset, PNG, mongo_context.assets, session=session)
    assert first.content == replay.content == PNG
    with mongo_context.client.start_session() as session:
        with session.start_transaction(), pytest.raises(asset_registry.TenantBrandingAssetRegistryInputError, match="D21B5B_CONTENT_EVIDENCE_MISMATCH"):
            asset_registry.create_or_replay(asset, PNG + b"different", mongo_context.assets, session=session)
    divergent_content = PNG + b"different"
    divergent = register_tenant_branding_asset(tenant_id=TENANT_A, asset_reference=reference, asset_kind=TenantBrandingAssetKind.LOGO, media_type="image/png", content=divergent_content, source_evidence_reference="p2c7r-replay-divergent", source_evidence_fingerprint=FP, registered_at=NOW)
    with mongo_context.client.start_session() as session:
        with session.start_transaction(), pytest.raises(asset_registry.TenantBrandingAssetRegistryConflictError):
            asset_registry.create_or_replay(divergent, divergent_content, mongo_context.assets, session=session)


def test_real_tenant_isolation_and_foreign_profile_binding_denied(api_context: tuple[MongoContext, AuthorityState, TestClient]) -> None:
    context, state, client = api_context
    descriptor = _data(_upload(client))
    client_b = _authority_app(context, state, TENANT_B)
    try:
        with client_b:
            before = context.profiles.count_documents({"tenant_id": TENANT_B})
            response = _profile(client_b, logo=descriptor["reference"], fingerprint=descriptor["contentFingerprint"])
            assert response.status_code in {404, 409, 503}
            assert context.profiles.count_documents({"tenant_id": TENANT_B}) == before
    finally:
        api_server.app.dependency_overrides.clear()


def test_real_profile_wrong_fingerprint_and_wrong_kind_fail_closed(api_context: tuple[MongoContext, AuthorityState, TestClient]) -> None:
    context, _, client = api_context
    logo = _data(_upload(client))["reference"]
    fingerprint = hashlib.sha3_512(PNG).hexdigest()
    before = context.profiles.count_documents({"tenant_id": TENANT_A})
    assert _profile(client, logo=logo, fingerprint="f" * 128).status_code in {409, 422, 503}
    assert _profile(client, favicon=logo, favicon_fingerprint=fingerprint).status_code in {409, 422, 503}
    assert context.profiles.count_documents({"tenant_id": TENANT_A}) == before


def test_real_profile_binding_currentness_and_authenticated_delivery(api_context: tuple[MongoContext, AuthorityState, TestClient]) -> None:
    context, _, client = api_context
    descriptor = _data(_upload(client))
    profile_response = _profile(client, logo=descriptor["reference"], fingerprint=descriptor["contentFingerprint"])
    assert profile_response.status_code == 201 and _data(profile_response)["selected"] is True
    delivered = _deliver(context, TENANT_A, TenantBrandingAssetKind.LOGO)
    assert delivered.content == PNG and delivered.content_fingerprint == descriptor["contentFingerprint"]


def test_real_upload_alone_does_not_change_current_profile_or_delivery(api_context: tuple[MongoContext, AuthorityState, TestClient]) -> None:
    context, _, client = api_context
    first = _data(_upload(client, content=PNG))
    assert _profile(client, logo=first["reference"], fingerprint=first["contentFingerprint"]).status_code == 201
    current_before = context.profile_current.find_one({"tenant_id": TENANT_A})["profile_id"]
    second = _data(_upload(client, content=JPEG, media="image/jpeg", filename="new.jpg"))
    assert context.profile_current.find_one({"tenant_id": TENANT_A})["profile_id"] == current_before
    assert _deliver(context, TENANT_A, TenantBrandingAssetKind.LOGO).content == PNG
    assert second["reference"] != first["reference"]


def test_real_noncurrent_profile_then_selection_moves_delivery_and_preserves_history(api_context: tuple[MongoContext, AuthorityState, TestClient]) -> None:
    context, _, client = api_context
    first = _data(_upload(client, content=PNG))
    assert _profile(client, label="A", logo=first["reference"], fingerprint=first["contentFingerprint"]).status_code == 201
    second = _data(_upload(client, content=JPEG, media="image/jpeg", filename="b.jpg"))
    created = _profile(client, label="B", logo=second["reference"], fingerprint=second["contentFingerprint"])
    assert created.status_code == 201 and _data(created)["selected"] is False
    assert _deliver(context, TENANT_A, TenantBrandingAssetKind.LOGO).content == PNG
    selected = client.post(f"/api/tenant-branding/profiles/{_data(created)['profileId']}/select")
    assert selected.status_code == 200 and _deliver(context, TENANT_A, TenantBrandingAssetKind.LOGO).content == JPEG
    assert context.assets.count_documents({"tenant_id": TENANT_A}) == 2
    assert context.profiles.count_documents({"tenant_id": TENANT_A}) == 2
    assert context.selections.count_documents({"tenant_id": TENANT_A}) == 2


def test_real_corrupt_stored_bytes_denied_by_delivery(api_context: tuple[MongoContext, AuthorityState, TestClient]) -> None:
    context, _, client = api_context
    descriptor = _data(_upload(client))
    assert _profile(client, logo=descriptor["reference"], fingerprint=descriptor["contentFingerprint"]).status_code == 201
    context.assets.update_one({"asset_reference": descriptor["reference"]}, {"$set": {"content_bytes": b"tampered"}})
    with pytest.raises(Exception):
        _deliver(context, TENANT_A, TenantBrandingAssetKind.LOGO)


def test_real_profile_failure_does_not_rollback_precommitted_asset(api_context: tuple[MongoContext, AuthorityState, TestClient], monkeypatch: pytest.MonkeyPatch) -> None:
    context, _, client = api_context
    descriptor = _data(_upload(client))
    original = http_router.profile_registry.persist_profile
    def fail_profile(*args: Any, **kwargs: Any) -> Any:
        original(*args, **kwargs)
        raise RuntimeError("P2C7R_PROFILE_ROLLBACK")
    monkeypatch.setattr(http_router.profile_registry, "persist_profile", fail_profile)
    assert _profile(client, logo=descriptor["reference"], fingerprint=descriptor["contentFingerprint"]).status_code == 503
    assert context.assets.count_documents({"asset_reference": descriptor["reference"]}) == 1
    assert context.profiles.count_documents({"tenant_id": TENANT_A}) == 0


def test_real_unavailable_persistence_is_bounded_503(api_context: tuple[MongoContext, AuthorityState, TestClient], monkeypatch: pytest.MonkeyPatch) -> None:
    _, _, client = api_context
    monkeypatch.setattr(http_router, "get_database", lambda: None)
    assert _upload(client).status_code == 503


def test_real_unauthenticated_upload_is_401(api_context: tuple[MongoContext, AuthorityState, TestClient]) -> None:
    context, _, client = api_context
    api_server.app.dependency_overrides.pop(http_router.get_current_identity, None)
    api_server.app.dependency_overrides.pop(auth_router.get_current_identity, None)
    before = context.assets.count_documents({"tenant_id": TENANT_A})
    assert _upload(client).status_code == 401
    assert context.assets.count_documents({"tenant_id": TENANT_A}) == before


def test_real_canonical_mount_includes_upload_route(api_context: tuple[MongoContext, AuthorityState, TestClient]) -> None:
    _, _, _ = api_context
    paths = set(api_server.app.openapi()["paths"])
    assert "/api/tenant-branding/assets/{kind}" in paths


def test_real_no_financial_or_public_storage_side_effects(api_context: tuple[MongoContext, AuthorityState, TestClient]) -> None:
    context, _, client = api_context
    response = _upload(client)
    assert response.status_code == 201
    encoded = response.text.lower()
    assert "public" not in encoded and "filesystem" not in encoded and "payment" not in encoded
    assert context.database_name != "wilsy"


# ARTIFACT: test_tenant_branding_asset_upload_http_real_mongo.py
# VERSION: v1.0.0-L10-P2C7R-D21B-GOVERNED-ASSET-UPLOAD-REAL-MONGO-CERT
# AUTHORITY BOUNDARY: mounted upload and current branding byte evidence only
# TENANT POSTURE: authenticated identity-derived tenant scope; UUID database
# FAIL-CLOSED POSTURE: unavailable, corrupt, unauthorized, unsafe and foreign state fails
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively
# END OF WILSY OS SOVEREIGN ARTIFACT
