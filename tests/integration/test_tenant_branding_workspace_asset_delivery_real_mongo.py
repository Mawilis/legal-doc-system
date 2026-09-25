"""Real-Mongo certificate for D21B10 current branding asset delivery.

TITLE: Tenant Branding Workspace Asset Delivery Real-Mongo Certificate
VERSION: v1.0.0-D21B10-TENANT-BRANDING-ASSET-DELIVERY-REAL-MONGO-CERT
AUTHORITY: Wilsy OS Core Governance
EPITOME: Certify exact current logo/favicon byte delivery through the complete
         D21B2B -> D21B4B -> D21B5B -> D21B6 -> D21B10 chain against a
         disposable writable Mongo replica set.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tests/integration/test_tenant_branding_workspace_asset_delivery_real_mongo.py
CERTIFICATION / UPDATE DATE: 2026-09-25
TRANSACTION BOUNDARY: Test caller owns every session/transaction; production
                      delivery composition owns none.
AUTHORITY BOUNDARY: Host-backed read-only current branding byte evidence only.
TENANT BOUNDARY: UUID-isolated database and exact tenant-scoped source chain.
FINANCIAL AUTHORITY BOUNDARY: None; Kennel EOS exclusively owns execution.
FAIL-CLOSED DECLARATION: Once fixture yields, stale/inactive/corrupt/foreign or
                         transaction-invalid authority releases no bytes.
"""
from __future__ import annotations

from datetime import datetime, timedelta, timezone
import os
from typing import Any, Iterator
import uuid

import pytest
from pymongo import MongoClient
from pymongo.errors import PyMongoError
from pymongo.read_concern import ReadConcern
from pymongo.write_concern import WriteConcern

from tools.eos.auth import tenant_branding_workspace_asset_delivery as delivery
from tools.eos.saas.billing import tenant_branding_asset_registry as asset_registry
from tools.eos.saas.billing import tenant_branding_entitlement_registry as entitlement_registry
from tools.eos.saas.billing import tenant_branding_profile_registry as profile_registry
from tools.eos.saas.billing.tenant_branding_vas_policy import TenantBrandingTier
from tools.eos.saas.domain.tenant_branding_asset import (
    TenantBrandingAssetKind,
    register_tenant_branding_asset,
)
from tools.eos.saas.domain.tenant_branding_entitlement import (
    TenantBrandingEntitlement,
    TenantBrandingEntitlementState,
    create_tenant_branding_entitlement,
)
from tools.eos.saas.domain.tenant_branding_profile import approve_tenant_branding_profile
from tools.eos.saas.domain.tenant_branding_profile_selection import (
    select_tenant_branding_profile,
)


MONGO_URI = os.getenv(
    "TEST_VENDOR_MONGO_URI",
    "mongodb://127.0.0.1:27027/?replicaSet=wilsyVendorCertRS",
)
EXPECTED_REPLICA_SET = "wilsyVendorCertRS"
NOW = datetime(2026, 9, 25, 23, 0, tzinfo=timezone.utc)
FP = "a" * 128
LOGO_BYTES = b"\x89PNG\r\n\x1a\nD21B10-real-logo"
FAVICON_BYTES = b"\x89PNG\r\n\x1a\nD21B10-real-favicon"


@pytest.fixture
def mongo_context() -> Iterator[
    tuple[MongoClient[Any], Any, Any, Any, Any, Any, Any, Any]
]:
    """Yield one UUID-isolated database with all six canonical collections."""
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
            pytest.skip(
                f"host Mongo unavailable during hello: {type(error).__name__}: {error}"
            )
        if hello.get("setName") != EXPECTED_REPLICA_SET:
            pytest.skip(f"wrong replica set: {hello.get('setName')!r}")
        if hello.get("isWritablePrimary", hello.get("ismaster")) is not True:
            pytest.skip("replica set has no writable primary")
        if hello.get("logicalSessionTimeoutMinutes") is None:
            pytest.skip("replica set has no logical-session capability")

        database = client[f"wilsy_d21b10_branding_{uuid.uuid4().hex}"]

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
        assets = collection(asset_registry.COLLECTION)

        entitlement_registry.ensure_indexes(entitlement_history, entitlement_current)
        profile_registry.ensure_indexes(profiles, selections, profile_current)
        asset_registry.ensure_indexes(assets)

        yield (
            client,
            database,
            entitlement_history,
            entitlement_current,
            profiles,
            selections,
            profile_current,
            assets,
        )
    finally:
        if database is not None:
            client.drop_database(database.name)
        client.close()


