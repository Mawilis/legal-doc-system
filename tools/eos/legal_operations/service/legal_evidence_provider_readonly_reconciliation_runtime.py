"""WILSY OS Legal Evidence Reconciliation Runtime Bootstrap.

TITLE: Legal Evidence Provider Read-Only Reconciliation Runtime
VERSION: v1.0.2-L10A2R-C4D7-RUNTIME-URI-PARSER-FIX
AUTHORITY: WILSY OS Core Governance / Python EOS Legal Operations
EPITOME: Bind the governed reconciliation composition only after explicit
         workload trust, separate TLS audit MongoDB, audit indexes, canonical
         business database, and read-only provider-role requirements validate.
ABSOLUTE CANONICAL PATH:
    /Users/wilsonkhanyezi/legal-doc-system/tools/eos/legal_operations/service/legal_evidence_provider_readonly_reconciliation_runtime.py
COLLABORATION / OWNERSHIP:
    Python EOS Legal Operations owns runtime composition; deployment authority
    owns production secrets, workload identity, MongoDB targets, and role ARN.
CERTIFICATION / UPDATE DATE: 2026-10-25
CHANGELOG:
    v1.0.2-L10A2R-C4D7-RUNTIME-URI-PARSER-FIX adds the missing standard-library
    URL parser import required by TLS enforcement and credential-free target
    identity validation; no authority or configuration fallback is introduced.
COMPLIANCE: AGENTS.md v1.2.0; ENGINEERING_CONSTITUTION.md v1.1.0.
SECURITY / PRIVACY POSTURE:
    Audit URI TLS is mandatory; fingerprints exclude URI credentials. Missing
    deployment authority fails closed; no secrets or raw URIs are logged.
TENANT BOUNDARY:
    Tenant/provider scope is server-configured and resolved by canonical EOS.
AUTHORITY BOUNDARY:
    Bootstrap/composition only; does not create identity, permission, provider
    mutation, orphan, retention, legal-hold, or deletion authority.
FINANCIAL AUTHORITY BOUNDARY:
    Kennel EOS remains the exclusive financial execution authority.
FAIL-CLOSED POSTURE:
    Missing or invalid runtime dependencies prevent composition readiness.
"""
from __future__ import annotations

import hashlib
import json
import logging
import os
import re

from datetime import datetime
from urllib.parse import urlsplit

import boto3
import botocore.session
from botocore.credentials import RefreshableCredentials
from collections.abc import Mapping
from typing import Any

from pymongo import MongoClient
from pymongo.uri_parser import parse_uri

from tools.eos.api.authority_bridge_router import (
    _production_noninteractive_assurance_service,
    _service_config,
)
from tools.eos.auth.current_platform_privileged_eligibility_prerequisite import (
    CurrentPlatformPrivilegedEligibilityPrerequisiteResolver,
)
from tools.eos.auth.current_privileged_eligibility import CurrentPrivilegedEligibilityResolver
from tools.eos.auth.current_system_permission_possession import CurrentSystemPermissionPossessionResolver
from tools.eos.auth.platform_privileged_eligibility_prerequisite_registry import (
    PlatformPrivilegedEligibilityPrerequisiteRegistry,
    COLLECTION as PLATFORM_PREREQUISITE_COLLECTION,
)
from tools.eos.auth.privileged_activation_registry import (
    PrivilegedActivationRegistry,
    COLLECTION as ACTIVATION_COLLECTION,
)
from tools.eos.auth.privileged_activation_use_authority import PrivilegedActivationUseAuthority
from tools.eos.auth.privileged_eligibility_evidence_registry import (
    PrivilegedEligibilityEvidenceRegistry,
    COLLECTION as ELIGIBILITY_EVIDENCE_COLLECTION,
)
from tools.eos.auth.principal_authority_repository import COLLECTION as PRINCIPAL_AUTHORITY_COLLECTION
from tools.eos.auth.system_permission_assignment_registry import (
    SystemPermissionAssignmentRegistry,
    COLLECTION as SYSTEM_PERMISSION_ASSIGNMENT_COLLECTION,
)
from tools.eos.legal_operations.service.legal_evidence_provider_readonly_reconciliation_production_composition import (
    LegalEvidenceProviderReadOnlyReconciliationProductionComposition,
    build_legal_evidence_provider_readonly_reconciliation_production_composition,
)
from tools.eos.legal_operations.service.legal_evidence_s3_storage_adapter import (
    DEFAULT_REGION,
    LegalEvidenceS3Configuration,
)
from tools.eos.legal_operations.service.legal_evidence_provider_readonly_reconciliation_idempotency_registry import (
    COLLECTION as OPERATION_IDEMPOTENCY_COLLECTION,
    LegalEvidenceReconciliationOperationIdempotencyRegistry,
)

