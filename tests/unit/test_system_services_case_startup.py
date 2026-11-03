from __future__ import annotations

import inspect

from tools.eos.api import server


def test_system_services_case_indexes_are_registered_by_canonical_startup():
    source = inspect.getsource(server.WilsyAPIServer._build_app)
    start = source.index("async def start_database")
    end = source.index("async def stop_database")
    startup = source[start:end]
    assert "SupportCaseRegistry(" in startup
    assert 'database["system_service_cases"]' in startup
    assert 'database["system_service_case_events"]' in startup
    assert ".ensure_indexes()" in startup
    assert "system_services_case_indexes_ready = client is not None" in startup


def test_system_services_case_storage_readiness_is_not_an_authorization_grant():
    source = inspect.getsource(server.WilsyAPIServer._build_app)
    assert "system_services_case_indexes_ready = False" in source
    assert "system_services_case_indexes_ready" not in source[source.index("# Sovereign mounting order"):]


def test_system_services_startup_does_not_create_cases_or_grants():
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


def test_system_services_server_version_tracks_case_index_bootstrap():
    assert server.VERSION == "v1.41.0-GLOBAL-MFA-ENROLLMENT-AND-LEGACY-MIGRATION"
