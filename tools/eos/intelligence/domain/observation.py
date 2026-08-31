# -*- coding: utf-8 -*-
"""TITLE: WILSY OS — INTELLIGENCE DOCK OBSERVATION & EVIDENCE DOMAIN.

VERSION: 1.0.0
AUTHORITY: Wilsy OS Core Governance
EPITOME:
    Immutable, evidence-bound domain entities for observations, evidence,
    hypotheses, recommendations, and explainable decisions used by the Wilsy
    Intelligence Dock. This artifact records and packages caller-supplied truth;
    it does not manufacture telemetry, confidence, provenance, tenant authority,
    business authority, or financial execution authority.
ABSOLUTE CANONICAL PATH:
    /Users/wilsonkhanyezi/legal-doc-system/tools/eos/intelligence/domain/observation.py
COLLABORATION / OWNERSHIP:
    Wilson Khanyezi / Wilsy OS Core Engineering
CERTIFICATION / UPDATE DATE: 2026-08-31
CHANGELOG:
    1.0.0:
        Resets the domain contract to a sovereign v1 baseline; removes synthetic
        observation values, subsystem defaults, perfect confidence defaults,
        random opaque IDs, and implicit timestamps; introduces immutable entities,
        explicit caller-authorized scope references, fail-closed validation,
        evidence/provenance requirements, confidence-basis requirements, and
        deterministic SHA-256 integrity anchors.
COMPLIANCE:
    POPIA section 19; GDPR Article 32; SOC 2 CC7.2; ISO 27001-aligned integrity,
    minimization, traceability, tenant separation, and fail-closed posture.
SECURITY / PRIVACY POSTURE:
    No credentials, secrets, authentication state, or raw tenant-authority claims
    are derived here. Callers must minimize payloads and supply only already-
    authorized scope references and evidence references.
TENANT BOUNDARY:
    ``scope_ref`` is an opaque reference to scope already authorized by the caller.
    It is evidence metadata only. Possession of a scope reference never establishes
    tenant membership, identity, role, entitlement, or authorization.
AUTHORITY BOUNDARY:
    These entities are descriptive and analytical records. Observation, evidence,
    hypothesis, recommendation, confidence, and decision packaging never grant
    business mutation authority or autonomous execution authority.
FINANCIAL AUTHORITY BOUNDARY:
    Kennel EOS exclusively owns financial execution. Nothing in this artifact can
    approve, release, settle, transfer, execute, or infer financial authority.
"""

from __future__ import annotations

import hashlib
import json
import math
import re
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Dict, Tuple, Union


VERSION = "1.0.0"

JsonScalar = Union[str, int, float, bool]

_SHA256_RE = re.compile(r"^sha256:[0-9a-f]{64}$")
_RISK_LEVELS = frozenset({"LOW", "MEDIUM", "HIGH", "CRITICAL"})
_HYPOTHESIS_STATES = frozenset({"OPEN", "SUPPORTED", "REJECTED", "INCONCLUSIVE"})
_DECISION_DISPOSITIONS = frozenset({"PROPOSED", "APPROVED", "REJECTED", "DEFERRED"})


def _require_non_blank_string(value: Any, field_name: str, *, max_length: int = 4096) -> str:
    """Return a trimmed non-blank string or fail closed."""
    if not isinstance(value, str):
        raise ValueError(f"{field_name} must be a string")
    normalized = value.strip()
    if not normalized:
        raise ValueError(f"{field_name} must be non-blank")
    if len(normalized) > max_length:
        raise ValueError(f"{field_name} exceeds maximum length {max_length}")
    return normalized


def _require_identifier(value: Any, field_name: str) -> str:
    """Validate an explicit caller-supplied identifier."""
    normalized = _require_non_blank_string(value, field_name, max_length=256)
    if any(character.isspace() for character in normalized):
        raise ValueError(f"{field_name} must not contain whitespace")
    return normalized


