"""Direct deterministic certificate for the WILSY OS reset orchestrator.

TITLE: WILSY OS Password Reset Service Direct Certificate
VERSION: v1.1.0-R10G10-ATOMIC-RESET-NOTIFICATION-CERT
AUTHORITY: Wilsy OS Core Governance
EPITOME: Certifies the public password-reset service boundary, ordering,
         durable-authority composition, failure handling, replay posture,
         callback retry rereads, and secret hygiene with deterministic fakes.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tests/unit/test_password_reset_service.py
COLLABORATION / OWNERSHIP: Certifies
                           tools/eos/saas/auth/password_reset_service.py;
                           production transaction and real-Mongo behavior are
                           reserved for later evidence gates.
CERTIFICATION / UPDATE DATE: 2026-09-22
CHANGELOG: v1.1.0-R10G10-ATOMIC-RESET-NOTIFICATION-CERT extends the frozen R10D2 certificate with
           atomic reset-notification intent creation, exact session propagation,
           retry-stable notification identity, rollback on notification
           persistence failure, post-commit-only dispatch, and non-fatal
           certified delivery failure.
           v1.0.0-R10D2-PASSWORD-RESET-SERVICE-DIRECT-CERT establishes direct public-entrypoint coverage for
           policy and hashing order, transactional capability revalidation,
           credential CAS, exact revocation, consume, replay, retry rereads,
           authority exclusion, and secret-safe results.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2 awareness.
SECURITY / PRIVACY POSTURE: Synthetic credentials only. No live environment
                            secret, bearer value, password hash, revision,
                            session identifier, or database payload is used.
TENANT BOUNDARY: Fakes require exact tenant/principal propagation and never
                 grant authority from caller-supplied identity fields.
AUTHORITY BOUNDARY: Test evidence only; no production authority, transport,
                    database, JWT, delivery, MFA, membership, role, or
                    financial execution is created.
FINANCIAL AUTHORITY BOUNDARY: None; Kennel EOS remains exclusive.
FAIL-CLOSED POSTURE: Every invalid, stale, failing, replayed, or uncertain
                     service path must raise without a success receipt.
"""
from __future__ import annotations

from datetime import datetime, timedelta, timezone
import hashlib
import ast
from pathlib import Path
from typing import Any

import pytest

from tools.eos.saas.auth.password_recovery import (
    PasswordRecoveryCapability,
    PasswordRecoveryCapabilityStatus,
)
from tools.eos.saas.auth.password_reset_notification import PasswordResetNotification
from tools.eos.saas.auth.password_reset_notification_dispatcher import (
    PasswordResetNotificationDispatchError,
)
from tools.eos.saas.auth.password_reset_notification_registry import (
    PasswordResetNotificationRegistryError,
)
from tools.eos.saas.auth.password_reset_service import (
    PasswordResetCode,
    PasswordResetResult,
    PasswordResetService,
    PasswordResetServiceError,
)


VERSION = "v1.1.0-R10G10-ATOMIC-RESET-NOTIFICATION-CERT"
NOW = datetime(2026, 9, 22, 12, 0, tzinfo=timezone.utc)
TENANT = "tenant-a"
PRINCIPAL = "principal-a"
RECOVERY_TOKEN = "synthetic-recovery-token"
TOKEN_DIGEST = hashlib.sha3_512(RECOVERY_TOKEN.encode("utf-8")).hexdigest()
NEW_PASSWORD = "synthetic valid password 123"
NOTIFICATION_ID = "WILSYRESETNOTICE-R10G10-CERT"


def _capability(
    *,
    status: PasswordRecoveryCapabilityStatus = PasswordRecoveryCapabilityStatus.ACTIVE,
    tenant_id: str = TENANT,
    principal_id: str = PRINCIPAL,
    expires_at: datetime | None = None,
) -> PasswordRecoveryCapability:
    """Create one deterministic capability with no live identity material."""

    issued_at = NOW - timedelta(minutes=5)
    expiry = expires_at or NOW + timedelta(hours=1)
    consumed_at = NOW - timedelta(minutes=1) if status is PasswordRecoveryCapabilityStatus.CONSUMED else None
    expired_at = expiry if status is PasswordRecoveryCapabilityStatus.EXPIRED else None
    revoked_at = NOW - timedelta(minutes=1) if status is PasswordRecoveryCapabilityStatus.REVOKED else None
    return PasswordRecoveryCapability(
        capability_id="cap-a",
        tenant_id=tenant_id,
        principal_id=principal_id,
        token_digest=TOKEN_DIGEST,
        issued_at=issued_at,
        expires_at=expiry,
        status=status,
        consumed_at=consumed_at,
        expired_at=expired_at,
        revoked_at=revoked_at,
    )


