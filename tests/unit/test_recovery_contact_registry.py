"""Direct certificate for WILSY OS recovery-contact persistence.

TITLE: WILSY OS Recovery Contact Registry Direct Certificate
VERSION: v1.0.0-R10E10-RECOVERY-CONTACT-REGISTRY-CERT
AUTHORITY: Wilsy OS Core Governance
EPITOME: Certifies exact tenant/principal contact persistence and lifecycle CAS
         using deterministic PyMongo-shaped in-memory evidence only.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tests/unit/test_recovery_contact_registry.py
COLLABORATION / OWNERSHIP: Exercises recovery_contact_registry.py and the R10E9
                           domain; no real Mongo, SMTP, auth, or password mutation.
CERTIFICATION / UPDATE DATE: 2026-09-22
CHANGELOG:
  v1.0.0-R10E10-RECOVERY-CONTACT-REGISTRY-CERT — Certifies deterministic indexes,
    one non-revoked EMAIL slot, strict hydration, tenant-scoped reads, VERIFIED
    resolution, caller-session propagation, exact verify/revoke CAS, stale-state
    rejection, and historical revoked-contact retention.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2; ISO 27001.
SECURITY / PRIVACY POSTURE: Synthetic addresses only; no recovery bearer or credentials.
TENANT BOUNDARY: Every lookup and transition is exact tenant/principal scoped.
AUTHORITY BOUNDARY: Persistence evidence only; no verification ceremony or recovery issuance.
FINANCIAL AUTHORITY BOUNDARY: None; Kennel EOS remains exclusively financial.
"""

from __future__ import annotations

from copy import deepcopy
from datetime import datetime, timedelta, timezone
from typing import Any, Iterable

import pytest
from pymongo.errors import DuplicateKeyError, PyMongoError

from tools.eos.saas.auth.recovery_contact import (
    RecoveryContactAuthority,
    RecoveryContactStatus,
    RecoveryContactVerificationMethod,
)
from tools.eos.saas.auth.recovery_contact_registry import (
    COLLECTION,
    INDEX_DEFINITIONS,
    RecoveryContactAlreadyExistsError,
    RecoveryContactAuthorityRegistry,
    RecoveryContactLifecycleConflictError,
    RecoveryContactPersistedRecordInvalidError,
    RecoveryContactPersistenceError,
)


NOW = datetime(2026, 9, 22, 18, 30, 0, tzinfo=timezone.utc)


class _Cursor:
    def __init__(self, rows: Iterable[dict[str, Any]]) -> None:
        self._rows = list(rows)

    def limit(self, count: int) -> "_Cursor":
        self._rows = self._rows[:count]
        return self

    def __iter__(self):
        return iter(deepcopy(self._rows))


class _Collection:
    def __init__(self) -> None:
        self.rows: list[dict[str, Any]] = []
        self.calls: list[dict[str, Any]] = []
        self.index_calls: list[tuple[tuple[tuple[str, int], ...], dict[str, Any]]] = []
        self.force_cas_miss = False
        self.fail_reads = False

    @staticmethod
    def _matches(row: dict[str, Any], query: dict[str, Any]) -> bool:
        return all(row.get(key) == expected for key, expected in query.items())

    def create_index(self, keys: list[tuple[str, int]], **options: Any) -> str:
        self.index_calls.append((tuple(keys), dict(options)))
        return str(options["name"])

    def insert_one(self, document: dict[str, Any], **options: Any) -> object:
        self.calls.append({"method": "insert_one", "document": deepcopy(document), "options": options})
        if any(row["contact_id"] == document["contact_id"] for row in self.rows):
            raise DuplicateKeyError("synthetic contact identity collision")
        if any(
            row["tenant_id"] == document["tenant_id"]
            and row["principal_id"] == document["principal_id"]
            and row["_active_slot"] == document["_active_slot"]
            for row in self.rows
        ):
            raise DuplicateKeyError("synthetic active slot collision")
        self.rows.append(deepcopy(document))
        return object()

    def find_one(self, query: dict[str, Any], **options: Any) -> dict[str, Any] | None:
        self.calls.append({"method": "find_one", "query": deepcopy(query), "options": options})
        if self.fail_reads:
            raise PyMongoError("synthetic read failure")
        for row in self.rows:
            if self._matches(row, query):
                return deepcopy(row)
        return None

    def find(self, query: dict[str, Any], **options: Any) -> _Cursor:
        self.calls.append({"method": "find", "query": deepcopy(query), "options": options})
        if self.fail_reads:
            raise PyMongoError("synthetic read failure")
        return _Cursor(row for row in self.rows if self._matches(row, query))

    def find_one_and_replace(
        self,
        query: dict[str, Any],
        replacement: dict[str, Any],
        **options: Any,
    ) -> dict[str, Any] | None:
        self.calls.append(
            {
                "method": "find_one_and_replace",
                "query": deepcopy(query),
                "replacement": deepcopy(replacement),
                "options": options,
            }
        )
        if self.force_cas_miss:
            return None
        for index, row in enumerate(self.rows):
            if self._matches(row, query):
                self.rows[index] = deepcopy(replacement)
                return deepcopy(replacement)
        return None


