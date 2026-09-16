"""R23 focused certificate for the OpenAI Responses adapter.

TITLE: WILSY AI OpenAI Responses Provider Unit Certificate
VERSION: v1.0.0-C1B-R23
AUTHORITY: Wilsy OS Core Governance
EPITOME: Prove one server-bound, non-streaming, tool-free OpenAI request maps
         exactly to the provider-neutral C1A result without retries or secrets.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tests/unit/test_openai_responses_provider.py
COLLABORATION / OWNERSHIP: Certifies tools/eos/intelligence/providers/
                            openai_responses_provider.py against C1A.
CERTIFICATION / UPDATE DATE: 2026-09-16
CHANGELOG: v1.0.0-C1B-R23 establishes deterministic SDK, failure, identity,
           output, usage, and no-retry certificates.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2.
SECURITY / PRIVACY POSTURE: Synthetic credentials and bounded fakes only.
TENANT BOUNDARY: Request tenant data is never projected into provider metadata.
AUTHORITY BOUNDARY: Provider transport evidence only; no legal or financial truth.
FAIL-CLOSED DECLARATION: Identity, response, usage, and SDK failures map safely.
"""
from __future__ import annotations

from types import SimpleNamespace
from typing import Any

import pytest

from tools.eos.intelligence.domain.ai_model_execution import (
    ModelExecutionError,
    ModelExecutionInput,
    ModelExecutionOutcome,
)
from tools.eos.intelligence.providers.openai_responses_provider import (
    OPENAI_BASE_URL,
    OpenAIResponsesProvider,
)


def request(**changes: Any) -> ModelExecutionInput:
    """Build one server-bound provider request with deterministic identities."""
    values: dict[str, Any] = {
        "tenant_id": "tenant-r23",
        "principal_id": "principal-r23",
        "invocation_id": "invocation-r23",
        "correlation_id": "correlation-r23",
        "entitlement_id": "entitlement-r23",
        "provider_id": "openai",
        "model_id": "gpt-5-mini",
        "prompt": "bounded prompt",
        "system_policy": "bounded policy",
    }
    values.update(changes)
    return ModelExecutionInput(**values)


class FakeResponses:
    """Deterministic Responses API surface recording every request."""

    def __init__(self, result: Any = None, error: Exception | None = None) -> None:
        self.result = result
        self.error = error
        self.calls: list[dict[str, Any]] = []

    def create(self, **kwargs: Any) -> Any:
        self.calls.append(kwargs)
        if self.error is not None:
            raise self.error
        return self.result


class FakeClient:
    """Injected SDK client; no network capability exists in this certificate."""

    def __init__(self, responses: FakeResponses) -> None:
        self.responses = responses


class StatusError(Exception):
    """SDK-shaped status exception carrying only a numeric HTTP status."""

    def __init__(self, status_code: int) -> None:
        self.status_code = status_code
        super().__init__("secret provider body")


def response(*, text: str = "bounded answer", input_tokens: Any = 7, output_tokens: Any = 3, request_id: Any = "resp-r23") -> Any:
    """Build an SDK-shaped response with explicit output and usage."""
    return SimpleNamespace(
        id=request_id,
        output_text=text,
        usage=SimpleNamespace(input_tokens=input_tokens, output_tokens=output_tokens),
    )


def test_success_projects_only_policy_prompt_and_server_identity() -> None:
    responses = FakeResponses(response(text="  bounded answer  "))
    provider = OpenAIResponsesProvider(model_id="gpt-5-mini", client=FakeClient(responses), max_output_tokens=123)
    result = provider.execute(request())
    assert result.outcome is ModelExecutionOutcome.SUCCESS
    assert result.provider_id == "openai"
    assert result.model_id == "gpt-5-mini"
    assert result.response_text == "bounded answer"
    assert result.input_tokens == 7
    assert result.output_tokens == 3
    assert result.provider_request_id == "resp-r23"
    assert responses.calls == [{
        "model": "gpt-5-mini",
        "instructions": "bounded policy",
        "input": "bounded prompt",
        "max_output_tokens": 123,
        "store": False,
        "tools": [],
    }]


def test_identity_drift_fails_before_provider_call() -> None:
    responses = FakeResponses(response())
    provider = OpenAIResponsesProvider(model_id="gpt-5-mini", client=FakeClient(responses))
    with pytest.raises(ModelExecutionError, match="R23_PROVIDER_IDENTITY_MISMATCH"):
        provider.execute(request(model_id="gpt-4o"))
    assert responses.calls == []


