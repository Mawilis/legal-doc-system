"""WILSY OS IAM Security Tranche-B Startup Index Certificate.
TITLE: IAM Security Tranche-B Startup Index Certificate
VERSION: v1.0.1-IAM-SECURITY-STARTUP-V1.43-ALIGNMENT
AUTHORITY: Wilsy OS Core Governance
EPITOME: Certifies canonical startup index registration for the five Tranche-B
         security registries without issuing security or business authority.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tests/unit/test_iam_security_tranche_b_startup_indexes.py
COLLABORATION / OWNERSHIP: Python EOS startup composition and security registry owners.
CERTIFICATION / UPDATE DATE: 2026-11-10
CHANGELOG: v1.0.1-IAM-SECURITY-STARTUP-V1.43-ALIGNMENT pins the startup certificate to the current server release; index assertions are unchanged.
CHANGELOG: v1.0.0-P3-R3G-S6-A2-IAM-SECURITY-STARTUP-INDEX-BOOTSTRAP established the five Tranche-B startup index assertions.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2.
SECURITY / PRIVACY POSTURE: Static startup inspection only; no credentials, tenant data, or evidence rows are read.
TENANT BOUNDARY: Startup index registration grants no tenant access or scope.
AUTHORITY BOUNDARY: Read-only startup composition evidence; no IAM/security issuance authority.
FINANCIAL AUTHORITY BOUNDARY: None; Kennel EOS remains exclusive.
FAIL-CLOSED POSTURE: Missing index registration or authority-bearing startup behavior fails certification.
"""
from __future__ import annotations

import inspect

from tools.eos.api import server


REGISTRIES = (
    "InternalServiceReplayRegistry",
    "InternalServiceWorkloadCredentialRegistry",
    "PrivilegedWorkloadTrustCurrentnessRegistry",
    "PrivilegedNoninteractiveSecurityProofRegistry",
    "PrivilegedSecurityAssuranceEvidenceRegistry",
)


def _startup() -> str:
    source = inspect.getsource(
        server.WilsyAPIServer._build_app
    )
    start = source.index(
        "async def start_database"
    )
    end = source.index(
        "async def stop_database"
    )
    return source[start:end]


def test_startup_owns_all_five_tranche_b_index_topologies() -> None:
    source = _startup()

    for registry in REGISTRIES:
        assert registry in source

    assert (
        "InternalServiceReplayRegistry.ensure_indexes("
        in source
    )

    for registry in REGISTRIES[1:]:
        assert (
            f"{registry}("
            in source
        )


def test_startup_bootstrap_creates_no_security_or_business_authority() -> None:
    source = _startup()

    for forbidden in (
        "consume_once(",
        "create_or_replay(",
        ".transition(",
        ".rotate(",
        "grant_role",
        "issue_credential",
        "activate_privilege",
    ):
        assert forbidden not in source


def test_server_version_is_tranche_b_bootstrap_version() -> None:
    assert (
        server.VERSION
        == "v1.43.0-AUTHENTICATED-LEGACY-QR-ROUTER-MOUNT"
    )


# ARTIFACT: test_iam_security_tranche_b_startup_indexes.py
# VERSION: v1.0.1-IAM-SECURITY-STARTUP-V1.43-ALIGNMENT
# AUTHORITY BOUNDARY: Startup index observation only; no IAM/security issuance.
# TENANT POSTURE: No tenant authority created.
# FAIL-CLOSED POSTURE: Missing startup ownership or authority-bearing behavior fails.
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS remains exclusive.
# END OF WILSY OS SOVEREIGN ARTIFACT
