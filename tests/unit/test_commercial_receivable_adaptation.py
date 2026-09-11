"""WILSY OS M11B canonical invoice-adaptation certificate.
TITLE: Invoice to Receivable Adaptation Certificate
VERSION: v1.1.0-M11-R8-R3B-P6E-R1
AUTHORITY: Wilsy OS Core Governance
EPITOME: Certify pure PlatformInvoice and ClientInvoice adaptation.
ABSOLUTE CANONICAL PATH: tests/unit/test_commercial_receivable_adaptation.py
COLLABORATION / OWNERSHIP: M11B adaptation certification owner.
CERTIFICATION / UPDATE DATE: 2026-09-07
CHANGELOG: v1.1.0-M11-R8-R3B-P6E-R1 certifies legacy proof correlation beside Model-C evidence.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2.
SECURITY / PRIVACY POSTURE: No provider, payment, or credential inputs.
TENANT BOUNDARY: Source invoice tenant is preserved.
AUTHORITY BOUNDARY: Commercial adaptation only.
FINANCIAL AUTHORITY BOUNDARY: No execution, settlement, or paid truth.
TRANSACTION BOUNDARY: Pure function; no persistence.
FAIL-CLOSED DECLARATION: Non-canonical family/type rejects.
"""
from dataclasses import replace
from tools.eos.saas.domain.billing import PlatformInvoice, ClientInvoice, InvoiceStatus, CLIENT_COMMERCIAL_EVIDENCE_VERSION
from tools.eos.saas.billing.commercial_receivable_adaptation import platform_invoice_to_receivable, client_invoice_to_receivable
from tools.eos.saas.domain.commercial_receivable import ReceivableFamily, ReceivableStatus
def test_platform_and_client_adapters_preserve_canonical_fields():
 p=PlatformInvoice('t','p-1',status=InvoiceStatus.OPEN,total=10.0,amount=10.0,outstanding_amount=10.0,currency='ZAR'); c=ClientInvoice('t','c-1',status=InvoiceStatus.OPEN,total=20.0,amount=20.0,outstanding_amount=20.0,currency='ZAR'); rp=platform_invoice_to_receivable(p); rc=client_invoice_to_receivable(c); assert rp.receivable_family is ReceivableFamily.PLATFORM and rc.receivable_family is ReceivableFamily.CLIENT; assert rp.source_invoice_id=='p-1' and rc.source_invoice_id=='c-1'; assert rp.original_amount_minor==1000 and rc.original_amount_minor==2000; assert rp.status is ReceivableStatus.OPEN and rc.status is ReceivableStatus.OPEN; assert rp.receivable_fingerprint != rc.receivable_fingerprint
def test_adapters_are_pure_and_do_not_expose_override_or_payment_fields():
 p=PlatformInvoice('t','p-1',status=InvoiceStatus.OPEN,total=10.0,amount=10.0,outstanding_amount=10.0,currency='ZAR'); before=p.to_dict(); r=platform_invoice_to_receivable(p); assert p.to_dict()==before; assert not any(x in r.to_dict() for x in ('paid','settled','executed','provider','payment_destination','payable_id'))
def test_client_legacy_proof_remains_receivable_correlation_when_new_evidence_exists():
 c=ClientInvoice('t','c-1',status=InvoiceStatus.OPEN,total=20.0,amount=20.0,outstanding_amount=20.0,currency='ZAR')
 c=replace(c, commercial_evidence_version=CLIENT_COMMERCIAL_EVIDENCE_VERSION, commercial_evidence_fingerprint=c.compute_commercial_evidence_fingerprint())
 r=client_invoice_to_receivable(c)
 assert r.source_invoice_fingerprint == c.proof_hash.lower()
# ARTIFACT: test_commercial_receivable_adaptation.py
# VERSION: v1.1.0-M11-R8-R3B-P6E-R1
# AUTHORITY BOUNDARY: Commercial adaptation only.
# TENANT POSTURE: Source tenant preserved.
# FAIL-CLOSED POSTURE: Invalid family/type rejects.
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively.
# END OF WILSY OS SOVEREIGN ARTIFACT