VERSION = "v1.0.2-L10A2R-C4D7-RUNTIME-URI-PARSER-FIX"

AUDIT_URI_ENV = "WILSY_LEGAL_EVIDENCE_RECONCILIATION_AUDIT_MONGODB_URI"
AWS_ROLE_ARN_ENV = "WILSY_LEGAL_EVIDENCE_RECONCILIATION_AWS_ROLE_ARN"
_AWS_ROLE_ARN = re.compile(r"arn:[a-z0-9-]+:iam::[0-9]{12}:role/[A-Za-z0-9+=,.@_/-]{1,512}\Z")
_ALLOWED_SOURCE_CREDENTIAL_METHODS = frozenset({"assume-role-with-web-identity", "container-role"})
logger = logging.getLogger(__name__)


def _mongo_deployment_identity(uri: str) -> tuple[str, dict[str, Any]]:
    parsed = parse_uri(uri.strip())
    options = parsed.get("options") or {}
    srv_fqdn = str(parsed.get("fqdn") or "").lower()
    if srv_fqdn:
        kind = "srv"
    else:
        kind = "direct"
    hosts = sorted(
        (str(host).lower(), int(port))
        for host, port in (parsed.get("nodelist") or [])
    )
    if not srv_fqdn and not hosts:
        raise LegalEvidenceProviderReadOnlyReconciliationRuntimeBootstrapError(
            "MONGODB_DEPLOYMENT_IDENTITY_UNPROVEN"
        )
    return kind, {
        "kind": kind,
        "hosts": hosts,
        "srv_fqdn": srv_fqdn,
        "replica_set": options.get("replicaSet") or options.get("replica_set"),
    }