def _pending(
    *,
    contact_id: str = "contact-one",
    tenant_id: str = "tenant-a",
    principal_id: str = "principal-a",
    address: str = "person@example.com",
    created_at: datetime = NOW,
) -> RecoveryContactAuthority:
    return RecoveryContactAuthority.pending(
        contact_id=contact_id,
        tenant_id=tenant_id,
        principal_id=principal_id,
        address=address,
        created_at=created_at,
    )


def _registry() -> tuple[RecoveryContactAuthorityRegistry, _Collection, object]:
    collection = _Collection()
    return RecoveryContactAuthorityRegistry(collection), collection, object()


def _last(collection: _Collection, method: str) -> dict[str, Any]:
    return next(call for call in reversed(collection.calls) if call["method"] == method)


def test_collection_and_index_contract() -> None:
    registry, collection, _ = _registry()
    registry.ensure_indexes()
    assert COLLECTION == "recovery_contact_authorities"
    assert len(INDEX_DEFINITIONS) == 3
    assert [options["name"] for _, options in collection.index_calls] == [
        "recovery_contact_identity_unique",
        "recovery_contact_tenant_principal_active_slot_unique",
        "recovery_contact_tenant_principal_status_channel",
    ]
    assert collection.index_calls[0][1]["unique"] is True
    assert collection.index_calls[1][1]["unique"] is True
    assert collection.index_calls[2][1]["unique"] is False


def test_create_pending_persists_exact_authority_and_session() -> None:
    registry, collection, session = _registry()
    contact = _pending()
    assert registry.create_pending(contact, session=session) == contact
    inserted = _last(collection, "insert_one")
    assert inserted["document"]["tenant_id"] == "tenant-a"
    assert inserted["document"]["principal_id"] == "principal-a"
    assert inserted["document"]["address"] == "person@example.com"
    assert inserted["document"]["status"] == "PENDING"
    assert inserted["document"]["_active_slot"] == "EMAIL"
    assert inserted["options"]["session"] is session
    assert "emailVerified" not in inserted["document"]
    assert "password" not in repr(inserted["document"]).lower()


def test_one_non_revoked_email_slot_per_tenant_principal() -> None:
    registry, _collection, session = _registry()
    registry.create_pending(_pending(contact_id="first"), session=session)
    with pytest.raises(RecoveryContactAlreadyExistsError) as error:
        registry.create_pending(
            _pending(contact_id="second", address="other@example.com"),
            session=session,
        )
    assert error.value.code == "RECOVERY_CONTACT_ACTIVE_SLOT_OCCUPIED"


def test_cross_tenant_contact_identity_is_scoped_absence() -> None:
    registry, collection, session = _registry()
    contact = _pending()
    registry.create_pending(contact, session=session)
    collection.calls.clear()
    assert registry.get_by_contact_id(
        tenant_id="tenant-b",
        contact_id=contact.contact_id,
        session=session,
    ) is None
    call = _last(collection, "find_one")
    assert call["query"] == {"tenant_id": "tenant-b", "contact_id": contact.contact_id}
    assert call["options"]["session"] is session


def test_pending_contact_is_not_resolved_as_verified() -> None:
    registry, _collection, session = _registry()
    contact = _pending()
    registry.create_pending(contact, session=session)
    assert registry.resolve_verified_for_principal(
        tenant_id="tenant-a",
        principal_id="principal-a",
        observed_at=NOW,
        session=session,
    ) is None


