"""Direct certificate for sovereign Legal client matter visibility provisioning.

TITLE: WILSY OS Legal Client Matter Visibility Provisioning Orchestrator Certificate
VERSION: v1.0.0-L8-7C3C-CLIENT-MATTER-VISIBILITY-PROVISIONING-CERT
AUTHORITY: Direct adversarial certification of C3C grant/revoke composition only.
EPITOME: Prove one active caller transaction, exact C3B actor authorization,
         independent ACTIVE target LEGAL_CLIENT IAM, canonical current P1
         CaseMatter evidence, and L8-7A/L8-7B append-only persistence are all
         required before visibility grant/revoke evidence can be returned.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tests/unit/test_legal_client_matter_visibility_orchestrator.py
COLLABORATION / OWNERSHIP: C3B authorization, current IAM readers, L8-5 current
                            matter composition, L8-7A relation values and L8-7B
                            registry remain independent canonical authorities;
                            this certificate proves only their C3C composition.
CERTIFICATION / UPDATE DATE: 2026-09-23
CHANGELOG: 2026-09-23 v1.0.0-L8-7C3C-CLIENT-MATTER-VISIBILITY-PROVISIONING-CERT
           establishes grant/replay, append-only revoke, active-transaction,
           actor-denial, target-client IAM, missing/foreign matter, divergent
           grant conflict, same-session propagation, currentness and
           non-authorizing/non-financial result proofs.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2; ISO 27001.
SECURITY / PRIVACY POSTURE: Synthetic opaque identities/evidence only.
TENANT BOUNDARY: One exact tenant and one caller-owned active session span every
                 actor/target IAM read, matter read and visibility write.
AUTHORITY BOUNDARY: Certificate only; no HTTP/client read authority is created.
FINANCIAL AUTHORITY BOUNDARY: Kennel EOS remains exclusive.
TRANSACTION BOUNDARY: Fake transaction marker only; orchestrator must not own it.
FAIL-CLOSED DECLARATION: Denied/inactive/missing IAM, absent matter, conflict,
                         revoked currentness or inactive transaction rejects.
"""
from __future__ import annotations

from copy import deepcopy
from datetime import datetime, timedelta, timezone
from types import SimpleNamespace
from typing import Any

import pytest

from tools.eos.auth.principal_authority_repository import (
    PrincipalAuthorityNotFoundError,
)
from tools.eos.auth.principal_status import PrincipalStatus
from tools.eos.auth.role_assignment import RoleAssignmentStatus
from tools.eos.auth.role_assignment_repository import RoleAssignmentNotFoundError
from tools.eos.auth.tenant_business_role import TenantBusinessRoleStatus
from tools.eos.auth.tenant_membership import TenantMembershipStatus
from tools.eos.auth.tenant_membership_repository import (
    TenantMembershipNotFoundError,
)
from tools.eos.legal_operations.domain.legal_operations_lifecycle import CaseMatter
from tools.eos.legal_operations.orchestration.legal_client_matter_visibility_orchestrator import (
    OPERATION,
    PERMISSION,
    VERSION as PRODUCTION_VERSION,
    LegalClientMatterVisibilityProvisioningError,
    LegalClientMatterVisibilityTransactionRequiredError,
    grant_client_matter_visibility,
    revoke_client_matter_visibility,
)
from tools.eos.legal_operations.registry.legal_client_matter_visibility_registry import (
    LegalClientMatterVisibilityNotFoundError,
    LegalClientMatterVisibilityRegistry,
)
from tools.eos.legal_operations.registry.legal_operations_lifecycle_registry import (
    LegalOperationsLifecycleRegistry,
)


VERSION = "v1.0.0-L8-7C3C-CLIENT-MATTER-VISIBILITY-PROVISIONING-CERT"
NOW = datetime(2026, 9, 23, 20, 0, tzinfo=timezone.utc)
TENANT = "tenant-c3c"
ACTOR = "principal-partner"
CLIENT = "principal-client"
MATTER = "matter-c3c"


class FakeSession:
    """Caller-owned transaction marker."""

    def __init__(self, active: bool) -> None:
        self.in_transaction = active


