"""WILSY AI authenticated reasoning HTTP boundary.

TITLE: WILSY AI C1B Authenticated Reasoning Router
VERSION: v1.0.0-C1B-R19
AUTHORITY: Wilsy OS Core Governance
EPITOME: Exposes one tenant-authorized reasoning command while composing the
         published entitlement, capacity, admission, and C1B evidence owners.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tools/eos/api/wilsy_ai_reasoning_router.py
COLLABORATION / OWNERSHIP: HTTP owns request validation and Mongo transaction
                            lifecycle; C1B owns claim/execute/finalize;
                            P4/P6A/P6B/P6C registries remain canonical.
CERTIFICATION / UPDATE DATE: 2026-09-16
CHANGELOG: v1.0.0-C1B-R19 adds the authenticated reasoning command, bounded
           deterministic identity derivation, provider-outside-transaction
           execution, and replay-safe finalization.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2.
SECURITY / PRIVACY POSTURE: Prompt and model output are transient; no request
                             authority fields or provider exception details are
                             accepted, logged, or returned.
TENANT BOUNDARY: Tenant and principal come only from RequireTenantAuthorization.
AUTHORITY BOUNDARY: Reasoning evidence and usage admission only; no legal,
                    service, invoice, payment, or settlement authority.
FINANCIAL AUTHORITY BOUNDARY: Kennel EOS exclusively owns financial execution.
FAIL-CLOSED DECLARATION: Missing authority, persistence, binding, replay, and
                         transaction certainty return bounded errors.
"""
from __future__ import annotations

from collections.abc import Callable
from datetime import datetime, timezone
import hashlib
import json
import re
from typing import Any, Final

from fastapi import APIRouter, Depends, Header, HTTPException, Request, status
from pydantic import BaseModel, ConfigDict, Field

from tools.eos.api.tenant_authorization_http import (
    RequireTenantAuthorization,
    TenantAuthorizationContext,
)
from tools.eos.intelligence.domain.ai_model_provider_binding import (
    ServerOwnedModelProviderBinding,
)
from tools.eos.intelligence.registry.ai_model_invocation_registry import (
    AIModelInvocationRegistry,
    COLLECTION as INVOCATION_COLLECTION,
)
from tools.eos.intelligence.wilsy_ai_reasoning_orchestrator import (
    WilsyAIReasoningOrchestrator,
    WilsyAIReasoningOrchestratorError,
)
from tools.eos.saas.billing.wilsy_ai_entitlement_registry import (
    COLLECTION as ENTITLEMENT_COLLECTION,
    WilsyAIEntitlementRegistry,
)
from tools.eos.saas.billing.wilsy_ai_usage_admission_authority import (
    MODULE_ID,
    WilsyAIUsageAdmissionAuthority,
)
from tools.eos.saas.billing.wilsy_ai_usage_admission_registry import (
    COLLECTION as ADMISSION_COLLECTION,
    WilsyAIUsageAdmissionRegistry,
)
from tools.eos.saas.billing.wilsy_ai_usage_capacity_orchestrator import (
    WilsyAIUsageCapacityOrchestrator,
)
from tools.eos.saas.billing.wilsy_ai_usage_observation_registry import (
    COLLECTION as OBSERVATION_COLLECTION,
    WilsyAIUsageObservationRegistry,
)


VERSION: Final[str] = "v1.0.0-C1B-R19"
REASONING_PERMISSION: Final[str] = "wilsy_ai:reasoning:execute"
REASONING_OPERATION: Final[str] = "wilsy_ai_reasoning_execute"
SYSTEM_POLICY: Final[str] = "WILSY_AI_REASONING_C1B_BOUNDED_EVIDENCE_ONLY_V1"
_KEY = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._:-]{0,127}$")
_REASONING_AUTH = RequireTenantAuthorization(REASONING_PERMISSION, REASONING_OPERATION)


class WilsyAIReasoningRequest(BaseModel):
    """Minimal caller input; all identity, capacity, and policy are server-owned."""

    model_config = ConfigDict(extra="forbid", frozen=True)
    prompt: str = Field(min_length=1, max_length=12_000)


class _TransactionUnknown(RuntimeError):
    """Commit outcome was not conclusively observed."""


class _ReasoningHTTPError(RuntimeError):
    """Internal bounded error carrying only a stable public code/status."""

    def __init__(self, code: str, http_status: int) -> None:
        self.code = code
        self.http_status = http_status
        super().__init__(code)


def _database() -> Any:
    """Obtain the explicit kernel database without creating a connection."""
    from tools.eos.kernel.db import get_database

    database = get_database()
    if database is None:
        raise _ReasoningHTTPError("C1B_REASONING_PERSISTENCE_UNAVAILABLE", status.HTTP_503_SERVICE_UNAVAILABLE)
    return database


def _collections() -> dict[str, Any]:
    """Resolve canonical C1B/P4/P5A collections from the active database."""
    database = _database()
    return {
        "entitlement": database[ENTITLEMENT_COLLECTION],
        "admission": database[ADMISSION_COLLECTION],
        "invocation": database[INVOCATION_COLLECTION],
        "observation": database[OBSERVATION_COLLECTION],
    }


