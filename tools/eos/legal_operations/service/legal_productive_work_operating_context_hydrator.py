"""
TITLE: WILSY OS Legal Productive-Work Operating-Context Hydrator

VERSION: v1.0.1-PW-P7B-CX27-OPERATING-CONTEXT-HYDRATOR

AUTHORITY:
    Wilsy OS Core Governance / Python EOS Legal Operations.

ABSOLUTE CANONICAL PATH:
    /Users/wilsonkhanyezi/legal-doc-system/tools/eos/legal_operations/service/legal_productive_work_operating_context_hydrator.py

COLLABORATION / OWNERSHIP:
    CX27 role-definition, occupancy, capability and scope registries provide
    durable descriptive truth; the productive-work read service consumes it.

CERTIFICATION / UPDATE DATE: 2026-10-16

CHANGELOG:
    2026-10-16 v1.0.1-PW-P7B-CX27-OPERATING-CONTEXT-HYDRATOR
    completes the sovereign header and versioned end seal without changing
    hydration, transaction, tenant or authority behavior.

COMPLIANCE:
    POPIA section 19; GDPR Article 32; SOC 2 CC7.2.

SECURITY / PRIVACY POSTURE:
    Tenant/principal scope is exact and every durable read shares the caller's
    active transaction; no identity or capability metadata is logged.

TENANT BOUNDARY:
    Cross-registry tenant, principal, role or revision mismatch fails closed.

EPITOME:
    Compose durable CX27 principal operating-role occupancy, exact occupied
    role revision, current capability metadata, and current organizational
    scope metadata into LegalProductiveWorkOperatingContext values.

SOVEREIGN COMPOSITION:
    current principal occupancy
        -> exact occupied role revision
        -> current capability bindings for that exact revision
        -> current scope bindings for that exact revision
        -> LegalProductiveWorkOperatingContext

TRANSACTION:
    Caller owns one already-active transaction. The identical session is
    propagated unchanged to every durable registry read.

AUTHORITY BOUNDARY:
    Read-only descriptive composition. This hydrator establishes no IAM
    permission, record/client/matter access, assignment, supervision,
    workflow authority, professional authority, financial authority,
    execution authority, or settlement authority.

FINANCIAL AUTHORITY BOUNDARY:
    NONE. Kennel EOS exclusively owns financial execution and settlement.
"""

from __future__ import annotations

from datetime import datetime
from typing import Any, Final, NoReturn, Protocol

from tools.eos.legal_operations.domain.legal_operating_role_capability_binding import (
    LegalOperatingRoleCapabilityBinding,
)
from tools.eos.legal_operations.domain.legal_operating_role_definition import (
    LegalOperatingRoleDefinition,
)
from tools.eos.legal_operations.domain.legal_operating_role_scope_binding import (
    LegalOperatingRoleScopeBinding,
)
from tools.eos.legal_operations.domain.legal_principal_operating_role_binding import (
    LegalPrincipalOperatingRoleBinding,
)
from tools.eos.legal_operations.domain.legal_profile_productive_work import (
    LegalProductiveWorkOperatingContext,
)


VERSION: Final[str] = (
    "v1.0.1-PW-P7B-CX27-OPERATING-CONTEXT-HYDRATOR"
)


class LegalProductiveWorkOperatingContextHydratorError(
    RuntimeError
):
    """Base fail-closed operating-context hydration error."""


class LegalProductiveWorkOperatingContextHydratorTransactionRequiredError(
    LegalProductiveWorkOperatingContextHydratorError
):
    """Caller failed to provide one already-active transaction."""


def _fail(
    error_type: type[
        LegalProductiveWorkOperatingContextHydratorError
    ],
    code: str,
) -> NoReturn:
    raise error_type(
        code
    )


def _text(
    name: str,
    value: object,
) -> str:
    if (
        not isinstance(
            value,
            str,
        )
        or not value
        or value.strip() != value
    ):
        _fail(
            LegalProductiveWorkOperatingContextHydratorError,
            f"PW_P7B_{name.upper()}_INVALID",
        )

    return value


