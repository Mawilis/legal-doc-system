"""
TITLE:
    WILSY OS System Permission Bootstrap Authority Direct Certificate
"""

from __future__ import annotations

from dataclasses import FrozenInstanceError
from datetime import datetime, timedelta, timezone

import pytest

from tools.eos.auth.system_permission_bootstrap_authority import (
    SystemPermissionBootstrapAuthority,
    SystemPermissionBootstrapAuthorityError,
    SystemPermissionBootstrapAuthorityStatus,
)


NOW = datetime(
    2026,
    10,
    14,
    19,
    0,
    tzinfo=timezone.utc,
)

ASSIGNMENT_PURPOSE = (
    "SEED_SYSTEM_PERMISSION_ASSIGNMENT_COMMAND_AUTHORITY"
)

REVOCATION_PURPOSE = (
    "SEED_SYSTEM_PERMISSION_REVOCATION_COMMAND_AUTHORITY"
)


def authority(
    *,
    purpose: str = ASSIGNMENT_PURPOSE,
) -> SystemPermissionBootstrapAuthority:
    return SystemPermissionBootstrapAuthority.issue(
        bootstrap_id="bootstrap-a",
        actor_principal_id="principal-a",
        purpose=purpose,
        evidence_reference="installation-root-evidence-a",
        issued_at=NOW,
    )


def test_issue_exact_active_authority() -> None:
    value = authority()

    assert value.bootstrap_id == "bootstrap-a"
    assert value.actor_principal_id == "principal-a"
    assert value.purpose == ASSIGNMENT_PURPOSE
    assert value.status is SystemPermissionBootstrapAuthorityStatus.ACTIVE
    assert value.revision == 1
    assert value.previous_fingerprint is None
    assert value.retired_at is None
    assert value.retirement_evidence_reference is None
    assert len(value.authority_fingerprint) == 128


@pytest.mark.parametrize(
    "purpose",
    (
        ASSIGNMENT_PURPOSE,
        REVOCATION_PURPOSE,
    ),
)
def test_closed_bootstrap_purposes_allow(
    purpose: str,
) -> None:
    assert authority(
        purpose=purpose,
    ).purpose == purpose


@pytest.mark.parametrize(
    "purpose",
    (
        "",
        "privileged_activation:issue",
        "kernel:write",
        "governance:evaluate",
        "tenant:profile:write",
        "system_permission_assignment:*",
        "ARBITRARY_SYSTEM_PERMISSION",
    ),
)
def test_arbitrary_bootstrap_purpose_rejected(
    purpose: str,
) -> None:
    with pytest.raises(
        SystemPermissionBootstrapAuthorityError,
        match="BOOTSTRAP_PURPOSE_NOT_ALLOWED|PURPOSE_INVALID",
    ):
        authority(
            purpose=purpose,
        )


@pytest.mark.parametrize(
    "field,value",
    (
        ("bootstrap_id", ""),
        ("bootstrap_id", "*"),
        ("actor_principal_id", ""),
        ("actor_principal_id", "*"),
        ("actor_principal_id", "principal-a "),
        ("evidence_reference", ""),
    ),
)
def test_identifier_material_fails_closed(
    field: str,
    value: str,
) -> None:
    kwargs = {
        "bootstrap_id": "bootstrap-a",
        "actor_principal_id": "principal-a",
        "purpose": ASSIGNMENT_PURPOSE,
        "evidence_reference": "evidence-a",
        "issued_at": NOW,
    }

    kwargs[field] = value

    with pytest.raises(
        SystemPermissionBootstrapAuthorityError
    ):
        SystemPermissionBootstrapAuthority.issue(
            **kwargs,
        )


def test_naive_issued_at_rejected() -> None:
    with pytest.raises(
        SystemPermissionBootstrapAuthorityError,
        match="ISSUED_AT_INVALID",
    ):
        SystemPermissionBootstrapAuthority.issue(
            bootstrap_id="bootstrap-a",
            actor_principal_id="principal-a",
            purpose=ASSIGNMENT_PURPOSE,
            evidence_reference="evidence-a",
            issued_at=datetime(
                2026,
                10,
                14,
                19,
                0,
            ),
        )


