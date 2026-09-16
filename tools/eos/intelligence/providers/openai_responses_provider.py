"""OpenAI Responses API adapter for the provider-neutral model contract.

TITLE: WILSY AI OpenAI Responses Provider Adapter
VERSION: v1.0.0-C1B-R23
AUTHORITY: Wilsy OS Core Governance
EPITOME: Translate one server-bound ModelExecutionInput into one bounded,
         non-streaming OpenAI Responses request and a sanitized ModelProviderResult.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tools/eos/intelligence/providers/openai_responses_provider.py
COLLABORATION / OWNERSHIP: Server-owned runtime constructs this adapter;
                            C1B consumes the provider-neutral result;
                            OpenAI owns transport capability only.
CERTIFICATION / UPDATE DATE: 2026-09-16
CHANGELOG: v1.0.0-C1B-R23 adds a single-call OpenAI Responses adapter with
           explicit no-retry, canonical endpoint, bounded output, and sanitized
           failure translation.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2.
SECURITY / PRIVACY POSTURE: API keys never enter request models, repr, errors,
                             logs, metadata, or durable evidence.
TENANT BOUNDARY: Tenant and principal fields are consumed only by WILSY's
                 transient provider-neutral request fingerprint; they are not
                 sent as provider metadata.
AUTHORITY BOUNDARY: Replaceable model-compute transport; no IAM, legal,
                    lifecycle, billing, payment, or settlement authority.
FINANCIAL AUTHORITY BOUNDARY: Kennel EOS exclusively owns financial execution.
FAIL-CLOSED DECLARATION: Identity drift, malformed responses, and vendor
                         failures map to bounded C1A outcomes without retries.
"""
from __future__ import annotations

from collections.abc import Mapping
import re
from typing import Any, Final, cast

from tools.eos.intelligence.domain.ai_model_execution import (
    ModelExecutionError,
    ModelExecutionInput,
    ModelExecutionOutcome,
    ModelProvider,
    ModelProviderResult,
)


VERSION: Final[str] = "v1.0.0-C1B-R23"
PROVIDER_ID: Final[str] = "openai"
OPENAI_BASE_URL: Final[str] = "https://api.openai.com/v1"
DEFAULT_TIMEOUT_SECONDS: Final[float] = 60.0
DEFAULT_MAX_OUTPUT_TOKENS: Final[int] = 8192
MAX_TIMEOUT_SECONDS: Final[float] = 120.0
MAX_OUTPUT_TOKENS: Final[int] = 8192
_IDENTITY = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._:-]{0,127}$")


class _MalformedProviderResponse(ValueError):
    """Internal marker for a response that violates the C1A result shape."""


def _bounded_model_id(model_id: object) -> str:
    """Require one exact server-owned model identity."""
    if not isinstance(model_id, str) or _IDENTITY.fullmatch(model_id) is None:
        raise ModelExecutionError("R23_MODEL_ID_INVALID")
    return model_id


def _bounded_timeout(value: object) -> float:
    """Require a conservative server-owned timeout."""
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ModelExecutionError("R23_TIMEOUT_INVALID")
    timeout = float(value)
    if timeout <= 0 or timeout > MAX_TIMEOUT_SECONDS:
        raise ModelExecutionError("R23_TIMEOUT_INVALID")
    return timeout


def _bounded_output_limit(value: object) -> int:
    """Require a positive bounded server-owned output limit."""
    if isinstance(value, bool) or not isinstance(value, int) or value <= 0 or value > MAX_OUTPUT_TOKENS:
        raise ModelExecutionError("R23_MAX_OUTPUT_TOKENS_INVALID")
    return value


def _field(value: object, name: str) -> object:
    """Read one SDK object or mapping field without invoking arbitrary methods."""
    if isinstance(value, Mapping):
        return value.get(name)
    return getattr(value, name, None)


def _provider_error_outcome(error: Exception) -> ModelExecutionOutcome:
    """Map expected SDK failures without retaining vendor details."""
    name = type(error).__name__.lower()
    if isinstance(error, TimeoutError) or "timeout" in name:
        return ModelExecutionOutcome.PROVIDER_TIMEOUT
    if isinstance(error, (ConnectionError, OSError)) or "connection" in name or "network" in name:
        return ModelExecutionOutcome.PROVIDER_UNAVAILABLE
    if "ratelimit" in name or "rate_limit" in name:
        return ModelExecutionOutcome.PROVIDER_UNAVAILABLE
    status_code = getattr(error, "status_code", None)
    if isinstance(status_code, int):
        if status_code in {408, 409, 429} or status_code >= 500:
            return ModelExecutionOutcome.PROVIDER_UNAVAILABLE
        if 400 <= status_code < 500:
            return ModelExecutionOutcome.PROVIDER_REJECTED_REQUEST
    if any(token in name for token in ("badrequest", "authentication", "permissiondenied", "notfound", "unprocessable")):
        return ModelExecutionOutcome.PROVIDER_REJECTED_REQUEST
    if "apierror" in name or "statuserror" in name:
        return ModelExecutionOutcome.PROVIDER_UNAVAILABLE
    return ModelExecutionOutcome.INTERNAL_CONTRACT_VIOLATION


