/* eslint-disable */
/**
 * ╔════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╗
 * ║ WILSY OS - VITE CLIENT CONFIGURATION RUNTIME [V2.5.0-PYTHON-EOS-API-ROUTING-BFF-ISOLATION]                                                            ║
 * ║ AUTHORITY: WILSY OS CORE INFRASTRUCTURE | TERMINAL WORKFLOW COMPLIANT                                                                ║
 * ╠════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╣
 * ║ VERSION: 2.5.0-PYTHON-EOS-API-ROUTING-BFF-ISOLATION | MIGRATION STAGE 1                                                                               ║
 * ║ ABSOLUTE PATH: /Users/wilsonkhanyezi/legal-doc-system/client/vite.config.js                                                          ║
 * ║ COLLABORATION / OWNERSHIP: WILSY Core Engineering; routing migration maintains Python EOS as canonical authority.                    ║
 * ║ CERTIFICATION / UPDATE DATE: 2026-10-27.                                                                                            ║
 * ║ COMPLIANCE: POPIA §19; GDPR Article 32; SOC 2 CC7.2; ISO 27001.                                                                    ║
 * ║ SECURITY / PRIVACY: Proxy failures fail closed; no bearer values or payloads are logged or synthesized.                           ║
 * ║ TENANT BOUNDARY: Routing only; downstream EOS services retain tenant admission and isolation.                                       ║
 * ║ AUTHORITY BOUNDARY: Transport dispatch only; no identity, authorization, document, or business truth is created.                    ║
 * ║ FINANCIAL AUTHORITY: Kennel EOS exclusively owns financial execution and settlement truth.                                          ║
 * ╠════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╣
 * ║ EPITOME:                                                                                                                             ║
 * ║ Routes Python-EOS-owned auth, legal-acceptance, Legal Operations, kernel, and governed billing paths to port 9095.                 ║
 * ║ General /api and legacy /auth traffic route directly to Python EOS. Node remains only for /api/generate/pdf until its              ║
 * ║ authenticated identity, tenant-bound proof, signed QR, and enterprise PDF behavior are ported and certified in Python.             ║
 * ╠════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╣
 * ║ CHANGE LOG (v2.5.0-PYTHON-EOS-API-ROUTING-BFF-ISOLATION):
 * ║   1. Sends the general /api fallback to Python EOS, not the Node BFF.
 * ║   2. Sends the legacy /auth alias to Python EOS /api/auth with an explicit prefix rewrite.
 * ║   3. Keeps /api/generate/pdf explicitly on Node as the sole verified application endpoint not yet ported.
 * ║   4. Leaves the BFF process running only until PDF parity is implemented and certified.
 * ║ 🔧 PRIOR CHANGE LOG (v2.4.1-L10-P2C7B-TENANT-BRANDING-ROUTER):
 * ║   1. Routes Python-EOS-owned /api/legal-operations and /api/tenant-branding directly to port 9095.
 * ║ 🔧 PRIOR CHANGE LOG (v2.3.9):
 * ║   1. Routes Python-EOS-owned /api/legal-acceptance directly to port 9095 so authenticated legal gating cannot fall through Node.
 * ║ 🔧 PRIOR CHANGE LOG (v2.3.8):                                                                                                               ║
 * ║   1. Routed /api/auth directly to the verified Kennel auth router; the live Node bootstrap was proxying it as /auth/login.         ║
 * ║ 🔧 PRIOR CHANGE LOG (v2.3.7):                                                                                                        ║
 * ║   1. Routed Kennel billing read models through /api/billing/* with the required /api removal only at the EOS boundary.             ║
 * ║   2. Previously preserved the general /api catch-all for Node; v2.5.0 retires that general fallback.
 * ║ 🔧 PRIOR CHANGE LOG (v2.3.6):                                                                                                        ║
 * ║   1. Previously preserved /api/auth → Node without rewriting; canonical auth now routes to Python EOS.
 * ║   2. Routed /api/billing/platform|client/invoices → Kennel /billing/* (Kennel has no /api prefix).                                 ║
 * ║   3. Previously routed remaining /api calls → Node; v2.5.0 isolates only the PDF endpoint.
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
      // Legacy /auth aliases are routed to canonical Python EOS auth.
      // Rewrite only this alias to the canonical /api/auth prefix.
      '/auth': {
        target: 'http://localhost:9095',
        rewrite: (path) => path.replace(/^\/auth/, '/api/auth'),
        changeOrigin: true,
        secure: false,
        configure: (proxy, options) => {
          proxy.on('proxyReq', (proxyReq, req, res) => {
            console.info(`[WILSY-PROXY-DISPATCH-AUTH] ${req.method} ${req.url}`);
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
      // Keep these rules before the general /api rule so invoice compose/list paths
      // retain the required /billing prefix rewrite; all other API traffic goes to EOS.
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

      // Preserve the Node BFF's legacy business-tenant alias rewrite in direct Python routing.
      '/api/business/tenants': {
        target: 'http://localhost:9095',
        changeOrigin: true,
        secure: false,
        rewrite: (path) => path.replace(/^\/api\/business\/tenants/, '/api/tenants'),
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
      // The sole remaining Node-owned HTTP application endpoint is PDF generation.
      // Keep this explicit route before the general /api rule until its Python
      // replacement passes identity, tenant, proof, QR and renderer parity tests.
      '/api/generate/pdf': {
        target: 'http://localhost:4000',
        changeOrigin: true,
        secure: false,
        configure: (proxy, options) => {
          proxy.on('proxyReq', (proxyReq, req, res) => {
            console.info(`[WILSY-PROXY-DISPATCH-LEGACY-PDF] ${req.method} ${req.url}`);
          });
          proxy.on('proxyRes', (proxyRes, req, res) => {
            console.info(`[WILSY-PROXY-RETURN-LEGACY-PDF] ${proxyRes.statusCode} ${req.url}`);
          });
          proxy.on('error', (err, req, res) => {
            console.error('[WILSY-PROXY-FATAL-LEGACY-PDF]', err.message);
            if (!res.headersSent) {
              res.writeHead(502, { 'Content-Type': 'application/json' });
              res.end(JSON.stringify({
                success: false,
                error: 'LEGACY_PDF_BACKEND_UNAVAILABLE',
                message: 'The legacy PDF endpoint is unavailable while Python EOS parity remains pending.'
              }));
            }
          });
        }
      },
      // All general API traffic is routed to Python EOS. The BFF is not a general fallback.
      '/api': {
        target: 'http://localhost:9095',
        changeOrigin: true,
        secure: false,
        ws: true,
        configure: (proxy, options) => {
          proxy.on('proxyReq', (proxyReq, req, res) => {
            console.info(`[WILSY-PROXY-DISPATCH] ${req.method} ${req.url} -> ${proxyReq.path}`);
          });
          proxy.on('proxyRes', (proxyRes, req, res) => {
            console.info(`[WILSY-PROXY-RETURN] ${proxyRes.statusCode} ${req.url}`);
          });
          proxy.on('error', (err, req, res) => {
            console.error('[WILSY-PROXY-FATAL]', err.message);
            if (!res.headersSent) {
              res.writeHead(502, { 'Content-Type': 'application/json' });
              res.end(JSON.stringify({
                success: false,
                message: 'Python EOS API unreachable – verify port 9095 is active.',
                error: err.message
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
 * INSTITUTIONAL CERTIFICATION SEAL — WILSY OS VITE CONFIGURATION V2.5.0-PYTHON-EOS-API-ROUTING-BFF-ISOLATION
 * ═══════════════════════════════════════════════════════════════════════════════════
 * Status: MIGRATION STAGE 1 — GENERAL API ROUTING TO PYTHON EOS; LEGACY PDF ISOLATED
 * Compliance: POPIA §19, GDPR §32, SOC2 §CC7.2
 * Proxy Rules:
 *   /api/auth → http://localhost:9095 (Kennel auth router) – no rewrite
 *   /auth      → http://localhost:9095/api/auth (legacy alias rewritten to Python EOS)
 *   /api/billing/platform|client → http://localhost:9095/billing/platform|client
 *   /api/billing/plans|summary|analytics|credit-scores|forensic-status → http://localhost:9095/billing/*
 *   /api/kernel → http://localhost:9095/api/kernel
 *   /api/tenant-branding → http://localhost:9095/api/tenant-branding
 *   /api/legal-operations → http://localhost:9095/api/legal-operations
 *   /api/legal-acceptance → http://localhost:9095/api/legal-acceptance
 *   /api/tenants, /api/employees → http://localhost:9095
 *   /api/generate/pdf → http://localhost:4000 (temporary legacy PDF route only)
 *   /api       → http://localhost:9095 (Python EOS general API)
 * ═══════════════════════════════════════════════════════════════════════════════════
 */
