"""
TITLE:
    WILSY OS P6 Privileged Activation Revocation Command Real-Mongo Certificate

VERSION:
    v1.2.0-P6-PRIVILEGED-ACTIVATION-REVOCATION-COMMAND-REAL-MONGO-CONCURRENCY

AUTHORITY:
    Wilsy OS IAM P6 certification only.

EPITOME:
    Exercise the P6 supervisory privileged-activation revocation command against
    a writable Mongo replica set using real principal authority, real current
    SYSTEM permission possession, immutable P6 command evidence, the dedicated
    durable evidence registry and the sealed activation registry inside one
    caller-owned transaction.

ABSOLUTE CANONICAL PATH:
    /Users/wilsonkhanyezi/legal-doc-system/tests/integration/
    test_privileged_activation_revocation_command_service_real_mongo.py

CERTIFICATION / UPDATE DATE:
    2026-10-15

CHANGELOG:
    v1.2.0-P6-PRIVILEGED-ACTIVATION-REVOCATION-COMMAND-REAL-MONGO-CONCURRENCY
        Adds a real writable-replica-set race certificate proving two
        competing, distinct supervisory revocation commands produce exactly
        one committed transaction, one denied transaction, one immutable
        command-evidence row and one terminal activation successor.
    v1.2.0-P6-PRIVILEGED-ACTIVATION-REVOCATION-COMMAND-REAL-MONGO-CONCURRENCY
        Expands the real-Mongo certificate across exact durable replay,
        divergent replay rejection, missing and revoked supervisory
        permission denial, caller-abort atomicity, temporal expiry,
        persisted-evidence corruption rejection, platform-scope isolation,
        and no-TTL/delete/break-glass/financial authority boundaries.
    v1.2.0-P6-PRIVILEGED-ACTIVATION-REVOCATION-COMMAND-REAL-MONGO-CONCURRENCY
        Initial RED real-Mongo certificate. Establishes replica-set/index
        posture and requires one authorized supervisor command to durably
        persist both immutable command evidence and the terminal activation
        revision atomically.

SECURITY / PRIVACY POSTURE:
    UUID-isolated disposable database. Synthetic identifiers only. No raw
    reason narrative, credential, bearer token, private key or financial data.

TENANT BOUNDARY:
    This initial certificate exercises PLATFORM_SYSTEM_ROOT only. Tenant scope
    is absent and cannot be manufactured by the command.

AUTHORITY BOUNDARY:
    Test certification only. No role grant, permission assignment policy,
    activation issuance policy, break-glass, HTTP or financial authority.

FINANCIAL AUTHORITY BOUNDARY:
    NONE.
"""

from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor
from threading import Barrier
from datetime import datetime, timedelta, timezone
import os
from typing import Any, Iterator
from uuid import uuid4

import pytest
from pymongo import MongoClient
from pymongo.errors import PyMongoError

from tools.eos.auth.current_system_permission_possession import (
    CurrentSystemPermissionPossessionResolver,
)
from tools.eos.auth.principal_authority import (
    PrincipalAuthority,
)
from tools.eos.auth.principal_authority_repository import (
    COLLECTION as PRINCIPAL_COLLECTION,
    PrincipalAuthorityRepository,
)
from tools.eos.auth.principal_status import (
    PrincipalStatus,
)
from tools.eos.auth.privileged_activation import (
    PrivilegedActivation,
)
from tools.eos.auth.privileged_activation_registry import (
    COLLECTION as ACTIVATION_COLLECTION,
    PrivilegedActivationRegistry,
)
from tools.eos.auth.privileged_activation_revocation_command_evidence import (
    PRIVILEGED_ACTIVATION_REVOKE_PERMISSION,
    PrivilegedActivationRevocationCommandEvidence,
)
from tools.eos.auth.privileged_activation_revocation_command_evidence_registry import (
    COLLECTION as EVIDENCE_COLLECTION,
    PrivilegedActivationRevocationCommandEvidencePersistedInvalidError,
    PrivilegedActivationRevocationCommandEvidenceRegistry,
)
from tools.eos.auth.privileged_activation_revocation_command_service import (
    PrivilegedActivationRevocationCommandError,
    PrivilegedActivationRevocationCommandService,
)
from tools.eos.auth.privileged_eligibility import (
    PrivilegedTargetClass,
)
from tools.eos.auth.privileged_security_assurance import (
    PrivilegedAssurancePurpose,
)
from tools.eos.auth.system_permission_assignment import (
    SystemPermissionAssignment,
)
from tools.eos.auth.system_permission_assignment_registry import (
    COLLECTION as ASSIGNMENT_COLLECTION,
    SystemPermissionAssignmentRegistry,
)


