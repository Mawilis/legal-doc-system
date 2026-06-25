/* eslint-disable */
/**
 * ╔════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╗
 * ║ WILSY OS - NEBULA COMMAND SKIN                                                                                          ║
 * ║ NIGHT + DAY MODE THEME TOKENS                                                                                            ║
 * ╚════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╝
 *
 * @fileoverview Wilsy Nebula Command operating skin extracted from the approved CRM hero visual.
 */

const NEBULA_COMMAND_NIGHT = Object.freeze({
  mode: 'night',
  canvas: '#040812',
  panel: '#071123',
  rail: 'rgba(4, 8, 18, 0.92)',
  brightText: '#F6F7F3',
  softText: '#DEE3F0',
  mutedText: '#8FA7C9',
  overlay: 'rgba(4, 8, 18, 0.78)',
  backgroundAlt: '#071123',
  surface: '#101D33',
  surfaceElevated: '#142844',
  surfaceGlass: 'rgba(16, 29, 51, 0.78)',
  card: '#101D33',
  cardStrong: '#142844',
  border: 'rgba(47, 232, 220, 0.26)',
  borderStrong: 'rgba(62, 124, 210, 0.55)',
  primary: '#3C7CD2',
  accentStrong: '#D7BC79',
  success: '#20E070',
  text: '#F6F7F3',
  textSoft: '#DEE3F0',
  textMuted: '#8FA7C9',
  glowPrimary: 'rgba(60, 124, 210, 0.42)',
  glowSecondary: 'rgba(47, 232, 220, 0.32)',
  glowAccent: 'rgba(181, 153, 96, 0.28)',
  heroGradient: 'linear-gradient(135deg, #040812 0%, #071123 46%, #11254A 72%, #1C929F 100%)',
  cardGradient: 'linear-gradient(135deg, rgba(4,8,18,0.94), rgba(16,29,51,0.88) 55%, rgba(28,146,159,0.24))',
  shellGradient: 'radial-gradient(circle at 72% 18%, rgba(47,232,220,0.22), transparent 34%), radial-gradient(circle at 32% 100%, rgba(60,124,210,0.24), transparent 38%), linear-gradient(135deg, #040812, #071123 48%, #101D33)'
});

const NEBULA_COMMAND_DAY = Object.freeze({
  mode: 'day',
  canvas: '#F6F9FF',
  panel: '#FFFFFF',
  rail: 'rgba(255, 255, 255, 0.92)',
  brightText: '#091527',
  softText: '#203451',
  mutedText: '#5F7391',
  overlay: 'rgba(234, 243, 255, 0.68)',
  backgroundAlt: '#EAF3FF',
  surface: '#FFFFFF',
  surfaceElevated: '#F2F7FF',
  surfaceGlass: 'rgba(255, 255, 255, 0.78)',
  card: '#FFFFFF',
  cardStrong: '#EAF3FF',
  border: 'rgba(14, 138, 178, 0.28)',
  borderStrong: 'rgba(11, 59, 120, 0.34)',
  primary: '#0B3B78',
  accentStrong: '#8B6422',
  success: '#139A53',
  text: '#091527',
  textSoft: '#203451',
  textMuted: '#5F7391',
  glowPrimary: 'rgba(11, 59, 120, 0.18)',
  glowSecondary: 'rgba(14, 138, 178, 0.16)',
  glowAccent: 'rgba(183, 141, 56, 0.18)',
  heroGradient: 'linear-gradient(135deg, #FFFFFF 0%, #F6F9FF 44%, #EAF3FF 72%, #CFEFFF 100%)',
  cardGradient: 'linear-gradient(135deg, rgba(255,255,255,0.96), rgba(234,243,255,0.88) 58%, rgba(14,138,178,0.10))',
  shellGradient: 'radial-gradient(circle at 72% 18%, rgba(14,138,178,0.16), transparent 34%), radial-gradient(circle at 32% 100%, rgba(11,59,120,0.12), transparent 38%), linear-gradient(135deg, #F6F9FF, #FFFFFF 48%, #EAF3FF)'
});

