"""
===============================================================================
WILSY ENGINEERING KERNEL
===============================================================================
Epitome:
    Package initialization surface for the Repository Dependency Intelligence Engine.
    Exposes canonical boundaries for resolving and analyzing complex internal 
    and external code dependency graphs.

Biblical Scale & Architecture:
    This is a billion-dollar, production-ready interface gateway. No child's place.
    Enforces strict package encapsulation. It ensures that downstream analytical
    drivers only consume high-level orchestration components, preventing raw parsing
    subroutines from polluting the system's global architectural footprint.

Collaboration & Maintenance:
    - [Encapsulation]: Controls entry points via a rigid `__all__` whitelist.
    - [Performance]: Maintains zero-overhead static tracking during system boot phase.
    - [Compliance]: Satisfies Layering and Isolation boundaries defined in the Kernel Constitution.

===============================================================================
"""

from __future__ import annotations

import logging

# Initialize institutional logger for package-level diagnostics
logger = logging.getLogger("wilsy.eos.repository.dependency")

try:
    # Orchestration hooks exported to the higher-order reporting domains
    from .analyzer import DependencyAnalyzer
    from .graph import DependencyGraph
    
    logger.debug("Successfully bound repository dependency analytical layers to public facade.")

except ImportError as err:
    # Phased-migration guard ensuring package compilation remains resilient during structural rollouts
    logger.warning(
        f"Dependency engine submodules initialized in decoupled phase posture: {err}. "
        f"Ensure downstream components resolve dependencies through dynamic interfaces."
    )

# Strict definition of allowed architectural components exposed to outer kernels
__all__ = [
    "DependencyAnalyzer",
    "DependencyGraph",
]
