"""Direct certificate for the provider-delete execution capability contract.

TITLE: Legal Evidence Provider Delete Execution Port Direct Certificate
VERSION: v1.0.0-L10A2R-C4D6E-A3-P4-P1-C1-PROVIDER-DELETE-EXECUTION-PORT-CERT
AUTHORITY: WILSY OS Core Governance / Python EOS Legal Operations
EPITOME:
    Certify immutable cleanup-command lineage binding and the strict absence of
    provider clients, deletion execution, durable mutation and success truth.
ABSOLUTE CANONICAL PATH:
    /Users/wilsonkhanyezi/legal-doc-system/tests/unit/test_legal_evidence_provider_delete_execution_port.py
COLLABORATION / OWNERSHIP:
    Legal Operations / Legal Evidence object plane.
CERTIFICATION / UPDATE DATE:
    2026-10-02
CHANGELOG:
    v1.0.0 establishes direct certification of the pure provider-delete
    execution-port capability contract.
AUTHORITY BOUNDARY:
    Cleanup command input only; this certificate grants no provider mutation,
    deletion-success truth, retention release, hold release or orphan proof.
FINANCIAL AUTHORITY BOUNDARY:
    None. Kennel EOS remains exclusive financial execution authority.
"""

from __future__ import annotations

from dataclasses import FrozenInstanceError
from datetime import datetime, timezone
from hashlib import sha3_512
import json
from pathlib import Path
from typing import Any, Mapping

import pytest

from tools.eos.legal_operations.domain.legal_evidence_provider_cleanup_command import (
    LegalEvidenceProviderCleanupCommand,
    SCHEMA as COMMAND_SCHEMA,
    VERSION as COMMAND_VERSION,
)
from tools.eos.legal_operations.service.legal_evidence_provider_delete_execution_port import (
    LegalEvidenceProviderDeleteExecutionPort,
    LegalEvidenceProviderDeleteExecutionPortError,
    LegalEvidenceProviderDeleteExecutionRequest,
    VERSION,
)


def _command() -> LegalEvidenceProviderCleanupCommand:
    """Hydrate one valid command through the certified durable path."""
    payload: dict[str, object] = {
        "schema": COMMAND_SCHEMA,
        "command_version": COMMAND_VERSION,
        "command_id": "cleanup-command-p4-p1-cert",
        "tenant_id": "tenant-p4-p1-cert",
        "principal_id": "principal-p4-p1-cert",
        "provider_name": "aws_s3",
        "storage_reference": "opaque/storage/p4-p1-cert",
        "object_version_reference": "version-p4-p1-cert",
        "cleanup_authorization_id": "cleanup-auth-p4-p1-cert",
        "cleanup_authorization_fingerprint": "a" * 128,
        "tenant_authorization_decision_id": "decision-p4-p1-cert",
        "tenant_authorization_evidence_fingerprint": "b" * 128,
        "issued_at": datetime(
            2026,
            10,
            2,
            14,
            0,
            0,
            tzinfo=timezone.utc,
        ).isoformat(),
        "reason_reference": "reason-p4-p1-cert",
    }

    canonical = json.dumps(
        payload,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=True,
    ).encode("utf-8")

    payload["fingerprint"] = sha3_512(canonical).hexdigest()

    return LegalEvidenceProviderCleanupCommand.from_dict(
        payload
    )


class _FakeDeleteAdapter:
    def __init__(self) -> None:
        self.requests: list[
            LegalEvidenceProviderDeleteExecutionRequest
        ] = []

    def execute_provider_delete(
        self,
        request: LegalEvidenceProviderDeleteExecutionRequest,
    ) -> Mapping[str, Any]:
        self.requests.append(request)
        return {"opaque": "provider-response"}


def test_version_and_protocol_surface() -> None:
    assert VERSION == (
        "v1.0.0-L10A2R-C4D6E-A3-P4-P1-"
        "PROVIDER-DELETE-EXECUTION-PORT"
    )
    assert hasattr(
        LegalEvidenceProviderDeleteExecutionPort,
        "execute_provider_delete",
    )


def test_request_is_frozen_slots_and_exactly_bound() -> None:
    command = _command()

    request = (
        LegalEvidenceProviderDeleteExecutionRequest
        .from_cleanup_command(command)
    )

    assert request.command_id == command.command_id
    assert request.command_fingerprint == command.fingerprint
    assert request.tenant_id == command.tenant_id
    assert request.provider_name == command.provider_name
    assert request.storage_reference == command.storage_reference
    assert (
        request.object_version_reference
        == command.object_version_reference
    )
    assert (
        request.cleanup_authorization_id
        == command.cleanup_authorization_id
    )
    assert (
        request.cleanup_authorization_fingerprint
        == command.cleanup_authorization_fingerprint
    )

    assert not hasattr(request, "__dict__")

    with pytest.raises((FrozenInstanceError, AttributeError)):
        request.tenant_id = "other"  # type: ignore[misc]


