/* eslint-disable */
/**
 * ╔════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╗
 * ║ WILSY OS - ACCOUNT THEME TOKEN ENGINE [V2.1.0-FORTUNE-500-RUNTIME]                                                     ║
 * ║ MODE-SAFE TOKENS | GLOBAL CSS VARIABLES | TENANT OVERRIDES | DASHBOARD RUNTIME | EVENT BUS | VALIDATION               ║
 * ╠════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╣
 * ║ ABSOLUTE PATH: /Users/wilsonkhanyezi/legal-doc-system/client/src/components/account/wilsyAccountThemeTokens.js         ║
 * ╠════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╣
 * ║ COLLABORATION                                                                                                          ║
 * ║ 1. Wilson Khanyezi - Mandated a Fortune-500-grade OS visual runtime that can scale to millions of tenants.             ║
 * ║ 2. AI Engineering - Hardened theme normalization, semantic token output, storage, event dispatch and validation.        ║
 * ╚════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╝
 *
 * @fileoverview Token engine for Wilsy OS Account Command Center operating skins.
 * This file is the browser-safe theme runtime bridge between the operating skin registry and every Wilsy OS cockpit.
 */

import DEFAULT_OPERATING_SKINS, {
  WILSY_OPERATING_SKINS_VERSION,
  WILSY_OPERATING_SKIN_IDS
} from './wilsyOperatingSkins.js';

export { DEFAULT_OPERATING_SKINS, WILSY_OPERATING_SKINS_VERSION };

export const WILSY_ACCOUNT_THEME_VERSION = 'V2.1.0-FORTUNE-500-RUNTIME';
export const MODE_KEYS = Object.freeze(['day', 'night', 'auto']);

export const WILSY_THEME_RUNTIME_STORAGE_KEYS = Object.freeze({
  accountTheme: 'wilsy:account-command-center:theme',
  accountMode: 'wilsy:account-command-center:mode',
  dashboardTheme: 'wilsy:dashboard-chrome:theme',
  dashboardMode: 'wilsy:dashboard-chrome:mode',
  runtimeTheme: 'wilsy:runtime:theme',
  runtimeMode: 'wilsy:runtime:mode',
  runtimeResolvedMode: 'wilsy:runtime:resolved-mode',
  runtimePacket: 'wilsy:runtime:theme-packet'
});

export const WILSY_THEME_RUNTIME_EVENTS = Object.freeze({
  global: 'wilsy:theme-change',
  account: 'wilsy:account-command-center:theme-change',
  committed: 'wilsy:theme-runtime-committed'
});

export const WILSY_THEME_RUNTIME_DATASETS = Object.freeze({
  theme: 'wilsyTheme',
  mode: 'wilsyMode',
  resolvedMode: 'wilsyResolvedMode',
  accountTheme: 'wilsyAccountTheme',
  accountMode: 'wilsyAccountMode',
  themeVersion: 'wilsyThemeVersion'
});

const THEME_ALIASES = Object.freeze({
  aurora: 'wilsy_aurora',
  wilsy: 'wilsy_aurora',
  flagship: 'wilsy_aurora',
  forensic: 'forensic_violet',
  violet: 'forensic_violet',
  cobalt: 'cobalt_glass',
  quantum: 'quantum_blue',
  analytics: 'quantum_blue',
  wilsy_daybreak: 'pearl_command',
  daybreak: 'pearl_command',
  pearl: 'pearl_command',
  black: 'sovereign_black',
  sovereign: 'sovereign_black',
  dark: 'sovereign_black',
  dark_ops: 'sovereign_black',
  revenue: 'crm_revenue_pulse',
  crm: 'crm_revenue_pulse',
  sales: 'crm_revenue_pulse',
  legal: 'legal_evidence_noir',
  evidence: 'legal_evidence_noir',
  finance: 'finance_ledger_green',
  ledger: 'finance_ledger_green',
  billing: 'finance_ledger_green',
  people: 'hr_people_graph',
  hr: 'hr_people_graph',
  construction: 'construction_command',
  build: 'construction_command',
  security: 'security_red_team',
  redteam: 'security_red_team',
  documents: 'document_vault_steel',
  vault: 'document_vault_steel',
  banking: 'banking_trust',
  law: 'law_firm_authority',
  health: 'healthcare_calm',
  healthcare: 'healthcare_calm',
  logistics: 'logistics_command',
  real_estate: 'real_estate_prestige',
  realestate: 'real_estate_prestige',
  estate: 'real_estate_prestige',
  government: 'government_civic',
  civic: 'government_civic',
  startup: 'startup_velocity',
  velocity: 'startup_velocity',
  contrast: 'high_contrast_sovereign',
  highcontrast: 'high_contrast_sovereign',
  low_light: 'low_light_ops',
  lowlight: 'low_light_ops',
  boardroom: 'presentation_boardroom',
  presentation: 'presentation_boardroom',
  field: 'outdoor_field_mode'
});

const REQUIRED_TOKEN_KEYS = Object.freeze([
  'isDay',
  'resolvedMode',
  'themeId',
  'accent',
  'secondary',
  'highlight',
  'live',
  'overlay',
  'panelBackground',
  'headerBackground',
  'cardBackground',
  'railBackground',
  'brightText',
  'softText',
  'mutedText',
  'border',
  'strongBorder',
  'authorityBorder',
  'commandBackground',
  'shadow',
  'cssVars'
]);

/**
 * @function normalizeLookupKey
 * @description Normalizes theme ids, aliases and labels into registry-safe lookup keys.
 * @param {string} value - Candidate lookup value.
 * @returns {string} Normalized lookup key.
 * @collaboration Keeps Account, Executive, CRM and tenant defaults from duplicating alias parsing.
 */
export const normalizeLookupKey = value => String(value || '')
  .trim()
  .toLowerCase()
  .replace(/[^a-z0-9]+/g, '_')
  .replace(/^_+|_+$/g, '');

/**
 * @function normalizeMode
 * @description Normalizes a requested Wilsy OS visual mode.
 * @param {string} mode - Candidate display mode.
 * @returns {string} Safe display mode.
 * @collaboration Keeps Day, Night and Auto as explicit operating modes separate from skin identity.
 */
export const normalizeMode = mode => {
  const normalized = normalizeLookupKey(mode);
  return MODE_KEYS.includes(normalized) ? normalized : 'night';
};

/**
 * @function normalizeThemeId
 * @description Normalizes legacy and shorthand theme ids into registered operating skin ids.
 * @param {string} themeId - Candidate theme id.
 * @returns {string} Safe theme id.
 * @collaboration Preserves old localStorage values while moving Wilsy OS to a registry-driven theme contract.
 */
export const normalizeThemeId = themeId => {
  const normalized = normalizeLookupKey(themeId);
  const aliased = THEME_ALIASES[normalized] || normalized;
  return WILSY_OPERATING_SKIN_IDS.includes(aliased) ? aliased : 'wilsy_aurora';
};

/**
 * @function resolveAutoMode
 * @description Resolves Auto mode to day or night based on local operator time.
 * @param {string} mode - Requested mode.
 * @param {Date} now - Optional clock source for deterministic tests.
 * @returns {string} Resolved display mode.
 * @collaboration Makes Auto an environment decision while preserving explicit Day and Night selections.
 */
export const resolveAutoMode = (mode, now = new Date()) => {
  const safeMode = normalizeMode(mode);
  if (safeMode !== 'auto') return safeMode;
  const hour = now.getHours();
  return hour >= 7 && hour < 18 ? 'day' : 'night';
};

/**
 * @function resolveThemeById
 * @description Finds a registered operating skin by id or alias.
 * @param {string} themeId - Candidate theme id.
 * @param {Array<Object>} themes - Theme registry collection.
 * @returns {Object} Registered operating skin.
 * @collaboration Gives every visual runtime path the same safe fallback behavior.
 */
export const resolveThemeById = (themeId, themes = DEFAULT_OPERATING_SKINS) => {
  const safeThemeId = normalizeThemeId(themeId);
  return themes.find(theme => theme.id === safeThemeId) || themes[0] || DEFAULT_OPERATING_SKINS[0];
};

/**
 * @function resolveModePalette
 * @description Resolves the palette object for a selected skin and resolved mode.
 * @param {Object} theme - Operating skin.
 * @param {string} resolvedMode - Resolved day or night mode.
 * @returns {Object} Palette tokens.
 * @collaboration Prevents skins from forcing modes and guarantees every skin has day and night values.
 */
export const resolveModePalette = (theme = {}, resolvedMode = 'night') => {
  const safeMode = resolvedMode === 'day' ? 'day' : 'night';
  const fallback = safeMode === 'day'
    ? {
        canvas: '#f7f8fb',
        panel: '#ffffff',
        card: '#f1f4fb',
        rail: 'rgba(255,255,255,0.92)',
        brightText: '#111827',
        softText: '#53617f',
        mutedText: '#74809a',
        overlay: 'rgba(235,240,250,0.64)'
      }
    : {
        canvas: '#020306',
        panel: '#05070d',
        card: '#080c18',
        rail: 'rgba(3,5,10,0.96)',
        brightText: '#fffaf0',
        softText: '#c5cce5',
        mutedText: '#7c86a8',
        overlay: 'rgba(2,3,6,0.78)'
      };

  return {
    ...fallback,
    ...(theme.modes?.[safeMode] || {})
  };
};

/**
 * @function buildModePair
 * @description Builds a complete day/night mode pair for tenant-provided skins.
 * @param {Object} theme - Candidate operating skin.
 * @returns {Object} Safe day/night mode pair.
 * @collaboration Prevents tenant custom skins from entering the runtime without both visual modes.
 */
export const buildModePair = theme => {
  const fallbackDay = resolveModePalette(theme, 'day');
  const fallbackNight = resolveModePalette(theme, 'night');

  return {
    day: {
      ...fallbackDay,
      ...(theme?.modes?.day || {})
    },
    night: {
      ...fallbackNight,
      ...(theme?.modes?.night || {})
    }
  };
};

/**
 * @function sanitizeOperatingSkin
 * @description Normalizes and completes one tenant or registry operating skin.
 * @param {Object} theme - Candidate operating skin.
 * @param {Object} fallbackTheme - Fallback registry skin.
 * @returns {Object} Safe operating skin.
 * @collaboration Allows enterprise tenant overrides without breaking the Wilsy OS token engine.
 */
export const sanitizeOperatingSkin = (theme = {}, fallbackTheme = DEFAULT_OPERATING_SKINS[0]) => {
  const normalizedId = normalizeThemeId(theme.id || fallbackTheme.id);

  return {
    accent: '#d4af37',
    secondary: '#2436a4',
    highlight: '#17bdf2',
    live: '#84f0c8',
    textOnAccent: '#020306',
    background: '#020306',
    doctrine: 'Tenant operating skin.',
    bestFor: 'Tenant surface',
    category: 'tenant',
    ...fallbackTheme,
    ...theme,
    id: normalizedId,
    modes: buildModePair({
      ...fallbackTheme,
      ...theme
    })
  };
};

/**
 * @function mergeOperatingSkins
 * @description Merges default registry skins with optional tenant-provided custom skins.
 * @param {Array<Object>} customThemes - Optional tenant theme collection.
 * @returns {Array<Object>} Unified operating skin collection.
 * @collaboration Allows tenant extensions without letting custom skins destroy the sovereign registry contract.
 */
export const mergeOperatingSkins = (customThemes = []) => {
  const map = new Map(DEFAULT_OPERATING_SKINS.map(theme => [theme.id, sanitizeOperatingSkin(theme, theme)]));

  customThemes.forEach(theme => {
    if (!theme || !theme.id) return;
    const normalizedId = normalizeThemeId(theme.id);
    const existing = map.get(normalizedId) || DEFAULT_OPERATING_SKINS[0];
    map.set(normalizedId, sanitizeOperatingSkin(theme, existing));
  });

  return Array.from(map.values());
};

/**
 * @function buildSurfaceGradients
 * @description Builds mode-safe surface gradients from a theme and palette.
 * @param {Object} theme - Operating skin.
 * @param {Object} palette - Resolved mode palette.
 * @param {boolean} isDay - Whether the resolved mode is day.
 * @returns {Object} Gradient token map.
 * @collaboration Keeps premium Wilsy OS visual depth centralized instead of scattering gradients across dashboards.
 */
export const buildSurfaceGradients = (theme, palette, isDay) => ({
  panelBackground: isDay
    ? `radial-gradient(circle at 8% 0%, ${theme.highlight}18 0%, transparent 34%), radial-gradient(circle at 92% 8%, ${theme.accent}14 0%, transparent 32%), linear-gradient(180deg, ${palette.panel} 0%, ${palette.card} 100%)`
    : `radial-gradient(circle at top left, ${theme.secondary}33 0%, transparent 36%), radial-gradient(circle at 90% 12%, ${theme.highlight}22 0%, transparent 34%), linear-gradient(180deg, ${palette.panel} 0%, ${palette.canvas} 100%)`,
  headerBackground: isDay
    ? `linear-gradient(135deg, ${theme.highlight}18 0%, ${theme.secondary}18 44%, ${palette.panel} 100%)`
    : `linear-gradient(135deg, #020306 0%, ${theme.secondary} 52%, ${theme.highlight} 100%)`,
  cardBackground: isDay
    ? `linear-gradient(180deg, ${palette.panel} 0%, ${palette.card} 100%)`
    : 'linear-gradient(180deg, rgba(8,12,24,0.94) 0%, rgba(3,5,10,0.98) 100%)',
  commandBackground: `linear-gradient(135deg, #fff1a8 0%, ${theme.accent} 100%)`
});

/**
 * @function buildCssVariableContract
 * @description Builds semantic CSS variables for Account, global OS shell, CRM and future dashboards.
 * @param {Object} params - Token params.
 * @returns {Object} CSS variable map.
 * @collaboration Gives Wilsy OS a single semantic repaint language for millions of tenant dashboards.
 */
export const buildCssVariableContract = ({
  theme,
  palette,
  resolvedMode,
  effectiveMode,
  gradients,
  isDay
}) => Object.freeze({
  '--wilsy-bg': palette.canvas,
  '--wilsy-surface': palette.panel,
  '--wilsy-card': palette.card,
  '--wilsy-rail': palette.rail,
  '--wilsy-text': palette.brightText,
  '--wilsy-soft-text': palette.softText,
  '--wilsy-muted-text': palette.mutedText,
  '--wilsy-overlay': palette.overlay,
  '--wilsy-accent': theme.accent,
  '--wilsy-accent-2': theme.highlight,
  '--wilsy-accent-3': theme.live,
  '--wilsy-secondary': theme.secondary,
  '--wilsy-border-color': isDay ? `${theme.secondary}33` : `${theme.highlight}33`,
  '--wilsy-authority-color': theme.accent,
  '--wilsy-live-color': theme.live,
  '--wilsy-command-bg': gradients.commandBackground,
  '--wilsy-theme-id': theme.id,
  '--wilsy-theme-mode': effectiveMode,
  '--wilsy-theme-resolved-mode': resolvedMode,
  '--wilsy-theme-version': WILSY_ACCOUNT_THEME_VERSION,
  '--wilsy-account-bg': palette.canvas,
  '--wilsy-account-panel': palette.panel,
  '--wilsy-account-card': palette.card,
  '--wilsy-account-rail': palette.rail,
  '--wilsy-account-accent': theme.accent,
  '--wilsy-account-secondary': theme.secondary,
  '--wilsy-account-highlight': theme.highlight,
  '--wilsy-account-live': theme.live,
  '--wilsy-account-bright-text': palette.brightText,
  '--wilsy-account-soft-text': palette.softText,
  '--wilsy-account-muted-text': palette.mutedText,
  '--wilsy-account-overlay': palette.overlay,
  '--crm-bg': palette.canvas,
  '--crm-surface': palette.panel,
  '--crm-card': palette.card,
  '--crm-accent': theme.accent,
  '--crm-accent-2': theme.highlight,
  '--crm-accent-3': theme.live,
  '--crm-glow': isDay ? `${theme.accent}22` : `${theme.accent}18`,
  '--crm-glow-2': isDay ? `${theme.highlight}18` : `${theme.highlight}14`
});

/**
 * @function buildVisualTokens
 * @description Builds the complete inline and CSS-variable token contract for an operating skin and resolved mode.
 * @param {Object} theme - Selected operating skin.
 * @param {string} resolvedMode - Resolved day or night mode.
 * @param {Object} options - Token build options.
 * @param {string} options.effectiveMode - Original mode selection such as auto.
 * @returns {Object} Visual tokens consumed by WilsyAccountCommandCenter and dashboard runtimes.
 * @collaboration Makes selected skin and selected mode independent, tokenized and globally broadcastable.
 */
export const buildVisualTokens = (theme = DEFAULT_OPERATING_SKINS[0], resolvedMode = 'night', options = {}) => {
  const safeTheme = sanitizeOperatingSkin(theme, DEFAULT_OPERATING_SKINS[0]);
  const safeMode = resolvedMode === 'day' ? 'day' : 'night';
  const effectiveMode = normalizeMode(options.effectiveMode || safeMode);
  const palette = resolveModePalette(safeTheme, safeMode);
  const isDay = safeMode === 'day';
  const gradients = buildSurfaceGradients(safeTheme, palette, isDay);

  return Object.freeze({
    isDay,
    resolvedMode: safeMode,
    effectiveMode,
    themeId: safeTheme.id,
    accent: safeTheme.accent,
    secondary: safeTheme.secondary,
    highlight: safeTheme.highlight,
    live: safeTheme.live,
    textOnAccent: safeTheme.textOnAccent,
    overlay: palette.overlay,
    panelBackground: gradients.panelBackground,
    headerBackground: gradients.headerBackground,
    cardBackground: gradients.cardBackground,
    railBackground: palette.rail,
    brightText: palette.brightText,
    softText: palette.softText,
    mutedText: palette.mutedText,
    border: `1px solid ${isDay ? safeTheme.secondary : safeTheme.highlight}33`,
    strongBorder: `1px solid ${safeTheme.live || safeTheme.highlight}66`,
    authorityBorder: `1px solid ${safeTheme.accent}77`,
    commandBackground: gradients.commandBackground,
    shadow: isDay ? `0 24px 70px ${safeTheme.secondary}22` : '0 24px 70px rgba(0,0,0,0.54)',
    palette: Object.freeze(palette),
    cssVars: buildCssVariableContract({
      theme: safeTheme,
      palette,
      resolvedMode: safeMode,
      effectiveMode,
      gradients,
      isDay
    })
  });
};

/**
 * @function resolveThemeRuntimeInput
 * @description Extracts theme and mode values from strings, DOM events, custom events and payload objects.
 * @param {unknown} input - Theme runtime input.
 * @returns {Object} Normalized runtime input.
 * @collaboration Lets Account, CRM, Executive and future services speak one resilient theme payload dialect.
 */
export const resolveThemeRuntimeInput = input => {
  const source = typeof input === 'string'
    ? { themeId: input }
    : (
        input?.detail
        || input?.target
        || input
        || {}
      );

  return {
    themeId: source.themeId || source.skinId || source.theme || source.skin || source.id || source.value,
    mode: source.mode || source.themeMode || source.displayMode,
    source: source.source || 'wilsy_theme_runtime_input'
  };
};

/**
 * @function buildWilsyThemeRuntimePacket
 * @description Builds a complete runtime theme packet from an input payload.
 * @param {Object|string} input - Theme input.
 * @param {Object} options - Runtime options.
 * @returns {Object} Complete runtime packet.
 * @collaboration Standardizes the payload used by Account Command Center, dashboards, storage and event subscribers.
 */
export const buildWilsyThemeRuntimePacket = (input = {}, options = {}) => {
  const parsed = resolveThemeRuntimeInput(input);
  const themes = mergeOperatingSkins(options.availableThemes || []);
  const theme = resolveThemeById(parsed.themeId || options.themeId, themes);
  const effectiveMode = normalizeMode(parsed.mode || options.mode || 'night');
  const resolvedMode = resolveAutoMode(effectiveMode, options.now || new Date());
  const tokens = buildVisualTokens(theme, resolvedMode, { effectiveMode });

  return Object.freeze({
    themeId: theme.id,
    mode: effectiveMode,
    resolvedMode,
    theme,
    tokens,
    source: parsed.source || options.source || 'wilsy_theme_runtime',
    themeVersion: WILSY_ACCOUNT_THEME_VERSION,
    registryVersion: WILSY_OPERATING_SKINS_VERSION,
    emittedAt: options.emittedAt || new Date().toISOString()
  });
};

