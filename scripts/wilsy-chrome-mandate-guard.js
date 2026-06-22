/* eslint-disable */
/**
 * @fileoverview Wilsy OS Chrome Mandate Guard.
 * @description Protects Wilsy OS cockpit files from broken chrome, hardcoded fake data, observer storms, blind skin selectors, unbound account-route placeholders, and monolithic Account component regressions.
 * @collaboration This guard is the executable production contract for Wilsy OS Chrome discipline.
 */

const fs = require('fs');
const path = require('path');

/**
 * @function readFileSafely
 * @description Reads a source file from disk and throws when the file is missing.
 * @param {string} targetPath - Absolute path to read.
 * @returns {string} Source content.
 * @collaboration Keeps Wilsy OS guard checks deterministic and explicit.
 */
function readFileSafely(targetPath) {
  if (!fs.existsSync(targetPath)) {
    throw new Error(`WILSY_CHROME_GUARD_FILE_NOT_FOUND: ${targetPath}`);
  }

  return fs.readFileSync(targetPath, 'utf8');
}

/**
 * @function assertContains
 * @description Requires a mandatory source marker.
 * @param {string} source - Source content.
 * @param {string} marker - Required marker.
 * @param {string} label - Guard label.
 * @returns {void}
 * @collaboration Documents Wilsy OS Chrome requirements in executable form.
 */
function assertContains(source, marker, label) {
  if (!source.includes(marker)) {
    throw new Error(`WILSY_CHROME_MANDATE_MISSING_${label}: ${marker}`);
  }
}

/**
 * @function assertAnyContains
 * @description Requires at least one acceptable source marker from an evolving Wilsy OS contract.
 * @param {string} source - Source content.
 * @param {string[]} markers - Acceptable markers.
 * @param {string} label - Guard label.
 * @returns {void}
 * @collaboration Lets the Chrome mandate evolve across successor patches without rejecting valid newer implementations.
 */
function assertAnyContains(source, markers, label) {
  const found = markers.some(marker => source.includes(marker));

  if (!found) {
    throw new Error(`WILSY_CHROME_MANDATE_MISSING_${label}: ${markers.join(' OR ')}`);
  }
}

/**
 * @function assertNotContains
 * @description Rejects forbidden source markers.
 * @param {string} source - Source content.
 * @param {string} marker - Forbidden marker.
 * @param {string} label - Guard label.
 * @returns {void}
 * @collaboration Stops fake data, observer storms, and visual regressions from shipping.
 */
function assertNotContains(source, marker, label) {
  if (source.includes(marker)) {
    throw new Error(`WILSY_CHROME_MANDATE_FORBIDDEN_${label}: ${marker}`);
  }
}

/**
 * @function readAccountChromeBundleSource
 * @description Reads Account Command Center plus extracted runtime and CSS companion files.
 * @param {string} accountPath - Absolute Account component path.
 * @returns {string} Combined source bundle.
 * @collaboration Allows Wilsy OS to reduce the Account component line count while preserving one guard contract across the full chrome bundle.
 */
function readAccountChromeBundleSource(accountPath) {
  const accountSource = readFileSafely(accountPath);
  const accountDir = path.dirname(accountPath);
  const companions = [
    'wilsyAccountRuntimeEnhancers.js',
    'wilsyAccountChromeRuntimeCss.js'
  ];

  const companionSource = companions
    .map(fileName => {
      const companionPath = path.join(accountDir, fileName);
      return fs.existsSync(companionPath) ? readFileSafely(companionPath) : '';
    })
    .join('\n');

  return `${accountSource}\n${companionSource}`;
}

