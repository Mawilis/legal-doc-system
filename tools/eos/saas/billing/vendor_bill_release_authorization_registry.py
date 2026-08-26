"""WILSY OS — VENDOR BILL RELEASE AUTHORIZATION REGISTRY
Version: v1.0.0-VENDOR-BILL-RELEASE-AUTHORIZATION-REGISTRY
Authority: Wilsy OS Core Governance | Classification: Institutional Artifact — Production Only
EPITOME: Tenant-scoped durable immutable release evidence with deterministic
SHA3-512 integrity and corruption-first hydration; persistence only.
ABSOLUTE PATH: /Users/wilsonkhanyezi/legal-doc-system/tools/eos/saas/billing/vendor_bill_release_authorization_registry.py
COLLABORATION: Wilson Khanyezi — Founder / Chief Architect; AI Engineering (Codex) — governed R2B-02.
Date: 2026-08-26 | COMPLIANCE: POPIA §19 | GDPR §32 | SOC2 CC7.2
ARCHITECTURE LOCK: APPROVED != RELEASE AUTHORIZED != EXECUTED != SETTLED
Kennel EOS remains the exclusive financial execution authority.
CHANGELOG:
- 2026-08-26 — v1.0.0-VENDOR-BILL-RELEASE-AUTHORIZATION-REGISTRY
  Initial sovereign tenant-scoped Mongo registry with deterministic SHA3-512
  idempotency evidence, corruption-first hydration, and caller-owned sessions.
"""

from __future__ import annotations

import hashlib
import json
import re
from dataclasses import dataclass
from enum import StrEnum
from typing import Any, Optional

from pymongo import ASCENDING, WriteConcern
from pymongo.client_session import ClientSession
from pymongo.collection import Collection
from pymongo.errors import DuplicateKeyError
from pymongo.read_concern import ReadConcern

from ...kernel.db import get_database
from ..domain.vendor_bill_release_authorization import (
    VendorBillReleaseAuthorization,
    VendorBillReleaseAuthorizationDomainError,
)

VERSION = "v1.0.0-VENDOR-BILL-RELEASE-AUTHORIZATION-REGISTRY"
COLLECTION = "vendor_bill_release_authorizations"
WRITE_CONCERN = WriteConcern(w="majority", j=True, wtimeout=10000)
READ_CONCERN = ReadConcern("majority")
_MAX_IDEMPOTENCY_KEY_LENGTH = 128
_MAX_TENANT_ID_LENGTH = 128
_MAX_PAYABLE_ID_LENGTH = 80
_MAX_RELEASE_AUTHORIZATION_ID_LENGTH = 80


class VendorBillReleaseAuthorizationRegistryError(RuntimeError):
    """Description: stable base error for persistence failures.

    Collaboration: consumed by future orchestration and registry callers.
    Institutional: prevents raw infrastructure failures becoming financial control semantics.
    """


class VendorBillReleaseAuthorizationNotFoundError(VendorBillReleaseAuthorizationRegistryError):
    """Description: tenant-scoped durable authorization was not found.

    Collaboration: used by future orchestration reads.
    Institutional: absence grants no release or execution authority.
    """


class VendorBillReleaseAuthorizationPersistedRecordInvalidError(VendorBillReleaseAuthorizationRegistryError):
    """Description: durable record failed metadata, domain, or fingerprint integrity.

    Collaboration: raised by hydration before replay or conflict classification.
    Institutional: corrupted persistence can never become financial authority.
    """


class VendorBillReleaseAuthorizationIdempotencyKeyReuseError(VendorBillReleaseAuthorizationRegistryError):
    """Description: payable-scoped key was reused with different evidence.

    Collaboration: protects retrying orchestration callers.
    Institutional: one command identity cannot authorize divergent evidence.
    """


class VendorBillReleaseAuthorizationCreateConflictError(VendorBillReleaseAuthorizationRegistryError):
    """Description: release identity conflicts with durable evidence.

    Collaboration: returned to future orchestration without raw Mongo errors.
    Institutional: immutable identity is preserved without execution authority.
    """


class VendorBillReleaseAuthorizationCreateOutcome(StrEnum):
    """Description: stable classification of registry create results.

    Collaboration: consumed by future orchestration for create versus replay.
    Institutional: replay is persistence-only, never payment execution or settlement.
    """

    CREATED = "CREATED"
    IDEMPOTENT_REPLAY = "IDEMPOTENT_REPLAY"


@dataclass(frozen=True)
class VendorBillReleaseAuthorizationCreateResult:
    """Description: immutable result pairing outcome with domain evidence.

    Collaboration: future orchestration consumes it after persistence.
    Institutional: carries no Kennel, bank, provider, or settlement truth.
    """

    outcome: VendorBillReleaseAuthorizationCreateOutcome
    authorization: VendorBillReleaseAuthorization


