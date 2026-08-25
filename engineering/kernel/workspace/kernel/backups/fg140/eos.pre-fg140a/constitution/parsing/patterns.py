"""
Wilsy Engineering Kernel
Engineering Constitution Manager

Constitution Parsing Patterns

Institutional regular expressions shared by all parsing modules.
"""

from __future__ import annotations

import re

PART_PATTERN = re.compile(
    r"^# Part\b.*$",
    re.MULTILINE,
)

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
