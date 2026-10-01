"""Direct certificate for durable provider-object orphan-proof registry.

VERSION: v1.0.2-L10A2R-C4D6D-B2-ORPHAN-PROOF-REGISTRY-CERT
AUTHORITY: WILSY OS Core Governance / Python EOS Legal Operations
CERTIFICATION / UPDATE DATE: 2026-10-01
CHANGELOG:
    v1.0.2-L10A2R-C4D6D-B2-ORPHAN-PROOF-REGISTRY-CERT replaces invalid
    dataclasses.replace-based divergence construction with two valid B1
    factory-issued divergent proofs for the same exact provider object,
    preserving production behavior and authority unchanged.
    v1.0.1-L10A2R-C4D6D-B2-ORPHAN-PROOF-REGISTRY-CERT corrects the direct
    certificate enumeration-kind import binding to the canonical
    LegalEvidenceProviderEnumerationKind symbol without changing production
    registry behavior or authority.
    v1.0.0-L10A2R-C4D6D-B2-ORPHAN-PROOF-REGISTRY-CERT certified exact
    collection/index identities, active caller-owned transaction enforcement,
    immutable exact replay, divergent provider-object re-proof rejection,
    strict B1 hydration, corruption rejection, duplicate-key whole-transaction
    retry, tenant isolation, zero TTL and explicit exclusion of
    deletion/provider/financial authority.
"""

from __future__ import annotations

from copy import deepcopy
from datetime import datetime, timedelta, timezone
from typing import Any

import pytest
from pymongo.errors import DuplicateKeyError

from tools.eos.legal_operations.domain.legal_evidence_provider_object_disownership import (
    LegalEvidenceProviderObjectDisownership,
)
from tools.eos.legal_operations.domain.legal_evidence_provider_object_orphan_proof import (
    LegalEvidenceProviderObjectOrphanProof,
    prove_legal_evidence_provider_object_orphan,
)
from tools.eos.legal_operations.registry.legal_evidence_provider_object_orphan_proof_registry import (
    COLLECTION,
    INDEX_TENANT_FINGERPRINT,
    INDEX_TENANT_PROVIDER_OBJECT,
    INDEX_TENANT_REFERENCE,
    LegalEvidenceProviderObjectOrphanProofConflictError,
    LegalEvidenceProviderObjectOrphanProofNotFoundError,
    LegalEvidenceProviderObjectOrphanProofPersistedRecordInvalidError,
    LegalEvidenceProviderObjectOrphanProofRegistry,
    LegalEvidenceProviderObjectOrphanProofTransactionRequiredError,
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
    LegalEvidenceProviderCoverageVerificationService,
)


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


class _Session:
    def __init__(
        self,
        *,
        in_transaction: bool,
    ) -> None:
        self.in_transaction = in_transaction


class _InsertResult:
    acknowledged = True


class _Collection:
    def __init__(self) -> None:
        self.rows: list[dict[str, object]] = []
        self.indexes: list[
            tuple[
                tuple[tuple[str, int], ...],
                dict[str, object],
            ]
        ] = []
        self.raise_duplicate = False

    def create_index(
        self,
        keys: list[tuple[str, int]],
        **kwargs: object,
    ) -> str:
        self.indexes.append(
            (
                tuple(keys),
                dict(kwargs),
            )
        )

        return str(
            kwargs.get(
                "name",
                "",
            )
        )

    def find_one(
        self,
        query: dict[str, object],
        *,
        session: Any,
    ) -> dict[str, object] | None:
        assert session.in_transaction is True

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
        session: Any,
    ) -> _InsertResult:
        assert session.in_transaction is True

        if self.raise_duplicate:
            self.raise_duplicate = False
            raise DuplicateKeyError(
                "duplicate"
            )

        self.rows.append(
            deepcopy(document)
        )

        return _InsertResult()


def _scope(
    *,
    tenant_id: str = "tenant-b2-cert",
) -> LegalEvidenceProviderDiscoveryScope:
    return LegalEvidenceProviderDiscoveryScope(
        tenant_id=tenant_id,
        tenant_scope_fingerprint=SHA_A,
    )


