from __future__ import annotations

from dataclasses import FrozenInstanceError
from datetime import datetime, timedelta, timezone

import pytest

from tools.eos.legal_operations.domain.legal_evidence_provider_delete_execution_evidence import (
    SCHEMA,
    VERSION,
    LegalEvidenceProviderDeleteExecutionEvidence,
    LegalEvidenceProviderDeleteExecutionEvidenceError,
)


AT = datetime(2026, 10, 2, 15, 30, tzinfo=timezone.utc)


def _evidence(**overrides):
    values = {
        "execution_evidence_id": "delete-execution-1",
        "tenant_id": "tenant-1",
        "command_id": "command-1",
        "cleanup_authorization_id": "cleanup-auth-1",
        "provider_name": "aws_s3",
        "storage_reference": "opaque/storage/key",
        "object_version_reference": "version-1",
        "command_fingerprint": "c" * 128,
        "cleanup_authorization_fingerprint": "d" * 128,
        "delete_marker": False,
        "delete_marker_version_reference": None,
        "executed_at": AT,
    }
    values.update(overrides)
    return LegalEvidenceProviderDeleteExecutionEvidence(**values)


def test_version_schema_and_frozen_slots():
    value = _evidence()

    assert VERSION.startswith("v1.0.0-L10A2R-A3-P4-P5A")
    assert SCHEMA.endswith("/V1")
    assert value.executed_at == AT

    with pytest.raises(FrozenInstanceError):
        setattr(value, "tenant_id", "changed")


def test_deterministic_fingerprint_and_exact_replay_value():
    first = _evidence()
    second = _evidence()

    assert first == second
    assert first.fingerprint == second.fingerprint
    assert len(first.fingerprint) == 128
    assert set(first.fingerprint) <= set("0123456789abcdef")


def test_timezone_is_normalized_to_utc():
    offset = timezone(timedelta(hours=2))
    value = _evidence(
        executed_at=datetime(2026, 10, 2, 17, 30, tzinfo=offset)
    )

    assert value.executed_at == AT
    assert value.fingerprint == _evidence().fingerprint


@pytest.mark.parametrize(
    ("field", "value", "expected"),
    [
        ("execution_evidence_id", "", "EXECUTION_EVIDENCE_ID_INVALID"),
        ("tenant_id", "global", "TENANT_REQUIRED"),
        ("command_id", " command", "COMMAND_ID_INVALID"),
        ("cleanup_authorization_id", "", "CLEANUP_AUTHORIZATION_ID_INVALID"),
        ("provider_name", " aws_s3", "PROVIDER_NAME_INVALID"),
        ("storage_reference", "", "STORAGE_REFERENCE_INVALID"),
        ("object_version_reference", "", "OBJECT_VERSION_REFERENCE_INVALID"),
        ("command_fingerprint", "c" * 127, "COMMAND_FINGERPRINT_INVALID"),
        (
            "cleanup_authorization_fingerprint",
            "d" * 127,
            "CLEANUP_AUTHORIZATION_FINGERPRINT_INVALID",
        ),
    ],
)
def test_malformed_identity_and_fingerprint_reject(
    field,
    value,
    expected,
):
    with pytest.raises(
        LegalEvidenceProviderDeleteExecutionEvidenceError,
        match=expected,
    ):
        _evidence(**{field: value})


def test_naive_execution_time_rejects():
    with pytest.raises(
        LegalEvidenceProviderDeleteExecutionEvidenceError,
        match="EXECUTED_AT_INVALID",
    ):
        _evidence(executed_at=datetime(2026, 10, 2, 15, 30))


def test_delete_marker_reference_requires_delete_marker():
    with pytest.raises(
        LegalEvidenceProviderDeleteExecutionEvidenceError,
        match="DELETE_MARKER_EVIDENCE_INVALID",
    ):
        _evidence(
            delete_marker=False,
            delete_marker_version_reference="delete-marker-version",
        )


def test_delete_marker_evidence_is_preserved_when_present():
    value = _evidence(
        delete_marker=True,
        delete_marker_version_reference="delete-marker-version",
    )

    assert value.delete_marker is True
    assert (
        value.delete_marker_version_reference
        == "delete-marker-version"
    )


def test_document_round_trip_is_exact():
    value = _evidence()

    hydrated = LegalEvidenceProviderDeleteExecutionEvidence.from_document(
        value.to_document()
    )

    assert hydrated == value
    assert hydrated.fingerprint == value.fingerprint


def test_document_corruption_rejects():
    value = _evidence()
    document = value.to_document()
    document["storage_reference"] = "different/storage"

    with pytest.raises(
        LegalEvidenceProviderDeleteExecutionEvidenceError,
        match="FINGERPRINT_MISMATCH",
    ):
        LegalEvidenceProviderDeleteExecutionEvidence.from_document(document)


def test_document_extra_field_rejects():
    document = _evidence().to_document()
    document["unexpected"] = True

    with pytest.raises(
        LegalEvidenceProviderDeleteExecutionEvidenceError,
        match="DOCUMENT_SCHEMA_INVALID",
    ):
        LegalEvidenceProviderDeleteExecutionEvidence.from_document(document)


def test_domain_contains_no_provider_execution_or_registry_authority():
    import inspect

    source = inspect.getsource(
        LegalEvidenceProviderDeleteExecutionEvidence
    )

    forbidden = (
        "delete_object",
        "boto3",
        "pymongo",
        "insert_one",
        "update_one",
        "delete_one",
        "registry",
    )

    for token in forbidden:
        assert token not in source


def test_unknown_delete_marker_evidence_is_preserved():
    value = _evidence(
        delete_marker=None,
        delete_marker_version_reference=None,
    )

    assert value.delete_marker is None
    assert value.delete_marker_version_reference is None

    hydrated = LegalEvidenceProviderDeleteExecutionEvidence.from_document(
        value.to_document()
    )
    assert hydrated == value


def test_unknown_delete_marker_cannot_claim_marker_version():
    with pytest.raises(
        LegalEvidenceProviderDeleteExecutionEvidenceError,
        match="DELETE_MARKER_EVIDENCE_INVALID",
    ):
        _evidence(
            delete_marker=None,
            delete_marker_version_reference="marker-version",
        )
