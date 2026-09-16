"""Direct C1A certificate for the provider-neutral model contract.

TITLE: WILSY AI Model Execution Unit Certificate
VERSION: v1.0.0-WILSY-AI-MODEL-EXECUTION-UNIT
AUTHORITY: Wilsy OS Core Governance
EPITOME: Proves the pure model request/result vocabulary and bounded immutable
         invocation evidence without invoking a provider or persistence.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tests/unit/test_ai_model_execution.py
COLLABORATION / OWNERSHIP: Certifies tools/eos/intelligence/domain/ai_model_execution.py.
CERTIFICATION / UPDATE DATE: 2026-09-16
CHANGELOG: v1.0.0 establishes direct validation of provider neutrality,
           server-bound identity, deterministic fingerprints, usage metadata,
           sanitized failures, and durable evidence exclusions.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2.
SECURITY / PRIVACY POSTURE: Test assertions prove no raw prompt, system policy,
                             reasoning, secret, or provider exception persists.
TENANT BOUNDARY: Every evidence object is derived from one explicit tenant.
AUTHORITY BOUNDARY: Model-compute evidence only; no legal or financial truth.
FINANCIAL AUTHORITY BOUNDARY: Kennel EOS exclusively owns financial execution.
FAIL-CLOSED DECLARATION: Contract and fingerprint drift must fail closed.
"""
from __future__ import annotations

from dataclasses import FrozenInstanceError
from datetime import datetime, timedelta, timezone
import ast
import inspect
from typing import Any, cast

import pytest

from tools.eos.intelligence.domain.ai_model_execution import (
    MODEL_EXECUTION_CAPABILITY,
    MODEL_EXECUTION_MODULE_ID,
    ModelExecutionError,
    ModelExecutionInput,
    ModelExecutionOutcome,
    ModelInvocationEvidence,
    ModelProviderResult,
    canonical_json,
    sanitize_provider_error,
    sha3_512_fingerprint,
)


BASE_TIME = datetime(2026, 9, 16, 8, 0, tzinfo=timezone.utc)


def make_request(**changes: object) -> ModelExecutionInput:
    """Build one valid server-bound transient request."""
    values: dict[str, object] = {
        "tenant_id": "tenant-c1a",
        "principal_id": "principal-1",
        "invocation_id": "invocation-1",
        "correlation_id": "correlation-1",
        "entitlement_id": "entitlement-1",
        "provider_id": "provider-neutral",
        "model_id": "model-neutral-v1",
        "prompt": "Summarize the supplied matter.",
        "system_policy": "Return bounded advisory text.",
        "request_units": 1,
        "tool_invocation_evidence_references": ("tool-evidence-1",),
    }
    values.update(changes)
    return ModelExecutionInput(**cast(Any, values))


def make_result(**changes: object) -> ModelProviderResult:
    """Build one valid transient provider result."""
    values: dict[str, object] = {
        "provider_id": "provider-neutral",
        "model_id": "model-neutral-v1",
        "response_text": "Bounded advisory result.",
        "provider_request_id": "provider-request-1",
        "input_tokens": 4,
        "output_tokens": 3,
    }
    values.update(changes)
    return ModelProviderResult(**cast(Any, values))


def make_evidence(**changes: object) -> ModelInvocationEvidence:
    """Compose one valid immutable evidence object."""
    request = make_request()
    result = make_result()
    values: dict[str, object] = {
        "tenant_id": request.tenant_id,
        "principal_id": request.principal_id,
        "invocation_id": request.invocation_id,
        "correlation_id": request.correlation_id,
        "entitlement_id": request.entitlement_id,
        "provider_id": result.provider_id,
        "model_id": result.model_id,
        "provider_request_id": result.provider_request_id,
        "request_fingerprint": request.request_fingerprint,
        "response_fingerprint": result.response_fingerprint,
        "request_units": request.request_units,
        "input_tokens": result.input_tokens,
        "output_tokens": result.output_tokens,
        "outcome": result.outcome,
        "error_classification": result.error_classification,
        "created_at": BASE_TIME,
        "completed_at": BASE_TIME + timedelta(milliseconds=4),
        "tool_invocation_evidence_references": request.tool_invocation_evidence_references,
    }
    values.update(changes)
    return ModelInvocationEvidence(**cast(Any, values))


