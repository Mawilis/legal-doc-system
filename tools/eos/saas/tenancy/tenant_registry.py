# -*- coding: utf-8 -*-
"""
===============================================================================
WILSY OS — SOVEREIGN OPERATING SYSTEM
TENANT REGISTRY — STRICT PROFILE MUTATION PERSISTENCE
===============================================================================

TITLE:
    WILSY OS Tenant Registry

FILE:
    tools/eos/saas/tenancy/tenant_registry.py

VERSION:
    v1.4.0-TENANT-PROFILE-MUTATION-PERSISTENCE

AUTHORITY:
    Wilsy OS Core Governance.
    Canonical MongoDB-backed tenant registry persistence boundary.

EPITOME:
    Adds a strict, profile-specific mutation operation bounded to the frozen
    six-field tenant profile policy while preserving the legacy generic update
    contract. Sector becomes durable top-level tenant truth. Profile mutation
    distinguishes absence, invalid persisted truth, invalid mutation input,
    inconsistent post-write state, and MongoDB infrastructure unavailability.

ABSOLUTE CANONICAL PATH:
    /Users/wilsonkhanyezi/legal-doc-system/tools/eos/saas/tenancy/tenant_registry.py

COLLABORATION / OWNERSHIP:
    Wilson Khanyezi / Wilsy Core Engineering.

CERTIFICATION / UPDATE DATE:
    2026-08-30

CHANGELOG:
    v1.4.0-TENANT-PROFILE-MUTATION-PERSISTENCE
        - Adds TenantRegistry.update_profile(tenant_id, payload).
        - Binds mutation fields to frozen PROFILE_MUTABLE_FIELDS_V1.
        - Allows exactly name, alias, industry, region, sector, and legal_name.
        - Rejects lifecycle, billing, verification, evidence, security-sensitive,
          system-managed, tenant-id, and unknown fields before MongoDB access.
        - Adds sector hydration/serialization across TenantEntity persistence.
        - Regenerates checksum internally after profile mutation while preserving
          created_at, lifecycle status, billing metadata, security metadata, and
          proof_hash evidence.
        - Treats same-value mutation as idempotent success.
        - Distinguishes genuine absence from invalid persisted truth,
          inconsistent post-write state, and MongoDB unavailability.
        - Preserves legacy TenantRegistry.update return/field behavior unchanged.

    v1.3.1-TENANT-REGISTRY-MAPPING-FAILURE-SEMANTICS
        - Distinguished malformed persisted GET truth from genuine absence.

    v1.3.0-TENANT-REGISTRY-FAILURE-SEMANTICS
        - Distinguished GET/archive infrastructure failure from ordinary
          absence/no-change.

COMPLIANCE:
    POPIA section 19.
    GDPR Article 32.
    SOC 2 CC7.2.
    ISO 27001.

SECURITY / PRIVACY POSTURE:
    Profile persistence is field-bounded independently of caller transport data.
    Caller-supplied lifecycle, plan, verification, evidence, security-sensitive,
    system-managed, tenant-id, or unknown fields are rejected before registry
    access. Infrastructure and persisted-truth failures are explicit.

TENANT BOUNDARY:
    update_profile is keyed only by the supplied tenant_id and has no transport
    tenant-header compatibility argument. It cannot redirect mutation through
    request headers, JWT claims, roles, permissions, or request state.

AUTHORITY BOUNDARY:
    This artifact owns persistence, hydration, field-bounded mutation, and
    persistence failure signaling only. It does not authenticate callers,
    authorize profile_update, establish membership, resolve business roles,
    grant permissions, or own HTTP status translation.

FINANCIAL AUTHORITY BOUNDARY:
    Profile mutation cannot alter plan or financial metadata.
    No financial execution authority exists here.
    Kennel EOS remains the exclusive financial execution authority.

STRUCTURAL GOVERNANCE:
    AGENTS.md v1.2.0-SOVEREIGN-LEGAL-OPERATIONS-CONSTITUTION.
    Full-file sovereign artifact.
    Fail-closed.
===============================================================================
"""

from __future__ import annotations

import copy
import hashlib
import json
import logging
import os
import uuid
from datetime import datetime, timezone
from typing import Any