def _observation(
    *,
    tenant_id: str = "tenant-b2-cert",
    provider_name: str = "aws_s3",
    storage_reference: str = "legal-evidence/b2/object",
    object_version_reference: str = "version-b2",
) -> LegalEvidenceCompletedObjectObservation:
    return LegalEvidenceCompletedObjectObservation(
        tenant_id=tenant_id,
        provider_name=provider_name,
        storage_reference=storage_reference,
        object_version_reference=object_version_reference,
        provider_integrity_reference='"etag-b2"',
        content_length=17,
        last_modified_at=AT,
        observed_at=AT,
        write_intent_metadata_state=(
            LegalEvidenceCompletedObjectIntentMetadataState.ABSENT
        ),
        write_intent_fingerprint=None,
    )


def _page(
    *,
    scope: LegalEvidenceProviderDiscoveryScope,
    kind: LegalEvidenceProviderEnumerationKind,
    observations: tuple[Any, ...] = (),
) -> LegalEvidenceProviderEnumerationPage:
    return LegalEvidenceProviderEnumerationPage(
        tenant_id=scope.tenant_id,
        tenant_scope_fingerprint=scope.tenant_scope_fingerprint,
        provider_name="aws_s3",
        enumeration_kind=kind,
        observed_at=AT,
        observations=observations,
        next_page_reference=None,
    )


