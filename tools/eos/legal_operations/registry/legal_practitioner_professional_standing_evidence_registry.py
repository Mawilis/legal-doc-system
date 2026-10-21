"""TITLE: WILSY OS Professional Standing Evidence Registry and Orchestrator.
VERSION: v1.0.0-R63-REGULATORY-EVIDENCE-FOUNDATION
AUTHORITY: Immutable regulatory-source observation persistence only.
EPITOME: Bind R62 professional-standing evidence to verified public LPC source
    identities, append-only lineage, exact replay, and fail-closed currentness.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tools/eos/legal_operations/registry/legal_practitioner_professional_standing_evidence_registry.py
COLLABORATION / OWNERSHIP: Wilsy OS Legal Operations owns documentary evidence;
    the Legal Practice Council remains authoritative for its published records.
CERTIFICATION / UPDATE DATE: 2026-10-21
CHANGELOG:
    2026-10-21 v1.0.0-R63-REGULATORY-EVIDENCE-FOUNDATION
    Introduces caller-transaction-owned immutable lineage, official-source
    correlation, exact replay, corruption rejection, and currentness reads.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2 controls.
SECURITY / PRIVACY POSTURE: Opaque subject identifiers and public-source
    references only; no credentials, names, client data, or matter content.
TENANT BOUNDARY: Every query and index begins with an exact non-pseudo tenant.
AUTHORITY BOUNDARY: Documentary evidence only; no practising, FFC, firm,
    authentication, IAM, matter-access, review, approval, or reassignment grant.
TRANSACTION BOUNDARY: Every read and write requires an active caller-owned
    MongoDB transaction. This module never starts, commits, aborts, or retries it.
FINANCIAL AUTHORITY BOUNDARY: None; Kennel EOS exclusively.
"""

from __future__ import annotations

from dataclasses import dataclass, fields, replace
from datetime import datetime
from hashlib import sha3_512
import hmac
import json
from typing import Any, Final, NoReturn

from pymongo import ASCENDING
from pymongo.errors import DuplicateKeyError, PyMongoError

from tools.eos.legal_operations.domain.legal_practitioner_professional_standing_evidence import (
    LegalPractitionerProfessionalStandingEvidence as Evidence,
    ProfessionalEvidenceKind,
    ProfessionalEvidenceMethod,
    ProfessionalStandingCurrentness,
    project_professional_standing_currentness,
)


VERSION: Final[str] = "v1.0.0-R63-REGULATORY-EVIDENCE-FOUNDATION"
SCHEMA: Final[str] = "WILSY-LEGAL-PROFESSIONAL-STANDING-EVIDENCE-REGISTRY/V1"
COLLECTION_NAME: Final[str] = "legal_practitioner_professional_standing_evidence"
MAX_HISTORY: Final[int] = 512

LPC_PRACTITIONER_DIRECTORY_ISSUER: Final[str] = (
    "legal-practice-council-public-directory"
)
LPC_FFC_VERIFICATION_ISSUER: Final[str] = (
    "legal-practice-council-ffc-verification"
)
LPC_PRACTITIONER_DIRECTORY_URI: Final[str] = (
    "https://lpc.org.za/members-of-the-public/search-practitioners/"
)
LPC_FFC_VERIFICATION_URI: Final[str] = (
    "https://lpc.org.za/legal-practitioners/ffc-verification/"
)
AUTHORITATIVE_PUBLIC_SOURCES: Final[
    dict[ProfessionalEvidenceKind, tuple[str, str]]
] = {
    ProfessionalEvidenceKind.PRACTISING_STATUS: (
        LPC_PRACTITIONER_DIRECTORY_ISSUER,
        LPC_PRACTITIONER_DIRECTORY_URI,
    ),
    ProfessionalEvidenceKind.FIDELITY_FUND_CERTIFICATE_STATUS: (
        LPC_FFC_VERIFICATION_ISSUER,
        LPC_FFC_VERIFICATION_URI,
    ),
}

