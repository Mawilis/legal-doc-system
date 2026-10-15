"""TITLE: Tenant Legal Operating Model Command Service Unit Certificate.
VERSION: v1.0.0-CX26-R3-CURRENT-OPERATING-MODEL-COMMAND-UNIT-CERT
AUTHORITY: Direct service-layer certification only.
EPITOME: Proves transaction-bound IAM admission, current reads, deterministic
idempotency, optimistic revision composition, replay, divergence rejection,
and authority boundaries without transport.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tests/unit/test_tenant_legal_operating_model_service.py
COLLABORATION / OWNERSHIP: CX26-R3 command-service certificate.
CERTIFICATION / UPDATE DATE: 2026-10-15
CHANGELOG: v1.0.0 establishes direct service command semantics.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2; ISO 27001.
SECURITY / PRIVACY POSTURE: Synthetic identifiers only.
TENANT BOUNDARY: Exact own-tenant authorization precedes registry access.
AUTHORITY BOUNDARY: Configuration command admission only; no role, workflow,
entitlement, professional, legal-execution, transport, or financial authority.
FINANCIAL AUTHORITY BOUNDARY: None; Kennel EOS exclusively executes finance.
TRANSACTION BOUNDARY: Caller supplies and owns one active transaction.
FAIL-CLOSED DECLARATION: Missing transaction, denial, unavailable authority,
stale revision, divergent replay, malformed command, and replay mismatch reject.
"""
from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Any

import pytest

from tools.eos.auth.principal_authority import PrincipalAuthority
from tools.eos.auth.principal_authority_repository import (
    PrincipalAuthorityNotFoundError,
)
from tools.eos.auth.principal_status import PrincipalStatus
from tools.eos.auth.role_assignment import (
    RoleAssignmentAuthority,
    RoleAssignmentStatus,
)
from tools.eos.auth.role_assignment_repository import (
    RoleAssignmentNotFoundError,
)
from tools.eos.auth.tenant_authorization import (
    TenantAuthorizationDecision,
    TenantAuthorizationReason,
)
from tools.eos.auth.tenant_membership import (
    TenantMembershipAuthority,
    TenantMembershipStatus,
)
from tools.eos.auth.tenant_membership_repository import (
    TenantMembershipNotFoundError,
)
from tools.eos.legal_operations.domain.tenant_legal_operating_model import (
    TenantLegalOperatingModel,
    TenantLegalOperatingModelError,
)
from tools.eos.legal_operations.registry.tenant_legal_operating_model_registry import (
    TenantLegalOperatingModelRegistryNotFoundError,
)
import tools.eos.legal_operations.service.tenant_legal_operating_model_service as service


TENANT = "tenant-operating-model-service"
PRINCIPAL = "principal-operating-model-admin"

BASE = datetime(
    2026,
    10,
    15,
    12,
    0,
    0,
    123456,
    tzinfo=timezone.utc,
)


class Session:
    """Minimal caller-owned transaction marker."""

    def __init__(self, active: bool = True) -> None:
        self.in_transaction = active


class PrincipalReader:
    """Resolve exactly one principal."""

    def __init__(
        self,
        status: PrincipalStatus = PrincipalStatus.ACTIVE,
    ) -> None:
        self.status = status

    def resolve(
        self,
        principal_id: str,
        *,
        session: Any = None,
    ) -> PrincipalAuthority:
        del session
        if principal_id != PRINCIPAL:
            raise PrincipalAuthorityNotFoundError("missing")
        return PrincipalAuthority(
            PRINCIPAL,
            self.status,
            0,
        )


class MembershipReader:
    """Resolve exact own-tenant membership."""

    def __init__(
        self,
        status: TenantMembershipStatus = TenantMembershipStatus.ACTIVE,
    ) -> None:
        self.status = status

    def resolve(
        self,
        principal_id: str,
        tenant_id: str,
        *,
        session: Any = None,
    ) -> TenantMembershipAuthority:
        del session
        if (
            principal_id != PRINCIPAL
            or tenant_id != TENANT
        ):
            raise TenantMembershipNotFoundError("missing")
        return TenantMembershipAuthority(
            PRINCIPAL,
            TENANT,
            self.status,
            0,
        )


class RoleReader:
    """Resolve exactly one current role."""

    def __init__(
        self,
        role_id: str,
        status: RoleAssignmentStatus = RoleAssignmentStatus.ACTIVE,
    ) -> None:
        self.role_id = role_id
        self.status = status

    def resolve(
        self,
        principal_id: str,
        tenant_id: str,
        role_id: str,
        *,
        session: Any = None,
    ) -> RoleAssignmentAuthority:
        del session
        if (
            principal_id != PRINCIPAL
            or tenant_id != TENANT
            or role_id != self.role_id
        ):
            raise RoleAssignmentNotFoundError("missing")
        return RoleAssignmentAuthority(
            PRINCIPAL,
            TENANT,
            self.role_id,
            self.status,
            0,
        )


