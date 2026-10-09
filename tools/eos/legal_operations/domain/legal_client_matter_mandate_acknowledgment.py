"""WILSY OS immutable firm-side mandate acknowledgment evidence domain.

TITLE: WILSY OS Legal Client Matter Mandate Acknowledgment
VERSION: v1.0.0-L9B5-FIRM-MANDATE-ACKNOWLEDGMENT
AUTHORITY: Wilsy OS Core Governance / Python EOS Legal Operations
EPITOME: Record one immutable, exact-grant-bound decision by an authorized
         firm-side actor concerning one published client mandate grant. This
         artifact is historical acknowledgment evidence only; it does not
         establish mandate currentness, Engagement, Representation, Court
         authority, or financial authority.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tools/eos/legal_operations/domain/legal_client_matter_mandate_acknowledgment.py
COLLABORATION / OWNERSHIP: LegalClientMatterMandateGrant owns the canonical
                            client-grant identity, tenant, matter, client
                            party, subject, breadth, scope and capabilities;
                            this artifact owns only the firm's immutable
                            acknowledgment decision and its provenance.
                            Future IAM, registry/currentness, mandate,
                            Engagement, Representation and Court authorities
                            remain separate.
CERTIFICATION / UPDATE DATE: 2026-09-27
CHANGELOG: v1.0.0-L9B5-FIRM-MANDATE-ACKNOWLEDGMENT establishes the closed
           ACKNOWLEDGED/DECLINED/REQUIRES_REVIEW decision vocabulary, exact
           published client-grant lineage, actor and authorization evidence,
           source evidence, UTC chronology, idempotency identity, deterministic
           SHA3-512 integrity and strict hydration. It creates no currentness,
           revocation, IAM, Engagement, Representation, Court or finance.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2; ISO 27001.
SECURITY / PRIVACY POSTURE: Opaque identifiers, bounded references and
                             lowercase SHA3-512 fingerprints only; no raw PII,
                             credentials, tokens, JWT/session material or
                             unrestricted evidence bodies are retained.
TENANT BOUNDARY: Tenant, matter, client party and subject identity are
                 derived from the exact published grant; no fallback,
                 cross-tenant substitution or caller reassertion is allowed.
AUTHORITY BOUNDARY: Immutable historical firm-side acknowledgment evidence
                    only. The actor identity is provenance, not authorization;
                    a future IAM-aware orchestrator must prove permission and
                    a future registry must determine currentness.
FINANCIAL AUTHORITY BOUNDARY: No fees, billing, payment, trust, settlement or
                              execution authority; Kennel EOS remains exclusive
                              financial execution authority.
TRANSACTION BOUNDARY: Pure immutable in-memory construction, deterministic
                      serialization and strict hydration only; no database,
                      HTTP, IAM, registry, transaction, retry, notification or
                      network behavior.
FAIL-CLOSED DECLARATION: Malformed grant lineage, identities, decision,
                         evidence, chronology, schema or fingerprint drift
                         rejects without coercion, fallback or authority
                         expansion.
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

from tools.eos.legal_operations.domain.legal_client_matter_mandate_grant import (
    LegalClientMatterMandateGrant,
)


VERSION: Final[str] = "v1.0.0-L9B5-FIRM-MANDATE-ACKNOWLEDGMENT"
SCHEMA: Final[str] = "WILSY-LEGAL-CLIENT-MATTER-MANDATE-ACKNOWLEDGMENT/V1"
_IDENTITY: Final[re.Pattern[str]] = re.compile(
    r"^[A-Za-z0-9][A-Za-z0-9._:-]{0,159}$"
)
_HEX: Final[re.Pattern[str]] = re.compile(r"^[0-9a-f]{128}$")
_FORBIDDEN_TENANTS: Final[frozenset[str]] = frozenset(
    {"default", "global", "global_root", "root", "master", "*"}
)
_FIELDS: Final[tuple[str, ...]] = (
    "schema",
    "acknowledgment_version",
    "acknowledgment_id",
    "tenant_id",
    "case_matter_id",
    "matter_fingerprint",
    "client_party_id",
    "subject_identity_fingerprint",
    "client_grant_id",
    "client_grant_fingerprint",
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
ACKNOWLEDGMENT_FIELDS: Final[frozenset[str]] = frozenset(_FIELDS)


class LegalClientMatterMandateAcknowledgmentDecision(StrEnum):
    """Closed firm-side acknowledgment decisions for one exact client grant.

    ``ACKNOWLEDGED`` is the sole positive prerequisite value for a future
    mandate-forming orchestrator. These values are historical decisions, not
    currentness, revocation, Engagement, Representation, Court or finance.
    """

    ACKNOWLEDGED = "ACKNOWLEDGED"
    DECLINED = "DECLINED"
    REQUIRES_REVIEW = "REQUIRES_REVIEW"


class LegalClientMatterMandateAcknowledgmentError(ValueError):
    """Stable, non-sensitive failure from acknowledgment validation."""

    def __init__(self, code: str) -> None:
        """Expose only a bounded code and never echo supplied authority data."""
        self.code = code
        super().__init__(code)


def _fail(code: str, cause: BaseException | None = None) -> NoReturn:
    """Raise one stable failure while retaining technical cause internally."""
    error = LegalClientMatterMandateAcknowledgmentError(code)
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
        _fail(f"L9B5_{name.upper()}_INVALID")
    return cast(str, value)


def _tenant(value: object) -> str:
    """Require one explicit non-global tenant identity."""
    tenant = _identity("tenant_id", value)
    if tenant.casefold() in _FORBIDDEN_TENANTS:
        _fail("L9B5_TENANT_REQUIRED")
    return tenant


def _fingerprint(name: str, value: object) -> str:
    """Require one lowercase SHA3-512 hexadecimal fingerprint."""
    if not isinstance(value, str) or _HEX.fullmatch(value) is None:
        _fail(f"L9B5_{name.upper()}_INVALID")
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
        _fail(f"L9B5_{name.upper()}_INVALID")
    normalized = unicodedata.normalize("NFC", value)
    if not normalized or len(normalized) > limit:
        _fail(f"L9B5_{name.upper()}_INVALID")
    return normalized


def _timestamp(name: str, value: object) -> datetime:
    """Require an aware timestamp and normalize it to UTC microseconds."""
    parsed = value
    if isinstance(parsed, str):
        try:
            parsed = datetime.fromisoformat(parsed.replace("Z", "+00:00"))
        except ValueError as error:
            _fail(f"L9B5_{name.upper()}_INVALID", error)
    if (
        not isinstance(parsed, datetime)
        or parsed.tzinfo is None
        or parsed.utcoffset() is None
    ):
        _fail(f"L9B5_{name.upper()}_INVALID")
    return parsed.astimezone(timezone.utc)


def _json_value(value: object) -> object:
    """Convert immutable values into deterministic JSON-safe values."""
    if isinstance(value, datetime):
        return value.astimezone(timezone.utc).isoformat(timespec="microseconds").replace(
            "+00:00", "Z"
        )
    if isinstance(value, StrEnum):
        return value.value
    return value


def _digest(instance: "LegalClientMatterMandateAcknowledgment") -> str:
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
class LegalClientMatterMandateAcknowledgment:
    """Immutable acknowledgment evidence for one exact client mandate grant.

    The canonical grant is the sole source of tenant, matter, client-party,
    subject and grant-lineage authority. This value records only the firm's
    decision and provenance; it performs no authentication, authorization,
    persistence, currentness, revocation, Engagement, Representation, Court
    or financial action.
    """

    acknowledgment_id: str
    tenant_id: str
    case_matter_id: str
    matter_fingerprint: str
    client_party_id: str
    subject_identity_fingerprint: str
    client_grant_id: str
    client_grant_fingerprint: str
    decision: LegalClientMatterMandateAcknowledgmentDecision | str
    decision_actor_principal_id: str
    authorization_evidence_reference: str
    authorization_evidence_fingerprint: str
    source_evidence_reference: str
    source_evidence_fingerprint: str
    occurred_at: datetime
    effective_from: datetime
    idempotency_key: str
    schema: str = SCHEMA
    acknowledgment_version: str = VERSION
    fingerprint: str = ""

    def __post_init__(self) -> None:
        """Validate the immutable snapshot and compute or verify integrity."""
        tenant = _tenant(self.tenant_id)
        acknowledgment_id = _identity("acknowledgment_id", self.acknowledgment_id)
        acknowledgment_version = _identity(
            "acknowledgment_version", self.acknowledgment_version
        )
        matter_id = _identity("case_matter_id", self.case_matter_id)
        matter_fingerprint = _fingerprint("matter_fingerprint", self.matter_fingerprint)
        party_id = _identity("client_party_id", self.client_party_id)
        subject_fingerprint = _fingerprint(
            "subject_identity_fingerprint", self.subject_identity_fingerprint
        )
        grant_id = _identity("client_grant_id", self.client_grant_id)
        grant_fingerprint = _fingerprint(
            "client_grant_fingerprint", self.client_grant_fingerprint
        )
        try:
            decision = LegalClientMatterMandateAcknowledgmentDecision(self.decision)
        except (TypeError, ValueError) as error:
            _fail("L9B5_DECISION_INVALID", error)
        actor = _identity("decision_actor_principal_id", self.decision_actor_principal_id)
        authorization_reference = _reference(
            "authorization_evidence_reference", self.authorization_evidence_reference
        )
        authorization_fingerprint = _fingerprint(
            "authorization_evidence_fingerprint",
            self.authorization_evidence_fingerprint,
        )
        source_reference = _reference(
            "source_evidence_reference", self.source_evidence_reference
        )
        source_fingerprint = _fingerprint(
            "source_evidence_fingerprint", self.source_evidence_fingerprint
        )
        occurred = _timestamp("occurred_at", self.occurred_at)
        effective = _timestamp("effective_from", self.effective_from)
        idempotency_key = _reference("idempotency_key", self.idempotency_key, limit=240)
        if self.schema != SCHEMA or acknowledgment_version != VERSION:
            _fail("L9B5_IDENTITY_INVALID")
        if effective < occurred:
            _fail("L9B5_EFFECTIVE_FROM_BEFORE_OCCURRED")

        object.__setattr__(self, "tenant_id", tenant)
        object.__setattr__(self, "acknowledgment_id", acknowledgment_id)
        object.__setattr__(self, "acknowledgment_version", acknowledgment_version)
        object.__setattr__(self, "case_matter_id", matter_id)
        object.__setattr__(self, "matter_fingerprint", matter_fingerprint)
        object.__setattr__(self, "client_party_id", party_id)
        object.__setattr__(self, "subject_identity_fingerprint", subject_fingerprint)
        object.__setattr__(self, "client_grant_id", grant_id)
        object.__setattr__(self, "client_grant_fingerprint", grant_fingerprint)
        object.__setattr__(self, "decision", decision)
        object.__setattr__(self, "decision_actor_principal_id", actor)
        object.__setattr__(self, "authorization_evidence_reference", authorization_reference)
        object.__setattr__(self, "authorization_evidence_fingerprint", authorization_fingerprint)
        object.__setattr__(self, "source_evidence_reference", source_reference)
        object.__setattr__(self, "source_evidence_fingerprint", source_fingerprint)
        object.__setattr__(self, "occurred_at", occurred)
        object.__setattr__(self, "effective_from", effective)
        object.__setattr__(self, "idempotency_key", idempotency_key)

        digest = _digest(self)
        if self.fingerprint and (
            not isinstance(self.fingerprint, str)
            or not hmac.compare_digest(self.fingerprint, digest)
        ):
            _fail("L9B5_FINGERPRINT_MISMATCH")
        object.__setattr__(self, "fingerprint", digest)

    @property
    def is_mandate_forming(self) -> bool:
        """Return whether this historical decision is the positive prerequisite.

        This property does not establish currentness or form a mandate; a
        future IAM-aware, registry-backed orchestrator must do that separately.
        """
        return self.decision is LegalClientMatterMandateAcknowledgmentDecision.ACKNOWLEDGED

    def to_dict(self) -> dict[str, object]:
        """Serialize the exact immutable snapshot without raw evidence bodies."""
        return {field: _json_value(getattr(self, field)) for field in _FIELDS}

    @classmethod
    def from_dict(cls, payload: Mapping[str, object]) -> "LegalClientMatterMandateAcknowledgment":
        """Hydrate only the exact schema and verify deterministic integrity."""
        if not isinstance(payload, Mapping) or set(payload) != set(_FIELDS):
            _fail("L9B5_SCHEMA_INVALID")
        values = dict(payload)
        stored = values.pop("fingerprint")
        result = cls(**cast(Any, values))
        if not isinstance(stored, str) or not hmac.compare_digest(stored, result.fingerprint):
            _fail("L9B5_FINGERPRINT_MISMATCH")
        return result

    @classmethod
    def from_client_grant(
        cls,
        *,
        client_grant: LegalClientMatterMandateGrant,
        acknowledgment_id: str,
        acknowledgment_version: str = VERSION,
        decision: LegalClientMatterMandateAcknowledgmentDecision | str,
        decision_actor_principal_id: str,
        authorization_evidence_reference: str,
        authorization_evidence_fingerprint: str,
        source_evidence_reference: str,
        source_evidence_fingerprint: str,
        occurred_at: datetime,
        effective_from: datetime,
        idempotency_key: str,
    ) -> "LegalClientMatterMandateAcknowledgment":
        """Construct acknowledgment from one exact published client grant.

        Tenant, matter, matter fingerprint, client party, subject identity and
        grant lineage are derived from ``client_grant``. Callers cannot supply
        duplicated scope, capability or identity authority. The actor and
        evidence values are recorded as provenance only; authentication and
        permission remain future orchestrator responsibilities.
        """
        if type(client_grant) is not LegalClientMatterMandateGrant:
            _fail("L9B5_CLIENT_GRANT_REQUIRED")
        try:
            client_grant.__post_init__()
        except Exception as error:
            _fail("L9B5_CLIENT_GRANT_INVALID", error)
        return cls(
            acknowledgment_id=acknowledgment_id,
            tenant_id=client_grant.tenant_id,
            case_matter_id=client_grant.case_matter_id,
            matter_fingerprint=client_grant.matter_fingerprint,
            client_party_id=client_grant.client_party_id,
            subject_identity_fingerprint=client_grant.subject_identity_fingerprint,
            client_grant_id=client_grant.client_grant_id,
            client_grant_fingerprint=client_grant.fingerprint,
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
            acknowledgment_version=acknowledgment_version,
        )


__all__ = [
    "ACKNOWLEDGMENT_FIELDS",
    "SCHEMA",
    "VERSION",
    "LegalClientMatterMandateAcknowledgment",
    "LegalClientMatterMandateAcknowledgmentDecision",
    "LegalClientMatterMandateAcknowledgmentError",
]


# ARTIFACT: legal_client_matter_mandate_acknowledgment.py
# VERSION: v1.0.0-L9B5-FIRM-MANDATE-ACKNOWLEDGMENT
# AUTHORITY BOUNDARY: immutable exact-client-grant acknowledgment evidence only
# TENANT POSTURE: exact tenant/matter/client-party/subject/grant binding; no fallback
# FAIL-CLOSED POSTURE: strict schema, decision, chronology and fingerprint validation
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively
# END OF WILSY OS SOVEREIGN ARTIFACT
