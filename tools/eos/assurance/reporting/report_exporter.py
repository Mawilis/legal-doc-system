"""
Wilsy Engineering Kernel

Engineering Assurance Reporting

Report Exporter

Read-only export of Engineering Assurance Reports.
"""

from __future__ import annotations

from ..domain.models import EngineeringAssuranceReport
from .report_formatter import ReportFormatter


class ReportExporter:
    """
    Read-only Engineering Assurance Report Exporter.

    Responsible only for exporting immutable Engineering
    Assurance Reports.
    """

    def __init__(
        self,
    ) -> None:
        """
        Initialize Report Exporter dependencies.
        """

        self._formatter = ReportFormatter()

    def export_json(
        self,
        report: EngineeringAssuranceReport,
    ) -> str:
        """
        Export an Engineering Assurance Report as JSON.
        """

        return self._formatter.to_json(report)
