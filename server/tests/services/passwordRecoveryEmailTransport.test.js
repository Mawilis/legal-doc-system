/**
 * WILSY OS — PASSWORD RECOVERY EMAIL TRANSPORT DIRECT CERTIFICATE
 * VERSION: v1.0.0-R10E4-PASSWORD-RECOVERY-EMAIL-TRANSPORT-CERT
 * AUTHORITY: Wilsy OS Core Governance
 * EPITOME: Certifies strict SMTP recovery delivery without network access,
 *          fake-success paths, recipient logging, or recovery authority.
 * ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/server/tests/services/passwordRecoveryEmailTransport.test.js
 * COLLABORATION / OWNERSHIP: Test-only evidence for the dedicated recovery
 *                            email transport; Python recovery truth is read-only.
 * CERTIFICATION / UPDATE DATE: 2026-09-22
 * CHANGELOG: v1.0.0-R10E4-PASSWORD-RECOVERY-EMAIL-TRANSPORT-CERT — Adds deterministic SMTP configuration,
 *            payload, escaping, trusted-origin, failure, and secret-boundary tests.
 * COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2; ISO 27001.
 * SECURITY / PRIVACY POSTURE: Synthetic bearer values and injected transport only.
 * TENANT BOUNDARY: No tenant data is accepted by the production transport.
 * AUTHORITY BOUNDARY: Transport-only certificate; no credential/recovery grant.
 * FINANCIAL AUTHORITY BOUNDARY: None; Kennel EOS remains exclusive.
 */

import { expect } from 'chai';
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

import {
  PasswordRecoveryEmailTransport,
  PasswordRecoveryEmailTransportError,
} from '../../services/passwordRecoveryEmailTransport.js';

const TOKEN = 'synthetic-recovery-value-0123456789-ABCDE';
const EXPIRY = '2026-09-22T18:30:00.000Z';
const HERE = path.dirname(fileURLToPath(import.meta.url));
const SOURCE_PATH = path.resolve(HERE, '../../services/passwordRecoveryEmailTransport.js');

const ENV_KEYS = [
  'SMTP_HOST',
  'SMTP_PORT',
  'SMTP_SECURE',
  'SMTP_USER',
  'SMTP_PASS',
  'SMTP_FROM',
  'EMAIL_FROM',
  'WILSY_PUBLIC_APP_ORIGIN',
];

function clearEnvironment() {
  for (const key of ENV_KEYS) delete process.env[key];
}

function configureSmtp() {
  process.env.SMTP_HOST = 'smtp.synthetic.invalid';
  process.env.SMTP_PORT = '587';
  process.env.SMTP_SECURE = 'false';
  process.env.SMTP_USER = 'synthetic-user';
  process.env.SMTP_PASS = 'synthetic-password';
  process.env.EMAIL_FROM = 'security@wilsy.invalid';
}

