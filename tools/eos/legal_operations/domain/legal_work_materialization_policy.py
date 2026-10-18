"""
WILSY OS — Legal Workflow Work-Materialization Policy Domain

TITLE: Legal Workflow Work-Materialization Policy Domain
VERSION: v1.0.0-P14-P7-WORK-MATERIALIZATION-POLICY
AUTHORITY: Wilsy OS Core Governance / Python EOS Legal Operations
EPITOME:
    Immutable policy truth describing which operational Legal work templates
    are eligible to materialize when one certified workflow transition reaches
    one exact target workflow stage.

    This artifact deliberately separates work-materialization description from
    assignment, supervision, IAM, professional authority, legal-deadline truth,
    notification delivery, AI execution and financial execution.

COMPETITIVE POSTURE:
    Supports stage-triggered multi-work policy, dependency DAGs, relative
    operational due offsets, stage re-entry through distinct transition
    provenance, and opaque materialization-condition references while retaining
    immutable evidence coordinates and fail-closed authority separation.

TENANT BOUNDARY:
    Exact non-pseudo tenant identity is mandatory.

AUTHORITY BOUNDARY:
    Descriptive immutable work-materialization policy only. A policy does not
    itself create a LegalWorkItem, assign or supervise a principal, grant IAM,
    establish professional qualification, calculate a legal deadline, deliver
    a notification, invoke AI, or execute a financial transaction.

TRANSACTION BOUNDARY:
    Pure immutable domain construction, serialization and strict hydration.
    No persistence, network, clock or transaction lifecycle behavior.

FINANCIAL AUTHORITY BOUNDARY:
    None. Kennel EOS remains exclusive for financial execution.

FAIL-CLOSED DECLARATION:
    Malformed identity, pseudo tenant, invalid revision, fingerprint drift,
    duplicate work-template identity, unresolved/self/cyclic dependency,
    invalid due semantics, duplicate/malformed condition reference, schema
    drift or corrupt hydrated fingerprint rejects.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum
from hashlib import sha3_512
import hmac
import json
import re
from typing import Final, Mapping, NoReturn, cast


VERSION: Final[str] = (
    "v1.0.0-P14-P7-WORK-MATERIALIZATION-POLICY"
)
SCHEMA: Final[str] = (
    "WILSY-LEGAL-WORK-MATERIALIZATION-POLICY/V1"
)

_TEMPLATE_SCHEMA: Final[str] = (
    "WILSY-LEGAL-WORK-MATERIALIZATION-TEMPLATE/V1"
)

_IDENTITY: Final[re.Pattern[str]] = re.compile(
    r"^[A-Za-z0-9][A-Za-z0-9._:/-]{0,255}$"
)
_HEX_128: Final[re.Pattern[str]] = re.compile(
    r"^[0-9a-f]{128}$"
)

_FORBIDDEN_TENANTS: Final[frozenset[str]] = frozenset(
    {
        "default",
        "global",
        "global_root",
        "root",
        "master",
        "*",
    }
)


class LegalWorkMaterializationPolicyError(ValueError):
    """Stable fail-closed domain validation error."""

    def __init__(self, code: str) -> None:
        self.code = code
        super().__init__(code)


def _fail(code: str) -> NoReturn:
    raise LegalWorkMaterializationPolicyError(code)


def _text(
    name: str,
    value: object,
    *,
    limit: int = 512,
    identity: bool = False,
) -> str:
    if not isinstance(value, str):
        _fail(f"P14_P7_{name.upper()}_INVALID")

    if (
        not value
        or value != value.strip()
        or len(value) > limit
    ):
        _fail(f"P14_P7_{name.upper()}_INVALID")

    if identity and _IDENTITY.fullmatch(value) is None:
        _fail(f"P14_P7_{name.upper()}_INVALID")

    return value


def _tenant(value: object) -> str:
    tenant = _text(
        "tenant_id",
        value,
        limit=160,
        identity=True,
    )

    if tenant.casefold() in _FORBIDDEN_TENANTS:
        _fail("P14_P7_TENANT_ID_INVALID")

    return tenant


def _positive_integer(
    name: str,
    value: object,
) -> int:
    if (
        isinstance(value, bool)
        or not isinstance(value, int)
        or value <= 0
    ):
        _fail(f"P14_P7_{name.upper()}_INVALID")

    return value


def _hex_fingerprint(
    name: str,
    value: object,
) -> str:
    if (
        not isinstance(value, str)
        or _HEX_128.fullmatch(value) is None
    ):
        _fail(f"P14_P7_{name.upper()}_FINGERPRINT_INVALID")

    return value


def _optional_fingerprint(
    name: str,
    value: object,
) -> str | None:
    if value is None:
        return None

    return _hex_fingerprint(name, value)


def _exact_reference(
    name: str,
    value: object,
) -> str:
    return _text(
        name,
        value,
        limit=512,
        identity=False,
    )


def _exact_tuple(
    name: str,
    value: object,
) -> tuple[str, ...]:
    if not isinstance(value, (tuple, list)):
        _fail(f"P14_P7_{name.upper()}_INVALID")

    normalized = tuple(
        _exact_reference(name, entry)
        for entry in value
    )

    if len(set(normalized)) != len(normalized):
        _fail(f"P14_P7_{name.upper()}_DUPLICATE")

    return normalized


class LegalOperationalDueRule(StrEnum):
    """
    Closed operational due-rule vocabulary.

    TRANSITION_OFFSET is an operational scheduling offset only. It is not a
    court-rule, statutory-period or other legal-deadline calculation.
    """

    NONE = "NONE"
    TRANSITION_OFFSET = "TRANSITION_OFFSET"


@dataclass(frozen=True, slots=True)
class LegalWorkMaterializationTemplate:
    """One immutable work template embedded in a materialization policy."""

    work_template_id: str
    title: str
    due_rule: LegalOperationalDueRule | str
    due_offset_seconds: int | None
    dependency_template_ids: tuple[str, ...]
    condition_references: tuple[str, ...]

    def __post_init__(self) -> None:
        template_id = _text(
            "work_template_id",
            self.work_template_id,
            limit=160,
            identity=True,
        )

        title = _text(
            "title",
            self.title,
            limit=512,
        )

        try:
            due_rule = LegalOperationalDueRule(
                self.due_rule
            )
        except (TypeError, ValueError) as error:
            raise LegalWorkMaterializationPolicyError(
                "P14_P7_DUE_RULE_INVALID"
            ) from error

        offset = self.due_offset_seconds

        if (
            due_rule
            is LegalOperationalDueRule.TRANSITION_OFFSET
        ):
            if (
                isinstance(offset, bool)
                or not isinstance(offset, int)
                or offset <= 0
            ):
                _fail(
                    "P14_P7_DUE_OFFSET_INVALID"
                )
        else:
            if offset is not None:
                _fail(
                    "P14_P7_DUE_OFFSET_NOT_ALLOWED"
                )

        dependencies = _exact_tuple(
            "dependency_template_ids",
            self.dependency_template_ids,
        )

        if template_id in dependencies:
            _fail(
                "P14_P7_DEPENDENCY_SELF_REFERENCE"
            )

        conditions = _exact_tuple(
            "condition_references",
            self.condition_references,
        )

        object.__setattr__(
            self,
            "work_template_id",
            template_id,
        )
        object.__setattr__(
            self,
            "title",
            title,
        )
        object.__setattr__(
            self,
            "due_rule",
            due_rule,
        )
        object.__setattr__(
            self,
            "due_offset_seconds",
            offset,
        )
        object.__setattr__(
            self,
            "dependency_template_ids",
            dependencies,
        )
        object.__setattr__(
            self,
            "condition_references",
            conditions,
        )

    def to_dict(self) -> dict[str, object]:
        """Serialize the exact immutable template contract."""
        return {
            "schema": _TEMPLATE_SCHEMA,
            "work_template_id":
                self.work_template_id,
            "title":
                self.title,
            "due_rule":
                LegalOperationalDueRule(
                    self.due_rule
                ).value,
            "due_offset_seconds":
                self.due_offset_seconds,
            "dependency_template_ids":
                list(
                    self.dependency_template_ids
                ),
            "condition_references":
                list(
                    self.condition_references
                ),
        }

    @classmethod
    def from_dict(
        cls,
        value: object,
    ) -> "LegalWorkMaterializationTemplate":
        """Strictly hydrate one immutable embedded template."""
        if not isinstance(value, Mapping):
            _fail(
                "P14_P7_TEMPLATE_SCHEMA_INVALID"
            )

        required = {
            "schema",
            "work_template_id",
            "title",
            "due_rule",
            "due_offset_seconds",
            "dependency_template_ids",
            "condition_references",
        }

        if set(value) != required:
            _fail(
                "P14_P7_TEMPLATE_SCHEMA_INVALID"
            )

        if value["schema"] != _TEMPLATE_SCHEMA:
            _fail(
                "P14_P7_TEMPLATE_SCHEMA_INVALID"
            )

        dependencies = value[
            "dependency_template_ids"
        ]
        conditions = value[
            "condition_references"
        ]

        if not isinstance(
            dependencies,
            (tuple, list),
        ):
            _fail(
                "P14_P7_DEPENDENCY_TEMPLATE_IDS_INVALID"
            )

        if not isinstance(
            conditions,
            (tuple, list),
        ):
            _fail(
                "P14_P7_CONDITION_REFERENCES_INVALID"
            )

        return cls(
            work_template_id=cast(
                str,
                value["work_template_id"],
            ),
            title=cast(
                str,
                value["title"],
            ),
            due_rule=cast(
                str,
                value["due_rule"],
            ),
            due_offset_seconds=cast(
                int | None,
                value["due_offset_seconds"],
            ),
            dependency_template_ids=tuple(
                cast(
                    list[str] | tuple[str, ...],
                    dependencies,
                )
            ),
            condition_references=tuple(
                cast(
                    list[str] | tuple[str, ...],
                    conditions,
                )
            ),
        )


@dataclass(frozen=True, slots=True)
class LegalWorkMaterializationPolicy:
    """
    Immutable workflow-stage to operational-work materialization policy.

    The policy is declarative only. It creates no work item itself and contains
    no assignee, supervisor, IAM, professional, legal-deadline, notification,
    AI-execution or financial authority.
    """

    tenant_id: str
    policy_id: str
    policy_revision: int

    workflow_definition_id: str
    workflow_definition_fingerprint: str

    target_stage_definition_id: str
    target_stage_fingerprint: str

    templates: tuple[
        LegalWorkMaterializationTemplate,
        ...,
    ]

    supersedes_fingerprint: str | None = None

    schema: str = SCHEMA
    policy_version: str = VERSION
    fingerprint: str = ""

    def __post_init__(self) -> None:
        tenant = _tenant(
            self.tenant_id
        )

        policy_id = _text(
            "policy_id",
            self.policy_id,
            limit=160,
            identity=True,
        )

        revision = _positive_integer(
            "policy_revision",
            self.policy_revision,
        )

        workflow_definition_id = _text(
            "workflow_definition_id",
            self.workflow_definition_id,
            limit=160,
            identity=True,
        )

        workflow_definition_fingerprint = (
            _hex_fingerprint(
                "workflow_definition",
                self.workflow_definition_fingerprint,
            )
        )

        target_stage_definition_id = _text(
            "target_stage_definition_id",
            self.target_stage_definition_id,
            limit=160,
            identity=True,
        )

        target_stage_fingerprint = (
            _hex_fingerprint(
                "target_stage",
                self.target_stage_fingerprint,
            )
        )

        if (
            not isinstance(self.templates, tuple)
            or not self.templates
        ):
            _fail(
                "P14_P7_TEMPLATES_REQUIRED"
            )

        templates: tuple[
            LegalWorkMaterializationTemplate,
            ...,
        ] = tuple(
            self.templates
        )

        if any(
            type(template)
            is not LegalWorkMaterializationTemplate
            for template in templates
        ):
            _fail(
                "P14_P7_TEMPLATE_INVALID"
            )

        template_ids = tuple(
            template.work_template_id
            for template in templates
        )

        if len(set(template_ids)) != len(
            template_ids
        ):
            _fail(
                "P14_P7_TEMPLATE_ID_DUPLICATE"
            )

        known_template_ids = set(
            template_ids
        )

        for template in templates:
            for dependency in (
                template.dependency_template_ids
            ):
                if dependency not in known_template_ids:
                    _fail(
                        "P14_P7_DEPENDENCY_UNKNOWN"
                    )

        self._validate_dependency_dag(
            templates
        )

        supersedes = _optional_fingerprint(
            "supersedes",
            self.supersedes_fingerprint,
        )

        if self.schema != SCHEMA:
            _fail(
                "P14_P7_SCHEMA_INVALID"
            )

        if self.policy_version != VERSION:
            _fail(
                "P14_P7_VERSION_INVALID"
            )

        object.__setattr__(
            self,
            "tenant_id",
            tenant,
        )
        object.__setattr__(
            self,
            "policy_id",
            policy_id,
        )
        object.__setattr__(
            self,
            "policy_revision",
            revision,
        )
        object.__setattr__(
            self,
            "workflow_definition_id",
            workflow_definition_id,
        )
        object.__setattr__(
            self,
            "workflow_definition_fingerprint",
            workflow_definition_fingerprint,
        )
        object.__setattr__(
            self,
            "target_stage_definition_id",
            target_stage_definition_id,
        )
        object.__setattr__(
            self,
            "target_stage_fingerprint",
            target_stage_fingerprint,
        )
        object.__setattr__(
            self,
            "templates",
            templates,
        )
        object.__setattr__(
            self,
            "supersedes_fingerprint",
            supersedes,
        )

        digest = self._compute_fingerprint()

        if self.fingerprint:
            supplied = _hex_fingerprint(
                "policy",
                self.fingerprint,
            )

            if not hmac.compare_digest(
                supplied,
                digest,
            ):
                _fail(
                    "P14_P7_FINGERPRINT_MISMATCH"
                )

        object.__setattr__(
            self,
            "fingerprint",
            digest,
        )

    @staticmethod
    def _validate_dependency_dag(
        templates: tuple[
            LegalWorkMaterializationTemplate,
            ...,
        ],
    ) -> None:
        dependencies = {
            template.work_template_id:
                template.dependency_template_ids
            for template in templates
        }

        visiting: set[str] = set()
        visited: set[str] = set()

        def visit(
            template_id: str,
        ) -> None:
            if template_id in visiting:
                _fail(
                    "P14_P7_DEPENDENCY_CYCLE"
                )

            if template_id in visited:
                return

            visiting.add(
                template_id
            )

            for dependency in dependencies[
                template_id
            ]:
                visit(
                    dependency
                )

            visiting.remove(
                template_id
            )
            visited.add(
                template_id
            )

        for template_id in dependencies:
            visit(
                template_id
            )

    def semantic_dict(
        self,
    ) -> dict[str, object]:
        """Return exact semantic policy truth used for fingerprinting."""
        return {
            "schema":
                self.schema,
            "policy_version":
                self.policy_version,
            "tenant_id":
                self.tenant_id,
            "policy_id":
                self.policy_id,
            "policy_revision":
                self.policy_revision,
            "workflow_definition_id":
                self.workflow_definition_id,
            "workflow_definition_fingerprint":
                self.workflow_definition_fingerprint,
            "target_stage_definition_id":
                self.target_stage_definition_id,
            "target_stage_fingerprint":
                self.target_stage_fingerprint,
            "templates": [
                template.to_dict()
                for template in self.templates
            ],
            "supersedes_fingerprint":
                self.supersedes_fingerprint,
        }

    def _compute_fingerprint(
        self,
    ) -> str:
        canonical = json.dumps(
            self.semantic_dict(),
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=False,
            allow_nan=False,
        )

        return sha3_512(
            canonical.encode("utf-8")
        ).hexdigest()

    def to_dict(
        self,
    ) -> dict[str, object]:
        """Serialize exact immutable policy truth with integrity digest."""
        return {
            **self.semantic_dict(),
            "fingerprint":
                self.fingerprint,
        }

    @classmethod
    def from_dict(
        cls,
        value: object,
    ) -> "LegalWorkMaterializationPolicy":
        """Strictly hydrate exact persisted policy truth."""
        if not isinstance(value, Mapping):
            _fail(
                "P14_P7_SCHEMA_INVALID"
            )

        required = {
            "schema",
            "policy_version",
            "tenant_id",
            "policy_id",
            "policy_revision",
            "workflow_definition_id",
            "workflow_definition_fingerprint",
            "target_stage_definition_id",
            "target_stage_fingerprint",
            "templates",
            "supersedes_fingerprint",
            "fingerprint",
        }

        if set(value) != required:
            _fail(
                "P14_P7_SCHEMA_INVALID"
            )

        if value["schema"] != SCHEMA:
            _fail(
                "P14_P7_SCHEMA_INVALID"
            )

        if value["policy_version"] != VERSION:
            _fail(
                "P14_P7_VERSION_INVALID"
            )

        raw_templates = value[
            "templates"
        ]

        if not isinstance(
            raw_templates,
            (tuple, list),
        ):
            _fail(
                "P14_P7_SCHEMA_INVALID"
            )

        templates = tuple(
            LegalWorkMaterializationTemplate.from_dict(
                entry
            )
            for entry in raw_templates
        )

        return cls(
            tenant_id=cast(
                str,
                value["tenant_id"],
            ),
            policy_id=cast(
                str,
                value["policy_id"],
            ),
            policy_revision=cast(
                int,
                value["policy_revision"],
            ),
            workflow_definition_id=cast(
                str,
                value["workflow_definition_id"],
            ),
            workflow_definition_fingerprint=cast(
                str,
                value[
                    "workflow_definition_fingerprint"
                ],
            ),
            target_stage_definition_id=cast(
                str,
                value["target_stage_definition_id"],
            ),
            target_stage_fingerprint=cast(
                str,
                value["target_stage_fingerprint"],
            ),
            templates=templates,
            supersedes_fingerprint=cast(
                str | None,
                value["supersedes_fingerprint"],
            ),
            schema=cast(
                str,
                value["schema"],
            ),
            policy_version=cast(
                str,
                value["policy_version"],
            ),
            fingerprint=cast(
                str,
                value["fingerprint"],
            ),
        )


__all__ = [
    "SCHEMA",
    "VERSION",
    "LegalOperationalDueRule",
    "LegalWorkMaterializationPolicy",
    "LegalWorkMaterializationPolicyError",
    "LegalWorkMaterializationTemplate",
]


# ==============================================================================
# WILSY OS SOVEREIGN ARTIFACT SEAL
# ==============================================================================
# ARTIFACT: legal_work_materialization_policy.py
# VERSION: v1.0.0-P14-P7-WORK-MATERIALIZATION-POLICY
# AUTHORITY BOUNDARY: immutable descriptive workflow-to-work policy only
# COMPETITIVE BASELINE: multi-work, dependency DAG, relative operational due
# TENANT POSTURE: exact non-pseudo tenant correlation
# WORK-ITEM CREATION AUTHORITY: NONE
# ASSIGNMENT AUTHORITY: NONE
# SUPERVISION AUTHORITY: NONE
# IAM / PROFESSIONAL AUTHORITY: NONE
# LEGAL-DEADLINE AUTHORITY: NONE
# NOTIFICATION-DELIVERY AUTHORITY: NONE
# AI EXECUTION AUTHORITY: NONE
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively
# TRANSACTION / PERSISTENCE AUTHORITY: NONE
# END OF WILSY OS SOVEREIGN ARTIFACT
