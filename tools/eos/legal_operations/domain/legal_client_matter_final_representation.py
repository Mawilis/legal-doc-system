"""WILSY OS immutable final client-matter Representation truth.

TITLE: WILSY OS Legal Client Matter Final Representation
VERSION: v1.0.0-L9C11-P24-FINAL-REPRESENTATION
AUTHORITY: Wilsy OS Core Governance / Python EOS Legal Operations
EPITOME: Form one immutable final Representation snapshot only when the
         certified P21A client-authority projection is APPOINTED, the P22
         firm-decision projection is ACCEPTED, and exact Engagement/Mandate
         lineage plus representative-eligibility evidence agree. This value
         is not attorney-of-record, Court Online, filing, appearance,
         admission, IAM, financial, settlement or execution authority.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tools/eos/legal_operations/domain/legal_client_matter_final_representation.py
COLLABORATION / OWNERSHIP: P1/P2 own immutable prerequisite evidence; P21A/P22
                            own positive currentness projections; Engagement
                            and Mandate own their formation evidence; P24 owns
                            only the final immutable Representation snapshot.
                            Formation/orchestration, IAM, Court and finance
                            remain later authorities.
CERTIFICATION / UPDATE DATE: 2026-09-28
CHANGELOG: v1.0.0-L9C11-P24 establishes exact P1/P2/currentness,
           Engagement/Mandate and representative-eligibility binding,
           deterministic SHA3-512 identity/integrity, non-widening scope,
           explicit UTC chronology and strict hydration. It creates no
           decision enum, lifecycle, currentness, IAM, Court or finance.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2; ISO 27001.
SECURITY / PRIVACY POSTURE: Opaque identifiers and SHA3-512 evidence only;
                             no PII, credentials, tokens or raw source data.
TENANT BOUNDARY: Every prerequisite and persisted field is bound to one exact
                 tenant, matter, client party and subject fingerprint.
AUTHORITY BOUNDARY: Final Representation business truth only. It does not
                    authenticate a principal, grant IAM, establish attorney-
                    of-record/Court authority, or authorize financial action.
FINANCIAL AUTHORITY BOUNDARY: No billing, payment, settlement, trust, release
                              or execution truth; Kennel EOS remains exclusive.
TRANSACTION BOUNDARY: Pure immutable construction, deterministic serialization
                      and strict hydration; no persistence, network, clock or
                      transaction lifecycle behavior.
FAIL-CLOSED DECLARATION: Mismatched lineage, non-positive currentness,
                         widening scope, ineligible role, malformed evidence,
                         invalid chronology or fingerprint drift rejects.
"""
from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from datetime import datetime, timezone
import hashlib
import hmac
import json
import re
from typing import Any, Final, NoReturn, cast
import unicodedata

from tools.eos.legal_operations.domain.legal_client_matter_engagement import (
    LegalClientMatterEngagement,
)
from tools.eos.legal_operations.domain.legal_client_matter_engagement_currentness import (
    LegalClientMatterEngagementCurrentness,
)
from tools.eos.legal_operations.domain.legal_client_matter_mandate import (
    LegalClientMatterMandate,
)
from tools.eos.legal_operations.domain.legal_client_matter_mandate_currentness import (
    LegalClientMatterMandateCurrentness,
)
from tools.eos.legal_operations.domain.legal_client_matter_representation_authority import (
    LegalClientMatterRepresentationAuthority,
)
from tools.eos.legal_operations.domain.legal_client_matter_representation_authority_currentness import (
    LegalClientMatterRepresentationAuthorityCurrentness,
)
from tools.eos.legal_operations.domain.legal_client_matter_representation_firm_decision import (
    LegalClientMatterRepresentationFirmDecision,
)
from tools.eos.legal_operations.domain.legal_client_matter_representation_firm_decision_currentness import (
    LegalClientMatterRepresentationFirmDecisionCurrentness,
)


