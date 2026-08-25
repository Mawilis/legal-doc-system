"""
===============================================================================
WILSY OS — FG231C ENTERPRISE NERVOUS SYSTEM [V1.0.0]
===============================================================================
Epitome:
    Sovereign governance linkage structures mapping enterprise capabilities to 
    zero-trust security policies, compliance mandates, and audit attestations.

Biblical Worth Billions:
    "Where no counsel is, the people fall: but in the multitude of counsellors 
    there is safety." — Proverbs 11:14

Collaboration & Ownership:
    - Founder & Chief Architect: Wilson Khanyezi (Wilsy (Pty) Ltd)
    - AI Collaborator: Core Systems Architecture Agent
    - File Path: tools/eos/repository/intelligence/governance/governance_links.py
===============================================================================
"""

from __future__ import annotations

from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone
from enum import Enum
from typing import List, Dict, Any, Optional


class ComplianceTier(str, Enum):
    """Compliance levels required for capability execution."""
    STANDARD = "STANDARD"
    HIGH_SECURITY = "HIGH_SECURITY"
    SOVEREIGN_AUDIT = "SOVEREIGN_AUDIT"


@dataclass
class GovernanceLink:
    """
    Binds a capability to specific governance requirements, cryptographic policy IDs,
    and zero-trust authorization checks.
    """
    capability_id: str
    policy_id: str
    compliance_tier: ComplianceTier
    requires_attestation: bool = True
    security_boundary: str = "LEVEL_5_SOVEREIGN"
    created_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

    def to_dict(self) -> Dict[str, Any]:
        """Converts governance link to a dictionary."""
        data = asdict(self)
        data["compliance_tier"] = self.compliance_tier.value if isinstance(self.compliance_tier, ComplianceTier) else str(self.compliance_tier)
        return data


@dataclass
class GovernanceLinkCatalog:
    """
    Catalog maintaining capability-to-policy compliance associations.
    """
    links: Dict[str, GovernanceLink] = field(default_factory=dict)

    def add_link(self, link: GovernanceLink) -> None:
        """Registers a capability governance link."""
        self.links[link.capability_id] = link

    def get_link(self, capability_id: str) -> Optional[GovernanceLink]:
        """Retrieves governance link for a capability ID."""
        return self.links.get(capability_id)

    def to_dict(self) -> Dict[str, Any]:
        """Serializes governance link catalog."""
        return {
            "total_links": len(self.links),
            "links": {k: v.to_dict() for k, v in self.links.items()},
        }