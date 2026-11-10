"""WILSY OS sovereign artifact-contract regression tests.

TITLE: Sovereign Artifact Header, Version, Changelog and Seal Guard
VERSION: v1.3.2-WILSY-PYTHON-DOCSTRING-SEAL-CERT
AUTHORITY: Wilsy OS Core Governance
EPITOME: Certifies complete changed-blob headers, exact versions and canonical
         paths, all required end-seal fields, and retained evidence posture.
ABSOLUTE CANONICAL PATH:
    /Users/wilsonkhanyezi/legal-doc-system/tests/unit/test_sovereign_artifact_contract.py
COLLABORATION / OWNERSHIP:
    Python EOS governance tests; artifact owners retain source authority.
CERTIFICATION / UPDATE DATE: 2026-11-10
CHANGELOG:
    2026-11-10 v1.3.2-WILSY-PYTHON-DOCSTRING-SEAL-CERT recognizes Python
    docstring-delimited seals and equivalent date/privacy labels while
    preserving terminal-seal, exact-version, and canonical-path enforcement.
    2026-11-10 v1.3.1-WILSY-COMPLETE-END-SEAL-CONTRACT accepts the governed certification-date variants and
    enforces exact changelog/version agreement, correct paths, complete seals,
    and whole-repository production, test, and active governance coverage.
    2026-11-10 v1.2.0-WILSY-CHANGED-BLOB-SOVEREIGN-CONTRACT validates Git-blob metadata for changed
    applicable production, test, and active governance files.
    2026-11-08 v1.1.0-WILSY-SOVEREIGN-ARTIFACT-CONTRACT-GUARD recognizes version declarations in YAML comment headers
    as well as Markdown and source-file headers, preserving strict agreement
    checks across all governed artifacts.
    v1.0.9-WILSY-SOVEREIGN-ARTIFACT-CONTRACT-GUARD asserts deleted Node
    orchestrators stay absent and retired shell launchers stay fail-closed.
    v1.0.6-WILSY-SOVEREIGN-ARTIFACT-CONTRACT-GUARD certified retired launchers.
    v1.0.5-WILSY-SOVEREIGN-ARTIFACT-CONTRACT-GUARD tracked the expanded inventory.
    v1.0.4-WILSY-SOVEREIGN-ARTIFACT-CONTRACT-GUARD audited deployment documentation.
    v1.0.3-WILSY-SOVEREIGN-ARTIFACT-CONTRACT-GUARD added self-audit coverage.
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

import pytest

from tools.eos.governance.repository_integrity_guard import (
    IntegrityFailure,
    _artifact_scope,
    validate_artifact_contract,
)

ROOT = Path(__file__).resolve().parents[2]
ARTIFACTS = (
    (
        ROOT / "tests/unit/test_sovereign_artifact_contract.py",
        "v1.3.2-WILSY-PYTHON-DOCSTRING-SEAL-CERT",
    ),
    (
        ROOT / "tools/eos/governance/repository_integrity_guard.py",
        "v1.2.0-CHANGED-BLOB-PYTHON-DOCSTRING-SEAL-CERT",
    ),
    (
        ROOT / "DEPLOYMENT.md",
        "v1.3.0-PYTHON-EOS-RETIRED-BACKEND-AND-MIGRATION-LINEAGE",
    ),
    (
        ROOT / "server/README.md",
        "v1.2.0-LEGACY-NODE-SOURCE-BOUNDARY",
    ),
    (
        ROOT / ".github/workflows/eos-runtime-database-consumer-inventory.yml",
        "v1.2.0-EOS-RUNTIME-DATABASE-INVENTORY-CERTIFICATION",
    ),
    (
        ROOT / "start_all.sh",
        "v1.0.0-LEGACY-NODE-START-ALL-RETIRED",
    ),
    (
        ROOT / "start_wilsy_os.sh",
        "v1.0.0-LEGACY-NODE-START-WILSY-OS-RETIRED",
    ),
    (
        ROOT / "GlobalLaunchSequence.sh",
        "v1.0.0-LEGACY-GLOBAL-LAUNCH-SEQUENCE-RETIRED",
    ),
    (
        ROOT / "Genesis_Ignition.sh",
        "v1.0.0-LEGACY-GENESIS-IGNITION-RETIRED",
    ),
    (
        ROOT / "Sovereign_Deployment_Automation.sh",
        "v1.0.0-LEGACY-NODE-DEPLOYMENT-AUTOMATION-RETIRED",
    ),
    (
        ROOT / "runbook_diagnostic.py",
        "v1.0.0-WILSY-KENNEL-EOS-RUNBOOK-DIAGNOSTIC",
    ),
    (
        ROOT / "docs/architecture/eos-runtime-database-consumer-inventory.md",
        "v2.8.0-KENNEL-EOS-LEGACY-NODE-FORENSIC-INVENTORY",
    ),
)
REQUIRED_HEADER_MARKERS = (
    "TITLE:",
    "VERSION:",
    "TITLE:",
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
            r"(?m)^\s*(?:#\s*)?(?:\*\*VERSION:\*\*|VERSION:)\s*(\S+)",
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


def test_changed_artifact_guard_rejects_version_drift_and_incorrect_paths() -> None:
    """Keep changed-blob enforcement strict for version and canonical-path drift.

    Tenant scope: synthetic repository metadata only. Mutation, persistence,
    authority, idempotency, and transaction ownership: none. Financial
    authority: none; Kennel EOS exclusively owns execution.
    """
    version = "v1.0.0-CHANGED-ARTIFACT-CONTRACT-TEST"
    path = "client/src/components/example.jsx"
    content = f"""/**
TITLE: Example changed source artifact
VERSION: {version}
AUTHORITY: Wilsy OS Core Governance
EPITOME: Synthetic regression fixture for the changed Git blob contract.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/{path}
COLLABORATION / OWNERSHIP: Repository integrity regression test owner.
CERTIFICATION / UPDATE DATE: 2026-11-10
CHANGELOG: {version} establishes the synthetic complete artifact fixture.
COMPLIANCE: Repository governance only.
SECURITY / PRIVACY POSTURE: Synthetic metadata; no secrets or tenant data.
TENANT BOUNDARY: No tenant data or authority.
AUTHORITY BOUNDARY: No runtime or business authority.
FINANCIAL AUTHORITY BOUNDARY: None; Kennel EOS remains exclusive.
*/
// ARTIFACT: Example changed source artifact
// VERSION: {version}
// AUTHORITY BOUNDARY: No runtime or business authority.
// TENANT POSTURE: No tenant data or authority.
// FAIL-CLOSED POSTURE: Invalid changed-blob metadata rejects.
// FINANCIAL EXECUTION AUTHORITY: None; Kennel EOS remains exclusive.
// END OF WILSY OS SOVEREIGN ARTIFACT
"""
    validate_artifact_contract(path, content)
    certification_variant = content.replace(
        "CERTIFICATION / UPDATE DATE:",
        "CERTIFICATION OR UPDATE DATE:",
    )
    validate_artifact_contract(path, certification_variant)
    python_docstring = content.replace("/**\n", '"""\n', 1)
    python_docstring = python_docstring.replace(
        "\n*/\n// ARTIFACT:",
        '\n"""\n"""\nARTIFACT:',
        1,
    )
    python_docstring = re.sub(r"(?m)^// ?", "", python_docstring).rstrip() + '\n"""\n'
    validate_artifact_contract(path, python_docstring)
    python_label_variant = python_docstring.replace(
        "CERTIFICATION / UPDATE DATE:",
        "CERTIFICATION/UPDATE DATE:",
    ).replace(
        "SECURITY / PRIVACY POSTURE:",
        "SECURITY/PRIVACY POSTURE:",
    )
    validate_artifact_contract(path, python_label_variant)
    with pytest.raises(IntegrityFailure, match="terminal sovereign end seal is missing"):
        validate_artifact_contract(path, python_docstring + "assert True\n")
    with pytest.raises(IntegrityFailure, match="header and end-seal versions differ"):
        validate_artifact_contract(
            path,
            content.replace(
                f"// VERSION: {version}\n// AUTHORITY BOUNDARY:",
                "// VERSION: v1.0.1-CHANGED-ARTIFACT-CONTRACT-TEST\n// AUTHORITY BOUNDARY:",
            ),
        )
    with pytest.raises(IntegrityFailure, match="canonical artifact path mismatch"):
        validate_artifact_contract(
            path,
            content.replace(path, "client/src/components/other.jsx"),
        )
    multiline_path = content.replace(
        f"ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/{path}",
        "ABSOLUTE CANONICAL PATH:\n"
        "    /Users/wilsonkhanyezi/legal-doc-system/client/src/components/\n"
        "    example.jsx",
    )
    validate_artifact_contract(path, multiline_path)
    with pytest.raises(IntegrityFailure, match="incomplete sovereign end seal"):
        validate_artifact_contract(
            path,
            content.replace(
                "// FAIL-CLOSED POSTURE:",
                "// OMITTED FAIL-CLOSED POSTURE:",
            ),
        )
    with pytest.raises(
        IntegrityFailure,
        match="current version is absent from the header changelog",
    ):
        validate_artifact_contract(
            path,
            content.replace(
                f"CHANGELOG: {version}",
                f"CHANGELOG: {version}-DRIFTED",
            ),
        )


