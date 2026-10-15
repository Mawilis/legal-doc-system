"""
WILSY OS P5 Privileged Activation Current-Use Real-Mongo Certificate.

Certifies the P5 current-use authority against the same sealed real-Mongo
substrate used by P4 activation issuance.

This certificate proves:
- an already-persisted current P4 platform activation can be used;
- activation tenant scope remains None while interactive proof tenant remains
  independently concrete;
- P2 is reread from the activation's exact eligibility evidence lineage;
- P3 is freshly composed for PRIVILEGED_ACTIVATION_USE;
- caller-owned Mongo transactions are propagated through P4/P2/P3;
- abort rolls back fresh use-time P3 evidence;
- expired P4 activation fails before fresh P3;
- revoked current P2 principal authority fails before fresh P3;
- P5 creates no independent persistence collection, TTL, permission,
  break-glass, HTTP, payment, subscription, or financial authority.
"""

from __future__ import annotations

from datetime import timedelta
from pathlib import Path
from typing import Any

import pytest

from tests.integration.test_privileged_activation_issuance_service_real_mongo import (
    NOW,
    PRINCIPAL,
    PROOF_REFERENCE,
    PROOF_TENANT,
    _issue,
    _seed,
    context,
)
from tools.eos.auth.principal_authority import (
    PrincipalAuthority,
)
from tools.eos.auth.principal_authority_repository import (
    PrincipalAuthorityRepository,
)
from tools.eos.auth.principal_status import (
    PrincipalStatus,
)
from tools.eos.auth.privileged_activation_use_authority import (
    PrivilegedActivationUseAuthority,
    PrivilegedActivationUseError,
)
from tools.eos.auth.privileged_eligibility import (
    SOVEREIGN_ARCHITECT,
)
from tools.eos.auth.privileged_security_assurance import (
    PrivilegedAssurancePurpose,
)


def _authority(
    value: dict[str, Any],
) -> PrivilegedActivationUseAuthority:
    issuance = value[
        "issuance_service"
    ]

    eligibility_resolver = getattr(
        issuance,
        "_eligibility_resolver",
    )

    interactive_assurance_service = getattr(
        issuance,
        "_interactive_assurance_service",
    )

    return PrivilegedActivationUseAuthority(
        activation_registry=
            value[
                "activation_registry"
            ],
        eligibility_resolver=
            eligibility_resolver,
        interactive_assurance_service=
            interactive_assurance_service,
    )


def _seed_and_issue(
    value: dict[str, Any],
    *,
    key: str,
):
    _seed(
        value
    )

    with value[
        "client"
    ].start_session() as session:
        session.start_transaction()

        activation = _issue(
            value,
            key=key,
            session=session,
        )

        session.commit_transaction()

    return activation


def _authorize_platform_interactive(
    value: dict[str, Any],
    *,
    activation: Any,
    key: str,
    at: Any,
    session: Any,
):
    return _authority(
        value
    ).authorize_interactive(
        activation_tenant_id=None,
        proof_tenant_id=
            PROOF_TENANT,
        principal_id=
            PRINCIPAL,
        privileged_role_id=
            SOVEREIGN_ARCHITECT,
        target_class=
            activation.target_class,
        at=at,
        proof_reference=
            PROOF_REFERENCE,
        idempotency_key=
            key,
        session=session,
    )


def _no_ttl(
    collection: Any,
) -> bool:
    return all(
        "expireAfterSeconds"
        not in index
        for index in collection.list_indexes()
    )


def test_real_mongo_current_activation_p2_and_fresh_use_p3_allow(
    context: dict[str, Any],
) -> None:
    activation = _seed_and_issue(
        context,
        key="issue-p5-c7-success",
    )

    assert (
        activation.tenant_id
        is None
    )

    assert (
        context[
            "assurance_collection"
        ].count_documents({})
        == 1
    )

    with context[
        "client"
    ].start_session() as session:
        session.start_transaction()

        result = (
            _authorize_platform_interactive(
                context,
                activation=activation,
                key="p5-use-success",
                at=(
                    NOW
                    + timedelta(
                        minutes=1
                    )
                ),
                session=session,
            )
        )

        session.commit_transaction()

    assert result == activation

    assert (
        result.activation_id
        == activation.activation_id
    )

    assert (
        result.activated_at
        == activation.activated_at
    )

    assert (
        result.effective_until
        == activation.effective_until
    )

    assurance_rows = list(
        context[
            "assurance_collection"
        ].find({})
    )

    assert len(
        assurance_rows
    ) == 2

    use_rows = [
        row
        for row in assurance_rows
        if row.get(
            "assurance_purpose"
        )
        == (
            PrivilegedAssurancePurpose
            .PRIVILEGED_ACTIVATION_USE
            .value
        )
    ]

    assert len(
        use_rows
    ) == 1

    assert (
        use_rows[0][
            "principal_id"
        ]
        == PRINCIPAL
    )

    assert (
        context[
            "activation_registry"
        ].get_history(
            activation.activation_id
        )
        == (
            activation,
        )
    )


