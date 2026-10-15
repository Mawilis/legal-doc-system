"""
Direct certificate for P3 durable security-assurance evidence registry.
"""

from __future__ import annotations

from datetime import (
    datetime,
    timezone,
)

import pytest
from pymongo.errors import OperationFailure

from tools.eos.auth.privileged_security_assurance import (
    PrivilegedAssuranceChannel,
    PrivilegedAssurancePurpose,
    PrivilegedAssuranceReason,
)
from tools.eos.auth.privileged_security_assurance_evidence import (
    PrivilegedSecurityAssuranceEvidence,
)
from tools.eos.auth.privileged_security_assurance_evidence_registry import (
    ASSURANCE_EVIDENCE_ID_INDEX,
    PRINCIPAL_CHANNEL_TIMELINE_INDEX,
    PRINCIPAL_PURPOSE_TIMELINE_INDEX,
    SCOPE_IDEMPOTENCY_INDEX,
    PrivilegedSecurityAssuranceEvidenceConflictError,
    PrivilegedSecurityAssuranceEvidenceRegistry,
    PrivilegedSecurityAssuranceEvidenceTransactionRequiredError,
)


AT = datetime(
    2026,
    10,
    14,
    2,
    0,
    0,
    tzinfo=timezone.utc,
)


class _Result:
    pass


class _Session:
    def __init__(
        self,
        active: bool = True,
    ) -> None:
        self.in_transaction = active


class _Collection:
    def __init__(
        self,
    ) -> None:
        self.rows: list[dict] = []
        self.indexes: list[
            tuple[object, bool, str]
        ] = []

    def create_index(
        self,
        keys,
        *,
        unique=False,
        name,
    ):
        self.indexes.append(
            (
                keys,
                unique,
                name,
            )
        )

    def find_one(
        self,
        query,
        *,
        session=None,
    ):
        for row in self.rows:
            if all(
                row.get(key)
                == value
                for key, value
                in query.items()
            ):
                return dict(row)

        return None

    def insert_one(
        self,
        row,
        *,
        session=None,
    ):
        self.rows.append(
            dict(row)
        )

        return _Result()


def evidence(
    *,
    evidence_id="assurance-evidence-1",
    principal_id="principal-1",
    channel=(
        PrivilegedAssuranceChannel
        .INTERACTIVE_STRONG_AUTH
    ),
    purpose=(
        PrivilegedAssurancePurpose
        .PRIVILEGED_ELIGIBILITY_TO_ACTIVATION
    ),
    idempotency_key="idem-1",
    sufficient=True,
    reason=(
        PrivilegedAssuranceReason
        .SUFFICIENT
    ),
):
    interactive = (
        channel
        is PrivilegedAssuranceChannel
        .INTERACTIVE_STRONG_AUTH
    )

    return (
        PrivilegedSecurityAssuranceEvidence(
            assurance_evidence_id=
                evidence_id,
            principal_id=
                principal_id,
            assurance_channel=
                channel,
            assurance_purpose=
                purpose,
            principal_current=
                True,
            credential_current=
                True,
            assurance_proof_current=
                True,
            session_current=
                True
                if interactive
                else None,
            factor_verification_current=
                True
                if interactive
                else None,
            authentication_recency_current=
                True
                if interactive
                else None,
            workload_proof_current=
                None
                if interactive
                else True,
            workload_proof_reference=
                None
                if interactive
                else "workload-proof:1",
            sufficient=
                sufficient,
            reason=
                reason,
            evaluated_at=
                AT,
            idempotency_key=
                idempotency_key,
        )
    )


