from __future__ import annotations

"""
===============================================================================
WILSY OS KERNEL — GOVERNANCE ENGINE BASIC USAGE EXAMPLE (FG177)
===============================================================================
"""

import sys
from pathlib import Path

# Ensure root directory is in sys.path
root_dir = Path(__file__).resolve().parents[4]
if str(root_dir) not in sys.path:
    sys.path.insert(0, str(root_dir))

from tools.eos.governance import (
    EnforcementMode,
    GovernanceAuditPublisher,
    GovernanceEngine,
    GovernancePolicy,
    GovernanceRegistry,
    GovernanceRule,
    PolicySeverity,
)


class MockExecutionContext:
    """Mock ExecutionContext adhering to FG145 context models."""
    def __init__(self, execution_id: str, user_id: str, cpu_allocation: int, roles: list[str]) -> None:
        self.execution_id = execution_id
        self.parameters = {
            "user_id": user_id,
            "requested_cpu": cpu_allocation,
            "roles": roles,
        }


def main():
    # 1. Initialize Components
    registry = GovernanceRegistry()
    publisher = GovernanceAuditPublisher()
    
    # Event Bus Listener
    events = []
    def mock_event_bus(event_type: str, payload: dict):
        events.append((event_type, payload))

    engine = GovernanceEngine(registry=registry, event_bus_publisher=mock_event_bus)

    # 2. Register Engine in Registry
    registry.register_engine(engine_id="governance", engine_instance=engine)

    # 3. Create & Register Policy
    rule = GovernanceRule(
        rule_id="RULE-CPU-CAP",
        rule_type="RESOURCE_LIMIT",
        params={"param": "requested_cpu", "max": 8},
        description="CPU core allocation must not exceed 8.",
    )
    policy = GovernancePolicy(
        policy_id="POL-RESOURCE-GUARD",
        name="Resource Allocation Policy",
        description="Prevents compute overload",
        version="1.0.0",
        severity=PolicySeverity.HIGH,
        enforcement_mode=EnforcementMode.STRICT,
        rules=[rule],
    )
    registry.register_policy(policy)

    # 4. Evaluate Valid ExecutionContext
    ctx = MockExecutionContext("EXEC-2026-001", "USR-WILSON", 4, ["admin"])
    decision = engine.evaluate(ctx)

    # 5. Publish Audit Artifact to Artifact Bus
    artifact = publisher.publish_decision(decision)

    print(f"Execution Status : {decision.status.value}")
    print(f"Artifact Schema  : {artifact['artifact_schema']}")
    print(f"Events Emitted   : {[e[0] for e in events]}")


if __name__ == "__main__":
    main()
