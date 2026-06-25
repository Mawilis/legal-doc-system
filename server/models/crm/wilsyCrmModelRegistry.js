/* eslint-disable */
/**
 * ╔════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╗
 * ║ WILSY OS - CRM MODEL REGISTRY                                                                                          ║
 * ║ REGISTERS CRM MONGOOSE MODELS FOR LIVE SOURCE POSTURE                                                                  ║
 * ╚════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╝
 *
 * @fileoverview CRM model registry.
 */

import WilsyCrmLead from './wilsyCrmLead.js';
import WilsyCrmContact from './wilsyCrmContact.js';
import WilsyCrmAccount from './wilsyCrmAccount.js';
import WilsyCrmDeal from './wilsyCrmDeal.js';
import WilsyCrmTask from './wilsyCrmTask.js';
import WilsyCrmMeeting from './wilsyCrmMeeting.js';
import WilsyCrmConnector from './wilsyCrmConnector.js';

import { registerWilsyCrmIntelligenceModels } from './wilsyCrmIntelligenceModels.js';
/**
 * @function registerWilsyCrmModels
 * @description Registers and returns all Wilsy CRM Mongoose models.
 * @returns {Object} Registered CRM models.
 * @collaboration Ensures live source posture can discover CRM models before returning route-only status.
 */
function registerWilsyCrmModels() {
  const intelligenceModels = registerWilsyCrmIntelligenceModels();

  return {
    CRMLead: WilsyCrmLead,
    CRMContact: WilsyCrmContact,
    CRMAccount: WilsyCrmAccount,
    CRMDeal: WilsyCrmDeal,
    CRMTask: WilsyCrmTask,
    CRMMeeting: WilsyCrmMeeting,
    CRMConnector: WilsyCrmConnector,
    ...intelligenceModels,
  };
}

export { registerWilsyCrmModels };

export default registerWilsyCrmModels;
