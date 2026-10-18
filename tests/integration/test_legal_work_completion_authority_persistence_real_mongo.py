"""
P14-R20R26 zero-monkeypatch real-Mongo completion-authority certificate.

Proves the actual production chain:

    caller-owned active Mongo transaction
      -> R20R23 historical assignment + canonical IAM evidence issuance
      -> R20R22 full completion authority evidence
      -> R20R18 completion event construction
      -> LegalWorkCompletionEventRegistry persistence

No monkeypatching of R20R23, R20R18, R20R20 or IAM evidence issuance.

Protected Mongo port 27027 is forbidden.
"""

from __future__ import annotations

from datetime import datetime, timedelta, timezone
import os
from typing import Any, Iterator
import uuid

import pytest
from pymongo import MongoClient
from pymongo.errors import PyMongoError
from pymongo.uri_parser import parse_uri

from tools.eos.auth.principal_authority import (
    PrincipalAuthority,
)
from tools.eos.auth.principal_authority_repository import (
    PrincipalAuthorityRepository,
)
from tools.eos.auth.principal_status import (
    PrincipalStatus,
)
from tools.eos.auth.role_assignment import (
    RoleAssignmentAuthority,
    RoleAssignmentStatus,
)
from tools.eos.auth.role_assignment_repository import (
    RoleAssignmentRepository,
)
from tools.eos.auth.tenant_authorization_decision_evidence_registry import (
    TenantAuthorizationDecisionEvidenceRegistry,
)
from tools.eos.auth.tenant_membership import (
    TenantMembershipAuthority,
    TenantMembershipStatus,
)
from tools.eos.auth.tenant_membership_repository import (
    TenantMembershipRepository,
)
from tools.eos.legal_operations.domain.legal_work_assignment import (
    LegalWorkAssignment,
)
from tools.eos.legal_operations.domain.legal_work_item import (
    LegalWorkItem,
    LegalWorkItemStatus,
)
from tools.eos.legal_operations.orchestration.legal_work_completion_persistence_orchestrator import (
    record_legal_work_completion,
)
from tools.eos.legal_operations.registry.legal_work_completion_event_registry import (
    COLLECTION_NAME as COMPLETION_COLLECTION_NAME,
    LegalWorkCompletionEventRegistry,
)


URI_ENV = "TEST_LEGAL_WORK_COMPLETION_EVENT_MONGO_URI"
RS_ENV = "TEST_LEGAL_WORK_COMPLETION_EVENT_REPLICA_SET"

IAM_COLLECTION_NAME = (
    "tenant_authorization_decision_evidence"
)

PRINCIPAL_COLLECTION = "principal_authorities"
MEMBERSHIP_COLLECTION = "tenant_memberships"
ROLE_ASSIGNMENT_COLLECTION = "role_assignments"

AUTHORIZATION_ROLE = "LEGAL_PARTNER"
BUSINESS_ROLE = "tenant_legal_partner"

OPERATION = "legal_work_item_complete"
PERMISSION = "legal_operations:work_item:complete"

EVALUATED_AT = datetime(
    2026,
    10,
    17,
    10,
    0,
    tzinfo=timezone.utc,
)

SOURCE_FP = "a" * 128
COMPLETION_FP = "b" * 128


class _PrincipalReader:
    def __init__(
        self,
        collection: Any,
    ) -> None:
        self.collection = collection

    def resolve(
        self,
        principal_id: str,
        *,
        session: Any = None,
    ) -> PrincipalAuthority:
        return PrincipalAuthorityRepository.resolve(
            principal_id,
            self.collection,
            session=session,
        )


class _MembershipReader:
    def __init__(
        self,
        collection: Any,
    ) -> None:
        self.collection = collection

    def resolve(
        self,
        principal_id: str,
        tenant_id: str,
        *,
        session: Any = None,
    ) -> TenantMembershipAuthority:
        return TenantMembershipRepository.resolve(
            principal_id,
            tenant_id,
            self.collection,
            session=session,
        )


class _RoleReader:
    def __init__(
        self,
        collection: Any,
    ) -> None:
        self.collection = collection

    def resolve(
        self,
        principal_id: str,
        tenant_id: str,
        role_id: str,
        *,
        session: Any = None,
    ) -> RoleAssignmentAuthority:
        return RoleAssignmentRepository.resolve(
            principal_id,
            tenant_id,
            role_id,
            self.collection,
            session=session,
        )