def _require_utc_timestamp(value: Any, field_name: str) -> str:
    """Validate and normalize an explicit timezone-aware timestamp to UTC."""
    raw = _require_non_blank_string(value, field_name, max_length=128)
    candidate = raw[:-1] + "+00:00" if raw.endswith("Z") else raw
    try:
        parsed = datetime.fromisoformat(candidate)
    except ValueError as exc:
        raise ValueError(f"{field_name} must be an ISO-8601 timestamp") from exc
    if parsed.tzinfo is None or parsed.utcoffset() is None:
        raise ValueError(f"{field_name} must include timezone information")
    return parsed.astimezone(timezone.utc).isoformat()


def _require_score(value: Any, field_name: str) -> float:
    """Validate an explicit finite score in the closed interval [0.0, 1.0]."""
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ValueError(f"{field_name} must be a finite number between 0.0 and 1.0")
    score = float(value)
    if not math.isfinite(score) or not 0.0 <= score <= 1.0:
        raise ValueError(f"{field_name} must be a finite number between 0.0 and 1.0")
    return score


def _require_json_scalar(value: Any, field_name: str) -> JsonScalar:
    """Validate a deterministic scalar observation value."""
    if isinstance(value, bool):
        return value
    if isinstance(value, int):
        return value
    if isinstance(value, float):
        if not math.isfinite(value):
            raise ValueError(f"{field_name} must not be NaN or infinite")
        return value
    if isinstance(value, str):
        return _require_non_blank_string(value, field_name, max_length=16384)
    raise ValueError(f"{field_name} must be a string, integer, finite float, or boolean")


def _require_references(
    values: Any,
    field_name: str,
    *,
    allow_empty: bool = False,
) -> Tuple[str, ...]:
    """Normalize reference collections into immutable, unique tuples."""
    if isinstance(values, (str, bytes)) or not isinstance(values, (tuple, list)):
        raise ValueError(f"{field_name} must be a tuple or list of identifiers")
    normalized = tuple(_require_identifier(value, field_name) for value in values)
    if not allow_empty and not normalized:
        raise ValueError(f"{field_name} must contain at least one reference")
    if len(set(normalized)) != len(normalized):
        raise ValueError(f"{field_name} must not contain duplicate references")
    return normalized


def _require_choice(value: Any, field_name: str, allowed: frozenset[str]) -> str:
    """Validate and normalize a bounded uppercase domain value."""
    normalized = _require_non_blank_string(value, field_name, max_length=64).upper()
    if normalized not in allowed:
        choices = ", ".join(sorted(allowed))
        raise ValueError(f"{field_name} must be one of: {choices}")
    return normalized


def _canonical_checksum(payload: Dict[str, Any]) -> str:
    """Return a deterministic SHA-256 integrity anchor for a canonical payload.

    The checksum proves payload integrity only. It does not prove that referenced
    evidence exists, is authoritative, or is within the caller's authorized scope.
    """
    canonical = json.dumps(
        payload,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=True,
        allow_nan=False,
    )
    digest = hashlib.sha256(canonical.encode("utf-8")).hexdigest()
    return f"sha256:{digest}"


def _validate_checksum(value: str, field_name: str) -> str:
    """Internal invariant check for generated SHA-256 anchors."""
    if not _SHA256_RE.fullmatch(value):
        raise ValueError(f"{field_name} must use sha256:<64 lowercase hexadecimal characters>")
    return value


