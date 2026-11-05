"""EOS application service for scoped System Services cases.

Authentication and final IAM decisions are injected from canonical EOS
composition. This service never trusts actor or tenant identifiers from a
request body and never owns Mongo transaction lifecycle.
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from hashlib import sha3_256
from typing import Callable, Protocol

from pymongo.client_session import ClientSession
from uuid import uuid4

from tools.eos.system_services.support_case import (
    SupportCase,
    SupportCaseCategory,
    SupportCaseEvent,
    SupportCaseScope,
    SupportCaseStatus,
)
from tools.eos.system_services.support_case_registry import SupportCaseRegistry


PERMISSION_QUEUE_READ = "system_services:queue:read"
PERMISSION_CASE_TRIAGE = "system_services:case:triage"
PERMISSION_IDENTITY_READ = "system_services:identity:read"


class SupportCaseApplicationError(RuntimeError):
    def __init__(self, code: str) -> None:
        self.code = code
        super().__init__(code)


@dataclass(frozen=True, slots=True)
class SupportCaseActorContext:
    """Server-derived actor and exact scope supplied by authenticated EOS composition."""

    principal_id: str
    scope: SupportCaseScope
    tenant_id: str | None = None

    def __post_init__(self) -> None:
        if not isinstance(self.principal_id, str) or not self.principal_id or self.principal_id != self.principal_id.strip():
            raise SupportCaseApplicationError("CASE_ACTOR_INVALID")
        if not isinstance(self.scope, SupportCaseScope):
            raise SupportCaseApplicationError("CASE_ACTOR_SCOPE_INVALID")
        if self.scope is SupportCaseScope.SYSTEM and self.tenant_id is not None:
            raise SupportCaseApplicationError("SYSTEM_ACTOR_MUST_NOT_BIND_TENANT")
        if self.scope is SupportCaseScope.TENANT and (
            not isinstance(self.tenant_id, str) or not self.tenant_id or self.tenant_id != self.tenant_id.strip()
        ):
            raise SupportCaseApplicationError("TENANT_ACTOR_SCOPE_REQUIRED")


class SystemServicesAuthorizer(Protocol):
    """Adapter to canonical EOS current-principal, workforce and IAM currentness."""

    def require(
        self,
        *,
        principal_id: str,
        permission_id: str,
        session: object | None,
    ) -> None: ...


class SupportCaseApplicationService:
    """Scope-safe user self-service and separately authorized SYSTEM queue operations."""

    def __init__(
        self,
        *,
        registry: SupportCaseRegistry,
        authorizer: SystemServicesAuthorizer,
        clock: Callable[[], datetime] | None = None,
        id_factory: Callable[[str], str] | None = None,
    ) -> None:
        if type(registry) is not SupportCaseRegistry or not callable(getattr(authorizer, "require", None)):
            raise SupportCaseApplicationError("CASE_APPLICATION_DEPENDENCY_INVALID")
        self._registry = registry
        self._authorizer = authorizer
        self._clock = clock or (lambda: datetime.now(timezone.utc))
        self._id_factory = id_factory or (lambda prefix: f"{prefix}-{uuid4().hex}")

    @staticmethod
    def _require_system_actor(actor: SupportCaseActorContext) -> None:
        if not isinstance(actor, SupportCaseActorContext) or actor.scope is not SupportCaseScope.SYSTEM:
            raise SupportCaseApplicationError("SYSTEM_SERVICES_SCOPE_REQUIRED")

    def create_own_case(
        self,
        *,
        actor: SupportCaseActorContext,
        category: SupportCaseCategory,
        idempotency_key: str,
        session: object,
    ) -> SupportCase:
        """Create a case only for the authenticated principal's exact tenant scope."""
        if not isinstance(actor, SupportCaseActorContext) or actor.scope is not SupportCaseScope.TENANT:
            raise SupportCaseApplicationError("TENANT_SELF_SERVICE_SCOPE_REQUIRED")
        if actor.tenant_id is None:
            raise SupportCaseApplicationError("TENANT_ACTOR_SCOPE_REQUIRED")
        if not isinstance(category, SupportCaseCategory):
            raise SupportCaseApplicationError("CASE_CATEGORY_INVALID")
        if not isinstance(idempotency_key, str) or not idempotency_key or idempotency_key != idempotency_key.strip():
            raise SupportCaseApplicationError("CASE_IDEMPOTENCY_KEY_INVALID")
        now = self._clock()
        request_fingerprint = sha3_256(
            (actor.tenant_id + "\\0" + actor.principal_id + "\\0" + idempotency_key).encode("utf-8")
        ).hexdigest()
        stable_case_id = "case-" + request_fingerprint
        case = SupportCase(
            case_id=stable_case_id,
            scope=SupportCaseScope.TENANT,
            tenant_id=actor.tenant_id,
            principal_id=actor.principal_id,
            category=category,
            created_at=now,
            updated_at=now,
        )
        event = SupportCaseEvent(
            event_id="event-" + request_fingerprint,
            case_id=case.case_id,
            actor_principal_id=actor.principal_id,
            idempotency_key="idem-" + request_fingerprint,
            from_status=None,
            to_status=SupportCaseStatus.OPEN,
            action="SELF_SERVICE_CASE_CREATED",
            occurred_at=now,
        )
        return self._registry.create(case, event, session=session)

    def list_own_cases(
        self,
        *,
        actor: SupportCaseActorContext,
        limit: int = 50,
        session: object | None = None,
    ) -> tuple[SupportCase, ...]:
        if not isinstance(actor, SupportCaseActorContext) or actor.scope is not SupportCaseScope.TENANT:
            raise SupportCaseApplicationError("TENANT_SELF_SERVICE_SCOPE_REQUIRED")
        return self._registry.list_cases(
            scope=SupportCaseScope.TENANT,
            tenant_id=actor.tenant_id,
            principal_id=actor.principal_id,
            limit=limit,
            session=session,
        )

    def read_own_case_history(
        self,
        *,
        actor: SupportCaseActorContext,
        case_id: str,
        session: object | None = None,
    ) -> tuple[SupportCaseEvent, ...]:
        if not isinstance(actor, SupportCaseActorContext) or actor.scope is not SupportCaseScope.TENANT:
            raise SupportCaseApplicationError("TENANT_SELF_SERVICE_SCOPE_REQUIRED")
        case = self._registry.get(
            case_id=case_id,
            scope=SupportCaseScope.TENANT,
            tenant_id=actor.tenant_id,
            session=session,
        )
        if case.principal_id != actor.principal_id:
            raise SupportCaseApplicationError("CASE_NOT_OWNED_BY_ACTOR")
        return self._registry.list_events(
            case_id=case_id,
            scope=SupportCaseScope.TENANT,
            tenant_id=actor.tenant_id,
            session=session,
        )

    def list_system_queue(
        self,
        *,
        actor: SupportCaseActorContext,
        limit: int = 50,
        statuses: tuple[SupportCaseStatus, ...] = (),
        session: object | None = None,
    ) -> tuple[SupportCase, ...]:
        self._require_system_actor(actor)
        self._authorizer.require(
            principal_id=actor.principal_id,
            permission_id=PERMISSION_QUEUE_READ,
            session=session,
        )
        return self._registry.list_cases(
            scope=SupportCaseScope.SYSTEM,
            statuses=statuses,
            limit=limit,
            session=session,
        )

    def read_system_case_history(
        self,
        *,
        actor: SupportCaseActorContext,
        case_id: str,
        session: object | None = None,
    ) -> tuple[SupportCaseEvent, ...]:
        self._require_system_actor(actor)
        self._authorizer.require(
            principal_id=actor.principal_id,
            permission_id=PERMISSION_IDENTITY_READ,
            session=session,
        )
        return self._registry.list_events(
            case_id=case_id,
            scope=SupportCaseScope.SYSTEM,
            session=session,
        )

    def transition_system_case(
        self,
        *,
        actor: SupportCaseActorContext,
        case_id: str,
        next_status: SupportCaseStatus,
        idempotency_key: str,
        expected_revision: int,
        session: object,
    ) -> SupportCase:
        self._require_system_actor(actor)
        self._authorizer.require(
            principal_id=actor.principal_id,
            permission_id=PERMISSION_CASE_TRIAGE,
            session=session,
        )
        current = self._registry.get(
            case_id=case_id,
            scope=SupportCaseScope.SYSTEM,
            session=session,
        )
        now = self._clock()
        event = SupportCaseEvent(
            event_id=self._id_factory("event"),
            case_id=case_id,
            actor_principal_id=actor.principal_id,
            idempotency_key=idempotency_key,
            from_status=current.status,
            to_status=next_status,
            action=f"CASE_TRANSITION_{next_status.value}",
            occurred_at=now,
        )
        return self._registry.transition(
            current=current,
            next_status=next_status,
            event=event,
            expected_revision=expected_revision,
            session=session,
        )


__all__ = [
    "PERMISSION_QUEUE_READ", "PERMISSION_CASE_TRIAGE", "PERMISSION_IDENTITY_READ",
    "SupportCaseApplicationError", "SupportCaseActorContext",
    "SystemServicesAuthorizer", "SupportCaseApplicationService",
]