def test_exact_four_indexes_and_no_ttl() -> None:
    collection = _Collection()

    registry = (
        PrivilegedSecurityAssuranceEvidenceRegistry(
            collection
        )
    )

    registry.ensure_indexes()

    assert len(
        collection.indexes
    ) == 4

    by_name = {
        item[2]:
            item
        for item in collection.indexes
    }

    assert set(
        by_name
    ) == {
        ASSURANCE_EVIDENCE_ID_INDEX,
        SCOPE_IDEMPOTENCY_INDEX,
        PRINCIPAL_PURPOSE_TIMELINE_INDEX,
        PRINCIPAL_CHANNEL_TIMELINE_INDEX,
    }

    assert (
        by_name[
            ASSURANCE_EVIDENCE_ID_INDEX
        ][1]
        is True
    )

    assert (
        by_name[
            SCOPE_IDEMPOTENCY_INDEX
        ][1]
        is True
    )

    assert (
        by_name[
            PRINCIPAL_PURPOSE_TIMELINE_INDEX
        ][1]
        is False
    )

    assert (
        by_name[
            PRINCIPAL_CHANNEL_TIMELINE_INDEX
        ][1]
        is False
    )


def test_missing_transaction_rejects_before_write() -> None:
    collection = _Collection()

    registry = (
        PrivilegedSecurityAssuranceEvidenceRegistry(
            collection
        )
    )

    with pytest.raises(
        PrivilegedSecurityAssuranceEvidenceTransactionRequiredError
    ):
        registry.create_or_replay(
            evidence(),
            session=None,
        )

    assert collection.rows == []

def test_inactive_transaction_rejects_before_write() -> None:
    collection = _Collection()

    registry = (
        PrivilegedSecurityAssuranceEvidenceRegistry(
            collection
        )
    )

    with pytest.raises(
        PrivilegedSecurityAssuranceEvidenceTransactionRequiredError
    ):
        registry.create_or_replay(
            evidence(),
            session=_Session(
                False
            ),
        )

    assert collection.rows == []


def test_create_and_get_exact_identity() -> None:
    collection = _Collection()

    registry = (
        PrivilegedSecurityAssuranceEvidenceRegistry(
            collection
        )
    )

    value = evidence()

    created = registry.create_or_replay(
        value,
        session=_Session(),
    )

    assert created == value

    assert (
        registry.get(
            assurance_evidence_id=
                value.assurance_evidence_id
        )
        == value
    )


def test_exact_replay_returns_existing() -> None:
    collection = _Collection()

    registry = (
        PrivilegedSecurityAssuranceEvidenceRegistry(
            collection
        )
    )

    value = evidence()

    registry.create_or_replay(
        value,
        session=_Session(),
    )

    replay = registry.create_or_replay(
        value,
        session=_Session(),
    )

    assert replay == value
    assert len(collection.rows) == 1


def test_divergent_scoped_replay_rejects() -> None:
    collection = _Collection()

    registry = (
        PrivilegedSecurityAssuranceEvidenceRegistry(
            collection
        )
    )

    first = evidence()

    registry.create_or_replay(
        first,
        session=_Session(),
    )

    second = evidence(
        evidence_id=
            "assurance-evidence-2",
        sufficient=False,
        reason=(
            PrivilegedAssuranceReason
            .AUTHENTICATION_NOT_RECENT
        ),
    )

    with pytest.raises(
        PrivilegedSecurityAssuranceEvidenceConflictError
    ):
        registry.create_or_replay(
            second,
            session=_Session(),
        )

    assert len(collection.rows) == 1


def test_global_identity_collision_rejects() -> None:
    collection = _Collection()

    registry = (
        PrivilegedSecurityAssuranceEvidenceRegistry(
            collection
        )
    )

    first = evidence()

    registry.create_or_replay(
        first,
        session=_Session(),
    )

    second = evidence(
        principal_id=
            "principal-2",
        idempotency_key=
            "idem-2",
    )

    with pytest.raises(
        PrivilegedSecurityAssuranceEvidenceConflictError
    ):
        registry.create_or_replay(
            second,
            session=_Session(),
        )