def test_real_mongo_use_abort_rolls_back_fresh_p3_only(
    context: dict[str, Any],
) -> None:
    activation = _seed_and_issue(
        context,
        key="issue-p5-c7-abort",
    )

    assurance_before = (
        context[
            "assurance_collection"
        ].count_documents({})
    )

    activation_before = (
        context[
            "activation_collection"
        ].count_documents({})
    )

    with context[
        "client"
    ].start_session() as session:
        session.start_transaction()

        result = (
            _authorize_platform_interactive(
                context,
                activation=activation,
                key="p5-use-abort",
                at=(
                    NOW
                    + timedelta(
                        minutes=1
                    )
                ),
                session=session,
            )
        )

        assert result == activation

        assert (
            context[
                "assurance_collection"
            ].count_documents(
                {},
                session=session,
            )
            == assurance_before + 1
        )

        session.abort_transaction()

    assert (
        context[
            "assurance_collection"
        ].count_documents({})
        == assurance_before
    )

    assert (
        context[
            "activation_collection"
        ].count_documents({})
        == activation_before
    )

    assert (
        context[
            "activation_registry"
        ].get_history(
            activation.activation_id
        )
        == (
            activation,
        )
    )


def test_real_mongo_expired_activation_denies_before_use_p3(
    context: dict[str, Any],
) -> None:
    activation = _seed_and_issue(
        context,
        key="issue-p5-c7-expired",
    )

    assurance_before = (
        context[
            "assurance_collection"
        ].count_documents({})
    )

    with context[
        "client"
    ].start_session() as session:
        session.start_transaction()

        with pytest.raises(
            PrivilegedActivationUseError,
            match="CURRENT_PRIVILEGED_ACTIVATION_REQUIRED",
        ):
            _authorize_platform_interactive(
                context,
                activation=activation,
                key="p5-use-expired",
                at=activation.effective_until,
                session=session,
            )

        session.abort_transaction()

    assert (
        context[
            "assurance_collection"
        ].count_documents({})
        == assurance_before
    )


def test_real_mongo_revoked_current_p2_denies_before_use_p3(
    context: dict[str, Any],
) -> None:
    activation = _seed_and_issue(
        context,
        key="issue-p5-c7-p2-revoked",
    )

    assurance_before = (
        context[
            "assurance_collection"
        ].count_documents({})
    )

    with context[
        "client"
    ].start_session() as session:
        session.start_transaction()

        PrincipalAuthorityRepository.compare_and_swap(
            PrincipalAuthority(
                PRINCIPAL,
                PrincipalStatus.REVOKED,
                2,
            ),
            1,
            context[
                "principals"
            ],
            session=session,
        )

        session.commit_transaction()

    with context[
        "client"
    ].start_session() as session:
        session.start_transaction()

        with pytest.raises(
            PrivilegedActivationUseError,
            match="CURRENT_PRIVILEGED_ELIGIBILITY_REQUIRED",
        ):
            _authorize_platform_interactive(
                context,
                activation=activation,
                key="p5-use-p2-revoked",
                at=(
                    NOW
                    + timedelta(
                        minutes=2
                    )
                ),
                session=session,
            )

        session.abort_transaction()

    assert (
        context[
            "assurance_collection"
        ].count_documents({})
        == assurance_before
    )

    assert (
        context[
            "activation_registry"
        ].get_history(
            activation.activation_id
        )
        == (
            activation,
        )
    )


def test_real_mongo_scope_and_persistence_boundaries(
    context: dict[str, Any],
) -> None:
    activation = _seed_and_issue(
        context,
        key="issue-p5-c7-boundary",
    )

    with context[
        "client"
    ].start_session() as session:
        session.start_transaction()

        result = (
            _authorize_platform_interactive(
                context,
                activation=activation,
                key="p5-use-boundary",
                at=(
                    NOW
                    + timedelta(
                        minutes=1
                    )
                ),
                session=session,
            )
        )

        session.commit_transaction()

    assert (
        result.tenant_id
        is None
    )

    assert _no_ttl(
        context[
            "activation_collection"
        ]
    )

    assert _no_ttl(
        context[
            "assurance_collection"
        ]
    )

    collections = set(
        context[
            "database"
        ].list_collection_names()
    )

    assert not any(
        "privileged_activation_use"
        in name
        for name in collections
    )

    assert not any(
        "break_glass"
        in name
        for name in collections
    )

    source = (
        Path(
            "tools/eos/auth/"
            "privileged_activation_use_authority.py"
        )
        .read_text(
            encoding="utf-8"
        )
    )

    assert (
        "privileged_activation:use"
        not in source
    )

    assert (
        "privileged_activation:break_glass"
        not in source
    )

    assert (
        "create_permission"
        not in source
    )

    lowered = source.casefold()

    forbidden_authority_surfaces = (
        "execute_payment(",
        "release_payment(",
        "settle_payment(",
        "record_settlement(",
        "create_settlement(",
        "payment_executor",
        "settlement_executor",
        "financial_execution",
        "create_permission(",
        "assign_role(",
        "break_glass(",
    )

    for forbidden in forbidden_authority_surfaces:
        assert forbidden not in lowered