def _seed(
    *,
    tenant_id: str,
    client: MongoClient[Any],
    entitlement_history: Any,
    entitlement_current: Any,
    profiles: Any,
    selections: Any,
    profile_current: Any,
    assets: Any,
) -> TenantBrandingEntitlement:
    """Commit one fully correlated current branding chain."""
    pending = create_tenant_branding_entitlement(
        tenant_id=tenant_id,
        entitlement_id="branding-entitlement-1",
        branding_tier=TenantBrandingTier.INSTITUTIONAL,
        source_evidence_reference="composition-real-1",
        source_evidence_fingerprint=FP,
    )
    logo_reference = f"asset:{tenant_id}:logo:primary"
    favicon_reference = f"asset:{tenant_id}:favicon:primary"
    logo = register_tenant_branding_asset(
        tenant_id=tenant_id,
        asset_reference=logo_reference,
        asset_kind=TenantBrandingAssetKind.LOGO,
        media_type="image/png",
        content=LOGO_BYTES,
        source_evidence_reference="logo-upload-real-1",
        source_evidence_fingerprint=FP,
        registered_at=NOW,
    )
    favicon = register_tenant_branding_asset(
        tenant_id=tenant_id,
        asset_reference=favicon_reference,
        asset_kind=TenantBrandingAssetKind.FAVICON,
        media_type="image/png",
        content=FAVICON_BYTES,
        source_evidence_reference="favicon-upload-real-1",
        source_evidence_fingerprint=FP,
        registered_at=NOW,
    )

    with client.start_session() as session:
        with session.start_transaction():
            entitlement_registry.create_or_replay(
                pending,
                entitlement_history,
                entitlement_current,
                session=session,
            )
            active = entitlement_registry.transition(
                tenant_id=tenant_id,
                entitlement_id=pending.entitlement_id,
                target_state=TenantBrandingEntitlementState.ACTIVE,
                expected_revision=0,
                evidence_reference="activation-real-1",
                evidence_fingerprint=FP,
                occurred_at=NOW,
                history_collection=entitlement_history,
                current_collection=entitlement_current,
                session=session,
            ).entitlement
            asset_registry.create_or_replay(
                logo,
                LOGO_BYTES,
                assets,
                session=session,
            )
            asset_registry.create_or_replay(
                favicon,
                FAVICON_BYTES,
                assets,
                session=session,
            )
            profile = approve_tenant_branding_profile(
                entitlement=active,
                profile_id="profile-primary",
                profile_label="Primary delivery brand",
                source_evidence_reference="profile-submission-real-1",
                source_evidence_fingerprint=FP,
                approved_at=NOW,
                approval_evidence_reference="profile-approval-real-1",
                approval_evidence_fingerprint=FP,
                logo_asset_reference=logo_reference,
                logo_asset_fingerprint=logo.content_fingerprint,
                primary_color="#112233",
                secondary_color="#445566",
                accent_color="#AABBCC",
                email_display_name="Acme Legal",
                favicon_asset_reference=favicon_reference,
                favicon_asset_fingerprint=favicon.content_fingerprint,
            )
            profile_registry.persist_profile(profile, profiles, session=session)
            selection = select_tenant_branding_profile(
                profile=profile,
                current_entitlement=active,
                selection_id="selection-1",
                selection_revision=1,
                selected_at=NOW,
                selection_evidence_reference="selection-real-1",
                selection_evidence_fingerprint=FP,
            )
            profile_registry.persist_selection_and_advance_current(
                selection,
                profiles,
                selections,
                profile_current,
                session=session,
            )
            return active


def _deliver(
    *,
    tenant_id: str,
    kind: TenantBrandingAssetKind,
    client: MongoClient[Any],
    entitlement_history: Any,
    entitlement_current: Any,
    profiles: Any,
    selections: Any,
    profile_current: Any,
    assets: Any,
) -> delivery.TenantBrandingWorkspaceAssetDelivery:
    """Read one current asset under a caller-owned transaction."""
    with client.start_session() as session:
        with session.start_transaction():
            return delivery.resolve_current_tenant_branding_asset(
                tenant_id=tenant_id,
                asset_kind=kind,
                entitlement_history_collection=entitlement_history,
                entitlement_current_collection=entitlement_current,
                profile_collection=profiles,
                selection_collection=selections,
                profile_current_collection=profile_current,
                asset_collection=assets,
                session=session,
            )


