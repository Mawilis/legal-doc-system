# -*- coding: utf-8 -*-
"""Dedicated certification for the closed PrincipalStatus value contract.

VERSION: v1.0.0-WILSY-PRINCIPAL-STATUS-CERT
CHANGELOG: v1.0.0 certifies values, serialization, rejection, and immutability only.

This file does not certify lifecycle transitions, persistence, authentication,
authorization, credentials, tenancy, or financial authority.
"""
from enum import StrEnum

import pytest

from tools.eos.auth.principal_status import PrincipalStatus


def test_exact_members_and_order() -> None:
    assert list(PrincipalStatus) == [
        PrincipalStatus.ACTIVE,
        PrincipalStatus.SUSPENDED,
        PrincipalStatus.REVOKED,
    ]
    assert [member.name for member in PrincipalStatus] == ["ACTIVE", "SUSPENDED", "REVOKED"]


def test_exact_serialized_values() -> None:
    assert [member.value for member in PrincipalStatus] == ["ACTIVE", "SUSPENDED", "REVOKED"]


@pytest.mark.parametrize("value, expected", [("ACTIVE", PrincipalStatus.ACTIVE), ("SUSPENDED", PrincipalStatus.SUSPENDED), ("REVOKED", PrincipalStatus.REVOKED)])
def test_exact_string_construction(value: str, expected: PrincipalStatus) -> None:
    assert PrincipalStatus(value) is expected


@pytest.mark.parametrize("value", ["UNKNOWN", "active", "Active", "", " ACTIVE", "ACTIVE "])
def test_invalid_values_are_rejected(value: str) -> None:
    with pytest.raises(ValueError):
        PrincipalStatus(value)


def test_members_are_string_enum_values_and_hashable() -> None:
    assert all(isinstance(member, StrEnum) for member in PrincipalStatus)
    assert {PrincipalStatus.ACTIVE, PrincipalStatus.SUSPENDED, PrincipalStatus.REVOKED}.__len__() == 3
    assert PrincipalStatus.ACTIVE == "ACTIVE"


def test_repeated_construction_returns_singletons() -> None:
    assert PrincipalStatus("ACTIVE") is PrincipalStatus.ACTIVE
    assert PrincipalStatus("SUSPENDED") is PrincipalStatus.SUSPENDED
    assert PrincipalStatus("REVOKED") is PrincipalStatus.REVOKED


def test_no_custom_transition_api_or_extra_domain_data() -> None:
    assert not any(name in PrincipalStatus.__dict__ for name in ("activate", "suspend", "revoke", "reactivate", "transition", "can_transition"))
    assert all(member.__class__ is PrincipalStatus for member in PrincipalStatus)


# ARTIFACT: test_principal_status.py
# VERSION: v1.0.0-WILSY-PRINCIPAL-STATUS-CERT
# END OF WILSY OS SOVEREIGN ARTIFACT
