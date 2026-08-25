"""
Wilsy Engineering Kernel
Engineering Constitution Manager

Compliance Rule Contract
"""

from __future__ import annotations

from abc import ABC
from abc import abstractmethod

from .models import ComplianceFinding
from .models import ComplianceReport


class ComplianceRuleContract(ABC):
    """
    Institutional contract implemented by every constitutional
    compliance rule.
    """

    @property
    @abstractmethod
    def identifier(self) -> str:
        """
        Stable institutional identifier.
        """

    @property
    @abstractmethod
    def title(self) -> str:
        """
        Human-readable rule title.
        """

    @abstractmethod
    def evaluate(
        self,
        report: ComplianceReport,
    ) -> ComplianceFinding:
        """
        Evaluate constitutional compliance.

        This operation shall be read-only.
        """
