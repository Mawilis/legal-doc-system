/**
 * TITLE: WILSY OS HR03 Organization Code Input HTML Pattern Contract
 * VERSION: v1.0.0-M03-HR03-HTML-V-PATTERN-CERT
 * AUTHORITY: WILSY OS People UX / source-owned identifier schema.
 * EPITOME: Catch Chromium HTML pattern v-mode regressions before browser acceptance.
 * ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/client/src/__tests__/components/hrOrganizationCodePattern.test.js
 * COLLABORATION / OWNERSHIP: WILSY OS Workforce Organization client and CI.
 * CERTIFICATION / UPDATE DATE: 2026-11-28
 * CHANGELOG: v1.0.0-M03-HR03-HTML-V-PATTERN-CERT compiles the actual input
 *            pattern under Unicode sets mode and checks identifiers against EOS.
 * COMPLIANCE: WCAG 2.2 user input feedback; AGENTS.md repository integrity.
 * SECURITY / PRIVACY POSTURE: Static component pattern; no personal data.
 * TENANT BOUNDARY: Does not read tenant or employee records.
 * AUTHORITY BOUNDARY: Browser validation complements, never replaces EOS validation.
 * FINANCIAL AUTHORITY BOUNDARY: Kennel EOS exclusively.
 */
import {describe,expect,it} from 'vitest';
import {readFileSync} from 'node:fs';

const source=readFileSync(new URL('../../components/hr/HrDashboard.jsx',import.meta.url),'utf8');
const codeField=source.match(/<input id="wilsy-organization-record-code"[^>]*>/);
const pattern=codeField?.[0].match(/pattern="([^"]+)"/)?.[1];

describe('HR03 organization identifier HTML pattern',()=>{
  it('compiles as an HTML v-mode expression and accepts exact EOS identifiers',()=>{
    expect(typeof pattern).toBe('string');
    const expression=new RegExp('^(?:'+pattern+')$','v');
    expect(expression.test('DEP-SOFTWARE-ENGINEERING')).toBe(true);
    expect(expression.test('DEP_OPERATIONS:1.2')).toBe(true);
    expect(expression.test('POS-A')).toBe(true);
    expect(expression.test('DEP HAS SPACES')).toBe(false);
    expect(expression.test('DEP/INVALID')).toBe(false);
  });
});
/**
 * ARTIFACT: client/src/__tests__/components/hrOrganizationCodePattern.test.js
 * VERSION: v1.0.0-M03-HR03-HTML-V-PATTERN-CERT
 * AUTHORITY BOUNDARY: Browser regex contract only; EOS remains authoritative.
 * TENANT POSTURE: No tenant or identity fixtures.
 * FAIL-CLOSED POSTURE: Invalid expressions or wrong input acceptance fail CI.
 * FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively.
 * END OF WILSY OS SOVEREIGN ARTIFACT
 */
