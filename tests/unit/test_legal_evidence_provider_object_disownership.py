"""Direct certificate for Legal Evidence provider-object disownership domain.

VERSION: v1.0.0-L10A2R-C4D6D-PROVIDER-OBJECT-DISOWNERSHIP-CERT
AUTHORITY: Wilsy OS Core Governance
CERTIFICATION / UPDATE DATE: 2026-10-01
CHANGELOG: v1.0.0-L10A2R-C4D6D certifies exact provider-object identity,
           explicit positive evidence, immutable deterministic fingerprinting,
           strict hydration and absence of orphan/delete inference.
"""

from __future__ import annotations

from dataclasses import FrozenInstanceError, replace
from datetime import datetime, timedelta, timezone
import inspect
from typing import Any, cast

import pytest

from tools.eos.legal_operations.domain.legal_evidence_provider_object_disownership import (
    SCHEMA,
    VERSION,
    LegalEvidenceProviderObjectDisownership,
    LegalEvidenceProviderObjectDisownershipError,
)


AT = datetime(
    2026,
    10,
    1,
    0,
    0,
    0,
    123456,
    tzinfo=timezone.utc,
)

SHA_A = "a" * 128
SHA_B = "b" * 128


def _value(
    **changes: object,
) -> LegalEvidenceProviderObjectDisownership:
    values: dict[str, object] = {
        "tenant_id":
            "tenant-c4d6d",
        "provider_name":
            "aws_s3",
        "storage_reference":
            "legal-evidence/c4d6d/object",
        "object_version_reference":
            "version-c4d6d",
        "disownership_reference":
            "disownership-c4d6d",
        "reason_reference":
            "reason:c4d6d:operator-reviewed",
        "source_evidence_reference":
            "source:c4d6d:provider-review",
        "source_evidence_fingerprint":
            SHA_A,
        "authorization_evidence_reference":
            "authorization:c4d6d:decision",
        "authorization_evidence_fingerprint":
            SHA_B,
        "decided_at":
            AT,
    }

    values.update(
        changes
    )

    return LegalEvidenceProviderObjectDisownership(
        **cast(
            dict[str, Any],
            values,
        )
    )


def test_exact_value_is_immutable_and_deterministic() -> None:
    first = _value()
    second = _value()

    assert first == second
    assert first.fingerprint == second.fingerprint
    assert len(first.fingerprint) == 128
    assert first.schema == SCHEMA
    assert first.version == VERSION

    with pytest.raises(
        FrozenInstanceError
    ):
        setattr(
            first,
            "tenant_id",
            "other",
        )


@pytest.mark.parametrize(
    ("field", "value"),
    [
        (
            "tenant_id",
            "",
        ),
        (
            "provider_name",
            "",
        ),
        (
            "storage_reference",
            "",
        ),
        (
            "object_version_reference",
            "",
        ),
        (
            "disownership_reference",
            "",
        ),
        (
            "reason_reference",
            "",
        ),
        (
            "source_evidence_reference",
            "",
        ),
        (
            "authorization_evidence_reference",
            "",
        ),
        (
            "source_evidence_fingerprint",
            "a" * 127,
        ),
        (
            "authorization_evidence_fingerprint",
            "B" * 128,
        ),
    ],
)
def test_required_identity_and_evidence_reject_malformed(
    field: str,
    value: object,
) -> None:
    with pytest.raises(
        LegalEvidenceProviderObjectDisownershipError
    ):
        _value(
            **{
                field:
                    value
            }
        )


def test_naive_decision_time_rejects() -> None:
    with pytest.raises(
        LegalEvidenceProviderObjectDisownershipError,
        match="L10A2R_C4D6D_DECIDED_AT_INVALID",
    ):
        _value(
            decided_at=AT.replace(
                tzinfo=None
            )
        )


def test_decision_time_normalizes_to_utc() -> None:
    local = AT.astimezone(
        timezone(
            timedelta(
                hours=2
            )
        )
    )

    value = _value(
        decided_at=local
    )

    assert value.decided_at == AT
    assert value.decided_at.tzinfo == timezone.utc


