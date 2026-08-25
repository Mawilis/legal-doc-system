"""
===============================================================================
WILSY ENGINEERING KERNEL — RUNNER (PRODUCTION GRADE)
===============================================================================
Epitome:
    Canonical entry point for Engineering Kernel execution.
    Thin wrapper around the production kernel that provides a synchronous interface.

Production Mandate:
    - Uses the real `WilsyKernelBootstrap` from the production kernel.
    - Exposes a clean `run()` method that returns an immutable session.
    - Handles asyncio event loop management safely.
    - Provides full observability through logging.

Collaboration & Maintenance:
    - Founder & Lead Architect: Wilson Khanyezi
    - Maintainers: Wilsy OS Core Engineering Team
===============================================================================
"""

from __future__ import annotations

import asyncio
import logging
import sys
from dataclasses import dataclass
from typing import Any, Dict, Optional

# Import the kernel from the same package
from . import WilsyKernelBootstrap

logger = logging.getLogger("WilsyOS.Kernel.Runner")


@dataclass
class EngineeringKernelSession:
    """
    Immutable session result from kernel execution.
    Contains the execution ID and the full result dictionary.
    """
    execution_id: str
    result: Dict[str, Any]
    success: bool = True

    def __post_init__(self):
        self.success = self.result.get("status") == "SUCCESS"


class EngineeringKernelPipeline:
    """
    Simple pipeline wrapper that delegates to the real kernel.
    Handles asyncio event loop execution safely.
    """

    def execute(self) -> EngineeringKernelSession:
        """
        Execute the kernel pipeline and return the session result.
        """
        logger.info("Starting Engineering Kernel Pipeline...")
        kernel = WilsyKernelBootstrap()

        try:
            # Use asyncio.run() for safe event loop management
            result = asyncio.run(kernel.boot_and_execute())
            logger.info(f"Pipeline complete. Status: {result.get('status', 'UNKNOWN')}")
        except Exception as e:
            logger.error(f"Pipeline failed: {e}", exc_info=True)
            result = {
                "status": "FAILED",
                "error": str(e),
                "session_id": getattr(kernel, "session_id", "unknown"),
            }

        return EngineeringKernelSession(
            execution_id=result.get("session_id", "unknown"),
            result=result
        )


class EngineeringKernelRunner:
    """
    Read-only Engineering Kernel Runner.

    Responsible only for executing the Engineering Kernel
    pipeline and returning the immutable execution session.
    """

    def __init__(self) -> None:
        self._pipeline = EngineeringKernelPipeline()

    def run(self) -> EngineeringKernelSession:
        """
        Execute the Engineering Kernel pipeline.
        Returns an immutable session with the execution result.
        """
        return self._pipeline.execute()


# ----------------------------------------------------------------------
# CLI ENTRY POINT (for testing)
# ----------------------------------------------------------------------
if __name__ == "__main__":
    import json
    import sys  # ensure sys is available in this scope
    runner = EngineeringKernelRunner()
    session = runner.run()
    print("\n>>> KERNEL RUNNER EXECUTION SESSION <<<")
    print(json.dumps(session.result, indent=2, default=str))
    print("=" * 80)
    print(f"Session ID: {session.execution_id}")
    print(f"Success: {session.success}")
    sys.exit(0 if session.success else 1)
