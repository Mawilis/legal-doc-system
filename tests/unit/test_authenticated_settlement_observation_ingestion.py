"""WILSY OS — M11E2D4 settlement-observation certificate.

TITLE: Authenticated Settlement Observation Unit Certificate
VERSION: v1.0.0-M11E2D4
AUTHORITY: Wilsy OS Core Governance / Kennel EOS
EPITOME: Certify execution-correlated settlement observation without platform settlement truth.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tests/unit/test_authenticated_settlement_observation_ingestion.py
COLLABORATION / OWNERSHIP: Kennel EOS settlement certificate owner.
CERTIFICATION / UPDATE DATE: 2026-09-07
CHANGELOG: v1.0.0-M11E2D4 certifies authenticated acceptance and fail-closed rejection.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2.
SECURITY / PRIVACY POSTURE: deterministic opaque references only.
TENANT BOUNDARY: tenant and execution correlation are mandatory.
AUTHORITY BOUNDARY: external evidence only; no downstream settlement authority.
FINANCIAL AUTHORITY BOUNDARY: no provider, paid, or closure state.
TRANSACTION BOUNDARY: caller-owned active session.
FAIL-CLOSED DECLARATION: weak/ambiguous evidence rejects.
"""
from datetime import datetime,timezone
from unittest.mock import Mock,patch
import pytest
from tools.eos.kennel.domain.financial_execution import FinancialExecutionTruth,FinancialExecutionStatus
from tools.eos.kennel.domain.financial_execution_provider_observation import EvidenceStrength,TransportDisposition
from tools.eos.kennel.orchestration.authenticated_settlement_observation_ingestion import *
def test_authenticated_settlement_is_correlated_and_persisted():
 n=datetime(2026,1,1,tzinfo=timezone.utc); t=FinancialExecutionTruth('gt','t','pay','auth','p','exec',FinancialExecutionStatus.EXECUTED,100,'ZAR',n,'dest','ev','a'*128,'b'*128,n); e=AuthenticatedSettlementTransportEvidence('t','p','exec','settle','settle-ev',100,'ZAR','dest',n,n,EvidenceStrength.AUTHENTICATED,TransportDisposition.RESPONSE_RECEIVED)
 with patch('tools.eos.kennel.orchestration.authenticated_settlement_observation_ingestion.FinancialExecutionTruthRegistry.get',return_value=t),patch('tools.eos.kennel.orchestration.authenticated_settlement_observation_ingestion.FinancialSettlementObservationRegistry.create',return_value=Mock()) as create: ingest_authenticated_settlement_observation('t',e,execution_truth_id='gt',execution_truth_collection=Mock(),observation_collection=Mock(),session=Mock(in_transaction=True))
 assert create.call_args.args[0].settlement_reference=='settle'
@pytest.mark.parametrize('strength',[EvidenceStrength.UNAUTHENTICATED,EvidenceStrength.CONFLICTING])
def test_weak_settlement_evidence_fails_closed(strength):
 n=datetime(2026,1,1,tzinfo=timezone.utc); e=AuthenticatedSettlementTransportEvidence('t','p','exec','settle','ev',1,'ZAR','dest',n,n,strength,TransportDisposition.RESPONSE_RECEIVED)
 with pytest.raises(AuthenticatedSettlementObservationIngestionError): ingest_authenticated_settlement_observation('t',e,execution_truth_id='x',execution_truth_collection=Mock(),observation_collection=Mock(),session=Mock(in_transaction=True))
# ARTIFACT: test_authenticated_settlement_observation_ingestion.py
# VERSION: v1.0.0-M11E2D4
# AUTHORITY BOUNDARY: certificate only; no financial authority.
# END OF WILSY OS SOVEREIGN ARTIFACT
