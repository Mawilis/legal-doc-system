"""Opt-in durable worker for Electrum PayShap completion inbox events."""
from __future__ import annotations

import asyncio
from datetime import datetime, timedelta, timezone
import logging
import re

from tools.eos.kennel.orchestration.electrum_payshap_completion_processing import (
    process_electrum_payshap_completion_event,
)
from tools.eos.kennel.registry.electrum_payshap_completion_inbox_registry import (
    ElectrumCompletionInboxConflict,
    ElectrumPayShapCompletionInboxRegistry,
)

logger = logging.getLogger(__name__)

INBOX = "electrum_payshap_completion_inbox"
BINDINGS = "electrum_provider_tenant_bindings"
OBSERVATIONS = "financial_settlement_observations"
EXECUTION_FACTS = "financial_execution_facts"
PLATFORM_TRUTH = "platform_billing_financial_execution_truths"
RELEASE_AUTHORIZATIONS = "platform_billing_release_authorizations"
INVOICES = "invoices"
ALLOCATIONS = "platform_invoice_settlement_allocations"
AUDIT = "billing_audit_events"
OUTBOX = "billing_outbox_events"
SUBSCRIPTIONS = "subscriptions"


def _safe_error_code(error: Exception) -> str:
    candidate = str(error)
    if re.fullmatch(r"[A-Z0-9_]{1,64}", candidate):
        return candidate
    name = type(error).__name__.upper()
    return name if re.fullmatch(r"[A-Z0-9_]{1,64}", name) else "ELECTRUM_PROCESSING_FAILED"


async def run_electrum_payshap_completion_worker(*, poll_interval_seconds: float = 1.0) -> None:
    """Poll durable inbox; every financial mutation remains in one Mongo transaction.

    This worker is opt-in and must be enabled explicitly. Failed correlations
    remain pending with bounded exponential retry; no subscription lifecycle
    transition or production billing enforcement is performed.
    """
    from tools.eos.kernel.db import get_client, get_database

    while True:
        try:
            client = get_client()
            database = get_database()
            if client is None or database is None:
                await asyncio.sleep(poll_interval_seconds)
                continue

            now = datetime.now(timezone.utc)
            inbox = database[INBOX]
            pending = inbox.find_one(
                {
                    "processing_status": "PENDING",
                    "available_at": {"$lte": now.isoformat()},
                },
                sort=[("available_at", 1), ("received_at", 1)],
            )
            if pending is None:
                await asyncio.sleep(poll_interval_seconds)
                continue

            message_id = pending["message_id"]
            try:
                with client.start_session() as session:
                    with session.start_transaction():
                        result = process_electrum_payshap_completion_event(
                            message_id,
                            inbox_collection=inbox,
                            binding_collection=database[BINDINGS],
                            observation_collection=database[OBSERVATIONS],
                            execution_truth_collection=database[EXECUTION_FACTS],
                            platform_truth_collection=database[PLATFORM_TRUTH],
                            release_authorization_collection=database[RELEASE_AUTHORIZATIONS],
                            platform_invoice_collection=database[INVOICES],
                            allocation_collection=database[ALLOCATIONS],
                            audit_collection=database[AUDIT],
                            outbox_collection=database[OUTBOX],
                            subscription_collection=database[SUBSCRIPTIONS],
                            session=session,
                            processed_at=now,
                        )
                logger.info(
                    "[ELECTRUM_SETTLEMENT] Inbox event processed: message_id=%s status=%s allocation_id=%s",
                    message_id,
                    result["processing_status"],
                    result.get("allocation_id"),
                )
            except asyncio.CancelledError:
                raise
            except Exception as error:
                code = _safe_error_code(error)
                try:
                    current = inbox.find_one({
                        "provider_name": "ELECTRUM",
                        "message_id": message_id,
                    })
                    if current is not None and current.get("processing_status") == "PENDING":
                        event, _ = ElectrumPayShapCompletionInboxRegistry.get(
                            "ELECTRUM", message_id, inbox
                        )
                        attempts = int(current.get("attempt_count", 0))
                        revision = int(current.get("processing_revision", 0))
                        delay = min(2 ** min(attempts, 8), 300)
                        retry_at = now + timedelta(seconds=delay)
                        with client.start_session() as session:
                            with session.start_transaction():
                                ElectrumPayShapCompletionInboxRegistry.schedule_retry(
                                    event,
                                    collection=inbox,
                                    session=session,
                                    expected_revision=revision,
                                    expected_attempt_count=attempts,
                                    retry_at=retry_at,
                                    error_code=code,
                                )
                except ElectrumCompletionInboxConflict:
                    # Another worker may have committed the event first.
                    pass
                except Exception:
                    logger.exception(
                        "[ELECTRUM_SETTLEMENT] Failed to schedule inbox retry: message_id=%s",
                        message_id,
                    )
                logger.warning(
                    "[ELECTRUM_SETTLEMENT] Inbox processing deferred: message_id=%s code=%s",
                    message_id,
                    code,
                )
                await asyncio.sleep(0.1)
        except asyncio.CancelledError:
            raise
        except Exception:
            logger.exception("[ELECTRUM_SETTLEMENT] Worker loop unavailable")
            await asyncio.sleep(poll_interval_seconds)


__all__ = ["run_electrum_payshap_completion_worker"]