class RecordingChecker:
    """Synthetic blocklist capability recording only policy interaction."""

    def __init__(self, *, mode: str = "allow") -> None:
        self.mode = mode
        self.calls: list[str] = []
        self.contexts: list[tuple[str, ...] | None] = []

    def is_blocked(self, candidate: str) -> bool:
        """Return deterministic policy evidence without persistence."""

        self.calls.append(candidate)
        self.contexts.append(None)
        if self.mode == "failure":
            raise RuntimeError("synthetic checker failure")
        return self.mode == "blocked"


class RecordingSession:
    """Minimal transaction wrapper with optional aborted-callback retry."""

    def __init__(self, events: list[str], *, retry_once: bool = False, fail_wrapper: bool = False) -> None:
        self.events = events
        self.retry_once = retry_once
        self.fail_wrapper = fail_wrapper
        self.callback_count = 0
        self.committed = False
        self.aborted = False

    def __enter__(self) -> "RecordingSession":
        self.events.append("session_enter")
        return self

    def __exit__(self, *args: object) -> bool:
        self.events.append("session_exit")
        return False

    def with_transaction(self, callback: Any) -> None:
        """Run callback, optionally replaying only an aborted transient attempt."""

        if self.fail_wrapper:
            self.events.append("transaction_wrapper_failure")
            raise RuntimeError("synthetic wrapper failure")
        while True:
            self.callback_count += 1
            self.events.append(f"callback_{self.callback_count}")
            try:
                callback(self)
            except Exception:
                self.aborted = True
                raise
            if self.retry_once and self.callback_count == 1:
                self.events.append("transient_attempt_aborted")
                continue
            self.committed = True
            self.events.append("transaction_complete")
            return


class RecordingClient:
    """Synthetic client/session source; it never opens a real database."""

    def __init__(self, *, retry_once: bool = False, fail_wrapper: bool = False) -> None:
        self.events: list[str] = []
        self.retry_once = retry_once
        self.fail_wrapper = fail_wrapper
        self.start_count = 0
        self.session: RecordingSession | None = None

    def start_session(self) -> RecordingSession:
        """Record one client-owned session acquisition."""

        self.start_count += 1
        self.events.append("start_session")
        self.session = RecordingSession(
            self.events,
            retry_once=self.retry_once,
            fail_wrapper=self.fail_wrapper,
        )
        return self.session


class RecordingRecoveryRegistry:
    """Synthetic recovery registry preserving lookup and consume authority."""

    def __init__(self, capabilities: list[PasswordRecoveryCapability | None]) -> None:
        self.capabilities = capabilities
        self.last_capability: PasswordRecoveryCapability | None = None
        self.lookup_calls: list[tuple[str, str, object | None]] = []
        self.consume_calls: list[tuple[PasswordRecoveryCapability, object | None]] = []
        self.consumed = False

    def get_by_token_digest(
        self,
        *,
        tenant_id: str,
        token_digest: str,
        session: object | None = None,
    ) -> PasswordRecoveryCapability | None:
        """Return the next durable snapshot only for the exact tenant selector."""

        self.lookup_calls.append((tenant_id, token_digest, session))
        if tenant_id != TENANT:
            return None
        if self.consumed:
            return _capability(status=PasswordRecoveryCapabilityStatus.CONSUMED)
        if self.capabilities:
            value = self.capabilities.pop(0)
            if value is not None:
                self.last_capability = value
                return value
        return self.last_capability

    def consume(
        self,
        capability: PasswordRecoveryCapability,
        consumed_at: datetime,
        *,
        session: object | None = None,
    ) -> PasswordRecoveryCapability:
        """Record exact transactional capability consumption."""

        self.consume_calls.append((capability, session))
        self.consumed = True
        return capability.consume(consumed_at)


class RetryRecoveryRegistry(RecordingRecoveryRegistry):
    """Recovery fake whose aborted callback attempts leave durable state intact."""

    def consume(
        self,
        capability: PasswordRecoveryCapability,
        consumed_at: datetime,
        *,
        session: object | None = None,
    ) -> PasswordRecoveryCapability:
        """Record the transition without committing fake durable state."""

        self.consume_calls.append((capability, session))
        return capability.consume(consumed_at)


