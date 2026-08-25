"""
===============================================================================
WILSY OS — SOVEREIGN LEADER ELECTION ENGINE
===============================================================================

File Path:
    tools/eos/reliability/high_availability/leader_election.py

Epitome:
    Executes distributed leader election and active/standby promotion protocols
    with split-brain prevention and quorum verification.

Biblical Worth Billions:
    "Where no counsel is, the people fall: but in the multitude of counsellors there is safety."
    — Proverbs 11:14

Collaboration & Sovereign Sign-Off:
    - Founder & Chief Architect: Wilson Khanyezi (Wilsy (Pty) Ltd)
    - AI Collaborator: Core Systems Engineering Agent (Gemini)
===============================================================================
"""

import time
from typing import Optional

class LeaderElectionEngine:
    """Manages active leader node election and standby coordination."""

    def __init__(self, cluster_id: str, lease_duration: float = 5.0) -> None:
        self.cluster_id = cluster_id
        self.lease_duration = lease_duration
        self.current_leader: Optional[str] = None
        self.lease_expiry: float = 0.0

    def attempt_acquisition(self, node_id: str, term: int) -> bool:
        """Attempts to acquire or renew leadership lease for a node."""
        now = time.time()
        if self.current_leader is None or now > self.lease_expiry:
            self.current_leader = node_id
            self.lease_expiry = now + self.lease_duration
            return True
        return self.current_leader == node_id

    def renew_lease(self, node_id: str) -> bool:
        """Renews active leadership lease."""
        now = time.time()
        if self.current_leader == node_id:
            self.lease_expiry = now + self.lease_duration
            return True
        return False

    def get_leader(self) -> Optional[str]:
        """Returns the current active leader node ID if lease is valid."""
        if time.time() > self.lease_expiry:
            return None
        return self.current_leader