/**
 * @function readStoredWilsyThemeRuntime
 * @description Reads the stored Wilsy OS theme runtime preference.
 * @param {Object} options - Read options.
 * @returns {Object} Stored runtime values.
 * @collaboration Gives dashboards a shared bootstrap path before Account Command Center mounts.
 */
export const readStoredWilsyThemeRuntime = (options = {}) => {
  if (typeof window === 'undefined') {
    return {
      themeId: options.themeId || 'wilsy_aurora',
      mode: options.mode || 'night'
    };
  }

  try {
    return {
      themeId: window.localStorage.getItem(WILSY_THEME_RUNTIME_STORAGE_KEYS.runtimeTheme)
        || window.localStorage.getItem(WILSY_THEME_RUNTIME_STORAGE_KEYS.dashboardTheme)
        || window.localStorage.getItem(WILSY_THEME_RUNTIME_STORAGE_KEYS.accountTheme)
        || options.themeId
        || 'wilsy_aurora',
      mode: window.localStorage.getItem(WILSY_THEME_RUNTIME_STORAGE_KEYS.runtimeMode)
        || window.localStorage.getItem(WILSY_THEME_RUNTIME_STORAGE_KEYS.dashboardMode)
        || window.localStorage.getItem(WILSY_THEME_RUNTIME_STORAGE_KEYS.accountMode)
        || options.mode
        || 'night'
    };
  } catch (error) {
    return {
      themeId: options.themeId || 'wilsy_aurora',
      mode: options.mode || 'night'
    };
  }
};

/**
 * @function persistWilsyThemeRuntime
 * @description Persists the Wilsy OS theme runtime packet into browser storage.
 * @param {Object} packet - Runtime packet.
 * @returns {void}
 * @collaboration Keeps Account, Executive, CRM and reloads aligned on one theme source of truth.
 */
export const persistWilsyThemeRuntime = packet => {
  if (typeof window === 'undefined' || !packet) return;

  try {
    window.localStorage.setItem(WILSY_THEME_RUNTIME_STORAGE_KEYS.accountTheme, packet.themeId);
    window.localStorage.setItem(WILSY_THEME_RUNTIME_STORAGE_KEYS.accountMode, packet.mode);
    window.localStorage.setItem(WILSY_THEME_RUNTIME_STORAGE_KEYS.dashboardTheme, packet.themeId);
    window.localStorage.setItem(WILSY_THEME_RUNTIME_STORAGE_KEYS.dashboardMode, packet.mode);
    window.localStorage.setItem(WILSY_THEME_RUNTIME_STORAGE_KEYS.runtimeTheme, packet.themeId);
    window.localStorage.setItem(WILSY_THEME_RUNTIME_STORAGE_KEYS.runtimeMode, packet.mode);
    window.localStorage.setItem(WILSY_THEME_RUNTIME_STORAGE_KEYS.runtimeResolvedMode, packet.resolvedMode);
    window.localStorage.setItem(WILSY_THEME_RUNTIME_STORAGE_KEYS.runtimePacket, JSON.stringify({
      themeId: packet.themeId,
      mode: packet.mode,
      resolvedMode: packet.resolvedMode,
      source: packet.source,
      themeVersion: packet.themeVersion,
      registryVersion: packet.registryVersion,
      emittedAt: packet.emittedAt
    }));
  } catch (error) {
    // Storage may be blocked; visual runtime must still apply to the active document.
  }
};


/**
 * @function buildWilsyDashboardReadabilityCss
 * @description Builds the enterprise contrast contract that keeps every Wilsy OS dashboard component readable in day mode.
 * @returns {string} Dashboard readability CSS.
 * @collaboration Prevents day skins from producing disconnected pastel cards, unreadable controls, weak navigation and Grade One SaaS surfaces.
 */
const buildWilsyDashboardReadabilityCss = () => `
body[data-wilsy-theme-runtime][data-wilsy-theme-resolved-mode="day"] {
  --wilsy-readable-day-text: #0f172a;
  --wilsy-readable-day-heading: #020617;
  --wilsy-readable-day-muted: #334155;
  --wilsy-readable-day-soft: #475569;
  --wilsy-readable-day-rail-text: #f8fafc;
  --wilsy-readable-day-rail-muted: #cbd5e1;
  --wilsy-readable-day-panel: rgba(248, 250, 252, 0.96);
  --wilsy-readable-day-card: rgba(255, 255, 255, 0.97);
  --wilsy-readable-day-card-alt: rgba(241, 245, 249, 0.96);
  --wilsy-readable-day-control: rgba(248, 250, 252, 0.94);
  --wilsy-readable-day-control-active: color-mix(in srgb, var(--wilsy-accent, #d4af37) 28%, #ffffff 72%);
  --wilsy-readable-day-rail: rgba(3, 7, 18, 0.98);
  --wilsy-readable-day-rail-alt: rgba(15, 23, 42, 0.98);
  --wilsy-readable-day-border: rgba(15, 23, 42, 0.18);
  --wilsy-readable-day-strong-border: rgba(15, 23, 42, 0.32);
  --wilsy-readable-day-command: rgba(2, 6, 23, 0.94);
}

body[data-wilsy-theme-runtime][data-wilsy-theme-resolved-mode="day"] #root,
body[data-wilsy-theme-runtime][data-wilsy-theme-resolved-mode="day"] main,
body[data-wilsy-theme-runtime][data-wilsy-theme-resolved-mode="day"] section,
body[data-wilsy-theme-runtime][data-wilsy-theme-resolved-mode="day"] article {
  color: var(--wilsy-readable-day-text) !important;
  text-shadow: none !important;
}

body[data-wilsy-theme-runtime][data-wilsy-theme-resolved-mode="day"] [class*="Dashboard"],
body[data-wilsy-theme-runtime][data-wilsy-theme-resolved-mode="day"] [class*="dashboard"],
body[data-wilsy-theme-runtime][data-wilsy-theme-resolved-mode="day"] [class*="CRM"],
body[data-wilsy-theme-runtime][data-wilsy-theme-resolved-mode="day"] [class*="crm"] {
  color: var(--wilsy-readable-day-text) !important;
}

/* DARK PREMIUM SHELLS: sidebar, rails, command spine, tenant header and OS top chrome stay dark for contrast. */
body[data-wilsy-theme-runtime][data-wilsy-theme-resolved-mode="day"] aside,
body[data-wilsy-theme-runtime][data-wilsy-theme-resolved-mode="day"] nav,
body[data-wilsy-theme-runtime][data-wilsy-theme-resolved-mode="day"] header,
body[data-wilsy-theme-runtime][data-wilsy-theme-resolved-mode="day"] [class*="Sidebar"],
body[data-wilsy-theme-runtime][data-wilsy-theme-resolved-mode="day"] [class*="sidebar"],
body[data-wilsy-theme-runtime][data-wilsy-theme-resolved-mode="day"] [class*="Rail"],
body[data-wilsy-theme-runtime][data-wilsy-theme-resolved-mode="day"] [class*="rail"],
body[data-wilsy-theme-runtime][data-wilsy-theme-resolved-mode="day"] [class*="Top"],
body[data-wilsy-theme-runtime][data-wilsy-theme-resolved-mode="day"] [class*="topbar"],
body[data-wilsy-theme-runtime][data-wilsy-theme-resolved-mode="day"] [class*="Topbar"],
body[data-wilsy-theme-runtime][data-wilsy-theme-resolved-mode="day"] [class*="Header"],
body[data-wilsy-theme-runtime][data-wilsy-theme-resolved-mode="day"] [class*="header"],
body[data-wilsy-theme-runtime][data-wilsy-theme-resolved-mode="day"] [class*="Command"],
body[data-wilsy-theme-runtime][data-wilsy-theme-resolved-mode="day"] [class*="command"] {
  background:
    radial-gradient(circle at 8% 0%, color-mix(in srgb, var(--wilsy-accent, #d4af37) 13%, transparent) 0%, transparent 38%),
    linear-gradient(135deg, var(--wilsy-readable-day-rail) 0%, var(--wilsy-readable-day-rail-alt) 100%) !important;
  color: var(--wilsy-readable-day-rail-text) !important;
  border-color: color-mix(in srgb, var(--wilsy-accent, #d4af37) 32%, rgba(255, 255, 255, 0.12)) !important;
  box-shadow: 0 18px 48px rgba(2, 6, 23, 0.28) !important;
}

body[data-wilsy-theme-runtime][data-wilsy-theme-resolved-mode="day"] aside *,
body[data-wilsy-theme-runtime][data-wilsy-theme-resolved-mode="day"] nav *,
body[data-wilsy-theme-runtime][data-wilsy-theme-resolved-mode="day"] header *,
body[data-wilsy-theme-runtime][data-wilsy-theme-resolved-mode="day"] [class*="Sidebar"] *,
body[data-wilsy-theme-runtime][data-wilsy-theme-resolved-mode="day"] [class*="sidebar"] *,
body[data-wilsy-theme-runtime][data-wilsy-theme-resolved-mode="day"] [class*="Rail"] *,
body[data-wilsy-theme-runtime][data-wilsy-theme-resolved-mode="day"] [class*="rail"] *,
body[data-wilsy-theme-runtime][data-wilsy-theme-resolved-mode="day"] [class*="Top"] *,
body[data-wilsy-theme-runtime][data-wilsy-theme-resolved-mode="day"] [class*="Header"] *,
body[data-wilsy-theme-runtime][data-wilsy-theme-resolved-mode="day"] [class*="Command"] * {
  color: var(--wilsy-readable-day-rail-text) !important;
  text-shadow: none !important;
}

body[data-wilsy-theme-runtime][data-wilsy-theme-resolved-mode="day"] aside small,
body[data-wilsy-theme-runtime][data-wilsy-theme-resolved-mode="day"] nav small,
body[data-wilsy-theme-runtime][data-wilsy-theme-resolved-mode="day"] header small,
body[data-wilsy-theme-runtime][data-wilsy-theme-resolved-mode="day"] [class*="Sidebar"] small,
body[data-wilsy-theme-runtime][data-wilsy-theme-resolved-mode="day"] [class*="Rail"] small,
body[data-wilsy-theme-runtime][data-wilsy-theme-resolved-mode="day"] [class*="Header"] small {
  color: var(--wilsy-readable-day-rail-muted) !important;
}

/* LIGHT WORK AREAS: cards, panels, tables, widgets and data blocks use dark typography. */
body[data-wilsy-theme-runtime][data-wilsy-theme-resolved-mode="day"] [class*="Workspace"],
body[data-wilsy-theme-runtime][data-wilsy-theme-resolved-mode="day"] [class*="workspace"],
body[data-wilsy-theme-runtime][data-wilsy-theme-resolved-mode="day"] [class*="Canvas"],
body[data-wilsy-theme-runtime][data-wilsy-theme-resolved-mode="day"] [class*="canvas"],
body[data-wilsy-theme-runtime][data-wilsy-theme-resolved-mode="day"] [class*="Content"],
body[data-wilsy-theme-runtime][data-wilsy-theme-resolved-mode="day"] [class*="content"] {
  background:
    radial-gradient(circle at 0% 0%, color-mix(in srgb, var(--wilsy-accent-2, #17bdf2) 9%, transparent) 0%, transparent 38%),
    linear-gradient(180deg, var(--wilsy-readable-day-panel) 0%, rgba(226, 232, 240, 0.92) 100%) !important;
  color: var(--wilsy-readable-day-text) !important;
}

body[data-wilsy-theme-runtime][data-wilsy-theme-resolved-mode="day"] [class*="Panel"],
body[data-wilsy-theme-runtime][data-wilsy-theme-resolved-mode="day"] [class*="panel"],
body[data-wilsy-theme-runtime][data-wilsy-theme-resolved-mode="day"] [class*="Card"],
body[data-wilsy-theme-runtime][data-wilsy-theme-resolved-mode="day"] [class*="card"],
body[data-wilsy-theme-runtime][data-wilsy-theme-resolved-mode="day"] [class*="Tile"],
body[data-wilsy-theme-runtime][data-wilsy-theme-resolved-mode="day"] [class*="tile"],
body[data-wilsy-theme-runtime][data-wilsy-theme-resolved-mode="day"] [class*="Metric"],
body[data-wilsy-theme-runtime][data-wilsy-theme-resolved-mode="day"] [class*="metric"],
body[data-wilsy-theme-runtime][data-wilsy-theme-resolved-mode="day"] [class*="Stat"],
body[data-wilsy-theme-runtime][data-wilsy-theme-resolved-mode="day"] [class*="stat"],
body[data-wilsy-theme-runtime][data-wilsy-theme-resolved-mode="day"] [class*="Widget"],
body[data-wilsy-theme-runtime][data-wilsy-theme-resolved-mode="day"] [class*="widget"],
body[data-wilsy-theme-runtime][data-wilsy-theme-resolved-mode="day"] [class*="Table"],
body[data-wilsy-theme-runtime][data-wilsy-theme-resolved-mode="day"] [class*="table"] {
  background:
    radial-gradient(circle at 0% 0%, color-mix(in srgb, var(--wilsy-accent-2, #17bdf2) 8%, transparent) 0%, transparent 42%),
    linear-gradient(180deg, var(--wilsy-readable-day-card) 0%, var(--wilsy-readable-day-card-alt) 100%) !important;
  color: var(--wilsy-readable-day-text) !important;
  border-color: var(--wilsy-readable-day-border) !important;
  box-shadow:
    0 16px 42px rgba(15, 23, 42, 0.10),
    inset 0 1px 0 rgba(255, 255, 255, 0.82) !important;
  text-shadow: none !important;
}

body[data-wilsy-theme-runtime][data-wilsy-theme-resolved-mode="day"] [class*="Panel"] *,
body[data-wilsy-theme-runtime][data-wilsy-theme-resolved-mode="day"] [class*="panel"] *,
body[data-wilsy-theme-runtime][data-wilsy-theme-resolved-mode="day"] [class*="Card"] *,
body[data-wilsy-theme-runtime][data-wilsy-theme-resolved-mode="day"] [class*="card"] *,
body[data-wilsy-theme-runtime][data-wilsy-theme-resolved-mode="day"] [class*="Tile"] *,
body[data-wilsy-theme-runtime][data-wilsy-theme-resolved-mode="day"] [class*="tile"] *,
body[data-wilsy-theme-runtime][data-wilsy-theme-resolved-mode="day"] [class*="Metric"] *,
body[data-wilsy-theme-runtime][data-wilsy-theme-resolved-mode="day"] [class*="metric"] *,
body[data-wilsy-theme-runtime][data-wilsy-theme-resolved-mode="day"] [class*="Stat"] *,
body[data-wilsy-theme-runtime][data-wilsy-theme-resolved-mode="day"] [class*="stat"] *,
body[data-wilsy-theme-runtime][data-wilsy-theme-resolved-mode="day"] [class*="Table"] *,
body[data-wilsy-theme-runtime][data-wilsy-theme-resolved-mode="day"] [class*="table"] * {
  color: var(--wilsy-readable-day-text) !important;
  text-shadow: none !important;
}

body[data-wilsy-theme-runtime][data-wilsy-theme-resolved-mode="day"] h1,
body[data-wilsy-theme-runtime][data-wilsy-theme-resolved-mode="day"] h2,
body[data-wilsy-theme-runtime][data-wilsy-theme-resolved-mode="day"] h3,
body[data-wilsy-theme-runtime][data-wilsy-theme-resolved-mode="day"] h4,
body[data-wilsy-theme-runtime][data-wilsy-theme-resolved-mode="day"] strong,
body[data-wilsy-theme-runtime][data-wilsy-theme-resolved-mode="day"] th {
  color: var(--wilsy-readable-day-heading) !important;
}

body[data-wilsy-theme-runtime][data-wilsy-theme-resolved-mode="day"] p,
body[data-wilsy-theme-runtime][data-wilsy-theme-resolved-mode="day"] span,
body[data-wilsy-theme-runtime][data-wilsy-theme-resolved-mode="day"] small,
body[data-wilsy-theme-runtime][data-wilsy-theme-resolved-mode="day"] label,
body[data-wilsy-theme-runtime][data-wilsy-theme-resolved-mode="day"] td {
  text-shadow: none !important;
}

/* Controls: stop pastel buttons/search fields from looking disabled or washed out. */
body[data-wilsy-theme-runtime][data-wilsy-theme-resolved-mode="day"] button,
body[data-wilsy-theme-runtime][data-wilsy-theme-resolved-mode="day"] input,
body[data-wilsy-theme-runtime][data-wilsy-theme-resolved-mode="day"] select,
body[data-wilsy-theme-runtime][data-wilsy-theme-resolved-mode="day"] textarea,
body[data-wilsy-theme-runtime][data-wilsy-theme-resolved-mode="day"] [role="button"],
body[data-wilsy-theme-runtime][data-wilsy-theme-resolved-mode="day"] [class*="Button"],
body[data-wilsy-theme-runtime][data-wilsy-theme-resolved-mode="day"] [class*="button"],
body[data-wilsy-theme-runtime][data-wilsy-theme-resolved-mode="day"] [class*="Search"],
body[data-wilsy-theme-runtime][data-wilsy-theme-resolved-mode="day"] [class*="search"] {
  background:
    linear-gradient(135deg, var(--wilsy-readable-day-control) 0%, rgba(226, 232, 240, 0.94) 100%) !important;
  color: var(--wilsy-readable-day-heading) !important;
  border-color: var(--wilsy-readable-day-strong-border) !important;
  text-shadow: none !important;
  box-shadow:
    0 10px 24px rgba(15, 23, 42, 0.08),
    inset 0 1px 0 rgba(255, 255, 255, 0.82) !important;
}

body[data-wilsy-theme-runtime][data-wilsy-theme-resolved-mode="day"] button *,
body[data-wilsy-theme-runtime][data-wilsy-theme-resolved-mode="day"] [role="button"] *,
body[data-wilsy-theme-runtime][data-wilsy-theme-resolved-mode="day"] [class*="Button"] *,
body[data-wilsy-theme-runtime][data-wilsy-theme-resolved-mode="day"] [class*="button"] * {
  color: var(--wilsy-readable-day-heading) !important;
}

body[data-wilsy-theme-runtime][data-wilsy-theme-resolved-mode="day"] input::placeholder,
body[data-wilsy-theme-runtime][data-wilsy-theme-resolved-mode="day"] textarea::placeholder {
  color: var(--wilsy-readable-day-soft) !important;
  opacity: 1 !important;
}

body[data-wilsy-theme-runtime][data-wilsy-theme-resolved-mode="day"] button:hover,
body[data-wilsy-theme-runtime][data-wilsy-theme-resolved-mode="day"] [role="button"]:hover {
  background:
    linear-gradient(135deg, color-mix(in srgb, var(--wilsy-accent, #d4af37) 28%, #ffffff 72%) 0%, color-mix(in srgb, var(--wilsy-accent-2, #17bdf2) 24%, #ffffff 76%) 100%) !important;
  border-color: color-mix(in srgb, var(--wilsy-accent, #d4af37) 58%, var(--wilsy-readable-day-strong-border) 42%) !important;
}

/* Active nav/pills/badges must look selected, not disabled. */
body[data-wilsy-theme-runtime][data-wilsy-theme-resolved-mode="day"] [aria-selected="true"],
body[data-wilsy-theme-runtime][data-wilsy-theme-resolved-mode="day"] [aria-current="page"],
body[data-wilsy-theme-runtime][data-wilsy-theme-resolved-mode="day"] [data-active="true"],
body[data-wilsy-theme-runtime][data-wilsy-theme-resolved-mode="day"] [class*="active"],
body[data-wilsy-theme-runtime][data-wilsy-theme-resolved-mode="day"] [class*="Active"],
body[data-wilsy-theme-runtime][data-wilsy-theme-resolved-mode="day"] [class*="selected"],
body[data-wilsy-theme-runtime][data-wilsy-theme-resolved-mode="day"] [class*="Selected"],
body[data-wilsy-theme-runtime][data-wilsy-theme-resolved-mode="day"] [class*="Badge"],
body[data-wilsy-theme-runtime][data-wilsy-theme-resolved-mode="day"] [class*="badge"],
body[data-wilsy-theme-runtime][data-wilsy-theme-resolved-mode="day"] [class*="Pill"],
body[data-wilsy-theme-runtime][data-wilsy-theme-resolved-mode="day"] [class*="pill"] {
  background:
    linear-gradient(135deg, color-mix(in srgb, var(--wilsy-accent, #d4af37) 34%, #ffffff 66%) 0%, color-mix(in srgb, var(--wilsy-accent-2, #17bdf2) 30%, #ffffff 70%) 100%) !important;
  color: var(--wilsy-readable-day-heading) !important;
  border-color: color-mix(in srgb, var(--wilsy-accent, #d4af37) 54%, var(--wilsy-readable-day-border) 46%) !important;
}

body[data-wilsy-theme-runtime][data-wilsy-theme-resolved-mode="day"] [aria-selected="true"] *,
body[data-wilsy-theme-runtime][data-wilsy-theme-resolved-mode="day"] [aria-current="page"] *,
body[data-wilsy-theme-runtime][data-wilsy-theme-resolved-mode="day"] [data-active="true"] *,
body[data-wilsy-theme-runtime][data-wilsy-theme-resolved-mode="day"] [class*="active"] *,
body[data-wilsy-theme-runtime][data-wilsy-theme-resolved-mode="day"] [class*="Active"] *,
body[data-wilsy-theme-runtime][data-wilsy-theme-resolved-mode="day"] [class*="Badge"] *,
body[data-wilsy-theme-runtime][data-wilsy-theme-resolved-mode="day"] [class*="badge"] *,
body[data-wilsy-theme-runtime][data-wilsy-theme-resolved-mode="day"] [class*="Pill"] *,
body[data-wilsy-theme-runtime][data-wilsy-theme-resolved-mode="day"] [class*="pill"] * {
  color: var(--wilsy-readable-day-heading) !important;
}

/* SVG/icon contrast follows local surface. */
body[data-wilsy-theme-runtime][data-wilsy-theme-resolved-mode="day"] svg {
  color: currentColor !important;
  stroke: currentColor !important;
}

body[data-wilsy-theme-runtime][data-wilsy-theme-resolved-mode="day"] a {
  color: color-mix(in srgb, var(--wilsy-accent-2, #17bdf2) 58%, #0f172a 42%) !important;
}

/* Right-side vertical command rail remains premium dark. */
body[data-wilsy-theme-runtime][data-wilsy-theme-resolved-mode="day"] [class*="CommandRail"],
body[data-wilsy-theme-runtime][data-wilsy-theme-resolved-mode="day"] [class*="commandRail"],
body[data-wilsy-theme-runtime][data-wilsy-theme-resolved-mode="day"] [class*="CommandSpine"],
body[data-wilsy-theme-runtime][data-wilsy-theme-resolved-mode="day"] [class*="commandSpine"] {
  background: linear-gradient(180deg, rgba(12, 7, 28, 0.98) 0%, rgba(2, 6, 23, 0.98) 100%) !important;
  color: #f8fafc !important;
}
`

