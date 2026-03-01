#!import crypto from 'crypto';

class DocumentEncryption {
  constructor() {
    this.algorithm = 'aes-256-gcm';
    this.key = crypto.scryptSync(
      process.env.DOC_ENCRYPTION_SECRET || 'wilsy_forensic_secret_key_2026',
      'salt',
      32
    );
  }

  async encryptDocument(buffer) {
    const iv = crypto.randomBytes(12);
    const cipher = crypto.createCipheriv(this.algorithm, this.key, iv);
    const encrypted = Buffer.concat([cipher.update(buffer), cipher.final()]);
    const tag = cipher.getAuthTag();

    // Bundle IV and Tag with the data for forensic recovery
    return Buffer.concat([iv, tag, encrypted]);
  }

  async decryptDocument(encryptedBuffer) {
    const iv = encryptedBuffer.slice(0, 12);
    const tag = encryptedBuffer.slice(12, 28);
    const text = encryptedBuffer.slice(28);

    const decipher = crypto.createDecipheriv(this.algorithm, this.key, iv);
    decipher.setAuthTag(tag);

    return Buffer.concat([decipher.update(text), decipher.final()]);
  }
}

export { DocumentEncryption };
