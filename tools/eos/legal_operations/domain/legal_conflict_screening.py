"""WILSY OS legal conflict screening evidence domain.

TITLE: Legal Conflict Screening Evidence
VERSION: v1.0.1-L8-8D-LEGAL-CONFLICT-SCREENING
AUTHORITY: Wilsy OS Core Governance / Python EOS Legal Operations
EPITOME: Derive deterministic, data-minimized conflict-screening signals only
         from exact tenant-scoped L8-8A party identity occurrences without
         converting adverse position, a database match, or absence of a match
         into a legal conflict determination or clearance decision.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tools/eos/legal_operations/domain/legal_conflict_screening.py
COLLABORATION / OWNERSHIP: L8-8A owns immutable matter-party facts; L8-8B owns
                            their persistence and exact subject lookup; L8-8D
                            owns only deterministic screening-result semantics.
                            Later orchestration may compose current matter state,
                            authorized human review, waiver/ethical-wall evidence
                            and durable screening persistence as separate gates.
CERTIFICATION / UPDATE DATE: 2026-09-25
CHANGELOG: v1.0.1-L8-8D-LEGAL-CONFLICT-SCREENING narrows the already-normalized match_kind union to LegalConflictMatchKind at serialization time for exact Pyright alignment; runtime screening semantics and serialized values are unchanged.
           v1.0.0-L8-8D-LEGAL-CONFLICT-SCREENING establishes exact-subject
           screening over L8-8A party facts. Cross-matter exact identity matches
           become REVIEW_REQUIRED signals, with a distinct opposing-side signal
           when one fact is CLIENT_SIDE and the other ADVERSE_SIDE. An empty
           exact-match set becomes NO_MATCH_FOUND only; it is explicitly not a
           no-conflict clearance. Same-matter duplicate subject facts, foreign
           tenants, mismatched subject identities, malformed evidence and
           fingerprint drift fail closed.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2; ISO 27001.
SECURITY / PRIVACY POSTURE: Screening evidence stores only opaque party/matter
                             identities and SHA3-512 fingerprints. Display names,
                             raw ID/passport/tax numbers, email, phone, address,
                             biometrics, KYC payloads and legal narrative are
                             deliberately excluded from screening output.
TENANT BOUNDARY: Source and every supplied occurrence must share one exact
                 non-global tenant and one exact subject identity fingerprint.
AUTHORITY BOUNDARY: Screening signal only. NO_MATCH_FOUND is not clearance;
                    REVIEW_REQUIRED is not a legal conflict finding, recusal,
                    waiver, ethical wall, client acceptance, representation
                    decision or legal advice.
FINANCIAL AUTHORITY BOUNDARY: None; Kennel EOS remains the exclusive financial
                               execution and settlement authority.
TRANSACTION BOUNDARY: Pure in-memory domain composition only; no database,
                      session, transaction, retry, commit or abort lifecycle.
FAIL-CLOSED DECLARATION: Foreign/malformed/divergent party evidence, same-matter
                         duplicate subject facts, mismatched subject identity,
                         invalid chronology and fingerprint drift reject.
"""
from __future__ import annotations

from collections.abc import Iterable, Mapping
from dataclasses import dataclass
from datetime import datetime, timezone
from enum import StrEnum
import hashlib
import hmac
import json
import re
from typing import Any, Final, NoReturn, cast

from tools.eos.legal_operations.domain.legal_matter_party import (
    LegalMatterParty,
    LegalMatterPartySide,
)


VERSION: Final[str] = "v1.0.1-L8-8D-LEGAL-CONFLICT-SCREENING"
SCHEMA: Final[str] = "WILSY-LEGAL-CONFLICT-SCREENING/V1"
_IDENTITY: Final[re.Pattern[str]] = re.compile(
    r"^[A-Za-z0-9][A-Za-z0-9._:-]{0,159}$"
)
_HEX: Final[re.Pattern[str]] = re.compile(r"^[0-9a-f]{128}$")
_FORBIDDEN_TENANTS: Final[frozenset[str]] = frozenset(
    {"default", "global", "global_root", "root", "master", "*"}
)


