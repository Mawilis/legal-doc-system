/* eslint-disable */
import * as wilsyOperatingSkins from '../../account/wilsyOperatingSkins.js';

export const WILSY_CRM_THEME_ENGINE_BRIDGE_VERSION = 'R67A-CRM-THEME-ENGINE-AUTHORITY-BRIDGE';
export const WILSY_CRM_FORENSIC_VIOLET_HEADER_LOCK_VERSION = 'R67F-FORENSIC-VIOLET-HEADER-TOKEN-LOCK';
export const WILSY_CRM_THEME_PRESET_AUTHORITY_VERSION = 'R67E-HEADER-THEME-TOKEN-AUTHORITY';

const FALLBACK_CRM_THEME_OPTIONS = Object.freeze([
  {
    id: 'WILSY_NEBULA_COMMAND',
    label: 'NEBULA',
    source: 'crm-fallback',
    className: '',
    cssVars: {
      '--lead-bg': '#050505',
      '--lead-card': 'rgba(13, 13, 13, 0.96)',
      '--lead-card-strong': 'rgba(18, 18, 18, 0.98)',
      '--lead-inner': 'rgba(8, 8, 8, 0.98)',
      '--lead-border': 'rgba(115, 115, 115, 0.42)',
      '--lead-border-soft': 'rgba(64, 64, 64, 0.7)',
      '--lead-muted': 'rgba(163, 163, 163, 0.82)',
      '--lead-muted-dim': 'rgba(115, 115, 115, 0.72)',
      '--lead-text': '#f5f5f5',
      '--lead-accent': '#22c55e',
      '--lead-accent-soft': 'rgba(34, 197, 94, 0.14)',
      '--lead-gold': '#efe7a5',
      '--lead-warning': '#f59e0b',
      '--lead-primary': 'linear-gradient(135deg, #f4f1a2 0%, #22c55e 70%, #16a34a 100%)'
    }
  },
  {
    id: 'WILSY_AURORA',
    label: 'AURORA',
    source: 'crm-fallback',
    className: '',
    cssVars: {
      '--lead-bg': '#07111f',
      '--lead-card': 'rgba(255, 255, 255, 0.06)',
      '--lead-card-strong': 'rgba(255, 255, 255, 0.08)',
      '--lead-inner': 'rgba(255, 255, 255, 0.04)',
      '--lead-border': 'rgba(125, 211, 252, 0.26)',
      '--lead-border-soft': 'rgba(255, 255, 255, 0.12)',
      '--lead-muted': 'rgba(203, 213, 225, 0.74)',
      '--lead-muted-dim': 'rgba(148, 163, 184, 0.58)',
      '--lead-text': '#eef8ff',
      '--lead-accent': '#67e8f9',
      '--lead-accent-soft': 'rgba(103, 232, 249, 0.12)',
      '--lead-gold': '#bae6fd',
      '--lead-warning': '#fbbf24',
      '--lead-primary': 'linear-gradient(135deg, #67e8f9 0%, #60a5fa 100%)'
    }
  },
  {
    id: 'WILSY_BLACK',
    label: 'BLACK',
    source: 'crm-fallback',
    className: '',
    cssVars: {
      '--lead-bg': '#020202',
      '--lead-card': 'rgba(10, 10, 10, 0.98)',
      '--lead-card-strong': 'rgba(16, 16, 16, 0.98)',
      '--lead-inner': 'rgba(0, 0, 0, 0.98)',
      '--lead-border': 'rgba(250, 240, 190, 0.24)',
      '--lead-border-soft': 'rgba(250, 240, 190, 0.12)',
      '--lead-muted': 'rgba(212, 212, 212, 0.76)',
      '--lead-muted-dim': 'rgba(163, 163, 163, 0.56)',
      '--lead-text': '#fafafa',
      '--lead-accent': '#d4af37',
      '--lead-accent-soft': 'rgba(212, 175, 55, 0.14)',
      '--lead-gold': '#f8e7a1',
      '--lead-warning': '#fbbf24',
      '--lead-primary': 'linear-gradient(135deg, #f8e7a1 0%, #d4af37 100%)'
    }
  },
  {
    id: 'WILSY_COBALT',
    label: 'COBALT',
    source: 'crm-fallback',
    className: '',
    cssVars: {
      '--lead-bg': '#06101f',
      '--lead-card': 'rgba(15, 23, 42, 0.96)',
      '--lead-card-strong': 'rgba(30, 41, 59, 0.96)',
      '--lead-inner': 'rgba(2, 6, 23, 0.98)',
      '--lead-border': 'rgba(96, 165, 250, 0.32)',
      '--lead-border-soft': 'rgba(96, 165, 250, 0.16)',
      '--lead-muted': 'rgba(191, 219, 254, 0.76)',
      '--lead-muted-dim': 'rgba(147, 197, 253, 0.54)',
      '--lead-text': '#eff6ff',
      '--lead-accent': '#60a5fa',
      '--lead-accent-soft': 'rgba(96, 165, 250, 0.14)',
      '--lead-gold': '#dbeafe',
      '--lead-warning': '#facc15',
      '--lead-primary': 'linear-gradient(135deg, #93c5fd 0%, #2563eb 100%)'
    }
  },
  {
    id: 'WILSY_PEARL',
    label: 'PEARL',
    source: 'crm-fallback',
    className: '',
    cssVars: {
      '--lead-bg': '#f8fafc',
      '--lead-card': 'rgba(255, 255, 255, 0.96)',
      '--lead-card-strong': 'rgba(255, 255, 255, 0.99)',
      '--lead-inner': 'rgba(248, 250, 252, 0.98)',
      '--lead-border': 'rgba(15, 23, 42, 0.18)',
      '--lead-border-soft': 'rgba(15, 23, 42, 0.1)',
      '--lead-muted': 'rgba(71, 85, 105, 0.8)',
      '--lead-muted-dim': 'rgba(100, 116, 139, 0.64)',
      '--lead-text': '#0f172a',
      '--lead-accent': '#166534',
      '--lead-accent-soft': 'rgba(22, 101, 52, 0.12)',
      '--lead-gold': '#8a6d1d',
      '--lead-warning': '#b45309',
      '--lead-primary': 'linear-gradient(135deg, #f8e7a1 0%, #22c55e 100%)'
    }
  },
  {
    id: 'WILSY_GOLD',
    label: 'GOLD',
    source: 'crm-fallback',
    className: '',
    cssVars: {
      '--lead-bg': '#0d0801',
      '--lead-card': 'rgba(24, 16, 4, 0.96)',
      '--lead-card-strong': 'rgba(34, 24, 8, 0.98)',
      '--lead-inner': 'rgba(10, 7, 2, 0.98)',
      '--lead-border': 'rgba(250, 204, 21, 0.32)',
      '--lead-border-soft': 'rgba(250, 204, 21, 0.16)',
      '--lead-muted': 'rgba(254, 243, 199, 0.78)',
      '--lead-muted-dim': 'rgba(217, 119, 6, 0.68)',
      '--lead-text': '#fff7ed',
      '--lead-accent': '#facc15',
      '--lead-accent-soft': 'rgba(250, 204, 21, 0.14)',
      '--lead-gold': '#fef3c7',
      '--lead-warning': '#fb923c',
      '--lead-primary': 'linear-gradient(135deg, #fef08a 0%, #f59e0b 100%)'
    }
  }
]);

