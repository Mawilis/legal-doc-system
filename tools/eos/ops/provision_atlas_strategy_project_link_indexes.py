"""TITLE: WILSY OS Atlas Strategy Project Link Index Migration.
VERSION: v1.0.0-ATLAS-EXPLICIT-EMPTY-SOURCE-INDEX-GATE
AUTHORITY: WILSY OS Core Governance / AGENTS.md.
EPITOME: Read-only inspection or explicitly approved, canonical Atlas-only
creation of the two unique indexes for an audited Strategy-to-Project link.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tools/eos/ops/provision_atlas_strategy_project_link_indexes.py
COLLABORATION / OWNERSHIP: StrategyProjectRelationshipRegistry owns the
index contract; EOS operator authorizes a guarded migration on canonical wilsy.
CERTIFICATION / UPDATE DATE: 2026-11-23
CHANGELOG: v1.0.0-ATLAS-EXPLICIT-EMPTY-SOURCE-INDEX-GATE adds an inert
--check path, explicit --apply --confirm-database wilsy, strict Atlas-SRV
target verification, preexisting-data rejection and post-DDL index readback.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2.
SECURITY / PRIVACY POSTURE: Never prints URI, credentials, hosts, documents
or raw exception strings; only bounded result and safe status codes.
TENANT BOUNDARY: Registry unique indexes begin with exact tenant_id.
AUTHORITY BOUNDARY: Operator DDL only; no IAM grants or Strategy command writes.
TRANSACTION BOUNDARY: Mongo index DDL is NOT a multi-collection atomic
transaction. Each step is independently rechecked, with no unsafe rollback.
FINANCIAL AUTHORITY BOUNDARY: Kennel EOS exclusively.
"""
from __future__ import annotations

import argparse
import sys
from typing import Any, Final

from pymongo import MongoClient
from pymongo.uri_parser import parse_uri

from tools.eos.kernel.db import resolve_mongo_uri
from tools.eos.saas.strategy_project_relationship_registry import (
    EVENT_COLLECTION,
    LINK_COLLECTION,
    StrategyProjectLinkError,
    StrategyProjectRelationshipRegistry,
)

VERSION: Final = "v1.0.0-ATLAS-EXPLICIT-EMPTY-SOURCE-INDEX-GATE"
_CANONICAL_DATABASE: Final = "wilsy"
_COLLECTIONS: Final = (LINK_COLLECTION, EVENT_COLLECTION)


class AtlasLinkMigrationError(ValueError):
    """Source-neutral safe error code; does not expose connection details."""

    def __init__(self, code: str) -> None:
        """Bind only a fixed migration status code to the exception."""
        self.code = code
        super().__init__(code)


def _verify_target(uri: str) -> str:
    """Accept only a canonical SRV URI explicitly naming database wilsy.

    The allowlist applies to URI type and named database, not an assumed
    hostname. An authenticated server check is still required before DDL.
    """
    if not uri.startswith("mongodb+srv://"):
        raise AtlasLinkMigrationError("ATLAS_STRATEGY_SRV_REQUIRED")
    try:
        parsed = parse_uri(uri)
    except Exception as exc:
        raise AtlasLinkMigrationError("ATLAS_STRATEGY_URI_INVALID") from exc
    if parsed.get("database") != _CANONICAL_DATABASE:
        raise AtlasLinkMigrationError("ATLAS_STRATEGY_DATABASE_MISMATCH")
    return _CANONICAL_DATABASE


def _inspect(database: Any) -> tuple[bool, bool]:
    """Inspect only collection names, record presence, and unique index spec.

    Absent collections do not cause writes. Any preexisting link/event data
    disallows this bootstrap script; source migration requires its own review.
    """
    names = set(database.list_collection_names())
    nonempty = False
    for name in _COLLECTIONS:
        if name in names and database[name].count_documents({}, limit=1) > 0:
            nonempty = True
    registry = StrategyProjectRelationshipRegistry(database)
    try:
        registry.require_indexes()
        indexed = True
    except StrategyProjectLinkError as exc:
        if exc.code != "STRATEGY_LINK_INDEX_UNAVAILABLE":
            raise
        indexed = False
    return indexed, nonempty


