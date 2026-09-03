"""WILSY OS — WILSY AI VAS direct contract certificate.

TITLE:
    WILSY AI VAS Access Direct Contract Certificate

VERSION:
    v1.0.2-WILSY-AI-VAS-ACCESS-CERT

AUTHORITY:
    Wilsy OS Core Governance

EPITOME:
    Direct deterministic certification of the immutable WILSY AI VAS access
    envelope, its evidence requirements, advisory-only capability firewall,
    tenant/context non-authority posture, structural sovereignty, and explicit
    separation from operational real-world certification.

ABSOLUTE CANONICAL PATH:
    /Users/wilsonkhanyezi/legal-doc-system/tests/eos/intelligence/test_wilsy_ai_vas_access.py

COLLABORATION / OWNERSHIP:
    Wilson Khanyezi / Wilsy OS Core Engineering

CERTIFICATION / UPDATE DATE:
    2026-09-03

CHANGELOG:
    v1.0.2-WILSY-AI-VAS-ACCESS-CERT:
        Full institutional artifact remediation under repository AGENTS.md.
        Adds complete sovereign header, explicit certification classification,
        real-world certification boundary, synchronized certificate version,
        self-structural certification, and mandatory terminal artifact seal.
        Existing VAS behavioral assertions remain intact.

    v1.0.1-WILSY-AI-VAS-ACCESS-CERT:
        Added AGENTS-oriented production artifact structural assertions and
        Intelligence Dock compatibility coverage.

    v1.0.0-WILSY-AI-VAS-ACCESS-CERT:
        Established direct contract tests for immutable VAS access semantics,
        mandatory evidence, quota failure, domain gating, deterministic
        checksum behavior, and non-advisory capability rejection.

COMPLIANCE:
    POPIA section 19; GDPR Article 32; SOC 2 CC7.2; ISO 27001-aligned testing
    of tenant separation, evidence minimization, integrity, and fail-closed
    access behavior. These references describe tested technical posture and do
    not manufacture external certification.

SECURITY / PRIVACY POSTURE:
    Test fixtures use synthetic opaque identifiers only and do not contain
    credentials, tokens, secrets, real tenant data, payment destinations, or
    production evidence payloads. This direct certificate performs no network,
    database, subscription, entitlement, or financial mutation.

TENANT BOUNDARY:
    The certificate proves that tenant, principal, scope, dashboard, business
    profile, domains, and capabilities remain explicit bounded inputs. It does
    not prove real persisted membership or tenant authorization; that belongs
    to operational integration certification.

AUTHORITY BOUNDARY:
    This file certifies the pure WILSY AI VAS access contract only. It does not
    establish identity, tenant membership, entitlement, subscription truth,
    persisted usage truth, business-profile truth, operational AI wiring,
    approval, business mutation, workflow dispatch, or execution authority.

FINANCIAL AUTHORITY BOUNDARY:
    Kennel EOS remains the exclusive financial execution authority. No test in
    this certificate may treat approval, entitlement, recommendation, payment
    attempt, release authorization, or execution as settlement.

CERTIFICATION CLASSIFICATION:
    DIRECT CONTRACT / STRUCTURAL CERTIFICATE.

REAL-WORLD CERTIFICATION BOUNDARY:
    THIS FILE IS NOT FINAL REAL-WORLD PRODUCTION CERTIFICATION.
    Production readiness additionally requires real Python authority and real
    persistence integration tests wherever those truths are persisted.
    Synthetic fixtures in this file MUST NOT be represented as operational
    tenant, subscription, entitlement, metering, or settlement evidence.

CONSTITUTION:
    NO EVIDENCE = NO FACT.
    NO ENTITLEMENT = NO AI COMPUTE.
    OBSERVED FACT != DERIVED SIGNAL != AI INFERENCE != RECOMMENDATION
                  != AUTHORIZATION != EXECUTION.
"""

