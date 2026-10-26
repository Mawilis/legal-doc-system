"""WILSY OS physical practitioner-binding EOS lifespan certificate.

TITLE: P12C Practitioner Binding Canonical EOS Lifespan Certificate
VERSION: v0.5.0-P12C-R4N-P10D2-P4C3B-POSITIVE-PROVENANCE
AUTHORITY: WILSY OS Sovereign Legal Operations
EPITOME: Exercise real EOS startup and shutdown against an owned
    disposable MongoDB replica set with physical P12C indexes.
ABSOLUTE CANONICAL PATH:
    /Users/wilsonkhanyezi/legal-doc-system-p9-reassignment/tests/integration/test_legal_practitioner_binding_authenticated_eos_lifespan_real_mongo.py
COLLABORATION / OWNERSHIP: WILSY OS sovereign engineering
CERTIFICATION / UPDATE DATE: 2026-10-20
CHANGELOG:
    v0.5.0-P12C-R4N-P10D2-P4C3B-POSITIVE-PROVENANCE implements
    disposable replica startup, canonical EOS lifespan, index,
    anonymous-denial, shutdown and cleanup checks.
COMPLIANCE: WILSY OS Engineering Constitution
SECURITY / PRIVACY: Isolated synthetic environment only
TENANT BOUNDARY: No production tenant, identity or role authority
AUTHORITY BOUNDARY: No authentication or authorization overrides
TRANSACTION BOUNDARY: No practitioner binding mutation
FINANCIAL AUTHORITY BOUNDARY: Kennel EOS exclusively
CERTIFICATION LIMIT: The positive certificate uses synthetic but
    domain-valid persisted provenance, not upstream human conflict review;
    complete practitioner-facing production readiness remains unproven.
"""

from __future__ import annotations

import os
import socket
import subprocess
import time
import uuid
from pathlib import Path
from tempfile import TemporaryDirectory

import pytest
from fastapi.testclient import TestClient
from pymongo import MongoClient
from pymongo.errors import PyMongoError

from tools.eos.api import server
from tools.eos.kernel import db as kernel_db

VERSION = "v0.5.0-P12C-R4N-P10D2-P4C3B-POSITIVE-PROVENANCE"

MONGOD = Path("/opt/homebrew/bin/mongod")
PROTECTED_PORTS = frozenset({27017, 27027, 61391})

GRANT_PATH = "/api/legal-operations/practitioner-bindings"
REVOKE_PATH = GRANT_PATH + "/revocations"


@pytest.fixture()
def isolated_eos_mongo(monkeypatch):
    """Own a disposable loopback replica and a unique database."""
    assert MONGOD.is_file(), "DISPOSABLE_MONGOD_MISSING"
    assert kernel_db.get_client() is None, (
        "EXISTING_KERNEL_DATABASE_CONNECTION"
    )

    with socket.socket(
        socket.AF_INET, socket.SOCK_STREAM
    ) as probe:
        probe.bind(("127.0.0.1", 0))
        port = probe.getsockname()[1]

    assert port not in PROTECTED_PORTS
    replica = "wilsyP12CLife" + uuid.uuid4().hex[:12]
    database_name = "wilsy_p12c_life_" + uuid.uuid4().hex
    uri = (
        f"mongodb://127.0.0.1:{port}/{database_name}"
        f"?replicaSet={replica}"
    )

    monkeypatch.setenv("MONGODB_URI", uri)
    monkeypatch.setenv("WILSY_KENNEL_DB_TLS", "false")
    monkeypatch.setenv(
        "WILSY_KENNEL_DB_SERVER_SELECTION_MS", "2000"
    )
    monkeypatch.setenv(
        "WILSY_KENNEL_DB_CONNECT_TIMEOUT_MS", "2000"
    )
    monkeypatch.setenv(
        "WILSY_DUNNING_SCHEDULER_ENABLED", "false"
    )
    monkeypatch.setenv("WILSY_ENV", "test")
    monkeypatch.setenv(
        "WILSY_JWT_SECRET",
        "P12C-ISOLATED-TEST-ONLY-SIGNING-KEY"
    )

    process = None
    bootstrap = None
    observer = None

    with TemporaryDirectory(prefix="wilsy-p12c-life-") as temp:
        folder = Path(temp)
        data = folder / "data"
        data.mkdir()

        try:
            process = subprocess.Popen(
                [
                    str(MONGOD),
                    "--dbpath", str(data),
                    "--port", str(port),
                    "--bind_ip", "127.0.0.1",
                    "--replSet", replica,
                    "--nounixsocket",
                    "--logpath", str(folder / "mongod.log"),
                    "--quiet",
                ],
                cwd=folder,
                stdin=subprocess.DEVNULL,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )

            bootstrap = MongoClient(
                f"mongodb://127.0.0.1:{port}/"
                "?directConnection=true",
                serverSelectionTimeoutMS=1000,
                connectTimeoutMS=1000,
            )

            deadline = time.monotonic() + 30
            while True:
                assert process.poll() is None, (
                    "DISPOSABLE_MONGO_EXITED"
                )
                try:
                    bootstrap.admin.command("ping")
                    break
                except PyMongoError:
                    assert time.monotonic() < deadline, (
                        "DISPOSABLE_MONGO_STARTUP_TIMEOUT"
                    )
                    time.sleep(0.25)

            bootstrap.admin.command({
                "replSetInitiate": {
                    "_id": replica,
                    "members": [{
                        "_id": 0,
                        "host": f"127.0.0.1:{port}",
                    }],
                },
            })

            observer = MongoClient(
                uri,
                serverSelectionTimeoutMS=2000,
                connectTimeoutMS=2000,
                retryWrites=False,
            )

            deadline = time.monotonic() + 35
            while True:
                assert process.poll() is None, (
                    "DISPOSABLE_MONGO_EXITED"
                )
                try:
                    hello = observer.admin.command("hello")
                    if hello.get("isWritablePrimary") is True:
                        break
                except PyMongoError:
                    pass

                assert time.monotonic() < deadline, (
                    "DISPOSABLE_MONGO_ELECTION_TIMEOUT"
                )
                time.sleep(0.25)

            assert hello["setName"] == replica
            assert hello.get(
                "logicalSessionTimeoutMinutes"
            ) is not None

            yield observer, database_name, replica, port

        finally:
            # EOS owns its kernel client; teardown is fail-closed.
            kernel_db.disconnect_db()
            if observer is not None:
                observer.close()
            if bootstrap is not None:
                bootstrap.close()
            if process is not None and process.poll() is None:
                process.terminate()
                try:
                    process.wait(timeout=10)
                except subprocess.TimeoutExpired:
                    process.kill()
                    process.wait(timeout=10)


