"""WILSY OS immutable firm-side Engagement decision evidence.

TITLE: WILSY OS Legal Client Matter Engagement Firm Decision
VERSION: v1.0.0-L9C1-ENGAGEMENT-FIRM-DECISION
AUTHORITY: Wilsy OS Core Governance / Python EOS Legal Operations
EPITOME: Record one explicit firm-side decision about whether one bounded
         Engagement may be entered for one exact client party and CaseMatter.
         This value is decision evidence only; it does not create Engagement,
         authenticate an actor, establish conflict clearance, prove mandate
         currentness, authorize Representation or Court action, or execute
         finance.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tools/eos/legal_operations/domain/legal_client_matter_engagement_firm_decision.py
COLLABORATION / OWNERSHIP: CaseMatter owns matter identity; LegalMatterParty
                            owns party and subject binding; a future IAM-aware
                            orchestrator owns actor authorization. L9C1 owns
                            only immutable decision evidence.
CERTIFICATION / UPDATE DATE: 2026-09-27
CHANGELOG: v1.0.0-L9C1-ENGAGEMENT-FIRM-DECISION establishes the bounded
           ACCEPTED/DECLINED/REQUIRES_REVIEW vocabulary, exact tenant/matter/
           client-party/subject binding, explicit actor and authorization
           provenance, aware UTC chronology, strict hydration and deterministic
           SHA3-512 integrity. It creates no Engagement or downstream authority.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2; ISO 27001.
SECURITY / PRIVACY POSTURE: Opaque identifiers, bounded references and
                             lowercase SHA3-512 fingerprints only; no PII,
                             credentials, tokens, raw review narrative or
                             permission claims are retained.
TENANT BOUNDARY: Tenant, matter, client party and subject identity are derived
                 from exact canonical values; no fallback or cross-tenant
                 substitution exists.
AUTHORITY BOUNDARY: Historical firm decision evidence only. The actor field is
                    provenance, not permission. ClientAcceptance, conflict,
                    mandate, IAM, Engagement, Representation and Court remain
                    separate authorities.
FINANCIAL AUTHORITY BOUNDARY: No fee, billing, payment, settlement, release or
                              execution truth; Kennel EOS remains exclusive.
TRANSACTION BOUNDARY: Pure immutable in-memory construction and deterministic
                      serialization only; no database, HTTP, registry, IAM,
                      clock read, retry or network behavior.
FAIL-CLOSED DECLARATION: Malformed, cross-scope, unknown, naive, divergent or
                         authority-expanding evidence rejects without coercion.
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

from tools.eos.legal_operations.domain.legal_matter_party import (
    LegalMatterParty,
    LegalMatterPartyRole,
    LegalMatterPartySide,
)
from tools.eos.legal_operations.domain.legal_operations_lifecycle import (
    CaseMatter,
    CaseMatterState,
)


VERSION: Final[str] = "v1.0.0-L9C1-ENGAGEMENT-FIRM-DECISION"
SCHEMA: Final[str] = "WILSY-LEGAL-CLIENT-MATTER-ENGAGEMENT-FIRM-DECISION/V1"
_IDENTITY: Final[re.Pattern[str]] = re.compile(
    r"^[A-Za-z0-9][A-Za-z0-9._:-]{0,159}$"
)
_SUBJECT_REFERENCE: Final[re.Pattern[str]] = re.compile(
    r"^(crm|contact|organization|entity|client|subject):"
    r"[A-Za-z0-9][A-Za-z0-9._:-]{0,191}$"
)
_HEX: Final[re.Pattern[str]] = re.compile(r"^[0-9a-f]{128}$")
_FORBIDDEN_TENANTS: Final[frozenset[str]] = frozenset(
    {"default", "global", "global_root", "root", "master", "*"}
)
_FIELDS: Final[tuple[str, ...]] = (
    "schema",
    "decision_version",
    "decision_id",
    "tenant_id",
    "case_matter_id",
    "matter_fingerprint",
    "client_party_id",
    "subject_reference",
    "subject_identity_fingerprint",
    "decision",
    "decision_actor_principal_id",
    "authorization_evidence_reference",
    "authorization_evidence_fingerprint",
    "source_evidence_reference",
    "source_evidence_fingerprint",
    "occurred_at",
    "effective_from",
    "idempotency_key",
    "fingerprint",
)
FIRM_DECISION_FIELDS: Final[frozenset[str]] = frozenset(_FIELDS)


class LegalClientMatterEngagementFirmDecisionType(StrEnum):
    """Closed firm-decision vocabulary; ACCEPTED is the sole positive state."""

    ACCEPTED = "ACCEPTED"
    DECLINED = "DECLINED"
    REQUIRES_REVIEW = "REQUIRES_REVIEW"


class LegalClientMatterEngagementFirmDecisionError(ValueError):
    """Stable non-sensitive validation failure for decision evidence."""

    def __init__(self, code: str) -> None:
        """Expose only a bounded code and never supplied authority data."""
        self.code = code
        super().__init__(code)


def _fail(code: str, cause: BaseException | None = None) -> NoReturn:
    """Raise one stable failure while retaining only an internal cause."""
    error = LegalClientMatterEngagementFirmDecisionError(code)
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
        _fail(f"L9C1_{name.upper()}_INVALID")
    return cast(str, value)


def _tenant(value: object) -> str:
    """Require one explicit non-global tenant identity."""
    tenant = _identity("tenant_id", value)
    if tenant.casefold() in _FORBIDDEN_TENANTS:
        _fail("L9C1_TENANT_REQUIRED")
    return tenant


def _fingerprint(name: str, value: object) -> str:
    """Require one lowercase SHA3-512 hexadecimal fingerprint."""
    if not isinstance(value, str) or _HEX.fullmatch(value) is None:
        _fail(f"L9C1_{name.upper()}_INVALID")
    return value


def _reference(name: str, value: object, *, limit: int = 512) -> str:
    """Require bounded NFC single-line evidence text."""
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
        _fail(f"L9C1_{name.upper()}_INVALID")
    normalized = unicodedata.normalize("NFC", value)
    if not normalized or len(normalized) > limit:
        _fail(f"L9C1_{name.upper()}_INVALID")
    return normalized


def _subject(value: object) -> str:
    """Require the canonical opaque subject-reference vocabulary."""
    reference = _reference("subject_reference", value, limit=224)
    if _SUBJECT_REFERENCE.fullmatch(reference) is None:
        _fail("L9C1_SUBJECT_REFERENCE_INVALID")
    return reference


def _timestamp(name: str, value: object) -> datetime:
    """Require an aware timestamp and normalize it to UTC microseconds."""
    parsed = value
    if isinstance(parsed, str):
        try:
            parsed = datetime.fromisoformat(parsed.replace("Z", "+00:00"))
        except ValueError as error:
            _fail(f"L9C1_{name.upper()}_INVALID", error)
    if (
        not isinstance(parsed, datetime)
        or parsed.tzinfo is None
        or parsed.utcoffset() is None
    ):
        _fail(f"L9C1_{name.upper()}_INVALID")
    return parsed.astimezone(timezone.utc)


def _json_value(value: object) -> object:
    """Convert immutable values into deterministic JSON-safe values."""
    if isinstance(value, datetime):
        return value.astimezone(timezone.utc).isoformat(
            timespec="microseconds"
        ).replace("+00:00", "Z")
    if isinstance(value, StrEnum):
        return value.value
    return value


@dataclass(frozen=True, slots=True)
class LegalClientMatterEngagementFirmDecision:
    """Immutable decision evidence for one exact client-matter context.

    ``ACCEPTED`` only satisfies the future firm-decision prerequisite. It does
    not form an Engagement, evaluate role permission, or replace the later
    ClientAcceptance, conflict, mandate-currentness, IAM, or registry gates.
    """

    decision_id: str
    tenant_id: str
    case_matter_id: str
    matter_fingerprint: str
    client_party_id: str
    subject_reference: str
    subject_identity_fingerprint: str
    decision: LegalClientMatterEngagementFirmDecisionType | str
    decision_actor_principal_id: str
    authorization_evidence_reference: str
    authorization_evidence_fingerprint: str
    source_evidence_reference: str
    source_evidence_fingerprint: str
    occurred_at: datetime
    effective_from: datetime
    idempotency_key: str
    schema: str = SCHEMA
    decision_version: str = VERSION
    fingerprint: str = ""

    def __post_init__(self) -> None:
        """Validate every semantic field and compute or verify integrity."""
        if self.schema != SCHEMA or self.decision_version != VERSION:
            _fail("L9C1_IDENTITY_INVALID")
        try:
            decision = LegalClientMatterEngagementFirmDecisionType(self.decision)
        except (TypeError, ValueError) as error:
            _fail("L9C1_DECISION_INVALID", error)
        occurred = _timestamp("occurred_at", self.occurred_at)
        effective = _timestamp("effective_from", self.effective_from)
        if effective < occurred:
            _fail("L9C1_EFFECTIVE_FROM_BEFORE_OCCURRED")
        normalized: dict[str, object] = {
            "decision_id": _identity("decision_id", self.decision_id),
            "tenant_id": _tenant(self.tenant_id),
            "case_matter_id": _identity("case_matter_id", self.case_matter_id),
            "matter_fingerprint": _fingerprint(
                "matter_fingerprint", self.matter_fingerprint
            ),
            "client_party_id": _identity("client_party_id", self.client_party_id),
            "subject_reference": _subject(self.subject_reference),
            "subject_identity_fingerprint": _fingerprint(
                "subject_identity_fingerprint", self.subject_identity_fingerprint
            ),
            "decision": decision,
            "decision_actor_principal_id": _identity(
                "decision_actor_principal_id", self.decision_actor_principal_id
            ),
            "authorization_evidence_reference": _reference(
                "authorization_evidence_reference",
                self.authorization_evidence_reference,
            ),
            "authorization_evidence_fingerprint": _fingerprint(
                "authorization_evidence_fingerprint",
                self.authorization_evidence_fingerprint,
            ),
            "source_evidence_reference": _reference(
                "source_evidence_reference", self.source_evidence_reference
            ),
            "source_evidence_fingerprint": _fingerprint(
                "source_evidence_fingerprint", self.source_evidence_fingerprint
            ),
            "occurred_at": occurred,
            "effective_from": effective,
            "idempotency_key": _reference(
                "idempotency_key", self.idempotency_key, limit=240
            ),
        }
        for field, value in normalized.items():
            object.__setattr__(self, field, value)
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
        if self.fingerprint:
            if not isinstance(self.fingerprint, str) or not hmac.compare_digest(
                self.fingerprint, digest
            ):
                _fail("L9C1_FINGERPRINT_MISMATCH")
        object.__setattr__(self, "fingerprint", digest)

    @property
    def is_engagement_forming(self) -> bool:
        """Return whether this evidence is the positive firm-decision state."""
        return self.decision is LegalClientMatterEngagementFirmDecisionType.ACCEPTED

    def to_dict(self) -> dict[str, object]:
        """Serialize exact decision evidence without raw authority data."""
        return {field: _json_value(getattr(self, field)) for field in _FIELDS}

    @classmethod
    def from_dict(
        cls, payload: Mapping[str, object]
    ) -> "LegalClientMatterEngagementFirmDecision":
        """Hydrate only the exact schema and verify deterministic integrity."""
        if not isinstance(payload, Mapping) or set(payload) != set(_FIELDS):
            _fail("L9C1_SCHEMA_INVALID")
        values = dict(payload)
        stored = values.pop("fingerprint")
        result = cls(**cast(Any, values))
        if not isinstance(stored, str) or not hmac.compare_digest(
            stored, result.fingerprint
        ):
            _fail("L9C1_FINGERPRINT_MISMATCH")
        return result

    @classmethod
    def from_canonical(
        cls,
        *,
        decision_id: str,
        case_matter: CaseMatter,
        party: LegalMatterParty,
        decision: LegalClientMatterEngagementFirmDecisionType | str,
        decision_actor_principal_id: str,
        authorization_evidence_reference: str,
        authorization_evidence_fingerprint: str,
        source_evidence_reference: str,
        source_evidence_fingerprint: str,
        occurred_at: datetime,
        effective_from: datetime,
        idempotency_key: str,
    ) -> "LegalClientMatterEngagementFirmDecision":
        """Derive exact tenant/matter/party bindings from canonical evidence.

        The factory requires an OPEN matter and a client-side CLIENT party. It
        intentionally does not accept ClientAcceptance, mandate or conflict
        objects: those are separate authorities composed later. Actor role and
        permission are likewise evaluated by a future IAM-aware orchestrator.
        """
        if type(case_matter) is not CaseMatter:
            _fail("L9C1_CASE_MATTER_REQUIRED")
        if type(party) is not LegalMatterParty:
            _fail("L9C1_PARTY_REQUIRED")
        try:
            case_matter.__post_init__()
            party.__post_init__()
        except Exception as error:
            _fail("L9C1_CANONICAL_EVIDENCE_INVALID", error)
        if case_matter.state is not CaseMatterState.OPEN:
            _fail("L9C1_OPEN_CASE_MATTER_REQUIRED")
        if party.party_side is not LegalMatterPartySide.CLIENT_SIDE:
            _fail("L9C1_CLIENT_PARTY_REQUIRED")
        if party.matter_role is not LegalMatterPartyRole.CLIENT:
            _fail("L9C1_CLIENT_PARTY_ROLE_REQUIRED")
        if (
            party.tenant_id != case_matter.tenant_id
            or party.case_matter_id != case_matter.case_matter_id
            or party.matter_fingerprint != case_matter.fingerprint
        ):
            _fail("L9C1_PARTY_MATTER_MISMATCH")
        occurred = _timestamp("occurred_at", occurred_at)
        effective = _timestamp("effective_from", effective_from)
        if effective < max(case_matter.opened_at, party.registered_at):
            _fail("L9C1_EFFECTIVE_FROM_INVALID")
        return cls(
            decision_id=decision_id,
            tenant_id=case_matter.tenant_id,
            case_matter_id=case_matter.case_matter_id,
            matter_fingerprint=case_matter.fingerprint,
            client_party_id=party.party_id,
            subject_reference=party.subject_reference,
            subject_identity_fingerprint=party.subject_identity_fingerprint,
            decision=decision,
            decision_actor_principal_id=decision_actor_principal_id,
            authorization_evidence_reference=authorization_evidence_reference,
            authorization_evidence_fingerprint=authorization_evidence_fingerprint,
            source_evidence_reference=source_evidence_reference,
            source_evidence_fingerprint=source_evidence_fingerprint,
            occurred_at=occurred,
            effective_from=effective,
            idempotency_key=idempotency_key,
        )


__all__ = [
    "FIRM_DECISION_FIELDS",
    "SCHEMA",
    "VERSION",
    "LegalClientMatterEngagementFirmDecision",
    "LegalClientMatterEngagementFirmDecisionError",
    "LegalClientMatterEngagementFirmDecisionType",
]


# ARTIFACT: legal_client_matter_engagement_firm_decision.py
# VERSION: v1.0.0-L9C1-ENGAGEMENT-FIRM-DECISION
# AUTHORITY BOUNDARY: immutable Engagement decision evidence only
# TENANT POSTURE: exact tenant/matter/client-party/subject binding; no fallback
# FAIL-CLOSED POSTURE: malformed, cross-scope, unknown or tampered evidence rejects
# FINANCIAL EXECUTION AUTHORITY: none; Kennel EOS exclusively
# END OF WILSY OS SOVEREIGN ARTIFACT
