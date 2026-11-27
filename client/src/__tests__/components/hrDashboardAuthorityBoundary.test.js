/**
 * TITLE: WILSY OS HR Dashboard Authority and Read-State Regression Certificate
 * VERSION: v1.8.5-GLOBAL-PEOPLE-SEARCH-CONTEXT-CERT
 * AUTHORITY: Wilsy OS Core Governance
 * EPITOME: Prevents dashboard consumers from presenting unavailable or stale HR
 *          sources as empty success and guards the exact session invalidation boundary.
 * ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/client/src/__tests__/components/hrDashboardAuthorityBoundary.test.js
 * COLLABORATION / OWNERSHIP: Client HR dashboard and hrService contract maintainers.
 * CERTIFICATION / UPDATE DATE: 2026-11-27
 * CHANGELOG:
 *   v1.8.5-GLOBAL-PEOPLE-SEARCH-CONTEXT-CERT verifies the global header and command overlay switch to functional People navigation rather than retaining generic work search.
 *   v1.8.4-READ-SCOPE-NOT-DECISION-AUTHORITY prevents treating readable submitted requisitions as the current operator's approval grant; command authority remains EOS-owned.
 *   v1.8.3-TRANSACTIONAL-HEADCOUNT-PAGINATION-CERT guards exact-tenant headcount page provenance, true total and server-owned hasMore rather than client truncation.
 *   v1.8.2-ONE-OVERVIEW-ADMISSION-RECOVERY certifies the single current-capacity denial recovery and real source-admission flags without repeated fake empty metrics.
 *   v1.8.1-M03-EXACT-HEADCOUNT-APPROVAL-SOURCE certifies source-owned submitted headcount approval queue rows and removal of the retired BFF headcount read.
 *   v1.8.0-CANONICAL-EOS-OVERVIEW-AND-CONTEXT-SEARCH guards live Python EOS workforce summary provenance and global context-aware People search without adding client-side authority or false KPI state.
 *   v1.7.0-EMPLOYER-IDENTITY-WORK-FIRST-OVERVIEW certifies authenticated tenant header/footer contract and functional work-first People Overview on a light Headquarters canvas without synthetic records.
 *   v1.6.3-NO-SPECULATIVE-HR-SOURCE-FANOUT certifies unavailable Onboarding/Exit UI does not trigger unrelated workforce or headcount requests, while Overview still reads bound EOS work sources.
 *   v1.6.2-NO-DECORATIVE-UNVERIFIED-METRICS certifies zero-admitted source views show a single honest authority state rather than four decorative unavailable KPI tiles.
 *   v1.6.1-LIFECYCLE-NAV-FAIL-CLOSED-CERT certifies source-unconnected onboarding/exit navigation is available without invalid API requests or simulated employee mutations.
 *   v1.6.0-PROTOTYPE-OWNED-PEOPLE-APPLICATION-CERT certifies prototype-grounded full People application composition, truthful EOS-only overview, single global logo and Headquarters-owned footer.
 *   v1.5.2-HR01-LEGACY-PROFILE-RETIREMENT — Asserts the unconditional black/gold HR profile card is unmounted in favour of the global authenticated WILSY identity.
 *   v1.5.1-HR01-SOURCE-PROVENANCE-PRIVACY-CERT — Guards canonical EOS workforce provenance and denies passthrough of employee PII into browser state.
 *   v1.5.0-HR01-VISIBLE-SOURCE-STATUS-AND-CONTRAST — Guards rendered People headings/error/search contrast and saturated source-owned badges/Project row accents.
 *   v1.4.1-M03-STATUS-PARITY-PROJECTS-AND-PEOPLE — Asserts both canonical Project task row and lifecycle chart use the same semantic source-status contract as People.
 *   v1.4.0-M03-PEOPLE-SURFACE-AND-STATUS-CERT — Certifies unified People surface, no wrong logo or black/gold chrome, read-only future modules and shared status semantics.
 *   v1.3.1-HR-STRICT-PAGE-CONTRACT — Aligns the regression assertion with the normalizer that requires source pagination metadata before verification.
 *   v1.3.0-HR-STRICT-PAGE-CONTRACT — Requires source pagination metadata before a workforce response can become verified data or verified empty.
 *   v1.2.0-HR-NO-MISSING-METRIC-ZERO — Guards snapshot count and currency formatters against turning missing or invalid values into zero.
 *   v1.1.0-HR-SESSION-INVALIDATION — Certifies explicit read states, verified-empty rendering, tenant/principal/session scoping, and all-request invalidation after 401.
 *   v1.0.0-HR-DASHBOARD-AUTHORITY-BOUNDARY-RED — Prevented unsupported HR dashboard
 *     actions from being presented as executable without Python EOS authority.
 * COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2.
 * SECURITY / PRIVACY POSTURE: Static contract checks contain no credentials or HR
 *                             payloads and protect against stale cross-scope display.
 * TENANT BOUNDARY: Dashboard reads require the exact authenticated tenant and principal.
 * AUTHORITY BOUNDARY: Tests verify presentation and transport contracts only; Python
 *                     EOS remains the source of authorization and HR business truth.
 * FINANCIAL AUTHORITY BOUNDARY: No financial execution authority; Kennel EOS remains exclusive.
 */

