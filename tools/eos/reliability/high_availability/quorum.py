"""
===============================================================================
WILSY OS — QUORUM VERIFICATION ENGINE
===============================================================================

File Path:
    tools/eos/reliability/high_availability/quorum.py

Epitome:
    Enforces majority quorum verification for leader elections and cluster state changes
    to prevent split-brain scenarios.

Biblical Worth Billions:
    "A house divided against itself cannot stand."
    — Mark 3:25

Collaboration & Sovereign Sign-Off:
    - Founder & Chief Architect: Wilson Khanyezi (Wilsy (Pty) Ltd)
    - AI Collaborator: Core Systems Engineering Agent (Gemini)
===============================================================================
"""

class QuorumEngine:
    """Verifies cluster quorum thresholds."""

    @staticmethod
    def verify_quorum(active_nodes: int, total_nodes: int) -> bool:
        """Returns True if active nodes satisfy the strict majority quorum (N/2 + 1)."""
        required = (total_nodes // 2) + 1
        return active_nodes >= required
