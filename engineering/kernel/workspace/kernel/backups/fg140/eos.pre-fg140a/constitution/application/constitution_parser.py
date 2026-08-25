"""
Wilsy Engineering Kernel
Engineering Constitution Manager

Engineering Constitution Parser

Application Orchestrator
"""

from __future__ import annotations

from pathlib import Path

from ..domain.models import Constitution
from ..domain.models import ConstitutionStructure

from ..parsing.patterns import (
    PART_PATTERN,
    ARTICLE_PATTERN,
    LAW_PATTERN,
)

from ..parsing.header_parser import HeaderParser
from ..parsing.part_parser import PartParser


class ConstitutionParser:
    """
    Application orchestrator for the Engineering Constitution.

    This class coordinates parsing.

    It SHALL NOT implement parsing logic.

    It SHALL remain read-only.
    """

    def __init__(self) -> None:
        self._header_parser = HeaderParser()
        self._part_parser = PartParser()

    def load_document(
        self,
        path: Path,
    ) -> str:
        """
        Load the Engineering Constitution from disk.
        """

        return path.read_text(encoding="utf-8")

    def discover_structure(
        self,
        document: str,
    ) -> ConstitutionStructure:
        """
        Perform read-only structural discovery.
        """

        return ConstitutionStructure(
            part_count=len(PART_PATTERN.findall(document)),
            article_count=len(ARTICLE_PATTERN.findall(document)),
            law_count=len(LAW_PATTERN.findall(document)),
        )

    def parse(
        self,
        path: Path,
    ) -> Constitution:
        """
        Parse the Engineering Constitution.

        Current pipeline:

        Repository
            ↓
        HeaderParser
            ↓
        PartParser
            ↓
        Immutable Constitution
        """

        document = self.load_document(path)

        structure = self.discover_structure(document)

        constitution = self._header_parser.parse(document)

        constitution.parts.extend(
            self._part_parser.parse(document)
        )

        _ = structure

        return constitution