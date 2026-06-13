/* eslint-disable */
import { describe, expect, it } from 'vitest';
import {
  answerExecutiveNaturalLanguageQuery,
  buildExecutiveTransformationPlaybook,
  resolveGrowthPhase
} from '../../src/services/ExecutiveTransformationEngine.js';

describe('ExecutiveTransformationEngine', () => {
  it('resolves foundation phase for early ARR tenants', () => {
    const phase = resolveGrowthPhase(125000);

    expect(phase.key).toBe('foundation');
    expect(phase.target).toBe('$0-$500K ARR');
  });

  it('builds a source-gated transformation playbook with proofs', () => {
    const playbook = buildExecutiveTransformationPlaybook({
      activeTenant: { tenantId: 'TENANT-1', integrations: [] },
      financialKPIs: {
        revenue: 100000,
        expenses: 40000,
        profitMargin: 24,
        arr: 220000,
        currency: 'ZAR'
      },
      sourceSnapshot: {
        finance: { live: true, status: 'FINANCE_SERVICE_LIVE' },
        telemetry: { live: false, status: 'SOURCE_SILENT' },
        records: { live: true, status: 'TENANT_COMMAND_LEDGER' }
      },
      sourceRows: [
        { key: 'finance', live: true, status: 'FINANCE_SERVICE_LIVE' },
        { key: 'telemetry', live: false, status: 'SOURCE_SILENT' },
        { key: 'records', live: true, status: 'TENANT_COMMAND_LEDGER' },
        { key: 'profile', live: true, status: 'TENANT_PROFILE_DERIVED' }
      ],
      profile: {
        industryKey: 'technology_saas',
        industryLabel: 'Technology, SaaS and Digital Product',
        sourceStatus: 'TENANT_PROFILE_DERIVED'
      },
      executiveReadiness: { score: 72, liveSources: 3, totalSources: 4 },
      wilsyAiPlan: [],
      accessDecision: { allowed: true },
      mutationReceipts: []
    });

    expect(playbook.phase.key).toBe('foundation');
    expect(playbook.insightRows.length).toBeGreaterThan(0);
    expect(playbook.integrationRows.some(row => row.status === 'SOURCE_REQUIRED')).toBe(true);
    expect(playbook.proofHash).toMatch(/^[A-F0-9]{128}$/);
  });

  it('answers executive revenue questions from local playbook evidence', () => {
    const playbook = buildExecutiveTransformationPlaybook({
      financialKPIs: { revenue: 50000, arr: 75000, currency: 'ZAR' },
      sourceRows: [{ key: 'finance', live: true, status: 'FINANCE_SERVICE_LIVE' }],
      profile: { industryKey: 'general_smb', industryLabel: 'General Business', sourceStatus: 'TENANT_PROFILE_DERIVED' },
      executiveReadiness: { score: 81, liveSources: 1, totalSources: 1 },
      accessDecision: { allowed: true }
    });

    const answer = answerExecutiveNaturalLanguageQuery({
      question: 'Show me ARR forecast',
      financialKPIs: { revenue: 50000, arr: 75000, currency: 'ZAR' },
      sourceRows: [{ key: 'finance', live: true, status: 'FINANCE_SERVICE_LIVE' }],
      executiveReadiness: { score: 81, liveSources: 1, totalSources: 1 },
      transformationPlaybook: playbook
    });

    expect(answer.intent).toBe('revenue_forecast');
    expect(answer.answer).toContain('ARR');
    expect(answer.proofHash).toMatch(/^[A-F0-9]{128}$/);
  });
});
