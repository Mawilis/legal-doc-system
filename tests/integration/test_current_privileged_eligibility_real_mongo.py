"""Real-Mongo certificate for current privileged eligibility.

This certificate proves that persisted historical P2 evidence cannot outlive
the current authority it depended on.

No P4 activation issuance is exercised here.
"""

from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Any, Iterator
from uuid import uuid4

import pytest
from pymongo import MongoClient
from pymongo.client_session import ClientSession
from pymongo.collection import Collection

import tools.eos.auth.privileged_eligibility_evidence as evidence_module
from tools.eos.auth.current_platform_privileged_eligibility_prerequisite import (
    CurrentPlatformPrivilegedEligibilityPrerequisiteResolver,
)
from tools.eos.auth.current_privileged_eligibility import (
    CurrentPrivilegedEligibilityError,
    CurrentPrivilegedEligibilityResolver,
)
from tools.eos.auth.platform_privileged_eligibility_prerequisite import (
    PlatformPrerequisiteStatus,
    PlatformPrivilegedEligibilityPrerequisite,
)
from tools.eos.auth.platform_privileged_eligibility_prerequisite_registry import (
    PlatformPrivilegedEligibilityPrerequisiteRegistry,
)
from tools.eos.auth.principal_authority import (
    PrincipalAuthority,
    PrincipalStatus,
)
from tools.eos.auth.principal_authority_repository import (
    PrincipalAuthorityRepository,
)
from tools.eos.auth.privileged_eligibility import (
    ENTERPRISE_ADMIN,
    SOVEREIGN_ARCHITECT,
    evaluate_privileged_eligibility,
)
from tools.eos.auth.privileged_eligibility_evidence import (
    LEGACY_SCHEMA,
    LEGACY_VERSION,
    PrivilegedEligibilityEvidence,
)
from tools.eos.auth.privileged_eligibility_evidence_registry import (
    PrivilegedEligibilityEvidenceRegistry,
)
from tools.eos.auth.tenant_membership import (
    TenantMembershipAuthority,
    TenantMembershipStatus,
)
from tools.eos.auth.tenant_membership_repository import (
    TenantMembershipRepository,
)
from tools.eos.workforce.domain.workforce_relationship import (
    WorkforceRelationship,
    WorkforceRelationshipStatus,
    WorkforceRelationshipType,
    WorkforceScopeKind,
)
from tools.eos.workforce.registry import (
    workforce_relationship_registry,
)


MONGO_URI = 'mongodb://127.0.0.1:27027/?replicaSet=wilsyVendorCertRS'

AT = datetime(
    2026,
    10,
    14,
    18,
    0,
    tzinfo=timezone.utc,
)

PLATFORM_PRINCIPAL = "principal-current-p2-root"
TENANT_PRINCIPAL = "principal-current-p2-tenant"
TENANT = "tenant-current-p2"

PLATFORM_EVIDENCE_ID = "eligibility-current-p2-root"
TENANT_EVIDENCE_ID = "eligibility-current-p2-tenant"


@pytest.fixture()
def mongo() -> Iterator[dict[str, Any]]:
    client: MongoClient[Any] = MongoClient(
        MONGO_URI,
        serverSelectionTimeoutMS=5000,
    )

    hello = client.admin.command(
        "hello"
    )

    assert (
        hello.get("setName")
        == "wilsyVendorCertRS"
    )

    assert (
        hello.get(
            "logicalSessionTimeoutMinutes"
        )
        is not None
    )

    canonical_before = set(
        client["wilsy"]
        .list_collection_names()
    )

    db_name = (
        "wilsy_current_p2_"
        + uuid4().hex
    )

    db = client[
        db_name
    ]

    principals: Collection[Any] = (
        db["principal_authorities"]
    )

    memberships: Collection[Any] = (
        db["tenant_memberships"]
    )

    prerequisites: Collection[Any] = (
        db[
            "platform_privileged_eligibility_prerequisites"
        ]
    )

    evidence: Collection[Any] = (
        db[
            "privileged_eligibility_evidence"
        ]
    )

    workforce: Collection[Any] = (
        db[
            "workforce_relationships"
        ]
    )

    PrincipalAuthorityRepository.ensure_indexes(
        principals
    )

    TenantMembershipRepository.ensure_indexes(
        memberships
    )

    prerequisite_registry = (
        PlatformPrivilegedEligibilityPrerequisiteRegistry(
            prerequisites
        )
    )

    prerequisite_registry.ensure_indexes()

    evidence_registry = (
        PrivilegedEligibilityEvidenceRegistry(
            evidence
        )
    )

    evidence_registry.ensure_indexes()

    workforce_relationship_registry.ensure_indexes(
        workforce
    )

    platform_resolver = (
        CurrentPlatformPrivilegedEligibilityPrerequisiteResolver(
            principal_collection=
                principals,
            prerequisite_registry=
                prerequisite_registry,
        )
    )

    resolver = (
        CurrentPrivilegedEligibilityResolver(
            principal_collection=
                principals,
            membership_collection=
                memberships,
            evidence_registry=
                evidence_registry,
            platform_prerequisite_resolver=
                platform_resolver,
            workforce_relationship_collection=
                workforce,
        )
    )

    try:
        yield {
            "client": client,
            "db": db,
            "db_name": db_name,
            "principals": principals,
            "memberships": memberships,
            "prerequisites": prerequisites,
            "evidence": evidence,
            "workforce": workforce,
            "prerequisite_registry":
                prerequisite_registry,
            "evidence_registry":
                evidence_registry,
            "resolver": resolver,
            "canonical_before":
                canonical_before,
        }

    finally:
        canonical_after = set(
            client["wilsy"]
            .list_collection_names()
        )

        assert (
            canonical_after
            == canonical_before
        )

        client.drop_database(
            db_name
        )

        client.close()