@pytest.mark.parametrize(
    ("error", "outcome"),
    [
        (type("APITimeoutError", (Exception,), {})("secret timeout"), ModelExecutionOutcome.PROVIDER_TIMEOUT),
        (type("APIConnectionError", (Exception,), {})("secret connection"), ModelExecutionOutcome.PROVIDER_UNAVAILABLE),
        (type("RateLimitError", (Exception,), {})("secret rate"), ModelExecutionOutcome.PROVIDER_UNAVAILABLE),
        (StatusError(503), ModelExecutionOutcome.PROVIDER_UNAVAILABLE),
        (StatusError(400), ModelExecutionOutcome.PROVIDER_REJECTED_REQUEST),
    ],
)
def test_expected_provider_failures_are_bounded_and_single_call(error: Exception, outcome: ModelExecutionOutcome) -> None:
    """Map timeout, network, rate, 5xx, and rejected 4xx without retry."""
    responses = FakeResponses(error=error)
    provider = OpenAIResponsesProvider(model_id="gpt-5-mini", client=FakeClient(responses))
    result = provider.execute(request())
    assert result.outcome is outcome
    assert result.response_text == ""
    assert len(responses.calls) == 1
    assert "secret" not in repr(result)


def test_unexpected_adapter_failure_is_not_provider_unavailable() -> None:
    responses = FakeResponses(error=RuntimeError("secret internal detail"))
    provider = OpenAIResponsesProvider(model_id="gpt-5-mini", client=FakeClient(responses))
    result = provider.execute(request())
    assert result.outcome is ModelExecutionOutcome.INTERNAL_CONTRACT_VIOLATION
    assert result.error_classification == "INTERNAL_CONTRACT_VIOLATION"
    assert "secret internal detail" not in repr(result)


@pytest.mark.parametrize(
    "bad_response",
    [
        SimpleNamespace(output_text="", usage=SimpleNamespace(input_tokens=1, output_tokens=1)),
        SimpleNamespace(output_text="answer", usage=None),
        SimpleNamespace(output_text="answer", usage=SimpleNamespace(input_tokens=None, output_tokens=1)),
        SimpleNamespace(output_text="answer", usage=SimpleNamespace(input_tokens=1, output_tokens=None)),
        SimpleNamespace(output_text="answer", usage=SimpleNamespace(input_tokens=1, output_tokens=1), id="bad id"),
    ],
)
def test_malformed_response_and_usage_fail_closed(bad_response: Any) -> None:
    responses = FakeResponses(bad_response)
    result = OpenAIResponsesProvider(model_id="gpt-5-mini", client=FakeClient(responses)).execute(request())
    assert result.outcome is ModelExecutionOutcome.PROVIDER_MALFORMED_RESPONSE
    assert len(responses.calls) == 1


def test_limits_and_client_repr_do_not_expose_credentials() -> None:
    responses = FakeResponses(response())
    provider = OpenAIResponsesProvider(model_id="gpt-5-mini", client=FakeClient(responses), timeout_seconds=60, max_output_tokens=8192)
    assert OPENAI_BASE_URL == "https://api.openai.com/v1"
    assert "api_key" not in repr(provider)
    assert "sk-secret" not in repr(provider)
    with pytest.raises(ModelExecutionError, match="R23_TIMEOUT_INVALID"):
        OpenAIResponsesProvider(model_id="gpt-5-mini", client=FakeClient(responses), timeout_seconds=121)
    with pytest.raises(ModelExecutionError, match="R23_MAX_OUTPUT_TOKENS_INVALID"):
        OpenAIResponsesProvider(model_id="gpt-5-mini", client=FakeClient(responses), max_output_tokens=8193)


def test_one_execute_never_retries() -> None:
    responses = FakeResponses(error=TimeoutError("secret timeout"))
    result = OpenAIResponsesProvider(model_id="gpt-5-mini", client=FakeClient(responses)).execute(request())
    assert result.outcome is ModelExecutionOutcome.PROVIDER_TIMEOUT
    assert len(responses.calls) == 1


# ARTIFACT: test_openai_responses_provider.py
# VERSION: v1.0.0-C1B-R23
# AUTHORITY BOUNDARY: OpenAI adapter certificate only
# TENANT POSTURE: no tenant metadata is sent to provider
# FAIL-CLOSED POSTURE: malformed/failed provider results are bounded
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively
# END OF WILSY OS SOVEREIGN ARTIFACT
