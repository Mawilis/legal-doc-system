"""WILSY OS AWS S3 Legal Evidence provider-delete execution adapter.

TITLE: Legal Evidence S3 Provider Delete Adapter
VERSION: v1.0.1-L10A2R-A3-P4-P3-S3-PROVIDER-DELETE-ADAPTER-GOVERNANCE
AUTHORITY: Wilsy OS Core Governance / Python EOS Legal Operations
PURPOSE:
    Execute one already-authorized, version-specific provider deletion against
    AWS S3 and return bounded provider-native execution evidence only.
EPITOME:
    One exact provider/object-version request is translated into one S3
    delete_object call without granting lifecycle, cleanup, reconciliation,
    absence, billing, payment or settlement authority.
ABSOLUTE CANONICAL PATH:
    /Users/wilsonkhanyezi/legal-doc-system/tools/eos/legal_operations/service/legal_evidence_s3_provider_delete_adapter.py
COLLABORATION / OWNERSHIP:
    Python EOS Legal Operations owns adapter semantics. AWS S3 is an external
    capability and evidence source only. Orchestration owns execution sequencing,
    durable claim fencing, evidence persistence and uncertainty handling.
CERTIFICATION OR UPDATE DATE: 2026-10-03
CHANGELOG:
    v1.0.1-L10A2R-A3-P4-P3-S3-PROVIDER-DELETE-ADAPTER-GOVERNANCE repairs sovereign governance metadata and adds the
    mandatory end seal only. Executable module VERSION remains
    v1.0.0-L10A2R-A3-P4-P3-S3-PROVIDER-DELETE-ADAPTER; provider identity, request validation, S3 call shape,
    response validation, evidence shape, exceptions and runtime control flow
    remain unchanged.
    v1.0.0-L10A2R-A3-P4-P3-S3-PROVIDER-DELETE-ADAPTER establishes the version-specific AWS S3 provider-delete adapter.
COMPLIANCE:
    WILSY OS sovereign Legal Operations governance; POPIA section 19; GDPR
    Article 32; SOC 2 CC7.2; ISO 27001.
SECURITY / PRIVACY POSTURE:
    The adapter accepts only opaque provider coordinates and a pre-certified
    request. AWS failures are converted to stable non-sensitive errors. No
    credentials, Mongo state, tenant registry state or lifecycle truth are
    persisted here.
TENANT BOUNDARY:
    Tenant authority arrives only through the exact certified execution request.
    This adapter performs no tenant discovery, tenant lookup or cross-tenant
    reconciliation.
AUTHORITY BOUNDARY:
    This adapter executes one external S3 delete capability only. It does not
    decide orphanhood, retention, legal hold, cleanup authorization, command
    issuance, lifecycle completion, durable reconciliation, physical absence,
    IAM, billing, payment or settlement truth.
TRANSACTION BOUNDARY:
    S3 deletion occurs outside Mongo transactions. This adapter performs no
    Mongo read/write and claims no distributed atomicity.
FAIL-CLOSED DECLARATION:
    Invalid provider identity, malformed provider coordinates, malformed response
    evidence, returned-version divergence and AWS failures reject without
    inventing deletion success. Omitted optional response headers remain unknown.
FINANCIAL AUTHORITY BOUNDARY:
    None. Provider deletion is not financial execution or settlement; Kennel EOS
    remains the exclusive financial execution authority.

EXECUTABLE MODULE VERSION:
    v1.0.0-L10A2R-A3-P4-P3-S3-PROVIDER-DELETE-ADAPTER

PROVIDER IDENTITY:
    aws_s3

SEMANTIC BOUNDARY:
    S3 DELETE REQUEST ACCEPTED
    != OBJECT PHYSICALLY ABSENT
    != DURABLE EXECUTION EVIDENCE COMMITTED
    != RECONCILED
    != CLEANUP COMPLETE
    != PAYMENT EXECUTED
    != SETTLED
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Final, Mapping, NoReturn

from botocore.client import BaseClient
from botocore.exceptions import BotoCoreError, ClientError

from tools.eos.legal_operations.service.legal_evidence_provider_delete_execution_port import (
    LegalEvidenceProviderDeleteExecutionPortError,
    LegalEvidenceProviderDeleteExecutionRequest,
)


VERSION: Final[str] = "v1.0.0-L10A2R-A3-P4-P3-S3-PROVIDER-DELETE-ADAPTER"
PROVIDER_NAME: Final[str] = "aws_s3"


class LegalEvidenceS3ProviderDeleteAdapterError(RuntimeError):
    """Stable non-sensitive S3 provider-delete failure."""

    def __init__(self, code: str) -> None:
        self.code = code
        super().__init__(code)


def _fail(code: str, cause: BaseException | None = None) -> NoReturn:
    error = LegalEvidenceS3ProviderDeleteAdapterError(code)
    if cause is None:
        raise error
    raise error from cause


def _required_text(name: str, value: object, *, limit: int = 2048) -> str:
    if (
        not isinstance(value, str)
        or not value
        or value != value.strip()
        or len(value) > limit
        or any(ord(character) < 32 for character in value)
    ):
        _fail(f"L10A2R_A3_P4_P3_{name.upper()}_INVALID")
    return value


@dataclass(frozen=True, slots=True)
class LegalEvidenceS3ProviderDeleteExecutionEvidence:
    """Provider-only evidence that S3 accepted one version-specific delete."""

    provider_name: str
    storage_reference: str
    object_version_reference: str
    delete_marker: bool | None
    delete_marker_version_reference: str | None

    def __post_init__(self) -> None:
        if self.provider_name != PROVIDER_NAME:
            _fail("L10A2R_A3_P4_P3_PROVIDER_NAME_INVALID")
        object.__setattr__(
            self,
            "storage_reference",
            _required_text("storage_reference", self.storage_reference),
        )
        object.__setattr__(
            self,
            "object_version_reference",
            _required_text(
                "object_version_reference",
                self.object_version_reference,
            ),
        )
        if (
            self.delete_marker is not None
            and not isinstance(self.delete_marker, bool)
        ):
            _fail("L10A2R_A3_P4_P3_DELETE_MARKER_INVALID")
        if self.delete_marker_version_reference is not None:
            object.__setattr__(
                self,
                "delete_marker_version_reference",
                _required_text(
                    "delete_marker_version_reference",
                    self.delete_marker_version_reference,
                ),
            )


class LegalEvidenceS3ProviderDeleteAdapter:
    """Execute exact version-specific S3 deletion for an authorized request."""

    def __init__(self, *, client: BaseClient, bucket: str) -> None:
        if client is None:
            _fail("L10A2R_A3_P4_P3_CLIENT_REQUIRED")
        self._client = client
        self._bucket = _required_text("bucket", bucket, limit=63)

    def execute_delete(
        self,
        request: LegalEvidenceProviderDeleteExecutionRequest,
    ) -> LegalEvidenceS3ProviderDeleteExecutionEvidence:
        if type(request) is not LegalEvidenceProviderDeleteExecutionRequest:
            _fail("L10A2R_A3_P4_P3_DELETE_REQUEST_REQUIRED")

        if request.provider_name != PROVIDER_NAME:
            _fail("L10A2R_A3_P4_P3_PROVIDER_MISMATCH")

        storage_reference = _required_text(
            "storage_reference",
            request.storage_reference,
        )
        object_version_reference = _required_text(
            "object_version_reference",
            request.object_version_reference,
        )

        try:
            response = self._client.delete_object(
                Bucket=self._bucket,
                Key=storage_reference,
                VersionId=object_version_reference,
            )
        except (BotoCoreError, ClientError) as error:
            _fail("L10A2R_A3_P4_P3_PROVIDER_DELETE_FAILED", error)

        if not isinstance(response, Mapping):
            _fail("L10A2R_A3_P4_P3_PROVIDER_RESPONSE_INVALID")

        if "DeleteMarker" in response:
            delete_marker_raw = response["DeleteMarker"]
            if not isinstance(delete_marker_raw, bool):
                _fail("L10A2R_A3_P4_P3_PROVIDER_RESPONSE_INVALID")
            delete_marker: bool | None = delete_marker_raw
        else:
            delete_marker = None

        if "VersionId" in response:
            response_version_raw = response["VersionId"]
            if (
                not isinstance(response_version_raw, str)
                or not response_version_raw
                or response_version_raw != response_version_raw.strip()
            ):
                _fail("L10A2R_A3_P4_P3_PROVIDER_RESPONSE_INVALID")

            if response_version_raw != object_version_reference:
                _fail("L10A2R_A3_P4_P3_PROVIDER_VERSION_MISMATCH")

            response_version: str | None = response_version_raw
        else:
            response_version = None

        delete_marker_version_reference = (
            response_version
            if delete_marker is True
            else None
        )

        return LegalEvidenceS3ProviderDeleteExecutionEvidence(
            provider_name=PROVIDER_NAME,
            storage_reference=storage_reference,
            object_version_reference=object_version_reference,
            delete_marker=delete_marker,
            delete_marker_version_reference=delete_marker_version_reference,
        )

# =============================================================================
# WILSY OS SOVEREIGN ARTIFACT SEAL
# =============================================================================
# ARTIFACT: legal_evidence_s3_provider_delete_adapter.py
# VERSION: v1.0.1-L10A2R-A3-P4-P3-S3-PROVIDER-DELETE-ADAPTER-GOVERNANCE
# AUTHORITY BOUNDARY: exact AWS S3 version-specific delete capability only; no cleanup authorization, lifecycle completion, durable reconciliation, physical-absence, IAM, billing, payment or settlement authority
# TENANT POSTURE: exact tenant authority is inherited from the certified request; adapter performs no tenant discovery or cross-tenant lookup
# FAIL-CLOSED POSTURE: provider mismatch, malformed request/response, version divergence and AWS failure reject without manufactured deletion-success truth
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively
# EXECUTABLE MODULE VERSION: v1.0.0-L10A2R-A3-P4-P3-S3-PROVIDER-DELETE-ADAPTER
# PROVIDER IDENTITY: aws_s3
# END OF WILSY OS SOVEREIGN ARTIFACT
