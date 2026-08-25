"""
===============================================================================
WILSY OS — FG221 CLUSTER ORCHESTRATOR SUBSYSTEM
===============================================================================

File Path:
    tools/eos/cluster/cluster_manager.py

Epitome:
    Unified orchestration facade managing cluster topology, compute node binding,
    worker lifecycle, load balancing, scheduled execution, metrics, and health audits.

Biblical Worth Billions:
    "For as the body is one, and hath many members, and all the members of that 
    one body, being many, are one body: so also is Christ."
    — 1 Corinthians 12:12

Collaboration & Sovereign Sign-Off:
    - Founder & Chief Architect: Wilson Khanyezi (Wilsy (Pty) Ltd)
    - AI Collaborator: Core Systems Engineering Agent (Gemini)
===============================================================================
"""

import threading
import logging
from typing import Dict, List, Optional, Set, Any, Callable

from tools.eos.cluster.domain.cluster_node import ClusterNode
from tools.eos.cluster.domain.worker import Worker
from tools.eos.cluster.domain.worker_status import WorkerStatus
from tools.eos.cluster.application.load_balancer import LoadBalancer, LoadBalancingStrategy
from tools.eos.cluster.application.dispatcher import Dispatcher, TaskExecutionResult
from tools.eos.cluster.application.scheduler import Scheduler
from tools.eos.cluster.infrastructure.heartbeat_listener import HeartbeatListener
from tools.eos.cluster.infrastructure.cluster_metrics import ClusterMetricsCollector, ClusterMetricsSnapshot
from tools.eos.cluster.infrastructure.cluster_report import ClusterReportGenerator

logger = logging.getLogger("wilsy_os.cluster.cluster_manager")