class RecordingAuthRegistry:
    """Synthetic AuthRegistry authority recording exact reset participants."""

    def __init__(self, *, failure: str | None = None, revision: int = 7) -> None:
        self.failure = failure
        self.revision = revision
        self.events: list[str] = []
        self.hash_calls: list[str] = []
        self.revision_calls: list[tuple[str, str, object | None]] = []
        self.cas_calls: list[tuple[str, str, int, str, object | None]] = []
        self.session_calls: list[tuple[str, str, object | None]] = []
        self.refresh_calls: list[tuple[str, str, object | None]] = []

    def hash_password(self, password: str) -> str:
        """Return synthetic bcrypt-shaped output before transaction start."""

        self.events.append("hash")
        self.hash_calls.append(password)
        if self.failure == "hash":
            raise RuntimeError("synthetic hash failure")
        return "bcrypt$synthetic$hash"

    def get_credential_revision(self, tenant_id: str, user_id: str, *, session: object | None = None) -> int:
        """Return durable revision evidence with exact session identity."""

        self.events.append("revision")
        self.revision_calls.append((tenant_id, user_id, session))
        if self.failure == "revision":
            raise RuntimeError("synthetic revision failure")
        return self.revision

    def compare_and_swap_password_hash(
        self,
        tenant_id: str,
        user_id: str,
        expected_credential_revision: int,
        new_password_hash: str,
        *,
        session: object | None = None,
    ) -> int:
        """Record exact atomic CAS arguments without implementing CAS logic."""

        self.events.append("cas")
        self.cas_calls.append((tenant_id, user_id, expected_credential_revision, new_password_hash, session))
        if self.failure == "cas":
            raise RuntimeError("synthetic CAS failure")
        return expected_credential_revision + 1

    def revoke_sessions(self, tenant_id: str, user_id: str, *, session: object | None = None) -> int:
        """Record exact tenant/principal session revocation."""

        self.events.append("sessions")
        self.session_calls.append((tenant_id, user_id, session))
        if self.failure == "sessions":
            raise RuntimeError("synthetic session failure")
        return 2

    def revoke_refresh_tokens(self, tenant_id: str, user_id: str, *, session: object | None = None) -> int:
        """Record exact tenant/principal refresh revocation."""

        self.events.append("refresh")
        self.refresh_calls.append((tenant_id, user_id, session))
        if self.failure == "refresh":
            raise RuntimeError("synthetic refresh failure")
        return 3



class RecordingNotificationRegistry:
    """Synthetic notification registry recording exact transaction participation."""

    def __init__(self, *, failure: bool = False) -> None:
        self.failure = failure
        self.create_calls: list[tuple[PasswordResetNotification, object | None]] = []

    def create(
        self,
        notification: PasswordResetNotification,
        *,
        session: object | None = None,
    ) -> PasswordResetNotification:
        """Record one notification-intent insert on the caller session."""

        self.create_calls.append((notification, session))
        if self.failure:
            raise PasswordResetNotificationRegistryError(
                "SYNTHETIC_NOTIFICATION_CREATE_FAILED"
            )
        return notification


class RecordingNotificationDispatcher:
    """Synthetic post-commit dispatcher with stable optional failure."""

    def __init__(
        self,
        *,
        failure: bool = False,
        client: RecordingClient | None = None,
    ) -> None:
        self.failure = failure
        self.client = client
        self.calls: list[tuple[str, str, datetime]] = []
        self.committed_at_call: list[bool] = []

    def dispatch(
        self,
        *,
        tenant_id: str,
        notification_id: str,
        observed_at: datetime,
    ) -> object:
        """Record post-commit dispatch without external transport."""

        self.calls.append((tenant_id, notification_id, observed_at))
        committed = bool(
            self.client is not None
            and self.client.session is not None
            and self.client.session.committed
        )
        self.committed_at_call.append(committed)
        if self.failure:
            raise PasswordResetNotificationDispatchError(
                "PASSWORD_RESET_NOTIFICATION_DELIVERY_FAILED"
            )
        return object()


def _notification_registry(service: PasswordResetService) -> RecordingNotificationRegistry:
    """Return the deterministic injected notification registry."""

    value = service._notification_registry
    assert isinstance(value, RecordingNotificationRegistry)
    return value


def _notification_dispatcher(service: PasswordResetService) -> RecordingNotificationDispatcher:
    """Return the deterministic injected post-commit dispatcher."""

    value = service._notification_dispatcher
    assert isinstance(value, RecordingNotificationDispatcher)
    return value


