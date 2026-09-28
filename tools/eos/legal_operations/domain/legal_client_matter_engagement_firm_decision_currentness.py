"""Pure currentness projection for Engagement firm decisions.

TITLE: WILSY OS Legal Engagement Firm Decision Currentness
VERSION: v1.0.0-L9C9-P3-ENGAGEMENT-FIRM-DECISION-CURRENTNESS
AUTHORITY: Wilsy OS Core Governance / Python EOS Legal Operations
EPITOME: Derive the current firm-decision state for one exact tenant, matter,
         client-party and subject lineage at one explicit evaluation instant.
         This artifact is immutable evidence only; it never reads persistence,
         reauthorizes IAM or forms Engagement.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tools/eos/legal_operations/domain/legal_client_matter_engagement_firm_decision_currentness.py
COLLABORATION / OWNERSHIP: The L9C1 domain owns each immutable decision;
                            the L9C9 registry owns history durability; this
                            module owns only pure currentness projection. A
                            later composer owns registry reads and transactions.
CERTIFICATION / UPDATE DATE: 2026-09-28
CHANGELOG: v1.0.0-L9C9-P3-ENGAGEMENT-FIRM-DECISION-CURRENTNESS establishes
           explicit NO_DECISION/ACCEPTED/DECLINED/REQUIRES_REVIEW/AMBIGUOUS/
           CORRUPT_BLOCKED states, exact lineage, explicit aware-UTC evaluation
           time, latest-effective decision semantics, duplicate handling and
           deterministic SHA3-512 projection integrity.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2; ISO 27001.
SECURITY / PRIVACY POSTURE: Only opaque identifiers and lowercase SHA3-512
                             fingerprints are retained; corrupt input is
                             represented by non-sensitive diagnostic markers.
TENANT BOUNDARY: Every decision must match the exact requested tenant, matter,
                 client party and subject fingerprint; cross-scope evidence is
                 corruption, never absence.
AUTHORITY BOUNDARY: Pure derived firm-decision currentness only. The result
                    does not authenticate an actor, re-run IAM, read a
                    registry, form Engagement, grant Representation or Court
                    authority, or execute finance.
FINANCIAL AUTHORITY BOUNDARY: None; Kennel EOS remains exclusive financial
                               execution and settlement authority.
TRANSACTION BOUNDARY: Immutable in-memory construction and deterministic
                      serialization only; no database, clock, network, session
                      or transaction behavior.
FAIL-CLOSED DECLARATION: Corruption outranks every normal result; conflicting
                         same-effective decisions are AMBIGUOUS; only
                         ACCEPTED is positive for a later Engagement gate.
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

from tools.eos.legal_operations.domain.legal_client_matter_engagement_firm_decision import (
    LegalClientMatterEngagementFirmDecision,
    LegalClientMatterEngagementFirmDecisionType,
)


VERSION: Final[str] = "v1.0.0-L9C9-P3-ENGAGEMENT-FIRM-DECISION-CURRENTNESS"
SCHEMA: Final[str] = "WILSY-LEGAL-CLIENT-MATTER-ENGAGEMENT-FIRM-DECISION-CURRENTNESS/V1"
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
    "decisive_decision_ids",
    "decisive_decision_fingerprints",
    "decisive_decisions",
    "corruption_evidence_fingerprints",
    "state",
    "reason",
    "fingerprint",
)
CURRENTNESS_FIELDS: Final[frozenset[str]] = frozenset(_FIELDS)


class LegalClientMatterEngagementFirmDecisionCurrentnessState(StrEnum):
    """Closed currentness vocabulary; only ACCEPTED is positive."""

    NO_DECISION = "NO_DECISION"
    ACCEPTED = "ACCEPTED"
    DECLINED = "DECLINED"
    REQUIRES_REVIEW = "REQUIRES_REVIEW"
    AMBIGUOUS = "AMBIGUOUS"
    CORRUPT_BLOCKED = "CORRUPT_BLOCKED"


class LegalClientMatterEngagementFirmDecisionCurrentnessReason(StrEnum):
    """Bounded explanation vocabulary for projection states."""

    NO_DECISION = "NO_DECISION"
    ACCEPTED = "ACCEPTED"
    DECLINED = "DECLINED"
    REQUIRES_REVIEW = "REQUIRES_REVIEW"
    AMBIGUOUS = "AMBIGUOUS_DECISIONS"
    CORRUPT_EVIDENCE = "CORRUPT_EVIDENCE"


class LegalClientMatterEngagementFirmDecisionCurrentnessError(ValueError):
    """Stable non-sensitive validation failure for the pure projection."""

    def __init__(self, code: str) -> None:
        self.code = code
        super().__init__(code)


def _fail(code: str, cause: BaseException | None = None) -> NoReturn:
    error = LegalClientMatterEngagementFirmDecisionCurrentnessError(code)
    if cause is None:
        raise error
    raise error from cause


def _identity(name: str, value: object) -> str:
    if not isinstance(value, str) or value != value.strip() or _IDENTITY.fullmatch(value) is None:
        _fail(f"L9C9_P3_{name.upper()}_INVALID")
    return value


def _tenant(value: object) -> str:
    result = _identity("tenant_id", value)
    if result.casefold() in _FORBIDDEN_TENANTS:
        _fail("L9C9_P3_TENANT_REQUIRED")
    return result


def _fingerprint(name: str, value: object) -> str:
    if not isinstance(value, str) or _HEX.fullmatch(value) is None:
        _fail(f"L9C9_P3_{name.upper()}_INVALID")
    return value


def _timestamp(name: str, value: object) -> datetime:
    parsed = value
    if isinstance(parsed, str):
        try:
            parsed = datetime.fromisoformat(parsed.replace("Z", "+00:00"))
        except ValueError as error:
            _fail(f"L9C9_P3_{name.upper()}_INVALID", error)
    if not isinstance(parsed, datetime) or parsed.tzinfo is None or parsed.utcoffset() is None:
        _fail(f"L9C9_P3_{name.upper()}_INVALID")
    return parsed.astimezone(UTC)


def _string_tuple(name: str, value: object, *, fingerprints: bool, unique: bool = True) -> tuple[str, ...]:
    if not isinstance(value, (tuple, list)):
        _fail(f"L9C9_P3_{name.upper()}_INVALID")
    validator = _fingerprint if fingerprints else _identity
    result = tuple(validator(name, item) for item in cast(tuple[Any, ...] | list[Any], value))
    if unique and len(set(result)) != len(result):
        _fail(f"L9C9_P3_{name.upper()}_DUPLICATE")
    return result


def _decision_tuple(value: object) -> tuple[str, ...]:
    if not isinstance(value, (tuple, list)):
        _fail("L9C9_P3_DECISIVE_DECISIONS_INVALID")
    result: list[str] = []
    for item in cast(tuple[Any, ...] | list[Any], value):
        try:
            result.append(LegalClientMatterEngagementFirmDecisionType(item).value)
        except (TypeError, ValueError) as error:
            _fail("L9C9_P3_DECISIVE_DECISION_INVALID", error)
    return tuple(result)


def _state(value: object) -> LegalClientMatterEngagementFirmDecisionCurrentnessState:
    try:
        return LegalClientMatterEngagementFirmDecisionCurrentnessState(value)
    except (TypeError, ValueError) as error:
        _fail("L9C9_P3_STATE_INVALID", error)


def _reason(value: object) -> LegalClientMatterEngagementFirmDecisionCurrentnessReason:
    try:
        return LegalClientMatterEngagementFirmDecisionCurrentnessReason(value)
    except (TypeError, ValueError) as error:
        _fail("L9C9_P3_REASON_INVALID", error)


def _json_value(value: object) -> object:
    if isinstance(value, datetime):
        return value.astimezone(UTC).isoformat(timespec="microseconds").replace("+00:00", "Z")
    if isinstance(value, StrEnum):
        return value.value
    if isinstance(value, tuple):
        return [_json_value(item) for item in value]
    return value


def _digest(instance: "LegalClientMatterEngagementFirmDecisionCurrentness") -> str:
    payload = {field: _json_value(getattr(instance, field)) for field in _FIELDS[:-1]}
    return hashlib.sha3_512(
        json.dumps(payload, ensure_ascii=False, allow_nan=False, sort_keys=False, separators=(",", ":")).encode("utf-8")
    ).hexdigest()


def _projection_id(tenant: str, matter: str, matter_fp: str, party: str, subject: str, at: datetime) -> str:
    payload = {
        "tenant_id": tenant,
        "case_matter_id": matter,
        "matter_fingerprint": matter_fp,
        "client_party_id": party,
        "subject_identity_fingerprint": subject,
        "evaluation_time": at.isoformat(timespec="microseconds"),
    }
    digest = hashlib.sha3_512(json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")).hexdigest()[:48]
    return f"currentness-{digest}"


def _corruption_marker(code: str) -> str:
    return hashlib.sha3_512(f"L9C9-P3:{code}".encode("utf-8")).hexdigest()


@dataclass(frozen=True, slots=True)
class LegalClientMatterEngagementFirmDecisionCurrentness:
    """Immutable exact-lineage firm-decision currentness evidence.

    The projection performs no persistence, registry read, authentication,
    authorization, hidden clock read or downstream Engagement mutation. The
    ``is_engagement_permitted`` helper is only a narrow positive state check.
    """

    currentness_id: str
    tenant_id: str
    case_matter_id: str
    matter_fingerprint: str
    client_party_id: str
    subject_identity_fingerprint: str
    evaluation_time: datetime
    decisive_effective_from: datetime | None
    decisive_decision_ids: tuple[str, ...]
    decisive_decision_fingerprints: tuple[str, ...]
    decisive_decisions: tuple[str, ...]
    corruption_evidence_fingerprints: tuple[str, ...]
    state: LegalClientMatterEngagementFirmDecisionCurrentnessState | str
    reason: LegalClientMatterEngagementFirmDecisionCurrentnessReason | str
    schema: str = SCHEMA
    currentness_version: str = VERSION
    fingerprint: str = ""

    def __post_init__(self) -> None:
        if self.schema != SCHEMA or self.currentness_version != VERSION:
            _fail("L9C9_P3_IDENTITY_INVALID")
        currentness_id = _identity("currentness_id", self.currentness_id)
        tenant = _tenant(self.tenant_id)
        matter = _identity("case_matter_id", self.case_matter_id)
        matter_fp = _fingerprint("matter_fingerprint", self.matter_fingerprint)
        party = _identity("client_party_id", self.client_party_id)
        subject = _fingerprint("subject_identity_fingerprint", self.subject_identity_fingerprint)
        evaluation = _timestamp("evaluation_time", self.evaluation_time)
        decisive_time = None if self.decisive_effective_from is None else _timestamp("decisive_effective_from", self.decisive_effective_from)
        ids = _string_tuple("decisive_decision_ids", self.decisive_decision_ids, fingerprints=False)
        fingerprints = _string_tuple("decisive_decision_fingerprints", self.decisive_decision_fingerprints, fingerprints=True)
        decisions = _decision_tuple(self.decisive_decisions)
        corruption = _string_tuple("corruption_evidence_fingerprints", self.corruption_evidence_fingerprints, fingerprints=True)
        state = _state(self.state)
        reason = _reason(self.reason)
        if len(ids) != len(fingerprints) or len(ids) != len(decisions):
            _fail("L9C9_P3_DECISIVE_EVIDENCE_LENGTH_MISMATCH")
        if state is LegalClientMatterEngagementFirmDecisionCurrentnessState.NO_DECISION:
            if decisive_time is not None or ids or fingerprints or decisions or corruption:
                _fail("L9C9_P3_NO_DECISION_EVIDENCE_FORBIDDEN")
            expected_reason = LegalClientMatterEngagementFirmDecisionCurrentnessReason.NO_DECISION
        elif state is LegalClientMatterEngagementFirmDecisionCurrentnessState.CORRUPT_BLOCKED:
            if not corruption or decisive_time is not None or ids or fingerprints or decisions:
                _fail("L9C9_P3_CORRUPT_EVIDENCE_REQUIRED")
            expected_reason = LegalClientMatterEngagementFirmDecisionCurrentnessReason.CORRUPT_EVIDENCE
        else:
            if decisive_time is None or not ids or not fingerprints or not decisions or corruption:
                _fail("L9C9_P3_DECISIVE_EVIDENCE_REQUIRED")
            if decisive_time > evaluation:
                _fail("L9C9_P3_DECISIVE_TIME_INVALID")
            if state is LegalClientMatterEngagementFirmDecisionCurrentnessState.AMBIGUOUS:
                if len(set(decisions)) < 2:
                    _fail("L9C9_P3_AMBIGUITY_EVIDENCE_REQUIRED")
            elif len(set(decisions)) != 1 or decisions[0] != state.value:
                _fail("L9C9_P3_STATE_EVIDENCE_MISMATCH")
            expected_reason = (
                LegalClientMatterEngagementFirmDecisionCurrentnessReason.AMBIGUOUS
                if state is LegalClientMatterEngagementFirmDecisionCurrentnessState.AMBIGUOUS
                else LegalClientMatterEngagementFirmDecisionCurrentnessReason(state.value)
            )
        if reason is not expected_reason:
            _fail("L9C9_P3_REASON_STATE_MISMATCH")
        object.__setattr__(self, "currentness_id", currentness_id)
        object.__setattr__(self, "tenant_id", tenant)
        object.__setattr__(self, "case_matter_id", matter)
        object.__setattr__(self, "matter_fingerprint", matter_fp)
        object.__setattr__(self, "client_party_id", party)
        object.__setattr__(self, "subject_identity_fingerprint", subject)
        object.__setattr__(self, "evaluation_time", evaluation)
        object.__setattr__(self, "decisive_effective_from", decisive_time)
        object.__setattr__(self, "decisive_decision_ids", ids)
        object.__setattr__(self, "decisive_decision_fingerprints", fingerprints)
        object.__setattr__(self, "decisive_decisions", decisions)
        object.__setattr__(self, "corruption_evidence_fingerprints", corruption)
        object.__setattr__(self, "state", state)
        object.__setattr__(self, "reason", reason)
        digest = _digest(self)
        if self.fingerprint and (not isinstance(self.fingerprint, str) or not hmac.compare_digest(self.fingerprint, digest)):
            _fail("L9C9_P3_FINGERPRINT_MISMATCH")
        object.__setattr__(self, "fingerprint", digest)

    @property
    def is_engagement_permitted(self) -> bool:
        """Return true only for current ACCEPTED evidence."""
        return self.state is LegalClientMatterEngagementFirmDecisionCurrentnessState.ACCEPTED

    @property
    def is_usable(self) -> bool:
        """Expose the same narrow positive predicate without forming Engagement."""
        return self.is_engagement_permitted

    def to_dict(self) -> dict[str, object]:
        """Serialize exact immutable projection evidence."""
        return {field: _json_value(getattr(self, field)) for field in _FIELDS}

    @classmethod
    def from_dict(cls, payload: Mapping[str, object]) -> "LegalClientMatterEngagementFirmDecisionCurrentness":
        """Hydrate the exact schema and verify deterministic integrity."""
        if not isinstance(payload, Mapping) or set(payload) != set(_FIELDS):
            _fail("L9C9_P3_SCHEMA_INVALID")
        values = dict(payload)
        stored = values.pop("fingerprint")
        result = cls(**cast(dict[str, Any], values))
        if not isinstance(stored, str) or not hmac.compare_digest(stored, result.fingerprint):
            _fail("L9C9_P3_FINGERPRINT_MISMATCH")
        return result


def _corrupt_result(
    tenant: str,
    matter: str,
    matter_fp: str,
    party: str,
    subject: str,
    at: datetime,
    evidence: tuple[str, ...],
) -> LegalClientMatterEngagementFirmDecisionCurrentness:
    return LegalClientMatterEngagementFirmDecisionCurrentness(
        currentness_id=_projection_id(tenant, matter, matter_fp, party, subject, at),
        tenant_id=tenant,
        case_matter_id=matter,
        matter_fingerprint=matter_fp,
        client_party_id=party,
        subject_identity_fingerprint=subject,
        evaluation_time=at,
        decisive_effective_from=None,
        decisive_decision_ids=(),
        decisive_decision_fingerprints=(),
        decisive_decisions=(),
        corruption_evidence_fingerprints=tuple(sorted(set(evidence))),
        state=LegalClientMatterEngagementFirmDecisionCurrentnessState.CORRUPT_BLOCKED,
        reason=LegalClientMatterEngagementFirmDecisionCurrentnessReason.CORRUPT_EVIDENCE,
    )


def project_legal_client_matter_engagement_firm_decision_currentness(
    *,
    tenant_id: str,
    case_matter_id: str,
    matter_fingerprint: str,
    client_party_id: str,
    subject_identity_fingerprint: str,
    evaluated_at: datetime,
    decisions: Iterable[LegalClientMatterEngagementFirmDecision],
) -> LegalClientMatterEngagementFirmDecisionCurrentness:
    """Project exact-scope firm-decision history at explicit ``evaluated_at``.

    ``effective_from`` alone determines authority. Input order, occurrence
    time, identifiers and fingerprints never choose a winner. Invalid or
    cross-scope authoritative evidence returns ``CORRUPT_BLOCKED`` rather than
    being skipped. Future decisions are excluded.
    """
    tenant = _tenant(tenant_id)
    matter = _identity("case_matter_id", case_matter_id)
    matter_fp = _fingerprint("matter_fingerprint", matter_fingerprint)
    party = _identity("client_party_id", client_party_id)
    subject = _fingerprint("subject_identity_fingerprint", subject_identity_fingerprint)
    at = _timestamp("evaluated_at", evaluated_at)
    try:
        history = tuple(decisions)
    except Exception:
        return _corrupt_result(tenant, matter, matter_fp, party, subject, at, (_corruption_marker("ITERABLE"),))
    malformed: list[str] = []
    valid: list[LegalClientMatterEngagementFirmDecision] = []
    by_id: dict[str, LegalClientMatterEngagementFirmDecision] = {}
    by_fingerprint: dict[str, LegalClientMatterEngagementFirmDecision] = {}
    for value in history:
        if type(value) is not LegalClientMatterEngagementFirmDecision:
            malformed.append(_corruption_marker("TYPE"))
            continue
        try:
            value.__post_init__()
            if (
                value.tenant_id != tenant
                or value.case_matter_id != matter
                or value.matter_fingerprint != matter_fp
                or value.client_party_id != party
                or value.subject_identity_fingerprint != subject
            ):
                malformed.append(value.fingerprint)
                continue
            prior_id = by_id.get(value.decision_id)
            prior_fingerprint = by_fingerprint.get(value.fingerprint)
            if (prior_id is not None and prior_id.to_dict() != value.to_dict()) or (
                prior_fingerprint is not None and prior_fingerprint.to_dict() != value.to_dict()
            ):
                malformed.append(value.fingerprint)
                continue
            if prior_id is None and prior_fingerprint is None:
                by_id[value.decision_id] = value
                by_fingerprint[value.fingerprint] = value
                valid.append(value)
        except Exception:
            malformed.append(_corruption_marker("MALFORMED"))
    if malformed:
        return _corrupt_result(tenant, matter, matter_fp, party, subject, at, tuple(malformed))
    applicable = [value for value in valid if value.effective_from <= at]
    if not applicable:
        return LegalClientMatterEngagementFirmDecisionCurrentness(
            currentness_id=_projection_id(tenant, matter, matter_fp, party, subject, at),
            tenant_id=tenant,
            case_matter_id=matter,
            matter_fingerprint=matter_fp,
            client_party_id=party,
            subject_identity_fingerprint=subject,
            evaluation_time=at,
            decisive_effective_from=None,
            decisive_decision_ids=(),
            decisive_decision_fingerprints=(),
            decisive_decisions=(),
            corruption_evidence_fingerprints=(),
            state=LegalClientMatterEngagementFirmDecisionCurrentnessState.NO_DECISION,
            reason=LegalClientMatterEngagementFirmDecisionCurrentnessReason.NO_DECISION,
        )
    decisive_time = max(value.effective_from for value in applicable)
    decisive = sorted(
        (value for value in applicable if value.effective_from == decisive_time),
        key=lambda value: (value.fingerprint, value.decision_id),
    )
    states = {str(getattr(value.decision, "value", value.decision)) for value in decisive}
    state = (
        LegalClientMatterEngagementFirmDecisionCurrentnessState.AMBIGUOUS
        if len(states) > 1
        else LegalClientMatterEngagementFirmDecisionCurrentnessState(next(iter(states)))
    )
    return LegalClientMatterEngagementFirmDecisionCurrentness(
        currentness_id=_projection_id(tenant, matter, matter_fp, party, subject, at),
        tenant_id=tenant,
        case_matter_id=matter,
        matter_fingerprint=matter_fp,
        client_party_id=party,
        subject_identity_fingerprint=subject,
        evaluation_time=at,
        decisive_effective_from=decisive_time,
        decisive_decision_ids=tuple(value.decision_id for value in decisive),
        decisive_decision_fingerprints=tuple(value.fingerprint for value in decisive),
        decisive_decisions=tuple(str(getattr(value.decision, "value", value.decision)) for value in decisive),
        corruption_evidence_fingerprints=(),
        state=state,
        reason=(
            LegalClientMatterEngagementFirmDecisionCurrentnessReason.AMBIGUOUS
            if state is LegalClientMatterEngagementFirmDecisionCurrentnessState.AMBIGUOUS
            else LegalClientMatterEngagementFirmDecisionCurrentnessReason(state.value)
        ),
    )


def evaluate_legal_client_matter_engagement_firm_decision_currentness(
    **kwargs: Any,
) -> LegalClientMatterEngagementFirmDecisionCurrentness:
    """Named evaluation alias using the same pure projection semantics."""
    return project_legal_client_matter_engagement_firm_decision_currentness(**kwargs)


__all__ = [
    "CURRENTNESS_FIELDS",
    "SCHEMA",
    "VERSION",
    "LegalClientMatterEngagementFirmDecisionCurrentness",
    "LegalClientMatterEngagementFirmDecisionCurrentnessError",
    "LegalClientMatterEngagementFirmDecisionCurrentnessReason",
    "LegalClientMatterEngagementFirmDecisionCurrentnessState",
    "evaluate_legal_client_matter_engagement_firm_decision_currentness",
    "project_legal_client_matter_engagement_firm_decision_currentness",
]


# ARTIFACT: legal_client_matter_engagement_firm_decision_currentness.py
# VERSION: v1.0.0-L9C9-P3-ENGAGEMENT-FIRM-DECISION-CURRENTNESS
# AUTHORITY BOUNDARY: pure immutable firm-decision currentness projection only
# TENANT POSTURE: exact tenant/matter/fingerprint/client/subject correlation
# FAIL-CLOSED POSTURE: corruption-first; conflicting same-effective evidence is ambiguous
# FINANCIAL EXECUTION AUTHORITY: none; Kennel EOS exclusively
# END OF WILSY OS SOVEREIGN ARTIFACT
