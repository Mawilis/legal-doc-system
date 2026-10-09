"""WILSY OS immutable client-matter conflict disposition evidence.

TITLE: WILSY OS Legal Client Matter Conflict Disposition
VERSION: v1.0.0-L9B2-CONFLICT-DISPOSITION
AUTHORITY: Wilsy OS Core Governance / Python EOS Legal Operations
EPITOME: Record one explicit, immutable firm-side disposition for one exact
         client subject and matter, bound to the precise conflict-screening
         and human-review lineage that supports the decision. This value does
         not infer clearance from screening, create waiver/ethical-wall/
         recusal authority, or form an Engagement.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tools/eos/legal_operations/domain/legal_client_matter_conflict_disposition.py
COLLABORATION / OWNERSHIP: L8-8D owns screening signals; L8-8E owns durable
                            screening evidence; L8-8G owns human review
                            evidence; L9B2 owns only this immutable explicit
                            disposition contract. A later registry/currentness
                            composer, mandate authority and firm Engagement
                            decision authority remain separate.
CERTIFICATION / UPDATE DATE: 2026-09-27
CHANGELOG: v1.0.0-L9B2-CONFLICT-DISPOSITION establishes the bounded
           ENGAGEMENT_PERMITTED, ENGAGEMENT_PROHIBITED and
           ENGAGEMENT_UNRESOLVED vocabulary, exact tenant/matter/client,
           screening/review lineage, explicit decision actor and provenance,
           dual UTC chronology, strict hydration and deterministic SHA3-512
           integrity. It creates no waiver, ethical wall, recusal, mandate,
           Engagement, Representation, Court or financial authority.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2; ISO 27001.
SECURITY / PRIVACY POSTURE: Stores opaque identifiers, bounded evidence
                             references and lowercase SHA3-512 fingerprints;
                             no names, email, credentials, tokens, raw review
                             narrative or client PII are retained.
TENANT BOUNDARY: Tenant, matter, client party and subject identity derive from
                 exact canonical objects and exact screening/review lineage;
                 cross-tenant or cross-matter composition rejects.
AUTHORITY BOUNDARY: Explicit historical disposition evidence only. Screening
                    and review never become implicit clearance. This value
                    does not authenticate the actor, establish currentness,
                    grant waiver/ethical-wall/recusal authority, create client
                    consent, form Engagement, authorize Representation/Court,
                    or execute finance.
FINANCIAL AUTHORITY BOUNDARY: None; Kennel EOS remains the exclusive financial
                               execution and settlement authority.
TRANSACTION BOUNDARY: Pure immutable in-memory construction, deterministic
                      serialization and strict hydration only; no database,
                      HTTP, IAM, registry, transaction, retry or network.
FAIL-CLOSED DECLARATION: Malformed scope, lineage, classification, chronology,
                         schema or fingerprint drift rejects without coercion,
                         fallback or authority inference.
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

from tools.eos.legal_operations.domain.legal_conflict_review import (
    LegalConflictReviewDetermination,
    LegalConflictReviewOutcome,
)
from tools.eos.legal_operations.domain.legal_conflict_screening import (
    LegalConflictScreeningResult,
)
from tools.eos.legal_operations.domain.legal_matter_party import (
    LegalMatterParty,
    LegalMatterPartyRole,
    LegalMatterPartySide,
)
from tools.eos.legal_operations.domain.legal_operations_lifecycle import CaseMatter


VERSION: Final[str] = "v1.0.0-L9B2-CONFLICT-DISPOSITION"
SCHEMA: Final[str] = "WILSY-LEGAL-CLIENT-MATTER-CONFLICT-DISPOSITION/V1"
_IDENTITY: Final[re.Pattern[str]] = re.compile(
    r"^[A-Za-z0-9][A-Za-z0-9._:-]{0,159}$"
)
_HEX: Final[re.Pattern[str]] = re.compile(r"^[0-9a-f]{128}$")
_FORBIDDEN_TENANTS: Final[frozenset[str]] = frozenset(
    {"default", "global", "global_root", "root", "master", "*"}
)


class LegalClientMatterConflictDispositionError(ValueError):
    """One stable fail-closed disposition-domain error without value leakage."""

    def __init__(self, code: str) -> None:
        self.code = code
        super().__init__(code)


class LegalClientMatterConflictDispositionType(StrEnum):
    """Closed V1 decisions; no waiver, wall, recusal or generic clearance."""

    ENGAGEMENT_PERMITTED = "ENGAGEMENT_PERMITTED"
    ENGAGEMENT_PROHIBITED = "ENGAGEMENT_PROHIBITED"
    ENGAGEMENT_UNRESOLVED = "ENGAGEMENT_UNRESOLVED"


_FIELDS: Final[tuple[str, ...]] = (
    "schema",
    "disposition_version",
    "disposition_id",
    "tenant_id",
    "case_matter_id",
    "matter_fingerprint",
    "screening_id",
    "screening_fingerprint",
    "conflict_review_id",
    "conflict_review_fingerprint",
    "review_outcome",
    "client_party_id",
    "subject_identity_fingerprint",
    "disposition",
    "decision_actor_principal_id",
    "authorization_evidence_reference",
    "authorization_evidence_fingerprint",
    "supporting_evidence_reference",
    "supporting_evidence_fingerprint",
    "occurred_at",
    "effective_from",
    "idempotency_key",
    "fingerprint",
)
DISPOSITION_FIELDS: Final[frozenset[str]] = frozenset(_FIELDS)


def _fail(code: str, cause: BaseException | None = None) -> NoReturn:
    error = LegalClientMatterConflictDispositionError(code)
    if cause is None:
        raise error
    raise error from cause


def _identity(name: str, value: object) -> str:
    if (
        not isinstance(value, str)
        or value != value.strip()
        or _IDENTITY.fullmatch(value) is None
    ):
        _fail(f"L9B2_{name.upper()}_INVALID")
    return cast(str, value)


def _tenant(value: object) -> str:
    tenant = _identity("tenant_id", value)
    if tenant.casefold() in _FORBIDDEN_TENANTS:
        _fail("L9B2_TENANT_REQUIRED")
    return tenant


def _fingerprint(name: str, value: object) -> str:
    if not isinstance(value, str) or _HEX.fullmatch(value) is None:
        _fail(f"L9B2_{name.upper()}_INVALID")
    return value


def _reference(name: str, value: object, *, limit: int = 512) -> str:
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
        _fail(f"L9B2_{name.upper()}_INVALID")
    normalized = unicodedata.normalize("NFC", value)
    if not normalized or len(normalized) > limit:
        _fail(f"L9B2_{name.upper()}_INVALID")
    return normalized


def _timestamp(name: str, value: object) -> datetime:
    parsed = value
    if isinstance(parsed, str):
        try:
            parsed = datetime.fromisoformat(parsed.replace("Z", "+00:00"))
        except ValueError as error:
            _fail(f"L9B2_{name.upper()}_INVALID", error)
    if (
        not isinstance(parsed, datetime)
        or parsed.tzinfo is None
        or parsed.utcoffset() is None
    ):
        _fail(f"L9B2_{name.upper()}_INVALID")
    return parsed.astimezone(timezone.utc)


def _json_value(value: object) -> object:
    if isinstance(value, datetime):
        return (
            value.astimezone(timezone.utc)
            .isoformat(timespec="microseconds")
            .replace("+00:00", "Z")
        )
    if isinstance(value, StrEnum):
        return value.value
    return value


def _compatibility(
    outcome: LegalConflictReviewOutcome,
    disposition: LegalClientMatterConflictDispositionType,
) -> bool:
    if outcome is LegalConflictReviewOutcome.CONFLICT_IDENTIFIED:
        return disposition in {
            LegalClientMatterConflictDispositionType.ENGAGEMENT_PROHIBITED,
            LegalClientMatterConflictDispositionType.ENGAGEMENT_UNRESOLVED,
        }
    if outcome is LegalConflictReviewOutcome.ESCALATION_REQUIRED:
        return disposition is LegalClientMatterConflictDispositionType.ENGAGEMENT_UNRESOLVED
    return True


@dataclass(frozen=True, slots=True)
class LegalClientMatterConflictDisposition:
    """Immutable explicit disposition bound to one review lineage.

    The object is evidence, not IAM. `ENGAGEMENT_PERMITTED` is accepted only
    for an explicit disposition over `NO_CONFLICT_IDENTIFIED`; it is never
    inferred from a screening status or review object alone. A later registry
    owns durable currentness and a later Engagement authority owns formation.
    """

    disposition_id: str
    tenant_id: str
    case_matter_id: str
    matter_fingerprint: str
    screening_id: str
    screening_fingerprint: str
    conflict_review_id: str
    conflict_review_fingerprint: str
    review_outcome: LegalConflictReviewOutcome | str
    client_party_id: str
    subject_identity_fingerprint: str
    disposition: LegalClientMatterConflictDispositionType | str
    decision_actor_principal_id: str
    authorization_evidence_reference: str
    authorization_evidence_fingerprint: str
    supporting_evidence_reference: str
    supporting_evidence_fingerprint: str
    occurred_at: datetime
    effective_from: datetime
    idempotency_key: str
    schema: str = SCHEMA
    disposition_version: str = VERSION
    fingerprint: str = ""

    def __post_init__(self) -> None:
        if self.schema != SCHEMA or self.disposition_version != VERSION:
            _fail("L9B2_IDENTITY_INVALID")
        try:
            outcome = LegalConflictReviewOutcome(self.review_outcome)
            disposition = LegalClientMatterConflictDispositionType(self.disposition)
        except (TypeError, ValueError) as error:
            _fail("L9B2_CLASSIFICATION_INVALID", error)
        if not _compatibility(outcome, disposition):
            _fail("L9B2_REVIEW_DISPOSITION_INCOMPATIBLE")
        occurred_at = _timestamp("occurred_at", self.occurred_at)
        effective_from = _timestamp("effective_from", self.effective_from)
        if effective_from < occurred_at:
            _fail("L9B2_EFFECTIVE_FROM_INVALID")
        normalized: dict[str, object] = {
            "disposition_id": _identity("disposition_id", self.disposition_id),
            "tenant_id": _tenant(self.tenant_id),
            "case_matter_id": _identity("case_matter_id", self.case_matter_id),
            "matter_fingerprint": _fingerprint(
                "matter_fingerprint", self.matter_fingerprint
            ),
            "screening_id": _identity("screening_id", self.screening_id),
            "screening_fingerprint": _fingerprint(
                "screening_fingerprint", self.screening_fingerprint
            ),
            "conflict_review_id": _identity(
                "conflict_review_id", self.conflict_review_id
            ),
            "conflict_review_fingerprint": _fingerprint(
                "conflict_review_fingerprint", self.conflict_review_fingerprint
            ),
            "review_outcome": outcome,
            "client_party_id": _identity("client_party_id", self.client_party_id),
            "subject_identity_fingerprint": _fingerprint(
                "subject_identity_fingerprint", self.subject_identity_fingerprint
            ),
            "disposition": disposition,
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
            "supporting_evidence_reference": _reference(
                "supporting_evidence_reference", self.supporting_evidence_reference
            ),
            "supporting_evidence_fingerprint": _fingerprint(
                "supporting_evidence_fingerprint",
                self.supporting_evidence_fingerprint,
            ),
            "occurred_at": occurred_at,
            "effective_from": effective_from,
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
        if self.fingerprint and (
            not isinstance(self.fingerprint, str)
            or not hmac.compare_digest(self.fingerprint, digest)
        ):
            _fail("L9B2_FINGERPRINT_MISMATCH")
        object.__setattr__(self, "fingerprint", digest)

    def to_dict(self) -> dict[str, object]:
        """Serialize exact evidence without PII or privileged narrative."""
        return {field: _json_value(getattr(self, field)) for field in _FIELDS}

    @classmethod
    def from_dict(
        cls,
        payload: Mapping[str, object],
    ) -> "LegalClientMatterConflictDisposition":
        """Hydrate only the exact schema and verify deterministic integrity."""
        if not isinstance(payload, Mapping) or set(payload) != set(_FIELDS):
            _fail("L9B2_SCHEMA_INVALID")
        values = dict(payload)
        stored = values.pop("fingerprint")
        result = cls(**cast(Any, values))
        if not isinstance(stored, str) or not hmac.compare_digest(
            stored, result.fingerprint
        ):
            _fail("L9B2_FINGERPRINT_MISMATCH")
        return result

    @classmethod
    def from_canonical(
        cls,
        *,
        disposition_id: str,
        case_matter: CaseMatter,
        party: LegalMatterParty,
        screening: LegalConflictScreeningResult,
        conflict_review: LegalConflictReviewDetermination,
        disposition: LegalClientMatterConflictDispositionType | str,
        decision_actor_principal_id: str,
        authorization_evidence_reference: str,
        authorization_evidence_fingerprint: str,
        supporting_evidence_reference: str,
        supporting_evidence_fingerprint: str,
        occurred_at: datetime,
        effective_from: datetime,
        idempotency_key: str,
    ) -> "LegalClientMatterConflictDisposition":
        """Compose evidence from exact matter, client, screening and review.

        This factory derives repeated identity and lineage fields and rejects
        cross-tenant, cross-matter, non-client, subject-divergent or tampered
        prerequisites before the immutable disposition is created. It does not
        authenticate the actor or create any legal, client or financial power.
        """
        required = (
            ("case_matter", CaseMatter, case_matter),
            ("party", LegalMatterParty, party),
            ("screening", LegalConflictScreeningResult, screening),
            ("conflict_review", LegalConflictReviewDetermination, conflict_review),
        )
        for name, expected, value in required:
            if type(value) is not expected:
                _fail(f"L9B2_{name.upper()}_REQUIRED")
            try:
                value.__post_init__()  # type: ignore[attr-defined]
            except Exception as error:
                _fail(f"L9B2_{name.upper()}_INVALID", error)
        if party.party_side is not LegalMatterPartySide.CLIENT_SIDE:
            _fail("L9B2_CLIENT_PARTY_REQUIRED")
        if party.matter_role is not LegalMatterPartyRole.CLIENT:
            _fail("L9B2_CLIENT_PARTY_ROLE_REQUIRED")
        if (
            party.tenant_id != case_matter.tenant_id
            or party.case_matter_id != case_matter.case_matter_id
            or party.matter_fingerprint != case_matter.fingerprint
        ):
            _fail("L9B2_PARTY_MATTER_MISMATCH")
        if (
            screening.tenant_id != case_matter.tenant_id
            or screening.source_case_matter_id != case_matter.case_matter_id
            or screening.source_party_id != party.party_id
            or screening.source_party_fingerprint != party.fingerprint
            or screening.subject_identity_fingerprint
            != party.subject_identity_fingerprint
        ):
            _fail("L9B2_SCREENING_CORRELATION_MISMATCH")
        if (
            conflict_review.tenant_id != screening.tenant_id
            or conflict_review.screening_id != screening.screening_id
            or conflict_review.screening_fingerprint != screening.fingerprint
            or conflict_review.source_party_id != screening.source_party_id
            or conflict_review.source_case_matter_id != screening.source_case_matter_id
            or conflict_review.subject_identity_fingerprint
            != screening.subject_identity_fingerprint
            or conflict_review.screening_status != screening.status
        ):
            _fail("L9B2_REVIEW_CORRELATION_MISMATCH")
        return cls(
            disposition_id=disposition_id,
            tenant_id=case_matter.tenant_id,
            case_matter_id=case_matter.case_matter_id,
            matter_fingerprint=case_matter.fingerprint,
            screening_id=screening.screening_id,
            screening_fingerprint=screening.fingerprint,
            conflict_review_id=conflict_review.review_id,
            conflict_review_fingerprint=conflict_review.fingerprint,
            review_outcome=conflict_review.outcome,
            client_party_id=party.party_id,
            subject_identity_fingerprint=party.subject_identity_fingerprint,
            disposition=disposition,
            decision_actor_principal_id=decision_actor_principal_id,
            authorization_evidence_reference=authorization_evidence_reference,
            authorization_evidence_fingerprint=authorization_evidence_fingerprint,
            supporting_evidence_reference=supporting_evidence_reference,
            supporting_evidence_fingerprint=supporting_evidence_fingerprint,
            occurred_at=occurred_at,
            effective_from=effective_from,
            idempotency_key=idempotency_key,
        )


__all__ = [
    "DISPOSITION_FIELDS",
    "SCHEMA",
    "VERSION",
    "LegalClientMatterConflictDisposition",
    "LegalClientMatterConflictDispositionError",
    "LegalClientMatterConflictDispositionType",
]


# ARTIFACT: legal_client_matter_conflict_disposition.py
# VERSION: v1.0.0-L9B2-CONFLICT-DISPOSITION
# AUTHORITY BOUNDARY: explicit immutable conflict disposition evidence only
# TENANT POSTURE: exact tenant/matter/client/subject and screening/review lineage
# FAIL-CLOSED POSTURE: malformed, cross-scope, incompatible or tampered evidence rejects
# FINANCIAL EXECUTION AUTHORITY: none; Kennel EOS exclusively
# END OF WILSY OS SOVEREIGN ARTIFACT
