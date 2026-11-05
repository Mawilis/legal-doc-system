from __future__ import annotations

from unittest.mock import Mock

import pytest

from tools.eos.saas.billing.financial_approval_aggregator import (
    FinancialApprovalAggregator,
    FinancialApprovalAggregatorError,
)


def test_financial_approval_aggregator_rejects_mixed_client_database_graph():
    database = Mock()
    database.client = object()
    supplied_client = object()
    aggregator = FinancialApprovalAggregator(database=database, client=supplied_client)

    with pytest.raises(
        FinancialApprovalAggregatorError,
        match="FINANCIAL_APPROVAL_AGGREGATOR_MIXED_CLIENT_GRAPH",
    ):
        aggregator.aggregate(
            tenant_id="tenant-1",
            evaluation_id="evaluation-1",
            result_id="result-1",
            evaluated_at=__import__("datetime").datetime.now(__import__("datetime").timezone.utc),
            created_at=__import__("datetime").datetime.now(__import__("datetime").timezone.utc),
        )


def test_financial_approval_aggregator_defaults_to_database_owned_client():
    client = object()
    database = Mock()
    database.client = client
    aggregator = FinancialApprovalAggregator(database=database)

    assert aggregator._client is client
    assert aggregator._db() is database
