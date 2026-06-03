/* eslint-disable */
/**
 * ####################################################################################################
 * # WILSY OS - LEGAL SECURITY PROXY LAYER                                                            #
 * # ABSOLUTE PATH: /Users/wilsonkhanyezi/legal-doc-system/server/middleware/legal-security/security.js#
 * ####################################################################################################
 * # EPITOME: BIBLICAL WORTH BILLIONS | CONSOLIDATED GATEKEEPER                                       #
 * ####################################################################################################
 */

import security from '../security.js';

// Re-exporting for project-wide consistency and legacy import reconciliation
export const {
  authLimiter,
  apiLimiter,
  quantumFirewall,
  cors,
  helmet,
  all
} = security;

export default security;
