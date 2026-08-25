"""
Wilsy Engineering Kernel
Engineering Constitution Manager

Compliance Engine

Read-only orchestration of constitutional compliance rules.
"""

from __future__ import annotations

from typing import Iterable

from .models import (
    ComplianceFinding,
    ComplianceReport,
    ComplianceRule,
    ComplianceStatus,
)
from .rule import ComplianceRuleContract


class ComplianceEngine:
    """
    Read-only constitutional compliance orchestrator.
    """

    def evaluate(
        self,
        rules: Iterable[ComplianceRuleContract],
    ) -> ComplianceReport:
        """
        Execute all compliance rules and return an immutable report.
        """

        evaluated_rules: list[ComplianceRule] = []
        findings: list[ComplianceFinding] = []

        overall_status = ComplianceStatus.COMPLIANT

        for rule in rules:
            finding = rule.evaluate(
                ComplianceReport()
            )

            evaluated_rules.append(
                ComplianceRule(
                    identifier=rule.identifier,
                    title=rule.title,
                    description="",
                )
            )

            findings.append(finding)

            if finding.status == ComplianceStatus.NON_COMPLIANT:
                overall_status = ComplianceStatus.NON_COMPLIANT
            elif (
                finding.status == ComplianceStatus.WARNING
                and overall_status != ComplianceStatus.NON_COMPLIANT
            ):
                overall_status = ComplianceStatus.WARNING

        return ComplianceReport(
            evaluated_rules=evaluated_rules,
            findings=findings,
            status=overall_status,
        )