def _tx(
    client: MongoClient[Any],
    operation,
):
    with client.start_session() as session:
        with session.start_transaction():
            return operation(
                session
            )


def _platform_prerequisite(
    *,
    principal_id: str = PLATFORM_PRINCIPAL,
    prerequisite_id: str = "platform-prerequisite-current-p2",
    source: str = "core-governance:current-p2",
) -> PlatformPrivilegedEligibilityPrerequisite:
    return (
        PlatformPrivilegedEligibilityPrerequisite
        .designate(
            platform_prerequisite_id=
                prerequisite_id,
            principal_id=
                principal_id,
            effective_from=
                AT,
            source_evidence_reference=
                source,
        )
    )


def _platform_evidence(
    prerequisite:
        PlatformPrivilegedEligibilityPrerequisite,
    *,
    evidence_id: str = PLATFORM_EVIDENCE_ID,
    revision: int | None = None,
    fingerprint: str | None = None,
    source_reference: str | None = None,
) -> PrivilegedEligibilityEvidence:
    decision = (
        evaluate_privileged_eligibility(
            principal_id=
                prerequisite.principal_id,
            privileged_role_id=
                SOVEREIGN_ARCHITECT,
            principal_current=True,
            platform_prerequisite_proven=True,
        )
    )

    return (
        PrivilegedEligibilityEvidence
        .from_decision(
            eligibility_evidence_id=
                evidence_id,
            decision=
                decision,
            evaluated_at=
                AT,
            idempotency_key=
                "idem-" + evidence_id,
            platform_prerequisite_id=
                prerequisite.platform_prerequisite_id,
            platform_prerequisite_revision=(
                prerequisite.revision
                if revision is None
                else revision
            ),
            platform_prerequisite_fingerprint=(
                prerequisite.prerequisite_fingerprint
                if fingerprint is None
                else fingerprint
            ),
            platform_prerequisite_source_evidence_reference=(
                prerequisite.source_evidence_reference
                if source_reference is None
                else source_reference
            ),
        )
    )


def _tenant_evidence(
    *,
    evidence_id: str = TENANT_EVIDENCE_ID,
) -> PrivilegedEligibilityEvidence:
    decision = (
        evaluate_privileged_eligibility(
            principal_id=
                TENANT_PRINCIPAL,
            privileged_role_id=
                ENTERPRISE_ADMIN,
            principal_current=True,
            tenant_id=
                TENANT,
            tenant_membership_current=True,
            workforce_required=True,
            tenant_workforce_current=True,
        )
    )

    return (
        PrivilegedEligibilityEvidence
        .from_decision(
            eligibility_evidence_id=
                evidence_id,
            decision=
                decision,
            evaluated_at=
                AT,
            idempotency_key=
                "idem-" + evidence_id,
        )
    )


def _active_workforce() -> WorkforceRelationship:
    return WorkforceRelationship(
        relationship_id=
            "workforce-current-p2",
        revision=1,
        scope_kind=
            WorkforceScopeKind.TENANT,
        scope_id=
            TENANT,
        principal_id=
            TENANT_PRINCIPAL,
        relationship_type=
            WorkforceRelationshipType.EMPLOYEE,
        status=
            WorkforceRelationshipStatus.ACTIVE,
        effective_from=
            AT,
        effective_until=
            None,
        status_effective_at=
            AT,
        reason_reference=
            "current-p2-active",
        supersedes_fingerprint=
            None,
    )


