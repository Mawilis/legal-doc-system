"""
TITLE: WILSY OS Legal Profile Productive Work Read Service

VERSION: v1.0.1-PW-P4-DURABLE-PRODUCTIVE-WORK-READ-SERVICE

AUTHORITY:
    Wilsy OS Core Governance / Python EOS Legal Operations.

ABSOLUTE CANONICAL PATH:
    /Users/wilsonkhanyezi/legal-doc-system/tools/eos/legal_operations/service/legal_profile_productive_work_read_service.py

COLLABORATION / OWNERSHIP:
    Governed Legal work-item, assignment and supervision registries plus the
    CX27 operating-context hydrator provide durable inputs to this projection.

CERTIFICATION / UPDATE DATE: 2026-10-16

CHANGELOG:
    2026-10-16 v1.0.1-PW-P4-DURABLE-PRODUCTIVE-WORK-READ-SERVICE
    completes the sovereign header and versioned end seal without changing
    read orchestration, transaction, tenant or authority behavior.

COMPLIANCE:
    POPIA section 19; GDPR Article 32; SOC 2 CC7.2.

SECURITY / PRIVACY POSTURE:
    Exact tenant/principal predicates and caller-owned transaction propagation;
    no work, identity or matter data is logged.

TENANT BOUNDARY:
    Cross-registry tenant, principal, matter or work-item drift fails closed.

EPITOME:
    Read current durable assignment and supervision truth, hydrate the exact
    Legal work items those relationships reference, and delegate deterministic
    projection to the sovereign pure productive-work composer.

AUTHORITY BOUNDARY:
    Read orchestration only. This service creates no IAM, tenant membership,
    role authority, assignment, supervision, work item, workflow transition,
    professional authority, billing, payment, execution or settlement truth.

TRANSACTION BOUNDARY:
    The caller owns one already-active transaction. The same session is
    propagated unchanged to every durable registry read.

OPERATING-CONTEXT POSTURE:
    Durable CX27 LegalProductiveWorkOperatingContext values are hydrated
    using the caller-owned transaction and remain descriptive/non-authorizing
    projection metadata.

FINANCIAL AUTHORITY BOUNDARY:
    NONE. Kennel EOS exclusively owns financial execution and settlement.
"""

from __future__ import annotations

from datetime import datetime, timedelta
from typing import Any, Final, NoReturn, Protocol

from tools.eos.legal_operations.domain.legal_profile_productive_work import (
    LegalProductiveWorkOperatingContext,
    LegalProductiveWorkProjection,
    compose_legal_productive_work,
)
from tools.eos.legal_operations.domain.legal_work_assignment import (
    LegalWorkAssignment,
)
from tools.eos.legal_operations.domain.legal_work_item import (
    LegalWorkItem,
)
from tools.eos.legal_operations.domain.legal_work_supervision_binding import (
    LegalSupervisionScope,
    LegalWorkSupervisionBinding,
)


VERSION: Final[str] = (
    "v1.0.1-PW-P4-DURABLE-PRODUCTIVE-WORK-READ-SERVICE"
)


class LegalProductiveWorkReadServiceError(RuntimeError):
    """Base fail-closed productive-work read-service error."""


class LegalProductiveWorkReadServiceTransactionRequiredError(
    LegalProductiveWorkReadServiceError
):
    """Caller failed to provide one already-active transaction."""


def _fail(
    error_type: type[LegalProductiveWorkReadServiceError],
    code: str,
) -> NoReturn:
    raise error_type(code)


def _text(
    name: str,
    value: object,
) -> str:
    if (
        not isinstance(value, str)
        or not value
        or value.strip() != value
    ):
        _fail(
            LegalProductiveWorkReadServiceError,
            f"PW_P4_{name.upper()}_INVALID",
        )

    return value


def _moment(
    value: object,
) -> datetime:
    if (
        not isinstance(value, datetime)
        or value.tzinfo is None
        or value.utcoffset() is None
    ):
        _fail(
            LegalProductiveWorkReadServiceError,
            "PW_P4_AS_OF_INVALID",
        )

    return value


def _transaction(
    session: Any,
) -> Any:
    if (
        session is None
        or not bool(
            getattr(
                session,
                "in_transaction",
                False,
            )
        )
    ):
        _fail(
            LegalProductiveWorkReadServiceTransactionRequiredError,
            "PW_P4_ACTIVE_CALLER_TRANSACTION_REQUIRED",
        )

    return session


