"""Real-Mongo certificate for authorized provider-object orphan-proof issuance.

TITLE: WILSY OS Authorized Provider-Object Orphan-Proof Real-Mongo Certificate
VERSION: v1.0.0-L10A2R-C4D6D-B3-REAL-MONGO-CERT
AUTHORITY: WILSY OS Core Governance / Python EOS Legal Operations
EPITOME: Prove B3 durable IAM evidence and B2 orphan-proof persistence share one
         caller-owned Mongo transaction with commit, rollback and exact replay.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tests/integration/test_legal_evidence_provider_object_orphan_proof_orchestrator_real_mongo.py
COLLABORATION / OWNERSHIP: C4D6D-B3 owns bounded issuance composition; IAM owns
                            durable authorization evidence; B1 owns immutable
                            orphan-proof truth; B2 owns exact persistence/replay.
CERTIFICATION / UPDATE DATE: 2026-10-01
CHANGELOG: 2026-10-01 v1.0.0-L10A2R-C4D6D-B3-REAL-MONGO-CERT establishes
           disposable replica-set certification for topology, active transaction
           enforcement, same-session IAM+B2 writes, commit/restart replay,
           rollback atomicity, divergent proof-material rejection and tenant
           isolation without later disposition authority.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2; ISO 27001.
SECURITY / PRIVACY POSTURE: UUID-isolated synthetic database only; credentials,
                             tokens and customer PII are never printed.
TENANT BOUNDARY: Every durable IAM and orphan-proof identity remains exact tenant
                 scoped. The disposable database is never named ``wilsy``.
AUTHORITY BOUNDARY: Runtime durability certificate only; no retention
                    satisfaction, hold release, cleanup/deletion authorization
                    or provider mutation.
FINANCIAL AUTHORITY BOUNDARY: Kennel EOS exclusively owns financial execution
                              and settlement truth.
TRANSACTION BOUNDARY: Tests own sessions, transactions, commits and aborts;
                      production orchestration owns none of them.
FAIL-CLOSED DECLARATION: Topology drift, inactive transaction, divergent IAM
                         replay, persistence mismatch or rollback leakage fails.
"""

from __future__ import annotations

import hashlib
import json
import os
import uuid
from datetime import datetime, timedelta, timezone
from types import SimpleNamespace
from typing import Any, Iterator, cast

import pytest
from pymongo import MongoClient, version as pymongo_version
from pymongo.errors import PyMongoError
from pymongo.read_concern import ReadConcern
from pymongo.write_concern import WriteConcern

from tools.eos.auth import (
    tenant_authorization_decision_evidence_registry as iam_module,
)
from tools.eos.auth.identity import SovereignIdentity
from tools.eos.auth.principal_status import PrincipalStatus
from tools.eos.auth.role_assignment import RoleAssignmentStatus
from tools.eos.auth.tenant_authorization import (
    TenantAuthorizationDecision,
    TenantAuthorizationReason,
)
from tools.eos.auth.tenant_authorization_decision_evidence_registry import (
    TenantAuthorizationDecisionEvidenceRegistry,
)
from tools.eos.auth.tenant_membership import TenantMembershipStatus
from tools.eos.legal_operations.domain.legal_evidence_provider_object_disownership import (
    LegalEvidenceProviderObjectDisownership,
)
from tools.eos.legal_operations.orchestration import (
    legal_evidence_provider_object_orphan_proof_orchestrator as issuer,
)
from tools.eos.legal_operations.registry.legal_evidence_provider_object_orphan_proof_registry import (
    COLLECTION as ORPHAN_COLLECTION,
    LegalEvidenceProviderObjectOrphanProofRegistry,
)
from tools.eos.legal_operations.service.legal_evidence_provider_cleanup_discovery_port import (
    LegalEvidenceCompletedObjectIntentMetadataState,
    LegalEvidenceCompletedObjectObservation,
    LegalEvidenceProviderDiscoveryScope,
)
from tools.eos.legal_operations.service.legal_evidence_provider_coverage_enumeration_port import (
    LegalEvidenceProviderEnumerationKind,
    LegalEvidenceProviderEnumerationPage,
)
from tools.eos.legal_operations.service.legal_evidence_provider_coverage_verification_service import (
    LegalEvidenceProviderCoverageVerification,
    LegalEvidenceProviderCoverageVerificationService,
)


