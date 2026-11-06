"""Authenticated tenant commercial agreement execution and bundle authority.

Draft/read access, execution, activation and entitlement readback are separate
IAM operations. Execution evidence is loaded and verified by server-configured
trusted adapters; HTTP bodies can supply only an evidence reference. Missing
trust providers fail closed with 503 and never accept browser-authored proofs.
"""
from __future__ import annotations

from datetime import datetime, timezone
import hashlib
import hmac
import json
from typing import Any, Callable

from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import BaseModel, ConfigDict, Field
from pymongo.errors import DuplicateKeyError, PyMongoError
from pymongo.read_concern import ReadConcern
from pymongo.read_preferences import ReadPreference
from pymongo.write_concern import WriteConcern

from tools.eos.api.tenant_authorization_http import (
    RequireTenantAuthorization,
    TenantAuthorizationContext,
)
from tools.eos.auth.principal_authority_repository import PrincipalAuthorityRepository
from tools.eos.auth.role_assignment_repository import RoleAssignmentRepository
from tools.eos.auth.tenant_authorization_decision_evidence_registry import (
    COLLECTION as AUTHORIZATION_EVIDENCE_COLLECTION,
    TenantAuthorizationDecisionEvidenceRegistry,
)
from tools.eos.auth.tenant_business_role_repository import TenantBusinessRoleRepository
from tools.eos.auth.tenant_membership_repository import TenantMembershipRepository
from tools.eos.kernel.db import get_client, get_database
from tools.eos.saas.billing.subscription_registry import subscriptions_collection
from tools.eos.saas.entitlement.commercial_agreement import (
    CommercialAgreement,
    CommercialAgreementError,
    CommercialAgreementState,
    CommercialRenewalMode,
)
from tools.eos.saas.entitlement.commercial_agreement_execution_verifier import (
    CommercialAgreementExecutionVerificationError,
    CommercialAgreementExecutionVerifier,
)
from tools.eos.saas.entitlement.commercial_agreement_registry import (
    CURRENT_COLLECTION as AGREEMENT_CURRENT_COLLECTION,
    HISTORY_COLLECTION as AGREEMENT_HISTORY_COLLECTION,
    CommercialAgreementRegistryConflictError,
    CommercialAgreementRegistryError,
    CommercialAgreementRegistryNotFoundError,
    CommercialAgreementRegistryPersistenceUnavailableError,
    CommercialAgreementRegistryPersistedRecordInvalidError,
    create_or_replay,
    ensure_indexes as ensure_agreement_indexes,
    get_current,
    get_history,
    transition as transition_agreement,
)
from tools.eos.saas.entitlement.commercial_bundle_activation import (
    CommercialBundleActivationConflictError,
    CommercialBundleActivationError,
    CommercialBundleActivationEvidenceError,
    CommercialBundleActivationPersistenceError,
    CommercialBundleActivationOutcome,
    CommercialBundleReconciliationState,
    VerifiedCommercialAgreementExecutionEvidence,
    activate_commercial_bundle,
    ensure_indexes as ensure_bundle_activation_indexes,
    reconcile_commercial_bundle_activation,
)
from tools.eos.saas.entitlement.commercial_offer_catalogue import (
    CommercialOfferId,
    CommercialOfferCatalogueError,
    get_commercial_offer,
)
from tools.eos.saas.entitlement.tenant_product_entitlement_issuance_orchestrator import (
    TenantProductEntitlementIssuanceAuthorizationError,
    TenantProductEntitlementIssuanceCompositionError,
    TenantProductEntitlementIssuanceEvidenceError,
    TenantProductEntitlementIssuanceInputError,
)
from tools.eos.saas.entitlement.tenant_product_entitlement_registry import (
    CURRENT_COLLECTION as ENTITLEMENT_CURRENT_COLLECTION,
    HISTORY_COLLECTION as ENTITLEMENT_HISTORY_COLLECTION,
    TenantProductEntitlementRegistryError,
    ensure_indexes as ensure_entitlement_indexes,
    get_current as get_current_product_entitlement,
)