describe('PasswordRecoveryEmailTransport direct certificate', () => {
  beforeEach(() => clearEnvironment());
  afterEach(() => clearEnvironment());

  it('fails closed when SMTP configuration is unavailable', async () => {
    const transport = new PasswordRecoveryEmailTransport({
      transporterFactory: () => ({ sendMail: async () => ({ messageId: 'unexpected' }) }),
    });
    try {
      await transport.deliver({
        recipientEmail: 'person@example.com',
        recoveryToken: TOKEN,
        expiresAt: EXPIRY,
      });
      throw new Error('expected transport failure');
    } catch (error) {
      expect(error).to.be.instanceOf(PasswordRecoveryEmailTransportError);
      expect(error.code).to.equal('RECOVERY_SMTP_UNAVAILABLE');
      expect(String(error)).not.to.contain(TOKEN);
      expect(String(error)).not.to.contain('person@example.com');
    }
  });

  it('sends one bounded SMTP payload with the recovery value only in message content', async () => {
    configureSmtp();
    process.env.WILSY_PUBLIC_APP_ORIGIN = 'https://app.wilsy.invalid';
    const factoryCalls = [];
    const mailCalls = [];
    const transport = new PasswordRecoveryEmailTransport({
      transporterFactory: (config) => {
        factoryCalls.push(config);
        return {
          sendMail: async (mail) => {
            mailCalls.push(mail);
            return { messageId: 'smtp-message-1' };
          },
        };
      },
    });

    const result = await transport.deliver({
      recipientEmail: ' Person@Example.COM ',
      recoveryToken: TOKEN,
      expiresAt: EXPIRY,
    });

    expect(result).to.deep.equal({ status: 'DELIVERED' });
    expect(factoryCalls).to.deep.equal([{
      host: 'smtp.synthetic.invalid',
      port: 587,
      secure: false,
      auth: { user: 'synthetic-user', pass: 'synthetic-password' },
    }]);
    expect(mailCalls).to.have.lengthOf(1);
    const mail = mailCalls[0];
    expect(mail.to).to.equal('person@example.com');
    expect(mail.from).to.equal('security@wilsy.invalid');
    expect(mail.subject).to.equal('Reset your WILSY OS password');
    expect(mail.text).to.contain(TOKEN);
    expect(mail.html).to.contain(TOKEN);
    expect(mail.text).to.contain('https://app.wilsy.invalid/reset-password');
    expect(mail.html).to.contain('https://app.wilsy.invalid/reset-password');
    expect(mail.headers['X-Wilsy-Message-Type']).to.equal('PASSWORD_RECOVERY');
  });

  it('escapes recovery bearer content before HTML rendering', async () => {
    configureSmtp();
    const bearer = 'abcdefghijklmnopqrstuvwxyz012345<unsafe>&"';
    const mailCalls = [];
    const transport = new PasswordRecoveryEmailTransport({
      transporterFactory: () => ({
        sendMail: async (mail) => {
          mailCalls.push(mail);
          return { messageId: 'smtp-message-2' };
        },
      }),
    });
    await transport.deliver({
      recipientEmail: 'person@example.com',
      recoveryToken: bearer,
      expiresAt: EXPIRY,
    });
    expect(mailCalls[0].html).not.to.contain('<unsafe>');
    expect(mailCalls[0].html).to.contain('&lt;unsafe&gt;');
    expect(mailCalls[0].text).to.contain(bearer);
  });

  it('rejects untrusted public-origin shapes before SMTP send', async () => {
    configureSmtp();
    process.env.WILSY_PUBLIC_APP_ORIGIN = 'https://user:pass@app.wilsy.invalid/path?secret=1';
    let sends = 0;
    const transport = new PasswordRecoveryEmailTransport({
      transporterFactory: () => ({
        sendMail: async () => { sends += 1; return { messageId: 'unexpected' }; },
      }),
    });
    try {
      await transport.deliver({
        recipientEmail: 'person@example.com',
        recoveryToken: TOKEN,
        expiresAt: EXPIRY,
      });
      throw new Error('expected origin failure');
    } catch (error) {
      expect(error.code).to.equal('RECOVERY_PUBLIC_ORIGIN_INVALID');
    }
    expect(sends).to.equal(0);
  });

  it('requires provider-confirmed message identity and maps provider errors code-only', async () => {
    configureSmtp();
    const unconfirmed = new PasswordRecoveryEmailTransport({
      transporterFactory: () => ({ sendMail: async () => ({}) }),
    });
    try {
      await unconfirmed.deliver({
        recipientEmail: 'person@example.com', recoveryToken: TOKEN, expiresAt: EXPIRY,
      });
      throw new Error('expected unconfirmed delivery failure');
    } catch (error) {
      expect(error).to.be.instanceOf(PasswordRecoveryEmailTransportError);
      expect(error.code).to.equal('RECOVERY_SMTP_DELIVERY_UNCONFIRMED');
    }

    const failed = new PasswordRecoveryEmailTransport({
      transporterFactory: () => ({ sendMail: async () => { throw new Error('provider leaked diagnostics'); } }),
    });
    try {
      await failed.deliver({
        recipientEmail: 'person@example.com', recoveryToken: TOKEN, expiresAt: EXPIRY,
      });
      throw new Error('expected SMTP failure');
    } catch (error) {
      expect(error.code).to.equal('RECOVERY_SMTP_DELIVERY_FAILED');
      expect(String(error)).not.to.contain('provider leaked diagnostics');
      expect(String(error)).not.to.contain(TOKEN);
    }
  });

  it('contains no logging, fake SendGrid, or development-success path', () => {
    const source = fs.readFileSync(SOURCE_PATH, 'utf8');
    expect(source).not.to.contain('console.log');
    expect(source).not.to.contain('logger.');
    expect(source.toLowerCase()).not.to.contain('sendgrid');
    expect(source).not.to.contain('devMode');
    expect(source).not.to.contain('IS_DEVELOPMENT');
  });
});

/**
 * ARTIFACT: server/tests/services/passwordRecoveryEmailTransport.test.js
 * VERSION: v1.0.0-R10E4-PASSWORD-RECOVERY-EMAIL-TRANSPORT-CERT
 * AUTHORITY BOUNDARY: deterministic SMTP recovery transport evidence only
 * TENANT POSTURE: no tenant data enters the transport contract
 * FAIL-CLOSED POSTURE: invalid configuration/input/unconfirmed provider delivery fails
 * FINANCIAL EXECUTION AUTHORITY: None; Kennel EOS remains exclusive
 * END OF WILSY OS SOVEREIGN ARTIFACT
 */
