"""TITLE: Kennel Financial Execution Truth and Subject-Neutral Fact Domain
VERSION: v2.0.0-M11-P5-R2D-R1
AUTHORITY: Wilsy OS Core Governance / Kennel EOS
EPITOME: Preserve AP execution truth while adding an immutable subject-neutral execution fact.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tools/eos/kennel/domain/financial_execution.py
COLLABORATION / OWNERSHIP: Kennel EOS execution-evidence domain owner.
CERTIFICATION / UPDATE DATE: 2026-09-08.
CHANGELOG: v2.0.0-M11-P5-R2D-R1 preserves historical AP truth and adds strict command/attempt-linked subject-neutral execution facts.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2.
SECURITY / PRIVACY POSTURE: Opaque tenant/provider references only; no credentials or raw payment data.
TENANT BOUNDARY: Every AP truth and neutral fact identity is tenant-scoped and immutable.
AUTHORITY BOUNDARY: Durable generic commands and authenticated provider evidence only; no caller-invented truth.
FINANCIAL AUTHORITY BOUNDARY: Execution evidence never implies settlement, paid state, or receivable closure.
TRANSACTION BOUNDARY: Pure immutable value objects; persistence and transaction lifecycle belong to registries/callers.
FAIL-CLOSED DECLARATION: Unknown, missing, malformed, subject-mixed, and fingerprint-divergent material rejects.
"""
from __future__ import annotations

import hashlib
import json
import re
from dataclasses import dataclass
from datetime import datetime
from enum import StrEnum
from typing import Any, Mapping

VERSION = "v2.0.0-M11-P5-R2D-R1"
_HEX = re.compile(r"^[0-9a-f]{128}$")


class FinancialExecutionTruthError(ValueError):
    """Fail-closed validation error for historical AP execution truth."""


class FinancialExecutionFactError(ValueError):
    """Fail-closed validation error for subject-neutral execution facts."""


class FinancialExecutionStatus(StrEnum):
    """Provider execution status; no member represents settlement or payment."""

    SUBMITTED = "SUBMITTED"
    ACCEPTED = "ACCEPTED"
    EXECUTED = "EXECUTED"
    FAILED = "FAILED"


def _canonical_digest(payload: Mapping[str, object]) -> str:
    """Hash deterministic canonical JSON with the institutional SHA3-512 convention."""
    encoded = json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode("utf-8")
    return hashlib.sha3_512(encoded).hexdigest()


