"""
* Epitome: Absolute Sovereign Enterprise Health Registry for Wilsy OS. 
*          Monitors, aggregates, and reports real-time health telemetry, component liveness, 
*          and sovereign system status across the multi-tenant grid with divine resilience.
* Collaboration Comments: 
    - Architect: Wilsy OS Core Engineering
    - Tier: Billion-Dollar Production Grade (v4.2.0-Sovereign)
    - Standards: Strict Type Hinting, Thread-Safe Concurrency, Immutable Auditing, 
      Zero-Defect Production Execution.
"""

import threading
import logging
import json
from typing import Dict, Any, Optional, Callable
from datetime import datetime, timezone

# Configure high-performance production logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] [WilsyOS-HealthRegistry]: %(message)s"
)
logger = logging.getLogger("EnterpriseHealthRegistry")

class EnterpriseHealthRegistry:
    """
    Core telemetry repository responsible for managing health probes, evaluating 
    subsystem status, and ensuring zero-defect operational availability across Wilsy OS.
    """
    
    _instance: Optional["EnterpriseHealthRegistry"] = None
    _lock: threading.Lock = threading.Lock()

    def __new__(cls) -> "EnterpriseHealthRegistry":
        with cls._lock:
            if cls._instance is None:
                cls._instance = super(EnterpriseHealthRegistry, cls).__new__(cls)
                cls._instance._initialize_registry()
            return cls._instance

    def _initialize_registry(self) -> None:
        """Initializes thread-safe health probe registries and status stores."""
        self._health_probes: Dict[str, Callable[[], bool]] = {}
        self._probe_statuses: Dict[str, Dict[str, Any]] = {}
        self._state_lock: threading.RLock = threading.RLock()
        logger.info("EnterpriseHealthRegistry successfully initialized with sovereign telemetry parameters.")

    def register_probe(self, probe_name: str, probe_func: Callable[[], bool]) -> bool:
        """
        Registers a health probe function for continuous system monitoring.

        Args:
            probe_name (str): Unique identifier of the health probe.
            probe_func (Callable[[], bool]): Executable returning True if healthy, False otherwise.

        Returns:
            bool: True if registration succeeds, False otherwise.
        """
        if not probe_name or not callable(probe_func):
            logger.error(f"Invalid parameters for health probe registration: {probe_name}")
            return False

        with self._state_lock:
            self._health_probes[probe_name] = probe_func
            self._probe_statuses[probe_name] = {
                "status": "REGISTERED",
                "last_checked": None
            }
            logger.info(f"Registered sovereign health probe: {probe_name}")
            return True

    def evaluate_health(self) -> Dict[str, Any]:
        """
        Executes all registered health probes and evaluates overall system health status.
        """
        with self._state_lock:
            logger.info("Evaluating sovereign health telemetry across all Wilsy OS probes...")
            all_healthy = True
            timestamp = datetime.now(timezone.utc).isoformat()

            for name, probe in self._health_probes.items():
                try:
                    is_healthy = probe()
                    status_str = "HEALTHY" if is_healthy else "UNHEALTHY"
                    if not is_healthy:
                        all_healthy = False
                        logger.warning(f"Health probe FAILED: {name}")
                    else:
                        logger.info(f"Health probe PASSED: {name}")

                    self._probe_statuses[name] = {
                        "status": status_str,
                        "last_checked": timestamp
                    }
                except Exception as e:
                    all_healthy = False
                    logger.critical(f"Critical exception raised during health probe '{name}': {str(e)}")
                    self._probe_statuses[name] = {
                        "status": "CRASHED",
                        "error": str(e),
                        "last_checked": timestamp
                    }

            system_status = "ONLINE_HEALTHY" if all_healthy else "DEGRADED"
            report = {
                "timestamp": timestamp,
                "system_status": system_status,
                "total_probes": len(self._health_probes),
                "probe_statuses": self._probe_statuses
            }
            logger.info(f"Sovereign health evaluation completed. System Status: {system_status}")
            return report

    def export_health_report(self) -> str:
        """
        Exports the latest health evaluation report as a formatted JSON payload.
        """
        with self._state_lock:
            report = self.evaluate_health()
            return json.dumps(report, indent=4)

# Global singleton accessor for enterprise dependency injection
health_registry = EnterpriseHealthRegistry()
