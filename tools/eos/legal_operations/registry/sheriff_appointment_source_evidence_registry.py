"""TITLE: WILSY OS Sheriff Appointment Evidence Registry
VERSION: v1.0.0-SHERIFF-APPOINTMENT-EVIDENCE-REGISTRY
AUTHORITY: Immutable tenant-scoped appointment source-observation persistence only.
EPITOME: Persist Sheriff appointment source evidence as append-only, caller-
    transaction-owned revision history with exact replay, deterministic
    tenant-first indexes, strict hydration and fork/corruption rejection.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tools/eos/legal_operations/registry/sheriff_appointment_source_evidence_registry.py
COLLABORATION / OWNERSHIP: Legal Operations owns documentary persistence;
    the Minister and South African Board for Sheriffs remain the relevant
    external statutory authorities; identity, verification and IAM are separate.
CERTIFICATION / UPDATE DATE: 2026-11-02
CHANGELOG:
    2026-11-02 v1.0.0-SHERIFF-APPOINTMENT-EVIDENCE-REGISTRY
    Introduces append-only source-evidence history, caller-owned active
    transaction enforcement, exact replay, predecessor lineage and fail-closed
    persisted-document validation. No source trust root or access authority.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2 technical controls.
SECURITY / PRIVACY POSTURE: Opaque identifiers, source references and SHA3-512
    fingerprints only; no raw identity documents, credentials or narrative data.
TENANT BOUNDARY: Every index, query, replay and conflict classification begins
    with exact non-pseudo tenant_id; cross-tenant absence is not disclosed.
AUTHORITY BOUNDARY: Persistence of observations only; no appointment
    authentication, issuer trust, FFC/insurance currentness, identity proof,
    IAM, office access, queue assignment or legal execution.
TRANSACTION BOUNDARY: Every read and write requires an active caller-owned
    MongoDB transaction. This module never starts, commits, aborts or retries it.
FINANCIAL AUTHORITY BOUNDARY: None; Kennel EOS exclusively.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from hashlib import sha3_512
import hmac
import json
import re
from typing import Any, Final, NoReturn

from pymongo import ASCENDING
from pymongo.errors import DuplicateKeyError, PyMongoError

from tools.eos.legal_operations.domain.sheriff_appointment_source_evidence import (
    SheriffAppointmentSourceEvidence as Evidence,
)


VERSION: Final[str] = "v1.0.0-SHERIFF-APPOINTMENT-EVIDENCE-REGISTRY"
SCHEMA: Final[str] = "WILSY-SHERIFF-APPOINTMENT-EVIDENCE-REGISTRY/V1"
COLLECTION_NAME: Final[str] = "sheriff_appointment_source_evidence"
MAX_HISTORY: Final[int] = 512
_HEX_128: Final[re.Pattern[str]] = re.compile(r"[0-9a-f]{128}\\Z")
_IDENTIFIER: Final[re.Pattern[str]] = re.compile(r"[A-Za-z0-9][A-Za-z0-9._:/?#=&%-]{0,511}\\Z")

IDENTITY_INDEX: Final[str] = "sheriff_appointment_evidence_identity_unique"
ROOT_INDEX: Final[str] = "sheriff_appointment_evidence_root_unique"
SUCCESSOR_INDEX: Final[str] = "sheriff_appointment_evidence_successor_unique"
FINGERPRINT_INDEX: Final[str] = "sheriff_appointment_evidence_fingerprint_unique"
HISTORY_INDEX: Final[str] = "sheriff_appointment_evidence_history"
INDEX_NAMES: Final[tuple[str, ...]] = (
    IDENTITY_INDEX,
    ROOT_INDEX,
    SUCCESSOR_INDEX,
    FINGERPRINT_INDEX,
    HISTORY_INDEX,
)


class SheriffAppointmentEvidenceRegistryError(RuntimeError):
    """Base content-free Sheriff appointment persistence failure."""


class SheriffAppointmentEvidenceTransactionRequired(
    SheriffAppointmentEvidenceRegistryError
):
    """The caller did not supply an already-active MongoDB transaction."""


class SheriffAppointmentEvidenceConflict(SheriffAppointmentEvidenceRegistryError):
    """The requested revision conflicts with tenant-scoped immutable history."""


class SheriffAppointmentEvidenceNotFound(SheriffAppointmentEvidenceRegistryError):
    """No exact tenant-scoped evidence history exists."""


class SheriffAppointmentEvidencePersistedInvalid(
    SheriffAppointmentEvidenceRegistryError
):
    """A durable document failed strict shape, fingerprint or lineage checks."""


class SheriffAppointmentEvidenceRetryTransaction(
    SheriffAppointmentEvidenceRegistryError
):
    """The caller must abort and retry the complete transaction from fresh state."""


class SheriffAppointmentEvidencePersistenceUnavailable(
    SheriffAppointmentEvidenceRegistryError
):
    """MongoDB failed without a safely established durable outcome."""


def _fail(
    error: type[SheriffAppointmentEvidenceRegistryError],
    code: str,
) -> NoReturn:
    raise error(code)


def _tenant(value: object) -> str:
    if (
        type(value) is not str
        or _IDENTIFIER.fullmatch(value) is None
        or value.casefold() in {"default", "global", "root", "*"}
    ):
        _fail(
            SheriffAppointmentEvidenceConflict,
            "SHERIFF_APPOINTMENT_REGISTRY_TENANT_INVALID",
        )
    return value


def _identity(name: str, value: object) -> str:
    if type(value) is not str or _IDENTIFIER.fullmatch(value) is None:
        _fail(
            SheriffAppointmentEvidenceConflict,
            f"SHERIFF_APPOINTMENT_REGISTRY_{name.upper()}_INVALID",
        )
    return value


def _transaction(session: object) -> object:
    marker = getattr(session, "in_transaction", False) if session is not None else False
    if marker is not True:
        _fail(
            SheriffAppointmentEvidenceTransactionRequired,
            "SHERIFF_APPOINTMENT_REGISTRY_ACTIVE_CALLER_TRANSACTION_REQUIRED",
        )
    return session


def _retryable(error: BaseException) -> bool:
    return isinstance(error, PyMongoError) and any(
        bool(error.has_error_label(label))
        for label in ("TransientTransactionError", "UnknownTransactionCommitResult")
    )


def _scope(value: Evidence) -> dict[str, object]:
    """Return immutable identity fields defining one appointment evidence family."""
    return {
        "tenant_id": value.tenant_id,
        "evidence_id": value.evidence_id,
        "principal_id": value.principal_id,
        "verified_subject_reference": value.verified_subject_reference,
        "sheriff_office_id": value.sheriff_office_id,
        "district_id": value.district_id,
        "court_reference": value.court_reference,
        "capacity": value.capacity.value,
        "statutory_basis": value.statutory_basis.value,
        "issuer_authority": value.issuer_authority.value,
    }


def _canonical_fingerprint(
    revision: int,
    predecessor: str | None,
    evidence: Evidence,
) -> str:
    material = {
        "schema": SCHEMA,
        "registry_version": VERSION,
        "revision": revision,
        "predecessor_registry_fingerprint": predecessor,
        "evidence_fingerprint": evidence.fingerprint,
        "scope": _scope(evidence),
    }
    encoded = json.dumps(
        material,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=True,
    ).encode("utf-8")
    return sha3_512(encoded).hexdigest()


@dataclass(frozen=True, slots=True)
class SheriffAppointmentEvidenceRevision:
    """Bind one immutable source observation to registry-owned revision lineage.

    The revision must equal the source evidence revision. The registry
    fingerprint chains the durable registry history independently of the
    source-evidence fingerprint. This record grants no appointment or access.
    """

    revision: int
    predecessor_registry_fingerprint: str | None
    evidence: Evidence
    schema: str = SCHEMA
    registry_version: str = VERSION
    registry_fingerprint: str = ""

    def __post_init__(self) -> None:
        """Validate exact source type, revision and registry-chain fingerprint."""
        if type(self.evidence) is not Evidence:
            _fail(
                SheriffAppointmentEvidenceConflict,
                "SHERIFF_APPOINTMENT_REGISTRY_DOMAIN_VALUE_REQUIRED",
            )
        if type(self.revision) is not int or self.revision < 1:
            _fail(
                SheriffAppointmentEvidenceConflict,
                "SHERIFF_APPOINTMENT_REGISTRY_REVISION_INVALID",
            )
        if self.revision != self.evidence.revision:
            _fail(
                SheriffAppointmentEvidenceConflict,
                "SHERIFF_APPOINTMENT_REGISTRY_SOURCE_REVISION_MISMATCH",
            )
        if self.schema != SCHEMA or self.registry_version != VERSION:
            _fail(
                SheriffAppointmentEvidenceConflict,
                "SHERIFF_APPOINTMENT_REGISTRY_SCHEMA_VERSION_INVALID",
            )
        predecessor = self.predecessor_registry_fingerprint
        if self.revision == 1 and predecessor is not None:
            _fail(
                SheriffAppointmentEvidenceConflict,
                "SHERIFF_APPOINTMENT_REGISTRY_ROOT_PREDECESSOR_FORBIDDEN",
            )
        if self.revision > 1 and (
            type(predecessor) is not str or _HEX_128.fullmatch(predecessor) is None
        ):
            _fail(
                SheriffAppointmentEvidenceConflict,
                "SHERIFF_APPOINTMENT_REGISTRY_PREDECESSOR_REQUIRED",
            )
        expected = _canonical_fingerprint(self.revision, predecessor, self.evidence)
        if self.registry_fingerprint:
            if (
                type(self.registry_fingerprint) is not str
                or _HEX_128.fullmatch(self.registry_fingerprint) is None
                or not hmac.compare_digest(self.registry_fingerprint, expected)
            ):
                _fail(
                    SheriffAppointmentEvidenceConflict,
                    "SHERIFF_APPOINTMENT_REGISTRY_FINGERPRINT_INVALID",
                )
        object.__setattr__(self, "registry_fingerprint", expected)

    @property
    def permits_operational_access(self) -> bool:
        """Durable appointment observations never grant office or queue access."""
        return False

    @property
    def permits_legal_execution(self) -> bool:
        """Durable appointment observations never authorize a legal act."""
        return False


def _encode(value: SheriffAppointmentEvidenceRevision) -> dict[str, object]:
    document = value.evidence.to_dict()
    document.update(
        {
            "registry_schema": value.schema,
            "registry_version": value.registry_version,
            "registry_revision": value.revision,
            "predecessor_registry_fingerprint": value.predecessor_registry_fingerprint,
            "registry_fingerprint": value.registry_fingerprint,
        }
    )
    return document


def _parse_instant(value: object) -> object:
    if value is None:
        return None
    if type(value) is not str:
        raise ValueError("PERSISTED_INSTANT_INVALID")
    parsed = datetime.fromisoformat(value)
    if parsed.tzinfo is None or parsed.utcoffset() is None:
        raise ValueError("PERSISTED_INSTANT_NOT_AWARE")
    return parsed


_EVIDENCE_FIELDS: Final[tuple[str, ...]] = (
    "tenant_id", "evidence_id", "revision", "principal_id",
    "verified_subject_reference", "sheriff_office_id", "district_id",
    "court_reference", "service_area_references", "capacity",
    "statutory_basis", "issuer_authority", "instrument_reference",
    "instrument_fingerprint", "source_uri", "source_observation_state",
    "source_verification_method", "source_verification_reference",
    "verified_by_principal_id", "observed_at", "effective_from",
    "effective_until", "appointing_principal_id", "board_approval_reference",
    "board_approval_fingerprint", "board_confirmation_reference",
    "board_confirmation_fingerprint", "board_consultation_reference",
    "board_consultation_fingerprint", "conditions_fingerprint",
    "supersedes_fingerprint", "schema", "version", "fingerprint",
)


def _decode(document: object) -> SheriffAppointmentEvidenceRevision:
    """Hydrate only exact, fingerprint-valid persisted registry documents."""
    if type(document) is not dict:
        _fail(
            SheriffAppointmentEvidencePersistedInvalid,
            "SHERIFF_APPOINTMENT_REGISTRY_DOCUMENT_INVALID",
        )
    expected_evidence = set(_EVIDENCE_FIELDS)
    allowed = expected_evidence | {
        "_id", "registry_schema", "registry_version", "registry_revision",
        "predecessor_registry_fingerprint", "registry_fingerprint",
    }
    if set(document) - allowed or not (allowed - {"_id"}).issubset(document):
        _fail(
            SheriffAppointmentEvidencePersistedInvalid,
            "SHERIFF_APPOINTMENT_REGISTRY_DOCUMENT_SHAPE_INVALID",
        )
    try:
        material = {
            key: document[key]
            for key in _EVIDENCE_FIELDS
        }
        for name in ("observed_at", "effective_from", "effective_until"):
            material[name] = _parse_instant(material[name])
        evidence = Evidence(**material)
        if not hmac.compare_digest(evidence.fingerprint, document["fingerprint"]):
            raise ValueError("SOURCE_FINGERPRINT_MISMATCH")
        return SheriffAppointmentEvidenceRevision(
            revision=document["registry_revision"],
            predecessor_registry_fingerprint=document[
                "predecessor_registry_fingerprint"
            ],
            evidence=evidence,
            schema=document["registry_schema"],
            registry_version=document["registry_version"],
            registry_fingerprint=document["registry_fingerprint"],
        )
    except SheriffAppointmentEvidenceRegistryError:
        raise
    except Exception as error:
        raise SheriffAppointmentEvidencePersistedInvalid(
            "SHERIFF_APPOINTMENT_REGISTRY_DOCUMENT_CORRUPT"
        ) from error


def _validate_history(
    history: tuple[SheriffAppointmentEvidenceRevision, ...],
) -> tuple[SheriffAppointmentEvidenceRevision, ...]:
    """Reject revision gaps, scope drift, duplicate instruments and chain forks."""
    previous: SheriffAppointmentEvidenceRevision | None = None
    evidence_fingerprints: set[str] = set()
    for expected_revision, item in enumerate(history, 1):
        if item.revision != expected_revision:
            _fail(
                SheriffAppointmentEvidencePersistedInvalid,
                "SHERIFF_APPOINTMENT_REGISTRY_REVISION_GAP",
            )
        if item.evidence.fingerprint in evidence_fingerprints:
            _fail(
                SheriffAppointmentEvidencePersistedInvalid,
                "SHERIFF_APPOINTMENT_REGISTRY_DUPLICATE_SOURCE_EVIDENCE",
            )
        evidence_fingerprints.add(item.evidence.fingerprint)
        if previous is None:
            if item.predecessor_registry_fingerprint is not None:
                _fail(
                    SheriffAppointmentEvidencePersistedInvalid,
                    "SHERIFF_APPOINTMENT_REGISTRY_AMBIGUOUS_ROOT",
                )
            if item.evidence.supersedes_fingerprint is not None:
                _fail(
                    SheriffAppointmentEvidencePersistedInvalid,
                    "SHERIFF_APPOINTMENT_REGISTRY_SOURCE_ROOT_SUPERSEDES",
                )
        else:
            if _scope(item.evidence) != _scope(previous.evidence):
                _fail(
                    SheriffAppointmentEvidencePersistedInvalid,
                    "SHERIFF_APPOINTMENT_REGISTRY_LINEAGE_SCOPE_CHANGED",
                )
            if not hmac.compare_digest(
                item.predecessor_registry_fingerprint or "",
                previous.registry_fingerprint,
            ):
                _fail(
                    SheriffAppointmentEvidencePersistedInvalid,
                    "SHERIFF_APPOINTMENT_REGISTRY_LINEAGE_FORKED",
                )
            if not hmac.compare_digest(
                item.evidence.supersedes_fingerprint or "",
                previous.evidence.fingerprint,
            ):
                _fail(
                    SheriffAppointmentEvidencePersistedInvalid,
                    "SHERIFF_APPOINTMENT_REGISTRY_SOURCE_PREDECESSOR_MISMATCH",
                )
            if item.evidence.observed_at < previous.evidence.observed_at:
                _fail(
                    SheriffAppointmentEvidencePersistedInvalid,
                    "SHERIFF_APPOINTMENT_REGISTRY_OBSERVATION_TIME_REGRESSION",
                )
        previous = item
    return history


class SheriffAppointmentEvidenceRegistry:
    """Persist exact-tenant source observations without authenticating appointments.

    Mutation semantics are append-only. Exact replay returns the durable
    revision; divergent replay and competing writes fail closed. The caller
    owns transaction start, commit, abort and whole-transaction retry.
    """

    def __init__(self, collection: Any) -> None:
        """Bind one injected Mongo-compatible collection; no global fallback."""
        if collection is None:
            _fail(
                SheriffAppointmentEvidenceConflict,
                "SHERIFF_APPOINTMENT_REGISTRY_COLLECTION_REQUIRED",
            )
        self._collection = collection

    def ensure_indexes(self) -> None:
        """Create tenant-first uniqueness/history indexes; never create TTL."""
        family = [
            ("tenant_id", ASCENDING),
            ("evidence_id", ASCENDING),
        ]
        self._collection.create_index(
            family + [("revision", ASCENDING)],
            unique=True,
            name=IDENTITY_INDEX,
        )
        self._collection.create_index(
            family,
            unique=True,
            name=ROOT_INDEX,
            partialFilterExpression={"revision": 1},
        )
        self._collection.create_index(
            family + [("supersedes_fingerprint", ASCENDING)],
            unique=True,
            name=SUCCESSOR_INDEX,
            partialFilterExpression={"supersedes_fingerprint": {"$type": "string"}},
        )
        self._collection.create_index(
            [("tenant_id", ASCENDING), ("registry_fingerprint", ASCENDING)],
            unique=True,
            name=FINGERPRINT_INDEX,
        )
        self._collection.create_index(
            family + [("observed_at", ASCENDING), ("revision", ASCENDING)],
            name=HISTORY_INDEX,
        )

    def get_history_if_any(
        self,
        *,
        tenant_id: str,
        evidence_id: str,
        session: object,
    ) -> tuple[SheriffAppointmentEvidenceRevision, ...]:
        """Return strict exact-tenant lineage or empty without existence leaks."""
        active = _transaction(session)
        tenant = _tenant(tenant_id)
        identity = _identity("evidence_id", evidence_id)
        query = {"tenant_id": tenant, "evidence_id": identity}
        try:
            documents = tuple(
                self._collection.find(query, session=active)
                .sort("revision", ASCENDING)
                .limit(MAX_HISTORY + 1)
            )
        except PyMongoError as error:
            if _retryable(error):
                raise SheriffAppointmentEvidenceRetryTransaction(
                    "SHERIFF_APPOINTMENT_REGISTRY_RETRY_TRANSACTION"
                ) from error
            raise SheriffAppointmentEvidencePersistenceUnavailable(
                "SHERIFF_APPOINTMENT_REGISTRY_READ_UNAVAILABLE"
            ) from error
        if len(documents) > MAX_HISTORY:
            _fail(
                SheriffAppointmentEvidencePersistedInvalid,
                "SHERIFF_APPOINTMENT_REGISTRY_HISTORY_OVERLONG",
            )
        history = _validate_history(tuple(_decode(item) for item in documents))
        if any(
            item.evidence.tenant_id != tenant
            or item.evidence.evidence_id != identity
            for item in history
        ):
            _fail(
                SheriffAppointmentEvidencePersistedInvalid,
                "SHERIFF_APPOINTMENT_REGISTRY_PERSISTED_SCOPE_MISMATCH",
            )
        return history

    def get_history(
        self,
        *,
        tenant_id: str,
        evidence_id: str,
        session: object,
    ) -> tuple[SheriffAppointmentEvidenceRevision, ...]:
        """Return exact tenant-scoped history and reject absence."""
        history = self.get_history_if_any(
            tenant_id=tenant_id,
            evidence_id=evidence_id,
            session=session,
        )
        if not history:
            _fail(
                SheriffAppointmentEvidenceNotFound,
                "SHERIFF_APPOINTMENT_REGISTRY_HISTORY_NOT_FOUND",
            )
        return history

    def persist_revision(
        self,
        value: SheriffAppointmentEvidenceRevision,
        *,
        session: object,
    ) -> SheriffAppointmentEvidenceRevision:
        """Append next exact revision or return exact replay in caller transaction."""
        active = _transaction(session)
        if type(value) is not SheriffAppointmentEvidenceRevision:
            _fail(
                SheriffAppointmentEvidenceConflict,
                "SHERIFF_APPOINTMENT_REGISTRY_REVISION_VALUE_REQUIRED",
            )
        tenant = _tenant(value.evidence.tenant_id)
        evidence_id = _identity("evidence_id", value.evidence.evidence_id)
        identity = {
            "tenant_id": tenant,
            "evidence_id": evidence_id,
            "revision": value.revision,
        }
        try:
            existing_raw = self._collection.find_one(identity, session=active)
            if existing_raw is not None:
                existing = _decode(existing_raw)
                history = self.get_history_if_any(
                    tenant_id=tenant,
                    evidence_id=evidence_id,
                    session=active,
                )
                if (
                    existing == value
                    and hmac.compare_digest(
                        existing.registry_fingerprint,
                        value.registry_fingerprint,
                    )
                    and history
                    and history[-1].revision >= value.revision
                ):
                    return existing
                _fail(
                    SheriffAppointmentEvidenceConflict,
                    "SHERIFF_APPOINTMENT_REGISTRY_DIVERGENT_REPLAY",
                )
            history = self.get_history_if_any(
                tenant_id=tenant,
                evidence_id=evidence_id,
                session=active,
            )
            if value.revision != len(history) + 1:
                _fail(
                    SheriffAppointmentEvidenceConflict,
                    "SHERIFF_APPOINTMENT_REGISTRY_REVISION_SEQUENCE_CONFLICT",
                )
            if history:
                previous = history[-1]
                if _scope(value.evidence) != _scope(previous.evidence):
                    _fail(
                        SheriffAppointmentEvidenceConflict,
                        "SHERIFF_APPOINTMENT_REGISTRY_LINEAGE_SCOPE_CHANGED",
                    )
                if value.predecessor_registry_fingerprint != previous.registry_fingerprint:
                    _fail(
                        SheriffAppointmentEvidenceConflict,
                        "SHERIFF_APPOINTMENT_REGISTRY_PREDECESSOR_MISMATCH",
                    )
                if value.evidence.supersedes_fingerprint != previous.evidence.fingerprint:
                    _fail(
                        SheriffAppointmentEvidenceConflict,
                        "SHERIFF_APPOINTMENT_REGISTRY_SOURCE_PREDECESSOR_MISMATCH",
                    )
                if value.evidence.observed_at < previous.evidence.observed_at:
                    _fail(
                        SheriffAppointmentEvidenceConflict,
                        "SHERIFF_APPOINTMENT_REGISTRY_OBSERVATION_TIME_REGRESSION",
                    )
            elif (
                value.predecessor_registry_fingerprint is not None
                or value.evidence.supersedes_fingerprint is not None
            ):
                _fail(
                    SheriffAppointmentEvidenceConflict,
                    "SHERIFF_APPOINTMENT_REGISTRY_ROOT_PREDECESSOR_FORBIDDEN",
                )
            self._collection.insert_one(_encode(value), session=active)
            durable = self._collection.find_one(identity, session=active)
            if durable is None:
                _fail(
                    SheriffAppointmentEvidencePersistedInvalid,
                    "SHERIFF_APPOINTMENT_REGISTRY_WRITE_NOT_READABLE",
                )
            result = _decode(durable)
            if result != value:
                _fail(
                    SheriffAppointmentEvidencePersistedInvalid,
                    "SHERIFF_APPOINTMENT_REGISTRY_WRITE_DIVERGED",
                )
            return result
        except SheriffAppointmentEvidenceRegistryError:
            raise
        except DuplicateKeyError as error:
            raise SheriffAppointmentEvidenceRetryTransaction(
                "SHERIFF_APPOINTMENT_REGISTRY_COMPETING_WRITE_RETRY"
            ) from error
        except PyMongoError as error:
            if _retryable(error):
                raise SheriffAppointmentEvidenceRetryTransaction(
                    "SHERIFF_APPOINTMENT_REGISTRY_RETRY_TRANSACTION"
                ) from error
            raise SheriffAppointmentEvidencePersistenceUnavailable(
                "SHERIFF_APPOINTMENT_REGISTRY_WRITE_UNAVAILABLE"
            ) from error

    def resolve_current(
        self,
        *,
        tenant_id: str,
        evidence_id: str,
        at: datetime,
        session: object,
    ) -> SheriffAppointmentEvidenceRevision | None:
        """Derive documentary currentness from validated history; store no pointer."""
        if type(at) is not datetime or at.tzinfo is None or at.utcoffset() is None:
            _fail(
                SheriffAppointmentEvidenceConflict,
                "SHERIFF_APPOINTMENT_REGISTRY_EVALUATION_TIME_INVALID",
            )
        moment = at
        history = self.get_history_if_any(
            tenant_id=tenant_id,
            evidence_id=evidence_id,
            session=session,
        )
        applicable = tuple(
            item for item in history if item.evidence.effective_from <= moment
        )
        if not applicable:
            return None
        latest = applicable[-1]
        if (
            latest.evidence.effective_until is not None
            and moment >= latest.evidence.effective_until
        ):
            return None
        if latest.evidence.source_observation_state.value in {
            "DISPUTED",
            "SOURCE_UNAVAILABLE",
            "UNVERIFIED_SUBMISSION",
        }:
            return None
        return latest


__all__ = [
    "VERSION",
    "SCHEMA",
    "COLLECTION_NAME",
    "MAX_HISTORY",
    "INDEX_NAMES",
    "SheriffAppointmentEvidenceRevision",
    "SheriffAppointmentEvidenceRegistry",
    "SheriffAppointmentEvidenceRegistryError",
    "SheriffAppointmentEvidenceTransactionRequired",
    "SheriffAppointmentEvidenceConflict",
    "SheriffAppointmentEvidenceNotFound",
    "SheriffAppointmentEvidencePersistedInvalid",
    "SheriffAppointmentEvidenceRetryTransaction",
    "SheriffAppointmentEvidencePersistenceUnavailable",
]

# ==============================================================================
# WILSY OS SOVEREIGN ARTIFACT SEAL
# ==============================================================================
# ARTIFACT: tools/eos/legal_operations/registry/sheriff_appointment_source_evidence_registry.py
# VERSION: v1.0.0-SHERIFF-APPOINTMENT-EVIDENCE-REGISTRY
# AUTHORITY BOUNDARY: immutable source-observation persistence only; no authentication, IAM, office access or execution
# TENANT POSTURE: exact tenant-first queries, indexes, replay and history
# FAIL-CLOSED POSTURE: absent transaction, divergent replay, fork, corruption, race and persistence outage reject
# FINANCIAL EXECUTION AUTHORITY: NONE; KENNEL EOS EXCLUSIVELY
# END OF WILSY OS SOVEREIGN ARTIFACT
