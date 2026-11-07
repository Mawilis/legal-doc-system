"""WILSY OS sovereign Python API server composition root.

TITLE: WILSY OS EOS Kernel API Server Factory
VERSION: v1.41.0-GLOBAL-MFA-ENROLLMENT-AND-LEGACY-MIGRATION
AUTHORITY: Wilsy OS Core Governance
EPITOME: Mount sovereign Python API authorities, including the authenticated
         practitioner-binding command transport, and hold that transport
         fail-closed until its access, binding, and conflict-disposition
         persistence indexes complete startup without creating identity,
         matter-content, ethical-wall, AI, commercial, payment, or settlement
         authority.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tools/eos/api/server.py
COLLABORATION / OWNERSHIP: Wilson Khanyezi / Wilsy OS Core Engineering
CERTIFICATION / UPDATE DATE: 2026-10-20
CHANGELOG: 2026-11-03 v1.39.0-GLOBAL-PRINCIPAL-AUTH-ROUTES-AND-MFA-FACTOR-BOOTSTRAP mounts the additive global login/selection/MFA/refresh/logout routes, installs global TOTP factor indexes, and accepts an injected platform KMS decryptor; absent KMS wiring keeps MFA completion unavailable.
2026-11-03 v1.36.0-GLOBAL-PRINCIPAL-AUTH-THROTTLE-INDEX-BOOTSTRAP installs the durable tenant-neutral global authentication rate-limit indexes alongside global credential and one-time membership/MFA challenge indexes during canonical connected startup; readiness remains false until every required index succeeds.
2026-11-03 v1.35.0-GLOBAL-PRINCIPAL-MFA-CHALLENGE-INDEX-BOOTSTRAP installs unique global-principal credential and single-use membership/MFA challenge indexes during canonical connected startup; no credentials, memberships, capacities, permissions, sessions, or identity authority are created.
2026-10-25 v1.34.0-L10A2R-C4D7-RECONCILIATION-RUNTIME-BOOTSTRAP mounts the dedicated signed-workload reconciliation route and binds canonical P2/P4/P5 authorities, a distinct deployment audit target, and transaction-bound idempotent response replay during startup; missing configuration remains fail-closed.
2026-10-20 v1.33.0-P12C-R4N-PRACTITIONER-BINDING-LIFECYCLE mounts the authenticated practitioner-binding command router exactly once, installs its access, binding and conflict-disposition indexes during connected startup, and denies commands until startup readiness completes while preserving router-owned tenant admission, transaction, Legal, ethical-wall, billing, settlement and Kennel EOS financial-execution boundaries.
2026-10-18 v1.27.0-P3-R3G-S5-A2-IAM-SECURITY-EVIDENCE-FACTOR-INDEX-BOOTSTRAP moves the already-certified tenant-authorization decision-evidence, authorization-role-revocation evidence, and privileged factor-currentness registry index DDL into canonical connected application startup while preserving all current-main router composition, request-path semantics, tenant boundaries, caller-owned transaction authority, and Kennel EOS financial execution exclusivity.
2026-10-18 v1.26.0-P1-R3E-AUTHORIZATION-ROLE-REVOCATION-RUNTIME-MOUNT mounts the certified ordinary authorization-role revocation router exactly once under /api while preserving router-owned authentication, tenant authorization, command, transaction, persistence, replay, root-lifecycle and financial boundaries; no privileged-security startup indexes are introduced.
2026-10-15 v1.25.0-CX26-R3-LEGAL-OPERATING-MODEL-ROUTER-MOUNT mounts the directly certified authenticated Tenant Legal Operating Model HTTP router exactly once under /api/legal/operating-model while preserving router-owned tenant correlation, IAM, transaction, persistence, workflow, legal-act, entitlement, billing, payment, settlement and financial boundaries.
2026-10-12 v1.24.0-L8-9C-LEGAL-STOREFRONT-PUBLIC-INTENT-ROUTER-MOUNT mounts the certified anonymous Legal Storefront public-intent router exactly once under /api/legal-storefront/public-intents and bootstraps the L8-9B durable intent indexes plus L8-9C0 ephemeral rate-limit indexes after successful database connection, without creating identity, tenant, Legal lifecycle, AI, subscription, entitlement, billing, payment, or settlement authority.
2026-10-12 v1.23.0-LEGAL-EVIDENCE-UPLOAD-ROUTER-MOUNT mounts the authenticated Legal Evidence multipart router exactly once under /api/legal-operations/evidence while preserving router-owned Partner IAM, canonical ProcessDocument scope, two-plane storage/commit, uncertainty, and financial boundaries.
2026-10-11 v1.22.0-LEGAL-CLIENT-ACCEPTANCE-ROUTER-MOUNT mounts the directly certified Legal Client Acceptance HTTP router exactly once under /api/legal-operations/client, preserving router-owned authenticated tenant admission, transaction lifecycle, server-derived client-acceptance context/issuance authority, and all engagement, representation, Court, AI, billing, payment, settlement, and Kennel boundaries.
2026-10-11 v1.21.0-D3B2A-MATTER-DEADLINE-ROUTER-MOUNT mounts the certified Legal Matter Deadline HTTP router exactly once under /api, preserving router-owned durable IAM, transaction, D3A service, tenant, AI, and Kennel boundaries; no deadline truth is created by application composition.
2026-10-05 v1.20.0-P0-C12F7C-HR-DOCUMENT-ROUTER-MOUNT composes the governed HR document router at /api/hr/documents; preserves Python EOS business authority, F6F ingestion ownership, persisted-sensitivity read authorization, tenant isolation, reconciliation-required 202 semantics, and no delete or financial execution authority.
2026-09-23 v1.18.0-L8-6B-DEPUTY-BINDING-INDEX-BOOTSTRAP bootstraps the
L8-6B deputy-principal binding registry indexes after successful database
connection so one-to-one tenant/principal and tenant/deputy uniqueness exists
before any binding command; startup creates no binding or authorization truth.
v1.19.0-L10-P2C7B-TENANT-BRANDING-ROUTER-MOUNT composes the governed tenant-
branding HTTP authority in the canonical EOS application so activation and
workspace projection requests cannot fall through to the Node BFF.
v1.15.0-C1C-R1B-GOVERNED-LEGAL-ORCHESTRATION composes the durable
C1C root registry and fail-closed canonical evidence/accounting seam.
v1.17.0-R1D-B0F-B4-PRODUCTION-LEGAL-ACCEPTANCE mounts the authenticated,
server-owned versioned legal-document and append-only acceptance authority.
v1.14.0-C1C-R1-GOVERNED-LEGAL-ORCHESTRATION composes one immutable
server-owned legal read registry and bounded legal-services route;
v1.13.0-C1B-R23-PRODUCTION-PROVIDER composes one optional,
server-owned OpenAI Responses provider binding from environment configuration
and keeps reasoning I/O off the ASGI event loop;
v1.12.0-C1B-R19-AUTHENTICATED-REASONING mounts the server-owned,
authenticated C1B reasoning command and extends no-store privacy headers;
v1.11.0-L7B-WILSY-AI-LEGAL-TOOL-MOUNT mounts the composed
authenticated WILSY AI Legal Tool Gateway; v1.10.0-L7D-B-EXPLICIT-DB-BOOTSTRAP assigns explicit database
connect/disconnect ownership to the ASGI lifecycle; v1.9.0 remains historical.
debug/docs and credentialed wildcard CORS, adds architecture-independent
security headers and no-store Legal Operations responses, and defaults the
dunning scheduler off in production; v1.8.0-L7B-LEGAL-OPERATIONS-COMMAND-MOUNT mounts the dedicated
authenticated Legal Operations command and read routers under /api without
adding financial authority, plus authenticated GET-only Legal Operations
billing and client-invoice read projections without adding issuance, payment,
settlement, or Kennel execution authority; v1.6.0 mounts the authenticated
PayShap host-runtime evidence router without changing billing or settlement
authority; v1.5.1 dual-mounted billing for BFF parity.
v1.10.0-L7D-B-EXPLICIT-DB-BOOTSTRAP assigns database connect/disconnect to
the ASGI lifecycle, leaving kernel and billing imports inert and persistence
fail-closed until explicit startup succeeds.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2; ISO 27001-aligned.
SECURITY / PRIVACY POSTURE: Router composition only; provider secrets and payloads are not logged or persisted here.
TENANT BOUNDARY: Mounted routers retain their own canonical tenant admission and isolation policies.
AUTHORITY BOUNDARY: HTTP application composition only; no identity, billing, provider, execution, or settlement truth is created here.
FINANCIAL AUTHORITY BOUNDARY: Kennel EOS remains exclusive financial execution authority; EXECUTION != SETTLEMENT.
FAIL-CLOSED DECLARATION: Router import/composition failures prevent the affected authority surface from being represented as mounted.
"""

