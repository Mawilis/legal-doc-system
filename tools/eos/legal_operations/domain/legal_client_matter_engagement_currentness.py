"""Pure currentness projection for immutable client-matter Engagement rows.

TITLE: WILSY OS Legal Client Matter Engagement Currentness
VERSION: v1.0.0-L9C11-P3-ENGAGEMENT-CURRENTNESS
AUTHORITY: Wilsy OS Core Governance / Python EOS Legal Operations
EPITOME: Determine whether exact immutable Engagement evidence has one and only
         one eligible record at an explicit instant. This projection does not
         invent lifecycle events or select a winner where the source contract
         provides no supersession authority.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tools/eos/legal_operations/domain/legal_client_matter_engagement_currentness.py
COLLABORATION / OWNERSHIP: LegalClientMatterEngagement owns immutable formation
                            evidence; this module owns only deterministic
                            in-memory currentness math. A future composer owns
                            registry reads and transaction boundaries.
CERTIFICATION / UPDATE DATE: 2026-09-28
CHANGELOG: v1.0.0-L9C11-P3-ENGAGEMENT-CURRENTNESS establishes explicit
           NO_ENGAGEMENT/CURRENT/AMBIGUOUS/CORRUPT_BLOCKED states, exact
           lineage, aware-UTC evaluation, future exclusion, exact-duplicate
           normalization, fail-closed corruption handling, order-independent
           multiplicity and deterministic SHA3-512 projection integrity.
           It creates no lifecycle, registry, Representation, Court, IAM or
           financial authority.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2; ISO 27001.
SECURITY / PRIVACY POSTURE: Only opaque identifiers and lowercase SHA3-512
                             fingerprints are retained; no PII or raw source
                             payloads are returned.
TENANT BOUNDARY: Every candidate must match the exact requested tenant, matter,
                 matter fingerprint, client party and subject fingerprint.
AUTHORITY BOUNDARY: Pure derived Engagement currentness only. No database,
                    current pointer, lifecycle event, IAM grant, Representation
                    formation, Court authority or actor authentication.
FINANCIAL AUTHORITY BOUNDARY: None; Kennel EOS remains exclusive for financial
                               execution and settlement.
TRANSACTION BOUNDARY: Immutable construction and deterministic serialization;
                      no clock, network, persistence or transaction behavior.
FAIL-CLOSED DECLARATION: Cross-lineage, malformed and contradictory evidence
                         yields CORRUPT_BLOCKED; multiple distinct eligible
                         rows yield AMBIGUOUS because no supersession contract
                         exists in the immutable Engagement source.
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

from tools.eos.legal_operations.domain.legal_client_matter_engagement import (
    LegalClientMatterEngagement,
)


VERSION: Final[str] = "v1.0.0-L9C11-P3-ENGAGEMENT-CURRENTNESS"
SCHEMA: Final[str] = "WILSY-LEGAL-CLIENT-MATTER-ENGAGEMENT-CURRENTNESS/V1"
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
    "evaluated_at",
    "decisive_effective_from",
    "decisive_engagement_id",
    "decisive_engagement_fingerprint",
    "candidate_engagement_ids",
    "candidate_engagement_fingerprints",
    "normalized_engagement_count",
    "eligible_engagement_count",
    "corruption_evidence_fingerprints",
    "state",
    "reason",
    "fingerprint",
)
CURRENTNESS_FIELDS: Final[frozenset[str]] = frozenset(_FIELDS)


class LegalClientMatterEngagementCurrentnessState(StrEnum):
    """Closed projection vocabulary; only CURRENT is positive."""

    NO_ENGAGEMENT = "NO_ENGAGEMENT"
    CURRENT = "CURRENT"
    AMBIGUOUS = "AMBIGUOUS"
    CORRUPT_BLOCKED = "CORRUPT_BLOCKED"


class LegalClientMatterEngagementCurrentnessReason(StrEnum):
    """Bounded reasons matching every projection state."""

    NO_ENGAGEMENT = "NO_ENGAGEMENT"
    CURRENT = "CURRENT"
    AMBIGUOUS = "AMBIGUOUS_ENGAGEMENTS"
    CORRUPT_EVIDENCE = "CORRUPT_EVIDENCE"


class LegalClientMatterEngagementCurrentnessError(ValueError):
    """Stable, non-sensitive validation failure for projection evidence."""

    def __init__(self, code: str) -> None:
        self.code = code
        super().__init__(code)


def _fail(code: str, cause: BaseException | None = None) -> NoReturn:
    error = LegalClientMatterEngagementCurrentnessError(code)
    if cause is None:
        raise error
    raise error from cause


def _identity(name: str, value: object) -> str:
    if not isinstance(value, str) or value != value.strip() or _IDENTITY.fullmatch(value) is None:
        _fail(f"L9C11_P3_{name.upper()}_INVALID")
    return cast(str, value)


def _tenant(value: object) -> str:
    tenant = _identity("tenant_id", value)
    if tenant.casefold() in _FORBIDDEN_TENANTS:
        _fail("L9C11_P3_TENANT_REQUIRED")
    return tenant


def _fingerprint(name: str, value: object) -> str:
    if not isinstance(value, str) or _HEX.fullmatch(value) is None:
        _fail(f"L9C11_P3_{name.upper()}_INVALID")
    return value


def _timestamp(name: str, value: object) -> datetime:
    parsed = value
    if isinstance(parsed, str):
        try:
            parsed = datetime.fromisoformat(parsed.replace("Z", "+00:00"))
        except ValueError as error:
            _fail(f"L9C11_P3_{name.upper()}_INVALID", error)
    if not isinstance(parsed, datetime) or parsed.tzinfo is None or parsed.utcoffset() is None:
        _fail(f"L9C11_P3_{name.upper()}_INVALID")
    return parsed.astimezone(UTC)


def _string_tuple(name: str, value: object, *, fingerprints: bool) -> tuple[str, ...]:
    if not isinstance(value, (tuple, list)):
        _fail(f"L9C11_P3_{name.upper()}_INVALID")
    validator = _fingerprint if fingerprints else _identity
    result = tuple(validator(name, item) for item in cast(tuple[Any, ...] | list[Any], value))
    if len(set(result)) != len(result):
        _fail(f"L9C11_P3_{name.upper()}_DUPLICATE")
    return result


def _json_value(value: object) -> object:
    if isinstance(value, datetime):
        return value.astimezone(UTC).isoformat(timespec="microseconds").replace("+00:00", "Z")
    if isinstance(value, StrEnum):
        return value.value
    if isinstance(value, tuple):
        return [_json_value(item) for item in value]
    return value


def _state(value: object) -> LegalClientMatterEngagementCurrentnessState:
    try:
        return LegalClientMatterEngagementCurrentnessState(value)
    except (TypeError, ValueError) as error:
        _fail("L9C11_P3_STATE_INVALID", error)


def _reason(value: object) -> LegalClientMatterEngagementCurrentnessReason:
    try:
        return LegalClientMatterEngagementCurrentnessReason(value)
    except (TypeError, ValueError) as error:
        _fail("L9C11_P3_REASON_INVALID", error)


def _projection_id(
    tenant: str,
    matter: str,
    matter_fingerprint: str,
    party: str,
    subject: str,
    evaluated_at: datetime,
) -> str:
    payload = {
        "tenant_id": tenant,
        "case_matter_id": matter,
        "matter_fingerprint": matter_fingerprint,
        "client_party_id": party,
        "subject_identity_fingerprint": subject,
        "evaluated_at": _json_value(evaluated_at),
    }
    digest = hashlib.sha3_512(
        json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")
    ).hexdigest()[:48]
    return f"engagement-currentness:{digest}"


def _corruption_marker(code: str) -> str:
    return hashlib.sha3_512(f"L9C11-P3:{code}".encode("utf-8")).hexdigest()


def _digest(instance: "LegalClientMatterEngagementCurrentness") -> str:
    payload = {field: _json_value(getattr(instance, field)) for field in _FIELDS[:-1]}
    return hashlib.sha3_512(
        json.dumps(payload, ensure_ascii=False, allow_nan=False, sort_keys=False, separators=(",", ":")).encode("utf-8")
    ).hexdigest()


@dataclass(frozen=True, slots=True)
class LegalClientMatterEngagementCurrentness:
    """Immutable exact-lineage Engagement currentness evidence.

    A single eligible distinct Engagement is CURRENT. Because the source
    Engagement contract has no supersession or termination event, two or more
    eligible distinct rows are AMBIGUOUS rather than latest-wins. The positive
    predicate is only a prerequisite signal; it never forms Representation.
    """

    currentness_id: str
    tenant_id: str
    case_matter_id: str
    matter_fingerprint: str
    client_party_id: str
    subject_identity_fingerprint: str
    evaluated_at: datetime
    decisive_effective_from: datetime | None
    decisive_engagement_id: str | None
    decisive_engagement_fingerprint: str | None
    candidate_engagement_ids: tuple[str, ...]
    candidate_engagement_fingerprints: tuple[str, ...]
    normalized_engagement_count: int
    eligible_engagement_count: int
    corruption_evidence_fingerprints: tuple[str, ...]
    state: LegalClientMatterEngagementCurrentnessState | str
    reason: LegalClientMatterEngagementCurrentnessReason | str
    schema: str = SCHEMA
    currentness_version: str = VERSION
    fingerprint: str = ""

    def __post_init__(self) -> None:
        """Validate exact state evidence and derive deterministic integrity."""
        if self.schema != SCHEMA or self.currentness_version != VERSION:
            _fail("L9C11_P3_IDENTITY_INVALID")
        currentness_id = _identity("currentness_id", self.currentness_id)
        tenant = _tenant(self.tenant_id)
        matter = _identity("case_matter_id", self.case_matter_id)
        matter_fingerprint = _fingerprint("matter_fingerprint", self.matter_fingerprint)
        party = _identity("client_party_id", self.client_party_id)
        subject = _fingerprint("subject_identity_fingerprint", self.subject_identity_fingerprint)
        evaluated_at = _timestamp("evaluated_at", self.evaluated_at)
        decisive_time = None if self.decisive_effective_from is None else _timestamp(
            "decisive_effective_from", self.decisive_effective_from
        )
        decisive_id = None if self.decisive_engagement_id is None else _identity(
            "decisive_engagement_id", self.decisive_engagement_id
        )
        decisive_fingerprint = None if self.decisive_engagement_fingerprint is None else _fingerprint(
            "decisive_engagement_fingerprint", self.decisive_engagement_fingerprint
        )
        candidate_ids = _string_tuple(
            "candidate_engagement_ids", self.candidate_engagement_ids, fingerprints=False
        )
        candidate_fingerprints = _string_tuple(
            "candidate_engagement_fingerprints",
            self.candidate_engagement_fingerprints,
            fingerprints=True,
        )
        corruption = _string_tuple(
            "corruption_evidence_fingerprints",
            self.corruption_evidence_fingerprints,
            fingerprints=True,
        )
        state = _state(self.state)
        reason = _reason(self.reason)
        if (
            isinstance(self.normalized_engagement_count, bool)
            or not isinstance(self.normalized_engagement_count, int)
            or self.normalized_engagement_count < 0
            or isinstance(self.eligible_engagement_count, bool)
            or not isinstance(self.eligible_engagement_count, int)
            or self.eligible_engagement_count < 0
            or self.eligible_engagement_count > self.normalized_engagement_count
        ):
            _fail("L9C11_P3_COUNT_INVALID")
        if len(candidate_ids) != len(candidate_fingerprints):
            _fail("L9C11_P3_CANDIDATE_EVIDENCE_LENGTH_MISMATCH")
        if state is LegalClientMatterEngagementCurrentnessState.NO_ENGAGEMENT:
            if candidate_ids or candidate_fingerprints or decisive_time is not None or decisive_id is not None or decisive_fingerprint is not None or corruption:
                _fail("L9C11_P3_NO_ENGAGEMENT_EVIDENCE_FORBIDDEN")
            if self.eligible_engagement_count != 0:
                _fail("L9C11_P3_NO_ENGAGEMENT_COUNT_INVALID")
            expected_reason = LegalClientMatterEngagementCurrentnessReason.NO_ENGAGEMENT
        elif state is LegalClientMatterEngagementCurrentnessState.CURRENT:
            if len(candidate_ids) != 1 or decisive_time is None or decisive_id is None or decisive_fingerprint is None or corruption:
                _fail("L9C11_P3_CURRENT_EVIDENCE_REQUIRED")
            if decisive_id != candidate_ids[0] or decisive_fingerprint != candidate_fingerprints[0]:
                _fail("L9C11_P3_DECISIVE_EVIDENCE_MISMATCH")
            if decisive_time > evaluated_at or self.eligible_engagement_count != 1:
                _fail("L9C11_P3_CURRENT_TIME_OR_COUNT_INVALID")
            expected_reason = LegalClientMatterEngagementCurrentnessReason.CURRENT
        elif state is LegalClientMatterEngagementCurrentnessState.AMBIGUOUS:
            if len(candidate_ids) < 2 or decisive_time is not None or decisive_id is not None or decisive_fingerprint is not None or corruption:
                _fail("L9C11_P3_AMBIGUITY_EVIDENCE_INVALID")
            if self.eligible_engagement_count < 2:
                _fail("L9C11_P3_AMBIGUITY_COUNT_INVALID")
            expected_reason = LegalClientMatterEngagementCurrentnessReason.AMBIGUOUS
        else:
            if not corruption or candidate_ids or candidate_fingerprints or decisive_time is not None or decisive_id is not None or decisive_fingerprint is not None:
                _fail("L9C11_P3_CORRUPT_EVIDENCE_INVALID")
            expected_reason = LegalClientMatterEngagementCurrentnessReason.CORRUPT_EVIDENCE
        if reason is not expected_reason:
            _fail("L9C11_P3_REASON_STATE_MISMATCH")
        for name, value in (
            ("currentness_id", currentness_id),
            ("tenant_id", tenant),
            ("case_matter_id", matter),
            ("matter_fingerprint", matter_fingerprint),
            ("client_party_id", party),
            ("subject_identity_fingerprint", subject),
            ("evaluated_at", evaluated_at),
            ("decisive_effective_from", decisive_time),
            ("decisive_engagement_id", decisive_id),
            ("decisive_engagement_fingerprint", decisive_fingerprint),
            ("candidate_engagement_ids", candidate_ids),
            ("candidate_engagement_fingerprints", candidate_fingerprints),
            ("corruption_evidence_fingerprints", corruption),
            ("state", state),
            ("reason", reason),
        ):
            object.__setattr__(self, name, value)
        digest = _digest(self)
        if self.fingerprint and (not isinstance(self.fingerprint, str) or not hmac.compare_digest(self.fingerprint, digest)):
            _fail("L9C11_P3_FINGERPRINT_MISMATCH")
        object.__setattr__(self, "fingerprint", digest)

    @property
    def is_current(self) -> bool:
        """Return true only for one exact decisive eligible Engagement."""
        return self.state is LegalClientMatterEngagementCurrentnessState.CURRENT

    @property
    def is_usable(self) -> bool:
        """Expose the same narrow prerequisite predicate without formation."""
        return self.is_current

    def to_dict(self) -> dict[str, object]:
        """Serialize exact immutable projection evidence."""
        return {field: _json_value(getattr(self, field)) for field in _FIELDS}

    @classmethod
    def from_dict(cls, payload: Mapping[str, object]) -> "LegalClientMatterEngagementCurrentness":
        """Hydrate the exact schema and verify deterministic integrity."""
        if not isinstance(payload, Mapping) or set(payload) != set(_FIELDS):
            _fail("L9C11_P3_SCHEMA_INVALID")
        values = dict(payload)
        stored = values.pop("fingerprint")
        result = cls(**cast(dict[str, Any], values))
        if not isinstance(stored, str) or not hmac.compare_digest(stored, result.fingerprint):
            _fail("L9C11_P3_FINGERPRINT_MISMATCH")
        return result


def _result(
    *,
    tenant: str,
    matter: str,
    matter_fingerprint: str,
    party: str,
    subject: str,
    evaluated_at: datetime,
    normalized_count: int,
    eligible_count: int,
    state: LegalClientMatterEngagementCurrentnessState,
    reason: LegalClientMatterEngagementCurrentnessReason,
    decisive: LegalClientMatterEngagement | None = None,
    candidates: tuple[LegalClientMatterEngagement, ...] = (),
    corruption: tuple[str, ...] = (),
) -> LegalClientMatterEngagementCurrentness:
    ordered = tuple(sorted(candidates, key=lambda value: (value.effective_from, value.fingerprint, value.engagement_id)))
    candidate_ids = tuple(value.engagement_id for value in ordered)
    candidate_fingerprints = tuple(value.fingerprint for value in ordered)
    return LegalClientMatterEngagementCurrentness(
        currentness_id=_projection_id(tenant, matter, matter_fingerprint, party, subject, evaluated_at),
        tenant_id=tenant,
        case_matter_id=matter,
        matter_fingerprint=matter_fingerprint,
        client_party_id=party,
        subject_identity_fingerprint=subject,
        evaluated_at=evaluated_at,
        decisive_effective_from=None if decisive is None else decisive.effective_from,
        decisive_engagement_id=None if decisive is None else decisive.engagement_id,
        decisive_engagement_fingerprint=None if decisive is None else decisive.fingerprint,
        candidate_engagement_ids=candidate_ids,
        candidate_engagement_fingerprints=candidate_fingerprints,
        normalized_engagement_count=normalized_count,
        eligible_engagement_count=eligible_count,
        corruption_evidence_fingerprints=tuple(sorted(set(corruption))),
        state=state,
        reason=reason,
    )


def _corrupt(
    tenant: str,
    matter: str,
    matter_fingerprint: str,
    party: str,
    subject: str,
    evaluated_at: datetime,
    evidence: tuple[str, ...],
    normalized_count: int = 0,
) -> LegalClientMatterEngagementCurrentness:
    return _result(
        tenant=tenant,
        matter=matter,
        matter_fingerprint=matter_fingerprint,
        party=party,
        subject=subject,
        evaluated_at=evaluated_at,
        normalized_count=normalized_count,
        eligible_count=0,
        state=LegalClientMatterEngagementCurrentnessState.CORRUPT_BLOCKED,
        reason=LegalClientMatterEngagementCurrentnessReason.CORRUPT_EVIDENCE,
        corruption=evidence or (_corruption_marker("UNKNOWN"),),
    )


def project_legal_client_matter_engagement_currentness(
    *,
    tenant_id: str,
    case_matter_id: str,
    matter_fingerprint: str,
    client_party_id: str,
    subject_identity_fingerprint: str,
    evaluated_at: datetime,
    engagements: Iterable[LegalClientMatterEngagement],
) -> LegalClientMatterEngagementCurrentness:
    """Project exact-lineage immutable Engagement history at ``evaluated_at``.

    The source domain defines no supersession or termination event. Therefore
    one eligible distinct row is CURRENT, while multiple eligible distinct
    rows are AMBIGUOUS; identifier or fingerprint ordering never selects a
    legal winner. Future rows are excluded after all history integrity checks.
    """
    tenant = _tenant(tenant_id)
    matter = _identity("case_matter_id", case_matter_id)
    matter_fp = _fingerprint("matter_fingerprint", matter_fingerprint)
    party = _identity("client_party_id", client_party_id)
    subject = _fingerprint("subject_identity_fingerprint", subject_identity_fingerprint)
    evaluated = _timestamp("evaluated_at", evaluated_at)
    try:
        history = tuple(engagements)
    except Exception:
        return _corrupt(tenant, matter, matter_fp, party, subject, evaluated, (_corruption_marker("ITERABLE"),))
    malformed: list[str] = []
    valid: list[LegalClientMatterEngagement] = []
    by_id: dict[str, LegalClientMatterEngagement] = {}
    by_fingerprint: dict[str, LegalClientMatterEngagement] = {}
    for candidate in history:
        if type(candidate) is not LegalClientMatterEngagement:
            malformed.append(_corruption_marker("TYPE"))
            continue
        try:
            candidate.__post_init__()
            if (
                candidate.tenant_id != tenant
                or candidate.case_matter_id != matter
                or candidate.matter_fingerprint != matter_fp
                or candidate.client_party_id != party
                or candidate.subject_identity_fingerprint != subject
            ):
                malformed.append(candidate.fingerprint)
                continue
            prior_id = by_id.get(candidate.engagement_id)
            prior_fingerprint = by_fingerprint.get(candidate.fingerprint)
            if (prior_id is not None and prior_id.to_dict() != candidate.to_dict()) or (
                prior_fingerprint is not None and prior_fingerprint.to_dict() != candidate.to_dict()
            ):
                malformed.append(candidate.fingerprint)
                continue
            if prior_id is None and prior_fingerprint is None:
                by_id[candidate.engagement_id] = candidate
                by_fingerprint[candidate.fingerprint] = candidate
                valid.append(candidate)
        except Exception:
            malformed.append(_corruption_marker("MALFORMED"))
    if malformed:
        return _corrupt(tenant, matter, matter_fp, party, subject, evaluated, tuple(malformed), len(valid))
    eligible = tuple(candidate for candidate in valid if candidate.effective_from <= evaluated)
    if not eligible:
        return _result(
            tenant=tenant,
            matter=matter,
            matter_fingerprint=matter_fp,
            party=party,
            subject=subject,
            evaluated_at=evaluated,
            normalized_count=len(valid),
            eligible_count=0,
            state=LegalClientMatterEngagementCurrentnessState.NO_ENGAGEMENT,
            reason=LegalClientMatterEngagementCurrentnessReason.NO_ENGAGEMENT,
        )
    if len(eligible) > 1:
        return _result(
            tenant=tenant,
            matter=matter,
            matter_fingerprint=matter_fp,
            party=party,
            subject=subject,
            evaluated_at=evaluated,
            normalized_count=len(valid),
            eligible_count=len(eligible),
            state=LegalClientMatterEngagementCurrentnessState.AMBIGUOUS,
            reason=LegalClientMatterEngagementCurrentnessReason.AMBIGUOUS,
            candidates=eligible,
        )
    return _result(
        tenant=tenant,
        matter=matter,
        matter_fingerprint=matter_fp,
        party=party,
        subject=subject,
        evaluated_at=evaluated,
        normalized_count=len(valid),
        eligible_count=1,
        state=LegalClientMatterEngagementCurrentnessState.CURRENT,
        reason=LegalClientMatterEngagementCurrentnessReason.CURRENT,
        decisive=next(iter(eligible)),
        candidates=eligible,
    )


def evaluate_legal_client_matter_engagement_currentness(**kwargs: Any) -> LegalClientMatterEngagementCurrentness:
    """Named evaluation alias with identical pure projection semantics."""
    return project_legal_client_matter_engagement_currentness(**kwargs)


__all__ = [
    "CURRENTNESS_FIELDS",
    "SCHEMA",
    "VERSION",
    "LegalClientMatterEngagementCurrentness",
    "LegalClientMatterEngagementCurrentnessError",
    "LegalClientMatterEngagementCurrentnessReason",
    "LegalClientMatterEngagementCurrentnessState",
    "evaluate_legal_client_matter_engagement_currentness",
    "project_legal_client_matter_engagement_currentness",
]


# ARTIFACT: legal_client_matter_engagement_currentness.py
# VERSION: v1.0.0-L9C11-P3-ENGAGEMENT-CURRENTNESS
# AUTHORITY BOUNDARY: pure immutable Engagement currentness projection only
# TENANT POSTURE: exact tenant/matter/matter-fingerprint/client/subject correlation
# FAIL-CLOSED POSTURE: malformed, cross-lineage and multiplicity evidence cannot become current
# FINANCIAL EXECUTION AUTHORITY: none; Kennel EOS exclusively
# END OF WILSY OS SOVEREIGN ARTIFACT
