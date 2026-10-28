/* eslint-disable */
/**
 * ╔════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╗
 * ║ WILSY OS - VITE CLIENT CONFIGURATION RUNTIME [V2.4.1-L10-P2C7B-TENANT-BRANDING-ROUTER]                                                            ║
 * ║ AUTHORITY: WILSY OS CORE INFRASTRUCTURE | TERMINAL WORKFLOW COMPLIANT                                                                ║
 * ╠════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╣
 * ║ VERSION: 2.4.1-L10-P2C7B-TENANT-BRANDING-ROUTER | PRODUCTION READY                                                                               ║
 * ║ ABSOLUTE PATH: /Users/wilsonkhanyezi/legal-doc-system/client/vite.config.js                                                          ║
 * ╠════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╣
 * ║ EPITOME:                                                                                                                             ║
 * ║ Routes all API traffic to Python EOS on port 9095; no Node API runtime fallback remains.                                             ║
 * ╠════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╣
 * ║ 🔧 CHANGE LOG (v2.4.1):
 * ║   1. Routes Python-EOS-owned /api/legal-operations directly to port 9095 so L8-6A sheriff queue reads cannot fall through Node.      ║
 * ║   2. Preserves the /api prefix because the Legal Operations router is mounted under /api.                                             ║
 * ║   3. Routes Python-EOS-owned /api/tenant-branding directly to port 9095 so governed branding activation cannot fall through Node.     ║
 * ║ 🔧 PRIOR CHANGE LOG (v2.3.9):
 * ║   1. Routes Python-EOS-owned /api/legal-acceptance directly to port 9095 so authenticated legal gating cannot fall through Node.
 * ║ 🔧 PRIOR CHANGE LOG (v2.3.8):                                                                                                               ║
 * ║   1. Routed /api/auth directly to the verified Kennel auth router; the live Node bootstrap was proxying it as /auth/login.         ║
 * ║ 🔧 PRIOR CHANGE LOG (v2.3.7):                                                                                                        ║
 * ║   1. Routed Kennel billing read models through /api/billing/* with the required /api removal only at the EOS boundary.             ║
 * ║   2. Routes the remaining API catch-all to Python EOS; unknown paths receive EOS 404 rather than falling through to Node.            ║
 * ║ 🔧 PRIOR CHANGE LOG (v2.3.6):                                                                                                        ║
 * ║   1. Routes /api/auth, billing, plans, subscriptions, tenants, employees and PDF export directly to Python EOS.                       ║
 * ║   2. Preserves only the /api/business/tenants compatibility rewrite and /auth alias.                                                   ║
 * ╚════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╝
 */

import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';
import path from 'path';

