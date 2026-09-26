"""TITLE: WILSY OS Legal Client Acceptance Context Evidence.
VERSION: v1.0.0-L9A4-P2C1-CLIENT-ACCEPTANCE-CONTEXT
AUTHORITY: Wilsy OS Core Governance / Python EOS Legal Operations.
EPITOME: Defines one immutable, server-composed correlation snapshot for a
         client review/acceptance journey. It binds one authenticated actor,
         represented matter party, acting capacity, exact reviewable instrument,
         ACTIVE lifecycle and current APPROVED firm decision without recording
         acceptance or creating any legal, Court or financial authority.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tools/eos/legal_operations/domain/legal_client_acceptance_context.py
COLLABORATION / OWNERSHIP: CaseMatter, LegalMatterParty, acting-capacity,
                            instrument, lifecycle and approval domains own
                            canonical source truth. A later authorized composer
                            owns currentness and issuance policy; a later
                            registry owns durability; a later projection owns
                            browser-safe delivery. This value owns correlation
                            evidence only.
CERTIFICATION / UPDATE DATE: 2026-09-26.
CHANGELOG: v1.0.0-L9A4-P2C1-CLIENT-ACCEPTANCE-CONTEXT establishes strict,
           immutable context evidence with exact actor/party/capacity/source
           binding, bounded chronology, replay identity and deterministic
           fingerprinting. It deliberately creates no ClientAcceptance,
           Engagement, Representation, Court or financial authority.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2; ISO 27001.
SECURITY / PRIVACY POSTURE: Opaque identifiers, bounded references,
                             fingerprints and intentionally selected review
                             metadata only. Raw content locators are retained
                             as server-only correlation evidence; no credentials,
                             tokens, secrets, email or client PII are required.
TENANT BOUNDARY: Tenant, matter and represented-party identity are derived
                 from exact canonical values and must agree across every input.
AUTHORITY BOUNDARY: Immutable server correlation evidence for a bounded client
                    review/acceptance journey. The context does not authenticate,
                    authorize, prove currentness, deliver content or accept terms.
FINANCIAL AUTHORITY BOUNDARY: None; Kennel EOS remains exclusive financial
                              execution authority.
FAIL-CLOSED DECLARATION: Missing, malformed, stale, cross-scope, non-ACTIVE,
                         non-APPROVED, temporally invalid or fingerprint-
                         divergent evidence rejects without coercion or repair.
"""
from __future__ import annotations

import hashlib
import hmac
import json
import re
import unicodedata
from dataclasses import dataclass
from datetime import datetime, timezone
from enum import StrEnum
from typing import Any, Final, Mapping, NoReturn, cast

from tools.eos.legal_operations.domain.legal_client_acting_capacity import (
    LegalClientActingCapacity,
    LegalClientActingCapacityType,
)
from tools.eos.legal_operations.domain.legal_client_matter_acceptance_instrument import (
    LegalClientMatterAcceptanceInstrument,
)
from tools.eos.legal_operations.domain.legal_client_matter_acceptance_instrument_approval import (
    LegalClientMatterAcceptanceInstrumentApproval,
    LegalClientMatterAcceptanceInstrumentApprovalDecision,
)
from tools.eos.legal_operations.domain.legal_client_matter_acceptance_instrument_lifecycle import (
    LegalClientMatterAcceptanceInstrumentLifecycle,
    LegalClientMatterAcceptanceInstrumentLifecycleStatus,
)
from tools.eos.legal_operations.domain.legal_matter_party import LegalMatterParty
from tools.eos.legal_operations.domain.legal_operations_lifecycle import (
    CaseMatter,
    CaseMatterState,
)


