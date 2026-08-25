"""
Wilsy Engineering Kernel

Validation Contracts
"""

from __future__ import annotations

from abc import ABC
from abc import abstractmethod

from .models import ValidationResult


class ValidationRuleContract(ABC):
    """
    Institutional contract implemented by every validation rule.
    """

    @abstractmethod
    def evaluate(
        self,
    ) -> ValidationResult:
        """
        Execute read-only validation.
        """
        raise NotImplementedError
