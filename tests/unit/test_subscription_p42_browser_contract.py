from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def test_subscription_hook_selects_catalogue_plan_without_client_pricing():
    source = (ROOT / "client/src/hooks/useSubscriptions.js").read_text()
    assert "upgrade: (subscriptionId, options = {}) => lifecycle(subscriptionId, 'upgrade', { newPlanId: options.newPlanId })" in source
    assert "downgrade: (subscriptionId, options = {}) => lifecycle(subscriptionId, 'downgrade', { newPlanId: options.newPlanId })" in source


def test_subscription_lifecycle_adapter_keeps_tenant_scope_out_of_json_body():
    source = (ROOT / "client/src/services/api/subscriptionApi.js").read_text()
    assert "const { tenantId: requestedTenantId, ...payload } = data;" in source
    assert "const tenantId = requestedTenantId || this.kennelTenantId;" in source
    assert "this.client.post(`/subscriptions/${subscriptionId}/${action}`, payload" in source
    assert "headers: this._tenantHeaders(tenantId, this._idempotencyKey())" in source


def test_browser_upgrade_contract_matches_python_p42_plan_selection_only():
    hook = (ROOT / "client/src/hooks/useSubscriptions.js").read_text()
    api = (ROOT / "client/src/services/api/subscriptionApi.js").read_text()
    assert "newAmount" not in hook[hook.index("upgrade:"):hook.index("getAudit,")]
    assert "newCurrency" not in hook[hook.index("upgrade:"):hook.index("getAudit,")]
    assert "payload" in api[api.index("async lifecycle("):api.index("async getAudit(")]
