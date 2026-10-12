"""Dedicated L8-8H6 Legal notification recipient-binding command certificate.

TITLE: Legal Notification Recipient Binding Command API Unit Certificate
VERSION: v1.0.0-L8-8H6-NOTIFICATION-RECIPIENT-BINDING-COMMAND-CERT
AUTHORITY: Wilsy OS Core Governance / API composition verification only.
EPITOME: Certifies exact Partner/Attorney recipient-binding command dependency,
         forbidden transport authority, server-owned authorization chronology,
         bounded create/revoke/supersede composition, HTTP error projection and
         API-owned transaction rollback without creating contact or delivery truth.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tests/unit/test_legal_notification_recipient_binding_command_router.py
COLLABORATION / OWNERSHIP: L8-8H owns recipient binding/lifecycle authority;
                            tenant IAM owns actor authorization; this certificate
                            verifies only the Python HTTP/transaction composition.
CERTIFICATION / UPDATE DATE: 2026-10-12
CHANGELOG: v1.0.0 establishes dedicated adversarial L8-8H6 command admission proof.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2.
SECURITY / PRIVACY POSTURE: Bodies contain opaque IDs and lifecycle times only;
                             email, phone, address, provider, channel and message
                             authority are explicitly rejected.
TENANT BOUNDARY: Tenant and actor identity are server-derived from the exact
                 authenticated TenantAuthorizationContext.
AUTHORITY BOUNDARY: Actor administration authority != recipient eligibility !=
                    contact authority != transport/delivery authority.
TRANSACTION BOUNDARY: Production API owns start/commit/abort; child registries
                      receive the already-active transaction only.
FINANCIAL AUTHORITY BOUNDARY: None; Kennel EOS remains exclusive.
FAIL-CLOSED DECLARATION: Extra authority, stale recipient, absence, ambiguity,
                         replay conflict, persistence outage and failed transactions reject.
"""
from __future__ import annotations

import asyncio
from datetime import datetime, timedelta, timezone
from types import SimpleNamespace
from typing import Any

import pytest
from pydantic import ValidationError

import tools.eos.api.legal_operations_command_router as command_api
from tools.eos.api.tenant_authorization_http import TenantAuthorizationContext
from tools.eos.auth.identity import SovereignIdentity
from tools.eos.auth.principal_status import PrincipalStatus
from tools.eos.auth.tenant_authorization import (
    TenantAuthorizationDecision,
    TenantAuthorizationReason,
)
from tools.eos.legal_operations.domain.legal_notification_recipient_binding import (
    LegalNotificationEvent,
    LegalNotificationRecipientBinding,
)


TENANT = "tenant-l8h6"
ACTOR = "principal-partner-l8h6"
RECIPIENT = "principal-recipient-l8h6"
MATTER = "matter-l8h6"
AUTH_AT = datetime(2026, 10, 12, 8, 0, tzinfo=timezone.utc)
EFFECTIVE = AUTH_AT + timedelta(hours=1)


class Session:
    """API transaction witness."""

    def __init__(self) -> None:
        self.in_transaction = False
        self.events: list[str] = []

    def start_transaction(self) -> None:
        self.events.append("start")
        self.in_transaction = True

    def commit_transaction(self) -> None:
        self.events.append("commit")
        self.in_transaction = False

    def abort_transaction(self) -> None:
        self.events.append("abort")
        self.in_transaction = False

    def __enter__(self) -> "Session":
        return self

    def __exit__(self, *_args: object) -> None:
        self.events.append("end")


class Client:
    """API client-session witness."""

    def __init__(self) -> None:
        self.session = Session()

    def start_session(self) -> Session:
        return self.session


class Database:
    """Minimal database seam used by registry constructors."""

    def __init__(self) -> None:
        self.requested: list[str] = []

    def get_collection(self, name: str) -> Any:
        self.requested.append(name)
        return SimpleNamespace(name=name)


class RecordingBindingRegistry:
    """Capture binding writes without replacing domain authority."""

    def __init__(self) -> None:
        self.values: list[LegalNotificationRecipientBinding] = []

    def create_or_replay(
        self,
        value: LegalNotificationRecipientBinding,
        *,
        session: Any,
    ) -> LegalNotificationRecipientBinding:
        assert getattr(session, "in_transaction", True) is True
        self.values.append(value)
        return value


class RecordingLifecycleRegistry:
    """Capture lifecycle writes."""

    def __init__(self) -> None:
        self.values: list[Any] = []

    def create_or_replay(self, value: Any, *, session: Any) -> Any:
        assert getattr(session, "in_transaction", True) is True
        self.values.append(value)
        return value


