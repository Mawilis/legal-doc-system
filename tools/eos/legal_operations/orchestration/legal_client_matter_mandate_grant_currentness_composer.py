"""Read-only composition of one client mandate-grant currentness result.

TITLE: WILSY OS Legal Client Matter Mandate Grant Currentness Composer
VERSION: v1.0.0-L9B9-P2-CLIENT-MANDATE-GRANT-CURRENTNESS-COMPOSER
AUTHORITY: Wilsy OS Core Governance / Python EOS Legal Operations
EPITOME: Re-read one exact grant, its complete lifecycle history, and its
         CaseMatter state inside one caller-owned transaction, then construct
         the published immutable currentness projection for one explicit
         evaluation instant. This composer is read-only and never persists the
         projection or infers successor currentness.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tools/eos/legal_operations/orchestration/legal_client_matter_mandate_grant_currentness_composer.py
COLLABORATION / OWNERSHIP: Formation and lifecycle registries own durable
                            evidence; LegalOperationsLifecycleRegistry owns
                            CaseMatter history; the currentness domain owns
                            projection invariants and fingerprints. This
                            composer owns only transaction-scoped composition.
CERTIFICATION / UPDATE DATE: 2026-09-27
CHANGELOG: v1.0.0-L9B9-P2-CLIENT-MANDATE-GRANT-CURRENTNESS-COMPOSER adds
           caller-session validation, consistent-snapshot reads, explicit
           formation time-window handling, deterministic lifecycle traversal,
           fail-closed terminal ambiguity handling, exact CaseMatter
           correlation, and read-only projection construction. It creates no
           currentness persistence or downstream legal authority.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2; ISO 27001.
SECURITY / PRIVACY POSTURE: Caller supplies only tenant/grant/evaluation
                             inputs. All authority fingerprints and state are
                             derived from canonical registries under the same
                             transaction. Errors expose stable codes only.
TENANT BOUNDARY: Every formation, lifecycle, and CaseMatter read is bound to
                 the exact tenant and persisted identity; cross-scope evidence
                 returns CORRUPT_BLOCKED.
AUTHORITY BOUNDARY: Read-only currentness composition only. No acting-capacity
                    re-read, acknowledgment, mandate, Engagement,
                    Representation, Court, IAM, HTTP, UI, or delivery action.
FINANCIAL AUTHORITY BOUNDARY: No financial authority, payment, settlement, or
                              execution is created; Kennel EOS remains the
                              exclusive financial execution authority.
TRANSACTION BOUNDARY: Caller supplies and owns an already-active Mongo
                      transaction. This module never starts, commits, aborts,
                      retries, or reconciles a transaction.
FAIL-CLOSED DECLARATION: Missing transactions, malformed/corrupt evidence,
                         scope divergence, conflicting terminal events, and
                         unavailable authoritative reads never degrade to
                         CURRENT.
"""
from __future__ import annotations

from collections.abc import Iterable
from datetime import datetime, timezone
import hashlib
import json
from typing import Any, Final, NoReturn, cast

from tools.eos.legal_operations.domain.legal_client_matter_mandate_grant import (
    LegalClientMatterMandateGrant,
)
from tools.eos.legal_operations.domain.legal_client_matter_mandate_grant_currentness import (
    LegalClientMatterMandateGrantCurrentness,
    LegalClientMatterMandateGrantCurrentnessReason,
    LegalClientMatterMandateGrantCurrentnessState,
)
from tools.eos.legal_operations.domain.legal_client_matter_mandate_grant_lifecycle import (
    LegalClientMatterMandateGrantLifecycle,
    LegalClientMatterMandateGrantLifecycleEvent,
)
from tools.eos.legal_operations.domain.legal_operations_current_projection import (
    resolve_current_lifecycle_snapshot,
)
from tools.eos.legal_operations.domain.legal_operations_lifecycle import (
    CaseMatter,
    CaseMatterState,
)
from tools.eos.legal_operations.registry import (
    legal_client_matter_mandate_grant_lifecycle_registry as lifecycle_registry,
    legal_client_matter_mandate_grant_registry as grant_registry,
    legal_operations_lifecycle_registry as matter_registry,
)


