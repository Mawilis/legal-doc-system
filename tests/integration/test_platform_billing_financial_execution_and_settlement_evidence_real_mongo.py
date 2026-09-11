"""WILSY OS — R3F0 PLATFORM BILLING EXECUTION / SETTLEMENT CERTIFICATE

TITLE: Platform Billing Financial Execution and Settlement Evidence Real-Mongo Certificate
VERSION: v1.1.0-R3F0-STRUCTURAL-REMEDIATION
AUTHORITY: Wilsy OS Core Governance / Kennel EOS
PURPOSE: Execute six bounded durable platform evidence scenarios against governed Mongo.
EPITOME: Prove tenant-scoped execution-truth and settlement-evidence persistence.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tests/integration/test_platform_billing_financial_execution_and_settlement_evidence_real_mongo.py
COLLABORATION / OWNERSHIP: EOS Kennel platform-financial integration certificate.
CERTIFICATION / UPDATE DATE: 2026-09-06; structural remediation.
CHANGELOG: v1.1.0-R3F0-STRUCTURAL-REMEDIATION replaced incomplete one-line banner.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2.
SECURITY / PRIVACY POSTURE: Synthetic UUID isolation; no secrets or raw provider credentials.
TENANT BOUNDARY: Every fixture, lookup, mutation, and assertion is tenant-scoped.
AUTHORITY BOUNDARY: Evidence certification only; no authority grant.
FINANCIAL AUTHORITY BOUNDARY: Kennel EOS exclusively; no provider execution or money movement.
TRANSACTION BOUNDARY: Governed Mongo client and caller-owned persistence graph only.
FAIL-CLOSED DECLARATION: Missing URI, invalid provenance, and persistence failures fail closed.
"""
from __future__ import annotations
import os,uuid
from datetime import datetime,timezone
import pytest
from pymongo import MongoClient
from tools.eos.saas.domain.platform_billing_release_authorization import PlatformBillingReleaseAuthorization
from tools.eos.saas.billing.platform_billing_release_authorization_registry import PlatformBillingReleaseAuthorizationRegistry
from tools.eos.saas.billing.platform_billing_financial_execution_request_issuance import issue_platform_billing_financial_execution_request as _issue_platform_billing_financial_execution_request
from tools.eos.saas.billing.platform_billing_financial_execution_request_registry import PlatformBillingFinancialExecutionRequestRegistry
from tools.eos.kennel.domain.platform_billing_financial_execution_truth import PlatformExecutionStatus
from tools.eos.kennel.registry.platform_billing_financial_execution_truth_registry import PlatformBillingFinancialExecutionTruthRegistry
from tools.eos.kennel.registry.platform_billing_financial_settlement_evidence_registry import PlatformBillingFinancialSettlementEvidenceRegistry
URI=os.getenv('TEST_VENDOR_MONGO_URI','')

