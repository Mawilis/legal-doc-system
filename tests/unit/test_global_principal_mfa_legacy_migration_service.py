from __future__ import annotations

from datetime import datetime, timezone
from types import SimpleNamespace
from typing import Any, cast

import pyotp
import pytest

from tools.eos.auth.principal_status import PrincipalStatus
from pymongo.errors import DuplicateKeyError

from tools.eos.auth.global_principal_mfa_legacy_migration_service import (
    GlobalPrincipalMfaLegacyMigrationCodeRejected,
    GlobalPrincipalMfaLegacyMigrationRejected,
    GlobalPrincipalMfaLegacyMigrationService,
)

NOW = datetime(2026, 11, 3, 12, 0, 0, tzinfo=timezone.utc)
SECRET = "JBSWY3DPEHPK3PXP"


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
    def __init__(self, rows=None):
        self.rows = [dict(row) for row in (rows or [])]

    def find(self, query, *, session=None):
        assert session is not None
        return _Cursor([dict(row) for row in self.rows if row.get("user_id") == query.get("user_id")])

    def update_one(self, query, update, *, upsert=False, session=None):
        assert session is not None
        for row in self.rows:
            matches_or = any(
                (condition.get("status", {}).get("$ne") is not None and row.get("status") != condition["status"]["$ne"])
                or (condition.get("credential_revision", {}).get("$ne") is not None and row.get("credential_revision") != condition["credential_revision"]["$ne"])
                for condition in query.get("$or", [])
            )
            if row.get("principal_id") == query.get("principal_id") and matches_or:
                row.update(update["$set"])
                return SimpleNamespace(matched_count=1, upserted_id=None)
        if upsert:
            if any(row.get("principal_id") == query.get("principal_id") for row in self.rows):
                raise DuplicateKeyError("unique principal factor")
            row = {"principal_id": query["principal_id"], **update["$set"]}
            self.rows.append(row)
            return SimpleNamespace(matched_count=0, upserted_id="new-factor")
        return SimpleNamespace(matched_count=0, upserted_id=None)


class _Credentials:
    def __init__(self, *, mfa_enabled=True, revision=7):
        self.value = SimpleNamespace(
            principal_id="principal-global",
            credential_revision=revision,
            mfa_enabled=mfa_enabled,
        )

    def get_by_principal(self, principal_id, *, session=None):
        assert session is not None
        assert principal_id == "principal-global"
        return self.value

    def enable_mfa(self, principal_id, expected_revision, *, session=None):
        assert session is not None
        assert principal_id == self.value.principal_id
        assert self.value.credential_revision == expected_revision
        assert self.value.mfa_enabled is False
        self.value = SimpleNamespace(
            principal_id=principal_id,
            credential_revision=expected_revision + 1,
            mfa_enabled=True,
        )
        return self.value


class _Principals:
    def __init__(self, status=PrincipalStatus.ACTIVE):
        self.value = SimpleNamespace(principal_id="principal-global", status=status)

    def get(self, principal_id, *, session=None):
        assert session is not None
        assert principal_id == "principal-global"
        return self.value


class _Kms:
    def __init__(self):
        self.values = {}

    def encrypt_secret(self, *, secret, principal_id, credential_revision):
        envelope_id = f"encrypted-{len(self.values) + 1}"
        self.values[envelope_id] = (secret, principal_id, credential_revision)
        return {
            "schema": "TEST_KMS",
            "ciphertext_reference": envelope_id,
            "principal_id": principal_id,
            "credential_revision": credential_revision,
        }


def _service(*, legacy_rows=None, factor_rows=None, mfa_enabled=True, principal_status=PrincipalStatus.ACTIVE):
    legacy = _Collection(
        [{"user_id": "principal-global", "secret": SECRET}]
        if legacy_rows is None
        else legacy_rows
    )
    factors = _Collection(factor_rows)
    kms = _Kms()
    service = GlobalPrincipalMfaLegacyMigrationService(
        kms=kms,
        legacy_factor_collection=cast(Any, legacy),
        factor_collection=cast(Any, factors),
        credential_repository=_Credentials(mfa_enabled=mfa_enabled),
        principal_repository=_Principals(principal_status),
    )
    return service, legacy, factors, kms


