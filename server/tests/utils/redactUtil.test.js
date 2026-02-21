/* eslint-disable */
import { expect } from 'chai';
import { redactPII } from '../../utils/redactUtil.js';

describe('Redact Utility - Forensic Grade', () => {
  it('should redact pii fields recursively', () => {
    const data = { user: { email: 'test@wilsy.os', phone: '0123456789' }, status: 'active' };
    const redacted = redactPII(data);
    expect(redacted.user.email).to.equal('[REDACTED]');
    expect(redacted.user.phone).to.equal('[REDACTED]');
    expect(redacted.status).to.equal('active');
  });
});