IDENTITY_INDEX: Final[str] = "r63_professional_evidence_identity_unique"
ROOT_INDEX: Final[str] = "r63_professional_evidence_root_unique"
SUCCESSOR_INDEX: Final[str] = "r63_professional_evidence_successor_unique"
FINGERPRINT_INDEX: Final[str] = "r63_professional_evidence_fingerprint_unique"
REFERENCE_INDEX: Final[str] = "r63_professional_evidence_reference_unique"
CURRENTNESS_INDEX: Final[str] = "r63_professional_evidence_currentness"
INDEX_NAMES: Final[tuple[str, ...]] = (
    IDENTITY_INDEX,
    ROOT_INDEX,
    SUCCESSOR_INDEX,
    FINGERPRINT_INDEX,
    REFERENCE_INDEX,
    CURRENTNESS_INDEX,
)


class ProfessionalStandingEvidenceRegistryError(RuntimeError):
    """Base content-free persistence and orchestration failure."""


class ProfessionalStandingEvidenceTransactionRequired(
    ProfessionalStandingEvidenceRegistryError
):
    """The caller did not supply an already-active MongoDB transaction."""


class ProfessionalStandingEvidenceConflict(ProfessionalStandingEvidenceRegistryError):
    """Replay, lineage, issuer, jurisdiction, or scope evidence conflicts."""


class ProfessionalStandingEvidenceNotFound(ProfessionalStandingEvidenceRegistryError):
    """No exact tenant-scoped lineage exists without disclosing other tenants."""


class ProfessionalStandingEvidencePersistedInvalid(
    ProfessionalStandingEvidenceRegistryError
):
    """Durable data failed strict shape, fingerprint, scope, or lineage checks."""


class ProfessionalStandingEvidenceRetryTransaction(
    ProfessionalStandingEvidenceRegistryError
):
    """The caller must abort and retry the complete transaction from fresh state."""


class ProfessionalStandingEvidencePersistenceUnavailable(
    ProfessionalStandingEvidenceRegistryError
):
    """MongoDB failed without a safely established durable outcome."""


def _fail(error: type[ProfessionalStandingEvidenceRegistryError], code: str) -> NoReturn:
    raise error(code)


def _transaction(session: object) -> object:
    marker = getattr(session, "in_transaction", False) if session is not None else False
    if marker is not True:
        _fail(
            ProfessionalStandingEvidenceTransactionRequired,
            "R63_PROFESSIONAL_EVIDENCE_ACTIVE_TRANSACTION_REQUIRED",
        )
    return session


def _retryable(error: BaseException) -> bool:
    return isinstance(error, PyMongoError) and any(
        bool(error.has_error_label(label))
        for label in ("TransientTransactionError", "UnknownTransactionCommitResult")
    )


def _valid_evidence(value: object) -> Evidence:
    if type(value) is not Evidence:
        _fail(
            ProfessionalStandingEvidenceConflict,
            "R63_PROFESSIONAL_EVIDENCE_DOMAIN_VALUE_REQUIRED",
        )
    try:
        canonical = replace(value)
        if not hmac.compare_digest(canonical.fingerprint, value.fingerprint):
            raise ValueError("FINGERPRINT_MISMATCH")
        return canonical
    except Exception as error:
        raise ProfessionalStandingEvidenceConflict(
            "R63_PROFESSIONAL_EVIDENCE_VALUE_INVALID"
        ) from error


def _verify_source(value: Evidence) -> None:
    kind = ProfessionalEvidenceKind(value.evidence_kind)
    expected = AUTHORITATIVE_PUBLIC_SOURCES[kind]
    if (
        value.jurisdiction != "ZA"
        or value.verification_method is not ProfessionalEvidenceMethod.PUBLIC_WEB_OBSERVATION
        or value.issuer_source_id != expected[0]
        or value.source_uri != expected[1]
    ):
        _fail(
            ProfessionalStandingEvidenceConflict,
            "R63_PROFESSIONAL_EVIDENCE_ISSUER_SOURCE_UNAUTHORIZED",
        )