/**
 * @function buildWilsyDashboardTitleContrastCss
 * @description Restores premium contrast for dark card headers, section titles, labels, card actions and icons after day-mode body readability rules.
 * @returns {string} Card title contrast CSS.
 * @collaboration Keeps CRM cards from looking like washed-out school-project widgets while preserving readable light card bodies.
 */
const buildWilsyDashboardTitleContrastCss = () => `
body[data-wilsy-theme-runtime][data-wilsy-theme-resolved-mode="day"] {
  --wilsy-readable-dark-strip: rgba(3, 7, 18, 0.98);
  --wilsy-readable-dark-strip-alt: rgba(15, 23, 42, 0.98);
  --wilsy-readable-strip-text: #f8fafc;
  --wilsy-readable-strip-muted: #cbd5e1;
  --wilsy-readable-strip-accent: color-mix(in srgb, var(--wilsy-accent, #d4af37) 72%, #ffffff 28%);
  --wilsy-readable-strip-live: color-mix(in srgb, var(--wilsy-accent-2, #17bdf2) 76%, #ffffff 24%);
}

/* Card header bands and section title strips stay dark and readable. */
body[data-wilsy-theme-runtime][data-wilsy-theme-resolved-mode="day"] [class*="Card"] [class*="Header"],
body[data-wilsy-theme-runtime][data-wilsy-theme-resolved-mode="day"] [class*="card"] [class*="header"],
body[data-wilsy-theme-runtime][data-wilsy-theme-resolved-mode="day"] [class*="Panel"] [class*="Header"],
body[data-wilsy-theme-runtime][data-wilsy-theme-resolved-mode="day"] [class*="panel"] [class*="header"],
body[data-wilsy-theme-runtime][data-wilsy-theme-resolved-mode="day"] [class*="Tile"] [class*="Header"],
body[data-wilsy-theme-runtime][data-wilsy-theme-resolved-mode="day"] [class*="tile"] [class*="header"],
body[data-wilsy-theme-runtime][data-wilsy-theme-resolved-mode="day"] [class*="Metric"] [class*="Header"],
body[data-wilsy-theme-runtime][data-wilsy-theme-resolved-mode="day"] [class*="metric"] [class*="header"],
body[data-wilsy-theme-runtime][data-wilsy-theme-resolved-mode="day"] [class*="Widget"] [class*="Header"],
body[data-wilsy-theme-runtime][data-wilsy-theme-resolved-mode="day"] [class*="widget"] [class*="header"],
body[data-wilsy-theme-runtime][data-wilsy-theme-resolved-mode="day"] [class*="Table"] [class*="Header"],
body[data-wilsy-theme-runtime][data-wilsy-theme-resolved-mode="day"] [class*="table"] [class*="header"] {
  background:
    radial-gradient(circle at 0% 0%, color-mix(in srgb, var(--wilsy-accent, #d4af37) 14%, transparent) 0%, transparent 42%),
    linear-gradient(135deg, var(--wilsy-readable-dark-strip) 0%, var(--wilsy-readable-dark-strip-alt) 100%) !important;
  color: var(--wilsy-readable-strip-text) !important;
  border-color: color-mix(in srgb, var(--wilsy-accent, #d4af37) 34%, rgba(255,255,255,0.12)) !important;
  text-shadow: none !important;
}

/* Everything inside those dark header bands must inherit light contrast. */
body[data-wilsy-theme-runtime][data-wilsy-theme-resolved-mode="day"] [class*="Card"] [class*="Header"] *,
body[data-wilsy-theme-runtime][data-wilsy-theme-resolved-mode="day"] [class*="card"] [class*="header"] *,
body[data-wilsy-theme-runtime][data-wilsy-theme-resolved-mode="day"] [class*="Panel"] [class*="Header"] *,
body[data-wilsy-theme-runtime][data-wilsy-theme-resolved-mode="day"] [class*="panel"] [class*="header"] *,
body[data-wilsy-theme-runtime][data-wilsy-theme-resolved-mode="day"] [class*="Tile"] [class*="Header"] *,
body[data-wilsy-theme-runtime][data-wilsy-theme-resolved-mode="day"] [class*="tile"] [class*="header"] *,
body[data-wilsy-theme-runtime][data-wilsy-theme-resolved-mode="day"] [class*="Metric"] [class*="Header"] *,
body[data-wilsy-theme-runtime][data-wilsy-theme-resolved-mode="day"] [class*="metric"] [class*="header"] *,
body[data-wilsy-theme-runtime][data-wilsy-theme-resolved-mode="day"] [class*="Widget"] [class*="Header"] *,
body[data-wilsy-theme-runtime][data-wilsy-theme-resolved-mode="day"] [class*="widget"] [class*="header"] *,
body[data-wilsy-theme-runtime][data-wilsy-theme-resolved-mode="day"] [class*="Table"] [class*="Header"] *,
body[data-wilsy-theme-runtime][data-wilsy-theme-resolved-mode="day"] [class*="table"] [class*="header"] * {
  color: var(--wilsy-readable-strip-text) !important;
  stroke: currentColor !important;
  text-shadow: none !important;
}

/* Semantic title/label text that lives in dark strips but may not have Header in its class. */
body[data-wilsy-theme-runtime][data-wilsy-theme-resolved-mode="day"] [class*="Card"] [class*="Title"],
body[data-wilsy-theme-runtime][data-wilsy-theme-resolved-mode="day"] [class*="card"] [class*="title"],
body[data-wilsy-theme-runtime][data-wilsy-theme-resolved-mode="day"] [class*="Panel"] [class*="Title"],
body[data-wilsy-theme-runtime][data-wilsy-theme-resolved-mode="day"] [class*="panel"] [class*="title"],
body[data-wilsy-theme-runtime][data-wilsy-theme-resolved-mode="day"] [class*="Tile"] [class*="Title"],
body[data-wilsy-theme-runtime][data-wilsy-theme-resolved-mode="day"] [class*="tile"] [class*="title"],
body[data-wilsy-theme-runtime][data-wilsy-theme-resolved-mode="day"] [class*="Metric"] [class*="Title"],
body[data-wilsy-theme-runtime][data-wilsy-theme-resolved-mode="day"] [class*="metric"] [class*="title"],
body[data-wilsy-theme-runtime][data-wilsy-theme-resolved-mode="day"] [class*="Section"] [class*="Title"],
body[data-wilsy-theme-runtime][data-wilsy-theme-resolved-mode="day"] [class*="section"] [class*="title"] {
  color: var(--wilsy-readable-strip-text) !important;
  text-shadow: none !important;
}

/* CRM-style uppercase labels such as MY OPEN TASKS / TODAY'S LEADS / DEALS CLOSING THIS MONTH. */
body[data-wilsy-theme-runtime][data-wilsy-theme-resolved-mode="day"] [class*="Card"] [class*="Label"],
body[data-wilsy-theme-runtime][data-wilsy-theme-resolved-mode="day"] [class*="card"] [class*="label"],
body[data-wilsy-theme-runtime][data-wilsy-theme-resolved-mode="day"] [class*="Panel"] [class*="Label"],
body[data-wilsy-theme-runtime][data-wilsy-theme-resolved-mode="day"] [class*="panel"] [class*="label"],
body[data-wilsy-theme-runtime][data-wilsy-theme-resolved-mode="day"] [class*="Tile"] [class*="Label"],
body[data-wilsy-theme-runtime][data-wilsy-theme-resolved-mode="day"] [class*="tile"] [class*="label"],
body[data-wilsy-theme-runtime][data-wilsy-theme-resolved-mode="day"] [class*="eyebrow"],
body[data-wilsy-theme-runtime][data-wilsy-theme-resolved-mode="day"] [class*="Eyebrow"],
body[data-wilsy-theme-runtime][data-wilsy-theme-resolved-mode="day"] [class*="caption"],
body[data-wilsy-theme-runtime][data-wilsy-theme-resolved-mode="day"] [class*="Caption"] {
  color: var(--wilsy-readable-strip-accent) !important;
  text-shadow: none !important;
  opacity: 1 !important;
}

/* Action links like Open must not become black-on-dark or white-on-white. */
body[data-wilsy-theme-runtime][data-wilsy-theme-resolved-mode="day"] [class*="Card"] a,
body[data-wilsy-theme-runtime][data-wilsy-theme-resolved-mode="day"] [class*="card"] a,
body[data-wilsy-theme-runtime][data-wilsy-theme-resolved-mode="day"] [class*="Panel"] a,
body[data-wilsy-theme-runtime][data-wilsy-theme-resolved-mode="day"] [class*="panel"] a,
body[data-wilsy-theme-runtime][data-wilsy-theme-resolved-mode="day"] [class*="Card"] button[class*="link"],
body[data-wilsy-theme-runtime][data-wilsy-theme-resolved-mode="day"] [class*="card"] button[class*="link"],
body[data-wilsy-theme-runtime][data-wilsy-theme-resolved-mode="day"] [class*="Panel"] button[class*="link"],
body[data-wilsy-theme-runtime][data-wilsy-theme-resolved-mode="day"] [class*="panel"] button[class*="link"] {
  color: var(--wilsy-readable-strip-live) !important;
  text-decoration: none !important;
  text-shadow: none !important;
}

/* Table headers remain dark and readable even inside light cards. */
body[data-wilsy-theme-runtime][data-wilsy-theme-resolved-mode="day"] thead,
body[data-wilsy-theme-runtime][data-wilsy-theme-resolved-mode="day"] tr[class*="Header"],
body[data-wilsy-theme-runtime][data-wilsy-theme-resolved-mode="day"] tr[class*="header"] {
  background: linear-gradient(135deg, rgba(3, 7, 18, 0.96) 0%, rgba(15, 23, 42, 0.96) 100%) !important;
  color: var(--wilsy-readable-strip-text) !important;
}

body[data-wilsy-theme-runtime][data-wilsy-theme-resolved-mode="day"] thead *,
body[data-wilsy-theme-runtime][data-wilsy-theme-resolved-mode="day"] tr[class*="Header"] *,
body[data-wilsy-theme-runtime][data-wilsy-theme-resolved-mode="day"] tr[class*="header"] * {
  color: var(--wilsy-readable-strip-text) !important;
  stroke: currentColor !important;
}

/* Fallback for the exact CRM card structure where a dark first child/header has no descriptive class. */
body[data-wilsy-theme-runtime][data-wilsy-theme-resolved-mode="day"] [class*="Card"] > :first-child,
body[data-wilsy-theme-runtime][data-wilsy-theme-resolved-mode="day"] [class*="card"] > :first-child,
body[data-wilsy-theme-runtime][data-wilsy-theme-resolved-mode="day"] [class*="Panel"] > :first-child,
body[data-wilsy-theme-runtime][data-wilsy-theme-resolved-mode="day"] [class*="panel"] > :first-child,
body[data-wilsy-theme-runtime][data-wilsy-theme-resolved-mode="day"] [class*="Tile"] > :first-child,
body[data-wilsy-theme-runtime][data-wilsy-theme-resolved-mode="day"] [class*="tile"] > :first-child {
  color: var(--wilsy-readable-strip-text) !important;
  border-color: color-mix(in srgb, var(--wilsy-accent, #d4af37) 32%, rgba(255,255,255,0.10)) !important;
}

body[data-wilsy-theme-runtime][data-wilsy-theme-resolved-mode="day"] [class*="Card"] > :first-child *,
body[data-wilsy-theme-runtime][data-wilsy-theme-resolved-mode="day"] [class*="card"] > :first-child *,
body[data-wilsy-theme-runtime][data-wilsy-theme-resolved-mode="day"] [class*="Panel"] > :first-child *,
body[data-wilsy-theme-runtime][data-wilsy-theme-resolved-mode="day"] [class*="panel"] > :first-child *,
body[data-wilsy-theme-runtime][data-wilsy-theme-resolved-mode="day"] [class*="Tile"] > :first-child *,
body[data-wilsy-theme-runtime][data-wilsy-theme-resolved-mode="day"] [class*="tile"] > :first-child * {
  color: var(--wilsy-readable-strip-text) !important;
  stroke: currentColor !important;
  text-shadow: none !important;
}
`

/**
 * @function buildWilsyDashboardRailConsistencyCss
 * @description Enforces premium sidebar and command-rail behavior so day mode does not expose zero-count text where the OS design expects status dots.
 * @returns {string} Sidebar and rail consistency CSS.
 * @collaboration Keeps CRM navigation, module rails and command spines visually consistent across day and night themes.
 */
