"""WILSY OS commercial agreement domain.

TITLE: Tenant Commercial Agreement
VERSION: v1.0.0-EOS-COMMERCIAL-AGREEMENT
AUTHORITY: Tenant commercial contract truth; not product entitlement or IAM.
PURPOSE: Represent an exact tenant's executed commercial agreement against one
         canonical offer descriptor, with immutable terms and evidence-bound
         lifecycle transitions. Persistence and HTTP authorization are separate.
SECURITY: No browser-authored tenant scope, pricing, permissions or entitlement.
FINANCIAL: No invoice, payment, settlement or execution authority; Kennel EOS
           remains the exclusive financial execution authority.
"""
from __future__ import annotations

from dataclasses import dataclass, replace
from datetime import datetime, timezone
from enum import StrEnum
import hashlib
import hmac
import json
import re
from typing import Final

from tools.eos.saas.entitlement.commercial_offer_catalogue import (
    CommercialOfferId,
    get_commercial_offer,
)

VERSION: Final[str] = "v1.0.0-EOS-COMMERCIAL-AGREEMENT"
SCHEMA: Final[str] = "WILSY-TENANT-COMMERCIAL-AGREEMENT/V1"
_ID: Final[re.Pattern[str]] = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._:-]{0,159}$")
_SHA3: Final[re.Pattern[str]] = re.compile(r"^[0-9a-f]{128}$")
_FORBIDDEN_TENANTS: Final[frozenset[str]] = frozenset(
    {"default", "global", "global_root", "root", "master", "*"}
)


class CommercialAgreementError(ValueError):
    """Agreement input, persisted shape or lifecycle evidence is invalid."""


class CommercialAgreementState(StrEnum):
    DRAFT = "DRAFT"
    EXECUTED = "EXECUTED"
    ACTIVE = "ACTIVE"
    SUSPENDED = "SUSPENDED"
    TERMINATED = "TERMINATED"
    EXPIRED = "EXPIRED"


class CommercialRenewalMode(StrEnum):
    NONE = "NONE"
    AUTOMATIC = "AUTOMATIC"
    MANUAL = "MANUAL"


def _text(name: str, value: object) -> str:
    if not isinstance(value, str) or not value or value != value.strip():
        raise CommercialAgreementError(f"COMMERCIAL_AGREEMENT_{name}_INVALID")
    if any(ord(char) < 32 for char in value):
        raise CommercialAgreementError(f"COMMERCIAL_AGREEMENT_{name}_INVALID")
    return value


def _identity(name: str, value: object) -> str:
    candidate = _text(name, value)
    if _ID.fullmatch(candidate) is None:
        raise CommercialAgreementError(f"COMMERCIAL_AGREEMENT_{name}_INVALID")
    return candidate


def _tenant(value: object) -> str:
    tenant = _identity("TENANT_ID", value)
    if tenant.casefold() in _FORBIDDEN_TENANTS:
        raise CommercialAgreementError("COMMERCIAL_AGREEMENT_TENANT_INVALID")
    return tenant


def _fingerprint(name: str, value: object) -> str:
    if not isinstance(value, str) or _SHA3.fullmatch(value) is None:
        raise CommercialAgreementError(f"COMMERCIAL_AGREEMENT_{name}_INVALID")
    return value


def _when(name: str, value: object, *, required: bool = False) -> datetime | None:
    candidate = value
    if isinstance(candidate, str):
        try:
            candidate = datetime.fromisoformat(candidate.replace("Z", "+00:00"))
        except ValueError as error:
            raise CommercialAgreementError(
                f"COMMERCIAL_AGREEMENT_{name}_INVALID"
            ) from error
    if candidate is None and not required:
        return None
    if (
        not isinstance(candidate, datetime)
        or candidate.tzinfo is None
        or candidate.utcoffset() is None
    ):
        raise CommercialAgreementError(f"COMMERCIAL_AGREEMENT_{name}_INVALID")
    return candidate.astimezone(timezone.utc)