def test_non_exact_command_type_rejects() -> None:
    class FakeCommand:
        pass

    with pytest.raises(
        LegalEvidenceProviderDeleteExecutionPortError,
        match="CLEANUP_COMMAND_INVALID",
    ):
        LegalEvidenceProviderDeleteExecutionRequest.from_cleanup_command(
            FakeCommand(),  # type: ignore[arg-type]
        )


@pytest.mark.parametrize(
    ("field", "value", "error"),
    [
        ("command_id", "", "COMMAND_ID_INVALID"),
        ("tenant_id", "", "TENANT_ID_INVALID"),
        ("provider_name", " aws_s3", "PROVIDER_NAME_INVALID"),
        (
            "storage_reference",
            "opaque/storage ",
            "STORAGE_REFERENCE_INVALID",
        ),
        (
            "object_version_reference",
            "",
            "OBJECT_VERSION_REFERENCE_INVALID",
        ),
        (
            "cleanup_authorization_id",
            "",
            "CLEANUP_AUTHORIZATION_ID_INVALID",
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
def test_malformed_request_rejects(
    field: str,
    value: str,
    error: str,
) -> None:
    payload = {
        "command_id": "command-cert",
        "command_fingerprint": "a" * 128,
        "tenant_id": "tenant-cert",
        "provider_name": "aws_s3",
        "storage_reference": "opaque/storage/cert",
        "object_version_reference": "version-cert",
        "cleanup_authorization_id": "cleanup-auth-cert",
        "cleanup_authorization_fingerprint": "b" * 128,
    }
    payload[field] = value

    with pytest.raises(
        LegalEvidenceProviderDeleteExecutionPortError,
        match=error,
    ):
        LegalEvidenceProviderDeleteExecutionRequest(**payload)


def test_runtime_protocol_accepts_matching_adapter_shape() -> None:
    adapter = _FakeDeleteAdapter()

    assert isinstance(
        adapter,
        LegalEvidenceProviderDeleteExecutionPort,
    )

    request = (
        LegalEvidenceProviderDeleteExecutionRequest
        .from_cleanup_command(_command())
    )
    result = adapter.execute_provider_delete(request)

    assert result == {"opaque": "provider-response"}
    assert adapter.requests == [request]


def test_contract_source_contains_no_provider_or_durable_execution() -> None:
    source = Path(
        "tools/eos/legal_operations/service/"
        "legal_evidence_provider_delete_execution_port.py"
    ).read_text()

    forbidden = (
        "boto3",
        "botocore",
        ".delete_object(",
        ".delete_objects(",
        "MongoClient",
        "insert_one(",
        "update_one(",
        "delete_one(",
        "delete_many(",
    )

    for value in forbidden:
        assert value not in source


def test_contract_does_not_manufacture_success_evidence() -> None:
    source = Path(
        "tools/eos/legal_operations/service/"
        "legal_evidence_provider_delete_execution_port.py"
    ).read_text()

    forbidden_names = (
        "LegalEvidenceProviderDeleteReceipt",
        "LegalEvidenceProviderDeletionReceipt",
        "LegalEvidenceProviderDeleteSuccess",
        "LegalEvidenceProviderDeletionEvidence",
    )

    for value in forbidden_names:
        assert value not in source


def test_port_exposes_no_registry_or_reconciliation_surface() -> None:
    assert not hasattr(
        LegalEvidenceProviderDeleteExecutionPort,
        "create_or_replay",
    )
    assert not hasattr(
        LegalEvidenceProviderDeleteExecutionPort,
        "reconcile",
    )
    assert not hasattr(
        LegalEvidenceProviderDeleteExecutionPort,
        "persist",
    )


# ARTIFACT: test_legal_evidence_provider_delete_execution_port.py
# VERSION: v1.0.0-L10A2R-C4D6E-A3-P4-P1-C1-PROVIDER-DELETE-EXECUTION-PORT-CERT
# AUTHORITY INPUT: exact cleanup command only
# TENANT POSTURE: exact command tenant preserved
# OBJECT POSTURE: provider/storage/object-version preserved
# PROVIDER CLIENT POSTURE: absent from production contract
# PROVIDER EXECUTION CERTIFIED: no
# DELETION SUCCESS EVIDENCE CERTIFIED: no
# DURABLE MUTATION CERTIFIED: no
# RECONCILIATION CERTIFIED: no
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively
# END OF WILSY OS SOVEREIGN TEST ARTIFACT