const buildWilsyDashboardRailConsistencyCss = () => `
body[data-wilsy-theme-runtime][data-wilsy-theme-resolved-mode="day"] {
  --wilsy-rail-dot: color-mix(in srgb, var(--wilsy-accent-2, #17bdf2) 72%, #ffffff 28%);
  --wilsy-rail-dot-muted: rgba(148, 163, 184, 0.46);
  --wilsy-rail-active-gradient: linear-gradient(135deg, color-mix(in srgb, var(--wilsy-accent, #d4af37) 76%, #ffffff 24%) 0%, color-mix(in srgb, var(--wilsy-accent-2, #17bdf2) 76%, #ffffff 24%) 100%);
}

/* Rails are command surfaces. Day mode must not turn module rows into washed-out content cards. */
body[data-wilsy-theme-runtime][data-wilsy-theme-resolved-mode="day"] aside,
body[data-wilsy-theme-runtime][data-wilsy-theme-resolved-mode="day"] nav,
body[data-wilsy-theme-runtime][data-wilsy-theme-resolved-mode="day"] [class*="Sidebar"],
body[data-wilsy-theme-runtime][data-wilsy-theme-resolved-mode="day"] [class*="sidebar"],
body[data-wilsy-theme-runtime][data-wilsy-theme-resolved-mode="day"] [class*="Rail"],
body[data-wilsy-theme-runtime][data-wilsy-theme-resolved-mode="day"] [class*="rail"] {
  background:
    radial-gradient(circle at 50% 0%, color-mix(in srgb, var(--wilsy-accent, #d4af37) 15%, transparent) 0%, transparent 42%),
    linear-gradient(180deg, rgba(5, 8, 18, 0.98) 0%, rgba(2, 6, 23, 0.99) 100%) !important;
  color: #f8fafc !important;
}

/* Sidebar rows retain rail semantics, but selected rows can still carry the chosen operating skin. */
body[data-wilsy-theme-runtime][data-wilsy-theme-resolved-mode="day"] aside button,
body[data-wilsy-theme-runtime][data-wilsy-theme-resolved-mode="day"] nav button,
body[data-wilsy-theme-runtime][data-wilsy-theme-resolved-mode="day"] aside [role="button"],
body[data-wilsy-theme-runtime][data-wilsy-theme-resolved-mode="day"] nav [role="button"],
body[data-wilsy-theme-runtime][data-wilsy-theme-resolved-mode="day"] [class*="Sidebar"] button,
body[data-wilsy-theme-runtime][data-wilsy-theme-resolved-mode="day"] [class*="sidebar"] button,
body[data-wilsy-theme-runtime][data-wilsy-theme-resolved-mode="day"] [class*="Rail"] button,
body[data-wilsy-theme-runtime][data-wilsy-theme-resolved-mode="day"] [class*="rail"] button,
body[data-wilsy-theme-runtime][data-wilsy-theme-resolved-mode="day"] [class*="nav"] [class*="item"],
body[data-wilsy-theme-runtime][data-wilsy-theme-resolved-mode="day"] [class*="Nav"] [class*="Item"],
body[data-wilsy-theme-runtime][data-wilsy-theme-resolved-mode="day"] [class*="module"] [class*="item"],
body[data-wilsy-theme-runtime][data-wilsy-theme-resolved-mode="day"] [class*="Module"] [class*="Item"] {
  background: transparent !important;
  color: #cbd5e1 !important;
  border-color: transparent !important;
  box-shadow: none !important;
  text-shadow: none !important;
}

body[data-wilsy-theme-runtime][data-wilsy-theme-resolved-mode="day"] aside button *,
body[data-wilsy-theme-runtime][data-wilsy-theme-resolved-mode="day"] nav button *,
body[data-wilsy-theme-runtime][data-wilsy-theme-resolved-mode="day"] aside [role="button"] *,
body[data-wilsy-theme-runtime][data-wilsy-theme-resolved-mode="day"] nav [role="button"] *,
body[data-wilsy-theme-runtime][data-wilsy-theme-resolved-mode="day"] [class*="Sidebar"] button *,
body[data-wilsy-theme-runtime][data-wilsy-theme-resolved-mode="day"] [class*="sidebar"] button *,
body[data-wilsy-theme-runtime][data-wilsy-theme-resolved-mode="day"] [class*="Rail"] button *,
body[data-wilsy-theme-runtime][data-wilsy-theme-resolved-mode="day"] [class*="rail"] button * {
  color: inherit !important;
  stroke: currentColor !important;
}

/* Active/current rail rows get the skin gradient and readable dark foreground, matching the night-mode dot semantics. */
body[data-wilsy-theme-runtime][data-wilsy-theme-resolved-mode="day"] aside [aria-current="page"],
body[data-wilsy-theme-runtime][data-wilsy-theme-resolved-mode="day"] nav [aria-current="page"],
body[data-wilsy-theme-runtime][data-wilsy-theme-resolved-mode="day"] aside [aria-selected="true"],
body[data-wilsy-theme-runtime][data-wilsy-theme-resolved-mode="day"] nav [aria-selected="true"],
body[data-wilsy-theme-runtime][data-wilsy-theme-resolved-mode="day"] aside [data-active="true"],
body[data-wilsy-theme-runtime][data-wilsy-theme-resolved-mode="day"] nav [data-active="true"],
body[data-wilsy-theme-runtime][data-wilsy-theme-resolved-mode="day"] aside [class*="active"],
body[data-wilsy-theme-runtime][data-wilsy-theme-resolved-mode="day"] nav [class*="active"],
body[data-wilsy-theme-runtime][data-wilsy-theme-resolved-mode="day"] [class*="Sidebar"] [class*="active"],
body[data-wilsy-theme-runtime][data-wilsy-theme-resolved-mode="day"] [class*="sidebar"] [class*="active"],
body[data-wilsy-theme-runtime][data-wilsy-theme-resolved-mode="day"] [class*="Rail"] [class*="active"],
body[data-wilsy-theme-runtime][data-wilsy-theme-resolved-mode="day"] [class*="rail"] [class*="active"] {
  background: var(--wilsy-rail-active-gradient) !important;
  color: #020617 !important;
  border-color: color-mix(in srgb, var(--wilsy-accent-2, #17bdf2) 42%, #ffffff 58%) !important;
  box-shadow: 0 16px 34px color-mix(in srgb, var(--wilsy-accent-2, #17bdf2) 18%, transparent) !important;
}

body[data-wilsy-theme-runtime][data-wilsy-theme-resolved-mode="day"] aside [aria-current="page"] *,
body[data-wilsy-theme-runtime][data-wilsy-theme-resolved-mode="day"] nav [aria-current="page"] *,
body[data-wilsy-theme-runtime][data-wilsy-theme-resolved-mode="day"] aside [aria-selected="true"] *,
body[data-wilsy-theme-runtime][data-wilsy-theme-resolved-mode="day"] nav [aria-selected="true"] *,
body[data-wilsy-theme-runtime][data-wilsy-theme-resolved-mode="day"] aside [data-active="true"] *,
body[data-wilsy-theme-runtime][data-wilsy-theme-resolved-mode="day"] nav [data-active="true"] *,
body[data-wilsy-theme-runtime][data-wilsy-theme-resolved-mode="day"] aside [class*="active"] *,
body[data-wilsy-theme-runtime][data-wilsy-theme-resolved-mode="day"] nav [class*="active"] *,
body[data-wilsy-theme-runtime][data-wilsy-theme-resolved-mode="day"] [class*="Sidebar"] [class*="active"] *,
body[data-wilsy-theme-runtime][data-wilsy-theme-resolved-mode="day"] [class*="sidebar"] [class*="active"] *,
body[data-wilsy-theme-runtime][data-wilsy-theme-resolved-mode="day"] [class*="Rail"] [class*="active"] *,
body[data-wilsy-theme-runtime][data-wilsy-theme-resolved-mode="day"] [class*="rail"] [class*="active"] * {
  color: #020617 !important;
  stroke: currentColor !important;
}

/* Rail count/status elements are status dots, not visible zero-count typography. */
body[data-wilsy-theme-runtime][data-wilsy-theme-resolved-mode="day"] aside [class*="count"],
body[data-wilsy-theme-runtime][data-wilsy-theme-resolved-mode="day"] aside [class*="Count"],
body[data-wilsy-theme-runtime][data-wilsy-theme-resolved-mode="day"] aside [class*="indicator"],
body[data-wilsy-theme-runtime][data-wilsy-theme-resolved-mode="day"] aside [class*="Indicator"],
body[data-wilsy-theme-runtime][data-wilsy-theme-resolved-mode="day"] aside [class*="status"],
body[data-wilsy-theme-runtime][data-wilsy-theme-resolved-mode="day"] aside [class*="Status"],
body[data-wilsy-theme-runtime][data-wilsy-theme-resolved-mode="day"] aside [class*="dot"],
body[data-wilsy-theme-runtime][data-wilsy-theme-resolved-mode="day"] aside [class*="Dot"],
body[data-wilsy-theme-runtime][data-wilsy-theme-resolved-mode="day"] nav [class*="count"],
body[data-wilsy-theme-runtime][data-wilsy-theme-resolved-mode="day"] nav [class*="Count"],
body[data-wilsy-theme-runtime][data-wilsy-theme-resolved-mode="day"] nav [class*="indicator"],
body[data-wilsy-theme-runtime][data-wilsy-theme-resolved-mode="day"] nav [class*="Indicator"],
body[data-wilsy-theme-runtime][data-wilsy-theme-resolved-mode="day"] nav [class*="status"],
body[data-wilsy-theme-runtime][data-wilsy-theme-resolved-mode="day"] nav [class*="Status"],
body[data-wilsy-theme-runtime][data-wilsy-theme-resolved-mode="day"] nav [class*="dot"],
body[data-wilsy-theme-runtime][data-wilsy-theme-resolved-mode="day"] nav [class*="Dot"],
body[data-wilsy-theme-runtime][data-wilsy-theme-resolved-mode="day"] [class*="Sidebar"] [class*="count"],
body[data-wilsy-theme-runtime][data-wilsy-theme-resolved-mode="day"] [class*="Sidebar"] [class*="Count"],
body[data-wilsy-theme-runtime][data-wilsy-theme-resolved-mode="day"] [class*="Sidebar"] [class*="indicator"],
body[data-wilsy-theme-runtime][data-wilsy-theme-resolved-mode="day"] [class*="Sidebar"] [class*="Indicator"],
body[data-wilsy-theme-runtime][data-wilsy-theme-resolved-mode="day"] [class*="sidebar"] [class*="count"],
body[data-wilsy-theme-runtime][data-wilsy-theme-resolved-mode="day"] [class*="sidebar"] [class*="Count"],
body[data-wilsy-theme-runtime][data-wilsy-theme-resolved-mode="day"] [class*="sidebar"] [class*="indicator"],
body[data-wilsy-theme-runtime][data-wilsy-theme-resolved-mode="day"] [class*="sidebar"] [class*="Indicator"] {
  display: inline-block !important;
  width: 10px !important;
  min-width: 10px !important;
  max-width: 10px !important;
  height: 10px !important;
  min-height: 10px !important;
  max-height: 10px !important;
  padding: 0 !important;
  border-radius: 999px !important;
  overflow: hidden !important;
  font-size: 0 !important;
  line-height: 0 !important;
  letter-spacing: 0 !important;
  color: transparent !important;
  background: var(--wilsy-rail-dot-muted) !important;
  border: 0 !important;
  box-shadow: none !important;
}

/* Fallback for CRM rows where the trailing status has no semantic class and is just the last child. */
body[data-wilsy-theme-runtime][data-wilsy-theme-resolved-mode="day"] aside [role="button"] > :last-child:not(svg):not(path),
body[data-wilsy-theme-runtime][data-wilsy-theme-resolved-mode="day"] nav [role="button"] > :last-child:not(svg):not(path),
body[data-wilsy-theme-runtime][data-wilsy-theme-resolved-mode="day"] aside button > :last-child:not(svg):not(path),
body[data-wilsy-theme-runtime][data-wilsy-theme-resolved-mode="day"] nav button > :last-child:not(svg):not(path),
body[data-wilsy-theme-runtime][data-wilsy-theme-resolved-mode="day"] [class*="Sidebar"] [role="button"] > :last-child:not(svg):not(path),
body[data-wilsy-theme-runtime][data-wilsy-theme-resolved-mode="day"] [class*="sidebar"] [role="button"] > :last-child:not(svg):not(path),
body[data-wilsy-theme-runtime][data-wilsy-theme-resolved-mode="day"] [class*="Rail"] [role="button"] > :last-child:not(svg):not(path),
body[data-wilsy-theme-runtime][data-wilsy-theme-resolved-mode="day"] [class*="rail"] [role="button"] > :last-child:not(svg):not(path) {
  display: inline-block !important;
  width: 10px !important;
  min-width: 10px !important;
  max-width: 10px !important;
  height: 10px !important;
  min-height: 10px !important;
  max-height: 10px !important;
  padding: 0 !important;
  border-radius: 999px !important;
  overflow: hidden !important;
  font-size: 0 !important;
  line-height: 0 !important;
  color: transparent !important;
  background: var(--wilsy-rail-dot-muted) !important;
}

/* Active row indicator is the live accent dot. */
body[data-wilsy-theme-runtime][data-wilsy-theme-resolved-mode="day"] aside [aria-current="page"] [class*="count"],
body[data-wilsy-theme-runtime][data-wilsy-theme-resolved-mode="day"] aside [data-active="true"] [class*="count"],
body[data-wilsy-theme-runtime][data-wilsy-theme-resolved-mode="day"] aside [class*="active"] [class*="count"],
body[data-wilsy-theme-runtime][data-wilsy-theme-resolved-mode="day"] nav [aria-current="page"] [class*="count"],
body[data-wilsy-theme-runtime][data-wilsy-theme-resolved-mode="day"] nav [data-active="true"] [class*="count"],
body[data-wilsy-theme-runtime][data-wilsy-theme-resolved-mode="day"] nav [class*="active"] [class*="count"],
body[data-wilsy-theme-runtime][data-wilsy-theme-resolved-mode="day"] aside [aria-current="page"] > :last-child:not(svg):not(path),
body[data-wilsy-theme-runtime][data-wilsy-theme-resolved-mode="day"] aside [data-active="true"] > :last-child:not(svg):not(path),
body[data-wilsy-theme-runtime][data-wilsy-theme-resolved-mode="day"] aside [class*="active"] > :last-child:not(svg):not(path),
body[data-wilsy-theme-runtime][data-wilsy-theme-resolved-mode="day"] nav [aria-current="page"] > :last-child:not(svg):not(path),
body[data-wilsy-theme-runtime][data-wilsy-theme-resolved-mode="day"] nav [data-active="true"] > :last-child:not(svg):not(path),
body[data-wilsy-theme-runtime][data-wilsy-theme-resolved-mode="day"] nav [class*="active"] > :last-child:not(svg):not(path) {
  background: var(--wilsy-rail-dot) !important;
  box-shadow: 0 0 0 4px color-mix(in srgb, var(--wilsy-rail-dot) 18%, transparent) !important;
}

/* Search fields in rails are readable controls, but not card-like white slabs. */
body[data-wilsy-theme-runtime][data-wilsy-theme-resolved-mode="day"] aside input,
body[data-wilsy-theme-runtime][data-wilsy-theme-resolved-mode="day"] nav input,
body[data-wilsy-theme-runtime][data-wilsy-theme-resolved-mode="day"] [class*="Sidebar"] input,
body[data-wilsy-theme-runtime][data-wilsy-theme-resolved-mode="day"] [class*="sidebar"] input,
body[data-wilsy-theme-runtime][data-wilsy-theme-resolved-mode="day"] [class*="Rail"] input,
body[data-wilsy-theme-runtime][data-wilsy-theme-resolved-mode="day"] [class*="rail"] input {
  background: rgba(15, 23, 42, 0.76) !important;
  color: #f8fafc !important;
  border-color: color-mix(in srgb, var(--wilsy-accent-2, #17bdf2) 32%, rgba(255,255,255,0.14)) !important;
}

body[data-wilsy-theme-runtime][data-wilsy-theme-resolved-mode="day"] aside input::placeholder,
body[data-wilsy-theme-runtime][data-wilsy-theme-resolved-mode="day"] nav input::placeholder,
body[data-wilsy-theme-runtime][data-wilsy-theme-resolved-mode="day"] [class*="Sidebar"] input::placeholder,
body[data-wilsy-theme-runtime][data-wilsy-theme-resolved-mode="day"] [class*="sidebar"] input::placeholder {
  color: #cbd5e1 !important;
  opacity: 1 !important;
}
`

/**
 * @function buildWilsyDashboardHeroAndMetricContrastCss
 * @description Governs workspace hero headers and KPI summary tiles so day-mode themes remain executive-readable.
 * @returns {string} Hero and KPI contrast CSS.
 * @collaboration Completes Wilsy OS visual authority across CRM hero regions, summary statistics and page intelligence sections.
 */
const buildWilsyDashboardHeroAndMetricContrastCss = () => `
body[data-wilsy-theme-runtime][data-wilsy-theme-resolved-mode="day"] {
  --wilsy-readable-hero-text: #f8fafc;
  --wilsy-readable-hero-muted: #cbd5e1;
  --wilsy-readable-hero-accent: color-mix(in srgb, var(--wilsy-accent, #d4af37) 72%, #ffffff 28%);
  --wilsy-readable-kpi-text: #0f172a;
  --wilsy-readable-kpi-heading: #020617;
  --wilsy-readable-kpi-muted: #334155;
  --wilsy-readable-kpi-card: rgba(248, 250, 252, 0.92);
  --wilsy-readable-kpi-border: rgba(15, 23, 42, 0.22);
}

/* Workspace hero / page intelligence header: dark executive strip, readable labels. */
body[data-wilsy-theme-runtime][data-wilsy-theme-resolved-mode="day"] [class*="Workspace"] > :first-child,
body[data-wilsy-theme-runtime][data-wilsy-theme-resolved-mode="day"] [class*="workspace"] > :first-child,
body[data-wilsy-theme-runtime][data-wilsy-theme-resolved-mode="day"] [class*="Canvas"] > :first-child,
body[data-wilsy-theme-runtime][data-wilsy-theme-resolved-mode="day"] [class*="canvas"] > :first-child,
body[data-wilsy-theme-runtime][data-wilsy-theme-resolved-mode="day"] [class*="Content"] > :first-child,
body[data-wilsy-theme-runtime][data-wilsy-theme-resolved-mode="day"] [class*="content"] > :first-child,
body[data-wilsy-theme-runtime][data-wilsy-theme-resolved-mode="day"] [class*="Hero"],
body[data-wilsy-theme-runtime][data-wilsy-theme-resolved-mode="day"] [class*="hero"],
body[data-wilsy-theme-runtime][data-wilsy-theme-resolved-mode="day"] [class*="PageHeader"],
body[data-wilsy-theme-runtime][data-wilsy-theme-resolved-mode="day"] [class*="pageHeader"],
body[data-wilsy-theme-runtime][data-wilsy-theme-resolved-mode="day"] [class*="OverviewHeader"],
body[data-wilsy-theme-runtime][data-wilsy-theme-resolved-mode="day"] [class*="overviewHeader"] {
  background:
    radial-gradient(circle at 0% 0%, color-mix(in srgb, var(--wilsy-accent, #d4af37) 14%, transparent) 0%, transparent 42%),
    radial-gradient(circle at 96% 0%, color-mix(in srgb, var(--wilsy-accent-2, #17bdf2) 12%, transparent) 0%, transparent 38%),
    linear-gradient(135deg, rgba(3, 7, 18, 0.98) 0%, rgba(15, 23, 42, 0.96) 100%) !important;
  color: var(--wilsy-readable-hero-text) !important;
  border-color: color-mix(in srgb, var(--wilsy-accent, #d4af37) 34%, rgba(255, 255, 255, 0.10)) !important;
  text-shadow: none !important;
}

/* Everything inside the hero strip must be light, except KPI cards explicitly corrected below. */
body[data-wilsy-theme-runtime][data-wilsy-theme-resolved-mode="day"] [class*="Workspace"] > :first-child *,
body[data-wilsy-theme-runtime][data-wilsy-theme-resolved-mode="day"] [class*="workspace"] > :first-child *,
body[data-wilsy-theme-runtime][data-wilsy-theme-resolved-mode="day"] [class*="Canvas"] > :first-child *,
body[data-wilsy-theme-runtime][data-wilsy-theme-resolved-mode="day"] [class*="canvas"] > :first-child *,
body[data-wilsy-theme-runtime][data-wilsy-theme-resolved-mode="day"] [class*="Content"] > :first-child *,
body[data-wilsy-theme-runtime][data-wilsy-theme-resolved-mode="day"] [class*="content"] > :first-child *,
body[data-wilsy-theme-runtime][data-wilsy-theme-resolved-mode="day"] [class*="Hero"] *,
body[data-wilsy-theme-runtime][data-wilsy-theme-resolved-mode="day"] [class*="hero"] *,
body[data-wilsy-theme-runtime][data-wilsy-theme-resolved-mode="day"] [class*="PageHeader"] *,
body[data-wilsy-theme-runtime][data-wilsy-theme-resolved-mode="day"] [class*="pageHeader"] * {
  color: var(--wilsy-readable-hero-text) !important;
  stroke: currentColor !important;
  text-shadow: none !important;
}

body[data-wilsy-theme-runtime][data-wilsy-theme-resolved-mode="day"] [class*="Workspace"] > :first-child small,
body[data-wilsy-theme-runtime][data-wilsy-theme-resolved-mode="day"] [class*="workspace"] > :first-child small,
body[data-wilsy-theme-runtime][data-wilsy-theme-resolved-mode="day"] [class*="Hero"] small,
body[data-wilsy-theme-runtime][data-wilsy-theme-resolved-mode="day"] [class*="hero"] small,
body[data-wilsy-theme-runtime][data-wilsy-theme-resolved-mode="day"] [class*="PageHeader"] small,
body[data-wilsy-theme-runtime][data-wilsy-theme-resolved-mode="day"] [class*="pageHeader"] small {
  color: var(--wilsy-readable-hero-muted) !important;
}

/* KPI / summary tiles inside hero: light glass card with dark readable metric text. */
body[data-wilsy-theme-runtime][data-wilsy-theme-resolved-mode="day"] [class*="Kpi"],
body[data-wilsy-theme-runtime][data-wilsy-theme-resolved-mode="day"] [class*="KPI"],
body[data-wilsy-theme-runtime][data-wilsy-theme-resolved-mode="day"] [class*="kpi"],
body[data-wilsy-theme-runtime][data-wilsy-theme-resolved-mode="day"] [class*="Summary"],
body[data-wilsy-theme-runtime][data-wilsy-theme-resolved-mode="day"] [class*="summary"],
body[data-wilsy-theme-runtime][data-wilsy-theme-resolved-mode="day"] [class*="Readiness"],
body[data-wilsy-theme-runtime][data-wilsy-theme-resolved-mode="day"] [class*="readiness"],
body[data-wilsy-theme-runtime][data-wilsy-theme-resolved-mode="day"] [class*="Source"],
body[data-wilsy-theme-runtime][data-wilsy-theme-resolved-mode="day"] [class*="source"],
body[data-wilsy-theme-runtime][data-wilsy-theme-resolved-mode="day"] [class*="Pipeline"],
body[data-wilsy-theme-runtime][data-wilsy-theme-resolved-mode="day"] [class*="pipeline"],
body[data-wilsy-theme-runtime][data-wilsy-theme-resolved-mode="day"] [class*="StatCard"],
body[data-wilsy-theme-runtime][data-wilsy-theme-resolved-mode="day"] [class*="statCard"],
body[data-wilsy-theme-runtime][data-wilsy-theme-resolved-mode="day"] [class*="MetricCard"],
body[data-wilsy-theme-runtime][data-wilsy-theme-resolved-mode="day"] [class*="metricCard"] {
  background:
    radial-gradient(circle at 0% 0%, color-mix(in srgb, var(--wilsy-accent-2, #17bdf2) 8%, transparent) 0%, transparent 42%),
    linear-gradient(180deg, var(--wilsy-readable-kpi-card) 0%, rgba(226, 232, 240, 0.92) 100%) !important;
  color: var(--wilsy-readable-kpi-text) !important;
  border-color: var(--wilsy-readable-kpi-border) !important;
  box-shadow:
    0 14px 34px rgba(15, 23, 42, 0.14),
    inset 0 1px 0 rgba(255, 255, 255, 0.82) !important;
  text-shadow: none !important;
}

/* KPI children override hero light text. */
body[data-wilsy-theme-runtime][data-wilsy-theme-resolved-mode="day"] [class*="Kpi"] *,
body[data-wilsy-theme-runtime][data-wilsy-theme-resolved-mode="day"] [class*="KPI"] *,
body[data-wilsy-theme-runtime][data-wilsy-theme-resolved-mode="day"] [class*="kpi"] *,
body[data-wilsy-theme-runtime][data-wilsy-theme-resolved-mode="day"] [class*="Summary"] *,
body[data-wilsy-theme-runtime][data-wilsy-theme-resolved-mode="day"] [class*="summary"] *,
body[data-wilsy-theme-runtime][data-wilsy-theme-resolved-mode="day"] [class*="Readiness"] *,
body[data-wilsy-theme-runtime][data-wilsy-theme-resolved-mode="day"] [class*="readiness"] *,
body[data-wilsy-theme-runtime][data-wilsy-theme-resolved-mode="day"] [class*="Source"] *,
body[data-wilsy-theme-runtime][data-wilsy-theme-resolved-mode="day"] [class*="source"] *,
body[data-wilsy-theme-runtime][data-wilsy-theme-resolved-mode="day"] [class*="Pipeline"] *,
body[data-wilsy-theme-runtime][data-wilsy-theme-resolved-mode="day"] [class*="pipeline"] * {
  color: var(--wilsy-readable-kpi-text) !important;
  stroke: currentColor !important;
  text-shadow: none !important;
}

/* KPI labels are muted dark, values are strong dark. */
body[data-wilsy-theme-runtime][data-wilsy-theme-resolved-mode="day"] [class*="Kpi"] small,
body[data-wilsy-theme-runtime][data-wilsy-theme-resolved-mode="day"] [class*="kpi"] small,
body[data-wilsy-theme-runtime][data-wilsy-theme-resolved-mode="day"] [class*="Summary"] small,
body[data-wilsy-theme-runtime][data-wilsy-theme-resolved-mode="day"] [class*="summary"] small,
body[data-wilsy-theme-runtime][data-wilsy-theme-resolved-mode="day"] [class*="Readiness"] small,
body[data-wilsy-theme-runtime][data-wilsy-theme-resolved-mode="day"] [class*="readiness"] small,
body[data-wilsy-theme-runtime][data-wilsy-theme-resolved-mode="day"] [class*="Source"] small,
body[data-wilsy-theme-runtime][data-wilsy-theme-resolved-mode="day"] [class*="source"] small,
body[data-wilsy-theme-runtime][data-wilsy-theme-resolved-mode="day"] [class*="Pipeline"] small,
body[data-wilsy-theme-runtime][data-wilsy-theme-resolved-mode="day"] [class*="pipeline"] small,
body[data-wilsy-theme-runtime][data-wilsy-theme-resolved-mode="day"] [class*="Label"],
body[data-wilsy-theme-runtime][data-wilsy-theme-resolved-mode="day"] [class*="label"] {
  color: var(--wilsy-readable-kpi-muted) !important;
  opacity: 1 !important;
}

body[data-wilsy-theme-runtime][data-wilsy-theme-resolved-mode="day"] [class*="Kpi"] strong,
body[data-wilsy-theme-runtime][data-wilsy-theme-resolved-mode="day"] [class*="kpi"] strong,
body[data-wilsy-theme-runtime][data-wilsy-theme-resolved-mode="day"] [class*="Summary"] strong,
body[data-wilsy-theme-runtime][data-wilsy-theme-resolved-mode="day"] [class*="summary"] strong,
body[data-wilsy-theme-runtime][data-wilsy-theme-resolved-mode="day"] [class*="Readiness"] strong,
body[data-wilsy-theme-runtime][data-wilsy-theme-resolved-mode="day"] [class*="readiness"] strong,
body[data-wilsy-theme-runtime][data-wilsy-theme-resolved-mode="day"] [class*="Source"] strong,
body[data-wilsy-theme-runtime][data-wilsy-theme-resolved-mode="day"] [class*="source"] strong,
body[data-wilsy-theme-runtime][data-wilsy-theme-resolved-mode="day"] [class*="Pipeline"] strong,
body[data-wilsy-theme-runtime][data-wilsy-theme-resolved-mode="day"] [class*="pipeline"] strong,
body[data-wilsy-theme-runtime][data-wilsy-theme-resolved-mode="day"] [class*="Value"],
body[data-wilsy-theme-runtime][data-wilsy-theme-resolved-mode="day"] [class*="value"],
body[data-wilsy-theme-runtime][data-wilsy-theme-resolved-mode="day"] [class*="Number"],
body[data-wilsy-theme-runtime][data-wilsy-theme-resolved-mode="day"] [class*="number"] {
  color: var(--wilsy-readable-kpi-heading) !important;
  opacity: 1 !important;
}
`

