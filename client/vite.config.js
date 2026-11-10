/* eslint-disable */
/**
 * TITLE: WILSY OS Sovereign Frontend Development Transport
 * VERSION: v2.5.0-LOOPBACK-ISOLATED-ATTENTION-ACCEPTANCE
 * AUTHORITY: Wilsy OS Core Governance; Python EOS owns business truth.
 * EPITOME: Preserve exact Vite proxy paths and permit isolated loopback
 *          side-by-side review without changing the existing application.
 * ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/client/vite.config.js
 * COLLABORATION / OWNERSHIP: Vite frontend transport; Python EOS owns
 *          authentication, IAM, work lifecycle and source commands.
 * CERTIFICATION / UPDATE DATE: 2026-11-10
 * CHANGELOG: v2.5.0-LOOPBACK-ISOLATED-ATTENTION-ACCEPTANCE adds
 *          validated optional WILSY_EOS_DEV_TARGET and WILSY_VITE_PORT
 *          without changing established default proxy routes or ports.
 * COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2.
 * SECURITY / PRIVACY POSTURE: Overrides restrict upstream to HTTP loopback.
 * TENANT BOUNDARY: Transport cannot establish tenant entitlement.
 * AUTHORITY BOUNDARY: No browser or proxy-based authentication grants.
 * TRANSACTION / IDEMPOTENCY BOUNDARY: No persisted mutation.
 * FINANCIAL AUTHORITY BOUNDARY: Kennel EOS exclusively executes funds.
 * FAIL-CLOSED POSTURE: Invalid custom host/port prevents dev startup.
 */
import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';
import path from 'path';

// Default ports remain unchanged. The PR409 review can safely use 9096/5174.
const configuredTarget = process.env.WILSY_EOS_DEV_TARGET || 'http://127.0.0.1:9095';
const targetUrl = new URL(configuredTarget);
if (targetUrl.protocol !== 'http:'
  || !['127.0.0.1', 'localhost'].includes(targetUrl.hostname)
  || !targetUrl.port || !Number.isInteger(Number(targetUrl.port))
  || Number(targetUrl.port) < 1 || Number(targetUrl.port) > 65535
  || targetUrl.pathname !== '/' || targetUrl.search || targetUrl.hash) {
  throw new Error('WILSY_EOS_DEV_TARGET_LOOPBACK_REQUIRED');
}
const configuredPort = process.env.WILSY_VITE_PORT || '5173';
if (!Number.isInteger(Number(configuredPort))
  || Number(configuredPort) < 1 || Number(configuredPort) > 65535) {
  throw new Error('WILSY_VITE_PORT_INVALID');
}
const eosProxyTarget = targetUrl.origin;