@dataclass(frozen=True, slots=True)
class Observation:
    """Immutable observation of caller-supplied, already-authorized telemetry.

    ``checksum`` is an integrity anchor over the observation payload. It is not
    proof that the source subsystem is trustworthy or that the caller is authorized.
    """

    observation_id: str
    scope_ref: str
    source_subsystem: str
    metric_key: str
    raw_value: JsonScalar
    timestamp: str
    checksum: str = field(init=False)

    def __post_init__(self) -> None:
        object.__setattr__(self, "observation_id", _require_identifier(self.observation_id, "observation_id"))
        object.__setattr__(self, "scope_ref", _require_identifier(self.scope_ref, "scope_ref"))
        object.__setattr__(
            self,
            "source_subsystem",
            _require_non_blank_string(self.source_subsystem, "source_subsystem", max_length=256),
        )
        object.__setattr__(
            self,
            "metric_key",
            _require_non_blank_string(self.metric_key, "metric_key", max_length=256),
        )
        object.__setattr__(self, "raw_value", _require_json_scalar(self.raw_value, "raw_value"))
        object.__setattr__(self, "timestamp", _require_utc_timestamp(self.timestamp, "timestamp"))

        checksum = _canonical_checksum(
            {
                "observation_id": self.observation_id,
                "scope_ref": self.scope_ref,
                "source_subsystem": self.source_subsystem,
                "metric_key": self.metric_key,
                "raw_value": self.raw_value,
                "timestamp": self.timestamp,
            }
        )
        object.__setattr__(self, "checksum", _validate_checksum(checksum, "checksum"))

    def to_dict(self) -> Dict[str, Any]:
        """Return a serialization-safe immutable observation projection."""
        return {
            "observation_id": self.observation_id,
            "scope_ref": self.scope_ref,
            "source_subsystem": self.source_subsystem,
            "metric_key": self.metric_key,
            "raw_value": self.raw_value,
            "timestamp": self.timestamp,
            "checksum": self.checksum,
        }


@dataclass(frozen=True, slots=True)
class Evidence:
    """Immutable evidence package referencing observed or externally resolved evidence.

    At least one observation or external source reference is mandatory. This class
    never invents evidence identifiers and never converts missing evidence into an
    apparently valid chain.
    """

    evidence_id: str
    scope_ref: str
    source_type: str
    summary: str
    observations: Tuple[str, ...]
    source_refs: Tuple[str, ...]
    created_at: str
    checksum: str = field(init=False)

    def __post_init__(self) -> None:
        object.__setattr__(self, "evidence_id", _require_identifier(self.evidence_id, "evidence_id"))
        object.__setattr__(self, "scope_ref", _require_identifier(self.scope_ref, "scope_ref"))
        object.__setattr__(
            self,
            "source_type",
            _require_non_blank_string(self.source_type, "source_type", max_length=128),
        )
        object.__setattr__(self, "summary", _require_non_blank_string(self.summary, "summary", max_length=8192))
        object.__setattr__(
            self,
            "observations",
            _require_references(self.observations, "observations", allow_empty=True),
        )
        object.__setattr__(
            self,
            "source_refs",
            _require_references(self.source_refs, "source_refs", allow_empty=True),
        )
        if not self.observations and not self.source_refs:
            raise ValueError("evidence requires at least one observation or source reference")
        object.__setattr__(self, "created_at", _require_utc_timestamp(self.created_at, "created_at"))

        checksum = _canonical_checksum(
            {
                "evidence_id": self.evidence_id,
                "scope_ref": self.scope_ref,
                "source_type": self.source_type,
                "summary": self.summary,
                "observations": self.observations,
                "source_refs": self.source_refs,
                "created_at": self.created_at,
            }
        )
        object.__setattr__(self, "checksum", _validate_checksum(checksum, "checksum"))

    def to_dict(self) -> Dict[str, Any]:
        """Return a serialization-safe evidence projection."""
        return {
            "evidence_id": self.evidence_id,
            "scope_ref": self.scope_ref,
            "source_type": self.source_type,
            "summary": self.summary,
            "observations": list(self.observations),
            "source_refs": list(self.source_refs),
            "created_at": self.created_at,
            "checksum": self.checksum,
        }


