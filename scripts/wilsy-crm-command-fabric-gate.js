/* eslint-disable */
/**
 * @fileoverview WILSY OS CRM Command Fabric production gate.
 */
const fs = require('node:fs');
const path = require('node:path');
const parser = require('../client/node_modules/@babel/parser');

const ROOT = process.cwd();
const CRM_DASH = 'client/src/components/crm/CRMDashboard.jsx';
const CRM_CSS = 'client/src/components/crm/CRMDashboard.module.css';
const LEAD_JSX = 'client/src/components/crm/lead/WilsyLeadOperatingRoom.jsx';
const LEAD_CSS = 'client/src/components/crm/lead/WilsyLeadOperatingRoom.module.css';
const RAIL_JSX = 'client/src/components/crm/rail/CrmSovereignSideRail.jsx';
const RAIL_CSS = 'client/src/components/crm/rail/CrmSovereignSideRail.module.css';
const CRM_SERVICE = 'client/src/services/crmService.js';
const CRM_ROUTE = 'server/routes/crmCommandRoutes.js';
const APP = 'server/app.js';
const HARDENING = 'server/middleware/ProductionHardening.middleware.js';
const THEME_BRIDGE = 'client/src/components/crm/theme/wilsyCrmThemeEngineBridge.js';

/**
 * @function readText
 * @description Reads a repository-relative file.
 * @param {string} relativePath - Repository-relative path.
 * @returns {string} File contents.
 * @collaboration Supplies source text for CRM production gates.
 */
function readText(relativePath) {
  const absolutePath = path.join(ROOT, relativePath);
  if (!fs.existsSync(absolutePath)) {
    throw new Error(`Missing required file: ${relativePath}`);
  }

  return fs.readFileSync(absolutePath, 'utf8');
}

/**
 * @function assertCondition
 * @description Throws when a gate condition fails.
 * @param {boolean} condition - Gate condition.
 * @param {string} message - Failure message.
 * @returns {void}
 * @collaboration Stops unsafe CRM regressions before build or commit.
 */
function assertCondition(condition, message) {
  if (!condition) {
    throw new Error(message);
  }
}

/**
 * @function assertIncludes
 * @description Requires source text to include a contract string.
 * @param {string} source - Source text.
 * @param {string} needle - Required contract.
 * @param {string} label - File label.
 * @returns {void}
 * @collaboration Locks CRM backend, rail, Lead cockpit and theme bridge contracts.
 */
function assertIncludes(source, needle, label) {
  assertCondition(source.includes(needle), `${label} missing required contract: ${needle}`);
}

/**
 * @function assertNotIncludes
 * @description Blocks forbidden source text.
 * @param {string} source - Source text.
 * @param {string} needle - Forbidden contract.
 * @param {string} label - File label.
 * @returns {void}
 * @collaboration Blocks dead handlers, failed experiments, fake rows and unsafe route bypasses.
 */
function assertNotIncludes(source, needle, label) {
  assertCondition(!source.includes(needle), `${label} contains forbidden regression: ${needle}`);
}

/**
 * @function assertNoLiteralNewlineCorruption
 * @description Blocks literal backslash-n corruption before Babel parses a source file.
 * @param {string} source - Source text to inspect.
 * @param {string} label - File label for guard reporting.
 * @returns {void}
 * @collaboration Protects CRM and Lead cockpit source from malformed script writes.
 */
function assertNoLiteralNewlineCorruption(source, label) {
  const firstLine = source.split('\n')[0] || '';
  assertNotIncludes(firstLine, '\\nimport', label);
  assertNotIncludes(source.slice(0, 120), '/* eslint-disable */\\n', label);
}

/**
 * @function parseModule
 * @description Parses JavaScript or JSX source with Babel.
 * @param {string} source - Source text.
 * @param {string} label - File label.
 * @returns {void}
 * @collaboration Catches syntax failures before Vite runtime.
 */
function parseModule(source, label) {
  assertNoLiteralNewlineCorruption(source, label);

  parser.parse(source, {
    sourceType: 'module',
    plugins: [
      'jsx',
      'importMeta',
      'dynamicImport',
      'classProperties',
      'objectRestSpread',
      'optionalChaining',
      'nullishCoalescingOperator',
      'topLevelAwait'
    ]
  });

  console.log(` - Parsed ${label}`);
}

/**
 * @function assertCleanSource
 * @description Blocks known unsafe source regressions.
 * @param {string} source - Source text.
 * @param {string} label - File label.
 * @returns {void}
 * @collaboration Keeps the CRM lane clean from failed experiments and fabricated records.
 */
