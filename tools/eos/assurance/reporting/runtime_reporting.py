"""
Wilsy Engineering Kernel

Engineering Assurance Reporting

Runtime Reporting

Runtime integration for Engineering Assurance Reporting.
"""

from __future__ import annotations

from ..domain.models import EngineeringAssuranceReport

from .assurance_ledger import AssuranceLedger
from .report_exporter import ReportExporter


class RuntimeReporting:
    """
    Read-only Engineering Assurance Runtime Reporting.

    Responsible only for coordinating immutable report recording
    and exporting.
    """

    def __init__(
        self,
    ) -> None:
        """
        Initialize Runtime Reporting dependencies.
        """

        self._ledger = AssuranceLedger()
        self._exporter = ReportExporter()

    def publish(
        self,
        report: EngineeringAssuranceReport,
    ) -> str:
        """
        Record and export an Engineering Assurance Report.
        """

        self._ledger.record(report)

        return self._exporter.export_json(report)

    @property
    def ledger(
        self,
    ) -> AssuranceLedger:
        """
        Access the immutable Assurance Ledger.
        """

        return self._ledger