def _runtime_contract() -> tuple[str, str]:
    if URI_ENV not in os.environ:
        raise RuntimeError(
            "R20R26_MONGO_URI_ENV_REQUIRED"
        )

    if RS_ENV not in os.environ:
        raise RuntimeError(
            "R20R26_MONGO_REPLICA_SET_ENV_REQUIRED"
        )

    uri = os.environ[URI_ENV].strip()
    replica_set = os.environ[RS_ENV].strip()

    if not uri:
        raise RuntimeError(
            "R20R26_MONGO_URI_REQUIRED"
        )

    if not replica_set:
        raise RuntimeError(
            "R20R26_REPLICA_SET_REQUIRED"
        )

    parsed = parse_uri(uri)

    nodes = tuple(
        parsed.get(
            "nodelist",
            (),
        )
    )

    if len(nodes) != 1:
        raise RuntimeError(
            "R20R26_SINGLE_NODE_REQUIRED"
        )

    host, port = nodes[0]

    if host not in (
        "127.0.0.1",
        "localhost",
    ):
        raise RuntimeError(
            "R20R26_LOOPBACK_REQUIRED"
        )

    if int(port) == 27027:
        raise RuntimeError(
            "R20R26_PROTECTED_27027_FORBIDDEN"
        )

    return uri, replica_set


@pytest.fixture()
def mongo_context() -> Iterator[
    tuple[
        MongoClient[Any],
        Any,
        TenantAuthorizationDecisionEvidenceRegistry,
        LegalWorkCompletionEventRegistry,
    ]
]:
    uri, replica_set = _runtime_contract()

    client: MongoClient[Any] = MongoClient(
        uri,
        replicaSet=replica_set,
        serverSelectionTimeoutMS=3000,
        connectTimeoutMS=3000,
        socketTimeoutMS=3000,
        retryWrites=True,
    )

    database: Any = None

    try:
        try:
            hello = client.admin.command(
                "hello"
            )
        except PyMongoError as error:
            pytest.fail(
                "R20R26_MONGO_RUNTIME_UNAVAILABLE:"
                + type(error).__name__,
                pytrace=False,
            )

        assert (
            hello.get("setName")
            == replica_set
        )

        assert hello.get(
            "isWritablePrimary",
            hello.get("ismaster"),
        ) is True

        address = client.address

        assert address is not None
        assert int(address[1]) != 27027

        database = client[
            "wilsy_p14_r20r26_"
            + uuid.uuid4().hex
        ]

        principals = database[
            PRINCIPAL_COLLECTION
        ]

        memberships = database[
            MEMBERSHIP_COLLECTION
        ]

        assignments = database[
            ROLE_ASSIGNMENT_COLLECTION
        ]

        iam_collection = database[
            IAM_COLLECTION_NAME
        ]

        completion_collection = database[
            COMPLETION_COLLECTION_NAME
        ]

        PrincipalAuthorityRepository.ensure_indexes(
            principals
        )

        TenantMembershipRepository.ensure_indexes(
            memberships
        )

        RoleAssignmentRepository.ensure_indexes(
            assignments
        )

        issuer = (
            TenantAuthorizationDecisionEvidenceRegistry(
                iam_collection,
                principal_repository=_PrincipalReader(
                    principals
                ),
                membership_repository=_MembershipReader(
                    memberships
                ),
                role_assignment_repository=_RoleReader(
                    assignments
                ),
                business_role_repository=_RoleReader(
                    assignments
                ),
            )
        )

        issuer.ensure_indexes()

        completion_registry = (
            LegalWorkCompletionEventRegistry(
                completion_collection
            )
        )

        completion_registry.ensure_indexes()

        yield (
            client,
            database,
            issuer,
            completion_registry,
        )

    finally:
        if database is not None:
            client.drop_database(
                database.name
            )

        client.close()


