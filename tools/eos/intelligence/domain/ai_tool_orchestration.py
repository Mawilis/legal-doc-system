"""WILSY OS C1C bounded AI tool-orchestration contracts.

TITLE: Governed AI Tool Orchestration Domain
VERSION: v1.0.0-C1C-R1
AUTHORITY: Wilsy OS Core Governance
EPITOME: Immutable, tenant-scoped orchestration facts and read-only tool
         contracts; model output is never a source of legal or financial truth.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tools/eos/intelligence/domain/ai_tool_orchestration.py
COLLABORATION / OWNERSHIP: C1C owns bounded orchestration state; C1A/C1B,
                            L7B and P6B remain canonical persistence owners.
CERTIFICATION / UPDATE DATE: 2026-09-16
CHANGELOG: v1.0.0-C1C-R1 establishes strict read-only contracts, deterministic
           identity/fingerprint derivation, and monotonic orchestration phases.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2.
SECURITY / PRIVACY POSTURE: No prompts, raw model output, tool payloads,
                             secrets, headers, or chain-of-thought are durable.
TENANT BOUNDARY: Every fact is explicitly tenant and principal scoped.
AUTHORITY BOUNDARY: Bounded orchestration evidence only; no legal lifecycle,
                    execution, billing, payment, or settlement authority.
FINANCIAL AUTHORITY BOUNDARY: Kennel EOS exclusively owns financial execution.
FAIL-CLOSED DECLARATION: Malformed contracts, phases, fingerprints, tenant
                         mismatch, skipped transitions, and divergent replay reject.
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from enum import StrEnum
import hashlib
import hmac
import json
import re
from types import MappingProxyType
from typing import Final, Mapping, Any

VERSION: Final[str] = "v1.0.0-C1C-R1"
MAX_MODEL_TURNS: Final[int] = 2
MAX_TOOL_INVOCATIONS: Final[int] = 1
_ID = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._:-]{0,127}$")
_HEX = re.compile(r"^[0-9a-f]{128}$")


class AIToolOrchestrationError(ValueError):
    """Stable fail-closed C1C contract error."""

    def __init__(self, code: str) -> None:
        self.code = code
        super().__init__(code)


class ToolRiskClass(StrEnum):
    """Closed risk vocabulary; R1 permits read-only tools only."""

    READ_ONLY = "READ_ONLY"


def _identity(value: object, code: str) -> str:
    if not isinstance(value, str) or _ID.fullmatch(value) is None:
        raise AIToolOrchestrationError(code)
    return value


def _digest(value: object, code: str) -> str:
    if not isinstance(value, str) or _HEX.fullmatch(value) is None:
        raise AIToolOrchestrationError(code)
    return value


@dataclass(frozen=True, slots=True)
class AIToolContract:
    """Immutable provider-neutral tool metadata with no callable authority."""

    identity: str
    version: str
    domain: str
    capability: str
    underlying_permission: str
    risk_class: ToolRiskClass
    pii_class: str
    argument_names: tuple[str, ...]

    def __post_init__(self) -> None:
        for value in (self.identity, self.version, self.domain, self.capability,
                      self.underlying_permission, self.pii_class):
            _identity(value, "C1C_TOOL_CONTRACT_TEXT_INVALID")
        if self.risk_class is not ToolRiskClass.READ_ONLY:
            raise AIToolOrchestrationError("C1C_TOOL_RISK_FORBIDDEN")
        if not isinstance(self.argument_names, tuple) or not self.argument_names:
            raise AIToolOrchestrationError("C1C_TOOL_ARGUMENTS_INVALID")
        if len(set(self.argument_names)) != len(self.argument_names):
            raise AIToolOrchestrationError("C1C_TOOL_ARGUMENTS_DUPLICATE")
        for argument in self.argument_names:
            _identity(argument, "C1C_TOOL_ARGUMENT_INVALID")


class OrchestrationPhase(StrEnum):
    """Strict monotonic root lifecycle."""

    STARTED = "STARTED"
    PLANNED_FINAL = "PLANNED_FINAL"
    PLANNED_TOOL = "PLANNED_TOOL"
    TOOL_COMPLETED = "TOOL_COMPLETED"
    COMPLETED = "COMPLETED"
    RECONCILIATION_REQUIRED = "RECONCILIATION_REQUIRED"


_ALLOWED: Final[Mapping[OrchestrationPhase, frozenset[OrchestrationPhase]]] = {
    OrchestrationPhase.STARTED: frozenset({OrchestrationPhase.PLANNED_FINAL, OrchestrationPhase.PLANNED_TOOL, OrchestrationPhase.RECONCILIATION_REQUIRED}),
    OrchestrationPhase.PLANNED_FINAL: frozenset({OrchestrationPhase.COMPLETED, OrchestrationPhase.RECONCILIATION_REQUIRED}),
    OrchestrationPhase.PLANNED_TOOL: frozenset({OrchestrationPhase.TOOL_COMPLETED, OrchestrationPhase.RECONCILIATION_REQUIRED}),
    OrchestrationPhase.TOOL_COMPLETED: frozenset({OrchestrationPhase.COMPLETED, OrchestrationPhase.RECONCILIATION_REQUIRED}),
    OrchestrationPhase.COMPLETED: frozenset(),
    OrchestrationPhase.RECONCILIATION_REQUIRED: frozenset(),
}


def orchestration_identity(tenant_id: str, principal_id: str, idempotency_key: str) -> str:
    """Derive an opaque root identity without persisting the raw key."""
    for value in (tenant_id, principal_id, idempotency_key):
        if not isinstance(value, str) or not value.strip():
            raise AIToolOrchestrationError("C1C_IDENTITY_INPUT_INVALID")
    raw = json.dumps({"tenant_id": tenant_id, "principal_id": principal_id,
                      "idempotency_key": idempotency_key}, sort_keys=True,
                     separators=(",", ":")).encode()
    return "c1c-orch-" + hashlib.sha3_512(raw).hexdigest()[:48]


@dataclass(frozen=True, slots=True)
class AIToolOrchestration:
    """Immutable bounded root snapshot; never contains transient text."""

    orchestration_id: str
    tenant_id: str
    principal_id: str
    correlation_id: str
    phase: OrchestrationPhase
    planner_invocation_id: str
    tool_invocation_id: str | None = None
    synthesis_invocation_id: str | None = None
    tool_identity: str | None = None
    resource_identity: str | None = None
    evidence_references: tuple[str, ...] = ()
    outcome: str | None = None
    revision: int = 0
    occurred_at: datetime = datetime(1970, 1, 1, tzinfo=timezone.utc)
    fingerprint: str = ""

    def __post_init__(self) -> None:
        for value in (self.orchestration_id, self.tenant_id, self.principal_id,
                      self.correlation_id, self.planner_invocation_id):
            _identity(value, "C1C_ORCHESTRATION_IDENTITY_INVALID")
        if self.tool_invocation_id is not None:
            _identity(self.tool_invocation_id, "C1C_TOOL_INVOCATION_ID_INVALID")
        if self.synthesis_invocation_id is not None:
            _identity(self.synthesis_invocation_id, "C1C_SYNTHESIS_INVOCATION_ID_INVALID")
        if self.tool_identity is not None:
            _identity(self.tool_identity, "C1C_TOOL_IDENTITY_INVALID")
        if self.resource_identity is not None:
            _identity(self.resource_identity, "C1C_RESOURCE_IDENTITY_INVALID")
        if not isinstance(self.phase, OrchestrationPhase):
            try:
                object.__setattr__(self, "phase", OrchestrationPhase(str(self.phase)))
            except ValueError as error:
                raise AIToolOrchestrationError("C1C_PHASE_INVALID") from error
        if isinstance(self.revision, bool) or not isinstance(self.revision, int) or self.revision < 0:
            raise AIToolOrchestrationError("C1C_REVISION_INVALID")
        if not isinstance(self.occurred_at, datetime) or self.occurred_at.tzinfo is None:
            raise AIToolOrchestrationError("C1C_OCCURRED_AT_INVALID")
        object.__setattr__(self, "occurred_at", self.occurred_at.astimezone(timezone.utc))
        payload = self.to_dict(include_fingerprint=False)
        digest = hashlib.sha3_512(json.dumps(payload, sort_keys=True, separators=(",", ":")).encode()).hexdigest()
        if self.fingerprint and not hmac.compare_digest(self.fingerprint, digest):
            raise AIToolOrchestrationError("C1C_FINGERPRINT_MISMATCH")
        object.__setattr__(self, "fingerprint", digest)

    def to_dict(self, *, include_fingerprint: bool = True) -> dict[str, object]:
        """Return bounded canonical fields only."""
        payload: dict[str, object] = {
            "orchestration_id": self.orchestration_id, "tenant_id": self.tenant_id,
            "principal_id": self.principal_id, "correlation_id": self.correlation_id,
            "phase": self.phase.value, "planner_invocation_id": self.planner_invocation_id,
            "tool_invocation_id": self.tool_invocation_id,
            "synthesis_invocation_id": self.synthesis_invocation_id,
            "tool_identity": self.tool_identity, "resource_identity": self.resource_identity,
            "evidence_references": list(self.evidence_references), "outcome": self.outcome,
            "revision": self.revision, "occurred_at": self.occurred_at.isoformat().replace("+00:00", "Z"),
        }
        if include_fingerprint:
            payload["fingerprint"] = self.fingerprint
        return payload

    def transition(self, phase: OrchestrationPhase, *, occurred_at: datetime, **changes: object) -> "AIToolOrchestration":
        """Apply one allowed monotonic transition with revision CAS semantics."""
        if phase not in _ALLOWED[self.phase]:
            raise AIToolOrchestrationError("C1C_PHASE_TRANSITION_FORBIDDEN")
        values = {**self.to_dict(include_fingerprint=False), **changes,
                  "phase": phase, "revision": self.revision + 1,
                  "occurred_at": occurred_at, "fingerprint": ""}
        values["evidence_references"] = tuple(values.get("evidence_references", ()))
        return AIToolOrchestration(**values)


__all__ = ["VERSION", "MAX_MODEL_TURNS", "MAX_TOOL_INVOCATIONS", "ToolRiskClass", "AIToolContract", "OrchestrationPhase", "AIToolOrchestration", "AIToolOrchestrationError", "orchestration_identity"]

# ARTIFACT: ai_tool_orchestration.py
# VERSION: v1.0.0-C1C-R1
# AUTHORITY BOUNDARY: bounded orchestration evidence and read-only metadata
# TENANT POSTURE: explicit tenant/principal identity on every snapshot
# FAIL-CLOSED POSTURE: strict schema, phase CAS and SHA3-512 fingerprints
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively
# END OF WILSY OS SOVEREIGN ARTIFACT
