"""Direct certificate for Legal Evidence provider cleanup command registry.

TITLE: Legal Evidence Provider Cleanup Command Registry Direct Certificate
VERSION: v1.0.1-L10A2R-C4D6E-A3-P3-P2-CLEANUP-COMMAND-REGISTRY-CERT
AUTHORITY: WILSY OS Core Governance / Python EOS Legal Operations
EPITOME: Certify exact durable cleanup-command persistence, replay, tenant
         isolation, corruption rejection and whole-transaction retry posture.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tests/unit/test_legal_evidence_provider_cleanup_command_registry.py
COLLABORATION / OWNERSHIP: Legal Operations / Legal Evidence
CERTIFICATION / UPDATE DATE: 2026-10-02
CHANGELOG:
    v1.0.1 certifies Mongo TransientTransactionError classification as a
    mandatory caller abort plus fresh whole-transaction restart boundary.
    v1.0.0 establishes direct unit certification for immutable command
    persistence, exact replay, four tenant-scoped unique identities, strict
    hydration, active transaction enforcement, duplicate-race retry posture,
    no TTL and no provider deletion execution.
AUTHORITY BOUNDARY:
    Test evidence only. Registry persistence is command-intent evidence and
    does not authorize or execute provider deletion.
TENANT BOUNDARY:
    Every durable identity and lookup is exact tenant scoped.
FINANCIAL AUTHORITY BOUNDARY:
    None. Kennel EOS remains the exclusive financial execution authority.
"""

from __future__ import annotations

from copy import deepcopy
from datetime import datetime, timezone
from hashlib import sha3_512
import json
from typing import Any

import pytest

from tools.eos.legal_operations.domain.legal_evidence_provider_cleanup_command import (
    LegalEvidenceProviderCleanupCommand,
    SCHEMA as COMMAND_SCHEMA,
    VERSION as COMMAND_VERSION,
)
from tools.eos.legal_operations.registry.legal_evidence_provider_cleanup_command_registry import (
    COLLECTION,
    INDEX_TENANT_CLEANUP_AUTHORIZATION,
    INDEX_TENANT_COMMAND_ID,
    INDEX_TENANT_FINGERPRINT,
    INDEX_TENANT_PROVIDER_OBJECT,
    VERSION,
    LegalEvidenceProviderCleanupCommandRegistry,
    LegalEvidenceProviderCleanupCommandRegistryIntegrityError,
    LegalEvidenceProviderCleanupCommandRegistryPersistenceError,
    LegalEvidenceProviderCleanupCommandRegistryRetryRequiredError,
    LegalEvidenceProviderCleanupCommandRegistryTransactionError,
)


TENANT = "tenant-p3-p2-cert"
OTHER_TENANT = "tenant-p3-p2-cert-other"


class DuplicateKeyError(Exception):
    """Mongo-shaped duplicate-key test error."""


class TransientTransactionError(Exception):
    """Mongo-shaped transient transaction test error."""

    def has_error_label(self, label: str) -> bool:
        return label == "TransientTransactionError"


class Session:
    """Minimal active-transaction test double."""

    def __init__(self, *, active: bool = True) -> None:
        self.in_transaction = active


class CallableSession:
    """Session whose transaction marker is callable."""

    def __init__(self, *, active: bool = True) -> None:
        self._active = active

    def in_transaction(self) -> bool:
        return self._active


class Collection:
    """Minimal deterministic Mongo-style collection test double."""

    def __init__(self) -> None:
        self.rows: list[dict[str, object]] = []
        self.indexes: list[
            tuple[list[tuple[str, int]], dict[str, object]]
        ] = []
        self.insert_failure: Exception | None = None
        self.find_failure: Exception | None = None
        self.sessions: list[object] = []

    def create_index(
        self,
        keys: list[tuple[str, int]],
        **kwargs: object,
    ) -> str | None:
        self.indexes.append((list(keys), dict(kwargs)))
        name = kwargs.get("name")
        return name if isinstance(name, str) else None

    def find_one(
        self,
        query: dict[str, object],
        *,
        session: object,
    ) -> dict[str, object] | None:
        self.sessions.append(session)

        if self.find_failure is not None:
            raise self.find_failure

        for row in self.rows:
            if all(
                row.get(key) == value
                for key, value in query.items()
            ):
                return deepcopy(row)

        return None

    def insert_one(
        self,
        document: dict[str, object],
        *,
        session: object,
    ) -> object:
        self.sessions.append(session)

        if self.insert_failure is not None:
            raise self.insert_failure

        self.rows.append(deepcopy(document))
        return object()


