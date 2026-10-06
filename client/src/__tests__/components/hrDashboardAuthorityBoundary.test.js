/**
 * WILSY OS — HR Dashboard Authority Boundary Certificate
 *
 * VERSION: v1.0.0-HR-DASHBOARD-AUTHORITY-BOUNDARY-RED
 * AUTHORITY: Wilsy OS Core Governance
 *
 * PURPOSE:
 * Prove that the HR dashboard cannot advertise or invoke HR mutations for
 * which no executable backend authority has been certified.
 *
 * This certificate intentionally begins RED against the current production
 * dashboard. It must become GREEN only by removing/fail-closing stale client
 * capabilities or by separately proving a real authoritative backend contract.
 */

import fs from 'node:fs';
import path from 'node:path';
import { describe, expect, it } from 'vitest';

const ROOT = process.cwd();

const dashboardPath = path.join(
  ROOT,
  'src/components/hr/HrDashboard.jsx',
);

const servicePath = path.join(
  ROOT,
  'src/services/hrService.js',
);

const dashboard = fs.readFileSync(dashboardPath, 'utf8');
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

describe('HR dashboard authority boundary', () => {
  it('does not call stale or unauthorized HR capabilities', () => {
    for (const symbol of forbiddenDashboardCalls) {
      expect(
        dashboard,
        `dashboard must not invoke ${symbol}`,
      ).not.toContain(symbol);
    }
  });

  it('does not solve parity by inventing unsupported hrService exports', () => {
    for (const symbol of forbiddenInventedServiceExports) {
      const declarationPattern = new RegExp(
        `\\bexport\\s+(?:(?:async\\s+)?function|const|let|var)\\s+${symbol}\\b`,
      );

      expect(
        service,
        `hrService must not manufacture ${symbol}`,
      ).not.toMatch(declarationPattern);
    }
  });

  it('preserves already-existing HR service capabilities', () => {
    for (const symbol of requiredExistingServiceExports) {
      expect(
        service,
        `existing certified HR service capability ${symbol} must remain`,
      ).toMatch(
        new RegExp(
          `export\\s+const\\s+${symbol}\\b`,
        ),
      );
    }
  });

  it('does not couple HR artifact generation to an uncertified relation write', () => {
    const artifactStart = dashboard.indexOf(
      'const generateArtifact = async',
    );

    expect(artifactStart).toBeGreaterThanOrEqual(0);

    const artifactEnd = dashboard.indexOf(
      'const generatePayslip = async',
      artifactStart,
    );

    expect(artifactEnd).toBeGreaterThan(artifactStart);

    const artifactBlock = dashboard.slice(
      artifactStart,
      artifactEnd,
    );

    expect(artifactBlock).not.toContain(
      'hrService.createEmployeeRelation',
    );
  });

  it('does not advertise executable payslip generation without backend authority', () => {
    expect(dashboard).not.toContain(
      'hrService.generatePayslip',
    );
  });
});
