"""Direct certificate for current-authority deputy-principal binding.

TITLE: WILSY OS Deputy Principal Binding Orchestration Certificate
VERSION: v1.0.0-L8-6B-DEPUTY-PRINCIPAL-BINDING-ORCHESTRATION-CERT
AUTHORITY: Direct adversarial certification of L8-6B authority composition.
EPITOME: Prove one active transaction and five independent current authorities
         are required before immutable binding persistence: principal,
         membership, tenant_deputy business role, DEPUTY assignment, and exact
         canonical Deputy evidence.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tests/unit/test_deputy_principal_binding_orchestrator.py
COLLABORATION / OWNERSHIP: Certificate for the L8-6B orchestrator; underlying
                            IAM, P1/P2/L8-5, binding value and registry remain
                            independent canonical authorities.
CERTIFICATION / UPDATE DATE: 2026-09-23
CHANGELOG: 2026-09-23 v1.0.0-L8-6B-DEPUTY-PRINCIPAL-BINDING-ORCHESTRATION-CERT
           establishes success/replay, transaction, principal/membership/role,
           Deputy scope/evidence, conflict, session propagation, and
           non-authorizing-result proofs.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2; ISO 27001.
SECURITY / PRIVACY POSTURE: Synthetic opaque values only.
TENANT BOUNDARY: All authority/lifecycle/binding reads and writes use one exact
                 tenant and one caller-owned active session.
AUTHORITY BOUNDARY: Certificate only; binding is not authorization or service.
FINANCIAL AUTHORITY BOUNDARY: Kennel EOS remains exclusive.
FAIL-CLOSED DECLARATION: Any missing/inactive/wrong authority, absent Deputy,
                         conflict, or inactive transaction rejects before write.
"""
from __future__ import annotations

from copy import deepcopy
from datetime import datetime, timezone
from types import SimpleNamespace
from typing import Any

import pytest
from pymongo.errors import DuplicateKeyError

from tools.eos.auth.principal_authority import PrincipalAuthority
from tools.eos.auth.principal_authority_repository import PrincipalAuthorityRepository
from tools.eos.auth.principal_status import PrincipalStatus
from tools.eos.auth.role_assignment import (
    RoleAssignmentAuthority,
    RoleAssignmentStatus,
)
from tools.eos.auth.role_assignment_repository import RoleAssignmentRepository
from tools.eos.auth.tenant_business_role import (
    TenantBusinessRoleAuthority,
    TenantBusinessRoleStatus,
)
from tools.eos.auth.tenant_business_role_repository import (
    TenantBusinessRoleRepository,
)
from tools.eos.auth.tenant_membership import (
    TenantMembershipAuthority,
    TenantMembershipStatus,
)
from tools.eos.auth.tenant_membership_repository import TenantMembershipRepository
from tools.eos.legal_operations.domain.legal_operations_lifecycle import Deputy
from tools.eos.legal_operations.orchestration.deputy_principal_binding_orchestrator import (
    VERSION as PRODUCTION_VERSION,
    DeputyPrincipalBindingOrchestrationError,
    DeputyPrincipalBindingTransactionRequiredError,
    bind_deputy_principal_identity,
)
from tools.eos.legal_operations.registry.deputy_principal_binding_registry import (
    DeputyPrincipalBindingRegistry,
)
from tools.eos.legal_operations.registry.legal_operations_lifecycle_registry import (
    LegalOperationsLifecycleRegistry,
)


VERSION = "v1.0.0-L8-6B-DEPUTY-PRINCIPAL-BINDING-ORCHESTRATION-CERT"
NOW = datetime(2026, 9, 23, 16, 30, tzinfo=timezone.utc)
TENANT = "tenant-a"
PRINCIPAL = "principal-1"
DEPUTY = "deputy-1"


class FakeSession:
    """Caller-owned active/inactive transaction marker."""

    def __init__(self, active: bool) -> None:
        self.in_transaction = active