def _collection(collection: Optional[Collection] = None) -> Collection:
    """Select canonical collection with majority durability."""
    if collection is not None:
        return collection.with_options(write_concern=WRITE_CONCERN, read_concern=READ_CONCERN)
    database = get_database()
    if database is None:
        raise VendorBillReleaseAuthorizationRegistryError(
            "VENDOR_BILL_RELEASE_AUTHORIZATION_PERSISTENCE_UNAVAILABLE"
        )
    return database[COLLECTION].with_options(write_concern=WRITE_CONCERN, read_concern=READ_CONCERN)


def _require_text(value: str, field_name: str, maximum: int) -> str:
    """Validate and normalize a bounded identity."""
    if not isinstance(value, str):
        raise VendorBillReleaseAuthorizationRegistryError(f"{field_name} is invalid")
    normalized = value.strip()
    if not normalized or len(normalized) > maximum:
        raise VendorBillReleaseAuthorizationRegistryError(f"{field_name} is invalid")
    return normalized


def _idempotency_key(value: str) -> str:
    """Validate the payable-scoped idempotency key."""
    return _require_text(value, "idempotency_key", _MAX_IDEMPOTENCY_KEY_LENGTH)


def _fingerprint(authorization: VendorBillReleaseAuthorization, key: str) -> str:
    """Bind the complete domain representation and normalized key."""
    body = authorization.to_persistence_dict()
    canonical = json.dumps(
        {"authorization": body, "idempotency_key": key},
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=True,
    )
    return hashlib.sha3_512(canonical.encode("utf-8")).hexdigest()


def _hydrate(document: dict[str, Any]) -> VendorBillReleaseAuthorization:
    """Perform metadata, fingerprint, and strict domain hydration checks."""
    try:
        key = document["create_idempotency_key"]
        fingerprint = document["create_fingerprint"]
        if not isinstance(key, str) or _idempotency_key(key) != key:
            raise ValueError("metadata")
        if not isinstance(fingerprint, str) or re.fullmatch(r"[0-9a-f]{128}", fingerprint) is None:
            raise ValueError("fingerprint")
        body = {name: value for name, value in document.items() if name not in {"_id", "create_idempotency_key", "create_fingerprint"}}
        authorization = VendorBillReleaseAuthorization.from_persistence_dict(body)
        if _fingerprint(authorization, key) != fingerprint:
            raise ValueError("integrity")
        return authorization
    except (KeyError, TypeError, ValueError, VendorBillReleaseAuthorizationDomainError) as error:
        raise VendorBillReleaseAuthorizationPersistedRecordInvalidError(
            "VENDOR_BILL_RELEASE_AUTHORIZATION_PERSISTED_RECORD_INVALID"
        ) from error


