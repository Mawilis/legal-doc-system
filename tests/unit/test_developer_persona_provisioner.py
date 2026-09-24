"""Direct unit certificate for the WILSY OS developer legal persona provisioner.

TITLE: WILSY OS Developer Legal Persona Provisioner Direct Certificate
VERSION: v1.0.0-D15G-DEV-LEGAL-PERSONA-PROVISIONER-CERT
AUTHORITY: Wilsy OS Core Governance
EPITOME: Deterministically certifies the non-production owner-authorized legal
         persona admission graph, exact caller transaction propagation, persona
         authority vocabulary, password-policy ordering, and fail-closed
         boundaries without network, MongoDB, secrets, or financial execution.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tests/unit/test_developer_persona_provisioner.py
COLLABORATION / OWNERSHIP: Test-only certificate for
                           tools/eos/auth/developer_persona_provisioner.py;
                           production auth, IAM, Mongo, browser, and Kennel
                           surfaces remain read-only.
CERTIFICATION / UPDATE DATE: 2026-09-24
CHANGELOG:
  v1.0.0-D15G-DEV-LEGAL-PERSONA-PROVISIONER-CERT — Establishes direct evidence
    for explicit non-production enablement, exact owner durable authority,
    canonical tenant scope, password policy before persistence, all eight
    legal-persona mappings, one caller-owned transaction, exact session
    propagation across every authority read/write, full callback replay,
    create-only conflict behavior, bounded secret-free failures, MFA non-bypass,
    and exclusion of JWT/session/refresh/financial execution authority.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2; ISO 27001 awareness.
SECURITY / PRIVACY POSTURE: Synthetic fixture values only. No real password,
                            token, email, tenant, database, network, or provider
                            capability is contacted or persisted.
TENANT BOUNDARY: Every successful scenario is bound to one exact owner tenant;
                 cross-tenant scope fails before password or persistence work.
AUTHORITY BOUNDARY: Certificate only. It proves orchestration behavior but
                    grants no principal, membership, business role, final role,
                    login session, MFA bypass, or browser authority.
FINANCIAL AUTHORITY BOUNDARY: None. Kennel EOS remains the exclusive financial
                              execution authority.
TRANSACTION BOUNDARY: In-memory transaction double records one ClientSession
                      identity across all participating reads and writes.
"""

from __future__ import annotations

import ast
from contextlib import contextmanager
from dataclasses import FrozenInstanceError
from datetime import datetime, timezone
import inspect
from pathlib import Path
from types import SimpleNamespace
from typing import Any, Iterator

import pytest

import tools.eos.auth.developer_persona_provisioner as mod
from tools.eos.auth.identity import SovereignIdentity
from tools.eos.auth.principal_authority import PrincipalAuthority
from tools.eos.auth.principal_status import PrincipalStatus
from tools.eos.auth.role_assignment import RoleAssignmentAuthority, RoleAssignmentStatus
from tools.eos.auth.tenant_business_role import (
    TenantBusinessRoleAuthority,
    TenantBusinessRoleStatus,
)
from tools.eos.auth.tenant_membership import (
    TenantMembershipAuthority,
    TenantMembershipStatus,
)


EXPECTED_VERSION = "v1.0.1-D15G-DEV-LEGAL-PERSONA-PROVISIONER"
CERTIFICATE_VERSION = "v1.0.0-D15G-DEV-LEGAL-PERSONA-PROVISIONER-CERT"
TENANT = "tenant-dev-legal"
OWNER = "owner-principal"
VALID_PASSWORD = "synthetic legal persona passphrase"


class RecordingChecker:
    """Record exact candidate use without external blocklist transport."""

    def __init__(self, blocked: bool = False) -> None:
        self.blocked = blocked
        self.candidates: list[str] = []

    def is_blocked(self, candidate: str) -> bool:
        """Return a deterministic blocklist decision."""
        self.candidates.append(candidate)
        return self.blocked


class FakeSession:
    """Minimal with_transaction double that can replay the complete callback."""

    def __init__(self, owner: "FakeClient") -> None:
        self.owner = owner
        self.replay = False

    def with_transaction(self, callback: Any) -> Any:
        """Invoke the complete callback once or twice using the exact session."""
        self.owner.transaction_calls += 1
        self.owner.trace.append("transaction.callback.enter")
        result = callback(self)
        self.owner.trace.append("transaction.callback.exit")
        if self.replay:
            self.owner.transaction_calls += 1
            self.owner.trace.append("transaction.callback.replay.enter")
            result = callback(self)
            self.owner.trace.append("transaction.callback.replay.exit")
        return result