def context(
    *,
    business_role: str = "tenant_legal_partner",
    authorization_role: str = "LEGAL_PARTNER",
) -> TenantAuthorizationContext:
    """Return server-authenticated recipient-binding administrator context."""

    identity = SovereignIdentity(
        identity_id=ACTOR,
        tenant_id=TENANT,
        username="partner",
        email="partner@example.test",
        auth_method="TEST",
        status=PrincipalStatus.ACTIVE,
    )
    decision = TenantAuthorizationDecision(
        True,
        TenantAuthorizationReason.AUTHORIZED,
        business_role,
        authorization_role,
    )
    return TenantAuthorizationContext(identity, TENANT, decision)


def create_command(**overrides: object) -> command_api.RecipientBindingCreateCommand:
    values: dict[str, Any] = {
        "binding_id": "binding-l8h6-1",
        "case_matter_id": MATTER,
        "recipient_principal_id": RECIPIENT,
        "effective_from": EFFECTIVE,
        "effective_until": None,
    }
    values.update(overrides)
    return command_api.RecipientBindingCreateCommand(**values)


def revoke_command(**overrides: object) -> command_api.RecipientBindingRevokeCommand:
    values: dict[str, Any] = {
        "lifecycle_event_id": "revoke-l8h6-1",
        "case_matter_id": MATTER,
        "target_binding_id": "binding-l8h6-1",
        "effective_at": EFFECTIVE + timedelta(hours=1),
    }
    values.update(overrides)
    return command_api.RecipientBindingRevokeCommand(**values)


def supersede_command(
    **overrides: object,
) -> command_api.RecipientBindingSupersedeCommand:
    values: dict[str, Any] = {
        "binding_id": "binding-l8h6-2",
        "case_matter_id": MATTER,
        "recipient_principal_id": "principal-recipient-l8h6-2",
        "effective_from": EFFECTIVE + timedelta(hours=2),
        "effective_until": None,
        "lifecycle_event_id": "supersede-l8h6-1",
        "target_binding_id": "binding-l8h6-1",
    }
    values.update(overrides)
    return command_api.RecipientBindingSupersedeCommand(**values)


def target_binding() -> LegalNotificationRecipientBinding:
    return LegalNotificationRecipientBinding(
        tenant_id=TENANT,
        binding_id="binding-l8h6-1",
        case_matter_id=MATTER,
        event=LegalNotificationEvent.RETURN_READY,
        recipient_principal_id=RECIPIENT,
        effective_from=EFFECTIVE,
        effective_until=None,
        created_by_principal_id=ACTOR,
        created_at=AUTH_AT,
    )


def test_command_models_reject_transport_authority_and_contact_fields() -> None:
    """Bodies cannot manufacture tenant, actor, IAM, chronology or contact truth."""

    assert set(create_command().model_dump()) == {
        "binding_id",
        "case_matter_id",
        "recipient_principal_id",
        "effective_from",
        "effective_until",
    }
    assert set(revoke_command().model_dump()) == {
        "lifecycle_event_id",
        "case_matter_id",
        "target_binding_id",
        "effective_at",
    }
    assert set(supersede_command().model_dump()) == {
        "binding_id",
        "case_matter_id",
        "recipient_principal_id",
        "effective_from",
        "effective_until",
        "lifecycle_event_id",
        "target_binding_id",
    }

    forbidden: dict[str, object] = {
        "tenant_id": TENANT,
        "actor_principal_id": ACTOR,
        "created_by_principal_id": ACTOR,
        "created_at": AUTH_AT,
        "recorded_at": AUTH_AT,
        "permission": "forged",
        "operation": "forged",
        "role": "LEGAL_PARTNER",
        "email": "forged@example.invalid",
        "phone": "+27000000000",
        "address": "forged",
        "channel": "EMAIL",
        "provider": "forged",
        "message": "forged",
    }
    for field, value in forbidden.items():
        with pytest.raises(ValidationError):
            create_command(**{field: value})
        with pytest.raises(ValidationError):
            revoke_command(**{field: value})
        with pytest.raises(ValidationError):
            supersede_command(**{field: value})


def test_dependency_is_exact_recipient_binding_permission_operation() -> None:
    dependency = command_api._RECIPIENT_BINDING
    assert command_api._RECIPIENT_BINDING_PERMISSION == (
        "legal_operations:notification_recipient_binding:write"
    )
    assert command_api._RECIPIENT_BINDING_OPERATION == (
        "legal_notification_recipient_binding_write"
    )
    assert dependency.permission_id == command_api._RECIPIENT_BINDING_PERMISSION
    assert dependency.operation == command_api._RECIPIENT_BINDING_OPERATION


