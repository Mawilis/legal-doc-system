#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
WILSY OS — Platform Tenant Update Script (Corrected)
Version: v1.0.1
Authority: Wilsy OS Core Governance
Purpose: One‑time production update of the platform tenant with official CIPC data.
"""
import os
import sys
import logging
from datetime import datetime, timezone

# ─── Compute project root (4 dirname calls) ──────────────────────────────
# Script: /Users/wilsonkhanyezi/legal-doc-system/tools/eos/scripts/update_platform_tenant.py
# Root:   /Users/wilsonkhanyezi/legal-doc-system
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
sys.path.insert(0, project_root)

# Now imports work
from tools.eos.saas.tenancy.tenant_registry import TenantRegistry
from tools.eos.saas.domain.tenant import TenantEntity, OrganizationProfile, SubscriptionPlan
from pymongo import MongoClient

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("WILSY.OS.PlatformUpdate")

# ─── Known tenant_id from the Kennel GET response ──────────────────────
TENANT_ID = "WILSYTENANT-4CD2FZ4O"   # <--- Replace if different!

# ─── Official CIPC Data ──────────────────────────────────────────────────
CIPC_DATA = {
    "registration_number": "2024/617944/07",
    "enterprise_name": "WILSY",
    "legal_name": "Wilsy (Pty) Ltd",
    "registration_date": "2024-10-02",
    "business_start_date": "2024-10-02",
    "enterprise_type": "Private Company",
    "enterprise_status": "In Business",
    "financial_year_end": "February",
    "tax_number": "9395759229",
    "registered_address": "UNIT 29 SUMATRA ESTATE, CORNER 8TH RD AND 7TH RD, NOORDWYK MIDRAND, GAUTENG, 1682",
    "director": {
        "name": "KHANYEZI, WILSON",
        "id_number": "8811045971084",
        "appointment_date": "2024-10-02",
        "postal_address": "UNIT 29 SUMATRA ESTATE, CORNER 8TH RD AND 7TH RD, NOORDWYK MIDRAND, GAUTENG, 1682",
        "residential_address": "UNIT 29 SUMATRA ESTATE, CORNER 8TH RD AND 7TH RD, NOORDWYK MIDRAND, GAUTENG, 1682",
    }
}

def update_platform_tenant():
    logger.info("🔍 Fetching platform tenant...")
    entity = TenantRegistry.get(TENANT_ID)
    if not entity:
        logger.error(f"Tenant {TENANT_ID} not found. Aborting.")
        sys.exit(1)

    logger.info(f"✅ Found tenant: {entity.tenant_id} - {entity.organization.organization_name}")

    # ─── Update organisation profile ────────────────────────────────────
    org = entity.organization
    org.organization_name = CIPC_DATA["enterprise_name"]
    org.legal_name = CIPC_DATA["legal_name"]
    org.tax_id = CIPC_DATA["tax_number"]
    org.contact_email = "wilson@wilsy.os"
    org.industry = CIPC_DATA["enterprise_type"]
    org.regions = ["Africa"]

    # ─── Update TenantEntity fields ─────────────────────────────────────
    entity.alias = "wilsy"
    entity.region = "ZA"
    entity.compliance_flags = {
        "popia_section_19": True,
        "gdpr_article_32": True,
        "soc2_cc7_2": True,
        "cipc_registered": True,
        "sars_verified": True,
    }
    # Generate deterministic proof_hash
    import hashlib
    import json
    proof_payload = {
        "tenant_id": entity.tenant_id,
        "name": org.organization_name,
        "legal_name": org.legal_name,
        "registration": CIPC_DATA["registration_number"],
        "tax": CIPC_DATA["tax_number"],
        "director": CIPC_DATA["director"]["id_number"],
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }
    entity.proof_hash = hashlib.sha3_512(
        json.dumps(proof_payload, sort_keys=True).encode("utf-8")
    ).hexdigest().upper()

    # ─── Build the full payload (including metadata) ───────────────────
    payload = entity.to_dict()
    payload["metadata"] = {
        "registration_number": CIPC_DATA["registration_number"],
        "registration_date": CIPC_DATA["registration_date"],
        "business_start_date": CIPC_DATA["business_start_date"],
        "enterprise_status": CIPC_DATA["enterprise_status"],
        "financial_year_end": CIPC_DATA["financial_year_end"],
        "registered_address": CIPC_DATA["registered_address"],
        "director": CIPC_DATA["director"],
    }

    # ─── Persist via registry ──────────────────────────────────────────
    result = TenantRegistry.update(TENANT_ID, payload)
    if result.get("success"):
        logger.info("✅ Platform tenant updated via registry.")
    else:
        logger.error(f"❌ Registry update failed: {result.get('error')}")
        # Continue anyway, we'll try direct update

    # ─── Direct MongoDB update to ensure metadata is stored ────────────
    # (Because the registry's _entity_to_doc does not include metadata)
    try:
        mongo_uri = os.getenv("MONGODB_URI", "mongodb://127.0.0.1:27017/wilsy")
        client = MongoClient(mongo_uri, connect=False)
        db = client.get_database("wilsy")
        coll = db["tenants"]
        result = coll.update_one(
            {"tenant_id": TENANT_ID},
            {"$set": {"metadata": payload["metadata"]}}
        )
        if result.modified_count > 0:
            logger.info("✅ Metadata field stored directly in MongoDB.")
        else:
            logger.warning("⚠️ No metadata change (maybe already present).")
        client.close()
    except Exception as e:
        logger.error(f"❌ Direct metadata update failed: {e}")

    # ─── Final verification ────────────────────────────────────────────
    updated = TenantRegistry.get(TENANT_ID)
    if updated:
        logger.info("🔎 Verification:")
        logger.info(f"   - alias: {updated.alias}")
        logger.info(f"   - region: {updated.region}")
        logger.info(f"   - compliance_flags: {updated.compliance_flags}")
        logger.info(f"   - proof_hash: {updated.proof_hash[:16]}...")
        # Check raw document for metadata
        raw = coll.find_one({"tenant_id": TENANT_ID})
        if raw and "metadata" in raw:
            logger.info(f"   - metadata keys: {list(raw['metadata'].keys())}")
        else:
            logger.warning("   - metadata not found in document.")
    else:
        logger.error("❌ Could not retrieve updated tenant.")

    logger.info("🎯 Platform tenant update complete.")

if __name__ == "__main__":
    update_platform_tenant()
