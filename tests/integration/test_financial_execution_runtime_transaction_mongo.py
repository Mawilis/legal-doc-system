"""WILSY OS cross-registry real-Mongo runtime certificate.

TITLE: Financial Execution Runtime Same-Session Transaction Certificate
VERSION: v1.1.0-M11-P5-R2E-R4-R3
AUTHORITY: Wilsy OS Core Governance / Kennel EOS
EPITOME: Certify neutral execution facts and AP/Platform projections across the six canonical collections.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tests/integration/test_financial_execution_runtime_transaction_mongo.py
COLLABORATION / OWNERSHIP: Kennel EOS host-certificate owner; R2E-R4 separate cross-registry responsibility.
CERTIFICATION / UPDATE DATE: 2026-09-08.
CHANGELOG: v1.1.0-M11-P5-R2E-R4-R3 adds live AP and Platform true-race caller-abort/fresh-retry proofs while retaining the R4 cross-registry certificate.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2.
SECURITY / PRIVACY POSTURE: UUID databases and opaque synthetic references only; no credentials or provider payloads.
TENANT BOUNDARY: Every command, attempt, observation, fact, and family-truth operation is tenant scoped.
AUTHORITY BOUNDARY: Tests exercise production registries and orchestration; fixtures never replace financial authority.
FINANCIAL AUTHORITY BOUNDARY: Execution evidence only; no settlement, paid state, receivable closure, or ClientInvoice mutation.
TRANSACTION BOUNDARY: Every certificate transaction is started, committed, or aborted by the test caller.
FAIL-CLOSED DECLARATION: Host absence, wrong replica set, duplicate races, divergent replay, and projection failures fail certification.
"""
from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timedelta, timezone
from threading import Barrier, Event
from typing import Any
from uuid import uuid4

import os
import pytest
from pymongo import MongoClient

from tools.eos.kennel.domain.financial_execution import (
    FinancialExecutionFact,
    FinancialExecutionStatus,
    FinancialExecutionTruth,
)
from tools.eos.kennel.domain.financial_execution_command import (
    AccountsPayableCommandSource,
    FinancialExecutionCommand,
    PlatformBillingCommandSource,
)
from tools.eos.kennel.domain.financial_execution_execution_time_evidence import (
    ExecutionTimeAuthorityKind,
    FinancialExecutionTimeEvidence,
)
from tools.eos.kennel.domain.financial_execution_lifecycle import (
    FinancialExecutionAttemptState,
)
from tools.eos.kennel.domain.financial_execution_provider_observation import (
    EvidenceStrength,
    ObservationStatus,
    TransportDisposition,
)
from tools.eos.kennel.domain.platform_billing_financial_execution_truth import (
    PlatformBillingFinancialExecutionTruth,
)
from tools.eos.kennel.orchestration.authenticated_provider_observation_ingestion import (
    AuthenticatedProviderTransportEvidence,
    ingest_authenticated_provider_observation,
)
from tools.eos.kennel.orchestration.financial_execution_attempt_issuance import (
    FinancialExecutionAttemptIssuance,
    issue_financial_execution_attempt,
)
from tools.eos.kennel.orchestration.financial_execution_runtime_orchestrator import (
    orchestrate_terminal_execution_fact_and_projection,
)
from tools.eos.kennel.orchestration.financial_execution_truth_derivation import (
    derive_financial_execution_fact,
)
from tools.eos.kennel.orchestration.accounts_payable_financial_execution_truth_projection import (
    project_financial_execution_fact_to_accounts_payable,
)
from tools.eos.kennel.orchestration.platform_billing_execution_truth_bridge import (
    bridge_financial_execution_fact_to_platform,
)
from tools.eos.kennel.registry.financial_execution_attempt_registry import (
    FinancialExecutionAttemptRegistry,
)
from tools.eos.kennel.registry.financial_execution_command_registry import (
    FinancialExecutionCommandRegistry,
)
from tools.eos.kennel.registry.financial_execution_provider_observation_registry import (
    FinancialExecutionProviderObservationRegistry,
)
from tools.eos.kennel.registry.financial_execution_registry import (
    FACT_COLLECTION,
    FinancialExecutionFactRegistry,
    FinancialExecutionTruthRegistry,
)
from tools.eos.kennel.registry.platform_billing_financial_execution_truth_registry import (
    PlatformBillingFinancialExecutionTruthRegistry,
    PlatformBillingFinancialExecutionTruthNotFoundError,
)


