import pytest

from tools.eos.system_services.runtime import (
    PLATFORM_WORKFORCE_SCOPE_ENV,
    build_system_services_runtime,
    configured_platform_workforce_scope_id,
    resolve_platform_workforce_scope_id,
)
from tools.eos.system_services.eos_authorizer import SystemServicesAuthorizationUnavailable


class Collection:
    def __init__(self):
        self.indexes = []

    def create_index(self, keys, **kwargs):
        self.indexes.append((keys, kwargs))
        return kwargs.get("name")


class Database:
    def __init__(self):
        self.collections = {}

    def __getitem__(self, name):
        return self.collections.setdefault(name, Collection())


def test_platform_workforce_scope_requires_trusted_explicit_configuration(monkeypatch):
    monkeypatch.delenv(PLATFORM_WORKFORCE_SCOPE_ENV, raising=False)
    with pytest.raises(SystemServicesAuthorizationUnavailable):
        configured_platform_workforce_scope_id()


@pytest.mark.parametrize("value", ["", " ", "wilsy-platform ", "*", "platform\\n"])
def test_platform_workforce_scope_rejects_invalid_values(value):
    with pytest.raises(SystemServicesAuthorizationUnavailable):
        resolve_platform_workforce_scope_id(value)


def test_platform_workforce_scope_accepts_existing_canonical_scope_identifier():
    assert resolve_platform_workforce_scope_id("wilsy-platform") == "wilsy-platform"


def test_runtime_composes_repositories_without_creating_authority_records():
    database = Database()
    case_registry, authorizer = build_system_services_runtime(
        database,
        platform_workforce_scope_id="wilsy-platform",
    )
    assert case_registry is not None
    assert authorizer is not None
    assert "principal_authorities" in database.collections
    assert "system_permission_assignments" in database.collections
    assert "workforce_relationship_history" in database.collections