def _service(
    recovery: RecordingRecoveryRegistry | None = None,
    auth: RecordingAuthRegistry | None = None,
    checker: RecordingChecker | None = None,
    client: RecordingClient | None = None,
    notification: RecordingNotificationRegistry | None = None,
    dispatcher: RecordingNotificationDispatcher | None = None,
) -> tuple[PasswordResetService, RecordingRecoveryRegistry, RecordingAuthRegistry, RecordingClient]:
    """Construct the real service with deterministic injected authorities."""

    registry = recovery or RecordingRecoveryRegistry([_capability()])
    authority = auth or RecordingAuthRegistry()
    mongo = client or RecordingClient()
    notice_registry = notification or RecordingNotificationRegistry()
    notice_dispatcher = dispatcher or RecordingNotificationDispatcher(client=mongo)
    return (
        PasswordResetService(
            client=mongo,
            recovery_registry=registry,
            auth_registry=authority,
            notification_registry=notice_registry,
            notification_dispatcher=notice_dispatcher,
            blocklist_checker=checker or RecordingChecker(),
            clock=lambda: NOW,
            notification_id_factory=lambda: NOTIFICATION_ID,
        ),
        registry,
        authority,
        mongo,
    )


def _reset(service: PasswordResetService) -> PasswordResetResult:
    """Invoke only the public reset entrypoint with synthetic values."""

    return service.reset_password(
        tenant_id=TENANT,
        recovery_token=RECOVERY_TOKEN,
        new_password=NEW_PASSWORD,
        context_terms=("synthetic-service",),
    )


def _assert_failure(service: PasswordResetService, code: PasswordResetCode) -> None:
    """Require one bounded code-only service failure."""

    with pytest.raises(PasswordResetServiceError) as caught:
        _reset(service)
    assert caught.value.code is code
    assert RECOVERY_TOKEN not in str(caught.value)
    assert NEW_PASSWORD not in repr(caught.value)


def test_success_order_and_public_receipt() -> None:
    """The public entrypoint performs the complete ordered composition."""

    service, recovery, auth, client = _service()
    checker = RecordingChecker()
    service, recovery, auth, client = _service(checker=checker)
    result = _reset(service)
    assert result == PasswordResetResult()
    assert auth.events == ["hash", "revision", "cas", "sessions", "refresh"]
    assert client.events == [
        "start_session",
        "session_enter",
        "callback_1",
        "transaction_complete",
        "session_exit",
    ]
    assert checker.calls == [NEW_PASSWORD]
    assert recovery.consume_calls[0][0].principal_id == PRINCIPAL
    notices = _notification_registry(service)
    dispatcher = _notification_dispatcher(service)
    assert len(notices.create_calls) == 1
    notice, notice_session = notices.create_calls[0]
    assert notice.notification_id == NOTIFICATION_ID
    assert notice.tenant_id == TENANT
    assert notice.principal_id == PRINCIPAL
    assert dispatcher.calls == [(TENANT, NOTIFICATION_ID, NOW)]
    assert dispatcher.committed_at_call == [True]
    assert client.session is not None and notice_session is client.session
    assert client.session.committed


def test_policy_rejection_starts_no_transaction() -> None:
    """A blocked prospective password cannot open persistence."""

    checker = RecordingChecker(mode="blocked")
    service, recovery, auth, client = _service(checker=checker)
    _assert_failure(service, PasswordResetCode.POLICY_REJECTED)
    assert client.start_count == 0
    assert auth.hash_calls == []
    assert recovery.consume_calls == []


def test_blocklist_failure_starts_no_transaction() -> None:
    """An unavailable checker fails closed before hashing or persistence."""

    service, recovery, auth, client = _service(checker=RecordingChecker(mode="failure"))
    _assert_failure(service, PasswordResetCode.POLICY_REJECTED)
    assert client.start_count == 0
    assert auth.hash_calls == []
    assert recovery.consume_calls == []


def test_hash_failure_starts_no_transaction() -> None:
    """Hash failure cannot produce a transaction or mutation."""

    service, recovery, auth, client = _service(auth=RecordingAuthRegistry(failure="hash"))
    _assert_failure(service, PasswordResetCode.HASHING_FAILED)
    assert client.start_count == 0
    assert recovery.consume_calls == []


def test_unknown_capability_fails_before_transaction() -> None:
    """Scoped absence is not interpreted as reset authority."""

    service, recovery, auth, client = _service(recovery=RecordingRecoveryRegistry([None]))
    _assert_failure(service, PasswordResetCode.RECOVERY_INVALID)
    assert client.start_count == 0
    assert auth.hash_calls == []


def test_expired_capability_fails_before_transaction() -> None:
    """Expired capability state is rejected before policy/hash work."""

    expired = _capability(expires_at=NOW - timedelta(seconds=1))
    service, recovery, auth, client = _service(recovery=RecordingRecoveryRegistry([expired]))
    _assert_failure(service, PasswordResetCode.RECOVERY_INVALID)
    assert client.start_count == 0
    assert auth.hash_calls == []


