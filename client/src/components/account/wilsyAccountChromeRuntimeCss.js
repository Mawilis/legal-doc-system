/* eslint-disable */
/**
 * @fileoverview Wilsy Account Chrome Runtime CSS.
 * @description Extracted CSS contract for WilsyAccountCommandCenter runtime chrome enhancements. This file reduces JSX line count without changing the current visual system.
 * @collaboration Keeps theme, identity, route, and switchboard CSS source-truth separated from the Account component.
 */

export const WILSY_ACCOUNT_CHROME_RUNTIME_CSS_LINE_REPAIR_VERSION = 'R18AD1J-RAW-RUNTIME-CSS-STRING-REPAIR';

const WILSY_ACCOUNT_EXTRACTED_CHROME_CSS = `
/* WILSY_R6K_OBLITERATE_UTILITY_AND_HEADER_CONTRAST */
[data-wilsy-account-command-center="true"] [data-wilsy-account-utility],
[data-wilsy-account-command-center="true"] button[aria-label="Close account command center"],
[data-wilsy-account-command-center="true"] button[aria-label="Dock account command center"],
[data-wilsy-account-command-center="true"] button[aria-label="Expand account command center"] {
  width: 34px !important;
  height: 34px !important;
  min-width: 34px !important;
  min-height: 34px !important;
  max-width: 34px !important;
  max-height: 34px !important;
  inline-size: 34px !important;
  block-size: 34px !important;
  flex: 0 0 34px !important;
  padding: 0 !important;
  margin: 0 !important;
  border-radius: 11px !important;
  display: grid !important;
  place-items: center !important;
  overflow: hidden !important;
  background: rgba(8, 13, 26, 0.92) !important;
  color: #f8fafc !important;
  border: 1px solid rgba(248, 250, 252, 0.22) !important;
  box-shadow: 0 10px 22px rgba(0, 0, 0, 0.34) !important;
  transform: none !important;
}

[data-wilsy-account-command-center="true"] [data-wilsy-account-utility="layout-toggle"],
[data-wilsy-account-command-center="true"] button[aria-label="Dock account command center"],
[data-wilsy-account-command-center="true"] button[aria-label="Expand account command center"] {
  top: 14px !important;
  right: 64px !important;
  left: auto !important;
  bottom: auto !important;
}

[data-wilsy-account-command-center="true"] [data-wilsy-account-utility="close"],
[data-wilsy-account-command-center="true"] button[aria-label="Close account command center"] {
  top: 14px !important;
  right: 22px !important;
  left: auto !important;
  bottom: auto !important;
}

[data-wilsy-account-command-center="true"] [data-wilsy-account-utility] span,
[data-wilsy-account-command-center="true"] button[aria-label="Dock account command center"] span,
[data-wilsy-account-command-center="true"] button[aria-label="Expand account command center"] span {
  display: none !important;
}

[data-wilsy-account-command-center="true"] [data-wilsy-account-utility] svg,
[data-wilsy-account-command-center="true"] button[aria-label="Close account command center"] svg,
[data-wilsy-account-command-center="true"] button[aria-label="Dock account command center"] svg,
[data-wilsy-account-command-center="true"] button[aria-label="Expand account command center"] svg {
  width: 14px !important;
  height: 14px !important;
  min-width: 14px !important;
  min-height: 14px !important;
  color: #f8fafc !important;
  stroke: #f8fafc !important;
}

/* Header card contrast firewall: day mode must not produce white-on-white header cards. */
[data-wilsy-account-command-center="true"][data-wilsy-resolved-mode="day"] [data-wilsy-role~="account-command-header"] [data-wilsy-role~="account-story"],
[data-wilsy-account-command-center="true"][data-wilsy-resolved-mode="day"] [data-wilsy-role~="account-command-header"] [data-wilsy-role~="account-story-tile"],
[data-wilsy-account-command-center="true"][data-wilsy-resolved-mode="day"] [data-wilsy-role~="account-command-header"] [data-wilsy-role~="account-role-narrative"] {
  background: linear-gradient(135deg, #07101f 0%, #101827 70%, #050814 100%) !important;
  color: #f8fafc !important;
  border-color: rgba(248, 250, 252, 0.18) !important;
  box-shadow: 0 16px 38px rgba(0, 0, 0, 0.30) !important;
}

[data-wilsy-account-command-center="true"][data-wilsy-resolved-mode="day"] [data-wilsy-role~="account-command-header"] [data-wilsy-role~="account-story"] *,
[data-wilsy-account-command-center="true"][data-wilsy-resolved-mode="day"] [data-wilsy-role~="account-command-header"] [data-wilsy-role~="account-story-tile"] *,
[data-wilsy-account-command-center="true"][data-wilsy-resolved-mode="day"] [data-wilsy-role~="account-command-header"] [data-wilsy-role~="account-role-narrative"] * {
  background-color: transparent !important;
  color: #f8fafc !important;
  opacity: 1 !important;
}

[data-wilsy-account-command-center="true"][data-wilsy-resolved-mode="day"] [data-wilsy-role~="account-command-header"] [data-wilsy-role~="account-story-tile"] span,
[data-wilsy-account-command-center="true"][data-wilsy-resolved-mode="day"] [data-wilsy-role~="account-command-header"] [data-wilsy-role~="account-story-tile"] small,
[data-wilsy-account-command-center="true"][data-wilsy-resolved-mode="day"] [data-wilsy-role~="account-role-narrative"] p,
[data-wilsy-account-command-center="true"][data-wilsy-resolved-mode="day"] [data-wilsy-role~="account-role-narrative"] small {
  color: #cbd5e1 !important;
}

[data-wilsy-account-command-center="true"][data-wilsy-resolved-mode="day"] [data-wilsy-role~="account-command-header"] select,
[data-wilsy-account-command-center="true"][data-wilsy-resolved-mode="day"] [data-wilsy-role~="account-command-header"] option {
  background: #101827 !important;
  color: #f8fafc !important;
  border-color: rgba(248, 250, 252, 0.22) !important;
}

/* Night mode should remain dark after toggling back from day. */
[data-wilsy-account-command-center="true"][data-wilsy-resolved-mode="night"] [data-wilsy-role~="account-command-header"] [data-wilsy-role~="account-story"],
[data-wilsy-account-command-center="true"][data-wilsy-resolved-mode="night"] [data-wilsy-role~="account-command-header"] [data-wilsy-role~="account-story-tile"],
[data-wilsy-account-command-center="true"][data-wilsy-resolved-mode="night"] [data-wilsy-role~="account-role-narrative"] {
  background: linear-gradient(135deg, #050814 0%, #090d1a 70%, #030712 100%) !important;
  color: #f8fafc !important;
  border-color: rgba(248, 250, 252, 0.16) !important;
}


/* WILSY_R6L_HARD_UTILITY_LOCK_AND_THEME_IDENTITY */
[data-wilsy-account-command-center="true"] [data-wilsy-account-utility-contract="R6L-LOCKED-UTILITY"],
[data-wilsy-account-command-center="true"] [data-wilsy-account-utility],
[data-wilsy-account-command-center="true"] button[aria-label="Close account command center"],
[data-wilsy-account-command-center="true"] button[aria-label="Dock account command center"],
[data-wilsy-account-command-center="true"] button[aria-label="Expand account command center"] {
  width: 34px !important;
  height: 34px !important;
  min-width: 34px !important;
  min-height: 34px !important;
  max-width: 34px !important;
  max-height: 34px !important;
  inline-size: 34px !important;
  block-size: 34px !important;
  flex-basis: 34px !important;
  flex-grow: 0 !important;
  flex-shrink: 0 !important;
  padding: 0 !important;
  margin: 0 !important;
  border-radius: 11px !important;
  display: grid !important;
  place-items: center !important;
  overflow: hidden !important;
  transform: none !important;
  background: rgba(8, 13, 26, 0.92) !important;
  color: #f8fafc !important;
  border: 1px solid rgba(248, 250, 252, 0.22) !important;
  box-shadow: 0 10px 22px rgba(0, 0, 0, 0.34) !important;
}

[data-wilsy-account-command-center="true"] [data-wilsy-account-utility="layout-toggle"],
[data-wilsy-account-command-center="true"] button[aria-label="Dock account command center"],
[data-wilsy-account-command-center="true"] button[aria-label="Expand account command center"] {
  top: 14px !important;
  right: 64px !important;
  left: auto !important;
  bottom: auto !important;
}

[data-wilsy-account-command-center="true"] [data-wilsy-account-utility="close"],
[data-wilsy-account-command-center="true"] button[aria-label="Close account command center"] {
  top: 14px !important;
  right: 22px !important;
  left: auto !important;
  bottom: auto !important;
}

[data-wilsy-account-command-center="true"] [data-wilsy-account-utility-contract="R6L-LOCKED-UTILITY"] svg,
[data-wilsy-account-command-center="true"] [data-wilsy-account-utility] svg {
  width: 14px !important;
  height: 14px !important;
  min-width: 14px !important;
  min-height: 14px !important;
  stroke: #f8fafc !important;
  color: #f8fafc !important;
}

[data-wilsy-account-command-center="true"] [data-wilsy-skin-symbol="R6L-THEME-SYMBOL"] {
  visibility: visible !important;
  opacity: 1 !important;
}


/* WILSY_R6M_TYPE_SYSTEM_CONTRACT */
[data-wilsy-account-command-center="true"] {
  --wilsy-font-display: "Aptos Display", "SF Pro Display", "Segoe UI Variable Display", "Inter", system-ui, sans-serif;
  --wilsy-font-text: "Aptos", "SF Pro Text", "Segoe UI Variable Text", "Inter", system-ui, sans-serif;
  --wilsy-font-mono: "SF Mono", "Cascadia Mono", "JetBrains Mono", "Menlo", "Consolas", monospace;

  --wilsy-type-hero: clamp(36px, 3.1vw, 52px);
  --wilsy-type-title: clamp(28px, 2.25vw, 40px);
  --wilsy-type-section: clamp(20px, 1.45vw, 28px);
  --wilsy-type-card: clamp(16px, 1.05vw, 20px);
  --wilsy-type-body: clamp(13px, 0.86vw, 15px);
  --wilsy-type-caption: clamp(11px, 0.72vw, 13px);
  --wilsy-type-micro: clamp(9px, 0.58vw, 11px);

  --wilsy-weight-black: 850;
  --wilsy-weight-bold: 720;
  --wilsy-weight-medium: 560;
  --wilsy-weight-regular: 430;

  font-family: var(--wilsy-font-text) !important;
  font-synthesis: none;
  text-rendering: geometricPrecision;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
}

[data-wilsy-account-command-center="true"] *,
[data-wilsy-account-command-center="true"] button,
[data-wilsy-account-command-center="true"] select,
[data-wilsy-account-command-center="true"] input {
  font-family: var(--wilsy-font-text) !important;
  font-synthesis: none !important;
}

[data-wilsy-account-command-center="true"] h1,
[data-wilsy-account-command-center="true"] h2,
[data-wilsy-account-command-center="true"] h3 {
  font-family: var(--wilsy-font-display) !important;
  font-weight: var(--wilsy-weight-black) !important;
  letter-spacing: -0.018em !important;
}

[data-wilsy-account-command-center="true"] h2 {
  font-size: var(--wilsy-type-hero) !important;
  line-height: 0.96 !important;
}

[data-wilsy-account-command-center="true"] h3 {
  font-size: var(--wilsy-type-title) !important;
  line-height: 1.02 !important;
}

[data-wilsy-account-command-center="true"] p {
  font-family: var(--wilsy-font-text) !important;
  font-size: var(--wilsy-type-body) !important;
  line-height: 1.52 !important;
  font-weight: var(--wilsy-weight-regular) !important;
  letter-spacing: 0.006em !important;
}

[data-wilsy-account-command-center="true"] small,
[data-wilsy-account-command-center="true"] em {
  font-family: var(--wilsy-font-text) !important;
  font-size: var(--wilsy-type-caption) !important;
  line-height: 1.38 !important;
  font-weight: var(--wilsy-weight-regular) !important;
  letter-spacing: 0.012em !important;
}

[data-wilsy-account-command-center="true"] [data-wilsy-role~="account-story-tile"] strong,
[data-wilsy-account-command-center="true"] [data-wilsy-theme-option] strong,
[data-wilsy-account-command-center="true"] [data-wilsy-theme-atlas] strong {
  font-family: var(--wilsy-font-display) !important;
  font-size: var(--wilsy-type-card) !important;
  line-height: 1.12 !important;
  font-weight: var(--wilsy-weight-bold) !important;
  letter-spacing: -0.006em !important;
}

[data-wilsy-account-command-center="true"] [data-wilsy-role~="account-role-narrative"] strong {
  font-family: var(--wilsy-font-display) !important;
  font-size: var(--wilsy-type-section) !important;
  line-height: 1.1 !important;
  font-weight: var(--wilsy-weight-bold) !important;
  letter-spacing: -0.006em !important;
}

[data-wilsy-account-command-center="true"] [data-wilsy-role~="account-story-tile"] span,
[data-wilsy-account-command-center="true"] [data-wilsy-role~="account-role-narrative"] span,
[data-wilsy-account-command-center="true"] [data-wilsy-theme-atlas] span,
[data-wilsy-account-command-center="true"] [data-wilsy-theme-option] em,
[data-wilsy-account-command-center="true"] [data-wilsy-preference-surface] [style*="uppercase"] {
  font-family: var(--wilsy-font-text) !important;
  font-size: var(--wilsy-type-micro) !important;
  font-weight: var(--wilsy-weight-bold) !important;
  letter-spacing: 0.14em !important;
  text-transform: uppercase !important;
}

[data-wilsy-account-command-center="true"] [data-wilsy-theme-option] span:not([data-wilsy-skin-symbol]),
[data-wilsy-account-command-center="true"] [data-wilsy-mode-copy] {
  font-family: var(--wilsy-font-display) !important;
  font-size: var(--wilsy-type-card) !important;
  font-weight: var(--wilsy-weight-bold) !important;
  letter-spacing: -0.004em !important;
}

[data-wilsy-account-command-center="true"] [data-wilsy-theme-option] small,
[data-wilsy-account-command-center="true"] [data-wilsy-mode-copy] + small {
  font-family: var(--wilsy-font-text) !important;
  font-size: var(--wilsy-type-caption) !important;
  font-weight: var(--wilsy-weight-regular) !important;
  line-height: 1.42 !important;
  letter-spacing: 0.008em !important;
}

[data-wilsy-account-command-center="true"] select,
[data-wilsy-account-command-center="true"] button {
  font-family: var(--wilsy-font-text) !important;
  font-size: var(--wilsy-type-body) !important;
  font-weight: var(--wilsy-weight-bold) !important;
  letter-spacing: 0.01em !important;
}

[data-wilsy-account-command-center="true"] [data-wilsy-account-utility],
[data-wilsy-account-command-center="true"] [data-wilsy-account-utility] * {
  font-size: 0 !important;
  line-height: 0 !important;
}

[data-wilsy-account-command-center="true"] [data-wilsy-account-utility] svg {
  font-size: initial !important;
}

[data-wilsy-account-command-center="true"] [data-wilsy-skin-symbol="R6L-THEME-SYMBOL"] {
  font-family: var(--wilsy-font-display) !important;
  font-size: 18px !important;
  font-weight: var(--wilsy-weight-black) !important;
  letter-spacing: 0 !important;
}



/* WILSY_R6R_FINAL_UTILITY_DOCK */
[data-wilsy-utility-dock-shell="R6R-FINAL-UTILITY-DOCK"] {
  position: absolute !important;
  top: 16px !important;
  right: 20px !important;
  z-index: 9999 !important;
  display: flex !important;
  align-items: center !important;
  justify-content: flex-end !important;
  gap: 8px !important;
  width: auto !important;
  height: 34px !important;
  min-height: 34px !important;
  pointer-events: auto !important;
}

[data-wilsy-utility-dock="R6R-FINAL-UTILITY-DOCK"],
[data-wilsy-utility-geometry="34x34"] {
  all: unset !important;
  box-sizing: border-box !important;
  position: relative !important;
  top: auto !important;
  right: auto !important;
  bottom: auto !important;
  left: auto !important;
  width: 34px !important;
  height: 34px !important;
  min-width: 34px !important;
  min-height: 34px !important;
  max-width: 34px !important;
  max-height: 34px !important;
  inline-size: 34px !important;
  block-size: 34px !important;
  flex: 0 0 34px !important;
  flex-basis: 34px !important;
  flex-grow: 0 !important;
  flex-shrink: 0 !important;
  padding: 0 !important;
  margin: 0 !important;
  border-radius: 11px !important;
  border: 1px solid rgba(248, 250, 252, 0.24) !important;
  background: rgba(8, 13, 26, 0.94) !important;
  color: #f8fafc !important;
  display: grid !important;
  place-items: center !important;
  overflow: hidden !important;
  transform: none !important;
  cursor: pointer !important;
  box-shadow: 0 10px 22px rgba(0, 0, 0, 0.34) !important;
}

[data-wilsy-utility-dock="R6R-FINAL-UTILITY-DOCK"] svg {
  width: 14px !important;
  height: 14px !important;
  min-width: 14px !important;
  min-height: 14px !important;
  color: #f8fafc !important;
  stroke: #f8fafc !important;
}

[data-wilsy-account-command-center="true"] button[aria-label="Dock account command center"]:not([data-wilsy-utility-dock="R6R-FINAL-UTILITY-DOCK"]),
[data-wilsy-account-command-center="true"] button[aria-label="Expand account command center"]:not([data-wilsy-utility-dock="R6R-FINAL-UTILITY-DOCK"]),
[data-wilsy-account-command-center="true"] button[aria-label="Close account command center"]:not([data-wilsy-utility-dock="R6R-FINAL-UTILITY-DOCK"]) {
  display: none !important;
  visibility: hidden !important;
  pointer-events: none !important;
  width: 0 !important;
  height: 0 !important;
  min-width: 0 !important;
  min-height: 0 !important;
  max-width: 0 !important;
  max-height: 0 !important;
  padding: 0 !important;
  margin: 0 !important;
  overflow: hidden !important;
}













/* WILSY_R7B_REFERENCE_IDENTITY_CHROME_RESET */
[data-wilsy-account-command-center="true"] {
  --wilsy-r7b-bg: #07101f;
  --wilsy-r7b-panel: rgba(8, 13, 26, 0.90);
  --wilsy-r7b-card: rgba(10, 18, 32, 0.88);
  --wilsy-r7b-border: rgba(148, 163, 184, 0.28);
  --wilsy-r7b-border-soft: rgba(148, 163, 184, 0.14);
  --wilsy-r7b-text: #f8fafc;
  --wilsy-r7b-muted: #a7b1c2;
  --wilsy-r7b-accent: #38bdf8;
  --wilsy-r7b-success: #22c55e;
  --wilsy-r7b-gold: #d4af37;
  --wilsy-r7b-identity-width: clamp(390px, 22vw, 430px);
  --wilsy-r7b-header-max: 292px;
}

/* The account top area is chrome, not a profile billboard. */
[data-wilsy-account-command-center="true"] [data-wilsy-role~="account-command-header"] {
  display: grid !important;
  grid-template-columns: var(--wilsy-r7b-identity-width) minmax(0, 1fr) !important;
  grid-template-rows: 112px 104px !important;
  gap: 14px 22px !important;
  align-items: stretch !important;
  min-height: 248px !important;
  max-height: var(--wilsy-r7b-header-max) !important;
  padding: 22px 116px 18px 32px !important;
  overflow: hidden !important;
  background:
    radial-gradient(circle at 0% 20%, rgba(56, 189, 248, 0.10) 0%, transparent 30%),
    radial-gradient(circle at 100% 0%, rgba(212, 175, 55, 0.06) 0%, transparent 28%),
    linear-gradient(135deg, #07101f 0%, #050814 62%, #030711 100%) !important;
}

/* Left reference card: clean command identity. */
[data-wilsy-account-command-center="true"] [data-wilsy-identity-chrome] {
  grid-column: 1 / 2 !important;
  grid-row: 1 / 3 !important;
  width: 100% !important;
  max-width: var(--wilsy-r7b-identity-width) !important;
  height: 220px !important;
  min-height: 220px !important;
  max-height: 220px !important;
  display: grid !important;
  grid-template-columns: 74px minmax(0, 1fr) 26px !important;
  grid-template-rows: 22px 62px 1px 26px 58px !important;
  gap: 8px 16px !important;
  align-items: center !important;
  padding: 22px 26px 22px 28px !important;
  border-radius: 24px !important;
  border: 1px solid var(--wilsy-r7b-border) !important;
  background:
    radial-gradient(circle at 15% 0%, rgba(56, 189, 248, 0.12) 0%, transparent 34%),
    linear-gradient(135deg, rgba(10, 18, 32, 0.96) 0%, rgba(5, 8, 20, 0.94) 100%) !important;
  box-shadow: 0 22px 56px rgba(0, 0, 0, 0.34), inset 0 1px 0 rgba(255, 255, 255, 0.045) !important;
  overflow: hidden !important;
}

/* Label is part of the card, not floating over content. */
[data-wilsy-account-command-center="true"] [data-wilsy-identity-chrome]::before {
  content: "COMMAND IDENTITY" !important;
  grid-column: 1 / -1 !important;
  grid-row: 1 / 2 !important;
  position: static !important;
  color: #94a3b8 !important;
  font-size: 10px !important;
  line-height: 1 !important;
  font-weight: 850 !important;
  letter-spacing: 0.18em !important;
  text-transform: uppercase !important;
}

/* Divider mirrors the reference, without cutting through controls. */
[data-wilsy-account-command-center="true"] [data-wilsy-identity-chrome]::after {
  content: "" !important;
  grid-column: 1 / -1 !important;
  grid-row: 3 / 4 !important;
  position: static !important;
  width: 100% !important;
  height: 1px !important;
  background: linear-gradient(90deg, transparent 0%, rgba(148, 163, 184, 0.28) 18%, rgba(148, 163, 184, 0.12) 100%) !important;
  opacity: 1 !important;
}

/* WK badge. */
[data-wilsy-account-command-center="true"] [data-wilsy-identity-chrome] > :first-child {
  grid-column: 1 / 2 !important;
  grid-row: 2 / 3 !important;
  width: 58px !important;
  height: 58px !important;
  min-width: 58px !important;
  min-height: 58px !important;
  max-width: 58px !important;
  max-height: 58px !important;
  border-radius: 14px !important;
  font-size: 26px !important;
  line-height: 1 !important;
  background:
    radial-gradient(circle at 35% 22%, rgba(56, 189, 248, 0.16) 0%, transparent 38%),
    linear-gradient(135deg, #08111f 0%, #0f172a 100%) !important;
  border: 1px solid rgba(56, 189, 248, 0.18) !important;
  box-shadow: 0 12px 28px rgba(14, 165, 233, 0.10), inset 0 1px 0 rgba(255, 255, 255, 0.07) !important;
}

/* Name appears once only. */
[data-wilsy-account-command-center="true"] [data-wilsy-identity-chrome] h1,
[data-wilsy-account-command-center="true"] [data-wilsy-identity-chrome] h2,
[data-wilsy-account-command-center="true"] [data-wilsy-identity-chrome] h3 {
  grid-column: 2 / 3 !important;
  grid-row: 2 / 3 !important;
  color: var(--wilsy-r7b-text) !important;
  font-size: clamp(18px, 1.12vw, 25px) !important;
  line-height: 1.05 !important;
  letter-spacing: -0.025em !important;
  font-weight: 820 !important;
  max-width: 100% !important;
  margin: 0 !important;
  white-space: nowrap !important;
  overflow: hidden !important;
  text-overflow: ellipsis !important;
  display: block !important;
}

/* Green verified check, not a giant duplicated row. */
[data-wilsy-account-command-center="true"] [data-wilsy-identity-chrome] svg:not([data-wilsy-tenant-icon]) {
  color: var(--wilsy-r7b-success) !important;
  stroke: var(--wilsy-r7b-success) !important;
}

/* Account reference chip. */
[data-wilsy-account-command-center="true"] [data-wilsy-identity-chrome] [style*="Account:"],
[data-wilsy-account-command-center="true"] [data-wilsy-identity-chrome] p {
  grid-column: 2 / 4 !important;
  grid-row: 4 / 5 !important;
  color: var(--wilsy-r7b-muted) !important;
  font-size: clamp(10px, 0.66vw, 12px) !important;
  line-height: 1.1 !important;
  height: 24px !important;
  min-height: 24px !important;
  margin: 0 !important;
  padding: 0 !important;
  max-width: 100% !important;
  border-radius: 999px !important;
  display: inline-flex !important;
  align-items: center !important;
  white-space: nowrap !important;
  overflow: hidden !important;
  text-overflow: ellipsis !important;
}

/* Tenant scope: readable, reference-shaped, no clipping. */
[data-wilsy-account-command-center="true"] [data-wilsy-tenant-scope-select] {
  grid-column: 1 / -1 !important;
  grid-row: 5 / 6 !important;
  width: 100% !important;
  max-width: 100% !important;
  min-height: 52px !important;
  height: 52px !important;
  max-height: 52px !important;
  padding: 18px 12px 8px !important;
  border-radius: 12px !important;
  border: 1px solid rgba(148, 163, 184, 0.32) !important;
  background: rgba(5, 8, 20, 0.78) !important;
  grid-template-columns: 28px minmax(0, 1fr) 18px !important;
  justify-self: stretch !important;
  align-self: end !important;
  gap: 10px !important;
  overflow: hidden !important;
}

[data-wilsy-account-command-center="true"] [data-wilsy-tenant-scope-select]::before {
  content: "TENANT SCOPE" !important;
  top: 7px !important;
  left: 48px !important;
  color: #94a3b8 !important;
  font-size: 8px !important;
  line-height: 1 !important;
  letter-spacing: 0.16em !important;
  font-weight: 850 !important;
}

[data-wilsy-account-command-center="true"] [data-wilsy-tenant-scope-select] svg {
  width: 18px !important;
  height: 18px !important;
  stroke: #e5e7eb !important;
}

[data-wilsy-account-command-center="true"] [data-wilsy-tenant-scope-select] select {
  color: var(--wilsy-r7b-text) !important;
  font-size: clamp(12px, 0.76vw, 15px) !important;
  line-height: 1 !important;
  font-weight: 760 !important;
  min-width: 0 !important;
  width: 100% !important;
  max-width: 100% !important;
  white-space: nowrap !important;
  overflow: hidden !important;
  text-overflow: ellipsis !important;
}

/* Right panel: no duplicate user name, no hardcoded time. */
[data-wilsy-account-command-center="true"] [data-wilsy-role~="account-role-narrative"] {
  grid-column: 2 / 3 !important;
  grid-row: 1 / 2 !important;
  min-height: 100px !important;
  max-height: 112px !important;
  padding: 18px 118px 16px 26px !important;
  border-radius: 22px !important;
  border: 1px solid rgba(148, 163, 184, 0.13) !important;
  background: linear-gradient(135deg, rgba(8, 13, 26, 0.90) 0%, rgba(3, 7, 17, 0.80) 100%) !important;
  display: grid !important;
  grid-template-columns: minmax(136px, 0.20fr) minmax(0, 1fr) !important;
  gap: 5px 22px !important;
  align-items: center !important;
  overflow: hidden !important;
}

[data-wilsy-account-command-center="true"] [data-wilsy-role~="account-role-narrative"] strong {
  font-size: 0 !important;
  line-height: 0 !important;
  overflow: hidden !important;
}

[data-wilsy-account-command-center="true"] [data-wilsy-role~="account-role-narrative"] strong::before {
  content: "Command authority and operating posture.";
  display: block;
  color: var(--wilsy-r7b-text);
  font-size: clamp(17px, 1.24vw, 24px);
  line-height: 1.08;
  font-weight: 820;
  letter-spacing: -0.018em;
}

[data-wilsy-account-command-center="true"] [data-wilsy-role~="account-role-narrative"] p {
  color: #dbe2ee !important;
  font-size: clamp(11px, 0.72vw, 13px) !important;
  line-height: 1.32 !important;
  margin: 0 !important;
}

[data-wilsy-account-command-center="true"] [data-wilsy-role~="account-role-narrative"] small {
  font-size: 0 !important;
  line-height: 0 !important;
}

[data-wilsy-account-command-center="true"] [data-wilsy-role~="account-role-narrative"]::after {
  content: "KNOWN FOR  \\u2022  FORENSIC COMMAND INTELLIGENCE";
  grid-column: 1 / -1;
  color: #94a3b8;
  font-size: 9px;
  font-weight: 850;
  letter-spacing: 0.16em;
  text-transform: uppercase;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

/* Signal cards: reference style. */
[data-wilsy-account-command-center="true"] [data-wilsy-role~="account-story"] {
  grid-column: 2 / 3 !important;
  grid-row: 2 / 3 !important;
  display: grid !important;
  grid-template-columns: repeat(4, minmax(0, 1fr)) !important;
  gap: 12px !important;
  width: 100% !important;
  max-width: 100% !important;
  overflow: hidden !important;
}

[data-wilsy-account-command-center="true"] [data-wilsy-role~="account-story-tile"] {
  position: relative !important;
  min-height: 92px !important;
  max-height: 104px !important;
  padding: 16px 14px 14px 72px !important;
  border-radius: 15px !important;
  border: 1px solid rgba(56, 189, 248, 0.20) !important;
  background: linear-gradient(135deg, rgba(10, 18, 32, 0.90) 0%, rgba(5, 8, 20, 0.74) 100%) !important;
  overflow: hidden !important;
  align-content: center !important;
}

[data-wilsy-account-command-center="true"] [data-wilsy-role~="account-story-tile"]::before {
  content: "";
  position: absolute;
  left: 0;
  top: 12px;
  bottom: 12px;
  width: 3px;
  border-radius: 999px;
  background: linear-gradient(180deg, #38bdf8 0%, #0ea5e9 100%);
  box-shadow: 0 0 20px rgba(56, 189, 248, 0.36);
}

[data-wilsy-account-command-center="true"] [data-wilsy-role~="account-story-tile"]::after {
  content: "\\u25ce";
  position: absolute;
  left: 22px;
  top: 50%;
  width: 38px;
  height: 38px;
  transform: translateY(-50%);
  display: grid;
  place-items: center;
  border-radius: 10px;
  color: #e5e7eb;
  font-size: 18px;
  border: 1px solid rgba(148, 163, 184, 0.28);
  background: rgba(15, 23, 42, 0.72);
}

[data-wilsy-account-command-center="true"] [data-wilsy-role~="account-story-tile"] span {
  color: #38bdf8 !important;
  font-size: 8px !important;
  line-height: 1 !important;
  letter-spacing: 0.16em !important;
  font-weight: 850 !important;
}

[data-wilsy-account-command-center="true"] [data-wilsy-role~="account-story-tile"] strong {
  display: block !important;
  color: var(--wilsy-r7b-text) !important;
  font-size: clamp(13px, 0.92vw, 17px) !important;
  line-height: 1.06 !important;
  margin-top: 5px !important;
  white-space: normal !important;
  overflow: hidden !important;
  text-overflow: ellipsis !important;
}

[data-wilsy-account-command-center="true"] [data-wilsy-role~="account-story-tile"] small {
  display: block !important;
  color: var(--wilsy-r7b-muted) !important;
  font-size: clamp(9px, 0.58vw, 11px) !important;
  line-height: 1.18 !important;
  margin-top: 4px !important;
  white-space: nowrap !important;
  overflow: hidden !important;
  text-overflow: ellipsis !important;
}

/* Bottom tab rail. */
[data-wilsy-account-command-center="true"] [data-wilsy-role~="account-command-tabs"] {
  padding: 14px 32px 18px !important;
  gap: 18px !important;
  border-top: 1px solid rgba(148, 163, 184, 0.12) !important;
  background: linear-gradient(180deg, rgba(7, 16, 31, 0.96) 0%, rgba(3, 7, 17, 0.98) 100%) !important;
}

[data-wilsy-account-command-center="true"] [data-wilsy-role~="account-command-tabs"] button {
  min-height: 58px !important;
  border-radius: 18px !important;
  border: 1px solid rgba(148, 163, 184, 0.26) !important;
  background: linear-gradient(135deg, rgba(10, 18, 32, 0.84) 0%, rgba(5, 8, 20, 0.78) 100%) !important;
  font-size: clamp(13px, 0.86vw, 16px) !important;
}

[data-wilsy-account-command-center="true"] [data-wilsy-role~="account-command-body"] {
  padding-top: 0 !important;
}

@media (max-width: 1360px) {
  [data-wilsy-account-command-center="true"] {
    --wilsy-r7b-identity-width: clamp(320px, 25vw, 390px);
    --wilsy-r7b-header-max: none;
  }

  [data-wilsy-account-command-center="true"] [data-wilsy-role~="account-command-header"] {
    max-height: none !important;
    grid-template-columns: var(--wilsy-r7b-identity-width) minmax(0, 1fr) !important;
  }

  [data-wilsy-account-command-center="true"] [data-wilsy-role~="account-story"] {
    grid-template-columns: repeat(2, minmax(0, 1fr)) !important;
  }
}

@media (max-width: 980px) {
  [data-wilsy-account-command-center="true"] [data-wilsy-role~="account-command-header"] {
    display: flex !important;
    flex-direction: column !important;
    padding: 62px 18px 16px !important;
  }

  [data-wilsy-account-command-center="true"] [data-wilsy-identity-chrome] {
    max-width: none !important;
    height: auto !important;
    min-height: 220px !important;
    max-height: none !important;
  }

  [data-wilsy-account-command-center="true"] [data-wilsy-role~="account-role-narrative"] {
    max-height: none !important;
    padding-right: 18px !important;
    grid-template-columns: minmax(0, 1fr) !important;
  }

  [data-wilsy-account-command-center="true"] [data-wilsy-role~="account-story"] {
    grid-template-columns: minmax(0, 1fr) !important;
  }
}


/* WILSY_R7C_REFERENCE_IDENTITY_RENDERER */
[data-wilsy-account-command-center="true"] {
  --wilsy-r7c-bg: #07101f;
  --wilsy-r7c-panel: rgba(8, 13, 26, 0.92);
  --wilsy-r7c-card: rgba(10, 18, 32, 0.88);
  --wilsy-r7c-border: rgba(148, 163, 184, 0.28);
  --wilsy-r7c-border-soft: rgba(148, 163, 184, 0.14);
  --wilsy-r7c-text: #f8fafc;
  --wilsy-r7c-muted: #a7b1c2;
  --wilsy-r7c-accent: #38bdf8;
  --wilsy-r7c-success: #22c55e;
  --wilsy-r7c-gold: #d4af37;
  --wilsy-r7c-identity-width: clamp(390px, 22vw, 430px);
  --wilsy-r7c-header-max: 292px;
}

/* Header follows the supplied reference: grid dominance and no profile billboard. */
[data-wilsy-account-command-center="true"] [data-wilsy-role~="account-command-header"] {
  display: grid !important;
  grid-template-columns: var(--wilsy-r7c-identity-width) minmax(0, 1fr) !important;
  grid-template-rows: 112px 104px !important;
  gap: 14px 22px !important;
  align-items: stretch !important;
  min-height: 248px !important;
  max-height: var(--wilsy-r7c-header-max) !important;
  padding: 22px 116px 18px 32px !important;
  overflow: hidden !important;
  background:
    radial-gradient(circle at 0% 20%, rgba(56, 189, 248, 0.10) 0%, transparent 30%),
    radial-gradient(circle at 100% 0%, rgba(212, 175, 55, 0.06) 0%, transparent 28%),
    linear-gradient(135deg, #07101f 0%, #050814 62%, #030711 100%) !important;
}

/* Legacy identity internals are hidden; R7C renderer becomes the visible source of truth. */
[data-wilsy-account-command-center="true"] [data-wilsy-identity-chrome][data-wilsy-r7c-identity-card="true"] {
  position: relative !important;
  grid-column: 1 / 2 !important;
  grid-row: 1 / 3 !important;
  width: 100% !important;
  max-width: var(--wilsy-r7c-identity-width) !important;
  height: 220px !important;
  min-height: 220px !important;
  max-height: 220px !important;
  display: block !important;
  padding: 0 !important;
  border-radius: 24px !important;
  border: 1px solid var(--wilsy-r7c-border) !important;
  background:
    radial-gradient(circle at 15% 0%, rgba(56, 189, 248, 0.12) 0%, transparent 34%),
    linear-gradient(135deg, rgba(10, 18, 32, 0.96) 0%, rgba(5, 8, 20, 0.94) 100%) !important;
  box-shadow: 0 22px 56px rgba(0, 0, 0, 0.34), inset 0 1px 0 rgba(255, 255, 255, 0.045) !important;
  overflow: hidden !important;
}

/* Hide old broken children but keep the actual tenant select clickable. */
[data-wilsy-account-command-center="true"] [data-wilsy-identity-chrome][data-wilsy-r7c-identity-card="true"] > :not([data-wilsy-r7c-identity-ui="true"]) {
  opacity: 0 !important;
  visibility: hidden !important;
  pointer-events: none !important;
}

[data-wilsy-account-command-center="true"] [data-wilsy-identity-chrome][data-wilsy-r7c-identity-card="true"] [data-wilsy-tenant-scope-select],
[data-wilsy-account-command-center="true"] [data-wilsy-identity-chrome][data-wilsy-r7c-identity-card="true"] select {
  position: absolute !important;
  left: 118px !important;
  right: 24px !important;
  bottom: 22px !important;
  width: auto !important;
  height: 52px !important;
  min-height: 52px !important;
  opacity: 0 !important;
  visibility: visible !important;
  pointer-events: auto !important;
  z-index: 9 !important;
}

/* Clean rendered identity layer. */
[data-wilsy-account-command-center="true"] [data-wilsy-r7c-identity-ui="true"] {
  position: absolute !important;
  inset: 0 !important;
  z-index: 2 !important;
  display: grid !important;
  grid-template-columns: 76px minmax(0, 1fr) !important;
  gap: 16px !important;
  align-items: center !important;
  padding: 26px 28px !important;
  pointer-events: none !important;
}

[data-wilsy-account-command-center="true"] .wilsy-r7c-identity-badge {
  width: 58px !important;
  height: 58px !important;
  border-radius: 14px !important;
  display: grid !important;
  place-items: center !important;
  color: #ffffff !important;
  font-size: 26px !important;
  line-height: 1 !important;
  font-weight: 860 !important;
  letter-spacing: -0.04em !important;
  background:
    radial-gradient(circle at 35% 22%, rgba(56, 189, 248, 0.16) 0%, transparent 38%),
    linear-gradient(135deg, #08111f 0%, #0f172a 100%) !important;
  border: 1px solid rgba(56, 189, 248, 0.18) !important;
  box-shadow: 0 12px 28px rgba(14, 165, 233, 0.10), inset 0 1px 0 rgba(255, 255, 255, 0.07) !important;
}

[data-wilsy-account-command-center="true"] .wilsy-r7c-identity-content {
  min-width: 0 !important;
  display: grid !important;
  grid-template-rows: auto auto auto 52px !important;
  gap: 8px !important;
  align-items: center !important;
}

[data-wilsy-account-command-center="true"] .wilsy-r7c-identity-eyebrow {
  display: flex !important;
  align-items: center !important;
  justify-content: space-between !important;
  gap: 10px !important;
  min-width: 0 !important;
}

[data-wilsy-account-command-center="true"] .wilsy-r7c-command-label {
  color: #94a3b8 !important;
  font-size: 10px !important;
  line-height: 1 !important;
  font-weight: 850 !important;
  letter-spacing: 0.18em !important;
  text-transform: uppercase !important;
  white-space: nowrap !important;
}

[data-wilsy-account-command-center="true"] .wilsy-r7c-verified-label {
  color: var(--wilsy-r7c-success) !important;
  font-size: 9px !important;
  line-height: 1 !important;
  font-weight: 820 !important;
  letter-spacing: 0.12em !important;
  text-transform: uppercase !important;
  white-space: nowrap !important;
}

[data-wilsy-account-command-center="true"] .wilsy-r7c-verified-label::before {
  content: "\\u25cf";
  margin-right: 6px;
}

[data-wilsy-account-command-center="true"] .wilsy-r7c-identity-name {
  color: var(--wilsy-r7c-text) !important;
  font-size: clamp(18px, 1.12vw, 25px) !important;
  line-height: 1.05 !important;
  letter-spacing: -0.025em !important;
  font-weight: 820 !important;
  max-width: 100% !important;
  white-space: nowrap !important;
  overflow: hidden !important;
  text-overflow: ellipsis !important;
}

[data-wilsy-account-command-center="true"] .wilsy-r7c-identity-account {
  color: var(--wilsy-r7c-muted) !important;
  font-size: clamp(10px, 0.66vw, 12px) !important;
  line-height: 1.1 !important;
  max-width: 100% !important;
  white-space: nowrap !important;
  overflow: hidden !important;
  text-overflow: ellipsis !important;
}

[data-wilsy-account-command-center="true"] .wilsy-r7c-identity-content::before {
  content: "";
  width: 100%;
  height: 1px;
  background: linear-gradient(90deg, transparent 0%, rgba(148, 163, 184, 0.28) 18%, rgba(148, 163, 184, 0.12) 100%);
}

[data-wilsy-account-command-center="true"] .wilsy-r7c-tenant-pill {
  height: 52px !important;
  min-height: 52px !important;
  display: grid !important;
  grid-template-columns: 28px minmax(0, 1fr) 18px !important;
  align-items: center !important;
  gap: 10px !important;
  padding: 18px 12px 8px !important;
  border-radius: 12px !important;
  border: 1px solid rgba(148, 163, 184, 0.32) !important;
  background: rgba(5, 8, 20, 0.78) !important;
  position: relative !important;
}

[data-wilsy-account-command-center="true"] .wilsy-r7c-tenant-pill::before {
  content: "TENANT SCOPE";
  position: absolute;
  top: 7px;
  left: 50px;
  color: #94a3b8;
  font-size: 8px;
  line-height: 1;
  letter-spacing: 0.16em;
  font-weight: 850;
}

[data-wilsy-account-command-center="true"] .wilsy-r7c-tenant-icon {
  color: var(--wilsy-r7c-success) !important;
  font-size: 20px !important;
}

[data-wilsy-account-command-center="true"] .wilsy-r7c-tenant-text {
  color: var(--wilsy-r7c-text) !important;
  font-size: clamp(12px, 0.76vw, 15px) !important;
  line-height: 1 !important;
  font-weight: 760 !important;
  min-width: 0 !important;
  white-space: nowrap !important;
  overflow: hidden !important;
  text-overflow: ellipsis !important;
}

[data-wilsy-account-command-center="true"] .wilsy-r7c-tenant-chevron {
  color: #cbd5e1 !important;
  font-size: 15px !important;
}

/* Right narrative: not a duplicate identity headline. */
[data-wilsy-account-command-center="true"] [data-wilsy-role~="account-role-narrative"] {
  grid-column: 2 / 3 !important;
  grid-row: 1 / 2 !important;
  min-height: 100px !important;
  max-height: 112px !important;
  padding: 18px 118px 16px 26px !important;
  border-radius: 22px !important;
  border: 1px solid rgba(148, 163, 184, 0.13) !important;
  background: linear-gradient(135deg, rgba(8, 13, 26, 0.90) 0%, rgba(3, 7, 17, 0.80) 100%) !important;
  display: grid !important;
  grid-template-columns: minmax(136px, 0.20fr) minmax(0, 1fr) !important;
  gap: 5px 22px !important;
  align-items: center !important;
  overflow: hidden !important;
}

[data-wilsy-account-command-center="true"] [data-wilsy-role~="account-role-narrative"] strong {
  font-size: 0 !important;
  line-height: 0 !important;
  overflow: hidden !important;
}

[data-wilsy-account-command-center="true"] [data-wilsy-role~="account-role-narrative"] strong::before {
  content: "Command authority and operating posture.";
  display: block;
  color: var(--wilsy-r7c-text);
  font-size: clamp(17px, 1.24vw, 24px);
  line-height: 1.08;
  font-weight: 820;
  letter-spacing: -0.018em;
}

[data-wilsy-account-command-center="true"] [data-wilsy-role~="account-role-narrative"] p {
  color: #dbe2ee !important;
  font-size: clamp(11px, 0.72vw, 13px) !important;
  line-height: 1.32 !important;
  margin: 0 !important;
}

[data-wilsy-account-command-center="true"] [data-wilsy-role~="account-role-narrative"] small {
  font-size: 0 !important;
  line-height: 0 !important;
}

[data-wilsy-account-command-center="true"] [data-wilsy-role~="account-role-narrative"]::after {
  content: "KNOWN FOR  \\u2022  FORENSIC COMMAND INTELLIGENCE";
  grid-column: 1 / -1;
  color: #94a3b8;
  font-size: 9px;
  font-weight: 850;
  letter-spacing: 0.16em;
  text-transform: uppercase;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

/* Signal cards follow the cockpit reference. */
[data-wilsy-account-command-center="true"] [data-wilsy-role~="account-story"] {
  grid-column: 2 / 3 !important;
  grid-row: 2 / 3 !important;
  display: grid !important;
  grid-template-columns: repeat(4, minmax(0, 1fr)) !important;
  gap: 12px !important;
  width: 100% !important;
  max-width: 100% !important;
  overflow: hidden !important;
}

[data-wilsy-account-command-center="true"] [data-wilsy-role~="account-story-tile"] {
  position: relative !important;
  min-height: 92px !important;
  max-height: 104px !important;
  padding: 16px 14px 14px 72px !important;
  border-radius: 15px !important;
  border: 1px solid rgba(56, 189, 248, 0.20) !important;
  background: linear-gradient(135deg, rgba(10, 18, 32, 0.90) 0%, rgba(5, 8, 20, 0.74) 100%) !important;
  overflow: hidden !important;
  align-content: center !important;
}

[data-wilsy-account-command-center="true"] [data-wilsy-role~="account-story-tile"]::before {
  content: "";
  position: absolute;
  left: 0;
  top: 12px;
  bottom: 12px;
  width: 3px;
  border-radius: 999px;
  background: linear-gradient(180deg, #38bdf8 0%, #0ea5e9 100%);
  box-shadow: 0 0 20px rgba(56, 189, 248, 0.36);
}

[data-wilsy-account-command-center="true"] [data-wilsy-role~="account-story-tile"]::after {
  content: "\\u25ce";
  position: absolute;
  left: 22px;
  top: 50%;
  width: 38px;
  height: 38px;
  transform: translateY(-50%);
  display: grid;
  place-items: center;
  border-radius: 10px;
  color: #e5e7eb;
  font-size: 18px;
  border: 1px solid rgba(148, 163, 184, 0.28);
  background: rgba(15, 23, 42, 0.72);
}

[data-wilsy-account-command-center="true"] [data-wilsy-role~="account-story-tile"] span {
  color: #38bdf8 !important;
  font-size: 8px !important;
  line-height: 1 !important;
  letter-spacing: 0.16em !important;
  font-weight: 850 !important;
}

[data-wilsy-account-command-center="true"] [data-wilsy-role~="account-story-tile"] strong {
  display: block !important;
  color: var(--wilsy-r7c-text) !important;
  font-size: clamp(13px, 0.92vw, 17px) !important;
  line-height: 1.06 !important;
  margin-top: 5px !important;
  white-space: normal !important;
  overflow: hidden !important;
  text-overflow: ellipsis !important;
}

[data-wilsy-account-command-center="true"] [data-wilsy-role~="account-story-tile"] small {
  display: block !important;
  color: var(--wilsy-r7c-muted) !important;
  font-size: clamp(9px, 0.58vw, 11px) !important;
  line-height: 1.18 !important;
  margin-top: 4px !important;
  white-space: nowrap !important;
  overflow: hidden !important;
  text-overflow: ellipsis !important;
}

/* Tab rail. */
[data-wilsy-account-command-center="true"] [data-wilsy-role~="account-command-tabs"] {
  padding: 14px 32px 18px !important;
  gap: 18px !important;
  border-top: 1px solid rgba(148, 163, 184, 0.12) !important;
  background: linear-gradient(180deg, rgba(7, 16, 31, 0.96) 0%, rgba(3, 7, 17, 0.98) 100%) !important;
}

[data-wilsy-account-command-center="true"] [data-wilsy-role~="account-command-tabs"] button {
  min-height: 58px !important;
  border-radius: 18px !important;
  border: 1px solid rgba(148, 163, 184, 0.26) !important;
  background: linear-gradient(135deg, rgba(10, 18, 32, 0.84) 0%, rgba(5, 8, 20, 0.78) 100%) !important;
  font-size: clamp(13px, 0.86vw, 16px) !important;
}

[data-wilsy-account-command-center="true"] [data-wilsy-role~="account-command-body"] {
  padding-top: 0 !important;
}

@media (max-width: 1360px) {
  [data-wilsy-account-command-center="true"] {
    --wilsy-r7c-identity-width: clamp(320px, 25vw, 390px);
    --wilsy-r7c-header-max: none;
  }

  [data-wilsy-account-command-center="true"] [data-wilsy-role~="account-command-header"] {
    max-height: none !important;
    grid-template-columns: var(--wilsy-r7c-identity-width) minmax(0, 1fr) !important;
  }

  [data-wilsy-account-command-center="true"] [data-wilsy-role~="account-story"] {
    grid-template-columns: repeat(2, minmax(0, 1fr)) !important;
  }
}

@media (max-width: 980px) {
  [data-wilsy-account-command-center="true"] [data-wilsy-role~="account-command-header"] {
    display: flex !important;
    flex-direction: column !important;
    padding: 62px 18px 16px !important;
  }

  [data-wilsy-account-command-center="true"] [data-wilsy-identity-chrome][data-wilsy-r7c-identity-card="true"] {
    max-width: none !important;
    height: 220px !important;
    max-height: 220px !important;
  }

  [data-wilsy-account-command-center="true"] [data-wilsy-role~="account-role-narrative"] {
    max-height: none !important;
    padding-right: 18px !important;
    grid-template-columns: minmax(0, 1fr) !important;
  }

  [data-wilsy-account-command-center="true"] [data-wilsy-role~="account-story"] {
    grid-template-columns: minmax(0, 1fr) !important;
  }
}


/* WILSY_R7E_SIGNAL_INTELLIGENCE_COCKPIT */
[data-wilsy-account-command-center="true"] [data-wilsy-role~="account-role-narrative"] {
  transition: all 0.25s ease-in-out !important;
  border-color: rgba(148, 163, 184, 0.20) !important;
  box-shadow: inset 0 1px 0 rgba(255, 255, 255, 0.045), 0 18px 44px rgba(0, 0, 0, 0.22) !important;
}

[data-wilsy-account-command-center="true"] [data-wilsy-role~="account-role-narrative"] strong::before {
  font-weight: 880 !important;
  letter-spacing: -0.022em !important;
}

[data-wilsy-account-command-center="true"] [data-wilsy-role~="account-story"] {
  grid-template-columns: minmax(0, 1.14fr) minmax(0, 1fr) minmax(0, 1fr) minmax(0, 0.92fr) !important;
  align-items: stretch !important;
  gap: 14px !important;
}

/* Forensic signal cards: hierarchy, motion, evidence. */
[data-wilsy-account-command-center="true"] [data-wilsy-r7e-signal-tile="true"] {
  isolation: isolate !important;
  cursor: pointer !important;
  transition: all 0.25s ease-in-out !important;
  transform: translate3d(0, 0, 0) !important;
  padding-bottom: 34px !important;
  min-height: 122px !important;
  max-height: 140px !important;
  text-align: left !important;
}

[data-wilsy-account-command-center="true"] [data-wilsy-r7e-signal-tile="true"]:hover,
[data-wilsy-account-command-center="true"] [data-wilsy-r7e-signal-tile="true"]:focus-visible {
  transform: translate3d(0, -2px, 0) !important;
  border-color: rgba(212, 175, 55, 0.48) !important;
  box-shadow:
    0 0 0 1px rgba(212, 175, 55, 0.10),
    0 0 18px rgba(212, 175, 55, 0.20),
    0 18px 44px rgba(0, 0, 0, 0.32) !important;
  outline: none !important;
}

[data-wilsy-account-command-center="true"] [data-wilsy-r7e-signal-tile="true"] span {
  text-transform: uppercase !important;
  letter-spacing: 0.18em !important;
  font-weight: 900 !important;
  margin-bottom: 6px !important;
}

[data-wilsy-account-command-center="true"] [data-wilsy-r7e-signal-tile="true"] strong {
  font-weight: 860 !important;
  letter-spacing: -0.018em !important;
  margin-bottom: 6px !important;
}

[data-wilsy-account-command-center="true"] [data-wilsy-r7e-signal-tile="true"] small {
  line-height: 1.35 !important;
  white-space: normal !important;
}

[data-wilsy-account-command-center="true"] [data-wilsy-r7e-priority="primary"] {
  border-color: rgba(212, 175, 55, 0.28) !important;
}

[data-wilsy-account-command-center="true"] [data-wilsy-r7e-priority="primary"]::before {
  background: linear-gradient(180deg, #d4af37 0%, #38bdf8 100%) !important;
}

[data-wilsy-account-command-center="true"] [data-wilsy-r7e-priority="watch"]::before {
  background: linear-gradient(180deg, #f59e0b 0%, #38bdf8 100%) !important;
}

[data-wilsy-account-command-center="true"] [data-wilsy-r7e-evidence="true"] {
  position: absolute !important;
  left: 72px !important;
  right: 14px !important;
  bottom: 12px !important;
  display: flex !important;
  align-items: center !important;
  justify-content: space-between !important;
  gap: 10px !important;
  pointer-events: none !important;
}

[data-wilsy-account-command-center="true"] .wilsy-r7e-evidence-anchor,
[data-wilsy-account-command-center="true"] .wilsy-r7e-evidence-seal {
  font-family: var(--wilsy-font-mono, ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace) !important;
  font-size: 9px !important;
  line-height: 1 !important;
  font-weight: 760 !important;
  letter-spacing: 0.08em !important;
  color: rgba(203, 213, 225, 0.78) !important;
  white-space: nowrap !important;
  overflow: hidden !important;
  text-overflow: ellipsis !important;
}

[data-wilsy-account-command-center="true"] .wilsy-r7e-evidence-seal {
  color: rgba(212, 175, 55, 0.88) !important;
}

/* Sovereign drilldown overlay. */
[data-wilsy-r7e-signal-overlay="true"] {
  position: fixed !important;
  inset: 0 !important;
  z-index: 9998 !important;
  display: grid !important;
  place-items: center !important;
  padding: 24px !important;
  background: rgba(2, 6, 23, 0.72) !important;
  backdrop-filter: blur(6px) !important;
  transition: opacity 0.25s ease-in-out !important;
}

[data-wilsy-r7e-signal-overlay="true"][hidden] {
  display: none !important;
}

.wilsy-r7e-signal-panel {
  width: min(680px, 94vw) !important;
  border-radius: 24px !important;
  border: 1px solid rgba(148, 163, 184, 0.28) !important;
  background:
    radial-gradient(circle at 0% 0%, rgba(56, 189, 248, 0.12) 0%, transparent 35%),
    linear-gradient(135deg, rgba(10, 18, 32, 0.98) 0%, rgba(3, 7, 17, 0.98) 100%) !important;
  box-shadow: 0 36px 90px rgba(0, 0, 0, 0.52) !important;
  padding: 26px !important;
  color: #f8fafc !important;
  transform: translate3d(0, 0, 0) !important;
  transition: all 0.25s ease-in-out !important;
}

.wilsy-r7e-signal-close {
  float: right !important;
  border: 1px solid rgba(148, 163, 184, 0.26) !important;
  background: rgba(15, 23, 42, 0.72) !important;
  color: #e5e7eb !important;
  border-radius: 12px !important;
  padding: 8px 12px !important;
  font-weight: 760 !important;
  cursor: pointer !important;
}

.wilsy-r7e-signal-eyebrow {
  color: #38bdf8 !important;
  font-size: 10px !important;
  font-weight: 900 !important;
  letter-spacing: 0.18em !important;
  text-transform: uppercase !important;
  margin-bottom: 12px !important;
}

.wilsy-r7e-signal-title {
  font-size: clamp(24px, 2.4vw, 34px) !important;
  line-height: 1.05 !important;
  letter-spacing: -0.03em !important;
  margin: 0 0 12px !important;
}

.wilsy-r7e-signal-narrative,
.wilsy-r7e-signal-telemetry {
  color: #cbd5e1 !important;
  font-size: 14px !important;
  line-height: 1.5 !important;
  margin: 0 0 12px !important;
}

.wilsy-r7e-signal-evidence {
  display: block !important;
  color: #d4af37 !important;
  background: rgba(2, 6, 23, 0.46) !important;
  border: 1px solid rgba(212, 175, 55, 0.18) !important;
  border-radius: 14px !important;
  padding: 12px !important;
  font-size: 12px !important;
  letter-spacing: 0.08em !important;
  white-space: normal !important;
}

@media (max-width: 1360px) {
  [data-wilsy-account-command-center="true"] [data-wilsy-role~="account-story"] {
    grid-template-columns: repeat(2, minmax(0, 1fr)) !important;
  }
}

@media (max-width: 760px) {
  [data-wilsy-account-command-center="true"] [data-wilsy-role~="account-story"] {
    grid-template-columns: minmax(0, 1fr) !important;
  }

  [data-wilsy-account-command-center="true"] [data-wilsy-r7e-signal-tile="true"] {
    min-height: 130px !important;
  }
}


/* WILSY_R7F_IDENTITY_HIERARCHY_EVIDENCE */
[data-wilsy-account-command-center="true"] [data-wilsy-identity-chrome][data-wilsy-r7c-identity-card="true"] {
  transition: all 0.25s ease-in-out !important;
  transform: translate3d(0, 0, 0) !important;
}

[data-wilsy-account-command-center="true"] [data-wilsy-identity-chrome][data-wilsy-r7c-identity-card="true"]:hover {
  transform: translate3d(0, -2px, 0) !important;
  border-color: rgba(34, 197, 94, 0.34) !important;
  box-shadow:
    0 0 0 1px rgba(34, 197, 94, 0.10),
    0 0 18px rgba(34, 197, 94, 0.14),
    0 22px 56px rgba(0, 0, 0, 0.38) !important;
}

/* Kill the old legacy pseudo label/divider. R7C renderer is the only visible identity source. */
[data-wilsy-account-command-center="true"] [data-wilsy-identity-chrome][data-wilsy-r7c-identity-card="true"]::before,
[data-wilsy-account-command-center="true"] [data-wilsy-identity-chrome][data-wilsy-r7c-identity-card="true"]::after,
[data-wilsy-account-command-center="true"] [data-wilsy-identity-chrome]::before,
[data-wilsy-account-command-center="true"] [data-wilsy-identity-chrome]::after {
  content: none !important;
  display: none !important;
  opacity: 0 !important;
  visibility: hidden !important;
}

/* Extra suppression for legacy children that were bleeding one-letter artifacts. */
[data-wilsy-account-command-center="true"] [data-wilsy-identity-chrome][data-wilsy-r7c-identity-card="true"] > :not([data-wilsy-r7c-identity-ui="true"]) {
  opacity: 0 !important;
  visibility: hidden !important;
  color: transparent !important;
  text-shadow: none !important;
  font-size: 0 !important;
  line-height: 0 !important;
  pointer-events: none !important;
}

/* Keep the real select clickable through the clean rendered tenant pill. */
[data-wilsy-account-command-center="true"] [data-wilsy-identity-chrome][data-wilsy-r7c-identity-card="true"] [data-wilsy-tenant-scope-select],
[data-wilsy-account-command-center="true"] [data-wilsy-identity-chrome][data-wilsy-r7c-identity-card="true"] select {
  opacity: 0 !important;
  visibility: visible !important;
  color: transparent !important;
  pointer-events: auto !important;
  z-index: 12 !important;
}

/* The rendered identity layer becomes a disciplined grid. */
[data-wilsy-account-command-center="true"] [data-wilsy-r7c-identity-ui="true"] {
  padding: 28px 34px !important;
  grid-template-columns: 76px minmax(0, 1fr) !important;
  gap: 18px !important;
  align-items: center !important;
}

[data-wilsy-account-command-center="true"] .wilsy-r7c-identity-content {
  grid-template-rows: auto auto auto auto 52px !important;
  gap: 7px !important;
  padding-right: 4px !important;
}

/* One sovereign header row only. TENANT VERIFIED is secondary, not pinned to the card edge. */
[data-wilsy-account-command-center="true"] .wilsy-r7c-identity-eyebrow {
  justify-content: flex-start !important;
  gap: 14px !important;
  padding: 0 !important;
  margin: 0 0 3px !important;
  min-width: 0 !important;
}

[data-wilsy-account-command-center="true"] .wilsy-r7c-command-label {
  color: #aab6c8 !important;
  font-size: 10px !important;
  line-height: 1 !important;
  font-weight: 900 !important;
  letter-spacing: 0.20em !important;
  text-transform: uppercase !important;
}

[data-wilsy-account-command-center="true"] .wilsy-r7c-verified-label {
  color: #22c55e !important;
  font-size: 10px !important;
  line-height: 1 !important;
  font-weight: 900 !important;
  letter-spacing: 0.16em !important;
  text-transform: uppercase !important;
  white-space: nowrap !important;
}

[data-wilsy-account-command-center="true"] .wilsy-r7c-verified-label::before {
  content: "\\u25cf" !important;
  margin-right: 7px !important;
  font-size: 11px !important;
}

/* Strong identity title with disciplined spacing. */
[data-wilsy-account-command-center="true"] .wilsy-r7c-identity-name {
  margin-top: 3px !important;
  font-size: clamp(20px, 1.24vw, 27px) !important;
  line-height: 1.05 !important;
  font-weight: 860 !important;
  letter-spacing: -0.028em !important;
}

/* Account reference = forensic typography. */
[data-wilsy-account-command-center="true"] .wilsy-r7c-identity-account {
  font-family: var(--wilsy-font-mono, ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace) !important;
  color: #a7b1c2 !important;
  font-size: clamp(10px, 0.66vw, 12px) !important;
  letter-spacing: 0.02em !important;
}

/* Clause anchor + deterministic seal. */
[data-wilsy-account-command-center="true"] .wilsy-r7f-identity-evidence {
  display: flex !important;
  align-items: center !important;
  justify-content: flex-start !important;
  gap: 10px !important;
  min-width: 0 !important;
  padding-top: 2px !important;
}

[data-wilsy-account-command-center="true"] .wilsy-r7f-clause-anchor,
[data-wilsy-account-command-center="true"] .wilsy-r7f-identity-seal {
  font-family: var(--wilsy-font-mono, ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace) !important;
  font-size: 9px !important;
  line-height: 1 !important;
  font-weight: 760 !important;
  letter-spacing: 0.08em !important;
  white-space: nowrap !important;
  overflow: hidden !important;
  text-overflow: ellipsis !important;
}

[data-wilsy-account-command-center="true"] .wilsy-r7f-clause-anchor {
  color: rgba(34, 197, 94, 0.90) !important;
}

[data-wilsy-account-command-center="true"] .wilsy-r7f-identity-seal {
  color: rgba(212, 175, 55, 0.88) !important;
}

[data-wilsy-account-command-center="true"] .wilsy-r7c-tenant-pill {
  margin-top: 5px !important;
  height: 54px !important;
  min-height: 54px !important;
  border-radius: 14px !important;
  border-color: rgba(148, 163, 184, 0.34) !important;
}

[data-wilsy-account-command-center="true"] .wilsy-r7c-tenant-pill::before {
  left: 52px !important;
  top: 7px !important;
  color: #aab6c8 !important;
  font-size: 8px !important;
  font-weight: 900 !important;
  letter-spacing: 0.18em !important;
}

[data-wilsy-account-command-center="true"] .wilsy-r7c-tenant-text {
  font-weight: 820 !important;
}

@media (max-width: 980px) {
  [data-wilsy-account-command-center="true"] [data-wilsy-r7c-identity-ui="true"] {
    padding: 26px 28px !important;
  }

  [data-wilsy-account-command-center="true"] .wilsy-r7c-identity-eyebrow {
    flex-wrap: wrap !important;
    row-gap: 6px !important;
  }
}


/* WILSY_R7G_TENANT_VERIFIED_NO_CLIP */
[data-wilsy-account-command-center="true"] [data-wilsy-r7c-identity-ui="true"] {
  grid-template-columns: 68px minmax(0, 1fr) !important;
  gap: 16px !important;
  padding: 28px 30px !important;
  overflow: hidden !important;
}

[data-wilsy-account-command-center="true"] .wilsy-r7c-identity-content {
  min-width: 0 !important;
  max-width: 100% !important;
  overflow: hidden !important;
}

/* Protected two-lane eyebrow: command label gets left lane, verified gets right lane. */
[data-wilsy-account-command-center="true"] .wilsy-r7c-identity-eyebrow {
  width: 100% !important;
  min-width: 0 !important;
  max-width: 100% !important;
  display: grid !important;
  grid-template-columns: minmax(0, 1fr) max-content !important;
  align-items: center !important;
  column-gap: 10px !important;
  justify-content: stretch !important;
  overflow: hidden !important;
  padding: 0 !important;
  margin: 0 0 4px !important;
}

/* Left label may truncate gracefully; right badge must never be cut. */
[data-wilsy-account-command-center="true"] .wilsy-r7c-command-label {
  min-width: 0 !important;
  max-width: 100% !important;
  overflow: hidden !important;
  text-overflow: ellipsis !important;
  white-space: nowrap !important;
  letter-spacing: 0.16em !important;
  font-size: 9px !important;
}

[data-wilsy-account-command-center="true"] .wilsy-r7c-verified-label {
  justify-self: end !important;
  width: max-content !important;
  max-width: none !important;
  flex: 0 0 auto !important;
  overflow: visible !important;
  text-overflow: clip !important;
  white-space: nowrap !important;
  letter-spacing: 0.10em !important;
  font-size: 9px !important;
  line-height: 1 !important;
  padding-inline: 0 !important;
}

[data-wilsy-account-command-center="true"] .wilsy-r7c-verified-label::before {
  margin-right: 6px !important;
  font-size: 10px !important;
}

/* Stop the invisible legacy layer from leaving one-letter artifacts. */
[data-wilsy-account-command-center="true"] [data-wilsy-identity-chrome][data-wilsy-r7c-identity-card="true"] > :not([data-wilsy-r7c-identity-ui="true"]) {
  opacity: 0 !important;
  visibility: hidden !important;
  color: transparent !important;
  text-shadow: none !important;
  font-size: 0 !important;
  line-height: 0 !important;
  overflow: hidden !important;
  max-width: 0 !important;
  max-height: 0 !important;
  pointer-events: none !important;
}

/* Keep the real hidden select clickable through the rendered tenant pill. */
[data-wilsy-account-command-center="true"] [data-wilsy-identity-chrome][data-wilsy-r7c-identity-card="true"] [data-wilsy-tenant-scope-select],
[data-wilsy-account-command-center="true"] [data-wilsy-identity-chrome][data-wilsy-r7c-identity-card="true"] select {
  max-width: none !important;
  max-height: none !important;
  opacity: 0 !important;
  visibility: visible !important;
  pointer-events: auto !important;
  z-index: 12 !important;
}

[data-wilsy-account-command-center="true"] .wilsy-r7c-identity-name,
[data-wilsy-account-command-center="true"] .wilsy-r7c-identity-account,
[data-wilsy-account-command-center="true"] .wilsy-r7f-identity-evidence,
[data-wilsy-account-command-center="true"] .wilsy-r7c-tenant-pill {
  min-width: 0 !important;
  max-width: 100% !important;
}


/* WILSY_R7H_PREFERENCES_NAV_MODE_AUTHORITY */
[data-wilsy-account-command-center="true"] [data-wilsy-role~="account-command-tabs"] {
  align-items: center !important;
  gap: 18px !important;
}

[data-wilsy-account-command-center="true"] [data-wilsy-r7h-tab-button="true"] {
  position: relative !important;
  isolation: isolate !important;
  transition: all 0.25s ease-in-out !important;
  transform: translate3d(0, 0, 0) !important;
  font-weight: 760 !important;
  letter-spacing: -0.01em !important;
  border-color: rgba(148, 163, 184, 0.24) !important;
}

[data-wilsy-account-command-center="true"] [data-wilsy-r7h-tab-button="true"]:hover {
  transform: translate3d(0, -2px, 0) !important;
  border-color: rgba(212, 175, 55, 0.34) !important;
  box-shadow: 0 0 14px rgba(212, 175, 55, 0.12) !important;
}

[data-wilsy-account-command-center="true"] [data-wilsy-r7h-active-tab="true"] {
  color: #f8fafc !important;
  border-color: rgba(212, 175, 55, 0.62) !important;
  box-shadow:
    0 0 0 1px rgba(212, 175, 55, 0.16),
    0 0 20px rgba(212, 175, 55, 0.22),
    inset 0 1px 0 rgba(255, 255, 255, 0.06) !important;
  font-weight: 880 !important;
}

[data-wilsy-account-command-center="true"] [data-wilsy-r7h-active-tab="true"]::after {
  content: "ACTIVE" !important;
  position: absolute !important;
  right: 18px !important;
  top: 10px !important;
  color: rgba(212, 175, 55, 0.92) !important;
  font-family: var(--wilsy-font-mono, ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace) !important;
  font-size: 8px !important;
  line-height: 1 !important;
  font-weight: 850 !important;
  letter-spacing: 0.14em !important;
  text-transform: uppercase !important;
}

[data-wilsy-account-command-center="true"] [data-wilsy-r7h-preferences-title="true"] {
  letter-spacing: -0.035em !important;
  line-height: 1.02 !important;
  margin-bottom: 12px !important;
}

[data-wilsy-account-command-center="true"] [data-wilsy-r7h-preferences-description="true"] {
  max-width: 920px !important;
  color: rgba(226, 232, 240, 0.88) !important;
  line-height: 1.55 !important;
  letter-spacing: -0.01em !important;
}

/* Mode badge becomes the dominant current-state signal. */
[data-wilsy-account-command-center="true"] [data-wilsy-r7h-mode-state-badge="true"] {
  position: relative !important;
  display: inline-flex !important;
  align-items: center !important;
  justify-content: center !important;
  min-width: 112px !important;
  min-height: 46px !important;
  padding: 16px 18px 8px !important;
  border-radius: 999px !important;
  border: 1px solid rgba(212, 175, 55, 0.30) !important;
  background:
    radial-gradient(circle at 20% 0%, rgba(212, 175, 55, 0.14) 0%, transparent 44%),
    rgba(10, 18, 32, 0.72) !important;
  box-shadow: inset 0 1px 0 rgba(255, 255, 255, 0.045) !important;
  color: #f8fafc !important;
  font-weight: 900 !important;
  letter-spacing: 0.18em !important;
  text-transform: uppercase !important;
}

[data-wilsy-account-command-center="true"] [data-wilsy-r7h-mode-state-badge="true"]::before {
  content: "ACTIVE MODE" !important;
  position: absolute !important;
  top: 7px !important;
  color: rgba(212, 175, 55, 0.86) !important;
  font-family: var(--wilsy-font-mono, ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace) !important;
  font-size: 7px !important;
  line-height: 1 !important;
  font-weight: 850 !important;
  letter-spacing: 0.14em !important;
}

/* Mode controls communicate meaning, not just icons. */
[data-wilsy-account-command-center="true"] [data-wilsy-r7h-mode-option] {
  position: relative !important;
  display: grid !important;
  align-content: center !important;
  justify-items: center !important;
  gap: 8px !important;
  min-height: 116px !important;
  padding: 20px 18px !important;
  transition: all 0.25s ease-in-out !important;
  transform: translate3d(0, 0, 0) !important;
  border-color: rgba(148, 163, 184, 0.24) !important;
}

[data-wilsy-account-command-center="true"] [data-wilsy-r7h-mode-option]:hover {
  transform: translate3d(0, -2px, 0) !important;
  border-color: rgba(212, 175, 55, 0.36) !important;
  box-shadow: 0 0 16px rgba(212, 175, 55, 0.16) !important;
}

[data-wilsy-account-command-center="true"] [data-wilsy-r7h-active-mode="true"] {
  border-color: rgba(212, 175, 55, 0.58) !important;
  box-shadow:
    0 0 0 1px rgba(212, 175, 55, 0.12),
    0 0 20px rgba(212, 175, 55, 0.20) !important;
}

[data-wilsy-account-command-center="true"] [data-wilsy-r7h-active-mode="true"]::after {
  content: "SELECTED" !important;
  position: absolute !important;
  right: 14px !important;
  top: 12px !important;
  color: rgba(212, 175, 55, 0.92) !important;
  font-family: var(--wilsy-font-mono, ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace) !important;
  font-size: 8px !important;
  font-weight: 850 !important;
  letter-spacing: 0.12em !important;
}

[data-wilsy-account-command-center="true"] [data-wilsy-r7h-mode-meta="true"] {
  display: block !important;
  max-width: 280px !important;
  color: rgba(203, 213, 225, 0.76) !important;
  font-size: 11px !important;
  line-height: 1.35 !important;
  font-weight: 560 !important;
  letter-spacing: -0.01em !important;
  text-align: center !important;
  pointer-events: none !important;
}


/* WILSY_R7I_MODE_SELECTOR_SOVEREIGN_ACTIVE_STATE */
[data-wilsy-account-command-center="true"] [data-wilsy-r7i-mode-button="true"] {
  position: relative !important;
  isolation: isolate !important;
  display: grid !important;
  grid-template-rows: auto auto auto !important;
  align-content: center !important;
  justify-items: center !important;
  gap: 9px !important;
  min-height: 126px !important;
  padding: 22px 24px !important;
  border-radius: 22px !important;
  border: 1px solid rgba(148, 163, 184, 0.24) !important;
  background:
    radial-gradient(circle at 50% 0%, rgba(148, 163, 184, 0.08) 0%, transparent 52%),
    rgba(10, 18, 32, 0.62) !important;
  cursor: pointer !important;
  transition: all 0.25s ease-in-out !important;
  transform: translate3d(0, 0, 0) !important;
  color: rgba(226, 232, 240, 0.66) !important;
}

[data-wilsy-account-command-center="true"] [data-wilsy-r7i-mode-button="true"]:hover {
  transform: translate3d(0, -2px, 0) !important;
  border-color: rgba(212, 175, 55, 0.34) !important;
  color: rgba(248, 250, 252, 0.92) !important;
  box-shadow:
    0 0 0 1px rgba(212, 175, 55, 0.08),
    0 0 18px rgba(212, 175, 55, 0.12) !important;
}

[data-wilsy-account-command-center="true"] [data-wilsy-r7i-active-mode="true"] {
  border: 2px solid rgba(212, 175, 55, 0.70) !important;
  background:
    radial-gradient(circle at 50% 0%, rgba(212, 175, 55, 0.18) 0%, transparent 54%),
    linear-gradient(135deg, rgba(10, 18, 32, 0.92) 0%, rgba(5, 8, 20, 0.82) 100%) !important;
  color: #f8fafc !important;
  box-shadow:
    0 0 0 1px rgba(212, 175, 55, 0.16),
    0 0 22px rgba(212, 175, 55, 0.28),
    inset 0 1px 0 rgba(255, 255, 255, 0.07) !important;
}

[data-wilsy-account-command-center="true"] [data-wilsy-r7i-active-mode="true"]::before {
  content: "ACTIVE MODE" !important;
  position: absolute !important;
  top: 14px !important;
  right: 16px !important;
  color: rgba(212, 175, 55, 0.94) !important;
  font-family: var(--wilsy-font-mono, ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace) !important;
  font-size: 8px !important;
  line-height: 1 !important;
  font-weight: 850 !important;
  letter-spacing: 0.13em !important;
  text-transform: uppercase !important;
}

[data-wilsy-account-command-center="true"] [data-wilsy-r7i-mode-button="true"] svg {
  width: 24px !important;
  height: 24px !important;
  margin: 0 !important;
  color: currentColor !important;
  stroke: currentColor !important;
  opacity: 0.84 !important;
}

[data-wilsy-account-command-center="true"] [data-wilsy-r7i-mode-label="true"] {
  color: currentColor !important;
  font-size: clamp(13px, 0.86vw, 16px) !important;
  line-height: 1 !important;
  font-weight: 880 !important;
  letter-spacing: 0.04em !important;
  text-transform: uppercase !important;
  text-align: center !important;
}

[data-wilsy-account-command-center="true"] [data-wilsy-r7i-mode-description="true"] {
  display: block !important;
  max-width: 280px !important;
  color: rgba(203, 213, 225, 0.72) !important;
  font-size: 11px !important;
  line-height: 1.35 !important;
  font-weight: 560 !important;
  letter-spacing: -0.01em !important;
  text-align: center !important;
  pointer-events: none !important;
}

[data-wilsy-account-command-center="true"] [data-wilsy-r7i-active-mode="true"] [data-wilsy-r7i-mode-description="true"] {
  color: rgba(226, 232, 240, 0.88) !important;
}

[data-wilsy-account-command-center="true"] [data-wilsy-r7i-mode-indicator="true"] {
  width: 9px !important;
  height: 9px !important;
  border-radius: 999px !important;
  display: block !important;
  background: rgba(100, 116, 139, 0.70) !important;
  box-shadow: none !important;
  transition: all 0.25s ease-in-out !important;
}

[data-wilsy-account-command-center="true"] [data-wilsy-r7i-active-mode="true"] [data-wilsy-r7i-mode-indicator="true"] {
  background: #d4af37 !important;
  box-shadow:
    0 0 0 5px rgba(212, 175, 55, 0.12),
    0 0 16px rgba(212, 175, 55, 0.68) !important;
}

[data-wilsy-account-command-center="true"] [data-wilsy-r7i-mode-button="true"][data-wilsy-r7i-active-mode="false"] {
  opacity: 0.72 !important;
}

[data-wilsy-account-command-center="true"] [data-wilsy-r7i-mode-button="true"][data-wilsy-r7i-active-mode="false"]:hover {
  opacity: 0.94 !important;
}




/* WILSY_R7J_PERFORMANCE_SAFE_AUTHORITY_PANELS */
[data-wilsy-account-command-center="true"] [data-wilsy-role~="account-role-narrative"] {
  min-height: 112px !important;
  max-height: 126px !important;
  padding: 20px 120px 18px 28px !important;
  border-radius: 24px !important;
  border-color: rgba(148, 163, 184, 0.24) !important;
  transition: all 0.25s ease-in-out !important;
}

[data-wilsy-account-command-center="true"] [data-wilsy-role~="account-role-narrative"] strong::before {
  font-size: clamp(24px, 1.7vw, 34px) !important;
  font-weight: 900 !important;
  letter-spacing: -0.035em !important;
}

[data-wilsy-account-command-center="true"] [data-wilsy-role~="account-role-narrative"] p {
  font-size: clamp(13px, 0.86vw, 16px) !important;
  line-height: 1.48 !important;
  color: rgba(226, 232, 240, 0.90) !important;
}

[data-wilsy-account-command-center="true"] [data-wilsy-role~="account-role-narrative"]::after {
  margin-top: 4px !important;
  color: rgba(174, 188, 208, 0.86) !important;
}

/* Panel rail: Tier and Authority lead; Identity and Reach remain forensic support signals. */
[data-wilsy-account-command-center="true"] [data-wilsy-role~="account-story"] {
  grid-template-columns: minmax(260px, 1.18fr) minmax(250px, 1.12fr) minmax(230px, 1fr) minmax(220px, 0.94fr) !important;
  gap: 16px !important;
  align-items: stretch !important;
  overflow: visible !important;
}

[data-wilsy-account-command-center="true"] [data-wilsy-r7e-signal-tile="true"],
[data-wilsy-account-command-center="true"] [data-wilsy-role~="account-story-tile"] {
  min-height: 150px !important;
  max-height: none !important;
  overflow: visible !important;
  padding: 22px 18px 32px 78px !important;
  border-radius: 20px !important;
  text-align: left !important;
  transition: all 0.25s ease-in-out !important;
  transform: translate3d(0, 0, 0) !important;
}

[data-wilsy-account-command-center="true"] [data-wilsy-r7e-signal-tile="true"]:hover,
[data-wilsy-account-command-center="true"] [data-wilsy-role~="account-story-tile"]:hover {
  transform: translate3d(0, -2px, 0) !important;
  border-color: rgba(212, 175, 55, 0.42) !important;
  box-shadow:
    0 0 0 1px rgba(212, 175, 55, 0.10),
    0 0 18px rgba(212, 175, 55, 0.16),
    0 18px 44px rgba(0, 0, 0, 0.30) !important;
}

[data-wilsy-account-command-center="true"] [data-wilsy-role~="account-story-tile"]::after {
  left: 24px !important;
  width: 42px !important;
  height: 42px !important;
}

[data-wilsy-account-command-center="true"] [data-wilsy-role~="account-story-tile"] span {
  display: block !important;
  margin-bottom: 8px !important;
  color: rgba(248, 250, 252, 0.92) !important;
  font-size: 10px !important;
  line-height: 1 !important;
  font-weight: 900 !important;
  letter-spacing: 0.20em !important;
  text-transform: uppercase !important;
}

[data-wilsy-account-command-center="true"] [data-wilsy-role~="account-story-tile"] strong {
  display: block !important;
  max-width: 100% !important;
  color: #f8fafc !important;
  font-size: clamp(18px, 1.16vw, 24px) !important;
  line-height: 1.04 !important;
  font-weight: 900 !important;
  letter-spacing: -0.03em !important;
  margin: 0 0 9px !important;
  white-space: normal !important;
  overflow: visible !important;
  text-overflow: clip !important;
}

[data-wilsy-account-command-center="true"] [data-wilsy-role~="account-story-tile"] small {
  display: block !important;
  max-width: 100% !important;
  color: rgba(226, 232, 240, 0.86) !important;
  font-size: clamp(12px, 0.72vw, 14px) !important;
  line-height: 1.42 !important;
  font-weight: 560 !important;
  white-space: normal !important;
  overflow: visible !important;
  text-overflow: clip !important;
}

[data-wilsy-account-command-center="true"] [data-wilsy-r7e-evidence="true"] {
  left: 78px !important;
  right: 18px !important;
  bottom: 13px !important;
  overflow: hidden !important;
}

[data-wilsy-account-command-center="true"] .wilsy-r7e-evidence-anchor,
[data-wilsy-account-command-center="true"] .wilsy-r7e-evidence-seal {
  font-size: 9px !important;
  max-width: 50% !important;
}

/* Tier and Authority are command-leading cards. */
[data-wilsy-account-command-center="true"] [data-wilsy-role~="account-story-tile"]:nth-child(1),
[data-wilsy-account-command-center="true"] [data-wilsy-role~="account-story-tile"]:nth-child(2) {
  border-color: rgba(212, 175, 55, 0.28) !important;
}

[data-wilsy-account-command-center="true"] [data-wilsy-role~="account-story-tile"]:nth-child(1)::before,
[data-wilsy-account-command-center="true"] [data-wilsy-role~="account-story-tile"]:nth-child(2)::before {
  background: linear-gradient(180deg, #d4af37 0%, #38bdf8 100%) !important;
}

@media (max-width: 1440px) {
  [data-wilsy-account-command-center="true"] [data-wilsy-role~="account-story"] {
    grid-template-columns: repeat(2, minmax(0, 1fr)) !important;
  }
}

@media (max-width: 760px) {
  [data-wilsy-account-command-center="true"] [data-wilsy-role~="account-story"] {
    grid-template-columns: minmax(0, 1fr) !important;
  }
}


/* WILSY_R7J_A_FOUR_SIGNAL_RAIL_RESTORE */
/* Desktop/laptop mandate: Tier, Authority, Identity and Reach remain four visible command cards. */
[data-wilsy-account-command-center="true"] [data-wilsy-role~="account-story"] {
  display: grid !important;
  grid-template-columns: repeat(4, minmax(0, 1fr)) !important;
  gap: clamp(10px, 0.74vw, 16px) !important;
  align-items: stretch !important;
  width: 100% !important;
  max-width: 100% !important;
  overflow: visible !important;
}

/* R7J-A cancels the incorrect 1440px two-column collapse without touching mobile behavior. */
@media (min-width: 981px) {
  [data-wilsy-account-command-center="true"] [data-wilsy-role~="account-story"] {
    grid-template-columns: repeat(4, minmax(0, 1fr)) !important;
  }
}

/* Four-card density contract: no clipped titles, no hidden support cards. */
[data-wilsy-account-command-center="true"] [data-wilsy-r7e-signal-tile="true"],
[data-wilsy-account-command-center="true"] [data-wilsy-role~="account-story-tile"] {
  min-width: 0 !important;
  min-height: clamp(118px, 8.2vw, 146px) !important;
  max-height: none !important;
  padding: clamp(16px, 1vw, 22px) clamp(12px, 0.9vw, 18px) clamp(26px, 1.55vw, 34px) clamp(58px, 4.1vw, 74px) !important;
  border-radius: clamp(16px, 1.15vw, 20px) !important;
  overflow: visible !important;
  text-align: left !important;
  align-content: center !important;
}

[data-wilsy-account-command-center="true"] [data-wilsy-role~="account-story-tile"]::after {
  left: clamp(16px, 1.3vw, 24px) !important;
  width: clamp(34px, 2.4vw, 42px) !important;
  height: clamp(34px, 2.4vw, 42px) !important;
}

[data-wilsy-account-command-center="true"] [data-wilsy-role~="account-story-tile"] span {
  display: block !important;
  margin-bottom: 7px !important;
  font-size: clamp(8px, 0.58vw, 10px) !important;
  line-height: 1 !important;
  font-weight: 900 !important;
  letter-spacing: clamp(0.12em, 0.82vw, 0.20em) !important;
  text-transform: uppercase !important;
  white-space: nowrap !important;
  overflow: hidden !important;
  text-overflow: ellipsis !important;
}

[data-wilsy-account-command-center="true"] [data-wilsy-role~="account-story-tile"] strong {
  display: block !important;
  max-width: 100% !important;
  color: #f8fafc !important;
  font-size: clamp(15px, 1.05vw, 22px) !important;
  line-height: 1.08 !important;
  font-weight: 900 !important;
  letter-spacing: -0.03em !important;
  margin: 0 0 7px !important;
  white-space: normal !important;
  overflow: visible !important;
  text-overflow: clip !important;
}

[data-wilsy-account-command-center="true"] [data-wilsy-role~="account-story-tile"] small {
  display: block !important;
  max-width: 100% !important;
  color: rgba(226, 232, 240, 0.86) !important;
  font-size: clamp(10px, 0.66vw, 13px) !important;
  line-height: 1.32 !important;
  font-weight: 560 !important;
  white-space: normal !important;
  overflow: visible !important;
  text-overflow: clip !important;
}

/* Evidence stays present but compact so it does not eat the card. */
[data-wilsy-account-command-center="true"] [data-wilsy-r7e-evidence="true"] {
  left: clamp(58px, 4.1vw, 74px) !important;
  right: 12px !important;
  bottom: 11px !important;
  overflow: hidden !important;
}

[data-wilsy-account-command-center="true"] .wilsy-r7e-evidence-anchor,
[data-wilsy-account-command-center="true"] .wilsy-r7e-evidence-seal {
  font-size: clamp(7px, 0.48vw, 9px) !important;
  max-width: 50% !important;
}

/* Mobile/tablet may collapse. Desktop must not. */
@media (max-width: 980px) {
  [data-wilsy-account-command-center="true"] [data-wilsy-role~="account-story"] {
    grid-template-columns: repeat(2, minmax(0, 1fr)) !important;
  }
}

@media (max-width: 640px) {
  [data-wilsy-account-command-center="true"] [data-wilsy-role~="account-story"] {
    grid-template-columns: minmax(0, 1fr) !important;
  }
}




/* WILSY_R7K_THEME_SWITCHBOARD_ACTIVE_AUTHORITY */
[data-wilsy-account-command-center="true"] [data-wilsy-theme-switchboard] {
  position: relative !important;
  isolation: isolate !important;
}

[data-wilsy-account-command-center="true"] [data-wilsy-r7k-active-skin-status="true"] {
  display: inline-flex !important;
  align-items: center !important;
  gap: 8px !important;
  padding: 8px 12px !important;
  border-radius: 999px !important;
  border: 1px solid rgba(212, 175, 55, 0.30) !important;
  background: rgba(10, 18, 32, 0.72) !important;
  color: #f8fafc !important;
  box-shadow: inset 0 1px 0 rgba(255, 255, 255, 0.05) !important;
}

[data-wilsy-account-command-center="true"] [data-wilsy-r7k-active-skin-status="true"]::before {
  content: "\\u25cf" !important;
  color: #d4af37 !important;
  font-size: 10px !important;
  filter: drop-shadow(0 0 8px rgba(212, 175, 55, 0.65)) !important;
}

[data-wilsy-account-command-center="true"] [data-wilsy-r7k-skin-card="true"] {
  position: relative !important;
  isolation: isolate !important;
  display: grid !important;
  grid-template-rows: 34px auto auto auto 1fr !important;
  align-content: start !important;
  gap: 9px !important;
  min-width: clamp(220px, 13.4vw, 275px) !important;
  min-height: 196px !important;
  padding: 20px 20px 18px !important;
  border-radius: 22px !important;
  border: 1px solid rgba(148, 163, 184, 0.20) !important;
  background:
    radial-gradient(circle at 40% 0%, rgba(34, 197, 94, 0.08) 0%, transparent 50%),
    rgba(10, 18, 32, 0.78) !important;
  cursor: pointer !important;
  transition: all 0.25s ease-in-out !important;
  transform: translate3d(0, 0, 0) !important;
  overflow: hidden !important;
}

[data-wilsy-account-command-center="true"] [data-wilsy-r7k-skin-card="true"]:hover {
  transform: translate3d(0, -2px, 0) !important;
  border-color: rgba(212, 175, 55, 0.36) !important;
  box-shadow:
    0 0 0 1px rgba(212, 175, 55, 0.10),
    0 0 18px rgba(212, 175, 55, 0.14),
    0 20px 44px rgba(0, 0, 0, 0.24) !important;
}

[data-wilsy-account-command-center="true"] [data-wilsy-r7k-active-skin="true"] {
  border: 2px solid rgba(212, 175, 55, 0.78) !important;
  background:
    radial-gradient(circle at 30% 0%, rgba(212, 175, 55, 0.18) 0%, transparent 52%),
    linear-gradient(135deg, rgba(12, 20, 36, 0.96) 0%, rgba(5, 8, 20, 0.90) 100%) !important;
  box-shadow:
    0 0 0 1px rgba(212, 175, 55, 0.18),
    0 0 24px rgba(212, 175, 55, 0.28),
    inset 0 1px 0 rgba(255, 255, 255, 0.08) !important;
}

[data-wilsy-account-command-center="true"] [data-wilsy-r7k-active-chip="true"] {
  position: absolute !important;
  right: 16px !important;
  top: 14px !important;
  display: none !important;
  padding: 6px 8px !important;
  border-radius: 999px !important;
  background: rgba(212, 175, 55, 0.14) !important;
  color: #d4af37 !important;
  font-family: var(--wilsy-font-mono, ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace) !important;
  font-size: 8px !important;
  line-height: 1 !important;
  font-weight: 850 !important;
  letter-spacing: 0.12em !important;
  text-transform: uppercase !important;
  pointer-events: none !important;
}

[data-wilsy-account-command-center="true"] [data-wilsy-r7k-active-skin="true"] [data-wilsy-r7k-active-chip="true"] {
  display: inline-flex !important;
}

[data-wilsy-account-command-center="true"] [data-wilsy-r7k-skin-card="true"]::before {
  content: "" !important;
  display: block !important;
  height: 28px !important;
  border-radius: 999px !important;
  border: 1px solid rgba(34, 197, 94, 0.46) !important;
  background:
    linear-gradient(90deg, rgba(34, 197, 94, 0.12) 0%, rgba(56, 189, 248, 0.08) 55%, rgba(212, 175, 55, 0.10) 100%) !important;
}

[data-wilsy-account-command-center="true"] [data-wilsy-r7k-active-skin="true"]::before {
  border-color: rgba(212, 175, 55, 0.72) !important;
  box-shadow: 0 0 14px rgba(212, 175, 55, 0.26) !important;
}

[data-wilsy-account-command-center="true"] [data-wilsy-r7k-skin-card="true"] strong,
[data-wilsy-account-command-center="true"] [data-wilsy-r7k-skin-card="true"] h3,
[data-wilsy-account-command-center="true"] [data-wilsy-r7k-skin-card="true"] h4 {
  color: #f8fafc !important;
  font-size: clamp(18px, 1.05vw, 24px) !important;
  line-height: 1.12 !important;
  font-weight: 900 !important;
  letter-spacing: -0.03em !important;
}

[data-wilsy-account-command-center="true"] [data-wilsy-r7k-skin-anchor="true"] {
  display: inline-flex !important;
  width: fit-content !important;
  max-width: 100% !important;
  color: #d4af37 !important;
  font-family: var(--wilsy-font-mono, ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace) !important;
  font-size: 9px !important;
  line-height: 1 !important;
  font-weight: 850 !important;
  letter-spacing: 0.10em !important;
  text-transform: uppercase !important;
  white-space: nowrap !important;
  overflow: hidden !important;
  text-overflow: ellipsis !important;
}

[data-wilsy-account-command-center="true"] [data-wilsy-r7k-skin-rhythm="true"] {
  display: block !important;
  color: rgba(203, 213, 225, 0.76) !important;
  font-size: 11px !important;
  line-height: 1.35 !important;
  font-weight: 560 !important;
  letter-spacing: -0.01em !important;
  max-width: 100% !important;
}

[data-wilsy-account-command-center="true"] [data-wilsy-r7k-active-skin="false"] {
  opacity: 0.78 !important;
}

[data-wilsy-account-command-center="true"] [data-wilsy-r7k-active-skin="false"]:hover {
  opacity: 0.96 !important;
}


/* WILSY_R7L_THEME_PALETTE_PREVIEW_SWITCHBOARD */
[data-wilsy-account-command-center="true"] [data-wilsy-r7l-active-skin-status="true"],
[data-wilsy-account-command-center="true"] [data-wilsy-r7k-active-skin-status="true"] {
  display: inline-flex !important;
  align-items: center !important;
  gap: 8px !important;
  padding: 8px 12px !important;
  border-radius: 999px !important;
  border: 1px solid rgba(212, 175, 55, 0.35) !important;
  background: rgba(10, 18, 32, 0.76) !important;
  color: #f8fafc !important;
  box-shadow: inset 0 1px 0 rgba(255, 255, 255, 0.05), 0 0 16px rgba(212, 175, 55, 0.10) !important;
}

[data-wilsy-account-command-center="true"] [data-wilsy-r7l-active-skin-status="true"]::before,
[data-wilsy-account-command-center="true"] [data-wilsy-r7k-active-skin-status="true"]::before {
  content: "\\u25cf" !important;
  color: #d4af37 !important;
  font-size: 10px !important;
  filter: drop-shadow(0 0 8px rgba(212, 175, 55, 0.70)) !important;
}

/* Real preview cards: no guessing, the colour identity is visible before selection. */
[data-wilsy-account-command-center="true"] [data-wilsy-r7l-skin-card="true"] {
  position: relative !important;
  isolation: isolate !important;
  display: grid !important;
  grid-template-rows: auto auto auto auto 1fr !important;
  align-content: start !important;
  gap: 10px !important;
  min-width: clamp(230px, 13.6vw, 288px) !important;
  min-height: 230px !important;
  padding: 18px 20px 18px !important;
  border-radius: 22px !important;
  border: 1px solid rgba(148, 163, 184, 0.22) !important;
  background:
    radial-gradient(circle at 26% 0%, color-mix(in srgb, #38bdf8 12%, transparent) 0%, transparent 48%),
    rgba(10, 18, 32, 0.82) !important;
  cursor: pointer !important;
  transition: all 0.25s ease-in-out !important;
  transform: translate3d(0, 0, 0) !important;
  overflow: hidden !important;
}

[data-wilsy-account-command-center="true"] [data-wilsy-r7l-skin-card="true"]::before {
  content: none !important;
  display: none !important;
}

[data-wilsy-account-command-center="true"] [data-wilsy-r7l-palette-preview="true"] {
  display: block !important;
  width: 100% !important;
  height: 48px !important;
  border-radius: 16px !important;
  border: 1px solid rgba(248, 250, 252, 0.18) !important;
  background:
    var(--wilsy-r7l-skin-gradient),
    linear-gradient(90deg, #d4af37 0%, #38bdf8 50%, #020617 100%) !important;
  box-shadow:
    inset 0 1px 0 rgba(255, 255, 255, 0.22),
    0 14px 28px rgba(0, 0, 0, 0.24) !important;
  pointer-events: none !important;
}

[data-wilsy-account-command-center="true"] [data-wilsy-r7l-palette-preview="true"]::after {
  content: var(--wilsy-r7l-skin-tone, "Wilsy") !important;
  display: inline-flex !important;
  align-items: center !important;
  height: 100% !important;
  padding-left: 12px !important;
  color: rgba(255, 255, 255, 0.92) !important;
  font-family: var(--wilsy-font-mono, ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace) !important;
  font-size: 9px !important;
  font-weight: 900 !important;
  letter-spacing: 0.12em !important;
  text-transform: uppercase !important;
  text-shadow: 0 1px 8px rgba(0, 0, 0, 0.55) !important;
}

[data-wilsy-account-command-center="true"] [data-wilsy-r7l-skin-card="true"]:hover {
  transform: translate3d(0, -2px, 0) !important;
  border-color: rgba(212, 175, 55, 0.38) !important;
  box-shadow:
    0 0 0 1px rgba(212, 175, 55, 0.10),
    0 0 18px rgba(212, 175, 55, 0.14),
    0 20px 44px rgba(0, 0, 0, 0.26) !important;
}

[data-wilsy-account-command-center="true"] [data-wilsy-r7l-active-skin="true"] {
  border: 2px solid rgba(212, 175, 55, 0.82) !important;
  box-shadow:
    0 0 0 1px rgba(212, 175, 55, 0.18),
    0 0 26px rgba(212, 175, 55, 0.30),
    inset 0 1px 0 rgba(255, 255, 255, 0.08) !important;
}

[data-wilsy-account-command-center="true"] [data-wilsy-r7l-active-skin="true"] [data-wilsy-r7l-palette-preview="true"] {
  box-shadow:
    inset 0 1px 0 rgba(255, 255, 255, 0.28),
    0 0 18px rgba(212, 175, 55, 0.30),
    0 14px 30px rgba(0, 0, 0, 0.30) !important;
}

[data-wilsy-account-command-center="true"] [data-wilsy-r7l-active-chip="true"] {
  position: absolute !important;
  right: 16px !important;
  top: 14px !important;
  display: none !important;
  padding: 6px 8px !important;
  border-radius: 999px !important;
  background: rgba(212, 175, 55, 0.16) !important;
  color: #d4af37 !important;
  font-family: var(--wilsy-font-mono, ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace) !important;
  font-size: 8px !important;
  line-height: 1 !important;
  font-weight: 850 !important;
  letter-spacing: 0.12em !important;
  text-transform: uppercase !important;
  pointer-events: none !important;
}

[data-wilsy-account-command-center="true"] [data-wilsy-r7l-active-skin="true"] [data-wilsy-r7l-active-chip="true"] {
  display: inline-flex !important;
}

[data-wilsy-account-command-center="true"] [data-wilsy-r7l-skin-card="true"] strong,
[data-wilsy-account-command-center="true"] [data-wilsy-r7l-skin-card="true"] h3,
[data-wilsy-account-command-center="true"] [data-wilsy-r7l-skin-card="true"] h4 {
  color: #f8fafc !important;
  font-size: clamp(18px, 1.05vw, 24px) !important;
  line-height: 1.12 !important;
  font-weight: 900 !important;
  letter-spacing: -0.03em !important;
}

[data-wilsy-account-command-center="true"] [data-wilsy-r7l-skin-anchor="true"] {
  display: inline-flex !important;
  width: fit-content !important;
  max-width: 100% !important;
  color: #d4af37 !important;
  font-family: var(--wilsy-font-mono, ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace) !important;
  font-size: 9px !important;
  line-height: 1 !important;
  font-weight: 850 !important;
  letter-spacing: 0.10em !important;
  text-transform: uppercase !important;
  white-space: nowrap !important;
  overflow: hidden !important;
  text-overflow: ellipsis !important;
}

[data-wilsy-account-command-center="true"] [data-wilsy-r7l-skin-rhythm="true"] {
  display: block !important;
  color: rgba(203, 213, 225, 0.78) !important;
  font-size: 11px !important;
  line-height: 1.35 !important;
  font-weight: 560 !important;
  letter-spacing: -0.01em !important;
  max-width: 100% !important;
}

[data-wilsy-account-command-center="true"] [data-wilsy-r7l-active-skin="false"] {
  opacity: 0.84 !important;
}

[data-wilsy-account-command-center="true"] [data-wilsy-r7l-active-skin="false"]:hover {
  opacity: 0.98 !important;
}




/* WILSY_R7O_NO_HARDCODE_PROFILE_INTELLIGENCE */
[data-wilsy-account-command-center="true"] [data-wilsy-r7o-profile-hub="true"] {
  position: relative !important;
  isolation: isolate !important;
  overflow: hidden !important;
}

[data-wilsy-account-command-center="true"] [data-wilsy-r7o-profile-summary="true"] {
  display: block !important;
  max-width: 860px !important;
  margin: 8px 0 14px !important;
  color: rgba(226, 232, 240, 0.82) !important;
  font-size: clamp(13px, 0.82vw, 16px) !important;
  line-height: 1.5 !important;
  font-weight: 560 !important;
}

[data-wilsy-account-command-center="true"] [data-wilsy-r7o-profile-evidence-strip="true"] {
  display: inline-flex !important;
  width: fit-content !important;
  max-width: 100% !important;
  margin: 0 0 22px !important;
  padding: 8px 12px !important;
  border-radius: 999px !important;
  border: 1px solid rgba(34, 197, 94, 0.24) !important;
  background: rgba(10, 18, 32, 0.72) !important;
  color: rgba(74, 222, 128, 0.92) !important;
  font-family: var(--wilsy-font-mono, ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace) !important;
  font-size: 9px !important;
  line-height: 1 !important;
  font-weight: 850 !important;
  letter-spacing: 0.10em !important;
  text-transform: uppercase !important;
  white-space: nowrap !important;
  overflow: hidden !important;
  text-overflow: ellipsis !important;
}

[data-wilsy-account-command-center="true"] [data-wilsy-r7o-edit-profile-command="true"] {
  position: absolute !important;
  top: 30px !important;
  right: 32px !important;
  border-color: rgba(212, 175, 55, 0.38) !important;
  background: rgba(212, 175, 55, 0.08) !important;
  color: rgba(248, 250, 252, 0.92) !important;
  transition: all 0.25s ease-in-out !important;
  transform: translate3d(0, 0, 0) !important;
}

[data-wilsy-account-command-center="true"] [data-wilsy-r7o-edit-profile-command="true"]:hover {
  transform: translate3d(0, -2px, 0) !important;
  box-shadow:
    0 0 0 1px rgba(212, 175, 55, 0.14),
    0 0 18px rgba(212, 175, 55, 0.20) !important;
}

[data-wilsy-account-command-center="true"] [data-wilsy-r7o-profile-card="true"] {
  position: relative !important;
  isolation: isolate !important;
  min-height: 146px !important;
  padding: 24px 26px 22px !important;
  border-radius: 22px !important;
  border-color: rgba(148, 163, 184, 0.24) !important;
  background:
    radial-gradient(circle at 0% 0%, rgba(34, 197, 94, 0.07) 0%, transparent 42%),
    rgba(8, 13, 26, 0.66) !important;
  transition: all 0.25s ease-in-out !important;
  transform: translate3d(0, 0, 0) !important;
}

[data-wilsy-account-command-center="true"] [data-wilsy-r7o-profile-card="true"]::before {
  content: attr(data-wilsy-r7o-profile-source) !important;
  position: absolute !important;
  top: 18px !important;
  right: 18px !important;
  padding: 6px 8px !important;
  border-radius: 999px !important;
  background: rgba(34, 197, 94, 0.10) !important;
  color: rgba(74, 222, 128, 0.92) !important;
  font-family: var(--wilsy-font-mono, ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace) !important;
  font-size: 8px !important;
  font-weight: 850 !important;
  letter-spacing: 0.10em !important;
  text-transform: uppercase !important;
}

[data-wilsy-account-command-center="true"] [data-wilsy-r7o-profile-card="true"]:hover {
  transform: translate3d(0, -2px, 0) !important;
  border-color: rgba(212, 175, 55, 0.36) !important;
  box-shadow:
    0 0 0 1px rgba(212, 175, 55, 0.10),
    0 0 18px rgba(212, 175, 55, 0.14) !important;
}

[data-wilsy-account-command-center="true"] [data-wilsy-r7o-profile-role="true"] {
  display: inline-flex !important;
  width: fit-content !important;
  margin-top: 12px !important;
  padding: 6px 8px !important;
  border-radius: 999px !important;
  background: rgba(56, 189, 248, 0.10) !important;
  color: rgba(125, 211, 252, 0.95) !important;
  font-family: var(--wilsy-font-mono, ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace) !important;
  font-size: 9px !important;
  font-weight: 850 !important;
  letter-spacing: 0.10em !important;
  text-transform: uppercase !important;
}

[data-wilsy-account-command-center="true"] [data-wilsy-r7o-profile-proof="true"] {
  display: block !important;
  margin-top: 8px !important;
  max-width: 720px !important;
  color: rgba(203, 213, 225, 0.76) !important;
  font-size: 11px !important;
  line-height: 1.35 !important;
  font-weight: 560 !important;
}

[data-wilsy-account-command-center="true"] [data-wilsy-r7o-profile-source="true"] {
  display: none !important;
}

/* No fake account routes: icon-only command route shells are suppressed until a real route contract exists. */
[data-wilsy-account-command-center="true"] [data-wilsy-r7o-route-unbound="true"] {
  display: none !important;
  visibility: hidden !important;
  pointer-events: none !important;
}

[data-wilsy-account-command-center="true"] [data-wilsy-r7o-route-section="true"][data-wilsy-r7o-route-state="empty"] {
  display: none !important;
  visibility: hidden !important;
  pointer-events: none !important;
  height: 0 !important;
  min-height: 0 !important;
  margin: 0 !important;
  padding: 0 !important;
  overflow: hidden !important;
}

/* WILSY_R9N_R7C_COMMAND_IDENTITY_SOURCE_UNCLIP */
/* Production source override: keep the restored R7C shell, remove the clipping/compression. */
[data-wilsy-account-command-center="true"] [data-wilsy-identity-chrome][data-wilsy-r7c-identity-card="true"] {
  width: 100% !important;
  min-height: clamp(390px, 42vh, 540px) !important;
  max-height: none !important;
  overflow: visible !important;
  border-radius: clamp(28px, 2.2vw, 36px) !important;
  box-sizing: border-box !important;
}

[data-wilsy-account-command-center="true"] [data-wilsy-r7c-identity-ui="true"] {
  display: grid !important;
  grid-template-columns: clamp(104px, 8vw, 140px) minmax(0, 1fr) !important;
  gap: clamp(28px, 3.1vw, 48px) !important;
  align-items: start !important;
  width: 100% !important;
  max-width: 100% !important;
  min-height: clamp(350px, 39vh, 500px) !important;
  padding: clamp(32px, 3.2vw, 54px) clamp(38px, 4vw, 72px) !important;
  overflow: visible !important;
  box-sizing: border-box !important;
}

[data-wilsy-account-command-center="true"] .wilsy-r7c-identity-badge {
  width: clamp(104px, 8vw, 140px) !important;
  height: clamp(104px, 8vw, 140px) !important;
  min-width: clamp(104px, 8vw, 140px) !important;
  min-height: clamp(104px, 8vw, 140px) !important;
  max-width: clamp(104px, 8vw, 140px) !important;
  max-height: clamp(104px, 8vw, 140px) !important;
  align-self: start !important;
  overflow: visible !important;
}

[data-wilsy-account-command-center="true"] .wilsy-r7c-identity-content {
  min-width: 0 !important;
  width: 100% !important;
  max-width: 100% !important;
  overflow: visible !important;
  display: grid !important;
  grid-template-rows: auto auto auto auto auto !important;
  gap: clamp(10px, 1vw, 16px) !important;
  align-content: start !important;
  padding: 0 !important;
  box-sizing: border-box !important;
}

[data-wilsy-account-command-center="true"] .wilsy-r7c-identity-eyebrow {
  width: 100% !important;
  max-width: 100% !important;
  min-width: 0 !important;
  display: flex !important;
  flex-wrap: wrap !important;
  justify-content: flex-start !important;
  align-items: center !important;
  gap: 14px 22px !important;
  overflow: visible !important;
  white-space: normal !important;
  margin: 0 0 4px !important;
}

[data-wilsy-account-command-center="true"] .wilsy-r7c-command-label,
[data-wilsy-account-command-center="true"] .wilsy-r7c-verified-label {
  width: auto !important;
  max-width: none !important;
  min-width: 0 !important;
  overflow: visible !important;
  text-overflow: clip !important;
  white-space: nowrap !important;
  font-size: clamp(10px, 0.82vw, 14px) !important;
  line-height: 1.1 !important;
  font-weight: 900 !important;
  letter-spacing: 0.22em !important;
}

[data-wilsy-account-command-center="true"] .wilsy-r7c-identity-name {
  display: block !important;
  width: 100% !important;
  max-width: 100% !important;
  min-width: 0 !important;
  overflow: visible !important;
  text-overflow: clip !important;
  white-space: normal !important;
  overflow-wrap: anywhere !important;
  font-size: clamp(28px, 2.4vw, 44px) !important;
  line-height: 1.06 !important;
  letter-spacing: -0.04em !important;
  margin: 0 !important;
}

[data-wilsy-account-command-center="true"] .wilsy-r7c-identity-account {
  display: block !important;
  width: 100% !important;
  max-width: 100% !important;
  min-width: 0 !important;
  overflow: visible !important;
  text-overflow: clip !important;
  white-space: normal !important;
  overflow-wrap: anywhere !important;
  color: rgba(203, 213, 225, 0.92) !important;
  font-size: clamp(12px, 0.82vw, 16px) !important;
  line-height: 1.35 !important;
}

[data-wilsy-account-command-center="true"] .wilsy-r7f-identity-evidence {
  display: flex !important;
  flex-wrap: wrap !important;
  align-items: center !important;
  justify-content: flex-start !important;
  gap: 10px 18px !important;
  width: 100% !important;
  max-width: 100% !important;
  min-width: 0 !important;
  overflow: visible !important;
}

[data-wilsy-account-command-center="true"] .wilsy-r7f-clause-anchor,
[data-wilsy-account-command-center="true"] .wilsy-r7f-identity-seal {
  display: inline-flex !important;
  width: auto !important;
  max-width: none !important;
  min-width: 0 !important;
  overflow: visible !important;
  text-overflow: clip !important;
  white-space: nowrap !important;
  font-size: clamp(9px, 0.62vw, 12px) !important;
  line-height: 1.1 !important;
}

[data-wilsy-account-command-center="true"] .wilsy-r7c-tenant-pill {
  width: min(100%, 620px) !important;
  max-width: 100% !important;
  height: auto !important;
  min-height: 88px !important;
  max-height: none !important;
  margin-top: clamp(8px, 1vw, 16px) !important;
  padding: 24px 18px 14px !important;
  display: grid !important;
  grid-template-columns: 42px minmax(0, 1fr) 28px !important;
  align-items: center !important;
  gap: 14px !important;
  overflow: visible !important;
  box-sizing: border-box !important;
}

[data-wilsy-account-command-center="true"] .wilsy-r7c-tenant-pill::before {
  left: 74px !important;
  top: 12px !important;
  max-width: calc(100% - 100px) !important;
  overflow: visible !important;
  text-overflow: clip !important;
  white-space: nowrap !important;
}

[data-wilsy-account-command-center="true"] .wilsy-r7c-tenant-text {
  display: block !important;
  min-width: 0 !important;
  max-width: 100% !important;
  overflow: visible !important;
  text-overflow: clip !important;
  white-space: normal !important;
  line-height: 1.12 !important;
}


/* WILSY_R9O_COMMAND_IDENTITY_COPY_UNCLIP */
/* Production polish: remove copy clipping from restored R7C Command Identity shell. */
[data-wilsy-account-command-center="true"] [data-wilsy-r7c-identity-ui="true"] {
  grid-template-columns: clamp(104px, 7.6vw, 132px) minmax(0, 1fr) !important;
  gap: clamp(28px, 3vw, 44px) !important;
  overflow: visible !important;
}

[data-wilsy-account-command-center="true"] .wilsy-r7c-identity-content {
  width: 100% !important;
  max-width: 100% !important;
  min-width: 0 !important;
  overflow: visible !important;
}

[data-wilsy-account-command-center="true"] .wilsy-r7c-identity-eyebrow {
  display: grid !important;
  grid-template-columns: minmax(220px, max-content) minmax(220px, max-content) !important;
  justify-content: start !important;
  align-items: center !important;
  column-gap: clamp(18px, 2vw, 30px) !important;
  row-gap: 8px !important;
  width: 100% !important;
  max-width: 100% !important;
  min-width: 0 !important;
  overflow: visible !important;
  white-space: nowrap !important;
}

[data-wilsy-account-command-center="true"] .wilsy-r7c-command-label,
[data-wilsy-account-command-center="true"] .wilsy-r7c-verified-label {
  display: inline-flex !important;
  width: max-content !important;
  min-width: max-content !important;
  max-width: none !important;
  overflow: visible !important;
  text-overflow: clip !important;
  white-space: nowrap !important;
  letter-spacing: 0.20em !important;
  font-size: clamp(10px, 0.74vw, 13px) !important;
  line-height: 1.1 !important;
}

[data-wilsy-account-command-center="true"] .wilsy-r7c-identity-name {
  max-width: 100% !important;
  overflow: visible !important;
  text-overflow: clip !important;
  white-space: normal !important;
}

[data-wilsy-account-command-center="true"] .wilsy-r7f-identity-evidence {
  display: grid !important;
  grid-template-columns: max-content minmax(180px, max-content) max-content !important;
  justify-content: start !important;
  align-items: center !important;
  column-gap: clamp(12px, 1.4vw, 22px) !important;
  row-gap: 8px !important;
  width: 100% !important;
  max-width: 100% !important;
  min-width: 0 !important;
  overflow: visible !important;
}

[data-wilsy-account-command-center="true"] .wilsy-r7f-clause-anchor,
[data-wilsy-account-command-center="true"] .wilsy-r7f-identity-seal,
[data-wilsy-account-command-center="true"] .wilsy-r7f-identity-evidence span {
  display: inline-flex !important;
  width: max-content !important;
  min-width: 0 !important;
  max-width: none !important;
  overflow: visible !important;
  text-overflow: clip !important;
  white-space: nowrap !important;
  letter-spacing: 0.15em !important;
  font-size: clamp(9px, 0.58vw, 11px) !important;
  line-height: 1.1 !important;
}

[data-wilsy-account-command-center="true"] .wilsy-r7c-tenant-pill {
  width: min(100%, 620px) !important;
  max-width: 100% !important;
  overflow: visible !important;
}

[data-wilsy-account-command-center="true"] .wilsy-r7c-tenant-text {
  overflow: visible !important;
  text-overflow: clip !important;
  white-space: normal !important;
}

`;

