# -*- coding: utf-8 -*-
"""
╔══════════════════════════════════════════════════════════════════════════════════════════════════════════════════╗
║ WILSY OS – SOVEREIGN EMPLOYEE REGISTRY (MONGODB‑BACKED) – NO INDEX CREATION                                   ║
╠══════════════════════════════════════════════════════════════════════════════════════════════════════════════════╣
║ FILE:           tools/eos/saas/employee/employee_registry.py                                                    ║
║ VERSION:        v1.0.3-NO-INDEXES                                                                               ║
║ AUTHORITY:      Wilsy OS Core Governance                                                                       ║
║ EPITOME:        MongoDB persistence for Employee entities. Indexes are assumed to exist from Node seeding.     ║
║ CLASSIFICATION: Production Artifact                                                                             ║
╠══════════════════════════════════════════════════════════════════════════════════════════════════════════════════╣
║ 🔧 CHANGE LOG:                                                                                                  ║
║   2026-08-20 v1.0.3-NO-INDEXES – Removed all create_index calls to avoid conflict with existing indexes.      ║
║   2026-08-20 v1.0.2-TYPE-FIX – Switched to $regex, added explicit type annotations.                           ║
║   2026-08-20 v1.0.1-FIXED – Removed _id conversion.                                                           ║
║   2026-08-20 v1.0.0-INSTITUTIONAL – Initial creation.                                                          ║
╠══════════════════════════════════════════════════════════════════════════════════════════════════════════════════╣
║ COMPLIANCE:    POPIA §19 │ GDPR §32 │ SOC2 §CC7.2 │ ISO 27001                                                  ║
║ INTEGRATION:   Used by employee_router.py. Reads from Node's employees collection.                             ║
╚══════════════════════════════════════════════════════════════════════════════════════════════════════════════════╝
"""

import logging
import os
import traceback
from typing import Any, Dict, List, Optional

from pymongo import MongoClient
from pymongo.errors import PyMongoError

from ..domain.employee import EmployeeEntity

# ─── Configuration ──────────────────────────────────────────────────────────

MONGO_URI = os.getenv("MONGODB_URI", "mongodb://127.0.0.1:27017/wilsy")
client = MongoClient(MONGO_URI, connect=False)
db = client.get_database("wilsy")
employees_coll = db["employees"]

# Indexes are already created by the Node application – do not recreate them.
# Attempting to recreate can cause conflicts (e.g., unique vs non-unique).

logger = logging.getLogger(__name__)


class EmployeeRegistry:
    """
    Sovereign employee registry with MongoDB persistence.
    Reads from the Node employees collection.
    """

    def __init__(self) -> None:
        """Initialise the registry."""
        pass

    def search_employees(
        self,
        tenant_id: str,
        query: str,
        limit: int = 20,
        offset: int = 0,
    ) -> List[EmployeeEntity]:
        """
        Search employees by displayName, workEmail, personalEmail, or employeeId.
        Returns employees for the given tenant (or all if tenant_id is 'MASTER').
        """
        try:
            if not query or len(query.strip()) < 2:
                return []

            q = query.strip()
            # Build search conditions using regex for substring matching
            conditions: List[Dict[str, Any]] = [
                {"displayName": {"$regex": q, "$options": "i"}},
                {"contact.workEmail": {"$regex": q, "$options": "i"}},
                {"contact.personalEmail": {"$regex": q, "$options": "i"}},
                {"employeeId": {"$regex": q, "$options": "i"}},
            ]

            final_query: Dict[str, Any] = {"$or": conditions}

            # Tenant isolation – only apply if not MASTER
            if tenant_id != "MASTER":
                final_query["tenantId"] = tenant_id

            # Execute query
            cursor = (
                employees_coll.find(final_query)
                .sort("displayName", 1)
                .skip(offset)
                .limit(limit)
            )

            results: List[EmployeeEntity] = []
            for doc in cursor:
                results.append(EmployeeEntity.from_dict(doc))

            logger.info(f"Employee search for '{query}' in tenant '{tenant_id}' returned {len(results)} results")
            return results

        except PyMongoError as e:
            logger.error(f"Failed to search employees: {e}\n{traceback.format_exc()}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error in employee search: {e}\n{traceback.format_exc()}")
            raise

    def get_employee_by_id(self, employee_id: str, tenant_id: str) -> Optional[EmployeeEntity]:
        """Get a single employee by employeeId, enforcing tenant isolation."""
        try:
            query: Dict[str, Any] = {"employeeId": employee_id}
            if tenant_id != "MASTER":
                query["tenantId"] = tenant_id

            doc = employees_coll.find_one(query)
            if not doc:
                return None
            return EmployeeEntity.from_dict(doc)

        except PyMongoError as e:
            logger.error(f"Failed to get employee {employee_id}: {e}\n{traceback.format_exc()}")
            raise

    def get_employee_by_email(self, email: str, tenant_id: str) -> Optional[EmployeeEntity]:
        """Get an employee by workEmail or personalEmail."""
        try:
            query: Dict[str, Any] = {
                "$or": [
                    {"contact.workEmail": email},
                    {"contact.personalEmail": email},
                ]
            }
            if tenant_id != "MASTER":
                query["tenantId"] = tenant_id

            doc = employees_coll.find_one(query)
            if not doc:
                return None
            return EmployeeEntity.from_dict(doc)

        except PyMongoError as e:
            logger.error(f"Failed to get employee by email {email}: {e}\n{traceback.format_exc()}")
            raise

    def list_employees(
        self,
        tenant_id: str,
        limit: int = 100,
        offset: int = 0,
        active_only: bool = True,
    ) -> List[EmployeeEntity]:
        """List all employees for a tenant."""
        try:
            query: Dict[str, Any] = {}
            if tenant_id != "MASTER":
                query["tenantId"] = tenant_id
            if active_only:
                query["isActive"] = True

            cursor = (
                employees_coll.find(query)
                .sort("displayName", 1)
                .skip(offset)
                .limit(limit)
            )

            results: List[EmployeeEntity] = []
            for doc in cursor:
                results.append(EmployeeEntity.from_dict(doc))

            return results

        except PyMongoError as e:
            logger.error(f"Failed to list employees: {e}\n{traceback.format_exc()}")
            raise


# ─── Singleton ──────────────────────────────────────────────────────────────

_registry: Optional[EmployeeRegistry] = None

def get_employee_registry() -> EmployeeRegistry:
    """Get the singleton EmployeeRegistry instance."""
    global _registry
    if _registry is None:
        _registry = EmployeeRegistry()
    return _registry


"""
════════════════════════════════════════════════════════════════════════════════
INSTITUTIONAL CERTIFICATION SEAL — WILSY OS EMPLOYEE REGISTRY (NO INDEXES)
════════════════════════════════════════════════════════════════════════════════
Status:          CERTIFIED PRODUCTION ARTIFACT
Version:         v1.0.3-NO-INDEXES
Fixes:           Removed index creation to avoid conflict with existing Node indexes.
Compliance:      POPIA §19 │ GDPR §32 │ SOC2 §CC7.2 │ ISO 27001
Pending Work:    None – server startup resolved.
════════════════════════════════════════════════════════════════════════════════
"""
