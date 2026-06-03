/* eslint-disable */
/**
 * ╔════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╗
 * ║ WILSY OS - OMEGA DESIGN MATRIX [V50.3.0-MARS-PROTOCOL]                                                                                 ║
 * ║ [UNIFIED SOVEREIGN PALETTE | CEREMONIAL ANIMATIONS | FORENSIC TYPOGRAPHY | ZERO-GRAVITY SHADOWS]                                       ║
 * ╠════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╣
 * ║ VERSION: 50.3.0-OMEGA | PRODUCTION HARDENED | BILLION-DOLLAR SPEC                                                                      ║
 * ║ EPITOME: BIBLICAL WORTH BILLIONS | NO CHILD'S PLACE | INSTITUTIONAL DOMINANCE | IDENTITY: WILSON KHANYEZI                                ║
 * ║ ABSOLUTE PATH: /Users/wilsonkhanyezi/legal-doc-system/client/tailwind.config.js                                                        ║
 * ╠════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╣
 * ║ 👥 COLLABORATION & SOVEREIGN SIGN-OFF:                                                                                                 ║
 * ║ • Wilson Khanyezi (CEO/Lead Architect) - Mandated the Mars Protocol: maximum creativity, unified tokens, and total visual authority.   ║
 * ║ • AI Engineering (Gemini) - FUSED: Merged client shadows and server typography into a single master protocol.                          ║
 * ║ • AI Engineering (Gemini) - INJECTED: Ceremonial keyframes (fadeIn, slideUp, shimmer, pulse) for the Boardroom HUD entrance.           ║
 * ╚════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╝
 *
 * @fileoverview Tailwind CSS Master Configuration for Wilsy OS Client.
 * Drives the Fortune-500 visual identity. All HUDs, Matrix overlays, and
 * Sovereign modules pull from this centralized reality engine.
 */

/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        // 👑 Calibrated Sovereign Gold Palette
        gold: {
          DEFAULT: '#D4AF37',
          light: '#F1C40F',
          dark: '#996515',
          shimmer: '#FFDF00',
        },
        // 🏛️ Deep Architectural Stone Foundations
        stone: {
          950: '#050505',
          900: '#111111',
          850: '#211F1D',
          800: '#1A1A1A',
          700: '#44403C',
        }
      },
      fontFamily: {
        // Forensic font for mathematical, telemetry, and transaction data
        mono: ['JetBrains Mono', 'Fira Code', 'monospace'],
        // Elegant, stable sans for high-level legal text and C-Suite reading
        sans: ['Inter', 'system-ui', 'sans-serif'],
      },
      boxShadow: {
        'gold-glow': '0 0 25px rgba(212, 175, 55, 0.3)',
        'gold-glow-intense': '0 0 50px rgba(212, 175, 55, 0.5)',
        'citadel': '0 0 100px rgba(0, 0, 0, 1)',
        'forensic-inset': 'inset 0 0 20px rgba(0, 0, 0, 1)',
      },
      animation: {
        // Legacy OS Animations
        'pulse-slow': 'pulse 4s cubic-bezier(0.4, 0, 0.6, 1) infinite',
        'ping-slow': 'ping 3s cubic-bezier(0, 0, 0.2, 1) infinite',
        'scan': 'scanline 6s linear infinite',
        'covenant-in': 'covenantIn 0.8s cubic-bezier(0.16, 1, 0.3, 1)',

        // Ceremonial HUD Animations (Mars Protocol)
        'fadeIn': 'fadeIn 1.5s ease forwards',
        'slideUp': 'slideUp 1.2s ease forwards',
        'shimmer': 'shimmer 3s ease-in-out infinite',
        // Overriding default tailwind pulse to be more authoritative for the Crest
        'pulse': 'wilsyPulse 2s cubic-bezier(0.4, 0, 0.6, 1) infinite',
      },
      keyframes: {
        scanline: {
          '0%': { transform: 'translateY(-100%)' },
          '100%': { transform: 'translateY(100%)' },
        },
        covenantIn: {
          '0%': { opacity: '0', transform: 'scale(0.98) translateY(20px)' },
          '100%': { opacity: '1', transform: 'scale(1) translateY(0)' },
        },
        // Ceremonial HUD Keyframes
        fadeIn: {
          '0%': { opacity: '0' },
          '100%': { opacity: '1' }
        },
        slideUp: {
          '0%': { transform: 'translateY(20px)', opacity: '0' },
          '100%': { transform: 'translateY(0)', opacity: '1' }
        },
        shimmer: {
          '0%': { borderColor: 'rgba(212, 175, 55, 0.2)' },
          '50%': { borderColor: 'rgba(212, 175, 55, 1)' },
          '100%': { borderColor: 'rgba(212, 175, 55, 0.2)' }
        },
        wilsyPulse: {
          '0%, 100%': { opacity: '1' },
          '50%': { opacity: '0.7' },
        }
      },
      letterSpacing: {
        'forensic': '0.5em',
        'sovereign': '0.8em',
      },
      borderColor: {
        gold: '#D4AF37',
      }
    },
  },
  plugins: [],
}
