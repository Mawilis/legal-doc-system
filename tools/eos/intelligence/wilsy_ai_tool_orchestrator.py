"""WILSY OS C1C bounded legal-tool orchestration runtime.

TITLE: Governed WILSY AI Tool Orchestrator
VERSION: v1.1.0-C1C-R1B
AUTHORITY: Wilsy OS Core Governance
EPITOME: Execute at most one server-authorized legal read between one planner
         and one synthesis turn, with deterministic root replay and no model
         authority over tenants, entitlements, Mongo, or legal truth.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tools/eos/intelligence/wilsy_ai_tool_orchestrator.py
COLLABORATION / OWNERSHIP: C1C composes C1B reasoning, L7B legal reads and
                            P6B observations; each upstream authority remains canonical.
CERTIFICATION / UPDATE DATE: 2026-09-17
CHANGELOG: v1.1.0-C1C-R1B adds durable root phase commits, caller-owned
           accounting transactions, reconciliation markers, and restart-safe
           replay without provider re-execution.
           v1.0.0-C1C-R1 establishes strict planner parsing, egress gating,
           one-tool bounds, replay, and bounded response sources.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2.
SECURITY / PRIVACY POSTURE: Raw prompt/model/tool data is transient only.
TENANT BOUNDARY: Root identity and every tool operation are tenant/principal scoped.
AUTHORITY BOUNDARY: Orchestration and read evidence only; no legal command,
                    service execution, invoice, payment, or settlement authority.
FINANCIAL AUTHORITY BOUNDARY: Kennel EOS exclusively owns financial execution.
FAIL-CLOSED DECLARATION: Strict JSON, capacity/IAM/egress rechecks, and unknown
                         commit/reconciliation failures never synthesize success.
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
import hashlib
import json
import re
from typing import Any, Mapping, Protocol, cast

from tools.eos.intelligence.domain.ai_model_execution import ModelExecutionInput, ModelProviderResult, ModelExecutionOutcome
from tools.eos.intelligence.domain.ai_tool_orchestration import AIToolOrchestration, OrchestrationPhase, MAX_MODEL_TURNS, MAX_TOOL_INVOCATIONS, orchestration_identity, AIToolOrchestrationError
from tools.eos.intelligence.tools.registry import ServerOwnedAIToolRegistry, AIToolRegistryError


class LegalToolEgressPolicy(Protocol):
    """Server-owned decision on whether a legal projection may leave storage."""
    def allow(self, *, tenant_id: str, principal_id: str, tool_identity: str, pii_class: str, result: Mapping[str, object]) -> bool: ...


class DenySensitiveEgress:
    """Default policy: legal PII never leaves the server without explicit policy."""
    def allow(self, **_kwargs: Any) -> bool:
        return False


class AllowTestEgress:
    """Explicitly injectable non-production policy useful for certificates."""
    def allow(self, **_kwargs: Any) -> bool:
        return True


class C1COrchestrationError(RuntimeError):
    """Stable bounded orchestration failure."""
    def __init__(self, code: str) -> None:
        self.code = code
        super().__init__(code)


@dataclass(frozen=True, slots=True)
class PlannerDecision:
    """Strict planner decision; arbitrary keys and prose are rejected."""
    decision: str
    response_text: str = ""
    tool_identity: str | None = None
    arguments: Mapping[str, str] | None = None


def parse_planner_json(raw: str) -> PlannerDecision:
    """Parse exact FINAL/TOOL JSON and reject all authority-expanding fields."""
    if not isinstance(raw, str):
        raise C1COrchestrationError("C1C_PLANNER_MALFORMED")
    try:
        payload = json.loads(raw)
    except (TypeError, ValueError) as error:
        raise C1COrchestrationError("C1C_PLANNER_MALFORMED") from error
    if not isinstance(payload, dict) or not isinstance(payload.get("decision"), str):
        raise C1COrchestrationError("C1C_PLANNER_MALFORMED")
    decision = payload["decision"]
    if decision == "FINAL":
        if set(payload) != {"decision", "response_text"} or not isinstance(payload.get("response_text"), str):
            raise C1COrchestrationError("C1C_PLANNER_MALFORMED")
        return PlannerDecision(decision="FINAL", response_text=payload["response_text"])
    if decision == "TOOL":
        if set(payload) != {"decision", "tool_identity", "arguments"} or not isinstance(payload.get("tool_identity"), str) or not isinstance(payload.get("arguments"), dict):
            raise C1COrchestrationError("C1C_PLANNER_MALFORMED")
        args = payload["arguments"]
        if set(args) != {"resource_identity"} or not isinstance(args.get("resource_identity"), str) or not args["resource_identity"].strip():
            raise C1COrchestrationError("C1C_PLANNER_MALFORMED")
        return PlannerDecision(decision="TOOL", tool_identity=payload["tool_identity"], arguments={"resource_identity": args["resource_identity"]})
    raise C1COrchestrationError("C1C_PLANNER_MALFORMED")


def _child(prefix: str, root: str) -> str:
    return f"{prefix}-{hashlib.sha3_512(root.encode()).hexdigest()[:40]}"


@dataclass(frozen=True, slots=True)
class OrchestrationResponse:
    """Bounded public response with evidence references only."""
    orchestration_id: str
    outcome: str
    response_text: str
    sources: tuple[dict[str, str], ...] = ()

    def to_dict(self) -> dict[str, object]:
        return {"orchestration_id": self.orchestration_id, "outcome": self.outcome, "response_text": self.response_text, "sources": [dict(item) for item in self.sources]}


class WilsyAIToolOrchestrator:
    """Run one bounded C1C flow using injected server-owned authorities."""

    __slots__ = ("_tools", "_model", "_egress", "_clock", "_roots", "_legal_reader", "_evidence_writer", "_usage_writer", "_tool_accounting_writer", "_root_registry", "_root_session_factory", "_tool_session_factory", "_production")

    def __init__(self, *, tool_registry: ServerOwnedAIToolRegistry, model_provider: Any, egress_policy: LegalToolEgressPolicy | None = None, legal_reader: Any | None = None, evidence_writer: Any | None = None, usage_writer: Any | None = None, tool_accounting_writer: Any | None = None, clock: Any | None = None, root_registry: Any | None = None, root_session_factory: Any | None = None, tool_session_factory: Any | None = None, production: bool = False) -> None:
        if hasattr(model_provider, "provider"):
            binding = model_provider
            provider = binding.provider
            class _BoundProvider:
                provider_id = binding.provider_id
                model_id = binding.model_id
                def execute(self, request: ModelExecutionInput) -> ModelProviderResult:
                    return provider.execute(request)
            model_provider = _BoundProvider()
        if not isinstance(tool_registry, ServerOwnedAIToolRegistry) or not callable(getattr(model_provider, "execute", None)):
            raise C1COrchestrationError("C1C_DEPENDENCIES_INVALID")
        self._tools, self._model, self._egress = tool_registry, model_provider, egress_policy or DenySensitiveEgress()
        if production and (root_registry is None or not callable(root_session_factory) or not callable(tool_accounting_writer)):
            raise C1COrchestrationError("C1C_DURABLE_ROOT_REQUIRED")
        self._clock, self._roots = (clock or (lambda: datetime.now(timezone.utc))), {}
        self._legal_reader, self._evidence_writer, self._usage_writer = legal_reader, evidence_writer, usage_writer
        self._tool_accounting_writer = tool_accounting_writer
        self._root_registry, self._root_session_factory, self._tool_session_factory, self._production = root_registry, root_session_factory, tool_session_factory or root_session_factory, production

    def persist_tool_accounting(self, *, evidence: Any, usage: Any, session: Any) -> None:
        """Write exact legal evidence and automation usage on one caller session.

        The caller starts/commits/aborts the transaction.  Both writes receive
        the identical session; a writer failure is propagated and no second
        persistence path is attempted.
        """
        if session is None or self._evidence_writer is None or self._usage_writer is None:
            raise C1COrchestrationError("C1C_TOOL_ACCOUNTING_DEPENDENCIES_INVALID")
        self._evidence_writer(evidence=evidence, session=session)
        self._usage_writer(usage=usage, session=session)

    def _durable_transition(self, root: AIToolOrchestration, phase: OrchestrationPhase, **changes: object) -> AIToolOrchestration:
        """Commit one root phase through the caller-independent production registry."""
        if not self._production:
            return root.transition(phase, occurred_at=self._now(), **changes)
        session = cast(Any, self._root_session_factory)()
        registry = cast(Any, self._root_registry)
        try:
            session.start_transaction()
            current = registry.get(tenant_id=root.tenant_id, orchestration_id=root.orchestration_id, session=session)
            if current.phase is not root.phase or current.revision != root.revision:
                raise C1COrchestrationError("C1C_DURABLE_ROOT_DIVERGED")
            next_root = current.transition(phase, occurred_at=self._now(), **changes)
            registry.transition(next_root, expected_revision=current.revision, session=session)
            session.commit_transaction()
            return next_root
        except C1COrchestrationError:
            if getattr(session, "in_transaction", False):
                session.abort_transaction()
            if phase is not OrchestrationPhase.RECONCILIATION_REQUIRED:
                self._mark_reconciliation(root)
            raise
        except Exception as error:
            if getattr(session, "in_transaction", False):
                session.abort_transaction()
            if phase is not OrchestrationPhase.RECONCILIATION_REQUIRED:
                self._mark_reconciliation(root)
            raise C1COrchestrationError("C1C_DURABLE_ROOT_UNAVAILABLE") from error
        finally:
            session.end_session()

    def _mark_reconciliation(self, root: AIToolOrchestration) -> None:
        """Best-effort durable reconciliation marker after an unknown transaction outcome."""
        if not self._production:
            return
        try:
            self._durable_transition(root, OrchestrationPhase.RECONCILIATION_REQUIRED)
        except Exception:
            # The original failure remains the authoritative error; callers must
            # not mistake an unavailable reconciliation write for success.
            return

    def _durable_tool_accounting(self, *, root: AIToolOrchestration, tenant_id: str, principal_id: str, invocation_id: str, correlation_id: str, tool_identity: str, resource_identity: str, evidence_reference: str, result_fingerprint: str, context: Any, collections: Mapping[str, Any], result: Mapping[str, object]) -> str:
        """Atomically persist canonical L7B evidence and M13P5B usage before synthesis."""
        if not self._production:
            return evidence_reference
        writer = cast(Any, self._tool_accounting_writer)
        session = cast(Any, self._tool_session_factory)()
        try:
            session.start_transaction()
            persisted = writer(
                tenant_id=tenant_id,
                principal_id=principal_id,
                invocation_id=invocation_id,
                correlation_id=correlation_id,
                tool_identity=tool_identity,
                resource_identity=resource_identity,
                evidence_reference=evidence_reference,
                result_fingerprint=result_fingerprint,
                context=context,
                collections=collections,
                result=result,
                session=session,
            )
            if not isinstance(persisted, str) or not persisted.strip():
                raise C1COrchestrationError("C1C_TOOL_ACCOUNTING_INVALID")
            session.commit_transaction()
            return persisted
        except Exception as error:
            if getattr(session, "in_transaction", False):
                session.abort_transaction()
            self._mark_reconciliation(root)
            if isinstance(error, C1COrchestrationError):
                raise
            raise C1COrchestrationError("C1C_TOOL_ACCOUNTING_UNAVAILABLE") from error
        finally:
            session.end_session()

    def _now(self) -> datetime:
        value = self._clock()
        if not isinstance(value, datetime) or value.tzinfo is None:
            raise C1COrchestrationError("C1C_CLOCK_INVALID")
        return value.astimezone(timezone.utc)

    def _provider_turn(self, *, tenant_id: str, principal_id: str, invocation_id: str, correlation_id: str, prompt: str, policy: str, tool_refs: tuple[str, ...] = ()) -> ModelProviderResult:
        provider_id = str(getattr(self._model, "provider_id", "server-bound"))
        model_id = str(getattr(self._model, "model_id", "server-bound"))
        request = ModelExecutionInput(tenant_id=tenant_id, principal_id=principal_id, invocation_id=invocation_id, correlation_id=correlation_id, entitlement_id="server-bound", provider_id=provider_id, model_id=model_id, prompt=prompt, system_policy=policy, tool_invocation_evidence_references=tool_refs)
        result = self._model.execute(request)
        if not isinstance(result, ModelProviderResult):
            raise C1COrchestrationError("C1C_PROVIDER_RESULT_INVALID")
        return result

    def run(self, *, tenant_id: str, principal_id: str, idempotency_key: str, prompt: str, context: Any = None, collections: Mapping[str, Any] | None = None) -> OrchestrationResponse:
        """Execute FINAL or one TOOL_ASSISTED flow; replay never calls provider again."""
        root_id = orchestration_identity(tenant_id, principal_id, idempotency_key)
        if root_id in self._roots and not self._production:
            return self._roots[root_id]
        if self._production and self._root_registry is None:
            raise C1COrchestrationError("C1C_DURABLE_ROOT_UNAVAILABLE")
        if not isinstance(prompt, str) or not prompt.strip():
            raise C1COrchestrationError("C1C_PROMPT_INVALID")
        planner_id, tool_id, synth_id = (_child("c1c-plan", root_id), _child("c1c-tool", root_id), _child("c1c-synth", root_id))
        durable_root: AIToolOrchestration | None = None
        if self._production:
            session_factory = cast(Any, self._root_session_factory)
            root_registry = cast(Any, self._root_registry)
            session = session_factory()
            try:
                if callable(getattr(session, "start_transaction", None)):
                    session.start_transaction()
                existing = None
                try:
                    existing = root_registry.get(tenant_id=tenant_id, orchestration_id=root_id, session=session)
                except Exception as error:
                    if "NOT_FOUND" not in str(error):
                        raise
                if existing is not None:
                    raise C1COrchestrationError("C1C_REPLAY_DURABLE")
                started = AIToolOrchestration(root_id, tenant_id, principal_id, root_id, OrchestrationPhase.STARTED, planner_id, occurred_at=self._now())
                durable_root = root_registry.create_or_replay(started, session=session)
                session.commit_transaction()
            except C1COrchestrationError:
                if getattr(session, "in_transaction", False):
                    session.abort_transaction()
                raise
            except Exception as error:
                if getattr(session, "in_transaction", False):
                    session.abort_transaction()
                raise C1COrchestrationError("C1C_DURABLE_ROOT_UNAVAILABLE") from error
            finally:
                session.end_session()
        planner = self._provider_turn(tenant_id=tenant_id, principal_id=principal_id, invocation_id=planner_id, correlation_id=root_id, prompt=prompt, policy="C1C planner: return exact FINAL or TOOL JSON; provider-native tools disabled.")
        if planner.outcome is not ModelExecutionOutcome.SUCCESS:
            raise C1COrchestrationError("C1C_PLANNER_UNAVAILABLE")
        decision = parse_planner_json(planner.response_text)
        now = self._now()
        if decision.decision == "FINAL":
            if durable_root is not None:
                durable_root = self._durable_transition(durable_root, OrchestrationPhase.PLANNED_FINAL)
                self._durable_transition(durable_root, OrchestrationPhase.COMPLETED, outcome="FINAL")
            response = OrchestrationResponse(root_id, "FINAL", decision.response_text, ())
            if not self._production:
                self._roots[root_id] = response
            return response
        if not self._tools.contains(decision.tool_identity or ""):
            raise C1COrchestrationError("C1C_TOOL_UNKNOWN")
        registered = self._tools.get(decision.tool_identity or "")
        arguments = decision.arguments or {}
        resource_identity = arguments.get("resource_identity")
        if not isinstance(resource_identity, str):
            raise C1COrchestrationError("C1C_PLANNER_MALFORMED")
        if durable_root is not None:
            durable_root = self._durable_transition(durable_root, OrchestrationPhase.PLANNED_TOOL, tool_invocation_id=tool_id, synthesis_invocation_id=synth_id, tool_identity=registered.contract.identity, resource_identity=resource_identity)
        result = registered.adapter(contract=registered.contract, resource_identity=resource_identity, context=context, collections=collections or {})
        if not isinstance(result, Mapping):
            raise C1COrchestrationError("C1C_TOOL_RESULT_INVALID")
        if not self._egress.allow(tenant_id=tenant_id, principal_id=principal_id, tool_identity=registered.contract.identity, pii_class=registered.contract.pii_class, result=result):
            raise C1COrchestrationError("C1C_EGRESS_DENIED")
        result_fp = hashlib.sha3_512(json.dumps(dict(result), sort_keys=True, separators=(",", ":"), default=str).encode()).hexdigest()
        evidence_ref = f"legal-tool:{tool_id}"
        if self._production:
            if durable_root is None:
                raise C1COrchestrationError("C1C_DURABLE_ROOT_UNAVAILABLE")
            evidence_ref = self._durable_tool_accounting(root=durable_root, tenant_id=tenant_id, principal_id=principal_id, invocation_id=tool_id, correlation_id=root_id, tool_identity=registered.contract.identity, resource_identity=resource_identity, evidence_reference=evidence_ref, result_fingerprint=result_fp, context=context, collections=collections or {}, result=result)
        elif self._evidence_writer is not None:
            persisted = self._evidence_writer(tool_identity=registered.contract.identity, resource_identity=resource_identity, result_fingerprint=result_fp, tenant_id=tenant_id, principal_id=principal_id, invocation_id=tool_id, context=context)
            evidence_ref = str(persisted)
        if not self._production and self._usage_writer is not None:
            self._usage_writer(tenant_id=tenant_id, source_evidence_reference=evidence_ref, source_evidence_fingerprint=result_fp, idempotency_key=tool_id)
        if durable_root is not None:
            durable_root = self._durable_transition(durable_root, OrchestrationPhase.TOOL_COMPLETED, evidence_references=(evidence_ref,))
        synthesis_prompt = json.dumps({"original_prompt": prompt, "tool_identity": registered.contract.identity, "resource_identity": resource_identity, "result": dict(result), "evidence_reference": evidence_ref}, sort_keys=True, separators=(",", ":"))
        synthesis = self._provider_turn(tenant_id=tenant_id, principal_id=principal_id, invocation_id=synth_id, correlation_id=root_id, prompt=synthesis_prompt, policy="C1C synthesis: use only observed tool result; do not invent legal or financial facts.", tool_refs=(evidence_ref,))
        if synthesis.outcome is not ModelExecutionOutcome.SUCCESS:
            if durable_root is not None:
                self._mark_reconciliation(durable_root)
            raise C1COrchestrationError("C1C_SYNTHESIS_RECONCILIATION_REQUIRED")
        response = OrchestrationResponse(root_id, "TOOL_ASSISTED", synthesis.response_text, ({"tool_identity": registered.contract.identity, "resource_identity": resource_identity, "evidence_reference": evidence_ref},))
        if durable_root is not None:
            self._durable_transition(durable_root, OrchestrationPhase.COMPLETED, outcome="TOOL_ASSISTED")
        if not self._production:
            self._roots[root_id] = response
        return response


__all__ = ["DenySensitiveEgress", "AllowTestEgress", "PlannerDecision", "parse_planner_json", "OrchestrationResponse", "WilsyAIToolOrchestrator", "C1COrchestrationError"]

# ARTIFACT: wilsy_ai_tool_orchestrator.py
# VERSION: v1.1.0-C1C-R1B
# AUTHORITY BOUNDARY: bounded planner/read/synthesis orchestration only
# TENANT POSTURE: root and child identities derive from tenant/principal/key
# FAIL-CLOSED POSTURE: one tool, two turns, strict parser, egress gate
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively
# END OF WILSY OS SOVEREIGN ARTIFACT
