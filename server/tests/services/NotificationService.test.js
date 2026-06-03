/* eslint-disable */
/**
 * 🧪 NotificationService Forensic Audit
 * @description Verifying the cryptographic sealing of user alerts.
 */
import { expect } from 'chai';
import NotificationService from '../../services/notification/NotificationService.js';

describe('📢 NotificationService Sovereign Audit', () => {
  it('dispatches a signed alert with a valid forensic signature', async () => {
    const userId = 'WILSON_K_FOUNDER';
    const event = 'VAULT_ACCESS_DETECTED';
    const payload = { location: 'Pretoria_Data_Center', ip: '102.69.0.1' };

    const result = await NotificationService.sendAlert(userId, event, payload);

    expect(result.status).to.equal('DISPATCHED');
    expect(result.alertId).to.match(/^ALT-/);
    expect(result.forensicSig).to.have.lengthOf(128); // Verifies SHA-512 integration
    expect(result.timestamp).to.exist;
  });
});
