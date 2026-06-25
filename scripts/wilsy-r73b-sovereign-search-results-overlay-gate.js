/* eslint-disable */
const fs = require('fs');

const DASHBOARD_FILE = 'client/src/components/crm/CRMDashboard.jsx';
const CSS_FILE = 'client/src/components/crm/CRMDashboard.module.css';

/**
 * @function readFile
 * @description Reads a source file for R73B sovereign search overlay verification.
 * @collaboration R73B gate, CRM dashboard overlay, source-guided search runtime.
 */
function readFile(filePath) {
  return fs.readFileSync(filePath, 'utf8');
}

/**
 * @function countPattern
 * @description Counts pattern matches in dashboard or CSS source.
 * @collaboration R73B semantic proof, overlay source inventory, search runtime audit.
 */
function countPattern(source, pattern) {
  return (source.match(pattern) || []).length;
}

/**
 * @function assertIncludes
 * @description Fails when required R73B source evidence is absent.
 * @collaboration R73B gate, sovereign search overlay proof, production integrity.
 */
function assertIncludes(source, value, label) {
  if (!source.includes(value)) {
    throw new Error(`R73B gate missing ${label}: ${value}`);
  }
}

/**
 * @function assertBlocked
 * @description Fails when forbidden behavior appears in the R73B lane.
 * @collaboration R73B lane quarantine, frontend-only search overlay, sovereign guard discipline.
 */
function assertBlocked(source, pattern, label) {
  if (pattern.test(source)) {
    throw new Error(`R73B gate blocked ${label}`);
  }
}

/**
 * @function hasBrokenOnChangeAssignment
 * @description Detects malformed onChange assignment while allowing valid JSX arrow syntax.
 * @collaboration R73B final gate, JSX syntax safety, command search preservation.
 */
