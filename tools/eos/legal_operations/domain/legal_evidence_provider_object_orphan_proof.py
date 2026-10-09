"""WILSY OS — positive Legal Evidence provider-object orphan proof.

TITLE: Legal Evidence Provider Object Orphan Proof
VERSION: v1.0.0-L10A2R-C4D6D-B1-PROVIDER-OBJECT-ORPHAN-PROOF
AUTHORITY: Wilsy OS Core Governance / Python EOS Legal Operations
EPITOME: Derive one immutable orphan-proof fact only when trusted exhaustive
         provider coverage seals the exact completed object and an already
         authorized durable disownership fact predates or equals that provider
         observation.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tools/eos/legal_operations/domain/legal_evidence_provider_object_orphan_proof.py
COLLABORATION / OWNERSHIP:
    C4D6C-B owns trusted exhaustive coverage and exact completed-observation
    membership evidence. C4D6D-A owns explicit authorized provider-object
    disownership. C4D6D-B1 owns only their fail-closed composition into one
    immutable orphan-proof fact. Later gates own persistence, retention,
    legal-hold governance, deletion authorization and provider deletion.
CERTIFICATION / UPDATE DATE: 2026-10-01
CHANGELOG:
    v1.0.0-L10A2R-C4D6D-B1-PROVIDER-OBJECT-ORPHAN-PROOF establishes exact
    tenant/provider/storage/version correlation, same-service sealed membership,
    positive disownership chronology, explicit proof time, strict hydration and
    deterministic SHA3-512 integrity.

COMPLIANCE:
    POPIA section 19; GDPR Article 32; SOC 2 CC7.2; ISO 27001-aligned
    integrity and tenant-isolation controls.

SECURITY / PRIVACY POSTURE:
    Opaque identifiers, timestamps and SHA3-512 fingerprints only. No provider
    credentials, object bytes, raw legal evidence bodies or financial data.

TENANT BOUNDARY:
    Coverage verification, completed observation and disownership must bind the
    identical tenant and provider object identity. Cross-scope composition fails
    closed.

AUTHORITY BOUNDARY:
    This artifact proves orphan status only for the exact provider object version
    represented by all certified prerequisite evidence.

    Orphan proof does NOT:
    - infer authority from ABSENT or NOT_OBSERVED metadata;
    - infer authority from registry absence or cleanup classification;
    - satisfy retention;
    - release legal hold;
    - authorize abort or deletion;
    - authorize or execute provider mutation;
    - establish billing, payment, settlement or financial execution truth.

CHRONOLOGY:
    disownership.decided_at <= verification.observed_at <= proved_at.
    A provider observation predating disownership is stale for orphan proof.

TRANSACTION / MUTATION BOUNDARY:
    Pure in-memory immutable composition and strict hydration only. No Mongo,
    provider IO, filesystem IO, network IO, transaction ownership or clock read.

FINANCIAL AUTHORITY BOUNDARY:
    None. Kennel EOS remains the exclusive financial execution authority.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
import hashlib
import hmac
import json
import re
from typing import Final, NoReturn

from tools.eos.legal_operations.domain.legal_evidence_provider_object_disownership import (
    LegalEvidenceProviderObjectDisownership,
    LegalEvidenceProviderObjectDisownershipError,
)
from tools.eos.legal_operations.service.legal_evidence_provider_cleanup_discovery_port import (
    LegalEvidenceCompletedObjectObservation,
)
from tools.eos.legal_operations.service.legal_evidence_provider_coverage_verification_service import (
    LegalEvidenceProviderCoverageVerification,
    LegalEvidenceProviderCoverageVerificationService,
)


VERSION: Final[str] = (
    "v1.0.0-L10A2R-C4D6D-B1-PROVIDER-OBJECT-ORPHAN-PROOF"
)

SCHEMA: Final[str] = (
    "wilsy.legal-evidence.provider-object-orphan-proof.v1"
)

_IDENTITY_RE: Final[re.Pattern[str]] = re.compile(
    r"^[A-Za-z0-9][A-Za-z0-9._:-]{0,255}$"
)

_SHA3_512_RE: Final[re.Pattern[str]] = re.compile(
    r"^[0-9a-f]{128}$"
)

_FIELDS: Final[frozenset[str]] = frozenset(
    {
        "tenant_id",
        "provider_name",
        "storage_reference",
        "object_version_reference",
        "orphan_proof_reference",
        "coverage_verification_fingerprint",
        "completed_observation_membership_fingerprint",
        "disownership_reference",
        "disownership_fingerprint",
        "provider_observed_at",
        "disownership_decided_at",
        "proved_at",
        "schema",
        "version",
        "fingerprint",
    }
)


class LegalEvidenceProviderObjectOrphanProofError(
    RuntimeError
):
    """Raised when exact orphan-proof evidence cannot be trusted."""


def _fail(
    code: str,
    cause: BaseException | None = None,
) -> NoReturn:
    error = LegalEvidenceProviderObjectOrphanProofError(
        code
    )

    if cause is None:
        raise error

    raise error from cause


def _identity(
    name: str,
    value: str,
) -> str:
    if (
        not isinstance(value, str)
        or _IDENTITY_RE.fullmatch(value) is None
    ):
        _fail(
            f"L10A2R_C4D6D_B1_{name.upper()}_INVALID"
        )

    return value


def _text(
    name: str,
    value: str,
    *,
    limit: int,
) -> str:
    if (
        not isinstance(value, str)
        or not value
        or value != value.strip()
        or len(value) > limit
        or any(
            character in value
            for character in ("\x00", "\r", "\n")
        )
    ):
        _fail(
            f"L10A2R_C4D6D_B1_{name.upper()}_INVALID"
        )

    return value


def _sha3(
    name: str,
    value: str,
) -> str:
    if (
        not isinstance(value, str)
        or _SHA3_512_RE.fullmatch(value) is None
    ):
        _fail(
            f"L10A2R_C4D6D_B1_{name.upper()}_INVALID"
        )

    return value


def _utc(
    name: str,
    value: datetime,
) -> datetime:
    if (
        not isinstance(value, datetime)
        or value.tzinfo is None
        or value.utcoffset() is None
    ):
        _fail(
            f"L10A2R_C4D6D_B1_{name.upper()}_INVALID"
        )

    return value.astimezone(
        timezone.utc
    )


def _document_str(
    name: str,
    value: object,
) -> str:
    """Return one persisted string field or fail closed."""
    if not isinstance(
        value,
        str,
    ):
        _fail(
            f"L10A2R_C4D6D_B1_{name.upper()}_INVALID"
        )

    return value


def _document_datetime(
    name: str,
    value: object,
) -> datetime:
    """Return one persisted datetime field or fail closed."""
    if not isinstance(
        value,
        datetime,
    ):
        _fail(
            f"L10A2R_C4D6D_B1_{name.upper()}_INVALID"
        )

    return value


def _fingerprint(
    *,
    tenant_id: str,
    provider_name: str,
    storage_reference: str,
    object_version_reference: str,
    orphan_proof_reference: str,
    coverage_verification_fingerprint: str,
    completed_observation_membership_fingerprint: str,
    disownership_reference: str,
    disownership_fingerprint: str,
    provider_observed_at: datetime,
    disownership_decided_at: datetime,
    proved_at: datetime,
) -> str:
    payload = {
        "completed_observation_membership_fingerprint":
            completed_observation_membership_fingerprint,
        "coverage_verification_fingerprint":
            coverage_verification_fingerprint,
        "disownership_decided_at":
            disownership_decided_at.isoformat(),
        "disownership_fingerprint":
            disownership_fingerprint,
        "disownership_reference":
            disownership_reference,
        "object_version_reference":
            object_version_reference,
        "orphan_proof_reference":
            orphan_proof_reference,
        "proved_at":
            proved_at.isoformat(),
        "provider_name":
            provider_name,
        "provider_observed_at":
            provider_observed_at.isoformat(),
        "schema":
            SCHEMA,
        "storage_reference":
            storage_reference,
        "tenant_id":
            tenant_id,
        "version":
            VERSION,
    }

    encoded = json.dumps(
        payload,
        ensure_ascii=False,
        allow_nan=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode(
        "utf-8"
    )

    return hashlib.sha3_512(
        encoded
    ).hexdigest()


@dataclass(
    frozen=True,
    slots=True,
    init=False,
)
class LegalEvidenceProviderObjectOrphanProof:
    """Immutable exact provider-object orphan-proof evidence.

    Authority:
        Proves only orphan status for one exact tenant-scoped provider object
        version from the prerequisite evidence bound into this value.

    Tenant scope:
        tenant_id, provider_name, storage_reference and object_version_reference
        are exact immutable coordinates.

    Mutation / persistence:
        No mutation, provider IO, persistence, transaction ownership or clock
        access. ``from_dict`` performs integrity hydration only; it does not
        perform prerequisite authority discovery.

    Fail-closed behavior:
        Direct construction is forbidden. Malformed or divergent persisted
        fields, chronology or fingerprint reject.

    Financial boundary:
        No financial authority. Kennel EOS remains exclusive.
    """

    tenant_id: str
    provider_name: str
    storage_reference: str
    object_version_reference: str
    orphan_proof_reference: str
    coverage_verification_fingerprint: str
    completed_observation_membership_fingerprint: str
    disownership_reference: str
    disownership_fingerprint: str
    provider_observed_at: datetime
    disownership_decided_at: datetime
    proved_at: datetime
    schema: str
    version: str
    fingerprint: str

    def __init__(
        self,
        *args: object,
        **kwargs: object,
    ) -> None:
        """Reject public construction; use the certified factory or hydration."""
        _fail(
            "L10A2R_C4D6D_B1_ORPHAN_PROOF_FACTORY_REQUIRED"
        )

    def __post_init__(
        self,
    ) -> None:
        """Revalidate immutable shape, chronology and fingerprint integrity."""
        tenant = _identity(
            "tenant_id",
            self.tenant_id,
        )
        provider = _identity(
            "provider_name",
            self.provider_name,
        )
        storage = _text(
            "storage_reference",
            self.storage_reference,
            limit=2048,
        )
        object_version = _text(
            "object_version_reference",
            self.object_version_reference,
            limit=1024,
        )
        reference = _identity(
            "orphan_proof_reference",
            self.orphan_proof_reference,
        )
        coverage_fingerprint = _sha3(
            "coverage_verification_fingerprint",
            self.coverage_verification_fingerprint,
        )
        membership_fingerprint = _sha3(
            "completed_observation_membership_fingerprint",
            self.completed_observation_membership_fingerprint,
        )
        disownership_reference = _identity(
            "disownership_reference",
            self.disownership_reference,
        )
        disownership_fingerprint = _sha3(
            "disownership_fingerprint",
            self.disownership_fingerprint,
        )
        observed = _utc(
            "provider_observed_at",
            self.provider_observed_at,
        )
        disowned = _utc(
            "disownership_decided_at",
            self.disownership_decided_at,
        )
        proved = _utc(
            "proved_at",
            self.proved_at,
        )

        if self.schema != SCHEMA:
            _fail(
                "L10A2R_C4D6D_B1_SCHEMA_INVALID"
            )

        if self.version != VERSION:
            _fail(
                "L10A2R_C4D6D_B1_VERSION_INVALID"
            )

        if disowned > observed:
            _fail(
                "L10A2R_C4D6D_B1_DISOWNERSHIP_AFTER_OBSERVATION"
            )

        if proved < observed or proved < disowned:
            _fail(
                "L10A2R_C4D6D_B1_PROOF_CHRONOLOGY_INVALID"
            )

        digest = _fingerprint(
            tenant_id=tenant,
            provider_name=provider,
            storage_reference=storage,
            object_version_reference=object_version,
            orphan_proof_reference=reference,
            coverage_verification_fingerprint=coverage_fingerprint,
            completed_observation_membership_fingerprint=membership_fingerprint,
            disownership_reference=disownership_reference,
            disownership_fingerprint=disownership_fingerprint,
            provider_observed_at=observed,
            disownership_decided_at=disowned,
            proved_at=proved,
        )

        if (
            not isinstance(self.fingerprint, str)
            or not hmac.compare_digest(
                self.fingerprint,
                digest,
            )
        ):
            _fail(
                "L10A2R_C4D6D_B1_FINGERPRINT_MISMATCH"
            )

        object.__setattr__(
            self,
            "tenant_id",
            tenant,
        )
        object.__setattr__(
            self,
            "provider_name",
            provider,
        )
        object.__setattr__(
            self,
            "storage_reference",
            storage,
        )
        object.__setattr__(
            self,
            "object_version_reference",
            object_version,
        )
        object.__setattr__(
            self,
            "orphan_proof_reference",
            reference,
        )
        object.__setattr__(
            self,
            "coverage_verification_fingerprint",
            coverage_fingerprint,
        )
        object.__setattr__(
            self,
            "completed_observation_membership_fingerprint",
            membership_fingerprint,
        )
        object.__setattr__(
            self,
            "disownership_reference",
            disownership_reference,
        )
        object.__setattr__(
            self,
            "disownership_fingerprint",
            disownership_fingerprint,
        )
        object.__setattr__(
            self,
            "provider_observed_at",
            observed,
        )
        object.__setattr__(
            self,
            "disownership_decided_at",
            disowned,
        )
        object.__setattr__(
            self,
            "proved_at",
            proved,
        )
        object.__setattr__(
            self,
            "schema",
            SCHEMA,
        )
        object.__setattr__(
            self,
            "version",
            VERSION,
        )
        object.__setattr__(
            self,
            "fingerprint",
            digest,
        )

    def to_dict(
        self,
    ) -> dict[str, object]:
        """Serialize the complete immutable evidence value without mutation."""
        self.__post_init__()

        return {
            "tenant_id":
                self.tenant_id,
            "provider_name":
                self.provider_name,
            "storage_reference":
                self.storage_reference,
            "object_version_reference":
                self.object_version_reference,
            "orphan_proof_reference":
                self.orphan_proof_reference,
            "coverage_verification_fingerprint":
                self.coverage_verification_fingerprint,
            "completed_observation_membership_fingerprint":
                self.completed_observation_membership_fingerprint,
            "disownership_reference":
                self.disownership_reference,
            "disownership_fingerprint":
                self.disownership_fingerprint,
            "provider_observed_at":
                self.provider_observed_at,
            "disownership_decided_at":
                self.disownership_decided_at,
            "proved_at":
                self.proved_at,
            "schema":
                self.schema,
            "version":
                self.version,
            "fingerprint":
                self.fingerprint,
        }

    @classmethod
    def from_dict(
        cls,
        value: dict[str, object],
    ) -> "LegalEvidenceProviderObjectOrphanProof":
        """Strictly hydrate exact persisted bytes and verify their fingerprint.

        Hydration proves integrity of supplied persisted evidence only. It does
        not independently rediscover coverage, disownership or provider state.
        """
        if not isinstance(
            value,
            dict,
        ):
            _fail(
                "L10A2R_C4D6D_B1_DOCUMENT_INVALID"
            )

        if set(value) != _FIELDS:
            _fail(
                "L10A2R_C4D6D_B1_DOCUMENT_FIELDS_INVALID"
            )

        tenant_id = _document_str(
            "tenant_id",
            value["tenant_id"],
        )
        provider_name = _document_str(
            "provider_name",
            value["provider_name"],
        )
        storage_reference = _document_str(
            "storage_reference",
            value["storage_reference"],
        )
        object_version_reference = _document_str(
            "object_version_reference",
            value["object_version_reference"],
        )
        orphan_proof_reference = _document_str(
            "orphan_proof_reference",
            value["orphan_proof_reference"],
        )
        coverage_verification_fingerprint = _document_str(
            "coverage_verification_fingerprint",
            value["coverage_verification_fingerprint"],
        )
        membership_fingerprint = _document_str(
            "completed_observation_membership_fingerprint",
            value["completed_observation_membership_fingerprint"],
        )
        disownership_reference = _document_str(
            "disownership_reference",
            value["disownership_reference"],
        )
        disownership_fingerprint = _document_str(
            "disownership_fingerprint",
            value["disownership_fingerprint"],
        )
        provider_observed_at = _document_datetime(
            "provider_observed_at",
            value["provider_observed_at"],
        )
        disownership_decided_at = _document_datetime(
            "disownership_decided_at",
            value["disownership_decided_at"],
        )
        proved_at = _document_datetime(
            "proved_at",
            value["proved_at"],
        )
        schema = _document_str(
            "schema",
            value["schema"],
        )
        version = _document_str(
            "version",
            value["version"],
        )
        fingerprint = _document_str(
            "fingerprint",
            value["fingerprint"],
        )

        return _build_orphan_proof(
            tenant_id=tenant_id,
            provider_name=provider_name,
            storage_reference=storage_reference,
            object_version_reference=object_version_reference,
            orphan_proof_reference=orphan_proof_reference,
            coverage_verification_fingerprint=coverage_verification_fingerprint,
            completed_observation_membership_fingerprint=membership_fingerprint,
            disownership_reference=disownership_reference,
            disownership_fingerprint=disownership_fingerprint,
            provider_observed_at=provider_observed_at,
            disownership_decided_at=disownership_decided_at,
            proved_at=proved_at,
            schema=schema,
            version=version,
            persisted_fingerprint=fingerprint,
        )


def _build_orphan_proof(
    *,
    tenant_id: str,
    provider_name: str,
    storage_reference: str,
    object_version_reference: str,
    orphan_proof_reference: str,
    coverage_verification_fingerprint: str,
    completed_observation_membership_fingerprint: str,
    disownership_reference: str,
    disownership_fingerprint: str,
    provider_observed_at: datetime,
    disownership_decided_at: datetime,
    proved_at: datetime,
    schema: str,
    version: str,
    persisted_fingerprint: str | None,
) -> LegalEvidenceProviderObjectOrphanProof:
    """Create one internally validated value for factory issuance or hydration."""
    tenant = _identity(
        "tenant_id",
        tenant_id,
    )
    provider = _identity(
        "provider_name",
        provider_name,
    )
    storage = _text(
        "storage_reference",
        storage_reference,
        limit=2048,
    )
    object_version = _text(
        "object_version_reference",
        object_version_reference,
        limit=1024,
    )
    reference = _identity(
        "orphan_proof_reference",
        orphan_proof_reference,
    )
    coverage_fingerprint = _sha3(
        "coverage_verification_fingerprint",
        coverage_verification_fingerprint,
    )
    membership_fingerprint = _sha3(
        "completed_observation_membership_fingerprint",
        completed_observation_membership_fingerprint,
    )
    disownership_ref = _identity(
        "disownership_reference",
        disownership_reference,
    )
    disownership_fp = _sha3(
        "disownership_fingerprint",
        disownership_fingerprint,
    )
    observed = _utc(
        "provider_observed_at",
        provider_observed_at,
    )
    disowned = _utc(
        "disownership_decided_at",
        disownership_decided_at,
    )
    proved = _utc(
        "proved_at",
        proved_at,
    )

    if schema != SCHEMA:
        _fail(
            "L10A2R_C4D6D_B1_SCHEMA_INVALID"
        )

    if version != VERSION:
        _fail(
            "L10A2R_C4D6D_B1_VERSION_INVALID"
        )

    if disowned > observed:
        _fail(
            "L10A2R_C4D6D_B1_DISOWNERSHIP_AFTER_OBSERVATION"
        )

    if proved < observed or proved < disowned:
        _fail(
            "L10A2R_C4D6D_B1_PROOF_CHRONOLOGY_INVALID"
        )

    digest = _fingerprint(
        tenant_id=tenant,
        provider_name=provider,
        storage_reference=storage,
        object_version_reference=object_version,
        orphan_proof_reference=reference,
        coverage_verification_fingerprint=coverage_fingerprint,
        completed_observation_membership_fingerprint=membership_fingerprint,
        disownership_reference=disownership_ref,
        disownership_fingerprint=disownership_fp,
        provider_observed_at=observed,
        disownership_decided_at=disowned,
        proved_at=proved,
    )

    if persisted_fingerprint is not None:
        persisted = _sha3(
            "fingerprint",
            persisted_fingerprint,
        )

        if not hmac.compare_digest(
            persisted,
            digest,
        ):
            _fail(
                "L10A2R_C4D6D_B1_FINGERPRINT_MISMATCH"
            )

    value = object.__new__(
        LegalEvidenceProviderObjectOrphanProof
    )

    for name, item in (
        ("tenant_id", tenant),
        ("provider_name", provider),
        ("storage_reference", storage),
        ("object_version_reference", object_version),
        ("orphan_proof_reference", reference),
        (
            "coverage_verification_fingerprint",
            coverage_fingerprint,
        ),
        (
            "completed_observation_membership_fingerprint",
            membership_fingerprint,
        ),
        (
            "disownership_reference",
            disownership_ref,
        ),
        (
            "disownership_fingerprint",
            disownership_fp,
        ),
        (
            "provider_observed_at",
            observed,
        ),
        (
            "disownership_decided_at",
            disowned,
        ),
        ("proved_at", proved),
        ("schema", SCHEMA),
        ("version", VERSION),
        ("fingerprint", digest),
    ):
        object.__setattr__(
            value,
            name,
            item,
        )

    value.__post_init__()

    return value


def prove_legal_evidence_provider_object_orphan(
    *,
    coverage_service: LegalEvidenceProviderCoverageVerificationService,
    verification: LegalEvidenceProviderCoverageVerification,
    observation: LegalEvidenceCompletedObjectObservation,
    disownership: LegalEvidenceProviderObjectDisownership,
    orphan_proof_reference: str,
    proved_at: datetime,
) -> LegalEvidenceProviderObjectOrphanProof:
    """Derive orphan proof from exact certified prerequisite evidence.

    Authority:
        Produces one orphan-proof fact only. It does not satisfy retention,
        release legal hold, authorize abort/deletion, mutate provider storage,
        create persistence or establish financial authority.

    Tenant and provider scope:
        Verification, completed observation and durable authorized disownership
        must correlate on exact tenant and provider identity; observation and
        disownership must also correlate on exact storage/version coordinates.

    Mutation / persistence / transaction ownership:
        Pure in-memory composition. No persistence, transaction lifecycle,
        provider IO, clock read, network IO or retry behavior.

    Fail-closed behavior:
        Cross-service or fabricated verification, unsealed observation,
        malformed/tampered prerequisite evidence, identity divergence, stale
        pre-disownership provider observation or invalid proof chronology rejects.

    Financial boundary:
        None. Kennel EOS remains the exclusive financial execution authority.
    """
    if (
        type(coverage_service)
        is not LegalEvidenceProviderCoverageVerificationService
    ):
        _fail(
            "L10A2R_C4D6D_B1_COVERAGE_SERVICE_REQUIRED"
        )

    if (
        type(verification)
        is not LegalEvidenceProviderCoverageVerification
    ):
        _fail(
            "L10A2R_C4D6D_B1_VERIFICATION_REQUIRED"
        )

    if (
        type(observation)
        is not LegalEvidenceCompletedObjectObservation
    ):
        _fail(
            "L10A2R_C4D6D_B1_COMPLETED_OBSERVATION_REQUIRED"
        )

    if (
        type(disownership)
        is not LegalEvidenceProviderObjectDisownership
    ):
        _fail(
            "L10A2R_C4D6D_B1_DISOWNERSHIP_REQUIRED"
        )

    if not coverage_service.accepts_verification(
        verification
    ):
        _fail(
            "L10A2R_C4D6D_B1_VERIFICATION_NOT_ACCEPTED"
        )

    try:
        observation.__post_init__()
        disownership.__post_init__()
    except (
        LegalEvidenceProviderObjectDisownershipError,
        RuntimeError,
        TypeError,
        ValueError,
    ) as error:
        _fail(
            "L10A2R_C4D6D_B1_PREREQUISITE_INVALID",
            error,
        )

    membership_fingerprint = (
        coverage_service
        .completed_observation_membership_fingerprint(
            verified=verification,
            observation=observation,
        )
    )

    if membership_fingerprint is None:
        _fail(
            "L10A2R_C4D6D_B1_OBSERVATION_NOT_VERIFIED"
        )

    if (
        verification.tenant_id != observation.tenant_id
        or verification.tenant_id != disownership.tenant_id
    ):
        _fail(
            "L10A2R_C4D6D_B1_TENANT_SCOPE_MISMATCH"
        )

    if (
        verification.provider_name != observation.provider_name
        or verification.provider_name != disownership.provider_name
    ):
        _fail(
            "L10A2R_C4D6D_B1_PROVIDER_SCOPE_MISMATCH"
        )

    if (
        observation.storage_reference
        != disownership.storage_reference
    ):
        _fail(
            "L10A2R_C4D6D_B1_STORAGE_REFERENCE_MISMATCH"
        )

    if (
        observation.object_version_reference
        != disownership.object_version_reference
    ):
        _fail(
            "L10A2R_C4D6D_B1_OBJECT_VERSION_MISMATCH"
        )

    observed = _utc(
        "provider_observed_at",
        verification.observed_at,
    )
    observation_observed = _utc(
        "observation_observed_at",
        observation.observed_at,
    )
    disowned = _utc(
        "disownership_decided_at",
        disownership.decided_at,
    )
    proved = _utc(
        "proved_at",
        proved_at,
    )

    if not hmac.compare_digest(
        verification.fingerprint,
        _sha3(
            "coverage_verification_fingerprint",
            verification.fingerprint,
        ),
    ):
        _fail(
            "L10A2R_C4D6D_B1_VERIFICATION_FINGERPRINT_INVALID"
        )

    if observation_observed != observed:
        _fail(
            "L10A2R_C4D6D_B1_OBSERVATION_TIME_MISMATCH"
        )

    if disowned > observed:
        _fail(
            "L10A2R_C4D6D_B1_DISOWNERSHIP_AFTER_OBSERVATION"
        )

    if proved < observed or proved < disowned:
        _fail(
            "L10A2R_C4D6D_B1_PROOF_CHRONOLOGY_INVALID"
        )

    return _build_orphan_proof(
        tenant_id=verification.tenant_id,
        provider_name=verification.provider_name,
        storage_reference=observation.storage_reference,
        object_version_reference=observation.object_version_reference,
        orphan_proof_reference=orphan_proof_reference,
        coverage_verification_fingerprint=verification.fingerprint,
        completed_observation_membership_fingerprint=membership_fingerprint,
        disownership_reference=disownership.disownership_reference,
        disownership_fingerprint=disownership.fingerprint,
        provider_observed_at=observed,
        disownership_decided_at=disowned,
        proved_at=proved,
        schema=SCHEMA,
        version=VERSION,
        persisted_fingerprint=None,
    )


__all__ = [
    "SCHEMA",
    "VERSION",
    "LegalEvidenceProviderObjectOrphanProof",
    "LegalEvidenceProviderObjectOrphanProofError",
    "prove_legal_evidence_provider_object_orphan",
]


# ARTIFACT: legal_evidence_provider_object_orphan_proof.py
# VERSION: v1.0.0-L10A2R-C4D6D-B1-PROVIDER-OBJECT-ORPHAN-PROOF
# AUTHORITY BOUNDARY: exact positive provider-object orphan proof only
# TENANT POSTURE: exact tenant/provider/storage/version prerequisite correlation
# COVERAGE POSTURE: exact same-service sealed completed-observation membership required
# DISOWNERSHIP POSTURE: explicit durable authorized disownership evidence required
# TIME POSTURE: disownership <= provider observation <= proof time
# RETENTION / HOLD POSTURE: no retention satisfaction or legal-hold release authority
# DELETION POSTURE: no abort, deletion authorization or provider deletion authority
# PERSISTENCE POSTURE: no registry or durable persistence authority
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively
# FAIL-CLOSED POSTURE: malformed, divergent, stale or fabricated prerequisite evidence rejects
# END OF WILSY OS SOVEREIGN ARTIFACT