URI = os.environ.get(
    "TEST_VENDOR_MONGO_URI",
    "mongodb://127.0.0.1:27027/?replicaSet=wilsyVendorCertRS",
)

EXPECTED_REPLICA_SET = "wilsyVendorCertRS"

NOW = datetime(
    2026,
    10,
    15,
    7,
    0,
    tzinfo=timezone.utc,
)

REVOKE_AT = (
    NOW
    + timedelta(minutes=1)
)

SUPERVISOR = "principal-p6-supervisor"
TARGET = "principal-p6-target"

ASSIGNMENT_ID = "assignment-p6-revoke"
ACTIVATION_ID = "activation-p6-target"

ROLE_ID = "SOVEREIGN_ARCHITECT"


@pytest.fixture()
def context() -> Iterator[dict[str, Any]]:
    """Provide one UUID-isolated writable real-Mongo P6 command plane."""

    client: MongoClient[Any] = MongoClient(
        URI,
        serverSelectionTimeoutMS=5000,
        connectTimeoutMS=5000,
        socketTimeoutMS=5000,
        retryWrites=True,
    )

    hello = client.admin.command(
        "hello"
    )

    assert (
        hello.get("setName")
        == EXPECTED_REPLICA_SET
    )

    assert (
        hello.get("isWritablePrimary")
        is True
    )

    assert (
        hello.get(
            "logicalSessionTimeoutMinutes"
        )
        is not None
    )

    db_name = (
        "wilsy_p6_revocation_"
        + uuid4().hex
    )

    assert db_name != "wilsy"

    database = client[
        db_name
    ]

    principals = database[
        PRINCIPAL_COLLECTION
    ]

    assignments = database[
        ASSIGNMENT_COLLECTION
    ]

    activations = database[
        ACTIVATION_COLLECTION
    ]

    evidence_collection = database[
        EVIDENCE_COLLECTION
    ]

    PrincipalAuthorityRepository.ensure_indexes(
        principals
    )

    assignment_registry = (
        SystemPermissionAssignmentRegistry(
            assignments
        )
    )

    assignment_registry.ensure_indexes()

    activation_registry = (
        PrivilegedActivationRegistry(
            activations
        )
    )

    activation_registry.ensure_indexes()

    evidence_registry = (
        PrivilegedActivationRevocationCommandEvidenceRegistry(
            evidence_collection
        )
    )

    evidence_registry.ensure_indexes()

    possession = (
        CurrentSystemPermissionPossessionResolver(
            principal_collection=
                principals,
            assignment_registry=
                assignment_registry,
        )
    )

    service = (
        PrivilegedActivationRevocationCommandService(
            possession_resolver=
                possession,
            activation_registry=
                activation_registry,
            evidence_registry=
                evidence_registry,
        )
    )

    result = {
        "client": client,
        "database": database,
        "db_name": db_name,
        "principals": principals,
        "assignments": assignments,
        "activations": activations,
        "evidence_collection":
            evidence_collection,
        "assignment_registry":
            assignment_registry,
        "activation_registry":
            activation_registry,
        "evidence_registry":
            evidence_registry,
        "service": service,
    }

    try:
        yield result

    finally:
        client.drop_database(
            db_name
        )

        assert (
            db_name
            not in client.list_database_names()
        )

        client.close()