VERSION: Final[str] = "v1.0.0-L9A4-P2C1-CLIENT-ACCEPTANCE-CONTEXT"
SCHEMA: Final[str] = "WILSY-LEGAL-CLIENT-ACCEPTANCE-CONTEXT/V1"
_IDENTITY: Final[re.Pattern[str]] = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._:-]{0,159}$")
_HEX: Final[re.Pattern[str]] = re.compile(r"^[0-9a-f]{128}$")
_FIELDS: Final[tuple[str, ...]] = (
    "schema",
    "context_version",
    "acceptance_context_id",
    "tenant_id",
    "actor_principal_id",
    "case_matter_id",
    "matter_reference",
    "matter_fingerprint",
    "party_id",
    "subject_reference",
    "subject_identity_fingerprint",
    "capacity_id",
    "capacity_type",
    "capacity_fingerprint",
    "capacity_effective_from",
    "capacity_effective_until",
    "instrument_id",
    "instrument_version",
    "instrument_fingerprint",
    "content_fingerprint",
    "content_reference",
    "title",
    "review_scope",
    "instrument_effective_from",
    "lifecycle_status",
    "lifecycle_fingerprint",
    "lifecycle_evidence_fingerprint",
    "approval_id",
    "approval_decision",
    "approval_fingerprint",
    "approval_effective_from",
    "issuer_evidence_reference",
    "issuer_evidence_fingerprint",
    "issued_at",
    "expires_at",
    "replay_key",
    "fingerprint",
)
CONTEXT_FIELDS: Final[frozenset[str]] = frozenset(_FIELDS)


class LegalClientAcceptanceContextError(ValueError):
    """Stable, non-sensitive validation failure for context evidence."""

    def __init__(self, code: str) -> None:
        """Expose only a bounded code; supplied values are never included."""
        self.code = code
        super().__init__(code)


def _fail(code: str, cause: BaseException | None = None) -> NoReturn:
    """Raise one stable validation code while retaining technical cause."""
    error = LegalClientAcceptanceContextError(code)
    if cause is None:
        raise error
    raise error from cause


def _identity(name: str, value: object) -> str:
    """Require one bounded opaque identity without coercion or trimming."""
    if (
        not isinstance(value, str)
        or value != value.strip()
        or _IDENTITY.fullmatch(value) is None
    ):
        _fail(f"L9A4_P2C1_{name.upper()}_INVALID")
    return cast(str, value)


def _tenant(value: object) -> str:
    """Require one explicit non-global tenant identity."""
    tenant = _identity("tenant_id", value)
    if tenant.casefold() in {"default", "global", "global_root", "root", "master", "*"}:
        _fail("L9A4_P2C1_TENANT_REQUIRED")
    return tenant


def _fingerprint(name: str, value: object) -> str:
    """Require one lowercase SHA3-512 hexadecimal fingerprint."""
    if not isinstance(value, str) or _HEX.fullmatch(value) is None:
        _fail(f"L9A4_P2C1_{name.upper()}_INVALID")
    return value


def _reference(name: str, value: object, *, limit: int = 512) -> str:
    """Require bounded NFC single-line opaque evidence/reference text."""
    if (
        not isinstance(value, str)
        or not value
        or value != value.strip()
        or len(value) > limit
        or any(ord(character) < 32 for character in value)
    ):
        _fail(f"L9A4_P2C1_{name.upper()}_INVALID")
    normalized = unicodedata.normalize("NFC", value)
    if not normalized or len(normalized) > limit:
        _fail(f"L9A4_P2C1_{name.upper()}_INVALID")
    return normalized


def _display(name: str, value: object, *, limit: int) -> str:
    """Require bounded NFC review metadata without treating it as authority."""
    return _reference(name, value, limit=limit)


def _timestamp(name: str, value: object) -> datetime:
    """Require an aware timestamp and normalize it to UTC with microseconds."""
    parsed = value
    if isinstance(parsed, str):
        try:
            parsed = datetime.fromisoformat(parsed.replace("Z", "+00:00"))
        except ValueError as error:
            _fail(f"L9A4_P2C1_{name.upper()}_INVALID", error)
    if not isinstance(parsed, datetime) or parsed.tzinfo is None or parsed.utcoffset() is None:
        _fail(f"L9A4_P2C1_{name.upper()}_INVALID")
    return parsed.astimezone(timezone.utc).replace(microsecond=parsed.microsecond)


