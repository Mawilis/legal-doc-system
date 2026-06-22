/**
 * WILSY OS — CRM SOVEREIGN INTEGRATION SERVICE
 * VERSION: 1.0.0-AI-THEME-ACCOUNT-PROFILE
 *
 * Role:
 * Pure frontend integration helpers for CRM theming, account profile, command
 * narrative, source posture and Wilsy AI commercial intelligence.
 *
 * Truth policy:
 * This file does not fabricate VERIFIED. It only narrates and derives posture
 * from live CRM data already present in the dashboard.
 */

export const CRM_SOVEREIGN_INTEGRATION_VERSION = '1.0.0-AI-THEME-ACCOUNT-PROFILE';
export const CRM_SOVEREIGN_TRUTH_POLICY = 'NO_FAKE_VERIFIED';

/**
 * @function safeText
 * @description Returns the first non-empty text value.
 * @param {...*} values - Candidate values.
 * @returns {string} First usable string.
 * @collaboration Prevents CRM account profile text from collapsing when tenant fields differ.
 */
export function safeText(...values) {
  const found = values.find((value) => value !== undefined && value !== null && String(value).trim() !== '');
  return found === undefined ? '' : String(found).trim();
}

/**
 * @function buildTenantTheme
 * @description Derives CRM theme variables from active tenant branding and profile data.
 * @param {object} activeTenant - Tenant context object.
 * @param {object} user - Authenticated user.
 * @returns {object} Theme tokens and style variables.
 * @collaboration Integrates the existing tenant/account theming engine into CRM without hardcoded brand assumptions.
 */
export function buildTenantTheme(activeTenant = {}, user = {}) {
  const branding = activeTenant?.branding || activeTenant?.theme || {};
  const primary = safeText(branding.primaryColor, branding.primary, activeTenant?.primaryColor, '#D4AF37');
  const secondary = safeText(branding.secondaryColor, branding.secondary, activeTenant?.secondaryColor, '#8B5CF6');
  const accent = safeText(branding.accentColor, branding.accent, activeTenant?.accentColor, '#38BDF8');
  const companyName = safeText(
    branding.companyName,
    activeTenant?.companyName,
    activeTenant?.name,
    activeTenant?.legalName,
    user?.tenantName,
    'Wilsy OS'
  );

  return {
    companyName,
    primary,
    secondary,
    accent,
    cssVars: {
      '--wilsy-crm-primary': primary,
      '--wilsy-crm-secondary': secondary,
      '--wilsy-crm-accent': accent,
      '--wilsy-crm-glow': `${primary}44`
    },
    panelStyle: {
      borderColor: `${primary}55`,
      boxShadow: `0 0 32px ${primary}22`
    }
  };
}

/**
 * @function buildAccountProfile
 * @description Builds the active account profile used by CRM command surfaces.
 * @param {object} activeTenant - Tenant context object.
 * @param {object} user - Authenticated user.
 * @param {string} tenantId - Resolved tenant id.
 * @returns {object} Account profile projection.
 * @collaboration Makes CRM context-aware of the account profile without coupling to a single profile hook.
 */
export function buildAccountProfile(activeTenant = {}, user = {}, tenantId = 'WILSY_GLOBAL_ROOT') {
  const branding = activeTenant?.branding || {};
  const profile = activeTenant?.profile || activeTenant?.accountProfile || {};

  const companyName = safeText(
    branding.companyName,
    profile.companyName,
    activeTenant?.companyName,
    activeTenant?.name,
    activeTenant?.legalName,
    'Wilsy OS'
  );

  const industry = safeText(profile.industry, activeTenant?.industry, activeTenant?.sector, 'Commercial Command');
  const jurisdiction = safeText(profile.jurisdiction, activeTenant?.jurisdiction, activeTenant?.country, 'ZA');
  const operatingModel = safeText(profile.operatingModel, activeTenant?.operatingModel, 'Sovereign OS');

  return {
    tenantId,
    companyName,
    industry,
    jurisdiction,
    operatingModel,
    userName: safeText(user?.name, user?.fullName, user?.email, 'System Operator'),
    profileLine: `${industry} · ${jurisdiction} · ${operatingModel}`,
    truthPolicy: CRM_SOVEREIGN_TRUTH_POLICY
  };
}

/**
 * @function buildCrmCommandQueryParams
 * @description Converts CRM posture filters into backend query params.
 * @param {object} filters - Filter values.
 * @returns {object} Query params.
 * @collaboration Lets the UI ask for source posture, board readiness, authority and contract posture directly.
 */
export function buildCrmCommandQueryParams(filters = {}) {
  const query = {};
  const entries = {
    sourcePosture: filters.sourcePosture,
    boardStatus: filters.boardStatus,
    authorityStatus: filters.authorityStatus,
    contractStatus: filters.contractStatus
  };

  Object.entries(entries).forEach(([key, value]) => {
    if (value && value !== 'ALL') query[key] = value;
  });

  return query;
}

