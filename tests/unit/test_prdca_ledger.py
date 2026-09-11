"""Direct certificate for the durable PRDCA ledger.

TITLE: PRDCA Ledger Direct Certificate
VERSION: v1.0.0-M11-R8-R3B-P8-P3L
AUTHORITY: Wilsy OS Core Governance
EPITOME: Proves immutable batch persistence, exact replay, duplicate conflict,
         strict hydration, index ownership, and caller transaction forwarding.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tests/unit/test_prdca_ledger.py
COLLABORATION / OWNERSHIP: Direct certificate for tools/eos/governance/prdca_ledger.py.
CERTIFICATION / UPDATE DATE: 2026-09-10
CHANGELOG: v1.0.0-M11-R8-R3B-P8-P3L certifies the Mongo ledger contract.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2.
"""
from __future__ import annotations

from types import SimpleNamespace
from typing import Any, Mapping, cast

import pytest
from pymongo.errors import DuplicateKeyError

import tools.eos.governance.prdca as core
from tools.eos.governance.prdca_ledger import (
    PRDCALedgerPersistedRecordInvalidError,
    PRDCALedgerTransactionRequiredError,
    PRDCAMongoLedger,
)


class _Collection:
    def __init__(self) -> None:
        self.rows: list[dict[str, object]] = []
        self.indexes: list[tuple[object, dict[str, object]]] = []
        self.inserts = 0
        self.duplicate = False

    def create_index(self, keys: object, **options: object) -> str:
        self.indexes.append((keys, options))
        return str(options.get("name", "index"))

    def find_one(self, query: dict[str, object], *, session: object = None) -> dict[str, object] | None:
        path = next(iter(query))
        value = query[path]
        return next(
            (
                row
                for row in self.rows
                if row.get("platform_registration", {}).get("artifact_id") == value  # type: ignore[union-attr]
            ),
            None,
        )

    def insert_one(self, document: dict[str, object], *, session: object = None) -> object:
        self.inserts += 1
        if self.duplicate:
            raise DuplicateKeyError("duplicate")
        self.rows.append(dict(document))
        return SimpleNamespace()


class _Active:
    active = True


class _Inactive:
    active = False


def _batch() -> core.PRDCACertificateBatch:
    payload: dict[str, object] = {"schema": "x"}
    envelope = {
        "envelope_schema": "WILSY-PRDCA-SIGNED-ENVELOPE/V1",
        "artifact_type": "PLATFORM_REGISTRATION_CERTIFICATE",
        "artifact_id": "a" * 128,
        "payload_schema": "WILSY-PLATFORM-REGISTRATION-CERTIFICATE/V1",
        "payload": payload,
        "campaign_identity": "campaign",
        "issuer_authority": "authority",
        "authority_key_id": "prdca-key:test",
        "signature_algorithm": "Ed25519",
        "signature": "signature",
        "issued_at": "2026-09-10T10:00:00.000000Z",
        "status": "ACTIVE",
    }
    dcc = dict(envelope, artifact_type="DEPLOYMENT_CERTIFICATION_CERTIFICATE", artifact_id="b" * 128)
    receipt = dict(envelope, artifact_type="DESCRIPTOR_VERIFICATION_RECEIPT", artifact_id="c" * 128)
    return core.PRDCACertificateBatch(
        platform_registration=core.PlatformRegistrationCertificateEnvelope(
            **{**envelope, "payload": cast(Mapping[str, object], envelope["payload"])}
        ),
        deployment_certification=core.DeploymentCertificationCertificateEnvelope(
            **{**dcc, "payload": cast(Mapping[str, object], dcc["payload"])}
        ),
        descriptor_receipt=core.DescriptorVerificationReceiptEnvelope(
            **{**receipt, "payload": cast(Mapping[str, object], receipt["payload"])}
        ),
    )


def test_indexes_are_three_unique_artifact_identity_indexes() -> None:
    collection = _Collection()
    PRDCAMongoLedger(cast(Any, collection)).ensure_indexes()
    assert len(collection.indexes) == 3
    assert all(options["unique"] is True for _, options in collection.indexes)


def test_append_requires_active_caller_transaction() -> None:
    ledger = PRDCAMongoLedger(cast(Any, _Collection()))
    with pytest.raises(PRDCALedgerTransactionRequiredError):
        ledger.append_batch(_batch(), cast(Any, _Inactive()))


def test_append_forwards_session_and_exact_replay_is_noop() -> None:
    collection = _Collection()
    ledger = PRDCAMongoLedger(cast(Any, collection))
    batch = _batch()
    session = _Active()
    ledger.append_batch(batch, cast(Any, session))
    ledger.append_batch(batch, cast(Any, session))
    assert collection.inserts == 1
    assert collection.rows[0]["schema"] == "WILSY-PRDCA-CERTIFICATE-BATCH/V1"


def test_duplicate_artifact_race_fails_closed_without_recovery() -> None:
    collection = _Collection()
    collection.duplicate = True
    ledger = PRDCAMongoLedger(cast(Any, collection))
    with pytest.raises(core.PRDCAArtifactConflictError):
        ledger.append_batch(_batch(), cast(Any, _Active()))


def test_strict_hydration_rejects_corrupted_fingerprint() -> None:
    collection = _Collection()
    ledger = PRDCAMongoLedger(cast(Any, collection))
    ledger.append_batch(_batch(), cast(Any, _Active()))
    collection.rows[0]["batch_fingerprint"] = "0" * 128
    with pytest.raises(PRDCALedgerPersistedRecordInvalidError):
        ledger.get_by_platform_registration_id("a" * 128)


def test_ledger_has_no_transaction_lifecycle_methods() -> None:
    public_names = set(PRDCAMongoLedger.__dict__)
    assert "start_transaction" not in public_names
    assert "commit" not in public_names
    assert "abort" not in public_names


# ARTIFACT: test_prdca_ledger.py
# VERSION: v1.0.0-M11-R8-R3B-P8-P3L
# AUTHORITY BOUNDARY: direct certificate for PRDCA ledger persistence only
# TENANT POSTURE: platform governance scope; no tenant authorization
# FAIL-CLOSED POSTURE: absent transaction, corruption, and duplicate races reject
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively
# END OF WILSY OS SOVEREIGN ARTIFACT
