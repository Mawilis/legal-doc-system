"""WILSY OS explicit commercial-offer catalogue.

TITLE: Commercial Offer Catalogue
VERSION: v1.0.0-WILSY-COMMERCIAL-OFFER-CATALOGUE
AUTHORITY: Global commercial packaging metadata only.
PURPOSE: Describe standalone and explicitly composed multi-product offers while
         keeping product identity, subscription lifecycle, entitlement issuance,
         IAM, pricing and financial execution in their existing authorities.

This catalogue is deliberately non-transactional. An offer is not a product,
subscription, purchase, entitlement, activation, workspace admission or grant of
permission. Bundle membership never creates implicit product dependencies or
IAM permissions. Every product in an offer remains subject to its own canonical
entitlement authority. Pricing, billing periods, invoices, payment, settlement
and financial execution are intentionally absent.

Commercial model values describe packaging forms that the commercial platform
may support; their presence does not mean that a particular model has been
priced, contracted, activated or certified for a tenant.
"""
from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from enum import StrEnum
import hashlib
import hmac
import json
from typing import Any, Final, cast

from tools.eos.saas.entitlement.product_catalogue import (
    TenantProductCatalogueError,
    TenantProductId,
    get_tenant_product,
    list_tenant_products,
)


VERSION: Final[str] = "v1.0.0-WILSY-COMMERCIAL-OFFER-CATALOGUE"
SCHEMA: Final[str] = "WILSY-COMMERCIAL-OFFER-CATALOGUE/V1"
CATALOGUE_IDENTITY: Final[str] = "WILSY_COMMERCIAL_OFFER_CATALOGUE"


class CommercialOfferCatalogueError(ValueError):
    """Raised when an offer descriptor violates the closed catalogue contract."""


class CommercialOfferKind(StrEnum):
    """Explicit composition shape; a bundle is not a product identifier."""

    STANDALONE = "STANDALONE"
    BUNDLE = "BUNDLE"


class CommercialModel(StrEnum):
    """Commercial packaging forms, not subscription or payment state."""

    RECURRING_SUBSCRIPTION = "RECURRING_SUBSCRIPTION"
    PERPETUAL_LICENSE = "PERPETUAL_LICENSE"
    USAGE_BASED = "USAGE_BASED"
    ENTERPRISE_AGREEMENT = "ENTERPRISE_AGREEMENT"
    CUSTOM_CONTRACT = "CUSTOM_CONTRACT"


class CommercialOfferId(StrEnum):
    """Closed offer identifiers distinct from TenantProductId."""

    LEGAL_OPERATIONS = "LEGAL_OPERATIONS_STANDALONE"
    BILLING = "BILLING_STANDALONE"
    CRM = "CRM_STANDALONE"
    HR = "HR_STANDALONE"
    OPERATIONS = "OPERATIONS_STANDALONE"
    INTELLIGENCE = "INTELLIGENCE_STANDALONE"
    POS = "POS_STANDALONE"
    PROFESSIONAL_SERVICES = "PROFESSIONAL_SERVICES_BUNDLE"
    BUSINESS_OPERATIONS = "BUSINESS_OPERATIONS_BUNDLE"
    ENTERPRISE_OPERATIONS = "ENTERPRISE_OPERATIONS_BUNDLE"


