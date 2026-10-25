"""Deployment bootstrap for the governed legal-evidence reconciliation route.

This module binds only canonical Python EOS authorities. It never provisions
platform decision-audit indexes at request time; deployment must run the
separate provisioner against the same explicit audit URI before startup.
"""
from __future__ import annotations

import hashlib
import json
import logging
import os
import re

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

AUDIT_URI_ENV = "WILSY_LEGAL_EVIDENCE_RECONCILIATION_AUDIT_MONGODB_URI"
AWS_ROLE_ARN_ENV = "WILSY_LEGAL_EVIDENCE_RECONCILIATION_AWS_ROLE_ARN"
_AWS_ROLE_ARN = re.compile(r"arn:[a-z0-9-]+:iam::[0-9]{12}:role/[A-Za-z0-9+=,.@_/-]{1,512}\Z")
_ALLOWED_SOURCE_CREDENTIAL_METHODS = frozenset({"assume-role-with-web-identity", "container-role"})
logger = logging.getLogger(__name__)


def audit_target_fingerprint(uri: str) -> str:
    """Return a credential-free fingerprint of the MongoDB target identity."""
    if not isinstance(uri, str) or not uri.strip():
        raise LegalEvidenceProviderReadOnlyReconciliationRuntimeBootstrapError(
            "RECONCILIATION_AUDIT_URI_REQUIRED"
        )
    try:
        parsed = parse_uri(uri.strip())
        hosts = sorted(
            (str(host).lower(), int(port))
            for host, port in (parsed.get("nodelist") or [])
        )
        options = parsed.get("options") or {}
        identity = {
            "hosts": hosts,
            "srv_fqdn": str(parsed.get("fqdn") or "").lower(),
            "database": parsed.get("database"),
            "replica_set": options.get("replicaSet"),
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
        target_botocore_session._credentials = RefreshableCredentials.create_from_metadata(
            metadata=metadata,
            refresh_using=refresh_assumed_credentials,
            method="assume-role",
            advisory_refresh_timeout=60,
            mandatory_refresh_timeout=30,
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
        target_fingerprint = audit_target_fingerprint(audit_uri)
        business_target_fingerprint = audit_target_fingerprint(business_uri)
    except Exception as error:
        raise LegalEvidenceProviderReadOnlyReconciliationRuntimeBootstrapError(
            "RECONCILIATION_MONGODB_TARGET_INVALID"
        ) from error
    if target_fingerprint == business_target_fingerprint:
        raise LegalEvidenceProviderReadOnlyReconciliationRuntimeBootstrapError(
            "RECONCILIATION_AUDIT_TARGET_NOT_SEPARATE"
        )
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
        storage_configuration = LegalEvidenceS3Configuration(
            bucket=values.get("WILSY_LEGAL_EVIDENCE_S3_BUCKET", ""),
            region=values.get("WILSY_LEGAL_EVIDENCE_S3_REGION", DEFAULT_REGION),
            kms_key_id=values.get("WILSY_LEGAL_EVIDENCE_S3_KMS_KEY_ID", "") or None,
        )
        reconciliation_s3_client = build_reconciliation_readonly_s3_client(
            env=values,
            region=storage_configuration.region,
        )
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
    "LegalEvidenceProviderReadOnlyReconciliationRuntimeBootstrapError",
    "build_legal_evidence_provider_readonly_reconciliation_runtime",
]
