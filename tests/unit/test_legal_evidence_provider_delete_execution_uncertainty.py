from dataclasses import FrozenInstanceError
from datetime import datetime, timedelta, timezone
from hashlib import sha3_512
import json

import pytest

from tools.eos.legal_operations.domain.legal_evidence_provider_cleanup_command import (
    SCHEMA as COMMAND_SCHEMA,
    VERSION as COMMAND_VERSION,
    LegalEvidenceProviderCleanupCommand,
)
from tools.eos.legal_operations.domain.legal_evidence_provider_delete_execution_evidence import (
    LegalEvidenceProviderDeleteExecutionEvidence,
)
from tools.eos.legal_operations.domain.legal_evidence_provider_delete_execution_uncertainty import (
    SCHEMA,
    VERSION,
    LegalEvidenceProviderDeleteExecutionUncertainty,
    LegalEvidenceProviderDeleteExecutionUncertaintyError,
    open_legal_evidence_provider_delete_execution_uncertainty,
)


AT = datetime(2026, 10, 2, 16, 0, tzinfo=timezone.utc)
SHA_C = "c" * 128
SHA_D = "d" * 128


def _command(**changes):
    values: dict[str, object] = {
        "schema": COMMAND_SCHEMA,
        "command_version": COMMAND_VERSION,
        "command_id": "command-1",
        "tenant_id": "tenant-1",
        "principal_id": "principal-1",
        "provider_name": "aws_s3",
        "storage_reference": "opaque-storage-key",
        "object_version_reference": "version-1",
        "cleanup_authorization_id": "authorization-1",
        "cleanup_authorization_fingerprint": SHA_D,
        "tenant_authorization_decision_id": "decision-1",
        "tenant_authorization_evidence_fingerprint": "b" * 128,
        "issued_at": AT.isoformat(),
        "reason_reference": "reason-1",
    }
    values.update(changes)

    issued_at = values.get("issued_at")
    if isinstance(issued_at, datetime):
        values["issued_at"] = issued_at.isoformat()

    raw = json.dumps(
        values,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=True,
    ).encode("utf-8")
    values["fingerprint"] = sha3_512(raw).hexdigest()

    return LegalEvidenceProviderCleanupCommand.from_dict(values)


def _execution(command=None, **changes):
    command = _command() if command is None else command
    values = {
        "execution_evidence_id": "execution-1",
        "tenant_id": command.tenant_id,
        "command_id": command.command_id,
        "cleanup_authorization_id": command.cleanup_authorization_id,
        "provider_name": command.provider_name,
        "storage_reference": command.storage_reference,
        "object_version_reference": command.object_version_reference,
        "command_fingerprint": command.fingerprint,
        "cleanup_authorization_fingerprint":
            command.cleanup_authorization_fingerprint,
        "delete_marker": None,
        "delete_marker_version_reference": None,
        "executed_at": AT + timedelta(seconds=1),
    }
    values.update(changes)
    return LegalEvidenceProviderDeleteExecutionEvidence(**values)


def _uncertainty(**changes):
    command = changes.pop("command", _command())
    execution = changes.pop(
        "execution_evidence",
        _execution(command),
    )
    recorded = changes.pop(
        "uncertainty_recorded_at",
        execution.executed_at + timedelta(seconds=1),
    )
    assert not changes
    return open_legal_evidence_provider_delete_execution_uncertainty(
        uncertainty_id="uncertainty-1",
        command=command,
        execution_evidence=execution,
        uncertainty_recorded_at=recorded,
    )


def test_version_schema_and_frozen_slots():
    value = _uncertainty()
    assert value.schema == SCHEMA
    assert value.version == VERSION
    assert value.__slots__
    with pytest.raises(FrozenInstanceError):
        value.command_id = "other"  # type: ignore[misc]


def test_exact_source_binding_and_execution_fingerprint():
    command = _command()
    execution = _execution(command)
    value = _uncertainty(
        command=command,
        execution_evidence=execution,
    )

    assert value.tenant_id == command.tenant_id
    assert value.command_id == command.command_id
    assert value.command_fingerprint == command.fingerprint
    assert value.execution_evidence_id == execution.execution_evidence_id
    assert value.execution_evidence_fingerprint == execution.fingerprint
    assert value.delete_marker is None


