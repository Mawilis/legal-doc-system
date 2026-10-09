"""Direct certificate for Legal Evidence provider cleanup command domain.

TITLE: Legal Evidence Provider Cleanup Command Direct Certificate
VERSION: v1.1.0-L10A2R-C4D6E-A3-P3-P1-CLEANUP-COMMAND-DURABLE-HYDRATION-CERT
AUTHORITY: WILSY OS Core Governance / Python EOS Legal Operations
EPITOME: Certify exact immutable binding of A2 cleanup authorization to
         successful actor authorization evidence without provider execution.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tests/unit/test_legal_evidence_provider_cleanup_command.py
COLLABORATION / OWNERSHIP: Legal Operations / Legal Evidence
CERTIFICATION / UPDATE DATE: 2026-10-02
CHANGELOG:
    v1.1.0 certifies strict durable serialization/hydration, exact-schema
    round-trip integrity, SHA3-512 corruption rejection, canonical persisted
    timestamps and preservation of the no-provider-execution boundary.
    v1.0.0 establishes direct pure-domain certification for deterministic
    command issuance, exact A2/IAM correlation, tenant/object scope,
    chronology, tamper resistance and execution-authority absence.
AUTHORITY BOUNDARY:
    Test evidence only. No provider mutation, deletion execution, persistence,
    HTTP/API routing, billing, payment, execution or settlement.
TENANT BOUNDARY:
    Exact cleanup and actor evidence must bind one tenant.
FINANCIAL AUTHORITY BOUNDARY:
    None. Kennel EOS remains the exclusive financial execution authority.
"""

from __future__ import annotations

from copy import deepcopy

from dataclasses import FrozenInstanceError, fields, replace
from datetime import datetime, timedelta, timezone
from hashlib import sha3_512
import inspect
import json

import pytest

from tools.eos.auth.tenant_authorization_decision_evidence import (
    TenantAuthorizationDecisionEvidence,
)
from tools.eos.legal_operations.domain.legal_evidence_provider_cleanup_authorization import (
    SCHEMA as CLEANUP_AUTH_SCHEMA,
    VERSION as CLEANUP_AUTH_VERSION,
    LegalEvidenceProviderCleanupAuthorization,
)
from tools.eos.legal_operations.domain.legal_evidence_provider_cleanup_command import (
    CLEANUP_AUTHORIZATION_ROLE,
    CLEANUP_BUSINESS_ROLE,
    CLEANUP_OPERATION,
    CLEANUP_PERMISSION,
    SCHEMA,
    VERSION,
    LegalEvidenceProviderCleanupCommand,
    LegalEvidenceProviderCleanupCommandError,
    cleanup_authorization_subject_reference,
    issue_legal_evidence_provider_cleanup_command,
)


AT = datetime(2026, 10, 2, 8, 0, 0, tzinfo=timezone.utc)
ACTOR_AT = AT + timedelta(minutes=1)
ISSUED_AT = AT + timedelta(minutes=2)

TENANT = "tenant-a3-p2-cert"
PRINCIPAL = "principal-a3-p2-cert"
PROVIDER = "aws_s3"
STORAGE = "opaque/storage/a3-p2-cert"
OBJECT_VERSION = "version-a3-p2-cert"


def _cleanup_authorization(
    *,
    tenant_id: str = TENANT,
    authorization_id: str = "cleanup-authorization-a3-p2-cert",
) -> LegalEvidenceProviderCleanupAuthorization:
    document: dict[str, object] = {
        "schema": CLEANUP_AUTH_SCHEMA,
        "authorization_version": CLEANUP_AUTH_VERSION,
        "authorization_id": authorization_id,
        "tenant_id": tenant_id,
        "provider_name": PROVIDER,
        "storage_reference": STORAGE,
        "object_version_reference": OBJECT_VERSION,
        "orphan_proof_fingerprint": "a" * 128,
        "disownership_fingerprint": "b" * 128,
        "preservation_fingerprint": "c" * 128,
        "preservation_assessed_at": (
            AT - timedelta(minutes=1)
        ).isoformat(),
        "authorized_at": AT.isoformat(),
        "reason_reference": "cleanup-authorized-a3-p2-cert",
    }

    raw = json.dumps(
        document,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=True,
    ).encode("utf-8")

    document["fingerprint"] = sha3_512(raw).hexdigest()

    return LegalEvidenceProviderCleanupAuthorization.from_dict(
        document
    )


