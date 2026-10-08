"""WILSY OS — Business Classification Projection V2 direct certificate.

TITLE: Business Classification Projection V2 Direct Certificate
VERSION: v2.0.0-BUSINESS-CLASSIFICATION-PROJECTION-DIRECT-CERTIFICATE
AUTHORITY: Wilsy OS Core Governance

PURPOSE:
    Freeze the V2 Business Classification Projection subject contract before
    production implementation exists.

BOUNDARY:
- V2 is a separate schema generation from V1.
- V2 explicitly binds one certified Business Identity revision and fingerprint.
- source_profile_digest remains independent classification-input provenance.
- V1 payloads are never silently promoted into V2.
- The pure domain performs no Business Identity lookup.
- No entitlement, permission, activation, regulatory, tax-validity,
  AI-execution, or financial authority is granted.
"""

from __future__ import annotations

from dataclasses import fields
from datetime import datetime, timezone
import hashlib
import inspect
from typing import Any, cast

import pytest

from tools.eos.saas.domain.business_classification_projection import (
    BusinessActivity,
    BusinessActivityConfirmation,
    BusinessActivityRole,
    BusinessClassificationEvidence,
    BusinessClassificationProjection,
    BusinessClassificationReference,
    BusinessClassificationSourceKind,
)

from tools.eos.saas.domain.business_classification_projection_v2 import (
    SCHEMA_VERSION,
    VERSION,
    BusinessClassificationProjectionV2,
)


NOW = datetime(
    2026,
    10,
    8,
    10,
    0,
    tzinfo=timezone.utc,
)

PROFILE_DIGEST = hashlib.sha3_512(
    b"tenant-profile-source-snapshot"
).hexdigest()

PROFILE_DIGEST_B = hashlib.sha3_512(
    b"tenant-profile-source-snapshot-b"
).hexdigest()

BUSINESS_IDENTITY_FINGERPRINT = hashlib.sha3_512(
    b"business-identity-revision-1"
).hexdigest()

BUSINESS_IDENTITY_FINGERPRINT_B = hashlib.sha3_512(
    b"business-identity-revision-2"
).hexdigest()

EVIDENCE_DIGEST = hashlib.sha3_512(
    b"classification-evidence"
).hexdigest()

SNAPSHOT_DIGEST = hashlib.sha3_512(
    b"official-taxonomy-snapshot"
).hexdigest()


def classification() -> BusinessClassificationReference:
    """Build one certified-shape classification reference."""
    return BusinessClassificationReference(
        scheme_id="ISIC",
        scheme_version="REV5",
        code="6201",
        title="Computer programming activities",
        jurisdiction="GLOBAL",
        taxonomy_snapshot_id="SNAPSHOT-001",
        taxonomy_snapshot_digest=SNAPSHOT_DIGEST,
    )


def evidence(
    evidence_id: str = "EVIDENCE-1",
) -> BusinessClassificationEvidence:
    """Build one immutable evidence fixture."""
    return BusinessClassificationEvidence(
        evidence_id=evidence_id,
        source_kind=(
            BusinessClassificationSourceKind.TENANT_DECLARATION
        ),
        source_reference="tenant-profile:industry",
        observed_at=NOW,
        source_digest=EVIDENCE_DIGEST,
    )


def activity(
    activity_id: str = "ACTIVITY-1",
) -> BusinessActivity:
    """Build one immutable classification activity fixture."""
    return BusinessActivity(
        activity_id=activity_id,
        role=BusinessActivityRole.PRIMARY,
        description="Synthetic business activity",
        confirmation=(
            BusinessActivityConfirmation.CONFIRMED
        ),
        confidence_basis_points=9500,
        evidence_refs=("EVIDENCE-1",),
        classifications=(classification(),),
    )


def projection(
    *,
    projection_id: str = "WILSYBUSCLASS-V2-TEST-1",
    tenant_id: str = "tenant-a",
    business_identity_id: str = "BUSINESS-001",
    business_identity_revision: int = 1,
    business_identity_fingerprint: str = (
        BUSINESS_IDENTITY_FINGERPRINT
    ),
    revision: int = 1,
    source_profile_digest: str = PROFILE_DIGEST,
    supersedes_projection_id: str | None = None,
) -> BusinessClassificationProjectionV2:
    """Build one V2 projection with explicit immutable Business Identity binding."""
    return BusinessClassificationProjectionV2(
        projection_id=projection_id,
        tenant_id=tenant_id,
        business_identity_id=business_identity_id,
        business_identity_revision=business_identity_revision,
        business_identity_fingerprint=(
            business_identity_fingerprint
        ),
        revision=revision,
        source_profile_digest=source_profile_digest,
        evidences=(evidence(),),
        activities=(activity(),),
        effective_from=NOW,
        created_at=NOW,
        supersedes_projection_id=(
            supersedes_projection_id
        ),
    )


def v1_projection() -> BusinessClassificationProjection:
    """Build one valid historical V1 projection."""
    return BusinessClassificationProjection(
        projection_id="WILSYBUSCLASS-V1-HISTORICAL",
        tenant_id="tenant-a",
        revision=1,
        source_profile_digest=PROFILE_DIGEST,
        evidences=(evidence(),),
        activities=(activity(),),
        effective_from=NOW,
        created_at=NOW,
        supersedes_projection_id=None,
    )


