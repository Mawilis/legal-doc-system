"""TITLE: Tenant Legal Operating Model Command Service Real-Mongo Certificate.
VERSION: v1.0.0-CX26-R3-CURRENT-OPERATING-MODEL-COMMAND-REAL-MONGO-CERT
AUTHORITY: Physical service/IAM/registry composition certification.
EPITOME: Proves the command service against sanctioned Mongo persistence,
real governed IAM repositories, active transactions, replay, revision
currentness, tenant isolation, rollback, denial, and zero-write failures.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tests/integration/test_tenant_legal_operating_model_service_real_mongo.py
COLLABORATION / OWNERSHIP: CX26-R3 service certificate; IAM and CX26-R2
registry retain their own authority boundaries.
CERTIFICATION / UPDATE DATE: 2026-10-15
CHANGELOG: v1.0.0 establishes real-Mongo service composition certification.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2; ISO 27001.
SECURITY / PRIVACY POSTURE: UUID-isolated synthetic database only.
TENANT BOUNDARY: Exact generated tenant/principal predicates throughout.
AUTHORITY BOUNDARY: Configuration admission only; no role provisioning,
workflow authority, entitlement, professional authority, legal execution,
transport, HTTP, billing, payment, or settlement authority.
FINANCIAL AUTHORITY BOUNDARY: None; Kennel EOS exclusively executes finance.
TRANSACTION BOUNDARY: Tests own every transaction and explicitly commit/abort.
FAIL-CLOSED DECLARATION: Denial, missing transaction, stale revision,
divergent replay, abort, or persistence failure must leave durable truth safe.
"""
from __future__ import annotations

from copy import deepcopy
from datetime import datetime, timedelta, timezone
import os
from typing import Any, Iterator
import uuid

import pytest
from pymongo import MongoClient
from pymongo.read_concern import ReadConcern
from pymongo.write_concern import WriteConcern

from tools.eos.auth.principal_authority import PrincipalAuthority
from tools.eos.auth.principal_authority_repository import (
    PrincipalAuthorityRepository,
)
from tools.eos.auth.principal_status import PrincipalStatus
from tools.eos.auth.role_assignment import (
    RoleAssignmentAuthority,
    RoleAssignmentStatus,
)
from tools.eos.auth.role_assignment_repository import (
    RoleAssignmentRepository,
)
from tools.eos.auth.tenant_membership import (
    TenantMembershipAuthority,
    TenantMembershipStatus,
)
from tools.eos.auth.tenant_membership_repository import (
    TenantMembershipRepository,
)
from tools.eos.legal_operations.registry import (
    tenant_legal_operating_model_registry as registry_module,
)
import tools.eos.legal_operations.service.tenant_legal_operating_model_service as service


MONGO_URI = os.getenv(
    "TEST_VENDOR_MONGO_URI",
    "mongodb://127.0.0.1:27027/?replicaSet=wilsyVendorCertRS",
)
EXPECTED_REPLICA_SET = "wilsyVendorCertRS"

BASE = datetime(
    2026,
    10,
    15,
    13,
    0,
    0,
    654321,
    tzinfo=timezone.utc,
)


class PrincipalReader:
    def __init__(self, collection: Any) -> None:
        self.collection = collection

    def resolve(
        self,
        principal_id: str,
        *,
        session: Any = None,
    ) -> object:
        return PrincipalAuthorityRepository.resolve(
            principal_id,
            collection=self.collection,
            session=session,
        )


class MembershipReader:
    def __init__(self, collection: Any) -> None:
        self.collection = collection

    def resolve(
        self,
        principal_id: str,
        tenant_id: str,
        *,
        session: Any = None,
    ) -> object:
        return TenantMembershipRepository.resolve(
            principal_id,
            tenant_id,
            collection=self.collection,
            session=session,
        )


class RoleReader:
    def __init__(self, collection: Any) -> None:
        self.collection = collection

    def resolve(
        self,
        principal_id: str,
        tenant_id: str,
        role_id: str,
        *,
        session: Any = None,
    ) -> object:
        return RoleAssignmentRepository.resolve(
            principal_id,
            tenant_id,
            role_id,
            collection=self.collection,
            session=session,
        )