def _actor(
    cleanup: LegalEvidenceProviderCleanupAuthorization,
    *,
    tenant_id: str | None = None,
    operation: str = CLEANUP_OPERATION,
    permission: str = CLEANUP_PERMISSION,
    business_role: str = CLEANUP_BUSINESS_ROLE,
    authorization_role: str = CLEANUP_AUTHORIZATION_ROLE,
    subject_reference: str | None = None,
    subject_evidence_fingerprint: str | None = None,
    authorized_at: datetime = ACTOR_AT,
) -> TenantAuthorizationDecisionEvidence:
    return TenantAuthorizationDecisionEvidence(
        tenant_id=(
            cleanup.tenant_id
            if tenant_id is None
            else tenant_id
        ),
        authorization_decision_id="actor-decision-a3-p2-cert",
        principal_id=PRINCIPAL,
        operation=operation,
        permission=permission,
        business_role=business_role,
        authorization_role=authorization_role,
        membership_revision=7,
        role_assignment_revision=11,
        subject_reference=(
            cleanup_authorization_subject_reference(
                cleanup.authorization_id
            )
            if subject_reference is None
            else subject_reference
        ),
        subject_evidence_fingerprint=(
            cleanup.fingerprint
            if subject_evidence_fingerprint is None
            else subject_evidence_fingerprint
        ),
        permission_namespace_version=(
            "v1.33.0-L10A2R-C4D6E-A3-P1A-"
            "LEGAL-EVIDENCE-CLEANUP-AUTHORITY-PERMISSION"
        ),
        authorization_role_policy_version=(
            "v1.33.0-L10A2R-C4D6E-A3-P1B-"
            "LEGAL-EVIDENCE-CLEANUP-AUTHORITY-PARTNER-GRANT"
        ),
        tenant_business_role_policy_version=(
            "v1.31.0-L10A2R-C4D6E-A3-P1C-"
            "LEGAL-EVIDENCE-CLEANUP-AUTHORITY-PARTNER-ELIGIBILITY"
        ),
        tenant_authorization_composition_version=(
            "v1.30.0-L10A2R-C4D6E-A3-P1D-"
            "LEGAL-EVIDENCE-CLEANUP-AUTHORIZATION-BINDING"
        ),
        idempotency_key="cleanup-command-a3-p2-cert",
        authorized_at=authorized_at,
    )


def _issue(
    *,
    cleanup: LegalEvidenceProviderCleanupAuthorization | None = None,
    actor: TenantAuthorizationDecisionEvidence | None = None,
    command_id: str = "cleanup-command-a3-p2-cert",
    issued_at: datetime = ISSUED_AT,
    reason_reference: str = "cleanup-command-reason-a3-p2-cert",
) -> LegalEvidenceProviderCleanupCommand:
    cleanup_value = cleanup or _cleanup_authorization()
    actor_value = actor or _actor(cleanup_value)

    return issue_legal_evidence_provider_cleanup_command(
        cleanup_authorization=cleanup_value,
        actor_authorization=actor_value,
        command_id=command_id,
        issued_at=issued_at,
        reason_reference=reason_reference,
    )