@dataclass(frozen=True)
class FinancialExecutionTruth:
    """Historical immutable AP execution evidence; this type remains AP-shaped."""

    execution_truth_id: str
    tenant_id: str
    payable_id: str
    release_authorization_id: str
    provider: str
    provider_execution_reference: str
    execution_status: FinancialExecutionStatus
    executed_amount_minor: int
    currency: str
    executed_at: datetime | None
    payment_destination_reference: str
    provider_evidence_reference: str
    execution_command_fingerprint: str
    execution_evidence_fingerprint: str
    created_at: datetime

    def __post_init__(self) -> None:
        """Validate the frozen AP contract without adding family inference."""
        for name in (
            "execution_truth_id", "tenant_id", "payable_id", "release_authorization_id",
            "provider", "provider_execution_reference", "payment_destination_reference",
            "provider_evidence_reference",
        ):
            value = getattr(self, name)
            if not isinstance(value, str) or not value.strip():
                raise FinancialExecutionTruthError(f"{name} must be non-empty")
        if not isinstance(self.execution_status, FinancialExecutionStatus):
            raise FinancialExecutionTruthError("execution_status is invalid")
        if not isinstance(self.executed_amount_minor, int) or isinstance(self.executed_amount_minor, bool) or self.executed_amount_minor <= 0:
            raise FinancialExecutionTruthError("executed_amount_minor must be positive")
        if not isinstance(self.currency, str) or re.fullmatch(r"[A-Z]{3}", self.currency) is None:
            raise FinancialExecutionTruthError("currency must be an uppercase 3-letter code")
        if not isinstance(self.created_at, datetime) or self.created_at.tzinfo is None:
            raise FinancialExecutionTruthError("timestamps must be timezone-aware")
        if self.execution_status is FinancialExecutionStatus.EXECUTED and (
            not isinstance(self.executed_at, datetime) or self.executed_at.tzinfo is None
        ):
            raise FinancialExecutionTruthError("EXECUTED requires timezone-aware executed_at")
        if self.execution_status is not FinancialExecutionStatus.EXECUTED and self.executed_at is not None:
            raise FinancialExecutionTruthError("non-EXECUTED outcomes must not carry executed_at")
        if isinstance(self.executed_at, datetime) and self.executed_at > self.created_at:
            raise FinancialExecutionTruthError("executed_at cannot be later than created_at")
        if _HEX.fullmatch(self.execution_command_fingerprint) is None or _HEX.fullmatch(self.execution_evidence_fingerprint) is None:
            raise FinancialExecutionTruthError("fingerprints must be lowercase SHA3-512 hex")

    def evidence_payload(self) -> dict[str, Any]:
        """Return the unchanged AP semantic payload used for its evidence digest."""
        return {
            name: (
                getattr(self, name).value
                if isinstance(getattr(self, name), StrEnum)
                else getattr(self, name).isoformat()
                if isinstance(getattr(self, name), datetime)
                else getattr(self, name)
            )
            for name in (
                "execution_truth_id", "tenant_id", "payable_id", "release_authorization_id",
                "provider", "provider_execution_reference", "execution_status",
                "executed_amount_minor", "currency", "executed_at",
                "payment_destination_reference", "provider_evidence_reference",
                "execution_command_fingerprint", "execution_evidence_fingerprint",
            )
        }

    def to_dict(self) -> dict[str, Any]:
        """Serialize the historical AP contract without settlement fields."""
        return {**self.evidence_payload(), "created_at": self.created_at.isoformat()}

    @property
    def evidence_fingerprint(self) -> str:
        """Compute the deterministic AP evidence digest."""
        return _canonical_digest(self.evidence_payload())

    @classmethod
    def from_mapping(cls, mapping: Mapping[str, Any]) -> "FinancialExecutionTruth":
        """Hydrate only the exact historical AP schema."""
        forbidden = {"bank_account", "bank_account_number", "card_number", "credentials", "paid", "settled", "settlement_id"}
        if forbidden.intersection(mapping):
            raise FinancialExecutionTruthError("forbidden financial fields")
        values = dict(mapping)
        allowed = {field.name for field in __import__("dataclasses").fields(cls)}
        if set(values) != allowed:
            raise FinancialExecutionTruthError("persisted AP truth fields are incomplete or unknown")
        try:
            if "execution_status" in values and not isinstance(values["execution_status"], FinancialExecutionStatus):
                values["execution_status"] = FinancialExecutionStatus(values["execution_status"])
            for field in ("executed_at", "created_at"):
                if isinstance(values.get(field), str):
                    values[field] = datetime.fromisoformat(values[field])
        except (TypeError, ValueError) as error:
            raise FinancialExecutionTruthError("invalid persisted execution mapping") from error
        return cls(**values)


