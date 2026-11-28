"""TITLE: WILSY OS Canonical Atlas Company Publication Index Admission.
VERSION: v1.0.0-EXPLICIT-COMPANY-DOCUMENT-INDEX-ADMISSION
AUTHORITY: WILSY OS Core Governance / AGENTS.md.
EPITOME: Guarded read-only preflight or operator-approved canonical wilsy
Atlas index provisioning required by audited Company Strategy draft/submit/
publish commands; never creates or approves publication records.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tools/eos/ops/provision_atlas_company_document_indexes.py
COLLABORATION / OWNERSHIP: CompanyOperatingDocumentRegistry is canonical
index owner; Python EOS publication and independent IAM remain separate.
CERTIFICATION / UPDATE DATE: 2026-11-23
CHANGELOG: v1.0.0-EXPLICIT-COMPANY-DOCUMENT-INDEX-ADMISSION adds
Atlas-only no-DDL --check, explicit operator confirmation for --apply, empty
source gate, named-database/replica-set verification, three exact unique index
provisions, and durable metadata readback with safe failure classification.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC2 CC7.2.
SECURITY / PRIVACY POSTURE: No connection strings, document bodies, names,
credentials, exception messages or principal identifiers logged.
TENANT BOUNDARY: Source indexes begin with tenant_id; no new IAM grants.
AUTHORITY BOUNDARY: Index DDL only, not an author or independent publisher.
TRANSACTION BOUNDARY: Mongo DDL cannot be atomically rolled back; on failure
re-inspect without automatic index deletion or source mutation.
FINANCIAL AUTHORITY BOUNDARY: Kennel EOS exclusively.
"""
from __future__ import annotations

import argparse
import sys
from typing import Final

from pymongo import MongoClient
from pymongo.uri_parser import parse_uri

from tools.eos.kernel.db import resolve_mongo_uri
from tools.eos.saas.company_operating_document_registry import (
    CompanyOperatingDocumentRegistry, COMMAND_COLLECTION, REVISION_COLLECTION,
)
from tools.eos.saas.domain.company_operating_document import CompanyDocumentError

VERSION: Final = "v1.0.0-EXPLICIT-COMPANY-DOCUMENT-INDEX-ADMISSION"
_DATABASE: Final = "wilsy"
_COLLECTIONS: Final = (REVISION_COLLECTION, COMMAND_COLLECTION)


class CompanyDocumentIndexAdmissionError(ValueError):
    """Fixed safe failure code; external exception text must remain private."""

    def __init__(self, code: str) -> None:
        """Store only a bounded machine-readable operator status."""
        self.code = code
        super().__init__(code)


def _assert_atlas_source(uri: str) -> None:
    """Require canonical Atlas-SRV URI explicitly naming the wilsy database."""
    if not isinstance(uri, str) or not uri.startswith("mongodb+srv://"):
        raise CompanyDocumentIndexAdmissionError("COMPANY_DOC_ATLAS_SRV_REQUIRED")
    try:
        parsed = parse_uri(uri)
    except Exception as error:
        raise CompanyDocumentIndexAdmissionError("COMPANY_DOC_ATLAS_URI_INVALID") from error
    if parsed.get("database") != _DATABASE:
        raise CompanyDocumentIndexAdmissionError("COMPANY_DOC_ATLAS_DATABASE_MISMATCH")


def _inspect(database: object) -> tuple[bool, bool]:
    """Read existing company document source/indexes; never execute DDL."""
    existing = set(database.list_collection_names())
    nonempty = any(
        database[name].count_documents({}, limit=1) > 0
        for name in _COLLECTIONS if name in existing
    )
    registry = CompanyOperatingDocumentRegistry(database)
    try:
        registry.require_command_indexes()
        ready = True
    except CompanyDocumentError as error:
        if error.code != "COMPANY_DOCUMENT_INDEX_PROVISIONING_REQUIRED":
            raise
        ready = False
    return ready, nonempty


