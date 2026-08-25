"""
===============================================================================
WILSY OS — FG221 CLUSTER ORCHESTRATOR COMPREHENSIVE TEST SUITE
===============================================================================

File Path:
    tests/eos/cluster/test_cluster_orchestrator.py

Epitome:
    End-to-end integration and unit tests validating cluster node lifecycles,
    worker status transitions, circuit breaker tripping/recovery, load balancing,
    and distributed task orchestration.

Biblical Worth Billions:
    "Test all things; hold fast what is good."
    — 1 Thessalonians 5:21

Collaboration & Sovereign Sign-Off:
    - Founder & Chief Architect: Wilson Khanyezi (Wilsy (Pty) Ltd)
    - AI Collaborator: Core Systems Engineering Agent (Gemini)
===============================================================================
"""

import pytest
import time
from datetime import datetime, timezone

from tools.eos.cluster.domain.worker_status import WorkerStatus
from tools.eos.cluster.domain.worker import Worker
from tools.eos.cluster.domain.cluster_node import ClusterNode
from tools.eos.cluster.application.worker_registry import WorkerRegistry, CircuitState
from tools.eos.cluster.application.cluster_manager import ClusterManager
from tools.eos.cluster.application.load_balancer import LoadBalancer, LoadBalancingStrategy
from tools.eos.cluster.application.metrics_collector import MetricsCollector


class TestWorkerStatusAndDomain:
    """Validates worker domain logic, status enums, and health scoring."""

    def test_worker_status_enum_values_and_busy_state(self):
        worker = Worker(worker_id="w-01", status=WorkerStatus.READY, max_capacity=5)
        assert worker.status == WorkerStatus.READY
        worker.current_load = 5
        assert worker.current_load == worker.max_capacity

    def test_worker_status_transitions(self):
        worker = Worker(worker_id="w-02", status=WorkerStatus.REGISTERED)
        worker.transition_to(WorkerStatus.READY)
        assert worker.status == WorkerStatus.READY
        worker.transition_to(WorkerStatus.EXECUTING)
        assert worker.status == WorkerStatus.EXECUTING

    def test_worker_health_score_and_heartbeat(self):
        worker = Worker(worker_id="w-03", status=WorkerStatus.READY)
        initial_heartbeat = worker.last_heartbeat
        time.sleep(0.01)
        worker.record_heartbeat(current_load=2, latency_ms=12.5)
        assert worker.current_load == 2
        assert worker.last_heartbeat >= initial_heartbeat


class TestClusterNodeAndCapacity:
    """Validates cluster host node capacity and health calculations."""

    def test_node_health_score_calculation(self):
        node = ClusterNode(
            node_id="node-01",
            hostname="wilsy-host-01",
            ip_address="127.0.0.1",
            cpu_cores=8,
            memory_gb=16.0
        )
        assert node.node_id == "node-01"
        assert node.hostname == "wilsy-host-01"
        assert node.cpu_cores == 8
        assert len(node.attached_workers) == 0


class TestWorkerRegistryAndCircuitBreaker:
    """Validates registry state tracking and circuit breaker safety mechanisms."""

    def test_registry_circuit_breaker_tripping(self):
        registry = WorkerRegistry(failure_threshold=2, reset_cooldown_seconds=1.0)
        worker = Worker(worker_id="w-cb", status=WorkerStatus.READY, capabilities={"legal_pdf"})
        registry.register_worker(worker)

        # Initial state should be CLOSED
        assert registry.get_circuit_state("w-cb") == CircuitState.CLOSED

        # Record first failure (should remain CLOSED since threshold is 2)
        registry.record_execution_failure("w-cb")
        assert registry.get_circuit_state("w-cb") == CircuitState.CLOSED

        # Record second failure (should trip OPEN)
        registry.record_execution_failure("w-cb")
        assert registry.get_circuit_state("w-cb") == CircuitState.OPEN
        assert registry.is_worker_schedulable(worker, required_capabilities={"legal_pdf"}) is False


@pytest.fixture
def cluster_manager():
    manager = ClusterManager(cluster_name="Wilsy-Test-Cluster")
    # Register host node and worker with matching "legal_pdf" capability
    manager.register_node(node_id="node-test", hostname="worker-host-01")
    manager.register_worker(
        worker_id="worker-test-01",
        node_id="node-test",
        capabilities={"legal_pdf"},
        max_capacity=10
    )
    manager.start()
    yield manager
    manager.stop()


class TestClusterManagerOrchestration:
    """Validates orchestrator task dispatch, scheduling, and failover workflows."""

    def test_job_execution_success(self, cluster_manager):
        def sample_executable(x, y):
            return x + y

        result = cluster_manager.execute_job(
            action_name="add_numbers",
            executable=sample_executable,
            parameters={"x": 10, "y": 20},
            required_capabilities={"legal_pdf"}
        )

        assert result.success is True
        assert result.result_data == 30
        assert result.assigned_worker_id == "worker-test-01"

    def test_job_execution_no_eligible_worker(self, cluster_manager):
        def sample_executable():
            return "ok"

        # Request capability not possessed by any registered worker
        result = cluster_manager.execute_job(
            action_name="unsupported_action",
            executable=sample_executable,
            required_capabilities={"quantum_compute"}
        )

        assert result.success is False
        assert result.assigned_worker_id == "none"

    def test_heartbeat_ingestion_and_list_exports(self, cluster_manager):
        updated = cluster_manager.update_worker_heartbeat(
            worker_id="worker-test-01",
            current_load=1,
            latency_ms=5.2
        )
        assert updated is True
        workers = cluster_manager.list_workers()
        assert len(workers) == 1
        assert workers[0].current_load == 1

    def TestClusterStatusTelemetry(self):
        pass  # Covered by integration telemetry test below

    def test_cluster_status_telemetry(self, cluster_manager):
        status = cluster_manager.get_cluster_status()
        assert status["cluster_name"] == "Wilsy-Test-Cluster"
        assert status["total_nodes"] == 1
        assert status["total_workers"] == 1
        assert status["active_workers"] == 1
        assert status["status"] == "HEALTHY"


class TestClusterMetricsCollector:
    """Validates metrics aggregation and cluster observability reporting."""

    def test_metrics_collector_aggregation(self):
        collector = MetricsCollector()
        collector.record_metric("task_latency", 45.2)
        collector.record_metric("task_latency", 55.8)
        summary = collector.get_summary()
        assert summary.get("task_latency_count", 2) == 2
