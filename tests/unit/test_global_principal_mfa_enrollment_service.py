from __future__ import annotations

from datetime import datetime, timezone
from types import SimpleNamespace
from typing import Any, cast

import pyotp
import pytest

from tools.eos.auth.global_principal_mfa_enrollment_service import (
    GlobalPrincipalMfaEnrollmentRejected,
    GlobalPrincipalMfaEnrollmentService,
)

NOW = datetime(2026, 11, 3, 12, 0, 0, tzinfo=timezone.utc)


class _Session:
    in_transaction = True


class _Cursor:
    def __init__(self, rows):
        self.rows = rows

    def limit(self, count):
        self.rows = self.rows[:count]
        return self

    def __iter__(self):
        return iter(self.rows)


class _Collection:
    def __init__(self) -> None:
        self.rows: list[dict[str, Any]] = []
        self.indexes: list[tuple[Any, dict[str, Any]]] = []

    def create_index(self, keys, **kwargs):
        self.indexes.append((keys, kwargs))
        return kwargs.get("name")

    @staticmethod
    def _matches(row, query):
        for key, expected in query.items():
            actual = row.get(key)
            if isinstance(expected, dict):
                if "$lte" in expected and not (actual is not None and actual <= expected["$lte"]):
                    return False
                if "$gt" in expected and not (actual is not None and actual > expected["$gt"]):
                    return False
                if "$ne" in expected and actual == expected["$ne"]:
                    return False
            elif actual != expected:
                return False
        return True

    def find(self, query, *, session=None):
        assert session is not None
        return _Cursor(
            [dict(row) for row in self.rows if self._matches(row, query)]
        )

    def delete_many(self, query, *, session=None):
        assert session is not None
        before = len(self.rows)
        self.rows = [row for row in self.rows if not self._matches(row, query)]
        return SimpleNamespace(deleted_count=before - len(self.rows))

    def find_one(self, query, *, session=None):
        assert session is not None
        return next((dict(row) for row in self.rows if self._matches(row, query)), None)

    def insert_one(self, document, *, session=None):
        assert session is not None
        if any(
            row.get("principal_id") == document.get("principal_id")
            or row.get("challenge_digest") == document.get("challenge_digest")
            for row in self.rows
        ):
            from pymongo.errors import DuplicateKeyError
            raise DuplicateKeyError("duplicate")
        row = dict(document)
        row["_id"] = f"row-{len(self.rows) + 1}"
        self.rows.append(row)
        return SimpleNamespace(inserted_id=row["_id"])

    def update_one(self, query, update, *, upsert=False, session=None):
        assert session is not None
        for row in self.rows:
            if self._matches(row, query):
                row.update(update.get("$set", {}))
                for key, increment in update.get("$inc", {}).items():
                    row[key] = row.get(key, 0) + increment
                return SimpleNamespace(matched_count=1, upserted_id=None)
        if upsert:
            row = dict(query)
            row.update(update["$set"])
            row["_id"] = f"row-{len(self.rows) + 1}"
            self.rows.append(row)
            return SimpleNamespace(matched_count=0, upserted_id=row["_id"])
        return SimpleNamespace(matched_count=0, upserted_id=None)

    def delete_one(self, query, *, session=None):
        assert session is not None
        for index, row in enumerate(self.rows):
            if self._matches(row, query):
                del self.rows[index]
                return SimpleNamespace(deleted_count=1)
        return SimpleNamespace(deleted_count=0)


class _Credentials:
    def __init__(self, *, mfa_enabled=False, revision=3):
        self.current = SimpleNamespace(
            principal_id="principal-global",
            normalized_email="person@example.com",
            credential_revision=revision,
            mfa_enabled=mfa_enabled,
            password_hash="not-used-by-this-service",
        )

    def get_by_principal(self, principal_id, *, session=None):
        assert session is not None
        assert principal_id == self.current.principal_id
        return self.current

    def enable_mfa(self, principal_id, expected_revision, *, session=None):
        assert session is not None
        assert principal_id == self.current.principal_id
        assert self.current.credential_revision == expected_revision
        assert self.current.mfa_enabled is False
        self.current = SimpleNamespace(
            **{
                **vars(self.current),
                "credential_revision": expected_revision + 1,
                "mfa_enabled": True,
            }
        )
        return self.current