/**
 * @function normalizeThemeId
 * @description Normalizes any skin identifier into a stable CRM theme id.
 * @param {string} value - Raw id.
 * @returns {string} Normalized id.
 * @collaboration Keeps Account skin engine names stable inside the CRM workspace.
 */
export function normalizeThemeId(value = '') {
  return String(value || 'WILSY_NEBULA_COMMAND')
    .replace(/([a-z0-9])([A-Z])/g, '$1_$2')
    .replace(/[^a-zA-Z0-9]+/g, '_')
    .replace(/^_+|_+$/g, '')
    .toUpperCase();
}

/**
 * @function normalizeCssVariableName
 * @description Converts a token key into a CSS custom property name.
 * @param {string} key - Token key.
 * @returns {string} CSS variable name.
 * @collaboration Lets future Account skin tokens flow into CRM without layout rewrites.
 */
export function normalizeCssVariableName(key = '') {
  if (String(key).startsWith('--')) return String(key);

  return `--lead-engine-${String(key)
    .replace(/([a-z0-9])([A-Z])/g, '$1-$2')
    .replace(/[^a-zA-Z0-9]+/g, '-')
    .replace(/^-+|-+$/g, '')
    .toLowerCase()}`;
}

/**
 * @function mapKnownThemeToken
 * @description Maps known design-token keys into Lead cockpit CSS variables.
 * @param {string} key - Token key.
 * @param {string|number} value - Token value.
 * @returns {Object} CSS variable packet.
 * @collaboration Aligns CRM Lead cockpit styling to shared Wilsy OS design tokens.
 */