export const WILSY_ACCOUNT_CHROME_RUNTIME_CSS_VERSION = 'R18AD1J-RAW-RUNTIME-CSS-STRING-REPAIR';

/* WILSY_R8A_ACCOUNT_CHROME_RUNTIME_CSS */


const WILSY_R8C_THEME_VIEWPORT_CSS = `
/* WILSY_R8C_THEME_VIEWPORT_SWITCHBOARD */
[data-wilsy-account-command-center="true"] [data-wilsy-r8c-mode-selector="true"] {
  max-height: clamp(128px, 16vh, 176px) !important;
  min-height: 0 !important;
  padding: clamp(14px, 1vw, 20px) !important;
  margin-bottom: clamp(14px, 1vw, 20px) !important;
  overflow: hidden !important;
}

[data-wilsy-account-command-center="true"] [data-wilsy-r8c-theme-viewport-switchboard="true"] {
  position: relative !important;
  display: grid !important;
  grid-template-rows: auto minmax(0, 1fr) !important;
  min-height: clamp(560px, 72vh, 880px) !important;
  max-height: 82vh !important;
  margin-top: clamp(14px, 1vw, 22px) !important;
  padding: 0 clamp(14px, 1vw, 20px) clamp(18px, 1.2vw, 28px) !important;
  border-radius: 28px !important;
  overflow: hidden !important;
  background: linear-gradient(180deg, rgba(2, 6, 23, 0.88) 0%, rgba(2, 6, 23, 0.72) 100%) !important;
  contain: layout paint style !important;
}

[data-wilsy-account-command-center="true"] [data-wilsy-r8c-theme-sticky-header="true"] {
  position: sticky !important;
  top: 0 !important;
  z-index: 20 !important;
  display: grid !important;
  grid-template-columns: minmax(0, 1fr) auto !important;
  gap: 12px !important;
  align-items: end !important;
  padding: clamp(18px, 1.2vw, 26px) 0 clamp(12px, 0.8vw, 18px) !important;
  margin: 0 !important;
  background: linear-gradient(180deg, rgba(2, 6, 23, 0.98) 0%, rgba(2, 6, 23, 0.90) 82%, rgba(2, 6, 23, 0) 100%) !important;
  backdrop-filter: blur(18px) saturate(1.18) !important;
  -webkit-backdrop-filter: blur(18px) saturate(1.18) !important;
  transform: translate3d(0, 0, 0) !important;
}

[data-wilsy-account-command-center="true"] [data-wilsy-r8c-theme-sticky-header="true"] h1,
[data-wilsy-account-command-center="true"] [data-wilsy-r8c-theme-sticky-header="true"] h2,
[data-wilsy-account-command-center="true"] [data-wilsy-r8c-theme-sticky-header="true"] h3 {
  margin: 0 !important;
  font-size: clamp(30px, 2.2vw, 52px) !important;
  line-height: 0.96 !important;
  letter-spacing: -0.055em !important;
}

[data-wilsy-account-command-center="true"] [data-wilsy-r8c-theme-sticky-header="true"] p {
  max-width: 860px !important;
  margin: 8px 0 0 !important;
  font-size: clamp(13px, 0.85vw, 16px) !important;
  line-height: 1.42 !important;
  color: rgba(226, 232, 240, 0.84) !important;
}

[data-wilsy-account-command-center="true"] [data-wilsy-r8c-theme-scroll-grid="true"] {
  display: grid !important;
  grid-template-columns: repeat(auto-fill, minmax(220px, 1fr)) !important;
  grid-auto-rows: minmax(188px, auto) !important;
  gap: clamp(12px, 0.95vw, 18px) !important;
  align-content: start !important;
  min-height: 0 !important;
  max-height: calc(82vh - 136px) !important;
  padding: 10px 10px 24px 0 !important;
  overflow-y: auto !important;
  overflow-x: hidden !important;
  overscroll-behavior: contain !important;
  scroll-behavior: smooth !important;
  scrollbar-gutter: stable both-edges !important;
  content-visibility: auto !important;
  contain-intrinsic-size: 760px !important;
}

[data-wilsy-account-command-center="true"] [data-wilsy-r8c-theme-scroll-grid="true"]::-webkit-scrollbar {
  width: 10px !important;
}

[data-wilsy-account-command-center="true"] [data-wilsy-r8c-theme-scroll-grid="true"]::-webkit-scrollbar-track {
  background: rgba(15, 23, 42, 0.58) !important;
  border-radius: 999px !important;
}

[data-wilsy-account-command-center="true"] [data-wilsy-r8c-theme-scroll-grid="true"]::-webkit-scrollbar-thumb {
  background: linear-gradient(180deg, rgba(212, 175, 55, 0.78), rgba(56, 189, 248, 0.64)) !important;
  border-radius: 999px !important;
}

[data-wilsy-account-command-center="true"] [data-wilsy-r8c-theme-card="true"] {
  min-height: 188px !important;
  height: auto !important;
  padding: clamp(18px, 1vw, 24px) !important;
  border-radius: 22px !important;
  content-visibility: auto !important;
  contain-intrinsic-size: 220px 188px !important;
  transition: transform 0.25s ease-in-out, border-color 0.25s ease-in-out, box-shadow 0.25s ease-in-out !important;
  transform: translate3d(0, 0, 0) !important;
}

[data-wilsy-account-command-center="true"] [data-wilsy-r8c-theme-card="true"]:hover {
  transform: translate3d(0, -2px, 0) !important;
}

[data-wilsy-account-command-center="true"] [data-wilsy-r8c-theme-card="true"][aria-pressed="true"],
[data-wilsy-account-command-center="true"] [data-wilsy-r8c-theme-card="true"][data-active="true"],
[data-wilsy-account-command-center="true"] [data-wilsy-r8c-theme-card="true"][data-selected="true"] {
  border-color: rgba(212, 175, 55, 0.78) !important;
  box-shadow: 0 0 0 1px rgba(212, 175, 55, 0.18), 0 0 22px rgba(212, 175, 55, 0.20) !important;
}

@media (max-height: 820px) {
  [data-wilsy-account-command-center="true"] [data-wilsy-r8c-mode-selector="true"] {
    max-height: 112px !important;
  }

  [data-wilsy-account-command-center="true"] [data-wilsy-r8c-theme-viewport-switchboard="true"] {
    max-height: 86vh !important;
  }

  [data-wilsy-account-command-center="true"] [data-wilsy-r8c-theme-scroll-grid="true"] {
    max-height: calc(86vh - 120px) !important;
    grid-auto-rows: minmax(168px, auto) !important;
  }

  [data-wilsy-account-command-center="true"] [data-wilsy-r8c-theme-card="true"] {
    min-height: 168px !important;
  }
}
`;


