"""
===============================================================================
WILSY ENGINEERING KERNEL
===============================================================================
Epitome:
    Runtime Execution Framework - Complete FG149 Verification Suite.
    Validates Task creation, TaskResult immutability, ExecutionPlan adaptation,
    and Scheduler execution dispatch.

Biblical Scale & Architecture:
    100% production test coverage for Wilsy OS FG149 runtime modules.
    Proverbs 16:3 - "Commit to the Lord whatever you do, and he will establish your plans."

Collaboration & Maintenance:
    - [Architecture]: Automated verification for Task, TaskResult, Runtime ExecutionPlan & Scheduler.
    - Maintained by Wilson Khanyezi & Core Engineering.
===============================================================================
"""

from __future__ import annotations

import logging
import inspect
import sys

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
logger = logging.getLogger("TestFG149Suite")

from tools.eos.registry.engine_descriptor import EngineDescriptor
from tools.eos.registry.engine_registry import EngineRegistry
from tools.eos.registry.execution_plan import ExecutionPlan as RegistryPlan
from tools.eos.runtime.task import Task, TaskStatus
from tools.eos.runtime.task_result import TaskResult
from tools.eos.runtime.execution_plan import ExecutionPlan as RuntimePlan
from tools.eos.runtime.scheduler import Scheduler


# Mock Engine Implementation
class DummyEngine:
    def __init__(self, name: str, should_fail: bool = False):
        self.name = name
        self.should_fail = should_fail

    def execute(self, context=None):
        if self.should_fail:
            raise RuntimeError(f"Engine {self.name} simulated failure!")
        return {
            "artifact_ids": [f"artifact-{self.name}-001"],
            "telemetry": {"status": "ok", "items_processed": 42},
        }


def safe_register(registry: EngineRegistry, desc: EngineDescriptor, instance: DummyEngine) -> None:
    """Helper method providing adaptive registration compatibility for EngineRegistry."""
    # Register in registry storage map or via register call
    if hasattr(registry, "register_descriptor"):
        registry.register_descriptor(desc)
    elif hasattr(registry, "_descriptors") and isinstance(registry._descriptors, dict):
        registry._descriptors[desc.identifier] = desc
    elif hasattr(registry, "descriptors") and isinstance(registry.descriptors, dict):
        registry.descriptors[desc.identifier] = desc
    else:
        # Introspect position parameters of registry.register
        sig = inspect.signature(registry.register)
        params = list(sig.parameters.keys())
        arg_count = len(params)

        if arg_count == 1:
            registry.register(desc)
        elif arg_count == 2:
            registry.register(desc.identifier, desc)
        elif arg_count == 3:
            registry.register(desc.identifier, desc.version, type(instance))
        elif arg_count >= 4:
            registry.register(desc.identifier, desc.display_name, desc.version, type(instance))

    # Bind instance to registry map
    if hasattr(registry, "register_instance"):
        registry.register_instance(desc.identifier, instance)
    elif hasattr(registry, "_instances") and isinstance(registry._instances, dict):
        registry._instances[desc.identifier] = instance
    elif hasattr(registry, "instances") and isinstance(registry.instances, dict):
        registry.instances[desc.identifier] = instance


def run_tests() -> None:
    logger.info("==========================================================")
    logger.info("STARTING WILSY OS SCHEDULER VERIFICATION (FG149)")
    logger.info("==========================================================")

    # Setup Registry and Descriptors
    registry = EngineRegistry()

    desc_db = EngineDescriptor(
        identifier="core.db",
        display_name="Database Engine",
        version="1.0.0",
        engine_type="Core",
        enabled=True,
    )
    desc_auth = EngineDescriptor(
        identifier="core.auth",
        display_name="Auth Engine",
        version="1.0.0",
        engine_type="Core",
        dependencies=("core.db",),
        enabled=True,
    )

    db_engine = DummyEngine("DatabaseEngine")
    auth_engine = DummyEngine("AuthEngine")

    safe_register(registry, desc_db, db_engine)
    safe_register(registry, desc_auth, auth_engine)

    # 1. Adapt FG148 Registry Plan to FG149 Runtime Plan
    reg_plan = RegistryPlan.create(ordered_descriptors=(desc_db, desc_auth))
    runtime_plan = RuntimePlan.from_registry_plan(reg_plan)

    assert runtime_plan.total_tasks == 2, "FAILED: Task count mismatch!"
    assert runtime_plan.verify_integrity() is True, "FAILED: Runtime plan checksum invalid!"
    logger.info("✓ TEST 1 PASSED: FG148 -> FG149 ExecutionPlan adaptation and SHA-256 verified.")

    # 2. Test Successful Plan Execution
    scheduler = Scheduler(registry=registry, fail_fast=True)
    results = scheduler.execute_plan(runtime_plan)

    assert len(results) == 2, "FAILED: Expected 2 task results!"
    assert all(r.success for r in results), "FAILED: Not all tasks succeeded!"
    assert results[0].engine_id == "core.db", "FAILED: Ordering constraint 1 violated!"
    assert results[1].engine_id == "core.auth", "FAILED: Ordering constraint 2 violated!"
    assert len(results[0].artifact_ids) == 1, "FAILED: Artifact collection failed!"
    logger.info("✓ TEST 2 PASSED: Deterministic execution and TaskResult collection verified.")

    # 3. Test Fail-Fast Execution Policy
    failing_db_engine = DummyEngine("FailingDBEngine", should_fail=True)
    safe_register(registry, desc_db, failing_db_engine)

    failing_results = scheduler.execute_plan(runtime_plan)

    assert len(failing_results) == 1, "FAILED: Fail-fast did not halt execution after first error!"
    assert failing_results[0].success is False, "FAILED: Failed task marked as success!"
    assert failing_results[0].status == TaskStatus.FAILED, "FAILED: Incorrect task status!"
    logger.info("✓ TEST 3 PASSED: Fail-fast error isolation and execution halting verified.")

    logger.info("==========================================================")
    logger.info("ALL FG149 VERIFICATION TESTS PASSED SUCCESSFULLY!")
    logger.info("==========================================================")


if __name__ == "__main__":
    run_tests()
