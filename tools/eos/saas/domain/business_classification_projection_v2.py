"""WILSY OS — Business Classification Projection V2 pure domain.

TITLE: Business Classification Projection V2
VERSION: v2.0.0-WILSY-BUSINESS-CLASSIFICATION-PROJECTION
AUTHORITY: Wilsy OS Core Governance

PURPOSE:
    Represent one immutable V2 Business Classification Projection explicitly
    bound to one certified Business Identity revision and integrity
    fingerprint.

GENERATION BOUNDARY:
- V1 remains a separate historical tenant-scoped classification schema.
- V2 never silently hydrates or promotes V1 payloads.
- V2 reuses the already-certified classification evidence/activity/reference
  value types without subclassing or mutating the V1 projection.
- source_profile_digest remains independent classification-input provenance.

AUTHORITY BOUNDARY:
- The pure domain performs no Business Identity lookup.
- Business Identity binding grants no entitlement, subscription, permission,
  role, service activation, regulatory status, tax validity, AI execution,
  or financial authority.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
import hashlib
import json
from typing import Any, Mapping

from tools.eos.saas.domain.business_classification_projection import (
    BusinessActivity,
    BusinessClassificationEvidence,
)


VERSION = (
    "v2.0.0-WILSY-BUSINESS-CLASSIFICATION-PROJECTION"
)

SCHEMA_VERSION = (
    "wilsy.business.classification.projection.v2"
)

_SHA3_512_HEX_LENGTH = 128
_LOWER_HEX = frozenset(
    "0123456789abcdef"
)


class BusinessClassificationProjectionV2Error(
    ValueError
):
    """Raised when V2 classification projection truth is invalid."""


def _exact_text(
    name: str,
    value: object,
) -> str:
    """Require exact non-empty non-padded text."""
    if not isinstance(
        value,
        str,
    ):
        raise BusinessClassificationProjectionV2Error(
            "BUSINESS_CLASSIFICATION_V2_"
            + name.upper()
            + "_INVALID"
        )

    if (
        not value
        or value != value.strip()
    ):
        raise BusinessClassificationProjectionV2Error(
            "BUSINESS_CLASSIFICATION_V2_"
            + name.upper()
            + "_INVALID"
        )

    return value


def _positive_int(
    name: str,
    value: object,
) -> int:
    """Require a positive integer and reject bool explicitly."""
    if (
        isinstance(
            value,
            bool,
        )
        or not isinstance(
            value,
            int,
        )
        or value < 1
    ):
        raise BusinessClassificationProjectionV2Error(
            "BUSINESS_CLASSIFICATION_V2_"
            + name.upper()
            + "_INVALID"
        )

    return value


def _lower_sha3_512(
    name: str,
    value: object,
) -> str:
    """Require exact lowercase SHA3-512 hexadecimal shape."""
    digest = _exact_text(
        name,
        value,
    )

    if (
        len(
            digest
        )
        != _SHA3_512_HEX_LENGTH
        or any(
            character not in _LOWER_HEX
            for character in digest
        )
    ):
        raise BusinessClassificationProjectionV2Error(
            "BUSINESS_CLASSIFICATION_V2_"
            + name.upper()
            + "_INVALID"
        )

    return digest


def _aware_datetime(
    name: str,
    value: object,
) -> datetime:
    """Require timezone-aware datetime truth."""
    if not isinstance(
        value,
        datetime,
    ):
        raise BusinessClassificationProjectionV2Error(
            "BUSINESS_CLASSIFICATION_V2_"
            + name.upper()
            + "_INVALID"
        )

    if (
        value.tzinfo is None
        or value.utcoffset() is None
    ):
        raise BusinessClassificationProjectionV2Error(
            "BUSINESS_CLASSIFICATION_V2_"
            + name.upper()
            + "_TIMEZONE_REQUIRED"
        )

    return value


def _strict_mapping(
    value: object,
    *,
    expected_keys: frozenset[str],
) -> Mapping[str, Any]:
    """Require one exact serialized V2 projection shape."""
    if not isinstance(
        value,
        Mapping,
    ):
        raise BusinessClassificationProjectionV2Error(
            "BUSINESS_CLASSIFICATION_V2_PROJECTION_INVALID"
        )

    if (
        frozenset(
            value.keys()
        )
        != expected_keys
    ):
        raise BusinessClassificationProjectionV2Error(
            "BUSINESS_CLASSIFICATION_V2_PROJECTION_SHAPE_INVALID"
        )

    return value


def _evidences(
    value: object,
) -> tuple[
    BusinessClassificationEvidence,
    ...,
]:
    """Require immutable validated V1-generation evidence value objects."""
    if (
        not isinstance(
            value,
            tuple,
        )
        or not value
        or any(
            not isinstance(
                entry,
                BusinessClassificationEvidence,
            )
            for entry in value
        )
    ):
        raise BusinessClassificationProjectionV2Error(
            "BUSINESS_CLASSIFICATION_V2_EVIDENCES_INVALID"
        )

    return value


def _activities(
    value: object,
) -> tuple[
    BusinessActivity,
    ...,
]:
    """Require immutable validated V1-generation activity value objects."""
    if (
        not isinstance(
            value,
            tuple,
        )
        or not value
        or any(
            not isinstance(
                entry,
                BusinessActivity,
            )
            for entry in value
        )
    ):
        raise BusinessClassificationProjectionV2Error(
            "BUSINESS_CLASSIFICATION_V2_ACTIVITIES_INVALID"
        )

    return value


@dataclass(
    frozen=True,
    slots=True,
    init=False,
)
class BusinessClassificationProjectionV2:
    """One immutable business-bound V2 classification projection."""

    projection_id: str
    tenant_id: str
    business_identity_id: str
    business_identity_revision: int
    business_identity_fingerprint: str
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
    supersedes_projection_id: str | None
    fingerprint: str = field(
        init=False,
    )

    def __init__(
        self,
        *,
        projection_id: str,
        tenant_id: str,
        business_identity_id: str,
        business_identity_revision: int,
        business_identity_fingerprint: str,
        revision: int,
        source_profile_digest: str,
        evidences: tuple[
            BusinessClassificationEvidence,
            ...,
        ],
        activities: tuple[
            BusinessActivity,
            ...,
        ],
        effective_from: datetime,
        created_at: datetime,
        supersedes_projection_id: str | None = None,
    ) -> None:
        """Construct one immutable V2 projection and derive its fingerprint."""
        normalized_projection_id = _exact_text(
            "projection_id",
            projection_id,
        )

        normalized_tenant_id = _exact_text(
            "tenant_id",
            tenant_id,
        )

        normalized_business_identity_id = _exact_text(
            "business_identity_id",
            business_identity_id,
        )

        normalized_business_identity_revision = _positive_int(
            "business_identity_revision",
            business_identity_revision,
        )

        normalized_business_identity_fingerprint = _lower_sha3_512(
            "business_identity_fingerprint",
            business_identity_fingerprint,
        )

        normalized_revision = _positive_int(
            "revision",
            revision,
        )

        normalized_source_profile_digest = _lower_sha3_512(
            "source_profile_digest",
            source_profile_digest,
        )

        normalized_evidences = _evidences(
            evidences
        )

        normalized_activities = _activities(
            activities
        )

        normalized_effective_from = _aware_datetime(
            "effective_from",
            effective_from,
        )

        normalized_created_at = _aware_datetime(
            "created_at",
            created_at,
        )

        normalized_supersedes: str | None

        if supersedes_projection_id is None:
            normalized_supersedes = None
        else:
            normalized_supersedes = _exact_text(
                "supersedes_projection_id",
                supersedes_projection_id,
            )

        if (
            normalized_revision == 1
            and normalized_supersedes is not None
        ):
            raise BusinessClassificationProjectionV2Error(
                "BUSINESS_CLASSIFICATION_V2_INITIAL_REVISION_"
                "SUPERSESSION_INVALID"
            )

        if (
            normalized_revision > 1
            and normalized_supersedes is None
        ):
            raise BusinessClassificationProjectionV2Error(
                "BUSINESS_CLASSIFICATION_V2_SUPERSESSION_REQUIRED"
            )

        if (
            normalized_supersedes
            == normalized_projection_id
        ):
            raise BusinessClassificationProjectionV2Error(
                "BUSINESS_CLASSIFICATION_V2_SELF_SUPERSESSION_INVALID"
            )

        object.__setattr__(
            self,
            "projection_id",
            normalized_projection_id,
        )

        object.__setattr__(
            self,
            "tenant_id",
            normalized_tenant_id,
        )

        object.__setattr__(
            self,
            "business_identity_id",
            normalized_business_identity_id,
        )

        object.__setattr__(
            self,
            "business_identity_revision",
            normalized_business_identity_revision,
        )

        object.__setattr__(
            self,
            "business_identity_fingerprint",
            normalized_business_identity_fingerprint,
        )

        object.__setattr__(
            self,
            "revision",
            normalized_revision,
        )

        object.__setattr__(
            self,
            "source_profile_digest",
            normalized_source_profile_digest,
        )

        object.__setattr__(
            self,
            "evidences",
            normalized_evidences,
        )

        object.__setattr__(
            self,
            "activities",
            normalized_activities,
        )

        object.__setattr__(
            self,
            "effective_from",
            normalized_effective_from,
        )

        object.__setattr__(
            self,
            "created_at",
            normalized_created_at,
        )

        object.__setattr__(
            self,
            "supersedes_projection_id",
            normalized_supersedes,
        )

        object.__setattr__(
            self,
            "fingerprint",
            self._compute_fingerprint(),
        )

    def _semantic_payload(
        self,
    ) -> dict[str, Any]:
        """Return exact semantic truth covered by the V2 fingerprint."""
        return {
            "schema_version":
                SCHEMA_VERSION,
            "projection_id":
                self.projection_id,
            "tenant_id":
                self.tenant_id,
            "business_identity_id":
                self.business_identity_id,
            "business_identity_revision":
                self.business_identity_revision,
            "business_identity_fingerprint":
                self.business_identity_fingerprint,
            "revision":
                self.revision,
            "source_profile_digest":
                self.source_profile_digest,
            "evidences": [
                entry.to_dict()
                for entry in self.evidences
            ],
            "activities": [
                entry.to_dict()
                for entry in self.activities
            ],
            "effective_from":
                self.effective_from.isoformat(),
            "created_at":
                self.created_at.isoformat(),
            "supersedes_projection_id":
                self.supersedes_projection_id,
        }

    def _compute_fingerprint(
        self,
    ) -> str:
        """Compute deterministic lowercase SHA3-512 over V2 semantic truth."""
        encoded = json.dumps(
            self._semantic_payload(),
            sort_keys=True,
            separators=(
                ",",
                ":",
            ),
            ensure_ascii=False,
        ).encode(
            "utf-8"
        )

        return hashlib.sha3_512(
            encoded
        ).hexdigest()

    def to_dict(
        self,
    ) -> dict[str, Any]:
        """Serialize exact V2 projection truth including derived integrity."""
        return {
            **self._semantic_payload(),
            "fingerprint":
                self.fingerprint,
        }

    @classmethod
    def from_dict(
        cls,
        payload: Mapping[str, Any],
    ) -> BusinessClassificationProjectionV2:
        """Strictly hydrate V2 only and reject V1 or integrity corruption."""
        expected = frozenset(
            {
                "schema_version",
                "projection_id",
                "tenant_id",
                "business_identity_id",
                "business_identity_revision",
                "business_identity_fingerprint",
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
        )

        if (
            value[
                "schema_version"
            ]
            != SCHEMA_VERSION
        ):
            raise BusinessClassificationProjectionV2Error(
                "BUSINESS_CLASSIFICATION_V2_SCHEMA_VERSION_INVALID"
            )

        supplied_fingerprint = _lower_sha3_512(
            "fingerprint",
            value[
                "fingerprint"
            ],
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
            raise BusinessClassificationProjectionV2Error(
                "BUSINESS_CLASSIFICATION_V2_EVIDENCES_INVALID"
            )

        if not isinstance(
            raw_activities,
            (list, tuple),
        ):
            raise BusinessClassificationProjectionV2Error(
                "BUSINESS_CLASSIFICATION_V2_ACTIVITIES_INVALID"
            )

        try:
            evidences = tuple(
                BusinessClassificationEvidence.from_dict(
                    entry
                )
                for entry in raw_evidences
            )

            activities = tuple(
                BusinessActivity.from_dict(
                    entry
                )
                for entry in raw_activities
            )

            effective_raw = value[
                "effective_from"
            ]

            created_raw = value[
                "created_at"
            ]

            if not isinstance(
                effective_raw,
                str,
            ):
                raise TypeError(
                    "effective_from"
                )

            if not isinstance(
                created_raw,
                str,
            ):
                raise TypeError(
                    "created_at"
                )

            effective_from = datetime.fromisoformat(
                effective_raw
            )

            created_at = datetime.fromisoformat(
                created_raw
            )

            restored = cls(
                projection_id=value[
                    "projection_id"
                ],
                tenant_id=value[
                    "tenant_id"
                ],
                business_identity_id=value[
                    "business_identity_id"
                ],
                business_identity_revision=value[
                    "business_identity_revision"
                ],
                business_identity_fingerprint=value[
                    "business_identity_fingerprint"
                ],
                revision=value[
                    "revision"
                ],
                source_profile_digest=value[
                    "source_profile_digest"
                ],
                evidences=evidences,
                activities=activities,
                effective_from=effective_from,
                created_at=created_at,
                supersedes_projection_id=value[
                    "supersedes_projection_id"
                ],
            )

        except BusinessClassificationProjectionV2Error:
            raise

        except Exception as error:
            raise BusinessClassificationProjectionV2Error(
                "BUSINESS_CLASSIFICATION_V2_DOCUMENT_INVALID"
            ) from error

        if (
            restored.fingerprint
            != supplied_fingerprint
        ):
            raise BusinessClassificationProjectionV2Error(
                "BUSINESS_CLASSIFICATION_V2_FINGERPRINT_MISMATCH"
            )

        return restored


__all__ = [
    "VERSION",
    "SCHEMA_VERSION",
    "BusinessClassificationProjectionV2Error",
    "BusinessClassificationProjectionV2",
]


# ARTIFACT: business_classification_projection_v2.py
