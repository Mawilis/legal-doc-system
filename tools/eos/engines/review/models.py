"""
===============================================================================
WILSY OS REVIEW ENGINE: ARBITRATION MODELS
===============================================================================
Epitome:
    The schema for human/AI collaborative decision making. An approval is 
    not just a "thumbs up"; it is a cryptographic, audited event.

Biblical Scale & Architecture:
    These models represent the "Sentinel Signature." They capture reviewer 
    intent, forensic cross-references, and the final state of the artifact.
    Frozen dataclasses are used to guarantee immutability of the review record.

Collaboration & Maintenance:
    - ReviewSignature: Used to record the identity, timestamp, and verification 
      status of a specific reviewer.
    - ReviewDecision: The aggregate container for the review process, holding 
      multiple signatures and the final rationale.
===============================================================================
"""

from dataclasses import dataclass
from typing import List
from datetime import datetime

@dataclass(frozen=True)
class ReviewSignature:
    """
    Immutable record of a single reviewer's input.
    """
    reviewer_id: str
    timestamp: datetime
    comment: str
    hash_verified: bool

@dataclass(frozen=True)
class ReviewDecision:
    """
    Finalized outcome of the arbitration process.
    """
    artifact_id: str
    approved: bool
    signatures: List[ReviewSignature]
    rationale: str