def test_retirement_is_terminal_chained_revision() -> None:
    active = authority()

    retired = active.retire(
        retired_at=(
            NOW
            + timedelta(minutes=1)
        ),
        retirement_evidence_reference="retire-evidence-a",
    )

    assert retired.status is SystemPermissionBootstrapAuthorityStatus.RETIRED
    assert retired.revision == 2
    assert (
        retired.previous_fingerprint
        == active.authority_fingerprint
    )
    assert retired.bootstrap_id == active.bootstrap_id
    assert retired.actor_principal_id == active.actor_principal_id
    assert retired.purpose == active.purpose

    with pytest.raises(
        SystemPermissionBootstrapAuthorityError,
        match="BOOTSTRAP_AUTHORITY_TERMINAL",
    ):
        retired.retire(
            retired_at=(
                NOW
                + timedelta(minutes=2)
            ),
            retirement_evidence_reference="retire-again",
        )


def test_backdated_retirement_rejected() -> None:
    with pytest.raises(
        SystemPermissionBootstrapAuthorityError,
        match="RETIREMENT_BEFORE_ISSUANCE",
    ):
        authority().retire(
            retired_at=(
                NOW
                - timedelta(seconds=1)
            ),
            retirement_evidence_reference="evidence-r",
        )


def test_immutable() -> None:
    value = authority()

    with pytest.raises(
        FrozenInstanceError
    ):
        value.purpose = REVOCATION_PURPOSE  # type: ignore[misc]


def test_fingerprint_covers_authority_material() -> None:
    first = authority(
        purpose=ASSIGNMENT_PURPOSE,
    )

    second = authority(
        purpose=REVOCATION_PURPOSE,
    )

    assert (
        first.authority_fingerprint
        != second.authority_fingerprint
    )


def test_serialization_has_no_tenant_role_or_privilege_surface() -> None:
    payload = authority().to_dict()

    forbidden = (
        "tenant_id",
        "business_role",
        "role_id",
        "authorization_role",
        "privileged_activation",
        "break_glass",
        "financial_authority",
        "permission_id",
    )

    assert all(
        key not in payload
        for key in forbidden
    )


def test_no_normal_authorization_api_surface() -> None:
    value = authority()

    for name in (
        "authorize",
        "allows",
        "grant",
        "assign",
        "activate",
        "issue_privileged_activation",
        "execute",
        "break_glass",
    ):
        assert not hasattr(
            value,
            name,
        )


def test_source_has_no_io_clock_random_or_shortcuts() -> None:
    source = (
        __import__(
            "inspect"
        )
        .getsource(
            __import__(
                "tools.eos.auth.system_permission_bootstrap_authority",
                fromlist=["*"],
            )
        )
    )

    forbidden = (
        "pymongo",
        "MongoClient",
        "insert_one",
        "update_one",
        "delete_one",
        "datetime.now",
        "uuid4",
        "random",
        "ENTERPRISE_ADMIN",
        "SOVEREIGN_ARCHITECT",
        "SUPER_ADMIN",
        "GLOBAL_ROOT",
        "admin:all",
        "tenant:manage",
    )

    assert all(
        token not in source
        for token in forbidden
    )


# =============================================================================
# WILSY OS TEST ARTIFACT SEAL
# ARTIFACT: tests/unit/test_system_permission_bootstrap_authority.py
# PURE DOMAIN: YES
# BOOTSTRAP PURPOSE VOCABULARY: CLOSED
# ACTIVE -> RETIRED ONLY: YES
# TENANT AUTHORITY: NONE
# ROLE AUTHORITY: NONE
# PRIVILEGED ACTIVATION AUTHORITY: NONE
# BREAK-GLASS AUTHORITY: NONE
# FINANCIAL EXECUTION AUTHORITY: NONE
# END OF WILSY OS TEST ARTIFACT