@pytest.fixture
def mongo_context() -> Iterator[
    tuple[
        MongoClient[Any],
        Any,
        Any,
        Any,
        Any,
        Any,
    ]
]:
    client: MongoClient[Any] = MongoClient(
        MONGO_URI,
        serverSelectionTimeoutMS=3000,
        connectTimeoutMS=3000,
        socketTimeoutMS=5000,
        retryWrites=True,
        tz_aware=True,
    )
    database: Any = None

    try:
        hello = client.admin.command("hello")

        assert hello.get("setName") == EXPECTED_REPLICA_SET
        assert hello.get(
            "isWritablePrimary",
            hello.get("ismaster"),
        ) is True
        assert hello.get(
            "logicalSessionTimeoutMinutes"
        ) is not None

        database = client[
            f"wilsy_cx26_r3_service_{uuid.uuid4().hex}"
        ]

        principals = database["principal_authorities"]
        memberships = database["tenant_memberships"]
        assignments = database["role_assignments"]

        models = database.get_collection(
            registry_module.COLLECTION_NAME,
            write_concern=WriteConcern(
                w="majority",
                j=True,
            ),
            read_concern=ReadConcern("majority"),
        )

        PrincipalAuthorityRepository.ensure_indexes(
            principals
        )
        TenantMembershipRepository.ensure_indexes(
            memberships
        )
        RoleAssignmentRepository.ensure_indexes(
            assignments
        )

        registry_module.TenantLegalOperatingModelRegistry(
            models
        ).ensure_indexes()

        yield (
            client,
            database,
            principals,
            memberships,
            assignments,
            models,
        )
    finally:
        if database is not None:
            name = database.name
            client.drop_database(name)
            assert name not in client.list_database_names()
        client.close()


