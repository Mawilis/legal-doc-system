from __future__ import annotations

from datetime import datetime, timezone

import pytest

from tools.eos.security.forensic_merkle_registry import (
    COLLECTION_NAME,
    ForensicEvidenceUnavailable,
    compute_merkle_root,
    extract_event_seal,
    read_tenant_forensic_chain,
    replay_hash_chain,
    sha3_512_hex,
    stable_json,
)


class FakeCursor(list):
    def sort(self, _spec):
        return self

    def limit(self, value):
        self.requested_limit = value
        return self


class FakeCollection:
    def __init__(self, rows):
        self.rows = rows
        self.query = None
        self.projection = None
        self.cursor = FakeCursor(rows)

    def find(self, query, projection):
        self.query = query
        self.projection = projection
        return self.cursor


class FakeDatabase:
    def __init__(self, rows):
        self.collection = FakeCollection(rows)
        self.name = None

    def __getitem__(self, name):
        self.name = name
        return self.collection


def _entry(tenant_id: str, position: int, previous: str = "") -> dict:
    seal = sha3_512_hex(stable_json({
        "tenantId": tenant_id,
        "traceId": f"trace-{position}",
        "eventType": "DOCUMENT_CREATED",
        "performedBy": "principal-1",
        "status": "SUCCESS",
        "timestamp": datetime(2026, 11, 8, 10, 0, position, tzinfo=timezone.utc),
        "metadata": {"document": f"doc-{position}"},
    }))
    return {
        "_id": f"row-{position}",
        "tenantId": tenant_id,
        "traceId": f"trace-{position}",
        "eventType": "DOCUMENT_CREATED",
        "performedBy": "principal-1",
        "status": "SUCCESS",
        "timestamp": datetime(2026, 11, 8, 10, 0, position, tzinfo=timezone.utc),
        "metadata": {"document": f"doc-{position}"},
        "eventSeal": seal,
        "chainPosition": position,
        "chainHash": sha3_512_hex(previous + seal),
    }


def test_sha3_and_merkle_root_are_deterministic_with_duplicate_last_balance():
    leaves = ["A" * 128, "B" * 128, "C" * 128]
    expected = sha3_512_hex(sha3_512_hex(leaves[0] + leaves[1]) + sha3_512_hex(leaves[2] + leaves[2]))
    assert compute_merkle_root(leaves) == expected
    assert compute_merkle_root([]) is None


def test_replay_accepts_valid_chain_and_reports_exact_terminal_hash():
    first = _entry("TENANT-A", 1)
    second = _entry("TENANT-A", 2, first["chainHash"])
    result = replay_hash_chain([first, second])
    assert result["valid"] is True
    assert result["mismatches"] == []
    assert result["lastPosition"] == 2
    assert result["lastHash"] == second["chainHash"]


def test_replay_detects_tampered_chain_hash_without_mutating_rows():
    entry = _entry("TENANT-A", 1)
    entry["chainHash"] = "F" * 128
    original = dict(entry)
    result = replay_hash_chain([entry])
    assert result["valid"] is False
    assert result["mismatches"][0]["actual"] == "F" * 128
    assert entry == original


def test_missing_event_seal_is_derived_and_counted_not_silently_promoted():
    entry = _entry("TENANT-A", 1)
    entry.pop("eventSeal")
    seal, derived = extract_event_seal(entry)
    assert len(seal) == 128
    assert derived is True
    result = replay_hash_chain([entry])
    assert result["derivedSealCount"] == 1


def test_tenant_read_uses_exact_tenant_partition_and_reports_no_evidence_as_silent():
    database = FakeDatabase([])
    result = read_tenant_forensic_chain(database, "TENANT-A", limit=50)
    assert database.name == COLLECTION_NAME
    assert database.collection.query == {"tenantId": "TENANT-A"}
    assert result["sourceStatus"] == "SOURCE_SILENT"
    assert result["verified"] is False
    assert result["merkleRoot"] is None
    assert result["anchorMode"] == "NOT_CONFIGURED"


def test_tenant_read_returns_replayed_evidence_and_never_claims_external_anchor():
    first = _entry("TENANT-A", 1)
    second = _entry("TENANT-A", 2, first["chainHash"])
    database = FakeDatabase([second, first])
    result = read_tenant_forensic_chain(database, "TENANT-A", limit=50)
    assert result["verified"] is True
    assert result["chainLength"] == 2
    assert [row["id"] for row in result["replay"]] == ["row-1", "row-2"]
    assert result["anchorProvider"] == "NONE"
    assert database.collection.query == {"tenantId": "TENANT-A"}


def test_database_and_tenant_scope_fail_closed():
    with pytest.raises(ForensicEvidenceUnavailable):
        read_tenant_forensic_chain(None, "TENANT-A")
    with pytest.raises(ValueError, match="FORENSIC_TENANT_SCOPE_REQUIRED"):
        read_tenant_forensic_chain(FakeDatabase([]), "  ")


def test_replay_limit_is_bounded():
    database = FakeDatabase([])
    read_tenant_forensic_chain(database, "TENANT-A", limit=999_999)
    assert database.collection.cursor.requested_limit == 20_000
