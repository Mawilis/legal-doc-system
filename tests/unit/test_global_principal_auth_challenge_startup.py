"""WILSY OS startup certification for global credential and challenge indexes.

TITLE: Global Principal Authentication Startup Index Certificate
VERSION: v1.0.1-GLOBAL-PRINCIPAL-CHALLENGE-STARTUP-TESTS
AUTHORITY: Verifies canonical EOS startup owns global credential and challenge index DDL.
EPITOME: Proves unique credential and one-time challenge indexes are installed
         before readiness is asserted and are never created by request handlers.
ABSOLUTE CANONICAL PATH:
    /Users/wilsonkhanyezi/legal-doc-system/tests/unit/test_global_principal_auth_challenge_startup.py
COLLABORATION / OWNERSHIP: Wilsy Core Engineering.
CERTIFICATION / UPDATE DATE: 2026-11-03.
CHANGELOG:
    v1.0.1-GLOBAL-PRINCIPAL-CHALLENGE-STARTUP-TESTS adds the durable global
    authentication rate-limit index to the required startup readiness set.
    v1.0.0 certifies credential/challenge index ownership and readiness lifecycle.
COMPLIANCE: Test artifact for POPIA section 19; GDPR Article 32; SOC 2 CC7.2.
SECURITY / PRIVACY POSTURE: Static composition inspection; no database connection or secrets.
TENANT BOUNDARY: Global credential indexes are tenant-neutral; challenge digests are scope-bound.
AUTHORITY BOUNDARY: Startup DDL only; no credentials, memberships or capacities are created.
FINANCIAL AUTHORITY BOUNDARY: No financial authority; Kennel EOS remains exclusive.
"""

from __future__ import annotations

import inspect

from tools.eos.api import server


def _startup_source() -> str:
    """Return only the canonical connected-database startup handler source."""
    source = inspect.getsource(server.WilsyAPIServer._build_app)
    start = source.index("async def start_database")
    end = source.index("async def stop_database")
    return source[start:end]


def _shutdown_source() -> str:
    """Return only the canonical database shutdown handler source."""
    source = inspect.getsource(server.WilsyAPIServer._build_app)
    start = source.index("async def stop_database")
    end = source.index("async def start_dunning_scheduler")
    return source[start:end]


def test_startup_installs_global_credential_and_challenge_indexes_before_readiness():
    source = _startup_source()
    credential = source.index("PrincipalCredentialRepository.ensure_indexes(")
    challenge = source.index("MembershipSelectionChallengeService.ensure_indexes(")
    factor = source.index("GlobalPrincipalTotpVerifier.ensure_indexes(")
    enrollment = source.index("GlobalPrincipalMfaEnrollmentService.ensure_indexes(")
    rate_limit = source.index("PrincipalAuthenticationRateLimit(")
    system_sessions = source.index("GlobalPrincipalSystemSessionAuthority.ensure_indexes(")
    system_readiness = source.index("global_principal_system_session_indexes_ready = client is not None")
    readiness = source.index("global_principal_auth_indexes_ready = client is not None")
    assert credential < challenge < factor < enrollment < system_sessions < rate_limit < readiness
    assert system_sessions < system_readiness < readiness
    assert "database[GLOBAL_PRINCIPAL_SYSTEM_SESSION_COLLECTION]" in source
    assert "database[GLOBAL_PRINCIPAL_SYSTEM_REFRESH_COLLECTION]" in source
    assert "database[PRINCIPAL_CREDENTIAL_COLLECTION]" in source
    assert "database[MEMBERSHIP_SELECTION_CHALLENGE_COLLECTION]" in source
    assert "database[GLOBAL_PRINCIPAL_MFA_FACTOR_COLLECTION]" in source
    assert "database[GLOBAL_PRINCIPAL_MFA_ENROLLMENT_CHALLENGE_COLLECTION]" in source
    assert "database[PRINCIPAL_AUTH_RATE_LIMIT_COLLECTION]" in source
    assert "kms_envelope.validate_access()" in source


def test_global_auth_index_readiness_defaults_and_shutdown_fail_closed():
    assert server.app.state.global_principal_auth_indexes_ready is False
    assert server.app.state.global_principal_mfa_enrollment_indexes_ready is False
    startup = _startup_source()
    shutdown = _shutdown_source()
    assert "global_principal_auth_indexes_ready = False" in startup
    assert "global_principal_auth_indexes_ready = False" in shutdown
    assert "global_principal_mfa_factor_indexes_ready = False" in startup
    assert "global_principal_mfa_factor_indexes_ready = False" in shutdown
    assert "global_principal_system_session_indexes_ready = False" in startup
    assert "global_principal_system_session_indexes_ready = False" in shutdown
    assert "global_principal_mfa_enrollment_indexes_ready = False" in startup
    assert "global_principal_mfa_enrollment_indexes_ready = False" in shutdown
    assert "global_principal_mfa_kms_envelope = None" in shutdown


def test_server_version_is_the_governed_global_auth_route_bootstrap():
    assert server.VERSION == "v1.41.0-GLOBAL-MFA-ENROLLMENT-AND-LEGACY-MIGRATION"


# ARTIFACT: test_global_principal_auth_challenge_startup.py
# VERSION: v1.0.1-GLOBAL-PRINCIPAL-CHALLENGE-STARTUP-TESTS
# AUTHORITY BOUNDARY: startup index ownership and readiness certification only
# TENANT POSTURE: global credential indexes remain tenant-neutral; challenge index stores no raw token
# FAIL-CLOSED POSTURE: readiness remains false unless connected startup completes both index declarations
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS remains exclusive
# END OF WILSY OS SOVEREIGN ARTIFACT
