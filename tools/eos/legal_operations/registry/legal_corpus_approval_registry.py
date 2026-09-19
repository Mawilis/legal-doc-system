"""Append-only persistence boundary for signed legal-corpus approvals.

TITLE: WILSY OS Legal Corpus Approval Evidence Registry
VERSION: v1.0.0-R1D-B0F-B4-R9B-P3-P1-LEGAL-CORPUS-APPROVAL-REGISTRY
AUTHORITY: Wilsy OS Core Governance
EPITOME: Persists and exactly replays one complete, already-verified PLATFORM
         legal-corpus approval authorization without issuing authority,
         promoting documents, or owning transaction lifecycle.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tools/eos/legal_operations/registry/legal_corpus_approval_registry.py
COLLABORATION / OWNERSHIP: The future approval service supplies a
                            VerifiedLegalCorpusApprovalAuthorization and owns
                            sessions, transactions, retries, and commit truth.
                            This registry owns only immutable evidence storage.
CERTIFICATION / UPDATE DATE: 2026-09-19
CHANGELOG: v1.0.0-P3-P1 establishes lossless 17-field authorization
           persistence, closed hydration, five-identity collision adjudication,
           exact replay, and caller-owned transaction boundaries.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2.
SECURITY / PRIVACY POSTURE: No private keys, secrets, request context, caller
                            mappings, or current-trust claims are accepted.
TENANT BOUNDARY: PLATFORM-only institutional approval; tenant/principal
                 acceptance is a separate authority plane.
AUTHORITY BOUNDARY: Requires an already verified proof and never issues,
                    verifies, promotes, reviews, accepts, signs, or executes.
FINANCIAL AUTHORITY BOUNDARY: None; Kennel EOS remains exclusive for financial
                              execution and settlement truth.
TRANSACTION BOUNDARY: Every relevant read and write forwards the caller's
                      session. This registry never creates sessions, starts or
                      ends transactions, retries, or interprets commit results.
FAIL-CLOSED POSTURE: Unknown inputs, corrupt rows, identity splits, divergent
                     collisions, and ambiguous duplicate races are errors.
"""
from __future__ import annotations

import json
from copy import deepcopy
from dataclasses import dataclass
from datetime import datetime, timezone
from enum import StrEnum
from typing import Any, Final, Mapping

from pymongo.errors import DuplicateKeyError, PyMongoError

from tools.eos.kernel import db as kernel_db
from tools.eos.legal_operations.domain.legal_acceptance import (
    LegalAgreementType,
    LegalDocumentStatus,
    LegalDocumentVersion,
)
from tools.eos.legal_operations.domain.legal_corpus_approval_authority import (
    LegalCorpusApprovalAuthorityEvidence,
    LegalCorpusApprovalAuthorityMechanism,
    LegalCorpusApprovalAuthorityScope,
    LegalCorpusApprovalAuthoritySource,
    LegalCorpusApprovalDecision,
    LegalCorpusApprovalOperation,
    LegalCorpusApprovalSigningMechanism,
)
from tools.eos.legal_operations.domain.legal_corpus_approval_authorization import (
    LegalCorpusApprovalAuthorization,
    LegalCorpusApprovalAuthorizationOperation,
    LegalCorpusApprovalAuthorizationScope,
    VerifiedLegalCorpusApprovalAuthorization,
)


VERSION: Final[str] = "v1.0.0-R1D-B0F-B4-R9B-P3-P1-LEGAL-CORPUS-APPROVAL-REGISTRY"
COLLECTION: Final[str] = "legal_corpus_approval_evidence"

AUTHORIZATION_STRUCTURAL_FIELDS: Final[frozenset[str]] = frozenset(
    {
        "schema",
        "authorization_id",
        "issuer_identity",
        "authority_role",
        "authority_domain",
        "algorithm",
        "key_id",
        "trust_fingerprint",
        "operation",
        "scope",
        "approval_evidence",
        "approval_evidence_fingerprint",
        "issued_at",
        "expires_at",
        "nonce",
        "idempotency_key",
        "signature_base64url",
    }
)