def _seed_platform_runtime_binding(database, tenant_id, now, session):
    from types import SimpleNamespace
    from tools.eos.kennel.domain.platform_billing_provider_policy import PlatformBillingProviderPolicy, PolicyStatus
    from tools.eos.kennel.domain.platform_billing_provider_policy_revision_authorization_subject import PlatformBillingProviderPolicyRevisionAuthorizationSubject
    from tools.eos.kennel.registry.platform_billing_provider_policy_registry import PlatformBillingProviderPolicyRegistry
    from tools.eos.kennel.registry.platform_billing_provider_policy_runtime_binding_registry import PlatformBillingProviderPolicyRuntimeBindingRegistry
    from tools.eos.kennel.orchestration.platform_billing_provider_policy_runtime_binding import bind_platform_billing_provider_policy_runtime

    policies = database["platform_billing_provider_policies"]
    bindings = database["platform_billing_provider_policy_runtime_bindings"]
    policy = PlatformBillingProviderPolicy(
        policy_id=f"policy-{tenant_id}",
        tenant_id=tenant_id,
        lane="PLATFORM_BILLING_OUTBOUND",
        authorized_provider_names=("PAYSHAP",),
        policy_revision=1,
        policy_authorization_reference=f"policy-auth-{tenant_id}",
        effective_at=now,
        expires_at=None,
        created_at=now,
        status=PolicyStatus.ACTIVE,
    )
    PlatformBillingProviderPolicyRegistry.create(policy, policies, session=session)
    subject = PlatformBillingProviderPolicyRevisionAuthorizationSubject.from_policy(policy)
    decision_id = f"policy-decision-{tenant_id}"
    evidence = SimpleNamespace(
        tenant_id=tenant_id,
        authorization_decision_id=decision_id,
        operation="platform_billing_provider_policy_activate",
        permission="platform_billing:provider_policy:admin",
        subject_reference=subject.subject_reference,
        subject_evidence_fingerprint=subject.subject_evidence_fingerprint,
    )
    bind_platform_billing_provider_policy_runtime(
        tenant_id=tenant_id,
        policy_id=policy.policy_id,
        policy_revision=policy.policy_revision,
        authorization_decision_id=decision_id,
        policy_collection=policies,
        authorization_registry=SimpleNamespace(get=lambda **_: evidence),
        binding_collection=bindings,
        binding_id=f"binding-{tenant_id}",
        activated_at=now,
        created_at=now,
        session=session,
    )


def issue_platform_billing_financial_execution_request(client, database, tenant_id, release_authorization_id, *, execution_request_id, requested_at, session):
    _seed_platform_runtime_binding(database, tenant_id, requested_at, session)
    return _issue_platform_billing_financial_execution_request(
        client,
        database,
        tenant_id,
        release_authorization_id,
        execution_request_id=execution_request_id,
        requested_at=requested_at,
        session=session,
    )


