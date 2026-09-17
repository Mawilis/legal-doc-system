"""WILSY OS C1D deterministic Legal Operations advisory adapter.

TITLE: Legal Operations Next-Best-Action Adapter
VERSION: v1.1.0-C1E-R1
AUTHORITY: Wilsy OS Core Governance; server-owned advisory policy
EPITOME: Converts complete C1C TOOL_ASSISTED evidence into one conservative,
         review-only advisory without calling providers or mutating legal state.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tools/eos/intelligence/adapters/legal_operations_advisory_adapter.py
COLLABORATION / OWNERSHIP: Consumes C1C orchestration and L7B invocation facts;
                            C1C, Legal Operations, IAM, and Kennel retain authority.
CERTIFICATION / UPDATE DATE: 2026-09-17
CHANGELOG: v1.1.0-C1E-R1 enforces typed C1D result references and preserves
           the seven-tool allowlist, five-category
           evidence binding, exact C1C result fingerprint validation, and review-only templates.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2.
SECURITY / PRIVACY POSTURE: Legal projections are transient; only identities and fingerprints persist.
TENANT BOUNDARY: Every input is checked against the C1C root and invocation tenant.
AUTHORITY BOUNDARY: Deterministic advisory proposal only; no legal command, IAM,
                    entitlement, capacity, payment, settlement, or execution authority.
FINANCIAL AUTHORITY BOUNDARY: Kennel EOS exclusively owns financial execution.
"""
from __future__ import annotations

from collections.abc import Mapping
from datetime import datetime, timezone
import hashlib
import json
from typing import Any, Final

from tools.eos.intelligence.domain.ai_tool_orchestration import AIToolOrchestration, OrchestrationPhase
from tools.eos.intelligence.domain.legal_ai_gateway import LegalAIToolInvocationEvidence, TOOL_CONTRACTS, TOOL_IDENTITIES
from tools.eos.intelligence.domain.next_best_action_advisory import (
    LEGAL_SOURCE_CATEGORIES,
    AdvisorySourceReference,
    NextBestActionAdvisory,
    NextBestActionAdvisoryError,
    build_advisory,
)

VERSION: Final[str] = "v1.1.0-C1E-R1"
POLICY_ID: Final[str] = "WILSY_AI_LEGAL_NEXT_BEST_ACTION_REVIEW_POLICY"
POLICY_VERSION: Final[str] = "v1"
RISK_LEVEL: Final[str] = "MEDIUM"

_TEMPLATES: Final[dict[str, tuple[str, str]]] = {
    "legal.instruction.read.v1": ("Review recorded instruction context", "Review the instruction and recorded service context before considering any downstream operational step."),
    "legal.attempt.read.v1": ("Review recorded attempt evidence", "Review the recorded attempt outcome and evidence before considering any follow-up service activity."),
    "legal.execution.read.v1": ("Review recorded execution evidence", "Review the recorded execution evidence before considering any further legal-operational step."),
    "legal.return.read.v1": ("Review return evidence", "Review the return evidence and recorded disposition before considering any downstream legal step."),
    "legal.tariff_assessment.read.v1": ("Review tariff assessment", "Review the tariff assessment before any billing consideration."),
    "legal.billing_eligibility.read.v1": ("Review billing eligibility", "Review billing-eligibility evidence before any invoicing consideration."),
    "legal.invoice.read.v1": ("Review invoice state", "Review the invoice state before any financial follow-up; no payment or settlement action is authorized."),
}


class LegalOperationsAdvisoryError(ValueError):
    """Stable fail-closed Legal adapter error."""

    def __init__(self, code: str) -> None:
        self.code = code
        super().__init__(code)


def _text(value: object, code: str) -> str:
    if not isinstance(value, str) or not value or value != value.strip() or len(value) > 512:
        raise LegalOperationsAdvisoryError(code)
    return value


def _result_fingerprint(result: Mapping[str, object]) -> str:
    """Reproduce the published C1C tool-result SHA3-512 canonicalization exactly."""
    return hashlib.sha3_512(json.dumps(dict(result), sort_keys=True, separators=(",", ":"), default=str).encode()).hexdigest()


def _source(category: str, identity: str, fingerprint: str, producer: str, version: str) -> AdvisorySourceReference:
    try:
        return AdvisorySourceReference(category, identity, fingerprint, producer, version)
    except NextBestActionAdvisoryError as error:
        raise LegalOperationsAdvisoryError("C1D_SOURCE_INVALID") from error