def test_changed_artifact_scope_covers_source_tests_and_active_governance() -> None:
    """Require changed source and active governance paths to use the blob contract.

    Tenant scope: repository paths only. Mutation and persistence: none.
    Authority: validation scope only, without runtime or business authority.
    Financial authority: none; Kennel EOS exclusively owns execution.
    """
    assert _artifact_scope("src/production_module.py") == "text"
    assert _artifact_scope("tests/unit/test_example.py") == "text"
    assert _artifact_scope(".github/workflows/example.yml") == "text"
    assert _artifact_scope("nested/AGENTS.md") == "text"
    assert _artifact_scope("tools/eos/governance/example.json") == "json"
    assert _artifact_scope("package-lock.json") is None
    assert _artifact_scope(
        "server/scripts/migration/DocumentMigrationEngine.js"
    ) is None
    assert _artifact_scope(
        "docs/architecture/eos-runtime-database-consumer-inventory.md"
    ) is None


def test_active_json_artifacts_use_the_complete_metadata_contract() -> None:
    """Validate active package and policy JSON metadata without changing them.

    Tenant scope: repository configuration only. Mutation, persistence,
    transaction ownership, idempotency, and business authority: none.
    Financial authority: none; Kennel EOS exclusively owns execution.
    """
    for relative_path in (
        "package.json",
        "tools/eos/governance/production_surface_policy.json",
    ):
        validate_artifact_contract(
            relative_path,
            (ROOT / relative_path).read_text(encoding="utf-8"),
        )


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
        "services/ai/aiService.js",
        "services/auth/authService.js",
        "services/crypto/cryptoService.js",
        "services/ledger/repair_ledger_service.js",
        "services/standards/standardsService.js",
        "start_all.sh",
        "start_wilsy_os.sh",
        "GlobalLaunchSequence.sh",
        "124 Node test files",
        "services/ai",
        "services/auth",
        "services/crypto",
        "services/ledger",
        "services/standards",
        "start_wilsy_os.sh",
        "GlobalLaunchSequence.sh",
        "repair_launcher.js",
        "build_orchestrator.js",
        "update_orchestrator.js",
        "bootstrap_wilsy_os.js",
        "route reachability",
    )
    for finding in required_findings:
        assert finding in content, f"Forensic inventory omitted unresolved finding: {finding}"