VERSION: Final[str] = "v1.0.0-L9C11-P24-FINAL-REPRESENTATION"
SCHEMA: Final[str] = "WILSY-LEGAL-CLIENT-MATTER-FINAL-REPRESENTATION/V1"
_IDENTITY: Final[re.Pattern[str]] = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._:-]{0,159}$")
_HEX: Final[re.Pattern[str]] = re.compile(r"^[0-9a-f]{128}$")
_FORBIDDEN_TENANTS: Final[frozenset[str]] = frozenset(
    {"default", "global", "global_root", "root", "master", "*"}
)
_ALLOWED_ROLES: Final[frozenset[str]] = frozenset({"LEGAL_ATTORNEY", "LEGAL_PARTNER"})
_ALLOWED_SCOPE: Final[frozenset[str]] = frozenset(
    {
        "ADVISORY",
        "NEGOTIATION",
        "TRANSACTIONAL",
        "DISPUTE_PREPARATION",
        "LITIGATION_PREPARATION",
        "SETTLEMENT_NEGOTIATION",
    }
)
_FIELDS: Final[tuple[str, ...]] = (
    "schema",
    "representation_version",
    "representation_id",
    "tenant_id",
    "case_matter_id",
    "matter_fingerprint",
    "client_party_id",
    "subject_identity_fingerprint",
    "representation_authority_id",
    "representation_authority_fingerprint",
    "firm_representation_decision_id",
    "firm_representation_decision_fingerprint",
    "representative_principal_id",
    "representative_role",
    "representation_scope_capabilities",
    "engagement_id",
    "engagement_fingerprint",
    "mandate_id",
    "mandate_fingerprint",
    "authority_currentness_id",
    "authority_currentness_fingerprint",
    "firm_decision_currentness_id",
    "firm_decision_currentness_fingerprint",
    "representative_eligibility_reference",
    "representative_eligibility_fingerprint",
    "source_evidence_reference",
    "source_evidence_fingerprint",
    "effective_from",
    "occurred_at",
    "idempotency_key",
    "fingerprint",
)
FINAL_REPRESENTATION_FIELDS: Final[frozenset[str]] = frozenset(_FIELDS)


class LegalClientMatterFinalRepresentationError(ValueError):
    """Stable non-sensitive fail-closed P24 domain error."""

    def __init__(self, code: str) -> None:
        self.code = code
        super().__init__(code)


def _fail(code: str, cause: BaseException | None = None) -> NoReturn:
    error = LegalClientMatterFinalRepresentationError(code)
    if cause is None:
        raise error
    raise error from cause


def _identity(name: str, value: object) -> str:
    if not isinstance(value, str) or value != value.strip() or _IDENTITY.fullmatch(value) is None:
        _fail(f"L9C11_P24_{name.upper()}_INVALID")
    return cast(str, value)


def _tenant(value: object) -> str:
    tenant = _identity("tenant_id", value)
    if tenant.casefold() in _FORBIDDEN_TENANTS:
        _fail("L9C11_P24_TENANT_REQUIRED")
    return tenant


def _fingerprint(name: str, value: object) -> str:
    if not isinstance(value, str) or _HEX.fullmatch(value) is None:
        _fail(f"L9C11_P24_{name.upper()}_INVALID")
    return value


def _reference(name: str, value: object, *, limit: int = 512) -> str:
    if (
        not isinstance(value, str)
        or not value
        or value != value.strip()
        or len(value) > limit
        or any(ord(ch) < 32 or 0x7F <= ord(ch) <= 0x9F or 0xD800 <= ord(ch) <= 0xDFFF for ch in value)
    ):
        _fail(f"L9C11_P24_{name.upper()}_INVALID")
    result = unicodedata.normalize("NFC", value)
    if not result or len(result) > limit:
        _fail(f"L9C11_P24_{name.upper()}_INVALID")
    return result


def _timestamp(name: str, value: object) -> datetime:
    parsed = value
    if isinstance(parsed, str):
        try:
            parsed = datetime.fromisoformat(parsed.replace("Z", "+00:00"))
        except ValueError as error:
            _fail(f"L9C11_P24_{name.upper()}_INVALID", error)
    if not isinstance(parsed, datetime) or parsed.tzinfo is None or parsed.utcoffset() is None:
        _fail(f"L9C11_P24_{name.upper()}_INVALID")
    return parsed.astimezone(timezone.utc)


