"""Real-Mongo certificate for authorized provider-object disownership issuance.

TITLE: WILSY OS Authorized Provider-Object Disownership Real-Mongo Certificate
VERSION: v1.0.0-L10A2R-C4D6D-A3-REAL-MONGO-CERT
AUTHORITY: WILSY OS Core Governance / Python EOS Legal Operations
EPITOME: Prove A3 durable IAM evidence and A2 positive disownership persistence
         share one caller-owned Mongo transaction with rollback and exact replay.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tests/integration/test_legal_evidence_provider_object_disownership_orchestrator_real_mongo.py
COLLABORATION / OWNERSHIP: C4D6D-A3 owns orchestration; A3-A1 owns the certified
                            IAM operation/permission/role binding; IAM owns
                            durable authorization evidence; A1 owns the immutable
                            disownership fact; A2 owns exact persistence/replay.
CERTIFICATION / UPDATE DATE: 2026-10-01
CHANGELOG: 2026-10-01 v1.0.0-L10A2R-C4D6D-A3-REAL-MONGO-CERT establishes
           disposable replica-set certification for topology, active transaction
           enforcement, same-session IAM+A2 writes, commit/restart replay,
           rollback atomicity, divergent-intent rejection and tenant opacity.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2; ISO 27001.
SECURITY / PRIVACY POSTURE: UUID-isolated synthetic database only. URI,
                             credentials, tokens and PII are never printed.
TENANT BOUNDARY: Every durable IAM and disownership identity is exact tenant
                 scoped. The disposable database is never named ``wilsy``.
AUTHORITY BOUNDARY: Runtime durability certificate only. A3-A1 separately owns
                    authorization-policy correctness. This certificate creates
                    no orphan proof, preservation release or deletion authority.
FINANCIAL AUTHORITY BOUNDARY: Kennel EOS exclusively owns financial execution
                              and settlement truth.
TRANSACTION BOUNDARY: This test owns all sessions, transactions, commits and
                      aborts. Production orchestration owns none of them.
FAIL-CLOSED DECLARATION: Topology drift, inactive transaction, divergent IAM
                         replay, persistence mismatch or rollback leakage fails.
"""

from __future__ import annotations

import hashlib
import os
import uuid
from types import SimpleNamespace
from typing import Any, Iterator, cast

import pytest
from pymongo import MongoClient, version as pymongo_version
from pymongo.errors import PyMongoError
from pymongo.read_concern import ReadConcern

from tools.eos.auth.identity import SovereignIdentity
from tools.eos.auth.principal_status import PrincipalStatus
from tools.eos.auth.role_assignment import RoleAssignmentStatus
from tools.eos.auth.tenant_membership import TenantMembershipStatus
from tools.eos.auth.tenant_authorization import (
    TenantAuthorizationDecision,
    TenantAuthorizationReason,
)
from tools.eos.auth import (
    tenant_authorization_decision_evidence_registry as iam_module,
)
from tools.eos.auth.tenant_authorization_decision_evidence_registry import (
    TenantAuthorizationDecisionEvidenceRegistry,
)
from tools.eos.legal_operations.orchestration import (
    legal_evidence_provider_object_disownership_orchestrator as issuer,
)
from tools.eos.legal_operations.registry.legal_evidence_provider_object_disownership_registry import (
    COLLECTION as DISOWNERSHIP_COLLECTION,
    LegalEvidenceProviderObjectDisownershipRegistry,
)


MONGO_URI = os.getenv(
    "TEST_VENDOR_MONGO_URI",
    "mongodb://127.0.0.1:27027/?replicaSet=wilsyVendorCertRS",
)

REPLICA_SET = "wilsyVendorCertRS"
MONGO_VERSION = "7.0.37"

IAM_COLLECTION = "tenant_authorization_decision_evidence"

TENANT = "tenant-c4d6d-a3"
OTHER_TENANT = "tenant-c4d6d-a3-other"
PRINCIPAL = "principal-c4d6d-a3"