function assertCleanSource(source, label) {
  [
    'handleCrmCommandSearchChangeR62B',
    'handleCrmCommandSearchChangeR62F',
    'handleCrmLiveSyncR62B',
    'handleCrmLiveSyncR62F',
    'await crmService',
    'export export',
    '\\nimport React',
    'LeadEnterpriseWorkspace',
    'WILSY_R63C_ENTERPRISE_LEAD_WORKSPACE',
    'leadEnterpriseWorkspace',
    'railCollapseToggleR63A',
    'WILSY_R64A_SOVEREIGN_RAIL_COLLAPSE',
    'railSovereignToggleR64A',
    'data-wilsy-crm-rail-mode',
    'crmRailCollapsedR64A',
    'sampleLead',
    'sampleCustomer',
    'faker'
  ].forEach((needle) => assertNotIncludes(source, needle, label));
}

/**
 * @function assertRequiredContracts
 * @description Validates required source contracts.
 * @param {string} source - Source text.
 * @param {string[]} contracts - Required contracts.
 * @param {string} label - File label.
 * @returns {void}
 * @collaboration Keeps production assertions readable and valid JavaScript.
 */
function assertRequiredContracts(source, contracts, label) {
  contracts.forEach((contract) => assertIncludes(source, contract, label));
}

/**
 * @function runGate
 * @description Runs the CRM Command Fabric production gate.
 * @returns {void}
 * @collaboration Freezes CRM command fabric, R65 rail, R67D header, R67B constants and R67A theme bridge.
 */
