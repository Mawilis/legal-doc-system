# -*- coding: utf-8 -*-
"""
===============================================================================
WILSY OS — SOVEREIGN CERTIFICATION
TENANT REGISTRY PROFILE MUTATION — UNIT CERTIFICATE
===============================================================================

TITLE:
    Tenant Registry Profile Mutation Unit Certification

FILE:
    tests/unit/test_tenant_registry_profile_mutation.py

VERSION:
    v1.0.0-TENANT-PROFILE-MUTATION-PERSISTENCE-CERT

AUTHORITY:
    Wilsy OS Core Governance.
    Deterministic unit evidence for C1 domain/persistence alignment.

EPITOME:
    Certifies sector domain round-trip, exact six-field persistence allowlisting,
    pre-Mongo rejection of forbidden mutation, strict invalid-document semantics,
    idempotent same-value success, checksum regeneration, proof-hash preservation,
    exact tenant targeting, and preservation of the legacy generic update API.

ABSOLUTE CANONICAL PATH:
    /Users/wilsonkhanyezi/legal-doc-system/tests/unit/test_tenant_registry_profile_mutation.py

COLLABORATION / OWNERSHIP:
    Wilson Khanyezi / Wilsy Core Engineering.

CERTIFICATION / UPDATE DATE:
    2026-08-30

CHANGELOG:
    v1.0.0-TENANT-PROFILE-MUTATION-PERSISTENCE-CERT
        - Initial deterministic C1 certification.

COMPLIANCE:
    POPIA section 19.
    GDPR Article 32.
    SOC 2 CC7.2.
    ISO 27001.

SECURITY / PRIVACY POSTURE:
    Test doubles never grant authorization. Assertions are persistence-only and
    explicitly prove forbidden caller fields cannot reach Mongo mutation.

TENANT BOUNDARY:
    Every mutation assertion uses an explicit tenant id and verifies no redirect
    parameter exists on update_profile.

AUTHORITY BOUNDARY:
    Unit evidence only; no business authorization or HTTP authority.

FINANCIAL AUTHORITY BOUNDARY:
    Proves plan cannot be mutated through strict profile persistence.
    No financial execution authority.

STRUCTURAL GOVERNANCE:
    AGENTS.md v1.2.0-SOVEREIGN-LEGAL-OPERATIONS-CONSTITUTION.
===============================================================================
"""

from __future__ import annotations

import copy
import inspect
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any

import pytest
from pymongo.errors import AutoReconnect, PyMongoError

from tools.eos.auth.tenant_authority_policy import PROFILE_MUTABLE_FIELDS_V1
from tools.eos.saas.domain.tenant import (
    OrganizationProfile,
    SubscriptionPlan,
    TenantEntity,
)
import tools.eos.saas.tenancy.tenant_registry as registry
from tools.eos.saas.tenancy.tenant_registry import (
    TenantRegistry,
    TenantRegistryError,
)


EXPECTED_DOMAIN_VERSION = "v1.4.0-TENANT-PROFILE-SECTOR-TRUTH"
EXPECTED_REGISTRY_VERSION = "v1.4.0-TENANT-PROFILE-MUTATION-PERSISTENCE"
EXPECTED_FIELDS = frozenset(
    {"name", "alias", "industry", "region", "sector", "legal_name"}
)


@dataclass(frozen=True)
class _UpdateResult:
    matched_count: int
    modified_count: int


def _set_dotted(document: dict[str, Any], path: str, value: Any) -> None:
    parts = path.split(".")
    target = document
    for part in parts[:-1]:
        child = target.get(part)
        if not isinstance(child, dict):
            child = {}
            target[part] = child
        target = child
    target[parts[-1]] = copy.deepcopy(value)