MONGO_URI = os.getenv(
    "TEST_VENDOR_MONGO_URI",
    "mongodb://127.0.0.1:27027/?replicaSet=wilsyVendorCertRS",
)

REPLICA_SET = "wilsyVendorCertRS"
MONGO_VERSION = "7.0.37"

IAM_COLLECTION = "tenant_authorization_decision_evidence"

TENANT = "tenant-c4d6d-b3"
OTHER_TENANT = "tenant-c4d6d-b3-other"
PRINCIPAL = "principal-c4d6d-b3"

AT = datetime(
    2026,
    10,
    1,
    12,
    0,
    tzinfo=timezone.utc,
)

SHA_A = "a" * 128
SHA_B = "b" * 128


class TrackingCollection:
    """Record every supplied Mongo session while delegating to a real collection."""

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
    """Expose one active principal to the canonical IAM evidence composer."""

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
    """Expose active tenant membership and a deterministic revision."""

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
    """Expose the certified LEGAL_PARTNER assignment."""

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
    """Retain the canonical authorizer repository boundary."""

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
    """Freeze the already-certified B3 IAM authorization outcome."""
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
        username="c4d6d-b3-operator",
        email="c4d6d-b3@example.test",
        auth_method="TEST",
        status=PrincipalStatus.ACTIVE,
    )


def _scope(
    tenant_id: str,
) -> LegalEvidenceProviderDiscoveryScope:
    return LegalEvidenceProviderDiscoveryScope(
        tenant_id=tenant_id,
        tenant_scope_fingerprint=SHA_A,
    )


def _observation(
    tenant_id: str,
) -> LegalEvidenceCompletedObjectObservation:
    return LegalEvidenceCompletedObjectObservation(
        tenant_id=tenant_id,
        provider_name="aws_s3",
        storage_reference="legal-evidence/b3-real/object",
        object_version_reference="version-b3-real",
        provider_integrity_reference='"etag-b3-real"',
        content_length=41,
        last_modified_at=AT,
        observed_at=AT,
        write_intent_metadata_state=(
            LegalEvidenceCompletedObjectIntentMetadataState.ABSENT
        ),
        write_intent_fingerprint=None,
    )


class _Provider:
    """Deterministic exhaustive provider source for valid B1 prerequisites."""

    def __init__(
        self,
        *,
        scope: LegalEvidenceProviderDiscoveryScope,
        observation: LegalEvidenceCompletedObjectObservation,
    ) -> None:
        self.scope = scope
        self.observation = observation

    def list_incomplete_write_session_page(
        self,
        scope: LegalEvidenceProviderDiscoveryScope,
        *,
        observed_at: datetime,
        page_reference: str | None,
    ) -> LegalEvidenceProviderEnumerationPage:
        assert scope == self.scope
        assert observed_at == AT
        assert page_reference is None

        return LegalEvidenceProviderEnumerationPage(
            tenant_id=scope.tenant_id,
            tenant_scope_fingerprint=scope.tenant_scope_fingerprint,
            provider_name=self.observation.provider_name,
            enumeration_kind=(
                LegalEvidenceProviderEnumerationKind
                .INCOMPLETE_WRITE_SESSIONS
            ),
            observed_at=AT,
            observations=(),
            next_page_reference=None,
        )

    def list_completed_object_version_page(
        self,
        scope: LegalEvidenceProviderDiscoveryScope,
        *,
        observed_at: datetime,
        page_reference: str | None,
    ) -> LegalEvidenceProviderEnumerationPage:
        assert scope == self.scope
        assert observed_at == AT
        assert page_reference is None

        return LegalEvidenceProviderEnumerationPage(
            tenant_id=scope.tenant_id,
            tenant_scope_fingerprint=scope.tenant_scope_fingerprint,
            provider_name=self.observation.provider_name,
            enumeration_kind=(
                LegalEvidenceProviderEnumerationKind
                .COMPLETED_OBJECT_VERSIONS
            ),
            observed_at=AT,
            observations=(
                self.observation,
            ),
            next_page_reference=None,
        )


