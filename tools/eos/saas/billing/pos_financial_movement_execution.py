"""WILSY OS M10B2 POS to Kennel execution bridge.
TITLE: POS Financial Movement Execution Bridge
VERSION: v1.0.0-M10B2
AUTHORITY: Wilsy OS Core Governance
EPITOME: Adapt canonical POS authorization into Kennel execution commands.
ABSOLUTE CANONICAL PATH: tools/eos/saas/billing/pos_financial_movement_execution.py
COLLABORATION / OWNERSHIP: SaaS POS adapter; Kennel owns execution truth.
CERTIFICATION / UPDATE DATE: 2026-09-06
CHANGELOG: v1.0.0-M10B2 establishes collection/refund provenance bridge.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2.
SECURITY / PRIVACY POSTURE: Opaque payment references only.
TENANT BOUNDARY: Exact tenant/location/sale/source equality required.
AUTHORITY BOUNDARY: Existing POS authorization is bound; no grant.
FINANCIAL AUTHORITY BOUNDARY: Bridge does not own execution or settlement.
TRANSACTION BOUNDARY: Caller owns collection and session.
FAIL-CLOSED DECLARATION: Any provenance drift rejects before provider.
"""
from tools.eos.kennel.domain.financial_movement_execution import FinancialMovementExecutionCommand, FinancialMovementDirection
import hashlib, json
from tools.eos.kennel.orchestration.financial_movement_execution_orchestrator import FinancialMovementExecutionOrchestrator
from ..domain.pos_commercial import POSSale, POSTenderIntent, POSRefundIntent, POSTenderType
from ..domain.pos_financial_execution_authorization import POSFinancialExecutionAuthorization, POSFinancialExecutionDirection

def _execute(sale, source, authorization, collection, orchestrator, *, session=None):
    if not isinstance(sale, POSSale) or not isinstance(source, (POSTenderIntent, POSRefundIntent)) or not isinstance(authorization, POSFinancialExecutionAuthorization): raise ValueError("M10B2_CANONICAL_INPUT_REQUIRED")
    if authorization.tenant_id != sale.tenant_id or authorization.location_id != sale.location_id or authorization.sale_id != sale.sale_id or authorization.sale_fingerprint != sale.fingerprint or source.tenant_id != sale.tenant_id or source.location_id != sale.location_id or source.sale_id != sale.sale_id or source.currency != sale.currency: raise ValueError("M10B2_PROVENANCE_INVALID")
    if authorization.authorization_fingerprint != authorization._computed_fingerprint(): raise ValueError("M10B2_AUTHORIZATION_FINGERPRINT_INVALID")
    expected = POSFinancialExecutionDirection.COLLECTION if isinstance(source, POSTenderIntent) else POSFinancialExecutionDirection.DISBURSEMENT
    if authorization.direction is not expected or authorization.source_id != (source.idempotency_key if isinstance(source, POSTenderIntent) else source.refund_intent_id): raise ValueError("M10B2_DIRECTION_OR_SOURCE_INVALID")
    if isinstance(source, POSTenderIntent):
        if source.tender_type in (POSTenderType.CASH, POSTenderType.VOUCHER, POSTenderType.STORE_CREDIT) or source.requested_amount_minor != authorization.amount_minor or source.requested_amount_minor != sale.total_minor: raise ValueError("M10B2_TENDER_INVALID")
    elif source.amount_minor != authorization.amount_minor: raise ValueError("M10B2_REFUND_INVALID")
    source_fp = hashlib.sha3_512(json.dumps(source.to_dict(), sort_keys=True, separators=(",", ":")).encode()).hexdigest()
    if authorization.source_evidence_fingerprint != source_fp: raise ValueError("M10B2_SOURCE_FINGERPRINT_INVALID")
    direction = FinancialMovementDirection.COLLECTION if expected is POSFinancialExecutionDirection.COLLECTION else FinancialMovementDirection.DISBURSEMENT
    command = FinancialMovementExecutionCommand(sale.tenant_id, authorization.authorization_id, authorization.authorization_fingerprint, "POS", sale.sale_id, authorization.sale_fingerprint, direction, authorization.authorization_id, authorization.idempotency_key, authorization.amount_minor, authorization.currency, "pos-instrument:" + authorization.source_id)
    return orchestrator.execute(command, collection, session=session)

def execute_pos_collection(sale, tender, authorization, collection, orchestrator, *, session=None): return _execute(sale, tender, authorization, collection, orchestrator, session=session)
def execute_pos_refund(sale, refund, authorization, collection, orchestrator, *, session=None): return _execute(sale, refund, authorization, collection, orchestrator, session=session)

# ARTIFACT: pos_financial_movement_execution.py
# VERSION: v1.0.0-M10B2
# AUTHORITY BOUNDARY: Kennel EOS owns execution.
# FAIL-CLOSED POSTURE: Provenance drift rejects.
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively.
# END OF WILSY OS SOVEREIGN ARTIFACT