def _identity(
    suffix: str,
) -> tuple[
    str,
    str,
    str,
]:
    tenant = (
        "tenant-r20r26-"
        + suffix
    )

    principal = (
        "principal-r20r26-"
        + suffix
    )

    work_id = (
        "work-r20r26-"
        + suffix
    )

    return (
        tenant,
        principal,
        work_id,
    )


def _seed_iam(
    *,
    database: Any,
    tenant_id: str,
    principal_id: str,
    session: Any,
) -> None:
    PrincipalAuthorityRepository.create(
        PrincipalAuthority(
            principal_id,
            PrincipalStatus.ACTIVE,
            0,
        ),
        database[
            PRINCIPAL_COLLECTION
        ],
        session=session,
    )

    TenantMembershipRepository.insert(
        TenantMembershipAuthority(
            principal_id,
            tenant_id,
            TenantMembershipStatus.ACTIVE,
            1,
        ),
        database[
            MEMBERSHIP_COLLECTION
        ],
        session=session,
    )

    RoleAssignmentRepository.insert(
        RoleAssignmentAuthority(
            principal_id,
            tenant_id,
            BUSINESS_ROLE,
            RoleAssignmentStatus.ACTIVE,
            0,
        ),
        database[
            ROLE_ASSIGNMENT_COLLECTION
        ],
        session=session,
    )

    RoleAssignmentRepository.insert(
        RoleAssignmentAuthority(
            principal_id,
            tenant_id,
            AUTHORIZATION_ROLE,
            RoleAssignmentStatus.ACTIVE,
            0,
        ),
        database[
            ROLE_ASSIGNMENT_COLLECTION
        ],
        session=session,
    )


def _work(
    *,
    tenant_id: str,
    work_item_id: str,
) -> LegalWorkItem:
    return LegalWorkItem(
        work_item_id=work_item_id,
        tenant_id=tenant_id,
        case_matter_id=(
            "matter-"
            + work_item_id
        ),
        title="Complete governed legal work",
        source_kind="LEGAL_MATTER_WORKFLOW",
        source_reference=(
            "workflow:"
            + work_item_id
        ),
        source_evidence_fingerprint=SOURCE_FP,
        status=LegalWorkItemStatus.IN_PROGRESS,
        created_at=(
            EVALUATED_AT
            - timedelta(days=3)
        ),
    )


def _assignment(
    *,
    tenant_id: str,
    principal_id: str,
    work: LegalWorkItem,
) -> LegalWorkAssignment:
    return LegalWorkAssignment(
        assignment_id=(
            "assignment-"
            + work.work_item_id
        ),
        tenant_id=tenant_id,
        case_matter_id=work.case_matter_id,
        work_item_id=work.work_item_id,
        assignee_principal_id=principal_id,
        assigned_by_principal_id=(
            "principal-partner-r20r26"
        ),
        assigned_at=(
            EVALUATED_AT
            - timedelta(hours=2)
        ),
        assignment_reason_reference=(
            "matter-workflow-assignment:"
            + work.work_item_id
        ),
        authorization_evidence_reference=(
            "assignment-authorization:"
            + work.work_item_id
        ),
    )


def _record(
    *,
    issuer: TenantAuthorizationDecisionEvidenceRegistry,
    registry: LegalWorkCompletionEventRegistry,
    tenant_id: str,
    principal_id: str,
    work: LegalWorkItem,
    assignment: LegalWorkAssignment,
    session: Any,
    completion_reference: str,
    completion_fingerprint: str = COMPLETION_FP,
):
    return record_legal_work_completion(
        tenant_id=tenant_id,
        principal_id=principal_id,
        work_item=work,
        assignments=(
            assignment,
        ),
        completion_evidence_reference=(
            completion_reference
        ),
        completion_evidence_fingerprint=(
            completion_fingerprint
        ),
        evaluated_at=EVALUATED_AT,
        authorization_evidence_issuer=issuer,
        completion_registry=registry,
        session=session,
    )


def _seed_committed(
    client: MongoClient[Any],
    database: Any,
    *,
    tenant_id: str,
    principal_id: str,
) -> None:
    with client.start_session() as session:
        session.start_transaction()

        _seed_iam(
            database=database,
            tenant_id=tenant_id,
            principal_id=principal_id,
            session=session,
        )

        session.commit_transaction()