APPROVAL_EVIDENCE_FIELDS: Final[frozenset[str]] = frozenset(
    {
        "approval_evidence_id",
        "schema_version",
        "scope",
        "operation",
        "approval_decision",
        "approval_authority_source",
        "approval_authority_mechanism",
        "approval_authority_mechanism_version",
        "human_authority_representation",
        "approval_signing_mechanism",
        "approval_signing_mechanism_version",
        "approval_signing_key_id",
        "approval_signature_reference",
        "approved_at",
        "effective_from",
        "idempotency_key",
        "provenance_reference",
        "source_document_id",
        "source_agreement_type",
        "source_version",
        "source_title",
        "source_jurisdiction",
        "source_locale",
        "source_effective_from",
        "source_status",
        "source_content_reference",
        "source_content",
        "source_sha3_512",
        "source_created_at",
        "source_supersedes_document_id",
        "approved_document_id",
        "approved_agreement_type",
        "approved_version",
        "approved_title",
        "approved_jurisdiction",
        "approved_locale",
        "approved_effective_from",
        "approved_status",
        "approved_content_reference",
        "approved_content",
        "approved_sha3_512",
        "approved_created_at",
        "approved_supersedes_document_id",
        "evidence_fingerprint",
    }
)

_ROW_METADATA_FIELDS: Final[frozenset[str]] = frozenset({"_id"})
_UTC = timezone.utc


class LegalCorpusApprovalRegistryError(RuntimeError):
    """Stable, non-sensitive failure for registry input or persistence."""

    def __init__(self, code: str) -> None:
        self.code = code
        super().__init__(code)


class LegalCorpusApprovalAdmissionState(StrEnum):
    """Non-authoritative outcome of one append-only admission attempt."""

    CREATED = "CREATED"
    EXACT_REPLAY = "EXACT_REPLAY"


@dataclass(frozen=True, slots=True)
class LegalCorpusApprovalDurableRecord:
    """Immutable, unverified read model of one persisted approval envelope.

    This value is not a current-trust proof. A later service must supply the
    persisted authorization to the governed verifier before using it for
    current eligibility decisions.
    """

    authorization: LegalCorpusApprovalAuthorization
    approval_evidence_fingerprint: str

    def to_document(self) -> dict[str, Any]:
        """Return a detached normalized 17-field durable representation."""
        return _durable_document(self.authorization)

    @property
    def approval_evidence_id(self) -> str:
        """Return the immutable nested evidence identity."""
        return self.authorization.approval_evidence.approval_evidence_id


@dataclass(frozen=True, slots=True)
class LegalCorpusApprovalAdmissionResult:
    """Report creation or exact replay without claiming approval success."""

    state: LegalCorpusApprovalAdmissionState
    record: LegalCorpusApprovalDurableRecord


@dataclass(frozen=True, slots=True)
class _IdentityMatch:
    selector: str
    row: dict[str, Any]
    record: LegalCorpusApprovalDurableRecord


def _target(collection: Any = None) -> Any:
    """Resolve an explicit collection or the canonical Kernel DB collection."""
    if collection is not None:
        return collection
    database = kernel_db.get_database()
    if database is None:
        raise LegalCorpusApprovalRegistryError("LEGAL_CORPUS_APPROVAL_DATABASE_UNAVAILABLE")
    return database[COLLECTION]


def _canonical_timestamp(value: datetime) -> str:
    """Serialize one aware instant without BSON precision loss."""
    if value.tzinfo is None or value.utcoffset() is None:
        raise LegalCorpusApprovalRegistryError("LEGAL_CORPUS_APPROVAL_PERSISTED_INVALID")
    return value.astimezone(_UTC).isoformat(timespec="microseconds")


def _parse_timestamp(value: Any) -> datetime:
    """Parse only canonical UTC microsecond timestamp strings."""
    if not isinstance(value, str):
        raise LegalCorpusApprovalRegistryError("LEGAL_CORPUS_APPROVAL_PERSISTED_INVALID")
    try:
        parsed = datetime.fromisoformat(value)
    except ValueError as error:
        raise LegalCorpusApprovalRegistryError("LEGAL_CORPUS_APPROVAL_PERSISTED_INVALID") from error
    if parsed.tzinfo is None or parsed.utcoffset() is None:
        raise LegalCorpusApprovalRegistryError("LEGAL_CORPUS_APPROVAL_PERSISTED_INVALID")
    normalized = parsed.astimezone(_UTC)
    if value != _canonical_timestamp(normalized):
        raise LegalCorpusApprovalRegistryError("LEGAL_CORPUS_APPROVAL_PERSISTED_INVALID")
    return normalized


def _canonical_bytes(payload: Mapping[str, Any]) -> bytes:
    """Serialize semantic primitives deterministically for replay comparison."""
    try:
        return json.dumps(
            payload,
            ensure_ascii=False,
            sort_keys=True,
            separators=(",", ":"),
            allow_nan=False,
        ).encode("utf-8")
    except (TypeError, ValueError) as error:
        raise LegalCorpusApprovalRegistryError("LEGAL_CORPUS_APPROVAL_PERSISTED_INVALID") from error


