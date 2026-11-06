from __future__ import annotations

from datetime import datetime, timezone
from types import SimpleNamespace
from typing import Any

import pyotp
import pytest

from tools.eos.auth.global_principal_totp_verifier import (
    GlobalPrincipalFactorRejected,
    GlobalPrincipalFactorUnavailable,
    GlobalPrincipalTotpVerifier,
)


NOW = datetime(2026, 11, 3, 12, 0, 0, tzinfo=timezone.utc)
SECRET = "JBSWY3DPEHPK3PXP"


class _Cursor:
    def __init__(self, rows: list[dict[str, Any]]) -> None:
        self.rows = rows

    def limit(self, count: int) -> list[dict[str, Any]]:
        return self.rows[:count]


class _Collection:
    def __init__(self, row: dict[str, Any]) -> None:
        self.row = row
        self.updates: list[tuple[dict[str, Any], dict[str, Any], Any]] = []

    def find(self, query: dict[str, Any], *, session: Any = None) -> _Cursor:
        assert session is not None
        return _Cursor([self.row] if self.row.get("principal_id") == query["principal_id"] else [])

    def update_one(
        self,
        query: dict[str, Any],
        update: dict[str, Any],
        *,
        upsert: bool,
        session: Any = None,
    ) -> SimpleNamespace:
        assert upsert is False
        assert session is not None
        self.updates.append((query, update, session))
        current = self.row.get("last_accepted_step")
        if "$or" in query:
            eligible = current is None or current < update["$set"]["last_accepted_step"]
        else:
            eligible = current is not None and current < update["$set"]["last_accepted_step"]
        if not eligible:
            return SimpleNamespace(matched_count=0)
        self.row.update(update["$set"])
        return SimpleNamespace(matched_count=1)


class _Credentials:
    def __init__(self, revision: int = 4) -> None:
        self.revision = revision

    def get_by_principal(self, principal_id: str, *, session: Any = None) -> Any:
        assert principal_id == "principal-global"
        assert session is not None
        return SimpleNamespace(
            principal_id=principal_id,
            credential_revision=self.revision,
            mfa_enabled=True,
        )


class _Transaction:
    in_transaction = True


def _factor() -> dict[str, Any]:
    return {
        "principal_id": "principal-global",
        "status": "ACTIVE",
        "credential_revision": 4,
        "encrypted_secret": "kms-envelope",
    }


def _verifier(collection: _Collection, revision: int = 4) -> GlobalPrincipalTotpVerifier:
    return GlobalPrincipalTotpVerifier(
        collection=collection,
        credential_repository=_Credentials(revision),
        decrypt_secret=lambda envelope, *, principal_id, credential_revision: SECRET if envelope == "kms-envelope" and principal_id == "principal-global" and credential_revision == 4 else "",
    )


def test_valid_factor_consumes_time_step_with_same_transaction() -> None:
    collection = _Collection(_factor())
    session = _Transaction()
    verifier = _verifier(collection)
    code = pyotp.TOTP(SECRET).at(NOW)

    assert verifier.verify(
        principal_id="principal-global",
        credential_revision=4,
        code=code,
        session=session,
        now=NOW,
    ) is True
    assert collection.row["last_accepted_step"] == pyotp.TOTP(SECRET).timecode(NOW)
    assert collection.updates[0][2] is session


def test_same_totp_step_cannot_be_replayed() -> None:
    collection = _Collection(_factor())
    verifier = _verifier(collection)
    code = pyotp.TOTP(SECRET).at(NOW)
    assert verifier.verify(
        principal_id="principal-global", credential_revision=4,
        code=code, session=_Transaction(), now=NOW,
    ) is True
    with pytest.raises(GlobalPrincipalFactorRejected, match="GLOBAL_FACTOR_REPLAYED"):
        verifier.verify(
            principal_id="principal-global", credential_revision=4,
            code=code, session=_Transaction(), now=NOW,
        )


def test_wrong_code_does_not_advance_replay_state() -> None:
    collection = _Collection(_factor())
    assert _verifier(collection).verify(
        principal_id="principal-global", credential_revision=4,
        code="000000", session=_Transaction(), now=NOW,
    ) is False
    assert "last_accepted_step" not in collection.row
    assert collection.updates == []


def test_changed_credential_revision_rejects_factor() -> None:
    collection = _Collection(_factor())
    with pytest.raises(GlobalPrincipalFactorRejected, match="GLOBAL_FACTOR_CREDENTIAL_STALE"):
        _verifier(collection, revision=5).verify(
            principal_id="principal-global", credential_revision=4,
            code=pyotp.TOTP(SECRET).at(NOW), session=_Transaction(), now=NOW,
        )


def test_plaintext_factor_secret_is_rejected() -> None:
    factor = _factor()
    factor["secret"] = SECRET
    collection = _Collection(factor)
    with pytest.raises(GlobalPrincipalFactorRejected, match="GLOBAL_FACTOR_ENROLLMENT_STALE"):
        _verifier(collection).verify(
            principal_id="principal-global", credential_revision=4,
            code=pyotp.TOTP(SECRET).at(NOW), session=_Transaction(), now=NOW,
        )


def test_missing_key_management_capability_fails_closed() -> None:
    collection = _Collection(_factor())
    verifier = GlobalPrincipalTotpVerifier(
        collection=collection, credential_repository=_Credentials()
    )
    with pytest.raises(GlobalPrincipalFactorUnavailable, match="GLOBAL_FACTOR_KEY_SERVICE_UNAVAILABLE"):
        verifier.verify(
            principal_id="principal-global", credential_revision=4,
            code=pyotp.TOTP(SECRET).at(NOW), session=_Transaction(), now=NOW,
        )


def test_verification_requires_caller_owned_active_transaction() -> None:
    collection = _Collection(_factor())
    with pytest.raises(GlobalPrincipalFactorRejected, match="GLOBAL_FACTOR_TRANSACTION_REQUIRED"):
        _verifier(collection).verify(
            principal_id="principal-global", credential_revision=4,
            code=pyotp.TOTP(SECRET).at(NOW), session=object(), now=NOW,
        )
