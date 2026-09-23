"""Binding-scoped personal active work for Legal Operations deputies.

TITLE: WILSY OS Deputy Personal Active Work Projection
VERSION: v1.0.1-L8-6C-DEPUTY-PERSONAL-ACTIVE-WORK
AUTHORITY: Deterministic read-only projection of one bound deputy's active attempts.
EPITOME: Resolve one immutable L8-6B principal-to-Deputy binding, derive the
         canonical deputy_id, compose deterministic L8-5 current ServiceAttempt
         models, and return only ALLOCATED/ATTEMPTED attempts owned by that
         exact bound deputy without inventing urgency, distance, routing,
         completion, return, billing, AI, payment, or financial truth.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tools/eos/legal_operations/domain/deputy_personal_active_work.py
COLLABORATION / OWNERSHIP: L8-6B owns immutable principal-to-Deputy identity
                            binding; P1/P2/L8-0/L8-5 own lifecycle/history/current
                            ServiceAttempt truth; this module owns personal queue
                            membership only. IAM/HTTP/client remain separate gates.
CERTIFICATION / UPDATE DATE: 2026-09-23
CHANGELOG: 2026-09-23 v1.0.1-L8-6C-DEPUTY-PERSONAL-ACTIVE-WORK
           makes the public aggregate independently validate canonical tenant,
           principal and deputy identities plus immutable tuple queue shape;
           binding-derived membership semantics remain unchanged.
           2026-09-23 v1.0.0-L8-6C-DEPUTY-PERSONAL-ACTIVE-WORK
           establishes binding-derived deputy identity, exact-tenant current
           attempt enumeration, ALLOCATED/ATTEMPTED-only personal membership,
           deterministic attempt ordering, session propagation, and fail-closed
           binding/read-model/type/tenant/state validation.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2; ISO 27001.
SECURITY / PRIVACY POSTURE: Projects only canonical opaque attempt identifiers
                             already present in Legal Operations evidence. No
                             credentials, client profile, geolocation, payment,
                             provider, secret, or AI content is introduced.
TENANT BOUNDARY: Binding resolution and every L8-5 read use the same explicit
                 tenant_id; only attempts whose canonical deputy_id equals the
                 bound deputy identity are returned.
AUTHORITY BOUNDARY: Read projection only. The binding is identity evidence, not
                    authorization; callers must independently prove current IAM.
                    Queue membership grants no attempt mutation, service,
                    completion, return, billing, invoice, payment, or settlement.
FINANCIAL AUTHORITY BOUNDARY: No financial semantics; Kennel EOS exclusively
                              owns financial execution and settlement.
TRANSACTION BOUNDARY: Caller-owned read session is forwarded unchanged to L8-6B
                      binding resolution and L8-5. This module starts, commits,
                      aborts, and retries nothing.
FAIL-CLOSED DECLARATION: Missing/corrupt binding, read-model failure, type or
                         tenant drift, unsupported attempt state, or principal
                         mismatch rejects the whole projection without fallback
                         or tenant-wide queue substitution.
"""
from __future__ import annotations

from dataclasses import dataclass
import re
from typing import Any, Final, NoReturn, cast

from tools.eos.legal_operations.domain.legal_operations_lifecycle import (
    ServiceAttempt,
    ServiceAttemptState,
)
from tools.eos.legal_operations.domain.legal_operations_read_model import (
    LegalOperationsEntityReadModel,
    LegalOperationsReadModelError,
    list_entity_read_models,
)
from tools.eos.legal_operations.registry.deputy_principal_binding_registry import (
    DeputyPrincipalBindingNotFoundError,
    DeputyPrincipalBindingPersistedRecordInvalidError,
    DeputyPrincipalBindingRegistry,
    DeputyPrincipalBindingRegistryError,
)


VERSION: Final[str] = "v1.0.1-L8-6C-DEPUTY-PERSONAL-ACTIVE-WORK"
_IDENTITY: Final[re.Pattern[str]] = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._:-]{0,127}$")
_FORBIDDEN_TENANTS: Final[frozenset[str]] = frozenset(
    {"default", "global", "global_root", "root", "master", "*"}
)


class DeputyPersonalActiveWorkError(RuntimeError):
    """Stable fail-closed L8-6C personal-work projection failure."""

    def __init__(self, code: str) -> None:
        """Create one bounded personal-work failure code."""
        self.code = code
        super().__init__(code)


def _fail(code: str, cause: BaseException | None = None) -> NoReturn:
    """Raise one stable projection error while retaining technical cause."""
    error = DeputyPersonalActiveWorkError(code)
    if cause is None:
        raise error
    raise error from cause


def _identity(name: str, value: object) -> str:
    """Require one exact opaque identity without normalization or defaults."""
    if not isinstance(value, str) or _IDENTITY.fullmatch(value) is None:
        _fail(f"L8_6C_{name.upper()}_INVALID")
    return cast(str, value)


def _tenant(value: object) -> str:
    """Require one canonical non-pseudo tenant identity."""
    tenant_id = _identity("tenant_id", value)
    if tenant_id.casefold() in _FORBIDDEN_TENANTS:
        _fail("L8_6C_TENANT_ID_INVALID")
    return tenant_id


