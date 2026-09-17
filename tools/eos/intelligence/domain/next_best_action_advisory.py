"""WILSY OS C1D immutable next-best-action advisory contract.

TITLE: Evidence-backed Next-Best-Action Advisory
VERSION: v1.0.0-C1D-R1
AUTHORITY: Wilsy OS Core Governance; Python EOS advisory evidence boundary
EPITOME: Binds an existing evidence-backed Recommendation and ExplainableDecision
         to a tenant-scoped, replayable source snapshot without granting authority.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tools/eos/intelligence/domain/next_best_action_advisory.py
COLLABORATION / OWNERSHIP: C1D advisory domain; C1C and Legal Operations remain
                            owners of orchestration, legal truth, and persistence facts.
CERTIFICATION / UPDATE DATE: 2026-09-17
CHANGELOG: v1.0.0-C1D-R1 establishes strict source references, deterministic
           identities, immutable supersession lineage, and advisory-only semantics.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2.
SECURITY / PRIVACY POSTURE: IDs and fingerprints only; no prompts, model output,
                             chain-of-thought, secrets, or raw legal projection data.
TENANT BOUNDARY: tenant_id and scope_ref are mandatory and never inferred.
AUTHORITY BOUNDARY: Advisory evidence only; no IAM, legal mutation, approval,
                    execution, payment, or settlement authority.
FINANCIAL AUTHORITY BOUNDARY: Kennel EOS exclusively owns financial execution.
"""
from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from datetime import datetime, timezone
import hashlib
import json
import re
from typing import Any, Final, cast

from tools.eos.intelligence.domain.observation import ExplainableDecision, Recommendation

VERSION: Final[str] = "v1.0.0-C1D-R1"
LEGAL_SOURCE_CATEGORIES: Final[tuple[str, ...]] = (
    "ORCHESTRATION_ROOT", "LEGAL_TOOL_INVOCATION", "LEGAL_TOOL_RESULT",
    "ENTITLEMENT", "CAPACITY",
)
_ID = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._:-]{0,127}$")
_HEX = re.compile(r"^[0-9a-f]{128}$")
_MAX_TEXT = 512
_ENVELOPE_KEYS: Final[frozenset[str]] = frozenset({
    "tenant_id", "advisory_id", "scope_ref", "policy_id", "policy_version",
    "recommendation", "decision", "source_references", "source_snapshot_fingerprint",
    "generated_at", "supersedes_advisory_id", "fingerprint",
})
_SOURCE_KEYS: Final[frozenset[str]] = frozenset({
    "evidence_type", "evidence_identity", "evidence_fingerprint",
    "producer_identity", "producer_version",
})


class NextBestActionAdvisoryError(ValueError):
    """Stable fail-closed C1D contract error with a non-sensitive code."""

    def __init__(self, code: str) -> None:
        self.code = code
        super().__init__(code)


def _text(value: object, code: str, *, limit: int = _MAX_TEXT) -> str:
    if not isinstance(value, str) or not value or value != value.strip() or len(value) > limit:
        raise NextBestActionAdvisoryError(code)
    return value


def _identity(value: object, code: str) -> str:
    if not isinstance(value, str) or _ID.fullmatch(value) is None:
        raise NextBestActionAdvisoryError(code)
    return value


def _fingerprint(value: object, code: str) -> str:
    if not isinstance(value, str) or _HEX.fullmatch(value) is None:
        raise NextBestActionAdvisoryError(code)
    return value


def _timestamp(value: object, code: str) -> str:
    if not isinstance(value, str) or not value or value != value.strip():
        raise NextBestActionAdvisoryError(code)
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError as error:
        raise NextBestActionAdvisoryError(code) from error
    if parsed.tzinfo is None or parsed.utcoffset() is None:
        raise NextBestActionAdvisoryError(code)
    return parsed.astimezone(timezone.utc).isoformat().replace("+00:00", "Z")


def _canonical(value: object) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def _digest(value: object) -> str:
    return hashlib.sha3_512(_canonical(value).encode("utf-8")).hexdigest()


