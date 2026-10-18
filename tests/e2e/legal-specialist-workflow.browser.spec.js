/**
 * WILSY OS — Legal Specialist Workflow authenticated browser certificate.
 *
 * Authority:
 * Browser observation only. Python EOS remains sovereign.
 *
 * Visibility:
 * Specialist Workflow may enrich Productive Work already admitted for the
 * authenticated principal. It may never manufacture browser work visibility.
 *
 * Mobile:
 * Secretary executes the same authority model at 390x844.
 */

import fs from 'node:fs';

import { expect, test } from '@playwright/test';

const statePath = process.env.BROWSER_CERT_STATE;

if (!statePath) {
  throw new Error('BROWSER_CERT_STATE_REQUIRED');
}

const state = JSON.parse(
  fs.readFileSync(statePath, 'utf8'),
);

const baseURL = process.env.BROWSER_CERT_BASE_URL;

if (!baseURL) {
  throw new Error('BROWSER_CERT_BASE_URL_REQUIRED');
}

async function openPersona(
  browser,
  actorKey,
  viewport = {
    width: 1440,
    height: 1000,
  },
) {
  const actor = state.actors?.[actorKey];

  if (!actor) {
    throw new Error(
      `P3_ACTOR_MISSING:${actorKey}`,
    );
  }

  const context = await browser.newContext({
    baseURL,
    viewport,
  });

  const page = await context.newPage();

  const pageErrors = [];

  page.on('pageerror', (error) => {
    pageErrors.push(error.message);
  });

  await page.addInitScript(
    ({
      accessToken,
      tenantId,
      principalId,
      email,
    }) => {
      localStorage.setItem(
        'wilsy_auth_token',
        accessToken,
      );
      localStorage.setItem(
        'token',
        accessToken,
      );
      localStorage.setItem(
        'tenantId',
        tenantId,
      );
      localStorage.setItem(
        'wilsy_tenant_id',
        tenantId,
      );
      localStorage.setItem(
        'wilsy_active_tenant',
        JSON.stringify({
          tenantId,
          id: tenantId,
        }),
      );
      localStorage.setItem(
        'wilsy_sovereign_user',
        JSON.stringify({
          id: principalId,
          email,
          tenantId,
        }),
      );
    },
    {
      accessToken: actor.access_token,
      tenantId: state.tenant_id,
      principalId: actor.principal_id,
      email: actor.email,
    },
  );

  const bootstrap = page.waitForResponse(
    (response) => (
      new URL(response.url()).pathname
        === '/api/auth/workspace-bootstrap'
      && response.request().method()
        === 'GET'
    ),
  );

  await page.goto('/');

  expect(
    (await bootstrap).status(),
  ).toBe(200);

  await expect(
    page.getByText(
      'Legal Operations Command Center',
      { exact: true },
    ),
  ).toBeVisible();

  return {
    actor,
    context,
    page,
    pageErrors,
  };
}

async function openMyWork(page) {
  const productivePromise =
    page.waitForResponse(
      (response) => (
        new URL(response.url()).pathname
          === '/api/legal-operations/productive-work'
        && response.request().method()
          === 'GET'
      ),
    );

  const workflowPromise =
    page.waitForResponse(
      (response) => (
        new URL(response.url()).pathname
          === '/api/legal-operations/specialist-workflow'
        && response.request().method()
          === 'GET'
      ),
    );

  await page.getByRole(
    'button',
    {
      name: 'My Work',
      exact: true,
    },
  ).first().click();

  const productiveResponse =
    await productivePromise;

  const workflowResponse =
    await workflowPromise;

  expect(
    productiveResponse.status(),
  ).toBe(200);

  expect(
    workflowResponse.status(),
  ).toBe(200);

  return {
    productive:
      await productiveResponse.json(),

    workflow:
      await workflowResponse.json(),
  };
}

