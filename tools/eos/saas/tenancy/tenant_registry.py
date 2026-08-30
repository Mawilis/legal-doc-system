# -*- coding: utf-8 -*-
"""
===============================================================================
WILSY OS — SOVEREIGN OPERATING SYSTEM
TENANT REGISTRY — MAPPING FAILURE SEMANTICS
===============================================================================

TITLE:
    WILSY OS Tenant Registry

FILE:
    tools/eos/saas/tenancy/tenant_registry.py

VERSION:
    v1.3.1-TENANT-REGISTRY-MAPPING-FAILURE-SEMANTICS

AUTHORITY:
    Wilsy OS Core Governance.
    Canonical MongoDB-backed tenant registry persistence boundary.

EPITOME:
    Owns tenant-registry persistence semantics while preserving the distinction
    between genuine tenant absence, infrastructure unavailability, and invalid
    persisted tenant truth. A matching document that cannot be mapped into a
    TenantEntity is never allowed to masquerade as tenant absence.

ABSOLUTE CANONICAL PATH:
    /Users/wilsonkhanyezi/legal-doc-system/tools/eos/saas/tenancy/tenant_registry.py

COLLABORATION / OWNERSHIP:
    Wilson Khanyezi / Wilsy Core Engineering.

CERTIFICATION / UPDATE DATE:
    2026-08-30

CHANGELOG:
    v1.3.1-TENANT-REGISTRY-MAPPING-FAILURE-SEMANTICS
        - Makes persisted GET mapping failure explicit.
        - Matching malformed documents raise
          TENANT_REGISTRY_GET_INVALID_DOCUMENT.
        - Genuine absence remains None.
        - Existing GET/archive infrastructure failure semantics remain exact.
        - list/create/update/get_tenant_by_alias business semantics remain
          intentionally unchanged.

    v1.3.0-TENANT-REGISTRY-FAILURE-SEMANTICS
        - Introduced TenantRegistryError.
        - Distinguished GET/archive MongoDB outages from ordinary
          absence/no-change.

COMPLIANCE:
    POPIA section 19.
    GDPR Article 32.
    SOC 2 CC7.2.
    ISO 27001.

SECURITY / PRIVACY POSTURE:
    Tenant profile persistence is bounded to the supplied tenant identifier.
    Invalid persisted GET truth fails explicitly. Infrastructure outages fail
    explicitly. Neither condition is converted into fabricated absence.
    Compatibility transport inputs do not grant or widen authority.

TENANT BOUNDARY:
    Direct GET/archive persistence operations are keyed by the supplied tenant
    identifier. The legacy tenant_id_header parameter is compatibility-only and
    never grants authority, changes tenant scope, or redirects persistence.

AUTHORITY BOUNDARY:
    This artifact owns tenant registry persistence, entity hydration, and
    bounded persistence/read-integrity failure signaling only. It does not
    authenticate callers, authorize operations, establish membership, grant
    roles, interpret JWT claims, or own HTTP authority.

FINANCIAL AUTHORITY BOUNDARY:
    No financial execution authority exists in this artifact.
    Kennel EOS remains the exclusive financial execution authority.

STRUCTURAL GOVERNANCE:
    AGENTS.md v1.2.0-SOVEREIGN-LEGAL-OPERATIONS-CONSTITUTION.
    Full-file sovereign artifact.
    Fail-closed.
===============================================================================
"""

from __future__ import annotations

import hashlib
import json
import logging
import os
import uuid
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Union

from bson import ObjectId
from bson.errors import InvalidId
from pymongo import MongoClient
from pymongo.errors import DuplicateKeyError, PyMongoError

from ..domain.tenant import OrganizationProfile, SubscriptionPlan, TenantEntity


# =============================================================================
# SOVEREIGN VERSION
# =============================================================================

VERSION = "v1.3.1-TENANT-REGISTRY-MAPPING-FAILURE-SEMANTICS"


# =============================================================================
# LOGGING AND PERSISTENCE CONNECTION
# =============================================================================

logger = logging.getLogger("WilsyOS.SaaS.Tenancy.TenantRegistry")

MONGO_URI = os.getenv("MONGODB_URI", "mongodb://127.0.0.1:27017/wilsy")
client = MongoClient(MONGO_URI, connect=False)
db = client.get_database("wilsy")
tenants_collection = db["tenants"]


# =============================================================================
# BOUNDED REGISTRY FAILURE CONTRACT
# =============================================================================


