/* eslint-disable */
/**
 * ╔════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╗
 * ║ WILSY OS - VITE CLIENT CONFIGURATION RUNTIME [V2.5.0-PYTHON-EOS-ROUTE-CONSOLIDATION]                                                            ║
 * ║ AUTHORITY: WILSY OS CORE INFRASTRUCTURE | TERMINAL WORKFLOW COMPLIANT                                                                ║
 * ╠════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╣
 * ║ VERSION: 2.5.0-PYTHON-EOS-ROUTE-CONSOLIDATION | MIGRATION IN PROGRESS                                                                               ║
 * ║ ABSOLUTE PATH: /Users/wilsonkhanyezi/legal-doc-system/client/vite.config.js                                                          ║
 * ╠════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╣
 * ║ EPITOME:                                                                                                                             ║
 * ║ Routes the legacy /auth alias and established Python-EOS surfaces to port 9095 while preserving the catch-all for not-yet-migrated ║
 * ║ API contracts. The Node BFF remains required until parity certification is complete.                                                 ║
 * ╠════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╣
 * ║ 🔧 CHANGE LOG (v2.5.0):
 * ║   1. Routes the general /api fallback to Python EOS; only /api/generate/pdf remains on Node pending certified PDF parity.               ║
 * ║   2. Routes BFF-forwarded plans, subscriptions, billing, tenant alias, and C1C/C1E advisory endpoints directly to Python EOS.            ║
 * ║ 🔧 PRIOR CHANGE LOG (v2.4.2):
 * ║   1. Routes the legacy /auth alias to canonical Python EOS /api/auth without relying on the Node BFF.                                  ║
 * ║   2. Keeps the general /api catch-all unchanged until every remaining Node-owned contract has a tested Python equivalent.             ║
 * ║ 🔧 PRIOR CHANGE LOG (v2.4.1):
 * ║   1. Routes Python-EOS-owned /api/legal-operations directly to port 9095 so L8-6A sheriff queue reads cannot fall through Node.      ║
 * ║   2. Preserves the /api prefix because the Legal Operations router is mounted under /api.                                             ║
 * ║   3. Routes Python-EOS-owned /api/tenant-branding directly to port 9095 so governed branding activation cannot fall through Node.     ║
 * ║ 🔧 PRIOR CHANGE LOG (v2.3.9):
 * ║   1. Routes Python-EOS-owned /api/legal-acceptance directly to port 9095 so authenticated legal gating cannot fall through Node.
 * ║ 🔧 PRIOR CHANGE LOG (v2.3.8):                                                                                                               ║
 * ║   1. Routed /api/auth directly to the verified Kennel auth router; the live Node bootstrap was proxying it as /auth/login.         ║
 * ║ 🔧 PRIOR CHANGE LOG (v2.3.7):                                                                                                        ║
 * ║   1. Routed Kennel billing read models through /api/billing/* with the required /api removal only at the EOS boundary.             ║
 * ║   2. Preserved the /api catch-all for Node-owned auth, business, telemetry, v1, treasury, subscriptions and partial payments.     ║
 * ║ 🔧 PRIOR CHANGE LOG (v2.3.6):                                                                                                        ║
 * ║   1. Preserved /api/auth → Node without rewriting.                                                                                  ║
 * ║   2. Routed /api/billing/platform|client/invoices → Kennel /billing/* (Kennel has no /api prefix).                                 ║
 * ║   3. Routed all remaining /api calls → Node, including /api/billing/invoices/:id/partial-payment.                                  ║
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
      // Legacy /auth callers are normalized to the canonical Python EOS auth router.
      // The explicit /api/auth rule remains unchanged for canonical callers.
      '/auth': {
        target: 'http://localhost:9095',
        changeOrigin: true,
        secure: false,
        rewrite: (path) => path.replace(/^\/auth(?=\/|$)/, '/api/auth'),
        configure: (proxy, options) => {
          proxy.on('proxyReq', (proxyReq, req, res) => {
            console.info(`[WILSY-PROXY-DISPATCH-AUTH] ${req.method} ${req.url} -> ${proxyReq.path}`);
          });
          proxy.on('proxyRes', (proxyRes, req, res) => {
            console.info(`[WILSY-PROXY-RETURN-AUTH] ${proxyRes.statusCode} ${req.url}`);
          });
          proxy.on('error', (err, req, res) => {
            console.error('[WILSY-PROXY-FATAL-AUTH]', err.message);
            if (!res.headersSent) {
              res.writeHead(502, { 'Content-Type': 'application/json' });
              res.end(JSON.stringify({
                success: false,
                message: 'Auth backend unreachable – verify Python EOS on port 9095 is active.',
                error: err.message
              }));
            }
          });
        }
      },
      // Kennel invoice lifecycle endpoints are mounted at /billing/*, not /api/billing/*.
      // Keep these rules before the general /api BFF rule so compose/list reach EOS,
      // while Node-owned actions (partial pay, PDF, audit) retain their correct owner.
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
      // Kennel billing read models are mounted at /billing/*, not /api/billing/*.
      // This explicit rule must remain ahead of /api so Node-only routes retain Node ownership.
      '^/api/billing/(plans|summary|analytics|credit-scores|forensic-status)(?:/|$)': {
        target: 'http://localhost:9095',
        changeOrigin: true,
        secure: false,
        rewrite: (path) => path.replace(/^\/api/, ''),
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
      // Node-owned binary PDF generation remains explicit until its Python
      // EOS equivalent passes the artifact identity, tenant, seal, and renderer certificates.
      '/api/generate/pdf': {
        target: 'http://localhost:4000',
        changeOrigin: true,
        secure: false,
        configure: (proxy, options) => {
          proxy.on('proxyReq', (proxyReq, req, res) => {
            console.info(`[WILSY-PROXY-DISPATCH-PDF-LEGACY] ${req.method} ${req.url} -> ${proxyReq.path}`);
          });
          proxy.on('proxyRes', (proxyRes, req, res) => {
            console.info(`[WILSY-PROXY-RETURN-PDF-LEGACY] ${proxyRes.statusCode} ${req.url}`);
          });
          proxy.on('error', (err, req, res) => {
            console.error('[WILSY-PROXY-FATAL-PDF-LEGACY]', err.message);
            if (!res.headersSent) {
              res.writeHead(502, { 'Content-Type': 'application/json' });
              res.end(JSON.stringify({
                success: false,
                error: 'LEGACY_PDF_RENDERER_UNAVAILABLE',
                message: 'The legacy PDF renderer is temporarily unavailable.',
              }));
            }
          });
        }
      },
      // These paths were previously forwarded by the BFF to the same canonical
      // Python EOS routes. Keep the original path contract, including explicit rewrites.
      '/api/business/tenants': {
        target: 'http://localhost:9095',
        changeOrigin: true,
        secure: false,
        rewrite: (path) => path.replace(/^\/api\/business\/tenants(?=\/|$)/, '/api/tenants'),
      },
      '/api/plans': {
        target: 'http://localhost:9095',
        changeOrigin: true,
        secure: false,
      },
      '/api/subscriptions': {
        target: 'http://localhost:9095',
        changeOrigin: true,
        secure: false,
      },
      '/api/wilsy-ai/legal-services': {
        target: 'http://localhost:9095',
        changeOrigin: true,
        secure: false,
      },
      '/api/wilsy-ai/legal-next-actions': {
        target: 'http://localhost:9095',
        changeOrigin: true,
        secure: false,
      },
      '/billing': {
        target: 'http://localhost:9095',
        changeOrigin: true,
        secure: false,
      },
      // Node's BFF previously stripped /api from all remaining billing calls.
      // Forward those contracts directly to the canonical EOS /billing router.
      '/api/billing': {
        target: 'http://localhost:9095',
        changeOrigin: true,
        secure: false,
        rewrite: (path) => path.replace(/^\/api(?=\/|$)/, ''),
      },
      // Only explicitly unmigrated routes should remain on the Node BFF.
      // The default API path now terminates at Python EOS; unknown paths fail there.
      '/api': {
        target: 'http://localhost:9095',
        changeOrigin: true,
        secure: false,
        configure: (proxy, options) => {
          proxy.on('proxyReq', (proxyReq, req, res) => {
            console.info(`[WILSY-PROXY-DISPATCH-EOS] ${req.method} ${req.url} -> ${proxyReq.path}`);
          });
          proxy.on('proxyRes', (proxyRes, req, res) => {
            console.info(`[WILSY-PROXY-RETURN-EOS] ${proxyRes.statusCode} ${req.url}`);
          });
          proxy.on('error', (err, req, res) => {
            console.error('[WILSY-PROXY-FATAL-EOS]', err.message);
            if (!res.headersSent) {
              res.writeHead(502, { 'Content-Type': 'application/json' });
              res.end(JSON.stringify({
                success: false,
                error: 'PYTHON_EOS_UNAVAILABLE',
                message: 'Python EOS is temporarily unavailable on port 9095.',
              }));
            }
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
 * ═══════════════════════════════════════════════════════════════════════════════════
 * INSTITUTIONAL MIGRATION SEAL — WILSY OS VITE CONFIGURATION V2.5.0-PYTHON-EOS-ROUTE-CONSOLIDATION
 * ═══════════════════════════════════════════════════════════════════════════════════
 * Status: PYTHON EOS MIGRATION IN PROGRESS — ONLY THE EXPLICIT PDF ROUTE REMAINS ON NODE
 * Compliance: POPIA §19, GDPR §32, SOC2 §CC7.2
 * Proxy Rules:
 *   /api/auth → http://localhost:9095 (Kennel auth router) – no rewrite
 *   /auth      → http://localhost:9095/api/auth (Python EOS, path rewrite)
 *   /api/billing/platform|client → http://localhost:9095/billing/platform|client
 *   /api/billing/plans|summary|analytics|credit-scores|forensic-status → http://localhost:9095/billing/*
 *   /api/kernel → http://localhost:9095/api/kernel
 *   /api/tenant-branding → http://localhost:9095/api/tenant-branding
 *   /api/legal-operations → http://localhost:9095/api/legal-operations
 *   /api/legal-acceptance → http://localhost:9095/api/legal-acceptance
 *   /api/tenants, /api/employees → http://localhost:9095
 *   /api/generate/pdf → http://localhost:4000 (legacy PDF renderer; temporary)
 *   /api       → http://localhost:9095 (Python EOS catch-all)
 * ═══════════════════════════════════════════════════════════════════════════════════
 */