function runGate() {
  const dash = readText(CRM_DASH);
  const css = readText(CRM_CSS);
  const leadJsx = readText(LEAD_JSX);
  const leadCss = readText(LEAD_CSS);
  const railJsx = readText(RAIL_JSX);
  const railCss = readText(RAIL_CSS);
  const service = readText(CRM_SERVICE);
  const route = readText(CRM_ROUTE);
  const app = readText(APP);
  const hardening = readText(HARDENING);
  const themeBridge = readText(THEME_BRIDGE);

  parseModule(dash, CRM_DASH);
  parseModule(leadJsx, LEAD_JSX);
  parseModule(railJsx, RAIL_JSX);
  parseModule(themeBridge, THEME_BRIDGE);

  [
    [dash, CRM_DASH],
    [css, CRM_CSS],
    [leadJsx, LEAD_JSX],
    [leadCss, LEAD_CSS],
    [railJsx, RAIL_JSX],
    [railCss, RAIL_CSS],
    [themeBridge, THEME_BRIDGE]
  ].forEach(([source, label]) => assertCleanSource(source, label));

  assertRequiredContracts(themeBridge, [
    'WILSY_CRM_THEME_ENGINE_BRIDGE_VERSION',
    'R67A-CRM-THEME-ENGINE-AUTHORITY-BRIDGE',
    'wilsyOperatingSkins',
    'FALLBACK_CRM_THEME_OPTIONS',
    'WILSY_NEBULA_COMMAND',
    'WILSY_PEARL',
    'resolveCrmThemeEngineOptions'
  ], THEME_BRIDGE);

  assertRequiredContracts(leadJsx, [
    'R67D-SOVEREIGN-HEADER-COMMAND-BRIDGE',
    'data-wilsy-lead-appbar="sovereign-header-command-bridge"',
    'data-wilsy-header-command-grid="investor-grade"',
    'data-wilsy-investor-strip="source-root-compliance"',
    'data-wilsy-header-shortcuts="production"',
    'data-wilsy-header-theme-dock="theme-engine-authority"',
    'headerPrimaryRow',
    'headerCommandGrid',
    'headerInvestorStrip',
    'headerShortcutBar',
    'headerSearch',
    'headerMoreMenu',
    'Theme Authority',
    'Source Routes',
    'Sovereign Root',
    'Compliance',
    'Command Center',
    'Wilsy AI Services',
    'const EMPTY_LEAD_DRAFT = Object.freeze',
    'const REQUIRED_LEAD_FIELDS = Object.freeze',
    'const LEAD_COLUMNS = Object.freeze',
    'const LEAD_VIEWS = Object.freeze',
    'resolveCrmThemeEngineOptions',
    'WILSY_CRM_THEME_ENGINE_BRIDGE_VERSION',
    'R66G_AUTO_TELEMETRY_HYDRATION',
    'renderEmptyActivationBoard',
    'Data Provenance Ledger',
    'No synthetic rows',
    'Backend authority only'
  ], LEAD_JSX);

  assertNotIncludes(leadJsx, '../../account/wilsyOperatingSkins.js', LEAD_JSX);
  assertNotIncludes(leadJsx, 'WILSY_LEAD_FALLBACK_THEME_OPTIONS', LEAD_JSX);
  assertNotIncludes(leadJsx, 'resolveLeadThemeEngineOptions()', LEAD_JSX);

  assertRequiredContracts(leadCss, [
    '.appHeader[data-wilsy-lead-appbar="sovereign-header-command-bridge"]',
    '.headerPrimaryRow',
    '.headerIdentity',
    '.headerThemeDock',
    '.headerCommandGrid',
    '.headerSearch',
    '.headerInvestorStrip',
    '.headerShortcutBar',
    '.headerPrimaryAction',
    '.headerMoreDock',
    '.headerMoreMenu',
    '.commandStrip',
    'display: none !important',
    '.leadOperatingRoom[data-wilsy-theme-bridge-version="R67A-CRM-THEME-ENGINE-AUTHORITY-BRIDGE"]',
    '.ledgerPanel[data-wilsy-ledger-state="empty"]',
    '.ledgerEmptyFrame',
    '.activationGrid'
  ], LEAD_CSS);

  assertRequiredContracts(css, [
    '.crmShell[data-wilsy-active-workspace="leads"] .commandSurface > header',
    'display: none !important',
    '.crmShell[data-wilsy-active-workspace="leads"] .workspaceViewport'
  ], CRM_CSS);

  assertRequiredContracts(railJsx, [
    'WILSY_CRM_RAIL_ENGINE_VERSION',
    'R65A-TRI-STATE-KINETIC-DOCKING-ENGINE',
    'EXPANDED',
    'COLLAPSED',
    'PEEKING'
  ], RAIL_JSX);

  assertRequiredContracts(railCss, [
    '.railShell[data-rail-state="COLLAPSED"]',
    '.railShell[data-rail-state="PEEKING"]',
    '.kineticToggle',
    '.hoverZone'
  ], RAIL_CSS);

  assertRequiredContracts(dash, [
    'WilsyLeadOperatingRoom',
    'WILSY_R66A_LEAD_OPERATING_ROOM',
    'data-wilsy-active-workspace={activeWorkspace}',
    "activeWorkspace === 'leads' ?",
    'R66B_LEAD_INGESTION_VALIDATION_SYNC',
    'R66B_LEAD_INGESTION_VALIDATION_SAVE',
    'createCrmCommandLead',
    'onSync={() => syncCrmCommandFabric'
  ], CRM_DASH);

  assertRequiredContracts(service, [
    'WILSY_CRM_COMMAND_FABRIC_CLIENT_VERSION',
    'searchCrmCommandFabric',
    'syncCrmCommandFabric',
    'createCrmCommandLead',
    '/api/crm/command'
  ], CRM_SERVICE);

  assertRequiredContracts(route, [
    'WILSY_CRM_COMMAND_FABRIC_VERSION',
    "router.get('/status'",
    "router.get('/search'",
    "router.post('/sync'",
    "router.post('/leads'",
    'Lead source payload required',
    'No CRM lead model is registered'
  ], CRM_ROUTE);

  assertRequiredContracts(hardening, [
    'WILSY_R62E_CRM_COMMAND_READONLY_INTEGRITY_BYPASS',
    "'/api/crm/command/status'",
    "'/api/crm/command/search'",
    "url.includes('/api/crm/command/sync')"
  ], HARDENING);

  [
    "url.includes('/api/crm/command')",
    "url.includes('/api/crm/command/leads')"
  ].forEach((needle) => assertNotIncludes(hardening, needle, HARDENING));

  ['mock', 'faker', 'sampleLead', 'sampleCustomer'].forEach((needle) => assertNotIncludes(route, needle, CRM_ROUTE));

  assertIncludes(app, "app.use('/api/crm/command', crmCommandRoutes);", APP);

  console.log('PASS: WILSY CRM COMMAND FABRIC PRODUCTION GATE');
  console.log(' - R67D sovereign header command bridge valid');
  console.log(' - Header shortcuts/search/investor strip present');
  console.log(' - R67B Lead runtime constants preserved');
  console.log(' - R67A CRM theme bridge preserved');
  console.log(' - R66G no-dead-ledger board preserved');
  console.log(' - R65A rail engine preserved');
  console.log(' - /api/crm/command mounted');
}