class _Collection:
    """Minimal deterministic Mongo collection double for persistence behavior."""

    def __init__(self, document: dict[str, Any] | None) -> None:
        self.document = copy.deepcopy(document)
        self.find_calls: list[dict[str, Any]] = []
        self.update_calls: list[tuple[dict[str, Any], dict[str, Any]]] = []
        self.fail_find: PyMongoError | None = None
        self.fail_update: PyMongoError | None = None
        self.disappear_after_update = False
        self.invalidate_after_update = False
        self._updated = False

    def find_one(self, query: dict[str, Any]) -> dict[str, Any] | None:
        self.find_calls.append(copy.deepcopy(query))
        if self.fail_find is not None:
            raise self.fail_find
        if self._updated and self.disappear_after_update:
            return None
        if self._updated and self.invalidate_after_update:
            return {
                "tenant_id": query.get("tenant_id"),
                "organization": "corrupt",
            }
        if self.document is None:
            return None
        if self.document.get("tenant_id") != query.get("tenant_id"):
            return None
        return copy.deepcopy(self.document)

    def update_one(
        self,
        query: dict[str, Any],
        mutation: dict[str, Any],
    ) -> _UpdateResult:
        self.update_calls.append(
            (copy.deepcopy(query), copy.deepcopy(mutation))
        )
        if self.fail_update is not None:
            raise self.fail_update
        if (
            self.document is None
            or self.document.get("tenant_id") != query.get("tenant_id")
        ):
            self._updated = True
            return _UpdateResult(matched_count=0, modified_count=0)

        before = copy.deepcopy(self.document)
        for path, value in mutation["$set"].items():
            _set_dotted(self.document, path, value)
        self._updated = True
        return _UpdateResult(
            matched_count=1,
            modified_count=int(self.document != before),
        )


def _base_document() -> dict[str, Any]:
    created = datetime(2026, 8, 30, tzinfo=timezone.utc)
    return {
        "tenant_id": "tenant-a",
        "name": "Tenant A",
        "organization": {
            "organization_name": "Tenant A",
            "industry": "Legal",
            "plan": "ENTERPRISE",
            "legal_name": "Tenant A Legal",
            "tax_id": "tax-a",
            "contact_email": "tenant-a@example.test",
            "regions": ["Africa"],
            "created_at": created.isoformat(),
        },
        "industry": "Legal",
        "legal_name": "Tenant A Legal",
        "tax_id": "tax-a",
        "contact_email": "tenant-a@example.test",
        "plan": "ENTERPRISE",
        "status": "ACTIVE",
        "created_at": created,
        "checksum": "legacy-checksum",
        "alias": "tenant-a",
        "region": "ZA",
        "sector": "Law",
        "compliance_flags": {"certified": True},
        "proof_hash": "proof-before",
        "verified": True,
    }


def _bind(
    monkeypatch: pytest.MonkeyPatch,
    collection: _Collection,
) -> _Collection:
    monkeypatch.setattr(registry, "tenants_collection", collection)
    return collection


def test_versions_and_policy_field_set_are_exact() -> None:
    """C1 production versions and frozen six-field canon are exact."""
    import tools.eos.saas.domain.tenant as domain

    assert domain.VERSION == EXPECTED_DOMAIN_VERSION
    assert registry.VERSION == EXPECTED_REGISTRY_VERSION
    assert PROFILE_MUTABLE_FIELDS_V1 == EXPECTED_FIELDS
    assert registry._PROFILE_MUTABLE_FIELDS == EXPECTED_FIELDS


def test_tenant_entity_sector_round_trips_through_domain_serialization() -> None:
    """Sector is top-level TenantEntity truth and survives to_dict/from_dict."""
    entity = TenantEntity(
        organization=OrganizationProfile(
            organization_name="Tenant A",
            industry="Legal",
            plan=SubscriptionPlan.ENTERPRISE,
        ),
        tenant_id="tenant-a",
        sector="Professional Services",
    )

    payload = entity.to_dict()
    restored = TenantEntity.from_dict(payload)

    assert payload["sector"] == "Professional Services"
    assert restored.sector == "Professional Services"
    assert restored.tenant_id == "tenant-a"