def test_real_eos_lifespan_and_anonymous_binding_denial(
    isolated_eos_mongo,
):
    """Real startup installs indexes; shutdown revokes readiness."""
    observer, name, replica, port = isolated_eos_mongo

    assert port not in PROTECTED_PORTS
    assert observer.admin.command("hello")["setName"] == replica
    assert kernel_db.get_client() is None

    app = server.WilsyAPIServer(
        reasoning_provider_binding=None
    ).get_app()

    assert app.state.p12c_binding_indexes_ready is False
    assert not app.dependency_overrides

    with TestClient(
        app, raise_server_exceptions=True
    ) as client:
        assert app.state.p12c_binding_indexes_ready is True
        assert kernel_db.get_client() is not None
        connected_database = kernel_db.get_database()
        assert connected_database is not None
        assert connected_database.name == name

        database = observer[name]

        for collection_name in (
            "legal_practitioner_matter_access_evidence",
            "legal_practitioner_matter_bindings",
        ):
            indexes = database[
                collection_name
            ].index_information()
            assert len(indexes) > 1, (
                "REQUIRED_INDEXES_MISSING",
                collection_name,
            )

        for path, body in (
            (
                GRANT_PATH,
                {
                    "case_matter_id": "case-synthetic",
                    "practitioner_principal_id": "principal-synthetic",
                    "binding_id": "binding-synthetic",
                    "access_evidence_id": "evidence-synthetic",
                    "expected_access_evidence_fingerprint":
                        "a" * 128,
                },
            ),
            (
                REVOKE_PATH,
                {
                    "binding_id": "binding-synthetic",
                    "evidence_reference": "revoke-synthetic",
                },
            ),
        ):
            response = client.post(
                path,
                json=body,
                headers={"X-Tenant-ID": "synthetic-tenant"},
            )
            assert response.status_code in (401, 403), (
                path,
                response.status_code,
                response.text,
            )

        assert database[
            "legal_practitioner_matter_bindings"
        ].count_documents({}) == 0

    assert app.state.p12c_binding_indexes_ready is False
    assert kernel_db.get_client() is None
    assert kernel_db.get_database() is None
    assert not app.dependency_overrides



