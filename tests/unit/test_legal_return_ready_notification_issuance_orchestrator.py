"""Direct adversarial certificate for Legal return-ready notification issuance.

TITLE: Legal Operations Return-Ready Notification Issuance Direct Certificate
VERSION: v1.0.0-L8-8G-RETURN-READY-NOTIFICATION-ISSUANCE-CERT
AUTHORITY: Wilsy OS Core Governance / Python EOS Legal Operations
EPITOME: Certify active caller-transaction enforcement, exact P2 ReturnOfService
         resolution, L8-8E derivation, L8-8F replay, wrong-type/foreign/absent
         evidence rejection and explicit no-delivery/no-return-creation authority.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tests/unit/test_legal_return_ready_notification_issuance_orchestrator.py
COLLABORATION / OWNERSHIP: Certificate only. P1/P2 own ReturnOfService truth;
                            L8-8E owns intent semantics; L8-8F owns persistence;
                            L8-8G owns composition only.
CERTIFICATION / UPDATE DATE: 2026-10-12
CHANGELOG: 2026-10-12 v1.0.0-L8-8G-RETURN-READY-NOTIFICATION-ISSUANCE-CERT
           establishes exact source resolution, transaction gating, deterministic
           replay, source/type/scope rejection and source-code authority firewalls.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2; ISO 27001.
SECURITY / PRIVACY POSTURE: Synthetic opaque identifiers and fingerprints only.
TENANT BOUNDARY: Requested tenant must own the exact P2 return evidence identity.
AUTHORITY BOUNDARY: Issuance composition certificate only; no recipient/channel,
                    provider, transport, return generation, lifecycle, Court,
                    invoice, payment, execution or settlement authority.
FINANCIAL AUTHORITY BOUNDARY: Kennel EOS remains exclusive.
FAIL-CLOSED DECLARATION: Missing transaction, malformed/absent/wrong-type/foreign
                         source, invalid intent or persistence failure reject.
"""
from __future__ import annotations

from copy import deepcopy
from datetime import datetime, timedelta, timezone
import inspect
from typing import Any

import pytest

import tools.eos.legal_operations.orchestration.legal_return_ready_notification_issuance_orchestrator as issuance
from tools.eos.legal_operations.domain.legal_operations_lifecycle import (
    CaseMatter,
    ReturnOfService,
    ServiceAttempt,
    ServiceAttemptState,
    ServiceExecution,
)
from tools.eos.legal_operations.orchestration.legal_return_ready_notification_issuance_orchestrator import (
    LegalReturnReadyNotificationIssuanceError,
    issue_return_ready_notification,
)
from tools.eos.legal_operations.registry.legal_operations_lifecycle_registry import (
    LegalOperationsLifecycleRegistryError,
)


BASE = datetime(2026, 10, 12, 5, 0, tzinfo=timezone.utc)
FP = "a" * 128
EVIDENCE_ID = "b" * 128


class Session:
    in_transaction = True


class Collection:
    def __init__(self) -> None:
        self.rows: list[dict[str, object]] = []
        self.calls: list[tuple[str, object]] = []

    def find_one(
        self,
        query: dict[str, object],
        *,
        session: object = None,
    ) -> dict[str, object] | None:
        self.calls.append(("find_one", session))
        return next(
            (
                row
                for row in self.rows
                if all(row.get(key) == value for key, value in query.items())
            ),
            None,
        )

    def insert_one(
        self,
        row: dict[str, object],
        *,
        session: object = None,
    ) -> None:
        self.calls.append(("insert_one", session))
        self.rows.append(deepcopy(row))