class FakeClient:
    """Record session ownership without touching PyMongo."""

    def __init__(self) -> None:
        self.session = FakeSession(self)
        self.start_calls = 0
        self.transaction_calls = 0
        self.trace: list[str] = []

    @contextmanager
    def start_session(self) -> Iterator[FakeSession]:
        """Yield the one caller-owned session used by the provisioner."""
        self.start_calls += 1
        self.trace.append("client.start_session")
        yield self.session
        self.trace.append("client.session.exit")


class Harness:
    """Deterministic dependency graph for one provisioner invocation."""

    def __init__(self) -> None:
        self.client = FakeClient()
        self.events: list[dict[str, Any]] = []
        self.principal: PrincipalAuthority | None = PrincipalAuthority(
            OWNER,
            PrincipalStatus.ACTIVE,
            0,
        )
        self.membership: TenantMembershipAuthority | None = TenantMembershipAuthority(
            OWNER,
            TENANT,
            TenantMembershipStatus.ACTIVE,
            0,
        )
        self.business_role: TenantBusinessRoleAuthority | None = TenantBusinessRoleAuthority(
            OWNER,
            TENANT,
            "tenant_owner",
            TenantBusinessRoleStatus.ACTIVE,
            0,
            datetime(2026, 9, 24, tzinfo=timezone.utc),
            None,
        )
        self.authorization_role: RoleAssignmentAuthority | None = RoleAssignmentAuthority(
            OWNER,
            TENANT,
            "ENTERPRISE_ADMIN",
            RoleAssignmentStatus.ACTIVE,
            0,
        )
        self.canonical_tenant = TENANT
        self.credential_conflict = False
        self.fail_stage: str | None = None
        self.created_principal_counter = 0

    def record(self, name: str, session: Any, **payload: Any) -> None:
        """Append one deterministic dependency event."""
        self.events.append({"name": name, "session": session, **payload})

    def maybe_fail(self, stage: str) -> None:
        """Inject one typed repository failure at a selected boundary."""
        if self.fail_stage != stage:
            return
        if stage.startswith("principal."):
            raise mod.PrincipalAuthorityRepositoryError("synthetic persistence detail")
        if stage.startswith("membership."):
            raise mod.TenantMembershipRepositoryError("synthetic persistence detail")
        if stage.startswith("business."):
            raise mod.TenantBusinessRoleRepositoryError("synthetic persistence detail")
        if stage.startswith("role."):
            raise mod.RoleAssignmentRepositoryError("synthetic persistence detail")
        raise AssertionError(f"unsupported fail stage: {stage}")


def _identity(tenant_id: str = TENANT) -> SovereignIdentity:
    """Build one authenticated owner projection; durable authority is separate."""
    return SovereignIdentity(
        identity_id=OWNER,
        tenant_id=tenant_id,
        username="owner",
        email="owner@example.invalid",
        roles=["IGNORED_PROJECTION_ROLE"],
        permissions=["*"],
        auth_method="TEST",
        status=PrincipalStatus.ACTIVE,
    )