@dataclass(frozen=True, slots=True)
class AdvisorySourceReference:
    """Immutable evidence identity; it contains no evidence payload or PII."""

    evidence_type: str
    evidence_identity: str
    evidence_fingerprint: str
    producer_identity: str
    producer_version: str

    def __post_init__(self) -> None:
        _identity(self.evidence_type, "C1D_SOURCE_TYPE_INVALID")
        _identity(self.evidence_identity, "C1D_SOURCE_IDENTITY_INVALID")
        _fingerprint(self.evidence_fingerprint, "C1D_SOURCE_FINGERPRINT_INVALID")
        _identity(self.producer_identity, "C1D_SOURCE_PRODUCER_INVALID")
        _identity(self.producer_version, "C1D_SOURCE_VERSION_INVALID")

    def to_dict(self) -> dict[str, str]:
        """Return the exact bounded source-reference projection."""
        return {
            "evidence_type": self.evidence_type,
            "evidence_identity": self.evidence_identity,
            "evidence_fingerprint": self.evidence_fingerprint,
            "producer_identity": self.producer_identity,
            "producer_version": self.producer_version,
        }

    @classmethod
    def from_dict(cls, payload: Mapping[str, object]) -> "AdvisorySourceReference":
        """Hydrate one strict source reference and reject unknown keys."""
        if not isinstance(payload, Mapping) or set(payload) != _SOURCE_KEYS:
            raise NextBestActionAdvisoryError("C1D_SOURCE_SCHEMA_INVALID")
        try:
            return cls(**{key: payload[key] for key in _SOURCE_KEYS})  # type: ignore[arg-type]
        except (TypeError, NextBestActionAdvisoryError) as error:
            if isinstance(error, NextBestActionAdvisoryError):
                raise
            raise NextBestActionAdvisoryError("C1D_SOURCE_SCHEMA_INVALID") from error


def _ordered_sources(sources: tuple[AdvisorySourceReference, ...]) -> tuple[AdvisorySourceReference, ...]:
    return tuple(sorted(sources, key=lambda item: (
        item.evidence_type, item.evidence_identity, item.evidence_fingerprint,
        item.producer_identity, item.producer_version,
    )))


def source_snapshot_fingerprint(sources: tuple[AdvisorySourceReference, ...]) -> str:
    """Compute the deterministic SHA3-512 identity of a source-reference set."""
    if not isinstance(sources, tuple) or not sources:
        raise NextBestActionAdvisoryError("C1D_SOURCES_REQUIRED")
    if any(not isinstance(item, AdvisorySourceReference) for item in sources):
        raise NextBestActionAdvisoryError("C1D_SOURCE_TYPE_INVALID")
    identities = [item.evidence_identity for item in sources]
    if len(set(identities)) != len(identities):
        raise NextBestActionAdvisoryError("C1D_SOURCE_IDENTITY_DUPLICATE")
    ordered = _ordered_sources(sources)
    return _digest([item.to_dict() for item in ordered])


def advisory_identity(*, tenant_id: str, scope_ref: str, policy_id: str,
                      policy_version: str, source_snapshot: str) -> str:
    """Derive an opaque advisory identity from tenant, policy, and source snapshot."""
    values = {
        "tenant_id": _identity(tenant_id, "C1D_TENANT_INVALID"),
        "scope_ref": _identity(scope_ref, "C1D_SCOPE_INVALID"),
        "policy_id": _identity(policy_id, "C1D_POLICY_INVALID"),
        "policy_version": _identity(policy_version, "C1D_POLICY_VERSION_INVALID"),
        "source_snapshot": _fingerprint(source_snapshot, "C1D_SNAPSHOT_INVALID"),
    }
    return "c1d-advisory-" + _digest(values)[:48]


def _child_identity(prefix: str, advisory_id: str) -> str:
    return prefix + _digest({"advisory_id": advisory_id})[:48]


def advisory_fingerprint(advisory: "NextBestActionAdvisory", *, include_fingerprint: bool = False) -> str:
    """Compute the immutable envelope fingerprint, excluding only its own field."""
    payload = advisory.to_dict()
    if not include_fingerprint:
        payload.pop("fingerprint", None)
    return _digest(payload)