class FakeCollection:
    """Small Mongo-compatible append-only store with call/session evidence."""

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
            if all(
                self._lookup(document, key) == value
                for key, value in query.items()
            ):
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
            if all(
                self._lookup(document, key) == value
                for key, value in query.items()
            )
        ]

    def insert_one(
        self,
        document: dict[str, object],
        *,
        session: object = None,
    ) -> object:
        self.calls.append(("insert_one", session, deepcopy(document)))
        self.docs.append(deepcopy(document))
        return SimpleNamespace(inserted_id=len(self.docs))


class PrincipalReader:
    """Read two current principal states with explicit absence semantics."""

    def __init__(
        self,
        *,
        actor_status: PrincipalStatus = PrincipalStatus.ACTIVE,
        client_status: PrincipalStatus = PrincipalStatus.ACTIVE,
    ) -> None:
        self.statuses = {
            ACTOR: actor_status,
            CLIENT: client_status,
        }
        self.calls: list[tuple[str, object]] = []

    def resolve(self, principal_id: str, *, session: object = None) -> object:
        self.calls.append((principal_id, session))
        if principal_id not in self.statuses:
            raise PrincipalAuthorityNotFoundError("missing")
        return SimpleNamespace(status=self.statuses[principal_id])


class MembershipReader:
    """Read current exact tenant membership for actor and target client."""

    def __init__(
        self,
        *,
        actor_status: TenantMembershipStatus = TenantMembershipStatus.ACTIVE,
        client_status: TenantMembershipStatus = TenantMembershipStatus.ACTIVE,
    ) -> None:
        self.statuses = {
            ACTOR: actor_status,
            CLIENT: client_status,
        }
        self.calls: list[tuple[str, str, object]] = []

    def resolve(
        self,
        principal_id: str,
        tenant_id: str,
        *,
        session: object = None,
    ) -> object:
        self.calls.append((principal_id, tenant_id, session))
        if tenant_id != TENANT or principal_id not in self.statuses:
            raise TenantMembershipNotFoundError("missing")
        return SimpleNamespace(status=self.statuses[principal_id])


class BusinessRoleReader:
    """Expose one explicit current business role per principal."""

    def __init__(
        self,
        *,
        actor_role: str = "tenant_legal_partner",
        client_role: str = "tenant_legal_client",
        client_status: TenantBusinessRoleStatus = TenantBusinessRoleStatus.ACTIVE,
    ) -> None:
        self.roles = {
            ACTOR: (actor_role, TenantBusinessRoleStatus.ACTIVE),
            CLIENT: (client_role, client_status),
        }
        self.calls: list[tuple[str, str, str, object]] = []

    def resolve(
        self,
        principal_id: str,
        tenant_id: str,
        role_id: str,
        *,
        session: object = None,
    ) -> object:
        self.calls.append((principal_id, tenant_id, role_id, session))
        configured = self.roles.get(principal_id)
        if (
            tenant_id != TENANT
            or configured is None
            or configured[0] != role_id
        ):
            raise RoleAssignmentNotFoundError("missing")
        return SimpleNamespace(status=configured[1])


class AuthorizationRoleReader:
    """Expose current final authorization roles for actor and client."""

    def __init__(
        self,
        *,
        actor_role: str = "LEGAL_PARTNER",
        actor_status: RoleAssignmentStatus = RoleAssignmentStatus.ACTIVE,
        client_status: RoleAssignmentStatus = RoleAssignmentStatus.ACTIVE,
    ) -> None:
        self.values = {
            (ACTOR, actor_role): actor_status,
            (CLIENT, "LEGAL_CLIENT"): client_status,
        }
        self.calls: list[tuple[str, str, str, object]] = []

    def resolve(
        self,
        principal_id: str,
        tenant_id: str,
        role_id: str,
        *,
        session: object = None,
    ) -> object:
        self.calls.append((principal_id, tenant_id, role_id, session))
        key = (principal_id, role_id)
        if tenant_id != TENANT or key not in self.values:
            raise RoleAssignmentNotFoundError("missing")
        return SimpleNamespace(status=self.values[key])