@pytest.fixture()
def harness(monkeypatch: pytest.MonkeyPatch) -> Harness:
    """Install deterministic repository, tenant, auth, and client doubles."""
    h = Harness()

    class PrincipalRepo:
        @staticmethod
        def resolve(principal_id: str, *, session: Any = None) -> PrincipalAuthority:
            h.record("principal.resolve", session, principal_id=principal_id)
            h.maybe_fail("principal.resolve")
            if h.principal is None:
                raise mod.PrincipalAuthorityNotFoundError("not found")
            return h.principal

        @staticmethod
        def create(value: PrincipalAuthority, *, session: Any = None) -> PrincipalAuthority:
            h.record("principal.create", session, value=value)
            h.maybe_fail("principal.create")
            return value

    class MembershipRepo:
        @staticmethod
        def resolve(
            principal_id: str,
            tenant_id: str,
            *,
            session: Any = None,
        ) -> TenantMembershipAuthority:
            h.record(
                "membership.resolve",
                session,
                principal_id=principal_id,
                tenant_id=tenant_id,
            )
            h.maybe_fail("membership.resolve")
            if h.membership is None:
                raise mod.TenantMembershipNotFoundError("not found")
            return h.membership

        @staticmethod
        def insert(
            value: TenantMembershipAuthority,
            *,
            session: Any = None,
        ) -> TenantMembershipAuthority:
            h.record("membership.insert", session, value=value)
            h.maybe_fail("membership.insert")
            return value

    class BusinessRoleRepo:
        @staticmethod
        def resolve(
            principal_id: str,
            tenant_id: str,
            *,
            session: Any = None,
        ) -> TenantBusinessRoleAuthority:
            h.record(
                "business.resolve",
                session,
                principal_id=principal_id,
                tenant_id=tenant_id,
            )
            h.maybe_fail("business.resolve")
            if h.business_role is None:
                raise mod.TenantBusinessRoleNotFoundError("not found")
            return h.business_role

        @staticmethod
        def insert(
            value: TenantBusinessRoleAuthority,
            *,
            session: Any = None,
        ) -> TenantBusinessRoleAuthority:
            h.record("business.insert", session, value=value)
            h.maybe_fail("business.insert")
            return value

    class RoleRepo:
        @staticmethod
        def resolve(
            principal_id: str,
            tenant_id: str,
            role_id: str,
            *,
            session: Any = None,
        ) -> RoleAssignmentAuthority:
            h.record(
                "role.resolve",
                session,
                principal_id=principal_id,
                tenant_id=tenant_id,
                role_id=role_id,
            )
            h.maybe_fail("role.resolve")
            if h.authorization_role is None:
                raise mod.RoleAssignmentNotFoundError("not found")
            return h.authorization_role

        @staticmethod
        def insert(
            value: RoleAssignmentAuthority,
            *,
            session: Any = None,
        ) -> RoleAssignmentAuthority:
            h.record("role.insert", session, value=value)
            h.maybe_fail("role.insert")
            return value

    class TenantRegistry:
        @staticmethod
        def resolve_canonical_tenant(
            tenant_id: str,
            *,
            session: Any = None,
        ) -> SimpleNamespace:
            h.record("tenant.resolve", session, tenant_id=tenant_id)
            if h.fail_stage == "tenant.resolve":
                raise mod.TenantRegistryError("synthetic tenant detail")
            return SimpleNamespace(tenant_id=h.canonical_tenant)

    class FakeAuthRegistry:
        def register_user(
            self,
            email: str,
            password: str,
            first_name: str,
            last_name: str,
            role: str,
            tenant_id: str,
            *,
            session: Any = None,
        ) -> SimpleNamespace:
            h.record(
                "credential.register",
                session,
                email=email,
                password=password,
                first_name=first_name,
                last_name=last_name,
                role=role,
                tenant_id=tenant_id,
            )
            if h.credential_conflict:
                raise ValueError("Email already exists")
            h.created_principal_counter += 1
            return SimpleNamespace(id=f"persona-principal-{h.created_principal_counter}")

    monkeypatch.setattr(mod, "PrincipalAuthorityRepository", PrincipalRepo)
    monkeypatch.setattr(mod, "TenantMembershipRepository", MembershipRepo)
    monkeypatch.setattr(mod, "TenantBusinessRoleRepository", BusinessRoleRepo)
    monkeypatch.setattr(mod, "RoleAssignmentRepository", RoleRepo)
    monkeypatch.setattr(mod, "TenantRegistry", TenantRegistry)
    monkeypatch.setattr(mod, "AuthRegistry", FakeAuthRegistry)
    monkeypatch.setattr(mod, "get_client", lambda: h.client)
    monkeypatch.setenv("ENV", "development")
    monkeypatch.setenv("WILSY_DEVELOPER_PERSONA_PROVISIONING", "1")
    return h