def _recommendation_from_dict(payload: object) -> Recommendation:
    if not isinstance(payload, Mapping):
        raise NextBestActionAdvisoryError("C1D_RECOMMENDATION_SCHEMA_INVALID")
    required = {"recommendation_id", "scope_ref", "action_title", "target_subsystem", "rationale", "confidence_score", "confidence_basis", "risk_level", "evidence_chain", "created_at", "checksum"}
    if set(payload) != required or not isinstance(payload["evidence_chain"], list):
        raise NextBestActionAdvisoryError("C1D_RECOMMENDATION_SCHEMA_INVALID")
    values = dict(payload)
    stored = values.pop("checksum")
    try:
        item = Recommendation(**values)  # type: ignore[arg-type]
    except (TypeError, ValueError) as error:
        raise NextBestActionAdvisoryError("C1D_RECOMMENDATION_CORRUPT") from error
    if stored != item.checksum:
        raise NextBestActionAdvisoryError("C1D_RECOMMENDATION_FINGERPRINT_MISMATCH")
    return item


def _decision_from_dict(payload: object) -> ExplainableDecision:
    if not isinstance(payload, Mapping):
        raise NextBestActionAdvisoryError("C1D_DECISION_SCHEMA_INVALID")
    required = {"decision_id", "scope_ref", "title", "rationale", "evidence_ids", "recommendation_ids", "confidence_score", "confidence_basis", "disposition", "created_at", "traceability_checksum"}
    if set(payload) != required or not isinstance(payload["evidence_ids"], list) or not isinstance(payload["recommendation_ids"], list):
        raise NextBestActionAdvisoryError("C1D_DECISION_SCHEMA_INVALID")
    values = dict(payload)
    stored = values.pop("traceability_checksum")
    try:
        item = ExplainableDecision(**values)  # type: ignore[arg-type]
    except (TypeError, ValueError) as error:
        raise NextBestActionAdvisoryError("C1D_DECISION_CORRUPT") from error
    if stored != item.traceability_checksum:
        raise NextBestActionAdvisoryError("C1D_DECISION_FINGERPRINT_MISMATCH")
    return item