def _activation() -> PrivilegedActivation:
    """Build one real persisted PLATFORM_SYSTEM_ROOT activation."""

    return PrivilegedActivation.issue(
        activation_id=ACTIVATION_ID,
        tenant_id=None,
        principal_id=TARGET,
        actor_principal_id=TARGET,
        privileged_role_id=ROLE_ID,
        target_class=(
            PrivilegedTargetClass
            .PLATFORM_SYSTEM_ROOT
        ),
        eligibility_evidence_id=
            "eligibility-p6-target",
        eligibility_evidence_fingerprint=
            "a" * 128,
        assurance_evidence_id=
            "assurance-p6-target",
        assurance_evidence_fingerprint=
            "b" * 128,
        creation_assurance_purpose=(
            PrivilegedAssurancePurpose
            .PRIVILEGED_ELIGIBILITY_TO_ACTIVATION
        ),
        activated_at=NOW,
        effective_until=(
            NOW
            + timedelta(minutes=10)
        ),
        issuance_idempotency_key=
            "issue-p6-target",
    )


def _assignment() -> SystemPermissionAssignment:
    """Build the supervisor's exact P6 SYSTEM permission assignment."""

    return SystemPermissionAssignment.assign(
        assignment_id=
            ASSIGNMENT_ID,
        principal_id=
            SUPERVISOR,
        permission_id=
            PRIVILEGED_ACTIVATION_REVOKE_PERMISSION,
        assigned_by_principal_id=
            "principal-p6-governance",
        assigned_at=(
            NOW
            - timedelta(minutes=1)
        ),
        assignment_evidence_reference=
            "governance:p6-revoke",
    )


def _seed(
    context: dict[str, Any],
) -> tuple[
    PrivilegedActivation,
    SystemPermissionAssignment,
]:
    """Persist actor/target principals, actor authority and target activation."""

    activation = _activation()
    assignment = _assignment()

    with context[
        "client"
    ].start_session() as session:
        session.start_transaction()

        PrincipalAuthorityRepository.create(
            PrincipalAuthority(
                SUPERVISOR,
                PrincipalStatus.ACTIVE,
                1,
            ),
            context[
                "principals"
            ],
            session=session,
        )

        PrincipalAuthorityRepository.create(
            PrincipalAuthority(
                TARGET,
                PrincipalStatus.ACTIVE,
                1,
            ),
            context[
                "principals"
            ],
            session=session,
        )

        context[
            "assignment_registry"
        ].create_or_replay(
            assignment,
            idempotency_key=
                "assignment-p6-create",
            session=session,
        )

        context[
            "activation_registry"
        ].create_or_replay(
            activation,
            session=session,
        )

        session.commit_transaction()

    return (
        activation,
        assignment,
    )


def _evidence(
    *,
    activation: PrivilegedActivation,
    assignment: SystemPermissionAssignment,
    idempotency_key: str = "revoke-p6-command",
) -> PrivilegedActivationRevocationCommandEvidence:
    """Compose one exact real-Mongo P6 supervisory command."""

    return (
        PrivilegedActivationRevocationCommandEvidence
        .compose(
            actor_principal_id=
                SUPERVISOR,
            actor_permission_id=
                PRIVILEGED_ACTIVATION_REVOKE_PERMISSION,
            actor_permission_assignment_id=
                assignment.assignment_id,
            actor_permission_assignment_revision=
                assignment.revision,
            actor_permission_assignment_fingerprint=
                assignment.assignment_fingerprint,
            target_activation_id=
                activation.activation_id,
            target_principal_id=
                activation.principal_id,
            target_class=
                activation.target_class.value,
            target_tenant_id=
                activation.tenant_id,
            revocation_reason_reference=
                "security-review:p6:001",
            authorized_at=
                REVOKE_AT,
            idempotency_key=
                idempotency_key,
        )
    )


def _commit_command(
    context: dict[str, Any],
    evidence: PrivilegedActivationRevocationCommandEvidence,
):
    """Commit one P6 command in one caller-owned transaction."""

    with context[
        "client"
    ].start_session() as session:
        session.start_transaction()

        result = context[
            "service"
        ].revoke(
            evidence,
            session=session,
        )

        session.commit_transaction()

    return result