class TenantRegistryError(RuntimeError):
    """Represent bounded tenant-registry persistence/read-integrity failure.

    Authority:
        Persistence/read-integrity signaling only.

    Tenant scope:
        Does not grant tenant access or alter lookup scope.

    Failure semantics:
        Used for infrastructure unavailability and invalid persisted tenant
        truth at explicitly governed registry boundaries. It does not represent
        genuine tenant absence, authentication failure, authorization denial,
        membership state, role possession, HTTP status, or financial execution.

    Mutation semantics:
        Raising this exception performs no mutation by itself.

    Financial boundary:
        No financial execution authority. Kennel EOS remains exclusive.
    """


# =============================================================================
# PRIVATE PERSISTENCE / HYDRATION HELPERS
# =============================================================================


def _to_plan_enum(plan_str: str) -> Any:
    """Convert a persisted plan string to the existing SubscriptionPlan shape."""
    plan_str = (plan_str or "BASIC").upper()
    try:
        return SubscriptionPlan[plan_str]
    except (KeyError, AttributeError):
        return getattr(SubscriptionPlan, plan_str, plan_str)


def _to_iso_datetime(dt: Union[datetime, str, None]) -> str:
    """Convert datetime/string input to the registry's existing ISO-string shape."""
    if isinstance(dt, datetime):
        return dt.isoformat()
    if isinstance(dt, str) and dt.strip():
        return dt
    return datetime.now(timezone.utc).isoformat()