URI = "mongodb://127.0.0.1:27027/?replicaSet=wilsyVendorCertRS"
CREATED_AT = datetime(2026, 9, 8, 10, tzinfo=timezone.utc)
EXECUTED_AT = CREATED_AT - timedelta(minutes=5)
FP_A = "a" * 128
FP_B = "b" * 128
FP_C = "c" * 128

COMMAND_COLLECTION = "kennel_financial_execution_commands"
ATTEMPT_COLLECTION = "kennel_financial_execution_attempts"
OBSERVATION_COLLECTION = "kennel_financial_execution_provider_observations"
AP_TRUTH_COLLECTION = "kennel_financial_execution_truth"
PLATFORM_TRUTH_COLLECTION = "kennel_platform_billing_financial_execution_truth"


@pytest.fixture()
def mongo_db() -> Any:
    """Provide only the configured vendor URI and an isolated UUID database."""
    configured = os.environ.get("TEST_VENDOR_MONGO_URI")
    assert configured, "TEST_VENDOR_MONGO_URI is required"
    client = MongoClient(configured, serverSelectionTimeoutMS=5000, retryWrites=True)
    hello = client.admin.command("hello")
    assert hello.get("setName") == "wilsyVendorCertRS"
    assert hello.get("isWritablePrimary") is True
    database_name = f"wilsy_runtime_transaction_cert_{uuid4().hex}"
    database = client[database_name]
    try:
        _ensure_indexes(database)
        yield client, database
    finally:
        client.drop_database(database_name)
        client.close()


def _ensure_indexes(database: Any) -> None:
    """Use each production owner to establish the six canonical collections."""
    FinancialExecutionCommandRegistry.ensure_indexes(database[COMMAND_COLLECTION])
    FinancialExecutionAttemptRegistry.ensure_indexes(database[ATTEMPT_COLLECTION])
    FinancialExecutionProviderObservationRegistry.ensure_indexes(database[OBSERVATION_COLLECTION])
    FinancialExecutionFactRegistry.ensure_indexes(database[FACT_COLLECTION])
    FinancialExecutionTruthRegistry.ensure_indexes(database[AP_TRUTH_COLLECTION])
    PlatformBillingFinancialExecutionTruthRegistry.ensure_indexes(database[PLATFORM_TRUTH_COLLECTION])


def _command(tenant_id: str, family: str, suffix: str) -> FinancialExecutionCommand:
    """Build a canonical typed AP or Platform command fixture."""
    if family == "AP":
        source: Any = AccountsPayableCommandSource(
            execution_request_id=f"request-ap-{suffix}",
            execution_request_fingerprint=FP_A,
            selection_decision_id=f"selection-ap-{suffix}",
            selection_decision_fingerprint=FP_B,
            payable_id=f"payable-{suffix}",
            release_authorization_id=f"release-ap-{suffix}",
            authorized_provider_name="PAYSHAP",
        )
    else:
        source = PlatformBillingCommandSource(
            execution_request_id=f"request-platform-{suffix}",
            execution_request_fingerprint=FP_A,
            routing_decision_id=f"routing-platform-{suffix}",
            routing_decision_fingerprint=FP_B,
            platform_invoice_id=f"platform-invoice-{suffix}",
            release_authorization_id=f"release-platform-{suffix}",
            release_authorization_fingerprint=FP_C,
            authorized_provider_name="PAYSHAP",
        )
    return FinancialExecutionCommand(
        tenant_id=tenant_id,
        execution_command_id=f"command-{family.lower()}-{suffix}",
        idempotency_key=f"idempotency-{family.lower()}-{suffix}",
        amount_minor=1000,
        currency="ZAR",
        payment_destination_reference=f"destination-{suffix}",
        source_authority=source,
        provider_name="PAYSHAP",
        created_at=CREATED_AT,
    )


def _seed_attempt(command: FinancialExecutionCommand, database: Any, session: Any, suffix: str) -> str:
    """Persist a command and issue its PREPARED attempt through production owners."""
    commands = database[COMMAND_COLLECTION]
    attempts = database[ATTEMPT_COLLECTION]
    FinancialExecutionCommandRegistry.create(command, commands, session=session)
    attempt_id = f"attempt-{suffix}"
    attempt = issue_financial_execution_attempt(
        command,
        FinancialExecutionAttemptIssuance(
            execution_attempt_id=attempt_id,
            provider_name=command.provider_name,
            created_at=CREATED_AT,
            request_evidence_reference=f"request-evidence-{suffix}",
        ),
        command_collection=commands,
        session=session,
    )
    FinancialExecutionAttemptRegistry.create(attempt, attempts, session=session)
    return attempt_id


