/**
 * Legacy PM2 entrypoint retired.
 *
 * Kennel EOS is the canonical application/API runtime. This intentionally
 * exports no PM2 applications so stale host-side PM2 commands cannot relaunch
 * the Node BFF. Frontend build, test and browser tooling remain supported.
 */
module.exports = { apps: [] };
