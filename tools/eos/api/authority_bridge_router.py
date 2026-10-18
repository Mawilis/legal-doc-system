"""

WILSY OS Python Authority Bridge Router
TITLE: WILSY OS Python Authority Bridge Router
VERSION: v1.1.1-P3-R3G-S6-A3-TRUST-DENIAL-PROVENANCE-MAPPING
AUTHORITY: HTTP composition of existing Python service-trust, identity, tenant, and authorization authorities.
EPITOME: Verifies a Node service assertion without allowing service metadata to become user or tenant authority.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tools/eos/api/authority_bridge_router.py
COLLABORATION / OWNERSHIP: Wilson Khanyezi / Wilsy Core Engineering; Python owns authority decisions.
CERTIFICATION/UPDATE DATE: 2026-10-14
CHANGELOG: 2026-10-14 v1.1.1-P3-R3G-S6-A3-TRUST-DENIAL-PROVENANCE-MAPPING preserves canonical trust-denial provenance across the existing S6 workload-proof exception cause chain so mounted bad-signature, replay, malformed, freshness, and authentication denials retain HTTP 401 while genuine configuration/infrastructure failure retains HTTP 503; no route, transaction, authority, tenant, activation, or financial behavior changes.
2026-10-14 v1.1.1-P3-R3G-S6-A3-TRUST-DENIAL-PROVENANCE-MAPPING certifies the existing P3-R3G-S6-A3 production authority bridge: canonical internal-service trust feeds S6-A2 noninteractive assurance through the canonical Kernel database/client; replay/workload/proof/evidence writes remain inside one caller-owned transaction and commit only after current human identity, tenant membership, and policy authorization succeed; every pre-commit denial aborts those writes; request-path index DDL remains absent; callers cannot assert principal or workload proof reference; no privileged activation or financial execution authority is created.
v1.1.1-P3-R3G-S6-A3-TRUST-DENIAL-PROVENANCE-MAPPING — service-trust-first ordering; governed user and tenant authorities execute only after trust.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2; ISO 27001.
SECURITY/PRIVACY POSTURE: Fail closed; bounded responses; secrets, credentials, claims, and repository details are never returned.
TENANT BOUNDARY: X-Tenant-ID is untrusted context and is admitted only by current Python membership authority.
AUTHORITY BOUNDARY: Owns HTTP composition only; it does not own identity, lifecycle, membership, role, or permission truth.
FINANCIAL AUTHORITY BOUNDARY: None; Kennel EOS remains exclusive.


"""
from __future__ import annotations

import hashlib
import os
from collections.abc import Awaitable, Callable, Mapping
from typing import Any, Protocol

from fastapi import APIRouter, Request, status
from fastapi.security import HTTPAuthorizationCredentials
from pydantic import BaseModel, ConfigDict

