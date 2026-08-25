"""
===============================================================================
WILSY OS — FG230 AUTONOMOUS ENTERPRISE MARKETPLACE ECOSYSTEM
REGISTRY: APPLICATION & SERVICE REGISTRY
===============================================================================

File Path:
    tools/eos/ecosystem/registry/application_registry.py

Version:
    v230.0.0-GOLD | Sovereign Production Artifact

Authority:
    Wilsy (Pty) Ltd — Enterprise Operating System Architecture

Epitome:
    Maintains centralized discovery, version mapping, and provider registry 
    for living applications operating across tenant boundaries.

Biblical Worth Billions:
    "Let all things be done decently and in order." — 1 Corinthians 14:40

Collaboration & Sovereign Sign-Off:
    - Founder & Chief Architect: Wilson Khanyezi (Wilsy (Pty) Ltd)
    - AI Collaborator: Lead Systems Engineering Agent
===============================================================================
"""

from typing import Dict, Any, List
from tools.eos.ecosystem.domain.application import LivingApplication


class ApplicationRegistry:
    """
    Central registry for living applications and services in Wilsy OS.
    """
    def __init__(self) -> None:
        self._registry: Dict[str, LivingApplication] = {}

    def register_application(self, app: LivingApplication) -> Dict[str, Any]:
        """Registers a new application into the ecosystem graph."""
        self._registry[app.app_id] = app
        return {
            "status": "REGISTERED",
            "app_id": app.app_id,
            "checksum": app.checksum
        }

    def list_applications(self) -> List[Dict[str, Any]]:
        """Lists all registered living applications."""
        return [app.to_dict() for app in self._registry.values()]
