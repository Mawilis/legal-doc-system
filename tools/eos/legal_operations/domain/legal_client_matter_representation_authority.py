"""WILSY OS immutable client-side Representation authority decision.

TITLE: WILSY OS Legal Client Matter Representation Authority
VERSION: v1.0.0-L9C11-P1-CLIENT-REPRESENTATION-AUTHORITY
AUTHORITY: Wilsy OS Core Governance / Python EOS Legal Operations
EPITOME: Preserve one immutable client-side appointment/authority decision
         that may later be considered when forming Representation for one exact
         tenant-scoped matter party. This artifact is prerequisite evidence
         only; it is not a formed Representation, currentness state, IAM grant,
         Court authority, or financial authority.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tools/eos/legal_operations/domain/legal_client_matter_representation_authority.py
COLLABORATION / OWNERSHIP: CaseMatter and LegalMatterParty own identity;
                            Engagement, Mandate and ActingCapacity own their
                            immutable upstream evidence; this artifact owns
                            only the client-side Representation appointment
                            decision. A later firm decision, IAM, registry,
                            currentness and formation authority remain separate.
CERTIFICATION / UPDATE DATE: 2026-09-28
CHANGELOG: v1.0.0-L9C11-P1 establishes exact tenant/matter/client-party,
           Engagement/Mandate/ActingCapacity lineage, designated principal and
           bounded non-Court scope, APPOINTED/DECLINED/REQUIRES_REVIEW client
           authority vocabulary, explicit UTC chronology, strict hydration and
           deterministic SHA3-512 integrity. It creates no Representation,
           lifecycle, currentness, IAM, persistence, HTTP, Court or finance.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2; ISO 27001.
SECURITY / PRIVACY POSTURE: Opaque identifiers, bounded references and
                             lowercase SHA3-512 fingerprints only; no names,
                             contact data, credentials, tokens or raw mandate.
TENANT BOUNDARY: Every lineage value must describe the same explicit tenant,
                 CaseMatter and client-side party. No fallback or cross-tenant
                 inference is permitted.
AUTHORITY BOUNDARY: Historical client appointment/authority evidence only.
                    The appointing actor is provenance, not IAM permission;
                    the representative principal is a designated subject, not
                    an authenticated or authorized actor. Engagement currentness,
                    firm acceptance and legal sufficiency remain unproved.
FINANCIAL AUTHORITY BOUNDARY: No billing, invoice, payment, settlement,
                              trust, release or execution truth; Kennel EOS
                              remains exclusive for financial execution.
TRANSACTION BOUNDARY: Pure immutable construction, deterministic serialization
                      and strict hydration only; no database, HTTP, IAM,
                      transaction, retry, clock, notification or network work.
FAIL-CLOSED DECLARATION: Malformed lineage, vocabulary, scope, chronology,
                         schema or fingerprint divergence rejects without
                         coercion, currentness inference or authority expansion.
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

from tools.eos.legal_operations.domain.legal_client_acting_capacity import (
    LegalClientActingCapacity,
)
from tools.eos.legal_operations.domain.legal_client_matter_engagement import (
    LegalClientMatterEngagement,
)
from tools.eos.legal_operations.domain.legal_client_matter_mandate import (
    LegalClientMatterMandate,
)


VERSION: Final[str] = "v1.0.0-L9C11-P1-CLIENT-REPRESENTATION-AUTHORITY"
SCHEMA: Final[str] = "WILSY-LEGAL-CLIENT-MATTER-REPRESENTATION-AUTHORITY/V1"
_IDENTITY: Final[re.Pattern[str]] = re.compile(
    r"^[A-Za-z0-9][A-Za-z0-9._:-]{0,159}$"
)
_HEX: Final[re.Pattern[str]] = re.compile(r"^[0-9a-f]{128}$")
_FORBIDDEN_TENANTS: Final[frozenset[str]] = frozenset(
    {"default", "global", "global_root", "root", "master", "*"}
)
_ALLOWED_SCOPE_CAPABILITIES: Final[frozenset[str]] = frozenset(
    {
        "ADVISORY",
        "NEGOTIATION",
        "TRANSACTIONAL",
        "DISPUTE_PREPARATION",
        "LITIGATION_PREPARATION",
        "SETTLEMENT_NEGOTIATION",
    }
)
_KNOWN_MANDATE_CAPABILITIES: Final[frozenset[str]] = _ALLOWED_SCOPE_CAPABILITIES | frozenset(
    {"COURT_FILING_PREPARATION", "COURT_APPEARANCE_PREPARATION"}
)
_FIELDS: Final[tuple[str, ...]] = (
    "schema",
    "authority_version",
    "authority_id",
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
    "mandate_scope_reference",
    "mandate_scope_fingerprint",
    "mandate_capabilities",
    "acting_capacity_id",
    "acting_capacity_fingerprint",
    "representative_principal_id",
    "representative_role",
    "representation_scope_capabilities",
    "decision",
    "appointing_principal_id",
    "source_evidence_reference",
    "source_evidence_fingerprint",
    "authorization_evidence_reference",
    "authorization_evidence_fingerprint",
    "occurred_at",
    "effective_from",
    "effective_until",
    "idempotency_key",
    "fingerprint",
)
REPRESENTATION_AUTHORITY_FIELDS: Final[frozenset[str]] = frozenset(_FIELDS)


class LegalClientMatterRepresentationAuthorityDecision(StrEnum):
    """Immutable client-side appointment decisions; no lifecycle states."""

    APPOINTED = "APPOINTED"
    DECLINED = "DECLINED"
    REQUIRES_REVIEW = "REQUIRES_REVIEW"


class LegalClientMatterRepresentationAuthorityError(ValueError):
    """Stable, non-sensitive failure from authority validation."""

    def __init__(self, code: str) -> None:
        """Expose only a bounded code and never supplied authority data."""
        self.code = code
        super().__init__(code)


def _fail(code: str, cause: BaseException | None = None) -> NoReturn:
    """Raise one stable failure while retaining technical cause internally."""
    error = LegalClientMatterRepresentationAuthorityError(code)
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
        _fail(f"L9C11_P1_{name.upper()}_INVALID")
    return cast(str, value)


def _tenant(value: object) -> str:
    """Require one explicit non-global tenant identity."""
    tenant = _identity("tenant_id", value)
    if tenant.casefold() in _FORBIDDEN_TENANTS:
        _fail("L9C11_P1_TENANT_REQUIRED")
    return tenant


def _fingerprint(name: str, value: object) -> str:
    """Require one lowercase SHA3-512 hexadecimal evidence fingerprint."""
    if not isinstance(value, str) or _HEX.fullmatch(value) is None:
        _fail(f"L9C11_P1_{name.upper()}_INVALID")
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
        _fail(f"L9C11_P1_{name.upper()}_INVALID")
    normalized = unicodedata.normalize("NFC", value)
    if not normalized or len(normalized) > limit:
        _fail(f"L9C11_P1_{name.upper()}_INVALID")
    return normalized


def _capabilities(name: str, value: object, *, allow_court: bool) -> tuple[str, ...]:
    """Normalize mandate capabilities and forbid Court scope in this contract."""
    if not isinstance(value, (tuple, list, set, frozenset)) or not value:
        _fail(f"L9C11_P1_{name.upper()}_INVALID")
    normalized: set[str] = set()
    for item in value:
        label = getattr(item, "value", item)
        if not isinstance(label, str) or label != label.strip() or not label:
            _fail(f"L9C11_P1_{name.upper()}_INVALID")
        label = label.upper()
        if not allow_court and label.startswith("COURT_"):
            _fail("L9C11_P1_COURT_SCOPE_FORBIDDEN")
        if label not in (_KNOWN_MANDATE_CAPABILITIES if allow_court else _ALLOWED_SCOPE_CAPABILITIES):
            _fail(f"L9C11_P1_{name.upper()}_INVALID")
        normalized.add(label)
    return tuple(sorted(normalized))


def _timestamp(name: str, value: object) -> datetime:
    """Require an aware timestamp and normalize it to UTC microseconds."""
    parsed = value
    if isinstance(parsed, str):
        try:
            parsed = datetime.fromisoformat(parsed.replace("Z", "+00:00"))
        except ValueError as error:
            _fail(f"L9C11_P1_{name.upper()}_INVALID", error)
    if (
        not isinstance(parsed, datetime)
        or parsed.tzinfo is None
        or parsed.utcoffset() is None
    ):
        _fail(f"L9C11_P1_{name.upper()}_INVALID")
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


def _digest(instance: "LegalClientMatterRepresentationAuthority") -> str:
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
class LegalClientMatterRepresentationAuthority:
    """Immutable client appointment evidence, not a formed Representation.

    The value binds exact upstream identities and a designated principal. It
    records client intent only; it does not authenticate either principal,
    evaluate Engagement currentness, grant IAM, create Representation, or
    authorize Court or financial activity.
    """

    authority_id: str
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
    mandate_scope_reference: str
    mandate_scope_fingerprint: str
    mandate_capabilities: tuple[str, ...] | list[str]
    acting_capacity_id: str
    acting_capacity_fingerprint: str
    representative_principal_id: str
    representative_role: str
    representation_scope_capabilities: tuple[str, ...] | list[str]
    decision: LegalClientMatterRepresentationAuthorityDecision | str
    appointing_principal_id: str
    source_evidence_reference: str
    source_evidence_fingerprint: str
    authorization_evidence_reference: str
    authorization_evidence_fingerprint: str
    occurred_at: datetime
    effective_from: datetime
    effective_until: datetime | None
    idempotency_key: str
    schema: str = SCHEMA
    authority_version: str = VERSION
    fingerprint: str = ""

    def __post_init__(self) -> None:
        """Validate the immutable snapshot and compute or verify integrity."""
        tenant = _tenant(self.tenant_id)
        authority_id = _identity("authority_id", self.authority_id)
        authority_version = _identity("authority_version", self.authority_version)
        matter_id = _identity("case_matter_id", self.case_matter_id)
        matter_fingerprint = _fingerprint("matter_fingerprint", self.matter_fingerprint)
        party_id = _identity("client_party_id", self.client_party_id)
        subject = _reference("subject_reference", self.subject_reference, limit=224)
        subject_fingerprint = _fingerprint(
            "subject_identity_fingerprint", self.subject_identity_fingerprint
        )
        engagement_id = _identity("engagement_id", self.engagement_id)
        engagement_fingerprint = _fingerprint(
            "engagement_fingerprint", self.engagement_fingerprint
        )
        mandate_id = _identity("mandate_id", self.mandate_id)
        mandate_fingerprint = _fingerprint("mandate_fingerprint", self.mandate_fingerprint)
        mandate_scope = _reference(
            "mandate_scope_reference", self.mandate_scope_reference
        )
        mandate_scope_fingerprint = _fingerprint(
            "mandate_scope_fingerprint", self.mandate_scope_fingerprint
        )
        mandate_capabilities = _capabilities(
            "mandate_capabilities", self.mandate_capabilities, allow_court=True
        )
        capacity_id = _identity("acting_capacity_id", self.acting_capacity_id)
        capacity_fingerprint = _fingerprint(
            "acting_capacity_fingerprint", self.acting_capacity_fingerprint
        )
        representative_principal = _identity(
            "representative_principal_id", self.representative_principal_id
        )
        representative_role = _identity("representative_role", self.representative_role)
        representation_capabilities = _capabilities(
            "representation_scope_capabilities",
            self.representation_scope_capabilities,
            allow_court=False,
        )
        if not set(representation_capabilities).issubset(mandate_capabilities):
            _fail("L9C11_P1_SCOPE_EXCEEDS_MANDATE")
        try:
            decision = LegalClientMatterRepresentationAuthorityDecision(self.decision)
        except (TypeError, ValueError) as error:
            _fail("L9C11_P1_DECISION_INVALID", error)
        appointing_principal = _identity(
            "appointing_principal_id", self.appointing_principal_id
        )
        source_reference = _reference("source_evidence_reference", self.source_evidence_reference)
        source_fingerprint = _fingerprint(
            "source_evidence_fingerprint", self.source_evidence_fingerprint
        )
        authorization_reference = _reference(
            "authorization_evidence_reference", self.authorization_evidence_reference
        )
        authorization_fingerprint = _fingerprint(
            "authorization_evidence_fingerprint",
            self.authorization_evidence_fingerprint,
        )
        occurred = _timestamp("occurred_at", self.occurred_at)
        effective = _timestamp("effective_from", self.effective_from)
        until = None if self.effective_until is None else _timestamp(
            "effective_until", self.effective_until
        )
        idempotency_key = _reference("idempotency_key", self.idempotency_key, limit=240)
        if self.schema != SCHEMA or authority_version != VERSION:
            _fail("L9C11_P1_IDENTITY_INVALID")
        if effective < occurred:
            _fail("L9C11_P1_EFFECTIVE_FROM_BEFORE_OCCURRED")
        if until is not None and until <= effective:
            _fail("L9C11_P1_EFFECTIVE_UNTIL_INVALID")

        for name, value in (
            ("tenant_id", tenant),
            ("authority_id", authority_id),
            ("authority_version", authority_version),
            ("case_matter_id", matter_id),
            ("matter_fingerprint", matter_fingerprint),
            ("client_party_id", party_id),
            ("subject_reference", subject),
            ("subject_identity_fingerprint", subject_fingerprint),
            ("engagement_id", engagement_id),
            ("engagement_fingerprint", engagement_fingerprint),
            ("mandate_id", mandate_id),
            ("mandate_fingerprint", mandate_fingerprint),
            ("mandate_scope_reference", mandate_scope),
            ("mandate_scope_fingerprint", mandate_scope_fingerprint),
            ("mandate_capabilities", mandate_capabilities),
            ("acting_capacity_id", capacity_id),
            ("acting_capacity_fingerprint", capacity_fingerprint),
            ("representative_principal_id", representative_principal),
            ("representative_role", representative_role),
            ("representation_scope_capabilities", representation_capabilities),
            ("decision", decision),
            ("appointing_principal_id", appointing_principal),
            ("source_evidence_reference", source_reference),
            ("source_evidence_fingerprint", source_fingerprint),
            ("authorization_evidence_reference", authorization_reference),
            ("authorization_evidence_fingerprint", authorization_fingerprint),
            ("occurred_at", occurred),
            ("effective_from", effective),
            ("effective_until", until),
            ("idempotency_key", idempotency_key),
        ):
            object.__setattr__(self, name, value)

        digest = _digest(self)
        if self.fingerprint and (
            not isinstance(self.fingerprint, str)
            or not hmac.compare_digest(self.fingerprint, digest)
        ):
            _fail("L9C11_P1_FINGERPRINT_MISMATCH")
        object.__setattr__(self, "fingerprint", digest)

    @property
    def is_appointing(self) -> bool:
        """Return whether this immutable decision is the positive appointment.

        This is historical evidence only. It does not establish currentness,
        firm acceptance, IAM authorization, or a formed Representation.
        """
        return self.decision is LegalClientMatterRepresentationAuthorityDecision.APPOINTED

    def to_dict(self) -> dict[str, object]:
        """Serialize the exact immutable snapshot without raw payloads."""
        return {field: _json_value(getattr(self, field)) for field in _FIELDS}

    @classmethod
    def from_dict(
        cls, payload: Mapping[str, object]
    ) -> "LegalClientMatterRepresentationAuthority":
        """Hydrate only the exact schema and verify deterministic integrity."""
        if not isinstance(payload, Mapping) or set(payload) != set(_FIELDS):
            _fail("L9C11_P1_SCHEMA_INVALID")
        values = dict(payload)
        stored = values.pop("fingerprint")
        result = cls(**cast(Any, values))
        if not isinstance(stored, str) or not hmac.compare_digest(stored, result.fingerprint):
            _fail("L9C11_P1_FINGERPRINT_MISMATCH")
        return result

    @classmethod
    def from_canonical(
        cls,
        *,
        authority_id: str,
        engagement: LegalClientMatterEngagement,
        mandate: LegalClientMatterMandate,
        acting_capacity: LegalClientActingCapacity,
        representative_principal_id: str,
        representative_role: str,
        representation_scope_capabilities: tuple[str, ...] | list[str],
        decision: LegalClientMatterRepresentationAuthorityDecision | str,
        appointing_principal_id: str,
        source_evidence_reference: str,
        source_evidence_fingerprint: str,
        authorization_evidence_reference: str,
        authorization_evidence_fingerprint: str,
        occurred_at: datetime,
        effective_from: datetime,
        effective_until: datetime | None,
        idempotency_key: str,
        authority_version: str = VERSION,
    ) -> "LegalClientMatterRepresentationAuthority":
        """Bind one exact Engagement, Mandate and ActingCapacity lineage.

        This constructor validates correlation and scope only. It deliberately
        does not evaluate Engagement currentness, inspect IAM, or form
        Representation. Upstream values are treated as immutable evidence.
        """
        if type(engagement) is not LegalClientMatterEngagement:
            _fail("L9C11_P1_ENGAGEMENT_REQUIRED")
        if type(mandate) is not LegalClientMatterMandate:
            _fail("L9C11_P1_MANDATE_REQUIRED")
        if type(acting_capacity) is not LegalClientActingCapacity:
            _fail("L9C11_P1_ACTING_CAPACITY_REQUIRED")
        correlated = (
            engagement.tenant_id == mandate.tenant_id == acting_capacity.tenant_id,
            engagement.case_matter_id == mandate.case_matter_id == acting_capacity.case_matter_id,
            engagement.matter_fingerprint == mandate.matter_fingerprint == acting_capacity.matter_fingerprint,
            engagement.client_party_id == mandate.client_party_id == acting_capacity.party_id,
            engagement.subject_identity_fingerprint
            == mandate.subject_identity_fingerprint
            == acting_capacity.subject_identity_fingerprint,
            engagement.acting_capacity_id == mandate.acting_capacity_id == acting_capacity.capacity_id,
            engagement.acting_capacity_fingerprint
            == mandate.acting_capacity_fingerprint
            == acting_capacity.fingerprint,
            engagement.mandate_id == mandate.mandate_id,
            engagement.mandate_fingerprint == mandate.fingerprint,
        )
        if not all(correlated):
            _fail("L9C11_P1_UPSTREAM_LINEAGE_MISMATCH")
        return cls(
            authority_id=authority_id,
            tenant_id=engagement.tenant_id,
            case_matter_id=engagement.case_matter_id,
            matter_fingerprint=engagement.matter_fingerprint,
            client_party_id=engagement.client_party_id,
            subject_reference=engagement.subject_reference,
            subject_identity_fingerprint=engagement.subject_identity_fingerprint,
            engagement_id=engagement.engagement_id,
            engagement_fingerprint=engagement.fingerprint,
            mandate_id=mandate.mandate_id,
            mandate_fingerprint=mandate.fingerprint,
            mandate_scope_reference=mandate.scope_reference,
            mandate_scope_fingerprint=mandate.scope_fingerprint,
            mandate_capabilities=mandate.capabilities,
            acting_capacity_id=acting_capacity.capacity_id,
            acting_capacity_fingerprint=acting_capacity.fingerprint,
            representative_principal_id=representative_principal_id,
            representative_role=representative_role,
            representation_scope_capabilities=representation_scope_capabilities,
            decision=decision,
            appointing_principal_id=appointing_principal_id,
            source_evidence_reference=source_evidence_reference,
            source_evidence_fingerprint=source_evidence_fingerprint,
            authorization_evidence_reference=authorization_evidence_reference,
            authorization_evidence_fingerprint=authorization_evidence_fingerprint,
            occurred_at=occurred_at,
            effective_from=effective_from,
            effective_until=effective_until,
            idempotency_key=idempotency_key,
            schema=SCHEMA,
            authority_version=authority_version,
        )


__all__ = [
    "REPRESENTATION_AUTHORITY_FIELDS",
    "SCHEMA",
    "VERSION",
    "LegalClientMatterRepresentationAuthority",
    "LegalClientMatterRepresentationAuthorityDecision",
    "LegalClientMatterRepresentationAuthorityError",
]


# ARTIFACT: legal_client_matter_representation_authority.py
# VERSION: v1.0.0-L9C11-P1-CLIENT-REPRESENTATION-AUTHORITY
# AUTHORITY BOUNDARY: immutable client appointment evidence only
# TENANT POSTURE: exact tenant/matter/client-party/upstream lineage; no fallback
# FAIL-CLOSED POSTURE: strict schema, scope, chronology and fingerprint validation
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively
# END OF WILSY OS SOVEREIGN ARTIFACT
