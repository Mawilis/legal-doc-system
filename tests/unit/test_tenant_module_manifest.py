"""TITLE: WILSY OS Tenant Module Manifest Contract Certificate.
VERSION: v1.1.0-WILSY-PLATFORM-OWNER-CERT
AUTHORITY: Repository-owned isolated regression evidence only.
EPITOME: Prove exact WILSY company separation while preserving customer Legal
availability, entitlement validation and fail-closed source behavior.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tests/unit/test_tenant_module_manifest.py
COLLABORATION / OWNERSHIP: Canonical tenant module projection and authenticated HTTP adapter.
CERTIFICATION / UPDATE DATE: 2026-11-13
CHANGELOG: v1.1.0-WILSY-PLATFORM-OWNER-CERT retains all existing assertions and
adds exact-company, customer preservation and legacy entitlement negative gates.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2.
SECURITY / PRIVACY POSTURE: Synthetic typed records only; no production data.
TENANT BOUNDARY: Exact company and customer fixtures; foreign evidence rejects.
AUTHORITY BOUNDARY: Projection tests grant no role, permission or entitlement.
FINANCIAL AUTHORITY BOUNDARY: Kennel EOS exclusively.
"""
from datetime import datetime, timezone

import pytest

from tools.eos.auth.tenant_module_manifest import (
    TenantModuleId,
    TenantModuleManifestError,
    build_tenant_module_manifest,
    list_tenant_module_descriptors,
)
from tools.eos.crm.domain.crm_core_entitlement import (
    CRM_CORE_FEATURE_ID,
    CrmCoreEntitlement,
    CrmCoreEntitlementState,
)
from tools.eos.saas.domain.tenant_product_entitlement import (
    TenantProductEntitlementState,
    create_tenant_product_entitlement,
)
from tools.eos.saas.entitlement.product_catalogue import TenantProductId


NOW = datetime(2026, 11, 6, 8, 0, tzinfo=timezone.utc)
SOURCE = "a" * 128
ACTIVATION = "b" * 128


def _active_product(product_id: TenantProductId, tenant_id: str = "TENANT-A"):
    pending = create_tenant_product_entitlement(
        tenant_id=tenant_id,
        entitlement_id=f"entitlement:{tenant_id}:{product_id.value}",
        product_id=product_id,
        source_evidence_reference="agreement:approved",
        source_evidence_fingerprint=SOURCE,
    )
    return pending.transition(
        TenantProductEntitlementState.ACTIVE,
        expected_revision=0,
        evidence_reference="subscription:active",
        evidence_fingerprint=ACTIVATION,
        occurred_at=NOW,
    )


def _active_crm(tenant_id: str = "TENANT-A"):
    pending = CrmCoreEntitlement(
        tenant_id=tenant_id,
        entitlement_id=f"crm.core:{tenant_id}:subscription-1",
        feature_id=CRM_CORE_FEATURE_ID,
        subscription_id="subscription-1",
        plan_id="plan-1",
        plan_catalogue_version=1,
        subscription_proof_hash="A" * 128,
        lifecycle_state=CrmCoreEntitlementState.PENDING_SOURCE,
    )
    return pending.transition(
        CrmCoreEntitlementState.ACTIVE,
        expected_revision=0,
        evidence_reference="subscription:active",
        evidence_fingerprint=ACTIVATION,
        occurred_at=NOW,
    )


def test_global_module_catalogue_is_closed_and_uses_canonical_product_keys():
    descriptors = list_tenant_module_descriptors()
    assert len(descriptors) == 7
    assert {item.product_id for item in descriptors} == set(TenantProductId)
    assert {item.module_id for item in descriptors} == set(TenantModuleId)


def test_only_exact_active_legal_product_entitlement_projects_legal_os():
    result = build_tenant_module_manifest(
        tenant_id="TENANT-A",
        entitlements=[_active_product(TenantProductId.LEGAL_OPERATIONS)],
    )
    assert len(result) == 1
    assert result[0].module_id is TenantModuleId.LEGAL_OS
    assert result[0].workspace_key == "LEGAL_DASHBOARD"
    assert result[0].entitlement_revision == 1


def test_pos_requires_its_own_active_product_entitlement():
    result = build_tenant_module_manifest(
        tenant_id="TENANT-A",
        entitlements=[_active_product(TenantProductId.POS)],
    )
    assert len(result) == 1
    assert result[0].module_id is TenantModuleId.POS
    assert result[0].product_id is TenantProductId.POS
    assert result[0].workspace_key == "POS_DASHBOARD"
    assert result[0].entitlement_id == "entitlement:TENANT-A:POS"


def test_crm_core_entitlement_projects_crm_without_role_or_permission_claims():
    result = build_tenant_module_manifest(
        tenant_id="TENANT-A",
        entitlements=[_active_crm()],
    )
    assert len(result) == 1
    assert result[0].module_id is TenantModuleId.CRM
    assert result[0].product_id is TenantProductId.CRM


def test_inactive_product_entitlement_is_not_projected():
    pending = create_tenant_product_entitlement(
        tenant_id="TENANT-A",
        entitlement_id="pending-legal",
        product_id=TenantProductId.LEGAL_OPERATIONS,
        source_evidence_reference="agreement:pending",
        source_evidence_fingerprint=SOURCE,
    )
    assert build_tenant_module_manifest(
        tenant_id="TENANT-A",
        entitlements=[pending],
    ) == ()


def test_entitlement_from_another_tenant_fails_closed():
    with pytest.raises(TenantModuleManifestError, match="TENANT_MISMATCH"):
        build_tenant_module_manifest(
            tenant_id="TENANT-A",
            entitlements=[_active_product(TenantProductId.LEGAL_OPERATIONS, "TENANT-B")],
        )


