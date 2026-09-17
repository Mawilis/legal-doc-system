"""C1D-R1 unit certificate for the immutable advisory foundation.

TITLE: Next-Best-Action Advisory Unit Certificate
VERSION: v1.1.0-C1E-R1
AUTHORITY: Wilsy OS Core Governance
EPITOME: Proves strict evidence binding, deterministic identity, replay-safe
         lineage, and advisory-only boundaries without database or provider calls.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tests/unit/test_next_best_action_advisory.py
COLLABORATION / OWNERSHIP: C1D domain and Legal adapter certificate.
CERTIFICATION / UPDATE DATE: 2026-09-17
CHANGELOG: v1.1.0-C1E-R1 refreshes typed result-reference fixtures while
           preserving immutable-envelope and adapter coverage.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2.
"""
from datetime import datetime, timezone
import hashlib
import json
from dataclasses import FrozenInstanceError, replace

import pytest

from tools.eos.intelligence.adapters.legal_operations_advisory_adapter import (
    POLICY_ID,
    POLICY_VERSION,
    LegalOperationsAdvisoryError,
    build_legal_advisory,
)
from tools.eos.intelligence.domain.ai_tool_orchestration import AIToolOrchestration, OrchestrationPhase, orchestration_identity
from tools.eos.intelligence.domain.legal_ai_gateway import GATEWAY_PERMISSION, LegalAIToolInvocationEvidence, TOOL_CONTRACTS, TOOL_IDENTITIES
from tools.eos.intelligence.domain.next_best_action_advisory import AdvisorySourceReference, NextBestActionAdvisory, NextBestActionAdvisoryError, build_advisory, source_snapshot_fingerprint

STAMP = datetime(2026, 9, 17, 8, 0, tzinfo=timezone.utc)
TENANT = "tenant-c1d"
PRINCIPAL = "principal-c1d"
ROOT_ID = orchestration_identity(TENANT, PRINCIPAL, "idem-c1d")


def _evidence(*, tool: str = "legal.attempt.read.v1", result: dict[str, object] | None = None):
    result = result or {"tenant_id": TENANT, "attempt_id": "attempt-1", "state": "ALLOCATED"}
    result_fp = hashlib.sha3_512(json.dumps(result, sort_keys=True, separators=(",", ":"), default=str).encode()).hexdigest()
    contract = TOOL_CONTRACTS[tool]
    root = AIToolOrchestration(ROOT_ID, TENANT, PRINCIPAL, ROOT_ID, OrchestrationPhase.COMPLETED, "planner-1", tool_invocation_id="inv-1", synthesis_invocation_id="synth-1", tool_identity=tool, resource_identity="attempt-1", evidence_references=("result-1",), outcome="TOOL_ASSISTED", revision=1, occurred_at=STAMP)
    invocation = LegalAIToolInvocationEvidence("inv-1", TENANT, PRINCIPAL, tool, "v1", GATEWAY_PERMISSION, contract.underlying_permission, contract.capability, "role", "entitlement-1", 1, "a" * 128, "tier", "b" * 128, "capacity:1", "c" * 128, ROOT_ID, "d" * 128, "READ", f"{contract.entity_type}:attempt-1", result_fp, STAMP)
    return root, invocation, result


def _advisory(**kwargs):
    root, invocation, result = _evidence(**kwargs)
    return build_legal_advisory(tenant_id=TENANT, scope_ref="matter-1", root=root, invocation=invocation, result=result, generated_at=STAMP)


def test_adapter_accepts_all_seven_tools_and_computes_evidence_completeness():
    for tool in TOOL_IDENTITIES:
        item = _advisory(tool=tool)
        assert item.recommendation.confidence_score == 1.0
        assert item.recommendation.risk_level == "MEDIUM"
        assert item.decision.disposition == "PROPOSED"
        assert len(item.source_references) == 5


def test_identity_snapshot_and_order_are_deterministic():
    item = _advisory()
    assert item == NextBestActionAdvisory.from_dict(item.to_dict())
    assert source_snapshot_fingerprint(tuple(reversed(item.source_references))) == item.source_snapshot_fingerprint
    changed = _advisory(result={"tenant_id": TENANT, "attempt_id": "attempt-2", "state": "ALLOCATED"})
    assert changed.advisory_id != item.advisory_id
    assert changed.recommendation.recommendation_id != item.recommendation.recommendation_id
    assert changed.decision.decision_id != item.decision.decision_id


