"""Real-Mongo certificate for the WILSY OS developer legal persona provisioner.

TITLE: WILSY OS Developer Legal Persona Provisioner Real-Mongo Certificate
VERSION: v1.0.0-D15G-DEV-LEGAL-PERSONA-REAL-MONGO-CERT
AUTHORITY: Wilsy OS Core Governance
EPITOME: Certifies the development-only legal persona admission graph against a
         UUID-isolated local MongoDB replica-set database, including durable
         authority composition, transaction rollback, secret hygiene, production
         denial, and absence of login/MFA/financial side effects.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tests/integration/test_developer_persona_provisioner_real_mongo.py
COLLABORATION / OWNERSHIP: Integration evidence only. Production provisioner,
                           AuthRegistry, tenant registry, IAM repositories, and
                           Kernel database lifecycle remain unchanged.
CERTIFICATION / UPDATE DATE: 2026-09-24
CHANGELOG:
  v1.0.0-D15G-DEV-LEGAL-PERSONA-REAL-MONGO-CERT — Establishes host-backed
    evidence for all eight legal persona authority pairs, exact owner-tenant
    admission, canonical credential persistence, no session/refresh/OTP
    issuance, password non-persistence, production fail-closed behavior, and
    real transaction rollback when downstream authority creation conflicts.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2; ISO 27001 awareness.
SECURITY / PRIVACY POSTURE: Synthetic identities and passwords only. The
                            password blocklist capability is deterministic and
                            offline; no production secrets or external provider
                            traffic are used.
TENANT BOUNDARY: Every scenario uses one UUID-isolated database and exact
                 synthetic tenant. The owner projection and durable owner
                 authority must match that tenant.
AUTHORITY BOUNDARY: Evidence only. This certificate creates only disposable
                    synthetic auth/IAM facts inside its isolated database.
FINANCIAL AUTHORITY BOUNDARY: None. Kennel EOS remains the exclusive financial
                              execution authority.
TRANSACTION BOUNDARY: Production provisioner owns the PyMongo session and
                      with_transaction callback. Rollback evidence is read from
                      MongoDB after an induced downstream authority conflict.
FAIL-CLOSED DECLARATION: Missing MongoDB, wrong replica-set identity, or absence
                         of a writable primary is a certification failure, not
                         a passing skip.
"""

from __future__ import annotations

from collections.abc import Generator
from dataclasses import dataclass
from datetime import datetime, timezone
import os
import uuid

import pytest
from pymongo import MongoClient
from pymongo.database import Database
from pymongo.errors import PyMongoError

import tools.eos.auth.developer_persona_provisioner as provisioner
import tools.eos.kernel.db as kernel_db
import tools.eos.saas.auth.auth_registry as auth_registry_module
from tools.eos.auth.identity import SovereignIdentity
from tools.eos.auth.principal_authority import PrincipalAuthority
from tools.eos.auth.principal_authority_repository import PrincipalAuthorityRepository
from tools.eos.auth.principal_status import PrincipalStatus
from tools.eos.auth.role_assignment import RoleAssignmentAuthority, RoleAssignmentStatus
from tools.eos.auth.role_assignment_repository import RoleAssignmentRepository
from tools.eos.auth.tenant_business_role import (
    TenantBusinessRoleAuthority,
    TenantBusinessRoleStatus,
)
from tools.eos.auth.tenant_business_role_repository import TenantBusinessRoleRepository
from tools.eos.auth.tenant_membership import (
    TenantMembershipAuthority,
    TenantMembershipStatus,
)
from tools.eos.auth.tenant_membership_repository import TenantMembershipRepository
from tools.eos.saas.tenancy.tenant_registry import TenantRegistry


VERSION = "v1.0.0-D15G-DEV-LEGAL-PERSONA-REAL-MONGO-CERT"
EXPECTED_PRODUCTION_VERSION = "v1.0.1-D15G-DEV-LEGAL-PERSONA-PROVISIONER"
DEFAULT_URI = "mongodb://127.0.0.1:27027/?replicaSet=wilsyVendorCertRS"
EXPECTED_REPLICA_SET = "wilsyVendorCertRS"
RAW_PASSWORD = "D15G synthetic persona access 2026!"


class AllowBlocklist:
    """Offline blocklist capability that records exact candidate use."""

    def __init__(self) -> None:
        self.candidates: list[str] = []

    def is_blocked(self, candidate: str) -> bool:
        """Permit the synthetic candidate without network or persistence."""
        self.candidates.append(candidate)
        return False