def _canonical_execution_truth(
    tenant_id,
    execution_request_id,
    *,
    request_collection,
    truth_collection,
    provider,
    provider_execution_reference,
    execution_status,
    executed_at,
    provider_evidence_reference,
    created_at,
):
    from tools.eos.kennel.domain.financial_execution_execution_time_evidence import ExecutionTimeAuthorityKind, FinancialExecutionTimeEvidence
    from tools.eos.kennel.domain.financial_execution_lifecycle import FinancialExecutionAttemptState
    from tools.eos.kennel.domain.financial_execution_provider_observation import EvidenceStrength, ObservationStatus, TransportDisposition
    from tools.eos.kennel.orchestration.authenticated_provider_observation_ingestion import AuthenticatedProviderTransportEvidence, ingest_authenticated_provider_observation
    from tools.eos.kennel.orchestration.financial_execution_attempt_issuance import FinancialExecutionAttemptIssuance, issue_financial_execution_attempt
    from tools.eos.kennel.orchestration.financial_execution_runtime_orchestrator import orchestrate_terminal_execution_fact_and_projection
    from tools.eos.kennel.orchestration.platform_billing_generic_financial_execution_command_issuance import issue_platform_billing_generic_financial_execution_command
    from tools.eos.kennel.orchestration.platform_billing_provider_routing import route_platform_billing_request
    from tools.eos.kennel.registry.financial_execution_attempt_registry import FinancialExecutionAttemptRegistry
    from tools.eos.kennel.registry.platform_billing_financial_execution_truth_registry import PlatformBillingFinancialExecutionTruthRegistry

    if getattr(execution_status, "value", execution_status) != "EXECUTED":
        raise RuntimeError("EXECUTED_EVIDENCE_REQUIRED")
    truth_id = f"platform-truth-{execution_request_id}"
    existing = truth_collection.find_one({"tenant_id": tenant_id, "execution_truth_id": truth_id})
    if existing is not None:
        hydrated = PlatformBillingFinancialExecutionTruthRegistry.get(tenant_id, truth_id, truth_collection)
        if (
            hydrated.provider_execution_reference != provider_execution_reference
            or hydrated.provider_evidence_reference != provider_evidence_reference
            or hydrated.executed_at != executed_at
        ):
            raise RuntimeError("DIVERGENT_EXECUTION_REPLAY")
        return hydrated

    database = request_collection.database
    commands = database["financial_execution_commands"]
    attempts = database["financial_execution_attempts"]
    observations = database["financial_execution_provider_observations"]
    facts = database["financial_execution_facts"]
    ap_truths = database["financial_execution_truths"]
    routing = database["platform_billing_provider_routing_decisions"]

    with database.client.start_session() as session:
        with session.start_transaction():
            route_platform_billing_request(
                tenant_id,
                execution_request_id,
                f"routing-{execution_request_id}",
                database,
                session=session,
            )
            command = issue_platform_billing_generic_financial_execution_command(
                tenant_id,
                execution_request_id,
                request_collection=request_collection,
                routing_collection=routing,
                command_collection=commands,
                session=session,
            )
            attempt_id = f"attempt-{execution_request_id}"
            attempt = issue_financial_execution_attempt(
                command,
                FinancialExecutionAttemptIssuance(
                    execution_attempt_id=attempt_id,
                    provider_name=command.provider_name,
                    created_at=command.created_at,
                    request_evidence_reference=f"request-evidence-{execution_request_id}",
                ),
                command_collection=commands,
                session=session,
            )
            FinancialExecutionAttemptRegistry.create(attempt, attempts, session=session)
            current = FinancialExecutionAttemptRegistry.get(tenant_id, attempt_id, attempts, session=session)
            transmitted = current.transition_to(FinancialExecutionAttemptState.TRANSMITTED)
            current = FinancialExecutionAttemptRegistry.transition(
                tenant_id, attempt_id, current.state, current.fingerprint, transmitted, attempts, session=session
            )
            for status, label in ((ObservationStatus.ACCEPTED, "accepted"), (ObservationStatus.PENDING, "pending")):
                result = ingest_authenticated_provider_observation(
                    tenant_id,
                    AuthenticatedProviderTransportEvidence(
                        observation_id=f"observation-{label}-{execution_request_id}",
                        tenant_id=tenant_id,
                        execution_attempt_id=attempt_id,
                        provider_name=command.provider_name,
                        observation_status=status,
                        observed_at=executed_at,
                        evidence_strength=EvidenceStrength.AUTHENTICATED,
                        transport_disposition=TransportDisposition.RESPONSE_RECEIVED,
                        provider_request_reference=f"provider-request-{execution_request_id}",
                        provider_execution_reference=f"provider-{label}-{execution_request_id}",
                        provider_evidence_reference=f"{label}-evidence-{execution_request_id}",
                    ),
                    session=session,
                    observation_collection=observations,
                    attempt_collection=attempts,
                )
                current = result.attempt

            time_evidence = FinancialExecutionTimeEvidence(
                tenant_id=tenant_id,
                execution_attempt_id=attempt_id,
                provider_name=command.provider_name,
                provider_execution_reference=provider_execution_reference,
                evidence_reference=provider_evidence_reference,
                executed_at=executed_at,
                authority_kind=ExecutionTimeAuthorityKind.PROVIDER_EXECUTION_CONFIRMATION,
                evidence_strength=EvidenceStrength.AUTHENTICATED,
            )
            result = ingest_authenticated_provider_observation(
                tenant_id,
                AuthenticatedProviderTransportEvidence(
                    observation_id=f"observation-executed-{execution_request_id}",
                    tenant_id=tenant_id,
                    execution_attempt_id=attempt_id,
                    provider_name=command.provider_name,
                    observation_status=ObservationStatus.EXECUTED,
                    observed_at=executed_at,
                    evidence_strength=EvidenceStrength.AUTHENTICATED,
                    transport_disposition=TransportDisposition.RESPONSE_RECEIVED,
                    provider_request_reference=f"provider-request-{execution_request_id}",
                    provider_execution_reference=provider_execution_reference,
                    provider_evidence_reference=provider_evidence_reference,
                    provider_occurred_at=executed_at,
                    execution_time_evidence=time_evidence,
                ),
                session=session,
                observation_collection=observations,
                attempt_collection=attempts,
            )
            current = result.attempt
            target = current.transition_to(
                FinancialExecutionAttemptState.CONFIRMED_EXECUTED,
                evidence_reference=provider_evidence_reference,
                confirmed_at=executed_at,
            )
            FinancialExecutionAttemptRegistry.transition(
                tenant_id, attempt_id, current.state, current.fingerprint, target, attempts, session=session
            )
            return orchestrate_terminal_execution_fact_and_projection(
                tenant_id,
                attempt_id,
                command_collection=commands,
                attempt_collection=attempts,
                observation_collection=observations,
                fact_collection=facts,
                ap_truth_collection=ap_truths,
                platform_truth_collection=truth_collection,
                execution_time_evidence=time_evidence,
                session=session,
            )


