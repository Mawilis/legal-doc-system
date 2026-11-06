import React from 'react';
import { fireEvent, render, screen, waitFor } from '@testing-library/react';
import { beforeEach, describe, expect, it, vi } from 'vitest';

const { readTenantModuleWorkspace, createTenantModuleWorkItem, completeTenantModuleWorkItem } = vi.hoisted(() => ({
  readTenantModuleWorkspace: vi.fn(),
  createTenantModuleWorkItem: vi.fn(),
  completeTenantModuleWorkItem: vi.fn(),
}));

vi.mock('../../src/services/tenantModuleWorkspaceService.js', () => ({
  readTenantModuleWorkspace,
  createTenantModuleWorkItem,
  completeTenantModuleWorkItem,
}));

import TenantModuleWorkspace from '../../src/components/os/TenantModuleWorkspace.jsx';

const operationsSnapshot = {
  tenantId: 'TENANT-OPS-1',
  productId: 'OPERATIONS',
  workspaceKey: 'OPERATIONS_DASHBOARD',
  generatedAt: '2026-11-06T10:00:00Z',
  items: [{
    work_item_id: 'tmw-ops-1',
    title: 'Publish operations runbook',
    kind: 'TASK',
    status: 'OPEN',
    priority: 'HIGH',
    due_at: null,
    is_overdue: false,
    is_due_today: false,
  }],
};

describe('independent tenant module daily-use workspace', () => {
  beforeEach(() => {
    readTenantModuleWorkspace.mockReset();
    createTenantModuleWorkItem.mockReset();
    completeTenantModuleWorkItem.mockReset();
    readTenantModuleWorkspace.mockResolvedValue(operationsSnapshot);
    createTenantModuleWorkItem.mockResolvedValue({ work_item_id: 'tmw-ops-2' });
    completeTenantModuleWorkItem.mockResolvedValue({ status: 'COMPLETED' });
  });

  it('loads Operations from its own product API and exposes keyboard-accessible task controls', async () => {
    render(<TenantModuleWorkspace moduleId="OPERATIONS" />);
    expect(await screen.findByText('Publish operations runbook')).toBeInTheDocument();
    expect(readTenantModuleWorkspace).toHaveBeenCalledWith('OPERATIONS');
    expect(screen.getByRole('button', { name: 'Refresh EOS' })).toBeInTheDocument();
    expect(screen.getByLabelText('Action title')).toBeInTheDocument();
    expect(screen.getByRole('button', { name: 'Create action' })).toBeEnabled();
  });

  it('creates and completes work only through the Operations EOS commands', async () => {
    render(<TenantModuleWorkspace moduleId="OPERATIONS" />);
    await screen.findByText('Publish operations runbook');
    fireEvent.change(screen.getByLabelText('Action title'), { target: { value: 'Review operating procedure' } });
    fireEvent.click(screen.getByRole('button', { name: 'Create action' }));
    await waitFor(() => expect(createTenantModuleWorkItem).toHaveBeenCalledWith('OPERATIONS', expect.objectContaining({
      title: 'Review operating procedure',
      kind: 'TASK',
    })));
    fireEvent.click(await screen.findByRole('button', { name: 'Complete' }));
    await waitFor(() => expect(completeTenantModuleWorkItem).toHaveBeenCalledWith(
      'OPERATIONS', 'tmw-ops-1', expect.any(String),
    ));
  });

  it('does not display cached/sample work when the module is denied or unavailable', async () => {
    readTenantModuleWorkspace.mockRejectedValue({ response: { status: 403 } });
    render(<TenantModuleWorkspace moduleId="INTELLIGENCE" />);
    expect(await screen.findByRole('alert')).toHaveTextContent('not currently admitted');
    expect(screen.queryByText('Publish operations runbook')).not.toBeInTheDocument();
    expect(readTenantModuleWorkspace).toHaveBeenCalledWith('INTELLIGENCE');
  });
});