@dataclass(frozen=True, slots=True)
class Runtime:
    """Isolated real-Mongo certificate graph."""

    client: MongoClient
    database: Database
    tenant_id: str
    owner_id: str
    identity: SovereignIdentity


def _active_owner_business(owner_id: str, tenant_id: str) -> TenantBusinessRoleAuthority:
    """Build the exact durable tenant-owner business role."""
    return TenantBusinessRoleAuthority(
        owner_id,
        tenant_id,
        "tenant_owner",
        TenantBusinessRoleStatus.ACTIVE,
        0,
        datetime.now(timezone.utc),
        None,
    )


def _seed_owner_graph(database: Database, owner_id: str, tenant_id: str) -> None:
    """Create canonical ACTIVE owner authority required by the provisioner."""
    PrincipalAuthorityRepository.ensure_indexes(database["principal_authorities"])
    TenantMembershipRepository.ensure_indexes(database["tenant_memberships"])
    TenantBusinessRoleRepository.ensure_indexes(database["tenant_business_roles"])
    RoleAssignmentRepository.ensure_indexes(database["role_assignments"])

    PrincipalAuthorityRepository.create(
        PrincipalAuthority(owner_id, PrincipalStatus.ACTIVE, 0),
        collection=database["principal_authorities"],
    )
    TenantMembershipRepository.insert(
        TenantMembershipAuthority(
            owner_id,
            tenant_id,
            TenantMembershipStatus.ACTIVE,
            0,
        ),
        collection=database["tenant_memberships"],
    )
    TenantBusinessRoleRepository.insert(
        _active_owner_business(owner_id, tenant_id),
        collection=database["tenant_business_roles"],
    )
    RoleAssignmentRepository.insert(
        RoleAssignmentAuthority(
            owner_id,
            tenant_id,
            "ENTERPRISE_ADMIN",
            RoleAssignmentStatus.ACTIVE,
            0,
        ),
        collection=database["role_assignments"],
    )


def _seed_tenant(database: Database, tenant_id: str) -> None:
    """Create one ACTIVE canonical tenant using the production registry."""
    database["tenants"].create_index(
        [("tenant_id", 1)],
        unique=True,
        name="tenant_id_unique",
    )
    result = TenantRegistry.create(
        {
            "tenant_id": tenant_id,
            "name": "D15G Synthetic Legal Tenant",
            "organization_name": "D15G Synthetic Legal Tenant",
            "industry": "legal",
            "plan": "COMMUNITY",
            "status": "ACTIVE",
            "verified": True,
        }
    )
    assert result.get("success") is True


def _ensure_auth_indexes(database: Database) -> None:
    """Create the isolated credential uniqueness constraints used by certification."""
    database["users"].create_index(
        [("email", 1)],
        unique=True,
        name="auth_email_unique",
    )
    database["users"].create_index(
        [("user_id", 1)],
        unique=True,
        name="auth_user_id_unique",
    )


@pytest.fixture()
def runtime(monkeypatch: pytest.MonkeyPatch) -> Generator[Runtime, None, None]:
    """Bind production persistence seams to one disposable replica-set database."""
    uri = os.getenv("TEST_VENDOR_MONGO_URI", DEFAULT_URI)
    client = MongoClient(
        uri,
        serverSelectionTimeoutMS=3000,
        retryWrites=True,
        retryReads=True,
    )
    try:
        hello = client.admin.command("hello")
    except PyMongoError as error:
        client.close()
        pytest.fail(f"REAL_MONGO_CERTIFICATION_BLOCKED: {type(error).__name__}")

    if hello.get("setName") != EXPECTED_REPLICA_SET:
        client.close()
        pytest.fail("REAL_MONGO_CERTIFICATION_BLOCKED: unexpected replica set")
    if hello.get("isWritablePrimary", hello.get("ismaster")) is not True:
        client.close()
        pytest.fail("REAL_MONGO_CERTIFICATION_BLOCKED: no writable primary")

    database_name = f"wilsy_d15g_persona_{uuid.uuid4().hex}"
    database = client[database_name]
    tenant_id = f"TENANT-D15G-{uuid.uuid4().hex.upper()}"
    owner_id = f"OWNER-D15G-{uuid.uuid4().hex}"

    monkeypatch.setattr(kernel_db, "get_database", lambda: database)
    monkeypatch.setattr(provisioner, "get_client", lambda: client)
    monkeypatch.setenv("ENV", "test")
    monkeypatch.setenv("WILSY_DEVELOPER_PERSONA_PROVISIONING", "1")

    _ensure_auth_indexes(database)
    _seed_tenant(database, tenant_id)
    _seed_owner_graph(database, owner_id, tenant_id)

    identity = SovereignIdentity(
        identity_id=owner_id,
        tenant_id=tenant_id,
        username="synthetic-owner",
        email="synthetic-owner@example.com",
        roles=["IGNORED_PROJECTION_ROLE"],
        permissions=["*"],
        auth_method="REAL_MONGO_CERT",
        status=PrincipalStatus.ACTIVE,
    )

    try:
        yield Runtime(client, database, tenant_id, owner_id, identity)
    finally:
        client.drop_database(database_name)
        client.close()


