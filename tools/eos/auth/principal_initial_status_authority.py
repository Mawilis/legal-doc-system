"""WILSY OS deployment-rooted principal initial-status authority.

TITLE: Principal Initial Status Authority
VERSION: v1.0.0-R1D-B0F-B4-R6A
AUTHORITY: Exact deployment decision for one initial PrincipalAuthority row.
EPITOME: Converts an explicit, deployment-controlled subject/status binding
         into immutable evidence without granting authentication or role power.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tools/eos/auth/principal_initial_status_authority.py
COLLABORATION / OWNERSHIP: Deployment configuration owns the decision; the
                           principal provisioning and migration seams consume evidence.
CERTIFICATION / UPDATE DATE: 2026-09-17
CHANGELOG: v1.0.0-R1D-B0F-B4-R6A establishes exact subject/status parsing,
           wildcard and duplicate rejection, and immutable fail-closed evidence.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2.
SECURITY / PRIVACY POSTURE: Configuration contents never enter exception text or logs.
TENANT BOUNDARY: No tenant, role, credential, or membership authority is represented.
AUTHORITY BOUNDARY: Initial PrincipalAuthority status only; no future transition authority.
FINANCIAL AUTHORITY BOUNDARY: None; Kennel EOS remains exclusive.
FAIL-CLOSED POSTURE: Missing, malformed, wildcard, duplicate, and mismatched decisions deny.
"""
from __future__ import annotations

import json
import os
from dataclasses import dataclass
from enum import StrEnum
from typing import Mapping

from tools.eos.auth.principal_status import PrincipalStatus


VERSION = "v1.0.0-R1D-B0F-B4-R6A"
PRINCIPAL_INITIAL_STATUS_AUTHORITY_CONFIG = "WILSY_PRINCIPAL_INITIAL_STATUS_AUTHORITY"
PRINCIPAL_INITIAL_STATUS_OPERATION = "principal_initial_activation"
AUTHORITY_SOURCE_ID = "deployment_principal_initial_status_config"


class PrincipalInitialStatusAuthorityDenialCode(StrEnum):
    """Stable, non-sensitive refusal codes for authority verification."""

    PRINCIPAL_ID_REQUIRED = "PRINCIPAL_ID_REQUIRED"
    TARGET_STATUS_REQUIRED = "TARGET_STATUS_REQUIRED"
    MISSING_AUTHORITY = "PRINCIPAL_INITIAL_STATUS_AUTHORITY_MISSING"
    MALFORMED_AUTHORITY = "PRINCIPAL_INITIAL_STATUS_AUTHORITY_MALFORMED"
    WILDCARD_NOT_ALLOWED = "PRINCIPAL_INITIAL_STATUS_AUTHORITY_WILDCARD"
    DUPLICATE_DECISION = "PRINCIPAL_INITIAL_STATUS_AUTHORITY_DUPLICATE"
    SUBJECT_NOT_AUTHORIZED = "PRINCIPAL_INITIAL_STATUS_AUTHORITY_SUBJECT_MISMATCH"
    STATUS_NOT_AUTHORIZED = "PRINCIPAL_INITIAL_STATUS_AUTHORITY_STATUS_MISMATCH"


class PrincipalInitialStatusAuthorityError(RuntimeError):
    """Fail-closed verification error; never contains configuration values."""

    def __init__(self, code: PrincipalInitialStatusAuthorityDenialCode) -> None:
        self.code = code
        super().__init__(code.value)


@dataclass(frozen=True, slots=True)
class PrincipalInitialStatusAuthorityEvidence:
    """Immutable evidence for one exact initial principal-status decision."""

    subject_principal_id: str
    target_status: PrincipalStatus
    operation: str
    authority_source: str

    def __post_init__(self) -> None:
        if not isinstance(self.subject_principal_id, str) or not self.subject_principal_id.strip():
            raise ValueError("subject_principal_id must be non-empty")
        if self.subject_principal_id != self.subject_principal_id.strip():
            raise ValueError("subject_principal_id must be trimmed")
        if self.subject_principal_id == "*":
            raise ValueError("wildcard subject is not allowed")
        if not isinstance(self.target_status, PrincipalStatus):
            raise TypeError("target_status must be PrincipalStatus")
        if self.operation != PRINCIPAL_INITIAL_STATUS_OPERATION:
            raise ValueError("operation is outside initial-status authority")
        if self.authority_source != AUTHORITY_SOURCE_ID:
            raise ValueError("authority_source is outside deployment authority")

    @property
    def principal_id(self) -> str:
        """Compatibility alias for the exact subject identity."""
        return self.subject_principal_id

    @property
    def initial_status(self) -> PrincipalStatus:
        """Compatibility alias for the explicitly bound target status."""
        return self.target_status


