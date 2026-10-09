"""WILSY OS matter acceptance-instrument approval evidence domain.

TITLE: WILSY OS Legal Client Matter Acceptance Instrument Approval
VERSION: v1.0.0-L9A4-P2B1-MATTER-ACCEPTANCE-INSTRUMENT-APPROVAL
AUTHORITY: Wilsy OS Core Governance / Python EOS Legal Operations
EPITOME: Bind one immutable firm-side approval decision to one exact tenant,
         CaseMatter, acceptance instrument version, and client-visible content
         without creating persistence, currentness, visibility, acceptance,
         engagement, representation, Court, or financial authority.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tools/eos/legal_operations/domain/legal_client_matter_acceptance_instrument_approval.py
COLLABORATION / OWNERSHIP: CaseMatter owns matter identity and lifecycle;
                            LegalClientMatterAcceptanceInstrument owns the
                            reviewable version/content identity; this module
                            owns only immutable approval-decision evidence.
                            A later IAM-aware orchestrator must authenticate
                            the approver and a later registry must own durable
                            replay/currentness composition.
CERTIFICATION / UPDATE DATE: 2026-09-26
CHANGELOG: v1.0.0-L9A4-P2B1-MATTER-ACCEPTANCE-INSTRUMENT-APPROVAL establishes
           exact matter/instrument subject binding, APPROVED/REJECTED decision
           evidence, opaque approver capacity and authorization/approval
           provenance, UTC chronology, idempotency identity, dual semantic
           fingerprints, strict hydration, and an OPEN CaseMatter factory.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2; ISO 27001.
SECURITY / PRIVACY POSTURE: Opaque identifiers, references, and SHA3-512
                             fingerprints only; no client PII, raw content,
                             credentials, tokens, or secret material.
TENANT BOUNDARY: Tenant, CaseMatter, and matter fingerprint are derived from
                 one exact canonical CaseMatter by the factory; direct values
                 remain explicitly tenant-scoped and never infer cross-tenant
                 identity.
AUTHORITY BOUNDARY: Historical firm-side approval decision evidence only. The
                    value does not authenticate or authorize an approver,
                    determine current approval, grant visibility, create client
                    acceptance, engagement, representation, Court authority,
                    or financial authority.
FINANCIAL AUTHORITY BOUNDARY: None; Kennel EOS remains the exclusive financial
                              execution and settlement authority.
TRANSACTION BOUNDARY: Pure immutable in-memory construction and deterministic
                      serialization; no database, HTTP, IAM, transaction,
                      retry, notification, currentness, or lifecycle mutation.
FAIL-CLOSED DECLARATION: Malformed scope, decision, evidence, chronology,
                         schema, or fingerprint drift rejects without coercive
                         repair or authority inference.
"""
from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from datetime import datetime, timezone
from enum import StrEnum
import hashlib
import hmac
import json
import re
from typing import Any, Final, NoReturn, cast
import unicodedata

from tools.eos.legal_operations.domain.legal_client_matter_acceptance_instrument import (
    LegalClientMatterAcceptanceInstrument,
)
from tools.eos.legal_operations.domain.legal_operations_lifecycle import (
    CaseMatter,
    CaseMatterState,
)


VERSION: Final[str] = (
    "v1.0.0-L9A4-P2B1-MATTER-ACCEPTANCE-INSTRUMENT-APPROVAL"
)
SCHEMA: Final[str] = "WILSY-LEGAL-CLIENT-MATTER-ACCEPTANCE-INSTRUMENT-APPROVAL/V1"
_IDENTITY: Final[re.Pattern[str]] = re.compile(
    r"^[A-Za-z0-9][A-Za-z0-9._:-]{0,159}$"
)
_HEX: Final[re.Pattern[str]] = re.compile(r"^[0-9a-f]{128}$")
_FORBIDDEN_TENANTS: Final[frozenset[str]] = frozenset(
    {"default", "global", "global_root", "root", "master", "*"}
)


class LegalClientMatterAcceptanceInstrumentApprovalDecision(StrEnum):
    """Closed immutable decision vocabulary for one exact instrument version.

    ``APPROVED`` and ``REJECTED`` are historical decision events only. They do
    not represent lifecycle states, currentness, client acceptance, or any
    downstream legal or financial authority.
    """

    APPROVED = "APPROVED"
    REJECTED = "REJECTED"


class LegalClientMatterAcceptanceInstrumentApprovalError(ValueError):
    """Stable fail-closed approval-domain error without supplied-value leakage."""

    def __init__(self, code: str) -> None:
        """Expose only a bounded validation code, never authority-bearing input."""
        self.code = code
        super().__init__(code)