def _scope(value: object) -> tuple[str, ...]:
    if not isinstance(value, (tuple, list, set, frozenset)) or isinstance(value, str) or not value:
        _fail("L9C11_P24_SCOPE_INVALID")
    labels: set[str] = set()
    for item in value:
        if not isinstance(item, str) or not item or item != item.strip():
            _fail("L9C11_P24_SCOPE_INVALID")
        label = item.upper()
        if label not in _ALLOWED_SCOPE:
            _fail("L9C11_P24_SCOPE_FORBIDDEN")
        labels.add(label)
    if len(labels) != len(value):
        _fail("L9C11_P24_SCOPE_DUPLICATE")
    return tuple(sorted(labels))


def _json_value(value: object) -> object:
    if isinstance(value, datetime):
        return value.astimezone(timezone.utc).isoformat(timespec="microseconds").replace("+00:00", "Z")
    return value


def _representation_id(instance: "LegalClientMatterFinalRepresentation") -> str:
    payload = {field: _json_value(getattr(instance, field)) for field in _FIELDS if field not in {"representation_id", "fingerprint"}}
    digest = hashlib.sha3_512(
        json.dumps(payload, ensure_ascii=False, allow_nan=False, sort_keys=False, separators=(",", ":")).encode("utf-8")
    ).hexdigest()
    return f"final-representation:{digest[:48]}"


def _digest(instance: "LegalClientMatterFinalRepresentation") -> str:
    payload = {field: _json_value(getattr(instance, field)) for field in _FIELDS[:-1]}
    return hashlib.sha3_512(
        json.dumps(payload, ensure_ascii=False, allow_nan=False, sort_keys=False, separators=(",", ":")).encode("utf-8")
    ).hexdigest()


