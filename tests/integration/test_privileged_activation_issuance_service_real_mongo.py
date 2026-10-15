"""
TITLE:
    WILSY OS P4 Privileged Activation Issuance Real-Mongo Certificate

VERSION:
    v1.0.0-P4-C5-PRIVILEGED-ACTIVATION-ISSUANCE-REAL-MONGO

AUTHORITY:
    Wilsy OS Sovereign IAM certification only.

PURPOSE:
    Certify the minimal P4 activation issuance composer against a writable
    Mongo replica set. The certificate composes real current D12 permission
    possession, real current P2 privileged eligibility, real interactive P3
    assurance, and the sealed activation registry inside one caller-owned
    Mongo transaction.

REPLAY:
    Every replay re-establishes P3, P2, and D12. A replay creates fresh P3
    historic evidence but returns the original still-current activation
    without refreshing activation identity, activated_at, or effective_until.

TRANSACTION BOUNDARY:
    The caller owns transaction start/commit/abort. Aborted issuance leaves
    neither P3 assurance evidence nor an activation.

AUTHORITY BOUNDARY:
    No HTTP, P5 current-use, break-glass, role-creation, tenant-plan,
    subscription, settlement, payment, or financial authority is created.
"""

from __future__ import annotations

from datetime import datetime, timedelta, timezone
import os
from types import SimpleNamespace
from typing import Any, Iterator, cast
from uuid import uuid4

import pytest
from pymongo import MongoClient
from pymongo.client_session import ClientSession

from tools.eos.auth.current_platform_privileged_eligibility_prerequisite import (
    CurrentPlatformPrivilegedEligibilityPrerequisiteResolver,
)
from tools.eos.auth.current_privileged_eligibility import (
    CurrentPrivilegedEligibilityResolver,
)
from tools.eos.auth.current_system_permission_possession import (
    CurrentSystemPermissionPossessionResolver,
)
from tools.eos.auth.platform_privileged_eligibility_prerequisite import (
    PlatformPrivilegedEligibilityPrerequisite,
)
from tools.eos.auth.platform_privileged_eligibility_prerequisite_registry import (
    COLLECTION as PREREQUISITE_COLLECTION,
    PlatformPrivilegedEligibilityPrerequisiteRegistry,
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
    ISSUANCE_PERMISSION,
)
from tools.eos.auth.privileged_activation_issuance_service import (
    PrivilegedActivationIssuanceService,
)
from tools.eos.auth.privileged_activation_registry import (
    COLLECTION as ACTIVATION_COLLECTION,
    PrivilegedActivationRegistry,
)
from tools.eos.auth.privileged_channel_currentness import (
    FactorVerificationStatus,
    InteractiveFactorVerificationEvent,
)
from tools.eos.auth.privileged_eligibility import (
    SOVEREIGN_ARCHITECT,
    evaluate_privileged_eligibility,
)
from tools.eos.auth.privileged_eligibility_evidence import (
    PrivilegedEligibilityEvidence,
)
from tools.eos.auth.privileged_eligibility_evidence_registry import (
    COLLECTION as ELIGIBILITY_COLLECTION,
    PrivilegedEligibilityEvidenceRegistry,
)
from tools.eos.auth.privileged_factor_verification_currentness_registry import (
    COLLECTION as FACTOR_COLLECTION,
    PrivilegedFactorVerificationCurrentnessRegistry,
)
from tools.eos.auth.privileged_interactive_assurance_service import (
    PrivilegedInteractiveAssuranceService,
)
from tools.eos.auth.privileged_interactive_security_proof import (
    PrivilegedInteractiveProofStatus,
    PrivilegedInteractiveSecurityProof,
)
from tools.eos.auth.privileged_interactive_security_proof_registry import (
    COLLECTION as PROOF_COLLECTION,
    PrivilegedInteractiveSecurityProofRegistry,
)
from tools.eos.auth.privileged_security_assurance import (
    PrivilegedAssurancePurpose,
)
from tools.eos.auth.privileged_security_assurance_evidence_registry import (
    COLLECTION as ASSURANCE_COLLECTION,
    PrivilegedSecurityAssuranceEvidenceRegistry,
)
from tools.eos.auth.system_permission_assignment import (
    SystemPermissionAssignment,
)
from tools.eos.auth.system_permission_assignment_registry import (
    COLLECTION as ASSIGNMENT_COLLECTION,
    SystemPermissionAssignmentRegistry,
)
from tools.eos.kernel import db as kernel_db
from tools.eos.saas.auth.auth_registry import (
    AuthRegistry,
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
    3,
    30,
    tzinfo=timezone.utc,
)

