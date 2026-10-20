"""TITLE: WILSY OS Immutable Practitioner Matter Access Evidence Contract.
VERSION: v2.0.0-P47-R33-PRACTITIONER-ACCESS-DOMAIN-SEPARATION
AUTHORITY: Python EOS Legal Operations immutable documentary state only.
EPITOME: Defines the exact frozen practitioner/matter access evidence shape
    while delegating construction, validation, hashing, serialization and
    hydration to the service-owned codec required by LAW EK-006.
ABSOLUTE CANONICAL PATH:
    /Users/wilsonkhanyezi/legal-doc-system/tools/eos/legal_operations/domain/legal_practitioner_matter_access.py
COLLABORATION / OWNERSHIP: Wilsy OS Core Engineering; the practitioner-access
    codec is the exclusive supported construction and integrity boundary.
CERTIFICATION / UPDATE DATE: 2026-10-20
CHANGELOG:
    2026-10-20 v2.0.0-P47-R33-PRACTITIONER-ACCESS-DOMAIN-SEPARATION
    Remove parsing, normalization, serialization and cryptographic behavior
    from the immutable domain while preserving the frozen V1 evidence schema.
    2026-10-19 v1.0.1-P9-R85R1-PRACTITIONER-MATTER-ACCESS-HYDRATION
    Established strict persisted SHA3-512 integrity and immutable evidence.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2 technical controls.
SECURITY / PRIVACY POSTURE: Contains identifiers and documentary policy state
    only; no logs, persistence, transport, parsing or caller-supplied trust.
TENANT BOUNDARY: Exact tenant, matter and practitioner identity; no defaults.
AUTHORITY BOUNDARY: ALLOW/DENY is documentary evidence, not proof of issuer
    authority, affirmative access, ethical-wall clearance, IAM or approval.
FINANCIAL AUTHORITY BOUNDARY: None; Kennel EOS exclusively.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from enum import StrEnum
from typing import Final


MODULE_VERSION: Final[str] = (
    "v2.0.0-P47-R33-PRACTITIONER-ACCESS-DOMAIN-SEPARATION"
)
EVIDENCE_VERSION: Final[str] = (
    "v1.0.1-P9-R85R1-PRACTITIONER-MATTER-ACCESS-HYDRATION"
)
# Compatibility name is persisted in existing evidence and cannot be changed.
VERSION: Final[str] = EVIDENCE_VERSION
SCHEMA: Final[str] = "WILSY-LEGAL-PRACTITIONER-MATTER-ACCESS-EVIDENCE/V1"


class LegalPractitionerMatterAccessError(ValueError):
    """Expose a bounded codec/factory failure without sensitive identifiers.

    This exception defines the stable public failure contract only. It grants
    no tenant, policy, issuance, access, reassignment or financial authority.
    """

    def __init__(self, code: str) -> None:
        """Record one stable error code without copying rejected payloads."""
        self.code = code
        super().__init__(code)


class LegalPractitionerMatterAccessDecision(StrEnum):
    """Identify documentary ALLOW or DENY evidence, never runtime permission."""

    ALLOW = "ALLOW"
    DENY = "DENY"


@dataclass(frozen=True, slots=True, kw_only=True, init=False)
class LegalPractitionerMatterAccessEvidence:
    """Hold codec-verified immutable practitioner/matter documentary evidence.

    Construction is intentionally unavailable in the domain. The service-owned
    codec validates every field, calculates or verifies SHA3-512 over the exact
    frozen material, and only then materializes this frozen value. Persistence,
    transaction, idempotency and authorization semantics are not domain powers.
    """

    access_evidence_id: str
    tenant_id: str
    case_matter_id: str
    practitioner_principal_id: str
    revision: int
    decision: LegalPractitionerMatterAccessDecision
    effective_from: datetime
    effective_until: datetime | None
    issued_by_principal_id: str
    source_evidence_fingerprint: str
    supersedes_fingerprint: str | None
    schema: str
    evidence_version: str
    fingerprint: str


__all__ = [
    "MODULE_VERSION",
    "EVIDENCE_VERSION",
    "VERSION",
    "SCHEMA",
    "LegalPractitionerMatterAccessError",
    "LegalPractitionerMatterAccessDecision",
    "LegalPractitionerMatterAccessEvidence",
]


# WILSY OS SOVEREIGN ARTIFACT SEAL
# ARTIFACT: legal_practitioner_matter_access.py
# VERSION: v2.0.0-P47-R33-PRACTITIONER-ACCESS-DOMAIN-SEPARATION
# AUTHORITY BOUNDARY: IMMUTABLE DOCUMENTARY STATE CONTRACT ONLY
# TENANT POSTURE: EXACT CODEC-VERIFIED IDENTITY; NO DEFAULT OR INFERENCE
# FAIL-CLOSED POSTURE: NO PUBLIC DOMAIN CONSTRUCTION OR OPERATIONAL BEHAVIOR
# AFFIRMATIVE ACCESS / ISSUANCE / ETHICAL-WALL / IAM AUTHORITY: NONE
# REASSIGNMENT / PERSISTENCE / FINANCIAL EXECUTION AUTHORITY: NONE
# END OF WILSY OS SOVEREIGN ARTIFACT
