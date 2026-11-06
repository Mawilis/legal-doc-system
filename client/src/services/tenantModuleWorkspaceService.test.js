import { beforeEach, describe, expect, it, vi } from 'vitest';

const { get, post } = vi.hoisted(() => ({
  get: vi.fn(),
  post: vi.fn(),
}));

vi.mock('./api.js', () => ({
  default: { get, post },
}));

import {
  completeTenantModuleWorkItem,
  createTenantModuleWorkItem,
  readTenantModuleWorkspace,
} from './tenantModuleWorkspaceService.js';

const workspace = {
  schema: 'WILSY-TENANT-MODULE-WORKSPACE/V1',
  tenant_id: 'TENANT-OPS-1',
  product_id: 'OPERATIONS',
  workspace_key: 'OPERATIONS_DASHBOARD',
  entitlement_id: 'tpe-operations',
  entitlement_revision: 2,
  entitlement_fingerprint: 'a'.repeat(128),
  entitlement_state: 'ACTIVE',
  generated_at: '2026-11-06T10:00:00Z',
  items: [{
    schema: 'WILSY-TENANT-MODULE-WORK-ITEM/V1',
    tenant_id: 'TENANT-OPS-1',
    work_item_id: 'tmw-1',
    title: 'Prepare operations plan',
    kind: 'TASK',
    status: 'OPEN',
    priority: 'HIGH',
    due_at: null,
    queue_position: 1,
    is_overdue: false,
    is_due_today: false,
  }],
};

describe('tenant module workspace API contract', () => {
  beforeEach(() => {
    get.mockReset();
    post.mockReset();
  });

  it('accepts only the exact product, workspace, active entitlement and tenant-bound items', async () => {
    get.mockResolvedValue({ data: workspace });
    const result = await readTenantModuleWorkspace('OPERATIONS');
    expect(get).toHaveBeenCalledWith('/tenant-modules/operations/workspace', expect.any(Object));
    expect(result.productId).toBe('OPERATIONS');
    expect(result.entitlement).toEqual({
      id: 'tpe-operations',
      revision: 2,
      fingerprint: 'a'.repeat(128),
      state: 'ACTIVE',
    });
    expect(result.items[0].tenant_id).toBe('TENANT-OPS-1');
  });

  it('rejects a valid server response for a different active tenant', async () => {
    get.mockResolvedValue({ data: workspace });
    await expect(readTenantModuleWorkspace('OPERATIONS', 'OTHER-TENANT')).rejects.toThrow(
      'TENANT_MODULE_WORKSPACE_RESPONSE_INVALID',
    );
  });

  it('rejects an item whose tenant differs from the authenticated workspace tenant', async () => {
    get.mockResolvedValue({
      data: { ...workspace, items: [{ ...workspace.items[0], tenant_id: 'OTHER-TENANT' }] },
    });
    await expect(readTenantModuleWorkspace('OPERATIONS')).rejects.toThrow(
      'TENANT_MODULE_WORKSPACE_RESPONSE_INVALID',
    );
  });

  it('rejects an inactive entitlement and a mismatched module product', async () => {
    get.mockResolvedValue({ data: { ...workspace, entitlement_state: 'SUSPENDED' } });
    await expect(readTenantModuleWorkspace('OPERATIONS')).rejects.toThrow(
      'TENANT_MODULE_WORKSPACE_RESPONSE_INVALID',
    );
    get.mockResolvedValue({ data: { ...workspace, product_id: 'INTELLIGENCE' } });
    await expect(readTenantModuleWorkspace('OPERATIONS')).rejects.toThrow(
      'TENANT_MODULE_WORKSPACE_RESPONSE_INVALID',
    );
  });

  it('sends stable command identity and fixed module routes', async () => {
    post.mockResolvedValue({ data: { work_item_id: 'tmw-2' } });
    await createTenantModuleWorkItem('INTELLIGENCE', { title: 'Review insight' }, 'stable-intel-key');
    expect(post).toHaveBeenCalledWith(
      '/tenant-modules/intelligence/workspace/work-items',
      { title: 'Review insight' },
      expect.objectContaining({ headers: { 'Idempotency-Key': 'stable-intel-key' } }),
    );
    await completeTenantModuleWorkItem('INTELLIGENCE', 'tmw-2', 'Insight reviewed');
    expect(post).toHaveBeenLastCalledWith(
      '/tenant-modules/intelligence/workspace/work-items/tmw-2/complete',
      { completion_note: 'Insight reviewed' },
      expect.any(Object),
    );
  });
});
