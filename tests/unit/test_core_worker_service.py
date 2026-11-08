import asyncio
from unittest.mock import MagicMock

import pytest

from tools.eos.runtime.core_worker_service import run_core_worker_service


def test_core_worker_service_uses_one_kernel_database_graph_and_stops_cleanly():
    client = object()
    database = MagicMock()
    database.client = client
    stop = asyncio.Event()
    stop.set()
    asyncio.run(run_core_worker_service(
        database=database,
        mongo_client=client,
        worker_id="worker-a",
        stop_event=stop,
    ))


def test_core_worker_service_rejects_mixed_database_client():
    database = MagicMock()
    database.client = object()
    with pytest.raises(RuntimeError, match="EOS_WORKER_DATABASE_CLIENT_MISMATCH"):
        asyncio.run(run_core_worker_service(
            database=database,
            mongo_client=object(),
            worker_id="worker-a",
            stop_event=asyncio.Event(),
        ))


def test_core_worker_service_fails_closed_without_kernel_database():
    with pytest.raises(RuntimeError, match="EOS_KERNEL_DATABASE_NOT_READY"):
        asyncio.run(run_core_worker_service(
            database=None,
            mongo_client=None,
            worker_id="worker-a",
            stop_event=asyncio.Event(),
        ))