def test_signed_access_token_and_durable_revision(isolated_eos_mongo):
    """Use unmodified JWT authentication and durable credential authority."""
    from tools.eos.auth.jwt_provider import (
        TokenPurpose,
        create_access_token,
        verify_access_token,
    )
    from tools.eos.auth.principal_authority import PrincipalAuthority
    from tools.eos.auth.principal_authority_repository import (
        PrincipalAuthorityRepository,
    )
    from tools.eos.auth.principal_status import PrincipalStatus
    from tools.eos.saas.auth.auth_registry import AuthRegistry
    from tools.eos.saas.tenancy.tenant_registry import TenantRegistry

    observer, database_name, replica, port = isolated_eos_mongo
    assert port not in PROTECTED_PORTS
    assert observer.admin.command("hello")["setName"] == replica

    tenant_id = "tenant-p12c-" + uuid.uuid4().hex
    principal_id = "principal-p12c-" + uuid.uuid4().hex
    revision = 7

    app = server.WilsyAPIServer(
        reasoning_provider_binding=None
    ).get_app()
    assert not app.dependency_overrides

    with TestClient(app, raise_server_exceptions=True) as client:
        assert app.state.p12c_binding_indexes_ready is True
        database = observer[database_name]

        created = TenantRegistry.create({
            "tenant_id": tenant_id,
            "name": "P12C Synthetic Legal Firm",
            "industry": "legal",
        })
        assert created.get("success") is True, created

        tenant = TenantRegistry.resolve_canonical_tenant(tenant_id)
        assert tenant.tenant_id == tenant_id
        tenant_status = getattr(tenant.status, "value", tenant.status)
        assert tenant_status == "ACTIVE"

        principal_collection = database["principal_authorities"]
        PrincipalAuthorityRepository.ensure_indexes(principal_collection)
        PrincipalAuthorityRepository.create(
            PrincipalAuthority(
                principal_id, PrincipalStatus.ACTIVE, 0
            ),
            principal_collection,
        )

        users = database["users"]
        users.insert_one({
            "user_id": principal_id,
            "email": "p12c-isolated@example.com",
            "firstName": "Synthetic",
            "lastName": "Practitioner",
            "role": "LEGAL_PARTNER",
            "permissions": [],
            "tenantId": tenant_id,
            "passwordHash": "synthetic-noncredential-value",
            "credential_revision": revision,
            "mfaRegistered": False,
            "hasSignedCovenant": False,
        })

        registry = AuthRegistry()
        assert registry.get_credential_revision(
            tenant_id, principal_id
        ) == revision

        token = registry.generate_access_jwt(
            principal_id, tenant_id, "LEGAL_PARTNER", []
        )
        claims = verify_access_token(token)
        assert claims is not None
        assert claims["identity_id"] == principal_id
        assert claims["tenant_id"] == tenant_id
        assert claims["token_purpose"] == "ACCESS"
        assert claims["credential_revision"] == revision

        headers = {
            "Authorization": "Bearer " + token,
            "X-Tenant-ID": tenant_id,
        }
        verified = client.get(
            "/api/auth/verify-token", headers=headers
        )
        assert verified.status_code == 200, (
            verified.status_code, verified.text
        )
        assert verified.json()["success"] is True
        assert verified.json()["user"]["id"] == principal_id

        # Valid authentication cannot invent partner membership or grants.
        denied = client.post(
            GRANT_PATH,
            headers=headers,
            json={
                "case_matter_id": "synthetic-matter",
                "practitioner_principal_id": principal_id,
                "binding_id": "synthetic-binding",
                "access_evidence_id": "synthetic-evidence",
                "expected_access_evidence_fingerprint": "a" * 128,
            },
        )
        assert denied.status_code == 403, (
            denied.status_code, denied.text
        )
        assert database[
            "legal_practitioner_matter_bindings"
        ].count_documents({}) == 0

        preauth = create_access_token(
            {
                "identity_id": principal_id,
                "tenant_id": tenant_id,
            },
            token_purpose=TokenPurpose.PRE_AUTH,
            credential_revision=revision,
        )
        preauth_response = client.get(
            "/api/auth/verify-token",
            headers={"Authorization": "Bearer " + preauth},
        )
        assert preauth_response.status_code in (401, 403)

        malformed = client.get(
            "/api/auth/verify-token",
            headers={"Authorization": "Bearer invalid.token"},
        )
        assert malformed.status_code in (401, 403)

        changed = users.update_one(
            {
                "user_id": principal_id,
                "tenantId": tenant_id,
                "credential_revision": revision,
            },
            {"$set": {"credential_revision": revision + 1}},
        )
        assert changed.matched_count == 1
        assert changed.modified_count == 1
        assert registry.get_credential_revision(
            tenant_id, principal_id
        ) == revision + 1

        stale = client.get(
            "/api/auth/verify-token", headers=headers
        )
        assert stale.status_code in (401, 403), (
            stale.status_code, stale.text
        )
        assert not app.dependency_overrides

    assert app.state.p12c_binding_indexes_ready is False
    assert kernel_db.get_client() is None
    assert kernel_db.get_database() is None



