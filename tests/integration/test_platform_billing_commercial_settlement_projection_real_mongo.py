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


def _seed_canonical_subscription(database, tenant_id):
    """Create canonical SubscriptionRegistry truth in this isolated test database."""
    from tools.eos.saas.billing import subscription_registry as subscription_registry_module
    from tools.eos.saas.billing import plan_registry as plan_registry_module
    from tools.eos.saas.billing.plan_registry import PlanRegistry
    from tools.eos.saas.billing.subscription_registry import SubscriptionRegistry

    previous_subscriptions = subscription_registry_module.subscriptions_collection
    previous_plans = plan_registry_module.plans_collection
    subscription_collection = database["subscriptions"]
    plan_collection = database["plans"]
    subscription_registry_module.subscriptions_collection = subscription_collection
    plan_registry_module.plans_collection = plan_collection
    try:
        PlanRegistry.provision_indexes()
        plan_id = f"WILSYPLAN-{uuid.uuid4().hex.upper()}"
        plan_result = PlanRegistry.create({
            "name": "Settlement Correlation Certificate",
            "price": 100.0,
            "currency": "ZAR",
            "billingFrequency": "monthly",
            "planType": "ENTERPRISE",
            "idempotencyKey": f"plan-cert-{uuid.uuid4().hex}",
            "plan_id": plan_id,
            "active": True,
            "features": ["crm.core"],
            "metadata": {"certificate": True, "catalogueAuthority": "PlanRegistry"},
            "tags": ["settlement-correlation-cert"],
            "user": "EOS-SETTLEMENT-CERT",
        })
        assert plan_result["success"] is True
        created = SubscriptionRegistry.create({
            "tenantId": tenant_id,
            "planId": plan_id,
            "startDate": "2026-01-01T00:00:00+00:00",
            "idempotencyKey": f"subscription-cert-{uuid.uuid4().hex}",
            "billingMode": "PLATFORM",
            "onboardingRef": f"ONBOARD-{tenant_id}",
            "sector": "LEGAL",
            "region": "ZA",
            "metadata": {"certificate": True},
        }, tenant_id_header=tenant_id)
        assert created["success"] is True
        return created["subscription"], subscription_collection
    finally:
        subscription_registry_module.subscriptions_collection = previous_subscriptions
        plan_registry_module.plans_collection = previous_plans


def graph():
    if not URI: raise RuntimeError("TEST_VENDOR_MONGO_URI is required")
    client = MongoClient(URI, serverSelectionTimeoutMS=2000, retryWrites=True); client.admin.command("ping")
    db = client[f"r3fc_{uuid.uuid4().hex}"]; tenant = f"tenant-{uuid.uuid4().hex}"; invoice_id = f"invoice-{uuid.uuid4().hex}"; now = datetime(2026, 1, 1, tzinfo=timezone.utc)
    subscription, subscription_collection = _seed_canonical_subscription(db, tenant)
    invoice = PlatformInvoice.from_dict({"tenant_id": tenant, "invoice_id": invoice_id, "subscription_id": subscription.subscription_id, "status": "open", "amount": 100.0, "total": 100.0, "currency": "ZAR", "issued_at": now, "created_at": now, "updated_at": now, "line_items": [{"description": "Platform", "amount": 100.0}]})
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
    return client, db, {"tenant": tenant, "invoice": invoice, "authorization": authorization, "settlement": settlement, "subscription": subscription, "subscription_collection": subscription_collection}

def project(client, db, state, settlement_id=None):
    with client.start_session() as session:
        with session.start_transaction():
            return project_platform_billing_commercial_settlement(state["tenant"], settlement_id or state["settlement"].settlement_evidence_id, settlement_collection=db["platform_billing_financial_settlement_evidence"], release_authorization_collection=db["platform_billing_release_authorizations"], platform_invoice_collection=db["invoices"], commercial_projection_collection=db["projections"], subscription_collection=state["subscription_collection"], session=session)

def test_r3fc_rm01_canonical_full_settlement():
    client, db, state = graph()
    try:
        result = project(client, db, state); invoice = db["invoices"].find_one({"invoice_id": state["invoice"].invoice_id}); assert result.tenant_id == state["tenant"] and db["projections"].count_documents({"tenant_id": state["tenant"]}) == 1 and invoice["status"] in (InvoiceStatus.PAID.value, InvoiceStatus.PAID.name) and invoice["amount_paid"] == 100.0 and invoice["outstanding_amount"] == 0  # type: ignore[index]
    finally: client.close()