const WILSY_R8D_COMMAND_IDENTITY_LABEL_CSS = `
/* WILSY_R8D_COMMAND_IDENTITY_LABEL_AUTHORITY */
[data-wilsy-account-command-center="true"] [data-wilsy-r8d-command-identity-safe-zone="true"] {
  overflow: visible !important;
  text-overflow: clip !important;
}

[data-wilsy-account-command-center="true"] [data-wilsy-r8d-command-identity-header-row="true"] {
  display: flex !important;
  align-items: center !important;
  justify-content: space-between !important;
  flex-wrap: wrap !important;
  gap: 8px 16px !important;
  width: 100% !important;
  min-width: 0 !important;
  max-width: 100% !important;
  padding: 0 0 10px !important;
  margin: 0 0 12px !important;
  border-bottom: 1px solid rgba(148, 163, 184, 0.14) !important;
  overflow: visible !important;
}

[data-wilsy-account-command-center="true"] [data-wilsy-r8d-command-identity-label="true"] {
  display: inline-flex !important;
  align-items: center !important;
  width: auto !important;
  min-width: max-content !important;
  max-width: none !important;
  white-space: nowrap !important;
  overflow: visible !important;
  text-overflow: clip !important;
  color: rgba(226, 232, 240, 0.92) !important;
  font-family: var(--wilsy-font-mono, ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace) !important;
  font-size: clamp(10px, 0.66vw, 12px) !important;
  line-height: 1 !important;
  font-weight: 900 !important;
  letter-spacing: clamp(0.13em, 0.32vw, 0.20em) !important;
  text-transform: uppercase !important;
}

[data-wilsy-account-command-center="true"] [data-wilsy-r8d-command-identity-label="true"]::before {
  content: "" !important;
  width: 7px !important;
  height: 7px !important;
  margin-right: 10px !important;
  border-radius: 999px !important;
  background: linear-gradient(135deg, rgba(212, 175, 55, 0.95), rgba(56, 189, 248, 0.88)) !important;
  box-shadow: 0 0 14px rgba(56, 189, 248, 0.28) !important;
  flex: 0 0 auto !important;
}

[data-wilsy-account-command-center="true"] [data-wilsy-r8d-tenant-verified-label="true"] {
  display: inline-flex !important;
  align-items: center !important;
  flex: 0 0 auto !important;
  width: auto !important;
  min-width: max-content !important;
  max-width: none !important;
  white-space: nowrap !important;
  overflow: visible !important;
  text-overflow: clip !important;
  color: rgba(34, 197, 94, 0.96) !important;
  font-family: var(--wilsy-font-mono, ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace) !important;
  font-size: clamp(10px, 0.66vw, 12px) !important;
  line-height: 1 !important;
  font-weight: 900 !important;
  letter-spacing: clamp(0.12em, 0.30vw, 0.18em) !important;
  text-transform: uppercase !important;
  text-shadow: 0 0 14px rgba(34, 197, 94, 0.18) !important;
}

@media (max-width: 760px) {
  [data-wilsy-account-command-center="true"] [data-wilsy-r8d-command-identity-header-row="true"] {
    justify-content: flex-start !important;
  }

  [data-wilsy-account-command-center="true"] [data-wilsy-r8d-command-identity-label="true"],
  [data-wilsy-account-command-center="true"] [data-wilsy-r8d-tenant-verified-label="true"] {
    font-size: 10px !important;
    letter-spacing: 0.12em !important;
  }
}
`;


