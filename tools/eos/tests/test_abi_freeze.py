"""
===============================================================================
WILSY OS KERNEL ARCHITECTURE - ENTERPRISE ENGINEERING PLATFORM
===============================================================================
PROJECT: Wilsy OS (Billion-Dollar Sovereign Infrastructure)
SUBSYSTEM: Kernel ABI Verification Suite
MILESTONE: FG178.5 - Kernel ABI Freeze
MODULE: test_abi_freeze.py

COLLABORATION & ARCHITECTURAL NOTICE:
Validates complete ABI compliance, lifecycle enforcement, compatibility adapter
wrapping, and symbol registry isolation under FG178.5 mandates.
===============================================================================
"""

import unittest
import logging
from typing import Dict, Any

from tools.eos.abi import (
    KernelABI,
    KernelVersionSpec,
    ABIValidator,
    ABIValidationError,
    BaseKernelEngine,
    BaseKernelEngineProtocol,
    ExecutionContextProtocol,
    EngineResultProtocol,
    EngineExecutionStatus,
    LifecyclePhase,
    EngineCapability,
    ABICompatibilityManager,
    EngineCompatibilityAdapter,
    ABIMigrationEngine,
)

logging.basicConfig(level=logging.INFO)


class DummyContext:
    """Mock ExecutionContext adhering to ExecutionContextProtocol."""
    execution_id = "exec_test_001"
    session_id = "sess_test_999"
    tenant_id = "tenant_alpha"
    metadata = {"environment": "test"}

    def get_parameter(self, key: str, default: Any = None) -> Any:
        return self.metadata.get(key, default)


class DummyResult:
    """Mock EngineResult adhering to EngineResultProtocol."""
    engine_name = "DummyCompliantEngine"
    status = EngineExecutionStatus.SUCCESS
    execution_id = "exec_test_001"
    outputs = {"result": "ok"}
    artifacts_created = []
    events_emitted = []
    execution_time_ms = 12.5
    error_message = None


class DummyCompliantEngine(BaseKernelEngine):
    """Standard engine fully conforming to FG178.5 Kernel ABI."""

    def __init__(self):
        super().__init__(engine_name="DummyCompliantEngine", version="1.0.0")

    def initialize(self, context: ExecutionContextProtocol) -> None:
        super().initialize(context)

    def validate(self, context: ExecutionContextProtocol) -> None:
        super().validate(context)

    def execute(self, context: ExecutionContextProtocol) -> EngineResultProtocol:
        super().execute(context)
        return DummyResult()

    def publish(self, context: ExecutionContextProtocol) -> None:
        super().publish(context)

    def shutdown(self, context: ExecutionContextProtocol) -> None:
        super().shutdown(context)


class LegacyNonCompliantEngine:
    """Pre-FG178.5 legacy engine lacking 5-stage lifecycle methods."""

    def __init__(self):
        self.engine_name = "LegacyNonCompliantEngine"
        self.version = "0.8.0"

    def run(self, context):
        return {"status": "SUCCESS", "data": "legacy_output"}


class TestKernelABIFreeze(unittest.TestCase):

    def test_01_kernel_abi_registry_and_symbols(self):
        """Verify frozen symbols are locked and immutable."""
        self.assertTrue(KernelABI.is_locked())
        symbols = KernelABI.get_registered_symbols()
        self.assertIn("BaseKernelEngineProtocol", symbols)
        self.assertIn("ExecutionContextProtocol", symbols)
        self.assertIn("EngineResultProtocol", symbols)

        with self.assertRaises(RuntimeError):
            KernelABI.register_symbol("IllegalSymbol", str, "Should fail")

    def test_02_abi_version_spec(self):
        """Verify version spec manifest export."""
        spec = KernelABI.get_version_spec()
        manifest = spec.export_manifest()
        self.assertEqual(manifest["abi_version"], "1.0")
        self.assertEqual(manifest["frozen_at_milestone"], "FG178.5")

    def test_03_compliant_engine_validation(self):
        """Verify a fully compliant engine passes ABI validation."""
        validator = ABIValidator(enforce_strict=True)
        engine = DummyCompliantEngine()
        result = validator.validate_engine(engine)
        self.assertTrue(result.is_compliant)
        self.assertEqual(len(result.checks_failed), 0)

    def test_04_non_compliant_engine_rejection(self):
        """Verify non-compliant engine triggers validation failure."""
        validator = ABIValidator(enforce_strict=False)
        legacy_engine = LegacyNonCompliantEngine()
        result = validator.validate_engine(legacy_engine)
        self.assertFalse(result.is_compliant)
        self.assertGreater(len(result.checks_failed), 0)

    def test_05_compatibility_adapter_wrapping(self):
        """Verify compatibility adapter elevates legacy engine to full Kernel ABI compliance."""
        adapter = EngineCompatibilityAdapter(LegacyNonCompliantEngine())
        validator = ABIValidator(enforce_strict=True)
        
        # Adapter must pass ABI validation
        result = validator.validate_engine(adapter)
        self.assertTrue(result.is_compliant)

        # Test execution lifecycle on adapted engine
        context = DummyContext()
        adapter.initialize(context)
        self.assertEqual(adapter.lifecycle_phase, LifecyclePhase.INITIALIZED)
        adapter.validate(context)
        self.assertEqual(adapter.lifecycle_phase, LifecyclePhase.VALIDATED)
        res = adapter.execute(context)
        self.assertEqual(adapter.lifecycle_phase, LifecyclePhase.EXECUTED)
        self.assertEqual(res.status, EngineExecutionStatus.SUCCESS)
        adapter.publish(context)
        adapter.shutdown(context)
        self.assertEqual(adapter.lifecycle_phase, LifecyclePhase.SHUTDOWN)

    def test_06_strict_system_registry_validation(self):
        """Verify strict registry validation raises exception on non-compliant engine."""
        validator = ABIValidator(enforce_strict=True)
        adapter = EngineCompatibilityAdapter(LegacyNonCompliantEngine())
        compliant_engine = DummyCompliantEngine()

        report = validator.validate_system_registry([compliant_engine, adapter])
        self.assertTrue(report.is_system_compliant)
        self.assertEqual(report.passed_engines, 2)

        with self.assertRaises(ABIValidationError):
            validator.validate_system_registry([LegacyNonCompliantEngine()])


if __name__ == "__main__":
    unittest.main()
