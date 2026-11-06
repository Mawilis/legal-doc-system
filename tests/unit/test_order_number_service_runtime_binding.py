from __future__ import annotations

from unittest.mock import Mock

import pytest

from tools.eos.saas.billing import order_number_service


class _Database:
    def __init__(self, client):
        self.client = client
        self.collection = Mock()
        self.collection.find_one.return_value = None

    def __getitem__(self, name):
        assert name == "counters"
        return self.collection


def test_order_number_service_uses_exact_kernel_database_and_client(monkeypatch):
    client = object()
    database = _Database(client)
    monkeypatch.setattr(order_number_service, "get_database", lambda: database)

    service = order_number_service.OrderNumberService(client)

    assert service.db is database
    assert service.counters is database.collection
    assert database.collection.insert_one.call_count == 2


def test_order_number_service_rejects_a_client_outside_kernel_runtime(monkeypatch):
    supplied_client = object()
    database = _Database(object())
    monkeypatch.setattr(order_number_service, "get_database", lambda: database)

    with pytest.raises(RuntimeError, match="ORDER_NUMBER_CANONICAL_DATABASE_UNAVAILABLE"):
        order_number_service.OrderNumberService(supplied_client)


def test_order_number_service_fails_closed_when_kernel_database_is_unavailable(monkeypatch):
    monkeypatch.setattr(order_number_service, "get_database", lambda: None)

    with pytest.raises(RuntimeError, match="ORDER_NUMBER_CANONICAL_DATABASE_UNAVAILABLE"):
        order_number_service.OrderNumberService(object())
