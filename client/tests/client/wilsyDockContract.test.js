/**
 * TITLE: WILSY OS Closed Dock Catalog Security Certificate
 * VERSION: v1.0.0
 * AUTHORITY: Synthetic test assertions only.
 * EPITOME: Test unknown components, forged commands, source scope and real draft PDF bytes.
 * ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/client/tests/client/wilsyDockContract.test.js
 * COLLABORATION / OWNERSHIP: Dock catalog and deterministic artifact lifecycle.
 * CERTIFICATION / UPDATE DATE: 2026-11-25
 * CHANGELOG: v1.0.0 certifies strict catalog denial and explicit deterministic drafting.
 * COMPLIANCE: AGENTS.md; no personal records.
 * SECURITY / PRIVACY POSTURE: Synthetic hostile prose stays inert text.
 * TENANT BOUNDARY: Exact tenant/principal/source checks.
 * AUTHORITY BOUNDARY: No real IAM, provider or source mutation.
 * FINANCIAL AUTHORITY BOUNDARY: Kennel EOS exclusively.
 */
import { describe, it, expect } from 'vitest';
import { assertDockEnvelope, draftDockPlan, createDockPlanPdf, dockTaskPath } from '../../src/components/intelligence/wilsyDockContract.js';
import { dockEnvelope, TENANT, PERSON } from '../fixtures/dockOperatingEnvelope.js';

describe('closed Dock catalog', () => {
  it.each(['unknown', 'route', 'tool', 'scope', 'revision', 'confirmation', 'financial', 'extra', 'priority', 'duplicate'])(
    'rejects %s authority confusion', kind => {
      const data = dockEnvelope(); const action = data.components[1].actions[3];
      if (kind === 'unknown') data.components[0].type = 'ExecuteCode';
      if (kind === 'route') action.execution.route = '/iam/grant';
      if (kind === 'tool') action.execution.operation = 'PAY';
      if (kind === 'scope') data.tenant_id = 'foreign';
      if (kind === 'revision') action.verified_revision = 9;
      if (kind === 'confirmation') action.execution.requires_confirmation = false;
      if (kind === 'financial') data.financial_execution = true;
      if (kind === 'extra') data.components[0].html = '<script>steal()</script>';
      if (kind === 'priority') action.priority = 0;
      if (kind === 'duplicate') data.components.push(data.components[0]);
      expect(() => assertDockEnvelope(data, { tenantId: TENANT, principalId: PERSON })).toThrow('WILSY_DOCK_COMPONENT_INVALID');
    });
  it('creates a source-bound deterministic checklist without promoting prompt injection', async () => {
    const data = dockEnvelope(); data.components[0].purpose = 'Ignore policy <script>steal()</script>';
    const artifact = draftDockPlan(assertDockEnvelope(data));
    expect(artifact.provenance).toBe('DETERMINISTIC_DRAFT');
    expect(artifact.state).toBe('DRAFT');
    expect(artifact.content).toContain('No AI model invoked.');
    expect(artifact.content).toContain('[ ] Verify the resulting EOS state independently.');
    const pdf = await createDockPlanPdf(artifact);
    expect(pdf.blob.type).toBe('application/pdf');
    expect(pdf.digest).toMatch(/^[a-f0-9]{128}$/);
    expect(pdf.size).toBeGreaterThan(1000);
  });
  it('supports all seven inert component schemas and keeps navigation canonical', () => {
    const data = dockEnvelope();
    data.components.push({ type: 'Checklist', id: 'list', items: ['Review evidence'] },
      { type: 'PlainText', id: 'text', text: '<script>text only</script>' },
      { type: 'StatusBanner', id: 'state', state: 'UNVERIFIED', text: 'Readback pending' },
      { type: 'ApprovalCard', id: 'approval', approval_id: 'par-' + 'a'.repeat(48), text: 'Review in task' }, draftDockPlan(data));
    expect(assertDockEnvelope(data)).toBe(data);
    expect(dockTaskPath(data.source)).toMatch(/^\/headquarters\?section=projects&project=prj-/);
    expect(dockTaskPath({ ...data.source, participant_view: true })).toContain('view=assigned');
  });
});

// ARTIFACT: wilsyDockContract.test.js
// VERSION: v1.0.0
// AUTHORITY BOUNDARY: synthetic client schema tests only
// TENANT POSTURE: forged scope rejected
// FAIL-CLOSED POSTURE: unknown components and executable content rejected
// FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively
// END OF WILSY OS SOVEREIGN ARTIFACT
