"""
===============================================================================
WILSY ENGINEERING KERNEL
===============================================================================
Epitome:
    Knowledge Base Playbook Engine for Legal AI Operations (FG172A).
    Defines immutable legal playbooks, rule evaluation engines, compliance tracking,
    and contextual policy enforcement for legal document intelligence.
    Billion-dollar software architecture: secure, robust, immutable, and future-proof.

Biblical Scale & Architecture:
    Production-ready knowledge playbook engine. Zero child's place.
    Hosea 4:6 - "My people are destroyed for lack of knowledge..."
    Proverbs 2:6 - "For the LORD giveth wisdom: out of his mouth cometh knowledge and understanding."

Collaboration & Maintenance:
    - [Architecture]: Rule parsing, semantic trigger matching, policy evaluation.
    - [Diagnostics]: Full async evaluation harness with remediation mapping & regex pattern matching.
    - Maintained by Wilson Khanyezi & Core Engineering.
===============================================================================
"""

from __future__ import annotations

import logging
import re
import time
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional
from uuid import uuid4

from pydantic import BaseModel, ConfigDict, Field

logger = logging.getLogger("WilsyOS.Knowledge.Playbook")


class PlaybookSeverityEnum(str, Enum):
    """Severity classification for playbook rule violations."""
    CRITICAL = "CRITICAL"
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"
    INFO = "INFO"


class PlaybookCategoryEnum(str, Enum):
    """Functional categorization for legal playbook rules."""
    COMPLIANCE = "COMPLIANCE"
    CLAUSE_VERIFICATION = "CLAUSE_VERIFICATION"
    RISK_ASSESSMENT = "RISK_ASSESSMENT"
    GOVERNANCE = "GOVERNANCE"
    STATUTORY = "STATUTORY"


class PlaybookRule(BaseModel):
    """Immutable rule specification within a legal playbook."""
    model_config = ConfigDict(frozen=True)

    rule_id: str = Field(default_factory=lambda: f"rule-{uuid4().hex[:8]}", description="Unique rule identifier.")
    title: str = Field(description="Human-readable rule title.")
    category: PlaybookCategoryEnum = Field(description="Functional domain of the rule.")
    severity: PlaybookSeverityEnum = Field(default=PlaybookSeverityEnum.HIGH, description="Violation severity level.")
    description: str = Field(description="Detailed explanation of legal standard or requirement.")
    required_keywords: List[str] = Field(
        default_factory=list,
        description="Required keywords/phrases (supports '|' separated alternatives, e.g., 'governing law|governed by')."
    )
    prohibited_keywords: List[str] = Field(
        default_factory=list,
        description="Keywords or phrases that trigger a policy violation."
    )
    custom_regex_patterns: List[str] = Field(
        default_factory=list,
        description="Custom regular expression patterns that must match document text."
    )
    remediation_guidance: str = Field(description="Actionable steps to resolve rule non-compliance.")


class KnowledgeBasePlaybook(BaseModel):
    """Aggregate entity representing an enterprise legal playbook."""
    model_config = ConfigDict(frozen=False)

    playbook_id: str = Field(default_factory=lambda: f"pb-{uuid4().hex[:8]}", description="Unique playbook identifier.")
    domain: str = Field(description="Target legal domain (e.g., Commercial Contracts, Regulatory Compliance).")
    title: str = Field(description="Playbook name.")
    version: str = Field(default="1.0.0", description="Semantic version string.")
    rules: List[PlaybookRule] = Field(default_factory=list, description="List of configured rules.")
    is_active: bool = Field(default=True, description="Active status flag.")
    created_at: str = Field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat(),
        description="ISO timestamp of creation."
    )

    # [FUNCTION EXPLANATION]: Safely registers a new rule into the active playbook.
    def add_rule(self, rule: PlaybookRule) -> None:
        """Appends a new rule to the playbook."""
        self.rules.append(rule)


class RuleEvaluationResult(BaseModel):
    """Evaluation result for an individual playbook rule."""
    model_config = ConfigDict(frozen=True)

    rule_id: str = Field(description="Evaluated rule ID.")
    rule_title: str = Field(description="Title of evaluated rule.")
    passed: bool = Field(description="True if rule requirements were met.")
    severity: PlaybookSeverityEnum = Field(description="Rule severity.")
    matched_snippets: List[str] = Field(default_factory=list, description="Text segments matching triggers.")
    findings: str = Field(description="Summary of analysis outcome.")
    remediation_guidance: Optional[str] = Field(default=None, description="Guidance if rule failed.")


