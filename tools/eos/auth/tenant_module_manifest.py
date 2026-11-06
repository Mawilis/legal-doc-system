"""WILSY OS tenant module manifest and entitlement projection.

TITLE: Tenant Module Manifest
VERSION: v1.0.0-EOS-TENANT-MODULE-MANIFEST
AUTHORITY: Read-only presentation projection over canonical product entitlements.
PURPOSE: Describe stable WILSY OS modules and expose only modules backed by
         exact ACTIVE tenant-product entitlement evidence.

SECURITY BOUNDARY:
    Product entitlement proves tenant product availability only. This manifest
    does not grant principal capacity, IAM permissions, route admission, Legal
    Practice authority, resource access or financial execution. Every module API
    and resource operation must independently authorize the current principal.

INPUT BOUNDARY:
    Only canonical domain objects returned by server-side entitlement authorities
    are accepted. Never hydrate this projection from browser/client-supplied
    entitlement JSON. Tenant membership and business capacity remain independent
    workspace-bootstrap conjuncts.
"""
from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum
import re
from typing import Final, Iterable

from tools.eos.crm.domain.crm_core_entitlement import (
    CRM_CORE_FEATURE_ID,
    CrmCoreEntitlement,
    CrmCoreEntitlementState,
)
from tools.eos.saas.domain.tenant_product_entitlement import (
    TenantProductEntitlement,
    TenantProductEntitlementState,
)
from tools.eos.saas.entitlement.product_catalogue import (
    TenantProductId,
    get_tenant_product,
)


VERSION: Final[str] = "v1.0.0-EOS-TENANT-MODULE-MANIFEST"
_SHA3: Final[re.Pattern[str]] = re.compile(r"^[0-9a-f]{128}$")


class TenantModuleManifestError(ValueError):
    """Fail-closed module manifest contract error."""


class TenantModuleId(StrEnum):
    LEGAL_OS = "LEGAL_OS"
    BILLING = "BILLING"
    CRM = "CRM"
    PEOPLE = "PEOPLE"


@dataclass(frozen=True, slots=True)
class TenantModuleDescriptor:
    """Global module metadata; contains no tenant or user authorization state."""

    module_id: TenantModuleId
    product_id: TenantProductId
    label: str
    workspace_key: str
    navigation_group: str
    icon_key: str
    description: str


@dataclass(frozen=True, slots=True)
class TenantModuleAvailability:
    """Minimal tenant-scoped browser projection of positive product evidence."""

    module_id: TenantModuleId
    product_id: TenantProductId
    label: str
    workspace_key: str
    navigation_group: str
    icon_key: str
    entitlement_id: str
    entitlement_revision: int
    entitlement_fingerprint: str


_MODULES: Final[tuple[TenantModuleDescriptor, ...]] = (
    TenantModuleDescriptor(
        TenantModuleId.LEGAL_OS,
        TenantProductId.LEGAL_OPERATIONS,
        "Legal OS",
        get_tenant_product(TenantProductId.LEGAL_OPERATIONS).workspace_key,
        "PROFESSIONAL_SERVICES",
        "scale",
        "Legal operations and professional practice workspace.",
    ),
    TenantModuleDescriptor(
        TenantModuleId.BILLING,
        TenantProductId.BILLING,
        "Billing",
        get_tenant_product(TenantProductId.BILLING).workspace_key,
        "BUSINESS_OPERATIONS",
        "receipt",
        "Tenant billing and commercial evidence workspace.",
    ),
    TenantModuleDescriptor(
        TenantModuleId.CRM,
        TenantProductId.CRM,
        "CRM",
        get_tenant_product(TenantProductId.CRM).workspace_key,
        "CUSTOMER_OPERATIONS",
        "users",
        "Customer, account and relationship operations workspace.",
    ),
    TenantModuleDescriptor(
        TenantModuleId.PEOPLE,
        TenantProductId.HR,
        "People",
        get_tenant_product(TenantProductId.HR).workspace_key,
        "PEOPLE_OPERATIONS",
        "users-round",
        "People and workforce operations workspace.",
    ),
)
_MODULE_BY_PRODUCT: Final[dict[TenantProductId, TenantModuleDescriptor]] = {
    module.product_id: module for module in _MODULES
}


def list_tenant_module_descriptors() -> tuple[TenantModuleDescriptor, ...]:
    """Return stable global module metadata, not tenant availability."""
    return _MODULES


def _tenant_text(value: object) -> str:
    if not isinstance(value, str) or not value or value != value.strip():
        raise TenantModuleManifestError("MODULE_MANIFEST_TENANT_INVALID")
    if value.casefold() in {"default", "global", "root", "master", "*"}:
        raise TenantModuleManifestError("MODULE_MANIFEST_TENANT_INVALID")
    return value


def _revision(value: object) -> int:
    if isinstance(value, bool) or not isinstance(value, int) or value < 0:
        raise TenantModuleManifestError("MODULE_MANIFEST_REVISION_INVALID")
    return value


def _fingerprint(value: object) -> str:
    if not isinstance(value, str) or _SHA3.fullmatch(value) is None:
        raise TenantModuleManifestError("MODULE_MANIFEST_FINGERPRINT_INVALID")
    return value


