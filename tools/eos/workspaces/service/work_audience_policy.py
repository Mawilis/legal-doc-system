"""TITLE: WILSY OS Source-Owned Work Audience Classification Policy.
VERSION: v1.0.0-EXACT-SOURCE-WORK-AUDIENCE-POLICY
AUTHORITY: WILSY OS Core Governance / AGENTS.md.
EPITOME: Define Operating, Platform Build and Unclassified work without
classifying by task title, module name, user designation or inferred context.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tools/eos/workspaces/service/work_audience_policy.py
COLLABORATION / OWNERSHIP: Project and each independently admitted My Work
source own their work metadata, audited classification and current revisions;
unified_my_work_projection will consume only an independently verified envelope.
CERTIFICATION / UPDATE DATE: 2026-11-23
CHANGELOG: v1.0.0-EXACT-SOURCE-WORK-AUDIENCE-POLICY creates pure
source- and tenant-bound category evidence verification, non-inferred
UNCLASSIFIED default, exact-revision/current evidence enforcement, and
independent critical-gate admission. No work mutation or IAM grant.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2.
SECURITY / PRIVACY POSTURE: No registry reads, logging, secrets or titles;
opaque stable error codes and no disclosure of foreign source objects.
TENANT BOUNDARY: Every verified category proof names the exact tenant,
source module and source record.
AUTHORITY BOUNDARY: An audience label is not visibility or command authority.
Only caller-authenticated, source-admitted records are eligible; this pure
validator does not verify signatures, principal roles or persistence by itself.
FINANCIAL AUTHORITY BOUNDARY: Kennel EOS exclusively.
"""
from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum
from typing import Mapping, Final


VERSION: Final = "v1.0.0-EXACT-SOURCE-WORK-AUDIENCE-POLICY"


class WorkAudience(StrEnum):
    """Source-proven work purpose, never a tenant role or permission."""

    OPERATING = "OPERATING"
    PLATFORM_BUILD = "PLATFORM_BUILD"
    UNCLASSIFIED = "UNCLASSIFIED"


class WorkAudiencePolicyError(ValueError):
    """Stable fail-closed work-purpose evidence error, without source details."""

    def __init__(self, code: str) -> None:
        """Return a fixed error code; no source document is disclosed."""
        self.code = code
        super().__init__(code)


@dataclass(frozen=True, slots=True)
class WorkAudienceDecision:
    """Read-only verified category result and evidence provenance.

    UNCLASSIFIED means the source has not supplied audited current evidence;
    it is never proof of an Operating or Platform Build decision. critical_gate
    may be true only with independently source-owned critical-gate evidence.
    """

    audience: WorkAudience
    source_evidence_ref: str | None
    source_revision: int | None
    critical_gate: bool


def _coordinate(value: object) -> bool:
    """Require a non-empty exact opaque identity without normalization."""
    return isinstance(value, str) and bool(value) and value == value.strip() and len(value) <= 256


def evaluate_work_audience(
    *, tenant_id: str, source: str, record_id: str, source_revision: int | None,
    evidence: Mapping[str, object] | None,
) -> WorkAudienceDecision:
    """Validate source-owned audience evidence for an already admitted work row.

    A caller must first enforce current exact-tenant membership, source read,
    item visibility and entitlement. Evidence is an authenticated output of
    that same source and its source revision, not user-supplied free text.
    No title or module-name heuristic is permitted. A source with no verified
    evidence remains visible as UNCLASSIFIED rather than silently suppressed.
    A purported classification that is foreign, stale, unsigned/unverified,
    missing its source audit coordinate, or unsupported fails closed.
    This policy does not create classifications, grants, approvals or scores.
    """
    if not all(_coordinate(value) for value in (tenant_id, source, record_id)):
        raise WorkAudiencePolicyError("WORK_AUDIENCE_SCOPE_INVALID")
    if source_revision is not None and (type(source_revision) is not int or source_revision < 1):
        raise WorkAudiencePolicyError("WORK_AUDIENCE_SOURCE_REVISION_INVALID")
    if evidence is None:
        return WorkAudienceDecision(WorkAudience.UNCLASSIFIED, None, None, False)
    if not isinstance(evidence, Mapping):
        raise WorkAudiencePolicyError("WORK_AUDIENCE_EVIDENCE_INVALID")
    allowed = frozenset({
        "tenant_id", "source", "record_id", "source_revision", "audience",
        "evidence_ref", "source_verified", "critical_gate", "critical_gate_evidence_ref",
    })
    if frozenset(evidence) != allowed:
        raise WorkAudiencePolicyError("WORK_AUDIENCE_EVIDENCE_INVALID")
    if (evidence.get("tenant_id") != tenant_id or evidence.get("source") != source
            or evidence.get("record_id") != record_id):
        raise WorkAudiencePolicyError("WORK_AUDIENCE_SCOPE_MISMATCH")
    if source_revision is None or type(evidence.get("source_revision")) is not int or (
        evidence["source_revision"] != source_revision
    ):
        raise WorkAudiencePolicyError("WORK_AUDIENCE_REVISION_MISMATCH")
    if evidence.get("source_verified") is not True or not _coordinate(evidence.get("evidence_ref")):
        raise WorkAudiencePolicyError("WORK_AUDIENCE_SOURCE_UNVERIFIED")
    value = evidence.get("audience")
    if value not in (WorkAudience.OPERATING.value, WorkAudience.PLATFORM_BUILD.value):
        raise WorkAudiencePolicyError("WORK_AUDIENCE_CLASSIFICATION_INVALID")
    gate = evidence.get("critical_gate")
    if type(gate) is not bool:
        raise WorkAudiencePolicyError("WORK_AUDIENCE_CRITICAL_GATE_INVALID")
    gate_ref = evidence.get("critical_gate_evidence_ref")
    if gate:
        if value != WorkAudience.PLATFORM_BUILD or not _coordinate(gate_ref):
            raise WorkAudiencePolicyError("WORK_AUDIENCE_CRITICAL_GATE_UNVERIFIED")
    elif gate_ref is not None:
        raise WorkAudiencePolicyError("WORK_AUDIENCE_CRITICAL_GATE_UNVERIFIED")
    return WorkAudienceDecision(WorkAudience(value), str(evidence["evidence_ref"]),
                                source_revision, gate)


__all__ = ["VERSION", "WorkAudience", "WorkAudiencePolicyError", "WorkAudienceDecision", "evaluate_work_audience"]


# ARTIFACT: work_audience_policy.py
# VERSION: v1.0.0-EXACT-SOURCE-WORK-AUDIENCE-POLICY
# AUTHORITY BOUNDARY: Pure classifier of verified source claims, never grants IAM.
# TENANT POSTURE: Every proof bound to current tenant/source/record/revision.
# FAIL-CLOSED POSTURE: Unknown, foreign, stale or unsupported claims are rejected.
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively.
# END OF WILSY OS SOVEREIGN ARTIFACT
