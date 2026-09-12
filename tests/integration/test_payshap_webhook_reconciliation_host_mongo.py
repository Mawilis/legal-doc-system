"""Bounded Real-Mongo certificate for the PayShap reconciliation host seam.

TITLE: PayShap Host Reconciliation Real-Mongo Certificate
VERSION: v1.0.0-M11-HOST-PAYSHAP-RECONCILIATION
AUTHORITY: Wilsy OS Core Governance / Kennel EOS
EPITOME: Prove signed PayShap EXECUTED evidence reaches canonical
         reconciliation and family-specific execution truth in one caller transaction.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tests/integration/test_payshap_webhook_reconciliation_host_mongo.py
COLLABORATION / OWNERSHIP: Kennel EOS provider-ingress and execution certificate owner.
CERTIFICATION / UPDATE DATE: 2026-09-12
CHANGELOG: v1.0.0 certifies AP/Platform host composition, exact replay,
           caller rollback, and fail-closed correlation on the certified replica set.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2.
SECURITY / PRIVACY POSTURE: Synthetic opaque references and a fixed test secret only.
TENANT BOUNDARY: Signed tenant, command, attempt, observation, and truth rows correlate exactly.
AUTHORITY BOUNDARY: Host composition delegates reconciliation; no settlement authority.
FINANCIAL AUTHORITY BOUNDARY: EXECUTION != SETTLEMENT; no invoice or paid mutation.
"""
from __future__ import annotations

import hashlib
import hmac
import json
import os
from datetime import datetime, timezone
from typing import Any, Generator
from unittest.mock import Mock
from uuid import uuid4

import pytest
from pymongo import MongoClient
from pymongo.collection import Collection
import tools.eos.api.payshap_webhook_router as router_module