def test_provider_neutral_contract_has_no_provider_sdk_imports() -> None:
    """The domain source must not couple to OpenAI, Anthropic, or HTTP clients."""
    module = __import__("tools.eos.intelligence.domain.ai_model_execution", fromlist=["x"])
    tree = ast.parse(inspect.getsource(module))
    imported = {
        node.module
        for node in ast.walk(tree)
        if isinstance(node, ast.ImportFrom)
    } | {
        alias.name
        for node in ast.walk(tree)
        if isinstance(node, ast.Import)
        for alias in node.names
    }
    assert not any(
        name and any(token in name.lower() for token in ("openai", "anthropic", "google", "boto3", "httpx", "requests"))
        for name in imported
    )


def test_server_bound_identity_and_distinct_model_capability() -> None:
    """Tenant identity is explicit and model-compute identity is distinct."""
    request = make_request()
    assert request.tenant_id == "tenant-c1a"
    assert MODEL_EXECUTION_MODULE_ID == "WILSY_AI_REASONING"
    assert MODEL_EXECUTION_CAPABILITY == "wilsy_ai.reasoning.execute.v1"
    assert MODEL_EXECUTION_MODULE_ID != "WILSY_AI_LEGAL_TOOL_GATEWAY"
    with pytest.raises(ModelExecutionError, match="C1A_TENANT_INVALID"):
        make_request(tenant_id="global")


def test_input_is_immutable_and_request_fingerprint_is_deterministic() -> None:
    """Equivalent requests hash identically while material changes are visible."""
    first = make_request()
    second = make_request()
    assert first.request_fingerprint == second.request_fingerprint
    assert len(first.request_fingerprint) == 128
    assert first.request_fingerprint == first.request_fingerprint.lower()
    assert make_request(prompt="A different bounded prompt.").request_fingerprint != first.request_fingerprint
    with pytest.raises(FrozenInstanceError):
        first.prompt = "changed"  # type: ignore[misc]


def test_response_and_evidence_fingerprints_are_deterministic_and_bound() -> None:
    """Provider result and complete evidence fingerprints bind their payloads."""
    result = make_result()
    assert result.response_fingerprint == make_result().response_fingerprint
    evidence = ModelInvocationEvidence.from_execution(
        make_request(), result, created_at=BASE_TIME, completed_at=BASE_TIME + timedelta(seconds=1)
    )
    assert len(evidence.fingerprint) == 128
    altered = make_evidence(correlation_id="correlation-2")
    assert altered.fingerprint != evidence.fingerprint
    assert evidence.to_dict()["fingerprint"] == evidence.fingerprint


def test_durable_evidence_excludes_transient_and_authority_expanding_fields() -> None:
    """Serialized evidence contains bounded references and no sensitive payload."""
    request = make_request(prompt="RAW USER PROMPT MUST NOT BE DURABLE")
    result = make_result(response_text="RAW PROVIDER RESPONSE MUST NOT BE DURABLE")
    evidence = ModelInvocationEvidence.from_execution(
        request, result, created_at=BASE_TIME, completed_at=BASE_TIME + timedelta(seconds=1)
    )
    payload = evidence.to_dict()
    forbidden = {
        "prompt",
        "system_prompt",
        "system_policy",
        "response_text",
        "chain_of_thought",
        "reasoning_trace",
        "provider_secret",
        "authorization_token",
        "raw_provider_error",
        "request_payload",
        "response_payload",
        "tool_results",
        "tenant_authority",
        "legal_truth",
        "financial_truth",
    }
    assert forbidden.isdisjoint(payload)
    assert payload["tool_invocation_evidence_references"] == ["tool-evidence-1"]
    assert payload["tenant_id"] == "tenant-c1a"
    assert "RAW USER PROMPT" not in canonical_json(payload)
    assert "RAW PROVIDER RESPONSE" not in canonical_json(payload)


def test_usage_metadata_and_sanitized_failure_vocabulary() -> None:
    """Usage quantities are representable and provider failures are bounded."""
    success = make_result(input_tokens=0, output_tokens=0)
    assert success.input_tokens == 0 and success.output_tokens == 0
    failure = ModelProviderResult(
        provider_id="provider-neutral",
        model_id="model-neutral-v1",
        outcome=ModelExecutionOutcome.PROVIDER_TIMEOUT,
        error_classification="PROVIDER_TIMEOUT",
    )
    assert failure.response_fingerprint
    assert sanitize_provider_error(TimeoutError("secret provider detail")) is ModelExecutionOutcome.PROVIDER_TIMEOUT
    assert sanitize_provider_error(ConnectionError("secret provider detail")) is ModelExecutionOutcome.PROVIDER_UNAVAILABLE
    assert sanitize_provider_error(ValueError("secret provider detail")) is ModelExecutionOutcome.PROVIDER_MALFORMED_RESPONSE
    with pytest.raises(ModelExecutionError, match="C1A_REQUEST_UNITS_INVALID"):
        make_request(request_units=0)
    with pytest.raises(ModelExecutionError, match="C1A_INPUT_TOKENS_INVALID"):
        make_result(input_tokens=-1)


