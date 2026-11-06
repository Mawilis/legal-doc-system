import fs from 'node:fs';
import { expect, test } from '@playwright/test';

const statePath = process.env.BROWSER_CERT_STATE;
if (!statePath) throw new Error('BROWSER_CERT_STATE_REQUIRED');
const state = JSON.parse(fs.readFileSync(statePath, 'utf8'));

async function authenticatedPage(browser, actorKey) {
  const actor = state.actors?.[actorKey];
  if (!actor) throw new Error(`POS_BROWSER_ACTOR_MISSING:${actorKey}`);
  const context = await browser.newContext();
  const page = await context.newPage();
  await page.addInitScript(({ token, tenantId, principalId, email }) => {
    localStorage.setItem('wilsy_auth_token', token);
    localStorage.setItem('token', token);
    localStorage.setItem('tenantId', tenantId);
    localStorage.setItem('wilsy_tenant_id', tenantId);
    localStorage.setItem('wilsy_active_tenant', JSON.stringify({ tenantId, id: tenantId }));
    localStorage.setItem('wilsy_sovereign_user', JSON.stringify({ id: principalId, email, tenantId }));
  }, {
    token: actor.access_token, tenantId: state.tenant_id,
    principalId: actor.principal_id, email: actor.email,
  });
  await page.goto('/');
  await expect(page.locator('body')).toBeVisible();
  return { context, page, actor };
}

async function api(page, method, path, body, key, tenantId = state.tenant_id) {
  return page.evaluate(async ({ method, path, body, key, tenantId }) => {
    const response = await fetch(path, {
      method,
      credentials: 'include',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${localStorage.getItem('wilsy_auth_token') || localStorage.getItem('token') || ''}`,
        'X-Tenant-ID': tenantId,
        ...(key ? { 'Idempotency-Key': key } : {}),
      },
      ...(body === undefined ? {} : { body: JSON.stringify(body) }),
    });
    const payload = await response.json().catch(() => ({}));
    return { status: response.status, payload };
  }, { method, path, body, key, tenantId });
}

test('POS operator completes authenticated daily-use sale and evidence journey', async ({ browser }) => {
  const { context, page, actor } = await authenticatedPage(browser, 'pos_operator');
  try {
    await expect(page.getByRole('heading', { name: 'Point of Sale' })).toBeVisible();
    await expect(page.getByLabel('Assigned location')).toHaveValue('browser-cert-store-01');

    const locations = await api(page, 'GET', '/api/pos/locations');
    expect(locations.status).toBe(200);
    expect(locations.payload.principal_id).toBe(actor.principal_id);
    expect(locations.payload.locations.map(item => item.location_id)).toEqual(['browser-cert-store-01']);

    const saleId = `browser-sale-${Date.now()}`;
    const sale = await api(page, 'POST', '/api/pos/locations/browser-cert-store-01/sales', {
      sale_id: saleId, currency: 'ZAR',
      lines: [{
        product_id: 'fixture-product', sku: 'SKU-POS-01', description: 'Synthetic POS item',
        quantity: 2, unit_price_minor: 10000, discount_minor: 0, tax_minor: 0, currency: 'ZAR',
      }],
    }, `sale:${saleId}`);
    expect(sale.status).toBe(201);
    expect(sale.payload.sale_id).toBe(saleId);

    const read = await api(page, 'GET', `/api/pos/locations/browser-cert-store-01/sales/${saleId}`);
    expect(read.status).toBe(200);
    expect(read.payload.sale.sale_id).toBe(saleId);
    expect(read.payload.financial_state).toBe('NOT_ASSERTED_BY_POS');

    const tender = await api(page, 'POST', `/api/pos/locations/browser-cert-store-01/sales/${saleId}/tenders`, {
      tender_type: 'CARD', amount_minor: 20000, evidence_id: `tender-${saleId}`,
    }, `tender:${saleId}`);
    expect(tender.status).toBe(201);

    const cash = await api(page, 'POST', `/api/pos/locations/browser-cert-store-01/sales/${saleId}/cash-tenders`, {
      cash_received_minor: 20000, evidence_id: `cash-${saleId}`,
    }, `cash:${saleId}`);
    expect(cash.status).toBe(201);

    const returned = await api(page, 'POST', `/api/pos/locations/browser-cert-store-01/sales/${saleId}/returns`, {
      sku: 'SKU-POS-01', quantity: 1, reason: 'Synthetic browser certification return',
      return_id: `return-${saleId}`,
    }, `return:${saleId}`);
    expect(returned.status).toBe(201);

    const refund = await api(page, 'POST', `/api/pos/locations/browser-cert-store-01/sales/${saleId}/refund-intents`, {
      amount_minor: 5000, basis: 'Synthetic browser certification refund',
      refund_intent_id: `refund-${saleId}`,
    }, `refund:${saleId}`);
    expect(refund.status).toBe(201);

    const evidence = await api(page, 'GET', `/api/pos/locations/browser-cert-store-01/sales/${saleId}`);
    expect(evidence.status).toBe(200);
    expect(evidence.payload.commercial_evidence.map(item => item.evidence_type)).toEqual(
      expect.arrayContaining(['TENDER_INTENT', 'CASH_TENDER', 'RETURN_INTENT', 'REFUND_INTENT']),
    );

    const wrongLocation = await api(page, 'GET', `/api/pos/locations/another-store/sales/${saleId}`);
    expect(wrongLocation.status).toBe(403);

  } finally {
    await context.close();
  }

  const approver = await authenticatedPage(browser, 'tenant_owner');
  try {
    const providerUnavailable = await api(approver.page, 'POST',
      `/api/pos/locations/browser-cert-store-01/sales/${saleId}/tenders/tender-${saleId}/execute`);
    expect(providerUnavailable.status).toBe(503);
    expect(providerUnavailable.payload.detail).toBe('KENNEL_FINANCIAL_MOVEMENT_PROVIDER_UNBOUND');
    const refundUnavailable = await api(approver.page, 'POST',
      `/api/pos/locations/browser-cert-store-01/sales/${saleId}/refund-intents/refund-${saleId}/execute`);
    expect(refundUnavailable.status).toBe(503);
    expect(refundUnavailable.payload.detail).toBe('KENNEL_FINANCIAL_MOVEMENT_PROVIDER_UNBOUND');
  } finally {
    await approver.context.close();
  }
});

test('POS location and sales APIs deny foreign tenants and unauthorized Legal roles', async ({ browser }) => {
  const { context, page } = await authenticatedPage(browser, 'partner');
  try {
    const unauthorized = await api(page, 'GET', '/api/pos/locations');
    expect(unauthorized.status).toBe(403);
  } finally {
    await context.close();
  }

  const owner = await authenticatedPage(browser, 'tenant_owner');
  try {
    const foreignTenant = await api(owner.page, 'GET', '/api/pos/locations', undefined, undefined, state.foreign_tenant_id);
    expect([401, 403]).toContain(foreignTenant.status);
  } finally {
    await owner.context.close();
  }
});
