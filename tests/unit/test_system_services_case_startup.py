"""WILSY OS system-services startup regression certificate.

TITLE: System Services Case Startup Certificate
VERSION: v1.0.0-EOS-QR-MOUNT-COMPOSITION-CERT
AUTHORITY: Wilsy OS Core Governance
EPITOME: Proves canonical startup installs system-service case indexes without
         creating cases, permission grants, or tenant authority.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tests/unit/test_system_services_case_startup.py
COLLABORATION / OWNERSHIP: Python EOS API composition and system-services owners.
CERTIFICATION / UPDATE DATE: 2026-11-10
CHANGELOG: v1.0.0-EOS-QR-MOUNT-COMPOSITION-CERT aligns the public composition
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
    assert server.VERSION == "v1.43.0-AUTHENTICATED-LEGACY-QR-ROUTER-MOUNT"


# ARTIFACT: System Services Case Startup Certificate
# VERSION: v1.0.0-EOS-QR-MOUNT-COMPOSITION-CERT
# AUTHORITY BOUNDARY: startup index ownership and composition version only
# TENANT POSTURE: no tenant data is read or mutated
# FAIL-CLOSED POSTURE: readiness is not converted into case or IAM authority
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively
# END OF WILSY OS SOVEREIGN ARTIFACT
