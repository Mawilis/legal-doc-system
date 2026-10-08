"""WILSY OS — Business Identity pure-domain direct certificate.

TITLE: Business Identity Domain Direct Certificate
VERSION: v1.0.0-BUSINESS-IDENTITY-DOMAIN-TEST
AUTHORITY: Wilsy OS Core Governance

PURPOSE:
    Freeze and certify the pure immutable Business Identity authority before
    production implementation exists.

BOUNDARY:
- Business Identity is distinct from Tenant Identity.
- Business Identity carries no classification, entitlement, subscription,
  permission, authorization, activation, regulatory, tax-validity, AI-execution
  or financial authority.
- The domain performs no tenant lookup and grants no product cardinality claim.
- Fingerprint is deterministic derived SHA3-512 integrity truth.
"""

from __future__ import annotations

from dataclasses import FrozenInstanceError, fields
from datetime import datetime, timedelta, timezone
import inspect
from typing import Any, cast

import pytest

from tools.eos.saas.domain.business_identity import (
    SCHEMA_VERSION,
    VERSION,
    BusinessIdentity,
    BusinessIdentityError,
)


NOW = datetime(
    2026,
    10,
    8,
    8,
    0,
    tzinfo=timezone.utc,
)


def identity(
    *,
    business_identity_id: str = "BUSINESS-IDENTITY-001",
    tenant_id: str = "tenant-a",
    revision: int = 1,
    organization_name: str = "Acme Holdings",
    legal_name: str = "Acme Holdings (Pty) Ltd",
    created_at: datetime = NOW,
    effective_from: datetime = NOW,
    supersedes_revision: int | None = None,
) -> BusinessIdentity:
    """Build one immutable Business Identity revision."""
    return BusinessIdentity(
        business_identity_id=business_identity_id,
        tenant_id=tenant_id,
        revision=revision,
        organization_name=organization_name,
        legal_name=legal_name,
        created_at=created_at,
        effective_from=effective_from,
        supersedes_revision=supersedes_revision,
    )


def test_version_and_schema_exact() -> None:
    assert (
        VERSION
        == "v1.0.0-WILSY-BUSINESS-IDENTITY-DOMAIN"
    )
    assert (
        SCHEMA_VERSION
        == "wilsy.business_identity.v1"
    )


def test_business_identity_is_immutable() -> None:
    value = identity()

    with pytest.raises(
        FrozenInstanceError
    ):
        cast(
            Any,
            value,
        ).legal_name = "Mutated"


def test_exact_minimal_field_set() -> None:
    assert [
        field.name
        for field in fields(
            BusinessIdentity
        )
    ] == [
        "business_identity_id",
        "tenant_id",
        "revision",
        "organization_name",
        "legal_name",
        "created_at",
        "effective_from",
        "supersedes_revision",
        "identity_fingerprint",
    ]


def test_business_identity_id_required_and_exact() -> None:
    assert (
        identity(
            business_identity_id="BUSINESS-EXACT"
        ).business_identity_id
        == "BUSINESS-EXACT"
    )

    for invalid in (
        "",
        " ",
        " BUSINESS-EXACT",
        "BUSINESS-EXACT ",
    ):
        with pytest.raises(
            BusinessIdentityError
        ):
            identity(
                business_identity_id=invalid
            )


def test_tenant_id_required_and_exact() -> None:
    assert (
        identity(
            tenant_id="tenant-exact"
        ).tenant_id
        == "tenant-exact"
    )

    for invalid in (
        "",
        " ",
        " tenant-exact",
        "tenant-exact ",
    ):
        with pytest.raises(
            BusinessIdentityError
        ):
            identity(
                tenant_id=invalid
            )


def test_organization_name_required_and_exact() -> None:
    assert (
        identity(
            organization_name="Exact Organization"
        ).organization_name
        == "Exact Organization"
    )

    for invalid in (
        "",
        " ",
        " Exact Organization",
        "Exact Organization ",
    ):
        with pytest.raises(
            BusinessIdentityError
        ):
            identity(
                organization_name=invalid
            )


def test_legal_name_required_and_exact() -> None:
    assert (
        identity(
            legal_name="Exact Legal Name"
        ).legal_name
        == "Exact Legal Name"
    )

    for invalid in (
        "",
        " ",
        " Exact Legal Name",
        "Exact Legal Name ",
    ):
        with pytest.raises(
            BusinessIdentityError
        ):
            identity(
                legal_name=invalid
            )


