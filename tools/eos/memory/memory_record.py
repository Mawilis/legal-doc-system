"""
===============================================================================
WILSY OS KERNEL — INSTITUTIONAL MEMORY RECORD DTO
===============================================================================
[EPITOME]:
    Defines immutable institutional memory record DTOs capturing execution telemetry, 
    artifacts, decisions, reviews, and event metadata for permanent storage.
    Engineered to billion-dollar enterprise production standards with zero tolerance 
    for missing symbols or technical debt.

[BIBLICAL FOUNDATION]:
    Psalm 119:160 — "The entirety of Your word is truth, and every one of Your righteous judgments endures forever."

[COLLABORATION & MAINTENANCE]:
    - Founder & Lead Architect: Wilson Khanyezi
    - Maintainers: Wilsy OS Core Engineering Team
    - Classification: Billion-Dollar Production Grade / Memory DTO
===============================================================================
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, ConfigDict, Field


class MemoryRecord(BaseModel):
    """
    [DTO SPECIFICATION]: Institutional Memory Record
    Immutable record capturing an execution lifecycle event, decision, or artifact 
    for permanent storage within Wilsy OS institutional memory.
    """
    model_config = ConfigDict(frozen=True, extra="forbid")

    record_id: str = Field(description="Unique institutional memory record identifier.")
    execution_id: str = Field(description="Associated Wilsy OS execution run identifier.")
    record_type: str = Field(description="Type of record (e.g., EXECUTION, DECISION, ARTIFACT, REVIEW, TELEMETRY).")
    producer: str = Field(description="Component or engine that produced the record.")
    title: str = Field(description="Descriptive title of the institutional record.")
    payload: Dict[str, Any] = Field(default_factory=dict, description="Structured record payload data.")
    tags: List[str] = Field(default_factory=list, description="Categorization tags for search and indexing.")
    checksum: str = Field(description="Cryptographic hash checksum verifying record integrity.")
    timestamp: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat(), description="ISO timestamp of record creation.")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional context and telemetry metadata.")
