from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def test_browser_plan_changes_send_only_the_canonical_plan_selector():
    source = (ROOT / "client/src/hooks/useSubscriptions.js").read_text()
    assert "upgrade: (subscriptionId, options = {}) => lifecycle(subscriptionId, 'upgrade', { newPlanId: options.newPlanId })" in source
    assert "downgrade: (subscriptionId, options = {}) => lifecycle(subscriptionId, 'downgrade', { newPlanId: options.newPlanId })" in source


def test_subscription_api_keeps_authorized_tenant_scope_out_of_plan_change_body():
    source = (ROOT / "client/src/services/api/subscriptionApi.js").read_text()
    start = source.index("async lifecycle(")
    end = source.index("async getAudit(", start)
    lifecycle = source[start:end]
    assert "const { tenantId: requestedTenantId, ...payload } = data;" in lifecycle
    assert "const tenantId = requestedTenantId || this.kennelTenantId;" in lifecycle
    assert "this.client.post(`/subscriptions/${subscriptionId}/${action}`, payload" in lifecycle
    assert "headers: this._tenantHeaders(tenantId, this._idempotencyKey())" in lifecycle


def test_plan_change_contract_rejects_browser_authored_commercial_values():
    source = (ROOT / "tools/eos/saas/billing/subscription_registry.py").read_text()
    start = source.index("_PLAN_CHANGE_ALLOWED_FIELDS")
    end = source.index("\n", start)
    assert '"newPlanId"' in source[start : start + 160]
    assert "newAmount" not in source[start : start + 160]
    assert "newCurrency" not in source[start : start + 160]
