"""
===============================================================================
WILSY ENGINEERING KERNEL
===============================================================================
Epitome:
    FG165 Policy Engine Integration & Compliance Test.
    Validates rule registry, file evaluations, size/complexity/naming rules,
    and institutional policy validation reports.
    Billion-dollar software architecture: secure, robust, immutable, and future-proof.
===============================================================================
"""

import sys
import os

# Ensure root directory is in sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../")))

from tools.eos.policy.policy_models import PolicyRule
from tools.eos.policy.policy_registry import PolicyRegistry
from tools.eos.policy.policy_engine import PolicyEngine


def test_policy_engine():
    print("===============================================================================")
    print("WILSY OS KERNEL - FG165 POLICY ENGINE & GOVERNANCE VERIFICATION")
    print("===============================================================================")

    registry = PolicyRegistry()

    # 1. Register institutional policy rules
    rule_size = PolicyRule(
        rule_id="RULE-SIZE-01",
        name="Maximum File Size",
        category="size",
        severity="ERROR",
        description="Ensure files do not exceed maximum byte size or line count.",
        parameters={"max_bytes": 50000, "max_lines": 500}
    )
    rule_naming = PolicyRule(
        rule_id="RULE-NAME-01",
        name="Standard Naming Convention",
        category="naming",
        severity="WARNING",
        description="Ensure Python source files adhere to snake_case naming standards.",
        parameters={"pattern": r"^[a-z_][a-z0-9_]*\.py$"}
    )
    rule_release = PolicyRule(
        rule_id="RULE-REL-01",
        name="Release Epitome Requirement",
        category="release",
        severity="ERROR",
        description="Ensure files contain institutional collaboration and epitome comments.",
        parameters={"required_markers": ["Epitome:", "Billion-dollar software architecture"]}
    )

    registry.register(rule_size)
    registry.register(rule_naming)
    registry.register(rule_release)
    print("  -> Successfully registered institutional policy rules.")

    # 2. Test PolicyEngine file evaluation
    engine = PolicyEngine(registry=registry)

    compliant_content = '''"""
===============================================================================
WILSY ENGINEERING KERNEL
===============================================================================
Epitome:
    Valid compliance file. Billion-dollar software architecture: secure and robust.
===============================================================================
"""
def secure_function():
    return True
'''

    # Evaluate a compliant file
    result_pass = engine.evaluate_file("tools/eos/policy/sample_valid.py", compliant_content, {"complexity": 5})
    print(f"  -> Compliant file evaluation passed? {result_pass.passed} (Expected: True)")
    assert result_pass.passed is True
    assert len(result_pass.violations) == 0

    # Evaluate a non-compliant file (missing release markers, failing naming, high size)
    violating_content = "print('hello world')"
    result_fail = engine.evaluate_file("tools/eos/policy/BAD_NAME.py", violating_content, {"complexity": 25})
    print(f"  -> Non-compliant file evaluation passed? {result_fail.passed} (Expected: False)")
    print(f"     Violations count: {len(result_fail.violations)}")
    print(f"     Warnings count: {len(result_fail.warnings)}")
    
    assert result_fail.passed is False
    assert len(result_fail.violations) > 0

    # 3. Test workspace-level policy evaluation
    workspace_eval = engine.evaluate_policies("default_governance")
    print(f"  -> Workspace evaluation status: {workspace_eval['status']}")
    print(f"     Files checked: {workspace_eval['validation_details']['files_checked']}")

    print("===============================================================================")
    print("FG165 POLICY ENGINE & GOVERNANCE VERIFIED SUCCESSFULLY.")
    print("===============================================================================")


if __name__ == "__main__":
    test_policy_engine()