_FIELDS: Final[tuple[str, ...]] = (
    "schema",
    "approval_version",
    "tenant_id",
    "case_matter_id",
    "matter_fingerprint",
    "approval_id",
    "instrument_id",
    "version",
    "instrument_fingerprint",
    "content_fingerprint",
    "decision",
    "approver_principal_id",
    "approver_capacity_reference",
    "authorization_evidence_reference",
    "authorization_evidence_fingerprint",
    "approval_evidence_reference",
    "approval_evidence_fingerprint",
    "occurred_at",
    "effective_from",
    "idempotency_key",
    "fingerprint",
)
APPROVAL_FIELDS: Final[frozenset[str]] = frozenset(_FIELDS)


def _fail(code: str, cause: BaseException | None = None) -> NoReturn:
    """Raise one stable error while retaining only an internal technical cause."""
    error = LegalClientMatterAcceptanceInstrumentApprovalError(code)
    if cause is None:
        raise error
    raise error from cause


def _identity(name: str, value: object) -> str:
    """Require one bounded opaque identity without trimming or coercion."""
    if (
        not isinstance(value, str)
        or value != value.strip()
        or _IDENTITY.fullmatch(value) is None
    ):
        _fail(f"L9A4_P2B1_{name.upper()}_INVALID")
    return cast(str, value)


def _tenant(value: object) -> str:
    """Require explicit tenant scope and reject pseudo/global tenants."""
    tenant = _identity("tenant_id", value)
    if tenant.casefold() in _FORBIDDEN_TENANTS:
        _fail("L9A4_P2B1_TENANT_REQUIRED")
    return tenant


def _fingerprint(name: str, value: object) -> str:
    """Require one lowercase SHA3-512 hexadecimal fingerprint."""
    if not isinstance(value, str) or _HEX.fullmatch(value) is None:
        _fail(f"L9A4_P2B1_{name.upper()}_INVALID")
    return value


def _reference(name: str, value: object, *, limit: int = 512) -> str:
    """Require bounded NFC-normalized single-line opaque evidence text."""
    if (
        not isinstance(value, str)
        or not value
        or value != value.strip()
        or len(value) > limit
        or any(
            ord(character) < 32
            or 0x7F <= ord(character) <= 0x9F
            or 0xD800 <= ord(character) <= 0xDFFF
            for character in value
        )
    ):
        _fail(f"L9A4_P2B1_{name.upper()}_INVALID")
    normalized = unicodedata.normalize("NFC", value)
    if not normalized or len(normalized) > limit:
        _fail(f"L9A4_P2B1_{name.upper()}_INVALID")
    return normalized


def _timestamp(name: str, value: object) -> datetime:
    """Require aware chronology and normalize it to UTC with microseconds."""
    parsed = value
    if isinstance(parsed, str):
        try:
            parsed = datetime.fromisoformat(parsed.replace("Z", "+00:00"))
        except ValueError as error:
            _fail(f"L9A4_P2B1_{name.upper()}_INVALID", error)
    if (
        not isinstance(parsed, datetime)
        or parsed.tzinfo is None
        or parsed.utcoffset() is None
    ):
        _fail(f"L9A4_P2B1_{name.upper()}_INVALID")
    return parsed.astimezone(timezone.utc)


def _json_value(value: object) -> object:
    """Convert immutable values to deterministic JSON-safe values."""
    if isinstance(value, datetime):
        return (
            value.astimezone(timezone.utc)
            .isoformat(timespec="microseconds")
            .replace("+00:00", "Z")
        )
    if isinstance(value, StrEnum):
        return value.value
    return value