def _start_session() -> Any:
    """Start one caller-owned Mongo session and transaction."""
    from tools.eos.kernel.db import get_client

    client = get_client()
    if client is None:
        raise _ReasoningHTTPError("C1B_REASONING_PERSISTENCE_UNAVAILABLE", status.HTTP_503_SERVICE_UNAVAILABLE)
    try:
        session = client.start_session()
        session.start_transaction()
        return session
    except Exception as error:
        raise _ReasoningHTTPError("C1B_REASONING_TRANSACTION_UNAVAILABLE", status.HTTP_503_SERVICE_UNAVAILABLE) from error


def _retryable(error: BaseException) -> bool:
    """Recognize only governed whole-transaction retry signals."""
    has_label = getattr(error, "has_error_label", None)
    if callable(has_label):
        try:
            if has_label("TransientTransactionError"):
                return True
            if has_label("UnknownTransactionCommitResult"):
                return False
        except Exception:
            pass
    code = str(getattr(error, "code", "") or error)
    text = f"{code} {error}".upper()
    return any(token in text for token in ("TRANSIENT", "RETRY_TRANSACTION", "UNKNOWN_COMMIT"))


def _transaction(callback: Callable[[Any], Any], *, retries: int = 2) -> Any:
    """Run a bounded caller transaction; never expose an uncertain commit."""
    last: BaseException | None = None
    for attempt in range(retries + 1):
        session: Any = None
        try:
            session = _start_session()
            result = callback(session)
            try:
                session.commit_transaction()
            except Exception as error:
                raise _TransactionUnknown from error
            return result
        except _TransactionUnknown as error:
            # A commit whose outcome is unknown is never retried: the caller
            # cannot prove whether durable state exists, so provider execution
            # must remain at zero and reconciliation can adjudicate safely.
            last = error
            raise _ReasoningHTTPError("C1B_TRANSACTION_OUTCOME_UNCERTAIN", status.HTTP_503_SERVICE_UNAVAILABLE) from error
        except Exception as error:
            last = error
            if attempt < retries and _retryable(error):
                continue
            if isinstance(error, _ReasoningHTTPError):
                raise
            raise error
        finally:
            if session is not None:
                try:
                    marker = getattr(session, "in_transaction", False)
                    active = marker() if callable(marker) else marker
                    if active is True:
                        session.abort_transaction()
                except Exception:
                    pass
                try:
                    session.end_session()
                except Exception:
                    pass
    raise RuntimeError("transaction did not execute") from last


def _identity_digest(tenant_id: str, principal_id: str, idempotency_key: str) -> str:
    """Derive stable internal identities from authorized scope and replay key."""
    payload = {"tenant_id": tenant_id, "principal_id": principal_id, "idempotency_key": idempotency_key}
    return hashlib.sha3_512(json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")).hexdigest()


def _ids(context: TenantAuthorizationContext, key: str) -> tuple[str, str, str, str]:
    """Return bounded admission, invocation, correlation, and internal key."""
    digest = _identity_digest(context.tenant_id, context.identity.identity_id, key)
    return (
        f"c1b-adm-{digest[:48]}",
        f"c1b-inv-{digest[48:96]}",
        f"c1b-correlation-{digest[:40]}",
        f"c1b-http-{digest[40:88]}",
    )


def _validate_key(value: str | None) -> str:
    """Require a bounded opaque replay locator."""
    if not isinstance(value, str) or _KEY.fullmatch(value) is None:
        raise _ReasoningHTTPError("C1B_IDEMPOTENCY_KEY_INVALID", status.HTTP_422_UNPROCESSABLE_ENTITY)
    return value


def _utc_now() -> datetime:
    """Return a BSON-stable UTC instant (Mongo dates have millisecond precision)."""
    return datetime.now(timezone.utc).replace(microsecond=0)


def _error_response(error: BaseException) -> HTTPException:
    """Translate governed failures without exposing exception material."""
    if isinstance(error, _ReasoningHTTPError):
        return HTTPException(status_code=error.http_status, detail=error.code)
    code = str(getattr(error, "code", ""))
    if "DIVERGENT" in code or "REEXECUTION" in code or "REPLAY" in code:
        return HTTPException(status_code=status.HTTP_409_CONFLICT, detail="C1B_REASONING_REPLAY_CONFLICT")
    if "CAPACITY" in code or "EXHAUSTED" in code:
        return HTTPException(status_code=status.HTTP_429_TOO_MANY_REQUESTS, detail="C1B_REASONING_CAPACITY_EXHAUSTED")
    if "NOT_FOUND" in code or "ENTITLEMENT" in code:
        return HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="C1B_REASONING_NOT_AUTHORIZED")
    if isinstance(error, WilsyAIReasoningOrchestratorError):
        return HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="C1B_REASONING_UNAVAILABLE")
    return HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="C1B_REASONING_UNAVAILABLE")


async def get_reasoning_provider_binding(request: Request) -> ServerOwnedModelProviderBinding | None:
    """Read only the server/application-owned provider binding."""
    binding = getattr(request.app.state, "wilsy_ai_reasoning_provider_binding", None)
    return binding if isinstance(binding, ServerOwnedModelProviderBinding) else None