def _canonical_settlement_evidence(
    tenant_id,
    platform_execution_truth_id,
    *,
    execution_collection,
    settlement_collection,
    settlement_reference,
    provider_settlement_evidence_reference,
    settled_at,
    created_at,
):
    from tools.eos.kennel.domain.financial_execution_provider_observation import EvidenceStrength, TransportDisposition
    from tools.eos.kennel.orchestration.authenticated_settlement_observation_ingestion import AuthenticatedSettlementTransportEvidence, ingest_authenticated_settlement_observation
    from tools.eos.kennel.orchestration.settlement_observation_to_platform_settlement_evidence import bridge_settlement_observation_to_platform_evidence
    from tools.eos.kennel.registry.financial_execution_registry import FinancialExecutionFactRegistry
    from tools.eos.kennel.registry.platform_billing_financial_execution_truth_registry import PlatformBillingFinancialExecutionTruthRegistry

    database = execution_collection.database
    facts = database["financial_execution_facts"]
    observations = database["financial_settlement_observations"]
    with database.client.start_session() as session:
        with session.start_transaction():
            platform = PlatformBillingFinancialExecutionTruthRegistry.get(
                tenant_id, platform_execution_truth_id, execution_collection, session=session
            )
            fact = FinancialExecutionFactRegistry.get(
                tenant_id, platform.source_execution_fact_id, facts, session=session
            )
            _, observation = ingest_authenticated_settlement_observation(
                tenant_id,
                AuthenticatedSettlementTransportEvidence(
                    tenant_id=tenant_id,
                    provider_name=fact.provider,
                    provider_execution_reference=fact.provider_execution_reference,
                    settlement_reference=settlement_reference,
                    provider_settlement_evidence_reference=provider_settlement_evidence_reference,
                    settled_amount_minor=fact.executed_amount_minor,
                    currency=fact.currency,
                    payment_destination_reference=fact.payment_destination_reference,
                    observed_at=settled_at,
                    settled_at=settled_at,
                    evidence_strength=EvidenceStrength.AUTHENTICATED,
                    transport_disposition=TransportDisposition.RESPONSE_RECEIVED,
                ),
                execution_truth_id=fact.execution_fact_id,
                execution_truth_collection=facts,
                observation_collection=observations,
                session=session,
            )
            return bridge_settlement_observation_to_platform_evidence(
                tenant_id,
                observation.observation_id,
                platform_execution_truth_id,
                observation_collection=observations,
                generic_truth_collection=facts,
                platform_truth_collection=execution_collection,
                evidence_collection=settlement_collection,
                session=session,
                created_at=created_at,
            )

