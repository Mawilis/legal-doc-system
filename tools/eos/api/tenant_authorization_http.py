"""
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2; ISO 27001.
SECURITY / PRIVACY POSTURE: No credentials or personal information exposed by this metadata repair.
TENANT BOUNDARY: Exact tenant scope, membership and entitlements remain server-governed.
AUTHORITY BOUNDARY: No new IAM, admission, session or business execution authority is created.
FINANCIAL AUTHORITY BOUNDARY: No financial execution; Kennel EOS remains exclusive.
Canonical tenant authorization HTTP composition and denial observation.

TITLE: WILSY OS Tenant Authorization HTTP Boundary
VERSION: v1.10.0-REQUEST-SCOPED-EVIDENCE-READS
AUTHORITY: FastAPI dependency translation of frozen durable tenant authorization.
EPITOME: Binds an authenticated identity and explicit tenant scope to current
         IAM truth, then emits one bounded terminal observation for admitted
         authorization denial or dependency unavailability without becoming
         an authorization authority; it scopes WILSY employer commands and
         requires active customer HR product entitlement.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tools/eos/api/tenant_authorization_http.py
COLLABORATION / OWNERSHIP: Wilson Khanyezi / Wilsy Core Engineering / Python EOS IAM.
CERTIFICATION / UPDATE DATE: 2026-11-15
CHANGELOG:
    2026-11-15 v1.10.0-REQUEST-SCOPED-EVIDENCE-READS reuses only successful,
    exact-key, sessionless principal, membership, business-capacity, and
    granting-role evidence reads during one HTTP request. Every source still
    evaluates its own permission and operation through the canonical composer;
    transaction-bound workforce currentness always reads transaction-local
    evidence and no decision survives the request.
    2026-11-15 v1.9.0-SCOPED-REQUEST-TIMING emits opt-in, trace-correlated,
    privacy-safe timing around the existing tenant/capacity decision,
    threadpool hand-off, HR workforce preflight, and HR entitlement gate. It
    introduces no authority, output, cache, or persistence behavior.
    2026-11-15 v1.8.0-WORKFORCE-PREFLIGHT-FAIL-CLOSED classifies a workforce-
    governed permission's non-eligible tenant role before opening the workforce
    currentness dependency. A role that could otherwise be authorized still
    requires the same transaction-bound currentness evidence. This keeps an
    unrelated optional HR source denied rather than letting an unavailable HR
    store fracture other independently admitted My Work sources.
    2026-11-15 v1.7.0-OPTIONAL-PLATFORM-EMPLOYER-SCOPE permits the existing
    optional source-admission adapter to carry the same validated canonical-WILSY
    employer IAM pair as the required adapter. This preserves denied-source
    omission while retaining currentness, entitlement and outage fail-closed
    behavior; it adds no permission or authorization path.
    2026-11-14 v1.6.0-PLAIN-LOG-SAFE-IAM-CORRELATION renders the existing
    closed pseudonymous observation in default message-only logs as well as
    structured metadata. No authentication, decision, tenant or write change.
    2026-11-12 v1.5.0-HR-ENTITLEMENT-PLATFORM-EMPLOYER-SCOPE keeps the
    canonical WILSY employer override inside this existing IAM dependency and
    requires exact active D22B2 HR entitlement for every customer hr: permission.
    Entitlement reads are tenant-scoped, read-only and fail closed.
    2026-11-11 v1.4.0-NONBLOCKING-TENANT-IAM-ADAPTER evaluates existing
    synchronous MongoDB authorization and its workforce transaction in
    FastAPI's bounded threadpool; 403/503 decisions are unchanged.
    2026-10-28 v1.3.0-P6-DIRECT-BUSINESS-ROLE-RESOLUTION exposes one exact-scope,
    single-read business-role lookup for the canonical resolver while preserving
    separate authorization-role reads and existing denial/outage classification.
    2026-10-19 v1.2.0-P6-IAM-DENIAL-OBSERVABILITY adds one failure-safe,
    bounded, post-decision structured observation for authenticated tenant IAM
    denials and dependency unavailability. Server-generated correlation and
    SHA3-512 pseudonyms exclude raw identity, credential, policy, request, and
    legal evidence; existing authentication, authorization, HTTP, tenant, and
    persistence authority remain unchanged.
    v1.1.0 routes governed tenant business-role identifiers to dedicated
    tenant_business_roles truth while preserving authorization-role resolution
    in role_assignments.
    v1.0.0 established the fail-closed tenant authorization HTTP dependency.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2.
SECURITY / PRIVACY POSTURE: Transport projections never grant authority;
                            malformed scope denies. SHA3-512 references are
                            pseudonymous and linkable, not anonymous.
TENANT BOUNDARY: X-Tenant-ID remains scope only; platform-employer pairs are selected only for canonical WILSY, and customer hr: permissions require exact-tenant ACTIVE D22B2 HR entitlement.
AUTHORITY BOUNDARY: Reuses frozen tenant IAM composition; D22B2 HR entitlement
                    is an independent customer-product gate and never grants IAM.
                    Observations classify existing IAM results and never decide access.
FINANCIAL AUTHORITY BOUNDARY: Kennel EOS exclusively owns financial execution.
"""

from __future__ import annotations

