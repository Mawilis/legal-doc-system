"""
===============================================================================
WILSY OS — FG221 CLUSTER ORCHESTRATOR SUBSYSTEM
===============================================================================

File Path:
    tools/eos/cluster/application/load_balancer.py

Epitome:
    Deterministic multi-strategy load balancer selecting execution workers based on 
    workload distribution, network latency, capabilities, and node locality.

Biblical Worth Billions:
    "A false balance is abomination to the LORD: but a just weight is his delight."
    — Proverbs 11:1

Collaboration & Sovereign Sign-Off:
    - Founder & Chief Architect: Wilson Khanyezi (Wilsy (Pty) Ltd)
    - AI Collaborator: Core Systems Engineering Agent (Gemini)
===============================================================================
"""

import threading
import logging
from enum import Enum
from typing import List, Optional, Set, Any

from tools.eos.cluster.domain.worker import Worker

logger = logging.getLogger("wilsy_os.cluster.load_balancer")


def _extract_capabilities_set(capabilities: Any) -> Set[str]:
    """Safely extracts a set of uppercase string capabilities from any format."""
    if capabilities is None:
        return set()
    if isinstance(capabilities, set):
        return {str(c).upper() for c in capabilities}
    if isinstance(capabilities, (list, tuple)):
        return {str(c).upper() for c in capabilities}
    if hasattr(capabilities, "to_set") and callable(getattr(capabilities, "to_set")):
        return {str(c).upper() for c in capabilities.to_set()}
    if hasattr(capabilities, "capabilities") and isinstance(getattr(capabilities, "capabilities"), (set, list, tuple)):
        return {str(c).upper() for c in getattr(capabilities, "capabilities")}
    if hasattr(capabilities, "__iter__"):
        try:
            return {str(c).upper() for c in capabilities}
        except TypeError:
            pass
    return set()


class LoadBalancingStrategy(str, Enum):
    """Supported deterministic load balancing strategies for Wilsy OS cluster."""
    ROUND_ROBIN = "ROUND_ROBIN"
    LEAST_LOADED = "LEAST_LOADED"
    LOWEST_LATENCY = "LOWEST_LATENCY"
    CAPABILITY_MATCH = "CAPABILITY_MATCH"
    LOCALITY_AWARE = "LOCALITY_AWARE"


class LoadBalancer:
    """
    Thread-safe workload routing engine providing deterministic worker selection 
    across heterogeneous hardware nodes and capability profiles.
    """

    def __init__(self, default_strategy: LoadBalancingStrategy = LoadBalancingStrategy.LEAST_LOADED) -> None:
        self.default_strategy = default_strategy
        self._lock = threading.RLock()
        self._rr_index = 0

    def select_worker(
        self,
        candidate_workers: List[Worker],
        strategy: Optional[LoadBalancingStrategy] = None,
        required_capabilities: Optional[Set[str]] = None,
        target_node_id: Optional[str] = None
    ) -> Optional[Worker]:
        """
        Selects the optimal worker from candidates according to the requested strategy.
        """
        with self._lock:
            if not candidate_workers:
                logger.warning("[LOAD_BALANCER_NO_CANDIDATES] Selection requested on empty worker list.")
                return None

            selected_strategy = strategy or self.default_strategy

            # Pre-filter candidate list by capabilities if specified
            if required_capabilities:
                req_caps = {c.upper() for c in required_capabilities}
                filtered = [
                    w for w in candidate_workers
                    if req_caps.issubset(_extract_capabilities_set(w.capabilities))
                ]
                if not filtered:
                    logger.warning(
                        f"[LOAD_BALANCER_CAPABILITY_MISMATCH] No workers matched required capabilities: {req_caps}"
                    )
                    return None
                candidate_workers = filtered

            # Filter out over-capacity workers
            available_workers = [w for w in candidate_workers if w.current_load < w.max_capacity]
            if not available_workers:
                logger.warning("[LOAD_BALANCER_BACKPRESSURE] All candidate workers at maximum capacity.")
                return None

            # Dispatch strategy logic
            if selected_strategy == LoadBalancingStrategy.ROUND_ROBIN:
                return self._select_round_robin(available_workers)

            elif selected_strategy == LoadBalancingStrategy.LEAST_LOADED:
                return self._select_least_loaded(available_workers)

            elif selected_strategy == LoadBalancingStrategy.LOWEST_LATENCY:
                return self._select_lowest_latency(available_workers)

            elif selected_strategy == LoadBalancingStrategy.LOCALITY_AWARE:
                return self._select_locality_aware(available_workers, target_node_id)

            elif selected_strategy == LoadBalancingStrategy.CAPABILITY_MATCH:
                return self._select_capability_match(available_workers, required_capabilities)

            return self._select_least_loaded(available_workers)

    def _select_round_robin(self, workers: List[Worker]) -> Worker:
        worker = workers[self._rr_index % len(workers)]
        self._rr_index = (self._rr_index + 1) % len(workers)
        return worker

    def _select_least_loaded(self, workers: List[Worker]) -> Worker:
        # Sort primarily by load ratio (current_load / max_capacity), secondarily by absolute load
        return min(workers, key=lambda w: (w.current_load / max(1, w.max_capacity), w.current_load))

    def _select_lowest_latency(self, workers: List[Worker]) -> Worker:
        return min(workers, key=lambda w: w.latency_ms)

    def _select_locality_aware(self, workers: List[Worker], target_node_id: Optional[str]) -> Worker:
        if target_node_id:
            local_workers = [w for w in workers if w.node_id == target_node_id]
            if local_workers:
                return self._select_least_loaded(local_workers)
        return self._select_least_loaded(workers)

    def _select_capability_match(
        self, 
        workers: List[Worker], 
        required_capabilities: Optional[Set[str]]
    ) -> Worker:
        req_caps = {c.upper() for c in (required_capabilities or set())}
        # Prefer workers whose capabilities tightly match requirements (minimizing extraneous capabilities)
        return min(
            workers,
            key=lambda w: (
                len(_extract_capabilities_set(w.capabilities) - req_caps),
                w.current_load
            )
        )
