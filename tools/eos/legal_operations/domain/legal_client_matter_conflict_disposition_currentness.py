"""Pure currentness projection for historical conflict dispositions.

TITLE: WILSY OS Legal Client Matter Conflict Disposition Currentness
VERSION: v1.0.0-L9C5-CONFLICT-DISPOSITION-CURRENTNESS
AUTHORITY: Wilsy OS Core Governance / Python EOS Legal Operations
EPITOME: Derive the disposition state that is authoritative for one exact
         tenant, matter, client party and subject at one explicit instant.
         This artifact is immutable evidence only; it does not form an
         Engagement or grant any legal, IAM, representation, court or
         financial authority.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tools/eos/legal_operations/domain/legal_client_matter_conflict_disposition_currentness.py
COLLABORATION / OWNERSHIP: LegalClientMatterConflictDisposition owns each
                            immutable historical decision. A future composer
                            owns registry reads and caller transactions;
                            this module owns only pure currentness derivation.
CERTIFICATION / UPDATE DATE: 2026-09-27
CHANGELOG: v1.0.0-L9C5-CONFLICT-DISPOSITION-CURRENTNESS establishes explicit
           time-bounded latest-effective disposition semantics, corruption-
           first fail-closed precedence, exact scope correlation, immutable
           decisive evidence lineage, strict hydration and SHA3-512 integrity.
           It adds no registry, Mongo, IAM, Engagement, Representation,
           Court, delivery or financial authority.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2; ISO 27001.
SECURITY / PRIVACY POSTURE: Only opaque identifiers and fingerprints are
                             retained; malformed evidence is represented by
                             a non-sensitive diagnostic fingerprint. No raw
                             narrative, PII, credentials, tokens or clocks.
TENANT BOUNDARY: Every supplied disposition must match the exact requested
                 tenant, matter, matter fingerprint, client party and subject
                 fingerprint. Cross-scope evidence is corruption, never
                 absence.
AUTHORITY BOUNDARY: Pure derived conflict-disposition currentness only.
                    The projection never authenticates an actor, reinterprets
                    review/screening, creates client consent, forms Engagement,
                    grants IAM, Representation or Court authority, or persists
                    currentness.
FINANCIAL AUTHORITY BOUNDARY: No payment, settlement, release or execution
                              authority; Kennel EOS remains exclusive.
TRANSACTION BOUNDARY: Immutable in-memory construction and strict
                      serialization/hydration only. A future composer owns
                      reads, transactions, retries and persistence.
FAIL-CLOSED DECLARATION: Corrupt evidence outranks every normal result;
                         same-effective conflicting states are AMBIGUOUS;
                         only ENGAGEMENT_PERMITTED is positive.
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

from tools.eos.legal_operations.domain.legal_client_matter_conflict_disposition import (
    LegalClientMatterConflictDisposition,
    LegalClientMatterConflictDispositionType,
)


VERSION: Final[str] = "v1.0.0-L9C5-CONFLICT-DISPOSITION-CURRENTNESS"
SCHEMA: Final[str] = "WILSY-LEGAL-CLIENT-MATTER-CONFLICT-DISPOSITION-CURRENTNESS/V1"
UTC = timezone.utc
_IDENTITY: Final[re.Pattern[str]] = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._:-]{0,159}$")
_HEX: Final[re.Pattern[str]] = re.compile(r"^[0-9a-f]{128}$")
_FORBIDDEN_TENANTS: Final[frozenset[str]] = frozenset(
    {"default", "global", "global_root", "root", "master", "*"}
)
_FIELDS: Final[tuple[str, ...]] = (
    "schema",
    "currentness_version",
    "currentness_id",
    "tenant_id",
    "case_matter_id",
    "matter_fingerprint",
    "client_party_id",
    "subject_identity_fingerprint",
    "evaluation_time",
    "decisive_effective_from",
    "decisive_disposition_ids",
    "decisive_disposition_fingerprints",
    "decisive_dispositions",
    "decisive_screening_ids",
    "decisive_screening_fingerprints",
    "decisive_conflict_review_ids",
    "decisive_conflict_review_fingerprints",
    "decisive_review_outcomes",
    "corruption_evidence_fingerprints",
    "state",
    "reason",
    "fingerprint",
)
CURRENTNESS_FIELDS: Final[frozenset[str]] = frozenset(_FIELDS)


class LegalClientMatterConflictDispositionCurrentnessState(StrEnum):
    """Closed result vocabulary; only ``ENGAGEMENT_PERMITTED`` is positive."""

    NO_DISPOSITION = "NO_DISPOSITION"
    ENGAGEMENT_PERMITTED = "ENGAGEMENT_PERMITTED"
    ENGAGEMENT_PROHIBITED = "ENGAGEMENT_PROHIBITED"
    ENGAGEMENT_UNRESOLVED = "ENGAGEMENT_UNRESOLVED"
    AMBIGUOUS = "AMBIGUOUS"
    CORRUPT_BLOCKED = "CORRUPT_BLOCKED"


class LegalClientMatterConflictDispositionCurrentnessReason(StrEnum):
    """Bounded explanation vocabulary aligned to projection states."""

    NO_DISPOSITION = "NO_DISPOSITION"
    ENGAGEMENT_PERMITTED = "ENGAGEMENT_PERMITTED"
    ENGAGEMENT_PROHIBITED = "ENGAGEMENT_PROHIBITED"
    ENGAGEMENT_UNRESOLVED = "ENGAGEMENT_UNRESOLVED"
    AMBIGUOUS = "AMBIGUOUS"
    CORRUPT_EVIDENCE = "CORRUPT_EVIDENCE"


class LegalClientMatterConflictDispositionCurrentnessError(ValueError):
    """Stable non-sensitive validation failure for the pure projection."""

    def __init__(self, code: str) -> None:
        self.code = code
        super().__init__(code)


def _fail(code: str, cause: BaseException | None = None) -> NoReturn:
    error = LegalClientMatterConflictDispositionCurrentnessError(code)
    if cause is None:
        raise error
    raise error from cause


def _identity(name: str, value: object) -> str:
    if not isinstance(value, str) or value != value.strip() or _IDENTITY.fullmatch(value) is None:
        _fail(f"L9C5_{name.upper()}_INVALID")
    return value


def _tenant(value: object) -> str:
    result = _identity("tenant_id", value)
    if result.casefold() in _FORBIDDEN_TENANTS:
        _fail("L9C5_TENANT_REQUIRED")
    return result


def _fingerprint(name: str, value: object) -> str:
    if not isinstance(value, str) or _HEX.fullmatch(value) is None:
        _fail(f"L9C5_{name.upper()}_INVALID")
    return value


def _timestamp(name: str, value: object) -> datetime:
    parsed = value
    if isinstance(parsed, str):
        try:
            parsed = datetime.fromisoformat(parsed.replace("Z", "+00:00"))
        except ValueError as error:
            _fail(f"L9C5_{name.upper()}_INVALID", error)
    if not isinstance(parsed, datetime) or parsed.tzinfo is None or parsed.utcoffset() is None:
        _fail(f"L9C5_{name.upper()}_INVALID")
    return parsed.astimezone(UTC).replace(microsecond=parsed.microsecond)


def _tuple_values(name: str, value: object, validator: Any, *, unique: bool = True) -> tuple[str, ...]:
    if not isinstance(value, (tuple, list)):
        _fail(f"L9C5_{name.upper()}_INVALID")
    result = tuple(validator(name, item) for item in cast(tuple[Any, ...] | list[Any], value))
    if unique and len(set(result)) != len(result):
        _fail(f"L9C5_{name.upper()}_DUPLICATE")
    return result


def _json_value(value: object) -> object:
    if isinstance(value, datetime):
        return value.astimezone(UTC).isoformat(timespec="microseconds").replace("+00:00", "Z")
    if isinstance(value, StrEnum):
        return value.value
    if isinstance(value, tuple):
        return [_json_value(item) for item in value]
    return value


def _digest(instance: "LegalClientMatterConflictDispositionCurrentness") -> str:
    payload = {field: _json_value(getattr(instance, field)) for field in _FIELDS[:-1]}
    return hashlib.sha3_512(
        json.dumps(payload, ensure_ascii=False, allow_nan=False, sort_keys=False, separators=(",", ":")).encode("utf-8")
    ).hexdigest()


def _projection_id(tenant_id: str, matter_id: str, evaluation_time: datetime) -> str:
    payload = {
        "tenant_id": tenant_id,
        "case_matter_id": matter_id,
        "evaluation_time": evaluation_time.isoformat(timespec="microseconds"),
    }
    digest = hashlib.sha3_512(json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")).hexdigest()[:48]
    return f"currentness-{digest}"


def _corruption_fingerprint(index: int, code: str) -> str:
    """Produce a non-sensitive stable marker without serializing bad input."""
    return hashlib.sha3_512(f"L9C5:{index}:{code}".encode("utf-8")).hexdigest()


def _state(value: object) -> LegalClientMatterConflictDispositionCurrentnessState:
    try:
        return LegalClientMatterConflictDispositionCurrentnessState(value)
    except (TypeError, ValueError) as error:
        _fail("L9C5_STATE_INVALID", error)


def _disposition(name: str, value: object) -> str:
    """Parse one closed historical disposition label."""
    try:
        return LegalClientMatterConflictDispositionType(value).value
    except (TypeError, ValueError) as error:
        _fail(f"L9C5_{name.upper()}_INVALID", error)


@dataclass(frozen=True, slots=True)
class LegalClientMatterConflictDispositionCurrentness:
    """Immutable exact-scope currentness evidence.

    The factory derives all decisive fields from immutable domain records. It
    performs no persistence, registry read, authentication, authorization,
    clock access, network operation or downstream Engagement mutation. A
    caller may use ``is_engagement_permitted`` only as a narrow positive
    projection; it is not permission to form an Engagement.
    """

    currentness_id: str
    tenant_id: str
    case_matter_id: str
    matter_fingerprint: str
    client_party_id: str
    subject_identity_fingerprint: str
    evaluation_time: datetime
    decisive_effective_from: datetime | None
    decisive_disposition_ids: tuple[str, ...]
    decisive_disposition_fingerprints: tuple[str, ...]
    decisive_dispositions: tuple[str, ...]
    decisive_screening_ids: tuple[str, ...]
    decisive_screening_fingerprints: tuple[str, ...]
    decisive_conflict_review_ids: tuple[str, ...]
    decisive_conflict_review_fingerprints: tuple[str, ...]
    decisive_review_outcomes: tuple[str, ...]
    corruption_evidence_fingerprints: tuple[str, ...]
    state: LegalClientMatterConflictDispositionCurrentnessState | str
    reason: LegalClientMatterConflictDispositionCurrentnessReason | str
    schema: str = SCHEMA
    currentness_version: str = VERSION
    fingerprint: str = ""

    def __post_init__(self) -> None:
        if self.schema != SCHEMA or self.currentness_version != VERSION:
            _fail("L9C5_IDENTITY_INVALID")
        currentness_id = _identity("currentness_id", self.currentness_id)
        tenant_id = _tenant(self.tenant_id)
        matter_id = _identity("case_matter_id", self.case_matter_id)
        matter_fp = _fingerprint("matter_fingerprint", self.matter_fingerprint)
        party_id = _identity("client_party_id", self.client_party_id)
        subject_fp = _fingerprint("subject_identity_fingerprint", self.subject_identity_fingerprint)
        evaluation_time = _timestamp("evaluation_time", self.evaluation_time)
        decisive_time = None if self.decisive_effective_from is None else _timestamp("decisive_effective_from", self.decisive_effective_from)
        ids = _tuple_values("decisive_disposition_ids", self.decisive_disposition_ids, _identity)
        fingerprints = _tuple_values("decisive_disposition_fingerprints", self.decisive_disposition_fingerprints, _fingerprint)
        dispositions = _tuple_values("decisive_dispositions", self.decisive_dispositions, _disposition, unique=False)
        screening_ids = _tuple_values("decisive_screening_ids", self.decisive_screening_ids, _identity, unique=False)
        screening_fps = _tuple_values("decisive_screening_fingerprints", self.decisive_screening_fingerprints, _fingerprint, unique=False)
        review_ids = _tuple_values("decisive_conflict_review_ids", self.decisive_conflict_review_ids, _identity, unique=False)
        review_fps = _tuple_values("decisive_conflict_review_fingerprints", self.decisive_conflict_review_fingerprints, _fingerprint, unique=False)
        outcomes = _tuple_values("decisive_review_outcomes", self.decisive_review_outcomes, lambda _n, value: str(value) if isinstance(value, str) and value.strip() else _fail("L9C5_DECISIVE_REVIEW_OUTCOMES_INVALID"), unique=False)
        corruption = _tuple_values("corruption_evidence_fingerprints", self.corruption_evidence_fingerprints, _fingerprint)
        state = _state(self.state)
        reason_value = self.reason
        try:
            reason = LegalClientMatterConflictDispositionCurrentnessReason(reason_value)
        except (TypeError, ValueError) as error:
            _fail("L9C5_REASON_INVALID", error)
        if not (len(ids) == len(fingerprints) == len(dispositions) == len(screening_ids) == len(screening_fps) == len(review_ids) == len(review_fps) == len(outcomes)):
            _fail("L9C5_DECISIVE_EVIDENCE_LENGTH_MISMATCH")
        if state is LegalClientMatterConflictDispositionCurrentnessState.NO_DISPOSITION:
            if decisive_time is not None or ids or fingerprints or dispositions or screening_ids or screening_fps or review_ids or review_fps or outcomes or corruption:
                _fail("L9C5_NO_DISPOSITION_EVIDENCE_FORBIDDEN")
        elif state is LegalClientMatterConflictDispositionCurrentnessState.CORRUPT_BLOCKED:
            if not corruption:
                _fail("L9C5_CORRUPTION_EVIDENCE_REQUIRED")
        else:
            if decisive_time is None or not ids or corruption:
                _fail("L9C5_DECISIVE_EVIDENCE_REQUIRED")
            if decisive_time is not None and decisive_time > evaluation_time:
                _fail("L9C5_DECISIVE_TIME_INVALID")
            if state is LegalClientMatterConflictDispositionCurrentnessState.AMBIGUOUS:
                if len(set(dispositions)) < 2:
                    _fail("L9C5_AMBIGUITY_EVIDENCE_REQUIRED")
            elif len(set(dispositions)) != 1 or dispositions[0] != state.value:
                _fail("L9C5_STATE_EVIDENCE_MISMATCH")
        expected_reason = LegalClientMatterConflictDispositionCurrentnessReason.CORRUPT_EVIDENCE if state is LegalClientMatterConflictDispositionCurrentnessState.CORRUPT_BLOCKED else LegalClientMatterConflictDispositionCurrentnessReason(state.value)
        if reason is not expected_reason:
            _fail("L9C5_REASON_STATE_MISMATCH")
        object.__setattr__(self, "currentness_id", currentness_id)
        object.__setattr__(self, "tenant_id", tenant_id)
        object.__setattr__(self, "case_matter_id", matter_id)
        object.__setattr__(self, "matter_fingerprint", matter_fp)
        object.__setattr__(self, "client_party_id", party_id)
        object.__setattr__(self, "subject_identity_fingerprint", subject_fp)
        object.__setattr__(self, "evaluation_time", evaluation_time)
        object.__setattr__(self, "decisive_effective_from", decisive_time)
        for name, value in (("decisive_disposition_ids", ids), ("decisive_disposition_fingerprints", fingerprints), ("decisive_dispositions", dispositions), ("decisive_screening_ids", screening_ids), ("decisive_screening_fingerprints", screening_fps), ("decisive_conflict_review_ids", review_ids), ("decisive_conflict_review_fingerprints", review_fps), ("decisive_review_outcomes", outcomes), ("corruption_evidence_fingerprints", corruption), ("state", state), ("reason", reason)):
            object.__setattr__(self, name, value)
        digest = _digest(self)
        if self.fingerprint and (not isinstance(self.fingerprint, str) or not hmac.compare_digest(self.fingerprint, digest)):
            _fail("L9C5_FINGERPRINT_MISMATCH")
        object.__setattr__(self, "fingerprint", digest)

    @property
    def is_engagement_permitted(self) -> bool:
        """Return true only for the exact positive disposition state."""
        return self.state is LegalClientMatterConflictDispositionCurrentnessState.ENGAGEMENT_PERMITTED

    @property
    def is_usable(self) -> bool:
        """Alias for the intentionally narrow positive predicate."""
        return self.is_engagement_permitted

    @property
    def is_permitted(self) -> bool:
        """Compatibility alias for the same narrow positive predicate."""
        return self.is_engagement_permitted

    @property
    def is_current(self) -> bool:
        """Compatibility alias; currentness is not downstream authorization."""
        return self.is_engagement_permitted

    @property
    def reason_code(self) -> LegalClientMatterConflictDispositionCurrentnessReason:
        """Return the bounded reason vocabulary."""
        return cast(LegalClientMatterConflictDispositionCurrentnessReason, self.reason)

    def to_dict(self) -> dict[str, object]:
        """Serialize all immutable evidence fields deterministically."""
        return {field: _json_value(getattr(self, field)) for field in _FIELDS}

    @classmethod
    def from_dict(cls, payload: Mapping[str, object]) -> "LegalClientMatterConflictDispositionCurrentness":
        """Hydrate the exact schema and verify the supplied SHA3-512 digest."""
        if not isinstance(payload, Mapping) or set(payload) != set(_FIELDS):
            _fail("L9C5_SCHEMA_INVALID")
        values = dict(payload)
        stored = values.pop("fingerprint")
        result = cls(**cast(dict[str, Any], values))
        if not isinstance(stored, str) or not hmac.compare_digest(stored, result.fingerprint):
            _fail("L9C5_FINGERPRINT_MISMATCH")
        return result


def _corrupt_result(tenant: str, matter_id: str, matter_fp: str, party: str, subject: str, at: datetime, evidence: tuple[str, ...]) -> LegalClientMatterConflictDispositionCurrentness:
    return LegalClientMatterConflictDispositionCurrentness(
        currentness_id=_projection_id(tenant, matter_id, at), tenant_id=tenant,
        case_matter_id=matter_id, matter_fingerprint=matter_fp, client_party_id=party,
        subject_identity_fingerprint=subject, evaluation_time=at,
        decisive_effective_from=None, decisive_disposition_ids=(),
        decisive_disposition_fingerprints=(), decisive_dispositions=(),
        decisive_screening_ids=(), decisive_screening_fingerprints=(),
        decisive_conflict_review_ids=(), decisive_conflict_review_fingerprints=(),
        decisive_review_outcomes=(), corruption_evidence_fingerprints=evidence,
        state=LegalClientMatterConflictDispositionCurrentnessState.CORRUPT_BLOCKED,
        reason=LegalClientMatterConflictDispositionCurrentnessReason.CORRUPT_EVIDENCE,
    )


def project_legal_client_matter_conflict_disposition_currentness(
    *, tenant_id: str, case_matter_id: str, matter_fingerprint: str,
    client_party_id: str, subject_identity_fingerprint: str,
    evaluation_time: datetime,
    dispositions: Iterable[LegalClientMatterConflictDisposition],
) -> LegalClientMatterConflictDispositionCurrentness:
    """Project exact-scope history without persistence or hidden time.

    ``effective_from`` alone determines the decisive instant. Input order,
    occurrence time, identifier order and fingerprint order never determine
    authority. Any malformed or cross-scope authoritative record returns
    ``CORRUPT_BLOCKED`` rather than being skipped.
    """
    tenant = _tenant(tenant_id)
    matter_id = _identity("case_matter_id", case_matter_id)
    matter_fp = _fingerprint("matter_fingerprint", matter_fingerprint)
    party = _identity("client_party_id", client_party_id)
    subject = _fingerprint("subject_identity_fingerprint", subject_identity_fingerprint)
    at = _timestamp("evaluation_time", evaluation_time)
    try:
        history = tuple(dispositions)
    except Exception as error:
        return _corrupt_result(tenant, matter_id, matter_fp, party, subject, at, (_corruption_fingerprint(0, "ITERABLE"),))
    malformed: list[str] = []
    valid: list[LegalClientMatterConflictDisposition] = []
    for index, value in enumerate(history):
        if type(value) is not LegalClientMatterConflictDisposition:
            malformed.append(_corruption_fingerprint(index, "TYPE"))
            continue
        try:
            value.__post_init__()
            if (value.tenant_id != tenant or value.case_matter_id != matter_id or value.matter_fingerprint != matter_fp or value.client_party_id != party or value.subject_identity_fingerprint != subject):
                malformed.append(value.fingerprint)
            else:
                valid.append(value)
        except Exception:
            malformed.append(_corruption_fingerprint(index, "MALFORMED"))
    if malformed:
        return _corrupt_result(tenant, matter_id, matter_fp, party, subject, at, tuple(sorted(set(malformed))))
    applicable = [value for value in valid if value.effective_from <= at]
    if not applicable:
        return LegalClientMatterConflictDispositionCurrentness(
            currentness_id=_projection_id(tenant, matter_id, at), tenant_id=tenant,
            case_matter_id=matter_id, matter_fingerprint=matter_fp, client_party_id=party,
            subject_identity_fingerprint=subject, evaluation_time=at,
            decisive_effective_from=None, decisive_disposition_ids=(),
            decisive_disposition_fingerprints=(), decisive_dispositions=(),
            decisive_screening_ids=(), decisive_screening_fingerprints=(),
            decisive_conflict_review_ids=(), decisive_conflict_review_fingerprints=(),
            decisive_review_outcomes=(), corruption_evidence_fingerprints=(),
            state=LegalClientMatterConflictDispositionCurrentnessState.NO_DISPOSITION,
            reason=LegalClientMatterConflictDispositionCurrentnessReason.NO_DISPOSITION,
        )
    decisive_time = max(value.effective_from for value in applicable)
    decisive = sorted((value for value in applicable if value.effective_from == decisive_time), key=lambda value: (value.fingerprint, value.disposition_id))
    states = {str(getattr(value.disposition, "value", value.disposition)) for value in decisive}
    state = (LegalClientMatterConflictDispositionCurrentnessState.AMBIGUOUS if len(states) > 1 else LegalClientMatterConflictDispositionCurrentnessState(next(iter(states))) )
    return LegalClientMatterConflictDispositionCurrentness(
        currentness_id=_projection_id(tenant, matter_id, at), tenant_id=tenant,
        case_matter_id=matter_id, matter_fingerprint=matter_fp, client_party_id=party,
        subject_identity_fingerprint=subject, evaluation_time=at,
        decisive_effective_from=decisive_time,
        decisive_disposition_ids=tuple(value.disposition_id for value in decisive),
        decisive_disposition_fingerprints=tuple(value.fingerprint for value in decisive),
        decisive_dispositions=tuple(str(getattr(value.disposition, "value", value.disposition)) for value in decisive),
        decisive_screening_ids=tuple(value.screening_id for value in decisive),
        decisive_screening_fingerprints=tuple(value.screening_fingerprint for value in decisive),
        decisive_conflict_review_ids=tuple(value.conflict_review_id for value in decisive),
        decisive_conflict_review_fingerprints=tuple(value.conflict_review_fingerprint for value in decisive),
        decisive_review_outcomes=tuple(str(getattr(value.review_outcome, "value", value.review_outcome)) for value in decisive),
        corruption_evidence_fingerprints=(), state=state,
        reason=LegalClientMatterConflictDispositionCurrentnessReason(state.value),
    )


def evaluate_legal_client_matter_conflict_disposition_currentness(**kwargs: Any) -> LegalClientMatterConflictDispositionCurrentness:
    """Named evaluation alias for callers describing an explicit evaluation."""
    return project_legal_client_matter_conflict_disposition_currentness(**kwargs)


__all__ = [
    "CURRENTNESS_FIELDS", "SCHEMA", "VERSION",
    "LegalClientMatterConflictDispositionCurrentness",
    "LegalClientMatterConflictDispositionCurrentnessError",
    "LegalClientMatterConflictDispositionCurrentnessReason",
    "LegalClientMatterConflictDispositionCurrentnessState",
    "project_legal_client_matter_conflict_disposition_currentness",
    "evaluate_legal_client_matter_conflict_disposition_currentness",
]


# ARTIFACT: legal_client_matter_conflict_disposition_currentness.py
# VERSION: v1.0.0-L9C5-CONFLICT-DISPOSITION-CURRENTNESS
# AUTHORITY BOUNDARY: immutable conflict-disposition currentness projection only
# TENANT POSTURE: exact tenant/matter/fingerprint/client/subject correlation
# FAIL-CLOSED POSTURE: corruption-first; ambiguous same-effective evidence is unusable
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively
# END OF WILSY OS SOVEREIGN ARTIFACT