def test_shape_version_schema_and_factory_only_contract() -> None:
    assert VERSION == (
        "v1.1.0-L10A2R-C4D6E-A3-P3-P1-"
        "CLEANUP-COMMAND-DURABLE-HYDRATION"
    )
    assert SCHEMA == (
        "wilsy.legal_evidence.provider_cleanup_command.v1"
    )

    assert [
        field.name
        for field in fields(
            LegalEvidenceProviderCleanupCommand
        )
    ] == [
        "command_id",
        "tenant_id",
        "principal_id",
        "provider_name",
        "storage_reference",
        "object_version_reference",
        "cleanup_authorization_id",
        "cleanup_authorization_fingerprint",
        "tenant_authorization_decision_id",
        "tenant_authorization_evidence_fingerprint",
        "issued_at",
        "reason_reference",
        "schema",
        "command_version",
        "_construction_proof",
    ]

    with pytest.raises(
        LegalEvidenceProviderCleanupCommandError,
        match="L10A2R_C4D6E_A3_P2_FACTORY_REQUIRED",
    ):
        LegalEvidenceProviderCleanupCommand(
            command_id="direct-forbidden",
            tenant_id=TENANT,
            principal_id=PRINCIPAL,
            provider_name=PROVIDER,
            storage_reference=STORAGE,
            object_version_reference=OBJECT_VERSION,
            cleanup_authorization_id="cleanup-direct",
            cleanup_authorization_fingerprint="a" * 128,
            tenant_authorization_decision_id="decision-direct",
            tenant_authorization_evidence_fingerprint="b" * 128,
            issued_at=ISSUED_AT,
            reason_reference="direct-forbidden",
        )


def test_positive_command_is_exact_deterministic_and_frozen() -> None:
    cleanup = _cleanup_authorization()
    actor = _actor(cleanup)

    first = _issue(
        cleanup=cleanup,
        actor=actor,
    )
    second = _issue(
        cleanup=cleanup,
        actor=actor,
    )

    assert first == second
    assert first.fingerprint == second.fingerprint
    assert len(first.fingerprint) == 128
    assert set(first.fingerprint) <= set("0123456789abcdef")

    assert first.tenant_id == cleanup.tenant_id
    assert first.principal_id == actor.principal_id
    assert first.provider_name == cleanup.provider_name
    assert first.storage_reference == cleanup.storage_reference
    assert (
        first.object_version_reference
        == cleanup.object_version_reference
    )
    assert (
        first.cleanup_authorization_id
        == cleanup.authorization_id
    )
    assert (
        first.cleanup_authorization_fingerprint
        == cleanup.fingerprint
    )
    assert (
        first.tenant_authorization_decision_id
        == actor.authorization_decision_id
    )
    assert (
        first.tenant_authorization_evidence_fingerprint
        == actor.authorization_evidence_fingerprint
    )
    assert first.issued_at == ISSUED_AT

    with pytest.raises(FrozenInstanceError):
        first.tenant_id = "mutated"  # type: ignore[misc]


@pytest.mark.parametrize(
    ("field", "value", "expected"),
    [
        (
            "operation",
            "legal_evidence_write",
            "ACTOR_OPERATION_MISMATCH",
        ),
        (
            "permission",
            "legal_operations:evidence:write",
            "ACTOR_PERMISSION_MISMATCH",
        ),
        (
            "business_role",
            "tenant_legal_attorney",
            "ACTOR_BUSINESS_ROLE_MISMATCH",
        ),
        (
            "authorization_role",
            "LEGAL_ATTORNEY",
            "ACTOR_AUTHORIZATION_ROLE_MISMATCH",
        ),
    ],
)
def test_crossed_actor_authority_dimensions_reject(
    field: str,
    value: str,
    expected: str,
) -> None:
    cleanup = _cleanup_authorization()

    kwargs: dict[str, object] = {field: value}
    actor = _actor(
        cleanup,
        **kwargs,  # type: ignore[arg-type]
    )

    with pytest.raises(
        LegalEvidenceProviderCleanupCommandError,
        match=f"L10A2R_C4D6E_A3_P2_{expected}",
    ):
        _issue(
            cleanup=cleanup,
            actor=actor,
        )


def test_cross_tenant_actor_evidence_rejects() -> None:
    cleanup = _cleanup_authorization()
    actor = _actor(
        cleanup,
        tenant_id="tenant-other",
    )

    with pytest.raises(
        LegalEvidenceProviderCleanupCommandError,
        match="L10A2R_C4D6E_A3_P2_TENANT_MISMATCH",
    ):
        _issue(
            cleanup=cleanup,
            actor=actor,
        )