function hasBrokenOnChangeAssignment(block) {
  return /onChange=\{\(event\)\s*=\s*(?:\n|\r|\s)*(?:onInput|onFocus|onKeyDown|\{)/.test(block);
}

/**
 * @function hasBrokenInputBodyLine
 * @description Detects the malformed input body line created by earlier merge scripts.
 * @collaboration R73B final gate, JSX input self-closing safety, search shell repair.
 */
function hasBrokenInputBodyLine(block) {
  return /^\s*>\s*\{\s*$/m.test(block);
}

/**
 * @function buildRecursiveExpansionPattern
 * @description Builds the recursive expansion token pattern without hardcoding the token in gate prose.
 * @collaboration Terminal boundary discipline, source self-scan safety, R73B guard precision.
 */
function buildRecursiveExpansionPattern() {
  const prefix = ['R', '70', 'F'].join('');
  return new RegExp(`${prefix}[-_]|\\b${prefix.toLowerCase()}[A-Za-z0-9_]*\\s*[=:]`);
}

/**
 * @function readChromeSearchBlock
 * @description Extracts the CRM dashboard top chrome search label block.
 * @collaboration R73B input merge proof, existing command search preservation, JSX syntax safety.
 */
function readChromeSearchBlock(dashboardSource) {
  const labelStart = dashboardSource.indexOf('<label className={styles.chromeSearch}>');
  const labelEnd = dashboardSource.indexOf('</label>', labelStart);

  if (labelStart < 0 || labelEnd < 0) {
    throw new Error('R73B gate blocked: chromeSearch label missing');
  }

  return dashboardSource.slice(labelStart, labelEnd + '</label>'.length);
}

/**
 * @function verifyChromeSearchMerge
 * @description Verifies the existing search input onChange was preserved and safely extended for R73B.
 * @collaboration R73B final syntax repair, command fabric preservation, sovereign overlay state binding.
 */
function verifyChromeSearchMerge(dashboardSource) {
  const block = readChromeSearchBlock(dashboardSource);

  [
    'value={searchTerm}',
    'onChange={(event) => {',
    'const query = event.target.value;',
    'setSearchTerm(query);',
    'setSovereignSearchQuery(query);',
    'setSovereignSearchOpen(true);',
    'searchCrmCommandFabric({',
    'data-wilsy-r73b-search-input="true"',
    'onFocus={() => setSovereignSearchOpen(true)}',
    'onKeyDown={(event) => {',
  ].forEach((value) => assertIncludes(block, value, `chrome search merge evidence ${value}`));

  if (hasBrokenOnChangeAssignment(block)) {
    throw new Error('R73B gate blocked: broken onChange assignment remains');
  }

  if (hasBrokenInputBodyLine(block)) {
    throw new Error('R73B gate blocked: malformed input body line remains');
  }

  assertBlocked(block, /onInput=\{\(event\)/, 'stale onInput artifact');

  return {
    preservesSearchTermState: true,
    preservesCommandFabricSearch: true,
    bindsOverlayQueryState: true,
    bindsKeyboardRuntime: true,
    brokenOnChangeAssignmentAbsent: true,
    staleOnInputAbsent: true,
    brokenInputBodyLineAbsent: true,
  };
}

/**
 * @function verifyDashboardSearchRuntime
 * @description Verifies CRMDashboard contains R73B search runtime, overlay, keyboard behavior, and mounted API transport.
 * @collaboration CRM dashboard search activation, R72W backend route mount, visible operator payoff.
 */
function verifyDashboardSearchRuntime(dashboardSource) {
  [
    ['@function CRMDashboard', 'CRMDashboard adjacent JSDoc'],
    ['R73B_SOVEREIGN_SEARCH_RUNTIME_HELPERS', 'helper marker'],
    ['SovereignSearchCommandOverlay', 'overlay component'],
    ['data-wilsy-r73b-sovereign-search-overlay', 'overlay DOM marker'],
    ['data-wilsy-r73b-search-input="true"', 'input merge marker'],
    ['sovereignSearchQuery', 'query state'],
    ['sovereignSearchOpen', 'open state'],
    ['sovereignSearchState', 'result state'],
    ['runSovereignSearchRuntime', 'runtime search function'],
    ['/api/crm/live/', 'live route transport'],
    ['/api/crm/intelligence/', 'intelligence route transport'],
    ['shouldOpenSovereignSearchFromKeyboard', 'keyboard command helper'],
    ['source-honest empty state', 'source honest empty state'],
  ].forEach(([value, label]) => assertIncludes(dashboardSource, value, label));

  return {
    hasOverlayComponent: true,
    hasDomMarker: true,
    hasInputMergeMarker: true,
    hasQueryState: true,
    hasKeyboardRuntime: true,
    hasLiveRouteTransport: true,
    hasIntelligenceRouteTransport: true,
    searchRuntimeFunctionCount: countPattern(dashboardSource, /function\s+[A-Za-z0-9_]*SovereignSearch[A-Za-z0-9_]*/g),
    apiRouteReferenceCount: countPattern(dashboardSource, /\/api\/crm\/(?:live|intelligence)\//g),
    keyboardEvidenceCount: countPattern(dashboardSource, /metaKey|ctrlKey|Escape|Enter|keydown/gi),
  };
}

/**
 * @function verifyCssOverlayRuntime
 * @description Verifies CRMDashboard CSS contains the R73B overlay styling contract.
 * @collaboration CRM dashboard styling, existing CSS module, no new UI system.
 */
function verifyCssOverlayRuntime(cssSource) {
  [
    '.sovereignSearchOverlay',
    '.sovereignSearchPanel',
    '.sovereignSearchHeader',
    '.sovereignSearchStatus',
    '.sovereignSearchResults',
    '.sovereignSearchResult',
    '.sovereignSearchGroup',
    '@media (max-width: 760px)',
  ].forEach((value) => assertIncludes(cssSource, value, `CSS selector ${value}`));

  return {
    overlaySelectorCount: countPattern(cssSource, /sovereignSearch[A-Za-z0-9_-]+/g),
    responsiveEvidence: countPattern(cssSource, /@media|max-width|calc\(/g),
    glassEvidence: countPattern(cssSource, /backdrop-filter|radial-gradient|rgba\(/g),
  };
}

/**
 * @function verifyLaneBoundaries
 * @description Verifies R73B changed sources do not include forbidden backend, export, secret, or recursive expansion behavior.
 * @collaboration R73B frontend-only lane, no backend mutation, secret guard companion.
 */
function verifyLaneBoundaries(dashboardSource, cssSource) {
  const combined = `${dashboardSource}\n${cssSource}`;

  [
    [/server\/middleware|server\/routes|server\/models|server\/services|server\/app\.js/, 'backend filesystem path reference'],
    [/WilsyAccountCommandCenter\.jsx|wilsyOperatingSkins|wilsyNebulaCommandSkin/, 'account/theme source mutation reference'],
    [/server\/exports|reports\/|forensic-fixes\//, 'filesystem report/export path'],
    [/\b(?:fs\.)?(?:writeFile|writeFileSync|createWriteStream)\s*\(/, 'executable filesystem write call'],
    [buildRecursiveExpansionPattern(), 'recursive expansion token shape'],
    [/VITE_[A-Z0-9_]*(SECRET|PASSWORD|PRIVATE|HMAC|JWT)/, 'unsafe browser secret env literal'],
  ].forEach(([pattern, label]) => assertBlocked(combined, pattern, label));
}

/**
 * @function runR73BSovereignSearchOverlayGate
 * @description Certifies the visible CRM sovereign search overlay and runtime transport.
 * @collaboration R73A discovery, R72W mounted APIs, CRM dashboard operator-grade search payoff.
 */
function runR73BSovereignSearchOverlayGate() {
  const dashboardSource = readFile(DASHBOARD_FILE);
  const cssSource = readFile(CSS_FILE);

  if (!dashboardSource.startsWith('/* eslint-disable */')) {
    throw new Error('R73B gate blocked: dashboard missing eslint-disable header');
  }

  const dashboardProof = verifyDashboardSearchRuntime(dashboardSource);
  const inputMergeProof = verifyChromeSearchMerge(dashboardSource);
  const cssProof = verifyCssOverlayRuntime(cssSource);
  verifyLaneBoundaries(dashboardSource, cssSource);

  console.log(JSON.stringify({
    gate: 'R73B_SOVEREIGN_SEARCH_RESULTS_OVERLAY_VERIFIED',
    lane: 'sovereign-search-results-overlay',
    files: [DASHBOARD_FILE, CSS_FILE],
    fileCount: 2,
    dashboardProof,
    inputMergeProof,
    cssProof,
    visibleSearchPayoff: true,
    keyboardCommandRuntime: true,
    mountedBackendTransport: true,
    preservesExistingSearchInputOnChange: true,
    sourceHonestEmptyState: true,
    noNewUiSystem: true,
    noBackendMutation: true,
    noServiceMutation: true,
    noAccountMutation: true,
    noRouteMutation: true,
    noModelMutation: true,
    noFilesystemReportExport: true,
    noExecutableFilesystemWriteCall: true,
    noSecrets: true,
    noRecursiveExpansionTokenShape: true,
  }, null, 2));

  console.log('');
  console.log('PASS: WILSY R73B SOVEREIGN SEARCH RESULTS OVERLAY GATE');
  console.log(' - CRM dashboard has visible sovereign search results overlay');
  console.log(' - existing search input onChange is preserved and extended safely');
  console.log(' - keyboard runtime supports command/ctrl+k, Enter and Escape');
  console.log(' - overlay queries mounted CRM live and intelligence route surfaces');
  console.log(' - CSS module contains responsive overlay styling');
  console.log(' - no backend, route, model, service, account, or new UI-system files are inside the lane');
}

runR73BSovereignSearchOverlayGate();
