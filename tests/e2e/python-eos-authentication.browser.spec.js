/**
 * TITLE: Python EOS password + TOTP browser certification
 * VERSION: v1.0.0-PYTHON-EOS-LOGIN-MFA-CERT
 * AUTHORITY: Disposable authenticated browser certification only.
 * EPITOME: Exercises the actual sign-in and MFA UI against Python EOS, then
 *          proves the Legal workspace remains fail-closed without ratification.
 * ABSOLUTE CANONICAL PATH: tests/e2e/python-eos-authentication.browser.spec.js
 * COLLABORATION / OWNERSHIP: Python EOS auth router, AuthContext, SovereignLogin,
 *                            SovereignMfaPortal, and guarded Legal Operations.
 * CERTIFICATION / UPDATE DATE: 2026-10-27
 * CHANGELOG: v1.0.0 adds a real password + TOTP browser journey using disposable
 *            fixture credentials and verifies the unratified workspace boundary.
 * SECURITY / PRIVACY POSTURE: Credentials, TOTP secret, and access token stay in
 *                             fixture memory/localStorage and are never printed.
 * TENANT BOUNDARY: Uses only the runner-owned synthetic tenant.
 * AUTHORITY BOUNDARY: Proves authentication only; no production authority is granted.
 * FAIL-CLOSED POSTURE: Successful MFA must not bypass the separate Legal workspace gate.
 */

import { createHmac } from 'node:crypto';
import fs from 'node:fs';

import { expect, test } from '@playwright/test';

const statePath = process.env.BROWSER_CERT_STATE;
if (!statePath) throw new Error('BROWSER_CERT_STATE_REQUIRED');
const state = JSON.parse(fs.readFileSync(statePath, 'utf8'));
const baseURL = process.env.BROWSER_CERT_BASE_URL || 'http://127.0.0.1:5174';

function decodeBase32(secret) {
  const alphabet = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ234567';
  let bits = 0;
  let value = 0;
  const bytes = [];
  for (const character of String(secret || '').replace(/=+$/u, '').toUpperCase()) {
    const digit = alphabet.indexOf(character);
    if (digit < 0) throw new Error('BROWSER_CERT_TOTP_SECRET_INVALID');
    value = (value << 5) | digit;
    bits += 5;
    if (bits >= 8) {
      bits -= 8;
      bytes.push((value >> bits) & 0xff);
    }
  }
  return Buffer.from(bytes);
}

function currentTotp(secret, now = Date.now()) {
  const counter = BigInt(Math.floor(now / 1000 / 30));
  const counterBytes = Buffer.alloc(8);
  counterBytes.writeBigUInt64BE(counter);
  const digest = createHmac('sha1', decodeBase32(secret)).update(counterBytes).digest();
  const offset = digest[digest.length - 1] & 0x0f;
  const binary = digest.readUInt32BE(offset) & 0x7fffffff;
  return String(binary % 1_000_000).padStart(6, '0');
}

test('password + TOTP succeed through Python EOS; Legal workspace remains fail-closed', async ({ page }) => {
  const actor = state.actors?.partner;
  expect(actor?.email).toBeTruthy();
  expect(actor?.password).toBeTruthy();
  expect(actor?.otp_secret).toBeTruthy();

  await page.goto('/login');
  await page.getByLabel('Work email').fill(actor.email);
  await page.getByLabel('Password').fill(actor.password);

  const loginResponsePromise = page.waitForResponse((response) => (
    new URL(response.url()).pathname === '/api/auth/login'
    && response.request().method() === 'POST'
  ));
  await page.getByRole('button', { name: 'Continue securely' }).click();
  const loginResponse = await loginResponsePromise;
  expect(loginResponse.status()).toBe(200);
  const loginPayload = await loginResponse.json();
  expect(loginPayload.status).toBe('MFA_REQUIRED');
  expect(loginPayload.requiresMFA).toBe(true);
  expect(loginPayload.tempToken).toBeTruthy();
  await expect(page).toHaveURL(/\/mfa(?:\?.*)?$/u);

  const verifyResponsePromise = page.waitForResponse((response) => (
    ['/api/auth/verify-3fa', '/api/auth/verify-otp'].includes(new URL(response.url()).pathname)
    && response.request().method() === 'POST'
  ));
  await page.getByLabel('Six-digit code').fill(currentTotp(actor.otp_secret));
  await page.getByRole('button', { name: 'Verify identity' }).click();
  const verifyResponse = await verifyResponsePromise;
  expect(verifyResponse.status()).toBe(200);
  await expect(page).not.toHaveURL(/\/mfa(?:\?.*)?$/u);

  const accessToken = await page.evaluate(() => (
    localStorage.getItem('wilsy_auth_token') || localStorage.getItem('token')
  ));
  expect(accessToken).toBeTruthy();

  const workspaceResponse = await page.request.get(
    `${baseURL}/api/legal-operations/workspace`,
    { headers: { Authorization: `Bearer ${accessToken}`, 'X-Tenant-ID': state.tenant_id } },
  );
  expect(workspaceResponse.status()).toBe(503);
  const workspacePayload = await workspaceResponse.json();
  expect(JSON.stringify(workspacePayload)).toMatch(/LEGAL_OPERATIONS_WORKSPACE_[A-Z_]+/u);
});

// ARTIFACT: python-eos-authentication.browser.spec.js
// AUTHORITY BOUNDARY: Disposable browser auth proof only.
// TENANT POSTURE: Runner-owned synthetic tenant only.
// FAIL-CLOSED POSTURE: MFA success never overrides Legal Operations ratification gate.
// END OF WILSY OS SOVEREIGN ARTIFACT
