"""WILSY OS SOVEREIGN ARTIFACT — API ERROR BOUNDARY
TITLE: Institutional API Error Taxonomy and HTTP Translation
VERSION: v1.0.15-STRUCTURE-COMPLIANCE
AUTHORITY: Wilsy OS Core Governance / Kennel EOS boundary
EPITOME: Canonical WilsyAPIException compatibility bridge and bounded HTTP error translation.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tools/eos/api/errors.py
COLLABORATION / OWNERSHIP: Wilson Khanyezi; Core Engineering
CERTIFICATION/UPDATE DATE: 2026-08-29
CHANGELOG: v1.0.15-STRUCTURE-COMPLIANCE — governed bridge, bounded translation, modern HTTP 422 cleanup.
COMPLIANCE: POPIA §19; GDPR Article 32; SOC 2 CC7.2; ISO 27001.
SECURITY/PRIVACY POSTURE: debug=False suppresses traces; details are bounded; unexpected errors become HTTP 500.
TENANT BOUNDARY: No tenant resolution or authorization.
AUTHORITY BOUNDARY: API error taxonomy/HTTP translation only; no authentication, principal, membership, or authorization truth.
FINANCIAL AUTHORITY BOUNDARY: Kennel EOS exclusively owns financial execution.
"""
from __future__ import annotations


import datetime
import logging
import traceback
from enum import Enum
from typing import Any, Dict, List, Optional, Union

from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from tools.eos.api.exceptions import WilsyAPIException

logger = logging.getLogger("WilsyOS.API.Errors")
VERSION = "v1.0.15-STRUCTURE-COMPLIANCE"


class APIErrorCode(str, Enum):
    """Enumeration of institutional Wilsy OS error codes."""
    RESOURCE_NOT_FOUND = "RESOURCE_NOT_FOUND"
    VALIDATION_ERROR = "VALIDATION_ERROR"
    UNAUTHORIZED = "UNAUTHORIZED"
    FORBIDDEN = "FORBIDDEN"
    INTERNAL_KERNEL_ERROR = "INTERNAL_KERNEL_ERROR"
    SERVICE_UNAVAILABLE = "SERVICE_UNAVAILABLE"
    BAD_REQUEST = "BAD_REQUEST"
    CONFLICT = "CONFLICT"


class APIErrorDetail(BaseModel):
    """Structured detail object attached to an institutional API error."""
    field: Optional[str] = Field(default=None, description="Target request field or attribute name.")
    message: str = Field(description="Human-readable detail message.")
    code: Optional[str] = Field(default=None, description="Specific sub-error code.")


class APIErrorModel(BaseModel):
    """Standardized institutional API error response body schema."""
    success: bool = Field(default=False, description="Always False for error responses.")
    error_code: str = Field(description="Institutional error code string.")
    message: str = Field(description="Primary high-level error message.")
    http_status: int = Field(description="HTTP status code integer.")
    execution_id: str = Field(default="exec-unknown", description="Tracing execution run identifier.")
    timestamp: str = Field(default_factory=lambda: datetime.datetime.now(datetime.timezone.utc).isoformat(), description="UTC timestamp of error occurrence.")
    details: List[APIErrorDetail] = Field(default_factory=list, description="List of granular error details.")
    stack_trace: Optional[str] = Field(default=None, description="Debugging stack trace (included in dev mode).")


class APIError(Exception):
    """Base exception for all Wilsy OS institutional API errors."""

    # [FUNCTION EXPLANATION]: Initializes base API exception with status, error codes, and details.
    def __init__(
        self,
        message: str,
        http_status: int = status.HTTP_500_INTERNAL_SERVER_ERROR,
        error_code: Union[APIErrorCode, str] = APIErrorCode.INTERNAL_KERNEL_ERROR,
        details: Optional[List[APIErrorDetail]] = None,
        execution_id: str = "exec-unknown",
    ) -> None:
        super().__init__(message)
        self.message = message
        self.http_status = http_status
        self.error_code = error_code.value if isinstance(error_code, APIErrorCode) else str(error_code)
        self.details = details or []
        self.execution_id = execution_id

    # [FUNCTION EXPLANATION]: Converts exception instance into a standardized JSONResponse object.
    def to_response(self, include_trace: bool = False) -> JSONResponse:
        trace_str = traceback.format_exc() if include_trace else None
        model = APIErrorModel(
            success=False,
            error_code=self.error_code,
            message=self.message,
            http_status=self.http_status,
            execution_id=self.execution_id,
            details=self.details,
            stack_trace=trace_str,
        )
        return JSONResponse(status_code=self.http_status, content=model.model_dump(mode="json"))


# Derived Institutional Exceptions

class ResourceNotFoundError(APIError):
    """Raised when a requested resource or artifact cannot be located."""
    def __init__(self, resource_type: str, resource_id: str, execution_id: str = "exec-unknown") -> None:
        super().__init__(
            message=f"{resource_type} with identifier '{resource_id}' was not found.",
            http_status=status.HTTP_404_NOT_FOUND,
            error_code=APIErrorCode.RESOURCE_NOT_FOUND,
            execution_id=execution_id,
        )


