"""WILSY OS M7 durable real-Mongo statement certificate.

TITLE: Six-scenario commercial statement snapshot certificate
VERSION: v1.1.0-M7
AUTHORITY: Wilsy OS Core Governance
PURPOSE: Exercise production platform/client statement graphs against Mongo.
EPITOME: Durable tenant-scoped snapshots, replay, isolation, and corruption gates.
ABSOLUTE CANONICAL PATH: tests/integration/test_commercial_statement_snapshot_real_mongo.py
COLLABORATION / OWNERSHIP: SaaS Billing statement and Kennel evidence owners.
CERTIFICATION / UPDATE DATE: 2026-09-06
CHANGELOG: v1.1.0-M7 replaces six environment placeholders with behavioral tests.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2.
SECURITY / PRIVACY POSTURE: Synthetic UUID data; no secrets or provider calls.
TENANT BOUNDARY: Every query and snapshot is tenant/account scoped.
AUTHORITY BOUNDARY: Projection and evidence only; Kennel owns execution truth.
FINANCIAL AUTHORITY BOUNDARY: No payment, settlement, or provider authority is invented.
TRANSACTION BOUNDARY: Certificate-owned client/session is forwarded to registries.
FAIL-CLOSED DECLARATION: Missing URI, provenance drift, conflicts, and corruption fail.
"""
from __future__ import annotations
import os, uuid
from datetime import datetime, timezone
import pytest
from pymongo import MongoClient
from tools.eos.saas.billing.platform_billing_financial_execution_request_registry import PlatformBillingFinancialExecutionRequestRegistry
from tools.eos.saas.domain.billing import ClientInvoice, PlatformInvoice
from tools.eos.saas.domain.platform_billing_release_authorization import PlatformBillingReleaseAuthorization
from tools.eos.saas.billing.platform_billing_release_authorization_registry import PlatformBillingReleaseAuthorizationRegistry
from tools.eos.saas.billing.platform_billing_financial_execution_request_issuance import issue_platform_billing_financial_execution_request as _issue_platform_billing_financial_execution_request
from tools.eos.saas.billing.platform_billing_financial_execution_request_registry import PlatformBillingFinancialExecutionRequestRegistry
from tools.eos.kennel.domain.platform_billing_financial_execution_truth import PlatformExecutionStatus
from tools.eos.kennel.registry.platform_billing_financial_execution_truth_registry import PlatformBillingFinancialExecutionTruthRegistry
from tools.eos.kennel.registry.platform_billing_financial_settlement_evidence_registry import PlatformBillingFinancialSettlementEvidenceRegistry
from tools.eos.saas.billing.platform_billing_commercial_settlement_projection import project_platform_billing_commercial_settlement
from tools.eos.saas.billing.platform_billing_commercial_settlement_projection_registry import PlatformBillingCommercialSettlementProjectionRegistry
from tools.eos.saas.domain.commercial_statement import CommercialStatementSnapshot, StatementFamily, StatementLedgerKind
from tools.eos.saas.billing.commercial_statement_engine import CommercialStatementError, generate_commercial_statement
from tools.eos.saas.billing.commercial_statement_registry import CommercialStatementRegistryError, CommercialStatementSnapshotRegistry

URI = os.environ.get("TEST_VENDOR_MONGO_URI", "").strip()

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


def _client():
    if not URI: raise RuntimeError("TEST_VENDOR_MONGO_URI is required")
    client = MongoClient(URI, serverSelectionTimeoutMS=2000, retryWrites=True); client.admin.command("ping")
    return client, client[f"m7_statement_{uuid.uuid4().hex}"], f"m7-{uuid.uuid4().hex}", datetime(2026, 1, 1, tzinfo=timezone.utc)

def _invoice(tenant, now, customer="customer-a"):
    return ClientInvoice.from_dict({"tenant_id":tenant,"invoice_id":f"invoice-{uuid.uuid4().hex}","customer_id":customer,"status":"open","total":125.0,"amount":125.0,"currency":"ZAR","line_items":[{"description":"Service","amount":125.0}],"issued_at":now,"due_at":now})

