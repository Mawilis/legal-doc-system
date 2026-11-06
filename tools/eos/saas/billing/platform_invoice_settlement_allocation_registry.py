"""Tenant-scoped immutable allocation registry; caller owns every transaction."""
from pymongo.errors import DuplicateKeyError

from tools.eos.saas.domain.platform_invoice_settlement_allocation import (
    PlatformInvoiceSettlementAllocation,
    PlatformInvoiceSettlementAllocationError,
)


class PlatformInvoiceSettlementAllocationNotFound(RuntimeError):
    pass


class PlatformInvoiceSettlementAllocationConflict(RuntimeError):
    pass


class PlatformInvoiceSettlementAllocationRegistry:
    @staticmethod
    def ensure_indexes(collection) -> None:
        collection.create_index(
            [("tenant_id", 1), ("allocation_id", 1)],
            unique=True,
            name="uq_platform_invoice_settlement_allocation",
        )
        collection.create_index(
            [("tenant_id", 1), ("observation_id", 1)],
            unique=True,
            name="uq_platform_invoice_settlement_observation_allocation",
        )
        collection.create_index(
            [("tenant_id", 1), ("invoice_id", 1), ("allocation_sequence", 1)],
            unique=True,
            name="uq_platform_invoice_settlement_allocation_sequence",
        )

    @staticmethod
    def create(value: PlatformInvoiceSettlementAllocation, collection, *, session):
        existing = collection.find_one(
            {"tenant_id": value.tenant_id, "observation_id": value.observation_id},
            session=session,
        )
        if existing is not None:
            try:
                replay = PlatformInvoiceSettlementAllocation.from_dict(existing)
            except (TypeError, ValueError, KeyError) as invalid:
                raise PlatformInvoiceSettlementAllocationConflict("ALLOCATION_PERSISTED_RECORD_INVALID") from invalid
            if replay.fingerprint == value.fingerprint:
                return replay
            raise PlatformInvoiceSettlementAllocationConflict("ALLOCATION_DUPLICATE_OR_CONFLICT")
        try:
            collection.insert_one(value.to_dict(), session=session)
            return value
        except DuplicateKeyError as error:
            # A concurrent unique-index winner requires retrying the entire caller transaction.
            raise PlatformInvoiceSettlementAllocationConflict("ALLOCATION_DUPLICATE_OR_CONFLICT") from error

    @staticmethod
    def get_by_observation(tenant_id: str, observation_id: str, collection, *, session):
        record = collection.find_one(
            {"tenant_id": tenant_id, "observation_id": observation_id},
            session=session,
        )
        if record is None:
            raise PlatformInvoiceSettlementAllocationNotFound("ALLOCATION_NOT_FOUND")
        try:
            return PlatformInvoiceSettlementAllocation.from_dict(record)
        except (TypeError, ValueError, KeyError) as error:
            raise PlatformInvoiceSettlementAllocationConflict("ALLOCATION_PERSISTED_RECORD_INVALID") from error
