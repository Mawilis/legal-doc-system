# -*- coding: utf-8 -*-
"""WILSY OS durable tenant-scoped Payment Destination registry and resolver.

VERSION: v1.0.0-KENNEL-PAYMENT-DESTINATION-REGISTRY-RESOLVER
AUTHORITY: Wilsy OS Core Governance
EPITOME: Durable opaque destination authority; no provider, execution, or settlement behavior.
ABSOLUTE PATH: /Users/wilsonkhanyezi/legal-doc-system/tools/eos/kennel/registry/payment_destination_registry.py
COLLABORATION: Wilson Khanyezi (Founder/Chief Architect); Codex (AI Engineering)
CHANGELOG: v1.0.0 establishes tenant-scoped identity, replay-safe persistence, corruption-first hydration, and eligibility resolution.
COMPLIANCE: POPIA §19 | GDPR Art. 32 | SOC2 CC7.2
"""
from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from typing import Any, Mapping, Optional

from pymongo import ASCENDING
from pymongo.collection import Collection
from pymongo.client_session import ClientSession
from pymongo.errors import DuplicateKeyError, PyMongoError

from ..domain.payment_destination import PaymentDestination, PaymentDestinationError, PaymentDestinationStatus

VERSION = "v1.0.0-KENNEL-PAYMENT-DESTINATION-REGISTRY-RESOLVER"
COLLECTION = "kennel_payment_destinations"


class PaymentDestinationRegistryError(RuntimeError):
    """Base fail-closed destination persistence or authority error."""


class PaymentDestinationNotFoundError(PaymentDestinationRegistryError):
    """Raised when tenant-scoped destination identity is absent."""


class PaymentDestinationPersistedRecordInvalidError(PaymentDestinationRegistryError):
    """Raised when persisted destination truth cannot be canonically hydrated."""


class PaymentDestinationCreateConflictError(PaymentDestinationRegistryError):
    """Raised when canonical identity collides with divergent destination truth."""


class PaymentDestinationReferenceConflictError(PaymentDestinationRegistryError):
    """Raised when an opaque reference is already bound to another identity."""


class PaymentDestinationEligibilityError(PaymentDestinationRegistryError):
    """Raised when a destination is not execution-eligible for resolution."""


@dataclass(frozen=True)
class ResolvedPaymentDestination:
    """Immutable execution-safe handle containing no provider credentials."""

    payment_destination_id: str
    tenant_id: str
    beneficiary_id: str
    destination_reference: str
    destination_type: str | None
    provider_metadata_reference: str | None
    destination_fingerprint: str


def _target(collection: Optional[Collection]) -> Collection:
    if collection is not None:
        return collection
    from ...kernel.db import get_database
    database = get_database()
    if database is None:
        raise PaymentDestinationRegistryError("PAYMENT_DESTINATION_PERSISTENCE_UNAVAILABLE")
    return database[COLLECTION]


