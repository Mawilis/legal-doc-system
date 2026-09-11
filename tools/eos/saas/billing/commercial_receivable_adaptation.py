"""WILSY OS M11B canonical invoice adaptation.
TITLE: Invoice to Commercial Receivable Adaptation
VERSION: v1.0.0-M11B
AUTHORITY: Wilsy OS Core Governance
EPITOME: Pure adaptation of canonical PlatformInvoice and ClientInvoice truth.
ABSOLUTE CANONICAL PATH: tools/eos/saas/billing/commercial_receivable_adaptation.py
COLLABORATION / OWNERSHIP: SaaS commercial adaptation owner.
CERTIFICATION / UPDATE DATE: 2026-09-07
CHANGELOG: v1.0.0-M11B establishes platform/client invoice mapping.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2.
SECURITY / PRIVACY POSTURE: No credentials, provider, or payment input accepted.
TENANT BOUNDARY: Source invoice tenant is canonical.
AUTHORITY BOUNDARY: Commercial adaptation only.
FINANCIAL AUTHORITY BOUNDARY: No execution, settlement, or paid authority.
TRANSACTION BOUNDARY: Pure function; no persistence or transaction lifecycle.
FAIL-CLOSED DECLARATION: Non-canonical invoice types reject.
"""
import hashlib, json
from tools.eos.saas.domain.billing import ClientInvoice, PlatformInvoice, to_minor_units
from tools.eos.saas.domain.commercial_receivable import CommercialReceivable, ReceivableFamily, ReceivableStatus

def _adapt(invoice, family):
    if not isinstance(invoice, (PlatformInvoice, ClientInvoice)) or invoice.invoice_type.value != family.value.lower(): raise ValueError('M11B_INVOICE_FAMILY_MISMATCH')
    amount=to_minor_units(invoice.total, invoice.currency); outstanding=to_minor_units(invoice.outstanding_amount, invoice.currency)
    source=getattr(invoice, 'commercial_release_evidence_fingerprint', '') or invoice.proof_hash.lower()
    if not source or len(source)!=128: source=hashlib.sha3_512(json.dumps(invoice.to_dict(),sort_keys=True,default=str,separators=(',',':')).encode()).hexdigest()
    return CommercialReceivable(invoice.tenant_id, family, f'{family.value.lower()}-receivable-{invoice.invoice_id}', invoice.invoice_id, invoice.currency, amount, 0, outstanding, source, ReceivableStatus.CLOSED_COMMERCIAL if outstanding==0 else ReceivableStatus.OPEN)

def platform_invoice_to_receivable(invoice: PlatformInvoice) -> CommercialReceivable:
    """Adapt canonical PlatformInvoice without caller override or persistence."""
    return _adapt(invoice, ReceivableFamily.PLATFORM)

def client_invoice_to_receivable(invoice: ClientInvoice) -> CommercialReceivable:
    """Adapt canonical ClientInvoice without caller override or persistence."""
    return _adapt(invoice, ReceivableFamily.CLIENT)

# ARTIFACT: commercial_receivable_adaptation.py
# VERSION: v1.0.0-M11B
# AUTHORITY BOUNDARY: Commercial adaptation only.
# TENANT POSTURE: Source invoice tenant preserved.
# FAIL-CLOSED POSTURE: Invalid source/family rejects.
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively.
# END OF WILSY OS SOVEREIGN ARTIFACT
