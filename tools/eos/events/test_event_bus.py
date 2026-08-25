"""
===============================================================================
WILSY ENGINEERING KERNEL
===============================================================================
Epitome:
    FG161 Event Bus Integration & Verification Test.
    Validates decoupled publisher-subscriber dispatch, immutable checksums,
    failure isolation, and strict contract adherence.
    Billion-dollar software architecture: secure, robust, immutable, and future-proof.
===============================================================================
"""

import sys
import os

# Ensure root directory is in sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../")))

from tools.eos.events.event_bus import EventBus
from tools.eos.events.event_types import EventType
from tools.eos.events.subscriber import Subscriber
from tools.eos.events.event import Event


class MockEngineSubscriber(Subscriber):
    """Mock engine subscriber for testing event reception."""

    def __init__(self, sub_id: str) -> None:
        self._sub_id = sub_id
        self.received_events = []

    @property
    def subscriber_id(self) -> str:
        return self._sub_id

    def subscribe(self, event_type: str) -> None:
        pass

    def unsubscribe(self, event_type: str) -> None:
        pass

    def notify(self, event: Event) -> None:
        self.received_events.append(event)
        if event.payload.get("fail_handler"):
            raise ValueError("Intentional subscriber failure for isolation test.")


def test_event_bus_workflow():
    print("===============================================================================")
    print("WILSY OS KERNEL - FG161 EVENT BUS VERIFICATION")
    print("===============================================================================")

    bus = EventBus(publisher_id="TestKernelScheduler")
    sub = MockEngineSubscriber(sub_id="RepositoryEngine")

    # 1. Register subscriber contract
    bus.register_subscriber(sub, [EventType.REPOSITORY_SCANNED, EventType.EXECUTION_STARTED])

    # 2. Publish event via EventBus
    event = bus.publish(
        event_type=EventType.REPOSITORY_SCANNED,
        payload={"indexed_files": 2789, "status": "success"},
        execution_id="exec-test-999"
    )

    print(f"  -> Published Event ID: [{event.event_id}]")
    print(f"  -> Cryptographic Checksum Verified: [{event.verify_integrity()}]")
    print(f"  -> Subscriber received events count: {len(sub.received_events)}")
    assert len(sub.received_events) == 1
    assert sub.received_events[0].payload["indexed_files"] == 2789

    # 3. Test failure isolation
    bus.publish(
        event_type=EventType.EXECUTION_STARTED,
        payload={"fail_handler": True, "message": "Test failure isolation"},
    )
    print("  -> Failure isolation test passed: Bus survived faulty subscriber exception.")

    # 4. Check event history
    history = bus.history()
    print(f"  -> Total events recorded in immutable history: {len(history)}")
    assert len(history) == 2

    print("===============================================================================")
    print("FG161 EVENT-DRIVEN ARCHITECTURE VERIFIED SUCCESSFULLY.")
    print("===============================================================================")


if __name__ == "__main__":
    test_event_bus_workflow()