VERSION: Final[str] = "v1.0.0-L9B9-P2-CLIENT-MANDATE-GRANT-CURRENTNESS-COMPOSER"
UTC = timezone.utc


class LegalClientMatterMandateGrantCurrentnessComposerError(RuntimeError):
    """Stable, non-sensitive fail-closed composition error."""

    def __init__(self, code: str) -> None:
        """Expose only a bounded code and never supplied authority data."""
        self.code = code
        super().__init__(code)


def _fail(code: str, cause: BaseException | None = None) -> NoReturn:
    """Raise one stable composer failure while retaining technical cause."""
    error = LegalClientMatterMandateGrantCurrentnessComposerError(code)
    if cause is None:
        raise error
    raise error from cause


def _text(name: str, value: object) -> str:
    """Require a bounded caller identity without trimming or coercion."""
    if not isinstance(value, str) or not value or value != value.strip():
        _fail(f"L9B9_P2_{name.upper()}_INVALID")
    return value


def _active_transaction(session: Any) -> Any:
    """Require an already-active caller-owned transaction before any read."""
    if session is None:
        _fail("L9B9_P2_ACTIVE_TRANSACTION_REQUIRED")
    marker = getattr(session, "in_transaction", None)
    try:
        active = marker() if callable(marker) else marker
    except (AttributeError, TypeError):
        active = False
    if active is not True:
        _fail("L9B9_P2_ACTIVE_TRANSACTION_REQUIRED")
    return session


def _evaluation_time(value: object) -> datetime:
    """Require explicit aware evaluation time and normalize it to UTC."""
    if not isinstance(value, datetime) or value.tzinfo is None or value.utcoffset() is None:
        _fail("L9B9_P2_EVALUATION_TIME_INVALID")
    return value.astimezone(UTC).replace(microsecond=value.microsecond)


def _projection_id(tenant_id: str, grant_id: str, evaluation_time: datetime) -> str:
    """Derive a bounded deterministic projection identity without persistence."""
    payload = {
        "tenant_id": tenant_id,
        "client_grant_id": grant_id,
        "evaluation_time": evaluation_time.isoformat(timespec="microseconds"),
    }
    digest = hashlib.sha3_512(
        json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")
    ).hexdigest()[:48]
    return f"currentness-{digest}"


def _formation_absent(
    *, tenant_id: str, grant_id: str, evaluation_time: datetime
) -> LegalClientMatterMandateGrantCurrentness:
    """Return a truthful absent-formation result without fabricated evidence."""
    return LegalClientMatterMandateGrantCurrentness(
        currentness_id=_projection_id(tenant_id, grant_id, evaluation_time),
        tenant_id=tenant_id,
        client_grant_id=grant_id,
        client_grant_fingerprint=None,
        case_matter_id=None,
        matter_fingerprint=None,
        client_party_id=None,
        subject_identity_fingerprint=None,
        evaluation_time=evaluation_time,
        state=LegalClientMatterMandateGrantCurrentnessState.FORMATION_ABSENT,
        reason=LegalClientMatterMandateGrantCurrentnessReason.FORMATION_ABSENT,
        matter_state=None,
        matter_state_evidence_fingerprint=None,
        formation_fingerprint=None,
        lifecycle_evidence_fingerprints=(),
        decisive_lifecycle_evidence_fingerprints=(),
    )


def _corrupt(
    *, tenant_id: str, grant_id: str, evaluation_time: datetime
) -> LegalClientMatterMandateGrantCurrentness:
    """Return a non-usable result when canonical correlation is not trusted."""
    return LegalClientMatterMandateGrantCurrentness(
        currentness_id=_projection_id(tenant_id, grant_id, evaluation_time),
        tenant_id=tenant_id,
        client_grant_id=grant_id,
        client_grant_fingerprint=None,
        case_matter_id=None,
        matter_fingerprint=None,
        client_party_id=None,
        subject_identity_fingerprint=None,
        evaluation_time=evaluation_time,
        state=LegalClientMatterMandateGrantCurrentnessState.CORRUPT_BLOCKED,
        reason=LegalClientMatterMandateGrantCurrentnessReason.CORRUPT_EVIDENCE,
        matter_state=None,
        matter_state_evidence_fingerprint=None,
        formation_fingerprint=None,
        lifecycle_evidence_fingerprints=(),
        decisive_lifecycle_evidence_fingerprints=(),
    )