def _canonical_json(material: dict[str, object]) -> bytes:
    def encode(value: object) -> object:
        if isinstance(value, datetime):
            return value.isoformat()
        if hasattr(value, "value"):
            return getattr(value, "value")
        return value

    return json.dumps(
        {key: encode(value) for key, value in material.items()},
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=True,
    ).encode("utf-8")


@dataclass(frozen=True, slots=True)
class ProfessionalStandingEvidenceRevision:
    """Bind one R62 observation to an immutable, deterministic lineage revision.

    Mutation semantics: none. Idempotency is enforced by the registry. Tenant
    scope, subject, jurisdiction, and evidence kind define one lineage family.
    The record carries no practising, FFC, affiliation, IAM, matter-access,
    review, approval, reassignment, transaction, or financial authority.
    """

    revision: int
    predecessor_registry_fingerprint: str | None
    evidence: Evidence
    schema: str = SCHEMA
    registry_version: str = VERSION
    registry_fingerprint: str = ""

    def __post_init__(self) -> None:
        """Validate source provenance and bind lineage plus R62 evidence."""
        item = _valid_evidence(self.evidence)
        _verify_source(item)
        if type(self.revision) is not int or self.revision < 1:
            _fail(
                ProfessionalStandingEvidenceConflict,
                "R63_PROFESSIONAL_EVIDENCE_REVISION_INVALID",
            )
        if self.revision == 1 and self.predecessor_registry_fingerprint is not None:
            _fail(
                ProfessionalStandingEvidenceConflict,
                "R63_PROFESSIONAL_EVIDENCE_ROOT_PREDECESSOR_FORBIDDEN",
            )
        if self.revision > 1 and (
            type(self.predecessor_registry_fingerprint) is not str
            or len(self.predecessor_registry_fingerprint) != 128
        ):
            _fail(
                ProfessionalStandingEvidenceConflict,
                "R63_PROFESSIONAL_EVIDENCE_PREDECESSOR_REQUIRED",
            )
        if self.schema != SCHEMA or self.registry_version != VERSION:
            _fail(
                ProfessionalStandingEvidenceConflict,
                "R63_PROFESSIONAL_EVIDENCE_SCHEMA_VERSION_INVALID",
            )
        material: dict[str, object] = {
            "schema": self.schema,
            "registry_version": self.registry_version,
            "revision": self.revision,
            "predecessor_registry_fingerprint": self.predecessor_registry_fingerprint,
            "evidence_fingerprint": item.fingerprint,
            "tenant_id": item.tenant_id,
            "practitioner_principal_id": item.practitioner_principal_id,
            "verified_subject_id": item.verified_subject_id,
            "jurisdiction": item.jurisdiction,
            "evidence_kind": item.evidence_kind,
        }
        expected = sha3_512(_canonical_json(material)).hexdigest()
        if self.registry_fingerprint and not hmac.compare_digest(
            self.registry_fingerprint, expected
        ):
            _fail(
                ProfessionalStandingEvidenceConflict,
                "R63_PROFESSIONAL_EVIDENCE_REGISTRY_FINGERPRINT_INVALID",
            )
        object.__setattr__(self, "evidence", item)
        object.__setattr__(self, "registry_fingerprint", expected)

    @property
    def permits_operational_access(self) -> bool:
        """Refuse to elevate durable regulatory evidence into access."""
        return False

    @property
    def permits_reassignment_execution(self) -> bool:
        """Refuse to elevate durable regulatory evidence into reassignment."""
        return False


_EVIDENCE_FIELDS: Final[tuple[str, ...]] = tuple(
    field.name for field in fields(Evidence) if field.name != "fingerprint"
)


def _scope(value: Evidence) -> dict[str, object]:
    return {
        "tenant_id": value.tenant_id,
        "practitioner_principal_id": value.practitioner_principal_id,
        "verified_subject_id": value.verified_subject_id,
        "jurisdiction": value.jurisdiction,
        "evidence_kind": ProfessionalEvidenceKind(value.evidence_kind).value,
    }