from __future__ import annotations

import asyncio
import logging
import os
import time
import uuid
from contextlib import suppress
from datetime import datetime, timedelta, timezone
from typing import Any, Callable, List, Optional, cast
from zoneinfo import ZoneInfo

from fastapi import Depends, FastAPI, HTTPException, Request, Response
from fastapi.middleware.cors import CORSMiddleware

from .auth_router import router as auth_router
from .global_principal_auth_router import router as global_principal_auth_router
from .authority_bridge_router import router as authority_bridge_router
from .billing_router import evaluate_all_tenant_dunning_lifecycles, router as billing_router
from .employee_router import router as employee_router
from .errors import register_error_handlers
from .institutional_pki_router import router as institutional_pki_router
from .kernel_routes import router as kernel_router
from .payshap_webhook_router import router as payshap_webhook_router
from .electrum_payshap_completion_router import router as electrum_payshap_completion_router
from tools.eos.security.institutional_pki import InstitutionalPKIError, InstitutionalPKIVerifier
from tools.eos.kennel.orchestration.electrum_payshap_completion_processing import ensure_electrum_payshap_completion_indexes
from tools.eos.kennel.orchestration.electrum_payshap_completion_worker import run_electrum_payshap_completion_worker
from .plan_router import plan_router
from .router import direct_router, router
from .subscription_router import subscription_router
from .tenant_router import tenant_router
from .legal_operations_router import router as legal_operations_router
from .owner_commercial_workspace_router import router as owner_commercial_workspace_router
from .headcount_requisition_router import router as headcount_requisition_router
from .hiring_lifecycle_router import router as hiring_lifecycle_router
from .candidate_evidence_upload_router import router as candidate_evidence_upload_router
from .tenant_module_workspace_router import router as tenant_module_workspace_router
from .unified_my_work_router import router as unified_my_work_router
from .pos_workspace_router import router as pos_workspace_router, ensure_pos_workspace_indexes
from .commercial_agreement_router import router as commercial_agreement_router
from tools.eos.saas.entitlement.commercial_agreement_execution_verifier import CommercialAgreementExecutionVerifier
from .legal_operations_command_router import router as legal_operations_command_router
from .authorization_role_revocation_router import router as authorization_role_revocation_router
from .legal_operations_billing_read_router import router as legal_operations_billing_read_router
from .legal_matter_deadline_router import router as legal_matter_deadline_router
from .legal_client_acceptance_router import router as legal_client_acceptance_router
from .legal_evidence_upload_router import router as legal_evidence_upload_router
from .tenant_legal_operating_model_router import router as tenant_legal_operating_model_router
from .legal_practitioner_matter_binding_router import router as legal_practitioner_matter_binding_router
from tools.eos.legal_operations.registry import (
    legal_practitioner_matter_access_registry as p12c_access_registry,
    legal_practitioner_matter_binding_registry as p12c_binding_registry,
    legal_client_matter_conflict_disposition_registry as p12c_disposition_registry,
)
from .legal_storefront_public_intent_router import (
    router as legal_storefront_public_intent_router,
)
from .wilsy_ai_legal_gateway_router import router as wilsy_ai_legal_gateway_router
from .wilsy_ai_reasoning_router import router as wilsy_ai_reasoning_router
from .wilsy_ai_legal_services_router import router as wilsy_ai_legal_services_router
from .wilsy_ai_advisory_router import router as wilsy_ai_advisory_router
from .legal_acceptance_router import router as legal_acceptance_router
from .tenant_branding_router import router as tenant_branding_router
from .telemetry_ingestion_router import router as telemetry_ingestion_router
from .legal_evidence_provider_readonly_reconciliation_router import router as legal_evidence_provider_readonly_reconciliation_router
from tools.eos.legal_operations.service.legal_evidence_provider_readonly_reconciliation_runtime import (
    LegalEvidenceProviderReadOnlyReconciliationRuntimeBootstrapError,
    build_legal_evidence_provider_readonly_reconciliation_runtime,
)
from .wilsy_ai_legal_gateway_router import MODULE_ID as WILSY_AI_LEGAL_MODULE_ID, _canonical_underlying_context
from .tenant_authorization_http import TenantAuthorizationContext
from .hr_document_router import router as hr_document_router
from .hr_workforce_directory_router import router as hr_workforce_directory_router
from tools.eos.auth.authentication import get_principal_authority_repository
from tools.eos.auth.authorization import get_role_assignment_repository
from tools.eos.auth.tenant_access import get_tenant_membership_repository
from tools.eos.auth.principal_credential_repository import (
    COLLECTION as PRINCIPAL_CREDENTIAL_COLLECTION,
    PrincipalCredentialRepository,
)
from tools.eos.auth.membership_selection_challenge import (
    COLLECTION as MEMBERSHIP_SELECTION_CHALLENGE_COLLECTION,
    MembershipSelectionChallengeService,
)
from tools.eos.auth.global_principal_session_authority import (
    SESSION_COLLECTION as GLOBAL_PRINCIPAL_SESSION_COLLECTION,
    REFRESH_COLLECTION as GLOBAL_PRINCIPAL_REFRESH_COLLECTION,
    GlobalPrincipalSessionAuthority,
)
from tools.eos.auth.global_principal_system_session_authority import (
    CHALLENGE_COLLECTION as GLOBAL_PRINCIPAL_SYSTEM_MFA_CHALLENGE_COLLECTION,
    SESSION_COLLECTION as GLOBAL_PRINCIPAL_SYSTEM_SESSION_COLLECTION,
    REFRESH_COLLECTION as GLOBAL_PRINCIPAL_SYSTEM_REFRESH_COLLECTION,
    GlobalPrincipalSystemMfaChallengeService,
    GlobalPrincipalSystemSessionAuthority,
)
from tools.eos.auth.global_principal_mfa_kms_envelope import (
    GlobalMfaKeyManagementError,
    build_global_mfa_kms_envelope_from_environment,
)
from tools.eos.auth.global_principal_mfa_enrollment_service import (
    CHALLENGE_COLLECTION as GLOBAL_PRINCIPAL_MFA_ENROLLMENT_CHALLENGE_COLLECTION,
    GlobalPrincipalMfaEnrollmentService,
)
from tools.eos.auth.global_principal_totp_verifier import (
    COLLECTION as GLOBAL_PRINCIPAL_MFA_FACTOR_COLLECTION,
    GlobalPrincipalTotpVerifier,
)
from tools.eos.auth.principal_authentication_rate_limit import (
    COLLECTION as PRINCIPAL_AUTH_RATE_LIMIT_COLLECTION,
    PrincipalAuthenticationRateLimit,
)
from tools.eos.auth.tenant_authorization_decision_evidence_registry import (
    COLLECTION as TENANT_AUTHORIZATION_DECISION_EVIDENCE_COLLECTION,
    TenantAuthorizationDecisionEvidenceRegistry,
)
from tools.eos.auth.authorization_role_revocation_evidence_registry import (
    COLLECTION as AUTHORIZATION_ROLE_REVOCATION_EVIDENCE_COLLECTION,
    AuthorizationRoleRevocationEvidenceRegistry,
)
from tools.eos.auth.privileged_factor_verification_currentness_registry import (
    COLLECTION as PRIVILEGED_FACTOR_CURRENTNESS_COLLECTION,
    PrivilegedFactorVerificationCurrentnessRegistry,
)
from tools.eos.auth.internal_service_replay_registry import (
    COLLECTION as INTERNAL_SERVICE_REPLAY_COLLECTION,
    InternalServiceReplayRegistry,
)
from tools.eos.auth.internal_service_workload_credential_registry import (
    COLLECTION as INTERNAL_SERVICE_WORKLOAD_CREDENTIAL_COLLECTION,
    POINTER_COLLECTION as INTERNAL_SERVICE_WORKLOAD_CREDENTIAL_POINTER_COLLECTION,
    InternalServiceWorkloadCredentialRegistry,
)
from tools.eos.auth.privileged_workload_trust_currentness_registry import (
    COLLECTION as PRIVILEGED_WORKLOAD_TRUST_CURRENTNESS_COLLECTION,
    PrivilegedWorkloadTrustCurrentnessRegistry,
)
from tools.eos.auth.privileged_noninteractive_security_proof_registry import (
    COLLECTION as PRIVILEGED_NONINTERACTIVE_SECURITY_PROOF_COLLECTION,
    PrivilegedNoninteractiveSecurityProofRegistry,
)
from tools.eos.auth.privileged_security_assurance_evidence_registry import (
    COLLECTION as PRIVILEGED_SECURITY_ASSURANCE_EVIDENCE_COLLECTION,
    PrivilegedSecurityAssuranceEvidenceRegistry,
)
from tools.eos.intelligence.providers.reasoning_provider_runtime import (
    build_reasoning_provider_binding_from_environment,
)
from tools.eos.kernel.db import connect_db, disconnect_db, get_database, get_client
from tools.eos.system_services.support_case_registry import SupportCaseRegistry
from tools.eos.system_services.security_incident_registry import (
    COLLECTION as SECURITY_INCIDENT_COLLECTION,
    EVENT_COLLECTION as SECURITY_INCIDENT_EVENT_COLLECTION,
    SecurityIncidentRegistry,
)
from tools.eos.system_services.security_incident_assignment_registry import (
    COLLECTION as SECURITY_INCIDENT_ASSIGNMENT_COLLECTION,
    EVENT_COLLECTION as SECURITY_INCIDENT_ASSIGNMENT_EVENT_COLLECTION,
    SecurityIncidentAssignmentRegistry,
)
from tools.eos.system_services.runtime import (
    PLATFORM_WORKFORCE_SCOPE_ENV,
    build_system_services_runtime,
    build_system_services_response_runtime,
)
from .system_services_router import router as system_services_router
from tools.eos.intelligence.tools import ServerOwnedAIToolRegistry
from tools.eos.intelligence.tools.legal_operations_read_tools import build_legal_read_registrations
from tools.eos.intelligence.wilsy_ai_tool_orchestrator import WilsyAIToolOrchestrator
from tools.eos.intelligence.domain.legal_ai_gateway import LegalAIToolInvocationEvidence, TOOL_CONTRACTS, authorize_legal_ai_tool
from tools.eos.intelligence.registry.legal_ai_tool_invocation_registry import LegalAIToolInvocationRegistry
from tools.eos.saas.billing.wilsy_ai_entitlement_registry import COLLECTION as ENTITLEMENT_COLLECTION, WilsyAIEntitlementRegistry
from tools.eos.saas.billing.wilsy_ai_usage_capacity_orchestrator import WilsyAIUsageCapacityOrchestrator
from tools.eos.saas.billing.wilsy_ai_usage_observation_registry import COLLECTION as OBSERVATION_COLLECTION, WilsyAIUsageObservationRegistry
from tools.eos.saas.domain.wilsy_ai_usage_observation import WilsyAIUsageObservation
from tools.eos.intelligence.registry.ai_tool_orchestration_registry import AIToolOrchestrationRegistry, COLLECTION as C1C_ORCHESTRATION_COLLECTION, ensure_indexes as ensure_c1c_indexes
from tools.eos.legal_operations.registry.deputy_principal_binding_registry import (
    COLLECTION as DEPUTY_PRINCIPAL_BINDING_COLLECTION,
    DeputyPrincipalBindingRegistry,
)
from tools.eos.legal_operations.registry.process_service_location_evidence_registry import (
    ACCESS_AUDIT_COLLECTION as LOCATION_ACCESS_AUDIT_COLLECTION,
    OBSERVATION_COLLECTION as LOCATION_OBSERVATION_COLLECTION,
    PERMISSION_COLLECTION as LOCATION_PERMISSION_COLLECTION,
    REVOCATION_COLLECTION as LOCATION_REVOCATION_COLLECTION,
    ProcessServiceLocationEvidenceRegistry,
)
from tools.eos.legal_operations.registry.legal_storefront_public_intent_registry import (
    COLLECTION as LEGAL_STOREFRONT_PUBLIC_INTENT_COLLECTION,
    LegalStorefrontPublicIntentRegistry,
)
from tools.eos.legal_operations.service.legal_storefront_public_intent_rate_limit import (
    COLLECTION as LEGAL_STOREFRONT_PUBLIC_INTENT_RATE_LIMIT_COLLECTION,
    LegalStorefrontPublicIntentRateLimit,
)