def _provision(
    harness: Harness,
    *,
    persona: mod.DeveloperLegalPersona = mod.DeveloperLegalPersona.LEGAL_PARTNER,
    identity: SovereignIdentity | None = None,
    tenant_id: str = TENANT,
    password: str = VALID_PASSWORD,
    checker: RecordingChecker | None = None,
) -> mod.DeveloperPersonaProvisioningResult:
    """Invoke the governed surface with synthetic, explicit inputs."""
    chosen_checker = checker or RecordingChecker(False)
    return mod.provision_developer_legal_persona(
        owner_identity=identity or _identity(),
        tenant_id=tenant_id,
        email="persona@example.invalid",
        password=password,
        first_name="Persona",
        last_name="Tester",
        persona=persona,
        password_blocklist_checker=chosen_checker,
        auth_registry=mod.AuthRegistry(),
    )


def test_version_signature_and_certificate_contract() -> None:
    """Freeze the production version and public provisioning surface."""
    assert mod.VERSION == EXPECTED_VERSION
    assert CERTIFICATE_VERSION in Path(__file__).read_text(encoding="utf-8")
    assert list(inspect.signature(mod.provision_developer_legal_persona).parameters) == [
        "owner_identity",
        "tenant_id",
        "email",
        "password",
        "first_name",
        "last_name",
        "persona",
        "password_blocklist_checker",
        "auth_registry",
    ]
    assert inspect.signature(
        mod.provision_developer_legal_persona
    ).parameters["auth_registry"].default is None


@pytest.mark.parametrize(
    ("environment", "flag"),
    [
        ("production", "1"),
        ("prod", "1"),
        ("", "1"),
        ("development", "0"),
        ("development", ""),
        ("test", "false"),
    ],
)
def test_environment_requires_explicit_nonproduction_and_enablement(
    harness: Harness,
    monkeypatch: pytest.MonkeyPatch,
    environment: str,
    flag: str,
) -> None:
    """Neither environment nor feature flag alone can enable provisioning."""
    monkeypatch.setenv("ENV", environment)
    monkeypatch.setenv("WILSY_DEVELOPER_PERSONA_PROVISIONING", flag)
    checker = RecordingChecker(False)
    with pytest.raises(mod.DeveloperPersonaProvisioningError) as caught:
        _provision(harness, checker=checker)
    assert caught.value.code is mod.DeveloperPersonaProvisioningCode.ENVIRONMENT_DENIED
    assert harness.client.start_calls == 0
    assert checker.candidates == []
    assert harness.events == []


def test_cross_tenant_scope_fails_before_password_or_persistence(
    harness: Harness,
) -> None:
    """Authenticated owner projection cannot redirect provisioning cross-tenant."""
    checker = RecordingChecker(False)
    with pytest.raises(mod.DeveloperPersonaProvisioningError) as caught:
        _provision(
            harness,
            identity=_identity("tenant-other"),
            tenant_id=TENANT,
            checker=checker,
        )
    assert caught.value.code is mod.DeveloperPersonaProvisioningCode.OWNER_SCOPE_MISMATCH
    assert checker.candidates == []
    assert harness.client.start_calls == 0
    assert harness.events == []


def test_password_policy_rejects_before_client_or_transaction(
    harness: Harness,
) -> None:
    """Invalid prospective password never reaches persistence."""
    checker = RecordingChecker(False)
    with pytest.raises(mod.DeveloperPersonaProvisioningError) as caught:
        _provision(harness, password="too-short", checker=checker)
    assert caught.value.code is mod.DeveloperPersonaProvisioningCode.PASSWORD_REJECTED
    assert harness.client.start_calls == 0
    assert harness.events == []