/**
 * @function buildWilsyDashboardTopCommandControlsCss
 * @description Governs CRM top command controls so day-mode search, identity blocks and action buttons remain premium, readable and properly spaced.
 * @returns {string} Top command controls CSS.
 * @collaboration Completes Wilsy OS command-bar visual authority across identity, search and primary action controls.
 */
const buildWilsyDashboardTopCommandControlsCss = () => `
body[data-wilsy-theme-runtime][data-wilsy-theme-resolved-mode="day"] {
  --wilsy-top-command-control: rgba(248, 250, 252, 0.96);
  --wilsy-top-command-control-strong: rgba(255, 255, 255, 0.98);
  --wilsy-top-command-text: #0f172a;
  --wilsy-top-command-heading: #020617;
  --wilsy-top-command-muted: #475569;
  --wilsy-top-command-soft: #64748b;
  --wilsy-top-command-border: rgba(15, 23, 42, 0.26);
  --wilsy-top-command-focus: color-mix(in srgb, var(--wilsy-accent-2, #17bdf2) 40%, rgba(15, 23, 42, 0.26) 60%);
}

/* Top command row spacing and control rhythm. */
body[data-wilsy-theme-runtime][data-wilsy-theme-resolved-mode="day"] header,
body[data-wilsy-theme-runtime][data-wilsy-theme-resolved-mode="day"] [class*="Topbar"],
body[data-wilsy-theme-runtime][data-wilsy-theme-resolved-mode="day"] [class*="topbar"],
body[data-wilsy-theme-runtime][data-wilsy-theme-resolved-mode="day"] [class*="Toolbar"],
body[data-wilsy-theme-runtime][data-wilsy-theme-resolved-mode="day"] [class*="toolbar"],
body[data-wilsy-theme-runtime][data-wilsy-theme-resolved-mode="day"] [class*="CommandBar"],
body[data-wilsy-theme-runtime][data-wilsy-theme-resolved-mode="day"] [class*="commandBar"],
body[data-wilsy-theme-runtime][data-wilsy-theme-resolved-mode="day"] [class*="ActionBar"],
body[data-wilsy-theme-runtime][data-wilsy-theme-resolved-mode="day"] [class*="actionBar"] {
  gap: clamp(12px, 1vw, 20px) !important;
  padding-inline: clamp(16px, 1.6vw, 30px) !important;
  align-items: center !important;
  border-color: color-mix(in srgb, var(--wilsy-accent, #d4af37) 30%, rgba(255, 255, 255, 0.12)) !important;
}

/* Identity block, search shell, and top command buttons are readable command controls. */
body[data-wilsy-theme-runtime][data-wilsy-theme-resolved-mode="day"] header button,
body[data-wilsy-theme-runtime][data-wilsy-theme-resolved-mode="day"] header [role="button"],
body[data-wilsy-theme-runtime][data-wilsy-theme-resolved-mode="day"] header input,
body[data-wilsy-theme-runtime][data-wilsy-theme-resolved-mode="day"] header select,
body[data-wilsy-theme-runtime][data-wilsy-theme-resolved-mode="day"] [class*="Topbar"] button,
body[data-wilsy-theme-runtime][data-wilsy-theme-resolved-mode="day"] [class*="topbar"] button,
body[data-wilsy-theme-runtime][data-wilsy-theme-resolved-mode="day"] [class*="Toolbar"] button,
body[data-wilsy-theme-runtime][data-wilsy-theme-resolved-mode="day"] [class*="toolbar"] button,
body[data-wilsy-theme-runtime][data-wilsy-theme-resolved-mode="day"] [class*="CommandBar"] button,
body[data-wilsy-theme-runtime][data-wilsy-theme-resolved-mode="day"] [class*="commandBar"] button,
body[data-wilsy-theme-runtime][data-wilsy-theme-resolved-mode="day"] [class*="ActionBar"] button,
body[data-wilsy-theme-runtime][data-wilsy-theme-resolved-mode="day"] [class*="actionBar"] button,
body[data-wilsy-theme-runtime][data-wilsy-theme-resolved-mode="day"] [class*="Topbar"] input,
body[data-wilsy-theme-runtime][data-wilsy-theme-resolved-mode="day"] [class*="topbar"] input,
body[data-wilsy-theme-runtime][data-wilsy-theme-resolved-mode="day"] [class*="Toolbar"] input,
body[data-wilsy-theme-runtime][data-wilsy-theme-resolved-mode="day"] [class*="toolbar"] input,
body[data-wilsy-theme-runtime][data-wilsy-theme-resolved-mode="day"] [class*="CommandBar"] input,
body[data-wilsy-theme-runtime][data-wilsy-theme-resolved-mode="day"] [class*="commandBar"] input,
body[data-wilsy-theme-runtime][data-wilsy-theme-resolved-mode="day"] [class*="Search"],
body[data-wilsy-theme-runtime][data-wilsy-theme-resolved-mode="day"] [class*="search"] {
  min-height: 54px !important;
  padding: 0 clamp(18px, 1.2vw, 26px) !important;
  margin-inline: clamp(4px, 0.35vw, 8px) !important;
  background:
    linear-gradient(180deg, var(--wilsy-top-command-control-strong) 0%, var(--wilsy-top-command-control) 100%) !important;
  color: var(--wilsy-top-command-heading) !important;
  border: 1px solid var(--wilsy-top-command-border) !important;
  box-shadow:
    0 12px 28px rgba(15, 23, 42, 0.10),
    inset 0 1px 0 rgba(255, 255, 255, 0.86) !important;
  text-shadow: none !important;
  opacity: 1 !important;
}

/* Search input inner text, placeholder and icon contrast. */
body[data-wilsy-theme-runtime][data-wilsy-theme-resolved-mode="day"] input,
body[data-wilsy-theme-runtime][data-wilsy-theme-resolved-mode="day"] textarea {
  color: var(--wilsy-top-command-heading) !important;
  caret-color: var(--wilsy-top-command-heading) !important;
  text-shadow: none !important;
  opacity: 1 !important;
}

body[data-wilsy-theme-runtime][data-wilsy-theme-resolved-mode="day"] input::placeholder,
body[data-wilsy-theme-runtime][data-wilsy-theme-resolved-mode="day"] textarea::placeholder {
  color: var(--wilsy-top-command-muted) !important;
  opacity: 1 !important;
}

body[data-wilsy-theme-runtime][data-wilsy-theme-resolved-mode="day"] [class*="Search"] *,
body[data-wilsy-theme-runtime][data-wilsy-theme-resolved-mode="day"] [class*="search"] * {
  color: var(--wilsy-top-command-heading) !important;
  stroke: currentColor !important;
  opacity: 1 !important;
}

/* Identity / profile block in the top row. */
body[data-wilsy-theme-runtime][data-wilsy-theme-resolved-mode="day"] [class*="Identity"],
body[data-wilsy-theme-runtime][data-wilsy-theme-resolved-mode="day"] [class*="identity"],
body[data-wilsy-theme-runtime][data-wilsy-theme-resolved-mode="day"] [class*="Profile"],
body[data-wilsy-theme-runtime][data-wilsy-theme-resolved-mode="day"] [class*="profile"],
body[data-wilsy-theme-runtime][data-wilsy-theme-resolved-mode="day"] [class*="User"],
body[data-wilsy-theme-runtime][data-wilsy-theme-resolved-mode="day"] [class*="user"] {
  color: var(--wilsy-top-command-heading) !important;
  text-shadow: none !important;
}

body[data-wilsy-theme-runtime][data-wilsy-theme-resolved-mode="day"] [class*="Identity"] *,
body[data-wilsy-theme-runtime][data-wilsy-theme-resolved-mode="day"] [class*="identity"] *,
body[data-wilsy-theme-runtime][data-wilsy-theme-resolved-mode="day"] [class*="Profile"] *,
body[data-wilsy-theme-runtime][data-wilsy-theme-resolved-mode="day"] [class*="profile"] *,
body[data-wilsy-theme-runtime][data-wilsy-theme-resolved-mode="day"] [class*="User"] *,
body[data-wilsy-theme-runtime][data-wilsy-theme-resolved-mode="day"] [class*="user"] * {
  color: inherit !important;
  stroke: currentColor !important;
  text-shadow: none !important;
}

/* Subtitles like SUPER ADMIN must remain visible, not washed out. */
body[data-wilsy-theme-runtime][data-wilsy-theme-resolved-mode="day"] [class*="Identity"] small,
body[data-wilsy-theme-runtime][data-wilsy-theme-resolved-mode="day"] [class*="identity"] small,
body[data-wilsy-theme-runtime][data-wilsy-theme-resolved-mode="day"] [class*="Profile"] small,
body[data-wilsy-theme-runtime][data-wilsy-theme-resolved-mode="day"] [class*="profile"] small,
body[data-wilsy-theme-runtime][data-wilsy-theme-resolved-mode="day"] [class*="User"] small,
body[data-wilsy-theme-runtime][data-wilsy-theme-resolved-mode="day"] [class*="user"] small {
  color: var(--wilsy-top-command-muted) !important;
  opacity: 1 !important;
}

/* Top action buttons: premium spacing, not cramped flat text. */
body[data-wilsy-theme-runtime][data-wilsy-theme-resolved-mode="day"] header button,
body[data-wilsy-theme-runtime][data-wilsy-theme-resolved-mode="day"] [class*="Topbar"] button,
body[data-wilsy-theme-runtime][data-wilsy-theme-resolved-mode="day"] [class*="topbar"] button,
body[data-wilsy-theme-runtime][data-wilsy-theme-resolved-mode="day"] [class*="Toolbar"] button,
body[data-wilsy-theme-runtime][data-wilsy-theme-resolved-mode="day"] [class*="toolbar"] button,
body[data-wilsy-theme-runtime][data-wilsy-theme-resolved-mode="day"] [class*="CommandBar"] button,
body[data-wilsy-theme-runtime][data-wilsy-theme-resolved-mode="day"] [class*="commandBar"] button,
body[data-wilsy-theme-runtime][data-wilsy-theme-resolved-mode="day"] [class*="ActionBar"] button,
body[data-wilsy-theme-runtime][data-wilsy-theme-resolved-mode="day"] [class*="actionBar"] button {
  display: inline-flex !important;
  align-items: center !important;
  justify-content: center !important;
  gap: 10px !important;
  min-width: clamp(150px, 10vw, 230px) !important;
  min-height: 54px !important;
  padding-inline: clamp(18px, 1.4vw, 30px) !important;
  border-radius: 0 !important;
  letter-spacing: 0.12em !important;
  font-weight: 900 !important;
  color: var(--wilsy-top-command-heading) !important;
  background:
    linear-gradient(135deg, rgba(255, 255, 255, 0.98) 0%, rgba(226, 232, 240, 0.94) 100%) !important;
  border-color: var(--wilsy-top-command-border) !important;
}

body[data-wilsy-theme-runtime][data-wilsy-theme-resolved-mode="day"] header button *,
body[data-wilsy-theme-runtime][data-wilsy-theme-resolved-mode="day"] [class*="Topbar"] button *,
body[data-wilsy-theme-runtime][data-wilsy-theme-resolved-mode="day"] [class*="topbar"] button *,
body[data-wilsy-theme-runtime][data-wilsy-theme-resolved-mode="day"] [class*="Toolbar"] button *,
body[data-wilsy-theme-runtime][data-wilsy-theme-resolved-mode="day"] [class*="toolbar"] button *,
body[data-wilsy-theme-runtime][data-wilsy-theme-resolved-mode="day"] [class*="CommandBar"] button *,
body[data-wilsy-theme-runtime][data-wilsy-theme-resolved-mode="day"] [class*="commandBar"] button *,
body[data-wilsy-theme-runtime][data-wilsy-theme-resolved-mode="day"] [class*="ActionBar"] button *,
body[data-wilsy-theme-runtime][data-wilsy-theme-resolved-mode="day"] [class*="actionBar"] button * {
  color: var(--wilsy-top-command-heading) !important;
  stroke: currentColor !important;
  opacity: 1 !important;
}

/* Primary CTA such as NEW LEAD gets the operating skin gradient. */
body[data-wilsy-theme-runtime][data-wilsy-theme-resolved-mode="day"] header button:last-of-type,
body[data-wilsy-theme-runtime][data-wilsy-theme-resolved-mode="day"] [class*="Topbar"] button:last-of-type,
body[data-wilsy-theme-runtime][data-wilsy-theme-resolved-mode="day"] [class*="topbar"] button:last-of-type,
body[data-wilsy-theme-runtime][data-wilsy-theme-resolved-mode="day"] [class*="Toolbar"] button:last-of-type,
body[data-wilsy-theme-runtime][data-wilsy-theme-resolved-mode="day"] [class*="toolbar"] button:last-of-type,
body[data-wilsy-theme-runtime][data-wilsy-theme-resolved-mode="day"] [class*="CommandBar"] button:last-of-type,
body[data-wilsy-theme-runtime][data-wilsy-theme-resolved-mode="day"] [class*="commandBar"] button:last-of-type,
body[data-wilsy-theme-runtime][data-wilsy-theme-resolved-mode="day"] [class*="ActionBar"] button:last-of-type,
body[data-wilsy-theme-runtime][data-wilsy-theme-resolved-mode="day"] [class*="actionBar"] button:last-of-type {
  background:
    linear-gradient(135deg, color-mix(in srgb, var(--wilsy-accent, #d4af37) 70%, #ffffff 30%) 0%, color-mix(in srgb, var(--wilsy-accent-2, #17bdf2) 72%, #ffffff 28%) 100%) !important;
  color: #020617 !important;
  border-color: color-mix(in srgb, var(--wilsy-accent-2, #17bdf2) 48%, rgba(15, 23, 42, 0.18) 52%) !important;
}

body[data-wilsy-theme-runtime][data-wilsy-theme-resolved-mode="day"] header button:hover,
body[data-wilsy-theme-runtime][data-wilsy-theme-resolved-mode="day"] [class*="Topbar"] button:hover,
body[data-wilsy-theme-runtime][data-wilsy-theme-resolved-mode="day"] [class*="topbar"] button:hover,
body[data-wilsy-theme-runtime][data-wilsy-theme-resolved-mode="day"] [class*="Toolbar"] button:hover,
body[data-wilsy-theme-runtime][data-wilsy-theme-resolved-mode="day"] [class*="toolbar"] button:hover,
body[data-wilsy-theme-runtime][data-wilsy-theme-resolved-mode="day"] [class*="CommandBar"] button:hover,
body[data-wilsy-theme-runtime][data-wilsy-theme-resolved-mode="day"] [class*="commandBar"] button:hover,
body[data-wilsy-theme-runtime][data-wilsy-theme-resolved-mode="day"] [class*="ActionBar"] button:hover,
body[data-wilsy-theme-runtime][data-wilsy-theme-resolved-mode="day"] [class*="actionBar"] button:hover {
  transform: translateY(-1px);
  box-shadow:
    0 0 0 1px color-mix(in srgb, var(--wilsy-accent, #d4af37) 48%, transparent),
    0 18px 42px rgba(15, 23, 42, 0.18) !important;
}
`


// WILSY_SEMANTIC_THEME_RUNTIME_STEP_R5A_START
const WILSY_SEMANTIC_THEME_RUNTIME_VERSION = 'R5A-SEMANTIC-OS-COMPILER';

/**
 * @function normalizeWilsyHexColor
 * @description Normalizes a hex color into six-character uppercase form.
 * @param {string} value - Candidate color value.
 * @param {string} fallback - Fallback color.
 * @returns {string} Normalized hex color.
 * @collaboration Allows every operating skin to compile into consistent semantic OS slots.
 */