_ALL_MODELS: Final[tuple[CommercialModel, ...]] = tuple(CommercialModel)
_CANONICAL_OFFERS: Final[dict[CommercialOfferId, dict[str, object]]] = {
    CommercialOfferId.LEGAL_OPERATIONS: {
        "label": "Legal Operations",
        "kind": CommercialOfferKind.STANDALONE,
        "product_ids": (TenantProductId.LEGAL_OPERATIONS,),
        "description": "Standalone Legal Operations product offer.",
    },
    CommercialOfferId.BILLING: {
        "label": "Billing",
        "kind": CommercialOfferKind.STANDALONE,
        "product_ids": (TenantProductId.BILLING,),
        "description": "Standalone Billing product offer.",
    },
    CommercialOfferId.CRM: {
        "label": "CRM",
        "kind": CommercialOfferKind.STANDALONE,
        "product_ids": (TenantProductId.CRM,),
        "description": "Standalone CRM product offer.",
    },
    CommercialOfferId.HR: {
        "label": "HR",
        "kind": CommercialOfferKind.STANDALONE,
        "product_ids": (TenantProductId.HR,),
        "description": "Standalone HR product offer.",
    },
    CommercialOfferId.OPERATIONS: {
        "label": "Operations",
        "kind": CommercialOfferKind.STANDALONE,
        "product_ids": (TenantProductId.OPERATIONS,),
        "description": "Standalone Operations product offer.",
    },
    CommercialOfferId.INTELLIGENCE: {
        "label": "Intelligence",
        "kind": CommercialOfferKind.STANDALONE,
        "product_ids": (TenantProductId.INTELLIGENCE,),
        "description": "Standalone Intelligence product offer.",
    },
    CommercialOfferId.POS: {
        "label": "Point of Sale",
        "kind": CommercialOfferKind.STANDALONE,
        "product_ids": (TenantProductId.POS,),
        "description": "Standalone Point of Sale product offer; not included in existing bundles.",
    },
    CommercialOfferId.PROFESSIONAL_SERVICES: {
        "label": "Professional Services",
        "kind": CommercialOfferKind.BUNDLE,
        "product_ids": (
            TenantProductId.LEGAL_OPERATIONS,
            TenantProductId.CRM,
            TenantProductId.BILLING,
        ),
        "description": "Explicit Legal Operations, CRM and Billing product composition.",
    },
    CommercialOfferId.BUSINESS_OPERATIONS: {
        "label": "Business Operations",
        "kind": CommercialOfferKind.BUNDLE,
        "product_ids": (
            TenantProductId.CRM,
            TenantProductId.HR,
            TenantProductId.BILLING,
        ),
        "description": "Explicit CRM, HR and Billing product composition.",
    },
    CommercialOfferId.ENTERPRISE_OPERATIONS: {
        "label": "Enterprise Operations",
        "kind": CommercialOfferKind.BUNDLE,
        "product_ids": (
            TenantProductId.LEGAL_OPERATIONS,
            TenantProductId.BILLING,
            TenantProductId.CRM,
            TenantProductId.HR,
        ),
        "description": "Explicit composition of all four currently catalogued tenant products.",
    },
}

_SERIALIZED_FIELDS: Final[frozenset[str]] = frozenset({
    "schema",
    "catalogue_identity",
    "catalogue_version",
    "offer_id",
    "label",
    "kind",
    "product_ids",
    "commercial_models",
    "description",
    "fingerprint",
})


def _text(value: object, code: str) -> str:
    if not isinstance(value, str) or not value or value != value.strip():
        raise CommercialOfferCatalogueError(code)
    return value


def _models(value: object) -> tuple[CommercialModel, ...]:
    if isinstance(value, str) or not isinstance(value, (tuple, list)):
        raise CommercialOfferCatalogueError("OFFER_MODELS_INVALID")
    try:
        items = tuple(CommercialModel(item) for item in value)
    except (TypeError, ValueError) as error:
        raise CommercialOfferCatalogueError("OFFER_MODELS_INVALID") from error
    if not items or len(set(items)) != len(items):
        raise CommercialOfferCatalogueError("OFFER_MODELS_INVALID")
    return items


def _products(value: object) -> tuple[TenantProductId, ...]:
    if isinstance(value, str) or not isinstance(value, (tuple, list)):
        raise CommercialOfferCatalogueError("OFFER_PRODUCTS_INVALID")
    try:
        items = tuple(TenantProductId(item) for item in value)
    except (TypeError, ValueError) as error:
        raise CommercialOfferCatalogueError("OFFER_PRODUCTS_INVALID") from error
    if not items or len(set(items)) != len(items):
        raise CommercialOfferCatalogueError("OFFER_PRODUCTS_INVALID")
    return items


