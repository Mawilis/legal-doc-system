from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

import pytest

from tools.eos.auth.privileged_channel_currentness import (
    FactorVerificationStatus,
    InteractiveFactorVerificationEvent,
    WorkloadTrustFact,
    WorkloadTrustStatus,
)
from tools.eos.auth.privileged_factor_verification_currentness_registry import (
    FactorCurrentnessConflictError,
    FactorCurrentnessPersistenceError,
    PrivilegedFactorVerificationCurrentnessRegistry,
)
from tools.eos.auth.privileged_workload_trust_currentness_registry import (
    PrivilegedWorkloadTrustCurrentnessRegistry,
    WorkloadTrustConflictError,
    WorkloadTrustPersistenceError,
)


NOW = datetime(
    2026,
    10,
    14,
    5,
    30,
    tzinfo=timezone.utc,
)


class Result:
    def __init__(
        self,
        matched: int,
        modified: int,
    ) -> None:
        self.matched_count = matched
        self.modified_count = modified


class Session:
    in_transaction = True


class InactiveSession:
    in_transaction = False


class Collection:
    def __init__(self) -> None:
        self.rows: list[dict[str, Any]] = []
        self.indexes: list[
            tuple[object, bool, str]
        ] = []

    def create_index(
        self,
        keys: object,
        *,
        unique: bool,
        name: str,
    ) -> str:
        self.indexes.append(
            (
                keys,
                unique,
                name,
            )
        )
        return name

    def find_one(
        self,
        query: dict[str, object],
        *,
        session: object = None,
    ) -> object:
        del session

        for row in self.rows:
            if all(
                row.get(key) == value
                for key, value in query.items()
            ):
                return dict(row)

        return None

    def insert_one(
        self,
        row: dict[str, object],
        *,
        session: object,
    ) -> object:
        del session

        for current in self.rows:
            if (
                current.get(
                    "factor_verification_reference"
                )
                is not None
                and current.get(
                    "factor_verification_reference"
                )
                == row.get(
                    "factor_verification_reference"
                )
            ):
                raise AssertionError(
                    "fake duplicate"
                )

            if (
                current.get(
                    "proof_reference"
                )
                is not None
                and current.get(
                    "proof_reference"
                )
                == row.get(
                    "proof_reference"
                )
            ):
                raise AssertionError(
                    "fake duplicate"
                )

            if (
                current.get(
                    "credential_or_attestation_reference"
                )
                is not None
                and current.get(
                    "credential_or_attestation_reference"
                )
                == row.get(
                    "credential_or_attestation_reference"
                )
            ):
                raise AssertionError(
                    "fake duplicate"
                )

        self.rows.append(
            dict(row)
        )

        return object()

    def update_one(
        self,
        query: dict[str, object],
        update: dict[str, dict[str, object]],
        *,
        session: object,
    ) -> Result:
        del session

        for row in self.rows:
            if all(
                row.get(key) == value
                for key, value in query.items()
            ):
                for key, value in update[
                    "$set"
                ].items():
                    row[key] = value

                return Result(
                    1,
                    1,
                )

        return Result(
            0,
            0,
        )


def factor_event(
    reference: str = "factor-1",
) -> InteractiveFactorVerificationEvent:
    return InteractiveFactorVerificationEvent(
        factor_verification_reference=
            reference,
        principal_id=
            "principal-1",
        session_reference=
            "WILSYSESSION-1",
        credential_revision=7,
        authenticated_at=NOW,
        status=
            FactorVerificationStatus
            .VERIFIED,
    )


def workload_fact(
    proof: str = "proof-1",
    credential: str = "attestation-1",
) -> WorkloadTrustFact:
    return WorkloadTrustFact(
        proof_reference=
            proof,
        principal_id=
            "machine-1",
        credential_or_attestation_reference=
            credential,
        observed_at=NOW,
        status=
            WorkloadTrustStatus.CURRENT,
    )


def test_factor_indexes_are_exact_and_no_ttl() -> None:
    collection = Collection()

    registry = (
        PrivilegedFactorVerificationCurrentnessRegistry(
            collection
        )
    )

    registry.ensure_indexes()

    assert len(
        collection.indexes
    ) == 3

    assert all(
        "expireAfterSeconds"
        not in repr(index)
        for index in collection.indexes
    )


