"""Atomic commercial bundle activation and unknown-commit reconciliation.

This service is transaction-participant only: callers own the active Mongo
transaction. A server-side signature verifier must produce the verified
execution-evidence value; browser payloads cannot construct or supply it.
Agreement execution, every product entitlement, and the immutable activation
receipt are committed or aborted together.
"""
from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from datetime import datetime, timezone
from enum import StrEnum
import hashlib
import hmac
import json
from typing import Any, Final

from pymongo import ASCENDING
from pymongo.errors import DuplicateKeyError, PyMongoError
from pymongo.read_concern import ReadConcern
from pymongo.write_concern import WriteConcern

from tools.eos.auth.identity import SovereignIdentity
from tools.eos.auth.principal_status import PrincipalStatus
from tools.eos.saas.entitlement.commercial_agreement import (
    CommercialAgreement,
    CommercialAgreementState,
)
from tools.eos.saas.entitlement.commercial_agreement_registry import (
    get_current as get_current_agreement,
    transition as transition_agreement,
    CommercialAgreementRegistryError,
    CommercialAgreementRegistryConflictError,
    CommercialAgreementRegistryNotFoundError,
)
from tools.eos.saas.entitlement.commercial_bundle_readiness import (
    CommercialBundleReadinessState,
    assess_commercial_bundle_readiness,
)
from tools.eos.saas.entitlement.commercial_offer_catalogue import (
    CommercialOfferKind,
    get_commercial_offer,
)
from tools.eos.saas.entitlement.tenant_product_entitlement_composer import (
    derive_tenant_product_entitlement_id,
)
from tools.eos.saas.entitlement.tenant_product_entitlement_issuance_orchestrator import (
    issue_tenant_product_entitlement,
)
from tools.eos.saas.entitlement.tenant_product_entitlement_registry import (
    get_current as get_current_product_entitlement,
    TenantProductEntitlementRegistryError,
    TenantProductEntitlementRegistryNotFoundError,
    TenantProductEntitlementRegistryPersistedRecordInvalidError,
)
from tools.eos.saas.domain.tenant_product_entitlement import (
    TenantProductEntitlementState,
)


VERSION: Final[str] = "v1.0.0-EOS-ATOMIC-COMMERCIAL-BUNDLE-ACTIVATION"
SCHEMA: Final[str] = "WILSY-COMMERCIAL-BUNDLE-ACTIVATION-RECEIPT/V1"
COLLECTION: Final[str] = "commercial_bundle_activation_receipts"
INDEX_NAME: Final[str] = "commercial_bundle_tenant_agreement_unique"
FINGERPRINT_INDEX_NAME: Final[str] = "commercial_bundle_tenant_fingerprint_unique"
WRITE_CONCERN: Final[WriteConcern] = WriteConcern(w="majority", j=True)
READ_CONCERN: Final[ReadConcern] = ReadConcern("majority")


class CommercialBundleActivationError(RuntimeError):
    """Fail-closed bundle activation or reconciliation error."""

    def __init__(self, code: str) -> None:
        self.code = code
        super().__init__(code)


class CommercialBundleActivationTransactionRequiredError(CommercialBundleActivationError):
    pass


class CommercialBundleActivationEvidenceError(CommercialBundleActivationError):
    pass


class CommercialBundleActivationConflictError(CommercialBundleActivationError):
    pass


class CommercialBundleActivationPersistenceError(CommercialBundleActivationError):
    pass


class CommercialBundleActivationOutcome(StrEnum):
    ACTIVATED = "ACTIVATED"
    IDEMPOTENT_REPLAY = "IDEMPOTENT_REPLAY"


class CommercialBundleReconciliationState(StrEnum):
    COMMITTED = "COMMITTED"
    NOT_COMMITTED = "NOT_COMMITTED"
    DIVERGED = "DIVERGED"


def _text(value: object, code: str, maximum: int = 256) -> str:
    if not isinstance(value, str) or not value or value != value.strip() or len(value) > maximum:
        raise CommercialBundleActivationError(code)
    return value


def _fingerprint(value: object, code: str) -> str:
    if not isinstance(value, str) or len(value) != 128 or any(c not in "0123456789abcdef" for c in value):
        raise CommercialBundleActivationError(code)
    return value


