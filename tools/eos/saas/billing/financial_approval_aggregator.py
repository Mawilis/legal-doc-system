# -*- coding: utf-8 -*-
"""WILSY OS – deterministic, shared-snapshot financial approval aggregation.

VERSION: v1.2.0-FINANCIAL-APPROVAL-AGGREGATOR
Only immutable policy, decision, and authorization evidence is read. Semantics are frozen at
FINANCIAL_APPROVAL_AGGREGATION_SEMANTICS_VERSION: distinct authorized actors, one decision per lane,
strict policy versions, valid-at-decision authorization, deterministic contradiction collapse, and
evaluation-wide rejection precedence. No result is persisted and no VendorBill/payment action is performed.
"""
from __future__ import annotations
import hashlib, json
from datetime import datetime
from typing import Any, Optional
from pymongo import MongoClient
from pymongo.read_concern import ReadConcern
from pymongo.database import Database
from ..domain.financial_approval_effective_result import (FinancialApprovalDecisionExclusionReason, FinancialApprovalEffectiveResult, FinancialApprovalEffectiveState, FinancialApprovalExcludedDecision, FinancialApprovalRequirementResult)
from ..domain.financial_approval_decision import FinancialApprovalDecision, FinancialApprovalDecisionType, FinancialApprovalSubjectType
from ..domain.financial_approval_policy_evaluation import FinancialApprovalPolicyEvaluation
from .financial_approval_policy_evaluation_registry import FinancialApprovalPolicyEvaluationRegistry
from .financial_approval_decision_registry import FinancialApprovalDecisionRegistry
from .financial_approval_actor_authorization_registry import FinancialApprovalActorAuthorizationRegistry
from ...kernel.db import get_database

FINANCIAL_APPROVAL_AGGREGATION_SEMANTICS_VERSION = "1.0.0"
MAX_EVIDENCE = 250

class FinancialApprovalAggregatorError(RuntimeError):
    """Infrastructure failure during evidence aggregation; never a business approval state."""

