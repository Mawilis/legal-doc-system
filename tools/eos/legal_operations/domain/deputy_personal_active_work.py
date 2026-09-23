"""Binding-scoped personal active work for Legal Operations deputies.

TITLE: WILSY OS Deputy Personal Active Work and Field Capability Projection
VERSION: v1.1.0-L8-6D-DEPUTY-PERSONAL-FIELD-CAPABILITY
AUTHORITY: Deterministic read-only projection of one bound deputy's active attempts.
EPITOME: Resolve one immutable L8-6B principal-to-Deputy binding, derive the
         canonical deputy_id, compose deterministic L8-5 current ServiceAttempt
         models, return only ALLOCATED/ATTEMPTED attempts owned by that exact
         bound deputy, and optionally bind each current attempt to its exact P2
         snapshot locator plus P5M state-valid next-command descriptor without
         inventing IAM, service, return, billing, AI, payment, or settlement truth.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tools/eos/legal_operations/domain/deputy_personal_active_work.py
COLLABORATION / OWNERSHIP: L8-6B owns immutable principal-to-Deputy identity
                            binding; P1/P2/L8-0/L8-5 own lifecycle/history/current
                            ServiceAttempt truth; P2 owns snapshot evidence
                            identity; P5M owns field capability mapping; this
                            module composes personal queue/capability reads only.
                            IAM/HTTP/client remain separate gates.
CERTIFICATION / UPDATE DATE: 2026-09-23
CHANGELOG: 2026-09-23 v1.1.0-L8-6D-DEPUTY-PERSONAL-FIELD-CAPABILITY
           adds a binding-scoped personal field-capability projection that
           reuses certified L8-6C personal active work, resolves each exact
           current P2 snapshot evidence locator under the caller-owned session,
           applies the P5M state-capability mapping, and rejects the whole result
           on locator/projection failure without partial capability fallback.
           2026-09-23 v1.0.1-L8-6C-DEPUTY-PERSONAL-ACTIVE-WORK
           makes the public aggregate independently validate canonical tenant,
           principal and deputy identities plus immutable tuple queue shape;
           binding-derived membership semantics remain unchanged.
           2026-09-23 v1.0.0-L8-6C-DEPUTY-PERSONAL-ACTIVE-WORK
           establishes binding-derived deputy identity, exact-tenant current
           attempt enumeration, ALLOCATED/ATTEMPTED-only personal membership,
           deterministic attempt ordering, session propagation, and fail-closed
           binding/read-model/type/tenant/state validation.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2; ISO 27001.
SECURITY / PRIVACY POSTURE: Projects canonical opaque attempt identifiers and,
                             for the field-capability read only, one exact
                             SHA3-512 P2 snapshot locator plus state-valid command
                             kinds. No credentials, client profile, geolocation,
                             payment, provider secret, or AI content is introduced.
TENANT BOUNDARY: Binding resolution and every L8-5 read use the same explicit
                 tenant_id; only attempts whose canonical deputy_id equals the
                 bound deputy identity are returned.
AUTHORITY BOUNDARY: Read projection only. The binding is identity evidence, not
                    authorization; callers must independently prove current IAM.
                    A field capability means only that the current P1 state can
                    accept an existing command kind. It does not grant or execute
                    mutation, service, return, billing, invoice, payment, or settlement.
FINANCIAL AUTHORITY BOUNDARY: No financial semantics; Kennel EOS exclusively
                              owns financial execution and settlement.
TRANSACTION BOUNDARY: Caller-owned read session is forwarded unchanged to L8-6B
                      binding resolution, L8-5 enumeration, and every P2 locator
                      read. This module starts, commits, aborts, and retries nothing.
FAIL-CLOSED DECLARATION: Missing/corrupt binding, read-model failure, type or
                         tenant drift, unsupported attempt state, principal
                         mismatch, P2 locator failure, or P5M capability mismatch
                         rejects the whole projection without fallback, partial
                         capabilities, or tenant-wide queue substitution.
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
from tools.eos.legal_operations.domain.process_service_field_evidence_projection import (
    FieldCommandCapabilityEntry,
    ProcessServiceFieldEvidenceProjectionError,
    project_field_command_capability,
)
from tools.eos.legal_operations.registry.deputy_principal_binding_registry import (
    DeputyPrincipalBindingNotFoundError,
    DeputyPrincipalBindingPersistedRecordInvalidError,
    DeputyPrincipalBindingRegistry,
    DeputyPrincipalBindingRegistryError,
)
from tools.eos.legal_operations.registry.legal_operations_lifecycle_registry import (
    LegalOperationsLifecycleRegistry,
    LegalOperationsLifecycleRegistryError,
)


VERSION: Final[str] = "v1.1.0-L8-6D-DEPUTY-PERSONAL-FIELD-CAPABILITY"
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


@dataclass(frozen=True, slots=True)
class DeputyPersonalFieldCapabilities:
    """Immutable state-capability projection for one bound deputy principal.

    capabilities has one entry for every current active attempt in the
    underlying L8-6C personal-work result and preserves that deterministic order.
    The entries contain opaque P2 locators and state-valid command kinds only.
    They are not IAM decisions and cannot execute or guarantee a command.
    """

    tenant_id: str
    principal_id: str
    deputy_id: str
    capabilities: tuple[FieldCommandCapabilityEntry, ...]

    def __post_init__(self) -> None:
        """Revalidate identity, immutable shape and exact deputy capability scope."""
        _tenant(self.tenant_id)
        _identity("principal_id", self.principal_id)
        _identity("deputy_id", self.deputy_id)
        if not isinstance(self.capabilities, tuple):
            _fail("L8_6D_FIELD_CAPABILITIES_INVALID")
        for value in self.capabilities:
            if type(value) is not FieldCommandCapabilityEntry:
                _fail("L8_6D_FIELD_CAPABILITY_INVALID")
            if value.tenant_id != self.tenant_id:
                _fail("L8_6D_TENANT_MISMATCH")
            if value.deputy_id != self.deputy_id:
                _fail("L8_6D_DEPUTY_SCOPE_MISMATCH")

    def to_dict(self) -> dict[str, object]:
        """Serialize exact bounded capabilities without authorization claims."""
        return {
            "tenant_id": self.tenant_id,
            "principal_id": self.principal_id,
            "deputy_id": self.deputy_id,
            "capabilities": [value.to_dict() for value in self.capabilities],
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


def get_deputy_personal_field_capabilities(
    *,
    tenant_id: str,
    principal_id: str,
    binding_collection: Any,
    lifecycle_collection: Any,
    session: Any = None,
) -> DeputyPersonalFieldCapabilities:
    """Return exact state-valid field command descriptors for one bound deputy.

    The function first resolves the already-certified L8-6C personal active-work
    projection. For each current ALLOCATED/ATTEMPTED ServiceAttempt, it asks P2
    for the exact persisted evidence identity of that current canonical snapshot
    and then asks P5M for the state-valid command-kind descriptor.

    Every locator read receives the caller-owned session unchanged. Any locator
    absence/corruption/ambiguity or capability mismatch rejects the entire
    projection; no partial list is returned. This function performs no IAM
    decision and no lifecycle/evidence/return/financial mutation.
    """
    personal = get_deputy_personal_active_work(
        tenant_id=tenant_id,
        principal_id=principal_id,
        binding_collection=binding_collection,
        lifecycle_collection=lifecycle_collection,
        session=session,
    )
    capabilities: list[FieldCommandCapabilityEntry] = []
    for model in personal.active_attempts:
        if type(model.current) is not ServiceAttempt:
            _fail("L8_6D_ATTEMPT_MODEL_INVALID")
        current = cast(ServiceAttempt, model.current)
        try:
            locator = LegalOperationsLifecycleRegistry.get_snapshot_evidence_identity(
                current,
                lifecycle_collection,
                session=session,
            )
        except LegalOperationsLifecycleRegistryError as error:
            _fail("L8_6D_SNAPSHOT_LOCATOR_UNAVAILABLE", error)
        try:
            capability = project_field_command_capability(
                attempt=current,
                current_evidence_identity=locator,
            )
        except ProcessServiceFieldEvidenceProjectionError as error:
            _fail("L8_6D_FIELD_CAPABILITY_INVALID", error)
        capabilities.append(capability)

    return DeputyPersonalFieldCapabilities(
        tenant_id=personal.tenant_id,
        principal_id=personal.principal_id,
        deputy_id=personal.deputy_id,
        capabilities=tuple(capabilities),
    )


__all__ = [
    "VERSION",
    "DeputyPersonalActiveWork",
    "DeputyPersonalActiveWorkError",
    "DeputyPersonalFieldCapabilities",
    "get_deputy_personal_active_work",
    "get_deputy_personal_field_capabilities",
]


# ARTIFACT: deputy_personal_active_work.py
# VERSION: v1.1.0-L8-6D-DEPUTY-PERSONAL-FIELD-CAPABILITY
# AUTHORITY BOUNDARY: binding-scoped deterministic personal active-work and state-capability read projection only
# TENANT POSTURE: exact tenant/principal binding plus bound-deputy current ServiceAttempt filtering and exact P2 locator scope
# FAIL-CLOSED POSTURE: binding/read-model/type/tenant/state/locator/capability drift rejects whole projection without fallback
# FINANCIAL EXECUTION AUTHORITY: none; Kennel EOS remains exclusive
# END OF WILSY OS SOVEREIGN ARTIFACT
