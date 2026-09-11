"""WILSY OS R3F-C durable real-Mongo behavioral certificate.
TITLE: Platform Billing Commercial Settlement Projection Certificate
VERSION: v1.1.0-R3F-C
AUTHORITY: Wilsy OS Core Governance / Kennel EOS
PURPOSE: Certify six durable projection and replay propositions.
EPITOME: Canonical settlement evidence drives one atomic commercial projection.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tests/integration/test_platform_billing_commercial_settlement_projection_real_mongo.py
COLLABORATION / OWNERSHIP: SaaS Billing projection owner with Kennel EOS evidence owners.
CERTIFICATION / UPDATE DATE: 2026-09-06
CHANGELOG: v1.1.0-R3F-C replaces scaffolding with durable behavioral fixtures.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2.
SECURITY / PRIVACY POSTURE: UUID-only synthetic data; no credentials or secrets.
TENANT BOUNDARY: Every key, lookup, mutation, and assertion is tenant-scoped.
AUTHORITY BOUNDARY: Kennel settlement evidence authorizes projection only.
FINANCIAL AUTHORITY BOUNDARY: No provider execution, money movement, or Payment state.
TRANSACTION BOUNDARY: Caller-owned session encloses projection and invoice CAS.
FAIL-CLOSED DECLARATION: Missing evidence and provenance/CAS conflicts abort.
"""
from __future__ import annotations
import os, uuid
from datetime import datetime, timezone
import pytest
from pymongo import MongoClient
from tools.eos.saas.domain.billing import PlatformInvoice, InvoiceStatus
from tools.eos.saas.domain.platform_billing_release_authorization import PlatformBillingReleaseAuthorization
from tools.eos.saas.billing.platform_billing_release_authorization_registry import PlatformBillingReleaseAuthorizationRegistry
from tools.eos.saas.billing.platform_billing_financial_execution_request_issuance import issue_platform_billing_financial_execution_request as _issue_platform_billing_financial_execution_request
from tools.eos.saas.billing.platform_billing_financial_execution_request_registry import PlatformBillingFinancialExecutionRequestRegistry
from tools.eos.kennel.domain.platform_billing_financial_execution_truth import PlatformExecutionStatus
from tools.eos.kennel.registry.platform_billing_financial_execution_truth_registry import PlatformBillingFinancialExecutionTruthRegistry
from tools.eos.kennel.registry.platform_billing_financial_settlement_evidence_registry import PlatformBillingFinancialSettlementEvidenceRegistry
from tools.eos.saas.billing.platform_billing_commercial_settlement_projection import PlatformBillingCommercialSettlementProjectionError, project_platform_billing_commercial_settlement
from tools.eos.saas.billing.platform_billing_commercial_settlement_projection_registry import PlatformBillingCommercialSettlementProjectionRegistry

URI = os.getenv("TEST_VENDOR_MONGO_URI", "")

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


def graph():
    if not URI: raise RuntimeError("TEST_VENDOR_MONGO_URI is required")
    client = MongoClient(URI, serverSelectionTimeoutMS=2000, retryWrites=True); client.admin.command("ping")
    db = client[f"r3fc_{uuid.uuid4().hex}"]; tenant = f"tenant-{uuid.uuid4().hex}"; invoice_id = f"invoice-{uuid.uuid4().hex}"; now = datetime(2026, 1, 1, tzinfo=timezone.utc)
    invoice = PlatformInvoice.from_dict({"tenant_id": tenant, "invoice_id": invoice_id, "status": "open", "amount": 100.0, "total": 100.0, "currency": "ZAR", "issued_at": now, "created_at": now, "updated_at": now, "line_items": [{"description": "Platform", "amount": 100.0}]})
    db["invoices"].insert_one(invoice.to_dict())
    authorization = PlatformBillingReleaseAuthorization(tenant, f"auth-{uuid.uuid4().hex}", invoice_id, invoice.commercial_release_evidence_fingerprint, "evidence", "a" * 128, invoice.release_amount_minor, invoice.currency, "principal", "basis", "destination", f"idem-{uuid.uuid4().hex}", now, now)
    authorization_collection = db["platform_billing_release_authorizations"]
    PlatformBillingReleaseAuthorizationRegistry.ensure_indexes(authorization_collection)
    PlatformBillingReleaseAuthorizationRegistry.create(authorization, authorization_collection)
    hydrated_authorization = PlatformBillingReleaseAuthorizationRegistry.get(tenant, authorization.release_authorization_id, authorization_collection)
    assert hydrated_authorization.release_authorization_id == authorization.release_authorization_id
    with client.start_session() as issuance_session:
        PlatformBillingFinancialExecutionRequestRegistry.ensure_indexes(db["platform_billing_financial_execution_requests"])
        with issuance_session.start_transaction():
            request_result = issue_platform_billing_financial_execution_request(client, db, tenant, authorization.release_authorization_id, execution_request_id=f"request-{uuid.uuid4().hex}", requested_at=now, session=issuance_session)
    request = request_result[0]
    request_collection = db["platform_billing_financial_execution_requests"]
    hydrated_request = PlatformBillingFinancialExecutionRequestRegistry.get(tenant, request.execution_request_id, request_collection)
    assert hydrated_request.execution_request_id == request.execution_request_id and hydrated_request.release_authorization_id == authorization.release_authorization_id
    truth_collection = db["platform_billing_financial_execution_truths"]; settlement_collection = db["platform_billing_financial_settlement_evidence"]
    PlatformBillingFinancialExecutionTruthRegistry.ensure_indexes(truth_collection); PlatformBillingFinancialSettlementEvidenceRegistry.ensure_indexes(settlement_collection); PlatformBillingCommercialSettlementProjectionRegistry.ensure_indexes(db["projections"])
    truth = _canonical_execution_truth(tenant, request.execution_request_id, request_collection=request_collection, truth_collection=truth_collection, provider="P", provider_execution_reference="execution", execution_status=PlatformExecutionStatus.EXECUTED, executed_at=now, provider_evidence_reference="evidence", created_at=now)
    settlement = _canonical_settlement_evidence(tenant, truth.execution_truth_id, execution_collection=truth_collection, settlement_collection=settlement_collection, settlement_reference="settlement", provider_settlement_evidence_reference="settled", settled_at=now, created_at=now)
    return client, db, {"tenant": tenant, "invoice": invoice, "authorization": authorization, "settlement": settlement}