def test_r3fc_rm01b_linked_invoice_settlement_preserves_canonical_subscription():
    client, db, state = graph()
    try:
        before = db["subscriptions"].find_one({
            "tenant_id": state["tenant"],
            "subscription_id": state["subscription"].subscription_id,
        })
        assert before is not None
        result = project(client, db, state)
        after = db["subscriptions"].find_one({
            "tenant_id": state["tenant"],
            "subscription_id": state["subscription"].subscription_id,
        })
        invoice = db["invoices"].find_one({"invoice_id": state["invoice"].invoice_id})
        assert result.tenant_id == state["tenant"]
        assert invoice["status"] in (InvoiceStatus.PAID.value, InvoiceStatus.PAID.name)
        assert after == before
        assert after["_registry_revision"] == before["_registry_revision"]
    finally:
        client.close()


def test_r3fc_rm01c_cross_tenant_subscription_link_cannot_settle_invoice():
    client, db, state = graph()
    try:
        db["subscriptions"].update_one(
            {"tenant_id": state["tenant"], "subscription_id": state["subscription"].subscription_id},
            {"$set": {"tenant_id": "neighbor-" + state["tenant"]}},
        )
        with pytest.raises(PlatformBillingCommercialSettlementProjectionError):
            project(client, db, state)
        invoice = db["invoices"].find_one({"invoice_id": state["invoice"].invoice_id})
        assert invoice["status"] not in (InvoiceStatus.PAID.value, InvoiceStatus.PAID.name)
        assert db["projections"].count_documents({"tenant_id": state["tenant"]}) == 0
    finally:
        client.close()


def test_r3fc_rm01d_missing_canonical_subscription_cannot_settle_invoice():
    client, db, state = graph()
    try:
        db["subscriptions"].delete_one({
            "tenant_id": state["tenant"],
            "subscription_id": state["subscription"].subscription_id,
        })
        with pytest.raises(PlatformBillingCommercialSettlementProjectionError):
            project(client, db, state)
        invoice = db["invoices"].find_one({"invoice_id": state["invoice"].invoice_id})
        assert invoice["status"] not in (InvoiceStatus.PAID.value, InvoiceStatus.PAID.name)
        assert db["projections"].count_documents({"tenant_id": state["tenant"]}) == 0
    finally:
        client.close()


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


def _atomic_transport_for_existing_execution(client, db, state):
    """Reset only settlement-stage rows and return the authenticated synthetic event."""
    from tools.eos.kennel.domain.financial_execution_provider_observation import EvidenceStrength, TransportDisposition
    from tools.eos.kennel.orchestration.authenticated_settlement_observation_ingestion import AuthenticatedSettlementTransportEvidence
    from tools.eos.kennel.registry.financial_execution_registry import FinancialExecutionFactRegistry
    from tools.eos.kennel.registry.platform_billing_financial_execution_truth_registry import PlatformBillingFinancialExecutionTruthRegistry

    settlement = state["settlement"]
    tenant_id = state["tenant"]
    platform = PlatformBillingFinancialExecutionTruthRegistry.get(
        tenant_id,
        settlement.platform_execution_truth_id,
        db["platform_billing_financial_execution_truths"],
    )
    fact = FinancialExecutionFactRegistry.get(
        tenant_id,
        platform.source_execution_fact_id,
        db["financial_execution_facts"],
    )
    db["financial_settlement_observations"].delete_many({"tenant_id": tenant_id})
    db["platform_billing_financial_settlement_evidence"].delete_many({"tenant_id": tenant_id})
    evidence = AuthenticatedSettlementTransportEvidence(
        tenant_id=tenant_id,
        provider_name=fact.provider,
        provider_execution_reference=fact.provider_execution_reference,
        settlement_reference=settlement.settlement_reference,
        provider_settlement_evidence_reference=settlement.provider_settlement_evidence_reference,
        settled_amount_minor=fact.executed_amount_minor,
        currency=fact.currency,
        payment_destination_reference=fact.payment_destination_reference,
        observed_at=settlement.settled_at,
        settled_at=settlement.settled_at,
        evidence_strength=EvidenceStrength.AUTHENTICATED,
        transport_disposition=TransportDisposition.RESPONSE_RECEIVED,
    )
    return evidence, fact.execution_fact_id, platform.execution_truth_id, settlement.created_at


