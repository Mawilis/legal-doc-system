"""
Direct certificate for P3 immutable security-assurance evidence.

VERSION:
v1.0.0-P3-R2-A1-PRIVILEGED-SECURITY-ASSURANCE-EVIDENCE-CERT
"""

from dataclasses import (
    FrozenInstanceError,
)
from datetime import (
    datetime,
    timezone,
)
import inspect

import pytest

from tools.eos.auth.privileged_security_assurance import (
    PrivilegedAssuranceChannel,
    PrivilegedAssurancePurpose,
    PrivilegedAssuranceReason,
    evaluate_privileged_security_assurance,
)
from tools.eos.auth.privileged_security_assurance_evidence import (
    PrivilegedSecurityAssuranceEvidence,
    PrivilegedSecurityAssuranceEvidenceError,
)


AT = datetime(
    2026,
    10,
    14,
    1,
    45,
    0,
    123456,
    tzinfo=timezone.utc,
)

CHANNEL_I = (
    PrivilegedAssuranceChannel
    .INTERACTIVE_STRONG_AUTH
)

CHANNEL_W = (
    PrivilegedAssuranceChannel
    .NONINTERACTIVE_WORKLOAD_PROOF
)

PURPOSE = (
    PrivilegedAssurancePurpose
    .PRIVILEGED_ELIGIBILITY_TO_ACTIVATION
)


def interactive_decision(
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
            PURPOSE,
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
        values,
        evaluate_privileged_security_assurance(
            **values
        ),
    )


def workload_decision(
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
            PURPOSE,
        "workload_proof_current":
            True,
        "workload_proof_reference":
            "proof:workload:001",
    }

    values.update(
        overrides
    )

    return (
        values,
        evaluate_privileged_security_assurance(
            **values
        ),
    )


def evidence_from(
    values,
    decision,
    *,
    evidence_id: str = "assurance-evidence-001",
    idempotency_key: str = "idem-assurance-001",
):
    return (
        PrivilegedSecurityAssuranceEvidence
        .from_decision(
            assurance_evidence_id=
                evidence_id,
            decision=
                decision,
            principal_current=
                values[
                    "principal_current"
                ],
            credential_current=
                values[
                    "credential_current"
                ],
            assurance_proof_current=
                values[
                    "assurance_proof_current"
                ],
            session_current=
                values.get(
                    "session_current"
                ),
            factor_verification_current=
                values.get(
                    "factor_verification_current"
                ),
            authentication_recency_current=
                values.get(
                    "authentication_recency_current"
                ),
            workload_proof_current=
                values.get(
                    "workload_proof_current"
                ),
            workload_proof_reference=
                values.get(
                    "workload_proof_reference"
                ),
            evaluated_at=
                AT,
            idempotency_key=
                idempotency_key,
        )
    )


def test_interactive_evidence_records_exact_decision_and_inputs() -> None:
    values, decision = (
        interactive_decision()
    )

    evidence = evidence_from(
        values,
        decision,
    )

    assert (
        evidence.principal_id
        == decision.principal_id
    )

    assert (
        evidence.assurance_channel
        is CHANNEL_I
    )

    assert (
        evidence.assurance_purpose
        is PURPOSE
    )

    assert evidence.sufficient is True

    assert (
        evidence.reason
        is PrivilegedAssuranceReason
        .SUFFICIENT
    )

    assert evidence.session_current is True
    assert (
        evidence.factor_verification_current
        is True
    )
    assert (
        evidence.authentication_recency_current
        is True
    )

    assert (
        evidence.workload_proof_current
        is None
    )

    assert (
        evidence.workload_proof_reference
        is None
    )


def test_workload_evidence_records_exact_decision_and_inputs() -> None:
    values, decision = (
        workload_decision()
    )

    evidence = evidence_from(
        values,
        decision,
    )

    assert (
        evidence.assurance_channel
        is CHANNEL_W
    )

    assert (
        evidence.workload_proof_current
        is True
    )

    assert (
        evidence.workload_proof_reference
        == "proof:workload:001"
    )

    assert evidence.session_current is None
    assert (
        evidence.factor_verification_current
        is None
    )
    assert (
        evidence.authentication_recency_current
        is None
    )