import hashlib
import json
import logging
import time
import uuid
from dataclasses import dataclass
from typing import Any, Final, cast

from fastapi import Depends, Header, Request, status
from pymongo.read_concern import ReadConcern
from pymongo.read_preferences import ReadPreference
from starlette.concurrency import run_in_threadpool

from tools.eos.api.exceptions import ForbiddenOperationException, WilsyAPIException
from tools.eos.auth.authentication import (
    current_request_timing_correlation,
    emit_request_timing,
    establish_request_timing_correlation,
    get_current_identity,
    get_principal_authority_repository,
)
from tools.eos.auth.authorization import (
    get_role_assignment_repository as _get_role_assignment_repository,
)
from tools.eos.auth.identity import SovereignIdentity
from tools.eos.auth.permission_namespace import permission_metadata
from tools.eos.auth.role_assignment_repository import (
    RoleAssignmentNotFoundError,
    RoleAssignmentRepositoryError,
)
from tools.eos.auth.tenant_access import get_tenant_membership_repository
from tools.eos.auth.tenant_authority_policy import TENANT_ROLES
from tools.eos.auth.tenant_authorization import (
    TenantAuthorizationDecision,
    TenantAuthorizationReason,
    authorize_tenant_operation,
)
from tools.eos.auth.tenant_business_role_repository import (
    TenantBusinessRoleNotFoundError,
    TenantBusinessRoleRepository,
    TenantBusinessRoleRepositoryError,
)
from tools.eos.auth.workspace_bootstrap_projection import (
    WILSY_COMPANY_TENANT_ID,
)
from tools.eos.kernel.db import get_client, get_database
from tools.eos.saas.domain.tenant_product_entitlement import (
    TenantProductEntitlementState,
)
from tools.eos.saas.entitlement.product_catalogue import TenantProductId
from tools.eos.saas.entitlement.tenant_product_entitlement_composer import (
    derive_tenant_product_entitlement_id,
)
from tools.eos.saas.entitlement.tenant_product_entitlement_registry import (
    CURRENT_COLLECTION as PRODUCT_ENTITLEMENT_CURRENT_COLLECTION,
    HISTORY_COLLECTION as PRODUCT_ENTITLEMENT_HISTORY_COLLECTION,
    TenantProductEntitlementRegistryError,
    TenantProductEntitlementRegistryNotFoundError,
    get_current as get_current_product_entitlement,
)
from tools.eos.kernel.db import get_client, get_database
from tools.eos.workforce.registry.workforce_relationship_registry import (
    COLLECTION_NAME as WORKFORCE_RELATIONSHIP_COLLECTION,
)


VERSION: Final[str] = "v1.10.0-REQUEST-SCOPED-EVIDENCE-READS"
logger = logging.getLogger("WilsyOS.API.TenantAuthorization")
_OBSERVATION_SCHEMA: Final[str] = "WILSY-TENANT-AUTHORIZATION-OBSERVATION/V1"
_OBSERVATION_VERSION: Final[str] = "v1.0.0-P6-IAM-DENIAL-OBSERVABILITY"

