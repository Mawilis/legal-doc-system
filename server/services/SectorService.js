/* eslint-disable */
/**
 * ####################################################################################################
 * # WILSY OS - SECTOR INJECTION SERVICE                                                            #
 * # ABSOLUTE PATH: /Users/wilsonkhanyezi/legal-doc-system/server/services/SectorService.js           #
 * ####################################################################################################
 * * 👥 COLLABORATION:
 * • Wilson Khanyezi (Lead Architect) - Universal Sector Mapping & Logic.
 * • Gemini (AI Engineering) - Automated DNA Injection.
 */

import { SectorRegistry } from '../models/SectorRegistry.js';
import logger from '../utils/logger.js';

class SectorService {
  /**
   * @desc Validates and retrieves the Industry DNA for a new tenant.
   */
  async getSectorProfile(sectorId) {
    const profile = await SectorRegistry.findOne({ sectorId, isActive: true });
    if (!profile) {
      logger.error(`[SECTOR-SERVICE] ❌ Industry Sector Not Registered: ${sectorId}`);
      throw new Error(`SECTOR_NOT_FOUND: ${sectorId} is not a valid Wilsy OS industry.`);
    }
    return profile;
  }

  /**
   * @desc Registers a new global business model.
   * This allows Wilson to "own" new sectors as they emerge in the global economy.
   */
  async registerGlobalSector(data) {
    try {
      const sector = await SectorRegistry.create(data);
      logger.info(`[SECTOR-SERVICE] ✅ Global Sector Registered: ${sector.name}`);
      return sector;
    } catch (err) {
      logger.error(`[SECTOR-SERVICE] ❌ Registration Failed: ${err.message}`);
      throw err;
    }
  }
}

export const sectorService = new SectorService();
export default sectorService;
