"""
Wilsy Engineering Kernel

Registry Validation Rule
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


class RegistryValidationRule(ValidationRuleContract):
    """
    Validate that the Kernel Registry exists.
    """

    RULE = ValidationRule(
        identifier="EK-REGISTRY-001",
        name="Kernel Registry Exists",
        description="The Engineering Kernel shall expose a Foundation Registry.",
    )

    def evaluate(
        self,
        runtime: KernelRuntimeContext,
    ) -> ValidationResult:

        passed = runtime.registry is not None

        finding = None

        if not passed:
            finding = ValidationFinding(
                rule=self.RULE,
                severity=ValidationSeverity.ERROR,
                message="Kernel Registry is missing.",
            )

        return ValidationResult(
            rule=self.RULE,
            passed=passed,
            finding=finding,
        )