SOURCE_FP = hashlib.sha3_512(
    b"c4d6d-a3-real-source"
).hexdigest()


class TrackingCollection:
    """Record every passed session while delegating to an actual collection."""

    def __init__(
        self,
        inner: Any,
    ) -> None:
        self.inner = inner
        self.sessions: list[Any] = []
        self.operations: list[str] = []

    def _record(
        self,
        operation: str,
        kwargs: dict[str, Any],
    ) -> None:
        self.operations.append(
            operation
        )
        self.sessions.append(
            kwargs.get(
                "session"
            )
        )

    def find_one(
        self,
        *args: Any,
        **kwargs: Any,
    ) -> Any:
        self._record(
            "find_one",
            kwargs,
        )
        return self.inner.find_one(
            *args,
            **kwargs,
        )

    def insert_one(
        self,
        *args: Any,
        **kwargs: Any,
    ) -> Any:
        self._record(
            "insert_one",
            kwargs,
        )
        return self.inner.insert_one(
            *args,
            **kwargs,
        )

    def create_index(
        self,
        *args: Any,
        **kwargs: Any,
    ) -> Any:
        return self.inner.create_index(
            *args,
            **kwargs,
        )

    def __getattr__(
        self,
        name: str,
    ) -> Any:
        return getattr(
            self.inner,
            name,
        )


class PrincipalRepository:
    """Expose one active principal snapshot to the canonical IAM composer."""

    @staticmethod
    def resolve(
        principal_id: str,
        *,
        session: Any = None,
    ) -> object:
        assert principal_id == PRINCIPAL
        assert session is not None

        return SimpleNamespace(
            status=PrincipalStatus.ACTIVE,
        )


class MembershipRepository:
    """Expose current tenant membership and revision to durable IAM evidence."""

    @staticmethod
    def resolve(
        principal_id: str,
        tenant_id: str,
        *,
        session: Any = None,
    ) -> object:
        assert principal_id == PRINCIPAL
        assert tenant_id in {
            TENANT,
            OTHER_TENANT,
        }
        assert session is not None

        return SimpleNamespace(
            status=TenantMembershipStatus.ACTIVE,
            revision=3,
        )


class AssignmentRepository:
    """Expose the certified LEGAL_PARTNER assignment and revision."""

    @staticmethod
    def resolve(
        principal_id: str,
        tenant_id: str,
        role_id: str,
        *,
        session: Any = None,
    ) -> object:
        assert principal_id == PRINCIPAL
        assert tenant_id in {
            TENANT,
            OTHER_TENANT,
        }
        assert role_id == "LEGAL_PARTNER"
        assert session is not None

        return SimpleNamespace(
            status=RoleAssignmentStatus.ACTIVE,
            revision=4,
        )


class BusinessRoleRepository:
    """Injected boundary retained for the canonical authorizer contract."""

    @staticmethod
    def resolve(
        principal_id: str,
        tenant_id: str,
        role_id: str,
        *,
        session: Any = None,
    ) -> object:
        assert principal_id == PRINCIPAL
        assert tenant_id in {
            TENANT,
            OTHER_TENANT,
        }
        assert session is not None

        return SimpleNamespace(
            status=RoleAssignmentStatus.ACTIVE,
            revision=5,
            role_id=role_id,
        )


def _authorized(
    **_kwargs: Any,
) -> TenantAuthorizationDecision:
    """Freeze only the already-certified A3-A1 authorization outcome."""
    return TenantAuthorizationDecision(
        True,
        TenantAuthorizationReason.AUTHORIZED,
        "tenant_legal_partner",
        "LEGAL_PARTNER",
    )


def _identity(
    tenant_id: str = TENANT,
) -> SovereignIdentity:
    """Build one synthetic active server-authenticated identity."""
    return SovereignIdentity(
        identity_id=PRINCIPAL,
        tenant_id=tenant_id,
        username="c4d6d-a3-operator",
        email="c4d6d-a3@example.test",
        auth_method="TEST",
        status=PrincipalStatus.ACTIVE,
    )