def _run_atomic_settlement(client, db, state, evidence, execution_truth_id, platform_truth_id, created_at):
    from tools.eos.saas.billing.atomic_platform_settlement import (
        commit_atomic_settlement_transaction,
        ensure_atomic_settlement_audit_indexes,
        settle_platform_invoice_atomically,
    )

    observations = db["financial_settlement_observations"]
    settlement_evidence = db["platform_billing_financial_settlement_evidence"]
    projections = db["projections"]
    audit = db["billing_audit_events"]
    outbox = db["billing_outbox_events"]
    ensure_atomic_settlement_audit_indexes(audit, outbox)
    with client.start_session() as session:
        session.start_transaction()
        result = settle_platform_invoice_atomically(
            state["tenant"],
            evidence,
            execution_truth_id=execution_truth_id,
            platform_truth_id=platform_truth_id,
            execution_truth_collection=db["financial_execution_facts"],
            observation_collection=observations,
            platform_truth_collection=db["platform_billing_financial_execution_truths"],
            settlement_evidence_collection=settlement_evidence,
            release_authorization_collection=db["platform_billing_release_authorizations"],
            platform_invoice_collection=db["invoices"],
            commercial_projection_collection=projections,
            subscription_collection=state["subscription_collection"],
            audit_collection=audit,
            outbox_collection=outbox,
            session=session,
            created_at=created_at,
            projected_at=created_at,
        )

        def verify_committed():
            """Read the exact settlement graph outside the uncertain session."""
            settlement = result["settlement_evidence"]
            observation = result["observation"]
            projection = result["commercial_projection"]
            event_key = (
                f"platform-settlement:{state['tenant']}:"
                f"{settlement.settlement_evidence_id}"
            )
            invoice = db["invoices"].find_one({
                "tenant_id": state["tenant"],
                "invoice_id": state["invoice"].invoice_id,
            })
            return (
                observations.find_one({
                    "tenant_id": state["tenant"],
                    "observation_id": observation.observation_id,
                }) is not None
                and settlement_evidence.find_one({
                    "tenant_id": state["tenant"],
                    "settlement_evidence_id": settlement.settlement_evidence_id,
                    "fingerprint": settlement.fingerprint,
                }) is not None
                and projections.find_one({
                    "tenant_id": state["tenant"],
                    "projection_id": projection.projection_id,
                }) is not None
                and invoice is not None
                and invoice.get("status") in ("paid", "PAID")
                and audit.find_one({
                    "tenant_id": state["tenant"],
                    "event_key": event_key,
                    "event_type": "PLATFORM_INVOICE_SETTLED",
                }) is not None
                and outbox.find_one({
                    "tenant_id": state["tenant"],
                    "event_key": event_key,
                    "event_type": "PLATFORM_INVOICE_SETTLED",
                }) is not None
            )

        result["commit_result"] = commit_atomic_settlement_transaction(
            session,
            verify_committed=verify_committed,
            max_commit_attempts=3,
        )
        return result


def test_r3fc_rm07_atomic_settlement_commits_observation_evidence_invoice_projection_and_audit():
    client, db, state = graph()
    try:
        before_subscription = db["subscriptions"].find_one({
            "tenant_id": state["tenant"],
            "subscription_id": state["subscription"].subscription_id,
        })
        evidence, fact_id, platform_id, created_at = _atomic_transport_for_existing_execution(client, db, state)
        result = _run_atomic_settlement(client, db, state, evidence, fact_id, platform_id, created_at)
        tenant = state["tenant"]
        invoice = db["invoices"].find_one({"tenant_id": tenant, "invoice_id": state["invoice"].invoice_id})
        assert invoice["status"] in (InvoiceStatus.PAID.value, InvoiceStatus.PAID.name)
        assert db["financial_settlement_observations"].count_documents({"tenant_id": tenant}) == 1
        assert db["platform_billing_financial_settlement_evidence"].count_documents({"tenant_id": tenant}) == 1
        assert db["projections"].count_documents({"tenant_id": tenant}) == 1
        assert db["billing_audit_events"].count_documents({"tenant_id": tenant, "event_type": "PLATFORM_INVOICE_SETTLED"}) == 1
        assert db["billing_outbox_events"].count_documents({"tenant_id": tenant, "event_type": "PLATFORM_INVOICE_SETTLED"}) == 1
        after_subscription = db["subscriptions"].find_one({
            "tenant_id": tenant,
            "subscription_id": state["subscription"].subscription_id,
        })
        assert after_subscription == before_subscription
        assert result["outbox_event"]["delivery_status"] == "PENDING"
    finally:
        client.close()