def test_consumed_capability_fails_before_transaction() -> None:
    """Consumed capability state cannot authorize a reset."""

    consumed = _capability(status=PasswordRecoveryCapabilityStatus.CONSUMED)
    service, recovery, auth, client = _service(recovery=RecordingRecoveryRegistry([consumed]))
    _assert_failure(service, PasswordResetCode.RECOVERY_INVALID)
    assert client.start_count == 0


def test_revoked_capability_fails_before_transaction() -> None:
    """Revoked capability state cannot authorize a reset."""

    revoked = _capability(status=PasswordRecoveryCapabilityStatus.REVOKED)
    service, recovery, auth, client = _service(recovery=RecordingRecoveryRegistry([revoked]))
    _assert_failure(service, PasswordResetCode.RECOVERY_INVALID)
    assert client.start_count == 0


def test_transactional_consumed_reread_overrides_active_preflight() -> None:
    """A capability becoming consumed between reads aborts the transaction."""

    consumed = _capability(status=PasswordRecoveryCapabilityStatus.CONSUMED)
    recovery = RecordingRecoveryRegistry([_capability(), consumed])
    service, recovery, auth, client = _service(recovery=recovery)
    _assert_failure(service, PasswordResetCode.RECOVERY_INVALID)
    assert client.session is not None and client.session.aborted
    assert auth.cas_calls == []
    assert len(recovery.lookup_calls) == 2


def test_transactional_revoked_reread_overrides_active_preflight() -> None:
    """A capability becoming revoked between reads aborts the transaction."""

    revoked = _capability(status=PasswordRecoveryCapabilityStatus.REVOKED)
    recovery = RecordingRecoveryRegistry([_capability(), revoked])
    service, recovery, auth, client = _service(recovery=recovery)
    _assert_failure(service, PasswordResetCode.RECOVERY_INVALID)
    assert client.session is not None and client.session.aborted
    assert auth.cas_calls == []
    assert len(recovery.lookup_calls) == 2


def test_tenant_and_principal_are_durable_not_caller_selected() -> None:
    """Caller selector cannot redirect the durable capability principal."""

    durable = _capability(tenant_id=TENANT, principal_id=PRINCIPAL)
    recovery = RecordingRecoveryRegistry([durable])
    service, recovery, auth, client = _service(recovery=recovery)
    with pytest.raises(PasswordResetServiceError) as caught:
        service.reset_password(
            tenant_id="attacker-selector",
            recovery_token=RECOVERY_TOKEN,
            new_password=NEW_PASSWORD,
        )
    assert caught.value.code is PasswordResetCode.RECOVERY_INVALID
    assert auth.cas_calls == []
    assert recovery.consume_calls == []
    assert client.start_count == 0


def test_revision_read_failure_aborts_without_success() -> None:
    """Durable revision unavailability cannot become a reset receipt."""

    service, recovery, auth, client = _service(auth=RecordingAuthRegistry(failure="revision"))
    _assert_failure(service, PasswordResetCode.TRANSACTION_FAILURE)
    assert client.session is not None and client.session.aborted
    assert recovery.consume_calls == []


def test_password_cas_failure_aborts_without_success() -> None:
    """Credential CAS failure prevents later revocation and consume."""

    service, recovery, auth, client = _service(auth=RecordingAuthRegistry(failure="cas"))
    _assert_failure(service, PasswordResetCode.TRANSACTION_FAILURE)
    assert client.session is not None and client.session.aborted
    assert auth.session_calls == [] and auth.refresh_calls == []
    assert recovery.consume_calls == []


def test_session_revocation_failure_aborts_without_success() -> None:
    """Session-revocation failure prevents refresh deletion and consume."""

    service, recovery, auth, client = _service(auth=RecordingAuthRegistry(failure="sessions"))
    _assert_failure(service, PasswordResetCode.TRANSACTION_FAILURE)
    assert client.session is not None and client.session.aborted
    assert auth.refresh_calls == [] and recovery.consume_calls == []


def test_refresh_revocation_failure_aborts_without_success() -> None:
    """Refresh-revocation failure prevents capability consumption."""

    service, recovery, auth, client = _service(auth=RecordingAuthRegistry(failure="refresh"))
    _assert_failure(service, PasswordResetCode.TRANSACTION_FAILURE)
    assert client.session is not None and client.session.aborted
    assert recovery.consume_calls == []


def test_recovery_consume_failure_aborts_without_success() -> None:
    """Consume failure cannot be reported as a committed reset."""

    class FailingConsume(RecordingRecoveryRegistry):
        def consume(self, capability: PasswordRecoveryCapability, consumed_at: datetime, *, session: object | None = None) -> PasswordRecoveryCapability:
            self.consume_calls.append((capability, session))
            raise RuntimeError("synthetic consume failure")

    recovery = FailingConsume([_capability()])
    service, recovery, auth, client = _service(recovery=recovery)
    _assert_failure(service, PasswordResetCode.TRANSACTION_FAILURE)
    assert client.session is not None and client.session.aborted



