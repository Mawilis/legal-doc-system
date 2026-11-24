"""
TITLE: WILSY OS MongoDB Transport Development Certificate
VERSION: v1.3.0-READONLY-CREDENTIAL-PROJECT-PLANS
AUTHORITY: Wilsy OS Core Governance
EPITOME: Compare local Mongo read-only command timings to Atlas execution time.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tools/eos/kernel/mongo_transport_certificate.py
COLLABORATION / OWNERSHIP: Kernel owns the sole Mongo lifecycle; this explicit
                           operator command observes it without creating authority.
CERTIFICATION / UPDATE DATE: 2026-11-24
CHANGELOG: v1.3.0-READONLY-CREDENTIAL-PROJECT-PLANS adds an explicit --plans
mode to inspect synthetic absent-key credential and exact-tenant Projects
query shapes with executionStats. Rejects collection scans, missing expected
indexes, returned records or document examinations; no IAM or data mutations.
CHANGELOG: v1.2.0-COMPLETE-SYNTHETIC-OR-TIMING executes and records the synthetic tenant-scoped $or find before reporting results, checks its empty result, and prevents incomplete samples from being labeled completed.
CHANGELOG: v1.1.0-SYNTHETIC-OR-TRANSPORT-CERT adds bounded synthetic tenant-scoped $or find and explain timings, alongside ping, without reading identities or changing Mongo/authorization authority.
CHANGELOG: v1.0.0-READONLY-TRANSPORT-CERT adds bounded, data-free ping/explain transport measurements.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2; ISO 27001.
SECURITY / PRIVACY POSTURE: No URI, host, credential, tenant, user or document output.
TENANT BOUNDARY: Synthetic absent tenant/user filter only.
AUTHORITY BOUNDARY: No IAM, session, authentication, or business authority.
FINANCIAL AUTHORITY BOUNDARY: Kennel EOS exclusively executes financial commands.
QUERY PLAN BOUNDARY: Synthetic absent keys never represent live authenticated query plans.
"""
from __future__ import annotations

import argparse
import secrets
import statistics
import time
from typing import Any, Final
from bson import ObjectId
from pymongo.errors import PyMongoError
from tools.eos.kernel.db import connect_db, disconnect_db, get_client, get_database

VERSION: Final[str] = "v1.3.0-READONLY-CREDENTIAL-PROJECT-PLANS"
_INDEX: Final[str] = "wilsy_auth_users_tenant_identity_lookup"
_ABSENT: Final[str] = "__WILSY_TRANSPORT_CERT_NEVER_A_REAL_ID__"