def _prerequisites(
    tenant_id: str,
) -> tuple[
    LegalEvidenceProviderCoverageVerificationService,
    LegalEvidenceProviderCoverageVerification,
    LegalEvidenceCompletedObjectObservation,
    LegalEvidenceProviderObjectDisownership,
]:
    scope = _scope(
        tenant_id
    )
    observation = _observation(
        tenant_id
    )

    service = LegalEvidenceProviderCoverageVerificationService(
        provider=_Provider(
            scope=scope,
            observation=observation,
        )
    )

    verification = service.verify_coverage(
        scope=scope,
        provider_name="aws_s3",
        observed_at=AT,
    )

    disownership = LegalEvidenceProviderObjectDisownership(
        tenant_id=tenant_id,
        provider_name="aws_s3",
        storage_reference=observation.storage_reference,
        object_version_reference=observation.object_version_reference,
        disownership_reference=(
            "disownership:"
            + tenant_id
            + ":b3-real"
        ),
        reason_reference="reason:b3-real",
        source_evidence_reference="source:b3-real",
        source_evidence_fingerprint=SHA_A,
        authorization_evidence_reference="authorization:b3-real",
        authorization_evidence_fingerprint=SHA_B,
        decided_at=AT - timedelta(
            minutes=5
        ),
    )

    return (
        service,
        verification,
        observation,
        disownership,
    )


def _iam_registry(
    collection: Any,
) -> TenantAuthorizationDecisionEvidenceRegistry:
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


def _orphan_registry(
    collection: Any,
) -> LegalEvidenceProviderObjectOrphanProofRegistry:
    return LegalEvidenceProviderObjectOrphanProofRegistry(
        cast(
            Any,
            collection,
        )
    )


def _issue(
    *,
    identity: SovereignIdentity,
    authorization_registry: TenantAuthorizationDecisionEvidenceRegistry,
    orphan_registry: LegalEvidenceProviderObjectOrphanProofRegistry,
    session: Any,
    orphan_proof_reference: str,
    proved_at: datetime = AT + timedelta(
        minutes=1
    ),
):
    tenant_id = identity.tenant_id

    (
        service,
        verification,
        observation,
        disownership,
    ) = _prerequisites(
        tenant_id
    )

    return issuer.issue_legal_evidence_provider_object_orphan_proof(
        identity=identity,
        coverage_service=service,
        verification=verification,
        observation=observation,
        disownership=disownership,
        orphan_proof_reference=orphan_proof_reference,
        proved_at=proved_at,
        authorization_evidence_registry=authorization_registry,
        orphan_proof_registry=orphan_registry,
        session=session,
    )