def _build_tenant_entity(
    *,
    tenant_id: str,
    organization: OrganizationProfile,
    status: str,
    created_at: str,
    alias: Any = None,
    region: Any = None,
    compliance_flags: Any = None,
    proof_hash: Any = None,
    verified: bool = False,
    checksum: Any = None,
) -> TenantEntity:
    """Construct TenantEntity while preserving existing constructor compatibility."""
    extended = {
        "alias": alias,
        "region": region,
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
            compliance_flags=compliance_flags,
            proof_hash=proof_hash,
            verified=verified,
        )  # type: ignore[call-arg]
    except TypeError:
        try:
            entity = TenantEntity(
                tenant_id=tenant_id,
                organization=organization,
                status=status,
                created_at=created_at,
            )  # type: ignore[call-arg]
        except TypeError:
            entity = TenantEntity(  # type: ignore[call-arg]
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


def _doc_to_entity(doc: Dict[str, Any]) -> Optional[TenantEntity]:
    """Map one tenant document using the registry's legacy tolerant contract.

    This helper intentionally returns None when a document cannot be hydrated.
    Existing list/create/update/alias-discovery semantics depend on that tolerant
    behavior and remain outside the B1.1 behavioral change.

    TenantRegistry.get() MUST use the strict GET helper below after document
    existence has been established.
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

        organization = OrganizationProfile(  # type: ignore[call-arg]
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
            compliance_flags=doc.get("compliance_flags"),
            proof_hash=doc.get("proof_hash"),
            verified=bool(doc.get("verified", False)),
            checksum=doc.get("checksum"),
        )
    except (AttributeError, KeyError, TypeError, ValueError) as exc:
        logger.error("Tenant document mapping failed for %s: %s", doc.get("_id"), exc)
        return None


def _doc_to_entity_for_get(doc: Dict[str, Any]) -> TenantEntity:
    """Hydrate an existing GET document or fail closed as invalid persisted truth.

    This helper is intentionally GET-specific. The caller has already established
    that a matching persisted document exists. Returning None here would fabricate
    tenant absence, so an unmappable document raises a bounded registry error.
    """
    entity = _doc_to_entity(doc)
    if entity is None:
        raise TenantRegistryError("TENANT_REGISTRY_GET_INVALID_DOCUMENT")
    return entity


def _entity_to_doc(entity: TenantEntity) -> Dict[str, Any]:
    """Serialize TenantEntity into the registry's existing persistence document."""
    org = entity.organization
    plan_value = org.plan.value if hasattr(org.plan, "value") else str(org.plan)
    created_raw = entity.created_at
    created_store: Any = created_raw
    return {
        "tenant_id": entity.tenant_id,
        "name": org.organization_name,
        "organization": {
            "organization_name": org.organization_name,
            "industry": org.industry,
            "plan": plan_value,
            "legal_name": org.legal_name,
            "tax_id": org.tax_id,
            "contact_email": org.contact_email,
            "regions": org.regions,
            "created_at": org.created_at,
        },
        "industry": org.industry,
        "plan": plan_value,
        "regions": org.regions,
        "status": entity.status,
        "created_at": created_store,
        "checksum": getattr(entity, "checksum", None),
        "alias": getattr(entity, "alias", None),
        "region": getattr(entity, "region", None),
        "compliance_flags": getattr(entity, "compliance_flags", None),
        "proof_hash": getattr(entity, "proof_hash", None),
        "verified": bool(getattr(entity, "verified", False)),
    }


# =============================================================================
# CANONICAL TENANT REGISTRY
# =============================================================================


class TenantRegistry:
    """Own the MongoDB-backed tenant persistence boundary.

    Authority:
        Persistence only. No authentication, authorization, membership, role,
        JWT, permission, transport, or financial authority.

    Tenant scope:
        Direct GET/archive operations use the supplied tenant identifier.
        tenant_id_header is compatibility-only and never authority.

    Mutation semantics:
        create/update/archive retain their existing persistence behavior.
        archive is a soft status transition, never hard deletion.

    Fail-closed semantics:
        GET distinguishes genuine absence, infrastructure outage, and invalid
        persisted tenant truth.

    Financial boundary:
        No financial execution authority. Kennel EOS remains exclusive.
    """

    @staticmethod
    def list(
        skip: int = 0,
        limit: int = 20,
        tenant_id_header: Optional[str] = None,
    ) -> Dict[str, Any]:
        """List persisted tenants using existing bounded fallback semantics.

        Authority:
            This method does not authorize listing.

        Tenant scope:
            tenant_id_header is compatibility-only and never narrows or grants
            access. The historical global list behavior remains contained at the
            HTTP layer and is intentionally unchanged here.

        Failure semantics:
            Existing empty-result-on-PyMongoError behavior is preserved because
            list-route migration is outside this delivery.

        Mutation semantics:
            Read-only.

        Financial boundary:
            No financial execution authority.
        """
        del tenant_id_header
        try:
            total = tenants_collection.count_documents({})
            cursor = tenants_collection.find({}, {"_id": 0}).skip(skip).limit(limit)
            docs = list(cursor)
            items: List[TenantEntity] = []
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
        tenant_id_header: Optional[str] = None,
    ) -> Optional[TenantEntity]:
        """Resolve one tenant by identifier with strict persisted-truth semantics.

        Authority:
            Persistence lookup only. This method does not authenticate or authorize.

        Tenant scope:
            Lookup is keyed by tenant_id. tenant_id_header is compatibility-only
            and never authority.

        Return semantics:
            A healthy matching document returns TenantEntity.
            Genuine absence returns None.

        Fail-closed semantics:
            MongoDB infrastructure failure raises
            TENANT_REGISTRY_GET_UNAVAILABLE with the original PyMongoError as
            __cause__.

            A matching persisted document that cannot be hydrated raises
            TENANT_REGISTRY_GET_INVALID_DOCUMENT and never masquerades as absence.

        Mutation semantics:
            Read-only.

        Financial boundary:
            No financial execution authority.
        """
        del tenant_id_header
        try:
            doc = tenants_collection.find_one({"tenant_id": tenant_id})
            if not doc and len(tenant_id) == 24:
                try:
                    doc = tenants_collection.find_one({"_id": ObjectId(tenant_id)})
                except (InvalidId, TypeError):
                    doc = None

            if doc:
                return _doc_to_entity_for_get(doc)

            return None
        except PyMongoError as exc:
            logger.error("Tenant get unavailable: %s", exc)
            raise TenantRegistryError("TENANT_REGISTRY_GET_UNAVAILABLE") from exc

    @staticmethod
    def get_tenant_by_alias(
        alias: str,
        tenant_id_header: Optional[str] = None,
    ) -> Optional[TenantEntity]:
        """Retrieve a tenant by alias, tenant id, or name case-insensitively.

        Authority:
            Persistence discovery only. No authorization grant is implied.

        Tenant scope:
            tenant_id_header is compatibility-only and never authority.

        Failure semantics:
            Existing alias-discovery behavior is intentionally preserved.

        Mutation semantics:
            Read-only.

        Financial boundary:
            No financial execution authority.
        """
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
        if doc:
            return _doc_to_entity(doc)
        return None

    @staticmethod
    def create(
        payload: Dict[str, Any],
        tenant_id_header: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Create one tenant using the existing registry create contract.

        Authority:
            Persistence only. This method does not authorize lifecycle creation.

        Tenant scope:
            tenant_id_header is ignored as authority.

        Mutation semantics:
            Existing structured success/error behavior is preserved.

        Failure semantics:
            Existing DuplicateKeyError/PyMongoError return semantics are preserved.

        Financial boundary:
            No financial execution authority.
        """
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
                    "regions": payload.get("regions", ["Africa", "Europe"]),
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
            entity = _doc_to_entity(doc)
            return {"success": True, "tenant": entity}
        except DuplicateKeyError:
            return {"success": False, "error": "Tenant ID already exists."}
        except PyMongoError as exc:
            logger.error("Tenant create failed: %s", exc)
            return {"success": False, "error": str(exc)}

    @staticmethod
    def update(
        tenant_id: str,
        payload: Dict[str, Any],
        tenant_id_header: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Update one tenant using the pre-existing registry field contract.

        Authority:
            Persistence only. This method does not authorize profile mutation.

        Tenant scope:
            tenant_id_header is compatibility-only and never authority.

        Mutation semantics:
            Existing field and return semantics are preserved. Field-policy
            alignment remains outside this delivery.

        Failure semantics:
            Existing structured PyMongoError behavior is preserved.

        Financial boundary:
            No financial execution authority.
        """
        del tenant_id_header
        try:
            doc = tenants_collection.find_one({"tenant_id": tenant_id})
            if not doc:
                return {"success": False, "error": "Tenant not found."}

            update_fields: Dict[str, Any] = {}
            if "name" in payload:
                update_fields["name"] = payload["name"]
                update_fields["organization.organization_name"] = payload["name"]
            if "industry" in payload:
                update_fields["industry"] = payload["industry"]
                update_fields["organization.industry"] = payload["industry"]
            if "plan" in payload:
                plan_val = str(payload["plan"]).upper()
                update_fields["plan"] = plan_val
                update_fields["organization.plan"] = plan_val
                update_fields["subscription.plan"] = plan_val.lower()
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
                update_fields["organization.contact_email"] = payload["contact_email"]
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
                update_fields["compliance_flags"] = payload["compliance_flags"]
            if "verified" in payload:
                update_fields["verified"] = payload["verified"]

            if not update_fields:
                return {"success": False, "error": "No fields to update."}

            result = tenants_collection.update_one(
                {"tenant_id": tenant_id},
                {"$set": update_fields},
            )
            if result.modified_count == 0:
                return {"success": False, "error": "No changes made."}

            updated_doc = tenants_collection.find_one({"tenant_id": tenant_id})
            if not updated_doc:
                return {
                    "success": False,
                    "error": "Failed to retrieve updated tenant.",
                }

            return {"success": True, "tenant": _doc_to_entity(updated_doc)}
        except PyMongoError as exc:
            logger.error("Tenant update failed: %s", exc)
            return {"success": False, "error": str(exc)}

    @staticmethod
    def archive(
        tenant_id: str,
        tenant_id_header: Optional[str] = None,
    ) -> bool:
        """Archive one tenant without hard deletion.

        Authority:
            Persistence only. This method does not authorize lifecycle archival.

        Tenant scope:
            tenant_id is the exact persistence target.
            tenant_id_header is compatibility-only and never authority.

        Mutation semantics:
            Performs only ``$set: {"status": "ARCHIVED"}``.
            True means the mutation modified a document.
            False means no document was modified.
            No hard deletion occurs.

        Fail-closed semantics:
            MongoDB infrastructure failure raises
            TENANT_REGISTRY_ARCHIVE_UNAVAILABLE with the original PyMongoError as
            __cause__.

        Financial boundary:
            No financial execution authority.
        """
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


# =============================================================================
# EXPLICIT PUBLIC EXPORT SURFACE
# =============================================================================

__all__ = ["TenantRegistry", "TenantRegistryError", "VERSION"]


# =============================================================================
# WILSY OS SOVEREIGN ARTIFACT CERTIFICATION SEAL
# =============================================================================
# ARTIFACT: tenant_registry.py
# VERSION: v1.3.1-TENANT-REGISTRY-MAPPING-FAILURE-SEMANTICS
# AUTHORITY BOUNDARY: tenant registry persistence, hydration, and bounded persistence/read-integrity signaling only; no authentication or authorization authority
# TENANT POSTURE: direct GET/archive remain tenant-id scoped; compatibility headers never grant, widen, or redirect tenant authority
# FAIL-CLOSED POSTURE: genuine absence alone returns None; invalid persisted GET truth raises TENANT_REGISTRY_GET_INVALID_DOCUMENT; GET/archive outages remain explicit
# FINANCIAL EXECUTION AUTHORITY: None. Kennel EOS remains exclusive.
# END OF WILSY OS SOVEREIGN ARTIFACT
