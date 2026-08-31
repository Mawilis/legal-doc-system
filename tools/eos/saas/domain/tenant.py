# -*- coding: utf-8 -*-
"""
===============================================================================
WILSY OS — SOVEREIGN OPERATING SYSTEM
TENANT DOMAIN — PROFILE SECTOR TRUTH
===============================================================================

TITLE:
    WILSY OS Tenant Domain

FILE:
    tools/eos/saas/domain/tenant.py

VERSION:
    v1.4.0-TENANT-PROFILE-SECTOR-TRUTH

AUTHORITY:
    Wilsy OS Core Governance.
    Canonical in-process tenant and organization domain representation.

EPITOME:
    Establishes sector as durable top-level tenant profile truth while preserving
    the existing organization profile, tenant identity, lifecycle, evidence, and
    compatibility serialization contracts. Sector is profile metadata beside
    alias and region; it is not billing, lifecycle, verification, security, or
    financial authority.

ABSOLUTE CANONICAL PATH:
    /Users/wilsonkhanyezi/legal-doc-system/tools/eos/saas/domain/tenant.py

COLLABORATION / OWNERSHIP:
    Wilson Khanyezi / Wilsy Core Engineering.

CERTIFICATION / UPDATE DATE:
    2026-08-30

CHANGELOG:
    v1.4.0-TENANT-PROFILE-SECTOR-TRUTH
        - Adds top-level TenantEntity.sector as optional durable profile truth.
        - Adds sector to TenantEntity to_dict/from_dict round-trip.
        - Preserves existing checksum construction, tenant identity, plan enum,
          organization fields, legacy update behavior, and all non-profile fields.
        - Reauthors the file under the current sovereign artifact contract.

    v1.3.1-DATACLASS-FIELD-ORDER
        - Preserved checksum init=False field-order compatibility.

COMPLIANCE:
    POPIA section 19.
    GDPR Article 32.
    SOC 2 CC7.2.
    ISO 27001.

SECURITY / PRIVACY POSTURE:
    Domain objects represent data only. Construction, deserialization, or mutation
    of these objects grants no tenant membership, role, permission, authentication,
    authorization, or financial authority.

TENANT BOUNDARY:
    tenant_id is represented as explicit tenant identity data. Sector, alias, and
    region are tenant profile attributes and never establish access to that tenant.

AUTHORITY BOUNDARY:
    This artifact owns domain representation and deterministic checksum behavior
    only. HTTP authority, durable authorization, repository scope enforcement,
    and persistence failure semantics are owned elsewhere.

FINANCIAL AUTHORITY BOUNDARY:
    Subscription plan is descriptive commercial metadata only.
    No financial execution authority exists here.
    Kennel EOS remains the exclusive financial execution authority.

STRUCTURAL GOVERNANCE:
    AGENTS.md v1.2.0-SOVEREIGN-LEGAL-OPERATIONS-CONSTITUTION.
    Full-file sovereign artifact.
    Fail-closed authority posture.
===============================================================================
"""

from __future__ import annotations

import hashlib
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any


VERSION = "v1.4.0-TENANT-PROFILE-SECTOR-TRUTH"


def parse_datetime(value: Any) -> str:
    """Normalize a datetime-like value into the existing ISO-string shape.

    Authority:
        Conversion only; no tenant or authorization authority.

    Mutation:
        Does not mutate caller state.

    Failure semantics:
        Invalid or unsupported values preserve the legacy behavior of resolving
        to the current UTC time.

    Financial boundary:
        No financial execution authority.
    """
    if isinstance(value, datetime):
        return value.isoformat()
    if isinstance(value, str):
        try:
            return datetime.fromisoformat(value).isoformat()
        except ValueError:
            return datetime.now(timezone.utc).isoformat()
    return datetime.now(timezone.utc).isoformat()