export function mapKnownThemeToken(key = '', value = '') {
  const normalized = String(key).replace(/^--/, '').replace(/[_\s]+/g, '-').toLowerCase();
  const mapped = {};

  const tokenMap = {
    'bg': '--lead-bg',
    'background': '--lead-bg',
    'surface': '--lead-card',
    'card': '--lead-card',
    'panel': '--lead-card-strong',
    'inner': '--lead-inner',
    'border': '--lead-border',
    'border-soft': '--lead-border-soft',
    'text': '--lead-text',
    'text-primary': '--lead-text',
    'muted': '--lead-muted',
    'text-muted': '--lead-muted',
    'accent': '--lead-accent',
    'primary': '--lead-accent',
    'gold': '--lead-gold',
    'warning': '--lead-warning'
  };

  if (tokenMap[normalized]) {
    mapped[tokenMap[normalized]] = String(value);
  }

  mapped[normalizeCssVariableName(key)] = String(value);
  return mapped;
}

/**
 * @function normalizeThemeTokenMap
 * @description Converts skin token maps into React style CSS variables.
 * @param {Object} tokens - Skin tokens.
 * @returns {Object} React style object.
 * @collaboration Keeps theme token ingestion isolated from Lead layout code.
 */
export function normalizeThemeTokenMap(tokens = {}) {
  if (!tokens || typeof tokens !== 'object') return {};

  return Object.entries(tokens).reduce((accumulator, [key, value]) => {
    if (value === null || value === undefined) return accumulator;

    if (['string', 'number'].includes(typeof value)) {
      return {
        ...accumulator,
        ...mapKnownThemeToken(key, value)
      };
    }

    return accumulator;
  }, {});
}

/**
 * @function isThemeLikeEntry
 * @description Determines whether an object resembles a skin/theme entry.
 * @param {Object} entry - Candidate entry.
 * @returns {boolean} True when candidate appears theme-like.
 * @collaboration Prevents random token strings from becoming fake skin options.
 */
export function isThemeLikeEntry(entry = {}) {
  if (!entry || typeof entry !== 'object') return false;

  return Boolean(
    entry.id ||
    entry.key ||
    entry.name ||
    entry.label ||
    entry.slug ||
    entry.shortLabel ||
    entry.tokens ||
    entry.cssVars ||
    entry.variables ||
    entry.themeTokens ||
    entry.palette ||
    entry.colors ||
    entry.className ||
    entry.cssClass ||
    entry.skinClass
  );
}

/**
 * @function extractThemeEngineEntries
 * @description Extracts skin-like entries from the shared Wilsy operating skin namespace.
 * @param {Object} moduleNamespace - Imported wilsyOperatingSkins namespace.
 * @returns {Array} Candidate skin entries.
 * @collaboration Uses the Account skin engine as CRM theme authority without editing the Account file.
 */
export function extractThemeEngineEntries(moduleNamespace = {}) {
  const entries = [];

  Object.values(moduleNamespace).forEach(value => {
    if (!value) return;

    if (Array.isArray(value)) {
      value.filter(isThemeLikeEntry).forEach(entry => entries.push(entry));
      return;
    }

    if (isThemeLikeEntry(value)) {
      entries.push(value);
      return;
    }

    if (typeof value === 'object') {
      Object.entries(value).forEach(([key, nested]) => {
        if (Array.isArray(nested)) {
          nested.filter(isThemeLikeEntry).forEach(entry => entries.push(entry));
          return;
        }

        if (isThemeLikeEntry(nested)) {
          entries.push({ id: key, ...nested });
        }
      });
    }
  });

  return entries;
}