def _moment(
    value: object,
) -> datetime:
    if (
        not isinstance(
            value,
            datetime,
        )
        or value.tzinfo is None
        or value.utcoffset() is None
    ):
        _fail(
            LegalProductiveWorkOperatingContextHydratorError,
            "PW_P7B_AT_INVALID",
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
            LegalProductiveWorkOperatingContextHydratorTransactionRequiredError,
            "PW_P7B_ACTIVE_CALLER_TRANSACTION_REQUIRED",
        )

    return session


class _PrincipalOperatingRoleReader(
    Protocol
):
    def list_current_for_principal(
        self,
        tenant_id: str,
        principal_id: str,
        at: datetime,
        *,
        session: Any,
    ) -> tuple[
        LegalPrincipalOperatingRoleBinding,
        ...
    ]:
        ...


class _OperatingRoleDefinitionReader(
    Protocol
):
    def get_revision(
        self,
        tenant_id: str,
        identity: str,
        revision: int,
        *,
        session: Any,
    ) -> LegalOperatingRoleDefinition:
        ...


class _OperatingRoleCapabilityReader(
    Protocol
):
    def list_current_for_operating_role_revision(
        self,
        tenant_id: str,
        operating_role_id: str,
        operating_role_revision: int,
        at: datetime,
        *,
        session: Any,
    ) -> tuple[
        LegalOperatingRoleCapabilityBinding,
        ...
    ]:
        ...


class _OperatingRoleScopeReader(
    Protocol
):
    def list_current_for_operating_role_revision(
        self,
        tenant_id: str,
        operating_role_id: str,
        operating_role_revision: int,
        at: datetime,
        *,
        session: Any,
    ) -> tuple[
        LegalOperatingRoleScopeBinding,
        ...
    ]:
        ...