def main(argv: list[str] | None = None) -> int:
    """Run no-write Atlas preflight or explicitly confirmed migration.

    Running the command with no flags or --check cannot create collections,
    indexes, source records, roles, permissions or paid AWS resources. --apply
    may create two Mongo unique indexes on wilsy only after record-empty
    preflight; never interpret the result as strategic outcome completion.
    """
    parser = argparse.ArgumentParser(description="Guarded canonical Atlas Strategy link index migration")
    choice = parser.add_mutually_exclusive_group()
    choice.add_argument("--check", action="store_true", help="Inspect source only; no writes")
    choice.add_argument("--apply", action="store_true", help="Allow two canonical index DDL operations")
    parser.add_argument("--confirm-database", choices=[_CANONICAL_DATABASE], default=None,
                        help="Required explicit confirmation when --apply is used")
    args = parser.parse_args(argv)
    if not args.apply and args.confirm_database is not None:
        parser.error("--confirm-database is only allowed with --apply")
    if args.apply and args.confirm_database != _CANONICAL_DATABASE:
        print("ATLAS_STRATEGY_INDEX_STATE=DENIED")
        print("ERROR_CODE=ATLAS_STRATEGY_EXPLICIT_CONFIRMATION_REQUIRED")
        return 2
    if not args.apply and not args.check:
        print("ATLAS_STRATEGY_INDEX_STATE=DRY_RUN_NOT_EXECUTED")
        print("ACTION=Use --check to inspect; --apply --confirm-database wilsy requires explicit approval")
        return 0
    phase = "PREFLIGHT"
    try:
        uri = resolve_mongo_uri()
        name = _verify_target(uri)
        with MongoClient(uri, serverSelectionTimeoutMS=10000, connectTimeoutMS=10000) as client:
            if not client.admin.command("hello").get("setName"):
                raise AtlasLinkMigrationError("ATLAS_STRATEGY_REPLICA_SET_REQUIRED")
            database = client.get_database(name)
            indexed, nonempty = _inspect(database)
            if args.check:
                print("ATLAS_STRATEGY_INDEX_STATE=" +
                      ("VERIFIED_EXISTING" if indexed else "MISSING_INDEXES"))
                print("ATLAS_STRATEGY_SOURCE_DATA=" + ("PRESENT" if nonempty else "EMPTY"))
                print("DATABASE=wilsy")
                print("DATABASE_MUTATIONS=NONE")
                return 0
            if nonempty:
                raise AtlasLinkMigrationError("ATLAS_STRATEGY_EXISTING_RECORDS_REVIEW_REQUIRED")
            if indexed:
                print("ATLAS_STRATEGY_INDEX_STATE=VERIFIED_EXISTING")
                print("DATABASE=wilsy")
                print("DATABASE_MUTATIONS=NONE")
                return 0
            # Not a transaction: one index may exist if the second fails.
            # A retry must inspect the current state and is safe only while
            # both source collections are still empty.
            phase = "INDEX_DDL"
            StrategyProjectRelationshipRegistry(database).ensure_indexes()
            phase = "INDEX_READBACK"
            StrategyProjectRelationshipRegistry(database).require_indexes()
        print("ATLAS_STRATEGY_INDEX_STATE=VERIFIED")
        print("DATABASE=wilsy")
        print("REQUIRED_UNIQUE_INDEXES=2")
        print("SOURCE_RECORDS_CREATED=0")
        return 0
    except Exception as exc:
        code = exc.code if isinstance(exc, (AtlasLinkMigrationError, StrategyProjectLinkError)) else (
            "ATLAS_STRATEGY_INDEX_OPERATION_UNAVAILABLE")
        print("ATLAS_STRATEGY_INDEX_STATE=FAILED", file=sys.stderr)
        print("ERROR_CODE=" + code, file=sys.stderr)
        print("FAILURE_PHASE=" + phase, file=sys.stderr)
        if phase != "PREFLIGHT":
            print("INDEX_STATE=PARTIAL_POSSIBLE_VERIFY_WITH_CHECK", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())


# ARTIFACT: provision_atlas_strategy_project_link_indexes.py
# VERSION: v1.0.0-ATLAS-EXPLICIT-EMPTY-SOURCE-INDEX-GATE
# AUTHORITY BOUNDARY: Operator-confirmed index DDL only, no source/IAM writes.
# TENANT POSTURE: Exact tenant-scoped unique key specifications.
# FAIL-CLOSED POSTURE: Wrong URI/DB, existing records and unverified source abort.
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively.
# END OF WILSY OS SOVEREIGN ARTIFACT