class FakeRegistry:
    """Deterministic in-memory registry protocol double."""

    def __init__(
        self,
        *,
        current: TenantLegalOperatingModel | None = None,
        replay: TenantLegalOperatingModel | None = None,
        persist_override: TenantLegalOperatingModel | None = None,
    ) -> None:
        self.current = current
        self.replay = replay
        self.persist_override = persist_override
        self.resolve_calls = 0
        self.get_calls = 0
        self.create_calls = 0
        self.created: list[TenantLegalOperatingModel] = []

    def get_by_id(
        self,
        tenant_id: str,
        operating_model_id: str,
        *,
        session: Any,
    ) -> TenantLegalOperatingModel:
        assert session.in_transaction is True
        self.get_calls += 1
        if (
            self.replay is not None
            and self.replay.tenant_id == tenant_id
            and self.replay.operating_model_id == operating_model_id
        ):
            return self.replay
        raise TenantLegalOperatingModelRegistryNotFoundError(
            "CX26_R2_NOT_FOUND"
        )

    def resolve_current(
        self,
        tenant_id: str,
        at: datetime,
        *,
        session: Any,
    ) -> TenantLegalOperatingModel:
        assert session.in_transaction is True
        self.resolve_calls += 1
        if (
            self.current is not None
            and self.current.tenant_id == tenant_id
            and self.current.effective_from <= at
        ):
            return self.current
        raise TenantLegalOperatingModelRegistryNotFoundError(
            "CX26_R2_NOT_FOUND"
        )

    def create_or_replay(
        self,
        value: TenantLegalOperatingModel,
        *,
        session: Any,
    ) -> TenantLegalOperatingModel:
        assert session.in_transaction is True
        self.create_calls += 1
        self.created.append(value)
        return self.persist_override or value


def repos(
    *,
    business_role: str = "tenant_admin",
    auth_role: str = "ENTERPRISE_ADMIN",
) -> dict[str, Any]:
    return {
        "principal_repository": PrincipalReader(),
        "membership_repository": MembershipReader(),
        "business_role_repository": RoleReader(
            business_role
        ),
        "role_assignment_repository": RoleReader(
            auth_role
        ),
    }


def model(
    *,
    tenant_id: str = TENANT,
    operating_model_id: str = "operating-model-existing",
    revision: int = 1,
    items: tuple[str, ...] = (
        "PERSONA_PARTNER",
        "PRACTICE_DISPUTES",
    ),
    effective_from: datetime = BASE,
    supersedes: str | None = None,
) -> TenantLegalOperatingModel:
    return TenantLegalOperatingModel(
        tenant_id=tenant_id,
        operating_model_id=operating_model_id,
        revision=revision,
        activated_item_ids=items,
        effective_from=effective_from,
        supersedes_operating_model_id=supersedes,
    )


def configure(
    registry: FakeRegistry,
    *,
    expected_revision: int | None = None,
    activated_item_ids: list[str] | tuple[str, ...] = (
        "PRACTICE_DISPUTES",
        "PERSONA_PARTNER",
    ),
    idempotency_key: str = "command-1",
    session: Session | None = None,
    effective_from: datetime = BASE,
    repository_overrides: dict[str, Any] | None = None,
) -> TenantLegalOperatingModel:
    values = repos()
    if repository_overrides:
        values.update(repository_overrides)

    return service.configure_tenant_legal_operating_model(
        tenant_id=TENANT,
        principal_id=PRINCIPAL,
        expected_revision=expected_revision,
        activated_item_ids=activated_item_ids,
        idempotency_key=idempotency_key,
        registry=registry,  # type: ignore[arg-type]
        session=session or Session(),
        effective_from=effective_from,
        **values,
    )


def test_identity_and_authority_constants_are_exact() -> None:
    assert (
        service.VERSION
        == "v1.0.0-CX26-R3-CURRENT-OPERATING-MODEL-COMMAND"
    )
    assert (
        service.PERMISSION
        == "legal_operations:operating_model:manage"
    )
    assert service.OPERATION == "legal_operating_model_manage"


def test_active_transaction_is_required_before_authority_or_registry() -> None:
    registry = FakeRegistry()

    with pytest.raises(
        service.TenantLegalOperatingModelAuthorityUnavailableError,
        match="CX26_R3_ACTIVE_TRANSACTION_REQUIRED",
    ) as error:
        configure(
            registry,
            session=Session(False),
        )

    assert error.value.code == "CX26_R3_ACTIVE_TRANSACTION_REQUIRED"
    assert registry.get_calls == 0
    assert registry.resolve_calls == 0
    assert registry.create_calls == 0