def test_failure_evidence_contains_only_sanitized_error_classification() -> None:
    """Failure evidence cannot contain an exception message or response text."""
    request = make_request()
    result = ModelProviderResult(
        provider_id=request.provider_id,
        model_id=request.model_id,
        outcome=ModelExecutionOutcome.PROVIDER_UNAVAILABLE,
        error_classification="PROVIDER_UNAVAILABLE",
    )
    evidence = ModelInvocationEvidence.from_execution(
        request, result, created_at=BASE_TIME, completed_at=BASE_TIME + timedelta(seconds=1)
    )
    assert evidence.error_classification == "PROVIDER_UNAVAILABLE"
    encoded = canonical_json(evidence.to_dict())
    assert "exception" not in encoded.lower()
    assert "traceback" not in encoded.lower()


def test_strict_hydration_rejects_unknown_fields_and_fingerprint_drift() -> None:
    """Persisted evidence is exact-schema and cryptographically self-checking."""
    payload = make_evidence().to_dict()
    unknown = dict(payload)
    unknown["unknown_field"] = "reject"
    with pytest.raises(ModelExecutionError, match="C1A_EVIDENCE_SCHEMA_INVALID"):
        ModelInvocationEvidence.from_dict(unknown)
    corrupt = dict(payload)
    corrupt["fingerprint"] = "0" * 128
    with pytest.raises(ModelExecutionError, match="C1A_EVIDENCE_FINGERPRINT_MISMATCH"):
        ModelInvocationEvidence.from_dict(corrupt)


def test_sha3_helper_is_lowercase_deterministic_and_not_python_hash() -> None:
    """The shared helper provides stable canonical SHA3-512 evidence."""
    digest = sha3_512_fingerprint({"b": 2, "a": 1})
    assert digest == sha3_512_fingerprint({"a": 1, "b": 2})
    assert len(digest) == 128 and digest == digest.lower()


def test_authority_firewall_and_no_usage_write() -> None:
    """The pure contract exposes no persistence, legal, financial, or usage write."""
    evidence = make_evidence()
    assert not hasattr(evidence, "create_or_replay")
    assert not hasattr(evidence, "settle")
    assert not hasattr(evidence, "transition")
    assert "usage_observation" not in evidence.to_dict()
    assert "legal_fact" not in evidence.to_dict()
    assert "financial_truth" not in evidence.to_dict()


def test_chronology_requires_completion_not_before_creation() -> None:
    """Evidence chronology is explicit and fail closed."""
    with pytest.raises(ModelExecutionError, match="C1A_EVIDENCE_CHRONOLOGY_INVALID"):
        make_evidence(completed_at=BASE_TIME - timedelta(microseconds=1))


def test_provider_result_cannot_supply_server_authority() -> None:
    """Provider result has operational metadata only and cannot override tenant."""
    result = make_result()
    assert not hasattr(result, "tenant_id")
    request = make_request(tenant_id="tenant-c1a")
    evidence = ModelInvocationEvidence.from_execution(
        request, result, created_at=BASE_TIME, completed_at=BASE_TIME
    )
    assert evidence.tenant_id == request.tenant_id


def test_tool_references_are_references_only() -> None:
    """Tool evidence references are opaque identities, never tool result payloads."""
    evidence = make_evidence(tool_invocation_evidence_references=("legal-tool-evidence-1",))
    assert evidence.tool_invocation_evidence_references == ("legal-tool-evidence-1",)
    assert all(isinstance(item, str) for item in evidence.tool_invocation_evidence_references)


# ARTIFACT: test_ai_model_execution.py
# VERSION: v1.0.0-WILSY-AI-MODEL-EXECUTION-UNIT
# AUTHORITY BOUNDARY: direct pure-contract certification only
# TENANT POSTURE: server-bound identity assertions
# FAIL-CLOSED POSTURE: invalid payloads and drift are rejected
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively
# END OF WILSY OS SOVEREIGN ARTIFACT