def _time_evidence(tenant_id: str, attempt_id: str, suffix: str) -> FinancialExecutionTimeEvidence:
    """Construct explicit authenticated execution-time evidence only."""
    return FinancialExecutionTimeEvidence(
        tenant_id=tenant_id,
        execution_attempt_id=attempt_id,
        provider_name="PAYSHAP",
        provider_execution_reference=f"provider-execution-{suffix}",
        evidence_reference=f"execution-evidence-{suffix}",
        executed_at=EXECUTED_AT,
        authority_kind=ExecutionTimeAuthorityKind.PROVIDER_EXECUTION_CONFIRMATION,
        evidence_strength=EvidenceStrength.AUTHENTICATED,
    )


def _apply_terminal_observation(tenant_id: str, attempt_id: str, database: Any, session: Any, suffix: str) -> None:
    """Persist authenticated observations, then perform the canonical terminal CAS."""
    observations = database[OBSERVATION_COLLECTION]
    attempts = database[ATTEMPT_COLLECTION]
    # The observation policy intentionally has no provider status that means
    # "TRANSMITTED".  Establish that transport antecedent through the frozen
    # attempt CAS before applying ACCEPTED/PENDING provider responses.
    current = FinancialExecutionAttemptRegistry.get(tenant_id, attempt_id, attempts, session=session)
    assert current is not None
    transmitted = current.transition_to(FinancialExecutionAttemptState.TRANSMITTED)
    current = FinancialExecutionAttemptRegistry.transition(
        tenant_id,
        attempt_id,
        current.state,
        current.fingerprint,
        transmitted,
        attempts,
        session=session,
    )
    accepted = AuthenticatedProviderTransportEvidence(
        observation_id=f"observation-accepted-{suffix}",
        tenant_id=tenant_id,
        execution_attempt_id=attempt_id,
        provider_name="PAYSHAP",
        observation_status=ObservationStatus.ACCEPTED,
        observed_at=EXECUTED_AT,
        evidence_strength=EvidenceStrength.AUTHENTICATED,
        transport_disposition=TransportDisposition.RESPONSE_RECEIVED,
        provider_request_reference=f"provider-request-{suffix}",
        provider_execution_reference=f"provider-accepted-{suffix}",
        provider_evidence_reference=f"accepted-evidence-{suffix}",
    )
    first = ingest_authenticated_provider_observation(
        tenant_id, accepted, session=session,
        observation_collection=observations, attempt_collection=attempts,
    )
    assert first.attempt.state is FinancialExecutionAttemptState.ACCEPTED
    pending = AuthenticatedProviderTransportEvidence(
        observation_id=f"observation-pending-{suffix}",
        tenant_id=tenant_id,
        execution_attempt_id=attempt_id,
        provider_name="PAYSHAP",
        observation_status=ObservationStatus.PENDING,
        observed_at=EXECUTED_AT,
        evidence_strength=EvidenceStrength.AUTHENTICATED,
        transport_disposition=TransportDisposition.RESPONSE_RECEIVED,
        provider_request_reference=f"provider-request-{suffix}",
        provider_execution_reference=f"provider-pending-{suffix}",
        provider_evidence_reference=f"pending-evidence-{suffix}",
    )
    pending_result = ingest_authenticated_provider_observation(
        tenant_id, pending, session=session,
        observation_collection=observations, attempt_collection=attempts,
    )
    assert pending_result.attempt.state is FinancialExecutionAttemptState.PENDING
    executed = AuthenticatedProviderTransportEvidence(
        observation_id=f"observation-executed-{suffix}",
        tenant_id=tenant_id,
        execution_attempt_id=attempt_id,
        provider_name="PAYSHAP",
        observation_status=ObservationStatus.EXECUTED,
        observed_at=EXECUTED_AT,
        evidence_strength=EvidenceStrength.AUTHENTICATED,
        transport_disposition=TransportDisposition.RESPONSE_RECEIVED,
        provider_request_reference=f"provider-request-{suffix}",
        provider_execution_reference=f"provider-execution-{suffix}",
        provider_evidence_reference=f"execution-evidence-{suffix}",
        provider_occurred_at=EXECUTED_AT,
        execution_time_evidence=_time_evidence(tenant_id, attempt_id, suffix),
    )
    second = ingest_authenticated_provider_observation(
        tenant_id, executed, session=session,
        observation_collection=observations, attempt_collection=attempts,
    )
    assert second.attempt.state is FinancialExecutionAttemptState.PENDING
    current = FinancialExecutionAttemptRegistry.get(tenant_id, attempt_id, attempts, session=session)
    target = current.transition_to(
        FinancialExecutionAttemptState.CONFIRMED_EXECUTED,
        evidence_reference=f"execution-evidence-{suffix}",
        confirmed_at=EXECUTED_AT,
    )
    terminal = FinancialExecutionAttemptRegistry.transition(
        tenant_id, attempt_id, current.state, current.fingerprint, target,
        attempts, session=session,
    )
    assert terminal.state is FinancialExecutionAttemptState.CONFIRMED_EXECUTED