_UNAVAILABLE: Final[frozenset[TenantAuthorizationReason]] = frozenset(
    {
        TenantAuthorizationReason.PRINCIPAL_AUTHORITY_UNAVAILABLE,
        TenantAuthorizationReason.MEMBERSHIP_AUTHORITY_UNAVAILABLE,
        TenantAuthorizationReason.TENANT_BUSINESS_ROLE_AUTHORITY_UNAVAILABLE,
        TenantAuthorizationReason.ROLE_ASSIGNMENT_AUTHORITY_UNAVAILABLE,
        TenantAuthorizationReason.WORKFORCE_AUTHORITY_UNAVAILABLE,
    }
)
_DENIED: Final[frozenset[TenantAuthorizationReason]] = frozenset(
    {
        TenantAuthorizationReason.INVALID_INPUT,
        TenantAuthorizationReason.PRINCIPAL_NOT_FOUND,
        TenantAuthorizationReason.PRINCIPAL_INACTIVE,
        TenantAuthorizationReason.MEMBERSHIP_NOT_FOUND,
        TenantAuthorizationReason.MEMBERSHIP_INACTIVE,
        TenantAuthorizationReason.NO_ACTIVE_TENANT_BUSINESS_ROLE,
        TenantAuthorizationReason.MULTIPLE_ACTIVE_TENANT_BUSINESS_ROLES,
        TenantAuthorizationReason.PERMISSION_UNKNOWN,
        TenantAuthorizationReason.PERMISSION_NOT_CANONICAL,
        TenantAuthorizationReason.PERMISSION_NAMESPACE_MISMATCH,
        TenantAuthorizationReason.PERMISSION_OPERATION_MISMATCH,
        TenantAuthorizationReason.PERMISSION_NOT_GRANTED,
        TenantAuthorizationReason.ROLE_ASSIGNMENT_INACTIVE,
        TenantAuthorizationReason.BUSINESS_ROLE_INELIGIBLE,
        TenantAuthorizationReason.SYSTEM_AUTHORITY_REQUIRED,
        TenantAuthorizationReason.FINANCIAL_EXECUTION_PROHIBITED,
        TenantAuthorizationReason.WORKFORCE_NOT_CURRENT,
    }
)
_PRINCIPAL_REASONS: Final[frozenset[TenantAuthorizationReason]] = frozenset(
    {
        TenantAuthorizationReason.PRINCIPAL_NOT_FOUND,
        TenantAuthorizationReason.PRINCIPAL_INACTIVE,
        TenantAuthorizationReason.PRINCIPAL_AUTHORITY_UNAVAILABLE,
    }
)
_MEMBERSHIP_REASONS: Final[frozenset[TenantAuthorizationReason]] = frozenset(
    {
        TenantAuthorizationReason.MEMBERSHIP_NOT_FOUND,
        TenantAuthorizationReason.MEMBERSHIP_INACTIVE,
        TenantAuthorizationReason.MEMBERSHIP_AUTHORITY_UNAVAILABLE,
    }
)
_BUSINESS_ROLE_REASONS: Final[frozenset[TenantAuthorizationReason]] = frozenset(
    {
        TenantAuthorizationReason.NO_ACTIVE_TENANT_BUSINESS_ROLE,
        TenantAuthorizationReason.MULTIPLE_ACTIVE_TENANT_BUSINESS_ROLES,
        TenantAuthorizationReason.BUSINESS_ROLE_INELIGIBLE,
        TenantAuthorizationReason.TENANT_BUSINESS_ROLE_AUTHORITY_UNAVAILABLE,
    }
)
_ROLE_ASSIGNMENT_REASONS: Final[frozenset[TenantAuthorizationReason]] = frozenset(
    {
        TenantAuthorizationReason.ROLE_ASSIGNMENT_INACTIVE,
        TenantAuthorizationReason.ROLE_ASSIGNMENT_AUTHORITY_UNAVAILABLE,
    }
)
_PERMISSION_REASONS: Final[frozenset[TenantAuthorizationReason]] = frozenset(
    {
        TenantAuthorizationReason.PERMISSION_UNKNOWN,
        TenantAuthorizationReason.PERMISSION_NOT_CANONICAL,
        TenantAuthorizationReason.PERMISSION_NAMESPACE_MISMATCH,
        TenantAuthorizationReason.PERMISSION_OPERATION_MISMATCH,
        TenantAuthorizationReason.PERMISSION_NOT_GRANTED,
    }
)
_WORKFORCE_REASONS: Final[frozenset[TenantAuthorizationReason]] = frozenset(
    {
        TenantAuthorizationReason.WORKFORCE_NOT_CURRENT,
        TenantAuthorizationReason.WORKFORCE_AUTHORITY_UNAVAILABLE,
    }
)

_TIMING_ADMISSION_LABELS: Final[dict[str, str]] = {
    "legal_productive_work_read": "LEGAL_READ",
    "operations_work_item_read": "OPERATIONS_READ",
    "intelligence_work_item_read": "INTELLIGENCE_READ",
    "crm_work_item_read": "CRM_READ",
    "platform_employer_headcount_requisition_read": "HR_HEADCOUNT_READ",
    "platform_employer_headcount_requisition_create": "HR_HEADCOUNT_SUBMIT",
    "platform_employer_headcount_requisition_decide": "HR_HEADCOUNT_DECIDE",
    "platform_employer_hiring_offer_read": "HR_OFFER_READ",
    "platform_employer_hiring_offer_submit": "HR_OFFER_SUBMIT",
    "platform_employer_hiring_offer_decide": "HR_OFFER_DECIDE",
    "platform_employer_hiring_offer_send": "HR_OFFER_SEND",
}


def _timing_admission_label(operation: str) -> str:
    """Return a closed diagnostic label without disclosing permission details."""

    return _TIMING_ADMISSION_LABELS.get(operation, "OTHER")


@dataclass(frozen=True, slots=True)
class TenantAuthorizationContext:
    """Authenticated exact-tenant context containing the canonical decision."""

    identity: SovereignIdentity
    tenant_id: str
    decision: TenantAuthorizationDecision


def _new_correlation_id() -> str:
    """Create one server-owned identifier for an admitted IAM evaluation."""

    return f"tenant-authorization-{uuid.uuid4().hex}"


def _observation_ref(value: str) -> str:
    """Return a linkable SHA3-512 pseudonym, never an anonymity claim."""

    return hashlib.sha3_512(value.encode("utf-8")).hexdigest()


def _decision_class(reason: TenantAuthorizationReason | None) -> str:
    """Collapse internal IAM reasons into a closed operational class."""

    if reason is None:
        return "CONSISTENCY"
    if reason in _PRINCIPAL_REASONS:
        return "PRINCIPAL"
    if reason in _MEMBERSHIP_REASONS:
        return "MEMBERSHIP"
    if reason in _BUSINESS_ROLE_REASONS:
        return "BUSINESS_ROLE"
    if reason in _ROLE_ASSIGNMENT_REASONS:
        return "ROLE_ASSIGNMENT"
    if reason in _PERMISSION_REASONS:
        return "PERMISSION"
    if reason in _WORKFORCE_REASONS:
        return "WORKFORCE"
    if reason is TenantAuthorizationReason.FINANCIAL_EXECUTION_PROHIBITED:
        return "FINANCIAL_BOUNDARY"
    if reason is TenantAuthorizationReason.SYSTEM_AUTHORITY_REQUIRED:
        return "SYSTEM_BOUNDARY"
    if reason is TenantAuthorizationReason.INVALID_INPUT:
        return "INPUT"
    return "CONSISTENCY"