/**
 * @function getCrmThemePresetCssVars
 * @description Resolves opinionated CRM cockpit CSS variables for known Wilsy skin ids.
 * @param {string} id - Normalized theme id.
 * @param {string} label - Theme label.
 * @returns {Object} CSS variable packet.
 * @collaboration Makes theme selection change real Lead cockpit surfaces, typography, borders and active glow.
 */
export function getCrmThemePresetCssVars(id = '', label = '') {
  const key = normalizeThemeId(`${id}_${label}`);

  const presets = {
    NEBULA: {
      '--lead-bg': '#050807',
      '--lead-card': 'rgba(13, 16, 14, 0.97)',
      '--lead-card-strong': 'rgba(18, 22, 20, 0.99)',
      '--lead-inner': 'rgba(3, 6, 5, 0.98)',
      '--lead-border': 'rgba(121, 255, 161, 0.34)',
      '--lead-border-soft': 'rgba(121, 255, 161, 0.15)',
      '--lead-muted': 'rgba(204, 214, 208, 0.78)',
      '--lead-muted-dim': 'rgba(132, 145, 138, 0.62)',
      '--lead-text': '#f8fff9',
      '--lead-accent': '#21d86d',
      '--lead-accent-soft': 'rgba(33, 216, 109, 0.16)',
      '--lead-gold': '#efe7a5',
      '--lead-warning': '#facc15',
      '--lead-primary': 'linear-gradient(135deg, #e8f79c 0%, #22c55e 72%, #11a64b 100%)'
    },
    AURORA: {
      '--lead-bg': '#06111f',
      '--lead-card': 'rgba(10, 18, 30, 0.96)',
      '--lead-card-strong': 'rgba(13, 26, 42, 0.98)',
      '--lead-inner': 'rgba(5, 11, 20, 0.98)',
      '--lead-border': 'rgba(103, 232, 249, 0.32)',
      '--lead-border-soft': 'rgba(103, 232, 249, 0.15)',
      '--lead-muted': 'rgba(203, 213, 225, 0.78)',
      '--lead-muted-dim': 'rgba(148, 163, 184, 0.62)',
      '--lead-text': '#f2fbff',
      '--lead-accent': '#67e8f9',
      '--lead-accent-soft': 'rgba(103, 232, 249, 0.16)',
      '--lead-gold': '#dbeafe',
      '--lead-warning': '#facc15',
      '--lead-primary': 'linear-gradient(135deg, #7dd3fc 0%, #22c55e 100%)'
    },
    BLACK: {
      '--lead-bg': '#030303',
      '--lead-card': 'rgba(9, 9, 9, 0.98)',
      '--lead-card-strong': 'rgba(14, 14, 14, 0.99)',
      '--lead-inner': 'rgba(0, 0, 0, 0.98)',
      '--lead-border': 'rgba(250, 240, 190, 0.28)',
      '--lead-border-soft': 'rgba(250, 240, 190, 0.13)',
      '--lead-muted': 'rgba(212, 212, 212, 0.76)',
      '--lead-muted-dim': 'rgba(140, 140, 140, 0.62)',
      '--lead-text': '#ffffff',
      '--lead-accent': '#d4af37',
      '--lead-accent-soft': 'rgba(212, 175, 55, 0.16)',
      '--lead-gold': '#f8e7a1',
      '--lead-warning': '#fbbf24',
      '--lead-primary': 'linear-gradient(135deg, #f8e7a1 0%, #d4af37 100%)'
    },
    COBALT: {
      '--lead-bg': '#071225',
      '--lead-card': 'rgba(10, 20, 38, 0.97)',
      '--lead-card-strong': 'rgba(15, 30, 55, 0.98)',
      '--lead-inner': 'rgba(3, 8, 20, 0.98)',
      '--lead-border': 'rgba(96, 165, 250, 0.34)',
      '--lead-border-soft': 'rgba(96, 165, 250, 0.16)',
      '--lead-muted': 'rgba(191, 219, 254, 0.76)',
      '--lead-muted-dim': 'rgba(147, 197, 253, 0.56)',
      '--lead-text': '#eff6ff',
      '--lead-accent': '#60a5fa',
      '--lead-accent-soft': 'rgba(96, 165, 250, 0.16)',
      '--lead-gold': '#dbeafe',
      '--lead-warning': '#facc15',
      '--lead-primary': 'linear-gradient(135deg, #93c5fd 0%, #2563eb 100%)'
    },
    PEARL: {
      '--lead-bg': '#f8fafc',
      '--lead-card': 'rgba(255, 255, 255, 0.97)',
      '--lead-card-strong': 'rgba(255, 255, 255, 0.99)',
      '--lead-inner': 'rgba(248, 250, 252, 0.98)',
      '--lead-border': 'rgba(15, 23, 42, 0.2)',
      '--lead-border-soft': 'rgba(15, 23, 42, 0.1)',
      '--lead-muted': 'rgba(51, 65, 85, 0.82)',
      '--lead-muted-dim': 'rgba(71, 85, 105, 0.66)',
      '--lead-text': '#0f172a',
      '--lead-accent': '#166534',
      '--lead-accent-soft': 'rgba(22, 101, 52, 0.13)',
      '--lead-gold': '#8a6d1d',
      '--lead-warning': '#b45309',
      '--lead-primary': 'linear-gradient(135deg, #f8e7a1 0%, #22c55e 100%)'
    },
    GOLD: {
      '--lead-bg': '#0d0801',
      '--lead-card': 'rgba(24, 16, 4, 0.97)',
      '--lead-card-strong': 'rgba(34, 24, 8, 0.99)',
      '--lead-inner': 'rgba(10, 7, 2, 0.98)',
      '--lead-border': 'rgba(250, 204, 21, 0.35)',
      '--lead-border-soft': 'rgba(250, 204, 21, 0.17)',
      '--lead-muted': 'rgba(254, 243, 199, 0.78)',
      '--lead-muted-dim': 'rgba(217, 119, 6, 0.68)',
      '--lead-text': '#fff7ed',
      '--lead-accent': '#facc15',
      '--lead-accent-soft': 'rgba(250, 204, 21, 0.16)',
      '--lead-gold': '#fef3c7',
      '--lead-warning': '#fb923c',
      '--lead-primary': 'linear-gradient(135deg, #fef08a 0%, #f59e0b 100%)'
    },
    FORENSIC_VIOLET: {
      '--lead-bg': '#070512',
      '--lead-card': 'rgba(10, 8, 22, 0.985)',
      '--lead-card-strong': 'rgba(14, 10, 30, 0.99)',
      '--lead-inner': 'rgba(5, 4, 14, 0.99)',
      '--lead-border': 'rgba(168, 85, 247, 0.38)',
      '--lead-border-soft': 'rgba(168, 85, 247, 0.18)',
      '--lead-muted': 'rgba(226, 214, 255, 0.78)',
      '--lead-muted-dim': 'rgba(167, 139, 250, 0.62)',
      '--lead-text': '#ffffff',
      '--lead-accent': '#a855f7',
      '--lead-accent-soft': 'rgba(168, 85, 247, 0.18)',
      '--lead-gold': '#f8e7a1',
      '--lead-warning': '#facc15',
      '--lead-primary': 'linear-gradient(135deg, #f8e7a1 0%, #a855f7 48%, #22c55e 100%)',
      '--lead-header-glow': 'rgba(168, 85, 247, 0.22)',
      '--lead-header-title-glow': 'rgba(248, 231, 161, 0.16)',
      '--lead-header-subtitle': '#5eead4',
      '--lead-header-baseline': 'rgba(248, 231, 161, 0.14)'
    },
    FORENSIC: {
      '--lead-bg': '#020617',
      '--lead-card': 'rgba(4, 8, 20, 0.98)',
      '--lead-card-strong': 'rgba(8, 13, 28, 0.99)',
      '--lead-inner': 'rgba(0, 0, 0, 0.98)',
      '--lead-border': 'rgba(45, 212, 191, 0.32)',
      '--lead-border-soft': 'rgba(45, 212, 191, 0.15)',
      '--lead-muted': 'rgba(153, 246, 228, 0.72)',
      '--lead-muted-dim': 'rgba(94, 234, 212, 0.52)',
      '--lead-text': '#ecfeff',
      '--lead-accent': '#2dd4bf',
      '--lead-accent-soft': 'rgba(45, 212, 191, 0.16)',
      '--lead-gold': '#ccfbf1',
      '--lead-warning': '#f59e0b',
      '--lead-primary': 'linear-gradient(135deg, #99f6e4 0%, #14b8a6 100%)'
    },
    QUANTUM: {
      '--lead-bg': '#09051a',
      '--lead-card': 'rgba(20, 12, 45, 0.96)',
      '--lead-card-strong': 'rgba(30, 18, 64, 0.98)',
      '--lead-inner': 'rgba(8, 4, 22, 0.98)',
      '--lead-border': 'rgba(168, 85, 247, 0.35)',
      '--lead-border-soft': 'rgba(168, 85, 247, 0.16)',
      '--lead-muted': 'rgba(233, 213, 255, 0.75)',
      '--lead-muted-dim': 'rgba(196, 181, 253, 0.58)',
      '--lead-text': '#faf5ff',
      '--lead-accent': '#a855f7',
      '--lead-accent-soft': 'rgba(168, 85, 247, 0.16)',
      '--lead-gold': '#e9d5ff',
      '--lead-warning': '#facc15',
      '--lead-primary': 'linear-gradient(135deg, #c084fc 0%, #22c55e 100%)'
    }
  };

  const orderedPresetKeys = [
    'FORENSIC_VIOLET',
    'NEBULA',
    'AURORA',
    'BLACK',
    'COBALT',
    'PEARL',
    'GOLD',
    'FORENSIC',
    'QUANTUM'
  ];
  const matchedKey = orderedPresetKeys.find(presetKey => key.includes(presetKey));
  const matched = matchedKey ? [matchedKey, presets[matchedKey]] : null;
  return matched ? matched[1] : presets.NEBULA;
}