def _json_value(value: object) -> object:
    """Convert immutable values to deterministic JSON-safe values."""
    if isinstance(value, datetime):
        return value.astimezone(timezone.utc).isoformat(timespec="microseconds").replace(
            "+00:00", "Z"
        )
    if isinstance(value, StrEnum):
        return value.value
    return value


def _digest(instance: "LegalClientAcceptanceContext") -> str:
    """Hash every declared semantic field except the derived fingerprint."""
    payload = {
        field: _json_value(getattr(instance, field)) for field in _FIELDS[:-1]
    }
    return hashlib.sha3_512(
        json.dumps(
            payload,
            ensure_ascii=False,
            allow_nan=False,
            sort_keys=False,
            separators=(",", ":"),
        ).encode("utf-8")
    ).hexdigest()


@dataclass(frozen=True, slots=True)
class LegalClientAcceptanceContext:
    """Immutable server correlation evidence for one client review journey.

    The factory :meth:`from_canonical` derives repeated tenant, matter, party,
    capacity, instrument, lifecycle and approval bindings from exact canonical
    domain values. The value performs no authentication, authorization lookup,
    currentness query, persistence, delivery, acceptance, engagement,
    representation, Court or financial action. ``content_reference`` is a
    server-only locator and must be excluded by any future browser projection.
    ``review_scope`` is the stable future ``LegalClientAcceptance``
    ``acceptance_scope`` mapping; no second scope vocabulary is invented.
    """

    schema: str
    context_version: str
    acceptance_context_id: str
    tenant_id: str
    actor_principal_id: str
    case_matter_id: str
    matter_reference: str
    matter_fingerprint: str
    party_id: str
    subject_reference: str
    subject_identity_fingerprint: str
    capacity_id: str
    capacity_type: LegalClientActingCapacityType | str
    capacity_fingerprint: str
    capacity_effective_from: datetime
    capacity_effective_until: datetime | None
    instrument_id: str
    instrument_version: str
    instrument_fingerprint: str
    content_fingerprint: str
    content_reference: str
    title: str
    review_scope: str
    instrument_effective_from: datetime
    lifecycle_status: LegalClientMatterAcceptanceInstrumentLifecycleStatus | str
    lifecycle_fingerprint: str
    lifecycle_evidence_fingerprint: str
    approval_id: str
    approval_decision: LegalClientMatterAcceptanceInstrumentApprovalDecision | str
    approval_fingerprint: str
    approval_effective_from: datetime
    issuer_evidence_reference: str
    issuer_evidence_fingerprint: str
    issued_at: datetime
    expires_at: datetime
    replay_key: str
    fingerprint: str = ""

    def __post_init__(self) -> None:
        """Validate the exact schema, chronology and deterministic integrity."""
        values: dict[str, object] = {
            "schema": self.schema,
            "context_version": self.context_version,
        }
        if values["schema"] != SCHEMA or values["context_version"] != VERSION:
            _fail("L9A4_P2C1_IDENTITY_INVALID")
        normalized: dict[str, object] = {
            "acceptance_context_id": _identity("acceptance_context_id", self.acceptance_context_id),
            "tenant_id": _tenant(self.tenant_id),
            "actor_principal_id": _identity("actor_principal_id", self.actor_principal_id),
            "case_matter_id": _identity("case_matter_id", self.case_matter_id),
            "matter_reference": _display("matter_reference", self.matter_reference, limit=240),
            "matter_fingerprint": _fingerprint("matter_fingerprint", self.matter_fingerprint),
            "party_id": _identity("party_id", self.party_id),
            "subject_reference": _reference("subject_reference", self.subject_reference, limit=224),
            "subject_identity_fingerprint": _fingerprint("subject_identity_fingerprint", self.subject_identity_fingerprint),
            "capacity_id": _identity("capacity_id", self.capacity_id),
            "capacity_fingerprint": _fingerprint("capacity_fingerprint", self.capacity_fingerprint),
            "capacity_effective_from": _timestamp("capacity_effective_from", self.capacity_effective_from),
            "capacity_effective_until": None if self.capacity_effective_until is None else _timestamp("capacity_effective_until", self.capacity_effective_until),
            "instrument_id": _identity("instrument_id", self.instrument_id),
            "instrument_version": _identity("instrument_version", self.instrument_version),
            "instrument_fingerprint": _fingerprint("instrument_fingerprint", self.instrument_fingerprint),
            "content_fingerprint": _fingerprint("content_fingerprint", self.content_fingerprint),
            "content_reference": _reference("content_reference", self.content_reference),
            "title": _display("title", self.title, limit=200),
            "review_scope": _display("review_scope", self.review_scope, limit=1000),
            "instrument_effective_from": _timestamp("instrument_effective_from", self.instrument_effective_from),
            "lifecycle_fingerprint": _fingerprint("lifecycle_fingerprint", self.lifecycle_fingerprint),
            "lifecycle_evidence_fingerprint": _fingerprint("lifecycle_evidence_fingerprint", self.lifecycle_evidence_fingerprint),
            "approval_id": _identity("approval_id", self.approval_id),
            "approval_fingerprint": _fingerprint("approval_fingerprint", self.approval_fingerprint),
            "approval_effective_from": _timestamp("approval_effective_from", self.approval_effective_from),
            "issuer_evidence_reference": _reference("issuer_evidence_reference", self.issuer_evidence_reference),
            "issuer_evidence_fingerprint": _fingerprint("issuer_evidence_fingerprint", self.issuer_evidence_fingerprint),
            "issued_at": _timestamp("issued_at", self.issued_at),
            "expires_at": _timestamp("expires_at", self.expires_at),
            "replay_key": _reference("replay_key", self.replay_key, limit=240),
        }
        try:
            normalized["capacity_type"] = LegalClientActingCapacityType(self.capacity_type)
            normalized["lifecycle_status"] = LegalClientMatterAcceptanceInstrumentLifecycleStatus(self.lifecycle_status)
            normalized["approval_decision"] = LegalClientMatterAcceptanceInstrumentApprovalDecision(self.approval_decision)
        except (TypeError, ValueError) as error:
            _fail("L9A4_P2C1_ENUM_INVALID", error)
        capacity_from = cast(datetime, normalized["capacity_effective_from"])
        capacity_until = cast(datetime | None, normalized["capacity_effective_until"])
        issued_at = cast(datetime, normalized["issued_at"])
        expires_at = cast(datetime, normalized["expires_at"])
        if capacity_until is not None and capacity_until <= capacity_from:
            _fail("L9A4_P2C1_CAPACITY_INTERVAL_INVALID")
        if expires_at <= issued_at:
            _fail("L9A4_P2C1_EXPIRY_INVALID")
        if normalized["lifecycle_status"] is not LegalClientMatterAcceptanceInstrumentLifecycleStatus.ACTIVE:
            _fail("L9A4_P2C1_LIFECYCLE_NOT_ACTIVE")
        if normalized["approval_decision"] is not LegalClientMatterAcceptanceInstrumentApprovalDecision.APPROVED:
            _fail("L9A4_P2C1_APPROVAL_NOT_APPROVED")
        for field, value in normalized.items():
            object.__setattr__(self, field, value)
        digest = _digest(self)
        if self.fingerprint and (
            not isinstance(self.fingerprint, str)
            or not hmac.compare_digest(self.fingerprint, digest)
        ):
            _fail("L9A4_P2C1_FINGERPRINT_MISMATCH")
        object.__setattr__(self, "fingerprint", digest)

    @property
    def acceptance_scope(self) -> str:
        """Return the future ClientAcceptance scope mapping from review scope."""
        return self.review_scope

    @classmethod
    def from_canonical(
        cls,
        *,
        acceptance_context_id: str,
        actor_principal_id: str,
        case_matter: CaseMatter,
        party: LegalMatterParty,
        acting_capacity: LegalClientActingCapacity,
        instrument: LegalClientMatterAcceptanceInstrument,
        lifecycle: LegalClientMatterAcceptanceInstrumentLifecycle,
        approval: LegalClientMatterAcceptanceInstrumentApproval,
        issued_at: datetime,
        expires_at: datetime,
        replay_key: str,
        issuer_evidence_reference: str,
        issuer_evidence_fingerprint: str,
    ) -> "LegalClientAcceptanceContext":
        """Derive one context solely from exact canonical domain evidence.

        The factory requires one OPEN matter, exact party/capacity correlation,
        capacity validity at issuance, effective instrument chronology, ACTIVE
        lifecycle, and APPROVED decision effective by issuance. It does not
        prove that these values remain current after construction and never
        persists, authenticates, authorizes, delivers, or records acceptance.
        """
        if type(case_matter) is not CaseMatter:
            _fail("L9A4_P2C1_CASE_MATTER_REQUIRED")
        if case_matter.state is not CaseMatterState.OPEN:
            _fail("L9A4_P2C1_OPEN_CASE_MATTER_REQUIRED")
        if type(party) is not LegalMatterParty:
            _fail("L9A4_P2C1_PARTY_REQUIRED")
        if type(acting_capacity) is not LegalClientActingCapacity:
            _fail("L9A4_P2C1_CAPACITY_REQUIRED")
        if type(instrument) is not LegalClientMatterAcceptanceInstrument:
            _fail("L9A4_P2C1_INSTRUMENT_REQUIRED")
        if type(lifecycle) is not LegalClientMatterAcceptanceInstrumentLifecycle:
            _fail("L9A4_P2C1_LIFECYCLE_REQUIRED")
        if type(approval) is not LegalClientMatterAcceptanceInstrumentApproval:
            _fail("L9A4_P2C1_APPROVAL_REQUIRED")
        issued = _timestamp("issued_at", issued_at)
        expires = _timestamp("expires_at", expires_at)
        if expires <= issued:
            _fail("L9A4_P2C1_EXPIRY_INVALID")
        if (
            party.tenant_id != case_matter.tenant_id
            or party.case_matter_id != case_matter.case_matter_id
            or party.matter_fingerprint != case_matter.fingerprint
        ):
            _fail("L9A4_P2C1_PARTY_MATTER_MISMATCH")
        if (
            acting_capacity.tenant_id != case_matter.tenant_id
            or acting_capacity.case_matter_id != case_matter.case_matter_id
            or acting_capacity.matter_fingerprint != case_matter.fingerprint
            or acting_capacity.party_id != party.party_id
            or acting_capacity.subject_reference != party.subject_reference
            or acting_capacity.subject_identity_fingerprint != party.subject_identity_fingerprint
            or acting_capacity.principal_id != actor_principal_id
        ):
            _fail("L9A4_P2C1_CAPACITY_CORRELATION_MISMATCH")
        if issued < acting_capacity.effective_from or (
            acting_capacity.effective_until is not None and issued >= acting_capacity.effective_until
        ):
            _fail("L9A4_P2C1_CAPACITY_NOT_VALID_AT_ISSUANCE")
        if (
            instrument.tenant_id != case_matter.tenant_id
            or instrument.case_matter_id != case_matter.case_matter_id
            or instrument.matter_fingerprint != case_matter.fingerprint
            or instrument.effective_from > issued
        ):
            _fail("L9A4_P2C1_INSTRUMENT_CORRELATION_INVALID")
        if (
            lifecycle.tenant_id != instrument.tenant_id
            or lifecycle.case_matter_id != instrument.case_matter_id
            or lifecycle.matter_fingerprint != instrument.matter_fingerprint
            or lifecycle.instrument_id != instrument.instrument_id
            or lifecycle.version != instrument.version
            or lifecycle.instrument_fingerprint != instrument.fingerprint
            or lifecycle.status is not LegalClientMatterAcceptanceInstrumentLifecycleStatus.ACTIVE
        ):
            _fail("L9A4_P2C1_LIFECYCLE_CORRELATION_INVALID")
        if (
            approval.tenant_id != instrument.tenant_id
            or approval.case_matter_id != instrument.case_matter_id
            or approval.matter_fingerprint != instrument.matter_fingerprint
            or approval.instrument_id != instrument.instrument_id
            or approval.version != instrument.version
            or approval.instrument_fingerprint != instrument.fingerprint
            or approval.content_fingerprint != instrument.content_fingerprint
            or approval.decision is not LegalClientMatterAcceptanceInstrumentApprovalDecision.APPROVED
            or approval.effective_from > issued
        ):
            _fail("L9A4_P2C1_APPROVAL_CORRELATION_INVALID")
        return cls(
            schema=SCHEMA,
            context_version=VERSION,
            acceptance_context_id=acceptance_context_id,
            tenant_id=case_matter.tenant_id,
            actor_principal_id=actor_principal_id,
            case_matter_id=case_matter.case_matter_id,
            matter_reference=case_matter.matter_reference,
            matter_fingerprint=case_matter.fingerprint,
            party_id=party.party_id,
            subject_reference=party.subject_reference,
            subject_identity_fingerprint=party.subject_identity_fingerprint,
            capacity_id=acting_capacity.capacity_id,
            capacity_type=acting_capacity.capacity_type,
            capacity_fingerprint=acting_capacity.fingerprint,
            capacity_effective_from=acting_capacity.effective_from,
            capacity_effective_until=acting_capacity.effective_until,
            instrument_id=instrument.instrument_id,
            instrument_version=instrument.version,
            instrument_fingerprint=instrument.fingerprint,
            content_fingerprint=instrument.content_fingerprint,
            content_reference=instrument.content_reference,
            title=instrument.title,
            review_scope=instrument.review_scope,
            instrument_effective_from=instrument.effective_from,
            lifecycle_status=lifecycle.status,
            lifecycle_fingerprint=lifecycle.fingerprint,
            lifecycle_evidence_fingerprint=lifecycle.lifecycle_evidence_fingerprint,
            approval_id=approval.approval_id,
            approval_decision=approval.decision,
            approval_fingerprint=approval.fingerprint,
            approval_effective_from=approval.effective_from,
            issuer_evidence_reference=issuer_evidence_reference,
            issuer_evidence_fingerprint=issuer_evidence_fingerprint,
            issued_at=issued,
            expires_at=expires,
            replay_key=replay_key,
        )

    def to_dict(self) -> dict[str, object]:
        """Serialize exact server evidence; no client-safe projection is implied."""
        return {field: _json_value(getattr(self, field)) for field in _FIELDS}

    @classmethod
    def from_dict(cls, payload: Mapping[str, object]) -> "LegalClientAcceptanceContext":
        """Hydrate only the exact schema and verify the supplied fingerprint."""
        if not isinstance(payload, Mapping) or set(payload) != set(_FIELDS):
            _fail("L9A4_P2C1_SCHEMA_INVALID")
        values = dict(payload)
        stored = values.pop("fingerprint")
        try:
            for field, enum_type in (
                ("capacity_type", LegalClientActingCapacityType),
                ("lifecycle_status", LegalClientMatterAcceptanceInstrumentLifecycleStatus),
                ("approval_decision", LegalClientMatterAcceptanceInstrumentApprovalDecision),
            ):
                if isinstance(values.get(field), str):
                    values[field] = enum_type(values[field])
        except (TypeError, ValueError) as error:
            _fail("L9A4_P2C1_ENUM_INVALID", error)
        result = cls(**cast(Any, values))
        if not isinstance(stored, str) or not hmac.compare_digest(stored, result.fingerprint):
            _fail("L9A4_P2C1_FINGERPRINT_MISMATCH")
        return result


__all__ = [
    "CONTEXT_FIELDS",
    "SCHEMA",
    "VERSION",
    "LegalClientAcceptanceContext",
    "LegalClientAcceptanceContextError",
]


# ARTIFACT: legal_client_acceptance_context.py
# VERSION: v1.0.0-L9A4-P2C1-CLIENT-ACCEPTANCE-CONTEXT
# AUTHORITY BOUNDARY: immutable server correlation evidence only; no acceptance issuance
# TENANT POSTURE: exact tenant/matter/party/capacity/instrument scope; no cross-tenant fallback
# FAIL-CLOSED POSTURE: malformed, stale, non-ACTIVE, non-APPROVED, expired or drifted evidence rejects
# FINANCIAL EXECUTION AUTHORITY: none; Kennel EOS remains exclusive
# END OF WILSY OS SOVEREIGN ARTIFACT
