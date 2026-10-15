"""
Direct certificate for P3-R3B durable interactive security-proof registry.
"""

from datetime import (
    datetime,
    timedelta,
    timezone,
)

import pytest

from tools.eos.auth.privileged_interactive_security_proof import (
    PrivilegedInteractiveProofStatus,
    PrivilegedInteractiveSecurityProof,
)
from tools.eos.auth.privileged_interactive_security_proof_registry import (
    FACTOR_REFERENCE_REVISION_INDEX,
    PRINCIPAL_AUTHENTICATED_TIMELINE_INDEX,
    PROOF_IDEMPOTENCY_INDEX,
    PROOF_REFERENCE_REVISION_INDEX,
    PROOF_REVISION_INDEX,
    SESSION_REVISION_INDEX,
    STATUS_CHANGED_TIMELINE_INDEX,
    PrivilegedInteractiveSecurityProofConflictError,
    PrivilegedInteractiveSecurityProofPersistedInvalidError,
    PrivilegedInteractiveSecurityProofRegistry,
    PrivilegedInteractiveSecurityProofTransactionRequiredError,
)


AT = datetime(
    2026,
    10,
    14,
    5,
    0,
    0,
    123456,
    tzinfo=timezone.utc,
)

LATER = AT + timedelta(
    minutes=1
)


class _Result:
    pass


class _Session:
    def __init__(
        self,
        active: bool = True,
    ) -> None:
        self.in_transaction = active


class _Cursor:
    def __init__(
        self,
        rows,
    ) -> None:
        self.rows = list(
            rows
        )

    def sort(
        self,
        field,
        direction,
    ):
        reverse = (
            direction < 0
        )

        self.rows.sort(
            key=lambda row:
                row[field],
            reverse=reverse,
        )

        return self

    def __iter__(
        self,
    ):
        return iter(
            self.rows
        )


class _Collection:
    def __init__(
        self,
    ) -> None:
        self.rows: list[dict] = []
        self.indexes: list[
            tuple[object, bool, str]
        ] = []
        self.index_options: dict[
            str,
            dict[str, object],
        ] = {}

    def create_index(
        self,
        keys,
        *,
        unique=False,
        name,
        partialFilterExpression=None,
    ):
        self.indexes.append(
            (
                keys,
                unique,
                name,
            )
        )
        self.index_options[name] = {
            "unique": unique,
            "partialFilterExpression":
                partialFilterExpression,
        }

    def find_one(
        self,
        query,
        *,
        session=None,
        sort=None,
    ):
        rows = [
            row
            for row in self.rows
            if all(
                row.get(key)
                == value
                for key, value
                in query.items()
            )
        ]

        if sort:
            for field, direction in reversed(
                sort
            ):
                rows.sort(
                    key=lambda row:
                        row[field],
                    reverse=(
                        direction < 0
                    ),
                )

        if not rows:
            return None

        return dict(
            rows[0]
        )

    def find(
        self,
        query,
        *,
        session=None,
    ):
        return _Cursor(
            [
                dict(row)
                for row in self.rows
                if all(
                    row.get(key)
                    == value
                    for key, value
                    in query.items()
                )
            ]
        )

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


def proof(
    *,
    proof_id="proof-1",
    principal_id="principal-1",
    factor_reference="factor-1",
    session_reference="session-1",
    proof_reference="proof-reference-1",
    status=(
        PrivilegedInteractiveProofStatus
        .VERIFIED
    ),
):
    return (
        PrivilegedInteractiveSecurityProof(
            proof_id=
                proof_id,
            principal_id=
                principal_id,
            factor_verification_reference=
                factor_reference,
            authenticated_at=
                AT,
            credential_revision=
                7,
            session_reference=
                session_reference,
            proof_status=
                status,
            proof_reference=
                proof_reference,
        )
    )


def registry():
    collection = _Collection()

    return (
        collection,
        PrivilegedInteractiveSecurityProofRegistry(
            collection
        ),
    )


def create(
    value=None,
    *,
    idempotency_key="create-1",
):
    collection, reg = registry()

    snapshot = reg.create_or_replay(
        value or proof(),
        status_changed_at=AT,
        idempotency_key=
            idempotency_key,
        session=_Session(),
    )

    return (
        collection,
        reg,
        snapshot,
    )