def test_real_current_logo_and_favicon_deliver_exact_registered_bytes(
    mongo_context: tuple[MongoClient[Any], Any, Any, Any, Any, Any, Any, Any],
) -> None:
    """Full real-Mongo chain returns exact current immutable image bytes."""
    (
        client,
        _,
        entitlement_history,
        entitlement_current,
        profiles,
        selections,
        profile_current,
        assets,
    ) = mongo_context
    tenant = f"tenant-success-{uuid.uuid4().hex}"
    _seed(
        tenant_id=tenant,
        client=client,
        entitlement_history=entitlement_history,
        entitlement_current=entitlement_current,
        profiles=profiles,
        selections=selections,
        profile_current=profile_current,
        assets=assets,
    )

    logo = _deliver(
        tenant_id=tenant,
        kind=TenantBrandingAssetKind.LOGO,
        client=client,
        entitlement_history=entitlement_history,
        entitlement_current=entitlement_current,
        profiles=profiles,
        selections=selections,
        profile_current=profile_current,
        assets=assets,
    )
    favicon = _deliver(
        tenant_id=tenant,
        kind=TenantBrandingAssetKind.FAVICON,
        client=client,
        entitlement_history=entitlement_history,
        entitlement_current=entitlement_current,
        profiles=profiles,
        selections=selections,
        profile_current=profile_current,
        assets=assets,
    )
    assert logo.content == LOGO_BYTES
    assert logo.media_type == "image/png"
    assert logo.kind is TenantBrandingAssetKind.LOGO
    assert favicon.content == FAVICON_BYTES
    assert favicon.media_type == "image/png"
    assert favicon.kind is TenantBrandingAssetKind.FAVICON


def test_real_foreign_tenant_has_no_deliverable_current_branding(
    mongo_context: tuple[MongoClient[Any], Any, Any, Any, Any, Any, Any, Any],
) -> None:
    """Foreign/no-current tenant receives no asset and no fallback."""
    (
        client,
        _,
        entitlement_history,
        entitlement_current,
        profiles,
        selections,
        profile_current,
        assets,
    ) = mongo_context
    tenant = f"tenant-a-{uuid.uuid4().hex}"
    foreign = f"tenant-b-{uuid.uuid4().hex}"
    _seed(
        tenant_id=tenant,
        client=client,
        entitlement_history=entitlement_history,
        entitlement_current=entitlement_current,
        profiles=profiles,
        selections=selections,
        profile_current=profile_current,
        assets=assets,
    )
    with pytest.raises(delivery.TenantBrandingWorkspaceAssetNotConfiguredError) as raised:
        _deliver(
            tenant_id=foreign,
            kind=TenantBrandingAssetKind.LOGO,
            client=client,
            entitlement_history=entitlement_history,
            entitlement_current=entitlement_current,
            profiles=profiles,
            selections=selections,
            profile_current=profile_current,
            assets=assets,
        )
    assert raised.value.code == "D21B10_BRANDING_NOT_CONFIGURED"


def test_real_inactive_session_cannot_release_branding_bytes(
    mongo_context: tuple[MongoClient[Any], Any, Any, Any, Any, Any, Any, Any],
) -> None:
    """Delivery inherits active transaction requirements from source registries."""
    (
        client,
        _,
        entitlement_history,
        entitlement_current,
        profiles,
        selections,
        profile_current,
        assets,
    ) = mongo_context
    tenant = f"tenant-session-{uuid.uuid4().hex}"
    _seed(
        tenant_id=tenant,
        client=client,
        entitlement_history=entitlement_history,
        entitlement_current=entitlement_current,
        profiles=profiles,
        selections=selections,
        profile_current=profile_current,
        assets=assets,
    )
    with client.start_session() as session:
        assert session.in_transaction is False
        with pytest.raises(delivery.TenantBrandingWorkspaceAssetDeliveryError) as raised:
            delivery.resolve_current_tenant_branding_asset(
                tenant_id=tenant,
                asset_kind=TenantBrandingAssetKind.LOGO,
                entitlement_history_collection=entitlement_history,
                entitlement_current_collection=entitlement_current,
                profile_collection=profiles,
                selection_collection=selections,
                profile_current_collection=profile_current,
                asset_collection=assets,
                session=session,
            )
    assert raised.value.code == "D21B10_CURRENT_BRANDING_AUTHORITY_UNAVAILABLE"


