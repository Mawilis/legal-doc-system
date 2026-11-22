"""TITLE: WILSY OS Local Strategy Relationship Index Provisioner.
VERSION: v1.1.0-SAFE-LOOPBACK-PREFLIGHT-DIAGNOSTICS
AUTHORITY: WILSY OS Core Governance / AGENTS.md.
EPITOME: Explicit opt-in, loopback-replica-only provisioning of the two exact
tenant-scoped unique indexes needed by strategy/project link commands.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tools/eos/ops/provision_local_strategy_project_link_indexes.py
COLLABORATION / OWNERSHIP: StrategyProjectRelationshipRegistry owns index
specifications; Python EOS operator owns database credentials and execution.
CERTIFICATION / UPDATE DATE: 2026-11-22
CHANGELOG: v1.1.0-SAFE-LOOPBACK-PREFLIGHT-DIAGNOSTICS introduces an
explicit --check (no-DDL) preflight and safe whitelisted error codes rather
than undifferentiated ValueError; reports whether the configured URI is a
local named replica-set target while never printing credentials or a URI.
CHANGELOG: v1.0.0-LOOPBACK-STRATEGY-LINK-INDEX-PREFLIGHT refuses production
or Atlas URIs, rejects unknown hosts, requires explicit --apply and confirms
unique index names/fields without mutating project or Strategy records.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2.
SECURITY / PRIVACY POSTURE: No secrets or Mongo URI echoed to stdout.
TENANT BOUNDARY: Indexes have tenant_id as leading field; no data migration.
AUTHORITY BOUNDARY: Local operator infrastructure DDL only, not user IAM grant.
FINANCIAL AUTHORITY BOUNDARY: Kennel EOS exclusively.
"""
from __future__ import annotations

import argparse
import sys

from pymongo import MongoClient
from pymongo.uri_parser import parse_uri

from tools.eos.kernel.db import resolve_mongo_uri
from tools.eos.saas.strategy_project_relationship_registry import (
    StrategyProjectRelationshipRegistry, StrategyProjectLinkError,
)

VERSION = "v1.1.0-SAFE-LOOPBACK-PREFLIGHT-DIAGNOSTICS"
_ALLOWED_HOSTS = frozenset({"127.0.0.1", "localhost", "::1"})


def _local_database_name(uri: str) -> str:
    """Prove an explicit single-host loopback Mongo URI with named database."""
    if not uri.startswith("mongodb://"):
        raise ValueError("LOCAL_MONGODB_STANDARD_URI_REQUIRED")
    try:
        parsed = parse_uri(uri)
    except Exception as error:
        raise ValueError("LOCAL_MONGODB_URI_INVALID") from error
    nodes = parsed.get("nodelist", [])
    if not nodes or any(host not in _ALLOWED_HOSTS for host, _port in nodes):
        raise ValueError("LOCAL_MONGODB_LOOPBACK_REQUIRED")
    name = parsed.get("database")
    if not isinstance(name, str) or not name:
        raise ValueError("LOCAL_MONGODB_DATABASE_NAME_REQUIRED")
    if parsed.get("options", {}).get("directConnection") is True:
        raise ValueError("LOCAL_MONGODB_REPLICA_SET_REQUIRED")
    return name


_SAFE_FAILURE_CODES = frozenset({
    "LOCAL_MONGODB_STANDARD_URI_REQUIRED",
    "LOCAL_MONGODB_URI_INVALID",
    "LOCAL_MONGODB_LOOPBACK_REQUIRED",
    "LOCAL_MONGODB_DATABASE_NAME_REQUIRED",
    "LOCAL_MONGODB_REPLICA_SET_REQUIRED",
    "STRATEGY_LINK_INDEX_UNAVAILABLE",
})


def main(argv: list[str] | None = None) -> int:
    """Run no-DDL preflight or explicit loopback-only DDL with safe diagnostics.

    --check never changes any indexes; --apply provisions only the canonical
    configured local replica-set database. No CLI parameter accepts secrets.
    """
    parser = argparse.ArgumentParser(description="Verify local Strategy project link index readiness")
    group = parser.add_mutually_exclusive_group()
    group.add_argument("--check", action="store_true", help="Check URI and local replica set without DDL")
    group.add_argument("--apply", action="store_true", help="Provision required unique indexes in local Mongo")
    args = parser.parse_args(argv)
    if not args.check and not args.apply:
        print("STRATEGY_LINK_INDEX_STATE=DRY_RUN_NOT_EXECUTED")
        print("ACTION=Run --check first; --apply is explicit local index DDL")
        return 0
    try:
        uri = resolve_mongo_uri()
        name = _local_database_name(uri)
        with MongoClient(uri, serverSelectionTimeoutMS=5000, connectTimeoutMS=5000) as client:
            hello = client.admin.command("hello")
            if not hello.get("setName"):
                raise ValueError("LOCAL_MONGODB_REPLICA_SET_REQUIRED")
            source = StrategyProjectRelationshipRegistry(client.get_database(name))
            if args.apply:
                source.ensure_indexes()
                source.require_indexes()
            else:
                # Read-only index metadata is useful but must not be confused
                # with provisioning. This path intentionally never runs DDL.
                try:
                    source.require_indexes()
                    state = "VERIFIED_EXISTING"
                except StrategyProjectLinkError as error:
                    if error.code != "STRATEGY_LINK_INDEX_UNAVAILABLE":
                        raise
                    state = "MISSING_INDEXES"
                print("STRATEGY_LINK_PREFLIGHT=" + state)
                print("INDEX_TARGET=LOOPBACK_REPLICA_SET")
                print("INDEX_MUTATION=NONE")
                return 0
        print("STRATEGY_LINK_INDEX_STATE=VERIFIED")
        print("INDEX_TARGET=LOOPBACK_REPLICA_SET")
        print("PROJECT_AND_STRATEGY_RECORDS=UNCHANGED")
        return 0
    except Exception as error:
        # No exception text from URI parsing or PyMongo: it might contain
        # credentials and remote endpoints. Only our known source-neutral
        # codes can appear in a user-facing diagnostic.
        candidate = (error.code if isinstance(error, StrategyProjectLinkError)
                     else str(error) if isinstance(error, ValueError) else "")
        code = candidate if candidate in _SAFE_FAILURE_CODES else "LOCAL_MONGODB_PREFLIGHT_UNAVAILABLE"
        print("STRATEGY_LINK_INDEX_STATE=FAILED", file=sys.stderr)
        print("ERROR_CODE=" + code, file=sys.stderr)
        print("ERROR_CLASS=" + type(error).__name__, file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())


# ARTIFACT: provision_local_strategy_project_link_indexes.py
# VERSION: v1.1.0-SAFE-LOOPBACK-PREFLIGHT-DIAGNOSTICS
# AUTHORITY BOUNDARY: Explicit operator-local index DDL, no task mutations.
# TENANT POSTURE: Index compound keys begin with exact tenant_id.
# FAIL-CLOSED POSTURE: Atlas, remote, missing DB, direct connection and failed DDL rejected.
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively.
# END OF WILSY OS SOVEREIGN ARTIFACT