def test_scope_distinguishes_channel() -> None:
    collection = _Collection()

    registry = (
        PrivilegedSecurityAssuranceEvidenceRegistry(
            collection
        )
    )

    first = evidence()

    second = evidence(
        evidence_id=
            "assurance-evidence-2",
        channel=(
            PrivilegedAssuranceChannel
            .NONINTERACTIVE_WORKLOAD_PROOF
        ),
    )

    registry.create_or_replay(
        first,
        session=_Session(),
    )

    registry.create_or_replay(
        second,
        session=_Session(),
    )

    assert len(collection.rows) == 2


def test_scope_distinguishes_purpose() -> None:
    collection = _Collection()

    registry = (
        PrivilegedSecurityAssuranceEvidenceRegistry(
            collection
        )
    )

    first = evidence()

    second = evidence(
        evidence_id=
            "assurance-evidence-2",
        purpose=(
            PrivilegedAssurancePurpose
            .PRIVILEGED_ACTIVATION_USE
        ),
    )

    registry.create_or_replay(
        first,
        session=_Session(),
    )

    registry.create_or_replay(
        second,
        session=_Session(),
    )

    assert len(collection.rows) == 2


def test_scope_distinguishes_principal() -> None:
    collection = _Collection()

    registry = (
        PrivilegedSecurityAssuranceEvidenceRegistry(
            collection
        )
    )

    first = evidence()

    second = evidence(
        evidence_id=
            "assurance-evidence-2",
        principal_id=
            "principal-2",
    )

    registry.create_or_replay(
        first,
        session=_Session(),
    )

    registry.create_or_replay(
        second,
        session=_Session(),
    )

    assert len(collection.rows) == 2


def test_corrupt_persisted_row_fails_closed() -> None:
    collection = _Collection()

    value = evidence()

    row = value.to_persisted()

    row[
        "assurance_evidence_fingerprint"
    ] = "f" * 128

    collection.rows.append(
        row
    )

    registry = (
        PrivilegedSecurityAssuranceEvidenceRegistry(
            collection
        )
    )

    from tools.eos.auth.privileged_security_assurance_evidence_registry import (
        PrivilegedSecurityAssuranceEvidencePersistedInvalidError,
    )

    with pytest.raises(
        PrivilegedSecurityAssuranceEvidencePersistedInvalidError
    ):
        registry.get(
            assurance_evidence_id=
                value.assurance_evidence_id
        )


def test_registry_surface_has_no_update_delete_or_purge() -> None:
    names = {
        name.casefold()
        for name
        in dir(
            PrivilegedSecurityAssuranceEvidenceRegistry
        )
    }

    for forbidden in (
        "update",
        "delete",
        "purge",
        "expire",
        "current",
    ):
        assert forbidden not in names


def test_historic_sufficient_row_is_readback_only() -> None:
    collection = _Collection()

    registry = (
        PrivilegedSecurityAssuranceEvidenceRegistry(
            collection
        )
    )

    value = evidence()

    registry.create_or_replay(
        value,
        session=_Session(),
    )

    historic = (
        registry.get_by_scope_idempotency(
            principal_id=
                value.principal_id,
            assurance_channel=
                value.assurance_channel.value,
            assurance_purpose=
                value.assurance_purpose.value,
            idempotency_key=
                value.idempotency_key,
        )
    )

    assert historic == value
    assert historic is not None
    assert historic.sufficient is True


def test_transient_transaction_error_label_is_preserved_for_host_retry() -> None:
    class _TransientCollection(_Collection):
        def insert_one(
            self,
            row,
            *,
            session=None,
        ):
            raise OperationFailure(
                "synthetic write conflict",
                code=112,
                details={
                    "code": 112,
                    "codeName": "WriteConflict",
                    "errorLabels": [
                        "TransientTransactionError",
                    ],
                },
            )

    collection = _TransientCollection()

    registry = (
        PrivilegedSecurityAssuranceEvidenceRegistry(
            collection
        )
    )

    error: OperationFailure | None = None

    try:
        registry.create_or_replay(
            evidence(),
            session=_Session(),
        )
    except OperationFailure as caught:
        error = caught

    assert error is not None

    assert error.has_error_label(
        "TransientTransactionError"
    )

    assert collection.rows == []