def test_exact_seven_indexes_and_no_ttl() -> None:
    collection, reg = registry()

    reg.ensure_indexes()

    assert len(
        collection.indexes
    ) == 9

    by_name = {
        item[2]:
            item
        for item in collection.indexes
    }

    assert (
        by_name[
            "privileged_interactive_proof_reference_initial_identity"
        ][1]
        is True
    )

    assert (
        collection.index_options[
            "privileged_interactive_proof_reference_initial_identity"
        ]["partialFilterExpression"]
        == {"revision": 1}
    )

    assert (
        by_name[
            "privileged_interactive_factor_reference_initial_identity"
        ][1]
        is True
    )

    assert (
        collection.index_options[
            "privileged_interactive_factor_reference_initial_identity"
        ]["partialFilterExpression"]
        == {"revision": 1}
    )


    assert set(
        by_name
    ) == {
        "privileged_interactive_proof_reference_initial_identity",
        "privileged_interactive_factor_reference_initial_identity",
        PROOF_REVISION_INDEX,
        PROOF_REFERENCE_REVISION_INDEX,
        FACTOR_REFERENCE_REVISION_INDEX,
        PROOF_IDEMPOTENCY_INDEX,
        PRINCIPAL_AUTHENTICATED_TIMELINE_INDEX,
        SESSION_REVISION_INDEX,
        STATUS_CHANGED_TIMELINE_INDEX,
    }

    assert (
        by_name[
            PROOF_REVISION_INDEX
        ][1]
        is True
    )

    assert (
        by_name[
            PROOF_REFERENCE_REVISION_INDEX
        ][1]
        is True
    )

    assert (
        by_name[
            FACTOR_REFERENCE_REVISION_INDEX
        ][1]
        is True
    )

    assert (
        by_name[
            PROOF_IDEMPOTENCY_INDEX
        ][1]
        is True
    )


def test_missing_transaction_rejects_create() -> None:
    collection, reg = registry()

    with pytest.raises(
        PrivilegedInteractiveSecurityProofTransactionRequiredError
    ):
        reg.create_or_replay(
            proof(),
            status_changed_at=AT,
            idempotency_key=
                "create-1",
            session=None,
        )

    assert collection.rows == []


def test_inactive_transaction_rejects_create() -> None:
    collection, reg = registry()

    with pytest.raises(
        PrivilegedInteractiveSecurityProofTransactionRequiredError
    ):
        reg.create_or_replay(
            proof(),
            status_changed_at=AT,
            idempotency_key=
                "create-1",
            session=_Session(False),
        )

    assert collection.rows == []


def test_initial_create_is_revision_one_verified() -> None:
    collection, reg, snapshot = create()

    assert snapshot.revision == 1

    assert (
        snapshot.proof.proof_status
        is PrivilegedInteractiveProofStatus
        .VERIFIED
    )

    assert (
        snapshot.previous_snapshot_fingerprint
        is None
    )

    assert (
        len(
            snapshot.snapshot_fingerprint
        )
        == 128
    )

    assert (
        collection.rows[0][
            "snapshot_fingerprint"
        ]
        == snapshot.snapshot_fingerprint
    )


def test_initial_nonverified_status_rejects() -> None:
    collection, reg = registry()

    with pytest.raises(
        PrivilegedInteractiveSecurityProofConflictError
    ):
        reg.create_or_replay(
            proof(
                status=(
                    PrivilegedInteractiveProofStatus
                    .REVOKED
                )
            ),
            status_changed_at=AT,
            idempotency_key=
                "create-1",
            session=_Session(),
        )

    assert collection.rows == []


def test_exact_create_replay_returns_existing() -> None:
    collection, reg, first = create()

    replay = reg.create_or_replay(
        proof(),
        status_changed_at=AT,
        idempotency_key=
            "create-1",
        session=_Session(),
    )

    assert replay == first

    assert len(
        collection.rows
    ) == 1


def test_divergent_create_replay_rejects() -> None:
    collection, reg, _ = create()

    with pytest.raises(
        PrivilegedInteractiveSecurityProofConflictError
    ):
        reg.create_or_replay(
            proof(
                principal_id=
                    "principal-2"
            ),
            status_changed_at=AT,
            idempotency_key=
                "create-1",
            session=_Session(),
        )

    assert len(
        collection.rows
    ) == 1


def test_proof_id_collision_rejects() -> None:
    collection, reg, _ = create()

    with pytest.raises(
        PrivilegedInteractiveSecurityProofConflictError
    ):
        reg.create_or_replay(
            proof(
                principal_id=
                    "principal-2",
                factor_reference=
                    "factor-2",
                session_reference=
                    "session-2",
                proof_reference=
                    "proof-reference-2",
            ),
            status_changed_at=AT,
            idempotency_key=
                "create-2",
            session=_Session(),
        )

    assert len(
        collection.rows
    ) == 1