def _timestamp(value: object, code: str) -> datetime:
    if not isinstance(value, datetime) or value.tzinfo is None or value.utcoffset() is None:
        raise CommercialBundleActivationError(code)
    return value.astimezone(timezone.utc)


def _sha3(value: object) -> str:
    return hashlib.sha3_512(
        json.dumps(value, sort_keys=True, ensure_ascii=False, allow_nan=False,
                   separators=(",", ":")).encode("utf-8")
    ).hexdigest()


def _active_transaction(session: Any) -> Any:
    marker = getattr(session, "in_transaction", None)
    try:
        active = marker() if callable(marker) else marker
    except (AttributeError, TypeError):
        active = False
    if active is not True:
        raise CommercialBundleActivationTransactionRequiredError(
            "COMMERCIAL_BUNDLE_ACTIVE_TRANSACTION_REQUIRED"
        )
    return session


@dataclass(frozen=True, slots=True)
class VerifiedCommercialAgreementExecutionEvidence:
    """Server-side verifier result; never accepted from an HTTP request body.

    A trusted signature adapter creates this value only after verifying the
    executed document, signatory identity/mandate, signature and evidence chain.
    The activation service rechecks every agreement binding before mutation.
    """

    tenant_id: str
    agreement_id: str
    contract_reference: str
    contract_version: str
    offer_fingerprint: str
    execution_evidence_reference: str
    execution_evidence_fingerprint: str
    signatory_principal_id: str
    signatory_authority_reference: str
    signatory_authority_fingerprint: str
    signed_at: datetime
    verified_at: datetime
    verifier_id: str
    verification_receipt_reference: str
    verification_receipt_fingerprint: str

    def __post_init__(self) -> None:
        for value, code in (
            (self.tenant_id, "COMMERCIAL_BUNDLE_EVIDENCE_TENANT_INVALID"),
            (self.agreement_id, "COMMERCIAL_BUNDLE_EVIDENCE_AGREEMENT_INVALID"),
            (self.contract_reference, "COMMERCIAL_BUNDLE_EVIDENCE_CONTRACT_INVALID"),
            (self.contract_version, "COMMERCIAL_BUNDLE_EVIDENCE_VERSION_INVALID"),
            (self.signatory_principal_id, "COMMERCIAL_BUNDLE_SIGNATORY_INVALID"),
            (self.signatory_authority_reference, "COMMERCIAL_BUNDLE_SIGNATORY_AUTHORITY_INVALID"),
            (self.verifier_id, "COMMERCIAL_BUNDLE_VERIFIER_INVALID"),
            (self.verification_receipt_reference, "COMMERCIAL_BUNDLE_VERIFICATION_REFERENCE_INVALID"),
            (self.execution_evidence_reference, "COMMERCIAL_BUNDLE_EXECUTION_REFERENCE_INVALID"),
        ):
            _text(value, code)
        for value, code in (
            (self.offer_fingerprint, "COMMERCIAL_BUNDLE_OFFER_FINGERPRINT_INVALID"),
            (self.execution_evidence_fingerprint, "COMMERCIAL_BUNDLE_EXECUTION_FINGERPRINT_INVALID"),
            (self.signatory_authority_fingerprint, "COMMERCIAL_BUNDLE_SIGNATORY_FINGERPRINT_INVALID"),
            (self.verification_receipt_fingerprint, "COMMERCIAL_BUNDLE_VERIFICATION_FINGERPRINT_INVALID"),
        ):
            _fingerprint(value, code)
        _timestamp(self.signed_at, "COMMERCIAL_BUNDLE_SIGNED_AT_INVALID")
        _timestamp(self.verified_at, "COMMERCIAL_BUNDLE_VERIFIED_AT_INVALID")
        if self.verified_at < self.signed_at:
            raise CommercialBundleActivationEvidenceError(
                "COMMERCIAL_BUNDLE_VERIFICATION_CHRONOLOGY_INVALID"
            )


