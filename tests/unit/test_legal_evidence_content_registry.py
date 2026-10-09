"""Direct certificate for the L10A2 Legal evidence-content registry.

TITLE: WILSY OS Legal Evidence Content Registry Direct Certificate
VERSION: v1.0.0-L10A2-LEGAL-EVIDENCE-CONTENT-REGISTRY-CERT
AUTHORITY: Wilsy OS Core Governance
EPITOME: Certify active-transaction enforcement, immutable byte persistence,
         exact replay, divergent conflict, byte corruption detection, exact
         tenant/matter/document reads and absence of lifecycle/financial authority.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tests/unit/test_legal_evidence_content_registry.py
COLLABORATION / OWNERSHIP: Certifies only L10A2 registry semantics using
                            synthetic in-memory Mongo-like doubles.
CERTIFICATION / UPDATE DATE: 2026-09-29
CHANGELOG: 2026-09-29 v1.0.0-L10A2-LEGAL-EVIDENCE-CONTENT-REGISTRY-CERT
           establishes direct persistence/read/corruption/tenant-boundary proof.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2; ISO 27001.
SECURITY / PRIVACY POSTURE: Synthetic bytes and opaque identities only.
TENANT BOUNDARY: Exact tenant scope is asserted on every certified read/write.
AUTHORITY BOUNDARY: Registry evidence only; no lifecycle, Court, IAM, AI,
                    service or financial authority is tested or created.
FINANCIAL AUTHORITY BOUNDARY: None; Kennel EOS remains exclusive.
FAIL-CLOSED DECLARATION: Unexpected acceptance of malformed, divergent or corrupt
                         persistence is a certificate failure.
"""
from __future__ import annotations

from copy import deepcopy
from datetime import datetime, timedelta, timezone
import hashlib
from typing import Any

import pytest
from pymongo.errors import DuplicateKeyError

from tools.eos.legal_operations.domain.legal_evidence_content import (
    LegalEvidenceContent,
    register_legal_evidence_content,
)
from tools.eos.legal_operations.registry.legal_evidence_content_registry import (
    COLLECTION,
    CONTENT_FINGERPRINT_INDEX_NAME,
    DOCUMENT_INDEX_NAME,
    REFERENCE_INDEX_NAME,
    VERSION,
    LegalEvidenceContentRegistryConflictError,
    LegalEvidenceContentRegistryNotFoundError,
    LegalEvidenceContentRegistryPersistedRecordInvalidError,
    LegalEvidenceContentRegistryRetryRequiredError,
    LegalEvidenceContentRegistryTransactionRequiredError,
    ensure_indexes,
    get_evidence_content,
    list_document_evidence_contents,
    persist_evidence_content,
    read_evidence_content_bytes,
)


TENANT = "tenant-l10a2"
MATTER = "matter-l10a2"
DOCUMENT = "document-l10a2"
CONTENT = b"%PDF-1.7\nL10A2 synthetic evidence\n"
SOURCE_FP = hashlib.sha3_512(b"source-l10a2").hexdigest()
NOW = datetime(2026, 9, 29, 17, 0, tzinfo=timezone.utc)


class Session:
    """Minimal active caller-owned transaction double."""

    in_transaction = True


class InactiveSession:
    """Minimal inactive transaction double."""

    in_transaction = False


class Cursor:
    """Minimal deterministic Mongo cursor double."""

    def __init__(self, rows: list[dict[str, Any]]) -> None:
        self.rows = rows

    def sort(self, spec: list[tuple[str, int]]) -> "Cursor":
        for field, direction in reversed(spec):
            self.rows.sort(
                key=lambda row: str(row.get(field, "")),
                reverse=direction < 0,
            )
        return self

    def limit(self, count: int) -> "Cursor":
        self.rows = self.rows[:count]
        return self

    def __iter__(self):
        return iter(self.rows)


class Collection:
    """Small exact-query persistence double for direct registry proof."""

    def __init__(self) -> None:
        self.rows: list[dict[str, Any]] = []
        self.indexes: list[tuple[Any, dict[str, Any]]] = []
        self.sessions: list[object] = []

    def with_options(self, **_: Any) -> "Collection":
        return self

    def create_index(self, keys: Any, **kwargs: Any) -> str:
        self.indexes.append((keys, kwargs))
        return str(kwargs["name"])

    def _matches(
        self,
        row: dict[str, Any],
        query: dict[str, Any],
    ) -> bool:
        return all(row.get(key) == value for key, value in query.items())

    def find(
        self,
        query: dict[str, Any],
        *,
        session: object,
    ) -> Cursor:
        self.sessions.append(session)
        return Cursor(
            [
                deepcopy(row)
                for row in self.rows
                if self._matches(row, query)
            ]
        )

    def insert_one(
        self,
        row: dict[str, Any],
        *,
        session: object,
    ) -> object:
        self.sessions.append(session)
        self.rows.append(deepcopy(row))
        return object()