def _failure(provider_id: str, model_id: str, outcome: ModelExecutionOutcome) -> ModelProviderResult:
    """Build a result containing only the bounded C1A failure vocabulary."""
    return ModelProviderResult(
        provider_id=provider_id,
        model_id=model_id,
        outcome=outcome,
        error_classification=outcome.value,
    )


class OpenAIResponsesProvider:
    """Execute one non-streaming Responses API request with no SDK retries."""

    __slots__ = ("_client", "_model_id", "_timeout_seconds", "_max_output_tokens")

    def __init__(
        self,
        *,
        model_id: str,
        api_key: str | None = None,
        timeout_seconds: float = DEFAULT_TIMEOUT_SECONDS,
        max_output_tokens: int = DEFAULT_MAX_OUTPUT_TOKENS,
        client: Any | None = None,
    ) -> None:
        """Construct one server-owned client or accept a deterministic test client."""
        self._model_id = _bounded_model_id(model_id)
        self._timeout_seconds = _bounded_timeout(timeout_seconds)
        self._max_output_tokens = _bounded_output_limit(max_output_tokens)
        if client is None:
            if not isinstance(api_key, str) or not api_key.strip() or len(api_key) > 4096:
                raise ModelExecutionError("R23_API_KEY_INVALID")
            from openai import OpenAI

            client = OpenAI(
                api_key=api_key,
                base_url=OPENAI_BASE_URL,
                timeout=self._timeout_seconds,
                max_retries=0,
            )
        if not callable(getattr(getattr(client, "responses", None), "create", None)):
            raise ModelExecutionError("R23_SDK_CLIENT_INVALID")
        self._client = client

    @property
    def model_id(self) -> str:
        """Return the immutable server-configured model identity."""
        return self._model_id

    def __repr__(self) -> str:
        """Expose only non-secret operational identity."""
        return f"OpenAIResponsesProvider(model_id={self._model_id!r}, timeout_seconds={self._timeout_seconds!r}, max_output_tokens={self._max_output_tokens!r})"

    def execute(self, request: ModelExecutionInput) -> ModelProviderResult:
        """Make at most one Responses API call and return sanitized evidence input."""
        if not isinstance(request, ModelExecutionInput):
            raise ModelExecutionError("R23_REQUEST_INVALID")
        if request.provider_id != PROVIDER_ID or request.model_id != self._model_id:
            raise ModelExecutionError("R23_PROVIDER_IDENTITY_MISMATCH")
        try:
            response = self._client.responses.create(
                model=self._model_id,
                instructions=request.system_policy,
                input=request.prompt,
                max_output_tokens=self._max_output_tokens,
                store=False,
                tools=[],
            )
        except Exception as error:
            return _failure(PROVIDER_ID, self._model_id, _provider_error_outcome(error))
        try:
            output_text = _field(response, "output_text")
            if not isinstance(output_text, str) or not output_text.strip():
                raise _MalformedProviderResponse("output")
            output_text = output_text.strip()
            usage = _field(response, "usage")
            if usage is None:
                raise _MalformedProviderResponse("usage")
            input_tokens = _field(usage, "input_tokens")
            output_tokens = _field(usage, "output_tokens")
            if any(isinstance(value, bool) or not isinstance(value, int) or value < 0 for value in (input_tokens, output_tokens)):
                raise _MalformedProviderResponse("tokens")
            input_token_count = cast(int, input_tokens)
            output_token_count = cast(int, output_tokens)
            provider_request_id = _field(response, "id")
            if provider_request_id is not None and (not isinstance(provider_request_id, str) or _IDENTITY.fullmatch(provider_request_id) is None):
                raise _MalformedProviderResponse("request_id")
            return ModelProviderResult(
                provider_id=PROVIDER_ID,
                model_id=self._model_id,
                response_text=output_text,
                provider_request_id=provider_request_id,
                input_tokens=input_token_count,
                output_tokens=output_token_count,
                outcome=ModelExecutionOutcome.SUCCESS,
            )
        except _MalformedProviderResponse:
            return _failure(PROVIDER_ID, self._model_id, ModelExecutionOutcome.PROVIDER_MALFORMED_RESPONSE)
        except Exception:
            return _failure(PROVIDER_ID, self._model_id, ModelExecutionOutcome.INTERNAL_CONTRACT_VIOLATION)


__all__ = ["VERSION", "PROVIDER_ID", "OPENAI_BASE_URL", "OpenAIResponsesProvider"]

# ARTIFACT: openai_responses_provider.py
# VERSION: v1.0.0-C1B-R23
# AUTHORITY BOUNDARY: replaceable OpenAI transport adapter only
# TENANT POSTURE: no provider metadata or caller-selected identity
# FAIL-CLOSED POSTURE: one call, no retry, bounded sanitized outcomes
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively
# END OF WILSY OS SOVEREIGN ARTIFACT
