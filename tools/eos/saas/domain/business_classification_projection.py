# -*- coding: utf-8 -*-
"""
===============================================================================
WILSY OS — SOVEREIGN PRODUCTION ARTIFACT
BUSINESS CLASSIFICATION PROJECTION DOMAIN
===============================================================================

TITLE:
    WILSY OS Business Classification Projection Domain

VERSION:
    v1.0.0-WILSY-BUSINESS-CLASSIFICATION-PROJECTION

AUTHORITY:
    Wilsy OS Core Governance

EPITOME:
    Immutable tenant-bound business-activity classification projection that
    separates captured business evidence from classification references,
    preserves primary and secondary activities, binds external taxonomy
    references to exact versioned snapshots, and provides deterministic
    cryptographic integrity without granting commercial, authorization,
    service-pack, AI-execution, or financial authority.

ABSOLUTE CANONICAL PATH:
    /Users/wilsonkhanyezi/legal-doc-system/tools/eos/saas/domain/business_classification_projection.py

COLLABORATION / OWNERSHIP:
    Wilson Khanyezi / Wilsy Core Engineering

CERTIFICATION / UPDATE DATE:
    2026-10-07

CHANGELOG:
    v1.0.0-WILSY-BUSINESS-CLASSIFICATION-PROJECTION
        - Introduces immutable tenant-scoped business classification projection.
        - Supports exactly one primary activity and zero or more secondary
          activities.
        - Supports multiple external taxonomy references per activity.
        - Binds every taxonomy reference to an exact scheme version and immutable
          source snapshot digest.
        - Captures source evidence provenance independently from classification.
        - Supports proposed versus confirmed classification state.
        - Encodes confidence as integer basis points.
        - Binds projections to an exact tenant-profile source snapshot digest.
        - Supports immutable historical supersession across revisions.
        - Provides strict serialization, hydration, and SHA3-512 integrity.
        - Excludes entitlement, authorization, service-pack activation, live-web
          execution, AI authority, payment, settlement and financial execution.

COMPLIANCE:
    Tenant-scoped provenance and integrity support POPIA section 19,
    GDPR Article 32, and SOC 2 evidence expectations.

SECURITY / PRIVACY POSTURE:
    All identifiers and evidence coordinates are validated fail-closed.
    Hydration rejects missing, extra, malformed and cryptographically corrupt
    payloads. Fingerprints are never repaired during hydration.

TENANT BOUNDARY:
    Every projection belongs to exactly one explicit non-global tenant.
    Global, wildcard, master and sovereign-root tenant scopes are prohibited.

AUTHORITY BOUNDARY:
    This module represents classification evidence and immutable classification
    truth only. It grants no subscription feature, entitlement, permission,
    authorization role, business role, record scope, service pack, dashboard,
    workflow, or AI authority.

FINANCIAL AUTHORITY BOUNDARY:
    This module has no payment, billing, settlement, treasury, banking, tender,
    accounting, provider-execution, or financial-execution authority.
    Kennel EOS remains the exclusive financial execution authority.

TAXONOMY BOUNDARY:
    External schemes such as ISIC, SIC, NACE and NAICS are referenced only
    through explicit scheme/version/code/snapshot coordinates. This module does
    not download taxonomies, prove external code membership, or assert that
    correspondence mappings are equivalent.

AI BOUNDARY:
    AI inference is not evidence authority. AI may later consume or propose
    classification candidates through separately governed orchestration, but it
    cannot silently confirm or mutate this immutable domain.

RUNTIME SIDE EFFECTS:
    None. Pure domain only.
===============================================================================
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
import hashlib
import json
from typing import Any, Final, Mapping

VERSION: Final[str] = (
    "v1.0.0-WILSY-BUSINESS-CLASSIFICATION-PROJECTION"
)

SCHEMA_VERSION: Final[str] = (
    "wilsy.business.classification.projection.v1"
)

_SHA3_512_HEX_LENGTH: Final[int] = 128

_LOWER_HEX: Final[frozenset[str]] = frozenset(
    "0123456789abcdef"
)

_FORBIDDEN_TENANT_IDS: Final[frozenset[str]] = frozenset(
    {
        "default",
        "global",
        "root",
        "*",
        "master",
        "global_root",
        "sovereign_root",
        "wilsy-sovereign-root",
    }
)


class BusinessClassificationProjectionError(ValueError):
    """Represent fail-closed business-classification validation or integrity failure.

    This exception creates no persistence, entitlement, authorization,
    commercial, service-pack, AI, payment, settlement, or financial truth.
    """


class BusinessActivityRole(str, Enum):
    """Identify whether an economic activity is primary or secondary.

    This is classification semantics only and is never an authorization role.
    """

    PRIMARY = "primary"
    SECONDARY = "secondary"


class BusinessActivityConfirmation(str, Enum):
    """Represent proposed versus explicitly confirmed classification state."""

    PROPOSED = "proposed"
    CONFIRMED = "confirmed"


class BusinessClassificationSourceKind(str, Enum):
    """Identify the provenance class of captured classification evidence.

    AI is deliberately absent because inference is advisory analysis, not source
    authority.
    """

    TENANT_DECLARATION = "tenant_declaration"
    OFFICIAL_REGISTRY = "official_registry"
    OFFICIAL_DOCUMENT = "official_document"
    FIRST_PARTY_SOURCE = "first_party_source"
    OPERATOR_VERIFICATION = "operator_verification"
    RESEARCH_CAPTURE = "research_capture"


def _exact_text(
    name: str,
    value: object,
) -> str:
    """Return exact non-empty non-padded text or fail closed."""
    if not isinstance(value, str):
        raise BusinessClassificationProjectionError(
            f"BUSINESS_CLASSIFICATION_{name.upper()}_INVALID"
        )

    if not value or value != value.strip():
        raise BusinessClassificationProjectionError(
            f"BUSINESS_CLASSIFICATION_{name.upper()}_INVALID"
        )

    return value


def _optional_exact_text(
    name: str,
    value: object,
) -> str | None:
    """Return optional exact text without normalizing caller truth."""
    if value is None:
        return None

    return _exact_text(name, value)


def _tenant_id(
    value: object,
) -> str:
    """Validate an explicit non-global tenant identifier."""
    tenant_id = _exact_text(
        "tenant_id",
        value,
    )

    if tenant_id.lower() in _FORBIDDEN_TENANT_IDS:
        raise BusinessClassificationProjectionError(
            "BUSINESS_CLASSIFICATION_TENANT_ID_FORBIDDEN"
        )

    return tenant_id


def _lower_sha3_512(
    name: str,
    value: object,
) -> str:
    """Validate exact lowercase SHA3-512 hexadecimal shape."""
    digest = _exact_text(
        name,
        value,
    )

    if (
        len(digest) != _SHA3_512_HEX_LENGTH
        or any(
            character not in _LOWER_HEX
            for character in digest
        )
    ):
        raise BusinessClassificationProjectionError(
            f"BUSINESS_CLASSIFICATION_{name.upper()}_INVALID"
        )

    return digest


def _aware_utc(
    name: str,
    value: object,
) -> datetime:
    """Validate an aware datetime and preserve the instant in UTC."""
    if (
        not isinstance(value, datetime)
        or value.tzinfo is None
        or value.utcoffset() is None
    ):
        raise BusinessClassificationProjectionError(
            f"BUSINESS_CLASSIFICATION_{name.upper()}_INVALID"
        )

    return value.astimezone(timezone.utc)


def _strict_int(
    name: str,
    value: object,
    *,
    minimum: int,
    maximum: int | None = None,
) -> int:
    """Validate an actual integer, excluding bool and invalid ranges."""
    if (
        isinstance(value, bool)
        or not isinstance(value, int)
    ):
        raise BusinessClassificationProjectionError(
            f"BUSINESS_CLASSIFICATION_{name.upper()}_INVALID"
        )

    if value < minimum:
        raise BusinessClassificationProjectionError(
            f"BUSINESS_CLASSIFICATION_{name.upper()}_INVALID"
        )

    if (
        maximum is not None
        and value > maximum
    ):
        raise BusinessClassificationProjectionError(
            f"BUSINESS_CLASSIFICATION_{name.upper()}_INVALID"
        )

    return value


def _enum_member(
    name: str,
    value: object,
    enum_type: type[Enum],
) -> Enum:
    """Resolve one exact closed-vocabulary enum value."""
    if isinstance(value, enum_type):
        return value

    if not isinstance(value, str):
        raise BusinessClassificationProjectionError(
            f"BUSINESS_CLASSIFICATION_{name.upper()}_INVALID"
        )

    try:
        return enum_type(value)
    except ValueError as error:
        raise BusinessClassificationProjectionError(
            f"BUSINESS_CLASSIFICATION_{name.upper()}_INVALID"
        ) from error


def _tuple_of_exact_text(
    name: str,
    value: object,
) -> tuple[str, ...]:
    """Validate a non-empty unique sequence of exact text references."""
    if not isinstance(
        value,
        (tuple, list),
    ):
        raise BusinessClassificationProjectionError(
            f"BUSINESS_CLASSIFICATION_{name.upper()}_INVALID"
        )

    result = tuple(
        _exact_text(
            name,
            entry,
        )
        for entry in value
    )

    if not result:
        raise BusinessClassificationProjectionError(
            f"BUSINESS_CLASSIFICATION_{name.upper()}_EMPTY"
        )

    if len(result) != len(set(result)):
        raise BusinessClassificationProjectionError(
            f"BUSINESS_CLASSIFICATION_{name.upper()}_DUPLICATE"
        )

    return result


def _strict_mapping(
    value: object,
    *,
    expected_keys: frozenset[str],
    surface: str,
) -> Mapping[str, Any]:
    """Require one exact serialized mapping shape."""
    if not isinstance(value, Mapping):
        raise BusinessClassificationProjectionError(
            f"BUSINESS_CLASSIFICATION_{surface}_INVALID"
        )

    if frozenset(value.keys()) != expected_keys:
        raise BusinessClassificationProjectionError(
            f"BUSINESS_CLASSIFICATION_{surface}_SHAPE_INVALID"
        )

    return value


@dataclass(frozen=True, slots=True)
class BusinessClassificationEvidence:
    """Capture immutable source evidence supporting business classification.

    Evidence records provenance only. It cannot confirm a classification,
    activate a workflow, grant entitlement, authorize a principal, or create
    financial truth.
    """

    evidence_id: str
    source_kind: BusinessClassificationSourceKind
    source_reference: str
    observed_at: datetime
    source_digest: str

    def __post_init__(self) -> None:
        """Validate and canonicalize immutable evidence coordinates."""
        object.__setattr__(
            self,
            "evidence_id",
            _exact_text(
                "evidence_id",
                self.evidence_id,
            ),
        )

        object.__setattr__(
            self,
            "source_kind",
            _enum_member(
                "source_kind",
                self.source_kind,
                BusinessClassificationSourceKind,
            ),
        )

        object.__setattr__(
            self,
            "source_reference",
            _exact_text(
                "source_reference",
                self.source_reference,
            ),
        )

        object.__setattr__(
            self,
            "observed_at",
            _aware_utc(
                "observed_at",
                self.observed_at,
            ),
        )

        object.__setattr__(
            self,
            "source_digest",
            _lower_sha3_512(
                "source_digest",
                self.source_digest,
            ),
        )

    def to_dict(self) -> dict[str, Any]:
        """Serialize exact evidence truth without creating authority."""
        return {
            "evidence_id": self.evidence_id,
            "source_kind": self.source_kind.value,
            "source_reference": self.source_reference,
            "observed_at": self.observed_at.isoformat(),
            "source_digest": self.source_digest,
        }

    @classmethod
    def from_dict(
        cls,
        payload: Mapping[str, Any],
    ) -> BusinessClassificationEvidence:
        """Hydrate strict evidence truth and reject shape widening."""
        expected = frozenset(
            {
                "evidence_id",
                "source_kind",
                "source_reference",
                "observed_at",
                "source_digest",
            }
        )

        value = _strict_mapping(
            payload,
            expected_keys=expected,
            surface="EVIDENCE",
        )

        try:
            observed_at = datetime.fromisoformat(
                value["observed_at"]
            )
        except (
            TypeError,
            ValueError,
        ) as error:
            raise BusinessClassificationProjectionError(
                "BUSINESS_CLASSIFICATION_OBSERVED_AT_INVALID"
            ) from error

        return cls(
            evidence_id=value["evidence_id"],
            source_kind=value["source_kind"],
            source_reference=value["source_reference"],
            observed_at=observed_at,
            source_digest=value["source_digest"],
        )


@dataclass(frozen=True, slots=True)
class BusinessClassificationReference:
    """Reference one code in one exact external taxonomy snapshot.

    This object records coordinates only. It does not prove source publication
    authenticity, code membership, or correspondence equivalence.
    """

    scheme_id: str
    scheme_version: str
    code: str
    title: str
    jurisdiction: str
    taxonomy_snapshot_id: str
    taxonomy_snapshot_digest: str

    def __post_init__(self) -> None:
        """Validate immutable taxonomy coordinates and source-snapshot binding."""
        for field_name in (
            "scheme_id",
            "scheme_version",
            "code",
            "title",
            "jurisdiction",
            "taxonomy_snapshot_id",
        ):
            object.__setattr__(
                self,
                field_name,
                _exact_text(
                    field_name,
                    getattr(
                        self,
                        field_name,
                    ),
                ),
            )

        object.__setattr__(
            self,
            "taxonomy_snapshot_digest",
            _lower_sha3_512(
                "taxonomy_snapshot_digest",
                self.taxonomy_snapshot_digest,
            ),
        )

    def coordinate(
        self,
    ) -> tuple[str, str, str, str, str]:
        """Return exact uniqueness coordinates for one taxonomy reference."""
        return (
            self.scheme_id,
            self.scheme_version,
            self.code,
            self.jurisdiction,
            self.taxonomy_snapshot_id,
        )

    def to_dict(self) -> dict[str, Any]:
        """Serialize exact taxonomy-reference truth."""
        return {
            "scheme_id": self.scheme_id,
            "scheme_version": self.scheme_version,
            "code": self.code,
            "title": self.title,
            "jurisdiction": self.jurisdiction,
            "taxonomy_snapshot_id": self.taxonomy_snapshot_id,
            "taxonomy_snapshot_digest": self.taxonomy_snapshot_digest,
        }

    @classmethod
    def from_dict(
        cls,
        payload: Mapping[str, Any],
    ) -> BusinessClassificationReference:
        """Hydrate an exact taxonomy reference without silent normalization."""
        expected = frozenset(
            {
                "scheme_id",
                "scheme_version",
                "code",
                "title",
                "jurisdiction",
                "taxonomy_snapshot_id",
                "taxonomy_snapshot_digest",
            }
        )

        value = _strict_mapping(
            payload,
            expected_keys=expected,
            surface="REFERENCE",
        )

        return cls(
            scheme_id=value["scheme_id"],
            scheme_version=value["scheme_version"],
            code=value["code"],
            title=value["title"],
            jurisdiction=value["jurisdiction"],
            taxonomy_snapshot_id=value["taxonomy_snapshot_id"],
            taxonomy_snapshot_digest=value[
                "taxonomy_snapshot_digest"
            ],
        )


@dataclass(frozen=True, slots=True)
class BusinessActivity:
    """Represent one immutable primary or secondary business activity.

    `role` is classification semantics only: primary versus secondary. It is
    never an authorization, business-role, membership, permission, or grant.
    """

    activity_id: str
    role: BusinessActivityRole
    description: str
    confirmation: BusinessActivityConfirmation
    confidence_basis_points: int
    evidence_refs: tuple[str, ...]
    classifications: tuple[
        BusinessClassificationReference,
        ...,
    ]

    def __post_init__(self) -> None:
        """Validate activity semantics, evidence references and mappings."""
        object.__setattr__(
            self,
            "activity_id",
            _exact_text(
                "activity_id",
                self.activity_id,
            ),
        )

        object.__setattr__(
            self,
            "role",
            _enum_member(
                "activity_role",
                self.role,
                BusinessActivityRole,
            ),
        )

        object.__setattr__(
            self,
            "description",
            _exact_text(
                "activity_description",
                self.description,
            ),
        )

        object.__setattr__(
            self,
            "confirmation",
            _enum_member(
                "activity_confirmation",
                self.confirmation,
                BusinessActivityConfirmation,
            ),
        )

        object.__setattr__(
            self,
            "confidence_basis_points",
            _strict_int(
                "confidence_basis_points",
                self.confidence_basis_points,
                minimum=0,
                maximum=10000,
            ),
        )

        object.__setattr__(
            self,
            "evidence_refs",
            _tuple_of_exact_text(
                "evidence_refs",
                self.evidence_refs,
            ),
        )

        if not isinstance(
            self.classifications,
            (tuple, list),
        ):
            raise BusinessClassificationProjectionError(
                "BUSINESS_CLASSIFICATION_REFERENCES_INVALID"
            )

        classifications = tuple(
            self.classifications
        )

        if not classifications:
            raise BusinessClassificationProjectionError(
                "BUSINESS_CLASSIFICATION_REFERENCES_EMPTY"
            )

        if not all(
            isinstance(
                entry,
                BusinessClassificationReference,
            )
            for entry in classifications
        ):
            raise BusinessClassificationProjectionError(
                "BUSINESS_CLASSIFICATION_REFERENCES_INVALID"
            )

        coordinates = tuple(
            entry.coordinate()
            for entry in classifications
        )

        if len(coordinates) != len(
            set(coordinates)
        ):
            raise BusinessClassificationProjectionError(
                "BUSINESS_CLASSIFICATION_REFERENCE_DUPLICATE"
            )

        object.__setattr__(
            self,
            "classifications",
            classifications,
        )

    def to_dict(self) -> dict[str, Any]:
        """Serialize exact activity truth with no downstream activation."""
        return {
            "activity_id": self.activity_id,
            "role": self.role.value,
            "description": self.description,
            "confirmation": self.confirmation.value,
            "confidence_basis_points": self.confidence_basis_points,
            "evidence_refs": list(self.evidence_refs),
            "classifications": [
                entry.to_dict()
                for entry in self.classifications
            ],
        }

    @classmethod
    def from_dict(
        cls,
        payload: Mapping[str, Any],
    ) -> BusinessActivity:
        """Hydrate strict activity truth and nested taxonomy references."""
        expected = frozenset(
            {
                "activity_id",
                "role",
                "description",
                "confirmation",
                "confidence_basis_points",
                "evidence_refs",
                "classifications",
            }
        )

        value = _strict_mapping(
            payload,
            expected_keys=expected,
            surface="ACTIVITY",
        )

        raw_evidence_refs = value[
            "evidence_refs"
        ]
        raw_classifications = value[
            "classifications"
        ]

        if not isinstance(
            raw_evidence_refs,
            (list, tuple),
        ):
            raise BusinessClassificationProjectionError(
                "BUSINESS_CLASSIFICATION_EVIDENCE_REFS_INVALID"
            )

        if not isinstance(
            raw_classifications,
            (list, tuple),
        ):
            raise BusinessClassificationProjectionError(
                "BUSINESS_CLASSIFICATION_REFERENCES_INVALID"
            )

        return cls(
            activity_id=value["activity_id"],
            role=value["role"],
            description=value["description"],
            confirmation=value["confirmation"],
            confidence_basis_points=value[
                "confidence_basis_points"
            ],
            evidence_refs=tuple(
                raw_evidence_refs
            ),
            classifications=tuple(
                BusinessClassificationReference.from_dict(
                    entry
                )
                for entry in raw_classifications
            ),
        )


@dataclass(frozen=True, slots=True)
class BusinessClassificationProjection:
    """Represent immutable versioned business classification for one tenant.

    A projection binds source evidence, economic activities and taxonomy
    references to one source tenant-profile snapshot. A later revision
    supersedes an earlier projection identity rather than rewriting history.

    The projection creates no entitlement, authorization, service-pack,
    dashboard, workflow, AI, payment, settlement or financial authority.
    """

    projection_id: str
    tenant_id: str
    revision: int
    source_profile_digest: str
    evidences: tuple[
        BusinessClassificationEvidence,
        ...,
    ]
    activities: tuple[
        BusinessActivity,
        ...,
    ]
    effective_from: datetime
    created_at: datetime
    supersedes_projection_id: str | None = None
    fingerprint: str = field(
        init=False,
        compare=True,
    )

    def __post_init__(self) -> None:
        """Validate complete immutable projection truth."""
        object.__setattr__(
            self,
            "projection_id",
            _exact_text(
                "projection_id",
                self.projection_id,
            ),
        )

        object.__setattr__(
            self,
            "tenant_id",
            _tenant_id(
                self.tenant_id
            ),
        )

        object.__setattr__(
            self,
            "revision",
            _strict_int(
                "revision",
                self.revision,
                minimum=1,
            ),
        )

        object.__setattr__(
            self,
            "source_profile_digest",
            _lower_sha3_512(
                "source_profile_digest",
                self.source_profile_digest,
            ),
        )

        object.__setattr__(
            self,
            "effective_from",
            _aware_utc(
                "effective_from",
                self.effective_from,
            ),
        )

        object.__setattr__(
            self,
            "created_at",
            _aware_utc(
                "created_at",
                self.created_at,
            ),
        )

        object.__setattr__(
            self,
            "supersedes_projection_id",
            _optional_exact_text(
                "supersedes_projection_id",
                self.supersedes_projection_id,
            ),
        )

        if self.revision == 1:
            if self.supersedes_projection_id is not None:
                raise BusinessClassificationProjectionError(
                    "BUSINESS_CLASSIFICATION_INITIAL_REVISION_SUPERSESSION_INVALID"
                )
        else:
            if self.supersedes_projection_id is None:
                raise BusinessClassificationProjectionError(
                    "BUSINESS_CLASSIFICATION_SUPERSESSION_REQUIRED"
                )

            if (
                self.supersedes_projection_id
                == self.projection_id
            ):
                raise BusinessClassificationProjectionError(
                    "BUSINESS_CLASSIFICATION_SELF_SUPERSESSION_FORBIDDEN"
                )

        if not isinstance(
            self.evidences,
            (tuple, list),
        ):
            raise BusinessClassificationProjectionError(
                "BUSINESS_CLASSIFICATION_EVIDENCES_INVALID"
            )

        evidences = tuple(
            self.evidences
        )

        if not evidences:
            raise BusinessClassificationProjectionError(
                "BUSINESS_CLASSIFICATION_EVIDENCES_EMPTY"
            )

        if not all(
            isinstance(
                entry,
                BusinessClassificationEvidence,
            )
            for entry in evidences
        ):
            raise BusinessClassificationProjectionError(
                "BUSINESS_CLASSIFICATION_EVIDENCES_INVALID"
            )

        evidence_ids = tuple(
            entry.evidence_id
            for entry in evidences
        )

        if len(evidence_ids) != len(
            set(evidence_ids)
        ):
            raise BusinessClassificationProjectionError(
                "BUSINESS_CLASSIFICATION_EVIDENCE_DUPLICATE"
            )

        object.__setattr__(
            self,
            "evidences",
            evidences,
        )

        if not isinstance(
            self.activities,
            (tuple, list),
        ):
            raise BusinessClassificationProjectionError(
                "BUSINESS_CLASSIFICATION_ACTIVITIES_INVALID"
            )

        activities = tuple(
            self.activities
        )

        if not activities:
            raise BusinessClassificationProjectionError(
                "BUSINESS_CLASSIFICATION_ACTIVITIES_EMPTY"
            )

        if not all(
            isinstance(
                entry,
                BusinessActivity,
            )
            for entry in activities
        ):
            raise BusinessClassificationProjectionError(
                "BUSINESS_CLASSIFICATION_ACTIVITIES_INVALID"
            )

        activity_ids = tuple(
            entry.activity_id
            for entry in activities
        )

        if len(activity_ids) != len(
            set(activity_ids)
        ):
            raise BusinessClassificationProjectionError(
                "BUSINESS_CLASSIFICATION_ACTIVITY_DUPLICATE"
            )

        primary_count = sum(
            entry.role
            is BusinessActivityRole.PRIMARY
            for entry in activities
        )

        if primary_count != 1:
            raise BusinessClassificationProjectionError(
                "BUSINESS_CLASSIFICATION_PRIMARY_ACTIVITY_CARDINALITY_INVALID"
            )

        known_evidence = set(
            evidence_ids
        )

        for entry in activities:
            if not set(
                entry.evidence_refs
            ).issubset(
                known_evidence
            ):
                raise BusinessClassificationProjectionError(
                    "BUSINESS_CLASSIFICATION_ACTIVITY_EVIDENCE_UNRESOLVED"
                )

        object.__setattr__(
            self,
            "activities",
            activities,
        )

        object.__setattr__(
            self,
            "fingerprint",
            self._compute_fingerprint(),
        )

    def _semantic_payload(
        self,
    ) -> dict[str, Any]:
        """Return exact semantic truth covered by the integrity fingerprint."""
        return {
            "schema_version": SCHEMA_VERSION,
            "projection_id": self.projection_id,
            "tenant_id": self.tenant_id,
            "revision": self.revision,
            "source_profile_digest": self.source_profile_digest,
            "evidences": [
                entry.to_dict()
                for entry in self.evidences
            ],
            "activities": [
                entry.to_dict()
                for entry in self.activities
            ],
            "effective_from": self.effective_from.isoformat(),
            "created_at": self.created_at.isoformat(),
            "supersedes_projection_id": self.supersedes_projection_id,
        }

    def _compute_fingerprint(
        self,
    ) -> str:
        """Compute deterministic lowercase SHA3-512 over semantic truth."""
        encoded = json.dumps(
            self._semantic_payload(),
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=False,
        ).encode("utf-8")

        return hashlib.sha3_512(
            encoded
        ).hexdigest()

    def to_dict(
        self,
    ) -> dict[str, Any]:
        """Serialize strict projection truth including fingerprint evidence."""
        return {
            **self._semantic_payload(),
            "fingerprint": self.fingerprint,
        }

    @classmethod
    def from_dict(
        cls,
        payload: Mapping[str, Any],
    ) -> BusinessClassificationProjection:
        """Hydrate strict projection truth and reject any integrity corruption."""
        expected = frozenset(
            {
                "schema_version",
                "projection_id",
                "tenant_id",
                "revision",
                "source_profile_digest",
                "evidences",
                "activities",
                "effective_from",
                "created_at",
                "supersedes_projection_id",
                "fingerprint",
            }
        )

        value = _strict_mapping(
            payload,
            expected_keys=expected,
            surface="PROJECTION",
        )

        if value["schema_version"] != SCHEMA_VERSION:
            raise BusinessClassificationProjectionError(
                "BUSINESS_CLASSIFICATION_SCHEMA_VERSION_INVALID"
            )

        supplied_fingerprint = _lower_sha3_512(
            "fingerprint",
            value["fingerprint"],
        )

        raw_evidences = value[
            "evidences"
        ]
        raw_activities = value[
            "activities"
        ]

        if not isinstance(
            raw_evidences,
            (list, tuple),
        ):
            raise BusinessClassificationProjectionError(
                "BUSINESS_CLASSIFICATION_EVIDENCES_INVALID"
            )

        if not isinstance(
            raw_activities,
            (list, tuple),
        ):
            raise BusinessClassificationProjectionError(
                "BUSINESS_CLASSIFICATION_ACTIVITIES_INVALID"
            )

        try:
            effective_from = datetime.fromisoformat(
                value["effective_from"]
            )
            created_at = datetime.fromisoformat(
                value["created_at"]
            )
        except (
            TypeError,
            ValueError,
        ) as error:
            raise BusinessClassificationProjectionError(
                "BUSINESS_CLASSIFICATION_DATETIME_INVALID"
            ) from error

        restored = cls(
            projection_id=value["projection_id"],
            tenant_id=value["tenant_id"],
            revision=value["revision"],
            source_profile_digest=value[
                "source_profile_digest"
            ],
            evidences=tuple(
                BusinessClassificationEvidence.from_dict(
                    entry
                )
                for entry in raw_evidences
            ),
            activities=tuple(
                BusinessActivity.from_dict(
                    entry
                )
                for entry in raw_activities
            ),
            effective_from=effective_from,
            created_at=created_at,
            supersedes_projection_id=value[
                "supersedes_projection_id"
            ],
        )

        if (
            restored.fingerprint
            != supplied_fingerprint
        ):
            raise BusinessClassificationProjectionError(
                "BUSINESS_CLASSIFICATION_FINGERPRINT_MISMATCH"
            )

        return restored


# =============================================================================
# WILSY OS SOVEREIGN ARTIFACT SEAL
# =============================================================================
# ARTIFACT: business_classification_projection.py
# VERSION: v1.0.0-WILSY-BUSINESS-CLASSIFICATION-PROJECTION
# AUTHORITY BOUNDARY: immutable business-classification truth only; no
# entitlement, permission, authorization role, business role, record scope,
# service-pack, workflow, AI, billing, payment, settlement or execution authority
# TENANT POSTURE: every projection is bound to exactly one non-global tenant;
# cross-tenant or global authority is never inferred
# FAIL-CLOSED POSTURE: malformed coordinates, unresolved evidence, duplicate
# identities, invalid primary cardinality, widened hydration and fingerprint
# corruption are rejected
# FINANCIAL EXECUTION AUTHORITY: none; Kennel EOS remains exclusive
# END OF WILSY OS SOVEREIGN ARTIFACT