const WILSY_R8F_COMMAND_ROUTES_SOURCE_BOUND_CSS = `
/* WILSY_R8F_COMMAND_ROUTES_SOURCE_BOUND */
[data-wilsy-account-command-center="true"] [data-wilsy-r8f-command-routes-source-bound="true"] {
  display: grid !important;
  grid-template-columns: repeat(2, minmax(280px, 1fr)) !important;
  gap: clamp(14px, 1vw, 20px) !important;
  align-items: stretch !important;
}

[data-wilsy-account-command-center="true"] [data-wilsy-r8f-command-route-card="true"] {
  position: relative !important;
  min-height: 168px !important;
  padding: 22px 24px !important;
  overflow: hidden !important;
  cursor: pointer !important;
  isolation: isolate !important;
  transition: transform 0.25s ease-in-out, border-color 0.25s ease-in-out, box-shadow 0.25s ease-in-out !important;
}

[data-wilsy-account-command-center="true"] [data-wilsy-r8f-command-route-card="true"]:hover {
  transform: translate3d(0, -2px, 0) !important;
  border-color: rgba(212, 175, 55, 0.42) !important;
  box-shadow: 0 20px 52px rgba(0, 0, 0, 0.24), 0 0 18px rgba(56, 189, 248, 0.10) !important;
}

[data-wilsy-account-command-center="true"] [data-wilsy-r8f-command-route-card="true"][data-wilsy-r8f-route-active="true"] {
  border-color: rgba(212, 175, 55, 0.72) !important;
  box-shadow: 0 0 0 1px rgba(212, 175, 55, 0.20), 0 0 26px rgba(212, 175, 55, 0.18) !important;
}

[data-wilsy-account-command-center="true"] [data-wilsy-r8f-route-copy="true"] {
  position: relative !important;
  z-index: 3 !important;
  display: grid !important;
  gap: 8px !important;
  padding-left: clamp(48px, 3.2vw, 70px) !important;
  min-width: 0 !important;
}

[data-wilsy-account-command-center="true"] [data-wilsy-r8f-route-label="true"] {
  display: block !important;
  color: rgba(248, 250, 252, 0.98) !important;
  font-size: clamp(17px, 1.05vw, 22px) !important;
  line-height: 1.05 !important;
  font-weight: 900 !important;
  letter-spacing: -0.03em !important;
}

[data-wilsy-account-command-center="true"] [data-wilsy-r8f-route-purpose="true"] {
  margin: 0 !important;
  color: rgba(226, 232, 240, 0.78) !important;
  font-size: clamp(12px, 0.78vw, 14px) !important;
  line-height: 1.34 !important;
  max-width: 52ch !important;
}

[data-wilsy-account-command-center="true"] [data-wilsy-r8f-route-meta="true"],
[data-wilsy-account-command-center="true"] [data-wilsy-r8f-route-evidence="true"] {
  display: inline-flex !important;
  width: fit-content !important;
  max-width: 100% !important;
  color: rgba(125, 211, 252, 0.92) !important;
  font-family: var(--wilsy-font-mono, ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace) !important;
  font-size: 10px !important;
  line-height: 1.1 !important;
  font-weight: 800 !important;
  letter-spacing: 0.08em !important;
  text-transform: uppercase !important;
  white-space: normal !important;
}

[data-wilsy-account-command-center="true"] [data-wilsy-r8f-route-evidence="true"] {
  color: rgba(34, 197, 94, 0.86) !important;
}

[data-wilsy-account-command-center="true"] [data-wilsy-r8f-command-route-detail="true"] {
  grid-column: 1 / -1 !important;
  display: grid !important;
  gap: 14px !important;
  padding: clamp(22px, 1.4vw, 30px) !important;
  border: 1px solid rgba(56, 189, 248, 0.26) !important;
  border-radius: 24px !important;
  background: linear-gradient(135deg, rgba(8, 13, 28, 0.96), rgba(2, 6, 23, 0.90)) !important;
  box-shadow: 0 28px 80px rgba(0, 0, 0, 0.26), inset 0 1px 0 rgba(255, 255, 255, 0.05) !important;
}

[data-wilsy-account-command-center="true"] [data-wilsy-r8f-detail-eyebrow="true"] {
  color: rgba(212, 175, 55, 0.92) !important;
  font-family: var(--wilsy-font-mono, ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace) !important;
  font-size: 11px !important;
  font-weight: 900 !important;
  letter-spacing: 0.18em !important;
  text-transform: uppercase !important;
}

[data-wilsy-account-command-center="true"] [data-wilsy-r8f-command-route-detail="true"] h3 {
  margin: 0 !important;
  color: rgba(248, 250, 252, 0.98) !important;
  font-size: clamp(24px, 1.7vw, 36px) !important;
  line-height: 1 !important;
  letter-spacing: -0.05em !important;
}

[data-wilsy-account-command-center="true"] [data-wilsy-r8f-command-route-detail="true"] p {
  margin: 0 !important;
  color: rgba(226, 232, 240, 0.82) !important;
  max-width: 86ch !important;
  line-height: 1.5 !important;
}

[data-wilsy-account-command-center="true"] [data-wilsy-r8f-detail-evidence="true"] {
  display: grid !important;
  grid-template-columns: repeat(auto-fit, minmax(220px, 1fr)) !important;
  gap: 10px !important;
}

[data-wilsy-account-command-center="true"] [data-wilsy-r8f-detail-evidence="true"] > div {
  display: grid !important;
  gap: 4px !important;
  padding: 12px 14px !important;
  border: 1px solid rgba(148, 163, 184, 0.16) !important;
  border-radius: 16px !important;
  background: rgba(15, 23, 42, 0.54) !important;
}

[data-wilsy-account-command-center="true"] [data-wilsy-r8f-detail-evidence="true"] span {
  color: rgba(148, 163, 184, 0.88) !important;
  font-size: 10px !important;
  font-weight: 900 !important;
  letter-spacing: 0.14em !important;
  text-transform: uppercase !important;
}

[data-wilsy-account-command-center="true"] [data-wilsy-r8f-detail-evidence="true"] strong {
  color: rgba(248, 250, 252, 0.94) !important;
  font-size: 13px !important;
  line-height: 1.35 !important;
  word-break: break-word !important;
}

[data-wilsy-account-command-center="true"] [data-wilsy-r8f-detail-action="true"] {
  justify-self: start !important;
  min-height: 46px !important;
  padding: 0 18px !important;
  border: 1px solid rgba(212, 175, 55, 0.42) !important;
  border-radius: 999px !important;
  background: linear-gradient(135deg, rgba(212, 175, 55, 0.18), rgba(56, 189, 248, 0.12)) !important;
  color: rgba(248, 250, 252, 0.94) !important;
  font-weight: 900 !important;
  letter-spacing: 0.04em !important;
  cursor: pointer !important;
}

@media (max-width: 980px) {
  [data-wilsy-account-command-center="true"] [data-wilsy-r8f-command-routes-source-bound="true"] {
    grid-template-columns: 1fr !important;
  }
}
`;


