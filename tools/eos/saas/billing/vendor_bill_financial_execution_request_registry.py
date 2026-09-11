"""TITLE: Vendor Bill Financial Execution Request Registry.
VERSION: v1.0.0-M11-P5-R1B-AP2A.
AUTHORITY: Wilsy OS Core Governance / Kennel EOS.
EPITOME: Durable tenant-scoped AP execution-request authority.
ABSOLUTE CANONICAL PATH: tools/eos/saas/billing/vendor_bill_financial_execution_request_registry.py
COLLABORATION / OWNERSHIP: SaaS AP request authority.
CERTIFICATION / UPDATE DATE: 2026-09-07.
CHANGELOG: v1.0.0 establishes strict immutable request persistence.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2.
TENANT BOUNDARY: Exact tenant/request identity on every operation.
AUTHORITY BOUNDARY: Request persistence only; no provider selection or execution.
"""
from __future__ import annotations
from typing import Any
from tools.eos.saas.domain.vendor_bill_financial_execution_request import VendorBillFinancialExecutionRequest

class VendorBillFinancialExecutionRequestRegistry:
    """Persist, hydrate, and replay immutable AP requests."""
    @staticmethod
    def create(value: VendorBillFinancialExecutionRequest, collection: Any, *, session: Any = None) -> tuple[VendorBillFinancialExecutionRequest, bool]:
        if not isinstance(value, VendorBillFinancialExecutionRequest): raise RuntimeError("REQUEST_INVALID")
        identity={"tenant_id":value.tenant_id,"execution_command_id":value.execution_command_id}
        existing=collection.find_one(identity, session=session)
        if existing is not None:
            current=VendorBillFinancialExecutionRequestRegistry._hydrate(existing)
            if current.fingerprint==value.fingerprint: return current, True
            raise RuntimeError("REQUEST_REPLAY_CONFLICT")
        collection.insert_one({**value.__dict__,"requested_at":value.requested_at.isoformat(),"request_fingerprint":value.fingerprint},session=session)
        return value, False
    @staticmethod
    def get(tenant_id: str, request_id: str, collection: Any, *, session: Any = None) -> VendorBillFinancialExecutionRequest:
        row=collection.find_one({"tenant_id":tenant_id,"execution_command_id":request_id},session=session)
        if row is None: raise RuntimeError("REQUEST_NOT_FOUND")
        return VendorBillFinancialExecutionRequestRegistry._hydrate(row)
    @staticmethod
    def _hydrate(row: Any) -> VendorBillFinancialExecutionRequest:
        body=dict(row); body.pop("_id",None); stored=body.pop("request_fingerprint",None)
        from datetime import datetime
        if isinstance(body.get("requested_at"),str): body["requested_at"]=datetime.fromisoformat(body["requested_at"])
        value=VendorBillFinancialExecutionRequest(**body)
        if stored!=value.fingerprint: raise RuntimeError("REQUEST_PERSISTED_RECORD_INVALID")
        return value

# ARTIFACT: vendor_bill_financial_execution_request_registry.py
# VERSION: v1.0.0-M11-P5-R1B-AP2A
# AUTHORITY BOUNDARY: durable request evidence only
# FAIL-CLOSED POSTURE: corruption and divergent replay reject
# END OF WILSY OS SOVEREIGN ARTIFACT
