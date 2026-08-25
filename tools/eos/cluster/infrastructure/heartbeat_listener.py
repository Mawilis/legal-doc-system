"""
===============================================================================
WILSY OS — FG221 CLUSTER ORCHESTRATOR SUBSYSTEM
===============================================================================

File Path:
    tools/eos/cluster/infrastructure/heartbeat_listener.py

Epitome:
    Threaded background health monitoring daemon continually inspecting node and
    worker vitality, automatically transitioning silent or unresponsive compute 
    nodes into OFFLINE or DEGRADED states.

Biblical Worth Billions:
    "The heart of the wise teacheth his mouth, and addeth learning to his lips."
    — Proverbs 16:23

Collaboration & Sovereign Sign-Off:
    - Founder & Chief Architect: Wilson Khanyezi (Wilsy (Pty) Ltd)
    - AI Collaborator: Core Systems Engineering Agent (Gemini)
===============================================================================
"""

import time
import threading
import logging
from datetime import datetime, timezone
from typing import Any, List, Optional

from tools.eos.cluster.domain.worker import Worker
from tools.eos.cluster.domain.worker_status import WorkerStatus

logger = logging.getLogger("wilsy_os.cluster.heartbeat_listener")


class HeartbeatListener:
    """
    Non-blocking background thread worker auditing pulse intervals from all registered 
    cluster compute instances and evicting silent nodes before cascade failures occur.
    """

    def __init__(
        self,
        cluster_manager: Any,
        check_interval_seconds: float = 5.0,
        timeout_seconds: float = 30.0
    ) -> None:
        self.cluster_manager = cluster_manager
        self.check_interval_seconds = check_interval_seconds
        self.timeout_seconds = timeout_seconds

        self._stop_event = threading.Event()
        self._monitor_thread: Optional[threading.Thread] = None
        self._lock = threading.RLock()

    def start(self) -> None:
        """Launches the background heartbeat audit loop in an isolated thread."""
        with self._lock:
            if self._monitor_thread is not None and self._monitor_thread.is_alive():
                logger.warning("[HEARTBEAT_LISTENER] Monitor loop is already running.")
                return

            self._stop_event.clear()
            self._monitor_thread = threading.Thread(
                target=self._run_monitor_loop,
                name="WilsyOS-HeartbeatListener",
                daemon=True
            )
            self._monitor_thread.start()
            logger.info(
                f"[HEARTBEAT_LISTENER_STARTED] Interval: {self.check_interval_seconds}s | "
                f"Timeout: {self.timeout_seconds}s"
            )

    def stop(self) -> None:
        """Signals the background listener thread to gracefully terminate."""
        with self._lock:
            if not self._monitor_thread or not self._monitor_thread.is_alive():
                return

            self._stop_event.set()
            self._monitor_thread.join(timeout=self.check_interval_seconds * 2)
            self._monitor_thread = None
            logger.info("[HEARTBEAT_LISTENER_STOPPED] Monitor thread shut down cleanly.")

    def _run_monitor_loop(self) -> None:
        """Main periodic loop inspecting worker heartbeat timestamps."""
        while not self._stop_event.is_set():
            try:
                self.audit_worker_health()
            except Exception as err:
                logger.error(f"[HEARTBEAT_AUDIT_ERROR] Unexpected error during scan: {err}", exc_info=True)

            self._stop_event.wait(self.check_interval_seconds)

    def audit_worker_health(self) -> List[str]:
        """
        Scans all registered workers across the cluster manager and flags stale workers 
        that failed to issue a heartbeat within `timeout_seconds`.
        """
        now = datetime.now(timezone.utc)
        evicted_worker_ids: List[str] = []

        if not hasattr(self.cluster_manager, "list_workers"):
            return evicted_worker_ids

        workers: List[Worker] = self.cluster_manager.list_workers()

        for worker in workers:
            if worker.status == WorkerStatus.OFFLINE:
                continue

            time_since_heartbeat = (now - worker.last_heartbeat).total_seconds()

            if time_since_heartbeat > self.timeout_seconds:
                logger.warning(
                    f"[HEARTBEAT_TIMEOUT] Worker ID: {worker.worker_id} silent for "
                    f"{time_since_heartbeat:.1f}s (Threshold: {self.timeout_seconds}s). "
                    f"Transitioning to OFFLINE."
                )
                worker.transition_to(WorkerStatus.OFFLINE)
                evicted_worker_ids.append(worker.worker_id)

                # Dispatch notification event if cluster manager supports event bus
                if hasattr(self.cluster_manager, "publish_event"):
                    self.cluster_manager.publish_event("WorkerOfflineTimeout", {
                        "worker_id": worker.worker_id,
                        "node_id": worker.node_id,
                        "last_heartbeat": worker.last_heartbeat.isoformat(),
                        "silent_duration_seconds": time_since_heartbeat
                    })

        return evicted_worker_ids
