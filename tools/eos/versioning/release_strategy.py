"""
===============================================================================
WILSY OS — INSTITUTIONAL VERSIONING ENGINE (FG209)
MODULE: RELEASE STRATEGY & BUMPING ENGINE
===============================================================================
Epitome:
    Calculates deterministic version transitions based on explicit release grades.
    Governs major breaking bumps, minor feature additions, patch fixes, and
    pre-release lifecycle advancements safely.

Biblical Worth Billions:
    "For which of you, intending to build a tower, sitteth not down first, 
     and counteth the cost, whether he have sufficient to finish it?" — Luke 14:28

Collaboration & Ownership:
    - Founder & Chief Architect: Wilson Khanyezi (Wilsy (Pty) Ltd)
    - AI Collaborator: Core Systems Engineering Agent
    - File Path: tools/eos/versioning/release_strategy.py
===============================================================================
"""

from __future__ import annotations

from enum import Enum
from typing import Optional, Union

from tools.eos.versioning.semantic_version import SemanticVersion


class ReleaseGrade(str, Enum):
    """Enumeration of authorized release magnitude increments."""
    MAJOR = "major"
    MINOR = "minor"
    PATCH = "patch"
    PRERELEASE = "prerelease"
    BUILD_METADATA = "build_metadata"


class ReleaseStrategyEngine:
    """
    Stateless engine for calculating subsequent semantic versions strictly 
    adhering to platform deployment rules.
    """

    @classmethod
    def calculate_next(
        cls, 
        current: Union[SemanticVersion, str], 
        grade: ReleaseGrade, 
        prerelease_tag: Optional[str] = None,
        build_tag: Optional[str] = None
    ) -> SemanticVersion:
        """
        Calculates the next version mathematically based on the requested grade.
        
        Args:
            current: The existing baseline SemanticVersion.
            grade: The requested release magnitude (MAJOR, MINOR, PATCH, PRERELEASE).
            prerelease_tag: Optional string required if grade is PRERELEASE.
            build_tag: Optional metadata tag to append to the result.
            
        Returns:
            SemanticVersion: The newly calculated target version.
        """
        base_ver = current if isinstance(current, SemanticVersion) else SemanticVersion.parse(current)
        
        target_ver: SemanticVersion

        if grade == ReleaseGrade.MAJOR:
            target_ver = base_ver.bump_major()
        
        elif grade == ReleaseGrade.MINOR:
            target_ver = base_ver.bump_minor()
            
        elif grade == ReleaseGrade.PATCH:
            target_ver = base_ver.bump_patch()
            
        elif grade == ReleaseGrade.PRERELEASE:
            if not prerelease_tag:
                raise ValueError("A 'prerelease_tag' string must be provided for a PRERELEASE bump.")
            target_ver = base_ver.with_prerelease(prerelease_tag)
            
        elif grade == ReleaseGrade.BUILD_METADATA:
            if not build_tag:
                raise ValueError("A 'build_tag' string must be provided for a BUILD_METADATA update.")
            target_ver = base_ver.with_build(build_tag)
            
        else:
            raise ValueError(f"Unknown ReleaseGrade: {grade}")

        # If a build tag was provided for standard bumps, apply it post-calculation
        if build_tag and grade != ReleaseGrade.BUILD_METADATA:
            target_ver = target_ver.with_build(build_tag)

        return target_ver

    @classmethod
    def evaluate_conventional_commits(cls, commits: list[str]) -> ReleaseGrade:
        """
        Analyzes a list of conventional commit messages to determine the requisite 
        ReleaseGrade for an automated build pipeline.
        
        Rules:
        - "BREAKING CHANGE" or type with "!" (e.g., feat!) -> MAJOR
        - "feat:" -> MINOR
        - "fix:", "perf:" -> PATCH
        - Anything else defaults to PATCH unless explicitly bypassed.
        """
        recommended_grade = ReleaseGrade.PATCH

        for msg in commits:
            clean_msg = msg.strip()
            
            # 1. Check for Major triggers
            if "BREAKING CHANGE" in clean_msg or "!" in clean_msg.split(":")[0]:
                return ReleaseGrade.MAJOR  # Short-circuit, highest precedence
                
            # 2. Check for Minor triggers
            if clean_msg.startswith("feat:") or clean_msg.startswith("feat("):
                recommended_grade = ReleaseGrade.MINOR
                
            # 3. Patch triggers (fix, perf, etc.) are already the default fallback

        return recommended_grade