class _WorkItemReader(Protocol):
    def get_by_id(
        self,
        tenant_id: str,
        work_item_id: str,
        *,
        session: object,
    ) -> LegalWorkItem:
        ...

    def list_matter(
        self,
        tenant_id: str,
        case_matter_id: str,
        *,
        session: object,
    ) -> tuple[LegalWorkItem, ...]:
        ...


class _AssignmentReader(Protocol):
    def list_current_for_assignee(
        self,
        tenant_id: str,
        principal_id: str,
        *,
        session: Any,
    ) -> tuple[LegalWorkAssignment, ...]:
        ...


class _SupervisionReader(Protocol):
    def list_current_for_supervisor(
        self,
        tenant_id: str,
        supervisor_principal_id: str,
        at: datetime,
        *,
        session: Any,
    ) -> tuple[LegalWorkSupervisionBinding, ...]:
        ...


class _OperatingContextHydrator(Protocol):
    def hydrate(
        self,
        *,
        tenant_id: str,
        principal_id: str,
        at: datetime,
        session: Any,
    ) -> tuple[
        LegalProductiveWorkOperatingContext,
        ...
    ]:
        ...


class LegalProductiveWorkReadService:
    """Compose durable principal work without creating authority."""

    def __init__(
        self,
        *,
        work_item_registry: _WorkItemReader,
        assignment_registry: _AssignmentReader,
        supervision_registry: _SupervisionReader,
        operating_context_hydrator: _OperatingContextHydrator,
    ) -> None:
        self._work_item_registry = work_item_registry
        self._assignment_registry = assignment_registry
        self._supervision_registry = supervision_registry
        self._operating_context_hydrator = operating_context_hydrator

    @staticmethod
    def _add_work_item(
        work_by_id: dict[str, LegalWorkItem],
        item: LegalWorkItem,
        *,
        tenant_id: str,
    ) -> None:
        if item.tenant_id != tenant_id:
            _fail(
                LegalProductiveWorkReadServiceError,
                "PW_P4_WORK_ITEM_TENANT_SCOPE_MISMATCH",
            )

        existing = work_by_id.get(
            item.work_item_id
        )

        if (
            existing is not None
            and existing != item
        ):
            _fail(
                LegalProductiveWorkReadServiceError,
                "PW_P4_WORK_ITEM_IDENTITY_COLLISION",
            )

        work_by_id[
            item.work_item_id
        ] = item

    def project(
        self,
        *,
        tenant_id: str,
        principal_id: str,
        as_of: datetime,
        session: Any,
        due_soon_window: timedelta = timedelta(
            hours=24
        ),
    ) -> LegalProductiveWorkProjection:
        """Read durable current truth and delegate to the pure composer."""

        tx = _transaction(
            session
        )

        tenant = _text(
            "tenant_id",
            tenant_id,
        )

        principal = _text(
            "principal_id",
            principal_id,
        )

        moment = _moment(
            as_of
        )

        operating_contexts = (
            self._operating_context_hydrator.hydrate(
                tenant_id=tenant,
                principal_id=principal,
                at=moment,
                session=tx,
            )
        )

        assignments = (
            self._assignment_registry.list_current_for_assignee(
                tenant,
                principal,
                session=tx,
            )
        )

        supervision = (
            self._supervision_registry.list_current_for_supervisor(
                tenant,
                principal,
                moment,
                session=tx,
            )
        )

        work_by_id: dict[
            str,
            LegalWorkItem,
        ] = {}

        for assignment in assignments:
            if assignment.tenant_id != tenant:
                _fail(
                    LegalProductiveWorkReadServiceError,
                    "PW_P4_ASSIGNMENT_TENANT_SCOPE_MISMATCH",
                )

            if (
                assignment.assignee_principal_id
                != principal
            ):
                _fail(
                    LegalProductiveWorkReadServiceError,
                    "PW_P4_ASSIGNMENT_PRINCIPAL_SCOPE_MISMATCH",
                )

            work_item = (
                self._work_item_registry.get_by_id(
                    tenant,
                    assignment.work_item_id,
                    session=tx,
                )
            )

            self._add_work_item(
                work_by_id,
                work_item,
                tenant_id=tenant,
            )

            if (
                work_item.case_matter_id
                != assignment.case_matter_id
                or work_item.work_item_id
                != assignment.work_item_id
            ):
                _fail(
                    LegalProductiveWorkReadServiceError,
                    "PW_P4_ASSIGNMENT_WORK_ITEM_SCOPE_MISMATCH",
                )

        for binding in supervision:
            if binding.tenant_id != tenant:
                _fail(
                    LegalProductiveWorkReadServiceError,
                    "PW_P4_SUPERVISION_TENANT_SCOPE_MISMATCH",
                )

            if (
                binding.supervisor_principal_id
                != principal
            ):
                _fail(
                    LegalProductiveWorkReadServiceError,
                    "PW_P4_SUPERVISION_PRINCIPAL_SCOPE_MISMATCH",
                )

            scope = LegalSupervisionScope(
                binding.scope
            )

            if scope is LegalSupervisionScope.WORK_ITEM:
                work_item_id = binding.work_item_id

                if work_item_id is None:
                    _fail(
                        LegalProductiveWorkReadServiceError,
                        "PW_P4_SUPERVISION_WORK_ITEM_REQUIRED",
                    )

                if work_item_id not in work_by_id:
                    work_item = (
                        self._work_item_registry.get_by_id(
                            tenant,
                            work_item_id,
                            session=tx,
                        )
                    )

                    self._add_work_item(
                        work_by_id,
                        work_item,
                        tenant_id=tenant,
                    )
                else:
                    work_item = work_by_id[
                        work_item_id
                    ]

                if (
                    work_item.case_matter_id
                    != binding.case_matter_id
                    or work_item.work_item_id
                    != work_item_id
                ):
                    _fail(
                        LegalProductiveWorkReadServiceError,
                        "PW_P4_SUPERVISION_WORK_ITEM_SCOPE_MISMATCH",
                    )

                continue

            if scope is LegalSupervisionScope.MATTER:
                matter_items = (
                    self._work_item_registry.list_matter(
                        tenant,
                        binding.case_matter_id,
                        session=tx,
                    )
                )

                for work_item in matter_items:
                    self._add_work_item(
                        work_by_id,
                        work_item,
                        tenant_id=tenant,
                    )

                    if (
                        work_item.case_matter_id
                        != binding.case_matter_id
                    ):
                        _fail(
                            LegalProductiveWorkReadServiceError,
                            "PW_P4_MATTER_WORK_ITEM_SCOPE_MISMATCH",
                        )

                continue

            _fail(
                LegalProductiveWorkReadServiceError,
                "PW_P4_SUPERVISION_SCOPE_INVALID",
            )

        work_items = tuple(
            work_by_id[
                work_item_id
            ]
            for work_item_id in sorted(
                work_by_id
            )
        )

        return compose_legal_productive_work(
            tenant_id=tenant,
            principal_id=principal,
            as_of=moment,
            operating_contexts=tuple(
                operating_contexts
            ),
            work_items=work_items,
            assignments=tuple(
                assignments
            ),
            supervision_bindings=tuple(
                supervision
            ),
            due_soon_window=due_soon_window,
        )