def test_success_creates_exact_five_fact_graph_in_one_session(
    harness: Harness,
) -> None:
    """Credential plus four governed authority facts share one transaction."""
    checker = RecordingChecker(False)
    result = _provision(harness, checker=checker)

    assert result.principal_id == "persona-principal-1"
    assert result.tenant_id == TENANT
    assert result.persona is mod.DeveloperLegalPersona.LEGAL_PARTNER
    assert result.business_role == "tenant_legal_partner"
    assert result.authorization_role == "LEGAL_PARTNER"
    assert result.credential_revision == 0
    assert result.mfa_enrollment_required is True
    assert checker.candidates == [VALID_PASSWORD]
    assert harness.client.start_calls == 1
    assert harness.client.transaction_calls == 1

    names = [event["name"] for event in harness.events]
    assert names == [
        "tenant.resolve",
        "principal.resolve",
        "membership.resolve",
        "business.resolve",
        "role.resolve",
        "credential.register",
        "principal.create",
        "membership.insert",
        "business.insert",
        "role.insert",
    ]
    assert all(event["session"] is harness.client.session for event in harness.events)

    credential = harness.events[5]
    assert credential["role"] == "LEGAL_PARTNER"
    assert credential["tenant_id"] == TENANT

    principal = harness.events[6]["value"]
    membership = harness.events[7]["value"]
    business = harness.events[8]["value"]
    role = harness.events[9]["value"]

    assert isinstance(principal, PrincipalAuthority)
    assert principal.principal_id == result.principal_id
    assert principal.status is PrincipalStatus.ACTIVE
    assert principal.revision == 0

    assert isinstance(membership, TenantMembershipAuthority)
    assert membership.principal_id == result.principal_id
    assert membership.tenant_id == TENANT
    assert membership.status is TenantMembershipStatus.ACTIVE
    assert membership.revision == 0

    assert isinstance(business, TenantBusinessRoleAuthority)
    assert business.principal_id == result.principal_id
    assert business.tenant_id == TENANT
    assert business.business_role == "tenant_legal_partner"
    assert business.status is TenantBusinessRoleStatus.ACTIVE
    assert business.revision == 0
    assert business.effective_at.tzinfo is not None
    assert business.revoked_at is None

    assert isinstance(role, RoleAssignmentAuthority)
    assert role.principal_id == result.principal_id
    assert role.tenant_id == TENANT
    assert role.role_id == "LEGAL_PARTNER"
    assert role.status is RoleAssignmentStatus.ACTIVE
    assert role.revision == 0

    with pytest.raises(FrozenInstanceError):
        result.principal_id = "mutation-forbidden"  # type: ignore[misc]


@pytest.mark.parametrize(
    ("persona", "business_role", "authorization_role"),
    [
        (mod.DeveloperLegalPersona.LEGAL_PARTNER, "tenant_legal_partner", "LEGAL_PARTNER"),
        (mod.DeveloperLegalPersona.LEGAL_ATTORNEY, "tenant_legal_attorney", "LEGAL_ATTORNEY"),
        (mod.DeveloperLegalPersona.LEGAL_PARALEGAL, "tenant_legal_paralegal", "LEGAL_PARALEGAL"),
        (mod.DeveloperLegalPersona.LEGAL_SECRETARY, "tenant_legal_secretary", "LEGAL_SECRETARY"),
        (mod.DeveloperLegalPersona.LEGAL_FINANCE, "tenant_legal_finance", "LEGAL_FINANCE"),
        (mod.DeveloperLegalPersona.SHERIFF, "tenant_sheriff", "SHERIFF"),
        (mod.DeveloperLegalPersona.DEPUTY, "tenant_deputy", "DEPUTY"),
        (mod.DeveloperLegalPersona.LEGAL_CLIENT, "tenant_legal_client", "LEGAL_CLIENT"),
    ],
)
def test_all_persona_authority_pairs_are_exact(
    harness: Harness,
    persona: mod.DeveloperLegalPersona,
    business_role: str,
    authorization_role: str,
) -> None:
    """Every supported persona maps to exactly one established authority pair."""
    result = _provision(harness, persona=persona)
    assert result.business_role == business_role
    assert result.authorization_role == authorization_role
    credential = next(
        event for event in harness.events if event["name"] == "credential.register"
    )
    assert credential["role"] == authorization_role
    business = next(
        event["value"] for event in harness.events if event["name"] == "business.insert"
    )
    assignment = next(
        event["value"] for event in harness.events if event["name"] == "role.insert"
    )
    assert business.business_role == business_role
    assert assignment.role_id == authorization_role


def test_owner_principal_absence_and_inactive_state_fail_closed(
    harness: Harness,
) -> None:
    """Projection claims never substitute for durable ACTIVE principal authority."""
    harness.principal = None
    with pytest.raises(mod.DeveloperPersonaProvisioningError) as missing:
        _provision(harness)
    assert missing.value.code is mod.DeveloperPersonaProvisioningCode.OWNER_PRINCIPAL_NOT_FOUND
    assert not any(event["name"] == "credential.register" for event in harness.events)

    harness.events.clear()
    harness.principal = PrincipalAuthority(OWNER, PrincipalStatus.SUSPENDED, 1)
    with pytest.raises(mod.DeveloperPersonaProvisioningError) as inactive:
        _provision(harness)
    assert inactive.value.code is mod.DeveloperPersonaProvisioningCode.OWNER_PRINCIPAL_INACTIVE
    assert not any(event["name"] == "credential.register" for event in harness.events)


