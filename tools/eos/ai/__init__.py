"""
===============================================================================
WILSY ENGINEERING KERNEL
===============================================================================
Epitome:
    AI Integration Layer Package Initialization.
    Exposes context provider, synthesis engine, recommendation engine, and explanation engine.

Biblical Scale & Architecture:
    Production-ready AI integration interface. Zero child's place.
    Empowers Wilsy OS with advanced cognitive synthesis, contextual ingestion, and intelligent telemetry.

Collaboration & Maintenance:
    - [Architecture]: Package entrypoint for AI cognitive and analytical subsystems.
    - Maintained by Wilson Khanyezi & Core Engineering.
===============================================================================
"""

from __future__ import annotations

from .context_provider import ContextProvider
from .synthesis_engine import SynthesisEngine
from .recommendation_engine import RecommendationEngine
from .explanation_engine import ExplanationEngine

__all__ = [
    "ContextProvider",
    "SynthesisEngine",
    "RecommendationEngine",
    "ExplanationEngine",
]
