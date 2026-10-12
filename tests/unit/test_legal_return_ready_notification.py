"""Direct adversarial certificate for Legal return-ready notification intent.

TITLE: Legal Operations Return-Ready Notification Intent Direct Certificate
VERSION: v1.0.0-L8-8E-RETURN-READY-NOTIFICATION-INTENT-CERT
AUTHORITY: Wilsy OS Core Governance / Python EOS Legal Operations
EPITOME: Certify exact canonical ReturnOfService binding, deterministic
         integrity, strict hydration, corruption rejection and the explicit
         no-recipient/no-transport/no-lifecycle-mutation authority boundary.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tests/unit/test_legal_return_ready_notification.py
COLLABORATION / OWNERSHIP: Certificate only. P1 owns ReturnOfService truth;
                            L8-8E owns immutable RETURN_READY intent semantics.
CERTIFICATION / UPDATE DATE: 2026-10-12
CHANGELOG: 2026-10-12 v1.0.0-L8-8E-RETURN-READY-NOTIFICATION-INTENT-CERT
           establishes canonical source derivation, exact round trip,
           deterministic replay, pseudo-tenant/source corruption rejection,
           schema/fingerprint tamper rejection and authority firewalls.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2; ISO 27001.
SECURITY / PRIVACY POSTURE: Synthetic opaque identifiers and fingerprints only.
TENANT BOUNDARY: Notification tenant and Legal identities derive only from one
                 validated canonical ReturnOfService.
AUTHORITY BOUNDARY: Intent certificate only; no recipient/channel/provider,
                    transport, custody/service/return mutation, Court, invoice,
                    payment, execution or settlement authority.
FINANCIAL AUTHORITY BOUNDARY: Kennel EOS remains exclusive.
FAIL-CLOSED DECLARATION: Invalid source, scope, schema, chronology or integrity
                         rejects without coercion or fallback.
"""
from __future__ import annotations

from copy import deepcopy
from dataclasses import fields
from datetime import datetime, timedelta, timezone
import inspect

import pytest

import tools.eos.legal_operations.domain.legal_return_ready_notification as notification
from tools.eos.legal_operations.domain.legal_operations_lifecycle import (
    ReturnOfService,
    ServiceAttempt,
    ServiceAttemptState,
    ServiceExecution,
)
from tools.eos.legal_operations.domain.legal_return_ready_notification import (
    LegalReturnReadyNotification,
    LegalReturnReadyNotificationError,
    LegalReturnReadyNotificationEvent,
    LegalReturnReadyNotificationStatus,
    create_return_ready_notification,
)


BASE = datetime(2026, 10, 12, 5, 0, tzinfo=timezone.utc)
EVIDENCE_FP = "a" * 128


def canonical_return(
    *,
    tenant_id: str = "tenant-a",
    return_id: str = "return-1",
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
        evidence_fingerprint=EVIDENCE_FP,
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
        return_id=return_id,
        generated_at=BASE + timedelta(minutes=4),
    )


def test_derives_exact_canonical_return_scope_and_round_trips() -> None:
    source = canonical_return()

    value = create_return_ready_notification(
        return_of_service=source,
        notification_id="notification-1",
    )

    assert value.tenant_id == source.tenant_id
    assert value.instruction_id == source.instruction_id
    assert value.document_id == source.document_id
    assert value.return_id == source.return_id
    assert value.return_fingerprint == source.fingerprint
    assert value.occurred_at == source.generated_at
    assert value.event is LegalReturnReadyNotificationEvent.RETURN_READY
    assert value.status is LegalReturnReadyNotificationStatus.PENDING
    assert LegalReturnReadyNotification.from_dict(value.to_dict()) == value


def test_same_source_and_notification_id_are_deterministic() -> None:
    source = canonical_return()

    first = create_return_ready_notification(
        return_of_service=source,
        notification_id="notification-1",
    )
    second = create_return_ready_notification(
        return_of_service=source,
        notification_id="notification-1",
    )

    assert first == second
    assert first.fingerprint == second.fingerprint


def test_distinct_notification_identity_changes_fingerprint() -> None:
    source = canonical_return()

    first = create_return_ready_notification(
        return_of_service=source,
        notification_id="notification-1",
    )
    second = create_return_ready_notification(
        return_of_service=source,
        notification_id="notification-2",
    )

    assert first.fingerprint != second.fingerprint


def test_factory_rejects_noncanonical_source_type() -> None:
    with pytest.raises(
        LegalReturnReadyNotificationError,
        match="L8_8E_RETURN_OF_SERVICE_REQUIRED",
    ):
        create_return_ready_notification(
            return_of_service=object(),  # type: ignore[arg-type]
            notification_id="notification-1",
        )