@dataclass(frozen=True, slots=True)
class LegalClientMatterFinalRepresentation:
    """Immutable final Representation truth with no decision state."""

    tenant_id: str
    case_matter_id: str
    matter_fingerprint: str
    client_party_id: str
    subject_identity_fingerprint: str
    representation_authority_id: str
    representation_authority_fingerprint: str
    firm_representation_decision_id: str
    firm_representation_decision_fingerprint: str
    representative_principal_id: str
    representative_role: str
    representation_scope_capabilities: tuple[str, ...] | list[str]
    engagement_id: str
    engagement_fingerprint: str
    mandate_id: str
    mandate_fingerprint: str
    authority_currentness_id: str
    authority_currentness_fingerprint: str
    firm_decision_currentness_id: str
    firm_decision_currentness_fingerprint: str
    representative_eligibility_reference: str
    representative_eligibility_fingerprint: str
    source_evidence_reference: str
    source_evidence_fingerprint: str
    effective_from: datetime
    occurred_at: datetime
    idempotency_key: str
    representation_id: str = ""
    schema: str = SCHEMA
    representation_version: str = VERSION
    fingerprint: str = ""

    def __post_init__(self) -> None:
        """Validate immutable fields and derive deterministic identities."""
        if self.schema != SCHEMA or self.representation_version != VERSION:
            _fail("L9C11_P24_IDENTITY_INVALID")
        normalized = {
            "tenant_id": _tenant(self.tenant_id),
            "case_matter_id": _identity("case_matter_id", self.case_matter_id),
            "matter_fingerprint": _fingerprint("matter_fingerprint", self.matter_fingerprint),
            "client_party_id": _identity("client_party_id", self.client_party_id),
            "subject_identity_fingerprint": _fingerprint("subject_identity_fingerprint", self.subject_identity_fingerprint),
            "representation_authority_id": _identity("representation_authority_id", self.representation_authority_id),
            "representation_authority_fingerprint": _fingerprint("representation_authority_fingerprint", self.representation_authority_fingerprint),
            "firm_representation_decision_id": _identity("firm_representation_decision_id", self.firm_representation_decision_id),
            "firm_representation_decision_fingerprint": _fingerprint("firm_representation_decision_fingerprint", self.firm_representation_decision_fingerprint),
            "representative_principal_id": _identity("representative_principal_id", self.representative_principal_id),
            "representative_role": _identity("representative_role", self.representative_role),
            "representation_scope_capabilities": _scope(self.representation_scope_capabilities),
            "engagement_id": _identity("engagement_id", self.engagement_id),
            "engagement_fingerprint": _fingerprint("engagement_fingerprint", self.engagement_fingerprint),
            "mandate_id": _identity("mandate_id", self.mandate_id),
            "mandate_fingerprint": _fingerprint("mandate_fingerprint", self.mandate_fingerprint),
            "authority_currentness_id": _identity("authority_currentness_id", self.authority_currentness_id),
            "authority_currentness_fingerprint": _fingerprint("authority_currentness_fingerprint", self.authority_currentness_fingerprint),
            "firm_decision_currentness_id": _identity("firm_decision_currentness_id", self.firm_decision_currentness_id),
            "firm_decision_currentness_fingerprint": _fingerprint("firm_decision_currentness_fingerprint", self.firm_decision_currentness_fingerprint),
            "representative_eligibility_reference": _reference("representative_eligibility_reference", self.representative_eligibility_reference),
            "representative_eligibility_fingerprint": _fingerprint("representative_eligibility_fingerprint", self.representative_eligibility_fingerprint),
            "source_evidence_reference": _reference("source_evidence_reference", self.source_evidence_reference),
            "source_evidence_fingerprint": _fingerprint("source_evidence_fingerprint", self.source_evidence_fingerprint),
            "effective_from": _timestamp("effective_from", self.effective_from),
            "occurred_at": _timestamp("occurred_at", self.occurred_at),
            "idempotency_key": _reference("idempotency_key", self.idempotency_key, limit=240),
        }
        if normalized["representative_role"] not in _ALLOWED_ROLES:
            _fail("L9C11_P24_REPRESENTATIVE_ROLE_INELIGIBLE")
        if cast(datetime, normalized["occurred_at"]) < cast(datetime, normalized["effective_from"]):
            _fail("L9C11_P24_OCCURRED_BEFORE_EFFECTIVE")
        for name, value in normalized.items():
            object.__setattr__(self, name, value)
        derived_id = _representation_id(self)
        if self.representation_id and self.representation_id != derived_id:
            _fail("L9C11_P24_REPRESENTATION_ID_MISMATCH")
        object.__setattr__(self, "representation_id", derived_id)
        digest = _digest(self)
        if self.fingerprint and (not isinstance(self.fingerprint, str) or not hmac.compare_digest(self.fingerprint, digest)):
            _fail("L9C11_P24_FINGERPRINT_MISMATCH")
        object.__setattr__(self, "fingerprint", digest)

    @property
    def is_final_representation(self) -> bool:
        """Return the non-stateful truth marker for this formed snapshot."""
        return True

    def to_dict(self) -> dict[str, object]:
        """Serialize the exact immutable snapshot without source payloads."""
        return {field: _json_value(getattr(self, field)) for field in _FIELDS}

    @classmethod
    def from_dict(cls, payload: Mapping[str, object]) -> "LegalClientMatterFinalRepresentation":
        """Hydrate only the exact P24 schema and verify integrity."""
        if not isinstance(payload, Mapping) or set(payload) != set(_FIELDS):
            _fail("L9C11_P24_SCHEMA_INVALID")
        values = dict(payload)
        stored = values.pop("fingerprint")
        result = cls(**cast(Any, values))
        if not isinstance(stored, str) or not hmac.compare_digest(stored, result.fingerprint):
            _fail("L9C11_P24_FINGERPRINT_MISMATCH")
        return result

    @classmethod
    def from_canonical(
        cls,
        *,
        authority: LegalClientMatterRepresentationAuthority,
        authority_currentness: LegalClientMatterRepresentationAuthorityCurrentness,
        firm_decision: LegalClientMatterRepresentationFirmDecision,
        firm_decision_currentness: LegalClientMatterRepresentationFirmDecisionCurrentness,
        engagement: LegalClientMatterEngagement,
        engagement_currentness: LegalClientMatterEngagementCurrentness,
        mandate: LegalClientMatterMandate,
        mandate_currentness: LegalClientMatterMandateCurrentness,
        representation_scope_capabilities: tuple[str, ...] | list[str],
        representative_eligibility_reference: str,
        representative_eligibility_fingerprint: str,
        source_evidence_reference: str,
        source_evidence_fingerprint: str,
        effective_from: datetime,
        occurred_at: datetime,
        idempotency_key: str,
        representation_version: str = VERSION,
    ) -> "LegalClientMatterFinalRepresentation":
        """Form one final snapshot from exact positive certified prerequisites."""
        expected = (
            ("authority", LegalClientMatterRepresentationAuthority, authority),
            ("authority_currentness", LegalClientMatterRepresentationAuthorityCurrentness, authority_currentness),
            ("firm_decision", LegalClientMatterRepresentationFirmDecision, firm_decision),
            ("firm_decision_currentness", LegalClientMatterRepresentationFirmDecisionCurrentness, firm_decision_currentness),
            ("engagement", LegalClientMatterEngagement, engagement),
            ("engagement_currentness", LegalClientMatterEngagementCurrentness, engagement_currentness),
            ("mandate", LegalClientMatterMandate, mandate),
            ("mandate_currentness", LegalClientMatterMandateCurrentness, mandate_currentness),
        )
        for name, expected_type, value in expected:
            if type(value) is not expected_type:
                _fail(f"L9C11_P24_{name.upper()}_REQUIRED")
            try:
                value.__post_init__()  # type: ignore[attr-defined]
            except Exception as error:
                _fail(f"L9C11_P24_{name.upper()}_INVALID", error)
        if not authority_currentness.is_currently_appointed:
            _fail("L9C11_P24_APPOINTED_CURRENTNESS_REQUIRED")
        if not firm_decision_currentness.is_currently_accepted:
            _fail("L9C11_P24_ACCEPTED_CURRENTNESS_REQUIRED")
        if not engagement_currentness.is_usable:
            _fail("L9C11_P24_CURRENT_ENGAGEMENT_REQUIRED")
        if not mandate_currentness.is_usable:
            _fail("L9C11_P24_CURRENT_MANDATE_REQUIRED")
        correlations = (
            authority.tenant_id == firm_decision.tenant_id == engagement.tenant_id == mandate.tenant_id,
            authority.case_matter_id == firm_decision.case_matter_id == engagement.case_matter_id == mandate.case_matter_id,
            authority.matter_fingerprint == firm_decision.matter_fingerprint == engagement.matter_fingerprint == mandate.matter_fingerprint,
            authority.client_party_id == firm_decision.client_party_id == engagement.client_party_id == mandate.client_party_id,
            authority.subject_identity_fingerprint == firm_decision.subject_identity_fingerprint == engagement.subject_identity_fingerprint == mandate.subject_identity_fingerprint,
            authority.engagement_id == engagement.engagement_id and authority.engagement_fingerprint == engagement.fingerprint,
            firm_decision.engagement_id == engagement.engagement_id and firm_decision.engagement_fingerprint == engagement.fingerprint,
            authority.mandate_id == mandate.mandate_id and authority.mandate_fingerprint == mandate.fingerprint,
            firm_decision.mandate_id == mandate.mandate_id and firm_decision.mandate_fingerprint == mandate.fingerprint,
            engagement.mandate_id == mandate.mandate_id and engagement.mandate_fingerprint == mandate.fingerprint,
            engagement.mandate_scope == mandate.scope_reference,
            authority.mandate_scope_reference == mandate.scope_reference and authority.mandate_scope_fingerprint == mandate.scope_fingerprint,
            firm_decision.representation_authority_id == authority.authority_id and firm_decision.representation_authority_fingerprint == authority.fingerprint,
            authority_currentness.tenant_id == authority.tenant_id and authority_currentness.case_matter_id == authority.case_matter_id and authority_currentness.matter_fingerprint == authority.matter_fingerprint and authority_currentness.client_party_id == authority.client_party_id and authority_currentness.subject_identity_fingerprint == authority.subject_identity_fingerprint,
            authority_currentness.decisive_authority_id == authority.authority_id and authority_currentness.decisive_authority_fingerprint == authority.fingerprint,
            authority_currentness.representative_principal_id == authority.representative_principal_id and authority_currentness.representative_role == authority.representative_role and authority_currentness.representation_scope_capabilities == tuple(authority.representation_scope_capabilities),
            firm_decision_currentness.tenant_id == firm_decision.tenant_id and firm_decision_currentness.case_matter_id == firm_decision.case_matter_id and firm_decision_currentness.matter_fingerprint == firm_decision.matter_fingerprint and firm_decision_currentness.client_party_id == firm_decision.client_party_id and firm_decision_currentness.subject_identity_fingerprint == firm_decision.subject_identity_fingerprint,
            firm_decision_currentness.representation_authority_id == authority.authority_id and firm_decision_currentness.representation_authority_fingerprint == authority.fingerprint,
            firm_decision_currentness.decisive_decision_id == firm_decision.decision_id and firm_decision_currentness.decisive_decision_fingerprint == firm_decision.fingerprint,
            firm_decision_currentness.representative_principal_id == authority.representative_principal_id and firm_decision_currentness.representative_role == authority.representative_role and firm_decision_currentness.decisive_representation_scope_capabilities == tuple(firm_decision.representation_scope_capabilities),
        )
        if not all(correlations):
            _fail("L9C11_P24_UPSTREAM_LINEAGE_MISMATCH")
        role = _identity("representative_role", authority.representative_role)
        if role not in _ALLOWED_ROLES:
            _fail("L9C11_P24_REPRESENTATIVE_ROLE_INELIGIBLE")
        final_scope = _scope(representation_scope_capabilities)
        authoritative_scopes = (
            set(authority.representation_scope_capabilities),
            set(firm_decision.representation_scope_capabilities),
            {str(item) for item in mandate.capabilities},
        )
        if any(not set(final_scope).issubset(scope) for scope in authoritative_scopes):
            _fail("L9C11_P24_SCOPE_WIDENING_FORBIDDEN")
        effective = _timestamp("effective_from", effective_from)
        occurred = _timestamp("occurred_at", occurred_at)
        lower_bound = max(authority.effective_from, firm_decision.effective_from, engagement.effective_from, mandate.effective_from)
        if effective < lower_bound:
            _fail("L9C11_P24_EFFECTIVE_FROM_BEFORE_PREREQUISITE")
        if occurred < effective:
            _fail("L9C11_P24_OCCURRED_BEFORE_EFFECTIVE")
        if effective > authority_currentness.evaluated_at or effective > firm_decision_currentness.evaluated_at:
            _fail("L9C11_P24_EFFECTIVE_AFTER_CURRENTNESS_EVALUATION")
        return cls(
            tenant_id=authority.tenant_id,
            case_matter_id=authority.case_matter_id,
            matter_fingerprint=authority.matter_fingerprint,
            client_party_id=authority.client_party_id,
            subject_identity_fingerprint=authority.subject_identity_fingerprint,
            representation_authority_id=authority.authority_id,
            representation_authority_fingerprint=authority.fingerprint,
            firm_representation_decision_id=firm_decision.decision_id,
            firm_representation_decision_fingerprint=firm_decision.fingerprint,
            representative_principal_id=authority.representative_principal_id,
            representative_role=role,
            representation_scope_capabilities=final_scope,
            engagement_id=engagement.engagement_id,
            engagement_fingerprint=engagement.fingerprint,
            mandate_id=mandate.mandate_id,
            mandate_fingerprint=mandate.fingerprint,
            authority_currentness_id=authority_currentness.currentness_id,
            authority_currentness_fingerprint=authority_currentness.fingerprint,
            firm_decision_currentness_id=firm_decision_currentness.currentness_id,
            firm_decision_currentness_fingerprint=firm_decision_currentness.fingerprint,
            representative_eligibility_reference=representative_eligibility_reference,
            representative_eligibility_fingerprint=representative_eligibility_fingerprint,
            source_evidence_reference=source_evidence_reference,
            source_evidence_fingerprint=source_evidence_fingerprint,
            effective_from=effective,
            occurred_at=occurred,
            idempotency_key=idempotency_key,
            schema=SCHEMA,
            representation_version=representation_version,
        )


__all__ = [
    "FINAL_REPRESENTATION_FIELDS",
    "SCHEMA",
    "VERSION",
    "LegalClientMatterFinalRepresentation",
    "LegalClientMatterFinalRepresentationError",
]


# ARTIFACT: legal_client_matter_final_representation.py
# VERSION: v1.0.0-L9C11-P24-FINAL-REPRESENTATION
# AUTHORITY BOUNDARY: immutable final Representation truth only
# TENANT POSTURE: exact P1/P2/Engagement/Mandate lineage; no fallback
# FAIL-CLOSED POSTURE: positive prerequisites, scope, role, chronology and integrity are mandatory
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively
# END OF WILSY OS SOVEREIGN ARTIFACT