def test_notification_persistence_failure_aborts_reset_before_commit() -> None:
    """Reset success requires atomic durable notification intent."""

    notices = RecordingNotificationRegistry(failure=True)
    dispatcher = RecordingNotificationDispatcher()
    service, recovery, auth, client = _service(
        notification=notices,
        dispatcher=dispatcher,
    )

    _assert_failure(service, PasswordResetCode.NOTIFICATION_PERSISTENCE_FAILURE)

    assert client.session is not None and client.session.aborted
    assert not client.session.committed
    assert len(notices.create_calls) == 1
    assert dispatcher.calls == []


def test_notification_intent_uses_durable_capability_identity_only() -> None:
    """Caller cannot nominate notification tenant, principal, or recipient."""

    service, recovery, auth, client = _service()
    _reset(service)

    notices = _notification_registry(service)
    notice = notices.create_calls[0][0]
    assert notice.tenant_id == TENANT
    assert notice.principal_id == PRINCIPAL
    assert notice.notification_id == NOTIFICATION_ID
    rendered = repr(notice.to_document()).lower()
    for forbidden in ("email", "address", "password", "recovery_token", "token_digest"):
        assert forbidden not in rendered


def test_post_commit_dispatch_failure_does_not_rewrite_committed_reset_truth() -> None:
    """Certified delivery failure leaves the committed reset receipt valid."""

    client = RecordingClient()
    dispatcher = RecordingNotificationDispatcher(failure=True, client=client)
    service, recovery, auth, client = _service(
        client=client,
        dispatcher=dispatcher,
    )

    result = _reset(service)

    assert result == PasswordResetResult()
    assert client.session is not None and client.session.committed
    assert dispatcher.calls == [(TENANT, NOTIFICATION_ID, NOW)]
    assert dispatcher.committed_at_call == [True]
    assert len(_notification_registry(service).create_calls) == 1


def test_notification_identity_is_created_once_per_public_call_across_callback_retry() -> None:
    """Whole-transaction callback retries preserve one logical notification ID."""

    recovery = RetryRecoveryRegistry([_capability(), _capability()])
    client = RecordingClient(retry_once=True)
    service, recovery, auth, client = _service(
        recovery=recovery,
        client=client,
    )

    _reset(service)

    notices = _notification_registry(service)
    assert len(notices.create_calls) == 2
    first, second = notices.create_calls
    assert first[0].notification_id == second[0].notification_id == NOTIFICATION_ID
    assert first[0].occurred_at == second[0].occurred_at == NOW
    assert _notification_dispatcher(service).calls == [(TENANT, NOTIFICATION_ID, NOW)]


def test_transaction_wrapper_failure_claims_no_success() -> None:
    """A transaction-wrapper fracture returns no bounded success receipt."""

    service, recovery, auth, client = _service(client=RecordingClient(fail_wrapper=True))
    _assert_failure(service, PasswordResetCode.TRANSACTION_FAILURE)
    assert client.start_count == 1
    assert recovery.consume_calls == []


def test_exact_same_session_reaches_every_mutation() -> None:
    """Object identity proves one transaction session reaches every participant."""

    service, recovery, auth, client = _service()
    _reset(service)
    assert client.session is not None
    session = client.session
    assert recovery.lookup_calls[1][2] is session
    assert auth.revision_calls[0][2] is session
    assert auth.cas_calls[0][4] is session
    assert auth.session_calls[0][2] is session
    assert auth.refresh_calls[0][2] is session
    assert recovery.consume_calls[0][1] is session
    notices = _notification_registry(service)
    assert len(notices.create_calls) == 1
    assert notices.create_calls[0][1] is session


def test_replay_after_success_is_rejected() -> None:
    """A consumed durable capability cannot authorize a second public call."""

    recovery = RecordingRecoveryRegistry([_capability()])
    service, recovery, auth, client = _service(recovery=recovery)
    _reset(service)
    _assert_failure(service, PasswordResetCode.RECOVERY_INVALID)
    assert client.start_count == 1


