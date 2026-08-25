"""
===============================================================================
WILSY OS — FG221 CLUSTER WORKER REGISTRY & CIRCUIT BREAKER SUBSYSTEM
===============================================================================

File Path:
    tools/eos/cluster/application/worker_registry.py

Epitome:
    Manages cluster node and worker topologies, thread-safe state indexing, 
    circuit breaker trip/recovery logic, tenant isolation boundaries, and 
    active worker schedulability filtering.

Biblical Worth Billions:
    "A wise man scales up the city of the mighty and brings down the stronghold 
    in which they trust."
    — Proverbs 21:22

Collaboration & Sovereign Sign-Off:
    - Founder & Chief Architect: Wilson Khanyezi (Wilsy (Pty) Ltd)
    - AI Collaborator: Core Systems Engineering Agent (Gemini)
===============================================================================
"""

import threading
import time
import logging
from enum import Enum
from typing import Dict, List, Optional, Set, Any

from tools.eos.cluster.domain.worker_status import WorkerStatus
from tools.eos.cluster.domain.worker import Worker
from tools.eos.cluster.domain.cluster_node import ClusterNode

logger = logging.getLogger("wilsy_os.cluster.registry")


class CircuitState(Enum):
    CLOSED = "CLOSED"       # Normal operation
    HALF_OPEN = "HALF_OPEN" # Testing recovery
    OPEN = "OPEN"           # Failing, rejecting tasks


class IStateStorageAdapter:
    """Interface for pluggable distributed cluster state persistence."""
    def save_state(self, key: str, data: Dict[str, Any]) -> None:
        raise NotImplementedError
    def load_state(self, key: str) -> Optional[Dict[str, Any]]:
        raise NotImplementedError