@pytest.mark.parametrize(
    "field",
    [
        "tenant_id",
        "provider_name",
        "storage_reference",
        "object_version_reference",
        "disownership_reference",
        "reason_reference",
        "source_evidence_reference",
        "source_evidence_fingerprint",
        "authorization_evidence_reference",
        "authorization_evidence_fingerprint",
        "decided_at",
    ],
)
def test_every_semantic_field_participates_in_fingerprint(
    field: str,
) -> None:
    original = _value()

    replacements: dict[str, object] = {
        "tenant_id":
            "tenant-c4d6d-other",
        "provider_name":
            "provider-other",
        "storage_reference":
            "legal-evidence/c4d6d/other",
        "object_version_reference":
            "version-other",
        "disownership_reference":
            "disownership-other",
        "reason_reference":
            "reason:other",
        "source_evidence_reference":
            "source:other",
        "source_evidence_fingerprint":
            "c" * 128,
        "authorization_evidence_reference":
            "authorization:other",
        "authorization_evidence_fingerprint":
            "d" * 128,
        "decided_at":
            AT + timedelta(
                seconds=1
            ),
    }

    divergent = replace(
        original,
        **{
            field:
                replacements[field],
            "fingerprint":
                "",
        },
    )

    assert divergent.fingerprint != original.fingerprint


def test_exact_round_trip_succeeds() -> None:
    value = _value()

    hydrated = (
        LegalEvidenceProviderObjectDisownership
        .from_dict(
            value.to_dict()
        )
    )

    assert hydrated == value


def test_unknown_or_missing_document_fields_reject() -> None:
    value = _value().to_dict()

    unknown = dict(
        value
    )
    unknown[
        "orphan_proven"
    ] = True

    with pytest.raises(
        LegalEvidenceProviderObjectDisownershipError,
        match="L10A2R_C4D6D_DOCUMENT_FIELDS_INVALID",
    ):
        LegalEvidenceProviderObjectDisownership.from_dict(
            unknown
        )

    missing = dict(
        value
    )
    missing.pop(
        "reason_reference"
    )

    with pytest.raises(
        LegalEvidenceProviderObjectDisownershipError,
        match="L10A2R_C4D6D_DOCUMENT_FIELDS_INVALID",
    ):
        LegalEvidenceProviderObjectDisownership.from_dict(
            missing
        )


def test_persisted_fingerprint_tampering_rejects() -> None:
    document = _value().to_dict()
    document[
        "fingerprint"
    ] = "f" * 128

    with pytest.raises(
        LegalEvidenceProviderObjectDisownershipError,
        match="L10A2R_C4D6D_FINGERPRINT_MISMATCH",
    ):
        LegalEvidenceProviderObjectDisownership.from_dict(
            document
        )


def test_public_value_contains_no_orphan_or_delete_authority() -> None:
    fields = set(
        LegalEvidenceProviderObjectDisownership
        .__dataclass_fields__
    )

    forbidden = {
        "orphan_proven",
        "cleanup_candidate",
        "retention_satisfied",
        "legal_hold_released",
        "abort_authorized",
        "delete_authorized",
        "provider_delete_authorized",
        "provider_deleted",
    }

    assert forbidden.isdisjoint(
        fields
    )

    public_methods = {
        name
        for name, value in inspect.getmembers(
            LegalEvidenceProviderObjectDisownership,
            predicate=inspect.isfunction,
        )
        if not name.startswith("_")
    }

    assert public_methods == {
        "to_dict",
    }


def test_no_inference_constructor_exists() -> None:
    source = inspect.getsource(
        LegalEvidenceProviderObjectDisownership
    )

    forbidden = {
        "from_absence",
        "from_not_found",
        "from_cleanup",
        "from_coverage",
        "prove_orphan",
        "authorize_delete",
    }

    assert all(
        token not in source
        for token in forbidden
    )


# ARTIFACT: test_legal_evidence_provider_object_disownership.py
# VERSION: v1.0.0-L10A2R-C4D6D-PROVIDER-OBJECT-DISOWNERSHIP-CERT
# AUTHORITY BOUNDARY: pure positive disownership-value certificate only
# INFERENCE POSTURE: no absence/coverage/cleanup inference constructor
# ORPHAN POSTURE: no orphan proof
# DELETION POSTURE: no abort/delete authority or provider mutation
# PERSISTENCE POSTURE: no registry or durable write
# ISSUANCE POSTURE: construction alone is not authorized issuance
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively
# END OF WILSY OS SOVEREIGN ARTIFACT