def _provision(
    runtime: Runtime,
    persona: provisioner.DeveloperLegalPersona,
    *,
    email: str,
    checker: AllowBlocklist | None = None,
) -> provisioner.DeveloperPersonaProvisioningResult:
    """Invoke unchanged production orchestration against the isolated database."""
    selected_checker = checker or AllowBlocklist()
    return provisioner.provision_developer_legal_persona(
        owner_identity=runtime.identity,
        tenant_id=runtime.tenant_id,
        email=email,
        password=RAW_PASSWORD,
        first_name="Synthetic",
        last_name="Persona",
        persona=persona,
        password_blocklist_checker=selected_checker,
    )


def test_real_mongo_version_and_replica_contract(runtime: Runtime) -> None:
    """Freeze production version and prove isolated host-backed persistence."""
    assert provisioner.VERSION == EXPECTED_PRODUCTION_VERSION
    assert runtime.database.name.startswith("wilsy_d15g_persona_")
    hello = runtime.client.admin.command("hello")
    assert hello["setName"] == EXPECTED_REPLICA_SET
    assert hello.get("isWritablePrimary", hello.get("ismaster")) is True


@pytest.mark.parametrize(
    ("persona", "business_role", "authorization_role"),
    [
        (
            provisioner.DeveloperLegalPersona.LEGAL_PARTNER,
            "tenant_legal_partner",
            "LEGAL_PARTNER",
        ),
        (
            provisioner.DeveloperLegalPersona.LEGAL_ATTORNEY,
            "tenant_legal_attorney",
            "LEGAL_ATTORNEY",
        ),
        (
            provisioner.DeveloperLegalPersona.LEGAL_PARALEGAL,
            "tenant_legal_paralegal",
            "LEGAL_PARALEGAL",
        ),
        (
            provisioner.DeveloperLegalPersona.LEGAL_SECRETARY,
            "tenant_legal_secretary",
            "LEGAL_SECRETARY",
        ),
        (
            provisioner.DeveloperLegalPersona.LEGAL_FINANCE,
            "tenant_legal_finance",
            "LEGAL_FINANCE",
        ),
        (
            provisioner.DeveloperLegalPersona.SHERIFF,
            "tenant_sheriff",
            "SHERIFF",
        ),
        (
            provisioner.DeveloperLegalPersona.DEPUTY,
            "tenant_deputy",
            "DEPUTY",
        ),
        (
            provisioner.DeveloperLegalPersona.LEGAL_CLIENT,
            "tenant_legal_client",
            "LEGAL_CLIENT",
        ),
    ],
)
def test_real_mongo_all_personas_commit_exact_authority_graph(
    runtime: Runtime,
    persona: provisioner.DeveloperLegalPersona,
    business_role: str,
    authorization_role: str,
) -> None:
    """Each canonical persona durably commits credential plus four authority facts."""
    checker = AllowBlocklist()
    email = f"d15g-{persona.value.lower()}-{uuid.uuid4().hex}@example.com"
    result = _provision(runtime, persona, email=email, checker=checker)

    assert checker.candidates == [RAW_PASSWORD]
    assert result.tenant_id == runtime.tenant_id
    assert result.persona is persona
    assert result.business_role == business_role
    assert result.authorization_role == authorization_role
    assert result.credential_revision == 0
    assert result.mfa_enrollment_required is True

    user = runtime.database["users"].find_one(
        {
            "user_id": result.principal_id,
            "tenantId": runtime.tenant_id,
        }
    )
    assert user is not None
    assert user["email"] == email
    assert user["role"] == authorization_role
    assert user["permissions"] == []
    assert user["credential_revision"] == 0
    assert user["mfaRegistered"] is False
    assert user["hasSignedCovenant"] is False
    assert isinstance(user["passwordHash"], str)
    assert user["passwordHash"] != RAW_PASSWORD
    assert RAW_PASSWORD not in repr(user)

    principal = PrincipalAuthorityRepository.resolve(
        result.principal_id,
        collection=runtime.database["principal_authorities"],
    )
    assert principal.status is PrincipalStatus.ACTIVE
    assert principal.revision == 0

    membership = TenantMembershipRepository.resolve(
        result.principal_id,
        runtime.tenant_id,
        collection=runtime.database["tenant_memberships"],
    )
    assert membership.status is TenantMembershipStatus.ACTIVE
    assert membership.revision == 0

    durable_business = TenantBusinessRoleRepository.resolve(
        result.principal_id,
        runtime.tenant_id,
        collection=runtime.database["tenant_business_roles"],
    )
    assert durable_business.business_role == business_role
    assert durable_business.status is TenantBusinessRoleStatus.ACTIVE
    assert durable_business.revision == 0
    assert durable_business.revoked_at is None

    durable_role = RoleAssignmentRepository.resolve(
        result.principal_id,
        runtime.tenant_id,
        authorization_role,
        collection=runtime.database["role_assignments"],
    )
    assert durable_role.status is RoleAssignmentStatus.ACTIVE
    assert durable_role.revision == 0

    assert runtime.database["sessions"].count_documents(
        {"user_id": result.principal_id}
    ) == 0
    assert runtime.database["refresh_tokens"].count_documents(
        {"user_id": result.principal_id}
    ) == 0
    assert runtime.database["otp_secrets"].count_documents(
        {"user_id": result.principal_id}
    ) == 0


