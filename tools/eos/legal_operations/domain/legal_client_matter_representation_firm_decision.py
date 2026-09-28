"""WILSY OS immutable firm-side Representation decision evidence.

TITLE: WILSY OS Legal Client Matter Representation Firm Decision
VERSION: v1.0.0-L9C11-P2-FIRM-REPRESENTATION-DECISION
AUTHORITY: Wilsy OS Core Governance / Python EOS Legal Operations
EPITOME: Record one explicit firm-side decision about one exact client
         Representation appointment, designated principal and bounded scope.
         This value is decision evidence only; it does not form Representation,
         evaluate Engagement currentness, grant IAM, authorize Court action, or
         execute finance.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tools/eos/legal_operations/domain/legal_client_matter_representation_firm_decision.py
COLLABORATION / OWNERSHIP: The published client Representation authority owns
                            appointment evidence; Engagement, Mandate and
                            ActingCapacity own upstream lineage; this artifact
                            owns only the firm's immutable decision. Future IAM,
                            registry, currentness and formation authorities
                            remain separate.
CERTIFICATION / UPDATE DATE: 2026-09-28
CHANGELOG: v1.0.0-L9C11-P2 establishes ACCEPTED/DECLINED/REQUIRES_REVIEW
           firm decision evidence bound to the exact client authority,
           representative, client-authority-bounded non-Court scope and
           upstream lineage, with explicit UTC chronology, deterministic
           decision identity, strict hydration and SHA3-512 integrity. It
           creates no Representation, lifecycle,
           currentness, IAM, persistence, HTTP, Court or finance.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2; ISO 27001.
SECURITY / PRIVACY POSTURE: Opaque identifiers, bounded references and
                             lowercase SHA3-512 fingerprints only; no PII,
                             credentials, tokens or raw authority payloads.
TENANT BOUNDARY: Exact tenant, CaseMatter, client party and subject lineage
                 must remain identical to the client authority; no fallback.
AUTHORITY BOUNDARY: Historical firm decision evidence only. Decision actor is
                    provenance, not permission; ACCEPTED is not currentness or
                    a formed Representation.
FINANCIAL AUTHORITY BOUNDARY: No billing, payment, settlement, trust, release
                              or execution truth; Kennel EOS remains exclusive.
TRANSACTION BOUNDARY: Pure immutable construction, deterministic serialization
                      and strict hydration only; no database, IAM, transaction,
                      retry, clock, notification or network behavior.
FAIL-CLOSED DECLARATION: Mismatched client state, lineage, representative,
                         scope, chronology, schema or fingerprint rejects
                         without authority expansion.
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

from tools.eos.legal_operations.domain.legal_client_matter_representation_authority import (
    LegalClientMatterRepresentationAuthority,
    LegalClientMatterRepresentationAuthorityDecision,
)


VERSION: Final[str] = "v1.0.0-L9C11-P2-FIRM-REPRESENTATION-DECISION"
SCHEMA: Final[str] = "WILSY-LEGAL-CLIENT-MATTER-REPRESENTATION-FIRM-DECISION/V1"
_IDENTITY: Final[re.Pattern[str]] = re.compile(
    r"^[A-Za-z0-9][A-Za-z0-9._:-]{0,159}$"
)
_HEX: Final[re.Pattern[str]] = re.compile(r"^[0-9a-f]{128}$")
_FORBIDDEN_TENANTS: Final[frozenset[str]] = frozenset(
    {"default", "global", "global_root", "root", "master", "*"}
)
_NON_COURT_SCOPE_CAPABILITIES: Final[frozenset[str]] = frozenset(
    {
        "ADVISORY",
        "NEGOTIATION",
        "TRANSACTIONAL",
        "DISPUTE_PREPARATION",
        "LITIGATION_PREPARATION",
        "SETTLEMENT_NEGOTIATION",
    }
)
_KNOWN_MANDATE_CAPABILITIES: Final[frozenset[str]] = (
    _NON_COURT_SCOPE_CAPABILITIES
    | frozenset({"COURT_FILING_PREPARATION", "COURT_APPEARANCE_PREPARATION"})
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
    "engagement_id",
    "engagement_fingerprint",
    "mandate_id",
    "mandate_fingerprint",
    "acting_capacity_id",
    "acting_capacity_fingerprint",
    "representation_authority_id",
    "representation_authority_fingerprint",
    "client_authority_decision",
    "client_authority_effective_from",
    "client_authority_scope_capabilities",
    "representative_principal_id",
    "representative_role",
    "mandate_capabilities",
    "representation_scope_capabilities",
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
REPRESENTATION_FIRM_DECISION_FIELDS: Final[frozenset[str]] = frozenset(_FIELDS)


class LegalClientMatterRepresentationFirmDecisionType(StrEnum):
    """Closed firm decisions; ACCEPTED is the sole positive value."""

    ACCEPTED = "ACCEPTED"
    DECLINED = "DECLINED"
    REQUIRES_REVIEW = "REQUIRES_REVIEW"


class LegalClientMatterRepresentationFirmDecisionError(ValueError):
    """Stable, non-sensitive failure from firm-decision validation."""

    def __init__(self, code: str) -> None:
        """Expose only a bounded code and never supplied authority data."""
        self.code = code
        super().__init__(code)


def _fail(code: str, cause: BaseException | None = None) -> NoReturn:
    """Raise one stable failure while retaining technical cause internally."""
    error = LegalClientMatterRepresentationFirmDecisionError(code)
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
        _fail(f"L9C11_P2_{name.upper()}_INVALID")
    return cast(str, value)


def _tenant(value: object) -> str:
    """Require one explicit non-global tenant identity."""
    tenant = _identity("tenant_id", value)
    if tenant.casefold() in _FORBIDDEN_TENANTS:
        _fail("L9C11_P2_TENANT_REQUIRED")
    return tenant


def _fingerprint(name: str, value: object) -> str:
    """Require one lowercase SHA3-512 hexadecimal fingerprint."""
    if not isinstance(value, str) or _HEX.fullmatch(value) is None:
        _fail(f"L9C11_P2_{name.upper()}_INVALID")
    return value


def _reference(name: str, value: object, *, limit: int = 512) -> str:
    """Require bounded NFC single-line evidence/reference text."""
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
        _fail(f"L9C11_P2_{name.upper()}_INVALID")
    normalized = unicodedata.normalize("NFC", value)
    if not normalized or len(normalized) > limit:
        _fail(f"L9C11_P2_{name.upper()}_INVALID")
    return normalized


def _capabilities(name: str, value: object, *, allow_court: bool) -> tuple[str, ...]:
    """Normalize scope capabilities and reject unknown or Court values."""
    if not isinstance(value, (tuple, list, set, frozenset)) or not value:
        _fail(f"L9C11_P2_{name.upper()}_INVALID")
    normalized: set[str] = set()
    for item in value:
        label = getattr(item, "value", item)
        if not isinstance(label, str) or label != label.strip() or not label:
            _fail(f"L9C11_P2_{name.upper()}_INVALID")
        label = label.upper()
        if not allow_court and label.startswith("COURT_"):
            _fail("L9C11_P2_COURT_SCOPE_FORBIDDEN")
        if label not in (
            _KNOWN_MANDATE_CAPABILITIES if allow_court else _NON_COURT_SCOPE_CAPABILITIES
        ):
            _fail(f"L9C11_P2_{name.upper()}_INVALID")
        normalized.add(label)
    return tuple(sorted(normalized))


def _timestamp(name: str, value: object) -> datetime:
    """Require an aware timestamp and normalize it to UTC microseconds."""
    parsed = value
    if isinstance(parsed, str):
        try:
            parsed = datetime.fromisoformat(parsed.replace("Z", "+00:00"))
        except ValueError as error:
            _fail(f"L9C11_P2_{name.upper()}_INVALID", error)
    if (
        not isinstance(parsed, datetime)
        or parsed.tzinfo is None
        or parsed.utcoffset() is None
    ):
        _fail(f"L9C11_P2_{name.upper()}_INVALID")
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


def _decision_id(payload: dict[str, object]) -> str:
    """Derive a stable decision identity from all non-derived intent fields."""
    digest = hashlib.sha3_512(
        json.dumps(
            payload,
            ensure_ascii=False,
            allow_nan=False,
            sort_keys=False,
            separators=(",", ":"),
        ).encode("utf-8")
    ).hexdigest()
    return f"representation-firm-decision:{digest[:48]}"


def _digest(instance: "LegalClientMatterRepresentationFirmDecision") -> str:
    """Hash every declared semantic field except the derived fingerprint."""
    payload = {field: _json_value(getattr(instance, field)) for field in _FIELDS[:-1]}
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
class LegalClientMatterRepresentationFirmDecision:
    """Immutable firm decision evidence for one client authority appointment."""

    tenant_id: str
    case_matter_id: str
    matter_fingerprint: str
    client_party_id: str
    subject_reference: str
    subject_identity_fingerprint: str
    engagement_id: str
    engagement_fingerprint: str
    mandate_id: str
    mandate_fingerprint: str
    acting_capacity_id: str
    acting_capacity_fingerprint: str
    representation_authority_id: str
    representation_authority_fingerprint: str
    client_authority_decision: LegalClientMatterRepresentationAuthorityDecision | str
    client_authority_effective_from: datetime
    client_authority_scope_capabilities: tuple[str, ...] | list[str]
    representative_principal_id: str
    representative_role: str
    mandate_capabilities: tuple[str, ...] | list[str]
    representation_scope_capabilities: tuple[str, ...] | list[str]
    decision: LegalClientMatterRepresentationFirmDecisionType | str
    decision_actor_principal_id: str
    authorization_evidence_reference: str
    authorization_evidence_fingerprint: str
    source_evidence_reference: str
    source_evidence_fingerprint: str
    occurred_at: datetime
    effective_from: datetime
    idempotency_key: str
    decision_id: str = ""
    schema: str = SCHEMA
    decision_version: str = VERSION
    fingerprint: str = ""

    def __post_init__(self) -> None:
        """Validate immutable evidence and derive deterministic identity/hash."""
        normalized: dict[str, object] = {
            "tenant_id": _tenant(self.tenant_id),
            "case_matter_id": _identity("case_matter_id", self.case_matter_id),
            "matter_fingerprint": _fingerprint("matter_fingerprint", self.matter_fingerprint),
            "client_party_id": _identity("client_party_id", self.client_party_id),
            "subject_reference": _reference("subject_reference", self.subject_reference, limit=224),
            "subject_identity_fingerprint": _fingerprint("subject_identity_fingerprint", self.subject_identity_fingerprint),
            "engagement_id": _identity("engagement_id", self.engagement_id),
            "engagement_fingerprint": _fingerprint("engagement_fingerprint", self.engagement_fingerprint),
            "mandate_id": _identity("mandate_id", self.mandate_id),
            "mandate_fingerprint": _fingerprint("mandate_fingerprint", self.mandate_fingerprint),
            "acting_capacity_id": _identity("acting_capacity_id", self.acting_capacity_id),
            "acting_capacity_fingerprint": _fingerprint("acting_capacity_fingerprint", self.acting_capacity_fingerprint),
            "representation_authority_id": _identity("representation_authority_id", self.representation_authority_id),
            "representation_authority_fingerprint": _fingerprint("representation_authority_fingerprint", self.representation_authority_fingerprint),
            "client_authority_scope_capabilities": _capabilities(
                "client_authority_scope_capabilities",
                self.client_authority_scope_capabilities,
                allow_court=False,
            ),
            "representative_principal_id": _identity("representative_principal_id", self.representative_principal_id),
            "representative_role": _identity("representative_role", self.representative_role),
            "mandate_capabilities": _capabilities("mandate_capabilities", self.mandate_capabilities, allow_court=True),
            "representation_scope_capabilities": _capabilities("representation_scope_capabilities", self.representation_scope_capabilities, allow_court=False),
            "decision_actor_principal_id": _identity("decision_actor_principal_id", self.decision_actor_principal_id),
            "authorization_evidence_reference": _reference("authorization_evidence_reference", self.authorization_evidence_reference),
            "authorization_evidence_fingerprint": _fingerprint("authorization_evidence_fingerprint", self.authorization_evidence_fingerprint),
            "source_evidence_reference": _reference("source_evidence_reference", self.source_evidence_reference),
            "source_evidence_fingerprint": _fingerprint("source_evidence_fingerprint", self.source_evidence_fingerprint),
            "client_authority_effective_from": _timestamp("client_authority_effective_from", self.client_authority_effective_from),
            "occurred_at": _timestamp("occurred_at", self.occurred_at),
            "effective_from": _timestamp("effective_from", self.effective_from),
            "idempotency_key": _reference("idempotency_key", self.idempotency_key, limit=240),
        }
        try:
            client_decision = LegalClientMatterRepresentationAuthorityDecision(
                self.client_authority_decision
            )
            firm_decision = LegalClientMatterRepresentationFirmDecisionType(self.decision)
        except (TypeError, ValueError) as error:
            _fail("L9C11_P2_DECISION_INVALID", error)
        normalized["client_authority_decision"] = client_decision
        normalized["decision"] = firm_decision
        mandate_capabilities = cast(tuple[str, ...], normalized["mandate_capabilities"])
        representation_scope_capabilities = cast(
            tuple[str, ...], normalized["representation_scope_capabilities"]
        )
        client_authority_scope_capabilities = cast(
            tuple[str, ...], normalized["client_authority_scope_capabilities"]
        )
        if not set(representation_scope_capabilities).issubset(mandate_capabilities):
            _fail("L9C11_P2_SCOPE_EXCEEDS_MANDATE")
        if not set(representation_scope_capabilities).issubset(
            client_authority_scope_capabilities
        ):
            _fail("L9C11_P2_SCOPE_EXCEEDS_CLIENT_AUTHORITY")
        if firm_decision is LegalClientMatterRepresentationFirmDecisionType.ACCEPTED:
            if client_decision is not LegalClientMatterRepresentationAuthorityDecision.APPOINTED:
                _fail("L9C11_P2_CLIENT_AUTHORITY_NOT_APPOINTED")
        client_authority_effective_from = cast(
            datetime, normalized["client_authority_effective_from"]
        )
        occurred_at = cast(datetime, normalized["occurred_at"])
        effective_from = cast(datetime, normalized["effective_from"])
        if effective_from < client_authority_effective_from:
            _fail("L9C11_P2_EFFECTIVE_FROM_BEFORE_CLIENT_AUTHORITY")
        if effective_from < occurred_at:
            _fail("L9C11_P2_EFFECTIVE_FROM_BEFORE_OCCURRED")
        if self.schema != SCHEMA or self.decision_version != VERSION:
            _fail("L9C11_P2_IDENTITY_INVALID")
        for name, value in normalized.items():
            object.__setattr__(self, name, value)
        intent = {field: _json_value(getattr(self, field)) for field in _FIELDS if field not in {"decision_id", "fingerprint"}}
        derived_id = _decision_id(intent)
        if self.decision_id and self.decision_id != derived_id:
            _fail("L9C11_P2_DECISION_ID_MISMATCH")
        object.__setattr__(self, "decision_id", derived_id)
        digest = _digest(self)
        if self.fingerprint and (
            not isinstance(self.fingerprint, str)
            or not hmac.compare_digest(self.fingerprint, digest)
        ):
            _fail("L9C11_P2_FINGERPRINT_MISMATCH")
        object.__setattr__(self, "fingerprint", digest)

    @property
    def is_representation_forming(self) -> bool:
        """Return whether the historical decision is the positive prerequisite."""
        return (
            self.decision is LegalClientMatterRepresentationFirmDecisionType.ACCEPTED
            and self.client_authority_decision
            is LegalClientMatterRepresentationAuthorityDecision.APPOINTED
        )

    def to_dict(self) -> dict[str, object]:
        """Serialize the exact immutable decision without raw payloads."""
        return {field: _json_value(getattr(self, field)) for field in _FIELDS}

    @classmethod
    def from_dict(
        cls, payload: Mapping[str, object]
    ) -> "LegalClientMatterRepresentationFirmDecision":
        """Hydrate only the exact schema and verify derived identity/integrity."""
        if not isinstance(payload, Mapping) or set(payload) != set(_FIELDS):
            _fail("L9C11_P2_SCHEMA_INVALID")
        values = dict(payload)
        stored = values.pop("fingerprint")
        result = cls(**cast(Any, values))
        if not isinstance(stored, str) or not hmac.compare_digest(stored, result.fingerprint):
            _fail("L9C11_P2_FINGERPRINT_MISMATCH")
        return result

    @classmethod
    def from_client_authority(
        cls,
        *,
        client_authority: LegalClientMatterRepresentationAuthority,
        decision: LegalClientMatterRepresentationFirmDecisionType | str,
        representation_scope_capabilities: tuple[str, ...] | list[str] | None = None,
        decision_actor_principal_id: str,
        authorization_evidence_reference: str,
        authorization_evidence_fingerprint: str,
        source_evidence_reference: str,
        source_evidence_fingerprint: str,
        occurred_at: datetime,
        effective_from: datetime,
        idempotency_key: str,
        decision_version: str = VERSION,
    ) -> "LegalClientMatterRepresentationFirmDecision":
        """Bind one exact published client authority without currentness/IAM.

        The firm decision preserves the authority's principal, role and
        lineage. A caller may narrow, but never widen, the authority's scope.
        """
        if type(client_authority) is not LegalClientMatterRepresentationAuthority:
            _fail("L9C11_P2_CLIENT_AUTHORITY_REQUIRED")
        return cls(
            tenant_id=client_authority.tenant_id,
            case_matter_id=client_authority.case_matter_id,
            matter_fingerprint=client_authority.matter_fingerprint,
            client_party_id=client_authority.client_party_id,
            subject_reference=client_authority.subject_reference,
            subject_identity_fingerprint=client_authority.subject_identity_fingerprint,
            engagement_id=client_authority.engagement_id,
            engagement_fingerprint=client_authority.engagement_fingerprint,
            mandate_id=client_authority.mandate_id,
            mandate_fingerprint=client_authority.mandate_fingerprint,
            acting_capacity_id=client_authority.acting_capacity_id,
            acting_capacity_fingerprint=client_authority.acting_capacity_fingerprint,
            representation_authority_id=client_authority.authority_id,
            representation_authority_fingerprint=client_authority.fingerprint,
            client_authority_decision=client_authority.decision,
            client_authority_effective_from=client_authority.effective_from,
            client_authority_scope_capabilities=client_authority.representation_scope_capabilities,
            representative_principal_id=client_authority.representative_principal_id,
            representative_role=client_authority.representative_role,
            mandate_capabilities=client_authority.mandate_capabilities,
            representation_scope_capabilities=(
                client_authority.representation_scope_capabilities
                if representation_scope_capabilities is None
                else representation_scope_capabilities
            ),
            decision=decision,
            decision_actor_principal_id=decision_actor_principal_id,
            authorization_evidence_reference=authorization_evidence_reference,
            authorization_evidence_fingerprint=authorization_evidence_fingerprint,
            source_evidence_reference=source_evidence_reference,
            source_evidence_fingerprint=source_evidence_fingerprint,
            occurred_at=occurred_at,
            effective_from=effective_from,
            idempotency_key=idempotency_key,
            schema=SCHEMA,
            decision_version=decision_version,
        )


__all__ = [
    "REPRESENTATION_FIRM_DECISION_FIELDS",
    "SCHEMA",
    "VERSION",
    "LegalClientMatterRepresentationFirmDecision",
    "LegalClientMatterRepresentationFirmDecisionError",
    "LegalClientMatterRepresentationFirmDecisionType",
]


# ARTIFACT: legal_client_matter_representation_firm_decision.py
# VERSION: v1.0.0-L9C11-P2-FIRM-REPRESENTATION-DECISION
# AUTHORITY BOUNDARY: immutable firm Representation decision evidence only
# TENANT POSTURE: exact client-authority lineage; no fallback
# FAIL-CLOSED POSTURE: strict client-state, scope, chronology and fingerprint validation
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively
# END OF WILSY OS SOVEREIGN ARTIFACT