/**
 * @function assertAccountChromeMandate
 * @description Validates Account Command Center against the current Wilsy OS Chrome mandate.
 * @param {string
  const wilsyR8FChromeGuardBundle =
    typeof bundledSource !== 'undefined' ? bundledSource :
    typeof source !== 'undefined' ? source :
    '';

  assertAnyContains(wilsyR8FChromeGuardBundle, [
    'WILSY_R8F_COMMAND_ROUTES_SOURCE_BOUND',
    'bootWilsyR8FSourceBoundCommandRoutesRuntime',
    'stampWilsyR8FSourceBoundCommandRoutes',
    'data-wilsy-r8f-command-routes-source-bound',
    'data-wilsy-r8f-command-route-card',
    'WILSY_R8F_COMMAND_ROUTES_SOURCE_BOUND_CSS'
  ], 'R8F_COMMAND_ROUTES_SOURCE_BOUND');


  const wilsyR8GChromeGuardBundle =
    typeof bundledSource !== 'undefined' ? bundledSource :
    typeof source !== 'undefined' ? source :
    '';

  assertAnyContains(wilsyR8GChromeGuardBundle, [
    'WILSY_R8G_COMMAND_ROUTES_DOM_PROOF',
    'bootWilsyR8GCommandRoutesDomProofRuntime',
    'replaceWilsyR8GCommandRoutesDeck',
    'data-wilsy-r8g-command-route-deck',
    'data-wilsy-r8g-command-route-card',
    'WILSY_R8G_COMMAND_ROUTES_DOM_PROOF_CSS'
  ], 'R8G_COMMAND_ROUTES_DOM_PROOF');

} accountSource - Account Command Center source content.
 * @param {string} bundledSource - Account source plus extracted companion modules.
 * @returns {void}
 * @collaboration Protects viewport discipline, performance, theme preview visibility, source-truth-only account management, and safe extraction boundaries.
 */
function assertAccountChromeMandate(accountSource, bundledSource) {
  assertContains(accountSource, '/* eslint-disable */', 'ESLINT_FILE_HEADER');

  assertAnyContains(accountSource, [
    'data-wilsy-account-command-center="true"',
    'WilsyAccountCommandCenter'
  ], 'ACCOUNT_COMMAND_CENTER_ROOT');

  assertAnyContains(accountSource, [
    'WILSY_R8A_ACCOUNT_EXTRACTION_BOUNDARY',
    "import './wilsyAccountRuntimeEnhancers'",
    'buildWilsyAccountExtractedChromeCss'
  ], 'R8A_ACCOUNT_EXTRACTION_BOUNDARY');

  assertAnyContains(bundledSource, [
    'WILSY_R8A_ACCOUNT_RUNTIME_ENHANCERS',
    'bootWilsyAccountRuntimeEnhancers'
  ], 'R8A_RUNTIME_EXTRACTION');

  
  assertAnyContains(bundledSource, [
    'WILSY_R8D_COMMAND_IDENTITY_LABEL_AUTHORITY',
    'bootWilsyR8DCommandIdentityLabelRuntime',
    'stampWilsyR8DCommandIdentityLabel',
    'data-wilsy-r8d-command-identity-label',
    'data-wilsy-r8d-tenant-verified-label',
    'data-wilsy-r8d-command-identity-header-row',
    'text-overflow: clip'
  ], 'R8D_COMMAND_IDENTITY_LABEL_AUTHORITY');

  assertAnyContains(bundledSource, [
    'WILSY_R8A_ACCOUNT_CHROME_RUNTIME_CSS',
    'buildWilsyAccountExtractedChromeCss'
  ], 'R8A_CSS_EXTRACTION');

  
  assertAnyContains(bundledSource, [
    'WILSY_R8C_THEME_VIEWPORT_SWITCHBOARD',
    'bootWilsyR8CThemeViewportRuntime',
    'stampWilsyR8CThemeViewport',
    'data-wilsy-r8c-theme-viewport-switchboard',
    'data-wilsy-r8c-theme-scroll-grid',
    'data-wilsy-r8c-theme-sticky-header',
    'scroll-behavior: smooth',
    'content-visibility: auto'
  ], 'R8C_THEME_VIEWPORT_SWITCHBOARD');

  assertAnyContains(bundledSource, [
    'WILSY_R7L_THEME_PALETTE_PREVIEW_SWITCHBOARD',
    'data-wilsy-r7l-palette-preview',
    '--wilsy-r7l-skin-gradient',
    'resolveWilsyR7LSkinPalette'
  ], 'VISIBLE_SKIN_PALETTE_PREVIEW');

  assertAnyContains(bundledSource, [
    'WILSY_R7O_NO_HARDCODE_PROFILE_INTELLIGENCE',
    'bootWilsyR7ONoHardcodeAccountHubRuntime',
    'deriveWilsyR7OProfileFieldContract',
    'removeWilsyR7NHardcodedRouteNodes',
    'data-wilsy-r7o-profile-card',
    'data-wilsy-r7o-route-unbound',
    'NO FAKE DATA • NO HARDCODED USER VALUES'
  ], 'NO_HARDCODE_MY_ACCOUNT_HUB');
  assertAnyContains(bundledSource, [
    'WILSY_R7P_COMMAND_ROUTES_NO_PLACEHOLDER_CONTRACTS',
    'bootWilsyR7PCommandRoutesRuntime',
    'deriveWilsyR7PRouteContract',
    'data-wilsy-r7p-route-unbound',
    'data-wilsy-r7p-route-pending-card',
    'Route contracts pending',
    'NO PLACEHOLDERS',
    'WILSY_R7O_NO_HARDCODE_PROFILE_INTELLIGENCE',
    'suppressWilsyR7OUnboundRoutes',
    'data-wilsy-r7o-route-unbound',
    'data-wilsy-r7o-route-section',
    'No fake account routes'
  ], 'COMMAND_ROUTES_NO_PLACEHOLDER_CONTRACTS');

  assertAnyContains(bundledSource, [
    'WILSY_R7Q_OPERATING_IDENTITY_UNIFORM_MATRIX',
    'bootWilsyR7QOperatingIdentityMatrixRuntime',
    'deriveWilsyR7QIdentityFacts',
    'data-wilsy-r7q-operating-identity-matrix',
    'data-wilsy-r7q-identity-grid',
    'data-wilsy-r7q-identity-card',
    'Source-bound command posture',
    'WILSY_R7F_IDENTITY_HIERARCHY_EVIDENCE',
    'deriveWilsyR7FIdentitySeal',
    'FORENSIC COMMAND INTELLIGENCE',
    'Command authority and operating posture',
    'Root Tenant Control',
    'Sovereign Command'
  ], 'OPERATING_IDENTITY_STABLE_CONTRACT');


  assertAnyContains(bundledSource, [
    'transition: all 0.25s ease-in-out',
    'translate3d(0, -2px, 0)',
    'transform: translate3d'
  ], 'MOTION_DISCIPLINE');

  assertNotContains(bundledSource, 'observer.observe(document.documentElement', 'DOCUMENT_LEVEL_OBSERVER_STORM');
  assertNotContains(bundledSource, 'TODAY, 09:42 UTC', 'HARDCODED_FAKE_TIME');
  assertNotContains(bundledSource, 'LAST ACTIVE  ●  TODAY', 'HARDCODED_LAST_ACTIVE');
  assertNotContains(bundledSource, 'controls the tenant command layer.', 'DUPLICATE_NAME_STORY');

  assertNotContains(bundledSource, 'Profile Command', 'HARDCODED_PROFILE_ROUTE');
  assertNotContains(bundledSource, 'People Graph', 'HARDCODED_PEOPLE_ROUTE');
  assertNotContains(bundledSource, 'Security Posture', 'HARDCODED_SECURITY_ROUTE');
  assertNotContains(bundledSource, 'Biometric Proof', 'HARDCODED_BIOMETRIC_ROUTE');
  assertNotContains(bundledSource, 'Device Sessions', 'HARDCODED_DEVICE_ROUTE');
  assertNotContains(bundledSource, 'Access Vault', 'HARDCODED_ACCESS_ROUTE');
}