def _runtime(tenant_id: str, attempt_id: str, database: Any, session: Any, suffix: str) -> Any:
    """Invoke the frozen runtime composer with all six explicit collections."""
    return orchestrate_terminal_execution_fact_and_projection(
        tenant_id,
        attempt_id,
        command_collection=database[COMMAND_COLLECTION],
        attempt_collection=database[ATTEMPT_COLLECTION],
        observation_collection=database[OBSERVATION_COLLECTION],
        fact_collection=database[FACT_COLLECTION],
        ap_truth_collection=database[AP_TRUTH_COLLECTION],
        platform_truth_collection=database[PLATFORM_TRUTH_COLLECTION],
        execution_time_evidence=_time_evidence(tenant_id, attempt_id, suffix),
        session=session,
    )


def _prepare_terminal_case(database: Any, tenant_id: str, family: str, suffix: str, client: Any) -> tuple[FinancialExecutionCommand, str]:
    """Commit canonical command/attempt antecedents before a focused runtime case."""
    session = client.start_session()
    session.start_transaction()
    try:
        command = _command(tenant_id, family, suffix)
        attempt_id = _seed_attempt(command, database, session, suffix)
        session.commit_transaction()
        return command, attempt_id
    finally:
        session.end_session()


def _seed_terminal_fact(database: Any, tenant_id: str, family: str, suffix: str, client: Any) -> tuple[FinancialExecutionCommand, str, FinancialExecutionFact]:
    """Commit command, attempt, observations, and exactly one neutral fact."""
    session = client.start_session()
    session.start_transaction()
    try:
        command = _command(tenant_id, family, suffix)
        attempt_id = _seed_attempt(command, database, session, suffix)
        _apply_terminal_observation(tenant_id, attempt_id, database, session, suffix)
        derived = derive_financial_execution_fact(
            tenant_id,
            attempt_id,
            command_collection=database[COMMAND_COLLECTION],
            attempt_collection=database[ATTEMPT_COLLECTION],
            observation_collection=database[OBSERVATION_COLLECTION],
            fact_collection=database[FACT_COLLECTION],
            execution_time_evidence=_time_evidence(tenant_id, attempt_id, suffix),
            session=session,
        )
        session.commit_transaction()
    finally:
        session.end_session()
    return command, attempt_id, derived.execution_fact


def test_ap_cross_registry_transaction_commit_and_visibility(mongo_db: Any) -> None:
    """Certify AP command through observation, neutral fact, and AP truth in one transaction."""
    client, database = mongo_db
    tenant_id, suffix = "tenant-ap", uuid4().hex
    session = client.start_session()
    session.start_transaction()
    try:
        command = _command(tenant_id, "AP", suffix)
        attempt_id = _seed_attempt(command, database, session, suffix)
        _apply_terminal_observation(tenant_id, attempt_id, database, session, suffix)
        result = _runtime(tenant_id, attempt_id, database, session, suffix)
        assert isinstance(result, FinancialExecutionTruth)
        fact = FinancialExecutionFactRegistry.get_by_attempt(tenant_id, attempt_id, database[FACT_COLLECTION], session=session)
        truth = FinancialExecutionTruthRegistry.get(tenant_id, command.execution_command_id, database[AP_TRUTH_COLLECTION], session=session)
        assert fact is not None and truth is not None
        assert isinstance(command.source_authority, AccountsPayableCommandSource)
        assert truth.payable_id == command.source_authority.payable_id
        assert fact.provider == command.provider_name
        assert database[FACT_COLLECTION].count_documents({}, session=session) == 1
        assert database[AP_TRUTH_COLLECTION].count_documents({}, session=session) == 1
        assert database[FACT_COLLECTION].count_documents({}) == 0
        assert database[AP_TRUTH_COLLECTION].count_documents({}) == 0
        session.commit_transaction()
    finally:
        session.end_session()
    assert database[FACT_COLLECTION].count_documents({}) == 1
    assert database[AP_TRUTH_COLLECTION].count_documents({}) == 1
    assert database[PLATFORM_TRUTH_COLLECTION].count_documents({}) == 0