class VendorBillReleaseAuthorizationRegistry:
    """Description: tenant-scoped Mongo boundary for immutable evidence.

    Collaboration: future orchestration may call it after separately establishing eligibility.
    Institutional: persists authority evidence only; it cannot decide approval, invoke
    Kennel EOS, execute money movement, or prove settlement.
    """

    @staticmethod
    def ensure_indexes(collection: Optional[Collection] = None) -> None:
        """Description: create the two canonical unique identities.

        Collaboration: prepares the future release registry without economic policy.
        Institutional: every identity is tenant-scoped and idempotency is payable-scoped.
        Args: collection, optional caller-supplied Mongo collection.
        Returns: None.
        Raises: registry persistence errors from Mongo.
        """
        target = _collection(collection)
        target.create_index([("tenant_id", ASCENDING), ("release_authorization_id", ASCENDING)], unique=True, name="tenant_release_authorization_identity_unique")
        target.create_index([("tenant_id", ASCENDING), ("payable_id", ASCENDING), ("create_idempotency_key", ASCENDING)], unique=True, name="tenant_payable_release_idempotency_unique")

    @staticmethod
    def create(authorization: VendorBillReleaseAuthorization, idempotency_key: str, collection: Optional[Collection] = None, *, session: Optional[ClientSession] = None) -> VendorBillReleaseAuthorizationCreateResult:
        """Description: durably insert immutable release evidence.

        Collaboration: consumed by future orchestration; it never authorizes execution.
        Institutional: fingerprints are SHA3-512, corruption precedes replay/conflict,
        and caller-owned sessions are preserved.
        Args: authorization, domain evidence; idempotency_key, payable-scoped command key.
        Returns: CREATED or IDEMPOTENT_REPLAY with hydrated evidence.
        Raises: stable registry errors for invalid, corrupt, or conflicting records.
        """
        if not isinstance(authorization, VendorBillReleaseAuthorization):
            raise VendorBillReleaseAuthorizationRegistryError("authorization must be VendorBillReleaseAuthorization")
        key = _idempotency_key(idempotency_key)
        target = _collection(collection)
        document = {**authorization.to_persistence_dict(), "create_idempotency_key": key, "create_fingerprint": _fingerprint(authorization, key)}
        try:
            target.insert_one(document, session=session)
            return VendorBillReleaseAuthorizationCreateResult(VendorBillReleaseAuthorizationCreateOutcome.CREATED, authorization)
        except DuplicateKeyError as error:
            existing = target.find_one({"tenant_id": authorization.tenant_id, "payable_id": authorization.payable_id, "create_idempotency_key": key}, session=session)
            if existing is not None:
                persisted = _hydrate(existing)
                if persisted == authorization and existing.get("create_fingerprint") == document["create_fingerprint"]:
                    return VendorBillReleaseAuthorizationCreateResult(VendorBillReleaseAuthorizationCreateOutcome.IDEMPOTENT_REPLAY, persisted)
                raise VendorBillReleaseAuthorizationIdempotencyKeyReuseError("VENDOR_BILL_RELEASE_AUTHORIZATION_IDEMPOTENCY_KEY_REUSED_WITH_DIFFERENT_COMMAND") from error
            existing = target.find_one({"tenant_id": authorization.tenant_id, "release_authorization_id": authorization.release_authorization_id}, session=session)
            if existing is not None:
                _hydrate(existing)
            raise VendorBillReleaseAuthorizationCreateConflictError("VENDOR_BILL_RELEASE_AUTHORIZATION_CREATE_CONFLICT") from error

    @staticmethod
    def get(tenant_id: str, release_authorization_id: str, collection: Optional[Collection] = None, *, session: Optional[ClientSession] = None) -> VendorBillReleaseAuthorization:
        """Description: retrieve one tenant-scoped authorization.

        Collaboration: supports future orchestration reads; no execution authority is granted.
        Institutional: tenant identity is mandatory on every query and corruption is rejected.
        Args: tenant_id, release_authorization_id, collection, session.
        Returns: hydrated immutable authorization.
        Raises: not-found or persisted-record-invalid errors.
        """
        document = _collection(collection).find_one({"tenant_id": _require_text(tenant_id, "tenant_id", _MAX_TENANT_ID_LENGTH), "release_authorization_id": _require_text(release_authorization_id, "release_authorization_id", _MAX_RELEASE_AUTHORIZATION_ID_LENGTH)}, session=session)
        if document is None:
            raise VendorBillReleaseAuthorizationNotFoundError("VENDOR_BILL_RELEASE_AUTHORIZATION_NOT_FOUND")
        return _hydrate(document)

    @staticmethod
    def get_by_idempotency_key(tenant_id: str, payable_id: str, idempotency_key: str, collection: Optional[Collection] = None, *, session: Optional[ClientSession] = None) -> VendorBillReleaseAuthorization:
        """Description: retrieve by payable-scoped command identity.

        Collaboration: supports future tenant-scoped registry orchestration.
        Institutional: tenant and payable predicates prevent cross-tenant replay.
        Args: tenant_id, payable_id, idempotency_key, collection, session.
        Returns: hydrated immutable authorization.
        Raises: not-found or persisted-record-invalid errors.
        """
        document = _collection(collection).find_one({"tenant_id": _require_text(tenant_id, "tenant_id", _MAX_TENANT_ID_LENGTH), "payable_id": _require_text(payable_id, "payable_id", _MAX_PAYABLE_ID_LENGTH), "create_idempotency_key": _idempotency_key(idempotency_key)}, session=session)
        if document is None:
            raise VendorBillReleaseAuthorizationNotFoundError("VENDOR_BILL_RELEASE_AUTHORIZATION_NOT_FOUND")
        return _hydrate(document)


# INSTITUTIONAL CERTIFICATION SEAL
# File: vendor_bill_release_authorization_registry.py
# Version: v1.0.0-VENDOR-BILL-RELEASE-AUTHORIZATION-REGISTRY
# Status: SOVEREIGN REGISTRY CONTRACT — R2B-02 | Authority: Wilsy OS Core Governance
# Tenant isolation; unique identity/index posture; SHA3-512 create evidence;
# corruption-first hydration; caller-owned sessions; Kennel EOS execution ownership.
# Runtime posture: MONGO PERSISTENCE ONLY / NO EXECUTION
# POPIA §19 | GDPR §32 | SOC2 CC7.2 | Certification date: 2026-08-26