/**
 * @function assertBasicChromeMandate
 * @description Validates baseline Wilsy OS source requirements for non-Account files.
 * @param {string} source - Source content.
 * @param {string} target - File target label.
 * @returns {void}
 * @collaboration Keeps the guard reusable while Account carries the deep chrome mandate.
 */
function assertBasicChromeMandate(source, target) {
  assertContains(source, '/* eslint-disable */', `ESLINT_FILE_HEADER_${path.basename(target)}`);
}

/**
 * @function runChromeMandateGuard
 * @description Runs Wilsy OS Chrome mandate checks against provided targets.
 * @returns {void}
 * @collaboration Provides a repeatable production gate for Wilsy OS Chrome quality.
 */
function runChromeMandateGuard() {
  const targets = process.argv.slice(2);
  const resolvedTargets = targets.length > 0
    ? targets
    : ['client/src/components/account/WilsyAccountCommandCenter.jsx'];

  resolvedTargets.forEach(target => {
    const targetPath = path.resolve(process.cwd(), target);
    const source = readFileSafely(targetPath);

    if (targetPath.endsWith('WilsyAccountCommandCenter.jsx')) {
      const bundledSource = readAccountChromeBundleSource(targetPath);
      assertAccountChromeMandate(source, bundledSource);
      console.log(`WILSY_CHROME_MANDATE_ACCOUNT_PASS: ${target}`);
      return;
    }

    assertBasicChromeMandate(source, target);
    console.log(`WILSY_CHROME_MANDATE_BASIC_PASS: ${target}`);
  });

  console.log('WILSY_CHROME_MANDATE_GUARD_PASS');
}

runChromeMandateGuard();
