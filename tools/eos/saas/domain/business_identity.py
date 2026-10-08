"""WILSY OS — sovereign immutable Business Identity pure domain.

TITLE: Business Identity Domain
VERSION: v1.0.0-WILSY-BUSINESS-IDENTITY-DOMAIN
AUTHORITY: Wilsy OS Core Governance

PURPOSE:
    Represent one immutable revision of sovereign Business Identity within an
    exact tenant ownership scope, independently from Tenant Identity,
    classification, entitlement, authorization, activation and financial truth.

AUTHORITY BOUNDARY:
- Business Identity is not Tenant Identity.
- Business Identity does not classify a business.
- Business Identity grants no entitlement, permission, role or record scope.
- Business Identity activates no service pack, workflow or subscription.
- Business Identity asserts no regulatory or tax-registration validity.
- Business Identity carries no financial execution authority.
- Tenant-to-business cardinality is deliberately not asserted by this domain.
- identity_fingerprint is deterministic derived SHA3-512 integrity truth.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
import hashlib
import json
import re
from typing import Any, Mapping


VERSION = "v1.0.0-WILSY-BUSINESS-IDENTITY-DOMAIN"
SCHEMA_VERSION = "wilsy.business_identity.v1"

_SHA3_512_HEX = re.compile(
    r"^[0-9a-f]{128}$"
)


class BusinessIdentityError(ValueError):
    """Raised when Business Identity truth is invalid or corrupt."""


def _exact_text(
    value: object,
    *,
    field_name: str,
) -> str:
    """Require exact non-empty unpadded text without normalization."""
    if not isinstance(
        value,
        str,
    ):
        raise BusinessIdentityError(
            "BUSINESS_IDENTITY_"
            + field_name.upper()
            + "_INVALID"
        )

    if (
        not value
        or not value.strip()
        or value != value.strip()
    ):
        raise BusinessIdentityError(
            "BUSINESS_IDENTITY_"
            + field_name.upper()
            + "_INVALID"
        )

    return value


def _aware_datetime(
    value: object,
    *,
    field_name: str,
) -> datetime:
    """Require timezone-aware datetime truth."""
    if not isinstance(
        value,
        datetime,
    ):
        raise BusinessIdentityError(
            "BUSINESS_IDENTITY_"
            + field_name.upper()
            + "_INVALID"
        )

    if (
        value.tzinfo is None
        or value.utcoffset() is None
    ):
        raise BusinessIdentityError(
            "BUSINESS_IDENTITY_"
            + field_name.upper()
            + "_TIMEZONE_REQUIRED"
        )

    return value


def _positive_revision(
    value: object,
    *,
    field_name: str,
) -> int:
    """Require a positive integer revision and reject bool explicitly."""
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
        raise BusinessIdentityError(
            "BUSINESS_IDENTITY_"
            + field_name.upper()
            + "_INVALID"
        )

    return value


@dataclass(
    frozen=True,
    slots=True,
    init=False,
)
class BusinessIdentity:
    """One immutable sovereign Business Identity revision."""

    business_identity_id: str
    tenant_id: str
    revision: int
    organization_name: str
    legal_name: str
    created_at: datetime
    effective_from: datetime
    supersedes_revision: int | None
    identity_fingerprint: str = field(
        init=False,
    )

    def __init__(
        self,
        *,
        business_identity_id: str,
        tenant_id: str,
        revision: int,
        organization_name: str,
        legal_name: str,
        created_at: datetime,
        effective_from: datetime,
        supersedes_revision: int | None = None,
    ) -> None:
        """Construct one immutable revision and derive its integrity identity."""
        normalized_business_identity_id = (
            _exact_text(
                business_identity_id,
                field_name="business_identity_id",
            )
        )

        normalized_tenant_id = (
            _exact_text(
                tenant_id,
                field_name="tenant_id",
            )
        )

        normalized_organization_name = (
            _exact_text(
                organization_name,
                field_name="organization_name",
            )
        )

        normalized_legal_name = (
            _exact_text(
                legal_name,
                field_name="legal_name",
            )
        )

        normalized_revision = (
            _positive_revision(
                revision,
                field_name="revision",
            )
        )

        normalized_created_at = (
            _aware_datetime(
                created_at,
                field_name="created_at",
            )
        )

        normalized_effective_from = (
            _aware_datetime(
                effective_from,
                field_name="effective_from",
            )
        )

        normalized_supersedes: int | None

        if supersedes_revision is None:
            normalized_supersedes = None
        else:
            normalized_supersedes = (
                _positive_revision(
                    supersedes_revision,
                    field_name="supersedes_revision",
                )
            )

        if (
            normalized_revision == 1
            and normalized_supersedes is not None
        ):
            raise BusinessIdentityError(
                "BUSINESS_IDENTITY_INITIAL_REVISION_"
                "SUPERSESSION_INVALID"
            )

        if (
            normalized_revision > 1
            and normalized_supersedes is None
        ):
            raise BusinessIdentityError(
                "BUSINESS_IDENTITY_SUPERSESSION_REQUIRED"
            )

        if (
            normalized_supersedes is not None
            and normalized_supersedes
            >= normalized_revision
        ):
            raise BusinessIdentityError(
                "BUSINESS_IDENTITY_SUPERSESSION_"
                "MUST_PRECEDE_REVISION"
            )

        object.__setattr__(
            self,
            "business_identity_id",
            normalized_business_identity_id,
        )

        object.__setattr__(
            self,
            "tenant_id",
            normalized_tenant_id,
        )

        object.__setattr__(
            self,
            "revision",
            normalized_revision,
        )

        object.__setattr__(
            self,
            "organization_name",
            normalized_organization_name,
        )

        object.__setattr__(
            self,
            "legal_name",
            normalized_legal_name,
        )

        object.__setattr__(
            self,
            "created_at",
            normalized_created_at,
        )

        object.__setattr__(
            self,
            "effective_from",
            normalized_effective_from,
        )

        object.__setattr__(
            self,
            "supersedes_revision",
            normalized_supersedes,
        )

        object.__setattr__(
            self,
            "identity_fingerprint",
            self._compute_fingerprint(),
        )

    def _semantic_payload(
        self,
    ) -> dict[str, Any]:
        """Return exact semantic truth covered by the integrity fingerprint."""
        return {
            "schema_version": SCHEMA_VERSION,
            "business_identity_id":
                self.business_identity_id,
            "tenant_id":
                self.tenant_id,
            "revision":
                self.revision,
            "organization_name":
                self.organization_name,
            "legal_name":
                self.legal_name,
            "created_at":
                self.created_at.isoformat(),
            "effective_from":
                self.effective_from.isoformat(),
            "supersedes_revision":
                self.supersedes_revision,
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
        ).encode(
            "utf-8"
        )

        return hashlib.sha3_512(
            encoded
        ).hexdigest()

    def to_dict(
        self,
    ) -> dict[str, Any]:
        """Serialize exact Business Identity truth including derived integrity."""
        return {
            **self._semantic_payload(),
            "identity_fingerprint":
                self.identity_fingerprint,
        }

    @classmethod
    def from_dict(
        cls,
        data: Mapping[str, Any],
    ) -> BusinessIdentity:
        """Strictly hydrate Business Identity and reject schema/integrity drift."""
        if not isinstance(
            data,
            Mapping,
        ):
            raise BusinessIdentityError(
                "BUSINESS_IDENTITY_DOCUMENT_INVALID"
            )

        expected = {
            "schema_version",
            "business_identity_id",
            "tenant_id",
            "revision",
            "organization_name",
            "legal_name",
            "created_at",
            "effective_from",
            "supersedes_revision",
            "identity_fingerprint",
        }

        if set(
            data.keys()
        ) != expected:
            raise BusinessIdentityError(
                "BUSINESS_IDENTITY_DOCUMENT_FIELDS_INVALID"
            )

        if (
            data.get(
                "schema_version"
            )
            != SCHEMA_VERSION
        ):
            raise BusinessIdentityError(
                "BUSINESS_IDENTITY_SCHEMA_VERSION_INVALID"
            )

        supplied_fingerprint = data.get(
            "identity_fingerprint"
        )

        if (
            not isinstance(
                supplied_fingerprint,
                str,
            )
            or _SHA3_512_HEX.fullmatch(
                supplied_fingerprint
            )
            is None
        ):
            raise BusinessIdentityError(
                "BUSINESS_IDENTITY_FINGERPRINT_INVALID"
            )

        try:
            created_raw = data[
                "created_at"
            ]

            effective_raw = data[
                "effective_from"
            ]

            if not isinstance(
                created_raw,
                str,
            ):
                raise TypeError(
                    "created_at"
                )

            if not isinstance(
                effective_raw,
                str,
            ):
                raise TypeError(
                    "effective_from"
                )

            created_at = (
                datetime.fromisoformat(
                    created_raw
                )
            )

            effective_from = (
                datetime.fromisoformat(
                    effective_raw
                )
            )

            value = cls(
                business_identity_id=data[
                    "business_identity_id"
                ],
                tenant_id=data[
                    "tenant_id"
                ],
                revision=data[
                    "revision"
                ],
                organization_name=data[
                    "organization_name"
                ],
                legal_name=data[
                    "legal_name"
                ],
                created_at=created_at,
                effective_from=effective_from,
                supersedes_revision=data[
                    "supersedes_revision"
                ],
            )
        except (
            BusinessIdentityError,
            KeyError,
            TypeError,
            ValueError,
        ) as error:
            if isinstance(
                error,
                BusinessIdentityError,
            ):
                raise

            raise BusinessIdentityError(
                "BUSINESS_IDENTITY_DOCUMENT_INVALID"
            ) from error

        if (
            value.identity_fingerprint
            != supplied_fingerprint
        ):
            raise BusinessIdentityError(
                "BUSINESS_IDENTITY_FINGERPRINT_MISMATCH"
            )

        return value


__all__ = [
    "VERSION",
    "SCHEMA_VERSION",
    "BusinessIdentityError",
    "BusinessIdentity",
]


# ARTIFACT: business_identity.py