def test_owner_membership_business_role_and_enterprise_admin_are_all_required(
    harness: Harness,
) -> None:
    """Owner authorization is conjunctive and re-resolved durably."""
    harness.membership = None
    with pytest.raises(mod.DeveloperPersonaProvisioningError) as missing_membership:
        _provision(harness)
    assert missing_membership.value.code is mod.DeveloperPersonaProvisioningCode.OWNER_MEMBERSHIP_NOT_FOUND

    harness.events.clear()
    harness.membership = TenantMembershipAuthority(
        OWNER,
        TENANT,
        TenantMembershipStatus.SUSPENDED,
        1,
    )
    with pytest.raises(mod.DeveloperPersonaProvisioningError) as inactive_membership:
        _provision(harness)
    assert inactive_membership.value.code is mod.DeveloperPersonaProvisioningCode.OWNER_MEMBERSHIP_INACTIVE

    harness.events.clear()
    harness.membership = TenantMembershipAuthority(
        OWNER,
        TENANT,
        TenantMembershipStatus.ACTIVE,
        0,
    )
    harness.business_role = TenantBusinessRoleAuthority(
        OWNER,
        TENANT,
        "tenant_admin",
        TenantBusinessRoleStatus.ACTIVE,
        0,
        datetime(2026, 9, 24, tzinfo=timezone.utc),
        None,
    )
    with pytest.raises(mod.DeveloperPersonaProvisioningError) as bad_business:
        _provision(harness)
    assert bad_business.value.code is mod.DeveloperPersonaProvisioningCode.OWNER_BUSINESS_ROLE_INVALID

    harness.events.clear()
    harness.business_role = TenantBusinessRoleAuthority(
        OWNER,
        TENANT,
        "tenant_owner",
        TenantBusinessRoleStatus.ACTIVE,
        0,
        datetime(2026, 9, 24, tzinfo=timezone.utc),
        None,
    )
    harness.authorization_role = None
    with pytest.raises(mod.DeveloperPersonaProvisioningError) as missing_role:
        _provision(harness)
    assert missing_role.value.code is mod.DeveloperPersonaProvisioningCode.OWNER_AUTHORIZATION_ROLE_NOT_FOUND

    harness.events.clear()
    harness.authorization_role = RoleAssignmentAuthority(
        OWNER,
        TENANT,
        "ENTERPRISE_ADMIN",
        RoleAssignmentStatus.REVOKED,
        1,
    )
    with pytest.raises(mod.DeveloperPersonaProvisioningError) as inactive_role:
        _provision(harness)
    assert inactive_role.value.code is mod.DeveloperPersonaProvisioningCode.OWNER_AUTHORIZATION_ROLE_INACTIVE


def test_canonical_tenant_mismatch_fails_before_credential_creation(
    harness: Harness,
) -> None:
    """Canonical tenant resolution cannot silently redirect target authority."""
    harness.canonical_tenant = "tenant-other"
    with pytest.raises(mod.DeveloperPersonaProvisioningError) as caught:
        _provision(harness)
    assert caught.value.code is mod.DeveloperPersonaProvisioningCode.TENANT_INVALID
    assert [event["name"] for event in harness.events] == ["tenant.resolve"]


def test_credential_conflict_and_repository_failure_are_bounded(
    harness: Harness,
) -> None:
    """Create-only conflicts and infrastructure failures never become success."""
    harness.credential_conflict = True
    with pytest.raises(mod.DeveloperPersonaProvisioningError) as conflict:
        _provision(harness)
    assert conflict.value.code is mod.DeveloperPersonaProvisioningCode.CREDENTIAL_CONFLICT
    assert not any(event["name"].endswith(".create") for event in harness.events)
    assert not any(event["name"].endswith(".insert") for event in harness.events)

    harness.events.clear()
    harness.credential_conflict = False
    harness.fail_stage = "principal.create"
    with pytest.raises(mod.DeveloperPersonaProvisioningError) as persistence:
        _provision(harness)
    assert persistence.value.code is mod.DeveloperPersonaProvisioningCode.PERSISTENCE_FAILURE
    assert "synthetic persistence detail" not in str(persistence.value)
    assert not any(
        event["name"] in {"membership.insert", "business.insert", "role.insert"}
        for event in harness.events
    )