def test_real_partner_reaches_missing_evidence_gate(isolated_eos_mongo):
    """Real signed partner JWT and physical IAM reach the evidence gate."""
    from datetime import datetime, timezone

    from tools.eos.auth.principal_authority import PrincipalAuthority
    from tools.eos.auth.principal_authority_repository import (
        PrincipalAuthorityRepository,
    )
    from tools.eos.auth.principal_status import PrincipalStatus
    from tools.eos.auth.tenant_membership import (
        TenantMembershipAuthority,
        TenantMembershipStatus,
    )
    from tools.eos.auth.tenant_membership_repository import (
        TenantMembershipRepository,
    )
    from tools.eos.auth.tenant_business_role import (
        TenantBusinessRoleAuthority,
        TenantBusinessRoleStatus,
    )
    from tools.eos.auth.tenant_business_role_repository import (
        TenantBusinessRoleRepository,
    )
    from tools.eos.auth.role_assignment import (
        RoleAssignmentAuthority,
        RoleAssignmentStatus,
    )
    from tools.eos.auth.role_assignment_repository import (
        RoleAssignmentRepository,
    )
    from tools.eos.saas.auth.auth_registry import AuthRegistry
    from tools.eos.saas.tenancy.tenant_registry import TenantRegistry

    observer, database_name, replica, port = isolated_eos_mongo

    assert port not in PROTECTED_PORTS
    assert observer.admin.command("hello")["setName"] == replica

    tenant_id = "tenant-p12c-partner-" + uuid.uuid4().hex
    principal_id = "principal-p12c-partner-" + uuid.uuid4().hex

    app = server.WilsyAPIServer(
        reasoning_provider_binding=None
    ).get_app()
    assert not app.dependency_overrides

    with TestClient(app, raise_server_exceptions=True) as client:
        assert app.state.p12c_binding_indexes_ready is True
        database = observer[database_name]

        created = TenantRegistry.create({
            "tenant_id": tenant_id,
            "name": "Synthetic P12C Partner Firm",
            "industry": "legal",
        })
        assert created.get("success") is True, created
        assert TenantRegistry.resolve_canonical_tenant(
            tenant_id
        ).tenant_id == tenant_id

        principals = database["principal_authorities"]
        memberships = database["tenant_memberships"]
        businesses = database["tenant_business_roles"]
        assignments = database["role_assignments"]

        PrincipalAuthorityRepository.ensure_indexes(principals)
        TenantMembershipRepository.ensure_indexes(memberships)
        TenantBusinessRoleRepository.ensure_indexes(businesses)
        RoleAssignmentRepository.ensure_indexes(assignments)

        PrincipalAuthorityRepository.create(
            PrincipalAuthority(
                principal_id, PrincipalStatus.ACTIVE, 0
            ),
            principals,
        )

        TenantMembershipRepository.insert(
            TenantMembershipAuthority(
                principal_id,
                tenant_id,
                TenantMembershipStatus.ACTIVE,
                0,
            ),
            memberships,
        )

        TenantBusinessRoleRepository.insert(
            TenantBusinessRoleAuthority(
                principal_id=principal_id,
                tenant_id=tenant_id,
                business_role="tenant_legal_partner",
                status=TenantBusinessRoleStatus.ACTIVE,
                revision=0,
                effective_at=datetime.now(timezone.utc),
                revoked_at=None,
            ),
            businesses,
        )

        RoleAssignmentRepository.insert(
            RoleAssignmentAuthority(
                principal_id,
                tenant_id,
                "LEGAL_PARTNER",
                RoleAssignmentStatus.ACTIVE,
                0,
            ),
            assignments,
        )

        database["users"].insert_one({
            "user_id": principal_id,
            "email": "p12c-partner@example.com",
            "firstName": "Synthetic",
            "lastName": "Partner",
            "role": "LEGAL_PARTNER",
            "permissions": [],
            "tenantId": tenant_id,
            "passwordHash": "synthetic-noncredential-value",
            "credential_revision": 3,
            "mfaRegistered": False,
            "hasSignedCovenant": False,
        })

        issuer = AuthRegistry()
        assert issuer.get_credential_revision(
            tenant_id, principal_id
        ) == 3

        token = issuer.generate_access_jwt(
            principal_id, tenant_id, "LEGAL_PARTNER", []
        )
        headers = {
            "Authorization": "Bearer " + token,
            "X-Tenant-ID": tenant_id,
        }

        authenticated = client.get(
            "/api/auth/verify-token", headers=headers
        )
        assert authenticated.status_code == 200, (
            authenticated.status_code, authenticated.text
        )
        assert authenticated.json()["user"]["id"] == principal_id

        # Valid partner IAM must reach the matter evidence boundary.
        # No legal access or disposition evidence is invented.
        response = client.post(
            GRANT_PATH,
            headers=headers,
            json={
                "case_matter_id": "matter-p12c-unseeded",
                "practitioner_principal_id": "lawyer-p12c-unseeded",
                "binding_id": "binding-p12c-unseeded",
                "access_evidence_id": "evidence-p12c-unseeded",
                "expected_access_evidence_fingerprint": "a" * 128,
            },
        )

        assert response.status_code == 403, (
            response.status_code, response.text
        )
        assert response.json().get("detail") == (
            "P9_BINDING_EVIDENCE_DENIED"
        ), response.text

        assert database[
            "legal_practitioner_matter_bindings"
        ].count_documents({}) == 0
        assert not app.dependency_overrides

    assert app.state.p12c_binding_indexes_ready is False
    assert kernel_db.get_client() is None
    assert kernel_db.get_database() is None


