"""
Direct certificate for P3-R3A interactive current-security-proof pure domain.
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

from tools.eos.auth.privileged_interactive_security_proof import (
    PrivilegedInteractiveProofStatus,
    PrivilegedInteractiveSecurityProof,
    PrivilegedInteractiveSecurityProofError,
)


AT = datetime(
    2026,
    10,
    14,
    4,
    30,
    0,
    123456,
    tzinfo=timezone.utc,
)


def proof(
    **overrides,
) -> PrivilegedInteractiveSecurityProof:
    values = {
        "proof_id":
            "interactive-proof-001",
        "principal_id":
            "principal-001",
        "factor_verification_reference":
            "factor-verification:001",
        "authenticated_at":
            AT,
        "credential_revision":
            7,
        "session_reference":
            "session-reference:001",
        "proof_status":
            PrivilegedInteractiveProofStatus
            .VERIFIED,
        "proof_reference":
            "interactive-security-proof:001",
    }

    values.update(
        overrides
    )

    return (
        PrivilegedInteractiveSecurityProof(
            **values
        )
    )


def test_exact_frozen_field_surface() -> None:
    assert set(
        PrivilegedInteractiveSecurityProof
        .__dataclass_fields__
    ) == {
        "proof_id",
        "principal_id",
        "factor_verification_reference",
        "authenticated_at",
        "credential_revision",
        "session_reference",
        "proof_status",
        "proof_reference",
    }


def test_verified_proof_constructs() -> None:
    value = proof()

    assert (
        value.proof_status
        is PrivilegedInteractiveProofStatus
        .VERIFIED
    )

    assert (
        value.factor_verification_successful
        is True
    )


@pytest.mark.parametrize(
    "status",
    (
        PrivilegedInteractiveProofStatus
        .REVOKED,
        PrivilegedInteractiveProofStatus
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
        value.factor_verification_successful
        is False
    )


def test_proof_is_immutable() -> None:
    value = proof()

    with pytest.raises(
        FrozenInstanceError
    ):
        value.proof_status = (  # type: ignore[misc]
            PrivilegedInteractiveProofStatus
            .REVOKED
        )


@pytest.mark.parametrize(
    "field",
    (
        "proof_id",
        "principal_id",
        "factor_verification_reference",
        "session_reference",
        "proof_reference",
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
        PrivilegedInteractiveSecurityProofError
    ):
        proof(
            **{
                field: bad,
            }
        )


@pytest.mark.parametrize(
    "revision",
    (
        -1,
        True,
        False,
        1.0,
        "1",
        None,
    ),
)
def test_credential_revision_is_strict_nonnegative_integer(
    revision,
) -> None:
    with pytest.raises(
        PrivilegedInteractiveSecurityProofError
    ):
        proof(
            credential_revision=
                revision
        )


def test_zero_credential_revision_is_lawful() -> None:
    assert (
        proof(
            credential_revision=0
        ).credential_revision
        == 0
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
        PrivilegedInteractiveSecurityProofError
    ):
        proof(
            proof_status=
                value
        )


def test_naive_timestamp_rejects() -> None:
    with pytest.raises(
        PrivilegedInteractiveSecurityProofError
    ):
        proof(
            authenticated_at=
                datetime(
                    2026,
                    10,
                    14,
                    4,
                    30,
                    0,
                )
        )


def test_timestamp_canonicalizes_to_utc() -> None:
    source = datetime(
        2026,
        10,
        14,
        6,
        30,
        0,
        123456,
        tzinfo=timezone(
            timedelta(
                hours=2
            )
        ),
    )

    value = proof(
        authenticated_at=
            source
    )

    assert (
        value.authenticated_at
        == AT
    )

    assert (
        value.authenticated_at.tzinfo
        is timezone.utc
    )


def test_no_tenant_or_principal_kind_fields() -> None:
    names = set(
        PrivilegedInteractiveSecurityProof
        .__dataclass_fields__
    )

    assert not names.intersection(
        {
            "tenant_id",
            "principal_kind",
            "kind",
            "is_service_account",
            "human",
            "machine",
            "ai_principal",
        }
    )


def test_no_recency_policy_in_record() -> None:
    names = set(
        PrivilegedInteractiveSecurityProof
        .__dataclass_fields__
    )

    assert not names.intersection(
        {
            "max_age",
            "recency_seconds",
            "recency_window",
            "is_recent",
            "authentication_recency_current",
        }
    )


def test_secret_and_bearer_material_absent() -> None:
    names = set(
        PrivilegedInteractiveSecurityProof
        .__dataclass_fields__
    )

    assert not names.intersection(
        {
            "password",
            "password_hash",
            "mfa_secret",
            "totp_secret",
            "otp",
            "raw_otp",
            "session_token",
            "refresh_token",
            "jwt",
            "api_key",
            "private_key",
            "workload_credential",
        }
    )


def test_domain_owns_no_persistence_or_authority() -> None:
    import tools.eos.auth.privileged_interactive_security_proof as module

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
        assert (
            forbidden
            not in source
        )


def test_domain_does_not_implement_mfa_or_session_lookup() -> None:
    import tools.eos.auth.privileged_interactive_security_proof as module

    source = inspect.getsource(
        module
    )

    for forbidden in (
        "verify_totp",
        "verify_otp",
        "verify_webauthn",
        "verify_passkey",
        "get_session",
        "validate_session",
        "get_credential_revision",
    ):
        assert (
            forbidden
            not in source
        )