const WILSY_R8G_COMMAND_ROUTES_DOM_PROOF_CSS = `
/* WILSY_R8G_COMMAND_ROUTES_DOM_PROOF */
[data-wilsy-account-command-center="true"] [data-wilsy-r8g-command-routes-dom-proof="true"] {
  overflow: visible !important;
}

[data-wilsy-account-command-center="true"] [data-wilsy-r8g-hidden-blank-route-card="true"] {
  display: none !important;
}

[data-wilsy-account-command-center="true"] [data-wilsy-r8g-command-route-deck="true"] {
  display: grid !important;
  grid-template-columns: repeat(2, minmax(280px, 1fr)) !important;
  gap: clamp(14px, 1vw, 20px) !important;
  width: 100% !important;
  margin-top: 18px !important;
}

[data-wilsy-account-command-center="true"] [data-wilsy-r8g-command-route-card="true"] {
  display: grid !important;
  gap: 10px !important;
  min-height: 176px !important;
  padding: clamp(20px, 1.3vw, 28px) !important;
  border: 1px solid rgba(212, 175, 55, 0.22) !important;
  border-radius: 24px !important;
  background:
    radial-gradient(circle at 12% 18%, rgba(56, 189, 248, 0.13), transparent 34%),
    linear-gradient(135deg, rgba(15, 23, 42, 0.82), rgba(2, 6, 23, 0.94)) !important;
  box-shadow: inset 0 1px 0 rgba(255, 255, 255, 0.05), 0 18px 54px rgba(0, 0, 0, 0.20) !important;
  text-align: left !important;
  cursor: pointer !important;
  color: rgba(248, 250, 252, 0.96) !important;
  transition: transform 0.22s ease, border-color 0.22s ease, box-shadow 0.22s ease !important;
}

[data-wilsy-account-command-center="true"] [data-wilsy-r8g-command-route-card="true"]:hover {
  transform: translate3d(0, -2px, 0) !important;
  border-color: rgba(212, 175, 55, 0.52) !important;
  box-shadow: 0 0 0 1px rgba(212, 175, 55, 0.16), 0 24px 70px rgba(0, 0, 0, 0.28) !important;
}

[data-wilsy-account-command-center="true"] [data-wilsy-r8g-command-route-card="true"][data-wilsy-r8g-route-active="true"] {
  border-color: rgba(212, 175, 55, 0.78) !important;
  box-shadow: 0 0 0 1px rgba(212, 175, 55, 0.24), 0 0 30px rgba(212, 175, 55, 0.18) !important;
}

[data-wilsy-account-command-center="true"] [data-wilsy-r8g-route-topline="true"] {
  display: flex !important;
  align-items: center !important;
  justify-content: space-between !important;
  gap: 14px !important;
}

[data-wilsy-account-command-center="true"] [data-wilsy-r8g-route-topline="true"] strong {
  color: rgba(248, 250, 252, 0.98) !important;
  font-size: clamp(18px, 1.14vw, 24px) !important;
  line-height: 1.05 !important;
  font-weight: 950 !important;
  letter-spacing: -0.04em !important;
}

[data-wilsy-account-command-center="true"] [data-wilsy-r8g-route-topline="true"] span {
  flex: 0 0 auto !important;
  padding: 7px 9px !important;
  border: 1px solid rgba(34, 197, 94, 0.32) !important;
  border-radius: 999px !important;
  color: rgba(34, 197, 94, 0.94) !important;
  font-family: var(--wilsy-font-mono, ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace) !important;
  font-size: 10px !important;
  font-weight: 900 !important;
}

[data-wilsy-account-command-center="true"] [data-wilsy-r8g-command-route-card="true"] p {
  margin: 0 !important;
  color: rgba(226, 232, 240, 0.78) !important;
  font-size: clamp(12px, 0.8vw, 14px) !important;
  line-height: 1.42 !important;
  max-width: 68ch !important;
}

[data-wilsy-account-command-center="true"] [data-wilsy-r8g-route-meta="true"],
[data-wilsy-account-command-center="true"] [data-wilsy-r8g-route-evidence="true"] {
  display: inline-flex !important;
  width: fit-content !important;
  max-width: 100% !important;
  color: rgba(125, 211, 252, 0.92) !important;
  font-family: var(--wilsy-font-mono, ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace) !important;
  font-size: 10px !important;
  line-height: 1.18 !important;
  font-weight: 850 !important;
  letter-spacing: 0.08em !important;
  text-transform: uppercase !important;
  white-space: normal !important;
}

[data-wilsy-account-command-center="true"] [data-wilsy-r8g-route-evidence="true"] {
  color: rgba(34, 197, 94, 0.88) !important;
}

[data-wilsy-account-command-center="true"] [data-wilsy-r8g-command-route-detail="true"] {
  grid-column: 1 / -1 !important;
  display: grid !important;
  gap: 14px !important;
  padding: clamp(22px, 1.4vw, 30px) !important;
  border: 1px solid rgba(56, 189, 248, 0.28) !important;
  border-radius: 24px !important;
  background: linear-gradient(135deg, rgba(8, 13, 28, 0.96), rgba(2, 6, 23, 0.90)) !important;
  box-shadow: 0 28px 80px rgba(0, 0, 0, 0.26), inset 0 1px 0 rgba(255, 255, 255, 0.05) !important;
}

[data-wilsy-account-command-center="true"] [data-wilsy-r8g-detail-eyebrow="true"] {
  color: rgba(212, 175, 55, 0.92) !important;
  font-family: var(--wilsy-font-mono, ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace) !important;
  font-size: 11px !important;
  font-weight: 900 !important;
  letter-spacing: 0.18em !important;
  text-transform: uppercase !important;
}

[data-wilsy-account-command-center="true"] [data-wilsy-r8g-command-route-detail="true"] h3 {
  margin: 0 !important;
  color: rgba(248, 250, 252, 0.98) !important;
  font-size: clamp(24px, 1.7vw, 36px) !important;
  line-height: 1 !important;
  letter-spacing: -0.05em !important;
}

[data-wilsy-account-command-center="true"] [data-wilsy-r8g-command-route-detail="true"] p {
  margin: 0 !important;
  color: rgba(226, 232, 240, 0.82) !important;
  max-width: 86ch !important;
  line-height: 1.5 !important;
}

[data-wilsy-account-command-center="true"] [data-wilsy-r8g-detail-matrix="true"] {
  display: grid !important;
  grid-template-columns: repeat(auto-fit, minmax(220px, 1fr)) !important;
  gap: 10px !important;
}

[data-wilsy-account-command-center="true"] [data-wilsy-r8g-detail-matrix="true"] > div {
  display: grid !important;
  gap: 4px !important;
  padding: 12px 14px !important;
  border: 1px solid rgba(148, 163, 184, 0.16) !important;
  border-radius: 16px !important;
  background: rgba(15, 23, 42, 0.54) !important;
}

[data-wilsy-account-command-center="true"] [data-wilsy-r8g-detail-matrix="true"] span {
  color: rgba(148, 163, 184, 0.88) !important;
  font-size: 10px !important;
  font-weight: 900 !important;
  letter-spacing: 0.14em !important;
  text-transform: uppercase !important;
}

[data-wilsy-account-command-center="true"] [data-wilsy-r8g-detail-matrix="true"] strong {
  color: rgba(248, 250, 252, 0.94) !important;
  font-size: 13px !important;
  line-height: 1.35 !important;
  word-break: break-word !important;
}

[data-wilsy-account-command-center="true"] [data-wilsy-r8g-route-action="true"] {
  justify-self: start !important;
  min-height: 46px !important;
  padding: 0 18px !important;
  border: 1px solid rgba(212, 175, 55, 0.42) !important;
  border-radius: 999px !important;
  background: linear-gradient(135deg, rgba(212, 175, 55, 0.18), rgba(56, 189, 248, 0.12)) !important;
  color: rgba(248, 250, 252, 0.94) !important;
  font-weight: 900 !important;
  letter-spacing: 0.04em !important;
  cursor: pointer !important;
}

@media (max-width: 980px) {
  [data-wilsy-account-command-center="true"] [data-wilsy-r8g-command-route-deck="true"] {
    grid-template-columns: 1fr !important;
  }
}
`;