def _grant_correlates(grant: object, tenant_id: str, grant_id: str) -> bool:
    """Require the hydrated formation to match the caller's exact identity."""
    return (
        type(grant) is LegalClientMatterMandateGrant
        and grant.tenant_id == tenant_id
        and grant.client_grant_id == grant_id
    )


def _event_correlates(
    event: LegalClientMatterMandateGrantLifecycle,
    grant: LegalClientMatterMandateGrant,
) -> bool:
    """Require every lifecycle event to match the complete grant key."""
    return (
        type(event) is LegalClientMatterMandateGrantLifecycle
        and event.tenant_id == grant.tenant_id
        and event.client_grant_id == grant.client_grant_id
        and event.client_grant_fingerprint == grant.fingerprint
        and event.case_matter_id == grant.case_matter_id
        and event.matter_fingerprint == grant.matter_fingerprint
        and event.client_party_id == grant.client_party_id
        and event.subject_identity_fingerprint == grant.subject_identity_fingerprint
        and event.breadth is grant.breadth
        and event.scope_fingerprint == grant.scope_fingerprint
        and event.capabilities == grant.capabilities
    )


def _ordered_events(
    events: Iterable[LegalClientMatterMandateGrantLifecycle],
) -> tuple[LegalClientMatterMandateGrantLifecycle, ...]:
    """Apply deterministic traversal ordering without granting precedence."""
    return tuple(
        sorted(
            events,
            key=lambda value: (
                value.effective_from,
                value.occurred_at,
                value.fingerprint,
                value.lifecycle_event_id,
            ),
        )
    )


def _terminal_projection(
    *,
    grant: LegalClientMatterMandateGrant,
    evaluation_time: datetime,
    events: tuple[LegalClientMatterMandateGrantLifecycle, ...],
) -> LegalClientMatterMandateGrantCurrentness | None:
    """Resolve applicable terminal evidence, refusing conflicting authority."""
    applicable = tuple(event for event in events if event.effective_from <= evaluation_time)
    if not applicable:
        return None
    ordered = _ordered_events(applicable)
    fingerprints = tuple(event.fingerprint for event in ordered)
    event_types = {event.event for event in ordered}
    if len(event_types) > 1:
        return _state_projection(
            grant=grant,
            evaluation_time=evaluation_time,
            state=LegalClientMatterMandateGrantCurrentnessState.AMBIGUOUS,
            reason=LegalClientMatterMandateGrantCurrentnessReason.AMBIGUOUS_LIFECYCLE,
            lifecycle_fingerprints=fingerprints,
            decisive_fingerprints=fingerprints,
        )
    first = ordered[0]
    if first.event is LegalClientMatterMandateGrantLifecycleEvent.REVOKED:
        return _state_projection(
            grant=grant,
            evaluation_time=evaluation_time,
            state=LegalClientMatterMandateGrantCurrentnessState.REVOKED,
            reason=LegalClientMatterMandateGrantCurrentnessReason.REVOKED,
            lifecycle_fingerprints=fingerprints,
            decisive_fingerprints=fingerprints,
        )
    successors = {
        (event.successor_client_grant_id, event.successor_client_grant_fingerprint)
        for event in ordered
    }
    if len(successors) != 1:
        return _state_projection(
            grant=grant,
            evaluation_time=evaluation_time,
            state=LegalClientMatterMandateGrantCurrentnessState.AMBIGUOUS,
            reason=LegalClientMatterMandateGrantCurrentnessReason.AMBIGUOUS_LIFECYCLE,
            lifecycle_fingerprints=fingerprints,
            decisive_fingerprints=fingerprints,
        )
    successor_id, successor_fp = next(iter(successors))
    return _state_projection(
        grant=grant,
        evaluation_time=evaluation_time,
        state=LegalClientMatterMandateGrantCurrentnessState.SUPERSEDED,
        reason=LegalClientMatterMandateGrantCurrentnessReason.SUPERSEDED,
        lifecycle_fingerprints=fingerprints,
        decisive_fingerprints=fingerprints,
        successor_client_grant_id=successor_id,
        successor_client_grant_fingerprint=successor_fp,
    )