def test_callback_retry_rereads_capability_and_revision() -> None:
    """Transient callback retry rereads durable capability and revision."""

    recovery = RetryRecoveryRegistry([_capability(), _capability()])
    auth = RecordingAuthRegistry()
    client = RecordingClient(retry_once=True)
    service, recovery, auth, client = _service(recovery=recovery, auth=auth, client=client)
    _reset(service)
    assert client.session is not None and client.session.callback_count == 2
    assert len(recovery.lookup_calls) == 3
    assert len(auth.revision_calls) == 2
    assert len(auth.cas_calls) == 2
    assert all(call[2] is client.session for call in recovery.lookup_calls[1:])
    assert all(call[2] is client.session for call in auth.revision_calls)
    assert all(call[4] is client.session for call in auth.cas_calls)
    notices = _notification_registry(service)
    assert len(notices.create_calls) == 2
    assert {notice.notification_id for notice, _session in notices.create_calls} == {NOTIFICATION_ID}
    assert all(session is client.session for _notice, session in notices.create_calls)
    assert _notification_dispatcher(service).calls == [(TENANT, NOTIFICATION_ID, NOW)]


def test_no_token_or_authenticated_session_issuance() -> None:
    """Static and runtime evidence show reset has no issuance authority."""

    service, recovery, auth, client = _service()
    result = _reset(service)
    assert result == PasswordResetResult()
    source = Path("tools/eos/saas/auth/password_reset_service.py").read_text()
    for forbidden in (
        "generate_jwt",
        "generate_access_jwt",
        "generate_pre_auth_jwt",
        "create_access_token",
        "generate_refresh_token",
        "create_session",
        "TokenService",
    ):
        assert forbidden not in source
    assert auth.events == ["hash", "revision", "cas", "sessions", "refresh"]


def test_non_password_authorities_are_untouched() -> None:
    """The service has no calls or parameters for MFA, roles, or status."""

    service, recovery, auth, client = _service()
    _reset(service)
    source = Path("tools/eos/saas/auth/password_reset_service.py").read_text()
    for forbidden in (
        "mfaRegistered",
        "otp_secrets",
        "role_assignment",
        "permissions",
        "PrincipalStatus",
        "legal_acceptance",
    ):
        assert forbidden not in source
    assert auth.session_calls and auth.refresh_calls


def test_secret_hygiene_for_receipt_and_failures() -> None:
    """Success and failure representations contain no secret-bearing values."""

    service, recovery, auth, client = _service()
    result = _reset(service)
    rendered = f"{result!r} {result!s}"
    assert RECOVERY_TOKEN not in rendered
    assert TOKEN_DIGEST not in rendered
    assert "bcrypt$synthetic$hash" not in rendered
    assert "revision" not in rendered.lower()
    _assert_failure(
        _service(recovery=RecordingRecoveryRegistry([None]))[0],
        PasswordResetCode.RECOVERY_INVALID,
    )


def test_context_terms_only_reach_policy_checker() -> None:
    """Context terms cannot become persistence or mutation authority."""

    checker = RecordingChecker()
    service, recovery, auth, client = _service(checker=checker)
    _reset(service)
    assert checker.calls == [NEW_PASSWORD]
    assert auth.cas_calls[0][0:2] == (TENANT, PRINCIPAL)
    assert all("synthetic-service" not in str(call) for call in auth.cas_calls)


def test_no_service_level_transaction_retry_or_blind_cas_replay() -> None:
    """One public call owns one with_transaction invocation and no outer loop."""

    source = Path("tools/eos/saas/auth/password_reset_service.py").read_text()
    assert source.count("with_transaction(callback)") == 1
    assert "for _ in range" not in source
    assert "while True" not in source
    assert "compare_and_swap_password_hash" in source


def test_public_api_and_certificate_identity_are_frozen() -> None:
    """The certificate anchors the intended public service artifact."""

    source = Path("tools/eos/saas/auth/password_reset_service.py").read_text()
    certificate_source = Path(__file__).read_text()
    assert VERSION in certificate_source
    assert "class PasswordResetService" in source
    assert "def reset_password(" in source
    assert "PasswordResetResult" in source
    assert "PasswordResetServiceError" in source


def test_callback_retry_does_not_use_cached_revision_or_capability() -> None:
    """Each retry obtains a fresh capability and revision snapshot."""

    recovery = RetryRecoveryRegistry([_capability(), _capability()])
    auth = RecordingAuthRegistry(revision=17)
    client = RecordingClient(retry_once=True)
    service, recovery, auth, client = _service(recovery=recovery, auth=auth, client=client)
    _reset(service)
    assert [call[2] for call in recovery.lookup_calls[1:]] == [client.session, client.session]
    assert [call[2] for call in auth.revision_calls] == [client.session, client.session]
    assert [call[4] for call in auth.cas_calls] == [client.session, client.session]
    assert [call[2] for call in auth.cas_calls] == [17, 17]