from tools.eos.kernel.db import get_client, get_database
from tools.eos.api.exceptions import ForbiddenOperationException, UnauthorizedAccessException, WilsyAPIException
from tools.eos.auth.authentication import get_current_identity, get_principal_authority_repository
from tools.eos.auth.authorization import RequirePermission, get_role_assignment_repository
from tools.eos.auth.identity import SovereignIdentity
from tools.eos.auth.internal_service_replay_registry import (
    COLLECTION as INTERNAL_SERVICE_REPLAY_COLLECTION,
    InternalServiceReplayRegistry,
)
from tools.eos.auth.internal_service_workload_credential_registry import (
    COLLECTION as INTERNAL_SERVICE_WORKLOAD_CREDENTIAL_COLLECTION,
    POINTER_COLLECTION as INTERNAL_SERVICE_WORKLOAD_CREDENTIAL_POINTER_COLLECTION,
    InternalServiceWorkloadCredentialRegistry,
)
from tools.eos.auth.internal_service_workload_proof_service import (
    InternalServiceWorkloadProofService,
)
from tools.eos.auth.internal_service_noninteractive_assurance_service import (
    InternalServiceNoninteractiveAssuranceService,
)
from tools.eos.auth.principal_authority_repository import (
    COLLECTION as PRINCIPAL_AUTHORITY_COLLECTION,
)
from tools.eos.auth.privileged_workload_trust_currentness_registry import (
    COLLECTION as PRIVILEGED_WORKLOAD_CURRENTNESS_COLLECTION,
    PrivilegedWorkloadTrustCurrentnessRegistry,
)
from tools.eos.auth.privileged_noninteractive_security_proof_registry import (
    COLLECTION as PRIVILEGED_NONINTERACTIVE_PROOF_COLLECTION,
    PrivilegedNoninteractiveSecurityProofRegistry,
)
from tools.eos.auth.privileged_security_assurance import (
    PrivilegedAssurancePurpose,
)
from tools.eos.auth.privileged_security_assurance_evidence_registry import (
    COLLECTION as PRIVILEGED_ASSURANCE_EVIDENCE_COLLECTION,
    PrivilegedSecurityAssuranceEvidenceRegistry,
)
from tools.eos.auth.internal_service_trust import (
    InternalServiceTrustAuthenticationError,
    InternalServiceTrustConfigurationError,
    InternalServiceTrustError,
    InternalServiceTrustFreshnessError,
    InternalServiceTrustMalformedRequestError,
    InternalServiceTrustReplayError,
    TrustResult,
    verify_internal_service_request,
)
from tools.eos.auth.tenant_access import get_current_tenant_identity, get_tenant_membership_repository

VERSION = "v1.1.1-P3-R3G-S6-A3-TRUST-DENIAL-PROVENANCE-MAPPING"
ROUTE_PATH = "/internal/authority/authorize"
SERVICE_HEADERS = (
    "X-Wilsy-Auth-Version", "X-Wilsy-Service-ID", "X-Wilsy-Audience", "X-Wilsy-Key-ID",
    "X-Wilsy-Timestamp", "X-Wilsy-Nonce", "X-Wilsy-Body-SHA3-512", "X-Wilsy-Correlation-ID",
    "X-Wilsy-Signature",
)


class ReplayProvider(Protocol):
    """Protocol for one-use internal-service replay admission.

    Implementations atomically admit each exact service/key/nonce claim at most
    once for its bounded expiry window. Replay admission is security evidence
    only and does not create principal, tenant, role, permission, privileged
    activation, session, or financial authority.
    """

    def consume_once(
        self,
        *,
        service_id: str,
        key_id: str,
        nonce: str,
        expires_at: int,
    ) -> bool:
        """Consume one exact replay claim or reject a duplicate.

        The bounded service/key/nonce/expiry tuple identifies the one-use trust
        claim. A true result represents replay admission only; it grants no
        identity, tenant, role, permission, activation, or financial authority.
        """
        ...


class BridgeRequest(BaseModel):
    """Only a server-controlled policy identifier may cross this boundary."""
    model_config = ConfigDict(extra="forbid")
    policy_id: str


def _service_config(env: Mapping[str, str] | None = None) -> tuple[dict[str, tuple[str, str]], str, str]:
    values = env or os.environ
    names = ("WILSY_INTERNAL_AUTH_SERVICE_ID", "WILSY_INTERNAL_AUTH_AUDIENCE", "WILSY_INTERNAL_AUTH_KEY_ID", "WILSY_INTERNAL_AUTH_SECRET")
    resolved = {name: values.get(name) for name in names}
    if any(not isinstance(value, str) or not value.strip() for value in resolved.values()):
        raise WilsyAPIException("Service trust is unavailable.", status_code=status.HTTP_503_SERVICE_UNAVAILABLE)
    service_id = resolved[names[0]].strip()  # type: ignore[union-attr]
    audience = resolved[names[1]].strip()  # type: ignore[union-attr]
    key_id = resolved[names[2]].strip()  # type: ignore[union-attr]
    secret = resolved[names[3]]
    assert isinstance(secret, str)
    return {key_id: (service_id, secret)}, service_id, audience