def test_migration_requires_password_verified_current_global_credential_and_legacy_totp_proof():
    service, legacy, factors, kms = _service()
    code = pyotp.TOTP(SECRET).at(NOW)
    receipt = service.migrate(
        principal_id="principal-global",
        credential_revision=7,
        code=code,
        session=_Session(),
        now=NOW,
    )
    assert receipt.principal_id == "principal-global"
    assert receipt.credential_revision == 7
    assert len(factors.rows) == 1
    factor = factors.rows[0]
    assert factor["status"] == "ACTIVE"
    assert factor["credential_revision"] == 7
    assert factor["migration_source"] == "LEGACY_OTP_SECRET_PROOF"
    assert factor["encrypted_secret"]["schema"] == "TEST_KMS"
    assert SECRET not in repr(factor)
    assert kms.values[factor["encrypted_secret"]["ciphertext_reference"]] == (
        SECRET, "principal-global", 7
    )
    # The legacy row is retained until the tenant-bound authentication cutover.
    assert legacy.rows == [{"user_id": "principal-global", "secret": SECRET}]



def test_legacy_factor_proof_enables_stale_mfa_flag_and_rebinds_envelope_to_new_revision():
    service, _legacy, factors, kms = _service(mfa_enabled=False)
    receipt = service.migrate(
        principal_id="principal-global",
        credential_revision=7,
        code=pyotp.TOTP(SECRET).at(NOW),
        session=_Session(),
        now=NOW,
    )
    factor = factors.rows[0]
    assert receipt.credential_revision == 8
    assert factor["credential_revision"] == 8
    assert factor["encrypted_secret"]["credential_revision"] == 8
    assert kms.values[factor["encrypted_secret"]["ciphertext_reference"]] == (
        SECRET, "principal-global", 8
    )


def test_invalid_legacy_totp_code_is_rejected_without_global_factor_write():
    service, _legacy, factors, _kms = _service()
    with pytest.raises(GlobalPrincipalMfaLegacyMigrationCodeRejected, match="CODE_INVALID"):
        service.migrate(
            principal_id="principal-global",
            credential_revision=7,
            code="000000",
            session=_Session(),
            now=NOW,
        )
    assert factors.rows == []


def test_ambiguous_legacy_factor_rows_are_quarantined():
    service, _legacy, factors, _kms = _service(
        legacy_rows=[
            {"user_id": "principal-global", "secret": SECRET},
            {"user_id": "principal-global", "secret": SECRET},
        ]
    )
    with pytest.raises(GlobalPrincipalMfaLegacyMigrationRejected, match="NOT_UNIQUE"):
        service.migrate(
            principal_id="principal-global",
            credential_revision=7,
            code=pyotp.TOTP(SECRET).at(NOW),
            session=_Session(),
            now=NOW,
        )
    assert factors.rows == []


def test_migration_requires_active_global_principal_and_existing_mfa_enrollment():
    inactive, *_ = _service(principal_status=PrincipalStatus.SUSPENDED)
    with pytest.raises(GlobalPrincipalMfaLegacyMigrationRejected, match="PRINCIPAL_NOT_ACTIVE"):
        inactive.migrate(
            principal_id="principal-global",
            credential_revision=7,
            code=pyotp.TOTP(SECRET).at(NOW),
            session=_Session(),
            now=NOW,
        )
    not_enrolled, *_ = _service(mfa_enabled=False, legacy_rows=[])
    with pytest.raises(GlobalPrincipalMfaLegacyMigrationRejected, match="LEGACY_FACTOR_NOT_UNIQUE"):
        not_enrolled.migrate(
            principal_id="principal-global",
            credential_revision=7,
            code=pyotp.TOTP(SECRET).at(NOW),
            session=_Session(),
            now=NOW,
        )


def test_migration_does_not_replace_an_already_current_active_factor():
    current = {
        "principal_id": "principal-global",
        "credential_revision": 7,
        "status": "ACTIVE",
        "encrypted_secret": {"schema": "EXISTING"},
    }
    service, _legacy, factors, _kms = _service(factor_rows=[current])
    with pytest.raises(GlobalPrincipalMfaLegacyMigrationRejected, match="ALREADY_CURRENT"):
        service.migrate(
            principal_id="principal-global",
            credential_revision=7,
            code=pyotp.TOTP(SECRET).at(NOW),
            session=_Session(),
            now=NOW,
        )
    assert factors.rows == [current]
