"""P6F immutable ClientInvoice issuance-evidence registry.

TITLE: Process-Service Client Invoice Issuance Registry
VERSION: v1.0.0-PROCESS-SERVICE-CLIENT-INVOICE-ISSUANCE-REGISTRY
AUTHORITY: Wilsy OS Core Governance
EPITOME: Public registry import for the P6F persistence-only boundary.  The
         canonical evidence type and registry implementation remain in the
         issuance authority module so no second derivation path exists.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tools/eos/saas/billing/process_service_client_invoice_issuance_registry.py
COLLABORATION / OWNERSHIP: P6F issuance authority supplies immutable evidence;
                            caller supplies collection/session/transaction.
TENANT BOUNDARY: All registry records and reads are tenant-scoped.
AUTHORITY BOUNDARY: Persistence and strict hydration only; no invoice,
                     payment, settlement, or Kennel execution authority.
FINANCIAL AUTHORITY BOUNDARY: Kennel EOS exclusively owns financial execution
                              and settlement.
FAIL-CLOSED DECLARATION: This module exposes no alternate construction or
                         derivation path and re-exports only the canonical gate.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2.
CERTIFICATION / UPDATE DATE: 2026-09-15
CHANGELOG: 2026-09-15 v1.0.0 establishes the named P6F registry boundary.
"""
from __future__ import annotations

from tools.eos.saas.billing.process_service_client_invoice_issuance import (
    ProcessServiceClientInvoiceIssuanceEvidence,
    ProcessServiceClientInvoiceIssuanceError,
    ProcessServiceClientInvoiceIssuanceRegistry,
)

VERSION = "v1.0.0-PROCESS-SERVICE-CLIENT-INVOICE-ISSUANCE-REGISTRY"

__all__ = [
    "VERSION",
    "ProcessServiceClientInvoiceIssuanceError",
    "ProcessServiceClientInvoiceIssuanceEvidence",
    "ProcessServiceClientInvoiceIssuanceRegistry",
]

# ARTIFACT: process_service_client_invoice_issuance_registry.py
# VERSION: v1.0.0-PROCESS-SERVICE-CLIENT-INVOICE-ISSUANCE-REGISTRY
# AUTHORITY BOUNDARY: P6F issuance-evidence persistence/hydration only.
# TENANT POSTURE: tenant-scoped immutable records; foreign absence is silent.
# FAIL-CLOSED POSTURE: canonical implementation rejects schema, replay, and race drift.
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively owns execution and settlement.
# END OF WILSY OS SOVEREIGN ARTIFACT