from bson import ObjectId
from bson.errors import InvalidId
from pymongo import MongoClient
from pymongo.errors import DuplicateKeyError, PyMongoError

from ...auth.tenant_authority_policy import PROFILE_MUTABLE_FIELDS_V1
from ..domain.tenant import OrganizationProfile, SubscriptionPlan, TenantEntity


VERSION = "v1.4.0-TENANT-PROFILE-MUTATION-PERSISTENCE"

logger = logging.getLogger("WilsyOS.SaaS.Tenancy.TenantRegistry")

MONGO_URI = os.getenv("MONGODB_URI", "mongodb://127.0.0.1:27017/wilsy")
client = MongoClient(MONGO_URI, connect=False)
db = client.get_database("wilsy")
tenants_collection = db["tenants"]

_PROFILE_MUTABLE_FIELDS = frozenset(PROFILE_MUTABLE_FIELDS_V1)
_REQUIRED_TEXT_PROFILE_FIELDS = frozenset({"name", "industry"})
_OPTIONAL_TEXT_PROFILE_FIELDS = (
    _PROFILE_MUTABLE_FIELDS - _REQUIRED_TEXT_PROFILE_FIELDS
)


class TenantRegistryError(RuntimeError):
    """Represent bounded tenant-registry persistence/read-integrity failure.

    Authority:
        Persistence/read-integrity signaling only.

    Tenant scope:
        Does not grant access or alter lookup/mutation scope.

    Failure semantics:
        Used for infrastructure failure, invalid persisted truth, invalid strict
        profile mutation input, or inconsistent strict post-write state.

    Mutation semantics:
        Raising this exception never grants permission to retry under a broader
        field set or another tenant.

    Financial boundary:
        No financial execution authority. Kennel EOS remains exclusive.
    """


def _to_plan_enum(plan_str: str) -> Any:
    """Convert a persisted plan string to the established SubscriptionPlan shape."""
    plan_str = (plan_str or "BASIC").upper()
    try:
        return SubscriptionPlan[plan_str]
    except (KeyError, AttributeError):
        return getattr(SubscriptionPlan, plan_str, plan_str)


def _to_iso_datetime(value: datetime | str | None) -> str:
    """Convert datetime/string input to the registry's existing ISO-string shape."""
    if isinstance(value, datetime):
        return value.isoformat()
    if isinstance(value, str) and value.strip():
        return value
    return datetime.now(timezone.utc).isoformat()


def _build_tenant_entity(
    *,
    tenant_id: str,
    organization: OrganizationProfile,
    status: str,
    created_at: str,
    alias: Any = None,
    region: Any = None,
    sector: Any = None,
    compliance_flags: Any = None,
    proof_hash: Any = None,
    verified: bool = False,
    checksum: Any = None,
) -> TenantEntity:
    """Construct TenantEntity while preserving legacy constructor compatibility."""
    extended = {
        "alias": alias,
        "region": region,
        "sector": sector,
        "compliance_flags": compliance_flags,
        "proof_hash": proof_hash,
        "verified": verified,
    }

    try:
        entity = TenantEntity(
            tenant_id=tenant_id,
            organization=organization,
            status=status,
            created_at=created_at,
            alias=alias,
            region=region,
            sector=sector,
            compliance_flags=compliance_flags,
            proof_hash=proof_hash,
            verified=verified,
        )
    except TypeError:
        try:
            entity = TenantEntity(
                tenant_id=tenant_id,
                organization=organization,
                status=status,
                created_at=created_at,
            )
        except TypeError:
            entity = TenantEntity(
                organization,
                tenant_id,
                status,
                created_at,
            )

    for key, value in extended.items():
        try:
            setattr(entity, key, value)
        except (AttributeError, TypeError) as exc:
            logger.debug(
                "TenantEntity compatibility hydration skipped for %s: %s",
                key,
                exc,
            )

    if checksum is not None:
        try:
            entity.checksum = checksum
        except (AttributeError, TypeError) as exc:
            logger.debug("TenantEntity checksum hydration skipped: %s", exc)

    return entity


