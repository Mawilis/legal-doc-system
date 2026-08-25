"""
Wilsy Engineering Kernel

Engineering Assurance Reporting

Report Formatter

Deterministic serialization of Engineering Assurance Reports.
"""

from __future__ import annotations

import json
from dataclasses import asdict

from ..domain.models import EngineeringAssuranceReport


class ReportFormatter:
    """
    Read-only Engineering Assurance Report Formatter.

    Responsible only for producing deterministic serialized
    representations of immutable Engineering Assurance Reports.
    """

    def to_json(
        self,
        report: EngineeringAssuranceReport,
    ) -> str:
        """
        Serialize an Engineering Assurance Report to JSON.
        """

        return json.dumps(
            asdict(report),
            indent=2,
            sort_keys=True,
            default=str,
        )
