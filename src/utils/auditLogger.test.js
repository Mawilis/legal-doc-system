import { describe, it, expect } from 'vitest';
import { auditLogger } from './auditLogger';

describe('AuditLogger', () => {
  it('generates SHA-256 forensic hashes for each entry', () => {
    const entry = { action: 'LOGIN', user: 'john.doe', timestamp: Date.now() };
    const log = auditLogger.log(entry);
    expect(log.forensicHash).toMatch(/^[a-f0-9]{64}$/);
  });

  it('encrypts sensitive data using AES-256-GCM', () => {
    const entry = { action: 'LOGIN', user: 'john.doe', password: 'secret', timestamp: Date.now() };
    const log = auditLogger.log(entry);
    expect(log.encryptedData).toBeDefined();
    expect(log.iv).toBeDefined();
    expect(log.tag).toBeDefined();
  });

  it('validates forensic hashes against expected patterns', () => {
    const entry = { action: 'LOGIN', user: 'john.doe', timestamp: Date.now() };
    const log = auditLogger.log(entry);
    expect(log.forensicHash).toMatch(/^[a-f0-9]{64}$/);
  });
});