def _iam_registry(
    collection: Any,
) -> TenantAuthorizationDecisionEvidenceRegistry:
    """Bind durable IAM evidence to the disposable real collection."""
    return TenantAuthorizationDecisionEvidenceRegistry(
        cast(
            Any,
            collection,
        ),
        principal_repository=PrincipalRepository(),
        membership_repository=MembershipRepository(),
        role_assignment_repository=AssignmentRepository(),
        business_role_repository=BusinessRoleRepository(),
    )


def _disownership_registry(
    collection: Any,
) -> LegalEvidenceProviderObjectDisownershipRegistry:
    """Bind A2 exact persistence to the disposable real collection."""
    return LegalEvidenceProviderObjectDisownershipRegistry(
        cast(
            Any,
            collection,
        )
    )


def _issue(
    *,
    identity: SovereignIdentity,
    authorization_registry: TenantAuthorizationDecisionEvidenceRegistry,
    disownership_registry: LegalEvidenceProviderObjectDisownershipRegistry,
    session: Any,
    disownership_reference: str,
    reason_reference: str = "reason:c4d6d-a3-real",
):
    """Call production A3 with fixed synthetic evidence inputs."""
    return issuer.issue_legal_evidence_provider_object_disownership(
        identity=identity,
        provider_name="s3",
        storage_reference="bucket/c4d6d-a3/object",
        object_version_reference="version-c4d6d-a3",
        disownership_reference=disownership_reference,
        reason_reference=reason_reference,
        source_evidence_reference="source:c4d6d-a3-real",
        source_evidence_fingerprint=SOURCE_FP,
        authorization_evidence_registry=authorization_registry,
        disownership_registry=disownership_registry,
        session=session,
    )


@pytest.fixture()
def mongo_context(
    monkeypatch: pytest.MonkeyPatch,
) -> Iterator[
    tuple[
        MongoClient[Any],
        Any,
        Any,
        Any,
    ]
]:
    """Yield one UUID-isolated database on the sanctioned replica set."""
    monkeypatch.setattr(
        iam_module,
        "authorize_tenant_operation",
        _authorized,
    )

    client: MongoClient[Any] = MongoClient(
        MONGO_URI,
        serverSelectionTimeoutMS=5_000,
        connectTimeoutMS=5_000,
        retryWrites=True,
        tz_aware=True,
    )

    database: Any = None

    try:
        try:
            hello = client.admin.command(
                "hello"
            )
            version = client.server_info().get(
                "version"
            )
        except (
            PyMongoError,
            OSError,
        ) as error:
            pytest.skip(
                "real Mongo unavailable for operator runtime: "
                + type(error).__name__
            )

        assert hello.get(
            "setName"
        ) == REPLICA_SET
        assert hello.get(
            "isWritablePrimary",
            hello.get(
                "ismaster"
            ),
        ) is True
        assert hello.get(
            "logicalSessionTimeoutMinutes"
        ) is not None
        assert version == MONGO_VERSION

        with client.start_session() as probe:
            probe.start_transaction(
                read_concern=ReadConcern(
                    "snapshot"
                )
            )
            assert probe.in_transaction is True
            probe.abort_transaction()

        name = (
            "wilsy_c4d6d_a3_"
            + uuid.uuid4().hex
        )

        assert len(
            name
        ) <= 63
        assert name != "wilsy"

        database = client[
            name
        ]

        iam_collection = database[
            IAM_COLLECTION
        ]
        disownership_collection = database[
            DISOWNERSHIP_COLLECTION
        ]

        iam_registry = _iam_registry(
            iam_collection
        )
        disownership_registry = _disownership_registry(
            disownership_collection
        )

        iam_registry.ensure_indexes()
        disownership_registry.ensure_indexes()

        yield (
            client,
            database,
            iam_collection,
            disownership_collection,
        )
    finally:
        if database is not None:
            client.drop_database(
                database.name
            )
        client.close()