def test_subject_reference_and_fingerprint_must_bind_exact_a2_fact() -> None:
    cleanup = _cleanup_authorization()

    wrong_reference = _actor(
        cleanup,
        subject_reference=(
            "legal-evidence-provider-cleanup-authorization:"
            "different"
        ),
    )

    with pytest.raises(
        LegalEvidenceProviderCleanupCommandError,
        match="L10A2R_C4D6E_A3_P2_ACTOR_SUBJECT_MISMATCH",
    ):
        _issue(
            cleanup=cleanup,
            actor=wrong_reference,
        )

    wrong_fingerprint = _actor(
        cleanup,
        subject_evidence_fingerprint="d" * 128,
    )

    with pytest.raises(
        LegalEvidenceProviderCleanupCommandError,
        match=(
            "L10A2R_C4D6E_A3_P2_"
            "ACTOR_SUBJECT_FINGERPRINT_MISMATCH"
        ),
    ):
        _issue(
            cleanup=cleanup,
            actor=wrong_fingerprint,
        )


def test_command_chronology_requires_both_sources_to_precede_issue() -> None:
    cleanup = _cleanup_authorization()

    actor = _actor(
        cleanup,
        authorized_at=AT + timedelta(minutes=3),
    )

    with pytest.raises(
        LegalEvidenceProviderCleanupCommandError,
        match="L10A2R_C4D6E_A3_P2_COMMAND_CHRONOLOGY_INVALID",
    ):
        _issue(
            cleanup=cleanup,
            actor=actor,
            issued_at=ISSUED_AT,
        )

    with pytest.raises(
        LegalEvidenceProviderCleanupCommandError,
        match="L10A2R_C4D6E_A3_P2_COMMAND_CHRONOLOGY_INVALID",
    ):
        _issue(
            cleanup=cleanup,
            actor=_actor(cleanup),
            issued_at=AT - timedelta(seconds=1),
        )


@pytest.mark.parametrize(
    ("name", "value"),
    [
        ("command_id", ""),
        ("command_id", " command"),
        ("reason_reference", ""),
        ("reason_reference", " reason"),
    ],
)
def test_malformed_command_identity_and_reason_reject(
    name: str,
    value: str,
) -> None:
    with pytest.raises(
        LegalEvidenceProviderCleanupCommandError,
    ):
        if name == "command_id":
            _issue(
                command_id=value,
            )
        else:
            assert name == "reason_reference"
            _issue(
                reason_reference=value,
            )


def test_replace_tamper_rejects_source_binding() -> None:
    command = _issue()

    with pytest.raises(
        LegalEvidenceProviderCleanupCommandError,
        match="L10A2R_C4D6E_A3_P2_SOURCE_BINDING_INVALID",
    ):
        replace(
            command,
            reason_reference="tampered",
        )

    with pytest.raises(
        LegalEvidenceProviderCleanupCommandError,
        match="L10A2R_C4D6E_A3_P2_SOURCE_BINDING_INVALID",
    ):
        replace(
            command,
            cleanup_authorization_fingerprint="e" * 128,
        )


def test_exact_document_round_trip_preserves_integrity() -> None:
    command = _issue()
    document = command.to_document()

    assert set(document) == {
        "schema",
        "command_version",
        "command_id",
        "tenant_id",
        "principal_id",
        "provider_name",
        "storage_reference",
        "object_version_reference",
        "cleanup_authorization_id",
        "cleanup_authorization_fingerprint",
        "tenant_authorization_decision_id",
        "tenant_authorization_evidence_fingerprint",
        "issued_at",
        "reason_reference",
        "fingerprint",
    }
    assert document["command_version"] == VERSION
    assert document["fingerprint"] == command.fingerprint

    hydrated = LegalEvidenceProviderCleanupCommand.from_dict(
        deepcopy(document)
    )

    assert hydrated == command
    assert hydrated.fingerprint == command.fingerprint
    assert hydrated.to_document() == document


def test_persisted_document_shape_corruption_rejects() -> None:
    extra = _issue().to_document()
    extra["unexpected_field"] = "forbidden"

    with pytest.raises(
        LegalEvidenceProviderCleanupCommandError,
        match="DOCUMENT_FIELDS_INVALID",
    ):
        LegalEvidenceProviderCleanupCommand.from_dict(extra)

    missing = _issue().to_document()
    missing.pop("reason_reference")

    with pytest.raises(
        LegalEvidenceProviderCleanupCommandError,
        match="DOCUMENT_FIELDS_INVALID",
    ):
        LegalEvidenceProviderCleanupCommand.from_dict(missing)