def _encode(value: ProfessionalStandingEvidenceRevision) -> dict[str, object]:
    evidence = value.evidence
    document = {name: getattr(evidence, name) for name in _EVIDENCE_FIELDS}
    document.update(
        {
            "evidence_kind": ProfessionalEvidenceKind(evidence.evidence_kind).value,
            "outcome": str(evidence.outcome),
            "verification_method": ProfessionalEvidenceMethod(
                evidence.verification_method
            ).value,
            "evidence_fingerprint": evidence.fingerprint,
            "registry_schema": value.schema,
            "registry_version": value.registry_version,
            "revision": value.revision,
            "predecessor_registry_fingerprint": value.predecessor_registry_fingerprint,
            "registry_fingerprint": value.registry_fingerprint,
        }
    )
    return document


def _decode(document: object) -> ProfessionalStandingEvidenceRevision:
    if type(document) is not dict:
        _fail(
            ProfessionalStandingEvidencePersistedInvalid,
            "R63_PROFESSIONAL_EVIDENCE_DOCUMENT_INVALID",
        )
    expected = set(_EVIDENCE_FIELDS) | {
        "_id",
        "evidence_fingerprint",
        "registry_schema",
        "registry_version",
        "revision",
        "predecessor_registry_fingerprint",
        "registry_fingerprint",
    }
    if set(document) - expected or not (expected - {"_id"}).issubset(document):
        _fail(
            ProfessionalStandingEvidencePersistedInvalid,
            "R63_PROFESSIONAL_EVIDENCE_DOCUMENT_SHAPE_INVALID",
        )
    try:
        item = Evidence(**{name: document[name] for name in _EVIDENCE_FIELDS})
        if not hmac.compare_digest(item.fingerprint, document["evidence_fingerprint"]):
            raise ValueError("EVIDENCE_FINGERPRINT_MISMATCH")
        return ProfessionalStandingEvidenceRevision(
            revision=document["revision"],
            predecessor_registry_fingerprint=document[
                "predecessor_registry_fingerprint"
            ],
            evidence=item,
            schema=document["registry_schema"],
            registry_version=document["registry_version"],
            registry_fingerprint=document["registry_fingerprint"],
        )
    except Exception as error:
        raise ProfessionalStandingEvidencePersistedInvalid(
            "R63_PROFESSIONAL_EVIDENCE_DOCUMENT_CORRUPT"
        ) from error


def _validate_history(
    history: tuple[ProfessionalStandingEvidenceRevision, ...],
) -> tuple[ProfessionalStandingEvidenceRevision, ...]:
    previous: ProfessionalStandingEvidenceRevision | None = None
    references: set[str] = set()
    evidence_ids: set[str] = set()
    for expected_revision, item in enumerate(history, 1):
        if item.revision != expected_revision:
            _fail(
                ProfessionalStandingEvidencePersistedInvalid,
                "R63_PROFESSIONAL_EVIDENCE_REVISION_GAP",
            )
        if item.evidence.evidence_reference in references or item.evidence.evidence_id in evidence_ids:
            _fail(
                ProfessionalStandingEvidencePersistedInvalid,
                "R63_PROFESSIONAL_EVIDENCE_DUPLICATE_HISTORY",
            )
        references.add(item.evidence.evidence_reference)
        evidence_ids.add(item.evidence.evidence_id)
        if previous is None:
            if item.predecessor_registry_fingerprint is not None:
                _fail(
                    ProfessionalStandingEvidencePersistedInvalid,
                    "R63_PROFESSIONAL_EVIDENCE_AMBIGUOUS_ROOT",
                )
        else:
            if _scope(item.evidence) != _scope(previous.evidence):
                _fail(
                    ProfessionalStandingEvidencePersistedInvalid,
                    "R63_PROFESSIONAL_EVIDENCE_LINEAGE_SCOPE_CHANGED",
                )
            if not hmac.compare_digest(
                item.predecessor_registry_fingerprint or "",
                previous.registry_fingerprint,
            ):
                _fail(
                    ProfessionalStandingEvidencePersistedInvalid,
                    "R63_PROFESSIONAL_EVIDENCE_LINEAGE_FORKED",
                )
            if item.evidence.observed_at < previous.evidence.observed_at:
                _fail(
                    ProfessionalStandingEvidencePersistedInvalid,
                    "R63_PROFESSIONAL_EVIDENCE_OBSERVATION_TIME_REGRESSION",
                )
        previous = item
    return history


