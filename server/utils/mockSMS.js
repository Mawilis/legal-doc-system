/* eslint-disable */
/**
 * ╔═══════════════════════════════════════════════════════════════════════════╗
 * ║ WILSY OS - MOCK SMS SERVICE - DEVELOPMENT MODE                           ║
 * ║ For production, replace with actual Twilio/SMS provider                  ║
 * ╚═══════════════════════════════════════════════════════════════════════════╝
 */

import { createAuditLog } from '../middleware/auditMiddleware.js';

/**
 * Mock SMS sender for development
 * @param {string} to - Phone number (E.164 format)
 * @param {string} message - SMS message content
 * @returns {Promise<Object>} Delivery result
 */
export async function sendSMS(to, message) {
  const messageId = `MOCK_SMS_${Date.now()}_${Math.random().toString(36).substr(2, 8)}`;

  console.log(`📱 MOCK SMS [${to}]: ${message.substring(0, 50)}...`);

  // Simulate successful delivery
  const result = {
    success: true,
    messageId,
    to: to.substring(0, 4) + '****' + to.substring(to.length - 4),
    timestamp: new Date().toISOString(),
    status: 'delivered',
    mock: true
  };

  // Audit log
  await createAuditLog({
    action: 'MOCK_SMS_SENT',
    category: 'NOTIFICATION',
    userId: 'system',
    metadata: {
      to: result.to,
      messageLength: message.length,
      messageId
    },
    status: 'SUCCESS'
  });

  return result;
}

/**
 * Mock bulk SMS sender
 * @param {Array} recipients - Array of phone numbers
 * @param {string} message - SMS message content
 * @returns {Promise<Array>} Delivery results
 */
export async function sendBulkSMS(recipients, message) {
  const results = [];

  for (const to of recipients) {
    const result = await sendSMS(to, message);
    results.push(result);

    // Rate limit simulation
    await new Promise(resolve => setTimeout(resolve, 100));
  }

  return results;
}

export default {
  sendSMS,
  sendBulkSMS
};
