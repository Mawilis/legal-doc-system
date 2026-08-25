from __future__ import annotations

"""
===============================================================================
WILSY OS KERNEL — GOVERNANCE ENGINE: INTEGRATION VERIFICATION (FG177)
===============================================================================
"""

import sys
from pathlib import Path

# Ensure root directory is in sys.path
root_dir = Path(__file__).resolve().parents[3]
if str(root_dir) not in sys.path:
    sys.path.insert(0, str(root_dir))

from tools.eos.governance import (
    EnforcementMode,
    GovernanceAuditPublisher,
    GovernanceEngine,
    GovernancePolicy,
    GovernanceRegistry,
    GovernanceReportGenerator,
    GovernanceRule,
    GovernanceStatus,
    PolicySeverity,
)


class MockExecutionContext:
    def __init__(self, execution_id: str, user_id: str, cpu_allocation: int, roles: list[str]) -> None:
        self.execution_id = execution_id
        self.parameters = {
            "user_id": user_id,
            "requested_cpu": cpu_allocation,
            "roles": roles,
        }


def run_verification() -> bool:
    print("=====================================================================")
    print(" WILSY OS KERNEL — FG177 GOVERNANCE ENGINE VERIFICATION SUITE")
    print("=====================================================================")

    # 1. Initialize Components
    registry = GovernanceRegistry()
    audit_publisher = GovernanceAuditPublisher()
    
    events_published = []
    def mock_event_publisher(event_type: str, payload: dict):
        events_published.append((event_type, payload))

    engine = GovernanceEngine(registry=registry, event_bus_publisher=mock_event_publisher)

    # Engine Self-Registration
    registry.register_engine("governance", engine)

    print("\n[+] 1. Registering Institutional Policies & Engine...")

    strict_policy = GovernancePolicy(
        policy_id="POL-STRICT-COMPLIANCE",
        name="Strict Kernel Access Policy",
        description="Enforces mandatory CPU threshold ceilings.",
        version="1.0.0",
        severity=PolicySeverity.CRITICAL,
        enforcement_mode=EnforcementMode.STRICT,
        rules=[
            GovernanceRule("RULE-LIMIT-CPU", "RESOURCE_LIMIT", {"param": "requested_cpu", "max": 8}),
        ],
    )

    audit_policy = GovernancePolicy(
        policy_id="POL-AUDIT-ROLES",
        name="Audit Access Control Policy",
        description="Audits context against institutional roles.",
        version="1.0.0",
        severity=PolicySeverity.HIGH,
        enforcement_mode=EnforcementMode.AUDIT,
        rules=[
            GovernanceRule("RULE-ALLOW-ROLES", "ALLOWED_ROLES", {"roles": ["admin", "kernel_worker"]}),
        ],
    )

    registry.register_policy(strict_policy)
    registry.register_policy(audit_policy)
    print(f"    Registered {registry.count()} policies and 'governance' engine in Registry.")

    # 2. Test Context: Valid (Pass)
    print("\n[+] 2. Evaluating Valid ExecutionContext (APPROVED)...")
    ctx_pass = MockExecutionContext("EXEC-001", "USR-WILSON-001", 4, ["admin"])
    decision_pass = engine.evaluate(ctx_pass)
    audit_publisher.publish_decision(decision_pass)

    assert decision_pass.status == GovernanceStatus.APPROVED, "Expected APPROVED status"
    print(f"    Status: {decision_pass.status.value}")
    print(f"    Checksum: {decision_pass.compute_checksum()[:16]}...")

    # 3. Test Context: STRICT Failure (Blocked)
    print("\n[+] 3. Evaluating CPU Limit Violation Context (BLOCKED)...")
    ctx_block = MockExecutionContext("EXEC-002", "USR-WILSON-001", 16, ["admin"])
    decision_block = engine.evaluate(ctx_block)
    audit_publisher.publish_decision(decision_block)

    assert decision_block.status == GovernanceStatus.BLOCKED, "Expected BLOCKED status"
    print(f"    Status: {decision_block.status.value}")

    # 4. Test Context: AUDIT Trigger (Requires Review)
    print("\n[+] 4. Evaluating Unauthorized Role Context (REQUIRES_REVIEW)...")
    ctx_audit = MockExecutionContext("EXEC-003", "USR-GUEST-999", 2, ["guest"])
    decision_audit = engine.evaluate(ctx_audit)
    audit_publisher.publish_decision(decision_audit)

    assert decision_audit.status == GovernanceStatus.REQUIRES_REVIEW, "Expected REQUIRES_REVIEW status"
    print(f"    Status: {decision_audit.status.value}")

    # 5. Verify Event Bus & Artifact Bus
    print("\n[+] 5. Verifying Event Bus & Artifact Bus Publication...")
    print(f"    Events Published    : {len(events_published)}")
    print(f"    Artifacts Published : {len(audit_publisher.published_history)}")
    assert len(events_published) > 0, "Event Bus should have received events."
    assert len(audit_publisher.published_history) == 3, "Artifact Bus should have 3 governance audit artifacts."

    # 6. Summary Report
    report = GovernanceReportGenerator.generate_summary([decision_pass, decision_block, decision_audit])
    print(f"\n[+] 6. Compliance Summary Report: {report}")

    print("\n=====================================================================")
    print(" [SUCCESS] ALL FG177 GOVERNANCE ENGINE CHECKS PASSED PERFECTLY")
    print("=====================================================================")
    return True


if __name__ == "__main__":
    success = run_verification()
    sys.exit(0 if success else 1)
