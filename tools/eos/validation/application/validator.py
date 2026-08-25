"""
Wilsy Engineering Kernel

Engineering Kernel System Validator

Application orchestrator for institutional validation.
"""

from __future__ import annotations

from ..domain.models import ValidationReport
from ..domain.models import ValidationStatus
from ..rules.registry_rule import RegistryValidationRule
from ..rules.runtime_rule import RuntimeValidationRule
from ...kernel.bootstrap import KernelBootstrap


class EngineeringKernelSystemValidator:
    """
    Read-only Engineering Kernel validator.

    Orchestrates institutional validation rules.
    """

    def validate(
        self,
    ) -> ValidationReport:

        runtime = KernelBootstrap().boot()

        results = [
            RuntimeValidationRule().evaluate(runtime),
            RegistryValidationRule().evaluate(runtime),
        ]

        status = (
            ValidationStatus.PASSED
            if all(result.passed for result in results)
            else ValidationStatus.FAILED
        )

        return ValidationReport(
            results=results,
            status=status,
        )
