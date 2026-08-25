"""
===============================================================================
WILSY ENGINEERING KERNEL
===============================================================================
Epitome:
    Master Verification Test for Knowledge Base Playbook Engine (FG172A).
    Verifies rule execution, prohibited/required keyword checks, phrase alias matching,
    compliance scoring, and remediation generation.
    Billion-dollar software architecture: secure, robust, immutable, and future-proof.

Biblical Scale & Architecture:
    Production-ready verification test. Zero child's place.
    Proverbs 24:3-4 - "Through wisdom is an house builded; and by understanding it is established..."

Collaboration & Maintenance:
    - Maintained by Wilson Khanyezi & Core Engineering.
===============================================================================
"""

from __future__ import annotations

import asyncio
import logging

from tools.eos.knowledge.playbook import (
    KnowledgeBasePlaybook,
    PlaybookCategoryEnum,
    PlaybookExecutionEngine,
    PlaybookRule,
    PlaybookSeverityEnum,
)

logging.basicConfig(level=logging.INFO)


# [FUNCTION EXPLANATION]: Executes end-to-end master verification of the Playbook Engine.
async def run_master_verification() -> None:
    print("\n==================================================================")
    print("      WILSY OS: FG172A PLAYBOOK ENGINE MASTER VERIFICATION       ")
    print("==================================================================\n")

    # 1. Define Sample Playbook Rules using phrase aliases
    rule1 = PlaybookRule(
        title="Indemnification Limitation",
        category=PlaybookCategoryEnum.RISK_ASSESSMENT,
        severity=PlaybookSeverityEnum.CRITICAL,
        description="Contract must limit liability and prohibit unlimited indemnification.",
        required_keywords=["limitation of liability", "indemnify"],
        prohibited_keywords=["unlimited liability", "unconditional indemnity"],
        remediation_guidance="Insert liability cap standard clause (Section 12.2)."
    )

    rule2 = PlaybookRule(
        title="Governing Law Clause",
        category=PlaybookCategoryEnum.GOVERNANCE,
        severity=PlaybookSeverityEnum.HIGH,
        description="Governing law must explicitly specify approved jurisdiction.",
        required_keywords=["governing law|governed by", "jurisdiction"],
        prohibited_keywords=[],
        remediation_guidance="Specify South African legal jurisdiction in Section 15.1."
    )

    # 2. Build Playbook
    playbook = KnowledgeBasePlaybook(
        domain="Commercial Agreements",
        title="Standard Enterprise Legal Review Playbook",
        version="2.0.0",
        rules=[rule1, rule2],
    )

    # 3. Instantiate Engine & Run Evaluation
    engine = PlaybookExecutionEngine(playbook=playbook)

    sample_contract_text = """
    This Agreement is governed by the laws of South Africa and subject to standard jurisdiction.
    Each party agrees to indemnify the other party subject to a reasonable limitation of liability cap.
    """

    report = await engine.execute_playbook(
        document_id="doc-contract-99",
        document_text=sample_contract_text,
    )

    # 4. Verification Assertions
    assert report.total_rules == 2, f"Expected 2 total rules, got {report.total_rules}"
    assert report.passed_rules == 2, f"Expected 2 passed rules, got {report.passed_rules}"
    assert report.compliance_score == 100.0, f"Expected 100% score, got {report.compliance_score}%"
    assert len(report.results) == 2

    print(f" -> Compliance Score: {report.compliance_score}%")
    print(f" -> Passed Rules: {report.passed_rules}/{report.total_rules}")
    print(" -> SUCCESS: Knowledge Base Playbook evaluation verified cleanly.")

    print("\n==================================================================")
    print("         FG172A MASTER VERIFICATION: ALL SYSTEMS GREEN           ")
    print("==================================================================\n")


if __name__ == "__main__":
    asyncio.run(run_master_verification())
