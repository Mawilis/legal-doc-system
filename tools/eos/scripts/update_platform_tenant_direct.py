#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
WILSY OS — Platform Tenant Update (Direct MongoDB)
Version: v1.0.2
Authority: Wilsy OS Core Governance
Purpose: Directly update the platform tenant document with full CIPC data.
"""
import os
import sys
import logging
import hashlib
import json
from datetime import datetime, timezone
from pymongo import MongoClient

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("WILSY.OS.PlatformUpdateDirect")

# ─── Configuration ──────────────────────────────────────────────────────────
# Use the same tenant_id from the curl response
TENANT_ID = "WILSYTENANT-4CD2FZ4O"   # <--- Replace if your tenant_id differs!

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

def main():
    # ─── Get MongoDB URI from environment ──────────────────────────────
    mongo_uri = os.getenv("MONGODB_URI")
    if not mongo_uri:
        logger.error("❌ MONGODB_URI environment variable not set.")
        sys.exit(1)

    logger.info(f"📡 Connecting to MongoDB: {mongo_uri.split('@')[-1].split('/')[0]}...")

    try:
        client = MongoClient(mongo_uri, connect=False)
        db = client.get_database("wilsy")
        coll = db["tenants"]

        # ─── Find the tenant ──────────────────────────────────────────────
        doc = coll.find_one({"tenant_id": TENANT_ID})
        if not doc:
            logger.error(f"❌ Tenant with ID {TENANT_ID} not found.")
            sys.exit(1)

        logger.info(f"✅ Found tenant: {doc.get('name')} - {TENANT_ID}")

        # ─── Prepare update fields ────────────────────────────────────────
        now = datetime.now(timezone.utc).isoformat()
        proof_payload = {
            "tenant_id": TENANT_ID,
            "name": CIPC_DATA["enterprise_name"],
            "legal_name": CIPC_DATA["legal_name"],
            "registration": CIPC_DATA["registration_number"],
            "tax": CIPC_DATA["tax_number"],
            "director": CIPC_DATA["director"]["id_number"],
            "timestamp": now,
        }
        proof_hash = hashlib.sha3_512(
            json.dumps(proof_payload, sort_keys=True).encode("utf-8")
        ).hexdigest().upper()

        update_data = {
            "alias": "wilsy",
            "region": "ZA",
            "compliance_flags": {
                "popia_section_19": True,
                "gdpr_article_32": True,
                "soc2_cc7_2": True,
                "cipc_registered": True,
                "sars_verified": True,
            },
            "proof_hash": proof_hash,
            "status": "ACTIVE",
            "industry": CIPC_DATA["enterprise_type"],
            "legal_name": CIPC_DATA["legal_name"],
            "tax_id": CIPC_DATA["tax_number"],
            "contact_email": "wilson@wilsy.os",
            "metadata": {
                "registration_number": CIPC_DATA["registration_number"],
                "registration_date": CIPC_DATA["registration_date"],
                "business_start_date": CIPC_DATA["business_start_date"],
                "enterprise_status": CIPC_DATA["enterprise_status"],
                "financial_year_end": CIPC_DATA["financial_year_end"],
                "registered_address": CIPC_DATA["registered_address"],
                "director": CIPC_DATA["director"],
            },
            "updated_at": now,
        }

        # ─── Perform the update ──────────────────────────────────────────
        result = coll.update_one({"tenant_id": TENANT_ID}, {"$set": update_data})

        if result.modified_count > 0:
            logger.info("✅ Platform tenant successfully updated.")
            logger.info(f"   Proof Hash: {proof_hash[:16]}...")
        else:
            logger.warning("⚠️ No changes were made (tenant already up‑to‑date).")

        # ─── Verify ──────────────────────────────────────────────────────
        updated_doc = coll.find_one({"tenant_id": TENANT_ID})
        if updated_doc:
            logger.info("🔎 Verification:")
            logger.info(f"   - alias: {updated_doc.get('alias')}")
            logger.info(f"   - region: {updated_doc.get('region')}")
            logger.info(f"   - compliance_flags: {updated_doc.get('compliance_flags')}")
            logger.info(f"   - proof_hash: {updated_doc.get('proof_hash', '')[:16]}...")
            logger.info(f"   - metadata keys: {list(updated_doc.get('metadata', {}).keys())}")
        else:
            logger.error("❌ Could not retrieve updated tenant.")

        client.close()

    except Exception as e:
        logger.error(f"❌ Update failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