def test_real_partner_grant_revoke_with_persisted_provenance(
    isolated_eos_mongo, monkeypatch,
):
    """Commit grant and revoke through genuine EOS authority and provenance."""
    from datetime import datetime, timezone

    from tools.eos.auth.principal_authority import PrincipalAuthority
    from tools.eos.auth.principal_authority_repository import (
        PrincipalAuthorityRepository,
    )
    from tools.eos.auth.principal_status import PrincipalStatus
    from tools.eos.auth.tenant_membership import (
        TenantMembershipAuthority,
        TenantMembershipStatus,
    )
    from tools.eos.auth.tenant_membership_repository import (
        TenantMembershipRepository,
    )
    from tools.eos.auth.tenant_business_role import (
        TenantBusinessRoleAuthority,
        TenantBusinessRoleStatus,
    )
    from tools.eos.auth.tenant_business_role_repository import (
        TenantBusinessRoleRepository,
    )
    from tools.eos.auth.role_assignment import (
        RoleAssignmentAuthority,
        RoleAssignmentStatus,
    )
    from tools.eos.auth.role_assignment_repository import (
        RoleAssignmentRepository,
    )
    from tools.eos.saas.auth.auth_registry import AuthRegistry
    from tools.eos.saas.tenancy.tenant_registry import TenantRegistry


    from datetime import timedelta

    from tools.eos.legal_operations.domain.legal_operations_lifecycle import (
        CaseMatter,
    )
    from tools.eos.legal_operations.registry.legal_operations_lifecycle_registry import (
        LegalOperationsLifecycleRegistry,
    )
    from tools.eos.legal_operations.domain.legal_client_matter_conflict_disposition import (
        LegalClientMatterConflictDisposition,
    )
    from tools.eos.legal_operations.registry import (
        legal_client_matter_conflict_disposition_registry as conflict_registry,
        legal_practitioner_matter_access_registry as access_registry,
        legal_practitioner_matter_binding_registry as binding_registry,
    )
    from tools.eos.legal_operations.domain.legal_practitioner_matter_access import (
        LegalPractitionerMatterAccessDecision,
        LegalPractitionerMatterAccessEvidence,
    )

    observer, database_name, replica, port = isolated_eos_mongo

    assert port not in PROTECTED_PORTS
    assert observer.admin.command("hello")["setName"] == replica

    tenant_id = "tenant-p12c-partner-" + uuid.uuid4().hex
    principal_id = "principal-p12c-partner-" + uuid.uuid4().hex

    app = server.WilsyAPIServer(
        reasoning_provider_binding=None
    ).get_app()
    assert not app.dependency_overrides

    with TestClient(app, raise_server_exceptions=True) as client:
        assert app.state.p12c_binding_indexes_ready is True
        database = observer[database_name]

        created = TenantRegistry.create({
            "tenant_id": tenant_id,
            "name": "Synthetic P12C Partner Firm",
            "industry": "legal",
        })
        assert created.get("success") is True, created
        assert TenantRegistry.resolve_canonical_tenant(
            tenant_id
        ).tenant_id == tenant_id

        principals = database["principal_authorities"]
        memberships = database["tenant_memberships"]
        businesses = database["tenant_business_roles"]
        assignments = database["role_assignments"]

        PrincipalAuthorityRepository.ensure_indexes(principals)
        TenantMembershipRepository.ensure_indexes(memberships)
        TenantBusinessRoleRepository.ensure_indexes(businesses)
        RoleAssignmentRepository.ensure_indexes(assignments)

        PrincipalAuthorityRepository.create(
            PrincipalAuthority(
                principal_id, PrincipalStatus.ACTIVE, 0
            ),
            principals,
        )

        TenantMembershipRepository.insert(
            TenantMembershipAuthority(
                principal_id,
                tenant_id,
                TenantMembershipStatus.ACTIVE,
                0,
            ),
            memberships,
        )

        TenantBusinessRoleRepository.insert(
            TenantBusinessRoleAuthority(
                principal_id=principal_id,
                tenant_id=tenant_id,
                business_role="tenant_legal_partner",
                status=TenantBusinessRoleStatus.ACTIVE,
                revision=0,
                effective_at=datetime.now(timezone.utc),
                revoked_at=None,
            ),
            businesses,
        )

        RoleAssignmentRepository.insert(
            RoleAssignmentAuthority(
                principal_id,
                tenant_id,
                "LEGAL_PARTNER",
                RoleAssignmentStatus.ACTIVE,
                0,
            ),
            assignments,
        )


        # The target practitioner receives real ACTIVE tenant IAM.
        practitioner_id = "lawyer-p12c-" + uuid.uuid4().hex

        PrincipalAuthorityRepository.create(
            PrincipalAuthority(
                practitioner_id, PrincipalStatus.ACTIVE, 0
            ),
            principals,
        )
        TenantMembershipRepository.insert(
            TenantMembershipAuthority(
                practitioner_id,
                tenant_id,
                TenantMembershipStatus.ACTIVE,
                0,
            ),
            memberships,
        )
        TenantBusinessRoleRepository.insert(
            TenantBusinessRoleAuthority(
                principal_id=practitioner_id,
                tenant_id=tenant_id,
                business_role="tenant_legal_attorney",
                status=TenantBusinessRoleStatus.ACTIVE,
                revision=0,
                effective_at=datetime.now(timezone.utc),
                revoked_at=None,
            ),
            businesses,
        )
        RoleAssignmentRepository.insert(
            RoleAssignmentAuthority(
                practitioner_id,
                tenant_id,
                "LEGAL_ATTORNEY",
                RoleAssignmentStatus.ACTIVE,
                0,
            ),
            assignments,
        )

        database["users"].insert_one({
            "user_id": principal_id,
            "email": "p12c-partner@example.com",
            "firstName": "Synthetic",
            "lastName": "Partner",
            "role": "LEGAL_PARTNER",
            "permissions": [],
            "tenantId": tenant_id,
            "passwordHash": "synthetic-noncredential-value",
            "credential_revision": 3,
            "mfaRegistered": False,
            "hasSignedCovenant": False,
        })

        issuer = AuthRegistry()
        assert issuer.get_credential_revision(
            tenant_id, principal_id
        ) == 3

        token = issuer.generate_access_jwt(
            principal_id, tenant_id, "LEGAL_PARTNER", []
        )
        headers = {
            "Authorization": "Bearer " + token,
            "X-Tenant-ID": tenant_id,
        }

        authenticated = client.get(
            "/api/auth/verify-token", headers=headers
        )
        assert authenticated.status_code == 200, (
            authenticated.status_code, authenticated.text
        )
        assert authenticated.json()["user"]["id"] == principal_id


        # Seed domain-valid synthetic source evidence through real registries.
        # No HTTP, authentication, IAM, or provenance reader is overridden.
        now = datetime.now(timezone.utc)
        case_matter_id = "matter-p12c-" + uuid.uuid4().hex
        binding_id = "binding-p12c-" + uuid.uuid4().hex
        evidence_id = "access-p12c-" + uuid.uuid4().hex
        client_party_id = "party-p12c-" + uuid.uuid4().hex
        subject_fingerprint = "b" * 128

        matter = CaseMatter(
            tenant_id=tenant_id,
            case_matter_id=case_matter_id,
            matter_reference="CASE-P12C-POSITIVE",
            opened_at=now - timedelta(days=3),
            evidence_reference="matter-open-p12c-fixture",
        )

        lifecycle = database["legal_operations_lifecycle"]
        # Use the registry's actual canonical collection identifier.
        from tools.eos.legal_operations.registry import (
            legal_operations_lifecycle_registry as lifecycle_module,
        )
        lifecycle = database[lifecycle_module.COLLECTION]
        LegalOperationsLifecycleRegistry.ensure_indexes(lifecycle)

        dispositions = database[conflict_registry.COLLECTION]
        conflict_registry.ensure_indexes(dispositions)

        access = database[
            "legal_practitioner_matter_access_evidence"
        ]
        access_registry.ensure_indexes(access)

        disposition = LegalClientMatterConflictDisposition(
            disposition_id="disposition-" + uuid.uuid4().hex,
            tenant_id=tenant_id,
            case_matter_id=case_matter_id,
            matter_fingerprint=matter.fingerprint,
            screening_id="screening-p12c-fixture",
            screening_fingerprint="c" * 128,
            conflict_review_id="review-p12c-fixture",
            conflict_review_fingerprint="d" * 128,
            review_outcome="NO_CONFLICT_IDENTIFIED",
            client_party_id=client_party_id,
            subject_identity_fingerprint=subject_fingerprint,
            disposition="ENGAGEMENT_PERMITTED",
            decision_actor_principal_id=principal_id,
            authorization_evidence_reference="iam:p12c:fixture",
            authorization_evidence_fingerprint="e" * 128,
            supporting_evidence_reference="review:p12c:fixture",
            supporting_evidence_fingerprint="f" * 128,
            occurred_at=now - timedelta(days=2),
            effective_from=now - timedelta(days=2),
            idempotency_key="p12c-" + uuid.uuid4().hex,
        )

        evidence = _p47_create_evidence(
            access_evidence_id=evidence_id,
            tenant_id=tenant_id,
            case_matter_id=case_matter_id,
            practitioner_principal_id=practitioner_id,
            revision=1,
            decision=LegalPractitionerMatterAccessDecision.ALLOW,
            effective_from=now - timedelta(days=1),
            effective_until=None,
            issued_by_principal_id=principal_id,
            source_evidence_fingerprint=disposition.fingerprint,
            supersedes_fingerprint=None,
        )

        with observer.start_session() as session:
            with session.start_transaction():
                assert LegalOperationsLifecycleRegistry.create(
                    matter, lifecycle, session=session
                ) == matter
                assert conflict_registry.persist_disposition(
                    disposition, dispositions, session=session
                ) == disposition
                assert access_registry.append_evidence(
                    evidence=evidence,
                    collection=access,
                    session=session,
                ) == evidence

        assert lifecycle.count_documents({
            "tenant_id": tenant_id,
            "entity_type": "CaseMatter",
        }) == 1
        assert dispositions.count_documents({
            "tenant_id": tenant_id,
        }) == 1
        assert access.count_documents({
            "tenant_id": tenant_id,
        }) == 1

        bindings = database[binding_registry.COLLECTION_NAME]
        assert bindings.count_documents({}) == 0

        granted = client.post(
            GRANT_PATH,
            headers=headers,
            json={
                "case_matter_id": case_matter_id,
                "practitioner_principal_id": practitioner_id,
                "binding_id": binding_id,
                "access_evidence_id": evidence_id,
                "expected_access_evidence_fingerprint":
                    evidence.fingerprint,
            },
        )
        assert granted.status_code == 201, (
            "GRANT_FAILED",
            granted.status_code,
            granted.text,
        )
        assert granted.json()["status"] == "ACTIVE"
        assert bindings.count_documents({
            "tenant_id": tenant_id
        }) == 1

        # Prove the HTTP-owned transaction aborts a real revocation write.
        # The injected failure happens only after the canonical service has
        # appended the REVOKED snapshot inside the route's live transaction.
        from tools.eos.api import legal_practitioner_matter_binding_router

        canonical_revoke = legal_practitioner_matter_binding_router.revoke_binding

        def fail_after_revocation_write(**kwargs):
            canonical_revoke(**kwargs)
            raise RuntimeError("P9_CERTIFICATE_FAILURE_AFTER_REVOCATION_WRITE")

        monkeypatch.setattr(
            legal_practitioner_matter_binding_router,
            "revoke_binding",
            fail_after_revocation_write,
        )
        failed_revoke = client.post(
            REVOKE_PATH,
            headers=headers,
            json={
                "binding_id": binding_id,
                "evidence_reference": "p12c-revocation-rollback-fixture",
            },
        )
        assert failed_revoke.status_code == 503, (
            failed_revoke.status_code, failed_revoke.text,
        )
        with observer.start_session() as session:
            with session.start_transaction():
                after_abort = binding_registry.read_binding_history(
                    tenant_id=tenant_id,
                    binding_id=binding_id,
                    collection=bindings,
                    session=session,
                )
        assert len(after_abort) == 1
        assert [item.status.value for item in after_abort] == ["ACTIVE"]
        assert bindings.count_documents({"tenant_id": tenant_id}) == 1

        monkeypatch.setattr(
            legal_practitioner_matter_binding_router,
            "revoke_binding",
            canonical_revoke,
        )
        revoked = client.post(
            REVOKE_PATH,
            headers=headers,
            json={
                "binding_id": binding_id,
                "evidence_reference": "p12c-revocation-fixture",
            },
        )
        assert revoked.status_code == 201, (
            "REVOKE_FAILED",
            revoked.status_code,
            revoked.text,
        )
        assert revoked.json()["status"] == "REVOKED"

        with observer.start_session() as session:
            with session.start_transaction():
                history = binding_registry.read_binding_history(
                    tenant_id=tenant_id,
                    binding_id=binding_id,
                    collection=bindings,
                    session=session,
                )
        assert len(history) == 2
        assert [item.status.value for item in history] == [
            "ACTIVE", "REVOKED"
        ]
        assert history[0].fingerprint != history[1].fingerprint
        assert bindings.count_documents({
            "tenant_id": tenant_id
        }) == 2

        assert not app.dependency_overrides

    assert app.state.p12c_binding_indexes_ready is False
    assert kernel_db.get_client() is None
    assert kernel_db.get_database() is None