def test_real_entitlement_suspension_revokes_asset_delivery(
    mongo_context: tuple[MongoClient[Any], Any, Any, Any, Any, Any, Any, Any],
) -> None:
    """A historically approved asset cannot be served after current suspension."""
    (
        client,
        _,
        entitlement_history,
        entitlement_current,
        profiles,
        selections,
        profile_current,
        assets,
    ) = mongo_context
    tenant = f"tenant-suspended-{uuid.uuid4().hex}"
    active = _seed(
        tenant_id=tenant,
        client=client,
        entitlement_history=entitlement_history,
        entitlement_current=entitlement_current,
        profiles=profiles,
        selections=selections,
        profile_current=profile_current,
        assets=assets,
    )
    with client.start_session() as session:
        with session.start_transaction():
            entitlement_registry.transition(
                tenant_id=tenant,
                entitlement_id=active.entitlement_id,
                target_state=TenantBrandingEntitlementState.SUSPENDED,
                expected_revision=active.lifecycle_revision,
                evidence_reference="suspension-real-1",
                evidence_fingerprint=FP,
                occurred_at=NOW + timedelta(minutes=1),
                history_collection=entitlement_history,
                current_collection=entitlement_current,
                session=session,
            )

    with pytest.raises(delivery.TenantBrandingWorkspaceAssetDeliveryError) as raised:
        _deliver(
            tenant_id=tenant,
            kind=TenantBrandingAssetKind.LOGO,
            client=client,
            entitlement_history=entitlement_history,
            entitlement_current=entitlement_current,
            profiles=profiles,
            selections=selections,
            profile_current=profile_current,
            assets=assets,
        )
    assert raised.value.code == "D21B10_CURRENT_BRANDING_AUTHORITY_UNAVAILABLE"


def test_real_corrupt_asset_bytes_never_leave_delivery_composer(
    mongo_context: tuple[MongoClient[Any], Any, Any, Any, Any, Any, Any, Any],
) -> None:
    """Physical byte tampering is caught before any delivery value is returned."""
    (
        client,
        _,
        entitlement_history,
        entitlement_current,
        profiles,
        selections,
        profile_current,
        assets,
    ) = mongo_context
    tenant = f"tenant-corrupt-{uuid.uuid4().hex}"
    _seed(
        tenant_id=tenant,
        client=client,
        entitlement_history=entitlement_history,
        entitlement_current=entitlement_current,
        profiles=profiles,
        selections=selections,
        profile_current=profile_current,
        assets=assets,
    )
    assets.update_one(
        {
            "tenant_id": tenant,
            "asset_reference": f"asset:{tenant}:logo:primary",
        },
        {"$set": {"content_bytes": LOGO_BYTES + b"-tampered"}},
    )

    with pytest.raises(delivery.TenantBrandingWorkspaceAssetDeliveryError) as raised:
        _deliver(
            tenant_id=tenant,
            kind=TenantBrandingAssetKind.LOGO,
            client=client,
            entitlement_history=entitlement_history,
            entitlement_current=entitlement_current,
            profiles=profiles,
            selections=selections,
            profile_current=profile_current,
            assets=assets,
        )
    assert raised.value.code == "D21B10_CURRENT_BRANDING_AUTHORITY_UNAVAILABLE"


# ARTIFACT: test_tenant_branding_workspace_asset_delivery_real_mongo.py
# VERSION: v1.0.0-D21B10-TENANT-BRANDING-ASSET-DELIVERY-REAL-MONGO-CERT
# AUTHORITY BOUNDARY: host-backed current logo/favicon delivery evidence only
# TENANT POSTURE: disposable UUID database and exact tenant-scoped source chain
# FAIL-CLOSED POSTURE: inactive/suspended/corrupt/foreign authority releases no bytes
# FINANCIAL EXECUTION AUTHORITY: none; Kennel EOS exclusively
# END OF WILSY OS SOVEREIGN ARTIFACT
