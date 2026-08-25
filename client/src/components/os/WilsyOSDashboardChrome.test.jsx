import { describe, expect, it } from 'vitest';
import { resolveWilsyChromeIdentitySources } from './wilsyDashboardChromeConfig';

describe('resolveWilsyChromeIdentitySources', () => {
    it('prefers explicit tenant and operator props while carrying auth details into the top bar', () => {
        const result = resolveWilsyChromeIdentitySources({
            tenant: {
                displayName: 'Acme Legal',
                logo: '/logos/acme.png',
                status: 'ACTIVE',
                tenantId: 'ACME-001'
            },
            operator: {
                displayName: 'Jane Doe',
                roleLabel: 'General Counsel',
                email: 'jane@acme.com'
            },
            authUser: {
                firstName: 'Ada',
                lastName: 'Lovelace',
                role: 'Founder',
                email: 'ada@wilsy.os'
            },
            activeTenant: {
                name: 'Wilsy Tenant',
                tenantId: 'WILSY-42'
            }
        });

        expect(result.tenant.displayName).toBe('Acme Legal');
        expect(result.tenant.logo).toBe('/logos/acme.png');
        expect(result.tenant.tenantId).toBe('ACME-001');
        expect(result.operator.displayName).toBe('Jane Doe');
        expect(result.operator.roleLabel).toBe('General Counsel');
        expect(result.operator.email).toBe('jane@acme.com');
    });

    it('falls back to auth and tenant context values for branding and user details', () => {
        const result = resolveWilsyChromeIdentitySources({
            authUser: {
                firstName: 'Ada',
                lastName: 'Lovelace',
                role: 'Founder',
                email: 'ada@wilsy.os'
            },
            activeTenant: {
                name: 'Wilsy Tenant',
                tenantId: 'WILSY-42',
                logo: '/logos/wilsy.png',
                status: 'LIVE'
            }
        });

        expect(result.tenant.displayName).toBe('Wilsy Tenant');
        expect(result.tenant.tenantId).toBe('WILSY-42');
        expect(result.tenant.logo).toBe('/logos/wilsy.png');
        expect(result.operator.displayName).toBe('Ada Lovelace');
        expect(result.operator.roleLabel).toBe('Founder');
        expect(result.operator.email).toBe('ada@wilsy.os');
    });
});