def _doc_to_entity(doc: dict[str, Any]) -> TenantEntity | None:
    """Map one tenant document using the registry's legacy tolerant contract.

    This deliberately preserves the B1.1 mapper failure surface. In particular,
    malformed persisted ``subscription`` values still fail hydration rather than
    being normalized into apparently healthy tenant truth. C1 adds only sector
    hydration to that frozen semantic boundary.
    """
    try:
        org_name = doc.get("name") or doc.get("organization_name") or "Unknown"
        industry = doc.get("industry") or "General"
        plan_str = (
            doc.get("subscription", {}).get("plan")
            or doc.get("plan")
            or "BASIC"
        )
        plan_enum = _to_plan_enum(str(plan_str))

        regions = doc.get("regions") or ["Africa", "Europe"]
        legal_name = doc.get("legal_name")
        tax_id = doc.get("tax_id")
        contact_email = doc.get("contact_email")

        raw_created = doc.get("created_at") or datetime.now(timezone.utc)
        created_at_str = _to_iso_datetime(raw_created)

        organization = OrganizationProfile(
            organization_name=org_name,
            industry=industry,
            plan=plan_enum,
            legal_name=legal_name,
            tax_id=tax_id,
            contact_email=contact_email,
            regions=regions,
            created_at=created_at_str,
        )

        tenant_id = doc.get("tenant_id") or str(doc["_id"])
        status = doc.get("status", "ACTIVE")

        return _build_tenant_entity(
            tenant_id=tenant_id,
            organization=organization,
            status=status,
            created_at=created_at_str,
            alias=doc.get("alias"),
            region=doc.get("region"),
            sector=doc.get("sector"),
            compliance_flags=doc.get("compliance_flags"),
            proof_hash=doc.get("proof_hash"),
            verified=bool(doc.get("verified", False)),
            checksum=doc.get("checksum"),
        )
    except (AttributeError, KeyError, TypeError, ValueError) as exc:
        logger.error(
            "Tenant document mapping failed for %s: %s",
            doc.get("_id"),
            exc,
        )
        return None


def _doc_to_entity_for_get(doc: dict[str, Any]) -> TenantEntity:
    """Hydrate an existing GET document or fail closed as invalid persisted truth."""
    entity = _doc_to_entity(doc)
    if entity is None:
        raise TenantRegistryError("TENANT_REGISTRY_GET_INVALID_DOCUMENT")
    return entity


def _validate_profile_update_document(doc: dict[str, Any]) -> None:
    """Require durable baseline truth suitable for an in-place profile mutation."""
    organization = doc.get("organization")
    if organization is not None and not isinstance(organization, dict):
        raise TenantRegistryError(
            "TENANT_REGISTRY_PROFILE_UPDATE_INVALID_DOCUMENT"
        )

    organization_doc = (
        organization if isinstance(organization, dict) else {}
    )
    name = (
        doc.get("name")
        or doc.get("organization_name")
        or organization_doc.get("organization_name")
    )
    industry = (
        doc.get("industry")
        or organization_doc.get("industry")
    )
    tenant_id = doc.get("tenant_id")

    if (
        not isinstance(tenant_id, str)
        or not tenant_id.strip()
        or not isinstance(name, str)
        or not name.strip()
        or not isinstance(industry, str)
        or not industry.strip()
    ):
        raise TenantRegistryError(
            "TENANT_REGISTRY_PROFILE_UPDATE_INVALID_DOCUMENT"
        )


def _doc_to_entity_for_profile_update(doc: dict[str, Any]) -> TenantEntity:
    """Hydrate strict profile-mutation truth or raise the bounded invalid token."""
    _validate_profile_update_document(doc)
    entity = _doc_to_entity(doc)
    if entity is None:
        raise TenantRegistryError(
            "TENANT_REGISTRY_PROFILE_UPDATE_INVALID_DOCUMENT"
        )
    return entity