def test_factor_requires_active_transaction() -> None:
    registry = (
        PrivilegedFactorVerificationCurrentnessRegistry(
            Collection()
        )
    )

    with pytest.raises(
        FactorCurrentnessPersistenceError
    ):
        registry.create_or_replay(
            factor_event(),
            recorded_at=NOW,
            session=InactiveSession(),
        )


def test_factor_create_replay_and_exact_read() -> None:
    registry = (
        PrivilegedFactorVerificationCurrentnessRegistry(
            Collection()
        )
    )

    tx = Session()
    event = factor_event()

    assert (
        registry.create_or_replay(
            event,
            recorded_at=NOW,
            session=tx,
        )
        == event
    )

    assert (
        registry.create_or_replay(
            event,
            recorded_at=NOW,
            session=tx,
        )
        == event
    )

    assert (
        registry.get(
            factor_verification_reference=
                "factor-1",
            session=tx,
        )
        == event
    )


def test_factor_reference_collision_rejected() -> None:
    registry = (
        PrivilegedFactorVerificationCurrentnessRegistry(
            Collection()
        )
    )

    tx = Session()

    registry.create_or_replay(
        factor_event(),
        recorded_at=NOW,
        session=tx,
    )

    divergent = (
        InteractiveFactorVerificationEvent(
            factor_verification_reference=
                "factor-1",
            principal_id=
                "principal-2",
            session_reference=
                "WILSYSESSION-2",
            credential_revision=2,
            authenticated_at=NOW,
            status=
                FactorVerificationStatus
                .VERIFIED,
        )
    )

    with pytest.raises(
        FactorCurrentnessConflictError
    ):
        registry.create_or_replay(
            divergent,
            recorded_at=NOW,
            session=tx,
        )


def test_factor_terminal_transition_and_replay() -> None:
    registry = (
        PrivilegedFactorVerificationCurrentnessRegistry(
            Collection()
        )
    )

    tx = Session()

    registry.create_or_replay(
        factor_event(),
        recorded_at=NOW,
        session=tx,
    )

    first = registry.terminate(
        factor_verification_reference=
            "factor-1",
        target_status=
            FactorVerificationStatus
            .REVOKED,
        session=tx,
    )

    second = registry.terminate(
        factor_verification_reference=
            "factor-1",
        target_status=
            FactorVerificationStatus
            .REVOKED,
        session=tx,
    )

    assert first == second
    assert (
        first.status
        is FactorVerificationStatus.REVOKED
    )


def test_workload_indexes_exact_and_no_ttl() -> None:
    collection = Collection()

    registry = (
        PrivilegedWorkloadTrustCurrentnessRegistry(
            collection
        )
    )

    registry.ensure_indexes()

    assert len(
        collection.indexes
    ) == 3

    assert all(
        "expireAfterSeconds"
        not in repr(index)
        for index in collection.indexes
    )


def test_workload_requires_active_transaction() -> None:
    registry = (
        PrivilegedWorkloadTrustCurrentnessRegistry(
            Collection()
        )
    )

    with pytest.raises(
        WorkloadTrustPersistenceError
    ):
        registry.create_or_replay(
            workload_fact(),
            recorded_at=NOW,
            session=InactiveSession(),
        )


def test_workload_create_exact_replay() -> None:
    registry = (
        PrivilegedWorkloadTrustCurrentnessRegistry(
            Collection()
        )
    )

    tx = Session()
    fact = workload_fact()

    assert (
        registry.create_or_replay(
            fact,
            recorded_at=NOW,
            session=tx,
        )
        == fact
    )

    assert (
        registry.create_or_replay(
            fact,
            recorded_at=NOW,
            session=tx,
        )
        == fact
    )


def test_workload_proof_collision_rejected() -> None:
    registry = (
        PrivilegedWorkloadTrustCurrentnessRegistry(
            Collection()
        )
    )

    tx = Session()

    registry.create_or_replay(
        workload_fact(),
        recorded_at=NOW,
        session=tx,
    )

    divergent = WorkloadTrustFact(
        proof_reference=
            "proof-1",
        principal_id=
            "machine-2",
        credential_or_attestation_reference=
            "attestation-2",
        observed_at=NOW,
        status=
            WorkloadTrustStatus.CURRENT,
    )

    with pytest.raises(
        WorkloadTrustConflictError
    ):
        registry.create_or_replay(
            divergent,
            recorded_at=NOW,
            session=tx,
        )