@dataclass(frozen=True, slots=True)
class LegalClientMatterAcceptanceInstrumentApproval:
    """Immutable approval decision evidence for one exact matter instrument.

    The object binds the canonical tenant/matter and both instrument/content
    fingerprints. It records opaque approver and evidence references without
    authenticating the actor or interpreting a role. A later IAM-aware caller
    must prove authority, while a later registry/currentness composer owns
    persistence, chronology across events, and presentability decisions.
    """

    tenant_id: str
    case_matter_id: str
    matter_fingerprint: str
    approval_id: str
    instrument_id: str
    version: str
    instrument_fingerprint: str
    content_fingerprint: str
    decision: LegalClientMatterAcceptanceInstrumentApprovalDecision | str
    approver_principal_id: str
    approver_capacity_reference: str
    authorization_evidence_reference: str
    authorization_evidence_fingerprint: str
    approval_evidence_reference: str
    approval_evidence_fingerprint: str
    occurred_at: datetime
    effective_from: datetime
    idempotency_key: str
    schema: str = SCHEMA
    approval_version: str = VERSION
    fingerprint: str = ""

    def __post_init__(self) -> None:
        """Validate and fingerprint the complete immutable evidence record."""
        tenant = _tenant(self.tenant_id)
        matter = _identity("case_matter_id", self.case_matter_id)
        matter_fingerprint = _fingerprint(
            "matter_fingerprint", self.matter_fingerprint
        )
        approval_id = _identity("approval_id", self.approval_id)
        instrument_id = _identity("instrument_id", self.instrument_id)
        version = _identity("version", self.version)
        instrument_fingerprint = _fingerprint(
            "instrument_fingerprint", self.instrument_fingerprint
        )
        content_fingerprint = _fingerprint(
            "content_fingerprint", self.content_fingerprint
        )
        approver = _identity(
            "approver_principal_id", self.approver_principal_id
        )
        capacity = _reference(
            "approver_capacity_reference",
            self.approver_capacity_reference,
            limit=240,
        )
        authorization_reference = _reference(
            "authorization_evidence_reference",
            self.authorization_evidence_reference,
        )
        authorization_fingerprint = _fingerprint(
            "authorization_evidence_fingerprint",
            self.authorization_evidence_fingerprint,
        )
        approval_reference = _reference(
            "approval_evidence_reference",
            self.approval_evidence_reference,
        )
        approval_fingerprint = _fingerprint(
            "approval_evidence_fingerprint",
            self.approval_evidence_fingerprint,
        )
        occurred_at = _timestamp("occurred_at", self.occurred_at)
        effective_from = _timestamp("effective_from", self.effective_from)
        idempotency_key = _reference(
            "idempotency_key", self.idempotency_key, limit=240
        )
        try:
            decision = LegalClientMatterAcceptanceInstrumentApprovalDecision(
                self.decision
            )
        except (TypeError, ValueError) as error:
            _fail("L9A4_P2B1_DECISION_INVALID", error)

        if effective_from < occurred_at:
            _fail("L9A4_P2B1_EFFECTIVE_FROM_BEFORE_OCCURRED_AT")
        if self.schema != SCHEMA or self.approval_version != VERSION:
            _fail("L9A4_P2B1_IDENTITY_INVALID")

        object.__setattr__(self, "tenant_id", tenant)
        object.__setattr__(self, "case_matter_id", matter)
        object.__setattr__(self, "matter_fingerprint", matter_fingerprint)
        object.__setattr__(self, "approval_id", approval_id)
        object.__setattr__(self, "instrument_id", instrument_id)
        object.__setattr__(self, "version", version)
        object.__setattr__(self, "instrument_fingerprint", instrument_fingerprint)
        object.__setattr__(self, "content_fingerprint", content_fingerprint)
        object.__setattr__(self, "decision", decision)
        object.__setattr__(self, "approver_principal_id", approver)
        object.__setattr__(self, "approver_capacity_reference", capacity)
        object.__setattr__(
            self,
            "authorization_evidence_reference",
            authorization_reference,
        )
        object.__setattr__(
            self,
            "authorization_evidence_fingerprint",
            authorization_fingerprint,
        )
        object.__setattr__(self, "approval_evidence_reference", approval_reference)
        object.__setattr__(
            self,
            "approval_evidence_fingerprint",
            approval_fingerprint,
        )
        object.__setattr__(self, "occurred_at", occurred_at)
        object.__setattr__(self, "effective_from", effective_from)
        object.__setattr__(self, "idempotency_key", idempotency_key)

        payload = {
            field: _json_value(getattr(self, field)) for field in _FIELDS[:-1]
        }
        digest = hashlib.sha3_512(
            json.dumps(
                payload,
                ensure_ascii=False,
                allow_nan=False,
                sort_keys=False,
                separators=(",", ":"),
            ).encode("utf-8")
        ).hexdigest()
        if self.fingerprint and (
            not isinstance(self.fingerprint, str)
            or not hmac.compare_digest(self.fingerprint, digest)
        ):
            _fail("L9A4_P2B1_FINGERPRINT_MISMATCH")
        object.__setattr__(self, "fingerprint", digest)

    @property
    def version_id(self) -> str:
        """Return the exact instrument/version identity bound by this decision."""
        return f"{self.instrument_id}:{self.version}"

    def to_dict(self) -> dict[str, object]:
        """Serialize exact approval evidence without PII or raw document body."""
        return {field: _json_value(getattr(self, field)) for field in _FIELDS}

    @classmethod
    def from_dict(
        cls,
        payload: Mapping[str, object],
    ) -> "LegalClientMatterAcceptanceInstrumentApproval":
        """Hydrate only the exact schema and verify its supplied fingerprint."""
        if not isinstance(payload, Mapping) or set(payload) != set(_FIELDS):
            _fail("L9A4_P2B1_SCHEMA_INVALID")
        values = dict(payload)
        stored = values.pop("fingerprint")
        try:
            if isinstance(values.get("decision"), str):
                values["decision"] = (
                    LegalClientMatterAcceptanceInstrumentApprovalDecision(
                        values["decision"]
                    )
                )
        except (TypeError, ValueError) as error:
            _fail("L9A4_P2B1_DECISION_INVALID", error)
        result = cls(**cast(Any, values))
        if (
            not isinstance(stored, str)
            or not hmac.compare_digest(stored, result.fingerprint)
        ):
            _fail("L9A4_P2B1_FINGERPRINT_MISMATCH")
        return result