def _observe_terminal(
    *,
    outcome: str,
    reason: TenantAuthorizationReason | None,
    tenant_id: str,
    principal_id: str,
    correlation_id: str,
    http_status: int,
) -> None:
    """Emit one bounded terminal observation without affecting the verdict.

    Raw identifiers, tokens, request headers, permission names, operation names,
    internal policy details, exception text, and legal evidence are excluded.
    The event observes an already-produced IAM result and has no grant, deny,
    persistence, workflow, legal-decision, or financial authority.
    """

    try:
        payload: dict[str, object] = {
            "schema": _OBSERVATION_SCHEMA,
            "version": _OBSERVATION_VERSION,
            "event": "TENANT_AUTHORIZATION_HTTP_TERMINAL",
            "outcome": outcome,
            "decision_class": _decision_class(reason),
            "tenant_ref": _observation_ref(tenant_id),
            "principal_ref": _observation_ref(principal_id),
            "correlation_ref": _observation_ref(correlation_id),
            "http_status": http_status,
        }
        logger.log(
            logging.WARNING if outcome == "AUTHORIZATION_DENIED" else logging.ERROR,
            "TENANT_AUTHORIZATION_HTTP_TERMINAL %s",
            json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=True),
            extra={"wilsy_authorization_observation": payload},
        )
    except Exception:
        return


class _TenantAuthorityRoleReader:
    """Resolve each role namespace from its canonical durable store."""

    def __init__(
        self,
        *,
        authorization_repository: Any,
        business_repository: Any,
    ) -> None:
        self._authorization_repository = authorization_repository
        self._business_repository = business_repository

    def resolve_current_business_role(
        self,
        principal_id: str,
        tenant_id: str,
        *,
        session: Any = None,
    ) -> object:
        """Resolve the legacy business-role projection for compatibility callers."""

        try:
            return (
                self._business_repository.resolve(principal_id, tenant_id)
                if session is None
                else self._business_repository.resolve(
                    principal_id, tenant_id, session=session
                )
            )
        except TenantBusinessRoleNotFoundError as exc:
            raise RoleAssignmentNotFoundError(
                "TENANT_BUSINESS_ROLE_NOT_FOUND"
            ) from exc
        except TenantBusinessRoleRepositoryError as exc:
            raise RoleAssignmentRepositoryError(
                "TENANT_BUSINESS_ROLE_AUTHORITY_UNAVAILABLE"
            ) from exc

    def resolve_all_business_roles(
        self, principal_id: str, tenant_id: str, *, session: Any = None
    ) -> tuple[object, ...]:
        """Read all current capacities for operation-aware selection."""
        try:
            resolver = getattr(self._business_repository, "resolve_all", None)
            if callable(resolver):
                values = resolver(principal_id, tenant_id, session=session)
                if not isinstance(values, tuple):
                    raise TenantBusinessRoleRepositoryError(
                        "TENANT_BUSINESS_ROLE_COLLECTION_INVALID"
                    )
                return values
            # Existing injected adapters remain single-capacity until migrated.
            legacy = self.resolve_current_business_role(
                principal_id, tenant_id, session=session
            )
            return (legacy,)
        except TenantBusinessRoleNotFoundError as exc:
            raise RoleAssignmentNotFoundError("TENANT_BUSINESS_ROLE_NOT_FOUND") from exc
        except TenantBusinessRoleRepositoryError as exc:
            raise RoleAssignmentRepositoryError("TENANT_BUSINESS_ROLE_AUTHORITY_UNAVAILABLE") from exc

    def resolve(
        self,
        principal_id: str,
        tenant_id: str,
        role_id: str,
        *,
        session: Any = None,
    ) -> object:
        """Read one current role from its existing namespace authority."""

        if role_id in TENANT_ROLES:
            try:
                exact_resolver = getattr(self._business_repository, "resolve_business_role", None)
                if callable(exact_resolver):
                    value = exact_resolver(
                        principal_id, tenant_id, role_id, session=session
                    )
                else:
                    value = self._business_repository.resolve(
                        principal_id, tenant_id, session=session
                    )
                    if getattr(value, "business_role", None) != role_id:
                        raise TenantBusinessRoleNotFoundError("TENANT_BUSINESS_ROLE_NOT_FOUND")
            except TenantBusinessRoleNotFoundError as exc:
                raise RoleAssignmentNotFoundError(
                    "TENANT_BUSINESS_ROLE_NOT_FOUND"
                ) from exc
            except TenantBusinessRoleRepositoryError as exc:
                raise RoleAssignmentRepositoryError(
                    "TENANT_BUSINESS_ROLE_AUTHORITY_UNAVAILABLE"
                ) from exc
            if getattr(value, "business_role", None) != role_id:
                raise RoleAssignmentNotFoundError("TENANT_BUSINESS_ROLE_NOT_FOUND")
            return value

        return (
            self._authorization_repository.resolve(principal_id, tenant_id, role_id)
            if session is None
            else self._authorization_repository.resolve(
                principal_id, tenant_id, role_id, session=session
            )
        )