def test_authorized_current_read_returns_exact_registry_truth() -> None:
    current = model()
    registry = FakeRegistry(current=current)

    result = service.get_current_tenant_legal_operating_model(
        tenant_id=TENANT,
        principal_id=PRINCIPAL,
        registry=registry,  # type: ignore[arg-type]
        session=Session(),
        observed_at=BASE,
        **repos(),
    )

    assert result is current
    assert registry.resolve_calls == 1
    assert registry.get_calls == 0
    assert registry.create_calls == 0


def test_denial_precedes_registry_read_or_write() -> None:
    registry = FakeRegistry()

    with pytest.raises(
        service.TenantLegalOperatingModelAuthorizationDeniedError,
        match="CX26_R3_AUTHORIZATION_DENIED",
    ):
        service.get_current_tenant_legal_operating_model(
            tenant_id=TENANT,
            principal_id=PRINCIPAL,
            registry=registry,  # type: ignore[arg-type]
            session=Session(),
            observed_at=BASE,
            **repos(
                business_role="tenant_owner",
            ),
        )

    assert registry.resolve_calls == 0
    assert registry.get_calls == 0
    assert registry.create_calls == 0


def test_authority_unavailable_is_typed_without_internal_leak(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    registry = FakeRegistry()

    monkeypatch.setattr(
        service,
        "authorize_tenant_operation",
        lambda **_: TenantAuthorizationDecision(
            False,
            TenantAuthorizationReason.PRINCIPAL_AUTHORITY_UNAVAILABLE,
        ),
    )

    with pytest.raises(
        service.TenantLegalOperatingModelAuthorityUnavailableError,
        match="CX26_R3_AUTHORITY_UNAVAILABLE",
    ) as error:
        configure(registry)

    assert error.value.code == "CX26_R3_AUTHORITY_UNAVAILABLE"
    assert registry.get_calls == 0
    assert registry.resolve_calls == 0
    assert registry.create_calls == 0


@pytest.mark.parametrize(
    ("expected_revision", "code"),
    [
        (0, "CX26_R3_EXPECTED_REVISION_INVALID"),
        (-1, "CX26_R3_EXPECTED_REVISION_INVALID"),
        (True, "CX26_R3_EXPECTED_REVISION_INVALID"),
    ],
)
def test_invalid_expected_revision_fails_before_registry(
    expected_revision: object,
    code: str,
) -> None:
    registry = FakeRegistry()

    with pytest.raises(
        service.TenantLegalOperatingModelRevisionConflictError,
        match=code,
    ):
        service.configure_tenant_legal_operating_model(
            tenant_id=TENANT,
            principal_id=PRINCIPAL,
            expected_revision=expected_revision,  # type: ignore[arg-type]
            activated_item_ids=["PERSONA_PARTNER"],
            idempotency_key="command-invalid-revision",
            registry=registry,  # type: ignore[arg-type]
            session=Session(),
            effective_from=BASE,
            **repos(),
        )

    assert registry.get_calls == 0
    assert registry.resolve_calls == 0
    assert registry.create_calls == 0


@pytest.mark.parametrize(
    "key",
    (
        "",
        " command",
        "command ",
        "x" * 201,
    ),
)
def test_invalid_idempotency_key_fails_before_registry(
    key: str,
) -> None:
    registry = FakeRegistry()

    with pytest.raises(
        service.TenantLegalOperatingModelRevisionConflictError,
        match="CX26_R3_IDEMPOTENCY_KEY_INVALID",
    ):
        configure(
            registry,
            idempotency_key=key,
        )

    assert registry.get_calls == 0
    assert registry.resolve_calls == 0
    assert registry.create_calls == 0


def test_invalid_activated_items_shape_uses_domain_error() -> None:
    registry = FakeRegistry()

    with pytest.raises(
        TenantLegalOperatingModelError,
        match="G7B_ACTIVATED_ITEMS_INVALID",
    ):
        service.configure_tenant_legal_operating_model(
            tenant_id=TENANT,
            principal_id=PRINCIPAL,
            expected_revision=None,
            activated_item_ids="PERSONA_PARTNER",  # type: ignore[arg-type]
            idempotency_key="command-items",
            registry=registry,  # type: ignore[arg-type]
            session=Session(),
            effective_from=BASE,
            **repos(),
        )

    assert registry.get_calls == 0
    assert registry.resolve_calls == 0
    assert registry.create_calls == 0


def test_first_revision_is_server_composed_and_canonical() -> None:
    registry = FakeRegistry()

    result = configure(registry)

    assert result.revision == 1
    assert result.tenant_id == TENANT
    assert result.supersedes_operating_model_id is None
    assert result.activated_item_ids == (
        "PERSONA_PARTNER",
        "PRACTICE_DISPUTES",
    )
    assert result.effective_from == BASE
    assert result.operating_model_id.startswith("tlom-")
    assert len(result.operating_model_id) == len("tlom-") + 128
    assert registry.get_calls == 1
    assert registry.resolve_calls == 1
    assert registry.create_calls == 1
    assert registry.created == [result]


def test_exact_idempotent_replay_returns_original_without_write() -> None:
    identity = service._idempotent_model_id(
        TENANT,
        "command-replay",
    )
    replay = model(
        operating_model_id=identity,
        revision=1,
        items=(
            "PERSONA_PARTNER",
            "PRACTICE_DISPUTES",
        ),
    )
    registry = FakeRegistry(replay=replay)

    result = configure(
        registry,
        idempotency_key="command-replay",
    )

    assert result is replay
    assert registry.get_calls == 1
    assert registry.resolve_calls == 0
    assert registry.create_calls == 0


def test_divergent_same_key_replay_fails_closed() -> None:
    identity = service._idempotent_model_id(
        TENANT,
        "command-divergent",
    )
    replay = model(
        operating_model_id=identity,
        items=("PERSONA_PARTNER",),
    )
    registry = FakeRegistry(replay=replay)

    with pytest.raises(
        service.TenantLegalOperatingModelRevisionConflictError,
        match="CX26_R3_DIVERGENT_IDEMPOTENCY_REPLAY",
    ):
        configure(
            registry,
            idempotency_key="command-divergent",
            activated_item_ids=(
                "PERSONA_PARTNER",
                "PRACTICE_DISPUTES",
            ),
        )

    assert registry.create_calls == 0


def test_stale_expected_revision_fails_without_create() -> None:
    registry = FakeRegistry(
        current=model(revision=1),
    )

    with pytest.raises(
        service.TenantLegalOperatingModelRevisionConflictError,
        match="CX26_R3_EXPECTED_REVISION_CONFLICT",
    ):
        configure(
            registry,
            expected_revision=None,
            idempotency_key="command-stale",
        )

    assert registry.create_calls == 0


def test_next_revision_supersedes_exact_current_truth() -> None:
    current = model(
        operating_model_id="operating-model-r1",
        revision=1,
    )
    registry = FakeRegistry(current=current)

    result = configure(
        registry,
        expected_revision=1,
        idempotency_key="command-r2",
        activated_item_ids=(
            "PERSONA_PARTNER",
            "RISK_CONFLICTS",
        ),
        effective_from=BASE + timedelta(minutes=1),
    )

    assert result.revision == 2
    assert (
        result.supersedes_operating_model_id
        == current.operating_model_id
    )
    assert result.activated_item_ids == (
        "PERSONA_PARTNER",
        "RISK_CONFLICTS",
    )
    assert registry.create_calls == 1


def test_persisted_replay_fingerprint_mismatch_fails_closed() -> None:
    wrong = model(
        operating_model_id="wrong-persisted",
        items=("PERSONA_PARTNER",),
    )
    registry = FakeRegistry(
        persist_override=wrong,
    )

    with pytest.raises(
        service.TenantLegalOperatingModelRevisionConflictError,
        match="CX26_R3_PERSISTED_REPLAY_MISMATCH",
    ):
        configure(
            registry,
            idempotency_key="command-persist-mismatch",
        )

    assert registry.create_calls == 1


def test_service_signature_has_no_caller_authority_fields() -> None:
    forbidden = {
        "role",
        "roles",
        "permission",
        "permissions",
        "authorization",
        "jwt_role",
        "trusted_role",
        "financial_execution",
        "payment_authority",
    }

    params = set(
        service.configure_tenant_legal_operating_model.__annotations__
    )

    assert not forbidden.intersection(params)


# ARTIFACT: test_tenant_legal_operating_model_service.py
# VERSION: v1.0.0-CX26-R3-CURRENT-OPERATING-MODEL-COMMAND-UNIT-CERT
# AUTHORITY BOUNDARY: exact-IAM command composition only; no transport or downstream capability grant
# TENANT POSTURE: current own-tenant authorization precedes every registry interaction
# FAIL-CLOSED POSTURE: invalid transaction, denial, outage, stale revision, divergent replay, malformed command, and persisted mismatch reject
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively
# END OF WILSY OS SOVEREIGN ARTIFACT
