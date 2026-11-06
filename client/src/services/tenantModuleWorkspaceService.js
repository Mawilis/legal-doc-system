import api from './api.js';

const MODULES = Object.freeze({
  OPERATIONS: Object.freeze({
    productId: 'OPERATIONS',
    workspaceKey: 'OPERATIONS_DASHBOARD',
    path: 'operations',
    label: 'Operations',
  }),
  INTELLIGENCE: Object.freeze({
    productId: 'INTELLIGENCE',
    workspaceKey: 'INTELLIGENCE_DASHBOARD',
    path: 'intelligence',
    label: 'Intelligence',
  }),
});

function moduleDescriptor(moduleId) {
  const descriptor = MODULES[moduleId];
  if (!descriptor) throw new Error('TENANT_MODULE_NOT_SUPPORTED');
  return descriptor;
}

export async function readTenantModuleWorkspace(moduleId) {
  const descriptor = moduleDescriptor(moduleId);
  const response = await api.get(`/tenant-modules/${descriptor.path}/workspace`, {
    timeout: 12000,
    forceNetworkRetry: true,
  });
  const value = response?.data;
  if (
    !value ||
    value.schema !== 'WILSY-TENANT-MODULE-WORKSPACE/V1' ||
    value.product_id !== descriptor.productId ||
    value.workspace_key !== descriptor.workspaceKey ||
    typeof value.tenant_id !== 'string' ||
    !Array.isArray(value.items)
  ) {
    throw new Error('TENANT_MODULE_WORKSPACE_RESPONSE_INVALID');
  }
  return Object.freeze({
    tenantId: value.tenant_id,
    productId: value.product_id,
    workspaceKey: value.workspace_key,
    generatedAt: value.generated_at,
    items: Object.freeze(value.items.map(item => Object.freeze({ ...item }))),
  });
}

export async function createTenantModuleWorkItem(moduleId, input, idempotencyKey = '') {
  const descriptor = moduleDescriptor(moduleId);
  const key = typeof idempotencyKey === 'string' && idempotencyKey.trim()
    ? idempotencyKey.trim()
    : (globalThis.crypto?.randomUUID?.()
      || `module-work-${Date.now()}-${Math.random().toString(16).slice(2)}`);
  const response = await api.post(
    `/tenant-modules/${descriptor.path}/workspace/work-items`,
    input,
    { headers: { 'Idempotency-Key': key }, timeout: 12000 },
  );
  return response?.data;
}

export async function completeTenantModuleWorkItem(moduleId, workItemId, completionNote) {
  const descriptor = moduleDescriptor(moduleId);
  const response = await api.post(
    `/tenant-modules/${descriptor.path}/workspace/work-items/${encodeURIComponent(workItemId)}/complete`,
    { completion_note: completionNote },
    { timeout: 12000 },
  );
  return response?.data;
}