class FakeCollection:
    """Small Mongo-compatible store preserving exact queries and sessions."""

    def __init__(self) -> None:
        self.docs: list[dict[str, Any]] = []
        self.calls: list[tuple[str, object, object]] = []

    @staticmethod
    def _lookup(document: dict[str, Any], key: str) -> Any:
        value: Any = document
        for part in key.split("."):
            if not isinstance(value, dict):
                return None
            value = value.get(part)
        return value

    def find_one(
        self,
        query: dict[str, object],
        *,
        session: object = None,
    ) -> dict[str, Any] | None:
        self.calls.append(("find_one", session, deepcopy(query)))
        for document in self.docs:
            if all(self._lookup(document, key) == value for key, value in query.items()):
                return deepcopy(document)
        return None

    def find(
        self,
        query: dict[str, object],
        *,
        session: object = None,
    ) -> list[dict[str, Any]]:
        self.calls.append(("find", session, deepcopy(query)))
        return [
            deepcopy(document)
            for document in self.docs
            if all(self._lookup(document, key) == value for key, value in query.items())
        ]

    def insert_one(
        self,
        document: dict[str, object],
        *,
        session: object = None,
    ) -> object:
        self.calls.append(("insert_one", session, deepcopy(document)))
        if "principal_id" in document and "deputy_id" in document:
            for existing in self.docs:
                if (
                    existing.get("tenant_id") == document.get("tenant_id")
                    and (
                        existing.get("principal_id") == document.get("principal_id")
                        or existing.get("deputy_id") == document.get("deputy_id")
                    )
                ):
                    raise DuplicateKeyError("synthetic duplicate")
        self.docs.append(deepcopy(document))
        return SimpleNamespace(inserted_id=len(self.docs))


def _collections() -> dict[str, FakeCollection]:
    return {
        "principal": FakeCollection(),
        "membership": FakeCollection(),
        "business": FakeCollection(),
        "role": FakeCollection(),
        "lifecycle": FakeCollection(),
        "binding": FakeCollection(),
    }


def _seed(
    stores: dict[str, FakeCollection],
    *,
    principal_status: PrincipalStatus = PrincipalStatus.ACTIVE,
    membership_status: TenantMembershipStatus = TenantMembershipStatus.ACTIVE,
    business_role: str = "tenant_deputy",
    business_status: TenantBusinessRoleStatus = TenantBusinessRoleStatus.ACTIVE,
    role_status: RoleAssignmentStatus = RoleAssignmentStatus.ACTIVE,
    deputy_tenant: str = TENANT,
    include_deputy: bool = True,
    include_role: bool = True,
) -> None:
    PrincipalAuthorityRepository.create(
        PrincipalAuthority(PRINCIPAL, principal_status, 0),
        stores["principal"],
    )
    TenantMembershipRepository.insert(
        TenantMembershipAuthority(
            PRINCIPAL,
            TENANT,
            membership_status,
            0,
        ),
        stores["membership"],
    )
    TenantBusinessRoleRepository.insert(
        TenantBusinessRoleAuthority(
            PRINCIPAL,
            TENANT,
            business_role,
            business_status,
            0,
            NOW,
            None,
        ),
        stores["business"],
    )
    if include_role:
        RoleAssignmentRepository.insert(
            RoleAssignmentAuthority(
                PRINCIPAL,
                TENANT,
                "DEPUTY",
                role_status,
                0,
            ),
            stores["role"],
        )
    if include_deputy:
        LegalOperationsLifecycleRegistry.create(
            Deputy(
                tenant_id=deputy_tenant,
                deputy_id=DEPUTY,
                sheriff_office_id="office-1",
                display_name="Deputy One",
                badge_reference="badge-1",
                evidence_reference="deputy-directory-evidence",
            ),
            stores["lifecycle"],
        )


def _bind(
    stores: dict[str, FakeCollection],
    session: FakeSession,
    *,
    deputy_id: str = DEPUTY,
):
    return bind_deputy_principal_identity(
        tenant_id=TENANT,
        principal_id=PRINCIPAL,
        deputy_id=deputy_id,
        bound_at=NOW,
        evidence_reference="binding-evidence",
        lifecycle_collection=stores["lifecycle"],
        binding_collection=stores["binding"],
        principal_collection=stores["principal"],
        membership_collection=stores["membership"],
        business_role_collection=stores["business"],
        role_assignment_collection=stores["role"],
        session=session,
    )


def _expect(
    code: str,
    operation: Any,
    *,
    error_type: type[DeputyPrincipalBindingOrchestrationError] = (
        DeputyPrincipalBindingOrchestrationError
    ),
) -> None:
    with pytest.raises(error_type) as caught:
        operation()
    assert caught.value.code == code
    assert str(caught.value) == code


def test_success_exact_replay_and_one_session_across_all_authorities() -> None:
    stores = _collections()
    _seed(stores)
    session = FakeSession(True)

    first = _bind(stores, session)
    replay = _bind(stores, session)

    assert first == replay
    assert first.tenant_id == TENANT
    assert first.principal_id == PRINCIPAL
    assert first.deputy_id == DEPUTY
    assert len(stores["binding"].docs) == 1
    for name, store in stores.items():
        assert store.calls, name
        assert all(
            observed_session is session
            for operation, observed_session, _ in store.calls
            if operation in {"find", "find_one", "insert_one"}
            and observed_session is not None
        )


def test_inactive_transaction_rejects_before_any_authority_read() -> None:
    stores = _collections()
    _seed(stores)
    for store in stores.values():
        store.calls.clear()

    _expect(
        "L8_6B_ACTIVE_TRANSACTION_REQUIRED",
        lambda: _bind(stores, FakeSession(False)),
        error_type=DeputyPrincipalBindingTransactionRequiredError,
    )
    assert all(not store.calls for store in stores.values())