const normalizeWilsyHexColor = (value, fallback = '#111827') => {
  const raw = String(value || fallback || '#111827').trim();

  if (/^#[0-9a-f]{3}$/i.test(raw)) {
    return `#${raw[1]}${raw[1]}${raw[2]}${raw[2]}${raw[3]}${raw[3]}`.toUpperCase();
  }

  if (/^#[0-9a-f]{6}$/i.test(raw)) return raw.toUpperCase();

  return fallback.toUpperCase();
};

/**
 * @function clampWilsyColorChannel
 * @description Keeps a color channel inside RGB boundaries.
 * @param {number} value - RGB channel.
 * @returns {number} Safe channel.
 * @collaboration Supports deterministic semantic color mixing for all dashboard themes.
 */
const clampWilsyColorChannel = value => Math.max(0, Math.min(255, Math.round(Number(value) || 0)));

/**
 * @function parseWilsyHexColor
 * @description Parses a hex color into RGB channels.
 * @param {string} value - Hex color.
 * @returns {Object} RGB channels.
 * @collaboration Powers dynamic theme compilation without hardcoding individual skins.
 */
const parseWilsyHexColor = value => {
  const safe = normalizeWilsyHexColor(value).replace('#', '');

  return {
    r: parseInt(safe.slice(0, 2), 16),
    g: parseInt(safe.slice(2, 4), 16),
    b: parseInt(safe.slice(4, 6), 16)
  };
};

/**
 * @function toWilsyHexColor
 * @description Converts RGB channels into a hex color.
 * @param {Object} color - RGB color.
 * @returns {string} Hex color.
 * @collaboration Keeps semantic slot generation browser-safe and dependency-free.
 */
const toWilsyHexColor = color => {
  const r = clampWilsyColorChannel(color.r).toString(16).padStart(2, '0');
  const g = clampWilsyColorChannel(color.g).toString(16).padStart(2, '0');
  const b = clampWilsyColorChannel(color.b).toString(16).padStart(2, '0');

  return `#${r}${g}${b}`.toUpperCase();
};

/**
 * @function mixWilsyHexColors
 * @description Mixes two hex colors using a weighted ratio.
 * @param {string} base - Base color.
 * @param {string} overlay - Overlay color.
 * @param {number} amount - Overlay amount between 0 and 1.
 * @returns {string} Mixed hex color.
 * @collaboration Converts operating-skin palettes into semantic component colors.
 */
const mixWilsyHexColors = (base, overlay, amount = 0.5) => {
  const safeAmount = Math.max(0, Math.min(1, Number(amount) || 0));
  const a = parseWilsyHexColor(base);
  const b = parseWilsyHexColor(overlay);

  return toWilsyHexColor({
    r: a.r + ((b.r - a.r) * safeAmount),
    g: a.g + ((b.g - a.g) * safeAmount),
    b: a.b + ((b.b - a.b) * safeAmount)
  });
};

/**
 * @function getWilsyReadableTextColor
 * @description Chooses dark or light foreground text based on perceived luminance.
 * @param {string} background - Background hex color.
 * @returns {string} Readable text color.
 * @collaboration Ensures future Wilsy OS skins do not create broken contrast.
 */
const getWilsyReadableTextColor = background => {
  const { r, g, b } = parseWilsyHexColor(background);
  const luminance = ((r * 299) + (g * 587) + (b * 114)) / 1000;

  return luminance >= 145 ? '#0F172A' : '#F8FAFC';
};

/**
 * @function buildWilsySemanticThemeSlots
 * @description Compiles raw theme variables into semantic Wilsy OS component slots.
 * @param {Object} params - Theme runtime params.
 * @returns {Object} Semantic slot variables.
 * @collaboration Makes every dashboard consume a stable OS contract instead of one-off theme CSS.
 */
const buildWilsySemanticThemeSlots = ({ cssVars = {}, resolvedModeId = 'night', modeId = 'night', themeId = 'wilsy_aurora' } = {}) => {
  const isDay = resolvedModeId === 'day';
  const accent = normalizeWilsyHexColor(cssVars['--wilsy-accent'] || cssVars['--crm-accent'] || '#D4AF37', '#D4AF37');
  const accentTwo = normalizeWilsyHexColor(cssVars['--wilsy-accent-2'] || cssVars['--wilsy-live'] || '#17BDF2', '#17BDF2');
  const danger = normalizeWilsyHexColor(cssVars['--wilsy-danger'] || '#EF4444', '#EF4444');
  const baseNight = normalizeWilsyHexColor(cssVars['--wilsy-bg'] || '#020617', '#020617');
  const surfaceNight = normalizeWilsyHexColor(cssVars['--wilsy-surface'] || '#080C18', '#080C18');

  const canvas = isDay ? mixWilsyHexColors('#F8FAFC', accentTwo, 0.045) : mixWilsyHexColors(baseNight, '#000000', 0.12);
  const workspace = isDay ? mixWilsyHexColors('#F1F5F9', accentTwo, 0.035) : mixWilsyHexColors(surfaceNight, baseNight, 0.55);
  const rail = isDay ? mixWilsyHexColors('#020617', accent, 0.09) : mixWilsyHexColors(baseNight, accent, 0.05);
  const topbar = isDay ? mixWilsyHexColors('#020617', accentTwo, 0.075) : mixWilsyHexColors(baseNight, accentTwo, 0.04);
  const card = isDay ? '#F8FAFC' : mixWilsyHexColors(surfaceNight, accent, 0.035);
  const cardAlt = isDay ? '#E2E8F0' : mixWilsyHexColors(baseNight, surfaceNight, 0.52);
  const cardHeader = isDay ? mixWilsyHexColors('#020617', accent, 0.075) : mixWilsyHexColors('#020617', accent, 0.105);
  const control = isDay ? '#F8FAFC' : mixWilsyHexColors(surfaceNight, '#FFFFFF', 0.035);
  const controlAlt = isDay ? '#E2E8F0' : mixWilsyHexColors(baseNight, '#FFFFFF', 0.055);
  const primary = mixWilsyHexColors(accent, accentTwo, 0.48);

  return {
    '--wilsy-semantic-runtime-version': WILSY_SEMANTIC_THEME_RUNTIME_VERSION,
    '--wilsy-semantic-theme-id': themeId,
    '--wilsy-semantic-mode': modeId,
    '--wilsy-semantic-resolved-mode': resolvedModeId,

    '--wilsy-slot-canvas-bg': canvas,
    '--wilsy-slot-canvas-text': getWilsyReadableTextColor(canvas),
    '--wilsy-slot-workspace-bg': workspace,
    '--wilsy-slot-workspace-text': getWilsyReadableTextColor(workspace),

    '--wilsy-slot-rail-bg': rail,
    '--wilsy-slot-rail-text': '#F8FAFC',
    '--wilsy-slot-rail-muted': '#CBD5E1',
    '--wilsy-slot-rail-active-bg': `linear-gradient(135deg, ${mixWilsyHexColors(accent, '#FFFFFF', isDay ? 0.24 : 0.05)} 0%, ${mixWilsyHexColors(accentTwo, '#FFFFFF', isDay ? 0.20 : 0.05)} 100%)`,
    '--wilsy-slot-rail-active-text': isDay ? '#020617' : '#F8FAFC',
    '--wilsy-slot-rail-dot': mixWilsyHexColors(accentTwo, '#FFFFFF', 0.2),
    '--wilsy-slot-rail-dot-muted': isDay ? 'rgba(148, 163, 184, 0.46)' : 'rgba(148, 163, 184, 0.38)',

    '--wilsy-slot-topbar-bg': topbar,
    '--wilsy-slot-topbar-text': '#F8FAFC',
    '--wilsy-slot-topbar-muted': '#CBD5E1',

    '--wilsy-slot-card-bg': card,
    '--wilsy-slot-card-bg-alt': cardAlt,
    '--wilsy-slot-card-text': isDay ? '#0F172A' : '#F8FAFC',
    '--wilsy-slot-card-muted': isDay ? '#334155' : '#CBD5E1',
    '--wilsy-slot-card-header-bg': cardHeader,
    '--wilsy-slot-card-header-text': '#F8FAFC',
    '--wilsy-slot-card-border': isDay ? 'rgba(15, 23, 42, 0.18)' : 'rgba(248, 250, 252, 0.12)',

    '--wilsy-slot-control-bg': control,
    '--wilsy-slot-control-bg-alt': controlAlt,
    '--wilsy-slot-control-text': isDay ? '#0F172A' : '#F8FAFC',
    '--wilsy-slot-control-muted': isDay ? '#475569' : '#CBD5E1',
    '--wilsy-slot-control-border': isDay ? 'rgba(15, 23, 42, 0.24)' : 'rgba(248, 250, 252, 0.16)',

    '--wilsy-slot-primary-bg': `linear-gradient(135deg, ${mixWilsyHexColors(accent, '#FFFFFF', isDay ? 0.24 : 0.02)} 0%, ${mixWilsyHexColors(accentTwo, '#FFFFFF', isDay ? 0.20 : 0.02)} 100%)`,
    '--wilsy-slot-primary-text': getWilsyReadableTextColor(primary),

    '--wilsy-slot-kpi-bg': isDay ? '#E2E8F0' : mixWilsyHexColors(surfaceNight, '#FFFFFF', 0.055),
    '--wilsy-slot-kpi-text': isDay ? '#0F172A' : '#F8FAFC',
    '--wilsy-slot-kpi-label': isDay ? '#334155' : '#CBD5E1',

    '--wilsy-slot-accent': accent,
    '--wilsy-slot-accent-2': accentTwo,
    '--wilsy-slot-danger': danger
  };
};

/**
 * @function buildWilsySemanticThemeCss
 * @description Builds the stable OS component contract consumed by all dashboards.
 * @returns {string} Semantic runtime CSS.
 * @collaboration Allows 20+ Wilsy dashboards to inherit themes through component roles instead of local patches.
 */
const buildWilsySemanticThemeCss = () => `
body[data-wilsy-semantic-theme-runtime] {
  background: var(--wilsy-slot-canvas-bg) !important;
  color: var(--wilsy-slot-canvas-text) !important;
}

body[data-wilsy-semantic-theme-runtime] :where([data-wilsy-role~="canvas"], [data-wilsy-role~="dashboard"], #root, main, [class*="Dashboard"], [class*="dashboard"]) {
  background: var(--wilsy-slot-canvas-bg) !important;
  color: var(--wilsy-slot-canvas-text) !important;
}

body[data-wilsy-semantic-theme-runtime] :where([data-wilsy-role~="rail"], [data-wilsy-role~="sidebar"], aside, nav, [class*="Sidebar"], [class*="sidebar"], [class*="Rail"], [class*="rail"]) {
  background:
    radial-gradient(circle at 50% 0%, color-mix(in srgb, var(--wilsy-slot-accent) 14%, transparent) 0%, transparent 42%),
    linear-gradient(180deg, var(--wilsy-slot-rail-bg) 0%, #020617 100%) !important;
  color: var(--wilsy-slot-rail-text) !important;
  border-color: color-mix(in srgb, var(--wilsy-slot-accent) 32%, rgba(255,255,255,0.12)) !important;
}

body[data-wilsy-semantic-theme-runtime] :where([data-wilsy-role~="rail"], [data-wilsy-role~="sidebar"], aside, nav, [class*="Sidebar"], [class*="sidebar"], [class*="Rail"], [class*="rail"]) * {
  color: inherit !important;
  stroke: currentColor !important;
}

body[data-wilsy-semantic-theme-runtime] :where(aside, nav, [class*="Sidebar"], [class*="sidebar"], [class*="Rail"], [class*="rail"]) :where(button, [role="button"], [class*="item"], [class*="Item"]) {
  background: transparent !important;
  color: var(--wilsy-slot-rail-muted) !important;
  border-color: transparent !important;
  box-shadow: none !important;
}

body[data-wilsy-semantic-theme-runtime] :where(aside, nav, [class*="Sidebar"], [class*="sidebar"], [class*="Rail"], [class*="rail"]) :where([aria-current="page"], [aria-selected="true"], [data-active="true"], [class*="active"], [class*="Active"]) {
  background: var(--wilsy-slot-rail-active-bg) !important;
  color: var(--wilsy-slot-rail-active-text) !important;
  box-shadow: 0 16px 34px color-mix(in srgb, var(--wilsy-slot-accent-2) 18%, transparent) !important;
}

body[data-wilsy-semantic-theme-runtime] :where(aside, nav, [class*="Sidebar"], [class*="sidebar"], [class*="Rail"], [class*="rail"]) :where([class*="count"], [class*="Count"], [class*="indicator"], [class*="Indicator"], [class*="status"], [class*="Status"], [class*="dot"], [class*="Dot"]),
body[data-wilsy-semantic-theme-runtime] :where(aside, nav, [class*="Sidebar"], [class*="sidebar"], [class*="Rail"], [class*="rail"]) :where(button, [role="button"]) > :last-child:not(svg):not(path) {
  display: inline-block !important;
  width: 10px !important;
  min-width: 10px !important;
  max-width: 10px !important;
  height: 10px !important;
  min-height: 10px !important;
  max-height: 10px !important;
  padding: 0 !important;
  border-radius: 999px !important;
  overflow: hidden !important;
  font-size: 0 !important;
  line-height: 0 !important;
  color: transparent !important;
  background: var(--wilsy-slot-rail-dot-muted) !important;
  border: 0 !important;
}

body[data-wilsy-semantic-theme-runtime] :where([data-wilsy-role~="topbar"], [data-wilsy-role~="commandbar"], header, [class*="Topbar"], [class*="topbar"], [class*="Toolbar"], [class*="toolbar"], [class*="CommandBar"], [class*="commandBar"], [class*="ActionBar"], [class*="actionBar"]) {
  background:
    radial-gradient(circle at 0% 0%, color-mix(in srgb, var(--wilsy-slot-accent-2) 10%, transparent) 0%, transparent 40%),
    linear-gradient(135deg, var(--wilsy-slot-topbar-bg) 0%, #020617 100%) !important;
  color: var(--wilsy-slot-topbar-text) !important;
  border-color: color-mix(in srgb, var(--wilsy-slot-accent) 30%, rgba(255,255,255,0.12)) !important;
  gap: clamp(12px, 1vw, 20px) !important;
  padding-inline: clamp(16px, 1.6vw, 30px) !important;
}

body[data-wilsy-semantic-theme-runtime] :where(header, [class*="Topbar"], [class*="topbar"], [class*="Toolbar"], [class*="toolbar"], [class*="CommandBar"], [class*="commandBar"], [class*="ActionBar"], [class*="actionBar"]) :where(input, select, textarea, [class*="Search"], [class*="search"], button, [role="button"]) {
  min-height: 54px !important;
  padding-inline: clamp(18px, 1.4vw, 30px) !important;
  margin-inline: clamp(4px, 0.35vw, 8px) !important;
  background: linear-gradient(180deg, var(--wilsy-slot-control-bg) 0%, var(--wilsy-slot-control-bg-alt) 100%) !important;
  color: var(--wilsy-slot-control-text) !important;
  border: 1px solid var(--wilsy-slot-control-border) !important;
  box-shadow: 0 12px 28px rgba(15, 23, 42, 0.10), inset 0 1px 0 rgba(255,255,255,0.72) !important;
  opacity: 1 !important;
}

body[data-wilsy-semantic-theme-runtime] input,
body[data-wilsy-semantic-theme-runtime] textarea {
  color: var(--wilsy-slot-control-text) !important;
  caret-color: var(--wilsy-slot-control-text) !important;
}

body[data-wilsy-semantic-theme-runtime] input::placeholder,
body[data-wilsy-semantic-theme-runtime] textarea::placeholder {
  color: var(--wilsy-slot-control-muted) !important;
  opacity: 1 !important;
}

body[data-wilsy-semantic-theme-runtime] :where(header, [class*="Topbar"], [class*="topbar"], [class*="Toolbar"], [class*="toolbar"], [class*="CommandBar"], [class*="commandBar"], [class*="ActionBar"], [class*="actionBar"]) button:last-of-type {
  background: var(--wilsy-slot-primary-bg) !important;
  color: var(--wilsy-slot-primary-text) !important;
  border-color: color-mix(in srgb, var(--wilsy-slot-accent-2) 48%, rgba(15,23,42,0.18) 52%) !important;
}

body[data-wilsy-semantic-theme-runtime] :where([data-wilsy-role~="workspace"], [class*="Workspace"], [class*="workspace"], [class*="Canvas"], [class*="canvas"], [class*="Content"], [class*="content"]) {
  background: linear-gradient(180deg, var(--wilsy-slot-workspace-bg) 0%, var(--wilsy-slot-canvas-bg) 100%) !important;
  color: var(--wilsy-slot-workspace-text) !important;
}

body[data-wilsy-semantic-theme-runtime] :where([data-wilsy-role~="card"], [class*="Card"], [class*="card"], [class*="Panel"], [class*="panel"], [class*="Tile"], [class*="tile"], [class*="Widget"], [class*="widget"], [class*="Table"], [class*="table"]) {
  background: linear-gradient(180deg, var(--wilsy-slot-card-bg) 0%, var(--wilsy-slot-card-bg-alt) 100%) !important;
  color: var(--wilsy-slot-card-text) !important;
  border-color: var(--wilsy-slot-card-border) !important;
  box-shadow: 0 16px 42px rgba(15, 23, 42, 0.10) !important;
}

body[data-wilsy-semantic-theme-runtime] :where([data-wilsy-role~="card"], [class*="Card"], [class*="card"], [class*="Panel"], [class*="panel"], [class*="Tile"], [class*="tile"]) * {
  color: var(--wilsy-slot-card-text) !important;
  text-shadow: none !important;
}

body[data-wilsy-semantic-theme-runtime] :where([data-wilsy-role~="card-header"], [class*="Card"] > :first-child, [class*="card"] > :first-child, [class*="Panel"] > :first-child, [class*="panel"] > :first-child, [class*="Header"], [class*="header"], thead) {
  background: linear-gradient(135deg, var(--wilsy-slot-card-header-bg) 0%, #020617 100%) !important;
  color: var(--wilsy-slot-card-header-text) !important;
  border-color: color-mix(in srgb, var(--wilsy-slot-accent) 34%, rgba(255,255,255,0.12)) !important;
}

body[data-wilsy-semantic-theme-runtime] :where([data-wilsy-role~="card-header"], [class*="Card"] > :first-child, [class*="card"] > :first-child, [class*="Panel"] > :first-child, [class*="panel"] > :first-child, [class*="Header"], [class*="header"], thead) * {
  color: var(--wilsy-slot-card-header-text) !important;
  stroke: currentColor !important;
}

body[data-wilsy-semantic-theme-runtime] :where([data-wilsy-role~="kpi"], [class*="Kpi"], [class*="KPI"], [class*="kpi"], [class*="Summary"], [class*="summary"], [class*="Readiness"], [class*="readiness"], [class*="Source"], [class*="source"], [class*="Pipeline"], [class*="pipeline"], [class*="MetricCard"], [class*="metricCard"]) {
  background: linear-gradient(180deg, var(--wilsy-slot-kpi-bg) 0%, var(--wilsy-slot-card-bg-alt) 100%) !important;
  color: var(--wilsy-slot-kpi-text) !important;
  border-color: var(--wilsy-slot-card-border) !important;
}

body[data-wilsy-semantic-theme-runtime] :where([data-wilsy-role~="kpi"], [class*="Kpi"], [class*="KPI"], [class*="kpi"], [class*="Summary"], [class*="summary"], [class*="Readiness"], [class*="readiness"], [class*="Source"], [class*="source"], [class*="Pipeline"], [class*="pipeline"]) * {
  color: var(--wilsy-slot-kpi-text) !important;
  stroke: currentColor !important;
}

body[data-wilsy-semantic-theme-runtime] svg {
  color: currentColor !important;
  stroke: currentColor !important;
}
`;

/**
 * @function applyWilsySemanticThemeRuntime
 * @description Applies semantic Wilsy OS component slots and final runtime CSS to the active document.
 * @param {Object} params - Semantic runtime params.
 * @returns {void}
 * @collaboration Makes every current and future dashboard consume one billion-dollar OS theme contract.
 */
const applyWilsySemanticThemeRuntime = ({ cssVars = {}, themeId = 'wilsy_aurora', modeId = 'night', resolvedModeId = 'night' } = {}) => {
  if (typeof document === 'undefined') return;

  const root = document.documentElement;
  const body = document.body;
  const semanticSlots = buildWilsySemanticThemeSlots({ cssVars, themeId, modeId, resolvedModeId });

  Object.entries(semanticSlots).forEach(([key, value]) => {
    root.style.setProperty(key, String(value));

    if (body) {
      body.style.setProperty(key, String(value));
    }
  });

  root.dataset.wilsySemanticThemeRuntime = WILSY_SEMANTIC_THEME_RUNTIME_VERSION;
  root.dataset.wilsySemanticThemeId = themeId;
  root.dataset.wilsySemanticMode = modeId;
  root.dataset.wilsySemanticResolvedMode = resolvedModeId;

  if (body) {
    body.dataset.wilsySemanticThemeRuntime = WILSY_SEMANTIC_THEME_RUNTIME_VERSION;
    body.dataset.wilsySemanticThemeId = themeId;
    body.dataset.wilsySemanticMode = modeId;
    body.dataset.wilsySemanticResolvedMode = resolvedModeId;
  }

  let styleNode = document.getElementById('wilsy-os-semantic-theme-runtime-style');

  if (!styleNode) {
    styleNode = document.createElement('style');
    styleNode.id = 'wilsy-os-semantic-theme-runtime-style';
    styleNode.setAttribute('data-wilsy-runtime-style', 'semantic-theme-compiler');
    document.head.appendChild(styleNode);
  }

  styleNode.textContent = `${buildWilsySemanticThemeCss()}
${buildWilsySemanticDayModeSurfaceGovernorCss()}`;
};

// WILSY_SEMANTIC_DAY_MODE_SURFACE_GOVERNOR_STEP_R5F_START
/**
 * @function buildWilsySemanticDayModeSurfaceGovernorCss
 * @description Builds semantic day-mode governance CSS so white mode stays enterprise-grade instead of mixing raw white strips into a dark command shell.
 * @returns {string} CSS for role-based day-mode surfaces.
 * @collaboration Uses the Wilsy OS semantic role contract to govern CRM, Account, Executive and future dashboards without dashboard-specific selector firefighting.
 */
const buildWilsySemanticDayModeSurfaceGovernorCss = () => `
html[data-wilsy-theme-resolved-mode="day"],
body[data-wilsy-theme-resolved-mode="day"] {
  --wilsy-day-command-shell: #070b16;
  --wilsy-day-command-shell-2: #0b1220;
  --wilsy-day-workspace: #eef3f8;
  --wilsy-day-surface: #f8fafc;
  --wilsy-day-surface-2: #e8eef6;
  --wilsy-day-text: #0f172a;
  --wilsy-day-muted: #475569;
  --wilsy-day-command-text: #f8fafc;
  --wilsy-day-border: rgba(15, 23, 42, 0.18);
  --wilsy-day-command-border: rgba(248, 250, 252, 0.18);
}

html[data-wilsy-theme-resolved-mode="day"] [data-wilsy-role~="dashboard"],
body[data-wilsy-theme-resolved-mode="day"] [data-wilsy-role~="dashboard"],
html[data-wilsy-theme-resolved-mode="day"] [data-wilsy-role~="canvas"],
body[data-wilsy-theme-resolved-mode="day"] [data-wilsy-role~="canvas"] {
  background:
    radial-gradient(circle at 16% 0%, color-mix(in srgb, var(--wilsy-accent, #d4af37) 11%, transparent) 0%, transparent 36%),
    radial-gradient(circle at 90% 0%, color-mix(in srgb, var(--wilsy-accent-2, #17bdf2) 10%, transparent) 0%, transparent 34%),
    linear-gradient(180deg, var(--wilsy-day-command-shell, #070b16) 0%, #0b1020 42%, var(--wilsy-day-workspace, #eef3f8) 100%) !important;
  color: var(--wilsy-day-command-text, #f8fafc) !important;
}

html[data-wilsy-theme-resolved-mode="day"] [data-wilsy-role~="rail"],
body[data-wilsy-theme-resolved-mode="day"] [data-wilsy-role~="rail"],
html[data-wilsy-theme-resolved-mode="day"] [data-wilsy-role~="sidebar"],
body[data-wilsy-theme-resolved-mode="day"] [data-wilsy-role~="sidebar"],
html[data-wilsy-theme-resolved-mode="day"] [data-wilsy-role~="topbar"],
body[data-wilsy-theme-resolved-mode="day"] [data-wilsy-role~="topbar"],
html[data-wilsy-theme-resolved-mode="day"] [data-wilsy-role~="commandbar"],
body[data-wilsy-theme-resolved-mode="day"] [data-wilsy-role~="commandbar"],
html[data-wilsy-theme-resolved-mode="day"] [data-wilsy-role~="command-rail"],
body[data-wilsy-theme-resolved-mode="day"] [data-wilsy-role~="command-rail"] {
  background:
    linear-gradient(180deg, color-mix(in srgb, var(--wilsy-day-command-shell-2, #0b1220) 92%, transparent) 0%, color-mix(in srgb, var(--wilsy-day-command-shell, #070b16) 96%, transparent) 100%) !important;
  color: var(--wilsy-day-command-text, #f8fafc) !important;
  border-color: var(--wilsy-day-command-border, rgba(248, 250, 252, 0.18)) !important;
  box-shadow: 0 24px 80px rgba(2, 6, 23, 0.34) !important;
}

html[data-wilsy-theme-resolved-mode="day"] [data-wilsy-role~="workspace"],
body[data-wilsy-theme-resolved-mode="day"] [data-wilsy-role~="workspace"] {
  background:
    linear-gradient(180deg, color-mix(in srgb, var(--wilsy-day-workspace, #eef3f8) 96%, transparent) 0%, color-mix(in srgb, var(--wilsy-day-surface, #f8fafc) 98%, transparent) 100%) !important;
  color: var(--wilsy-day-text, #0f172a) !important;
}

html[data-wilsy-theme-resolved-mode="day"] [data-wilsy-role~="card"],
body[data-wilsy-theme-resolved-mode="day"] [data-wilsy-role~="card"],
html[data-wilsy-theme-resolved-mode="day"] [data-wilsy-role~="kpi"],
body[data-wilsy-theme-resolved-mode="day"] [data-wilsy-role~="kpi"] {
  background:
    linear-gradient(180deg, color-mix(in srgb, var(--wilsy-day-surface, #f8fafc) 96%, transparent) 0%, color-mix(in srgb, var(--wilsy-day-surface-2, #e8eef6) 88%, transparent) 100%) !important;
  color: var(--wilsy-day-text, #0f172a) !important;
  border-color: var(--wilsy-day-border, rgba(15, 23, 42, 0.18)) !important;
  box-shadow: 0 18px 44px rgba(15, 23, 42, 0.12) !important;
}

html[data-wilsy-theme-resolved-mode="day"] [data-wilsy-role~="card-header"],
body[data-wilsy-theme-resolved-mode="day"] [data-wilsy-role~="card-header"] {
  background:
    linear-gradient(180deg, color-mix(in srgb, var(--wilsy-day-surface-2, #e8eef6) 96%, transparent) 0%, color-mix(in srgb, var(--wilsy-day-surface, #f8fafc) 92%, transparent) 100%) !important;
  color: var(--wilsy-day-text, #0f172a) !important;
  border-color: var(--wilsy-day-border, rgba(15, 23, 42, 0.18)) !important;
}

html[data-wilsy-theme-resolved-mode="day"] [data-wilsy-role~="control"],
body[data-wilsy-theme-resolved-mode="day"] [data-wilsy-role~="control"],
html[data-wilsy-theme-resolved-mode="day"] [data-wilsy-role~="search"],
body[data-wilsy-theme-resolved-mode="day"] [data-wilsy-role~="search"],
html[data-wilsy-theme-resolved-mode="day"] input,
body[data-wilsy-theme-resolved-mode="day"] input,
html[data-wilsy-theme-resolved-mode="day"] select,
body[data-wilsy-theme-resolved-mode="day"] select,
html[data-wilsy-theme-resolved-mode="day"] textarea,
body[data-wilsy-theme-resolved-mode="day"] textarea {
  background:
    linear-gradient(180deg, #ffffff 0%, color-mix(in srgb, var(--wilsy-day-surface-2, #e8eef6) 86%, #ffffff 14%) 100%) !important;
  color: var(--wilsy-day-text, #0f172a) !important;
  border-color: color-mix(in srgb, var(--wilsy-accent, #d4af37) 36%, rgba(15, 23, 42, 0.22)) !important;
  box-shadow: inset 0 1px 0 rgba(255, 255, 255, 0.82), 0 12px 30px rgba(15, 23, 42, 0.10) !important;
}

html[data-wilsy-theme-resolved-mode="day"] [data-wilsy-role~="button"],
body[data-wilsy-theme-resolved-mode="day"] [data-wilsy-role~="button"],
html[data-wilsy-theme-resolved-mode="day"] button,
body[data-wilsy-theme-resolved-mode="day"] button {
  color: var(--wilsy-day-text, #0f172a) !important;
  border-color: color-mix(in srgb, var(--wilsy-accent, #d4af37) 38%, rgba(15, 23, 42, 0.20)) !important;
}

html[data-wilsy-theme-resolved-mode="day"] [data-wilsy-role~="rail"] button,
body[data-wilsy-theme-resolved-mode="day"] [data-wilsy-role~="rail"] button,
html[data-wilsy-theme-resolved-mode="day"] [data-wilsy-role~="topbar"] button,
body[data-wilsy-theme-resolved-mode="day"] [data-wilsy-role~="topbar"] button,
html[data-wilsy-theme-resolved-mode="day"] [data-wilsy-role~="command-rail"] button,
body[data-wilsy-theme-resolved-mode="day"] [data-wilsy-role~="command-rail"] button {
  background: color-mix(in srgb, var(--wilsy-day-command-shell-2, #0b1220) 74%, var(--wilsy-accent, #d4af37) 10%) !important;
  color: var(--wilsy-day-command-text, #f8fafc) !important;
  border-color: var(--wilsy-day-command-border, rgba(248, 250, 252, 0.18)) !important;
}

html[data-wilsy-theme-resolved-mode="day"] [data-wilsy-role~="badge"],
body[data-wilsy-theme-resolved-mode="day"] [data-wilsy-role~="badge"],
html[data-wilsy-theme-resolved-mode="day"] [data-wilsy-role~="indicator"],
body[data-wilsy-theme-resolved-mode="day"] [data-wilsy-role~="indicator"] {
  background: color-mix(in srgb, var(--wilsy-accent, #d4af37) 18%, #ffffff 82%) !important;
  color: var(--wilsy-day-text, #0f172a) !important;
  border-color: color-mix(in srgb, var(--wilsy-accent, #d4af37) 42%, rgba(15, 23, 42, 0.22)) !important;
}
`;
// WILSY_SEMANTIC_DAY_MODE_SURFACE_GOVERNOR_STEP_R5F_END


// WILSY_SEMANTIC_THEME_RUNTIME_STEP_R5A_END



// WILSY_SEMANTIC_ROLE_STAMPER_STEP_R5B_START
const WILSY_SEMANTIC_ROLE_STAMPER_VERSION = 'R5B-SEMANTIC-ROLE-STAMPER';

const WILSY_SEMANTIC_ROLE_STAMPING_STATE = {
  observer: null,
  frame: null
};

const WILSY_SEMANTIC_ROLE_SELECTOR_PLAN = Object.freeze([
  { selector: '#root, main, [class*="Dashboard"], [class*="dashboard"]', role: 'dashboard canvas' },
  { selector: 'aside, nav, [class*="Sidebar"], [class*="sidebar"], [class*="Rail"], [class*="rail"]', role: 'rail sidebar' },
  { selector: 'header, [class*="Topbar"], [class*="topbar"], [class*="Toolbar"], [class*="toolbar"], [class*="CommandBar"], [class*="commandBar"], [class*="ActionBar"], [class*="actionBar"]', role: 'topbar commandbar' },
  { selector: '[class*="Workspace"], [class*="workspace"], [class*="Canvas"], [class*="canvas"], [class*="Content"], [class*="content"]', role: 'workspace' },
  { selector: '[class*="Card"], [class*="card"], [class*="Panel"], [class*="panel"], [class*="Tile"], [class*="tile"], [class*="Widget"], [class*="widget"], [class*="Table"], [class*="table"]', role: 'card' },
  { selector: '[class*="Kpi"], [class*="KPI"], [class*="kpi"], [class*="Summary"], [class*="summary"], [class*="Readiness"], [class*="readiness"], [class*="Source"], [class*="source"], [class*="Pipeline"], [class*="pipeline"], [class*="MetricCard"], [class*="metricCard"], [class*="StatCard"], [class*="statCard"]', role: 'kpi card' },
  { selector: '[class*="CommandRail"], [class*="commandRail"], [class*="CommandSpine"], [class*="commandSpine"]', role: 'command-rail rail' },
  { selector: '[class*="Search"], [class*="search"]', role: 'search control' },
  { selector: '[class*="Badge"], [class*="badge"], [class*="Pill"], [class*="pill"]', role: 'badge' }
]);

/**
 * @function mergeWilsySemanticRole
 * @description Adds one or more Wilsy OS semantic roles to a DOM element without removing existing roles.
 * @param {Element} element - Target DOM element.
 * @param {string} role - Space-separated semantic roles.
 * @returns {void}
 * @collaboration Lets every dashboard surface opt into the semantic theme compiler dynamically.
 */
const mergeWilsySemanticRole = (element, role) => {
  if (!element || !element.dataset || !role) return;

  const roleSet = new Set(String(element.dataset.wilsyRole || '').split(/\s+/).filter(Boolean));

  String(role).split(/\s+/).filter(Boolean).forEach(token => roleSet.add(token));

  element.dataset.wilsyRole = Array.from(roleSet).join(' ');
};

/**
 * @function stampWilsySemanticSelectorRole
 * @description Applies one semantic role to every element matching a selector.
 * @param {string} selector - Browser selector.
 * @param {string} role - Semantic role.
 * @returns {void}
 * @collaboration Converts existing CRM, Executive and future dashboard DOM into semantic OS surfaces.
 */
const stampWilsySemanticSelectorRole = (selector, role) => {
  if (typeof document === 'undefined' || !selector || !role) return;

  try {
    document.querySelectorAll(selector).forEach(element => mergeWilsySemanticRole(element, role));
  } catch (error) {
    console.warn('[WILSY-SEMANTIC-ROLE-SELECTOR-SKIPPED]', selector, error.message);
  }
};

/**
 * @function stampWilsyCardHeaderRoles
 * @description Stamps first-child header bands inside cards, panels and tiles as semantic card-header surfaces.
 * @returns {void}
 * @collaboration Stops card headers from depending on fragile class names across 20+ dashboards.
 */
const stampWilsyCardHeaderRoles = () => {
  if (typeof document === 'undefined') return;

  document.querySelectorAll('[data-wilsy-role~="card"], [class*="Card"], [class*="card"], [class*="Panel"], [class*="panel"], [class*="Tile"], [class*="tile"]').forEach(container => {
    const firstChild = container.firstElementChild;

    if (!firstChild || firstChild.matches('input, textarea, select, option, svg, path')) return;

    mergeWilsySemanticRole(container, 'card');
    mergeWilsySemanticRole(firstChild, 'card-header');
  });

  document.querySelectorAll('thead, tr[class*="Header"], tr[class*="header"], [class*="CardHeader"], [class*="cardHeader"], [class*="PanelHeader"], [class*="panelHeader"]').forEach(element => {
    mergeWilsySemanticRole(element, 'card-header');
  });
};

/**
 * @function stampWilsyControlRoles
 * @description Stamps buttons, inputs and command controls with semantic roles under topbars and command rails.
 * @returns {void}
 * @collaboration Makes topbar search and action controls inherit OS-grade spacing and contrast.
 */
const stampWilsyControlRoles = () => {
  if (typeof document === 'undefined') return;

  document.querySelectorAll('[data-wilsy-role~="topbar"], header, [class*="Topbar"], [class*="topbar"], [class*="Toolbar"], [class*="toolbar"], [class*="CommandBar"], [class*="commandBar"], [class*="ActionBar"], [class*="actionBar"]').forEach(topbar => {
    topbar.querySelectorAll('button, [role="button"]').forEach(element => mergeWilsySemanticRole(element, 'button control'));
    topbar.querySelectorAll('input, select, textarea, [class*="Search"], [class*="search"]').forEach(element => mergeWilsySemanticRole(element, 'search control'));
  });

  document.querySelectorAll('button, [role="button"]').forEach(element => {
    if (element.closest('[data-wilsy-role~="rail"], aside, nav, [class*="Sidebar"], [class*="sidebar"], [class*="Rail"], [class*="rail"]')) {
      mergeWilsySemanticRole(element, 'rail-item');
    }
  });
};

/**
 * @function stampWilsyRailIndicatorRoles
 * @description Stamps navigation counts, status marks and trailing module indicators as semantic rail indicators.
 * @returns {void}
 * @collaboration Keeps day and night mode rails consistent instead of exposing raw zero-count text.
 */
const stampWilsyRailIndicatorRoles = () => {
  if (typeof document === 'undefined') return;

  document.querySelectorAll('[data-wilsy-role~="rail"], aside, nav, [class*="Sidebar"], [class*="sidebar"], [class*="Rail"], [class*="rail"]').forEach(rail => {
    rail.querySelectorAll('[class*="count"], [class*="Count"], [class*="indicator"], [class*="Indicator"], [class*="status"], [class*="Status"], [class*="dot"], [class*="Dot"]').forEach(element => {
      mergeWilsySemanticRole(element, 'indicator');
    });

    rail.querySelectorAll('button, [role="button"], [data-wilsy-role~="rail-item"]').forEach(item => {
      const lastChild = item.lastElementChild;

      if (!lastChild || lastChild.matches('svg, path')) return;

      const textValue = String(lastChild.textContent || '').trim();
      const isIndicatorLike = textValue === '' || /^[0-9]+$/.test(textValue) || lastChild.offsetWidth <= 28;

      if (isIndicatorLike) {
        mergeWilsySemanticRole(lastChild, 'indicator');
      }
    });
  });
};

/**
 * @function applyWilsySemanticRoleStamps
 * @description Applies Wilsy OS semantic data roles across the currently mounted dashboard DOM.
 * @returns {void}
 * @collaboration Bridges existing dashboards into the new semantic theme runtime without rewriting every dashboard at once.
 */
const applyWilsySemanticRoleStamps = () => {
  if (typeof document === 'undefined') return;

  WILSY_SEMANTIC_ROLE_SELECTOR_PLAN.forEach(item => stampWilsySemanticSelectorRole(item.selector, item.role));
  stampWilsyCardHeaderRoles();
  stampWilsyControlRoles();
  stampWilsyRailIndicatorRoles();

  document.documentElement.dataset.wilsySemanticRoleStamper = WILSY_SEMANTIC_ROLE_STAMPER_VERSION;

  if (document.body) {
    document.body.dataset.wilsySemanticRoleStamper = WILSY_SEMANTIC_ROLE_STAMPER_VERSION;
  }

  publishWilsySemanticRoleCoverage();
};

/**
 * @function scheduleWilsySemanticRoleStamps
 * @description Schedules semantic role stamping after dashboard DOM mutations settle.
 * @returns {void}
 * @collaboration Keeps lazy-loaded dashboards aligned with the theme runtime after route changes.
 */
const scheduleWilsySemanticRoleStamps = () => {
  if (typeof window === 'undefined') return;

  if (WILSY_SEMANTIC_ROLE_STAMPING_STATE.frame) {
    window.cancelAnimationFrame(WILSY_SEMANTIC_ROLE_STAMPING_STATE.frame);
  }

  WILSY_SEMANTIC_ROLE_STAMPING_STATE.frame = window.requestAnimationFrame(() => {
    WILSY_SEMANTIC_ROLE_STAMPING_STATE.frame = null;
    applyWilsySemanticRoleStamps();
  });
};

/**
 * @function observeWilsySemanticRoleStamps
 * @description Observes dashboard DOM changes and re-applies semantic roles for lazy-mounted surfaces.
 * @returns {void}
 * @collaboration Makes the OS theme contract durable across CRM, Executive and future dashboard transitions.
 */
const observeWilsySemanticRoleStamps = () => {
  if (typeof window === 'undefined' || typeof MutationObserver === 'undefined' || !document.body) return;
  if (WILSY_SEMANTIC_ROLE_STAMPING_STATE.observer) return;

  WILSY_SEMANTIC_ROLE_STAMPING_STATE.observer = new MutationObserver(() => {
    scheduleWilsySemanticRoleStamps();
  });

  WILSY_SEMANTIC_ROLE_STAMPING_STATE.observer.observe(document.body, {
    childList: true,
    subtree: true
  });
};
// WILSY_SEMANTIC_ROLE_STAMPER_STEP_R5B_END



// WILSY_SEMANTIC_ROLE_COVERAGE_GATE_STEP_R5C_START
const WILSY_SEMANTIC_ROLE_COVERAGE_VERSION = 'R5C-SEMANTIC-ROLE-COVERAGE-GATE';

const WILSY_REQUIRED_SEMANTIC_ROLES = Object.freeze([
  'dashboard',
  'canvas',
  'rail',
  'topbar',
  'workspace',
  'card',
  'card-header',
  'search',
  'control'
]);

/**
 * @function collectWilsySemanticRoleCoverage
 * @description Collects live semantic role counts from the mounted dashboard DOM.
 * @returns {Object} Semantic role coverage report.
 * @collaboration Gives Wilsy OS an investor-grade runtime audit for all dashboard theme surfaces.
 */
const collectWilsySemanticRoleCoverage = () => {
  if (typeof document === 'undefined') {
    return {
      version: WILSY_SEMANTIC_ROLE_COVERAGE_VERSION,
      ok: false,
      reason: 'document_unavailable',
      totalRoleStampedNodes: 0,
      roles: {},
      missingRequiredRoles: [...WILSY_REQUIRED_SEMANTIC_ROLES]
    };
  }

  const roleNodes = Array.from(document.querySelectorAll('[data-wilsy-role]'));
  const roles = roleNodes.reduce((accumulator, element) => {
    String(element.dataset.wilsyRole || '')
      .split(/\s+/)
      .filter(Boolean)
      .forEach(role => {
        accumulator[role] = (accumulator[role] || 0) + 1;
      });

    return accumulator;
  }, {});

  const missingRequiredRoles = WILSY_REQUIRED_SEMANTIC_ROLES.filter(role => !roles[role]);

  return {
    version: WILSY_SEMANTIC_ROLE_COVERAGE_VERSION,
    ok: missingRequiredRoles.length === 0,
    themeRuntime: document.body?.dataset?.wilsyThemeRuntime || '',
    semanticRuntime: document.body?.dataset?.wilsySemanticThemeRuntime || '',
    roleStamper: document.body?.dataset?.wilsySemanticRoleStamper || '',
    totalRoleStampedNodes: roleNodes.length,
    roles,
    missingRequiredRoles,
    slotPreview: {
      cardText: getComputedStyle(document.documentElement).getPropertyValue('--wilsy-slot-card-text').trim(),
      cardHeaderText: getComputedStyle(document.documentElement).getPropertyValue('--wilsy-slot-card-header-text').trim(),
      railText: getComputedStyle(document.documentElement).getPropertyValue('--wilsy-slot-rail-text').trim(),
      topbarText: getComputedStyle(document.documentElement).getPropertyValue('--wilsy-slot-topbar-text').trim(),
      controlText: getComputedStyle(document.documentElement).getPropertyValue('--wilsy-slot-control-text').trim()
    }
  };
};

/**
 * @function publishWilsySemanticRoleCoverage
 * @description Publishes the semantic role coverage report to body datasets and a browser global for diagnostics.
 * @returns {Object} Semantic role coverage report.
 * @collaboration Prevents future Wilsy OS dashboards from shipping with silent theme contract gaps.
 */
const publishWilsySemanticRoleCoverage = () => {
  const report = collectWilsySemanticRoleCoverage();

  if (typeof window !== 'undefined') {
    window.__WILSY_SEMANTIC_ROLE_COVERAGE__ = report;
  }

  if (typeof document !== 'undefined') {
    document.documentElement.dataset.wilsySemanticRoleCoverage = WILSY_SEMANTIC_ROLE_COVERAGE_VERSION;
    document.documentElement.dataset.wilsySemanticRoleHealth = report.ok ? 'pass' : 'degraded';
    document.documentElement.dataset.wilsySemanticRoleCount = String(report.totalRoleStampedNodes);

    if (document.body) {
      document.body.dataset.wilsySemanticRoleCoverage = WILSY_SEMANTIC_ROLE_COVERAGE_VERSION;
      document.body.dataset.wilsySemanticRoleHealth = report.ok ? 'pass' : 'degraded';
      document.body.dataset.wilsySemanticRoleCount = String(report.totalRoleStampedNodes);
    }
  }

  if (!report.ok && typeof console !== 'undefined') {
    console.warn('[WILSY-SEMANTIC-ROLE-COVERAGE-DEGRADED]', report);
  }

  return report;
};
// WILSY_SEMANTIC_ROLE_COVERAGE_GATE_STEP_R5C_END


/**
 * @function applyWilsyThemeRuntime
 * @description Applies selected Wilsy OS account theme tokens to the document, body and global dashboard repaint layer.
 * @param {Object} params - Runtime theme packet.
 * @returns {void}
 * @collaboration Gives Wilsy OS a single repaint path for Account, CRM and future dashboard shells.
 */
export const applyWilsyThemeRuntime = ({ theme, effectiveMode, resolvedMode, tokens, mode 
} = {}) => {
  if (typeof document === 'undefined') return;

  const root = document.documentElement;
  const body = document.body;
  const cssVars = tokens?.cssVars || tokens || {};
  const themeId = theme?.id || cssVars['--wilsy-theme-id'] || root.dataset.wilsyTheme || 'wilsy_aurora';
  const modeId = effectiveMode || mode || cssVars['--wilsy-theme-mode'] || 'night';
  const resolvedModeId = resolvedMode || cssVars['--wilsy-theme-resolved-mode'] || modeId;

  Object.entries(cssVars).forEach(([key, value]) => {
    if (!key || typeof key !== 'string') return;

    root.style.setProperty(key, String(value ?? ''));

    if (body) {
      body.style.setProperty(key, String(value ?? ''));
    }
  });

  root.dataset.wilsyTheme = themeId;
  root.dataset.wilsyThemeMode = modeId;
  root.dataset.wilsyThemeResolvedMode = resolvedModeId;
  root.dataset.wilsyThemeRuntime = themeId;

  if (body) {
    body.dataset.wilsyTheme = themeId;
    body.dataset.wilsyThemeMode = modeId;
    body.dataset.wilsyThemeResolvedMode = resolvedModeId;
    body.dataset.wilsyThemeRuntime = themeId;
  }

  // WILSY_GLOBAL_THEME_RUNTIME_STYLE_INJECTION_STEP_R4I
  try {
    const styleId = 'wilsy-os-global-theme-runtime-style';
    const runtimeCss = `
html[data-wilsy-theme-runtime],
body[data-wilsy-theme-runtime] {
  background:
    radial-gradient(circle at 12% 0%, color-mix(in srgb, var(--wilsy-accent-2, #17bdf2) 18%, transparent) 0%, transparent 35%),
    radial-gradient(circle at 88% 8%, color-mix(in srgb, var(--wilsy-accent, #d4af37) 14%, transparent) 0%, transparent 34%),
    linear-gradient(180deg, var(--wilsy-bg, #020306) 0%, color-mix(in srgb, var(--wilsy-bg, #020306) 94%, #000 6%) 100%) !important;
  color: var(--wilsy-text, #fffaf0) !important;
}

body[data-wilsy-theme-runtime] #root,
body[data-wilsy-theme-runtime] [class*="Dashboard"],
body[data-wilsy-theme-runtime] [class*="dashboard"],
body[data-wilsy-theme-runtime] [class*="CRM"],
body[data-wilsy-theme-runtime] [class*="crm"] {
  background:
    radial-gradient(circle at 8% 0%, color-mix(in srgb, var(--wilsy-accent-2, #17bdf2) 15%, transparent) 0%, transparent 32%),
    radial-gradient(circle at 92% 8%, color-mix(in srgb, var(--wilsy-accent, #d4af37) 12%, transparent) 0%, transparent 36%),
    linear-gradient(180deg, var(--crm-bg, var(--wilsy-bg, #020306)) 0%, var(--wilsy-bg, #020306) 100%) !important;
  color: var(--wilsy-text, #fffaf0) !important;
  border-color: var(--wilsy-border-color, rgba(212, 175, 55, 0.28)) !important;
  transition: background 220ms ease, color 220ms ease, border-color 220ms ease, box-shadow 220ms ease;
}

body[data-wilsy-theme-runtime] [class*="Sidebar"],
body[data-wilsy-theme-runtime] [class*="sidebar"],
body[data-wilsy-theme-runtime] [class*="Rail"],
body[data-wilsy-theme-runtime] [class*="rail"],
body[data-wilsy-theme-runtime] [class*="Navigation"],
body[data-wilsy-theme-runtime] [class*="navigation"] {
  background:
    radial-gradient(circle at 50% 0%, color-mix(in srgb, var(--wilsy-accent, #d4af37) 14%, transparent) 0%, transparent 42%),
    linear-gradient(180deg, var(--wilsy-rail, rgba(3, 5, 10, 0.96)) 0%, var(--wilsy-bg, #020306) 100%) !important;
  color: var(--wilsy-text, #fffaf0) !important;
  border-color: var(--wilsy-border-color, rgba(212, 175, 55, 0.28)) !important;
}

body[data-wilsy-theme-runtime] [class*="Top"],
body[data-wilsy-theme-runtime] [class*="top"],
body[data-wilsy-theme-runtime] [class*="Header"],
body[data-wilsy-theme-runtime] [class*="header"],
body[data-wilsy-theme-runtime] [class*="Toolbar"],
body[data-wilsy-theme-runtime] [class*="toolbar"] {
  background:
    linear-gradient(135deg, color-mix(in srgb, var(--wilsy-rail, #05070d) 92%, transparent) 0%, color-mix(in srgb, var(--wilsy-surface, #080c18) 96%, transparent) 100%) !important;
  color: var(--wilsy-text, #fffaf0) !important;
  border-color: var(--wilsy-border-color, rgba(212, 175, 55, 0.28)) !important;
}

body[data-wilsy-theme-runtime] [class*="Workspace"],
body[data-wilsy-theme-runtime] [class*="workspace"],
body[data-wilsy-theme-runtime] [class*="Canvas"],
body[data-wilsy-theme-runtime] [class*="canvas"],
body[data-wilsy-theme-runtime] [class*="Content"],
body[data-wilsy-theme-runtime] [class*="content"] {
  background:
    radial-gradient(circle at 0% 0%, color-mix(in srgb, var(--wilsy-accent-2, #17bdf2) 10%, transparent) 0%, transparent 35%),
    linear-gradient(180deg, var(--crm-surface, var(--wilsy-surface, #05070d)) 0%, var(--wilsy-bg, #020306) 100%) !important;
  color: var(--wilsy-text, #fffaf0) !important;
}

body[data-wilsy-theme-runtime] [class*="Panel"],
body[data-wilsy-theme-runtime] [class*="panel"],
body[data-wilsy-theme-runtime] [class*="Card"],
body[data-wilsy-theme-runtime] [class*="card"],
body[data-wilsy-theme-runtime] [class*="Tile"],
body[data-wilsy-theme-runtime] [class*="tile"],
body[data-wilsy-theme-runtime] [class*="Metric"],
body[data-wilsy-theme-runtime] [class*="metric"],
body[data-wilsy-theme-runtime] [class*="Table"],
body[data-wilsy-theme-runtime] [class*="table"] {
  background:
    radial-gradient(circle at 0% 0%, color-mix(in srgb, var(--wilsy-accent-2, #17bdf2) 9%, transparent) 0%, transparent 40%),
    linear-gradient(180deg, color-mix(in srgb, var(--crm-card, var(--wilsy-card, #080c18)) 96%, transparent) 0%, color-mix(in srgb, var(--crm-surface, var(--wilsy-surface, #05070d)) 98%, transparent) 100%) !important;
  color: var(--wilsy-text, #fffaf0) !important;
  border-color: var(--wilsy-border-color, rgba(212, 175, 55, 0.28)) !important;
  box-shadow: 0 18px 48px color-mix(in srgb, var(--wilsy-accent, #d4af37) 11%, transparent) !important;
}

body[data-wilsy-theme-runtime] h1,
body[data-wilsy-theme-runtime] h2,
body[data-wilsy-theme-runtime] h3,
body[data-wilsy-theme-runtime] h4,
body[data-wilsy-theme-runtime] strong {
  color: var(--wilsy-text, #fffaf0) !important;
}

body[data-wilsy-theme-runtime] button,
body[data-wilsy-theme-runtime] input,
body[data-wilsy-theme-runtime] select,
body[data-wilsy-theme-runtime] textarea {
  border-color: var(--wilsy-border-color, rgba(212, 175, 55, 0.28)) !important;
}
`;

    let styleNode = document.getElementById(styleId);

    if (!styleNode) {
      styleNode = document.createElement('style');
      styleNode.id = styleId;
      styleNode.setAttribute('data-wilsy-runtime-style', 'global-theme-repaint');
      document.head.appendChild(styleNode);
    }

    styleNode.textContent = `${runtimeCss}\n${buildWilsyDashboardReadabilityCss()}\n${buildWilsyDashboardTitleContrastCss()}\n${buildWilsyDashboardRailConsistencyCss()}\n${buildWilsyDashboardHeroAndMetricContrastCss()}\n${buildWilsyDashboardTopCommandControlsCss()}`;
  } catch (globalThemeRuntimeError) {
    console.warn('[WILSY-GLOBAL-THEME-RUNTIME-SKIPPED]', globalThemeRuntimeError.message);
  }

  // WILSY_SEMANTIC_THEME_RUNTIME_CALL_STEP_R5A_FIX
  applyWilsySemanticThemeRuntime({ cssVars, themeId, modeId, resolvedModeId });
  publishWilsySemanticRoleCoverage();
  // WILSY_SEMANTIC_ROLE_STAMPER_CALL_STEP_R5B_FIX_START
  applyWilsySemanticRoleStamps();
  scheduleWilsySemanticRoleStamps();
  observeWilsySemanticRoleStamps();

  if (typeof window !== 'undefined') {
    window.setTimeout(() => {
      applyWilsySemanticRoleStamps();
    }, 0);
  }
  // WILSY_SEMANTIC_ROLE_STAMPER_CALL_STEP_R5B_FIX_END
};

/**
 * @function dispatchWilsyThemeRuntime
 * @description Broadcasts a Wilsy OS theme runtime packet on the browser event bus.
 * @param {Object} packet - Runtime packet.
 * @returns {void}
 * @collaboration Lets dashboards repaint immediately without coupling to the Account Command Center internals.
 */
export const dispatchWilsyThemeRuntime = packet => {
  if (typeof window === 'undefined' || !packet) return;

  const detail = {
    themeId: packet.themeId,
    mode: packet.mode,
    resolvedMode: packet.resolvedMode,
    accent: packet.theme?.accent,
    secondary: packet.theme?.secondary,
    highlight: packet.theme?.highlight,
    live: packet.theme?.live,
    skin: packet.theme,
    tokens: packet.tokens?.cssVars || {},
    source: packet.source,
    themeVersion: packet.themeVersion,
    registryVersion: packet.registryVersion,
    emittedAt: packet.emittedAt
  };

  window.dispatchEvent(new CustomEvent(WILSY_THEME_RUNTIME_EVENTS.global, { detail }));
  window.dispatchEvent(new CustomEvent(WILSY_THEME_RUNTIME_EVENTS.account, { detail }));
  window.dispatchEvent(new CustomEvent(WILSY_THEME_RUNTIME_EVENTS.committed, { detail }));
};

/**
 * @function commitWilsyThemeRuntime
 * @description Builds, persists, applies and broadcasts a Wilsy OS runtime theme packet.
 * @param {Object|string} input - Theme runtime input.
 * @param {Object} options - Runtime options.
 * @returns {Object} Committed runtime packet.
 * @collaboration Provides the one-command OS theme bus that future dashboards and tenants can call.
 */
export const commitWilsyThemeRuntime = (input = {}, options = {}) => {
  const packet = buildWilsyThemeRuntimePacket(input, options);

  if (options.persist !== false) persistWilsyThemeRuntime(packet);
  if (options.apply !== false) {
    applyWilsyThemeRuntime({
      theme: packet.theme,
      effectiveMode: packet.mode,
      resolvedMode: packet.resolvedMode,
      tokens: packet.tokens
    });
  }
  if (options.dispatch !== false) dispatchWilsyThemeRuntime(packet);

  return packet;
};

/**
 * @function subscribeWilsyThemeRuntime
 * @description Subscribes to Wilsy OS theme runtime changes.
 * @param {Function} callback - Runtime event callback.
 * @returns {Function} Unsubscribe function.
 * @collaboration Gives Executive, CRM, TopRail and future tenant shells a stable subscription API.
 */
export const subscribeWilsyThemeRuntime = callback => {
  if (typeof window === 'undefined' || typeof callback !== 'function') return () => {};

  /**
   * @function handleWilsyThemeRuntimeEvent
   * @description Normalizes browser CustomEvent payloads before notifying a Wilsy OS theme runtime subscriber.
   * @param {CustomEvent} event - Browser theme runtime event.
   * @returns {void}
   * @collaboration Keeps dashboard subscribers decoupled from raw browser event details while satisfying Wilsy documentation guard rules.
   */
  const handleWilsyThemeRuntimeEvent = event => callback(event.detail || {});
  window.addEventListener(WILSY_THEME_RUNTIME_EVENTS.global, handleWilsyThemeRuntimeEvent);
  window.addEventListener(WILSY_THEME_RUNTIME_EVENTS.committed, handleWilsyThemeRuntimeEvent);

  return () => {
    window.removeEventListener(WILSY_THEME_RUNTIME_EVENTS.global, handleWilsyThemeRuntimeEvent);
    window.removeEventListener(WILSY_THEME_RUNTIME_EVENTS.committed, handleWilsyThemeRuntimeEvent);
  };
};

/**
 * @function validateVisualTokens
 * @description Validates the token packet emitted by buildVisualTokens.
 * @param {Object} tokens - Token packet.
 * @returns {Array<string>} Validation issues.
 * @collaboration Stops incomplete visual tokens before they become broken dashboard UI.
 */
export const validateVisualTokens = tokens => {
  const issues = [];

  REQUIRED_TOKEN_KEYS.forEach(key => {
    if (tokens?.[key] === undefined || tokens?.[key] === null) {
      issues.push(`missing token key ${key}`);
    }
  });

  if (!tokens?.cssVars || Object.keys(tokens.cssVars).length < 20) {
    issues.push('cssVars contract below minimum semantic token count');
  }

  if (tokens?.isDay && tokens?.resolvedMode !== 'day') {
    issues.push('isDay true while resolvedMode is not day');
  }

  if (!tokens?.isDay && tokens?.resolvedMode !== 'night') {
    issues.push('isDay false while resolvedMode is not night');
  }

  return issues;
};

/**
 * @function assertWilsyThemeTokenEngine
 * @description Validates the full token engine across all registered operating skins and modes.
 * @returns {Object} Token engine health object.
 * @collaboration Gives guard scripts and future tests a deterministic proof of OS-grade theme readiness.
 */
export const assertWilsyThemeTokenEngine = () => {
  const issues = [];

  DEFAULT_OPERATING_SKINS.forEach(theme => {
    ['day', 'night'].forEach(mode => {
      const tokens = buildVisualTokens(theme, mode, { effectiveMode: mode });
      validateVisualTokens(tokens).forEach(issue => {
        issues.push(`${theme.id}:${mode}:${issue}`);
      });
    });
  });

  if (!WILSY_OPERATING_SKIN_IDS.includes('wilsy_aurora')) {
    issues.push('default skin wilsy_aurora is missing');
  }

  return Object.freeze({
    ok: issues.length === 0,
    version: WILSY_ACCOUNT_THEME_VERSION,
    registryVersion: WILSY_OPERATING_SKINS_VERSION,
    skinCount: DEFAULT_OPERATING_SKINS.length,
    modeCount: MODE_KEYS.length,
    issues: Object.freeze(issues)
  });
};

export const WILSY_ACCOUNT_THEME_ENGINE_HEALTH = assertWilsyThemeTokenEngine();

export default buildVisualTokens;