def test_insufficient_result_is_lawful_evidence() -> None:
    values, decision = (
        interactive_decision(
            authentication_recency_current=
                False
        )
    )

    evidence = evidence_from(
        values,
        decision,
    )

    assert evidence.sufficient is False

    assert (
        evidence.reason
        is PrivilegedAssuranceReason
        .AUTHENTICATION_NOT_RECENT
    )


def test_evidence_does_not_re_evaluate_p3() -> None:
    import tools.eos.auth.privileged_security_assurance_evidence as module

    source = inspect.getsource(
        module
    )

    assert (
        "evaluate_privileged_security_assurance"
        not in source
    )


def test_evidence_is_immutable() -> None:
    values, decision = (
        interactive_decision()
    )

    evidence = evidence_from(
        values,
        decision,
    )

    with pytest.raises(
        FrozenInstanceError
    ):
        evidence.sufficient = False  # type: ignore[misc]


def test_exact_persisted_shape_and_null_channel_fields() -> None:
    values, decision = (
        interactive_decision()
    )

    evidence = evidence_from(
        values,
        decision,
    )

    persisted = (
        evidence.to_persisted()
    )

    assert set(
        persisted
    ) == {
        "schema",
        "assurance_evidence_id",
        "principal_id",
        "assurance_channel",
        "assurance_purpose",
        "principal_current",
        "credential_current",
        "assurance_proof_current",
        "session_current",
        "factor_verification_current",
        "authentication_recency_current",
        "workload_proof_current",
        "workload_proof_reference",
        "sufficient",
        "reason",
        "evaluated_at",
        "idempotency_key",
        "assurance_evidence_fingerprint",
    }

    assert (
        persisted[
            "workload_proof_current"
        ]
        is None
    )

    assert (
        persisted[
            "workload_proof_reference"
        ]
        is None
    )


def test_fingerprint_is_deterministic_sha3_512() -> None:
    values, decision = (
        interactive_decision()
    )

    first = evidence_from(
        values,
        decision,
    )

    second = evidence_from(
        values,
        decision,
    )

    assert (
        first.assurance_evidence_fingerprint
        == second.assurance_evidence_fingerprint
    )

    assert (
        len(
            first.assurance_evidence_fingerprint
        )
        == 128
    )

    assert (
        first.assurance_evidence_fingerprint
        == first.assurance_evidence_fingerprint.lower()
    )


def test_exact_hydration_round_trip() -> None:
    values, decision = (
        workload_decision()
    )

    evidence = evidence_from(
        values,
        decision,
    )

    assert (
        PrivilegedSecurityAssuranceEvidence
        .from_persisted(
            evidence.to_persisted()
        )
        == evidence
    )


def test_corrupt_fingerprint_rejects() -> None:
    values, decision = (
        interactive_decision()
    )

    persisted = evidence_from(
        values,
        decision,
    ).to_persisted()

    persisted[
        "assurance_evidence_fingerprint"
    ] = "f" * 128

    with pytest.raises(
        PrivilegedSecurityAssuranceEvidenceError
    ):
        (
            PrivilegedSecurityAssuranceEvidence
            .from_persisted(
                persisted
            )
        )


def test_unknown_persisted_field_rejects() -> None:
    values, decision = (
        interactive_decision()
    )

    persisted = evidence_from(
        values,
        decision,
    ).to_persisted()

    persisted["extra"] = "forbidden"

    with pytest.raises(
        PrivilegedSecurityAssuranceEvidenceError
    ):
        (
            PrivilegedSecurityAssuranceEvidence
            .from_persisted(
                persisted
            )
        )


def test_noncanonical_time_rejects() -> None:
    values, decision = (
        interactive_decision()
    )

    persisted = evidence_from(
        values,
        decision,
    ).to_persisted()

    persisted["evaluated_at"] = (
        "2026-10-14T03:45:00.123456+02:00"
    )

    with pytest.raises(
        PrivilegedSecurityAssuranceEvidenceError
    ):
        (
            PrivilegedSecurityAssuranceEvidence
            .from_persisted(
                persisted
            )
        )


