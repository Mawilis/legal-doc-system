/* eslint-disable*/
/*╔══════════════════════════════════════════════════════════════════════════════╗
  ║ CRYPTO UTILITIES - INVESTOR-GRADE MODULE                                    ║
  ║ Cryptographic operations | Hash generation | Secure ID creation             ║
  ╚══════════════════════════════════════════════════════════════════════════════╝*/

import crypto from 'crypto';

/**
 * Generate a cryptographically secure random ID
 * @param {string} prefix - Optional prefix for the ID
 * @returns {string} Secure random ID
 */
export const generateId = (prefix = '') => {
  const randomBytes = crypto.randomBytes(16).toString('hex');
  const timestamp = Date.now().toString(36);
  const id = `${timestamp}-${randomBytes}`;
  return prefix ? `${prefix}-${id}` : id;
};

/**
 * Generate SHA256 hash of a string
 * @param {string} data - Data to hash
 * @returns {string} SHA256 hash
 */
export const generateHash = (data) => {
  return crypto
    .createHash('sha256')
    .update(typeof data === 'string' ? data : JSON.stringify(data))
    .digest('hex');
};

/**
 * Generate HMAC signature
 * @param {string} data - Data to sign
 * @param {string} key - Secret key
 * @returns {string} HMAC signature
 */
export const generateHmac = (data, key) => {
  return crypto
    .createHmac('sha256', key)
    .update(typeof data === 'string' ? data : JSON.stringify(data))
    .digest('hex');
};

/**
 * Generate random bytes as hex
 * @param {number} bytes - Number of bytes
 * @returns {string} Random hex string
 */
export const randomHex = (bytes = 32) => {
  return crypto.randomBytes(bytes).toString('hex');
};

/**
 * Generate random bytes as base64
 * @param {number} bytes - Number of bytes
 * @returns {string} Random base64 string
 */
export const randomBase64 = (bytes = 32) => {
  return crypto.randomBytes(bytes).toString('base64');
};

export default {
  generateId,
  generateHash,
  generateHmac,
  randomHex,
  randomBase64
};