def test_revision_must_be_positive_integer_not_bool() -> None:
    for invalid in (
        0,
        -1,
        cast(Any, True),
        cast(Any, False),
        cast(Any, 1.5),
        cast(Any, "1"),
    ):
        with pytest.raises(
            BusinessIdentityError
        ):
            identity(
                revision=invalid
            )


def test_created_at_requires_timezone() -> None:
    naive = datetime(
        2026,
        10,
        8,
        8,
        0,
    )

    with pytest.raises(
        BusinessIdentityError
    ):
        identity(
            created_at=naive
        )


def test_effective_from_requires_timezone() -> None:
    naive = datetime(
        2026,
        10,
        8,
        8,
        0,
    )

    with pytest.raises(
        BusinessIdentityError
    ):
        identity(
            effective_from=naive
        )


def test_revision_one_forbids_supersedes_revision() -> None:
    with pytest.raises(
        BusinessIdentityError
    ):
        identity(
            revision=1,
            supersedes_revision=1,
        )


def test_later_revision_requires_supersedes_revision() -> None:
    with pytest.raises(
        BusinessIdentityError
    ):
        identity(
            revision=2,
            supersedes_revision=None,
        )


def test_supersedes_revision_must_be_positive_integer_not_bool() -> None:
    for invalid in (
        0,
        -1,
        cast(Any, True),
        cast(Any, False),
        cast(Any, 1.5),
        cast(Any, "1"),
    ):
        with pytest.raises(
            BusinessIdentityError
        ):
            identity(
                revision=3,
                supersedes_revision=invalid,
            )


def test_supersedes_revision_must_be_less_than_revision() -> None:
    for invalid in (
        3,
        4,
        999,
    ):
        with pytest.raises(
            BusinessIdentityError
        ):
            identity(
                revision=3,
                supersedes_revision=invalid,
            )


def test_non_adjacent_supersession_is_domain_valid() -> None:
    value = identity(
        revision=7,
        supersedes_revision=2,
    )

    assert value.revision == 7
    assert value.supersedes_revision == 2


def test_identity_fingerprint_is_lowercase_sha3_512() -> None:
    fingerprint = identity().identity_fingerprint

    assert len(
        fingerprint
    ) == 128

    assert fingerprint == fingerprint.lower()

    int(
        fingerprint,
        16,
    )


def test_identity_fingerprint_covers_business_identity_id() -> None:
    assert (
        identity(
            business_identity_id="BUSINESS-A"
        ).identity_fingerprint
        != identity(
            business_identity_id="BUSINESS-B"
        ).identity_fingerprint
    )


def test_identity_fingerprint_covers_tenant_id() -> None:
    assert (
        identity(
            tenant_id="tenant-a"
        ).identity_fingerprint
        != identity(
            tenant_id="tenant-b"
        ).identity_fingerprint
    )


def test_identity_fingerprint_covers_revision() -> None:
    first = identity(
        revision=1,
    )

    later = identity(
        revision=3,
        supersedes_revision=1,
    )

    assert (
        first.identity_fingerprint
        != later.identity_fingerprint
    )


def test_identity_fingerprint_covers_organization_name() -> None:
    assert (
        identity(
            organization_name="Organization A"
        ).identity_fingerprint
        != identity(
            organization_name="Organization B"
        ).identity_fingerprint
    )


def test_identity_fingerprint_covers_legal_name() -> None:
    assert (
        identity(
            legal_name="Legal A"
        ).identity_fingerprint
        != identity(
            legal_name="Legal B"
        ).identity_fingerprint
    )


def test_identity_fingerprint_covers_created_at() -> None:
    assert (
        identity(
            created_at=NOW
        ).identity_fingerprint
        != identity(
            created_at=(
                NOW
                + timedelta(
                    seconds=1
                )
            )
        ).identity_fingerprint
    )


def test_identity_fingerprint_covers_effective_from() -> None:
    assert (
        identity(
            effective_from=NOW
        ).identity_fingerprint
        != identity(
            effective_from=(
                NOW
                + timedelta(
                    seconds=1
                )
            )
        ).identity_fingerprint
    )


def test_identity_fingerprint_covers_supersedes_revision() -> None:
    first = identity(
        revision=4,
        supersedes_revision=1,
    )

    second = identity(
        revision=4,
        supersedes_revision=2,
    )

    assert (
        first.identity_fingerprint
        != second.identity_fingerprint
    )