def _ended_workforce(
    current: WorkforceRelationship,
    *,
    ended_at: datetime,
) -> WorkforceRelationship:
    return WorkforceRelationship(
        relationship_id=
            current.relationship_id,
        revision=
            current.revision + 1,
        scope_kind=
            current.scope_kind,
        scope_id=
            current.scope_id,
        principal_id=
            current.principal_id,
        relationship_type=
            current.relationship_type,
        status=
            WorkforceRelationshipStatus.ENDED,
        effective_from=
            current.effective_from,
        effective_until=
            ended_at,
        status_effective_at=
            ended_at,
        reason_reference=
            "current-p2-ended",
        supersedes_fingerprint=
            current.fingerprint,
    )


def _seed_platform(
    mongo: dict[str, Any],
    *,
    evidence: PrivilegedEligibilityEvidence | None = None,
) -> tuple[
    PlatformPrivilegedEligibilityPrerequisite,
    PrivilegedEligibilityEvidence,
]:
    prerequisite = (
        _platform_prerequisite()
    )

    value = (
        evidence
        if evidence is not None
        else _platform_evidence(
            prerequisite
        )
    )

    def operation(
        session: ClientSession,
    ):
        PrincipalAuthorityRepository.create(
            PrincipalAuthority(
                PLATFORM_PRINCIPAL,
                PrincipalStatus.ACTIVE,
                0,
            ),
            mongo["principals"],
            session=session,
        )

        mongo[
            "prerequisite_registry"
        ].append(
            prerequisite,
            session=session,
        )

        mongo[
            "evidence_registry"
        ].create_or_replay(
            value,
            session=session,
        )

    _tx(
        mongo["client"],
        operation,
    )

    return (
        prerequisite,
        value,
    )


def _seed_tenant(
    mongo: dict[str, Any],
) -> tuple[
    PrivilegedEligibilityEvidence,
    WorkforceRelationship,
]:
    evidence = (
        _tenant_evidence()
    )

    workforce = (
        _active_workforce()
    )

    def operation(
        session: ClientSession,
    ):
        PrincipalAuthorityRepository.create(
            PrincipalAuthority(
                TENANT_PRINCIPAL,
                PrincipalStatus.ACTIVE,
                0,
            ),
            mongo["principals"],
            session=session,
        )

        TenantMembershipRepository.insert(
            TenantMembershipAuthority(
                TENANT_PRINCIPAL,
                TENANT,
                TenantMembershipStatus.ACTIVE,
                0,
            ),
            mongo["memberships"],
            session=session,
        )

        workforce_relationship_registry.persist_revision(
            workforce,
            collection=
                mongo["workforce"],
            session=session,
        )

        mongo[
            "evidence_registry"
        ].create_or_replay(
            evidence,
            session=session,
        )

    _tx(
        mongo["client"],
        operation,
    )

    return (
        evidence,
        workforce,
    )


def _resolve_in_tx(
    mongo: dict[str, Any],
    *,
    evidence_id: str,
    at: datetime,
):
    with mongo[
        "client"
    ].start_session() as session:
        with session.start_transaction():
            return (
                mongo["resolver"]
                .resolve(
                    eligibility_evidence_id=
                        evidence_id,
                    at=
                        at,
                    session=
                        session,
                )
            )


def test_real_platform_active_exact_lineage_is_current(
    mongo: dict[str, Any],
) -> None:
    _prerequisite, evidence = (
        _seed_platform(
            mongo
        )
    )

    assert (
        _resolve_in_tx(
            mongo,
            evidence_id=
                evidence.eligibility_evidence_id,
            at=
                AT + timedelta(
                    minutes=1
                ),
        )
        == evidence
    )


def test_real_platform_principal_revocation_denies_snapshot_true(
    mongo: dict[str, Any],
) -> None:
    _prerequisite, evidence = (
        _seed_platform(
            mongo
        )
    )

    assert (
        evidence.principal_current
        is True
    )

    _tx(
        mongo["client"],
        lambda session:
            PrincipalAuthorityRepository
            .compare_and_swap(
                PrincipalAuthority(
                    PLATFORM_PRINCIPAL,
                    PrincipalStatus.REVOKED,
                    1,
                ),
                0,
                mongo["principals"],
                session=session,
            ),
    )

    assert (
        _resolve_in_tx(
            mongo,
            evidence_id=
                evidence.eligibility_evidence_id,
            at=
                AT + timedelta(
                    minutes=2
                ),
        )
        is None
    )


