"""TITLE: WILSY AI Usage Admission Authority.
VERSION: v1.0.0-C1B-R2
AUTHORITY: Wilsy OS Core Governance.
EPITOME: Compose P4 entitlement, P6B complete usage, P6A observed capacity,
         and durable held reservations into one atomic admission decision.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tools/eos/saas/billing/wilsy_ai_usage_admission_authority.py
COLLABORATION / OWNERSHIP: C1B authority; provider execution is a future
                            caller phase after this reservation commits.
CERTIFICATION / UPDATE DATE: 2026-09-16
CHANGELOG: v1.0.0-C1B-R2 establishes fail-closed reservation composition and
           reconciliation-required uncertainty semantics.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2.
SECURITY / PRIVACY POSTURE: No provider calls, prompts, secrets, or money.
TENANT BOUNDARY: Capacity and reservations are exact tenant-scoped facts.
AUTHORITY BOUNDARY: Admission reservation only; no usage or provider result.
FINANCIAL AUTHORITY BOUNDARY: Kennel EOS exclusively owns financial execution.
FAIL-CLOSED DECLARATION: Capacity races and upstream drift deny admission.
"""
from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Final
from uuid import uuid4

from tools.eos.saas.domain.wilsy_ai_usage_admission import WilsyAIUsageAdmission, WilsyAIUsageAdmissionState

VERSION: Final[str] = "v1.0.0-C1B-R2"
MODULE_ID: Final[str] = "WILSY_AI_REASONING"


class WilsyAIUsageAdmissionAuthorityError(ValueError):
    """Raised when canonical admission cannot be established."""


class WilsyAIUsageAdmissionAuthority:
    """Reserve one reasoning request under caller-owned transaction state."""

    __slots__ = ("_capacity", "_registry")

    def __init__(self, *, capacity_orchestrator: Any, admission_registry: Any) -> None:
        if capacity_orchestrator is None or admission_registry is None:
            raise WilsyAIUsageAdmissionAuthorityError("C1B_ADMISSION_DEPENDENCIES_REQUIRED")
        self._capacity, self._registry = capacity_orchestrator, admission_registry

    def reserve(self, *, tenant_id: str, entitlement_id: str, idempotency_key: str, session: Any, as_of: datetime, admission_id: str | None = None, reserved_request_units: int = 1) -> WilsyAIUsageAdmission:
        """Derive effective capacity and persist a reservation; never commits."""
        if not isinstance(tenant_id, str) or not tenant_id.strip() or not isinstance(idempotency_key, str) or not idempotency_key.strip() or session is None or not isinstance(as_of, datetime) or as_of.tzinfo is None or as_of.utcoffset() is None:
            raise WilsyAIUsageAdmissionAuthorityError("C1B_ADMISSION_INPUT_INVALID")
        if not isinstance(reserved_request_units, int) or isinstance(reserved_request_units, bool) or reserved_request_units <= 0:
            raise WilsyAIUsageAdmissionAuthorityError("C1B_ADMISSION_UNITS_INVALID")
        try:
            capacity = self._capacity.derive_capacity(tenant_id=tenant_id, entitlement_id=entitlement_id, as_of=as_of, session=session)
            window_start = capacity.daily_window_start
            held = self._registry.held_request_units(tenant_id=tenant_id, entitlement_id=entitlement_id, window_start=window_start, session=session)
            available = max(0, capacity.daily_remaining_request_units - held)
            now = as_of.astimezone(timezone.utc)
            admission = WilsyAIUsageAdmission(tenant_id=tenant_id, admission_id=admission_id or f"adm-{uuid4().hex}", idempotency_key=idempotency_key, entitlement_id=entitlement_id, module_id=capacity.module_id, entitlement_revision=capacity.entitlement_revision, entitlement_fingerprint=capacity.entitlement_fingerprint, window_start=window_start, window_end=capacity.daily_window_end, reserved_request_units=reserved_request_units, state=WilsyAIUsageAdmissionState.RESERVED, created_at=now, updated_at=now)
            return self._registry.reserve(admission, available_request_units=available, session=session)
        except WilsyAIUsageAdmissionAuthorityError:
            raise
        except Exception as error:
            raise WilsyAIUsageAdmissionAuthorityError("C1B_ADMISSION_REJECTED") from error

    reserve_admission = reserve


__all__ = ["VERSION", "MODULE_ID", "WilsyAIUsageAdmissionAuthority", "WilsyAIUsageAdmissionAuthorityError"]

# ARTIFACT: wilsy_ai_usage_admission_authority.py
# VERSION: v1.0.0-C1B-R2
# AUTHORITY BOUNDARY: atomic tenant-scoped admission reservation only
# TENANT POSTURE: canonical P4/P6 identity and explicit tenant predicates
# FAIL-CLOSED POSTURE: active held reservations consume capacity; uncertainty holds
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively
# END OF WILSY OS SOVEREIGN ARTIFACT
