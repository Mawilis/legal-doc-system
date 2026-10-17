"""
WILSY OS Legal Work Completion Persistence Orchestrator.

VERSION: v2.1.0-P14-R20R28-WORK-COMPLETION-REPLAY-FIRST
AUTHORITY: Wilsy OS Legal Operations completion persistence orchestration.
CHANGELOG: v2.1.0-P14-R20R28-WORK-COMPLETION-REPLAY-FIRST adds durable completion-history replay adjudication
before authority composition while preserving caller-owned transaction,
tenant, IAM, workflow, dependency, legal-event and financial boundaries.
TENANT BOUNDARY: Completion history and persistence remain scoped to the
exact tenant and work item supplied through the authenticated command path.
AUTHORITY BOUNDARY: This orchestrator sequences certified completion
authority composition, pure event preparation and immutable persistence; it
does not manufacture IAM, assignment, supervision or adjacent authority.
FINANCIAL AUTHORITY BOUNDARY: NONE. Kennel EOS remains the exclusive
financial execution authority.

P14-R20R28 topology:

    caller-owned active transaction
        -> durable completion-history replay adjudication
        -> R20R23 canonical completion-authority composition
        -> R20R18 pure completion-event preparation
        -> completion-event registry create_or_replay

Exact replay returns the already-recorded immutable completion event before
new authority composition. Ambiguous history and divergent replay fail closed.

The exact same caller-owned active transaction is propagated through
history resolution, authority composition and durable completion persistence.

This orchestrator does not:
- evaluate IAM directly;
- manage transaction lifecycle;
- synthesize authority provenance;
- perform workflow/dependency/notification/legal-event/financial execution.
"""

from __future__ import annotations

from datetime import datetime
from typing import Any, Final, NoReturn, Protocol

from tools.eos.legal_operations.domain.legal_work_assignment import (
    LegalWorkAssignment,
)
from tools.eos.legal_operations.domain.legal_work_completion_event import (
    LegalWorkCompletionEvent,
)
from tools.eos.legal_operations.domain.legal_work_item import (
    LegalWorkItem,
)
from tools.eos.legal_operations.service.legal_work_completion_authority_composer import (
    AuthorizationEvidenceIssuer,
    compose_legal_work_completion_authority_evidence,
)
from tools.eos.legal_operations.service.legal_work_completion_command_service import (
    prepare_legal_work_completion_event,
)


VERSION: Final[str] = (
    "v2.1.0-P14-R20R28-"
    "WORK-COMPLETION-REPLAY-FIRST"
)


class LegalWorkCompletionPersistenceOrchestrationError(
    RuntimeError
):
    """Fail-closed completion persistence orchestration error."""


class CompletionRegistry(
    Protocol
):
    def list_work_history(
        self,
        tenant_id: str,
        work_item_id: str,
        *,
        session: object,
    ) -> tuple[
        LegalWorkCompletionEvent,
        ...,
    ]:
        """Return immutable completion history for one tenant/work item."""
        ...

    def create_or_replay(
        self,
        value: LegalWorkCompletionEvent,
        *,
        session: Any,
    ) -> LegalWorkCompletionEvent:
        ...


def _fail(
    code: str,
) -> NoReturn:
    raise LegalWorkCompletionPersistenceOrchestrationError(
        code
    )


def _active_transaction(
    session: object,
) -> object:
    if session is None:
        _fail(
            "P14_R20R25_ACTIVE_TRANSACTION_REQUIRED"
        )

    marker = getattr(
        session,
        "in_transaction",
        False,
    )

    active = (
        marker()
        if callable(marker)
        else marker
    )

    if active is not True:
        _fail(
            "P14_R20R25_ACTIVE_TRANSACTION_REQUIRED"
        )

    return session