/**
 * @function normalizeThemeEngineOption
 * @description Normalizes one Account skin entry into a CRM theme option.
 * @param {Object} entry - Theme engine entry.
 * @param {number} index - Entry index.
 * @returns {Object|null} Normalized CRM theme option.
 * @collaboration Lets the CRM cockpit consume future Account skin shapes safely.
 */
export function normalizeThemeEngineOption(entry = {}, index = 0) {
  if (!isThemeLikeEntry(entry)) return null;

  const rawId = entry.id || entry.key || entry.name || entry.slug || entry.label || `THEME_${index + 1}`;
  const id = normalizeThemeId(rawId);
  const label = String(entry.shortLabel || entry.label || entry.name || rawId)
    .replace(/([a-z0-9])([A-Z])/g, '$1 $2')
    .replace(/[_-]+/g, ' ')
    .trim()
    .split(' ')[0]
    .toUpperCase();

  const tokenPacket = entry.tokens || entry.cssVars || entry.variables || entry.themeTokens || entry.palette || entry.colors || {};
  const cssVars = { ...getCrmThemePresetCssVars(id, label), ...normalizeThemeTokenMap(tokenPacket) };
  const className = String(entry.className || entry.cssClass || entry.skinClass || '');

  return {
    id,
    label,
    source: 'wilsyOperatingSkins',
    className,
    cssVars
  };
}