def record_legal_client_matter_acceptance_instrument_approval(
    *,
    case_matter: CaseMatter,
    instrument: LegalClientMatterAcceptanceInstrument,
    approval_id: str,
    decision: LegalClientMatterAcceptanceInstrumentApprovalDecision | str,
    approver_principal_id: str,
    approver_capacity_reference: str,
    authorization_evidence_reference: str,
    authorization_evidence_fingerprint: str,
    approval_evidence_reference: str,
    approval_evidence_fingerprint: str,
    occurred_at: datetime,
    effective_from: datetime,
    idempotency_key: str,
) -> LegalClientMatterAcceptanceInstrumentApproval:
    """Create approval evidence from one exact OPEN CaseMatter and instrument.

    Tenant, matter identity, matter fingerprint, instrument identity, version,
    instrument fingerprint, and content fingerprint are derived from canonical
    domain values. The factory does not authenticate the approver, query IAM,
    persist evidence, derive currentness, grant visibility, create acceptance,
    or create any engagement, representation, Court, or financial fact.
    """
    if type(case_matter) is not CaseMatter:
        _fail("L9A4_P2B1_CASE_MATTER_REQUIRED")
    if case_matter.state is not CaseMatterState.OPEN:
        _fail("L9A4_P2B1_OPEN_CASE_MATTER_REQUIRED")
    if type(instrument) is not LegalClientMatterAcceptanceInstrument:
        _fail("L9A4_P2B1_INSTRUMENT_REQUIRED")
    if (
        instrument.tenant_id != case_matter.tenant_id
        or instrument.case_matter_id != case_matter.case_matter_id
        or instrument.matter_fingerprint != case_matter.fingerprint
    ):
        _fail("L9A4_P2B1_SUBJECT_MISMATCH")
    return LegalClientMatterAcceptanceInstrumentApproval(
        tenant_id=case_matter.tenant_id,
        case_matter_id=case_matter.case_matter_id,
        matter_fingerprint=case_matter.fingerprint,
        approval_id=approval_id,
        instrument_id=instrument.instrument_id,
        version=instrument.version,
        instrument_fingerprint=instrument.fingerprint,
        content_fingerprint=instrument.content_fingerprint,
        decision=decision,
        approver_principal_id=approver_principal_id,
        approver_capacity_reference=approver_capacity_reference,
        authorization_evidence_reference=authorization_evidence_reference,
        authorization_evidence_fingerprint=authorization_evidence_fingerprint,
        approval_evidence_reference=approval_evidence_reference,
        approval_evidence_fingerprint=approval_evidence_fingerprint,
        occurred_at=occurred_at,
        effective_from=effective_from,
        idempotency_key=idempotency_key,
    )


__all__ = [
    "APPROVAL_FIELDS",
    "SCHEMA",
    "VERSION",
    "LegalClientMatterAcceptanceInstrumentApproval",
    "LegalClientMatterAcceptanceInstrumentApprovalDecision",
    "LegalClientMatterAcceptanceInstrumentApprovalError",
    "record_legal_client_matter_acceptance_instrument_approval",
]


# ARTIFACT: legal_client_matter_acceptance_instrument_approval.py
# VERSION: v1.0.0-L9A4-P2B1-MATTER-ACCEPTANCE-INSTRUMENT-APPROVAL
# AUTHORITY BOUNDARY: immutable matter-instrument approval decision evidence only
# TENANT POSTURE: exact tenant/CaseMatter/instrument/version and dual fingerprints
# FAIL-CLOSED POSTURE: malformed, stale, divergent, or tampered evidence rejects
# FINANCIAL EXECUTION AUTHORITY: none; Kennel EOS exclusively
# END OF WILSY OS SOVEREIGN ARTIFACT