def _decision_rows(raw: str) -> list[Mapping[str, object]]:
    try:
        parsed = json.loads(raw)
    except (TypeError, ValueError, json.JSONDecodeError) as error:
        raise PrincipalInitialStatusAuthorityError(
            PrincipalInitialStatusAuthorityDenialCode.MALFORMED_AUTHORITY
        ) from error
    if isinstance(parsed, Mapping):
        parsed = [parsed]
    if not isinstance(parsed, list) or not parsed:
        raise PrincipalInitialStatusAuthorityError(
            PrincipalInitialStatusAuthorityDenialCode.MALFORMED_AUTHORITY
        )
    rows: list[Mapping[str, object]] = []
    seen: set[str] = set()
    for row in parsed:
        if not isinstance(row, Mapping):
            raise PrincipalInitialStatusAuthorityError(
                PrincipalInitialStatusAuthorityDenialCode.MALFORMED_AUTHORITY
            )
        subject = row.get("principal_id", row.get("subject_principal_id"))
        status = row.get("initial_status", row.get("target_status"))
        if not isinstance(subject, str) or not subject.strip() or subject != subject.strip():
            raise PrincipalInitialStatusAuthorityError(
                PrincipalInitialStatusAuthorityDenialCode.MALFORMED_AUTHORITY
            )
        if subject == "*":
            raise PrincipalInitialStatusAuthorityError(
                PrincipalInitialStatusAuthorityDenialCode.WILDCARD_NOT_ALLOWED
            )
        if subject in seen:
            raise PrincipalInitialStatusAuthorityError(
                PrincipalInitialStatusAuthorityDenialCode.DUPLICATE_DECISION
            )
        if not isinstance(status, str) or status not in {item.value for item in PrincipalStatus}:
            raise PrincipalInitialStatusAuthorityError(
                PrincipalInitialStatusAuthorityDenialCode.MALFORMED_AUTHORITY
            )
        seen.add(subject)
        rows.append({"principal_id": subject, "initial_status": status})
    return rows


def verify_principal_initial_status_authority(
    *,
    principal_id: str,
    target_status: PrincipalStatus,
    environ: Mapping[str, str] | None = None,
) -> PrincipalInitialStatusAuthorityEvidence:
    """Verify deployment configuration for one exact initial status decision.

    The returned evidence is immutable but construction alone grants nothing;
    provisioning must still validate and persist it through its own boundary.
    """
    if not isinstance(principal_id, str) or not principal_id.strip():
        raise PrincipalInitialStatusAuthorityError(
            PrincipalInitialStatusAuthorityDenialCode.PRINCIPAL_ID_REQUIRED
        )
    if principal_id != principal_id.strip() or principal_id == "*":
        raise PrincipalInitialStatusAuthorityError(
            PrincipalInitialStatusAuthorityDenialCode.WILDCARD_NOT_ALLOWED
        )
    if not isinstance(target_status, PrincipalStatus):
        raise PrincipalInitialStatusAuthorityError(
            PrincipalInitialStatusAuthorityDenialCode.TARGET_STATUS_REQUIRED
        )
    source = os.environ if environ is None else environ
    raw = source.get(PRINCIPAL_INITIAL_STATUS_AUTHORITY_CONFIG)
    if raw is None or not raw.strip():
        raise PrincipalInitialStatusAuthorityError(
            PrincipalInitialStatusAuthorityDenialCode.MISSING_AUTHORITY
        )
    rows = _decision_rows(raw)
    matching = [row for row in rows if row["principal_id"] == principal_id]
    if not matching:
        raise PrincipalInitialStatusAuthorityError(
            PrincipalInitialStatusAuthorityDenialCode.SUBJECT_NOT_AUTHORIZED
        )
    if matching[0]["initial_status"] != target_status.value:
        raise PrincipalInitialStatusAuthorityError(
            PrincipalInitialStatusAuthorityDenialCode.STATUS_NOT_AUTHORIZED
        )
    return PrincipalInitialStatusAuthorityEvidence(
        subject_principal_id=principal_id,
        target_status=target_status,
        operation=PRINCIPAL_INITIAL_STATUS_OPERATION,
        authority_source=AUTHORITY_SOURCE_ID,
    )


verify_principal_activation_authority = verify_principal_initial_status_authority

__all__ = [
    "AUTHORITY_SOURCE_ID",
    "PRINCIPAL_INITIAL_STATUS_AUTHORITY_CONFIG",
    "PRINCIPAL_INITIAL_STATUS_OPERATION",
    "PrincipalInitialStatusAuthorityDenialCode",
    "PrincipalInitialStatusAuthorityError",
    "PrincipalInitialStatusAuthorityEvidence",
    "VERSION",
    "verify_principal_activation_authority",
    "verify_principal_initial_status_authority",
]

# ARTIFACT: principal_initial_status_authority.py
# VERSION: v1.0.0-R1D-B0F-B4-R6A
# AUTHORITY BOUNDARY: one explicit initial PrincipalAuthority status decision
# TENANT POSTURE: tenant-neutral; roles and membership remain separate
# FAIL-CLOSED POSTURE: no wildcard, role/status inference, duplicate, or implicit ACTIVE
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS remains exclusive
# END OF WILSY OS SOVEREIGN ARTIFACT