def _stores() -> tuple[FakeCollection, FakeCollection]:
    lifecycle = FakeCollection()
    visibility = FakeCollection()
    LegalOperationsLifecycleRegistry.create(
        CaseMatter(
            tenant_id=TENANT,
            case_matter_id=MATTER,
            matter_reference="CASE-C3C",
            opened_at=NOW,
            evidence_reference="matter-registration",
        ),
        lifecycle,
    )
    lifecycle.calls.clear()
    return lifecycle, visibility


def _readers(
    *,
    actor_business_role: str = "tenant_legal_partner",
    actor_authorization_role: str = "LEGAL_PARTNER",
    actor_principal_status: PrincipalStatus = PrincipalStatus.ACTIVE,
    client_principal_status: PrincipalStatus = PrincipalStatus.ACTIVE,
    client_membership_status: TenantMembershipStatus = TenantMembershipStatus.ACTIVE,
    client_business_role: str = "tenant_legal_client",
    client_business_status: TenantBusinessRoleStatus = TenantBusinessRoleStatus.ACTIVE,
    client_role_status: RoleAssignmentStatus = RoleAssignmentStatus.ACTIVE,
) -> tuple[
    PrincipalReader,
    MembershipReader,
    BusinessRoleReader,
    AuthorizationRoleReader,
]:
    return (
        PrincipalReader(
            actor_status=actor_principal_status,
            client_status=client_principal_status,
        ),
        MembershipReader(client_status=client_membership_status),
        BusinessRoleReader(
            actor_role=actor_business_role,
            client_role=client_business_role,
            client_status=client_business_status,
        ),
        AuthorizationRoleReader(
            actor_role=actor_authorization_role,
            client_status=client_role_status,
        ),
    )


def _grant(
    lifecycle: FakeCollection,
    visibility: FakeCollection,
    session: FakeSession,
    readers: tuple[
        PrincipalReader,
        MembershipReader,
        BusinessRoleReader,
        AuthorizationRoleReader,
    ],
    *,
    tenant_id: str = TENANT,
    case_matter_id: str = MATTER,
    evidence_reference: str = "grant-evidence",
):
    principal, membership, business, roles = readers
    return grant_client_matter_visibility(
        tenant_id=tenant_id,
        actor_principal_id=ACTOR,
        client_principal_id=CLIENT,
        case_matter_id=case_matter_id,
        granted_at=NOW + timedelta(minutes=1),
        evidence_reference=evidence_reference,
        lifecycle_collection=lifecycle,
        visibility_collection=visibility,
        principal_repository=principal,
        membership_repository=membership,
        business_role_repository=business,
        role_assignment_repository=roles,
        session=session,
    )


def _revoke(
    lifecycle: FakeCollection,
    visibility: FakeCollection,
    session: FakeSession,
    readers: tuple[
        PrincipalReader,
        MembershipReader,
        BusinessRoleReader,
        AuthorizationRoleReader,
    ],
):
    principal, membership, business, roles = readers
    return revoke_client_matter_visibility(
        tenant_id=TENANT,
        actor_principal_id=ACTOR,
        client_principal_id=CLIENT,
        case_matter_id=MATTER,
        revoked_at=NOW + timedelta(minutes=2),
        evidence_reference="revoke-evidence",
        lifecycle_collection=lifecycle,
        visibility_collection=visibility,
        principal_repository=principal,
        membership_repository=membership,
        business_role_repository=business,
        role_assignment_repository=roles,
        session=session,
    )


def _expect(
    code: str,
    operation: Any,
    *,
    error_type: type[LegalClientMatterVisibilityProvisioningError] = (
        LegalClientMatterVisibilityProvisioningError
    ),
) -> None:
    with pytest.raises(error_type) as caught:
        operation()
    assert caught.value.code == code
    assert str(caught.value) == code


def test_grant_exact_replay_full_current_truth_and_same_session() -> None:
    lifecycle, visibility = _stores()
    readers = _readers()
    session = FakeSession(True)

    first = _grant(lifecycle, visibility, session, readers)
    replay = _grant(lifecycle, visibility, session, readers)

    assert first == replay
    assert first.tenant_id == TENANT
    assert first.client_principal_id == CLIENT
    assert first.case_matter_id == MATTER
    assert first.granted_by_principal_id == ACTOR
    assert first.status.value == "ACTIVE"
    assert len(visibility.docs) == 1

    principal, membership, business, roles = readers
    for calls in (
        principal.calls,
        membership.calls,
        business.calls,
        roles.calls,
    ):
        assert calls
        assert all(call[-1] is session for call in calls)
    for store in (lifecycle, visibility):
        assert store.calls
        assert all(
            observed_session is session
            for operation, observed_session, _ in store.calls
            if operation in {"find", "find_one", "insert_one"}
        )