def test_real_topology_and_inactive_transaction_reject_before_write(
    mongo_context: tuple[
        MongoClient[Any],
        Any,
        Any,
        Any,
    ],
) -> None:
    """A3 rejects absence or inactive sessions before either durable write."""
    client, database, iam_collection, disownership_collection = (
        mongo_context
    )

    assert database.name != "wilsy"
    assert len(
        database.name
    ) <= 63

    assert client.admin.command(
        "hello"
    )["setName"] == REPLICA_SET

    authorization_registry = _iam_registry(
        iam_collection
    )
    disownership_registry = _disownership_registry(
        disownership_collection
    )

    with pytest.raises(
        issuer.LegalEvidenceProviderObjectDisownershipOrchestrationError
    ) as missing:
        _issue(
            identity=_identity(),
            authorization_registry=authorization_registry,
            disownership_registry=disownership_registry,
            session=None,
            disownership_reference="disownership:a3:missing-session",
        )

    assert (
        missing.value.code
        == "L10A2R_C4D6D_A3_ACTIVE_TRANSACTION_REQUIRED"
    )

    with client.start_session() as inactive:
        assert inactive.in_transaction is False

        with pytest.raises(
            issuer.LegalEvidenceProviderObjectDisownershipOrchestrationError
        ) as captured:
            _issue(
                identity=_identity(),
                authorization_registry=authorization_registry,
                disownership_registry=disownership_registry,
                session=inactive,
                disownership_reference="disownership:a3:inactive-session",
            )

    assert (
        captured.value.code
        == "L10A2R_C4D6D_A3_ACTIVE_TRANSACTION_REQUIRED"
    )

    assert iam_collection.count_documents(
        {}
    ) == 0

    assert disownership_collection.count_documents(
        {}
    ) == 0


def test_real_commit_persists_correlated_iam_and_disownership_in_same_session(
    mongo_context: tuple[
        MongoClient[Any],
        Any,
        Any,
        Any,
    ],
) -> None:
    """One caller-owned transaction durably contains correlated IAM+A2 rows."""
    client, _database, raw_iam, raw_disownership = mongo_context

    tracked_iam = TrackingCollection(
        raw_iam
    )
    tracked_disownership = TrackingCollection(
        raw_disownership
    )

    authorization_registry = _iam_registry(
        tracked_iam
    )
    disownership_registry = _disownership_registry(
        tracked_disownership
    )

    with client.start_session() as session:
        session.start_transaction(
            read_concern=ReadConcern(
                "snapshot"
            )
        )

        value = _issue(
            identity=_identity(),
            authorization_registry=authorization_registry,
            disownership_registry=disownership_registry,
            session=session,
            disownership_reference="disownership:a3:positive",
        )

        assert session.in_transaction is True

        assert raw_iam.count_documents(
            {
                "tenant_id":
                    TENANT,
            },
            session=session,
        ) == 1

        assert raw_disownership.count_documents(
            {
                "tenant_id":
                    TENANT,
                "disownership_reference":
                    value.disownership_reference,
            },
            session=session,
        ) == 1

        used_sessions = [
            item
            for item in (
                tracked_iam.sessions
                + tracked_disownership.sessions
            )
            if item is not None
        ]

        assert used_sessions
        assert all(
            item is session
            for item in used_sessions
        )

        iam_row = raw_iam.find_one(
            {
                "tenant_id":
                    TENANT,
            },
            session=session,
        )

        disownership_row = raw_disownership.find_one(
            {
                "tenant_id":
                    TENANT,
                "disownership_reference":
                    value.disownership_reference,
            },
            session=session,
        )

        assert iam_row is not None
        assert disownership_row is not None

        assert (
            iam_row[
                "authorization_evidence_fingerprint"
            ]
            == value.authorization_evidence_fingerprint
        )

        assert (
            "tenant-authorization-decision:"
            + iam_row[
                "authorization_decision_id"
            ]
            == value.authorization_evidence_reference
        )

        assert (
            iam_row[
                "authorized_at"
            ]
            == value.decided_at.isoformat(
                timespec="microseconds"
            )
        )

        assert (
            iam_row[
                "operation"
            ]
            == issuer.OPERATION
        )

        assert (
            iam_row[
                "permission"
            ]
            == issuer.PERMISSION
        )

        assert (
            disownership_row[
                "authorization_evidence_reference"
            ]
            == value.authorization_evidence_reference
        )

        assert (
            disownership_row[
                "authorization_evidence_fingerprint"
            ]
            == value.authorization_evidence_fingerprint
        )

        session.commit_transaction()

    assert raw_iam.count_documents(
        {}
    ) == 1

    assert raw_disownership.count_documents(
        {}
    ) == 1


