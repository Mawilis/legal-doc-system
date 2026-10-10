"""WILSY OS pure Legal Operations product-availability projection.

TITLE: Legal Product Availability Projection
VERSION: v1.0.0-D22B5-LEGAL-PRODUCT-AVAILABILITY-PROJECTION
AUTHORITY: Wilsy OS Core Governance
EPITOME: Project whether the exact tenant-level Legal Operations entitlement is
         currently ACTIVE without granting principal, route, workspace,
         commercial, payment, execution, or settlement authority.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tools/eos/saas/entitlement/legal_product_availability_projection.py
COLLABORATION / OWNERSHIP: D22A owns product identity and workspace description;
                            D22B1 owns lifecycle meaning; D22B2 owns durable
                            currentness; D22B3 owns deterministic lineage IDs.
                            This module owns only the bounded read projection.
CERTIFICATION / UPDATE DATE: 2026-10-10
CHANGELOG: v1.0.0-D22B5-LEGAL-PRODUCT-AVAILABILITY-PROJECTION establishes the
           first server-owned, Legal-only availability projection with lawful
           absence, integrity reproof, and fail-closed dependency handling.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2; ISO 27001.
SECURITY / PRIVACY POSTURE: Projects opaque tenant and entitlement identities
                             only; no principal, permission, subscription,
                             pricing, payment, or personal information.
TENANT BOUNDARY: The caller supplies one canonical tenant identity; the
                 entitlement identity is derived server-side and hydrated only
                 through the exact tenant-scoped D22B2 current-read primitive.
AUTHORITY BOUNDARY: Descriptive Legal product availability only. Availability
                    is not IAM, route, workspace, Legal-acceptance, practice,
                    AI, subscription, CRM, Billing, or HR authority.
TRANSACTION BOUNDARY: The caller owns the active transaction and all retry,
                      commit, and abort decisions. The exact session is only
                      forwarded unchanged to D22B2.
FINANCIAL AUTHORITY BOUNDARY: No billing, payment, execution, paid, or settlement
                              truth. Kennel EOS remains exclusive.
FAIL-CLOSED DECLARATION: Invalid input, catalogue drift, corrupted hydration,
                         transaction failure, retry signals, conflicts, and
                         persistence outages reject; exact absence alone is
                         projected as unavailable.
"""
from __future__ import annotations

from dataclasses import dataclass
import re
from typing import Any, Final, NoReturn, cast

from tools.eos.saas.domain.tenant_product_entitlement import (
    TenantProductEntitlementState,
)
from tools.eos.saas.entitlement.product_catalogue import (
    TenantProductId,
    get_tenant_product,
)
from tools.eos.saas.entitlement.tenant_product_entitlement_composer import (
    derive_tenant_product_entitlement_id,
)
from tools.eos.saas.entitlement.tenant_product_entitlement_registry import (
    TenantProductEntitlementRegistryError,
    TenantProductEntitlementRegistryNotFoundError,
    get_current,
)


VERSION: Final[str] = "v1.0.0-D22B5-LEGAL-PRODUCT-AVAILABILITY-PROJECTION"
_TENANT_ID: Final[re.Pattern[str]] = re.compile(
    r"^[A-Za-z0-9][A-Za-z0-9._:-]{0,159}$"
)
_FORBIDDEN_TENANTS: Final[frozenset[str]] = frozenset(
    {"default", "global", "global_root", "root", "master", "*"}
)


class LegalProductAvailabilityProjectionError(RuntimeError):
    """Stable fail-closed projection error with no admission implication.

    The error describes an inability to establish the bounded projection. It
    never downgrades corruption or infrastructure failure into unavailability.
    """

    def __init__(self, code: str, message: str) -> None:
        """Create one bounded code/message pair for an internal caller."""
        self.code = code
        self.message = message
        super().__init__(f"{code}: {message}")


@dataclass(frozen=True, slots=True)
class LegalProductAvailabilityProjection:
    """Immutable evidence-backed Legal product availability description.

    This value carries no role, permission, admission, subscription, billing,
    payment, execution, settlement, CRM, Billing-product, or HR-product truth.
    """

    tenant_id: str
    product_id: TenantProductId
    workspace_key: str
    entitlement_id: str
    lifecycle_state: TenantProductEntitlementState | None
    available: bool


def _raise(code: str, message: str, cause: BaseException | None = None) -> NoReturn:
    """Raise one projection failure and preserve any dependency cause."""
    error = LegalProductAvailabilityProjectionError(code, message)
    if cause is None:
        raise error
    raise error from cause


def _tenant_id(value: object) -> str:
    """Require one bounded canonical tenant identity before any authority read."""
    if (
        not isinstance(value, str)
        or _TENANT_ID.fullmatch(value) is None
        or value.casefold() in _FORBIDDEN_TENANTS
    ):
        _raise(
            "D22B5_TENANT_ID_INVALID",
            "tenant_id must be canonical non-empty tenant text",
        )
    return value


