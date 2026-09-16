"""WILSY OS provider-neutral model execution contract.

TITLE: WILSY AI Model Execution and Invocation Evidence
VERSION: v1.0.0-WILSY-AI-MODEL-EXECUTION
AUTHORITY: Wilsy OS Core Governance
EPITOME: Defines a provider-independent transient execution request/result and
         immutable, tenant-scoped model-invocation evidence for later runtime
         composition. Provider and model names are operational metadata only.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tools/eos/intelligence/domain/ai_model_execution.py
COLLABORATION / OWNERSHIP: Future orchestrators provide server-bound identity;
                            injected providers compute transient results; the
                            dedicated C1A registry persists bounded evidence.
CERTIFICATION / UPDATE DATE: 2026-09-16
CHANGELOG: v1.0.0 establishes the provider-neutral execution vocabulary,
           deterministic SHA3-512 request/response/evidence fingerprints, and
           a durable payload that excludes prompts, reasoning, secrets, and
           raw provider failures.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2.
SECURITY / PRIVACY POSTURE: Raw prompts and provider responses remain
                             transient; durable evidence contains fingerprints
                             and bounded metadata only.
TENANT BOUNDARY: Tenant and principal identities are server-bound input and
                 are never accepted from provider output.
AUTHORITY BOUNDARY: Model-compute evidence only; no IAM, entitlement,
                    legal, billing, payment, execution, or settlement truth.
FINANCIAL AUTHORITY BOUNDARY: Kennel EOS exclusively owns financial execution
                              and settlement.
FAIL-CLOSED DECLARATION: Invalid identity, metadata, timestamps, fingerprints,
                         outcome, or payload shape raises a stable C1A error.
"""
from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from enum import Enum
import hashlib
import hmac
import json
import re
from typing import Any, Final, NoReturn, Protocol, cast


VERSION: Final[str] = "v1.0.0-WILSY-AI-MODEL-EXECUTION"
SCHEMA: Final[str] = "WILSY-AI-MODEL-EXECUTION/V1"
MODEL_EXECUTION_MODULE_ID: Final[str] = "WILSY_AI_REASONING"
MODEL_EXECUTION_CAPABILITY: Final[str] = "wilsy_ai.reasoning.execute.v1"
_ENTITY_TYPE: Final[str] = "ModelInvocationEvidence"
_IDENTITY = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._:-]{0,127}$")
_SHA3 = re.compile(r"^[0-9a-f]{128}$")
_FORBIDDEN_TENANTS = frozenset({"default", "global", "global_root", "root", "master", "*"})
_ERROR_CLASSES = frozenset(
    {
        "PROVIDER_UNAVAILABLE",
        "PROVIDER_TIMEOUT",
        "PROVIDER_REJECTED_REQUEST",
        "PROVIDER_MALFORMED_RESPONSE",
        "INTERNAL_CONTRACT_VIOLATION",
    }
)


class ModelExecutionError(ValueError):
    """Stable fail-closed error for the pure C1A model contract."""

    def __init__(self, code: str) -> None:
        """Create an error without retaining provider exception material."""
        self.code = code
        super().__init__(code)


class ModelExecutionOutcome(str, Enum):
    """Bounded provider outcome vocabulary."""

    SUCCESS = "SUCCESS"
    PROVIDER_UNAVAILABLE = "PROVIDER_UNAVAILABLE"
    PROVIDER_TIMEOUT = "PROVIDER_TIMEOUT"
    PROVIDER_REJECTED_REQUEST = "PROVIDER_REJECTED_REQUEST"
    PROVIDER_MALFORMED_RESPONSE = "PROVIDER_MALFORMED_RESPONSE"
    INTERNAL_CONTRACT_VIOLATION = "INTERNAL_CONTRACT_VIOLATION"


def _fail(code: str) -> NoReturn:
    """Raise a stable C1A validation error."""
    raise ModelExecutionError(code)


def _identity(name: str, value: object) -> str:
    """Require one non-empty canonical opaque identity."""
    if not isinstance(value, str) or _IDENTITY.fullmatch(value) is None:
        _fail(f"C1A_{name.upper()}_INVALID")
    return cast(str, value)