def _durable_document(authorization: LegalCorpusApprovalAuthorization) -> dict[str, Any]:
    """Build the corrected lossless 17-field document from bound authorization."""
    if not isinstance(authorization, LegalCorpusApprovalAuthorization):
        raise LegalCorpusApprovalRegistryError("LEGAL_CORPUS_APPROVAL_AUTHORITY_INPUT_INVALID")
    payload = deepcopy(authorization.to_document())
    evidence = payload.get("approval_evidence")
    if not isinstance(evidence, dict):
        raise LegalCorpusApprovalRegistryError("LEGAL_CORPUS_APPROVAL_PERSISTED_INVALID")
    payload["approval_evidence_fingerprint"] = authorization.approval_evidence.evidence_fingerprint
    if set(payload) != AUTHORIZATION_STRUCTURAL_FIELDS:
        raise LegalCorpusApprovalRegistryError("LEGAL_CORPUS_APPROVAL_PERSISTED_INVALID")
    if evidence.get("evidence_fingerprint") != payload["approval_evidence_fingerprint"]:
        raise LegalCorpusApprovalRegistryError("LEGAL_CORPUS_APPROVAL_PERSISTED_INVALID")
    return payload


def _document_from_payload(payload: Mapping[str, Any], prefix: str) -> LegalDocumentVersion:
    """Hydrate one flattened governed legal-document binding."""
    try:
        return LegalDocumentVersion(
            document_id=payload[f"{prefix}_document_id"],
            agreement_type=LegalAgreementType(payload[f"{prefix}_agreement_type"]),
            version=payload[f"{prefix}_version"],
            title=payload[f"{prefix}_title"],
            jurisdiction=payload[f"{prefix}_jurisdiction"],
            locale=payload[f"{prefix}_locale"],
            effective_from=_parse_timestamp(payload[f"{prefix}_effective_from"]),
            status=LegalDocumentStatus(payload[f"{prefix}_status"]),
            content_reference=payload[f"{prefix}_content_reference"],
            content=payload[f"{prefix}_content"],
            sha3_512=payload[f"{prefix}_sha3_512"],
            created_at=_parse_timestamp(payload[f"{prefix}_created_at"]),
            supersedes_document_id=payload[f"{prefix}_supersedes_document_id"],
        )
    except (
        KeyError,
        TypeError,
        ValueError,
        OverflowError,
        LegalCorpusApprovalRegistryError,
    ) as error:
        raise LegalCorpusApprovalRegistryError("LEGAL_CORPUS_APPROVAL_PERSISTED_INVALID") from error


def _hydrate_evidence(payload: Any) -> LegalCorpusApprovalAuthorityEvidence:
    """Hydrate and revalidate the complete 44-field nested evidence mapping."""
    if not isinstance(payload, dict) or set(payload) != APPROVAL_EVIDENCE_FIELDS:
        raise LegalCorpusApprovalRegistryError("LEGAL_CORPUS_APPROVAL_PERSISTED_INVALID")
    try:
        return LegalCorpusApprovalAuthorityEvidence(
            approval_evidence_id=payload["approval_evidence_id"],
            schema_version=payload["schema_version"],
            scope=LegalCorpusApprovalAuthorityScope(payload["scope"]),
            operation=LegalCorpusApprovalOperation(payload["operation"]),
            approval_decision=LegalCorpusApprovalDecision(payload["approval_decision"]),
            approval_authority_source=LegalCorpusApprovalAuthoritySource(payload["approval_authority_source"]),
            approval_authority_mechanism=LegalCorpusApprovalAuthorityMechanism(payload["approval_authority_mechanism"]),
            approval_authority_mechanism_version=payload["approval_authority_mechanism_version"],
            human_authority_representation=payload["human_authority_representation"],
            approval_signing_mechanism=LegalCorpusApprovalSigningMechanism(payload["approval_signing_mechanism"]),
            approval_signing_mechanism_version=payload["approval_signing_mechanism_version"],
            approval_signing_key_id=payload["approval_signing_key_id"],
            approval_signature_reference=payload["approval_signature_reference"],
            source_document=_document_from_payload(payload, "source"),
            approved_document=_document_from_payload(payload, "approved"),
            approved_at=_parse_timestamp(payload["approved_at"]),
            effective_from=_parse_timestamp(payload["effective_from"]),
            idempotency_key=payload["idempotency_key"],
            provenance_reference=payload["provenance_reference"],
            evidence_fingerprint=payload["evidence_fingerprint"],
        )
    except (
        KeyError,
        TypeError,
        ValueError,
        OverflowError,
        LegalCorpusApprovalRegistryError,
    ) as error:
        raise LegalCorpusApprovalRegistryError("LEGAL_CORPUS_APPROVAL_PERSISTED_INVALID") from error