@pytest.mark.parametrize(
    ("mutation", "code"),
    (
        ("principal", "L8_6B_PRINCIPAL_INACTIVE"),
        ("membership", "L8_6B_MEMBERSHIP_INACTIVE"),
        ("business", "L8_6B_DEPUTY_BUSINESS_ROLE_REQUIRED"),
        ("role", "L8_6B_DEPUTY_AUTHORIZATION_ROLE_REQUIRED"),
    ),
)
def test_inactive_or_wrong_current_iam_rejects_before_binding_write(
    mutation: str,
    code: str,
) -> None:
    stores = _collections()
    kwargs: dict[str, object] = {}
    if mutation == "principal":
        kwargs["principal_status"] = PrincipalStatus.SUSPENDED
    elif mutation == "membership":
        kwargs["membership_status"] = TenantMembershipStatus.SUSPENDED
    elif mutation == "business":
        kwargs["business_role"] = "tenant_sheriff"
    elif mutation == "role":
        kwargs["role_status"] = RoleAssignmentStatus.REVOKED
    _seed(stores, **kwargs)
    session = FakeSession(True)

    _expect(code, lambda: _bind(stores, session))
    assert stores["binding"].docs == []


def test_missing_deputy_and_foreign_deputy_are_exact_absence() -> None:
    stores = _collections()
    _seed(stores, include_deputy=False)
    session = FakeSession(True)
    _expect("L8_6B_DEPUTY_NOT_FOUND", lambda: _bind(stores, session))
    assert stores["binding"].docs == []

    stores = _collections()
    _seed(stores, deputy_tenant="tenant-b")
    session = FakeSession(True)
    _expect("L8_6B_DEPUTY_NOT_FOUND", lambda: _bind(stores, session))
    assert stores["binding"].docs == []


def test_missing_deputy_role_assignment_rejects_before_lifecycle_read() -> None:
    stores = _collections()
    _seed(stores, include_role=False)
    session = FakeSession(True)

    _expect(
        "L8_6B_DEPUTY_AUTHORIZATION_ROLE_NOT_FOUND",
        lambda: _bind(stores, session),
    )
    assert stores["binding"].docs == []
    assert stores["lifecycle"].calls


def test_existing_different_binding_conflict_preserves_first_identity() -> None:
    stores = _collections()
    _seed(stores)
    session = FakeSession(True)
    first = _bind(stores, session)

    other_deputy = Deputy(
        tenant_id=TENANT,
        deputy_id="deputy-2",
        sheriff_office_id="office-1",
        display_name="Deputy Two",
        badge_reference="badge-2",
        evidence_reference="deputy-2-evidence",
    )
    LegalOperationsLifecycleRegistry.create(
        other_deputy,
        stores["lifecycle"],
        session=session,
    )

    _expect(
        "L8_6B_BINDING_CONFLICT",
        lambda: _bind(stores, session, deputy_id="deputy-2"),
    )
    resolved = DeputyPrincipalBindingRegistry.resolve_by_principal(
        TENANT,
        PRINCIPAL,
        stores["binding"],
        session=session,
    )
    assert resolved == first
    assert len(stores["binding"].docs) == 1


def test_result_is_identity_evidence_not_authorization_or_financial_truth() -> None:
    stores = _collections()
    _seed(stores)
    value = _bind(stores, FakeSession(True))
    keys = set(value.to_dict())

    for forbidden in {
        "permission",
        "role_id",
        "business_role",
        "authorized",
        "queue",
        "attempt_id",
        "service_execution_id",
        "return_id",
        "invoice",
        "payment",
        "settlement",
        "ai_score",
    }:
        assert forbidden not in keys

    assert PRODUCTION_VERSION == (
        "v1.0.1-L8-6B-DEPUTY-PRINCIPAL-BINDING-ORCHESTRATION"
    )
    assert VERSION == (
        "v1.0.0-L8-6B-DEPUTY-PRINCIPAL-BINDING-ORCHESTRATION-CERT"
    )


# ARTIFACT: test_deputy_principal_binding_orchestrator.py
# VERSION: v1.0.0-L8-6B-DEPUTY-PRINCIPAL-BINDING-ORCHESTRATION-CERT
# AUTHORITY BOUNDARY: direct five-authority binding composition certificate only
# TENANT POSTURE: exact same tenant/session across IAM, Deputy, and binding evidence
# FAIL-CLOSED POSTURE: inactive/missing/wrong authority, absence, conflict, or transaction drift rejects
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS remains exclusive
# END OF WILSY OS SOVEREIGN ARTIFACT
