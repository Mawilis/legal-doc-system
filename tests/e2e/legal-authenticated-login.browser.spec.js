/**
 * TITLE: WILSY OS real authenticated login and Legal Operations browser certificate
 * VERSION: v1.0.0-PYTHON-EOS-LOGIN-LEGAL-OPS-BROWSER-CERT
 * AUTHORITY: Browser certification evidence only.
 * EPITOME: Exercises the real sign-in form, canonical Python EOS password/MFA
 *          endpoints, durable session promotion, workspace bootstrap and
 *          authenticated Legal Operations productive-work projection.
 * ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tests/e2e/legal-authenticated-login.browser.spec.js
 * COLLABORATION / OWNERSHIP: Python EOS owns credentials, MFA, session and Legal IAM;
 *                            this test observes only the real browser/runtime contract.
 * CERTIFICATION / UPDATE DATE: 2026-10-27
 * CHANGELOG: v1.0.0 adds a real browser login journey with server-verified TOTP;
 *            existing browser certificates may continue testing already-issued sessions.
 * COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2.
 * SECURITY / PRIVACY POSTURE: Synthetic credentials remain in a mode-0600 temporary
 *                             state file and are never logged or included in assertions.
 * TENANT BOUNDARY: Only the disposable fixture tenant and seeded principal are used.
 * AUTHORITY BOUNDARY: Test assertions only; no client-side identity or authorization authority.
 * FINANCIAL AUTHORITY BOUNDARY: None; Kennel EOS remains exclusive.
 */

import crypto from 'node:crypto';
import fs from 'node:fs';
import { expect, test } from '@playwright/test';

const statePath = process.env.BROWSER_CERT_STATE;
if (!statePath) throw new Error('BROWSER_CERT_STATE_REQUIRED');
const state = JSON.parse(fs.readFileSync(statePath, 'utf8'));
const actor = state.actors?.partner;
if (!actor?.email || !actor?.password || !actor?.otp_secret) {
  throw new Error('BROWSER_CERT_REAL_LOGIN_FIXTURE_INCOMPLETE');
}

function totp(secret, at = Date.now()) {
  const alphabet = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ234567';
  const normalized = secret.replace(/=+$/g, '').toUpperCase();
  let bits = '';
  for (const char of normalized) {
    const value = alphabet.indexOf(char);
    if (value < 0) throw new Error('BROWSER_CERT_TOTP_SECRET_INVALID');
    bits += value.toString(2).padStart(5, '0');
  }
  const key = Buffer.alloc(Math.floor(bits.length / 8));
  for (let i = 0; i < key.length; i += 1) {
    key[i] = Number.parseInt(bits.slice(i * 8, i * 8 + 8), 2);
  }
  const counter = BigInt(Math.floor(at / 30_000));
  const message = Buffer.alloc(8);
  message.writeBigUInt64BE(counter);
  const digest = crypto.createHmac('sha1', key).update(message).digest();
  const offset = digest[digest.length - 1] & 0x0f;
  const binary = (
    ((digest[offset] & 0x7f) << 24)
    | ((digest[offset + 1] & 0xff) << 16)
    | ((digest[offset + 2] & 0xff) << 8)
    | (digest[offset + 3] & 0xff)
  );
  return String(binary % 1_000_000).padStart(6, '0');
}

test('real browser login verifies password and TOTP before Legal Operations access', async ({ page }) => {
  const observedApiFailures = [];
  page.on('response', (response) => {
    const pathname = new URL(response.url()).pathname;
    if (
      pathname.startsWith('/api/auth/')
      || pathname.startsWith('/api/legal-operations/')
    ) {
      if (response.status() >= 500) observedApiFailures.push(response.status());
    }
  });

  await page.goto('/login');
  await expect(page.getByRole('heading', { name: 'Sign in' })).toBeVisible();
  await page.locator('#work-email').fill(actor.email);
  await page.locator('#work-password').fill(actor.password);

  const loginResponsePromise = page.waitForResponse((response) => (
    new URL(response.url()).pathname === '/api/auth/login'
    && response.request().method() === 'POST'
  ));
  await page.getByRole('button', { name: 'Continue securely' }).click();
  const loginResponse = await loginResponsePromise;
  expect(loginResponse.status()).toBe(200);
  expect((await loginResponse.json()).status).toBe('MFA_REQUIRED');
  await expect(page).toHaveURL(/\/mfa$/);
  await expect(page.locator('#mfa-code')).toBeVisible();

  const verifyResponsePromise = page.waitForResponse((response) => (
    new URL(response.url()).pathname === '/api/auth/verify-otp'
    && response.request().method() === 'POST'
  ));
  const bootstrapResponsePromise = page.waitForResponse((response) => (
    new URL(response.url()).pathname === '/api/auth/workspace-bootstrap'
    && response.request().method() === 'GET'
  ));
  await page.locator('#mfa-code').fill(totp(actor.otp_secret));
  await page.getByRole('button', { name: 'Verify identity' }).click();
  const verifyResponse = await verifyResponsePromise;
  expect(verifyResponse.status()).toBe(200);
  const authenticated = await verifyResponse.json();
  expect(authenticated.status).toBe('AUTHENTICATED');
  expect(typeof authenticated.token).toBe('string');
  expect(authenticated.token.length).toBeGreaterThan(20);

  const bootstrapResponse = await bootstrapResponsePromise;
  expect(bootstrapResponse.status()).toBe(200);

  await page.goto('/legal/');
  const productiveWork = await page.waitForResponse((response) => (
    new URL(response.url()).pathname === '/api/legal-operations/productive-work'
    && response.request().method() === 'GET'
  ));
  expect(productiveWork.status()).toBe(200);
  expect(observedApiFailures).toEqual([]);
});

// ARTIFACT: legal-authenticated-login.browser.spec.js
// VERSION: v1.0.0-PYTHON-EOS-LOGIN-LEGAL-OPS-BROWSER-CERT
// AUTHORITY BOUNDARY: browser certification only
// TENANT POSTURE: disposable synthetic tenant only
// FAIL-CLOSED POSTURE: password, TOTP, session, workspace, or Legal Ops failures fail the test
// FINANCIAL EXECUTION AUTHORITY: Kennel EOS remains exclusive
// END OF WILSY OS SOVEREIGN ARTIFACT
