"""Authenticated tenant commercial agreement HTTP surface.

Draft creation and readback only. Execution and activation require a separately
verified contract-evidence authority and are intentionally not exposed here.
"""
from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from fastapi import APIRouter, Depends, Header, HTTPException
from pydantic import BaseModel, ConfigDict, Field
from pymongo.read_concern import ReadConcern
from pymongo.read_preferences import ReadPreference
from pymongo.write_concern import WriteConcern

from tools.eos.api.tenant_authorization_http import (
    RequireTenantAuthorization,
    TenantAuthorizationContext,
)
from tools.eos.kernel.db import get_client, get_database
from tools.eos.saas.entitlement.commercial_agreement import (
    CommercialAgreement,
    CommercialAgreementError,
    CommercialAgreementState,
    CommercialRenewalMode,
)
from tools.eos.saas.entitlement.commercial_agreement_registry import (
    CURRENT_COLLECTION,
    HISTORY_COLLECTION,
    CommercialAgreementRegistryConflictError,
    CommercialAgreementRegistryError,
    CommercialAgreementRegistryNotFoundError,
    CommercialAgreementRegistryPersistenceUnavailableError,
    CommercialAgreementRegistryPersistedRecordInvalidError,
    create_or_replay,
    ensure_indexes,
    get_current,
    get_history,
)
from tools.eos.saas.entitlement.commercial_offer_catalogue import (
    CommercialOfferId,
    CommercialOfferCatalogueError,
    get_commercial_offer,
)

router = APIRouter(prefix="/commercial/agreements", tags=["Commercial Agreements"])
_READ = RequireTenantAuthorization(
    "tenant:commercial_agreement:read", "commercial_agreement_read"
)
_DRAFT_CREATE = RequireTenantAuthorization(
    "tenant:commercial_agreement:draft:create", "commercial_agreement_draft_create"
)


class CommercialAgreementDraftRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    agreement_id: str = Field(min_length=1, max_length=160)
    offer_id: str
    contract_reference: str = Field(min_length=1, max_length=160)
    contract_version: str = Field(min_length=1, max_length=80)
    counterparty_legal_name: str = Field(min_length=1, max_length=240)
    effective_at: datetime
    expires_at: datetime | None = None
    renewal_mode: CommercialRenewalMode
    notice_days: int = Field(ge=0, le=365)
    termination_terms_reference: str = Field(min_length=1, max_length=160)


def _collections(database: Any) -> tuple[Any, Any]:
    history = database.get_collection(
        HISTORY_COLLECTION,
        write_concern=WriteConcern(w="majority", j=True),
        read_concern=ReadConcern("majority"),
    )
    current = database.get_collection(
        CURRENT_COLLECTION,
        write_concern=WriteConcern(w="majority", j=True),
        read_concern=ReadConcern("majority"),
    )
    return history, current


def _transaction(callback):
    client, database = get_client(), get_database()
    if client is None or database is None:
        raise HTTPException(status_code=503, detail="COMMERCIAL_AGREEMENT_DATABASE_UNAVAILABLE")
    try:
        history, current = _collections(database)
        ensure_indexes(history, current)
        with client.start_session() as session:
            return session.with_transaction(
                lambda tx: callback(history, current, tx),
                read_concern=ReadConcern("snapshot"),
                write_concern=WriteConcern(w="majority", j=True),
                read_preference=ReadPreference.PRIMARY,
            )
    except CommercialAgreementRegistryNotFoundError as error:
        raise HTTPException(status_code=404, detail=error.code) from error
    except CommercialAgreementRegistryConflictError as error:
        raise HTTPException(status_code=409, detail=error.code) from error
    except CommercialAgreementError as error:
        raise HTTPException(status_code=422, detail=str(error)) from error
    except CommercialOfferCatalogueError as error:
        raise HTTPException(status_code=422, detail=str(error)) from error
    except CommercialAgreementRegistryPersistedRecordInvalidError as error:
        raise HTTPException(status_code=503, detail=error.code) from error
    except CommercialAgreementRegistryPersistenceUnavailableError as error:
        raise HTTPException(status_code=503, detail=error.code) from error
    except CommercialAgreementRegistryError as error:
        raise HTTPException(status_code=503, detail=error.code) from error
    except HTTPException:
        raise
    except Exception as error:
        raise HTTPException(status_code=503, detail="COMMERCIAL_AGREEMENT_TRANSACTION_UNAVAILABLE") from error


@router.post("", status_code=201)
async def create_draft(
    body: CommercialAgreementDraftRequest,
    context: TenantAuthorizationContext = Depends(_DRAFT_CREATE),
) -> dict[str, object]:
    """Create one exact-tenant draft; browser tenant and offer fingerprints are not trusted."""
    def create(history, current, session):
        if body.effective_at.tzinfo is None or body.effective_at.utcoffset() is None:
            raise HTTPException(status_code=422, detail="EFFECTIVE_AT_MUST_BE_TIMEZONE_AWARE")
        if body.expires_at is not None and (
            body.expires_at.tzinfo is None or body.expires_at.utcoffset() is None
        ):
            raise HTTPException(status_code=422, detail="EXPIRES_AT_MUST_BE_TIMEZONE_AWARE")
        try:
            offer_id = CommercialOfferId(body.offer_id)
        except (TypeError, ValueError) as error:
            raise HTTPException(status_code=422, detail="COMMERCIAL_OFFER_UNKNOWN") from error
        offer = get_commercial_offer(offer_id)
        agreement = CommercialAgreement(
            tenant_id=context.tenant_id,
            agreement_id=body.agreement_id,
            offer_id=offer.offer_id,
            offer_fingerprint=offer.fingerprint,
            contract_reference=body.contract_reference,
            contract_version=body.contract_version,
            counterparty_legal_name=body.counterparty_legal_name,
            effective_at=body.effective_at,
            expires_at=body.expires_at,
            renewal_mode=body.renewal_mode,
            notice_days=body.notice_days,
            termination_terms_reference=body.termination_terms_reference,
            lifecycle_state=CommercialAgreementState.DRAFT,
        )
        outcome, persisted = create_or_replay(agreement, history, current, session=session)
        return {"outcome": outcome.value, "agreement": persisted.to_dict()}
    return _transaction(create)


@router.get("/{agreement_id}")
async def read_current(
    agreement_id: str,
    context: TenantAuthorizationContext = Depends(_READ),
) -> dict[str, object]:
    """Read the current agreement snapshot under the authenticated tenant scope."""
    def read(history, current, session):
        agreement = get_current(context.tenant_id, agreement_id, history, current, session=session)
        return {"agreement": agreement.to_dict()}
    return _transaction(read)


@router.get("/{agreement_id}/history")
async def read_history(
    agreement_id: str,
    context: TenantAuthorizationContext = Depends(_READ),
) -> dict[str, object]:
    """Read immutable agreement history for the authenticated tenant only."""
    def read(history, current, session):
        items = get_history(context.tenant_id, agreement_id, history, session=session)
        return {"tenant_id": context.tenant_id, "agreement_id": agreement_id,
                "revisions": [item.to_dict() for item in items]}
    return _transaction(read)


__all__ = ["router", "CommercialAgreementDraftRequest"]