const WILSY_R9P_COMMAND_IDENTITY_FINAL_ORDER_FIX_CSS = `
  /* WILSY_R9P_COMMAND_IDENTITY_FINAL_ORDER_FIX */
  [data-wilsy-account-command-center="true"] [data-wilsy-identity-chrome][data-wilsy-r7c-identity-card="true"] {
    width: 100% !important;
    max-width: 100% !important;
    min-height: clamp(390px, 42vh, 540px) !important;
    max-height: none !important;
    overflow: visible !important;
    box-sizing: border-box !important;
  }

  [data-wilsy-account-command-center="true"] [data-wilsy-r7c-identity-ui="true"] {
    width: 100% !important;
    max-width: 100% !important;
    display: grid !important;
    grid-template-columns: clamp(104px, 7.4vw, 132px) minmax(0, 1fr) !important;
    gap: clamp(28px, 3vw, 44px) !important;
    align-items: start !important;
    overflow: visible !important;
    box-sizing: border-box !important;
  }

  [data-wilsy-account-command-center="true"] .wilsy-r7c-identity-content {
    min-width: 0 !important;
    width: 100% !important;
    max-width: 100% !important;
    overflow: visible !important;
    display: grid !important;
    align-content: start !important;
    gap: 14px !important;
  }

  [data-wilsy-account-command-center="true"] .wilsy-r7c-identity-eyebrow {
    display: flex !important;
    flex-wrap: nowrap !important;
    align-items: center !important;
    justify-content: flex-start !important;
    gap: clamp(18px, 2vw, 30px) !important;
    width: 100% !important;
    max-width: 100% !important;
    overflow: visible !important;
    white-space: nowrap !important;
  }

  [data-wilsy-account-command-center="true"] .wilsy-r7c-command-label,
  [data-wilsy-account-command-center="true"] .wilsy-r7c-verified-label {
    display: inline-flex !important;
    flex: 0 0 auto !important;
    width: auto !important;
    min-width: max-content !important;
    max-width: none !important;
    overflow: visible !important;
    text-overflow: clip !important;
    white-space: nowrap !important;
    font-size: clamp(9px, 0.68vw, 12px) !important;
    line-height: 1.1 !important;
    letter-spacing: 0.15em !important;
  }

  [data-wilsy-account-command-center="true"] .wilsy-r7c-identity-name {
    width: 100% !important;
    max-width: 100% !important;
    min-width: 0 !important;
    overflow: visible !important;
    text-overflow: clip !important;
    white-space: normal !important;
    overflow-wrap: anywhere !important;
    font-size: clamp(28px, 2.35vw, 42px) !important;
    line-height: 1.06 !important;
    letter-spacing: -0.04em !important;
  }

  [data-wilsy-account-command-center="true"] .wilsy-r7c-identity-account {
    width: 100% !important;
    max-width: 100% !important;
    overflow: visible !important;
    text-overflow: clip !important;
    white-space: normal !important;
    overflow-wrap: anywhere !important;
  }

  [data-wilsy-account-command-center="true"] .wilsy-r7f-identity-evidence {
    display: flex !important;
    flex-wrap: nowrap !important;
    justify-content: flex-start !important;
    align-items: center !important;
    gap: clamp(12px, 1.3vw, 20px) !important;
    width: 100% !important;
    max-width: 100% !important;
    overflow: visible !important;
    white-space: nowrap !important;
  }

  [data-wilsy-account-command-center="true"] .wilsy-r7f-clause-anchor,
  [data-wilsy-account-command-center="true"] .wilsy-r7f-identity-seal,
  [data-wilsy-account-command-center="true"] .wilsy-r7f-identity-evidence span {
    display: inline-flex !important;
    flex: 0 0 auto !important;
    width: auto !important;
    min-width: max-content !important;
    max-width: none !important;
    overflow: visible !important;
    text-overflow: clip !important;
    white-space: nowrap !important;
    font-size: clamp(8px, 0.54vw, 10px) !important;
    line-height: 1.1 !important;
    letter-spacing: 0.12em !important;
  }

  [data-wilsy-account-command-center="true"] .wilsy-r7c-tenant-pill {
    width: min(100%, 620px) !important;
    max-width: 100% !important;
    overflow: visible !important;
  }

  [data-wilsy-account-command-center="true"] .wilsy-r7c-tenant-text {
    overflow: visible !important;
    text-overflow: clip !important;
    white-space: normal !important;
  }
`;

