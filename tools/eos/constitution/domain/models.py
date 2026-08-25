"""
Wilsy Engineering Kernel
Engineering Constitution Manager

Institutional Domain Models
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import List


@dataclass(frozen=True)
class RepositoryEvidence:
    command: str
    output: str
    verified: bool
    timestamp: str


@dataclass(frozen=True)
class ValidationFinding:
    severity: str
    category: str
    location: str
    rationale: str


@dataclass(frozen=True)
class Law:
    identifier: str
    title: str


@dataclass(frozen=True)
class Article:
    identifier: str
    title: str
    laws: List[Law] = field(default_factory=list)


@dataclass(frozen=True)
class Part:
    identifier: str
    title: str
    articles: List[Article] = field(default_factory=list)


@dataclass(frozen=True)
class ConstitutionStructure:
    part_count: int
    article_count: int
    law_count: int


@dataclass(frozen=True)
class Constitution:
    specification_id: str
    version: str
    title: str
    mission: str
    parts: List[Part] = field(default_factory=list)