def test_r3fc_rm08_atomic_settlement_abort_rolls_back_every_stage_then_recovers():
    client, db, state = graph()
    try:
        evidence, fact_id, platform_id, created_at = _atomic_transport_for_existing_execution(client, db, state)
        from tools.eos.saas.billing.atomic_platform_settlement import (
            ensure_atomic_settlement_audit_indexes,
            settle_platform_invoice_atomically,
        )
        audit = db["billing_audit_events"]
        outbox = db["billing_outbox_events"]
        ensure_atomic_settlement_audit_indexes(audit, outbox)
        with client.start_session() as session:
            with pytest.raises(RuntimeError, match="SIMULATED_INTERRUPTION"):
                with session.start_transaction():
                    settle_platform_invoice_atomically(
                        state["tenant"], evidence,
                        execution_truth_id=fact_id,
                        platform_truth_id=platform_id,
                        execution_truth_collection=db["financial_execution_facts"],
                        observation_collection=db["financial_settlement_observations"],
                        platform_truth_collection=db["platform_billing_financial_execution_truths"],
                        settlement_evidence_collection=db["platform_billing_financial_settlement_evidence"],
                        release_authorization_collection=db["platform_billing_release_authorizations"],
                        platform_invoice_collection=db["invoices"],
                        commercial_projection_collection=db["projections"],
                        subscription_collection=state["subscription_collection"],
                        audit_collection=audit,
                        outbox_collection=outbox,
                        session=session,
                        created_at=created_at,
                        projected_at=created_at,
                    )
                    raise RuntimeError("SIMULATED_INTERRUPTION")
        tenant = state["tenant"]
        invoice = db["invoices"].find_one({"tenant_id": tenant, "invoice_id": state["invoice"].invoice_id})
        assert invoice["status"] not in (InvoiceStatus.PAID.value, InvoiceStatus.PAID.name)
        assert db["financial_settlement_observations"].count_documents({"tenant_id": tenant}) == 0
        assert db["platform_billing_financial_settlement_evidence"].count_documents({"tenant_id": tenant}) == 0
        assert db["projections"].count_documents({"tenant_id": tenant}) == 0
        assert audit.count_documents({"tenant_id": tenant, "event_type": "PLATFORM_INVOICE_SETTLED"}) == 0
        assert outbox.count_documents({"tenant_id": tenant, "event_type": "PLATFORM_INVOICE_SETTLED"}) == 0

        recovered = _run_atomic_settlement(client, db, state, evidence, fact_id, platform_id, created_at)
        assert recovered["commercial_projection"].tenant_id == tenant
        assert db["financial_settlement_observations"].count_documents({"tenant_id": tenant}) == 1
        assert db["platform_billing_financial_settlement_evidence"].count_documents({"tenant_id": tenant}) == 1
        assert db["projections"].count_documents({"tenant_id": tenant}) == 1
        assert audit.count_documents({"tenant_id": tenant, "event_type": "PLATFORM_INVOICE_SETTLED"}) == 1
        assert outbox.count_documents({"tenant_id": tenant, "event_type": "PLATFORM_INVOICE_SETTLED"}) == 1
    finally:
        client.close()