def test_service_source_has_no_live_transport_or_database_client_creation() -> None:
    """The certificate and service remain deterministic at this evidence class."""

    source = Path("tools/eos/saas/auth/password_reset_service.py").read_text()
    assert "from pymongo" not in source
    assert "import pymongo" not in source
    assert "urllib" not in source
    assert "requests" not in source
    assert "httpx" not in source
    assert "smtplib" not in source
    assert "start_session()" in source
    assert "notification_registry.create(notification, session=session)" in source


def test_transaction_failure_has_no_partial_success_claim() -> None:
    """Every participant failure produces an exception, never a receipt."""

    for failure in ("revision", "cas", "sessions", "refresh"):
        service, recovery, auth, client = _service(auth=RecordingAuthRegistry(failure=failure))
        with pytest.raises(PasswordResetServiceError):
            _reset(service)
        assert client.session is not None and not client.session.committed


def test_f9_link_is_the_credential_cas_not_verifier_duplication() -> None:
    """The reset certificate links to F9 through the canonical CAS seam only."""

    service, recovery, auth, client = _service()
    _reset(service)
    assert len(auth.cas_calls) == 1
    source = Path("tools/eos/saas/auth/password_reset_service.py").read_text()
    assert "get_current_identity" not in source
    assert "verify_access_token" not in source
    assert "compare_and_swap_password_hash" in source


def test_recovery_consume_uses_transactional_snapshot_not_preflight_object() -> None:
    """The consumed object is the second, transactionally re-read value."""

    first = _capability()
    second = _capability()
    recovery = RecordingRecoveryRegistry([first, second])
    service, recovery, auth, client = _service(recovery=recovery)
    _reset(service)
    assert recovery.consume_calls[0][0] is second
    assert recovery.consume_calls[0][0] is not first


def test_caller_revision_is_not_an_entrypoint_argument() -> None:
    """The public API derives revision from durable AuthRegistry state."""

    service, recovery, auth, client = _service()
    _reset(service)
    assert auth.cas_calls[0][2] == 7
    assert "expected_credential_revision" not in str(PasswordResetService.reset_password)


def test_transaction_callback_uses_exact_durable_identity_on_all_mutations() -> None:
    """Every mutation receives the capability's durable tenant and principal."""

    service, recovery, auth, client = _service()
    _reset(service)
    assert auth.cas_calls[0][0:2] == (TENANT, PRINCIPAL)
    assert auth.session_calls[0][0:2] == (TENANT, PRINCIPAL)
    assert auth.refresh_calls[0][0:2] == (TENANT, PRINCIPAL)


def test_certificate_contains_no_environment_secrets_or_real_credentials() -> None:
    """The certificate uses only explicit synthetic values."""

    service_source = Path("tools/eos/saas/auth/password_reset_service.py").read_text()
    assert "os.getenv" not in service_source
    assert "MONGODB_URI" not in service_source
    assert "JWT_SECRET" not in service_source
    assert "-----BEGIN" not in service_source


def test_transactional_read_and_mutation_counts_are_bounded() -> None:
    """One success performs exactly one preflight and one transactional reread."""

    service, recovery, auth, client = _service()
    _reset(service)
    assert len(recovery.lookup_calls) == 2
    assert len(auth.revision_calls) == 1
    assert len(auth.cas_calls) == 1
    assert len(auth.session_calls) == 1
    assert len(auth.refresh_calls) == 1
    assert len(recovery.consume_calls) == 1


def test_certificate_has_no_parameterized_case_loss_or_runtime_skip() -> None:
    """All direct cases are ordinary collected tests with no dynamic omissions."""

    tree = ast.parse(Path(__file__).read_text())
    forbidden = {"parametrize", "skip", "skipif", "xfail"}
    calls = [node for node in ast.walk(tree) if isinstance(node, ast.Call)]
    assert all(
        not (
            isinstance(call.func, ast.Attribute)
            and call.func.attr in forbidden
        )
        for call in calls
    )


def test_result_is_minimal_and_non_sensitive() -> None:
    """The success receipt contains only a bounded status field."""

    service, recovery, auth, client = _service()
    result = _reset(service)
    assert result.status == "PASSWORD_RESET_COMMITTED"
    assert set(result.__dataclass_fields__) == {"status"}
    assert NOTIFICATION_ID not in repr(result)


# ARTIFACT: test_password_reset_service.py
# VERSION: v1.1.0-R10G10-ATOMIC-RESET-NOTIFICATION-CERT
# AUTHORITY BOUNDARY: deterministic direct certificate only; no production authority
# TENANT POSTURE: exact synthetic tenant/principal propagation is asserted
# FAIL-CLOSED POSTURE: invalid, replayed, partial, and unavailable paths require denial
# FINANCIAL EXECUTION AUTHORITY: none; Kennel EOS remains exclusive
# END OF WILSY OS SOVEREIGN ARTIFACT
