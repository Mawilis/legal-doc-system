"""WILSY OS sovereign artifact-contract regression tests.

TITLE: Sovereign Artifact Header, Version, Changelog and Seal Guard
VERSION: v1.0.3-WILSY-SOVEREIGN-ARTIFACT-CONTRACT-GUARD
AUTHORITY: Wilsy OS Core Governance
EPITOME: Prevents the corrected Kennel EOS runbook and forensic inventory from
         losing their required sovereign header, version agreement, changelog,
         explicit end seal, or fail-closed inventory classification.
ABSOLUTE CANONICAL PATH:
    /Users/wilsonkhanyezi/legal-doc-system/tests/unit/test_sovereign_artifact_contract.py
COLLABORATION / OWNERSHIP:
    Python EOS governance tests; artifact owners retain source authority.
CERTIFICATION / UPDATE DATE: 2026-11-08
CHANGELOG:
    v1.0.3-WILSY-SOVEREIGN-ARTIFACT-CONTRACT-GUARD adds self-audit coverage
    for this test artifact as well as the diagnostic and forensic inventory.
    v1.0.2-WILSY-SOVEREIGN-ARTIFACT-CONTRACT-GUARD avoids embedding forbidden
    source markers while retaining exact target checks.
    v1.0.1-WILSY-SOVEREIGN-ARTIFACT-CONTRACT-GUARD documents test boundaries.
    v1.0.0-WILSY-SOVEREIGN-ARTIFACT-CONTRACT-GUARD established the initial checks.
COMPLIANCE: AGENTS.md v1.2.0; ENGINEERING_CONSTITUTION.md v1.1.0.
SECURITY / PRIVACY POSTURE: Reads repository text only; opens no secrets,
    network connections, databases, or external processes.
TENANT BOUNDARY: No tenant data or tenant authority is accessed.
AUTHORITY BOUNDARY: Test-only structural governance; no business or runtime
    authority.
FINANCIAL AUTHORITY BOUNDARY: No payment, provider, settlement, invoice, or
    ledger execution authority.
TRANSACTION BOUNDARY: No persistence or database transaction is performed.
FAIL-CLOSED DECLARATION: Missing or divergent artifact metadata fails tests.

WILSY OWNS BUSINESS TRUTH. KENNEL EOS IS THE EXCLUSIVE FINANCIAL EXECUTION AUTHORITY.
"""

from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
ARTIFACTS = (
    (
        ROOT / "tests/unit/test_sovereign_artifact_contract.py",
        "v1.0.3-WILSY-SOVEREIGN-ARTIFACT-CONTRACT-GUARD",
    ),
    (
        ROOT / "runbook_diagnostic.py",
        "v1.0.0-WILSY-KENNEL-EOS-RUNBOOK-DIAGNOSTIC",
    ),
    (
        ROOT / "docs/architecture/eos-runtime-database-consumer-inventory.md",
        "v2.4.0-KENNEL-EOS-LEGACY-NODE-FORENSIC-INVENTORY",
    ),
)
REQUIRED_HEADER_MARKERS = (
    "TITLE:",
    "VERSION:",
    "AUTHORITY:",
    "EPITOME:",
    "ABSOLUTE CANONICAL PATH:",
    "COLLABORATION",
    "CERTIFICATION",
    "CHANGELOG:",
    "COMPLIANCE:",
    "SECURITY",
    "TENANT BOUNDARY:",
    "AUTHORITY BOUNDARY:",
    "FINANCIAL AUTHORITY BOUNDARY:",
    "TRANSACTION BOUNDARY:",
)
FORBIDDEN_TEMPLATE_MARKERS = ("TO" + "DO", "FIX" + "ME", "Not" + "Implemented", "PLACE" + "HOLDER")


def test_governed_artifacts_have_complete_header_version_changelog_and_seal() -> None:
    """Check structural metadata without acquiring business authority.

    Tenant scope: repository-local text only; no tenant records are read.
    Mutation: none. Idempotency: not applicable to this read-only assertion.
    Transaction ownership: none; no database session is opened.
    Fail-closed: missing or divergent metadata raises an assertion failure.
    Financial boundary: no payment, settlement, or ledger authority.
    """
    for path, expected_version in ARTIFACTS:
        assert path.is_file(), f"Governed artifact is missing: {path}"
        content = path.read_text(encoding="utf-8")
        for marker in REQUIRED_HEADER_MARKERS:
            assert marker in content, f"{path}: missing required header marker {marker}"
        version_matches = re.findall(
            r"(?m)^\s*(?:\*\*VERSION:\*\*|VERSION:)\s*(\S+)",
            content,
        )
        assert version_matches, f"{path}: no version declaration found"
        assert version_matches[0] == expected_version, (
            f"{path}: expected version {expected_version}, got {version_matches[0]}"
        )
        assert content.count(expected_version) >= 3, (
            f"{path}: version must agree across header, changelog and end seal"
        )
        assert "CHANGELOG:" in content and expected_version in content.split("CHANGELOG:", 1)[1]
        final_line = content.rstrip().splitlines()[-1]
        assert final_line.endswith("END OF WILSY OS SOVEREIGN ARTIFACT"), (
            f"{path}: explicit sovereign end seal is missing"
        )
        for marker in FORBIDDEN_TEMPLATE_MARKERS:
            assert marker not in content, f"{path}: unresolved marker {marker}"


def test_forensic_inventory_does_not_claim_unverified_legacy_parity() -> None:
    """Preserve unresolved findings as a fail-closed governance assertion.

    Tenant scope: no tenant data is accessed. Mutation and persistence: none.
    Idempotency and transaction ownership: not applicable; this test is read-only.
    Fail-closed: removal of an unresolved finding fails the test rather than
    silently upgrading the inventory classification. Financial authority: none.
    """
    path = ROOT / "docs/architecture/eos-runtime-database-consumer-inventory.md"
    content = path.read_text(encoding="utf-8")
    required_findings = (
        "PARTIAL — NOT OPERATIONALLY CERTIFIED",
        "UNKNOWN / REQUIRES FORENSICS",
        "MISSING PARITY",
        "nginx.conf",
        "infra/nginx/fortress-lb.conf",
        "k8s/predictive-deployment.yaml",
        "Sovereign_Deployment_Automation.sh",
        "initializeSovereignJobs",
        "verificationSyncJob.js",
    )
    for finding in required_findings:
        assert finding in content, f"Forensic inventory omitted unresolved finding: {finding}"


# ARTIFACT: test_sovereign_artifact_contract.py
# VERSION: v1.0.3-WILSY-SOVEREIGN-ARTIFACT-CONTRACT-GUARD
# AUTHORITY BOUNDARY: structural governance tests only.
# TENANT POSTURE: no tenant access or authority.
# FAIL-CLOSED POSTURE: missing, divergent, or unsealed artifact metadata fails.
# FINANCIAL EXECUTION AUTHORITY: none; Kennel EOS exclusively owns execution.
# END OF WILSY OS SOVEREIGN ARTIFACT