def _hydrate(row: Any) -> LegalCorpusApprovalDurableRecord:
    """Hydrate one closed-schema row without claiming current trust."""
    if not isinstance(row, dict) or set(row) - AUTHORIZATION_STRUCTURAL_FIELDS - _ROW_METADATA_FIELDS:
        raise LegalCorpusApprovalRegistryError("LEGAL_CORPUS_APPROVAL_PERSISTED_INVALID")
    if set(row) - _ROW_METADATA_FIELDS != AUTHORIZATION_STRUCTURAL_FIELDS:
        raise LegalCorpusApprovalRegistryError("LEGAL_CORPUS_APPROVAL_PERSISTED_INVALID")
    nested = row.get("approval_evidence")
    nested_evidence = _hydrate_evidence(nested)
    top_fingerprint = row.get("approval_evidence_fingerprint")
    if not isinstance(top_fingerprint, str) or top_fingerprint != nested_evidence.evidence_fingerprint:
        raise LegalCorpusApprovalRegistryError("LEGAL_CORPUS_APPROVAL_PERSISTED_INVALID")
    try:
        authorization = LegalCorpusApprovalAuthorization(
            schema=row["schema"],
            authorization_id=row["authorization_id"],
            issuer_identity=row["issuer_identity"],
            authority_role=row["authority_role"],
            authority_domain=row["authority_domain"],
            algorithm=row["algorithm"],
            key_id=row["key_id"],
            trust_fingerprint=row["trust_fingerprint"],
            operation=LegalCorpusApprovalAuthorizationOperation(row["operation"]),
            scope=LegalCorpusApprovalAuthorizationScope(row["scope"]),
            approval_evidence=nested_evidence,
            issued_at=_parse_timestamp(row["issued_at"]),
            expires_at=_parse_timestamp(row["expires_at"]),
            nonce=row["nonce"],
            idempotency_key=row["idempotency_key"],
            signature_base64url=row["signature_base64url"],
        )
    except (
        KeyError,
        TypeError,
        ValueError,
        OverflowError,
        LegalCorpusApprovalRegistryError,
    ) as error:
        raise LegalCorpusApprovalRegistryError("LEGAL_CORPUS_APPROVAL_PERSISTED_INVALID") from error
    canonical = _durable_document(authorization)
    semantic_row = {key: deepcopy(value) for key, value in row.items() if key != "_id"}
    if _canonical_bytes(canonical) != _canonical_bytes(semantic_row):
        raise LegalCorpusApprovalRegistryError("LEGAL_CORPUS_APPROVAL_PERSISTED_INVALID")
    return LegalCorpusApprovalDurableRecord(authorization, top_fingerprint)


def _read_one(source: Any, query: dict[str, Any], session: Any) -> dict[str, Any] | None:
    """Read one row with caller-session forwarding and bounded errors."""
    try:
        row = source.find_one(query, session=session)
    except PyMongoError as error:
        raise LegalCorpusApprovalRegistryError("LEGAL_CORPUS_APPROVAL_READ_FAILED") from error
    if row is None:
        return None
    if not isinstance(row, dict):
        raise LegalCorpusApprovalRegistryError("LEGAL_CORPUS_APPROVAL_PERSISTED_INVALID")
    return deepcopy(row)


def _identity_queries(authorization: LegalCorpusApprovalAuthorization) -> tuple[tuple[str, dict[str, Any]], ...]:
    """Return all five governed unique-identity selectors."""
    evidence = authorization.approval_evidence
    return (
        (
            "evidence_id",
            {"approval_evidence.approval_evidence_id": evidence.approval_evidence_id},
        ),
        ("authorization_id", {"authorization_id": authorization.authorization_id}),
        (
            "authorization_idempotency",
            {
                "scope": authorization.scope.value,
                "operation": authorization.operation.value,
                "idempotency_key": authorization.idempotency_key,
            },
        ),
        (
            "evidence_idempotency",
            {
                "scope": authorization.scope.value,
                "operation": authorization.operation.value,
                "approval_evidence.idempotency_key": evidence.idempotency_key,
            },
        ),
        (
            "target_version",
            {
                "scope": authorization.scope.value,
                "operation": authorization.operation.value,
                "approval_evidence.approved_document_id": evidence.approved_document_id,
                "approval_evidence.approved_version": evidence.approved_version,
            },
        ),
    )