def _state_projection(
    *,
    grant: LegalClientMatterMandateGrant,
    evaluation_time: datetime,
    state: LegalClientMatterMandateGrantCurrentnessState,
    reason: LegalClientMatterMandateGrantCurrentnessReason,
    lifecycle_fingerprints: tuple[str, ...],
    decisive_fingerprints: tuple[str, ...],
    successor_client_grant_id: str | None = None,
    successor_client_grant_fingerprint: str | None = None,
    matter: CaseMatter | None = None,
) -> LegalClientMatterMandateGrantCurrentness:
    """Construct through the projection domain, never duplicate its digest."""
    return LegalClientMatterMandateGrantCurrentness(
        currentness_id=_projection_id(grant.tenant_id, grant.client_grant_id, evaluation_time),
        tenant_id=grant.tenant_id,
        client_grant_id=grant.client_grant_id,
        client_grant_fingerprint=grant.fingerprint,
        case_matter_id=grant.case_matter_id,
        matter_fingerprint=grant.matter_fingerprint,
        client_party_id=grant.client_party_id,
        subject_identity_fingerprint=grant.subject_identity_fingerprint,
        evaluation_time=evaluation_time,
        state=state,
        reason=reason,
        matter_state=None if matter is None else matter.state,
        matter_state_evidence_fingerprint=None if matter is None else matter.fingerprint,
        formation_fingerprint=grant.fingerprint,
        lifecycle_evidence_fingerprints=lifecycle_fingerprints,
        decisive_lifecycle_evidence_fingerprints=decisive_fingerprints,
        successor_client_grant_id=successor_client_grant_id,
        successor_client_grant_fingerprint=successor_client_grant_fingerprint,
    )