class LegalConflictScreeningError(ValueError):
    """One fail-closed L8-8D screening-domain failure with stable code."""

    def __init__(self, code: str) -> None:
        self.code = code
        super().__init__(code)


class LegalConflictScreeningStatus(StrEnum):
    """Closed screening outcomes that deliberately exclude legal clearance."""

    NO_MATCH_FOUND = "NO_MATCH_FOUND"
    REVIEW_REQUIRED = "REVIEW_REQUIRED"


class LegalConflictMatchKind(StrEnum):
    """Closed exact-subject match classifications for human review."""

    CROSS_MATTER_EXACT_SUBJECT_MATCH = "CROSS_MATTER_EXACT_SUBJECT_MATCH"
    OPPOSING_SIDE_EXACT_SUBJECT_MATCH = "OPPOSING_SIDE_EXACT_SUBJECT_MATCH"


def _fail(code: str, cause: BaseException | None = None) -> NoReturn:
    error = LegalConflictScreeningError(code)
    if cause is None:
        raise error
    raise error from cause


def _identity(name: str, value: object) -> str:
    if (
        not isinstance(value, str)
        or value != value.strip()
        or _IDENTITY.fullmatch(value) is None
    ):
        _fail(f"L8_8D_{name.upper()}_INVALID")
    return value


def _tenant(value: object) -> str:
    tenant = _identity("tenant_id", value)
    if tenant.casefold() in _FORBIDDEN_TENANTS:
        _fail("L8_8D_TENANT_REQUIRED")
    return tenant


def _fingerprint(name: str, value: object) -> str:
    if not isinstance(value, str) or _HEX.fullmatch(value) is None:
        _fail(f"L8_8D_{name.upper()}_INVALID")
    return value


def _text(name: str, value: object, *, limit: int = 512) -> str:
    if (
        not isinstance(value, str)
        or not value
        or value != value.strip()
        or len(value) > limit
        or any(ord(character) < 32 for character in value)
    ):
        _fail(f"L8_8D_{name.upper()}_INVALID")
    return value


def _timestamp(value: object) -> datetime:
    parsed = value
    if isinstance(parsed, str):
        try:
            parsed = datetime.fromisoformat(parsed.replace("Z", "+00:00"))
        except ValueError as error:
            _fail("L8_8D_SCREENED_AT_INVALID", error)
    if (
        not isinstance(parsed, datetime)
        or parsed.tzinfo is None
        or parsed.utcoffset() is None
    ):
        _fail("L8_8D_SCREENED_AT_INVALID")
    return parsed.astimezone(timezone.utc)


def _json_value(value: object) -> object:
    if isinstance(value, datetime):
        return value.astimezone(timezone.utc).isoformat().replace("+00:00", "Z")
    if isinstance(value, StrEnum):
        return value.value
    if isinstance(value, tuple):
        return [_json_value(item) for item in value]
    if isinstance(value, LegalConflictMatchSignal):
        return value.to_dict()
    return value