def setup_graph():
 if not URI: raise RuntimeError('TEST_VENDOR_MONGO_URI is required')
 c=MongoClient(URI,serverSelectionTimeoutMS=2000); d=c[f'r3f0_{uuid.uuid4().hex}']; n=datetime(2026,1,1,tzinfo=timezone.utc); a=PlatformBillingReleaseAuthorization('t','a','i','a'*128,'e','b'*128,100,'ZAR','p','basis','dest','k',n,n); ac=d['platform_billing_release_authorizations']; PlatformBillingReleaseAuthorizationRegistry.ensure_indexes(ac); ac.insert_one(a.to_persistence_dict())
 with c.start_session() as issuance_session:
  PlatformBillingFinancialExecutionRequestRegistry.ensure_indexes(d["platform_billing_financial_execution_requests"])
  with issuance_session.start_transaction(): issue_platform_billing_financial_execution_request(c,d,'t','a',execution_request_id='r',requested_at=n,session=issuance_session)
 PlatformBillingFinancialExecutionTruthRegistry.ensure_indexes(d['platform_billing_financial_execution_truths']); PlatformBillingFinancialSettlementEvidenceRegistry.ensure_indexes(d['platform_billing_financial_settlement_evidence']); return c,d,a
def truth(d, *, executed_at, created_at, provider_execution_reference='x', provider_evidence_reference='e'): return _canonical_execution_truth('t','r',request_collection=d['platform_billing_financial_execution_requests'],truth_collection=d['platform_billing_financial_execution_truths'],provider='P',provider_execution_reference=provider_execution_reference,execution_status=PlatformExecutionStatus.EXECUTED,executed_at=executed_at,provider_evidence_reference=provider_evidence_reference,created_at=created_at)
def close(c): c.close()
def test_r3f0_rm01():
 c,d,a=setup_graph()
 try:
  n=datetime(2026,1,1,tzinfo=timezone.utc); assert truth(d,executed_at=n,created_at=n).platform_invoice_id==a.platform_invoice_id
 finally: close(c)
def test_r3f0_rm02():
 c,d,_=setup_graph()
 try:
  with pytest.raises(Exception): _canonical_execution_truth('wrong','r',request_collection=d['platform_billing_financial_execution_requests'],truth_collection=d['platform_billing_financial_execution_truths'],provider='P',provider_execution_reference='x',execution_status=PlatformExecutionStatus.EXECUTED,executed_at=datetime.now(timezone.utc),provider_evidence_reference='e',created_at=datetime.now(timezone.utc))
 finally: close(c)
def test_r3f0_rm03():
 c,d,a=setup_graph()
 try:
  n=datetime(2026,1,1,tzinfo=timezone.utc); v=truth(d,executed_at=n,created_at=n); assert (v.executed_amount_minor,v.currency,v.platform_invoice_id)==(100,'ZAR',a.platform_invoice_id)
 finally: close(c)
def test_r3f0_rm04():
 c,d,_=setup_graph()
 try:
  n=datetime(2026,1,1,tzinfo=timezone.utc); v=truth(d,executed_at=n,created_at=n); s=_canonical_settlement_evidence('t',v.execution_truth_id,execution_collection=d['platform_billing_financial_execution_truths'],settlement_collection=d['platform_billing_financial_settlement_evidence'],settlement_reference='s',provider_settlement_evidence_reference='se',settled_at=n,created_at=n); assert s.platform_execution_truth_id==v.execution_truth_id
 finally: close(c)
def test_r3f0_rm05():
 c,d,_=setup_graph()
 try:
  with pytest.raises(Exception): _canonical_settlement_evidence('wrong','missing',execution_collection=d['platform_billing_financial_execution_truths'],settlement_collection=d['platform_billing_financial_settlement_evidence'],settlement_reference='s',provider_settlement_evidence_reference='se',settled_at=datetime.now(timezone.utc),created_at=datetime.now(timezone.utc))
 finally: close(c)
