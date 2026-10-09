/**
 * TITLE: WILSY OS authenticated browser-certification harness
 * VERSION: v1.0.0-L8-8M-R3-PLAYWRIGHT-CONFIG
 * AUTHORITY: Test orchestration only; no application or legal authority.
 * EPITOME: Provide one deterministic, repository-local Playwright configuration
 *          for the disposable authenticated Legal OS browser certificate.
 * ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tests/e2e/playwright.config.js
 * COLLABORATION / OWNERSHIP: L8-8M-R3 browser certificate infrastructure.
 * CERTIFICATION / UPDATE DATE: 2026-09-26
 * CHANGELOG: v1.0.0 selects Chromium-compatible browser execution, a bounded
 *             base URL, one worker, and no committed browser binaries.
 * COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2.
 * SECURITY / PRIVACY POSTURE: Test state is supplied through a temporary file;
 *                             credentials and bearer values are never reported.
 * TENANT BOUNDARY: The fixture supplies one disposable tenant only.
 * AUTHORITY BOUNDARY: Browser automation and assertion only.
 * FINANCIAL AUTHORITY BOUNDARY: None; Kennel EOS remains exclusive.
 */

import { defineConfig, devices } from '@playwright/test';

export default defineConfig({
  testDir: '.',
  testMatch: '**/*.browser.spec.js',
  timeout: 90_000,
  expect: { timeout: 15_000 },
  fullyParallel: false,
  workers: 1,
  retries: 0,
  reporter: process.env.CI ? [['line']] : [['list']],
  use: {
    baseURL: process.env.BROWSER_CERT_BASE_URL || 'http://127.0.0.1:5174',
    browserName: 'chromium',
    launchOptions: {
      executablePath: process.env.WILSY_BROWSER_EXECUTABLE
        || (process.platform === 'darwin'
          ? '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome'
          : undefined),
    },
    headless: true,
    trace: 'retain-on-failure',
    screenshot: 'only-on-failure',
    video: 'off',
    ...devices['Desktop Chrome'],
  },
});

// ARTIFACT: playwright.config.js
// VERSION: v1.0.0-L8-8M-R3-PLAYWRIGHT-CONFIG
// AUTHORITY BOUNDARY: browser test configuration only
// TENANT POSTURE: disposable fixture scope only
// FAIL-CLOSED POSTURE: no hidden retries or production endpoint defaults
// FINANCIAL EXECUTION AUTHORITY: Kennel EOS remains exclusive
// END OF WILSY OS SOVEREIGN ARTIFACT