def canonical_return(
    *,
    tenant_id: str = "tenant-a",
) -> ReturnOfService:
    allocated = ServiceAttempt(
        tenant_id=tenant_id,
        attempt_id="attempt-1",
        instruction_id="instruction-1",
        document_id="document-1",
        deputy_id="deputy-1",
        allocated_at=BASE,
        allocation_evidence_reference="allocation-1",
    )
    attempted = allocated.transition_to(
        ServiceAttemptState.ATTEMPTED,
        evidence_reference="attempt-1",
        occurred_at=BASE + timedelta(minutes=1),
    )
    completed = attempted.transition_to(
        ServiceAttemptState.COMPLETED,
        evidence_reference="service-evidence-1",
        evidence_fingerprint=FP,
        occurred_at=BASE + timedelta(minutes=2),
    )
    execution = ServiceExecution.from_attempt(
        attempt=completed,
        service_execution_id="execution-1",
        executed_at=BASE + timedelta(minutes=3),
    )
    return ReturnOfService.from_service_execution(
        instruction_id="instruction-1",
        service_execution=execution,
        return_id="return-1",
        generated_at=BASE + timedelta(minutes=4),
    )


def install_source(
    monkeypatch: pytest.MonkeyPatch,
    value: object,
) -> list[tuple[object, ...]]:
    calls: list[tuple[object, ...]] = []

    def get(
        tenant_id: str,
        evidence_identity: str,
        collection: object,
        *,
        session: object = None,
    ) -> object:
        calls.append((tenant_id, evidence_identity, collection, session))
        return value

    monkeypatch.setattr(
        issuance.LegalOperationsLifecycleRegistry,
        "get",
        staticmethod(get),
    )
    return calls


def issue(
    *,
    collection: Collection,
    session: object,
):
    return issue_return_ready_notification(
        tenant_id="tenant-a",
        return_evidence_identity=EVIDENCE_ID,
        notification_id="notification-1",
        lifecycle_collection=object(),
        notification_collection=collection,
        session=session,
    )


