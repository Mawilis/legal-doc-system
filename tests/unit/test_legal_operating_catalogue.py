"""TITLE: G7A Global Legal Operating Catalogue direct certificate.

VERSION: v1.0.1-G7A-GLOBAL-LEGAL-OPERATING-CATALOGUE-CERT
AUTHORITY: Wilsy OS Core Governance / Python EOS Legal Operations
EPITOME: Certifies deterministic, immutable, tenant-neutral catalogue semantics
         and the absence of IAM, commercial, or financial authority.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tests/unit/test_legal_operating_catalogue.py
COLLABORATION / OWNERSHIP: G7A direct pure-domain certificate only.
CERTIFICATION / UPDATE DATE: 2026-10-15
CHANGELOG: v1.0.1 certifies the sovereign metadata and authority exclusions.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2; ISO 27001.
SECURITY / PRIVACY POSTURE: Uses no tenant, principal, credential, or PII data.
TENANT BOUNDARY: Proves global vocabulary only; no tenant activation is inferred.
AUTHORITY BOUNDARY: Tests description and evidence flags, never authorization.
FINANCIAL AUTHORITY BOUNDARY: None; Kennel EOS exclusively executes or settles.
"""
from __future__ import annotations

import hashlib
import json
import operator
from typing import Any, cast

import pytest

from tools.eos.legal_operations.domain.legal_operating_catalogue import (
    CATALOGUE_FINGERPRINT,
    CATALOGUE_IDENTITY,
    ITEMS_BY_DIMENSION,
    ITEMS_BY_ID,
    LegalOperatingCatalogueError,
    LegalOperatingDimension,
    SCHEMA,
    VERSION,
    get_legal_operating_item,
    list_items_for_dimension,
    list_legal_operating_dimensions,
    list_legal_operating_items,
)


def test_identity_is_exact() -> None:
    assert VERSION == "v1.0.1-G7A-GLOBAL-LEGAL-OPERATING-CATALOGUE"
    assert SCHEMA == "WILSY-GLOBAL-LEGAL-OPERATING-CATALOGUE/V1"
    assert CATALOGUE_IDENTITY == "WILSY_GLOBAL_LEGAL_OPERATING_CATALOGUE"


def test_all_dimensions_are_present() -> None:
    expected = {
        "ORGANIZATIONAL_PERSONA",
        "SENIORITY_POSITION",
        "PROFESSIONAL_QUALIFICATION",
        "TRAINING_STATUS",
        "REGULATORY_APPOINTMENT",
        "LEADERSHIP_APPOINTMENT",
        "PRACTICE_FUNCTION",
        "LEGAL_OPERATIONS_FUNCTION",
        "RISK_COMPLIANCE_FUNCTION",
        "KNOWLEDGE_FUNCTION",
        "FINANCE_COMMERCIAL_FUNCTION",
        "TECHNOLOGY_DATA_FUNCTION",
        "PEOPLE_FUNCTION",
        "BUSINESS_DEVELOPMENT_FUNCTION",
        "INFORMATION_DELIVERY_FUNCTION",
        "FIRM_OPERATIONS_FUNCTION",
        "EXTERNAL_ECOSYSTEM_PERSONA",
        "JURISDICTION_OVERLAY",
    }
    assert {
        item.value
        for item in list_legal_operating_dimensions()
    } == expected


def test_ids_are_unique_and_uppercase() -> None:
    items = list_legal_operating_items()
    ids = [item.item_id for item in items]
    assert len(ids) == len(set(ids))
    assert all(value == value.upper() for value in ids)
    assert set(ids) == set(ITEMS_BY_ID)


def test_dimension_mapping_is_total_and_exact() -> None:
    flattened = []
    for dimension in LegalOperatingDimension:
        rows = list_items_for_dimension(dimension)
        assert rows == ITEMS_BY_DIMENSION[dimension]
        flattened.extend(rows)
    assert tuple(flattened) != ()
    assert set(flattened) == set(list_legal_operating_items())


def test_existing_wilsy_personas_are_represented() -> None:
    expected = {
        "PERSONA_PARTNER",
        "PERSONA_ATTORNEY",
        "PERSONA_PARALEGAL",
        "PERSONA_LEGAL_SECRETARY",
        "PERSONA_LEGAL_FINANCE",
        "PERSONA_SHERIFF",
        "PERSONA_DEPUTY",
        "PERSONA_CLIENT",
    }
    assert expected <= set(ITEMS_BY_ID)