export default defineConfig({
  plugins: [react()],
  optimizeDeps: {
    include: ['js-sha3', 'axios', 'react', 'react-dom', 'react-router-dom']
  },
  server: {
    port: Number(configuredPort),
    host: true,
    strictPort: true,
    open: true,
    proxy: {
      // Python EOS owns the canonical /api/auth router. Preserve its /api prefix.
      '/api/auth': {
        target: eosProxyTarget,
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
                message: 'Auth backend unreachable – verify EOS API on port 9095 is active.',
                error: err.message
              }));
            }
          });
        }
      },
      // Compatibility path: send legacy /auth callers to the canonical EOS auth router.
      '/auth': {
        target: eosProxyTarget,
        changeOrigin: true,
        secure: false,
        rewrite: (path) => path.replace(/^\/auth/, '/api/auth'),
      },
      // EOS billing lifecycle routes are mounted at /billing/* and /api/billing/*.
      // Keep these rules before the general /api EOS rule so compose/list reach EOS,
      // while EOS-owned application routes retain their canonical owner.
      '/api/billing/platform': {
        target: eosProxyTarget,
        changeOrigin: true,
        secure: false,
        rewrite: (path) => path.replace(/^\/api/, ''),
      },
      '/api/billing/client': {
        target: eosProxyTarget,
        changeOrigin: true,
        secure: false,
        rewrite: (path) => path.replace(/^\/api/, ''),
      },
      // EOS billing read models are mounted at /billing/*.
      // This explicit rule must remain ahead of /api so EOS routes retain their canonical ownership.
      '^/api/billing/(plans|summary|analytics|credit-scores|forensic-status)(?:/|$)': {
        target: eosProxyTarget,
        changeOrigin: true,
        secure: false,
        rewrite: (path) => path.replace(/^\/api/, ''),
      },
      // Kernel is an EOS service and is explicitly mounted at /api/kernel.
      '/api/kernel': {
        target: eosProxyTarget,
        changeOrigin: true,
        secure: false,
      },
      // Python EOS owns governed tenant-branding activation and workspace projection.
      // Preserve /api because the branding router is mounted under /api.
      '/api/tenant-branding': {
        target: eosProxyTarget,
        changeOrigin: true,
        secure: false,
      },
      // Python EOS owns the tenant-owner commercial Legal workspace.
      // Preserve /api; this is transport only, never browser-side business logic.
      '/api/crm/owner-workspace': {
        target: eosProxyTarget,
        changeOrigin: true,
        secure: false,
      },
      // Python EOS owns independent Operations and Intelligence work queues.
      '/api/tenant-modules': {
        target: eosProxyTarget,
        changeOrigin: true,
        secure: false,
      },
      // Python EOS owns authenticated Legal Operations read/command authority.
      // Preserve /api because the EOS router is mounted under /api.
      '/api/legal-operations': {
        target: eosProxyTarget,
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
        target: eosProxyTarget,
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

      // EOS owns the tenant and employee directories used by workspace typeaheads.
      '/api/tenants': {
        target: eosProxyTarget,
        changeOrigin: true,
        secure: false,
      },
      '/api/employees': {
        target: eosProxyTarget,
        changeOrigin: true,
        secure: false,
      },
      // All remaining application API traffic is sent directly to Python EOS.
      '/api': {
        target: eosProxyTarget,
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
 * INSTITUTIONAL CERTIFICATION SEAL — WILSY OS VITE CONFIGURATION v2.5.0-LOOPBACK-ISOLATED-ATTENTION-ACCEPTANCE
 * ═══════════════════════════════════════════════════════════════════════════════════
 * Status: CERTIFIED PRODUCTION ARTIFACT
 * Compliance: POPIA §19, GDPR §32, SOC2 §CC7.2
 * Proxy Rules (default loopback 9095, optional validated dev override):
 *   /api/auth → http://localhost:9095 (Kennel auth router) – no rewrite
 *   /auth      → http://127.0.0.1:9095/api/auth (Python EOS)
 *   /api/billing/platform|client → http://localhost:9095/billing/platform|client
 *   /api/billing/plans|summary|analytics|credit-scores|forensic-status → http://localhost:9095/billing/*
 *   /api/kernel → http://localhost:9095/api/kernel
 *   /api/tenant-branding → http://localhost:9095/api/tenant-branding
 *   /api/legal-operations → http://localhost:9095/api/legal-operations
 *   /api/legal-acceptance → http://localhost:9095/api/legal-acceptance
 *   /api/tenants, /api/employees → http://localhost:9095
 *   /api       → http://127.0.0.1:9095 (Python EOS)
 * ═══════════════════════════════════════════════════════════════════════════════════
 */

// ARTIFACT: client/vite.config.js
// VERSION: v2.5.0-LOOPBACK-ISOLATED-ATTENTION-ACCEPTANCE
// AUTHORITY BOUNDARY: Vite proxy only; Python EOS business authority.
// TENANT POSTURE: Transport cannot establish tenant scope.
// FAIL-CLOSED POSTURE: Non-loopback targets and invalid ports rejected.
// FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively.
// END OF WILSY OS SOVEREIGN ARTIFACT