# ARTIFACT: test_legal_practitioner_binding_authenticated_eos_lifespan_real_mongo.py
# VERSION: v0.5.0-P12C-R4N-P10D2-P4C3B-POSITIVE-PROVENANCE
# AUTHORITY BOUNDARY: physical lifecycle and anonymous denial only
# TENANT POSTURE: synthetic isolated database
# FAIL-CLOSED POSTURE: unready and anonymous commands cannot succeed
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively
# END OF WILSY OS SOVEREIGN ARTIFACT


def test_preexisting_domain_valid_binding_history_accepts_indexes(
    isolated_eos_mongo,
):
    """Indexes install over pre-existing valid ACTIVE/REVOKED history."""
    from datetime import datetime, timedelta, timezone
    import runpy

    from tools.eos.legal_operations.registry import (
        legal_practitioner_matter_binding_registry as registry,
    )

    observer, database_name, _, _ = isolated_eos_mongo
    fixture = runpy.run_path(
        str(Path(__file__).resolve().parents[1] / "unit"
            / "test_legal_practitioner_matter_binding.py")
    )
    make = fixture["make"]
    collection = observer[database_name]["p9_valid_preexisting_bindings"]

    active = make(binding_id="preexisting-binding")
    revoked = active.revoke(
        revoked_by_principal_id="synthetic-partner",
        revoked_at=datetime.now(timezone.utc) + timedelta(days=1),
        evidence_reference="synthetic-revocation-evidence",
    )
    independent = make(
        binding_id="preexisting-independent-binding",
        practitioner_principal_id="synthetic-other-practitioner",
    )
    collection.insert_many([
        active.to_dict(), revoked.to_dict(), independent.to_dict()
    ])

    registry.ensure_indexes(collection)
    indexes = {
        item["name"]: item for item in collection.list_indexes()
        if item["name"] != "_id_"
    }
    assert set(indexes) == {
        registry.SNAPSHOT_INDEX,
        registry.FINGERPRINT_INDEX,
        registry.SCOPE_INDEX,
    }
    assert all(item.get("unique") is True for item in indexes.values())
    assert collection.count_documents({}) == 3


