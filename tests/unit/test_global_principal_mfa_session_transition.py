"""Unit tests for the atomic verified-MFA to global-session transition."""
from datetime import datetime, timezone
from typing import Any, cast

import pytest

from tools.eos.auth.global_principal_mfa_session_transition import (
    GlobalPrincipalMfaSessionTransition,
)


class Transaction:
    in_transaction = True


def test_transition_consumes_mfa_then_issues_session_in_same_transaction() -> None:
    session = Transaction()
    selected = object()
    receipt = object()
    events: list[tuple[str, Any, Any]] = []
    instant = datetime(2026, 11, 3, tzinfo=timezone.utc)

    class Challenges:
        def consume_mfa_challenge_after_factor_verification(self, *, mfa_challenge_token, session, now):
            events.append(("consume", mfa_challenge_token, session))
            return selected

    class Sessions:
        def issue_after_mfa(self, selected_context, *, session, now):
            events.append(("issue", selected_context, session))
            return receipt

    transition = GlobalPrincipalMfaSessionTransition(
        challenge_service=cast(Any, Challenges()),
        session_authority=cast(Any, Sessions()),
    )
    result = transition.complete_after_verified_factor(
        mfa_challenge_token="opaque-mfa-challenge",
        session=session,
        now=instant,
    )

    assert result is receipt
    assert events == [
        ("consume", "opaque-mfa-challenge", session),
        ("issue", selected, session),
    ]


def test_session_issue_failure_propagates_for_caller_transaction_abort() -> None:
    session = Transaction()
    events: list[str] = []

    class Challenges:
        def consume_mfa_challenge_after_factor_verification(self, **kwargs):
            events.append("mfa-consumed-in-transaction")
            return object()

    class Sessions:
        def issue_after_mfa(self, *_args, **_kwargs):
            events.append("session-write-failed")
            raise RuntimeError("synthetic session persistence failure")

    transition = GlobalPrincipalMfaSessionTransition(
        challenge_service=cast(Any, Challenges()),
        session_authority=cast(Any, Sessions()),
    )
    with pytest.raises(RuntimeError, match="synthetic session persistence failure"):
        transition.complete_after_verified_factor(
            mfa_challenge_token="opaque-mfa-challenge",
            session=session,
        )
    assert events == ["mfa-consumed-in-transaction", "session-write-failed"]
    assert session.in_transaction is True


def test_mfa_consumption_failure_never_attempts_session_issue() -> None:
    class Challenges:
        def consume_mfa_challenge_after_factor_verification(self, **kwargs):
            raise RuntimeError("factor challenge rejected")

    class Sessions:
        def issue_after_mfa(self, *_args, **_kwargs):
            raise AssertionError("session issuance must not run")

    transition = GlobalPrincipalMfaSessionTransition(
        challenge_service=cast(Any, Challenges()),
        session_authority=cast(Any, Sessions()),
    )
    with pytest.raises(RuntimeError, match="factor challenge rejected"):
        transition.complete_after_verified_factor(
            mfa_challenge_token="opaque-mfa-challenge",
            session=Transaction(),
        )
