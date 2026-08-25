"""
===============================================================================
WILSY ENGINEERING KERNEL
===============================================================================
Epitome:
    FG163 Execution Memory Integration & Query Test.
    Validates durable recording, attribute indexing, advanced multi-criteria
    querying, and statistical metrics across historical execution memory.
    Billion-dollar software architecture: secure, robust, immutable, and future-proof.
===============================================================================
"""

import sys
import os

# Ensure root directory is in sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../")))

from tools.eos.history.execution_store import ExecutionStore, ExecutionRecord
from tools.eos.history.execution_index import ExecutionIndex
from tools.eos.history.query_engine import QueryEngine


def test_execution_memory():
    print("===============================================================================")
    print("WILSY OS KERNEL - FG163 EXECUTION MEMORY & QUERY VERIFICATION")
    print("===============================================================================")

    store = ExecutionStore()
    index = ExecutionIndex()
    query_engine = QueryEngine(store, index)

    # 1. Create and record historical execution items
    rec1 = ExecutionRecord(
        execution_id="exec-2026-001",
        engine_id="RepositoryEngine",
        status="success",
        start_time="2026-07-21T10:00:00Z",
        end_time="2026-07-21T10:00:05Z",
        payload={"indexed_files": 1500, "module": "core"},
        metrics={"duration_ms": 5000}
    )
    rec2 = ExecutionRecord(
        execution_id="exec-2026-002",
        engine_id="QualityEngine",
        status="failed",
        start_time="2026-07-21T10:05:00Z",
        end_time="2026-07-21T10:05:02Z",
        payload={"lint_errors": 4},
        error="SyntaxError in compliance module"
    )
    rec3 = ExecutionRecord(
        execution_id="exec-2026-003",
        engine_id="RepositoryEngine",
        status="success",
        start_time="2026-07-21T10:10:00Z",
        end_time="2026-07-21T10:10:04Z",
        payload={"indexed_files": 2789, "module": "eos"},
        metrics={"duration_ms": 4000}
    )

    query_engine.record_and_index(rec1)
    query_engine.record_and_index(rec2)
    query_engine.record_and_index(rec3)
    print("  -> Successfully recorded and indexed 3 execution runs.")

    # 2. Test querying by engine ID
    repo_runs = query_engine.query(engine_id="RepositoryEngine")
    print(f"  -> Query by engine 'RepositoryEngine': found {len(repo_runs)} runs.")
    assert len(repo_runs) == 2

    # 3. Test querying by status
    failed_runs = query_engine.query(status="failed")
    print(f"  -> Query by status 'failed': found {len(failed_runs)} runs.")
    assert len(failed_runs) == 1
    assert failed_runs[0].execution_id == "exec-2026-002"

    # 4. Test querying with keyword search
    keyword_runs = query_engine.query(keyword="SyntaxError")
    print(f"  -> Query by keyword 'SyntaxError': found {len(keyword_runs)} runs.")
    assert len(keyword_runs) == 1

    # 5. Test aggregated statistics
    stats = query_engine.get_statistics()
    print(f"  -> Aggregate Statistics computed:")
    print(f"     - Total Runs: {stats['total_runs']}")
    print(f"     - Success Rate: {stats['success_rate']}%")
    print(f"     - Status Breakdown: {stats['status_breakdown']}")
    assert stats["total_runs"] == 3
    assert stats["success_rate"] == 66.67

    print("===============================================================================")
    print("FG163 EXECUTION MEMORY & QUERY ENGINE VERIFIED SUCCESSFULLY.")
    print("===============================================================================")


if __name__ == "__main__":
    test_execution_memory()