runGate();
/**
 * @function runR67EHeaderThemeAuthorityGate
 * @description Validates the header theme-token authority and alignment lock.
 * @returns {void}
 * @collaboration Ensures Lead cockpit skins control actual variables and header alignment cannot regress into placeholders.
 */
function runR67EHeaderThemeAuthorityGate() {
  const themeBridge = fs.readFileSync(path.join(ROOT, 'client/src/components/crm/theme/wilsyCrmThemeEngineBridge.js'), 'utf8');
  const leadCss = fs.readFileSync(path.join(ROOT, 'client/src/components/crm/lead/WilsyLeadOperatingRoom.module.css'), 'utf8');

  [
    'WILSY_CRM_THEME_PRESET_AUTHORITY_VERSION',
    'R67E-HEADER-THEME-TOKEN-AUTHORITY',
    'getCrmThemePresetCssVars',
    'const cssVars = { ...getCrmThemePresetCssVars(id, label), ...normalizeThemeTokenMap(tokenPacket) };',
    'FORENSIC',
    'QUANTUM'
  ].forEach((contract) => assertIncludes(themeBridge, contract, 'client/src/components/crm/theme/wilsyCrmThemeEngineBridge.js'));

  [
    'R67E - HEADER THEME TOKEN AUTHORITY + ALIGNMENT LOCK',
    '.headerThemeDock .skinSwitcher::before',
    'content: "THEME AUTHORITY"',
    '.headerThemeDock .skinActive',
    '.leadOperatingRoom[data-wilsy-lead-skin="WILSY_AURORA"]',
    '.leadOperatingRoom[data-wilsy-lead-skin="WILSY_NEBULA_COMMAND"]',
    '.leadOperatingRoom[data-wilsy-lead-skin="WILSY_PEARL"]',
    'grid-template-columns: minmax(420px, 0.76fr) minmax(520px, 1.24fr) !important'
  ].forEach((contract) => assertIncludes(leadCss, contract, 'client/src/components/crm/lead/WilsyLeadOperatingRoom.module.css'));

  console.log(' - R67E header theme-token authority valid');
}

runR67EHeaderThemeAuthorityGate();
/**
 * @function runR67FForensicVioletHeaderGate
 * @description Validates FORENSIC_VIOLET header token authority and typography alignment.
 * @returns {void}
 * @collaboration Keeps the attached Lead header from reverting into an unconnected placeholder.
 */
function runR67FForensicVioletHeaderGate() {
  const themeBridge = fs.readFileSync(path.join(ROOT, 'client/src/components/crm/theme/wilsyCrmThemeEngineBridge.js'), 'utf8');
  const leadCss = fs.readFileSync(path.join(ROOT, 'client/src/components/crm/lead/WilsyLeadOperatingRoom.module.css'), 'utf8');

  [
    'WILSY_CRM_FORENSIC_VIOLET_HEADER_LOCK_VERSION',
    'R67F-FORENSIC-VIOLET-HEADER-TOKEN-LOCK',
    'FORENSIC_VIOLET:',
    '--lead-header-glow',
    '--lead-header-title-glow',
    '--lead-header-subtitle',
    'orderedPresetKeys'
  ].forEach((contract) => assertIncludes(themeBridge, contract, 'client/src/components/crm/theme/wilsyCrmThemeEngineBridge.js'));

  [
    'R67F - FORENSIC VIOLET HEADER LOCK',
    '.leadOperatingRoom[data-wilsy-lead-skin="FORENSIC_VIOLET"] .appHeader',
    '.leadOperatingRoom[data-wilsy-lead-skin="FORENSIC_VIOLET"] .headerIdentity strong',
    '.leadOperatingRoom[data-wilsy-lead-skin="FORENSIC_VIOLET"] .headerIdentity em',
    '.leadOperatingRoom[data-wilsy-lead-skin="FORENSIC_VIOLET"] .headerThemeDock .skinSwitcher',
    'content: "THEME AUTHORITY"',
    'font-family: ui-monospace',
    'text-align: left !important',
    'letter-spacing: -0.105em'
  ].forEach((contract) => assertIncludes(leadCss, contract, 'client/src/components/crm/lead/WilsyLeadOperatingRoom.module.css'));

  console.log(' - R67F forensic violet header lock valid');
}

runR67FForensicVioletHeaderGate();
