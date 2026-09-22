/**
 * WILSY OS — RECOVERY CONTACT VERIFICATION EMAIL TRANSPORT CERTIFICATE
 * VERSION: v1.0.0-R10E15-RECOVERY-CONTACT-VERIFICATION-EMAIL-TRANSPORT-CERT
 * AUTHORITY: Wilsy OS Core Governance
 * EPITOME: Deterministically certifies strict SMTP recovery-contact verification
 *          delivery without network access or authority transfer.
 * ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/server/tests/services/recoveryContactVerificationEmailTransport.test.js
 * CERTIFICATION / UPDATE DATE: 2026-09-22
 * CHANGELOG:
 *   v1.0.0-R10E15-RECOVERY-CONTACT-VERIFICATION-EMAIL-TRANSPORT-CERT — Certifies
 *   configuration fail-closed behavior, exact message content, escaping,
 *   provider confirmation, code-only failures, and absence of fake-success paths.
 * AUTHORITY BOUNDARY: Transport evidence only.
 * FINANCIAL AUTHORITY BOUNDARY: None; Kennel EOS remains exclusive.
 */

import { expect } from 'chai';
import {
  RecoveryContactVerificationEmailTransport,
  RecoveryContactVerificationEmailTransportError,
} from '../../services/recoveryContactVerificationEmailTransport.js';

const VALID_ENV = Object.freeze({
  SMTP_HOST: 'smtp.example.test',
  SMTP_PORT: '587',
  SMTP_SECURE: 'false',
  SMTP_USER: 'smtp-user',
  SMTP_PASS: 'smtp-pass',
  EMAIL_FROM: 'security@wilsy.example',
});
const TOKEN = 'synthetic-verification-token-0123456789-ABCDE';
const EXPIRY = new Date('2026-09-22T20:15:00.000Z');

function harness({ environment = VALID_ENV, result = { messageId: 'msg-1' }, failure = null } = {}) {
  const calls = [];
  const transporterFactory = (config) => {
    calls.push({ type: 'config', config });
    return {
      async sendMail(message) {
        calls.push({ type: 'mail', message });
        if (failure) throw failure;
        return result;
      },
    };
  };
  return {
    transport: new RecoveryContactVerificationEmailTransport({
      transporterFactory,
      environment,
    }),
    calls,
  };
}

describe('R10E15 recovery contact verification email transport', () => {
  it('delivers exact verification content through configured SMTP only', async () => {
    const { transport, calls } = harness();
    const receipt = await transport.deliver({
      recipientEmail: ' Person@Example.COM ',
      verificationToken: TOKEN,
      expiresAt: EXPIRY,
    });

    expect(receipt).to.deep.equal({ status: 'DELIVERED' });
    expect(calls).to.have.length(2);
    expect(calls[0].config).to.deep.equal({
      host: 'smtp.example.test',
      port: 587,
      secure: false,
      auth: { user: 'smtp-user', pass: 'smtp-pass' },
    });
    const message = calls[1].message;
    expect(message.from).to.equal('security@wilsy.example');
    expect(message.to).to.equal('person@example.com');
    expect(message.subject).to.equal('Verify your WILSY OS recovery email');
    expect(message.text).to.include(TOKEN);
    expect(message.text).to.include(EXPIRY.toISOString());
    expect(message.html).to.include(TOKEN);
    expect(message.headers['X-Wilsy-Message-Type']).to.equal('RECOVERY_CONTACT_VERIFICATION');
  });

  it('escapes verification bearer before HTML rendering', async () => {
    const { transport, calls } = harness();
    const token = 'synthetic-<verify>&"value"-0123456789-ABCDE';
    await transport.deliver({
      recipientEmail: 'person@example.com',
      verificationToken: token,
      expiresAt: EXPIRY,
    });
    const html = calls[1].message.html;
    expect(html).not.to.include('<verify>');
    expect(html).to.include('&lt;verify&gt;');
    expect(html).to.include('&amp;');
    expect(html).to.include('&quot;');
  });

  it('fails closed when SMTP configuration is incomplete', async () => {
    const { transport, calls } = harness({
      environment: { SMTP_HOST: 'smtp.example.test' },
    });
    try {
      await transport.deliver({
        recipientEmail: 'person@example.com',
        verificationToken: TOKEN,
        expiresAt: EXPIRY,
      });
      throw new Error('expected rejection');
    } catch (error) {
      expect(error).to.be.instanceOf(RecoveryContactVerificationEmailTransportError);
      expect(error.code).to.equal('RECOVERY_CONTACT_VERIFICATION_SMTP_UNAVAILABLE');
    }
    expect(calls).to.deep.equal([]);
  });

  it('rejects malformed recipient, token, and expiry before provider use', async () => {
    const cases = [
      { recipientEmail: 'invalid', verificationToken: TOKEN, expiresAt: EXPIRY },
      { recipientEmail: 'person@example.com', verificationToken: 'short', expiresAt: EXPIRY },
      { recipientEmail: 'person@example.com', verificationToken: TOKEN, expiresAt: 'not-a-date' },
    ];
    for (const options of cases) {
      const { transport, calls } = harness();
      let rejected = false;
      try {
        await transport.deliver(options);
      } catch (error) {
        rejected = true;
        expect(error).to.be.instanceOf(RecoveryContactVerificationEmailTransportError);
      }
      expect(rejected).to.equal(true);
      expect(calls).to.deep.equal([]);
    }
  });

  it('requires provider message confirmation and maps provider failure to code only', async () => {
    const unconfirmed = harness({ result: {} });
    try {
      await unconfirmed.transport.deliver({
        recipientEmail: 'person@example.com',
        verificationToken: TOKEN,
        expiresAt: EXPIRY,
      });
      throw new Error('expected rejection');
    } catch (error) {
      expect(error.code).to.equal('RECOVERY_CONTACT_VERIFICATION_SMTP_DELIVERY_UNCONFIRMED');
      expect(String(error)).not.to.include(TOKEN);
      expect(String(error)).not.to.include('person@example.com');
    }

    const failed = harness({ failure: new Error('provider secret diagnostic') });
    try {
      await failed.transport.deliver({
        recipientEmail: 'person@example.com',
        verificationToken: TOKEN,
        expiresAt: EXPIRY,
      });
      throw new Error('expected rejection');
    } catch (error) {
      expect(error.code).to.equal('RECOVERY_CONTACT_VERIFICATION_SMTP_DELIVERY_FAILED');
      expect(String(error)).not.to.include('provider secret diagnostic');
    }
  });

  it('contains no development fake-success transport', async () => {
    const source = RecoveryContactVerificationEmailTransport.prototype.deliver.toString();
    expect(source).not.to.include('DEV MODE');
    expect(source).not.to.include('console.log');
    expect(source).not.to.include('fake');
    expect(source).to.include('sendMail');
  });
});

/**
 * ARTIFACT: server/tests/services/recoveryContactVerificationEmailTransport.test.js
 * VERSION: v1.0.0-R10E15-RECOVERY-CONTACT-VERIFICATION-EMAIL-TRANSPORT-CERT
 * AUTHORITY BOUNDARY: deterministic SMTP transport evidence only
 * FAIL-CLOSED POSTURE: malformed config/input and unconfirmed provider delivery reject
 * FINANCIAL EXECUTION AUTHORITY: None; Kennel EOS remains exclusively financial
 * END OF WILSY OS SOVEREIGN ARTIFACT
 */
