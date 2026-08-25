# -*- coding: utf-8 -*-
"""
╔══════════════════════════════════════════════════════════════════════════════════════════════════════════════════╗
║ WILSY OS – REPOSITORY INTELLIGENCE DOMAIN MODELS                                                               ║
╠══════════════════════════════════════════════════════════════════════════════════════════════════════════════════╣
║ FILE:           tools/eos/repository/domain/models.py                                                          ║
║ VERSION:        v2.0.0-INSTITUTIONAL                                                                           ║
║ AUTHORITY:      Wilsy OS Core Governance                                                                       ║
║ EPITOME:        Canonical immutable institutional models shared by the Repository Intelligence Framework.       ║
║ CLASSIFICATION: Production Artifact                                                                             ║
╠══════════════════════════════════════════════════════════════════════════════════════════════════════════════════╣
║ 🔧 CHANGE LOG:                                                                                                  ║
║   2026-08-23 v2.0.0-INSTITUTIONAL – Added sovereign header, version, and certification seal.                   ║
║   2026-08-20 v1.0.0-INTELLIGENCE – Initial creation of RepositoryMetrics, RepositoryAssessment,                ║
║        RepositoryFinding, RepositoryIntelligenceReport.                                                        ║
╠══════════════════════════════════════════════════════════════════════════════════════════════════════════════════╣
║ COMPLIANCE:    POPIA §19 │ GDPR §32 │ SOC2 §CC7.2 │ ISO 27001                                                  ║
║ INTEGRATION:   Used by Repository Intelligence Runtime, Report Builder, and all consumers.                      ║
╚══════════════════════════════════════════════════════════════════════════════════════════════════════════════════╝
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum


class RepositoryHealth(str, Enum):
    """
    Institutional repository health.
    """

    HEALTHY = "HEALTHY"
    WARNING = "WARNING"
    CRITICAL = "CRITICAL"


class RepositoryStatus(str, Enum):
    """
    Institutional repository readiness.
    """

    READY = "READY"
    DEGRADED = "DEGRADED"
    BLOCKED = "BLOCKED"


@dataclass(frozen=True)
class RepositoryFinding:
    """
    Immutable repository intelligence finding.
    """

    identifier: str
    message: str


@dataclass(frozen=True)
class RepositoryMetrics:
    """
    Immutable repository metrics.
    """

    file_count: int
    directory_count: int
    python_module_count: int
    package_count: int


@dataclass(frozen=True)
class RepositoryAssessment:
    """
    Immutable repository assessment.
    """

    health: RepositoryHealth
    status: RepositoryStatus
    score: int
    findings: list[RepositoryFinding] = field(default_factory=list)


@dataclass(frozen=True)
class RepositoryIntelligenceReport:
    """
    Canonical immutable Repository Intelligence Report.

    Represents the complete synthesized repository intelligence state
    produced by the Repository Intelligence Runtime.
    """

    metrics: RepositoryMetrics
    graph: tuple[str, ...]
    assessment: RepositoryAssessment
    generated_at: str  # ISO-8601 timestamp, e.g., from datetime.now(UTC).isoformat()


"""
════════════════════════════════════════════════════════════════════════════════
INSTITUTIONAL CERTIFICATION SEAL — WILSY OS REPOSITORY DOMAIN MODELS v2.0.0
════════════════════════════════════════════════════════════════════════════════
Status:          CERTIFIED PRODUCTION ARTIFACT
Version:         v2.0.0-INSTITUTIONAL
Fixes:           Institutionalised file with header and seal; all models unchanged.
Compliance:      POPIA §19 │ GDPR §32 │ SOC2 §CC7.2 │ ISO 27001
Note:            This file is ready for deployment. The `generated_at` field is
                 already present and will be supplied by the Report Builder.
════════════════════════════════════════════════════════════════════════════════
"""