def test_real_commit_restart_exact_replay_is_one_iam_and_one_a2_row(
    mongo_context: tuple[
        MongoClient[Any],
        Any,
        Any,
        Any,
    ],
) -> None:
    """Fresh transaction replay returns the exact historic IAM+A2 evidence."""
    client, _database, iam_collection, disownership_collection = (
        mongo_context
    )

    authorization_registry = _iam_registry(
        iam_collection
    )
    disownership_registry = _disownership_registry(
        disownership_collection
    )

    with client.start_session() as first_session:
        first_session.start_transaction()

        first = _issue(
            identity=_identity(),
            authorization_registry=authorization_registry,
            disownership_registry=disownership_registry,
            session=first_session,
            disownership_reference="disownership:a3:replay",
        )

        first_session.commit_transaction()

    with client.start_session() as replay_session:
        replay_session.start_transaction()

        replayed = _issue(
            identity=_identity(),
            authorization_registry=authorization_registry,
            disownership_registry=disownership_registry,
            session=replay_session,
            disownership_reference="disownership:a3:replay",
        )

        replay_session.commit_transaction()

    assert replayed == first

    assert iam_collection.count_documents(
        {
            "tenant_id":
                TENANT,
        }
    ) == 1

    assert disownership_collection.count_documents(
        {
            "tenant_id":
                TENANT,
            "disownership_reference":
                first.disownership_reference,
        }
    ) == 1


def test_real_abort_rolls_back_both_iam_and_disownership_rows(
    mongo_context: tuple[
        MongoClient[Any],
        Any,
        Any,
        Any,
    ],
) -> None:
    """Caller abort removes both transaction-pending durable rows atomically."""
    client, _database, iam_collection, disownership_collection = (
        mongo_context
    )

    authorization_registry = _iam_registry(
        iam_collection
    )
    disownership_registry = _disownership_registry(
        disownership_collection
    )

    with client.start_session() as session:
        session.start_transaction()

        value = _issue(
            identity=_identity(),
            authorization_registry=authorization_registry,
            disownership_registry=disownership_registry,
            session=session,
            disownership_reference="disownership:a3:rollback",
        )

        assert iam_collection.count_documents(
            {
                "tenant_id":
                    TENANT,
            },
            session=session,
        ) == 1

        assert disownership_collection.count_documents(
            {
                "tenant_id":
                    TENANT,
                "disownership_reference":
                    value.disownership_reference,
            },
            session=session,
        ) == 1

        session.abort_transaction()

    assert iam_collection.count_documents(
        {}
    ) == 0

    assert disownership_collection.count_documents(
        {}
    ) == 0