@dataclass(frozen=True, slots=True)
class Hypothesis:
    """Evidence-linked analytical hypothesis with explicit confidence basis.

    Confidence is caller-supplied analytical metadata. It is not authorization,
    execution certainty, or a substitute for evidence validation.
    """

    hypothesis_id: str
    scope_ref: str
    statement: str
    evidence_ids: Tuple[str, ...]
    confidence_score: float
    confidence_basis: str
    state: str
    created_at: str
    checksum: str = field(init=False)

    def __post_init__(self) -> None:
        object.__setattr__(self, "hypothesis_id", _require_identifier(self.hypothesis_id, "hypothesis_id"))
        object.__setattr__(self, "scope_ref", _require_identifier(self.scope_ref, "scope_ref"))
        object.__setattr__(
            self,
            "statement",
            _require_non_blank_string(self.statement, "statement", max_length=8192),
        )
        object.__setattr__(
            self,
            "evidence_ids",
            _require_references(self.evidence_ids, "evidence_ids"),
        )
        object.__setattr__(
            self,
            "confidence_score",
            _require_score(self.confidence_score, "confidence_score"),
        )
        object.__setattr__(
            self,
            "confidence_basis",
            _require_non_blank_string(self.confidence_basis, "confidence_basis", max_length=4096),
        )
        object.__setattr__(
            self,
            "state",
            _require_choice(self.state, "state", _HYPOTHESIS_STATES),
        )
        object.__setattr__(self, "created_at", _require_utc_timestamp(self.created_at, "created_at"))

        checksum = _canonical_checksum(
            {
                "hypothesis_id": self.hypothesis_id,
                "scope_ref": self.scope_ref,
                "statement": self.statement,
                "evidence_ids": self.evidence_ids,
                "confidence_score": self.confidence_score,
                "confidence_basis": self.confidence_basis,
                "state": self.state,
                "created_at": self.created_at,
            }
        )
        object.__setattr__(self, "checksum", _validate_checksum(checksum, "checksum"))

    def to_dict(self) -> Dict[str, Any]:
        """Return a serialization-safe hypothesis projection."""
        return {
            "hypothesis_id": self.hypothesis_id,
            "scope_ref": self.scope_ref,
            "statement": self.statement,
            "evidence_ids": list(self.evidence_ids),
            "confidence_score": self.confidence_score,
            "confidence_basis": self.confidence_basis,
            "state": self.state,
            "created_at": self.created_at,
            "checksum": self.checksum,
        }


@dataclass(frozen=True, slots=True)
class Recommendation:
    """Evidence-backed recommendation that carries no execution authority."""

    recommendation_id: str
    scope_ref: str
    action_title: str
    target_subsystem: str
    rationale: str
    confidence_score: float
    confidence_basis: str
    risk_level: str
    evidence_chain: Tuple[str, ...]
    created_at: str
    checksum: str = field(init=False)

    def __post_init__(self) -> None:
        object.__setattr__(
            self,
            "recommendation_id",
            _require_identifier(self.recommendation_id, "recommendation_id"),
        )
        object.__setattr__(self, "scope_ref", _require_identifier(self.scope_ref, "scope_ref"))
        object.__setattr__(
            self,
            "action_title",
            _require_non_blank_string(self.action_title, "action_title", max_length=512),
        )
        object.__setattr__(
            self,
            "target_subsystem",
            _require_non_blank_string(self.target_subsystem, "target_subsystem", max_length=256),
        )
        object.__setattr__(
            self,
            "rationale",
            _require_non_blank_string(self.rationale, "rationale", max_length=8192),
        )
        object.__setattr__(
            self,
            "confidence_score",
            _require_score(self.confidence_score, "confidence_score"),
        )
        object.__setattr__(
            self,
            "confidence_basis",
            _require_non_blank_string(self.confidence_basis, "confidence_basis", max_length=4096),
        )
        object.__setattr__(
            self,
            "risk_level",
            _require_choice(self.risk_level, "risk_level", _RISK_LEVELS),
        )
        object.__setattr__(
            self,
            "evidence_chain",
            _require_references(self.evidence_chain, "evidence_chain"),
        )
        object.__setattr__(self, "created_at", _require_utc_timestamp(self.created_at, "created_at"))

        checksum = _canonical_checksum(
            {
                "recommendation_id": self.recommendation_id,
                "scope_ref": self.scope_ref,
                "action_title": self.action_title,
                "target_subsystem": self.target_subsystem,
                "rationale": self.rationale,
                "confidence_score": self.confidence_score,
                "confidence_basis": self.confidence_basis,
                "risk_level": self.risk_level,
                "evidence_chain": self.evidence_chain,
                "created_at": self.created_at,
            }
        )
        object.__setattr__(self, "checksum", _validate_checksum(checksum, "checksum"))

    def to_dict(self) -> Dict[str, Any]:
        """Return a serialization-safe recommendation projection."""
        return {
            "recommendation_id": self.recommendation_id,
            "scope_ref": self.scope_ref,
            "action_title": self.action_title,
            "target_subsystem": self.target_subsystem,
            "rationale": self.rationale,
            "confidence_score": self.confidence_score,
            "confidence_basis": self.confidence_basis,
            "risk_level": self.risk_level,
            "evidence_chain": list(self.evidence_chain),
            "created_at": self.created_at,
            "checksum": self.checksum,
        }


