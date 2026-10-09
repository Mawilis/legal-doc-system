"""WILSY OS canonical tenant-selectable product catalogue.

TITLE: Tenant Product Catalogue
VERSION: v1.0.0-D22A-TENANT-PRODUCT-CATALOGUE
AUTHORITY: Wilsy OS Core Governance
EPITOME: Own the immutable closed catalogue of tenant-selectable WILSY OS
         product modules without granting entitlement, IAM authority,
         subscription, payment or financial-execution truth.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tools/eos/saas/entitlement/product_catalogue.py
COLLABORATION / OWNERSHIP: Python EOS owns product identity/catalogue truth.
                            PlanRegistry owns base commercial plan truth;
                            SubscriptionRegistry owns subscription lifecycle;
                            tenant product entitlement is a separate future
                            authority; WILSY AI and Tenant Branding remain
                            separate VAS domains; IAM owns principal authority.
CERTIFICATION / UPDATE DATE: 2026-09-24
CHANGELOG: v1.0.0-D22A-TENANT-PRODUCT-CATALOGUE establishes the first closed
           tenant-selectable product catalogue for Legal Operations, Billing,
           CRM and HR. It intentionally excludes WILSY AI and Tenant Branding
           because those are value-added-service authorities with independent
           commercial/entitlement lifecycles. "Full Enterprise" is not a
           product and no wildcard product exists.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2; ISO 27001.
SECURITY / PRIVACY POSTURE: Pure immutable in-process catalogue; no tenant
                             records, credentials, network, filesystem,
                             provider clients, MongoDB or KMS access.
TENANT BOUNDARY: Product descriptors are global catalogue facts only. They do
                 not prove a tenant purchased, activated, or may access a
                 product.
AUTHORITY BOUNDARY: Product identity, display metadata and dependency
                    declaration only. No tenant entitlement, role, permission,
                    route admission, workspace access or VAS activation.
FINANCIAL AUTHORITY BOUNDARY: No price, invoice, charge, payment, execution or
                               settlement truth. Kennel EOS remains exclusive.
FAIL-CLOSED DECLARATION: Unknown products, duplicate identifiers, descriptor
                         drift, undeclared dependencies, VAS leakage and
                         fingerprint drift reject deterministically.
"""
from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from enum import Enum
import hashlib
import hmac
import json
from typing import Any, Final, cast


VERSION: Final[str] = "v1.0.0-D22A-TENANT-PRODUCT-CATALOGUE"
SCHEMA: Final[str] = "WILSY-TENANT-PRODUCT-CATALOGUE/V1"
CATALOGUE_IDENTITY: Final[str] = "WILSY_TENANT_PRODUCT_CATALOGUE"


class TenantProductCatalogueError(ValueError):
    """Raised when a tenant-product catalogue descriptor violates the contract."""


class TenantProductId(str, Enum):
    """Closed identifiers for tenant-selectable WILSY OS product modules."""

    LEGAL_OPERATIONS = "LEGAL_OPERATIONS"
    BILLING = "BILLING"
    CRM = "CRM"
    HR = "HR"


_CANONICAL_INPUTS: Final[dict[TenantProductId, dict[str, object]]] = {
    TenantProductId.LEGAL_OPERATIONS: {
        "label": "Legal Operations",
        "workspace_key": "LEGAL_DASHBOARD",
        "required_products": (),
        "description": "Legal matter, instruction, process-service, return and legal-operations workspace.",
    },
    TenantProductId.BILLING: {
        "label": "Billing",
        "workspace_key": "BILLING_HUB",
        "required_products": (),
        "description": "Tenant billing, invoicing and commercial evidence workspace; no financial execution authority.",
    },
    TenantProductId.CRM: {
        "label": "CRM",
        "workspace_key": "CRM_DASHBOARD",
        "required_products": (),
        "description": "Tenant customer, account, lead, deal and relationship operations workspace.",
    },
    TenantProductId.HR: {
        "label": "HR",
        "workspace_key": "HR_DASHBOARD",
        "required_products": (),
        "description": "Tenant people, workforce and human-resources operations workspace.",
    },
}

