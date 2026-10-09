"""Real-Mongo certificate for D21B6 tenant branding workspace projection.

TITLE: Tenant Branding Workspace Projection Real-Mongo Certificate
VERSION: v1.0.1-D21B6-TENANT-BRANDING-WORKSPACE-PROJECTION-REAL-MONGO-CERT
AUTHORITY: Wilsy OS Core Governance
EPITOME: Certify the complete D21B2B -> D21B4B -> D21B5B -> D21B6 read chain
         against one disposable Mongo replica-set database under caller-owned
         transactions.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tests/integration/test_tenant_branding_workspace_projection_real_mongo.py
COLLABORATION / OWNERSHIP: Host-backed D21B6 composition certificate only; all
                            durable source authorities remain owned by their
                            certified registries.
CERTIFICATION / UPDATE DATE: 2026-09-25
CHANGELOG: v1.0.1-D21B6-TENANT-BRANDING-WORKSPACE-PROJECTION-REAL-MONGO-CERT adds explicit dictionary shape narrowing for optional
           logo/favicon projection descriptors so the certificate satisfies
           bounded Pyright without changing any runtime assertion.
           v1.0.0-D21B6-TENANT-BRANDING-WORKSPACE-PROJECTION-REAL-MONGO-CERT proved exact committed full-chain composition, safe absent
           branding, tenant silence, caller transaction enforcement, entitlement
           suspension revocation of presentation, and durable asset-byte
           corruption rejection.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2; ISO 27001.
SECURITY / PRIVACY POSTURE: UUID-isolated synthetic evidence and bounded image
                             bytes only; no credentials or external calls.
TENANT BOUNDARY: All six physical collections and runtime reads are tenant scoped.
AUTHORITY BOUNDARY: Read-only presentation composition evidence only.
FINANCIAL AUTHORITY BOUNDARY: None; Kennel EOS remains exclusive.
TRANSACTION BOUNDARY: Test caller owns every session/transaction lifecycle.
FAIL-CLOSED DECLARATION: Once fixture yields, any persistence, correlation,
                         transaction, suspension or corruption failure is a
                         certificate failure.
"""
from __future__ import annotations

from datetime import datetime, timedelta, timezone
import json
import os
from typing import Any, Iterator
import uuid

import pytest
from pymongo import MongoClient
from pymongo.errors import PyMongoError
from pymongo.read_concern import ReadConcern
from pymongo.write_concern import WriteConcern

from tools.eos.auth import tenant_branding_workspace_projection as projection
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
NOW = datetime(2026, 9, 25, 21, 0, tzinfo=timezone.utc)
FP = "a" * 128
LOGO_BYTES = b"\x89PNG\r\n\x1a\nD21B6-real-logo"
FAVICON_BYTES = b"\x89PNG\r\n\x1a\nD21B6-real-favicon"


@pytest.fixture
def mongo_context() -> Iterator[
    tuple[MongoClient[Any], Any, Any, Any, Any, Any, Any, Any]
]:
    """Yield one isolated database and all six canonical branding collections."""
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

        database = client[f"wilsy_d21b6_branding_{uuid.uuid4().hex}"]

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

        entitlement_registry.ensure_indexes(
            entitlement_history,
            entitlement_current,
        )
        profile_registry.ensure_indexes(
            profiles,
            selections,
            profile_current,
        )
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