@dataclass(frozen=True, slots=True)
class ExplainableDecision:
    """Governed decision record linked to evidence and recommendations.

    ``disposition`` records a caller-supplied governance outcome. Even an APPROVED
    disposition does not grant execution authority; an authorized execution boundary
    must independently validate and execute any resulting action.
    """

    decision_id: str
    scope_ref: str
    title: str
    rationale: str
    evidence_ids: Tuple[str, ...]
    recommendation_ids: Tuple[str, ...]
    confidence_score: float
    confidence_basis: str
    disposition: str
    created_at: str
    traceability_checksum: str = field(init=False)

    def __post_init__(self) -> None:
        object.__setattr__(self, "decision_id", _require_identifier(self.decision_id, "decision_id"))
        object.__setattr__(self, "scope_ref", _require_identifier(self.scope_ref, "scope_ref"))
        object.__setattr__(self, "title", _require_non_blank_string(self.title, "title", max_length=512))
        object.__setattr__(
            self,
            "rationale",
            _require_non_blank_string(self.rationale, "rationale", max_length=8192),
        )
        object.__setattr__(
            self,
            "evidence_ids",
            _require_references(self.evidence_ids, "evidence_ids"),
        )
        object.__setattr__(
            self,
            "recommendation_ids",
            _require_references(self.recommendation_ids, "recommendation_ids", allow_empty=True),
        )
        object.__setattr__(
            self,
            "confidence_score",
            _require_score(self.confidence_score, "confidence_score"),
        )
        object.__setattr__(
            self,
            "confidence_basis",
            _require_non_blank_string(self.confidence_basis, "confidence_basis", max_length=4096),
        )
        object.__setattr__(
            self,
            "disposition",
            _require_choice(self.disposition, "disposition", _DECISION_DISPOSITIONS),
        )
        object.__setattr__(self, "created_at", _require_utc_timestamp(self.created_at, "created_at"))

        checksum = _canonical_checksum(
            {
                "decision_id": self.decision_id,
                "scope_ref": self.scope_ref,
                "title": self.title,
                "rationale": self.rationale,
                "evidence_ids": self.evidence_ids,
                "recommendation_ids": self.recommendation_ids,
                "confidence_score": self.confidence_score,
                "confidence_basis": self.confidence_basis,
                "disposition": self.disposition,
                "created_at": self.created_at,
            }
        )
        object.__setattr__(
            self,
            "traceability_checksum",
            _validate_checksum(checksum, "traceability_checksum"),
        )

    def to_dict(self) -> Dict[str, Any]:
        """Return a serialization-safe explainable-decision projection."""
        return {
            "decision_id": self.decision_id,
            "scope_ref": self.scope_ref,
            "title": self.title,
            "rationale": self.rationale,
            "evidence_ids": list(self.evidence_ids),
            "recommendation_ids": list(self.recommendation_ids),
            "confidence_score": self.confidence_score,
            "confidence_basis": self.confidence_basis,
            "disposition": self.disposition,
            "created_at": self.created_at,
            "traceability_checksum": self.traceability_checksum,
        }


# =============================================================================
# WILSY OS SOVEREIGN ARTIFACT SEAL
# =============================================================================
# ARTIFACT: Intelligence Dock Observation & Evidence Domain
# VERSION: 1.0.0
# AUTHORITY BOUNDARY: Descriptive/analytical domain entities only; no identity,
# tenant-membership derivation, authorization, business mutation, or execution authority.
# TENANT POSTURE: scope_ref is caller-authorized metadata only and never establishes authority.
# FAIL-CLOSED POSTURE: Missing identifiers, scope, timestamps, evidence, confidence basis,
# malformed scores, malformed references, and invalid bounded domain values are rejected.
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively.
# END OF WILSY OS SOVEREIGN ARTIFACT