@dataclass(frozen=True, slots=True)
class NextBestActionAdvisory:
    """Immutable tenant-scoped advisory envelope with no execution authority."""

    tenant_id: str
    advisory_id: str
    scope_ref: str
    policy_id: str
    policy_version: str
    recommendation: Recommendation
    decision: ExplainableDecision
    source_references: tuple[AdvisorySourceReference, ...]
    source_snapshot_fingerprint: str
    generated_at: str
    supersedes_advisory_id: str | None
    fingerprint: str

    def __post_init__(self) -> None:
        _identity(self.tenant_id, "C1D_TENANT_INVALID")
        _identity(self.advisory_id, "C1D_ADVISORY_ID_INVALID")
        _identity(self.scope_ref, "C1D_SCOPE_INVALID")
        _identity(self.policy_id, "C1D_POLICY_INVALID")
        _identity(self.policy_version, "C1D_POLICY_VERSION_INVALID")
        if not isinstance(self.recommendation, Recommendation) or not isinstance(self.decision, ExplainableDecision):
            raise NextBestActionAdvisoryError("C1D_NESTED_CONTRACT_INVALID")
        if not isinstance(self.source_references, tuple) or not self.source_references:
            raise NextBestActionAdvisoryError("C1D_SOURCES_REQUIRED")
        if any(not isinstance(item, AdvisorySourceReference) for item in self.source_references):
            raise NextBestActionAdvisoryError("C1D_SOURCE_TYPE_INVALID")
        if self.source_references != _ordered_sources(self.source_references):
            raise NextBestActionAdvisoryError("C1D_SOURCE_ORDER_INVALID")
        snapshot = source_snapshot_fingerprint(self.source_references)
        if snapshot != self.source_snapshot_fingerprint:
            raise NextBestActionAdvisoryError("C1D_SOURCE_SNAPSHOT_MISMATCH")
        generated = _timestamp(self.generated_at, "C1D_GENERATED_AT_INVALID")
        object.__setattr__(self, "generated_at", generated)
        if self.supersedes_advisory_id is not None:
            _identity(self.supersedes_advisory_id, "C1D_SUPERSEDER_INVALID")
            if self.supersedes_advisory_id == self.advisory_id:
                raise NextBestActionAdvisoryError("C1D_SELF_SUPERSESSION")
        expected_id = advisory_identity(tenant_id=self.tenant_id, scope_ref=self.scope_ref, policy_id=self.policy_id, policy_version=self.policy_version, source_snapshot=snapshot)
        if self.advisory_id != expected_id:
            raise NextBestActionAdvisoryError("C1D_ADVISORY_ID_MISMATCH")
        expected_chain = tuple(item.evidence_identity for item in self.source_references)
        if self.recommendation.scope_ref != self.scope_ref or self.recommendation.evidence_chain != expected_chain:
            raise NextBestActionAdvisoryError("C1D_RECOMMENDATION_TRACEABILITY_MISMATCH")
        if self.decision.scope_ref != self.scope_ref or self.decision.recommendation_ids != (self.recommendation.recommendation_id,) or self.decision.evidence_ids != expected_chain:
            raise NextBestActionAdvisoryError("C1D_DECISION_TRACEABILITY_MISMATCH")
        if self.decision.disposition != "PROPOSED":
            raise NextBestActionAdvisoryError("C1D_DECISION_DISPOSITION_INVALID")
        _fingerprint(self.fingerprint, "C1D_ADVISORY_FINGERPRINT_INVALID")
        if self.fingerprint != advisory_fingerprint(self):
            raise NextBestActionAdvisoryError("C1D_ADVISORY_FINGERPRINT_MISMATCH")

    def to_dict(self) -> dict[str, object]:
        """Return the strict durable envelope projection."""
        return {
            "tenant_id": self.tenant_id,
            "advisory_id": self.advisory_id,
            "scope_ref": self.scope_ref,
            "policy_id": self.policy_id,
            "policy_version": self.policy_version,
            "recommendation": self.recommendation.to_dict(),
            "decision": self.decision.to_dict(),
            "source_references": [item.to_dict() for item in self.source_references],
            "source_snapshot_fingerprint": self.source_snapshot_fingerprint,
            "generated_at": self.generated_at,
            "supersedes_advisory_id": self.supersedes_advisory_id,
            "fingerprint": self.fingerprint,
        }

    @classmethod
    def from_dict(cls, payload: Mapping[str, object]) -> "NextBestActionAdvisory":
        """Hydrate and cryptographically revalidate a strict durable envelope."""
        if not isinstance(payload, Mapping) or set(payload) != _ENVELOPE_KEYS:
            raise NextBestActionAdvisoryError("C1D_ENVELOPE_SCHEMA_INVALID")
        references = payload["source_references"]
        if not isinstance(references, list):
            raise NextBestActionAdvisoryError("C1D_SOURCE_SCHEMA_INVALID")
        try:
            return cls(
                tenant_id=cast(str, payload["tenant_id"]), advisory_id=cast(str, payload["advisory_id"]), scope_ref=cast(str, payload["scope_ref"]),
                policy_id=cast(str, payload["policy_id"]), policy_version=cast(str, payload["policy_version"]),
                recommendation=_recommendation_from_dict(payload["recommendation"]),
                decision=_decision_from_dict(payload["decision"]),
                source_references=tuple(AdvisorySourceReference.from_dict(item) for item in references),
                source_snapshot_fingerprint=cast(str, payload["source_snapshot_fingerprint"]), generated_at=cast(str, payload["generated_at"]),
                supersedes_advisory_id=cast(str | None, payload["supersedes_advisory_id"]), fingerprint=cast(str, payload["fingerprint"]),
            )  # type: ignore[arg-type]
        except NextBestActionAdvisoryError:
            raise
        except (TypeError, ValueError) as error:
            raise NextBestActionAdvisoryError("C1D_ENVELOPE_CORRUPT") from error


