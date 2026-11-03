import api from './api.js';

export async function readOwnerCommercialWorkspace() {
  const response = await api.get('/crm/owner-workspace');
  const value = response?.data;
  if (
    !value ||
    value.schema !== 'WILSY-OWNER-COMMERCIAL-WORKSPACE/V1' ||
    typeof value.tenant_id !== 'string' ||
    !Array.isArray(value.items)
  ) {
    throw new Error('OWNER_WORKSPACE_RESPONSE_INVALID');
  }
  return Object.freeze({
    tenantId: value.tenant_id,
    generatedAt: value.generated_at,
    items: Object.freeze(value.items.map(item => Object.freeze({ ...item }))),
  });
}

export async function createOwnerCommercialWorkItem(input) {
  const key = globalThis.crypto?.randomUUID?.()
    || `owner-work-${Date.now()}-${Math.random().toString(16).slice(2)}`;
  const response = await api.post(
    '/crm/owner-workspace/work-items',
    input,
    { headers: { 'Idempotency-Key': key } },
  );
  return response?.data;
}

export async function completeOwnerCommercialWorkItem(workItemId, completionNote) {
  const response = await api.post(
    `/crm/owner-workspace/work-items/${encodeURIComponent(workItemId)}/complete`,
    { completion_note: completionNote },
  );
  return response?.data;
}