@pytest.mark.parametrize(
    ("field", "replacement"),
    [
        ("tenant_id", "tenant-2"),
        ("command_id", "command-other"),
        ("cleanup_authorization_id", "authorization-other"),
        ("provider_name", "provider-other"),
        ("storage_reference", "other-key"),
        ("object_version_reference", "version-other"),
        ("command_fingerprint", SHA_C),
        ("cleanup_authorization_fingerprint", SHA_C),
    ],
)
def test_source_mismatch_rejects(field, replacement):
    command = _command()
    execution = _execution(command, **{field: replacement})
    with pytest.raises(
        LegalEvidenceProviderDeleteExecutionUncertaintyError,
        match="MISMATCH",
    ):
        _uncertainty(
            command=command,
            execution_evidence=execution,
        )


def test_execution_cannot_precede_command():
    command = _command()
    execution = _execution(
        command,
        executed_at=command.issued_at - timedelta(microseconds=1),
    )
    with pytest.raises(
        LegalEvidenceProviderDeleteExecutionUncertaintyError,
        match="EXECUTION_CHRONOLOGY_INVALID",
    ):
        _uncertainty(
            command=command,
            execution_evidence=execution,
        )


def test_uncertainty_cannot_precede_execution():
    command = _command()
    execution = _execution(command)
    with pytest.raises(
        LegalEvidenceProviderDeleteExecutionUncertaintyError,
        match="CHRONOLOGY_INVALID",
    ):
        _uncertainty(
            command=command,
            execution_evidence=execution,
            uncertainty_recorded_at=(
                execution.executed_at - timedelta(microseconds=1)
            ),
        )


def test_delete_marker_unknown_is_preserved():
    value = _uncertainty()
    assert value.delete_marker is None
    assert value.delete_marker_version_reference is None


def test_delete_marker_positive_evidence_is_preserved():
    command = _command()
    execution = _execution(
        command,
        delete_marker=True,
        delete_marker_version_reference="version-1",
    )
    value = _uncertainty(
        command=command,
        execution_evidence=execution,
    )
    assert value.delete_marker is True
    assert value.delete_marker_version_reference == "version-1"


def test_document_round_trip_is_exact():
    value = _uncertainty()
    document = value.to_document()
    assert (
        LegalEvidenceProviderDeleteExecutionUncertainty.from_document(
            document
        )
        == value
    )


def test_document_extra_field_rejects():
    document = _uncertainty().to_document()
    document["later_authority"] = True
    with pytest.raises(
        LegalEvidenceProviderDeleteExecutionUncertaintyError,
        match="DOCUMENT_SCHEMA_INVALID",
    ):
        LegalEvidenceProviderDeleteExecutionUncertainty.from_document(
            document
        )


def test_document_corruption_rejects():
    document = _uncertainty().to_document()
    document["command_id"] = "command-corrupt"
    with pytest.raises(
        LegalEvidenceProviderDeleteExecutionUncertaintyError,
        match="FINGERPRINT_MISMATCH",
    ):
        LegalEvidenceProviderDeleteExecutionUncertainty.from_document(
            document
        )


def test_naive_times_reject():
    value = _uncertainty()
    document = value.to_document()
    document["uncertainty_recorded_at"] = "2026-10-02T16:00:02"
    document["fingerprint"] = ""
    with pytest.raises(
        LegalEvidenceProviderDeleteExecutionUncertaintyError,
        match="UNCERTAINTY_RECORDED_AT_INVALID",
    ):
        LegalEvidenceProviderDeleteExecutionUncertainty.from_document(
            document
        )


def test_domain_contains_no_execution_registry_or_retry_authority():
    forbidden = {
        "execute_delete",
        "delete_object",
        "create_or_replay",
        "reconcile",
        "retry",
        "commit",
        "abort",
        "authorize",
    }
    public = {
        name
        for name in dir(
            LegalEvidenceProviderDeleteExecutionUncertainty
        )
        if not name.startswith("_")
    }
    assert forbidden.isdisjoint(public)