class _Kms:
    def __init__(self):
        self.secrets: dict[str, tuple[str, str, int]] = {}

    def encrypt_secret(self, *, secret, principal_id, credential_revision):
        envelope_id = f"cipher-{len(self.secrets) + 1}"
        self.secrets[envelope_id] = (secret, principal_id, credential_revision)
        return {
            "schema": "TEST_KMS_ENVELOPE",
            "ciphertext_reference": envelope_id,
            "principal_id": principal_id,
            "credential_revision": credential_revision,
        }

    def decrypt_secret(self, envelope, *, principal_id, credential_revision):
        stored = self.secrets[envelope["ciphertext_reference"]]
        if stored[1:] != (principal_id, credential_revision):
            raise ValueError("context mismatch")
        return stored[0]


def _service(mfa_enabled=False, legacy_rows=None):
    challenges = _Collection()
    factors = _Collection()
    legacy_factors = _Collection()
    legacy_factors.rows = [dict(row) for row in (legacy_rows or [])]
    credentials = _Credentials(mfa_enabled=mfa_enabled)
    kms = _Kms()
    service = GlobalPrincipalMfaEnrollmentService(
        kms=kms,
        challenge_collection=cast(Any, challenges),
        factor_collection=cast(Any, factors),
        legacy_factor_collection=cast(Any, legacy_factors),
        credential_repository=credentials,
    )
    return service, challenges, factors, credentials, kms


def test_issue_returns_secret_once_and_persists_only_encrypted_seed():
    service, challenges, _factors, _credentials, _kms = _service()
    receipt = service.issue(
        principal_id="principal-global",
        credential_revision=3,
        session=_Session(),
        now=NOW,
    )
    assert receipt.secret
    assert receipt.secret in receipt.provisioning_uri
    assert receipt.challenge_token
    assert len(challenges.rows) == 1
    persisted = challenges.rows[0]
    assert persisted["encrypted_secret"]["schema"] == "TEST_KMS_ENVELOPE"
    assert "secret" not in persisted
    assert receipt.secret not in repr(persisted)
    assert receipt.challenge_token not in repr(persisted)
    assert persisted["challenge_digest"] != receipt.challenge_token


def test_issue_rejects_password_only_reenrollment_when_mfa_is_already_enabled():
    service, *_ = _service(mfa_enabled=True)
    with pytest.raises(GlobalPrincipalMfaEnrollmentRejected, match="GLOBAL_MFA_RECOVERY_REQUIRED"):
        service.issue(
            principal_id="principal-global",
            credential_revision=3,
            session=_Session(),
            now=NOW,
        )



def test_first_time_enrollment_cannot_bypass_an_existing_legacy_factor():
    service, *_ = _service(
        mfa_enabled=False,
        legacy_rows=[{"user_id": "principal-global", "secret": "legacy-secret"}],
    )
    with pytest.raises(GlobalPrincipalMfaEnrollmentRejected, match="GLOBAL_MFA_RECOVERY_REQUIRED"):
        service.issue(
            principal_id="principal-global",
            credential_revision=3,
            session=_Session(),
            now=NOW,
        )


def test_issue_allows_only_one_unexpired_pending_enrollment():
    service, *_ = _service()
    service.issue(
        principal_id="principal-global",
        credential_revision=3,
        session=_Session(),
        now=NOW,
    )
    with pytest.raises(GlobalPrincipalMfaEnrollmentRejected, match="GLOBAL_MFA_ENROLLMENT_ALREADY_PENDING"):
        service.issue(
            principal_id="principal-global",
            credential_revision=3,
            session=_Session(),
            now=NOW,
        )