def _revoke_supervisor_permission(
    context: dict[str, Any],
    assignment: SystemPermissionAssignment,
) -> SystemPermissionAssignment:
    """Persist the terminal revision of the supervisor's revoke permission."""

    revoked = assignment.revoke(
        revoked_by_principal_id=
            "principal-p6-governance",
        revoked_at=(
            NOW
            + timedelta(seconds=30)
        ),
        revocation_evidence_reference=
            "governance:p6-revoke-withdrawn",
    )

    with context[
        "client"
    ].start_session() as session:
        session.start_transaction()

        context[
            "assignment_registry"
        ].revoke_or_replay(
            revoked,
            revocation_idempotency_key=
                "assignment-p6-revoke",
            session=session,
        )

        session.commit_transaction()

    return revoked


def test_real_mongo_index_contract_and_no_ttl(
    context: dict[str, Any],
) -> None:
    """P6 evidence registry has exactly four custom non-TTL indexes."""

    indexes = list(
        context[
            "evidence_collection"
        ].list_indexes()
    )

    custom = [
        value
        for value in indexes
        if value["name"] != "_id_"
    ]

    assert len(custom) == 4

    assert all(
        "expireAfterSeconds"
        not in value
        for value in custom
    )


def test_real_authorized_supervisor_revokes_atomically(
    context: dict[str, Any],
) -> None:
    """One current supervisor command must durably revoke one exact activation."""

    activation, assignment = _seed(
        context
    )

    evidence = _evidence(
        activation=activation,
        assignment=assignment,
    )

    with context[
        "client"
    ].start_session() as session:
        session.start_transaction()

        result = context[
            "service"
        ].revoke(
            evidence,
            session=session,
        )

        assert (
            result.evidence
            == evidence
        )

        assert (
            result.activation.status.value
            == "REVOKED"
        )

        assert (
            context[
                "evidence_collection"
            ].count_documents(
                {},
                session=session,
            )
            == 1
        )

        assert (
            len(
                context[
                    "activation_registry"
                ].get_history(
                    ACTIVATION_ID,
                    session=session,
                )
            )
            == 2
        )

        session.commit_transaction()

    history = (
        context[
            "activation_registry"
        ].get_history(
            ACTIVATION_ID
        )
    )

    assert len(history) == 2

    assert (
        history[-1].status.value
        == "REVOKED"
    )

    assert (
        context[
            "evidence_collection"
        ].count_documents({})
        == 1
    )


def test_real_exact_durable_replay_returns_same_terminal_result(
    context: dict[str, Any],
) -> None:
    """Exact command replay preserves one evidence row and one terminal successor."""

    activation, assignment = _seed(
        context
    )

    evidence = _evidence(
        activation=activation,
        assignment=assignment,
    )

    first = _commit_command(
        context,
        evidence,
    )

    second = _commit_command(
        context,
        evidence,
    )

    assert first == second

    assert (
        context[
            "evidence_collection"
        ].count_documents({})
        == 1
    )

    history = context[
        "activation_registry"
    ].get_history(
        ACTIVATION_ID
    )

    assert len(history) == 2

    assert (
        history[-1].status.value
        == "REVOKED"
    )


def test_real_missing_revoke_permission_denies_before_mutation(
    context: dict[str, Any],
) -> None:
    """Supervisor without current explicit P6 permission cannot revoke."""

    activation = _activation()

    with context[
        "client"
    ].start_session() as session:
        session.start_transaction()

        PrincipalAuthorityRepository.create(
            PrincipalAuthority(
                SUPERVISOR,
                PrincipalStatus.ACTIVE,
                1,
            ),
            context[
                "principals"
            ],
            session=session,
        )

        PrincipalAuthorityRepository.create(
            PrincipalAuthority(
                TARGET,
                PrincipalStatus.ACTIVE,
                1,
            ),
            context[
                "principals"
            ],
            session=session,
        )

        context[
            "activation_registry"
        ].create_or_replay(
            activation,
            session=session,
        )

        session.commit_transaction()

    synthetic_assignment = _assignment()

    evidence = _evidence(
        activation=activation,
        assignment=synthetic_assignment,
    )

    with context[
        "client"
    ].start_session() as session:
        session.start_transaction()

        with pytest.raises(
            PrivilegedActivationRevocationCommandError,
            match="CURRENT_REVOCATION_AUTHORITY_REQUIRED",
        ):
            context[
                "service"
            ].revoke(
                evidence,
                session=session,
            )

        session.abort_transaction()

    assert (
        context[
            "evidence_collection"
        ].count_documents({})
        == 0
    )

    assert (
        context[
            "activation_registry"
        ].get_history(
            ACTIVATION_ID
        )
        == (
            activation,
        )
    )