from tools.eos.api.payshap_webhook_router import (
    PayShapWebhookHostError,
    compose_authenticated_payshap_webhook,
)
from tools.eos.kennel.evidence.payshap_webhook_ingestion import PayShapWebhookError
from tools.eos.kennel.domain.financial_execution_command import (
    AccountsPayableCommandSource,
    FinancialExecutionCommand,
    PlatformBillingCommandSource,
)
from tools.eos.kennel.domain.financial_execution_lifecycle import (
    FinancialExecutionAttemptState,
)
from tools.eos.kennel.orchestration.financial_execution_attempt_issuance import (
    FinancialExecutionAttemptIssuance,
    issue_financial_execution_attempt,
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
from tools.eos.kennel.evidence.payshap_evidence_store import PayShapEvidenceRegistry


URI = "mongodb://127.0.0.1:27027/?replicaSet=wilsyVendorCertRS"
SECRET = "bounded-host-test-secret"
NOW = datetime(2026, 9, 12, 10, tzinfo=timezone.utc)


@pytest.fixture()
def runtime() -> Generator[dict[str, Any], None, None]:
    configured = os.environ.get("TEST_VENDOR_MONGO_URI")
    assert configured == URI, "TEST_VENDOR_MONGO_URI must select the certified replica set"
    client = MongoClient(configured, serverSelectionTimeoutMS=5000, retryWrites=True)
    hello = client.admin.command("hello")
    assert hello.get("setName") == "wilsyVendorCertRS"
    assert hello.get("isWritablePrimary") is True
    database = client[f"phrm_{uuid4().hex}"]
    collections = {
        "database": database,
        "client": client,
        "command_collection": database["kennel_financial_execution_commands"],
        "attempt_collection": database["kennel_financial_execution_attempts"],
        "observation_collection": database["kennel_financial_execution_provider_observations"],
        "fact_collection": database[FACT_COLLECTION],
        "ap_truth_collection": database["kennel_financial_execution_truth"],
        "platform_truth_collection": database["kennel_platform_billing_financial_execution_truth"],
        "payshap_collection": database["kennel_payshap_provider_evidence"],
    }
    FinancialExecutionCommandRegistry.ensure_indexes(collections["command_collection"])
    FinancialExecutionAttemptRegistry.ensure_indexes(collections["attempt_collection"])
    FinancialExecutionProviderObservationRegistry.ensure_indexes(collections["observation_collection"])
    FinancialExecutionFactRegistry.ensure_indexes(collections["fact_collection"])
    FinancialExecutionTruthRegistry.ensure_indexes(collections["ap_truth_collection"])
    from tools.eos.kennel.registry.platform_billing_financial_execution_truth_registry import (
        PlatformBillingFinancialExecutionTruthRegistry,
    )

    PlatformBillingFinancialExecutionTruthRegistry.ensure_indexes(collections["platform_truth_collection"])
    PayShapEvidenceRegistry.ensure_indexes(collections["payshap_collection"])
    try:
        yield collections
    finally:
        client.drop_database(database.name)
        client.close()


def _command(family: str, suffix: str) -> FinancialExecutionCommand:
    if family == "AP":
        source = AccountsPayableCommandSource(
            execution_request_id=f"request-{suffix}",
            execution_request_fingerprint="a" * 128,
            selection_decision_id=f"selection-{suffix}",
            selection_decision_fingerprint="b" * 128,
            payable_id=f"payable-{suffix}",
            release_authorization_id=f"release-{suffix}",
            authorized_provider_name="PAYSHAP",
        )
    else:
        source = PlatformBillingCommandSource(
            execution_request_id=f"request-{suffix}",
            execution_request_fingerprint="a" * 128,
            routing_decision_id=f"routing-{suffix}",
            routing_decision_fingerprint="b" * 128,
            platform_invoice_id=f"invoice-{suffix}",
            release_authorization_id=f"release-{suffix}",
            release_authorization_fingerprint="c" * 128,
            authorized_provider_name="PAYSHAP",
        )
    return FinancialExecutionCommand(
        tenant_id="tenant-host",
        execution_command_id=f"command-{suffix}",
        idempotency_key=f"key-{suffix}",
        amount_minor=1000,
        currency="ZAR",
        payment_destination_reference=f"destination-{suffix}",
        source_authority=source,
        provider_name="PAYSHAP",
        created_at=NOW,
    )


def _seed(data: dict[str, Any], family: str, suffix: str) -> tuple[FinancialExecutionCommand, str]:
    command = _command(family, suffix)
    attempt_id = f"attempt-{suffix}"
    with data["client"].start_session() as session:
        session.start_transaction()
        FinancialExecutionCommandRegistry.create(command, data["command_collection"], session=session)
        attempt = issue_financial_execution_attempt(
            command,
            FinancialExecutionAttemptIssuance(
                execution_attempt_id=attempt_id,
                provider_name="PAYSHAP",
                created_at=NOW,
                request_evidence_reference=f"request-evidence-{suffix}",
            ),
            command_collection=data["command_collection"],
            session=session,
        )
        FinancialExecutionAttemptRegistry.create(attempt, data["attempt_collection"], session=session)
        current = FinancialExecutionAttemptRegistry.get(
            "tenant-host", attempt_id, data["attempt_collection"], session=session
        )
        for target_state in (FinancialExecutionAttemptState.TRANSMITTED, FinancialExecutionAttemptState.ACCEPTED):
            target = current.transition_to(target_state)
            current = FinancialExecutionAttemptRegistry.transition(
                "tenant-host",
                attempt_id,
                current.state,
                current.fingerprint,
                target,
                data["attempt_collection"],
                session=session,
            )
        session.commit_transaction()
    return command, attempt_id


def _payload(command: FinancialExecutionCommand, suffix: str) -> dict[str, object]:
    return {
        "event_id": f"event-{suffix}",
        "reference": f"provider-request-{suffix}",
        "execution_command_id": command.execution_command_id,
        "status": "EXECUTED",
        "amount": "10.00",
        "currency": "ZAR",
        "tenant_id": "tenant-host",
        "provider_execution_reference": f"provider-execution-{suffix}",
        "provider_timestamp": NOW.isoformat(),
    }


def _signature(payload: dict[str, object]) -> str:
    canonical = json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=True)
    return hmac.new(SECRET.encode(), canonical.encode(), hashlib.sha256).hexdigest()


def _call(data: dict[str, Any], payload: dict[str, object], session: Any) -> Any:
    return compose_authenticated_payshap_webhook(
        payload,
        _signature(payload),
        SECRET,
        database=data["database"],
        session=session,
    )


@pytest.mark.parametrize("family", ("AP", "PLATFORM"))
def test_authenticated_executed_host_path_and_exact_replay(
    runtime: dict[str, Any], family: str
) -> None:
    command, attempt_id = _seed(runtime, family, family.lower())
    payload = _payload(command, family.lower())
    with runtime["client"].start_session() as session:
        session.start_transaction()
        first = _call(runtime, payload, session)
        session.commit_transaction()
    assert first.reconciliation_required is False
    assert runtime["attempt_collection"].find_one({"execution_attempt_id": attempt_id})["state"] == "CONFIRMED_EXECUTED"
    assert runtime["fact_collection"].count_documents({}) == 1
    truth_collection = runtime["ap_truth_collection"] if family == "AP" else runtime["platform_truth_collection"]
    assert truth_collection.count_documents({}) == 1
    with runtime["client"].start_session() as session:
        session.start_transaction()
        replay = _call(runtime, payload, session)
        session.commit_transaction()
    assert replay.replay is True
    assert runtime["fact_collection"].count_documents({}) == 1
    assert truth_collection.count_documents({}) == 1