class DuplicateRaceCollection(Collection):
    """Collection double that reports a duplicate-key insertion race."""

    def insert_one(
        self,
        row: dict[str, Any],
        *,
        session: object,
    ) -> object:
        del row, session
        raise DuplicateKeyError("synthetic race")


def value(
    *,
    content: bytes = CONTENT,
    registered_at: datetime = NOW,
    source_reference: str = "upload:l10a2",
) -> LegalEvidenceContent:
    """Return one valid synthetic L10A1 value."""
    return register_legal_evidence_content(
        tenant_id=TENANT,
        case_matter_id=MATTER,
        document_id=DOCUMENT,
        media_type="application/pdf",
        original_filename="evidence.pdf",
        content=content,
        source_evidence_reference=source_reference,
        source_evidence_fingerprint=SOURCE_FP,
        registered_at=registered_at,
    )


def test_contract_identity_and_collection() -> None:
    """Certify stable L10A2 identity and dedicated collection."""
    assert VERSION == "v1.0.0-L10A2-LEGAL-EVIDENCE-CONTENT-REGISTRY"
    assert COLLECTION == "legal_evidence_contents"


def test_indexes_are_exact_and_have_no_ttl() -> None:
    """Certify immutable/read indexes and deliberate absence of TTL deletion."""
    collection = Collection()
    ensure_indexes(collection)

    by_name = {
        options["name"]: (keys, options)
        for keys, options in collection.indexes
    }

    assert set(by_name) == {
        REFERENCE_INDEX_NAME,
        DOCUMENT_INDEX_NAME,
        CONTENT_FINGERPRINT_INDEX_NAME,
    }
    assert by_name[REFERENCE_INDEX_NAME][1]["unique"] is True
    assert by_name[DOCUMENT_INDEX_NAME][1]["unique"] is False
    assert by_name[CONTENT_FINGERPRINT_INDEX_NAME][1]["unique"] is False

    for _, options in collection.indexes:
        assert "expireAfterSeconds" not in options


@pytest.mark.parametrize(
    "operation",
    [
        "persist",
        "get",
        "bytes",
        "list",
    ],
)
def test_active_transaction_is_mandatory(operation: str) -> None:
    """Certify no operational read/write occurs outside caller transaction."""
    collection = Collection()
    item = value()

    with pytest.raises(
        LegalEvidenceContentRegistryTransactionRequiredError,
    ):
        if operation == "persist":
            persist_evidence_content(
                item,
                CONTENT,
                collection,
                session=None,
            )
        elif operation == "get":
            get_evidence_content(
                TENANT,
                item.content_reference,
                collection,
                session=InactiveSession(),
            )
        elif operation == "bytes":
            read_evidence_content_bytes(
                TENANT,
                item.content_reference,
                collection,
                session=None,
            )
        else:
            list_document_evidence_contents(
                TENANT,
                MATTER,
                DOCUMENT,
                collection,
                session=InactiveSession(),
            )


def test_persist_and_exact_replay_return_same_canonical_value() -> None:
    """Certify one write and zero-divergence replay semantics."""
    collection = Collection()
    session = Session()
    item = value()

    first = persist_evidence_content(
        item,
        CONTENT,
        collection,
        session=session,
    )
    second = persist_evidence_content(
        item,
        CONTENT,
        collection,
        session=session,
    )

    assert first == item
    assert second == item
    assert len(collection.rows) == 1
    assert collection.rows[0]["content_bytes"] == CONTENT
    assert all(observed is session for observed in collection.sessions)


def test_different_bytes_cannot_replay_same_value() -> None:
    """Certify bytes must remain correlated to immutable metadata."""
    collection = Collection()
    item = value()
    persist_evidence_content(
        item,
        CONTENT,
        collection,
        session=Session(),
    )

    with pytest.raises(Exception, match="L10A2_CONTENT_CORRELATION_INVALID"):
        persist_evidence_content(
            item,
            CONTENT + b"divergent",
            collection,
            session=Session(),
        )


def test_same_reference_with_divergent_metadata_conflicts() -> None:
    """Certify immutable reference cannot acquire divergent provenance."""
    collection = Collection()
    original = value()
    persist_evidence_content(
        original,
        CONTENT,
        collection,
        session=Session(),
    )

    changed = LegalEvidenceContent(
        tenant_id=original.tenant_id,
        case_matter_id=original.case_matter_id,
        document_id=original.document_id,
        content_reference=original.content_reference,
        media_type=original.media_type,
        original_filename=original.original_filename,
        content_length=original.content_length,
        content_fingerprint=original.content_fingerprint,
        source_evidence_reference="different-source",
        source_evidence_fingerprint=original.source_evidence_fingerprint,
        registered_at=original.registered_at,
    )

    with pytest.raises(
        LegalEvidenceContentRegistryConflictError,
    ):
        persist_evidence_content(
            changed,
            CONTENT,
            collection,
            session=Session(),
        )


