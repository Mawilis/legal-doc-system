"""
Wilsy Engineering Kernel
Engineering Constitution Manager

Constitution Parser

Part Discovery
"""

from __future__ import annotations

import re
from pathlib import Path

from ..domain.models import Constitution
from ..domain.models import ConstitutionStructure
from ..domain.models import Part


class ConstitutionParser:
    """
    Read-only Engineering Constitution parser.
    """

    PART_PATTERN = re.compile(r"^# Part\b.*$", re.MULTILINE)

    ARTICLE_PATTERN = re.compile(
        r"^ARTICLE\s+\d+",
        re.MULTILINE,
    )

    LAW_PATTERN = re.compile(
        r"^LAW\s+EK-\d{3}",
        re.MULTILINE,
    )

    SPECIFICATION_PATTERN = re.compile(
        r"^Specification ID:\s*(.+)$",
        re.MULTILINE,
    )

    VERSION_PATTERN = re.compile(
        r"^Version:\s*(.+)$",
        re.MULTILINE,
    )

    TITLE_PATTERN = re.compile(
        r"^#\s+(.+)$",
        re.MULTILINE,
    )

    def load_document(
        self,
        path: Path,
    ) -> str:
        """
        Load the Engineering Constitution.
        """

        return path.read_text(encoding="utf-8")

    def discover_structure(
        self,
        document: str,
    ) -> ConstitutionStructure:
        """
        Read-only repository discovery.
        """

        return ConstitutionStructure(
            part_count=len(self.PART_PATTERN.findall(document)),
            article_count=len(self.ARTICLE_PATTERN.findall(document)),
            law_count=len(self.LAW_PATTERN.findall(document)),
        )

    def parse_header(
        self,
        document: str,
    ) -> Constitution:
        """
        Parse the institutional header.
        """

        specification = self.SPECIFICATION_PATTERN.search(document)
        version = self.VERSION_PATTERN.search(document)
        title = self.TITLE_PATTERN.search(document)

        return Constitution(
            specification_id=specification.group(1).strip() if specification else "",
            version=version.group(1).strip() if version else "",
            title=title.group(1).strip() if title else "",
            mission="",
            parts=[],
        )

    def parse_parts(
        self,
        document: str,
    ) -> list[Part]:
        """
        Parse constitutional Parts only.

        Articles and Laws are intentionally ignored during FG134D.
        """

        parts: list[Part] = []

        for index, match in enumerate(
            self.PART_PATTERN.findall(document),
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

    def parse(
        self,
        path: Path,
    ) -> Constitution:
        """
        Parse the Engineering Constitution.

        FG134E constructs:

        * Constitution
        * ConstitutionStructure
        * Part
        """

        document = self.load_document(path)

        structure = self.discover_structure(document)

        constitution = self.parse_header(document)

        constitution.parts.extend(
            self.parse_parts(document)
        )

        # Structure is intentionally retained for future parser packets.
        _ = structure

        return constitution