class LegalProductiveWorkOperatingContextHydrator:
    """Hydrate non-authorizing productive-work operating contexts."""

    def __init__(
        self,
        *,
        principal_operating_role_registry:
            _PrincipalOperatingRoleReader,
        operating_role_definition_registry:
            _OperatingRoleDefinitionReader,
        operating_role_capability_registry:
            _OperatingRoleCapabilityReader,
        operating_role_scope_registry:
            _OperatingRoleScopeReader,
    ) -> None:
        self._principal_operating_role_registry = (
            principal_operating_role_registry
        )

        self._operating_role_definition_registry = (
            operating_role_definition_registry
        )

        self._operating_role_capability_registry = (
            operating_role_capability_registry
        )

        self._operating_role_scope_registry = (
            operating_role_scope_registry
        )

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
        """Return deterministic descriptive contexts for one exact principal."""

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
            at
        )

        occupancies = (
            self._principal_operating_role_registry
            .list_current_for_principal(
                tenant,
                principal,
                moment,
                session=tx,
            )
        )

        exact_roles: dict[
            tuple[
                str,
                int,
            ],
            LegalPrincipalOperatingRoleBinding,
        ] = {}

        for occupancy in occupancies:
            if (
                occupancy.tenant_id
                != tenant
                or occupancy.principal_id
                != principal
            ):
                _fail(
                    LegalProductiveWorkOperatingContextHydratorError,
                    "PW_P7B_OCCUPANCY_SCOPE_MISMATCH",
                )

            key = (
                occupancy.operating_role_id,
                occupancy.operating_role_revision,
            )

            exact_roles.setdefault(
                key,
                occupancy,
            )

        contexts: list[
            LegalProductiveWorkOperatingContext
        ] = []

        for (
            operating_role_id,
            operating_role_revision,
        ) in sorted(
            exact_roles
        ):
            role = (
                self._operating_role_definition_registry
                .get_revision(
                    tenant,
                    operating_role_id,
                    operating_role_revision,
                    session=tx,
                )
            )

            if (
                role.tenant_id
                != tenant
                or role.operating_role_id
                != operating_role_id
                or role.role_revision
                != operating_role_revision
            ):
                _fail(
                    LegalProductiveWorkOperatingContextHydratorError,
                    "PW_P7B_ROLE_DEFINITION_SCOPE_MISMATCH",
                )

            capability_bindings = (
                self._operating_role_capability_registry
                .list_current_for_operating_role_revision(
                    tenant,
                    operating_role_id,
                    operating_role_revision,
                    moment,
                    session=tx,
                )
            )

            capability_ids: set[
                str
            ] = set()

            for binding in capability_bindings:
                if (
                    binding.tenant_id
                    != tenant
                    or binding.operating_role_id
                    != operating_role_id
                    or binding.operating_role_revision
                    != operating_role_revision
                ):
                    _fail(
                        LegalProductiveWorkOperatingContextHydratorError,
                        "PW_P7B_CAPABILITY_BINDING_SCOPE_MISMATCH",
                    )

                capability_ids.update(
                    binding.capability_ids
                )

            scope_bindings = (
                self._operating_role_scope_registry
                .list_current_for_operating_role_revision(
                    tenant,
                    operating_role_id,
                    operating_role_revision,
                    moment,
                    session=tx,
                )
            )

            offices: set[
                str
            ] = set()

            practices: set[
                str
            ] = set()

            business_units: set[
                str
            ] = set()

            jurisdictions: set[
                str
            ] = set()

            for binding in scope_bindings:
                if (
                    binding.tenant_id
                    != tenant
                    or binding.operating_role_id
                    != operating_role_id
                    or binding.operating_role_revision
                    != operating_role_revision
                ):
                    _fail(
                        LegalProductiveWorkOperatingContextHydratorError,
                        "PW_P7B_SCOPE_BINDING_SCOPE_MISMATCH",
                    )

                offices.update(
                    binding.office_references
                )

                practices.update(
                    binding.practice_references
                )

                business_units.update(
                    binding.business_unit_references
                )

                jurisdictions.update(
                    binding.jurisdiction_references
                )

            contexts.append(
                LegalProductiveWorkOperatingContext(
                    operating_role_id=
                        operating_role_id,
                    operating_role_revision=
                        operating_role_revision,
                    display_name=
                        role.display_name,
                    capability_ids=
                        tuple(
                            sorted(
                                capability_ids
                            )
                        ),
                    office_references=
                        tuple(
                            sorted(
                                offices
                            )
                        ),
                    practice_references=
                        tuple(
                            sorted(
                                practices
                            )
                        ),
                    business_unit_references=
                        tuple(
                            sorted(
                                business_units
                            )
                        ),
                    jurisdiction_references=
                        tuple(
                            sorted(
                                jurisdictions
                            )
                        ),
                )
            )

        return tuple(
            contexts
        )


__all__ = [
    "VERSION",
    "LegalProductiveWorkOperatingContextHydrator",
    "LegalProductiveWorkOperatingContextHydratorError",
    "LegalProductiveWorkOperatingContextHydratorTransactionRequiredError",
]

# ==============================================================================
# WILSY OS SOVEREIGN ARTIFACT SEAL
# ==============================================================================
# ARTIFACT: legal_productive_work_operating_context_hydrator.py
# VERSION: v1.0.1-PW-P7B-CX27-OPERATING-CONTEXT-HYDRATOR
# READ-ONLY CX27 COMPOSITION: YES
# CURRENT PRINCIPAL OCCUPANCY: YES
# EXACT OCCUPIED ROLE REVISION: YES
# CURRENT CAPABILITY METADATA: YES
# CURRENT ORGANIZATIONAL SCOPE METADATA: YES
# MULTI-ROLE: YES
# DETERMINISTIC METADATA UNION: YES
# ROLE TITLE AUTHORITY: NONE
# OCCUPANCY AUTHORIZATION: NONE
# CAPABILITY IAM AUTHORITY: NONE
# SCOPE RECORD / CLIENT / MATTER AUTHORITY: NONE
# ASSIGNMENT / SUPERVISION AUTHORITY: NONE
# WORKFLOW AUTHORITY: NONE
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively
# FAIL-CLOSED POSTURE: invalid input, inactive transaction, or scope drift rejects
# END OF WILSY OS SOVEREIGN ARTIFACT