def _command(
    *,
    tenant_id: str = TENANT,
    command_id: str = "cleanup-command-p3-p2-cert",
    cleanup_authorization_id: str = "cleanup-auth-p3-p2-cert",
    provider_name: str = "aws_s3",
    storage_reference: str = "opaque/storage/p3-p2-cert",
    object_version_reference: str = "version-p3-p2-cert",
    reason_reference: str = "reason-p3-p2-cert",
) -> LegalEvidenceProviderCleanupCommand:
    payload: dict[str, object] = {
        "schema": COMMAND_SCHEMA,
        "command_version": COMMAND_VERSION,
        "command_id": command_id,
        "tenant_id": tenant_id,
        "principal_id": "principal-p3-p2-cert",
        "provider_name": provider_name,
        "storage_reference": storage_reference,
        "object_version_reference": object_version_reference,
        "cleanup_authorization_id": cleanup_authorization_id,
        "cleanup_authorization_fingerprint": "a" * 128,
        "tenant_authorization_decision_id": "decision-p3-p2-cert",
        "tenant_authorization_evidence_fingerprint": "b" * 128,
        "issued_at": datetime(
            2026,
            10,
            2,
            12,
            0,
            0,
            tzinfo=timezone.utc,
        ).isoformat(),
        "reason_reference": reason_reference,
    }

    raw = json.dumps(
        payload,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=True,
    ).encode("utf-8")

    payload["fingerprint"] = sha3_512(raw).hexdigest()

    return LegalEvidenceProviderCleanupCommand.from_dict(
        payload
    )


def _registry() -> tuple[
    Collection,
    LegalEvidenceProviderCleanupCommandRegistry,
]:
    collection = Collection()
    return (
        collection,
        LegalEvidenceProviderCleanupCommandRegistry(
            collection
        ),
    )


def test_registry_identity_version_collection_and_indexes() -> None:
    assert VERSION == (
        "v1.0.1-L10A2R-C4D6E-A3-P3-P2-"
        "CLEANUP-COMMAND-REGISTRY"
    )
    assert COLLECTION == (
        "legal_evidence_provider_cleanup_commands"
    )

    collection, registry = _registry()
    registry.ensure_indexes()

    assert len(collection.indexes) == 4

    names = {
        item[1]["name"]
        for item in collection.indexes
    }

    assert names == {
        INDEX_TENANT_COMMAND_ID,
        INDEX_TENANT_FINGERPRINT,
        INDEX_TENANT_CLEANUP_AUTHORIZATION,
        INDEX_TENANT_PROVIDER_OBJECT,
    }

    assert all(
        item[1]["unique"] is True
        for item in collection.indexes
    )

    assert all(
        "expireAfterSeconds" not in item[1]
        for item in collection.indexes
    )


def test_create_once_and_exact_replay() -> None:
    collection, registry = _registry()
    session = Session()
    value = _command()

    first = registry.create_or_replay(
        value,
        session=session,
    )
    second = registry.create_or_replay(
        value,
        session=session,
    )

    assert first == value
    assert second == value
    assert first.fingerprint == value.fingerprint
    assert second.fingerprint == value.fingerprint
    assert len(collection.rows) == 1
    assert collection.rows[0] == value.to_document()
    assert all(
        seen is session
        for seen in collection.sessions
    )