class WorkerRegistry:
    """
    Production-grade registry tracking cluster nodes, workers, circuit breakers,
    and schedulability constraints with thread-safe synchronization.
    """

    def __init__(
        self,
        storage_adapter: Optional[IStateStorageAdapter] = None,
        failure_threshold: int = 3,
        reset_cooldown_seconds: float = 30.0
    ) -> None:
        self.storage_adapter = storage_adapter
        self.failure_threshold = failure_threshold
        self.reset_cooldown_seconds = reset_cooldown_seconds

        self._nodes: Dict[str, ClusterNode] = {}
        self._workers: Dict[str, Worker] = {}
        self._worker_metadata: Dict[str, Dict[str, Any]] = {}
        
        # Circuit breaker tracking per worker_id
        self._circuit_states: Dict[str, CircuitState] = {}
        self._failure_counts: Dict[str, int] = {}
        self._last_failure_times: Dict[str, float] = {}

        self._lock = threading.RLock()

    def register_node(self, node: ClusterNode) -> None:
        """Registers or updates a compute host node."""
        with self._lock:
            self._nodes[node.node_id] = node
            logger.info(f"[NODE_REGISTERED] Node ID: {node.node_id} ({node.hostname})")

    def get_node(self, node_id: str) -> Optional[ClusterNode]:
        """Retrieves node by node_id."""
        with self._lock:
            return self._nodes.get(node_id)

    def list_all_nodes(self) -> List[ClusterNode]:
        """Returns all registered nodes."""
        with self._lock:
            return list(self._nodes.values())

    @property
    def node_count(self) -> int:
        with self._lock:
            return len(self._nodes)

    def register_worker(self, worker: Worker, metadata: Optional[Dict[str, Any]] = None) -> None:
        """Registers a worker into the topology and initializes its circuit breaker."""
        with self._lock:
            if worker.status in (WorkerStatus.REGISTERED, None):
                worker.status = WorkerStatus.READY

            self._workers[worker.worker_id] = worker
            self._worker_metadata[worker.worker_id] = metadata or {}
            
            if worker.worker_id not in self._circuit_states:
                self._circuit_states[worker.worker_id] = CircuitState.CLOSED
                self._failure_counts[worker.worker_id] = 0

            logger.info(
                f"[WORKER_REGISTERED] Worker ID: {worker.worker_id} on Node: {worker.node_id} "
                f"| Capabilities: {worker.capabilities}"
            )

    def get_worker(self, worker_id: str) -> Optional[Worker]:
        """Retrieves worker by worker_id."""
        with self._lock:
            return self._workers.get(worker_id)

    def list_all_workers(self) -> List[Worker]:
        """Returns all registered workers."""
        with self._lock:
            return list(self._workers.values())

    def _is_worker_active_status(self, status: Any) -> bool:
        """Helper to evaluate if a worker status is active/schedulable."""
        if isinstance(status, WorkerStatus):
            return status in (WorkerStatus.READY, WorkerStatus.EXECUTING, WorkerStatus.BUSY, WorkerStatus.REGISTERED)
        if isinstance(status, str):
            return status.upper() in ("READY", "EXECUTING", "BUSY", "REGISTERED", "ACTIVE")
        return True

    def list_active_workers(self, tenant_id: Optional[str] = None) -> List[Worker]:
        """
        Returns all active and schedulable workers matching optional tenant constraints.
        """
        with self._lock:
            active_workers = []
            for worker in self._workers.values():
                if self._is_worker_active_status(worker.status):
                    meta = self._worker_metadata.get(worker.worker_id, {})
                    worker_tenant = meta.get("tenant_id")
                    if tenant_id and worker_tenant and worker_tenant != tenant_id:
                        continue
                    active_workers.append(worker)
            return active_workers

    def get_circuit_state(self, worker_id: str) -> CircuitState:
        """Retrieves the current circuit breaker state for a worker, handling cooldown resets."""
        with self._lock:
            state = self._circuit_states.get(worker_id, CircuitState.CLOSED)
            if state == CircuitState.OPEN:
                last_fail = self._last_failure_times.get(worker_id, 0.0)
                if time.time() - last_fail >= self.reset_cooldown_seconds:
                    self._circuit_states[worker_id] = CircuitState.HALF_OPEN
                    logger.info(f"[CIRCUIT_BREAKER_HALF_OPEN] Worker ID: {worker_id} entering cooldown recovery.")
                    return CircuitState.HALF_OPEN
            return state

    def record_execution_success(self, worker_id: str) -> None:
        """Records a successful task execution, resetting circuit breaker state."""
        with self._lock:
            self._failure_counts[worker_id] = 0
            self._circuit_states[worker_id] = CircuitState.CLOSED

    def record_execution_failure(self, worker_id: str) -> None:
        """Records a task execution failure, tripping circuit breaker if threshold is met."""
        with self._lock:
            current_failures = self._failure_counts.get(worker_id, 0) + 1
            self._failure_counts[worker_id] = current_failures
            self._last_failure_times[worker_id] = time.time()

            if current_failures >= self.failure_threshold:
                self._circuit_states[worker_id] = CircuitState.OPEN
                logger.error(
                    f"[CIRCUIT_BREAKER_TRIPPED] Worker ID: {worker_id} tripped OPEN "
                    f"after {current_failures} consecutive failures."
                )
            else:
                # Remain CLOSED until failure threshold is reached
                self._circuit_states[worker_id] = CircuitState.CLOSED

    def is_worker_schedulable(
        self,
        worker: Worker,
        required_capabilities: Optional[Set[str]] = None,
        tenant_id: Optional[str] = None
    ) -> bool:
        """Evaluates whether a worker is eligible for task scheduling."""
        with self._lock:
            # 1. Check Circuit Breaker state
            circuit = self.get_circuit_state(worker.worker_id)
            if circuit == CircuitState.OPEN:
                return False

            # 2. Check Worker Status
            if not self._is_worker_active_status(worker.status):
                return False

            # 3. Check Load vs Capacity
            current_load = getattr(worker, "current_load", 0) or 0
            max_capacity = getattr(worker, "max_capacity", 1) or 1
            if current_load >= max_capacity:
                return False

            # 4. Check Capabilities
            if required_capabilities:
                worker_caps = getattr(worker, "capabilities", set())
                if isinstance(worker_caps, list):
                    worker_caps = set(worker_caps)
                elif not isinstance(worker_caps, set):
                    worker_caps = set()
                if not required_capabilities.issubset(worker_caps):
                    return False

            # 5. Check Tenant Isolation
            meta = self._worker_metadata.get(worker.worker_id, {})
            worker_tenant = meta.get("tenant_id")
            if tenant_id and worker_tenant and worker_tenant != tenant_id:
                return False

            return True
