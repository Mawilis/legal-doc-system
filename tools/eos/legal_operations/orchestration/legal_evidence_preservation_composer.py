"""WILSY OS — runtime Legal Evidence preservation composer.

TITLE: Legal Evidence Preservation Composer
VERSION: v1.0.0-L10A2R-C4D4C-PRESERVATION-COMPOSER
AUTHORITY: WILSY OS Core Governance / Python EOS Legal Operations
EPITOME: Compose one non-durable preservation projection from the exact
         durable C4D4A retention fact and bounded C4D4B legal-hold history
         under one caller-owned active transaction and explicit assessment
         instant.
ABSOLUTE CANONICAL PATH:
    /Users/wilsonkhanyezi/legal-doc-system/tools/eos/legal_operations/orchestration/legal_evidence_preservation_composer.py
COLLABORATION / OWNERSHIP:
    C4D4A registry owns durable retention facts.
    C4D4B registry owns durable append-only legal-hold history.
    C4D4B currentness owns pure hold-history currentness semantics.
    C4D4C preservation state vocabulary remains owned by the pure preservation
    domain. This composer only reads, projects and combines already-authoritative
    evidence.
CERTIFICATION / UPDATE DATE: 2026-10-01
CHANGELOG:
    v1.0.0 establishes caller-transaction propagation, exact provider-object
    reads, pure retention assessment, pure legal-hold currentness projection,
    fail-closed preservation aggregation and zero persistence.
COMPLIANCE:
    Derived preservation evidence only. It does not determine whether a legal
    hold should be imposed or released and does not create legal clearance.
SECURITY / PRIVACY POSTURE:
    Exact tenant/provider-object scoping; no raw evidence content; no external
    network or provider IO; no hidden clock.
TENANT BOUNDARY:
    Both durable source reads use the exact caller-supplied tenant and provider
    object identity under the same active caller-owned session.
AUTHORITY BOUNDARY:
    Read/compose only. No hold issuance/release, retention satisfaction,
    orphan proof, deletion authorization or provider mutation.
FINANCIAL AUTHORITY BOUNDARY:
    No billing, payment, execution or settlement authority. Kennel EOS remains
    exclusive financial execution authority.

TRANSACTION BOUNDARY:
    Caller owns the active transaction. This composer never starts, commits,
    aborts or retries a transaction.

PERSISTENCE BOUNDARY:
    None. The composed result is derived runtime evidence and is never written
    as canonical durable truth.

TIME BOUNDARY:
    One explicit caller-supplied aware ``assessed_at`` instant. No wall clock.

FAIL-CLOSED DECLARATION:
    Inactive/missing transaction, cross-scope source evidence, malformed source
    evidence, ambiguous legal-hold currentness and corrupt legal-hold currentness
    cannot create clearance or deletion authority. Ambiguous/corrupt hold
    currentness remains preservation-blocking.
"""

from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any, Final, Protocol

from tools.eos.legal_operations.domain.legal_evidence_legal_hold_constraint import (
    LegalEvidenceLegalHoldConstraint,
)
from tools.eos.legal_operations.domain.legal_evidence_legal_hold_currentness import (
    LegalEvidenceLegalHoldCurrentness,
    project_legal_evidence_legal_hold_currentness,
)
from tools.eos.legal_operations.domain.legal_evidence_preservation_assessment import (
    LegalEvidencePreservationState,
)
from tools.eos.legal_operations.domain.legal_evidence_retention_constraint import (
    LegalEvidenceRetentionAssessment,
    LegalEvidenceRetentionConstraint,
    assess_legal_evidence_retention,
)


VERSION: Final[str] = (
    "v1.0.0-L10A2R-C4D4C-PRESERVATION-COMPOSER"
)


class LegalEvidencePreservationComposerError(
    ValueError
):
    """Stable fail-closed orchestration error without source-data disclosure."""

    def __init__(
        self,
        code: str,
    ) -> None:
        """Expose one bounded institutional error code."""

        self.code = code
        super().__init__(
            code
        )


class _RetentionReader(
    Protocol
):
    """Structural read contract for the C4D4A durable source."""

    def get_by_provider_object(
        self,
        *,
        tenant_id: str,
        provider_name: str,
        storage_reference: str,
        object_version_reference: str,
        session: Any,
    ) -> LegalEvidenceRetentionConstraint:
        """Return the exact durable provider-object retention fact."""

        ...


