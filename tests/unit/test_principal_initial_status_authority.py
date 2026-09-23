"""R1D-B0F-B4-R6A direct principal initial-status authority certificate.

TITLE: Principal Initial Status Authority Certificate
VERSION: v1.0.0-R1D-B0F-B4-R6A
AUTHORITY: Deterministic unit evidence for deployment-rooted activation proof.
EPITOME: Proves exact subject/status binding and every fail-closed parser gate.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tests/unit/test_principal_initial_status_authority.py
COLLABORATION / OWNERSHIP: Exercises the authority seam consumed by provisioning.
CERTIFICATION / UPDATE DATE: 2026-09-17
CHANGELOG: v1.0.0-R1D-B0F-B4-R6A adds direct exact, malformed, wildcard,
           duplicate, subject, status, and immutable-evidence certificates.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2.
SECURITY / PRIVACY POSTURE: Synthetic opaque identifiers only; no network or secrets.
TENANT BOUNDARY: No tenant or membership authority is represented.
AUTHORITY BOUNDARY: Test-only proof; evidence construction never persists authority.
FINANCIAL AUTHORITY BOUNDARY: None; Kennel EOS remains exclusive.
"""
from __future__ import annotations

import pytest

from tools.eos.auth.principal_initial_status_authority import (
    AUTHORITY_SOURCE_ID,
    PRINCIPAL_INITIAL_STATUS_AUTHORITY_CONFIG,
    PRINCIPAL_INITIAL_STATUS_OPERATION,
    PrincipalInitialStatusAuthorityDenialCode,
    PrincipalInitialStatusAuthorityError,
    verify_principal_initial_status_authority,
)
from tools.eos.auth.principal_status import PrincipalStatus


PRINCIPAL = "695e423c9d355c0675c6835d"


def _env(value: str) -> dict[str, str]:
    return {PRINCIPAL_INITIAL_STATUS_AUTHORITY_CONFIG: value}


def test_exact_subject_and_active_status_return_immutable_evidence() -> None:
    evidence = verify_principal_initial_status_authority(
        principal_id=PRINCIPAL,
        target_status=PrincipalStatus.ACTIVE,
        environ=_env('{"principal_id":"695e423c9d355c0675c6835d","initial_status":"ACTIVE"}'),
    )
    assert evidence.subject_principal_id == PRINCIPAL
    assert evidence.target_status is PrincipalStatus.ACTIVE
    assert evidence.operation == PRINCIPAL_INITIAL_STATUS_OPERATION
    assert evidence.authority_source == AUTHORITY_SOURCE_ID
    with pytest.raises(AttributeError):
        evidence.target_status = PrincipalStatus.SUSPENDED  # type: ignore[misc]


@pytest.mark.parametrize(
    "value,code",
    [
        ("[]", PrincipalInitialStatusAuthorityDenialCode.MALFORMED_AUTHORITY),
        ("not-json", PrincipalInitialStatusAuthorityDenialCode.MALFORMED_AUTHORITY),
        ('{"principal_id":"*","initial_status":"ACTIVE"}', PrincipalInitialStatusAuthorityDenialCode.WILDCARD_NOT_ALLOWED),
        ('{"principal_id":"other","initial_status":"ACTIVE"}', PrincipalInitialStatusAuthorityDenialCode.SUBJECT_NOT_AUTHORIZED),
        ('{"principal_id":"695e423c9d355c0675c6835d","initial_status":"SUSPENDED"}', PrincipalInitialStatusAuthorityDenialCode.STATUS_NOT_AUTHORIZED),
        ('[{"principal_id":"695e423c9d355c0675c6835d","initial_status":"ACTIVE"},{"principal_id":"695e423c9d355c0675c6835d","initial_status":"SUSPENDED"}]', PrincipalInitialStatusAuthorityDenialCode.DUPLICATE_DECISION),
    ],
)
def test_configuration_denials_are_fail_closed(value: str, code: PrincipalInitialStatusAuthorityDenialCode) -> None:
    with pytest.raises(PrincipalInitialStatusAuthorityError) as error:
        verify_principal_initial_status_authority(
            principal_id=PRINCIPAL,
            target_status=PrincipalStatus.ACTIVE,
            environ=_env(value),
        )
    assert error.value.code is code


def test_missing_configuration_is_denied() -> None:
    with pytest.raises(PrincipalInitialStatusAuthorityError) as error:
        verify_principal_initial_status_authority(
            principal_id=PRINCIPAL,
            target_status=PrincipalStatus.ACTIVE,
            environ={},
        )
    assert error.value.code is PrincipalInitialStatusAuthorityDenialCode.MISSING_AUTHORITY


# ARTIFACT: test_principal_initial_status_authority.py
# VERSION: v1.0.0-R1D-B0F-B4-R6A
# AUTHORITY BOUNDARY: deterministic authority-parser evidence only
# TENANT POSTURE: tenant-neutral synthetic identities
# FAIL-CLOSED POSTURE: malformed, wildcard, duplicate, absent, and mismatched config denies
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS remains exclusive
# END OF WILSY OS SOVEREIGN ARTIFACT
