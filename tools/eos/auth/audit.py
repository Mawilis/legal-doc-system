"""
===============================================================================
WILSY OS — SOVEREIGN OPERATING SYSTEM
MODULE: FG212 INSTITUTIONAL AUTHENTICATION - SECURITY AUDIT
FILE: tools/eos/auth/audit.py
===============================================================================
Epitome:
    Logs authentication attempts, token validation failures, and authorization
    rejections to the immutable sovereign audit ledger.

Biblical Worth Billions:
    "Be diligent to know the state of your flocks, and commit your hearts to your herds."
    — Proverbs 27:23

Collaboration & Ownership:
    - Founder & Chief Architect: Wilson Khanyezi (Wilsy (Pty) Ltd)
    - AI Collaborator: Core Systems Engineering Agent
    - File Path: tools/eos/auth/audit.py
===============================================================================
"""

import logging
from datetime import datetime, timezone, timedelta
from typing import Any, Dict

logger = logging.getLogger("WilsyOS.SecurityAudit")


def log_auth_event(event_type: str, principal: str, success: bool, details: Dict[str, Any] = None):
    """Emits an immutable structured security audit log entry."""
    sast_tz = timezone(timedelta(hours=2))
    timestamp = datetime.now(sast_tz).strftime("%B %d, %Y | %H:%M:%S SAST")
    status_str = "SUCCESS" if success else "REJECTED"
    
    log_payload = {
        "timestamp": timestamp,
        "event_type": event_type,
        "principal": principal,
        "status": status_str,
        "details": details or {}
    }
    logger.info(f"[SECURITY AUDIT] {log_payload}")
    return log_payload
