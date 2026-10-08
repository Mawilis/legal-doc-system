"""
TITLE: WILSY OS CRM Email Template Pure Domain
VERSION: v1.0.0-CRM-EMAIL-TEMPLATE

AUTHORITY:
    Immutable tenant-bound CRM email-template metadata and published content
    revision truth only.

EPITOME:
    Establishes email templates as first-class CRM content while preserving
    strict separation between reusable template truth, rendered drafts,
    mailbox identities, send authorization, sequence execution, consent,
    suppression, provider delivery and engagement evidence.

ABSOLUTE CANONICAL PATH:
    /Users/wilsonkhanyezi/legal-doc-system/tools/eos/crm/domain/crm_email_template.py

RESEARCH BASIS:
    Apollo:
        - reusable email templates;
        - editable linked templates;
        - prospect preview;
        - basic/custom dynamic variables;
        - advanced conditional variables as a separately governed concern;
        - sent messages remain historical facts when templates later change.

    lemlist:
        - reusable template library;
        - customizable email content;
        - custom variables;
        - signatures;
        - HTML, images and attachments;
        - fallback/personalization syntax as a separately governed concern.

    WILSY OS:
        - exact tenant identity;
        - immutable evidence-bearing domain values;
        - explicit authority separation;
        - no role-name, UI-token or provider shortcut creates authority.

TEMPLATE SCOPE:
    USER_PRIVATE
        Template belongs to one exact owner principal.

    TEAM_SHARED
        Template is associated with one explicit team reference.

    TENANT_SHARED
        Template is shared at tenant level but grants no permission itself.

    SYSTEM_SEED
        Platform-provided template definition; still tenant-bound when admitted
        into tenant CRM context and still grants no execution authority.

TEMPLATE ORIGIN:
    SYSTEM_SEED
    TENANT_CREATED
    COPIED

REVISION DOCTRINE:
    Published revisions are immutable. Editing a template produces later
    revision truth; prior revision history is never rewritten.

VARIABLE DOCTRINE:
    This v1 domain supports only allowlisted CRM namespaces:
        lead.*
        contact.*
        account.*
        owner.*
        sender.*
        custom.*

    Variable keys are declarations, not database paths. Rendering code must
    later resolve them through certified field projections. Arbitrary storage,
    authentication, billing or internal-system paths fail closed.

    Conditional expressions, fallback expressions and arbitrary Liquid-like
    execution are deliberately outside v1 and require separate research and
    certification.

CUSTOMIZATION DOCTRINE:
    A rendered email draft may later be customized independently. Draft
    mutation is deliberately outside this immutable template domain.

MAILBOX BOUNDARY:
    No SMTP password, OAuth token, refresh token, provider credential or
    mailbox secret exists in this domain.

SEND BOUNDARY:
    Template ownership, visibility, origin, content or revision does not
    authorize email send.

CONSENT BOUNDARY:
    No lawful-basis, suppression, opt-out or contactability decision exists
    in this domain.

SEQUENCE BOUNDARY:
    No sequence scheduling, cadence, queue or workflow authority exists here.

DELIVERY BOUNDARY:
    No sent, delivered, bounced, opened, clicked or replied state exists here.

AI BOUNDARY:
    AI may later draft or recommend content, but this domain grants no AI
    execution and no autonomous send authority.

FINANCIAL AUTHORITY BOUNDARY:
    None. Kennel EOS remains exclusive financial execution authority.

CHANGELOG:
    2026-10-07 v1.0.0 establishes immutable tenant-bound CRM email template
    metadata and published content revision truth.
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from datetime import datetime, timezone
from enum import Enum
import hashlib
import hmac
import json
import re
import unicodedata
from typing import Final, cast


CRM_EMAIL_TEMPLATE_VERSION: Final[str] = (
    "v1.0.0-CRM-EMAIL-TEMPLATE"
)

CRM_EMAIL_TEMPLATE_SCHEMA: Final[str] = (
    "WILSY-CRM-EMAIL-TEMPLATE/V1"
)


_FORBIDDEN_TENANTS: Final[frozenset[str]] = frozenset({
    "default",
    "global",
    "root",
    "*",
    "master",
    "global_root",
    "sovereign_root",
    "wilsy-sovereign-root",
})

_LOWER_HEX: Final[frozenset[str]] = frozenset(
    "0123456789abcdef"
)

_VARIABLE_KEY = re.compile(
    r"^(lead|contact|account|owner|sender|custom)"
    r"\.[A-Za-z][A-Za-z0-9_]*$"
)

_TEMPLATE_VARIABLE = re.compile(
    r"\{\{([^{}]+)\}\}"
)

_TEMPLATE_FIELDS = frozenset({
    "schema",
    "version",
    "entity_type",
    "tenant_id",
    "template_id",
    "name",
    "scope",
    "origin",
    "lifecycle",
    "owner_principal_id",
    "team_id",
    "folder",
    "tags",
    "created_at",
    "metadata_revision",
    "updated_at",
    "metadata_fingerprint",
})

_REVISION_FIELDS: Final[frozenset[str]] = frozenset({
    "schema",
    "version",
    "entity_type",
    "tenant_id",
    "template_id",
    "revision",
    "subject",
    "text_body",
    "html_body",
    "variable_keys",
    "attachment_references",
    "signature_reference",
    "source_reference",
    "source_fingerprint",
    "published_at",
    "fingerprint",
})


class CrmEmailTemplateError(ValueError):
    """Raised when CRM email-template truth fails closed."""


class CrmEmailTemplateScope(str, Enum):
    """Closed template visibility/ownership classification."""

    USER_PRIVATE = "USER_PRIVATE"
    TEAM_SHARED = "TEAM_SHARED"
    TENANT_SHARED = "TENANT_SHARED"
    SYSTEM_SEED = "SYSTEM_SEED"


class CrmEmailTemplateOrigin(str, Enum):
    """Closed template provenance origin."""

    SYSTEM_SEED = "SYSTEM_SEED"
    TENANT_CREATED = "TENANT_CREATED"
    COPIED = "COPIED"


class CrmEmailTemplateLifecycle(str, Enum):
    """Closed template lifecycle."""

    ACTIVE = "ACTIVE"
    ARCHIVED = "ARCHIVED"


def _exact_text(
    name: str,
    value: object,
    *,
    allow_empty: bool = False,
) -> str:
    """Require NFC text without hidden trimming or control characters."""

    if not isinstance(value, str):
        raise CrmEmailTemplateError(
            f"CRM_EMAIL_TEMPLATE_{name.upper()}_INVALID"
        )

    if value != value.strip():
        raise CrmEmailTemplateError(
            f"CRM_EMAIL_TEMPLATE_{name.upper()}_INVALID"
        )

    if not value and not allow_empty:
        raise CrmEmailTemplateError(
            f"CRM_EMAIL_TEMPLATE_{name.upper()}_INVALID"
        )

    normalized = unicodedata.normalize(
        "NFC",
        value,
    )

    if normalized != value:
        raise CrmEmailTemplateError(
            f"CRM_EMAIL_TEMPLATE_{name.upper()}_INVALID"
        )

    if any(
        ord(character) < 32
        and character not in "\n\r\t"
        for character in value
    ):
        raise CrmEmailTemplateError(
            f"CRM_EMAIL_TEMPLATE_{name.upper()}_INVALID"
        )

    return value


def _tenant(value: object) -> str:
    """Require one explicit non-pseudo tenant identity."""

    tenant = _exact_text(
        "tenant_id",
        value,
    )

    if tenant.casefold() in _FORBIDDEN_TENANTS:
        raise CrmEmailTemplateError(
            "CRM_EMAIL_TEMPLATE_TENANT_ID_INVALID"
        )

    return tenant


def _optional_identifier(
    name: str,
    value: object,
) -> str | None:
    """Validate an optional exact identifier."""

    if value is None:
        return None

    return _exact_text(
        name,
        value,
    )


def _timestamp(
    name: str,
    value: object,
) -> datetime:
    """Require timezone-aware datetime and normalize to UTC."""

    if (
        not isinstance(value, datetime)
        or value.tzinfo is None
        or value.utcoffset() is None
    ):
        raise CrmEmailTemplateError(
            f"CRM_EMAIL_TEMPLATE_{name.upper()}_INVALID"
        )

    return value.astimezone(
        timezone.utc
    )


def _utc_text(value: datetime) -> str:
    """Serialize one aware timestamp canonically."""

    return (
        value.astimezone(timezone.utc)
        .isoformat()
        .replace("+00:00", "Z")
    )


def _positive_revision(value: object) -> int:
    """Require a positive integer revision; bool is invalid."""

    if (
        isinstance(value, bool)
        or not isinstance(value, int)
        or value < 1
    ):
        raise CrmEmailTemplateError(
            "CRM_EMAIL_TEMPLATE_REVISION_INVALID"
        )

    return value


def _sha3_512(
    name: str,
    value: object,
) -> str:
    """Require canonical lowercase SHA3-512 hexadecimal shape."""

    if (
        not isinstance(value, str)
        or len(value) != 128
        or any(
            character not in _LOWER_HEX
            for character in value
        )
    ):
        raise CrmEmailTemplateError(
            f"CRM_EMAIL_TEMPLATE_{name.upper()}_INVALID"
        )

    return value


def _scope(value: object) -> CrmEmailTemplateScope:
    try:
        return CrmEmailTemplateScope(value)
    except (TypeError, ValueError) as error:
        raise CrmEmailTemplateError(
            "CRM_EMAIL_TEMPLATE_SCOPE_INVALID"
        ) from error


def _origin(value: object) -> CrmEmailTemplateOrigin:
    try:
        return CrmEmailTemplateOrigin(value)
    except (TypeError, ValueError) as error:
        raise CrmEmailTemplateError(
            "CRM_EMAIL_TEMPLATE_ORIGIN_INVALID"
        ) from error


def _lifecycle(value: object) -> CrmEmailTemplateLifecycle:
    try:
        return CrmEmailTemplateLifecycle(value)
    except (TypeError, ValueError) as error:
        raise CrmEmailTemplateError(
            "CRM_EMAIL_TEMPLATE_LIFECYCLE_INVALID"
        ) from error


def _string_tuple(
    name: str,
    value: object,
) -> tuple[str, ...]:
    """Require an ordered immutable sequence of unique exact strings."""

    if (
        not isinstance(value, Sequence)
        or isinstance(value, (str, bytes, bytearray))
    ):
        raise CrmEmailTemplateError(
            f"CRM_EMAIL_TEMPLATE_{name.upper()}_INVALID"
        )

    result = tuple(
        _exact_text(
            name,
            entry,
        )
        for entry in value
    )

    if len(result) != len(set(result)):
        raise CrmEmailTemplateError(
            f"CRM_EMAIL_TEMPLATE_{name.upper()}_DUPLICATE"
        )

    return result


def _variable_keys(
    value: object,
) -> tuple[str, ...]:
    """Validate closed variable namespaces without granting field access."""

    variables = _string_tuple(
        "variable_keys",
        value,
    )

    for variable in variables:
        if _VARIABLE_KEY.fullmatch(variable) is None:
            raise CrmEmailTemplateError(
                "CRM_EMAIL_TEMPLATE_VARIABLE_KEY_INVALID"
            )

    return variables


def _used_variables(
    *,
    subject: str,
    text_body: str,
    html_body: str,
) -> frozenset[str]:
    """Extract exact v1 variable tokens from template content."""

    combined = "\n".join(
        (
            subject,
            text_body,
            html_body,
        )
    )

    used: set[str] = set()

    for match in _TEMPLATE_VARIABLE.finditer(
        combined
    ):
        raw = match.group(1)

        if raw != raw.strip():
            raise CrmEmailTemplateError(
                "CRM_EMAIL_TEMPLATE_VARIABLE_EXPRESSION_INVALID"
            )

        if _VARIABLE_KEY.fullmatch(raw) is None:
            raise CrmEmailTemplateError(
                "CRM_EMAIL_TEMPLATE_VARIABLE_EXPRESSION_INVALID"
            )

        used.add(raw)

    return frozenset(used)


def _validate_scope_binding(
    *,
    scope: CrmEmailTemplateScope,
    origin: CrmEmailTemplateOrigin,
    owner_principal_id: str | None,
    team_id: str | None,
) -> None:
    """Enforce explicit scope coordinates without inferring authority."""

    if scope is CrmEmailTemplateScope.USER_PRIVATE:
        if owner_principal_id is None or team_id is not None:
            raise CrmEmailTemplateError(
                "CRM_EMAIL_TEMPLATE_SCOPE_BINDING_INVALID"
            )

    elif scope is CrmEmailTemplateScope.TEAM_SHARED:
        if team_id is None or owner_principal_id is not None:
            raise CrmEmailTemplateError(
                "CRM_EMAIL_TEMPLATE_SCOPE_BINDING_INVALID"
            )

    elif scope is CrmEmailTemplateScope.TENANT_SHARED:
        if (
            owner_principal_id is not None
            or team_id is not None
        ):
            raise CrmEmailTemplateError(
                "CRM_EMAIL_TEMPLATE_SCOPE_BINDING_INVALID"
            )

    elif scope is CrmEmailTemplateScope.SYSTEM_SEED:
        if (
            owner_principal_id is not None
            or team_id is not None
            or origin is not CrmEmailTemplateOrigin.SYSTEM_SEED
        ):
            raise CrmEmailTemplateError(
                "CRM_EMAIL_TEMPLATE_SCOPE_BINDING_INVALID"
            )

    if (
        origin is CrmEmailTemplateOrigin.SYSTEM_SEED
        and scope is not CrmEmailTemplateScope.SYSTEM_SEED
    ):
        raise CrmEmailTemplateError(
            "CRM_EMAIL_TEMPLATE_SYSTEM_SEED_SCOPE_INVALID"
        )


def _revision_fingerprint(
    *,
    tenant_id: str,
    template_id: str,
    revision: int,
    subject: str,
    text_body: str,
    html_body: str,
    variable_keys: tuple[str, ...],
    attachment_references: tuple[str, ...],
    signature_reference: str,
    source_reference: str,
    source_fingerprint: str,
    published_at: datetime,
) -> str:
    """Create deterministic SHA3-512 identity for published content."""

    payload = {
        "schema": CRM_EMAIL_TEMPLATE_SCHEMA,
        "version": CRM_EMAIL_TEMPLATE_VERSION,
        "entity_type": "CrmEmailTemplateRevision",
        "tenant_id": tenant_id,
        "template_id": template_id,
        "revision": revision,
        "subject": subject,
        "text_body": text_body,
        "html_body": html_body,
        "variable_keys": list(variable_keys),
        "attachment_references":
            list(attachment_references),
        "signature_reference":
            signature_reference,
        "source_reference":
            source_reference,
        "source_fingerprint":
            source_fingerprint,
        "published_at":
            _utc_text(published_at),
    }

    encoded = json.dumps(
        payload,
        ensure_ascii=False,
        allow_nan=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")

    return hashlib.sha3_512(
        encoded
    ).hexdigest()


@dataclass(
    frozen=True,
    slots=True,
)
class _MetadataUnset:
    """Private sentinel for omitted metadata revision coordinates."""


_METADATA_UNSET = _MetadataUnset()


def _metadata_fingerprint(
    *,
    tenant_id: str,
    template_id: str,
    name: str,
    scope: CrmEmailTemplateScope,
    origin: CrmEmailTemplateOrigin,
    lifecycle: CrmEmailTemplateLifecycle,
    owner_principal_id: str | None,
    team_id: str | None,
    folder: str,
    tags: tuple[str, ...],
    created_at: datetime,
    metadata_revision: int,
    updated_at: datetime,
) -> str:
    """Create deterministic SHA3-512 identity for current metadata truth."""

    payload = {
        "schema": CRM_EMAIL_TEMPLATE_SCHEMA,
        "version": CRM_EMAIL_TEMPLATE_VERSION,
        "entity_type": "CrmEmailTemplate",
        "tenant_id": tenant_id,
        "template_id": template_id,
        "name": name,
        "scope": scope.value,
        "origin": origin.value,
        "lifecycle": lifecycle.value,
        "owner_principal_id": owner_principal_id,
        "team_id": team_id,
        "folder": folder,
        "tags": list(tags),
        "created_at": _utc_text(created_at),
        "metadata_revision": metadata_revision,
        "updated_at": _utc_text(updated_at),
    }

    encoded = json.dumps(
        payload,
        ensure_ascii=False,
        allow_nan=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")

    return hashlib.sha3_512(
        encoded
    ).hexdigest()


def _metadata_revision(
    value: object,
) -> int:
    """Require one positive non-boolean metadata CAS revision."""

    if (
        isinstance(value, bool)
        or not isinstance(value, int)
        or value < 1
    ):
        raise CrmEmailTemplateError(
            "CRM_EMAIL_TEMPLATE_METADATA_REVISION_INVALID"
        )

    return value


@dataclass(
    frozen=True,
    slots=True,
)
class CrmEmailTemplate:
    """Immutable CRM email-template metadata current state.

    Metadata evolution is explicit optimistic concurrency control. Template
    content revisions remain separate immutable published snapshots.

    This value describes organization and visibility classification only.
    It does not grant read, edit, send, sharing, mailbox, consent, sequence,
    AI execution or financial authority.
    """

    tenant_id: str
    template_id: str
    name: str
    scope: CrmEmailTemplateScope
    origin: CrmEmailTemplateOrigin
    lifecycle: CrmEmailTemplateLifecycle
    owner_principal_id: str | None
    team_id: str | None
    folder: str
    tags: tuple[str, ...]
    created_at: datetime
    metadata_revision: int
    updated_at: datetime
    metadata_fingerprint: str

    @classmethod
    def create(
        cls,
        *,
        tenant_id: str,
        template_id: str,
        name: str,
        scope: CrmEmailTemplateScope | str,
        origin: CrmEmailTemplateOrigin | str,
        lifecycle: CrmEmailTemplateLifecycle | str,
        owner_principal_id: str | None,
        team_id: str | None,
        folder: str,
        tags: Sequence[str],
        created_at: datetime,
    ) -> "CrmEmailTemplate":
        """Create initial validated metadata at CAS revision one."""

        canonical_tenant = _tenant(
            tenant_id
        )

        canonical_template_id = _exact_text(
            "template_id",
            template_id,
        )

        canonical_name = _exact_text(
            "name",
            name,
        )

        canonical_scope = _scope(
            scope
        )

        canonical_origin = _origin(
            origin
        )

        canonical_lifecycle = _lifecycle(
            lifecycle
        )

        canonical_owner = _optional_identifier(
            "owner_principal_id",
            owner_principal_id,
        )

        canonical_team = _optional_identifier(
            "team_id",
            team_id,
        )

        canonical_folder = _exact_text(
            "folder",
            folder,
            allow_empty=True,
        )

        canonical_tags = _string_tuple(
            "tags",
            tags,
        )

        canonical_created_at = _timestamp(
            "created_at",
            created_at,
        )

        _validate_scope_binding(
            scope=canonical_scope,
            origin=canonical_origin,
            owner_principal_id=canonical_owner,
            team_id=canonical_team,
        )

        revision = 1
        updated_at = canonical_created_at

        fingerprint = _metadata_fingerprint(
            tenant_id=canonical_tenant,
            template_id=canonical_template_id,
            name=canonical_name,
            scope=canonical_scope,
            origin=canonical_origin,
            lifecycle=canonical_lifecycle,
            owner_principal_id=canonical_owner,
            team_id=canonical_team,
            folder=canonical_folder,
            tags=canonical_tags,
            created_at=canonical_created_at,
            metadata_revision=revision,
            updated_at=updated_at,
        )

        return cls(
            tenant_id=canonical_tenant,
            template_id=canonical_template_id,
            name=canonical_name,
            scope=canonical_scope,
            origin=canonical_origin,
            lifecycle=canonical_lifecycle,
            owner_principal_id=canonical_owner,
            team_id=canonical_team,
            folder=canonical_folder,
            tags=canonical_tags,
            created_at=canonical_created_at,
            metadata_revision=revision,
            updated_at=updated_at,
            metadata_fingerprint=fingerprint,
        )

    def revise_metadata(
        self,
        *,
        expected_revision: int,
        expected_fingerprint: str,
        occurred_at: datetime,
        name: str | _MetadataUnset = _METADATA_UNSET,
        scope: (
            CrmEmailTemplateScope
            | str
            | _MetadataUnset
        ) = _METADATA_UNSET,
        lifecycle: (
            CrmEmailTemplateLifecycle
            | str
            | _MetadataUnset
        ) = _METADATA_UNSET,
        owner_principal_id: (
            str
            | None
            | _MetadataUnset
        ) = _METADATA_UNSET,
        team_id: (
            str
            | None
            | _MetadataUnset
        ) = _METADATA_UNSET,
        folder: str | _MetadataUnset = _METADATA_UNSET,
        tags: Sequence[str] | _MetadataUnset = _METADATA_UNSET,
    ) -> "CrmEmailTemplate":
        """Return exactly one CAS-guarded immutable metadata successor."""

        expected = _metadata_revision(
            expected_revision
        )

        if expected != self.metadata_revision:
            raise CrmEmailTemplateError(
                "CRM_EMAIL_TEMPLATE_METADATA_REVISION_CONFLICT"
            )

        expected_fp = _sha3_512(
            "metadata_fingerprint",
            expected_fingerprint,
        )

        if expected_fp != self.metadata_fingerprint:
            raise CrmEmailTemplateError(
                "CRM_EMAIL_TEMPLATE_METADATA_FINGERPRINT_CONFLICT"
            )

        if (
            self.origin
            is CrmEmailTemplateOrigin.SYSTEM_SEED
            or self.scope
            is CrmEmailTemplateScope.SYSTEM_SEED
        ):
            raise CrmEmailTemplateError(
                "CRM_EMAIL_TEMPLATE_SYSTEM_SEED_MUTATION_FORBIDDEN"
            )

        if (
            self.lifecycle
            is CrmEmailTemplateLifecycle.ARCHIVED
        ):
            raise CrmEmailTemplateError(
                "CRM_EMAIL_TEMPLATE_ARCHIVED_MUTATION_FORBIDDEN"
            )

        canonical_occurred_at = _timestamp(
            "occurred_at",
            occurred_at,
        )

        if canonical_occurred_at <= self.updated_at:
            raise CrmEmailTemplateError(
                "CRM_EMAIL_TEMPLATE_METADATA_TIMESTAMP_NOT_ADVANCING"
            )

        canonical_name = (
            self.name
            if isinstance(name, _MetadataUnset)
            else _exact_text(
                "name",
                name,
            )
        )

        canonical_scope = (
            self.scope
            if isinstance(scope, _MetadataUnset)
            else _scope(
                scope
            )
        )

        canonical_lifecycle = (
            self.lifecycle
            if isinstance(lifecycle, _MetadataUnset)
            else _lifecycle(
                lifecycle
            )
        )

        canonical_owner = (
            self.owner_principal_id
            if isinstance(
                owner_principal_id,
                _MetadataUnset,
            )
            else _optional_identifier(
                "owner_principal_id",
                owner_principal_id,
            )
        )

        canonical_team = (
            self.team_id
            if isinstance(
                team_id,
                _MetadataUnset,
            )
            else _optional_identifier(
                "team_id",
                team_id,
            )
        )

        canonical_folder = (
            self.folder
            if isinstance(folder, _MetadataUnset)
            else _exact_text(
                "folder",
                folder,
                allow_empty=True,
            )
        )

        canonical_tags = (
            self.tags
            if isinstance(tags, _MetadataUnset)
            else _string_tuple(
                "tags",
                tags,
            )
        )

        _validate_scope_binding(
            scope=canonical_scope,
            origin=self.origin,
            owner_principal_id=canonical_owner,
            team_id=canonical_team,
        )

        if (
            canonical_lifecycle
            is not self.lifecycle
            and canonical_lifecycle
            is not CrmEmailTemplateLifecycle.ARCHIVED
        ):
            raise CrmEmailTemplateError(
                "CRM_EMAIL_TEMPLATE_LIFECYCLE_TRANSITION_INVALID"
            )

        changed = (
            canonical_name != self.name
            or canonical_scope is not self.scope
            or canonical_lifecycle is not self.lifecycle
            or canonical_owner != self.owner_principal_id
            or canonical_team != self.team_id
            or canonical_folder != self.folder
            or canonical_tags != self.tags
        )

        if not changed:
            raise CrmEmailTemplateError(
                "CRM_EMAIL_TEMPLATE_METADATA_CHANGE_REQUIRED"
            )

        next_revision = self.metadata_revision + 1

        next_fingerprint = _metadata_fingerprint(
            tenant_id=self.tenant_id,
            template_id=self.template_id,
            name=canonical_name,
            scope=canonical_scope,
            origin=self.origin,
            lifecycle=canonical_lifecycle,
            owner_principal_id=canonical_owner,
            team_id=canonical_team,
            folder=canonical_folder,
            tags=canonical_tags,
            created_at=self.created_at,
            metadata_revision=next_revision,
            updated_at=canonical_occurred_at,
        )

        return CrmEmailTemplate(
            tenant_id=self.tenant_id,
            template_id=self.template_id,
            name=canonical_name,
            scope=canonical_scope,
            origin=self.origin,
            lifecycle=canonical_lifecycle,
            owner_principal_id=canonical_owner,
            team_id=canonical_team,
            folder=canonical_folder,
            tags=canonical_tags,
            created_at=self.created_at,
            metadata_revision=next_revision,
            updated_at=canonical_occurred_at,
            metadata_fingerprint=next_fingerprint,
        )

    def to_dict(
        self,
    ) -> dict[str, object]:
        """Serialize exact durable metadata current-state truth."""

        return {
            "schema":
                CRM_EMAIL_TEMPLATE_SCHEMA,
            "version":
                CRM_EMAIL_TEMPLATE_VERSION,
            "entity_type":
                "CrmEmailTemplate",
            "tenant_id":
                self.tenant_id,
            "template_id":
                self.template_id,
            "name":
                self.name,
            "scope":
                self.scope.value,
            "origin":
                self.origin.value,
            "lifecycle":
                self.lifecycle.value,
            "owner_principal_id":
                self.owner_principal_id,
            "team_id":
                self.team_id,
            "folder":
                self.folder,
            "tags":
                list(self.tags),
            "created_at":
                _utc_text(self.created_at),
            "metadata_revision":
                self.metadata_revision,
            "updated_at":
                _utc_text(self.updated_at),
            "metadata_fingerprint":
                self.metadata_fingerprint,
        }

    @classmethod
    def from_dict(
        cls,
        payload: Mapping[str, object],
    ) -> "CrmEmailTemplate":
        """Strictly hydrate and fingerprint-check metadata current state."""

        if not isinstance(payload, Mapping):
            raise CrmEmailTemplateError(
                "CRM_EMAIL_TEMPLATE_DOCUMENT_INVALID"
            )

        if set(payload) != _TEMPLATE_FIELDS:
            raise CrmEmailTemplateError(
                "CRM_EMAIL_TEMPLATE_DOCUMENT_SCHEMA_INVALID"
            )

        if (
            payload["schema"]
            != CRM_EMAIL_TEMPLATE_SCHEMA
            or payload["version"]
            != CRM_EMAIL_TEMPLATE_VERSION
            or payload["entity_type"]
            != "CrmEmailTemplate"
        ):
            raise CrmEmailTemplateError(
                "CRM_EMAIL_TEMPLATE_DOCUMENT_IDENTITY_INVALID"
            )

        raw_created = payload[
            "created_at"
        ]

        raw_updated = payload[
            "updated_at"
        ]

        if (
            not isinstance(raw_created, str)
            or not isinstance(raw_updated, str)
        ):
            raise CrmEmailTemplateError(
                "CRM_EMAIL_TEMPLATE_TIMESTAMP_INVALID"
            )

        try:
            created_at = datetime.fromisoformat(
                raw_created.replace(
                    "Z",
                    "+00:00",
                )
            )

            updated_at = datetime.fromisoformat(
                raw_updated.replace(
                    "Z",
                    "+00:00",
                )
            )

        except ValueError as error:
            raise CrmEmailTemplateError(
                "CRM_EMAIL_TEMPLATE_TIMESTAMP_INVALID"
            ) from error

        canonical_created_at = _timestamp(
            "created_at",
            created_at,
        )

        canonical_updated_at = _timestamp(
            "updated_at",
            updated_at,
        )

        revision = _metadata_revision(
            payload[
                "metadata_revision"
            ]
        )

        if (
            revision == 1
            and canonical_updated_at
            != canonical_created_at
        ):
            raise CrmEmailTemplateError(
                "CRM_EMAIL_TEMPLATE_INITIAL_METADATA_TIMESTAMP_INVALID"
            )

        if (
            revision > 1
            and canonical_updated_at
            <= canonical_created_at
        ):
            raise CrmEmailTemplateError(
                "CRM_EMAIL_TEMPLATE_METADATA_TIMESTAMP_INVALID"
            )

        raw_tags = payload[
            "tags"
        ]

        if not isinstance(raw_tags, list):
            raise CrmEmailTemplateError(
                "CRM_EMAIL_TEMPLATE_TAGS_INVALID"
            )

        canonical_tenant = _tenant(
            payload[
                "tenant_id"
            ]
        )

        canonical_template_id = _exact_text(
            "template_id",
            payload[
                "template_id"
            ],
        )

        canonical_name = _exact_text(
            "name",
            payload[
                "name"
            ],
        )

        canonical_scope = _scope(
            payload[
                "scope"
            ]
        )

        canonical_origin = _origin(
            payload[
                "origin"
            ]
        )

        canonical_lifecycle = _lifecycle(
            payload[
                "lifecycle"
            ]
        )

        canonical_owner = _optional_identifier(
            "owner_principal_id",
            payload[
                "owner_principal_id"
            ],
        )

        canonical_team = _optional_identifier(
            "team_id",
            payload[
                "team_id"
            ],
        )

        canonical_folder = _exact_text(
            "folder",
            payload[
                "folder"
            ],
            allow_empty=True,
        )

        canonical_tags = _string_tuple(
            "tags",
            raw_tags,
        )

        _validate_scope_binding(
            scope=canonical_scope,
            origin=canonical_origin,
            owner_principal_id=canonical_owner,
            team_id=canonical_team,
        )

        if (
            canonical_origin
            is CrmEmailTemplateOrigin.SYSTEM_SEED
            and revision != 1
        ):
            raise CrmEmailTemplateError(
                "CRM_EMAIL_TEMPLATE_SYSTEM_SEED_REVISION_INVALID"
            )

        stored_fingerprint = _sha3_512(
            "metadata_fingerprint",
            payload[
                "metadata_fingerprint"
            ],
        )

        expected_fingerprint = _metadata_fingerprint(
            tenant_id=canonical_tenant,
            template_id=canonical_template_id,
            name=canonical_name,
            scope=canonical_scope,
            origin=canonical_origin,
            lifecycle=canonical_lifecycle,
            owner_principal_id=canonical_owner,
            team_id=canonical_team,
            folder=canonical_folder,
            tags=canonical_tags,
            created_at=canonical_created_at,
            metadata_revision=revision,
            updated_at=canonical_updated_at,
        )

        if stored_fingerprint != expected_fingerprint:
            raise CrmEmailTemplateError(
                "CRM_EMAIL_TEMPLATE_METADATA_FINGERPRINT_MISMATCH"
            )

        return cls(
            tenant_id=canonical_tenant,
            template_id=canonical_template_id,
            name=canonical_name,
            scope=canonical_scope,
            origin=canonical_origin,
            lifecycle=canonical_lifecycle,
            owner_principal_id=canonical_owner,
            team_id=canonical_team,
            folder=canonical_folder,
            tags=canonical_tags,
            created_at=canonical_created_at,
            metadata_revision=revision,
            updated_at=canonical_updated_at,
            metadata_fingerprint=stored_fingerprint,
        )



@dataclass(
    frozen=True,
    slots=True,
)
class CrmEmailTemplateRevision:
    """Immutable published template content revision.

    A revision captures reusable content and declared variable coordinates.
    It contains no rendering engine, mailbox authority or send execution.
    """

    tenant_id: str
    template_id: str
    revision: int
    subject: str
    text_body: str
    html_body: str
    variable_keys: tuple[str, ...]
    attachment_references: tuple[str, ...]
    signature_reference: str
    source_reference: str
    source_fingerprint: str
    published_at: datetime
    fingerprint: str

    @classmethod
    def publish(
        cls,
        *,
        tenant_id: str,
        template_id: str,
        revision: int,
        subject: str,
        text_body: str,
        html_body: str,
        variable_keys: Sequence[str],
        attachment_references: Sequence[str],
        signature_reference: str,
        source_reference: str,
        source_fingerprint: str,
        published_at: datetime,
    ) -> "CrmEmailTemplateRevision":
        """Publish one immutable validated template content revision."""

        canonical_tenant = _tenant(
            tenant_id
        )

        canonical_template = _exact_text(
            "template_id",
            template_id,
        )

        canonical_revision = _positive_revision(
            revision
        )

        canonical_subject = _exact_text(
            "subject",
            subject,
            allow_empty=True,
        )

        canonical_text = _exact_text(
            "text_body",
            text_body,
            allow_empty=True,
        )

        canonical_html = _exact_text(
            "html_body",
            html_body,
            allow_empty=True,
        )

        if (
            not canonical_subject
            and not canonical_text
            and not canonical_html
        ):
            raise CrmEmailTemplateError(
                "CRM_EMAIL_TEMPLATE_CONTENT_EMPTY"
            )

        canonical_variables = _variable_keys(
            variable_keys
        )

        used_variables = _used_variables(
            subject=canonical_subject,
            text_body=canonical_text,
            html_body=canonical_html,
        )

        undeclared = (
            used_variables
            - set(canonical_variables)
        )

        if undeclared:
            raise CrmEmailTemplateError(
                "CRM_EMAIL_TEMPLATE_UNDECLARED_VARIABLE"
            )

        canonical_attachments = _string_tuple(
            "attachment_references",
            attachment_references,
        )

        canonical_signature = _exact_text(
            "signature_reference",
            signature_reference,
            allow_empty=True,
        )

        canonical_source_reference = _exact_text(
            "source_reference",
            source_reference,
        )

        canonical_source_fingerprint = _sha3_512(
            "source_fingerprint",
            source_fingerprint,
        )

        canonical_published_at = _timestamp(
            "published_at",
            published_at,
        )

        fingerprint = _revision_fingerprint(
            tenant_id=canonical_tenant,
            template_id=canonical_template,
            revision=canonical_revision,
            subject=canonical_subject,
            text_body=canonical_text,
            html_body=canonical_html,
            variable_keys=canonical_variables,
            attachment_references=
                canonical_attachments,
            signature_reference=
                canonical_signature,
            source_reference=
                canonical_source_reference,
            source_fingerprint=
                canonical_source_fingerprint,
            published_at=
                canonical_published_at,
        )

        return cls(
            tenant_id=canonical_tenant,
            template_id=canonical_template,
            revision=canonical_revision,
            subject=canonical_subject,
            text_body=canonical_text,
            html_body=canonical_html,
            variable_keys=canonical_variables,
            attachment_references=
                canonical_attachments,
            signature_reference=
                canonical_signature,
            source_reference=
                canonical_source_reference,
            source_fingerprint=
                canonical_source_fingerprint,
            published_at=
                canonical_published_at,
            fingerprint=fingerprint,
        )

    def to_dict(
        self,
    ) -> dict[str, object]:
        """Serialize one exact published revision."""

        return {
            "schema":
                CRM_EMAIL_TEMPLATE_SCHEMA,
            "version":
                CRM_EMAIL_TEMPLATE_VERSION,
            "entity_type":
                "CrmEmailTemplateRevision",
            "tenant_id":
                self.tenant_id,
            "template_id":
                self.template_id,
            "revision":
                self.revision,
            "subject":
                self.subject,
            "text_body":
                self.text_body,
            "html_body":
                self.html_body,
            "variable_keys":
                list(self.variable_keys),
            "attachment_references":
                list(self.attachment_references),
            "signature_reference":
                self.signature_reference,
            "source_reference":
                self.source_reference,
            "source_fingerprint":
                self.source_fingerprint,
            "published_at":
                _utc_text(self.published_at),
            "fingerprint":
                self.fingerprint,
        }

    @classmethod
    def from_dict(
        cls,
        payload: Mapping[str, object],
    ) -> "CrmEmailTemplateRevision":
        """Strictly hydrate and fingerprint-check one published revision."""

        if not isinstance(payload, Mapping):
            raise CrmEmailTemplateError(
                "CRM_EMAIL_TEMPLATE_REVISION_DOCUMENT_INVALID"
            )

        if set(payload) != _REVISION_FIELDS:
            raise CrmEmailTemplateError(
                "CRM_EMAIL_TEMPLATE_REVISION_SCHEMA_INVALID"
            )

        if (
            payload["schema"]
            != CRM_EMAIL_TEMPLATE_SCHEMA
            or payload["version"]
            != CRM_EMAIL_TEMPLATE_VERSION
            or payload["entity_type"]
            != "CrmEmailTemplateRevision"
        ):
            raise CrmEmailTemplateError(
                "CRM_EMAIL_TEMPLATE_REVISION_IDENTITY_INVALID"
            )

        raw_published = payload[
            "published_at"
        ]

        if not isinstance(raw_published, str):
            raise CrmEmailTemplateError(
                "CRM_EMAIL_TEMPLATE_PUBLISHED_AT_INVALID"
            )

        try:
            published_at = datetime.fromisoformat(
                raw_published.replace(
                    "Z",
                    "+00:00",
                )
            )
        except ValueError as error:
            raise CrmEmailTemplateError(
                "CRM_EMAIL_TEMPLATE_PUBLISHED_AT_INVALID"
            ) from error

        raw_variables = payload[
            "variable_keys"
        ]

        raw_attachments = payload[
            "attachment_references"
        ]

        if not isinstance(raw_variables, list):
            raise CrmEmailTemplateError(
                "CRM_EMAIL_TEMPLATE_VARIABLE_KEYS_INVALID"
            )

        if not isinstance(raw_attachments, list):
            raise CrmEmailTemplateError(
                "CRM_EMAIL_TEMPLATE_ATTACHMENT_REFERENCES_INVALID"
            )

        item = cls.publish(
            tenant_id=cast(
                str,
                payload["tenant_id"],
            ),
            template_id=cast(
                str,
                payload["template_id"],
            ),
            revision=cast(
                int,
                payload["revision"],
            ),
            subject=cast(
                str,
                payload["subject"],
            ),
            text_body=cast(
                str,
                payload["text_body"],
            ),
            html_body=cast(
                str,
                payload["html_body"],
            ),
            variable_keys=cast(
                list[str],
                raw_variables,
            ),
            attachment_references=cast(
                list[str],
                raw_attachments,
            ),
            signature_reference=cast(
                str,
                payload["signature_reference"],
            ),
            source_reference=cast(
                str,
                payload["source_reference"],
            ),
            source_fingerprint=cast(
                str,
                payload["source_fingerprint"],
            ),
            published_at=published_at,
        )

        stored_fingerprint = _sha3_512(
            "fingerprint",
            payload["fingerprint"],
        )

        if not hmac.compare_digest(
            stored_fingerprint,
            item.fingerprint,
        ):
            raise CrmEmailTemplateError(
                "CRM_EMAIL_TEMPLATE_FINGERPRINT_MISMATCH"
            )

        return item


__all__ = [
    "CRM_EMAIL_TEMPLATE_SCHEMA",
    "CRM_EMAIL_TEMPLATE_VERSION",
    "CrmEmailTemplate",
    "CrmEmailTemplateError",
    "CrmEmailTemplateLifecycle",
    "CrmEmailTemplateOrigin",
    "CrmEmailTemplateRevision",
    "CrmEmailTemplateScope",
]

# ARTIFACT: crm_email_template.py
# VERSION: v1.0.0-CRM-EMAIL-TEMPLATE
# AUTHORITY BOUNDARY: immutable customizable template/revision truth only
# VARIABLE POSTURE: allowlisted namespaces; no arbitrary database field access
# MAILBOX CREDENTIAL AUTHORITY: none
# SEND AUTHORITY: none
# CONSENT/SUPPRESSION AUTHORITY: none
# SEQUENCE EXECUTION AUTHORITY: none
# DELIVERY EVENT AUTHORITY: none
# AI SEND AUTHORITY: none
# FINANCIAL EXECUTION AUTHORITY: none; Kennel EOS remains exclusive
# END OF WILSY OS SOVEREIGN ARTIFACT
