"""
===============================================================================
WILSY OS PATCH ENGINE: REMEDIATION MODELS
===============================================================================
Epitome:
    The blueprint for system healing. Defines how the OS interprets failures 
    and structures the remediation code required to restore architectural 
    integrity.

Biblical Scale & Architecture:
    These models are the prescription for a sick artifact. They map the 
    'sickness' (violation) to the 'cure' (patch). Immutable by design.

Collaboration & Maintenance:
    - PatchManifest: The high-level instruction set for the remediation.
    - RemediationReport: The post-patch verification log.
===============================================================================
"""
from dataclasses import dataclass
from typing import Dict, Any, List

@dataclass(frozen=True)
class PatchManifest:
    """
    Instructions for repairing a failing artifact.
    """
    artifact_id: str
    target_violation: str
    patch_instructions: str
    security_priority: int

@dataclass(frozen=True)
class RemediationReport:
    """
    The outcome of a patch application.
    """
    patch_id: str
    success: bool
    details: Dict[str, Any]
    applied_at: str