def test_real_revoked_supervisor_permission_denies_before_mutation(
    context: dict[str, Any],
) -> None:
    """A historic assignment cannot authorize a later P6 command."""

    activation, assignment = _seed(
        context
    )

    _revoke_supervisor_permission(
        context,
        assignment,
    )

    evidence = _evidence(
        activation=activation,
        assignment=assignment,
    )

    with context[
        "client"
    ].start_session() as session:
        session.start_transaction()

        with pytest.raises(
            PrivilegedActivationRevocationCommandError,
            match="CURRENT_REVOCATION_AUTHORITY_REQUIRED",
        ):
            context[
                "service"
            ].revoke(
                evidence,
                session=session,
            )

        session.abort_transaction()

    assert (
        context[
            "evidence_collection"
        ].count_documents({})
        == 0
    )

    assert (
        context[
            "activation_registry"
        ].get_history(
            ACTIVATION_ID
        )
        == (
            activation,
        )
    )


def test_real_divergent_idempotency_replay_fails_closed(
    context: dict[str, Any],
) -> None:
    """Same actor+idempotency key cannot represent a different command."""

    activation, assignment = _seed(
        context
    )

    original = _evidence(
        activation=activation,
        assignment=assignment,
    )

    _commit_command(
        context,
        original,
    )

    divergent = (
        PrivilegedActivationRevocationCommandEvidence
        .compose(
            actor_principal_id=
                SUPERVISOR,
            actor_permission_id=
                PRIVILEGED_ACTIVATION_REVOKE_PERMISSION,
            actor_permission_assignment_id=
                assignment.assignment_id,
            actor_permission_assignment_revision=
                assignment.revision,
            actor_permission_assignment_fingerprint=
                assignment.assignment_fingerprint,
            target_activation_id=
                activation.activation_id,
            target_principal_id=
                activation.principal_id,
            target_class=
                activation.target_class.value,
            target_tenant_id=
                activation.tenant_id,
            revocation_reason_reference=
                "security-review:p6:DIFFERENT",
            authorized_at=
                REVOKE_AT,
            idempotency_key=
                original.idempotency_key,
        )
    )

    with context[
        "client"
    ].start_session() as session:
        session.start_transaction()

        with pytest.raises(
            PrivilegedActivationRevocationCommandError,
            match="DIVERGENT_IDEMPOTENCY_REPLAY",
        ):
            context[
                "service"
            ].revoke(
                divergent,
                session=session,
            )

        session.abort_transaction()

    assert (
        context[
            "evidence_collection"
        ].count_documents({})
        == 1
    )

    assert (
        len(
            context[
                "activation_registry"
            ].get_history(
                ACTIVATION_ID
            )
        )
        == 2
    )


def test_real_caller_abort_rolls_back_evidence_and_revocation(
    context: dict[str, Any],
) -> None:
    """Evidence and terminal activation revision share one atomic caller transaction."""

    activation, assignment = _seed(
        context
    )

    evidence = _evidence(
        activation=activation,
        assignment=assignment,
        idempotency_key=
            "revoke-p6-abort",
    )

    with context[
        "client"
    ].start_session() as session:
        session.start_transaction()

        result = context[
            "service"
        ].revoke(
            evidence,
            session=session,
        )

        assert (
            result.activation.status.value
            == "REVOKED"
        )

        assert (
            context[
                "evidence_collection"
            ].count_documents(
                {},
                session=session,
            )
            == 1
        )

        assert (
            len(
                context[
                    "activation_registry"
                ].get_history(
                    ACTIVATION_ID,
                    session=session,
                )
            )
            == 2
        )

        session.abort_transaction()

    assert (
        context[
            "evidence_collection"
        ].count_documents({})
        == 0
    )

    assert (
        context[
            "activation_registry"
        ].get_history(
            ACTIVATION_ID
        )
        == (
            activation,
        )
    )


