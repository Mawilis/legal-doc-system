/* eslint-disable */
/**
 * WILSY OS — SOURCE REGISTRY DOCTOR
 * VERSION: 1.1.0-SOVEREIGN-FILE-GUARDED
 * ABSOLUTE PATH: /Users/wilsonkhanyezi/legal-doc-system/server/scripts/sourceRegistryDoctor.js
 *
 * Purpose:
 * - Diagnose Source Registry connectors before evidence verification.
 * - Sort ERROR before MISSING before PENDING.
 * - Inspect module existence, module import health, required methods, env vars and evidence-file paths.
 * - Never mark any source VERIFIED.
 * - Never fabricate evidence.
 */

import fs from 'fs';
import path from 'path';
import crypto from 'crypto';
import { fileURLToPath, pathToFileURL } from 'url';
import dotenv from 'dotenv';

dotenv.config();

export const SOURCE_REGISTRY_DOCTOR_VERSION = '1.1.0-SOVEREIGN-FILE-GUARDED';
export const TRUTH_POLICY = 'NO_FAKE_VERIFIED';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);
const SERVER_ROOT = path.resolve(__dirname, '..');

export const SOURCE_REGISTRY_CONNECTOR_BLUEPRINTS = Object.freeze([
  {
    key: 'FINANCE',
    label: 'Finance Ledger',
    moduleRelativePath: 'services/sourceConnectors/financeSourceConnector.js',
    requiredMethods: [
      'getRevenueYTD',
      'getAnnualRecurringRevenue',
      'getRunwayMonths',
      'getContractValueLedger',
    ],
    env: [
      'WILSY_FINANCE_EVIDENCE_FILE',
      'WILSY_FINANCE_API_URL',
      'WILSY_QUICKBOOKS_ACCESS_TOKEN',
      'WILSY_XERO_ACCESS_TOKEN',
      'WILSY_STRIPE_SECRET_KEY',
    ],
    evidenceFiles: ['WILSY_FINANCE_EVIDENCE_FILE'],
  },
  {
    key: 'HR',
    label: 'People / HRIS Registry',
    moduleRelativePath: 'services/sourceConnectors/hrSourceConnector.js',
    requiredMethods: ['getEmployeeProfile', 'getIPAssignment', 'getAuthorityRecord'],
    env: [
      'WILSY_HR_EVIDENCE_FILE',
      'WILSY_HR_API_URL',
      'WILSY_BAMBOOHR_API_KEY',
      'WILSY_PERSONIO_API_TOKEN',
      'WILSY_MICROSOFT_GRAPH_TOKEN',
    ],
    evidenceFiles: ['WILSY_HR_EVIDENCE_FILE'],
  },
  {
    key: 'COMPLIANCE',
    label: 'Compliance Registry',
    moduleRelativePath: 'services/sourceConnectors/complianceSourceConnector.js',
    requiredMethods: [
      'getPOPIAStatus',
      'getGDPRStatus',
      'getSOC2Status',
      'getJurisdictionControls',
    ],
    env: ['WILSY_COMPLIANCE_EVIDENCE_FILE', 'WILSY_COMPLIANCE_API_URL'],
    evidenceFiles: ['WILSY_COMPLIANCE_EVIDENCE_FILE'],
  },
  {
    key: 'TELEMETRY',
    label: 'Telemetry / Reliability Evidence',
    moduleRelativePath: 'services/sourceConnectors/telemetrySourceConnector.js',
    requiredMethods: ['getUptime', 'getIncidentLog', 'getChangeControlLog'],
    env: [
      'WILSY_TELEMETRY_EVIDENCE_FILE',
      'WILSY_TELEMETRY_API_URL',
      'WILSY_PROMETHEUS_BASE_URL',
      'WILSY_DATADOG_API_KEY',
      'WILSY_PAGERDUTY_TOKEN',
      'WILSY_SENTRY_TOKEN',
      'WILSY_GITHUB_TOKEN',
      'WILSY_GITLAB_TOKEN',
    ],
    evidenceFiles: ['WILSY_TELEMETRY_EVIDENCE_FILE'],
  },
  {
    key: 'CRM',
    label: 'CRM / Contract Ledger',
    moduleRelativePath: 'services/sourceConnectors/crmSourceConnector.js',
    requiredMethods: ['getTenantProfile', 'getContractLedger', 'getCounterpartyAuthority'],
    env: [
      'WILSY_CRM_EVIDENCE_FILE',
      'WILSY_CRM_API_URL',
      'WILSY_HUBSPOT_ACCESS_TOKEN',
      'WILSY_ZENDESK_API_TOKEN',
    ],
    evidenceFiles: ['WILSY_CRM_EVIDENCE_FILE'],
  },
]);