def test_platform_cross_registry_transaction_commit_and_visibility(mongo_db: Any) -> None:
    """Certify Platform command through observation, neutral fact, and Platform truth atomically."""
    client, database = mongo_db
    tenant_id, suffix = "tenant-platform", uuid4().hex
    session = client.start_session()
    session.start_transaction()
    try:
        command = _command(tenant_id, "PLATFORM", suffix)
        attempt_id = _seed_attempt(command, database, session, suffix)
        _apply_terminal_observation(tenant_id, attempt_id, database, session, suffix)
        result = _runtime(tenant_id, attempt_id, database, session, suffix)
        assert isinstance(command.source_authority, PlatformBillingCommandSource)
        assert isinstance(result, PlatformBillingFinancialExecutionTruth)
        assert result.platform_invoice_id == command.source_authority.platform_invoice_id
        fact = FinancialExecutionFactRegistry.get_by_attempt(tenant_id, attempt_id, database[FACT_COLLECTION], session=session)
        truth = PlatformBillingFinancialExecutionTruthRegistry.get(
            tenant_id, f"platform-truth-{command.source_authority.execution_request_id}",
            database[PLATFORM_TRUTH_COLLECTION], session=session,
        )
        assert fact is not None
        assert truth.source_execution_fact_id == fact.execution_fact_id
        assert truth.provider == command.provider_name
        assert database[FACT_COLLECTION].count_documents({}) == 0
        assert database[PLATFORM_TRUTH_COLLECTION].count_documents({}) == 0
        session.commit_transaction()
    finally:
        session.end_session()
    assert database[FACT_COLLECTION].count_documents({}) == 1
    assert database[PLATFORM_TRUTH_COLLECTION].count_documents({}) == 1
    assert database[AP_TRUTH_COLLECTION].count_documents({}) == 0


def test_ap_projection_failure_rolls_back_fact_observation_attempt_and_truth(mongo_db: Any) -> None:
    """Certify AP child failure cannot partially commit neutral execution evidence."""
    client, database = mongo_db
    tenant_id, suffix = "tenant-ap-failure", uuid4().hex
    command, attempt_id = _prepare_terminal_case(database, tenant_id, "AP", suffix, client)
    source = command.source_authority
    assert isinstance(source, AccountsPayableCommandSource)
    conflict = FinancialExecutionTruth(
        command.execution_command_id, tenant_id, source.payable_id, source.release_authorization_id,
        command.provider_name, f"provider-execution-{suffix}", FinancialExecutionStatus.EXECUTED,
        command.amount_minor + 1, command.currency, EXECUTED_AT, command.payment_destination_reference,
        f"execution-evidence-{suffix}", command.fingerprint, "d" * 128, command.created_at,
    )
    FinancialExecutionTruthRegistry.create(conflict, command.idempotency_key, database[AP_TRUTH_COLLECTION])
    session = client.start_session()
    session.start_transaction()
    try:
        _apply_terminal_observation(tenant_id, attempt_id, database, session, suffix)
        with pytest.raises(RuntimeError):
            _runtime(tenant_id, attempt_id, database, session, suffix)
        session.abort_transaction()
    finally:
        session.end_session()
    assert database[FACT_COLLECTION].count_documents({}) == 0
    assert database[OBSERVATION_COLLECTION].count_documents({}) == 0
    assert database[ATTEMPT_COLLECTION].find_one({"execution_attempt_id": attempt_id})["state"] == "PREPARED"
    assert database[AP_TRUTH_COLLECTION].count_documents({}) == 1