def _tenant(value: object) -> str:
    """Require an explicit non-pseudo tenant identity."""
    tenant = _identity("tenant_id", value)
    if tenant.casefold() in _FORBIDDEN_TENANTS:
        _fail("C1A_TENANT_INVALID")
    return tenant


def _text(name: str, value: object, *, allow_empty: bool = False) -> str:
    """Validate transient or bounded textual content without persistence."""
    if not isinstance(value, str) or value != value.strip() or (not allow_empty and not value):
        _fail(f"C1A_{name.upper()}_INVALID")
    if any(ord(character) < 32 and character not in "\n\t" for character in value):
        _fail(f"C1A_{name.upper()}_INVALID")
    return value


def _digest(name: str, value: object) -> str:
    """Require an exact lowercase SHA3-512 digest."""
    if not isinstance(value, str) or _SHA3.fullmatch(value) is None:
        _fail(f"C1A_{name.upper()}_INVALID")
    return value


def _when(name: str, value: object) -> datetime:
    """Require an aware UTC timestamp and normalize its representation."""
    if not isinstance(value, datetime) or value.tzinfo is None or value.utcoffset() != timedelta(0):
        _fail(f"C1A_{name.upper()}_INVALID")
    return value.astimezone(timezone.utc)


def _nonnegative(name: str, value: object, *, positive: bool = False) -> int:
    """Validate usage quantities without accepting booleans."""
    if isinstance(value, bool) or not isinstance(value, int) or value < 0 or (positive and value <= 0):
        _fail(f"C1A_{name.upper()}_INVALID")
    return value


def _json_value(value: object) -> object:
    """Convert supported values to deterministic JSON primitives."""
    if isinstance(value, datetime):
        return value.astimezone(timezone.utc).isoformat().replace("+00:00", "Z")
    if isinstance(value, Enum):
        return value.value
    if isinstance(value, tuple):
        return [_json_value(item) for item in value]
    if isinstance(value, list):
        return [_json_value(item) for item in value]
    if isinstance(value, Mapping):
        return {str(key): _json_value(item) for key, item in value.items()}
    return value


def canonical_json(value: object) -> str:
    """Return the repository's deterministic, non-ambiguous JSON encoding."""
    try:
        return json.dumps(
            _json_value(value),
            ensure_ascii=False,
            allow_nan=False,
            sort_keys=True,
            separators=(",", ":"),
        )
    except (TypeError, ValueError) as error:
        raise ModelExecutionError("C1A_CANONICAL_SERIALIZATION_INVALID") from error


def sha3_512_fingerprint(value: object) -> str:
    """Return a lowercase SHA3-512 digest over deterministic canonical JSON."""
    return hashlib.sha3_512(canonical_json(value).encode("utf-8")).hexdigest()


def sanitize_provider_error(error: BaseException) -> ModelExecutionOutcome:
    """Map common failure shapes to bounded outcomes without retaining details."""
    if isinstance(error, TimeoutError):
        return ModelExecutionOutcome.PROVIDER_TIMEOUT
    if isinstance(error, (ConnectionError, OSError)):
        return ModelExecutionOutcome.PROVIDER_UNAVAILABLE
    if isinstance(error, (ValueError, TypeError, KeyError)):
        return ModelExecutionOutcome.PROVIDER_MALFORMED_RESPONSE
    return ModelExecutionOutcome.INTERNAL_CONTRACT_VIOLATION