@dataclass(frozen=True, slots=True)
class LegalConflictMatchSignal:
    """One exact cross-matter subject occurrence requiring bounded review.

    A signal records only matching evidence topology. It does not establish a
    professional conflict, prior representation, duty, recusal requirement,
    ethical wall, waiver, client acceptance decision or legal conclusion.
    """

    tenant_id: str
    subject_identity_fingerprint: str
    source_party_id: str
    source_case_matter_id: str
    source_party_fingerprint: str
    matched_party_id: str
    matched_case_matter_id: str
    matched_party_fingerprint: str
    match_kind: LegalConflictMatchKind | str

    def __post_init__(self) -> None:
        tenant = _tenant(self.tenant_id)
        subject = _fingerprint(
            "subject_identity_fingerprint",
            self.subject_identity_fingerprint,
        )
        source_party = _identity("source_party_id", self.source_party_id)
        source_matter = _identity(
            "source_case_matter_id",
            self.source_case_matter_id,
        )
        source_fp = _fingerprint(
            "source_party_fingerprint",
            self.source_party_fingerprint,
        )
        matched_party = _identity("matched_party_id", self.matched_party_id)
        matched_matter = _identity(
            "matched_case_matter_id",
            self.matched_case_matter_id,
        )
        matched_fp = _fingerprint(
            "matched_party_fingerprint",
            self.matched_party_fingerprint,
        )
        try:
            kind = LegalConflictMatchKind(self.match_kind)
        except (TypeError, ValueError) as error:
            _fail("L8_8D_MATCH_KIND_INVALID", error)
        if source_party == matched_party:
            _fail("L8_8D_SELF_MATCH_INVALID")
        if source_matter == matched_matter:
            _fail("L8_8D_SAME_MATTER_SUBJECT_DUPLICATE")
        object.__setattr__(self, "tenant_id", tenant)
        object.__setattr__(self, "subject_identity_fingerprint", subject)
        object.__setattr__(self, "source_party_id", source_party)
        object.__setattr__(self, "source_case_matter_id", source_matter)
        object.__setattr__(self, "source_party_fingerprint", source_fp)
        object.__setattr__(self, "matched_party_id", matched_party)
        object.__setattr__(self, "matched_case_matter_id", matched_matter)
        object.__setattr__(self, "matched_party_fingerprint", matched_fp)
        object.__setattr__(self, "match_kind", kind)

    def to_dict(self) -> dict[str, object]:
        """Serialize only data-minimized exact-match topology."""
        return {
            "tenant_id": self.tenant_id,
            "subject_identity_fingerprint": self.subject_identity_fingerprint,
            "source_party_id": self.source_party_id,
            "source_case_matter_id": self.source_case_matter_id,
            "source_party_fingerprint": self.source_party_fingerprint,
            "matched_party_id": self.matched_party_id,
            "matched_case_matter_id": self.matched_case_matter_id,
            "matched_party_fingerprint": self.matched_party_fingerprint,
            "match_kind": cast(LegalConflictMatchKind, self.match_kind).value,
        }


_RESULT_FIELDS: Final[tuple[str, ...]] = (
    "schema",
    "screening_version",
    "tenant_id",
    "screening_id",
    "source_party_id",
    "source_case_matter_id",
    "source_party_fingerprint",
    "subject_identity_fingerprint",
    "screened_at",
    "status",
    "matches",
    "source_evidence_reference",
    "source_evidence_fingerprint",
    "fingerprint",
)
SCREENING_FIELDS: Final[frozenset[str]] = frozenset(_RESULT_FIELDS)