class _HoldHistoryReader(
    Protocol
):
    """Structural read contract for the C4D4B append-only source."""

    def list_provider_object_history(
        self,
        *,
        tenant_id: str,
        provider_name: str,
        storage_reference: str,
        object_version_reference: str,
        session: Any,
    ) -> Iterable[
        LegalEvidenceLegalHoldConstraint
    ]:
        """Return bounded durable legal-hold history for one provider object."""

        ...


def _aware_utc(
    value: object,
) -> datetime:
    """Require one explicit aware assessment instant normalized to UTC."""

    if (
        not isinstance(
            value,
            datetime,
        )
        or value.tzinfo is None
        or value.utcoffset() is None
    ):
        raise LegalEvidencePreservationComposerError(
            "L10A2R_C4D4C_COMPOSER_ASSESSED_AT_INVALID"
        )

    return value.astimezone(
        timezone.utc
    )


def _require_active_transaction(
    session: object,
) -> None:
    """Require the caller to own one already-active transaction."""

    if session is None:
        raise LegalEvidencePreservationComposerError(
            "L10A2R_C4D4C_COMPOSER_ACTIVE_TRANSACTION_REQUIRED"
        )

    try:
        active = bool(
            getattr(
                session,
                "in_transaction",
            )
        )
    except Exception as error:
        raise LegalEvidencePreservationComposerError(
            "L10A2R_C4D4C_COMPOSER_ACTIVE_TRANSACTION_REQUIRED"
        ) from error

    if not active:
        raise LegalEvidencePreservationComposerError(
            "L10A2R_C4D4C_COMPOSER_ACTIVE_TRANSACTION_REQUIRED"
        )


def _derive_state(
    retention: LegalEvidenceRetentionAssessment,
    hold: LegalEvidenceLegalHoldCurrentness,
) -> tuple[
    LegalEvidencePreservationState,
    bool,
]:
    """Derive the existing C4D4C state from certified source projections."""

    retention_required = not retention.retention_elapsed
    hold_required = hold.preservation_blocking

    if (
        retention_required
        and hold_required
    ):
        return (
            LegalEvidencePreservationState.RETENTION_AND_LEGAL_HOLD_REQUIRED,
            True,
        )

    if retention_required:
        return (
            LegalEvidencePreservationState.RETENTION_REQUIRED,
            True,
        )

    if hold_required:
        return (
            LegalEvidencePreservationState.LEGAL_HOLD_REQUIRED,
            True,
        )

    return (
        LegalEvidencePreservationState.NO_PRESERVATION_BLOCK_DEMONSTRATED,
        False,
    )


@dataclass(
    frozen=True,
    slots=True,
)
class LegalEvidencePreservationComposition:
    """Immutable non-durable preservation composition for one provider object.

    ``legal_hold_currentness`` retains ambiguity/corruption detail while
    ``state`` uses the existing C4D4C preservation vocabulary. This value never
    constitutes deletion authorization, provider mutation authority, orphan
    proof, retention satisfaction, or legal clearance.
    """

    retention: LegalEvidenceRetentionAssessment
    legal_hold_currentness: LegalEvidenceLegalHoldCurrentness
    assessed_at: datetime
    state: LegalEvidencePreservationState
    preservation_required: bool
    orphan_proven: bool = False
    deletion_authorized: bool = False
    provider_delete_authorized: bool = False

    def __post_init__(
        self,
    ) -> None:
        """Verify source correlation, state consistency and authority bounds."""

        assessed_at = _aware_utc(
            self.assessed_at
        )

        retention_constraint = (
            self.retention.constraint
        )

        hold = (
            self.legal_hold_currentness
        )

        if (
            retention_constraint.tenant_id
            != hold.tenant_id
            or retention_constraint.provider_name
            != hold.provider_name
            or retention_constraint.storage_reference
            != hold.storage_reference
            or retention_constraint.object_version_reference
            != hold.object_version_reference
        ):
            raise LegalEvidencePreservationComposerError(
                "L10A2R_C4D4C_COMPOSER_SOURCE_SCOPE_MISMATCH"
            )

        if (
            self.retention.assessed_at
            != assessed_at
            or hold.evaluated_at
            != assessed_at
        ):
            raise LegalEvidencePreservationComposerError(
                "L10A2R_C4D4C_COMPOSER_ASSESSMENT_TIME_MISMATCH"
            )

        expected_state, expected_required = (
            _derive_state(
                self.retention,
                hold,
            )
        )

        if (
            self.state
            is not expected_state
            or self.preservation_required
            is not expected_required
        ):
            raise LegalEvidencePreservationComposerError(
                "L10A2R_C4D4C_COMPOSER_STATE_MISMATCH"
            )

        if (
            self.orphan_proven
            or self.deletion_authorized
            or self.provider_delete_authorized
        ):
            raise LegalEvidencePreservationComposerError(
                "L10A2R_C4D4C_COMPOSER_LATER_AUTHORITY_FORBIDDEN"
            )

        object.__setattr__(
            self,
            "assessed_at",
            assessed_at,
        )


