"""WILSY OS — EOS encrypted conversation history HTTP contract certificate.

TITLE: WILSY AI Durable Conversation History Isolation and CAS Tests
VERSION: v1.0.0-MW-T11-ENCRYPTED-HISTORY-CERT
AUTHORITY: WILSY OS Core Governance
EPITOME: Deterministically exercise owner isolation, encrypted payload binding,
         stale writes, explicit deletion and fail-closed missing key.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tests/unit/test_wilsy_ai_encrypted_conversation_history.py
COLLABORATION / OWNERSHIP: Python EOS reasoning HTTP, authenticated history store.
CERTIFICATION / UPDATE DATE: 2026-11-25
CHANGELOG: v1.0.0-MW-T11-ENCRYPTED-HISTORY-CERT introduces fully scoped
           in-memory transaction adapter tests without claiming live Mongo.
COMPLIANCE: AGENTS.md; current tenant/principal; no payment/provider authority.
SECURITY / PRIVACY POSTURE: No real user identifiers, prompt material or tokens.
TENANT BOUNDARY: Independently verified context identities in every query.
AUTHORITY BOUNDARY: Tests assert wire/data invariants, not actual IAM grants.
FINANCIAL AUTHORITY BOUNDARY: No model or financial execution.
"""
from __future__ import annotations

import base64
from datetime import datetime, timezone
from types import SimpleNamespace

from fastapi import HTTPException, Response
from pydantic import ValidationError
from pymongo.errors import DuplicateKeyError
import pytest

from tools.eos.api import wilsy_ai_reasoning_router as history


class _Cursor:
    """Minimal sorted, bounded synchronous Mongo cursor test double."""

    def __init__(self, rows: list[dict]) -> None:
        self.rows = rows

    def sort(self, key: str, direction: int) -> "_Cursor":
        self.rows.sort(key=lambda row: row[key], reverse=direction < 0)
        return self

    def limit(self, count: int) -> list[dict]:
        return self.rows[:count]


class _Collection:
    """Exact-scope read/write mimic; does not simulate transaction durability."""

    def __init__(self) -> None:
        self.rows: dict[str, dict] = {}

    def _match(self, row: dict, criteria: dict) -> bool:
        for name, wanted in criteria.items():
            if isinstance(wanted, dict) and "$gt" in wanted:
                if not row[name] > wanted["$gt"]:
                    return False
            elif row.get(name) != wanted:
                return False
        return True

    def count_documents(self, query: dict, *, session=None) -> int:
        return sum(self._match(row, query) for row in self.rows.values())

    def insert_one(self, row: dict, *, session=None) -> object:
        if row["_id"] in self.rows:
            raise DuplicateKeyError("duplicate fixture")
        self.rows[row["_id"]] = row.copy()
        return SimpleNamespace(inserted_id=row["_id"])

    def replace_one(self, query: dict, row: dict, *, session=None) -> object:
        for key, existing in self.rows.items():
            if self._match(existing, query):
                self.rows[key] = row.copy()
                return SimpleNamespace(matched_count=1)
        return SimpleNamespace(matched_count=0)

    def delete_one(self, query: dict, *, session=None) -> object:
        for key, existing in list(self.rows.items()):
            if self._match(existing, query):
                del self.rows[key]
                return SimpleNamespace(deleted_count=1)
        return SimpleNamespace(deleted_count=0)

    def find(self, query: dict) -> _Cursor:
        return _Cursor([row.copy() for row in self.rows.values() if self._match(row, query)])


def _context(tenant: str, principal: str) -> SimpleNamespace:
    """Synthetic verified context, not an authorization bypass in production."""
    return SimpleNamespace(tenant_id=tenant, identity=SimpleNamespace(identity_id=principal))