def _availability_from_product_entitlement(
    tenant_id: str,
    entitlement: TenantProductEntitlement,
) -> TenantModuleAvailability | None:
    if entitlement.tenant_id != tenant_id:
        raise TenantModuleManifestError("MODULE_MANIFEST_TENANT_MISMATCH")
    if entitlement.lifecycle_state is not TenantProductEntitlementState.ACTIVE:
        return None

    try:
        product_id = TenantProductId(entitlement.product_id)
    except (TypeError, ValueError) as error:
        raise TenantModuleManifestError("MODULE_MANIFEST_PRODUCT_INVALID") from error

    descriptor = get_tenant_product(product_id)
    if entitlement.product_catalogue_fingerprint != descriptor.fingerprint:
        raise TenantModuleManifestError("MODULE_MANIFEST_CATALOGUE_BINDING_INVALID")

    fingerprint = _fingerprint(entitlement.fingerprint)
    revision = _revision(entitlement.lifecycle_revision)
    module = _MODULE_BY_PRODUCT[product_id]
    return TenantModuleAvailability(
        module_id=module.module_id,
        product_id=product_id,
        label=module.label,
        workspace_key=module.workspace_key,
        navigation_group=module.navigation_group,
        icon_key=module.icon_key,
        entitlement_id=entitlement.entitlement_id,
        entitlement_revision=revision,
        entitlement_fingerprint=fingerprint,
    )


def _availability_from_crm_entitlement(
    tenant_id: str,
    entitlement: CrmCoreEntitlement,
) -> TenantModuleAvailability | None:
    if entitlement.tenant_id != tenant_id:
        raise TenantModuleManifestError("MODULE_MANIFEST_TENANT_MISMATCH")
    if entitlement.feature_id != CRM_CORE_FEATURE_ID:
        raise TenantModuleManifestError("MODULE_MANIFEST_CRM_FEATURE_INVALID")
    if entitlement.lifecycle_state is not CrmCoreEntitlementState.ACTIVE:
        return None

    fingerprint = _fingerprint(entitlement.fingerprint)
    revision = _revision(entitlement.lifecycle_revision)
    module = _MODULE_BY_PRODUCT[TenantProductId.CRM]
    return TenantModuleAvailability(
        module_id=module.module_id,
        product_id=module.product_id,
        label=module.label,
        workspace_key=module.workspace_key,
        navigation_group=module.navigation_group,
        icon_key=module.icon_key,
        entitlement_id=entitlement.entitlement_id,
        entitlement_revision=revision,
        entitlement_fingerprint=fingerprint,
    )


def build_tenant_module_manifest(
    *,
    tenant_id: str,
    entitlements: Iterable[TenantProductEntitlement | CrmCoreEntitlement],
) -> tuple[TenantModuleAvailability, ...]:
    """Project modules from canonical typed entitlement domain objects only.

    The caller must obtain these objects from the canonical server-side
    entitlement registry/resolver after authenticating and resolving the exact
    tenant. Missing, pending, suspended and revoked products are omitted.
    Unknown object types, duplicate product evidence, tenant mismatch and
    malformed integrity evidence fail closed.

    This is tenant-level product availability, not per-principal authorization.
    """
    tenant = _tenant_text(tenant_id)
    if isinstance(entitlements, (str, bytes)):
        raise TenantModuleManifestError("MODULE_MANIFEST_ENTITLEMENTS_INVALID")

    projected: dict[TenantProductId, TenantModuleAvailability] = {}
    try:
        iterator = iter(entitlements)
    except TypeError as error:
        raise TenantModuleManifestError(
            "MODULE_MANIFEST_ENTITLEMENTS_INVALID"
        ) from error

    for entitlement in iterator:
        if isinstance(entitlement, TenantProductEntitlement):
            item = _availability_from_product_entitlement(tenant, entitlement)
        elif isinstance(entitlement, CrmCoreEntitlement):
            item = _availability_from_crm_entitlement(tenant, entitlement)
        else:
            raise TenantModuleManifestError(
                "MODULE_MANIFEST_ENTITLEMENT_TYPE_INVALID"
            )

        if item is None:
            continue
        if item.product_id in projected:
            raise TenantModuleManifestError(
                "MODULE_MANIFEST_DUPLICATE_PRODUCT_EVIDENCE"
            )
        projected[item.product_id] = item

    return tuple(
        projected[descriptor.product_id]
        for descriptor in _MODULES
        if descriptor.product_id in projected
    )


__all__ = [
    "VERSION",
    "TenantModuleAvailability",
    "TenantModuleDescriptor",
    "TenantModuleId",
    "TenantModuleManifestError",
    "build_tenant_module_manifest",
    "list_tenant_module_descriptors",
]

# PRESENTATION ONLY: no IAM, route, matter, payment or execution authority
# LEGAL OS: tenant entitlement does not imply Legal Practice capacity or G68 clearance
# COMMERCIAL STATE: only typed canonical product-entitlement objects are accepted
# END OF WILSY OS TENANT MODULE MANIFEST
