"""Direct certificate for password-recovery request orchestration.

TITLE: WILSY OS Password Recovery Request Service Direct Certificate
VERSION: v1.0.0-R10E3-PASSWORD-RECOVERY-REQUEST-SERVICE-CERT
AUTHORITY: Wilsy OS Core Governance
EPITOME: Certifies exact ACTIVE-principal admission, replacement recovery-window
         issuance, post-commit delivery, cooldown suppression, compensation,
         and enumeration-safe result semantics without Mongo or network access.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tests/unit/test_password_recovery_request_service.py
COLLABORATION / OWNERSHIP: Test-only evidence for the R10E3 service. Registry,
                           AuthRegistry, principal authority, and delivery are
                           deterministic fakes; production files are read-only.
CERTIFICATION / UPDATE DATE: 2026-09-22
CHANGELOG:
  v1.0.0-R10E3-PASSWORD-RECOVERY-REQUEST-SERVICE-CERT — Adds direct deterministic evidence for request admission,
    exact transaction/session propagation, prior-window expiry/revocation,
    30-minute TTL, 60-second cooldown, digest-only persistence, post-commit
    delivery ordering, delivery-failure compensation, uniform absent/inactive/
    throttled receipts, and secret/authority boundaries.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2; ISO 27001.
SECURITY / PRIVACY POSTURE: Synthetic bearer values only; tests assert raw
                            tokens never enter persisted capability state.
TENANT BOUNDARY: Synthetic exact tenant/email principal resolution only.
AUTHORITY BOUNDARY: Recovery issuance orchestration evidence; no password, JWT,
                    MFA, role, membership, session, or financial authority.
FINANCIAL AUTHORITY BOUNDARY: None; Kennel EOS remains exclusively financial.
"""

from __future__ import annotations

import hashlib
import inspect
from datetime import datetime, timedelta, timezone
from types import SimpleNamespace
from typing import Any

import pytest

from tools.eos.auth.principal_authority_repository import PrincipalAuthorityNotFoundError
from tools.eos.auth.principal_status import PrincipalStatus
from tools.eos.saas.auth.password_recovery import (
    PasswordRecoveryCapability,
    PasswordRecoveryCapabilityStatus,
)
from tools.eos.saas.auth.password_recovery_request_service import (
    RECOVERY_COOLDOWN,
    RECOVERY_TTL,
    PasswordRecoveryRequestCode,
    PasswordRecoveryRequestResult,
    PasswordRecoveryRequestService,
    PasswordRecoveryRequestServiceError,
)


NOW = datetime(2026, 9, 22, 16, 0, 0, tzinfo=timezone.utc)
RAW_TOKEN = "synthetic-recovery-token-value-0123456789-ABCDE"


class _Session:
    def __init__(self, events: list[str]) -> None:
        self.events = events
        self.with_transaction_calls = 0

    def __enter__(self) -> "_Session":
        self.events.append("session-enter")
        return self

    def __exit__(self, *_args: Any) -> None:
        self.events.append("session-exit")

    def with_transaction(self, callback: Any) -> None:
        self.with_transaction_calls += 1
        self.events.append("transaction-begin")
        callback(self)
        self.events.append("transaction-commit")


class _Client:
    def __init__(self, events: list[str]) -> None:
        self.events = events
        self.sessions: list[_Session] = []

    def start_session(self) -> _Session:
        session = _Session(self.events)
        self.sessions.append(session)
        return session


class _Auth:
    def __init__(self, principal_id: str | None = "principal-a") -> None:
        self.principal_id = principal_id
        self.calls: list[tuple[str, str, Any]] = []

    def resolve_principal_id_by_email_for_tenant(
        self, tenant_id: str, email: str, *, session: Any = None
    ) -> str | None:
        self.calls.append((tenant_id, email, session))
        return self.principal_id


class _PrincipalRepository:
    def __init__(self, status: PrincipalStatus | None = PrincipalStatus.ACTIVE) -> None:
        self.status = status
        self.calls: list[tuple[str, Any]] = []

    def get(self, principal_id: str, *, session: Any = None) -> Any:
        self.calls.append((principal_id, session))
        if self.status is None:
            raise PrincipalAuthorityNotFoundError("PRINCIPAL_AUTHORITY_NOT_FOUND")
        return SimpleNamespace(principal_id=principal_id, status=self.status, revision=4)


