import { describe, expect, it } from 'vitest';
import { isWilsyPlatformTenant } from '../../src/components/os/wilsyDashboardChromeConfig.js';

describe('WILSY platform tenant mark selection', () => {
  it('uses the canonical platform mark only for the exact WILSY tenant', () => {
    expect(isWilsyPlatformTenant('WILSYTENANT-4CD2FZ4O')).toBe(true);
    expect(isWilsyPlatformTenant('WILSYTENANT-OTHER')).toBe(false);
    expect(isWilsyPlatformTenant('wilsytenant-4cd2fz4o')).toBe(false);
    expect(isWilsyPlatformTenant(null)).toBe(false);
    expect(isWilsyPlatformTenant(undefined)).toBe(false);
  });
});
