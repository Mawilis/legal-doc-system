"""TITLE: Authority Namespace Canon Certification.
VERSION: v1.0.1-AUTHORITY-NAMESPACE-CERT
AUTHORITY: Tests the immutable namespace classification contract only.
EPITOME: Proves namespace separation and fail-closed migration metadata.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tests/unit/test_authority_namespace.py
COLLABORATION / OWNERSHIP: Wilson Khanyezi / Wilsy Core Engineering.
CERTIFICATION/UPDATE DATE: 2026-08-30.
CHANGELOG: v1.0.1 substantively certifies 30 namespace security properties and immutable migration metadata.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2; ISO 27001.
SECURITY/PRIVACY POSTURE: No credentials, JWTs, Node objects, tenant sentinels, or financial authority are processed.
TENANT BOUNDARY: Classification never proves tenant membership.
AUTHORITY BOUNDARY: Certification covers namespace semantics only.
FINANCIAL AUTHORITY BOUNDARY: Kennel EOS remains exclusive.
"""
from dataclasses import FrozenInstanceError

import pytest
from tools.eos.auth import authority_namespace as namespace_module

from tools.eos.auth.authority_namespace import (
    AuthorityNamespace, PrincipalKind, canonical_metadata, classify_legacy, metadata,
)


def test_thirty_properties():
    ns = tuple(AuthorityNamespace)
    assert len(ns) == 5  # P01
    assert ns == (AuthorityNamespace.SYSTEM, AuthorityNamespace.TENANT, AuthorityNamespace.DOMAIN, AuthorityNamespace.PROFILE, AuthorityNamespace.SERVICE)  # P02
    assert len(set(ns)) == 5  # P03
    assert metadata("SYSTEM").authority_capable is True  # P04
    assert metadata("TENANT").authority_capable is True  # P05
    assert metadata("SERVICE").authority_capable is True  # P06
    assert metadata("DOMAIN").authority_capable is False  # P07
    assert metadata("PROFILE").authority_capable is False  # P08
    assert metadata("SYSTEM").principal_kind is PrincipalKind.HUMAN  # P09
    assert metadata("TENANT").tenant_membership_required is True  # P10
    assert metadata("SERVICE").principal_kind is PrincipalKind.SERVICE  # P11
    assert metadata("DOMAIN").principal_kind is PrincipalKind.NON_PRINCIPAL_CLASSIFICATION  # P12
    assert metadata("PROFILE").principal_kind is PrincipalKind.NON_PRINCIPAL_CLASSIFICATION  # P13
    assert metadata("SYSTEM").explicit_target_scope_required_for_cross_tenant is True  # P14
    assert metadata("SERVICE").service_scope is True  # P15
    assert metadata("SYSTEM").authority_capable and not hasattr(metadata("SYSTEM"), "authorized")  # P16
    aliases = {"founder": AuthorityNamespace.SYSTEM, "FOUNDER": AuthorityNamespace.SYSTEM, "sovereign": AuthorityNamespace.SYSTEM, "SOVEREIGN": AuthorityNamespace.SYSTEM, "omega": AuthorityNamespace.SYSTEM, "OMEGA": AuthorityNamespace.SYSTEM, "super_admin": AuthorityNamespace.SYSTEM, "SUPER_ADMIN": AuthorityNamespace.SYSTEM, "superadmin": AuthorityNamespace.SYSTEM, "PLATFORM_ADMIN": AuthorityNamespace.SYSTEM, "tenant_owner": AuthorityNamespace.TENANT}
    assert all(classify_legacy(value) is target and not hasattr(classify_legacy(value), "permissions") for value, target in aliases.items())  # P17
    assert classify_legacy("tenant_owner") is AuthorityNamespace.TENANT  # P18
    assert metadata("DOMAIN").authority_capable is False and classify_legacy("lawyer") is AuthorityNamespace.DOMAIN  # P19
    assert metadata("PROFILE").authority_capable is False and classify_legacy("investor") is AuthorityNamespace.PROFILE  # P20
    assert classify_legacy("admin") is None  # P21
    assert classify_legacy("GLOBAL_ROOT") is None  # P22
    assert classify_legacy("MASTER") is None  # P23
    assert classify_legacy(None) is None  # P24
    assert classify_legacy(" unknown ") is None  # P25
    assert classify_legacy("unknown") is None  # P26
    assert classify_legacy({"role": "admin"}) is None  # P27
    assert canonical_metadata() == canonical_metadata() and isinstance(canonical_metadata(), bytes)  # P28
    assert metadata("TENANT").tenant_membership_required and not hasattr(metadata("TENANT"), "membership_proven")  # P29
    assert metadata("SERVICE").principal_kind is not PrincipalKind.HUMAN  # P30


@pytest.mark.parametrize("value", [None, "", " ", "\t", "\n", "\r\n", "Admin", "ADMIN", "ROOT", "SYSTEM", "WILSY_ROOT", "WILSY_SOVEREIGN_ROOT", "WILSY_GLOBAL_ROOT", "GLOBAL_ROOT", "MASTER", "not-known"])
def test_negative_inputs_fail_closed(value):
    assert classify_legacy(value) is None


def test_every_production_legacy_alias_is_publicly_certified():
    assert namespace_module._LEGACY
    for alias in namespace_module._LEGACY:
        result = classify_legacy(alias)
        assert result is namespace_module._LEGACY[alias]
        assert alias not in {item.value for item in AuthorityNamespace}
        assert not hasattr(result, "authorized")
        assert not hasattr(result, "allowed")
        assert not hasattr(result, "permissions")


def test_every_production_ambiguous_alias_denies():
    for alias in namespace_module._AMBIGUOUS:
        assert classify_legacy(alias) is None


def test_unknown_namespace_fails_closed():
    with pytest.raises(ValueError, match="UNKNOWN_AUTHORITY_NAMESPACE"):
        metadata("NOPE")


def test_metadata_is_immutable():
    with pytest.raises(FrozenInstanceError):
        metadata("SYSTEM").authority_capable = False  # type: ignore[misc,assignment]


def test_legacy_metadata_is_immutable():
    from tools.eos.auth import authority_namespace as module
    with pytest.raises(TypeError):
        module._LEGACY["new"] = AuthorityNamespace.SYSTEM  # type: ignore[index]
    with pytest.raises(TypeError):
        del module._LEGACY["founder"]  # type: ignore[index]


def test_legacy_is_migration_metadata_not_authorization():
    assert not hasattr(classify_legacy("founder"), "permissions")


def test_canonical_round_trip():
    import json
    assert tuple(item["namespace"] for item in json.loads(canonical_metadata())) == tuple(item.value for item in AuthorityNamespace)


# ARTIFACT: test_authority_namespace.py
# VERSION: v1.0.1-AUTHORITY-NAMESPACE-CERT
# AUTHORITY BOUNDARY: certifies namespace separation only
# TENANT POSTURE: no membership or tenant authority is fabricated
# FAIL-CLOSED POSTURE: malformed and ambiguous values deny
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS remains exclusive
# END OF WILSY OS SOVEREIGN ARTIFACT