def _origin_form(request: Request) -> str:
    raw_path = request.scope.get("raw_path")
    query = request.scope.get("query_string", b"")
    if not isinstance(raw_path, bytes) or not isinstance(query, bytes):
        raise WilsyAPIException("Service trust is unavailable.", status_code=503)
    try:
        return (raw_path + (b"?" + query if query else b"")).decode("ascii")
    except UnicodeDecodeError as error:
        raise WilsyAPIException("Service trust denied.", status_code=401) from error


def _trust_headers(request: Request) -> dict[str, str]:
    mapping = {
        "version": "X-Wilsy-Auth-Version", "service_id": "X-Wilsy-Service-ID",
        "audience": "X-Wilsy-Audience", "key_id": "X-Wilsy-Key-ID",
        "timestamp": "X-Wilsy-Timestamp", "nonce": "X-Wilsy-Nonce",
        "body_sha3_512": "X-Wilsy-Body-SHA3-512", "correlation_id": "X-Wilsy-Correlation-ID",
        "signature": "X-Wilsy-Signature",
    }
    headers = {field: request.headers.get(header, "") for field, header in mapping.items()}
    headers.update({"method": request.method, "path": _origin_form(request)})
    return headers


def _trust_failure(error: Exception) -> WilsyAPIException:
    """Map bounded internal-service trust provenance to the canonical HTTP boundary.

    Direct trust failures and trust failures preserved through the S6 workload
    proof cause/context chain retain their authentication/replay/configuration
    classification. Security denial remains HTTP 401; genuine configuration or
    infrastructure unavailability remains HTTP 503. No exception detail,
    credential, signature, tenant authority, or privileged authority is exposed.
    """
    current: BaseException | None = error
    visited: set[int] = set()

    while current is not None and id(current) not in visited:
        visited.add(id(current))

        if (
            isinstance(
                current,
                InternalServiceTrustConfigurationError,
            )
            and str(current) == "unknown trust key"
        ):
            return WilsyAPIException(
                "Service trust denied.",
                status_code=401,
            )

        if isinstance(
            current,
            InternalServiceTrustReplayError,
        ):
            return WilsyAPIException(
                "Service trust denied.",
                status_code=401,
            )

        if isinstance(
            current,
            InternalServiceTrustConfigurationError,
        ):
            return WilsyAPIException(
                "Service trust is unavailable.",
                status_code=503,
            )

        if isinstance(
            current,
            InternalServiceTrustError,
        ):
            return WilsyAPIException(
                "Service trust denied.",
                status_code=401,
            )

        current = (
            current.__cause__
            if current.__cause__ is not None
            else current.__context__
        )

    return WilsyAPIException(
        "Service trust is unavailable.",
        status_code=503,
    )


def _internal_assurance_idempotency_key(
    *,
    trust_headers: Mapping[str, str],
    body: bytes,
) -> str:
    material = "\n".join(
        (
            trust_headers.get("service_id", ""),
            trust_headers.get("key_id", ""),
            trust_headers.get("audience", ""),
            trust_headers.get("method", ""),
            trust_headers.get("path", ""),
            trust_headers.get("timestamp", ""),
            trust_headers.get("nonce", ""),
            trust_headers.get("body_sha3_512", ""),
            trust_headers.get("correlation_id", ""),
        )
    ).encode("utf-8") + b"\x00" + body

    return (
        "internal-service-assurance:"
        + hashlib.sha3_512(material).hexdigest()
    )


