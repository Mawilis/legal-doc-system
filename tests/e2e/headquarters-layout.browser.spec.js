/**
 * TITLE: WILSY Headquarters responsive layout browser regression
 * VERSION: v1.0.1-VITE-REACT-DOM-ENTRY
 * AUTHORITY: Rendered client evidence only; Python EOS retains all business authority.
 * EPITOME: Measures the real Headquarters component at desktop, wide desktop,
 *          tablet and mobile widths without credentials, database state or writes.
 * ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tests/e2e/headquarters-layout.browser.spec.js
 * COLLABORATION / OWNERSHIP: Playwright renders the existing Vite component and its own scoped styles.
 * CERTIFICATION / UPDATE DATE: 2026-11-16
 * CHANGELOG: v1.0.1-VITE-REACT-DOM-ENTRY proves actual DOM box geometry, overflow, card order and source-honest empty rendering at four widths.
 * COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2.
 * SECURITY / PRIVACY POSTURE: No credentials, tenant records or business content; API requests are denied locally.
 * TENANT BOUNDARY: Unauthenticated presentation-only render; no tenant is selected.
 * AUTHORITY BOUNDARY: Geometry assertions cannot establish authentication, source admission or business truth.
 * FINANCIAL AUTHORITY BOUNDARY: No financial commands or records.
 */
import fs from 'node:fs';
import { chromium, expect, test } from '@playwright/test';

const browserExecutable = process.env.WILSY_BROWSER_EXECUTABLE
  || (process.platform === 'darwin' ? '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome' : undefined);
const evidenceDirectory = process.env.WILSY_HEADQUARTERS_LAYOUT_EVIDENCE_DIR
  || '/tmp/wilsy-headquarters-layout-evidence';
fs.mkdirSync(evidenceDirectory, { recursive: true, mode: 0o700 });

