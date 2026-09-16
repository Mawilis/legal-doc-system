"""TITLE: C1B server-owned provider binding certificate.
VERSION: v1.0.0-C1B-R2
AUTHORITY: Wilsy OS Core Governance.
EPITOME: Certify missing, disabled, injected, and caller-override behavior.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tests/unit/test_ai_model_provider_binding.py
CHANGELOG: v1.0.0-C1B-R2 certifies provider-neutral binding without network execution.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2.
"""
import pytest

from tools.eos.intelligence.domain.ai_model_provider_binding import AIModelProviderBindingError, ServerOwnedModelProviderBinding


class Provider:
    def execute(self, request: object) -> object: return request


def test_injected_binding_is_server_owned_and_deterministic() -> None:
    resolver = ServerOwnedModelProviderBinding.from_injected(provider=Provider(), provider_id="local", model_id="model-a")
    binding = resolver.resolve()
    assert (binding.provider_id, binding.model_id) == ("local", "model-a")
    with pytest.raises(AIModelProviderBindingError): resolver.resolve(requested_provider_id="other")


def test_missing_and_disabled_bindings_fail_closed() -> None:
    with pytest.raises(AIModelProviderBindingError, match="MISSING"): ServerOwnedModelProviderBinding().resolve()
    resolver = ServerOwnedModelProviderBinding.from_injected(provider=Provider(), enabled=False)
    with pytest.raises(AIModelProviderBindingError, match="DISABLED"): resolver.resolve()


# ARTIFACT: test_ai_model_provider_binding.py
# VERSION: v1.0.0-C1B-R2
# END OF WILSY OS SOVEREIGN ARTIFACT
