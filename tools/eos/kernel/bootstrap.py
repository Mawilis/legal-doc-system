from __future__ import annotations

import logging
import os
import sys
from typing import Any, Iterable, List, Optional, cast

# Enterprise ABI & Registry Imports
from tools.eos.abi import (
    ABICompatibilityManager,
    ABIValidationReport,
    ABIValidator,
    BaseKernelEngineProtocol,
    KernelABI,
    KernelVersionSpec,
)
from tools.eos.kernel.registry import KernelRegistry
from tools.eos.kernel.runtime import KernelRuntimeContext

# Sovereign Kernel Core Imports
try:
    from tools.eos.kernel.contracts import BaseKernelSubsystem
    from tools.eos.kernel.engine import KernelEngine
except ImportError as e:
    raise ImportError("CRITICAL: Kernel Bootstrap requires linked engine and contract subsystems.") from e

# Structured Institutional Logging
logger = logging.getLogger("WilsyOS.Kernel.Bootstrap")
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")


# ═══════════════════════════════════════════════════════════════════════════════
# SOVEREIGN BOOTLOADER SUBSYSTEM
# ═══════════════════════════════════════════════════════════════════════════════

class KernelBootstrap(BaseKernelSubsystem):
    """
    Institutional Purpose:
        Sovereign Engineering Kernel Bootstrap Gatekeeper. Responsible for initializing,
        validating, and locking the Wilsy OS Engineering Kernel runtime. Enforces
        Kernel ABI compliance across all system engines before releasing the immutable runtime context.
    """

    VERSION = "3.1.0-Sovereign"
    STARTUP_MODE = "ENTERPRISE_SECURE"

    def __init__(
        self,
        enforce_strict_abi: bool = True,
        auto_adapt_legacy: bool = True,
        consensus_threshold: float = 80.0,
        strict_mode: bool = True,
    ) -> None:
        super().__init__("KernelBootstrap")
        self.enforce_strict_abi = enforce_strict_abi
        self.auto_adapt_legacy = auto_adapt_legacy
        self.consensus_threshold = consensus_threshold
        self.strict_mode = strict_mode

        self.validator = ABIValidator(enforce_strict=enforce_strict_abi)
        self.compatibility_manager = ABICompatibilityManager()
        self.kernel_engine: Optional[KernelEngine] = None
        self._runtime_context: Optional[KernelRuntimeContext] = None

    def initialize_subsystem(self) -> None:
        """
        Executes the complete boot sequence: registry loading, legacy engine adaptation,
        ABI validation, ABI locking, and Kernel Engine binding with error-safe exception boundaries.
        """
        logger.info("Initiating Wilsy OS Kernel Bootstrap & ABI boot sequence [v%s]...", self.VERSION)

        try:
            # 1. Load Kernel Registry
            registry = KernelRegistry()

            # Safely extract and cast registered engines to satisfy strict typing
            registered_engines: List[Any] = []
            get_all_fn = getattr(registry, "get_all_engines", None)
            if callable(get_all_fn):
                raw_res = get_all_fn()
                if isinstance(raw_res, Iterable):
                    registered_engines = list(cast(Iterable[Any], raw_res))
            else:
                engines_attr = getattr(registry, "engines", None)
                if isinstance(engines_attr, dict):
                    registered_engines = list(engines_attr.values())
                elif isinstance(engines_attr, Iterable):
                    registered_engines = list(cast(Iterable[Any], engines_attr))
                else:
                    list_fn = getattr(registry, "list_engines", None)
                    if callable(list_fn):
                        raw_list = list_fn()
                        if isinstance(raw_list, Iterable):
                            registered_engines = list(cast(Iterable[Any], raw_list))

            # 2. Adapt legacy engines if enabled
            processed_engines: List[Any] = []
            for engine in registered_engines:
                if self.auto_adapt_legacy and not isinstance(engine, BaseKernelEngineProtocol):
                    logger.warning("Adapting non-compliant legacy engine '%s' via Compatibility Manager.", engine)
                    adapted_engine = self.compatibility_manager.adapt_engine(engine)
                    processed_engines.append(adapted_engine)
                else:
                    processed_engines.append(engine)

            # 3. Enforce Kernel ABI Startup Validation
            validation_report: ABIValidationReport
            if processed_engines:
                validation_report = self.validator.validate_system_registry(processed_engines)
            else:
                logger.info("Kernel Registry empty during bootstrap. Framework ABI locked.")
                validation_report = ABIValidationReport(total_engines_scanned=0, passed_engines=0, failed_engines=0)

            # 4. Ensure Kernel ABI is locked
            if not KernelABI.is_locked():
                KernelABI.lock_abi()

            version_spec: KernelVersionSpec = KernelABI.get_version_spec()
            logger.info(
                "Kernel ABI verification successful. Version: %s | ABI: %s | Active Engines: %d",
                self.VERSION,
                version_spec.abi,
                len(processed_engines),
            )

            # 5. Construct Immutable Runtime Context
            self._runtime_context = KernelRuntimeContext(
                registry=registry,
                version=self.VERSION,
                startup_mode=self.STARTUP_MODE,
                abi_validation_report=validation_report,
                version_spec=version_spec,
            )

            # 6. Instantiate Master Kernel Engine
            self.kernel_engine = KernelEngine(
                consensus_threshold=self.consensus_threshold,
                strict_mode=self.strict_mode
            )
            self.kernel_engine.activate()

            logger.info("Wilsy OS Kernel Bootstrap successfully completed and locked.")

        except Exception as e:
            logger.critical(f"Critical failure during Kernel Bootstrap initialization: {str(e)}", exc_info=True)
            raise RuntimeError(f"Kernel Bootstrap failed: {str(e)}") from e

    def boot(self) -> KernelRuntimeContext:
        """
        Public execution handle for the sovereign boot sequence.
        Returns the immutable KernelRuntimeContext.
        """
        if not self.is_active:
            self.activate()

        if not self._runtime_context:
            raise RuntimeError("Kernel runtime context was not initialized during activation.")
        return self._runtime_context

    def get_engine(self) -> KernelEngine:
        """Returns the active, activated KernelEngine instance."""
        if not self.is_active or not self.kernel_engine:
            raise RuntimeError("KernelBootstrap is not active. Call activate() before accessing engine.")
        return self.kernel_engine


# ═══════════════════════════════════════════════════════════════════════════════
# CERTIFICATION SEAL & HEALTH CHECK
# ═══════════════════════════════════════════════════════════════════════════════

def wilsy_os_kernel_bootstrap_seal() -> bool:
    """
    Sovereign Health Check: Instantiates bootloader, validates ABI compliance,
    locks the system, and verifies successful initialization. Must return True.
    """
    try:
        bootloader = KernelBootstrap(enforce_strict_abi=True, auto_adapt_legacy=True)
        runtime_ctx = bootloader.boot()
        engine = bootloader.get_engine()

        return runtime_ctx is not None and engine.is_active
    except Exception as e:
        logger.error(f"Kernel Bootstrap Seal Broken: {str(e)}")
        return False


# Execute seal on load
if not wilsy_os_kernel_bootstrap_seal():
    raise SystemError("CRITICAL: tools.eos.kernel.bootstrap failed Sovereign Certification Seal. Halt execution.")

__all__ = [
    "KernelBootstrap",
    "wilsy_os_kernel_bootstrap_seal",
]