class FinancialApprovalAggregator:
    def __init__(self, database: Optional[Database[Any]] = None, client: Optional[MongoClient[Any]] = None) -> None:
        self._database = database
        self._client = client or (database.client if database is not None else None)

    def _db(self) -> Database[Any]:
        database = self._database if self._database is not None else get_database()
        if database is None:
            raise FinancialApprovalAggregatorError("FINANCIAL_APPROVAL_AGGREGATOR_PERSISTENCE_UNAVAILABLE")
        return database

    @staticmethod
    def _collect_subject_decisions(tenant_id: str, subject_type: FinancialApprovalSubjectType, subject_id: str, collection: Any, session: Any) -> tuple[FinancialApprovalDecision, ...]:
        collected: list[FinancialApprovalDecision] = []
        cursor: Optional[str] = None
        while True:
            page = FinancialApprovalDecisionRegistry.list_for_subject_page(tenant_id, subject_type, subject_id, MAX_EVIDENCE, cursor, collection, session=session)
            collected.extend(page.items)
            if page.next_cursor is None:
                return tuple(collected)
            cursor = page.next_cursor

    @staticmethod
    def _collect_requirement_authorizations(tenant_id: str, evaluation_id: str, requirement_id: str, collection: Any, session: Any) -> tuple[Any, ...]:
        collected: list[Any] = []
        cursor: Optional[str] = None
        while True:
            page = FinancialApprovalActorAuthorizationRegistry.list_for_requirement_page(tenant_id, evaluation_id, requirement_id, MAX_EVIDENCE, cursor, collection, session=session)
            collected.extend(page.items)
            if page.next_cursor is None:
                return tuple(collected)
            cursor = page.next_cursor

    @staticmethod
    def _fingerprint(evaluation: FinancialApprovalPolicyEvaluation, decisions: list[FinancialApprovalDecision], authorizations: list[Any]) -> str:
        payload = {"semantics_version": FINANCIAL_APPROVAL_AGGREGATION_SEMANTICS_VERSION, "evaluation": evaluation.to_dict(), "decisions": [d.to_dict() for d in sorted(decisions, key=lambda x: x.decision_id)], "authorizations": [a.to_dict() for a in sorted(authorizations, key=lambda x: x.authorization_id)]}
        return hashlib.sha3_512(json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode("utf-8")).hexdigest()

    def aggregate(self, tenant_id: str, evaluation_id: str, result_id: str, evaluated_at: datetime, created_at: datetime) -> FinancialApprovalEffectiveResult:
        database = self._db(); client = self._client or database.client
        decisions: list[FinancialApprovalDecision] = []; authorizations: list[Any] = []
        with client.start_session() as session:
            session.start_transaction(read_concern=ReadConcern("snapshot"))
            evaluation = FinancialApprovalPolicyEvaluationRegistry.get(tenant_id, evaluation_id, database["financial_approval_policy_evaluations"], session=session)
            decisions = list(self._collect_subject_decisions(tenant_id, FinancialApprovalSubjectType(evaluation.subject_type.value), evaluation.subject_id, database["financial_approval_decisions"], session))
            for requirement in evaluation.approval_requirements:
                authorizations.extend(self._collect_requirement_authorizations(tenant_id, evaluation.evaluation_id, requirement.requirement_id, database["financial_approval_actor_authorizations"], session))
            session.commit_transaction()
        fingerprint = self._fingerprint(evaluation, decisions, authorizations)
        if not evaluation.approval_required:
            return FinancialApprovalEffectiveResult(tenant_id=evaluation.tenant_id,result_id=result_id,subject_type=evaluation.subject_type,subject_id=evaluation.subject_id,subject_revision=evaluation.subject_revision,evaluation_id=evaluation.evaluation_id,approval_policy_reference=evaluation.approval_policy_reference,approval_policy_version=evaluation.approval_policy_version,effective_state=FinancialApprovalEffectiveState.NOT_REQUIRED,evaluated_at=evaluated_at,created_at=created_at,source_evidence_fingerprint=fingerprint)
        exclusions: list[FinancialApprovalExcludedDecision] = []
        mapped: list[tuple[FinancialApprovalDecision, Any, str]] = []
        reqs = {r.requirement_id: r for r in evaluation.approval_requirements}
        auth_by_req = {r: [a for a in authorizations if a.requirement_id == r] for r in reqs}
        for decision in decisions:
            reason: Optional[FinancialApprovalDecisionExclusionReason] = None
            if decision.subject_revision != evaluation.subject_revision: reason = FinancialApprovalDecisionExclusionReason.WRONG_SUBJECT_REVISION
            elif decision.approval_policy_reference != evaluation.approval_policy_reference: reason = FinancialApprovalDecisionExclusionReason.POLICY_REFERENCE_MISMATCH
            elif decision.approval_policy_version is None: reason = FinancialApprovalDecisionExclusionReason.POLICY_VERSION_MISSING
            elif decision.approval_policy_version != evaluation.approval_policy_version: reason = FinancialApprovalDecisionExclusionReason.POLICY_VERSION_MISMATCH
            lanes: list[tuple[Any, Any]] = []
            if reason is None:
                candidate_auth = [a for a in authorizations if a.actor_id == decision.actor_id and a.subject_revision == decision.subject_revision]
                capacity_requirements = [r for r in reqs.values() if r.actor_capacity == decision.actor_capacity]
                if not capacity_requirements:
                    reason = (FinancialApprovalDecisionExclusionReason.ACTOR_CAPACITY_MISMATCH if candidate_auth else FinancialApprovalDecisionExclusionReason.NO_MATCHING_REQUIREMENT)
                elif not candidate_auth:
                    reason = FinancialApprovalDecisionExclusionReason.UNAUTHORIZED_ACTOR
                for requirement_id, requirement in reqs.items():
                    if reason is not None:
                        break
                    matches = [a for a in auth_by_req[requirement_id] if a.actor_id == decision.actor_id and a.actor_capacity == decision.actor_capacity == requirement.actor_capacity and a.subject_revision == decision.subject_revision and a.authorized_at <= decision.decided_at and (a.valid_until is None or decision.decided_at <= a.valid_until)]
                    if matches: lanes.append((requirement, sorted(matches, key=lambda a: (-a.authorized_at.timestamp(), a.authorization_id))[0]))
                if not lanes and reason is None:
                    time_auth = [a for a in candidate_auth if a.actor_capacity == decision.actor_capacity and any(r.actor_capacity == a.actor_capacity for r in reqs.values())]
                    if time_auth and any(a.authorized_at > decision.decided_at for a in time_auth): reason = FinancialApprovalDecisionExclusionReason.AUTHORIZATION_NOT_YET_VALID
                    elif time_auth and all(a.valid_until is not None and decision.decided_at > a.valid_until for a in time_auth): reason = FinancialApprovalDecisionExclusionReason.AUTHORIZATION_EXPIRED
                    elif candidate_auth and not any(a.actor_capacity == decision.actor_capacity for a in candidate_auth): reason = FinancialApprovalDecisionExclusionReason.ACTOR_CAPACITY_MISMATCH
                    else: reason = FinancialApprovalDecisionExclusionReason.UNAUTHORIZED_ACTOR
                elif len(lanes) > 1: reason = FinancialApprovalDecisionExclusionReason.AMBIGUOUS_REQUIREMENT_MAPPING
            if reason is not None: exclusions.append(FinancialApprovalExcludedDecision(decision.decision_id, decision.actor_id, reason)); continue
            mapped.append((decision, lanes[0][1], lanes[0][0].requirement_id))
        effective: dict[tuple[str,str], tuple[FinancialApprovalDecision, Any]] = {}
        for decision, authorization, requirement_id in mapped:
            key=(requirement_id, decision.actor_id); current=effective.get(key)
            if current is None or decision.decided_at > current[0].decided_at or (decision.decided_at == current[0].decided_at and decision.decision_id < current[0].decision_id):
                if current: exclusions.append(FinancialApprovalExcludedDecision(current[0].decision_id,current[0].actor_id,FinancialApprovalDecisionExclusionReason.SUPERSEDED_BY_LATER_DECISION,key[0]))
                effective[key]=(decision,authorization)
            else: exclusions.append(FinancialApprovalExcludedDecision(decision.decision_id,decision.actor_id,FinancialApprovalDecisionExclusionReason.SUPERSEDED_BY_LATER_DECISION,requirement_id))
        requirement_results=[]; counted_decisions=[]; counted_auth=[]; rejection_decisions=[]; rejection_actors=[]
        for requirement in evaluation.approval_requirements:
            rows=[(d,a) for (rid,_), (d,a) in effective.items() if rid == requirement.requirement_id and d.decision is FinancialApprovalDecisionType.APPROVED]
            rows.sort(key=lambda x:x[0].actor_id); actors=tuple(d.actor_id for d,a in rows); decisions_ids=tuple(d.decision_id for d,a in rows); auth_ids=tuple(a.authorization_id for d,a in rows); counted_decisions.extend(decisions_ids); counted_auth.extend(auth_ids); requirement_results.append(FinancialApprovalRequirementResult(requirement.requirement_id,requirement.actor_capacity,requirement.approvals_required,len(actors),len(actors)>=requirement.approvals_required,actors,decisions_ids,auth_ids))
        for d,a in sorted(effective.values(),key=lambda x:(x[0].decided_at,x[0].decision_id)):
            if d.decision is FinancialApprovalDecisionType.REJECTED: rejection_decisions.append(d.decision_id); rejection_actors.append(d.actor_id)
        rejection_decisions=sorted(set(rejection_decisions)); rejection_actors=sorted(set(rejection_actors)); reject_count=len(rejection_actors); rejected=(bool(rejection_decisions) if evaluation.rejection_rule.value == "ANY_VALID_REJECTION_BLOCKS" else reject_count >= (evaluation.rejections_required or 0)); state=FinancialApprovalEffectiveState.REJECTED if rejected else (FinancialApprovalEffectiveState.APPROVED if all(r.satisfied for r in requirement_results) else FinancialApprovalEffectiveState.PENDING)
        exclusions=sorted(exclusions,key=lambda e:(e.decision_id,e.actor_id,e.reason.value))[:MAX_EVIDENCE]
        return FinancialApprovalEffectiveResult(tenant_id=evaluation.tenant_id,result_id=result_id,subject_type=evaluation.subject_type,subject_id=evaluation.subject_id,subject_revision=evaluation.subject_revision,evaluation_id=evaluation.evaluation_id,approval_policy_reference=evaluation.approval_policy_reference,approval_policy_version=evaluation.approval_policy_version,effective_state=state,evaluated_at=evaluated_at,created_at=created_at,requirement_results=tuple(requirement_results),counted_decision_ids=tuple(sorted(counted_decisions)),counted_authorization_ids=tuple(sorted(counted_auth)),rejection_decision_ids=tuple(rejection_decisions),rejection_actor_ids=tuple(rejection_actors),rejections_required=evaluation.rejections_required,rejections_counted=reject_count,excluded_decisions=tuple(exclusions),source_evidence_fingerprint=fingerprint)
