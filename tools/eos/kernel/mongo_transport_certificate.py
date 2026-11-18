"""
TITLE: WILSY OS MongoDB Transport Development Certificate
VERSION: v1.0.0-READONLY-TRANSPORT-CERT
AUTHORITY: Wilsy OS Core Governance
EPITOME: Compare local Mongo read-only command timings to Atlas execution time.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tools/eos/kernel/mongo_transport_certificate.py
COLLABORATION / OWNERSHIP: Kernel owns the sole Mongo lifecycle; this explicit
                           operator command observes it without creating authority.
CERTIFICATION / UPDATE DATE: 2026-11-19
CHANGELOG: v1.0.0-READONLY-TRANSPORT-CERT adds bounded, data-free ping/explain transport measurements.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2; ISO 27001.
SECURITY / PRIVACY POSTURE: No URI, host, credential, tenant, user or document output.
TENANT BOUNDARY: Synthetic absent tenant/user filter only.
AUTHORITY BOUNDARY: No IAM, session, authentication, or business authority.
FINANCIAL AUTHORITY BOUNDARY: Kennel EOS exclusively executes financial commands.
"""
from __future__ import annotations

import argparse
import statistics
import time
from typing import Any, Final
from pymongo.errors import PyMongoError
from tools.eos.kernel.db import connect_db, disconnect_db, get_client, get_database

VERSION: Final[str] = "v1.0.0-READONLY-TRANSPORT-CERT"
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


def run_certificate(*, samples: int) -> int:
    """Observe canonical EOS Mongo round trips, preserving its lifecycle.

    The caller explicitly invokes this command in development. No request
    credentials, tenant authority, user record, or real query result is read.
    Only a synthetic nonexistent equality is explained, and all operations
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
        command = {
            "explain": {
                "find": "users",
                "filter": {"tenantId": _ABSENT, "user_id": _ABSENT},
                "projection": {"_id": 1},
                "limit": 1,
                "maxTimeMS": 3000,
            },
            "verbosity": "executionStats",
            "maxTimeMS": 3000,
        }
        pings: list[float] = []
        client_explains: list[float] = []
        server_explains: list[float] = []
        for _sample in range(samples):
            started = time.perf_counter_ns()
            client.admin.command({"ping": 1, "maxTimeMS": 3000})
            pings.append((time.perf_counter_ns() - started) / 1_000_000)
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
                or _INDEX not in _indexes(plan.get("queryPlanner", {}).get("winningPlan"))
            ):
                print("EOS_MONGO_TRANSPORT_CERT=EXPLAIN_NOT_CERTIFIED")
                return 4
            server_explains.append(float(server_ms))
        print(f"EOS_MONGO_TRANSPORT_CERT=READ_ONLY_COMPLETED samples={samples}")
        for name, data in (
            ("PING_CLIENT", pings),
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
    return run_certificate(samples=parser.parse_args().samples)


if __name__ == "__main__":
    raise SystemExit(main())

# ARTIFACT: mongo_transport_certificate.py
# VERSION: v1.0.0-READONLY-TRANSPORT-CERT
# AUTHORITY BOUNDARY: Explicit read-only Kernel Mongo timing observation.
# TENANT POSTURE: Synthetic absent scope and identity; no record access.
# FAIL-CLOSED POSTURE: Unavailable index, query plan, or Mongo connection is failure.
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively; no financial execution.
# END OF WILSY OS SOVEREIGN ARTIFACT