def test_real_platform_retirement_denies_historic_p2(
    mongo: dict[str, Any],
) -> None:
    prerequisite, evidence = (
        _seed_platform(
            mongo
        )
    )

    retired_at = (
        AT + timedelta(
            minutes=10
        )
    )

    retired = (
        prerequisite.transition(
            status=
                PlatformPrerequisiteStatus.RETIRED,
            effective_from=
                retired_at,
            source_evidence_reference=
                "core-governance:retired-current-p2",
        )
    )

    _tx(
        mongo["client"],
        lambda session:
            mongo[
                "prerequisite_registry"
            ].append(
                retired,
                session=session,
            ),
    )

    assert (
        _resolve_in_tx(
            mongo,
            evidence_id=
                evidence.eligibility_evidence_id,
            at=
                retired_at
                + timedelta(
                    seconds=1
                ),
        )
        is None
    )


def test_real_platform_lineage_drift_denies(
    mongo: dict[str, Any],
) -> None:
    prerequisite = (
        _platform_prerequisite()
    )

    stale = (
        _platform_evidence(
            prerequisite,
            evidence_id=
                "eligibility-current-p2-stale-lineage",
            revision=
                prerequisite.revision + 7,
            fingerprint=
                "b" * 128,
            source_reference=
                "core-governance:stale-lineage",
        )
    )

    _seed_platform(
        mongo,
        evidence=stale,
    )

    assert (
        _resolve_in_tx(
            mongo,
            evidence_id=
                stale.eligibility_evidence_id,
            at=
                AT + timedelta(
                    minutes=1
                ),
        )
        is None
    )


def test_real_legacy_v1_platform_boolean_denied(
    mongo: dict[str, Any],
) -> None:
    prerequisite = (
        _platform_prerequisite()
    )

    payload = {
        "schema":
            LEGACY_SCHEMA,
        "version":
            LEGACY_VERSION,
        "eligibility_evidence_id":
            "legacy-current-p2-platform",
        "principal_id":
            PLATFORM_PRINCIPAL,
        "privileged_role_id":
            "SOVEREIGN_ARCHITECT",
        "target_class":
            "PLATFORM_SYSTEM_ROOT",
        "tenant_id":
            None,
        "principal_current":
            True,
        "tenant_membership_current":
            None,
        "workforce_required":
            False,
        "tenant_workforce_current":
            None,
        "platform_prerequisite_proven":
            True,
        "eligible":
            True,
        "reason":
            "ELIGIBLE",
        "evaluated_at":
            AT.isoformat(),
        "idempotency_key":
            "legacy-current-p2-idem",
    }

    row = {
        **payload,
        "eligibility_evidence_fingerprint":
            evidence_module._fingerprint(
                payload
            ),
    }

    restored = (
        PrivilegedEligibilityEvidence
        .from_persisted(
            row
        )
    )

    assert (
        restored.to_persisted()
        == row
    )

    def operation(
        session: ClientSession,
    ):
        PrincipalAuthorityRepository.create(
            PrincipalAuthority(
                PLATFORM_PRINCIPAL,
                PrincipalStatus.ACTIVE,
                0,
            ),
            mongo["principals"],
            session=session,
        )

        mongo[
            "prerequisite_registry"
        ].append(
            prerequisite,
            session=session,
        )

        mongo[
            "evidence"
        ].insert_one(
            row,
            session=session,
        )

    _tx(
        mongo["client"],
        operation,
    )

    assert (
        _resolve_in_tx(
            mongo,
            evidence_id=
                "legacy-current-p2-platform",
            at=
                AT + timedelta(
                    minutes=1
                ),
        )
        is None
    )


def test_real_tenant_live_principal_membership_workforce_current(
    mongo: dict[str, Any],
) -> None:
    evidence, _workforce = (
        _seed_tenant(
            mongo
        )
    )

    assert (
        _resolve_in_tx(
            mongo,
            evidence_id=
                evidence.eligibility_evidence_id,
            at=
                AT + timedelta(
                    minutes=1
                ),
        )
        == evidence
    )


def test_real_tenant_principal_revocation_denies_snapshot_true(
    mongo: dict[str, Any],
) -> None:
    evidence, _workforce = (
        _seed_tenant(
            mongo
        )
    )

    assert (
        evidence.principal_current
        is True
    )

    _tx(
        mongo["client"],
        lambda session:
            PrincipalAuthorityRepository
            .compare_and_swap(
                PrincipalAuthority(
                    TENANT_PRINCIPAL,
                    PrincipalStatus.REVOKED,
                    1,
                ),
                0,
                mongo["principals"],
                session=session,
            ),
    )

    assert (
        _resolve_in_tx(
            mongo,
            evidence_id=
                evidence.eligibility_evidence_id,
            at=
                AT + timedelta(
                    minutes=2
                ),
        )
        is None
    )