@dataclass(slots=True)
class _RequestScopedAuthorityEvidence:
    """Store successful source-independent reads for one ASGI request only.

    The cache owns no authority and stores no authorization decision. Its key
    includes repository purpose, resolver method, and every exact string
    argument. Failed reads are deliberately not cached. A non-``None`` Mongo
    session always bypasses this cache so caller-owned transactional workforce
    currentness remains fresh and transaction-bound.
    """

    values: dict[tuple[str, str, tuple[str, ...]], object]


class _RequestScopedEvidenceReader:
    """Delegate one evidence repository through a request-local success cache.

    This adapter exposes only the read methods consumed by the canonical tenant
    authorization composer. It does not alter inputs, exceptions, return
    values, revisions, session propagation, tenant scope, or repository
    transaction ownership.
    """

    def __init__(
        self,
        *,
        purpose: str,
        repository: Any,
        evidence: _RequestScopedAuthorityEvidence,
    ) -> None:
        self._purpose = purpose
        self._repository = repository
        self._evidence = evidence

    def __getattribute__(self, name: str) -> Any:
        """Expose optional capacity readers only when the original has them.

        The frozen composer uses attribute presence to choose between its
        multi-capacity and legacy exact-role paths. Advertising an adapter
        method that the original repository lacks would incorrectly change a
        valid legacy denial into an authority outage.
        """

        if name in {"resolve_current_business_role", "resolve_all_business_roles"}:
            repository = object.__getattribute__(self, "_repository")
            if not callable(getattr(repository, name, None)):
                raise AttributeError(name)
        return object.__getattribute__(self, name)

    def _read(self, method: str, *arguments: str, session: Any = None) -> object:
        resolver = getattr(self._repository, method)
        if session is not None:
            return resolver(*arguments, session=session)
        key = (self._purpose, method, arguments)
        if key in self._evidence.values:
            return self._evidence.values[key]
        value = resolver(*arguments)
        self._evidence.values[key] = value
        return value

    def resolve(
        self,
        principal_id: str,
        tenant_id: str | None = None,
        role_id: str | None = None,
        *,
        session: Any = None,
    ) -> object:
        """Resolve one exact current evidence record with session preservation."""

        arguments = tuple(
            value for value in (principal_id, tenant_id, role_id) if value is not None
        )
        return self._read("resolve", *arguments, session=session)

    def resolve_current_business_role(
        self, principal_id: str, tenant_id: str, *, session: Any = None
    ) -> object:
        """Resolve legacy single-capacity evidence without widening its scope."""

        return self._read(
            "resolve_current_business_role", principal_id, tenant_id, session=session
        )

    def resolve_all_business_roles(
        self, principal_id: str, tenant_id: str, *, session: Any = None
    ) -> object:
        """Resolve all exact current capacities through the original reader."""

        return self._read(
            "resolve_all_business_roles", principal_id, tenant_id, session=session
        )

    def __getattr__(self, name: str) -> Any:
        """Expose non-resolution repository metadata without adding authority."""

        return getattr(self._repository, name)


def _request_scoped_evidence(
    request: Request,
) -> _RequestScopedAuthorityEvidence:
    """Return the one non-persistent authority-evidence cache for a request.

    Request state is discarded by ASGI at request completion. The cache is not
    process-global, cross-request, durable, or a replacement for currentness
    or revocation checks.
    """

    current = getattr(request.state, "wilsy_tenant_authority_evidence", None)
    if isinstance(current, _RequestScopedAuthorityEvidence):
        return current
    created = _RequestScopedAuthorityEvidence(values={})
    request.state.wilsy_tenant_authority_evidence = created
    return created


def _request_scoped_reader(
    *,
    request: Request,
    purpose: str,
    repository: Any,
) -> _RequestScopedEvidenceReader:
    """Bind an existing authority repository to the active request only."""

    return _RequestScopedEvidenceReader(
        purpose=purpose,
        repository=repository,
        evidence=_request_scoped_evidence(request),
    )


def get_role_assignment_repository() -> _TenantAuthorityRoleReader:
    """Compose separate existing business-role and authorization-role stores."""

    return _TenantAuthorityRoleReader(
        authorization_repository=_get_role_assignment_repository(),
        business_repository=TenantBusinessRoleRepository(),
    )


def _require_active_hr_product_entitlement(tenant_id: str) -> None:
    """Require exact active D22B2 HR product truth for a customer HR request.

    This function performs one read-only snapshot transaction against the
    canonical entitlement history/current-pointer registry. It never derives
    IAM, membership, role, WILSY employer, payroll, or commercial truth.
    Missing or terminal entitlement is denied; registry or transport faults
    remain unavailable.
    """
    client = get_client()
    database = get_database()
    if client is None or database is None:
        raise WilsyAPIException(
            "HR product entitlement authority unavailable.",
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
        )

    entitlement_id = derive_tenant_product_entitlement_id(
        tenant_id, TenantProductId.HR
    )
    try:
        with client.start_session() as session:
            with session.start_transaction(
                read_concern=ReadConcern("snapshot"),
                read_preference=ReadPreference.PRIMARY,
            ):
                entitlement = get_current_product_entitlement(
                    tenant_id,
                    entitlement_id,
                    database.get_collection(
                        PRODUCT_ENTITLEMENT_HISTORY_COLLECTION
                    ),
                    database.get_collection(
                        PRODUCT_ENTITLEMENT_CURRENT_COLLECTION
                    ),
                    session=session,
                )
    except TenantProductEntitlementRegistryNotFoundError as error:
        raise ForbiddenOperationException(
            "An active HR product entitlement is required."
        ) from error
    except TenantProductEntitlementRegistryError as error:
        raise WilsyAPIException(
            "HR product entitlement authority unavailable.",
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
        ) from error
    except Exception as error:
        raise WilsyAPIException(
            "HR product entitlement authority unavailable.",
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
        ) from error

    if (
        entitlement.tenant_id != tenant_id
        or entitlement.entitlement_id != entitlement_id
        or entitlement.product_id is not TenantProductId.HR
        or entitlement.lifecycle_state is not TenantProductEntitlementState.ACTIVE
    ):
        raise ForbiddenOperationException(
            "An active HR product entitlement is required."
        )


