"""WILSY OS C1E governed advisory product service.

TITLE: WILSY AI Legal Next-Action Advisory Service
VERSION: v1.0.1-C1E-R1D
AUTHORITY: Wilsy OS Core Governance; server-owned advisory composition
EPITOME: Resolves completed C1C/L7B evidence, rechecks current legal access,
         recomputes the current projection, and persists one immutable C1D
         advisory through a caller-session transaction owned by this service.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tools/eos/intelligence/wilsy_ai_advisory_service.py
COLLABORATION / OWNERSHIP: C1C and L7B supply evidence; C1D registry stores
                            advisory facts; the router owns transport only.
CERTIFICATION / UPDATE DATE: 2026-09-17
CHANGELOG: v1.0.1-C1E-R1D repairs exact replay ordering so an unchanged source
           snapshot is reconciled before predecessor supersession resolution;
           tenant-scoped generation, stale-source rejection, and bounded
           transaction/reconciliation semantics remain fail-closed.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2.
SECURITY / PRIVACY POSTURE: Caller input is limited to orchestration_id; raw
                            legal projections and fingerprints never leave the service.
TENANT BOUNDARY: Every evidence lookup and write uses the authenticated tenant.
AUTHORITY BOUNDARY: Review-only advisory evidence; no legal command, execution,
                    payment, settlement, model, or provider authority.
FINANCIAL AUTHORITY BOUNDARY: Kennel EOS exclusively owns financial execution.
"""
from __future__ import annotations

import inspect
import hashlib
import json
from collections.abc import Mapping
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any, Callable, Final

from tools.eos.api.tenant_authorization_http import TenantAuthorizationContext
from tools.eos.auth.authentication import get_principal_authority_repository
from tools.eos.auth.authorization import get_role_assignment_repository
from tools.eos.auth.tenant_access import get_tenant_membership_repository
from tools.eos.auth.tenant_authorization import TenantAuthorizationReason, authorize_tenant_operation
from tools.eos.intelligence.adapters.legal_operations_advisory_adapter import (
    LegalOperationsAdvisoryAdapter,
    LegalOperationsAdvisoryError,
)
from tools.eos.intelligence.domain.ai_tool_orchestration import OrchestrationPhase
from tools.eos.intelligence.domain.legal_ai_gateway import TOOL_CONTRACTS
from tools.eos.intelligence.domain.legal_ai_read_adapter import LegalAIReadAdapter
from tools.eos.intelligence.domain.next_best_action_advisory import NextBestActionAdvisory
from tools.eos.intelligence.registry.ai_tool_orchestration_registry import (
    AIToolOrchestrationRegistry,
    COLLECTION as ORCHESTRATION_COLLECTION,
)
from tools.eos.intelligence.registry.legal_ai_tool_invocation_registry import (
    COLLECTION as INVOCATION_COLLECTION,
    LegalAIToolInvocationRegistry,
)
from tools.eos.intelligence.registry.next_best_action_advisory_registry import (
    COLLECTION as ADVISORY_COLLECTION,
    NextBestActionAdvisoryConflictError,
    NextBestActionAdvisoryRegistry,
    NextBestActionAdvisoryRegistryError,
)

VERSION: Final[str] = "v1.0.1-C1E-R1D"
GENERATE_OPERATION: Final[str] = "wilsy_ai_legal_advisory_generate"
READ_OPERATION: Final[str] = "wilsy_ai_legal_advisory_read"


class WilsyAIAdvisoryServiceError(ValueError):
    """Stable non-sensitive service error code translated by the router."""

    def __init__(self, code: str) -> None:
        self.code = code
        super().__init__(code)


@dataclass(frozen=True, slots=True)
class AdvisoryServiceResult:
    """Internal result preserving whether persistence was a verified replay."""

    advisory: NextBestActionAdvisory
    replay: bool

    def to_public_dict(self, *, status: str = "CURRENT", superseded_by: str | None = None) -> dict[str, object]:
        """Return the deliberately redacted public v1 response projection."""
        recommendation = self.advisory.recommendation
        return {
            "advisory_id": self.advisory.advisory_id,
            "scope_ref": self.advisory.scope_ref,
            "title": recommendation.action_title,
            "rationale": recommendation.rationale,
            "confidence_score": recommendation.confidence_score,
            "confidence_basis": recommendation.confidence_basis,
            "risk_level": recommendation.risk_level,
            "generated_at": self.advisory.generated_at,
            "status": status,
            "superseded_by_advisory_id": superseded_by,
        }