def build_legal_advisory(*, tenant_id: str, scope_ref: str, root: AIToolOrchestration,
                         invocation: LegalAIToolInvocationEvidence,
                         result: Mapping[str, object], generated_at: datetime | str | None = None,
                         supersedes_advisory_id: str | None = None) -> NextBestActionAdvisory:
    """Build one review-only advisory from a complete C1C TOOL_ASSISTED record.

    The caller supplies already-authorized root, invocation, and transient result
    facts. This function performs no retrieval, model call, HTTP call, transaction,
    legal mutation, billing mutation, or financial execution.
    """
    if not isinstance(root, AIToolOrchestration) or not isinstance(invocation, LegalAIToolInvocationEvidence):
        raise LegalOperationsAdvisoryError("C1D_EVIDENCE_TYPE_INVALID")
    tenant = _text(tenant_id, "C1D_TENANT_REQUIRED")
    scope = _text(scope_ref, "C1D_SCOPE_REQUIRED")
    if invocation.tenant_id != tenant or root.tenant_id != tenant:
        raise LegalOperationsAdvisoryError("C1D_TENANT_MISMATCH")
    if root.phase is not OrchestrationPhase.COMPLETED or root.outcome != "TOOL_ASSISTED":
        raise LegalOperationsAdvisoryError("C1D_TOOL_ASSISTED_EVIDENCE_REQUIRED")
    if root.orchestration_id != invocation.correlation_id or root.tool_invocation_id != invocation.invocation_id:
        raise LegalOperationsAdvisoryError("C1D_ROOT_INVOCATION_MISMATCH")
    if root.tool_identity != invocation.tool_identity or root.tool_identity not in TOOL_IDENTITIES:
        raise LegalOperationsAdvisoryError("C1D_TOOL_IDENTITY_MISMATCH")
    contract = TOOL_CONTRACTS.get(invocation.tool_identity)
    if contract is None or invocation.tool_version != contract.version:
        raise LegalOperationsAdvisoryError("C1D_TOOL_VERSION_MISMATCH")
    if not isinstance(result, Mapping) or not result:
        raise LegalOperationsAdvisoryError("C1D_RESULT_REQUIRED")
    if "tenant_id" in result and result["tenant_id"] != tenant:
        raise LegalOperationsAdvisoryError("C1D_RESULT_TENANT_MISMATCH")
    if _result_fingerprint(result) != invocation.result_fingerprint:
        raise LegalOperationsAdvisoryError("C1D_RESULT_FINGERPRINT_MISMATCH")
    expected_reference = f"{contract.entity_type}:{root.resource_identity}" if root.resource_identity else ""
    if invocation.result_reference != expected_reference or not root.evidence_references:
        raise LegalOperationsAdvisoryError("C1D_RESULT_REFERENCE_MISMATCH")
    if not invocation.entitlement_id or not invocation.entitlement_fingerprint or not invocation.capacity_evidence_reference or not invocation.capacity_evidence_fingerprint:
        raise LegalOperationsAdvisoryError("C1D_ENTITLEMENT_CAPACITY_REQUIRED")
    sources = (
        _source("ORCHESTRATION_ROOT", root.orchestration_id, root.fingerprint, "c1c.orchestration", "v1"),
        _source("LEGAL_TOOL_INVOCATION", invocation.invocation_id, invocation.fingerprint, "l7b.legal_ai_gateway", invocation.gateway_version),
        _source("LEGAL_TOOL_RESULT", invocation.result_reference, invocation.result_fingerprint, invocation.tool_identity, invocation.tool_version),
        _source("ENTITLEMENT", invocation.entitlement_id, invocation.entitlement_fingerprint, "wilsy_ai_entitlement", "v1"),
        _source("CAPACITY", invocation.capacity_evidence_reference, invocation.capacity_evidence_fingerprint, "wilsy_ai_usage_capacity", "v1"),
    )
    if tuple(item.evidence_type for item in sources) != LEGAL_SOURCE_CATEGORIES:
        raise LegalOperationsAdvisoryError("C1D_EVIDENCE_CATEGORY_INVALID")
    if generated_at is None:
        stamp = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
    elif isinstance(generated_at, datetime):
        if generated_at.tzinfo is None or generated_at.utcoffset() is None:
            raise LegalOperationsAdvisoryError("C1D_GENERATED_AT_INVALID")
        stamp = generated_at.astimezone(timezone.utc).isoformat().replace("+00:00", "Z")
    else:
        stamp = _text(generated_at, "C1D_GENERATED_AT_INVALID")
    action, rationale = _TEMPLATES[invocation.tool_identity]
    try:
        return build_advisory(tenant_id=tenant, scope_ref=scope, policy_id=POLICY_ID, policy_version=POLICY_VERSION, source_references=sources, action_title=action, target_subsystem="Legal Operations review", rationale=rationale, risk_level=RISK_LEVEL, generated_at=stamp, supersedes_advisory_id=supersedes_advisory_id)
    except NextBestActionAdvisoryError as error:
        raise LegalOperationsAdvisoryError(error.code) from error


class LegalOperationsAdvisoryAdapter:
    """Stateless server-owned adapter for deterministic Legal review advice."""

    def build(self, **kwargs: Any) -> NextBestActionAdvisory:
        """Delegate to :func:`build_legal_advisory` without acquiring authority."""
        return build_legal_advisory(**kwargs)


__all__ = ["VERSION", "POLICY_ID", "POLICY_VERSION", "TOOL_IDENTITIES", "LegalOperationsAdvisoryError", "LegalOperationsAdvisoryAdapter", "build_legal_advisory"]

# ARTIFACT: legal_operations_advisory_adapter.py
# VERSION: v1.1.0-C1E-R1
# AUTHORITY BOUNDARY: deterministic advisory proposal only; no legal or execution authority
# TENANT POSTURE: root, invocation, and transient result tenant must agree exactly
# FAIL-CLOSED POSTURE: incomplete C1C evidence, unknown tools, mismatched fingerprints, and drift reject
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively
# END OF WILSY OS SOVEREIGN ARTIFACT