def _entity_to_doc(entity: TenantEntity) -> dict[str, Any]:
    """Serialize TenantEntity into the registry persistence document shape."""
    organization = entity.organization
    plan_value = (
        organization.plan.value
        if hasattr(organization.plan, "value")
        else str(organization.plan)
    )
    return {
        "tenant_id": entity.tenant_id,
        "name": organization.organization_name,
        "organization": {
            "organization_name": organization.organization_name,
            "industry": organization.industry,
            "plan": plan_value,
            "legal_name": organization.legal_name,
            "tax_id": organization.tax_id,
            "contact_email": organization.contact_email,
            "regions": organization.regions,
            "created_at": organization.created_at,
        },
        "industry": organization.industry,
        "legal_name": organization.legal_name,
        "tax_id": organization.tax_id,
        "contact_email": organization.contact_email,
        "plan": plan_value,
        "regions": organization.regions,
        "status": entity.status,
        "created_at": entity.created_at,
        "checksum": getattr(entity, "checksum", None),
        "alias": getattr(entity, "alias", None),
        "region": getattr(entity, "region", None),
        "sector": getattr(entity, "sector", None),
        "compliance_flags": getattr(entity, "compliance_flags", None),
        "proof_hash": getattr(entity, "proof_hash", None),
        "verified": bool(getattr(entity, "verified", False)),
    }


def _validate_profile_update_input(
    tenant_id: str,
    payload: dict[str, Any],
) -> None:
    """Validate strict profile mutation shape before any MongoDB access."""
    if not isinstance(tenant_id, str) or not tenant_id.strip():
        raise TenantRegistryError(
            "TENANT_REGISTRY_PROFILE_UPDATE_INVALID_TENANT_ID"
        )

    if not isinstance(payload, dict) or not payload:
        raise TenantRegistryError(
            "TENANT_REGISTRY_PROFILE_UPDATE_EMPTY"
        )

    payload_fields = frozenset(payload)
    if not payload_fields <= _PROFILE_MUTABLE_FIELDS:
        raise TenantRegistryError(
            "TENANT_REGISTRY_PROFILE_UPDATE_INVALID_FIELDS"
        )

    for field_name in _REQUIRED_TEXT_PROFILE_FIELDS:
        if field_name not in payload:
            continue
        value = payload[field_name]
        if not isinstance(value, str) or not value.strip():
            raise TenantRegistryError(
                "TENANT_REGISTRY_PROFILE_UPDATE_INVALID_VALUES"
            )

    for field_name in _OPTIONAL_TEXT_PROFILE_FIELDS:
        if field_name not in payload:
            continue
        value = payload[field_name]
        if value is not None and not isinstance(value, str):
            raise TenantRegistryError(
                "TENANT_REGISTRY_PROFILE_UPDATE_INVALID_VALUES"
            )


def _build_profile_update(
    doc: dict[str, Any],
    payload: dict[str, Any],
) -> tuple[dict[str, Any], dict[str, Any]]:
    """Build bounded Mongo $set fields plus the resulting candidate document."""
    candidate = copy.deepcopy(doc)
    organization = candidate.get("organization")
    if organization is None:
        organization = {}
        candidate["organization"] = organization
    if not isinstance(organization, dict):
        raise TenantRegistryError(
            "TENANT_REGISTRY_PROFILE_UPDATE_INVALID_DOCUMENT"
        )

    update_fields: dict[str, Any] = {}

    if "name" in payload:
        candidate["name"] = payload["name"]
        organization["organization_name"] = payload["name"]
        update_fields["name"] = payload["name"]
        update_fields["organization.organization_name"] = payload["name"]

    if "industry" in payload:
        candidate["industry"] = payload["industry"]
        organization["industry"] = payload["industry"]
        update_fields["industry"] = payload["industry"]
        update_fields["organization.industry"] = payload["industry"]

    if "legal_name" in payload:
        candidate["legal_name"] = payload["legal_name"]
        organization["legal_name"] = payload["legal_name"]
        update_fields["legal_name"] = payload["legal_name"]
        update_fields["organization.legal_name"] = payload["legal_name"]

    for field_name in ("alias", "region", "sector"):
        if field_name in payload:
            candidate[field_name] = payload[field_name]
            update_fields[field_name] = payload[field_name]

    checksum_candidate = copy.deepcopy(candidate)
    checksum_candidate.pop("checksum", None)
    candidate_entity = _doc_to_entity_for_profile_update(
        checksum_candidate
    )
    candidate["checksum"] = candidate_entity.checksum
    update_fields["checksum"] = candidate_entity.checksum

    return update_fields, candidate