import fs from 'node:fs';
import path from 'node:path';
import { describe, expect, it } from 'vitest';
import { workStatusTone, workStatusColor, workStatusClasses } from '../../theme/workStatus.js';

const ROOT = process.cwd();
const dashboardPath = path.join(ROOT, 'src/components/hr/HrDashboard.jsx');
const projectRowPath = path.join(ROOT, 'src/components/workspaces/ProjectWorkRow.jsx');
const projectTasksPath = path.join(ROOT, 'src/components/workspaces/ProjectTasksPanel.jsx');
const servicePath = path.join(ROOT, 'src/services/hrService.js');
const dashboard = fs.readFileSync(dashboardPath, 'utf8');
const projectRow = fs.readFileSync(projectRowPath, 'utf8');
const projectTasks = fs.readFileSync(projectTasksPath, 'utf8');
const service = fs.readFileSync(servicePath, 'utf8');

const forbiddenDashboardCalls = [
  'hrService.getEmployeeWorkLogs',
  'hrService.getEmployeeRelations',
  'hrService.getHrArtifacts',
  'hrService.generateHrArtifact',
  'hrService.updateCandidate',
  'hrService.updatePayrollRecord',
  'hrService.createPayrollRecord',
  'hrService.updateEmployeeWorkLog',
  'hrService.createEmployeeWorkLog',
  'hrService.updateEmployeeRelation',
  'hrService.createEmployeeRelation',
  'hrService.generatePayslip',
  'hrService.deleteEmployeeWorkLog',
  'hrService.deleteEmployeeRelation',
  'hrService.getEmployees',
  'hrService.createEmployee',
  'hrService.updateEmployee',
  'hrService.deleteEmployee',
];

const forbiddenInventedServiceExports = [
  'getEmployeeWorkLogs',
  'getEmployeeRelations',
  'getHrArtifacts',
  'generateHrArtifact',
  'updateCandidate',
  'updatePayrollRecord',
  'createPayrollRecord',
  'updateEmployeeWorkLog',
  'createEmployeeWorkLog',
  'updateEmployeeRelation',
  'createEmployeeRelation',
  'generatePayslip',
  'deleteEmployeeWorkLog',
  'deleteEmployeeRelation',
];

const requiredExistingServiceExports = [
  'getEmployees',
  'createEmployee',
  'updateEmployee',
  'deleteEmployee',
  'getRecruitmentCandidates',
  'createCandidate',
  'updateCandidateStage',
  'deleteCandidate',
  'getPayrollSummary',
  'syncPayroll',
  'getBenefits',
  'getPerformanceReviews',
  'getTimeOffRequests',
];

