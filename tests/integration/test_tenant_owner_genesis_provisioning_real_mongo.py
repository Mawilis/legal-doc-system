"""Disposable real-Mongo transaction certification for EOS owner genesis.

The lifecycle fake writes only a synthetic ownership event. This test certifies
transaction/session propagation and rollback mechanics, not production issuer
verification or legal ownership sufficiency.
"""
from __future__ import annotations

import os
from datetime import datetime, timezone
from types import SimpleNamespace
from uuid import uuid4
from typing import Any

import pytest
from pymongo import MongoClient

from tools.eos.auth.role_assignment_repository import RoleAssignmentRepository
from tools.eos.auth.tenant_business_role import TenantBusinessRoleAuthority, TenantBusinessRoleStatus
from tools.eos.auth.tenant_business_role_repository import (
    HISTORY_COLLECTION,
    MULTI_COLLECTION,
    TenantBusinessRoleRepository,
)
from tools.eos.auth.tenant_membership_repository import TenantMembershipRepository
from tools.eos.auth.tenant_owner_genesis_provisioning import TenantOwnerGenesisProvisioningCommand
from tools.eos.auth.tenant_ownership_verifier import (
    TenantOwnershipOperation,
    TenantOwnershipVerificationRequest,
    VerifiedTenantOwnershipEvidence,
)
from tools.eos.saas.tenancy.tenant_registry import TenantRegistry


def _request(tenant_id: str, principal_id: str) -> TenantOwnershipVerificationRequest:
    return TenantOwnershipVerificationRequest(
        tenant_id=tenant_id,
        legal_entity_reference=f"entity-{tenant_id}",
        principal_id=principal_id,
        operation=TenantOwnershipOperation.TENANT_GENESIS,
        evaluated_at=datetime.now(timezone.utc),
    )


def _evidence(request: TenantOwnershipVerificationRequest) -> VerifiedTenantOwnershipEvidence:
    # Synthetic opaque evidence is used only to reach the transaction boundary.
    value = object.__new__(VerifiedTenantOwnershipEvidence)
    object.__setattr__(value, "request", request)
    return value


class _MongoLifecycle:
    def __init__(self, database: Any) -> None:
        self.database = database

    def execute(self, **kwargs: Any) -> object:
        request = kwargs["request"]
        session = kwargs["session"]
        self.database["synthetic_ownership_events"].insert_one(
            {
                "tenant_id": request.tenant_id,
                "principal_id": request.principal_id,
                "command_id": kwargs["command_id"],
                "revision": 1,
            },
            session=session,
        )
        return SimpleNamespace(
            tenant_id=request.tenant_id,
            legal_entity_reference=request.legal_entity_reference,
            principal_id=request.principal_id,
            operation=request.operation,
            command_id=kwargs["command_id"],
            revision=1,
        )


def _build_command(database: Any) -> TenantOwnerGenesisProvisioningCommand:
    return TenantOwnerGenesisProvisioningCommand(
        lifecycle=_MongoLifecycle(database),  # type: ignore[arg-type]
        tenant_create=lambda payload, *, session: TenantRegistry.create(
            payload, session=session
        ),
    )