def test_caller_abort_rolls_back_host_evidence_observation_cas_and_truth(
    runtime: dict[str, Any],
) -> None:
    command, attempt_id = _seed(runtime, "AP", "abort")
    payload = _payload(command, "abort")
    with runtime["client"].start_session() as session:
        session.start_transaction()
        _call(runtime, payload, session)
        session.abort_transaction()
    assert runtime["payshap_collection"].count_documents({}) == 0
    assert runtime["observation_collection"].count_documents({}) == 0
    assert runtime["fact_collection"].count_documents({}) == 0
    assert runtime["ap_truth_collection"].count_documents({}) == 0
    assert runtime["attempt_collection"].find_one({"execution_attempt_id": attempt_id})["state"] == "ACCEPTED"
    with runtime["client"].start_session() as session:
        session.start_transaction()
        retry = _call(runtime, payload, session)
        session.commit_transaction()
    assert retry.replay is False
    assert runtime["attempt_collection"].find_one({"execution_attempt_id": attempt_id})["state"] == "CONFIRMED_EXECUTED"
    assert runtime["fact_collection"].count_documents({}) == 1
    assert runtime["ap_truth_collection"].count_documents({}) == 1


def test_downstream_failure_rolls_back_every_host_child_write(
    runtime: dict[str, Any], monkeypatch: pytest.MonkeyPatch
) -> None:
    command, attempt_id = _seed(runtime, "AP", "failure")
    payload = _payload(command, "failure")
    monkeypatch.setattr(
        router_module,
        "reconcile_and_finalize_execution",
        Mock(side_effect=RuntimeError("bounded downstream failure")),
    )
    with runtime["client"].start_session() as session:
        session.start_transaction()
        with pytest.raises(RuntimeError, match="bounded downstream failure"):
            _call(runtime, payload, session)
        session.abort_transaction()
    assert runtime["payshap_collection"].count_documents({}) == 0
    assert runtime["observation_collection"].count_documents({}) == 0
    assert runtime["fact_collection"].count_documents({}) == 0
    assert runtime["ap_truth_collection"].count_documents({}) == 0
    assert runtime["attempt_collection"].find_one({"execution_attempt_id": attempt_id})["state"] == "ACCEPTED"


def test_missing_execution_reference_and_timestamp_fail_closed(
    runtime: dict[str, Any],
) -> None:
    command, _ = _seed(runtime, "AP", "missing")
    for field in ("provider_execution_reference", "provider_timestamp"):
        payload = _payload(command, "missing")
        payload.pop(field)
        with runtime["client"].start_session() as session:
            session.start_transaction()
            with pytest.raises(PayShapWebhookError, match="EXECUTION_EVIDENCE_INCOMPLETE"):
                _call(runtime, payload, session)
            session.abort_transaction()


def test_cross_tenant_and_ambiguous_attempts_fail_closed(runtime: dict[str, Any]) -> None:
    command, _ = _seed(runtime, "AP", "ambiguous")
    with runtime["client"].start_session() as session:
        session.start_transaction()
        other = issue_financial_execution_attempt(
            command,
            FinancialExecutionAttemptIssuance(
                execution_attempt_id="attempt-ambiguous-2",
                provider_name="PAYSHAP",
                created_at=NOW,
            ),
            command_collection=runtime["command_collection"],
            session=session,
        )
        FinancialExecutionAttemptRegistry.create(other, runtime["attempt_collection"], session=session)
        session.commit_transaction()
    payload = _payload(command, "ambiguous")
    with runtime["client"].start_session() as session:
        session.start_transaction()
        with pytest.raises(PayShapWebhookHostError, match="CORRELATION_NOT_UNIQUE"):
            _call(runtime, payload, session)
        session.abort_transaction()
    cross_tenant = dict(payload, tenant_id="tenant-other")
    with runtime["client"].start_session() as session:
        session.start_transaction()
        with pytest.raises(PayShapWebhookHostError, match="CORRELATION_NOT_UNIQUE"):
            _call(runtime, cross_tenant, session)
        session.abort_transaction()


# ARTIFACT: test_payshap_webhook_reconciliation_host_mongo.py
# VERSION: v1.0.0-M11-HOST-PAYSHAP-RECONCILIATION
# AUTHORITY BOUNDARY: bounded PayShap host composition certificate only.
# TENANT POSTURE: exact tenant and command/attempt correlation; bounded database cleanup.
# FAIL-CLOSED POSTURE: missing, ambiguous, and divergent host evidence rejects.
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively; EXECUTION != SETTLEMENT.
# END OF WILSY OS SOVEREIGN ARTIFACT
