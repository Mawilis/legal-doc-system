"""TITLE: WILSY OS Canonical Ethical-Wall Source Adapters.
VERSION: v1.0.0-G78-CANONICAL-TRANSACTIONAL-SOURCE-ADAPTERS
AUTHORITY: Exact transaction-bound canonical evidence reads only.
EPITOME: Adapt current IAM, binding, assignment, conflict, confidentiality
review and G76-B policy sources to G77 without accepting caller approvals or
converting documentary evidence into operational access.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tools/eos/legal_operations/service/legal_work_ethical_wall_source_adapters.py
COLLABORATION / OWNERSHIP: Wilsy OS Core Engineering / Legal Operations;
canonical registries retain persistence and currentness ownership.
CERTIFICATION / UPDATE DATE: 2026-10-21.
CHANGELOG: 2026-10-21 v1.0.0 introduces six bounded G78 source adapters.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2.
SECURITY / PRIVACY POSTURE: Content-free stable failures and no logging.
TENANT BOUNDARY: Every read uses exact tenant/matter/practitioner predicates.
TRANSACTION BOUNDARY: Active caller-owned transaction required throughout.
AUTHORITY BOUNDARY: Evidence retrieval only; no content or operational grant.
FINANCIAL AUTHORITY BOUNDARY: None; Kennel EOS exclusively.
"""
from __future__ import annotations

from dataclasses import fields, replace
from datetime import datetime, timezone
from enum import StrEnum
from typing import Any, Final, NoReturn

from tools.eos.auth.tenant_authorization import authorize_tenant_operation
from tools.eos.legal_operations.domain.legal_practitioner_matter_binding import (
    LegalPractitionerMatterBinding as Binding,
    PractitionerMatterBindingStatus,
)
from tools.eos.legal_operations.domain.legal_work_assignment import LegalWorkAssignment
from tools.eos.legal_operations.domain.legal_work_practitioner_confidentiality_review_decision import (
    ConfidentialityReviewCurrentnessState,
    ConfidentialityReviewDecision,
    ConfidentialityReviewDecisionState,
    project_confidentiality_review_currentness,
)
from tools.eos.legal_operations.orchestration.legal_client_matter_conflict_disposition_currentness_composer import (
    LegalClientMatterConflictDispositionCurrentnessComposer,
)

VERSION: Final[str] = "v1.0.0-G78-CANONICAL-TRANSACTIONAL-SOURCE-ADAPTERS"
SOURCE_VERIFIED_CLEARANCE: Final[bool] = False
OPERATIONAL_ACCESS_ENABLED: Final[bool] = False
MAX_BINDING_ROWS: Final[int] = 4
MAX_REVIEW_HISTORY: Final[int] = 128


class EthicalWallSourceUnavailable(RuntimeError):
    """Stable non-sensitive canonical source failure."""

    def __init__(self, code: str) -> None:
        self.code = code
        super().__init__(code)


def _fail(code: str, cause: BaseException | None = None) -> NoReturn:
    error = EthicalWallSourceUnavailable(code)
    if cause is None:
        raise error
    raise error from cause


def _tx(session: object) -> object:
    try:
        marker = getattr(session, "in_transaction", False)
        active = marker() if callable(marker) else marker
    except Exception:
        active = False
    if active is not True:
        _fail("G78_SOURCE_TRANSACTION_REQUIRED")
    return session


def _id(value: object) -> str:
    if (
        type(value) is not str or not value or value != value.strip()
        or len(value) > 200 or any(character.isspace() for character in value)
        or value.casefold() in {"default", "global", "root", "*"}
    ):
        _fail("G78_SOURCE_SCOPE_INVALID")
    return value


def _at(value: object) -> datetime:
    if type(value) is not datetime or value.tzinfo is None or value.utcoffset() is None:
        _fail("G78_SOURCE_TIME_INVALID")
    result = value.astimezone(timezone.utc)
    if result.microsecond or result != value:
        _fail("G78_SOURCE_TIME_INVALID")
    return result


class CanonicalTenantIamSource:
    """Compose current tenant IAM from canonical repositories and fixed operation."""

    def __init__(
        self, *, permission_id: str, operation: str, principal_repository: object,
        membership_repository: object, business_role_repository: object,
        role_assignment_repository: object,
    ) -> None:
        self._permission = _id(permission_id)
        self._operation = _id(operation)
        self._principal = principal_repository
        self._membership = membership_repository
        self._business_role = business_role_repository
        self._role_assignment = role_assignment_repository

    def resolve_current(
        self, *, tenant_id: str, case_matter_id: str,
        practitioner_principal_id: str, session: object,
    ) -> object:
        """Return canonical IAM decision; matter remains independently verified."""
        tx = _tx(session)
        tenant, principal = _id(tenant_id), _id(practitioner_principal_id)
        _id(case_matter_id)
        try:
            return authorize_tenant_operation(
                principal_id=principal, tenant_id=tenant,
                permission_id=self._permission, operation=self._operation,
                principal_repository=self._principal,
                membership_repository=self._membership,
                business_role_repository=self._business_role,
                role_assignment_repository=self._role_assignment,
                session=tx,
            )
        except Exception as error:
            _fail("G78_IAM_SOURCE_UNAVAILABLE", error)