@dataclass(frozen=True, slots=True)
class ModelExecutionInput:
    """Transient server-bound request consumed by an injected model provider.

    Prompt and policy text are intentionally transient fields. They are used
    to derive ``request_fingerprint`` but are never members of durable
    ``ModelInvocationEvidence``.
    """

    tenant_id: str
    principal_id: str
    invocation_id: str
    correlation_id: str
    entitlement_id: str
    provider_id: str
    model_id: str
    prompt: str
    system_policy: str
    request_units: int = 1
    tool_invocation_evidence_references: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        """Validate all server-bound identity and transient request fields."""
        _tenant(self.tenant_id)
        for name in (
            "principal_id",
            "invocation_id",
            "correlation_id",
            "entitlement_id",
            "provider_id",
            "model_id",
        ):
            _identity(name, getattr(self, name))
        _text("prompt", self.prompt)
        _text("system_policy", self.system_policy)
        _nonnegative("request_units", self.request_units, positive=True)
        if not isinstance(self.tool_invocation_evidence_references, tuple):
            _fail("C1A_TOOL_REFERENCES_INVALID")
        for reference in self.tool_invocation_evidence_references:
            _identity("tool_invocation_evidence_reference", reference)

    @property
    def request_fingerprint(self) -> str:
        """Fingerprint safe request identity/material without persisting raw text."""
        return sha3_512_fingerprint(
            {
                "tenant_id": self.tenant_id,
                "principal_id": self.principal_id,
                "invocation_id": self.invocation_id,
                "correlation_id": self.correlation_id,
                "entitlement_id": self.entitlement_id,
                "provider_id": self.provider_id,
                "model_id": self.model_id,
                "prompt": self.prompt,
                "system_policy": self.system_policy,
                "request_units": self.request_units,
                "tool_invocation_evidence_references": self.tool_invocation_evidence_references,
            }
        )


@dataclass(frozen=True, slots=True)
class ModelProviderResult:
    """Transient provider result; it carries no server authority identities."""

    provider_id: str
    model_id: str
    response_text: str = ""
    provider_request_id: str | None = None
    input_tokens: int | None = None
    output_tokens: int | None = None
    outcome: ModelExecutionOutcome = ModelExecutionOutcome.SUCCESS
    error_classification: str | None = None

    def __post_init__(self) -> None:
        """Validate bounded provider metadata and sanitize outcome vocabulary."""
        _identity("provider_id", self.provider_id)
        _identity("model_id", self.model_id)
        if self.provider_request_id is not None:
            _identity("provider_request_id", self.provider_request_id)
        if self.input_tokens is not None:
            _nonnegative("input_tokens", self.input_tokens)
        if self.output_tokens is not None:
            _nonnegative("output_tokens", self.output_tokens)
        if not isinstance(self.outcome, ModelExecutionOutcome):
            try:
                object.__setattr__(self, "outcome", ModelExecutionOutcome(str(self.outcome)))
            except ValueError as error:
                raise ModelExecutionError("C1A_OUTCOME_INVALID") from error
        if self.outcome is ModelExecutionOutcome.SUCCESS:
            _text("response_text", self.response_text)
            if self.error_classification is not None:
                _fail("C1A_SUCCESS_ERROR_INVALID")
        else:
            if self.response_text:
                _fail("C1A_FAILURE_RESPONSE_INVALID")
            if self.error_classification not in _ERROR_CLASSES or self.error_classification != self.outcome.value:
                _fail("C1A_ERROR_CLASSIFICATION_INVALID")

    @property
    def response_fingerprint(self) -> str:
        """Fingerprint provider result material without storing response text."""
        return sha3_512_fingerprint(
            {
                "provider_id": self.provider_id,
                "model_id": self.model_id,
                "provider_request_id": self.provider_request_id,
                "response_text": self.response_text,
                "input_tokens": self.input_tokens,
                "output_tokens": self.output_tokens,
                "outcome": self.outcome.value,
                "error_classification": self.error_classification,
            }
        )


class ModelProvider(Protocol):
    """Dependency-injection protocol with no provider SDK coupling."""

    def execute(self, request: ModelExecutionInput) -> ModelProviderResult:
        """Compute a transient provider result for one canonical request."""
        ...


_EVIDENCE_FIELDS: Final[tuple[str, ...]] = (
    "schema",
    "version",
    "entity_type",
    "tenant_id",
    "principal_id",
    "invocation_id",
    "correlation_id",
    "entitlement_id",
    "provider_id",
    "model_id",
    "provider_request_id",
    "request_fingerprint",
    "response_fingerprint",
    "request_units",
    "input_tokens",
    "output_tokens",
    "outcome",
    "error_classification",
    "created_at",
    "completed_at",
    "tool_invocation_evidence_references",
    "fingerprint",
)