@dataclass(frozen=True, slots=True)
class CommercialBundleActivationReceipt:
    tenant_id: str
    agreement_id: str
    offer_id: str
    offer_fingerprint: str
    agreement_fingerprint: str
    agreement_revision: int
    activation_evidence_reference: str
    activation_evidence_fingerprint: str
    execution_evidence_reference: str
    execution_evidence_fingerprint: str
    activated_at: datetime
    product_entitlements: tuple[dict[str, str], ...]
    schema: str = SCHEMA
    version: str = VERSION
    fingerprint: str = ""

    def payload(self) -> dict[str, object]:
        return {
            "schema": self.schema,
            "version": self.version,
            "tenant_id": self.tenant_id,
            "agreement_id": self.agreement_id,
            "offer_id": self.offer_id,
            "offer_fingerprint": self.offer_fingerprint,
            "agreement_fingerprint": self.agreement_fingerprint,
            "agreement_revision": self.agreement_revision,
            "activation_evidence_reference": self.activation_evidence_reference,
            "activation_evidence_fingerprint": self.activation_evidence_fingerprint,
            "execution_evidence_reference": self.execution_evidence_reference,
            "execution_evidence_fingerprint": self.execution_evidence_fingerprint,
            "activated_at": self.activated_at.astimezone(timezone.utc).isoformat().replace("+00:00", "Z"),
            "product_entitlements": [dict(item) for item in self.product_entitlements],
        }

    def to_document(self) -> dict[str, object]:
        payload = self.payload()
        payload["fingerprint"] = self.fingerprint or _sha3(payload)
        return payload


def _receipt_collection(collection: Any) -> Any:
    if collection is None:
        raise CommercialBundleActivationPersistenceError(
            "COMMERCIAL_BUNDLE_RECEIPT_COLLECTION_REQUIRED"
        )
    try:
        return collection.with_options(write_concern=WRITE_CONCERN, read_concern=READ_CONCERN)
    except AttributeError:
        return collection


def ensure_indexes(receipt_collection: Any) -> None:
    target = _receipt_collection(receipt_collection)
    try:
        target.create_index(
            [("tenant_id", ASCENDING), ("agreement_id", ASCENDING)],
            unique=True, name=INDEX_NAME,
        )
        target.create_index(
            [("tenant_id", ASCENDING), ("fingerprint", ASCENDING)],
            unique=True, name=FINGERPRINT_INDEX_NAME,
        )
    except PyMongoError as error:
        raise CommercialBundleActivationPersistenceError(
            "COMMERCIAL_BUNDLE_RECEIPT_INDEX_INSTALL_FAILED"
        ) from error


def _read_receipt(collection: Any, tenant_id: str, agreement_id: str, session: Any) -> Mapping[str, Any] | None:
    try:
        return _receipt_collection(collection).find_one(
            {"tenant_id": tenant_id, "agreement_id": agreement_id}, session=session
        )
    except PyMongoError as error:
        raise CommercialBundleActivationPersistenceError(
            "COMMERCIAL_BUNDLE_RECEIPT_READ_FAILED"
        ) from error


def _hydrate_receipt(row: Mapping[str, Any]) -> CommercialBundleActivationReceipt:
    raw = dict(row)
    raw.pop("_id", None)
    expected = {
        "schema", "version", "tenant_id", "agreement_id", "offer_id",
        "offer_fingerprint", "agreement_fingerprint", "agreement_revision",
        "activation_evidence_reference", "activation_evidence_fingerprint",
        "execution_evidence_reference", "execution_evidence_fingerprint",
        "activated_at", "product_entitlements", "fingerprint",
    }
    if set(raw) != expected or raw.get("schema") != SCHEMA or raw.get("version") != VERSION:
        raise CommercialBundleActivationPersistenceError(
            "COMMERCIAL_BUNDLE_RECEIPT_SCHEMA_INVALID"
        )
    fingerprint = raw.pop("fingerprint")
    if fingerprint != _sha3(raw):
        raise CommercialBundleActivationPersistenceError(
            "COMMERCIAL_BUNDLE_RECEIPT_FINGERPRINT_INVALID"
        )
    try:
        activated_at = datetime.fromisoformat(str(raw["activated_at"]).replace("Z", "+00:00"))
        products = raw["product_entitlements"]
        if not isinstance(products, list) or not all(isinstance(item, Mapping) for item in products):
            raise ValueError("product_entitlements")
        receipt = CommercialBundleActivationReceipt(
            tenant_id=str(raw["tenant_id"]),
            agreement_id=str(raw["agreement_id"]),
            offer_id=str(raw["offer_id"]),
            offer_fingerprint=str(raw["offer_fingerprint"]),
            agreement_fingerprint=str(raw["agreement_fingerprint"]),
            agreement_revision=int(raw["agreement_revision"]),
            activation_evidence_reference=str(raw["activation_evidence_reference"]),
            activation_evidence_fingerprint=str(raw["activation_evidence_fingerprint"]),
            execution_evidence_reference=str(raw["execution_evidence_reference"]),
            execution_evidence_fingerprint=str(raw["execution_evidence_fingerprint"]),
            activated_at=activated_at,
            product_entitlements=tuple(dict(item) for item in products),
            schema=str(raw["schema"]),
            version=str(raw["version"]),
            fingerprint=str(fingerprint),
        )
    except (KeyError, TypeError, ValueError) as error:
        raise CommercialBundleActivationPersistenceError(
            "COMMERCIAL_BUNDLE_RECEIPT_HYDRATION_INVALID"
        ) from error
    if receipt.fingerprint != _sha3(receipt.payload()):
        raise CommercialBundleActivationPersistenceError(
            "COMMERCIAL_BUNDLE_RECEIPT_CORRELATION_INVALID"
        )
    return receipt