def test_r3fc_rm09_atomic_duplicate_delivery_is_one_durable_settlement():
    client, db, state = graph()
    try:
        evidence, fact_id, platform_id, created_at = _atomic_transport_for_existing_execution(client, db, state)
        first = _run_atomic_settlement(client, db, state, evidence, fact_id, platform_id, created_at)
        db["billing_outbox_events"].update_one(
            {"tenant_id": state["tenant"], "event_key": first["outbox_event"]["event_key"]},
            {"$set": {"delivery_status": "DELIVERED", "delivery_attempts": 1, "delivered_at": created_at.isoformat()}},
        )
        second = _run_atomic_settlement(client, db, state, evidence, fact_id, platform_id, created_at)
        tenant = state["tenant"]
        assert first["settlement_evidence"].fingerprint == second["settlement_evidence"].fingerprint
        assert second["outbox_event"]["delivery_status"] == "DELIVERED"
        assert db["financial_settlement_observations"].count_documents({"tenant_id": tenant}) == 1
        assert db["platform_billing_financial_settlement_evidence"].count_documents({"tenant_id": tenant}) == 1
        assert db["projections"].count_documents({"tenant_id": tenant}) == 1
        assert db["billing_audit_events"].count_documents({"tenant_id": tenant, "event_type": "PLATFORM_INVOICE_SETTLED"}) == 1
        assert db["billing_outbox_events"].count_documents({"tenant_id": tenant, "event_type": "PLATFORM_INVOICE_SETTLED"}) == 1
    finally:
        client.close()


def test_r3fc_rm12_unknown_commit_acknowledgement_retries_same_transaction_on_replica_set():
    """A one-shot unknown commit result is retried on the same session and commits once."""
    client, db, state = graph()
    try:
        evidence, fact_id, platform_id, created_at = _atomic_transport_for_existing_execution(
            client, db, state
        )
        client.admin.command({
            "configureFailPoint": "failCommand",
            "mode": {"times": 1},
            "data": {
                "failCommands": ["commitTransaction"],
                "errorCode": 91,
                "errorLabels": ["UnknownTransactionCommitResult"],
            },
        })
        result = _run_atomic_settlement(
            client, db, state, evidence, fact_id, platform_id, created_at
        )
        tenant = state["tenant"]
        event_key = (
            f"platform-settlement:{tenant}:"
            f"{result['settlement_evidence'].settlement_evidence_id}"
        )
        assert db["financial_settlement_observations"].count_documents({"tenant_id": tenant}) == 1
        assert db["platform_billing_financial_settlement_evidence"].count_documents({"tenant_id": tenant}) == 1
        assert db["projections"].count_documents({"tenant_id": tenant}) == 1
        assert db["invoices"].count_documents({
            "tenant_id": tenant,
            "invoice_id": state["invoice"].invoice_id,
            "status": {"$in": ["paid", "PAID"]},
        }) == 1
        assert db["billing_audit_events"].count_documents({
            "tenant_id": tenant, "event_key": event_key,
        }) == 1
        assert db["billing_outbox_events"].count_documents({
            "tenant_id": tenant, "event_key": event_key,
        }) == 1
    finally:
        try:
            client.admin.command({
                "configureFailPoint": "failCommand",
                "mode": "off",
            })
        except Exception:
            pass
        client.close()


def test_r3fc_rm13_unknown_commit_exhaustion_reconciles_exact_durable_readback(monkeypatch):
    """A committed transaction with three lost acknowledgements is read-back reconciled."""
    from pymongo.client_session import ClientSession
    from pymongo.errors import PyMongoError

    client, db, state = graph()
    try:
        evidence, fact_id, platform_id, created_at = _atomic_transport_for_existing_execution(
            client, db, state
        )
        original_commit = ClientSession.commit_transaction
        commit_calls = 0

        class LostCommitAcknowledgement(PyMongoError):
            def has_error_label(self, label):
                return label == "UnknownTransactionCommitResult"

        def commit_then_lose_ack(session, *args, **kwargs):
            nonlocal commit_calls
            commit_calls += 1
            original_commit(session, *args, **kwargs)
            raise LostCommitAcknowledgement("server commit completed; acknowledgement was lost")

        monkeypatch.setattr(ClientSession, "commit_transaction", commit_then_lose_ack)
        result = _run_atomic_settlement(
            client, db, state, evidence, fact_id, platform_id, created_at
        )
        tenant = state["tenant"]
        assert commit_calls == 3
        assert result["commit_result"] == "COMMITTED_RECONCILED"
        assert db["financial_settlement_observations"].count_documents({"tenant_id": tenant}) == 1
        assert db["platform_billing_financial_settlement_evidence"].count_documents({"tenant_id": tenant}) == 1
        assert db["projections"].count_documents({"tenant_id": tenant}) == 1
        assert db["invoices"].count_documents({
            "tenant_id": tenant,
            "invoice_id": state["invoice"].invoice_id,
            "status": {"$in": ["paid", "PAID"]},
        }) == 1
        assert db["billing_audit_events"].count_documents({
            "tenant_id": tenant,
            "event_type": "PLATFORM_INVOICE_SETTLED",
        }) == 1
        assert db["billing_outbox_events"].count_documents({
            "tenant_id": tenant,
            "event_type": "PLATFORM_INVOICE_SETTLED",
        }) == 1
    finally:
        client.close()