@dataclass(frozen=True, slots=True)
class LegalConflictScreeningResult:
    """Immutable result of one exact-subject screening pass.

    NO_MATCH_FOUND means only that no additional exact L8-8A occurrence was
    supplied by the authoritative query scope. It must never be presented as
    conflict clearance or permission to accept/continue representation.
    """

    tenant_id: str
    screening_id: str
    source_party_id: str
    source_case_matter_id: str
    source_party_fingerprint: str
    subject_identity_fingerprint: str
    screened_at: datetime
    status: LegalConflictScreeningStatus | str
    matches: tuple[LegalConflictMatchSignal, ...]
    source_evidence_reference: str
    source_evidence_fingerprint: str
    schema: str = SCHEMA
    screening_version: str = VERSION
    fingerprint: str = ""

    def __post_init__(self) -> None:
        tenant = _tenant(self.tenant_id)
        screening_id = _identity("screening_id", self.screening_id)
        source_party = _identity("source_party_id", self.source_party_id)
        source_matter = _identity(
            "source_case_matter_id",
            self.source_case_matter_id,
        )
        source_fp = _fingerprint(
            "source_party_fingerprint",
            self.source_party_fingerprint,
        )
        subject = _fingerprint(
            "subject_identity_fingerprint",
            self.subject_identity_fingerprint,
        )
        screened_at = _timestamp(self.screened_at)
        try:
            status = LegalConflictScreeningStatus(self.status)
        except (TypeError, ValueError) as error:
            _fail("L8_8D_SCREENING_STATUS_INVALID", error)
        if not isinstance(self.matches, tuple):
            _fail("L8_8D_MATCHES_INVALID")
        matches = tuple(self.matches)
        if any(type(item) is not LegalConflictMatchSignal for item in matches):
            _fail("L8_8D_MATCHES_INVALID")
        if len({item.matched_party_id for item in matches}) != len(matches):
            _fail("L8_8D_DUPLICATE_MATCH_INVALID")
        for item in matches:
            if (
                item.tenant_id != tenant
                or item.subject_identity_fingerprint != subject
                or item.source_party_id != source_party
                or item.source_case_matter_id != source_matter
                or item.source_party_fingerprint != source_fp
            ):
                _fail("L8_8D_MATCH_CORRELATION_INVALID")
        if status is LegalConflictScreeningStatus.NO_MATCH_FOUND and matches:
            _fail("L8_8D_STATUS_MATCH_MISMATCH")
        if status is LegalConflictScreeningStatus.REVIEW_REQUIRED and not matches:
            _fail("L8_8D_STATUS_MATCH_MISMATCH")
        evidence_reference = _text(
            "source_evidence_reference",
            self.source_evidence_reference,
        )
        evidence_fingerprint = _fingerprint(
            "source_evidence_fingerprint",
            self.source_evidence_fingerprint,
        )
        if self.schema != SCHEMA or self.screening_version != VERSION:
            _fail("L8_8D_IDENTITY_INVALID")

        sorted_matches = tuple(
            sorted(
                matches,
                key=lambda item: (
                    item.matched_case_matter_id,
                    item.matched_party_id,
                    item.matched_party_fingerprint,
                ),
            )
        )
        object.__setattr__(self, "tenant_id", tenant)
        object.__setattr__(self, "screening_id", screening_id)
        object.__setattr__(self, "source_party_id", source_party)
        object.__setattr__(self, "source_case_matter_id", source_matter)
        object.__setattr__(self, "source_party_fingerprint", source_fp)
        object.__setattr__(self, "subject_identity_fingerprint", subject)
        object.__setattr__(self, "screened_at", screened_at)
        object.__setattr__(self, "status", status)
        object.__setattr__(self, "matches", sorted_matches)
        object.__setattr__(self, "source_evidence_reference", evidence_reference)
        object.__setattr__(self, "source_evidence_fingerprint", evidence_fingerprint)

        payload = {
            field: _json_value(getattr(self, field))
            for field in _RESULT_FIELDS[:-1]
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
            _fail("L8_8D_FINGERPRINT_MISMATCH")
        object.__setattr__(self, "fingerprint", digest)

    def to_dict(self) -> dict[str, object]:
        """Serialize the immutable screening result without raw party PII."""
        return {
            field: _json_value(getattr(self, field))
            for field in _RESULT_FIELDS
        }

    @classmethod
    def from_dict(
        cls,
        payload: Mapping[str, object],
    ) -> "LegalConflictScreeningResult":
        """Hydrate one exact screening result and verify deterministic integrity."""
        if not isinstance(payload, Mapping) or set(payload) != set(_RESULT_FIELDS):
            _fail("L8_8D_SCHEMA_INVALID")
        values = dict(payload)
        raw_matches = values.get("matches")
        if not isinstance(raw_matches, list):
            _fail("L8_8D_MATCHES_INVALID")
        matches: list[LegalConflictMatchSignal] = []
        for raw in raw_matches:
            if not isinstance(raw, Mapping):
                _fail("L8_8D_MATCHES_INVALID")
            try:
                matches.append(
                    LegalConflictMatchSignal(**cast(Any, dict(raw)))
                )
            except (TypeError, ValueError, LegalConflictScreeningError) as error:
                _fail("L8_8D_MATCHES_INVALID", error)
        values["matches"] = tuple(matches)
        stored = values.pop("fingerprint")
        result = cls(**cast(Any, values))
        if (
            not isinstance(stored, str)
            or not hmac.compare_digest(stored, result.fingerprint)
        ):
            _fail("L8_8D_FINGERPRINT_MISMATCH")
        return result


def _match_kind(
    source: LegalMatterParty,
    matched: LegalMatterParty,
) -> LegalConflictMatchKind:
    sides = {source.party_side, matched.party_side}
    if sides == {
        LegalMatterPartySide.CLIENT_SIDE,
        LegalMatterPartySide.ADVERSE_SIDE,
    }:
        return LegalConflictMatchKind.OPPOSING_SIDE_EXACT_SUBJECT_MATCH
    return LegalConflictMatchKind.CROSS_MATTER_EXACT_SUBJECT_MATCH


def build_legal_conflict_screening(
    *,
    source_party: LegalMatterParty,
    occurrences: Iterable[LegalMatterParty],
    screening_id: str,
    screened_at: datetime,
    source_evidence_reference: str,
    source_evidence_fingerprint: str,
) -> LegalConflictScreeningResult:
    """Build one deterministic exact-subject screening result.

    occurrences must be the authoritative exact-tenant/exact-subject lookup
    result supplied by a later certified composer. The source party may be
    included and is ignored as self evidence. Every other exact occurrence is
    transformed into a review signal; no legal conflict or clearance is inferred.
    """
    if type(source_party) is not LegalMatterParty:
        _fail("L8_8D_SOURCE_PARTY_REQUIRED")
    values = tuple(occurrences)
    signals: list[LegalConflictMatchSignal] = []
    for occurrence in values:
        if type(occurrence) is not LegalMatterParty:
            _fail("L8_8D_OCCURRENCE_INVALID")
        if occurrence.tenant_id != source_party.tenant_id:
            _fail("L8_8D_TENANT_MISMATCH")
        if (
            occurrence.subject_identity_fingerprint
            != source_party.subject_identity_fingerprint
        ):
            _fail("L8_8D_SUBJECT_IDENTITY_MISMATCH")
        if occurrence.party_id == source_party.party_id:
            if occurrence.to_dict() != source_party.to_dict():
                _fail("L8_8D_SOURCE_PARTY_DIVERGENCE")
            continue
        if occurrence.case_matter_id == source_party.case_matter_id:
            _fail("L8_8D_SAME_MATTER_SUBJECT_DUPLICATE")
        signals.append(
            LegalConflictMatchSignal(
                tenant_id=source_party.tenant_id,
                subject_identity_fingerprint=(
                    source_party.subject_identity_fingerprint
                ),
                source_party_id=source_party.party_id,
                source_case_matter_id=source_party.case_matter_id,
                source_party_fingerprint=source_party.fingerprint,
                matched_party_id=occurrence.party_id,
                matched_case_matter_id=occurrence.case_matter_id,
                matched_party_fingerprint=occurrence.fingerprint,
                match_kind=_match_kind(source_party, occurrence),
            )
        )

    matches = tuple(
        sorted(
            signals,
            key=lambda item: (
                item.matched_case_matter_id,
                item.matched_party_id,
                item.matched_party_fingerprint,
            ),
        )
    )
    status = (
        LegalConflictScreeningStatus.REVIEW_REQUIRED
        if matches
        else LegalConflictScreeningStatus.NO_MATCH_FOUND
    )
    return LegalConflictScreeningResult(
        tenant_id=source_party.tenant_id,
        screening_id=screening_id,
        source_party_id=source_party.party_id,
        source_case_matter_id=source_party.case_matter_id,
        source_party_fingerprint=source_party.fingerprint,
        subject_identity_fingerprint=source_party.subject_identity_fingerprint,
        screened_at=screened_at,
        status=status,
        matches=matches,
        source_evidence_reference=source_evidence_reference,
        source_evidence_fingerprint=source_evidence_fingerprint,
    )


__all__ = [
    "SCHEMA",
    "SCREENING_FIELDS",
    "VERSION",
    "LegalConflictMatchKind",
    "LegalConflictMatchSignal",
    "LegalConflictScreeningError",
    "LegalConflictScreeningResult",
    "LegalConflictScreeningStatus",
    "build_legal_conflict_screening",
]


# ARTIFACT: legal_conflict_screening.py
# VERSION: v1.0.1-L8-8D-LEGAL-CONFLICT-SCREENING
# AUTHORITY BOUNDARY: exact-subject screening evidence only; no conflict determination or clearance
# TENANT POSTURE: all source/occurrence facts must share one exact tenant and subject identity
# FAIL-CLOSED POSTURE: foreign/divergent/duplicate/malformed evidence rejects; no-match never upgrades to clearance
# FINANCIAL EXECUTION AUTHORITY: none; Kennel EOS exclusively
# END OF WILSY OS SOVEREIGN ARTIFACT