def test_real_expired_activation_denies_without_evidence(
    context: dict[str, Any],
) -> None:
    """An expired activation cannot be newly revoked by supervisory command."""

    activation, assignment = _seed(
        context
    )

    expired_time = (
        activation.effective_until
        + timedelta(seconds=1)
    )

    evidence = (
        PrivilegedActivationRevocationCommandEvidence
        .compose(
            actor_principal_id=
                SUPERVISOR,
            actor_permission_id=
                PRIVILEGED_ACTIVATION_REVOKE_PERMISSION,
            actor_permission_assignment_id=
                assignment.assignment_id,
            actor_permission_assignment_revision=
                assignment.revision,
            actor_permission_assignment_fingerprint=
                assignment.assignment_fingerprint,
            target_activation_id=
                activation.activation_id,
            target_principal_id=
                activation.principal_id,
            target_class=
                activation.target_class.value,
            target_tenant_id=
                activation.tenant_id,
            revocation_reason_reference=
                "security-review:p6:expired",
            authorized_at=
                expired_time,
            idempotency_key=
                "revoke-p6-expired",
        )
    )

    with context[
        "client"
    ].start_session() as session:
        session.start_transaction()

        with pytest.raises(
            PrivilegedActivationRevocationCommandError,
            match="CURRENT_TARGET_ACTIVATION_REQUIRED",
        ):
            context[
                "service"
            ].revoke(
                evidence,
                session=session,
            )

        session.abort_transaction()

    assert (
        context[
            "evidence_collection"
        ].count_documents({})
        == 0
    )

    assert (
        context[
            "activation_registry"
        ].get_history(
            ACTIVATION_ID
        )
        == (
            activation,
        )
    )


def test_real_corrupt_command_evidence_fails_closed(
    context: dict[str, Any],
) -> None:
    """Persisted evidence corruption is detected before replay is returned."""

    activation, assignment = _seed(
        context
    )

    evidence = _evidence(
        activation=activation,
        assignment=assignment,
    )

    _commit_command(
        context,
        evidence,
    )

    context[
        "evidence_collection"
    ].update_one(
        {
            "revocation_command_evidence_id":
                evidence.revocation_command_evidence_id,
        },
        {
            "$set": {
                "fingerprint":
                    "0" * 128,
            }
        },
    )

    with pytest.raises(
        PrivilegedActivationRevocationCommandEvidencePersistedInvalidError
    ):
        context[
            "evidence_registry"
        ].get(
            revocation_command_evidence_id=
                evidence.revocation_command_evidence_id,
        )


def test_real_platform_target_persists_no_tenant_material(
    context: dict[str, Any],
) -> None:
    """PLATFORM_SYSTEM_ROOT revocation evidence cannot manufacture tenant scope."""

    activation, assignment = _seed(
        context
    )

    evidence = _evidence(
        activation=activation,
        assignment=assignment,
        idempotency_key=
            "revoke-p6-platform-scope",
    )

    _commit_command(
        context,
        evidence,
    )

    row = context[
        "evidence_collection"
    ].find_one(
        {
            "revocation_command_evidence_id":
                evidence.revocation_command_evidence_id,
        }
    )

    assert row is not None

    assert (
        row["target_class"]
        == "PLATFORM_SYSTEM_ROOT"
    )

    assert (
        row["target_tenant_id"]
        is None
    )


def test_real_no_ttl_delete_break_glass_or_financial_authority(
    context: dict[str, Any],
) -> None:
    """P6 persistence introduces no hidden expiry/delete or adjacent authority."""

    activation, assignment = _seed(
        context
    )

    evidence = _evidence(
        activation=activation,
        assignment=assignment,
        idempotency_key=
            "revoke-p6-boundary",
    )

    _commit_command(
        context,
        evidence,
    )

    indexes = list(
        context[
            "evidence_collection"
        ].list_indexes()
    )

    assert all(
        "expireAfterSeconds"
        not in value
        for value in indexes
    )

    row = context[
        "evidence_collection"
    ].find_one({})

    assert row is not None

    lowered = {
        str(key).casefold()
        for key in row
    }

    for forbidden in (
        "password",
        "otp",
        "jwt",
        "bearer",
        "private_key",
        "raw_reason",
        "payment",
        "settlement",
        "financial",
        "break_glass",
    ):
        assert all(
            forbidden
            not in key
            for key in lowered
        )

    collections = set(
        context[
            "database"
        ].list_collection_names()
    )

    assert not any(
        (
            "break_glass" in name
            or "payment" in name
            or "settlement" in name
            or "financial" in name
        )
        for name in collections
    )


