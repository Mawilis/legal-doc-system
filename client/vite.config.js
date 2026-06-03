/* eslint-disable */
/**
 * ╔════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╗
 * ║ WILSY OS - SOVEREIGN HANDSHAKE ENGINE [V25.2.0-MARS]                                                                                   ║
 * ║ [VITE_PROXY_BRIDGE | AUTO-LAUNCH | OMEGA-LEVEL SYNC | DIAGNOSTIC LOGGING]                                                              ║
 * ╠════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╣
 * ║ VERSION: 25.2.0-MARS | BIBLICAL WORTH BILLIONS | PRODUCTION READY                                                                      ║
 * ║ EPITOME: NO CHILD'S PLACE | INSTITUTIONAL AUTHORITY | MARS-SPEC ENGINEERING                                                            ║
 * ║ ABSOLUTE PATH: /Users/wilsonkhanyezi/legal-doc-system/client/vite.config.js                                                             ║
 * ╠════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╣
 * ║ 👥 COLLABORATION & SOVEREIGN SIGN-OFF:                                                                                                 ║
 * ║ • Wilson Khanyezi (CEO/Lead Architect) - Mandated auto-browser launch for boardroom workflow efficiency. [2026-05-15]                  ║
 * ║ • AI Engineering (DeepSeek) - RECTIFIED: Enabled 'open' server flag and preserved IPv4 127.0.0.1 anchoring. [2026-05-15]               ║
 * ║ • AI Engineering (DeepSeek) - FORTIFIED: Transparent proxy rewrite for seamless API handshake. [2026-05-15]                            ║
 * ║ • AI Engineering (DeepSeek) - EPITOMISED: Full JSDoc, added proxy diagnostic logging, version bump. [2026-05-16]                       ║
 * ╚════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╝
 */

import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

/**
 * Vite configuration for WILSY OS frontend.
 *
 * **Features**:
 * - React plugin for JSX/TSX support.
 * - PostCSS configuration for Tailwind/CSS processing.
 * - Development server on port 3000 with auto‑launch.
 * - Proxy bridge: `/api` requests forwarded to backend on port 5050.
 * - Diagnostic logging for proxy events (error, proxyReq, proxyRes).
 *
 * @type {import('vite').UserConfig}
 */
export default defineConfig({
  // ============================================================================
  // 🧩 PLUGINS
  // ============================================================================
  /**
   * Vite plugins – React support.
   * @type {Array}
   */
  plugins: [react()],

  // ============================================================================
  // 🎨 CSS CONFIGURATION
  // ============================================================================
  /**
   * CSS processing options – points to PostCSS config file.
   * @type {Object}
   */
  css: {
    postcss: './postcss.config.js'
  },

  // ============================================================================
  // 🖥️ DEVELOPMENT SERVER - MARS Protocol Bridge
  // ============================================================================
  /**
   * Development server configuration.
   * @type {Object}
   */
  server: {
    /**
     * Frontend port – fixed to 3000.
     * @type {number}
     */
    port: 3000,
    /**
     * Automatically open browser on start.
     * @type {boolean}
     */
    open: true,
    /**
     * Proxy configuration for API requests.
     * @type {Object}
     */
    proxy: {
      '/api': {
        /**
         * Backend target URL.
         * @type {string}
         */
        target: 'http://127.0.0.1:5050',
        /**
         * Preserve the original host header.
         * @type {boolean}
         */
        changeOrigin: true,
        /**
         * Allow self‑signed certificates in development.
         * @type {boolean}
         */
        secure: false,
        /**
         * Enable WebSocket proxying.
         * @type {boolean}
         */
        ws: true,
        /**
         * No rewrite – keep `/api` prefix.
         * @param {string} path - Original request path
         * @returns {string} Unmodified path
         */
        rewrite: (path) => path,
        /**
         * Configure proxy event handlers for diagnostics.
         * @param {import('vite').ProxyOptions} proxy - The proxy instance
         */
        configure: (proxy) => {
          // Log proxy errors
          proxy.on('error', (err, req, res) => {
            console.error('[VITE-PROXY] ❌ Proxy error:', err.message);
            console.error('[VITE-PROXY] Request:', req.method, req.url);
          });
          // Log outgoing proxy requests
          proxy.on('proxyReq', (proxyReq, req, res) => {
            console.log('[VITE-PROXY] 🚀', req.method, req.url, '→', proxyReq.path);
          });
          // Log proxy responses
          proxy.on('proxyRes', (proxyRes, req, res) => {
            console.log('[VITE-PROXY] ✅', req.method, req.url, '→', proxyRes.statusCode);
          });
        }
      }
    }
  }
});

// Display configuration summary on startup
console.log(`
╔══════════════════════════════════════════════════════════════════════════╗
║           🔌 SOVEREIGN HANDSHAKE ENGINE ACTIVE - MARS PROTOCOL         ║
║   Frontend: http://localhost:3000 | Backend: http://127.0.0.1:5050      ║
║   Proxy: /api → /api | Auto-Launch: ENABLED | Status: BOARDROOM READY   ║
║   Diagnostic Logging: ACTIVE                                            ║
╚══════════════════════════════════════════════════════════════════════════╝
`);
