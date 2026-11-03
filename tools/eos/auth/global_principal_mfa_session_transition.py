"""Atomic bridge from verified selected-membership MFA to a global session.

The transport/factor verifier must verify the enrolled factor for the principal
bound to the opaque MFA challenge before calling this coordinator. This module
then consumes that challenge and issues the selected-membership session using
the exact same caller-owned Mongo transaction. It never commits, aborts, retries,
or verifies a factor itself.
"""
from __future__ import annotations

from datetime import datetime
from typing import Any

from pymongo.client_session import ClientSession

from tools.eos.auth.global_principal_session_authority import (
    GlobalPrincipalSessionAuthority,
    GlobalPrincipalSessionReceipt,
)
from tools.eos.auth.membership_selection_challenge import (
    MembershipSelectionChallengeService,
)


class GlobalPrincipalMfaSessionTransition:
    """Compose one-time MFA consumption and session issuance atomically."""

    def __init__(
        self,
        *,
        challenge_service: MembershipSelectionChallengeService,
        session_authority: GlobalPrincipalSessionAuthority,
    ) -> None:
        self._challenges = challenge_service
        self._sessions = session_authority

    def complete_after_verified_factor(
        self,
        *,
        mfa_challenge_token: str,
        session: ClientSession | Any,
        now: datetime | None = None,
    ) -> GlobalPrincipalSessionReceipt:
        """Consume MFA and issue ACCESS/refresh in one caller-owned transaction.

        Call only after the enrolled factor has been verified against the
        principal bound to this challenge. If either transition raises, the
        caller MUST abort this transaction. Committing is permitted only after
        this method returns successfully.
        """
        selected = self._challenges.consume_mfa_challenge_after_factor_verification(
            mfa_challenge_token=mfa_challenge_token,
            session=session,
            now=now,
        )
        return self._sessions.issue_after_mfa(
            selected,
            session=session,
            now=now,
        )


__all__ = ["GlobalPrincipalMfaSessionTransition"]