class PlaybookExecutionReport(BaseModel):
    """Complete summary report generated from running a playbook against a legal document."""
    model_config = ConfigDict(frozen=True)

    report_id: str = Field(default_factory=lambda: f"rpt-{uuid4().hex[:8]}", description="Unique report ID.")
    playbook_id: str = Field(description="Executed playbook ID.")
    document_id: str = Field(description="Target legal document ID.")
    compliance_score: float = Field(ge=0.0, le=100.0, description="Overall compliance score percentage.")
    total_rules: int = Field(ge=0, description="Total rules evaluated.")
    passed_rules: int = Field(ge=0, description="Number of rules passed.")
    failed_rules: int = Field(ge=0, description="Number of rules failed.")
    execution_duration_ms: float = Field(ge=0.0, description="Execution duration in milliseconds.")
    results: List[RuleEvaluationResult] = Field(default_factory=list, description="Individual rule evaluation results.")


class PlaybookExecutionEngine:
    """Async engine for evaluating legal documents against Knowledge Base Playbooks."""

    def __init__(self, playbook: KnowledgeBasePlaybook) -> None:
        self._playbook = playbook
        logger.info(f"Initialized PlaybookExecutionEngine for Playbook [{playbook.playbook_id}] - Domain: {playbook.domain}")

    # [FUNCTION EXPLANATION]: Evaluates a single rule against target document text content.
    def _evaluate_rule(self, rule: PlaybookRule, text_content: str) -> RuleEvaluationResult:
        lowered_text = text_content.lower()
        matched_snippets: List[str] = []
        violations: List[str] = []

        # 1. Check prohibited terms
        for term in rule.prohibited_keywords:
            pattern = r'\b' + re.escape(term.lower()) + r'\b'
            if re.search(pattern, lowered_text):
                matched_snippets.append(f"Prohibited term found: '{term}'")
                violations.append(f"Document contains prohibited term '{term}'.")

        # 2. Check required terms (supports option groups delimited by '|')
        missing_required = []
        for term_group in rule.required_keywords:
            options = [opt.strip().lower() for opt in term_group.split("|")]
            found = False
            for opt in options:
                pattern = r'\b' + re.escape(opt) + r'\b'
                if re.search(pattern, lowered_text):
                    found = True
                    matched_snippets.append(f"Matched required term: '{opt}'")
                    break
            if not found:
                missing_required.append(term_group)

        if missing_required:
            violations.append(f"Missing required key terms: {', '.join(missing_required)}")

        # 3. Check custom regex patterns
        for pattern_str in rule.custom_regex_patterns:
            if not re.search(pattern_str, text_content, re.IGNORECASE):
                violations.append(f"Document failed required pattern: '{pattern_str}'")

        passed = len(violations) == 0
        findings = "Rule requirement satisfied." if passed else " | ".join(violations)

        return RuleEvaluationResult(
            rule_id=rule.rule_id,
            rule_title=rule.title,
            passed=passed,
            severity=rule.severity,
            matched_snippets=matched_snippets,
            findings=findings,
            remediation_guidance=rule.remediation_guidance if not passed else None,
        )

    # [FUNCTION EXPLANATION]: Runs full asynchronous evaluation of all playbook rules against document content.
    async def execute_playbook(self, document_id: str, document_text: str) -> PlaybookExecutionReport:
        """
        Executes all active rules in the playbook against the document text asynchronously,
        returning a standardized PlaybookExecutionReport with compliance scoring.
        """
        start_time = time.perf_counter()
        logger.info(f"Executing Playbook [{self._playbook.playbook_id}] against Document [{document_id}]")

        results: List[RuleEvaluationResult] = []
        passed_count = 0

        for rule in self._playbook.rules:
            result = self._evaluate_rule(rule, document_text)
            results.append(result)
            if result.passed:
                passed_count += 1

        total_rules = len(self._playbook.rules)
        failed_count = total_rules - passed_count
        score = round((passed_count / total_rules * 100.0), 2) if total_rules > 0 else 100.0
        duration_ms = round((time.perf_counter() - start_time) * 1000, 2)

        logger.info(
            f"Playbook execution finished for Document [{document_id}]. "
            f"Score: {score}% ({passed_count}/{total_rules} passed) in {duration_ms}ms"
        )

        return PlaybookExecutionReport(
            playbook_id=self._playbook.playbook_id,
            document_id=document_id,
            compliance_score=score,
            total_rules=total_rules,
            passed_rules=passed_count,
            failed_rules=failed_count,
            execution_duration_ms=duration_ms,
            results=results,
        )