class LegalEvidencePreservationComposer:
    """Read-only runtime composer over certified C4D4A/C4D4B sources.

    The caller supplies and owns one active transaction. The composer performs
    exactly one retention provider-object read and one legal-hold provider-object
    history read under that same session, delegates all source semantics to the
    certified pure domains, persists nothing and creates no later authority.
    """

    def __init__(
        self,
        retention_registry: _RetentionReader,
        legal_hold_registry: _HoldHistoryReader,
    ) -> None:
        """Bind existing durable read surfaces without assuming ownership."""

        self._retention_registry = (
            retention_registry
        )
        self._legal_hold_registry = (
            legal_hold_registry
        )

    def compose_preservation(
        self,
        *,
        tenant_id: str,
        provider_name: str,
        storage_reference: str,
        object_version_reference: str,
        assessed_at: datetime,
        session: Any,
    ) -> LegalEvidencePreservationComposition:
        """Compose current preservation evidence under the caller transaction.

        No durable mutation occurs. Ambiguous or corrupt legal-hold currentness
        remains preservation-blocking through the certified currentness result.
        """

        _require_active_transaction(
            session
        )

        at = _aware_utc(
            assessed_at
        )

        retention_constraint = (
            self._retention_registry.get_by_provider_object(
                tenant_id=tenant_id,
                provider_name=provider_name,
                storage_reference=storage_reference,
                object_version_reference=object_version_reference,
                session=session,
            )
        )

        hold_history = tuple(
            self._legal_hold_registry.list_provider_object_history(
                tenant_id=tenant_id,
                provider_name=provider_name,
                storage_reference=storage_reference,
                object_version_reference=object_version_reference,
                session=session,
            )
        )

        retention = (
            assess_legal_evidence_retention(
                retention_constraint,
                assessed_at=at,
            )
        )

        hold_currentness = (
            project_legal_evidence_legal_hold_currentness(
                tenant_id=tenant_id,
                provider_name=provider_name,
                storage_reference=storage_reference,
                object_version_reference=object_version_reference,
                evaluated_at=at,
                history=hold_history,
            )
        )

        state, preservation_required = (
            _derive_state(
                retention,
                hold_currentness,
            )
        )

        return LegalEvidencePreservationComposition(
            retention=retention,
            legal_hold_currentness=hold_currentness,
            assessed_at=at,
            state=state,
            preservation_required=preservation_required,
        )


__all__ = [
    "VERSION",
    "LegalEvidencePreservationComposer",
    "LegalEvidencePreservationComposerError",
    "LegalEvidencePreservationComposition",
]


# ARTIFACT: legal_evidence_preservation_composer.py
# VERSION: v1.0.0-L10A2R-C4D4C-PRESERVATION-COMPOSER
# AUTHORITY BOUNDARY: read-only preservation composition only
# TENANT POSTURE: exact tenant/provider-object source correlation
# FAIL-CLOSED POSTURE: ambiguity/corruption remain preservation-blocking
# TRANSACTION POSTURE: caller-owned active transaction only
# PERSISTENCE POSTURE: none
# HOLD POSTURE: no hold issuance/release authority
# RETENTION POSTURE: no retention-satisfaction authority
# ORPHAN POSTURE: no orphan-proof authority
# DELETION POSTURE: no deletion/provider-mutation authority
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively
# END OF WILSY OS SOVEREIGN ARTIFACT
