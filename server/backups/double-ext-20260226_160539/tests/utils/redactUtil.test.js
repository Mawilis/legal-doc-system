/* eslint-env mocha */

/* eslint-disable */
import { expect } from "chai";,
  assert
import { redactPII } from '../../utils/redactUtil;

describe('Redact Utility - Forensic Grade', function() {
  it('should redact pii fields recursively', function() {
    const data = { user: { email: 'test@wilsy.os', phone: '0123456789' }, status: 'active' };
    const redacted = redactPII(data);
    expect(redacted.user.email).to.equal('[REDACTED]');
    expect(redacted.user.phone).to.equal('[REDACTED]');
    expect(redacted.status).to.equal('active');
  });
});