def build_advisory(*, tenant_id: str, scope_ref: str, policy_id: str, policy_version: str,
                   source_references: tuple[AdvisorySourceReference, ...], action_title: str,
                   target_subsystem: str, rationale: str, risk_level: str,
                   generated_at: str, supersedes_advisory_id: str | None = None) -> NextBestActionAdvisory:
    """Build one deterministic PROPOSED advisory from validated source identities."""
    ordered = _ordered_sources(source_references)
    snapshot = source_snapshot_fingerprint(ordered)
    identifier = advisory_identity(tenant_id=tenant_id, scope_ref=scope_ref, policy_id=policy_id, policy_version=policy_version, source_snapshot=snapshot)
    chain = tuple(item.evidence_identity for item in ordered)
    completeness = len({item.evidence_type for item in ordered if item.evidence_type in LEGAL_SOURCE_CATEGORIES}) / len(LEGAL_SOURCE_CATEGORIES)
    basis = "Deterministic evidence-completeness ratio only; not legal correctness, model certainty, execution authorization, or outcome probability."
    stamp = _timestamp(generated_at, "C1D_GENERATED_AT_INVALID")
    recommendation = Recommendation(_child_identity("c1d-rec-", identifier), scope_ref, _text(action_title, "C1D_ACTION_INVALID"), _text(target_subsystem, "C1D_TARGET_INVALID"), _text(rationale, "C1D_RATIONALE_INVALID", limit=8192), completeness, basis, _text(risk_level, "C1D_RISK_INVALID"), chain, stamp)
    decision = ExplainableDecision(_child_identity("c1d-dec-", identifier), scope_ref, recommendation.action_title, recommendation.rationale, chain, (recommendation.recommendation_id,), completeness, basis, "PROPOSED", stamp)
    provisional = object.__new__(NextBestActionAdvisory)
    for name, value in (
        ("tenant_id", tenant_id), ("advisory_id", identifier), ("scope_ref", scope_ref),
        ("policy_id", policy_id), ("policy_version", policy_version),
        ("recommendation", recommendation), ("decision", decision),
        ("source_references", ordered), ("source_snapshot_fingerprint", snapshot),
        ("generated_at", stamp), ("supersedes_advisory_id", supersedes_advisory_id),
        ("fingerprint", "0" * 128),
    ):
        object.__setattr__(provisional, name, value)
    return NextBestActionAdvisory(
        tenant_id, identifier, scope_ref, policy_id, policy_version,
        recommendation, decision, ordered, snapshot, stamp,
        supersedes_advisory_id, advisory_fingerprint(provisional),
    )


@dataclass(frozen=True, slots=True)
class AdvisoryStatusProjection:
    """Derived current/stale view; disposition is never persisted."""

    advisory: NextBestActionAdvisory
    disposition: str
    superseded_by_advisory_id: str | None

    def __post_init__(self) -> None:
        if self.disposition not in {"CURRENT", "STALE"}:
            raise NextBestActionAdvisoryError("C1D_STATUS_INVALID")
        if (self.disposition == "CURRENT") != (self.superseded_by_advisory_id is None):
            raise NextBestActionAdvisoryError("C1D_STATUS_LINEAGE_INVALID")


SourceEvidenceReference = AdvisorySourceReference
NextBestActionAdvisoryEnvelope = NextBestActionAdvisory
compute_source_snapshot_fingerprint = source_snapshot_fingerprint
derive_advisory_id = advisory_identity
compute_advisory_fingerprint = advisory_fingerprint


__all__ = ["VERSION", "LEGAL_SOURCE_CATEGORIES", "NextBestActionAdvisoryError", "AdvisorySourceReference", "SourceEvidenceReference", "NextBestActionAdvisory", "NextBestActionAdvisoryEnvelope", "AdvisoryStatusProjection", "source_snapshot_fingerprint", "compute_source_snapshot_fingerprint", "advisory_identity", "derive_advisory_id", "advisory_fingerprint", "compute_advisory_fingerprint", "build_advisory"]

# ARTIFACT: next_best_action_advisory.py
# VERSION: v1.0.0-C1D-R1
# AUTHORITY BOUNDARY: immutable advisory evidence only; no approval or execution grant
# TENANT POSTURE: explicit tenant and scope binding; no cross-tenant inference
# FAIL-CLOSED POSTURE: strict schema, traceability, fingerprint, and supersession inputs
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively
# END OF WILSY OS SOVEREIGN ARTIFACT
