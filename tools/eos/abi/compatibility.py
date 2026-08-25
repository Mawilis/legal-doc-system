"""
===============================================================================
WILSY OS KERNEL ARCHITECTURE - ENTERPRISE ENGINEERING PLATFORM
===============================================================================
PROJECT: Wilsy OS (Billion-Dollar Sovereign Infrastructure)
SUBSYSTEM: Kernel ABI & Core Governance Framework
MILESTONE: FG178.5 - Kernel ABI Freeze
MODULE: compatibility.py

COLLABORATION & ARCHITECTURAL NOTICE:
Cross-version compatibility engine. Ensures legacy engine modules or future
ABI extensions run seamlessly without breaking backwards compatibility.
===============================================================================
"""

import logging
import time
from typing import Dict, Any, Optional
from dataclasses import dataclass, field

from tools.eos.abi.kernel_version import Version, ABICompatibilityLevel, KERNEL_VERSION
from tools.eos.abi.kernel_contracts import (
    BaseKernelEngineProtocol,
    ExecutionContextProtocol,
    EngineResultProtocol,
    EngineExecutionStatus,
    LifecyclePhase,
    EngineCapability,
)

logger = logging.getLogger("WilsyOS.ABI.Compatibility")


@dataclass
class AdaptiveEngineResult:
    """Fallback result payload for legacy engines adapted to ABI 1.0."""
    engine_name: str
    status: EngineExecutionStatus
    execution_id: str
    outputs: Dict[str, Any]
    artifacts_created: list = field(default_factory=list)
    events_emitted: list = field(default_factory=list)
    execution_time_ms: float = 0.0
    error_message: Optional[str] = None


class EngineCompatibilityAdapter:
    """
    Wraps legacy engines (pre-FG178.5) to expose the full 5-stage Kernel ABI contract.
    """

    def __init__(self, legacy_engine: Any) -> None:
        self.legacy_engine = legacy_engine
        self.engine_name: str = getattr(legacy_engine, "engine_name", legacy_engine.__class__.__name__)
        self.version: str = getattr(legacy_engine, "version", "0.9.0")
        self.capabilities = [EngineCapability.READ_ONLY]
        self.lifecycle_phase = LifecyclePhase.UNINITIALIZED

    def initialize(self, context: ExecutionContextProtocol) -> None:
        logger.info("Adapter: Initializing legacy engine '%s'", self.engine_name)
        if hasattr(self.legacy_engine, "initialize"):
            self.legacy_engine.initialize(context)
        elif hasattr(self.legacy_engine, "setup"):
            self.legacy_engine.setup(context)
        self.lifecycle_phase = LifecyclePhase.INITIALIZED

    def validate(self, context: ExecutionContextProtocol) -> None:
        logger.info("Adapter: Validating legacy engine '%s'", self.engine_name)
        if hasattr(self.legacy_engine, "validate"):
            self.legacy_engine.validate(context)
        self.lifecycle_phase = LifecyclePhase.VALIDATED

    def execute(self, context: ExecutionContextProtocol) -> EngineResultProtocol:
        logger.info("Adapter: Executing legacy engine '%s'", self.engine_name)
        self.lifecycle_phase = LifecyclePhase.EXECUTING
        start_time = time.time()
        
        try:
            if hasattr(self.legacy_engine, "execute"):
                raw_res = self.legacy_engine.execute(context)
            elif hasattr(self.legacy_engine, "run"):
                raw_res = self.legacy_engine.run(context)
            else:
                raw_res = {"status": "SUCCESS", "result": "Legacy execution complete"}

            elapsed_ms = (time.time() - start_time) * 1000.0
            self.lifecycle_phase = LifecyclePhase.EXECUTED

            if hasattr(raw_res, "status") and hasattr(raw_res, "outputs"):
                return raw_res

            outputs = raw_res if isinstance(raw_res, dict) else {"data": raw_res}
            return AdaptiveEngineResult(
                engine_name=self.engine_name,
                status=EngineExecutionStatus.SUCCESS,
                execution_id=getattr(context, "execution_id", "compat_exec_id"),
                outputs=outputs,
                execution_time_ms=elapsed_ms,
            )
        except Exception as err:
            elapsed_ms = (time.time() - start_time) * 1000.0
            self.lifecycle_phase = LifecyclePhase.FAILED
            logger.error("Adapter execution failed for legacy engine '%s': %s", self.engine_name, err)
            return AdaptiveEngineResult(
                engine_name=self.engine_name,
                status=EngineExecutionStatus.FAILURE,
                execution_id=getattr(context, "execution_id", "compat_exec_id"),
                outputs={},
                execution_time_ms=elapsed_ms,
                error_message=str(err),
            )

    def publish(self, context: ExecutionContextProtocol) -> None:
        logger.info("Adapter: Publishing legacy engine '%s'", self.engine_name)
        if hasattr(self.legacy_engine, "publish"):
            self.legacy_engine.publish(context)
        self.lifecycle_phase = LifecyclePhase.PUBLISHED

    def shutdown(self, context: ExecutionContextProtocol) -> None:
        logger.info("Adapter: Shutting down legacy engine '%s'", self.engine_name)
        if hasattr(self.legacy_engine, "shutdown"):
            self.legacy_engine.shutdown(context)
        elif hasattr(self.legacy_engine, "cleanup"):
            self.legacy_engine.cleanup(context)
        self.lifecycle_phase = LifecyclePhase.SHUTDOWN


class ABICompatibilityManager:
    """
    Evaluates engine compatibility against target Kernel version and adapts when necessary.
    """

    def __init__(self, target_kernel_version: str = KERNEL_VERSION) -> None:
        self.target_version = Version.parse(target_kernel_version)

    def evaluate_compatibility(self, engine: Any) -> ABICompatibilityLevel:
        engine_ver_str = getattr(engine, "version", "1.0.0")
        try:
            engine_ver = Version.parse(engine_ver_str)
            return engine_ver.is_compatible_with(self.target_version)
        except Exception:
            return ABICompatibilityLevel.BACKWARD_COMPATIBLE

    def adapt_engine(self, engine: Any) -> BaseKernelEngineProtocol:
        """Adapts an engine to ensure full Kernel ABI compliance."""
        if isinstance(engine, BaseKernelEngineProtocol):
            return engine
        logger.warning("Engine '%s' does not implement BaseKernelEngineProtocol. Adapting via EngineCompatibilityAdapter.", engine)
        return EngineCompatibilityAdapter(engine)
