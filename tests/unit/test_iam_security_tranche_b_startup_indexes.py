"""IAM security Tranche-B canonical startup index certification."""
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
        == "v1.28.0-P3-R3G-S6-A2-IAM-SECURITY-STARTUP-INDEX-BOOTSTRAP"
    )


# ARTIFACT: test_iam_security_tranche_b_startup_indexes.py
# VERSION: v1.0.0-P3-R3G-S6-A2-IAM-SECURITY-STARTUP-INDEX-BOOTSTRAP
# AUTHORITY BOUNDARY: Startup index observation only; no IAM/security issuance.
# TENANT POSTURE: No tenant authority created.
# FAIL-CLOSED POSTURE: Missing startup ownership or authority-bearing behavior fails.
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS remains exclusive.
# END OF WILSY OS SOVEREIGN ARTIFACT
