# -*- coding: utf-8 -*-
"""Bounded certification for the immutable PrincipalAuthority snapshot.

VERSION: v1.0.0-WILSY-PRINCIPAL-AUTHORITY-CERT
CHANGELOG: v1.0.0 certifies identity, status, revision, immutability, and exclusions only.
"""
from dataclasses import FrozenInstanceError, fields
from typing import cast

import pytest

from tools.eos.auth.principal_authority import PrincipalAuthority
from tools.eos.auth.principal_status import PrincipalStatus


@pytest.mark.parametrize("status", list(PrincipalStatus))
def test_valid_status_snapshots(status: PrincipalStatus) -> None:
    authority = PrincipalAuthority("principal-001", status, 0)
    assert authority.principal_id == "principal-001"
    assert authority.status is status
    assert authority.revision == 0


def test_principal_id_is_retained_exactly() -> None:
    assert PrincipalAuthority("Opaque-ID/001", PrincipalStatus.ACTIVE, 4).principal_id == "Opaque-ID/001"


@pytest.mark.parametrize("value", ["", "   ", " principal", "principal "])
def test_invalid_principal_id_rejected(value: str) -> None:
    with pytest.raises(ValueError):
        PrincipalAuthority(value, PrincipalStatus.ACTIVE, 0)


def test_missing_or_non_string_principal_id_rejected() -> None:
    with pytest.raises((TypeError, ValueError)):
        PrincipalAuthority(cast(str, None), PrincipalStatus.ACTIVE, 0)


def test_invalid_status_rejected_without_string_coercion() -> None:
    with pytest.raises(TypeError):
        PrincipalAuthority("principal-001", cast(PrincipalStatus, "ACTIVE"), 0)


@pytest.mark.parametrize("revision", [-1, -100])
def test_negative_revision_rejected(revision: int) -> None:
    with pytest.raises(ValueError):
        PrincipalAuthority("principal-001", PrincipalStatus.ACTIVE, revision)


def test_boolean_revision_rejected() -> None:
    with pytest.raises(TypeError):
        PrincipalAuthority("principal-001", PrincipalStatus.ACTIVE, cast(int, True))


def test_non_integer_revision_rejected() -> None:
    with pytest.raises(TypeError):
        PrincipalAuthority("principal-001", PrincipalStatus.ACTIVE, cast(int, "0"))


def test_record_is_immutable_and_hashable() -> None:
    authority = PrincipalAuthority("principal-001", PrincipalStatus.ACTIVE, 0)
    with pytest.raises(FrozenInstanceError):
        setattr(authority, "status", PrincipalStatus.REVOKED)
    assert hash(authority) == hash(PrincipalAuthority("principal-001", PrincipalStatus.ACTIVE, 0))


def test_record_has_exact_fields_and_no_mutation_methods() -> None:
    assert [field.name for field in fields(PrincipalAuthority)] == ["principal_id", "status", "revision"]
    assert not any(name in PrincipalAuthority.__dict__ for name in ("activate", "suspend", "revoke", "restore", "transition", "set_status", "increment_revision"))


def test_record_excludes_other_authorities() -> None:
    names = {field.name for field in fields(PrincipalAuthority)}
    assert not names.intersection({"tenant_id", "roles", "permissions", "scopes", "credential_id", "jwt_id", "api_key_id", "kind", "principal_kind", "is_service_account", "email", "username", "created_at", "updated_at", "financial_authority"})


def test_equality_is_deterministic_and_material_fields_differ() -> None:
    base = PrincipalAuthority("principal-001", PrincipalStatus.ACTIVE, 0)
    assert base == PrincipalAuthority("principal-001", PrincipalStatus.ACTIVE, 0)
    assert base != PrincipalAuthority("principal-001", PrincipalStatus.SUSPENDED, 0)
    assert base != PrincipalAuthority("principal-001", PrincipalStatus.ACTIVE, 1)
    assert base != PrincipalAuthority("principal-002", PrincipalStatus.ACTIVE, 0)


def test_zero_and_large_non_negative_revisions_are_valid() -> None:
    assert PrincipalAuthority("principal-001", PrincipalStatus.ACTIVE, 0).revision == 0
    assert PrincipalAuthority("principal-001", PrincipalStatus.ACTIVE, 2**63).revision == 2**63


# ARTIFACT: test_principal_authority.py
# VERSION: v1.0.0-WILSY-PRINCIPAL-AUTHORITY-CERT
# END OF WILSY OS SOVEREIGN ARTIFACT
