"""TITLE: WILSY OS Legal Workflow Definition Domain.

VERSION: v1.0.1-G7G-R2-LEGAL-WORKFLOW-DEFINITION

AUTHORITY:
    Wilsy OS Core Governance / Python EOS Legal Operations.

EPITOME:
    Preserve one immutable, versioned Legal workflow-definition header that
    identifies a reusable operating process without creating workflow-instance,
    stage, work-item, assignment, supervision, IAM, entitlement, legal-event,
    billing, payment, settlement, or financial-execution authority.

OWNERSHIP MODEL:
    PLATFORM definitions are reusable WILSY-supplied operating blueprints and
    have no owner_tenant_id.

    TENANT definitions are tenant-owned immutable operating blueprints and
    require one exact non-pseudo owner_tenant_id.

    Tenant activation is a separate future authority that determines which
    definition/version a tenant may use.

APPLICABILITY MODEL:
    required_operating_item_ids reference the immutable G7A Legal operating
    catalogue and express descriptive/configuration applicability only.

    jurisdiction_references are opaque, explicit jurisdiction-overlay
    references. This domain does not interpret law, calculate legal dates,
    select governing law, or create jurisdictional authority.

VERSIONING:
    definition_revision is a positive integer. Definitions are immutable.
    Active matter workflow instances must later pin the exact definition
    identity, revision, and fingerprint.

STAGE BOUNDARY:
    This artifact deliberately owns no stages, transitions, conditions,
    completion gates, work generation, branching, or automation actions.
    Those belong to separately certified artifacts.

COMMERCIAL BOUNDARY:
    No plan, subscription, entitlement, price, quota, or commercial ownership
    truth is created here.

AUTHORITY BOUNDARY:
    Workflow configuration is not IAM, legal-event authority, professional
    authority, assignment authority, or supervision authority.

FINANCIAL AUTHORITY:
    None. Kennel EOS remains exclusive financial execution authority.
"""
from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum
from hashlib import sha3_512
import hmac
import json
from typing import Final, NoReturn

from tools.eos.legal_operations.domain.legal_operating_catalogue import (
    CATALOGUE_FINGERPRINT,
    LegalOperatingCatalogueError,
    get_legal_operating_item,
)


VERSION: Final[str] = (
    "v1.0.1-G7G-R2-LEGAL-WORKFLOW-DEFINITION"
)
SCHEMA: Final[str] = (
    "WILSY-LEGAL-WORKFLOW-DEFINITION/V1"
)


class LegalWorkflowDefinitionError(ValueError):
    """Stable fail-closed workflow-definition validation failure."""

    def __init__(self, code: str) -> None:
        self.code = code
        super().__init__(code)


class LegalWorkflowDefinitionOwner(StrEnum):
    """Immutable ownership namespace for one definition."""

    PLATFORM = "PLATFORM"
    TENANT = "TENANT"


def _fail(code: str) -> NoReturn:
    raise LegalWorkflowDefinitionError(code)


def _text(
    name: str,
    value: object,
    *,
    limit: int = 320,
) -> str:
    if not isinstance(value, str):
        _fail(f"G7G_R2_{name.upper()}_INVALID")

    normalized = value.strip()

    if (
        not normalized
        or normalized != value
        or len(normalized) > limit
    ):
        _fail(f"G7G_R2_{name.upper()}_INVALID")

    return normalized


def _tenant(
    value: object,
) -> str:
    tenant = _text(
        "owner_tenant_id",
        value,
        limit=160,
    )

    if tenant.casefold() in {
        "default",
        "global",
        "root",
        "*",
    }:
        _fail("G7G_R2_OWNER_TENANT_INVALID")

    return tenant


def _revision(value: object) -> int:
    if (
        isinstance(value, bool)
        or not isinstance(value, int)
        or value < 1
    ):
        _fail(
            "G7G_R2_DEFINITION_REVISION_INVALID"
        )

    return value


def _catalogue_items(
    value: object,
) -> tuple[str, ...]:
    if not isinstance(value, tuple):
        _fail(
            "G7G_R2_REQUIRED_OPERATING_ITEMS_INVALID"
        )

    result: list[str] = []
    seen: set[str] = set()

    for raw in value:
        item_id = _text(
            "required_operating_item_id",
            raw,
            limit=160,
        )

        if item_id in seen:
            _fail(
                "G7G_R2_REQUIRED_OPERATING_ITEM_DUPLICATE"
            )

        try:
            get_legal_operating_item(item_id)
        except LegalOperatingCatalogueError as error:
            raise LegalWorkflowDefinitionError(
                "G7G_R2_REQUIRED_OPERATING_ITEM_UNKNOWN"
            ) from error

        seen.add(item_id)
        result.append(item_id)

    return tuple(result)