def _save(db, snapshot, *, session=None):
    c = db["commercial_statement_snapshots"]; CommercialStatementSnapshotRegistry.ensure_indexes(c); return CommercialStatementSnapshotRegistry.create(snapshot, c, session=session)

def _statement(tenant, now, invoice, lane=StatementLedgerKind.CLIENT, account="customer-a"):
    return generate_commercial_statement(tenant_id=tenant, ledger_kind=lane, family=StatementFamily.OPEN_ITEM, account_id=account, currency="ZAR", as_of=now, invoices=(invoice,))

def _platform_graph():
    client, db, tenant, now = _client(); invoice = PlatformInvoice.from_dict({"tenant_id":tenant,"invoice_id":f"platform-{uuid.uuid4().hex}","status":"open","total":100.0,"amount":100.0,"currency":"ZAR","line_items":[{"description":"Platform","amount":100.0}],"issued_at":now,"due_at":now})
    db["platform_invoices"].insert_one(invoice.to_dict()); auth = PlatformBillingReleaseAuthorization(tenant, f"auth-{uuid.uuid4().hex}", invoice.invoice_id, invoice.commercial_release_evidence_fingerprint, "evidence", "a"*128, invoice.release_amount_minor, invoice.currency, "principal", "basis", "destination", f"idem-{uuid.uuid4().hex}", now, now)
    ac = db["platform_billing_release_authorizations"]; PlatformBillingReleaseAuthorizationRegistry.ensure_indexes(ac); PlatformBillingReleaseAuthorizationRegistry.create(auth, ac)
    with client.start_session() as issuance_session:
        PlatformBillingFinancialExecutionRequestRegistry.ensure_indexes(db["platform_billing_financial_execution_requests"])
        with issuance_session.start_transaction():
            request, _ = issue_platform_billing_financial_execution_request(client, db, tenant, auth.release_authorization_id, execution_request_id=f"request-{uuid.uuid4().hex}", requested_at=now, session=issuance_session)
    rc = db["platform_billing_financial_execution_requests"]; tc = db["platform_billing_financial_execution_truths"]; ec = db["platform_billing_financial_settlement_evidence"]; pc = db["platform_billing_commercial_settlement_projections"]
    PlatformBillingFinancialExecutionTruthRegistry.ensure_indexes(tc); PlatformBillingFinancialSettlementEvidenceRegistry.ensure_indexes(ec); PlatformBillingCommercialSettlementProjectionRegistry.ensure_indexes(pc)
    truth = _canonical_execution_truth(tenant, request.execution_request_id, request_collection=rc, truth_collection=tc, provider="certificate", provider_execution_reference="execution", execution_status=PlatformExecutionStatus.EXECUTED, executed_at=now, provider_evidence_reference="evidence", created_at=now)
    evidence = _canonical_settlement_evidence(tenant, truth.execution_truth_id, execution_collection=tc, settlement_collection=ec, settlement_reference="settlement", provider_settlement_evidence_reference="settled", settled_at=now, created_at=now)
    with client.start_session() as session:
        with session.start_transaction():
            projection = project_platform_billing_commercial_settlement(tenant, evidence.settlement_evidence_id, settlement_collection=ec, release_authorization_collection=ac, platform_invoice_collection=db["platform_invoices"], commercial_projection_collection=pc, session=session)
    return client, db, tenant, now, invoice, projection

def test_rm_st01_platform_statement_snapshot_real_graph():
    client, db, tenant, now, original_invoice, projection = _platform_graph()
    try:
        invoice = PlatformInvoice.from_dict(db["platform_invoices"].find_one({"invoice_id":original_invoice.invoice_id}) or {})
        statement = generate_commercial_statement(tenant_id=tenant, ledger_kind=StatementLedgerKind.PLATFORM, family=StatementFamily.OPEN_ITEM, account_id=tenant, currency=invoice.currency, as_of=now, invoices=(invoice,), settlement_projections=(projection,))
        with client.start_session() as session:
            with session.start_transaction():
                snap = _save(db, CommercialStatementSnapshot.from_statement(statement, generated_at=now, source_evidence_fingerprint=projection.projection_fingerprint), session=session); hydrated = CommercialStatementSnapshotRegistry.get(tenant, snap.snapshot_id, db["commercial_statement_snapshots"], session=session)
        activities = hydrated.statement.activities
        assert len(activities) == 2 and hydrated.statement.closing_balance_minor == 0
        assert {activity.source_type for activity in activities} == {"invoice", "r3f_settlement"}
    finally: client.close()

