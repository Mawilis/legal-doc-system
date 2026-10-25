"""Deployment-only provisioning for reconciliation authorization audit indexes.

Run this as an authorized deployment step with the same
WILSY_LEGAL_EVIDENCE_RECONCILIATION_AUDIT_MONGODB_URI supplied to the EOS
runtime. This command is never called from request handling or application
startup.
"""
from __future__ import annotations

import os

from pymongo import MongoClient

from tools.eos.legal_operations.service.legal_evidence_provider_readonly_reconciliation_production_composition import (
    PlatformAuthorizationDecisionEvidenceIndexProvisioner,
)
from tools.eos.legal_operations.service.legal_evidence_provider_readonly_reconciliation_runtime import (
    AUDIT_URI_ENV,
    LegalEvidenceProviderReadOnlyReconciliationRuntimeBootstrapError,
    audit_target_fingerprint,
    require_distinct_mongo_deployments,
    require_tls_mongodb_uri,
)


def main() -> int:
    uri = os.environ.get(AUDIT_URI_ENV, "").strip()
    if not uri:
        raise SystemExit("RECONCILIATION_AUDIT_URI_REQUIRED")
    business_uri = os.environ.get("MONGODB_URI", "").strip()
    if not business_uri:
        raise SystemExit("CANONICAL_BUSINESS_URI_REQUIRED")
    try:
        require_distinct_mongo_deployments(business_uri, uri)
        require_tls_mongodb_uri(uri)
        audit_fingerprint = audit_target_fingerprint(uri)
    except LegalEvidenceProviderReadOnlyReconciliationRuntimeBootstrapError as error:
        raise SystemExit(str(error)) from None
    except Exception:
        raise SystemExit("MONGODB_TARGET_CONFIGURATION_INVALID") from None

    client = None
    try:
        client = MongoClient(
            uri,
            tz_aware=True,
            serverSelectionTimeoutMS=5000,
            connectTimeoutMS=5000,
        )
        client.admin.command("ping")
        database = client.get_database()
        provisioner = PlatformAuthorizationDecisionEvidenceIndexProvisioner(
            audit_database=database,
            audit_client=client,
        )
        provisioner.provision()
        if not provisioner.verify():
            raise SystemExit("RECONCILIATION_AUDIT_INDEX_VERIFICATION_FAILED")
        print("RECONCILIATION_AUDIT_INDEXES_PROVISIONED_AND_VERIFIED")
        print(f"AUDIT_DATABASE_NAME={provisioner.database_name}")
        print(f"AUDIT_TARGET_FINGERPRINT={audit_target_fingerprint(uri)}")
        print("AUDIT_URI_VALUE=REDACTED")
        return 0
    except SystemExit:
        raise
    except Exception:
        raise SystemExit("RECONCILIATION_AUDIT_PROVISIONING_FAILED") from None
    finally:
        if client is not None:
            client.close()


if __name__ == "__main__":
    raise SystemExit(main())