def test_preexisting_duplicate_active_scope_fails_index_installation(
    isolated_eos_mongo,
):
    """Conflicting legacy rows must stop startup index certification."""
    from pymongo.errors import DuplicateKeyError
    import runpy

    from tools.eos.legal_operations.registry import (
        legal_practitioner_matter_binding_registry as registry,
    )

    observer, database_name, _, _ = isolated_eos_mongo
    fixture = runpy.run_path(
        str(Path(__file__).resolve().parents[1] / "unit"
            / "test_legal_practitioner_matter_binding.py")
    )
    make = fixture["make"]
    collection = observer[database_name]["p9_conflicting_preexisting_bindings"]
    first = make(binding_id="conflicting-binding-one")
    second = make(binding_id="conflicting-binding-two")
    assert (
        first.tenant_id,
        first.case_matter_id,
        first.practitioner_principal_id,
    ) == (
        second.tenant_id,
        second.case_matter_id,
        second.practitioner_principal_id,
    )
    assert first.fingerprint != second.fingerprint
    collection.insert_many([first.to_dict(), second.to_dict()])

    with pytest.raises(DuplicateKeyError):
        registry.ensure_indexes(collection)

    installed = {
        item["name"] for item in collection.list_indexes()
        if item["name"] != "_id_"
    }
    assert registry.SCOPE_INDEX not in installed
    assert collection.count_documents({}) == 2


