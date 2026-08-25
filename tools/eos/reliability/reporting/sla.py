"""
===============================================================================
WILSY OS — SLA COMPLIANCE CALCULATOR
===============================================================================

File Path:
    tools/eos/reliability/reporting/sla.py

Epitome:
    Calculates enterprise SLA uptime percentages and reliability compliance.

Biblical Worth Billions:
    "Better is it that thou shouldest not vow, than that thou shouldest vow and not pay."
    — Ecclesiastes 5:5

Collaboration & Sovereign Sign-Off:
    - Founder & Chief Architect: Wilson Khanyezi (Wilsy (Pty) Ltd)
    - AI Collaborator: Core Systems Engineering Agent (Gemini)
===============================================================================
"""

class SLACalculator:
    """Calculates SLA metrics."""
    
    @staticmethod
    def calculate_uptime(total_minutes: float, downtime_minutes: float) -> float:
        if total_minutes <= 0:
            return 100.0
        return max(0.0, ((total_minutes - downtime_minutes) / total_minutes) * 100.0)