def _verify_execution_evidence(
    agreement: CommercialAgreement,
    evidence: VerifiedCommercialAgreementExecutionEvidence,
) -> None:
    if type(evidence) is not VerifiedCommercialAgreementExecutionEvidence:
        raise CommercialBundleActivationEvidenceError(
            "COMMERCIAL_BUNDLE_VERIFIED_EXECUTION_EVIDENCE_REQUIRED"
        )
    exact = (
        evidence.tenant_id == agreement.tenant_id
        and evidence.agreement_id == agreement.agreement_id
        and evidence.contract_reference == agreement.contract_reference
        and evidence.contract_version == agreement.contract_version
        and hmac.compare_digest(evidence.offer_fingerprint, agreement.offer_fingerprint)
        and evidence.execution_evidence_reference == agreement.execution_evidence_reference
        and hmac.compare_digest(
            evidence.execution_evidence_fingerprint,
            agreement.execution_evidence_fingerprint or "",
        )
    )
    if not exact:
        raise CommercialBundleActivationEvidenceError(
            "COMMERCIAL_BUNDLE_EXECUTION_EVIDENCE_DIVERGENCE"
        )


def _receipt_fingerprint_payload(
    agreement: CommercialAgreement,
    evidence: VerifiedCommercialAgreementExecutionEvidence,
    product_receipts: tuple[dict[str, str], ...],
    occurred_at: datetime,
    activation_reference: str,
) -> dict[str, object]:
    return {
        "tenant_id": agreement.tenant_id,
        "agreement_id": agreement.agreement_id,
        "offer_id": str(agreement.offer_id),
        "offer_fingerprint": agreement.offer_fingerprint,
        "execution_evidence_reference": evidence.execution_evidence_reference,
        "execution_evidence_fingerprint": evidence.execution_evidence_fingerprint,
        "signatory_principal_id": evidence.signatory_principal_id,
        "signatory_authority_reference": evidence.signatory_authority_reference,
        "signatory_authority_fingerprint": evidence.signatory_authority_fingerprint,
        "verification_receipt_reference": evidence.verification_receipt_reference,
        "verification_receipt_fingerprint": evidence.verification_receipt_fingerprint,
        "product_entitlements": [dict(item) for item in product_receipts],
        "activated_at": occurred_at.astimezone(timezone.utc).isoformat().replace("+00:00", "Z"),
        "activation_evidence_reference": activation_reference,
    }