PROOF_TENANT = "tenant-p4-c5-proof"
PRINCIPAL = "principal-p4-c5"
SESSION_REFERENCE = "WILSYSESSION-p4-c5"
FACTOR_REFERENCE = "WILSYFACTOR-p4-c5"
PROOF_REFERENCE = "WILSYPROOFREF-p4-c5"
PROOF_ID = "WILSYPROOF-p4-c5"

PREREQUISITE_ID = "platform-prerequisite-p4-c5"
ELIGIBILITY_ID = "eligibility-p4-c5"
ASSIGNMENT_ID = "assignment-p4-c5"

PURPOSE = (
    PrivilegedAssurancePurpose
    .PRIVILEGED_ELIGIBILITY_TO_ACTIVATION
)


class TenantRegistry:
    @classmethod
    def resolve_canonical_tenant(
        cls,
        value: object,
        *,
        allow_alias: bool = False,
        session: object = None,
    ) -> object:
        del allow_alias, session

        if value != PROOF_TENANT:
            raise ValueError(
                "AUTH_TENANT_CANONICAL_INVALID"
            )

        return SimpleNamespace(
            tenant_id=PROOF_TENANT
        )


class SequenceFactory:
    def __init__(
        self,
        prefix: str,
    ) -> None:
        self.prefix = prefix
        self.count = 0

    def __call__(self) -> str:
        self.count += 1
        return (
            self.prefix
            + "-"
            + str(self.count)
        )


def _no_ttl(
    collection: Any,
) -> bool:
    return all(
        "expireAfterSeconds"
        not in item
        for item in collection.list_indexes()
    )