class RequireTenantAuthorization:
    """Require one canonical permission-operation pair for one exact tenant.

    Authentication remains owned by ``get_current_identity``. This dependency
    passes the authenticated principal and explicit tenant scope to the existing
    ``authorize_tenant_operation`` composer. It observes terminal denials and
    outages only after that canonical boundary has classified the result.
    """

    def __init__(
        self,
        permission_id: str,
        operation: str,
        *,
        platform_employer_permission_id: str | None = None,
        platform_employer_operation: str | None = None,
        preflight_workforce_denial: bool = False,
    ) -> None:
        """Freeze customer IAM and optional exact-WILSY employer pair metadata.

        The optional employer pair is selected only for the canonical WILSY
        company tenant. Both pairs still pass through the same current-truth
        resolver, membership check, business-role eligibility and durable role
        assignment lookup.
        """
        base_pair = (permission_id, operation)
        employer_pair = (
            platform_employer_permission_id,
            platform_employer_operation,
        )
        if not all(
            isinstance(value, str) and value and value == value.strip()
            for value in base_pair
        ):
            raise ValueError(
                "permission_id and operation must be non-empty trimmed strings"
            )
        if (employer_pair[0] is None) != (employer_pair[1] is None):
            raise ValueError(
                "platform-employer permission and operation must be supplied together"
            )
        if employer_pair[0] is not None and not all(
            isinstance(value, str)
            and value
            and value == value.strip()
            for value in employer_pair
        ):
            raise ValueError(
                "platform-employer permission and operation must be non-empty strings"
            )
        if employer_pair[0] is not None and not cast(
            str, employer_pair[0]
        ).startswith("platform_employer:"):
            raise ValueError(
                "platform-employer permission must use its canonical namespace"
            )
        self.permission_id = permission_id
        self.operation = operation
        self.platform_employer_permission_id = platform_employer_permission_id
        self.platform_employer_operation = platform_employer_operation
        self._preflight_workforce_denial = preflight_workforce_denial is True

    async def __call__(
        self,
        request: Request,
        identity: SovereignIdentity = Depends(get_current_identity),
        tenant_id: str | None = Header(default=None, alias="X-Tenant-ID"),
        principal_repository: Any = Depends(get_principal_authority_repository),
        membership_repository: Any = Depends(get_tenant_membership_repository),
        role_assignment_repository: Any = Depends(get_role_assignment_repository),
    ) -> TenantAuthorizationContext:
        """Return existing authorized context or preserve bounded 403/503 truth."""

        timing_correlation = establish_request_timing_correlation(request)
        correlation_id = _new_correlation_id()
        observed_tenant = (
            tenant_id
            if isinstance(tenant_id, str) and tenant_id
            else "UNRESOLVED_TENANT_SCOPE"
        )
        if (
            not isinstance(tenant_id, str)
            or not tenant_id
            or tenant_id != tenant_id.strip()
        ):
            _observe_terminal(
                outcome="AUTHORIZATION_DENIED",
                reason=TenantAuthorizationReason.INVALID_INPUT,
                tenant_id=observed_tenant,
                principal_id=identity.identity_id,
                correlation_id=correlation_id,
                http_status=status.HTTP_403_FORBIDDEN,
            )
            raise ForbiddenOperationException("Tenant scope is required.")

        permission_id = self.permission_id
        operation = self.operation
        if (
            tenant_id == WILSY_COMPANY_TENANT_ID
            and self.platform_employer_permission_id is not None
            and self.platform_employer_operation is not None
        ):
            permission_id = self.platform_employer_permission_id
            operation = self.platform_employer_operation
        timing_label = _timing_admission_label(operation)
        scoped_principal_repository = _request_scoped_reader(
            request=request,
            purpose="PRINCIPAL",
            repository=principal_repository,
        )
        scoped_membership_repository = _request_scoped_reader(
            request=request,
            purpose="MEMBERSHIP",
            repository=membership_repository,
        )
        scoped_role_repository = _request_scoped_reader(
            request=request,
            purpose="ROLE",
            repository=role_assignment_repository,
        )

        selected_business_role = None
        if identity.principal_scope == "GLOBAL":
            if len(identity.roles) != 1:
                raise ForbiddenOperationException("Tenant authorization denied.")
            selected_business_role = identity.roles[0]

        workforce_required = False
        try:
            workforce_required = (
                permission_metadata(permission_id).workforce_currentness_required
                is True
            )
        except ValueError:
            workforce_required = False

        authorization_submitted_ns = time.perf_counter_ns()
        authorization_execution_started_ns = [0]
        authorization_outcome = "UNAVAILABLE"

        def evaluate_authority() -> TenantAuthorizationDecision:
            authorization_execution_started_ns[0] = time.perf_counter_ns()
            if workforce_required:
                if self._preflight_workforce_denial:
                    # The canonical composer resolves principal, membership,
                    # selected business role and operation eligibility before
                    # workforce currentness. Optional source admission may
                    # classify an already role-ineligible caller without
                    # opening a workforce dependency. A caller that could
                    # otherwise proceed still requires the same transaction-
                    # bound workforce evidence below.
                    preflight_started_ns = time.perf_counter_ns()
                    preflight_outcome = "UNAVAILABLE"
                    try:
                        preflight = authorize_tenant_operation(
                            principal_id=identity.identity_id,
                            tenant_id=tenant_id,
                            permission_id=permission_id,
                            operation=operation,
                            principal_repository=scoped_principal_repository,
                            membership_repository=scoped_membership_repository,
                            business_role_repository=scoped_role_repository,
                            role_assignment_repository=scoped_role_repository,
                            selected_business_role=selected_business_role,
                        )
                        preflight_outcome = (
                            "AUTHORIZED"
                            if preflight.authorized
                            else _decision_class(preflight.reason)
                        )
                    finally:
                        emit_request_timing(
                            stage=f"TENANT_{timing_label}_HR_PREFLIGHT",
                            outcome=preflight_outcome,
                            started_ns=preflight_started_ns,
                            correlation=timing_correlation,
                        )
                    if (
                        preflight.reason
                        is not TenantAuthorizationReason.WORKFORCE_AUTHORITY_UNAVAILABLE
                    ):
                        return preflight
                client = get_client()
                database = get_database()
                if client is None or database is None:
                    _observe_terminal(
                        outcome="DEPENDENCY_UNAVAILABLE",
                        reason=TenantAuthorizationReason.WORKFORCE_AUTHORITY_UNAVAILABLE,
                        tenant_id=tenant_id,
                        principal_id=identity.identity_id,
                        correlation_id=correlation_id,
                        http_status=status.HTTP_503_SERVICE_UNAVAILABLE,
                    )
                    raise WilsyAPIException(
                        "Authorization authority unavailable.",
                        status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                    )
                workforce_collection = database[WORKFORCE_RELATIONSHIP_COLLECTION]
                with client.start_session() as session:
                    with session.start_transaction():
                        return authorize_tenant_operation(
                            principal_id=identity.identity_id,
                            tenant_id=tenant_id,
                            permission_id=permission_id,
                            operation=operation,
                            principal_repository=scoped_principal_repository,
                            membership_repository=scoped_membership_repository,
                            business_role_repository=scoped_role_repository,
                            role_assignment_repository=scoped_role_repository,
                            session=session,
                            workforce_relationship_collection=workforce_collection,
                            selected_business_role=selected_business_role,
                        )
            else:
                return authorize_tenant_operation(
                    principal_id=identity.identity_id,
                    tenant_id=tenant_id,
                    permission_id=permission_id,
                    operation=operation,
                    principal_repository=scoped_principal_repository,
                    membership_repository=scoped_membership_repository,
                    business_role_repository=scoped_role_repository,
                    role_assignment_repository=scoped_role_repository,
                    selected_business_role=selected_business_role,
                )

        try:
            decision = await run_in_threadpool(evaluate_authority)
            authorization_outcome = (
                "AUTHORIZED"
                if decision.authorized
                else _decision_class(decision.reason)
            )
        except (ForbiddenOperationException, WilsyAPIException):
            raise
        except Exception as error:
            _observe_terminal(
                outcome="DEPENDENCY_UNAVAILABLE",
                reason=(
                    TenantAuthorizationReason.WORKFORCE_AUTHORITY_UNAVAILABLE
                    if workforce_required
                    else None
                ),
                tenant_id=tenant_id,
                principal_id=identity.identity_id,
                correlation_id=correlation_id,
                http_status=status.HTTP_503_SERVICE_UNAVAILABLE,
            )
            raise WilsyAPIException(
                "Authorization authority unavailable.",
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            ) from error
        finally:
            execution_started_ns = authorization_execution_started_ns[0]
            if execution_started_ns:
                completed_ns = time.perf_counter_ns()
                emit_request_timing(
                    stage=f"TENANT_{timing_label}_THREADPOOL_QUEUE",
                    outcome=authorization_outcome,
                    started_ns=authorization_submitted_ns,
                    correlation=timing_correlation,
                    duration_ms=(
                        execution_started_ns - authorization_submitted_ns
                    ) / 1_000_000,
                )
                emit_request_timing(
                    stage=f"TENANT_{timing_label}_CURRENTNESS",
                    outcome=authorization_outcome,
                    started_ns=execution_started_ns,
                    correlation=timing_correlation,
                    duration_ms=(completed_ns - execution_started_ns) / 1_000_000,
                )

        if (
            decision.authorized is True
            and decision.reason is TenantAuthorizationReason.AUTHORIZED
        ):
            if permission_id.startswith("hr:"):
                entitlement_started_ns = time.perf_counter_ns()
                entitlement_outcome = "UNAVAILABLE"
                try:
                    await run_in_threadpool(
                        _require_active_hr_product_entitlement,
                        tenant_id,
                    )
                    entitlement_outcome = "ACTIVE"
                except (ForbiddenOperationException, WilsyAPIException):
                    raise
                except Exception as error:
                    raise WilsyAPIException(
                        "HR product entitlement authority unavailable.",
                        status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                    ) from error
                finally:
                    emit_request_timing(
                        stage=f"TENANT_{timing_label}_HR_ENTITLEMENT",
                        outcome=entitlement_outcome,
                        started_ns=entitlement_started_ns,
                        correlation=timing_correlation,
                    )
            return TenantAuthorizationContext(identity, tenant_id, decision)
        if decision.authorized is True or decision.reason is TenantAuthorizationReason.AUTHORIZED:
            _observe_terminal(
                outcome="DEPENDENCY_UNAVAILABLE",
                reason=None,
                tenant_id=tenant_id,
                principal_id=identity.identity_id,
                correlation_id=correlation_id,
                http_status=status.HTTP_503_SERVICE_UNAVAILABLE,
            )
            raise WilsyAPIException(
                "Authorization decision unavailable.",
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            )
        if decision.reason in _UNAVAILABLE:
            _observe_terminal(
                outcome="DEPENDENCY_UNAVAILABLE",
                reason=decision.reason,
                tenant_id=tenant_id,
                principal_id=identity.identity_id,
                correlation_id=correlation_id,
                http_status=status.HTTP_503_SERVICE_UNAVAILABLE,
            )
            raise WilsyAPIException(
                "Authorization authority unavailable.",
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            )
        if decision.reason in _DENIED:
            _observe_terminal(
                outcome="AUTHORIZATION_DENIED",
                reason=decision.reason,
                tenant_id=tenant_id,
                principal_id=identity.identity_id,
                correlation_id=correlation_id,
                http_status=status.HTTP_403_FORBIDDEN,
            )
            raise ForbiddenOperationException("Tenant authorization denied.")
        _observe_terminal(
            outcome="DEPENDENCY_UNAVAILABLE",
            reason=None,
            tenant_id=tenant_id,
            principal_id=identity.identity_id,
            correlation_id=correlation_id,
            http_status=status.HTTP_503_SERVICE_UNAVAILABLE,
        )
        raise WilsyAPIException(
            "Authorization decision unavailable.",
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
        )


