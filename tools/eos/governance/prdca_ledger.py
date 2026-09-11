"""Wilsy durable PRDCA certificate ledger.

TITLE: Platform Registration and Deployment Certification Authority Ledger
VERSION: v1.0.1-M11-R8-R3B-P8-P3L-R2R1
AUTHORITY: Wilsy OS Core Governance
EPITOME: Persist immutable PRDCA certificate batches in a caller-owned Mongo
         transaction with exact-artifact uniqueness and strict hydration.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tools/eos/governance/prdca_ledger.py
COLLABORATION / OWNERSHIP: PRDCA ledger persistence owner; certificate semantics
                            remain owned by prdca.py and transaction lifecycle
                            remains owned by the caller.
CERTIFICATION / UPDATE DATE: 2026-09-10
CHANGELOG: v1.0.1-M11-R8-R3B-P8-P3L-R2R1 repairs canonical serialization of
           immutable mapping payloads while preserving ledger semantics.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2.
SECURITY / PRIVACY POSTURE: No key loading, secret retrieval, network client,
                            provider, KMS, or deployment-evidence production.
TENANT BOUNDARY: Platform governance scope; no tenant authorization.
AUTHORITY BOUNDARY: Durable certificate evidence only; never issues authority.
FINANCIAL AUTHORITY BOUNDARY: Kennel EOS exclusively owns financial execution.
FAIL-CLOSED DECLARATION: Missing caller transaction, malformed records,
                          duplicate artifacts, and persistence failures reject.
"""
from __future__ import annotations

import hashlib
import json
from types import MappingProxyType
from typing import Any, Final, Mapping, Protocol, cast

from pymongo import ASCENDING
from pymongo.client_session import ClientSession
from pymongo.collection import Collection
from pymongo.errors import DuplicateKeyError, PyMongoError

from tools.eos.governance.prdca import (
    AuthenticatedRuntimeDeploymentEvidence,
    CallerOwnedTransaction,
    DescriptorVerificationReceiptEnvelope,
    DeploymentCertificationCertificateEnvelope,
    PRDCACertificateBatch,
    PRDCAArtifactConflictError,
    PlatformRegistrationCertificateEnvelope,
)


COLLECTION: Final[str] = "prdca_certificate_batches"
BATCH_SCHEMA: Final[str] = "WILSY-PRDCA-CERTIFICATE-BATCH/V1"
_BATCH_FIELDS: Final[tuple[str, ...]] = (
    "schema",
    "platform_registration",
    "deployment_certification",
    "descriptor_receipt",
    "batch_fingerprint",
)
_BATCH_FINGERPRINT_FIELDS: Final[tuple[str, ...]] = _BATCH_FIELDS[:-1]
_ENVELOPE_FIELDS: Final[tuple[str, ...]] = (
    "envelope_schema",
    "artifact_type",
    "artifact_id",
    "payload_schema",
    "payload",
    "campaign_identity",
    "issuer_authority",
    "authority_key_id",
    "signature_algorithm",
    "signature",
    "issued_at",
    "status",
)


class PRDCALedgerError(RuntimeError):
    """Base fail-closed durable-ledger error."""


class PRDCALedgerTransactionRequiredError(PRDCALedgerError):
    """The caller did not provide an active transaction."""


class PRDCALedgerPersistedRecordInvalidError(PRDCALedgerError):
    """A durable batch violates its exact schema or fingerprint."""


class PRDCALedgerPersistenceError(PRDCALedgerError):
    """The backing collection could not complete the requested operation."""


class PRDCAMongoSession(CallerOwnedTransaction):
    """Adapt a real Mongo session to the PRDCA caller-owned marker protocol.

    The caller still starts, commits, and aborts the underlying session. This
    wrapper only exposes its active state to the frozen PRDCA core and ledger.
    """

    def __init__(self, session: ClientSession) -> None:
        if session is None:
            raise PRDCALedgerTransactionRequiredError("M11P3L_MONGO_SESSION_REQUIRED")
        self._session = session

    @property
    def active(self) -> bool:
        """Return whether the caller's underlying Mongo transaction is active."""
        return bool(getattr(self._session, "in_transaction", False))

    @property
    def mongo_session(self) -> ClientSession:
        """Return the caller-owned session for collection method forwarding."""
        return self._session


class _SessionCarrier(Protocol):
    @property
    def mongo_session(self) -> ClientSession: ...