def test_factory_revalidates_corrupted_return_source() -> None:
    source = canonical_return()
    object.__setattr__(source, "service_evidence_fingerprint", "bad")

    with pytest.raises(
        LegalReturnReadyNotificationError,
        match="L8_8E_RETURN_OF_SERVICE_INVALID",
    ):
        create_return_ready_notification(
            return_of_service=source,
            notification_id="notification-1",
        )


def test_factory_rejects_pseudo_tenant_even_on_tampered_source() -> None:
    source = canonical_return()
    object.__setattr__(source, "tenant_id", "root")

    with pytest.raises(
        LegalReturnReadyNotificationError,
        match="L8_8E_RETURN_OF_SERVICE_INVALID",
    ):
        create_return_ready_notification(
            return_of_service=source,
            notification_id="notification-1",
        )


@pytest.mark.parametrize(
    ("field", "value", "code"),
    [
        ("schema", "OTHER", "L8_8E_SCHEMA_INVALID"),
        (
            "notification_version",
            "v0",
            "L8_8E_VERSION_INVALID",
        ),
        (
            "fingerprint",
            "b" * 128,
            "L8_8E_FINGERPRINT_MISMATCH",
        ),
    ],
)
def test_hydration_rejects_schema_version_and_fingerprint_drift(
    field: str,
    value: object,
    code: str,
) -> None:
    payload = create_return_ready_notification(
        return_of_service=canonical_return(),
        notification_id="notification-1",
    ).to_dict()
    payload[field] = value

    with pytest.raises(LegalReturnReadyNotificationError, match=code):
        LegalReturnReadyNotification.from_dict(payload)


def test_hydration_rejects_unknown_fields_and_missing_fields() -> None:
    payload = create_return_ready_notification(
        return_of_service=canonical_return(),
        notification_id="notification-1",
    ).to_dict()

    injected = deepcopy(payload)
    injected["recipient_email"] = "person@example.invalid"
    with pytest.raises(
        LegalReturnReadyNotificationError,
        match="L8_8E_PAYLOAD_INVALID",
    ):
        LegalReturnReadyNotification.from_dict(injected)

    missing = deepcopy(payload)
    del missing["return_fingerprint"]
    with pytest.raises(
        LegalReturnReadyNotificationError,
        match="L8_8E_PAYLOAD_INVALID",
    ):
        LegalReturnReadyNotification.from_dict(missing)


def test_hydration_rejects_unknown_event_and_status() -> None:
    payload = create_return_ready_notification(
        return_of_service=canonical_return(),
        notification_id="notification-1",
    ).to_dict()

    invalid_event = deepcopy(payload)
    invalid_event["event"] = "PICKUP_READY"
    with pytest.raises(
        LegalReturnReadyNotificationError,
        match="L8_8E_PAYLOAD_INVALID",
    ):
        LegalReturnReadyNotification.from_dict(invalid_event)

    invalid_status = deepcopy(payload)
    invalid_status["status"] = "SENT"
    with pytest.raises(
        LegalReturnReadyNotificationError,
        match="L8_8E_PAYLOAD_INVALID",
    ):
        LegalReturnReadyNotification.from_dict(invalid_status)


def test_domain_contains_no_recipient_transport_or_delivery_state() -> None:
    field_names = {field.name for field in fields(LegalReturnReadyNotification)}
    forbidden = {
        "recipient",
        "recipient_id",
        "recipient_email",
        "phone",
        "channel",
        "provider",
        "provider_id",
        "message",
        "message_body",
        "template",
        "delivery_status",
        "attempt_count",
        "delivered_at",
        "sent_at",
        "transport_secret",
    }
    assert not field_names.intersection(forbidden)


def test_source_contains_no_network_or_downstream_mutation_authority() -> None:
    source = inspect.getsource(notification)

    forbidden = (
        "requests.",
        "httpx.",
        "aiohttp.",
        "smtplib",
        "twilio",
        ".transition_to(",
        "notification_send",
        "send_email",
        "send_sms",
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

    assert "RETURN_READY" in source
    assert "recipient" in source
    assert "Kennel EOS" in source


# ARTIFACT: test_legal_return_ready_notification.py
# VERSION: v1.0.0-L8-8E-RETURN-READY-NOTIFICATION-INTENT-CERT
# AUTHORITY BOUNDARY: immutable RETURN_READY intent certificate only
# TENANT POSTURE: every asserted identity derives from one canonical ReturnOfService
# DELIVERY POSTURE: no recipient/channel/provider/message/delivery lifecycle exists
# FAIL-CLOSED POSTURE: source/schema/event/status/fingerprint corruption rejects
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively
# END OF WILSY OS SOVEREIGN ARTIFACT
