"""Wilsy OS M13-P6C canonical WILSY AI capacity runtime composition.

TITLE: WILSY AI Usage Capacity Runtime Orchestrator
VERSION: v1.0.0-M13-P6C
AUTHORITY: Wilsy OS Core Governance
EPITOME: Compose caller-supplied P4 entitlement truth, P6B bounded raw
         observations, and the frozen P6A capacity derivation in one explicit
         transaction snapshot without creating a second authority.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tools/eos/saas/billing/wilsy_ai_usage_capacity_orchestrator.py
COLLABORATION / OWNERSHIP: P4 owns durable entitlement lifecycle truth; P5A
                            owns immutable observations; P5B/P6B own durable
                            bounded retrieval; P6A owns capacity derivation;
                            this module owns composition only. Kennel EOS owns
                            financial execution and settlement.
CERTIFICATION / UPDATE DATE: 2026-09-13
CHANGELOG: v1.0.0-M13-P6C establishes caller-session composition from the
           canonical P4 registry through P6B retrieval into unchanged P6A.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2.
SECURITY / PRIVACY POSTURE: No network, secrets, providers, clients, metrics,
                             persistence writes, or financial operations.
TENANT BOUNDARY: Tenant and entitlement identifiers are explicit; the caller
                 entitlement ID is only a tenant-scoped locator.
AUTHORITY BOUNDARY: Runtime composition only; no entitlement, usage, quota,
                    commercial, invoice, payment, execution, or settlement
                    authority.
FINANCIAL AUTHORITY BOUNDARY: Kennel EOS exclusively owns execution/settlement.
TRANSACTION BOUNDARY: Caller supplies an already-active session/transaction;
                      this module never starts, commits, aborts, or retries.
FAIL-CLOSED DECLARATION: Invalid composition inputs and inactive caller
                         snapshots reject; upstream P4, P6B, and P6A governed
                         failures are propagated unchanged.
"""
from __future__ import annotations

from datetime import datetime
from typing import Any, Final

from tools.eos.saas.billing.wilsy_ai_entitlement_registry import (
    WilsyAIEntitlementRegistry,
)
from tools.eos.saas.billing.wilsy_ai_usage_capacity import (
    WilsyAIUsageCapacity,
    derive_wilsy_ai_usage_capacity,
)
from tools.eos.saas.billing.wilsy_ai_usage_observation_registry import (
    WilsyAIUsageObservationRegistry,
)
from tools.eos.saas.domain.wilsy_ai_entitlement import WilsyAIEntitlement


VERSION: Final[str] = "v1.0.0-M13-P6C"
_FORBIDDEN_TENANTS: Final[frozenset[str]] = frozenset(
    {"default", "global", "root", "*", "global_root"}
)


class WilsyAIUsageCapacityOrchestratorError(ValueError):
    """Raised when P6C composition cannot establish its explicit boundary."""


def _require_tenant(value: object) -> str:
    if not isinstance(value, str) or not value or value != value.strip():
        raise WilsyAIUsageCapacityOrchestratorError("M13P6C_TENANT_REQUIRED")
    if value.lower() in _FORBIDDEN_TENANTS:
        raise WilsyAIUsageCapacityOrchestratorError("M13P6C_TENANT_FORBIDDEN")
    return value


def _require_as_of(value: object) -> datetime:
    if not isinstance(value, datetime) or value.tzinfo is None or value.utcoffset() is None:
        raise WilsyAIUsageCapacityOrchestratorError("M13P6C_AS_OF_INVALID")
    return value


def _require_active_session(session: object) -> None:
    if session is None:
        raise WilsyAIUsageCapacityOrchestratorError("M13P6C_SESSION_REQUIRED")
    state = getattr(session, "in_transaction", False)
    if callable(state):
        state = state()
    if state is not True:
        raise WilsyAIUsageCapacityOrchestratorError("M13P6C_TRANSACTION_REQUIRED")


