"""TITLE: WILSY OS Tenant Legal Operating Model Domain.

VERSION: v1.0.1-G7B-TENANT-LEGAL-OPERATING-MODEL

ARTIFACT: tools/eos/legal_operations/domain/tenant_legal_operating_model.py
EPITOME: Immutable exact-tenant activation of canonical Legal operating-model vocabulary.
COLLABORATION / OWNERSHIP: G7B owns tenant Legal operating-model configuration semantics only; IAM, professional, workflow, entitlement, commercial, and financial authorities remain external.
SECURITY / PRIVACY POSTURE: Stores opaque tenant configuration identifiers and deterministic SHA3-512 fingerprints only; no credentials or principal authority.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2; ISO 27001.
TRANSACTION OWNERSHIP: NONE in the pure domain; persistence transactions are caller-owned by registry consumers.
CHANGELOG: v1.0.1 completes sovereign artifact metadata and end sealing without changing tenant operating-model semantics.

AUTHORITY:
    Wilsy OS Core Governance / Python EOS Legal Operations.

EPITOME:
    Defines one immutable tenant-scoped Legal operating-model revision selecting
    a bounded subset of the canonical G7A Global Legal Operating Catalogue.

    This domain records configuration only. It does not grant principal role,
    qualification, regulatory appointment, permission, entitlement, browser
    authority, legal execution, billing, payment, settlement, or financial
    execution authority.

TENANT BOUNDARY:
    Exact non-pseudo tenant_id is mandatory.

AUTHORITY BOUNDARY:
    Selected catalogue items are tenant configuration facts only.

COMMERCIAL BOUNDARY:
    This domain does not prove that the tenant commercially owns Legal
    Operations or any plan feature. Commercial entitlement is an external
    prerequisite owned elsewhere.

CLASSIFICATION BOUNDARY:
    Business Classification may recommend an operating model but never creates
    one.

FINANCIAL AUTHORITY BOUNDARY:
    None. Kennel EOS remains the exclusive financial execution and settlement
    authority.

FAIL-CLOSED POSTURE:
    Unknown catalogue items, duplicate selections, invalid revisions, malformed
    timestamps, invalid supersession, drifted catalogue fingerprint, pseudo
    tenants, and fingerprint mismatch reject.
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from hashlib import sha3_512
import hmac
import json
from typing import Final, NoReturn

from tools.eos.legal_operations.domain.legal_operating_catalogue import (
    CATALOGUE_FINGERPRINT,
    LegalOperatingCatalogueError,
    get_legal_operating_item,
)


VERSION: Final[str] = "v1.0.1-G7B-TENANT-LEGAL-OPERATING-MODEL"
SCHEMA: Final[str] = "WILSY-TENANT-LEGAL-OPERATING-MODEL/V1"


class TenantLegalOperatingModelError(ValueError):
    """Stable fail-closed tenant Legal operating-model error."""

    def __init__(self, code: str) -> None:
        self.code = code
        super().__init__(code)


def _fail(code: str) -> NoReturn:
    raise TenantLegalOperatingModelError(code)


def _text(name: str, value: object) -> str:
    if not isinstance(value, str):
        _fail(f"G7B_{name.upper()}_INVALID")
    normalized = value.strip()
    if not normalized or normalized != value:
        _fail(f"G7B_{name.upper()}_INVALID")
    return normalized


def _when(name: str, value: object) -> datetime:
    if not isinstance(value, datetime):
        _fail(f"G7B_{name.upper()}_INVALID")
    if value.tzinfo is None or value.utcoffset() is None:
        _fail(f"G7B_{name.upper()}_INVALID")
    normalized = value.astimezone(timezone.utc)
    return normalized


def _revision(value: object) -> int:
    if isinstance(value, bool) or not isinstance(value, int) or value < 1:
        _fail("G7B_REVISION_INVALID")
    return value


def _catalogue_items(value: object) -> tuple[str, ...]:
    if not isinstance(value, tuple):
        _fail("G7B_ACTIVATED_ITEMS_INVALID")

    normalized: list[str] = []
    seen: set[str] = set()

    for raw in value:
        item_id = _text("activated_item", raw)
        try:
            get_legal_operating_item(item_id)
        except LegalOperatingCatalogueError as error:
            raise TenantLegalOperatingModelError(
                "G7B_ACTIVATED_ITEM_UNKNOWN"
            ) from error

        if item_id in seen:
            _fail("G7B_ACTIVATED_ITEM_DUPLICATE")

        seen.add(item_id)
        normalized.append(item_id)

    return tuple(sorted(normalized))


@dataclass(frozen=True, slots=True)
class TenantLegalOperatingModel:
    tenant_id: str
    operating_model_id: str
    revision: int
    activated_item_ids: tuple[str, ...]
    effective_from: datetime
    supersedes_operating_model_id: str | None
    catalogue_fingerprint: str = CATALOGUE_FINGERPRINT
    schema: str = SCHEMA
    model_version: str = VERSION
    fingerprint: str = ""

    def __post_init__(self) -> None:
        tenant_id = _text("tenant_id", self.tenant_id)

        if tenant_id.casefold() in {"default", "global", "root", "*"}:
            _fail("G7B_TENANT_REQUIRED")

        operating_model_id = _text(
            "operating_model_id",
            self.operating_model_id,
        )

        revision = _revision(self.revision)
        activated_item_ids = _catalogue_items(
            self.activated_item_ids
        )
        effective_from = _when(
            "effective_from",
            self.effective_from,
        )

        supersedes = self.supersedes_operating_model_id
        if supersedes is not None:
            supersedes = _text(
                "supersedes_operating_model_id",
                supersedes,
            )
            if supersedes == operating_model_id:
                _fail("G7B_SUPERSESSION_INVALID")

        if self.schema != SCHEMA or self.model_version != VERSION:
            _fail("G7B_IDENTITY_INVALID")

        if (
            not isinstance(self.catalogue_fingerprint, str)
            or len(self.catalogue_fingerprint) != 128
            or self.catalogue_fingerprint.lower()
            != self.catalogue_fingerprint
        ):
            _fail("G7B_CATALOGUE_FINGERPRINT_INVALID")

        try:
            int(self.catalogue_fingerprint, 16)
        except ValueError as error:
            raise TenantLegalOperatingModelError(
                "G7B_CATALOGUE_FINGERPRINT_INVALID"
            ) from error

        if not hmac.compare_digest(
            self.catalogue_fingerprint,
            CATALOGUE_FINGERPRINT,
        ):
            _fail("G7B_CATALOGUE_BINDING_INVALID")

        object.__setattr__(self, "tenant_id", tenant_id)
        object.__setattr__(
            self,
            "operating_model_id",
            operating_model_id,
        )
        object.__setattr__(self, "revision", revision)
        object.__setattr__(
            self,
            "activated_item_ids",
            activated_item_ids,
        )
        object.__setattr__(
            self,
            "effective_from",
            effective_from,
        )
        object.__setattr__(
            self,
            "supersedes_operating_model_id",
            supersedes,
        )

        computed = self._compute_fingerprint()

        if self.fingerprint:
            if (
                not isinstance(self.fingerprint, str)
                or len(self.fingerprint) != 128
                or self.fingerprint.lower() != self.fingerprint
            ):
                _fail("G7B_FINGERPRINT_INVALID")
            try:
                int(self.fingerprint, 16)
            except ValueError as error:
                raise TenantLegalOperatingModelError(
                    "G7B_FINGERPRINT_INVALID"
                ) from error

            if not hmac.compare_digest(
                self.fingerprint,
                computed,
            ):
                _fail("G7B_FINGERPRINT_MISMATCH")

        object.__setattr__(
            self,
            "fingerprint",
            computed,
        )

    def semantic_dict(self) -> dict[str, object]:
        return {
            "schema": self.schema,
            "model_version": self.model_version,
            "tenant_id": self.tenant_id,
            "operating_model_id": self.operating_model_id,
            "revision": self.revision,
            "activated_item_ids": list(
                self.activated_item_ids
            ),
            "effective_from": self.effective_from.isoformat(),
            "supersedes_operating_model_id":
                self.supersedes_operating_model_id,
            "catalogue_fingerprint":
                self.catalogue_fingerprint,
        }

    def _compute_fingerprint(self) -> str:
        canonical = json.dumps(
            self.semantic_dict(),
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=False,
        )
        return sha3_512(
            canonical.encode("utf-8")
        ).hexdigest()

    def to_dict(self) -> dict[str, object]:
        return {
            **self.semantic_dict(),
            "fingerprint": self.fingerprint,
        }

    @classmethod
    def from_dict(
        cls,
        value: object,
    ) -> "TenantLegalOperatingModel":
        if not isinstance(value, dict):
            _fail("G7B_PAYLOAD_INVALID")

        required = {
            "schema",
            "model_version",
            "tenant_id",
            "operating_model_id",
            "revision",
            "activated_item_ids",
            "effective_from",
            "supersedes_operating_model_id",
            "catalogue_fingerprint",
            "fingerprint",
        }

        if set(value) != required:
            _fail("G7B_PAYLOAD_SCHEMA_INVALID")

        raw_items = value["activated_item_ids"]
        if not isinstance(raw_items, list):
            _fail("G7B_ACTIVATED_ITEMS_INVALID")

        raw_effective = value["effective_from"]
        if not isinstance(raw_effective, str):
            _fail("G7B_EFFECTIVE_FROM_INVALID")

        try:
            effective_from = datetime.fromisoformat(
                raw_effective
            )
        except ValueError as error:
            raise TenantLegalOperatingModelError(
                "G7B_EFFECTIVE_FROM_INVALID"
            ) from error

        return cls(
            schema=value["schema"],
            model_version=value["model_version"],
            tenant_id=value["tenant_id"],
            operating_model_id=value["operating_model_id"],
            revision=value["revision"],
            activated_item_ids=tuple(raw_items),
            effective_from=effective_from,
            supersedes_operating_model_id=value[
                "supersedes_operating_model_id"
            ],
            catalogue_fingerprint=value[
                "catalogue_fingerprint"
            ],
            fingerprint=value["fingerprint"],
        )


__all__ = [
    "SCHEMA",
    "VERSION",
    "TenantLegalOperatingModel",
    "TenantLegalOperatingModelError",
]

# ARTIFACT: tenant_legal_operating_model.py
# VERSION: v1.0.1-G7B-TENANT-LEGAL-OPERATING-MODEL
# AUTHORITY BOUNDARY: tenant Legal configuration only; no IAM/professional/entitlement authority
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively
# END OF WILSY OS SOVEREIGN ARTIFACT