def record_legal_work_completion(
    *,
    tenant_id: str,
    principal_id: str,
    work_item: LegalWorkItem,
    assignments: tuple[
        LegalWorkAssignment,
        ...,
    ],
    completion_evidence_reference: str,
    completion_evidence_fingerprint: str,
    evaluated_at: datetime,
    authorization_evidence_issuer: AuthorizationEvidenceIssuer,
    completion_registry: CompletionRegistry,
    session: object,
) -> LegalWorkCompletionEvent:
    """
    Compose authority, construct event and persist exact completion truth.

    Transaction lifecycle belongs exclusively to the caller.
    """

    tx = _active_transaction(
        session
    )

    existing_history = completion_registry.list_work_history(
        tenant_id,
        work_item.work_item_id,
        session=tx,
    )

    if len(existing_history) > 1:
        _fail(
            "P14_R20R28_COMPLETION_REPLAY_HISTORY_AMBIGUOUS"
        )

    if existing_history:
        existing = existing_history[0]

        exact_replay = (
            existing.tenant_id == tenant_id
            and existing.case_matter_id
            == work_item.case_matter_id
            and existing.work_item_id
            == work_item.work_item_id
            and existing.work_item_fingerprint
            == work_item.fingerprint
            and existing.actor_principal_id
            == principal_id
            and existing.completion_evidence_reference
            == completion_evidence_reference
            and existing.completion_evidence_fingerprint
            == completion_evidence_fingerprint
        )

        if exact_replay:
            return existing

        _fail(
            "P14_R20R28_COMPLETION_ALREADY_RECORDED_DIFFERENTLY"
        )

    authority = (
        compose_legal_work_completion_authority_evidence(
            tenant_id=tenant_id,
            principal_id=principal_id,
            work_item=work_item,
            assignments=assignments,
            evaluated_at=evaluated_at,
            authorization_evidence_issuer=(
                authorization_evidence_issuer
            ),
            session=tx,
        )
    )

    candidate = prepare_legal_work_completion_event(
        work_item=work_item,
        completion_authority_evidence=authority,
        completion_evidence_reference=(
            completion_evidence_reference
        ),
        completion_evidence_fingerprint=(
            completion_evidence_fingerprint
        ),
    )

    return completion_registry.create_or_replay(
        candidate,
        session=tx,
    )


__all__ = [
    "VERSION",
    "CompletionRegistry",
    "LegalWorkCompletionPersistenceOrchestrationError",
    "record_legal_work_completion",
]


# =============================================================================
# WILSY OS SOVEREIGN ARTIFACT SEAL
# =============================================================================
# ARTIFACT:
#   legal_work_completion_persistence_orchestrator.py
# VERSION:
#   v2.1.0-P14-R20R28-WORK-COMPLETION-REPLAY-FIRST
# AUTHORITY BOUNDARY:
#   Completion persistence orchestration only; no independent IAM,
#   assignment, supervision, workflow, dependency, legal-event or
#   financial execution authority.
# TENANT POSTURE:
#   Exact tenant/work-item history and persistence scope only.
# REPLAY:
#   Durable completion history is adjudicated before R20R23 composition;
#   exact replay returns existing immutable truth, while divergent or
#   ambiguous history fails closed.
# AUTHORITY COMPOSITION:
#   R20R23 exactly once when no prior completion exists.
# EVENT PREPARATION:
#   R20R18 exactly once when no prior completion exists.
# PERSISTENCE:
#   completion registry create_or_replay exactly once for a new candidate.
# TRANSACTION:
#   one exact caller-owned active session.
# IAM DIRECT EVALUATION:
#   NONE
# TRANSACTION LIFECYCLE:
#   NONE
# WORKFLOW:
#   NONE
# DEPENDENCY:
#   NONE
# NOTIFICATION:
#   NONE
# LEGAL EVENT:
#   NONE
# FINANCIAL EXECUTION AUTHORITY:
#   NONE; Kennel EOS exclusively owns financial execution.
# END OF WILSY OS SOVEREIGN ARTIFACT
# =============================================================================
