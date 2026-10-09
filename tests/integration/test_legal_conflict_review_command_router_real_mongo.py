"""Real-Mongo HTTP certificate for L8-8K authorized conflict review.

VERSION: v1.0.0-L8-8K-CONFLICT-REVIEW-COMMAND-API-REAL-MONGO-CERT
AUTHORITY: Wilsy OS Core Governance
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tests/integration/test_legal_conflict_review_command_router_real_mongo.py
EPITOME: Prove the complete HTTP -> current IAM -> durable authorization evidence
         -> persisted screening -> human review -> immutable review registry chain
         against one disposable writable Mongo replica set.
TRANSACTION BOUNDARY: Production command API owns each request transaction; the
                      harness owns only fixture-seeding transactions.
AUTHORITY BOUNDARY: Host-backed conflict-review command evidence only.
FINANCIAL AUTHORITY BOUNDARY: Kennel EOS exclusively owns execution.
"""
from __future__ import annotations

from datetime import datetime, timezone
import os
from typing import Any, Iterator
from uuid import uuid4

from fastapi import FastAPI
from fastapi.testclient import TestClient

from tools.eos.api.errors import register_error_handlers
import pytest
from pymongo import MongoClient
from pymongo.errors import PyMongoError
from pymongo.read_concern import ReadConcern
from pymongo.write_concern import WriteConcern

import tools.eos.api.legal_operations_command_router as command_api
import tools.eos.api.tenant_authorization_http as authorization_http
from tools.eos.auth import authentication, tenant_access
from tools.eos.auth.identity import SovereignIdentity
from tools.eos.auth.principal_authority import PrincipalAuthority
from tools.eos.auth.principal_authority_repository import (
    COLLECTION as PRINCIPAL_COLLECTION,
    PrincipalAuthorityRepository,
)
from tools.eos.auth.principal_status import PrincipalStatus
from tools.eos.auth.role_assignment import (
    RoleAssignmentAuthority,
    RoleAssignmentStatus,
)
from tools.eos.auth.role_assignment_repository import (
    COLLECTION as ROLE_COLLECTION,
    RoleAssignmentNotFoundError,
    RoleAssignmentRepository,
    RoleAssignmentRepositoryError,
)
from tools.eos.auth.tenant_authority_policy import TENANT_ROLES
from tools.eos.auth.tenant_authorization_decision_evidence_registry import (
    COLLECTION as AUTH_EVIDENCE_COLLECTION,
    TenantAuthorizationDecisionEvidenceRegistry,
)
from tools.eos.auth.tenant_business_role import (
    TenantBusinessRoleAuthority,
    TenantBusinessRoleStatus,
)
from tools.eos.auth.tenant_business_role_repository import (
    COLLECTION as BUSINESS_ROLE_COLLECTION,
    TenantBusinessRoleNotFoundError,
    TenantBusinessRoleRepository,
    TenantBusinessRoleRepositoryError,
)
from tools.eos.auth.tenant_membership import (
    TenantMembershipAuthority,
    TenantMembershipStatus,
)
from tools.eos.auth.tenant_membership_repository import (
    COLLECTION as MEMBERSHIP_COLLECTION,
    TenantMembershipRepository,
)
from tools.eos.legal_operations.domain.legal_conflict_review import (
    LegalConflictReviewOutcome,
)
from tools.eos.legal_operations.orchestration.legal_conflict_review_orchestrator import (
    issue_legal_conflict_review,
)
from tools.eos.legal_operations.domain.legal_conflict_screening import (
    LegalConflictMatchKind,
    LegalConflictMatchSignal,
    LegalConflictScreeningResult,
    LegalConflictScreeningStatus,
)
from tools.eos.legal_operations.registry.legal_conflict_review_registry import (
    COLLECTION as REVIEW_COLLECTION,
    LegalConflictReviewRegistry,
)
from tools.eos.legal_operations.registry.legal_conflict_screening_registry import (
    COLLECTION as SCREENING_COLLECTION,
    LegalConflictScreeningRegistry,
)


