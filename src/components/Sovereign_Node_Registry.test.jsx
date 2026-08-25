import { render, screen } from '@testing-library/react';
import Sovereign_Node_Registry from './Sovereign_Node_Registry';
import { TenantProvider } from '../context/TenantContext';

describe('Sovereign_Node_Registry', () => {
  it('renders the component with the correct text', () => {
    render(
      <TenantProvider>
        <Sovereign_Node_Registry />
      </TenantProvider>
    );
    expect(screen.getByText(/SHA512/i)).toBeInTheDocument();
    expect(screen.getByPlaceholderText(/QUERY REGISTRY.../i)).toBeInTheDocument();
  });

  it('renders the component with the correct accessibility tags', () => {
    render(
      <TenantProvider>
        <Sovereign_Node_Registry />
      </TenantProvider>
    );
    expect(screen.getByRole('heading', { name: /Sovereign Node Registry/i })).toBeInTheDocument();
  });

  it('renders the component with the correct placeholder strings', () => {
    render(
      <TenantProvider>
        <Sovereign_Node_Registry />
      </TenantProvider>
    );
    expect(screen.getByPlaceholderText(/QUERY REGISTRY.../i)).toBeInTheDocument();
  });
});