def test_owner_genesis_commits_all_records_and_rolls_back_every_participant(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    uri = os.environ.get("TEST_TENANT_OWNER_MONGO_URI", "").strip()
    if not uri:
        pytest.fail("TEST_TENANT_OWNER_MONGO_URI is required for real-Mongo certification")

    client = MongoClient(uri, serverSelectionTimeoutMS=10_000)
    database_name = f"owner_genesis_cert_{uuid4().hex}"
    database = client[database_name]
    try:
        client.admin.command("ping")
        hello = client.admin.command("hello")
        assert hello.get("setName"), "real Mongo replica set is required"
        assert hello.get("isWritablePrimary"), "Mongo primary is required"

        monkeypatch.setattr(
            "tools.eos.kernel.db.get_database", lambda: database
        )
        monkeypatch.setattr(
            "tools.eos.saas.tenancy.tenant_registry._resolve_collection",
            lambda collection=None: database["tenants"],
        )
        TenantMembershipRepository.ensure_indexes(database["tenant_memberships"])
        RoleAssignmentRepository.ensure_indexes(database["role_assignments"])
        TenantBusinessRoleRepository.ensure_multi_capacity_indexes(database)

        # Seed a distinct existing capacity and prove genesis adds owner without
        # replacing the Legal Partner record.
        owner_tenant = f"tenant-success-{uuid4().hex}"
        owner_principal = f"principal-success-{uuid4().hex}"
        with client.start_session() as session:
            with session.start_transaction():
                TenantBusinessRoleRepository.record_capacity_revision(
                    TenantBusinessRoleAuthority(
                        owner_principal, owner_tenant, "tenant_legal_partner",
                        TenantBusinessRoleStatus.ACTIVE, 0,
                        datetime.now(timezone.utc), None,
                    ),
                    expected_revision=None,
                    database=database,
                    session=session,
                )

        request = _request(owner_tenant, owner_principal)
        with client.start_session() as session:
            with session.start_transaction():
                result = _build_command(database).execute(
                    request=request,
                    evidence=_evidence(request),
                    actor_principal_id=owner_principal,
                    command_id=f"genesis-{uuid4().hex}",
                    tenant_payload={"tenant_id": owner_tenant, "name": "Synthetic Entity"},
                    database=database,
                    session=session,
                )
                assert result.tenant.tenant_id == owner_tenant

        assert database["tenants"].count_documents({"tenant_id": owner_tenant}) == 1
        assert database["synthetic_ownership_events"].count_documents({"tenant_id": owner_tenant}) == 1
        assert database["tenant_memberships"].count_documents({"tenant_id": owner_tenant, "principal_id": owner_principal}) == 1
        assert database["role_assignments"].count_documents({"tenant_id": owner_tenant, "principal_id": owner_principal, "role_id": "TENANT_OWNER"}) == 1
        capacities = TenantBusinessRoleRepository.resolve_all(owner_principal, owner_tenant)
        assert {item.business_role for item in capacities} == {"tenant_legal_partner", "tenant_owner"}
        assert database[HISTORY_COLLECTION].count_documents({"tenant_id": owner_tenant}) == 2

        # Force failure after both current capacity and immutable history writes.
        # The caller-owned transaction must roll back tenant, event, membership,
        # IAM role, capacity projection, and history together.
        rollback_tenant = f"tenant-rollback-{uuid4().hex}"
        rollback_principal = f"principal-rollback-{uuid4().hex}"
        rollback_request = _request(rollback_tenant, rollback_principal)
        original_record = TenantBusinessRoleRepository.record_capacity_revision

        def fail_after_capacity_write(*args: Any, **kwargs: Any) -> object:
            original_record(*args, **kwargs)
            raise RuntimeError("synthetic post-capacity failure")

        monkeypatch.setattr(
            TenantBusinessRoleRepository,
            "record_capacity_revision",
            staticmethod(fail_after_capacity_write),
        )
        with client.start_session() as session:
            with pytest.raises(RuntimeError, match="synthetic post-capacity failure"):
                with session.start_transaction():
                    _build_command(database).execute(
                        request=rollback_request,
                        evidence=_evidence(rollback_request),
                        actor_principal_id=rollback_principal,
                        command_id=f"rollback-{uuid4().hex}",
                        tenant_payload={"tenant_id": rollback_tenant, "name": "Rollback Entity"},
                        database=database,
                        session=session,
                    )

        assert database["tenants"].count_documents({"tenant_id": rollback_tenant}) == 0
        assert database["synthetic_ownership_events"].count_documents({"tenant_id": rollback_tenant}) == 0
        assert database["tenant_memberships"].count_documents({"tenant_id": rollback_tenant}) == 0
        assert database["role_assignments"].count_documents({"tenant_id": rollback_tenant}) == 0
        assert database[MULTI_COLLECTION].count_documents({"tenant_id": rollback_tenant}) == 0
        assert database[HISTORY_COLLECTION].count_documents({"tenant_id": rollback_tenant}) == 0
    finally:
        client.drop_database(database_name)
        client.close()