def test_issues_exact_return_ready_intent_and_replays(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    source = canonical_return()
    calls = install_source(monkeypatch, source)
    collection = Collection()
    session = Session()

    first = issue(collection=collection, session=session)
    replay = issue(collection=collection, session=session)

    assert first == replay
    assert first.tenant_id == source.tenant_id
    assert first.return_id == source.return_id
    assert first.return_fingerprint == source.fingerprint
    assert len(collection.rows) == 1
    assert len(calls) == 2
    assert all(call[0] == "tenant-a" for call in calls)
    assert all(call[1] == EVIDENCE_ID for call in calls)
    assert all(call[3] is session for call in calls)
    assert all(call_session is session for _, call_session in collection.calls)


def test_requires_active_transaction_before_p2_read(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    called = False

    def forbidden(*args: object, **kwargs: object) -> object:
        nonlocal called
        del args, kwargs
        called = True
        return canonical_return()

    monkeypatch.setattr(
        issuance.LegalOperationsLifecycleRegistry,
        "get",
        staticmethod(forbidden),
    )

    with pytest.raises(
        LegalReturnReadyNotificationIssuanceError,
        match="L8_8G_ACTIVE_TRANSACTION_REQUIRED",
    ):
        issue(collection=Collection(), session=None)

    assert called is False


def test_absent_or_corrupt_p2_return_rejects(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    def unavailable(*args: object, **kwargs: object) -> object:
        del args, kwargs
        raise LegalOperationsLifecycleRegistryError("missing")

    monkeypatch.setattr(
        issuance.LegalOperationsLifecycleRegistry,
        "get",
        staticmethod(unavailable),
    )

    with pytest.raises(
        LegalReturnReadyNotificationIssuanceError,
        match="L8_8G_RETURN_UNAVAILABLE",
    ):
        issue(collection=Collection(), session=Session())


def test_wrong_p2_entity_type_rejects(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    install_source(
        monkeypatch,
        CaseMatter(
            tenant_id="tenant-a",
            case_matter_id="matter-1",
            matter_reference="MAT-001",
            opened_at=BASE,
            evidence_reference="matter-registration-1",
        ),
    )

    with pytest.raises(
        LegalReturnReadyNotificationIssuanceError,
        match="L8_8G_RETURN_TYPE_INVALID",
    ):
        issue(collection=Collection(), session=Session())


def test_foreign_return_scope_rejects(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    install_source(monkeypatch, canonical_return(tenant_id="tenant-b"))

    with pytest.raises(
        LegalReturnReadyNotificationIssuanceError,
        match="L8_8G_RETURN_SCOPE_MISMATCH",
    ):
        issue(collection=Collection(), session=Session())


@pytest.mark.parametrize(
    ("field", "value", "code"),
    [
        ("tenant_id", "root", "L8_8G_TENANT_INVALID"),
        (
            "return_evidence_identity",
            "not-a-sha3",
            "L8_8G_RETURN_EVIDENCE_IDENTITY_INVALID",
        ),
        (
            "notification_id",
            " notification-1",
            "L8_8G_NOTIFICATION_ID_INVALID",
        ),
    ],
)
def test_malformed_routing_inputs_reject_before_p2_read(
    monkeypatch: pytest.MonkeyPatch,
    field: str,
    value: object,
    code: str,
) -> None:
    called = False

    def forbidden(*args: object, **kwargs: object) -> object:
        nonlocal called
        del args, kwargs
        called = True
        return canonical_return()

    monkeypatch.setattr(
        issuance.LegalOperationsLifecycleRegistry,
        "get",
        staticmethod(forbidden),
    )

    values: dict[str, Any] = {
        "tenant_id": "tenant-a",
        "return_evidence_identity": EVIDENCE_ID,
        "notification_id": "notification-1",
        "lifecycle_collection": object(),
        "notification_collection": Collection(),
        "session": Session(),
    }
    values[field] = value

    with pytest.raises(
        LegalReturnReadyNotificationIssuanceError,
        match=code,
    ):
        issue_return_ready_notification(**values)

    assert called is False


def test_corrupted_canonical_return_is_revalidated_and_rejected(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    source = canonical_return()
    object.__setattr__(source, "service_evidence_fingerprint", "bad")
    install_source(monkeypatch, source)

    with pytest.raises(
        LegalReturnReadyNotificationIssuanceError,
        match="L8_8G_NOTIFICATION_INVALID",
    ):
        issue(collection=Collection(), session=Session())


def test_source_contains_no_return_creation_or_delivery_authority() -> None:
    source = inspect.getsource(issuance)

    forbidden = (
        "ReturnOfService.from_service_execution(",
        "ServiceExecution.from_attempt(",
        ".transition_to(",
        "requests.",
        "httpx.",
        "aiohttp.",
        "smtplib",
        "twilio",
        "send_email",
        "send_sms",
        "notification_send",
        "court_file",
        "invoice_issue",
        "payment_execute",
        "settlement_execute",
        "start_transaction(",
        "commit_transaction(",
        "abort_transaction(",
    )
    for token in forbidden:
        assert token not in source

    assert "LegalOperationsLifecycleRegistry.get" in source
    assert "create_return_ready_notification" in source
    assert "LegalReturnReadyNotificationRegistry" in source
    assert "Kennel EOS" in source


# ARTIFACT: test_legal_return_ready_notification_issuance_orchestrator.py
# VERSION: v1.0.0-L8-8G-RETURN-READY-NOTIFICATION-ISSUANCE-CERT
# AUTHORITY BOUNDARY: exact P2 ReturnOfService -> L8-8E intent -> L8-8F persistence composition certificate only
# TENANT POSTURE: exact requested tenant must own the canonical P2 return evidence
# TRANSACTION POSTURE: active caller transaction required before P2 read or persistence
# DELIVERY POSTURE: no recipient/channel/provider/message/transport/delivery authority
# FAIL-CLOSED POSTURE: malformed/absent/wrong-type/foreign/corrupt source rejects
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively
# END OF WILSY OS SOVEREIGN ARTIFACT