def seed_authorized_identity(
    *,
    principal_id: str,
    tenant_id: str,
    principals: Any,
    memberships: Any,
    assignments: Any,
    business_role: str = "tenant_admin",
    authorization_role: str = "ENTERPRISE_ADMIN",
) -> None:
    PrincipalAuthorityRepository.create(
        PrincipalAuthority(
            principal_id,
            PrincipalStatus.ACTIVE,
            0,
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

    RoleAssignmentRepository.insert(
        RoleAssignmentAuthority(
            principal_id,
            tenant_id,
            business_role,
            RoleAssignmentStatus.ACTIVE,
            0,
        ),
        assignments,
    )

    if authorization_role != business_role:
        RoleAssignmentRepository.insert(
            RoleAssignmentAuthority(
                principal_id,
                tenant_id,
                authorization_role,
                RoleAssignmentStatus.ACTIVE,
                0,
            ),
            assignments,
        )


def dependencies(
    principals: Any,
    memberships: Any,
    assignments: Any,
) -> dict[str, Any]:
    role_reader = RoleReader(assignments)

    return {
        "principal_repository": PrincipalReader(
            principals
        ),
        "membership_repository": MembershipReader(
            memberships
        ),
        "business_role_repository": role_reader,
        "role_assignment_repository": role_reader,
    }


def configure(
    *,
    principal_id: str,
    tenant_id: str,
    models: Any,
    principals: Any,
    memberships: Any,
    assignments: Any,
    session: Any,
    expected_revision: int | None,
    key: str,
    items: tuple[str, ...],
    effective_from: datetime,
):
    return service.configure_tenant_legal_operating_model(
        tenant_id=tenant_id,
        principal_id=principal_id,
        expected_revision=expected_revision,
        activated_item_ids=items,
        idempotency_key=key,
        registry=registry_module.TenantLegalOperatingModelRegistry(
            models
        ),
        session=session,
        effective_from=effective_from,
        **dependencies(
            principals,
            memberships,
            assignments,
        ),
    )


def test_real_authorized_create_exact_replay_and_current_read(
    mongo_context: tuple[
        MongoClient[Any],
        Any,
        Any,
        Any,
        Any,
        Any,
    ],
) -> None:
    (
        client,
        _database,
        principals,
        memberships,
        assignments,
        models,
    ) = mongo_context

    principal_id = f"principal-{uuid.uuid4().hex}"
    tenant_id = f"tenant-{uuid.uuid4().hex}"

    seed_authorized_identity(
        principal_id=principal_id,
        tenant_id=tenant_id,
        principals=principals,
        memberships=memberships,
        assignments=assignments,
    )

    with client.start_session() as session:
        with session.start_transaction():
            first = configure(
                principal_id=principal_id,
                tenant_id=tenant_id,
                models=models,
                principals=principals,
                memberships=memberships,
                assignments=assignments,
                session=session,
                expected_revision=None,
                key="create-r1",
                items=(
                    "PRACTICE_DISPUTES",
                    "PERSONA_PARTNER",
                ),
                effective_from=BASE,
            )

    assert first.revision == 1
    assert first.activated_item_ids == (
        "PERSONA_PARTNER",
        "PRACTICE_DISPUTES",
    )
    assert models.count_documents(
        {"tenant_id": tenant_id}
    ) == 1

    with client.start_session() as session:
        with session.start_transaction():
            replay = configure(
                principal_id=principal_id,
                tenant_id=tenant_id,
                models=models,
                principals=principals,
                memberships=memberships,
                assignments=assignments,
                session=session,
                expected_revision=None,
                key="create-r1",
                items=(
                    "PERSONA_PARTNER",
                    "PRACTICE_DISPUTES",
                ),
                effective_from=BASE
                + timedelta(minutes=10),
            )

            current = (
                service.get_current_tenant_legal_operating_model(
                    tenant_id=tenant_id,
                    principal_id=principal_id,
                    registry=registry_module.TenantLegalOperatingModelRegistry(
                        models
                    ),
                    session=session,
                    observed_at=BASE,
                    **dependencies(
                        principals,
                        memberships,
                        assignments,
                    ),
                )
            )

    assert replay == first
    assert current == first
    assert models.count_documents(
        {"tenant_id": tenant_id}
    ) == 1


def test_real_next_revision_and_stale_expected_revision_zero_write(
    mongo_context: tuple[
        MongoClient[Any],
        Any,
        Any,
        Any,
        Any,
        Any,
    ],
) -> None:
    (
        client,
        _database,
        principals,
        memberships,
        assignments,
        models,
    ) = mongo_context

    principal_id = f"principal-{uuid.uuid4().hex}"
    tenant_id = f"tenant-{uuid.uuid4().hex}"

    seed_authorized_identity(
        principal_id=principal_id,
        tenant_id=tenant_id,
        principals=principals,
        memberships=memberships,
        assignments=assignments,
    )

    with client.start_session() as session:
        with session.start_transaction():
            first = configure(
                principal_id=principal_id,
                tenant_id=tenant_id,
                models=models,
                principals=principals,
                memberships=memberships,
                assignments=assignments,
                session=session,
                expected_revision=None,
                key="r1",
                items=("PERSONA_PARTNER",),
                effective_from=BASE,
            )

    with client.start_session() as session:
        with session.start_transaction():
            second = configure(
                principal_id=principal_id,
                tenant_id=tenant_id,
                models=models,
                principals=principals,
                memberships=memberships,
                assignments=assignments,
                session=session,
                expected_revision=1,
                key="r2",
                items=(
                    "PERSONA_PARTNER",
                    "RISK_CONFLICTS",
                ),
                effective_from=BASE
                + timedelta(minutes=1),
            )

    assert first.revision == 1
    assert second.revision == 2
    assert (
        second.supersedes_operating_model_id
        == first.operating_model_id
    )

    before = list(
        models.find(
            {"tenant_id": tenant_id},
            {"_id": 0},
        )
    )

    with client.start_session() as session:
        session.start_transaction()
        with pytest.raises(
            service.TenantLegalOperatingModelRevisionConflictError,
            match="CX26_R3_EXPECTED_REVISION_CONFLICT",
        ):
            configure(
                principal_id=principal_id,
                tenant_id=tenant_id,
                models=models,
                principals=principals,
                memberships=memberships,
                assignments=assignments,
                session=session,
                expected_revision=1,
                key="stale-r3",
                items=("PERSONA_PARTNER",),
                effective_from=BASE
                + timedelta(minutes=2),
            )
        session.abort_transaction()

    after = list(
        models.find(
            {"tenant_id": tenant_id},
            {"_id": 0},
        )
    )

    assert after == before
    assert len(after) == 2


def test_real_divergent_idempotency_replay_zero_write(
    mongo_context: tuple[
        MongoClient[Any],
        Any,
        Any,
        Any,
        Any,
        Any,
    ],
) -> None:
    (
        client,
        _database,
        principals,
        memberships,
        assignments,
        models,
    ) = mongo_context

    principal_id = f"principal-{uuid.uuid4().hex}"
    tenant_id = f"tenant-{uuid.uuid4().hex}"

    seed_authorized_identity(
        principal_id=principal_id,
        tenant_id=tenant_id,
        principals=principals,
        memberships=memberships,
        assignments=assignments,
    )

    with client.start_session() as session:
        with session.start_transaction():
            configure(
                principal_id=principal_id,
                tenant_id=tenant_id,
                models=models,
                principals=principals,
                memberships=memberships,
                assignments=assignments,
                session=session,
                expected_revision=None,
                key="same-key",
                items=("PERSONA_PARTNER",),
                effective_from=BASE,
            )

    before = deepcopy(
        models.find_one({"tenant_id": tenant_id})
    )

    with client.start_session() as session:
        session.start_transaction()

        with pytest.raises(
            service.TenantLegalOperatingModelRevisionConflictError,
            match="CX26_R3_DIVERGENT_IDEMPOTENCY_REPLAY",
        ):
            configure(
                principal_id=principal_id,
                tenant_id=tenant_id,
                models=models,
                principals=principals,
                memberships=memberships,
                assignments=assignments,
                session=session,
                expected_revision=None,
                key="same-key",
                items=(
                    "PERSONA_PARTNER",
                    "PRACTICE_DISPUTES",
                ),
                effective_from=BASE
                + timedelta(minutes=1),
            )

        session.abort_transaction()

    assert models.count_documents(
        {"tenant_id": tenant_id}
    ) == 1
    assert (
        models.find_one({"tenant_id": tenant_id})
        == before
    )


def test_real_authorization_denial_precedes_operating_model_write(
    mongo_context: tuple[
        MongoClient[Any],
        Any,
        Any,
        Any,
        Any,
        Any,
    ],
) -> None:
    (
        client,
        _database,
        principals,
        memberships,
        assignments,
        models,
    ) = mongo_context

    principal_id = f"principal-{uuid.uuid4().hex}"
    tenant_id = f"tenant-{uuid.uuid4().hex}"

    seed_authorized_identity(
        principal_id=principal_id,
        tenant_id=tenant_id,
        principals=principals,
        memberships=memberships,
        assignments=assignments,
        business_role="tenant_owner",
        authorization_role="ENTERPRISE_ADMIN",
    )

    with client.start_session() as session:
        session.start_transaction()

        with pytest.raises(
            service.TenantLegalOperatingModelAuthorizationDeniedError,
            match="CX26_R3_AUTHORIZATION_DENIED",
        ):
            configure(
                principal_id=principal_id,
                tenant_id=tenant_id,
                models=models,
                principals=principals,
                memberships=memberships,
                assignments=assignments,
                session=session,
                expected_revision=None,
                key="denied",
                items=("PERSONA_PARTNER",),
                effective_from=BASE,
            )

        session.abort_transaction()

    assert models.count_documents(
        {"tenant_id": tenant_id}
    ) == 0


def test_real_missing_transaction_rejects_before_mutation(
    mongo_context: tuple[
        MongoClient[Any],
        Any,
        Any,
        Any,
        Any,
        Any,
    ],
) -> None:
    (
        client,
        _database,
        principals,
        memberships,
        assignments,
        models,
    ) = mongo_context

    principal_id = f"principal-{uuid.uuid4().hex}"
    tenant_id = f"tenant-{uuid.uuid4().hex}"

    seed_authorized_identity(
        principal_id=principal_id,
        tenant_id=tenant_id,
        principals=principals,
        memberships=memberships,
        assignments=assignments,
    )

    with client.start_session() as session:
        assert session.in_transaction is False

        with pytest.raises(
            service.TenantLegalOperatingModelAuthorityUnavailableError,
            match="CX26_R3_ACTIVE_TRANSACTION_REQUIRED",
        ):
            configure(
                principal_id=principal_id,
                tenant_id=tenant_id,
                models=models,
                principals=principals,
                memberships=memberships,
                assignments=assignments,
                session=session,
                expected_revision=None,
                key="no-transaction",
                items=("PERSONA_PARTNER",),
                effective_from=BASE,
            )

    assert models.count_documents(
        {"tenant_id": tenant_id}
    ) == 0


def test_real_caller_abort_rolls_back_successful_service_write(
    mongo_context: tuple[
        MongoClient[Any],
        Any,
        Any,
        Any,
        Any,
        Any,
    ],
) -> None:
    (
        client,
        _database,
        principals,
        memberships,
        assignments,
        models,
    ) = mongo_context

    principal_id = f"principal-{uuid.uuid4().hex}"
    tenant_id = f"tenant-{uuid.uuid4().hex}"

    seed_authorized_identity(
        principal_id=principal_id,
        tenant_id=tenant_id,
        principals=principals,
        memberships=memberships,
        assignments=assignments,
    )

    with client.start_session() as session:
        session.start_transaction()

        value = configure(
            principal_id=principal_id,
            tenant_id=tenant_id,
            models=models,
            principals=principals,
            memberships=memberships,
            assignments=assignments,
            session=session,
            expected_revision=None,
            key="abort-write",
            items=("PERSONA_PARTNER",),
            effective_from=BASE,
        )

        assert value.revision == 1
        assert models.count_documents(
            {"tenant_id": tenant_id},
            session=session,
        ) == 1

        session.abort_transaction()

    assert models.count_documents(
        {"tenant_id": tenant_id}
    ) == 0


def test_real_tenant_isolation_keeps_independent_current_truth(
    mongo_context: tuple[
        MongoClient[Any],
        Any,
        Any,
        Any,
        Any,
        Any,
    ],
) -> None:
    (
        client,
        _database,
        principals,
        memberships,
        assignments,
        models,
    ) = mongo_context

    principal_a = f"principal-a-{uuid.uuid4().hex}"
    principal_b = f"principal-b-{uuid.uuid4().hex}"
    tenant_a = f"tenant-a-{uuid.uuid4().hex}"
    tenant_b = f"tenant-b-{uuid.uuid4().hex}"

    seed_authorized_identity(
        principal_id=principal_a,
        tenant_id=tenant_a,
        principals=principals,
        memberships=memberships,
        assignments=assignments,
    )

    seed_authorized_identity(
        principal_id=principal_b,
        tenant_id=tenant_b,
        principals=principals,
        memberships=memberships,
        assignments=assignments,
    )

    with client.start_session() as session:
        with session.start_transaction():
            value_a = configure(
                principal_id=principal_a,
                tenant_id=tenant_a,
                models=models,
                principals=principals,
                memberships=memberships,
                assignments=assignments,
                session=session,
                expected_revision=None,
                key="tenant-a",
                items=("PERSONA_PARTNER",),
                effective_from=BASE,
            )

    with client.start_session() as session:
        with session.start_transaction():
            value_b = configure(
                principal_id=principal_b,
                tenant_id=tenant_b,
                models=models,
                principals=principals,
                memberships=memberships,
                assignments=assignments,
                session=session,
                expected_revision=None,
                key="tenant-b",
                items=("PRACTICE_DISPUTES",),
                effective_from=BASE,
            )

    assert value_a.tenant_id == tenant_a
    assert value_b.tenant_id == tenant_b
    assert models.count_documents(
        {"tenant_id": tenant_a}
    ) == 1
    assert models.count_documents(
        {"tenant_id": tenant_b}
    ) == 1


# ARTIFACT: test_tenant_legal_operating_model_service_real_mongo.py
# VERSION: v1.0.0-CX26-R3-CURRENT-OPERATING-MODEL-COMMAND-REAL-MONGO-CERT
# AUTHORITY BOUNDARY: exact service/IAM/registry composition evidence only; no transport or downstream authority
# TENANT POSTURE: UUID-isolated exact-tenant persistence and current IAM truth
# FAIL-CLOSED POSTURE: denial, missing transaction, stale revision, divergent replay, abort, and tenant crossing cannot create durable truth
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively
# END OF WILSY OS SOVEREIGN ARTIFACT