def test_v2_version_and_schema_exact() -> None:
    assert (
        VERSION
        == "v2.0.0-WILSY-BUSINESS-CLASSIFICATION-PROJECTION"
    )

    assert (
        SCHEMA_VERSION
        == "wilsy.business.classification.projection.v2"
    )


def test_v2_exact_field_set() -> None:
    assert [
        field.name
        for field in fields(
            BusinessClassificationProjectionV2
        )
    ] == [
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
    ]


def test_business_identity_id_required_and_exact() -> None:
    assert (
        projection(
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
            ValueError
        ):
            projection(
                business_identity_id=invalid
            )


def test_business_identity_revision_positive_integer_not_bool() -> None:
    for invalid in (
        0,
        -1,
        cast(Any, True),
        cast(Any, False),
        cast(Any, 1.5),
        cast(Any, "1"),
    ):
        with pytest.raises(
            ValueError
        ):
            projection(
                business_identity_revision=invalid
            )


def test_business_identity_fingerprint_lowercase_sha3_512() -> None:
    assert (
        projection().business_identity_fingerprint
        == BUSINESS_IDENTITY_FINGERPRINT
    )

    for invalid in (
        "",
        "0" * 127,
        "0" * 129,
        "G" * 128,
        BUSINESS_IDENTITY_FINGERPRINT.upper(),
    ):
        with pytest.raises(
            ValueError
        ):
            projection(
                business_identity_fingerprint=invalid
            )


def test_business_identity_binding_fields_are_required() -> None:
    signature = inspect.signature(
        BusinessClassificationProjectionV2
    )

    for name in (
        "business_identity_id",
        "business_identity_revision",
        "business_identity_fingerprint",
    ):
        assert (
            signature.parameters[
                name
            ].default
            is inspect.Parameter.empty
        )


def test_business_identity_id_binds_projection_fingerprint() -> None:
    first = projection(
        business_identity_id="BUSINESS-A",
    )

    second = projection(
        business_identity_id="BUSINESS-B",
    )

    assert (
        first.fingerprint
        != second.fingerprint
    )


def test_business_identity_revision_binds_projection_fingerprint() -> None:
    first = projection(
        business_identity_revision=1,
    )

    second = projection(
        business_identity_revision=2,
    )

    assert (
        first.fingerprint
        != second.fingerprint
    )


def test_business_identity_fingerprint_binds_projection_fingerprint() -> None:
    first = projection(
        business_identity_fingerprint=(
            BUSINESS_IDENTITY_FINGERPRINT
        ),
    )

    second = projection(
        business_identity_fingerprint=(
            BUSINESS_IDENTITY_FINGERPRINT_B
        ),
    )

    assert (
        first.fingerprint
        != second.fingerprint
    )


def test_source_profile_digest_remains_independent_provenance() -> None:
    first = projection(
        source_profile_digest=PROFILE_DIGEST,
    )

    second = projection(
        source_profile_digest=PROFILE_DIGEST_B,
    )

    assert (
        first.business_identity_fingerprint
        == second.business_identity_fingerprint
    )

    assert (
        first.source_profile_digest
        != second.source_profile_digest
    )

    assert (
        first.fingerprint
        != second.fingerprint
    )


def test_projection_revision_is_independent_from_business_identity_revision() -> None:
    value = projection(
        revision=1,
        business_identity_revision=7,
    )

    assert value.revision == 1
    assert (
        value.business_identity_revision
        == 7
    )


def test_v2_serialization_contains_exact_business_identity_binding() -> None:
    value = projection()

    payload = value.to_dict()

    assert (
        payload[
            "business_identity_id"
        ]
        == value.business_identity_id
    )

    assert (
        payload[
            "business_identity_revision"
        ]
        == value.business_identity_revision
    )

    assert (
        payload[
            "business_identity_fingerprint"
        ]
        == value.business_identity_fingerprint
    )

    assert (
        payload[
            "source_profile_digest"
        ]
        == value.source_profile_digest
    )

    assert (
        payload[
            "schema_version"
        ]
        == SCHEMA_VERSION
    )

    assert (
        BusinessClassificationProjectionV2.from_dict(
            payload
        )
        == value
    )


def test_v2_hydration_requires_business_identity_binding() -> None:
    payload = projection().to_dict()

    for field_name in (
        "business_identity_id",
        "business_identity_revision",
        "business_identity_fingerprint",
    ):
        broken = dict(
            payload
        )

        broken.pop(
            field_name
        )

        with pytest.raises(
            ValueError
        ):
            BusinessClassificationProjectionV2.from_dict(
                broken
            )


def test_v1_payload_is_not_silently_hydrated_as_v2() -> None:
    historical = v1_projection()

    payload = historical.to_dict()

    assert (
        payload[
            "schema_version"
        ]
        != SCHEMA_VERSION
    )

    with pytest.raises(
        ValueError
    ):
        BusinessClassificationProjectionV2.from_dict(
            payload
        )


def test_business_identity_binding_grants_no_commercial_authority() -> None:
    public = {
        name
        for name, member
        in inspect.getmembers(
            BusinessClassificationProjectionV2
        )
        if (
            callable(
                member
            )
            and not name.startswith("_")
        )
    }

    assert not (
        public
        & {
            "authorize",
            "grant_permission",
            "grant_entitlement",
            "subscribe",
            "activate",
            "activate_service_pack",
            "set_regulatory_status",
            "verify_tax_registration",
            "invoice",
            "charge",
            "collect",
            "settle",
            "execute_payment",
            "refund",
        }
    )


# ARTIFACT: test_business_classification_projection_v2_domain.py