def test_proof_reference_collision_rejects() -> None:
    collection, reg, _ = create()

    with pytest.raises(
        PrivilegedInteractiveSecurityProofConflictError
    ):
        reg.create_or_replay(
            proof(
                proof_id=
                    "proof-2",
                principal_id=
                    "principal-2",
                factor_reference=
                    "factor-2",
                session_reference=
                    "session-2",
            ),
            status_changed_at=AT,
            idempotency_key=
                "create-2",
            session=_Session(),
        )

    assert len(
        collection.rows
    ) == 1


def test_factor_reference_collision_rejects() -> None:
    collection, reg, _ = create()

    with pytest.raises(
        PrivilegedInteractiveSecurityProofConflictError
    ):
        reg.create_or_replay(
            proof(
                proof_id=
                    "proof-2",
                principal_id=
                    "principal-2",
                session_reference=
                    "session-2",
                proof_reference=
                    "proof-reference-2",
            ),
            status_changed_at=AT,
            idempotency_key=
                "create-2",
            session=_Session(),
        )

    assert len(
        collection.rows
    ) == 1


@pytest.mark.parametrize(
    "target",
    (
        PrivilegedInteractiveProofStatus
        .REVOKED,
        PrivilegedInteractiveProofStatus
        .INVALIDATED,
    ),
)
def test_verified_can_transition_to_terminal(
    target,
) -> None:
    collection, reg, first = create()

    second = reg.transition_status(
        proof_id=
            first.proof.proof_id,
        target_status=
            target,
        status_changed_at=
            LATER,
        idempotency_key=
            "transition-1",
        expected_revision=
            first.revision,
        expected_snapshot_fingerprint=
            first.snapshot_fingerprint,
        session=_Session(),
    )

    assert second.revision == 2

    assert (
        second.proof.proof_status
        is target
    )

    assert (
        second.previous_snapshot_fingerprint
        == first.snapshot_fingerprint
    )

    assert len(
        collection.rows
    ) == 2


def test_terminal_status_has_no_successor() -> None:
    collection, reg, first = create()

    second = reg.transition_status(
        proof_id=
            first.proof.proof_id,
        target_status=(
            PrivilegedInteractiveProofStatus
            .REVOKED
        ),
        status_changed_at=
            LATER,
        idempotency_key=
            "transition-1",
        expected_revision=
            first.revision,
        expected_snapshot_fingerprint=
            first.snapshot_fingerprint,
        session=_Session(),
    )

    with pytest.raises(
        PrivilegedInteractiveSecurityProofConflictError
    ):
        reg.transition_status(
            proof_id=
                second.proof.proof_id,
            target_status=(
                PrivilegedInteractiveProofStatus
                .INVALIDATED
            ),
            status_changed_at=
                LATER
                + timedelta(
                    seconds=1
                ),
            idempotency_key=
                "transition-2",
            expected_revision=
                second.revision,
            expected_snapshot_fingerprint=
                second.snapshot_fingerprint,
            session=_Session(),
        )

    assert len(
        collection.rows
    ) == 2


def test_transition_exact_replay_returns_existing() -> None:
    collection, reg, first = create()

    kwargs = {
        "proof_id":
            first.proof.proof_id,
        "target_status":
            PrivilegedInteractiveProofStatus
            .REVOKED,
        "status_changed_at":
            LATER,
        "idempotency_key":
            "transition-1",
        "expected_revision":
            first.revision,
        "expected_snapshot_fingerprint":
            first.snapshot_fingerprint,
        "session":
            _Session(),
    }

    second = reg.transition_status(
        **kwargs
    )

    replay = reg.transition_status(
        **kwargs
    )

    assert replay == second

    assert len(
        collection.rows
    ) == 2


def test_transition_divergent_replay_rejects() -> None:
    collection, reg, first = create()

    reg.transition_status(
        proof_id=
            first.proof.proof_id,
        target_status=(
            PrivilegedInteractiveProofStatus
            .REVOKED
        ),
        status_changed_at=
            LATER,
        idempotency_key=
            "transition-1",
        expected_revision=
            first.revision,
        expected_snapshot_fingerprint=
            first.snapshot_fingerprint,
        session=_Session(),
    )

    with pytest.raises(
        PrivilegedInteractiveSecurityProofConflictError
    ):
        reg.transition_status(
            proof_id=
                first.proof.proof_id,
            target_status=(
                PrivilegedInteractiveProofStatus
                .INVALIDATED
            ),
            status_changed_at=
                LATER,
            idempotency_key=
                "transition-1",
            expected_revision=
                first.revision,
            expected_snapshot_fingerprint=
                first.snapshot_fingerprint,
            session=_Session(),
        )

    assert len(
        collection.rows
    ) == 2