def _seed_current_branding(
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
    """Atomically seed mutually correlated current branding authority."""
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
            active_result = entitlement_registry.transition(
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
            )
            active = active_result.entitlement

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
                profile_label="Primary real-Mongo brand",
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
            profile_registry.persist_profile(
                profile,
                profiles,
                session=session,
            )
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


def _read_projection(
    *,
    tenant_id: str,
    client: MongoClient[Any],
    entitlement_history: Any,
    entitlement_current: Any,
    profiles: Any,
    selections: Any,
    profile_current: Any,
    assets: Any,
) -> projection.TenantBrandingWorkspaceProjection | None:
    """Read D21B6 under one caller-owned transaction."""
    with client.start_session() as session:
        with session.start_transaction():
            return projection.build_tenant_branding_workspace_projection(
                tenant_id=tenant_id,
                entitlement_history_collection=entitlement_history,
                entitlement_current_collection=entitlement_current,
                profile_collection=profiles,
                selection_collection=selections,
                profile_current_collection=profile_current,
                asset_collection=assets,
                session=session,
            )


def test_real_full_chain_projects_current_active_branding_without_raw_bytes(
    mongo_context: tuple[MongoClient[Any], Any, Any, Any, Any, Any, Any, Any],
) -> None:
    """Physically prove exact current entitlement/profile/assets compose safely."""
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
    active = _seed_current_branding(
        tenant_id=tenant,
        client=client,
        entitlement_history=entitlement_history,
        entitlement_current=entitlement_current,
        profiles=profiles,
        selections=selections,
        profile_current=profile_current,
        assets=assets,
    )

    result = _read_projection(
        tenant_id=tenant,
        client=client,
        entitlement_history=entitlement_history,
        entitlement_current=entitlement_current,
        profiles=profiles,
        selections=selections,
        profile_current=profile_current,
        assets=assets,
    )
    assert result is not None
    payload = result.to_dict()
    assert payload["tenantId"] == tenant
    assert payload["entitlementFingerprint"] == active.fingerprint
    assert payload["brandingTier"] == TenantBrandingTier.INSTITUTIONAL.value
    logo_payload = payload["logo"]
    favicon_payload = payload["favicon"]
    assert isinstance(logo_payload, dict)
    assert isinstance(favicon_payload, dict)
    assert logo_payload["kind"] == "LOGO"
    assert favicon_payload["kind"] == "FAVICON"
    assert payload["platformTrustMarkRequired"] is True

    serialized = json.dumps(payload, sort_keys=True)
    assert "D21B6-real-logo" not in serialized
    assert "D21B6-real-favicon" not in serialized
    assert "data:" not in serialized
    assert "http://" not in serialized
    assert "https://" not in serialized


def test_real_no_current_profile_and_foreign_tenant_are_safe_absence(
    mongo_context: tuple[MongoClient[Any], Any, Any, Any, Any, Any, Any, Any],
) -> None:
    """No explicit current profile means no tenant-brand presentation authority."""
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
    _seed_current_branding(
        tenant_id=tenant,
        client=client,
        entitlement_history=entitlement_history,
        entitlement_current=entitlement_current,
        profiles=profiles,
        selections=selections,
        profile_current=profile_current,
        assets=assets,
    )

    absent = _read_projection(
        tenant_id=foreign,
        client=client,
        entitlement_history=entitlement_history,
        entitlement_current=entitlement_current,
        profiles=profiles,
        selections=selections,
        profile_current=profile_current,
        assets=assets,
    )
    assert absent is None


def test_real_inactive_session_cannot_read_branding_authority(
    mongo_context: tuple[MongoClient[Any], Any, Any, Any, Any, Any, Any, Any],
) -> None:
    """D21B6 inherits the registries' active caller-transaction requirement."""
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
    _seed_current_branding(
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
        with pytest.raises(
            projection.TenantBrandingWorkspaceProjectionError
        ) as raised:
            projection.build_tenant_branding_workspace_projection(
                tenant_id=tenant,
                entitlement_history_collection=entitlement_history,
                entitlement_current_collection=entitlement_current,
                profile_collection=profiles,
                selection_collection=selections,
                profile_current_collection=profile_current,
                asset_collection=assets,
                session=session,
            )
    assert raised.value.code == "D21B6_PROFILE_AUTHORITY_UNAVAILABLE"


def test_real_entitlement_suspension_revokes_previously_approved_branding(
    mongo_context: tuple[MongoClient[Any], Any, Any, Any, Any, Any, Any, Any],
) -> None:
    """Current entitlement suspension blocks a still-current historical profile."""
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
    active = _seed_current_branding(
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

    with pytest.raises(
        projection.TenantBrandingWorkspaceProjectionError
    ) as raised:
        _read_projection(
            tenant_id=tenant,
            client=client,
            entitlement_history=entitlement_history,
            entitlement_current=entitlement_current,
            profiles=profiles,
            selections=selections,
            profile_current=profile_current,
            assets=assets,
        )
    assert raised.value.code == "D21B6_ENTITLEMENT_INACTIVE"


def test_real_asset_byte_corruption_rejects_current_branding_projection(
    mongo_context: tuple[MongoClient[Any], Any, Any, Any, Any, Any, Any, Any],
) -> None:
    """Durable byte tampering cannot pass through an otherwise-current profile."""
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
    _seed_current_branding(
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

    with pytest.raises(
        projection.TenantBrandingWorkspaceProjectionError
    ) as raised:
        _read_projection(
            tenant_id=tenant,
            client=client,
            entitlement_history=entitlement_history,
            entitlement_current=entitlement_current,
            profiles=profiles,
            selections=selections,
            profile_current=profile_current,
            assets=assets,
        )
    assert raised.value.code == "D21B6_ASSET_AUTHORITY_UNAVAILABLE"


# ARTIFACT: test_tenant_branding_workspace_projection_real_mongo.py
# VERSION: v1.0.1-D21B6-TENANT-BRANDING-WORKSPACE-PROJECTION-REAL-MONGO-CERT
# AUTHORITY BOUNDARY: host-backed current branding composition evidence only; no IAM/browser/legal/financial authority
# TENANT POSTURE: disposable UUID database and exact tenant-scoped six-collection chain
# FAIL-CLOSED POSTURE: inactive transaction, suspended entitlement and byte corruption cannot become presentation truth
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively
# END OF WILSY OS SOVEREIGN ARTIFACT