DEFAULT_URI = "mongodb://127.0.0.1:27027/?replicaSet=wilsyVendorCertRS"
EXPECTED_REPLICA_SET = "wilsyVendorCertRS"
NOW = datetime(2026, 9, 25, 4, 0, tzinfo=timezone.utc)
FP_A = "a" * 128
FP_B = "b" * 128
FP_C = "c" * 128


class _PrincipalReader:
    def __init__(self, collection: Any) -> None:
        self._collection = collection

    def resolve(self, principal_id: str, *, session: Any = None) -> Any:
        return PrincipalAuthorityRepository.get(
            principal_id,
            self._collection,
            session=session,
        )


class _MembershipReader:
    def __init__(self, collection: Any) -> None:
        self._collection = collection

    def resolve(
        self,
        principal_id: str,
        tenant_id: str,
        *,
        session: Any = None,
    ) -> Any:
        return TenantMembershipRepository.resolve(
            principal_id,
            tenant_id,
            self._collection,
            session=session,
        )


class _RoleReader:
    """Resolve authorization and business roles from their canonical stores."""

    def __init__(self, authorization_collection: Any, business_collection: Any) -> None:
        self._authorization_collection = authorization_collection
        self._business_collection = business_collection

    def resolve(
        self,
        principal_id: str,
        tenant_id: str,
        role_id: str,
        *,
        session: Any = None,
    ) -> Any:
        if role_id in TENANT_ROLES:
            try:
                value = TenantBusinessRoleRepository.resolve(
                    principal_id,
                    tenant_id,
                    self._business_collection,
                    session=session,
                )
            except TenantBusinessRoleNotFoundError as error:
                raise RoleAssignmentNotFoundError(
                    "TENANT_BUSINESS_ROLE_NOT_FOUND"
                ) from error
            except TenantBusinessRoleRepositoryError as error:
                raise RoleAssignmentRepositoryError(
                    "TENANT_BUSINESS_ROLE_AUTHORITY_UNAVAILABLE"
                ) from error
            if value.business_role != role_id:
                raise RoleAssignmentNotFoundError(
                    "TENANT_BUSINESS_ROLE_NOT_FOUND"
                )
            return value

        return RoleAssignmentRepository.resolve(
            principal_id,
            tenant_id,
            role_id,
            self._authorization_collection,
            session=session,
        )


@pytest.fixture
def mongo_context() -> Iterator[dict[str, Any]]:
    client: MongoClient[Any] = MongoClient(
        os.getenv("TEST_VENDOR_MONGO_URI", DEFAULT_URI),
        serverSelectionTimeoutMS=3000,
        connectTimeoutMS=3000,
        retryWrites=True,
        tz_aware=True,
    )
    database: Any = None
    try:
        try:
            hello = client.admin.command("hello")
        except PyMongoError as error:
            pytest.skip(
                f"host Mongo unavailable during hello: {type(error).__name__}: {error}"
            )
        if hello.get("setName") != EXPECTED_REPLICA_SET:
            pytest.skip(f"wrong replica set: {hello.get('setName')!r}")
        if hello.get("isWritablePrimary", hello.get("ismaster")) is not True:
            pytest.skip("replica set has no writable primary")
        if hello.get("logicalSessionTimeoutMinutes") is None:
            pytest.skip("replica set has no logical-session capability")

        database = client.get_database(
            f"wilsy_l8_8k_conflict_review_{uuid4().hex}",
            read_concern=ReadConcern("majority"),
            write_concern=WriteConcern(w="majority", j=True),
        )
        collections = {
            "principal": database.get_collection(PRINCIPAL_COLLECTION),
            "membership": database.get_collection(MEMBERSHIP_COLLECTION),
            "roles": database.get_collection(ROLE_COLLECTION),
            "business": database.get_collection(BUSINESS_ROLE_COLLECTION),
            "authorization": database.get_collection(AUTH_EVIDENCE_COLLECTION),
            "screening": database.get_collection(SCREENING_COLLECTION),
            "review": database.get_collection(REVIEW_COLLECTION),
        }

        PrincipalAuthorityRepository.ensure_indexes(collections["principal"])
        TenantMembershipRepository.ensure_indexes(collections["membership"])
        RoleAssignmentRepository.ensure_indexes(collections["roles"])
        TenantBusinessRoleRepository.ensure_indexes(collections["business"])
        TenantAuthorizationDecisionEvidenceRegistry(
            collections["authorization"],
            principal_repository=object(),
        ).ensure_indexes()
        LegalConflictScreeningRegistry.ensure_indexes(collections["screening"])
        LegalConflictReviewRegistry.ensure_indexes(collections["review"])

        yield {
            "client": client,
            "database": database,
            "collections": collections,
        }
    finally:
        if database is not None:
            client.drop_database(database.name)
        client.close()