function sha3(value) {
  return crypto
    .createHash('sha3-512')
    .update(String(value || ''))
    .digest('hex');
}

function maskSecret(value = '') {
  const raw = String(value || '');

  if (!raw) return '';
  if (raw.length <= 8) return '********';

  return `${raw.slice(0, 4)}…${raw.slice(-4)}`;
}

function resolveEvidencePath(value = '') {
  const raw = String(value || '').trim();

  if (!raw) return '';

  return path.isAbsolute(raw) ? raw : path.resolve(SERVER_ROOT, raw);
}

function createBaseConnectorResult(blueprint) {
  return {
    key: blueprint.key,
    label: blueprint.label,
    status: 'PENDING',
    severity: 'LOW',
    moduleRelativePath: blueprint.moduleRelativePath,
    moduleAbsolutePath: path.join(SERVER_ROOT, blueprint.moduleRelativePath),
    moduleExists: false,
    moduleImports: false,
    requiredMethods: [],
    env: [],
    evidenceFiles: [],
    errors: [],
    repairActions: [],
    fakeVerified: false,
    truthPolicy: TRUTH_POLICY,
  };
}

function resolveExportedConnector(moduleNamespace) {
  return moduleNamespace?.default || moduleNamespace;
}

export async function inspectSourceRegistryConnector(blueprint) {
  const result = createBaseConnectorResult(blueprint);
  result.moduleExists = fs.existsSync(result.moduleAbsolutePath);

  if (!result.moduleExists) {
    result.status = 'ERROR';
    result.severity = 'HIGH';
    result.errors.push(`Connector module missing: ${result.moduleRelativePath}`);
    result.repairActions.push(`Create or restore ${result.moduleRelativePath}.`);
    return result;
  }

  try {
    const connectorUrl = pathToFileURL(result.moduleAbsolutePath).href;
    const moduleNamespace = await import(`${connectorUrl}?doctor=${Date.now()}`);
    const connector = resolveExportedConnector(moduleNamespace);

    result.moduleImports = true;

    blueprint.requiredMethods.forEach((method) => {
      const installed = typeof connector?.[method] === 'function';

      result.requiredMethods.push({
        method,
        installed,
        status: installed ? 'READY_TO_CALL' : 'ERROR',
      });

      if (!installed) {
        result.status = 'ERROR';
        result.severity = 'HIGH';
        result.errors.push(`Missing required method: ${method}`);
        result.repairActions.push(`Implement ${method} in ${result.moduleRelativePath}.`);
      }
    });
  } catch (error) {
    result.status = 'ERROR';
    result.severity = 'HIGH';
    result.errors.push(`Connector import failed: ${error.message}`);
    result.repairActions.push(`Fix module import/runtime error in ${result.moduleRelativePath}.`);
  }

  blueprint.env.forEach((name) => {
    const value = process.env[name] || '';

    result.env.push({
      name,
      present: Boolean(value),
      maskedValue: value ? maskSecret(value) : '',
      status: value ? 'PRESENT' : 'MISSING',
    });
  });

  blueprint.evidenceFiles.forEach((name) => {
    const rawPath = process.env[name] || '';
    const resolvedPath = resolveEvidencePath(rawPath);
    const exists = Boolean(resolvedPath && fs.existsSync(resolvedPath));

    result.evidenceFiles.push({
      env: name,
      configured: Boolean(rawPath),
      path: rawPath,
      resolvedPath,
      exists,
      status: exists ? 'PRESENT' : rawPath ? 'MISSING_FILE' : 'NOT_CONFIGURED',
    });

    if (rawPath && !exists) {
      result.status = result.status === 'ERROR' ? 'ERROR' : 'MISSING';
      result.severity = result.severity === 'HIGH' ? 'HIGH' : 'MEDIUM';
      result.repairActions.push(`Create evidence file configured by ${name}: ${resolvedPath}`);
    }
  });

  const anyEnv = result.env.some((item) => item.present);
  const anyEvidenceFile = result.evidenceFiles.some((item) => item.exists);

  if (result.status !== 'ERROR') {
    if (!anyEnv && !anyEvidenceFile) {
      result.status = 'MISSING';
      result.severity = 'MEDIUM';
      result.repairActions.push(
        `Configure at least one real ${result.label} evidence source or API credential.`
      );
    } else {
      result.status = 'PENDING';
      result.severity = 'LOW';
      result.repairActions.push(
        'Run /api/source-registry/verify with a signed artifact payload to evaluate live evidence.'
      );
    }
  }

  return result;
}