_SERIALIZED_FIELDS: Final[frozenset[str]] = frozenset(
    {
        "schema",
        "catalogue_identity",
        "catalogue_version",
        "product_id",
        "label",
        "workspace_key",
        "required_products",
        "description",
        "fingerprint",
    }
)


def _text(value: object, code: str) -> str:
    """Return one exact non-empty text value or fail closed."""
    if not isinstance(value, str) or not value or value != value.strip():
        raise TenantProductCatalogueError(code)
    return value


def _digest(payload: Mapping[str, object]) -> str:
    """Return lowercase SHA3-512 over deterministic UTF-8 JSON."""
    encoded = json.dumps(
        dict(payload),
        ensure_ascii=False,
        allow_nan=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")
    return hashlib.sha3_512(encoded).hexdigest()


def _canonical_payload(
    *,
    product_id: TenantProductId,
    label: str,
    workspace_key: str,
    required_products: tuple[TenantProductId, ...],
    description: str,
) -> dict[str, object]:
    """Return one product descriptor excluding the derived fingerprint."""
    return {
        "schema": SCHEMA,
        "catalogue_identity": CATALOGUE_IDENTITY,
        "catalogue_version": VERSION,
        "product_id": product_id.value,
        "label": label,
        "workspace_key": workspace_key,
        "required_products": [item.value for item in required_products],
        "description": description,
    }


def _dependencies(value: object) -> tuple[TenantProductId, ...]:
    """Validate exact required-product identifiers without inference."""
    if isinstance(value, str) or not isinstance(value, (tuple, list)):
        raise TenantProductCatalogueError("D22A_DEPENDENCIES_INVALID")
    try:
        items = tuple(TenantProductId(item) for item in value)
    except (TypeError, ValueError) as error:
        raise TenantProductCatalogueError("D22A_DEPENDENCIES_INVALID") from error
    if len(set(items)) != len(items):
        raise TenantProductCatalogueError("D22A_DEPENDENCIES_INVALID")
    return items


@dataclass(frozen=True, slots=True)
class TenantProductDescriptor:
    """Immutable product-catalogue fact with deterministic integrity evidence."""

    product_id: TenantProductId | str
    label: str
    workspace_key: str
    required_products: tuple[TenantProductId | str, ...]
    description: str
    schema: str = SCHEMA
    catalogue_identity: str = CATALOGUE_IDENTITY
    catalogue_version: str = VERSION
    fingerprint: str = ""

    def __post_init__(self) -> None:
        """Validate exact canonical values and derive the SHA3-512 seal."""
        try:
            product_id = TenantProductId(self.product_id)
        except (TypeError, ValueError) as error:
            raise TenantProductCatalogueError("D22A_UNKNOWN_PRODUCT") from error

        if (
            self.schema != SCHEMA
            or self.catalogue_identity != CATALOGUE_IDENTITY
            or self.catalogue_version != VERSION
        ):
            raise TenantProductCatalogueError("D22A_IDENTITY_INVALID")

        label = _text(self.label, "D22A_LABEL_INVALID")
        workspace_key = _text(self.workspace_key, "D22A_WORKSPACE_KEY_INVALID")
        description = _text(self.description, "D22A_DESCRIPTION_INVALID")
        required_products = _dependencies(self.required_products)

        if product_id in required_products:
            raise TenantProductCatalogueError("D22A_SELF_DEPENDENCY_INVALID")

        canonical = _CANONICAL_INPUTS[product_id]
        if (
            label != canonical["label"]
            or workspace_key != canonical["workspace_key"]
            or required_products != canonical["required_products"]
            or description != canonical["description"]
        ):
            raise TenantProductCatalogueError("D22A_CALLER_VALUE_OVERRIDE")

        payload = _canonical_payload(
            product_id=product_id,
            label=label,
            workspace_key=workspace_key,
            required_products=required_products,
            description=description,
        )
        digest = _digest(payload)

        if self.fingerprint and (
            not isinstance(self.fingerprint, str)
            or not hmac.compare_digest(self.fingerprint, digest)
        ):
            raise TenantProductCatalogueError("D22A_FINGERPRINT_MISMATCH")

        object.__setattr__(self, "product_id", product_id)
        object.__setattr__(self, "label", label)
        object.__setattr__(self, "workspace_key", workspace_key)
        object.__setattr__(self, "required_products", required_products)
        object.__setattr__(self, "description", description)
        object.__setattr__(self, "fingerprint", digest)

    def to_dict(self) -> dict[str, object]:
        """Return the exact detached descriptor suitable for evidence transport."""
        payload = _canonical_payload(
            product_id=cast(TenantProductId, self.product_id),
            label=self.label,
            workspace_key=self.workspace_key,
            required_products=cast(tuple[TenantProductId, ...], self.required_products),
            description=self.description,
        )
        payload["fingerprint"] = self.fingerprint
        return payload


def get_tenant_product(product_id: TenantProductId | str) -> TenantProductDescriptor:
    """Return one exact immutable product descriptor.

    The descriptor is catalogue truth only and cannot establish tenant
    entitlement, subscription, user authority or workspace admission.
    """
    try:
        normalized = TenantProductId(product_id)
    except (TypeError, ValueError) as error:
        raise TenantProductCatalogueError("D22A_UNKNOWN_PRODUCT") from error
    return _CATALOGUE[normalized]


def list_tenant_products() -> tuple[TenantProductDescriptor, ...]:
    """Return the exact closed tenant-selectable product catalogue."""
    return tuple(_CATALOGUE[item] for item in TenantProductId)


def hydrate_tenant_product(
    payload: Mapping[str, object],
) -> TenantProductDescriptor:
    """Strictly hydrate one descriptor and recompute canonical integrity."""
    if not isinstance(payload, Mapping) or set(payload) != _SERIALIZED_FIELDS:
        raise TenantProductCatalogueError("D22A_DESCRIPTOR_SCHEMA_INVALID")
    raw: Mapping[str, Any] = payload
    required = raw["required_products"]
    if not isinstance(required, list):
        raise TenantProductCatalogueError("D22A_DESCRIPTOR_SCHEMA_INVALID")
    return TenantProductDescriptor(
        product_id=raw["product_id"],
        label=cast(str, raw["label"]),
        workspace_key=cast(str, raw["workspace_key"]),
        required_products=tuple(cast(list[str], required)),
        description=cast(str, raw["description"]),
        schema=cast(str, raw["schema"]),
        catalogue_identity=cast(str, raw["catalogue_identity"]),
        catalogue_version=cast(str, raw["catalogue_version"]),
        fingerprint=cast(str, raw["fingerprint"]),
    )


_CATALOGUE: Final[dict[TenantProductId, TenantProductDescriptor]] = {
    product_id: TenantProductDescriptor(
        product_id=product_id,
        label=cast(str, values["label"]),
        workspace_key=cast(str, values["workspace_key"]),
        required_products=cast(tuple[TenantProductId, ...], values["required_products"]),
        description=cast(str, values["description"]),
    )
    for product_id, values in _CANONICAL_INPUTS.items()
}

__all__ = [
    "CATALOGUE_IDENTITY",
    "SCHEMA",
    "TenantProductCatalogueError",
    "TenantProductDescriptor",
    "TenantProductId",
    "VERSION",
    "get_tenant_product",
    "hydrate_tenant_product",
    "list_tenant_products",
]

# ARTIFACT: product_catalogue.py
# VERSION: v1.0.0-D22A-TENANT-PRODUCT-CATALOGUE
# AUTHORITY BOUNDARY: product catalogue description only; no tenant entitlement or IAM authority
# TENANT POSTURE: global catalogue facts only; no tenant identity is inferred or mutated
# FAIL-CLOSED POSTURE: unknown products, descriptor drift and VAS leakage reject
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively
# END OF WILSY OS SOVEREIGN ARTIFACT
