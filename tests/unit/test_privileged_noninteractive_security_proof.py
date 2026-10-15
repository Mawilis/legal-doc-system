"""
Direct certificate for P3-R3D noninteractive current-security-proof domain.
"""

from dataclasses import (
    FrozenInstanceError,
)
from datetime import (
    datetime,
    timedelta,
    timezone,
)
import inspect

import pytest

from tools.eos.auth.privileged_noninteractive_security_proof import (
    PrivilegedNoninteractiveProofStatus,
    PrivilegedNoninteractiveSecurityProof,
    PrivilegedNoninteractiveSecurityProofError,
)


AT = datetime(
    2026,
    10,
    14,
    6,
    0,
    0,
    123456,
    tzinfo=timezone.utc,
)


def proof(
    **overrides,
) -> PrivilegedNoninteractiveSecurityProof:
    values = {
        "proof_id":
            "workload-proof-001",
        "principal_id":
            "principal-001",
        "proof_reference":
            "workload-proof-reference:001",
        "credential_or_attestation_reference":
            "attestation-reference:001",
        "observed_at":
            AT,
        "proof_status":
            PrivilegedNoninteractiveProofStatus
            .VERIFIED,
    }

    values.update(
        overrides
    )

    return (
        PrivilegedNoninteractiveSecurityProof(
            **values
        )
    )


def test_exact_frozen_field_surface() -> None:
    assert set(
        PrivilegedNoninteractiveSecurityProof
        .__dataclass_fields__
    ) == {
        "proof_id",
        "principal_id",
        "proof_reference",
        "credential_or_attestation_reference",
        "observed_at",
        "proof_status",
    }


def test_verified_proof_constructs() -> None:
    value = proof()

    assert (
        value.proof_status
        is PrivilegedNoninteractiveProofStatus
        .VERIFIED
    )

    assert (
        value.workload_proof_successful
        is True
    )


@pytest.mark.parametrize(
    "status",
    (
        PrivilegedNoninteractiveProofStatus
        .REVOKED,
        PrivilegedNoninteractiveProofStatus
        .INVALIDATED,
    ),
)
def test_nonverified_status_is_not_successful(
    status,
) -> None:
    value = proof(
        proof_status=status
    )

    assert (
        value.workload_proof_successful
        is False
    )


def test_proof_is_immutable() -> None:
    value = proof()

    with pytest.raises(
        FrozenInstanceError
    ):
        value.proof_status = (  # type: ignore[misc]
            PrivilegedNoninteractiveProofStatus
            .REVOKED
        )


@pytest.mark.parametrize(
    "field",
    (
        "proof_id",
        "principal_id",
        "proof_reference",
        "credential_or_attestation_reference",
    ),
)
@pytest.mark.parametrize(
    "bad",
    (
        "",
        " ",
        " leading",
        "trailing ",
        None,
        7,
    ),
)
def test_identifiers_fail_closed(
    field,
    bad,
) -> None:
    with pytest.raises(
        PrivilegedNoninteractiveSecurityProofError
    ):
        proof(
            **{
                field: bad,
            }
        )


@pytest.mark.parametrize(
    "value",
    (
        "VERIFIED",
        "REVOKED",
        "INVALIDATED",
        None,
        1,
    ),
)
def test_status_requires_exact_enum(
    value,
) -> None:
    with pytest.raises(
        PrivilegedNoninteractiveSecurityProofError
    ):
        proof(
            proof_status=value
        )


def test_naive_timestamp_rejects() -> None:
    with pytest.raises(
        PrivilegedNoninteractiveSecurityProofError
    ):
        proof(
            observed_at=
                datetime(
                    2026,
                    10,
                    14,
                    6,
                    0,
                    0,
                )
        )


def test_timestamp_canonicalizes_to_utc() -> None:
    source = datetime(
        2026,
        10,
        14,
        8,
        0,
        0,
        123456,
        tzinfo=timezone(
            timedelta(
                hours=2
            )
        ),
    )

    value = proof(
        observed_at=
            source
    )

    assert (
        value.observed_at
        == AT
    )

    assert (
        value.observed_at.tzinfo
        is timezone.utc
    )


def test_no_tenant_or_principal_kind_fields() -> None:
    names = set(
        PrivilegedNoninteractiveSecurityProof
        .__dataclass_fields__
    )

    assert not names.intersection(
        {
            "tenant_id",
            "principal_kind",
            "kind",
            "is_service_account",
            "is_service",
            "human",
            "machine",
            "ai_principal",
        }
    )


def test_caller_asserted_identity_shortcuts_absent() -> None:
    names = set(
        PrivilegedNoninteractiveSecurityProof
        .__dataclass_fields__
    )

    assert not names.intersection(
        {
            "username",
            "role",
            "roles",
            "is_service_account",
            "service_account",
            "machine_identity",
            "workload_identity",
        }
    )


def test_secret_and_bearer_material_absent() -> None:
    names = set(
        PrivilegedNoninteractiveSecurityProof
        .__dataclass_fields__
    )

    assert not names.intersection(
        {
            "api_key",
            "private_key",
            "client_secret",
            "workload_credential",
            "certificate",
            "jwt",
            "access_token",
            "bearer_token",
            "password",
            "password_hash",
            "mfa_secret",
            "otp",
            "refresh_token",
        }
    )


def test_domain_owns_no_persistence_or_authority() -> None:
    import tools.eos.auth.privileged_noninteractive_security_proof as module

    source = inspect.getsource(
        module
    ).casefold()

    for forbidden in (
        "pymongo",
        "fastapi",
        "mongoclient",
        "insert_one(",
        "update_one(",
        "delete_one(",
        "create_index(",
        "start_transaction(",
        "commit_transaction(",
        "abort_transaction(",
        "role_assignment_repository",
        "privileged_activation_registry",
        "financial_execution_repository",
        "evaluate_privileged_security_assurance(",
    ):
        assert forbidden not in source


def test_domain_does_not_verify_workload_credentials() -> None:
    import tools.eos.auth.privileged_noninteractive_security_proof as module

    source = inspect.getsource(
        module
    )

    for forbidden in (
        "verify_api_key",
        "verify_private_key",
        "verify_client_secret",
        "verify_certificate",
        "validate_certificate",
        "verify_jwt",
        "validate_jwt",
        "get_service_account",
        "get_workload_identity",
    ):
        assert forbidden not in source
