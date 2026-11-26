/**
 * TITLE: WILSY OS Projects Workspace CSS Source Certificate
 * VERSION: v1.0.0-NODE-ISOLATED-CSS-CONTRACT
 * AUTHORITY: Node-only frontend CSS contract test; no Python EOS authority.
 * EPITOME: Verify template and accountability contrast declarations in exact CSS source.
 * ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/client/scripts/certify-projects-workspace-css.mjs
 * COLLABORATION / OWNERSHIP: Projects workspace UI and source-backed frontend certification.
 * CERTIFICATION / UPDATE DATE: 2026-11-26
 * CHANGELOG: v1.0.0-NODE-ISOLATED-CSS-CONTRACT moves exact CSS-text assertions outside
 *            jsdom/Vite transforms, preserving every original contract.
 * COMPLIANCE: AGENTS.md; POPIA section 19; GDPR Article 32.
 * SECURITY / PRIVACY POSTURE: Read-only local repository CSS; no network or identity.
 * TENANT BOUNDARY: No tenant records or cross-tenant reads.
 * AUTHORITY BOUNDARY: No task, approval, tenant or financial mutation authority.
 * FINANCIAL AUTHORITY BOUNDARY: No payment or settlement authority.
 * FAIL-CLOSED POSTURE: Missing stylesheet or missing CSS declarations fail the test.
 */
import { readFileSync } from 'node:fs';
import { fileURLToPath } from 'node:url';
import { dirname, resolve } from 'node:path';
import test from 'node:test';
import assert from 'node:assert/strict';

const css = readFileSync(
  resolve(dirname(fileURLToPath(import.meta.url)), '../src/components/workspaces/ProjectsWorkspace.css'),
  'utf8',
);

test('industry template labels retain explicit readable contrast', () => {
  assert.ok(css.includes('[aria-label="Industry project templates"] form :is(label, legend)'));
  assert.ok(css.includes('-webkit-text-fill-color: #193451 !important;'));
});

test('accountability labels retain source-specific legibility rules', () => {
  assert.match(css, /\.wilsy-projects \.wp-detail \.wp-accountability form label\s*\{[^}]*color:\s*#203a5e\s*!important;/);
  assert.match(css, /\.wilsy-projects \.wp-detail \.wp-accountability form label\s*\{[^}]*text-transform:\s*none\s*!important;/);
});

// ARTIFACT: certify-projects-workspace-css.mjs
// VERSION: v1.0.0-NODE-ISOLATED-CSS-CONTRACT
// AUTHORITY BOUNDARY: Read-only Node test; EOS owns source authorization
// TENANT POSTURE: No tenant records; no business IAM authority
// FAIL-CLOSED POSTURE: CSS source rules missing = test failure
// FINANCIAL EXECUTION AUTHORITY: none
// END OF WILSY OS SOVEREIGN ARTIFACT
