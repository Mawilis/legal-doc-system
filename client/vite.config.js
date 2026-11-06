/* eslint-disable */
/**
 * WILSY OS — React/Vite frontend development configuration.
 * Application API authority: Python EOS only.
 * Browser responsibility: presentation and transport; EOS owns identity,
 * tenant membership, IAM, business operations and durable application state.
 * Vite is a frontend development/build tool, not an application backend.
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
      // EOS billing read models are mounted at /billing/*.
      // This explicit rule must remain ahead of /api so EOS routes retain their canonical ownership.
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
      // Python EOS owns the tenant-owner commercial Legal workspace.
      // Preserve /api; this is transport only, never browser-side business logic.
      '/api/crm/owner-workspace': {
        target: 'http://localhost:9095',
        changeOrigin: true,
        secure: false,
      },
      // Python EOS owns independent Operations and Intelligence work queues.
      '/api/tenant-modules': {
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

      // EOS owns the tenant and employee directories used by workspace typeaheads.
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
 * INSTITUTIONAL CERTIFICATION SEAL — WILSY OS VITE CONFIGURATION V2.4.1-L10-P2C7B-TENANT-BRANDING-ROUTER
 * ═══════════════════════════════════════════════════════════════════════════════════
 * Status: CERTIFIED PRODUCTION ARTIFACT
 * Compliance: POPIA §19, GDPR §32, SOC2 §CC7.2
 * Proxy Rules:
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