def _payload(
    *,
    offer_id: CommercialOfferId,
    label: str,
    kind: CommercialOfferKind,
    product_ids: tuple[TenantProductId, ...],
    commercial_models: tuple[CommercialModel, ...],
    description: str,
) -> dict[str, object]:
    return {
        "schema": SCHEMA,
        "catalogue_identity": CATALOGUE_IDENTITY,
        "catalogue_version": VERSION,
        "offer_id": offer_id.value,
        "label": label,
        "kind": kind.value,
        "product_ids": [item.value for item in product_ids],
        "commercial_models": [item.value for item in commercial_models],
        "description": description,
    }


def _digest(value: Mapping[str, object]) -> str:
    encoded = json.dumps(
        dict(value),
        ensure_ascii=False,
        allow_nan=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")
    return hashlib.sha3_512(encoded).hexdigest()


@dataclass(frozen=True, slots=True)
class CommercialOfferDescriptor:
    """Immutable explicit offer composition with deterministic integrity seal."""

    offer_id: CommercialOfferId | str
    label: str
    kind: CommercialOfferKind | str
    product_ids: tuple[TenantProductId | str, ...]
    commercial_models: tuple[CommercialModel | str, ...]
    description: str
    schema: str = SCHEMA
    catalogue_identity: str = CATALOGUE_IDENTITY
    catalogue_version: str = VERSION
    fingerprint: str = ""

    def __post_init__(self) -> None:
        try:
            offer_id = CommercialOfferId(self.offer_id)
            kind = CommercialOfferKind(self.kind)
        except (TypeError, ValueError) as error:
            raise CommercialOfferCatalogueError("OFFER_IDENTITY_INVALID") from error

        if (
            self.schema != SCHEMA
            or self.catalogue_identity != CATALOGUE_IDENTITY
            or self.catalogue_version != VERSION
        ):
            raise CommercialOfferCatalogueError("OFFER_CATALOGUE_IDENTITY_INVALID")

        label = _text(self.label, "OFFER_LABEL_INVALID")
        description = _text(self.description, "OFFER_DESCRIPTION_INVALID")
        product_ids = _products(self.product_ids)
        commercial_models = _models(self.commercial_models)

        if kind is CommercialOfferKind.STANDALONE and len(product_ids) != 1:
            raise CommercialOfferCatalogueError("OFFER_STANDALONE_CARDINALITY_INVALID")
        if kind is CommercialOfferKind.BUNDLE and len(product_ids) < 2:
            raise CommercialOfferCatalogueError("OFFER_BUNDLE_CARDINALITY_INVALID")

        # Bind each product to the canonical D22A catalogue. A bundle is only
        # an explicit offer composition; this loop issues no product authority.
        for product_id in product_ids:
            get_tenant_product(product_id)

        canonical = _CANONICAL_OFFERS[offer_id]
        if (
            label != canonical["label"]
            or kind is not canonical["kind"]
            or product_ids != canonical["product_ids"]
            or description != canonical["description"]
            or commercial_models != _ALL_MODELS
        ):
            raise CommercialOfferCatalogueError("OFFER_CALLER_VALUE_OVERRIDE")

        payload = _payload(
            offer_id=offer_id,
            label=label,
            kind=kind,
            product_ids=product_ids,
            commercial_models=commercial_models,
            description=description,
        )
        digest = _digest(payload)
        if self.fingerprint and (
            not isinstance(self.fingerprint, str)
            or not hmac.compare_digest(self.fingerprint, digest)
        ):
            raise CommercialOfferCatalogueError("OFFER_FINGERPRINT_MISMATCH")

        object.__setattr__(self, "offer_id", offer_id)
        object.__setattr__(self, "label", label)
        object.__setattr__(self, "kind", kind)
        object.__setattr__(self, "product_ids", product_ids)
        object.__setattr__(self, "commercial_models", commercial_models)
        object.__setattr__(self, "description", description)
        object.__setattr__(self, "fingerprint", digest)

    def to_dict(self) -> dict[str, object]:
        """Return a detached strict descriptor with no tenant/commercial state."""
        payload = _payload(
            offer_id=cast(CommercialOfferId, self.offer_id),
            label=self.label,
            kind=cast(CommercialOfferKind, self.kind),
            product_ids=cast(tuple[TenantProductId, ...], self.product_ids),
            commercial_models=cast(tuple[CommercialModel, ...], self.commercial_models),
            description=self.description,
        )
        payload["fingerprint"] = self.fingerprint
        return payload


def _descriptor(
    offer_id: CommercialOfferId,
    values: dict[str, object],
) -> CommercialOfferDescriptor:
    return CommercialOfferDescriptor(
        offer_id=offer_id,
        label=cast(str, values["label"]),
        kind=cast(CommercialOfferKind, values["kind"]),
        product_ids=cast(tuple[TenantProductId, ...], values["product_ids"]),
        commercial_models=_ALL_MODELS,
        description=cast(str, values["description"]),
    )


_CATALOGUE: Final[dict[CommercialOfferId, CommercialOfferDescriptor]] = {
    offer_id: _descriptor(offer_id, values)
    for offer_id, values in _CANONICAL_OFFERS.items()
}


def get_commercial_offer(
    offer_id: CommercialOfferId | str,
) -> CommercialOfferDescriptor:
    """Return one exact global offer descriptor; never an entitlement decision."""
    try:
        normalized = CommercialOfferId(offer_id)
    except (TypeError, ValueError) as error:
        raise CommercialOfferCatalogueError("OFFER_UNKNOWN") from error
    return _CATALOGUE[normalized]


def list_commercial_offers() -> tuple[CommercialOfferDescriptor, ...]:
    """Return the closed standalone and explicit bundle offer catalogue."""
    return tuple(_CATALOGUE[item] for item in CommercialOfferId)


def hydrate_commercial_offer(
    payload: Mapping[str, object],
) -> CommercialOfferDescriptor:
    """Strictly hydrate a descriptor and recompute its canonical fingerprint."""
    if not isinstance(payload, Mapping) or set(payload) != _SERIALIZED_FIELDS:
        raise CommercialOfferCatalogueError("OFFER_DESCRIPTOR_SCHEMA_INVALID")
    raw: Mapping[str, Any] = payload
    product_ids = raw["product_ids"]
    models = raw["commercial_models"]
    if not isinstance(product_ids, list) or not isinstance(models, list):
        raise CommercialOfferCatalogueError("OFFER_DESCRIPTOR_SCHEMA_INVALID")
    try:
        return CommercialOfferDescriptor(
            offer_id=cast(str, raw["offer_id"]),
            label=cast(str, raw["label"]),
            kind=cast(str, raw["kind"]),
            product_ids=tuple(cast(list[str], product_ids)),
            commercial_models=tuple(cast(list[str], models)),
            description=cast(str, raw["description"]),
            schema=cast(str, raw["schema"]),
            catalogue_identity=cast(str, raw["catalogue_identity"]),
            catalogue_version=cast(str, raw["catalogue_version"]),
            fingerprint=cast(str, raw["fingerprint"]),
        )
    except TenantProductCatalogueError as error:
        raise CommercialOfferCatalogueError("OFFER_PRODUCT_CATALOGUE_INVALID") from error


__all__ = [
    "CATALOGUE_IDENTITY",
    "CommercialModel",
    "CommercialOfferCatalogueError",
    "CommercialOfferDescriptor",
    "CommercialOfferId",
    "CommercialOfferKind",
    "SCHEMA",
    "VERSION",
    "get_commercial_offer",
    "hydrate_commercial_offer",
    "list_commercial_offers",
]

# AUTHORITY BOUNDARY: static offer composition only; no subscription, entitlement, IAM or workspace authority
# FINANCIAL BOUNDARY: no price, invoice, payment, settlement or execution truth
# BUNDLE RULE: every included product is explicit and remains independently entitled
# END OF WILSY OS COMMERCIAL OFFER CATALOGUE