export default defineConfig({
  plugins: [react()],
  optimizeDeps: {
    include: ['js-sha3', 'axios', 'react', 'react-dom', 'react-router-dom']
  },
  server: {
    port: 5173,
    host: true,
    strictPort: true,
    open: true,
    proxy: {
      // Kennel owns the live /api/auth router. Preserve its /api prefix.
      '/api/auth': {
        target: 'http://localhost:9095',
        changeOrigin: true,
        secure: false,
        configure: (proxy, options) => {
          proxy.on('proxyReq', (proxyReq, req, res) => {
            console.info(`[WILSY-PROXY-DISPATCH-AUTH-API] ${req.method} ${req.url} -> ${proxyReq.path}`);
          });
          proxy.on('proxyRes', (proxyRes, req, res) => {
            console.info(`[WILSY-PROXY-RETURN-AUTH-API] ${proxyRes.statusCode} ${req.url}`);
          });
          proxy.on('error', (err, req, res) => {
            console.error('[WILSY-PROXY-FATAL-AUTH-API]', err.message);
            if (!res.headersSent) {
              res.writeHead(502, { 'Content-Type': 'application/json' });
              res.end(JSON.stringify({
                success: false,
                message: 'Auth backend unreachable – verify Kennel server on port 9095 is active.',
                error: err.message
              }));
            }
          });
        }
      },
      // Legacy auth alias rewrites to canonical Python EOS auth.
      '/auth': {
        target: 'http://localhost:9095',
        changeOrigin: true,
        secure: false,
        rewrite: (path) => path.replace(/^\/auth/, '/api/auth'),
      },
      // Billing operations are owned by Python EOS; mutations retain domain authorization and Kennel EOS financial boundaries.
      '/api/billing/platform': {
        target: 'http://localhost:9095',
        changeOrigin: true,
        secure: false,
        rewrite: (path) => path.replace(/^\/api/, ''),
      },
      '/api/billing/client': {
        target: 'http://localhost:9095',
        changeOrigin: true,
        secure: false,
        rewrite: (path) => path.replace(/^\/api/, ''),
      },
      // Python EOS exposes the canonical billing router under /api/billing.
      '/api/billing': {
        target: 'http://localhost:9095',
        changeOrigin: true,
        secure: false,
      },
      // Kernel is an EOS service and is explicitly mounted at /api/kernel.
      '/api/kernel': {
        target: 'http://localhost:9095',
        changeOrigin: true,
        secure: false,
      },
      // Python EOS owns governed tenant-branding activation and workspace projection.
      // Preserve /api because the branding router is mounted under /api.
      '/api/tenant-branding': {
        target: 'http://localhost:9095',
        changeOrigin: true,
        secure: false,
      },
      // Python EOS owns authenticated Legal Operations read/command authority.
      // Preserve /api because the EOS router is mounted under /api.
      '/api/legal-operations': {
        target: 'http://localhost:9095',
        changeOrigin: true,
        secure: false,
        configure: (proxy, options) => {
          proxy.on('proxyReq', (proxyReq, req, res) => {
            console.info(`[WILSY-PROXY-DISPATCH-LEGAL-OPERATIONS] ${req.method} ${req.url} -> ${proxyReq.path}`);
          });
          proxy.on('proxyRes', (proxyRes, req, res) => {
            console.info(`[WILSY-PROXY-RETURN-LEGAL-OPERATIONS] ${proxyRes.statusCode} ${req.url}`);
          });
          proxy.on('error', (err, req, res) => {
            console.error(
              '[WILSY-PROXY-FATAL-LEGAL-OPERATIONS]',
              err.message,
            );
            if (!res.headersSent) {
              res.writeHead(
                502,
                { 'Content-Type': 'application/json' },
              );
              res.end(JSON.stringify({
                success: false,
                message: 'Legal Operations EOS backend unreachable on port 9095.',
                error: err.message,
              }));
            }
          });
        },
      },

      // Python EOS owns authenticated legal-acceptance authority.
      // Preserve /api because the EOS router is mounted under /api.
      '/api/legal-acceptance': {
        target: 'http://localhost:9095',
        changeOrigin: true,
        secure: false,
        configure: (proxy, options) => {
          proxy.on('proxyReq', (proxyReq, req, res) => {
            console.info(`[WILSY-PROXY-DISPATCH-LEGAL-ACCEPTANCE] ${req.method} ${req.url} -> ${proxyReq.path}`);
          });
          proxy.on('proxyRes', (proxyRes, req, res) => {
            console.info(`[WILSY-PROXY-RETURN-LEGAL-ACCEPTANCE] ${proxyRes.statusCode} ${req.url}`);
          });
          proxy.on('error', (err, req, res) => {
            console.error(
              '[WILSY-PROXY-FATAL-LEGAL-ACCEPTANCE]',
              err.message,
            );
            if (!res.headersSent) {
              res.writeHead(
                502,
                { 'Content-Type': 'application/json' },
              );
              res.end(JSON.stringify({
                success: false,
                message: 'Legal acceptance EOS backend unreachable on port 9095.',
                error: err.message,
              }));
            }
          });
        },
      },

      // Kennel owns the tenant and employee directories used by BillingHUD typeaheads.
      '/api/tenants': {
        target: 'http://localhost:9095',
        changeOrigin: true,
        secure: false,
      },
      '/api/employees': {
        target: 'http://localhost:9095',
        changeOrigin: true,
        secure: false,
      },
      // Historical business tenant URL is a compatibility alias only.
      '/api/business/tenants': {
        target: 'http://localhost:9095',
        changeOrigin: true,
        secure: false,
        rewrite: (path) => path.replace(/^\/api\/business\/tenants/, '/api/tenants'),
      },
      '/api/plans': { target: 'http://localhost:9095', changeOrigin: true, secure: false },
      '/api/subscriptions': { target: 'http://localhost:9095', changeOrigin: true, secure: false },
      '/api/wilsy-ai/legal-services': { target: 'http://localhost:9095', changeOrigin: true, secure: false },
      '/api/wilsy-ai/legal-next-actions': { target: 'http://localhost:9095', changeOrigin: true, secure: false },
      '/api/generate/pdf': { target: 'http://localhost:9095', changeOrigin: true, secure: false },
      // All remaining API traffic terminates at Python EOS. Unknown paths return
      // an EOS 404; no Node runtime fallback or authority downgrade exists.
      '/api': {
        target: 'http://localhost:9095',
        changeOrigin: true,
        secure: false,
        ws: true,
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
 * ═══════════════════════════════════════════════════════════════════════════════════
 * INSTITUTIONAL CERTIFICATION SEAL — WILSY OS VITE CONFIGURATION V2.4.1-L10-P2C7B-TENANT-BRANDING-ROUTER
 * ═══════════════════════════════════════════════════════════════════════════════════
 * Status: CERTIFIED PRODUCTION ARTIFACT
 * Compliance: POPIA §19, GDPR §32, SOC2 §CC7.2
 * Proxy Rules:
 *   /api/auth → http://localhost:9095/api/auth (Python EOS; no rewrite)
 *   /auth      → http://localhost:9095/api/auth (Python EOS compatibility rewrite)
 *   /api/billing/platform|client → http://localhost:9095/billing/platform|client
 *   /api/billing/** → Python EOS; platform/client legacy prefixes rewrite to /billing/**
 *   /api/kernel → http://localhost:9095/api/kernel
 *   /api/tenant-branding → http://localhost:9095/api/tenant-branding
 *   /api/legal-operations → http://localhost:9095/api/legal-operations
 *   /api/legal-acceptance → http://localhost:9095/api/legal-acceptance
 *   /api/tenants, /api/employees → http://localhost:9095
 *   /api       → http://localhost:9095 (Python EOS; no Node runtime fallback)
 * ═══════════════════════════════════════════════════════════════════════════════════
 */
