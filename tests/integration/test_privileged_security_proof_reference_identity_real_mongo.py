from __future__ import annotations
import os

from concurrent.futures import ThreadPoolExecutor
from threading import Barrier
from typing import Any
import uuid

import pytest
from pymongo import MongoClient
from pymongo.errors import (
    DuplicateKeyError,
    OperationFailure,
    PyMongoError,
)

from tools.eos.auth import (
    privileged_interactive_security_proof_registry
    as interactive_registry,
)
from tools.eos.auth import (
    privileged_noninteractive_security_proof_registry
    as noninteractive_registry,
)


MONGO_URI = os.environ["WILSY_VENDOR_CERT_MONGO_URI"]


@pytest.fixture()
def mongo_context():
    client: MongoClient[Any] = MongoClient(
        MONGO_URI,
        serverSelectionTimeoutMS=3000,
    )

    hello = client.admin.command("hello")
    assert hello.get("setName") == "wilsyVendorCertRS"

    database = client[
        "wilsy_p3_reference_identity_"
        + uuid.uuid4().hex
    ]

    try:
        yield client, database
    finally:
        client.drop_database(database.name)
        client.close()


def _assert_index(
    collection: Any,
    *,
    name: str,
    field: str,
) -> None:
    indexes = {
        item["name"]: item
        for item in collection.list_indexes()
    }

    value = indexes[name]

    assert dict(value["key"]) == {
        field: 1,
    }

    assert value.get("unique") is True

    assert value.get(
        "partialFilterExpression"
    ) == {
        "revision": 1,
    }

    assert "expireAfterSeconds" not in value


def _interactive_row(
    *,
    proof_id: str,
    proof_reference: str,
    factor_reference: str,
    revision: int = 1,
) -> dict[str, object]:
    return {
        "proof_id": proof_id,
        "revision": revision,
        "proof_reference": proof_reference,
        "factor_verification_reference":
            factor_reference,
        "idempotency_key":
            f"idem-{proof_id}-{revision}",
    }


def _noninteractive_row(
    *,
    proof_id: str,
    proof_reference: str,
    credential_reference: str,
    revision: int = 1,
) -> dict[str, object]:
    return {
        "proof_id": proof_id,
        "revision": revision,
        "proof_reference": proof_reference,
        "credential_or_attestation_reference":
            credential_reference,
        "idempotency_key":
            f"idem-{proof_id}-{revision}",
    }


def _race(
    client: MongoClient[Any],
    collection: Any,
    first: dict[str, object],
    second: dict[str, object],
) -> list[str]:
    barrier = Barrier(2)

    def worker(
        row: dict[str, object],
    ) -> str:
        try:
            with client.start_session() as session:
                session.start_transaction()

                barrier.wait(timeout=5)

                collection.insert_one(
                    row,
                    session=session,
                )

                session.commit_transaction()

            return "COMMIT"

        except DuplicateKeyError:
            return "DUPLICATE_KEY"

        except OperationFailure as error:
            if error.has_error_label(
                "TransientTransactionError"
            ):
                return "TRANSIENT_TRANSACTION_ERROR"

            return (
                "OPERATION_FAILURE:"
                + str(error.code)
            )

        except PyMongoError as error:
            if error.has_error_label(
                "TransientTransactionError"
            ):
                return "TRANSIENT_TRANSACTION_ERROR"

            return (
                "PYMONGO_ERROR:"
                + type(error).__name__
            )

    with ThreadPoolExecutor(
        max_workers=2
    ) as executor:
        futures = (
            executor.submit(worker, first),
            executor.submit(worker, second),
        )

        return [
            future.result(timeout=15)
            for future in futures
        ]


def _assert_serialized(
    outcomes: list[str],
) -> None:
    assert outcomes.count("COMMIT") == 1
    assert len(outcomes) == 2

    loser = [
        value
        for value in outcomes
        if value != "COMMIT"
    ]

    assert len(loser) == 1

    assert loser[0] in {
        "DUPLICATE_KEY",
        "TRANSIENT_TRANSACTION_ERROR",
    }