def test_platform_projection_failure_rolls_back_fact_observation_attempt_and_truth(mongo_db: Any) -> None:
    """Certify Platform child failure cannot partially commit neutral execution evidence."""
    client, database = mongo_db
    tenant_id, suffix = "tenant-platform-failure", uuid4().hex
    command, attempt_id = _prepare_terminal_case(database, tenant_id, "PLATFORM", suffix, client)
    fake_fact = FinancialExecutionFact(
        FinancialExecutionFact.deterministic_id(tenant_id, f"other-{suffix}"), tenant_id,
        command.execution_command_id, command.fingerprint, f"other-{suffix}", command.provider_name,
        f"provider-execution-{suffix}", FinancialExecutionStatus.EXECUTED, command.amount_minor,
        command.currency, EXECUTED_AT, command.payment_destination_reference, f"other-evidence-{suffix}",
        "e" * 128, command.created_at,
    )
    conflict = PlatformBillingFinancialExecutionTruth.from_execution_fact(fake_fact, command)
    PlatformBillingFinancialExecutionTruthRegistry.create(conflict, database[PLATFORM_TRUTH_COLLECTION])
    session = client.start_session()
    session.start_transaction()
    try:
        _apply_terminal_observation(tenant_id, attempt_id, database, session, suffix)
        with pytest.raises(RuntimeError):
            _runtime(tenant_id, attempt_id, database, session, suffix)
        session.abort_transaction()
    finally:
        session.end_session()
    assert database[FACT_COLLECTION].count_documents({}) == 0
    assert database[OBSERVATION_COLLECTION].count_documents({}) == 0
    assert database[ATTEMPT_COLLECTION].find_one({"execution_attempt_id": attempt_id})["state"] == "PREPARED"
    assert database[PLATFORM_TRUTH_COLLECTION].count_documents({}) == 1


@pytest.mark.parametrize("family", ["AP", "PLATFORM"])
def test_committed_reentry_is_exact_replay_without_second_truth(mongo_db: Any, family: str) -> None:
    """Certify committed AP and Platform reentry preserves one fact and one family truth."""
    client, database = mongo_db
    tenant_id, suffix = f"tenant-{family.lower()}-reentry", uuid4().hex
    session = client.start_session()
    session.start_transaction()
    command = _command(tenant_id, family, suffix)
    attempt_id = _seed_attempt(command, database, session, suffix)
    _apply_terminal_observation(tenant_id, attempt_id, database, session, suffix)
    _runtime(tenant_id, attempt_id, database, session, suffix)
    session.commit_transaction()
    session.end_session()
    session = client.start_session()
    session.start_transaction()
    try:
        replay = _runtime(tenant_id, attempt_id, database, session, suffix)
        assert replay is not None
        assert database[FACT_COLLECTION].count_documents({}, session=session) == 1
        assert database[AP_TRUTH_COLLECTION].count_documents({}, session=session) + database[PLATFORM_TRUTH_COLLECTION].count_documents({}, session=session) == 1
        session.commit_transaction()
    finally:
        session.end_session()
    assert database[FACT_COLLECTION].count_documents({}) == 1
    assert database[AP_TRUTH_COLLECTION].count_documents({}) + database[PLATFORM_TRUTH_COLLECTION].count_documents({}) == 1


def test_cross_tenant_reads_and_runtime_are_isolated(mongo_db: Any) -> None:
    """Certify wrong-tenant command, fact, observation, and truth access cannot cross the boundary."""
    client, database = mongo_db
    tenant_id, suffix = "tenant-isolated", uuid4().hex
    session = client.start_session()
    session.start_transaction()
    command = _command(tenant_id, "AP", suffix)
    attempt_id = _seed_attempt(command, database, session, suffix)
    _apply_terminal_observation(tenant_id, attempt_id, database, session, suffix)
    _runtime(tenant_id, attempt_id, database, session, suffix)
    session.commit_transaction()
    session.end_session()
    with pytest.raises(Exception):
        FinancialExecutionCommandRegistry.get("other-tenant", command.execution_command_id, database[COMMAND_COLLECTION])
    assert FinancialExecutionFactRegistry.get("other-tenant", FinancialExecutionFact.deterministic_id(tenant_id, attempt_id), database[FACT_COLLECTION]) is None
    with pytest.raises(Exception):
        FinancialExecutionAttemptRegistry.get("other-tenant", attempt_id, database[ATTEMPT_COLLECTION])
    assert database[OBSERVATION_COLLECTION].count_documents({"tenant_id": "other-tenant"}) == 0
    assert FinancialExecutionTruthRegistry.get("other-tenant", command.execution_command_id, database[AP_TRUTH_COLLECTION]) is None


