"""
Wilsy Engineering Kernel
Engineering Constitution Manager

Part Parser
"""

from __future__ import annotations

from ..domain.models import Part
from .patterns import PART_PATTERN


class PartParser:
    """
    Parse constitutional Parts.

    This parser is read-only.
    """

    def parse(
        self,
        document: str,
    ) -> list[Part]:
        parts: list[Part] = []

        for index, match in enumerate(
            PART_PATTERN.findall(document),
            start=1,
        ):
            parts.append(
                Part(
                    identifier=f"PART-{index}",
                    title=match.replace("#", "").strip(),
                    articles=[],
                )
            )

        return parts