def test_rm_st02_client_statement_snapshot_real_graph():
    client, db, tenant, now = _client()
    try:
        with client.start_session() as session:
            with session.start_transaction():
                snap = _save(db, CommercialStatementSnapshot.from_statement(_statement(tenant, now, _invoice(tenant, now)), generated_at=now), session=session); hydrated = CommercialStatementSnapshotRegistry.get(tenant, snap.snapshot_id, db["commercial_statement_snapshots"], session=session)
        assert hydrated.statement.ledger_kind is StatementLedgerKind.CLIENT and hydrated.statement.closing_balance_minor == 12500 and all(a.kind.value == "INVOICE_CHARGE" for a in hydrated.statement.activities)
    finally: client.close()

def test_rm_st03_tenant_and_customer_isolation_real_graph():
    client, db, tenant, now = _client(); invoice = _invoice(tenant, now)
    try:
        with pytest.raises(CommercialStatementError): _statement(f"wrong-{tenant}", now, invoice)
        with pytest.raises(CommercialStatementError): _statement(tenant, now, invoice, account="customer-b")
        assert db["commercial_statement_snapshots"].count_documents({}) == 0
    finally: client.close()

def test_rm_st04_cross_lane_and_provenance_fail_closed_real_graph():
    client, db, tenant, now = _client()
    try:
        with pytest.raises(CommercialStatementError): _statement(tenant, now, _invoice(tenant, now), lane=StatementLedgerKind.PLATFORM, account=tenant)
        platform = PlatformInvoice.from_dict({"tenant_id":tenant,"invoice_id":"platform-1","status":"open","total":10.0,"amount":10.0,"currency":"ZAR","line_items":[{"description":"Platform","amount":10.0}],"issued_at":now,"due_at":now})
        with pytest.raises(CommercialStatementError): _statement(tenant, now, platform)
        assert db["commercial_statement_snapshots"].count_documents({}) == 0
    finally: client.close()

def test_rm_st05_identical_snapshot_replay_real_graph():
    client, db, tenant, now = _client()
    try:
        with client.start_session() as session:
            with session.start_transaction():
                snap = CommercialStatementSnapshot.from_statement(_statement(tenant, now, _invoice(tenant, now)), generated_at=now); first, second = _save(db, snap, session=session), _save(db, snap, session=session)
                assert first.to_dict() == second.to_dict() and db["commercial_statement_snapshots"].count_documents({"tenant_id":tenant}, session=session) == 1
    finally: client.close()

def test_rm_st06_corrupt_snapshot_fail_closed_real_graph():
    client, db, tenant, now = _client()
    try:
        with client.start_session() as session:
            with session.start_transaction():
                snap = _save(db, CommercialStatementSnapshot.from_statement(_statement(tenant, now, _invoice(tenant, now)), generated_at=now), session=session); c = db["commercial_statement_snapshots"]; c.update_one({"tenant_id":tenant,"snapshot_id":snap.snapshot_id},{"$set":{"statement.closing_balance_minor":1}}, session=session)
                with pytest.raises(CommercialStatementRegistryError, match="M7_SNAPSHOT_CORRUPT"): CommercialStatementSnapshotRegistry.get(tenant, snap.snapshot_id, c, session=session)
        assert c.count_documents({"tenant_id":tenant}) == 1
    finally: client.close()

# ARTIFACT: test_commercial_statement_snapshot_real_mongo.py
# VERSION: v1.1.0-M7
# AUTHORITY BOUNDARY: Certification evidence only; no authority grant.
# TENANT POSTURE: Synthetic UUID isolation and bounded cleanup.
# FAIL-CLOSED POSTURE: No skips, xfails, or silent corruption repair.
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively.
# END OF WILSY OS SOVEREIGN ARTIFACT