class SubscriptionPlan(str, Enum):
    """Represent commercial tenant subscription labels without execution authority.

    These values are descriptive metadata only. They do not prove payment,
    settlement, entitlement, or financial execution.
    """

    COMMUNITY = "COMMUNITY"
    PROFESSIONAL = "PROFESSIONAL"
    ENTERPRISE = "ENTERPRISE"
    SOVEREIGN_ENTERPRISE = "SOVEREIGN_ENTERPRISE"

    # Legacy alias retained for registry payloads that still emit BASIC.
    BASIC = "COMMUNITY"


@dataclass
class OrganizationProfile:
    """Represent organization metadata embedded in one tenant.

    Authority:
        Data representation only.

    Tenant scope:
        Organization metadata does not establish membership or tenant authority.

    Mutation:
        ``update`` preserves the existing compatibility behavior, including
        updating this profile's created_at field.

    Financial boundary:
        ``plan`` is descriptive metadata only; no financial execution authority.
    """

    organization_name: str
    industry: str
    plan: SubscriptionPlan
    legal_name: str | None = None
    tax_id: str | None = None
    contact_email: str | None = None
    regions: list[str] = field(default_factory=lambda: ["Africa", "Europe"])
    created_at: str = field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )

    def to_dict(self) -> dict[str, Any]:
        """Serialize this organization profile without granting authority."""
        return {
            "organization_name": self.organization_name,
            "industry": self.industry,
            "plan": (
                self.plan.value
                if isinstance(self.plan, SubscriptionPlan)
                else str(self.plan)
            ),
            "legal_name": self.legal_name,
            "tax_id": self.tax_id,
            "contact_email": self.contact_email,
            "regions": self.regions,
            "created_at": self.created_at,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "OrganizationProfile":
        """Deserialize organization data using the existing plan fallback."""
        plan_raw = data.get("plan", "COMMUNITY")
        try:
            plan = (
                plan_raw
                if isinstance(plan_raw, SubscriptionPlan)
                else SubscriptionPlan(str(plan_raw).upper())
            )
        except ValueError:
            plan = SubscriptionPlan.COMMUNITY

        return cls(
            organization_name=data["organization_name"],
            industry=data["industry"],
            plan=plan,
            legal_name=data.get("legal_name"),
            tax_id=data.get("tax_id"),
            contact_email=data.get("contact_email"),
            regions=data.get("regions", ["Africa", "Europe"]),
            created_at=parse_datetime(
                data.get(
                    "created_at",
                    datetime.now(timezone.utc).isoformat(),
                )
            ),
        )

    def update(self, updates: dict[str, Any]) -> None:
        """Apply the pre-existing in-memory organization update contract.

        This compatibility method performs no authorization. Profile-specific
        persistence policy is enforced by TenantRegistry.update_profile instead.
        """
        for key, value in updates.items():
            if not hasattr(self, key):
                continue
            if key == "plan" and isinstance(value, str):
                try:
                    value = SubscriptionPlan(value.upper())
                except ValueError:
                    value = SubscriptionPlan.COMMUNITY
            setattr(self, key, value)

        self.created_at = datetime.now(timezone.utc).isoformat()


@dataclass
class TenantEntity:
    """Represent one isolated tenant and its durable profile projection.

    Authority:
        Domain representation only. Instantiating or mutating this object never
        authenticates or authorizes a caller.

    Tenant scope:
        ``tenant_id`` identifies the represented tenant. ``alias``, ``region``,
        and ``sector`` are profile attributes only.

    Integrity:
        ``checksum`` is deterministically recomputed from tenant id, organization
        name, plan, lifecycle status, and created_at when this object initializes
        or uses the legacy in-memory ``update`` method.

    Mutation:
        The in-memory ``update`` method is retained for compatibility. The strict
        durable HTTP-ready mutation contract belongs to TenantRegistry.update_profile.

    Financial boundary:
        No financial execution authority. Kennel EOS remains exclusive.
    """

    organization: OrganizationProfile
    tenant_id: str = field(
        default_factory=lambda: f"WILSYTENANT-{uuid.uuid4().hex[:8].upper()}"
    )
    status: str = "ACTIVE"
    created_at: str = field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )
    checksum: str = field(default="", init=False)

    alias: str | None = None
    region: str | None = None
    sector: str | None = None
    compliance_flags: dict[str, Any] | None = None
    proof_hash: str | None = None
    verified: bool = False

    def __post_init__(self) -> None:
        """Compute the current deterministic tenant checksum."""
        self.checksum = self._compute_checksum()

    def _compute_checksum(self) -> str:
        """Return the deterministic SHA-256 tenant integrity checksum.

        This is an integrity projection only. It is not a signature, credential,
        authorization grant, payment proof, or financial execution record.
        """
        plan_value = (
            self.organization.plan.value
            if isinstance(self.organization.plan, SubscriptionPlan)
            else str(self.organization.plan)
        )
        raw_data = (
            f"{self.tenant_id}:"
            f"{self.organization.organization_name}:"
            f"{plan_value}:"
            f"{self.status}:"
            f"{self.created_at}"
        )
        return hashlib.sha256(raw_data.encode("utf-8")).hexdigest()

    def to_dict(self) -> dict[str, Any]:
        """Serialize the tenant entity, including durable sector profile truth."""
        return {
            "tenant_id": self.tenant_id,
            "organization": self.organization.to_dict(),
            "status": self.status,
            "created_at": self.created_at,
            "checksum": self.checksum,
            "alias": self.alias,
            "region": self.region,
            "sector": self.sector,
            "compliance_flags": self.compliance_flags,
            "proof_hash": self.proof_hash,
            "verified": self.verified,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "TenantEntity":
        """Deserialize tenant data and recompute its in-memory checksum."""
        organization = OrganizationProfile.from_dict(data["organization"])
        tenant = cls(
            organization=organization,
            tenant_id=data.get(
                "tenant_id",
                f"WILSYTENANT-{uuid.uuid4().hex[:8].upper()}",
            ),
            status=data.get("status", "ACTIVE"),
            created_at=parse_datetime(
                data.get(
                    "created_at",
                    datetime.now(timezone.utc).isoformat(),
                )
            ),
            alias=data.get("alias"),
            region=data.get("region"),
            sector=data.get("sector"),
            compliance_flags=data.get("compliance_flags"),
            proof_hash=data.get("proof_hash"),
            verified=bool(data.get("verified", False)),
        )
        tenant.checksum = tenant._compute_checksum()
        return tenant

    def update(self, updates: dict[str, Any]) -> None:
        """Apply the pre-existing in-memory tenant update compatibility contract.

        This method is intentionally not the durable profile mutation boundary.
        It performs no authorization and retains historical created_at/checksum
        behavior for existing callers.
        """
        if "organization" in updates:
            self.organization.update(updates["organization"])

        for key, value in updates.items():
            if key != "organization" and hasattr(self, key) and key != "checksum":
                setattr(self, key, value)

        self.created_at = datetime.now(timezone.utc).isoformat()
        self.checksum = self._compute_checksum()


__all__ = [
    "VERSION",
    "parse_datetime",
    "SubscriptionPlan",
    "OrganizationProfile",
    "TenantEntity",
]


# =============================================================================
# WILSY OS SOVEREIGN ARTIFACT CERTIFICATION SEAL
# =============================================================================
# ARTIFACT: tenant.py
# VERSION: v1.4.0-TENANT-PROFILE-SECTOR-TRUTH
# AUTHORITY BOUNDARY: tenant/organization domain representation and deterministic checksum behavior only; no authentication, authorization, persistence, or execution authority
# TENANT POSTURE: tenant_id identifies the represented tenant; alias, region, and sector are profile data and never access grants
# FAIL-CLOSED POSTURE: domain construction cannot confer authority; unsupported plan input retains the established COMMUNITY compatibility fallback
# FINANCIAL EXECUTION AUTHORITY: None. Kennel EOS remains exclusive.
# END OF WILSY OS SOVEREIGN ARTIFACT
