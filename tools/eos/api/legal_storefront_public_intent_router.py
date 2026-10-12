"""Public HTTP admission for immutable Legal Storefront acquisition intent.

TITLE: Legal Storefront Public Intent HTTP Admission
VERSION: v1.0.0-L8-9C-LEGAL-STOREFRONT-PUBLIC-INTENT-HTTP
AUTHORITY: Wilsy OS Core Governance / Python EOS Legal Operations
EPITOME: Admit one bounded anonymous Legal Storefront acquisition request by
         issuing server-owned intent identity/time, enforcing durable pre-tenant
         request density, and persisting immutable L8-9A intent evidence through
         the L8-9B registry without creating tenant, identity, Legal lifecycle,
         commercial, AI, payment or settlement authority.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tools/eos/api/legal_storefront_public_intent_router.py
COLLABORATION / OWNERSHIP: L8-9A owns immutable intent semantics; L8-9B owns
                            durable intent persistence; L8-9C0 owns pre-tenant
                            request-density capability; this file owns HTTP
                            transport/orchestration only.
CERTIFICATION / UPDATE DATE: 2026-10-12
CHANGELOG: 2026-10-12 v1.0.0-L8-9C-LEGAL-STOREFRONT-PUBLIC-INTENT-HTTP
           establishes bounded POST admission at
           /legal-storefront/public-intents with server-generated UUID intent
           identity, server-owned UTC submission time, normalized-contact
           SHA3-512 rate subject, durable L8-9C0 throttling, caller-owned Mongo
           transaction for L8-9B persistence, bounded 202 projection and
           fail-closed error mapping.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2; ISO 27001.
SECURITY / PRIVACY POSTURE: Request body is restricted to the exact L8-9A
                             descriptive acquisition fields. No password,
                             credential, secret, API key, tenant selector,
                             principal, role, plan, subscription, entitlement,
                             Legal instruction, payment or settlement field is
                             accepted. Rate limiting receives only SHA3-512 of
                             the already-normalized contact email.
TENANT BOUNDARY: Explicitly pre-tenant. No tenant_id is accepted, derived,
                 persisted, returned or created by this route.
AUTHORITY BOUNDARY: HTTP admission and orchestration only. Acceptance proves
                    only durable public acquisition intent. It does not verify
                    identity/contact ownership, create users/tenants, assign
                    roles, provision products, admit Legal lifecycle commands,
                    send notifications, or establish billing/payment truth.
AI AUTHORITY BOUNDARY: WILSY AI is not invoked by anonymous admission. Durable
                       intent evidence may become downstream observable input
                       only through a separately governed intelligence seam.
TRANSACTION BOUNDARY: L8-9C0 rate counting is its own certified atomic Mongo
                      operation. L8-9B persistence runs inside one caller-owned
                      Mongo transaction created/committed/aborted here.
FINANCIAL AUTHORITY BOUNDARY: None. Kennel EOS remains the exclusive financial
                              execution authority.
FAIL-CLOSED DECLARATION: Invalid request/domain state returns bounded 422,
                         throttling returns 429, persistence/runtime failure
                         returns 503, and no failure path fabricates acceptance.
"""

from __future__ import annotations

from datetime import datetime, timezone
import hashlib
import uuid
from typing import Any, Final

from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, ConfigDict, StrictStr

from tools.eos.kernel.db import get_client, get_database
from tools.eos.legal_operations.domain.legal_storefront_public_intent import (
    LegalStorefrontPublicIntentError,
    create_legal_storefront_public_intent,
)
from tools.eos.legal_operations.registry.legal_storefront_public_intent_registry import (
    COLLECTION as INTENT_COLLECTION,
    LegalStorefrontPublicIntentRegistry,
    LegalStorefrontPublicIntentRegistryError,
    LegalStorefrontPublicIntentRegistryRetryTransactionError,
)
from tools.eos.legal_operations.service.legal_storefront_public_intent_rate_limit import (
    COLLECTION as RATE_COLLECTION,
    LegalStorefrontPublicIntentRateLimit,
    LegalStorefrontPublicIntentRateLimitDependencyError,
    LegalStorefrontPublicIntentRateLimitError,
    LegalStorefrontPublicIntentRateLimitedError,
)


VERSION: Final[str] = (
    "v1.0.0-L8-9C-LEGAL-STOREFRONT-PUBLIC-INTENT-HTTP"
)

router = APIRouter(
    prefix="/legal-storefront",
    tags=["Legal Storefront"],
)


class LegalStorefrontPublicIntentRequest(BaseModel):
    """Exact anonymous request body accepted by L8-9C.

    This transport object owns no domain normalization, identity, tenant,
    subscription, Legal lifecycle, AI, billing or financial authority.
    """

    model_config = ConfigDict(extra="forbid", strict=True)

    organization_name: StrictStr
    contact_email: StrictStr
    industry: StrictStr
    region: StrictStr


def _now() -> datetime:
    """Return one server-owned timezone-aware UTC submission observation."""
    return datetime.now(timezone.utc)


