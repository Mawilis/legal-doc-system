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
from tools.eos.legal_operations.domain.legal_evidence_provider_delete_execution_claim import (
    SCHEMA,
    VERSION,
    LegalEvidenceProviderDeleteExecutionClaim,
    LegalEvidenceProviderDeleteExecutionClaimError,
    open_legal_evidence_provider_delete_execution_claim,
)


AT = datetime(2026, 10, 2, 16, 0, tzinfo=timezone.utc)


def _command(**changes):
    values: dict[str, object] = {
        "schema": COMMAND_SCHEMA,
        "command_version": COMMAND_VERSION,
        "command_id": "command-claim-1",
        "tenant_id": "tenant-claim-1",
        "principal_id": "principal-claim-1",
        "provider_name": "aws_s3",
        "storage_reference": "opaque-storage-key",
        "object_version_reference": "version-1",
        "cleanup_authorization_id": "authorization-1",
        "cleanup_authorization_fingerprint": "a" * 128,
        "tenant_authorization_decision_id": "decision-1",
        "tenant_authorization_evidence_fingerprint": "b" * 128,
        "issued_at": AT.isoformat(),
        "reason_reference": "reason-1",
    }
    values.update(changes)

    issued_at = values.get("issued_at")
    if isinstance(issued_at, datetime):
        values["issued_at"] = issued_at.isoformat()

    canonical = json.dumps(
        values,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=True,
    ).encode("utf-8")
    values["fingerprint"] = sha3_512(canonical).hexdigest()

    return LegalEvidenceProviderCleanupCommand.from_dict(values)


def _claim(
    *,
    command=None,
    claim_id="claim-1",
    claimed_at=None,
):
    command = _command() if command is None else command
    when = (
        command.issued_at + timedelta(seconds=1)
        if claimed_at is None
        else claimed_at
    )
    return open_legal_evidence_provider_delete_execution_claim(
        claim_id=claim_id,
        command=command,
        claimed_at=when,
    )


def test_version_schema_frozen_slots_and_exact_binding():
    command = _command()
    value = _claim(command=command)

    assert value.schema == SCHEMA
    assert value.version == VERSION
    assert value.tenant_id == command.tenant_id
    assert value.command_id == command.command_id
    assert (
        value.cleanup_authorization_id
        == command.cleanup_authorization_id
    )
    assert value.provider_name == command.provider_name
    assert value.storage_reference == command.storage_reference
    assert (
        value.object_version_reference
        == command.object_version_reference
    )
    assert value.command_fingerprint == command.fingerprint
    assert (
        value.cleanup_authorization_fingerprint
        == command.cleanup_authorization_fingerprint
    )
    with pytest.raises(FrozenInstanceError):
        value.command_id = "other"  # type: ignore[misc]


def test_deterministic_fingerprint_for_exact_claim():
    command = _command()
    when = command.issued_at + timedelta(seconds=1)

    first = _claim(command=command, claimed_at=when)
    second = _claim(command=command, claimed_at=when)

    assert first == second
    assert first.fingerprint == second.fingerprint
    assert len(first.fingerprint) == 128


def test_timezone_normalizes_to_utc():
    command = _command()
    local = datetime(
        2026,
        10,
        2,
        18,
        0,
        1,
        tzinfo=timezone(timedelta(hours=2)),
    )
    value = _claim(command=command, claimed_at=local)
    assert value.claimed_at == datetime(
        2026,
        10,
        2,
        16,
        0,
        1,
        tzinfo=timezone.utc,
    )


def test_claim_cannot_precede_command():
    command = _command()
    with pytest.raises(
        LegalEvidenceProviderDeleteExecutionClaimError,
        match="CHRONOLOGY_INVALID",
    ):
        _claim(
            command=command,
            claimed_at=command.issued_at - timedelta(microseconds=1),
        )


@pytest.mark.parametrize(
    ("field", "value", "code"),
    [
        ("claim_id", "", "CLAIM_ID_INVALID"),
        ("tenant_id", "global", "TENANT_REQUIRED"),
        ("command_id", " command", "COMMAND_ID_INVALID"),
        (
            "cleanup_authorization_id",
            "",
            "CLEANUP_AUTHORIZATION_ID_INVALID",
        ),
        ("provider_name", " aws_s3", "PROVIDER_NAME_INVALID"),
        ("storage_reference", "", "STORAGE_REFERENCE_INVALID"),
        (
            "object_version_reference",
            "",
            "OBJECT_VERSION_REFERENCE_INVALID",
        ),
        (
            "command_fingerprint",
            "c" * 127,
            "COMMAND_FINGERPRINT_INVALID",
        ),
        (
            "cleanup_authorization_fingerprint",
            "d" * 127,
            "CLEANUP_AUTHORIZATION_FINGERPRINT_INVALID",
        ),
    ],
)
def test_malformed_direct_value_rejects(field, value, code):
    base = _claim()
    values = base.to_document()
    values.pop("fingerprint")
    values[field] = value
    values["claimed_at"] = base.claimed_at

    with pytest.raises(
        LegalEvidenceProviderDeleteExecutionClaimError,
        match=code,
    ):
        LegalEvidenceProviderDeleteExecutionClaim(
            **values,  # type: ignore[arg-type]
        )


def test_naive_claimed_at_rejects():
    base = _claim()
    values = base.to_document()
    values.pop("fingerprint")
    values["claimed_at"] = datetime(2026, 10, 2, 16, 0, 1)

    with pytest.raises(
        LegalEvidenceProviderDeleteExecutionClaimError,
        match="CLAIMED_AT_INVALID",
    ):
        LegalEvidenceProviderDeleteExecutionClaim(
            **values,  # type: ignore[arg-type]
        )


def test_document_round_trip_is_exact():
    value = _claim()
    assert (
        LegalEvidenceProviderDeleteExecutionClaim.from_document(
            value.to_document()
        )
        == value
    )


def test_document_extra_field_rejects():
    document = _claim().to_document()
    document["retry_authorized"] = True

    with pytest.raises(
        LegalEvidenceProviderDeleteExecutionClaimError,
        match="DOCUMENT_SCHEMA_INVALID",
    ):
        LegalEvidenceProviderDeleteExecutionClaim.from_document(
            document
        )


def test_document_corruption_rejects():
    document = _claim().to_document()
    document["command_id"] = "corrupt-command"

    with pytest.raises(
        LegalEvidenceProviderDeleteExecutionClaimError,
        match="FINGERPRINT_MISMATCH",
    ):
        LegalEvidenceProviderDeleteExecutionClaim.from_document(
            document
        )


def test_claim_has_no_provider_retry_reconciliation_or_absence_authority():
    forbidden = {
        "execute_delete",
        "delete_object",
        "retry",
        "reconcile",
        "authorize_retry",
        "prove_absence",
        "release",
    }
    public = {
        name
        for name in dir(LegalEvidenceProviderDeleteExecutionClaim)
        if not name.startswith("_")
    }
    assert forbidden.isdisjoint(public)
