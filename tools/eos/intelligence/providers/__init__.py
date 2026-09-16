"""WILSY AI infrastructure provider adapters.

TITLE: WILSY AI Provider Adapter Package
VERSION: v1.0.0-C1B-R23
AUTHORITY: Wilsy OS Core Governance
EPITOME: Isolate replaceable vendor SDK translation from provider-neutral
         reasoning, entitlement, capacity, and evidence authorities.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tools/eos/intelligence/providers/__init__.py
COLLABORATION / OWNERSHIP: C1B consumes ModelProvider implementations; server
                            runtime configuration selects an adapter.
CERTIFICATION / UPDATE DATE: 2026-09-16
CHANGELOG: v1.0.0-C1B-R23 establishes the infrastructure-only provider package.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2.
SECURITY / PRIVACY POSTURE: Credentials and provider payloads remain transient.
TENANT BOUNDARY: No tenant authority or caller-selected provider identity.
AUTHORITY BOUNDARY: Vendor SDK translation and bounded failure mapping only.
FINANCIAL AUTHORITY BOUNDARY: Kennel EOS exclusively owns financial execution.
FAIL-CLOSED DECLARATION: Unsupported or malformed provider configuration denies.
"""

from .openai_responses_provider import OpenAIResponsesProvider
from .reasoning_provider_runtime import (
    ReasoningProviderConfigurationError,
    build_reasoning_provider_binding_from_environment,
)

__all__ = [
    "OpenAIResponsesProvider",
    "ReasoningProviderConfigurationError",
    "build_reasoning_provider_binding_from_environment",
]

# ARTIFACT: tools/eos/intelligence/providers/__init__.py
# VERSION: v1.0.0-C1B-R23
# AUTHORITY BOUNDARY: replaceable provider infrastructure only
# TENANT POSTURE: no caller-selected provider authority
# FAIL-CLOSED POSTURE: malformed configuration is inactive
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively
# END OF WILSY OS SOVEREIGN ARTIFACT