def test_professional_and_appointment_items_require_evidence() -> None:
    for item in list_items_for_dimension(
        LegalOperatingDimension.PROFESSIONAL_QUALIFICATION
    ):
        assert item.requires_professional_evidence is True

    for item in list_items_for_dimension(
        LegalOperatingDimension.TRAINING_STATUS
    ):
        assert item.requires_professional_evidence is True

    for item in list_items_for_dimension(
        LegalOperatingDimension.REGULATORY_APPOINTMENT
    ):
        assert item.requires_appointment_evidence is True


def test_catalogue_contains_no_permission_or_commercial_authority_fields() -> None:
    for item in list_legal_operating_items():
        keys = set(item.semantic_dict())
        assert keys == {
            "item_id",
            "dimension",
            "label",
            "description",
            "requires_professional_evidence",
            "requires_appointment_evidence",
        }


def test_catalogue_contains_no_tenant_entitlement_or_execution_truth() -> None:
    forbidden = {
        "tenant_id",
        "principal_id",
        "permission",
        "authorization_role",
        "plan_id",
        "subscription_id",
        "product_id",
        "entitlement_id",
        "matter_id",
        "payment_status",
        "settlement_status",
    }
    for item in list_legal_operating_items():
        assert forbidden.isdisjoint(item.semantic_dict())


def test_finance_and_trust_labels_do_not_create_financial_authority() -> None:
    trust = get_legal_operating_item("FINANCE_TRUST_ACCOUNTING")
    signatory = get_legal_operating_item("APPOINTMENT_TRUST_SIGNATORY")
    assert trust.dimension is LegalOperatingDimension.FINANCE_COMMERCIAL_FUNCTION
    assert signatory.dimension is LegalOperatingDimension.REGULATORY_APPOINTMENT
    assert signatory.requires_appointment_evidence is True


def test_unknown_item_and_dimension_fail_closed() -> None:
    with pytest.raises(
        LegalOperatingCatalogueError,
        match="G7A_UNKNOWN_ITEM",
    ):
        get_legal_operating_item("NOT_REAL")

    with pytest.raises(
        LegalOperatingCatalogueError,
        match="G7A_UNKNOWN_ITEM",
    ):
        get_legal_operating_item("persona_partner")

    with pytest.raises(
        LegalOperatingCatalogueError,
        match="G7A_UNKNOWN_DIMENSION",
    ):
        list_items_for_dimension("NOT_REAL")


def test_fingerprint_is_sha3_512_shape_and_deterministic() -> None:
    assert len(CATALOGUE_FINGERPRINT) == 128
    int(CATALOGUE_FINGERPRINT, 16)

    payload = {
        "schema": SCHEMA,
        "identity": CATALOGUE_IDENTITY,
        "version": VERSION,
        "items": [
            item.semantic_dict()
            for item in list_legal_operating_items()
        ],
    }
    canonical = json.dumps(
        payload,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
    )
    assert CATALOGUE_FINGERPRINT == hashlib.sha3_512(
        canonical.encode("utf-8")
    ).hexdigest()


def test_catalogue_maps_are_immutable() -> None:
    with pytest.raises(TypeError):
        operator.setitem(
            cast(Any, ITEMS_BY_ID),
            "X",
            ITEMS_BY_ID["PERSONA_PARTNER"],
        )

    with pytest.raises(TypeError):
        operator.setitem(
            cast(Any, ITEMS_BY_DIMENSION),
            LegalOperatingDimension.ORGANIZATIONAL_PERSONA,
            (),
        )


def test_no_authorization_role_names_are_manufactured() -> None:
    ids = set(ITEMS_BY_ID)
    assert "LEGAL_PARTNER" not in ids
    assert "LEGAL_ATTORNEY" not in ids
    assert "LEGAL_CLIENT" not in ids
    assert "SHERIFF" not in ids
    assert "DEPUTY" not in ids


# ARTIFACT: test_legal_operating_catalogue.py
# VERSION: v1.0.1-G7A-GLOBAL-LEGAL-OPERATING-CATALOGUE-CERT
# AUTHORITY BOUNDARY: direct pure-domain catalogue certificate only
# TENANT POSTURE: global vocabulary only; tenant activation is never inferred
# FAIL-CLOSED POSTURE: unknown exact identifiers and dimensions must reject
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively
# END OF WILSY OS SOVEREIGN ARTIFACT
