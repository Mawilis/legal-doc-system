"""Wilsy PRDCA application caller and deployment composition boundary.

TITLE: Platform Registration and Deployment Certification Authority Application Caller
VERSION: v1.0.0-M11-R8-R3B-P8-P3N
AUTHORITY: Wilsy OS Core Governance
EPITOME: Compose the certified PRDCA runtime with a caller-owned Mongo ledger
         and own the explicit application transaction lifecycle.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tools/eos/governance/prdca_application.py
COLLABORATION / OWNERSHIP: Canonical application caller; prdca_runtime.py owns
                            dependency composition, prdca.py owns certificate
                            semantics, and prdca_ledger.py owns persistence.
CERTIFICATION / UPDATE DATE: 2026-09-10
CHANGELOG: v1.0.0-M11-R8-R3B-P8-P3N establishes dependency-injected Mongo
           application composition with explicit commit/abort ownership.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2.
SECURITY / PRIVACY POSTURE: No client, network, secret, KMS, or provider access
                             occurs during import; all infrastructure is injected.
TENANT BOUNDARY: Platform governance evidence only; no tenant authorization.
AUTHORITY BOUNDARY: Application transaction orchestration only; no new authority.
FINANCIAL AUTHORITY BOUNDARY: Kennel EOS exclusively owns financial execution.
FAIL-CLOSED DECLARATION: Missing dependencies, invalid database names, and
                          failed persistence reject; commit uncertainty is surfaced.
"""
from __future__ import annotations

import re
from pathlib import Path
from typing import Final

from pymongo import MongoClient

from tools.eos.governance.prdca import (
    AuthenticatedRuntimeDeploymentEvidence,
    PRDCACertificateBatch,
    PRDCAKeyResolver,
    PRDCASigner,
)
from tools.eos.governance.prdca_ledger import (
    COLLECTION,
    PRDCAMongoLedger,
    PRDCAMongoSession,
)
from tools.eos.governance.prdca_runtime import PRDCARuntimeComposition, compose_prdca_runtime
from tools.eos.saas.billing.tenant_inbound_provider_credential_metadata_source_registry import (
    TenantInboundCredentialMetadataSourceDescriptor,
)


PRDCA_APPLICATION_OWNER: Final[str] = (
    "WILSY_PLATFORM_REGISTRATION_AND_DEPLOYMENT_CERTIFICATION_AUTHORITY"
)
PRDCA_APPLICATION_VERSION: Final[str] = "v1.0.0-M11-R8-R3B-P8-P3N"
_DATABASE_NAME = re.compile(r"^[a-zA-Z0-9][a-zA-Z0-9_.-]{0,62}$")


class PRDCAApplicationError(ValueError):
    """Fail-closed application composition or dependency error."""


class PRDCAApplication:
    """Canonical application caller for PRDCA certificate persistence.

    The application owns Mongo session creation and transaction commit/abort.
    It never reimplements issuance, verification, canonicalization, or ledger
    persistence; those remain delegated to the certified lower-level owners.
    """

    __slots__ = ("_client", "_ledger", "_runtime")

    def __init__(
        self,
        *,
        mongo_client: MongoClient,
        runtime: PRDCARuntimeComposition,
        ledger: PRDCAMongoLedger,
    ) -> None:
        if mongo_client is None or runtime is None or ledger is None:
            raise PRDCAApplicationError("M11P3N_DEPENDENCIES_REQUIRED")
        self._client = mongo_client
        self._runtime = runtime
        self._ledger = ledger

    @classmethod
    def from_mongo(
        cls,
        *,
        mongo_client: MongoClient,
        database_name: str,
        signer: PRDCASigner,
        key_resolver: PRDCAKeyResolver,
        deployment_evidence_key_resolver: PRDCAKeyResolver,
        clock: object | None = None,
        artifact_root: str | Path | None = None,
    ) -> "PRDCAApplication":
        """Compose the caller from injected Mongo and cryptographic dependencies."""
        if mongo_client is None or not isinstance(database_name, str) or _DATABASE_NAME.fullmatch(database_name) is None:
            raise PRDCAApplicationError("M11P3N_DATABASE_NAME_INVALID")
        database = mongo_client[database_name]
        ledger = PRDCAMongoLedger(database[COLLECTION])
        runtime = compose_prdca_runtime(
            signer=signer,
            key_resolver=key_resolver,
            deployment_evidence_key_resolver=deployment_evidence_key_resolver,
            ledger=ledger,
            clock=clock,
            artifact_root=artifact_root,
        )
        return cls(mongo_client=mongo_client, runtime=runtime, ledger=ledger)

    @property
    def runtime(self) -> PRDCARuntimeComposition:
        """Return the composed runtime for immutable certificate preparation."""
        return self._runtime

    def initialize(self) -> None:
        """Create the certified ledger indexes as an explicit deployment action."""
        self._ledger.ensure_indexes()

    def issue_and_persist_certificate_batch(
        self,
        *,
        source_identity: str,
        source_contract_version: str,
        implementation_identity: str,
        capability_class: str,
        campaign_identity: str,
        authority_key_id: str,
        deployment_evidence: AuthenticatedRuntimeDeploymentEvidence,
        descriptor: TenantInboundCredentialMetadataSourceDescriptor,
    ) -> PRDCACertificateBatch:
        """Issue and durably persist one batch in an application-owned transaction.

        A failed operation is aborted by this caller and re-raised. An uncertain
        commit is never hidden; callers must retry the complete operation in a
        new transaction with the same canonical request and evidence.
        """
        with self._client.start_session() as session:
            session.start_transaction()
            try:
                batch = self._runtime.issue_and_persist_certificate_batch(
                    source_identity=source_identity,
                    source_contract_version=source_contract_version,
                    implementation_identity=implementation_identity,
                    capability_class=capability_class,
                    campaign_identity=campaign_identity,
                    authority_key_id=authority_key_id,
                    deployment_evidence=deployment_evidence,
                    descriptor=descriptor,
                    session=PRDCAMongoSession(session),
                )
                session.commit_transaction()
                return batch
            except BaseException:
                if session.in_transaction:
                    session.abort_transaction()
                raise

    def get_certificate_batch(self, artifact_id: str) -> PRDCACertificateBatch:
        """Read and strictly hydrate one persisted batch by exact artifact ID."""
        return self._ledger.get_by_platform_registration_id(artifact_id)


__all__ = [
    "PRDCAApplication",
    "PRDCAApplicationError",
    "PRDCA_APPLICATION_OWNER",
    "PRDCA_APPLICATION_VERSION",
]


# ARTIFACT: prdca_application.py
# VERSION: v1.0.0-M11-R8-R3B-P8-P3N
# AUTHORITY BOUNDARY: canonical PRDCA application transaction caller only
# TENANT POSTURE: platform governance scope; no tenant authorization
# FAIL-CLOSED POSTURE: explicit injected dependencies and surfaced commit failures
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively
# END OF WILSY OS SOVEREIGN ARTIFACT