test('Headquarters cards retain approved widths, order and non-overlap at four viewports', async () => {
  const browser = await chromium.launch({
    headless: true,
    executablePath: browserExecutable,
    args: ['--no-sandbox', '--disable-gpu', '--disable-dev-shm-usage'],
  });
  try {
    const page = await browser.newPage({ viewport: { width: 1440, height: 1100 }, deviceScaleFactor: 1 });
    await page.route('**/api/**', (route) => route.fulfill({ status: 401, contentType: 'application/json', body: '{}' }));
    await page.goto(process.env.BROWSER_CERT_BASE_URL || 'http://127.0.0.1:5173/discovery', { waitUntil: 'networkidle' });
    await page.evaluate(() => { document.body.innerHTML = '<div id="hq-layout-regression-root"></div>'; });
    await page.evaluate(async () => {
      const componentUrl = '/src/components/workspaces/WilsyHeadquartersWorkspace.jsx';
      const transformed = await fetch(componentUrl).then((response) => response.text());
      const dependencyUrl = (name) => {
        const match = transformed.match(new RegExp(`from [\\"']([^\\"']*/${name}\\.js\\?v=[^\\"']+)[\\"']`));
        if (!match) throw new Error(`HEADQUARTERS_BROWSER_DEPENDENCY_UNRESOLVED:${name}`);
        return match[1];
      };
      const reactUrl = dependencyUrl('react');
      const routerUrl = dependencyUrl('react-router-dom');
      const domUrl = reactUrl.replace('/react.js?', '/react-dom.js?');
      const [ReactModule, ReactDomModule, RouterModule, AuthModule, WorkspaceModule] = await Promise.all([
        import(reactUrl), import(domUrl), import(routerUrl),
        import('/src/contexts/authContext.jsx'), import(componentUrl),
      ]);
      const React = ReactModule.default;
      const root = ReactDomModule.default.createRoot(document.getElementById('hq-layout-regression-root'));
      root.render(React.createElement(
        RouterModule.MemoryRouter,
        null,
        React.createElement(AuthModule.default.Provider, { value: {} }, React.createElement(WorkspaceModule.default)),
      ));
      window.__headquartersLayoutRegressionRoot = root;
    });
    await page.locator('.hq-operating-grid').waitFor({ state: 'visible' });

    for (const width of [1440, 1760, 1024, 390]) {
      await page.setViewportSize({ width, height: 1100 });
      const measurements = await page.evaluate(() => {
        const box = (selector) => {
          const element = document.querySelector(selector);
          if (!element) throw new Error(`HEADQUARTERS_LAYOUT_ELEMENT_MISSING:${selector}`);
          const rect = element.getBoundingClientRect();
          return { x: rect.x, y: rect.y, width: rect.width, height: rect.height,
            right: rect.right, bottom: rect.bottom, scrollWidth: element.scrollWidth,
            clientWidth: element.clientWidth };
        };
        const grid = document.querySelector('.hq-operating-grid');
        return {
          viewport: document.documentElement.clientWidth,
          documentWidth: document.documentElement.scrollWidth,
          gridColumns: getComputedStyle(grid).gridTemplateColumns.split(' ').length,
          hero: box('.hq-hero'), glance: box('.hq-glance'), kpis: box('.hq-kpis'),
          workColumn: box('[data-hq-column="work"]'),
          organisationColumn: box('[data-hq-column="organisation"]'),
          reportingColumn: box('[data-hq-column="reporting"]'),
          work: box('.hq-work'), performance: box('.hq-performance'),
          organisation: box('.hq-organisation'), departments: box('.hq-departments'),
          strategy: box('.hq-strategy'), calendar: box('.hq-main-reporting'),
          release: box('.hq-release-panel'), actions: box('.hq-quick-actions-panel'),
          buttonsAccessible: [...document.querySelectorAll('.wilsyHqShell button')].every((button) =>
            Boolean((button.getAttribute('aria-label') || button.innerText || button.title).trim())),
          imagesLoaded: [...document.querySelectorAll('.wilsyHqShell img')].every((image) => image.complete && image.naturalWidth > 0),
        };
      });
      expect(measurements.documentWidth, `horizontal overflow at ${width}px`).toBeLessThanOrEqual(measurements.viewport + 1);
      expect(measurements.buttonsAccessible, `unnamed button at ${width}px`).toBe(true);
      expect(measurements.imagesLoaded, `broken image at ${width}px`).toBe(true);
      for (const card of [measurements.work, measurements.performance, measurements.organisation,
        measurements.departments, measurements.strategy, measurements.calendar,
        measurements.release, measurements.actions]) {
        expect(card.scrollWidth, `horizontal card overflow at ${width}px`).toBeLessThanOrEqual(card.clientWidth + 2);
      }

      if (width >= 1200) {
        expect(measurements.gridColumns).toBe(12);
        expect(measurements.workColumn.width).toBeGreaterThan(measurements.organisationColumn.width);
        expect(measurements.organisationColumn.width).toBeGreaterThan(measurements.reportingColumn.width);
        expect(measurements.workColumn.width).toBeGreaterThan(400);
        expect(measurements.organisationColumn.width).toBeGreaterThan(300);
        expect(measurements.reportingColumn.width).toBeGreaterThan(240);
        expect(measurements.workColumn.right).toBeLessThanOrEqual(measurements.organisationColumn.x + 1);
        expect(measurements.organisationColumn.right).toBeLessThanOrEqual(measurements.reportingColumn.x + 1);
        expect(measurements.hero.y).toBeCloseTo(measurements.glance.y, 0);
        expect(measurements.hero.width).toBeGreaterThan(measurements.glance.width * 2.8);
        expect(measurements.glance.width).toBeGreaterThan(measurements.hero.width / 4.2);
        expect(measurements.kpis.width).toBeGreaterThan(measurements.hero.width);
        expect(measurements.work.x).toBe(measurements.performance.x);
        expect(measurements.performance.y).toBeGreaterThanOrEqual(measurements.work.bottom);
        expect(measurements.organisation.x).toBe(measurements.departments.x);
        expect(measurements.departments.y).toBeGreaterThanOrEqual(measurements.organisation.bottom);
        expect(measurements.strategy.x).toBe(measurements.organisationColumn.x);
        expect(measurements.strategy.y).toBeGreaterThanOrEqual(measurements.departments.bottom);
        expect(measurements.calendar.x).toBe(measurements.reportingColumn.x);
        expect(measurements.release.y).toBeGreaterThanOrEqual(measurements.calendar.bottom);
        expect(measurements.actions.y).toBeGreaterThanOrEqual(measurements.release.bottom);
      } else if (width >= 768) {
        expect(measurements.gridColumns).toBe(2);
        expect(measurements.workColumn.x).toBeLessThan(measurements.organisationColumn.x);
        expect(measurements.workColumn.right).toBeLessThanOrEqual(measurements.organisationColumn.x + 1);
        expect(measurements.reportingColumn.y).toBeGreaterThan(measurements.organisationColumn.bottom);
      } else {
        expect(measurements.gridColumns).toBe(1);
        expect(measurements.hero.y).toBeLessThan(measurements.work.y);
        expect(measurements.work.y).toBeLessThan(measurements.performance.y);
        expect(measurements.performance.y).toBeLessThan(measurements.organisation.y);
        expect(measurements.reportingColumn.y).toBeGreaterThan(measurements.organisationColumn.bottom);
      }
      await page.screenshot({ path: `${evidenceDirectory}/headquarters-${width}.png`, fullPage: true });
      console.log(JSON.stringify({ viewport: width, ...measurements }));
    }
  } finally {
    await browser.close();
  }
});

// ARTIFACT: headquarters-layout.browser.spec.js
// VERSION: v1.0.1-VITE-REACT-DOM-ENTRY
// AUTHORITY BOUNDARY: Browser geometry only; no source or command authority.
// TENANT POSTURE: Unauthenticated render with all API requests denied.
// FAIL-CLOSED POSTURE: Missing nodes, overflow, inaccessible controls or wrong bounds fail the test.
// FINANCIAL EXECUTION AUTHORITY: None.
// END OF WILSY OS SOVEREIGN ARTIFACT