from __future__ import annotations

import ast
from dataclasses import FrozenInstanceError
from pathlib import Path
import re

import pytest

from tools.eos.intelligence.domain.vas_access import (
    ADVISORY_AI_CAPABILITIES,
    VERSION as VAS_VERSION,
    WilsyAIVASAccess,
)


TEST_VERSION = "v1.0.2-WILSY-AI-VAS-ACCESS-CERT"
_EXPECTED_VAS_VERSION = "v1.0.1-WILSY-AI-VAS-ACCESS"

_PRODUCTION_PATH = Path(
    "tools/eos/intelligence/domain/vas_access.py"
)

_CERTIFICATE_PATH = Path(__file__)


def _access(**changes: object) -> WilsyAIVASAccess:
    """Build one explicit synthetic contract fixture.

    This helper exercises pure construction only. It is intentionally not an
    operational tenant/subscription/entitlement fixture and must never be used
    as evidence of persisted real-world certification.
    """
    values = {
        "tenant_id": "TENANT-001",
        "principal_id": "PRINCIPAL-001",
        "scope_ref": "SCOPE-001",
        "entitlement_ref": "ENTITLEMENT-001",
        "subscription_ref": "SUBSCRIPTION-001",
        "entitlement_evidence_refs": (
            "EVIDENCE-ENTITLEMENT-001",
        ),
        "usage_evidence_refs": (
            "EVIDENCE-USAGE-SNAPSHOT-001",
        ),
        "business_profile_ref": "BUSINESS-PROFILE-001",
        "business_profile_evidence_refs": (
            "EVIDENCE-BUSINESS-PROFILE-001",
        ),
        "business_type": "Legal Practice",
        "dashboard_id": "DASHBOARD-LEGAL-001",
        "dashboard_domain": "LEGAL",
        "allowed_domains": (
            "BILLING",
            "CRM",
            "LEGAL",
        ),
        "allowed_capabilities": (
            "EXPLAIN",
            "RECOMMEND",
            "SUMMARIZE",
        ),
        "usage_limit": 1000,
        "usage_consumed": 125,
        "evaluated_at":
            "2026-09-03T12:00:00+02:00",
    }

    values.update(changes)

    return WilsyAIVASAccess(**values)  # type: ignore[arg-type]


def test_versions_are_exact() -> None:
    assert VAS_VERSION == _EXPECTED_VAS_VERSION
    assert TEST_VERSION == "v1.0.2-WILSY-AI-VAS-ACCESS-CERT"


def test_access_is_explicit_and_deterministic() -> None:
    first = _access()
    second = _access()

    assert first == second
    assert first.checksum == second.checksum
    assert first.checksum.startswith("sha3-512:")
    assert first.usage_remaining == 875
    assert (
        first.evaluated_at
        == "2026-09-03T10:00:00+00:00"
    )


def test_access_is_immutable() -> None:
    access = _access()

    with pytest.raises(FrozenInstanceError):
        access.tenant_id = "OTHER"  # type: ignore[misc]


def test_entitlement_evidence_is_mandatory() -> None:
    with pytest.raises(
        ValueError,
        match="entitlement_evidence_refs",
    ):
        _access(entitlement_evidence_refs=())


def test_usage_snapshot_evidence_is_mandatory() -> None:
    with pytest.raises(
        ValueError,
        match="usage_evidence_refs",
    ):
        _access(usage_evidence_refs=())


def test_business_profile_evidence_is_mandatory() -> None:
    with pytest.raises(
        ValueError,
        match="business_profile_evidence_refs",
    ):
        _access(business_profile_evidence_refs=())


def test_exhausted_usage_fails_closed() -> None:
    with pytest.raises(
        ValueError,
        match="^NO_ENTITLEMENT_CAPACITY$",
    ):
        _access(
            usage_limit=100,
            usage_consumed=100,
        )


