/**
 * ====================================================================
 *  WILSY OS – SOVEREIGN TEST UTILITY
 *  Version: v1.0.5-REAL-TENANT
 *  Authority: WILSY OS KENNEL EOS – TENANT ISOLATION & CRYPTOGRAPHIC VERIFICATION
 *  Epitome: Provides a wrapper with AuthProvider, TenantProvider, and Router
 *           for sovereign component tests.
 *  Collaboration: Wilson (architect), AI (implementation) – 2026-08-10
 *  Institutional: POPIA §19, GDPR §32, SOC2 §CC7.2 – ensures test
 *                 isolation and mimics production context.
 * ====================================================================
 */

import React from 'react';
import { render } from '@testing-library/react';
import { Router } from 'react-router-dom';
import { createMemoryHistory } from 'history';
import { AuthProvider } from './contexts/authContext';
import { TenantProvider } from './context/TenantContext';

/**
 * AllProviders – wraps children with required context providers and router.
 *
 * @param {Object} props
 * @param {React.ReactNode} props.children - Component to wrap.
 * @param {Object} [props.authValue] - Mock auth context value.
 * @param {Object} [props.tenantValue] - Mock tenant context value.
 * @param {Array} [props.initialEntries] - Initial route entries for history.
 * @returns {JSX.Element} Wrapped component.
 */
export function AllProviders({ children, authValue = {}, tenantValue = {}, initialEntries = ['/'] }) {
  const defaultAuth = {
    user: { id: 'test-user', role: 'FOUNDER', tenantId: 'TEST_TENANT' },
    isAuthenticated: true,
    login: () => {},
    logout: () => {},
    ...authValue,
  };

  // Provide a real tenant context with a mock tenant
  const defaultTenant = {
    tenant: { id: 'TEST_TENANT', name: 'Test Tenant', alias: 'test' },
    setTenant: () => {},
    clearTenant: () => {},
    ...tenantValue,
  };

  const history = createMemoryHistory({ initialEntries });

  return (
    <Router location={history.location} navigator={history}>
      <AuthProvider value={defaultAuth}>
        <TenantProvider value={defaultTenant}>
          {children}
        </TenantProvider>
      </AuthProvider>
    </Router>
  );
}

/**
 * customRender – renders a component with all providers and router.
 *
 * @param {React.ReactElement} ui - Component to render.
 * @param {Object} options - Render options (including wrapper overrides).
 * @returns {Object} RTL render result.
 */
export function customRender(ui, options = {}) {
  return render(ui, {
    wrapper: ({ children }) => <AllProviders>{children}</AllProviders>,
    ...options,
  });
}

export * from '@testing-library/react';
export { default as userEvent } from '@testing-library/user-event';