class OptionalTenantAuthorization:
    """Resolve one source's existing IAM decision without failing unrelated sources.

    Only a canonical authorization denial is represented as None so the
    caller can omit that source. Authentication failures and authorization
    dependency outages remain exceptions and therefore fail the whole request.
    This adapter creates no permission, role, membership, or capacity authority.
    """

    def __init__(
        self,
        permission_id: str,
        operation: str,
        *,
        platform_employer_permission_id: str | None = None,
        platform_employer_operation: str | None = None,
    ) -> None:
        """Freeze optional admission over the canonical required IAM contract.

        The optional pair is deliberately delegated to
        :class:`RequireTenantAuthorization`; it therefore uses precisely the
        same canonical-WILSY selection, identity currentness, membership,
        business-capacity, role-assignment and customer HR-entitlement gates.
        Only an already-classified authorization denial becomes ``None``.
        """
        self._required = RequireTenantAuthorization(
            permission_id,
            operation,
            platform_employer_permission_id=platform_employer_permission_id,
            platform_employer_operation=platform_employer_operation,
            preflight_workforce_denial=True,
        )

    async def __call__(
        self,
        request: Request,
        identity: SovereignIdentity = Depends(get_current_identity),
        tenant_id: str | None = Header(default=None, alias="X-Tenant-ID"),
        principal_repository: Any = Depends(get_principal_authority_repository),
        membership_repository: Any = Depends(get_tenant_membership_repository),
        role_assignment_repository: Any = Depends(get_role_assignment_repository),
    ) -> TenantAuthorizationContext | None:
        try:
            return await self._required(
                request,
                identity,
                tenant_id,
                principal_repository,
                membership_repository,
                role_assignment_repository,
            )
        except ForbiddenOperationException:
            # A source denial is intentionally non-disclosing and does not
            # prevent the principal from seeing other independently admitted
            # work sources. WilsyAPIException (including 503) is not swallowed.
            return None


__all__ = [
    "VERSION",
    "TenantAuthorizationContext",
    "RequireTenantAuthorization",
    "OptionalTenantAuthorization",
]


# ARTIFACT: tenant_authorization_http.py
# VERSION: v1.10.0-REQUEST-SCOPED-EVIDENCE-READS
# AUTHORITY BOUNDARY: existing HTTP IAM composition plus independent D22B2 customer HR product admission and bounded post-decision observation; no grant, assignment, workforce, payroll or settlement truth ownership
# TENANT POSTURE: platform-employer pairs are canonical-WILSY-only; customer HR requires exact-tenant ACTIVE entitlement plus current IAM
# FAIL-CLOSED POSTURE: only canonical AUTHORIZED plus required active product entitlement succeeds; denied, unavailable, inconsistent and unknown results remain bounded
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS remains exclusive
# END OF WILSY OS SOVEREIGN ARTIFACT