const WILSY_NEBULA_COMMAND_SKIN = Object.freeze({
  id: 'wilsy-nebula-command',
  themeId: 'wilsy-nebula-command',
  skinId: 'wilsy-nebula-command',
  name: 'Wilsy Nebula Command',
  label: 'Wilsy Nebula Command',
  displayName: 'Wilsy Nebula Command',
  shortLabel: 'Nebula',
  doctrine: 'Nebula command skin. Navy depth, cyan edge glow, sovereign gold and live-green signals.',
  bestFor: 'Command DNA',
  accent: '#B59960',
  secondary: '#214594',
  highlight: '#2FE8DC',
  live: '#20E070',
  textOnAccent: '#040812',
  background: '#040812',
  canvas: '#040812',
  panel: '#071123',
  rail: 'rgba(4, 8, 18, 0.92)',
  brightText: '#F6F7F3',
  softText: '#DEE3F0',
  mutedText: '#8FA7C9',
  description: 'Approved CRM command skin with nebula navy depth, cyan edge glow, sovereign gold authority and live-green tenant signals.',
  shortDescription: 'Nebula navy, cyan edge glow, sovereign gold and live-green signals.',
  summary: 'Approved Nebula command palette for CRM, tenant identity and boardroom views.',
  subtitle: 'Nebula navy · cyan edge · gold · live green',
  categoryLabel: 'COMMAND DNA',
  categoryText: 'COMMAND DNA',
  useCase: 'CRM command, account command center, boardroom-ready tenant identity and revenue intelligence.',
  buyerSignal: 'premium CRM command identity',
  tenantDefault: true,
  surfaces: ['crm', 'account', 'executive', 'founder', 'boardroom'],
  category: 'core',
  status: 'production',
  previewGradient: 'linear-gradient(90deg, #B59960 0%, #101D33 26%, #214594 46%, #3C7CD2 64%, #2FE8DC 100%)',
  gradient: 'linear-gradient(90deg, #B59960 0%, #101D33 26%, #214594 46%, #3C7CD2 64%, #2FE8DC 100%)',
  colorHint: 'linear-gradient(90deg, #B59960 0%, #101D33 26%, #214594 46%, #3C7CD2 64%, #2FE8DC 100%)',
  colourHint: 'linear-gradient(90deg, #B59960 0%, #101D33 26%, #214594 46%, #3C7CD2 64%, #2FE8DC 100%)',
  accentGradient: 'linear-gradient(90deg, #B59960, #214594, #3C7CD2, #2FE8DC)',
  palette: ['#B59960', '#101D33', '#214594', '#3C7CD2', '#2FE8DC', '#20E070'],
  supportsDayMode: true,
  supportsNightMode: true,
  defaultMode: 'night',
  modes: {
    night: NEBULA_COMMAND_NIGHT,
    day: NEBULA_COMMAND_DAY
  },
  colors: {
    night: NEBULA_COMMAND_NIGHT,
    day: NEBULA_COMMAND_DAY
  },
  tokens: {
    night: NEBULA_COMMAND_NIGHT,
    day: NEBULA_COMMAND_DAY
  },
  swatch: {
    gradient: 'linear-gradient(90deg, #B59960 0%, #101D33 26%, #214594 46%, #3C7CD2 64%, #2FE8DC 100%)',
    colorHint: 'linear-gradient(90deg, #B59960 0%, #101D33 26%, #214594 46%, #3C7CD2 64%, #2FE8DC 100%)',
    background: '#040812',
    surface: '#101D33',
    primary: '#3C7CD2',
    secondary: '#1C929F',
    accent: '#B59960',
    success: '#20E070',
    text: '#F6F7F3'
  },
  cssVariables: {
    night: {
      '--wilsy-bg': NEBULA_COMMAND_NIGHT.background,
      '--wilsy-bg-alt': NEBULA_COMMAND_NIGHT.backgroundAlt,
      '--wilsy-surface': NEBULA_COMMAND_NIGHT.surface,
      '--wilsy-surface-elevated': NEBULA_COMMAND_NIGHT.surfaceElevated,
      '--wilsy-card': NEBULA_COMMAND_NIGHT.card,
      '--wilsy-border': NEBULA_COMMAND_NIGHT.border,
      '--wilsy-border-strong': NEBULA_COMMAND_NIGHT.borderStrong,
      '--wilsy-primary': NEBULA_COMMAND_NIGHT.primary,
      '--wilsy-secondary': NEBULA_COMMAND_NIGHT.secondary,
      '--wilsy-accent': NEBULA_COMMAND_NIGHT.accent,
      '--wilsy-success': NEBULA_COMMAND_NIGHT.success,
      '--wilsy-text': NEBULA_COMMAND_NIGHT.text,
      '--wilsy-text-soft': NEBULA_COMMAND_NIGHT.textSoft,
      '--wilsy-text-muted': NEBULA_COMMAND_NIGHT.textMuted,
      '--crm-bg': NEBULA_COMMAND_NIGHT.background,
      '--crm-card': NEBULA_COMMAND_NIGHT.card,
      '--crm-panel': NEBULA_COMMAND_NIGHT.surface,
      '--crm-border': NEBULA_COMMAND_NIGHT.border,
      '--crm-blue': NEBULA_COMMAND_NIGHT.primary,
      '--crm-cyan': NEBULA_COMMAND_NIGHT.secondary,
      '--crm-gold': NEBULA_COMMAND_NIGHT.accent,
      '--crm-green': NEBULA_COMMAND_NIGHT.success,
      '--crm-text': NEBULA_COMMAND_NIGHT.text,
      '--crm-soft': NEBULA_COMMAND_NIGHT.textMuted,
      '--tenant-primary': NEBULA_COMMAND_NIGHT.primary,
      '--tenant-secondary': NEBULA_COMMAND_NIGHT.secondary,
      '--tenant-accent': NEBULA_COMMAND_NIGHT.accent
    },
    day: {
      '--wilsy-bg': NEBULA_COMMAND_DAY.background,
      '--wilsy-bg-alt': NEBULA_COMMAND_DAY.backgroundAlt,
      '--wilsy-surface': NEBULA_COMMAND_DAY.surface,
      '--wilsy-surface-elevated': NEBULA_COMMAND_DAY.surfaceElevated,
      '--wilsy-card': NEBULA_COMMAND_DAY.card,
      '--wilsy-border': NEBULA_COMMAND_DAY.border,
      '--wilsy-border-strong': NEBULA_COMMAND_DAY.borderStrong,
      '--wilsy-primary': NEBULA_COMMAND_DAY.primary,
      '--wilsy-secondary': NEBULA_COMMAND_DAY.secondary,
      '--wilsy-accent': NEBULA_COMMAND_DAY.accent,
      '--wilsy-success': NEBULA_COMMAND_DAY.success,
      '--wilsy-text': NEBULA_COMMAND_DAY.text,
      '--wilsy-text-soft': NEBULA_COMMAND_DAY.textSoft,
      '--wilsy-text-muted': NEBULA_COMMAND_DAY.textMuted,
      '--crm-bg': NEBULA_COMMAND_DAY.background,
      '--crm-card': NEBULA_COMMAND_DAY.card,
      '--crm-panel': NEBULA_COMMAND_DAY.surface,
      '--crm-border': NEBULA_COMMAND_DAY.border,
      '--crm-blue': NEBULA_COMMAND_DAY.primary,
      '--crm-cyan': NEBULA_COMMAND_DAY.secondary,
      '--crm-gold': NEBULA_COMMAND_DAY.accent,
      '--crm-green': NEBULA_COMMAND_DAY.success,
      '--crm-text': NEBULA_COMMAND_DAY.text,
      '--crm-soft': NEBULA_COMMAND_DAY.textMuted,
      '--tenant-primary': NEBULA_COMMAND_DAY.primary,
      '--tenant-secondary': NEBULA_COMMAND_DAY.secondary,
      '--tenant-accent': NEBULA_COMMAND_DAY.accent
    }
  }
});

export {
  NEBULA_COMMAND_DAY,
  NEBULA_COMMAND_NIGHT,
  WILSY_NEBULA_COMMAND_SKIN
};

export default WILSY_NEBULA_COMMAND_SKIN;
