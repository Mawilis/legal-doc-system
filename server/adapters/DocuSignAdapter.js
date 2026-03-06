#!/* eslint-disable */
import crypto from 'crypto';

export const DocuSignAdapter = {
  async generateProof(payload, signer) {
    // Forensic proof: Deterministic HMAC over payload + signer + timestamp
    const normalized = JSON.stringify(payload);
    const ts = new Date().toISOString();
    const h = crypto
      .createHmac('sha256', process.env.PROVIDER_KEY || 'provider-test-key')
      .update(`${normalized}|${signer.id || signer.email}|${ts}`)
      .digest('hex');

    return {
      proof: {
        method: 'provider-hmac',
        value: h,
        ts,
        provider: 'docusign-sim',
      },
    };
  },
};

export default DocuSignAdapter;
