"""
Direct certificate for P3 pure privileged security-assurance domain.

VERSION:
v1.0.0-P3-R1-PRIVILEGED-SECURITY-ASSURANCE-CERT
"""

from dataclasses import (
    FrozenInstanceError,
)
import inspect

import pytest

from tools.eos.auth.privileged_security_assurance import (
    PrivilegedAssuranceChannel,
    PrivilegedAssurancePurpose,
    PrivilegedAssuranceReason,
    PrivilegedSecurityAssuranceDecision,
    evaluate_privileged_security_assurance,
)


CHANNEL_I = (
    PrivilegedAssuranceChannel
    .INTERACTIVE_STRONG_AUTH
)

CHANNEL_W = (
    PrivilegedAssuranceChannel
    .NONINTERACTIVE_WORKLOAD_PROOF
)

PURPOSE_A = (
    PrivilegedAssurancePurpose
    .PRIVILEGED_ELIGIBILITY_TO_ACTIVATION
)

PURPOSE_U = (
    PrivilegedAssurancePurpose
    .PRIVILEGED_ACTIVATION_USE
)


def interactive(
    **overrides,
):
    values = {
        "principal_id":
            "principal-a",
        "principal_current":
            True,
        "credential_current":
            True,
        "assurance_channel":
            CHANNEL_I,
        "assurance_proof_current":
            True,
        "assurance_purpose":
            PURPOSE_A,
        "session_current":
            True,
        "factor_verification_current":
            True,
        "authentication_recency_current":
            True,
    }

    values.update(
        overrides
    )

    return (
        evaluate_privileged_security_assurance(
            **values
        )
    )


def workload(
    **overrides,
):
    values = {
        "principal_id":
            "principal-machine",
        "principal_current":
            True,
        "credential_current":
            True,
        "assurance_channel":
            CHANNEL_W,
        "assurance_proof_current":
            True,
        "assurance_purpose":
            PURPOSE_A,
        "workload_proof_current":
            True,
        "workload_proof_reference":
            "workload-proof:001",
    }

    values.update(
        overrides
    )

    return (
        evaluate_privileged_security_assurance(
            **values
        )
    )


def test_interactive_complete_current_proof_is_sufficient() -> None:
    decision = interactive()

    assert (
        decision.sufficient
        is True
    )

    assert (
        decision.reason
        is PrivilegedAssuranceReason
        .SUFFICIENT
    )


def test_noninteractive_complete_current_proof_is_sufficient() -> None:
    decision = workload()

    assert (
        decision.sufficient
        is True
    )

    assert (
        decision.reason
        is PrivilegedAssuranceReason
        .SUFFICIENT
    )


@pytest.mark.parametrize(
    (
        "field",
        "reason",
    ),
    (
        (
            "principal_current",
            PrivilegedAssuranceReason
            .PRINCIPAL_NOT_CURRENT,
        ),
        (
            "credential_current",
            PrivilegedAssuranceReason
            .CREDENTIAL_NOT_CURRENT,
        ),
        (
            "assurance_proof_current",
            PrivilegedAssuranceReason
            .ASSURANCE_PROOF_NOT_CURRENT,
        ),
        (
            "session_current",
            PrivilegedAssuranceReason
            .SESSION_NOT_CURRENT,
        ),
        (
            "factor_verification_current",
            PrivilegedAssuranceReason
            .FACTOR_VERIFICATION_NOT_CURRENT,
        ),
        (
            "authentication_recency_current",
            PrivilegedAssuranceReason
            .AUTHENTICATION_NOT_RECENT,
        ),
    ),
)
def test_interactive_currentness_fails_closed(
    field,
    reason,
) -> None:
    decision = interactive(
        **{
            field: False,
        }
    )

    assert (
        decision.sufficient
        is False
    )

    assert (
        decision.reason
        is reason
    )


@pytest.mark.parametrize(
    (
        "field",
        "reason",
    ),
    (
        (
            "principal_current",
            PrivilegedAssuranceReason
            .PRINCIPAL_NOT_CURRENT,
        ),
        (
            "credential_current",
            PrivilegedAssuranceReason
            .CREDENTIAL_NOT_CURRENT,
        ),
        (
            "assurance_proof_current",
            PrivilegedAssuranceReason
            .ASSURANCE_PROOF_NOT_CURRENT,
        ),
        (
            "workload_proof_current",
            PrivilegedAssuranceReason
            .WORKLOAD_PROOF_NOT_CURRENT,
        ),
    ),
)
def test_workload_currentness_fails_closed(
    field,
    reason,
) -> None:
    decision = workload(
        **{
            field: False,
        }
    )

    assert (
        decision.sufficient
        is False
    )

    assert (
        decision.reason
        is reason
    )


@pytest.mark.parametrize(
    "field",
    (
        "session_current",
        "factor_verification_current",
        "authentication_recency_current",
    ),
)
def test_interactive_missing_required_channel_input_denies(
    field,
) -> None:
    decision = interactive(
        **{
            field: None,
        }
    )

    assert (
        decision.sufficient
        is False
    )

    assert (
        decision.reason
        is PrivilegedAssuranceReason
        .CHANNEL_INPUT_MISMATCH
    )