def _active(session: object) -> bool:
    return bool(
        getattr(session, "active", False)
        or getattr(session, "in_transaction", False)
    )


def _raw_session(session: object) -> object:
    return getattr(session, "mongo_session", session)


def _json_ready(value: object) -> object:
    """Convert immutable mapping containers to ordered JSON-native values."""
    if isinstance(value, Mapping):
        return {key: _json_ready(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [_json_ready(item) for item in value]
    return value


def _canonical_bytes(document: Mapping[str, object], fields: tuple[str, ...]) -> bytes:
    if tuple(document) != fields:
        raise PRDCALedgerPersistedRecordInvalidError("M11P3L_FIELD_ORDER_INVALID")
    try:
        encoded = json.dumps(
            _json_ready(document),
            ensure_ascii=False,
            sort_keys=False,
            allow_nan=False,
            separators=(",", ":"),
        ).encode("utf-8")
    except (TypeError, ValueError, UnicodeEncodeError) as exc:
        raise PRDCALedgerPersistedRecordInvalidError(
            "M11P3L_CANONICAL_SERIALIZATION_INVALID"
        ) from exc
    if encoded != encoded.rstrip() or encoded.endswith(b"\n"):
        raise PRDCALedgerPersistedRecordInvalidError("M11P3L_TRAILING_WHITESPACE")
    return encoded


def _batch_document(batch: PRDCACertificateBatch) -> dict[str, object]:
    if not isinstance(batch, PRDCACertificateBatch):
        raise PRDCALedgerPersistedRecordInvalidError("M11P3L_BATCH_REQUIRED")
    body: dict[str, object] = {
        "schema": BATCH_SCHEMA,
        "platform_registration": batch.platform_registration.to_dict(),
        "deployment_certification": batch.deployment_certification.to_dict(),
        "descriptor_receipt": batch.descriptor_receipt.to_dict(),
    }
    body["batch_fingerprint"] = hashlib.sha3_512(
        _canonical_bytes(body, _BATCH_FINGERPRINT_FIELDS)
    ).hexdigest()
    return body


def _envelope(value: object, envelope_type: type[Any]) -> Any:
    if not isinstance(value, Mapping) or tuple(value) != _ENVELOPE_FIELDS:
        raise PRDCALedgerPersistedRecordInvalidError("M11P3L_ENVELOPE_SCHEMA_INVALID")
    payload = value.get("payload")
    if not isinstance(payload, Mapping):
        raise PRDCALedgerPersistedRecordInvalidError("M11P3L_ENVELOPE_PAYLOAD_INVALID")
    try:
        return envelope_type(
            **{
                field: MappingProxyType(dict(payload)) if field == "payload" else value[field]
                for field in _ENVELOPE_FIELDS
            }
        )
    except (TypeError, ValueError) as exc:
        raise PRDCALedgerPersistedRecordInvalidError(
            "M11P3L_ENVELOPE_HYDRATION_INVALID"
        ) from exc


def _hydrate(document: Mapping[str, object]) -> PRDCACertificateBatch:
    if not isinstance(document, Mapping):
        raise PRDCALedgerPersistedRecordInvalidError("M11P3L_RECORD_REQUIRED")
    body = dict(document)
    body.pop("_id", None)
    if tuple(body) != _BATCH_FIELDS:
        raise PRDCALedgerPersistedRecordInvalidError("M11P3L_BATCH_SCHEMA_INVALID")
    expected = hashlib.sha3_512(
        _canonical_bytes(
            {field: body[field] for field in _BATCH_FINGERPRINT_FIELDS},
            _BATCH_FINGERPRINT_FIELDS,
        )
    ).hexdigest()
    stored = body["batch_fingerprint"]
    if not isinstance(stored, str) or stored != expected:
        raise PRDCALedgerPersistedRecordInvalidError("M11P3L_BATCH_FINGERPRINT_INVALID")
    if body["schema"] != BATCH_SCHEMA:
        raise PRDCALedgerPersistedRecordInvalidError("M11P3L_BATCH_SCHEMA_INVALID")
    return PRDCACertificateBatch(
        platform_registration=_envelope(
            body["platform_registration"], PlatformRegistrationCertificateEnvelope
        ),
        deployment_certification=_envelope(
            body["deployment_certification"], DeploymentCertificationCertificateEnvelope
        ),
        descriptor_receipt=_envelope(
            body["descriptor_receipt"], DescriptorVerificationReceiptEnvelope
        ),
    )


class PRDCAMongoLedger:
    """Persist immutable PRDCA batches through a caller-owned Mongo transaction."""

    def __init__(self, collection: Collection) -> None:
        self._collection = collection

    def ensure_indexes(self) -> None:
        """Create deterministic unique artifact indexes outside transactions."""
        self._collection.create_index(
            [("platform_registration.artifact_id", ASCENDING)],
            unique=True,
            name="prdca_platform_registration_artifact_unique",
        )
        self._collection.create_index(
            [("deployment_certification.artifact_id", ASCENDING)],
            unique=True,
            name="prdca_deployment_certification_artifact_unique",
        )
        self._collection.create_index(
            [("descriptor_receipt.artifact_id", ASCENDING)],
            unique=True,
            name="prdca_descriptor_receipt_artifact_unique",
        )

    def append_batch(
        self, batch: PRDCACertificateBatch, session: CallerOwnedTransaction
    ) -> None:
        """Append one immutable batch or return exact replay without rewriting.

        Duplicate-key recovery is intentionally not attempted inside the failed
        transaction. The caller must retry the whole operation in a new one.
        """
        if not _active(session):
            raise PRDCALedgerTransactionRequiredError("M11P3L_ACTIVE_TRANSACTION_REQUIRED")
        document = _batch_document(batch)
        mongo_session = _raw_session(session)
        platform_registration = document["platform_registration"]
        if not isinstance(platform_registration, Mapping):
            raise PRDCALedgerPersistedRecordInvalidError(
                "M11P3L_PLATFORM_REGISTRATION_INVALID"
            )
        query = {
            "platform_registration.artifact_id": platform_registration["artifact_id"]
        }
        try:
            existing = self._collection.find_one(query, session=mongo_session)
            if existing is not None:
                existing_body = dict(existing)
                existing_body.pop("_id", None)
                if existing_body == document:
                    return
                raise PRDCAArtifactConflictError("M11P3L_ARTIFACT_ID_CONFLICT")
            self._collection.insert_one(
                document, session=cast(ClientSession | None, mongo_session)
            )
        except PRDCAArtifactConflictError:
            raise
        except DuplicateKeyError as exc:
            raise PRDCAArtifactConflictError(
                "M11P3L_DUPLICATE_ARTIFACT_RETRY_TRANSACTION"
            ) from exc
        except PyMongoError as exc:
            raise PRDCALedgerPersistenceError("M11P3L_PERSISTENCE_FAILURE") from exc

    def get_by_platform_registration_id(
        self, artifact_id: str, *, session: CallerOwnedTransaction | None = None
    ) -> PRDCACertificateBatch:
        """Read and strictly hydrate one batch by exact platform artifact ID."""
        if not isinstance(artifact_id, str) or not artifact_id:
            raise PRDCALedgerPersistedRecordInvalidError("M11P3L_ARTIFACT_ID_REQUIRED")
        try:
            query = {"platform_registration.artifact_id": artifact_id}
            existing = self._collection.find_one(
                query, session=_raw_session(session) if session is not None else None
            )
            if existing is None:
                raise PRDCALedgerPersistenceError("M11P3L_ARTIFACT_NOT_FOUND")
            return _hydrate(existing)
        except PRDCALedgerError:
            raise
        except PyMongoError as exc:
            raise PRDCALedgerPersistenceError("M11P3L_READ_FAILURE") from exc


__all__ = [
    "BATCH_SCHEMA",
    "COLLECTION",
    "PRDCALedgerError",
    "PRDCALedgerPersistedRecordInvalidError",
    "PRDCALedgerPersistenceError",
    "PRDCALedgerTransactionRequiredError",
    "PRDCAMongoLedger",
    "PRDCAMongoSession",
]


# ARTIFACT: prdca_ledger.py
# VERSION: v1.0.1-M11-R8-R3B-P8-P3L-R2R1
# AUTHORITY BOUNDARY: immutable PRDCA certificate evidence persistence only
# TENANT POSTURE: platform governance scope; no tenant authorization
# FAIL-CLOSED POSTURE: absent transaction, corruption, duplicate, and DDL errors reject
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively
# END OF WILSY OS SOVEREIGN ARTIFACT