def test_workload_credential_reference_collision_rejected() -> None:
    registry = (
        PrivilegedWorkloadTrustCurrentnessRegistry(
            Collection()
        )
    )

    tx = Session()

    registry.create_or_replay(
        workload_fact(),
        recorded_at=NOW,
        session=tx,
    )

    with pytest.raises(
        WorkloadTrustConflictError
    ):
        registry.create_or_replay(
            workload_fact(
                proof="proof-2",
                credential="attestation-1",
            ),
            recorded_at=NOW,
            session=tx,
        )


def test_workload_terminal_transition_and_replay() -> None:
    registry = (
        PrivilegedWorkloadTrustCurrentnessRegistry(
            Collection()
        )
    )

    tx = Session()

    registry.create_or_replay(
        workload_fact(),
        recorded_at=NOW,
        session=tx,
    )

    first = registry.terminate(
        proof_reference="proof-1",
        target_status=
            WorkloadTrustStatus.REVOKED,
        session=tx,
    )

    second = registry.terminate(
        proof_reference="proof-1",
        target_status=
            WorkloadTrustStatus.REVOKED,
        session=tx,
    )

    assert first == second
    assert (
        first.status
        is WorkloadTrustStatus.REVOKED
    )



def test_workload_persisted_observed_at_is_canonical_utc_iso_and_hydrates_exactly() -> None:
    """Mongo-safe text preserves aware UTC currentness chronology exactly."""
    from datetime import (
        datetime,
        timedelta,
        timezone,
    )

    from tools.eos.auth.privileged_channel_currentness import (
        WorkloadTrustFact,
        WorkloadTrustStatus,
    )

    import tools.eos.auth.privileged_workload_trust_currentness_registry as module

    observed = datetime(
        2026,
        10,
        14,
        8,
        30,
        37,
        123456,
        tzinfo=timezone(
            timedelta(hours=2)
        ),
    )

    fact = WorkloadTrustFact(
        proof_reference="workload-roundtrip-proof",
        principal_id="principal-roundtrip",
        credential_or_attestation_reference=(
            "credential-roundtrip"
        ),
        observed_at=observed,
        status=WorkloadTrustStatus.CURRENT,
    )

    persisted = module._persisted(
        fact,
        recorded_at=datetime(
            2026,
            10,
            14,
            6,
            31,
            tzinfo=timezone.utc,
        ),
    )

    assert (
        persisted["observed_at"]
        == "2026-10-14T06:30:37.123456+00:00"
    )

    hydrated = module._hydrate(
        persisted
    )

    assert hydrated == fact
    assert hydrated.observed_at.tzinfo is not None
    assert hydrated.observed_at.utcoffset() is not None
    assert hydrated.observed_at == datetime(
        2026,
        10,
        14,
        6,
        30,
        37,
        123456,
        tzinfo=timezone.utc,
    )


def test_workload_hydration_rejects_naive_or_non_text_observed_at() -> None:
    """Persistence repair never weakens strict aware-datetime domain semantics."""
    from datetime import datetime

    import pytest

    from tools.eos.auth.privileged_workload_trust_currentness_registry import (
        WorkloadTrustPersistenceError,
    )

    import tools.eos.auth.privileged_workload_trust_currentness_registry as module

    base = {
        "proof_reference": "workload-roundtrip-proof",
        "principal_id": "principal-roundtrip",
        "credential_or_attestation_reference": "credential-roundtrip",
        "status": "CURRENT",
    }

    for invalid in (
        datetime(2026, 10, 14, 6, 30),
        "2026-10-14T06:30:37",
        None,
        7,
    ):
        row = {
            **base,
            "observed_at": invalid,
        }

        with pytest.raises(
            WorkloadTrustPersistenceError,
            match="PERSISTED_ROW_INVALID",
        ):
            module._hydrate(row)