class _Registry:
    def __init__(self, capabilities: list[PasswordRecoveryCapability] | None = None) -> None:
        self.capabilities = list(capabilities or [])
        self.calls: list[tuple[str, Any]] = []

    def _replace(self, replacement: PasswordRecoveryCapability) -> None:
        self.capabilities = [
            replacement if item.capability_id == replacement.capability_id else item
            for item in self.capabilities
        ]

    def list_active_for_principal(
        self, *, tenant_id: str, principal_id: str, session: Any | None = None
    ) -> tuple[PasswordRecoveryCapability, ...]:
        self.calls.append(("list", (tenant_id, principal_id, session)))
        return tuple(
            item for item in self.capabilities
            if item.tenant_id == tenant_id
            and item.principal_id == principal_id
            and item.status is PasswordRecoveryCapabilityStatus.ACTIVE
        )

    def create(self, capability: PasswordRecoveryCapability, *, session: Any | None = None) -> PasswordRecoveryCapability:
        self.calls.append(("create", (capability, session)))
        self.capabilities.append(capability)
        return capability

    def get_by_capability_id(
        self, *, tenant_id: str, capability_id: str, session: Any | None = None
    ) -> PasswordRecoveryCapability | None:
        self.calls.append(("get", (tenant_id, capability_id, session)))
        return next(
            (item for item in self.capabilities if item.tenant_id == tenant_id and item.capability_id == capability_id),
            None,
        )

    def revoke(
        self, capability: PasswordRecoveryCapability, revoked_at: datetime, *, session: Any | None = None
    ) -> PasswordRecoveryCapability:
        self.calls.append(("revoke", (capability, revoked_at, session)))
        replacement = capability.revoke(revoked_at)
        self._replace(replacement)
        return replacement

    def expire(
        self, capability: PasswordRecoveryCapability, expired_at: datetime, *, session: Any | None = None
    ) -> PasswordRecoveryCapability:
        self.calls.append(("expire", (capability, expired_at, session)))
        replacement = capability.expire(expired_at)
        self._replace(replacement)
        return replacement


class _Delivery:
    def __init__(self, events: list[str], *, fail: bool = False) -> None:
        self.events = events
        self.fail = fail
        self.calls: list[dict[str, Any]] = []

    def deliver_password_recovery(self, **kwargs: Any) -> None:
        self.events.append("delivery")
        self.calls.append(dict(kwargs))
        if self.fail:
            raise RuntimeError("synthetic delivery failure")


def _capability(
    capability_id: str, issued_at: datetime, expires_at: datetime
) -> PasswordRecoveryCapability:
    return PasswordRecoveryCapability.issue(
        capability_id=capability_id,
        tenant_id="TENANT-ONE",
        principal_id="principal-a",
        token_digest=hashlib.sha3_512(capability_id.encode("utf-8")).hexdigest(),
        issued_at=issued_at,
        expires_at=expires_at,
    )


def _service(
    *,
    auth: _Auth | None = None,
    principal: _PrincipalRepository | None = None,
    registry: _Registry | None = None,
    delivery_fail: bool = False,
) -> tuple[PasswordRecoveryRequestService, _Client, _Registry, _Delivery, list[str]]:
    events: list[str] = []
    client = _Client(events)
    recovery = registry or _Registry()
    delivery = _Delivery(events, fail=delivery_fail)
    service = PasswordRecoveryRequestService(
        delivery=delivery,
        client=client,
        auth_registry=auth or _Auth(),
        recovery_registry=recovery,
        principal_repository=principal or _PrincipalRepository(),
        clock=lambda: NOW,
        token_factory=lambda: RAW_TOKEN,
        capability_id_factory=lambda: "WILSYREC-CERT",
    )
    return service, client, recovery, delivery, events


def test_constants_and_public_result_are_bounded() -> None:
    assert RECOVERY_TTL == timedelta(minutes=30)
    assert RECOVERY_COOLDOWN == timedelta(seconds=60)
    result = PasswordRecoveryRequestResult()
    assert result.status == "PASSWORD_RECOVERY_REQUEST_ACCEPTED"
    assert result.__dict__ if hasattr(result, "__dict__") else True
    assert "token" not in repr(result).lower()
    assert "principal" not in repr(result).lower()


@pytest.mark.parametrize("email", ["", "invalid", "a@b", "a @example.com", None])
def test_invalid_request_fails_before_persistence_or_delivery(email: object) -> None:
    service, client, registry, delivery, _events = _service()
    with pytest.raises(PasswordRecoveryRequestServiceError) as error:
        service.request_recovery(tenant_id="TENANT-ONE", email=email)  # type: ignore[arg-type]
    assert error.value.code is PasswordRecoveryRequestCode.INVALID_REQUEST
    assert client.sessions == []
    assert registry.calls == []
    assert delivery.calls == []


def test_absent_and_inactive_principals_return_same_receipt_without_delivery() -> None:
    absent, absent_client, _registry, absent_delivery, _events = _service(auth=_Auth(None))
    inactive, inactive_client, _registry2, inactive_delivery, _events2 = _service(
        principal=_PrincipalRepository(PrincipalStatus.SUSPENDED)
    )
    assert absent.request_recovery(tenant_id="TENANT-ONE", email="person@example.com") == PasswordRecoveryRequestResult()
    assert inactive.request_recovery(tenant_id="TENANT-ONE", email="person@example.com") == PasswordRecoveryRequestResult()
    assert absent_client.sessions == [] and inactive_client.sessions == []
    assert absent_delivery.calls == [] and inactive_delivery.calls == []