def _collision_code(selector: str) -> str:
    """Map a unique selector to a stable semantic collision code."""
    if selector == "evidence_id":
        return "LEGAL_CORPUS_APPROVAL_EVIDENCE_ID_COLLISION"
    if selector == "authorization_id":
        return "LEGAL_CORPUS_APPROVAL_AUTHORIZATION_ID_COLLISION"
    if selector in {"authorization_idempotency", "evidence_idempotency"}:
        return "LEGAL_CORPUS_APPROVAL_IDEMPOTENCY_CONFLICT"
    return "LEGAL_CORPUS_APPROVAL_IMMUTABILITY_CONFLICT"


def _physical_key(row: Mapping[str, Any], record: LegalCorpusApprovalDurableRecord) -> bytes | str:
    """Identify one stored row while excluding driver metadata when absent."""
    if "_id" in row:
        return f"mongo:{row['_id']!s}"
    return _canonical_bytes(record.to_document())


def _collect_matches(source: Any, authorization: LegalCorpusApprovalAuthorization, session: Any) -> list[_IdentityMatch]:
    """Read all identity selectors before any admission insert."""
    matches: list[_IdentityMatch] = []
    for selector, query in _identity_queries(authorization):
        row = _read_one(source, query, session)
        if row is not None:
            matches.append(_IdentityMatch(selector, row, _hydrate(row)))
    return matches


def _adjudicate_matches(
    matches: list[_IdentityMatch],
    authorization: LegalCorpusApprovalAuthorization,
    *,
    duplicate_error: DuplicateKeyError | None = None,
) -> LegalCorpusApprovalAdmissionResult:
    """Classify exact, divergent, split, and unavailable identity matches."""
    if not matches:
        error = LegalCorpusApprovalRegistryError("LEGAL_CORPUS_APPROVAL_DUPLICATE_UNAVAILABLE")
        if duplicate_error is None:
            raise error
        raise error from duplicate_error
    target = _durable_document(authorization)
    target_bytes = _canonical_bytes(target)
    physical = {_physical_key(match.row, match.record) for match in matches}
    if len(physical) != 1:
        error = LegalCorpusApprovalRegistryError("LEGAL_CORPUS_APPROVAL_IMMUTABILITY_CONFLICT")
        if duplicate_error is None:
            raise error
        raise error from duplicate_error
    for match in matches:
        if _canonical_bytes(match.record.to_document()) != target_bytes:
            error = LegalCorpusApprovalRegistryError(_collision_code(match.selector))
            if duplicate_error is None:
                raise error
            raise error from duplicate_error
    return LegalCorpusApprovalAdmissionResult(
        LegalCorpusApprovalAdmissionState.EXACT_REPLAY,
        _record_from_authorization(match.record.authorization for match in matches),
    )


def _record_from_authorization(
    authorizations: Any,
) -> LegalCorpusApprovalDurableRecord:
    """Create one immutable unverified record from a converged authorization."""
    authorization = next(iter(authorizations))
    return LegalCorpusApprovalDurableRecord(
        authorization,
        authorization.approval_evidence.evidence_fingerprint,
    )


