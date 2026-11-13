/* eslint-disable */
/**
 * TITLE: WILSY OS Sovereign Frontend Development Transport
 * VERSION: v2.6.0-CANONICAL-DEV-PORTS
 * AUTHORITY: Wilsy OS Core Governance; Python EOS owns business truth.
 * EPITOME: Preserve governed Vite proxy paths on the canonical development
 *          endpoints, with test-only isolation owned by the browser runner.
 * ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/client/vite.config.js
 * COLLABORATION / OWNERSHIP: Vite frontend transport; Python EOS owns
 *          authentication, IAM, work lifecycle and source commands.
 * CERTIFICATION / UPDATE DATE: 2026-11-10
 * CHANGELOG: v2.6.0-CANONICAL-DEV-PORTS removes unused per-process port
 *          overrides introduced for PR review. The authenticated browser
 *          runner keeps its isolated temporary Vite config and runtime-selected
 *          ports by replacing these literal loopback EOS proxy targets.
 * COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2.
 * SECURITY / PRIVACY POSTURE: Application proxies use the fixed loopback EOS target.
 * TENANT BOUNDARY: Transport cannot establish tenant entitlement.
 * AUTHORITY BOUNDARY: No browser or proxy-based authentication grants.
 * TRANSACTION / IDEMPOTENCY BOUNDARY: No persisted mutation.
 * FINANCIAL AUTHORITY BOUNDARY: Kennel EOS exclusively executes funds.
 * FAIL-CLOSED POSTURE: Normal Vite startup uses port 5173 and EOS port 9095.
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
      // Python EOS owns the canonical /api/auth router. Preserve its /api prefix.
      '/api/auth': {
        target: 'http://127.0.0.1:9095',
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
        target: 'http://127.0.0.1:9095',
        changeOrigin: true,
        secure: false,
        rewrite: (path) => path.replace(/^\/auth/, '/api/auth'),
      },
      // EOS billing lifecycle routes are mounted at /billing/* and /api/billing/*.
      // Keep these rules before the general /api EOS rule so compose/list reach EOS,
      // while EOS-owned application routes retain their canonical owner.
      '/api/billing/platform': {
        target: 'http://127.0.0.1:9095',
        changeOrigin: true,
        secure: false,
        rewrite: (path) => path.replace(/^\/api/, ''),
      },
      '/api/billing/client': {
        target: 'http://127.0.0.1:9095',
        changeOrigin: true,
        secure: false,
        rewrite: (path) => path.replace(/^\/api/, ''),
      },
      // EOS billing read models are mounted at /billing/*.
      // This explicit rule must remain ahead of /api so EOS routes retain their canonical ownership.
      '^/api/billing/(plans|summary|analytics|credit-scores|forensic-status)(?:/|$)': {
        target: 'http://127.0.0.1:9095',
        changeOrigin: true,
        secure: false,
        rewrite: (path) => path.replace(/^\/api/, ''),
      },
      // Kernel is an EOS service and is explicitly mounted at /api/kernel.
      '/api/kernel': {
        target: 'http://127.0.0.1:9095',
        changeOrigin: true,
        secure: false,
      },
      // Python EOS owns governed tenant-branding activation and workspace projection.
      // Preserve /api because the branding router is mounted under /api.
      '/api/tenant-branding': {
        target: 'http://127.0.0.1:9095',
        changeOrigin: true,
        secure: false,
      },
      // Python EOS owns the tenant-owner commercial Legal workspace.
      // Preserve /api; this is transport only, never browser-side business logic.
      '/api/crm/owner-workspace': {
        target: 'http://127.0.0.1:9095',
        changeOrigin: true,
        secure: false,
      },
      // Python EOS owns independent Operations and Intelligence work queues.
      '/api/tenant-modules': {
        target: 'http://127.0.0.1:9095',
        changeOrigin: true,
        secure: false,
      },
      // Python EOS owns authenticated Legal Operations read/command authority.
      // Preserve /api because the EOS router is mounted under /api.
      '/api/legal-operations': {
        target: 'http://127.0.0.1:9095',
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
        target: 'http://127.0.0.1:9095',
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
        target: 'http://127.0.0.1:9095',
        changeOrigin: true,
        secure: false,
      },
      '/api/employees': {
        target: 'http://127.0.0.1:9095',
        changeOrigin: true,
        secure: false,
      },
      // All remaining application API traffic is sent directly to Python EOS.
      '/api': {
        target: 'http://127.0.0.1:9095',
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
 * INSTITUTIONAL CERTIFICATION SEAL — WILSY OS VITE CONFIGURATION v2.6.0-CANONICAL-DEV-PORTS
 * ═══════════════════════════════════════════════════════════════════════════════════
 * Status: CERTIFIED DEVELOPMENT TRANSPORT ARTIFACT
 * Compliance: POPIA §19, GDPR §32, SOC2 §CC7.2
 * Default application endpoints: frontend 5173; Python EOS 9095.
 * Authenticated browser certification owns an isolated temporary config and
 * replaces the fixed loopback EOS target with its disposable EOS listener.
 * Proxy paths preserve their established API rewrites and ownership.
 */

// ARTIFACT: client/vite.config.js
// VERSION: v2.6.0-CANONICAL-DEV-PORTS
// AUTHORITY BOUNDARY: Vite proxy only; Python EOS business authority.
// TENANT POSTURE: Transport cannot establish tenant scope.
// FAIL-CLOSED POSTURE: Fixed canonical dev target; runner isolation is disposable.
// FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively.
// END OF WILSY OS SOVEREIGN ARTIFACT