@pytest.fixture()
def context(
    monkeypatch: pytest.MonkeyPatch,
) -> Iterator[dict[str, Any]]:
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
        "wilsy_p4_c5_"
        + uuid4().hex
    )

    assert db_name != "wilsy"

    database = client[
        db_name
    ]

    monkeypatch.setattr(
        kernel_db,
        "_db",
        database,
    )

    monkeypatch.setattr(
        kernel_db,
        "_client",
        client,
    )

    monkeypatch.setattr(
        kernel_db,
        "_ready",
        True,
    )

    principals = database[
        PRINCIPAL_COLLECTION
    ]

    assignments = database[
        ASSIGNMENT_COLLECTION
    ]

    prerequisites = database[
        PREREQUISITE_COLLECTION
    ]

    eligibility_collection = database[
        ELIGIBILITY_COLLECTION
    ]

    factors = database[
        FACTOR_COLLECTION
    ]

    proofs = database[
        PROOF_COLLECTION
    ]

    assurance_collection = database[
        ASSURANCE_COLLECTION
    ]

    activations = database[
        ACTIVATION_COLLECTION
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

    prerequisite_registry = (
        PlatformPrivilegedEligibilityPrerequisiteRegistry(
            prerequisites
        )
    )
    prerequisite_registry.ensure_indexes()

    eligibility_registry = (
        PrivilegedEligibilityEvidenceRegistry(
            eligibility_collection
        )
    )
    eligibility_registry.ensure_indexes()

    factor_registry = (
        PrivilegedFactorVerificationCurrentnessRegistry(
            factors
        )
    )
    factor_registry.ensure_indexes()

    proof_registry = (
        PrivilegedInteractiveSecurityProofRegistry(
            proofs
        )
    )
    proof_registry.ensure_indexes()

    assurance_registry = (
        PrivilegedSecurityAssuranceEvidenceRegistry(
            assurance_collection
        )
    )
    assurance_registry.ensure_indexes()

    activation_registry = (
        PrivilegedActivationRegistry(
            activations
        )
    )
    activation_registry.ensure_indexes()

    platform_resolver = (
        CurrentPlatformPrivilegedEligibilityPrerequisiteResolver(
            principal_collection=
                principals,
            prerequisite_registry=
                prerequisite_registry,
        )
    )

    eligibility_resolver = (
        CurrentPrivilegedEligibilityResolver(
            principal_collection=
                principals,
            membership_collection=
                database[
                    "tenant_memberships"
                ],
            evidence_registry=
                eligibility_registry,
            platform_prerequisite_resolver=
                platform_resolver,
            workforce_relationship_collection=
                database[
                    "workforce_relationships"
                ],
        )
    )

    permission_resolver = (
        CurrentSystemPermissionPossessionResolver(
            principal_collection=
                principals,
            assignment_registry=
                assignment_registry,
        )
    )

    auth = AuthRegistry()

    cast(
        Any,
        auth,
    ).tenant_registry = TenantRegistry

    evidence_ids = SequenceFactory(
        "WILSYASSURANCE-p4-c5"
    )

    attempt_ids = SequenceFactory(
        "attempt-p4-c5"
    )

    assurance_service = (
        PrivilegedInteractiveAssuranceService(
            auth_registry=
                auth,
            principal_collection=
                principals,
            factor_registry=
                factor_registry,
            proof_registry=
                proof_registry,
            evidence_registry=
                assurance_registry,
            maximum_age_seconds=300,
            clock=lambda: NOW,
            evidence_id_factory=
                evidence_ids,
        )
    )

    issuance_service = (
        PrivilegedActivationIssuanceService(
            permission_resolver=
                permission_resolver,
            eligibility_resolver=
                eligibility_resolver,
            interactive_assurance_service=
                assurance_service,
            noninteractive_assurance_service=
                object(),
            activation_registry=
                activation_registry,
            activation_id_factory=
                lambda: "unused-p4-c5",
            clock=lambda: NOW,
            assurance_attempt_id_factory=
                attempt_ids,
        )
    )

    result = {
        "client": client,
        "database": database,
        "db_name": db_name,
        "principals": principals,
        "assignment_registry":
            assignment_registry,
        "prerequisite_registry":
            prerequisite_registry,
        "eligibility_registry":
            eligibility_registry,
        "factor_registry":
            factor_registry,
        "proof_registry":
            proof_registry,
        "assurance_registry":
            assurance_registry,
        "assurance_collection":
            assurance_collection,
        "activation_registry":
            activation_registry,
        "activation_collection":
            activations,
        "issuance_service":
            issuance_service,
        "evidence_ids":
            evidence_ids,
        "attempt_ids":
            attempt_ids,
    }

    try:
        yield result
    finally:
        client.drop_database(
            db_name
        )
        client.close()


def _seed(
    context: dict[str, Any],
    *,
    include_permission: bool = True,
) -> PrivilegedEligibilityEvidence:
    prerequisite = (
        PlatformPrivilegedEligibilityPrerequisite
        .designate(
            platform_prerequisite_id=
                PREREQUISITE_ID,
            principal_id=
                PRINCIPAL,
            effective_from=
                NOW
                - timedelta(minutes=1),
            source_evidence_reference=
                "core-governance:p4-c5",
        )
    )

    decision = (
        evaluate_privileged_eligibility(
            principal_id=
                PRINCIPAL,
            privileged_role_id=
                SOVEREIGN_ARCHITECT,
            principal_current=True,
            platform_prerequisite_proven=True,
        )
    )

    evidence = (
        PrivilegedEligibilityEvidence
        .from_decision(
            eligibility_evidence_id=
                ELIGIBILITY_ID,
            decision=
                decision,
            evaluated_at=
                NOW,
            idempotency_key=
                "eligibility-p4-c5-idem",
            platform_prerequisite_id=
                prerequisite
                .platform_prerequisite_id,
            platform_prerequisite_revision=
                prerequisite.revision,
            platform_prerequisite_fingerprint=
                prerequisite
                .prerequisite_fingerprint,
            platform_prerequisite_source_evidence_reference=
                prerequisite
                .source_evidence_reference,
        )
    )

    assignment = (
        SystemPermissionAssignment.assign(
            assignment_id=
                ASSIGNMENT_ID,
            principal_id=
                PRINCIPAL,
            permission_id=
                ISSUANCE_PERMISSION,
            assigned_by_principal_id=
                "principal-p4-c5-grantor",
            assigned_at=
                NOW
                - timedelta(minutes=1),
            assignment_evidence_reference=
                "assignment-evidence-p4-c5",
        )
    )

    with context[
        "client"
    ].start_session() as session:
        with session.start_transaction():
            PrincipalAuthorityRepository.create(
                PrincipalAuthority(
                    PRINCIPAL,
                    PrincipalStatus.ACTIVE,
                    1,
                ),
                context[
                    "principals"
                ],
                session=session,
            )

            context[
                "database"
            ]["users"].insert_one(
                {
                    "user_id": PRINCIPAL,
                    "email":
                        "p4-c5@example.com",
                    "firstName": "P4",
                    "lastName": "Certificate",
                    "role": "USER",
                    "permissions": [],
                    "tenantId":
                        PROOF_TENANT,
                    "passwordHash":
                        "synthetic",
                    "credential_revision": 7,
                    "mfaRegistered": True,
                    "hasSignedCovenant": True,
                    "createdAt":
                        NOW.replace(
                            tzinfo=None
                        ),
                    "updatedAt":
                        NOW.replace(
                            tzinfo=None
                        ),
                },
                session=session,
            )

            context[
                "database"
            ]["sessions"].insert_one(
                {
                    "tenant_id":
                        PROOF_TENANT,
                    "user_id":
                        PRINCIPAL,
                    "session_reference":
                        SESSION_REFERENCE,
                    "expires_at":
                        NOW
                        + timedelta(hours=1),
                },
                session=session,
            )

            context[
                "prerequisite_registry"
            ].append(
                prerequisite,
                session=session,
            )

            context[
                "eligibility_registry"
            ].create_or_replay(
                evidence,
                session=session,
            )

            if include_permission:
                context[
                    "assignment_registry"
                ].create_or_replay(
                    assignment,
                    idempotency_key=
                        "assignment-create-p4-c5",
                    session=session,
                )

            context[
                "factor_registry"
            ].create_or_replay(
                InteractiveFactorVerificationEvent(
                    FACTOR_REFERENCE,
                    PRINCIPAL,
                    SESSION_REFERENCE,
                    7,
                    NOW,
                    FactorVerificationStatus
                    .VERIFIED,
                ),
                recorded_at=NOW,
                session=session,
            )

            context[
                "proof_registry"
            ].create_or_replay(
                PrivilegedInteractiveSecurityProof(
                    PROOF_ID,
                    PRINCIPAL,
                    FACTOR_REFERENCE,
                    NOW,
                    7,
                    SESSION_REFERENCE,
                    PrivilegedInteractiveProofStatus
                    .VERIFIED,
                    PROOF_REFERENCE,
                ),
                status_changed_at=
                    NOW,
                idempotency_key=
                    "proof-create-p4-c5",
                session=session,
            )

    return evidence


def _issue(
    context: dict[str, Any],
    *,
    key: str,
    session: ClientSession,
):
    return (
        context[
            "issuance_service"
        ]
        .issue_interactive(
            tenant_id=None,
            eligibility_evidence_id=
                ELIGIBILITY_ID,
            proof_tenant_id=
                PROOF_TENANT,
            proof_reference=
                PROOF_REFERENCE,
            issuance_idempotency_key=
                key,
            session=session,
        )
    )


def test_real_mongo_first_issuance_composes_all_four_authorities(
    context: dict[str, Any],
) -> None:
    evidence = _seed(
        context
    )

    with context[
        "client"
    ].start_session() as session:
        session.start_transaction()

        activation = _issue(
            context,
            key="issue-p4-c5",
            session=session,
        )

        session.commit_transaction()

    assert (
        activation.principal_id
        == PRINCIPAL
    )

    assert (
        activation.actor_principal_id
        == PRINCIPAL
    )

    assert (
        activation.privileged_role_id
        == SOVEREIGN_ARCHITECT
    )

    assert (
        activation.tenant_id
        is None
    )

    assert (
        activation.eligibility_evidence_id
        == evidence.eligibility_evidence_id
    )

    assert (
        activation.eligibility_evidence_fingerprint
        == evidence.eligibility_evidence_fingerprint
    )

    history = (
        context[
            "activation_registry"
        ]
        .get_history(
            activation.activation_id
        )
    )

    assert history == (
        activation,
    )

    assert (
        context[
            "assurance_collection"
        ].count_documents({})
        == 1
    )


def test_real_mongo_exact_replay_freshens_p3_but_not_activation_lifetime(
    context: dict[str, Any],
) -> None:
    _seed(
        context
    )

    with context[
        "client"
    ].start_session() as session:
        session.start_transaction()

        first = _issue(
            context,
            key="issue-p4-c5",
            session=session,
        )

        session.commit_transaction()

    with context[
        "client"
    ].start_session() as session:
        session.start_transaction()

        second = _issue(
            context,
            key="issue-p4-c5",
            session=session,
        )

        session.commit_transaction()

    assert second == first

    assert (
        second.activation_id
        == first.activation_id
    )

    assert (
        second.activated_at
        == first.activated_at
    )

    assert (
        second.effective_until
        == first.effective_until
    )

    assert (
        context[
            "activation_registry"
        ]
        .get_history(
            first.activation_id
        )
        == (first,)
    )

    assurance_rows = list(
        context[
            "assurance_collection"
        ].find({})
    )

    assert len(
        assurance_rows
    ) == 2

    keys = {
        row["idempotency_key"]
        for row in assurance_rows
    }

    assert len(keys) == 2

    assert all(
        str(key).startswith(
            "issue-p4-c5:assurance:"
        )
        for key in keys
    )


def test_real_mongo_abort_rolls_back_fresh_p3_and_activation(
    context: dict[str, Any],
) -> None:
    _seed(
        context
    )

    assurance_before = (
        context[
            "assurance_collection"
        ].count_documents({})
    )

    activation_before = (
        context[
            "activation_collection"
        ].count_documents({})
    )

    with context[
        "client"
    ].start_session() as session:
        session.start_transaction()

        value = _issue(
            context,
            key="issue-p4-c5-abort",
            session=session,
        )

        assert value is not None

        session.abort_transaction()

    assert (
        context[
            "assurance_collection"
        ].count_documents({})
        == assurance_before
    )

    assert (
        context[
            "activation_collection"
        ].count_documents({})
        == activation_before
    )


def test_real_mongo_missing_current_d12_denies_before_activation(
    context: dict[str, Any],
) -> None:
    _seed(
        context,
        include_permission=False,
    )

    with context[
        "client"
    ].start_session() as session:
        session.start_transaction()

        with pytest.raises(
            Exception,
            match="ISSUANCE_PERMISSION_NOT_CURRENT",
        ):
            _issue(
                context,
                key="issue-p4-c5-denied",
                session=session,
            )

        session.abort_transaction()

    assert (
        context[
            "activation_collection"
        ].count_documents({})
        == 0
    )

    assert (
        context[
            "assurance_collection"
        ].count_documents({})
        == 0
    )


def test_real_mongo_activation_authority_collections_have_no_ttl(
    context: dict[str, Any],
) -> None:
    assert _no_ttl(
        context[
            "activation_collection"
        ]
    )

    assert _no_ttl(
        context[
            "assurance_collection"
        ]
    )

    assignment_collection = (
        context[
            "database"
        ][
            ASSIGNMENT_COLLECTION
        ]
    )

    eligibility_collection = (
        context[
            "database"
        ][
            ELIGIBILITY_COLLECTION
        ]
    )

    assert _no_ttl(
        assignment_collection
    )

    assert _no_ttl(
        eligibility_collection
    )
