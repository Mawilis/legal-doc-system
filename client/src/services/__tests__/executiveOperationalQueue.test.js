import { describe, expect, it } from 'vitest';
import {
  buildDecisionExceptions,
  buildOperationalQueue,
  getOperationalRecordFields
} from '../executiveOperationalQueue.js';

describe('executive operational queue projection', () => {
  it('projects actionable records only from responding tenant sources', () => {
    const queue = buildOperationalQueue([
      {
        key: 'crm', label: 'CRM', functionKey: 'crm', live: true,
        status: 'CRM_SOURCE_LIVE', lastSync: '2026-11-06T06:00:00.000Z',
        records: [
          { id: 'lead-1', title: 'Renewal approval', status: 'AWAITING_APPROVAL', priority: 'HIGH' },
          { id: 'lead-2', title: 'Closed account', status: 'CLOSED' },
          { id: 'lead-3', title: 'Unclassified account' }
        ]
      },
      {
        key: 'hr', label: 'HR', functionKey: 'hr', live: false,
        status: 'HR_ACCESS_DENIED',
        records: [{ id: 'person-1', title: 'Must not leak', status: 'OPEN' }]
      }
    ]);
    expect(queue).toHaveLength(1);
    expect(queue[0]).toMatchObject({
      id: 'crm:lead-1', recordId: 'lead-1', sourceKey: 'crm',
      status: 'AWAITING_APPROVAL', title: 'Renewal approval', priority: 'HIGH'
    });
  });

  it('orders critical work before ordinary work deterministically', () => {
    const queue = buildOperationalQueue([{
      key: 'ops', label: 'Operations', live: true, status: 'OPS_SOURCE_LIVE',
      records: [
        { id: 'normal', title: 'Normal task', status: 'OPEN' },
        { id: 'blocked', title: 'Blocked task', status: 'BLOCKED' },
        { id: 'overdue', title: 'Overdue task', status: 'OVERDUE' }
      ]
    }]);
    expect(queue.map((row) => row.recordId)).toEqual(['blocked', 'overdue', 'normal']);
  });

  it('separates approval and risk exceptions from the general queue', () => {
    const queue = buildOperationalQueue([{
      key: 'finance', label: 'Finance', live: true,
      records: [
        { id: 'approval', title: 'Approve payment', status: 'AWAITING_APPROVAL' },
        { id: 'open', title: 'Open item', status: 'OPEN' }
      ]
    }]);
    expect(buildDecisionExceptions(queue).map((row) => row.recordId)).toEqual(['approval']);
  });

  it('exposes only allowlisted inspector fields', () => {
    expect(getOperationalRecordFields({
      reference: 'INV-10', status: 'OVERDUE', amount: 1200,
      currency: 'ZAR', password: 'never-render'
    })).toEqual([
      ['Reference', 'INV-10'], ['Status', 'OVERDUE'],
      ['Amount', '1200'], ['Currency', 'ZAR']
    ]);
  });

  it('does not treat missing sources or status-less records as a clear queue', () => {
    expect(buildOperationalQueue([
      { key: 'it', live: false, records: [{ id: 'x', status: 'OPEN' }] },
      { key: 'crm', live: true, records: [{ id: 'y', title: 'Unclassified' }] }
    ])).toEqual([]);
  });
});
