import { describe, expect, it } from 'vitest';
import { resolveRoleMode } from '../../src/components/industry/LegalDashboard.jsx';

describe('Legal tenant-owner commercial workspace boundary', () => {
  it('resolves tenant owners to a dedicated commercial-only presentation mode', () => {
    expect(resolveRoleMode('TENANT_OWNER')).toBe('TENANT_OWNER');
    expect(resolveRoleMode('OWNER')).toBe('TENANT_OWNER');
  });

  it('does not map non-Legal executive identities into a Legal practice role', () => {
    expect(resolveRoleMode('CEO')).toBe('UNRESOLVED');
    expect(resolveRoleMode('ENTERPRISE_ADMIN')).toBe('UNRESOLVED');
  });

  it('preserves the published Legal practice role mapping', () => {
    expect(resolveRoleMode('LEGAL_PARTNER')).toBe('LEGAL_PRACTICE');
    expect(resolveRoleMode('LEGAL_ATTORNEY')).toBe('LEGAL_PRACTICE');
  });
});