def test_legacy_node_launchers_are_fail_closed() -> None:
    """Prevent retired root launchers from acquiring process or deployment authority.

    Tenant scope: none. Mutation: none. Idempotency and transaction ownership:
    not applicable. Fail-closed: every retired launcher must exit before any
    Node, npm-start, PM2, process-kill, or background-service command. Financial
    execution authority: none.
    """
    launchers = (
        ("start_all.sh", "LEGACY_NODE_LAUNCHER_RETIRED"),
        ("start_wilsy_os.sh", "LEGACY_NODE_LAUNCHER_RETIRED"),
        ("GlobalLaunchSequence.sh", "LEGACY_NODE_LAUNCHER_RETIRED"),
        ("Genesis_Ignition.sh", "LEGACY_NODE_IGNITION_RETIRED"),
        ("Sovereign_Deployment_Automation.sh", "LEGACY_NODE_DEPLOYMENT_RETIRED"),
    )
    forbidden_commands = ("npm start", "node ", "pm2 ", "lsof -ti", "nohup ")
    for filename, retirement_marker in launchers:
        source = (ROOT / filename).read_text(encoding="utf-8")
        assert retirement_marker in source, f"{filename} lost its retirement marker"
        for command in forbidden_commands:
            assert command not in source, f"{filename} can still invoke {command}"