def test_interactive_rejects_workload_material() -> None:
    decision = interactive(
        workload_proof_current=True,
        workload_proof_reference=
            "workload-proof:forbidden",
    )

    assert (
        decision.sufficient
        is False
    )

    assert (
        decision.reason
        is PrivilegedAssuranceReason
        .CHANNEL_INPUT_MISMATCH
    )


def test_workload_rejects_interactive_material() -> None:
    decision = workload(
        session_current=True,
    )

    assert (
        decision.sufficient
        is False
    )

    assert (
        decision.reason
        is PrivilegedAssuranceReason
        .CHANNEL_INPUT_MISMATCH
    )


@pytest.mark.parametrize(
    "overrides",
    (
        {
            "workload_proof_current":
                None,
        },
        {
            "workload_proof_reference":
                None,
        },
        {
            "workload_proof_reference":
                "",
        },
        {
            "workload_proof_reference":
                " bad ",
        },
    ),
)
def test_workload_missing_or_malformed_channel_material_denies(
    overrides,
) -> None:
    decision = workload(
        **overrides
    )

    assert (
        decision.sufficient
        is False
    )

    assert (
        decision.reason
        is PrivilegedAssuranceReason
        .CHANNEL_INPUT_MISMATCH
    )


def test_assurance_purpose_is_exactly_preserved() -> None:
    decision = interactive(
        assurance_purpose=
            PURPOSE_U,
    )

    assert (
        decision.assurance_purpose
        is PURPOSE_U
    )


def test_decision_is_immutable() -> None:
    decision = interactive()

    with pytest.raises(
        FrozenInstanceError
    ):
        decision.sufficient = False  # type: ignore[misc]


@pytest.mark.parametrize(
    "principal_id",
    (
        "",
        " ",
        " principal-a",
        "principal-a ",
        None,
        7,
    ),
)
def test_malformed_principal_rejects(
    principal_id,
) -> None:
    with pytest.raises(
        (
            ValueError,
            TypeError,
        )
    ):
        interactive(
            principal_id=
                principal_id
        )


@pytest.mark.parametrize(
    "field",
    (
        "principal_current",
        "credential_current",
        "assurance_proof_current",
    ),
)
def test_common_currentness_requires_actual_bool(
    field,
) -> None:
    with pytest.raises(
        TypeError
    ):
        interactive(
            **{
                field: 1,
            }
        )


def test_unknown_channel_rejects() -> None:
    with pytest.raises(
        TypeError
    ):
        interactive(
            assurance_channel=
                "INTERACTIVE_STRONG_AUTH"
        )


def test_unknown_purpose_rejects() -> None:
    with pytest.raises(
        TypeError
    ):
        interactive(
            assurance_purpose=
                "PRIVILEGED_ACTIVATION_USE"
        )


def test_decision_reason_consistency_is_enforced() -> None:
    with pytest.raises(
        ValueError
    ):
        PrivilegedSecurityAssuranceDecision(
            principal_id=
                "principal-a",
            assurance_channel=
                CHANNEL_I,
            assurance_purpose=
                PURPOSE_A,
            sufficient=True,
            reason=(
                PrivilegedAssuranceReason
                .SESSION_NOT_CURRENT
            ),
        )


def test_no_principal_kind_or_human_only_surface() -> None:
    names = set(
        PrivilegedSecurityAssuranceDecision
        .__dataclass_fields__
    )

    assert not names.intersection(
        {
            "principal_kind",
            "kind",
            "is_service_account",
            "human",
            "machine",
            "ai_principal",
        }
    )


def test_decision_surface_is_exact() -> None:
    assert set(
        PrivilegedSecurityAssuranceDecision
        .__dataclass_fields__
    ) == {
        "principal_id",
        "assurance_channel",
        "assurance_purpose",
        "sufficient",
        "reason",
    }


def test_domain_contains_no_mfa_registration_authority() -> None:
    import tools.eos.auth.privileged_security_assurance as module

    source = inspect.getsource(
        module
    )

    assert (
        "mfaRegistered"
        not in source
    )

    assert (
        "mfa_registered"
        not in source
    )


def test_domain_owns_no_persistence_activation_or_finance() -> None:
    import tools.eos.auth.privileged_security_assurance as module

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
        "privileged_activation_registry",
        "role_assignment_repository",
        "refresh_token_registry",
        "financial_execution_repository",
    ):
        assert (
            forbidden
            not in source
        )


def test_domain_does_not_mutate_p2_contract() -> None:
    import tools.eos.auth.privileged_eligibility as p2

    p2_source = inspect.getsource(
        p2
    )

    for forbidden in (
        "security_assurance",
        "mfa_registered",
        "session_current",
        "factor_verification_current",
        "authentication_recency_current",
        "workload_proof_current",
    ):
        assert (
            forbidden
            not in p2_source
        )