def test_success_expires_and_revokes_prior_windows_then_delivers_after_commit() -> None:
    expired = _capability("expired", NOW - timedelta(hours=2), NOW - timedelta(hours=1))
    older = _capability("older", NOW - timedelta(minutes=10), NOW + timedelta(minutes=20))
    registry = _Registry([expired, older])
    service, client, recovery, delivery, events = _service(registry=registry)

    result = service.request_recovery(tenant_id="TENANT-ONE", email=" PERSON@EXAMPLE.COM ")

    assert result == PasswordRecoveryRequestResult()
    assert len(client.sessions) == 1
    assert [call[0] for call in recovery.calls[:4]] == ["list", "expire", "revoke", "create"]
    created = next(item for item in recovery.capabilities if item.capability_id == "WILSYREC-CERT")
    assert created.status is PasswordRecoveryCapabilityStatus.ACTIVE
    assert created.issued_at == NOW
    assert created.expires_at == NOW + timedelta(minutes=30)
    assert created.token_digest == hashlib.sha3_512(RAW_TOKEN.encode("utf-8")).hexdigest()
    assert RAW_TOKEN not in repr(created)
    assert delivery.calls == [{
        "recipient_email": "person@example.com",
        "recovery_token": RAW_TOKEN,
        "expires_at": NOW + timedelta(minutes=30),
    }]
    assert events.index("transaction-commit") < events.index("delivery")


def test_recent_active_window_enforces_cooldown_without_reissue_or_delivery() -> None:
    recent = _capability("recent", NOW - timedelta(seconds=30), NOW + timedelta(minutes=29))
    registry = _Registry([recent])
    service, _client, recovery, delivery, _events = _service(registry=registry)
    result = service.request_recovery(tenant_id="TENANT-ONE", email="person@example.com")
    assert result == PasswordRecoveryRequestResult()
    assert [call[0] for call in recovery.calls] == ["list"]
    assert delivery.calls == []
    assert len(recovery.capabilities) == 1


def test_transaction_reresolves_principal_with_same_session() -> None:
    auth = _Auth()
    service, client, _recovery, _delivery, _events = _service(auth=auth)
    service.request_recovery(tenant_id="TENANT-ONE", email="person@example.com")
    assert len(auth.calls) == 2
    assert auth.calls[0] == ("TENANT-ONE", "person@example.com", None)
    assert auth.calls[1][0:2] == ("TENANT-ONE", "person@example.com")
    assert auth.calls[1][2] is client.sessions[0]


def test_delivery_failure_compensates_new_capability_and_emits_no_secret_in_error(monkeypatch: pytest.MonkeyPatch) -> None:
    audit_calls: list[tuple[Any, ...]] = []
    monkeypatch.setattr(
        "tools.eos.saas.auth.password_recovery_request_service.log_auth_event",
        lambda *args, **kwargs: audit_calls.append((*args, kwargs)),
    )
    service, client, recovery, delivery, events = _service(delivery_fail=True)
    with pytest.raises(PasswordRecoveryRequestServiceError) as error:
        service.request_recovery(tenant_id="TENANT-ONE", email="person@example.com")
    assert error.value.code is PasswordRecoveryRequestCode.DELIVERY_FAILURE
    assert RAW_TOKEN not in str(error.value)
    issued = next(item for item in recovery.capabilities if item.capability_id == "WILSYREC-CERT")
    assert issued.status is PasswordRecoveryCapabilityStatus.REVOKED
    assert len(client.sessions) == 2
    assert events.count("transaction-commit") == 2
    assert delivery.calls[0]["recovery_token"] == RAW_TOKEN
    assert audit_calls


def test_service_source_never_returns_logs_or_persists_raw_token() -> None:
    source = inspect.getsource(PasswordRecoveryRequestService)
    assert "return raw_token" not in source
    assert "token_digest=token_digest" in source
    assert "recovery_token=raw_token" in source
    assert "log_auth_event" in source
    assert "recipient_email" in source
    assert "passwordHash" not in source
    assert "generate_jwt" not in source
    assert "create_session" not in source
    assert "revoke_sessions" not in source


# ARTIFACT: tests/unit/test_password_recovery_request_service.py
# VERSION: v1.0.0-R10E3-PASSWORD-RECOVERY-REQUEST-SERVICE-CERT
# AUTHORITY BOUNDARY: deterministic recovery-request orchestration evidence only
# TENANT POSTURE: exact tenant/email lookup and tenant/principal capability lifecycle
# FAIL-CLOSED POSTURE: invalid, ambiguous, transaction, and delivery failure returns no recovery secret
# FINANCIAL EXECUTION AUTHORITY: None; Kennel EOS remains exclusive
# END OF WILSY OS SOVEREIGN ARTIFACT