def test_real_runtime_is_writable_replica_set_and_never_27027(
    mongo_context: tuple[
        MongoClient[Any],
        Any,
        TenantAuthorizationDecisionEvidenceRegistry,
        LegalWorkCompletionEventRegistry,
    ],
) -> None:
    client, _, _, _ = mongo_context

    hello = client.admin.command(
        "hello"
    )

    assert hello.get(
        "isWritablePrimary",
        hello.get("ismaster"),
    ) is True

    assert client.address is not None
    assert int(client.address[1]) != 27027


def test_real_indexes_exist_and_neither_authority_nor_completion_has_ttl(
    mongo_context: tuple[
        MongoClient[Any],
        Any,
        TenantAuthorizationDecisionEvidenceRegistry,
        LegalWorkCompletionEventRegistry,
    ],
) -> None:
    _, database, _, _ = mongo_context

    for collection_name in (
        IAM_COLLECTION_NAME,
        COMPLETION_COLLECTION_NAME,
    ):
        indexes = tuple(
            database[
                collection_name
            ].list_indexes()
        )

        assert indexes

        for index in indexes:
            assert (
                "expireAfterSeconds"
                not in index
            )


def test_real_commit_persists_canonical_iam_and_completion_atomically(
    mongo_context: tuple[
        MongoClient[Any],
        Any,
        TenantAuthorizationDecisionEvidenceRegistry,
        LegalWorkCompletionEventRegistry,
    ],
) -> None:
    (
        client,
        database,
        issuer,
        registry,
    ) = mongo_context

    suffix = uuid.uuid4().hex

    tenant_id, principal_id, work_id = (
        _identity(suffix)
    )

    _seed_committed(
        client,
        database,
        tenant_id=tenant_id,
        principal_id=principal_id,
    )

    work = _work(
        tenant_id=tenant_id,
        work_item_id=work_id,
    )

    assignment = _assignment(
        tenant_id=tenant_id,
        principal_id=principal_id,
        work=work,
    )

    iam_collection = database[
        IAM_COLLECTION_NAME
    ]

    completion_collection = database[
        COMPLETION_COLLECTION_NAME
    ]

    assert iam_collection.count_documents(
        {}
    ) == 0

    assert completion_collection.count_documents(
        {}
    ) == 0

    with client.start_session() as session:
        session.start_transaction()

        event = _record(
            issuer=issuer,
            registry=registry,
            tenant_id=tenant_id,
            principal_id=principal_id,
            work=work,
            assignment=assignment,
            session=session,
            completion_reference=(
                "completion-source:"
                + work_id
            ),
        )

        assert event.tenant_id == tenant_id
        assert event.case_matter_id == (
            work.case_matter_id
        )
        assert event.work_item_id == work_id
        assert (
            event.work_item_fingerprint
            == work.fingerprint
        )
        assert (
            event.actor_principal_id
            == principal_id
        )
        assert (
            event.completed_at
            == EVALUATED_AT
        )

        assert (
            event.authorization_evidence_reference
            .startswith(
                "legal-work-completion-authority-evidence:"
            )
        )

        assert iam_collection.count_documents(
            {
                "tenant_id": tenant_id,
                "principal_id": principal_id,
                "operation": OPERATION,
                "permission": PERMISSION,
            },
            session=session,
        ) == 1

        assert completion_collection.count_documents(
            {
                "tenant_id": tenant_id,
                "work_item_id": work_id,
            },
            session=session,
        ) == 1

        session.commit_transaction()

    assert iam_collection.count_documents(
        {
            "tenant_id": tenant_id,
            "principal_id": principal_id,
            "operation": OPERATION,
            "permission": PERMISSION,
        }
    ) == 1

    assert completion_collection.count_documents(
        {
            "tenant_id": tenant_id,
            "work_item_id": work_id,
        }
    ) == 1