class ProfessionalStandingEvidenceRegistry:
    """Persist and evaluate official-source R62 evidence without granting access.

    Mutation semantics: append-only inserts. Exact replay returns the durable
    value; divergent or competing replay fails closed. The caller exclusively
    owns transaction start, commit, abort, and whole-transaction retry.
    """

    def __init__(self, collection: Any) -> None:
        """Bind one injected Mongo-compatible collection; no global fallback."""
        self._collection = collection

    def ensure_indexes(self) -> None:
        """Install deterministic uniqueness/read indexes and no TTL index."""
        family = [
            ("tenant_id", ASCENDING),
            ("practitioner_principal_id", ASCENDING),
            ("verified_subject_id", ASCENDING),
            ("jurisdiction", ASCENDING),
            ("evidence_kind", ASCENDING),
        ]
        self._collection.create_index(
            family + [("revision", ASCENDING)], name=IDENTITY_INDEX, unique=True
        )
        self._collection.create_index(
            family,
            name=ROOT_INDEX,
            unique=True,
            partialFilterExpression={"revision": 1},
        )
        self._collection.create_index(
            family + [("predecessor_registry_fingerprint", ASCENDING)],
            name=SUCCESSOR_INDEX,
            unique=True,
            partialFilterExpression={
                "predecessor_registry_fingerprint": {"$type": "string"}
            },
        )
        self._collection.create_index(
            [("tenant_id", ASCENDING), ("registry_fingerprint", ASCENDING)],
            name=FINGERPRINT_INDEX,
            unique=True,
        )
        self._collection.create_index(
            [("tenant_id", ASCENDING), ("evidence_reference", ASCENDING)],
            name=REFERENCE_INDEX,
            unique=True,
        )
        self._collection.create_index(
            family + [("observed_at", ASCENDING), ("revision", ASCENDING)],
            name=CURRENTNESS_INDEX,
        )

    def get_history_if_any(
        self,
        *,
        tenant_id: str,
        practitioner_principal_id: str,
        verified_subject_id: str,
        jurisdiction: str,
        evidence_kind: ProfessionalEvidenceKind | str,
        session: object,
    ) -> tuple[ProfessionalStandingEvidenceRevision, ...]:
        """Return validated exact-scope lineage or empty without existence leaks."""
        active = _transaction(session)
        try:
            kind = ProfessionalEvidenceKind(evidence_kind)
            query = {
                "tenant_id": tenant_id,
                "practitioner_principal_id": practitioner_principal_id,
                "verified_subject_id": verified_subject_id,
                "jurisdiction": jurisdiction,
                "evidence_kind": kind.value,
            }
            documents = tuple(
                self._collection.find(query, session=active)
                .sort("revision", ASCENDING)
                .limit(MAX_HISTORY + 1)
            )
        except (TypeError, ValueError) as error:
            raise ProfessionalStandingEvidenceConflict(
                "R63_PROFESSIONAL_EVIDENCE_SCOPE_INVALID"
            ) from error
        except Exception as error:
            if _retryable(error):
                raise ProfessionalStandingEvidenceRetryTransaction(
                    "R63_PROFESSIONAL_EVIDENCE_RETRY_TRANSACTION"
                ) from error
            raise ProfessionalStandingEvidencePersistenceUnavailable(
                "R63_PROFESSIONAL_EVIDENCE_READ_UNAVAILABLE"
            ) from error
        if len(documents) > MAX_HISTORY:
            _fail(
                ProfessionalStandingEvidencePersistedInvalid,
                "R63_PROFESSIONAL_EVIDENCE_HISTORY_OVERLONG",
            )
        history = _validate_history(tuple(_decode(document) for document in documents))
        if any(_scope(item.evidence) != query for item in history):
            _fail(
                ProfessionalStandingEvidencePersistedInvalid,
                "R63_PROFESSIONAL_EVIDENCE_PERSISTED_SCOPE_MISMATCH",
            )
        return history

    def get_history(
        self,
        *,
        tenant_id: str,
        practitioner_principal_id: str,
        verified_subject_id: str,
        jurisdiction: str,
        evidence_kind: ProfessionalEvidenceKind | str,
        session: object,
    ) -> tuple[ProfessionalStandingEvidenceRevision, ...]:
        """Return strict exact-scope history and reject tenant-scoped absence."""
        history = self.get_history_if_any(
            tenant_id=tenant_id,
            practitioner_principal_id=practitioner_principal_id,
            verified_subject_id=verified_subject_id,
            jurisdiction=jurisdiction,
            evidence_kind=evidence_kind,
            session=session,
        )
        if not history:
            _fail(
                ProfessionalStandingEvidenceNotFound,
                "R63_PROFESSIONAL_EVIDENCE_HISTORY_NOT_FOUND",
            )
        return history

    def create_or_replay(
        self, value: ProfessionalStandingEvidenceRevision, *, session: object
    ) -> ProfessionalStandingEvidenceRevision:
        """Append the exact next official-source revision or return exact replay."""
        active = _transaction(session)
        if type(value) is not ProfessionalStandingEvidenceRevision:
            _fail(
                ProfessionalStandingEvidenceConflict,
                "R63_PROFESSIONAL_EVIDENCE_REVISION_VALUE_REQUIRED",
            )
        item = replace(value)
        family = _scope(item.evidence)
        identity = {**family, "revision": item.revision}
        try:
            existing_raw = self._collection.find_one(identity, session=active)
            if existing_raw is not None:
                existing = _decode(existing_raw)
                if existing == item and hmac.compare_digest(
                    existing.registry_fingerprint, item.registry_fingerprint
                ):
                    self.get_history_if_any(
                        tenant_id=item.evidence.tenant_id,
                        practitioner_principal_id=(
                            item.evidence.practitioner_principal_id
                        ),
                        verified_subject_id=item.evidence.verified_subject_id,
                        jurisdiction=item.evidence.jurisdiction,
                        evidence_kind=item.evidence.evidence_kind,
                        session=active,
                    )
                    return existing
                _fail(
                    ProfessionalStandingEvidenceConflict,
                    "R63_PROFESSIONAL_EVIDENCE_DIVERGENT_REPLAY",
                )
            history = self.get_history_if_any(
                tenant_id=item.evidence.tenant_id,
                practitioner_principal_id=item.evidence.practitioner_principal_id,
                verified_subject_id=item.evidence.verified_subject_id,
                jurisdiction=item.evidence.jurisdiction,
                evidence_kind=item.evidence.evidence_kind,
                session=active,
            )
            if item.revision != len(history) + 1:
                _fail(
                    ProfessionalStandingEvidenceConflict,
                    "R63_PROFESSIONAL_EVIDENCE_REVISION_SEQUENCE_CONFLICT",
                )
            if history:
                previous = history[-1]
                if item.predecessor_registry_fingerprint != previous.registry_fingerprint:
                    _fail(
                        ProfessionalStandingEvidenceConflict,
                        "R63_PROFESSIONAL_EVIDENCE_PREDECESSOR_MISMATCH",
                    )
                if item.evidence.observed_at < previous.evidence.observed_at:
                    _fail(
                        ProfessionalStandingEvidenceConflict,
                        "R63_PROFESSIONAL_EVIDENCE_OBSERVATION_TIME_REGRESSION",
                    )
            self._collection.insert_one(_encode(item), session=active)
            durable = self._collection.find_one(identity, session=active)
            if durable is None:
                _fail(
                    ProfessionalStandingEvidencePersistedInvalid,
                    "R63_PROFESSIONAL_EVIDENCE_WRITE_NOT_READABLE",
                )
            return _decode(durable)
        except ProfessionalStandingEvidenceRegistryError:
            raise
        except DuplicateKeyError as error:
            raise ProfessionalStandingEvidenceRetryTransaction(
                "R63_PROFESSIONAL_EVIDENCE_CONCURRENT_WRITE_RETRY"
            ) from error
        except Exception as error:
            if _retryable(error):
                raise ProfessionalStandingEvidenceRetryTransaction(
                    "R63_PROFESSIONAL_EVIDENCE_RETRY_TRANSACTION"
                ) from error
            raise ProfessionalStandingEvidencePersistenceUnavailable(
                "R63_PROFESSIONAL_EVIDENCE_WRITE_UNAVAILABLE"
            ) from error

    def evaluate_currentness(
        self,
        *,
        tenant_id: str,
        practitioner_principal_id: str,
        verified_subject_id: str,
        jurisdiction: str,
        evidence_kind: ProfessionalEvidenceKind | str,
        evaluation_time: datetime,
        session: object,
    ) -> ProfessionalStandingCurrentness:
        """Project R62 currentness from strict durable official-source lineage."""
        history = self.get_history_if_any(
            tenant_id=tenant_id,
            practitioner_principal_id=practitioner_principal_id,
            verified_subject_id=verified_subject_id,
            jurisdiction=jurisdiction,
            evidence_kind=evidence_kind,
            session=session,
        )
        return project_professional_standing_currentness(
            tenant_id=tenant_id,
            practitioner_principal_id=practitioner_principal_id,
            jurisdiction=jurisdiction,
            evidence_kind=evidence_kind,
            evaluation_time=evaluation_time,
            evidence=(item.evidence for item in history),
        )