def test_inactive_transaction_rejects_before_every_authority_read() -> None:
    lifecycle, visibility = _stores()
    readers = _readers()
    session = FakeSession(False)

    _expect(
        "L8_7C3C_ACTIVE_TRANSACTION_REQUIRED",
        lambda: _grant(lifecycle, visibility, session, readers),
        error_type=LegalClientMatterVisibilityTransactionRequiredError,
    )
    principal, membership, business, roles = readers
    assert principal.calls == []
    assert membership.calls == []
    assert business.calls == []
    assert roles.calls == []
    assert lifecycle.calls == []
    assert visibility.calls == []


@pytest.mark.parametrize(
    ("actor_business_role", "actor_authorization_role", "reason"),
    (
        (
            "tenant_legal_client",
            "LEGAL_CLIENT",
            "BUSINESS_ROLE_INELIGIBLE",
        ),
        (
            "tenant_sheriff",
            "SHERIFF",
            "BUSINESS_ROLE_INELIGIBLE",
        ),
        (
            "tenant_legal_partner",
            "LEGAL_CLIENT",
            "PERMISSION_NOT_GRANTED",
        ),
    ),
)
def test_actor_denial_short_circuits_target_matter_and_visibility(
    actor_business_role: str,
    actor_authorization_role: str,
    reason: str,
) -> None:
    lifecycle, visibility = _stores()
    readers = _readers(
        actor_business_role=actor_business_role,
        actor_authorization_role=actor_authorization_role,
    )
    session = FakeSession(True)

    _expect(
        f"L8_7C3C_ACTOR_AUTHORIZATION_DENIED_{reason}",
        lambda: _grant(lifecycle, visibility, session, readers),
    )
    principal, membership, _, _ = readers
    assert [call[0] for call in principal.calls] == [ACTOR]
    assert [call[0] for call in membership.calls] == [ACTOR]
    assert lifecycle.calls == []
    assert visibility.calls == []


@pytest.mark.parametrize(
    ("readers", "code"),
    (
        (
            _readers(client_principal_status=PrincipalStatus.SUSPENDED),
            "L8_7C3C_CLIENT_PRINCIPAL_INACTIVE",
        ),
        (
            _readers(
                client_membership_status=TenantMembershipStatus.SUSPENDED
            ),
            "L8_7C3C_CLIENT_MEMBERSHIP_INACTIVE",
        ),
        (
            _readers(client_business_role="tenant_legal_secretary"),
            "L8_7C3C_CLIENT_BUSINESS_ROLE_NOT_FOUND",
        ),
        (
            _readers(
                client_business_status=TenantBusinessRoleStatus.REVOKED
            ),
            "L8_7C3C_CLIENT_BUSINESS_ROLE_REQUIRED",
        ),
        (
            _readers(client_role_status=RoleAssignmentStatus.REVOKED),
            "L8_7C3C_CLIENT_AUTHORIZATION_ROLE_REQUIRED",
        ),
    ),
)
def test_target_client_iam_failure_rejects_before_matter_or_visibility(
    readers: tuple[
        PrincipalReader,
        MembershipReader,
        BusinessRoleReader,
        AuthorizationRoleReader,
    ],
    code: str,
) -> None:
    lifecycle, visibility = _stores()
    _expect(
        code,
        lambda: _grant(lifecycle, visibility, FakeSession(True), readers),
    )
    assert lifecycle.calls == []
    assert visibility.calls == []