def test_verify_cas_and_verified_resolution_preserve_exact_session() -> None:
    registry, collection, session = _registry()
    pending = _pending()
    registry.create_pending(pending, session=session)
    verified_at = NOW + timedelta(minutes=1)
    verified = registry.verify(
        pending,
        verified_at=verified_at,
        method=RecoveryContactVerificationMethod.EMAIL_CHALLENGE,
        session=session,
    )
    assert verified.status is RecoveryContactStatus.VERIFIED
    assert verified.revision == 1
    cas = _last(collection, "find_one_and_replace")
    assert cas["query"]["tenant_id"] == pending.tenant_id
    assert cas["query"]["principal_id"] == pending.principal_id
    assert cas["query"]["revision"] == 0
    assert cas["query"]["status"] == "PENDING"
    assert cas["options"]["session"] is session

    resolved = registry.resolve_verified_for_principal(
        tenant_id=pending.tenant_id,
        principal_id=pending.principal_id,
        observed_at=verified_at,
        session=session,
    )
    assert resolved == verified


def test_revoke_frees_active_slot_and_retains_historical_row() -> None:
    registry, collection, session = _registry()
    pending = _pending(contact_id="first")
    registry.create_pending(pending, session=session)
    verified = registry.verify(
        pending,
        verified_at=NOW + timedelta(minutes=1),
        method=RecoveryContactVerificationMethod.EMAIL_CHALLENGE,
        session=session,
    )
    revoked = registry.revoke(
        verified,
        revoked_at=NOW + timedelta(minutes=2),
        session=session,
    )
    assert revoked.status is RecoveryContactStatus.REVOKED
    assert revoked.revision == 2
    assert collection.rows[0]["_active_slot"] == "REVOKED:first"

    replacement = _pending(
        contact_id="second",
        address="new@example.com",
        created_at=NOW + timedelta(minutes=3),
    )
    assert registry.create_pending(replacement, session=session) == replacement
    assert len(collection.rows) == 2


def test_stale_revision_transition_fails_closed() -> None:
    registry, collection, session = _registry()
    pending = _pending()
    registry.create_pending(pending, session=session)
    verified = registry.verify(
        pending,
        verified_at=NOW + timedelta(minutes=1),
        method=RecoveryContactVerificationMethod.EMAIL_CHALLENGE,
        session=session,
    )
    collection.force_cas_miss = True
    with pytest.raises(RecoveryContactLifecycleConflictError) as error:
        registry.revoke(
            verified,
            revoked_at=NOW + timedelta(minutes=2),
            session=session,
        )
    assert error.value.code in {
        "RECOVERY_CONTACT_STALE_REVISION",
        "RECOVERY_CONTACT_LIFECYCLE_CONFLICT",
    }


def test_corrupt_active_slot_metadata_is_rejected() -> None:
    registry, collection, session = _registry()
    contact = _pending()
    registry.create_pending(contact, session=session)
    collection.rows[0]["_active_slot"] = "BROKEN"
    with pytest.raises(RecoveryContactPersistedRecordInvalidError):
        registry.get_by_contact_id(
            tenant_id=contact.tenant_id,
            contact_id=contact.contact_id,
            session=session,
        )


def test_read_failure_is_not_scoped_absence() -> None:
    registry, collection, session = _registry()
    collection.fail_reads = True
    with pytest.raises(RecoveryContactPersistenceError) as error:
        registry.get_by_contact_id(
            tenant_id="tenant-a",
            contact_id="contact-a",
            session=session,
        )
    assert error.value.code == "RECOVERY_CONTACT_READ_FAILED"


# ARTIFACT: tests/unit/test_recovery_contact_registry.py
# VERSION: v1.0.0-R10E10-RECOVERY-CONTACT-REGISTRY-CERT
# AUTHORITY BOUNDARY: deterministic recovery-contact persistence evidence only
# TENANT POSTURE: exact tenant/principal scope; one non-revoked EMAIL slot
# FAIL-CLOSED POSTURE: corrupt, stale, duplicate, ambiguous, and cross-tenant state never verifies contact
# FINANCIAL EXECUTION AUTHORITY: None; Kennel EOS remains exclusively financial
# END OF WILSY OS SOVEREIGN ARTIFACT