/**
 * @function countPostures
 * @description Counts records by a nested posture path.
 * @param {Array<object>} records - CRM records.
 * @param {Function} reader - Value reader.
 * @returns {object} Count map.
 * @collaboration Turns raw CRM collections into operating posture intelligence.
 */
export function countPostures(records = [], reader = () => 'UNKNOWN') {
  return records.reduce((acc, record) => {
    const key = reader(record) || 'UNKNOWN';
    acc[key] = (acc[key] || 0) + 1;
    return acc;
  }, {});
}

/**
 * @function buildSourcePostureSummary
 * @description Builds source, authority and contract posture summary from CRM collections and command-center data.
 * @param {object} collections - CRM collection states.
 * @param {object} commandCenter - Optional command-center envelope.
 * @returns {object} Source posture summary.
 * @collaboration Makes Wilsy CRM measure evidence posture as a first-class business signal.
 */
export function buildSourcePostureSummary(collections = {}, commandCenter = null) {
  const records = Object.values(collections).flatMap((collection) => collection?.items || []);
  const verified = records.filter((record) => record?.sourcePosture === 'VERIFIED').length;
  const repairSignals = records.reduce((sum, record) => sum + Number(record?.repairSignals?.length || 0), 0);

  return {
    total: records.length,
    verified,
    missing: records.filter((record) => record?.sourcePosture === 'MISSING').length,
    pending: records.filter((record) => record?.sourcePosture === 'PENDING' || record?.sourcePosture === 'NOT_EVALUATED').length,
    repairSignals: commandCenter?.repairSignalCount ?? repairSignals,
    source: countPostures(records, (record) => record?.sourcePosture || 'NOT_EVALUATED'),
    authority: countPostures(records, (record) => record?.authority?.status || record?.boardReadiness?.authorityPosture || 'UNKNOWN'),
    contract: countPostures(records, (record) => record?.contractLedger?.status || record?.boardReadiness?.contractPosture || 'NONE'),
    board: countPostures(records, (record) => record?.boardReadiness?.status || 'NOT_READY'),
    truthPolicy: CRM_SOVEREIGN_TRUTH_POLICY
  };
}

/**
 * @function buildWilsyAiCrmNarrative
 * @description Builds deterministic Wilsy AI CRM narrative from live dashboard facts.
 * @param {object} context - CRM context.
 * @returns {object} Wilsy AI narrative.
 * @collaboration Gives the dashboard an AI command layer without pretending a model verified facts.
 */
export function buildWilsyAiCrmNarrative(context = {}) {
  const totalRecords = Number(context.sourcePostureSummary?.total || 0);
  const repairSignals = Number(context.sourcePostureSummary?.repairSignals || 0);
  const weightedPipeline = Number(context.weightedPipeline || 0);
  const liveSources = Number(context.liveSources || 0);
  const unboundSources = Number(context.unboundSources || 0);
  const companyName = safeText(context.accountProfile?.companyName, 'Wilsy OS');

  if (!totalRecords) {
    return {
      title: 'Wilsy AI Commercial Command',
      stance: 'ARMED_EMPTY_LEDGER',
      risk: 'CONTROLLED',
      story: `${companyName} CRM is live and waiting for real commercial records. Empty state is acceptable; synthetic records are forbidden.`,
      nextAction: 'Import or create the first real lead, account, deal, authority or contract record.',
      truthPolicy: CRM_SOVEREIGN_TRUTH_POLICY
    };
  }

  if (repairSignals > 0 || unboundSources > 0) {
    return {
      title: 'Wilsy AI Evidence Repair Command',
      stance: 'REPAIR_REQUIRED',
      risk: repairSignals > 10 ? 'HIGH' : 'MEDIUM',
      story: `${companyName} has ${totalRecords} CRM records and ${repairSignals} evidence repair signals. Revenue activity exists, but board reliance waits for source, authority and contract posture.`,
      nextAction: 'Use Source Posture, Authority and Contract filters to clear repair signals one lane at a time.',
      truthPolicy: CRM_SOVEREIGN_TRUTH_POLICY
    };
  }

  return {
    title: 'Wilsy AI Revenue Command',
    stance: 'BOARDROOM_READY',
    risk: 'LOW',
    story: `${companyName} has ${totalRecords} CRM records, ${liveSources} live CRM source lanes and weighted pipeline of R ${Math.round(weightedPipeline).toLocaleString()}.`,
    nextAction: 'Promote verified CRM evidence into Legal Artifact Studio, Source Registry and Executive Dashboard.',
    truthPolicy: CRM_SOVEREIGN_TRUTH_POLICY
  };
}