class CanonicalPractitionerBindingSource:
    """Read exact binding snapshots and reject revocation or ambiguity."""

    def __init__(self, collection: Any) -> None:
        self._collection = collection

    def resolve_current(
        self, *, tenant_id: str, case_matter_id: str,
        practitioner_principal_id: str, session: object,
    ) -> Binding:
        """Return one exact active unrevoked canonical binding."""
        tx = _tx(session)
        scope = {
            "tenant_id": _id(tenant_id), "case_matter_id": _id(case_matter_id),
            "practitioner_principal_id": _id(practitioner_principal_id),
        }
        try:
            rows = tuple(self._collection.find(scope, session=tx).limit(MAX_BINDING_ROWS + 1))
        except Exception as error:
            _fail("G78_BINDING_SOURCE_UNAVAILABLE", error)
        if not rows:
            _fail("G78_BINDING_NOT_FOUND")
        if len(rows) > MAX_BINDING_ROWS:
            _fail("G78_BINDING_HISTORY_INVALID")
        values: list[Binding] = []
        try:
            for row in rows:
                document = dict(row)
                document.pop("_id", None)
                values.append(Binding.from_dict(document))
        except Exception as error:
            _fail("G78_BINDING_INVALID", error)
        if any(
            item.tenant_id != scope["tenant_id"]
            or item.case_matter_id != scope["case_matter_id"]
            or item.practitioner_principal_id != scope["practitioner_principal_id"]
            for item in values
        ):
            _fail("G78_BINDING_SCOPE_INVALID")
        by_identity: dict[str, list[Binding]] = {}
        for item in values:
            by_identity.setdefault(item.binding_id, []).append(item)
        active: list[Binding] = []
        for history in by_identity.values():
            if any(item.status is PractitionerMatterBindingStatus.REVOKED for item in history):
                continue
            candidates = [
                item for item in history
                if item.status is PractitionerMatterBindingStatus.ACTIVE
            ]
            if len(candidates) == 1:
                active.extend(candidates)
        if not active and any(
            item.status is PractitionerMatterBindingStatus.REVOKED for item in values
        ):
            _fail("G78_BINDING_REVOKED")
        if len(active) != 1:
            _fail("G78_BINDING_CURRENTNESS_INVALID")
        return active[0]


class CanonicalMatterAssignmentSource:
    """Filter canonical assignment-registry currentness to exact matter scope."""

    def __init__(self, registry: Any) -> None:
        self._registry = registry

    def resolve_current(
        self, *, tenant_id: str, case_matter_id: str,
        practitioner_principal_id: str, session: object,
    ) -> tuple[LegalWorkAssignment, ...]:
        """Return current assignments for this principal and exact matter."""
        tx = _tx(session)
        tenant, matter, principal = _id(tenant_id), _id(case_matter_id), _id(practitioner_principal_id)
        try:
            values = self._registry.list_current_for_assignee(
                tenant, principal, session=tx,
            )
        except Exception as error:
            _fail("G78_ASSIGNMENT_SOURCE_UNAVAILABLE", error)
        if type(values) is not tuple or any(type(item) is not LegalWorkAssignment for item in values):
            _fail("G78_ASSIGNMENT_INVALID")
        selected = tuple(item for item in values if item.case_matter_id == matter)
        if not selected:
            _fail("G78_ASSIGNMENT_NOT_FOUND")
        if any(item.tenant_id != tenant or item.assignee_principal_id != principal for item in selected):
            _fail("G78_ASSIGNMENT_SCOPE_INVALID")
        return selected


class CanonicalConflictDispositionSource:
    """Delegate conflict history and projection to the existing canonical composer."""

    def __init__(
        self, *, disposition_collection: object, matter_fingerprint: str,
        client_party_id: str, subject_identity_fingerprint: str,
        evaluation_time: datetime,
    ) -> None:
        self._composer = LegalClientMatterConflictDispositionCurrentnessComposer(
            disposition_collection=disposition_collection,
        )
        self._matter_fingerprint = _id(matter_fingerprint)
        self._client_party_id = _id(client_party_id)
        self._subject_fingerprint = _id(subject_identity_fingerprint)
        self._evaluation_time = _at(evaluation_time)

    def resolve_current(
        self, *, tenant_id: str, case_matter_id: str,
        practitioner_principal_id: str, session: object,
    ) -> object:
        """Return canonical conflict currentness for the bound matter subject."""
        tx = _tx(session)
        _id(practitioner_principal_id)
        try:
            return self._composer.compose_currentness(
                _id(tenant_id), _id(case_matter_id), self._matter_fingerprint,
                self._client_party_id, self._subject_fingerprint,
                self._evaluation_time, tx,
            )
        except Exception as error:
            _fail("G78_CONFLICT_SOURCE_UNAVAILABLE", error)


