"""
===============================================================================
WILSY ENGINEERING KERNEL
===============================================================================
Epitome:
    FG162 Engine Lifecycle & Host Integration Test.
    Validates institutional engine factory creation, lifecycle state transitions,
    bootstrap sequence, supervision, and graceful shutdown.
    Billion-dollar software architecture: secure, robust, immutable, and future-proof.
===============================================================================
"""

import sys
import os

# Ensure root directory is in sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../")))

from tools.eos.events.event_bus import EventBus
from tools.eos.runtime.engine_host import EngineHost
from tools.eos.runtime.lifecycle_manager import EngineState


class MockManagedEngine:
    """Mock engine adhering to the ManagedEngine protocol for testing."""

    def __init__(self, event_bus: EventBus, engine_id: str = "mock-engine-001") -> None:
        self._engine_id = engine_id
        self.event_bus = event_bus
        self.initialized = False
        self.running = False

    @property
    def engine_id(self) -> str:
        return self._engine_id

    def initialize(self) -> None:
        self.initialized = True

    def start(self) -> None:
        self.running = True

    def stop(self) -> None:
        self.running = False

    def health_check(self) -> bool:
        return self.initialized and self.running


def test_lifecycle_workflow():
    print("===============================================================================")
    print("WILSY OS KERNEL - FG162 ENGINE LIFECYCLE HOST VERIFICATION")
    print("===============================================================================")

    host = EngineHost()

    # 1. Register engine class with factory
    host.factory.register_engine_class("MockEngine", MockManagedEngine)

    # 2. Register engine instance via host
    engine = host.register("MockEngine", engine_id="RepositoryServiceEngine")
    print(f"  -> Registered engine ID: [{engine.engine_id}]")

    # Verify initial state is UNINITIALIZED
    initial_state = host.lifecycle_manager.get_engine_state(engine.engine_id)
    print(f"  -> Initial state: [{initial_state}]")
    assert initial_state == EngineState.UNINITIALIZED

    # 3. Run master bootstrap sequence
    host.bootstrap()

    running_state = host.lifecycle_manager.get_engine_state(engine.engine_id)
    print(f"  -> Post-bootstrap state: [{running_state}]")
    assert running_state == EngineState.RUNNING

    # 4. Supervise health check
    is_healthy = host.supervise()
    print(f"  -> Health supervision status: [{is_healthy}]")
    assert is_healthy is True

    # 5. Graceful shutdown
    host.shutdown()
    stopped_state = host.lifecycle_manager.get_engine_state(engine.engine_id)
    print(f"  -> Post-shutdown state: [{stopped_state}]")
    assert stopped_state == EngineState.STOPPED

    print("===============================================================================")
    print("FG162 ENGINE LIFECYCLE MANAGER VERIFIED SUCCESSFULLY.")
    print("===============================================================================")


if __name__ == "__main__":
    test_lifecycle_workflow()