def test_create_uses_server_tenant_actor_and_authorization_time(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Create derives scope/actor/created_at exclusively from server authority."""

    session = SimpleNamespace(in_transaction=True)
    database = Database()
    binding_registry = RecordingBindingRegistry()
    lifecycle_registry = RecordingLifecycleRegistry()
    matter = SimpleNamespace(case_matter_id=MATTER, fingerprint="a" * 128)
    evidence_calls: list[dict[str, Any]] = []

    monkeypatch.setattr(
        command_api,
        "_transaction",
        lambda callback: callback(session, database),
    )
    monkeypatch.setattr(
        command_api,
        "_recipient_command_sources",
        lambda *_args, **_kwargs: (
            matter,
            binding_registry,
            lifecycle_registry,
        ),
    )

    def evidence(**kwargs: Any) -> Any:
        evidence_calls.append(kwargs)
        return SimpleNamespace(authorized_at=AUTH_AT)

    monkeypatch.setattr(
        command_api,
        "_recipient_authorization_evidence",
        evidence,
    )

    result = asyncio.run(
        command_api.create_notification_recipient_binding(
            create_command(),
            context(),
            object(),
            object(),
            object(),
        )
    )

    assert len(binding_registry.values) == 1
    value = binding_registry.values[0]
    assert value.tenant_id == TENANT
    assert value.created_by_principal_id == ACTOR
    assert value.recipient_principal_id == RECIPIENT
    assert value.created_at == AUTH_AT
    assert value.effective_from == EFFECTIVE
    assert evidence_calls[0]["context"].tenant_id == TENANT
    assert evidence_calls[0]["idempotency_key"] == (
        "legal-notification-recipient-binding:create:binding-l8h6-1"
    )
    assert result["data"]["created_at"] == "2026-10-12T08:00:00.000000Z"


def test_revoke_and_supersede_preserve_target_and_use_server_time(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Termination evidence is append-only and server-chronologized."""

    session = SimpleNamespace(in_transaction=True)
    database = Database()
    target = target_binding()
    lifecycle_registry = RecordingLifecycleRegistry()
    binding_registry = RecordingBindingRegistry()
    matter = SimpleNamespace(case_matter_id=MATTER, fingerprint="b" * 128)

    monkeypatch.setattr(
        command_api,
        "_transaction",
        lambda callback: callback(session, database),
    )
    monkeypatch.setattr(
        command_api,
        "_binding_by_id",
        lambda *_args, **_kwargs: target,
    )
    monkeypatch.setattr(
        command_api,
        "_recipient_authorization_evidence",
        lambda **_kwargs: SimpleNamespace(authorized_at=AUTH_AT),
    )
    monkeypatch.setattr(
        command_api,
        "LegalNotificationRecipientBindingRegistry",
        lambda _collection: binding_registry,
    )
    monkeypatch.setattr(
        command_api,
        "LegalNotificationRecipientBindingLifecycleRegistry",
        lambda _collection: lifecycle_registry,
    )

    revoked = asyncio.run(
        command_api.revoke_notification_recipient_binding(
            revoke_command(),
            context(),
            object(),
            object(),
            object(),
        )
    )
    assert len(lifecycle_registry.values) == 1
    revocation = lifecycle_registry.values[0]
    assert revocation.target_binding_id == target.binding_id
    assert revocation.target_binding_fingerprint == target.fingerprint
    assert revocation.created_by_principal_id == ACTOR
    assert revocation.created_at == AUTH_AT
    assert target.to_dict() == target_binding().to_dict()
    assert revoked["data"]["target_binding_id"] == target.binding_id

    successor_registry = RecordingBindingRegistry()
    successor_lifecycle = RecordingLifecycleRegistry()
    monkeypatch.setattr(
        command_api,
        "_recipient_command_sources",
        lambda *_args, **_kwargs: (
            matter,
            successor_registry,
            successor_lifecycle,
        ),
    )

    superseded = asyncio.run(
        command_api.supersede_notification_recipient_binding(
            supersede_command(),
            context(),
            object(),
            object(),
            object(),
        )
    )
    successor = successor_registry.values[0]
    change = successor_lifecycle.values[0]
    assert successor.created_at == AUTH_AT
    assert successor.created_by_principal_id == ACTOR
    assert change.target_binding_id == target.binding_id
    assert change.successor_binding_id == successor.binding_id
    assert change.successor_binding_fingerprint == successor.fingerprint
    assert change.created_at == AUTH_AT
    assert superseded["data"]["binding_id"] == successor.binding_id


@pytest.mark.parametrize(
    ("code", "status_code", "detail"),
    [
        (
            "L8_8H6_WHOLE_TRANSACTION_RETRY_REQUIRED",
            409,
            "LEGAL_OPERATIONS_RETRY_REQUIRED",
        ),
        (
            "L8_8H_REGISTRY_RETRY_TRANSACTION_REQUIRED",
            409,
            "LEGAL_OPERATIONS_RETRY_REQUIRED",
        ),
        (
            "L8_8H_REGISTRY_REPLAY_CONFLICT",
            409,
            "LEGAL_NOTIFICATION_RECIPIENT_BINDING_CONFLICT",
        ),
        (
            "LEGAL_NOTIFICATION_RECIPIENT_BINDING_AMBIGUOUS",
            409,
            "LEGAL_NOTIFICATION_RECIPIENT_BINDING_CONFLICT",
        ),
        (
            "LEGAL_NOTIFICATION_RECIPIENT_ADMIN_AUTHORIZATION_REQUIRED",
            403,
            "LEGAL_NOTIFICATION_RECIPIENT_AUTHORIZATION_REQUIRED",
        ),
        (
            "LEGAL_NOTIFICATION_RECIPIENT_BINDING_NOT_FOUND",
            404,
            "LEGAL_OPERATION_NOT_FOUND",
        ),
        (
            "LEGAL_NOTIFICATION_RECIPIENT_NOT_CURRENT",
            404,
            "LEGAL_OPERATION_NOT_FOUND",
        ),
        (
            "LEGAL_NOTIFICATION_RECIPIENT_AUTHORITY_UNAVAILABLE",
            503,
            "LEGAL_OPERATIONS_UNAVAILABLE",
        ),
        (
            "L8_8H_REGISTRY_PERSISTENCE_UNAVAILABLE",
            503,
            "LEGAL_OPERATIONS_UNAVAILABLE",
        ),
        (
            "L8_8H_BINDING_ID_INVALID",
            422,
            "LEGAL_OPERATIONS_COMMAND_INVALID",
        ),
    ],
)
def test_recipient_error_taxonomy_is_bounded(
    code: str,
    status_code: int,
    detail: str,
) -> None:
    error = command_api.CommandError(code)
    projected = command_api._http_error(error)
    assert projected.status_code == status_code
    assert projected.detail == detail


def test_create_failure_aborts_api_transaction(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Authority failure aborts the API transaction and never fabricates success."""

    client = Client()
    database = Database()
    monkeypatch.setattr(
        command_api,
        "_db_handles",
        lambda: (client, database),
    )

    def fail(*_args: Any, **_kwargs: Any) -> Any:
        raise command_api.CommandError(
            "LEGAL_NOTIFICATION_RECIPIENT_AUTHORITY_UNAVAILABLE"
        )

    monkeypatch.setattr(
        command_api,
        "_recipient_command_sources",
        fail,
    )

    with pytest.raises(command_api.HTTPException) as raised:
        asyncio.run(
            command_api.create_notification_recipient_binding(
                create_command(),
                context(),
                object(),
                object(),
                object(),
            )
        )

    assert raised.value.status_code == 503
    assert raised.value.detail == "LEGAL_OPERATIONS_UNAVAILABLE"
    assert client.session.events == ["start", "abort", "end"]


def test_response_contains_no_contact_transport_or_authorization_evidence(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    session = SimpleNamespace(in_transaction=True)
    registry = RecordingBindingRegistry()
    matter = SimpleNamespace(case_matter_id=MATTER, fingerprint="c" * 128)

    monkeypatch.setattr(
        command_api,
        "_transaction",
        lambda callback: callback(session, Database()),
    )
    monkeypatch.setattr(
        command_api,
        "_recipient_command_sources",
        lambda *_args, **_kwargs: (
            matter,
            registry,
            RecordingLifecycleRegistry(),
        ),
    )
    monkeypatch.setattr(
        command_api,
        "_recipient_authorization_evidence",
        lambda **_kwargs: SimpleNamespace(authorized_at=AUTH_AT),
    )

    result = asyncio.run(
        command_api.create_notification_recipient_binding(
            create_command(),
            context(),
            object(),
            object(),
            object(),
        )
    )
    projection = str(result).lower()
    for forbidden in (
        "email",
        "phone",
        "address",
        "channel",
        "provider",
        "message",
        "authorization_evidence",
        "permission",
        "authorization_role",
    ):
        assert forbidden not in projection


# ARTIFACT: test_legal_notification_recipient_binding_command_router.py
# VERSION: v1.0.0-L8-8H6-NOTIFICATION-RECIPIENT-BINDING-COMMAND-CERT
# AUTHORITY BOUNDARY: authenticated recipient-binding HTTP/transaction certificate only
# TENANT POSTURE: tenant/actor/authorization chronology are server-owned
# FAIL-CLOSED POSTURE: authority/body/scope/currentness/conflict/outage failures reject boundedly
# FINANCIAL EXECUTION AUTHORITY: none; Kennel EOS exclusively
# END OF WILSY OS SOVEREIGN ARTIFACT
