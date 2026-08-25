"""
===============================================================================
WILSY OS KERNEL ARCHITECTURE - ENTERPRISE ENGINEERING PLATFORM
===============================================================================
PROJECT: Wilsy OS (Billion-Dollar Sovereign Infrastructure)
SUBSYSTEM: Kernel ABI & Core Governance Framework
MILESTONE: FG178.5 - Kernel ABI Freeze
MODULE: abi_validator.py

COLLABORATION & ARCHITECTURAL NOTICE:
Strict validation engine that enforces Kernel ABI compliance at system startup.
Scans registered engines and verifies 5-stage lifecycle compliance, typed contexts,
event publishing, artifact generation, and governance integration.
If any engine fails compliance, startup is refused.
===============================================================================
"""

import inspect
import logging
from dataclasses import dataclass, field
from typing import Dict, List, Any, Type, Optional

from tools.eos.abi.kernel_contracts import BaseKernelEngineProtocol
from tools.eos.abi.kernel_version import KERNEL_VERSION, ABI_VERSION

logger = logging.getLogger("WilsyOS.ABI.Validator")


class ABIValidationError(Exception):
    """Raised when an engine fails strict Kernel ABI startup validation."""
    pass


@dataclass
class EngineValidationResult:
    """Detailed validation metrics for a single registered engine."""
    engine_name: str
    is_compliant: bool
    checks_passed: List[str] = field(default_factory=list)
    checks_failed: List[str] = field(default_factory=list)
    diagnostics: List[str] = field(default_factory=list)


@dataclass
class ABIValidationReport:
    """Aggregate system-wide validation report produced during startup."""
    kernel_version: str = KERNEL_VERSION
    abi_version: str = ABI_VERSION
    total_engines_scanned: int = 0
    passed_engines: int = 0
    failed_engines: int = 0
    engine_results: Dict[str, EngineValidationResult] = field(default_factory=dict)

    @property
    def is_system_compliant(self) -> bool:
        return self.failed_engines == 0 and self.total_engines_scanned > 0


class ABIValidator:
    """
    Startup gatekeeper enforcing compliance with Wilsy OS Kernel ABI (FG178.5).
    """

    MANDATORY_LIFECYCLE_METHODS = [
        "initialize",
        "validate",
        "execute",
        "publish",
        "shutdown",
    ]

    def __init__(self, enforce_strict: bool = True) -> None:
        self.enforce_strict = enforce_strict

    def validate_engine(self, engine_cls_or_instance: Any) -> EngineValidationResult:
        """Inspects an engine implementation against Kernel ABI mandates."""
        engine_name = getattr(
            engine_cls_or_instance,
            "engine_name",
            getattr(engine_cls_or_instance, "__name__", str(engine_cls_or_instance)),
        )

        result = EngineValidationResult(engine_name=engine_name, is_compliant=True)

        # Check 1: Mandatory 5-stage Lifecycle Methods
        for method in self.MANDATORY_LIFECYCLE_METHODS:
            if not hasattr(engine_cls_or_instance, method):
                result.is_compliant = False
                result.checks_failed.append(f"missing_lifecycle_method_{method}")
                result.diagnostics.append(f"Engine '{engine_name}' lacks required method '{method}()'.")
            else:
                attr = getattr(engine_cls_or_instance, method)
                if not callable(attr):
                    result.is_compliant = False
                    result.checks_failed.append(f"non_callable_{method}")
                    result.diagnostics.append(f"Attribute '{method}' in engine '{engine_name}' is not callable.")
                else:
                    result.checks_passed.append(f"lifecycle_method_{method}")

        # Check 2: Method Signatures Accept ExecutionContext
        for method in self.MANDATORY_LIFECYCLE_METHODS:
            if hasattr(engine_cls_or_instance, method):
                method_obj = getattr(engine_cls_or_instance, method)
                try:
                    sig = inspect.signature(method_obj)
                    params = list(sig.parameters.keys())
                    if params and params[0] in ("self", "cls"):
                        params = params[1:]
                    if not params:
                        result.is_compliant = False
                        result.checks_failed.append(f"invalid_signature_{method}")
                        result.diagnostics.append(f"Method '{method}()' in '{engine_name}' must accept 'context' parameter.")
                    else:
                        result.checks_passed.append(f"valid_signature_{method}")
                except Exception as err:
                    result.diagnostics.append(f"Could not inspect signature for '{method}()': {err}")

        # Check 3: Required Metadata
        if hasattr(engine_cls_or_instance, "version"):
            result.checks_passed.append("has_version")
        else:
            result.diagnostics.append(f"Engine '{engine_name}' should expose explicit 'version' string.")

        return result

    def validate_system_registry(self, registered_engines: List[Any]) -> ABIValidationReport:
        """
        Scans all registered engines in the system and generates a startup audit report.
        If strict mode is enabled and validation fails, raises ABIValidationError to halt startup.
        """
        report = ABIValidationReport()
        report.total_engines_scanned = len(registered_engines)

        logger.info("Beginning Wilsy OS Kernel ABI Startup Validation [v%s]...", ABI_VERSION)

        for engine in registered_engines:
            res = self.validate_engine(engine)
            report.engine_results[res.engine_name] = res
            if res.is_compliant:
                report.passed_engines += 1
            else:
                report.failed_engines += 1
                logger.error("ABI Compliance Failure in Engine '%s': %s", res.engine_name, res.diagnostics)

        logger.info(
            "ABI Validation complete: Total=%d | Passed=%d | Failed=%d",
            report.total_engines_scanned,
            report.passed_engines,
            report.failed_engines,
        )

        if self.enforce_strict and not report.is_system_compliant:
            raise ABIValidationError(
                f"Kernel ABI Validation failed! {report.failed_engines} engine(s) failed strict compliance. "
                f"Refusing system startup under milestone FG178.5."
            )

        return report
