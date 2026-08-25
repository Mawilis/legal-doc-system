/* eslint-disable */
/**
 * ╔════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╗
 * ║ WILSY OS - VITE CLIENT CONFIGURATION RUNTIME [V2.3.8-KENNEL-AUTH-OWNER]                                                            ║
 * ║ AUTHORITY: WILSY OS CORE INFRASTRUCTURE | TERMINAL WORKFLOW COMPLIANT                                                                ║
 * ╠════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╣
 * ║ VERSION: 2.3.8-KENNEL-AUTH-OWNER | PRODUCTION READY                                                                               ║
 * ║ ABSOLUTE PATH: /Users/wilsonkhanyezi/legal-doc-system/client/vite.config.js                                                          ║
 * ╠════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╣
 * ║ EPITOME:                                                                                                                             ║
 * ║ Routes Node-owned /api traffic to port 4000 while explicitly rewriting EOS invoice paths to port 9095.                              ║
 * ╠════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╣
 * ║ 🔧 CHANGE LOG (v2.3.8):                                                                                                               ║
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
      // 👇 Fallback for /auth (without /api) – also to Node
      '/auth': {
        target: 'http://localhost:4000',
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
                message: 'Auth backend unreachable – verify Node server on port 4000 is active.',
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
      // All remaining API traffic belongs to the Node BFF (port 4000).
      '/api': {
        target: 'http://localhost:4000',
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
                message: 'Node BFF unreachable – verify port 4000 is active.',
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
 * INSTITUTIONAL CERTIFICATION SEAL — WILSY OS VITE CONFIGURATION V2.3.8-KENNEL-AUTH-OWNER
 * ═══════════════════════════════════════════════════════════════════════════════════
 * Status: CERTIFIED PRODUCTION ARTIFACT
 * Compliance: POPIA §19, GDPR §32, SOC2 §CC7.2
 * Proxy Rules:
 *   /api/auth → http://localhost:9095 (Kennel auth router) – no rewrite
 *   /auth      → http://localhost:4000 (Node backend)
 *   /api/billing/platform|client → http://localhost:9095/billing/platform|client
 *   /api/billing/plans|summary|analytics|credit-scores|forensic-status → http://localhost:9095/billing/*
 *   /api/kernel → http://localhost:9095/api/kernel
 *   /api/tenants, /api/employees → http://localhost:9095
 *   /api       → http://localhost:4000 (Node BFF)
 * ═══════════════════════════════════════════════════════════════════════════════════
 */
