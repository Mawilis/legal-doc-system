"""
Wilsy Engineering Kernel
Engineering Constitution Manager

Header Parser
"""

from __future__ import annotations

from ..domain.models import Constitution
from .patterns import (
    SPECIFICATION_PATTERN,
    VERSION_PATTERN,
    TITLE_PATTERN,
)


class HeaderParser:
    """
    Parse the institutional header of the Engineering Constitution.

    This parser is read-only.
    """

    def parse(
        self,
        document: str,
    ) -> Constitution:
        specification = SPECIFICATION_PATTERN.search(document)
        version = VERSION_PATTERN.search(document)
        title = TITLE_PATTERN.search(document)

        return Constitution(
            specification_id=specification.group(1).strip() if specification else "",
            version=version.group(1).strip() if version else "",
            title=title.group(1).strip() if title else "",
            mission="",
            parts=[],
        )