/**
 * @function resolveCrmThemeEngineOptions
 * @description Resolves CRM theme options from the shared Wilsy skin engine with fallback safety.
 * @returns {Array} CRM theme options.
 * @collaboration Makes the Lead cockpit use Wilsy OS skin authority instead of local-only skins.
 */
export function resolveCrmThemeEngineOptions() {
  const engineOptions = extractThemeEngineEntries(wilsyOperatingSkins)
    .map(normalizeThemeEngineOption)
    .filter(Boolean);

  const byId = new Map();

  [...engineOptions, ...FALLBACK_CRM_THEME_OPTIONS].forEach(option => {
    if (!option?.id || byId.has(option.id)) return;
    byId.set(option.id, option);
  });

  const resolved = Array.from(byId.values()).slice(0, 8);
  return resolved.length ? resolved : FALLBACK_CRM_THEME_OPTIONS;
}

/**
 * @function getDefaultCrmThemeOption
 * @description Returns the first resolved CRM theme option.
 * @returns {Object} Default CRM theme option.
 * @collaboration Provides deterministic fallback when no Account skin is selected yet.
 */
export function getDefaultCrmThemeOption() {
  return resolveCrmThemeEngineOptions()[0] || FALLBACK_CRM_THEME_OPTIONS[0];
}