def test_all_exact_tenant_scoped_lookups() -> None:
    _, registry = _registry()
    session = Session()
    value = _command()

    registry.create_or_replay(
        value,
        session=session,
    )

    assert (
        registry.get_by_command_id(
            tenant_id=value.tenant_id,
            command_id=value.command_id,
            session=session,
        )
        == value
    )
    assert (
        registry.get_by_fingerprint(
            tenant_id=value.tenant_id,
            fingerprint=value.fingerprint,
            session=session,
        )
        == value
    )
    assert (
        registry.get_by_cleanup_authorization_id(
            tenant_id=value.tenant_id,
            cleanup_authorization_id=
                value.cleanup_authorization_id,
            session=session,
        )
        == value
    )
    assert (
        registry.get_by_provider_object(
            tenant_id=value.tenant_id,
            provider_name=value.provider_name,
            storage_reference=value.storage_reference,
            object_version_reference=
                value.object_version_reference,
            session=session,
        )
        == value
    )


def test_cross_tenant_reads_are_absent() -> None:
    _, registry = _registry()
    session = Session()
    value = _command()

    registry.create_or_replay(
        value,
        session=session,
    )

    assert registry.get_by_command_id(
        tenant_id=OTHER_TENANT,
        command_id=value.command_id,
        session=session,
    ) is None

    assert registry.get_by_fingerprint(
        tenant_id=OTHER_TENANT,
        fingerprint=value.fingerprint,
        session=session,
    ) is None

    assert registry.get_by_cleanup_authorization_id(
        tenant_id=OTHER_TENANT,
        cleanup_authorization_id=
            value.cleanup_authorization_id,
        session=session,
    ) is None

    assert registry.get_by_provider_object(
        tenant_id=OTHER_TENANT,
        provider_name=value.provider_name,
        storage_reference=value.storage_reference,
        object_version_reference=
            value.object_version_reference,
        session=session,
    ) is None


@pytest.mark.parametrize(
    "candidate",
    [
        lambda value: _command(
            command_id=value.command_id,
            reason_reference="different-reason",
        ),
        lambda value: _command(
            cleanup_authorization_id=
                value.cleanup_authorization_id,
            command_id="different-command",
            reason_reference="different-reason",
        ),
        lambda value: _command(
            command_id="different-command",
            cleanup_authorization_id=
                "different-cleanup-auth",
            provider_name=value.provider_name,
            storage_reference=value.storage_reference,
            object_version_reference=
                value.object_version_reference,
            reason_reference="different-reason",
        ),
    ],
)
def test_divergent_identity_collisions_reject(
    candidate,
) -> None:
    _, registry = _registry()
    session = Session()
    value = _command()

    registry.create_or_replay(
        value,
        session=session,
    )

    with pytest.raises(
        LegalEvidenceProviderCleanupCommandRegistryIntegrityError,
        match="REPLAY_CONFLICT",
    ):
        registry.create_or_replay(
            candidate(value),
            session=session,
        )


def test_wrong_domain_type_rejects() -> None:
    _, registry = _registry()

    with pytest.raises(
        LegalEvidenceProviderCleanupCommandRegistryIntegrityError,
        match="COMMAND_REQUIRED",
    ):
        registry.create_or_replay(
            object(),  # type: ignore[arg-type]
            session=Session(),
        )


@pytest.mark.parametrize(
    "session",
    [
        None,
        Session(active=False),
        CallableSession(active=False),
    ],
)
def test_missing_or_inactive_transaction_rejects(
    session: object | None,
) -> None:
    _, registry = _registry()

    with pytest.raises(
        LegalEvidenceProviderCleanupCommandRegistryTransactionError,
        match="ACTIVE_TRANSACTION_REQUIRED",
    ):
        registry.create_or_replay(
            _command(),
            session=session,
        )


def test_callable_active_transaction_is_supported() -> None:
    _, registry = _registry()
    session = CallableSession(active=True)
    value = _command()

    assert registry.create_or_replay(
        value,
        session=session,
    ) == value


def test_persisted_corruption_rejects() -> None:
    collection, registry = _registry()
    session = Session()
    value = _command()

    corrupted = value.to_document()
    corrupted["reason_reference"] = "tampered"
    collection.rows.append(corrupted)

    with pytest.raises(
        LegalEvidenceProviderCleanupCommandRegistryIntegrityError,
        match="PERSISTED_DOCUMENT_CORRUPT",
    ):
        registry.get_by_command_id(
            tenant_id=value.tenant_id,
            command_id=value.command_id,
            session=session,
        )