def test_r3f0_rm06():
 c,d,_=setup_graph()
 try:
  observed_at=datetime(2026,1,1,tzinfo=timezone.utc); created_at=datetime(2026,1,1,0,0,1,tzinfo=timezone.utc)
  first=truth(d,executed_at=observed_at,created_at=created_at)
  replay=truth(d,executed_at=observed_at,created_at=created_at)
  assert replay==first
  hydrated=PlatformBillingFinancialExecutionTruthRegistry.get('t',first.execution_truth_id,d['platform_billing_financial_execution_truths'])
  assert hydrated==first
  with pytest.raises(Exception):
   truth(d,executed_at=observed_at,created_at=created_at,provider_execution_reference='different')
  settled_at=datetime(2026,1,2,tzinfo=timezone.utc); settlement_created_at=datetime(2026,1,2,0,0,1,tzinfo=timezone.utc)
  settlement=_canonical_settlement_evidence('t',first.execution_truth_id,execution_collection=d['platform_billing_financial_execution_truths'],settlement_collection=d['platform_billing_financial_settlement_evidence'],settlement_reference='s',provider_settlement_evidence_reference='se',settled_at=settled_at,created_at=settlement_created_at)
  settlement_replay=_canonical_settlement_evidence('t',first.execution_truth_id,execution_collection=d['platform_billing_financial_execution_truths'],settlement_collection=d['platform_billing_financial_settlement_evidence'],settlement_reference='s',provider_settlement_evidence_reference='se',settled_at=settled_at,created_at=settlement_created_at)
  assert settlement_replay==settlement
  with pytest.raises(Exception):
   _canonical_settlement_evidence('t',first.execution_truth_id,execution_collection=d['platform_billing_financial_execution_truths'],settlement_collection=d['platform_billing_financial_settlement_evidence'],settlement_reference='different',provider_settlement_evidence_reference='se',settled_at=settled_at,created_at=settlement_created_at)
 finally: close(c)
# ARTIFACT: test_platform_billing_financial_execution_and_settlement_evidence_real_mongo.py
# VERSION: v1.1.0
# AUTHORITY BOUNDARY: Kennel evidence only.
# END OF WILSY OS SOVEREIGN ARTIFACT
# WILSY OS SOVEREIGN ARTIFACT STRUCTURE
# TITLE: R3F0 Platform Billing Financial Execution Truth and Settlement Evidence
# VERSION: v1.1.0-R3F0-STRUCTURAL-REMEDIATION
# AUTHORITY: Wilsy OS Core Governance / Kennel EOS
# PURPOSE: Durable, tenant-scoped platform execution and settlement evidence.
# EPITOME: Canonical platform financial truth without provider execution or money movement.
# ABSOLUTE CANONICAL PATH: tests/integration/test_platform_billing_financial_execution_and_settlement_evidence_real_mongo.py
# COLLABORATION / OWNERSHIP: Kennel EOS platform financial domain; R3F0 certificates.
# CERTIFICATION / UPDATE DATE: 2026-09-06; structural remediation.
# CHANGELOG: v1.1.0-R3F0-STRUCTURAL-REMEDIATION complete sovereign metadata alignment.
# COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2.
# SECURITY / PRIVACY POSTURE: Tenant isolation; UUID synthetic tests; no raw secrets.
# TENANT BOUNDARY: Every read, write, replay, and certificate assertion is tenant-scoped.
# AUTHORITY BOUNDARY: Kennel EOS is exclusive financial execution authority.
# FINANCIAL AUTHORITY BOUNDARY: Evidence only; no provider call, settlement inference, or paid state.
# TRANSACTION BOUNDARY: Caller-owned Mongo session propagates through durable operations.
# FAIL-CLOSED DECLARATION: Invalid authority, provenance, persistence, or hydration fails closed.
# BEGIN SOVEREIGN HEADER SEAL
# END SOVEREIGN HEADER SEAL

# ARTIFACT: tests/integration/test_platform_billing_financial_execution_and_settlement_evidence_real_mongo.py
# VERSION: v1.1.0-R3F0-STRUCTURAL-REMEDIATION
# AUTHORITY BOUNDARY: Certification evidence only.
# TENANT POSTURE: Tenant-scoped synthetic fixtures.
# FAIL-CLOSED POSTURE: Failures are surfaced; no skips.
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively.
# END OF WILSY OS SOVEREIGN ARTIFACT