def main(argv: list[str] | None = None) -> int:
    """Operate only with explicit local shell command and canonical Atlas URI.

    The no-argument mode is inert. --check may perform read-only metadata
    requests; --apply --confirm-database wilsy provisions three unique indexes
    only when both source collections have no records. Any existing records
    require independent migration review and cannot be overwritten here.
    """
    parser = argparse.ArgumentParser(description="Canonical Atlas Company document index migration")
    actions = parser.add_mutually_exclusive_group()
    actions.add_argument("--check", action="store_true", help="Read-only Atlas index/source preflight")
    actions.add_argument("--apply", action="store_true", help="Provision source-owned unique indexes")
    parser.add_argument("--confirm-database", choices=[_DATABASE],
                        help="Required exact DB acknowledgment for any DDL")
    args = parser.parse_args(argv)
    if not args.apply:
        if args.confirm_database is not None:
            parser.error("--confirm-database requires --apply")
        if not args.check:
            print("COMPANY_DOC_INDEX_STATE=DRY_RUN_NOT_EXECUTED")
            print("ACTION=Run --check before explicit --apply")
            return 0
    elif args.confirm_database != _DATABASE:
        print("COMPANY_DOC_INDEX_STATE=DENIED")
        print("ERROR_CODE=COMPANY_DOC_INDEX_CONFIRMATION_REQUIRED")
        return 2

    phase = "PREFLIGHT"
    try:
        uri = resolve_mongo_uri()
        _assert_atlas_source(uri)
        with MongoClient(uri, serverSelectionTimeoutMS=10000, connectTimeoutMS=10000) as client:
            if not client.admin.command("hello").get("setName"):
                raise CompanyDocumentIndexAdmissionError("COMPANY_DOC_REPLICA_SET_REQUIRED")
            database = client.get_database(_DATABASE)
            ready, nonempty = _inspect(database)
            if args.check:
                print("COMPANY_DOC_INDEX_STATE=" + ("VERIFIED_EXISTING" if ready else "MISSING_INDEXES"))
                print("COMPANY_DOC_SOURCE_DATA=" + ("PRESENT" if nonempty else "EMPTY"))
                print("DATABASE=wilsy")
                print("DATABASE_MUTATIONS=NONE")
                return 0
            if nonempty:
                raise CompanyDocumentIndexAdmissionError("COMPANY_DOC_SOURCE_RECONCILIATION_REQUIRED")
            if ready:
                print("COMPANY_DOC_INDEX_STATE=VERIFIED_EXISTING")
                print("DATABASE_MUTATIONS=NONE")
                return 0
            phase = "INDEX_DDL"
            CompanyOperatingDocumentRegistry(database).provision_indexes()
            phase = "INDEX_READBACK"
            CompanyOperatingDocumentRegistry(database).require_command_indexes()
        print("COMPANY_DOC_INDEX_STATE=VERIFIED")
        print("DATABASE=wilsy")
        print("REQUIRED_UNIQUE_INDEXES=3")
        print("PUBLISHED_STRATEGY_RECORDS_CREATED=0")
        return 0
    except Exception as error:
        code = error.code if isinstance(error, (CompanyDocumentIndexAdmissionError,
                                              CompanyDocumentError)) else "COMPANY_DOC_INDEX_SOURCE_UNAVAILABLE"
        print("COMPANY_DOC_INDEX_STATE=FAILED", file=sys.stderr)
        print("ERROR_CODE=" + code, file=sys.stderr)
        print("FAILURE_PHASE=" + phase, file=sys.stderr)
        if phase != "PREFLIGHT":
            print("INDEX_STATE=PARTIAL_POSSIBLE_RECHECK_REQUIRED", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())


# ARTIFACT: provision_atlas_company_document_indexes.py
# VERSION: v1.0.0-EXPLICIT-COMPANY-DOCUMENT-INDEX-ADMISSION
# AUTHORITY BOUNDARY: Explicit operator DDL only; no company approval rights.
# TENANT POSTURE: Canonical wilsy database and unique tenant-leading indexes.
# FAIL-CLOSED POSTURE: No write without exact source, empty registry and approval.
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively.
# END OF WILSY OS SOVEREIGN ARTIFACT