_REVIEW_FIELDS: Final[tuple[str, ...]] = tuple(
    item.name for item in fields(ConfidentialityReviewDecision)
)
_REVIEW_INPUTS: Final[tuple[str, ...]] = tuple(
    name for name in _REVIEW_FIELDS if name != "fingerprint"
)


def encode_confidentiality_review(value: ConfidentialityReviewDecision) -> dict[str, object]:
    """Encode one canonical immutable review for strict Mongo persistence."""
    if type(value) is not ConfidentialityReviewDecision:
        _fail("G78_REVIEW_INVALID")
    try:
        canonical = replace(value)
    except Exception as error:
        _fail("G78_REVIEW_INVALID", error)
    if canonical != value:
        _fail("G78_REVIEW_INVALID")
    return {name: getattr(value, name) for name in _REVIEW_FIELDS}


def _decode_review(raw: object) -> ConfidentialityReviewDecision:
    if type(raw) is not dict:
        _fail("G78_REVIEW_INVALID")
    document = dict(raw)
    document.pop("_id", None)
    if set(document) != set(_REVIEW_FIELDS):
        _fail("G78_REVIEW_INVALID")
    try:
        value = ConfidentialityReviewDecision(
            **{name: document[name] for name in _REVIEW_INPUTS}
        )
    except Exception as error:
        _fail("G78_REVIEW_INVALID", error)
    if value.fingerprint != document["fingerprint"]:
        _fail("G78_REVIEW_INVALID")
    return value


class CanonicalConfidentialityReviewSource:
    """Hydrate and project exact practitioner review history."""

    def __init__(self, collection: Any, evaluation_time: datetime) -> None:
        self._collection = collection
        self._evaluation_time = _at(evaluation_time)

    def resolve_current(
        self, *, tenant_id: str, case_matter_id: str,
        practitioner_principal_id: str, session: object,
    ) -> ConfidentialityReviewDecision:
        """Return only the canonical current approved review evidence."""
        tx = _tx(session)
        scope = {
            "tenant_id": _id(tenant_id), "case_matter_id": _id(case_matter_id),
            "practitioner_principal_id": _id(practitioner_principal_id),
        }
        try:
            rows = tuple(self._collection.find(scope, session=tx).limit(MAX_REVIEW_HISTORY + 1))
        except Exception as error:
            _fail("G78_REVIEW_SOURCE_UNAVAILABLE", error)
        if not rows or len(rows) > MAX_REVIEW_HISTORY:
            _fail("G78_REVIEW_NOT_FOUND")
        history = tuple(_decode_review(row) for row in rows)
        projection = project_confidentiality_review_currentness(
            **scope, evaluation_time=self._evaluation_time, decisions=history,
        )
        if projection.state is not ConfidentialityReviewCurrentnessState.APPROVED_RECORDED_UNVERIFIED:
            _fail("G78_REVIEW_NOT_CURRENT")
        current = max(
            (item for item in history if item.decided_at <= self._evaluation_time),
            key=lambda item: item.decided_at,
        )
        if current.decision is not ConfidentialityReviewDecisionState.APPROVED:
            _fail("G78_REVIEW_NOT_CURRENT")
        return current


class CanonicalEthicalWallPolicySource:
    """Expose only G76-B currentness and immutable history reads."""

    def __init__(self, registry: Any) -> None:
        self._registry = registry

    def get_current(
        self, tenant_id: str, case_matter_id: str, policy_id: str, *, session: object,
    ) -> object:
        """Delegate exact current-pointer resolution to G76-B."""
        return self._registry.get_current(
            _id(tenant_id), _id(case_matter_id), _id(policy_id), session=_tx(session),
        )

    def list_history(
        self, tenant_id: str, case_matter_id: str, policy_id: str, *, session: object,
    ) -> object:
        """Delegate exact immutable history validation to G76-B."""
        return self._registry.list_history(
            _id(tenant_id), _id(case_matter_id), _id(policy_id), session=_tx(session),
        )


__all__ = [
    "VERSION", "SOURCE_VERIFIED_CLEARANCE", "OPERATIONAL_ACCESS_ENABLED",
    "EthicalWallSourceUnavailable", "CanonicalTenantIamSource",
    "CanonicalPractitionerBindingSource", "CanonicalMatterAssignmentSource",
    "CanonicalConflictDispositionSource", "CanonicalConfidentialityReviewSource",
    "CanonicalEthicalWallPolicySource", "encode_confidentiality_review",
]

# ARTIFACT: legal_work_ethical_wall_source_adapters.py
# VERSION: v1.0.0-G78-CANONICAL-TRANSACTIONAL-SOURCE-ADAPTERS
# AUTHORITY BOUNDARY: canonical evidence reads only; no content or access grant
# TENANT POSTURE: exact tenant/matter/practitioner on every operation
# FAIL-CLOSED POSTURE: missing, revoked, stale, corrupt or foreign source rejects
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively
# END OF WILSY OS SOVEREIGN ARTIFACT
