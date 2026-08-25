"""
===============================================================================
WILSY OS — FG227 CLOUD PLATFORM SUBSYSTEM
DOMAIN: CLOUD MODEL & ENTITY DEFINITIONS
===============================================================================

File Path:
    tools/eos/cloud/domain/cloud_model.py

Version:
    v227.0.0-GOLD | Sovereign Production Artifact

Authority:
    Wilsy (Pty) Ltd — Enterprise Operating System Architecture

Epitome:
    Defines core data structures for cloud providers, tenants, infrastructure 
    blueprints, and runtime deployment states across public, private, and hybrid clouds.

Biblical Worth Billions:
    "For which of you, intending to build a tower, sitteth not down first, and 
    counteth the cost, whether he have sufficient to finish it?" — Luke 14:28

Collaboration & Sovereign Sign-Off:
    - Founder & Chief Architect: Wilson Khanyezi (Wilsy (Pty) Ltd)
    - AI Collaborator: Lead Systems Engineering Agent
===============================================================================
"""

import hashlib
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Dict, Any, List


class CloudProviderType(str, Enum):
    """Supported cloud infrastructure providers."""
    AWS = "AWS"
    AZURE = "AZURE"
    GCP = "GCP"
    ORACLE = "ORACLE"
    DIGITALOCEAN = "DIGITALOCEAN"
    OPENSTACK = "OPENSTACK"
    VMWARE = "VMWARE"
    BARE_METAL = "BARE_METAL"


class DeploymentModel(str, Enum):
    """Cloud deployment architectural models."""
    PUBLIC_CLOUD = "PUBLIC_CLOUD"
    PRIVATE_CLOUD = "PRIVATE_CLOUD"
    HYBRID_CLOUD = "HYBRID_CLOUD"


@dataclass
class TenantProfile:
    """
    Encapsulates an isolated tenant entity within the Wilsy OS Cloud Platform.
    """
    tenant_id: str = field(default_factory=lambda: f"TENANT-{uuid.uuid4().hex[:6].upper()}")
    tenant_name: str = "Enterprise Global Corp"
    deployment_model: DeploymentModel = DeploymentModel.HYBRID_CLOUD
    primary_provider: CloudProviderType = CloudProviderType.AWS
    status: str = "PROVISIONED"
    created_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    checksum: str = field(init=False)

    def __post_init__(self) -> None:
        """Computes cryptographic verification checksum upon tenant initialization."""
        self.checksum = self._compute_checksum()

    def _compute_checksum(self) -> str:
        """Generates a SHA-256 integrity hash for the tenant profile."""
        raw_data = f"{self.tenant_id}:{self.tenant_name}:{self.deployment_model.value}:{self.primary_provider.value}:{self.status}:{self.created_at}"
        return hashlib.sha256(raw_data.encode("utf-8")).hexdigest()

    def to_dict(self) -> Dict[str, Any]:
        """Serializes the tenant profile into a dictionary representation."""
        return {
            "tenant_id": self.tenant_id,
            "tenant_name": self.tenant_name,
            "deployment_model": self.deployment_model.value,
            "primary_provider": self.primary_provider.value,
            "status": self.status,
            "created_at": self.created_at,
            "checksum": self.checksum
        }