def _identity(value: str, name: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise PaymentDestinationRegistryError(f"invalid {name}")
    return value.strip()


def _fingerprint(destination: PaymentDestination) -> str:
    return destination.fingerprint


def _document(destination: PaymentDestination) -> dict[str, Any]:
    return {**destination.to_persistence_dict(), "destination_fingerprint": _fingerprint(destination)}


def _hydrate(document: Mapping[str, Any]) -> PaymentDestination:
    try:
        data = dict(document)
        stored = data.pop("destination_fingerprint", None)
        data.pop("_id", None)
        destination = PaymentDestination.from_persistence_dict(data)
        if not isinstance(stored, str) or stored != destination.fingerprint:
            raise PaymentDestinationPersistedRecordInvalidError("PAYMENT_DESTINATION_PERSISTED_RECORD_INVALID")
        return destination
    except PaymentDestinationPersistedRecordInvalidError:
        raise
    except (TypeError, ValueError, PaymentDestinationError) as error:
        raise PaymentDestinationPersistedRecordInvalidError("PAYMENT_DESTINATION_PERSISTED_RECORD_INVALID") from error


class PaymentDestinationRegistry:
    """Persists immutable destination authority and resolves only eligible opaque handles."""

    @staticmethod
    def ensure_indexes(collection: Optional[Collection] = None) -> None:
        target = _target(collection)
        target.create_index([("tenant_id", ASCENDING), ("payment_destination_id", ASCENDING)], unique=True, name="tenant_payment_destination_identity_unique")
        target.create_index([("tenant_id", ASCENDING), ("destination_reference", ASCENDING)], unique=True, name="tenant_payment_destination_reference_unique")
        target.create_index([("tenant_id", ASCENDING), ("beneficiary_id", ASCENDING), ("created_at", ASCENDING)], name="tenant_beneficiary_payment_destinations")

    @staticmethod
    def create(destination: PaymentDestination, collection: Optional[Collection] = None, *, session: Optional[ClientSession] = None) -> PaymentDestination:
        if not isinstance(destination, PaymentDestination):
            raise PaymentDestinationRegistryError("destination must be PaymentDestination")
        target = _target(collection)
        document = _document(destination)
        try:
            target.insert_one(document, session=session)
            return destination
        except DuplicateKeyError as error:
            existing = target.find_one({"tenant_id": destination.tenant_id, "payment_destination_id": destination.payment_destination_id}, session=session)
            if existing is not None:
                durable = _hydrate(existing)
                if durable == destination:
                    return durable
                raise PaymentDestinationCreateConflictError("PAYMENT_DESTINATION_CREATE_CONFLICT") from error
            existing = target.find_one({"tenant_id": destination.tenant_id, "destination_reference": destination.destination_reference}, session=session)
            if existing is not None:
                _hydrate(existing)
                raise PaymentDestinationReferenceConflictError("PAYMENT_DESTINATION_REFERENCE_CONFLICT") from error
            raise PaymentDestinationCreateConflictError("PAYMENT_DESTINATION_CREATE_CONFLICT") from error
        except PyMongoError as error:
            raise PaymentDestinationRegistryError("PAYMENT_DESTINATION_CREATE_FAILED") from error

    @staticmethod
    def get(tenant_id: str, payment_destination_id: str, collection: Optional[Collection] = None, *, session: Optional[ClientSession] = None) -> PaymentDestination:
        document = _target(collection).find_one({"tenant_id": _identity(tenant_id, "tenant_id"), "payment_destination_id": _identity(payment_destination_id, "payment_destination_id")}, session=session)
        if document is None:
            raise PaymentDestinationNotFoundError("PAYMENT_DESTINATION_NOT_FOUND")
        return _hydrate(document)

    @staticmethod
    def get_by_reference(tenant_id: str, destination_reference: str, collection: Optional[Collection] = None, *, session: Optional[ClientSession] = None) -> PaymentDestination:
        document = _target(collection).find_one({"tenant_id": _identity(tenant_id, "tenant_id"), "destination_reference": _identity(destination_reference, "destination_reference")}, session=session)
        if document is None:
            raise PaymentDestinationNotFoundError("PAYMENT_DESTINATION_NOT_FOUND")
        return _hydrate(document)

    @staticmethod
    def resolve(tenant_id: str, destination_reference: str, beneficiary_id: str | None = None, collection: Optional[Collection] = None, *, session: Optional[ClientSession] = None) -> ResolvedPaymentDestination:
        destination = PaymentDestinationRegistry.get_by_reference(tenant_id, destination_reference, collection, session=session)
        if beneficiary_id is not None and destination.beneficiary_id != _identity(beneficiary_id, "beneficiary_id"):
            raise PaymentDestinationEligibilityError("PAYMENT_DESTINATION_BENEFICIARY_MISMATCH")
        if not destination.is_execution_eligible:
            raise PaymentDestinationEligibilityError("PAYMENT_DESTINATION_NOT_EXECUTION_ELIGIBLE")
        return ResolvedPaymentDestination(destination.payment_destination_id, destination.tenant_id, destination.beneficiary_id, destination.destination_reference, destination.destination_type, destination.provider_metadata_reference, destination.fingerprint)

    @staticmethod
    def revoke(tenant_id: str, payment_destination_id: str, revoked_at: Any, collection: Optional[Collection] = None, *, session: Optional[ClientSession] = None) -> PaymentDestination:
        destination = PaymentDestinationRegistry.get(tenant_id, payment_destination_id, collection, session=session)
        if destination.status is PaymentDestinationStatus.REVOKED:
            if destination.revoked_at != revoked_at:
                raise PaymentDestinationCreateConflictError("PAYMENT_DESTINATION_REVOCATION_CONFLICT")
            return destination
        replacement = PaymentDestination(destination.payment_destination_id, destination.tenant_id, destination.beneficiary_id, destination.destination_reference, PaymentDestinationStatus.REVOKED, destination.verification_state, destination.created_at, destination.destination_type, destination.provider_metadata_reference, destination.verified_at, revoked_at)
        result = _target(collection).replace_one({"tenant_id": destination.tenant_id, "payment_destination_id": destination.payment_destination_id, "destination_fingerprint": destination.fingerprint}, _document(replacement), session=session)
        if result.modified_count != 1:
            raise PaymentDestinationRegistryError("PAYMENT_DESTINATION_REVOCATION_CONFLICT")
        return replacement


# ARTIFACT: payment_destination_registry.py
# VERSION: v1.0.0-KENNEL-PAYMENT-DESTINATION-REGISTRY-RESOLVER
# AUTHORITY BOUNDARY: registry owns destination truth; resolver never executes money.
# TENANT POSTURE: every lookup and mutation is tenant-scoped.
# FAIL-CLOSED POSTURE: corruption, conflicts, revocation, and ineligible states reject.
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively owns execution truth.
# END OF WILSY OS SOVEREIGN ARTIFACT