def test_runtime_inventory_workflow_covers_legacy_service_and_deployment_surfaces() -> None:
    """Require CI to run when any legacy runtime or ingress surface changes.

    Tenant scope: none. Mutation and persistence: none. Idempotency and
    transaction ownership: not applicable. Fail-closed: missing path filters
    or governance tests fail this assertion. Financial authority: none.
    """
    path = ROOT / ".github/workflows/eos-runtime-database-consumer-inventory.yml"
    content = path.read_text(encoding="utf-8")
    required_paths = (
        '      - "services/**"',
        '      - "start_all.sh"',
        '      - "start_wilsy_os.sh"',
        '      - "GlobalLaunchSequence.sh"',
        '      - "Genesis_Ignition.sh"',
        '      - "Sovereign_Deployment_Automation.sh"',
        '      - "repair_launcher.js"',
        '      - "build_orchestrator.js"',
        '      - "update_orchestrator.js"',
        '      - "bootstrap_wilsy_os.js"',
        '      - "nginx.conf"',
        '      - "infra/nginx/**"',
        '      - "k8s/**"',
        '      - "charts/legal-os/**"',
        '      - "server/**"',
        "tests/unit/test_sovereign_artifact_contract.py",
    )
    for required in required_paths:
        assert required in content, f"Runtime inventory workflow omits {required}"


def test_deleted_root_node_orchestrators_remain_absent() -> None:
    """Prevent unreferenced Node process generators from returning.

    Tenant scope: none. Mutation and persistence: none. Idempotency and
    transaction ownership: not applicable. Fail-closed: recreation of any
    deleted orchestrator fails this test. Financial authority: none.
    """
    deleted_paths = (
        "repair_launcher.js",
        "build_orchestrator.js",
        "update_orchestrator.js",
        "bootstrap_wilsy_os.js",
    )
    for relative_path in deleted_paths:
        assert not (ROOT / relative_path).exists(), (
            f"Retired Node orchestrator was recreated: {relative_path}"
        )


# ARTIFACT: test_sovereign_artifact_contract.py
# VERSION: v1.3.2-WILSY-PYTHON-DOCSTRING-SEAL-CERT
# AUTHORITY BOUNDARY: structural governance tests only.
# TENANT POSTURE: no tenant access or authority.
# FAIL-CLOSED POSTURE: missing, divergent, or unsealed artifact metadata fails.
# FINANCIAL EXECUTION AUTHORITY: none; Kennel EOS exclusively owns execution.
# END OF WILSY OS SOVEREIGN ARTIFACT