def resolve_legal_product_availability(
    tenant_id: str,
    history_collection: Any,
    current_collection: Any,
    *,
    session: Any,
) -> LegalProductAvailabilityProjection:
    """Resolve current tenant-level Legal Operations product availability.

    @description Derives all product and entitlement identity server-side,
        forwards the caller's exact persistence dependencies to D22B2, and
        maps only ACTIVE to available.
    @collaboration D22A catalogue, D22B3 composer identity, D22B2 registry, and
        D22B1 lifecycle are consumed without duplicating their authority.
    @institutional Keeps product availability distinct from IAM, workspace
        admission, commercial authority, and Kennel EOS financial execution.
    @param tenant_id Canonical tenant scope; never a principal or workspace key.
    @param history_collection Exact D22B2 immutable-history collection handle.
    @param current_collection Exact D22B2 current-pointer collection handle.
    @param session Exact active caller-owned Mongo transaction session.
    @returns Immutable descriptive Legal product availability evidence.
    @raises LegalProductAvailabilityProjectionError on invalid input, catalogue
        drift, authority mismatch, corruption, transaction failure, retry
        requirement, conflict, or persistence outage.
    """
    tenant = _tenant_id(tenant_id)
    try:
        descriptor = get_tenant_product(TenantProductId.LEGAL_OPERATIONS)
        if (
            descriptor.product_id is not TenantProductId.LEGAL_OPERATIONS
            or not isinstance(descriptor.workspace_key, str)
            or not descriptor.workspace_key
            or descriptor.workspace_key != descriptor.workspace_key.strip()
        ):
            _raise(
                "D22B5_CATALOGUE_AUTHORITY_INVALID",
                "canonical Legal Operations descriptor is inconsistent",
            )
        entitlement_id = derive_tenant_product_entitlement_id(
            tenant,
            TenantProductId.LEGAL_OPERATIONS,
        )
    except LegalProductAvailabilityProjectionError:
        raise
    except Exception as error:
        _raise(
            "D22B5_CANONICAL_AUTHORITY_UNAVAILABLE",
            "canonical Legal product authority could not be resolved",
            error,
        )

    try:
        entitlement = get_current(
            tenant,
            entitlement_id,
            history_collection,
            current_collection,
            session=session,
        )
    except TenantProductEntitlementRegistryNotFoundError:
        return LegalProductAvailabilityProjection(
            tenant_id=tenant,
            product_id=TenantProductId.LEGAL_OPERATIONS,
            workspace_key=descriptor.workspace_key,
            entitlement_id=entitlement_id,
            lifecycle_state=None,
            available=False,
        )
    except TenantProductEntitlementRegistryError as error:
        _raise(
            "D22B5_REGISTRY_AUTHORITY_FAILURE",
            "current Legal product entitlement could not be established",
            error,
        )

    try:
        authority_matches = (
            entitlement.tenant_id == tenant
            and entitlement.entitlement_id == entitlement_id
            and entitlement.product_id is TenantProductId.LEGAL_OPERATIONS
            and type(entitlement.lifecycle_state) is TenantProductEntitlementState
        )
    except (AttributeError, TypeError) as error:
        _raise(
            "D22B5_HYDRATED_AUTHORITY_INVALID",
            "hydrated entitlement does not expose canonical authority fields",
            error,
        )
    if not authority_matches:
        _raise(
            "D22B5_HYDRATED_AUTHORITY_MISMATCH",
            "hydrated entitlement does not match requested Legal authority",
        )

    lifecycle_state = cast(TenantProductEntitlementState, entitlement.lifecycle_state)
    return LegalProductAvailabilityProjection(
        tenant_id=tenant,
        product_id=TenantProductId.LEGAL_OPERATIONS,
        workspace_key=descriptor.workspace_key,
        entitlement_id=entitlement_id,
        lifecycle_state=lifecycle_state,
        available=lifecycle_state is TenantProductEntitlementState.ACTIVE,
    )


__all__ = [
    "LegalProductAvailabilityProjection",
    "LegalProductAvailabilityProjectionError",
    "VERSION",
    "resolve_legal_product_availability",
]

# ARTIFACT: legal_product_availability_projection.py
# VERSION: v1.0.0-D22B5-LEGAL-PRODUCT-AVAILABILITY-PROJECTION
# AUTHORITY BOUNDARY: descriptive Legal product availability only; no IAM, admission, subscription, billing, payment, execution, or settlement authority
# TENANT POSTURE: exact caller tenant plus server-derived Legal entitlement identity through D22B2 currentness
# FAIL-CLOSED POSTURE: only exact absence becomes unavailable; drift, corruption, transaction failure, retry and persistence outage reject
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively
# END OF WILSY OS SOVEREIGN ARTIFACT