class _Provider:
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

        return _page(
            scope=scope,
            kind=(
                LegalEvidenceProviderEnumerationKind
                .INCOMPLETE_WRITE_SESSIONS
            ),
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

        return _page(
            scope=scope,
            kind=(
                LegalEvidenceProviderEnumerationKind
                .COMPLETED_OBJECT_VERSIONS
            ),
            observations=(
                self.observation,
            ),
        )


def _disownership(
    *,
    tenant_id: str = "tenant-b2-cert",
    provider_name: str = "aws_s3",
    storage_reference: str = "legal-evidence/b2/object",
    object_version_reference: str = "version-b2",
    reference: str = "disownership-b2",
) -> LegalEvidenceProviderObjectDisownership:
    return LegalEvidenceProviderObjectDisownership(
        tenant_id=tenant_id,
        provider_name=provider_name,
        storage_reference=storage_reference,
        object_version_reference=object_version_reference,
        disownership_reference=reference,
        reason_reference="reason:b2",
        source_evidence_reference="source:b2",
        source_evidence_fingerprint=SHA_A,
        authorization_evidence_reference="authorization:b2",
        authorization_evidence_fingerprint=SHA_B,
        decided_at=AT - timedelta(minutes=5),
    )


def _value(
    *,
    tenant_id: str = "tenant-b2-cert",
    provider_name: str = "aws_s3",
    storage_reference: str = "legal-evidence/b2/object",
    object_version_reference: str = "version-b2",
    orphan_proof_reference: str = "orphan-proof-b2",
    proved_at: datetime = AT + timedelta(minutes=1),
) -> LegalEvidenceProviderObjectOrphanProof:
    scope = _scope(
        tenant_id=tenant_id,
    )

    observation = _observation(
        tenant_id=tenant_id,
        provider_name=provider_name,
        storage_reference=storage_reference,
        object_version_reference=object_version_reference,
    )

    service = LegalEvidenceProviderCoverageVerificationService(
        provider=_Provider(
            scope=scope,
            observation=observation,
        )
    )

    verification = service.verify_coverage(
        scope=scope,
        provider_name=provider_name,
        observed_at=AT,
    )

    disownership = _disownership(
        tenant_id=tenant_id,
        provider_name=provider_name,
        storage_reference=storage_reference,
        object_version_reference=object_version_reference,
    )

    return prove_legal_evidence_provider_object_orphan(
        coverage_service=service,
        verification=verification,
        observation=observation,
        disownership=disownership,
        orphan_proof_reference=orphan_proof_reference,
        proved_at=proved_at,
    )


def _registry() -> tuple[
    LegalEvidenceProviderObjectOrphanProofRegistry,
    _Collection,
    _Session,
]:
    collection = _Collection()

    registry = (
        LegalEvidenceProviderObjectOrphanProofRegistry(
            collection
        )
    )

    session = _Session(
        in_transaction=True
    )

    return (
        registry,
        collection,
        session,
    )


def test_collection_identity_is_dedicated() -> None:
    assert (
        COLLECTION
        == "legal_evidence_provider_object_orphan_proofs"
    )


def test_indexes_are_exact_unique_and_have_no_ttl() -> None:
    registry, collection, _ = _registry()

    registry.ensure_indexes()

    by_name = {
        str(
            kwargs["name"]
        ): (
            keys,
            kwargs,
        )
        for keys, kwargs in collection.indexes
    }

    assert set(
        by_name
    ) == {
        INDEX_TENANT_REFERENCE,
        INDEX_TENANT_FINGERPRINT,
        INDEX_TENANT_PROVIDER_OBJECT,
    }

    reference = by_name[
        INDEX_TENANT_REFERENCE
    ]

    assert reference[0] == (
        ("tenant_id", 1),
        ("orphan_proof_reference", 1),
    )

    assert (
        reference[1]["unique"]
        is True
    )

    fingerprint = by_name[
        INDEX_TENANT_FINGERPRINT
    ]

    assert fingerprint[0] == (
        ("tenant_id", 1),
        ("fingerprint", 1),
    )

    assert (
        fingerprint[1]["unique"]
        is True
    )

    provider_object = by_name[
        INDEX_TENANT_PROVIDER_OBJECT
    ]

    assert provider_object[0] == (
        ("tenant_id", 1),
        ("provider_name", 1),
        ("storage_reference", 1),
        ("object_version_reference", 1),
    )

    assert (
        provider_object[1]["unique"]
        is True
    )

    assert all(
        "expireAfterSeconds"
        not in kwargs
        for _, kwargs in collection.indexes
    )


@pytest.mark.parametrize(
    "session",
    [
        None,
        _Session(
            in_transaction=False
        ),
    ],
)
def test_create_requires_active_caller_transaction(
    session: Any,
) -> None:
    registry, _, _ = _registry()

    with pytest.raises(
        LegalEvidenceProviderObjectOrphanProofTransactionRequiredError,
        match="L10A2R_C4D6D_B2_ACTIVE_TRANSACTION_REQUIRED",
    ):
        registry.create_or_replay(
            _value(),
            session=session,
        )


def test_create_and_exact_replay_return_same_value() -> None:
    registry, collection, session = _registry()
    value = _value()

    created = registry.create_or_replay(
        value,
        session=session,
    )

    replayed = registry.create_or_replay(
        value,
        session=session,
    )

    assert created == value
    assert replayed == value
    assert len(collection.rows) == 1


@pytest.mark.parametrize(
    (
        "orphan_proof_reference",
        "proved_at",
    ),
    [
        (
            "orphan-proof-divergent-reference",
            AT + timedelta(minutes=1),
        ),
        (
            "orphan-proof-divergent-proof-time",
            AT + timedelta(minutes=2),
        ),
    ],
)
def test_provider_object_divergence_rejects_without_second_row(
    orphan_proof_reference: str,
    proved_at: datetime,
) -> None:
    registry, collection, session = _registry()
    value = _value()

    registry.create_or_replay(
        value,
        session=session,
    )

    divergent = _value(
        orphan_proof_reference=orphan_proof_reference,
        proved_at=proved_at,
    )

    assert divergent != value
    assert divergent.fingerprint != value.fingerprint

    with pytest.raises(
        LegalEvidenceProviderObjectOrphanProofConflictError,
        match="L10A2R_C4D6D_B2_IMMUTABLE_DIVERGENCE",
    ):
        registry.create_or_replay(
            divergent,
            session=session,
        )

    assert len(collection.rows) == 1


def test_reference_reuse_for_other_provider_object_rejects() -> None:
    registry, collection, session = _registry()

    value = _value()

    registry.create_or_replay(
        value,
        session=session,
    )

    divergent = _value(
        storage_reference="legal-evidence/b2/other",
        object_version_reference="version-b2-other",
        orphan_proof_reference=value.orphan_proof_reference,
    )

    with pytest.raises(
        LegalEvidenceProviderObjectOrphanProofConflictError,
        match="L10A2R_C4D6D_B2_IMMUTABLE_DIVERGENCE",
    ):
        registry.create_or_replay(
            divergent,
            session=session,
        )

    assert len(collection.rows) == 1


def test_get_by_reference_and_provider_object_are_tenant_scoped() -> None:
    registry, _, session = _registry()

    value = _value()

    registry.create_or_replay(
        value,
        session=session,
    )

    assert (
        registry.get_by_reference(
            tenant_id=value.tenant_id,
            orphan_proof_reference=(
                value.orphan_proof_reference
            ),
            session=session,
        )
        == value
    )

    assert (
        registry.get_by_provider_object(
            tenant_id=value.tenant_id,
            provider_name=value.provider_name,
            storage_reference=value.storage_reference,
            object_version_reference=(
                value.object_version_reference
            ),
            session=session,
        )
        == value
    )

    with pytest.raises(
        LegalEvidenceProviderObjectOrphanProofNotFoundError,
        match="L10A2R_C4D6D_B2_NOT_FOUND",
    ):
        registry.get_by_reference(
            tenant_id="tenant-other",
            orphan_proof_reference=(
                value.orphan_proof_reference
            ),
            session=session,
        )

    with pytest.raises(
        LegalEvidenceProviderObjectOrphanProofNotFoundError,
        match="L10A2R_C4D6D_B2_NOT_FOUND",
    ):
        registry.get_by_provider_object(
            tenant_id="tenant-other",
            provider_name=value.provider_name,
            storage_reference=value.storage_reference,
            object_version_reference=(
                value.object_version_reference
            ),
            session=session,
        )


def test_persisted_record_round_trips_exact_b1_document() -> None:
    registry, collection, session = _registry()

    value = _value()

    registry.create_or_replay(
        value,
        session=session,
    )

    assert len(collection.rows) == 1
    assert collection.rows[0] == value.to_dict()

    loaded = registry.get_by_reference(
        tenant_id=value.tenant_id,
        orphan_proof_reference=(
            value.orphan_proof_reference
        ),
        session=session,
    )

    assert loaded == value
    assert loaded.to_dict() == value.to_dict()


def test_corrupt_persisted_record_rejects_without_healing() -> None:
    registry, collection, session = _registry()

    value = _value()

    registry.create_or_replay(
        value,
        session=session,
    )

    collection.rows[0][
        "coverage_verification_fingerprint"
    ] = "f" * 128

    corrupt = deepcopy(
        collection.rows[0]
    )

    with pytest.raises(
        LegalEvidenceProviderObjectOrphanProofPersistedRecordInvalidError,
        match="L10A2R_C4D6D_B2_PERSISTED_RECORD_INVALID",
    ):
        registry.get_by_reference(
            tenant_id=value.tenant_id,
            orphan_proof_reference=(
                value.orphan_proof_reference
            ),
            session=session,
        )

    assert collection.rows[0] == corrupt


def test_post_construction_value_tampering_rejects_before_write() -> None:
    registry, collection, session = _registry()

    value = _value()

    object.__setattr__(
        value,
        "fingerprint",
        "f" * 128,
    )

    with pytest.raises(
        LegalEvidenceProviderObjectOrphanProofPersistedRecordInvalidError,
        match="L10A2R_C4D6D_B2_VALUE_INVALID",
    ):
        registry.create_or_replay(
            value,
            session=session,
        )

    assert collection.rows == []


def test_duplicate_key_requires_whole_transaction_retry() -> None:
    registry, collection, session = _registry()

    collection.raise_duplicate = True

    with pytest.raises(
        LegalEvidenceProviderObjectOrphanProofConflictError,
        match="L10A2R_C4D6D_B2_WHOLE_TRANSACTION_RETRY_REQUIRED",
    ):
        registry.create_or_replay(
            _value(),
            session=session,
        )

    assert collection.rows == []


def test_registry_surface_has_no_delete_update_or_later_authority() -> None:
    forbidden = {
        "authorize_abort",
        "authorize_delete",
        "authorize_deletion",
        "delete",
        "delete_one",
        "delete_many",
        "delete_object",
        "delete_objects",
        "provider_delete",
        "release_legal_hold",
        "retention_satisfied",
        "update",
        "update_one",
        "update_many",
    }

    assert forbidden.isdisjoint(
        dir(
            LegalEvidenceProviderObjectOrphanProofRegistry
        )
    )


# ARTIFACT: test_legal_evidence_provider_object_orphan_proof_registry.py
# VERSION: v1.0.2-L10A2R-C4D6D-B2-ORPHAN-PROOF-REGISTRY-CERT
# AUTHORITY BOUNDARY: durable persistence/replay certificate only
# TRANSACTION POSTURE: active caller-owned transaction required
# REPLAY POSTURE: exact immutable replay only; divergent provider-object proof rejects
# CORRUPTION POSTURE: corrupt B1 durable evidence rejects without healing
# TTL POSTURE: zero TTL
# ORPHAN POSTURE: registry persists B1 proof only; absence is never orphan evidence
# RETENTION / HOLD POSTURE: no retention satisfaction or legal-hold release authority
# DELETION POSTURE: no abort/update/delete/provider mutation authority
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively
# END OF WILSY OS SOVEREIGN ARTIFACT