class ValidationError(APIError):
    """Raised when request payload or parameters fail validation rules."""
    def __init__(self, message: str, details: Optional[List[APIErrorDetail]] = None, execution_id: str = "exec-unknown") -> None:
        super().__init__(
            message=message,
            http_status=status.HTTP_422_UNPROCESSABLE_CONTENT,
            error_code=APIErrorCode.VALIDATION_ERROR,
            details=details,
            execution_id=execution_id,
        )


class UnauthorizedError(APIError):
    """Raised when request lacks valid authentication credentials."""
    def __init__(self, message: str = "Authentication credentials were not provided or are invalid.", execution_id: str = "exec-unknown") -> None:
        super().__init__(
            message=message,
            http_status=status.HTTP_401_UNAUTHORIZED,
            error_code=APIErrorCode.UNAUTHORIZED,
            execution_id=execution_id,
        )


class ForbiddenError(APIError):
    """Raised when authenticated user lacks permissions for a resource."""
    def __init__(self, message: str = "Access denied for the requested institutional action.", execution_id: str = "exec-unknown") -> None:
        super().__init__(
            message=message,
            http_status=status.HTTP_403_FORBIDDEN,
            error_code=APIErrorCode.FORBIDDEN,
            execution_id=execution_id,
        )


class ServiceUnavailableError(APIError):
    """Raised when a subsystem or backing engine is offline or unresponsive."""
    def __init__(self, subsystem: str, execution_id: str = "exec-unknown") -> None:
        super().__init__(
            message=f"Subsystem '{subsystem}' is currently unavailable.",
            http_status=status.HTTP_503_SERVICE_UNAVAILABLE,
            error_code=APIErrorCode.SERVICE_UNAVAILABLE,
            execution_id=execution_id,
        )


# [FUNCTION EXPLANATION]: Registers global institutional exception handlers onto FastAPI app.
def register_error_handlers(app: FastAPI, debug: bool = False) -> None:
    """
    Hooks custom exception handlers into a FastAPI application instance.

    Args:
        app (FastAPI): The target FastAPI application instance.
        debug (bool): Flag indicating whether stack traces should be returned in responses.
    """

    @app.exception_handler(APIError)
    async def api_error_handler(request: Request, exc: APIError) -> JSONResponse:
        logger.warning(f"API Exception [{exc.error_code}]: {exc.message} (Path: {request.url.path})")
        return exc.to_response(include_trace=debug)

    @app.exception_handler(RequestValidationError)
    async def validation_error_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
        details = [
            APIErrorDetail(
                field=".".join(str(loc) for loc in err.get("loc", [])),
                message=err.get("msg", "Invalid parameter"),
                code=err.get("type", "value_error"),
            )
            for err in exc.errors()
        ]
        val_exc = ValidationError(
            message="Request parameter or body validation failed.",
            details=details,
        )
        return val_exc.to_response(include_trace=debug)

    @app.exception_handler(WilsyAPIException)
    async def wilsy_api_exception_handler(request: Request, exc: WilsyAPIException) -> JSONResponse:
        code_map = {
            status.HTTP_401_UNAUTHORIZED: APIErrorCode.UNAUTHORIZED,
            status.HTTP_403_FORBIDDEN: APIErrorCode.FORBIDDEN,
            status.HTTP_422_UNPROCESSABLE_CONTENT: APIErrorCode.VALIDATION_ERROR,
            status.HTTP_502_BAD_GATEWAY: APIErrorCode.SERVICE_UNAVAILABLE,
        }
        mapped = code_map.get(exc.status_code, APIErrorCode.INTERNAL_KERNEL_ERROR)
        bounded = APIError(
            message=exc.message,
            http_status=exc.status_code,
            error_code=mapped,
            details=[],
            execution_id=getattr(request.state, "execution_id", "exec-unknown"),
        )
        return bounded.to_response(include_trace=debug)

    @app.exception_handler(Exception)
    async def unhandled_exception_handler(request: Request, exc: Exception) -> JSONResponse:
        logger.exception(f"Unhandled Exception on [{request.url.path}]: {exc}")
        internal_exc = APIError(
            message="An unexpected kernel error occurred while processing the request.",
            http_status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            error_code=APIErrorCode.INTERNAL_KERNEL_ERROR,
        )
        return internal_exc.to_response(include_trace=debug)

# ARTIFACT: errors.py
# VERSION: v1.0.15-STRUCTURE-COMPLIANCE
# AUTHORITY BOUNDARY: API error taxonomy and HTTP translation only.
# TENANT POSTURE: No tenant authority or inference.
# FAIL-CLOSED POSTURE: Unexpected failures collapse to bounded HTTP 500.
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS remains exclusive.
# END OF WILSY OS SOVEREIGN ARTIFACT