class ClusterManager:
    """
    Central sovereign entry point coordinating hardware nodes, worker allocation, 
    job dispatching, load balancing strategies, and continuous system monitoring.
    """

    def __init__(
        self,
        default_strategy: LoadBalancingStrategy = LoadBalancingStrategy.LEAST_LOADED,
        heartbeat_check_interval: float = 5.0,
        heartbeat_timeout: float = 30.0,
        event_bus: Optional[Any] = None,
        artifact_bus: Optional[Any] = None
    ) -> None:
        self._lock = threading.RLock()
        self.event_bus = event_bus
        self.artifact_bus = artifact_bus

        # Registry tables
        self._nodes: Dict[str, ClusterNode] = {}
        self._workers: Dict[str, Worker] = {}

        # Core operational components
        self.load_balancer = LoadBalancer(default_strategy=default_strategy)
        self.dispatcher = Dispatcher(event_bus=event_bus, artifact_bus=artifact_bus)
        self.scheduler = Scheduler(cluster_manager=self)
        self.metrics_collector = ClusterMetricsCollector()
        self.reporter = ClusterReportGenerator(metrics_collector=self.metrics_collector)
        self.heartbeat_listener = HeartbeatListener(
            cluster_manager=self,
            check_interval_seconds=heartbeat_check_interval,
            timeout_seconds=heartbeat_timeout
        )

    # -------------------------------------------------------------------------
    # Lifecycle Management
    # -------------------------------------------------------------------------

    def start(self) -> None:
        """Starts background monitoring and heartbeat tracking services."""
        logger.info("[CLUSTER_MANAGER_STARTING] Initializing Cluster Orchestrator services.")
        self.heartbeat_listener.start()

    def stop(self) -> None:
        """Gracefully halts background monitoring and flushes active operations."""
        logger.info("[CLUSTER_MANAGER_STOPPING] Shutting down Cluster Orchestrator services.")
        self.heartbeat_listener.stop()

    # -------------------------------------------------------------------------
    # Node Management
    # -------------------------------------------------------------------------

    def register_node(self, node: ClusterNode) -> None:
        """Registers a compute node into the cluster topology."""
        with self._lock:
            if node.node_id in self._nodes:
                logger.warning(f"[NODE_REGISTRATION_EXISTS] Overwriting existing node ID: {node.node_id}")
            self._nodes[node.node_id] = node
            logger.info(f"[NODE_REGISTERED] Node ID: {node.node_id} | Host: {node.hostname} | Cores: {node.cpu_cores}")

    def unregister_node(self, node_id: str) -> bool:
        """Removes a compute node and unbinds its attached workers."""
        with self._lock:
            node = self._nodes.pop(node_id, None)
            if not node:
                return False

            # Detach all associated workers
            for worker_id in list(node.attached_workers):
                self.unregister_worker(worker_id)

            logger.info(f"[NODE_UNREGISTERED] Node ID: {node_id}")
            return True

    def get_node(self, node_id: str) -> Optional[ClusterNode]:
        """Retrieves a registered node by ID."""
        with self._lock:
            return self._nodes.get(node_id)

    def list_nodes(self) -> List[ClusterNode]:
        """Lists all active compute nodes in the cluster."""
        with self._lock:
            return list(self._nodes.values())

    # -------------------------------------------------------------------------
    # Worker Management
    # -------------------------------------------------------------------------

    def register_worker(self, worker: Worker) -> None:
        """Registers a compute worker unit and links it to its parent node if present."""
        with self._lock:
            self._workers[worker.worker_id] = worker

            # Attach to node if node_id matches
            if worker.node_id in self._nodes:
                self._nodes[worker.node_id].attach_worker(worker.worker_id)

            logger.info(
                f"[WORKER_REGISTERED] Worker ID: {worker.worker_id} | Node ID: {worker.node_id} | "
                f"Capacity: {worker.max_capacity} | Status: {worker.status.value}"
            )

    def unregister_worker(self, worker_id: str) -> bool:
        """Unregisters a worker and detaches it from its node."""
        with self._lock:
            worker = self._workers.pop(worker_id, None)
            if not worker:
                return False

            if worker.node_id in self._nodes:
                self._nodes[worker.node_id].detach_worker(worker_id)

            logger.info(f"[WORKER_UNREGISTERED] Worker ID: {worker_id}")
            return True

    def update_worker_heartbeat(
        self,
        worker_id: str,
        current_load: Optional[int] = None,
        latency_ms: Optional[float] = None
    ) -> bool:
        """Updates worker vitality timestamp and load telemetry."""
        with self._lock:
            worker = self._workers.get(worker_id)
            if not worker:
                return False

            worker.heartbeat(current_load=current_load, latency_ms=latency_ms)
            return True

    def get_worker(self, worker_id: str) -> Optional[Worker]:
        """Retrieves a registered worker by ID."""
        with self._lock:
            return self._workers.get(worker_id)

    def list_workers(self) -> List[Worker]:
        """Lists all registered compute workers."""
        with self._lock:
            return list(self._workers.values())

    # -------------------------------------------------------------------------
    # Execution & Routing Facade
    # -------------------------------------------------------------------------

    def execute_job(
        self,
        action_name: str,
        executable: Callable[..., Any],
        parameters: Optional[Dict[str, Any]] = None,
        required_capabilities: Optional[Set[str]] = None,
        target_node_id: Optional[str] = None,
        tenant_id: Optional[str] = None,
        strategy: Optional[LoadBalancingStrategy] = None
    ) -> TaskExecutionResult:
        """
        Selects an available worker using load balancing strategies and dispatches 
        the workload unit synchronously.
        """
        with self._lock:
            candidate_workers = [
                w for w in self._workers.values()
                if w.status in (WorkerStatus.READY, WorkerStatus.EXECUTING, WorkerStatus.BUSY)
            ]

        selected_worker = self.load_balancer.select_worker(
            candidate_workers=candidate_workers,
            strategy=strategy,
            required_capabilities=required_capabilities,
            target_node_id=target_node_id
        )

        if not selected_worker:
            logger.error(
                f"[EXECUTION_FAILED_NO_WORKER] No available workers matched requirements for action: {action_name}"
            )
            result = TaskExecutionResult(
                task_id=f"failed-{action_name}",
                action_name=action_name,
                assigned_worker_id="none",
                success=False,
                error_message="No suitable compute worker available to accept task."
            )
            self.metrics_collector.record_task_completion(0.0, success=False)
            return result

        result = self.dispatcher.dispatch(
            worker=selected_worker,
            action_name=action_name,
            executable=executable,
            parameters=parameters
        )

        self.metrics_collector.record_task_completion(
            execution_time_ms=result.execution_time_ms,
            success=result.success
        )

        return result

    def publish_event(self, event_type: str, payload: Dict[str, Any]) -> None:
        """Relays internal events to the system event bus if attached."""
        if self.event_bus and hasattr(self.event_bus, "publish"):
            try:
                self.event_bus.publish(event_type, payload)
            except Exception as err:
                logger.warning(f"[EVENT_PUBLISH_FAILED] Event {event_type}: {err}")

    # -------------------------------------------------------------------------
    # Telemetry & Reporting
    # -------------------------------------------------------------------------

    def get_metrics_snapshot(self) -> ClusterMetricsSnapshot:
        """Captures a real-time operational snapshot of cluster telemetry."""
        return self.metrics_collector.capture_snapshot(self)

    def generate_ascii_report(self) -> str:
        """Returns an ASCII-formatted topology and metrics dashboard report."""
        return self.reporter.generate_ascii_summary(self)

    def generate_json_report(self) -> Dict[str, Any]:
        """Returns a structured JSON-serializable dictionary audit report."""
        return self.reporter.generate_json_report(self)
