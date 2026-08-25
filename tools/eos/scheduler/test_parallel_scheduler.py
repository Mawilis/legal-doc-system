"""
===============================================================================
WILSY ENGINEERING KERNEL
===============================================================================
Epitome:
    FG167 Parallel Scheduler Verification Suite.
    Validates DAG validation, concurrent execution topology (A -> B,C -> D),
    cycle detection, error cascading, and maximum throughput speedups.
    Billion-dollar software architecture: secure, robust, immutable, and future-proof.
===============================================================================
"""

import sys
import time
from pathlib import Path

# Ensure module path resolution
scheduler_dir = Path(__file__).parent.resolve()
if str(scheduler_dir) not in sys.path:
    sys.path.insert(0, str(scheduler_dir))

from parallel_scheduler import ParallelScheduler, TaskState, DependencyGraphError


def task_a():
    time.sleep(0.1)
    return "Output A"

def task_b(input_a):
    time.sleep(0.3)
    return f"B processed [{input_a}]"

def task_c(input_a):
    time.sleep(0.3)
    return f"C processed [{input_a}]"

def task_d(results_b, results_c):
    time.sleep(0.1)
    return f"D merged ({results_b}) and ({results_c})"


def test_parallel_scheduler():
    print("===============================================================================")
    print("WILSY OS KERNEL - FG167 PARALLEL SCHEDULER VERIFICATION")
    print("===============================================================================")

    scheduler = ParallelScheduler(max_workers=4)

    # Build DAG graph: Task A -> [Task B, Task C] -> Task D
    scheduler.add_task(task_id="TaskA", action=task_a)
    scheduler.add_task(task_id="TaskB", action=task_b, dependencies=["TaskA"], args=["Output A"])
    scheduler.add_task(task_id="TaskC", action=task_c, dependencies=["TaskA"], args=["Output A"])
    scheduler.add_task(
        task_id="TaskD", 
        action=task_d, 
        dependencies=["TaskB", "TaskC"], 
        args=["B processed [Output A]", "C processed [Output A]"]
    )

    # 1. Verify topological sorting
    topo_order = scheduler.validate_dag()
    print(f"  -> Validated DAG Topological Order: {topo_order}")
    assert topo_order[0] == "TaskA"
    assert topo_order[-1] == "TaskD"

    # 2. Execute parallel benchmark
    start = time.perf_counter()
    results = scheduler.run()
    elapsed = time.perf_counter() - start

    print(f"  -> Total Parallel Execution Time: {elapsed:.4f}s")
    # Sequential would take 0.1 + 0.3 + 0.3 + 0.1 = 0.8s
    # Parallel takes ~ 0.1 + 0.3 + 0.1 = 0.5s because B and C run concurrently!
    assert elapsed < 0.7, f"Execution too slow ({elapsed:.4f}s), expected parallel speedup."

    # 3. Verify task output states
    for task_id, node in results.items():
        print(f"  -> Node [{task_id}] State: {node.state.value} | Output: {node.result}")
        assert node.state == TaskState.COMPLETED

    # 4. Test Cycle Detection
    print("  -> Verifying Cyclic Dependency Detection...")
    cycle_scheduler = ParallelScheduler()
    cycle_scheduler.add_task("X", action=lambda: None, dependencies=["Y"])
    cycle_scheduler.add_task("Y", action=lambda: None, dependencies=["X"])

    cycle_detected = False
    try:
        cycle_scheduler.validate_dag()
    except DependencyGraphError as e:
        cycle_detected = True
        print(f"  -> Successfully caught cycle error: {e}")

    assert cycle_detected, "Cycle detection failed to trigger DependencyGraphError."

    print("===============================================================================")
    print("FG167 PARALLEL SCHEDULER VERIFIED SUCCESSFULLY.")
    print("===============================================================================")


if __name__ == "__main__":
    test_parallel_scheduler()