VERSION = "v1.41.0-GLOBAL-MFA-ENROLLMENT-AND-LEGACY-MIGRATION"
logger = logging.getLogger("WilsyOS.API.Server")


class WilsyAPIServer:
    """Build the canonical FastAPI composition root without owning domain truth."""

    def __init__(
        self,
        title: str = "Wilsy OS Institutional API Gateway",
        description: str = "Billion-dollar institutional legal document & intelligence API platform.",
        version: str = "1.0.0",
        debug: bool = False,
        allowed_origins: Optional[List[str]] = None,
        reasoning_provider_binding: Any | None = None,
        global_principal_mfa_decrypt_secret: Callable[..., str] | None = None,
        commercial_agreement_execution_verifier: CommercialAgreementExecutionVerifier | None = None,
    ) -> None:
        """Initialize immutable server configuration and build the FastAPI app."""
        self.title = title
        self.description = description
        self.version = version
        self.production_mode = os.getenv("WILSY_ENV", os.getenv("ENV", "")).strip().lower() == "production"
        # Production must never inherit debug or wildcard credentialed CORS.
        self.debug = bool(debug) and not self.production_mode
        configured_origins = os.getenv("WILSY_CORS_ALLOWED_ORIGINS", "")
        parsed_origins = [item.strip() for item in configured_origins.split(",") if item.strip()]
        self.allowed_origins = list(allowed_origins) if allowed_origins is not None else parsed_origins
        if reasoning_provider_binding is None:
            try:
                reasoning_provider_binding = build_reasoning_provider_binding_from_environment()
            except Exception as error:
                # Configuration failure is isolated to optional reasoning; a
                # stable code is logged without exposing secrets or values.
                code = getattr(error, "code", "R23_PROVIDER_CONFIGURATION_INVALID")
                logger.error("[WILSY_AI_PROVIDER] binding unavailable: %s", code)
                reasoning_provider_binding = None
        self.reasoning_provider_binding = reasoning_provider_binding
        self.global_principal_mfa_decrypt_secret = global_principal_mfa_decrypt_secret
        if commercial_agreement_execution_verifier is not None and not isinstance(
            commercial_agreement_execution_verifier, CommercialAgreementExecutionVerifier
        ):
            raise TypeError("COMMERCIAL_AGREEMENT_EXECUTION_VERIFIER_CONFIGURATION_INVALID")
        self.commercial_agreement_execution_verifier = commercial_agreement_execution_verifier
        self.app: FastAPI = self._build_app()

    def _build_app(self) -> FastAPI:
        """Compose middleware, lifecycle hooks, and sovereign routers."""
        app = FastAPI(
            title=self.title,
            description=self.description,
            version=self.version,
            debug=self.debug,
            docs_url="/docs" if (not self.production_mode or os.getenv("WILSY_API_DOCS_ENABLED", "").strip().lower() in {"1", "true", "yes", "on"}) else None,
            redoc_url="/redoc" if (not self.production_mode or os.getenv("WILSY_API_DOCS_ENABLED", "").strip().lower() in {"1", "true", "yes", "on"}) else None,
        )
        app.state.wilsy_ai_reasoning_provider_binding = self.reasoning_provider_binding
        # Missing PKI, trusted timestamp or signatory-mandate adapters leave
        # agreement execution unavailable; no request payload can fill this slot.
        app.state.commercial_agreement_execution_verifier = self.commercial_agreement_execution_verifier
        # Build one immutable server-owned C1C registry at composition time.
        # No request, model output, or caller payload can mutate membership.
        app.state.wilsy_ai_legal_tool_registry = ServerOwnedAIToolRegistry(build_legal_read_registrations())
        app.state.wilsy_ai_legal_services_orchestrator = None
        # No binding command is ready before certified index startup.
        app.state.p12c_binding_indexes_ready = False
        app.state.global_principal_auth_indexes_ready = False
        app.state.global_principal_session_indexes_ready = False
        app.state.global_principal_system_session_indexes_ready = False
        app.state.global_principal_mfa_factor_indexes_ready = False
        app.state.global_principal_mfa_enrollment_indexes_ready = False
        app.state.global_principal_totp_verifier = None
        app.state.global_principal_mfa_decrypt_secret = self.global_principal_mfa_decrypt_secret
        app.state.global_principal_mfa_kms_envelope = None
        # Case storage readiness is separate from IAM authorization readiness.
        app.state.system_services_case_indexes_ready = False
        app.state.system_services_authority_ready = False
        app.state.system_services_authorizer = None
        app.state.system_services_case_registry = None
        app.state.system_services_incident_indexes_ready = False
        app.state.system_services_incident_registry = None
        app.state.system_services_assignment_indexes_ready = False
        app.state.system_services_assignment_registry = None
        app.state.system_services_response_indexes_ready = False
        app.state.system_services_response_decision_registry = None
        app.state.system_services_response_decision_service = None
        app.state.system_services_response_executor = None
        app.state.system_services_response_permission_assignments = None
        app.state.legal_evidence_provider_readonly_reconciliation_composition = None
        app.state.legal_evidence_provider_readonly_reconciliation_audit_client = None
        # C1E service is constructed lazily or by deployment composition; it
        # owns its caller-session transaction and never creates a second client.
        app.state.wilsy_ai_advisory_service = None
        # Production orchestration receives a required accounting seam.  The
        # seam must be explicitly supplied by the canonical L7B/M13P5B
        # composition; absent wiring fails closed rather than using memory.
        def persist_c1c_tool_accounting(**kwargs: Any) -> str:
            """Persist L7B invocation evidence and M13P5B usage atomically.

            This callback is invoked inside the orchestrator-owned accounting
            transaction.  It only composes existing canonical registries and
            never starts, commits, or aborts the caller's session.
            """
            session = kwargs.get("session")
            context = kwargs.get("context")
            tenant_id = kwargs.get("tenant_id")
            principal_id = kwargs.get("principal_id")
            tool_identity = kwargs.get("tool_identity")
            resource_identity = kwargs.get("resource_identity")
            invocation_id = kwargs.get("invocation_id")
            correlation_id = kwargs.get("correlation_id")
            result_fingerprint = kwargs.get("result_fingerprint")
            if session is None or not isinstance(context, TenantAuthorizationContext) or not all(isinstance(value, str) and value.strip() for value in (tenant_id, principal_id, tool_identity, resource_identity, invocation_id, correlation_id, result_fingerprint)):
                raise RuntimeError("C1C_TOOL_ACCOUNTING_INPUT_INVALID")
            tenant = cast(str, tenant_id)
            principal = cast(str, principal_id)
            tool = cast(str, tool_identity)
            resource = cast(str, resource_identity)
            invocation = cast(str, invocation_id)
            correlation = cast(str, correlation_id)
            result_fp = cast(str, result_fingerprint)
            if context.tenant_id != tenant:
                raise RuntimeError("C1C_TOOL_ACCOUNTING_TENANT_MISMATCH")
            database = get_database()
            if database is None:
                raise RuntimeError("C1C_TOOL_ACCOUNTING_DATABASE_UNAVAILABLE")
            contract = TOOL_CONTRACTS.get(tool)
            if contract is None:
                raise RuntimeError("C1C_TOOL_ACCOUNTING_TOOL_UNKNOWN")
            collections = {
                "entitlement": database[ENTITLEMENT_COLLECTION],
                "observation": database[OBSERVATION_COLLECTION],
            }
            entitlement = WilsyAIEntitlementRegistry(collections["entitlement"]).get_by_module(tenant_id=tenant, module_id=WILSY_AI_LEGAL_MODULE_ID, session=session)
            capacity = WilsyAIUsageCapacityOrchestrator.from_collections(entitlement_collection=collections["entitlement"], observation_collection=collections["observation"]).derive_capacity(tenant_id=tenant, entitlement_id=entitlement.entitlement_id, as_of=datetime.now(timezone.utc), session=session)
            underlying = _canonical_underlying_context(context, contract, session, get_principal_authority_repository(), get_tenant_membership_repository(), get_role_assignment_repository())
            input_payload = {"resource_identity": resource, "entitlement_id": entitlement.entitlement_id, "correlation_id": correlation}
            authorized = authorize_legal_ai_tool(gateway_context=context, underlying_context=underlying, entitlement=entitlement, capacity=capacity, tool_identity=tool, input_payload=input_payload, occurred_at=datetime.now(timezone.utc), result_reference=f"{contract.entity_type}:{resource}")
            evidence = LegalAIToolInvocationEvidence(
                invocation_id=invocation,
                tenant_id=authorized.tenant_id,
                principal_id=authorized.principal_id,
                tool_identity=authorized.tool_identity,
                tool_version=authorized.tool_version,
                gateway_permission=authorized.gateway_permission,
                underlying_permission=authorized.underlying_permission,
                capability=authorized.capability,
                business_role=authorized.business_role,
                entitlement_id=authorized.entitlement_id,
                entitlement_revision=authorized.entitlement_revision,
                entitlement_fingerprint=authorized.entitlement_fingerprint,
                tier=authorized.tier,
                policy_fingerprint=authorized.policy_fingerprint,
                capacity_evidence_reference=authorized.capacity_evidence_reference,
                capacity_evidence_fingerprint=authorized.capacity_evidence_fingerprint,
                correlation_id=authorized.correlation_id,
                input_fingerprint=authorized.input_fingerprint,
                result_classification=authorized.result_classification,
                result_reference=authorized.result_reference,
                result_fingerprint=result_fp,
                occurred_at=authorized.occurred_at,
            )
            persisted = LegalAIToolInvocationRegistry(database["wilsy_ai_legal_tool_invocations"]).create_or_replay(evidence, session=session)
            usage = WilsyAIUsageObservation(
                tenant_id=tenant,
                usage_observation_id=f"c1c-usage:{invocation_id}",
                entitlement_id=entitlement.entitlement_id,
                entitlement_revision=entitlement.lifecycle_revision,
                entitlement_fingerprint=entitlement.fingerprint,
                module_id=entitlement.module_id,
                request_units=1,
                input_tokens=0,
                output_tokens=0,
                automation_actions=1,
                occurred_at=persisted.occurred_at,
                source_evidence_reference=str(kwargs["evidence_reference"]),
                source_evidence_fingerprint=persisted.fingerprint,
            )
            WilsyAIUsageObservationRegistry(collections["observation"]).create_or_replay(usage, idempotency_key=invocation, session=session)
            return str(kwargs["evidence_reference"])

        app.state.wilsy_ai_legal_tool_accounting_writer = persist_c1c_tool_accounting
        app.state.wilsy_ai_legal_tool_accounting = persist_c1c_tool_accounting

        allow_credentials = "*" not in self.allowed_origins and bool(self.allowed_origins)
        app.add_middleware(
            CORSMiddleware,
            allow_origins=self.allowed_origins,
            allow_credentials=allow_credentials,
            allow_methods=["*"],
            allow_headers=["*"],
        )

        @app.middleware("http")
        async def tracing_middleware(
            request: Request,
            call_next: Callable[..., Any],
        ) -> Response:
            """Attach bounded request execution metadata without creating authority."""
            start_time = time.perf_counter()
            if not hasattr(request.state, "execution_id"):
                request.state.execution_id = f"EXEC-{uuid.uuid4().hex[:8].upper()}"
            response = await call_next(request)
            process_time = (time.perf_counter() - start_time) * 1000
            response.headers["X-Process-Time-Ms"] = f"{process_time:.3f}"
            response.headers["X-Wilsy-OS-Kernel"] = "FG169-Active"
            response.headers["X-Content-Type-Options"] = "nosniff"
            response.headers["Referrer-Policy"] = "no-referrer"
            response.headers["X-Frame-Options"] = "DENY"
            if request.url.path.startswith(("/api/legal-operations", "/api/wilsy-ai/reasoning", "/api/wilsy-ai/legal-next-actions", "/api/auth/global")):
                response.headers["Cache-Control"] = "no-store"
            if "x-trace-id" not in response.headers and "x-trace-id" in request.headers:
                response.headers["x-trace-id"] = request.headers["x-trace-id"]
            return response

        register_error_handlers(app, debug=self.debug)

        async def run_dunning_scheduler() -> None:
            """Execute the ledger-owned dunning pass once daily at 00:15 SAST."""
            timezone_sast = ZoneInfo("Africa/Johannesburg")
            while True:
                now = datetime.now(timezone_sast)
                next_run = now.replace(hour=0, minute=15, second=0, microsecond=0)
                if now >= next_run:
                    next_run += timedelta(days=1)
                await asyncio.sleep((next_run - now).total_seconds())
                try:
                    result = await evaluate_all_tenant_dunning_lifecycles()
                    logger.info(
                        "[DUNNING_SCHEDULER] Daily evaluation complete: tenants=%s transitions=%s",
                        result["evaluated_tenants"],
                        result["transition_count"],
                    )
                except asyncio.CancelledError:
                    raise
                except Exception:
                    logger.exception(
                        "[DUNNING_SCHEDULER] Daily evaluation failed; next scheduled pass remains armed"
                    )

        @app.on_event("startup")
        async def start_database() -> None:
            """Own explicit database bootstrap at application startup."""
            app.state.institutional_pki_ready = False
            app.state.institutional_pki_verifier = None
            try:
                app.state.institutional_pki_verifier = InstitutionalPKIVerifier.from_environment()
                app.state.institutional_pki_ready = True
                logger.info("[INSTITUTIONAL_PKI] Explicit pinned trust anchors and current CRL bundle loaded")
            except InstitutionalPKIError as error:
                app.state.institutional_pki_verifier = None
                app.state.institutional_pki_ready = False
                logger.warning("[INSTITUTIONAL_PKI] Verification unavailable: %s", error.code)
            app.state.p12c_binding_indexes_ready = False
            app.state.global_principal_auth_indexes_ready = False
            app.state.global_principal_session_indexes_ready = False
            app.state.global_principal_system_session_indexes_ready = False
            app.state.global_principal_mfa_factor_indexes_ready = False
            app.state.global_principal_mfa_enrollment_indexes_ready = False
            app.state.global_principal_totp_verifier = None
            app.state.global_principal_mfa_kms_envelope = None
            app.state.system_services_case_indexes_ready = False
            app.state.system_services_authority_ready = False
            app.state.system_services_authorizer = None
            app.state.system_services_case_registry = None
            app.state.system_services_incident_indexes_ready = False
            app.state.system_services_incident_registry = None
            app.state.system_services_assignment_indexes_ready = False
            app.state.system_services_assignment_registry = None
            app.state.system_services_response_indexes_ready = False
            app.state.system_services_response_decision_registry = None
            app.state.system_services_response_decision_service = None
            app.state.system_services_response_executor = None
            app.state.system_services_response_permission_assignments = None
            app.state.pos_workspace_indexes_ready = False
            app.state.telemetry_indexes_ready = False
            app.state.electrum_completion_indexes_ready = False
            app.state.electrum_settlement_worker_enabled = False
            connected, detail = connect_db()
            if not connected:
                logger.error("[KENNEL_DB] Explicit startup bootstrap unavailable: %s", detail)
                return
            app.state.legal_evidence_provider_readonly_reconciliation_composition = None
            app.state.legal_evidence_provider_readonly_reconciliation_audit_client = None
            provider = self.reasoning_provider_binding
            database, client = get_database(), get_client()
            if database is None:
                return
            if database is not None:
                try:
                    ensure_pos_workspace_indexes(database)
                    app.state.pos_workspace_indexes_ready = True
                except Exception as error:
                    app.state.pos_workspace_indexes_ready = False
                    logger.error("[POS_WORKSPACE] Canonical index bootstrap unavailable: %s", type(error).__name__)
                try:
                    ensure_electrum_payshap_completion_indexes(
                        inbox_collection=database["electrum_payshap_completion_inbox"],
                        binding_collection=database["electrum_provider_account_bindings"],
                        observation_collection=database["financial_settlement_observations"],
                        platform_truth_collection=database["platform_billing_financial_execution_truths"],
                        allocation_collection=database["platform_invoice_settlement_allocations"],
                        audit_collection=database["billing_audit_events"],
                        outbox_collection=database["billing_outbox_events"],
                    )
                    app.state.electrum_completion_indexes_ready = True
                except Exception as error:
                    app.state.electrum_completion_indexes_ready = False
                    logger.warning(
                        "[ELECTRUM_SETTLEMENT] Index provisioning unavailable: %s",
                        type(error).__name__,
                    )
                # Support-case storage indexes are canonical startup DDL.
                # This flag signals storage readiness only; route admission
                # must independently authorize every caller through EOS IAM.
                case_registry = SupportCaseRegistry(
                    cases=database["system_service_cases"],
                    events=database["system_service_case_events"],
                )
                case_registry.ensure_indexes()
                app.state.system_services_case_registry = case_registry
                app.state.system_services_case_indexes_ready = client is not None
                incident_registry = SecurityIncidentRegistry(
                    incidents=database[SECURITY_INCIDENT_COLLECTION],
                    events=database[SECURITY_INCIDENT_EVENT_COLLECTION],
                )
                incident_registry.ensure_indexes()
                app.state.system_services_incident_registry = incident_registry
                app.state.system_services_incident_indexes_ready = client is not None
                assignment_registry = SecurityIncidentAssignmentRegistry(
                    assignments=database[SECURITY_INCIDENT_ASSIGNMENT_COLLECTION],
                    events=database[SECURITY_INCIDENT_ASSIGNMENT_EVENT_COLLECTION],
                )
                assignment_registry.ensure_indexes()
                app.state.system_services_assignment_registry = assignment_registry
                app.state.system_services_assignment_indexes_ready = client is not None
                # SYSTEM Services authority is composed only from trusted
                # deployment configuration and canonical EOS repositories.
                # Missing scope configuration keeps staff APIs unavailable;
                # it never falls back to a tenant ID or a source-code default.
                platform_scope_id = os.getenv(PLATFORM_WORKFORCE_SCOPE_ENV, "")
                try:
                    case_registry, system_authorizer = build_system_services_runtime(
                        database,
                        platform_workforce_scope_id=platform_scope_id,
                    )
                    app.state.system_services_case_registry = case_registry
                    app.state.system_services_authorizer = system_authorizer
                    app.state.system_services_authority_ready = True
                except Exception as error:
                    # Tenant self-service remains available from the independent
                    # case store; only the privileged SYSTEM queue stays unavailable.
                    app.state.system_services_case_registry = case_registry
                    app.state.system_services_authorizer = None
                    app.state.system_services_authority_ready = False
                    code = getattr(error, "code", "SYSTEM_SERVICES_AUTHORITY_CONFIGURATION_UNAVAILABLE")
                    logger.warning("[SYSTEM_SERVICES] Authority composition unavailable: %s", code)
                if (
                    app.state.system_services_authority_ready is True
                    and app.state.system_services_authorizer is not None
                ):
                    try:
                        response_runtime = build_system_services_response_runtime(
                            database,
                            authorizer=app.state.system_services_authorizer,
                        )
                        app.state.system_services_response_decision_registry = response_runtime.decision_registry
                        app.state.system_services_response_decision_service = response_runtime.decision_service
                        app.state.system_services_response_executor = response_runtime.canonical_executor
                        app.state.system_services_response_permission_assignments = response_runtime.permission_assignment_registry
                        app.state.system_services_response_indexes_ready = True
                    except Exception as error:
                        # Response governance fails closed independently; the
                        # existing queue and tenant intake retain their own readiness.
                        app.state.system_services_response_indexes_ready = False
                        app.state.system_services_response_decision_registry = None
                        app.state.system_services_response_decision_service = None
                        app.state.system_services_response_executor = None
                        app.state.system_services_response_permission_assignments = None
                        code = getattr(error, "code", "SYSTEM_SERVICES_RESPONSE_COMPOSITION_UNAVAILABLE")
                        logger.warning("[SYSTEM_SERVICES] Response composition unavailable: %s", code)
                # Global authentication and one-time challenge indexes are
                # canonical startup DDL. Request handlers never create indexes.
                PrincipalCredentialRepository.ensure_indexes(
                    database[PRINCIPAL_CREDENTIAL_COLLECTION]
                )
                MembershipSelectionChallengeService.ensure_indexes(
                    database[MEMBERSHIP_SELECTION_CHALLENGE_COLLECTION]
                )
                GlobalPrincipalSessionAuthority.ensure_indexes(
                    database[GLOBAL_PRINCIPAL_SESSION_COLLECTION],
                    database[GLOBAL_PRINCIPAL_REFRESH_COLLECTION],
                )
                app.state.global_principal_session_indexes_ready = client is not None
                GlobalPrincipalSystemMfaChallengeService.ensure_indexes(
                    database[GLOBAL_PRINCIPAL_SYSTEM_MFA_CHALLENGE_COLLECTION]
                )
                GlobalPrincipalSystemSessionAuthority.ensure_indexes(
                    database[GLOBAL_PRINCIPAL_SYSTEM_SESSION_COLLECTION],
                    database[GLOBAL_PRINCIPAL_SYSTEM_REFRESH_COLLECTION],
                )
                app.state.global_principal_system_session_indexes_ready = client is not None
                GlobalPrincipalTotpVerifier.ensure_indexes(
                    database[GLOBAL_PRINCIPAL_MFA_FACTOR_COLLECTION]
                )
                app.state.global_principal_mfa_factor_indexes_ready = client is not None
                GlobalPrincipalMfaEnrollmentService.ensure_indexes(
                    database[GLOBAL_PRINCIPAL_MFA_ENROLLMENT_CHALLENGE_COLLECTION]
                )
                app.state.global_principal_mfa_enrollment_indexes_ready = client is not None
                decrypt_global_mfa_secret = cast(
                    Callable[..., str] | None,
                    getattr(app.state, "global_principal_mfa_decrypt_secret", None),
                )
                if not callable(decrypt_global_mfa_secret):
                    try:
                        kms_envelope = build_global_mfa_kms_envelope_from_environment()
                        if kms_envelope is not None:
                            kms_envelope.validate_access()
                            app.state.global_principal_mfa_kms_envelope = kms_envelope
                            decrypt_global_mfa_secret = kms_envelope.decrypt_secret
                    except GlobalMfaKeyManagementError as error:
                        app.state.global_principal_mfa_kms_envelope = None
                        logger.warning(
                            "[GLOBAL_PRINCIPAL_MFA] KMS composition unavailable: %s",
                            str(error),
                        )
                if callable(decrypt_global_mfa_secret):
                    app.state.global_principal_totp_verifier = GlobalPrincipalTotpVerifier(
                        collection=database[GLOBAL_PRINCIPAL_MFA_FACTOR_COLLECTION],
                        decrypt_secret=decrypt_global_mfa_secret,
                    )
                PrincipalAuthenticationRateLimit(
                    database[PRINCIPAL_AUTH_RATE_LIMIT_COLLECTION]
                ).ensure_indexes()
                app.state.global_principal_auth_indexes_ready = client is not None
                database["wilsy_sovereign_telemetry"].create_index(
                    "trace_id", unique=True, sparse=True, name="uq_telemetry_trace_id"
                )
                TenantAuthorizationDecisionEvidenceRegistry(
                    database[
                        TENANT_AUTHORIZATION_DECISION_EVIDENCE_COLLECTION
                    ],
                    principal_repository=(
                        get_principal_authority_repository()
                    ),
                ).ensure_indexes()
                AuthorizationRoleRevocationEvidenceRegistry(
                    database[
                        AUTHORIZATION_ROLE_REVOCATION_EVIDENCE_COLLECTION
                    ]
                ).ensure_indexes()
                PrivilegedFactorVerificationCurrentnessRegistry(
                    database[
                        PRIVILEGED_FACTOR_CURRENTNESS_COLLECTION
                    ]
                ).ensure_indexes()
                InternalServiceReplayRegistry.ensure_indexes(
                    database[
                        INTERNAL_SERVICE_REPLAY_COLLECTION
                    ]
                )
                InternalServiceWorkloadCredentialRegistry(
                    database[
                        INTERNAL_SERVICE_WORKLOAD_CREDENTIAL_COLLECTION
                    ],
                    database[
                        INTERNAL_SERVICE_WORKLOAD_CREDENTIAL_POINTER_COLLECTION
                    ],
                ).ensure_indexes()
                PrivilegedWorkloadTrustCurrentnessRegistry(
                    database[
                        PRIVILEGED_WORKLOAD_TRUST_CURRENTNESS_COLLECTION
                    ]
                ).ensure_indexes()
                PrivilegedNoninteractiveSecurityProofRegistry(
                    database[
                        PRIVILEGED_NONINTERACTIVE_SECURITY_PROOF_COLLECTION
                    ]
                ).ensure_indexes()
                PrivilegedSecurityAssuranceEvidenceRegistry(
                    database[
                        PRIVILEGED_SECURITY_ASSURANCE_EVIDENCE_COLLECTION
                    ]
                ).ensure_indexes()
                DeputyPrincipalBindingRegistry.ensure_indexes(
                    database[DEPUTY_PRINCIPAL_BINDING_COLLECTION]
                )
                ProcessServiceLocationEvidenceRegistry.ensure_indexes(
                    database[LOCATION_PERMISSION_COLLECTION],
                    database[LOCATION_OBSERVATION_COLLECTION],
                    database[LOCATION_REVOCATION_COLLECTION],
                    database[LOCATION_ACCESS_AUDIT_COLLECTION],
                )
                LegalStorefrontPublicIntentRegistry.ensure_indexes(
                    database[LEGAL_STOREFRONT_PUBLIC_INTENT_COLLECTION]
                )
                LegalStorefrontPublicIntentRateLimit.ensure_indexes(
                    database[
                        LEGAL_STOREFRONT_PUBLIC_INTENT_RATE_LIMIT_COLLECTION
                    ]
                )
                # P12C: immutable practitioner-binding dependency indexes.
                # Installation belongs to startup, not request transactions.
                p12c_access_registry.ensure_indexes(
                    database["legal_practitioner_matter_access_evidence"]
                )
                p12c_binding_registry.ensure_indexes(
                    database[p12c_binding_registry.COLLECTION_NAME]
                )
                p12c_disposition_registry.ensure_indexes(
                    database[p12c_disposition_registry.COLLECTION]
                )
            if provider is not None and database is not None and client is not None:
                ensure_c1c_indexes(database[C1C_ORCHESTRATION_COLLECTION])
                app.state.wilsy_ai_legal_services_orchestrator = WilsyAIToolOrchestrator(
                    tool_registry=app.state.wilsy_ai_legal_tool_registry,
                    model_provider=provider,
                    root_registry=AIToolOrchestrationRegistry(database[C1C_ORCHESTRATION_COLLECTION]),
                    root_session_factory=client.start_session,
                    tool_accounting_writer=persist_c1c_tool_accounting,
                    production=True,
                )
            app.state.telemetry_indexes_ready = client is not None
            # Build the governed reconciliation graph only from canonical
            # business authorities and an explicitly separate deployment audit URI.
            if database is not None:
                try:
                    reconciliation_composition, reconciliation_audit_client = (
                        build_legal_evidence_provider_readonly_reconciliation_runtime(
                            mongo_database=database,
                        )
                    )
                    if reconciliation_composition.business_client is not client:
                        reconciliation_audit_client.close()
                        raise LegalEvidenceProviderReadOnlyReconciliationRuntimeBootstrapError(
                            "RECONCILIATION_BUSINESS_CLIENT_BINDING_MISMATCH"
                        )
                    app.state.legal_evidence_provider_readonly_reconciliation_composition = (
                        reconciliation_composition
                    )
                    app.state.legal_evidence_provider_readonly_reconciliation_audit_client = (
                        reconciliation_audit_client
                    )
                except Exception as error:
                    code = getattr(error, "args", ["RECONCILIATION_RUNTIME_COMPOSITION_UNAVAILABLE"])[0]
                    logger.error(
                        "[LEGAL_EVIDENCE_RECONCILIATION] Runtime composition unavailable: %s",
                        str(code) if isinstance(code, str) else "RECONCILIATION_RUNTIME_COMPOSITION_UNAVAILABLE",
                    )
            # Only completed startup establishes binding readiness.
            app.state.p12c_binding_indexes_ready = client is not None

        @app.on_event("shutdown")
        async def stop_database() -> None:
            """Release the kernel database during controlled application shutdown."""
            app.state.institutional_pki_ready = False
            app.state.institutional_pki_verifier = None
            app.state.p12c_binding_indexes_ready = False
            app.state.global_principal_auth_indexes_ready = False
            app.state.global_principal_session_indexes_ready = False
            app.state.global_principal_system_session_indexes_ready = False
            app.state.global_principal_mfa_factor_indexes_ready = False
            app.state.global_principal_mfa_enrollment_indexes_ready = False
            app.state.global_principal_totp_verifier = None
            app.state.global_principal_mfa_kms_envelope = None
            app.state.system_services_case_indexes_ready = False
            app.state.system_services_authority_ready = False
            app.state.system_services_authorizer = None
            app.state.system_services_case_registry = None
            app.state.system_services_incident_indexes_ready = False
            app.state.system_services_incident_registry = None
            app.state.system_services_assignment_indexes_ready = False
            app.state.system_services_assignment_registry = None
            app.state.telemetry_indexes_ready = False
            audit_client = getattr(
                app.state,
                "legal_evidence_provider_readonly_reconciliation_audit_client",
                None,
            )
            app.state.legal_evidence_provider_readonly_reconciliation_composition = None
            app.state.legal_evidence_provider_readonly_reconciliation_audit_client = None
            if audit_client is not None:
                with suppress(Exception):
                    audit_client.close()
            disconnect_db()

        @app.on_event("startup")
        async def start_dunning_scheduler() -> None:
            """Arm the daily dunning scheduler when enabled by environment policy."""
            enabled = os.getenv(
                "WILSY_DUNNING_SCHEDULER_ENABLED",
                "false" if self.production_mode else "true",
            ).strip().lower() in {"1", "true", "yes", "on"}
            if enabled:
                app.state.dunning_scheduler_task = asyncio.create_task(
                    run_dunning_scheduler()
                )
                logger.info(
                    "[DUNNING_SCHEDULER] Armed for daily 00:15 SAST evaluation"
                )
            else:
                logger.warning(
                    "[DUNNING_SCHEDULER] Disabled by WILSY_DUNNING_SCHEDULER_ENABLED"
                )

        @app.on_event("shutdown")
        async def stop_dunning_scheduler() -> None:
            """Cancel the scheduler cleanly during controlled API shutdown."""
            task = getattr(app.state, "dunning_scheduler_task", None)
            if task:
                task.cancel()
                with suppress(asyncio.CancelledError):
                    await task

        @app.on_event("startup")
        async def start_electrum_settlement_worker() -> None:
            """Arm the settlement inbox worker only by explicit environment opt-in."""
            enabled = os.getenv(
                "WILSY_ELECTRUM_SETTLEMENT_WORKER_ENABLED", "false"
            ).strip().lower() in {"1", "true", "yes", "on"}
            sandbox_only = os.getenv("WILSY_ELECTRUM_ENVIRONMENT", "").strip().lower() == "sandbox"
            if enabled and sandbox_only and getattr(app.state, "electrum_completion_indexes_ready", False) is True:
                app.state.electrum_settlement_worker_task = asyncio.create_task(
                    run_electrum_payshap_completion_worker()
                )
                app.state.electrum_settlement_worker_enabled = True
                logger.info("[ELECTRUM_SETTLEMENT] Completion inbox worker explicitly enabled")
            else:
                app.state.electrum_settlement_worker_enabled = False
                logger.info(
                    "[ELECTRUM_SETTLEMENT] Completion inbox worker remains disabled"
                )

        @app.on_event("shutdown")
        async def stop_electrum_settlement_worker() -> None:
            """Cancel the opt-in inbox worker cleanly during API shutdown."""
            task = getattr(app.state, "electrum_settlement_worker_task", None)
            if task:
                task.cancel()
                with suppress(asyncio.CancelledError):
                    await task

        @app.get("/")
        async def root_health() -> dict[str, str]:
            """Return bounded API composition health metadata."""
            return {
                "status": "OPERATIONAL",
                "kernel": "EOS Kernel v1.6.0",
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "bridge": "kernel-v1.1.1",
            }

        # Sovereign mounting order.
        app.include_router(kernel_router)
        app.include_router(kernel_router, prefix="/api")
        app.include_router(institutional_pki_router, prefix="/api")

        app.include_router(direct_router)
        app.include_router(router)
        app.include_router(tenant_router)
        app.include_router(legal_operations_router, prefix="/api")
        app.include_router(owner_commercial_workspace_router, prefix="/api")
        app.include_router(headcount_requisition_router, prefix="/api")
        app.include_router(hiring_lifecycle_router, prefix="/api")
        app.include_router(candidate_evidence_upload_router, prefix="/api")
        app.include_router(tenant_module_workspace_router, prefix="/api")
        app.include_router(unified_my_work_router, prefix="/api")
        app.include_router(pos_workspace_router, prefix="/api")
        app.include_router(commercial_agreement_router, prefix="/api")
        app.include_router(legal_operations_command_router, prefix="/api")
        app.include_router(authorization_role_revocation_router, prefix="/api")
        app.include_router(legal_operations_billing_read_router, prefix="/api")
        app.include_router(legal_matter_deadline_router, prefix="/api")
        app.include_router(legal_client_acceptance_router, prefix="/api")
        app.include_router(legal_evidence_upload_router, prefix="/api")
        app.include_router(legal_evidence_provider_readonly_reconciliation_router, prefix="/api")
        app.include_router(tenant_legal_operating_model_router, prefix="/api")
        # P12C readiness is server-owned, never supplied by request callers.
        # It precedes command transactions and adds no IAM authority.
        def require_p12c_binding_ready(request: Request) -> None:
            if (
                getattr(
                    request.app.state,
                    "p12c_binding_indexes_ready",
                    False,
                )
                is not True
            ):
                raise HTTPException(
                    status_code=503,
                    detail="P9_BINDING_INDEXES_NOT_READY",
                )

        app.include_router(
            legal_practitioner_matter_binding_router,
            prefix="/api",
            dependencies=[Depends(require_p12c_binding_ready)],
        )
        app.include_router(
            legal_storefront_public_intent_router,
            prefix="/api",
        )
        app.include_router(wilsy_ai_legal_gateway_router, prefix="/api")
        app.include_router(wilsy_ai_reasoning_router, prefix="/api")
        app.include_router(wilsy_ai_legal_services_router, prefix="/api")
        app.include_router(wilsy_ai_advisory_router, prefix="/api")
        app.include_router(legal_acceptance_router, prefix="/api")
        app.include_router(tenant_branding_router, prefix="/api")
        app.include_router(telemetry_ingestion_router, prefix="/api")
        app.include_router(subscription_router)
        app.include_router(plan_router)

        app.include_router(auth_router, prefix="/api")
        app.include_router(global_principal_auth_router, prefix="/api")
        app.include_router(system_services_router, prefix="/api")

        app.include_router(billing_router)
        app.include_router(billing_router, prefix="/api")

        app.include_router(employee_router)
        app.include_router(authority_bridge_router)

        # Provider evidence ingress is mounted once at its canonical route.
        app.include_router(payshap_webhook_router)
        app.include_router(electrum_payshap_completion_router)
        app.include_router(hr_document_router)
        app.include_router(hr_workforce_directory_router)

        logger.info(
            "WilsyAPIServer [%s v%s] initialized with sovereign routers "
            "(kernel, auth, role revocation, billing, employees, internal authority, PayShap evidence, legal acceptance, Legal Evidence upload, Legal Storefront public intent, tenant branding, legal matter deadlines).",
            self.title,
            self.version,
        )
        return app

    def get_app(self) -> FastAPI:
        """Return the already-built canonical FastAPI application."""
        return self.app


app = WilsyAPIServer().get_app()

# ARTIFACT: server.py
# VERSION: v1.41.0-GLOBAL-MFA-ENROLLMENT-AND-LEGACY-MIGRATION
# AUTHORITY BOUNDARY: HTTP application composition only; domain authorities remain separate.
# TENANT POSTURE: Mounted routers retain their canonical tenant isolation and admission rules.
# FAIL-CLOSED POSTURE: Unmounted or failed router composition is never represented as operational authority.
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively; EXECUTION != SETTLEMENT.
# END OF WILSY OS SOVEREIGN ARTIFACT
