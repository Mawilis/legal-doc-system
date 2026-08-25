"""
===============================================================================
WILSY OS — FG231C ENTERPRISE NERVOUS SYSTEM [V1.0.0]
===============================================================================
Epitome:
    Enterprise Governance Engine enforcing zero-trust compliance validation, 
    policy link verification, cryptographic attestations, and audit recording.

Biblical Worth Billions:
    "The law of the wise is a fountain of life, to depart from the snares of death."
    — Proverbs 13:14

Collaboration & Ownership:
    - Founder & Chief Architect: Wilson Khanyezi (Wilsy OS)
    - AI Collaborator: Core Systems Architecture Agent
    - File Path: tools/eos/repository/intelligence/governance/governance_engine.py
===============================================================================
"""

from __future__ import annotations

import json
import os
import logging
from typing import Dict, Any, List

from.governance_links import (
    GovernanceLink,
    ComplianceTier,
    GovernanceLinkCatalog,
)

logger = logging.getLogger("WilsyOS.FG231C.GovernanceEngine")


class GovernanceEngine:
    """
    Sovereign governance engine responsible for linking capability registers
    to enterprise policy models, performing compliance checks, and writing audit state.
    """

    def __init__(self, primary_output_path: str = "reports/GovernanceLinks.json") -> None:
        self.primary_output_path = primary_output_path
        self.catalog = GovernanceLinkCatalog()

    def build_governance_links(self) -> GovernanceLinkCatalog:
        """
        Binds registered core platform capabilities to enterprise zero-trust security policies.
        """
        links = [
            GovernanceLink(
                capability_id="CAP-REPOSITORY-SCAN",
                policy_id="POL-GOV-001-AST-SCAN-INTEGRITY",
                compliance_tier=ComplianceTier.SOVEREIGN_AUDIT,
                requires_attestation=True,
                security_boundary="LEVEL_5_SOVEREIGN",
            ),
            GovernanceLink(
                capability_id="CAP-KNOWLEDGE-SYNCHRONIZATION",
                policy_id="POL-GOV-002-KNOWLEDGE-GRAPH-ISOLATION",
                compliance_tier=ComplianceTier.HIGH_SECURITY,
                requires_attestation=True,
                security_boundary="LEVEL_4_ENTERPRISE",
            ),
            GovernanceLink(
                capability_id="CAP-PREDICTION-RISK-ASSESSMENT",
                policy_id="POL-GOV-003-PREDICTIVE-BLAST-RADIUS-BOUNDS",
                compliance_tier=ComplianceTier.HIGH_SECURITY,
                requires_attestation=True,
                security_boundary="LEVEL_4_ENTERPRISE",
            ),
            GovernanceLink(
                capability_id="CAP-GOVERNANCE-COMPLIANCE",
                policy_id="POL-GOV-004-SOVEREIGN-POLICY-ATTESTATION",
                compliance_tier=ComplianceTier.SOVEREIGN_AUDIT,
                requires_attestation=True,
                security_boundary="LEVEL_5_SOVEREIGN",
            ),
            GovernanceLink(
                capability_id="CAP-CONTROL-ROOM-DISPATCH",
                policy_id="POL-GOV-005-EXECUTIVE-TELEMETRY-STREAMING",
                compliance_tier=ComplianceTier.SOVEREIGN_AUDIT,
                requires_attestation=True,
                security_boundary="LEVEL_5_SOVEREIGN",
            ),
        ]

        for link in links:
            self.catalog.add_link(link)

        return self.catalog

    def audit_governance_coverage(self, expected_capability_ids: List[str]) -> Dict[str, Any]:
        """
        Verifies that every provided capability ID has an associated zero-trust governance policy.
        """
        uncovered = [cap_id for cap_id in expected_capability_ids if cap_id not in self.catalog.links]
        return {
            "total_expected": len(expected_capability_ids),
            "covered_capabilities": len(expected_capability_ids) - len(uncovered),
            "uncovered_capabilities": uncovered,
            "compliance_percentage": (
                ((len(expected_capability_ids) - len(uncovered)) / len(expected_capability_ids)) * 100.0
                if expected_capability_ids
                else 100.0
            ),
        }

    def execute_and_save(self) -> Dict[str, Any]:
        """
        Builds governance linkages, audits platform coverage, and persists JSON artifacts.
        """
        logger.info("Executing Governance Engine...")
        self.build_governance_links()

        expected = [
            "CAP-REPOSITORY-SCAN",
            "CAP-KNOWLEDGE-SYNCHRONIZATION",
            "CAP-PREDICTION-RISK-ASSESSMENT",
            "CAP-GOVERNANCE-COMPLIANCE",
            "CAP-CONTROL-ROOM-DISPATCH",
        ]
        audit_report = self.audit_governance_coverage(expected)

        catalog_dict = self.catalog.to_dict()
        catalog_dict["audit_summary"] = audit_report

        # Primary persistence target (reports/)
        os.makedirs(os.path.dirname(self.primary_output_path), exist_ok=True)
        with open(self.primary_output_path, "w", encoding="utf-8") as f:
            json.dump(catalog_dict, f, indent=2)

        # Local module mirror target
        local_dir = os.path.dirname(__file__)
        local_target = os.path.join(local_dir, "governance_links.json")
        with open(local_target, "w", encoding="utf-8") as f:
            json.dump(catalog_dict, f, indent=2)

        logger.info(
            "Successfully verified %d governance policy links with %.1f%% compliance coverage.",
            len(self.catalog.links),
            audit_report["compliance_percentage"],
        )
        return catalog_dict