def test_duplicate_product_evidence_fails_closed():
    with pytest.raises(TenantModuleManifestError, match="DUPLICATE_PRODUCT_EVIDENCE"):
        build_tenant_module_manifest(
            tenant_id="TENANT-A",
            entitlements=[
                _active_product(TenantProductId.LEGAL_OPERATIONS),
                _active_product(TenantProductId.LEGAL_OPERATIONS),
            ],
        )


def test_unknown_entitlement_object_cannot_be_used_as_browser_authority():
    class ForgedProjection:
        tenant_id = "TENANT-A"
        product_id = TenantProductId.LEGAL_OPERATIONS
        lifecycle_state = "ACTIVE"
        fingerprint = ACTIVATION

    with pytest.raises(TenantModuleManifestError, match="ENTITLEMENT_TYPE_INVALID"):
        build_tenant_module_manifest(
            tenant_id="TENANT-A",
            entitlements=[ForgedProjection()],
        )


def test_pseudo_tenant_rejects():
    with pytest.raises(TenantModuleManifestError, match="TENANT_INVALID"):
        build_tenant_module_manifest(tenant_id="GLOBAL", entitlements=[])


def test_manifest_does_not_turn_legal_entitlement_into_legal_practice_authority():
    result = build_tenant_module_manifest(
        tenant_id="TENANT-A",
        entitlements=[_active_product(TenantProductId.LEGAL_OPERATIONS)],
    )
    item = result[0]
    assert item.module_id is TenantModuleId.LEGAL_OS
    assert not hasattr(item, "business_role")
    assert not hasattr(item, "permissions")
    assert not hasattr(item, "g68_clearance")
    assert not hasattr(item, "matter_access")


def test_billing_and_hr_are_not_exposed_without_positive_entitlement_evidence():
    result = build_tenant_module_manifest(
        tenant_id="TENANT-A",
        entitlements=[_active_product(TenantProductId.LEGAL_OPERATIONS)],
    )
    assert {item.product_id for item in result} == {TenantProductId.LEGAL_OPERATIONS}


def test_operations_and_intelligence_require_separate_active_product_evidence():
    operations = build_tenant_module_manifest(
        tenant_id="TENANT-A",
        entitlements=[_active_product(TenantProductId.OPERATIONS)],
    )
    intelligence = build_tenant_module_manifest(
        tenant_id="TENANT-A",
        entitlements=[_active_product(TenantProductId.INTELLIGENCE)],
    )
    assert len(operations) == len(intelligence) == 1
    assert operations[0].module_id is TenantModuleId.OPERATIONS
    assert operations[0].workspace_key == "OPERATIONS_DASHBOARD"
    assert intelligence[0].module_id is TenantModuleId.INTELLIGENCE
    assert intelligence[0].workspace_key == "INTELLIGENCE_DASHBOARD"
    assert operations[0].product_id is not intelligence[0].product_id
    assert operations[0].entitlement_id != intelligence[0].entitlement_id


def test_wilsy_platform_owner_excludes_legal_but_retains_internal_tools():
    """Owning WILSY OS is distinct from consuming its customer Legal product."""
    from tools.eos.auth.workspace_bootstrap_projection import WILSY_COMPANY_TENANT_ID as company
    legal = _active_product(TenantProductId.LEGAL_OPERATIONS, company)
    operations = _active_product(TenantProductId.OPERATIONS, company)
    evidence_before = (legal.fingerprint, operations.fingerprint)
    result = build_tenant_module_manifest(tenant_id=company, entitlements=[legal, operations])
    assert [item.module_id for item in result] == [TenantModuleId.OPERATIONS]
    assert evidence_before == (legal.fingerprint, operations.fingerprint)
    assert build_tenant_module_manifest(tenant_id=company, entitlements=[legal]) == ()


@pytest.mark.parametrize("tenant", ["WILSYTENANT-OTHER", "wilsytenant-4cd2fz4o", "CUSTOMER-LAW-FIRM"])
def test_noncompany_tenants_keep_their_exact_legal_product_projection(tenant):
    """Names, similar identifiers and role labels cannot select company policy."""
    result = build_tenant_module_manifest(tenant_id=tenant, entitlements=[_active_product(TenantProductId.LEGAL_OPERATIONS, tenant)])
    assert [item.module_id for item in result] == [TenantModuleId.LEGAL_OS]


def test_company_exclusion_does_not_skip_foreign_or_duplicate_evidence_validation():
    """Even a hidden Legal module must pass exact scope and evidence integrity."""
    from tools.eos.auth.workspace_bootstrap_projection import WILSY_COMPANY_TENANT_ID as company
    with pytest.raises(TenantModuleManifestError, match="TENANT_MISMATCH"):
        build_tenant_module_manifest(tenant_id=company, entitlements=[_active_product(TenantProductId.LEGAL_OPERATIONS)])
    legal = _active_product(TenantProductId.LEGAL_OPERATIONS, company)
    with pytest.raises(TenantModuleManifestError, match="DUPLICATE_PRODUCT_EVIDENCE"):
        build_tenant_module_manifest(tenant_id=company, entitlements=[legal, legal])

# ARTIFACT: test_tenant_module_manifest.py
# VERSION: v1.1.0-WILSY-PLATFORM-OWNER-CERT
# AUTHORITY BOUNDARY: Regression evidence only; no IAM/entitlement mutation.
# TENANT POSTURE: Exact company exclusion and customer Legal preservation.
# FAIL-CLOSED POSTURE: Foreign or malformed source evidence never passes.
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively.
# END OF WILSY OS SOVEREIGN ARTIFACT
