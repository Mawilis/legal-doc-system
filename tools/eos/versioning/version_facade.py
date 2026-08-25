"""
===============================================================================
WILSY OS — INSTITUTIONAL VERSIONING ENGINE (FG209)
MODULE: UNIFIED SYSTEM FACADE (GATEWAY)
===============================================================================
Epitome:
    Unified primary gateway facade for the Versioning Engine. Exposes a single,
    thread-safe operational API aggregating Registry, Policy Enforcer,
    Compatibility Matrix, Release Strategy, and Audit Ledger services.

Biblical Worth Billions:
    "For in him dwelleth all the fulness of the Godhead bodily." — Colossians 2:9

Collaboration & Ownership:
    - Founder & Chief Architect: Wilson Khanyezi (Wilsy (Pty) Ltd)
    - AI Collaborator: Core Systems Engineering Agent
    - File Path: tools/eos/versioning/version_facade.py
===============================================================================
"""

from __future__ import annotations

from typing import List, Optional, Tuple, Dict, Any, Union

from tools.eos.versioning.semantic_version import SemanticVersion
from tools.eos.versioning.version_identifier import VersionIdentifier, VersionKind
from tools.eos.versioning.version_registry import VersionRegistry, RegisteredEntityRecord
from tools.eos.versioning.version_audit_log import VersionAuditLedger, AuditAction, VersionAuditEntry
from tools.eos.versioning.version_policy_enforcer import VersionPolicyEnforcer, PolicyEvaluationResult
from tools.eos.versioning.version_compatibility_matrix import VersionCompatibilityMatrix
from tools.eos.versioning.release_strategy import ReleaseStrategyEngine, ReleaseGrade


class InstitutionalVersioningEngine:
    """
    Unified Facade providing single-point control over all versioning primitives 
    in Wilsy OS.
    """

    def __init__(self, current_kernel_version: str = "2.0.0") -> None:
        self.registry = VersionRegistry(current_kernel_version=current_kernel_version)
        self.audit_ledger = VersionAuditLedger()
        self.policy_enforcer = VersionPolicyEnforcer(registry=self.registry)
        self.compatibility_matrix = VersionCompatibilityMatrix()

        # Record initial kernel registration in audit ledger
        kernel_id = VersionIdentifier.create(
            kind=VersionKind.KERNEL,
            name="wilsy_kernel",
            version=current_kernel_version
        )
        self.audit_ledger.record_event(
            action=AuditAction.REGISTERED,
            identifier=kernel_id,
            actor="kernel_init",
            reason="Initial Kernel Boot"
        )

    # -------------------------------------------------------------------------
    # Registry & Lifecycle Operations
    # -------------------------------------------------------------------------

    def register_version(
        self,
        kind: Union[VersionKind, str],
        name: str,
        version: str,
        actor: str = "system",
        is_experimental: bool = False
    ) -> RegisteredEntityRecord:
        """
        Registers a new entity version and appends an entry to the audit ledger.
        """
        ver_id = VersionIdentifier.create(kind=kind, name=name, version=version)
        record = self.registry.register_entity(identifier=ver_id, is_experimental=is_experimental)
        
        self.audit_ledger.record_event(
            action=AuditAction.REGISTERED,
            identifier=ver_id,
            actor=actor
        )
        return record

    def deprecate_version(self, urn: str, reason: str, actor: str = "system") -> RegisteredEntityRecord:
        """
        Marks a registered entity version as deprecated.
        """
        record = self.registry.mark_deprecated(urn, reason)
        self.audit_ledger.record_event(
            action=AuditAction.DEPRECATED,
            identifier=record.identifier,
            actor=actor,
            reason=reason
        )
        return record

    def remove_version(self, urn: str, actor: str = "system") -> RegisteredEntityRecord:
        """
        Marks a registered entity version as removed from service.
        """
        record = self.registry.mark_removed(urn)
        self.audit_ledger.record_event(
            action=AuditAction.REMOVED,
            identifier=record.identifier,
            actor=actor
        )
        return record

    # -------------------------------------------------------------------------
    # Execution Governance & Policy
    # -------------------------------------------------------------------------

    def verify_execution_permitted(self, urn: str) -> None:
        """
        Enforces runtime execution safety rules for a target URN.
        Raises PolicyViolationError if blocked.
        """
        self.policy_enforcer.enforce_execution_allowed(urn)

    def validate_deployment_upgrade(
        self, 
        current_urn: str, 
        target_urn: str, 
        breaking_approved: bool = False
    ) -> PolicyEvaluationResult:
        """
        Validates whether upgrading from current_urn to target_urn violates CI/CD policy.
        """
        return self.policy_enforcer.validate_upgrade_path(
            current_urn=current_urn,
            target_urn=target_urn,
            breaking_change_approved=breaking_approved
        )

    # -------------------------------------------------------------------------
    # Compatibility Matrix Governance
    # -------------------------------------------------------------------------

    def register_compatibility_rule(
        self, 
        source_urn: str, 
        dependencies: List[Tuple[VersionKind, str, str]]
    ) -> None:
        """
        Registers dependency requirements for a given component.
        """
        self.compatibility_matrix.register_rule(source_urn, dependencies)

    def validate_cluster_compatibility(self, active_urns: List[str]) -> Tuple[bool, List[str]]:
        """
        Verifies that all active services in a cluster fulfill cross-component requirements.
        """
        return self.compatibility_matrix.validate_cluster(active_urns)

    # -------------------------------------------------------------------------
    # Release Bumping Calculations
    # -------------------------------------------------------------------------

    @staticmethod
    def calculate_next_version(
        current_version: str,
        grade: ReleaseGrade,
        prerelease_tag: Optional[str] = None,
        build_tag: Optional[str] = None
    ) -> SemanticVersion:
        """
        Calculates next semantic version string based on release grade.
        """
        return ReleaseStrategyEngine.calculate_next(
            current=current_version,
            grade=grade,
            prerelease_tag=prerelease_tag,
            build_tag=build_tag
        )

    # -------------------------------------------------------------------------
    # Audit Trail Access
    # -------------------------------------------------------------------------

    def get_audit_trail(self) -> List[VersionAuditEntry]:
        """
        Returns complete immutable history of versioning operations.
        """
        return self.audit_ledger.get_full_ledger()