def _intent_id() -> str:
    """Return one opaque server-issued L8-9A-compatible intent identifier."""
    return f"WILSY-LSI-{uuid.uuid4().hex}"


def _rate_subject(contact_email: str) -> str:
    """Derive an opaque SHA3-512 rate subject from normalized contact metadata.

    The caller never supplies this digest directly. Raw contact data is not
    persisted by L8-9C0.
    """
    return hashlib.sha3_512(
        contact_email.encode("utf-8")
    ).hexdigest()


def _handles() -> tuple[Any, Any]:
    """Resolve existing Kernel Mongo handles lazily for request execution."""
    return get_client(), get_database()


def _admit_in_transaction(
    *,
    database: Any,
    session: Any,
    intent: Any,
) -> Any:
    """Persist one immutable L8-9A intent through L8-9B in caller transaction."""
    registry = LegalStorefrontPublicIntentRegistry(
        database[INTENT_COLLECTION]
    )
    return registry.create_or_replay(
        intent,
        session=session,
    )


@router.post(
    "/public-intents",
    status_code=status.HTTP_202_ACCEPTED,
)
async def submit_legal_storefront_public_intent(
    request: LegalStorefrontPublicIntentRequest,
) -> dict[str, str]:
    """Accept and durably record one bounded pre-tenant Storefront intent.

    The route issues intent identity/time server-side, validates immutable
    L8-9A semantics, derives an opaque SHA3-512 request-density subject from
    the normalized contact email, applies L8-9C0 throttling, then persists the
    immutable intent under one caller-owned Mongo transaction via L8-9B.

    A successful 202 response means only that immutable public-intent evidence
    was durably admitted. It does not authenticate contact ownership, create a
    principal/tenant, grant access, select a product or plan, establish a Legal
    instruction/matter/document, call WILSY AI, send a notification, or create
    billing/payment/settlement truth.
    """
    submitted_at = _now()

    try:
        intent = create_legal_storefront_public_intent(
            intent_id=_intent_id(),
            organization_name=request.organization_name,
            contact_email=request.contact_email,
            industry=request.industry,
            region=request.region,
            submitted_at=submitted_at,
        )
    except LegalStorefrontPublicIntentError as error:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail={"code": str(error)},
        ) from error

    client, database = _handles()
    if client is None or database is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail={"code": "L8_9C_PERSISTENCE_UNAVAILABLE"},
        )

    rate_gate = LegalStorefrontPublicIntentRateLimit(
        database[RATE_COLLECTION]
    )

    try:
        rate_gate.require_allowed(
            subject_digest=_rate_subject(intent.contact_email),
            observed_at=submitted_at,
        )
    except LegalStorefrontPublicIntentRateLimitedError as error:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail={"code": error.code},
        ) from error
    except (
        LegalStorefrontPublicIntentRateLimitDependencyError,
        LegalStorefrontPublicIntentRateLimitError,
    ) as error:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail={"code": error.code},
        ) from error

    try:
        with client.start_session() as session:
            session.start_transaction()
            try:
                persisted = _admit_in_transaction(
                    database=database,
                    session=session,
                    intent=intent,
                )
                session.commit_transaction()
            except Exception:
                if bool(getattr(session, "in_transaction", False)):
                    session.abort_transaction()
                raise
    except LegalStorefrontPublicIntentRegistryRetryTransactionError as error:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail={"code": error.code},
        ) from error
    except LegalStorefrontPublicIntentRegistryError as error:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail={"code": error.code},
        ) from error
    except HTTPException:
        raise
    except Exception as error:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail={"code": "L8_9C_PERSISTENCE_UNAVAILABLE"},
        ) from error

    return {
        "status": "ACCEPTED",
        "intentId": persisted.intent_id,
    }


__all__ = [
    "VERSION",
    "LegalStorefrontPublicIntentRequest",
    "router",
    "submit_legal_storefront_public_intent",
]


# ARTIFACT: legal_storefront_public_intent_router.py
# VERSION: v1.0.0-L8-9C-LEGAL-STOREFRONT-PUBLIC-INTENT-HTTP
# AUTHORITY BOUNDARY: anonymous HTTP admission/orchestration only; 202 proves durable public intent, not identity, tenant, Legal lifecycle, AI, commercial or financial authority
# TENANT POSTURE: pre-tenant; tenant_id is neither accepted, derived, persisted nor returned
# TRANSACTION POSTURE: L8-9C0 owns atomic rate write; this adapter owns the L8-9B Mongo transaction
# PRIVACY POSTURE: request body is exact bounded acquisition metadata; rate gate receives SHA3-512 normalized contact only
# AI POSTURE: WILSY AI is not invoked; downstream intelligence requires a separately governed evidence-consumption seam
# FAIL-CLOSED POSTURE: malformed input, throttling, unavailable persistence, retry/corruption and unexpected runtime failure never fabricate acceptance
# FINANCIAL EXECUTION AUTHORITY: none; Kennel EOS remains exclusive
# END OF WILSY OS SOVEREIGN ARTIFACT
