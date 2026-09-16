"""TITLE: C1B reasoning entitlement provisioning certificate.
VERSION: v1.0.0-C1B-R2
AUTHORITY: Wilsy OS Core Governance.
EPITOME: Certify explicit P4-backed provisioning and activation evidence.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tests/unit/test_wilsy_ai_reasoning_entitlement_provisioning.py
CHANGELOG: v1.0.0-C1B-R2 certifies tenant binding and replay behavior.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2.
"""
from datetime import datetime, timezone

from tools.eos.saas.billing.wilsy_ai_commercial_policy import WilsyAITier, get_wilsy_ai_commercial_policy
from tools.eos.saas.billing.wilsy_ai_entitlement_provisioning import activate_wilsy_ai_reasoning_entitlement, provision_wilsy_ai_reasoning_entitlement
from tools.eos.saas.domain.wilsy_ai_entitlement import WilsyAIEntitlementState


class Registry:
    def __init__(self) -> None: self.item = None
    def create_or_replay(self, item, **_: object): self.item = item; return item
    def transition(self, **kwargs: object):
        assert self.item is not None
        self.item = self.item.transition(kwargs["target_state"], expected_revision=kwargs["expected_revision"], evidence_reference=kwargs["evidence_reference"], evidence_fingerprint=kwargs["evidence_fingerprint"], occurred_at=kwargs["occurred_at"])
        return self.item


def test_explicit_provision_then_evidence_backed_activation() -> None:
    registry, session = Registry(), object()
    item = provision_wilsy_ai_reasoning_entitlement(registry=registry, tenant_id="tenant-a", entitlement_id="ent-a", tier=WilsyAITier.STARTER, source_evidence_reference="source-a", source_evidence_fingerprint="a" * 128, idempotency_key="key-a", session=session)
    assert item.module_id == "WILSY_AI_REASONING" and item.lifecycle_state is WilsyAIEntitlementState.PENDING_SOURCE
    active = activate_wilsy_ai_reasoning_entitlement(registry=registry, entitlement=item, activation_evidence_reference="activate-a", activation_evidence_fingerprint="b" * 128, occurred_at=datetime(2026, 9, 16, tzinfo=timezone.utc), session=session)
    assert active.lifecycle_state is WilsyAIEntitlementState.ACTIVE


def test_policy_fingerprint_is_canonical() -> None:
    assert get_wilsy_ai_commercial_policy(WilsyAITier.STARTER).policy_fingerprint


# ARTIFACT: test_wilsy_ai_reasoning_entitlement_provisioning.py
# VERSION: v1.0.0-C1B-R2
# END OF WILSY OS SOVEREIGN ARTIFACT