def test_real_mongo_owner_authority_is_not_mutated(runtime: Runtime) -> None:
    """Provisioning a persona leaves every durable owner fact byte-equivalent."""
    collections_and_filters = (
        (
            "principal_authorities",
            {"principal_id": runtime.owner_id},
        ),
        (
            "tenant_memberships",
            {"principal_id": runtime.owner_id, "tenant_id": runtime.tenant_id},
        ),
        (
            "tenant_business_roles",
            {"principal_id": runtime.owner_id, "tenant_id": runtime.tenant_id},
        ),
        (
            "role_assignments",
            {
                "principal_id": runtime.owner_id,
                "tenant_id": runtime.tenant_id,
                "role_id": "ENTERPRISE_ADMIN",
            },
        ),
    )
    before = {
        name: runtime.database[name].find_one(predicate)
        for name, predicate in collections_and_filters
    }

    _provision(
        runtime,
        provisioner.DeveloperLegalPersona.LEGAL_PARTNER,
        email=f"owner-preservation-{uuid.uuid4().hex}@example.com",
    )

    after = {
        name: runtime.database[name].find_one(predicate)
        for name, predicate in collections_and_filters
    }
    assert after == before


def test_real_mongo_downstream_authority_conflict_rolls_back_credential(
    runtime: Runtime,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """A post-credential principal conflict aborts the entire Mongo transaction."""
    fixed_uuid = uuid.UUID("12345678-1234-5678-1234-567812345678")
    target_principal = f"WILSYAUTH-{fixed_uuid}"
    email = f"rollback-{uuid.uuid4().hex}@example.com"

    PrincipalAuthorityRepository.create(
        PrincipalAuthority(target_principal, PrincipalStatus.ACTIVE, 0),
        collection=runtime.database["principal_authorities"],
    )
    monkeypatch.setattr(auth_registry_module.uuid, "uuid4", lambda: fixed_uuid)

    with pytest.raises(provisioner.DeveloperPersonaProvisioningError) as caught:
        _provision(
            runtime,
            provisioner.DeveloperLegalPersona.LEGAL_ATTORNEY,
            email=email,
        )
    assert caught.value.code is provisioner.DeveloperPersonaProvisioningCode.AUTHORITY_CONFLICT

    assert runtime.database["users"].count_documents({"email": email}) == 0
    assert runtime.database["tenant_memberships"].count_documents(
        {
            "principal_id": target_principal,
            "tenant_id": runtime.tenant_id,
        }
    ) == 0
    assert runtime.database["tenant_business_roles"].count_documents(
        {
            "principal_id": target_principal,
            "tenant_id": runtime.tenant_id,
        }
    ) == 0
    assert runtime.database["role_assignments"].count_documents(
        {
            "principal_id": target_principal,
            "tenant_id": runtime.tenant_id,
        }
    ) == 0
    assert runtime.database["principal_authorities"].count_documents(
        {"principal_id": target_principal}
    ) == 1


def test_real_mongo_production_environment_denies_before_mutation(
    runtime: Runtime,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Even an explicit feature flag cannot enable the provisioner in production."""
    monkeypatch.setenv("ENV", "production")
    before_users = runtime.database["users"].count_documents({})

    with pytest.raises(provisioner.DeveloperPersonaProvisioningError) as caught:
        _provision(
            runtime,
            provisioner.DeveloperLegalPersona.LEGAL_CLIENT,
            email=f"production-denied-{uuid.uuid4().hex}@example.com",
        )
    assert caught.value.code is provisioner.DeveloperPersonaProvisioningCode.ENVIRONMENT_DENIED
    assert runtime.database["users"].count_documents({}) == before_users


def test_real_mongo_cross_tenant_projection_denies_without_disclosure_or_write(
    runtime: Runtime,
) -> None:
    """A mismatched authenticated tenant cannot redirect persona provisioning."""
    foreign_identity = runtime.identity.model_copy(
        update={"tenant_id": f"FOREIGN-{uuid.uuid4().hex}"}
    )
    email = f"cross-tenant-denied-{uuid.uuid4().hex}@example.com"
    before_users = runtime.database["users"].count_documents({})

    with pytest.raises(provisioner.DeveloperPersonaProvisioningError) as caught:
        provisioner.provision_developer_legal_persona(
            owner_identity=foreign_identity,
            tenant_id=runtime.tenant_id,
            email=email,
            password=RAW_PASSWORD,
            first_name="Synthetic",
            last_name="Persona",
            persona=provisioner.DeveloperLegalPersona.LEGAL_CLIENT,
            password_blocklist_checker=AllowBlocklist(),
        )
    assert caught.value.code is provisioner.DeveloperPersonaProvisioningCode.OWNER_SCOPE_MISMATCH
    assert runtime.database["users"].count_documents({}) == before_users
    assert runtime.database["users"].count_documents({"email": email}) == 0


def test_real_mongo_durable_owner_role_drift_denies_before_target_write(
    runtime: Runtime,
) -> None:
    """Projected owner claims cannot replace exact durable tenant_owner authority."""
    runtime.database["tenant_business_roles"].update_one(
        {
            "principal_id": runtime.owner_id,
            "tenant_id": runtime.tenant_id,
        },
        {
            "$set": {
                "business_role": "tenant_admin",
                "revision": 1,
            }
        },
    )
    email = f"owner-drift-denied-{uuid.uuid4().hex}@example.com"
    before_users = runtime.database["users"].count_documents({})

    with pytest.raises(provisioner.DeveloperPersonaProvisioningError) as caught:
        _provision(
            runtime,
            provisioner.DeveloperLegalPersona.LEGAL_PARTNER,
            email=email,
        )
    assert caught.value.code is provisioner.DeveloperPersonaProvisioningCode.OWNER_BUSINESS_ROLE_INVALID
    assert runtime.database["users"].count_documents({}) == before_users
    assert runtime.database["users"].count_documents({"email": email}) == 0


def test_real_mongo_certificate_never_mutates_canonical_database(runtime: Runtime) -> None:
    """The certificate database is UUID isolated and never named canonical wilsy."""
    assert runtime.database.name != "wilsy"
    assert runtime.database.name.startswith("wilsy_d15g_persona_")


# ARTIFACT: tests/integration/test_developer_persona_provisioner_real_mongo.py
# VERSION: v1.0.0-D15G-DEV-LEGAL-PERSONA-REAL-MONGO-CERT
# AUTHORITY BOUNDARY: host-backed evidence for development-only legal persona admission
# TENANT POSTURE: UUID-isolated database and exact owner/tenant authority only
# FAIL-CLOSED POSTURE: environment, tenant, owner-role, authority-conflict, and replica-set failures deny
# FINANCIAL EXECUTION AUTHORITY: none; Kennel EOS remains exclusive
# END OF WILSY OS SOVEREIGN ARTIFACT
