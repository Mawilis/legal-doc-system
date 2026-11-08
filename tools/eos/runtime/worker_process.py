"""Standalone Python EOS durable worker process.

The process owns no second Mongo client or database authority. It composes the
kernel database, provisions only its explicit queue/outbox indexes, schedules
daily compliance tasks, and consumes only registered worker engines.
"""
from __future__ import annotations

import asyncio
import logging
import os
import signal

from tools.eos.kernel.db import connect_db, disconnect_db, get_client, get_database
from .compliance_scan_scheduler import run_daily_compliance_scheduler
from .durable_worker_runtime import (
    CLIENTS_COLLECTION,
    NOTIFICATION_OUTBOX_COLLECTION,
    TASK_COLLECTION,
    provision_compliance_worker_indexes,
    provision_durable_worker_indexes,
    register_compliance_scan_worker,
)
from .durable_worker_runtime import create_durable_worker_runner
from .worker_registry import EngineWorkerRegistry

logger = logging.getLogger("WilsyOS.Runtime.WorkerProcess")


async def serve() -> None:
    worker_id = os.getenv("WILSY_EOS_WORKER_ID", "").strip()
    if not worker_id:
        raise RuntimeError("WILSY_EOS_WORKER_ID_REQUIRED")
    connected, detail = connect_db()
    if not connected:
        raise RuntimeError(f"EOS_KERNEL_DATABASE_UNAVAILABLE:{detail}")
    stop_event = asyncio.Event()
    loop = asyncio.get_running_loop()
    for sig in (signal.SIGINT, signal.SIGTERM):
        try:
            loop.add_signal_handler(sig, stop_event.set)
        except NotImplementedError:
            pass
    try:
        database, client = get_database(), get_client()
        if database is None or client is None:
            raise RuntimeError("EOS_KERNEL_DATABASE_NOT_READY")
        provision_durable_worker_indexes(database)
        provision_compliance_worker_indexes(database)
        registry = EngineWorkerRegistry()
        register_compliance_scan_worker(registry, database=database, mongo_client=client)
        runner = create_durable_worker_runner(
            worker_registry=registry, worker_id=worker_id,
            database=database, mongo_client=client,
        )
        scheduler = asyncio.create_task(
            run_daily_compliance_scheduler(
                tenants=database[CLIENTS_COLLECTION] if False else database["tenants"],
                tasks=database[TASK_COLLECTION], stop_event=stop_event,
            )
        )
        worker = asyncio.create_task(
            runner.run_forever(stop_event=stop_event, idle_poll_seconds=1.0)
        )
        logger.info("Python EOS durable worker online; registered_engines=%s", registry.engine_names)
        try:
            await asyncio.gather(scheduler, worker)
        finally:
            stop_event.set()
            for task in (scheduler, worker):
                task.cancel()
            await asyncio.gather(scheduler, worker, return_exceptions=True)
    finally:
        disconnect_db()


def main() -> None:
    logging.basicConfig(level=os.getenv("LOG_LEVEL", "INFO"))
    asyncio.run(serve())


if __name__ == "__main__":
    main()