def test_real_divergent_decision_material_rejects_before_second_a2_row(
    mongo_context: tuple[
        MongoClient[Any],
        Any,
        Any,
        Any,
    ],
) -> None:
    """Stable subject identity plus changed decision material fails IAM replay."""
    client, _database, iam_collection, disownership_collection = (
        mongo_context
    )

    authorization_registry = _iam_registry(
        iam_collection
    )
    disownership_registry = _disownership_registry(
        disownership_collection
    )

    reference = "disownership:a3:divergent"

    with client.start_session() as seed:
        seed.start_transaction()

        first = _issue(
            identity=_identity(),
            authorization_registry=authorization_registry,
            disownership_registry=disownership_registry,
            session=seed,
            disownership_reference=reference,
            reason_reference="reason:a3:first",
        )

        seed.commit_transaction()

    with client.start_session() as divergent:
        divergent.start_transaction()

        with pytest.raises(
            issuer.LegalEvidenceProviderObjectDisownershipOrchestrationError
        ) as captured:
            _issue(
                identity=_identity(),
                authorization_registry=authorization_registry,
                disownership_registry=disownership_registry,
                session=divergent,
                disownership_reference=reference,
                reason_reference="reason:a3:changed",
            )

        assert (
            captured.value.code
            == "L10A2R_C4D6D_A3_AUTHORIZATION_REPLAY_CONFLICT"
        )

        divergent.abort_transaction()

    assert iam_collection.count_documents(
        {
            "tenant_id":
                TENANT,
        }
    ) == 1

    assert disownership_collection.count_documents(
        {
            "tenant_id":
                TENANT,
            "disownership_reference":
                first.disownership_reference,
        }
    ) == 1


def test_real_tenant_scope_is_durable_and_noncollapsing(
    mongo_context: tuple[
        MongoClient[Any],
        Any,
        Any,
        Any,
    ],
) -> None:
    """Same provider-object reference under another tenant remains separate."""
    client, _database, iam_collection, disownership_collection = (
        mongo_context
    )

    authorization_registry = _iam_registry(
        iam_collection
    )
    disownership_registry = _disownership_registry(
        disownership_collection
    )

    reference = "disownership:a3:tenant-opacity"

    with client.start_session() as first_session:
        first_session.start_transaction()

        first = _issue(
            identity=_identity(
                TENANT
            ),
            authorization_registry=authorization_registry,
            disownership_registry=disownership_registry,
            session=first_session,
            disownership_reference=reference,
        )

        first_session.commit_transaction()

    with client.start_session() as second_session:
        second_session.start_transaction()

        second = _issue(
            identity=_identity(
                OTHER_TENANT
            ),
            authorization_registry=authorization_registry,
            disownership_registry=disownership_registry,
            session=second_session,
            disownership_reference=reference,
        )

        second_session.commit_transaction()

    assert first.tenant_id == TENANT
    assert second.tenant_id == OTHER_TENANT
    assert first != second

    assert iam_collection.count_documents(
        {}
    ) == 2

    assert disownership_collection.count_documents(
        {}
    ) == 2

    assert disownership_collection.count_documents(
        {
            "tenant_id":
                TENANT,
            "disownership_reference":
                reference,
        }
    ) == 1

    assert disownership_collection.count_documents(
        {
            "tenant_id":
                OTHER_TENANT,
            "disownership_reference":
                reference,
        }
    ) == 1


def test_real_certificate_has_no_downstream_authority() -> None:
    """Runtime certificate does not widen A3 into later authority gates."""
    source = open(
        issuer.__file__,
        encoding="utf-8",
    ).read()

    forbidden = (
        "orphan_proven",
        "retention_satisfied",
        "legal_hold_release",
        "cleanup_eligible",
        "delete_authorization",
        "provider_delete",
        "payment_executed",
        "settled",
    )

    for token in forbidden:
        assert token not in source


# ARTIFACT: test_legal_evidence_provider_object_disownership_orchestrator_real_mongo.py
# VERSION: v1.0.0-L10A2R-C4D6D-A3-REAL-MONGO-CERT
# AUTHORITY BOUNDARY: disposable real-Mongo A3 durability certificate only
# TENANT POSTURE: exact tenant-scoped IAM/A2 evidence in UUID-isolated database
# TRANSACTION POSTURE: caller owns every session, transaction, commit and abort
# REPLAY POSTURE: commit/restart exact replay only; divergent intent fails closed
# ORPHAN POSTURE: no orphan proof
# PRESERVATION POSTURE: no retention satisfaction or legal-hold release authority
# DELETION POSTURE: no cleanup eligibility, delete authorization or provider mutation
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively
# END OF WILSY OS SOVEREIGN ARTIFACT
