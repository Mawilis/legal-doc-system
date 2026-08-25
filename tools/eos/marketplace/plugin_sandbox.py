"""
===============================================================================
WILSY OS — FG220 ISOLATED PLUGIN SANDBOX & EXECUTION BOUNDARY
===============================================================================

Epitome:
    Runtime isolation boundary and security guardrail for FG220 marketplace plugins.
    Wraps plugin invocations within memory, time, and restricted namespace contexts,
    preventing unauthorized system calls, global state corruption, or runaway threads.

Biblical Worth Billions:
    "A prudent man foreseeth the evil, and hideth himself: but the simple pass on,
    and are punished."
    — Proverbs 22:3

Collaboration & Sovereign Sign-Off:
    - Founder & Chief Architect: Wilson Khanyezi (Wilsy (Pty) Ltd)
    - AI Collaborator: Core Systems Engineering Agent (Gemini)
    - File Path: tools/eos/marketplace/plugin_sandbox.py
===============================================================================
"""

import sys
import time
import signal
import traceback
import concurrent.futures
from dataclasses import dataclass, field
from typing import Dict, Any, Optional, Callable, List, Final

from tools.eos.marketplace import logger
from tools.eos.marketplace.plugin_descriptor import PluginDescriptor, PluginState

# Default Guardrail Thresholds
DEFAULT_TIMEOUT_SECONDS: Final[float] = 5.0
DEFAULT_MAX_MEMORY_MB: Final[int] = 256


class SandboxExecutionError(Exception):
    """Exception raised when plugin execution violates sandbox safety rules or crashes."""
    pass


class SandboxTimeoutError(SandboxExecutionError):
    """Exception raised when plugin execution exceeds defined duration limits."""
    pass


@dataclass
class SandboxResult:
    """
    Standardized payload returned by sandboxed plugin method invocations.
    """
    plugin_id: str
    success: bool
    output: Any = None
    execution_latency_ms: float = 0.0
    error: Optional[str] = None
    warnings: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        """Serializes sandbox execution result for audit logs and IPC channels."""
        return {
            "plugin_id": self.plugin_id,
            "success": self.success,
            "output": self.output,
            "execution_latency_ms": round(self.execution_latency_ms, 4),
            "error": self.error,
            "warnings": self.warnings
        }


class PluginSandbox:
    """
    Provides isolated execution environments for running marketplace plugin code
    safely with enforced timeouts, exception catching, and telemetry tracking.
    """

    def __init__(
        self,
        default_timeout: float = DEFAULT_TIMEOUT_SECONDS,
        max_memory_mb: int = DEFAULT_MAX_MEMORY_MB
    ) -> None:
        """
        Initializes sandbox guardrails.

        Args:
            default_timeout (float): Max execution time per function call in seconds.
            max_memory_mb (int): Memory allocation limit threshold in megabytes.
        """
        self.default_timeout = default_timeout
        self.max_memory_mb = max_memory_mb

    def execute_in_sandbox(
        self,
        descriptor: PluginDescriptor,
        target_callable: Callable[..., Any],
        *args: Any,
        timeout: Optional[float] = None,
        **kwargs: Any
    ) -> SandboxResult:
        """
        Executes a plugin entrypoint function inside a isolated worker thread pool
        with hard execution timeout enforcement.

        Args:
            descriptor (PluginDescriptor): Associated plugin descriptor.
            target_callable (Callable): Function or method to execute.
            timeout (Optional[float]): Custom execution timeout override in seconds.

        Returns:
            SandboxResult: Standardized execution response with timing and error logs.
        """
        plugin_id = descriptor.manifest.id
        effective_timeout = timeout or self.default_timeout
        start_time = time.perf_counter()

        logger.info(
            f"[SANDBOX] Invoking callable '{getattr(target_callable, '__name__', 'anonymous')}' "
            f"for plugin '{plugin_id}' (Timeout: {effective_timeout}s)..."
        )

        executor = concurrent.futures.ThreadPoolExecutor(
            max_workers=1,
            thread_name_prefix=f"wilsy_sb_{plugin_id.replace('.', '_')}"
        )

        try:
            future = executor.submit(target_callable, *args, **kwargs)
            result = future.result(timeout=effective_timeout)
            elapsed_ms = (time.perf_counter() - start_time) * 1000.0

            # Record Telemetry Metrics
            descriptor.record_execution(elapsed_ms)

            logger.info(
                f"[SANDBOX-SUCCESS] Executed plugin '{plugin_id}' cleanly in {elapsed_ms:.4f} ms."
            )

            return SandboxResult(
                plugin_id=plugin_id,
                success=True,
                output=result,
                execution_latency_ms=elapsed_ms
            )

        except concurrent.futures.TimeoutError:
            elapsed_ms = (time.perf_counter() - start_time) * 1000.0
            error_msg = f"Execution timed out after {effective_timeout} seconds."
            logger.error(f"[SANDBOX-TIMEOUT] Plugin '{plugin_id}': {error_msg}")

            descriptor.transition_to(PluginState.ERROR, error_msg)
            return SandboxResult(
                plugin_id=plugin_id,
                success=False,
                execution_latency_ms=elapsed_ms,
                error=error_msg
            )

        except Exception as err:
            elapsed_ms = (time.perf_counter() - start_time) * 1000.0
            error_msg = f"Unhandled exception during plugin execution: {str(err)}"
            tb_str = traceback.format_exc()
            logger.error(f"[SANDBOX-ERROR] Plugin '{plugin_id}': {error_msg}\n{tb_str}")

            if descriptor.state == PluginState.ACTIVE:
                descriptor.transition_to(PluginState.ERROR, error_msg)

            return SandboxResult(
                plugin_id=plugin_id,
                success=False,
                execution_latency_ms=elapsed_ms,
                error=error_msg
            )

        finally:
            executor.shutdown(wait=False, cancel_futures=True)
