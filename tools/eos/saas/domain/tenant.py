# -*- coding: utf-8 -*-
"""
╔══════════════════════════════════════════════════════════════════════════════════════════════════════════════════╗
║ WILSY OS — SOVEREIGN TENANT DOMAIN MODEL (PYTHON) – WITH VERIFIED FIELD                                       ║
╠══════════════════════════════════════════════════════════════════════════════════════════════════════════════════╣
║ FILE:           tools/eos/saas/domain/tenant.py                                                                ║
║ VERSION:        v1.3.1-DATACLASS-FIELD-ORDER                                                                  ║
║ AUTHORITY:      Wilsy OS Core Governance                                                                       ║
║ EPITOME:        TenantEntity field order fixed — checksum init=False now has default so __init__ accepts       ║
║                 tenant_id, status, alias, region, compliance_flags, proof_hash, verified.                      ║
║ CLASSIFICATION: Production Artifact                                                                            ║
╠══════════════════════════════════════════════════════════════════════════════════════════════════════════════════╣
║ 🔧 CHANGE LOG:                                                                                                  ║
║   2026-08-23 v1.3.1-DATACLASS-FIELD-ORDER – checksum=field(default="", init=False); restores full __init__.     ║
║   2026-08-23 v1.3.0-VERIFIED-FIELD – Added `verified: bool = False` to TenantEntity; updated to_dict/from_dict. ║
║   2026-08-23 v1.2.0-EXTRA-FIELDS – Added alias, region, compliance_flags, proof_hash.                          ║
║   2026-08-19 v1.1.1-FIXED – Reordered fields, WILSYTENANT- prefix, parse_datetime helper.                      ║
║   2026-08-19 v1.1.0-INSTITUTIONAL – Added legal_name, tax_id, contact_email; to_dict/from_dict methods.        ║
╠══════════════════════════════════════════════════════════════════════════════════════════════════════════════════╣
║ COMPLIANCE:    POPIA §19 │ GDPR §32 │ SOC2 §CC7.2 │ ISO 27001                                                  ║
║ CRYPTO:        SHA‑256 checksum for tenant integrity                                                           ║
║ IDENTITY:      WILSYTENANT-XXXXXXXX (8‑char hex)                                                               ║
║ INTEGRATION:   Used by tenant_registry.py and tenant_router.py.                                                ║
╚══════════════════════════════════════════════════════════════════════════════════════════════════════════════════╝
"""

import hashlib
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Dict, Any, List, Optional


# ─── Helper ──────────────────────────────────────────────────────────────────

def parse_datetime(val: Any) -> str:
    """
    Parse a datetime from ISO string or return the string if already.
    For consistency, we store datetimes as ISO strings.
    """
    if isinstance(val, datetime):
        return val.isoformat()
    if isinstance(val, str):
        try:
            dt = datetime.fromisoformat(val)
            return dt.isoformat()
        except ValueError:
            return datetime.now(timezone.utc).isoformat()
    return datetime.now(timezone.utc).isoformat()


# ─── Enums ────────────────────────────────────────────────────────────────────

class SubscriptionPlan(str, Enum):
    """Commercial enterprise subscription tiers."""
    COMMUNITY = "COMMUNITY"
    PROFESSIONAL = "PROFESSIONAL"
    ENTERPRISE = "ENTERPRISE"
    SOVEREIGN_ENTERPRISE = "SOVEREIGN_ENTERPRISE"
    # Alias retained for registry/legacy payloads that still send BASIC
    BASIC = "COMMUNITY"


# ─── Domain Models ──────────────────────────────────────────────────────────

@dataclass
class OrganizationProfile:
    """
    Encapsulates commercial organization metadata for a tenant.
    Required fields first: organization_name, industry, plan.
    """
    organization_name: str
    industry: str
    plan: SubscriptionPlan
    legal_name: Optional[str] = None
    tax_id: Optional[str] = None
    contact_email: Optional[str] = None
    regions: List[str] = field(default_factory=lambda: ["Africa", "Europe"])
    created_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

    def to_dict(self) -> Dict[str, Any]:
        """Serialise the organisation profile to a dictionary."""
        return {
            "organization_name": self.organization_name,
            "industry": self.industry,
            "plan": self.plan.value if isinstance(self.plan, SubscriptionPlan) else str(self.plan),
            "legal_name": self.legal_name,
            "tax_id": self.tax_id,
            "contact_email": self.contact_email,
            "regions": self.regions,
            "created_at": self.created_at,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "OrganizationProfile":
        """Deserialise from a dictionary."""
        plan_raw = data.get("plan", "COMMUNITY")
        try:
            plan = SubscriptionPlan(str(plan_raw).upper()) if not isinstance(plan_raw, SubscriptionPlan) else plan_raw
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
            created_at=parse_datetime(data.get("created_at", datetime.now(timezone.utc).isoformat())),
        )

    def update(self, updates: Dict[str, Any]) -> None:
        """
        Update fields from a dictionary.
        Handles plan conversion from string to enum.
        """
        for key, value in updates.items():
            if hasattr(self, key):
                if key == "plan" and isinstance(value, str):
                    try:
                        value = SubscriptionPlan(value.upper())
                    except ValueError:
                        value = SubscriptionPlan.COMMUNITY
                setattr(self, key, value)
        self.created_at = datetime.now(timezone.utc).isoformat()