__all__ = [
    "VERSION",
    "SCHEMA",
    "COLLECTION_NAME",
    "MAX_HISTORY",
    "LPC_PRACTITIONER_DIRECTORY_ISSUER",
    "LPC_FFC_VERIFICATION_ISSUER",
    "LPC_PRACTITIONER_DIRECTORY_URI",
    "LPC_FFC_VERIFICATION_URI",
    "AUTHORITATIVE_PUBLIC_SOURCES",
    "INDEX_NAMES",
    "ProfessionalStandingEvidenceRegistryError",
    "ProfessionalStandingEvidenceTransactionRequired",
    "ProfessionalStandingEvidenceConflict",
    "ProfessionalStandingEvidenceNotFound",
    "ProfessionalStandingEvidencePersistedInvalid",
    "ProfessionalStandingEvidenceRetryTransaction",
    "ProfessionalStandingEvidencePersistenceUnavailable",
    "ProfessionalStandingEvidenceRevision",
    "ProfessionalStandingEvidenceRegistry",
]


# WILSY OS SOVEREIGN ARTIFACT SEAL
# ARTIFACT: legal_practitioner_professional_standing_evidence_registry.py
# VERSION: v1.0.0-R63-REGULATORY-EVIDENCE-FOUNDATION
# AUTHORITY BOUNDARY: official-source documentary persistence/currentness only
# TENANT POSTURE: exact tenant predicates; cross-tenant absence is non-disclosing
# FAIL-CLOSED POSTURE: unauthorized issuer, replay divergence, fork, corruption,
# stale, revoked, ambiguous, unavailable, or non-transactional work never grants
# OPERATIONAL ACCESS / IAM / MATTER ACCESS / REASSIGNMENT AUTHORITY: NONE
# FINANCIAL EXECUTION AUTHORITY: NONE; KENNEL EOS EXCLUSIVELY
# END OF WILSY OS SOVEREIGN ARTIFACT
