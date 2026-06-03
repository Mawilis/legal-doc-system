/* eslint-disable */
/**
 * ╔════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╗
 * ║ WILSY OS - TENANT DNA INJECTOR (RUNTIME WHITE-LABELING ENGINE)                                                                         ║
 * ╠════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╣
 * ║ VERSION: 15.5.0-SINGULARITY-OMEGA | PRODUCTION READY                                                                                 ║
 * ║ EPITOME: BIBLICAL WORTH BILLIONS | NO CHILD'S PLACE | DYNAMIC BRANDING                                                                 ║
 * ╠════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╣
 * ║ COLLABORATION NOTES:                                                                                                                   ║
 * ║ 1. FUNCTIONALITY: Injects brand-specific variables into the document root based on the authenticated tenant context.                  ║
 * ║ 2. BRANDING SPEED: Allows new Fortune 500 firms to be onboarded and branded visually in < 10 minutes.                                  ║
 * ║ 3. DNA PRESERVATION: Ensures Wilsy OS structural integrity remains while visual identity shifts.                                       ║
 * ╚════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╝
 */

import { useEffect } from 'react';

/**
 * @hook useTenantDNA
 * @param {Object} tenantConfig - The configuration object retrieved from the Sovereign backend.
 */
export const useTenantDNA = (tenantConfig) => {
  useEffect(() => {
    // 🛡️ Guardian: Prevent execution if config is incomplete or system is in Genesis state.
    if (!tenantConfig || !tenantConfig.theme) return;

    const root = document.documentElement;
    const { primary, secondary, accent, logoUrl } = tenantConfig.theme;

    try {
      // 🧬 INJECT BRAND DNA: Mapping database values to CSS Custom Properties
      if (primary) root.style.setProperty('--tenant-primary', primary);
      if (secondary) root.style.setProperty('--tenant-secondary', secondary);
      if (accent) root.style.setProperty('--tenant-accent', accent);

      // 🏛️ GLOBAL TOPOGRAPHY: Setting the "Data-Tenant" attribute for specific theme selectors
      root.setAttribute('data-tenant', tenantConfig.slug || 'default');

      // 🏷️ METADATA BRANDING: Update document metadata for white-labeling
      document.title = `${tenantConfig.name} | Sovereign Operating System`;

      // 📊 LOGGING: Anchor branding event for forensic UI tracking
      console.log(`[DNA-INJECTOR] ✅ Sovereign Branding successfully applied for: ${tenantConfig.name}`);
    } catch (error) {
      console.error(`[DNA-INJECTOR] ❌ Branding Collision: ${error.message}`);
    }
  }, [tenantConfig]);
};

export default useTenantDNA;