def _await(value: Any) -> Any:
    """Marker used by tests to identify potentially asynchronous adapters."""
    return value


def _error_code(error: BaseException) -> str:
    """Read stable registry codes without requiring registry exception fields."""
    return str(getattr(error, "code", "") or (error.args[0] if error.args else ""))


class WilsyAIAdvisoryService:
    """Compose C1E advisories while owning sessions and whole transactions."""

    __slots__ = (
        "_database", "_session_factory", "_orchestrations", "_invocations",
        "_advisories", "_legal_reader", "_adapter", "_authority_checker",
    )

    def __init__(
        self,
        *,
        database: Any | None = None,
        session_factory: Callable[[], Any] | None = None,
        orchestration_registry: Any | None = None,
        invocation_registry: Any | None = None,
        advisory_registry: Any | None = None,
        legal_reader: Any | None = None,
        adapter: Any | None = None,
        authority_checker: Callable[..., Any] | None = None,
    ) -> None:
        self._database = database
        self._session_factory = session_factory
        self._orchestrations = orchestration_registry
        self._invocations = invocation_registry
        self._advisories = advisory_registry
        self._legal_reader = legal_reader or LegalAIReadAdapter()
        self._adapter = adapter or LegalOperationsAdvisoryAdapter()
        self._authority_checker = authority_checker

    def _wire(self) -> tuple[Any, Any, Any]:
        if self._orchestrations is not None and self._invocations is not None and self._advisories is not None:
            if self._session_factory is None:
                raise WilsyAIAdvisoryServiceError("C1E_SESSION_FACTORY_UNAVAILABLE")
            return self._orchestrations, self._invocations, self._advisories
        try:
            from tools.eos.kernel.db import get_client, get_database
            database = self._database or get_database()
            client = get_client()
        except Exception as error:
            raise WilsyAIAdvisoryServiceError("C1E_PERSISTENCE_UNAVAILABLE") from error
        if database is None or client is None:
            raise WilsyAIAdvisoryServiceError("C1E_PERSISTENCE_UNAVAILABLE")
        self._database = database
        self._session_factory = self._session_factory or client.start_session
        self._orchestrations = AIToolOrchestrationRegistry(database[ORCHESTRATION_COLLECTION])
        self._invocations = LegalAIToolInvocationRegistry(database[INVOCATION_COLLECTION])
        self._advisories = NextBestActionAdvisoryRegistry(database[ADVISORY_COLLECTION])
        return self._orchestrations, self._invocations, self._advisories

    @staticmethod
    def _transaction(session: Any) -> None:
        starter = getattr(session, "start_transaction", None)
        if callable(starter):
            starter()

    @staticmethod
    def _commit(session: Any) -> None:
        commit = getattr(session, "commit_transaction", None)
        if callable(commit):
            commit()

    @staticmethod
    def _abort(session: Any) -> None:
        abort = getattr(session, "abort_transaction", None)
        if callable(abort):
            abort()

    @staticmethod
    def _end(session: Any) -> None:
        end = getattr(session, "end_session", None)
        if callable(end):
            end()

    async def _read_projection(self, *, root: Any, context: TenantAuthorizationContext, session: Any) -> Mapping[str, object]:
        contract = TOOL_CONTRACTS.get(root.tool_identity or "")
        if contract is None or not root.resource_identity:
            raise WilsyAIAdvisoryServiceError("C1E_EVIDENCE_CORRUPT")
        if self._authority_checker is not None:
            decision = self._authority_checker(contract=contract, context=context, session=session)
            if inspect.isawaitable(decision):
                decision = await decision
            if decision is not True:
                raise WilsyAIAdvisoryServiceError("C1E_LEGAL_AUTHORITY_DENIED")
        else:
            try:
                decision = authorize_tenant_operation(
                    principal_id=context.identity.identity_id,
                    tenant_id=context.tenant_id,
                    permission_id=contract.underlying_permission,
                    operation={
                        "legal_operations:instruction:read": "legal_instruction_read",
                        "legal_operations:attempt:read": "legal_attempt_read",
                        "legal_operations:return:read": "legal_return_read",
                        "legal_operations:billing:read": "legal_billing_read",
                        "legal_operations:invoice:read": "legal_invoice_read",
                    }.get(contract.underlying_permission, "legal_attempt_read"),
                    principal_repository=get_principal_authority_repository(),
                    membership_repository=get_tenant_membership_repository(),
                    role_assignment_repository=get_role_assignment_repository(),
                    business_role_repository=get_role_assignment_repository(),
                    session=session,
                )
            except Exception as error:
                raise WilsyAIAdvisoryServiceError("C1E_LEGAL_AUTHORITY_UNAVAILABLE") from error
            if not decision.authorized or decision.reason is not TenantAuthorizationReason.AUTHORIZED:
                raise WilsyAIAdvisoryServiceError("C1E_LEGAL_AUTHORITY_DENIED")
        collections = self._collections()
        value = self._legal_reader.read(contract=contract, resource_identity=root.resource_identity, context=context, collections=collections)
        if inspect.isawaitable(value):
            value = await value
        if not isinstance(value, Mapping):
            raise WilsyAIAdvisoryServiceError("C1E_SOURCE_PROJECTION_INVALID")
        return value

    def _collections(self) -> dict[str, Any]:
        if self._database is None:
            return {}
        return {"lifecycle": self._database["legal_operations_lifecycle_facts"], "tariff": self._database["process_service_tariff_assessments"], "eligibility": self._database["process_service_billing_eligibilities"], "invoice": self._database["client_invoices"], "issuance": self._database["process_service_client_invoice_issuances"]}

    async def generate(self, *, orchestration_id: str, context: TenantAuthorizationContext, generated_at: datetime | str | None = None) -> AdvisoryServiceResult:
        """Generate or exactly replay a tenant-scoped advisory from current evidence."""
        if not isinstance(orchestration_id, str) or not orchestration_id or orchestration_id != orchestration_id.strip():
            raise WilsyAIAdvisoryServiceError("C1E_ORCHESTRATION_ID_INVALID")
        if not isinstance(context, TenantAuthorizationContext):
            raise WilsyAIAdvisoryServiceError("C1E_AUTHORITY_REQUIRED")
        orchestrations, invocations, advisories = self._wire()
        if self._session_factory is None:
            raise WilsyAIAdvisoryServiceError("C1E_SESSION_FACTORY_UNAVAILABLE")
        session = self._session_factory()
        self._transaction(session)
        try:
            try:
                root = orchestrations.get(tenant_id=context.tenant_id, orchestration_id=orchestration_id, session=session)
            except Exception as error:
                code = _error_code(error)
                raise WilsyAIAdvisoryServiceError("C1E_ORCHESTRATION_NOT_FOUND" if "NOT_FOUND" in code else "C1E_EVIDENCE_CORRUPT") from error
            if root.phase is not OrchestrationPhase.COMPLETED or root.outcome != "TOOL_ASSISTED":
                raise WilsyAIAdvisoryServiceError("C1E_TOOL_ASSISTED_REQUIRED")
            if not root.tool_invocation_id or not root.tool_identity or not root.resource_identity:
                raise WilsyAIAdvisoryServiceError("C1E_EVIDENCE_CORRUPT")
            try:
                invocation = invocations.get(tenant_id=context.tenant_id, invocation_id=root.tool_invocation_id, session=session)
            except Exception as error:
                raise WilsyAIAdvisoryServiceError("C1E_EVIDENCE_CORRUPT") from error
            if invocation.correlation_id != root.orchestration_id or invocation.tool_identity != root.tool_identity:
                raise WilsyAIAdvisoryServiceError("C1E_EVIDENCE_CORRUPT")
            result = await self._read_projection(root=root, context=context, session=session)
            try:
                current = await self._read_projection(root=root, context=context, session=session)
                if dict(current) != dict(result):
                    raise WilsyAIAdvisoryServiceError("C1E_SOURCE_SNAPSHOT_STALE")
            except WilsyAIAdvisoryServiceError:
                raise
            try:
                candidate = self._adapter.build(
                    tenant_id=context.tenant_id,
                    scope_ref=root.orchestration_id,
                    root=root,
                    invocation=invocation,
                    result=result,
                    generated_at=generated_at,
                    supersedes_advisory_id=None,
                )
            except LegalOperationsAdvisoryError as error:
                code = getattr(error, "code", "C1E_EVIDENCE_CORRUPT")
                raise WilsyAIAdvisoryServiceError("C1E_SOURCE_SNAPSHOT_STALE" if "FINGERPRINT" in code else code) from error
            try:
                prior = advisories.get(tenant_id=context.tenant_id, advisory_id=candidate.advisory_id, session=session)
            except NextBestActionAdvisoryRegistryError as error:
                if _error_code(error) != "C1D_NOT_FOUND":
                    raise WilsyAIAdvisoryServiceError("C1E_EVIDENCE_CORRUPT") from error
                prior = None
            if prior is not None:
                if prior.to_dict() != candidate.to_dict():
                    raise WilsyAIAdvisoryServiceError("C1E_EVIDENCE_CORRUPT")
                self._commit(session)
                return AdvisoryServiceResult(prior, True)
            try:
                predecessor = advisories.get_current_by_scope(
                    tenant_id=context.tenant_id,
                    scope_ref=root.orchestration_id,
                    policy_id="WILSY_AI_LEGAL_NEXT_BEST_ACTION_REVIEW_POLICY",
                    policy_version="v1",
                    session=session,
                )
            except NextBestActionAdvisoryRegistryError as error:
                if _error_code(error) == "C1D_CURRENT_NOT_FOUND":
                    predecessor = None
                else:
                    raise WilsyAIAdvisoryServiceError("C1E_EVIDENCE_CORRUPT") from error
            except WilsyAIAdvisoryServiceError:
                raise
            try:
                advisory = candidate if predecessor is None else self._adapter.build(
                    tenant_id=context.tenant_id,
                    scope_ref=root.orchestration_id,
                    root=root,
                    invocation=invocation,
                    result=result,
                    generated_at=generated_at,
                    supersedes_advisory_id=predecessor.advisory_id,
                )
            except LegalOperationsAdvisoryError as error:
                code = getattr(error, "code", "C1E_EVIDENCE_CORRUPT")
                raise WilsyAIAdvisoryServiceError("C1E_SOURCE_SNAPSHOT_STALE" if "FINGERPRINT" in code else code) from error
            persisted = advisories.create_or_replay(advisory, session=session)
            self._commit(session)
            return AdvisoryServiceResult(persisted, False)
        except WilsyAIAdvisoryServiceError:
            self._abort(session)
            raise
        except NextBestActionAdvisoryConflictError as error:
            self._abort(session)
            raise WilsyAIAdvisoryServiceError("C1E_SUPERSESSION_CONFLICT") from error
        except Exception as error:
            self._abort(session)
            raise WilsyAIAdvisoryServiceError("C1E_ADVISORY_RECONCILIATION_REQUIRED") from error
        finally:
            self._end(session)

    async def get(self, *, advisory_id: str, context: TenantAuthorizationContext) -> tuple[AdvisoryServiceResult, str, str | None]:
        """Retrieve a tenant advisory and derive CURRENT/STALE without mutation."""
        if not isinstance(advisory_id, str) or not advisory_id.strip():
            raise WilsyAIAdvisoryServiceError("C1E_ADVISORY_NOT_FOUND")
        if not isinstance(context, TenantAuthorizationContext):
            raise WilsyAIAdvisoryServiceError("C1E_AUTHORITY_REQUIRED")
        orchestrations, invocations, advisories = self._wire()
        if self._session_factory is None:
            raise WilsyAIAdvisoryServiceError("C1E_SESSION_FACTORY_UNAVAILABLE")
        session = self._session_factory(); self._transaction(session)
        try:
            try:
                advisory = advisories.get(tenant_id=context.tenant_id, advisory_id=advisory_id, session=session)
            except NextBestActionAdvisoryRegistryError as error:
                if "NOT_FOUND" in str(error):
                    raise WilsyAIAdvisoryServiceError("C1E_ADVISORY_NOT_FOUND") from error
                raise WilsyAIAdvisoryServiceError("C1E_PERSISTENCE_UNAVAILABLE") from error
            references = {item.evidence_type: item for item in advisory.source_references}
            root_reference = references.get("ORCHESTRATION_ROOT")
            invocation_reference = references.get("LEGAL_TOOL_INVOCATION")
            result_reference = references.get("LEGAL_TOOL_RESULT")
            if root_reference is None or invocation_reference is None or result_reference is None:
                raise WilsyAIAdvisoryServiceError("C1E_EVIDENCE_CORRUPT")
            try:
                root = orchestrations.get(tenant_id=context.tenant_id, orchestration_id=root_reference.evidence_identity, session=session)
                invocation = invocations.get(tenant_id=context.tenant_id, invocation_id=invocation_reference.evidence_identity, session=session)
            except Exception as error:
                raise WilsyAIAdvisoryServiceError("C1E_EVIDENCE_CORRUPT") from error
            if root.fingerprint != root_reference.evidence_fingerprint or invocation.fingerprint != invocation_reference.evidence_fingerprint:
                raise WilsyAIAdvisoryServiceError("C1E_SOURCE_SNAPSHOT_STALE")
            if (root.orchestration_id != advisory.scope_ref or root.orchestration_id != invocation.correlation_id
                    or root.tool_invocation_id != invocation.invocation_id
                    or root.tool_identity != invocation.tool_identity
                    or invocation.result_reference != result_reference.evidence_identity):
                raise WilsyAIAdvisoryServiceError("C1E_EVIDENCE_CORRUPT")
            current_result = await self._read_projection(root=root, context=context, session=session)
            if not isinstance(current_result, Mapping):
                raise WilsyAIAdvisoryServiceError("C1E_SOURCE_PROJECTION_INVALID")
            current_fingerprint = hashlib.sha3_512(json.dumps(dict(current_result), sort_keys=True, separators=(",", ":"), default=str).encode()).hexdigest()
            if current_fingerprint != invocation.result_fingerprint or current_fingerprint != result_reference.evidence_fingerprint:
                raise WilsyAIAdvisoryServiceError("C1E_SOURCE_SNAPSHOT_STALE")
            projection = advisories.get_status(tenant_id=context.tenant_id, advisory_id=advisory_id, session=session)
            self._commit(session)
            return AdvisoryServiceResult(projection.advisory, True), projection.disposition, projection.superseded_by_advisory_id
        except WilsyAIAdvisoryServiceError:
            self._abort(session); raise
        except NextBestActionAdvisoryRegistryError as error:
            self._abort(session)
            raise WilsyAIAdvisoryServiceError("C1E_ADVISORY_RECONCILIATION_REQUIRED") from error
        except Exception as error:
            self._abort(session)
            raise WilsyAIAdvisoryServiceError("C1E_ADVISORY_RECONCILIATION_REQUIRED") from error
        finally:
            self._end(session)


__all__ = ["VERSION", "GENERATE_OPERATION", "READ_OPERATION", "WilsyAIAdvisoryServiceError", "AdvisoryServiceResult", "WilsyAIAdvisoryService"]

# ARTIFACT: wilsy_ai_advisory_service.py
# VERSION: v1.0.1-C1E-R1D
# AUTHORITY BOUNDARY: server-owned review advisory composition only
# TENANT POSTURE: exact tenant-scoped root, invocation, projection and registry access
# FAIL-CLOSED POSTURE: stale, corrupt, foreign, divergent and ambiguous evidence rejects
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively
# END OF WILSY OS SOVEREIGN ARTIFACT