def test_read_metadata_and_bytes_reverify_exact_content() -> None:
    """Certify read APIs expose only content that passes byte integrity proof."""
    collection = Collection()
    item = value()
    persist_evidence_content(
        item,
        CONTENT,
        collection,
        session=Session(),
    )

    assert (
        get_evidence_content(
            TENANT,
            item.content_reference,
            collection,
            session=Session(),
        )
        == item
    )
    assert (
        read_evidence_content_bytes(
            TENANT,
            item.content_reference,
            collection,
            session=Session(),
        )
        == CONTENT
    )


def test_cross_tenant_reference_is_absent() -> None:
    """Certify exact content reference does not disclose across tenant scope."""
    collection = Collection()
    item = value()
    persist_evidence_content(
        item,
        CONTENT,
        collection,
        session=Session(),
    )

    with pytest.raises(
        LegalEvidenceContentRegistryNotFoundError,
    ):
        get_evidence_content(
            "tenant-other",
            item.content_reference,
            collection,
            session=Session(),
        )


def test_corrupt_persisted_bytes_fail_closed() -> None:
    """Certify durable byte corruption is detected on metadata and byte reads."""
    collection = Collection()
    item = value()
    persist_evidence_content(
        item,
        CONTENT,
        collection,
        session=Session(),
    )
    collection.rows[0]["content_bytes"] = CONTENT + b"tampered"

    with pytest.raises(
        LegalEvidenceContentRegistryPersistedRecordInvalidError,
    ):
        get_evidence_content(
            TENANT,
            item.content_reference,
            collection,
            session=Session(),
        )

    with pytest.raises(
        LegalEvidenceContentRegistryPersistedRecordInvalidError,
    ):
        read_evidence_content_bytes(
            TENANT,
            item.content_reference,
            collection,
            session=Session(),
        )


def test_corrupt_persisted_metadata_fails_closed() -> None:
    """Certify durable metadata fingerprint drift cannot hydrate."""
    collection = Collection()
    item = value()
    persist_evidence_content(
        item,
        CONTENT,
        collection,
        session=Session(),
    )
    collection.rows[0]["original_filename"] = "tampered.pdf"

    with pytest.raises(
        LegalEvidenceContentRegistryPersistedRecordInvalidError,
    ):
        get_evidence_content(
            TENANT,
            item.content_reference,
            collection,
            session=Session(),
        )


def test_document_listing_is_exact_scope_and_newest_first() -> None:
    """Certify exact tenant/matter/document list boundary and chronology."""
    collection = Collection()
    first_content = CONTENT
    second_content = CONTENT + b"v2"

    first = value(
        content=first_content,
        registered_at=NOW,
        source_reference="upload:first",
    )
    second = value(
        content=second_content,
        registered_at=NOW + timedelta(minutes=1),
        source_reference="upload:second",
    )

    persist_evidence_content(
        first,
        first_content,
        collection,
        session=Session(),
    )
    persist_evidence_content(
        second,
        second_content,
        collection,
        session=Session(),
    )

    listed = list_document_evidence_contents(
        TENANT,
        MATTER,
        DOCUMENT,
        collection,
        session=Session(),
    )

    assert listed == (second, first)

    assert (
        list_document_evidence_contents(
            "tenant-other",
            MATTER,
            DOCUMENT,
            collection,
            session=Session(),
        )
        == ()
    )


def test_duplicate_insert_race_requires_whole_transaction_retry() -> None:
    """Certify registry does not reconcile a duplicate race inside transaction."""
    collection = DuplicateRaceCollection()
    item = value()

    with pytest.raises(
        LegalEvidenceContentRegistryRetryRequiredError,
    ):
        persist_evidence_content(
            item,
            CONTENT,
            collection,
            session=Session(),
        )


def test_registry_has_no_update_delete_or_downstream_authority_methods() -> None:
    """Certify L10A2 cannot mutate lifecycle, Court or financial truth."""
    from tools.eos.legal_operations.registry.legal_evidence_content_registry import (
        LegalEvidenceContentRegistry,
    )

    public = {
        name
        for name in dir(LegalEvidenceContentRegistry)
        if not name.startswith("_")
    }

    forbidden = {
        "update",
        "delete",
        "expire",
        "submit_to_court",
        "mark_filed",
        "advance_document",
        "transfer_custody",
        "authorize_service",
        "authorize_payment",
        "execute_payment",
        "settle",
    }

    assert forbidden.isdisjoint(public)


# ARTIFACT: test_legal_evidence_content_registry.py
# VERSION: v1.0.0-L10A2-LEGAL-EVIDENCE-CONTENT-REGISTRY-CERT
# AUTHORITY BOUNDARY: direct immutable Legal evidence-content registry certificate only
# TENANT POSTURE: exact tenant/matter/document scope with cross-tenant absence proof
# FAIL-CLOSED POSTURE: transaction/divergence/corruption/race failures reject
# FINANCIAL EXECUTION AUTHORITY: none; Kennel EOS remains exclusive
# END OF WILSY OS SOVEREIGN ARTIFACT