function summarizeDoctorResults(results = []) {
  return results.reduce(
    (summary, item) => {
      summary.total += 1;
      summary[item.status.toLowerCase()] = (summary[item.status.toLowerCase()] || 0) + 1;
      return summary;
    },
    {
      total: 0,
      error: 0,
      missing: 0,
      pending: 0,
      verified: 0,
      blocked: 0,
    }
  );
}

function sortDoctorResults(results = []) {
  const rank = {
    ERROR: 0,
    MISSING: 1,
    BLOCKED: 2,
    PENDING: 3,
    VERIFIED: 4,
  };

  return results.slice().sort((a, b) => (rank[a.status] ?? 99) - (rank[b.status] ?? 99));
}

export function buildSourceRegistryEnvTemplate(results = []) {
  const lines = [
    '# ======================================================',
    '# WILSY OS — SOURCE REGISTRY EVIDENCE CONFIG TEMPLATE',
    '# Generated by server/scripts/sourceRegistryDoctor.js',
    '# Fill real values only. Do not use fake evidence.',
    '# ======================================================',
  ];

  results.forEach((connector) => {
    lines.push('');
    lines.push(`# ${connector.label}`);

    connector.env.forEach((env) => {
      lines.push(`${env.name}=`);
    });
  });

  return Array.from(new Set(lines)).join('\n');
}

export async function buildSourceRegistryDoctorReport() {
  const connectors = [];

  for (const blueprint of SOURCE_REGISTRY_CONNECTOR_BLUEPRINTS) {
    connectors.push(await inspectSourceRegistryConnector(blueprint));
  }

  const orderedConnectors = sortDoctorResults(connectors);
  const summary = summarizeDoctorResults(orderedConnectors);

  const report = {
    success: true,
    service: 'source-registry-doctor',
    version: SOURCE_REGISTRY_DOCTOR_VERSION,
    status: summary.error
      ? 'ERROR'
      : summary.missing
        ? 'MISSING'
        : summary.pending
          ? 'PENDING'
          : 'READY',
    summary,
    connectors: orderedConnectors,
    envTemplate: buildSourceRegistryEnvTemplate(orderedConnectors),
    truthPolicy: TRUTH_POLICY,
    generatedAt: new Date().toISOString(),
  };

  report.reportHash = sha3(
    JSON.stringify({
      version: report.version,
      status: report.status,
      summary: report.summary,
      connectors: report.connectors,
      truthPolicy: report.truthPolicy,
      generatedAt: report.generatedAt,
    })
  );

  return report;
}

export function printSourceRegistryDoctorReport(report) {
  console.log('\n======================================================');
  console.log('WILSY OS — SOURCE REGISTRY DOCTOR REPORT');
  console.log('======================================================');
  console.log(`Version: ${report.version}`);
  console.log(`Status: ${report.status}`);
  console.log(`Connectors: ${report.summary.total}`);
  console.log(`Errors: ${report.summary.error}`);
  console.log(`Missing: ${report.summary.missing}`);
  console.log(`Pending: ${report.summary.pending}`);
  console.log(`Truth Policy: ${report.truthPolicy}`);
  console.log(`Report Hash: ${report.reportHash}`);
  console.log('======================================================\n');

  report.connectors.forEach((connector) => {
    console.log(`[${connector.status}] ${connector.label}`);
    console.log(`  Module: ${connector.moduleRelativePath}`);
    console.log(`  Module exists: ${connector.moduleExists ? 'YES' : 'NO'}`);
    console.log(`  Module imports: ${connector.moduleImports ? 'YES' : 'NO'}`);

    connector.requiredMethods.forEach((method) => {
      console.log(`  Method: ${method.method} => ${method.status}`);
    });

    connector.errors.forEach((error) => console.log(`  ERROR: ${error}`));
    connector.repairActions.forEach((action) => console.log(`  ACTION: ${action}`));
    console.log('');
  });
}

async function main() {
  const report = await buildSourceRegistryDoctorReport();

  if (process.argv.includes('--json')) {
    console.log(JSON.stringify(report, null, 2));
    return;
  }

  if (process.argv.includes('--env-template')) {
    console.log(report.envTemplate);
    return;
  }

  printSourceRegistryDoctorReport(report);
}

if (import.meta.url === pathToFileURL(process.argv[1] || '').href) {
  main().catch((error) => {
    console.error(
      JSON.stringify(
        {
          success: false,
          service: 'source-registry-doctor',
          status: 'ERROR',
          error: error.message,
          stack: error.stack,
          truthPolicy: TRUTH_POLICY,
        },
        null,
        2
      )
    );
    process.exit(1);
  });
}
