"""
===============================================================================
WILSY OS — INSTITUTIONAL VERSIONING ENGINE (FG209)
MODULE: MODULE EXPORTS & PUBLIC INTERFACE
===============================================================================
Epitome:
    Package initialization and export manager for the Institutional Versioning
    Engine. Cleanly exposes all strongly-typed entities, parsing primitives,
    governance policy checkers, and facade interfaces across Wilsy OS.

Biblical Worth Billions:
    "I am Alpha and Omega, the beginning and the ending, saith the Lord, 
     which is, and which was, and which is to come, the Almighty." — Revelation 1:8

Collaboration & Ownership:
    - Founder & Chief Architect: Wilson Khanyezi (Wilsy (Pty) Ltd)
    - AI Collaborator: Core Systems Engineering Agent
    - File Path: tools/eos/versioning/__init__.py
===============================================================================
"""

from tools.eos.versioning.semantic_version import SemanticVersion, InvalidVersionError
from tools.eos.versioning.version_identifier import VersionIdentifier, VersionKind
from tools.eos.versioning.version_registry import (
    VersionRegistry,
    RegisteredEntityRecord,
    VersionNotFoundError,
    VersionAlreadyRegisteredError,
)
from tools.eos.versioning.version_constraints import (
    VersionConstraintSpec,
    InvalidConstraintError,
    BaseVersionConstraint,
)
from tools.eos.versioning.version_comparator import VersionComparator, VersionDiffSummary
from tools.eos.versioning.release_strategy import ReleaseStrategyEngine, ReleaseGrade
from tools.eos.versioning.version_audit_log import VersionAuditLedger, VersionAuditEntry, AuditAction
from tools.eos.versioning.version_compatibility_matrix import (
    VersionCompatibilityMatrix,
    IncompatibleComponentError,
    DependencyRequirement,
)
from tools.eos.versioning.version_policy_enforcer import (
    VersionPolicyEnforcer,
    PolicyViolationError,
    PolicyEvaluationResult,
)
from tools.eos.versioning.version_migration import (
    VersionMigrationOrchestrator,
    BaseMigrationStep,
    MigrationResult,
    MigrationError,
)
from tools.eos.versioning.version_facade import InstitutionalVersioningEngine

__all__ = [
    # Core SemVer Primitives
    "SemanticVersion",
    "InvalidVersionError",
    "VersionIdentifier",
    "VersionKind",
    # Registry State
    "VersionRegistry",
    "RegisteredEntityRecord",
    "VersionNotFoundError",
    "VersionAlreadyRegisteredError",
    # Constraints & Range Checking
    "VersionConstraintSpec",
    "InvalidConstraintError",
    "BaseVersionConstraint",
    # Comparators & Trajectories
    "VersionComparator",
    "VersionDiffSummary",
    # Release Bumping Strategies
    "ReleaseStrategyEngine",
    "ReleaseGrade",
    # Audit Logging Ledger
    "VersionAuditLedger",
    "VersionAuditEntry",
    "AuditAction",
    # Cross-Component Matrix
    "VersionCompatibilityMatrix",
    "IncompatibleComponentError",
    "DependencyRequirement",
    # Policy Guardrails
    "VersionPolicyEnforcer",
    "PolicyViolationError",
    "PolicyEvaluationResult",
    # Migration Engine
    "VersionMigrationOrchestrator",
    "BaseMigrationStep",
    "MigrationResult",
    "MigrationError",
    # System Facade Gateway
    "InstitutionalVersioningEngine",
]