class LegalCorpusApprovalRegistry:
    """Persist only complete, verified PLATFORM approval evidence.

    ``admit_verified_approval`` accepts the guarded proof returned by the
    governed verifier. It performs no signature verification itself and owns no
    Mongo transaction. The caller must provide the same session to the later
    document registry so both durable rows share one transaction.
    """

    @staticmethod
    def ensure_indexes(collection: Any = None) -> None:
        """Create the exact five unique and two lookup indexes at deployment."""
        source = _target(collection)
        source.create_index(
            [("approval_evidence.approval_evidence_id", 1)],
            unique=True,
            name="legal_corpus_approval_evidence_id_unique",
        )
        source.create_index(
            [("authorization_id", 1)],
            unique=True,
            name="legal_corpus_approval_authorization_id_unique",
        )
        source.create_index(
            [("scope", 1), ("operation", 1), ("idempotency_key", 1)],
            unique=True,
            name="legal_corpus_approval_authorization_idempotency_unique",
        )
        source.create_index(
            [
                ("scope", 1),
                ("operation", 1),
                ("approval_evidence.idempotency_key", 1),
            ],
            unique=True,
            name="legal_corpus_approval_evidence_idempotency_unique",
        )
        source.create_index(
            [
                ("scope", 1),
                ("operation", 1),
                ("approval_evidence.approved_document_id", 1),
                ("approval_evidence.approved_version", 1),
            ],
            unique=True,
            name="legal_corpus_approval_target_version_unique",
        )
        source.create_index(
            [("approval_evidence.evidence_fingerprint", 1)],
            unique=False,
            name="legal_corpus_approval_evidence_fingerprint_lookup",
        )
        source.create_index(
            [
                ("approval_evidence.source_document_id", 1),
                ("approval_evidence.source_version", 1),
            ],
            unique=False,
            name="legal_corpus_approval_source_lookup",
        )

    @staticmethod
    def admit_verified_approval(
        proof: VerifiedLegalCorpusApprovalAuthorization,
        collection: Any = None,
        *,
        session: Any = None,
    ) -> LegalCorpusApprovalAdmissionResult:
        """Admit or replay one proof using only its bound authorization.

        The method never accepts separate evidence or authorization arguments.
        It reads every unique identity before a first insert, forwards the
        caller session to all reads and writes, and returns ``CREATED`` only
        after the insert call succeeds. A successful insert is not a commit
        claim; the caller owns the transaction outcome.
        """
        if not isinstance(proof, VerifiedLegalCorpusApprovalAuthorization):
            raise LegalCorpusApprovalRegistryError("LEGAL_CORPUS_APPROVAL_AUTHORITY_INPUT_INVALID")
        authorization = proof.authorization
        source = _target(collection)
        matches = _collect_matches(source, authorization, session)
        if matches:
            return _adjudicate_matches(matches, authorization)
        payload = _durable_document(authorization)
        insert_payload = deepcopy(payload)
        try:
            source.insert_one(insert_payload, session=session)
        except DuplicateKeyError as error:
            try:
                raced = _collect_matches(source, authorization, session)
                return _adjudicate_matches(raced, authorization, duplicate_error=error)
            except LegalCorpusApprovalRegistryError as reconciliation_error:
                if reconciliation_error.__cause__ is not error:
                    raise reconciliation_error from error
                raise
        except PyMongoError as error:
            raise LegalCorpusApprovalRegistryError("LEGAL_CORPUS_APPROVAL_CREATE_FAILED") from error
        return LegalCorpusApprovalAdmissionResult(
            LegalCorpusApprovalAdmissionState.CREATED,
            LegalCorpusApprovalDurableRecord(
                authorization,
                authorization.approval_evidence.evidence_fingerprint,
            ),
        )

    @staticmethod
    def get_by_approval_evidence_id(
        approval_evidence_id: str,
        collection: Any = None,
        *,
        session: Any = None,
    ) -> LegalCorpusApprovalDurableRecord | None:
        """Read one immutable, non-authoritative record by evidence identity."""
        if not isinstance(approval_evidence_id, str) or not approval_evidence_id.strip():
            raise LegalCorpusApprovalRegistryError("LEGAL_CORPUS_APPROVAL_AUTHORITY_INPUT_INVALID")
        row = _read_one(
            _target(collection),
            {"approval_evidence.approval_evidence_id": approval_evidence_id.strip()},
            session,
        )
        return None if row is None else _hydrate(row)


__all__ = [
    "APPROVAL_EVIDENCE_FIELDS",
    "AUTHORIZATION_STRUCTURAL_FIELDS",
    "COLLECTION",
    "LegalCorpusApprovalAdmissionResult",
    "LegalCorpusApprovalAdmissionState",
    "LegalCorpusApprovalDurableRecord",
    "LegalCorpusApprovalRegistry",
    "LegalCorpusApprovalRegistryError",
    "VERSION",
]


# ARTIFACT: legal_corpus_approval_registry.py
# VERSION: v1.0.0-R1D-B0F-B4-R9B-P3-P1-LEGAL-CORPUS-APPROVAL-REGISTRY
# AUTHORITY BOUNDARY: append-only persistence of already-verified PLATFORM approval evidence
# TENANT POSTURE: no tenant/principal authority; acceptance remains separate
# FAIL-CLOSED POSTURE: closed hydration, identity splits, divergent replay, and duplicate ambiguity reject
# FINANCIAL EXECUTION AUTHORITY: none; Kennel EOS remains exclusive
# END OF WILSY OS SOVEREIGN ARTIFACT