def test_durable_identity_conflict_rejects() -> None:
    collection, registry = _registry()
    session = Session()
    value = _command()

    requested = value.to_document()
    divergent = _command(
        command_id="different-command",
        cleanup_authorization_id=
            value.cleanup_authorization_id,
        storage_reference="different/storage",
        object_version_reference="different-version",
        reason_reference="different-reason",
    ).to_document()

    # Two individually valid rows deliberately claim different immutable
    # identities. Ordering makes the cleanup-authorization lookup resolve the
    # divergent row while command-id/fingerprint resolve the requested row.
    # The registry must reject the resulting multi-identity disagreement.
    collection.rows.extend(
        [
            divergent,
            requested,
        ]
    )

    with pytest.raises(
        LegalEvidenceProviderCleanupCommandRegistryIntegrityError,
        match="DURABLE_IDENTITY_CONFLICT",
    ):
        registry.create_or_replay(
            value,
            session=session,
        )


def test_duplicate_key_requires_fresh_whole_transaction_retry() -> None:
    collection, registry = _registry()
    collection.insert_failure = DuplicateKeyError(
        "duplicate"
    )

    with pytest.raises(
        LegalEvidenceProviderCleanupCommandRegistryRetryRequiredError,
        match="WHOLE_TRANSACTION_RETRY_REQUIRED",
    ):
        registry.create_or_replay(
            _command(),
            session=Session(),
        )


def test_transient_transaction_error_requires_fresh_whole_transaction_retry() -> None:
    collection, registry = _registry()
    collection.insert_failure = TransientTransactionError(
        "write conflict"
    )

    with pytest.raises(
        LegalEvidenceProviderCleanupCommandRegistryRetryRequiredError,
        match="WHOLE_TRANSACTION_RETRY_REQUIRED",
    ):
        registry.create_or_replay(
            _command(),
            session=Session(),
        )


def test_non_duplicate_insert_failure_rejects_as_persistence() -> None:
    collection, registry = _registry()
    collection.insert_failure = RuntimeError(
        "storage unavailable"
    )

    with pytest.raises(
        LegalEvidenceProviderCleanupCommandRegistryPersistenceError,
        match="INSERT_FAILED",
    ):
        registry.create_or_replay(
            _command(),
            session=Session(),
        )


def test_collection_interface_failure_rejects() -> None:
    collection, registry = _registry()
    collection.find_failure = TypeError(
        "invalid collection interface"
    )

    with pytest.raises(
        LegalEvidenceProviderCleanupCommandRegistryPersistenceError,
        match="COLLECTION_INTERFACE_INVALID",
    ):
        registry.create_or_replay(
            _command(),
            session=Session(),
        )


def test_no_provider_execution_or_ttl_authority_surface() -> None:
    _, registry = _registry()

    for attribute in (
        "delete",
        "delete_object",
        "delete_objects",
        "execute",
        "cleanup_execute",
    ):
        assert not hasattr(registry, attribute)


# ARTIFACT: test_legal_evidence_provider_cleanup_command_registry.py
# VERSION: v1.0.1-L10A2R-C4D6E-A3-P3-P2-CLEANUP-COMMAND-REGISTRY-CERT
# AUTHORITY BOUNDARY: direct durable command-registry certificate only
# TENANT POSTURE: every identity, replay and lookup is tenant scoped
# TRANSACTION POSTURE: caller-owned active transaction required
# IDEMPOTENCY POSTURE: exact immutable command replay only
# RETRY POSTURE: duplicate-key race requires fresh whole-transaction retry
# TTL POSTURE: no TTL deletion index
# PROVIDER MUTATION POSTURE: none
# DELETION EXECUTION POSTURE: none
# FAIL-CLOSED POSTURE: corruption, collision, transaction and persistence failures reject
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively
# END OF WILSY OS SOVEREIGN TEST ARTIFACT