describe('HR dashboard authority and read-state boundary', () => {
  it('does not call stale or unauthorized HR capabilities', () => {
    for (const symbol of forbiddenDashboardCalls) {
      expect(dashboard, `dashboard must not invoke ${symbol}`).not.toContain(symbol);
    }
  });

  it('does not solve parity by inventing unsupported hrService exports', () => {
    for (const symbol of forbiddenInventedServiceExports) {
      const declarationPattern = new RegExp(
        `\\bexport\\s+(?:(?:async\\s+)?function|const|let|var)\\s+${symbol}\\b`,
      );
      expect(service, `hrService must not manufacture ${symbol}`).not.toMatch(declarationPattern);
    }
  });

  it('preserves existing service exports while keeping their failures transparent', () => {
    for (const symbol of requiredExistingServiceExports) {
      expect(service, `existing service export ${symbol} must remain`).toMatch(
        new RegExp(`export\\s+const\\s+${symbol}\\b`),
      );
    }
    expect(service).toContain("createHrTransportError('HR_API_CIRCUIT_OPEN', 503)");
    expect(service).toContain("createHrTransportError('HR_SOURCE_RESPONSE_INVALID', 502)");
    expect(service).not.toMatch(/return\s+emptyPage\b/);
  });

  it('keeps verified data, verified empty, denied, unavailable and authentication states distinct', () => {
    for (const state of [
      'VERIFIED_DATA',
      'VERIFIED_EMPTY',
      'ACCESS_DENIED',
      'SOURCE_UNAVAILABLE',
      'AUTHENTICATION_REQUIRED',
    ]) {
      expect(dashboard).toContain(`${state}: '${state}'`);
    }
    expect(dashboard).toContain('const verifiedDataset = normalizeDataset(payload)');
    expect(dashboard).toContain('unavailableReadState(previous[tabName], errorCode)');
    expect(dashboard).toContain("if (status === 401) return HR_READ_STATE.AUTHENTICATION_REQUIRED");
    expect(dashboard).toContain("if (status === 403) return HR_READ_STATE.ACCESS_DENIED");
    expect(dashboard).toContain("if (value === null || value === undefined || value === '') return 'Unavailable'");
    expect(dashboard).toContain("if (!Number.isFinite(numeric)) return 'Unavailable'");
    expect(dashboard).toContain('const total = payload.total;');
    expect(dashboard).toContain('const hasMore = payload.hasMore;');
    expect(dashboard).not.toContain('payload.total ?? items?.length');
  });

  it('shows no employees only after a valid authoritative empty workforce response', () => {
    expect(dashboard).toContain("api.get('/hr/workforce'");
    expect(dashboard).toContain('shownState?.status === HR_READ_STATE.VERIFIED_EMPTY');
    expect(dashboard).toContain('EOS verified no records for this view.');
    expect(dashboard).toContain('isVerifiedReadState(shownState)');
    expect(dashboard).not.toContain('Employee admission unavailable');
    expect(dashboard).not.toContain('DEFAULT_TENANT_ID');
    expect(dashboard).not.toContain("'MASTER'");
  });

  it('clears current HR data and invalidates every pending source read after a 401', () => {
    expect(dashboard).toContain('invalidatedSessionScopeKeyRef = useRef(null)');
    expect(dashboard).toContain('invalidatedSessionScopeKeyRef.current === requestedScopeKey');
    expect(dashboard).toContain('invalidateHrSessionScope(requestedScopeKey, errorCode)');
    expect(dashboard).toContain('snapshotRequestSequenceRef.current += 1');
    expect(dashboard).toContain('datasetRequestSequencesRef.current[datasetName] =');
    expect(dashboard).toContain('setDatasetReadStates(createInitialDatasetReadStates(HR_READ_STATE.AUTHENTICATION_REQUIRED))');
    expect(dashboard).toContain('setSnapshot(createEmptySnapshot())');
  });

  it('binds pending reads to exact tenant, principal and authenticated session generation', () => {
    expect(dashboard).toContain('`${tenantId}\\u001f${principalId}\\u001f${String(auth.sessionGeneration ?? \'\')}`');
    expect(dashboard).toContain('tenantScopeKeyRef.current !== requestedScopeKey');
    expect(dashboard).toContain('datasetRequestSequencesRef.current[tabName] !== requestSequence');
  });

  it('does not couple HR artifact generation to an uncertified relation write', () => {
    const artifactStart = dashboard.indexOf('const generateArtifact = async');
    expect(artifactStart).toBeGreaterThanOrEqual(0);
    const artifactEnd = dashboard.indexOf('const generatePayslip = async', artifactStart);
    expect(artifactEnd).toBeGreaterThan(artifactStart);
    expect(dashboard.slice(artifactStart, artifactEnd)).not.toContain('hrService.createEmployeeRelation');
  });

  it('does not advertise executable payslip generation without backend authority', () => {
    expect(dashboard).not.toContain('hrService.generatePayslip');
  });
  it('replaces the legacy HR chrome and wrong logo without fabricating commands', () => {
    expect(dashboard).toContain('data-testid="people-os-workspace"');
    expect(dashboard).toContain('Plan · Hire · Onboard · Manage · Pay inputs · Grow · Correct · Exit');
    expect(dashboard).not.toContain('<WilsyOSDashboardChrome');
    expect(dashboard).not.toContain('<WilsyProfilePanel');
    expect(dashboard).not.toContain('wilsy-logo.svg');
    expect(dashboard).toContain("const isSourceConnected = ['employees', 'candidates', 'offers', 'jobOpenings'].includes(activeTab)");
    expect(dashboard).toContain('No simulated records or actions are shown.');
  });

  it('shares verified status colours with project tasks and retains text labels', () => {
    expect(workStatusTone('IN_PROGRESS')).toBe('active');
    expect(workStatusTone('DONE')).toBe('success');
    expect(workStatusTone('BLOCKED')).toBe('blocked');
    expect(workStatusTone('PENDING')).toBe('caution');
    expect(workStatusTone('unrecognized_eos_status')).toBe('neutral');
    expect(workStatusColor('DONE')).toBe('#15803d');
    expect(workStatusColor('BLOCKED')).toBe('#be3640');
    expect(workStatusClasses('APPROVED')).toContain('bg-emerald-700 text-white');
    expect(dashboard).toContain('workStatusClasses(value)');
    expect(projectRow).toContain('workStatusClasses(pendingStatus !== null');
    expect(projectRow).toContain('workStatusAccentClass(item.status)');
    expect(projectTasks).toContain('workStatusColor(status)');
  });

  it('prevents inherited HR palette from hiding the error title or workforce search', () => {
    const css = fs.readFileSync(path.join(ROOT, 'src/components/hr/HrDashboard.module.css'), 'utf8');
    expect(dashboard).toContain('styles.peopleNoticeTitle');
    expect(dashboard).toContain('styles.peopleSearchInput');
    expect(dashboard).toContain('styles.peopleHeading');
    expect(css).toContain('.peopleSurface .peopleNoticeTitle');
    expect(css).toContain('color: #881337 !important');
    expect(css).toContain('.peopleSurface .peopleSearchInput::placeholder');
    expect(css).toContain('color: #475569 !important');
    expect(css).toContain('.peopleSurface .peopleSearch:focus-within');
  });

  it('accepts only canonical workforce source payload and keeps PII out of browser state', () => {
    expect(dashboard).toContain("sourcePage?.source !== 'AUTHORISED_HR_EMPLOYEE_REGISTRY'");
    expect(dashboard).toContain("'HR_WORKFORCE_PROVENANCE_INVALID'");
    const mappingStart = dashboard.indexOf('items: sourcePage.items.map(employee => ({');
    const mappingEnd = dashboard.indexOf('total: sourcePage.total', mappingStart);
    expect(mappingStart).toBeGreaterThanOrEqual(0);
    const mapping = dashboard.slice(mappingStart, mappingEnd);
    expect(mapping).not.toContain('...employee');
    expect(mapping).not.toContain('bank');
    expect(mapping).not.toContain('salary');
    expect(mapping).not.toContain('identityNumber');
  });

  it('implements the supplied Hire-to-Exit prototype hierarchy without fictitious HR data', () => {
    expect(dashboard).toContain("useState('overview')");
    expect(dashboard).toContain("id: 'overview', title: 'Overview'");
    expect(dashboard).toContain('data-testid="people-lifecycle-overview"');
    expect(dashboard).toContain('People <em>at work.</em>');
    expect(dashboard).toContain('One governed employee chain');
    expect(dashboard).toContain('EOS reauthorizes every source decision');
    expect(dashboard).toContain('SOURCE-OWNED PEOPLE REQUESTS · MAKER ≠ CHECKER');
    expect(dashboard).toContain("isVerifiedReadState(datasetReadStates.offers)");
    expect(dashboard).toContain("isVerifiedReadState(datasetReadStates.candidates)");
    expect(dashboard).toContain("isVerifiedReadState(metric.state) ? metric.dataset.total : 'Unavailable'");
    expect(dashboard).toContain('styles.sourceUnverified');
    expect(dashboard).toContain('Decisions & next actions');
    expect(dashboard).toContain('Verified workforce & hiring');
    expect(dashboard.indexOf('Decisions & next actions')).toBeLessThan(dashboard.indexOf('Verified workforce & hiring'));
    expect(dashboard).toContain('className={styles.overviewActions}');
    expect(dashboard).toContain('const overviewHasAuthorizedSource = isVerifiedReadState(snapshotReadState)');
    expect(dashboard).toContain("['candidates', 'offers', 'jobOpenings']");
    expect(dashboard).toContain('overviewHasAuthorizedSource && <React.Fragment>');
    expect(dashboard).toContain("api.get('/hr/workforce/overview'");
    expect(dashboard).toContain("api.get('/hr/headcount-requisitions/overview'");
    expect(dashboard).toContain("source?.schema !== 'WILSY-HEADCOUNT-OVERVIEW/V1'");
    expect(dashboard).toContain("source?.source !== 'EOS_HEADCOUNT_REQUISITIONS'");
    expect(dashboard).toContain('total: source.total');
    expect(dashboard).toContain('hasMore: source.hasMore');
    expect(dashboard).toContain("item.status === 'SUBMITTED'");
    expect(dashboard).not.toContain("hrService.getJobOpenings(tenantId, params)");

    expect(dashboard).toContain("payload.schema !== 'WILSY-PEOPLE-WORKFORCE-OVERVIEW/V1'");
    expect(dashboard).not.toContain("api.get('/hr/snapshot'");
    expect(dashboard).toContain("'wilsy:people-context-search'");
    const globalChrome = fs.readFileSync(path.join(ROOT, 'src/App.jsx'), 'utf8');
    expect(globalChrome).toContain("get('section') === 'hr-workspace'");
    expect(globalChrome).toContain('Search workforce or open a People module…');
    expect(globalChrome).toContain("['Workforce', 'Hiring', 'Offers', 'Headcount']");
    expect(globalChrome).toContain("detail: { query: moduleName }");

    expect(dashboard).toContain("setActiveTab('employees')");
    expect(dashboard).toContain('People access requires an authorized operating capacity');
    expect(dashboard).toContain('Founder designation alone does not grant HR authority.');
    expect(dashboard).not.toContain('24 / 28 Planned');
    expect(dashboard).not.toContain('Onboard Naledi');
    expect(dashboard).toContain("const sourceTab = activeTab === 'overview' ? 'employees'");
    expect(dashboard).toContain("Object.prototype.hasOwnProperty.call(pageStates, activeTab) ? activeTab : null");
    expect(dashboard).toContain('const reads = sourceTab');
    expect(dashboard).toContain('if (sourceTab && sourceTab !==');
    expect(dashboard).toContain("id: 'onboarding', title: 'Onboarding'");
    expect(dashboard).toContain("id: 'exit', title: 'Exit'");
  });

  it('keeps the global logo and delegates owned People footer to Headquarters', () => {
    const hq = fs.readFileSync(path.join(ROOT, 'src/components/workspaces/WilsyHeadquartersWorkspace.jsx'), 'utf8');
    expect(hq).toContain("peopleOwnsCanvas = section === 'hr-workspace'");
    expect(hq).toContain('hq-layout--people-owned');
    expect(hq).toContain('data-workspace-ownership="PEOPLE"');
    expect(hq).toContain('aria-label="Return to Headquarters"');
    expect(hq).toContain('className="hq-global-footer"');
    expect(hq).toContain('className="hq-footer-tenant"');
    expect(hq).toContain('employerName && employerReference');
    expect(dashboard).not.toContain('wilsy-logo.svg');
  });

});

/**
 * ARTIFACT: client/src/__tests__/components/hrDashboardAuthorityBoundary.test.js
 * VERSION: v1.8.5-GLOBAL-PEOPLE-SEARCH-CONTEXT-CERT
 * AUTHORITY BOUNDARY: Regression assertions only; Python EOS owns HR authorization and truth.
 * TENANT POSTURE: Checks exact principal, tenant and session scope without fixture credentials.
 * FAIL-CLOSED POSTURE: Prevents denied, unavailable, malformed and unauthenticated reads from becoming empty success.
 * FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively.
 * END OF WILSY OS SOVEREIGN ARTIFACT
 */