def test_dashboard_domain_must_be_entitled() -> None:
    with pytest.raises(
        ValueError,
        match="^DASHBOARD_DOMAIN_NOT_ENTITLED$",
    ):
        _access(
            dashboard_domain="PAYROLL",
        )


def test_domains_and_capabilities_are_explicit() -> None:
    access = _access()

    assert access.permits_domain("legal")
    assert access.permits_domain("CRM")
    assert not access.permits_domain("PAYROLL")

    assert access.permits_capability("explain")
    assert access.permits_capability("RECOMMEND")
    assert not access.permits_capability("EXECUTE")

    assert ADVISORY_AI_CAPABILITIES == frozenset(
        {
            "EXPLAIN",
            "RECOMMEND",
            "SUMMARIZE",
        }
    )


def test_non_advisory_capability_fails_closed() -> None:
    for capability in (
        "APPROVE",
        "AUTHORIZE",
        "EXECUTE",
        "PAY",
        "RELEASE",
        "SETTLE",
    ):
        with pytest.raises(
            ValueError,
            match="^UNSUPPORTED_AI_CAPABILITY$",
        ):
            _access(
                allowed_capabilities=(capability,),
            )


def test_canonical_order_is_required() -> None:
    with pytest.raises(
        ValueError,
        match="canonical sorted order",
    ):
        _access(
            allowed_domains=(
                "LEGAL",
                "CRM",
            )
        )


def test_no_identity_or_time_defaults_exist() -> None:
    with pytest.raises(TypeError):
        WilsyAIVASAccess()  # type: ignore[call-arg]


def test_projection_does_not_create_execution_authority() -> None:
    projected = _access().to_dict()

    assert "execute" not in projected
    assert "payment" not in projected
    assert "release" not in projected
    assert "settlement" not in projected


def test_business_type_and_dashboard_are_context_not_authority() -> None:
    access = _access()

    assert access.business_type == "Legal Practice"
    assert access.dashboard_domain == "LEGAL"
    assert access.dashboard_domain in access.allowed_domains


def test_production_sovereign_header_version_and_end_seal_agree() -> None:
    source = _PRODUCTION_PATH.read_text(encoding="utf-8")

    header = re.search(
        r"(?m)^VERSION:\n\s+(v[^\n]+)$",
        source,
    )
    runtime = re.search(
        r'(?m)^VERSION = "([^"]+)"$',
        source,
    )
    seal = re.search(
        r"(?m)^# VERSION: (v[^\n]+)$",
        source,
    )

    assert header is not None
    assert runtime is not None
    assert seal is not None

    assert header.group(1) == _EXPECTED_VAS_VERSION
    assert runtime.group(1) == _EXPECTED_VAS_VERSION
    assert seal.group(1) == _EXPECTED_VAS_VERSION

    assert source.rstrip().endswith(
        "# END OF WILSY OS SOVEREIGN ARTIFACT"
    )


def test_production_sovereign_structure_contains_required_fields() -> None:
    source = _PRODUCTION_PATH.read_text(encoding="utf-8")

    required = (
        "TITLE:",
        "VERSION:",
        "AUTHORITY:",
        "EPITOME:",
        "ABSOLUTE CANONICAL PATH:",
        "COLLABORATION / OWNERSHIP:",
        "CERTIFICATION / UPDATE DATE:",
        "CHANGELOG:",
        "COMPLIANCE:",
        "SECURITY / PRIVACY POSTURE:",
        "TENANT BOUNDARY:",
        "AUTHORITY BOUNDARY:",
        "FINANCIAL AUTHORITY BOUNDARY:",
        "# ARTIFACT:",
        "# TENANT POSTURE:",
        "# FAIL-CLOSED POSTURE:",
        "# FINANCIAL EXECUTION AUTHORITY:",
        "# END OF WILSY OS SOVEREIGN ARTIFACT",
    )

    for token in required:
        assert token in source

    upper = source.upper()

    assert "TODO" not in upper
    assert "FIXME" not in upper


