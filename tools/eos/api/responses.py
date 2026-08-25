"""
===============================================================================
WILSY OS — SOVEREIGN OPERATING SYSTEM
MODULE: FG211 INSTITUTIONAL REST API - UNIFORM RESPONSES
FILE: tools/eos/api/responses.py
===============================================================================
Epitome:
    Enforces standardized JSON response formatting and SAST timestamping for
    all FG211 Kernel Gateway endpoints.

Biblical Worth Billions:
    "In the mouth of two or three witnesses shall every word be established."
    — 2 Corinthians 13:1

Collaboration & Ownership:
    - Founder & Chief Architect: Wilson Khanyezi (Wilsy (Pty) Ltd)
    - AI Collaborator: Core Systems Engineering Agent
    - File Path: tools/eos/api/responses.py
===============================================================================
"""

from datetime import datetime, timezone, timedelta
from typing import Any, Dict, Optional
from fastapi.responses import JSONResponse
from tools.eos.api.schemas import StandardApiResponse


def format_response(
    data: Optional[Any] = None,
    message: str = "Operation executed successfully.",
    status_code: int = 200,
    success: bool = True,
    execution_id: str = "KEXEC-FG211-GATEWAY"
) -> JSONResponse:
    """Formats any endpoint return value into the Wilsy OS sovereign response envelope."""
    sast_tz = timezone(timedelta(hours=2))
    timestamp = datetime.now(sast_tz).strftime("%B %d, %Y | %H:%M:%S SAST")

    response_model = StandardApiResponse(
        success=success,
        status_code=status_code,
        message=message,
        data=data,
        timestamp=timestamp,
        execution_id=execution_id
    )
    return JSONResponse(status_code=status_code, content=response_model.dict())
