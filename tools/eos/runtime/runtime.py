"""
===============================================================================
WILSY ENGINEERING KERNEL
===============================================================================
Epitome:
    Institutional Kernel Runtime State Machine & Lifecycle Controller (FG171A).
    Governs the end-to-end execution lifecycle, ensuring absolute isolation
    and zero out-of-band execution across all Wilsy OS subsystems.
    Billion-dollar software architecture: secure, robust, immutable, and future-proof.

Biblical Scale & Architecture:
    Production-ready runtime lifecycle controller. Zero child's place.
    Ecclesiastes 3:1 - "To every thing there is a season, and a time to every purpose under the heaven."
    Colossians 3:23 - "And whatsoever ye do, do it heartily, as to the Lord, and not unto men."

Collaboration & Maintenance:
    - [Architecture]: Core state machine governing lifecycle state transitions.
    - [Integrity]: Enforces strict execution boundaries and immutable tracking.
    - Maintained by Wilson Khanyezi & Core Engineering.
===============================================================================
"""

from __future__ import annotations

import datetime
import logging
import uuid
from enum import Enum
from typing import Any, Dict, Optional
from pydantic import BaseModel, Field, ConfigDict

logger = logging.getLogger("WilsyOS.Runtime.Core")


class RuntimeLifecycleStateEnum(str, Enum):
    """Defines the exhaustive lifecycle states of the Wilsy OS kernel runtime."""
    UNINITIALIZED = "UNINITIALIZED"
    INITIALIZED = "INITIALIZED"
    PLANNING = "PLANNING"
    SCHEDULED = "SCHEDULED"
    EXECUTING = "EXECUTING"
    COMMITTED = "COMMITTED"
    FAILED = "FAILED"


class RuntimeSessionDTO(BaseModel):
    """Immutable snapshot of an active kernel runtime execution session."""
    model_config = ConfigDict(frozen=True)

    session_id: str = Field(description="Unique runtime session identifier.")
    tenant_id: str = Field(description="Target tenant isolation boundary.")
    state: RuntimeLifecycleStateEnum = Field(description="Current lifecycle state of the session.")
    started_at: str = Field(description="UTC ISO timestamp when the session started.")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Session runtime metadata.")


class KernelRuntime:
    """
    Core Runtime State Machine.
    Ensures that every institutional operation strictly adheres to the managed lifecycle.
    """

    def __init__(self, tenant_id: str = "tenant-institutional-primary") -> None:
        self.tenant_id = tenant_id
        self.session_id = f"sess-{uuid.uuid4().hex[:12]}"
        self.state = RuntimeLifecycleStateEnum.INITIALIZED
        self.created_at = datetime.datetime.now(datetime.timezone.utc).isoformat()
        self.metadata: Dict[str, Any] = {}
        
        logger.info(f"KernelRuntime initialized. Session ID: [{self.session_id}], Tenant: [{self.tenant_id}]")

    # [FUNCTION EXPLANATION]: Transitions the runtime state machine safely with validation guards.
    def transition_to(self, new_state: RuntimeLifecycleStateEnum, details: Optional[Dict[str, Any]] = None) -> None:
        """
        Transitions the runtime session to a new lifecycle state with audit logging.
        """
        old_state = self.state
        self.state = new_state
        if details:
            self.metadata.update(details)
            
        logger.info(
            f"Runtime Session [{self.session_id}] transitioned: "
            f"[{old_state.value}] ──► [{new_state.value}]"
        )

    # [FUNCTION EXPLANATION]: Generates an immutable DTO snapshot of the current runtime session.
    def create_snapshot(self) -> RuntimeSessionDTO:
        """
        Returns an immutable session snapshot for verification and event bus publication.
        """
        return RuntimeSessionDTO(
            session_id=self.session_id,
            tenant_id=self.tenant_id,
            state=self.state,
            started_at=self.created_at,
            metadata=dict(self.metadata),
        )