def test_exported_production_class_and_public_methods_are_documented() -> None:
    source = _PRODUCTION_PATH.read_text(encoding="utf-8")
    tree = ast.parse(source)

    classes = {
        node.name: node
        for node in tree.body
        if isinstance(node, ast.ClassDef)
    }

    target = classes["WilsyAIVASAccess"]

    assert ast.get_docstring(target)

    public_methods = {
        node.name: node
        for node in target.body
        if isinstance(
            node,
            (ast.FunctionDef, ast.AsyncFunctionDef),
        )
        and not node.name.startswith("_")
    }

    assert set(public_methods) == {
        "usage_remaining",
        "permits_domain",
        "permits_capability",
        "to_dict",
    }

    for node in public_methods.values():
        assert ast.get_docstring(node)


def test_certificate_itself_satisfies_sovereign_artifact_structure() -> None:
    source = _CERTIFICATE_PATH.read_text(encoding="utf-8")

    required = (
        "TITLE:",
        "VERSION:",
        "AUTHORITY:",
        "EPITOME:",
        "ABSOLUTE CANONICAL PATH:",
        "COLLABORATION / OWNERSHIP:",
        "CERTIFICATION / UPDATE DATE:",
        "CHANGELOG:",
        "COMPLIANCE:",
        "SECURITY / PRIVACY POSTURE:",
        "TENANT BOUNDARY:",
        "AUTHORITY BOUNDARY:",
        "FINANCIAL AUTHORITY BOUNDARY:",
        "CERTIFICATION CLASSIFICATION:",
        "REAL-WORLD CERTIFICATION BOUNDARY:",
        "# ARTIFACT:",
        "# VERSION:",
        "# AUTHORITY BOUNDARY:",
        "# TENANT POSTURE:",
        "# FAIL-CLOSED POSTURE:",
        "# FINANCIAL EXECUTION AUTHORITY:",
        "# END OF WILSY OS SOVEREIGN ARTIFACT",
    )

    for token in required:
        assert token in source

    header = re.search(
        r"(?m)^VERSION:\n\s+(v[^\n]+)$",
        source,
    )
    runtime = re.search(
        r'(?m)^TEST_VERSION = "([^"]+)"$',
        source,
    )
    seal = re.search(
        r"(?m)^# VERSION: (v[^\n]+)$",
        source,
    )

    assert header is not None
    assert runtime is not None
    assert seal is not None

    assert header.group(1) == TEST_VERSION
    assert runtime.group(1) == TEST_VERSION
    assert seal.group(1) == TEST_VERSION

    assert (
        "THIS FILE IS NOT FINAL REAL-WORLD PRODUCTION CERTIFICATION."
        in source
    )

    assert source.rstrip().endswith(
        "# END OF WILSY OS SOVEREIGN ARTIFACT"
    )


# =============================================================================
# WILSY OS SOVEREIGN ARTIFACT SEAL
# =============================================================================
# ARTIFACT: tests/eos/intelligence/test_wilsy_ai_vas_access.py
# VERSION: v1.0.2-WILSY-AI-VAS-ACCESS-CERT
# AUTHORITY BOUNDARY:
#   Direct contract and structural certification only. No authentication,
#   tenant membership, subscription, entitlement, metering, AI execution,
#   business mutation, approval, workflow dispatch, or persistence authority.
# TENANT POSTURE:
#   Synthetic opaque fixture identifiers only. This certificate is not evidence
#   of a real tenant, membership, persisted subscription, entitlement, or usage.
# FAIL-CLOSED POSTURE:
#   Contract failures remain explicit; this certificate cannot be used to
#   substitute for required real authority/persistence integration tests.
# FINANCIAL EXECUTION AUTHORITY:
#   Kennel EOS exclusively.
# END OF WILSY OS SOVEREIGN ARTIFACT