def _verify_existing_receipt(
    receipt: CommercialBundleActivationReceipt,
    agreement: CommercialAgreement,
    evidence: VerifiedCommercialAgreementExecutionEvidence,
    history_collection: Any,
    current_collection: Any,
    session: Any,
) -> None:
    _verify_execution_evidence(agreement, evidence)
    offer = get_commercial_offer(agreement.offer_id)
    if (
        agreement.lifecycle_state is not CommercialAgreementState.ACTIVE
        or receipt.agreement_fingerprint != agreement.fingerprint
        or receipt.agreement_revision != agreement.lifecycle_revision
        or receipt.offer_id != offer.offer_id.value
        or receipt.offer_fingerprint != offer.fingerprint
        or receipt.execution_evidence_reference != evidence.execution_evidence_reference
        or receipt.execution_evidence_fingerprint != evidence.execution_evidence_fingerprint
    ):
        raise CommercialBundleActivationConflictError(
            "COMMERCIAL_BUNDLE_EXISTING_RECEIPT_DIVERGENCE"
        )
    if tuple(item.get("product_id") for item in receipt.product_entitlements) != tuple(
        item.value for item in offer.product_ids
    ):
        raise CommercialBundleActivationConflictError(
            "COMMERCIAL_BUNDLE_RECEIPT_PRODUCT_SET_INVALID"
        )
    for item in receipt.product_entitlements:
        entitlement = get_current_product_entitlement(
            agreement.tenant_id,
            item["entitlement_id"],
            history_collection,
            current_collection,
            session=session,
        )
        if (
            entitlement.lifecycle_state is not TenantProductEntitlementState.ACTIVE
            or entitlement.fingerprint != item["entitlement_fingerprint"]
            or entitlement.product_id.value != item["product_id"]
        ):
            raise CommercialBundleActivationConflictError(
                "COMMERCIAL_BUNDLE_ENTITLEMENT_READBACK_DIVERGENCE"
            )