def _pair(name: str, reference: object, fingerprint: object) -> tuple[str | None, str | None]:
    if reference is None and fingerprint is None:
        return None, None
    if reference is None or fingerprint is None:
        raise CommercialAgreementError(
            f"COMMERCIAL_AGREEMENT_{name}_EVIDENCE_PAIR_INVALID"
        )
    return (
        _identity(f"{name}_REFERENCE", reference),
        _fingerprint(f"{name}_FINGERPRINT", fingerprint),
    )


def _digest(payload: dict[str, object]) -> str:
    encoded = json.dumps(
        payload, ensure_ascii=False, allow_nan=False, sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")
    return hashlib.sha3_512(encoded).hexdigest()


def _iso(value: datetime | None) -> str | None:
    if value is None:
        return None
    return value.astimezone(timezone.utc).isoformat().replace("+00:00", "Z")


@dataclass(frozen=True, slots=True)
class CommercialAgreement:
    """Immutable tenant agreement snapshot with canonical offer and evidence binding.

    Execution evidence must be supplied by an independently authenticated
    contract-signature/evidence authority. A reference and digest bind evidence;
    they do not themselves verify a signature or grant a product entitlement.
    """

    tenant_id: str
    agreement_id: str
    offer_id: CommercialOfferId | str
    offer_fingerprint: str
    contract_reference: str
    contract_version: str
    counterparty_legal_name: str
    effective_at: datetime
    expires_at: datetime | None
    renewal_mode: CommercialRenewalMode | str
    notice_days: int
    termination_terms_reference: str
    lifecycle_state: CommercialAgreementState | str = CommercialAgreementState.DRAFT
    executed_at: datetime | None = None
    execution_evidence_reference: str | None = None
    execution_evidence_fingerprint: str | None = None
    activated_at: datetime | None = None
    activation_evidence_reference: str | None = None
    activation_evidence_fingerprint: str | None = None
    suspended_at: datetime | None = None
    suspension_evidence_reference: str | None = None
    suspension_evidence_fingerprint: str | None = None
    terminated_at: datetime | None = None
    termination_evidence_reference: str | None = None
    termination_evidence_fingerprint: str | None = None
    expired_at: datetime | None = None
    expiry_evidence_reference: str | None = None
    expiry_evidence_fingerprint: str | None = None
    lifecycle_revision: int = 0
    schema: str = SCHEMA
    version: str = VERSION
    fingerprint: str = ""

    def __post_init__(self) -> None:
        if self.schema != SCHEMA or self.version != VERSION:
            raise CommercialAgreementError("COMMERCIAL_AGREEMENT_IDENTITY_INVALID")
        tenant = _tenant(self.tenant_id)
        agreement_id = _identity("AGREEMENT_ID", self.agreement_id)
        contract_ref = _identity("CONTRACT_REFERENCE", self.contract_reference)
        contract_version = _text("CONTRACT_VERSION", self.contract_version)
        counterparty = _text("COUNTERPARTY_LEGAL_NAME", self.counterparty_legal_name)
        termination_terms = _identity(
            "TERMINATION_TERMS_REFERENCE", self.termination_terms_reference
        )
        try:
            offer_id = CommercialOfferId(self.offer_id)
            renewal = CommercialRenewalMode(self.renewal_mode)
            state = CommercialAgreementState(self.lifecycle_state)
        except (TypeError, ValueError) as error:
            raise CommercialAgreementError("COMMERCIAL_AGREEMENT_ENUM_INVALID") from error
        offer = get_commercial_offer(offer_id)
        offer_fingerprint = _fingerprint("OFFER_FINGERPRINT", self.offer_fingerprint)
        if not hmac.compare_digest(offer.fingerprint, offer_fingerprint):
            raise CommercialAgreementError("COMMERCIAL_AGREEMENT_OFFER_BINDING_INVALID")
        if isinstance(self.notice_days, bool) or not isinstance(self.notice_days, int) or not 0 <= self.notice_days <= 365:
            raise CommercialAgreementError("COMMERCIAL_AGREEMENT_NOTICE_DAYS_INVALID")
        if self.lifecycle_revision < 0 or isinstance(self.lifecycle_revision, bool) or not isinstance(self.lifecycle_revision, int):
            raise CommercialAgreementError("COMMERCIAL_AGREEMENT_REVISION_INVALID")

        effective = _when("EFFECTIVE_AT", self.effective_at, required=True)
        expires = _when("EXPIRES_AT", self.expires_at)
        if expires is not None and expires <= effective:
            raise CommercialAgreementError("COMMERCIAL_AGREEMENT_TERM_INVALID")
        executed = _when("EXECUTED_AT", self.executed_at)
        activated = _when("ACTIVATED_AT", self.activated_at)
        suspended = _when("SUSPENDED_AT", self.suspended_at)
        terminated = _when("TERMINATED_AT", self.terminated_at)
        expired = _when("EXPIRED_AT", self.expired_at)
        execution_ref, execution_fp = _pair(
            "EXECUTION", self.execution_evidence_reference,
            self.execution_evidence_fingerprint,
        )
        activation_ref, activation_fp = _pair(
            "ACTIVATION", self.activation_evidence_reference,
            self.activation_evidence_fingerprint,
        )
        suspension_ref, suspension_fp = _pair(
            "SUSPENSION", self.suspension_evidence_reference,
            self.suspension_evidence_fingerprint,
        )
        termination_ref, termination_fp = _pair(
            "TERMINATION", self.termination_evidence_reference,
            self.termination_evidence_fingerprint,
        )
        expiry_ref, expiry_fp = _pair(
            "EXPIRY", self.expiry_evidence_reference,
            self.expiry_evidence_fingerprint,
        )

        if state is CommercialAgreementState.DRAFT:
            if any((executed, execution_ref, execution_fp, activated, activation_ref,
                    activation_fp, suspended, suspension_ref, suspension_fp,
                    terminated, termination_ref, termination_fp, expired,
                    expiry_ref, expiry_fp)):
                raise CommercialAgreementError("COMMERCIAL_AGREEMENT_DRAFT_SHAPE_INVALID")
        else:
            if executed is None or execution_ref is None or execution_fp is None:
                raise CommercialAgreementError("COMMERCIAL_AGREEMENT_EXECUTION_REQUIRED")
            if executed < effective and state is CommercialAgreementState.ACTIVE:
                raise CommercialAgreementError("COMMERCIAL_AGREEMENT_EXECUTION_CHRONOLOGY_INVALID")

        if state in (CommercialAgreementState.ACTIVE, CommercialAgreementState.SUSPENDED,
                     CommercialAgreementState.TERMINATED, CommercialAgreementState.EXPIRED):
            if activated is None or activation_ref is None or activation_fp is None:
                raise CommercialAgreementError("COMMERCIAL_AGREEMENT_ACTIVATION_EVIDENCE_REQUIRED")
        elif any((activated, activation_ref, activation_fp)):
            raise CommercialAgreementError("COMMERCIAL_AGREEMENT_ACTIVATION_SHAPE_INVALID")

        if state is CommercialAgreementState.SUSPENDED:
            if suspended is None or suspension_ref is None or suspension_fp is None:
                raise CommercialAgreementError("COMMERCIAL_AGREEMENT_SUSPENSION_EVIDENCE_REQUIRED")
        elif state in (CommercialAgreementState.TERMINATED, CommercialAgreementState.EXPIRED):
            suspension_values = (suspended, suspension_ref, suspension_fp)
            if any(value is not None for value in suspension_values) and not all(
                value is not None for value in suspension_values
            ):
                raise CommercialAgreementError("COMMERCIAL_AGREEMENT_SUSPENSION_SHAPE_INVALID")
        elif any((suspended, suspension_ref, suspension_fp)):
            raise CommercialAgreementError("COMMERCIAL_AGREEMENT_SUSPENSION_SHAPE_INVALID")

        if state is CommercialAgreementState.TERMINATED:
            if terminated is None or termination_ref is None or termination_fp is None:
                raise CommercialAgreementError("COMMERCIAL_AGREEMENT_TERMINATION_EVIDENCE_REQUIRED")
        elif any((terminated, termination_ref, termination_fp)):
            raise CommercialAgreementError("COMMERCIAL_AGREEMENT_TERMINATION_SHAPE_INVALID")

        if state is CommercialAgreementState.EXPIRED:
            if expired is None or expiry_ref is None or expiry_fp is None:
                raise CommercialAgreementError("COMMERCIAL_AGREEMENT_EXPIRY_EVIDENCE_REQUIRED")
        elif any((expired, expiry_ref, expiry_fp)):
            raise CommercialAgreementError("COMMERCIAL_AGREEMENT_EXPIRY_SHAPE_INVALID")

        if activated is not None and (executed is None or activated < executed):
            raise CommercialAgreementError("COMMERCIAL_AGREEMENT_ACTIVATION_CHRONOLOGY_INVALID")
        if suspended is not None and (activated is None or suspended < activated):
            raise CommercialAgreementError("COMMERCIAL_AGREEMENT_SUSPENSION_CHRONOLOGY_INVALID")
        if terminated is not None and (
            activated is None or terminated < activated
            or (suspended is not None and terminated < suspended)
        ):
            raise CommercialAgreementError("COMMERCIAL_AGREEMENT_TERMINATION_CHRONOLOGY_INVALID")
        if expired is not None and (
            expires is None or expired < expires
            or (suspended is not None and expired < suspended)
        ):
            raise CommercialAgreementError("COMMERCIAL_AGREEMENT_EXPIRY_CHRONOLOGY_INVALID")

        object.__setattr__(self, "tenant_id", tenant)
        object.__setattr__(self, "agreement_id", agreement_id)
        object.__setattr__(self, "offer_id", offer_id)
        object.__setattr__(self, "offer_fingerprint", offer_fingerprint)
        object.__setattr__(self, "contract_reference", contract_ref)
        object.__setattr__(self, "contract_version", contract_version)
        object.__setattr__(self, "counterparty_legal_name", counterparty)
        object.__setattr__(self, "termination_terms_reference", termination_terms)
        object.__setattr__(self, "renewal_mode", renewal)
        object.__setattr__(self, "lifecycle_state", state)
        object.__setattr__(self, "effective_at", effective)
        object.__setattr__(self, "expires_at", expires)
        object.__setattr__(self, "executed_at", executed)
        object.__setattr__(self, "activated_at", activated)
        object.__setattr__(self, "suspended_at", suspended)
        object.__setattr__(self, "terminated_at", terminated)
        object.__setattr__(self, "expired_at", expired)
        for name, value in (
            ("execution_evidence_reference", execution_ref),
            ("execution_evidence_fingerprint", execution_fp),
            ("activation_evidence_reference", activation_ref),
            ("activation_evidence_fingerprint", activation_fp),
            ("suspension_evidence_reference", suspension_ref),
            ("suspension_evidence_fingerprint", suspension_fp),
            ("termination_evidence_reference", termination_ref),
            ("termination_evidence_fingerprint", termination_fp),
            ("expiry_evidence_reference", expiry_ref),
            ("expiry_evidence_fingerprint", expiry_fp),
        ):
            object.__setattr__(self, name, value)
        payload = self._payload()
        digest = _digest(payload)
        if self.fingerprint and not hmac.compare_digest(
            _fingerprint("FINGERPRINT", self.fingerprint), digest
        ):
            raise CommercialAgreementError("COMMERCIAL_AGREEMENT_FINGERPRINT_MISMATCH")
        object.__setattr__(self, "fingerprint", digest)

    def transition(
        self,
        target_state: CommercialAgreementState | str,
        *,
        expected_revision: int,
        evidence_reference: str,
        evidence_fingerprint: str,
        occurred_at: datetime,
    ) -> "CommercialAgreement":
        """Derive one evidence-bound lifecycle transition from this snapshot."""
        if (
            isinstance(expected_revision, bool)
            or not isinstance(expected_revision, int)
            or expected_revision != self.lifecycle_revision
        ):
            raise CommercialAgreementError("COMMERCIAL_AGREEMENT_STALE_REVISION")
        try:
            target = CommercialAgreementState(target_state)
        except (TypeError, ValueError) as error:
            raise CommercialAgreementError("COMMERCIAL_AGREEMENT_TARGET_STATE_INVALID") from error
        when = _when("TRANSITION_OCCURRED_AT", occurred_at, required=True)
        reference = _identity("TRANSITION_EVIDENCE_REFERENCE", evidence_reference)
        fingerprint = _fingerprint("TRANSITION_EVIDENCE_FINGERPRINT", evidence_fingerprint)
        allowed = {
            CommercialAgreementState.DRAFT: {CommercialAgreementState.EXECUTED},
            CommercialAgreementState.EXECUTED: {CommercialAgreementState.ACTIVE},
            CommercialAgreementState.ACTIVE: {
                CommercialAgreementState.SUSPENDED,
                CommercialAgreementState.TERMINATED,
                CommercialAgreementState.EXPIRED,
            },
            CommercialAgreementState.SUSPENDED: {
                CommercialAgreementState.TERMINATED,
                CommercialAgreementState.EXPIRED,
            },
            CommercialAgreementState.TERMINATED: set(),
            CommercialAgreementState.EXPIRED: set(),
        }
        if target not in allowed[self.lifecycle_state]:
            raise CommercialAgreementError("COMMERCIAL_AGREEMENT_TRANSITION_NOT_ALLOWED")
        changes: dict[str, object] = {
            "lifecycle_state": target,
            "lifecycle_revision": self.lifecycle_revision + 1,
            "fingerprint": "",
        }
        if target is CommercialAgreementState.EXECUTED:
            changes.update(
                executed_at=when,
                execution_evidence_reference=reference,
                execution_evidence_fingerprint=fingerprint,
            )
        elif target is CommercialAgreementState.ACTIVE:
            changes.update(
                activated_at=when,
                activation_evidence_reference=reference,
                activation_evidence_fingerprint=fingerprint,
            )
        elif target is CommercialAgreementState.SUSPENDED:
            changes.update(
                suspended_at=when,
                suspension_evidence_reference=reference,
                suspension_evidence_fingerprint=fingerprint,
            )
        elif target is CommercialAgreementState.TERMINATED:
            changes.update(
                terminated_at=when,
                termination_evidence_reference=reference,
                termination_evidence_fingerprint=fingerprint,
            )
        elif target is CommercialAgreementState.EXPIRED:
            changes.update(
                expired_at=when,
                expiry_evidence_reference=reference,
                expiry_evidence_fingerprint=fingerprint,
            )
        return replace(self, **changes)

    def _payload(self) -> dict[str, object]:
        return {
            "schema": self.schema, "version": self.version,
            "tenant_id": self.tenant_id, "agreement_id": self.agreement_id,
            "offer_id": str(self.offer_id), "offer_fingerprint": self.offer_fingerprint,
            "contract_reference": self.contract_reference,
            "contract_version": self.contract_version,
            "counterparty_legal_name": self.counterparty_legal_name,
            "effective_at": _iso(self.effective_at), "expires_at": _iso(self.expires_at),
            "renewal_mode": str(self.renewal_mode), "notice_days": self.notice_days,
            "termination_terms_reference": self.termination_terms_reference,
            "lifecycle_state": str(self.lifecycle_state),
            "executed_at": _iso(self.executed_at),
            "execution_evidence_reference": self.execution_evidence_reference,
            "execution_evidence_fingerprint": self.execution_evidence_fingerprint,
            "activated_at": _iso(self.activated_at),
            "activation_evidence_reference": self.activation_evidence_reference,
            "activation_evidence_fingerprint": self.activation_evidence_fingerprint,
            "suspended_at": _iso(self.suspended_at),
            "suspension_evidence_reference": self.suspension_evidence_reference,
            "suspension_evidence_fingerprint": self.suspension_evidence_fingerprint,
            "terminated_at": _iso(self.terminated_at),
            "termination_evidence_reference": self.termination_evidence_reference,
            "termination_evidence_fingerprint": self.termination_evidence_fingerprint,
            "expired_at": _iso(self.expired_at),
            "expiry_evidence_reference": self.expiry_evidence_reference,
            "expiry_evidence_fingerprint": self.expiry_evidence_fingerprint,
            "lifecycle_revision": self.lifecycle_revision,
        }

    def to_dict(self) -> dict[str, object]:
        """Return a detached strict serializable snapshot."""
        payload = self._payload()
        payload["fingerprint"] = self.fingerprint
        return payload