/**
 * @function buildWilsyAccountExtractedChromeCss
 * @description Returns the complete extracted Wilsy Account chrome CSS bundle.
 * @returns {string} Extracted runtime CSS.
 * @collaboration Keeps WilsyAccountCommandCenter lean while preserving theme, identity, route, and command chrome styling.
 */
export function buildWilsyAccountExtractedChromeCss() {
  const cssSegments = [
    typeof WILSY_ACCOUNT_EXTRACTED_CHROME_CSS !== 'undefined' ? WILSY_ACCOUNT_EXTRACTED_CHROME_CSS : '',
    typeof WILSY_R8C_THEME_VIEWPORT_CSS !== 'undefined' ? WILSY_R8C_THEME_VIEWPORT_CSS : '',
    typeof WILSY_R8D_COMMAND_IDENTITY_LABEL_CSS !== 'undefined' ? WILSY_R8D_COMMAND_IDENTITY_LABEL_CSS : '',
    typeof WILSY_R8F_COMMAND_ROUTES_SOURCE_BOUND_CSS !== 'undefined' ? WILSY_R8F_COMMAND_ROUTES_SOURCE_BOUND_CSS : '',
    typeof WILSY_R8G_COMMAND_ROUTES_DOM_PROOF_CSS !== 'undefined' ? WILSY_R8G_COMMAND_ROUTES_DOM_PROOF_CSS : '',
    typeof WILSY_R9P_COMMAND_IDENTITY_FINAL_ORDER_FIX_CSS !== 'undefined' ? WILSY_R9P_COMMAND_IDENTITY_FINAL_ORDER_FIX_CSS : ''
  ];

  return cssSegments.filter(Boolean).join('\n');
}