@dataclass(frozen=True, slots=True)
class FinancialExecutionFact:
    """Immutable subject-neutral provider execution fact with explicit command lineage."""

    execution_fact_id: str
    tenant_id: str
    execution_command_id: str
    execution_command_fingerprint: str
    execution_attempt_id: str
    provider: str
    provider_execution_reference: str
    execution_status: FinancialExecutionStatus
    executed_amount_minor: int
    currency: str
    executed_at: datetime | None
    payment_destination_reference: str
    provider_evidence_reference: str
    execution_evidence_fingerprint: str
    created_at: datetime

    @staticmethod
    def deterministic_id(tenant_id: str, execution_attempt_id: str) -> str:
        """Derive a stable fact identity from tenant and attempt only."""
        payload = {"tenant_id": tenant_id, "execution_attempt_id": execution_attempt_id}
        return f"fact-{_canonical_digest(payload)}"

    def __post_init__(self) -> None:
        """Validate neutral identity, lineage, execution evidence, and timestamps."""
        for name in (
            "execution_fact_id", "tenant_id", "execution_command_id", "execution_attempt_id",
            "provider", "provider_execution_reference", "payment_destination_reference",
            "provider_evidence_reference",
        ):
            value = getattr(self, name)
            if not isinstance(value, str) or not value.strip():
                raise FinancialExecutionFactError(f"{name} must be non-empty")
        if self.execution_attempt_id == self.execution_command_id:
            raise FinancialExecutionFactError("attempt and command identities must differ")
        if self.execution_fact_id != self.deterministic_id(self.tenant_id, self.execution_attempt_id):
            raise FinancialExecutionFactError("execution_fact_id is not the deterministic tenant/attempt identity")
        if not isinstance(self.execution_status, FinancialExecutionStatus):
            raise FinancialExecutionFactError("execution_status is invalid")
        if not isinstance(self.executed_amount_minor, int) or isinstance(self.executed_amount_minor, bool) or self.executed_amount_minor <= 0:
            raise FinancialExecutionFactError("executed_amount_minor must be positive")
        if not isinstance(self.currency, str) or re.fullmatch(r"[A-Z]{3}", self.currency) is None:
            raise FinancialExecutionFactError("currency must be an uppercase 3-letter code")
        if not isinstance(self.created_at, datetime) or self.created_at.tzinfo is None:
            raise FinancialExecutionFactError("created_at must be timezone-aware")
        if self.execution_status is FinancialExecutionStatus.EXECUTED and (
            not isinstance(self.executed_at, datetime) or self.executed_at.tzinfo is None
        ):
            raise FinancialExecutionFactError("EXECUTED requires timezone-aware executed_at")
        if self.execution_status is not FinancialExecutionStatus.EXECUTED and self.executed_at is not None:
            raise FinancialExecutionFactError("non-EXECUTED outcomes must not carry executed_at")
        for name in ("execution_command_fingerprint", "execution_evidence_fingerprint"):
            if _HEX.fullmatch(getattr(self, name)) is None:
                raise FinancialExecutionFactError(f"{name} must be lowercase SHA3-512 hex")

    def evidence_payload(self) -> dict[str, Any]:
        """Return every immutable neutral-fact field for canonical fingerprinting."""
        return {
            name: (
                getattr(self, name).value
                if isinstance(getattr(self, name), StrEnum)
                else getattr(self, name).isoformat()
                if isinstance(getattr(self, name), datetime)
                else getattr(self, name)
            )
            for name in (
                "execution_fact_id", "tenant_id", "execution_command_id",
                "execution_command_fingerprint", "execution_attempt_id", "provider",
                "provider_execution_reference", "execution_status", "executed_amount_minor",
                "currency", "executed_at", "payment_destination_reference",
                "provider_evidence_reference", "execution_evidence_fingerprint", "created_at",
            )
        }

    def to_dict(self) -> dict[str, Any]:
        """Serialize the strict subject-neutral schema with no commercial subjects."""
        return self.evidence_payload()

    @property
    def fingerprint(self) -> str:
        """Compute canonical SHA3-512 over the complete immutable fact."""
        return _canonical_digest(self.evidence_payload())

    @classmethod
    def from_mapping(cls, mapping: Mapping[str, Any]) -> "FinancialExecutionFact":
        """Hydrate exactly the neutral schema; unknown and missing fields fail closed."""
        allowed = {
            "execution_fact_id", "tenant_id", "execution_command_id", "execution_command_fingerprint",
            "execution_attempt_id", "provider", "provider_execution_reference", "execution_status",
            "executed_amount_minor", "currency", "executed_at", "payment_destination_reference",
            "provider_evidence_reference", "execution_evidence_fingerprint", "created_at",
        }
        values = dict(mapping)
        if set(values) != allowed:
            raise FinancialExecutionFactError("persisted execution fact fields are incomplete or unknown")
        try:
            if not isinstance(values["execution_status"], FinancialExecutionStatus):
                values["execution_status"] = FinancialExecutionStatus(values["execution_status"])
            for field in ("executed_at", "created_at"):
                if isinstance(values[field], str):
                    values[field] = datetime.fromisoformat(values[field])
        except (TypeError, ValueError) as error:
            raise FinancialExecutionFactError("invalid persisted execution fact mapping") from error
        return cls(**values)


# ARTIFACT: financial_execution.py
# VERSION: v2.0.0-M11-P5-R2D-R1
# AUTHORITY BOUNDARY: AP truth remains AP-only; neutral facts carry execution evidence only.
# TENANT POSTURE: deterministic tenant/attempt identity and strict tenant-scoped fields.
# FAIL-CLOSED POSTURE: unknown, missing, malformed, subject-mixed, and divergent facts reject.
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively; execution is not settlement.
# END OF WILSY OS SOVEREIGN ARTIFACT
