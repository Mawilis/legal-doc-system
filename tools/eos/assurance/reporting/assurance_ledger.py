"""
Wilsy Engineering Kernel

Engineering Assurance Reporting

Assurance Ledger

Immutable institutional ledger for Engineering Assurance Reports.
"""

from __future__ import annotations

from ..domain.models import EngineeringAssuranceReport


class AssuranceLedger:
    """
    Read-only Engineering Assurance Ledger.

    Responsible only for maintaining an immutable collection of
    Engineering Assurance Reports.
    """

    def __init__(
        self,
    ) -> None:
        """
        Initialize an empty Assurance Ledger.
        """

        self._reports: list[EngineeringAssuranceReport] = []

    def record(
        self,
        report: EngineeringAssuranceReport,
    ) -> None:
        """
        Record an immutable Engineering Assurance Report.
        """

        self._reports.append(report)

    def reports(
        self,
    ) -> tuple[EngineeringAssuranceReport, ...]:
        """
        Return all recorded Engineering Assurance Reports as an
        immutable tuple.
        """

        return tuple(self._reports)
