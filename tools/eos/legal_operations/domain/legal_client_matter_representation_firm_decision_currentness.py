"""Pure currentness projection for firm Representation decision history.

TITLE: WILSY OS Legal Client Matter Representation Firm Decision Currentness
VERSION: v1.0.0-L9C11-P22-FIRM-REPRESENTATION-DECISION-CURRENTNESS
AUTHORITY: Wilsy OS Core Governance / Python EOS Legal Operations
EPITOME: Derive one deterministic, fail-closed currentness result for an
         exact tenant, matter, client, P1 authority, representative and role
         at an explicit evaluation instant. This artifact is immutable
         evidence only; it never reads persistence or invents lifecycle,
         revocation, replacement, withdrawal or supersession authority.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tools/eos/legal_operations/domain/legal_client_matter_representation_firm_decision_currentness.py
COLLABORATION / OWNERSHIP: P2 owns immutable firm decisions; P9 owns bounded
                            history reads; this module owns only pure P22
                            projection. A separate composer owns one read.
CERTIFICATION / UPDATE DATE: 2026-09-28
CHANGELOG: v1.0.0-L9C11-P22 establishes explicit time evaluation, exact P1
           and representative lineage, canonical duplicate normalization,
           ambiguity without latest-wins or decision precedence, corruption
           blocking, and deterministic SHA3-512 projection integrity.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2; ISO 27001.
SECURITY / PRIVACY POSTURE: Only opaque identifiers and SHA3-512 fingerprints
                             are retained; source payloads and PII are absent.
TENANT BOUNDARY: Every decision must match the exact supplied tenant,
                 matter, client, subject, P1 authority, principal and role.
AUTHORITY BOUNDARY: Pure derived P2 currentness only. It does not authenticate
                    actors, grant IAM, form Representation or Court authority,
                    create lifecycle events, or execute finance.
FINANCIAL AUTHORITY BOUNDARY: None; Kennel EOS remains exclusive financial
                               execution and settlement authority.
TRANSACTION BOUNDARY: Immutable in-memory construction and deterministic
                      serialization only; no database, clock, network or
                      transaction behavior.
FAIL-CLOSED DECLARATION: Any malformed or cross-lineage history blocks the
                         projection; exact duplicates collapse; every distinct
                         eligible row is ambiguous because no P2 precedence,
                         supersession, revocation or expiry contract exists.
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

from tools.eos.legal_operations.domain.legal_client_matter_representation_firm_decision import (
    LegalClientMatterRepresentationFirmDecision,
    LegalClientMatterRepresentationFirmDecisionType,
)


VERSION: Final[str] = "v1.0.0-L9C11-P22-FIRM-REPRESENTATION-DECISION-CURRENTNESS"
SCHEMA: Final[str] = "WILSY-LEGAL-CLIENT-MATTER-REPRESENTATION-FIRM-DECISION-CURRENTNESS/V1"
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
    "representation_authority_id",
    "representation_authority_fingerprint",
    "representative_principal_id",
    "representative_role",
    "evaluated_at",
    "decisive_effective_from",
    "decisive_decision_id",
    "decisive_decision_fingerprint",
    "decisive_decision",
    "decisive_representation_scope_capabilities",
    "candidate_decision_ids",
    "candidate_decision_fingerprints",
    "candidate_decisions",
    "normalized_decision_count",
    "eligible_decision_count",
    "corruption_evidence_fingerprints",
    "state",
    "reason",
    "fingerprint",
)
CURRENTNESS_FIELDS: Final[frozenset[str]] = frozenset(_FIELDS)


class LegalClientMatterRepresentationFirmDecisionCurrentnessState(StrEnum):
    """Closed result vocabulary; only ACCEPTED is positive."""

    NO_DECISION = "NO_DECISION"
    ACCEPTED = "ACCEPTED"
    DECLINED = "DECLINED"
    REQUIRES_REVIEW = "REQUIRES_REVIEW"
    AMBIGUOUS = "AMBIGUOUS"
    CORRUPT_BLOCKED = "CORRUPT_BLOCKED"


class LegalClientMatterRepresentationFirmDecisionCurrentnessReason(StrEnum):
    """Stable explanation vocabulary corresponding to result states."""

    NO_DECISION = "NO_DECISION"
    ACCEPTED = "ACCEPTED"
    DECLINED = "DECLINED"
    REQUIRES_REVIEW = "REQUIRES_REVIEW"
    AMBIGUOUS = "AMBIGUOUS_DECISIONS"
    CORRUPT_EVIDENCE = "CORRUPT_EVIDENCE"


class LegalClientMatterRepresentationFirmDecisionCurrentnessError(ValueError):
    """Stable non-sensitive validation failure for pure P22 evidence."""

    def __init__(self, code: str) -> None:
        self.code = code
        super().__init__(code)


def _fail(code: str, cause: BaseException | None = None) -> NoReturn:
    error = LegalClientMatterRepresentationFirmDecisionCurrentnessError(code)
    if cause is None:
        raise error
    raise error from cause


def _identity(name: str, value: object) -> str:
    if not isinstance(value, str) or value != value.strip() or _IDENTITY.fullmatch(value) is None:
        _fail(f"L9C11_P22_{name.upper()}_INVALID")
    return cast(str, value)


def _tenant(value: object) -> str:
    tenant = _identity("tenant_id", value)
    if tenant.casefold() in _FORBIDDEN_TENANTS:
        _fail("L9C11_P22_TENANT_REQUIRED")
    return tenant


def _fingerprint(name: str, value: object) -> str:
    if not isinstance(value, str) or _HEX.fullmatch(value) is None:
        _fail(f"L9C11_P22_{name.upper()}_INVALID")
    return value


def _timestamp(name: str, value: object) -> datetime:
    parsed = value
    if isinstance(parsed, str):
        try:
            parsed = datetime.fromisoformat(parsed.replace("Z", "+00:00"))
        except ValueError as error:
            _fail(f"L9C11_P22_{name.upper()}_INVALID", error)
    if not isinstance(parsed, datetime) or parsed.tzinfo is None or parsed.utcoffset() is None:
        _fail(f"L9C11_P22_{name.upper()}_INVALID")
    return parsed.astimezone(UTC)


def _strings(name: str, value: object, *, fingerprints: bool) -> tuple[str, ...]:
    if not isinstance(value, (tuple, list)):
        _fail(f"L9C11_P22_{name.upper()}_INVALID")
    validator = _fingerprint if fingerprints else _identity
    values = tuple(validator(name, item) for item in cast(tuple[Any, ...] | list[Any], value))
    if len(values) != len(set(values)):
        _fail(f"L9C11_P22_{name.upper()}_DUPLICATE")
    return values


def _decisions(value: object) -> tuple[str, ...]:
    if not isinstance(value, (tuple, list)):
        _fail("L9C11_P22_CANDIDATE_DECISIONS_INVALID")
    result: list[str] = []
    for item in cast(tuple[Any, ...] | list[Any], value):
        try:
            result.append(LegalClientMatterRepresentationFirmDecisionType(item).value)
        except (TypeError, ValueError) as error:
            _fail("L9C11_P22_CANDIDATE_DECISION_INVALID", error)
    return tuple(result)


def _state(value: object) -> LegalClientMatterRepresentationFirmDecisionCurrentnessState:
    try:
        return LegalClientMatterRepresentationFirmDecisionCurrentnessState(value)
    except (TypeError, ValueError) as error:
        _fail("L9C11_P22_STATE_INVALID", error)


def _reason(value: object) -> LegalClientMatterRepresentationFirmDecisionCurrentnessReason:
    try:
        return LegalClientMatterRepresentationFirmDecisionCurrentnessReason(value)
    except (TypeError, ValueError) as error:
        _fail("L9C11_P22_REASON_INVALID", error)


def _json_value(value: object) -> object:
    if isinstance(value, datetime):
        return value.astimezone(UTC).isoformat(timespec="microseconds").replace("+00:00", "Z")
    if isinstance(value, StrEnum):
        return value.value
    if isinstance(value, tuple):
        return [_json_value(item) for item in value]
    return value


def _projection_id(
    tenant: str,
    matter: str,
    matter_fp: str,
    party: str,
    subject: str,
    authority_id: str,
    authority_fp: str,
    representative: str,
    role: str,
    at: datetime,
) -> str:
    payload = {
        "tenant_id": tenant,
        "case_matter_id": matter,
        "matter_fingerprint": matter_fp,
        "client_party_id": party,
        "subject_identity_fingerprint": subject,
        "representation_authority_id": authority_id,
        "representation_authority_fingerprint": authority_fp,
        "representative_principal_id": representative,
        "representative_role": role,
        "evaluated_at": _json_value(at),
    }
    digest = hashlib.sha3_512(
        json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")
    ).hexdigest()[:48]
    return f"representation-firm-decision-currentness:{digest}"


def _corruption_marker(code: str) -> str:
    return hashlib.sha3_512(f"L9C11-P22:{code}".encode("utf-8")).hexdigest()


def _digest(instance: "LegalClientMatterRepresentationFirmDecisionCurrentness") -> str:
    payload = {field: _json_value(getattr(instance, field)) for field in _FIELDS[:-1]}
    return hashlib.sha3_512(
        json.dumps(payload, ensure_ascii=False, allow_nan=False, sort_keys=False, separators=(",", ":")).encode("utf-8")
    ).hexdigest()


@dataclass(frozen=True, slots=True)
class LegalClientMatterRepresentationFirmDecisionCurrentness:
    """Immutable exact-lineage P2 currentness evidence.

    A single eligible ACCEPTED decision is the only positive result and binds
    its exact P1 authority, P2 identity, fingerprint and scope. Declined and
    review states retain candidate evidence but deliberately expose no selected
    P2. Distinct eligible history is ambiguous regardless of chronology.
    """

    currentness_id: str
    tenant_id: str
    case_matter_id: str
    matter_fingerprint: str
    client_party_id: str
    subject_identity_fingerprint: str
    representation_authority_id: str
    representation_authority_fingerprint: str
    representative_principal_id: str
    representative_role: str
    evaluated_at: datetime
    decisive_effective_from: datetime | None
    decisive_decision_id: str | None
    decisive_decision_fingerprint: str | None
    decisive_decision: str | None
    decisive_representation_scope_capabilities: tuple[str, ...]
    candidate_decision_ids: tuple[str, ...]
    candidate_decision_fingerprints: tuple[str, ...]
    candidate_decisions: tuple[str, ...]
    normalized_decision_count: int
    eligible_decision_count: int
    corruption_evidence_fingerprints: tuple[str, ...]
    state: LegalClientMatterRepresentationFirmDecisionCurrentnessState | str
    reason: LegalClientMatterRepresentationFirmDecisionCurrentnessReason | str
    schema: str = SCHEMA
    currentness_version: str = VERSION
    fingerprint: str = ""

    def __post_init__(self) -> None:
        if self.schema != SCHEMA or self.currentness_version != VERSION:
            _fail("L9C11_P22_IDENTITY_INVALID")
        currentness_id = _identity("currentness_id", self.currentness_id)
        tenant = _tenant(self.tenant_id)
        matter = _identity("case_matter_id", self.case_matter_id)
        matter_fp = _fingerprint("matter_fingerprint", self.matter_fingerprint)
        party = _identity("client_party_id", self.client_party_id)
        subject = _fingerprint("subject_identity_fingerprint", self.subject_identity_fingerprint)
        authority_id = _identity("representation_authority_id", self.representation_authority_id)
        authority_fp = _fingerprint("representation_authority_fingerprint", self.representation_authority_fingerprint)
        representative = _identity("representative_principal_id", self.representative_principal_id)
        role = _identity("representative_role", self.representative_role)
        evaluated = _timestamp("evaluated_at", self.evaluated_at)
        decisive_time = None if self.decisive_effective_from is None else _timestamp("decisive_effective_from", self.decisive_effective_from)
        decisive_id = None if self.decisive_decision_id is None else _identity("decisive_decision_id", self.decisive_decision_id)
        decisive_fp = None if self.decisive_decision_fingerprint is None else _fingerprint("decisive_decision_fingerprint", self.decisive_decision_fingerprint)
        decisive_decision = None if self.decisive_decision is None else _decisions((self.decisive_decision,))[0]
        scope = _strings("decisive_representation_scope_capabilities", self.decisive_representation_scope_capabilities, fingerprints=False)
        candidate_ids = _strings("candidate_decision_ids", self.candidate_decision_ids, fingerprints=False)
        candidate_fps = _strings("candidate_decision_fingerprints", self.candidate_decision_fingerprints, fingerprints=True)
        candidate_decisions = _decisions(self.candidate_decisions)
        corruption = _strings("corruption_evidence_fingerprints", self.corruption_evidence_fingerprints, fingerprints=True)
        state = _state(self.state)
        reason = _reason(self.reason)
        counts = (self.normalized_decision_count, self.eligible_decision_count)
        if any(isinstance(value, bool) or not isinstance(value, int) or value < 0 for value in counts):
            _fail("L9C11_P22_COUNT_INVALID")
        normalized_count, eligible_count = counts
        if eligible_count > normalized_count or len(candidate_ids) != len(candidate_fps) or len(candidate_ids) != len(candidate_decisions):
            _fail("L9C11_P22_CANDIDATE_EVIDENCE_INVALID")
        positive_fields = (decisive_time, decisive_id, decisive_fp, decisive_decision)
        if state is LegalClientMatterRepresentationFirmDecisionCurrentnessState.NO_DECISION:
            if any(value is not None for value in positive_fields) or scope or candidate_ids or candidate_fps or candidate_decisions or corruption or eligible_count != 0:
                _fail("L9C11_P22_NO_DECISION_EVIDENCE_FORBIDDEN")
            expected_reason = LegalClientMatterRepresentationFirmDecisionCurrentnessReason.NO_DECISION
        elif state is LegalClientMatterRepresentationFirmDecisionCurrentnessState.CORRUPT_BLOCKED:
            if not corruption or any(value is not None for value in positive_fields) or scope or candidate_ids or candidate_fps or candidate_decisions:
                _fail("L9C11_P22_CORRUPT_EVIDENCE_INVALID")
            expected_reason = LegalClientMatterRepresentationFirmDecisionCurrentnessReason.CORRUPT_EVIDENCE
        elif state is LegalClientMatterRepresentationFirmDecisionCurrentnessState.ACCEPTED:
            if not all(value is not None for value in positive_fields) or not scope or len(candidate_ids) != 1 or eligible_count != 1 or corruption:
                _fail("L9C11_P22_ACCEPTED_EVIDENCE_REQUIRED")
            if decisive_time is None or decisive_id is None or decisive_fp is None or decisive_decision is None:
                _fail("L9C11_P22_ACCEPTED_EVIDENCE_REQUIRED")
            if decisive_id != candidate_ids[0] or decisive_fp != candidate_fps[0] or decisive_decision != "ACCEPTED" or candidate_decisions != ("ACCEPTED",) or decisive_time > evaluated:
                _fail("L9C11_P22_ACCEPTED_EVIDENCE_MISMATCH")
            expected_reason = LegalClientMatterRepresentationFirmDecisionCurrentnessReason.ACCEPTED
        else:
            if any(value is not None for value in positive_fields) or scope or not candidate_ids or not candidate_fps or not candidate_decisions or eligible_count < 1 or corruption:
                _fail("L9C11_P22_NON_POSITIVE_EVIDENCE_INVALID")
            if state is LegalClientMatterRepresentationFirmDecisionCurrentnessState.AMBIGUOUS:
                if len(candidate_ids) < 2:
                    _fail("L9C11_P22_AMBIGUITY_EVIDENCE_REQUIRED")
                expected_reason = LegalClientMatterRepresentationFirmDecisionCurrentnessReason.AMBIGUOUS
            elif len(candidate_ids) != 1 or candidate_decisions[0] != state.value:
                _fail("L9C11_P22_STATE_EVIDENCE_MISMATCH")
            else:
                expected_reason = LegalClientMatterRepresentationFirmDecisionCurrentnessReason(state.value)
        if reason is not expected_reason:
            _fail("L9C11_P22_REASON_STATE_MISMATCH")
        for name, value in (
            ("currentness_id", currentness_id), ("tenant_id", tenant), ("case_matter_id", matter),
            ("matter_fingerprint", matter_fp), ("client_party_id", party), ("subject_identity_fingerprint", subject),
            ("representation_authority_id", authority_id), ("representation_authority_fingerprint", authority_fp),
            ("representative_principal_id", representative), ("representative_role", role), ("evaluated_at", evaluated),
            ("decisive_effective_from", decisive_time), ("decisive_decision_id", decisive_id),
            ("decisive_decision_fingerprint", decisive_fp), ("decisive_decision", decisive_decision),
            ("decisive_representation_scope_capabilities", scope), ("candidate_decision_ids", candidate_ids),
            ("candidate_decision_fingerprints", candidate_fps), ("candidate_decisions", candidate_decisions),
            ("corruption_evidence_fingerprints", corruption), ("state", state), ("reason", reason),
        ):
            object.__setattr__(self, name, value)
        digest = _digest(self)
        if self.fingerprint and (not isinstance(self.fingerprint, str) or not hmac.compare_digest(self.fingerprint, digest)):
            _fail("L9C11_P22_FINGERPRINT_MISMATCH")
        object.__setattr__(self, "fingerprint", digest)

    @property
    def is_currently_accepted(self) -> bool:
        """Return true only for one exact eligible ACCEPTED P2 decision."""
        return self.state is LegalClientMatterRepresentationFirmDecisionCurrentnessState.ACCEPTED

    @property
    def is_usable(self) -> bool:
        """Expose the same narrow positive predicate for final formation."""
        return self.is_currently_accepted

    def to_dict(self) -> dict[str, object]:
        """Serialize exact immutable projection evidence."""
        return {field: _json_value(getattr(self, field)) for field in _FIELDS}

    @classmethod
    def from_dict(cls, payload: Mapping[str, object]) -> "LegalClientMatterRepresentationFirmDecisionCurrentness":
        """Hydrate only the exact schema and verify deterministic integrity."""
        if not isinstance(payload, Mapping) or set(payload) != set(_FIELDS):
            _fail("L9C11_P22_SCHEMA_INVALID")
        values = dict(payload)
        stored = values.pop("fingerprint")
        result = cls(**cast(dict[str, Any], values))
        if not isinstance(stored, str) or not hmac.compare_digest(stored, result.fingerprint):
            _fail("L9C11_P22_FINGERPRINT_MISMATCH")
        return result


def _result(
    *, tenant: str, matter: str, matter_fp: str, party: str, subject: str,
    authority_id: str, authority_fp: str, representative: str, role: str,
    evaluated: datetime, normalized: int, eligible: tuple[LegalClientMatterRepresentationFirmDecision, ...] = (),
    state: LegalClientMatterRepresentationFirmDecisionCurrentnessState,
    reason: LegalClientMatterRepresentationFirmDecisionCurrentnessReason,
    corruption: tuple[str, ...] = (),
) -> LegalClientMatterRepresentationFirmDecisionCurrentness:
    ordered = tuple(sorted(eligible, key=lambda value: (value.fingerprint, value.decision_id)))
    accepted = state is LegalClientMatterRepresentationFirmDecisionCurrentnessState.ACCEPTED
    selected = ordered[0] if accepted and len(ordered) == 1 else None
    return LegalClientMatterRepresentationFirmDecisionCurrentness(
        currentness_id=_projection_id(tenant, matter, matter_fp, party, subject, authority_id, authority_fp, representative, role, evaluated),
        tenant_id=tenant, case_matter_id=matter, matter_fingerprint=matter_fp,
        client_party_id=party, subject_identity_fingerprint=subject,
        representation_authority_id=authority_id, representation_authority_fingerprint=authority_fp,
        representative_principal_id=representative, representative_role=role,
        evaluated_at=evaluated,
        decisive_effective_from=None if selected is None else selected.effective_from,
        decisive_decision_id=None if selected is None else selected.decision_id,
        decisive_decision_fingerprint=None if selected is None else selected.fingerprint,
        decisive_decision=None if selected is None else str(getattr(selected.decision, "value", selected.decision)),
        decisive_representation_scope_capabilities=() if selected is None else tuple(selected.representation_scope_capabilities),
        candidate_decision_ids=tuple(value.decision_id for value in ordered),
        candidate_decision_fingerprints=tuple(value.fingerprint for value in ordered),
        candidate_decisions=tuple(str(getattr(value.decision, "value", value.decision)) for value in ordered),
        normalized_decision_count=normalized, eligible_decision_count=len(ordered),
        corruption_evidence_fingerprints=tuple(sorted(set(corruption))), state=state, reason=reason,
    )


def _corrupt(*, tenant: str, matter: str, matter_fp: str, party: str, subject: str, authority_id: str, authority_fp: str, representative: str, role: str, evaluated: datetime, evidence: tuple[str, ...], normalized: int = 0) -> LegalClientMatterRepresentationFirmDecisionCurrentness:
    return _result(tenant=tenant, matter=matter, matter_fp=matter_fp, party=party, subject=subject, authority_id=authority_id, authority_fp=authority_fp, representative=representative, role=role, evaluated=evaluated, normalized=normalized, state=LegalClientMatterRepresentationFirmDecisionCurrentnessState.CORRUPT_BLOCKED, reason=LegalClientMatterRepresentationFirmDecisionCurrentnessReason.CORRUPT_EVIDENCE, corruption=evidence or (_corruption_marker("UNKNOWN"),))


def project_legal_client_matter_representation_firm_decision_currentness(
    *, tenant_id: str, case_matter_id: str, matter_fingerprint: str,
    client_party_id: str, subject_identity_fingerprint: str,
    representation_authority_id: str, representation_authority_fingerprint: str,
    representative_principal_id: str, representative_role: str,
    evaluated_at: datetime,
    decisions: Iterable[LegalClientMatterRepresentationFirmDecision],
) -> LegalClientMatterRepresentationFirmDecisionCurrentness:
    """Project one exact P9 lineage at explicit ``evaluated_at``.

    All rows are revalidated before future rows are excluded. Canonical exact
    replays collapse, while every distinct eligible truth is ambiguous. No
    latest-wins, decision precedence, revocation, supersession or expiry is
    inferred from chronological fields.
    """
    tenant = _tenant(tenant_id); matter = _identity("case_matter_id", case_matter_id)
    matter_fp = _fingerprint("matter_fingerprint", matter_fingerprint); party = _identity("client_party_id", client_party_id)
    subject = _fingerprint("subject_identity_fingerprint", subject_identity_fingerprint)
    authority_id = _identity("representation_authority_id", representation_authority_id)
    authority_fp = _fingerprint("representation_authority_fingerprint", representation_authority_fingerprint)
    representative = _identity("representative_principal_id", representative_principal_id)
    role = _identity("representative_role", representative_role); evaluated = _timestamp("evaluated_at", evaluated_at)
    try:
        history = tuple(decisions)
    except Exception:
        return _corrupt(tenant=tenant, matter=matter, matter_fp=matter_fp, party=party, subject=subject, authority_id=authority_id, authority_fp=authority_fp, representative=representative, role=role, evaluated=evaluated, evidence=(_corruption_marker("ITERABLE"),))
    malformed: list[str] = []; valid: list[LegalClientMatterRepresentationFirmDecision] = []
    by_id: dict[str, LegalClientMatterRepresentationFirmDecision] = {}; by_fp: dict[str, LegalClientMatterRepresentationFirmDecision] = {}
    for candidate in history:
        if type(candidate) is not LegalClientMatterRepresentationFirmDecision:
            malformed.append(_corruption_marker("TYPE")); continue
        try:
            candidate.__post_init__()
            if (candidate.tenant_id != tenant or candidate.case_matter_id != matter or candidate.matter_fingerprint != matter_fp or candidate.client_party_id != party or candidate.subject_identity_fingerprint != subject or candidate.representation_authority_id != authority_id or candidate.representation_authority_fingerprint != authority_fp or candidate.representative_principal_id != representative or candidate.representative_role != role):
                malformed.append(candidate.fingerprint); continue
            prior_id = by_id.get(candidate.decision_id); prior_fp = by_fp.get(candidate.fingerprint); canonical = candidate.to_dict()
            if (prior_id is not None and prior_id.to_dict() != canonical) or (prior_fp is not None and prior_fp.to_dict() != canonical):
                malformed.append(candidate.fingerprint); continue
            if prior_id is None and prior_fp is None:
                by_id[candidate.decision_id] = candidate; by_fp[candidate.fingerprint] = candidate; valid.append(candidate)
        except Exception:
            malformed.append(_corruption_marker("MALFORMED"))
    if malformed:
        return _corrupt(tenant=tenant, matter=matter, matter_fp=matter_fp, party=party, subject=subject, authority_id=authority_id, authority_fp=authority_fp, representative=representative, role=role, evaluated=evaluated, evidence=tuple(malformed), normalized=len(valid))
    eligible = tuple(value for value in valid if value.effective_from <= evaluated)
    if not eligible:
        return _result(tenant=tenant, matter=matter, matter_fp=matter_fp, party=party, subject=subject, authority_id=authority_id, authority_fp=authority_fp, representative=representative, role=role, evaluated=evaluated, normalized=len(valid), state=LegalClientMatterRepresentationFirmDecisionCurrentnessState.NO_DECISION, reason=LegalClientMatterRepresentationFirmDecisionCurrentnessReason.NO_DECISION)
    if len(eligible) > 1:
        return _result(tenant=tenant, matter=matter, matter_fp=matter_fp, party=party, subject=subject, authority_id=authority_id, authority_fp=authority_fp, representative=representative, role=role, evaluated=evaluated, normalized=len(valid), eligible=eligible, state=LegalClientMatterRepresentationFirmDecisionCurrentnessState.AMBIGUOUS, reason=LegalClientMatterRepresentationFirmDecisionCurrentnessReason.AMBIGUOUS)
    first = next(iter(eligible))
    state = LegalClientMatterRepresentationFirmDecisionCurrentnessState(str(getattr(first.decision, "value", first.decision)))
    return _result(tenant=tenant, matter=matter, matter_fp=matter_fp, party=party, subject=subject, authority_id=authority_id, authority_fp=authority_fp, representative=representative, role=role, evaluated=evaluated, normalized=len(valid), eligible=eligible, state=state, reason=LegalClientMatterRepresentationFirmDecisionCurrentnessReason(state.value))


def evaluate_legal_client_matter_representation_firm_decision_currentness(**kwargs: Any) -> LegalClientMatterRepresentationFirmDecisionCurrentness:
    """Named evaluation alias with identical pure projection semantics."""
    return project_legal_client_matter_representation_firm_decision_currentness(**kwargs)


__all__ = [
    "CURRENTNESS_FIELDS", "SCHEMA", "VERSION",
    "LegalClientMatterRepresentationFirmDecisionCurrentness",
    "LegalClientMatterRepresentationFirmDecisionCurrentnessError",
    "LegalClientMatterRepresentationFirmDecisionCurrentnessReason",
    "LegalClientMatterRepresentationFirmDecisionCurrentnessState",
    "evaluate_legal_client_matter_representation_firm_decision_currentness",
    "project_legal_client_matter_representation_firm_decision_currentness",
]


# ARTIFACT: legal_client_matter_representation_firm_decision_currentness.py
# VERSION: v1.0.0-L9C11-P22-FIRM-REPRESENTATION-DECISION-CURRENTNESS
# AUTHORITY BOUNDARY: pure immutable P2 currentness projection only
# TENANT POSTURE: exact tenant/matter/client/P1/principal/role lineage
# FAIL-CLOSED POSTURE: corruption and multiplicity never become accepted
# FINANCIAL EXECUTION AUTHORITY: none; Kennel EOS exclusively
# END OF WILSY OS SOVEREIGN ARTIFACT