def test_registry_mapper_and_serializer_round_trip_sector() -> None:
    """Registry hydration and serialization preserve sector as top-level truth."""
    document = _base_document()

    entity = registry._doc_to_entity(document)

    assert entity is not None
    assert entity.sector == "Law"
    serialized = registry._entity_to_doc(entity)
    assert serialized["sector"] == "Law"


def test_update_profile_signature_has_no_transport_scope_parameter() -> None:
    """Strict persistence accepts tenant_id + payload only."""
    assert tuple(
        inspect.signature(TenantRegistry.update_profile).parameters
    ) == ("tenant_id", "payload")


def test_empty_payload_fails_before_mongo_access(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Empty mutation cannot trigger a persistence read or write."""
    collection = _bind(monkeypatch, _Collection(_base_document()))

    with pytest.raises(
        TenantRegistryError,
        match="^TENANT_REGISTRY_PROFILE_UPDATE_EMPTY$",
    ):
        TenantRegistry.update_profile("tenant-a", {})

    assert collection.find_calls == []
    assert collection.update_calls == []


@pytest.mark.parametrize(
    "field_name",
    [
        "status",
        "plan",
        "tax_id",
        "contact_email",
        "verified",
        "checksum",
        "proof_hash",
        "compliance_flags",
        "created_at",
        "updated_at",
        "tenant_id",
        "unknown",
    ],
)
def test_forbidden_or_unknown_fields_fail_before_mongo_access(
    monkeypatch: pytest.MonkeyPatch,
    field_name: str,
) -> None:
    """No non-canonical field can cross the strict persistence boundary."""
    collection = _bind(monkeypatch, _Collection(_base_document()))

    with pytest.raises(
        TenantRegistryError,
        match="^TENANT_REGISTRY_PROFILE_UPDATE_INVALID_FIELDS$",
    ):
        TenantRegistry.update_profile(
            "tenant-a",
            {field_name: "attacker-controlled"},
        )

    assert collection.find_calls == []
    assert collection.update_calls == []


@pytest.mark.parametrize(
    ("payload", "token"),
    [
        ({"name": ""}, "TENANT_REGISTRY_PROFILE_UPDATE_INVALID_VALUES"),
        ({"industry": None}, "TENANT_REGISTRY_PROFILE_UPDATE_INVALID_VALUES"),
        ({"sector": 42}, "TENANT_REGISTRY_PROFILE_UPDATE_INVALID_VALUES"),
    ],
)
def test_invalid_profile_values_fail_before_mongo_access(
    monkeypatch: pytest.MonkeyPatch,
    payload: dict[str, Any],
    token: str,
) -> None:
    """Invalid value shapes are rejected before durable truth is read."""
    collection = _bind(monkeypatch, _Collection(_base_document()))

    with pytest.raises(TenantRegistryError, match=f"^{token}$"):
        TenantRegistry.update_profile("tenant-a", payload)

    assert collection.find_calls == []
    assert collection.update_calls == []


def test_invalid_tenant_id_fails_before_mongo_access(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Blank tenant identity cannot enter strict profile persistence."""
    collection = _bind(monkeypatch, _Collection(_base_document()))

    with pytest.raises(
        TenantRegistryError,
        match="^TENANT_REGISTRY_PROFILE_UPDATE_INVALID_TENANT_ID$",
    ):
        TenantRegistry.update_profile(" ", {"alias": "x"})

    assert collection.find_calls == []
    assert collection.update_calls == []


def test_genuine_absence_returns_none_without_mutation(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Only genuine pre-mutation absence returns None."""
    collection = _bind(monkeypatch, _Collection(None))

    result = TenantRegistry.update_profile(
        "missing",
        {"alias": "missing"},
    )

    assert result is None
    assert collection.find_calls == [{"tenant_id": "missing"}]
    assert collection.update_calls == []


def test_invalid_existing_document_fails_before_update(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Malformed existing truth cannot be mutated or fabricated as absence."""
    malformed = {
        "tenant_id": "tenant-a",
        "organization": "not-a-document",
        "status": "ACTIVE",
    }
    collection = _bind(monkeypatch, _Collection(malformed))

    with pytest.raises(
        TenantRegistryError,
        match="^TENANT_REGISTRY_PROFILE_UPDATE_INVALID_DOCUMENT$",
    ):
        TenantRegistry.update_profile(
            "tenant-a",
            {"alias": "changed"},
        )

    assert len(collection.find_calls) == 1
    assert collection.update_calls == []


def test_all_six_profile_fields_mutate_and_protected_truth_is_preserved(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Strict mutation writes all six fields and no caller-protected business truth."""
    before = _base_document()
    collection = _bind(monkeypatch, _Collection(before))

    result = TenantRegistry.update_profile(
        "tenant-a",
        {
            "name": "Tenant Alpha",
            "alias": "alpha",
            "industry": "Technology",
            "region": "EU",
            "sector": "AI",
            "legal_name": "Tenant Alpha Legal",
        },
    )

    assert result is not None
    assert result.tenant_id == "tenant-a"
    assert result.organization.organization_name == "Tenant Alpha"
    assert result.organization.industry == "Technology"
    assert result.organization.legal_name == "Tenant Alpha Legal"
    assert result.alias == "alpha"
    assert result.region == "EU"
    assert result.sector == "AI"

    assert collection.document is not None
    persisted = collection.document
    assert persisted["name"] == "Tenant Alpha"
    assert persisted["organization"]["organization_name"] == "Tenant Alpha"
    assert persisted["industry"] == "Technology"
    assert persisted["organization"]["industry"] == "Technology"
    assert persisted["legal_name"] == "Tenant Alpha Legal"
    assert persisted["organization"]["legal_name"] == "Tenant Alpha Legal"
    assert persisted["alias"] == "alpha"
    assert persisted["region"] == "EU"
    assert persisted["sector"] == "AI"

    for field_name in (
        "tenant_id",
        "status",
        "plan",
        "tax_id",
        "contact_email",
        "verified",
        "compliance_flags",
        "created_at",
        "proof_hash",
    ):
        assert persisted[field_name] == before[field_name]

    assert persisted["checksum"] != "legacy-checksum"
    assert persisted["checksum"] == result.checksum
    assert persisted["proof_hash"] == "proof-before"


def test_update_profile_checksum_matches_candidate_domain_truth(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Internal checksum regeneration matches TenantEntity's canonical algorithm."""
    document = _base_document()
    collection = _bind(monkeypatch, _Collection(document))

    result = TenantRegistry.update_profile(
        "tenant-a",
        {"name": "Tenant Renamed"},
    )

    assert result is not None
    expected = TenantEntity(
        organization=OrganizationProfile(
            organization_name="Tenant Renamed",
            industry="Legal",
            plan=SubscriptionPlan.ENTERPRISE,
            legal_name="Tenant A Legal",
            tax_id="tax-a",
            contact_email="tenant-a@example.test",
            regions=["Africa"],
            created_at=document["created_at"].isoformat(),
        ),
        tenant_id="tenant-a",
        status="ACTIVE",
        created_at=document["created_at"].isoformat(),
        alias="tenant-a",
        region="ZA",
        sector="Law",
        compliance_flags={"certified": True},
        proof_hash="proof-before",
        verified=True,
    )
    assert result.checksum == expected.checksum


def test_same_value_mutation_is_idempotent_success(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """modified_count zero cannot fabricate a profile-mutation failure."""
    document = _base_document()
    first = _bind(monkeypatch, _Collection(document))
    canonical = TenantRegistry.update_profile(
        "tenant-a",
        {"alias": "tenant-a"},
    )
    assert canonical is not None
    assert first.document is not None

    second = _bind(monkeypatch, _Collection(first.document))
    before = copy.deepcopy(second.document)
    repeated = TenantRegistry.update_profile(
        "tenant-a",
        {"alias": "tenant-a"},
    )

    assert repeated is not None
    assert second.document == before
    assert second.update_calls
    assert repeated.alias == "tenant-a"


def test_find_outage_raises_unavailable_with_original_cause(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Mongo read outage is explicit and preserves the PyMongo cause."""
    collection = _Collection(_base_document())
    cause = AutoReconnect("offline")
    collection.fail_find = cause
    _bind(monkeypatch, collection)

    with pytest.raises(
        TenantRegistryError,
        match="^TENANT_REGISTRY_PROFILE_UPDATE_UNAVAILABLE$",
    ) as caught:
        TenantRegistry.update_profile(
            "tenant-a",
            {"alias": "changed"},
        )

    assert caught.value.__cause__ is cause
    assert collection.update_calls == []


def test_update_outage_raises_unavailable_with_original_cause(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Mongo write outage is explicit and preserves the PyMongo cause."""
    collection = _Collection(_base_document())
    cause = AutoReconnect("offline")
    collection.fail_update = cause
    _bind(monkeypatch, collection)

    with pytest.raises(
        TenantRegistryError,
        match="^TENANT_REGISTRY_PROFILE_UPDATE_UNAVAILABLE$",
    ) as caught:
        TenantRegistry.update_profile(
            "tenant-a",
            {"alias": "changed"},
        )

    assert caught.value.__cause__ is cause
    assert len(collection.update_calls) == 1


def test_post_write_disappearance_is_inconsistent_not_absence(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """A target disappearing after a matched write fails closed."""
    collection = _Collection(_base_document())
    collection.disappear_after_update = True
    _bind(monkeypatch, collection)

    with pytest.raises(
        TenantRegistryError,
        match="^TENANT_REGISTRY_PROFILE_UPDATE_INCONSISTENT_STATE$",
    ):
        TenantRegistry.update_profile(
            "tenant-a",
            {"alias": "changed"},
        )


def test_post_write_invalid_truth_fails_explicitly(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Corrupt post-write truth cannot be returned as a successful entity."""
    collection = _Collection(_base_document())
    collection.invalidate_after_update = True
    _bind(monkeypatch, collection)

    with pytest.raises(
        TenantRegistryError,
        match="^TENANT_REGISTRY_PROFILE_UPDATE_INVALID_DOCUMENT$",
    ):
        TenantRegistry.update_profile(
            "tenant-a",
            {"alias": "changed"},
        )


def test_legacy_update_signature_and_broad_status_contract_remain_separate(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Legacy update remains compatibility API while strict profile update is bounded."""
    assert tuple(inspect.signature(TenantRegistry.update).parameters) == (
        "tenant_id",
        "payload",
        "tenant_id_header",
    )

    collection = _bind(monkeypatch, _Collection(_base_document()))
    result = TenantRegistry.update(
        "tenant-a",
        {"status": "SUSPENDED"},
    )

    assert result["success"] is True
    assert collection.document is not None
    assert collection.document["status"] == "SUSPENDED"


# =============================================================================
# WILSY OS SOVEREIGN CERTIFICATION SEAL
# =============================================================================
# ARTIFACT: test_tenant_registry_profile_mutation.py
# VERSION: v1.0.0-TENANT-PROFILE-MUTATION-PERSISTENCE-CERT
# AUTHORITY BOUNDARY: deterministic domain/persistence evidence only; no authentication, HTTP, membership, role, permission, or financial authority
# TENANT POSTURE: update_profile accepts explicit tenant_id plus exact six-field profile payload only; no transport scope input exists
# FAIL-CLOSED POSTURE: forbidden/invalid input fails before Mongo; invalid truth and outages are explicit; same-value mutation succeeds without widening fields
# FINANCIAL EXECUTION AUTHORITY: None. Plan mutation is prohibited through update_profile.
# END OF WILSY OS SOVEREIGN ARTIFACT