def _production_noninteractive_assurance_service(
    *,
    database: Any,
) -> InternalServiceNoninteractiveAssuranceService:
    credential_registry = InternalServiceWorkloadCredentialRegistry(
        database[
            INTERNAL_SERVICE_WORKLOAD_CREDENTIAL_COLLECTION
        ],
        database[
            INTERNAL_SERVICE_WORKLOAD_CREDENTIAL_POINTER_COLLECTION
        ],
    )

    workload_registry = (
        PrivilegedWorkloadTrustCurrentnessRegistry(
            database[
                PRIVILEGED_WORKLOAD_CURRENTNESS_COLLECTION
            ]
        )
    )

    workload_source = InternalServiceWorkloadProofService(
        replay_collection=
            database[
                INTERNAL_SERVICE_REPLAY_COLLECTION
            ],
        credential_registry=
            credential_registry,
        principal_collection=
            database[
                PRINCIPAL_AUTHORITY_COLLECTION
            ],
        workload_registry=
            workload_registry,
    )

    return (
        InternalServiceNoninteractiveAssuranceService(
            workload_source=
                workload_source,
            workload_registry=
                workload_registry,
            proof_registry=
                PrivilegedNoninteractiveSecurityProofRegistry(
                    database[
                        PRIVILEGED_NONINTERACTIVE_PROOF_COLLECTION
                    ]
                ),
            evidence_registry=
                PrivilegedSecurityAssuranceEvidenceRegistry(
                    database[
                        PRIVILEGED_ASSURANCE_EVIDENCE_COLLECTION
                    ]
                ),
        )
    )


async def _authorize_production_request(
    request: Request,
    payload: BridgeRequest,
    *,
    identity_provider:
        Callable[
            [],
            Awaitable[SovereignIdentity],
        ],
    tenant_provider:
        Callable[
            [SovereignIdentity],
            Awaitable[SovereignIdentity],
        ],
    authorization_provider:
        Callable[
            [SovereignIdentity, str],
            Awaitable[SovereignIdentity],
        ],
    config:
        Mapping[str, str]
        | None = None,
) -> dict[str, Any]:
    body = await request.body()

    try:
        keys, _service_id, audience = (
            _service_config(config)
        )
        trust_headers = _trust_headers(
            request
        )
    except Exception as error:
        if isinstance(
            error,
            WilsyAPIException,
        ):
            raise
        raise _trust_failure(
            error
        ) from error

    client = get_client()
    database = get_database()

    if (
        client is None
        or database is None
    ):
        raise WilsyAPIException(
            "Authorization authority is unavailable.",
            status_code=503,
        )

    service = (
        _production_noninteractive_assurance_service(
            database=database
        )
    )

    with client.start_session() as session:
        session.start_transaction()

        try:
            assurance = service.compose(
                request=trust_headers,
                body=body,
                keys=keys,
                expected_audience=
                    audience,
                assurance_purpose=(
                    PrivilegedAssurancePurpose
                    .PRIVILEGED_ELIGIBILITY_TO_ACTIVATION
                ),
                idempotency_key=(
                    _internal_assurance_idempotency_key(
                        trust_headers=
                            trust_headers,
                        body=body,
                    )
                ),
                session=session,
            )

            identity = (
                await identity_provider()
            )

            tenant_identity = (
                await tenant_provider(
                    identity
                )
            )

            authorized = (
                await authorization_provider(
                    tenant_identity,
                    payload.policy_id,
                )
            )

            session.commit_transaction()

        except (
            UnauthorizedAccessException,
            ForbiddenOperationException,
        ):
            if getattr(
                session,
                "in_transaction",
                False,
            ):
                session.abort_transaction()
            raise

        except Exception as error:
            if getattr(
                session,
                "in_transaction",
                False,
            ):
                session.abort_transaction()

            if isinstance(
                error,
                WilsyAPIException,
            ):
                raise

            if (
                error.__class__
                .__module__
                .startswith(
                    "tools.eos.auth.internal_service"
                )
            ):
                raise _trust_failure(
                    error
                ) from error

            raise WilsyAPIException(
                "Authorization authority is unavailable.",
                status_code=503,
            ) from error

    return {
        "allowed": True,
        "identity_id":
            authorized.identity_id,
        "tenant_id":
            authorized.tenant_id,
        "correlation_id":
            assurance
            .workload_fact
            .proof_reference,
    }