@dataclass(frozen=True, slots=True)
class DeputyPersonalActiveWork:
    """Immutable personal active-work projection for one bound deputy principal.

    The aggregate contains only current ServiceAttempt read models whose
    canonical deputy_id equals the bound deputy_id and whose state is ALLOCATED
    or ATTEMPTED. Result order follows L8-5 canonical attempt identity order.

    This aggregate is not authorization and owns no lifecycle mutation,
    service outcome, return, billing, payment, financial execution, or
    settlement semantics.
    """

    tenant_id: str
    principal_id: str
    deputy_id: str
    active_attempts: tuple[LegalOperationsEntityReadModel, ...]

    def __post_init__(self) -> None:
        """Revalidate exact identity, immutable shape and queue membership."""
        _tenant(self.tenant_id)
        _identity("principal_id", self.principal_id)
        _identity("deputy_id", self.deputy_id)
        if not isinstance(self.active_attempts, tuple):
            _fail("L8_6C_ACTIVE_ATTEMPTS_INVALID")
        for model in self.active_attempts:
            if model.tenant_id != self.tenant_id:
                _fail("L8_6C_TENANT_MISMATCH")
            if model.entity_type != "ServiceAttempt":
                _fail("L8_6C_ATTEMPT_MODEL_INVALID")
            if type(model.current) is not ServiceAttempt:
                _fail("L8_6C_ATTEMPT_MODEL_INVALID")
            current = cast(ServiceAttempt, model.current)
            if current.deputy_id != self.deputy_id:
                _fail("L8_6C_DEPUTY_SCOPE_MISMATCH")
            if current.state not in {
                ServiceAttemptState.ALLOCATED,
                ServiceAttemptState.ATTEMPTED,
            }:
                _fail("L8_6C_ACTIVE_MEMBERSHIP_INVALID")

    def to_dict(self) -> dict[str, object]:
        """Serialize exact current models without inventing additional fields."""
        return {
            "tenant_id": self.tenant_id,
            "principal_id": self.principal_id,
            "deputy_id": self.deputy_id,
            "active_attempts": [
                model.to_dict() for model in self.active_attempts
            ],
        }


def get_deputy_personal_active_work(
    *,
    tenant_id: str,
    principal_id: str,
    binding_collection: Any,
    lifecycle_collection: Any,
    session: Any = None,
) -> DeputyPersonalActiveWork:
    """Return exact active ServiceAttempt work for one bound deputy principal.

    The immutable L8-6B registry first resolves the exact tenant/principal
    binding under the caller-owned session. Its deputy_id is the only deputy
    identity accepted by this projection. L8-5 then returns deterministic
    current-plus-history ServiceAttempt models for the exact tenant.

    Only bound-deputy ALLOCATED and ATTEMPTED current states are included.
    Bound-deputy COMPLETED, NOT_COMPLETED and CANCELLED attempts are excluded.
    Attempts assigned to any other deputy are excluded regardless of state.
    Any binding corruption or tenant-wide ServiceAttempt evidence corruption
    rejects the entire result rather than yielding partial personal work.

    Current IAM is intentionally not inferred from the immutable binding.
    Callers must separately prove ACTIVE principal, ACTIVE membership,
    tenant_deputy eligibility and ACTIVE DEPUTY assignment before invoking
    this projection.
    """
    try:
        binding = DeputyPrincipalBindingRegistry.resolve_by_principal(
            tenant_id,
            principal_id,
            binding_collection,
            session=session,
        )
    except DeputyPrincipalBindingNotFoundError as error:
        _fail("L8_6C_BINDING_REQUIRED", error)
    except DeputyPrincipalBindingPersistedRecordInvalidError as error:
        _fail("L8_6C_BINDING_INVALID", error)
    except DeputyPrincipalBindingRegistryError as error:
        _fail("L8_6C_BINDING_UNAVAILABLE", error)

    if binding.tenant_id != tenant_id or binding.principal_id != principal_id:
        _fail("L8_6C_BINDING_SCOPE_MISMATCH")

    try:
        models = list_entity_read_models(
            tenant_id=tenant_id,
            entity_type="ServiceAttempt",
            lifecycle_collection=lifecycle_collection,
            session=session,
        )
    except LegalOperationsReadModelError as error:
        _fail("L8_6C_ATTEMPT_EVIDENCE_UNAVAILABLE", error)

    active: list[LegalOperationsEntityReadModel] = []
    for model in models:
        if model.tenant_id != tenant_id:
            _fail("L8_6C_TENANT_MISMATCH")
        if model.entity_type != "ServiceAttempt" or type(model.current) is not ServiceAttempt:
            _fail("L8_6C_ATTEMPT_MODEL_INVALID")
        current = cast(ServiceAttempt, model.current)

        if current.state not in {
            ServiceAttemptState.ALLOCATED,
            ServiceAttemptState.ATTEMPTED,
            ServiceAttemptState.COMPLETED,
            ServiceAttemptState.NOT_COMPLETED,
            ServiceAttemptState.CANCELLED,
        }:
            _fail("L8_6C_ATTEMPT_STATE_UNSUPPORTED")

        if current.deputy_id != binding.deputy_id:
            continue
        if current.state in {
            ServiceAttemptState.ALLOCATED,
            ServiceAttemptState.ATTEMPTED,
        }:
            active.append(model)

    return DeputyPersonalActiveWork(
        tenant_id=tenant_id,
        principal_id=principal_id,
        deputy_id=binding.deputy_id,
        active_attempts=tuple(active),
    )


__all__ = [
    "VERSION",
    "DeputyPersonalActiveWork",
    "DeputyPersonalActiveWorkError",
    "get_deputy_personal_active_work",
]


# ARTIFACT: deputy_personal_active_work.py
# VERSION: v1.0.1-L8-6C-DEPUTY-PERSONAL-ACTIVE-WORK
# AUTHORITY BOUNDARY: binding-scoped deterministic personal active-work projection only
# TENANT POSTURE: exact tenant/principal binding plus bound-deputy ServiceAttempt filtering
# FAIL-CLOSED POSTURE: missing/corrupt binding, read-model/type/tenant/state drift rejects without fallback
# FINANCIAL EXECUTION AUTHORITY: none; Kennel EOS remains exclusive
# END OF WILSY OS SOVEREIGN ARTIFACT