def test_missing_and_foreign_matter_are_bounded_absence() -> None:
    lifecycle, visibility = _stores()
    readers = _readers()

    _expect(
        "L8_7C3C_CASE_MATTER_NOT_FOUND",
        lambda: _grant(
            lifecycle,
            visibility,
            FakeSession(True),
            readers,
            case_matter_id="matter-missing",
        ),
    )
    assert visibility.docs == []

    foreign_lifecycle = FakeCollection()
    LegalOperationsLifecycleRegistry.create(
        CaseMatter(
            tenant_id="tenant-other",
            case_matter_id=MATTER,
            matter_reference="CASE-FOREIGN",
            opened_at=NOW,
            evidence_reference="foreign-matter",
        ),
        foreign_lifecycle,
    )
    foreign_lifecycle.calls.clear()
    _expect(
        "L8_7C3C_CASE_MATTER_NOT_FOUND",
        lambda: _grant(
            foreign_lifecycle,
            visibility,
            FakeSession(True),
            _readers(),
        ),
    )
    assert visibility.docs == []


def test_divergent_grant_conflicts_without_overwriting_first_evidence() -> None:
    lifecycle, visibility = _stores()
    session = FakeSession(True)
    first = _grant(
        lifecycle,
        visibility,
        session,
        _readers(),
        evidence_reference="grant-one",
    )

    _expect(
        "L8_7C3C_VISIBILITY_CONFLICT",
        lambda: _grant(
            lifecycle,
            visibility,
            session,
            _readers(),
            evidence_reference="grant-two",
        ),
    )
    current = LegalClientMatterVisibilityRegistry.resolve_current_active(
        TENANT,
        CLIENT,
        MATTER,
        visibility,
        session=session,
    )
    assert current == first
    assert len(visibility.docs) == 1


def test_revoke_appends_history_and_removes_current_visibility() -> None:
    lifecycle, visibility = _stores()
    session = FakeSession(True)
    _grant(lifecycle, visibility, session, _readers())

    revoked = _revoke(
        lifecycle,
        visibility,
        session,
        _readers(),
    )
    assert revoked.status.value == "REVOKED"
    assert revoked.revoked_by_principal_id == ACTOR
    assert len(visibility.docs) == 2
    assert {row["status"] for row in visibility.docs} == {"ACTIVE", "REVOKED"}

    with pytest.raises(LegalClientMatterVisibilityNotFoundError):
        LegalClientMatterVisibilityRegistry.resolve_current_active(
            TENANT,
            CLIENT,
            MATTER,
            visibility,
            session=session,
        )

    _expect(
        "L8_7C3C_ACTIVE_VISIBILITY_NOT_FOUND",
        lambda: _revoke(
            lifecycle,
            visibility,
            session,
            _readers(),
        ),
    )


def test_result_contains_relation_evidence_not_read_or_financial_authority() -> None:
    lifecycle, visibility = _stores()
    value = _grant(
        lifecycle,
        visibility,
        FakeSession(True),
        _readers(),
    )
    payload = value.to_dict()
    assert OPERATION == "legal_client_visibility_write"
    assert PERMISSION == "legal_operations:client_visibility:write"
    assert PRODUCTION_VERSION == (
        "v1.0.0-L8-7C3C-CLIENT-MATTER-VISIBILITY-PROVISIONING"
    )
    assert VERSION == (
        "v1.0.0-L8-7C3C-CLIENT-MATTER-VISIBILITY-PROVISIONING-CERT"
    )
    forbidden = {
        "authorized",
        "permission",
        "business_role",
        "role_id",
        "instruction_id",
        "document_id",
        "attempt_id",
        "service_execution_id",
        "return_id",
        "invoice_id",
        "payment_id",
        "settlement_id",
        "paid",
        "settled",
    }
    assert forbidden.isdisjoint(payload)


# SOVEREIGN ARTIFACT SEAL
# ARTIFACT: test_legal_client_matter_visibility_orchestrator.py
# VERSION: v1.0.0-L8-7C3C-CLIENT-MATTER-VISIBILITY-PROVISIONING-CERT
# AUTHORITY BOUNDARY: direct C3C actor/target/matter/visibility composition certificate only
# TENANT POSTURE: exact same tenant/session across current IAM, CaseMatter and visibility persistence
# FAIL-CLOSED POSTURE: denied/inactive/missing authority, absent matter, conflict or revoked currentness rejects
# FINANCIAL EXECUTION AUTHORITY: none; Kennel EOS remains exclusive
# END OF WILSY OS SOVEREIGN ARTIFACT
