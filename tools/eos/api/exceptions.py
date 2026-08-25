"""
===============================================================================
WILSY OS — SOVEREIGN OPERATING SYSTEM
MODULE: FG211 INSTITUTIONAL REST API - EXCEPTIONS ENGINE
FILE: tools/eos/api/exceptions.py
===============================================================================
Epitome:
    Defines sovereign HTTP and kernel exceptions for the FG211 Kernel Gateway,
    ensuring deterministic error payloads, status code mapping, and audit logging.

Biblical Worth Billions:
    "In the mouth of two or three witnesses shall every word be established."
    — 2 Corinthians 13:1

Collaboration & Ownership:
    - Founder & Chief Architect: Wilson Khanyezi (Wilsy (Pty) Ltd)
    - AI Collaborator: Core Systems Engineering Agent
    - File Path: tools/eos/api/exceptions.py
===============================================================================
"""

from typing import Any, Dict, Optional


class WilsyAPIException(Exception):
    """Base institutional exception for all Wilsy OS API gateway errors."""
    def __init__(self, message: str, status_code: int = 500, details: Optional[Dict[str, Any]] = None):
        super().__init__(message)
        self.message = message
        self.status_code = status_code
        self.details = details or {}


class KernelGatewayError(WilsyAPIException):
    """Raised when kernel execution or runtime dispatch fails."""
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(message=message, status_code=502, details=details)


class ContractValidationException(WilsyAPIException):
    """Raised when request payload or schema validation fails."""
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(message=message, status_code=422, details=details)


class UnauthorizedAccessException(WilsyAPIException):
    """Raised when authentication credentials are missing or invalid."""
    def __init__(self, message: str = "Unauthorized kernel access."):
        super().__init__(message=message, status_code=401)


class ForbiddenOperationException(WilsyAPIException):
    """Raised when authenticated identity lacks required role/permissions."""
    def __init__(self, message: str = "Forbidden kernel operation."):
        super().__init__(message=message, status_code=403)