def _screening(tenant: str, suffix: str) -> LegalConflictScreeningResult:
    return LegalConflictScreeningResult(
        tenant_id=tenant,
        screening_id=f"screening-{suffix}",
        source_party_id=f"party-source-{suffix}",
        source_case_matter_id=f"matter-source-{suffix}",
        source_party_fingerprint=FP_A,
        subject_identity_fingerprint=FP_B,
        screened_at=NOW,
        status=LegalConflictScreeningStatus.REVIEW_REQUIRED,
        matches=(
            LegalConflictMatchSignal(
                tenant_id=tenant,
                subject_identity_fingerprint=FP_B,
                source_party_id=f"party-source-{suffix}",
                source_case_matter_id=f"matter-source-{suffix}",
                source_party_fingerprint=FP_A,
                matched_party_id=f"party-match-{suffix}",
                matched_case_matter_id=f"matter-match-{suffix}",
                matched_party_fingerprint=FP_C,
                match_kind=(
                    LegalConflictMatchKind.CROSS_MATTER_EXACT_SUBJECT_MATCH
                ),
            ),
        ),
        source_evidence_reference=f"screening-source:{suffix}",
        source_evidence_fingerprint=FP_C,
    )


def _seed(
    context: dict[str, Any],
    *,
    business_role: str = "tenant_legal_partner",
    grant_role: str = "LEGAL_PARTNER",
    screening: bool = True,
) -> tuple[str, str, LegalConflictScreeningResult]:
    collections = context["collections"]
    client: MongoClient[Any] = context["client"]
    suffix = uuid4().hex
    tenant = f"tenant-review-{suffix}"
    principal = f"principal-review-{suffix}"
    screening_value = _screening(tenant, suffix)

    with client.start_session() as session:
        session.start_transaction(
            read_concern=ReadConcern("snapshot"),
            write_concern=WriteConcern(w="majority", j=True),
        )
        PrincipalAuthorityRepository.create(
            PrincipalAuthority(principal, PrincipalStatus.ACTIVE, 0),
            collections["principal"],
            session=session,
        )
        TenantMembershipRepository.insert(
            TenantMembershipAuthority(
                principal,
                tenant,
                TenantMembershipStatus.ACTIVE,
                0,
            ),
            collections["membership"],
            session=session,
        )
        TenantBusinessRoleRepository.insert(
            TenantBusinessRoleAuthority(
                principal,
                tenant,
                business_role,
                TenantBusinessRoleStatus.ACTIVE,
                0,
                NOW,
                None,
            ),
            collections["business"],
            session=session,
        )
        RoleAssignmentRepository.insert(
            RoleAssignmentAuthority(
                principal,
                tenant,
                grant_role,
                RoleAssignmentStatus.ACTIVE,
                0,
            ),
            collections["roles"],
            session=session,
        )
        if screening:
            LegalConflictScreeningRegistry.persist_screening(
                screening_value,
                collections["screening"],
                session=session,
            )
        session.commit_transaction()

    return tenant, principal, screening_value


def _identity(principal: str, tenant: str) -> SovereignIdentity:
    return SovereignIdentity(
        identity_id=principal,
        tenant_id=tenant,
        username="reviewer",
        email="reviewer@example.test",
        auth_method="TEST",
        status=PrincipalStatus.ACTIVE,
    )