def test_persisted_document_fingerprint_corruption_rejects() -> None:
    fingerprint = _issue().to_document()
    fingerprint["fingerprint"] = "0" * 128

    with pytest.raises(
        LegalEvidenceProviderCleanupCommandError,
        match="FINGERPRINT_MISMATCH",
    ):
        LegalEvidenceProviderCleanupCommand.from_dict(
            fingerprint
        )

    payload = _issue().to_document()
    payload["reason_reference"] = "tampered"

    with pytest.raises(
        LegalEvidenceProviderCleanupCommandError,
        match="FINGERPRINT_MISMATCH",
    ):
        LegalEvidenceProviderCleanupCommand.from_dict(
            payload
        )


def test_persisted_schema_and_version_drift_reject() -> None:
    schema = _issue().to_document()
    schema["schema"] = "wilsy.invalid.cleanup.command.v1"

    with pytest.raises(
        LegalEvidenceProviderCleanupCommandError,
        match="SCHEMA_INVALID",
    ):
        LegalEvidenceProviderCleanupCommand.from_dict(schema)

    version = _issue().to_document()
    version["command_version"] = "v0.0.0-invalid"

    with pytest.raises(
        LegalEvidenceProviderCleanupCommandError,
        match="VERSION_INVALID",
    ):
        LegalEvidenceProviderCleanupCommand.from_dict(version)


def test_noncanonical_persisted_timestamp_rejects() -> None:
    document = _issue().to_document()
    document["issued_at"] = (
        str(document["issued_at"])
        .replace("+00:00", "Z")
    )

    with pytest.raises(
        LegalEvidenceProviderCleanupCommandError,
        match="DOCUMENT_TIMESTAMP_INVALID",
    ):
        LegalEvidenceProviderCleanupCommand.from_dict(
            document
        )


def test_hydration_grants_no_provider_delete_authority() -> None:
    hydrated = LegalEvidenceProviderCleanupCommand.from_dict(
        _issue().to_document()
    )

    for attribute in (
        "delete",
        "delete_object",
        "delete_objects",
        "execute",
        "provider_delete_authorized",
    ):
        assert not hasattr(hydrated, attribute)


def test_command_has_no_provider_persistence_or_execution_surface() -> None:
    command = _issue()
    source = inspect.getsource(
        __import__(
            "tools.eos.legal_operations.domain."
            "legal_evidence_provider_cleanup_command",
            fromlist=["*"],
        )
    )

    for attribute in (
        "delete",
        "delete_object",
        "delete_objects",
        "execute",
        "persist",
        "save",
    ):
        assert not hasattr(command, attribute)

    forbidden = (
        "boto3",
        "botocore",
        "S3BinaryStorageAdapter",
        "BinaryStoragePort",
        "insert_one",
        "update_one",
        "replace_one",
        "delete_one",
        "start_transaction",
    )

    for symbol in forbidden:
        assert symbol not in source


def test_subject_reference_is_deterministic_and_exact() -> None:
    cleanup = _cleanup_authorization()

    expected = (
        "legal-evidence-provider-cleanup-authorization:"
        + cleanup.authorization_id
    )

    assert (
        cleanup_authorization_subject_reference(
            cleanup.authorization_id
        )
        == expected
    )
    assert (
        cleanup_authorization_subject_reference(
            cleanup.authorization_id
        )
        == expected
    )


# ARTIFACT: test_legal_evidence_provider_cleanup_command.py
# VERSION: v1.1.0-L10A2R-C4D6E-A3-P3-P1-CLEANUP-COMMAND-DURABLE-HYDRATION-CERT
# AUTHORITY BOUNDARY: direct pure-domain certificate only
# TENANT POSTURE: exact A2 cleanup authorization + exact actor evidence correlation
# PROVIDER MUTATION POSTURE: none
# DELETION EXECUTION POSTURE: none
# PERSISTENCE POSTURE: none
# FAIL-CLOSED POSTURE: malformed, crossed, tampered and chronologically invalid evidence rejects
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively
# END OF WILSY OS SOVEREIGN TEST ARTIFACT
