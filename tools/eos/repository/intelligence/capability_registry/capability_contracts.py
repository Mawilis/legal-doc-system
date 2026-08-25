"""
===============================================================================
WILSY OS — FG231C ENTERPRISE NERVOUS SYSTEM [V1.0.0]
===============================================================================
Epitome:
    Contract validation and interface verification for sovereign capability 
    registration in the Wilsy OS Enterprise Nervous System.

Biblical Worth Billions:
    "A false balance is abomination to the LORD: but a just weight is his delight."
    — Proverbs 11:1

Collaboration & Ownership:
    - Founder & Chief Architect: Wilson Khanyezi (Wilsy (Pty) Ltd)
    - AI Collaborator: Core Systems Architecture Agent
    - File Path: tools/eos/repository/intelligence/capability_registry/capability_contracts.py
===============================================================================
"""

from __future__ import annotations

from typing import Tuple, List
from.capability_models import CapabilityMetadata, CapabilityCriticality, CapabilityLifecycleState


class CapabilityContractValidator:
    """
    Sovereign contract engine ensuring all capabilities registered into 
    the Wilsy OS brain adhere to strict enterprise compliance rules.
    """

    @staticmethod
    def validate(cap: CapabilityMetadata) -> Tuple[bool, List[str]]:
        """
        Validates capability metadata against system invariants.
        Returns a tuple of (is_valid, list_of_error_messages).
        """
        errors: List[str] = []

        # Rule 1: ID Prefix Verification
        if not cap.capability_id.startswith("CAP-"):
            errors.append(f"Invalid Capability ID prefix: '{cap.capability_id}'. ID must begin with 'CAP-'.")

        # Rule 2: Event Binding Requirements
        if not cap.produces_events and not cap.consumes_events:
            errors.append(f"Capability '{cap.capability_id}' is isolated. It must produce or consume at least one event.")

        # Rule 3: Confidence Boundary Check
        if cap.confidence < 0.0 or cap.confidence > 1.0:
            errors.append(f"Capability '{cap.capability_id}' confidence score ({cap.confidence}) must be bounded between 0.0 and 1.0.")

        # Rule 4: Reuse Score Boundary Check
        if cap.reuse_score < 0.0 or cap.reuse_score > 1.0:
            errors.append(f"Capability '{cap.capability_id}' reuse score ({cap.reuse_score}) must be bounded between 0.0 and 1.0.")

        # Rule 5: Non-empty Core Field Requirements
        if not cap.name.strip():
            errors.append(f"Capability '{cap.capability_id}' has an empty or invalid name.")
        if not cap.owner.strip():
            errors.append(f"Capability '{cap.capability_id}' must specify a clear module owner.")
        if not cap.purpose.strip():
            errors.append(f"Capability '{cap.capability_id}' must define a functional purpose.")

        is_valid = len(errors) == 0
        return is_valid, errors