def _client(
    context: dict[str, Any],
    monkeypatch: pytest.MonkeyPatch,
    *,
    tenant: str,
    principal: str,
) -> TestClient:
    collections = context["collections"]
    principal_reader = _PrincipalReader(collections["principal"])
    membership_reader = _MembershipReader(collections["membership"])
    role_reader = _RoleReader(collections["roles"], collections["business"])

    app = FastAPI()
    register_error_handlers(app)
    app.dependency_overrides[authorization_http.get_current_identity] = (
        lambda: _identity(principal, tenant)
    )
    app.dependency_overrides[
        authentication.get_principal_authority_repository
    ] = lambda: principal_reader
    app.dependency_overrides[
        tenant_access.get_tenant_membership_repository
    ] = lambda: membership_reader
    app.dependency_overrides[
        authorization_http.get_role_assignment_repository
    ] = lambda: role_reader
    app.include_router(command_api.router, prefix="/api")

    monkeypatch.setattr(
        command_api,
        "_db_handles",
        lambda: (context["client"], context["database"]),
    )
    return TestClient(app)


def _payload(
    screening: LegalConflictScreeningResult,
    *,
    review_id: str = "review-1",
    outcome: str = "CONFLICT_IDENTIFIED",
) -> dict[str, str]:
    return {
        "screening_id": screening.screening_id,
        "review_id": review_id,
        "outcome": outcome,
        "review_reason_reference": "review-reason:real-mongo",
    }


def test_real_direct_review_composition_resolves_durable_authorization_and_review(
    mongo_context: dict[str, Any],
) -> None:
    """Expose the complete L8-8J host-backed composition before HTTP redaction."""
    tenant, principal, screening = _seed(mongo_context)
    collections = mongo_context["collections"]
    principal_reader = _PrincipalReader(collections["principal"])
    membership_reader = _MembershipReader(collections["membership"])
    role_reader = _RoleReader(collections["roles"], collections["business"])
    authorization_registry = TenantAuthorizationDecisionEvidenceRegistry(
        collections["authorization"],
        principal_repository=principal_reader,
        membership_repository=membership_reader,
        role_assignment_repository=role_reader,
        business_role_repository=role_reader,
    )

    with mongo_context["client"].start_session() as session:
        session.start_transaction(
            read_concern=ReadConcern("snapshot"),
            write_concern=WriteConcern(w="majority", j=True),
        )
        value = issue_legal_conflict_review(
            tenant_id=tenant,
            reviewer_principal_id=principal,
            screening_id=screening.screening_id,
            review_id="review-direct",
            outcome=LegalConflictReviewOutcome.CONFLICT_IDENTIFIED,
            review_reason_reference="review-reason:direct-real-mongo",
            screening_collection=collections["screening"],
            review_collection=collections["review"],
            authorization_evidence_registry=authorization_registry,
            session=session,
        )
        assert value.tenant_id == tenant
        assert value.screening_id == screening.screening_id
        assert value.reviewer_principal_id == principal
        assert value.outcome is LegalConflictReviewOutcome.CONFLICT_IDENTIFIED
        assert value.reviewed_at >= screening.screened_at
        assert collections["authorization"].count_documents(
            {"tenant_id": tenant},
            session=session,
        ) == 1
        assert collections["review"].count_documents(
            {"tenant_id": tenant},
            session=session,
        ) == 1
        session.abort_transaction()

    assert collections["authorization"].count_documents(
        {"tenant_id": tenant}
    ) == 0
    assert collections["review"].count_documents({"tenant_id": tenant}) == 0