def _jurisdictions(
    value: object,
) -> tuple[str, ...]:
    if not isinstance(value, tuple):
        _fail(
            "G7G_R2_JURISDICTION_REFERENCES_INVALID"
        )

    result: list[str] = []
    seen: set[str] = set()

    for raw in value:
        reference = _text(
            "jurisdiction_reference",
            raw,
            limit=240,
        )

        if reference in seen:
            _fail(
                "G7G_R2_JURISDICTION_REFERENCE_DUPLICATE"
            )

        seen.add(reference)
        result.append(reference)

    return tuple(result)


def _catalogue_fingerprint(
    value: object,
) -> str:
    if (
        not isinstance(value, str)
        or len(value) != 128
        or value.lower() != value
    ):
        _fail(
            "G7G_R2_CATALOGUE_FINGERPRINT_INVALID"
        )

    try:
        int(value, 16)
    except ValueError as error:
        raise LegalWorkflowDefinitionError(
            "G7G_R2_CATALOGUE_FINGERPRINT_INVALID"
        ) from error

    if not hmac.compare_digest(
        value,
        CATALOGUE_FINGERPRINT,
    ):
        _fail(
            "G7G_R2_CATALOGUE_BINDING_INVALID"
        )

    return value


@dataclass(frozen=True, slots=True)
class LegalWorkflowDefinition:
    """One immutable Legal operating workflow-definition header."""

    workflow_definition_id: str
    definition_revision: int

    owner: LegalWorkflowDefinitionOwner | str
    owner_tenant_id: str | None

    name: str
    description_reference: str

    required_operating_item_ids: tuple[str, ...]
    jurisdiction_references: tuple[str, ...]

    catalogue_fingerprint: str = CATALOGUE_FINGERPRINT

    schema: str = SCHEMA
    workflow_definition_version: str = VERSION
    fingerprint: str = ""

    def __post_init__(self) -> None:
        definition_id = _text(
            "workflow_definition_id",
            self.workflow_definition_id,
            limit=160,
        )

        revision = _revision(
            self.definition_revision
        )

        try:
            owner = LegalWorkflowDefinitionOwner(
                self.owner
            )
        except (TypeError, ValueError) as error:
            raise LegalWorkflowDefinitionError(
                "G7G_R2_OWNER_INVALID"
            ) from error

        owner_tenant_id = self.owner_tenant_id

        if owner is LegalWorkflowDefinitionOwner.PLATFORM:
            if owner_tenant_id is not None:
                _fail(
                    "G7G_R2_PLATFORM_OWNER_FORBIDS_TENANT"
                )
        else:
            if owner_tenant_id is None:
                _fail(
                    "G7G_R2_TENANT_OWNER_REQUIRES_TENANT"
                )

            owner_tenant_id = _tenant(
                owner_tenant_id
            )

        name = _text(
            "name",
            self.name,
            limit=240,
        )

        description_reference = _text(
            "description_reference",
            self.description_reference,
            limit=320,
        )

        operating_items = _catalogue_items(
            self.required_operating_item_ids
        )

        jurisdictions = _jurisdictions(
            self.jurisdiction_references
        )

        catalogue_fingerprint = (
            _catalogue_fingerprint(
                self.catalogue_fingerprint
            )
        )

        if (
            self.schema != SCHEMA
            or self.workflow_definition_version
            != VERSION
        ):
            _fail(
                "G7G_R2_IDENTITY_INVALID"
            )

        object.__setattr__(
            self,
            "workflow_definition_id",
            definition_id,
        )
        object.__setattr__(
            self,
            "definition_revision",
            revision,
        )
        object.__setattr__(
            self,
            "owner",
            owner,
        )
        object.__setattr__(
            self,
            "owner_tenant_id",
            owner_tenant_id,
        )
        object.__setattr__(
            self,
            "name",
            name,
        )
        object.__setattr__(
            self,
            "description_reference",
            description_reference,
        )
        object.__setattr__(
            self,
            "required_operating_item_ids",
            operating_items,
        )
        object.__setattr__(
            self,
            "jurisdiction_references",
            jurisdictions,
        )
        object.__setattr__(
            self,
            "catalogue_fingerprint",
            catalogue_fingerprint,
        )

        digest = self._compute_fingerprint()

        if self.fingerprint:
            supplied = _text(
                "fingerprint",
                self.fingerprint,
                limit=128,
            )

            if (
                len(supplied) != 128
                or supplied.lower() != supplied
            ):
                _fail(
                    "G7G_R2_FINGERPRINT_INVALID"
                )

            try:
                int(supplied, 16)
            except ValueError as error:
                raise LegalWorkflowDefinitionError(
                    "G7G_R2_FINGERPRINT_INVALID"
                ) from error

            if not hmac.compare_digest(
                supplied,
                digest,
            ):
                _fail(
                    "G7G_R2_FINGERPRINT_MISMATCH"
                )

        object.__setattr__(
            self,
            "fingerprint",
            digest,
        )

    def semantic_dict(
        self,
    ) -> dict[str, object]:
        return {
            "schema":
                self.schema,
            "workflow_definition_version":
                self.workflow_definition_version,
            "workflow_definition_id":
                self.workflow_definition_id,
            "definition_revision":
                self.definition_revision,
            "owner":
                LegalWorkflowDefinitionOwner(
                    self.owner
                ).value,
            "owner_tenant_id":
                self.owner_tenant_id,
            "name":
                self.name,
            "description_reference":
                self.description_reference,
            "required_operating_item_ids":
                list(
                    self.required_operating_item_ids
                ),
            "jurisdiction_references":
                list(
                    self.jurisdiction_references
                ),
            "catalogue_fingerprint":
                self.catalogue_fingerprint,
        }

    def _compute_fingerprint(
        self,
    ) -> str:
        canonical = json.dumps(
            self.semantic_dict(),
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=False,
        )

        return sha3_512(
            canonical.encode("utf-8")
        ).hexdigest()

    def to_dict(
        self,
    ) -> dict[str, object]:
        return {
            **self.semantic_dict(),
            "fingerprint":
                self.fingerprint,
        }

    @classmethod
    def from_dict(
        cls,
        value: object,
    ) -> "LegalWorkflowDefinition":
        if not isinstance(value, dict):
            _fail(
                "G7G_R2_PAYLOAD_INVALID"
            )

        required = {
            "schema",
            "workflow_definition_version",
            "workflow_definition_id",
            "definition_revision",
            "owner",
            "owner_tenant_id",
            "name",
            "description_reference",
            "required_operating_item_ids",
            "jurisdiction_references",
            "catalogue_fingerprint",
            "fingerprint",
        }

        if set(value) != required:
            _fail(
                "G7G_R2_PAYLOAD_SCHEMA_INVALID"
            )

        raw_items = value[
            "required_operating_item_ids"
        ]
        raw_jurisdictions = value[
            "jurisdiction_references"
        ]

        if not isinstance(raw_items, list):
            _fail(
                "G7G_R2_REQUIRED_OPERATING_ITEMS_INVALID"
            )

        if not isinstance(
            raw_jurisdictions,
            list,
        ):
            _fail(
                "G7G_R2_JURISDICTION_REFERENCES_INVALID"
            )

        return cls(
            schema=value["schema"],
            workflow_definition_version=value[
                "workflow_definition_version"
            ],
            workflow_definition_id=value[
                "workflow_definition_id"
            ],
            definition_revision=value[
                "definition_revision"
            ],
            owner=value["owner"],
            owner_tenant_id=value[
                "owner_tenant_id"
            ],
            name=value["name"],
            description_reference=value[
                "description_reference"
            ],
            required_operating_item_ids=tuple(
                raw_items
            ),
            jurisdiction_references=tuple(
                raw_jurisdictions
            ),
            catalogue_fingerprint=value[
                "catalogue_fingerprint"
            ],
            fingerprint=value[
                "fingerprint"
            ],
        )


__all__ = [
    "SCHEMA",
    "VERSION",
    "LegalWorkflowDefinition",
    "LegalWorkflowDefinitionError",
    "LegalWorkflowDefinitionOwner",
]

# ARTIFACT: legal_workflow_definition.py
# VERSION: v1.0.1-G7G-R2-LEGAL-WORKFLOW-DEFINITION
# AUTHORITY BOUNDARY: immutable workflow configuration header only
# WORKFLOW NOT IAM: YES
# WORKFLOW NOT LEGAL EVENT: YES
# STAGE AUTHORITY: NONE
# ASSIGNMENT AUTHORITY: NONE
# SUPERVISION AUTHORITY: NONE
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively
# TENANT POSTURE: exact tenant correlation; cross-tenant inference prohibited
# FAIL-CLOSED POSTURE: malformed, incomplete, or divergent evidence rejects
# END OF WILSY OS SOVEREIGN ARTIFACT
