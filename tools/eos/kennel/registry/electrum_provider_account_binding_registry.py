"""Operator-provisioned Electrum creditor-account to opaque destination binding.

The binding does not select a tenant. The provider UETR must resolve to exactly
one existing tenant-scoped platform execution truth; that canonical truth owns
the tenant/invoice correlation.
"""
from __future__ import annotations

from pymongo.errors import DuplicateKeyError


class ElectrumProviderAccountBindingError(RuntimeError):
    pass


class ElectrumProviderAccountBindingRegistry:
    @staticmethod
    def ensure_indexes(collection) -> None:
        collection.create_index(
            [("provider_name", 1), ("payment_scheme", 1), ("creditor_account_fingerprint", 1)],
            unique=True,
            name="uq_electrum_provider_account_binding",
        )
        collection.create_index(
            [("binding_id", 1)],
            unique=True,
            name="uq_electrum_provider_account_binding_id",
        )

    @staticmethod
    def create(
        *,
        binding_id: str,
        creditor_account_fingerprint: str,
        payment_destination_reference: str,
        collection,
        session,
    ) -> dict:
        for value in (binding_id, creditor_account_fingerprint, payment_destination_reference):
            if not isinstance(value, str) or not value.strip():
                raise ElectrumProviderAccountBindingError("ELECTRUM_ACCOUNT_BINDING_IDENTITY_INVALID")
        if (
            len(creditor_account_fingerprint) != 64
            or any(ch not in "0123456789abcdef" for ch in creditor_account_fingerprint)
        ):
            raise ElectrumProviderAccountBindingError("ELECTRUM_ACCOUNT_BINDING_FINGERPRINT_INVALID")
        document = {
            "provider_name": "ELECTRUM",
            "payment_scheme": "ZA_RPP",
            "binding_id": binding_id,
            "creditor_account_fingerprint": creditor_account_fingerprint,
            "payment_destination_reference": payment_destination_reference,
            "status": "ACTIVE",
        }
        existing = collection.find_one(
            {"provider_name": "ELECTRUM", "payment_scheme": "ZA_RPP",
             "creditor_account_fingerprint": creditor_account_fingerprint},
            session=session,
        )
        if existing is not None:
            comparable = {key: existing.get(key) for key in document}
            if comparable == document:
                return existing
            raise ElectrumProviderAccountBindingError("ELECTRUM_ACCOUNT_BINDING_CONFLICT")
        try:
            collection.insert_one(document, session=session)
        except DuplicateKeyError as error:
            raise ElectrumProviderAccountBindingError("ELECTRUM_ACCOUNT_BINDING_DUPLICATE_RACE") from error
        return document

    @staticmethod
    def get_by_creditor_account_fingerprint(fingerprint: str, collection, *, session):
        matches = list(collection.find(
            {
                "provider_name": "ELECTRUM",
                "payment_scheme": "ZA_RPP",
                "creditor_account_fingerprint": fingerprint,
                "status": "ACTIVE",
            },
            session=session,
        ).limit(2))
        if len(matches) != 1:
            raise ElectrumProviderAccountBindingError("ELECTRUM_ACCOUNT_BINDING_NOT_UNIQUE")
        value = matches[0]
        if not all(isinstance(value.get(key), str) and value[key].strip() for key in (
            "payment_destination_reference", "binding_id"
        )):
            raise ElectrumProviderAccountBindingError("ELECTRUM_ACCOUNT_BINDING_RECORD_INVALID")
        return value


__all__ = ["ElectrumProviderAccountBindingError", "ElectrumProviderAccountBindingRegistry"]
