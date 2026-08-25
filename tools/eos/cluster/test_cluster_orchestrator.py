"""
===============================================================================
WILSY OS — FG221 CLUSTER ORCHESTRATOR SUBSYSTEM
===============================================================================

File Path:
    tools/eos/cluster/test_cluster_orchestrator.py

Epitome:
    Complete production validation suite verifying domain entity state machines,
    multi-strategy load balancing routing, queue scheduling, heartbeat auditing,
    and cluster reporting components.

Biblical Worth Billions:
    "Prove all things; hold fast that which is good."
    — 1 Thessalonians 5:21

Collaboration & Sovereign Sign-Off:
    - Founder & Chief Architect: Wilson Khanyezi (Wilsy (Pty) Ltd)
    - AI Collaborator: Core Systems Engineering Agent (Gemini)
===============================================================================
"""

import time
import unittest
from datetime import datetime, timezone, timedelta

from tools.eos.cluster.domain.worker_status import WorkerStatus
from tools.eos.cluster.domain.worker_capabilities import WorkerCapabilities
from tools.eos.cluster.domain.cluster_node import ClusterNode
from tools.eos.cluster.domain.worker import Worker
from tools.eos.cluster.application.load_balancer import LoadBalancer, LoadBalancingStrategy
from tools.eos.cluster.application.dispatcher import Dispatcher
from tools.eos.cluster.application.scheduler import Scheduler
from tools.eos.cluster.infrastructure.heartbeat_listener import HeartbeatListener
from tools.eos.cluster.infrastructure.cluster_metrics import ClusterMetricsCollector
from tools.eos.cluster.infrastructure.cluster_report import ClusterReportGenerator
from tools.eos.cluster.cluster_manager import ClusterManager


class TestClusterOrchestrator(unittest.TestCase):
    """Production validation test suite for Wilsy OS Cluster Orchestrator."""

    def setUp(self) -> None:
        self.manager = ClusterManager(
            default_strategy=LoadBalancingStrategy.LEAST_LOADED,
            heartbeat_check_interval=0.1,
            heartbeat_timeout=0.3
        )

        self.node_a = ClusterNode(node_id="node-a", hostname="node-a.wilsy.local", cpu_cores=16, memory_gb=64.0)
        self.node_b = ClusterNode(node_id="node-b", hostname="node-b.wilsy.local", cpu_cores=32, memory_gb=128.0)

        self.manager.register_node(self.node_a)
        self.manager.register_node(self.node_b)

        self.worker_1 = Worker(
            worker_id="w-1",
            node_id="node-a",
            capabilities=WorkerCapabilities({"AI_TRAINING", "DATA_PROCESSING"}),
            max_capacity=5,
            latency_ms=10.0
        )
        self.worker_2 = Worker(
            worker_id="w-2",
            node_id="node-b",
            capabilities=WorkerCapabilities({"DATA_PROCESSING", "GPU_ACCELERATED"}),
            max_capacity=10,
            latency_ms=2.0
        )

        self.manager.register_worker(self.worker_1)
        self.manager.register_worker(self.worker_2)

    def test_node_and_worker_registration(self) -> None:
        """Verifies topology registration, linking, and state queries."""
        nodes = self.manager.list_nodes()
        workers = self.manager.list_workers()

        self.assertEqual(len(nodes), 2)
        self.assertEqual(len(workers), 2)
        self.assertIn("w-1", self.node_a.attached_workers)
        self.assertIn("w-2", self.node_b.attached_workers)

    def test_load_balancer_strategies(self) -> None:
        """Verifies deterministic routing across strategies."""
        lb = LoadBalancer()
        candidates = [self.worker_1, self.worker_2]

        # 1. Least Loaded (worker_2 capacity is 10 vs worker_1 capacity 5; initial load is 0)
        selected = lb.select_worker(candidates, strategy=LoadBalancingStrategy.LEAST_LOADED)
        self.assertIsNotNone(selected)

        # 2. Lowest Latency (worker_2 is 2.0ms vs worker_1 10.0ms)
        selected_lat = lb.select_worker(candidates, strategy=LoadBalancingStrategy.LOWEST_LATENCY)
        self.assertEqual(selected_lat.worker_id, "w-2")

        # 3. Capability Match
        selected_cap = lb.select_worker(
            candidates,
            strategy=LoadBalancingStrategy.CAPABILITY_MATCH,
            required_capabilities={"GPU_ACCELERATED"}
        )
        self.assertEqual(selected_cap.worker_id, "w-2")

        # 4. Locality Aware
        selected_loc = lb.select_worker(
            candidates,
            strategy=LoadBalancingStrategy.LOCALITY_AWARE,
            target_node_id="node-a"
        )
        self.assertEqual(selected_loc.worker_id, "w-1")

    def test_synchronous_job_execution(self) -> None:
        """Verifies dispatcher execution and state accounting."""
        def dummy_compute(a: int, b: int) -> int:
            return a + b

        res = self.manager.execute_job(
            action_name="AddNumbers",
            executable=dummy_compute,
            parameters={"a": 15, "b": 27}
        )

        self.assertTrue(res.success)
        self.assertEqual(res.result_data, 42)
        self.assertGreater(res.execution_time_ms, 0.0)

    def test_scheduler_queue_priority(self) -> None:
        """Verifies priority queue ordering and batch processing."""
        scheduler = Scheduler(cluster_manager=self.manager)

        def echo_val(val: str) -> str:
            return f"Processed-{val}"

        job1 = scheduler.schedule("LowPriority", echo_val, {"val": "Low"}, priority=20)
        job2 = scheduler.schedule("HighPriority", echo_val, {"val": "High"}, priority=1)

        self.assertEqual(scheduler.pending_job_count, 2)

        results = scheduler.process_all_pending()
        self.assertEqual(len(results), 2)
        # First executed job should be HighPriority due to lower priority integer value (1 < 20)
        self.assertEqual(results[0].action_name, "HighPriority")
        self.assertEqual(results[0].result_data, "Processed-High")

    def test_heartbeat_listener_stale_eviction(self) -> None:
        """Verifies automatic marking of unresponsive workers as OFFLINE."""
        stale_worker = Worker(
            worker_id="w-stale",
            node_id="node-a",
            last_heartbeat=datetime.now(timezone.utc) - timedelta(seconds=10)
        )
        self.manager.register_worker(stale_worker)

        listener = HeartbeatListener(cluster_manager=self.manager, timeout_seconds=2.0)
        evicted = listener.audit_worker_health()

        self.assertIn("w-stale", evicted)
        self.assertEqual(stale_worker.status, WorkerStatus.OFFLINE)

    def test_metrics_and_reporting(self) -> None:
        """Verifies telemetry snapshots and report rendering."""
        self.manager.execute_job(
            action_name="QuickJob",
            executable=lambda: "OK"
        )

        snapshot = self.manager.get_metrics_snapshot()
        self.assertEqual(snapshot.total_nodes, 2)
        self.assertEqual(snapshot.total_workers, 2)
        self.assertEqual(snapshot.total_tasks_executed, 1)

        ascii_report = self.manager.generate_ascii_report()
        self.assertIn("WILSY OS — CLUSTER ORCHESTRATOR AUDIT REPORT", ascii_report)
        self.assertIn("node-a.wilsy.local", ascii_report)

        json_report = self.manager.generate_json_report()
        self.assertEqual(json_report["metrics"]["total_nodes"], 2)


if __name__ == "__main__":
    unittest.main()
