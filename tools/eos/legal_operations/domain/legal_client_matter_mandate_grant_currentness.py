"""Immutable currentness evidence for one client-matter mandate grant.

TITLE: WILSY OS Legal Client Matter Mandate Grant Currentness Projection
VERSION: v1.0.0-L9B9-P1-CLIENT-MANDATE-GRANT-CURRENTNESS
AUTHORITY: Wilsy OS Core Governance / Python EOS Legal Operations
EPITOME: Bind one already-adjudicated grant-currentness result to the exact
         tenant, grant, matter evidence, evaluation instant, lifecycle
         evidence, and bounded reason that produced it. This artifact is an
         immutable projection only; it does not discover, query, or compute
         currentness and it never creates downstream legal authority.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tools/eos/legal_operations/domain/legal_client_matter_mandate_grant_currentness.py
COLLABORATION / OWNERSHIP: LegalClientMatterMandateGrant and its lifecycle
                            evidence remain formation/history authorities.
                            A future composer supplies already-correlated
                            evidence and owns repository reads and the caller
                            transaction. This module owns projection shape,
                            state invariants, serialization, and integrity.
CERTIFICATION / UPDATE DATE: 2026-09-27
CHANGELOG: v1.0.0-L9B9-P1-CLIENT-MANDATE-GRANT-CURRENTNESS establishes the
           bounded state vocabulary, exact identity/evidence binding,
           explicit aware-UTC evaluation, immutable state invariants,
           deterministic SHA3-512 integrity, and strict hydration. It adds no
           currentness composer, registry, persistence, or downstream authority.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2; ISO 27001.
SECURITY / PRIVACY POSTURE: Opaque identifiers and lowercase SHA3-512
                             fingerprints only; no raw PII, credentials,
                             tokens, payload bodies, or mutable status are
                             retained. Errors expose stable codes only.
TENANT BOUNDARY: One explicit non-global tenant is bound to one exact grant,
                 matter, party, and evidence set; no fallback or inference is
                 available.
AUTHORITY BOUNDARY: Projection evidence only. This module performs no
                    repository query, lifecycle selection, authorization,
                    acknowledgment, mandate formation, Engagement,
                    Representation, Court, delivery, or acceptance action.
FINANCIAL AUTHORITY BOUNDARY: No financial authority, payment, settlement, or
                              execution is created; Kennel EOS remains the
                              exclusive financial execution authority.
TRANSACTION BOUNDARY: Pure immutable construction, deterministic
                      serialization, and strict hydration only. No database,
                      network, clock, session, retry, commit, or abort.
FAIL-CLOSED DECLARATION: Invalid scope, timestamp, state/evidence combination,
                         schema, or fingerprint rejects without coercion.
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

from tools.eos.legal_operations.domain.legal_operations_lifecycle import (
    CaseMatterState,
)


VERSION: Final[str] = "v1.0.0-L9B9-P1-CLIENT-MANDATE-GRANT-CURRENTNESS"
SCHEMA: Final[str] = "WILSY-LEGAL-CLIENT-MATTER-MANDATE-GRANT-CURRENTNESS/V1"
_IDENTITY: Final[re.Pattern[str]] = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._:-]{0,159}$")
_HEX: Final[re.Pattern[str]] = re.compile(r"^[0-9a-f]{128}$")
_FIELDS: Final[tuple[str, ...]] = (
    "schema",
    "currentness_version",
    "currentness_id",
    "tenant_id",
    "client_grant_id",
    "client_grant_fingerprint",
    "case_matter_id",
    "matter_fingerprint",
    "client_party_id",
    "subject_identity_fingerprint",
    "evaluation_time",
    "state",
    "reason",
    "matter_state",
    "matter_state_evidence_fingerprint",
    "formation_fingerprint",
    "lifecycle_evidence_fingerprints",
    "decisive_lifecycle_evidence_fingerprints",
    "successor_client_grant_id",
    "successor_client_grant_fingerprint",
    "fingerprint",
)
CURRENTNESS_FIELDS: Final[frozenset[str]] = frozenset(_FIELDS)


class LegalClientMatterMandateGrantCurrentnessState(StrEnum):
    """Closed outcomes for one exact evaluation instant."""

    CURRENT = "CURRENT"
    FORMATION_ABSENT = "FORMATION_ABSENT"
    NOT_YET_EFFECTIVE = "NOT_YET_EFFECTIVE"
    EXPIRED = "EXPIRED"
    REVOKED = "REVOKED"
    SUPERSEDED = "SUPERSEDED"
    MATTER_CLOSED = "MATTER_CLOSED"
    AMBIGUOUS = "AMBIGUOUS"
    CORRUPT_BLOCKED = "CORRUPT_BLOCKED"


class LegalClientMatterMandateGrantCurrentnessReason(StrEnum):
    """Bounded machine-readable explanation for a projection outcome."""

    CURRENT = "CURRENT"
    FORMATION_ABSENT = "FORMATION_ABSENT"
    NOT_YET_EFFECTIVE = "NOT_YET_EFFECTIVE"
    EXPIRED = "EXPIRED"
    REVOKED = "REVOKED"
    SUPERSEDED = "SUPERSEDED"
    MATTER_CLOSED = "MATTER_CLOSED"
    AMBIGUOUS_LIFECYCLE = "AMBIGUOUS_LIFECYCLE"
    CORRUPT_EVIDENCE = "CORRUPT_EVIDENCE"


class LegalClientMatterMandateGrantCurrentnessError(ValueError):
    """Stable, non-sensitive failure from projection validation."""

    def __init__(self, code: str) -> None:
        """Expose only a bounded code and never echo authority-bearing input."""
        self.code = code
        super().__init__(code)


def _fail(code: str) -> NoReturn:
    """Raise one stable fail-closed projection error."""
    raise LegalClientMatterMandateGrantCurrentnessError(code)


def _identity(name: str, value: object) -> str:
    """Require one bounded opaque identity without trimming or coercion."""
    if not isinstance(value, str) or value != value.strip() or _IDENTITY.fullmatch(value) is None:
        _fail(f"L9B9_P1_{name.upper()}_INVALID")
    return value


def _tenant(value: object) -> str:
    """Require one explicit non-global tenant scope."""
    tenant = _identity("tenant_id", value)
    if tenant.casefold() in {"default", "global", "global_root", "root", "master", "*"}:
        _fail("L9B9_P1_TENANT_REQUIRED")
    return tenant


def _fingerprint(name: str, value: object) -> str:
    """Require one lowercase SHA3-512 hexadecimal evidence fingerprint."""
    if not isinstance(value, str) or _HEX.fullmatch(value) is None:
        _fail(f"L9B9_P1_{name.upper()}_INVALID")
    return value


def _optional_fingerprint(name: str, value: object) -> str | None:
    """Validate an optional fingerprint without inventing absent evidence."""
    if value is None:
        return None
    return _fingerprint(name, value)


def _timestamp(name: str, value: object) -> datetime:
    """Require an aware timestamp and canonicalize it to UTC microseconds."""
    parsed = value
    if isinstance(parsed, str):
        try:
            parsed = datetime.fromisoformat(parsed.replace("Z", "+00:00"))
        except ValueError as error:
            raise LegalClientMatterMandateGrantCurrentnessError(
                f"L9B9_P1_{name.upper()}_INVALID"
            ) from error
    if not isinstance(parsed, datetime) or parsed.tzinfo is None or parsed.utcoffset() is None:
        _fail(f"L9B9_P1_{name.upper()}_INVALID")
    return parsed.astimezone(timezone.utc).replace(microsecond=parsed.microsecond)


def _state(value: object) -> LegalClientMatterMandateGrantCurrentnessState:
    """Parse only the certified currentness state vocabulary."""
    try:
        return LegalClientMatterMandateGrantCurrentnessState(value)
    except (TypeError, ValueError) as error:
        raise LegalClientMatterMandateGrantCurrentnessError(
            "L9B9_P1_STATE_INVALID"
        ) from error


def _reason(value: object) -> LegalClientMatterMandateGrantCurrentnessReason:
    """Parse only the certified bounded reason vocabulary."""
    try:
        return LegalClientMatterMandateGrantCurrentnessReason(value)
    except (TypeError, ValueError) as error:
        raise LegalClientMatterMandateGrantCurrentnessError(
            "L9B9_P1_REASON_INVALID"
        ) from error


def _matter_state(value: object) -> CaseMatterState | None:
    """Parse an optional canonical CaseMatter lifecycle state."""
    if value is None:
        return None
    try:
        return CaseMatterState(value)
    except (TypeError, ValueError) as error:
        raise LegalClientMatterMandateGrantCurrentnessError(
            "L9B9_P1_MATTER_STATE_INVALID"
        ) from error


def _fingerprint_tuple(name: str, value: object) -> tuple[str, ...]:
    """Validate an immutable, ordered tuple of unique evidence fingerprints."""
    if not isinstance(value, (tuple, list)) or not value:
        _fail(f"L9B9_P1_{name.upper()}_INVALID")
    result = tuple(_fingerprint(name, item) for item in cast(tuple[Any, ...] | list[Any], value))
    if len(set(result)) != len(result):
        _fail(f"L9B9_P1_{name.upper()}_DUPLICATE")
    return result


def _json_value(value: object) -> object:
    """Convert immutable values into deterministic JSON-safe values."""
    if isinstance(value, datetime):
        return value.astimezone(timezone.utc).isoformat(timespec="microseconds").replace(
            "+00:00", "Z"
        )
    if isinstance(value, StrEnum):
        return value.value
    if isinstance(value, tuple):
        return [_json_value(item) for item in value]
    return value


def _digest(instance: "LegalClientMatterMandateGrantCurrentness") -> str:
    """Hash every semantic field except the derived fingerprint."""
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
class LegalClientMatterMandateGrantCurrentness:
    """Immutable, evidence-bound result for one grant at one instant.

    The value accepts evidence already selected by a future composer. It does
    not select lifecycle events, read CaseMatter, read a registry, consult a
    clock, or create any legal, IAM, Engagement, Representation, Court, or
    financial authority. Only ``CURRENT`` is usable; all other states remain
    explicit fail-closed outcomes.
    """

    currentness_id: str
    tenant_id: str
    client_grant_id: str
    client_grant_fingerprint: str | None
    case_matter_id: str
    matter_fingerprint: str | None
    client_party_id: str
    subject_identity_fingerprint: str | None
    evaluation_time: datetime
    state: LegalClientMatterMandateGrantCurrentnessState | str
    reason: LegalClientMatterMandateGrantCurrentnessReason | str
    matter_state: CaseMatterState | str | None
    matter_state_evidence_fingerprint: str | None
    formation_fingerprint: str | None
    lifecycle_evidence_fingerprints: tuple[str, ...]
    decisive_lifecycle_evidence_fingerprints: tuple[str, ...]
    successor_client_grant_id: str | None = None
    successor_client_grant_fingerprint: str | None = None
    schema: str = SCHEMA
    currentness_version: str = VERSION
    fingerprint: str = ""

    def __post_init__(self) -> None:
        """Validate exact schema, state evidence invariants, and integrity."""
        if self.schema != SCHEMA or self.currentness_version != VERSION:
            _fail("L9B9_P1_IDENTITY_INVALID")
        currentness_id = _identity("currentness_id", self.currentness_id)
        tenant_id = _tenant(self.tenant_id)
        grant_id = _identity("client_grant_id", self.client_grant_id)
        matter_id = _identity("case_matter_id", self.case_matter_id)
        party_id = _identity("client_party_id", self.client_party_id)
        evaluation = _timestamp("evaluation_time", self.evaluation_time)
        state = _state(self.state)
        reason = _reason(self.reason)
        matter_state = _matter_state(self.matter_state)
        grant_fp = _optional_fingerprint("client_grant_fingerprint", self.client_grant_fingerprint)
        matter_fp = _optional_fingerprint("matter_fingerprint", self.matter_fingerprint)
        subject_fp = _optional_fingerprint("subject_identity_fingerprint", self.subject_identity_fingerprint)
        matter_evidence_fp = _optional_fingerprint(
            "matter_state_evidence_fingerprint", self.matter_state_evidence_fingerprint
        )
        formation_fp = _optional_fingerprint("formation_fingerprint", self.formation_fingerprint)
        lifecycle = _fingerprint_tuple(
            "lifecycle_evidence_fingerprints", self.lifecycle_evidence_fingerprints
        ) if self.lifecycle_evidence_fingerprints else ()
        decisive = _fingerprint_tuple(
            "decisive_lifecycle_evidence_fingerprints",
            self.decisive_lifecycle_evidence_fingerprints,
        ) if self.decisive_lifecycle_evidence_fingerprints else ()
        successor_id = None if self.successor_client_grant_id is None else _identity(
            "successor_client_grant_id", self.successor_client_grant_id
        )
        successor_fp = _optional_fingerprint(
            "successor_client_grant_fingerprint", self.successor_client_grant_fingerprint
        )
        if (successor_id is None) != (successor_fp is None):
            _fail("L9B9_P1_SUCCESSOR_PAIR_REQUIRED")

        formation_absent = state is LegalClientMatterMandateGrantCurrentnessState.FORMATION_ABSENT
        corrupt = state is LegalClientMatterMandateGrantCurrentnessState.CORRUPT_BLOCKED
        if formation_absent:
            if any(value is not None for value in (grant_fp, matter_fp, subject_fp, formation_fp)):
                _fail("L9B9_P1_FORMATION_ABSENT_EVIDENCE_FORBIDDEN")
            if lifecycle or decisive or successor_id is not None:
                _fail("L9B9_P1_FORMATION_ABSENT_LIFECYCLE_FORBIDDEN")
        elif not corrupt:
            if any(value is None for value in (grant_fp, matter_fp, subject_fp, formation_fp)):
                _fail("L9B9_P1_FORMATION_EVIDENCE_REQUIRED")
            assert grant_fp is not None and formation_fp is not None
            if grant_fp != formation_fp:
                _fail("L9B9_P1_FORMATION_FINGERPRINT_MISMATCH")
            if matter_state is None or matter_evidence_fp is None:
                _fail("L9B9_P1_MATTER_EVIDENCE_REQUIRED")

        if state is LegalClientMatterMandateGrantCurrentnessState.CURRENT:
            if reason is not LegalClientMatterMandateGrantCurrentnessReason.CURRENT:
                _fail("L9B9_P1_REASON_STATE_MISMATCH")
            if matter_state is not CaseMatterState.OPEN or decisive:
                _fail("L9B9_P1_CURRENT_EVIDENCE_INVALID")
        elif state is LegalClientMatterMandateGrantCurrentnessState.FORMATION_ABSENT:
            if reason is not LegalClientMatterMandateGrantCurrentnessReason.FORMATION_ABSENT:
                _fail("L9B9_P1_REASON_STATE_MISMATCH")
        elif state is LegalClientMatterMandateGrantCurrentnessState.MATTER_CLOSED:
            if matter_state is not CaseMatterState.CLOSED or reason is not LegalClientMatterMandateGrantCurrentnessReason.MATTER_CLOSED:
                _fail("L9B9_P1_MATTER_CLOSED_EVIDENCE_INVALID")
        elif state is LegalClientMatterMandateGrantCurrentnessState.REVOKED:
            if not decisive or reason is not LegalClientMatterMandateGrantCurrentnessReason.REVOKED:
                _fail("L9B9_P1_REVOCATION_EVIDENCE_REQUIRED")
            if any(fp not in lifecycle for fp in decisive):
                _fail("L9B9_P1_DECISIVE_EVIDENCE_NOT_BOUND")
            if successor_id is not None:
                _fail("L9B9_P1_REVOKED_SUCCESSOR_FORBIDDEN")
        elif state is LegalClientMatterMandateGrantCurrentnessState.SUPERSEDED:
            if not decisive or successor_id is None or reason is not LegalClientMatterMandateGrantCurrentnessReason.SUPERSEDED:
                _fail("L9B9_P1_SUPERSESSION_EVIDENCE_REQUIRED")
            if any(fp not in lifecycle for fp in decisive):
                _fail("L9B9_P1_DECISIVE_EVIDENCE_NOT_BOUND")
        elif state is LegalClientMatterMandateGrantCurrentnessState.AMBIGUOUS:
            if len(decisive) < 2 or reason is not LegalClientMatterMandateGrantCurrentnessReason.AMBIGUOUS_LIFECYCLE:
                _fail("L9B9_P1_AMBIGUITY_EVIDENCE_REQUIRED")
            if any(fp not in lifecycle for fp in decisive):
                _fail("L9B9_P1_DECISIVE_EVIDENCE_NOT_BOUND")
            if successor_id is not None:
                _fail("L9B9_P1_AMBIGUOUS_SUCCESSOR_FORBIDDEN")
        elif corrupt:
            if reason is not LegalClientMatterMandateGrantCurrentnessReason.CORRUPT_EVIDENCE:
                _fail("L9B9_P1_REASON_STATE_MISMATCH")
            if grant_fp is not None or formation_fp is not None or decisive:
                _fail("L9B9_P1_CORRUPT_TRUSTED_EVIDENCE_FORBIDDEN")
        elif reason.value != state.value:
            _fail("L9B9_P1_REASON_STATE_MISMATCH")

        object.__setattr__(self, "currentness_id", currentness_id)
        object.__setattr__(self, "tenant_id", tenant_id)
        object.__setattr__(self, "client_grant_id", grant_id)
        object.__setattr__(self, "client_grant_fingerprint", grant_fp)
        object.__setattr__(self, "case_matter_id", matter_id)
        object.__setattr__(self, "matter_fingerprint", matter_fp)
        object.__setattr__(self, "client_party_id", party_id)
        object.__setattr__(self, "subject_identity_fingerprint", subject_fp)
        object.__setattr__(self, "evaluation_time", evaluation)
        object.__setattr__(self, "state", state)
        object.__setattr__(self, "reason", reason)
        object.__setattr__(self, "matter_state", matter_state)
        object.__setattr__(self, "matter_state_evidence_fingerprint", matter_evidence_fp)
        object.__setattr__(self, "formation_fingerprint", formation_fp)
        object.__setattr__(self, "lifecycle_evidence_fingerprints", lifecycle)
        object.__setattr__(self, "decisive_lifecycle_evidence_fingerprints", decisive)
        object.__setattr__(self, "successor_client_grant_id", successor_id)
        object.__setattr__(self, "successor_client_grant_fingerprint", successor_fp)
        digest = _digest(self)
        if self.fingerprint and (
            not isinstance(self.fingerprint, str) or not hmac.compare_digest(self.fingerprint, digest)
        ):
            _fail("L9B9_P1_FINGERPRINT_MISMATCH")
        object.__setattr__(self, "fingerprint", digest)

    @property
    def is_current(self) -> bool:
        """Return whether this exact evidence projection is usable."""
        return self.state is LegalClientMatterMandateGrantCurrentnessState.CURRENT

    @property
    def is_usable(self) -> bool:
        """Return the same narrow usability predicate as ``is_current``."""
        return self.is_current

    @property
    def reason_code(self) -> LegalClientMatterMandateGrantCurrentnessReason:
        """Expose the bounded machine-readable reason without free prose."""
        return cast(LegalClientMatterMandateGrantCurrentnessReason, self.reason)

    def to_dict(self) -> dict[str, object]:
        """Serialize the complete immutable projection evidence."""
        return {field: _json_value(getattr(self, field)) for field in _FIELDS}

    @classmethod
    def from_dict(
        cls, payload: Mapping[str, object]
    ) -> "LegalClientMatterMandateGrantCurrentness":
        """Hydrate exact schema fields and verify the supplied fingerprint."""
        if not isinstance(payload, Mapping) or set(payload) != set(_FIELDS):
            _fail("L9B9_P1_SCHEMA_INVALID")
        values = dict(payload)
        stored = values.pop("fingerprint")
        result = cls(**cast(dict[str, Any], values))
        if not isinstance(stored, str) or not hmac.compare_digest(stored, result.fingerprint):
            _fail("L9B9_P1_FINGERPRINT_MISMATCH")
        return result


def project_legal_client_matter_mandate_grant_currentness(
    **values: object,
) -> LegalClientMatterMandateGrantCurrentness:
    """Construct one state-safe projection from already-correlated evidence.

    This convenience boundary performs no lifecycle selection, repository
    access, CaseMatter query, clock read, authorization, or transaction work.
    Callers remain responsible for proving that every supplied fingerprint and
    state is the result of their separately governed composition step.
    """
    return LegalClientMatterMandateGrantCurrentness(**cast(dict[str, Any], values))


__all__ = [
    "CURRENTNESS_FIELDS",
    "SCHEMA",
    "VERSION",
    "LegalClientMatterMandateGrantCurrentness",
    "LegalClientMatterMandateGrantCurrentnessError",
    "LegalClientMatterMandateGrantCurrentnessReason",
    "LegalClientMatterMandateGrantCurrentnessState",
    "project_legal_client_matter_mandate_grant_currentness",
]


# ARTIFACT: legal_client_matter_mandate_grant_currentness.py
# VERSION: v1.0.0-L9B9-P1-CLIENT-MANDATE-GRANT-CURRENTNESS
# AUTHORITY BOUNDARY: immutable currentness projection evidence only
# TENANT POSTURE: exact tenant/grant/matter/party binding; no fallback
# FAIL-CLOSED POSTURE: strict schema, evidence, state, timestamp, and fingerprint validation
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively
# END OF WILSY OS SOVEREIGN ARTIFACT