def activate_commercial_bundle(
    *,
    identity: SovereignIdentity,
    agreement_id: str,
    verified_execution_evidence: VerifiedCommercialAgreementExecutionEvidence,
    occurred_at: datetime,
    agreement_history_collection: Any,
    agreement_current_collection: Any,
    subscription_collection: Any,
    entitlement_history_collection: Any,
    entitlement_current_collection: Any,
    authorization_evidence_registry: Any,
    receipt_collection: Any,
    session: Any,
) -> tuple[CommercialBundleActivationOutcome, CommercialBundleActivationReceipt]:
    """Execute agreement and issue all offer products in one caller transaction."""
    tx = _active_transaction(session)
    if not isinstance(identity, SovereignIdentity) or identity.status is not PrincipalStatus.ACTIVE:
        raise CommercialBundleActivationError("COMMERCIAL_BUNDLE_ACTIVE_IDENTITY_REQUIRED")
    tenant_id = _text(identity.tenant_id, "COMMERCIAL_BUNDLE_TENANT_INVALID")
    principal_id = _text(identity.identity_id, "COMMERCIAL_BUNDLE_PRINCIPAL_INVALID")
    agreement_id = _text(agreement_id, "COMMERCIAL_BUNDLE_AGREEMENT_ID_INVALID")
    when = _timestamp(occurred_at, "COMMERCIAL_BUNDLE_OCCURRED_AT_INVALID")
    if verified_execution_evidence.tenant_id != tenant_id or verified_execution_evidence.agreement_id != agreement_id:
        raise CommercialBundleActivationEvidenceError(
            "COMMERCIAL_BUNDLE_VERIFIED_EVIDENCE_SCOPE_MISMATCH"
        )

    agreement = get_current_agreement(
        tenant_id, agreement_id, agreement_history_collection,
        agreement_current_collection, session=tx,
    )
    _verify_execution_evidence(agreement, verified_execution_evidence)
    offer = get_commercial_offer(agreement.offer_id)
    if offer.kind is not CommercialOfferKind.BUNDLE:
        raise CommercialBundleActivationError("COMMERCIAL_BUNDLE_OFFER_REQUIRED")
    readiness = assess_commercial_bundle_readiness(offer.offer_id)
    if readiness.state is not CommercialBundleReadinessState.PRODUCT_MAPPING_COMPLETE:
        raise CommercialBundleActivationError("COMMERCIAL_BUNDLE_PRODUCT_MAPPING_INCOMPLETE")

    existing_row = _read_receipt(receipt_collection, tenant_id, agreement_id, tx)
    if existing_row is not None:
        receipt = _hydrate_receipt(existing_row)
        _verify_existing_receipt(
            receipt, agreement, verified_execution_evidence,
            entitlement_history_collection, entitlement_current_collection, tx,
        )
        return CommercialBundleActivationOutcome.IDEMPOTENT_REPLAY, receipt

    if agreement.lifecycle_state is CommercialAgreementState.DRAFT:
        _, agreement = transition_agreement(
            tenant_id=tenant_id,
            agreement_id=agreement_id,
            target_state=CommercialAgreementState.EXECUTED,
            expected_revision=agreement.lifecycle_revision,
            evidence_reference=verified_execution_evidence.execution_evidence_reference,
            evidence_fingerprint=verified_execution_evidence.execution_evidence_fingerprint,
            occurred_at=verified_execution_evidence.signed_at,
            history_collection=agreement_history_collection,
            current_collection=agreement_current_collection,
            session=tx,
        )
    elif agreement.lifecycle_state is not CommercialAgreementState.EXECUTED:
        raise CommercialBundleActivationConflictError(
            "COMMERCIAL_BUNDLE_AGREEMENT_NOT_EXECUTABLE"
        )

    if (
        agreement.executed_at != verified_execution_evidence.signed_at.astimezone(timezone.utc)
        or agreement.execution_evidence_reference != verified_execution_evidence.execution_evidence_reference
        or agreement.execution_evidence_fingerprint != verified_execution_evidence.execution_evidence_fingerprint
    ):
        raise CommercialBundleActivationEvidenceError(
            "COMMERCIAL_BUNDLE_EXECUTION_EVIDENCE_DIVERGENCE"
        )

    product_receipts: list[dict[str, str]] = []
    for product_id in offer.product_ids:
        result = issue_tenant_product_entitlement(
            identity=identity,
            product_id=product_id,
            idempotency_key=f"bundle-{_sha3([tenant_id, agreement_id, product_id.value])[:48]}",
            occurred_at=when,
            subscription_collection=subscription_collection,
            entitlement_history_collection=entitlement_history_collection,
            entitlement_current_collection=entitlement_current_collection,
            authorization_evidence_registry=authorization_evidence_registry,
            session=tx,
        )
        entitlement = result.composition.entitlement
        if entitlement.lifecycle_state is not TenantProductEntitlementState.ACTIVE:
            raise CommercialBundleActivationConflictError(
                "COMMERCIAL_BUNDLE_PRODUCT_ENTITLEMENT_NOT_ACTIVE"
            )
        product_receipts.append({
            "product_id": product_id.value,
            "entitlement_id": entitlement.entitlement_id,
            "entitlement_fingerprint": entitlement.fingerprint,
            "authorization_decision_id": result.authorization_evidence.authorization_decision_id,
            "authorization_evidence_fingerprint": result.authorization_evidence.fingerprint,
        })

    activation_reference = f"bundle-act-{_sha3([tenant_id, agreement_id])[:48]}"
    product_tuple = tuple(product_receipts)
    activation_fp = _sha3(
        _receipt_fingerprint_payload(
            agreement, verified_execution_evidence, product_tuple, when, activation_reference
        )
    )
    _, active_agreement = transition_agreement(
        tenant_id=tenant_id,
        agreement_id=agreement_id,
        target_state=CommercialAgreementState.ACTIVE,
        expected_revision=agreement.lifecycle_revision,
        evidence_reference=activation_reference,
        evidence_fingerprint=activation_fp,
        occurred_at=when,
        history_collection=agreement_history_collection,
        current_collection=agreement_current_collection,
        session=tx,
    )
    receipt = CommercialBundleActivationReceipt(
        tenant_id=tenant_id,
        agreement_id=agreement_id,
        offer_id=offer.offer_id.value,
        offer_fingerprint=offer.fingerprint,
        agreement_fingerprint=active_agreement.fingerprint,
        agreement_revision=active_agreement.lifecycle_revision,
        activation_evidence_reference=activation_reference,
        activation_evidence_fingerprint=activation_fp,
        execution_evidence_reference=verified_execution_evidence.execution_evidence_reference,
        execution_evidence_fingerprint=verified_execution_evidence.execution_evidence_fingerprint,
        activated_at=when,
        product_entitlements=product_tuple,
    )
    receipt = CommercialBundleActivationReceipt(
        **{
            **receipt.__dict__,
            "fingerprint": _sha3(receipt.payload()),
        }
    )
    try:
        _receipt_collection(receipt_collection).insert_one(
            receipt.to_document(), session=tx
        )
    except DuplicateKeyError as error:
        raise CommercialBundleActivationConflictError(
            "COMMERCIAL_BUNDLE_RECEIPT_CREATE_RACE"
        ) from error
    except PyMongoError as error:
        raise CommercialBundleActivationPersistenceError(
            "COMMERCIAL_BUNDLE_RECEIPT_CREATE_FAILED"
        ) from error
    return CommercialBundleActivationOutcome.ACTIVATED, receipt


