/* eslint-disable */
import path from 'path';
import { pathToFileURL } from 'url';

/**
 * 🏛️ WILSY OS - SOVEREIGN APP LOADER
 * [GOD MODE: ACTIVE | ESM PROTOCOL: ENFORCED]
 * ---------------------------------------------------------------------------
 * Bypasses legacy require() hooks by using absolute File URLs and
 * dynamic imports. Essential for graphs using Top-Level Await.
 * ---------------------------------------------------------------------------
 */
export const loadApp = async () => {
  try {
    const appPath = path.resolve(process.cwd(), 'app.js');
    const appUrl = pathToFileURL(appPath).href;

    // Add a cache-buster to ensure we load the fresh ESM state
    const module = await import(`${appUrl}?update=${Date.now()}`);

    const app = module.default || module.app;

    if (!app) {
      throw new Error('Sovereign App Export Missing: Ensure app.js exports default or app.');
    }

    return app;
  } catch (error) {
    console.error('❌ [SOVEREIGN_LOAD_FAILURE]:', error.message);
    throw error;
  }
};

export default loadApp;