def test_r3fc_rm11_concurrent_identical_settlement_delivery_converges_to_one_commit():
    """Concurrent duplicate deliveries may conflict, but whole-transaction retry converges."""
    from concurrent.futures import ThreadPoolExecutor
    from threading import Barrier
    from time import sleep

    client, db, state = graph()
    try:
        evidence, fact_id, platform_id, created_at = _atomic_transport_for_existing_execution(
            client, db, state
        )
        barrier = Barrier(2)

        def deliver():
            barrier.wait(timeout=10)
            last_error = None
            for attempt in range(3):
                try:
                    return _run_atomic_settlement(
                        client, db, state, evidence, fact_id, platform_id, created_at
                    )
                except Exception as error:
                    last_error = error
                    if attempt < 2:
                        sleep(0.05 * (attempt + 1))
            raise AssertionError("CONCURRENT_SETTLEMENT_RETRY_EXHAUSTED") from last_error

        with ThreadPoolExecutor(max_workers=2) as executor:
            results = list(executor.map(lambda _: deliver(), range(2)))

        tenant = state["tenant"]
        assert len(results) == 2
        assert all(result["settlement_evidence"].fingerprint == results[0]["settlement_evidence"].fingerprint for result in results)
        assert db["invoices"].count_documents({
            "tenant_id": tenant,
            "invoice_id": state["invoice"].invoice_id,
            "status": {"$in": [InvoiceStatus.PAID.value, InvoiceStatus.PAID.name]},
        }) == 1
        assert db["financial_settlement_observations"].count_documents({"tenant_id": tenant}) == 1
        assert db["platform_billing_financial_settlement_evidence"].count_documents({"tenant_id": tenant}) == 1
        assert db["projections"].count_documents({"tenant_id": tenant}) == 1
        assert db["billing_audit_events"].count_documents({
            "tenant_id": tenant, "event_type": "PLATFORM_INVOICE_SETTLED"
        }) == 1
        assert db["billing_outbox_events"].count_documents({
            "tenant_id": tenant, "event_type": "PLATFORM_INVOICE_SETTLED"
        }) == 1
    finally:
        client.close()


def test_r3fc_rm10_atomic_divergent_settlement_replay_is_rejected():
    from dataclasses import replace
    from tools.eos.saas.billing.atomic_platform_settlement import AtomicPlatformSettlementError

    client, db, state = graph()
    try:
        evidence, fact_id, platform_id, created_at = _atomic_transport_for_existing_execution(client, db, state)
        _run_atomic_settlement(client, db, state, evidence, fact_id, platform_id, created_at)
        divergent = replace(
            evidence,
            provider_settlement_evidence_reference="different-provider-settlement-proof",
        )
        with pytest.raises(AtomicPlatformSettlementError):
            _run_atomic_settlement(client, db, state, divergent, fact_id, platform_id, created_at)
        tenant = state["tenant"]
        assert db["financial_settlement_observations"].count_documents({"tenant_id": tenant}) == 1
        assert db["platform_billing_financial_settlement_evidence"].count_documents({"tenant_id": tenant}) == 1
        assert db["projections"].count_documents({"tenant_id": tenant}) == 1
        assert db["billing_audit_events"].count_documents({"tenant_id": tenant, "event_type": "PLATFORM_INVOICE_SETTLED"}) == 1
        assert db["billing_outbox_events"].count_documents({"tenant_id": tenant, "event_type": "PLATFORM_INVOICE_SETTLED"}) == 1
    finally:
        client.close()
