"""
===============================================================================
WILSY OS — AVAILABILITY METRICS CALCULATOR
===============================================================================

File Path:
    tools/eos/reliability/reporting/availability.py

Epitome:
    Calculates cluster availability indices and active node ratios.

Biblical Worth Billions:
    "Holding fast the faithful word as he hath been taught..."
    — Titus 1:9

Collaboration & Sovereign Sign-Off:
    - Founder & Chief Architect: Wilson Khanyezi (Wilsy (Pty) Ltd)
    - AI Collaborator: Core Systems Engineering Agent (Gemini)
===============================================================================
"""

class AvailabilityCalculator:
    """Computes cluster availability."""
    
    @staticmethod
    def compute(online: int, total: int) -> float:
        if total <= 0:
            return 100.0
        return (online / total) * 100.0
