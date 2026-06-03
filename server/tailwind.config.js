/* eslint-disable */
/**
 * @file tailwind.config.js
 * @version 1.0.0
 * @epitome Sovereign Visual Identity - Wilsy OS
 * @description Calibrated theme tokens for Gold and Stone architecture.
 * * BIBLICAL STANDARDS:
 * - Majesty: Metallic gold accents.
 * - Stability: Deep stone foundations.
 * - Clarity: High-contrast forensic readability.
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
        // Calibrated Sovereign Gold
        gold: {
          DEFAULT: '#d4af37',
          light: '#f1d592',
          dark: '#9a7b1a',
          shimmer: '#ffdf00',
        },
        // Deep Architectural Stone
        stone: {
          950: '#0c0a09',
          900: '#1c1917',
          850: '#211f1d',
          800: '#292524',
          700: '#44403c',
        },
      },
      fontFamily: {
        // Forensic font for mathematical and transaction data
        mono: ['JetBrains Mono', 'Fira Code', 'monospace'],
        // Elegant, stable sans for high-level legal text
        sans: ['Inter', 'system-ui', 'sans-serif'],
      },
      boxShadow: {
        // Subtle gold glow for active Sovereign elements
        'gold-glow': '0 0 15px -3px rgba(212, 175, 55, 0.4)',
      },
      borderColor: {
        gold: '#d4af37',
      }
    },
  },
  plugins: [],
}