def test_caller_cannot_assert_identity_fingerprint() -> None:
    constructor = cast(
        Any,
        BusinessIdentity,
    )

    with pytest.raises(
        TypeError
    ):
        constructor(
            business_identity_id="BUSINESS-IDENTITY-001",
            tenant_id="tenant-a",
            revision=1,
            organization_name="Acme Holdings",
            legal_name="Acme Holdings (Pty) Ltd",
            created_at=NOW,
            effective_from=NOW,
            supersedes_revision=None,
            identity_fingerprint="0" * 128,
        )


def test_exact_to_dict_from_dict_roundtrip() -> None:
    value = identity()

    payload = value.to_dict()

    assert (
        payload["schema_version"]
        == SCHEMA_VERSION
    )

    assert (
        BusinessIdentity.from_dict(
            payload
        )
        == value
    )


def test_hydration_rejects_missing_fields() -> None:
    payload = identity().to_dict()

    for field_name in tuple(
        payload
    ):
        broken = dict(
            payload
        )

        broken.pop(
            field_name
        )

        with pytest.raises(
            BusinessIdentityError
        ):
            BusinessIdentity.from_dict(
                broken
            )


def test_hydration_rejects_extra_fields() -> None:
    payload = identity().to_dict()

    payload[
        "unexpected"
    ] = "forbidden"

    with pytest.raises(
        BusinessIdentityError
    ):
        BusinessIdentity.from_dict(
            payload
        )


def test_hydration_rejects_corrupt_fingerprint() -> None:
    payload = identity().to_dict()

    payload[
        "identity_fingerprint"
    ] = "0" * 128

    with pytest.raises(
        BusinessIdentityError
    ):
        BusinessIdentity.from_dict(
            payload
        )


def test_industry_sector_and_region_are_not_identity_fields() -> None:
    names = {
        field.name
        for field in fields(
            BusinessIdentity
        )
    }

    assert not (
        names
        & {
            "industry",
            "sector",
            "region",
            "regions",
        }
    )


def test_plan_subscription_and_entitlement_are_not_identity_fields() -> None:
    names = {
        field.name
        for field in fields(
            BusinessIdentity
        )
    }

    assert not (
        names
        & {
            "plan",
            "subscription",
            "subscription_tier",
            "entitlement",
            "entitlements",
            "features",
        }
    )


def test_tax_id_is_not_v1_identity_without_issuer_jurisdiction_semantics() -> None:
    names = {
        field.name
        for field in fields(
            BusinessIdentity
        )
    }

    assert "tax_id" not in names
    assert "tax_number" not in names


def test_business_identity_has_no_classification_authority() -> None:
    public = {
        name
        for name, member
        in inspect.getmembers(
            BusinessIdentity
        )
        if (
            callable(member)
            and not name.startswith("_")
        )
    }

    assert not (
        public
        & {
            "classify",
            "set_industry",
            "set_sector",
            "map_taxonomy",
            "activate_classification",
        }
    )


def test_business_identity_has_no_authorization_or_activation_authority() -> None:
    public = {
        name
        for name, member
        in inspect.getmembers(
            BusinessIdentity
        )
        if (
            callable(member)
            and not name.startswith("_")
        )
    }

    assert not (
        public
        & {
            "authorize",
            "grant_permission",
            "assign_role",
            "grant_entitlement",
            "activate",
            "activate_service_pack",
            "subscribe",
        }
    )


def test_business_identity_has_no_financial_authority() -> None:
    public = {
        name
        for name, member
        in inspect.getmembers(
            BusinessIdentity
        )
        if (
            callable(member)
            and not name.startswith("_")
        )
    }

    assert not (
        public
        & {
            "invoice",
            "charge",
            "collect",
            "settle",
            "execute_payment",
            "refund",
        }
    )


def test_domain_does_not_assert_single_or_multi_business_tenant_cardinality() -> None:
    names = {
        field.name
        for field in fields(
            BusinessIdentity
        )
    }

    assert not (
        names
        & {
            "is_only_business",
            "is_primary_business",
            "business_count",
            "tenant_business_count",
            "single_business",
            "multi_business",
        }
    )

    public = {
        name
        for name, member
        in inspect.getmembers(
            BusinessIdentity
        )
        if (
            callable(member)
            and not name.startswith("_")
        )
    }

    assert not (
        public
        & {
            "assert_single_business",
            "assert_multi_business",
            "set_primary_business",
            "count_businesses",
        }
    )


# ARTIFACT: test_business_identity_domain.py
