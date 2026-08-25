"""
===============================================================================
WILSY ENGINEERING KERNEL
===============================================================================
Epitome:
    Wilsy OS Institutional API Gateway Package (FG169).
    Exposes kernel capabilities, execution history, digital twins, intelligence,
    observability, and artifact repositories through a production-grade,
    contract-driven REST/ASGI platform interface.
    Billion-dollar software architecture: secure, robust, immutable, and future-proof.

Biblical Scale & Architecture:
    Institutional platform API entrypoint. Zero child's place.
    Isaiah 22:22 - "And the key of the house of David will I lay upon his shoulder;
                   so he shall open, and none shall shut; and he shall shut, and none shall open."
    Proverbs 8:14 - "Counsel is mine, and sound wisdom: I am understanding; I have strength."

Collaboration & Maintenance:
    - [Architecture]: Master entrypoint for Wilsy OS Institutional API gateway.
    - [Integration]: Exposes endpoints for Kernel, Repository, Twin, History, and Telemetry.
    - Maintained by Wilson Khanyezi & Core Engineering.
===============================================================================
"""

from __future__ import annotations

import logging

logger = logging.getLogger("WilsyOS.API")

# [FUNCTION EXPLANATION]: Lazy/Safe import loader for API package components.
try:
    from .errors import APIError, APIErrorDetail, ResourceNotFoundError, ValidationError
    from .responses import APIResponse, APIStatus, PaginatedResponse
    from .contracts import (
        KernelSessionDTO,
        RepositoryMetricsDTO,
        ArtifactCatalogDTO,
        DigitalTwinSnapshotDTO,
        ObservabilityDTO,
        IntelligenceReasoningDTO,
        SystemHealthDTO,
    )
    from .router import APIRouter
    from .server import WilsyAPIServer

    __all__ = [
        "APIError",
        "APIErrorDetail",
        "ResourceNotFoundError",
        "ValidationError",
        "APIResponse",
        "APIStatus",
        "PaginatedResponse",
        "KernelSessionDTO",
        "RepositoryMetricsDTO",
        "ArtifactCatalogDTO",
        "DigitalTwinSnapshotDTO",
        "ObservabilityDTO",
        "IntelligenceReasoningDTO",
        "SystemHealthDTO",
        "APIRouter",
        "WilsyAPIServer",
    ]
except ImportError as e:
    logger.debug(f"API package submodules initializing... ({e})")
    __all__ = []