def reconcile_commercial_bundle_activation(
    *,
    tenant_id: str,
    agreement_id: str,
    agreement_history_collection: Any,
    agreement_current_collection: Any,
    entitlement_history_collection: Any,
    entitlement_current_collection: Any,
    receipt_collection: Any,
    session: Any,
) -> tuple[CommercialBundleReconciliationState, CommercialBundleActivationReceipt | None]:
    """Reconcile an uncertain commit from fresh durable agreement/receipt/product state."""
    tx = _active_transaction(session)
    tenant = _text(tenant_id, "COMMERCIAL_BUNDLE_TENANT_INVALID")
    agreement_key = _text(agreement_id, "COMMERCIAL_BUNDLE_AGREEMENT_ID_INVALID")
    try:
        agreement = get_current_agreement(
            tenant, agreement_key, agreement_history_collection,
            agreement_current_collection, session=tx,
        )
    except CommercialAgreementRegistryNotFoundError:
        return CommercialBundleReconciliationState.NOT_COMMITTED, None

    row = _read_receipt(receipt_collection, tenant, agreement_key, tx)
    if row is None:
        if agreement.lifecycle_state in (
            CommercialAgreementState.DRAFT,
            CommercialAgreementState.EXECUTED,
        ):
            return CommercialBundleReconciliationState.NOT_COMMITTED, None
        return CommercialBundleReconciliationState.DIVERGED, None

    receipt = _hydrate_receipt(row)
    if (
        agreement.lifecycle_state is not CommercialAgreementState.ACTIVE
        or agreement.fingerprint != receipt.agreement_fingerprint
        or agreement.lifecycle_revision != receipt.agreement_revision
    ):
        return CommercialBundleReconciliationState.DIVERGED, receipt
    offer = get_commercial_offer(agreement.offer_id)
    if (
        receipt.offer_id != offer.offer_id.value
        or receipt.offer_fingerprint != offer.fingerprint
        or tuple(item.get("product_id") for item in receipt.product_entitlements)
        != tuple(item.value for item in offer.product_ids)
    ):
        return CommercialBundleReconciliationState.DIVERGED, receipt
    for item in receipt.product_entitlements:
        try:
            entitlement = get_current_product_entitlement(
                tenant, item["entitlement_id"],
                entitlement_history_collection, entitlement_current_collection,
                session=tx,
            )
        except TenantProductEntitlementRegistryError:
            return CommercialBundleReconciliationState.DIVERGED, receipt
        if (
            entitlement.lifecycle_state is not TenantProductEntitlementState.ACTIVE
            or entitlement.product_id.value != item["product_id"]
            or entitlement.fingerprint != item["entitlement_fingerprint"]
        ):
            return CommercialBundleReconciliationState.DIVERGED, receipt
    return CommercialBundleReconciliationState.COMMITTED, receipt


__all__ = [
    "COLLECTION",
    "CommercialBundleActivationConflictError",
    "CommercialBundleActivationError",
    "CommercialBundleActivationEvidenceError",
    "CommercialBundleActivationOutcome",
    "CommercialBundleActivationPersistenceError",
    "CommercialBundleActivationReceipt",
    "CommercialBundleActivationTransactionRequiredError",
    "CommercialBundleReconciliationState",
    "INDEX_NAME",
    "FINGERPRINT_INDEX_NAME",
    "SCHEMA",
    "VERSION",
    "VerifiedCommercialAgreementExecutionEvidence",
    "activate_commercial_bundle",
    "ensure_indexes",
    "reconcile_commercial_bundle_activation",
]