def test_cross_registry_concurrent_runtime_race_has_one_fact_and_truth(mongo_db: Any) -> None:
    """Certify independent caller transactions leave one canonical AP fact and truth."""
    client, database = mongo_db
    tenant_id, suffix = "tenant-race", uuid4().hex
    session = client.start_session()
    session.start_transaction()
    command = _command(tenant_id, "AP", suffix)
    attempt_id = _seed_attempt(command, database, session, suffix)
    _apply_terminal_observation(tenant_id, attempt_id, database, session, suffix)
    session.commit_transaction()
    session.end_session()
    barrier = Barrier(2)

    def invoke() -> str:
        caller = client.start_session()
        try:
            caller.start_transaction()
            barrier.wait(timeout=15)
            _runtime(tenant_id, attempt_id, database, caller, suffix)
            caller.commit_transaction()
            return "COMMITTED"
        except Exception:
            try:
                caller.abort_transaction()
            except Exception:
                pass
            return "ABORTED"
        finally:
            caller.end_session()

    with ThreadPoolExecutor(max_workers=2) as executor:
        outcomes = list(executor.map(lambda _: invoke(), range(2)))
    assert "COMMITTED" in outcomes
    assert database[FACT_COLLECTION].count_documents({"tenant_id": tenant_id}) == 1
    assert database[AP_TRUTH_COLLECTION].count_documents({"tenant_id": tenant_id}) == 1
    assert database[PLATFORM_TRUTH_COLLECTION].count_documents({"tenant_id": tenant_id}) == 0


def test_ap_truth_live_race_uses_caller_fresh_retry(mongo_db: Any) -> None:
    """Certify AP truth loser propagation and whole-transaction caller retry."""
    client, database = mongo_db
    tenant_id, suffix = "tenant-ap-truth-race", uuid4().hex
    command, attempt_id, fact = _seed_terminal_fact(database, tenant_id, "AP", suffix, client)
    source = command.source_authority
    assert isinstance(source, AccountsPayableCommandSource)
    truth = FinancialExecutionTruth(
        execution_truth_id=command.execution_command_id,
        tenant_id=command.tenant_id,
        payable_id=source.payable_id,
        release_authorization_id=source.release_authorization_id,
        provider=fact.provider,
        provider_execution_reference=fact.provider_execution_reference,
        execution_status=fact.execution_status,
        executed_amount_minor=command.amount_minor,
        currency=command.currency,
        executed_at=fact.executed_at,
        payment_destination_reference=command.payment_destination_reference,
        provider_evidence_reference=fact.provider_evidence_reference,
        execution_command_fingerprint=command.fingerprint,
        execution_evidence_fingerprint=fact.execution_evidence_fingerprint,
        created_at=command.created_at,
    )
    barrier = Barrier(2)
    winner_committed = Event()

    def invoke(role: str) -> str:
        caller = client.start_session()
        caller_closed = False
        try:
            caller.start_transaction()
            assert FinancialExecutionTruthRegistry.get_by_idempotency_key(
                tenant_id, source.payable_id, command.idempotency_key,
                database[AP_TRUTH_COLLECTION], session=caller,
            ) is None
            barrier.wait(timeout=15)
            if role == "loser":
                assert winner_committed.wait(timeout=15)
            result = FinancialExecutionTruthRegistry.create(
                truth, command.idempotency_key, database[AP_TRUTH_COLLECTION], session=caller
            )
            caller.commit_transaction()
            return "COMMITTED" if result.execution_truth == truth else "DIVERGENT"
        except Exception:
            if role != "loser":
                raise
            try:
                caller.abort_transaction()
            finally:
                caller.end_session()
                caller_closed = True
            retry = client.start_session()
            try:
                retry.start_transaction()
                replay = FinancialExecutionTruthRegistry.create(
                    truth, command.idempotency_key, database[AP_TRUTH_COLLECTION], session=retry
                )
                assert replay.execution_truth == truth
                retry.commit_transaction()
                return "RETRIED"
            finally:
                retry.end_session()
        finally:
            if role == "winner":
                winner_committed.set()
            if not caller_closed:
                caller.end_session()

    with ThreadPoolExecutor(max_workers=2) as executor:
        winner = executor.submit(invoke, "winner")
        loser = executor.submit(invoke, "loser")
        outcomes = [winner.result(timeout=30), loser.result(timeout=30)]
    assert outcomes[0] == "COMMITTED"
    assert outcomes[1] == "RETRIED"
    assert database[FACT_COLLECTION].count_documents({"tenant_id": tenant_id}) == 1
    assert database[AP_TRUTH_COLLECTION].count_documents({"tenant_id": tenant_id}) == 1
    assert database[AP_TRUTH_COLLECTION].find_one({"tenant_id": tenant_id})["provider"] == "PAYSHAP"
    assert attempt_id