def _start(
    session: Any,
) -> None:
    session.start_transaction(
        read_concern=ReadConcern(
            "snapshot"
        ),
        write_concern=WriteConcern(
            "majority",
            j=True,
        ),
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
            pytest.fail(
                "real Mongo unavailable for B3 certificate: "
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
        assert pymongo_version

        with client.start_session() as probe:
            _start(
                probe
            )
            assert probe.in_transaction is True
            probe.abort_transaction()

        name = (
            "wilsy_c4d6d_b3_"
            + uuid.uuid4().hex
        )

        assert len(
            name
        ) <= 63
        assert name != "wilsy"

        database = client[
            name
        ]

        iam_collection = database.get_collection(
            IAM_COLLECTION,
            write_concern=WriteConcern(
                "majority",
                j=True,
            ),
            read_concern=ReadConcern(
                "majority"
            ),
        )

        orphan_collection = database.get_collection(
            ORPHAN_COLLECTION,
            write_concern=WriteConcern(
                "majority",
                j=True,
            ),
            read_concern=ReadConcern(
                "majority"
            ),
        )

        _iam_registry(
            iam_collection
        ).ensure_indexes()

        _orphan_registry(
            orphan_collection
        ).ensure_indexes()

        yield (
            client,
            database,
            iam_collection,
            orphan_collection,
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
    client, database, iam_collection, orphan_collection = mongo_context

    assert database.name.startswith(
        "wilsy_c4d6d_b3_"
    )
    assert database.name != "wilsy"

    hello = client.admin.command(
        "hello"
    )

    assert hello["setName"] == REPLICA_SET
    assert hello["isWritablePrimary"] is True

    authorization_registry = _iam_registry(
        iam_collection
    )
    orphan_registry = _orphan_registry(
        orphan_collection
    )

    with pytest.raises(
        issuer.LegalEvidenceProviderObjectOrphanProofOrchestrationError
    ) as missing:
        _issue(
            identity=_identity(),
            authorization_registry=authorization_registry,
            orphan_registry=orphan_registry,
            session=None,
            orphan_proof_reference="orphan-proof:b3:missing",
        )

    assert (
        missing.value.code
        == "L10A2R_C4D6D_B3_ACTIVE_TRANSACTION_REQUIRED"
    )

    with client.start_session() as inactive:
        assert inactive.in_transaction is False

        with pytest.raises(
            issuer.LegalEvidenceProviderObjectOrphanProofOrchestrationError
        ) as captured:
            _issue(
                identity=_identity(),
                authorization_registry=authorization_registry,
                orphan_registry=orphan_registry,
                session=inactive,
                orphan_proof_reference="orphan-proof:b3:inactive",
            )

    assert (
        captured.value.code
        == "L10A2R_C4D6D_B3_ACTIVE_TRANSACTION_REQUIRED"
    )

    assert iam_collection.count_documents(
        {}
    ) == 0

    assert orphan_collection.count_documents(
        {}
    ) == 0


def test_real_commit_persists_correlated_iam_and_b2_in_same_session(
    mongo_context: tuple[
        MongoClient[Any],
        Any,
        Any,
        Any,
    ],
) -> None:
    client, _database, raw_iam, raw_orphan = mongo_context

    tracked_iam = TrackingCollection(
        raw_iam
    )
    tracked_orphan = TrackingCollection(
        raw_orphan
    )

    authorization_registry = _iam_registry(
        tracked_iam
    )
    orphan_registry = _orphan_registry(
        tracked_orphan
    )

    session = None

    with client.start_session() as session:
        _start(
            session
        )

        value = _issue(
            identity=_identity(),
            authorization_registry=authorization_registry,
            orphan_registry=orphan_registry,
            session=session,
            orphan_proof_reference="orphan-proof:b3:positive",
        )

        assert session.in_transaction is True

        assert raw_iam.count_documents(
            {
                "tenant_id":
                    TENANT,
            },
            session=session,
        ) == 1

        assert raw_orphan.count_documents(
            {
                "tenant_id":
                    TENANT,
                "orphan_proof_reference":
                    value.orphan_proof_reference,
            },
            session=session,
        ) == 1

        used_sessions = [
            item
            for item in (
                tracked_iam.sessions
                + tracked_orphan.sessions
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

        orphan_row = raw_orphan.find_one(
            {
                "tenant_id":
                    TENANT,
                "orphan_proof_reference":
                    value.orphan_proof_reference,
            },
            session=session,
        )

        assert iam_row is not None
        assert orphan_row is not None

        expected_subject_fingerprint = hashlib.sha3_512(
            json.dumps(
                {
                    "tenant_id":
                        TENANT,
                    "actor_principal_id":
                        PRINCIPAL,
                    "provider_name":
                        value.provider_name,
                    "storage_reference":
                        value.storage_reference,
                    "object_version_reference":
                        value.object_version_reference,
                    "orphan_proof_reference":
                        value.orphan_proof_reference,
                    "orphan_proof_fingerprint":
                        value.fingerprint,
                    "coverage_verification_fingerprint":
                        value.coverage_verification_fingerprint,
                    "completed_observation_membership_fingerprint":
                        value.completed_observation_membership_fingerprint,
                    "disownership_reference":
                        value.disownership_reference,
                    "disownership_fingerprint":
                        value.disownership_fingerprint,
                    "provider_observed_at":
                        value.provider_observed_at.isoformat(
                            timespec="microseconds"
                        ),
                    "disownership_decided_at":
                        value.disownership_decided_at.isoformat(
                            timespec="microseconds"
                        ),
                    "proved_at":
                        value.proved_at.isoformat(
                            timespec="microseconds"
                        ),
                },
                sort_keys=True,
                separators=(",", ":"),
                ensure_ascii=True,
            ).encode(
                "utf-8"
            )
        ).hexdigest()

        assert (
            iam_row[
                "subject_evidence_fingerprint"
            ]
            == expected_subject_fingerprint
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
            iam_row[
                "business_role"
            ]
            == issuer.BUSINESS_ROLE
        )

        assert (
            iam_row[
                "authorization_role"
            ]
            == issuer.AUTHORIZATION_ROLE
        )

        assert (
            iam_row[
                "idempotency_key"
            ]
            == iam_row[
                "subject_reference"
            ]
        )

        assert (
            orphan_row[
                "fingerprint"
            ]
            == value.fingerprint
        )

        session.commit_transaction()

    assert raw_iam.count_documents(
        {}
    ) == 1

    assert raw_orphan.count_documents(
        {}
    ) == 1


def test_real_commit_restart_exact_replay_is_one_iam_and_one_b2_row(
    mongo_context: tuple[
        MongoClient[Any],
        Any,
        Any,
        Any,
    ],
) -> None:
    client, _database, iam_collection, orphan_collection = mongo_context

    authorization_registry = _iam_registry(
        iam_collection
    )
    orphan_registry = _orphan_registry(
        orphan_collection
    )

    reference = "orphan-proof:b3:replay"

    with client.start_session() as first_session:
        _start(
            first_session
        )

        first = _issue(
            identity=_identity(),
            authorization_registry=authorization_registry,
            orphan_registry=orphan_registry,
            session=first_session,
            orphan_proof_reference=reference,
        )

        first_session.commit_transaction()

    with client.start_session() as replay_session:
        _start(
            replay_session
        )

        replayed = _issue(
            identity=_identity(),
            authorization_registry=authorization_registry,
            orphan_registry=orphan_registry,
            session=replay_session,
            orphan_proof_reference=reference,
        )

        replay_session.commit_transaction()

    assert replayed == first

    assert iam_collection.count_documents(
        {
            "tenant_id":
                TENANT,
        }
    ) == 1

    assert orphan_collection.count_documents(
        {
            "tenant_id":
                TENANT,
            "orphan_proof_reference":
                reference,
        }
    ) == 1


def test_real_abort_rolls_back_both_iam_and_b2_rows(
    mongo_context: tuple[
        MongoClient[Any],
        Any,
        Any,
        Any,
    ],
) -> None:
    client, _database, iam_collection, orphan_collection = mongo_context

    authorization_registry = _iam_registry(
        iam_collection
    )
    orphan_registry = _orphan_registry(
        orphan_collection
    )

    with client.start_session() as session:
        _start(
            session
        )

        value = _issue(
            identity=_identity(),
            authorization_registry=authorization_registry,
            orphan_registry=orphan_registry,
            session=session,
            orphan_proof_reference="orphan-proof:b3:rollback",
        )

        assert iam_collection.count_documents(
            {},
            session=session,
        ) == 1

        assert orphan_collection.count_documents(
            {
                "orphan_proof_reference":
                    value.orphan_proof_reference,
            },
            session=session,
        ) == 1

        session.abort_transaction()

    assert iam_collection.count_documents(
        {}
    ) == 0

    assert orphan_collection.count_documents(
        {}
    ) == 0


def test_real_divergent_proof_material_rejects_before_second_b2_row(
    mongo_context: tuple[
        MongoClient[Any],
        Any,
        Any,
        Any,
    ],
) -> None:
    client, _database, iam_collection, orphan_collection = mongo_context

    authorization_registry = _iam_registry(
        iam_collection
    )
    orphan_registry = _orphan_registry(
        orphan_collection
    )

    reference = "orphan-proof:b3:divergent"

    with client.start_session() as seed:
        _start(
            seed
        )

        first = _issue(
            identity=_identity(),
            authorization_registry=authorization_registry,
            orphan_registry=orphan_registry,
            session=seed,
            orphan_proof_reference=reference,
            proved_at=AT + timedelta(
                minutes=1
            ),
        )

        seed.commit_transaction()

    with client.start_session() as divergent:
        _start(
            divergent
        )

        with pytest.raises(
            issuer.LegalEvidenceProviderObjectOrphanProofOrchestrationError
        ) as captured:
            _issue(
                identity=_identity(),
                authorization_registry=authorization_registry,
                orphan_registry=orphan_registry,
                session=divergent,
                orphan_proof_reference=reference,
                proved_at=AT + timedelta(
                    minutes=2
                ),
            )

        assert (
            captured.value.code
            == "L10A2R_C4D6D_B3_AUTHORIZATION_REPLAY_CONFLICT"
        )

        divergent.abort_transaction()

    assert iam_collection.count_documents(
        {
            "tenant_id":
                TENANT,
        }
    ) == 1

    assert orphan_collection.count_documents(
        {
            "tenant_id":
                TENANT,
            "orphan_proof_reference":
                first.orphan_proof_reference,
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
    client, _database, iam_collection, orphan_collection = mongo_context

    authorization_registry = _iam_registry(
        iam_collection
    )
    orphan_registry = _orphan_registry(
        orphan_collection
    )

    reference = "orphan-proof:b3:tenant-isolation"

    with client.start_session() as first_session:
        _start(
            first_session
        )

        first = _issue(
            identity=_identity(
                TENANT
            ),
            authorization_registry=authorization_registry,
            orphan_registry=orphan_registry,
            session=first_session,
            orphan_proof_reference=reference,
        )

        first_session.commit_transaction()

    with client.start_session() as second_session:
        _start(
            second_session
        )

        second = _issue(
            identity=_identity(
                OTHER_TENANT
            ),
            authorization_registry=authorization_registry,
            orphan_registry=orphan_registry,
            session=second_session,
            orphan_proof_reference=reference,
        )

        second_session.commit_transaction()

    assert first.tenant_id == TENANT
    assert second.tenant_id == OTHER_TENANT
    assert first != second

    assert iam_collection.count_documents(
        {}
    ) == 2

    assert orphan_collection.count_documents(
        {}
    ) == 2

    assert orphan_collection.count_documents(
        {
            "tenant_id":
                TENANT,
            "orphan_proof_reference":
                reference,
        }
    ) == 1

    assert orphan_collection.count_documents(
        {
            "tenant_id":
                OTHER_TENANT,
            "orphan_proof_reference":
                reference,
        }
    ) == 1


def test_real_certificate_grants_no_later_or_financial_authority() -> None:
    forbidden = {
        "retention_satisfied",
        "retention_expired",
        "legal_hold_released",
        "hold_released",
        "cleanup_authorized",
        "delete_authorized",
        "deletion_authorized",
        "provider_delete_authorized",
        "delete_object",
        "delete_objects",
        "billing_authorized",
        "payment_authorized",
        "settlement_authorized",
    }

    public_surface = {
        name
        for name in dir(
            issuer
        )
        if not name.startswith("_")
    }

    assert forbidden.isdisjoint(
        public_surface
    )


# ARTIFACT: test_legal_evidence_provider_object_orphan_proof_orchestrator_real_mongo.py
# VERSION: v1.0.0-L10A2R-C4D6D-B3-REAL-MONGO-CERT
# AUTHORITY BOUNDARY: disposable real-Mongo B3 durability certificate only
# TENANT POSTURE: exact tenant-scoped IAM/B2 evidence in UUID-isolated database
# TRANSACTION POSTURE: caller owns every session, transaction, commit and abort
# REPLAY POSTURE: commit/restart exact replay only; divergent proof fails closed
# PRESERVATION POSTURE: no retention satisfaction or legal-hold release authority
# DELETION POSTURE: no cleanup eligibility, delete authorization or provider mutation
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively
# END OF WILSY OS SOVEREIGN ARTIFACT