def test_real_competing_revocations_have_one_durable_winner(
    context: dict[str, Any],
) -> None:
    """Two competing commands produce one durable terminal transition only."""

    activation, assignment = _seed(
        context
    )

    first = _evidence(
        activation=activation,
        assignment=assignment,
        idempotency_key=
            "revoke-p6-race-a",
    )

    second = (
        PrivilegedActivationRevocationCommandEvidence
        .compose(
            actor_principal_id=
                SUPERVISOR,
            actor_permission_id=
                PRIVILEGED_ACTIVATION_REVOKE_PERMISSION,
            actor_permission_assignment_id=
                assignment.assignment_id,
            actor_permission_assignment_revision=
                assignment.revision,
            actor_permission_assignment_fingerprint=
                assignment.assignment_fingerprint,
            target_activation_id=
                activation.activation_id,
            target_principal_id=
                activation.principal_id,
            target_class=
                activation.target_class.value,
            target_tenant_id=
                activation.tenant_id,
            revocation_reason_reference=
                "security-review:p6:race-b",
            authorized_at=
                REVOKE_AT,
            idempotency_key=
                "revoke-p6-race-b",
        )
    )

    barrier = Barrier(
        2
    )

    def worker(
        evidence: PrivilegedActivationRevocationCommandEvidence,
    ) -> str:
        with context[
            "client"
        ].start_session() as session:
            session.start_transaction()

            barrier.wait(
                timeout=5
            )

            try:
                context[
                    "service"
                ].revoke(
                    evidence,
                    session=session,
                )

                session.commit_transaction()

                return "COMMITTED"

            except (
                PrivilegedActivationRevocationCommandError,
                PyMongoError,
            ):
                if session.in_transaction:
                    session.abort_transaction()

                return "DENIED"

    with ThreadPoolExecutor(
        max_workers=2
    ) as pool:
        futures = (
            pool.submit(
                worker,
                first,
            ),
            pool.submit(
                worker,
                second,
            ),
        )

        results = tuple(
            future.result(
                timeout=15
            )
            for future in futures
        )

    assert (
        results.count(
            "COMMITTED"
        )
        == 1
    )

    assert (
        results.count(
            "DENIED"
        )
        == 1
    )

    history = context[
        "activation_registry"
    ].get_history(
        ACTIVATION_ID
    )

    assert len(
        history
    ) == 2

    assert (
        history[0].status.value
        == "ACTIVE"
    )

    assert (
        history[1].status.value
        == "REVOKED"
    )

    assert (
        context[
            "evidence_collection"
        ].count_documents({})
        == 1
    )

    durable = context[
        "evidence_collection"
    ].find_one({})

    assert durable is not None

    assert (
        durable["idempotency_key"]
        in {
            first.idempotency_key,
            second.idempotency_key,
        }
    )

    assert (
        durable[
            "revocation_reason_reference"
        ]
        in {
            first.revocation_reason_reference,
            second.revocation_reason_reference,
        }
    )


# WILSY OS SOVEREIGN TEST ARTIFACT SEAL
# ARTIFACT: test_privileged_activation_revocation_command_service_real_mongo.py
# VERSION: v1.2.0-P6-PRIVILEGED-ACTIVATION-REVOCATION-COMMAND-REAL-MONGO-CONCURRENCY
# AUTHORITY BOUNDARY: P6 REAL-MONGO CERTIFICATION ONLY; NO RUNTIME AUTHORITY
# TENANT POSTURE: PLATFORM_SYSTEM_ROOT INITIAL CERTIFICATE; TENANT MATERIAL ABSENT
# FAIL-CLOSED POSTURE: WRITABLE REPLICA SET, CALLER TRANSACTION, IMMUTABLE EVIDENCE, NO TTL
# FINANCIAL EXECUTION AUTHORITY: NONE
# END OF WILSY OS SOVEREIGN TEST ARTIFACT