def test_platform_truth_live_race_uses_caller_fresh_retry(mongo_db: Any) -> None:
    """Certify Platform truth loser propagation and whole-transaction caller retry."""
    client, database = mongo_db
    tenant_id, suffix = "tenant-platform-truth-race", uuid4().hex
    command, attempt_id, fact = _seed_terminal_fact(database, tenant_id, "PLATFORM", suffix, client)
    truth = PlatformBillingFinancialExecutionTruth.from_execution_fact(fact, command)
    barrier = Barrier(2)
    winner_committed = Event()

    def invoke(role: str) -> str:
        caller = client.start_session()
        caller_closed = False
        try:
            caller.start_transaction()
            try:
                PlatformBillingFinancialExecutionTruthRegistry.get(
                    tenant_id, truth.execution_truth_id, database[PLATFORM_TRUTH_COLLECTION], session=caller
                )
            except PlatformBillingFinancialExecutionTruthNotFoundError:
                pass
            else:
                raise AssertionError("platform truth must be absent before race")
            barrier.wait(timeout=15)
            if role == "loser":
                assert winner_committed.wait(timeout=15)
            result = bridge_financial_execution_fact_to_platform(
                tenant_id, fact.execution_fact_id,
                fact_collection=database[FACT_COLLECTION],
                command_collection=database[COMMAND_COLLECTION],
                platform_truth_collection=database[PLATFORM_TRUTH_COLLECTION],
                session=caller,
            )
            caller.commit_transaction()
            return "COMMITTED" if result == truth else "DIVERGENT"
        except Exception:
            if role != "loser":
                raise
            try:
                caller.abort_transaction()
            finally:
                caller.end_session()
                caller_closed = True
            retry = client.start_session()
            try:
                retry.start_transaction()
                replay = bridge_financial_execution_fact_to_platform(
                    tenant_id, fact.execution_fact_id,
                    fact_collection=database[FACT_COLLECTION],
                    command_collection=database[COMMAND_COLLECTION],
                    platform_truth_collection=database[PLATFORM_TRUTH_COLLECTION],
                    session=retry,
                )
                assert replay == truth
                retry.commit_transaction()
                return "RETRIED"
            finally:
                retry.end_session()
        finally:
            if role == "winner":
                winner_committed.set()
            if not caller_closed:
                caller.end_session()

    with ThreadPoolExecutor(max_workers=2) as executor:
        winner = executor.submit(invoke, "winner")
        loser = executor.submit(invoke, "loser")
        outcomes = [winner.result(timeout=30), loser.result(timeout=30)]
    assert outcomes[0] == "COMMITTED"
    assert outcomes[1] == "RETRIED"
    assert database[FACT_COLLECTION].count_documents({"tenant_id": tenant_id}) == 1
    assert database[PLATFORM_TRUTH_COLLECTION].count_documents({"tenant_id": tenant_id}) == 1
    assert database[PLATFORM_TRUTH_COLLECTION].find_one({"tenant_id": tenant_id})["provider"] == "PAYSHAP"
    assert attempt_id


# ARTIFACT: test_financial_execution_runtime_transaction_mongo.py
# VERSION: v1.1.0-M11-P5-R2E-R4-R3
# AUTHORITY BOUNDARY: live six-collection transaction evidence only.
# TENANT POSTURE: isolated UUID database and exact tenant-scoped queries.
# FAIL-CLOSED POSTURE: host or transaction failure prevents certification; no skip is success.
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS production registries and orchestrator exclusively.
# END OF WILSY OS SOVEREIGN ARTIFACT