@dataclass
class TenantEntity:
    """
    Encapsulates an isolated enterprise tenant with dedicated boundary, artifacts, and billing.

    Field order (dataclass rule):
      1. Required (no default): organization
      2. Optional with defaults: tenant_id, status, created_at, alias, …
      3. init=False fields MUST still carry a default so later fields stay in __init__
    """
    organization: OrganizationProfile
    tenant_id: str = field(default_factory=lambda: f"WILSYTENANT-{uuid.uuid4().hex[:8].upper()}")
    status: str = "ACTIVE"
    created_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    # CRITICAL: default="" so fields below remain valid __init__ parameters
    checksum: str = field(default="", init=False)

    # ─── Extended fields (all defaulted — valid after defaulted fields) ─────
    alias: Optional[str] = None
    region: Optional[str] = None
    compliance_flags: Optional[Dict[str, Any]] = None
    proof_hash: Optional[str] = None
    verified: bool = False

    def __post_init__(self) -> None:
        """Computes cryptographic verification checksum upon initialisation."""
        self.checksum = self._compute_checksum()

    def _compute_checksum(self) -> str:
        """Generates SHA‑256 integrity hash for the tenant entity."""
        plan_val = (
            self.organization.plan.value
            if isinstance(self.organization.plan, SubscriptionPlan)
            else str(self.organization.plan)
        )
        raw_data = (
            f"{self.tenant_id}:"
            f"{self.organization.organization_name}:"
            f"{plan_val}:"
            f"{self.status}:"
            f"{self.created_at}"
        )
        return hashlib.sha256(raw_data.encode("utf-8")).hexdigest()

    def to_dict(self) -> Dict[str, Any]:
        """Serialise the tenant entity to a dictionary."""
        return {
            "tenant_id": self.tenant_id,
            "organization": self.organization.to_dict(),
            "status": self.status,
            "created_at": self.created_at,
            "checksum": self.checksum,
            "alias": self.alias,
            "region": self.region,
            "compliance_flags": self.compliance_flags,
            "proof_hash": self.proof_hash,
            "verified": self.verified,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "TenantEntity":
        """Deserialise from a dictionary."""
        org_data = data["organization"]
        org = OrganizationProfile.from_dict(org_data)
        tenant = cls(
            organization=org,
            tenant_id=data.get("tenant_id", f"WILSYTENANT-{uuid.uuid4().hex[:8].upper()}"),
            status=data.get("status", "ACTIVE"),
            created_at=parse_datetime(data.get("created_at", datetime.now(timezone.utc).isoformat())),
            alias=data.get("alias"),
            region=data.get("region"),
            compliance_flags=data.get("compliance_flags"),
            proof_hash=data.get("proof_hash"),
            verified=bool(data.get("verified", False)),
        )
        tenant.checksum = tenant._compute_checksum()
        return tenant

    def update(self, updates: Dict[str, Any]) -> None:
        """
        Update tenant fields and recompute checksum.
        If 'organization' is present, update the organisation profile.
        """
        if "organization" in updates:
            self.organization.update(updates["organization"])
        for key, value in updates.items():
            if key != "organization" and hasattr(self, key) and key != "checksum":
                setattr(self, key, value)
        self.created_at = datetime.now(timezone.utc).isoformat()
        self.checksum = self._compute_checksum()


"""
════════════════════════════════════════════════════════════════════════════════
INSTITUTIONAL CERTIFICATION SEAL — WILSY OS TENANT DOMAIN (DATACLASS FIELD ORDER)
════════════════════════════════════════════════════════════════════════════════
Status:          CERTIFIED PRODUCTION ARTIFACT
Version:         v1.3.1-DATACLASS-FIELD-ORDER
Fix:             checksum = field(default="", init=False) so TenantEntity.__init__
                 accepts tenant_id, status, created_at, alias, region,
                 compliance_flags, proof_hash, verified (clears Pylance call-arg).
Additions:       verified: bool = False; SubscriptionPlan.BASIC alias → COMMUNITY
Compliance:      POPIA §19 │ GDPR §32 │ SOC2 §CC7.2 │ ISO 27001
Crypto:          SHA‑256 checksum per tenant
Identity:        WILSYTENANT-XXXXXXXX
Methods:         to_dict, from_dict, update, _compute_checksum
════════════════════════════════════════════════════════════════════════════════
"""
