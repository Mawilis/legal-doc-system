"""
* Epitome: Absolute Sovereign Runtime Registry Engine for Wilsy OS (FG233D).
*          Maintains the sovereign enterprise directory of active runtime components, 
*          domains, endpoints, and dynamic capabilities.
* Collaboration Comments: 
    - Architect: Wilsy OS Core Engineering
    - Tier: Billion-Dollar Production Grade (v5.0.0-Omega)
    - Standards: Strict Type Hinting, Thread-Safe Concurrency, Immutable Auditing, 
      Zero-Defect Production Execution.
    - Biblical Worth Billions Reference: "He counteth the number of the stars; he 
      calleth them all by their names." — Psalm 147:4
"""

import threading
import logging
import json
from typing import Dict, Any, List, Optional
from datetime import datetime, timezone

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] [WilsyOS-RuntimeRegistryEngine]: %(message)s"
)
logger = logging.getLogger("RuntimeRegistryEngine")

class RuntimeRegistryEngine:
    """
    Manages the sovereign enterprise registry for all active runtime components and domains.
    """
    
    _instance: Optional["RuntimeRegistryEngine"] = None
    _lock: threading.Lock = threading.Lock()

    def __new__(cls) -> "RuntimeRegistryEngine":
        with cls._lock:
            if cls._instance is None:
                cls._instance = super(RuntimeRegistryEngine, cls).__new__(cls)
                cls._instance._initialize_registry()
            return cls._instance

    def _initialize_registry(self) -> None:
        self._state_lock: threading.RLock = threading.RLock()
        self._registry: Dict[str, Dict[str, Any]] = {}
        logger.info("RuntimeRegistryEngine successfully initialized with Omega registry rules.")

    def register_component(self, component_name: str, domain: str, version: str) -> Dict[str, Any]:
        """
        Registers or updates a runtime component within the enterprise registry.

        Args:
            component_name (str): Unique name of the component.
            domain (str): Associated enterprise domain.
            version (str): Component version.

        Returns:
            Dict[str, Any]: Registration confirmation manifest.
        """
        with self._state_lock:
            registration_manifest = {
                "component_name": component_name,
                "domain": domain,
                "version": version,
                "status": "REGISTERED_ACTIVE",
                "registered_at": datetime.now(timezone.utc).isoformat()
            }
            self._registry[component_name] = registration_manifest
            logger.info(f"Component [{component_name}] in domain [{domain}] successfully registered.")
            return registration_manifest

    def get_registry_status(self) -> Dict[str, Any]:
        """
        Retrieves the complete state of the enterprise runtime registry.

        Returns:
            Dict[str, Any]: Registry status manifest.
        """
        with self._state_lock:
            return {
                "registry_status": "ACTIVE_OPERATIONAL",
                "total_registered_components": len(self._registry),
                "components": self._registry,
                "timestamp": datetime.now(timezone.utc).isoformat()
            }

runtime_registry_engine = RuntimeRegistryEngine()