class WilsyAIUsageCapacityOrchestrator:
    """Compose P4, P6B, and P6A under one caller-owned transaction snapshot.

    The P4 registry is queried first.  Its returned entitlement, rather than
    any caller-supplied commercial or module values, supplies the module ID,
    lifecycle revision, and entitlement fingerprint forwarded to P6B.  The
    resulting tuple is passed unchanged to P6A, which remains the sole
    capacity authority.  All registry and derivation exceptions retain their
    original governed type and code.
    """

    __slots__ = ("_entitlement_registry", "_observation_registry")

    def __init__(self, *, entitlement_registry: Any, observation_registry: Any) -> None:
        if entitlement_registry is None or observation_registry is None:
            raise WilsyAIUsageCapacityOrchestratorError("M13P6C_REGISTRIES_REQUIRED")
        if not callable(getattr(entitlement_registry, "get", None)):
            raise WilsyAIUsageCapacityOrchestratorError("M13P6C_ENTITLEMENT_REGISTRY_INVALID")
        if not callable(getattr(observation_registry, "get_bounded_for_p6a", None)):
            raise WilsyAIUsageCapacityOrchestratorError("M13P6C_OBSERVATION_REGISTRY_INVALID")
        self._entitlement_registry = entitlement_registry
        self._observation_registry = observation_registry

    @classmethod
    def from_collections(
        cls,
        *,
        entitlement_collection: Any,
        observation_collection: Any,
    ) -> "WilsyAIUsageCapacityOrchestrator":
        """Compose canonical P4/P6B registries from injected Mongo collections.

        Collection construction is dependency injection only; no connection,
        client, session, index, or transaction is created by this factory.
        The caller still supplies the active session to ``derive_capacity``.
        """
        if entitlement_collection is None or observation_collection is None:
            raise WilsyAIUsageCapacityOrchestratorError("M13P6C_COLLECTIONS_REQUIRED")
        return cls(
            entitlement_registry=WilsyAIEntitlementRegistry(entitlement_collection),
            observation_registry=WilsyAIUsageObservationRegistry(observation_collection),
        )

    def derive_capacity(
        self,
        *,
        tenant_id: str,
        entitlement_id: str,
        as_of: datetime,
        session: Any,
    ) -> WilsyAIUsageCapacity:
        """Return unchanged P6A capacity from canonical P4 and P6B evidence.

        ``entitlement_id`` is only a locator.  Module identity, lifecycle
        revision, and fingerprint are read from the P4 result and cannot be
        overridden by the caller.  The same active session is passed to both
        registries.  This method performs no writes and owns no transaction
        lifecycle; P4/P6B/P6A failures are deliberately not translated.
        """
        tenant = _require_tenant(tenant_id)
        if not isinstance(entitlement_id, str) or not entitlement_id or entitlement_id != entitlement_id.strip():
            raise WilsyAIUsageCapacityOrchestratorError("M13P6C_ENTITLEMENT_ID_REQUIRED")
        snapshot = _require_as_of(as_of)
        _require_active_session(session)
        entitlement = self._entitlement_registry.get(
            tenant_id=tenant,
            entitlement_id=entitlement_id,
            session=session,
        )
        if not isinstance(entitlement, WilsyAIEntitlement):
            raise WilsyAIUsageCapacityOrchestratorError("M13P6C_ENTITLEMENT_INVALID")
        observations = self._observation_registry.get_bounded_for_p6a(
            tenant_id=tenant,
            entitlement_id=entitlement.entitlement_id,
            module_id=entitlement.module_id,
            expected_entitlement_revision=entitlement.lifecycle_revision,
            expected_entitlement_fingerprint=entitlement.fingerprint,
            as_of=snapshot,
            session=session,
        )
        return derive_wilsy_ai_usage_capacity(
            entitlement=entitlement,
            observations=observations,
            as_of=snapshot,
        )


__all__ = [
    "VERSION",
    "WilsyAIUsageCapacityOrchestrator",
    "WilsyAIUsageCapacityOrchestratorError",
]

# ARTIFACT: wilsy_ai_usage_capacity_orchestrator.py
# VERSION: v1.0.0-M13-P6C
# AUTHORITY BOUNDARY: P4/P6B/P6A runtime composition only
# TENANT POSTURE: explicit tenant-scoped locator and canonical P4 identity
# FAIL-CLOSED POSTURE: active caller snapshot and upstream governed errors
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively
# END OF WILSY OS SOVEREIGN ARTIFACT