function visibleWorkIds(payload) {
  return new Set([
    ...(payload.assigned_work_items || []),
    ...(payload.supervised_work_items || []),
    ...(payload.overdue_work_items || []),
    ...(payload.due_soon_work_items || []),
  ].map(
    (row) => row.work_item_id,
  ));
}

for (
  const actorKey
  of [
    'partner',
    'attorney',
    'paralegal',
    'secretary',
  ]
) {
  test(
    `P3 ${actorKey} receives only own visible specialist workflow`,
    async ({ browser }) => {
      const mobile =
        actorKey === 'secretary';

      const {
        actor,
        context,
        page,
        pageErrors,
      } = await openPersona(
        browser,
        actorKey,
        mobile
          ? {
            width: 390,
            height: 844,
          }
          : undefined,
      );

      const {
        productive,
        workflow,
      } = await openMyWork(page);

      expect(
        productive.tenant_id,
      ).toBe(
        state.tenant_id,
      );

      expect(
        productive.principal_id,
      ).toBe(
        actor.principal_id,
      );

      expect(
        workflow.tenant_id,
      ).toBe(
        state.tenant_id,
      );

      expect(
        workflow.principal_id,
      ).toBe(
        actor.principal_id,
      );

      const visibleIds =
        visibleWorkIds(productive);

      expect(
        visibleIds.has(
          state.workflow_work_items[
            actorKey
          ],
        ),
      ).toBe(true);

      expect(
        workflow.rows.length,
      ).toBeGreaterThan(0);

      for (
        const row
        of workflow.rows
      ) {
        expect(
          visibleIds.has(
            row.work_item_id,
          ),
          `specialist row ${row.work_item_id} exceeded productive-work visibility`,
        ).toBe(true);
      }

      const ownRow =
        workflow.rows.find(
          (row) => (
            row.work_item_id
            === state.workflow_work_items[
              actorKey
            ]
          ),
        );

      expect(
        ownRow,
      ).toBeTruthy();

      expect(
        ownRow.readiness,
      ).toBe(
        'BLOCKED_DEPENDENCY_AND_GATE',
      );

      expect(
        ownRow.unsatisfied_gate_references,
      ).toContain(
        'gate:review',
      );

      expect(
        ownRow.blocking_dependency_work_item_ids.length,
      ).toBeGreaterThan(0);

      await expect(
        page.locator(
          '[data-legal-specialist-workflow="practice-my-work"]',
        ),
      ).toBeVisible();

      await expect(
        page.getByText(
          `Workflow: ${ownRow.stage_definition_id}`,
          { exact: true },
        ).first(),
      ).toBeVisible();

      await expect(
        page.getByText(
          'Blocked by dependency and gate',
          { exact: true },
        ).first(),
      ).toBeVisible();

      await expect(
        page.getByText(
          /Unsatisfied gates: gate:review/,
        ).first(),
      ).toBeVisible();

      if (mobile) {
        const metrics =
          await page.evaluate(
            () => ({
              viewport:
                window.innerWidth,
              document:
                document.documentElement
                  .scrollWidth,
              body:
                document.body.scrollWidth,
            }),
          );

        expect(
          metrics.viewport,
        ).toBe(390);

        expect(
          metrics.document,
        ).toBeLessThanOrEqual(
          metrics.viewport + 1,
        );

        expect(
          metrics.body,
        ).toBeLessThanOrEqual(
          metrics.viewport + 1,
        );

        await expect(
          page.getByRole(
            'button',
            {
              name: 'Refresh my work',
              exact: true,
            },
          ),
        ).toBeVisible();
      }

      expect(
        pageErrors,
      ).toEqual([]);

      await context.close();
    },
  );
}

// ARTIFACT: legal-specialist-workflow.browser.spec.js
// AUTHORITY: authenticated browser observation only
// PRODUCTIVE WORK VISIBILITY CEILING: absolute
// MOBILE AUTHORITY MODEL: identical to desktop
// SHERIFF / DEPUTY AUTHORITY EXPANSION: none