def test_real_http_success_and_exact_retry_replay_one_review(
    mongo_context: dict[str, Any],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    tenant, principal, screening = _seed(mongo_context)
    collections = mongo_context["collections"]
    client = _client(
        mongo_context,
        monkeypatch,
        tenant=tenant,
        principal=principal,
    )
    headers = {"X-Tenant-ID": tenant}

    first = client.post(
        "/api/legal-operations/conflict-reviews",
        json=_payload(screening),
        headers=headers,
    )
    second = client.post(
        "/api/legal-operations/conflict-reviews",
        json=_payload(screening),
        headers=headers,
    )

    assert first.status_code == 200, first.text
    assert second.status_code == 200, second.text
    assert second.json() == first.json()
    body = first.json()["data"]
    assert set(body) == {
        "review_id",
        "screening_id",
        "outcome",
        "reviewed_at",
        "fingerprint",
    }
    assert body["review_id"] == "review-1"
    assert body["screening_id"] == screening.screening_id
    assert body["outcome"] == "CONFLICT_IDENTIFIED"
    assert len(body["fingerprint"]) == 128
    assert collections["authorization"].count_documents(
        {"tenant_id": tenant}
    ) == 1
    assert collections["review"].count_documents({"tenant_id": tenant}) == 1


def test_real_missing_screening_returns_404_before_authorization_evidence_write(
    mongo_context: dict[str, Any],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    tenant, principal, screening = _seed(mongo_context, screening=False)
    collections = mongo_context["collections"]
    client = _client(
        mongo_context,
        monkeypatch,
        tenant=tenant,
        principal=principal,
    )
    response = client.post(
        "/api/legal-operations/conflict-reviews",
        json=_payload(screening),
        headers={"X-Tenant-ID": tenant},
    )
    assert response.status_code == 404
    assert response.json() == {"detail": "LEGAL_OPERATION_NOT_FOUND"}
    assert collections["authorization"].count_documents({}) == 0
    assert collections["review"].count_documents({}) == 0


def test_real_non_review_role_is_denied_before_command_transaction(
    mongo_context: dict[str, Any],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    tenant, principal, screening = _seed(
        mongo_context,
        business_role="tenant_legal_paralegal",
        grant_role="LEGAL_PARALEGAL",
    )
    collections = mongo_context["collections"]
    client = _client(
        mongo_context,
        monkeypatch,
        tenant=tenant,
        principal=principal,
    )
    response = client.post(
        "/api/legal-operations/conflict-reviews",
        json=_payload(screening),
        headers={"X-Tenant-ID": tenant},
    )
    assert response.status_code == 403
    assert collections["authorization"].count_documents({}) == 0
    assert collections["review"].count_documents({}) == 0


def test_real_divergent_same_review_id_returns_conflict_and_preserves_first(
    mongo_context: dict[str, Any],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    tenant, principal, screening = _seed(mongo_context)
    collections = mongo_context["collections"]
    client = _client(
        mongo_context,
        monkeypatch,
        tenant=tenant,
        principal=principal,
    )
    headers = {"X-Tenant-ID": tenant}

    first = client.post(
        "/api/legal-operations/conflict-reviews",
        json=_payload(screening),
        headers=headers,
    )
    divergent = client.post(
        "/api/legal-operations/conflict-reviews",
        json=_payload(
            screening,
            outcome=LegalConflictReviewOutcome.NO_CONFLICT_IDENTIFIED.value,
        ),
        headers=headers,
    )

    assert first.status_code == 200, first.text
    assert divergent.status_code == 409
    assert divergent.json() == {"detail": "LEGAL_CONFLICT_REVIEW_CONFLICT"}
    assert collections["authorization"].count_documents(
        {"tenant_id": tenant}
    ) == 1
    assert collections["review"].count_documents({"tenant_id": tenant}) == 1
    row = collections["review"].find_one({"tenant_id": tenant})
    assert row is not None
    assert row["review_payload"]["outcome"] == "CONFLICT_IDENTIFIED"


# ARTIFACT: test_legal_conflict_review_command_router_real_mongo.py
# VERSION: v1.0.0-L8-8K-CONFLICT-REVIEW-COMMAND-API-REAL-MONGO-CERT
# AUTHORITY BOUNDARY: host-backed authenticated conflict-review transport evidence only
# TENANT POSTURE: UUID-isolated database; IAM, screening, auth evidence and review rows are exact tenant scoped
# FAIL-CLOSED POSTURE: direct composition plus HTTP replay are exact; missing/unauthorized/divergent commands cannot create extra evidence
# FINANCIAL EXECUTION AUTHORITY: none; Kennel EOS exclusively
# END OF WILSY OS SOVEREIGN ARTIFACT