def test_complete_transaction_callback_replays_all_authority_work(
    harness: Harness,
) -> None:
    """A PyMongo callback retry re-enters the complete governed authority graph."""
    harness.client.session.replay = True
    result = _provision(harness)
    assert harness.client.start_calls == 1
    assert harness.client.transaction_calls == 2
    assert result.principal_id == "persona-principal-2"

    for name in (
        "tenant.resolve",
        "principal.resolve",
        "membership.resolve",
        "business.resolve",
        "role.resolve",
        "credential.register",
        "principal.create",
        "membership.insert",
        "business.insert",
        "role.insert",
    ):
        assert sum(event["name"] == name for event in harness.events) == 2

    assert all(event["session"] is harness.client.session for event in harness.events)


def test_error_and_result_surfaces_do_not_expose_password_material(
    harness: Harness,
) -> None:
    """Bounded failures and committed result omit prospective password/hash state."""
    secret = "synthetic highly private password phrase"
    harness.credential_conflict = True
    with pytest.raises(mod.DeveloperPersonaProvisioningError) as caught:
        _provision(harness, password=secret)
    assert secret not in str(caught.value)
    assert secret not in repr(caught.value)

    harness.events.clear()
    harness.credential_conflict = False
    result = _provision(harness, password=secret)
    assert secret not in repr(result)
    assert "password" not in vars(result)
    assert "hash" not in vars(result)


def test_source_excludes_login_mfa_bypass_transport_and_financial_execution() -> None:
    """Static evidence keeps the provisioner out of adjacent execution authority."""
    source_path = Path(mod.__file__).resolve()
    source = source_path.read_text(encoding="utf-8")
    tree = ast.parse(source, filename=str(source_path))

    called_attributes = {
        node.func.attr
        for node in ast.walk(tree)
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute)
    }
    forbidden_calls = {
        "create_session",
        "generate_jwt",
        "generate_access_jwt",
        "generate_pre_auth_jwt",
        "generate_refresh_token",
        "create_otp_secret",
        "verify_otp",
    }
    assert forbidden_calls.isdisjoint(called_attributes)

    imported_modules: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imported_modules.update(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            imported_modules.add(node.module)
    assert not any(module.startswith("fastapi") for module in imported_modules)
    assert not any(".billing" in module for module in imported_modules)
    assert not any("kennel" in module.lower() for module in imported_modules)


def test_structural_sovereign_contract_is_exact() -> None:
    """Freeze header, version agreement, seal, and placeholder absence."""
    source = Path(mod.__file__).read_text(encoding="utf-8")
    for field in (
        "TITLE:",
        "VERSION:",
        "AUTHORITY:",
        "EPITOME:",
        "ABSOLUTE CANONICAL PATH:",
        "COLLABORATION / OWNERSHIP:",
        "CERTIFICATION / UPDATE DATE:",
        "CHANGELOG:",
        "COMPLIANCE:",
        "SECURITY / PRIVACY POSTURE:",
        "TENANT BOUNDARY:",
        "AUTHORITY BOUNDARY:",
        "FINANCIAL AUTHORITY BOUNDARY:",
    ):
        assert field in source
    assert source.count(EXPECTED_VERSION) == 4
    assert "TODO" not in source
    assert "FIXME" not in source
    assert source.rstrip().endswith("# END OF WILSY OS SOVEREIGN ARTIFACT")


# ARTIFACT: tests/unit/test_developer_persona_provisioner.py
# VERSION: v1.0.0-D15G-DEV-LEGAL-PERSONA-PROVISIONER-CERT
# AUTHORITY BOUNDARY: direct offline evidence for development-only legal persona admission orchestration
# TENANT POSTURE: exact owner tenant and same-session durable authority composition only
# FAIL-CLOSED POSTURE: environment, scope, password, owner authority, tenant, conflict, and persistence failures deny
# FINANCIAL EXECUTION AUTHORITY: none; Kennel EOS remains exclusive
# END OF WILSY OS SOVEREIGN ARTIFACT