router = APIRouter(prefix="/commercial/agreements", tags=["Commercial Agreements"])
_READ = RequireTenantAuthorization(
    "tenant:commercial_agreement:read", "commercial_agreement_read"
)
_DRAFT_CREATE = RequireTenantAuthorization(
    "tenant:commercial_agreement:draft:create", "commercial_agreement_draft_create"
)
_EXECUTE = RequireTenantAuthorization(
    "tenant:commercial_agreement:execute", "commercial_agreement_execute"
)
_ACTIVATE = RequireTenantAuthorization(
    "tenant:commercial_agreement:activate", "commercial_agreement_activate"
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


class CommercialAgreementExecutionRequest(BaseModel):
    """Only a reference to server-held execution evidence is requestable."""

    model_config = ConfigDict(extra="forbid")
    execution_evidence_reference: str = Field(min_length=1, max_length=256)


def _collections(database: Any) -> tuple[Any, Any]:
    history = database.get_collection(
        AGREEMENT_HISTORY_COLLECTION,
        write_concern=WriteConcern(w="majority", j=True),
        read_concern=ReadConcern("majority"),
    )
    current = database.get_collection(
        AGREEMENT_CURRENT_COLLECTION,
        write_concern=WriteConcern(w="majority", j=True),
        read_concern=ReadConcern("majority"),
    )
    return history, current


def _execution_verifier(request: Request) -> CommercialAgreementExecutionVerifier:
    verifier = getattr(request.app.state, "commercial_agreement_execution_verifier", None)
    if not isinstance(verifier, CommercialAgreementExecutionVerifier):
        raise HTTPException(
            status_code=503,
            detail="COMMERCIAL_AGREEMENT_TRUSTED_EXECUTION_VERIFIER_UNAVAILABLE",
        )
    return verifier


def _assert_verified_agreement_binding(
    agreement: Any, verified: VerifiedCommercialAgreementExecutionEvidence
) -> None:
    """Recheck every immutable contract binding at the HTTP authority boundary."""
    if type(verified) is not VerifiedCommercialAgreementExecutionEvidence:
        raise HTTPException(status_code=503, detail="COMMERCIAL_EXECUTION_VERIFIER_CONTRACT_INVALID")
    exact = (
        verified.tenant_id == agreement.tenant_id
        and verified.agreement_id == agreement.agreement_id
        and verified.contract_reference == agreement.contract_reference
        and verified.contract_version == agreement.contract_version
        and hmac.compare_digest(verified.offer_fingerprint, agreement.offer_fingerprint)
    )
    if not exact:
        raise HTTPException(status_code=422, detail="COMMERCIAL_EXECUTION_VERIFIED_EVIDENCE_SCOPE_MISMATCH")


_EXECUTION_VERIFICATION_COLLECTION = "commercial_agreement_execution_verification_receipts"
_EXECUTION_VERIFICATION_SCHEMA = "WILSY-COMMERCIAL-AGREEMENT-EXECUTION-VERIFICATION/V1"


def _sha3(payload: object) -> str:
    return hashlib.sha3_512(
        json.dumps(payload, sort_keys=True, ensure_ascii=False, allow_nan=False,
                   separators=(",", ":")).encode("utf-8")
    ).hexdigest()


def _execution_verification_payload(
    agreement: Any, verified: VerifiedCommercialAgreementExecutionEvidence,
    recorded_at: datetime,
) -> dict[str, object]:
    return {
        "schema": _EXECUTION_VERIFICATION_SCHEMA,
        "tenant_id": agreement.tenant_id,
        "agreement_id": agreement.agreement_id,
        "contract_reference": agreement.contract_reference,
        "contract_version": agreement.contract_version,
        "offer_fingerprint": agreement.offer_fingerprint,
        "execution_evidence_reference": verified.execution_evidence_reference,
        "execution_evidence_fingerprint": verified.execution_evidence_fingerprint,
        "signatory_principal_id": verified.signatory_principal_id,
        "signatory_authority_reference": verified.signatory_authority_reference,
        "signatory_authority_fingerprint": verified.signatory_authority_fingerprint,
        "signed_at": verified.signed_at.astimezone(timezone.utc).isoformat().replace("+00:00", "Z"),
        "verified_at": verified.verified_at.astimezone(timezone.utc).isoformat().replace("+00:00", "Z"),
        "verifier_id": verified.verifier_id,
        "verification_receipt_reference": verified.verification_receipt_reference,
        "verification_receipt_fingerprint": verified.verification_receipt_fingerprint,
        "recorded_at": recorded_at.astimezone(timezone.utc).isoformat().replace("+00:00", "Z"),
    }


def _ensure_execution_verification_indexes(collection: Any) -> None:
    collection.create_index(
        [("tenant_id", 1), ("agreement_id", 1)],
        unique=True, name="commercial_execution_verification_tenant_agreement_unique",
    )
    collection.create_index(
        [("tenant_id", 1), ("verification_receipt_reference", 1)],
        unique=True, name="commercial_execution_verification_receipt_unique",
    )


def _verify_execution_verification_receipt(
    row: Any, agreement: Any, verified: VerifiedCommercialAgreementExecutionEvidence,
) -> None:
    if not isinstance(row, dict):
        raise HTTPException(status_code=503, detail="COMMERCIAL_EXECUTION_VERIFICATION_RECEIPT_INVALID")
    raw = dict(row)
    raw.pop("_id", None)
    record_fingerprint = raw.pop("record_fingerprint", None)
    expected_fields = {
        "schema", "tenant_id", "agreement_id", "contract_reference",
        "contract_version", "offer_fingerprint", "execution_evidence_reference",
        "execution_evidence_fingerprint", "signatory_principal_id",
        "signatory_authority_reference", "signatory_authority_fingerprint",
        "signed_at", "verified_at", "verifier_id",
        "verification_receipt_reference", "verification_receipt_fingerprint",
        "recorded_at",
    }
    if (
        set(raw) != expected_fields
        or raw.get("schema") != _EXECUTION_VERIFICATION_SCHEMA
        or record_fingerprint != _sha3(raw)
        or raw.get("tenant_id") != agreement.tenant_id
        or raw.get("agreement_id") != agreement.agreement_id
        or raw.get("contract_reference") != agreement.contract_reference
        or raw.get("contract_version") != agreement.contract_version
        or raw.get("offer_fingerprint") != agreement.offer_fingerprint
        or raw.get("execution_evidence_reference") != verified.execution_evidence_reference
        or raw.get("execution_evidence_fingerprint") != verified.execution_evidence_fingerprint
        or raw.get("signed_at") != (
            agreement.executed_at.astimezone(timezone.utc).isoformat().replace("+00:00", "Z")
            if agreement.executed_at is not None else None
        )
        or raw.get("signatory_principal_id") != verified.signatory_principal_id
        or raw.get("signatory_authority_reference") != verified.signatory_authority_reference
        or raw.get("signatory_authority_fingerprint") != verified.signatory_authority_fingerprint
        or raw.get("verification_receipt_reference") != verified.verification_receipt_reference
        or raw.get("verification_receipt_fingerprint") != verified.verification_receipt_fingerprint
        or raw.get("verifier_id") != verified.verifier_id
    ):
        raise HTTPException(status_code=503, detail="COMMERCIAL_EXECUTION_VERIFICATION_RECEIPT_DIVERGENCE")


def _transaction(callback: Callable[[Any, Any, Any], Any]) -> Any:
    client, database = get_client(), get_database()
    if client is None or database is None:
        raise HTTPException(status_code=503, detail="COMMERCIAL_AGREEMENT_DATABASE_UNAVAILABLE")
    try:
        history, current = _collections(database)
        ensure_agreement_indexes(history, current)
        execution_receipts = database.get_collection(
            _EXECUTION_VERIFICATION_COLLECTION,
            write_concern=WriteConcern(w="majority", j=True),
            read_concern=ReadConcern("majority"),
        )
        _ensure_execution_verification_indexes(execution_receipts)
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
    except CommercialAgreementExecutionVerificationError as error:
        status = 503 if any(word in error.code for word in ("UNAVAILABLE", "UNTRUSTED")) else 422
        raise HTTPException(status_code=status, detail=error.code) from error
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


def _bundle_transaction(callback: Callable[..., Any]) -> Any:
    """Open one transaction and inject every canonical bundle participant."""
    client, database = get_client(), get_database()
    if client is None or database is None:
        raise HTTPException(status_code=503, detail="COMMERCIAL_BUNDLE_DATABASE_UNAVAILABLE")
    try:
        agreement_history, agreement_current = _collections(database)
        entitlement_history = database.get_collection(
            ENTITLEMENT_HISTORY_COLLECTION,
            write_concern=WriteConcern(w="majority", j=True),
            read_concern=ReadConcern("majority"),
        )
        entitlement_current = database.get_collection(
            ENTITLEMENT_CURRENT_COLLECTION,
            write_concern=WriteConcern(w="majority", j=True),
            read_concern=ReadConcern("majority"),
        )
        receipts = database.get_collection(
            "commercial_bundle_activation_receipts",
            write_concern=WriteConcern(w="majority", j=True),
            read_concern=ReadConcern("majority"),
        )
        authorization = database.get_collection(
            AUTHORIZATION_EVIDENCE_COLLECTION,
            write_concern=WriteConcern(w="majority", j=True),
            read_concern=ReadConcern("majority"),
        )
        ensure_agreement_indexes(agreement_history, agreement_current)
        ensure_entitlement_indexes(entitlement_history, entitlement_current)
        ensure_bundle_activation_indexes(receipts)
        execution_receipts = database.get_collection(
            _EXECUTION_VERIFICATION_COLLECTION,
            write_concern=WriteConcern(w="majority", j=True),
            read_concern=ReadConcern("majority"),
        )
        _ensure_execution_verification_indexes(execution_receipts)
        issuer = TenantAuthorizationDecisionEvidenceRegistry(
            authorization,
            principal_repository=PrincipalAuthorityRepository,
            membership_repository=TenantMembershipRepository,
            role_assignment_repository=RoleAssignmentRepository,
            business_role_repository=TenantBusinessRoleRepository,
        )
        issuer.ensure_indexes()
        with client.start_session() as session:
            return session.with_transaction(
                lambda tx: callback(
                    agreement_history, agreement_current,
                    entitlement_history, entitlement_current,
                    receipts, issuer, tx,
                ),
                read_concern=ReadConcern("snapshot"),
                write_concern=WriteConcern(w="majority", j=True),
                read_preference=ReadPreference.PRIMARY,
            )
    except CommercialAgreementRegistryNotFoundError as error:
        raise HTTPException(status_code=404, detail=error.code) from error
    except (CommercialAgreementRegistryConflictError, CommercialBundleActivationConflictError) as error:
        raise HTTPException(status_code=409, detail=getattr(error, "code", "COMMERCIAL_BUNDLE_CONFLICT")) from error
    except (CommercialBundleActivationEvidenceError, CommercialAgreementExecutionVerificationError) as error:
        code = getattr(error, "code", "COMMERCIAL_BUNDLE_EVIDENCE_INVALID")
        status = 503 if any(word in code for word in ("UNAVAILABLE", "UNTRUSTED")) else 422
        raise HTTPException(status_code=status, detail=code) from error
    except (CommercialBundleActivationPersistenceError, CommercialAgreementRegistryPersistenceUnavailableError) as error:
        raise HTTPException(status_code=503, detail=getattr(error, "code", "COMMERCIAL_BUNDLE_PERSISTENCE_UNAVAILABLE")) from error
    except TenantProductEntitlementIssuanceAuthorizationError as error:
        raise HTTPException(status_code=403, detail=error.code) from error
    except TenantProductEntitlementIssuanceInputError as error:
        raise HTTPException(status_code=422, detail=error.code) from error
    except TenantProductEntitlementIssuanceCompositionError as error:
        raise HTTPException(status_code=422, detail=error.code) from error
    except TenantProductEntitlementIssuanceEvidenceError as error:
        raise HTTPException(status_code=503, detail=error.code) from error
    except (CommercialBundleActivationError, CommercialAgreementRegistryError, TenantProductEntitlementRegistryError) as error:
        raise HTTPException(status_code=503, detail=getattr(error, "code", "COMMERCIAL_BUNDLE_OPERATION_UNAVAILABLE")) from error
    except HTTPException:
        raise
    except Exception as error:
        raise HTTPException(status_code=503, detail="COMMERCIAL_BUNDLE_TRANSACTION_UNAVAILABLE") from error


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


@router.post("/{agreement_id}/execute")
async def execute_agreement(
    agreement_id: str,
    body: CommercialAgreementExecutionRequest,
    request: Request,
    context: TenantAuthorizationContext = Depends(_EXECUTE),
) -> dict[str, object]:
    """Record execution only after server-side signature, mandate and timestamp verification."""
    verifier = _execution_verifier(request)

    def execute(history, current, session):
        agreement = get_current(context.tenant_id, agreement_id, history, current, session=session)
        verified = verifier.verify(
            agreement=agreement,
            evidence_reference=body.execution_evidence_reference,
        )
        _assert_verified_agreement_binding(agreement, verified)
        if verified.signatory_principal_id != context.identity.identity_id:
            raise HTTPException(status_code=403, detail="COMMERCIAL_AGREEMENT_SIGNATORY_MUST_MATCH_AUTHENTICATED_PRINCIPAL")
        database = get_database()
        if database is None:
            raise HTTPException(status_code=503, detail="COMMERCIAL_AGREEMENT_DATABASE_UNAVAILABLE")
        execution_receipts = database.get_collection(
            _EXECUTION_VERIFICATION_COLLECTION,
            write_concern=WriteConcern(w="majority", j=True),
            read_concern=ReadConcern("majority"),
        )
        existing_receipt = execution_receipts.find_one(
            {"tenant_id": context.tenant_id, "agreement_id": agreement_id},
            session=session,
        )
        if agreement.lifecycle_state is CommercialAgreementState.EXECUTED:
            if (
                agreement.execution_evidence_reference == verified.execution_evidence_reference
                and agreement.execution_evidence_fingerprint == verified.execution_evidence_fingerprint
                and existing_receipt is not None
            ):
                _verify_execution_verification_receipt(existing_receipt, agreement, verified)
                return {"outcome": "IDEMPOTENT_REPLAY", "agreement": agreement.to_dict()}
            raise HTTPException(status_code=409, detail="COMMERCIAL_AGREEMENT_EXECUTION_REPLAY_CONFLICT")
        if agreement.lifecycle_state is not CommercialAgreementState.DRAFT:
            raise HTTPException(status_code=409, detail="COMMERCIAL_AGREEMENT_NOT_EXECUTABLE")
        if existing_receipt is not None:
            raise HTTPException(status_code=503, detail="COMMERCIAL_EXECUTION_RECEIPT_WITHOUT_EXECUTION")
        _, persisted = transition_agreement(
            tenant_id=context.tenant_id,
            agreement_id=agreement_id,
            target_state=CommercialAgreementState.EXECUTED,
            expected_revision=agreement.lifecycle_revision,
            evidence_reference=verified.execution_evidence_reference,
            evidence_fingerprint=verified.execution_evidence_fingerprint,
            occurred_at=verified.signed_at,
            history_collection=history,
            current_collection=current,
            session=session,
        )
        payload = _execution_verification_payload(
            agreement, verified, datetime.now(timezone.utc)
        )
        document = {**payload, "record_fingerprint": _sha3(payload)}
        try:
            execution_receipts.insert_one(document, session=session)
        except DuplicateKeyError as error:
            raise HTTPException(status_code=409, detail="COMMERCIAL_EXECUTION_VERIFICATION_RECEIPT_CONFLICT") from error
        except PyMongoError as error:
            raise HTTPException(status_code=503, detail="COMMERCIAL_EXECUTION_VERIFICATION_RECEIPT_PERSISTENCE_UNAVAILABLE") from error
        return {
            "outcome": "EXECUTED",
            "verification_receipt_reference": verified.verification_receipt_reference,
            "verification_receipt_fingerprint": verified.verification_receipt_fingerprint,
            "agreement": persisted.to_dict(),
        }
    return _transaction(execute)


@router.post("/{agreement_id}/activate")
async def activate_agreement(
    agreement_id: str,
    body: CommercialAgreementExecutionRequest,
    request: Request,
    context: TenantAuthorizationContext = Depends(_ACTIVATE),
) -> dict[str, object]:
    """Atomically activate the verified agreement and issue every mapped product."""
    verifier = _execution_verifier(request)

    def activate(history, current, entitlement_history, entitlement_current, receipts, issuer, session):
        agreement = get_current(context.tenant_id, agreement_id, history, current, session=session)
        # Do not reject ACTIVE before checking the durable activation receipt:
        # the activation service owns exact replay validation and reconciliation.
        # It still rejects non-executable states when no matching receipt exists.
        verified = verifier.verify(
            agreement=agreement,
            evidence_reference=body.execution_evidence_reference,
        )
        _assert_verified_agreement_binding(agreement, verified)
        database = get_database()
        if database is None:
            raise HTTPException(status_code=503, detail="COMMERCIAL_AGREEMENT_DATABASE_UNAVAILABLE")
        execution_receipts = database.get_collection(
            _EXECUTION_VERIFICATION_COLLECTION,
            write_concern=WriteConcern(w="majority", j=True),
            read_concern=ReadConcern("majority"),
        )
        verification_row = execution_receipts.find_one(
            {"tenant_id": context.tenant_id, "agreement_id": agreement_id},
            session=session,
        )
        if verification_row is None:
            raise HTTPException(status_code=409, detail="COMMERCIAL_AGREEMENT_EXECUTION_VERIFICATION_RECEIPT_REQUIRED")
        _verify_execution_verification_receipt(verification_row, agreement, verified)
        outcome, receipt = activate_commercial_bundle(
            identity=context.identity,
            agreement_id=agreement_id,
            verified_execution_evidence=verified,
            occurred_at=datetime.now(timezone.utc),
            agreement_history_collection=history,
            agreement_current_collection=current,
            subscription_collection=subscriptions_collection,
            entitlement_history_collection=entitlement_history,
            entitlement_current_collection=entitlement_current,
            authorization_evidence_registry=issuer,
            receipt_collection=receipts,
            session=session,
        )
        return {"outcome": outcome.value, "activation_receipt": receipt.to_document()}
    return _bundle_transaction(activate)


@router.get("/{agreement_id}/entitlements")
async def read_activated_entitlements(
    agreement_id: str,
    context: TenantAuthorizationContext = Depends(_READ),
) -> dict[str, object]:
    """Read receipt-correlated active product entitlements for the authenticated tenant."""
    def read(history, current, session):
        database = get_database()
        if database is None:
            raise HTTPException(status_code=503, detail="COMMERCIAL_BUNDLE_DATABASE_UNAVAILABLE")
        entitlement_history = database.get_collection(ENTITLEMENT_HISTORY_COLLECTION)
        entitlement_current = database.get_collection(ENTITLEMENT_CURRENT_COLLECTION)
        receipts = database.get_collection("commercial_bundle_activation_receipts")
        state, receipt = reconcile_commercial_bundle_activation(
            tenant_id=context.tenant_id,
            agreement_id=agreement_id,
            agreement_history_collection=history,
            agreement_current_collection=current,
            entitlement_history_collection=entitlement_history,
            entitlement_current_collection=entitlement_current,
            receipt_collection=receipts,
            session=session,
        )
        if state is not CommercialBundleReconciliationState.COMMITTED or receipt is None:
            raise HTTPException(status_code=404, detail="COMMERCIAL_BUNDLE_ACTIVATION_NOT_COMMITTED")
        products = []
        for item in receipt.product_entitlements:
            entitlement = get_current_product_entitlement(
                context.tenant_id, item["entitlement_id"],
                entitlement_history, entitlement_current, session=session,
            )
            if (
                entitlement.lifecycle_state.value != "ACTIVE"
                or entitlement.fingerprint != item["entitlement_fingerprint"]
                or entitlement.product_id.value != item["product_id"]
            ):
                raise HTTPException(status_code=503, detail="COMMERCIAL_BUNDLE_ENTITLEMENT_READBACK_DIVERGENCE")
            products.append({
                "product_id": entitlement.product_id.value,
                "entitlement_id": entitlement.entitlement_id,
                "lifecycle_state": entitlement.lifecycle_state.value,
                "fingerprint": entitlement.fingerprint,
            })
        return {
            "tenant_id": context.tenant_id,
            "agreement_id": agreement_id,
            "activation_receipt_fingerprint": receipt.fingerprint,
            "product_entitlements": products,
        }
    return _transaction(read)


__all__ = [
    "router",
    "CommercialAgreementDraftRequest",
    "CommercialAgreementExecutionRequest",
]