@pytest.mark.parametrize(
    "field",
    (
        "principal_current",
        "credential_current",
        "assurance_proof_current",
        "session_current",
        "factor_verification_current",
        "authentication_recency_current",
    ),
)
def test_interactive_boolean_fields_reject_non_bool(
    field,
) -> None:
    values, decision = (
        interactive_decision()
    )

    kwargs = {
        "assurance_evidence_id":
            "assurance-evidence-001",
        "decision":
            decision,
        "principal_current":
            values[
                "principal_current"
            ],
        "credential_current":
            values[
                "credential_current"
            ],
        "assurance_proof_current":
            values[
                "assurance_proof_current"
            ],
        "session_current":
            values[
                "session_current"
            ],
        "factor_verification_current":
            values[
                "factor_verification_current"
            ],
        "authentication_recency_current":
            values[
                "authentication_recency_current"
            ],
        "workload_proof_current":
            None,
        "workload_proof_reference":
            None,
        "evaluated_at":
            AT,
        "idempotency_key":
            "idem-assurance-001",
    }

    kwargs[field] = 1

    with pytest.raises(
        PrivilegedSecurityAssuranceEvidenceError
    ):
        (
            PrivilegedSecurityAssuranceEvidence
            .from_decision(
                **kwargs
            )
        )


def test_interactive_rejects_workload_fields() -> None:
    values, decision = (
        interactive_decision()
    )

    with pytest.raises(
        PrivilegedSecurityAssuranceEvidenceError
    ):
        (
            PrivilegedSecurityAssuranceEvidence
            .from_decision(
                assurance_evidence_id=
                    "assurance-evidence-001",
                decision=
                    decision,
                principal_current=True,
                credential_current=True,
                assurance_proof_current=True,
                session_current=True,
                factor_verification_current=True,
                authentication_recency_current=True,
                workload_proof_current=True,
                workload_proof_reference=
                    "forbidden",
                evaluated_at=AT,
                idempotency_key=
                    "idem-assurance-001",
            )
        )


def test_workload_rejects_interactive_fields() -> None:
    values, decision = (
        workload_decision()
    )

    with pytest.raises(
        PrivilegedSecurityAssuranceEvidenceError
    ):
        (
            PrivilegedSecurityAssuranceEvidence
            .from_decision(
                assurance_evidence_id=
                    "assurance-evidence-001",
                decision=
                    decision,
                principal_current=True,
                credential_current=True,
                assurance_proof_current=True,
                session_current=True,
                factor_verification_current=None,
                authentication_recency_current=None,
                workload_proof_current=True,
                workload_proof_reference=
                    "proof:workload:001",
                evaluated_at=AT,
                idempotency_key=
                    "idem-assurance-001",
            )
        )


def test_no_tenant_field_exists() -> None:
    assert (
        "tenant_id"
        not in (
            PrivilegedSecurityAssuranceEvidence
            .__dataclass_fields__
        )
    )


def test_no_sequence_expiry_or_provenance_invention() -> None:
    names = set(
        PrivilegedSecurityAssuranceEvidence
        .__dataclass_fields__
    )

    assert not names.intersection(
        {
            "sequence_number",
            "previous_fingerprint",
            "supersedes_fingerprint",
            "expires_at",
            "expiry",
            "proof_fingerprint",
            "source_revision",
        }
    )


def test_secret_and_bearer_fields_absent() -> None:
    names = set(
        PrivilegedSecurityAssuranceEvidence
        .__dataclass_fields__
    )

    assert not names.intersection(
        {
            "password",
            "password_hash",
            "mfa_registered",
            "mfa_secret",
            "totp_secret",
            "otp",
            "session_token",
            "refresh_token",
            "jwt",
            "api_key",
            "private_key",
            "workload_credential",
        }
    )


def test_domain_owns_no_persistence_or_activation() -> None:
    import tools.eos.auth.privileged_security_assurance_evidence as module

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