def test_immutable_and_strict_envelope_contract():
    item = _advisory()
    with pytest.raises(FrozenInstanceError):
        item.scope_ref = "other"  # type: ignore[misc]
    payload = item.to_dict()
    payload["unexpected"] = True
    with pytest.raises(NextBestActionAdvisoryError, match="SCHEMA"):
        NextBestActionAdvisory.from_dict(payload)
    corrupted = item.to_dict()
    corrupted["fingerprint"] = "0" * 128
    with pytest.raises(NextBestActionAdvisoryError, match="FINGERPRINT"):
        NextBestActionAdvisory.from_dict(corrupted)


def test_duplicate_sources_and_traceability_fail_closed():
    item = _advisory()
    duplicate = item.source_references + (item.source_references[0],)
    with pytest.raises(NextBestActionAdvisoryError, match="DUPLICATE"):
        source_snapshot_fingerprint(duplicate)
    with pytest.raises(NextBestActionAdvisoryError):
        replace(item, scope_ref="other")


def test_adapter_rejects_final_only_unknown_or_mismatched_evidence():
    root, invocation, result = _evidence()
    with pytest.raises(LegalOperationsAdvisoryError, match="TOOL_ASSISTED"):
        build_legal_advisory(tenant_id=TENANT, scope_ref="matter-1", root=replace(root, phase=OrchestrationPhase.STARTED, fingerprint=""), invocation=invocation, result=result, generated_at=STAMP)
    with pytest.raises(LegalOperationsAdvisoryError, match="FINGERPRINT"):
        build_legal_advisory(tenant_id=TENANT, scope_ref="matter-1", root=root, invocation=invocation, result={"tenant_id": TENANT, "attempt_id": "changed"}, generated_at=STAMP)
    with pytest.raises(LegalOperationsAdvisoryError, match="TENANT"):
        build_legal_advisory(tenant_id="tenant-other", scope_ref="matter-1", root=root, invocation=invocation, result=result, generated_at=STAMP)


def test_adapter_rejects_root_tool_drift_and_exposes_no_execution_surface():
    root, invocation, result = _evidence()
    drifted_root = replace(root, tool_identity="legal.command.execute.v1", fingerprint="")
    with pytest.raises(LegalOperationsAdvisoryError, match="TOOL"):
        build_legal_advisory(tenant_id=TENANT, scope_ref="matter-1", root=drifted_root, invocation=invocation, result=result, generated_at=STAMP)
    adapter_methods = {name for name in dir(build_legal_advisory) if name in {"execute", "approve", "release", "settle", "pay"}}
    assert adapter_methods == set()
    assert not hasattr(__import__("tools.eos.intelligence.adapters.legal_operations_advisory_adapter", fromlist=["LegalOperationsAdvisoryAdapter"]).LegalOperationsAdvisoryAdapter, "execute")


def test_recommendation_is_not_an_execution_or_financial_authority():
    item = _advisory()
    assert item.decision.disposition == "PROPOSED"
    assert "authorization" in item.recommendation.confidence_basis
    assert POLICY_ID == item.policy_id and POLICY_VERSION == item.policy_version
    assert not any("legal." in ref.evidence_identity for ref in item.source_references)


def test_supersession_self_reference_rejected():
    item = _advisory()
    with pytest.raises(NextBestActionAdvisoryError, match="SELF"):
        build_advisory(tenant_id=TENANT, scope_ref="matter-1", policy_id=POLICY_ID, policy_version=POLICY_VERSION, source_references=item.source_references, action_title="Review", target_subsystem="Legal Operations review", rationale="Review evidence before considering a downstream step.", risk_level="MEDIUM", generated_at="2026-09-17T08:01:00Z", supersedes_advisory_id=item.advisory_id)


# ARTIFACT: test_next_best_action_advisory.py
# VERSION: v1.1.0-C1E-R1
# CERTIFICATION: focused unit proof only; no Mongo or provider execution
# END OF WILSY OS SOVEREIGN ARTIFACT