@dataclass(frozen=True, slots=True)
class ModelInvocationEvidence:
    """Immutable bounded model-compute evidence, not legal or financial truth."""

    tenant_id: str
    principal_id: str
    invocation_id: str
    correlation_id: str
    entitlement_id: str
    provider_id: str
    model_id: str
    provider_request_id: str | None
    request_fingerprint: str
    response_fingerprint: str
    request_units: int
    input_tokens: int | None
    output_tokens: int | None
    outcome: ModelExecutionOutcome
    error_classification: str | None
    created_at: datetime
    completed_at: datetime
    tool_invocation_evidence_references: tuple[str, ...] = ()
    schema: str = SCHEMA
    version: str = VERSION
    entity_type: str = _ENTITY_TYPE
    fingerprint: str = field(default="", repr=False, compare=False)

    def __post_init__(self) -> None:
        """Reject malformed, forged, or authority-expanding evidence."""
        _tenant(self.tenant_id)
        for name in (
            "principal_id",
            "invocation_id",
            "correlation_id",
            "entitlement_id",
            "provider_id",
            "model_id",
        ):
            _identity(name, getattr(self, name))
        if self.provider_request_id is not None:
            _identity("provider_request_id", self.provider_request_id)
        _digest("request_fingerprint", self.request_fingerprint)
        _digest("response_fingerprint", self.response_fingerprint)
        _nonnegative("request_units", self.request_units, positive=True)
        if self.input_tokens is not None:
            _nonnegative("input_tokens", self.input_tokens)
        if self.output_tokens is not None:
            _nonnegative("output_tokens", self.output_tokens)
        if not isinstance(self.outcome, ModelExecutionOutcome):
            try:
                object.__setattr__(self, "outcome", ModelExecutionOutcome(str(self.outcome)))
            except ValueError as error:
                raise ModelExecutionError("C1A_OUTCOME_INVALID") from error
        if self.outcome is ModelExecutionOutcome.SUCCESS:
            if self.error_classification is not None:
                _fail("C1A_SUCCESS_ERROR_INVALID")
        elif self.error_classification != self.outcome.value:
            _fail("C1A_ERROR_CLASSIFICATION_INVALID")
        if not isinstance(self.tool_invocation_evidence_references, tuple):
            _fail("C1A_TOOL_REFERENCES_INVALID")
        for reference in self.tool_invocation_evidence_references:
            _identity("tool_invocation_evidence_reference", reference)
        if self.schema != SCHEMA or self.version != VERSION or self.entity_type != _ENTITY_TYPE:
            _fail("C1A_EVIDENCE_IDENTITY_INVALID")
        created = _when("created_at", self.created_at)
        completed = _when("completed_at", self.completed_at)
        if completed < created:
            _fail("C1A_EVIDENCE_CHRONOLOGY_INVALID")
        object.__setattr__(self, "created_at", created)
        object.__setattr__(self, "completed_at", completed)
        payload = self._payload()
        digest = sha3_512_fingerprint(payload)
        if self.fingerprint and (not _SHA3.fullmatch(self.fingerprint) or not hmac.compare_digest(self.fingerprint, digest)):
            _fail("C1A_EVIDENCE_FINGERPRINT_MISMATCH")
        object.__setattr__(self, "fingerprint", digest)

    def _payload(self) -> dict[str, object]:
        """Return the complete durable payload excluding its self-fingerprint."""
        return {
            "schema": self.schema,
            "version": self.version,
            "entity_type": self.entity_type,
            "tenant_id": self.tenant_id,
            "principal_id": self.principal_id,
            "invocation_id": self.invocation_id,
            "correlation_id": self.correlation_id,
            "entitlement_id": self.entitlement_id,
            "provider_id": self.provider_id,
            "model_id": self.model_id,
            "provider_request_id": self.provider_request_id,
            "request_fingerprint": self.request_fingerprint,
            "response_fingerprint": self.response_fingerprint,
            "request_units": self.request_units,
            "input_tokens": self.input_tokens,
            "output_tokens": self.output_tokens,
            "outcome": self.outcome,
            "error_classification": self.error_classification,
            "created_at": self.created_at,
            "completed_at": self.completed_at,
            "tool_invocation_evidence_references": self.tool_invocation_evidence_references,
        }

    def to_dict(self) -> dict[str, object]:
        """Serialize exact bounded evidence; no prompt, response, secret, or CoT."""
        payload = self._payload()
        payload["fingerprint"] = self.fingerprint
        return {field_name: _json_value(payload[field_name]) for field_name in _EVIDENCE_FIELDS}

    @classmethod
    def from_execution(
        cls,
        request: ModelExecutionInput,
        result: ModelProviderResult,
        *,
        created_at: datetime,
        completed_at: datetime,
    ) -> "ModelInvocationEvidence":
        """Compose evidence from server-bound input and transient provider result."""
        if not isinstance(request, ModelExecutionInput) or not isinstance(result, ModelProviderResult):
            _fail("C1A_EXECUTION_TYPES_INVALID")
        if request.provider_id != result.provider_id or request.model_id != result.model_id:
            _fail("C1A_PROVIDER_METADATA_MISMATCH")
        return cls(
            tenant_id=request.tenant_id,
            principal_id=request.principal_id,
            invocation_id=request.invocation_id,
            correlation_id=request.correlation_id,
            entitlement_id=request.entitlement_id,
            provider_id=result.provider_id,
            model_id=result.model_id,
            provider_request_id=result.provider_request_id,
            request_fingerprint=request.request_fingerprint,
            response_fingerprint=result.response_fingerprint,
            request_units=request.request_units,
            input_tokens=result.input_tokens,
            output_tokens=result.output_tokens,
            outcome=result.outcome,
            error_classification=result.error_classification,
            created_at=created_at,
            completed_at=completed_at,
            tool_invocation_evidence_references=request.tool_invocation_evidence_references,
        )

    @classmethod
    def from_dict(cls, payload: Mapping[str, object]) -> "ModelInvocationEvidence":
        """Hydrate exactly the canonical fields and verify the evidence digest."""
        if not isinstance(payload, Mapping) or set(payload) != set(_EVIDENCE_FIELDS):
            _fail("C1A_EVIDENCE_SCHEMA_INVALID")
        values = dict(payload)
        stored = values.pop("fingerprint")
        for field_name in ("created_at", "completed_at"):
            timestamp = values.get(field_name)
            if isinstance(timestamp, str):
                try:
                    values[field_name] = datetime.fromisoformat(timestamp.replace("Z", "+00:00"))
                except ValueError as error:
                    raise ModelExecutionError("C1A_TIMESTAMP_INVALID") from error
        references = values.get("tool_invocation_evidence_references")
        if isinstance(references, list):
            values["tool_invocation_evidence_references"] = tuple(references)
        try:
            evidence = cls(**cast(Any, values))
        except TypeError as error:
            raise ModelExecutionError("C1A_EVIDENCE_SCHEMA_INVALID") from error
        if not isinstance(stored, str) or not hmac.compare_digest(stored, evidence.fingerprint):
            _fail("C1A_EVIDENCE_FINGERPRINT_MISMATCH")
        return evidence


__all__ = [
    "VERSION",
    "SCHEMA",
    "MODEL_EXECUTION_MODULE_ID",
    "MODEL_EXECUTION_CAPABILITY",
    "ModelExecutionError",
    "ModelExecutionOutcome",
    "ModelExecutionInput",
    "ModelProviderResult",
    "ModelProvider",
    "ModelInvocationEvidence",
    "canonical_json",
    "sha3_512_fingerprint",
    "sanitize_provider_error",
]

# ARTIFACT: ai_model_execution.py
# VERSION: v1.0.0-WILSY-AI-MODEL-EXECUTION
# AUTHORITY BOUNDARY: provider-neutral model-compute evidence only
# TENANT POSTURE: server-bound tenant identity; no provider override
# FAIL-CLOSED POSTURE: strict fields, fingerprints, chronology, and outcomes
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively
# END OF WILSY OS SOVEREIGN ARTIFACT