class TenantRegistry:
    """Own the MongoDB-backed tenant persistence boundary.

    Authority:
        Persistence only. No authentication, authorization, membership, role,
        JWT, permission, transport, or financial authority.

    Tenant scope:
        Strict get/archive/update_profile operations target the supplied tenant id.
        Legacy tenant_id_header parameters remain compatibility-only where present.

    Mutation:
        create/update preserve their legacy behavior. archive remains a soft status
        transition. update_profile is the strict six-field profile mutation path.

    Failure semantics:
        Strict get/archive/update_profile distinguish bounded persistence failures
        from ordinary absence/no-change semantics.

    Financial boundary:
        No financial execution authority. Kennel EOS remains exclusive.
    """

    @staticmethod
    def list(
        skip: int = 0,
        limit: int = 20,
        tenant_id_header: str | None = None,
    ) -> dict[str, Any]:
        """List tenants using the preserved legacy tolerant/fallback semantics."""
        del tenant_id_header
        try:
            total = tenants_collection.count_documents({})
            cursor = (
                tenants_collection.find({}, {"_id": 0})
                .skip(skip)
                .limit(limit)
            )
            docs = list(cursor)
            items: list[TenantEntity] = []
            for doc in docs:
                entity = _doc_to_entity(doc)
                if entity:
                    items.append(entity)
                else:
                    logger.warning(
                        "Skipped tenant document after bounded mapping failure: %s",
                        doc.get("_id"),
                    )
            return {"items": items, "total": total}
        except PyMongoError as exc:
            logger.error("Tenant list failed: %s", exc)
            return {"items": [], "total": 0}

    @staticmethod
    def get(
        tenant_id: str,
        tenant_id_header: str | None = None,
    ) -> TenantEntity | None:
        """Resolve one tenant with strict absence/outage/corruption semantics."""
        del tenant_id_header
        try:
            doc = tenants_collection.find_one({"tenant_id": tenant_id})
            if not doc and len(tenant_id) == 24:
                try:
                    doc = tenants_collection.find_one(
                        {"_id": ObjectId(tenant_id)}
                    )
                except (InvalidId, TypeError):
                    doc = None

            if doc:
                return _doc_to_entity_for_get(doc)
            return None
        except PyMongoError as exc:
            logger.error("Tenant get unavailable: %s", exc)
            raise TenantRegistryError(
                "TENANT_REGISTRY_GET_UNAVAILABLE"
            ) from exc

    @staticmethod
    def get_tenant_by_alias(
        alias: str,
        tenant_id_header: str | None = None,
    ) -> TenantEntity | None:
        """Retrieve a tenant by alias, tenant id, or name using legacy semantics."""
        del tenant_id_header
        if not alias:
            return None

        doc = tenants_collection.find_one(
            {
                "$or": [
                    {"alias": {"$regex": f"^{alias}$", "$options": "i"}},
                    {"tenant_id": {"$regex": f"^{alias}$", "$options": "i"}},
                    {"name": {"$regex": f"^{alias}$", "$options": "i"}},
                ]
            }
        )
        return _doc_to_entity(doc) if doc else None

    @staticmethod
    def create(
        payload: dict[str, Any],
        tenant_id_header: str | None = None,
    ) -> dict[str, Any]:
        """Create one tenant using the preserved legacy structured result contract."""
        del tenant_id_header
        try:
            name = payload.get("name") or payload.get("organization_name")
            if not name:
                return {
                    "success": False,
                    "error": "Missing 'name' or 'organization_name'.",
                }

            tenant_id = payload.get("tenant_id")
            if not tenant_id:
                tenant_id = f"WILSYTENANT-{uuid.uuid4().hex[:8].upper()}"

            now = datetime.now(timezone.utc)
            now_iso = now.isoformat()
            doc = {
                "tenant_id": tenant_id,
                "name": name,
                "organization": {
                    "organization_name": name,
                    "industry": payload.get("industry", "General"),
                    "plan": payload.get("plan", "BASIC"),
                    "legal_name": payload.get("legal_name"),
                    "tax_id": payload.get("tax_id"),
                    "contact_email": payload.get("contact_email"),
                    "regions": payload.get(
                        "regions",
                        ["Africa", "Europe"],
                    ),
                    "created_at": now_iso,
                },
                "industry": payload.get("industry", "General"),
                "plan": payload.get("plan", "BASIC"),
                "regions": payload.get("regions", ["Africa", "Europe"]),
                "status": payload.get("status", "ACTIVE"),
                "created_at": now,
                "checksum": payload.get("checksum"),
                "alias": payload.get("alias"),
                "region": payload.get("region"),
                "compliance_flags": payload.get("compliance_flags")
                or {
                    "popia_section_19": True,
                    "gdpr_article_32": True,
                    "soc2_cc7_2": True,
                },
                "verified": payload.get("verified", False),
            }
            proof_payload = {
                key: value
                for key, value in doc.items()
                if key not in {"created_at", "proof_hash"}
            }
            doc["proof_hash"] = hashlib.sha3_512(
                json.dumps(
                    proof_payload,
                    sort_keys=True,
                    default=str,
                    separators=(",", ":"),
                ).encode("utf-8")
            ).hexdigest().upper()

            tenants_collection.insert_one(doc)
            return {
                "success": True,
                "tenant": _doc_to_entity(doc),
            }
        except DuplicateKeyError:
            return {
                "success": False,
                "error": "Tenant ID already exists.",
            }
        except PyMongoError as exc:
            logger.error("Tenant create failed: %s", exc)
            return {"success": False, "error": str(exc)}

    @staticmethod
    def update(
        tenant_id: str,
        payload: dict[str, Any],
        tenant_id_header: str | None = None,
    ) -> dict[str, Any]:
        """Update one tenant using the preserved legacy generic field contract.

        This method intentionally remains distinct from update_profile. Existing
        script callers rely on this structured result and broad compatibility
        field behavior.
        """
        del tenant_id_header
        try:
            doc = tenants_collection.find_one({"tenant_id": tenant_id})
            if not doc:
                return {"success": False, "error": "Tenant not found."}

            update_fields: dict[str, Any] = {}
            if "name" in payload:
                update_fields["name"] = payload["name"]
                update_fields["organization.organization_name"] = payload["name"]
            if "industry" in payload:
                update_fields["industry"] = payload["industry"]
                update_fields["organization.industry"] = payload["industry"]
            if "plan" in payload:
                plan_value = str(payload["plan"]).upper()
                update_fields["plan"] = plan_value
                update_fields["organization.plan"] = plan_value
                update_fields["subscription.plan"] = plan_value.lower()
            if "status" in payload:
                update_fields["status"] = payload["status"]
            if "legal_name" in payload:
                update_fields["legal_name"] = payload["legal_name"]
                update_fields["organization.legal_name"] = payload["legal_name"]
            if "tax_id" in payload:
                update_fields["tax_id"] = payload["tax_id"]
                update_fields["organization.tax_id"] = payload["tax_id"]
            if "contact_email" in payload:
                update_fields["contact_email"] = payload["contact_email"]
                update_fields["organization.contact_email"] = payload[
                    "contact_email"
                ]
            if "regions" in payload:
                update_fields["regions"] = payload["regions"]
                update_fields["organization.regions"] = payload["regions"]
            if "checksum" in payload:
                update_fields["checksum"] = payload["checksum"]
            if "alias" in payload:
                update_fields["alias"] = payload["alias"]
            if "region" in payload:
                update_fields["region"] = payload["region"]
            if "compliance_flags" in payload:
                update_fields["compliance_flags"] = payload[
                    "compliance_flags"
                ]
            if "verified" in payload:
                update_fields["verified"] = payload["verified"]

            if not update_fields:
                return {
                    "success": False,
                    "error": "No fields to update.",
                }

            result = tenants_collection.update_one(
                {"tenant_id": tenant_id},
                {"$set": update_fields},
            )
            if result.modified_count == 0:
                return {
                    "success": False,
                    "error": "No changes made.",
                }

            updated_doc = tenants_collection.find_one(
                {"tenant_id": tenant_id}
            )
            if not updated_doc:
                return {
                    "success": False,
                    "error": "Failed to retrieve updated tenant.",
                }

            return {
                "success": True,
                "tenant": _doc_to_entity(updated_doc),
            }
        except PyMongoError as exc:
            logger.error("Tenant update failed: %s", exc)
            return {"success": False, "error": str(exc)}

    @staticmethod
    def update_profile(
        tenant_id: str,
        payload: dict[str, Any],
    ) -> TenantEntity | None:
        """Strictly mutate the six-field tenant profile persistence contract.

        Authority:
            Persistence only. This method does not authorize profile_update and
            does not inspect JWT, caller roles, request headers, or request state.

        Tenant scope:
            The exact supplied tenant_id is the only persistence target.

        Allowed mutation:
            Exactly the frozen PROFILE_MUTABLE_FIELDS_V1 set:
            name, alias, industry, region, sector, legal_name.

        Protected truth:
            status, plan, tax_id, contact_email, verified, compliance_flags,
            proof_hash, created_at, tenant_id, and every unknown field cannot be
            caller-mutated through this method. Checksum is regenerated internally
            from the candidate current profile; proof_hash is preserved as separate
            evidence because no canonical proof-hash mutation contract exists.

        Idempotency:
            Same-value mutation is successful and returns the current entity.
            ``modified_count == 0`` is not treated as failure.

        Return semantics:
            Genuine pre-mutation absence returns None.

        Fail-closed semantics:
            Invalid target/input/document/inconsistent-state and MongoDB outage
            raise bounded TenantRegistryError tokens. PyMongoError is preserved as
            __cause__ for TENANT_REGISTRY_PROFILE_UPDATE_UNAVAILABLE.

        Financial boundary:
            Plan and financial metadata are not mutable here. No financial
            execution authority.
        """
        _validate_profile_update_input(tenant_id, payload)

        try:
            existing_doc = tenants_collection.find_one(
                {"tenant_id": tenant_id}
            )
            if existing_doc is None:
                return None

            _doc_to_entity_for_profile_update(existing_doc)
            update_fields, _candidate = _build_profile_update(
                existing_doc,
                payload,
            )

            result = tenants_collection.update_one(
                {"tenant_id": tenant_id},
                {"$set": update_fields},
            )
            if result.matched_count != 1:
                raise TenantRegistryError(
                    "TENANT_REGISTRY_PROFILE_UPDATE_INCONSISTENT_STATE"
                )

            updated_doc = tenants_collection.find_one(
                {"tenant_id": tenant_id}
            )
            if updated_doc is None:
                raise TenantRegistryError(
                    "TENANT_REGISTRY_PROFILE_UPDATE_INCONSISTENT_STATE"
                )

            return _doc_to_entity_for_profile_update(updated_doc)
        except TenantRegistryError:
            raise
        except PyMongoError as exc:
            logger.error("Tenant profile update unavailable: %s", exc)
            raise TenantRegistryError(
                "TENANT_REGISTRY_PROFILE_UPDATE_UNAVAILABLE"
            ) from exc

    @staticmethod
    def archive(
        tenant_id: str,
        tenant_id_header: str | None = None,
    ) -> bool:
        """Archive one tenant using the preserved soft-delete contract."""
        del tenant_id_header
        try:
            result = tenants_collection.update_one(
                {"tenant_id": tenant_id},
                {"$set": {"status": "ARCHIVED"}},
            )
            return result.modified_count > 0
        except PyMongoError as exc:
            logger.error("Tenant archive unavailable: %s", exc)
            raise TenantRegistryError(
                "TENANT_REGISTRY_ARCHIVE_UNAVAILABLE"
            ) from exc


__all__ = [
    "VERSION",
    "TenantRegistry",
    "TenantRegistryError",
]


# =============================================================================
# WILSY OS SOVEREIGN ARTIFACT CERTIFICATION SEAL
# =============================================================================
# ARTIFACT: tenant_registry.py
# VERSION: v1.4.0-TENANT-PROFILE-MUTATION-PERSISTENCE
# AUTHORITY BOUNDARY: tenant persistence, hydration, exact six-field profile mutation, and bounded persistence failure signaling only; no authentication or authorization authority
# TENANT POSTURE: update_profile targets only its explicit tenant_id; no header/JWT/role/request-state scope can redirect persistence
# FAIL-CLOSED POSTURE: invalid target/input/persisted truth fails explicitly; genuine absence alone returns None; same-value profile mutation succeeds; Mongo outage raises TENANT_REGISTRY_PROFILE_UPDATE_UNAVAILABLE
# FINANCIAL EXECUTION AUTHORITY: None. Plan is immutable through update_profile; Kennel EOS remains exclusive.
# END OF WILSY OS SOVEREIGN ARTIFACT