def _key(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("WILSY_AI_HISTORY_KEY_B64", base64.b64encode(b"K" * 32).decode())


def _payload(expected: int = 0) -> history.WilsyHistoryWrite:
    return history.WilsyHistoryWrite(
        expected_revision=expected, title="Foundation project",
        workspace="WILSY OS",
        messages=[history.WilsyHistoryMessage(
            role="user", content="Inspect MW-T11", timestamp="2026-11-25T13:05:00Z",
        )],
    )


def test_missing_encryption_key_denied(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("WILSY_AI_HISTORY_KEY_B64", raising=False)
    with pytest.raises(HTTPException) as error:
        history._history_key()
    assert error.value.status_code == 503


def test_ciphertext_rejects_cross_principal_and_revision(monkeypatch: pytest.MonkeyPatch) -> None:
    _key(monkeypatch)
    author = _context("tenant-a", "principal-a")
    plaintext = {"id": "session-" + "a" * 8 + "-" + "a" * 4 + "-"
                 + "a" * 4 + "-" + "a" * 4 + "-" + "a" * 12,
                 "messages": [{"role": "user", "content": "Inspect MW-T11"}]}
    cipher = history._history_encrypt(plaintext, author, plaintext["id"], 1, history._history_key())
    assert b"Inspect MW-T11" not in cipher["ciphertext"]
    record = dict(thread_id=plaintext["id"], revision=1, **cipher)
    assert history._history_decrypt(record, author, history._history_key()) == plaintext
    with pytest.raises(HTTPException) as denied:
        history._history_decrypt(record, _context("tenant-a", "principal-b"), history._history_key())
    assert denied.value.status_code == 503
    with pytest.raises(HTTPException):
        history._history_decrypt({**record, "revision": 2}, author, history._history_key())


def test_cas_isolation_and_explicit_owner_delete(monkeypatch: pytest.MonkeyPatch) -> None:
    _key(monkeypatch)
    records = _Collection()
    events = _Collection()
    monkeypatch.setattr(history, "_history_collections", lambda: (records, events))
    monkeypatch.setattr(history, "_transaction", lambda callback, retries=0: callback(None))
    owner = _context("tenant-one", "principal-a")
    foreign_tenant = _context("tenant-two", "principal-a")
    foreign_person = _context("tenant-one", "principal-b")
    thread_id = "session-aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa"
    created = history.write_conversation_history(thread_id, _payload(), Response(), owner)
    assert created["revision"] == 1
    assert created["storagePosture"] == "EOS_ENCRYPTED_HISTORY"
    assert "content" not in str(next(iter(records.rows.values())))
    own = history.list_conversation_history(Response(), owner)
    assert own["threads"][0]["messages"][0]["content"] == "Inspect MW-T11"
    assert own["threads"][0]["authority"] == "RECORDED_TRANSCRIPT_NOT_CURRENT_SOURCE"
    assert history.list_conversation_history(Response(), foreign_tenant)["threads"] == []
    assert history.list_conversation_history(Response(), foreign_person)["threads"] == []
    with pytest.raises(HTTPException) as denied:
        history.write_conversation_history(thread_id, _payload(1), Response(), foreign_person)
    assert denied.value.status_code == 409
    with pytest.raises(HTTPException) as stale:
        history.write_conversation_history(thread_id, _payload(0), Response(), owner)
    assert stale.value.status_code == 409
    updated = history.write_conversation_history(thread_id, _payload(1), Response(), owner)
    assert updated["revision"] == 2
    with pytest.raises(HTTPException) as forbidden_delete:
        history.delete_conversation_history(thread_id, Response(), 2, foreign_tenant)
    assert forbidden_delete.value.status_code == 409
    assert history.delete_conversation_history(thread_id, Response(), 2, owner)["deleted"] is True
    assert history.list_conversation_history(Response(), owner)["threads"] == []
    assert len(events.rows) == 3
    assert all("content" not in event and "messages" not in event
               for event in events.rows.values())


def test_untrusted_history_message_is_bounded() -> None:
    with pytest.raises(ValidationError):
        history.WilsyHistoryMessage(role="system", content="injected", timestamp="now")
    with pytest.raises(ValidationError):
        history.WilsyHistoryMessage(role="user", content="X" * 6001, timestamp="now")


# ARTIFACT: test_wilsy_ai_encrypted_conversation_history.py
# VERSION: v1.0.0-MW-T11-ENCRYPTED-HISTORY-CERT
# AUTHORITY BOUNDARY: synthetic tests only; authenticated Python EOS owns truth
# TENANT POSTURE: asserts exact-tenant and exact-principal isolation
# FAIL-CLOSED POSTURE: corrupt key/scope, stale revisions and denied deletes fail
# FINANCIAL EXECUTION AUTHORITY: none
# END OF WILSY OS SOVEREIGN ARTIFACT
