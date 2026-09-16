"""Server-owned production reasoning provider configuration.

TITLE: WILSY AI Reasoning Provider Runtime Factory
VERSION: v1.0.0-C1B-R23
AUTHORITY: Wilsy OS Core Governance
EPITOME: Resolve one optional, server-owned OpenAI Responses binding from
         bounded environment configuration without accepting caller overrides.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tools/eos/intelligence/providers/reasoning_provider_runtime.py
COLLABORATION / OWNERSHIP: API composition invokes this factory once per
                            application; C1B consumes its binding; adapter owns
                            vendor translation.
CERTIFICATION / UPDATE DATE: 2026-09-16
CHANGELOG: v1.0.0-C1B-R23 establishes explicit provider selection, secret
           sourcing, timeout/output bounds, and fail-closed configuration.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2.
SECURITY / PRIVACY POSTURE: API keys are read only for SDK construction and
                             never retained by this factory or placed in errors.
TENANT BOUNDARY: Configuration is server-wide; request tenants cannot alter it.
AUTHORITY BOUNDARY: Provider binding configuration only; no execution or law.
FINANCIAL AUTHORITY BOUNDARY: Kennel EOS exclusively owns financial execution.
FAIL-CLOSED DECLARATION: Unknown or malformed configuration returns bounded
                         configuration errors and never substitutes a provider.
"""
from __future__ import annotations

import os
from typing import Final

from tools.eos.intelligence.domain.ai_model_provider_binding import (
    AIModelProviderBinding,
    ServerOwnedModelProviderBinding,
)

from .openai_responses_provider import (
    DEFAULT_MAX_OUTPUT_TOKENS,
    DEFAULT_TIMEOUT_SECONDS,
    OpenAIResponsesProvider,
)


VERSION: Final[str] = "v1.0.0-C1B-R23"
_MAX_TIMEOUT_SECONDS: Final[float] = 120.0
_MAX_OUTPUT_TOKENS: Final[int] = 8192


class ReasoningProviderConfigurationError(ValueError):
    """Stable configuration failure that contains no secret material."""

    def __init__(self, code: str) -> None:
        self.code = code
        super().__init__(code)


def _bounded_timeout(raw: str) -> float:
    """Parse one positive bounded timeout from server configuration."""
    try:
        value = float(raw)
    except (TypeError, ValueError) as error:
        raise ReasoningProviderConfigurationError("R23_TIMEOUT_INVALID") from error
    if value <= 0 or value > _MAX_TIMEOUT_SECONDS:
        raise ReasoningProviderConfigurationError("R23_TIMEOUT_INVALID")
    return value


def _bounded_output_tokens(raw: str) -> int:
    """Parse one positive bounded output limit from server configuration."""
    try:
        value = int(raw)
    except (TypeError, ValueError) as error:
        raise ReasoningProviderConfigurationError("R23_MAX_OUTPUT_TOKENS_INVALID") from error
    if value <= 0 or value > _MAX_OUTPUT_TOKENS:
        raise ReasoningProviderConfigurationError("R23_MAX_OUTPUT_TOKENS_INVALID")
    return value


def build_reasoning_provider_binding_from_environment() -> ServerOwnedModelProviderBinding | None:
    """Build one server-owned production binding, or None when unconfigured."""
    selector = os.getenv("WILSY_AI_REASONING_PROVIDER", "").strip().lower()
    if not selector:
        return None
    if selector != "openai":
        raise ReasoningProviderConfigurationError("R23_PROVIDER_UNSUPPORTED")
    api_key = os.getenv("OPENAI_API_KEY", "")
    model_id = os.getenv("WILSY_AI_REASONING_MODEL", "")
    if not api_key.strip():
        raise ReasoningProviderConfigurationError("R23_API_KEY_MISSING")
    if not model_id.strip():
        raise ReasoningProviderConfigurationError("R23_MODEL_ID_MISSING")
    timeout = _bounded_timeout(os.getenv("WILSY_AI_REASONING_TIMEOUT_SECONDS", str(DEFAULT_TIMEOUT_SECONDS)))
    max_output_tokens = _bounded_output_tokens(os.getenv("WILSY_AI_REASONING_MAX_OUTPUT_TOKENS", str(DEFAULT_MAX_OUTPUT_TOKENS)))
    try:
        provider = OpenAIResponsesProvider(
            model_id=model_id,
            api_key=api_key,
            timeout_seconds=timeout,
            max_output_tokens=max_output_tokens,
        )
        return ServerOwnedModelProviderBinding(
            AIModelProviderBinding(provider_id="openai", model_id=provider.model_id, provider=provider)
        )
    except Exception as error:
        if isinstance(error, ReasoningProviderConfigurationError):
            raise
        raise ReasoningProviderConfigurationError("R23_PROVIDER_CONFIGURATION_INVALID") from error


__all__ = ["VERSION", "ReasoningProviderConfigurationError", "build_reasoning_provider_binding_from_environment"]

# ARTIFACT: reasoning_provider_runtime.py
# VERSION: v1.0.0-C1B-R23
# AUTHORITY BOUNDARY: server-owned provider configuration only
# TENANT POSTURE: request tenants cannot select provider/model/secret
# FAIL-CLOSED POSTURE: absent or malformed configuration is inactive
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively
# END OF WILSY OS SOVEREIGN ARTIFACT
