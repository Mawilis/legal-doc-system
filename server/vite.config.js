/* eslint-disable */
/**
 * ╔════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╗
 * ║ WILSY OS - VITE CLIENT CONFIGURATION RUNTIME [V2.1.4-PRODUCTION-GRADE]                                                                 ║
 * ║ [VITE DEV SERVER | DIRECT API PROXY ROUTING | EXPLICIT MACOS BROWSER SPAWN | EOS KENNEL ALIGNED]                                       ║
 * ╠════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╣
 * ║ VERSION: 2.1.4-PRODUCTION-GRADE | BILLION-DOLLAR ENTERPRISE SOFTWARE | BIBLICAL WORTH COMPLIANT                                       ║
 * ║ ABSOLUTE PATH: /Users/wilsonkhanyezi/legal-doc-system/client/vite.config.js                                                           ║
 * ╠════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╣
 * ║ EPITOME:                                                                                                                               ║
 * ║ Production-grade Vite configuration maintaining pristine /api path preservation from the frontend client (port 5173) to the Express    ║
 * ║ backend kernel (port 5050), ensuring exact route matching for authentication and telemetry endpoints without prefix stripping.          ║
 * ╠════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╣
 * ║ BIBLICAL WORTH BILLIONS:                                                                                                               ║
 * ║ "Wisdom is the principal thing; therefore get wisdom: and with all thy getting get understanding." — Proverbs 4:7                      ║
 * ╠════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╣
 * ║ COLLABORATION & SOVEREIGN SIGN-OFF:                                                                                                    ║
 * ║ • Wilson Khanyezi (Founder/CEO) - Mandated exact /api route preservation and verified backend kernel synchronization.                    ║
 * ║ • AI Engineering (Gemini) - RECTIFIED: Removed rewrite prefix stripping to ensure backend Express routers receive full /api/* paths.     ║
 * ╚════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╝
 */

import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';
import path from 'path';

/**
 * @function defineConfig
 * @description Configures the Vite development server and bundling environment for Wilsy OS.
 *              Ensures deterministic path resolution, zero-latency backend API proxy routing preserving the /api namespace, and explicit browser opening.
 * @returns {import('vite').UserConfig} The Vite configuration object.
 */
export default defineConfig({
  plugins: [react()],
  server: {
    port: 5173,
    host: true,
    strictPort: true,
    open: 'http://localhost:5173',
    proxy: {
      '/api': {
        target: 'http://localhost:5050',
        changeOrigin: true,
        secure: false,
        configure: (proxy, options) => {
          proxy.on('error', (err, req, res) => {
            console.error('[WILSY-CLIENT-PROXY-ERROR] Failed to communicate with Express backend kernel:', err.message);
          });
        }
      }
    }
  },
  resolve: {
    alias: {
      '@': path.resolve(__dirname, './src')
    }
  }
});

/**
 * @seal Wilsy OS Institutional Seal - Verified Production Ready
 */