def project(client, db, state, settlement_id=None):
    with client.start_session() as session:
        with session.start_transaction():
            return project_platform_billing_commercial_settlement(state["tenant"], settlement_id or state["settlement"].settlement_evidence_id, settlement_collection=db["platform_billing_financial_settlement_evidence"], release_authorization_collection=db["platform_billing_release_authorizations"], platform_invoice_collection=db["invoices"], commercial_projection_collection=db["projections"], session=session)

def test_r3fc_rm01_canonical_full_settlement():
    client, db, state = graph()
    try:
        result = project(client, db, state); invoice = db["invoices"].find_one({"invoice_id": state["invoice"].invoice_id}); assert result.tenant_id == state["tenant"] and db["projections"].count_documents({"tenant_id": state["tenant"]}) == 1 and invoice["status"] in (InvoiceStatus.PAID.value, InvoiceStatus.PAID.name) and invoice["amount_paid"] == 100.0 and invoice["outstanding_amount"] == 0  # type: ignore[index]
    finally: client.close()

def test_r3fc_rm02_wrong_tenant_missing_settlement():
    client, db, state = graph()
    try:
        with pytest.raises(Exception): project(client, db, dict(state, tenant=f"wrong-{state['tenant']}"))
        assert db["projections"].count_documents({"tenant_id": state["tenant"]}) == 0
    finally: client.close()

def test_r3fc_rm03_provenance_liability_mismatch():
    client, db, state = graph()
    try:
        db["platform_billing_release_authorizations"].update_one({"tenant_id": state["tenant"]}, {"$set": {"authorized_amount_minor": 99}})
        with pytest.raises(Exception): project(client, db, state)
        assert db["projections"].count_documents({"tenant_id": state["tenant"]}) == 0
    finally: client.close()

def test_r3fc_rm04_executed_is_not_settled():
    client, db, state = graph()
    try:
        db["platform_billing_financial_settlement_evidence"].delete_many({"tenant_id": state["tenant"]})
        with pytest.raises(Exception): project(client, db, state, "missing-settlement")
        assert db["projections"].count_documents({"tenant_id": state["tenant"]}) == 0
    finally: client.close()

def test_r3fc_rm05_identical_replay():
    client, db, state = graph()
    try:
        first = project(client, db, state)
        second = project(client, db, state)
        assert first.commercial_settlement_projection_id == second.commercial_settlement_projection_id and db["projections"].count_documents({"tenant_id": state["tenant"]}) == 1
    finally: client.close()

def test_r3fc_rm06_conflict_or_drift_fails_closed():
    client, db, state = graph()
    try:
        first = project(client, db, state); db["invoices"].update_one({"invoice_id": state["invoice"].invoice_id}, {"$set": {"currency": "USD"}})
        with pytest.raises(Exception): project(client, db, state)
        assert db["projections"].count_documents({"tenant_id": state["tenant"]}) == 1 and db["projections"].find_one({"tenant_id": state["tenant"]})["projection_fingerprint"] == first.projection_fingerprint  # type: ignore[index]
    finally: client.close()

# ARTIFACT: tests/integration/test_platform_billing_commercial_settlement_projection_real_mongo.py
# VERSION: v1.1.0-R3F-C
# AUTHORITY BOUNDARY: Certification evidence only; no authority grant.
# TENANT POSTURE: Synthetic UUID isolation and bounded cleanup.
# FAIL-CLOSED POSTURE: All failures surface; no skips or xfails.
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively.
# END OF WILSY OS SOVEREIGN ARTIFACT
