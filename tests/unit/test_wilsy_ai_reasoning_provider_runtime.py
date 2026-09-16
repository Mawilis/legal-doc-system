"""R23 certificate for server-owned reasoning provider configuration.

TITLE: WILSY AI Reasoning Provider Runtime Unit Certificate
VERSION: v1.0.0-C1B-R23
AUTHORITY: Wilsy OS Core Governance
EPITOME: Prove optional, server-owned OpenAI configuration fails closed and
         constructs one replaceable provider binding without network calls.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tests/unit/test_wilsy_ai_reasoning_provider_runtime.py
COLLABORATION / OWNERSHIP: Certifies tools/eos/intelligence/providers/
                            reasoning_provider_runtime.py and server composition.
CERTIFICATION / UPDATE DATE: 2026-09-16
CHANGELOG: v1.0.0-C1B-R23 establishes selector, secret, model, bounds,
           injection-precedence, and no-network runtime certificates.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2.
SECURITY / PRIVACY POSTURE: Synthetic credentials only; secrets never appear
                             in errors or representations.
TENANT BOUNDARY: Provider configuration is server-owned and tenant-neutral.
AUTHORITY BOUNDARY: Runtime binding configuration only; no execution authority.
FAIL-CLOSED DECLARATION: Missing, unknown, or malformed configuration is inactive.
"""
from __future__ import annotations

from types import SimpleNamespace
from typing import Any

import pytest

import tools.eos.api.server as server_module
import tools.eos.intelligence.providers.reasoning_provider_runtime as runtime
from tools.eos.intelligence.domain.ai_model_provider_binding import ServerOwnedModelProviderBinding


class FakeProvider:
    """No-network provider constructor double."""

    constructions = 0

    def __init__(self, **kwargs: Any) -> None:
        type(self).constructions += 1
        self.model_id = kwargs.get("model_id", "test-model")

    def execute(self, request: Any) -> Any:
        raise AssertionError("runtime certificate must not execute a provider")


def test_no_selector_returns_no_binding(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("WILSY_AI_REASONING_PROVIDER", raising=False)
    assert runtime.build_reasoning_provider_binding_from_environment() is None


@pytest.mark.parametrize(
    ("selector", "code"),
    [("anthropic", "R23_PROVIDER_UNSUPPORTED"), ("openai", "R23_API_KEY_MISSING")],
)
def test_missing_or_unknown_provider_configuration_fails_closed(monkeypatch: pytest.MonkeyPatch, selector: str, code: str) -> None:
    monkeypatch.setenv("WILSY_AI_REASONING_PROVIDER", selector)
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    monkeypatch.delenv("WILSY_AI_REASONING_MODEL", raising=False)
    with pytest.raises(runtime.ReasoningProviderConfigurationError, match=code):
        runtime.build_reasoning_provider_binding_from_environment()


@pytest.mark.parametrize(
    ("variable", "value", "code"),
    [
        ("WILSY_AI_REASONING_TIMEOUT_SECONDS", "bad", "R23_TIMEOUT_INVALID"),
        ("WILSY_AI_REASONING_TIMEOUT_SECONDS", "121", "R23_TIMEOUT_INVALID"),
        ("WILSY_AI_REASONING_MAX_OUTPUT_TOKENS", "bad", "R23_MAX_OUTPUT_TOKENS_INVALID"),
        ("WILSY_AI_REASONING_MAX_OUTPUT_TOKENS", "8193", "R23_MAX_OUTPUT_TOKENS_INVALID"),
    ],
)
def test_malformed_bounds_fail_closed(monkeypatch: pytest.MonkeyPatch, variable: str, value: str, code: str) -> None:
    monkeypatch.setenv("WILSY_AI_REASONING_PROVIDER", "openai")
    monkeypatch.setenv("OPENAI_API_KEY", "synthetic-key")
    monkeypatch.setenv("WILSY_AI_REASONING_MODEL", "gpt-5-mini")
    monkeypatch.setenv(variable, value)
    with pytest.raises(runtime.ReasoningProviderConfigurationError, match=code):
        runtime.build_reasoning_provider_binding_from_environment()


def test_valid_openai_configuration_is_server_owned_and_constructed_once(monkeypatch: pytest.MonkeyPatch) -> None:
    FakeProvider.constructions = 0
    monkeypatch.setenv("WILSY_AI_REASONING_PROVIDER", "openai")
    monkeypatch.setenv("OPENAI_API_KEY", "synthetic-key")
    monkeypatch.setenv("WILSY_AI_REASONING_MODEL", "gpt-5-mini")
    monkeypatch.setenv("WILSY_AI_REASONING_TIMEOUT_SECONDS", "30")
    monkeypatch.setenv("WILSY_AI_REASONING_MAX_OUTPUT_TOKENS", "100")
    monkeypatch.setattr(runtime, "OpenAIResponsesProvider", FakeProvider)
    binding = runtime.build_reasoning_provider_binding_from_environment()
    assert isinstance(binding, ServerOwnedModelProviderBinding)
    assert binding.resolve().provider_id == "openai"
    assert binding.resolve().model_id == "gpt-5-mini"
    assert FakeProvider.constructions == 1
    with pytest.raises(Exception, match="CALLER_SELECTION_FORBIDDEN"):
        binding.resolve(requested_provider_id="other")


def test_programmatic_server_injection_overrides_environment(monkeypatch: pytest.MonkeyPatch) -> None:
    sentinel = ServerOwnedModelProviderBinding.from_injected(provider=FakeProvider())
    monkeypatch.setattr(server_module, "build_reasoning_provider_binding_from_environment", lambda: (_ for _ in ()).throw(AssertionError("factory must not run")))
    app = server_module.WilsyAPIServer(reasoning_provider_binding=sentinel, allowed_origins=[]).app
    assert app.state.wilsy_ai_reasoning_provider_binding is sentinel


def test_server_reasoning_endpoint_uses_worker_function_boundary() -> None:
    import inspect
    import tools.eos.api.wilsy_ai_reasoning_router as router_module

    assert inspect.iscoroutinefunction(router_module.execute_reasoning) is False


# ARTIFACT: test_wilsy_ai_reasoning_provider_runtime.py
# VERSION: v1.0.0-C1B-R23
# AUTHORITY BOUNDARY: provider runtime configuration certificate only
# TENANT POSTURE: no caller-selected tenant/provider/model authority
# FAIL-CLOSED POSTURE: malformed configuration returns stable errors
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively
# END OF WILSY OS SOVEREIGN ARTIFACT
