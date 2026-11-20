"""WILSY OS system-services startup regression certificate.

TITLE: System Services Case Startup Certificate
VERSION: v1.0.9-AI-PROVIDER-COMPOSITION-CERT
AUTHORITY: Wilsy OS Core Governance
EPITOME: Proves canonical startup installs system-service case indexes without
         creating cases, permission grants, or tenant authority.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tests/unit/test_system_services_case_startup.py
COLLABORATION / OWNERSHIP: Python EOS API composition and system-services owners.
CERTIFICATION / UPDATE DATE: 2026-11-10
CHANGELOG: v1.0.9-AI-PROVIDER-COMPOSITION-CERT pins the canonical provider composition version while preserving all index ownership, readiness, tenant and IAM denial assertions.
CHANGELOG: v1.0.8-TRUSTED-SCAN-INDEX-COMPOSITION-CERT verifies the trusted scan-clearance index bootstrap version without rolling back source indexes.
CHANGELOG: v1.0.9-AI-PROVIDER-COMPOSITION-CERT pins
  task quarantined attachment manifest and command replay indexes to
  canonical EOS startup without provisioning provider objects or users.
CHANGELOG: v1.0.9-AI-PROVIDER-COMPOSITION-CERT pins exact reviewer
business decision and idempotent event indexes at EOS startup.
CHANGELOG: v1.0.9-AI-PROVIDER-COMPOSITION-CERT pins recipient inbox and receipt
indexes at canonical EOS startup; no messages or recipients are created.
CHANGELOG: v1.0.9-AI-PROVIDER-COMPOSITION-CERT pins exact-task comment
indexes in canonical EOS readiness, without creating message records.
CHANGELOG: v1.0.9-AI-PROVIDER-COMPOSITION-CERT pins additive task/dependency indexes
at canonical EOS startup; no synthetic tasks or IAM are created.
CHANGELOG: v1.0.9-AI-PROVIDER-COMPOSITION-CERT pins additive exact-tenant participant indexes at canonical startup; no grants or records are issued.
 2026-11-18 v1.0.9-AI-PROVIDER-COMPOSITION-CERT aligns canonical
server-version certification with additive Project Notes startup indexes;
no existing Global Principal or System Services authority is changed.
CHANGELOG: v1.0.9-AI-PROVIDER-COMPOSITION-CERT aligns the public composition
           version assertion with the mounted authenticated QR router release.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2.
SECURITY / PRIVACY POSTURE: Static source inspection; no database or secret access.
TENANT BOUNDARY: Startup index readiness creates no tenant or principal authority.
AUTHORITY BOUNDARY: Test certificate only; no cases or grants are issued.
FINANCIAL AUTHORITY BOUNDARY: Kennel EOS exclusively owns execution and settlement.
"""
from __future__ import annotations

import inspect

from tools.eos.api import server


def test_system_services_case_indexes_are_registered_by_canonical_startup() -> None:
    source = inspect.getsource(server.WilsyAPIServer._build_app)
    start = source.index("async def start_database")
    end = source.index("async def stop_database")
    startup = source[start:end]
    assert "SupportCaseRegistry(" in startup
    assert 'database["system_service_cases"]' in startup
    assert 'database["system_service_case_events"]' in startup
    assert ".ensure_indexes()" in startup
    assert "system_services_case_indexes_ready = client is not None" in startup


def test_system_services_case_storage_readiness_is_not_an_authorization_grant() -> None:
    source = inspect.getsource(server.WilsyAPIServer._build_app)
    assert "system_services_case_indexes_ready = False" in source
    assert "system_services_case_indexes_ready" not in source[
        source.index("# Sovereign mounting order") :
    ]


def test_system_services_startup_does_not_create_cases_or_grants() -> None:
    source = inspect.getsource(server.WilsyAPIServer._build_app)
    start = source.index("async def start_database")
    end = source.index("async def stop_database")
    startup = source[start:end]
    for forbidden in (
        ".create(",
        ".transition(",
        ".assign(",
        ".revoke(",
        "create_or_replay(",
    ):
        assert forbidden not in startup


def test_system_services_server_version_tracks_governed_router_composition() -> None:
    assert server.VERSION == "v1.55.0-RESOLVED-LEGAL-AI-PROVIDER-COMPOSITION"


# ARTIFACT: System Services Case Startup Certificate
# VERSION: v1.0.9-AI-PROVIDER-COMPOSITION-CERT
# AUTHORITY BOUNDARY: startup index ownership and composition version only
# TENANT POSTURE: no tenant data is read or mutated
# FAIL-CLOSED POSTURE: readiness is not converted into case or IAM authority
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively
# END OF WILSY OS SOVEREIGN ARTIFACT