def test_real_abort_leaves_neither_iam_nor_completion_fact(
    mongo_context: tuple[
        MongoClient[Any],
        Any,
        TenantAuthorizationDecisionEvidenceRegistry,
        LegalWorkCompletionEventRegistry,
    ],
) -> None:
    (
        client,
        database,
        issuer,
        registry,
    ) = mongo_context

    suffix = uuid.uuid4().hex

    tenant_id, principal_id, work_id = (
        _identity(suffix)
    )

    _seed_committed(
        client,
        database,
        tenant_id=tenant_id,
        principal_id=principal_id,
    )

    work = _work(
        tenant_id=tenant_id,
        work_item_id=work_id,
    )

    assignment = _assignment(
        tenant_id=tenant_id,
        principal_id=principal_id,
        work=work,
    )

    iam_collection = database[
        IAM_COLLECTION_NAME
    ]

    completion_collection = database[
        COMPLETION_COLLECTION_NAME
    ]

    with client.start_session() as session:
        session.start_transaction()

        _record(
            issuer=issuer,
            registry=registry,
            tenant_id=tenant_id,
            principal_id=principal_id,
            work=work,
            assignment=assignment,
            session=session,
            completion_reference=(
                "completion-abort:"
                + work_id
            ),
        )

        assert iam_collection.count_documents(
            {
                "tenant_id": tenant_id,
                "principal_id": principal_id,
                "operation": OPERATION,
            },
            session=session,
        ) == 1

        assert completion_collection.count_documents(
            {
                "tenant_id": tenant_id,
                "work_item_id": work_id,
            },
            session=session,
        ) == 1

        session.abort_transaction()

    assert iam_collection.count_documents(
        {
            "tenant_id": tenant_id,
            "principal_id": principal_id,
            "operation": OPERATION,
        }
    ) == 0

    assert completion_collection.count_documents(
        {
            "tenant_id": tenant_id,
            "work_item_id": work_id,
        }
    ) == 0


def test_real_exact_replay_keeps_one_iam_and_one_completion_fact(
    mongo_context: tuple[
        MongoClient[Any],
        Any,
        TenantAuthorizationDecisionEvidenceRegistry,
        LegalWorkCompletionEventRegistry,
    ],
) -> None:
    (
        client,
        database,
        issuer,
        registry,
    ) = mongo_context

    suffix = uuid.uuid4().hex

    tenant_id, principal_id, work_id = (
        _identity(suffix)
    )

    _seed_committed(
        client,
        database,
        tenant_id=tenant_id,
        principal_id=principal_id,
    )

    work = _work(
        tenant_id=tenant_id,
        work_item_id=work_id,
    )

    assignment = _assignment(
        tenant_id=tenant_id,
        principal_id=principal_id,
        work=work,
    )

    reference = (
        "completion-replay:"
        + work_id
    )

    with client.start_session() as session:
        session.start_transaction()

        first = _record(
            issuer=issuer,
            registry=registry,
            tenant_id=tenant_id,
            principal_id=principal_id,
            work=work,
            assignment=assignment,
            session=session,
            completion_reference=reference,
        )

        session.commit_transaction()

    with client.start_session() as session:
        session.start_transaction()

        replay = _record(
            issuer=issuer,
            registry=registry,
            tenant_id=tenant_id,
            principal_id=principal_id,
            work=work,
            assignment=assignment,
            session=session,
            completion_reference=reference,
        )

        session.commit_transaction()

    assert replay == first

    assert database[
        IAM_COLLECTION_NAME
    ].count_documents(
        {
            "tenant_id": tenant_id,
            "principal_id": principal_id,
            "operation": OPERATION,
            "permission": PERMISSION,
        }
    ) == 1

    assert database[
        COMPLETION_COLLECTION_NAME
    ].count_documents(
        {
            "tenant_id": tenant_id,
            "work_item_id": work_id,
        }
    ) == 1


def test_certificate_contains_no_production_patch_hooks(
) -> None:
    import ast
    from pathlib import Path

    tree = ast.parse(
        Path(__file__).read_text(
            encoding="utf-8"
        )
    )

    for node in ast.walk(tree):
        if (
            isinstance(node, ast.Name)
            and node.id == "MagicMock"
        ):
            raise AssertionError(
                "MAGIC_MOCK_FORBIDDEN"
            )

        if (
            isinstance(node, ast.Attribute)
            and node.attr == "setattr"
            and isinstance(
                node.value,
                ast.Name,
            )
            and node.value.id == "monkeypatch"
        ):
            raise AssertionError(
                "PYTEST_MONKEYPATCH_SETATTR_FORBIDDEN"
            )
