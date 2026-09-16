"""TITLE: Server-Owned AI Model Provider Binding.
VERSION: v1.0.0-C1B-R2
AUTHORITY: Wilsy OS Core Governance.
EPITOME: Resolve a provider-neutral model binding from server-owned
         configuration or deterministic test injection; callers select neither.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tools/eos/intelligence/domain/ai_model_provider_binding.py
COLLABORATION / OWNERSHIP: C1B seam consumed by a future orchestrator; C1A
                            defines execution protocol and remains unchanged.
CERTIFICATION / UPDATE DATE: 2026-09-16
CHANGELOG: v1.0.0-C1B-R2 establishes immutable binding identity and fail-closed
           disabled/missing resolution without network or vendor SDKs.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2.
SECURITY / PRIVACY POSTURE: No credentials or provider responses are retained.
TENANT BOUNDARY: Binding is server-owned and may be scoped to one tenant.
AUTHORITY BOUNDARY: Provider/model selection seam only; no execution.
FINANCIAL AUTHORITY BOUNDARY: Kennel EOS exclusively owns financial execution.
FAIL-CLOSED DECLARATION: Missing, disabled, malformed, or caller-selected
                         bindings reject deterministically.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Final, Protocol

VERSION: Final[str] = "v1.0.0-C1B-R2"


class AIModelProviderBindingError(ValueError):
    """Raised when server-owned binding resolution fails closed."""


class ModelProvider(Protocol):
    """Provider-neutral execution protocol implemented outside this package."""

    def execute(self, request: Any) -> Any: ...


@dataclass(frozen=True, slots=True)
class AIModelProviderBinding:
    """Immutable server-owned provider/model identity and injected capability."""

    provider_id: str
    model_id: str
    provider: ModelProvider
    enabled: bool = True
    binding_version: str = VERSION

    def __post_init__(self) -> None:
        if self.binding_version != VERSION or not isinstance(self.provider_id, str) or not self.provider_id.strip() or not isinstance(self.model_id, str) or not self.model_id.strip() or self.provider is None or not callable(getattr(self.provider, "execute", None)):
            raise AIModelProviderBindingError("C1B_PROVIDER_BINDING_INVALID")
        if not isinstance(self.enabled, bool):
            raise AIModelProviderBindingError("C1B_PROVIDER_BINDING_ENABLED_INVALID")


class ServerOwnedModelProviderBinding:
    """Resolver whose only mutable input is server-owned construction state."""

    __slots__ = ("_binding",)

    def __init__(self, binding: AIModelProviderBinding | None = None) -> None:
        self._binding = binding

    @classmethod
    def from_injected(cls, *, provider: ModelProvider, provider_id: str = "injected", model_id: str = "test-model", enabled: bool = True) -> "ServerOwnedModelProviderBinding":
        """Build deterministic test binding; this is not caller request authority."""
        return cls(AIModelProviderBinding(provider_id=provider_id, model_id=model_id, provider=provider, enabled=enabled))

    def resolve(self, *, requested_provider_id: str | None = None, requested_model_id: str | None = None) -> AIModelProviderBinding:
        """Return server binding; any caller attempt to override identity denies."""
        if requested_provider_id is not None or requested_model_id is not None:
            raise AIModelProviderBindingError("C1B_PROVIDER_MODEL_CALLER_SELECTION_FORBIDDEN")
        if self._binding is None:
            raise AIModelProviderBindingError("C1B_PROVIDER_BINDING_MISSING")
        if not self._binding.enabled:
            raise AIModelProviderBindingError("C1B_PROVIDER_BINDING_DISABLED")
        return self._binding


def resolve_server_owned_binding(binding: ServerOwnedModelProviderBinding, *, requested_provider_id: str | None = None, requested_model_id: str | None = None) -> AIModelProviderBinding:
    """Resolve one server-owned binding without executing a provider."""
    if not isinstance(binding, ServerOwnedModelProviderBinding):
        raise AIModelProviderBindingError("C1B_PROVIDER_BINDING_RESOLVER_INVALID")
    return binding.resolve(requested_provider_id=requested_provider_id, requested_model_id=requested_model_id)


__all__ = ["VERSION", "ModelProvider", "AIModelProviderBinding", "AIModelProviderBindingError", "ServerOwnedModelProviderBinding", "resolve_server_owned_binding"]

# ARTIFACT: ai_model_provider_binding.py
# VERSION: v1.0.0-C1B-R2
# AUTHORITY BOUNDARY: server-owned provider/model binding seam only
# TENANT POSTURE: no caller-controlled provider identity
# FAIL-CLOSED POSTURE: missing, disabled, malformed, or overridden binding denies
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively
# END OF WILSY OS SOVEREIGN ARTIFACT