router = APIRouter(prefix="/wilsy-ai", tags=["WILSY AI Reasoning"])


@router.post("/reasoning")
async def execute_reasoning(
    request: WilsyAIReasoningRequest,
    context: TenantAuthorizationContext = Depends(_REASONING_AUTH),
    idempotency_key: str | None = Header(default=None, alias="Idempotency-Key"),
    provider_binding: ServerOwnedModelProviderBinding | None = Depends(get_reasoning_provider_binding),
) -> dict[str, object]:
    """Reserve, claim, execute once outside Mongo, and finalize evidence."""
    try:
        key = _validate_key(idempotency_key)
    except _ReasoningHTTPError as error:
        raise _error_response(error)
    if provider_binding is None:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="C1B_PROVIDER_BINDING_MISSING")
    admission_id, invocation_id, correlation_id, internal_key = _ids(context, key)
    now = _utc_now()
    try:
        collections = _collections()
        admission_registry = WilsyAIUsageAdmissionRegistry(collections["admission"])
        invocation_registry = AIModelInvocationRegistry(collections["invocation"])
        observation_registry = WilsyAIUsageObservationRegistry(collections["observation"])
        orchestrator = WilsyAIReasoningOrchestrator(
            admission_registry=admission_registry,
            invocation_registry=invocation_registry,
            observation_registry=observation_registry,
            binding=provider_binding,
        )
    except Exception as error:
        raise _error_response(error)

    def pre_provider(session: Any) -> Any:
        entitlement = WilsyAIEntitlementRegistry(collections["entitlement"]).get_by_module(
            tenant_id=context.tenant_id, module_id=MODULE_ID, session=session
        )
        capacity = WilsyAIUsageCapacityOrchestrator.from_collections(
            entitlement_collection=collections["entitlement"], observation_collection=collections["observation"]
        ).derive_capacity(
            tenant_id=context.tenant_id, entitlement_id=entitlement.entitlement_id, as_of=now, session=session
        )
        if capacity.daily_remaining_request_units < 1:
            raise _ReasoningHTTPError("C1B_REASONING_CAPACITY_EXHAUSTED", status.HTTP_429_TOO_MANY_REQUESTS)
        admission_authority = WilsyAIUsageAdmissionAuthority(
            capacity_orchestrator=WilsyAIUsageCapacityOrchestrator.from_collections(
                entitlement_collection=collections["entitlement"], observation_collection=collections["observation"]
            ),
            admission_registry=WilsyAIUsageAdmissionRegistry(collections["admission"]),
        )
        admission_authority.reserve(
            tenant_id=context.tenant_id,
            entitlement_id=entitlement.entitlement_id,
            idempotency_key=internal_key,
            admission_id=admission_id,
            reserved_request_units=1,
            session=session,
            as_of=now,
        )
        return orchestrator.claim(
            tenant_id=context.tenant_id,
            principal_id=context.identity.identity_id,
            admission_id=admission_id,
            invocation_id=invocation_id,
            correlation_id=correlation_id,
            entitlement_id=entitlement.entitlement_id,
            prompt=request.prompt,
            system_policy=SYSTEM_POLICY,
            tool_invocation_evidence_references=(),
            session=session,
            occurred_at=now,
        )

    try:
        permit = _transaction(pre_provider)
    except Exception as error:
        raise _error_response(error)

    try:
        # Use one BSON-stable request instant for the transient completion
        # marker; finalization obtains a fresh instant that is never earlier
        # than claim when requests execute within the same wall-clock second.
        provider_attempt = orchestrator.execute(permit, completed_at=now)
    except Exception as error:
        raise _error_response(error)

    def finalize(session: Any) -> Any:
        return orchestrator.finalize(provider_attempt, session=session, occurred_at=_utc_now())

    try:
        final = _transaction(finalize)
    except Exception as error:
        raise _error_response(error)
    if final.admission.state.value != "COMPLETED" or final.usage_observation is None:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="C1B_REASONING_RECONCILIATION_REQUIRED")
    return {
        "invocation_id": final.invocation_evidence.invocation_id,
        "admission_id": final.admission.admission_id,
        "outcome": provider_attempt.result.outcome.value,
        "response_text": final.response_text,
        "usage_observation_id": final.usage_observation.usage_observation_id,
    }


__all__ = [
    "VERSION",
    "REASONING_PERMISSION",
    "REASONING_OPERATION",
    "SYSTEM_POLICY",
    "WilsyAIReasoningRequest",
    "get_reasoning_provider_binding",
    "execute_reasoning",
    "router",
]

# ARTIFACT: wilsy_ai_reasoning_router.py
# VERSION: v1.0.0-C1B-R19
# AUTHORITY BOUNDARY: authenticated reasoning evidence and usage admission only
# TENANT POSTURE: RequireTenantAuthorization supplies tenant and principal
# FAIL-CLOSED POSTURE: bounded keys, server-owned identities, replay-safe transactions
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively
# END OF WILSY OS SOVEREIGN ARTIFACT