def test_physical_identity_indexes(
    mongo_context,
) -> None:
    _client, database = mongo_context

    interactive = database[
        interactive_registry.COLLECTION
    ]

    interactive_registry        .PrivilegedInteractiveSecurityProofRegistry(
            interactive
        )        .ensure_indexes()

    _assert_index(
        interactive,
        name=(
            interactive_registry
            .PROOF_REFERENCE_INITIAL_IDENTITY_INDEX
        ),
        field="proof_reference",
    )

    _assert_index(
        interactive,
        name=(
            interactive_registry
            .FACTOR_REFERENCE_INITIAL_IDENTITY_INDEX
        ),
        field="factor_verification_reference",
    )

    noninteractive = database[
        noninteractive_registry.COLLECTION
    ]

    noninteractive_registry        .PrivilegedNoninteractiveSecurityProofRegistry(
            noninteractive
        )        .ensure_indexes()

    _assert_index(
        noninteractive,
        name=(
            noninteractive_registry
            .PROOF_REFERENCE_INITIAL_IDENTITY_INDEX
        ),
        field="proof_reference",
    )

    _assert_index(
        noninteractive,
        name=(
            noninteractive_registry
            .CREDENTIAL_REFERENCE_INITIAL_IDENTITY_INDEX
        ),
        field="credential_or_attestation_reference",
    )


def test_all_initial_reference_races_serialize(
    mongo_context,
) -> None:
    client, database = mongo_context

    interactive = database[
        interactive_registry.COLLECTION
    ]

    interactive_registry        .PrivilegedInteractiveSecurityProofRegistry(
            interactive
        )        .ensure_indexes()

    outcomes = _race(
        client,
        interactive,
        _interactive_row(
            proof_id="i-proof-a",
            proof_reference="shared-i-proof",
            factor_reference="factor-a",
        ),
        _interactive_row(
            proof_id="i-proof-b",
            proof_reference="shared-i-proof",
            factor_reference="factor-b",
        ),
    )

    _assert_serialized(outcomes)

    outcomes = _race(
        client,
        interactive,
        _interactive_row(
            proof_id="i-factor-a",
            proof_reference="proof-a",
            factor_reference="shared-factor",
        ),
        _interactive_row(
            proof_id="i-factor-b",
            proof_reference="proof-b",
            factor_reference="shared-factor",
        ),
    )

    _assert_serialized(outcomes)

    noninteractive = database[
        noninteractive_registry.COLLECTION
    ]

    noninteractive_registry        .PrivilegedNoninteractiveSecurityProofRegistry(
            noninteractive
        )        .ensure_indexes()

    outcomes = _race(
        client,
        noninteractive,
        _noninteractive_row(
            proof_id="n-proof-a",
            proof_reference="shared-n-proof",
            credential_reference="attestation-a",
        ),
        _noninteractive_row(
            proof_id="n-proof-b",
            proof_reference="shared-n-proof",
            credential_reference="attestation-b",
        ),
    )

    _assert_serialized(outcomes)

    outcomes = _race(
        client,
        noninteractive,
        _noninteractive_row(
            proof_id="n-credential-a",
            proof_reference="proof-a",
            credential_reference="shared-attestation",
        ),
        _noninteractive_row(
            proof_id="n-credential-b",
            proof_reference="proof-b",
            credential_reference="shared-attestation",
        ),
    )

    _assert_serialized(outcomes)


def test_same_proof_revision_history_remains_allowed(
    mongo_context,
) -> None:
    _client, database = mongo_context

    interactive = database[
        interactive_registry.COLLECTION
    ]

    interactive_registry        .PrivilegedInteractiveSecurityProofRegistry(
            interactive
        )        .ensure_indexes()

    interactive.insert_one(
        _interactive_row(
            proof_id="interactive-history",
            proof_reference="interactive-history-ref",
            factor_reference="interactive-factor-ref",
            revision=1,
        )
    )

    interactive.insert_one(
        _interactive_row(
            proof_id="interactive-history",
            proof_reference="interactive-history-ref",
            factor_reference="interactive-factor-ref",
            revision=2,
        )
    )

    assert interactive.count_documents(
        {
            "proof_id":
                "interactive-history"
        }
    ) == 2

    noninteractive = database[
        noninteractive_registry.COLLECTION
    ]

    noninteractive_registry        .PrivilegedNoninteractiveSecurityProofRegistry(
            noninteractive
        )        .ensure_indexes()

    noninteractive.insert_one(
        _noninteractive_row(
            proof_id="noninteractive-history",
            proof_reference="noninteractive-history-ref",
            credential_reference="attestation-history",
            revision=1,
        )
    )

    noninteractive.insert_one(
        _noninteractive_row(
            proof_id="noninteractive-history",
            proof_reference="noninteractive-history-ref",
            credential_reference="attestation-history",
            revision=2,
        )
    )

    assert noninteractive.count_documents(
        {
            "proof_id":
                "noninteractive-history"
        }
    ) == 2