__all__ = [
    "VERSION",
    "LegalProductiveWorkReadService",
    "LegalProductiveWorkReadServiceError",
    "LegalProductiveWorkReadServiceTransactionRequiredError",
]

# ==============================================================================
# WILSY OS SOVEREIGN ARTIFACT SEAL
# ==============================================================================
# ARTIFACT: legal_profile_productive_work_read_service.py
# VERSION: v1.0.1-PW-P4-DURABLE-PRODUCTIVE-WORK-READ-SERVICE
# READ-ONLY DURABLE ORCHESTRATION: YES
# CALLER-OWNED ACTIVE TRANSACTION REQUIRED: YES
# CURRENT ASSIGNMENT SOURCE: LegalWorkAssignmentRegistry
# CURRENT SUPERVISION SOURCE: LegalWorkSupervisionBindingRegistry
# WORK TRUTH SOURCE: LegalWorkItemRegistry
# PURE COMPOSER REUSED: YES
# OPERATING CONTEXT AUTHORITY: NONE
# IAM AUTHORITY: NONE
# ASSIGNMENT MUTATION AUTHORITY: NONE
# SUPERVISION MUTATION AUTHORITY: NONE
# WORK-ITEM MUTATION AUTHORITY: NONE
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively
# FAIL-CLOSED POSTURE: invalid input, inactive transaction, or scope drift rejects
# END OF WILSY OS SOVEREIGN ARTIFACT