async def authorize_request(
    request: Request,
    payload: BridgeRequest,
    *,
    identity_provider: Callable[[], Awaitable[SovereignIdentity]] | None = None,
    tenant_provider: Callable[[SovereignIdentity], Awaitable[SovereignIdentity]] | None = None,
    authorization_provider: Callable[[SovereignIdentity, str], Awaitable[SovereignIdentity]] | None = None,
    replay_store: ReplayProvider | None = None,
    config: Mapping[str, str] | None = None,
    trust_verifier: Callable[..., TrustResult] = verify_internal_service_request,
) -> dict[str, Any]:
    """Execute the fixed fail-closed authority sequence with narrow test seams."""
    body = await request.body()
    try:
        keys, service_id, audience = _service_config(config)
        selected_replay = replay_store or InternalServiceReplayRegistry()
        trust = trust_verifier(request=_trust_headers(request), body=body, keys=keys, replay_store=selected_replay)
    except Exception as error:
        if isinstance(error, WilsyAPIException):
            raise
        raise _trust_failure(error) from error
    try:
        identity = await (identity_provider or (lambda: get_current_identity()))()  # type: ignore[call-arg]
        tenant_identity = await (tenant_provider or (lambda value: get_current_tenant_identity(tenant_id=request.headers.get("X-Tenant-ID"), identity=value))) (identity)  # type: ignore[call-arg]
        authorized = await (authorization_provider or _authorize_policy)(tenant_identity, payload.policy_id)
    except (UnauthorizedAccessException, ForbiddenOperationException):
        raise
    except Exception as error:
        raise WilsyAPIException("Authorization authority is unavailable.", status_code=503) from error
    return {"allowed": True, "identity_id": authorized.identity_id, "tenant_id": authorized.tenant_id, "correlation_id": trust.correlation_id}


async def _authorize_policy(identity: SovereignIdentity, policy_id: str) -> SovereignIdentity:
    policies = {"audit:read": RequirePermission("audit:read")}
    policy = policies.get(policy_id)
    if policy is None:
        raise ForbiddenOperationException("Requested authorization policy is not available.")
    return await policy(identity=identity, repository=get_role_assignment_repository())


router = APIRouter(tags=["Internal Python Authority"])


@router.post(ROUTE_PATH)
async def authorize(request: Request, payload: BridgeRequest) -> dict[str, Any]:
    """Authorize one server-controlled policy after service, user, tenant, and role gates."""
    async def current_identity() -> SovereignIdentity:
        authorization = request.headers.get("Authorization")
        credentials = None
        if authorization:
            scheme, _, token = authorization.partition(" ")
            if scheme and token:
                credentials = HTTPAuthorizationCredentials(scheme=scheme, credentials=token)
        return await get_current_identity(
            request,
            credentials=credentials,
            api_key=None,
            repository=get_principal_authority_repository(),
        )

    async def current_tenant(identity: SovereignIdentity) -> SovereignIdentity:
        return await get_current_tenant_identity(
            tenant_id=request.headers.get("X-Tenant-ID"),
            identity=identity,
            repository=get_tenant_membership_repository(),
        )

    return await _authorize_production_request(
        request,
        payload,
        identity_provider=current_identity,
        tenant_provider=current_tenant,
        authorization_provider=_authorize_policy,
    )


__all__ = ["BridgeRequest", "ROUTE_PATH", "authorize", "authorize_request", "router"]

# ARTIFACT: authority_bridge_router.py
# VERSION: v1.1.1-P3-R3G-S6-A3-TRUST-DENIAL-PROVENANCE-MAPPING
# AUTHORITY BOUNDARY: HTTP composition only; Python identity, membership, and authorization remain authoritative.
# TENANT POSTURE: Explicit X-Tenant-ID requires current ACTIVE membership; service metadata never substitutes for tenant authority.
# FAIL-CLOSED POSTURE: Trust, replay, authentication, membership, or authorization failures deny or return bounded 503.
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS remains exclusive.
# END OF WILSY OS SOVEREIGN ARTIFACT