def test_real_tenant_membership_revocation_denies_snapshot_true(
    mongo: dict[str, Any],
) -> None:
    evidence, _workforce = (
        _seed_tenant(
            mongo
        )
    )

    assert (
        evidence.tenant_membership_current
        is True
    )

    _tx(
        mongo["client"],
        lambda session:
            TenantMembershipRepository
            .compare_and_swap(
                TenantMembershipAuthority(
                    TENANT_PRINCIPAL,
                    TENANT,
                    TenantMembershipStatus.REVOKED,
                    1,
                ),
                0,
                mongo["memberships"],
                session=session,
            ),
    )

    assert (
        _resolve_in_tx(
            mongo,
            evidence_id=
                evidence.eligibility_evidence_id,
            at=
                AT + timedelta(
                    minutes=2
                ),
        )
        is None
    )


def test_real_tenant_workforce_loss_denies_snapshot_true(
    mongo: dict[str, Any],
) -> None:
    evidence, active = (
        _seed_tenant(
            mongo
        )
    )

    before_end = (
        AT + timedelta(
            minutes=5
        )
    )

    assert (
        _resolve_in_tx(
            mongo,
            evidence_id=
                evidence.eligibility_evidence_id,
            at=
                before_end,
        )
        == evidence
    )

    assert (
        evidence.tenant_workforce_current
        is True
    )

    ended_at = (
        AT + timedelta(
            minutes=10
        )
    )

    ended = (
        _ended_workforce(
            active,
            ended_at=
                ended_at,
        )
    )

    _tx(
        mongo["client"],
        lambda session:
            workforce_relationship_registry
            .persist_revision(
                ended,
                collection=
                    mongo["workforce"],
                session=session,
            ),
    )

    assert (
        _resolve_in_tx(
            mongo,
            evidence_id=
                evidence.eligibility_evidence_id,
            at=
                ended_at
                + timedelta(
                    seconds=1
                ),
        )
        is None
    )


def test_real_workforce_currentness_requires_caller_transaction(
    mongo: dict[str, Any],
) -> None:
    evidence, _workforce = (
        _seed_tenant(
            mongo
        )
    )

    with pytest.raises(
        CurrentPrivilegedEligibilityError,
        match=
            "WORKFORCE_CURRENTNESS_UNAVAILABLE",
    ):
        mongo[
            "resolver"
        ].resolve(
            eligibility_evidence_id=
                evidence.eligibility_evidence_id,
            at=
                AT + timedelta(
                    minutes=1
                ),
            session=None,
        )


def test_real_current_p2_resolution_is_read_only(
    mongo: dict[str, Any],
) -> None:
    platform_prerequisite, platform_evidence = (
        _seed_platform(
            mongo
        )
    )

    counts_before = {
        "principals":
            mongo["principals"]
            .count_documents({}),
        "memberships":
            mongo["memberships"]
            .count_documents({}),
        "prerequisites":
            mongo["prerequisites"]
            .count_documents({}),
        "evidence":
            mongo["evidence"]
            .count_documents({}),
        "workforce":
            mongo["workforce"]
            .count_documents({}),
    }

    assert (
        _resolve_in_tx(
            mongo,
            evidence_id=
                platform_evidence
                .eligibility_evidence_id,
            at=
                AT + timedelta(
                    minutes=1
                ),
        )
        == platform_evidence
    )

    counts_after = {
        "principals":
            mongo["principals"]
            .count_documents({}),
        "memberships":
            mongo["memberships"]
            .count_documents({}),
        "prerequisites":
            mongo["prerequisites"]
            .count_documents({}),
        "evidence":
            mongo["evidence"]
            .count_documents({}),
        "workforce":
            mongo["workforce"]
            .count_documents({}),
    }

    assert (
        counts_after
        == counts_before
    )

    assert (
        platform_prerequisite.revision
        == 1
    )


def test_real_certificate_owns_no_p4_or_activation_collection(
    mongo: dict[str, Any],
) -> None:
    names = set(
        mongo["db"]
        .list_collection_names()
    )

    assert (
        "privileged_activations"
        not in names
    )

    assert (
        "privileged_activation_assurance"
        not in names
    )