def test_confirm_enables_mfa_and_reencrypts_seed_at_new_credential_revision():
    service, challenges, factors, credentials, _kms = _service()
    receipt = service.issue(
        principal_id="principal-global",
        credential_revision=3,
        session=_Session(),
        now=NOW,
    )
    code = pyotp.TOTP(receipt.secret, digits=6, interval=30).at(NOW)
    completion = service.confirm(
        challenge_token=receipt.challenge_token,
        code=code,
        session=_Session(),
        now=NOW,
    )
    assert completion.principal_id == "principal-global"
    assert completion.credential_revision == 4
    assert credentials.current.mfa_enabled is True
    assert credentials.current.credential_revision == 4
    assert len(factors.rows) == 1
    factor = factors.rows[0]
    assert factor["status"] == "ACTIVE"
    assert factor["credential_revision"] == 4
    assert factor["encrypted_secret"]["credential_revision"] == 4
    assert factor["last_accepted_step"] == pyotp.TOTP(receipt.secret, interval=30).timecode(NOW)
    assert receipt.secret not in repr(factor)
    assert challenges.rows == []


def test_invalid_confirmation_code_does_not_enable_or_consume_enrollment():
    service, challenges, factors, credentials, _kms = _service()
    receipt = service.issue(
        principal_id="principal-global",
        credential_revision=3,
        session=_Session(),
        now=NOW,
    )
    with pytest.raises(GlobalPrincipalMfaEnrollmentRejected, match="GLOBAL_MFA_ENROLLMENT_CODE_INVALID"):
        service.confirm(
            challenge_token=receipt.challenge_token,
            code="000000",
            session=_Session(),
            now=NOW,
        )
    assert credentials.current.mfa_enabled is False
    assert credentials.current.credential_revision == 3
    assert len(challenges.rows) == 1
    assert challenges.rows[0]["attempt_count"] == 1
    assert factors.rows == []


def test_enrollment_challenge_locks_after_five_invalid_codes():
    service, challenges, *_ = _service()
    receipt = service.issue(
        principal_id="principal-global",
        credential_revision=3,
        session=_Session(),
        now=NOW,
    )
    for _ in range(5):
        with pytest.raises(GlobalPrincipalMfaEnrollmentRejected, match="CODE_INVALID"):
            service.confirm(
                challenge_token=receipt.challenge_token,
                code="000000",
                session=_Session(),
                now=NOW,
            )
    assert challenges.rows[0]["attempt_count"] == 5
    assert challenges.rows[0]["status"] == "LOCKED"
    with pytest.raises(GlobalPrincipalMfaEnrollmentRejected, match="INVALID_EXPIRED_OR_CONSUMED"):
        service.confirm(
            challenge_token=receipt.challenge_token,
            code="000000",
            session=_Session(),
            now=NOW,
        )


def test_confirmation_challenge_is_single_use():
    service, *_ = _service()
    receipt = service.issue(
        principal_id="principal-global",
        credential_revision=3,
        session=_Session(),
        now=NOW,
    )
    code = pyotp.TOTP(receipt.secret, digits=6, interval=30).at(NOW)
    service.confirm(
        challenge_token=receipt.challenge_token,
        code=code,
        session=_Session(),
        now=NOW,
    )
    with pytest.raises(GlobalPrincipalMfaEnrollmentRejected, match="INVALID_EXPIRED_OR_CONSUMED"):
        service.confirm(
            challenge_token=receipt.challenge_token,
            code=code,
            session=_Session(),
            now=NOW,
        )


def test_expired_enrollment_challenge_is_rejected():
    service, *_ = _service()
    receipt = service.issue(
        principal_id="principal-global",
        credential_revision=3,
        session=_Session(),
        now=NOW,
    )
    with pytest.raises(GlobalPrincipalMfaEnrollmentRejected, match="INVALID_EXPIRED_OR_CONSUMED"):
        service.confirm(
            challenge_token=receipt.challenge_token,
            code="123456",
            session=_Session(),
            now=NOW.replace(minute=NOW.minute + 6),
        )


def test_enrollment_requires_caller_owned_transaction():
    service, *_ = _service()
    with pytest.raises(GlobalPrincipalMfaEnrollmentRejected, match="TRANSACTION_REQUIRED"):
        service.issue(
            principal_id="principal-global",
            credential_revision=3,
            session=object(),
            now=NOW,
        )