class LegalClientMatterMandateGrantCurrentnessComposer:
    """Compose one read-only currentness projection in a caller transaction.

    The constructor receives only collection handles. ``compose_currentness``
    accepts tenant/grant/evaluation inputs and an active caller session; no
    caller-supplied fingerprint, lifecycle state, matter state, or successor
    authority is trusted. The method performs no writes and leaves transaction
    lifecycle entirely with its caller.
    """

    def __init__(
        self,
        *,
        grant_collection: Any,
        lifecycle_collection: Any,
        matter_lifecycle_collection: Any,
    ) -> None:
        """Bind the three read-only canonical collection surfaces."""
        if any(value is None for value in (grant_collection, lifecycle_collection, matter_lifecycle_collection)):
            _fail("L9B9_P2_COLLECTION_REQUIRED")
        self._grant_collection = grant_collection
        self._lifecycle_collection = lifecycle_collection
        self._matter_lifecycle_collection = matter_lifecycle_collection

    def compose_currentness(
        self,
        tenant_id: str,
        client_grant_id: str,
        evaluation_time: datetime,
        session: Any,
    ) -> LegalClientMatterMandateGrantCurrentness:
        """Read canonical evidence and return one exact projection.

        Formation, lifecycle, and CaseMatter reads receive the same active
        session. Future lifecycle events are excluded at the supplied instant;
        equal or cross-time terminal conflicts are never resolved by ordering.
        Acting capacity, acknowledgment, mandate, Engagement, IAM, HTTP, and
        financial authorities are deliberately not consulted.
        """
        tx = _active_transaction(session)
        tenant = _text("tenant_id", tenant_id)
        grant_id = _text("client_grant_id", client_grant_id)
        at = _evaluation_time(evaluation_time)
        try:
            grant = grant_registry.get_grant(
                tenant, grant_id, self._grant_collection, session=tx
            )
        except grant_registry.LegalClientMatterMandateGrantRegistryNotFoundError:
            return _formation_absent(tenant_id=tenant, grant_id=grant_id, evaluation_time=at)
        except grant_registry.LegalClientMatterMandateGrantRegistryError as error:
            _fail("L9B9_P2_FORMATION_UNAVAILABLE", error)
        if not _grant_correlates(grant, tenant, grant_id):
            return _corrupt(tenant_id=tenant, grant_id=grant_id, evaluation_time=at)
        assert type(grant) is LegalClientMatterMandateGrant
        if at < grant.effective_from:
            return _state_projection(
                grant=grant,
                evaluation_time=at,
                state=LegalClientMatterMandateGrantCurrentnessState.NOT_YET_EFFECTIVE,
                reason=LegalClientMatterMandateGrantCurrentnessReason.NOT_YET_EFFECTIVE,
                lifecycle_fingerprints=(),
                decisive_fingerprints=(),
            )
        if grant.effective_until is not None and at >= grant.effective_until:
            return _state_projection(
                grant=grant,
                evaluation_time=at,
                state=LegalClientMatterMandateGrantCurrentnessState.EXPIRED,
                reason=LegalClientMatterMandateGrantCurrentnessReason.EXPIRED,
                lifecycle_fingerprints=(),
                decisive_fingerprints=(),
            )
        try:
            history = lifecycle_registry.list_events_for_grant(
                tenant,
                grant.client_grant_id,
                self._lifecycle_collection,
                session=tx,
            )
        except lifecycle_registry.LegalClientMatterMandateGrantLifecycleRegistryError as error:
            return _corrupt(tenant_id=tenant, grant_id=grant_id, evaluation_time=at)
        if any(not _event_correlates(event, grant) for event in history):
            return _corrupt(tenant_id=tenant, grant_id=grant_id, evaluation_time=at)
        terminal = _terminal_projection(grant=grant, evaluation_time=at, events=history)
        if terminal is not None:
            return terminal
        try:
            matter_history = matter_registry.LegalOperationsLifecycleRegistry.get_entity_history(
                tenant,
                "CaseMatter",
                grant.case_matter_id,
                self._matter_lifecycle_collection,
                session=tx,
            )
            matter_value = resolve_current_lifecycle_snapshot(
                matter_history, expected_type=CaseMatter
            )
        except Exception:
            return _corrupt(tenant_id=tenant, grant_id=grant_id, evaluation_time=at)
        if (
            type(matter_value) is not CaseMatter
            or matter_value.tenant_id != tenant
            or matter_value.case_matter_id != grant.case_matter_id
            or matter_value.fingerprint == ""
        ):
            return _corrupt(tenant_id=tenant, grant_id=grant_id, evaluation_time=at)
        if matter_value.state is not CaseMatterState.OPEN:
            return _state_projection(
                grant=grant,
                evaluation_time=at,
                state=LegalClientMatterMandateGrantCurrentnessState.MATTER_CLOSED,
                reason=LegalClientMatterMandateGrantCurrentnessReason.MATTER_CLOSED,
                lifecycle_fingerprints=(),
                decisive_fingerprints=(),
                matter=matter_value,
            )
        return _state_projection(
            grant=grant,
            evaluation_time=at,
            state=LegalClientMatterMandateGrantCurrentnessState.CURRENT,
            reason=LegalClientMatterMandateGrantCurrentnessReason.CURRENT,
            lifecycle_fingerprints=(),
            decisive_fingerprints=(),
            matter=matter_value,
        )


def compose_currentness(
    *,
    tenant_id: str,
    client_grant_id: str,
    evaluation_time: datetime,
    session: Any,
    grant_collection: Any,
    lifecycle_collection: Any,
    matter_lifecycle_collection: Any,
) -> LegalClientMatterMandateGrantCurrentness:
    """Compose through a one-shot functional boundary using the same contract."""
    composer = LegalClientMatterMandateGrantCurrentnessComposer(
        grant_collection=grant_collection,
        lifecycle_collection=lifecycle_collection,
        matter_lifecycle_collection=matter_lifecycle_collection,
    )
    return composer.compose_currentness(tenant_id, client_grant_id, evaluation_time, session)


__all__ = [
    "VERSION",
    "LegalClientMatterMandateGrantCurrentnessComposer",
    "LegalClientMatterMandateGrantCurrentnessComposerError",
    "compose_currentness",
]


# ARTIFACT: legal_client_matter_mandate_grant_currentness_composer.py
# VERSION: v1.0.0-L9B9-P2-CLIENT-MANDATE-GRANT-CURRENTNESS-COMPOSER
# AUTHORITY BOUNDARY: read-only currentness composition; no persistence
# TENANT POSTURE: exact tenant and canonical formation/lifecycle/matter scope
# FAIL-CLOSED POSTURE: no degraded CURRENT; conflicts and corruption block
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively
# END OF WILSY OS SOVEREIGN ARTIFACT