def test_stale_expected_revision_rejects() -> None:
    collection, reg, first = create()

    with pytest.raises(
        PrivilegedInteractiveSecurityProofConflictError
    ):
        reg.transition_status(
            proof_id=
                first.proof.proof_id,
            target_status=(
                PrivilegedInteractiveProofStatus
                .REVOKED
            ),
            status_changed_at=
                LATER,
            idempotency_key=
                "transition-1",
            expected_revision=2,
            expected_snapshot_fingerprint=
                first.snapshot_fingerprint,
            session=_Session(),
        )

    assert len(
        collection.rows
    ) == 1


def test_stale_fingerprint_rejects() -> None:
    collection, reg, first = create()

    with pytest.raises(
        PrivilegedInteractiveSecurityProofConflictError
    ):
        reg.transition_status(
            proof_id=
                first.proof.proof_id,
            target_status=(
                PrivilegedInteractiveProofStatus
                .REVOKED
            ),
            status_changed_at=
                LATER,
            idempotency_key=
                "transition-1",
            expected_revision=
                first.revision,
            expected_snapshot_fingerprint=
                "f" * 128,
            session=_Session(),
        )

    assert len(
        collection.rows
    ) == 1


def test_reads_by_explicit_authority() -> None:
    collection, reg, first = create()

    by_id = reg.get_current_by_proof_id(
        proof_id=
            first.proof.proof_id
    )

    by_reference = (
        reg.get_current_by_proof_reference(
            proof_reference=
                first.proof.proof_reference
        )
    )

    by_factor = (
        reg.get_current_by_factor_reference(
            factor_verification_reference=
                first
                .proof
                .factor_verification_reference
        )
    )

    assert by_id == first
    assert by_reference == first
    assert by_factor == first


def test_history_is_revision_ordered() -> None:
    collection, reg, first = create()

    second = reg.transition_status(
        proof_id=
            first.proof.proof_id,
        target_status=(
            PrivilegedInteractiveProofStatus
            .REVOKED
        ),
        status_changed_at=
            LATER,
        idempotency_key=
            "transition-1",
        expected_revision=
            first.revision,
        expected_snapshot_fingerprint=
            first.snapshot_fingerprint,
        session=_Session(),
    )

    history = reg.get_history_by_proof_id(
        proof_id=
            first.proof.proof_id
    )

    assert history == (
        first,
        second,
    )


def test_corrupt_fingerprint_fails_closed() -> None:
    collection, reg, first = create()

    collection.rows[0][
        "snapshot_fingerprint"
    ] = "f" * 128

    with pytest.raises(
        PrivilegedInteractiveSecurityProofPersistedInvalidError
    ):
        reg.get_current_by_proof_id(
            proof_id=
                first.proof.proof_id
        )


def test_broken_previous_fingerprint_fails_closed() -> None:
    collection, reg, first = create()

    reg.transition_status(
        proof_id=
            first.proof.proof_id,
        target_status=(
            PrivilegedInteractiveProofStatus
            .REVOKED
        ),
        status_changed_at=
            LATER,
        idempotency_key=
            "transition-1",
        expected_revision=
            first.revision,
        expected_snapshot_fingerprint=
            first.snapshot_fingerprint,
        session=_Session(),
    )

    collection.rows[1][
        "previous_snapshot_fingerprint"
    ] = "f" * 128

    with pytest.raises(
        PrivilegedInteractiveSecurityProofPersistedInvalidError
    ):
        reg.get_history_by_proof_id(
            proof_id=
                first.proof.proof_id
        )


def test_registry_has_no_ambient_principal_or_session_current_read() -> None:
    names = set(
        dir(
            PrivilegedInteractiveSecurityProofRegistry
        )
    )

    assert (
        "get_current_by_principal"
        not in names
    )

    assert (
        "get_current_by_session"
        not in names
    )

    assert (
        "get_current_by_principal_and_session"
        not in names
    )


def test_registry_surface_has_no_update_delete_or_ttl() -> None:
    names = {
        name.casefold()
        for name in dir(
            PrivilegedInteractiveSecurityProofRegistry
        )
    }

    for forbidden in (
        "update",
        "delete",
        "purge",
        "expire",
    ):
        assert forbidden not in names


def test_registry_owns_no_external_currentness_or_authority() -> None:
    import inspect
    import tools.eos.auth.privileged_interactive_security_proof_registry as module

    source = inspect.getsource(
        module
    )

    forbidden = (
        "verify_totp",
        "verify_otp",
        "verify_webauthn",
        "verify_passkey",
        "get_credential_revision",
        "validate_session",
        "evaluate_privileged_security_assurance(",
        "privileged_activation",
        "break_glass",
        "financial_execution",
        "expireAfterSeconds",
    )

    for token in forbidden:
        assert token not in source