def mongo_deployment_fingerprint(uri: str) -> str:
    """Fingerprint the cluster identity without database or credentials."""
    _, identity = _mongo_deployment_identity(uri)
    encoded = json.dumps(identity, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha3_512(encoded).hexdigest()


def require_distinct_mongo_deployments(business_uri: str, audit_uri: str) -> None:
    business_kind, business_identity = _mongo_deployment_identity(business_uri)
    audit_kind, audit_identity = _mongo_deployment_identity(audit_uri)
    if business_kind != audit_kind:
        raise LegalEvidenceProviderReadOnlyReconciliationRuntimeBootstrapError(
            "BUSINESS_AUDIT_DEPLOYMENT_IDENTITY_UNPROVEN"
        )
    if business_identity == audit_identity:
        raise LegalEvidenceProviderReadOnlyReconciliationRuntimeBootstrapError(
            "RECONCILIATION_AUDIT_TARGET_NOT_SEPARATE"
        )


def require_tls_mongodb_uri(uri: str) -> None:
    parsed = parse_uri(uri.strip())
    scheme = urlsplit(uri.strip()).scheme.lower()
    options = parsed.get("options") or {}
    tls_value = options.get("tls", options.get("ssl"))
    tls_enabled = (
        scheme == "mongodb+srv"
        if tls_value is None
        else tls_value is True or str(tls_value).strip().lower() in {"true", "1"}
    )
    if not tls_enabled:
        raise LegalEvidenceProviderReadOnlyReconciliationRuntimeBootstrapError(
            "RECONCILIATION_AUDIT_TLS_REQUIRED"
        )


def audit_target_fingerprint(uri: str) -> str:
    """Return a credential-free fingerprint of the MongoDB target identity."""
    if not isinstance(uri, str) or not uri.strip():
        raise LegalEvidenceProviderReadOnlyReconciliationRuntimeBootstrapError(
            "RECONCILIATION_AUDIT_URI_REQUIRED"
        )
    try:
        parsed = parse_uri(uri.strip())
        _, deployment_identity = _mongo_deployment_identity(uri)
        identity = {
            "deployment": deployment_identity,
            "database": parsed.get("database"),
        }
        encoded = json.dumps(identity, sort_keys=True, separators=(",", ":")).encode("utf-8")
    except Exception as error:
        raise LegalEvidenceProviderReadOnlyReconciliationRuntimeBootstrapError(
            "RECONCILIATION_MONGODB_TARGET_INVALID"
        ) from error
    return hashlib.sha3_512(encoded).hexdigest()


def build_reconciliation_readonly_s3_client(
    *,
    env: Mapping[str, str],
    region: str,
) -> Any:
    """Assume the dedicated read-only provider role using approved pod identity.

    Ambient node credentials, static environment keys, and local credential
    profiles are deliberately rejected. The assumed credentials are supplied
    only to the reconciliation S3 client; the existing upload route keeps its
    separately governed client and permissions.
    """
    role_arn = env.get(AWS_ROLE_ARN_ENV, "")
    if not isinstance(role_arn, str) or not _AWS_ROLE_ARN.fullmatch(role_arn.strip()):
        raise LegalEvidenceProviderReadOnlyReconciliationRuntimeBootstrapError(
            "RECONCILIATION_AWS_ROLE_ARN_REQUIRED"
        )
    try:
        session = boto3.session.Session()
        source_credentials = session.get_credentials()
        if (
            source_credentials is None
            or getattr(source_credentials, "method", None) not in _ALLOWED_SOURCE_CREDENTIAL_METHODS
        ):
            raise LegalEvidenceProviderReadOnlyReconciliationRuntimeBootstrapError(
                "RECONCILIATION_AWS_WORKLOAD_IDENTITY_UNAVAILABLE"
            )
        sts = session.client("sts", region_name=region)

        def refresh_assumed_credentials() -> dict[str, str]:
            assumed = sts.assume_role(
                RoleArn=role_arn.strip(),
                RoleSessionName="wilsy-legal-evidence-reconciliation",
                DurationSeconds=900,
            )
            credentials = assumed.get("Credentials") if isinstance(assumed, dict) else None
            if not isinstance(credentials, dict):
                raise LegalEvidenceProviderReadOnlyReconciliationRuntimeBootstrapError(
                    "RECONCILIATION_AWS_ROLE_ASSUMPTION_FAILED"
                )
            access_key = credentials.get("AccessKeyId")
            secret_key = credentials.get("SecretAccessKey")
            session_token = credentials.get("SessionToken")
            expiration = credentials.get("Expiration")
            if (
                not all(
                    isinstance(value, str) and value.strip()
                    for value in (access_key, secret_key, session_token)
                )
                or not callable(getattr(expiration, "isoformat", None))
            ):
                raise LegalEvidenceProviderReadOnlyReconciliationRuntimeBootstrapError(
                    "RECONCILIATION_AWS_ROLE_ASSUMPTION_FAILED"
                )
            return {
                "access_key": access_key,
                "secret_key": secret_key,
                "token": session_token,
                "expiry_time": expiration.isoformat(),
            }

        metadata = refresh_assumed_credentials()
        target_botocore_session = botocore.session.get_session()
        target_botocore_session._credentials = RefreshableCredentials(
            access_key=metadata["access_key"],
            secret_key=metadata["secret_key"],
            token=metadata["token"],
            expiry_time=datetime.fromisoformat(metadata["expiry_time"]),
            refresh_using=refresh_assumed_credentials,
            method="assume-role",
            advisory_timeout=60,
            mandatory_timeout=30,
        )
        target_botocore_session.set_config_variable("region", region)
        target_session = boto3.session.Session(botocore_session=target_botocore_session)
        return target_session.client("s3", region_name=region)
    except LegalEvidenceProviderReadOnlyReconciliationRuntimeBootstrapError:
        raise
    except Exception as error:
        raise LegalEvidenceProviderReadOnlyReconciliationRuntimeBootstrapError(
            "RECONCILIATION_AWS_ROLE_ASSUMPTION_FAILED"
        ) from error


class LegalEvidenceProviderReadOnlyReconciliationRuntimeBootstrapError(RuntimeError):
    """Stable startup error without exposing deployment secrets."""


def build_legal_evidence_provider_readonly_reconciliation_runtime(
    *,
    mongo_database: Any,
    env: Mapping[str, str] | None = None,
) -> tuple[LegalEvidenceProviderReadOnlyReconciliationProductionComposition, Any]:
    """Build runtime authority from canonical Mongo collections and explicit config.

    The returned audit client must be retained for application lifetime and
    closed during shutdown. Audit indexes are verified by the composition but
    never created here. Missing or malformed deployment configuration fails
    closed; no fallback URI, audience, tenant, bucket, or workload key exists.
    """
    values = os.environ if env is None else env
    audit_uri = values.get(AUDIT_URI_ENV, "")
    if not isinstance(audit_uri, str) or not audit_uri.strip():
        raise LegalEvidenceProviderReadOnlyReconciliationRuntimeBootstrapError(
            "RECONCILIATION_AUDIT_URI_REQUIRED"
        )
    business_uri = values.get("MONGODB_URI", "")
    if not isinstance(business_uri, str) or not business_uri.strip():
        raise LegalEvidenceProviderReadOnlyReconciliationRuntimeBootstrapError(
            "CANONICAL_BUSINESS_URI_REQUIRED"
        )
    try:
        require_distinct_mongo_deployments(business_uri, audit_uri)
        require_tls_mongodb_uri(audit_uri)
        target_fingerprint = audit_target_fingerprint(audit_uri)
    except LegalEvidenceProviderReadOnlyReconciliationRuntimeBootstrapError:
        raise
    except Exception as error:
        raise LegalEvidenceProviderReadOnlyReconciliationRuntimeBootstrapError(
            "RECONCILIATION_MONGODB_TARGET_INVALID"
        ) from error
    if mongo_database is None or getattr(mongo_database, "client", None) is None:
        raise LegalEvidenceProviderReadOnlyReconciliationRuntimeBootstrapError(
            "CANONICAL_BUSINESS_DATABASE_REQUIRED"
        )

    audit_client = None
    try:
        audit_client = MongoClient(
            audit_uri.strip(),
            tz_aware=True,
            serverSelectionTimeoutMS=5000,
            connectTimeoutMS=5000,
        )
        audit_client.admin.command("ping")
        audit_database = audit_client.get_database()
        if audit_database.client is not audit_client or audit_database.client is mongo_database.client:
            raise LegalEvidenceProviderReadOnlyReconciliationRuntimeBootstrapError(
                "RECONCILIATION_AUDIT_CLIENT_INVALID"
            )

        workload_keys, _service_id, expected_audience = _service_config(values)
        storage_configuration = LegalEvidenceS3Configuration(
            bucket=values.get("WILSY_LEGAL_EVIDENCE_S3_BUCKET", ""),
            region=values.get("WILSY_LEGAL_EVIDENCE_S3_REGION", DEFAULT_REGION),
            kms_key_id=values.get("WILSY_LEGAL_EVIDENCE_S3_KMS_KEY_ID", "") or None,
        )
        reconciliation_s3_client = build_reconciliation_readonly_s3_client(
            env=values,
            region=storage_configuration.region,
        )
        database = mongo_database
        principals = database[PRINCIPAL_AUTHORITY_COLLECTION]

        prerequisite_registry = PlatformPrivilegedEligibilityPrerequisiteRegistry(
            database[PLATFORM_PREREQUISITE_COLLECTION]
        )
        eligibility_registry = PrivilegedEligibilityEvidenceRegistry(
            database[ELIGIBILITY_EVIDENCE_COLLECTION]
        )
        assignment_registry = SystemPermissionAssignmentRegistry(
            database[SYSTEM_PERMISSION_ASSIGNMENT_COLLECTION]
        )
        activation_registry = PrivilegedActivationRegistry(
            database[ACTIVATION_COLLECTION]
        )

        # Existing canonical registry index methods are deployment-startup work,
        # never request-path DDL.
        prerequisite_registry.ensure_indexes()
        eligibility_registry.ensure_indexes()
        assignment_registry.ensure_indexes()
        activation_registry.ensure_indexes()

        platform_resolver = CurrentPlatformPrivilegedEligibilityPrerequisiteResolver(
            principal_collection=principals,
            prerequisite_registry=prerequisite_registry,
        )
        eligibility_resolver = CurrentPrivilegedEligibilityResolver(
            principal_collection=principals,
            membership_collection=database["tenant_memberships"],
            evidence_registry=eligibility_registry,
            platform_prerequisite_resolver=platform_resolver,
            workforce_relationship_collection=database["workforce_relationships"],
        )
        possession_resolver = CurrentSystemPermissionPossessionResolver(
            principal_collection=principals,
            assignment_registry=assignment_registry,
        )
        use_authority = PrivilegedActivationUseAuthority(
            activation_registry=activation_registry,
            eligibility_resolver=eligibility_resolver,
            noninteractive_assurance_service=_production_noninteractive_assurance_service(
                database=database
            ),
        )
        operation_idempotency_registry = LegalEvidenceReconciliationOperationIdempotencyRegistry(
            database[OPERATION_IDEMPOTENCY_COLLECTION]
        )
        operation_idempotency_registry.ensure_indexes()
        composition = build_legal_evidence_provider_readonly_reconciliation_production_composition(
            mongo_database=database,
            audit_database=audit_database,
            audit_client=audit_client,
            use_authority=use_authority,
            permission_possession_resolver=possession_resolver,
            workload_keys=workload_keys,
            expected_audience=expected_audience,
            env=values,
            s3_client=reconciliation_s3_client,
            idempotency_registry=operation_idempotency_registry,
        )
        logger.info(
            "LEGAL_EVIDENCE_RECONCILIATION_AUDIT_TARGET_VERIFIED database=%s AUDIT_TARGET_FINGERPRINT=%s",
            audit_database.name,
            target_fingerprint,
        )
        if composition.business_client is not database.client:
            raise LegalEvidenceProviderReadOnlyReconciliationRuntimeBootstrapError(
                "RECONCILIATION_BUSINESS_CLIENT_BINDING_MISMATCH"
            )
        return composition, audit_client
    except Exception as error:
        if audit_client is not None:
            audit_client.close()
        if isinstance(error, LegalEvidenceProviderReadOnlyReconciliationRuntimeBootstrapError):
            raise
        raise LegalEvidenceProviderReadOnlyReconciliationRuntimeBootstrapError(
            "RECONCILIATION_RUNTIME_COMPOSITION_UNAVAILABLE"
        ) from error


__all__ = [
    "AUDIT_URI_ENV",
    "AWS_ROLE_ARN_ENV",
    "build_reconciliation_readonly_s3_client",
    "audit_target_fingerprint",
    "mongo_deployment_fingerprint",
    "require_distinct_mongo_deployments",
    "require_tls_mongodb_uri",
    "LegalEvidenceProviderReadOnlyReconciliationRuntimeBootstrapError",
    "build_legal_evidence_provider_readonly_reconciliation_runtime",
]

# ==============================================================================
# WILSY OS SOVEREIGN ARTIFACT SEAL
#
# ARTIFACT: legal_evidence_provider_readonly_reconciliation_runtime.py
# VERSION: v1.0.2-L10A2R-C4D7-RUNTIME-URI-PARSER-FIX
# AUTHORITY BOUNDARY: Runtime bootstrap and canonical composition only.
# TENANT POSTURE: Server-owned scope; request input cannot select tenant/provider.
# FAIL-CLOSED POSTURE: Invalid trust, TLS, audit target, indexes, or role blocks readiness.
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively.
# END OF WILSY OS SOVEREIGN ARTIFACT
# ==============================================================================