def test_real_registry_replay_divergence_and_cross_tenant_absence(
    isolated_eos_mongo,
):
    """Real Mongo verifies idempotent exact replay and tenant-scoped reads."""
    from datetime import datetime, timedelta, timezone
    import runpy

    from tools.eos.legal_operations.registry import (
        legal_practitioner_matter_binding_registry as registry,
    )

    observer, database_name, _, _ = isolated_eos_mongo
    fixture = runpy.run_path(
        str(Path(__file__).resolve().parents[1] / "unit"
            / "test_legal_practitioner_matter_binding.py")
    )
    make = fixture["make"]
    collection = observer[database_name][
        "p9_replay_isolation_bindings"
    ]
    registry.ensure_indexes(collection)
    active = make(binding_id="replay-binding")
    with observer.start_session() as session:
        with session.start_transaction():
            assert registry.append_binding(
                binding=active, collection=collection, session=session
            ) == active
    with observer.start_session() as session:
        with session.start_transaction():
            assert registry.append_binding(
                binding=active, collection=collection, session=session
            ) == active
            assert registry.read_binding_history(
                tenant_id=active.tenant_id,
                binding_id=active.binding_id,
                collection=collection,
                session=session,
            ) == (active,)
    assert collection.count_documents({}) == 1

    divergent = make(
        binding_id="replay-divergent-binding",
        practitioner_principal_id=active.practitioner_principal_id,
    )
    with observer.start_session() as session:
        with session.start_transaction():
            with pytest.raises(registry.BindingConflict):
                registry.append_binding(
                    binding=divergent,
                    collection=collection,
                    session=session,
                )
    assert collection.count_documents({}) == 1

    with observer.start_session() as session:
        with session.start_transaction():
            assert registry.read_binding_history(
                tenant_id="different-tenant",
                binding_id=active.binding_id,
                collection=collection,
                session=session,
            ) == ()
            assert registry.resolve_current_binding(
                tenant_id="different-tenant",
                binding_id=active.binding_id,
                collection=collection,
                session=session,
            ) is None
    assert collection.count_documents({}) == 1


from tools.eos.legal_operations.service.legal_practitioner_matter_access_codec import (
    create_practitioner_matter_access as _p47_create_evidence,
)