def _p95(values: list[float]) -> float:
    """Nearest-rank empirical percentile; no extrapolation."""
    return sorted(values)[(95 * len(values) + 99) // 100 - 1]


def _indexes(node: Any) -> set[str]:
    """Read only index names from a winning plan, ignoring record data."""
    found: set[str] = set()
    if isinstance(node, dict):
        if isinstance(node.get("indexName"), str):
            found.add(node["indexName"])
        for key, value in node.items():
            if key not in {"rejectedPlans", "indexBounds", "filter"}:
                found.update(_indexes(value))
    elif isinstance(node, list):
        for child in node:
            found.update(_indexes(child))
    return found


def _plan_stages(node: Any) -> set[str]:
    """Collect winning-plan stage labels, excluding rejected candidates and query data."""
    stages: set[str] = set()
    if isinstance(node, dict):
        stage = node.get("stage")
        if isinstance(stage, str):
            stages.add(stage)
        for key, value in node.items():
            if key not in {"rejectedPlans", "indexBounds", "filter"}:
                stages.update(_plan_stages(value))
    elif isinstance(node, list):
        for child in node:
            stages.update(_plan_stages(child))
    return stages


def _certify_source_plans(db: Any) -> bool:
    """Inspect absent-key credential and Projects read shapes without revealing data.

    The certificate never reads returned business records. The caller must
    still certify real authenticated plans separately; synthetic planning
    proves only index availability and the bounded query shape.
    """
    absence = "__WILSY_CERT_ABSENT_" + secrets.token_hex(20)
    shapes = (
        ("CREDENTIAL_PRINCIPAL", "principal_credentials",
         {"principal_id": absence}, None,
         "principal_credential_principal_unique"),
        ("CREDENTIAL_EMAIL", "principal_credentials",
         {"normalized_email": absence}, None,
         "principal_credential_email_unique"),
        ("PROJECT_DETAIL", "wilsy_projects",
         {"tenant_id": absence, "project_id": absence, "archived_at": None},
         None, "wilsy_project_tenant_identity_unique"),
        ("PROJECT_LIST", "wilsy_projects",
         {"tenant_id": absence, "archived_at": None},
         [("updated_at", -1), ("project_id", 1)],
         "wilsy_project_tenant_active_recent"),
        ("PROJECT_SUMMARY", "wilsy_projects",
         {"tenant_id": absence, "archived_at": None},
         None, "wilsy_project_tenant_active_recent"),
    )
    for label, collection, predicate, sort, expected_index in shapes:
        # Metadata is inspected, but never changed or provisioned here.
        if expected_index not in db[collection].index_information():
            print(f"EOS_QUERY_PLAN {label}=INDEX_NOT_READY")
            return False
        find: dict[str, Any] = {
            "find": collection, "filter": predicate,
            "projection": {"_id": 1}, "limit": 2, "maxTimeMS": 3000,
        }
        if sort is not None:
            find["sort"] = dict(sort)
        if label == "PROJECT_SUMMARY":
            # The source-owned summary pins this exact index.
            find["hint"] = expected_index
        plan = db.command({
            "explain": find, "verbosity": "executionStats",
            "maxTimeMS": 3000,
        })
        stats = plan.get("executionStats")
        winning = plan.get("queryPlanner", {}).get("winningPlan")
        if not isinstance(stats, dict) or not isinstance(winning, dict):
            print(f"EOS_QUERY_PLAN {label}=UNAVAILABLE")
            return False
        indexes = _indexes(winning)
        stages = _plan_stages(winning)
        scanned = stats.get("totalDocsExamined")
        returned = stats.get("nReturned")
        keys = stats.get("totalKeysExamined")
        if (
            expected_index not in indexes or "COLLSCAN" in stages
            or scanned != 0 or returned != 0
            or not isinstance(keys, int) or isinstance(keys, bool)
        ):
            print(f"EOS_QUERY_PLAN {label}=NOT_CERTIFIED")
            return False
        print(
            f"EOS_QUERY_PLAN {label}=INDEXED index={expected_index} "
            f"keys_examined={keys} docs_examined=0 returned=0"
        )
    return True


def run_certificate(*, samples: int, plans: bool = False) -> int:
    """Observe canonical EOS Mongo round trips, preserving its lifecycle.

    The caller explicitly invokes this command in development. No request
    credentials, tenant authority, user record, or real query result is read.
    Only a synthetic nonexistent tenant-scoped $or is read and explained, and all operations
    are bounded. Failure exits nonzero rather than reporting a false pass.
    """
    if not 3 <= samples <= 15:
        raise ValueError("INVALID_CERTIFICATE_SAMPLE_COUNT")
    connected, _ = connect_db()
    if not connected:
        print("EOS_MONGO_TRANSPORT_CERT=UNAVAILABLE")
        return 2
    try:
        client, db = get_client(), get_database()
        if client is None or db is None:
            print("EOS_MONGO_TRANSPORT_CERT=UNAVAILABLE")
            return 2
        if _INDEX not in db["users"].index_information():
            print("EOS_MONGO_TRANSPORT_CERT=INDEX_NOT_READY")
            return 3
        synthetic_filter = {
            "tenantId": _ABSENT,
            "$or": [
                {"user_id": _ABSENT},
                {"_id": ObjectId("000000000000000000000000")},
            ],
        }
        command = {
            "explain": {
                "find": "users",
                "filter": synthetic_filter,
                "projection": {"_id": 1},
                "limit": 1,
                "maxTimeMS": 3000,
            },
            "verbosity": "executionStats",
            "maxTimeMS": 3000,
        }
        pings: list[float] = []
        client_finds: list[float] = []
        client_explains: list[float] = []
        server_explains: list[float] = []
        for _sample in range(samples):
            started = time.perf_counter_ns()
            client.admin.command({"ping": 1, "maxTimeMS": 3000})
            pings.append((time.perf_counter_ns() - started) / 1_000_000)
            started = time.perf_counter_ns()
            candidates = list(
                db["users"].find(
                    synthetic_filter,
                    {"_id": 1},
                    limit=3,
                    max_time_ms=3000,
                )
            )
            client_finds.append((time.perf_counter_ns() - started) / 1_000_000)
            if candidates:
                print("EOS_MONGO_TRANSPORT_CERT=SYNTHETIC_FILTER_NOT_ABSENT")
                return 4
            started = time.perf_counter_ns()
            plan = db.command(command)
            client_explains.append((time.perf_counter_ns() - started) / 1_000_000)
            stats = plan.get("executionStats", {})
            server_ms = stats.get("executionTimeMillis")
            if (
                not isinstance(server_ms, (int, float))
                or isinstance(server_ms, bool)
                or stats.get("nReturned") != 0
                or stats.get("totalDocsExamined") != 0
                or not _indexes(plan.get("queryPlanner", {}).get("winningPlan"))
            ):
                print("EOS_MONGO_TRANSPORT_CERT=EXPLAIN_NOT_CERTIFIED")
                return 4
            server_explains.append(float(server_ms))
        if not all(
            len(values) == samples
            for values in (pings, client_finds, client_explains, server_explains)
        ):
            print("EOS_MONGO_TRANSPORT_CERT=INCOMPLETE_SAMPLES")
            return 4
        if plans and not _certify_source_plans(db):
            print("EOS_MONGO_TRANSPORT_CERT=SOURCE_PLANS_NOT_CERTIFIED")
            return 4
        print(f"EOS_MONGO_TRANSPORT_CERT=READ_ONLY_COMPLETED samples={samples}")
        for name, data in (
            ("PING_CLIENT", pings),
            ("SYNTHETIC_OR_FIND_CLIENT", client_finds),
            ("EXPLAIN_CLIENT", client_explains),
            ("EXPLAIN_SERVER", server_explains),
        ):
            print(f"{name}_MS median={statistics.median(data):.3f} p95={_p95(data):.3f} max={max(data):.3f}")
        gap = [max(0.0, client_ms - server_ms) for client_ms, server_ms in zip(client_explains, server_explains)]
        print(f"EXPLAIN_OUTSIDE_SERVER_MS median={statistics.median(gap):.3f} p95={_p95(gap):.3f}")
        return 0
    except (PyMongoError, OSError, TypeError, ValueError, KeyError):
        print("EOS_MONGO_TRANSPORT_CERT=TRANSPORT_OR_PLAN_UNAVAILABLE")
        return 4
    finally:
        disconnect_db()


def main() -> int:
    """Run the read-only certificate only when explicitly invoked."""
    parser = argparse.ArgumentParser(description="WILSY EOS read-only Mongo transport certificate")
    parser.add_argument("--samples", type=int, default=5, choices=range(3, 16), metavar="3..15")
    parser.add_argument("--plans", action="store_true", help="Verify absent-key credential and Projects query plans")
    args = parser.parse_args()
    return run_certificate(samples=args.samples, plans=args.plans)


if __name__ == "__main__":
    raise SystemExit(main())

# ARTIFACT: mongo_transport_certificate.py
# VERSION: v1.3.0-READONLY-CREDENTIAL-PROJECT-PLANS
# AUTHORITY BOUNDARY: Explicit read-only Kernel Mongo timing observation.
# TENANT POSTURE: Synthetic absent scope and identity; no record access.
# FAIL-CLOSED POSTURE: Unavailable index, query plan, or Mongo connection is failure.
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively; no financial execution.
# END OF WILSY OS SOVEREIGN ARTIFACT
