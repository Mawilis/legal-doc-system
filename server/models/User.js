/* eslint-disable */
/**
 * ╔════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╗
 * ║ WILSY OS - USER MODEL COMPATIBILITY BRIDGE [V1.0.0-PRODUCTION-ALIAS]                                                                 ║
 * ║ [IDENTITY MODEL ALIAS | LEGACY IMPORT STABILITY | NO DUPLICATE SCHEMA | SERVER BOOT PROTECTION]                                      ║
 * ╠════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╣
 * ║ VERSION: 1.0.0-PRODUCTION-ALIAS | PRODUCTION READY | USERMODEL CANONICAL EXPORT BRIDGE                                              ║
 * ║ ABSOLUTE PATH: /Users/wilsonkhanyezi/legal-doc-system/server/models/User.js                                                           ║
 * ╠════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╣
 * ║ COLLABORATION & SOVEREIGN SIGN-OFF:                                                                                                    ║
 * ║ • Wilson Khanyezi (Founder/CEO) - Identified that the canonical identity model is userModel.js and server imports were fracturing.   ║
 * ║ • AI Engineering (Codex) - ARCHITECTED: Added a zero-duplication bridge so legacy User.js imports resolve to the real userModel.js.  ║
 * ╚════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╝
 */

import User, { User as NamedUser, UserSchema } from './userModel.js';

/**
 * @function resolveCanonicalUserModel
 * @description Returns the canonical Wilsy OS user model exported by userModel.js.
 * @returns {import('mongoose').Model} Canonical User mongoose model.
 * @collaboration Keeps legacy imports operational without creating a second users schema or collection.
 */
export const resolveCanonicalUserModel = () => User;

export { NamedUser as User, UserSchema };
export default User;
