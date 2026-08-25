"""
Wilsy Engineering Kernel

Runtime Validation Rule
"""

from __future__ import annotations

from ..domain.contracts import ValidationRuleContract
from ..domain.models import (
    ValidationFinding,
    ValidationResult,
    ValidationRule,
    ValidationSeverity,
)
from ...kernel.runtime import KernelRuntimeContext


class RuntimeValidationRule(ValidationRuleContract):
    """
    Validate that a Kernel Runtime Context exists.
    """

    RULE = ValidationRule(
        identifier="EK-RUNTIME-001",
        name="Kernel Runtime Exists",
        description="The Engineering Kernel shall expose a runtime context.",
    )

    def evaluate(
        self,
        runtime: KernelRuntimeContext,
    ) -> ValidationResult:

        passed = runtime is not None

        finding = None

        if not passed:
            finding = ValidationFinding(
                rule=self.RULE,
                severity=ValidationSeverity.ERROR,
                message="Kernel runtime context is missing.",
            )

        return ValidationResult(
            rule=self.RULE,
            passed=passed,
            finding=finding,
        )
